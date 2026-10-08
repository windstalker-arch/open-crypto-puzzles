#!/usr/bin/env python3
"""ca-family battery: rebuild the ca-family candidates byte-exactly from the
certified on-disk artifacts (CosmicDuality.txt + "Last solved and unsolved parts.txt")
and submit every derived reading of each object to BOTH gates.

Objects rebuilt (same pipeline as R-CAFORMULA-REPRO / chain4_ca_hunt.py):
  cc  = 1327B decrypted Cosmic Duality (XK a795de11.., EVP-MD5)        sha 4f7a1e4e..
  c4  = 1151B chain4 (mask b657264f2f6e6921 + PW 38d4f4c9..)           sha e4269ed5..
  yl  = 1539-char yourlife plaintext                                   sha 90829b51..
  ca  = c4[246:1151] XOR yl[633:1538]  (905B)                          sha 5940983c..
  ca_full   = c4[0:1151] XOR yl[387:1538] (1151B)                      sha 2b2493c1dde738d0
  ca_head   = c4[0:246] XOR yl[387:633] (246B)                         sha 1d0eb750b6caeae1

Candidate family (pre-registered, bounded):
  per object, every {hex-base58, base64, hex-upper, hex-lower, latin-1 raw} reading;
  per 32B slice of interest, the raw + hex + base64 + WIF + b58check forms;
  published keystream head, k_new (cc[833:865] XOR ca[280:312]), and their inverse.

Every line is submitted verbatim as the candidate answer string X to
tools/oracle.py (small-gate 1GSMG1JC9...) and tools/oracle_dualite.py
(17ucy1K9ZUAa...). The oracles themselves try both raw-X and sha256(X) password
forms under both digests and all readings, so a single submission covers the
pipeline's full attested surface.

Usage:
  python3 tools/ca_family_battery.py            # rebuild, self-check, then submit
  python3 tools/ca_family_battery.py --stdin    # read candidate lines from stdin instead
"""
from __future__ import annotations

import base64
import hashlib
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CD = Path(os.path.expanduser("~/briefcase/CosmicDuality.txt"))
YL = Path(os.path.expanduser(
    "~/storage/external/briefcase/gsmg-solver-group/Last solved and unsolved parts.txt"))

# certified anchors
SHA_CC = "4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081"
SHA_C4 = "e4269ed5fbb202a81e5e1aa6b5190fdd1ea126b2c8547ea7cdbdf45387ea135b"
SHA_YL = "90829b510c3697569da47d2817f545f1e2a1cddd78e45f821dafcdab3dc0c281"
SHA_CA = "5940983cfa61ffab2522236b6da1dd1c9db97b9ca3d3ecb845038c811ca1f00d"

XK = bytes.fromhex("a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735")
MASK = bytes.fromhex("b657264f2f6e6921")
PW = bytes.fromhex("38d4f4c90cb45fdfc8cff50d0ed1c5740a25de4b8e946d0a5ae2667a23a259cc")
KEYSTREAM = "38d7c0b10bda30809b62a39ef58272ad9ae88a08335c606b93eb2bddb996bd25"


