#!/usr/bin/env python3
"""matrix_neighborhood_sweep.py -- perturb the documented row/col-sum -> base-38
reduction (knightsafda #72) and check every resulting key block against the
on-chain prize pubkey 04f4d1bb... (1GSMG1JC9).

Documented (reproduces Half/BetterHalf DECOY keys):
  bits = 1327B, MSB-first, row-major, 103x103
  RS[i], CS[i] = row/col bit sums
  secondary[i] = chr((RS[i] + CS[(i+7)%103]) & 0xFF)   # must land in 80..117
  base-38 decode (digit=ord-80, big-endian) -> 68 bytes -> Half[0:32],Better[32:64]

Neighborhood: bit-order {msb,lsb} x fill {row,col} x dihedral(8)... dedup ->
matrices; op {add,xor,rs-cs,cs-rs}; shift k in 0..102; digit-base {80,79,81};
string order {fwd,rev}; key blocks {[0:32],[32:64]}. Witness: pubkey equality.
"""
import os
import sys
from pathlib import Path

from ecdsa import SECP256k1, SigningKey

KNOWN_PUB = bytes.fromhex(
    "04f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464"
    "9c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559")

data = Path(os.path.expanduser("~/cosmic_decrypted.bin")).read_bytes()
N = 103
fullbits = N*N  # 10609

def bitstream(d, lsb):
    out = []
    for b in d:
        if lsb:
            for s in range(8):
                out.append((b >> s) & 1)
        else:
            for s in range(7, -1, -1):
                out.append((b >> s) & 1)
    return out

def make_matrix(bits, colmajor=False):
    m = [[0]*N for _ in range(N)]
    for k in range(fullbits):
        i, j = (k//N, k%N) if not colmajor else (k%N, k//N)
        m[i][j] = bits[k]
    return m

def dihedral(m):
    def rotc(m):  # rotate 90 cw
        return [list(r[::-1]) for r in zip(*m)]
    out, cur = [m], m
    for _ in range(3):
        cur = rotc(cur); out.append(cur)
    fl = [r[::-1] for r in m]
    out.append(fl)
    cur = fl
    for _ in range(3):
        cur = rotc(cur); out.append(cur)
    # dedup by tuple
    seen, res = set(), []
    for mm in out:
        t = tuple(tuple(r) for r in mm)
        if t not in seen:
            seen.add(t); res.append(mm)
    return res

def sums(m):
    RS = [sum(r) for r in m]
    CS = [sum(m[i][j] for i in range(N)) for j in range(N)]
    return RS, CS

def to_68bytes(chars, base):
    v = 0
    for ch in chars:
        v = v*38 + (ord(ch) - base)
    return v.to_bytes(68, "big")

def check(keybytes, tag):
    try:
        sk = SigningKey.from_string(keybytes, curve=SECP256k1)
        pub = b"\x04" + sk.get_verifying_key().to_string()
    except Exception:
        return False
    if pub == KNOWN_PUB:
        print("*** PRIZE MATCH ***", tag, keybytes.hex())
        return True
    return False

count = 0
for lsb in (False, True):
    bits = bitstream(data, lsb)
    for colmajor in (False, True):
        m0 = make_matrix(bits, colmajor)
        for mm in dihedral(m0):
            RS, CS = sums(mm)
            for opi, op in enumerate(("add","xor","rs-cs","cs-rs")):
                for k in range(N):
                    # build char list (ord values)
                    vals = []
                    ok = True
                    for i in range(N):
                        a = RS[i]
                        b = CS[(i+k) % N]
                        if opi == 0: v = a + b
                        elif opi == 1: v = a ^ b
                        elif opi == 2: v = a - b
                        else: v = b - a
                        v &= 0xFF
                        vals.append(v)
                    # filter by any base window 80..117 / 79..116 / 81..118
                    for base in (80, 79, 81):
                        if min(vals) < base or max(vals) > base+37:
                            continue
                        s = "".join(chr(v) for v in vals)
                        for rev in (False, True):
                            chars = s[::-1] if rev else s
                            b68 = to_68bytes(chars, base)
                            for which in ("first32","mid32"):
                                kb = b68[:32] if which=="first32" else b68[32:64]
                                count += 1
                                tag = f"{op}/k{k}/b{base}/rev{int(rev)}/{which}/lsb{int(lsb)}/cm{int(colmajor)}"
                                if check(kb, tag):
                                    sys.exit(0)
print("no match; constructs checked:", count)