#!/usr/bin/env python3
"""
shamir_combine.py -- reconstruct a split material blendally, byte-field (GF(2^8)),
prime-field (GF(p)), or plain XOR, for the GSMG.io "Just Half" / "Better Half" split
hypotheses.

Purpose:
    The puzzle keeps publishing key material in mechanical halves ("Just Half",
    "Better Half", the 36 x 32-byte mystery blocks, the two halves that per the
    briefing were already NOT converted by a Shamir GF(256) or a mod-256 read of
    the mystery blocks). If a pair of bytes ever IS a Shamir split under the
    byte-field that the mainstream libraries (hashicorp/vault, privy-io
    shamir-secret-sharing) use, or a big-integer split over a prime (e.g. the
    secp256k1 group order N, or some other mod p), this tool reconstructs the
    secret. It handles all three layouts:

      GF(2^8)   layout {y1..yN, x}, x byte LAST, x any byte distinct per share.
                Tables and arithmetic are a verbatim Python port of
                hashicorp/vault/shamir (samiam.org tables, generator 0xe5),
                which privy-io's shamir-secret-sharing replicates byte-for-byte,
                so shares from either library combine here.
      GF(p)     shares as (x, y) big-integers; Lagrange interpolation at x=0
                recovers the integer secret mod p (default p = secp256k1 order N).
      XOR       ALL shares XOR to the secret (a k-of-k one-time pad: for 2 halves,
                secret = h1 XOR h2).

Usage:
    python3 tools/shamir_combine.py --selftest
    python3 tools/shamir_combine.py gf256 --share <hex> --share <hex> [...]
    python3 tools/shamir_combine.py gfp --prime <hex> --share <x>:<hex> --share <x>:<hex> [...]
    python3 tools/shamir_combine.py xor   --share <hex> --share <hex> [...]

Output:
    The reconstructed secret as hex (and utf-8-decodable text when it is plaintext).
    Exit 0 on success.

Certified against:
    --selftest recombines four REAL share files that were produced by two OTHER
    libraries -- hashicorp/vault (Go) and privy-io shamir-secret-sharing (TS) --
    from the same secret b"cross-check-secret"; both pairs must re-decrypt here.
    GF(p) and XOR are certified by fixed deterministic vectors plus a round trip.

Dependencies: stdlib only.
"""

from __future__ import annotations

import argparse
import secrets
import sys

# --- GF(2^8): verbatim port of hashicorp/vault/shamir tables.go (samiam.org,
# generator 0xe5). These are NOT produced by one liner loop; they must match the
# Go byte-for-byte or every combine here is garbage.
LOG_TABLE = [
    0x00, 0xff, 0xc8, 0x08, 0x91, 0x10, 0xd0, 0x36,
    0x5a, 0x3e, 0xd8, 0x43, 0x99, 0x77, 0xfe, 0x18,
    0x23, 0x20, 0x07, 0x70, 0xa1, 0x6c, 0x0c, 0x7f,
    0x62, 0x8b, 0x40, 0x46, 0xc7, 0x4b, 0xe0, 0x0e,
    0xeb, 0x16, 0xe8, 0xad, 0xcf, 0xcd, 0x39, 0x53,
    0x6a, 0x27, 0x35, 0x93, 0xd4, 0x4e, 0x48, 0xc3,
    0x2b, 0x79, 0x54, 0x28, 0x09, 0x78, 0x0f, 0x21,
    0x90, 0x87, 0x14, 0x2a, 0xa9, 0x9c, 0xd6, 0x74,
    0xb4, 0x7c, 0xde, 0xed, 0xb1, 0x86, 0x76, 0xa4,
    0x98, 0xe2, 0x96, 0x8f, 0x02, 0x32, 0x1c, 0xc1,
    0x33, 0xee, 0xef, 0x81, 0xfd, 0x30, 0x5c, 0x13,
    0x9d, 0x29, 0x17, 0xc4, 0x11, 0x44, 0x8c, 0x80,
    0xf3, 0x73, 0x42, 0x1e, 0x1d, 0xb5, 0xf0, 0x12,
    0xd1, 0x5b, 0x41, 0xa2, 0xd7, 0x2c, 0xe9, 0xd5,
    0x59, 0xcb, 0x50, 0xa8, 0xdc, 0xfc, 0xf2, 0x56,
    0x72, 0xa6, 0x65, 0x2f, 0x9f, 0x9b, 0x3d, 0xba,
    0x7d, 0xc2, 0x45, 0x82, 0xa7, 0x57, 0xb6, 0xa3,
    0x7a, 0x75, 0x4f, 0xae, 0x3f, 0x37, 0x6d, 0x47,
    0x61, 0xbe, 0xab, 0xd3, 0x5f, 0xb0, 0x58, 0xaf,
    0xca, 0x5e, 0xfa, 0x85, 0xe4, 0x4d, 0x8a, 0x05,
    0xfb, 0x60, 0xb7, 0x7b, 0xb8, 0x26, 0x4a, 0x67,
    0xc6, 0x1a, 0xf8, 0x69, 0x25, 0xb3, 0xdb, 0xbd,
    0x66, 0xdd, 0xf1, 0xd2, 0xdf, 0x03, 0x8d, 0x34,
    0xd9, 0x92, 0x0d, 0x63, 0x55, 0xaa, 0x49, 0xec,
    0xbc, 0x95, 0x3c, 0x84, 0x0b, 0xf5, 0xe6, 0xe7,
    0xe5, 0xac, 0x7e, 0x6e, 0xb9, 0xf9, 0xda, 0x8e,
    0x9a, 0xc9, 0x24, 0xe1, 0x0a, 0x15, 0x6b, 0x3a,
    0xa0, 0x51, 0xf4, 0xea, 0xb2, 0x97, 0x9e, 0x5d,
    0x22, 0x88, 0x94, 0xce, 0x19, 0x01, 0x71, 0x4c,
    0xa5, 0xe3, 0xc5, 0x31, 0xbb, 0xcc, 0x1f, 0x2d,
    0x3b, 0x52, 0x6f, 0xf6, 0x2e, 0x89, 0xf7, 0xc0,
    0x68, 0x1b, 0x64, 0x04, 0x06, 0xbf, 0x83, 0x38,
]

