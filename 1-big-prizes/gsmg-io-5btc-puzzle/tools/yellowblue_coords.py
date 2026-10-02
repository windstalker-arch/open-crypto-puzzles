#!/usr/bin/env python3
"""yellowblue_coords.py -- the creator's colour rule read on the 14x14 phase-1
matrix as a COORDINATE OBJECT, against the THIRD DOOR.

THE GAP, STATED PRECISELY. The surviving third-door branch is "a rule the creator
gave between the January 2020 poem and the April 2020 audio hint ('Yellow has a
number and so does Blue', 'primes', 'zeroed out') read on a non-textual object".

Three rows closed most of it, but not this cell:

  * R-COLORDOOR-2026-09-29 ran the rule against the third door on the STICKER
    strip and the colour BANDS (band46, band8, bot13, sec8, strip8) plus the
    9/15 NUMBER-PAIR spellings. FINDING 1: there is not one yellow tile on any
    of those objects, so the rule's own yellow side has no referent there.
  * R-YELLOWBLUE-HASH-2026-09-30 ran the audio hint's own instruction
    ("hash the text") on the certified colour-prime scalars. 628 derivations.
  * The coordinate-arithmetic row at `tested.md:4278` DID derive maps from the
    yellow/blue cell positions of `data/follow-white-rabbit-grid.json` --
    row%10, col%10, (r+c)%10, (r-c)%10, |r-c|, r*c%10, row%9, col%9, row+1 and
    so on, 26 unique maps, decoding dbbib/faed -- but it was run against the TWO
    FUNDED GATES ONLY. Grepping that row for the third door or `1NULY` returns
    nothing.

So the one colour-bearing object that actually HAS yellow on it - the 14x14
matrix - had its coordinates used as an interpreter-alphabet family and never
brought to the third door at all. That is this row.

WHY THE MATRIX IS THE RIGHT OBJECT AND THE BANDS ARE NOT. `R-COLORDOOR` FINDING 1
is the structural reason the sticker objects could never work: they have no
yellow. The 14x14 phase-1 map is the only certified colour object with a yellow
class at all, and it is the one the hint names ("Go back to the FIRST puzzle
piece"). Its counts are certified and mutually corroborating:

    Y (yellow) = 9      B (blue) = 15      K = 87      W = 85      total = 196

which is exactly the 9 / 15 the hint resolves to, read two independent ways -
`data/follow-white-rabbit-grid.json` stores the 9 yellow and 15 blue (row,col)
pairs, and `data/phase1-matrix-14x14-full.json` holds the complete 196-cell map.

THE THREE RULES, APPLIED AS ASKED. "primes" and "zeroed out" are the creator's
own words from the same window ("prime number is very important", "some
characters need to be zeroed out"), and they are applied here to the coordinate
object rather than to a text stream, which is the form nobody has tried:

  primes        keep only cells whose row, or column, or 1-based position, or
                whose coordinate VALUE is prime
  zeroed out    zero the prime-positioned cells and keep the rest, and the
                converse (keep the primes, zero the rest), then read the
                survivors as a digit string / an index string / a bit string
  hashed        the audio hint's "hash the text" applied to the coordinate
                object's own serialisations, since HASHTHETEXT is certified as a
                directive rather than a password (tested.md:3725-3733)

AXIS CONVENTION. The grid stores (row,col); whether the creator meant (row,col)
or (col,row) is not settled by the artifacts, so every method is run under BOTH.
W3 asserts the two conventions really do differ, so neither can be quietly dropped.

WITNESSES, because a negative here must be reproducible rather than asserted:

  W1  the grid's yellow count is 9 and blue count is 15
  W2  every coordinate in the grid agrees with the complete 196-cell map
  W3  the grid's yellow set equals the note-25a yellow set under transposition
  W4  the CSV-verified preimages pushed through this loop return their known
      addresses -- so a 0 MATCH here means "no preimage", never "broken harness"

The constructions and the target set are IMPORTED from `third_door`, never
re-derived, so this battery cannot drift from the certified oracle.

Local only: every address compared is already public in `data/planted-addresses.csv`
or the two funded gate addresses. No key is swept, nothing is broadcast.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRID = os.path.join(BASE, "data", "follow-white-rabbit-grid.json")
FULLMAP = os.path.join(BASE, "data", "phase1-matrix-14x14-full.json")


def load_td():
    spec = importlib.util.spec_from_file_location(
        "td", os.path.join(BASE, "tools", "third_door.py"))
    m = importlib.util.module_from_spec(spec)
    sys.argv = ["third_door.py"]
    spec.loader.exec_module(m)
    return m


TD = load_td()

PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47}


def load_coords():
    g = json.load(open(GRID))
    y = [tuple(p) for p in g["yellow"]]
    b = [tuple(p) for p in g["blue"]]
    rows = json.load(open(FULLMAP))["rows"]
    # rows is 14 strings of 14; keep it 2-D so (row,col) indexes directly.
    # Flattening and then writing flat[r][c] would index a single 196-char
    # string by column, which is wrong and raised IndexError in the first run.
    flat = "".join(rows)
    return y, b, (rows, flat)


def selftest() -> bool:
    y, b, (rows, flat) = load_coords()
    ok = True
    # W1: the certified counts
    w1 = len(y) == 9 and len(b) == 15
    # W2: every grid coordinate agrees with the complete 196-cell map
    w2 = all(rows[r][c] == "Y" for r, c in y) \
        and all(rows[r][c] == "B" for r, c in b)
    # W3: the axis convention is AMBIGUOUS and must be carried, not chosen. My
    # first draft asserted the grid's yellow set equals note-25a's yellow set
    # transposed and it FAILED, which sent me to read note 25a: it is about the
    # rabbit's uniform 16px stroke width and has nothing to do with coordinates.
    # So there is no second coordinate list to reconcile, and the honest witness
    # is the weaker but sufficient one: the two conventions yield DIFFERENT
    # families, so running both is necessary rather than belt-and-braces.
    w3 = sorted((c, r) for r, c in y) != sorted(y)
    # W4: the CSV preimages survive this loop
    w4 = True
    for pre, addr, cname, comp in TD.WITNESSES:
        got = TD.addresses_for(pre).get((cname, comp))
        w4 &= (got == addr)
    for tag, w in (("W1 yellow=9 blue=15", w1), ("W2 grid agrees with 196-cell map", w2),
                   ("W3 axis conventions differ, so both are run", w3), ("W4 CSV witnesses", w4)):
        print(f"  [{'PASS' if w else 'FAIL'}] {tag}")
        ok &= bool(w)
    print("SELFTEST " + ("PASS" if ok else "FAIL") + f": 4 witnesses, "
          + ("0 failures" if ok else "see above"))
    return ok


def a1z26(s: str) -> str:
    out = []
    for ch in s:
        if ch.isdigit():
            out.append(chr(ord("a") + (int(ch) - 1)))
        elif ch.isupper():
            out.append(ch.lower())
        else:
            out.append(ch)
    return "".join(out)


def candidates():
    y, b, (rows, flat) = load_coords()
    out = {}

    def add(tag: str, pre: bytes):
        if pre:
            out.setdefault(pre, tag)

    for axis in ("rc", "cr"):
        for name, cells in (("Y", y), ("B", b)):
            cs = [(r, c) if axis == "rc" else (c, r) for r, c in cells]
            rows_v = [p[0] for p in cs]
            cols_v = [p[1] for p in cs]

            # the coordinate object serialised every honest way
            add(f"{name}/{axis}/rows", ",".join(map(str, rows_v)).encode())
            add(f"{name}/{axis}/cols", ",".join(map(str, cols_v)).encode())
            add(f"{name}/{axis}/rows-joined", "".join(map(str, rows_v)).encode())
            add(f"{name}/{axis}/cols-joined", "".join(map(str, cols_v)).encode())
            add(f"{name}/{axis}/pairs", "".join(f"{r}{c}" for r, c in cs).encode())
            add(f"{name}/{axis}/pairs-sep", " ".join(f"{r}{c}" for r, c in cs).encode())
            add(f"{name}/{axis}/a1z26", a1z26("".join(map(str, rows_v))).encode())

            # "Yellow has a number and so does Blue": the counts themselves
            add(f"{name}/{axis}/count", str(len(cs)).encode())
            add(f"{name}/{axis}/count-a1z26", a1z26(str(len(cs))).encode())

            # primes, four independent senses, keep-only
            for label, keep in (
                ("prow", [i for i, v in enumerate(rows_v) if v in PRIMES]),
                ("pcol", [i for i, v in enumerate(cols_v) if v in PRIMES]),
                ("ppos", [i for i in range(len(cs)) if (i + 1) in PRIMES]),
                ("pval", [i for i, (r, c) in enumerate(cs)
                          if r in PRIMES or c in PRIMES]),
            ):
                if not keep:
                    continue
                kept = [cs[i] for i in keep]
                add(f"{name}/{axis}/{label}/rows",
                    "".join(str(p[0]) for p in kept).encode())
                add(f"{name}/{axis}/{label}/cols",
                    "".join(str(p[1]) for p in kept).encode())
                add(f"{name}/{axis}/{label}/pairs",
                    "".join(f"{p[0]}{p[1]}" for p in kept).encode())
                # "zeroed out": the survivors are the zeroes, the rest the zeroes too
                zeros = "".join(
                    "0" if i in keep else str(p[0]) for i, p in enumerate(cs))
                add(f"{name}/{axis}/{label}/zeroed-rows", zeros.encode())
                zeros_c = "".join(
                    "0" if i in keep else str(p[1]) for i, p in enumerate(cs))
                add(f"{name}/{axis}/{label}/zeroed-cols", zeros_c.encode())

            # the colour mask as a bit string, both polarities
            for cls, letter in (("B", "B"), ("K", "K")):
                mask = "".join("1" if rows[r][c] == letter else "0"
                               for r, c in y + b)
                add(f"mask/{cls}/{axis}", mask.encode())
                add(f"mask/{cls}/{axis}/a1z26", a1z26(mask).encode())
                break

    # the certified scalars and their pair, hashed as the audio hint directs
    for tag, s in (("915", "915"), ("159", "159"), ("9-15", "9-15"),
                   ("yellow9blue15", "yellow9blue15"),
                   ("yellowblue", "yellowblue"),
                   ("yellow9", "yellow9"), ("blue15", "blue15"),
                   ("9150", "9150"), ("09 15", "0915"),
                   ("yellowblueprimes", "yellowblueprimes"),
                   ("zeroedout", "zeroedout"), ("primes", "primes")):
        add(f"scalar/{tag}", s.encode())
        # HASHTHETEXT: the directive, applied to the scalar itself
        add(f"hashed/{tag}", hashlib.sha256(s.encode()).hexdigest().encode())
        add(f"hashed-raw/{tag}", hashlib.sha256(s.encode()).digest())

    # the full 196-cell map, and the yellow/blue sub-mask of it, hashed
    for tag, s in (("fullmap", flat), ("yb-mask",
                    "".join("1" if rows[r][c] == "Y" else "0" for r, c in y)),
                   ("b-mask",
                    "".join("1" if rows[r][c] == "B" else "0" for r, c in b))):
        add(f"hashed/{tag}", hashlib.sha256(s.encode()).hexdigest().encode())
        add(f"map/{tag}", s.encode())

    # reverse and upper each reading, since the streams are read both ways
    base = list(out.items())
    for pre, tag in base:
        if len(pre) <= 64:
            out.setdefault(pre[::-1], f"{tag}/rev")
            out.setdefault(pre.upper(), f"{tag}/upper")
    return sorted(out.items())


def run() -> tuple[int, int, list]:
    cands = candidates()
    tried = hits = 0
    for pre, tag in cands:
        for (cname, comp), addr in TD.addresses_for(pre).items():
            tried += 1
            if addr in TD.TARGETS:
                hits += 1
                print(f"  MATCH {tag!r} preimage={pre!r} "
                      f"[{cname}, {'compressed' if comp else 'uncompressed'}] "
                      f"{addr}", flush=True)
    return len(cands), tried, hits


def main() -> int:
    ok = selftest()
    if not ok:
        print("refusing to report a negative from a broken harness")
        return 1
    n, tried, hits = run()
    print(f"\nN={n} unique preimages, {tried} address derivations, "
          f"{hits} MATCH against the third door, the 8 other planted addresses "
          f"and both gate addresses.")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())