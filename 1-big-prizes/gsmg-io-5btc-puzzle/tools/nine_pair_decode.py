#!/usr/bin/env python3
"""Two-symbol (and trit-packed) readings of the 9-letter SalPhaseIon streams.

R-ABRUN-DECODE-2026-09-28 recovered the page's {a,b} block rule and left the
9-letter channel's grouping explicitly OPEN, naming two untried shapes:
"2 symbols per char, or 9-as-trit-style packing".

This tool tests exactly those shapes, plus the small number of variations that
are forced by the same arithmetic, and oracles every clean decode against BOTH
funded gates.

Shapes tested
-------------
PAIR       base-9 pair value v = s1*9 + s2, range 0..80. All 81 values fit
           inside the 95 printable ASCII codes, but the offset is NOT unique:
           the admissible range is 32..46, so all 15 are swept rather than
           assuming one.
TRIT3      3 symbols -> v = d1*81 + d2*9 + d3, range 0..728, one char each.
TRIT       9 = 3^2, so one symbol is two trits. TRIT packs each symbol into
           exactly two ternary digits, giving one full byte per symbol-pair
           boundary differently: 2 symbols -> 4 trits -> 0..80 (same range as
           PAIR, packed as trits) and 4 symbols -> 8 trits -> 0..6560, which
           then splits into two 13-bit or three 8-bit groups. Tested because
           trit packing is a distinct *bit layout*, not a distinct value.

Maps
----
POS     a..i -> 0..8   (rank positional, base 9)
CANON   a..i -> 1..9   (the certified page map; base 9, digits 1-9)
and the reverse of each stream.

Every decode that is fully printable and >= 6 characters is pushed to
tools/oracle.py (small gate 1GSMG1JC9...) and tools/oracle_dualite.py
(17ucy1K9...).

    python3 tools/nine_pair_decode.py --selftest
    python3 tools/nine_pair_decode.py
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STREAMS = ROOT / "data" / "finalpage-digit-streams.json"
ORACLE = ROOT / "tools" / "oracle.py"
ORACLE_D = ROOT / "tools" / "oracle_dualite.py"

POS = {c: i for i, c in enumerate("abcdefghi")}          # a=0 .. i=8
CANON = {c: i + 1 for i, c in enumerate("abcdefghi")}    # a=1 .. i=9
MAPS = {"POS": POS, "CANON": CANON}


def digits(stream: str, m: dict) -> list[int]:
    return [m[c] for c in stream if c in m]


def pair_read(ds: list[int], offset: int) -> str:
    """base-9 pair v = d1*9 + d2, shifted by offset, dropped if unprintable."""
    out = []
    for i in range(0, len(ds) - 1, 2):
        v = ds[i] * 9 + ds[i + 1] + offset
        if 32 <= v <= 126:
            out.append(chr(v))
        else:
            out.append("\x00")
    return "".join(out)


def trit4(ds: list[int], offset: int) -> str:
    """4 symbols -> 8 trits -> integer 0..6560, emitted low-6-bits first."""
    out = []
    for i in range(0, len(ds) - 3, 4):
        v = 0
        for d in ds[i : i + 4]:
            v = v * 9 + d
        # 0..6560 -> two 13-bit halves -> one printable char each
        for half in (v & 0x1FFF, (v >> 13) & 0x1FFF):
            c = half + offset
            out.append(chr(c) if 32 <= c <= 126 else "\x00")
    return "".join(out)


def trit3(ds: list[int], offset: int) -> str:
    """3 symbols -> 6 trits -> 0..728, split as printable chars directly."""
    out = []
    for i in range(0, len(ds) - 2, 3):
        v = 0
        for d in ds[i : i + 3]:
            v = v * 9 + d
        c = v + offset
        out.append(chr(c) if 32 <= c <= 126 else "\x00")
    return "".join(out)


def clean(s: str) -> str | None:
    if "\x00" in s:
        return None
    letters = [c for c in s if c.isalnum()]
    if len(letters) < 6:
        return None
    return s


def windowed(s: str) -> str | None:
    """Longest printable run inside a partially-printable decode.

    Needed because the trit shapes span 0..728 / 0..6560, so NO offset makes
    every character printable and `clean` would reject the shape outright,
    leaving the direction untested rather than tested-and-negative. The longest
    run is the strongest in-shape window, which is what a real plaintext would
    look like if the grouping were right but the offset wrong.
    """
    best = ""
    for part in s.split("\x00"):
        if len(part) > len(best):
            best = part
    return best if len([c for c in best if c.isalnum()]) >= 6 else None


def selftest() -> int:
    """Encoder/decoder round-trip on synthetic streams, plus the arithmetic
    claim that 81 printable codes fit with a +32 offset."""
    assert 9 * 9 == 81
    # The offset is NOT unique: 81 values must all land in 32..126, so the
    # admissible range is exactly 32..46 (min 0+o>=32, max 80+o<=126). The tool
    # therefore sweeps all 15 rather than pretending one is derived. This
    # assertion pins the bracket so a later edit cannot silently widen it.
    assert (32, 46) == (32, 126 - 80), "admissible offset range changed"
    # round trip PAIR: value v must come back from its own digits
    for v in (0, 1, 40, 80):
        d = [v // 9, v % 9]
        assert d[0] * 9 + d[1] == v
    # the real streams must have the right shape
    D = json.loads(STREAMS.read_text())
    dbbib, faed = D["dbbib_91"].rstrip("z"), D["faed_570"].rstrip("z")
    assert len(dbbib) == 91 and len(faed) == 570
    assert set(dbbib) <= set("abcdefghi")
    # a synthetic readable stream must decode back under PAIR
    msg = "HELLOWORLD"
    ds = [0] * len(msg)
    enc = []
    for ch in msg:
        v = ord(ch) - 32
        enc += [v // 9, v % 9]
    assert pair_read(enc, 32) == msg, "PAIR is not invertible as documented"
    # trit3 round trip on a synthetic readable stream
    enc3 = []
    for ch in "TESTING":
        v = ord(ch) - 32
        if v > 728:
            continue
        enc3 += [v // 81, (v // 9) % 9, v % 9]
    assert trit3(enc3, 32) == "TESTING", "TRIT3 is not invertible as documented"
    # regression guard: the hit detector must NOT fire on the literal
    # "NO MATCH", which a substring test would report as a hit.
    def hit(out: str) -> bool:
        return bool(re.search(r"^MATCH ", out, re.M))

    assert not hit("NO MATCH"), "hit detector false-positives on NO MATCH"
    assert hit("MATCH 1GSMG1JC9 reading=raw priv_hex=ab12 wif=L1aW4"), \
        "hit detector misses a real MATCH line"
    assert not hit("cipher: no valid padding: OK\nNO MATCH"), \
        "hit detector false-positives inside a longer report"
    print("SELFTEST PASS 9/9")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    D = json.loads(STREAMS.read_text())
    streams = {
        "dbbib_91": D["dbbib_91"].rstrip("z"),
        "faed_570": D["faed_570"].rstrip("z"),
        "dbbib+faed": D["dbbib_91"].rstrip("z") + D["faed_570"].rstrip("z"),
        "faed+dbbib": D["faed_570"].rstrip("z") + D["dbbib_91"].rstrip("z"),
    }

    cands: dict[str, str] = {}
    total = 0
    for sname, s in streams.items():
        for mname, m in MAPS.items():
            for direction, ds in (("fwd", digits(s, m)), ("rev", digits(s, m)[::-1])):
                # PAIR: sweep the full admissible offset bracket 32..46
                for off in range(32, 47):
                    total += 1
                    t = pair_read(ds, off)
                    c = clean(t)
                    if c:
                        cands[f"PAIR/{sname}/{mname}/{direction}/o{off}"] = c
                # trit-style packing: 3 trits = 729 values, so a wider
                # admissible bracket 32..(126-728) is empty -> only offsets that
                # keep the USED values printable, swept over the same 32..46
                # plus the exact-width ones for 4-trit halves.
                for off in list(range(32, 47)) + [0, -32]:
                    total += 1
                    t = trit3(ds, off)
                    c = clean(t) or windowed(t)
                    if c:
                        cands[f"TRIT3/{sname}/{mname}/{direction}/o{off}"] = c
                    total += 1
                    t = trit4(ds, off)
                    c = clean(t) or windowed(t)
                    if c:
                        cands[f"TRIT4/{sname}/{mname}/{direction}/o{off}"] = c

    print(f"reads attempted: {total}   fully-printable candidates: {len(cands)}")
    for k in sorted(cands):
        v = cands[k]
        print(f"  {k:52s} {v[:64]!r}")

    if not cands:
        print("\n0 clean decodes; nothing to oracle.")
        return 0

    hits = 0
    for k, v in sorted(cands.items()):
        for orc, tag in ((ORACLE, "small"), (ORACLE_D, "dualite")):
            r = subprocess.run(
                [sys.executable, str(orc), v],
                capture_output=True, text=True, cwd=ROOT,
            )
            out = (r.stdout + r.stderr).strip()
            # NOTE: must anchor to line-start. A bare `"MATCH" in out` also
            # fires on the literal string "NO MATCH", which would report every
            # negative as a hit. The real oracle prints a line starting "MATCH ".
            if re.search(r"^MATCH ", out, re.M):
                hits += 1
                print(f"\n*** MATCH ({tag}) via {k} ***\n{out}")
    print(f"\nORACLE: {len(cands)} candidates x 2 gates, {hits} MATCH")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
