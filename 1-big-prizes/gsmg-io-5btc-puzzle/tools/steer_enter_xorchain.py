#!/usr/bin/env python3
"""Steer battery: "your last command" -> "enter".

The Dualite/Cosmic blob's 32-byte password is the XOR chain of sha256 of seven
tokens (canonical order): matrixsumlist, enter, lastwordsbeforearchichoice,
thispassword, matrixsumlist, yourlastcommand, secondanswer
-> XK a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735,
used RAW as the password with EVP-MD5 -> 1327B plaintext sha256 4f7a1e4e...

The steer decodes token 6 (`yourlastcommand`) to `enter` (the page's decoded
40-token a/b run), which prior rows (late-82 permuted the LITERAL token, never
the decoded value) never applied to the XOR-chain derivation. This battery
recomputes the XOR key for a small family of token-6 spellings (and order
variants), decrypts the Dualite blob under each, reduces the plaintext with both
the standard readings and the extended set from oracle_dualite.py, and compares
P2PKH (comp+uncomp) to both funded gates.

Witness: the canonical token list must reproduce XK a795de11... and plaintext
sha256 4f7a1e4e... through the SAME code path.
"""
from __future__ import annotations
import os

import base64
import hashlib
import sys
import time
from pathlib import Path

from Crypto.Cipher import AES

DUALITE_B64_TXT = os.path.expanduser("~/briefcase/CosmicDuality.txt")

CANON_XK = "a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735"
CANON_PT_SHA = "4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081"

BASES = [
    "matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
    "matrixsumlist", "yourlastcommand", "secondanswer",
]
T6_VARIANTS = [
    "yourlastcommand",       # canonical
    "enter", "ENTER", "Enter",
    "yourlastcommandenter", "yourlastcommand^enter",
    "your last command", "your-last-command", "your_last_command",
    "lastcommand", "yourcommand", "enterenter", "e n t e r", "	enter",
    "matrixsumlist", "secondanswer", "thispassword",
]
ORDER_VARIANTS = [
    ("matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
     "matrixsumlist", "secondanswer", "enter"),
    ("matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
     "matrixsumlist", "enter", "secondanswer", "enter"),
    ("enter", "matrixsumlist", "lastwordsbeforearchichoice", "thispassword",
     "matrixsumlist", "enter", "secondanswer"),
]

X = 0xF4D1BBD91E65E2A019566A17574E97DAE908B784B388891848007E4F55D5A464
Y_EXPECT = 0x9C73D25FC5ED8FD7227CAB0BE4E576C0C6404DB5AA546286563E4BE12BF33559
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GATES = {"g1": "a9553269572a317e39f0f518cb87c1a0ee1dbae4",
         "g2": "4bc468447fe1b048ad030a2f9a125478eabc4ed6"}


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def sha256h(s: str) -> bytes:
    return sha256(s.encode())


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def evp_md5(password: bytes, salt: bytes, key_len=32, iv_len=16):
    derived, prev = b"", b""
    while len(derived) < key_len + iv_len:
        prev = hashlib.md5(prev + password + salt).digest()
        derived += prev
    return derived[:key_len], derived[key_len:key_len + iv_len]


def unpad_pkcs7(data: bytes) -> bytes | None:
    if not data:
        return None
    n = data[-1]
    if n < 1 or n > 16 or n > len(data):
        return None
    if data[-n:] != bytes([n]) * n:
        return None
    return data[:-n]


def decrypt_dualite(password: bytes, digest="md5") -> bytes | None:
    raw = base64.b64decode("".join(open(DUALITE_B64_TXT).read().split()))
    if raw[:8] != b"Salted__":
        return None
    salt, ct = raw[8:16], raw[16:]
    if digest == "md5":
        key, iv = evp_md5(password, salt)
    else:
        derived, prev = b"", b""
        while len(derived) < 48:
            prev = hashlib.sha256(prev + password + salt).digest()
            derived += prev
        key, iv = derived[:32], derived[32:48]
    return unpad_pkcs7(AES.new(key, AES.MODE_CBC, iv).decrypt(ct))


