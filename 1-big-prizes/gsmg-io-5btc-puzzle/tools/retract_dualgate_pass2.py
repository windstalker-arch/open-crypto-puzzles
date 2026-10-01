#!/usr/bin/env python3

# DO NOT RERUN. One-shot migration pass 2 (2026-10-01), kept as the record of a failed
# approach. Known defect: its proximity guard (see the test-record guard below) skipped
# rewrites near words like "candidate"/"escrow", so REAL status assertions such as
# "Both gates remain open; no candidate X introduced" survived unretracted. Superseded
# by _pass3.py.
"""Pass 2: finish the status-assertion retraction (R-DUALITEPROV-2026-10-01).

Pass 1 handled the phrasings it anticipated. This handles the residual
STATUS assertions, and -- critically -- leaves TEST RECORDS alone.

KEEP (true): "0 MATCH both gates", "NEGATIVE both gates", "0 MATCH on both
gates", "witness ... both gates", "escrow ... both gates" -- candidates
really were tested against both addresses, so both addresses really were
queried. These stay verbatim.

REWRITE (false): "The funded gate remains open", "The funded gate remains open",
"The funded gate remains open", "Funded gate intact (...)", "Both funded gates
unchanged" -- these assert that TWO PRIZE GATES exist and are live, which
R-DUALITEPROV disproves.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Applied in order; each is a status assertion.
RULES = [
    # sentence-initial capitalised forms
    (r"\*\*The funded gate remains open", "**The funded gate remains open"),
    (r"The funded gate remains open", "The funded gate remains open"),
    (r"The funded gate remains open", "The funded gate remains open"),
    (r"The funded gate remains open\b", "The funded gate remains open"),
    (r"The funded gate remains open\b", "The funded gate remains open"),
    (r"The funded gate unchanged", "The funded gate unchanged"),
    (r"The funded gate unchanged, nothing opened", "The funded gate unchanged, nothing opened"),
    # "intact (balances)" forms -- these assert two live funded gates
    (r"Funded gate intact \(1GSMG1JC9 = ?125,?635,?374 sat? / ?17ucy1K9[^)]*\)",
     "Funded gate intact (1GSMG1JC9 = 125,635,374 sat); 17ucy1K9... is the creator's "
     "halving-withdrawal address (never spent), not a second gate"),
    (r"Funded gate intact \(`tools/check_escrows[^)]*\)",
     "Funded gate intact (`tools/check_escrows`)"),
    (r"Funded gate intact \(1GSMG1JC9 =",
     "Funded gate intact (1GSMG1JC9 ="),
    (r"Funded gate intact\b", "Funded gate intact"),
    # lowercase mid-sentence forms
    (r"the funded gate remains open", "the funded gate remains open"),
    (r"the funded gate remains funded", "the funded gate remains funded"),
    (r"the funded gate intact", "the funded gate intact"),
    (r"the funded gate remains open", "the funded gate remains open"),
    (r"the funded gate unchanged", "the funded gate unchanged"),
    (r"the funded gate remains open", "the funded gate remains open"),
    # escrow-status sentences
    (r"Escrow check rc=0, both gates OK",
     "Escrow check rc=0, funded gate OK (17ucy1K9... is a halving-withdrawal address)"),
    (r"escrow check rc=0, both gates OK", "escrow check rc=0, funded gate OK"),
]

# Test-record guards: if a matched region sits inside one of these, revert it.
GUARD = re.compile(
    r"(MATCH|NEGATIVE|NO MATCH|candidate|cands|tested|witness|attempts|"
    r"escrow check|rc=0|stdin|--selftest|checked against|derivation|"
    r"oracle|pw |password|keystream|certified negative)",
    re.I,
)


def main() -> int:
    total = 0
    for path in sorted(ROOT.rglob("*")):
        if path.suffix not in {".md", ".py"} or not path.is_file():
            continue
        if path.name == "retract_dualgate_phrases.py":
            continue
        try:
            src = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        out = src
        for pat, rep in RULES:
            def _sub(m, rep=rep):
                # Guard: skip if this occurrence is a test record.
                window = out[max(0, m.start() - 60):m.end() + 60]
                return m.group(0) if GUARD.search(window) else m.expand(rep)
            out = re.sub(pat, _sub, out)
        if out != src:
            n = sum(1 for a, b in zip(src.split("\n"), out.split("\n")) if a != b)
            path.write_text(out, encoding="utf-8")
            print(f"{n:4d} lines  {path.relative_to(ROOT)}")
            total += n
    print(f"\nlines touched: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())