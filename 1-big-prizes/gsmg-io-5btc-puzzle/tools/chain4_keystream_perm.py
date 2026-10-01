#!/usr/bin/env python3
"""chain4_keystream_perm.py -- reproduce the external claim that "all 40,320
public-half triangle orders as a keystream" was swept, oracle-certified.

External claim (reproduced faithfully under a documented construction):
"Chain4 / XOR-triangle conditional branch - every ordering falsified as a
literal or masked triangle; every one-byte AES-key completion; all 40,320
public-half triangle orders as a keystream."

40,320 == 8! .  We take the 8-block public window = the LAST 8 of the 35
x 32-byte Chain4 body blocks (the "public half tail" that any solver can
assemble from the published chain, blocks[27]..blocks[34]), and for every
permutation p of [0..7] form an ORDER-SENSITIVE keystream assembly:
   ks = XOR_i  rotate_left( blocks[27 + p[i]], i )        (i = 0..7)
i.e. each public half-block is rotated by its permuted rank before the
column-wise XOR keystream is summed.  A plain XOR triangle is order-
invariant, so the rotation makes this genuinely exercise all 40,320 orders.

Per-order candidates (all legs):
   ks.hex() , ks.hex() reversed (WAR=RAW), ks latin-1 raw,
   sha256(ks).hex(),
   (ks XOR cc[0:32]).hex, (ks XOR B1_79[0:32]).hex,
   (ks XOR matrix 24-bit color-word padded).hex,
and the same set re-run over the REVERSED block window (blocks[34]..blocks[27])
for the mirror leg.  Every output is fed to BOTH gate addresses via
oracle.py / oracle_dualite.py --stdin (raw-X + sha256-X hex legs).

Certified path: oracle.py --selftest / oracle_dualite.py --selftest were PASS
immediately before this battery.
"""

from __future__ import annotations

import base64
import hashlib
import itertools
import os
import subprocess
import sys
import time
from pathlib import Path

from Crypto.Cipher import AES

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIDU = os.path.expanduser("~/briefcase/CosmicDuality.txt")
DATA = Path(os.path.join(BASE, "data"))


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


def rotl(b, n):
    return b[n:] + b[:n]


def load_chain():
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
    return cc, c4[2:]


def main() -> int:
    cc, body = load_chain()
    blocks = [body[i * 32:(i + 1) * 32] for i in range(35)]
    print(f"chain4 body {len(body)}B, 35 blocks + {len(body)-35*32} residual "
          f"(residual: {sha256b(body[35*32:])[:8]})", flush=True)
    print(f"cc {len(cc)}B, sha256[:8] {sha256b(cc)[:8]}", flush=True)

    b1 = (DATA / "B1_79B.bin").read_bytes()
    print(f"B1_79 {len(b1)}B, [0:32] head {b1[:8].hex()}", flush=True)

    color24 = bytes.fromhex("08c26d").ljust(32, b"\x00")
    targets = {"cc[0:32]": cc[:32], "B1[0:32]": b1[:32], "color24padded": color24}

    lines = []
    due = set()

    def add(label, ks):
        if ks is None or len(ks) != 32:
            return
        for leg, s in (
            ("hex", ks.hex()),
            ("hexrev", ks[::-1].hex()),
            ("latin", ks.decode("latin-1")),
            ("sha", sha256b(ks)),
            ("shaREV", sha256b(ks[::-1])),
        ):
            if s in due:
                continue
            due.add(s)
            lines.append((label, s))
        for tname, t in targets.items():
            x = bytes(a ^ b for a, b in zip(ks, t))
            for leg, s in (("xor_" + tname, x.hex()),):
                if s not in due:
                    due.add(s)
                    lines.append((label + "/" + leg, s))

    windows = {"tail(b27..34)": blocks[27:35], "head(b0..7)": blocks[0:8],
               "mid(b14..21)": blocks[14:22], "mirrorrev-tail": blocks[34:26:-1]}
    t0 = time.time()
    total = 0
    for wname, win in windows.items():
        for p in itertools.permutations(range(8)):
            ks = bytes(32)
            for i, bi in enumerate(p):
                ks = bytes(a ^ b for a, b in zip(ks, rotl(win[bi], i)))
            total += 1
            add(wname + "/" + "".join(map(str, p)), ks)
    print(f"permutations assembled: {total} ({time.time()-t0:.0f}s), "
          f"unique candidate strings: {len(lines)}", flush=True)

    save = os.environ.get("KSPERM_SAVE", "")
    if save:
        Path(save).write_text("\n".join(s for _, s in lines) + "\n")
        print(f"saved {len(lines)} candidate strings -> {save}", flush=True)

    only = os.environ.get("KSPERM_ONLY", "")
    legs = [("oracle.py", "1GSMG1JC9"), ("oracle_dualite.py", "17ucy1K9")]
    if only:
        legs = [l for l in legs if l[0] == only]
    t0 = time.time()
    for script, gate in legs:
        txt = "\n".join(s for _, s in lines) + "\n"
        p = subprocess.run([sys.executable, "tools/" + script, "--stdin"],
                           input=txt, capture_output=True, text=True)
        rc = p.returncode
        print(f"  {script} ({gate}): exit={rc} ({time.time()-t0:.0f}s "
              f"{'MATCH' if rc == 0 else 'no match'})", flush=True)
        t0 = time.time()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())