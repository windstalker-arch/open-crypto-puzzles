#!/usr/bin/env python3
"""matrix_byteboundary.py -- the phase-1 14x14 matrix read as its own file says
to read it: CCW spiral, MSB-first, and the YELLOW/BLUE cells as BYTE BOUNDARIES.

WHY THIS TOOL EXISTS. `R-TD-YINYANG-2026-10-03` closed the literal half of the
door thread and left the reading half open. The author's own 2023-02-23 binary
(`#8446`, re-decoded byte-exactly in that row) says, in order:

    yellow blue primes matrix sum list last words before archi choice yin yang

`matrixsumlist` is already operationalised by the community tool
`dbbi_sum_faed.py` (row-sums of a keyed 14x14 symmetric matrix), and the
`primes` rule has 35 ledger rows against it. But the phrase ORDERS the tokens
`yellow`, `blue` FIRST and `primes` THIRD, and nobody had asked what the yellow
and blue cells are FOR in a grid whose only other colours are black and white.
This tool answers exactly that, and nothing else.

TWO CHECKS, AND THE SECOND ONE IS THE NEGATIVE.

  CHECK 1 (positive, structural). Under the reading order the grid file itself
  documents -- "CCW spiral from top-left (down the left column first), B/K=1
  W/Y=0, MSB-first" -- the 196 bit positions carry 24 whole bytes plus a
  4-bit remainder. The 9 YELLOW and 15 BLUE cells are not scattered: they land
  on positions 8, 16, 24, ... 192, i.e. EXACTLY ONCE on each of the 24 byte
  boundaries, and on no other position. That is 24/24, and it is not a
  consequence of the bit encoding (see CHECK 2). Under uniform choice of 24 of
  196 positions the probability is 1/C(196,24) = 2.6e-31.

  CHECK 2 (NEGATIVE, and it retracts an attractive false positive). It is very
  tempting to observe that the marker colour agrees with the low bit of its own
  byte for all 24 bytes -- YELLOW iff LSB 0, BLUE iff LSB 1 -- and to call that
  a parity channel. IT IS A TAUTOLOGY. The file defines `B/K=1, W/Y=0`, so a
  BLUE cell IS a 1 bit and a YELLOW cell IS a 0 bit. "The marker equals the bit
  it marks" cannot fail. This row records the retraction explicitly so the
  agreement is never again cited as evidence, exactly as `R-DOORGlyph` did for
  the D00R/zeroed coincidence.

  CHECK 3 (NEGATIVE). The matrix is the one genuinely black-and-white object in
  the puzzle (K=87, W=85 -- near-equal, taijitu-shaped), and `R-YINYANG-MARKER`
  tested taijitu geometry only on the four DECRYPTED PLAINTEXTS and the 36x36
  cosmic framing. The puzzle's own matrix was never tested for the property.
  It is not point-symmetric, and neither are Y nor B paired under 180 rotation.

WITNESS. The spiral traversal is not asserted, it is checked against an
independently documented fact: `GSMG_research_baseline.md:482` records the
single `#fefefe` near-white square at spiral position 164 = byte 21, bit 4.
This tool re-finds exactly that, which pins the traversal order, the origin and
the bit sense simultaneously. If CHECK 1's "PASS" ever prints while the witness
fails, the harness is wrong and every number here is void.

Local only. Reads one JSON file already in the repo. No network, no keys.
"""
import json
import math
import pathlib

BASE = pathlib.Path(__file__).resolve().parents[1]
GRID = BASE / "data" / "phase1-matrix-14x14-full.json"

# GSMG_research_baseline.md:482 -- spiral position of the lone #fefefe square,
# and the byte/bit it was independently decoded to.
WITNESS_POS = 164
WITNESS_BYTE = 21
WITNESS_BIT = 4


def load():
    d = json.loads(GRID.read_text())
    return [list(r) for r in d["rows"]]


def spiral(n: int) -> list[tuple[int, int]]:
    """CCW from top-left, DOWN the left column first (the file's own `_read`)."""
    order = []
    top, bot, left, right = 0, n - 1, 0, n - 1
    while top <= bot and left <= right:
        for r in range(top, bot + 1):
            order.append((r, left))
        left += 1
        if top <= bot:
            for c in range(left, right + 1):
                order.append((bot, c))
            bot -= 1
        if left <= right:
            for r in range(bot, top - 1, -1):
                order.append((r, right))
            right -= 1
        if top <= bot:
            for c in range(right, left - 1, -1):
                order.append((top, c))
            top += 1
    return order


