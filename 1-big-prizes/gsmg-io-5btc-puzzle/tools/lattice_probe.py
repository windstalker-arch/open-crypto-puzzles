#!/usr/bin/env python3
"""lattice_probe.py -- read-only latent-structure survey of the GSMG artifacts.

Datasets probed:
  - dbbib(69) / faed(570) 9-symbol streams under three value encodings
  - white-rabbit 14x14 colored cells (15 blue + 9 yellow -> 24-bit key)
  - canonical matrix-sumlist RS/CS (14 rows/cols sums)
  - certified salphaseion artifacts (even_stream 285, object_256 256)

Checks: factor-pair reshapes + rank/det/gcd/singular spectrum; low-rank
signature; Berlekamp-Massey linear recurrence over GF(p); autocorrelation /
rotation period; prefix-sum reduction; convex/linear structure of the rabbit
cells; kernel relations of RS/CS over small moduli.

Output is informational only (no oracle feeds).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.loads(Path(os.path.join(BASE, "data",
                                   "finalpage-digit-streams.json")).read_text())
RABBIT = json.loads(Path(os.path.join(BASE, "data",
                                     "follow-white-rabbit-grid.json")).read_text())
SALP = json.loads(Path(os.path.join(BASE, "data", "salphaseion-streams.json")).read_text())

DBBIB = DATA["dbbib_91"].lower()   # authoritative; DATA["dbbib"] is the crop
FAED = DATA["faed_570"].rstrip("z").lower()
CANON = {"a": 8, "b": 1, "c": 5, "d": 0, "e": 6, "f": 3, "g": 7, "h": 4, "i": 2}


def enc(stream: str, kind: str):
    if kind == "v0":
        return [ord(c) - 97 for c in stream]
    if kind == "v1":
        return [ord(c) - 96 for c in stream]
    return [CANON[c] for c in stream]


def factors(n: int):
    out = []
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            out.append((d, n // d))
    return out


def report(name: str, rows: int, cols: int, m: np.ndarray):
    g = int(np.gcd.reduce(m.ravel())) if m.size else 0
    print(f"  [{name}] {rows}x{cols} gcd={g} "
          f"rank={int(np.linalg.matrix_rank(m))} "
          f"rsums=({','.join(str(int(x)) for x in m.sum(1))[:60]}...) "
          f"csums=({','.join(str(int(x)) for x in m.sum(0))[:60]}...)")


def probe_linear_recurrence(seq, p, name):
    n = len(seq)
    s = [x % p for x in seq]
    # Berlekamp-Massey
    C, B = [1], [1]
    L, m, b = 0, 1, 1
    for nn in range(n):
        d = s[nn]
        for i in range(1, L + 1):
            d = (d + C[i] * s[nn - i]) % p
        if d == 0:
            m += 1
            continue
        T = C[:]
        coef = d * pow(b, -1, p) % p
        if len(C) < len(B) + m:
            C += [0] * (len(B) + m - len(C))
        for j in range(len(B)):
            C[j + m] = (C[j + m] - coef * B[j]) % p
        if 2 * L <= nn:
            L = nn + 1 - L
            B, b, m = T, d, 1
        else:
            m += 1
    print(f"    {name}: GF({p}) linear complexity = {L} "
          f"(poly len {len(C) - 1})", end="")
    picks = (1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)
    print("  period(j):", end=" ")
    for j in picks:
        if j <= n // 2 and s[:n - j] == s[j:]:
            print(f"{j}", end=" ")
    print()


def probe_rotation(seq, name):
    n = len(seq)
    for j in range(1, n // 2 + 1):
        if n % j == 0 and seq[: n - j] == seq[j:]:
            print(f"    {name}: rotation period/in-block repeat {j}")
            return
    print(f"    {name}: no rotation period < n/2")


def control_checks() -> None:
    """Known-structured sequences: prove the fingerprints can fire."""
    import itertools
    print("\n=== E. probe control: known-structured sequences ===")
    cyclic = list(itertools.islice(itertools.cycle([0, 1, 2, 3, 4, 5, 6, 7, 8]),
                                   69))
    slope = list(range(69))
    print(f"  cycle a..i x69: sum={sum(cyclic)} "
          f"period(9)={cyclic[:60] == cyclic[9:69]}")
    print("    cyclic GF(2) complexity below:")
    probe_linear_recurrence(cyclic, 2, "cycle")
    probe_linear_recurrence(slope, 13, "ramp")
    m = np.array(cyclic).reshape(3, 23)
    print(f"  cycle reshaped 3x23 rank={int(np.linalg.matrix_rank(m))} "
          f"(rank-deficient expected)")
    m2 = np.array(slope).reshape(3, 23)
    print(f"  ramp reshaped 3x23 rank={int(np.linalg.matrix_rank(m2))} "
          f"(rank-deficient expected)")


def main() -> int:
    print("=== A. streams: values / reshapes / recurrences ===")
    for label, st in (("dbbib", DBBIB), ("faed", FAED)):
        for kind in ("v0", "v1", "canon"):
            v = enc(st, kind)
            print(f"  {label}/{kind}: n={len(st)} "
                  f"sum={sum(v)} gcd={int(np.gcd.reduce(v))} "
                  f"unique={sorted(set(v))}")
            if len(st) == 69 or len(st) == 570:
                for r, c in factors(len(st)):
                    m = np.array(v).reshape(r, c)
                    report(f"{label}/{kind}", r, c, m)
        v0 = enc(st, "v0")
        probe_linear_recurrence(v0, 13, f"{label}")
        probe_linear_recurrence(v0, 3, f"{label}")
        probe_linear_recurrence(v0, 2, f"{label}")
        if label == "dbbib":
            probe_rotation(v0, label)

    print("\n=== B. white-rabbit 14x14 colored cells ===")
    blue, yellow = RABBIT["blue"], RABBIT["yellow"]
    bits = np.zeros((14, 14), dtype=int)
    for r, c in blue:
        bits[r, c] = 0
    for r, c in yellow:
        bits[r, c] = 1
    print(f"  blue={len(blue)} yellow={len(yellow)} "
          f"rowsums={bits.sum(1).tolist()} colsums={bits.sum(0).tolist()}")
    by_row = sorted([(r, c, 1 if (r, c) in [tuple(y) for y in yellow] else 0)
                     for r, c in blue + yellow])
    dr = [by_row[i + 1][0] - by_row[i][0] for i in range(len(by_row) - 1)]
    dc = [by_row[i + 1][1] - by_row[i][1] for i in range(len(by_row) - 1)]
    print(f"  row-major deltas dr={dr}")
    print(f"  row-major deltas dc={dc}")
    print(f"  gcd(dr)={int(np.gcd.reduce(dr))} gcd(dc)={int(np.gcd.reduce(dc))}")
    # collinearity of blue cells
    bl = sorted(blue)
    slopes = []
    for i in range(len(bl) - 1):
        r1, c1 = bl[i]
        r2, c2 = bl[i + 1]
        drv, dcv = r2 - r1, c2 - c1
        import math
        g = math.gcd(drv, dcv)
        if g:
            slopes.append((drv // g, dcv // g))
    print(f"  consecutive-blue slopes: {slopes}")
    # read 24-bit key as established: one-positions = yellow sorted (0-based)
    pos = [r * 14 + c for r, c in sorted(yellow)]
    key = sum(1 << p for p in pos)
    print(f"  yellow row-major positions -> this reading: bits {sorted(pos)} "
          f"= 0x{key:X}")

    print("\n=== C. matrix-sumlist RS/CS ===")
    RS = [7, 6, 5, 5, 5, 5, 3, 8, 7, 6, 7, 6, 6, 0]
    CS = [7, 8, 4, 8, 7, 5, 5, 5, 5, 5, 6, 5, 6, 0]
    print(f"  RS={RS}; CS={CS}")
    print(f"  RS diffs={[RS[i+1]-RS[i] for i in range(13)]}")
    print(f"  CS diffs={[CS[i+1]-CS[i] for i in range(13)]}")
    print(f"  RS+CS={[RS[i]+CS[i] for i in range(14)]}")
    print(f"  RS-CS={[RS[i]-CS[i] for i in range(14)]}")
    for mod in (2, 3, 5, 9, 13):
        rel = [(RS[i] + RS[i + 1]) % mod for i in range(13)]
        print(f"    mod{mod}: RS[i]+RS[i+1] = {rel}")
    # small integer kernel of [RS ; CS] over small moduli
    for mod in (2, 3, 5, 7, 9, 13):
        a = np.array([[RS[i], CS[i]] for i in range(14)]) % mod
        rank = int(np.linalg.matrix_rank(a))
        print(f"    mod{mod}: rank of 14x2 [RS,CS] matrix = {rank}")

    print("\n=== D. certified artifacts ===")
    for kind, s in (("even_stream", SALP["even_stream"]),
                    ("object_256", SALP["object_256"]),
                    ("odd_pre_reduction", SALP["odd_pre_reduction"])):
        v = [ord(c) - 65 for c in s]
        print(f"  {kind}: n={len(s)} sum={sum(v)} "
              f"gcd={int(np.gcd.reduce(v))}")
        probe_linear_recurrence(v, 13, kind)
        for r, c in factors(len(s)):
            m = np.array(v).reshape(r, c)
            report(kind, r, c, m)
    control_checks()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())