EXP_TABLE = [
    0x01, 0xe5, 0x4c, 0xb5, 0xfb, 0x9f, 0xfc, 0x12,
    0x03, 0x34, 0xd4, 0xc4, 0x16, 0xba, 0x1f, 0x36,
    0x05, 0x5c, 0x67, 0x57, 0x3a, 0xd5, 0x21, 0x5a,
    0x0f, 0xe4, 0xa9, 0xf9, 0x4e, 0x64, 0x63, 0xee,
    0x11, 0x37, 0xe0, 0x10, 0xd2, 0xac, 0xa5, 0x29,
    0x33, 0x59, 0x3b, 0x30, 0x6d, 0xef, 0xf4, 0x7b,
    0x55, 0xeb, 0x4d, 0x50, 0xb7, 0x2a, 0x07, 0x8d,
    0xff, 0x26, 0xd7, 0xf0, 0xc2, 0x7e, 0x09, 0x8c,
    0x1a, 0x6a, 0x62, 0x0b, 0x5d, 0x82, 0x1b, 0x8f,
    0x2e, 0xbe, 0xa6, 0x1d, 0xe7, 0x9d, 0x2d, 0x8a,
    0x72, 0xd9, 0xf1, 0x27, 0x32, 0xbc, 0x77, 0x85,
    0x96, 0x70, 0x08, 0x69, 0x56, 0xdf, 0x99, 0x94,
    0xa1, 0x90, 0x18, 0xbb, 0xfa, 0x7a, 0xb0, 0xa7,
    0xf8, 0xab, 0x28, 0xd6, 0x15, 0x8e, 0xcb, 0xf2,
    0x13, 0xe6, 0x78, 0x61, 0x3f, 0x89, 0x46, 0x0d,
    0x35, 0x31, 0x88, 0xa3, 0x41, 0x80, 0xca, 0x17,
    0x5f, 0x53, 0x83, 0xfe, 0xc3, 0x9b, 0x45, 0x39,
    0xe1, 0xf5, 0x9e, 0x19, 0x5e, 0xb6, 0xcf, 0x4b,
    0x38, 0x04, 0xb9, 0x2b, 0xe2, 0xc1, 0x4a, 0xdd,
    0x48, 0x0c, 0xd0, 0x7d, 0x3d, 0x58, 0xde, 0x7c,
    0xd8, 0x14, 0x6b, 0x87, 0x47, 0xe8, 0x79, 0x84,
    0x73, 0x3c, 0xbd, 0x92, 0xc9, 0x23, 0x8b, 0x97,
    0x95, 0x44, 0xdc, 0xad, 0x40, 0x65, 0x86, 0xa2,
    0xa4, 0xcc, 0x7f, 0xec, 0xc0, 0xaf, 0x91, 0xfd,
    0xf7, 0x4f, 0x81, 0x2f, 0x5b, 0xea, 0xa8, 0x1c,
    0x02, 0xd1, 0x98, 0x71, 0xed, 0x25, 0xe3, 0x24,
    0x06, 0x68, 0xb3, 0x93, 0x2c, 0x6f, 0x3e, 0x6c,
    0x0a, 0xb8, 0xce, 0xae, 0x74, 0xb1, 0x42, 0xb4,
    0x1e, 0xd3, 0x49, 0xe9, 0x9c, 0xc8, 0xc6, 0xc7,
    0x22, 0x6e, 0xdb, 0x20, 0xbf, 0x43, 0x51, 0x52,
    0x66, 0xb2, 0x76, 0x60, 0xda, 0xc5, 0xf3, 0xf6,
    0xaa, 0xcd, 0x9a, 0xa0, 0x75, 0x54, 0x0e, 0x01,
]

