#!/usr/bin/env python3
"""
oracle.py -- candidate checker for Andy Bauch's "New Money" COG triptych.

Purpose:
    Given a candidate private key, as 64 hex characters or as a WIF string (compressed
    or uncompressed), derive both the compressed and uncompressed P2PKH addresses and
    compare each byte-exact to the COG escrow address. COG's one on-chain spend reveals
    a compressed public key, so a compressed WIF is the expected payload shape, but this
    oracle checks both forms so a raw-hex or uncompressed-WIF candidate is not missed.

Usage:
    python3 tools/oracle.py --selftest                 # must print SELFTEST OK
    python3 tools/oracle.py "<64 hex chars>"
    python3 tools/oracle.py "<WIF string>"
    python3 tools/oracle.py --stdin                     # one candidate per line

Input:
    A single candidate on the command line: 64 hex characters, or a base58check WIF
    (51 characters starting with 5 for uncompressed, 52 starting with K or L for
    compressed). One per line on stdin for --stdin.

Output:
    "MATCH <address> (<compressed|uncompressed>)" for a hit, "NO MATCH" otherwise.
    Exit 0 on any match, 1 if none.

Dependencies:
    stdlib, ecdsa, base58.
"""

from __future__ import annotations

import argparse
import hashlib
import sys

import base58
import ecdsa

TARGET_ADDRESS = "1HLodS8H2GoWbnBXWcz7EkY773dKdD4JEv"

# Public test vector, unrelated to COG: the private key behind Andy Bauch's already-solved
# sibling piece BITCOIN $60 in the same "New Money" series (minikey "SnoMtVnKbtCGApncmTzEXSep4kD4Gs",
# SHA-256'd per the series' own published mechanism). Its uncompressed address is the real,
# on-chain address of that solved piece. This certifies the general secp256k1 -> hash160 ->
# base58check pipeline used here; it does not depend on COG's own unknown encoding.
SELFTEST_PRIV_HEX = "f328af1da84271c144ed27196a3e8e659b6051f725403c7806c6d266dccb7407"
SELFTEST_UNCOMPRESSED_ADDRESS = "1HvEJG5JR84MVpncXcDVBqx65uY5odr6fP"
SELFTEST_COMPRESSED_ADDRESS = "19x4S51LV5TBo4DyecF1RqvNXQubw4dzNg"
SELFTEST_WIF_UNCOMPRESSED = "5KfNkSeQwNgjHr7cRErzDmq5XdUm8qc94YM3iEN5YaMYoA2UGky"
SELFTEST_WIF_COMPRESSED = "L5NNzkC8eziMfMnBKzBdZNsCzC1XobY6adMUxyz34NDhLNHr96MK"


def _h160(pub: bytes) -> bytes:
    return hashlib.new("ripemd160", hashlib.sha256(pub).digest()).digest()


def _p2pkh(pub: bytes) -> str:
    return base58.b58encode_check(b"\x00" + _h160(pub)).decode()


def priv_to_addresses(priv: bytes) -> tuple[str, str] | tuple[None, None]:
    """Return (compressed_addr, uncompressed_addr) for a 32-byte private key, or (None, None)."""
    if len(priv) != 32:
        return (None, None)
    n = int.from_bytes(priv, "big")
    if n == 0 or n >= ecdsa.SECP256k1.order:
        return (None, None)
    vk = ecdsa.SigningKey.from_string(priv, curve=ecdsa.SECP256k1).get_verifying_key()
    xy = vk.to_string()
    x, y = xy[:32], xy[32:]
    uncompressed = _p2pkh(b"\x04" + xy)
    compressed_prefix = b"\x03" if y[-1] & 1 else b"\x02"
    compressed = _p2pkh(compressed_prefix + x)
    return compressed, uncompressed


def decode_candidate(candidate: str) -> bytes | None:
    """Accept 64 hex chars, or a base58check WIF (with or without compression flag)."""
    candidate = candidate.strip()
    if len(candidate) == 64:
        try:
            return bytes.fromhex(candidate)
        except ValueError:
            return None
    try:
        raw = base58.b58decode_check(candidate)
    except ValueError:
        return None
    if len(raw) == 33 and raw[0] == 0x80:
        return raw[1:]
    if len(raw) == 34 and raw[0] == 0x80 and raw[-1] == 0x01:
        return raw[1:-1]
    return None


def check(candidate: str) -> tuple[bool, str | None, str | None]:
    priv = decode_candidate(candidate)
    if priv is None:
        return False, None, None
    compressed, uncompressed = priv_to_addresses(priv)
    if compressed is None:
        return False, None, None
    if compressed == TARGET_ADDRESS:
        return True, compressed, "compressed"
    if uncompressed == TARGET_ADDRESS:
        return True, uncompressed, "uncompressed"
    return False, None, None


def selftest() -> bool:
    ok = True

    priv = bytes.fromhex(SELFTEST_PRIV_HEX)
    compressed, uncompressed = priv_to_addresses(priv)
    found_u = uncompressed == SELFTEST_UNCOMPRESSED_ADDRESS
    print(f"hex vector -> uncompressed {SELFTEST_UNCOMPRESSED_ADDRESS}: {'OK' if found_u else 'FAIL'}")
    ok = ok and found_u
    found_c = compressed == SELFTEST_COMPRESSED_ADDRESS
    print(f"hex vector -> compressed {SELFTEST_COMPRESSED_ADDRESS}: {'OK' if found_c else 'FAIL'}")
    ok = ok and found_c

    priv_from_wif_u = decode_candidate(SELFTEST_WIF_UNCOMPRESSED)
    found_wu = priv_from_wif_u == priv
    print(f"WIF uncompressed decode -> same private key: {'OK' if found_wu else 'FAIL'}")
    ok = ok and found_wu

    priv_from_wif_c = decode_candidate(SELFTEST_WIF_COMPRESSED)
    found_wc = priv_from_wif_c == priv
    print(f"WIF compressed decode -> same private key: {'OK' if found_wc else 'FAIL'}")
    ok = ok and found_wc

    matched, addr, form = check(SELFTEST_PRIV_HEX)
    clean = not matched
    print(f"negative control (public vector vs COG's escrow) -> no match: {'OK' if clean else 'FAIL'}")
    ok = ok and clean

    if ok:
        print("SELFTEST OK")
    return ok


def _print_result(candidate: str) -> bool:
    matched, addr, form = check(candidate)
    if matched:
        print(f"MATCH {addr} ({form})")
    else:
        print("NO MATCH")
    return matched


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", nargs="?", help="64 hex chars, or a WIF string")
    parser.add_argument("--stdin", action="store_true", help="read candidates, one per line")
    parser.add_argument("--selftest", action="store_true", help="run the certification vector")
    args = parser.parse_args()

    if args.selftest:
        return 0 if selftest() else 1

    if args.stdin:
        any_hit = False
        for line in sys.stdin:
            line = line.strip()
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