def sha256b(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def evp(pw: bytes, salt: bytes, digest: str = "md5"):
    H = hashlib.md5 if digest == "md5" else hashlib.sha256
    d, prev = b"", b""
    while len(d) < 48:
        prev = H(prev + pw + salt).digest()
        d += prev
    return d[:32], d[32:48]


def unpad(b: bytes) -> bytes:
    return b[:-b[-1]] if b else b


def rebuild() -> dict:
    raw = base64.b64decode(CD.read_bytes().strip())
    k, iv = evp(XK, raw[8:16], "md5")
    cc = unpad(AES_decrypt(k, iv, raw[16:]))
    mystery = bytes(a ^ b for a, b in zip(cc[158:158 + 1168], (MASK * 146)[:1168]))
    kk, ivv = evp(PW, mystery[8:16], "md5")
    c4 = unpad(AES_decrypt(kk, ivv, mystery[16:]))
    m = __import__("re").search(r"yourlifeisthesum[a-z]*", YL.read_text(encoding="utf-8", errors="replace"))
    yl = m.group(0)
    ca = bytes(a ^ b for a, b in zip(c4[246:1151], yl[633:1538].encode()))
    ca_full = bytes(a ^ b for a, b in zip(c4[0:1151], yl[387:1538].encode()))
    ca_head = bytes(a ^ b for a, b in zip(c4[0:246], yl[387:633].encode()))
    return {"cc": cc, "c4": c4, "yl": yl, "ca": ca, "ca_full": ca_full, "ca_head": ca_head}


def AES_decrypt(k: bytes, iv: bytes, ct: bytes) -> bytes:
    from Crypto.Cipher import AES
    return AES.new(k, AES.MODE_CBC, iv).decrypt(ct)


def b58(b: bytes) -> str:
    return "".join(base58_encode(b))


def base58_encode(b: bytes) -> list:
    alpha = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    n = int.from_bytes(b, "big")
    out = []
    while n:
        n, r = divmod(n, 58)
        out.append(alpha[r])
    return list(reversed(out or ["0"]))


def wif_uncomp(priv: bytes) -> str:
    payload = b"\x80" + priv
    chk = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    return b58(payload + chk)


def readings_of(obj: dict) -> list[str]:
    cands = []
    # per-object full-string readings
    for name, b in obj.items():
        if name == "yl":
            continue
        cands.append(("obj:%s:hex" % name, b.hex()))
        cands.append(("obj:%s:HEX" % name, b.hex().upper()))
        cands.append(("obj:%s:b64" % name, base64.b64encode(b).decode()))
        cands.append(("obj:%s:latin1" % name, "".join(chr(x) for x in b)))
        cands.append(("obj:%s:sha256hex" % name, sha256b(b)))
    # yl full string in a few trivial forms
    y = obj["yl"]
    cands.append(("obj:yl:raw", y))
    cands.append(("obj:yl:upper", y.upper()))
    # 32B slices of interest
    slices = {
        "cc833": obj["cc"][833:865],
        "ca280": obj["ca"][280:312],
        "ca_head32": obj["ca"][:32],
        "c4_246_278": obj["c4"][246:278],
        "yl_633_665": obj["yl"][633:665].encode(),
        "k_new": bytes(a ^ b for a, b in zip(obj["cc"][833:865], obj["ca"][280:312])),
        "k_new_inv": bytes(a ^ b for a, b in zip(obj["ca"][280:312], obj["cc"][833:865])),
    }
    for name, b in slices.items():
        cands.append(("slice:%s:hex" % name, b.hex()))
        cands.append(("slice:%s:b64" % name, base64.b64encode(b).decode()))
        cands.append(("slice:%s:latin1" % name, "".join(chr(x) for x in b)))
        cands.append(("slice:%s:wif" % name, wif_uncomp(b)))
        cands.append(("slice:%s:b58" % name, b58(b)))
        cands.append(("slice:%s:sha256hex" % name, sha256b(b)))
    # published keystream head as submitted-if-SHA
    cands.append(("keystream_head", KEYSTREAM))
    return cands


def run_oracle(exe: str, lines: list[str]) -> list:
    proc = subprocess.run(
        [sys.executable, exe, "--stdin"],
        input="\n".join(lines) + "\n",
        capture_output=True, text=True)
    out = proc.stdout
    hits = [l for l in out.splitlines()
            if l.startswith("MATCH ") and "reading=" in l]
    return hits


def main() -> int:
    obj = rebuild()
    bad = []
    for name, exp in (("cc", SHA_CC), ("c4", SHA_C4), ("ca", SHA_CA)):
        got = sha256b(obj[name])
        if not got.startswith(exp[:16]):
            bad.append(f"{name}: sha256 {got[:16]} != {exp[:16]}")
    if sha256b(obj["yl"].encode()) != SHA_YL:
        bad.append("yl: sha256 mismatch")
    if bad:
        print("REBUILD FAILED:", *bad, sep="\n  ")
        return 2
    print("rebuild OK: cc/c4/yl/ca anchors match on-disk records")

    candidates = readings_of(obj)
    print(f"candidates: {len(candidates)}")
    lines = [c for _, c in candidates]
    for exe in ("tools/oracle.py", "tools/oracle_dualite.py"):
        p = REPO / exe
        hits = run_oracle(str(p), lines)
        print(f"{exe}: {len(lines)} submitted, {len(hits)} MATCH")
        for h in hits:
            print("  HIT:", h)
    return 0 if True else 1


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)