SECP256K1_ORDER = int(
    "fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141", 16
)


def _gf_mult(a, b):
    if a == 0 or b == 0:
        return 0
    return EXP_TABLE[(LOG_TABLE[a] + LOG_TABLE[b]) % 255]


def _gf_div(a, b):
    if b == 0:
        raise ValueError("divide by zero in GF(2^8)")
    if a == 0:
        return 0
    return EXP_TABLE[(int(LOG_TABLE[a]) - int(LOG_TABLE[b]) + 255) % 255]


def _gf_add(a, b):
    return a ^ b


def _gf_interpolate_0(x_samples, y_samples):
    limit = len(x_samples)
    result = 0
    for i in range(limit):
        basis = 1
        for j in range(limit):
            if i == j:
                continue
            num = _gf_add(0, x_samples[j])
            denom = _gf_add(x_samples[i], x_samples[j])
            basis = _gf_mult(basis, _gf_div(num, denom))
        result = _gf_add(result, _gf_mult(y_samples[i], basis))
    return result


def combine_gf256(shares_hex):
    """shares_hex: list of hex strings, layout {y1..yN, x}, x byte LAST."""
    shares = [bytes.fromhex(s) for s in shares_hex]
    first_len = len(shares[0])
    if first_len < 2:
        raise ValueError("shares must be at least two bytes")
    for s in shares[1:]:
        if len(s) != first_len:
            raise ValueError("all shares must be the same length")
    xs = [s[first_len - 1] for s in shares]
    if len(set(xs)) != len(xs):
        raise ValueError("duplicate x coordinate in shares")
    secret = bytearray(first_len - 1)
    for idx in range(first_len - 1):
        ys = [s[idx] for s in shares]
        secret[idx] = _gf_interpolate_0(xs, ys)
    return bytes(secret)


def combine_gfp(pairs, prime):
    """pairs: list of (x:int, y:int); recovers f(0) mod prime via Lagrange."""
    xs = [x for x, _ in pairs]
    ys = [y for _, y in pairs]
    if len(set(xs)) != len(xs):
        raise ValueError("duplicate x coordinate")
    result = 0
    for i in range(len(pairs)):
        li = 1
        for j in range(len(pairs)):
            if i == j:
                continue
            num = (-xs[j]) % prime
            denom = (xs[i] - xs[j]) % prime
            li = li * num % prime * pow(denom, prime - 2, prime) % prime
        result = (result + ys[i] * li) % prime
    return result


def combine_xor(shares_hex):
    blobs = [bytes.fromhex(s) for s in shares_hex]
    first = len(blobs[0])
    if first == 0:
        raise ValueError("empty share")
    for b in blobs[1:]:
        if len(b) != first:
            raise ValueError("all shares must be the same length")
    out = bytearray(first)
    for b in blobs:
        for i in range(first):
            out[i] ^= b[i]
    return bytes(out)


def _render(secret_bytes):
    low = str(secret_bytes)[:200]
    text = ""
    try:
        text = secret_bytes.decode("ascii")
        if any(ch < " " for ch in text) and "\n" not in text and "\r" not in text:
            text = ""
    except (UnicodeDecodeError, AttributeError):
        text = ""
    return low


def _check(cond, label):
    print(f"{label}: {'OK' if cond else 'FAIL'}")
    return cond


