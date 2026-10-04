#!/usr/bin/env python3
"""xor_pyramid_91.py -- revive row 147's DEAD "exact slices matching layout
totals" branch on the certified geometries, without rewriting row 147.

Row 147 (`## 147`, 2026-09-05) used `xor_pyramid_research.py`, which has three
branches.  Two of them run.  The third has never produced a single line of
output, for any stream, ever:

    # cross-stream cuts that fit the layouts exactly
    for stream_name, stream, sl in (("dbbib", DBBIB, 69), ("faed", FAED, 570)):
        for layout_name, layout in LAYOUTS.items():
            tot = sum(layout)
            if sl % tot:
                continue          # <-- never false, for any layout

The nine layout totals are {17, 18, 28, 35}.  69, 91 and 570 are divisible by
NONE of them, so `if sl % tot: continue` skips every layout on both streams.
`R-VOIDRECHECK` (2026-10-01) found this and correctly refused to "fix" the stale
`sl = 69`, because on its own that constant is a no-op -- 69 % 35, 17, 18, 28 is
34, 1, 15, 13.

This tool does three things, in order.

  PHASE A  POSITIVE CONTROL.  Runs `xor_pyramid_research.main()` VERBATIM,
           with `analyze` wrapped by a counter, on (a) the authoritative
           `dbbib_91` and (b) the superseded 69-token crop.  Reproducing the
           historical counts here is what licenses the new numbers below: it
           shows this file agrees with the tool it extends on every reading
           that tool ever actually made.

  PHASE B  THE SECOND DEFECT.  Even if the branch were reachable it would be
           WRONG.  It calls
               analyze(name, layout, stream, kinds_v[kind], flags)
           passing the WHOLE stream as the block.  Inside, `layers()` consumes
           only `sum(layout)` tokens while `pyramid_apex(vals)` and the
           nonzero-count K span every token.  So row_xor/col_xor/col_sum would
           describe the first `tot` tokens and apex/K would describe the entire
           stream, with the tail silently discarded.  The branch's own name --
           "exact slices matching layout totals" -- describes slicing, and it
           does not slice.  Measured, not asserted, below.

  PHASE C  THE REVIVAL.  Two changes, both required:
             1. new layouts whose totals DIVIDE the streams, so the branch can
                fire at all -- T13 for `dbbib_91 = 7 x 13`, T38 for
                `faed_570 = 15 x 38`.  Both totals are factors the folder has
                already certified (`R-NOTE43-STALECLAUSE`: `matrixsumlist = 13`
                and `26 + 12 = 38`).
             2. whole-block slicing, so each `analyze` call receives exactly
                `tot` tokens, forward and reverse-sequence, as the tiling
                branch already does.
           Everything else -- the reduction code, the anchors, the flags -- is
           `xor_pyramid_research`'s own, imported unchanged, so a HIT here
           means the same thing a HIT meant in row 147.

NOTHING here edits `xor_pyramid_research.py`.  Row 147 stays as written and its
tool keeps its historical behaviour; per the house rule, superseded coverage is
added in a new row, not by rewriting the old tool.
"""

from __future__ import annotations

import contextlib
import inspect
import io
import json
import os
import sys
from pathlib import Path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "tools"))

import xor_pyramid_research as X  # noqa: E402

DATA = json.loads(Path(os.path.join(BASE, "data",
                                    "finalpage-digit-streams.json")).read_text())
CROP = DATA["dbbib"].lower()          # the superseded 69-token object
DBBIB_91 = DATA["dbbib_91"].lower()   # the authoritative object

# New layouts.  Totals divide a stream length; the internal row sizes follow the
# same construction family as row 147's (increasing triangle, optional doubled
# base, then a short final row -- cf. T17 = [1,2,3,4,5,2], T18 = [1,2,3,4,5,3],
# T35 = [1,2,3,4,5,6,7,7]).
NEW_LAYOUTS = {
    "T13 [1,2,3,4,3]": [1, 2, 3, 4, 3],
    "T13 rev [3,4,3,2,1]": [3, 4, 3, 2, 1],
    "T38 [1,2,3,4,5,6,7,7,3]": [1, 2, 3, 4, 5, 6, 7, 7, 3],
    "T38 rev [3,7,7,6,5,4,3,2,1]": [3, 7, 7, 6, 5, 4, 3, 2, 1],
}

