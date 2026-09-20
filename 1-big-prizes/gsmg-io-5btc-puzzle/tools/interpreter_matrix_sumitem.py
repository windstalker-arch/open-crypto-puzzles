#!/usr/bin/env python3
"""interpreter_matrix_sumitem.py -- battery (b): matrix-sumlist over the raw
15x19 even + 15x19 odd grids using the KEYED-interpreter alphabet DBIFHCEG
(interpreter square value order: D=1,B=2,I=3,F=4,H=5,C=6,E=7,G=8,A=9,K=10..Z=26).

Bifid repro certified (bifid_repro.py): grid DBIFHCEGAKLMNOPQRSTUVWXYZ 5x5
row-major, ID square, half-split. The keyed alphabet ORDER itself was never
used as the matrix A=1..26 value map in any prior row (8056/8057 used the
natural A=1..Z=26 on these grids). This is the untested combo: cell = position
within DBIFHCEG-first keyed order, row/col sums on the 15x19 even and 15x19 odd
grids, all joins/mod-reductions, both gates.
"""

import json, itertools

KEY = "DBIFHCEG"          # 9-letter keyed head (interpreter alphabet, J dropped)
KEYED = KEY + "".join(c for c in "AKLMNOPQRSTUVWXYZ" if c not in KEY)  # 26
VAL = {c: i + 1 for i, c in enumerate(KEYED)}   # D=1 ... Z=26 in keyed order
assert len(KEYED) == 26 and set(KEYED) == set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

data = json.load(open("data/salphaseion-streams.json"))
EVEN = data["even_stream"]        # 285 chars = 15x19
ODD = data["odd_pre_reduction"]   # 285 chars = 15x19

def to_grid(s, w=19):
    return [s[r * w:(r + 1) * w] for r in range(len(s) // w)]

def rsums(g): return [sum(VAL[c] for c in row) for row in g]
def csums(g): return [sum(VAL[g[r][c]] for r in range(len(g))) for c in range(len(g[0]))]

def j1(v):  return "".join(str(x) for x in v)
def j26(v): return "".join(chr(65 + (x - 1) % 26) for x in v)
def j36(v):
    A = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(A[x % 36] for x in v)
def jm9(v): return "".join(chr(48 + (x - 1) % 9) for x in v)  # 1..9 digits

def build():
    cands = set()
    for name, s in (("even", EVEN), ("odd", ODD)):
        g = to_grid(s)
        rs, cs = rsums(g), csums(g)
        for tag, v in (("R", rs), ("C", cs)):
            for jn in (j1, j26, j36, jm9):
                cands.add(jn(v))
                cands.add(jn(v)[::-1])
                cands.add(jn(v).lower())
        # RC / CR concats, both directions
        for jn in (j1, j26, j36):
            cands.add(jn(rs) + jn(cs))
            cands.add(jn(cs) + jn(rs))
        # interleave digits (123456.. / house-interleave)
        d = []
        for a, b in zip(rs, cs):
            d += [a, b]
        cands.add(j1(d)); cands.add(j36(d))
        # grid-diagonal reads (main + anti), row/col reversed
        r = len(g); c = len(g[0])
        diag = [g[i][i] for i in range(min(r, c))]
        anti = [g[i][c - 1 - i] for i in range(min(r, c))]
        for seq in (diag, anti, rs[::-1], cs[::-1]):
            cands.add(j1([VAL[x] for x in seq]))
    # even+odd combined 15x38 by rows, and row-pairwise interleave
    ge, go = to_grid(EVEN), to_grid(ODD)
    rows = [ge[i] + go[i] for i in range(15)]          # 15x38
    rs = [sum(VAL[c] for c in row) for row in rows]
    cols = [sum(rows[r][c] for r in range(15)) for c in range(38)]
    for jn in (j1, j26, j36):
        cands.add(jn(rs)); cands.add(jn(cols))
        cands.add(jn(rs) + jn(cols)); cands.add(jn(cols) + jn(rs))
    inter = []
    for i in range(15):
        inter.append(VAL[EVEN[i]] and 0 or 0)
    # row-pairwise digit interleave across both grids
    digs = []
    for r in range(15):
        for cr in range(19):
            digs.append(VAL[ge[r][cr]])
            digs.append(VAL[go[r][cr]])
    digs2 = []
    for r in range(15):
        for cr in range(19):
            digs2.append(VAL[go[r][cr]] * 26 + VAL[ge[r][cr]])
    cands.add(j1(digs)); cands.add(j26(digs)); cands.add(j36(digs))
    cands.add(j1(di if False else digs2)[:4] and "" or "")
    return cands

cands = build()
lst = sorted(cands)
print(f"interpreter-keyed matrix-sumitem battery: {len(lst)} forms")
open("/data/data/com.termux/files/usr/tmp/opencode/gsmg_ik_matrix1.txt", "w").write("\n".join(lst))
print("wrote")
