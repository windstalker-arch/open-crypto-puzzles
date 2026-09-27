#!/usr/bin/env python3
"""Re-extract and render the LVL5 mini-hint from crypto5fix.png at pixel level.

Motivation: the folder's analysis had the mini-hint only as a transcription
("-1*x + 64/x"). This script independently re-extracts the actual pixels of the
2021 addition (2 white lines + the bottom-left mini-hint) from the image and
renders them as ASCII so the glyphs can be re-read directly. It confirms the
geometry byte-perfect against data/rectangle-measurements.csv (already certified
against the author's MATLAB script) and exposes structure the transcription
dropped: the mini-hint is made of 4 stacked dot-matrix formula lines PLUS a
5-row-high digit band (rows ~926-930) PLUS lower glyphs (rows ~913-923, 933-942).

Usage:
  python3 tools/extract_minihint.py      # render the whole hint region

No private keys are involved; this is read-only image analysis of the public clue.
"""
from PIL import Image
import numpy as np
import os

IMG = os.path.join(os.path.dirname(__file__), "..", "clues", "crypto5fix.png")
ORIG = os.path.join(os.path.dirname(__file__), "..", "clues", "crypto5.png")


def render(a, r0, r1, c0, c1, step=1, label=""):
    print("\n=== %s (rows %d-%d, cols %d-%d) ===" % (label, r0, r1, c0, c1))
    for y in range(r0 - 1, r1, step):
        line = ""
        for x in range(c0 - 1, c1, step):
            line += "#" if a[y, x] == 255 else "."
        print(line)


def main():
    a = np.array(Image.open(IMG).convert("L"))
    a0 = np.array(Image.open(ORIG).convert("L"))
    assert a.shape == a0.shape, "image dimension mismatch"

    d = (a != a0)
    ys, xs = np.where(d)
    print("differences vs original:", int(d.sum()),
          "rows %d-%d cols %d-%d" % (ys.min(), ys.max(), xs.min(), xs.max()))

    print("\n-- White line under rectangle ~40 (kitchen sink check -- length) --")
    render(a, 543, 544, 679, 697, 1, "line under #40")
    render(a, 729, 730, 565, 572, 1, "line under #53")

    print("\n-- Mini-hint, formula lines 1-4 (bottom-left corner) --")
    render(a, 806, 872, 45, 79, 1, "formula lines")

    print("\n-- Mini-hint, upper glyph (diagonal) --")
    render(a, 912, 924, 52, 74, 1, "upper glyph")

    print("\n-- Mini-hint, digit band row (5 rows) -> 14 glyphs --")
    render(a, 926, 931, 40, 102, 1, "digit band")

    print("\n-- Mini-hint, lower glyph --")
    render(a, 932, 943, 52, 74, 1, "lower glyph")


if __name__ == "__main__":
    main()
