#!/usr/bin/env python3
"""colorprime_matrix_battery.py -- late-324. Deep-research seams on the certified
spiral color-prime 0x08c26d (573-ish family) and the yellow/blue matrix geometry
that were NOT closed by rows 136/137/138/141 (row-major key) or late-271..311.

The certified color word is the CCW-spiral compact read of the 24 colored cells
(follow-white-rabbit-grid.json) matching the README 14x14 definition exactly:
    BBBBYBBBYYBBBBYBBYYBYYBY
    Yellow=1 bits = 000010001100001001101101 = 0x08c26d (PRIME), 1-based
    one-positions [5,9,10,15,18,19,21,22,24].  Row 138 masked with the ROW-MAJOR
    key positions [2,8,9,10,12,14,18,19,22]; the SPIRAL positions were never used.

Families generated (every output line is a candidate X for the funded gates):
  A. spiral color-prime as cyclic positional mask (keep/drop one-positions and
     complement positions, mod-24) over dbbib69/faed570/concats; also the
     24-bit streams raw as bigint->bytes ascii and as hexpair ascii.
  C. RLE run-length encoding of the certified color word (runs
     [4,1,3,2,4,1,2,2,1,2,1,1], blue/yellow alternating) as digits,
     sums/prefixes, and repeated-char constructions.
  D. base-14 raw coordinate value maps (row/col/r+c/|r-c| value 0..13 -> digit,
     letter order = certified spiral ranks of the 9 yellow cells AND first-9
     blue cells), decoded via bigint base-14 -> bytes -> ascii and via hexpair.
     (Row 182 closed only mod-10/mod-9 reductions of coordinates, never the
     raw base-14 0..13 values.)

Usage:
    python3 tools/colorprime_matrix_battery.py --selftest
    python3 tools/colorprime_matrix_battery.py --gen                # writes candidates
    python3 tools/colorprime_matrix_battery.py --both               # write gates + feed
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())
GRID = json.loads(Path(os.path.join(ROOT, "data", "follow-white-rabbit-grid.json")).read_text())

DBBI69 = DATA["dbbib"]
DBBI91 = DATA["dbbib_91"]
FAED = DATA["faed_570"][:570]
CANON = dict(a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, i=9)

# certified spiral compact color word (CCW, start top-left, d,r,u,l)
_BLUE = {tuple(c) for c in GRID["blue"]}
_YELLOW = {tuple(c) for c in GRID["yellow"]}
_COLOR = {c: "B" for c in _BLUE}
_COLOR.update({c: "Y" for c in _YELLOW})

_N = 14
_seq = [(1, 0), (0, 1), (-1, 0), (0, -1)]
_seen = {(0, 0)}
_order = [(0, 0)]
_r, _c, _d = 0, 0, 0
for _ in range(_N * _N - 1):
    for _t in range(4):
        _dr, _dc = _seq[_d]
        _nr, _nc = _r + _dr, _c + _dc
        if 0 <= _nr < _N and 0 <= _nc < _N and (_nr, _nc) not in _seen:
            break
        _d = (_d + 1) % 4
    _r, _c = _nr, _nc
    _seen.add((_r, _c))
    _order.append((_r, _c))
SPIRAL_COLORED = [c for c in _order if c in _COLOR]           # 24 cells, certified order
COLOR_WORD = "".join(_COLOR[c] for c in SPIRAL_COLORED)       # BBBBYBBBYYBBBBYBBYYBYYBY
Y_BITS = "".join("1" if _COLOR[c] == "Y" else "0" for c in SPIRAL_COLORED)
B_BITS = "".join("1" if _COLOR[c] == "B" else "0" for c in SPIRAL_COLORED)
Y_ONES = [i for i, ch in enumerate(Y_BITS) if ch == "1"]
B_ONES = [i for i, ch in enumerate(B_BITS) if ch == "1"]
RUNS = []
last = None
for i, ch in enumerate(COLOR_WORD):
    if i == 0 or ch != COLOR_WORD[i - 1]:
        RUNS.append([ch, 1])
    else:
        RUNS[-1][1] += 1
RUN_LENS = [n for _, n in RUNS]
# 9 yellow cells in spiral rank order, 15 blue cells in spiral rank order
SPIRAL_YL = [c for c in SPIRAL_COLORED if _COLOR[c] == "Y"]
SPIRAL_BL = [c for c in SPIRAL_COLORED if _COLOR[c] == "B"]

STREAMS = {"dbbib69": DBBI69, "faed570": FAED,
           "dbbib69+faed570": DBBI69 + FAED, "faed570+dbbib69": FAED + DBBI69}


def apply_mask_mask(s: str, keep: set) -> str:
    """cyclic mod-24 positional mask: keep every token whose index%24 in keep."""
    return "".join(ch for i, ch in enumerate(s) if (i % 24) in keep)


def bigint_bytes(ds: str, base: int) -> bytes:
    if not ds or not all(c.isdigit() for c in ds):
        return b""
    v = int(ds, base)
    n = (v.bit_length() + 7) // 8
    return v.to_bytes(n, "big")


def hexpair_bytes(ds: str) -> bytes:
    if len(ds) % 2:
        ds = ds[:-1]
    try:
        return bytes.fromhex(ds)
    except ValueError:
        return b""


def letters_of(s: str, m) -> str:
    return "".join(str(m.get(ch, ch)) for ch in s)


def coord_digit_map(cells, axis, mod, order_letters="abcdefghi"):
    """a..i -> raw row/col value at the cell with that rank."""
    m = {}
    for j, (r, c) in enumerate(cells[:9]):
        v = (r if axis == "row" else c)
        m[order_letters[j]] = str(v % mod if mod else v)
    return m


def gen():
    cands = []
    # ---- A: spiral color-prime masks ----
    keep_sets = {
        "spiral_ones": set(Y_ONES),       # prime positions (9)
        "spiral_zeros": set(B_ONES),      # complement (15)
    }
    for kname, keep in keep_sets.items():
        for sname, s in STREAMS.items():
            for rev in (False, True):
                src = s[::-1] if rev else s
                kept = apply_mask_mask(src, keep)
                if not kept:
                    continue
                cands.append(f"A.{kname}.{sname}.fwd_keep" if not rev else f"A.{kname}.{sname}.rev_keep")
                cands.append(kept)
                # interpreter letter decodes of the kept stream
                cands.append(letters_of(kept, CANON))
                # digits via CANON then bigint->ascii
                ds = "".join(str(CANON.get(ch, 0)) for ch in kept)
                cands.append(bigint_bytes(ds, 10).decode("ascii", "replace"))
    # the 24-bit streams raw
    cands.append(Y_BITS)
    cands.append(B_BITS)
    cands.append(hex(int(Y_BITS, 2)))          # 0x8c26d
    cands.append(hex(int(B_BITS, 2)))
    cands.append(str(int(Y_BITS, 2)))          # 574061
    cands.append(str(int(B_BITS, 2)))

    # ---- C: RLE runs ----
    rle = "".join(str(n) for _, n in RUNS)          # 413241221211
    cands.append(rle)
    cands.append("-".join(str(n) for _, n in RUNS))
    cands.append("".join(str(n) for n in reversed(RUN_LENS)))
    cands.append("".join(str(n) for n in RUN_LENS if n % 2))
    # prefix sums of runs
    acc = 0
    pref = []
    for ch, n in RUNS:
        acc += n
        pref.append(str(acc))
    cands.append("".join(pref))
    cands.append(",".join(pref))
    # run lengths of each color separately
    ylens = [n for ch, n in RUNS if ch == "Y"]
    blens = [n for ch, n in RUNS if ch == "B"]
    cands.append("".join(str(n) for n in ylens))   # 1,2,1,2,2,1 -> 121221
    cands.append("".join(str(n) for n in blens))   # 4,3,4,2,1,1 -> 434211
    cands.append("".join(str(n) for n in ylens) + "".join(str(n) for n in blens))
    cands.append("".join(str(n) for n in blens) + "".join(str(n) for n in ylens))
    # spread Y-run lengths among blue: interleave b1 y1 b2 y2 ...
    inter = "".join(f"{b}{y}" for b, y in zip(blens, ylens))
    cands.append(inter)
    cands.append("".join(str(n) for ch, n in RUNS) + str(len(RUNS)))
    # run positions as a..i length-12: concatenated positional digits
    poss = []
    acc = 0
    for ch, n in RUNS:
        poss.append(str(acc + 1))
        acc += n
    cands.append("".join(poss))
    # zero-based variants
    cands.append("".join(str(sum(x[1] for x in RUNS[:j])) for j in range(len(RUNS))))

    # ---- D: base-14 raw coordinate maps (yellow first-9, blue first-9) ----
    order_sets = {"yellow_spiral": SPIRAL_YL, "blue_spiral_first9": SPIRAL_BL[:9]}
    for axis in ("row", "col"):
        for oname, cells in order_sets.items():
            for reduce_axis in (None, lambda r, c: r + c, lambda r, c: abs(r - c)):
                tag = ("" if reduce_axis is None else
                       ("rc+" if reduce_axis(2, 3) == 5 else "rcabs"))
                m = {}
                for j, (r, c) in enumerate(cells):
                    v = r if axis == "row" else c
                    if reduce_axis is not None:
                        v = reduce_axis(r, c)
                    m["abcdefghi"[j]] = str(v % 14 if v >= 14 else v)
                for sname in ("dbbib69", "faed570", "dbbib69+faed570", "faed570+dbbib69"):
                    s = STREAMS[sname]
                    dsl = "".join(m.get(ch, "0") for ch in s)
                    if all(ch in "0123456789" for ch in dsl):
                        cands.append(bigint_bytes(dsl, 14).decode("ascii", "replace"))
                        cands.append(hexpair_bytes(dsl).decode("ascii", "replace"))
    return [c for c in dict.fromkeys(cands)
            if c and not any(x in c for x in ("\n", "\r", "\t"))
            and all(32 <= ord(x) < 127 for x in c)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--gen", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        assert COLOR_WORD == "BBBBYBBBYYBBBBYBBYYBYYBY", COLOR_WORD
        assert Y_BITS == "000010001100001001101101", Y_BITS
        assert int(Y_BITS, 2) == 574061, int(Y_BITS, 2)
        assert RUN_LENS == [4, 1, 3, 2, 4, 1, 2, 2, 1, 2, 1, 1], RUN_LENS
        assert len(SPIRAL_YL) == 9 and len(SPIRAL_BL) == 15
        assert Y_ONES == [4, 8, 9, 14, 17, 18, 20, 21, 23], Y_ONES
        c = gen()
        assert "574061" in c
        assert "413241221211" in c
        assert c and len(c) > 40
        print(f"SELFTEST OK ({len(c)} unique candidates)")
        return 0

    if args.gen:
        c = gen()
        out = os.path.join(os.path.expanduser("~"), "colorprime_matrix_cands.txt")
        Path(out).write_text("\n".join(c) + "\n")
        print(f"wrote {len(c)} unique candidates -> {out}")
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())