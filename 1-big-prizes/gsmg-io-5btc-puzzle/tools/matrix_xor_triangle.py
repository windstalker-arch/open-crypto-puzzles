#!/usr/bin/env python3
"""matrix_xor_triangle.py -- XOR-triangle collapse of the literal 2D matrix
bitstreams (103x103 cosmic, 14x14 phase-1). Deterministic; research-only.

Prior sweeps applied XOR-triangle / pyramid reductions to the 1D digit streams
(dbbib/faed) and to the Chain4 byte blocks, and a Rule-90 *generativity* test to
the 103x103.  This tool instead collapses the verified 2D bit matrices themselves:

  C1  flat adjacent-pair XOR pyramid of the flattened stream (rows, cols, spiral)
  C2  per-row and per-column adjacent-XOR apex -> 103/14-bit vectors
  C3  alternating 2D fold (rows then cols) to a single bit, per stage
  C4  NW-SE and NE-SW diagonal XOR lists
  C5  row1-4 elementwise-XOR vector and its 4xN XOR pyramid (community hint)

Outputs candidate X lines (hex and latin-1 of each packed read) for the oracles.
No randomness.

Witnesses (asserted here, certified in analysis/tested.md):
  * cosmic matrix bit-unpack: rs 39..67, cs 40..65, S=5193 (103x103)
  * phase-1 matrix cell-center ccw spiral -> b"gsmg.io/theseedisplanted"
"""
import os
import json
from pathlib import Path

from PIL import Image

BASE = Path(os.path.expanduser("~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle"))
COSMIC = Path(os.path.expanduser("~/cosmic_decrypted.bin"))
PUZZLE_PNG = Path(os.path.expanduser("~/briefcase/gsmg-community/puzzle.png"))

OUT = "/data/data/com.termux/files/usr/tmp/opencode/matrix_xor_triangle_cands.txt"

# ---------------------------------------------------------------- cosmic 103x103
raw = COSMIC.read_bytes()
assert len(raw) == 1327
cosbits = []
for b in raw:
    for s in range(7, -1, -1):
        cosbits.append((b >> s) & 1)
assert len(cosbits) == 10616
N = 103
CM = [cosbits[i * N:(i + 1) * N] for i in range(N)]
rs = [sum(r) for r in CM]
cs = [sum(CM[i][j] for i in range(N)) for j in range(N)]
assert 39 <= min(rs) and max(rs) <= 67, rs
assert 40 <= min(cs) and max(cs) <= 65, cs
assert sum(rs) == 5193

# ---------------------------------------------------------------- phase-1 14x14
im = Image.open(PUZZLE_PNG).convert("RGB")
cells = []
for r in range(14):
    row = []
    for c in range(14):
        px = im.getpixel((c * 75 + 37, r * 75 + 37))
        row.append(px)
    cells.append(row)


def bitof(px):
    r, g, b = px
    if (r, g, b) == (63, 72, 204):
        return 1
    if r < 40 and g < 40 and b < 40:
        return 1
    return 0


P14 = [[bitof(px) for px in row] for row in cells]
rs14 = [sum(r) for r in P14]
cs14 = [sum(P14[i][j] for i in range(14)) for j in range(14)]
assert rs14 == [6, 10, 8, 7, 6, 6, 5, 5, 9, 9, 7, 8, 7, 9], rs14
assert cs14 == [8, 10, 8, 10, 8, 7, 4, 6, 7, 5, 9, 6, 6, 8], cs14


def ccw_spiral(M):
    rows, cols = len(M), len(M[0])
    out = []
    sr, sc, er, ec = 0, 0, rows - 1, cols - 1
    while sr <= er and sc <= ec:
        for i in range(sr, er + 1):
            out.append(M[i][sc])
        sc += 1
        for j in range(sc, ec + 1):
            out.append(M[er][j])
        er -= 1
        for i in range(er, sr - 1, -1):
            out.append(M[i][ec])
        ec -= 1
        for j in range(ec, sc - 1, -1):
            out.append(M[sr][j])
        sr += 1
    return out


SPIRAL = ccw_spiral(P14)
s = "".join(map(str, SPIRAL))
assert bytes(int(s[i:i + 8], 2) for i in range(0, 192, 8)) == b"gsmg.io/theseedisplanted"

# ---------------------------------------------------------------- helpers
def pack(bits, width):
    n = len(bits)
    pad = (-n) % width
    bits = bits + [0] * pad
    out = bytearray()
    for i in range(0, len(bits), 8):
        b = 0
        for j in range(8):
            b = (b << 1) | bits[i + j]
        out.append(b)
    return bytes(out)


def adj_xor_pyramid(bits):
    levels = [list(bits)]
    cur = levels[0]
    while len(cur) > 1:
        nxt = [cur[k] ^ cur[k + 1] for k in range(len(cur) - 1)]
        levels.append(nxt)
        cur = nxt
    return levels