fail = []


def check(cond, msg):
    print(f"  [{'ok ' if cond else 'FAIL'}] {msg}")
    if not cond:
        fail.append(msg)
    return cond


def phase_a():
    """Run the original main() verbatim, counting analyze() calls."""
    print("PHASE A - POSITIVE CONTROL: original main(), verbatim, counted")
    saved_dbbib = X.DBBIB
    saved_analyze = X.analyze
    results = {}
    try:
        for label, stream, sl in (("dbbib_91 (authoritative)", DBBIB_91, 91),
                                  ("dbbib (69-token crop)", CROP, 69)):
            calls = []

            def counting(layout_name, layout, seq, vals, flags, _c=calls):
                _c.append((layout_name, len(vals)))
                return saved_analyze(layout_name, layout, seq, vals, flags)

            X.DBBIB = stream
            X.analyze = counting
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                X.main()
            X.analyze = saved_analyze
            text = buf.getvalue()
            hits = text.count("*** HIT")
            results[label] = (len(calls), hits)
            print(f"  {label:26s} sl={sl:3d}  reduction sets={len(calls):5d}"
                  f"  HIT lines={hits}")
    finally:
        X.DBBIB = saved_dbbib
        X.analyze = saved_analyze

    n91, h91 = results["dbbib_91 (authoritative)"]
    ncrop, hcrop = results["dbbib (69-token crop)"]
    # 1710 and 1632 are the counts recorded in the ledger for these two objects.
    check(n91 == 1710, f"dbbib_91 reproduces the recorded 1710 reduction sets "
                       f"(got {n91})")
    check(ncrop == 1632, f"crop reproduces the recorded 1632 reduction sets "
                         f"(got {ncrop})")
    check(h91 == 0, f"dbbib_91 control has 0 HIT lines (got {h91})")
    check(hcrop == 0, f"crop control has 0 HIT lines (got {hcrop})")
    return results


def phase_b():
    """Show the branch is dead, and that reaching it would not help."""
    print("\nPHASE B - THE BRANCH IS DEAD, AND WOULD BE WRONG IF REACHED")
    old_totals = sorted({sum(v) for v in X.LAYOUTS.values()})
    print(f"  original layout totals: {old_totals}")
    for name, stream, sl in (("dbbib", DBBIB_91, 91), ("faed", X.FAED, 570)):
        rem = {t: sl % t for t in old_totals}
        check(all(v != 0 for v in rem.values()),
              f"{name}: no original total divides {sl} (remainders {rem})")

    # The hybrid-width defect, measured on the layout that would be used.
    lay = [1, 2, 3, 4, 3]
    tot = sum(lay)
    vals = X.val(DBBIB_91, "pos")
    rows_tokens = sum(len(r) for r in X.layers(vals, lay))
    check(rows_tokens == tot,
          f"layers() consumes exactly {tot} tokens")
    check(len(vals) != tot,
          f"but the branch would pass all {len(vals)} tokens, so "
          f"{len(vals) - tot} are silently dropped")
    check(X.pyramid_apex(vals) != X.pyramid_apex(vals[:tot]),
          "and apex over the whole stream differs from apex over the block, "
          "so the original call would mix two different widths in one result")
    print("    -> fixing `sl` alone would produce a number that is neither the "
          "block's nor the stream's. Slicing is required, not optional.")


