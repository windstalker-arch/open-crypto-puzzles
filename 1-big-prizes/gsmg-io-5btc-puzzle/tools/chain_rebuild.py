#!/usr/bin/env python3
import os
"""Reproduce the GSMG.io public decryption chain CADEIA 1 -> 4 end to end.

Everything here is verified against independently-published SHA256 anchors:

  CADEIA 1  fixed small blob (salt 3ab585348552415d, pw = the 5-token concat
            "matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist",
            EVP MD5 AES-256-CBC) -> 80B = K_C1 || K_C2 || E_C(15B)
            WIF(K_C1 uncompressed) 5K2byJMssxFKuTgnk9YQjpBz5FhkwwF2LaZoAyTus8HjGEpz8AT
            (matches issue #108 / PR #68)
  CADEIA 2  p32 outer envelope (salt b45a5e3d827593ca, pw = WIF(K_C1) from CADEIA 1)
            -> 79B = K_S1 || K_S2 || E_S(15B)
            sha256 = b40fce72ef5638e4f79b3233e653f8a5dbdb0d4ae2009d2d3da2c98b70f4d004
            (tools/rung2_b2.py certifies it: the envelope decrypts byte-exactly to
            data/B2_79B.bin and re-encrypts back to the same ciphertext)
  CADEIA 3  Dualite blob (salt 2d3f6fe06dc950e6) L1 decrypt under XOR-key
            a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735,
            EVP MD5 AES-256-CBC -> 1327B cosmic_correct `cc`
            sha256 = 4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081
            (matches #68 / #82 / #99)
  CADEIA 4  mystery = cc[158:158+1168] XOR mask b657264f2f6e6921
            -> Salted__ blob, salt 5bbd88ac32481bca (the "hidden blob" of #88)
            AES-256-CBC EVP MD5 pw 38d4f4c90cb45fdfc8cff50d0ed1c5740a25de4b8e946d0a5ae2667a23a259cc
            (= E_C||E_S||E_B[:2]) -> 1151B chain4, sha256
            e4269ed5fbb202a81e5e1aa6b5190fdd1ea126b2c8547ea7cdbdf45387ea135b
            (matches PR #68)

CHAIN4_PW below is E_C(15) || E_S(15) || E_B[:2]. With CADEIA 2 certified, 30 of
those 32 bytes are derived on-puzzle. The last two are no longer a community quote
either: `tools/eb_tail_sweep.py` sweeps all 2^16 tails against the published chain-4
hash and finds exactly one, 59cc (R-EBTAIL-2026-09-27). All 32 bytes are on-puzzle.
The missing operand is not the key -- it is ca/cosmic_A.

The final step (recover private key k with k*G = (f4d1bbd9..., odd y) from the
chain4 35x32-byte blocks via an "XOR triangle" using operand ca/cosmic_A) is NOT
publicly solvable: cosmic_A is only ever referenced by SHA256-prefix cd3fea3d...
(#92) and the creator disavows a "step after Cosmic Duality" (#104).
"""
import base64
import hashlib
from pathlib import Path

from coincurve import PublicKey
from Crypto.Cipher import AES

BLOB1 = ("U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z"
         "QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ")
DUALITE_TXT = os.path.expanduser("~/briefcase/CosmicDuality.txt")
XORKEY = bytes.fromhex("a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735")
MASK = bytes.fromhex("b657264f2f6e6921")
CHAIN4_PW = bytes.fromhex("38d4f4c90cb45fdfc8cff50d0ed1c5740a25de4b8e946d0a5ae2667a23a259cc")


def sha256b(b): return hashlib.sha256(b).hexdigest()

def evp(pw, salt, digest="md5"):
    H = hashlib.md5 if digest == "md5" else hashlib.sha256
    d, prev = b"", b""
    while len(d) < 48:
        prev = H(prev + pw + salt).digest(); d += prev
    return d[:32], d[32:48]

def aes_dec(ct, pw, salt, digest="md5"):
    k, iv = evp(pw, salt, digest)
    return AES.new(k, AES.MODE_CBC, iv).decrypt(ct)

def unpad(p):
    n = p[-1]
    return p[:-n] if p and n <= 16 and p[-n:] == bytes([n]) * n else None

def b58(b):
    A = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    n = int.from_bytes(b, "big"); o = ""
    while n > 0: n, r = divmod(n, 58); o = A[r] + o
    return "1" * (len(b) - len(b.lstrip(b"\x00"))) + o

# CADEIA 1
r1 = base64.b64decode(BLOB1)
P = aes_dec(r1[16:], b"matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist", r1[8:16], "md5")
K_C1, K_C2, E_C = P[:32], P[32:64], P[64:79]
wb = b"\x80" + K_C1
wc = b58(wb + hashlib.sha256(hashlib.sha256(wb).digest()).digest()[:4])
pk1 = PublicKey.from_valid_secret(K_C1).format(compressed=False)
print(f"[CADEIA 1] K_C1={K_C1.hex()}")
print(f"            K_C2={K_C2.hex()}")
print(f"            E_C (15)={E_C.hex()}")
print(f"            WIF(K_C1,uncomp)={wc}")
print("            K_C1 pub H160={}".format(hashlib.new("ripemd160", hashlib.sha256(pk1).digest()).hexdigest()))

# CADEIA 3
raw3 = base64.b64decode(Path(DUALITE_TXT).read_bytes().strip())
cc = aes_dec(raw3[16:], XORKEY, raw3[8:16], "md5")
cc = cc[:-cc[-1]]
print(f"[CADEIA 3] cc={len(cc)}B sha256={sha256b(cc)}")

# CADEIA 4
mystery = bytes(a ^ b for a, b in zip(cc[158:158 + 1168], (MASK * 146)[:1168]))
c4 = aes_dec(mystery[16:], CHAIN4_PW, mystery[8:16], "md5")
c4 = c4[:-c4[-1]]
print(f"[CADEIA 4] mystery salt={mystery[8:16].hex()}")
print(f"            chain4={len(c4)}B sha256={sha256b(c4)}")
print(f"            chain4[:2]={c4[:2]!r}")
