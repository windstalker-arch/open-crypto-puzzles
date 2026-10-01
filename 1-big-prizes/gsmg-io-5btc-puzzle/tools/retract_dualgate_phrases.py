#!/usr/bin/env python3

# DO NOT RERUN. One-shot migration for the two-gate retraction (2026-10-01), kept only as
# the record of what was tried. Two known defects, both of which damaged text and both
# repaired before the commit: (1) the replacement strings below contain a MALFORMED
# ELLIPSIS, "17ucy1K9.." (two dots) instead of "...", which is what truncated ellipses
# and rewrote the alphabet range {a..i} to {a.i} across 243 + 1,378 lines; (2) this
# script rewrote ITS OWN SOURCE while running. Superseded by _pass3.py.
"""Retract the two-funded-gates premise ledger-wide (R-DUALITEPROV-2026-10-01).

`17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa` is the creator's halving-withdrawal
address (2.5 BTC on 2020-05-11 + 1.25 BTC on 2024-04-24, both sourced from
the prize address, never spent) -- not a second prize gate.

CRITICAL DISTINCTION: this rewrites only STATUS ASSERTIONS (a gate being
open / funded / live / a prize target). It deliberately PRESERVES TEST
RECORDS ("NO MATCH both gates", "witness: oracle_dualite.py PASS"),
because those remain true: candidates really were tested against both
addresses. Rewriting those would falsify the experimental record.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "analysis" / "tested.md"

# Files where a bare address mention is documentation of on-chain history,
# not a claim that two gates exist. Left alone.
SKIP_BASENAMES = {"puzzle.json"}

# (pattern, replacement) applied to STATUS assertions only.
# Ordered most-specific first.
STATUS_RULES = [
    # --- explicit "the funded gate remains open" family ---
    (r"the funded gate remains open", "the funded gate remains open"),
    (r"the funded gate remains open", "the funded gate remains open"),
    (r"the funded gate remains open", "the funded gate remains open"),
    (r"the funded gate remains OPEN", "the funded gate remains OPEN"),
    (r"the funded gate remains OPEN", "the funded gate remains OPEN"),
    (r"the funded gate remains funded", "the funded gate remains funded"),
    (r"the funded gate remains live and funded", "the funded gate remains live and funded"),
    (r"the funded gate re-verified open", "the funded gate re-verified open"),
    (r"the funded gate re-verified funded", "the funded gate re-verified funded"),
    (r"the funded gate verified funded", "the funded gate verified funded"),
    (r"the funded gate verified open", "the funded gate verified open"),
    # --- "the funded gate unchanged / intact" = status ---
    (r"the funded gate unchanged", "the funded gate unchanged"),
    (r"the funded gate intact and open", "the funded gate intact and open"),
    (r"the funded gate intact/open", "the funded gate intact/open"),
    (r"the funded gate unchanged, nothing opened", "the funded gate unchanged, nothing opened"),
    (r"the funded gate still open", "the funded gate still open"),
    (r"the funded gate verified funded", "the funded gate verified funded"),
    (r"the funded gate remains open", "the funded gate remains open"),
    (r"funded gate unspent = GATE OPEN", "funded gate unspent = GATE OPEN"),
    # --- "halving-withdrawal address" as a prize noun ---
    (r"halving-withdrawal address \(3\.75 BTC\) is now oracle-testable",
     "17ucy1K9.. is a halving-withdrawal address, not a prize target; only the funded gate is a prize"),
    (r"the halving-withdrawal address", "the halving-withdrawal address"),
    (r"halving-withdrawal address", "halving-withdrawal address"),
    # --- "both gate addresses" as a NOUN phrase in status sentences ---
    (r"negative on both gate addresses", "negative on both gate addresses"),
    (r"against both gate addresses", "against both gate addresses"),
    (r"on both gate addresses", "on both gate addresses"),
    (r"neither gate address", "neither gate address"),
    (r"either gate address", "either gate address"),
    (r"the funded gate is still funded and unspent (17ucy1K9.. is a halving-withdrawal address, never spent)",
     "the funded gate is still funded and unspent (17ucy1K9.. is a halving-withdrawal address, never spent)"),
    (r"both gate addresses", "both gate addresses"),
    # --- capitalised sentence-initial leftovers ---
    (r"\*\*the funded gate remains open\.\*\*", "**The funded gate remains open.**"),
    (r"funded/unspent = the funded gate remains open",
     "funded/unspent = the funded gate remains open"),
]


def scrub(text: str) -> tuple[str, int]:
    total = 0
    for pat, rep in STATUS_RULES:
        text, n = re.subn(pat, rep, text)
        total += n
    # Tidy the artefacts my own rules can create: doubled periods, and a
    # lowercase sentence start left behind by a rule that fired mid-sentence.
    text = re.sub(r"\.\.", ".", text)
    text = re.sub(r"the funded gate remains open\. the funded gate remains open\.",
                  "the funded gate remains open.", text)
    return text, total


def main() -> int:
    changed = 0
    for path in sorted(ROOT.rglob("*")):
        if path.suffix not in {".md", ".py"} or not path.is_file():
            continue
        if path.name in SKIP_BASENAMES or "tested.md" not in path.name and path.suffix == ".json":
            continue
        try:
            src = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        out, n = scrub(src)
        if n and out != src:
            path.write_text(out, encoding="utf-8")
            print(f"{n:4d}  {path.relative_to(ROOT)}")
            changed += n
    print(f"\ntotal status-assertion rewrites: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())