#!/usr/bin/env python3
"""Off-chain premise battery: stress-test "the gate answer is the small-blob
AES password". Candidate privkeys derived WITHOUT the X-decrypts-blob step,
from EVP AES key/IV objects, K/E-field x-coordinate reads, and raw certified
transcripts. Exact checks: k*G == gate-1 X, or P2PKH (comp+uncomp) == either gate.
"""
from __future__ import annotations

import base64
import hashlib
import itertools
import sys
import time
from pathlib import Path

import coincurve

FOLDER = Path(__file__).resolve().parent.parent
DATA = FOLDER / "data"
B1 = (DATA / "B1_79.bin").read_bytes()
B2 = (DATA / "B2_79.bin").read_bytes()

X = 0xF4D1BBD91E65E2A019566A17574E97DAE908B784B388891848007E4F55D5A464
Y_EXPECT = 0x9C73D25FC5ED8FD7227CAB0BE4E576C0C6404DB5AA546286563E4BE12BF33559
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Pp = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

GATES = {"g1": "a9553269572a317e39f0f518cb87c1a0ee1dbae4",
         "g2": "4bc468447fe1b048ad030a2f9a125478eabc4ed6"}

BLOB_B64 = ("U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z"
            "QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ")
BLOB = base64.b64decode(BLOB_B64)
SALT_SMALL = BLOB[8:16]
PW_CERT = "matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist"

PHASE2_BLOB = base64.b64decode(
    "U2FsdGVkX18GKGYS1D7X7VjxWz6uUyPFszr8dVvtOIrJqioWHgT69JJnzJGDVOvF"
    "QYWh5BEZxFPXmMq1cbyy3dVVDgLhF050xlDy2J5grtKw9jUOO4oFNRgoD+1dlukX"
    "pd8ccg++kkXgE9mGBP6lQbukDiSjY4mnR2Mv6ydIncrRqacQNVEmEgM4fGTi1ANz"
    "nHsGn7mP+P3UyrJCRbuFmpZJc4CNdPj6YuxwR4HkHkqcfxh0L5CaEu4VbY70+fmk"
    "qgZQyMJqiUlaV9KC4UPuRVj0r7MYbVRazkhsjeIcogmdJGEeBwD47lEB7X9PNKWm"
    "ojTvRZg6R+sZzRZE26VLaF+s9cpTo4Y8PZUxKvQ86HXC8QIavUgDfw7HxIxkTatv"
    "CW2yq3ZOXl5naR6oSNxdX9alyhTzB+/2623oGdlWev5Oo8xHJqUi7QjVP+mNC8BA"
    "+Cg0DJwcOFGO5K7g8Rm06+sLogwntdIgTo70X3FegAtipHboeUNKefiAguvkDoIf"
    "8iMPc+83PygvlZPDNQCOKugwDEUimhHwQrMsmalRNoFEQEb+ZIC+na15cPoRAlOD"
    "NJfXIJ96ihAy9wWis39mQW6JFqZmUags4xoP3lJ35bCrXsNOPFZ4WH+f4YC/Ov8C"
    "QW5bjtxno8GG4b/wBWevhcRVMK6KmRJj8NBCssnrlz0sQ70rMNkiN2wiSPcwX3Ad"
    "JgLs8vQAUM59x9fkKFFzD4+Sc1sJztUTB7CMGGfpZOA8W33VZnEdmGcoaHlDsR8G"
    "vAkZ+jg+QJs9ZNHqWE1+1zgm/6NsWWgWH8OI2PPCfXHxDbfDk8uD/Zibr/yjSKvu"
    "Sb8OecflOT2hw37WL49uADgeWgnp2bzkfGIq7EYS7OImjZZwY5h4sfcPfhvQ9kOV")
SALT_P2 = PHASE2_BLOB[8:16]
PW_P2 = hashlib.sha256(b"causality").hexdigest()

K_C1, K_C2, E_C = B1[0:32], B1[32:64], B1[64:79]
K_S1, K_S2, E_S = B2[0:32], B2[32:64], B2[64:79]


