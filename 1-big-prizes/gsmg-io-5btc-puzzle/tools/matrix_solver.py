#!/usr/bin/env python3
"""matrix_solver.py -- true linear-system solving over the GSMG final-page digit streams.

matrixsumlist was previously tested only as sums->characters. This tool implements the
untested reading: treat the reshaped a..i / B..E / 23-letter streams as DENSE matrices and
SOLVE linear systems (modular Gaussian elimination over GF(p), plus rational Gaussian over
Q) whose RHS are the exact row-sum and column-sum LISTS of the matrix ("list of sums").
Each solution vector x is canonicalised to candidate answer-X strings (letters mod 26,
alphanumeric mod 36, bytes mod 256, joined digits) for the final-gate oracles.

Reproducible, deterministic. No randomness.
"""
import os
import json
import sys
from fractions import Fraction
from pathlib import Path

BASE = os.path.expanduser("~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle")
FF = json.loads(Path(f"{BASE}/data/finalpage-digit-streams.json").read_text())
SF = json.loads(Path(f"{BASE}/data/salphaseion-streams.json").read_text())

FAED = FF["faed_570"].rstrip("z")
DBBIB = FF["dbbib_91"]   # authoritative; FF["dbbib"] is the crop
EVEN = SF["even_stream"]
ODD = SF["odd_pre_reduction"]
OBJ = SF["object_256"]
Z1 = FF["z_segment_1"]
Z2 = FF["z_segment_2"]

READINGS = {}


def mapstream(s, mapping):
    return [mapping[c] for c in s]


def reshape(vals, rows, cols):
    return [vals[r * cols:(r + 1) * cols] for r in range(rows)]


def matmul(A, B):
    r, mid = len(A), len(B)
    if B and not isinstance(B[0], list):
        return [sum(A[i][k] * B[k] for k in range(mid)) for i in range(r)]
    c = len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(mid)) for j in range(c)] for i in range(r)]


def trans(A):
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]


def rowsum(M, p=None):
    return [sum(row) for row in M]


def colsum(M, p=None):
    c = len(M[0])
    return [sum(M[i][j] for i in range(len(M))) for j in range(c)]


def first_block(vals, rows, cols, n):
    A = reshape(vals, rows, cols)
    sq = [A[i][:n] for i in range(n)]
    return sq, A


def egcd_inv(a, p):
    a %= p
    if a == 0:
        return None
    g, x, y = p, 0, 1
    aa, bb = a, p
    x0, x1 = 1, 0
    while bb:
        q = aa // bb
        aa, bb = bb, aa - q * bb
        x0, x1 = x1, x0 - q * x1
    if aa != 1:
        return None
    return x0 % p


def gauss_mod(M, b, p):
    n = len(M)
    aug = [list(M[i]) + [b[i] % p] for i in range(n)]
    for col in range(n):
        piv = next((r for r in range(col, n) if aug[r][col] % p != 0), None)
        if piv is None:
            return None
        aug[col], aug[piv] = aug[piv], aug[col]
        inv = egcd_inv(aug[col][col], p)
        if inv is None:
            return None
        aug[col] = [(v % p) * inv % p for v in aug[col]]
        for r in range(n):
            if r != col and aug[r][col] % p != 0:
                f = aug[r][col] % p
                aug[r] = [(aug[r][k] - f * aug[col][k]) % p for k in range(n + 1)]
    return [aug[i][n] % p for i in range(n)]


def gauss_frac(M, b):
    n = len(M)
    aug = [[Fraction(M[i][j]) for j in range(n)] + [Fraction(b[i])] for i in range(n)]
    for col in range(n):
        piv = next((r for r in range(col, n) if aug[r][col] != 0), None)
        if piv is None:
            return None
        aug[col], aug[piv] = aug[piv], aug[col]
        inv = 1 / aug[col][col]
        aug[col] = [v * inv for v in aug[col]]
        for r in range(n):
            if r != col and aug[r][col] != 0:
                f = aug[r][col]
                aug[r] = [aug[r][k] - f * aug[col][k] for k in range(n + 1)]
    x = [aug[i][n] for i in range(n)]
    if any(t.denominator not in (1, 2, 4, 8, 16) and t.denominator > 256 for t in x):
        return None
    return x


