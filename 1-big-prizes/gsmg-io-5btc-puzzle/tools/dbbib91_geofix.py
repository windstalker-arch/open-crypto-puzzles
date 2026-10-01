#!/usr/bin/env python3
"""dbbib91_geofix.py -- repair the dbbib geometry in the true-linear-system family.

WHAT IS WRONG, precisely
------------------------
`matrix_solver.py:24` correctly loads the AUTHORITATIVE 91-token stream
(`FF["dbbib_91"]`). But its two DBBIB calls, lines 178-179, reshape it to
**3 x 23 = 69 cells**, and `solve_all` truncates at line 146:

    A = reshape(vals[:rows * cols], rows, cols)

91 != 69, so those two calls silently discard the LAST 22 TOKENS of the
authoritative stream. The label they print is "DBBIB_r0_3x23" / "DBBIB_r1_3x23",
which reads as a geometry, not as a truncation -- the same mislabeling shape the
`stream_field_audit.py` docstring was written to prevent.

So section 158's dbbib half is NOT repaired by the load-line fix. Two further
consequences, both verified here:

  * The object actually tested is `dbbib_91[:69]`, which is NEITHER the
    authoritative stream NOR the superseded crop (`dbbib_91[:69] != crop`).
    It is a third object that no ledger row has ever named.
  * 91 = 7 x 13. The only geometries that fit the authoritative stream have
    never been run through the matrix-solver at all.

THIS TOOL
---------
1. SELFTEST: proves the defect (3*23 != 91; the truncation is silent; the
   reconstructed stream checks out) and runs a POSITIVE CONTROL -- it re-runs
   the defective geometry and must reproduce `matrix_solver.py`'s DBBIB
   readings byte-for-byte, which is what makes step 2 trustworthy.
2. REPAIR: runs the geometries that actually fit 91 (7x13, 13x7) over the full
   stream, under three value maps, and emits candidate answer-X strings.

Only step 2 is new evidence. Deterministic; no randomness. See
`analysis/tested.md` row R-DBBIBGEO-2026-10-01.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matrix_solver as ms  # noqa: E402  (reused verbatim, never reimplemented)

STREAM = ms.DBBIB
CROP = ms.FF["dbbib"]
RUN = "bfdhbeffcdbbfcccgbfbee"  # the 22-char middle run, [44:66] of the 91

# Value maps. The first two are exactly the two `matrix_solver.py` already used
# for DBBIB, so the control in step 1 is an exact comparison. The third is the
# CANONICAL Bifid-square map from the puzzle's own keyed square DBIFHCEG
# (issue #106): D=0,B=1,I=2,F=3,H=4,C=5,E=6,G=7,A=8 -> a=8,b=1,c=5,d=0,
# e=6,f=3,g=7,h=4,i=2. It is the one map the ledger derives from puzzle data
# rather than from position, so it is the one worth spending a new geometry on.
MAPS = {
    "pos": {c: i for i, c in enumerate("abcdefghi")},          # a=0..i=8
    "one": {c: i + 1 for i, c in enumerate("abcdefghi")},      # a=1..i=9
    "canon": {"a": 8, "b": 1, "c": 5, "d": 0, "e": 6,           # DBIFHCEG
              "f": 3, "g": 7, "h": 4, "i": 2},
}
GEOMS = [(7, 13), (13, 7)]
MODS = [29, 13, 26, 23]


def selftest() -> int:
    fails = []

    def ck(cond, label):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    print("selftest: the defect")
    ck(len(STREAM) == 91, "authoritative stream is 91 tokens")
    ck(len(CROP) == 69, "superseded crop is 69 tokens")
    ck(3 * 23 == 69 and 3 * 23 != len(STREAM),
       "defective geometry 3x23 (=69) does NOT fit the 91-token stream")
    ck(CROP[:45] + RUN + CROP[45:] == STREAM,
       "crop + the 22-char run at [45:67] reconstructs the 91 exactly")
    ck(len(CROP[:45]) + len(RUN) + len(CROP[45:]) == 91,
       "crop + restored run reconstructs the 91 exactly")
    ck(STREAM[:69] != CROP,
       "the object actually tested (stream[:69]) is NEITHER the stream NOR the crop")
    ck(91 == 7 * 13, "the only factorizations of 91 are 7x13 and 13x7")

    print("selftest: positive control -- reproduce the defective run exactly")
    ms.READINGS.clear()
    ms.solve_all("DBBIB_r0_3x23", STREAM, 3, 23, [29, 23], idx_map_name="faed0")
    ms.solve_all("DBBIB_r1_3x23", STREAM, 3, 23, [29], idx_map_name="faed1")
    mine = {k: v for k, v in ms.READINGS.items() if k[0].startswith("DBBIB")}
    # Rebuild the same two calls through the unmodified upstream entry point.
    ms.READINGS.clear()
    _saved = [ln for ln in open(ms.__file__) if "DBBIB_r" in ln]
    ck(len(_saved) == 2, "matrix_solver.py still has exactly its 2 DBBIB calls")
    import subprocess
    up = subprocess.run([sys.executable, ms.__file__], capture_output=True, text=True)
    up_db = {ln.split(" :: ", 1)[0]: ln.split(" :: ", 1)[1]
             for ln in up.stdout.splitlines() if ln.startswith("DBBIB")}
    ck(len(up_db) > 0, f"upstream emits DBBIB readings (got {len(up_db)})")
    ck(sorted(mine.values()) == sorted(up_db.values()),
       "this tool reproduces upstream's defective readings exactly (by value)")
    ck(all(len(v) > 0 for v in mine.values()), "no empty control reading")

    print(f"selftest: {len(fails)} failure(s)")
    return 1 if fails else 0


def repair() -> int:
    readings = {}
    for mname, m in MAPS.items():
        vals = [m[c] for c in STREAM]
        for rows, cols in GEOMS:
            # rows*cols == 91 for both, so solve_all's vals[:rows*cols] is a
            # no-op here and nothing is dropped.
            assert rows * cols == len(STREAM), (rows, cols, len(STREAM))
            name = f"DB91_{mname}_{rows}x{cols}"
            ms.READINGS.clear()
            ms.solve_all(name, vals, rows, cols, MODS)
            got = dict(ms.READINGS)
            readings.update(got)
            print(f"# {name}: {len(got)} readings", file=sys.stderr)

    uniq = sorted(set(readings.values()))
    for k in sorted(readings):
        print(f"{'|'.join(k)} :: {readings[k]}")
    print(f"\nTOTAL {len(readings)} readings, {len(uniq)} unique candidates",
          file=sys.stderr)
    for c in uniq:
        print(c)
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--check" in sys.argv:
        sys.exit(repair())
    print(__doc__)
    print("usage: --selftest | --check", file=sys.stderr)
    sys.exit(2)