def sha256b(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def evp_bytes_to_key(password: bytes, salt: bytes, key_len: int, iv_len: int,
                     digest: str):
    H = hashlib.sha256 if digest == "sha256" else hashlib.md5
    derived, prev = b"", b""
    while len(derived) < key_len + iv_len:
        prev = H(prev + password + salt).digest()
        derived += prev
    return derived[:key_len], derived[key_len:key_len + iv_len]


def i2b(i: int) -> bytes:
    return (i & ((1 << 256) - 1)).to_bytes(32, "big")


def b2i(b: bytes) -> int:
    return int.from_bytes(b, "big")


def h160(pub: bytes) -> str:
    return hashlib.new("ripemd160", sha256b(pub)).hexdigest()


def point_ok(x: int, y: int) -> str | None:
    if x == X and y == Y_EXPECT:
        return "gate1-X"
    up = b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")
    cp = (b"\x03" if y & 1 else b"\x02") + x.to_bytes(32, "big")
    for name, h in GATES.items():
        if h160(up) == h or h160(cp) == h:
            return f"{name}-h160"
    return None


def scan(name: str, kb: bytes | int, hits: list[str]) -> int:
    k = kb if isinstance(kb, int) else b2i(kb)
    r = 0
    if 0 < k < N:
        try:
            x, y = coincurve.PublicKey.from_valid_secret(i2b(k)).point()
            if point_ok(x, y):
                hits.append(f"{name}@scalar")
                r = 1
        except Exception:
            pass
    if isinstance(kb, bytes) and len(kb) == 32:
        z = b2i(kb)
        if 0 < z < Pp:
            for px in (0x02, 0x03):
                try:
                    p = coincurve.PublicKey(bytes([px]) + kb)
                except Exception:
                    continue
                x, y = p.point()
                if point_ok(x, y):
                    hits.append(f"{name}@xcoord")
                    r = 1
    return r


def main() -> int:
    t0 = time.time()
    hits: list[str] = []
    tested = 0

    items: list[tuple[str, bytes]] = []

    for pw, salt, tag in ((PW_CERT, SALT_SMALL, "small"), (PW_P2, SALT_P2, "p2")):
        for digest in ("md5", "sha256"):
            k, iv = evp_bytes_to_key(pw.encode(), salt, 32, 16, digest)
            items += [
                (f"{tag}_{digest}_key", k),
                (f"{tag}_{digest}_iv", iv.ljust(32, b"\x00")),
                (f"{tag}_{digest}_keyxoriv", bytes(a ^ b for a, b in zip(k, iv.ljust(32, b"\x00")))),
                (f"{tag}_{digest}_sha(pw)", sha256b(pw.encode())),
                (f"{tag}_{digest}_sha(salt)", sha256b(salt)),
            ]

    vals = {"K_C1": K_C1, "K_C2": K_C2, "K_S1": K_S1, "K_S2": K_S2}
    for nm, v in vals.items():
        items.append((nm, v))
    for i, j in itertools.combinations(vals, 2):
        items.append((f"{i}^{j}", bytes(a ^ b for a, b in zip(vals[i], vals[j]))))
    items.append(("E_C31", E_C.ljust(32, b"\x00")))
    items.append(("E_S31", E_S.ljust(32, b"\x00")))
    items.append(("E_CxorE_S", bytes(a ^ b for a, b in zip(E_C.ljust(32, b"\x00"), E_S.ljust(32, b"\x00")))))

    wif = "5K2byJMssxFKuTgnk9YQjpBz5FhkwwF2LaZoAyTus8HjGEpz8AT"
    chain4_pw = bytes.fromhex("38d4f4c90cb45fdfc8cff50d0ed1c57"
                              "40a25de4b8e946d0a5ae2667a23a259cc")
    items += [
        ("blob96", BLOB), ("blob_ct", BLOB[16:]),
        ("b1_79", B1), ("b2_79", B2), ("b1b2", B1 + B2), ("b2b1", B2 + B1),
        ("chain4_pw", chain4_pw), ("wif_kc1", wif.encode()),
        ("ph2_ct", PHASE2_BLOB[16:]), ("pw_cert", PW_CERT.encode()),
        ("sha(b1)", sha256b(B1)), ("sha(b2)", sha256b(B2)),
        ("sha(b1b2)", sha256b(B1 + B2)), ("sha(chain4)", sha256b(chain4_pw)),
    ]

    for nm, kb in items:
        tested += 1
        scan(nm, kb, hits)

    print(f"[offchain] {tested} checks (scalar + xcoord), {time.time()-t0:.2f}s")
    print(f"[offchain] HITS: {len(hits)}")
    for h in hits:
        print("  HIT:", h)
    return 0


if __name__ == "__main__":
    sys.exit(main())