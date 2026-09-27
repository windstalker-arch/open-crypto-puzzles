#!/usr/bin/env python3
"""CADEIA 2 (the B2 rung) is a real rung, and its password is DERIVED, not authored.

The 96-byte p32 outer envelope (issue #22 base64, transcribed in
`tools/mirror79_research.py`) is NOT a third copy of the small half and NOT a
community fabrication. Under the WIF of the first 32 bytes of B1 it decrypts
byte-exactly to `data/B2_79.bin`:

  p32 outer, salt b45a5e3d827593ca, ct 80 B  ->  plaintext 79 B + 1 pad byte
  password = WIF(K_C1, uncompressed) 5K2byJMssxFKuTgnk9YQjpBz5FhkwwF2LaZoAyTus8HjGEpz8AT
  KDF      = EVP_BytesToKey with MD5, AES-256-CBC
  plaintext sha256 = b40fce72ef5638e4f79b3233e653f8a5dbdb0d4ae2009d2d3da2c98b70f4d004
                   == sha256(data/B2_79.bin)

So the ladder is  raw words -> (B1 envelope) -> B1 -> WIF -> (p32 outer) -> B2
and the B2 tail E_S is anchored, not asserted. That matters beyond B2 itself:
the chain-4 AES password used by `tools/chain_rebuild.py` is

  E_C(15) || E_S(15) || 59cc  =  38d4f4c9..d1c5 || 740a25de..23a2 || 59cc

so 30 of its 32 bytes are now derived on-puzzle rather than quoted from a
commenter. The remaining 2 bytes (E_B[:2] = 59cc) are still community-sourced;
they occur in neither B1, B2 nor chain4.

Why this was missed for weeks: the earlier "B2 has no envelope" rows swept the
envelope against ~60 *authorial password strings*. The password that opens it is
not a string anyone wrote - it is a value computed out of B1. Sweeping authorial
strings over a derived-password chain can never find it.

Run:  python3 tools/rung2_b2.py [--selftest]
`--selftest` is the default behaviour; the script asserts every anchor and exits
non-zero if any of them stops holding.
"""
import base64
import hashlib
import sys
from pathlib import Path

from coincurve import PublicKey
from Crypto.Cipher import AES

FOLDER = Path(__file__).resolve().parent.parent
DATA = FOLDER / "data"

# issue #22 base64 of the p32 outer envelope, identical to the transcription in
# tools/mirror79_research.py (lines 56-58) and to ~/Download/Telegram/p32b.b64.txt
B2_BLOB = ("U2FsdGVkX1+0Wl49gnWTyiimluu7V3+vl7st0gUt9sWDzNLxDmlPMsDSiuW2a46zg"
           "KlIi8aaqY5gpJPPEzW1n9n3/26qs4zstWtPKF8Zs/BTNN4IiEh4qu18mdC0NAv4")
# the small half, for the control rung
B1_BLOB = ("U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z"
           "QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ")

RAW_PW = b"matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist"
CHAIN4_PW = bytes.fromhex("38d4f4c90cb45fdfc8cff50d0ed1c5740a25de4b8e946d0a5ae2667a23a259cc")

A = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def sha256b(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def b58(raw: bytes) -> str:
    n = int.from_bytes(raw, "big")
    o = ""
    while n > 0:
        n, r = divmod(n, 58)
        o = A[r] + o
    return "1" * (len(raw) - len(raw.lstrip(b"\x00"))) + o


def b58check(prefix: bytes, payload: bytes) -> str:
    raw = prefix + payload
    return b58(raw + sha256b(sha256b(raw))[:4])


def wif(key32: bytes) -> str:
    return b58check(b"\x80", key32)


def addr_of(pub65: bytes) -> str:
    return b58check(b"\x00", hashlib.new("ripemd160", sha256b(pub65)).digest())


def evp(pw: bytes, salt: bytes, dg: str = "md5") -> tuple[bytes, bytes]:
    h = hashlib.md5 if dg == "md5" else hashlib.sha256
    d, prev = b"", b""
    while len(d) < 48:
        prev = h(prev + pw + salt).digest()
        d += prev
    return d[:32], d[32:48]


def unpad(b: bytes) -> bytes:
    n = b[-1]
    assert 1 <= n <= 16 and b[-n:] == bytes([n]) * n, "bad PKCS7"
    return b[:-n]


def aes_dec(ct: bytes, pw: bytes, salt: bytes, dg: str = "md5") -> bytes:
    k, iv = evp(pw, salt, dg)
    return AES.new(k, AES.MODE_CBC, iv).decrypt(ct)


def aes_enc(pt: bytes, pw: bytes, salt: bytes, dg: str = "md5") -> bytes:
    k, iv = evp(pw, salt, dg)
    n = 16 - len(pt) % 16
    return AES.new(k, AES.MODE_CBC, iv).encrypt(pt + bytes([n]) * n)


def pub_of(key32: bytes) -> bytes:
    """Uncompressed SEC1 point for a 32-byte scalar."""
    return PublicKey.from_valid_secret(key32).format(compressed=False)


def main() -> int:
    ok = True
    B1 = (DATA / "B1_79.bin").read_bytes()
    B2 = (DATA / "B2_79.bin").read_bytes()

    # --- rung 0 (CONTROL, must fire): small half envelope -> B1 -------------
    r1 = base64.b64decode(B1_BLOB)
    p1 = unpad(aes_dec(r1[16:], RAW_PW, r1[8:16]))
    h1 = sha256b(B1).hex()
    print(f"[control] small half salt={r1[8:16].hex()} ct={len(r1) - 16}B "
          f"-> {len(p1)}B")
    print(f"          B1_79 sha256={h1}")
    ok &= p1 == B1
    print(f"          envelope plaintext == data/B1_79.bin : {p1 == B1}")

    K_C1, K_C2, E_C = B1[:32], B1[32:64], B1[64:79]
    K_S1, K_S2, E_S = B2[:32], B2[32:64], B2[64:79]
    w = wif(K_C1)
    print(f"[rung 1]  WIF(K_C1) = {w}")
    ok &= w == "5K2byJMssxFKuTgnk9YQjpBz5FhkwwF2LaZoAyTus8HjGEpz8AT"

    # --- rung 2 (the finding): p32 outer envelope, password = WIF(K_C1) ----
    r2 = base64.b64decode(B2_BLOB)
    print(f"[rung 2]  p32 outer salt={r2[8:16].hex()} ct={len(r2) - 16}B")
    print(f"          envelope sha256={sha256b(r2).hex()}")
    p2 = unpad(aes_dec(r2[16:], w.encode(), r2[8:16]))
    h2 = sha256b(p2).hex()
    print(f"          plaintext {len(p2)}B sha256={h2}")
    ok &= p2 == B2
    print(f"          envelope plaintext == data/B2_79.bin : {p2 == B2}")

    # --- forward control for rung 2 (no padding ambiguity) ------------------
    re = aes_enc(B2, w.encode(), r2[8:16])
    print(f"[control] re-encrypt B2_79 under the same key reproduces the ct : "
          f"{re == r2[16:]}")
    ok &= re == r2[16:]

    # --- the same-ciphertext claim from the older rows ---------------------
    r1_again = base64.b64decode(B1_BLOB)
    print(f"          small-half ct == p32-outer ct : {r1_again[16:] == r2[16:]} "
          f"(distinct envelopes, distinct ciphertexts)")

    # --- what the finding anchors downstream -------------------------------
    print(f"[chain4]  E_C={E_C.hex()}  E_S={E_S.hex()}")
    print(f"          E_C||E_S||{CHAIN4_PW[30:].hex()} == CHAIN4_PW : "
          f"{E_C + E_S + CHAIN4_PW[30:] == CHAIN4_PW}")
    ok &= E_C + E_S + CHAIN4_PW[30:] == CHAIN4_PW
    print("          30 of the 32 chain-4 password bytes are now derived on-puzzle;")
    print(f"          E_B[:2]={CHAIN4_PW[30:].hex()} still has no on-puzzle source "
          f"(absent from B1: {CHAIN4_PW[30:].hex() not in B1.hex()}, "
          f"B2: {CHAIN4_PW[30:].hex() not in B2.hex()})")

    # --- the four ladder keys ---------------------------------------------
    # WITNESS for the address path itself: K_C1's compressed address is a value
    # already recorded elsewhere in the repo, so a wrong scalar->point routine
    # cannot slip through silently.
    for nm, k32 in (("K_C1", K_C1), ("K_C2", K_C2), ("K_S1", K_S1), ("K_S2", K_S2)):
        pub = pub_of(k32)
        comp = PublicKey.from_valid_secret(k32).format(compressed=True)
        h = hashlib.new("ripemd160", sha256b(pub)).hexdigest()
        print(f"[ladder]  {nm} {wif(k32)}")
        print(f"          h160(uncomp)={h}  addr(uncomp)={addr_of(pub)}")
        print(f"          addr(comp)  ={addr_of(comp)}")
        if nm == "K_C1":
            ok &= addr_of(comp) == "14zJ3RHPxiRJAmYHUNTvPoCTxhFB6gACgf"
            print(f"          witness: == the address already recorded for K_C1*G : "
                  f"{addr_of(comp) == '14zJ3RHPxiRJAmYHUNTvPoCTxhFB6gACgf'}")

    print("RESULT:", "ALL ANCHORS HOLD" if ok else "ANCHOR FAILURE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
