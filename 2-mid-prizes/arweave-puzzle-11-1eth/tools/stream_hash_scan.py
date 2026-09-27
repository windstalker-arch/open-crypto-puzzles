#!/usr/bin/env python3
"""Hash-family scan of extracted bit streams for Arweave Puzzle #11.

The prior raw-pixel hashes hashed byte/floating arrays, not the LSB-extracted
bit streams. Here we hash each extracted bitstream (per channel, plane, width,
read-order) as a whole and as a 32-byte prefix, via SHA-256 / double-SHA-256 /
Keccak-256 / BLAKE2s, and derive the ETH address of every 256-bit hash output.
"""
import importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import plane_window_scan as p  # noqa
import hashlib
from eth_keys import keys
from Crypto.Hash import keccak

TARGET = "0xff2142e98e09b5344994f9beb9c56c95506b9f17"
PREFIX = TARGET[2:6]
SCALAR = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

KEYS = {b"GRAY": p.G.flatten(), b"ALPHA": p.A.flatten()}
HASHERS = ["sha256", "sha256d", "keccak256", "blake2s"]


def kh(data, mode):
    if mode == "sha256":
        return hashlib.sha256(data).digest()
    if mode == "sha256d":
        return hashlib.sha256(hashlib.sha256(data).digest()).digest()
    if mode == "keccak256":
        k = keccak.new(digest_bits=256)
        k.update(data)
        return k.digest()
    if mode == "blake2s":
        return hashlib.blake2s(data).digest()


def check(digest, label):
    if len(digest) < 32:
        return
    pv = int.from_bytes(digest, "big")
    if pv == 0 or pv >= SCALAR:
        return
    a = keys.PrivateKey(digest).public_key.to_checksum_address().lower()
    if a == TARGET or a.startswith("0x" + PREFIX):
        print(f"RESULT {label} {a} {digest.hex()}", flush=True)


def main():
    total = 0
    for chname, flat in KEYS.items():
        for plane in range(8):
            data = p.make_stream(flat, plane, 1, False)
            for mode in HASHERS:
                total += 1
                check(kh(data, mode), f"{chname} p{plane} bw1 {mode}")
        for bw in (2, 4, 8):
            for lsbf in (False, True):
                data = p.make_stream(flat, 0, bw, lsbf)
                for mode in HASHERS:
                    total += 1
                    check(kh(data, mode), f"{chname} p0 bw{bw} lsbf{int(lsbf)} {mode}")
                # also the raw first 32 bytes as the key
                pv = int.from_bytes(data[:32], "big")
                if 0 < pv < SCALAR:
                    total += 1
                    check(data[:32], f"{chname} p0 bw{bw} lsbf{int(lsbf)} rawprefix")
    print(f"hash-consumed {total} candidates; final check done", flush=True)


if __name__ == "__main__":
    main()