def canonical(x):
    out = set()
    letters = "".join(chr(65 + (int(xi) % 26)) for xi in x)
    alpha36 = "".join("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[int(xi) % 36] for xi in x)
    digits = "".join(str(int(xi)) for xi in x)
    out.add(("LE26", letters))
    out.add(("AL36", alpha36))
    out.add(("DIGIT", digits))
    byt = bytes((int(xi) % 256) & 0xFF for xi in x)
    if all(32 <= c < 127 for c in byt):
        out.add(("BYTXT", byt.decode("latin1")))
    yield from sorted(out)


def solve_all(name, values, rows, cols, mods, idx_map_name=None):
    if idx_map_name == "faed0":
        m = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7, "i": 8}
    elif idx_map_name == "faed1":
        m = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9}
    vals = mapstream(values, m) if idx_map_name else list(values)
    if len(vals) < rows * cols:
        return
    A = reshape(vals[:rows * cols], rows, cols)
    sq = [A[i][:rows] for i in range(rows)] if cols >= rows else None
    AA = matmul(A, trans(A))
    rs = rowsum(A)
    cs = colsum(A)
    systems = {}
    if sq is not None:
        systems["sqxRS"] = (sq, rs[:rows])
        systems["sqxCS"] = (sq, cs[:rows])
    if len(cs) == rows:
        systems["AsqxCS"] = (AA, cs)
    systems["AAt_y"] = (AA, matmul(A, cs))
    for sname, (M, b) in systems.items():
        for p in mods:
            x = gauss_mod(M, b, p)
            if x is None:
                continue
            for cname, cand in canonical(x):
                READINGS[(name, sname, f"mod{p}", cname)] = cand
    if sq is not None:
        x = gauss_frac(sq, rs[:rows])
        if x is not None:
            for cname, cand in canonical(x):
                READINGS[(name, "sqxRS", "fracQ", cname)] = cand


def main():
    sys.setrecursionlimit(10000)
    solve_all("FAED_r0_19x30", FAED, 19, 30, [29, 13, 26], idx_map_name="faed0")
    solve_all("FAED_r1_19x30", FAED, 19, 30, [29], idx_map_name="faed1")
    solve_all("FAED_r0_15x38", FAED, 15, 38, [29], idx_map_name="faed0")
    solve_all("FAED_r0_15x38r", FAED, 38, 15, [29], idx_map_name="faed0")
    solve_all("DBBIB_r0_3x23", DBBIB, 3, 23, [29, 23], idx_map_name="faed0")
    solve_all("DBBIB_r1_3x23", DBBIB, 3, 23, [29], idx_map_name="faed1")
    evmap = {k: i for i, k in enumerate(sorted(set(EVEN)))}
    solve_all("EVEN_r0_15x19", [evmap[c] for c in EVEN], 15, 19, [29])
    oddmap = {k: i for i, k in enumerate(sorted(set(ODD)))}
    solve_all("ODD_r0_15x19", [oddmap[c] for c in ODD], 15, 19, [29])
    objs = {c: i for i, c in enumerate(sorted(set(OBJ)))}
    solve_all("OBJ256_r0_16x16", [objs[c] for c in OBJ], 16, 16, [23, 29])
    z1m = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7, "i": 8, "o": 9}
    solve_all("Z1_r0_7x9", [z1m[c] for c in Z1], 7, 9, [29, 19])
    z2m = {"a": 0, "b": 1, "c": 2, "d": 3, "f": 4, "g": 5, "h": 6, "i": 7, "o": 8}
    solve_all("Z2_r0_1x29", [z2m[c] for c in Z2], 1, 29, [])

    rows = sorted(READINGS)
    for k in rows:
        print(f"{'|'.join(k)} :: {READINGS[k]}")
    out = [READINGS[k] for k in rows]
    uniq = sorted(set(out))
    print(f"\nTOTAL {len(out)} readings, {len(uniq)} unique candidates", file=sys.stderr)
    for c in uniq:
        print(c)


if __name__ == "__main__":
    main()