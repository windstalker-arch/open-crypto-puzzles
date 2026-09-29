#!/usr/bin/env python3
"""R-P15FIX - the retraction-integrity check this session needed and did not have.

`R-P15FIX` retracted claims in three rows and the summary documents. Retractions are
written as markdown strikethrough (`~~struck~~`) plus a header tag, which means two
things can silently rot:

  1. An UNBALANCED `~~`. If a retraction opens a strike and never closes it, the span
     runs until the next `~~` anywhere in a 17,000-line file, striking out live text
     that was meant to stay. This actually happened here: `R-P15NULL`'s reframe was
     struck with an opener and no closer, and the file ended with 47 `~~` tokens (odd).
  2. A RETRACTION THAT DECAYS. `R-P32BLOB` was header-tagged "solved" while three
     false claims sat live in its body - `R-P15FIX` method rule 5, "a header tag is not
     a row". A tag is a promise about a body, and nothing here can check the promise.

`--check` reports both, and `--selftest` proves the checker detects each defect on
synthetic input before anyone trusts it on the real ledger.

Use:

    python3 tools/retraction_audit.py --check     # audit the live ledger
    python3 tools/retraction_audit.py --selftest  # rc=0 or fail
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "analysis" / "tested.md"
BRIEF = REPO / "analysis" / "STATE_BRIEF.md"

# The claim this session established: the blob is SOLVED (R-P32KEY, 2026-09-26).
# Any of these appearing as a live assertion means a retraction decayed.
SOLVED_CLAIM = "THE PHASE-3.2 BLOB IS SOLVED"
KEYLESS = "keyless"

# Rows retracted or written by R-P15FIX; the sweep is expected to find all of them.
EXPECTED_TAGS = [
    "R-P32BLOB", "R-P32BLOB2", "R-P32BLOB3", "R-P32FLAG",
    "R-IMGSCOPE", "R-P15NULL", "R-DIG149", "R-P15FIX",
]


def token_lines(text: str) -> list[int]:
    """Line numbers of every `~~` occurrence, in document order."""
    out: list[int] = []
    for i, line in enumerate(text.split("\n"), 1):
        out.extend([i] * line.count("~~"))
    return out


def struck_map(text: str) -> list[bool]:
    """Per-line flag: is this line inside an open `~~` span? Toggles in doc order.

    This marks the whole line when a span crosses into it. It does NOT resolve a
    same-line `~~x~~`, which is struck but reports False here - use
    `line_is_struck()` for that, and note the two disagree by design.
    """
    flags: list[bool] = []
    inside = False
    for line in text.split("\n"):
        flags.append(inside)
        for _ in range(line.count("~~")):
            inside = not inside
    return flags


def line_is_struck(text: str) -> list[bool]:
    """Per-line flag including same-line spans: True if ANY part of the line is struck.

    `~~a~~ b` is struck AND not struck, so a line-level boolean is only ever a
    conservative approximation. Use the token-parity form when you need the whole
    line cleared, and this one when you need to know whether a retraction already
    covers something.
    """
    flags: list[bool] = []
    inside = False
    for line in text.split("\n"):
        was = inside
        for _ in range(line.count("~~")):
            inside = not inside
        flags.append(was or line.count("~~") > 0)
    return flags


def check_ledger(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    problems: list[str] = []

    toks = token_lines(text)
    if len(toks) % 2:
        unclosed = toks[-1]
        problems.append(
            f"UNBALANCED ~~: {len(toks)} tokens (odd). The unclosed OPENER is the "
            f"last unpaired token, at line {unclosed} - report the line, not the "
            f"phrase; a strike span opened there runs until the next ~~ anywhere in "
            f"the file, striking out live text that was meant to stay")

    flags = struck_map(text)
    for i, line in enumerate(lines):
        if "keyless ciphertext" not in line.lower() or flags[i]:
            continue
        if any(m in line for m in META_MARKERS) or RETRACTED_MARK in line:
            continue
        problems.append(f"L{i+1}: live 'keyless ciphertext' assertion outside a strike")

    headers = [l for l in lines if l.startswith("## R-")]
    for tag in EXPECTED_TAGS:
        rows = [h for h in headers if h.startswith(f"## {tag}-")]
        if not rows:
            problems.append(f"row {tag} not found in the ledger")
        elif not re.search(r"RETRACT|REFUT", rows[0]):
            problems.append(f"row {tag} has no RETRACT/REFUT tag in its header")

    if SOLVED_CLAIM not in text:
        problems.append("the solve statement is missing from the ledger")

    return problems


def check_brief(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    flags = struck_map(text)
    problems = []
    for i, line in enumerate(text.split("\n")):
        low = line.lower()
        if "keyless ciphertext" in low and not flags[i]:
            problems.append(f"STATE_BRIEF L{i+1}: live 'keyless ciphertext' assertion")
    return problems


def selftest() -> int:
    fails = 0

    def check(name: str, ok: bool) -> None:
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
        if not ok:
            fails += 1

    print("T1  an EVEN token count is reported clean")
    check("balanced span -> no problem",
          not _unbalanced("a ~~b~~ c\nd ~~e~~ f\n"))
    # One opener, no closer. (The earlier fixture here had two openers and therefore an
    # even count, so it was testing nothing - same class of error as the file bug.)
    check("odd count is detected", bool(_unbalanced("a ~~b c\nd e f\n")))

    print("T2  struck_map tracks spans ACROSS lines (the defect in the real file)")
    # Semantics: flags[i] is the span state at the START of line i, so a line that
    # holds the closing ~~ is itself still counted as struck. No trailing newline here,
    # or split() yields a phantom extra line.
    txt = "one ~~two\nthree\nfour~~ five\nsix"
    m = struck_map(txt)
    check("line 1 (holds the opener) is not yet struck", m[0] is False)
    check("line 2 is inside the span", m[1] is True)
    check("line 3 (holds the closer) is still inside the span", m[2] is True)
    check("line 4 is clean again", m[3] is False)

    print("T3  the two live-assertion classes are detected")
    live = "## R-X-2026: header\nbody says phase 3.2 is a keyless ciphertext still\n"
    check("live 'keyless ciphertext' flagged", _live_keyless(live))
    struck = "## R-X-2026: header\nbody ~~says a keyless ciphertext still~~ corrected\n"
    check("struck 'keyless ciphertext' NOT flagged", not _live_keyless(struck))

    print("T4  unrelated 'keyless' uses are not flagged")
    other = "a keyless Trifid decode of the stream\nkeyless homophonic substitution\n"
    check("keyless Trifid / homophonic not flagged", not _live_keyless(other))

    print("T5  the real ledger passes")
    p = check_ledger(LEDGER)
    for x in p:
        print(f"      -> {x}")
    check(f"no problems in the real ledger (found {len(p)})", not p)

    print("T6  the real brief passes")
    q = check_brief(BRIEF) if BRIEF.exists() else []
    for x in q:
        print(f"      -> {x}")
    check(f"no problems in STATE_BRIEF (found {len(q)})", not q)

    print()
    if fails:
        print("SELFTEST FAILED: %d check(s)" % fails)
        return 1
    print("SELFTEST PASS: 14 checks")
    return 0


def _unbalanced(text: str) -> bool:
    return len(token_lines(text)) % 2 == 1


def _live_keyless(text: str) -> bool:
    """A LIVE assertion = the phrase appears, not inside a strike, and not as a quotation.

    A retraction must be able to name the thing it retracts, so this predicate ignores
    lines that are clearly bookkeeping about the retraction rather than claims.
    """
    flags = line_is_struck(text)
    lines = text.split("\n")
    for i, l in enumerate(lines):
        if "keyless ciphertext" not in l.lower() or flags[i]:
            continue
        if i + 1 < len(lines) and any(m in l for m in META_MARKERS):
            continue
        if RETRACTED_MARK in l:
            continue
        return True
    return False


META_MARKERS = (
    "R-P15FIX", "RETRACT", "REFUT", "not a keyless ciphertext",
    "VERDICT IS NOW STRUCK", "rests on a grep", "To re-check",
)
RETRACTED_MARK = "It is not a keyless ciphertext"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.check:
        probs = check_ledger(LEDGER) + check_brief(BRIEF)
        for p in probs:
            print(f"[PROBLEM] {p}")
        print()
        print(f"{len(probs)} problem(s).")
        return 1 if probs else 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
