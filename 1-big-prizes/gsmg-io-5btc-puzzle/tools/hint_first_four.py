#!/usr/bin/env python3
"""Transcribe the four first hints of the GSMG puzzle, reproducibly.

The published page ends its hidden message with the directive
`four first hints is your last command`, and this folder had only ever carried a
guess at what those four hints say (`leads.md` records the "first hint" password
as `firsttint`, which is an interpretation, not a reading).  The four earliest
hint screenshots are transcribed here so the guess can be checked against the
actual text.

The four earliest files in the community hints folder, in filename order:

    2020-01-14-roses-are-red.png
    2020-02-20-decentraland.jpg
    2020-04-08.png
    2020-05-11.png

Note on ordering: the folder is a community mirror of a Telegram group, so
"earliest by filename" is the earliest *mirrored* hint, which is the best
available proxy for the author's publication order.  It is not proof of the
author's order, and the derived instruction depends on that order.

Usage:
    python3 tools/hint_first_four.py            # transcribe all four
    python3 tools/hint_first_four.py --cmds     # also list candidate commands
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HINTS = os.path.join(HERE, os.pardir, os.pardir, "gsmg-community-hints-repo", "hints")

FOUR = [
    "2020-01-14-roses-are-red.png",
    "2020-02-20-decentraland.jpg",
    "2020-04-08.png",
    "2020-05-11.png",
]

# Words that read as instructions to the solver rather than as prose.
COMMANDY = re.compile(
    r"\b(type|press|go back|go to|enter|start|help|open|follow|use|read|"
    r"look|see|find|click|select|choose)\b", re.I)


def ocr(path, psm=6):
    r = subprocess.run(["tesseract", path, "-", "--psm", str(psm)],
                       capture_output=True, text=True).stdout
    lines = [ln.strip() for ln in r.splitlines() if ln.strip()]
    return lines


def main():
    for name in FOUR:
        path = os.path.join(HINTS, name)
        if not os.path.exists(path):
            raise SystemExit("missing hint image: %s" % path)
        print("=" * 72)
        print(name)
        print("=" * 72)
        for psm in (6, 4):
            lines = ocr(path, psm)
            if psm == 6 or len(lines) < 2:
                for ln in lines:
                    print("   %s" % ln)
        print()

    if "--cmds" in sys.argv:
        print("=" * 72)
        print("instruction-shaped words present in the four hints")
        print("=" * 72)
        for name in FOUR:
            text = " ".join(ocr(os.path.join(HINTS, name), 6))
            hits = sorted({m.group(0).lower() for m in COMMANDY.finditer(text)})
            print("  %-34s %s" % (name, ", ".join(hits)))
        print()
        print("Open question, not answered here: the page's directive is")
        print("'four first hints is your last command'. The only literal commands")
        print("in the four are in hint 2, which is an in-game sign reading")
        print("'Type /help for info about controls' and 'Press E to enter and start'.")
        print("Whether the intended 'last command' is '/help', 'E', or the last")
        print("instruction-word of hint 1 ('Go back to the first puzzle piece') is")
        print("NOT decided by this transcription, and nothing here has been sent to")
        print("the gate. 0 oracle calls.")


if __name__ == "__main__":
    main()
