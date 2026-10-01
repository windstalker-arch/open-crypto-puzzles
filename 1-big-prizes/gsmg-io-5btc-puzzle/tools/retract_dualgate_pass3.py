#!/usr/bin/env python3

# DO NOT RERUN. One-shot migration pass 3 (2026-10-01) - the exact-string pass that
# actually completed the retraction. Safe because its patterns are exact strings with no
# metacharacters. Idempotent: rerunning it is a no-op.
"""Pass 3: the residual status assertions pass 2's proximity guard skipped.

Pass 2 guarded rewrites against nearby test-record keywords, which was too
broad: real status assertions like "Both gates remain open; no candidate X
introduced" sit right next to "candidate" and were wrongly preserved.

This pass uses exact, anchored patterns instead of proximity heuristics, so
each rewrite is deterministic:

  STATUS (false, two live prize gates claimed)  -> singular
  RECORDS (true, two addresses were queried)    -> untouched, never listed here
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXACT = [
    # capitalised, sentence-initial
    ("Both funded gates remain OPEN", "The funded gate remains OPEN"),
    ("Both funded gates remain open", "The funded gate remains open"),
    ("Both gates remain OPEN", "The funded gate remains OPEN"),
    ("Both gates remain open", "The funded gate remains open"),
    ("Both gates remain", "The funded gate remains"),
    ("Both funded gates open", "The funded gate remains open"),
    ("Both gates open", "The funded gate remains open"),
    ("Both gates unchanged", "The funded gate unchanged"),
    ("Both gates intact", "The funded gate intact"),
    ("Both funded gates unchanged", "The funded gate unchanged"),
    ("Both funded gates are", "The funded gate is"),
    ("Both funded/unspent = BOTH GATES OPEN", "funded/unspent = GATE OPEN"),
    # markdown-bold variants
    ("** Both gates unchanged", "**The funded gate unchanged"),
    ("** Both gates", "**The funded gate"),
    ("**Both funded gates remain open", "**The funded gate remains open"),
    # lowercase mid-sentence
    ("both funded gates remain open", "the funded gate remains open"),
    ("both gates remain open", "the funded gate remains open"),
    ("both gates remain OPEN", "the funded gate remains OPEN"),
    ("both gates open", "the funded gate remains open"),
    ("both gates unchanged", "the funded gate unchanged"),
    ("both gates intact", "the funded gate intact"),
]


def main() -> int:
    total = 0
    for path in sorted(ROOT.rglob("*")):
        if path.suffix not in {".md", ".py"} or not path.is_file():
            continue
        if path.name.startswith("retract_dualgate"):
            continue
        try:
            src = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        out = src
        hits = 0
        for old, new in EXACT:
            n = out.count(old)
            if n:
                out = out.replace(old, new)
                hits += n
        if out != src:
            path.write_text(out, encoding="utf-8")
            print(f"{hits:4d}  {path.relative_to(ROOT)}")
            total += hits
    print(f"\ntotal rewrites: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())