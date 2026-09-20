#!/usr/bin/env python3
"""
sha3_variants.py -- sweep the small-blob gate across SHA3 / SHAKE digest variants.

Context (see analysis/tested.md s.117/118): the page token `shabef` maps to SHA-3.
Prior work tested ONLY sha3_256(X).hexdigest()/raw as the password rule with EVP
digests {md5, sha256, sha3_256}. This adds the OTHER NIST SHA-3 variants and the
SHAKE XOFs as the password digest, plus the phase-2 blob as the certification
witness (phase-2 password = sha256("causality")).

Password rules (given candidate X, the AES blob password string P):
  P = <digest>(X).hexdigest()      (hex)
  P = <digest>(X).digest()         (raw bytes -> latin-1 string)
where <digest> in {sha3_224, sha3_256, sha3_384, sha3_512, shake_128(32),
shake_256(32), sha256}, over EVP digests {md5, sha256, sha3_256}, x 4 plaintext
readings. No seeded guess; this is a coverage test of the variant space.
"""
import base64
import hashlib
import sys

from Crypto.Cipher import AES
from ecdsa import SECP256k1, SigningKey

BLOB_B64 = (
    "U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z"
    "QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ"
)
TARGET = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
PHASE2_BLOB_B64 = (
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
    "Sb8OecflOT2hw37WL49uADgeWgnp2bzkfGIq7EYS7OImjZZwY5h4sfcPfhvQ9kOV"
)


def hash_bytes(digest_name: str, data: bytes) -> bytes:
    k = digest_name
    if k.startswith("shake_"):
        length = int(k.split("_")[1])
        return hashlib.shake_128(data).digest(length) if length == 128 else hashlib.shake_256(data).digest(length)
    return hashlib.new(k, data).digest()


def evp(password: bytes, salt: bytes, key_len: int, iv_len: int, digest: str):
    H = hashlib.sha256 if digest == "sha256" else hashlib.md5 if digest == "md5" else (lambda d: hashlib.new("sha3_256", d))
    derived, prev = b"", b""
    while len(derived) < key_len + iv_len:
        prev = H(prev + password + salt).digest()
        derived += prev
    return derived[:key_len], derived[key_len:key_len + iv_len]


def unpad(data: bytes):
    if not data:
        return None
    n = data[-1]
    if n < 1 or n > 16 or n > len(data):
        return None
    if data[-n:] != bytes([n]) * n:
        return None
    return data[:-n]


def decrypt(blob_b64: str, password: str, evp_digest: str):
    raw = base64.b64decode(blob_b64)
    if raw[:8] != b"Salted__":
        return None
    salt, ct = raw[8:16], raw[16:]
    key, iv = evp(password.encode("utf-8"), salt, 32, 16, evp_digest)
    plain = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
    return unpad(plain)


def readings(plain: bytes):
    out = [("sha256p", hashlib.sha256(plain).digest())]
    if len(plain) >= 32:
        out.append(("first32", plain[:32]))
        out.append(("last32", plain[-32:]))
    if len(plain) >= 64:
        out.append(("sha256first64", hashlib.sha256(plain[:64]).digest()))
    return out


def addr_of(priv: bytes):
    sk = SigningKey.from_string(priv, curve=SECP256k1)
    vk = sk.get_verifying_key()
    pub = b"\x04" + vk.to_string()
    h160 = hashlib.new("ripemd160", hashlib.sha256(pub).digest()).digest()
    return base58_check(h160)


def base58_check(h160: bytes):
    import base58
    return base58.b58encode_check(b"\x00" + h160).decode()


PASSWORD_DIGESTS = ["sha3_224", "sha3_256", "sha3_384", "sha3_512", "shake_128", "shake_256", "sha256"]
EVP_DIGESTS = ["md5", "sha256", "sha3_256"]


def test_one(candidate: str, verbose=False):
    hits = []
    for pd in PASSWORD_DIGESTS:
        pbytes = hash_bytes(pd, candidate.encode("utf-8"))
        for form, pstr in (("hex", pbytes.hex()), ("raw", pbytes.decode("latin-1"))):
            for ed in EVP_DIGESTS:
                plain = decrypt(BLOB_B64, pstr, ed)
                if plain is None:
                    continue
                for rname, kb in readings(plain):
                    if len(kb) != 32:
                        continue
                    address = addr_of(kb)
                    if address == TARGET:
                        hits.append((pd, form, ed, rname, kb.hex()))
    return hits


def selftest():
    p2 = sha_hash("sha256", b"causality")
    rec = decrypt(PHASE2_BLOB_B64, p2, "sha256")
    assert rec is not None and b"keymakers" in rec, "phase-2 vector failed"
    # positive control of the sha3 plumbing: sha3_256("foo") known hex
    ctrl = hashlib.new("sha3_256", b"foo").hexdigest()
    assert ctrl == "76d3bc41c9f588f7fcd0d5bf4718f8f84b1c41b20882703100b9eb9413807c01", "sha3 known vector failed"
    return True


def sha_hash(name, data):
    return hashlib.new(name, data).hexdigest()


def main(argv):
    if "--selftest" in argv:
        print("selftest", "OK" if selftest() else "FAIL")
        return 0 if selftest() else 1
    candidates = [l.rstrip("\n") for l in sys.stdin if l.strip()]
    total = 0
    for c in candidates:
        hits = test_one(c)
        total += len(hits)
        if hits:
            print("MATCH", c, hits)
    print(f"DONE {len(candidates)} cands, {total} hits")
    return 0 if total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