def diags(M, nwse=True):
    rows, cols = len(M), len(M[0])
    out = []
    for d in range(-(cols - 1), rows):
        vals = []
        for i in range(rows):
            j = d + i if nwse else (cols - 1 - d - i)
            if 0 <= j < cols:
                vals.append(M[i][j])
        if vals:
            out.append(vals)
    return out


def xor2(vals):
    x = 0
    for v in vals:
        x ^= v
    return x


def emit(cands, label, bytesvals):
    for i, bv in enumerate(bytesvals):
        if not bv:
            continue
        text = bv.decode("latin-1")
        cands[label + f"#{i} hex"] = bv.hex()
        cands[label + f"#{i} lat"] = text


# ---------------------------------------------------------------- collection
cands = {}


def addmatrix(M, tag):
    rows, cols = len(M), len(M[0])

    # C1: flat pyramids over row-major / col-major flattens
    for order, flat in (("rm", [b for row in M for b in row]),
                        ("cm", [M[i][j] for j in range(cols) for i in range(rows)])):
        levs = adj_xor_pyramid(flat)
        # sample levels (incl apex) packed at several widths
        nsample = sorted(set([max(1, int(len(flat) * f)) for f in (0.5, 0.25, 0.1)]))
        idx = set([0, len(levs) - 1] + [min(len(levs) - 1, k) for k in nsample])
        for k in sorted(idx):
            for width in (8, 32, 256):
                emit(cands, f"{tag}|C1|{order}|lvl{k}|w{width}",
                     [pack(levs[k], width)])
        emit(cands, f"{tag}|C1|{order}|parities", [pack([xor2(l) for l in levs], 8)])

    # C2: per-row / per-col apex vectors
    rvec = [adj_xor_pyramid(r)[-1][0] for r in M]
    cvec = [adj_xor_pyramid([M[i][j] for i in range(rows)])[-1][0] for j in range(cols)]
    emit(cands, f"{tag}|C2|rowvec", [pack(rvec, 8)])
    emit(cands, f"{tag}|C2|colvec", [pack(cvec, 8)])

    # C3: alternating 2D fold
    stage = [list(r) for r in M]
    stouts = []
    stouts.append([b for row in stage for b in row])
    while len(stage) > 1:
        if len(stage[0]) > 1:
            stage = [[stage[i][j] ^ stage[i][j + 1] for j in range(len(stage[0]) - 1)]
                     for i in range(len(stage))]
        elif len(stage) > 1:
            stage = [[stage[i][0] ^ stage[i + 1][0]] for i in range(len(stage) - 1)]
        stouts.append([b for row in stage for b in row])
        if len(stage) == 1 and len(stage[0]) == 1:
            break
    for k in range(min(len(stouts), 12)):
        emit(cands, f"{tag}|C3|stage{k}", [pack(stouts[k], 8)])

    # C4: diagonal XOR lists
    for nm, nwse in (("nwse", True), ("nesw", False)):
        dl = [xor2(v) for v in diags(M, nwse)]
        emit(cands, f"{tag}|C4|{nm}", [pack(dl, 8)])
        emit(cands, f"{tag}|C4|{nm}|mod26", [bytes(v % 26 + 65 for v in dl)])
        emit(cands, f"{tag}|C4|{nm}|mod10", [b"".join(str(v % 10).encode() for v in dl)])

    # C5: row1-4 (community hint) - rows 1..4 1-indexed
    if rows >= 4:
        block = M[:4]
        elem = [xor2([block[i][j] for i in range(4)]) for j in range(cols)]
        emit(cands, f"{tag}|C5|r1-4xor", [pack(elem, 8)])
        flat4 = [b for row in block for b in row]
        levs = adj_xor_pyramid(flat4)
        for k in [0, 1, 2, 3, len(levs) - 1]:
            emit(cands, f"{tag}|C5|r1-4|lvl{k}", [pack(levs[k], 8)])
        rvec4 = [adj_xor_pyramid(r)[-1][0] for r in block]
        emit(cands, f"{tag}|C5|r1-4|rowex", [pack(rvec4, 8)])


addmatrix(CM, "cos103")
addmatrix(P14, "ph14")
addmatrix([[P14[c][r] for c in range(14)] for r in range(14)], "ph14T")

# spiral flatten of the 14x14 (certified witness path) flat pyramid
levs = adj_xor_pyramid(SPIRAL)
for k in [0, len(levs) - 1, int(len(levs) * 0.5)]:
    emit(cands, f"ph14|C1|sp|lvl{k}|w8", [pack(levs[k], 8)])

order = sorted(cands)
with open(OUT, "w") as f:
    f.write("\n".join(cands[k] for k in order))
    f.write("\n")
print(f"candidates: {len(order)} -> {OUT}")
print("sample:", [cands[k] for k in order[:3]], [cands[k] for k in order[-3:]])