def readings(plain: bytes):
    out = [("sha256(pt)", sha256(plain))]
    if len(plain) >= 32:
        out += [("first32", plain[:32]), ("last32", plain[-32:])]
    if len(plain) >= 64:
        out += [("sha256(first64)", sha256(plain[:64]))]
    # extended readings from oracle_dualite
    out += [("first64", plain[:64]), ("last64", plain[-64:]),
            ("rev-first32", plain[:32][::-1]), ("rev-last32", plain[-32:][::-1]),
            ("sha256(first32)", sha256(plain[:32])), ("sha256(last32)", sha256(plain[-32:])),
            ("md5(first32)", hashlib.md5(plain[:32]).digest()),
            ("md5(last32)", hashlib.md5(plain[-32:]).digest())]
    return out


B58A = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58check(prefix, payload):
    raw = prefix + payload
    cs = sha256(sha256(raw))[:4]
    n = int.from_bytes(raw + cs, "big")
    o = ""
    while n:
        n, r = divmod(n, 58)
        o = B58A[r] + o
    return "1" * (len(raw + cs) - len((raw + cs).lstrip(b"\x00"))) + o


def priv_to_addrs(kb: bytes):
    import coincurve
    try:
        x, y = coincurve.PublicKey.from_valid_secret(kb).point()
    except Exception:
        return None
    up = b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")
    cp = (b"\x03" if y & 1 else b"\x02") + x.to_bytes(32, "big")
    return [b58check(b"\x00", hashlib.new("ripemd160", sha256(f)).digest())
            for f in (up, cp)]


def check_readings(plain: bytes, tag: str, hits: list[str]) -> None:
    for name, kb in readings(plain):
        if len(kb) != 32:
            continue
        try:
            import coincurve
            x, y = coincurve.PublicKey.from_valid_secret(kb).point()
        except Exception:
            continue
        if x == X and y == Y_EXPECT:
            hits.append(f"{tag}:{name}:GATE1-X")
        for label, kbfmt in (("up", b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")),
                             ("cp", (b"\x03" if y & 1 else b"\x02") + x.to_bytes(32, "big"))):
            h = hashlib.new("ripemd160", sha256(kbfmt)).hexdigest()
            if h in GATES.values():
                hits.append(f"{tag}:{name}:{h}")


def main() -> int:
    t0 = time.time()
    hits: list[str] = []

    # --- witness: canonical chain ---
    canon = BASES
    xk_canon = b"\x00" * 32
    for t in canon:
        xk_canon = xor_bytes(xk_canon, sha256h(t))
    pt_canon = decrypt_dualite(xk_canon, "md5")
    assert xk_canon.hex() == CANON_XK, xk_canon.hex()
    assert pt_canon is not None and sha256(pt_canon).hex() == CANON_PT_SHA
    print("WITNESS OK: canonical XK and plaintext sha256 reproduce exactly")

    total = 0
    # --- token-6 variants (position 6 = index 5) ---
    lists = []
    for t6 in T6_VARIANTS:
        lst = BASES[:5] + [t6] + BASES[6:]
        lists.append((f"T6={t6!r}", lst))
    for ov in ORDER_VARIANTS:
        lists.append(("order:" + ",".join(ov[:3]), list(ov)))
    for i, (tag, lst) in enumerate(lists):
        xk = b"\x00" * 32
        for t in lst:
            xk = xor_bytes(xk, sha256h(t))
        pt = decrypt_dualite(xk, "md5")
        total += 1
        if pt is None:
            continue
        # also try sha256(xk-hex) and xk-hex-ascii as password? those are X-forms;
        # the canonical uses raw xk bytes; try raw ascii-hex variant too
        check_readings(pt, f"{tag}[md5]", hits)
        pt2 = decrypt_dualite(xk, "sha256")
        total += 1 if pt2 is not None else 0
        if pt2 is not None:
            check_readings(pt2, f"{tag}[sha256]", hits)
        # ascii-hex of xk as password
        xks = xk.hex().encode()
        pt3 = decrypt_dualite(xks, "md5")
        total += 1 if pt3 is not None else 0
        if pt3 is not None:
            check_readings(pt3, f"{tag}[xkhex-md5]", hits)

    print(f"[steer-enter] {total} decrypt attempts ({len(lists)} chains), "
          f"{time.time()-t0:.1f}s, HITS={len(hits)}")
    for h in hits:
        print("  HIT:", h)
    return 0


if __name__ == "__main__":
    sys.exit(main())