def selftest():
    ok = True
    # Cross-library vectors: real shares produced on this device by hashicorp/vault
    # (Go, gotest.go split, b"cross-check-secret", 3 parts, threshold 2) and by
    # privy-io/shamir-secret-sharing (TS). Independent of this script's own split.
    vault_s0 = "817f222249d5c9f64beb429a01f7fb24cf3091"
    vault_s2 = "ebad605fbe00217b91c2d1847461f61027a947"
    privy_s0 = "b105537175de0c212e5ebac89bace1642a4e43"
    privy_s1 = "bfee90f6e7b6998e0653fd66c495f0a2171f41"
    secret = b"cross-check-secret"

    a = combine_gf256([vault_s0, vault_s2])
    ok &= _check(a == secret, "gf256: vault(go) shares -> b'cross-check-secret'")

    b = combine_gf256([vault_s0, vault_s2])
    print(f"gf256: vault share pair re-decrypt = {a!r}")
    print(f"gf256: privy share pair re-decrypt = {combine_gf256([privy_s0, privy_s1])!r}")
    ok &= _check(combine_gf256([privy_s0, privy_s1]) == secret,
                 "gf256: privy(ts) shares -> b'cross-check-secret'")

    # GF(p) -- deterministic vector: f(x) = 123 + 7x mod secp256k1 order,
    # f(1)=130, f(2)=137. Lagrange at 0 must re-return 123.
    n = SECP256K1_ORDER
    got = combine_gfp([(1, 130), (2, 137)], n)
    ok &= _check(got == 123, "gfp: deterministic poly f(x)=123+7x -> 123")
    print(f"gfp: poly interpolate -> {got}")

    # GF(p) round trip on a real 32-byte scalar (own split).
    key = 0x48cc46e66bdd36b09ae344552f606a761f9d90681f20dfefe2b43db18b623971
    xs = [11, 29, 71]
    ys = [(key + 7 * x) % n for x in xs]
    got2 = combine_gfp(list(zip(xs, ys)), n)
    ok &= _check(got2 == key, "gfp: degree-1 round trip through 2 shares -> key")
    xs3 = [11, 29, 71, 131]
    a1 = 5 * key % n
    a2 = 3 * key % n
    def _poly(x):
        return (key + a1 * x + a2 * x * x) % n
    got3 = combine_gfp([(x, _poly(x)) for x in xs3[:3]], n)
    ok &= _check(got3 == key, "gfp: degree-2 (3 of 4 shares) round trip -> key")

    # XOR -- deterministic vector, then a random pad.
    import hashlib
    pad = bytes.fromhex("deadbeef00cafe00")
    fixed = bytes.fromhex("47534d4700000000")
    ok &= _check(combine_xor([pad.hex(), fixed.hex()]) == (
        bytes([a ^ b for a, b in zip(pad, fixed)])), "xor: fixed vector")
    s = b"gsmg"
    pad2 = secrets.token_bytes(len(s))
    c = bytes([x ^ y for x, y in zip(s, pad2)])
    ok &= _check(combine_xor([pad2.hex(), c.hex()]) == s, "xor: random 2-of-2 round trip")

    if ok:
        print("SELFTEST OK")
    return ok


def _parse_share_pair(arg):
    x, _, y = arg.partition(":")
    if not _:
        raise ValueError(f"share must be <x>:<hex>, got {arg!r}")
    return int(x), int(y, 16)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", nargs="?", choices=["gf256", "gfp", "xor"],
                        help="combine mode (gf256 | gfp | xor)")
    parser.add_argument("--share", action="append", default=[],
                        help="share as hex (gf256/xor) or <x>:<hex> (gfp); repeat")
    parser.add_argument("--prime", default=None,
                        help="GF(p) modulus in hex; default secp256k1 order N")
    parser.add_argument("--selftest", action="store_true", help="run certification checks")
    args = parser.parse_args()

    if args.selftest:
        return 0 if selftest() else 1

    if args.mode == "gf256":
        out = combine_gf256(args.share)
    elif args.mode == "gfp":
        prime = int(args.prime, 16) if args.prime else SECP256K1_ORDER
        pairs = [_parse_share_pair(s) for s in args.share]
        iv = combine_gfp(pairs, prime)
        out = iv.to_bytes((iv.bit_length() + 7) // 8 or 1, "big")
    elif args.mode == "xor":
        out = combine_xor(args.share)
    else:
        parser.print_help()
        return 0

    print(f"secret hex: {out.hex()}")
    try:
        print(f"secret text: {out.decode('utf-8')}")
    except (UnicodeDecodeError, AttributeError):
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())