#!/usr/bin/env python3
"""chain4_xor_pyramid.py -- XOR pyramid over the Chain4 35-block structure.

Chain4 body (c4[2:], 1149 B) = 35 x 32-byte blocks + 29 residual.  35 == the
user's  1+2+3+4+5+6+7+7  row-size layout (and half-splits 1..5+2 = 17,
1..5+3 = 18).  Prior runs only flat XOR-collapsed the 32-byte blocks across
arbitrary widths; here we build the *topological* XOR triangle:

  LAYOUT_A  rows [1,2,3,4,5,6,7] : 28-block triangle over a 7-block base, plus
            the extra 7-block row (b[28:35]) -> 35 blocks total.
  LAYOUT_B  rows [1,2,3,4,5,6,7,7]: doubled-base trapezoid (two 7-wide rows).
  HALF      the 35-block triangle split 17/18 (half-and-better-half): pyramid
            over the left 17 and right 18 blocks.

Every 32-byte apex/reduction is tested as the private key X (on-chain pubkey
TX=f4d1...), as password material (sha256 prefix cd3fea3d), and fed to both
funded gates via oracle.py / oracle_dualite.py (--stdin).

Read-only research; the oracle feed is the only side effect.
"""

from __future__ import annotations

import base64
import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

from Crypto.Cipher import AES

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "tools"))

CIDU = os.path.expanduser("~/briefcase/CosmicDuality.txt")


def sha256b(b):
    return hashlib.sha256(b).hexdigest()


def evp(pw, salt, digest="md5"):
    H = hashlib.md5 if digest == "md5" else hashlib.sha256
    d = b""
    prev = b""
    while len(d) < 48:
        prev = H(prev + pw + salt).digest()
        d += prev
    return d[:32], d[32:48]


def load_body():
    raw = base64.b64decode(Path(CIDU).read_bytes().strip())
    salt = raw[8:16]
    ct = raw[16:]
    XK = bytes.fromhex("a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735")
    k, iv = evp(XK, salt, "md5")
    cc = AES.new(k, AES.MODE_CBC, iv).decrypt(ct)
    cc = cc[: -cc[-1]]
    mask = bytes.fromhex("b657264f2f6e6921")
    mystery = bytes(a ^ b for a, b in zip(cc[158:158 + 1168], (mask * 146)[:1168]))
    PW = bytes.fromhex("38d4f4c90cb45fdfc8cff50d0ed1c5740a25de4b8e946d0a5ae2667a23a259cc")
    kk, ivv = evp(PW, mystery[8:16], "md5")
    c4 = AES.new(kk, AES.MODE_CBC, ivv).decrypt(mystery[16:])
    c4 = c4[: -c4[-1]]
    return c4[2:]


def pyr_apex(vals):
    row = vals[:]
    while len(row) > 1:
        row = [xor_bytes(row[i], row[i + 1]) for i in range(len(row) - 1)]
    return row[0]


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def half_rows_and_apex(blocks, n):
    """Triangle over the rightmost/base n blocks -> apex (half & better half)."""
    from math import comb
    out = bytearray(32)
    for i, b in enumerate(blocks[-n:]):
        if comb(n - 1, i) & 1:
            out = bytearray(xor_bytes(out, b))
    return bytes(out)


def main() -> int:
    body = load_body()
    print(f"chain4 body len={len(body)}; 35x32 blocks + {len(body) - 35 * 32} "
          f"residual", flush=True)
    blocks = [body[i * 32:(i + 1) * 32] for i in range(35)]
    lines = []          # (label, candidate string)

    # LAYOUT_A (28-cell triangle over a 7-block base = blocks[21:28]) plus the
    # extra 7-cell row blocks[28:35].
    apex_a = pyr_apex(blocks[21:28])
    acc = bytes(32)
    for b in blocks[28:35]:
        acc = xor_bytes(acc, b)
    lines.append(("LAYOUT_A apex (7-block triangle)", apex_a))
    lines.append(("extra 7-row xor-all", acc))

    # LAYOUT_B: doubled-base trapezoid rows [1..6,7,7]; 21 top cells = the
    # pairwise-XOR tower, then apex over the whole 35 via pascal-parity subset.
    apex_b = pyr_apex(blocks[14:35])
    lines.append(("LAYOUT_B apex (21-cell tower)", apex_b))

    # half-and-better-half 17/18
    apex17 = half_rows_and_apex(blocks, 17)
    apex18 = half_rows_and_apex(blocks, 18)
    lines.append(("HALF-17 apex", apex17))
    lines.append(("HALF-18 apex", apex18))
    lines.append(("HALF-17 xor 18", xor_bytes(apex17, apex18)))

    # net triangle apex over ALL 35 base cells (pascal parity subset)
    apex_all = half_rows_and_apex(blocks, 35)
    lines.append(("apex over 35-base (pascal subset)", apex_all))

    # per-base-row xor reductions
    for lab, r in (("base row0 xor-all", blocks[0:7]),
                   ("base row1 xor-all", blocks[7:14])):
        acc = bytes(32)
        for b in r:
            acc = xor_bytes(acc, b)
        lines.append((lab, acc))

    print(f"{len(lines)} raw candidates; materializing strings...", flush=True)
    feed = []
    for lab, raw in lines:
        if raw is None:
            continue
        hexs = raw.hex()
        latin = raw.decode("latin-1")
        sha = sha256b(raw)
        pk_ok = ""
        try:
            from coincurve import PublicKey
            pk = PublicKey.from_valid_secret(raw).format(compressed=False)
            if pk[1:33].hex() == "f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464":
                pk_ok = "PUBKEY-MATCH"
        except Exception:
            pass
        print(f"  {lab:44s} sha256={sha[:8]}{' CD!' if sha.startswith('cd3fea3d') else ''} "
              f"{pk_ok}", flush=True)
        feed.append((lab, hexs))
        feed.append((lab, latin))
        feed.append((lab, sha))

    # certified oracle path: --stdin, one candidate per line, exact match
    N = len(feed)
    print(f"candidate strings: {N} (x UPPER/lower via oracle case variants "
          f"in subprocess) -> feeding both gate addresses", flush=True)
    for script, gate in (("oracle.py", "1GSMG1JC9"),
                         ("oracle_dualite.py", "17ucy1K9")):
        txt = "\n".join(s for _, s in feed) + "\n"
        t0 = time.time()
        p = subprocess.run([sys.executable, "tools/" + script, "--stdin"],
                           input=txt, capture_output=True, text=True)
        rc = p.returncode
        print(f"  {script} ({gate}): exit={rc} ({time.time() - t0:.0f}s "
              f"{'MATCH' if rc == 0 else 'no match'})", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())