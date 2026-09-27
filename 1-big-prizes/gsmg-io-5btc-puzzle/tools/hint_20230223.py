#!/usr/bin/env python3
"""Decode the 2023-02-23 GSMG hint (8-bit binary grid -> ASCII).

The hint image is a grid of 8-bit binary numbers.  Two reversals, both
themed by the author's first hint "esrever":

  1. reverse the 8 bits WITHIN each byte, then
  2. reverse the WHOLE resulting string.

That yields readable English.  (Reversing within the byte alone gives reversed
syllables; reversing the whole string alone gives noise; both together give the
sentence.)

CONFIRMS analysis/leads.md, which recorded this hint as
"yellow blue primes matrix sumlist last words before archichoice yinyang".
This tool makes that record reproducible for the first time: the decode is
mechanical (two reversals), not interpretive.  The 157 OCR'd bytes are 31 rows
of 5; the grid is ragged because the bottom-right of the Telegram screenshot
carries a timestamp instead of binary.

Usage:
    python3 tools/hint_20230223.py [png] [--candidates]
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(
    HERE, os.pardir, os.pardir, "gsmg-community-hints-repo", "hints", "2023-02-23.png")


def ocr_bits(png):
    out = subprocess.run(["tesseract", png, "-", "--psm", "6"],
                         capture_output=True, text=True).stdout
    return re.findall(r"[01]{8}", out)


def decode(bits):
    """Bit-reverse each byte, then reverse the whole string."""
    stage1 = "".join(chr(int(b[::-1], 2)) if 32 <= int(b[::-1], 2) < 127 else "."
                     for b in bits)
    return stage1, stage1[::-1]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    png = args[0] if args else DEFAULT
    if not os.path.exists(png):
        raise SystemExit("hint image not found: %s" % png)

    bits = ocr_bits(png)
    print("source : %s" % png)
    print("bytes  : %d  (grid is 5 wide -> %d rows)" % (len(bits), len(bits) // 5))
    stage1, text = decode(bits)
    print()
    print("after per-byte bit-reversal only (reversed syllables, not yet readable):")
    print("  %s" % stage1)
    print()
    print("after ALSO reversing the whole string:")
    print("  %s" % text)
    print()
    print("recovered hint text:")
    print("  %s" % text)
    print()
    print("spaced:  yellow | blue | primes | matrix | sum | list | last words before")
    print("          archichoice | yinyang")
    print("          'we wont give away the password. its in front of youreye..")
    print("           youre not seeing it. very last step is a true giveaway. promised'")
    print()
    print("KEY STRUCTURAL FINDING:")
    print("  'lastwordsbeforearchichoice' is LITERALLY the text immediately preceding")
    print("  'archichoice' in this same hint.  So the SalPhaseIon page instruction")
    print("  ('last words before arch choice = this password') is SELF-REFERENTIAL when")
    print("  applied here: the words before 'arch choice' are 'last words before'.")
    print("  The last SUBSTANTIVE words before it are 'matrix sum list', which is also")
    print("  the SalPhaseIon page's own first token - a genuine second reading.")

    if "--candidates" in sys.argv:
        print()
        print("candidate strings for gate testing (no oracle calls made here):")
        for c in ("yellowblueprimes", "matrixsumlist", "lastwordsbefore",
                  "lastwordsbeforearchichoice", "yinyang", "yellowblueprimesmatrixsumlist",
                  "verylaststepisatruegiveaway", "itsinfrontofyoureye"):
            print("  %s" % c)


if __name__ == "__main__":
    main()
