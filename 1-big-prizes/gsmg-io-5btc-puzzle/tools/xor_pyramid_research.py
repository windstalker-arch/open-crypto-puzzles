#!/usr/bin/env python3
"""xor_pyramid_research.py -- XOR pyramid/triangle over *triangular row
layouts* of the final-page digit streams (read-only research; no oracle feed).

Row layouts probed (user-directed):
  35-cell  T35 = [1,2,3,4,5,6,7,7]
  17-cell  T17 = [1,2,3,4,5,2]
  18-cell  T18 = [1,2,3,4,5,3]
  plus natural relatives: reversed row orders, the plain triangle 1..7=28,
  doubled-base 7,7,6,...,1, and tile-into-blocks of the streams.

For every (stream, block, layout, value-encoding) we report the XOR/arithmetic
reductions of the trapezoid:
  - row parity (XOR of each row) and row sum
  - column parity aligned-left and col sum
  - the standard adjacent-pair XOR-triangle apex of the whole block
  - partial apices of the 1..7 triangle vs the extra row
  - flatten / apex ascii / hex reads
and FLAG any reduction that collides with the canonical anchors:
  x0=35, y0=74, K=76, RS/CS lists, rabbit key 0x41D464 ones {2,5,6,10,12,14,15,16,22},
  printable-ASCII stretch, or the certified Bifid plaintext head / object_256.

Output is diagnostic ASCII only.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.loads(Path(os.path.join(BASE, "data",
                                   "finalpage-digit-streams.json")).read_text())
STORED = json.loads(Path(os.path.join(BASE, "data",
                                     "salphaseion-streams.json")).read_text())

DBBIB = DATA["dbbib_91"].lower()   # authoritative; DATA["dbbib"] is the crop
FAED = DATA["faed_570"].rstrip("z").lower()
CANON = {"a": 8, "b": 1, "c": 5, "d": 0, "e": 6, "f": 3, "g": 7, "h": 4, "i": 2}

LAYOUTS = {
    "T35 [1,2,3,4,5,6,7,7]": [1, 2, 3, 4, 5, 6, 7, 7],
    "T35 rev [7,7,6,5,4,3,2,1]": [7, 7, 6, 5, 4, 3, 2, 1],
    "T35 [7,6,5,4,3,2,1,7]": [7, 6, 5, 4, 3, 2, 1, 7],
    "T17 [1,2,3,4,5,2]": [1, 2, 3, 4, 5, 2],
    "T17 rev [2,5,4,3,2,1]": [2, 5, 4, 3, 2, 1],
    "T18 [1,2,3,4,5,3]": [1, 2, 3, 4, 5, 3],
    "T18 rev [3,5,4,3,2,1]": [3, 5, 4, 3, 2, 1],
    "T28 [1,2,3,4,5,6,7]": [1, 2, 3, 4, 5, 6, 7],
    "T28 rev [7,6,5,4,3,2,1]": [7, 6, 5, 4, 3, 2, 1],
}

RS = [7, 6, 5, 5, 5, 5, 3, 8, 7, 6, 7, 6, 6, 0]
CS = [7, 8, 4, 8, 7, 5, 5, 5, 5, 5, 6, 5, 6, 0]
RKEY_ONES = {2, 5, 6, 10, 12, 14, 15, 16, 22}
OBJ256 = STORED["object_256"]


def val(stream, kind):
    if kind == "pos":
        return [ord(c) - 97 for c in stream]
    if kind == "one":
        return [ord(c) - 96 for c in stream]
    return [CANON[c] for c in stream]


def xor_reduce(vals):
    x = 0
    for v in vals:
        x ^= v
    return x


def pyramid_apex(vals):
    """Standard adjacent-pair XOR pyramid of a 1-D sequence down to apex."""
    row = vals[:]
    while len(row) > 1:
        row = [row[i] ^ row[i + 1] for i in range(len(row) - 1)]
    return row[0] if row else 0


def layers(seq, layout):
    rows, i = [], 0
    for ln in layout:
        rows.append(seq[i:i + ln])
        i += ln
    return rows


def report_block(name, seq, vals):
    ax = pyramid_apex(vals)
    flat_xor = xor_reduce(vals)
    flat_sum = sum(vals)
    ax_sym = "".join("abcdefghi"[v] for v in
                     [ax]) if ax < 9 else "?"
    print(f"    {name}: len={len(vals)} apex={ax} flat_xor={flat_xor} "
          f"flat_sum={flat_sum} apex_sym={ax_sym}")
    return ax, flat_xor, flat_sum


def analyze(layout_name, layout, seq, vals, flags):
    rows = layers(vals, layout)
    widths = sorted(set(layout), reverse=True)
    ncols = max(layout)
    row_xor = [xor_reduce(r) for r in rows]
    row_sum = [sum(r) for r in rows]
    col_xor = []
    col_sum = []
    for c in range(ncols):
        col_vals = [r[c] for r in rows if c < len(r)]
        col_xor.append(xor_reduce(col_vals))
        col_sum.append(sum(col_vals))
    apex = pyramid_apex(vals)
    # extra-row partial apices: run triangle on leading rows then drop last
    # row (the doubled 7) -> two-layer view; and split of the base rows.
    tri_rows = rows[:-1]
    n_tri = sum(len(r) for r in tri_rows)
    apex_tri = pyramid_apex(vals[:n_tri]) if n_tri else 0
    apex_last = pyramid_apex(vals[n_tri:]) if len(vals) > n_tri else 0
    body = {"x": 0, "y": 0, "k": 0}
    body["x"] = apex
    body["k"] = flat_k = sum(1 for v in vals if v != 0)
    body["y"] = 0

    hits = []
    for lab, L in (("RS", RS), ("CS", CS)):
        S = row_sum + col_sum
        if S == L:
            hits.append(f"row+col sums == {lab}")
    if col_sum == RS or row_sum == RS:
        hits.append("partial == RS")
    if col_sum == CS or row_sum == CS:
        hits.append("partial == CS")
    for comb_name, comb in (("rows_xor+cols_xor", row_xor + col_xor),
                            ("rows_sum+cols_sum", row_sum + col_sum),
                            ("cols_xor+rows_xor", col_xor + row_xor)):
        for lab, L in (("RS", RS), ("CS", CS)):
            if comb == L:
                hits.append(f"{comb_name} == {lab}")
    if apex == 35:
        hits.append("apex==35 (x0)")
    if apex == 17 or apex == 18:
        hits.append(f"apex=={apex} (half/better-half)")
    if flat_k == 76:
        hits.append("nonzero-count K==76")
    if set(col_xor) == RKEY_ONES or set(col_sum) == RKEY_ONES:
        hits.append("collides rabbit 0x41D464")

    flags["cols_xor"] = col_xor
    flags["cols_sum"] = col_sum
    flags["rows_xor"] = row_xor
    flags["rows_sum"] = row_sum
    flags["apex"] = apex
    flags["apex_tri"] = apex_tri
    flags["apex_last"] = apex_last
    flags["k"] = flat_k
    flags["hits"] = hits

    if hits:
        print(f"    *** HIT {layout_name}: {hits}")
        print(f"        rows_xor={row_xor} rows_sum={row_sum}")
        print(f"        cols_xor={col_xor} cols_sum={col_sum}")
        print(f"        apex={apex} tri={apex_tri} last={apex_last} K={flat_k}")

    ascii_probe = []
    for name, s in (("rows_xor", row_xor), ("rows_sum", row_sum),
                    ("cols_xor", col_xor), ("cols_sum", col_sum)):
        # only flag stretches of 2+ printable ASCII
        s = [v % 26 + 65 for v in s]
        probe = "".join(chr(v) for v in s)
        if len(probe) >= 2 and probe.isalpha():
            ascii_probe.append(f"{name}->{probe}")
    if ascii_probe:
        flags["printable"].append((layout_name, ascii_probe))
    print(f"    {layout_name}: rx={row_xor} sx={row_sum} cx={col_xor} "
          f"cs={col_sum} apex={apex} tri={apex_tri} last={apex_last} K={flat_k}")
    return row_xor, row_sum, col_xor, col_sum, apex, flat_k


def main() -> int:
    print("=== XOR pyramid/triangle research over triangular row layouts ===\n")
    flags = {"printable": []}
    for stream_name, stream in (("dbbib", DBBIB), ("faed", FAED)):
        for kind in ("pos", "one", "canon"):
            v = val(stream, kind)
            print(f"-- {stream_name} ({len(v)}) encoding={kind} --")
            for layout_name, layout in LAYOUTS.items():
                tot = sum(layout)
                # tile the stream into whole blocks of this layout
                blocks = [v[i:i + tot] for i in range(0, len(v), tot)]
                for b in blocks:
                    if len(b) != tot:
                        continue
                    analyze(layout_name, layout, stream, b, flags)
                # also the reverse-order blocks (last-first) for the doubled rows
                rev = v[::-1]
                for b in [rev[i:i + tot] for i in range(0, len(rev), tot)]:
                    if len(b) != tot:
                        continue
                    analyze(f"{layout_name} [rev-seq]", layout, rev, b, flags)

    # cross-stream cuts that fit the layouts exactly
    print("\n-- exact slices matching layout totals --")
    for stream_name, stream, sl in (("dbbib", DBBIB, 69), ("faed", FAED, 570)):
        kinds_v = {k: val(stream, k) for k in ("pos", "one", "canon")}
        for layout_name, layout in LAYOUTS.items():
            tot = sum(layout)
            if sl % tot:
                continue
            for kind in ("pos", "one", "canon"):
                analyze(f"{stream_name}/{kind}", layout, stream,
                        kinds_v[kind], flags)

    print("\n-- HALF-AND-BETTER-HALF 17/18 alternating blocks --")
    for stream_name, stream, sl in (("dbbib", DBBIB, 69), ("faed", FAED, 570)):
        for kind in ("pos", "one", "canon"):
            v = val(stream, kind)
            print(f"  {stream_name}/{kind}")
            # alternating 17,18,17,18,... block parsing (and 18,17 first)
            for start in (17, 18):
                blocks = []
                rest = v[:]
                cur = start
                while len(rest) >= cur:
                    blocks.append(rest[:cur])
                    rest = rest[cur:]
                    cur = 35 - cur
                tag = f"alt{start}->" + ",".join(str(len(b)) for b in blocks)
                print(f"    {tag}: blocks={len(blocks)} rest={len(rest)}")
                for b in blocks:
                    lay = LAYOUTS[f"T{len(b)} [1,2,3,4,5,{len(b)-15}]"] \
                        if len(b) in (17, 18) else None
                    if lay:
                        analyze(tag, lay, stream, b, flags)

    print("\n=== printable-stretch flags ===")
    if not flags["printable"]:
        print("  none")
    async_obj = []
    return 0


if __name__ == "__main__":
    raise SystemExit(main())