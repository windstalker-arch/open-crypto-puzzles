#!/usr/bin/env python3
"""Decode the {a,b} letter runs on the SalPhaseIon page as 7-bit ASCII.

The SalPhaseIon capture (data/live_salphaseion.txt) is 1075 whitespace-separated
single-character tokens. Two of its blocks use a TWO-letter alphabet, {a,b}, and
those runs carry literal English under a fixed rule:

    a -> 0, b -> 1, concatenate, take MSB-first, 8 bits per character.

The rule is not assumed; it is *recovered* from the page. Scanning every maximal
{a,b} run, exactly two of the 134 runs are long enough to hold a character and
decode to fully printable ASCII, and both are words of the certified RAW_PW
recipe:

    raw[91:195]  ->  104 tokens -> 13 characters -> "matrixsumlist"
    raw[959:999] ->   40 tokens ->  5 characters -> "enter"

RAW_PW = matrixsumlist + enter + lastwordsbeforearchichoice + thispassword
         + matrixsumlist

so these two decodes are elements 1 and 2 of the 5-element recipe, recovered from
the page rather than assumed. The remaining 132 runs are all < 8 tokens and so
cannot hold a whole character; there is no further literal word in this channel.

This tool only describes the page. It makes no claim about the two 9-letter
streams (dbbib_91, faed_570), which use a different alphabet and are handled
elsewhere.

    python3 tools/ab_run_decode.py --selftest
    python3 tools/ab_run_decode.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "data" / "live_salphaseion.txt"
STREAMS = ROOT / "data" / "finalpage-digit-streams.json"

# The two clean runs, as (start, length, text). Asserted, not searched for.
CLEAN_WITNESSES = [
    (91, 104, "matrixsumlist"),
    (959, 40, "enter"),
]

# Elements 1 and 2 of the certified recipe, for the corroboration check.
RECIPE_HEAD = ("matrixsumlist", "enter")

BITMAP = {"a": "0", "b": "1"}


# ----------------------------------------------------------------- primitives

def page_tokens() -> list[str]:
    if not PAGE.is_file():
        raise SystemExit(f"missing page capture: {PAGE}")
    return PAGE.read_text(encoding="utf-8", errors="replace").split()


def ab_runs(tokens: list[str]) -> list[tuple[int, str]]:
    """Every maximal {a,b} run, as (start_token_index, run_text)."""
    return [(m.start(), m.group())
            for m in re.finditer(r"[ab]+", "".join(tokens))]


def decode_run(run: str, zero: str = "a", msb: bool = True) -> tuple[bytes, int]:
    """Decode a {a,b} run to bytes. Returns (bytes, leftover_bit_count)."""
    bits = "".join("0" if c == zero else "1" for c in run)
    whole = len(bits) // 8 * 8
    body = bits[:whole]
    if not msb:
        body = body[::-1]
    out = bytes(int(body[i:i + 8], 2) for i in range(0, whole, 8))
    return out, len(bits) - whole


def printable(data: bytes) -> int:
    return sum(32 <= b < 127 for b in data)


# ------------------------------------------------------------------- analysis

def scan() -> list[tuple[int, int, int, str, int]]:
    """All runs that can hold at least one character.

    Returns (start, length, n_chars, decoded_text, leftover_bits) for every run
    of >= 8 tokens, clean or not.
    """
    tokens = page_tokens()
    rows = []
    for start, run in ab_runs(tokens):
        if len(run) < 8:
            continue
        data, rem = decode_run(run)
        rows.append((start, len(run), len(data),
                     data.decode("ascii", "replace"), rem))
    return rows


def _raw(start: int) -> bytes:
    """Re-decode the run at `start` to raw bytes, for the printability test."""
    for s, run in ab_runs(page_tokens()):
        if s == start:
            return decode_run(run)[0]
    raise KeyError(start)


def structure() -> dict:
    """The block map of the page, for the record."""
    tokens = page_tokens()
    d = json.loads(STREAMS.read_text())
    a, b = d["dbbib_91"], d["faed_570"][:570]
    joined = "".join(tokens)
    return {
        "page_tokens": len(tokens),
        "A_dbbib_91": {"span": [0, 91], "len": len(a),
                       "alphabet": sorted(set(a)), "matches": joined[0:91] == a},
        "GAP_91_195": {"span": [91, 195], "len": 195 - 91,
                       "alphabet": sorted(set(joined[91:195])),
                       "note": "two-letter {a,b} block, unrecorded in prior ledger"},
        "B_faed_570": {"span": [195, 765], "len": len(b),
                       "alphabet": sorted(set(b)), "matches": joined[195:765] == b},
        "z_separator_765": joined[765],
        "tail_o_count": joined.count("o"),
        "z_positions": [i for i, c in enumerate(joined) if c == "z"],
    }


# ------------------------------------------------------------------- selftest

def selftest() -> int:
    bad = 0

    # 1. the bit mapping and 8-bits-per-char convention
    got, rem = decode_run("abbabbab")
    ok = got == b"m" and rem == 0
    bad += not ok
    print(f"  [{'PASS' if ok else 'FAIL'}] primitive: 'abbabbab' -> {got!r} "
          f"rem={rem} (want b'm')")

    # 2. every clean witness decodes exactly, at the recorded position
    by_start = {r[0]: r for r in scan()}
    for start, length, text in CLEAN_WITNESSES:
        row = by_start.get(start)
        ok = row is not None and row[1] == length and row[3] == text
        bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] clean run @{start:5d}: "
              f"{row[3]!r} len={row[1] if row else '?'} (want {text!r} len={length})")

    # 3. the two decodes are elements 1 and 2 of the certified recipe
    decoded = [t for _, _, t in CLEAN_WITNESSES]
    ok = tuple(decoded) == RECIPE_HEAD
    bad += not ok
    print(f"  [{'PASS' if ok else 'FAIL'}] decodes {decoded} == RAW_PW head "
          f"{list(RECIPE_HEAD)}")

    # 4. the claim that no OTHER run yields a whole character is exhaustive:
    #    every run not in the witness list must be < 8 tokens.
    longs = [r[0] for r in scan()]
    ok = longs == sorted(s for s, _, _ in CLEAN_WITNESSES)
    bad += not ok
    print(f"  [{'PASS' if ok else 'FAIL'}] exhaustive: exactly "
          f"{len(CLEAN_WITNESSES)} runs >= 8 tokens at {longs}")

    # 5. structural map must hold: A and B land where the ledger says
    st = structure()
    ok = (st["A_dbbib_91"]["matches"] and st["B_faed_570"]["matches"]
          and st["GAP_91_195"]["alphabet"] == ["a", "b"]
          and st["A_dbbib_91"]["len"] == 91 and st["B_faed_570"]["len"] == 570)
    bad += not ok
    print(f"  [{'PASS' if ok else 'FAIL'}] structure: A@{st['A_dbbib_91']['span']} "
          f"({st['A_dbbib_91']['len']}), gap@{st['GAP_91_195']['span']} "
          f"alpha={st['GAP_91_195']['alphabet']}, "
          f"B@{st['B_faed_570']['span']} ({st['B_faed_570']['len']}), "
          f"z@{st['z_separator_765']!r}")

    print(f"SELFTEST {'PASS' if bad == 0 else 'FAIL'}: {bad} failures")
    return 1 if bad else 0


def run() -> int:
    st = structure()
    print("=== SalPhaseIon page block map ===")
    print(f"  page tokens              : {st['page_tokens']}")
    for key in ("A_dbbib_91", "GAP_91_195", "B_faed_570"):
        blk = st[key]
        print(f"  raw{str(blk['span']):<12}  len={blk['len']:<4} "
              f"alphabet={''.join(blk['alphabet'])}")
    print(f"  raw[765] = {st['z_separator_765']!r} (separator), "
          f"z at {st['z_positions']}, 'o' count {st['tail_o_count']}")

    runs = ab_runs(page_tokens())
    longs = scan()
    print(f"\n=== {len(runs)} maximal {{a,b}} runs, {len(longs)} long enough to "
          f"hold a character ===")
    for start, length, n, txt, rem in longs:
        data = _raw(start)
        pr = printable(data)
        tag = "CLEAN ASCII" if pr == n else f"{pr}/{n} printable"
        print(f"  raw[{start}:{start + length}]  {length:>4} tokens -> {n:>2} chars"
              f"  rem={rem}  {txt!r:<18} {tag}")

    print("\n=== certified ===")
    for start, length, text in CLEAN_WITNESSES:
        print(f"  RAW_PW element: raw[{start}:{start + length}] -> {text!r}")
    print("  RAW_PW = matrixsumlist + enter + lastwordsbeforearchichoice"
          " + thispassword + matrixsumlist")
    print("  elements 1-2 are page-confirmed; 3-5 are not in this channel.")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true",
                    help="print the page block map and the decoded runs")
    a = ap.parse_args(argv)
    rc = 0
    if a.selftest or not a.run:
        rc |= selftest()
    if a.run:
        rc |= run()
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
