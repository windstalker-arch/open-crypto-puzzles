#!/usr/bin/env python3
"""
oracle.py -- final-gate candidate checker for the GSMG.io puzzle.

Purpose:
    The puzzle's last published page names an OpenSSL AES blob and tells the solver
    to find the password. This script reproduces that specific, publicly documented
    half of the final gate: given a candidate answer string X, it computes
    password = sha256(X).hexdigest(), decrypts the blob printed on the last page
    (OpenSSL legacy "Salted__" format, AES-256-CBC, MD5 key derivation) with that
    password, reduces the resulting plaintext to a 32-byte value with a small set of
    standard readings, derives the uncompressed secp256k1 public key, and compares
    its HASH160 to the escrow address.

    This is NOT the puzzle's own sealed answer-checker (an unpublished tool some
    solvers reference informally); that tool is not public and this repository has
    no access to it, so it is not shipped here. What is shipped is the AES-blob
    pipeline itself, which is fully reproducible from the puzzle's own published
    material and the escrow's on-chain public key.

Usage:
    python3 tools/oracle.py --selftest              # see "Certified against" below
    python3 tools/oracle.py "<candidate answer>"     # try one candidate
    python3 tools/oracle.py --stdin                  # one candidate per line

Input:
    A candidate answer string X.

Output:
    "MATCH <address> reading=<name> priv_hex=<hex> wif=<wif>" on a hit,
    "NO MATCH" otherwise. Exit 0 on any match, 1 if none matched.

Dependencies: stdlib, pycryptodome, ecdsa, base58.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import sys

import base58
from Crypto.Cipher import AES
from ecdsa import SECP256k1, SigningKey

# The blob printed on the puzzle's last published page (128 base64 characters,
# decodes to 96 bytes: "Salted__" + 8-byte salt + 80 bytes of ciphertext).
BLOB_B64 = (
    "U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z"
    "QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ"
)

TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

# The escrow's public key, recovered from its 2024 spending transaction on chain
# (block 840725, txid 88cdb3cd...). Used only by the selftest, to certify the
# address-derivation half of the pipeline against a real, independently checkable
# fact: this pubkey's HASH160 must equal TARGET_ADDRESS.
KNOWN_PUBKEY_HEX = (
    "04f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464"
    "9c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559"
)


# Certification vector: the puzzle's own phase-2 blob, published on
# gsmg.io/choiceisanillusioncreatedbetweenthosewithpowerandthosewithoutaveryspecial
# dessertiwroteitmyself, whose password is the known stage answer sha256("causality").
# This is a real end-to-end vector for the key-derivation and AES half of the pipeline,
# which a self-made round trip cannot provide: a self-made blob is encrypted with the
# same derivation it is then decrypted with, so it cannot detect a wrong digest.
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
PHASE2_MARKER = b"keymakers"


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def evp_bytes_to_key(password: bytes, salt: bytes, key_len: int, iv_len: int,
                     digest: str = "sha256") -> tuple[bytes, bytes]:
    """OpenSSL's EVP_BytesToKey, with the digest selectable.

    This puzzle uses BOTH digests, so neither can be assumed:

      phase 2, phase 3   SHA-256 (the `openssl enc` default since OpenSSL 1.1.0);
                         MD5 yields invalid padding and garbage on both.
      Cosmic Duality     MD5; SHA-256 fails on it.

    An earlier version of this file hardcoded MD5 and described it as the scheme used
    throughout, which is wrong for phases 2 and 3. Hardcoding SHA-256 instead would be
    equally wrong for Cosmic Duality. Since the small blob's password is unknown, its
    digest cannot be determined, so `attempt` tries both."""
    H = hashlib.sha256 if digest == "sha256" else hashlib.md5
    derived, prev = b"", b""
    while len(derived) < key_len + iv_len:
        prev = H(prev + password + salt).digest()
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


def decrypt_blob(blob_b64: str, password: str, digest: str = "sha256") -> bytes | None:
    """Decrypt an OpenSSL "Salted__" AES-256-CBC blob. Returns the unpadded
    plaintext, or None if the header is malformed or padding does not validate."""
    raw = base64.b64decode(blob_b64)
    if raw[:8] != b"Salted__":
        return None
    salt, ciphertext = raw[8:16], raw[16:]
    key, iv = evp_bytes_to_key(password.encode("utf-8"), salt, 32, 16, digest)
    plain = AES.new(key, AES.MODE_CBC, iv).decrypt(ciphertext)
    return unpad_pkcs7(plain)


def readings(plain: bytes) -> list[tuple[str, bytes]]:
    """Standard ways to reduce a decrypted plaintext to a 32-byte private key
    candidate, with no judgment on how the bytes look (binary key material is
    expected, not printable text).

    The documented 79-byte chain artifact is K_C1(32) || K_C2(32) || E_C(15).
    Before the readings audit (2026-09-17) only first32 (=K_C1), last32 (a
    K_C2/E_C straddle, NOT clean), sha256(whole) and sha256(first64) were
    tried: a correct password whose key lives in the clean K_C2 field, an XOR
    of the K-fields, or a reversed/field-hash reading would have been reported
    NO MATCH. This is the full K-field union.
    """
    out = [("sha256(plaintext)", sha256(plain))]
    if len(plain) >= 32:
        out.append(("first32", plain[:32]))
        out.append(("last32", plain[-32:]))
    if len(plain) >= 64:
        out.append(("sha256(first64)", sha256(plain[:64])))
        # the two clean 32-byte fields, as scalars and as field-hashes
        k1, k2 = plain[:32], plain[32:64]
        out.append(("K_C2_field", k2))
        out.append(("sha256(K_C2_field)", sha256(k2)))
        out.append(("sha256(K_C1||K_C2)", sha256(k1 + k2)))
        out.append(("K_C1_xor_K_C2", bytes(a ^ b for a, b in zip(k1, k2))))
        out.append(("sha256(K_C1_xor_K_C2)", sha256(bytes(a ^ b for a, b in zip(k1, k2)))))
    if len(plain) >= 32:
        # tails, field concats and XORs with the trailing short field zero-padded
        left = plain[:32]
        tail15 = plain[64:]
        out.append(("rev(first32)", plain[:32][::-1]))
        out.append(("rev(last32)", plain[-32:][::-1]))
        out.append(("sha256(reversed_plaintext)", sha256(plain[::-1])))
        if len(plain) >= 64:
            second = plain[32:64]
            out.append(("sha256(K_C2||E_C)", sha256(second + tail15)))
            out.append(("sha256(K_C1||E_C)", sha256(left + tail15)))
            ec = tail15.ljust(32, b"\x00")
            out.append(("K_C1_xor_E_Cpad", bytes(a ^ b for a, b in zip(left, ec))))
            out.append(("K_C2_xor_E_Cpad", bytes(a ^ b for a, b in zip(second, ec))))
            out.append(("sha256(K_C1_xor_E_Cpad)", sha256(bytes(a ^ b for a, b in zip(left, ec)))))
            out.append(("sha256(K_C2_xor_E_Cpad)", sha256(bytes(a ^ b for a, b in zip(second, ec)))))
    # md5 double to 32 bytes (hex form is 32 chars not 32 bytes; use digest paired)
    out.append(("md5(plaintext)||md5(plaintext)", hashlib.md5(plain).digest() * 2))
    return out


def priv_to_address(priv_bytes: bytes) -> tuple[str, str]:
    """Uncompressed secp256k1 public key -> HASH160 -> P2PKH address. Returns
    (address, uncompressed_pubkey_hex)."""
    sk = SigningKey.from_string(priv_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    pub = b"\x04" + vk.to_string()
    h160 = hashlib.new("ripemd160", sha256(pub)).digest()
    address = base58.b58encode_check(b"\x00" + h160).decode()
    return address, pub.hex()


def wif_uncompressed(priv_bytes: bytes) -> str:
    return base58.b58encode_check(b"\x80" + priv_bytes).decode()


def attempt(candidate: str) -> tuple[bool, dict]:
    # Certified password conventions for this puzzle's blobs:
    #   phase 2 / phase 3   password = sha256(X).hexdigest(),  SHA-256 EVP digest
    #   small final gate    password = X (raw string),         MD5 EVP digest
    #   cosmic duality      password = X (raw string),         MD5 EVP digest
    # The small gate's raw-X + MD5 form is anchored: it decrypts the 96-byte blob
    # (salt 3ab585348552415d) to the 79-byte chain-1 artifact B1_79B.bin (SHA256
    # 1449a217...). The sha256(X) transform is retained too because phases 2/3 use
    # it, and the blob's digest cannot be assumed. Try password in both raw and
    # sha256-hex form, under both digests, and accept any valid decrypt.
    for password in (candidate, hashlib.sha256(candidate.encode("utf-8")).hexdigest()):
        plains = [(d, decrypt_blob(BLOB_B64, password, d)) for d in ("sha256", "md5")]
        plains = [(d, p) for d, p in plains if p is not None]
        for digest, plain in plains:
            for name, key_bytes in readings(plain):
                if len(key_bytes) != 32:
                    continue
                try:
                    address, _ = priv_to_address(key_bytes)
                except Exception:  # noqa: BLE001  out-of-range scalar, etc.
                    continue
                if address == TARGET_ADDRESS:
                    return True, {
                        "password_form": "raw" if password == candidate else "sha256(X)",
                        "digest": digest,
                        "reading": name,
                        "address": address,
                        "priv_hex": key_bytes.hex(),
                        "wif": wif_uncompressed(key_bytes),
                    }
    return False, {"reason": "no password form/digest/reading matched the address"}


def selftest() -> bool:
    ok = True

    # Part 1: the address-derivation half of the pipeline, certified against a
    # real, independently checkable fact: the escrow's own on-chain public key
    # (recovered from its 2024 spending transaction) must hash to its address.
    pub = bytes.fromhex(KNOWN_PUBKEY_HEX)
    h160 = hashlib.new("ripemd160", sha256(pub)).digest()
    address_from_known_pubkey = base58.b58encode_check(b"\x00" + h160).decode()
    part1 = address_from_known_pubkey == TARGET_ADDRESS
    print(f"HASH160(known on-chain pubkey) -> {TARGET_ADDRESS}: {'OK' if part1 else 'FAIL'}")
    ok = ok and part1

    # Part 2: the AES decrypt implementation, certified against a real puzzle blob.
    # The phase-2 blob's password is a known stage answer, so this exercises
    # evp_bytes_to_key + AES-256-CBC + PKCS7 unpadding end to end against material
    # the puzzle itself published, rather than against a self-made vector.
    phase2_password = sha256(b"causality").hex()
    recovered = decrypt_blob(PHASE2_BLOB_B64, phase2_password)
    part2 = recovered is not None and PHASE2_MARKER in recovered
    print(f"phase-2 blob decrypts under sha256(\"causality\"): {'OK' if part2 else 'FAIL'}")
    ok = ok and part2

    # Part 2b: a wrong password must not validate (no false positive from a
    # coincidentally-valid PKCS7 padding byte).
    wrong = decrypt_blob(PHASE2_BLOB_B64, "definitely the wrong password")
    part2b = wrong is None
    print(f"wrong password on the same blob -> no valid padding: {'OK' if part2b else 'FAIL'}")
    ok = ok and part2b

    # Part 2c: MD5 must fail on the phase-2 blob specifically. This does NOT mean MD5
    # is unused in the puzzle: the Cosmic Duality blob uses MD5 (verified against its
    # published plaintext hash). The two digests appear on different blobs, which is
    # why attempt() tries both rather than assuming either.
    def _md5_derive(password, salt, key_len, iv_len):
        derived, prev = b"", b""
        while len(derived) < key_len + iv_len:
            prev = hashlib.md5(prev + password + salt).digest()
            derived += prev
        return derived[:key_len], derived[key_len:key_len + iv_len]

    raw2 = base64.b64decode(PHASE2_BLOB_B64)
    k2, iv2 = _md5_derive(phase2_password.encode("utf-8"), raw2[8:16], 32, 16)
    md5_plain = AES.new(k2, AES.MODE_CBC, iv2).decrypt(raw2[16:])
    part2c = unpad_pkcs7(md5_plain) is None
    print(f"MD5 fails on the phase-2 blob specifically: {'OK' if part2c else 'FAIL'}")
    ok = ok and part2c

    # Part 2d: the small final gate certifies the RAW password form. The known raw
    # concatenation of the SalPhaseIon tokens (matrixsumlist + enter +
    # lastwordsbeforearchichoice + thispassword + matrixsumlist) decrypts the 96-byte
    # blob (salt 3ab585348552415d) with EVP-MD5 to the 79-byte chain-1 artifact
    # B1_79B.bin (SHA256 1449a217...). Same AES/padding code path as attempt(),
    # password used directly (NOT sha256(X)). This is why attempt() now tries X raw.
    RAW_PW = "matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist"
    RAW_PLAIN_SHA = "1449a2178eea7c0e3fabac8c1ad2afa294be4fc1800c594a025a056e88c626bf"
    _check = decrypt_blob(BLOB_B64, RAW_PW, "md5")
    raw_ok = _check is not None and sha256(_check).hex() == RAW_PLAIN_SHA
    print(f"small-blob re-decrypts under raw password + MD5 -> B1_79B.bin: {'OK' if raw_ok else 'FAIL'}")
    ok = ok and raw_ok
    # And the sha256(X) form must NOT be what opens it (it is the falsified premise).
    _hex_only = decrypt_blob(BLOB_B64, hashlib.sha256(RAW_PW.encode()).hexdigest(), "md5")
    raw_excl = _hex_only is None
    print(f"sha256(hex) form on the same password yields no padding: {'OK' if raw_excl else 'FAIL'}")
    ok = ok and raw_excl

    # Part 2e: the extended K-field readings (readings-audit, 2026-09-17) are
    # shape-certified against the real 79-byte artifact: first32 IS the chain-1
    # key K_C1, and the new construction readings are unambiguous slices/hashes
    # that all land on 32-byte values the address pipeline can consume. This is
    # a positive control tied to published material, not a self-made digest.
    _b1 = decrypt_blob(BLOB_B64, RAW_PW, "md5")
    _names = dict(readings(_b1))
    first32_ok = _names.get("first32") == _b1[:32]
    k2_field_ok = _names.get("K_C2_field") == _b1[32:64]
    k1_ok = k2_ok = xor_ok = tails_ok = rev_ok = True
    k1, k2, tail15 = _b1[:32], _b1[32:64], _b1[64:]
    if len(tail15) == 15:
        k1_ok = _names.get("sha256(K_C1||K_C2)") == sha256(k1 + k2)
        k2_ok = _names.get("sha256(K_C2||E_C)") == sha256(k2 + tail15)
        ec = tail15.ljust(32, b"\x00")
        xor_ok = _names.get("K_C1_xor_K_C2") == bytes(a ^ b for a, b in zip(k1, k2))
        tails_ok = _names.get("rev(last32)") == _b1[-32:][::-1]
        rev_ok = _names.get("sha256(reversed_plaintext)") == sha256(_b1[::-1])
    shape_ok = first32_ok and k2_field_ok and k1_ok and k2_ok and xor_ok and tails_ok and rev_ok
    _all32 = all(len(v) == 32 for v in _names.values())
    print(f"extended K-field readings shape-certified on B1_79 (all 32B, known fields): "
          f"{'OK' if shape_ok and _all32 else 'FAIL'}")
    ok = ok and shape_ok and _all32

    # Part 3: the real blob decodes to the documented shape (96 bytes total,
    # 8-byte salt, 80 bytes ciphertext = 5 AES blocks), independent of password.
    raw = base64.b64decode(BLOB_B64)
    part3 = raw[:8] == b"Salted__" and len(raw) == 96 and raw[8:16].hex() == "3ab585348552415d"
    print(f"published blob shape (96 bytes, salt 3ab585348552415d): {'OK' if part3 else 'FAIL'}")
    ok = ok and part3

    # Part 4: byte-exact provenance of BLOB_B64 from the page itself. On the
    # 2023-06-01 byte-exact textarea capture, the blob is printed split around the
    # second a/b run: [64-char head ending '9z'] [40-char a/b run] [64-char tail].
    # Re-joining head + tail reproduces BLOB_B64 exactly; removing the embedded run is
    # the only edit needed. The two a/b runs on the page decode (a=0, b=1, 8 bits per
    # byte) to the password tokens 'matrixsumlist' and 'enter' that feed RAW_PW.
    _run_msl = "abbabbababbaaaababbbabaaabbbaabaabbabaababbbbaaaabbbaabbabbbabababbabbababbabbaaabbabaababbbaabbabbbabaa"
    _run_enter = "abbaabababbabbbaabbbabaaabbaabababbbaaba"
    _dec = lambda _r: bytes(
        int("".join("0" if c == "a" else "1" for c in _r)[i : i + 8], 2)
        for i in range(0, len(_r), 8)
    )
    part4a = _dec(_run_msl) == b"matrixsumlist" and _dec(_run_enter) == b"enter"
    part4b = BLOB_B64.startswith("U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z")
    part4c = BLOB_B64.endswith("QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ")
    part4d = len(_run_msl) == 104 and len(_run_enter) == 40
    part4 = part4a and part4b and part4c and part4d
    print(f"page provenance: blob split around a/b runs; runs decode to "
          f"'matrixsumlist'/'enter'; head+tail == BLOB_B64: {'OK' if part4 else 'FAIL'}")
    ok = ok and part4

    if ok:
        print("SELFTEST OK")
        print(
            "Note: part 1 certifies the address half against on-chain data; parts 2, "
            "2b and 2c certify the key-derivation and AES half against a real puzzle "
            "blob whose password is known. The puzzle uses SHA-256 on phases 2 and 3 "
            "and MD5 on Cosmic Duality, so attempt() tries both. X remains unsolved."
        )
    return ok


def _print_result(candidate: str) -> bool:
    matched, info = attempt(candidate)
    if matched:
        print(f"MATCH {info['address']} reading={info['reading']} priv_hex={info['priv_hex']} wif={info['wif']}")
    else:
        print("NO MATCH")
    return matched


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", nargs="?", help="candidate answer string X")
    parser.add_argument("--stdin", action="store_true", help="read candidates, one per line")
    parser.add_argument("--selftest", action="store_true", help="run the certification checks")
    args = parser.parse_args()

    if args.selftest:
        return 0 if selftest() else 1

    if args.stdin:
        any_hit = False
        for line in sys.stdin:
            line = line.rstrip("\n")
            if not line:
                continue
            any_hit = _print_result(line) or any_hit
        return 0 if any_hit else 1

    if not args.candidate:
        parser.print_help()
        return 0

    return 0 if _print_result(args.candidate) else 1


if __name__ == "__main__":
    sys.exit(main())
