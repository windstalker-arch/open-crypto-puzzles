#!/usr/bin/env python3
"""
mystery_split_sweep.py -- drive the certified sealed-split reconstruction tool
(shamir_combine.py) over the 36 x 32-byte "mystery" blocks of chain3[158:1327]
and the two OP_RETURN halves, emitting oracle candidates for BOTH gate addresses.

Purpose:
    The briefing's "Shamir GF(256) recovery from mystery blocks" and
    "Shamir mod256 and Lagrange over N" negatives have NO witness in this folder
    (see Note 36 / tested.md late-36), so the three split layouts are re-swept here
    ansatz-for-ansatz with a certified tool. 2-of-2 focus: every cross pair of the
    36 blocks, under XOR / GF(2^8) / GF(p) (p = secp256k1 order N), plus the
    "Just Half" (64B) and "Better Half" (34B) OP_RETURN payloads and the 17B tail.

Layouts emitted (one oracle-candidate line per reconstruction):
  XOR       b[i] ^ b[j];  b[i] ^ b[j] ^ tail_pad32;  b[i][:17] ^ tail;  op-return halves
  GF(2^8)   share layout {y1..y30, x} with x = LAST byte; x = FIRST byte; sequential
            x = (idx+1) appended (y = full 32B, secret 32B) -- all from shamir_combine
  GF(p)     (x=last byte, y=first31), (x=first byte, y=rest31), (x=seq, y=full32 if < N)

Output:
    One candidate string per line on stdout (hex of the reconstruction, or the
    printable ASCII form when it is plain). Pipe into
    tools/oracle.py --stdin and tools/oracle_dualite.py --stdin.

Input:
    Reads ~/briefcase/CosmicDuality.txt and reproduces the 36 blocks exactly as
    chain_rebuild.py does; the three anchor checks (block[0], block[1], tail) must
    pass or the script refuses to run.

Dependencies: stdlib, pycryptodome (AES, same as chain_rebuild.py and oracle.py).
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path

from Crypto.Cipher import AES

from shamir_combine import SECP256K1_ORDER, combine_gf256, combine_gfp

XORKEY = bytes.fromhex("a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735")
DUALITE_TXT = Path.home() / "briefcase/CosmicDuality.txt"

OP_JH = bytes.fromhex(
    "0495c689eb5aef53f7fa1ef650c56eac1a0e1b590f2a82fe6ddb7484ece385b3"
    "7545eba470edae4316701263ce3abb194eca111d6107add0a30aab8bd77785f5"
)
OP_BH = bytes.fromhex("1f3afc610c1befe34300a07ec01e74c6b7f1e870dd3ff7e46e726363d0c9f1845165")


def evp(pw, salt, digest="md5"):
    H = hashlib.md5 if digest == "md5" else hashlib.sha256
    d, prev = b"", b""
    while len(d) < 48:
        prev = H(prev + pw + salt).digest()
        d += prev
    return d[:32], d[32:48]


def load_blocks():
    raw = base64.b64decode(Path(DUALITE_TXT).read_bytes().strip())
    key, iv = evp(XORKEY, raw[8:16], "md5")
    cc = AES.new(key, AES.MODE_CBC, iv).decrypt(raw[16:])
    cc = cc[:-cc[-1]]
    sha = hashlib.sha256(cc).hexdigest()
    if sha != "4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081":
        sys.exit("cc sha256 anchor mismatch: " + sha)
    if len(cc) != 1327:
        sys.exit(f"cc length {len(cc)} != 1327")
    mystery = cc[158:1327]
    blocks = [mystery[i * 32:(i + 1) * 32] for i in range(36)]
    tail = mystery[-17:]
    checks = {
        0: "e5364a3b4a0a367eedeaaee31d2672ebd4b26aa8b5181216faf62481525ddd73",
        1: "546d892449eefbd4aaf97590d075d5ad35d91c1b434b2bd6efb3c51e53023a78",
    }
    for i, want in checks.items():
        if blocks[i].hex() != want:
            sys.exit(f"anchor block[{i}] mismatch: {blocks[i].hex()}")
    if tail.hex() != "b21ed4067b11cf446d297ba3e69512343a":
        sys.exit("anchor tail mismatch")
    return blocks, tail


def xorbytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def printable(b):
    try:
        s = b.decode("ascii")
        if all(0x20 <= ord(c) < 0x7F for c in s):
            return s
    except (UnicodeDecodeError, AttributeError):
        pass
    return None


def emit(out, b):
    if not b:
        return
    out.add(b.hex())
    p = printable(b)
    if p:
        out.add(p)


def main():
    blocks, tail = load_blocks()
    out = set()
    tailpad = (tail + bytes(15))[:32]

    # ---- XOR 2-of-2: every cross pair, pair XOR tailpad, block-prefix/tail ----
    for i in range(36):
        for j in range(i + 1, 36):
            emit(out, xorbytes(blocks[i], blocks[j]))
            emit(out, xorbytes(blocks[i][:17], tail))
        emit(out, blocks[i][:17])
    for i in range(36):
        for j in range(i + 1, 36):
            x = bytes(a ^ b for a, b in zip(blocks[i], blocks[j]))
            emit(out, xorbytes(x, tailpad))

    # ---- OP_RETURN "half" pairs ----
    emit(out, xorbytes(OP_JH[:32], OP_JH[32:]))
    emit(out, xorbytes(OP_JH[:32], OP_BH))
    emit(out, xorbytes(OP_JH[32:], OP_BH))
    emit(out, xorbytes(OP_JH[:32], tailpad))
    emit(out, xorbytes(OP_JH[32:], tailpad))
    emit(out, xorbytes(OP_BH, tailpad))

    # ---- GF(2^8): last-byte x, first-byte x, sequential-x (y = full 32B) ----
    for i in range(36):
        for j in range(i + 1, 36):
            try:
                emit(out, combine_gf256([blocks[i].hex(), blocks[j].hex()]))
            except ValueError:
                pass
            # x in FIRST byte -> rotate so x is last again: share = y||x
            ri = blocks[i][1:] + blocks[i][:1]
            rj = blocks[j][1:] + blocks[j][:1]
            try:
                emit(out, combine_gf256([ri.hex(), rj.hex()]))
            except ValueError:
                pass
            # sequential x: share = 32B y, x byte appended, x = (idx+1)
            si = blocks[i] + bytes([(i + 1) & 0xFF])
            sj = blocks[j] + bytes([(j + 1) & 0xFF])
            try:
                emit(out, combine_gf256([si.hex(), sj.hex()]))
            except ValueError:
                pass

    # ---- GF(p) over secp256k1 order N ----
    for i in range(36):
        for j in range(i + 1, 36):
            def _try(pairs):
                try:
                    v = combine_gfp(pairs, SECP256K1_ORDER)
                except ValueError:
                    return
                if 0 < v < SECP256K1_ORDER:
                    emit(out, v.to_bytes(32, "big"))

            xi, xj = blocks[i][-1], blocks[j][-1]
            if xi != xj:
                _try([(xi, int.from_bytes(blocks[i][:31], "big")),
                      (xj, int.from_bytes(blocks[j][:31], "big"))])
            xi, xj = blocks[i][0], blocks[j][0]
            if xi != xj:
                _try([(xi, int.from_bytes(blocks[i][1:32], "big")),
                      (xj, int.from_bytes(blocks[j][1:32], "big"))])
            si, sj = i + 1, j + 1
            yi, yj = int.from_bytes(blocks[i], "big"), int.from_bytes(blocks[j], "big")
            if yi < SECP256K1_ORDER and yj < SECP256K1_ORDER:
                _try([(si, yi), (sj, yj)])

    for c in sorted(out):
        print(c)
    n = len(out)
    print(f"# {n} unique candidates", file=sys.stderr)


if __name__ == "__main__":
    main()