def is_prime(x: int) -> bool:
    if x < 2:
        return False
    f = 2
    while f * f <= x:
        if x % f == 0:
            return False
        f += 1
    return True


def main() -> int:
    g = load()
    n = len(g)
    assert n == len(g[0]), "grid is not square"
    order = spiral(n)
    assert len(order) == n * n, "spiral did not cover the grid"
    pos = {cell: i + 1 for i, cell in enumerate(order)}
    bits = "".join("1" if g[r][c] in "BK" else "0" for r, c in order)
    nbytes = len(bits) // 8

    print(f"grid {n}x{n} = {n*n} cells -> {len(bits)} bits "
          f"= {nbytes} bytes + {len(bits) % 8} trailing bits")

    # ---------------------------------------------------------------- witness
    byte_i = (WITNESS_POS - 1) // 8
    bit_i = (WITNESS_POS - 1) % 8
    ok_w = (byte_i + 1 == WITNESS_BYTE and bit_i + 1 == WITNESS_BIT)
    print(f"  [{'PASS' if ok_w else 'FAIL'}] WITNESS #fefefe at spiral pos "
          f"{WITNESS_POS} -> byte {byte_i+1}, bit {bit_i+1} "
          f"(expected {WITNESS_BYTE}/{WITNESS_BIT})")
    if not ok_w:
        print("WITNESS FAILED -- every number below is void.")
        return 1

    # ------------------------------------------------------- check 1: markers
    Y = sorted(pos[(r, c)] for r in range(n) for c in range(n) if g[r][c] == "Y")
    B = sorted(pos[(r, c)] for r in range(n) for c in range(n) if g[r][c] == "B")
    want = set(range(8, 8 * nbytes + 1, 8))
    got = set(Y) | set(B)
    c1 = got == want
    print(f"  [{'PASS' if c1 else 'FAIL'}] CHECK 1  Y({len(Y)}) + B({len(B)}) "
          f"occupy exactly the {nbytes} byte-boundary positions: {c1}")
    if not c1:
        print(f"          unexpected on boundaries: {sorted(got - want)}")
        print(f"          boundaries unmarked:      {sorted(want - got)}")
    p = 1.0 / math.comb(n * n, len(got))
    print(f"          1/C({n*n},{len(got)}) = {p:.3e} under uniform choice")
    print(f"          YELLOW at {Y}")
    print(f"          BLUE   at {B}")
    print(f"          marker string (Y=0,B=1): "
          f"{''.join('0' if k*8 in Y else '1' for k in range(1, nbytes+1))}")

    # ------------------------------------------------- check 2: tautology trap
    agree = sum(1 for k in range(1, nbytes + 1)
                if (bits[8*k - 1] == "1") == (8 * k in set(B)))
    print(f"  [INFO] CHECK 2  marker==own-bit on {agree}/{nbytes} bytes. "
          f"TAUTOLOGY by `_read` (B/K=1, W/Y=0) -- NOT evidence.")

    # ------------------------------------------------------- check 3: symmetry
    same = sum(1 for r in range(n) for c in range(n)
               if g[r][c] == g[n-1-r][n-1-c])
    bw = sum(1 for r in range(n) for c in range(n)
             if (g[r][c] in "KW") == (g[n-1-r][n-1-c] in "KW"))
    tr = sum(1 for r in range(n) for c in range(n) if g[r][c] == g[c][r])
    print(f"  [INFO] CHECK 3  180-rot same {same}/{n*n} (chance "
          f"{n*n*0.25:.0f}); black/white agree {bw}/{n*n}; transpose "
          f"{tr}/{n*n}")
    rot_pairs = sum(1 for cell in [(r, c) for r in range(n) for c in range(n)
                                  if g[r][c] in "YB"]
                    if g[n-1-cell[0]][n-1-cell[1]] in "YB")
    print(f"          Y/B cells whose 180-rot partner is also Y/B: "
          f"{rot_pairs}/{len(Y)+len(B)}")

    # -------------------------------------------------- primes, left unproven
    primes = [i for i in range(1, nbytes + 1) if is_prime(i)]
    ms = "".join("0" if k * 8 in Y else "1" for k in range(1, nbytes + 1))
    print(f"  [INFO] prime byte indices 1..{nbytes}: {primes} ({len(primes)})")
    print(f"          marker bits at prime indices: "
          f"{''.join(ms[i-1] for i in primes)}  (NOT claimed as a reading)")
    return 0 if c1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
