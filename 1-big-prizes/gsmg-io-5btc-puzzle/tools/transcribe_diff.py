#!/usr/bin/env python3
"""transcribe_diff.py -- compare a fresh visual transcription of the final-page
digit streams against the stored (authoritative) values.

Purpose: the lead-0 crux is the visual/interpretive read of the SalPhaseIon
page ("in front of your eyes"). When a human transcribes the page, the very
first check is whether that reading differs from the stored dbbib_91 / faed_570
-- any discrepancy is a candidate new-lead fact (a "zeroed-out" character, a
per-glyph color cue, a dropped/added token). This tool makes that comparison
exact and machine-checkable so the delta feeds straight into the decode battery.

Stored references (data/finalpage-digit-streams.json, authoritative after
Note 32 / tested.md late-47):
    dbbib_91 : 91 tokens  (live page + Wayback, 91 = 7x13, top-2 {b,e})
    faed_570 : 570 tokens (trailing 'z' marker removed)

Usage:
    python3 tools/transcribe_diff.py --dbbib "<91 letters>" --faed "<570 letters>"
    python3 tools/transcribe_diff.py --streams-file F      # lines:  dbbib: <str> / faed: <str>
    python3 tools/transcribe_diff.py --selftest            # stored-vs-stored must diff as identity

Optional: mark uncertainty/zeroed glyphs in-place (e.g. '*' or '_') -- they are
reported as positional flags, not as literal stream content.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
SYMBOLS = set("abcdefghi")


def load_stored() -> dict[str, str]:
    d = json.loads(Path(DATA_FILE).read_text())
    dbbib = d["dbbib_91"]
    faed = d["faed_570"].rstrip("z")
    return {"dbbib": dbbib, "faed": faed}


def clean(s: str) -> tuple[str, list[tuple[int, str]]]:
    """Keep only [a-i]; anything else (whitespace, punctuation, marks) is a flag.
    Flags are recorded as (stream_index, char)."""
    out = []
    flags: list[tuple[int, str]] = []
    for ch in s:
        if ch in SYMBOLS:
            out.append(ch)
        elif not ch.isspace():
            flags.append((len(out), ch))
    return "".join(out), flags


def diff(name: str, stored: str, given: str, gflags: list[tuple[int, str]]) -> list[str]:
    lines: list[str] = []
    if len(given) != len(stored):
        lines.append(f"  LENGTH {name}: stored={len(stored)} given={len(given)} "
                     f"({'+' if len(given) > len(stored) else ''}{len(given) - len(stored)})")
    n = min(len(stored), len(given))
    diffs = [i for i in range(n) if stored[i] != given[i]]
    if diffs:
        head = ", ".join(f"{i}:{stored[i]}->{given[i]}" for i in diffs[:25])
        more = "" if len(diffs) <= 25 else f" (+{len(diffs) - 25} more)"
        lines.append(f"  DIFF {name}: {len(diffs)} positions -> {head}{more}")
    if gflags:
        fh = ", ".join(f"{i}:'{ch}'" for i, ch in gflags[:25])
        more = "" if len(gflags) <= 25 else f" (+{len(gflags) - 25} more)"
        lines.append(f"  FLAGS {name}: {len(gflags)} non-symbol glyphs at -> {fh}{more}")
    if not lines:
        lines.append(f"  {name}: IDENTICAL ({len(stored)} chars)")
    return lines


def selftest() -> int:
    stored = load_stored()
    out = diff("dbbib", stored["dbbib"], stored["dbbib"], [])
    out += diff("faed", stored["faed"], stored["faed"], [])
    out += diff("flagcheck", stored["faed"], stored["faed"][:570] + "x", [])
    ok = all("IDENTICAL" in x for x in out if "dbbib:" in x or "faed:" in x)
    fail = any("flagcheck" in x and "IDENTICAL" in x for x in out)
    print("SELFTEST:", "PASS" if (ok and not fail) else "FAIL")
    for x in out:
        print(x)
    if fail:
        print("FAIL: `flagcheck` should have reported the length diff")
        return 1
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dbbib", help="transcribed 91-token dbbib stream (a..i)")
    ap.add_argument("--faed", help="transcribed 570-token faed stream (a..i)")
    ap.add_argument("--streams-file", help="file with lines 'dbbib: <str>' / 'faed: <str>'")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    stored = load_stored()
    given: dict[str, str] = {}
    flags: dict[str, list[tuple[int, str]]] = {}

    if args.streams_file:
        txt = Path(args.streams_file).read_text()
        for m in re.finditer(r"^(dbbib|faed)\s*[:=]\s*(.+)$", txt, re.M | re.I):
            name = m.group(1).lower()
            if name not in given:
                given[name], flags[name] = clean(m.group(2))
    for name, key in (("dbbib", "dbbib"), ("faed", "faed")):
        v = getattr(args, key)
        if v:
            given[name], flags[name] = clean(v)
    if not given:
        ap.print_help()
        return 2

    rc = 0
    for name in ("dbbib", "faed"):
        if name not in given:
            continue
        for ln in diff(name, stored[name], given[name], flags[name]):
            print(ln)
            if "DIFF" in ln or "FLAGS" in ln or "LENGTH" in ln:
                rc = 1
    print("VERDICT:", "matches stored (no new positional data)" if rc == 0
          else "differs from stored (review the positions above)")
    return rc


if __name__ == "__main__":
    sys.exit(main())