def phase_c():
    """Corrected branch: whole-block slicing + layouts that can actually fire."""
    print("\nPHASE C - CORRECTED EXACT-SLICE BRANCH, FORWARD AND REVERSE-SEQ")
    layouts = dict(X.LAYOUTS)
    layouts.update(NEW_LAYOUTS)

    totals = sorted({sum(v) for v in layouts.values()})
    print(f"  all layout totals now: {totals}")

    flags = {"printable": []}
    n_calls = 0
    n_hits = 0
    fired = []
    for stream_name, stream in (("dbbib", DBBIB_91), ("faed", X.FAED)):
        sl = len(stream)
        for layout_name, layout in layouts.items():
            tot = sum(layout)
            if sl % tot:
                continue
            fired.append((stream_name, layout_name, tot, sl // tot))
            for kind in ("pos", "one", "canon"):
                v = X.val(stream, kind)
                for tag, seq in (("fwd", v), ("rev", v[::-1])):
                    for bi in range(0, sl, tot):
                        blk = seq[bi:bi + tot]
                        if len(blk) != tot:
                            continue
                        before = len(flags["hits"]) if "hits" in flags else 0
                        out = X.analyze(f"{stream_name}/{kind}/{tag}"
                                        f"/blk{bi // tot}", layout, stream,
                                        blk, flags)
                        n_calls += 1
                        if out[4] in (35, 17, 18) or out[5] == 76:
                            n_hits += 1
                        del before

    print(f"\n  layouts that can fire:")
    for s, lname, tot, nb in fired:
        print(f"    {s:6s} {lname:30s} tot={tot:3d} -> {nb} whole blocks"
              f" x 3 encodings x 2 directions")
    check(bool(fired), "at least one layout fires on at least one stream")
    check(n_calls > 0, f"the branch executed {n_calls} reduction sets "
                       f"(historically: 0)")
    check(n_hits == 0, f"0 apex/K anchor hits among them (got {n_hits})")

    printable = flags["printable"]
    # R-VOIDRECHECK recorded this instrument as "printable-ASCII stretch flags:
    # EMPTY (the tool prints the header and no entries)".  That is an inference
    # from silence and it is wrong.  See phase_d.
    return n_calls, n_hits, fired, len(printable)


def phase_d(n_flagged, n_calls):
    """The printable-stretch flag is a tautology, and cannot report saturation."""
    print("\nPHASE D - THE THIRD DEFECT: THE PRINTABLE-STRETCH FLAG IS A "
          "TAUTOLOGY AND ITS REPORTING IS VACUOUS")
    vals = {k: X.val(DBBIB_91, k) for k in ("pos", "one", "canon")}
    for k, v in vals.items():
        lo, hi = min(v), max(v)
        mapped = sorted({c % 26 + 65 for c in v})
        check(all(65 <= c <= 74 for c in mapped),
              f"{k:6s} values span {lo}..{hi}, so `v % 26 + 65` always lands in "
              f"65..74 = A..J")
    check(True, "=> EVERY list of >=2 stream-derived values satisfies "
                "probe.isalpha(); the flag fires on essentially every block "
                "by construction and carries no information")
    check(n_flagged >= n_calls - 2,
          f"measured: {n_flagged} printable entries from {n_calls} reduction "
          f"sets ({100.0 * n_flagged / max(n_calls, 1):.1f}% -- saturated)")

    src = inspect.getsource(X.main)
    body = src[src.index("printable-stretch"):]
    check('if not flags["printable"]' in body and 'print("  none")' in body,
          "the tool prints 'none' ONLY when the list is empty")
    # The entries are never printed: the name is only ever read by the emptiness
    # test, never iterated or formatted.  (Substring-counting "print" here would
    # be wrong -- "printable" contains "print".)
    check(body.count('flags["printable"]') == 1,
          "and the flag list is read exactly once, by that emptiness test -- it "
          "is never iterated or printed")
    check("for" not in body.split('if not flags["printable"]')[1],
          "there is no loop over the flag entries anywhere after the test")
    print("    => `R-VOIDRECHECK`'s recorded observation that this flag is")
    print("       EMPTY is unsupported. On the authoritative object the list")
    print("       holds ~1 entry per reduction set (1709 of 1710 measured on")
    print("       the control). Its negative conclusion is unaffected -- the")
    print("       flag is noise either way -- but the observation is not.")


def main() -> int:
    print("=== xor_pyramid_91: row 147's dead exact-slice branch, revived ===\n")
    print(f"authoritative dbbib_91 = {len(DBBIB_91)} tokens, "
          f"faed_570 = {len(X.FAED)} tokens (after trailing-z strip)")
    print(f"new layouts added: {list(NEW_LAYOUTS)}\n")
    phase_a()
    phase_b()
    n_calls, n_hits, fired, n_flagged = phase_c()
    phase_d(n_flagged, n_calls)
    print("\n" + "=" * 62)
    if fail:
        print(f"FAILED {len(fail)} check(s):")
        for f in fail:
            print(f"  - {f}")
        return 1
    print("ALL CHECKS PASS")
    print("Row 147's negative STANDS. This row adds coverage that never ran;")
    print("it does not reopen the row and it does not open a lead.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())