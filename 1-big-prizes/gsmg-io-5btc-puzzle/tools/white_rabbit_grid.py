#!/usr/bin/env python3
"""
R-WRGRID (2026-09-27): extract + certify the phase-1 14x14 whole-pixel matrix
from EITHER of its two pixel-exact renderings, and prove the section-120 read.

  A) clues/puzzle.png                 1048x1556  cell=75  x0=0 y0=0
  B) img/follow_the_white_rabbit.png   350x350   cell=25  x0=0 y0=0

Both yield the IDENTICAL 196-cell colour grid and the identical read
`gsmg.io/theseedisplanted` via CCW spiral from top-left, B/K=1 W/Y=0, MSB-first.

Why this file exists: data/follow-white-rabbit-grid.json stores only the blue
(15) and yellow (9) lists. That is LOSSY - the bit assignment is black-vs-white
(B/K=1, W/Y=0), so the 87 black cells carry 85% of the 1-bits and the phase-1
seed is NOT derivable from the blue/yellow file alone. See tested.md R-WRGRID.

Usage:  python3 tools/white_rabbit_grid.py [--write-full]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

N = 14
SEED = b"gsmg.io/theseedisplanted"

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def classify(px):
    """4-colour palette: blue 63,72,204 / yellow 255,242,0 / white ~255 / black ~0."""
    r, g, b = int(px[0]), int(px[1]), int(px[2])
    if b > 150 and r < 120 and g < 120:
        return "B"
    if r > 200 and g > 200 and b < 100:
        return "Y"
    if r > 200 and g > 200 and b > 200:
        return "W"
    return "K"


def extract(path, cell, x0=0, y0=0):
    """Classify each cell by its DOMINANT colour, not by its centre pixel.

    R-GRID76 (2026-10-04): the centre-pixel rule this function used to apply
    misread exactly one cell, (r=7, c=6). That cell is 76% white / 24% black,
    because a drawn outline stroke passes through its middle; sampling the
    centre therefore returned black for a white cell. It is spiral bit 193,
    which lies in the 4-bit tail BEYOND the 24-byte seed slug (bits 0..191), so
    the `gsmg.io/theseedisplanted` witness cannot see it and the error passed
    unnoticed into data/phase1-matrix-14x14-full.json.

    Dominant colour is the correct rule, and it is the rule the seed itself
    certifies: of the 7 cells the drawn figure crosses, the 3 that fall inside
    the seed-covered range (spiral 172, 184, 187) are ALL white under dominant
    colour, and flipping any of them to black breaks the slug. The figure is
    decoration drawn over a white background, not part of the encoding.

    Both renderings agree exactly on the disputed cell -- 475/625 and 4275/5625
    white, a perfectly scale-invariant 3x stroke -- so this is not an artefact
    of one image. Near-white (254,254,254) still classifies as W, which is what
    the (r=7, c=4) nest cell requires.
    """
    im = Image.open(path).convert("RGB")
    a = np.asarray(im, dtype=np.uint8)
    H, W = a.shape[:2]
    grid = []
    for r in range(N):
        row = []
        for c in range(N):
            y0c, y1c = y0 + cell * r, min(y0 + cell * r + cell, H)
            x0c, x1c = x0 + cell * c, min(x0 + cell * c + cell, W)
            block = a[y0c:y1c, x0c:x1c].reshape(-1, 3)
            if block.size == 0:
                row.append("?")
                continue
            # most frequent exact RGB triple in the cell wins
            vals, counts = np.unique(block, axis=0, return_counts=True)
            row.append(classify(vals[int(counts.argmax())]))
        grid.append("".join(row))
    return grid


def ccw_spiral():
    """CCW from top-left == DOWN the left column first. 1-of-8: the CW variant is garbage."""
    order, top, bot, left, right = [], 0, N - 1, 0, N - 1
    while top <= bot and left <= right:
        for r in range(top, bot + 1):
            order.append((r, left))
        left += 1
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


def read(grid):
    """B/K = 1, W/Y = 0; 196 bits packed MSB-first -> 24 bytes."""
    bits = "".join("1" if grid[r][c] in "BK" else "0" for r, c in ccw_spiral())
    padded = bits + "0" * ((-len(bits)) % 8)
    return bits, bytes(int(padded[i:i + 8], 2) for i in range(0, len(padded), 8))


def render(grid):
    counts = {ch: sum(row.count(ch) for row in grid) for ch in "BKWY"}
    out = ["  colour grid (B=blue K=black W=white Y=yellow):"]
    out += ["   %2d  %s" % (i, r) for i, r in enumerate(grid)]
    out.append("  counts: %s  total=%d" % (counts, sum(counts.values())))
    return "\n".join(out)


def _candidate_roots():
    """Where to hunt for the follow_the_white_rabbit renderings, in order.

    Override with GSMG_SEARCH_ROOTS (os.pathsep separated). The default is every
    ancestor of this puzzle folder up to $HOME, plus a gsmg/ and briefcase/
    sibling at each level, which is what the three hardcoded home-directory paths
    used to name without pinning the script to one machine. The walk stops at
    $HOME so it never recurses over the whole filesystem.
    """
    env = os.environ.get("GSMG_SEARCH_ROOTS")
    if env:
        return [p for p in env.split(os.pathsep) if p]
    home = os.path.expanduser("~")
    roots = []
    here = REPO
    while True:
        roots.append(here)
        roots.append(os.path.join(here, "gsmg"))
        roots.append(os.path.join(here, "briefcase"))
        if here == home:
            break
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent
    return roots


def main():
    srcs = [
        ("clues/puzzle.png", 75, os.path.join(REPO, "clues", "puzzle.png")),
        ("follow_the_white_rabbit.png", 25, None),
    ]
    for name, cell, fixed in srcs:
        if fixed is None:
            hits = []
            for root in _candidate_roots():
                for dp, _dn, fn in os.walk(root):
                    for f in fn:
                        if "follow_the_white_rabbit" in f and f.lower().endswith(".png"):
                            hits.append(os.path.join(dp, f))
            if hits:
                srcs[1] = (name, cell, sorted(hits)[0])

    grids = {}
    for name, cell, path in srcs:
        if not path or not os.path.exists(path):
            print("SKIP %s (not found)" % name)
            continue
        grid = extract(path, cell)
        grids[name] = grid
        bits, decoded = read(grid)
        print("=" * 72)
        print("%s   cell=%dpx   %s" % (name, cell, path))
        print(render(grid))
        print("  ones=%d  read -> %r" % (bits.count("1"), decoded[:24]))
        print("  WITNESS %s" % ("PASS" if decoded[:len(SEED)] == SEED else "FAIL"))

    if len(grids) == 2:
        (n1, g1), (n2, g2) = grids.items()
        same = g1 == g2
        print("=" * 72)
        print("pixel-exact agreement across the two renderings: %s" % same)
        if not same:
            for r in range(N):
                for c in range(N):
                    if g1[r][c] != g2[r][c]:
                        print("   DIFF (%d,%d) %s vs %s" % (r, c, g1[r][c], g2[r][c]))

    if "--write-full" in sys.argv and grids:
        name = "follow_the_white_rabbit.png"
        grid = grids.get(name) or next(iter(grids.values()))
        dest = os.path.join(REPO, "data", "phase1-matrix-14x14-full.json")
        payload = {
            "_row": "R-WRGRID (2026-09-27); CORRECTED at (7,6) by R-GRID76 (2026-10-04)",
            "_note": ("COMPLETE 196-cell colour map. follow-white-rabbit-grid.json is LOSSY: "
                      "it stores only blue+yellow, but the bit assignment is B/K=1 W/Y=0, so the "
                      "black cells carry 85%% of the 1-bits. Use this file to reproduce the read."),
            "_read": "CCW spiral from top-left (down the left column first), B/K=1 W/Y=0, MSB-first",
            "_seed": SEED.decode(),
            "_provenance": ("identical in all 196 cells to clues/puzzle.png (cell=75) and to the "
                            "recovered img/follow_the_white_rabbit.png (cell=25)"),
            "_correction_R_GRID76": (
                "The 2026-09-27 version of this file had K=87 W=85 (dark total 102) because "
                "extract() sampled each cell's CENTRE PIXEL. Cell (7,6) is 76% white / 24% black "
                "-- a drawn outline stroke crosses its centre -- so it was misread as black. "
                "extract() now uses the DOMINANT colour. Effect: exactly one cell changes, "
                "(7,6) K->W; counts become K=86 W=86 (a perfect black/white balance, which is "
                "what community issue #106 reported), the B/K=1 dark total becomes 101, and the "
                "row/col sum lists become 610876654997879 / 8108108736759668, matching #106 "
                "exactly on all 28 values. The gsmg.io/theseedisplanted witness does NOT "
                "discriminate: (7,6) is spiral bit 193, inside the 4-bit tail beyond the 24-byte "
                "slug (bits 0..191). Those 4 previously-unchecked bits are now 0000. The same "
                "centre-pixel error is present in the archived official grid "
                "follow_the_white_rabbit_grid_14x14.json, so that file is wrong at this cell too."),
            "legend": {"B": "blue 63,72,204", "K": "black 0,0,0", "W": "white 255,255,255",
                       "Y": "yellow 255,242,0"},
            "rows": grid,
        }
        with open(dest, "w") as fh:
            json.dump(payload, fh, indent=1)
        print("wrote %s" % dest)


if __name__ == "__main__":
    main()
