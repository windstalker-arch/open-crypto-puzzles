#!/usr/bin/env python3
"""lattice_probe_91: repair of the STALE-CROP RESHAPE SUPPRESSION defect in
tools/lattice_probe.py (line 133), discovered 2026-10-01.

DEFECT
------
lattice_probe.py:33 loads the AUTHORITATIVE stream (DATA["dbbib_91"]) but its
section-A reshape fingerprint is gated by:

    if len(st) == 69 or len(st) == 570:      # lattice_probe.py:133
        for r, c in factors(len(st)):
            m = np.array(v).reshape(r, c)
            report(...)

`69` is the superseded OCR crop length. With the authoritative 91-token
stream, len(st) is neither 69 nor 570, so the gate is FALSE and the ENTIRE
reshape / rank / gcd / row-col-sum fingerprint NEVER RUNS for dbbib.

IMPACT ON THE LEDGER
--------------------
tested.md row 146 claims "34 factor-pair reshapes -> integer rank / gcd /
row-col sums (every reshape full-rank with gcd 1)" and "low-rank / singular
spectrum / white-rabbit key-bit collisions: none". That claim was measured on
the 69-token crop, whose ONLY factor pair is 3x23. On the authoritative
dbbib_91 the reshape coverage is ZERO, and the 7x13 shape -- the exact shape
that exposed the matrix_solver truncation defect (tested.md R-DBBIBGEO) --
is never probed by this tool at all.

Note this defect SILENTLY rather than loudly: the tool prints section A with
n=91 and valid GF(k) recurrence lines, so a reader checking token counts sees
a healthy run. Only the missing "[dbbib/...]" reshape lines reveal it.

REPAIR STRATEGY (same as tools/dbbib91_geofix.py)
-------------------------------------------------
This tool does NOT edit lattice_probe.py. Instead:
  1. POSITIVE CONTROL: re-derives the defective baseline from the 69-token
     crop, proving the historical 3x23 reading is reproducible and that the
     repair preserves it.
  2. Runs the suppressed fingerprint on dbbib_91 for every factor pair in
     BOTH orientations (7x13 and 13x7 -- factors() returns only d<=sqrt(n),
     so the transpose orientation is otherwise never covered).
  3. Adds the checks the section-A gate suppressed: integer rank, gcd, full
     row/col sums, near-low-rank / singular spectrum, RS/CS collisions, and
     the white-rabbit 0x41D464 key-bit set.

This tool makes NO oracle/gate calls. It is structural fingerprinting only.
"""
import importlib.util as _ilu
import json
import os
import sys
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
LP_PATH = Path(__file__).resolve().parent / "lattice_probe.py"

# Reuse the audited primitives (enc/factors/report/probe_linear_recurrence) so
# the repair cannot silently diverge from the tool it repairs.
_spec = _ilu.spec_from_file_location("_lp", LP_PATH)
_lp = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_lp)

DATA = json.loads((BASE / "data" / "finalpage-digit-streams.json").read_text())
DBBIB_91 = DATA["dbbib_91"].lower()
DBBIB_CROP = DATA["dbbib"].lower()

RS = [7, 6, 5, 5, 5, 5, 3, 8, 7, 6, 7, 6, 6, 0]
CS = [7, 8, 4, 8, 7, 5, 5, 5, 5, 5, 6, 5, 6, 0]
RKEY_ONES = {2, 5, 6, 10, 12, 14, 15, 16, 22}  # 0x41D464, from lattice_probe


def singular_spectrum(m):
    """Return (rank, smallest 3 singular values, cond ratio)."""
    sv = np.linalg.svd(np.asarray(m, dtype=float), compute_uv=False)
    sv = sv[sv > 1e-9]
    if sv.size == 0:
        return 0, [], 0.0
    ratio = float(sv[-1] / sv[0]) if sv[0] else 0.0
    return int(len(sv)), [round(float(x), 4) for x in sv[-3:]], ratio


def reshape_report(label, v, r, c):
    m = np.array(v).reshape(r, c)
    rank, smin, ratio = singular_spectrum(m)
    g = int(np.gcd.reduce(m.ravel())) if m.size else 0
    full_rank = rank == min(r, c)
    print(f"\n  [{label}] {r}x{c}")
    print(f"    rank={rank} (min dim {min(r, c)}) "
          f"{'FULL-RANK' if full_rank else '*** RANK-DEFICIENT ***'}")
    print(f"    gcd(all entries)={g}")
    print(f"    smallest singular values={smin} s_min/s_max={ratio:.6f}")
    if ratio < 1e-2:
        print("    *** NEAR-LOW-RANK (within 1% of rank-deficiency) ***")
    rs = [int(x) for x in m.sum(1)]
    cs = [int(x) for x in m.sum(0)]
    print(f"    rowsums({r})={rs}")
    print(f"    colsums({c})={cs}")
    # anchor collisions suppressed by the gate
    for lab, L in (("RS", RS), ("CS", CS)):
        if rs == L:
            print(f"    *** rowsums == {lab} ***")
        if cs == L:
            print(f"    *** colsums == {lab} ***")
        if rs + cs == L:
            print(f"    *** rowsums+colsums == {lab} ***")
        if cs + rs == L:
            print(f"    *** colsums+rowsums == {lab} ***")
    for lab, S in (("rowsum set", set(rs)), ("colsum set", set(cs))):
        if S == RKEY_ONES:
            print(f"    *** {lab} == white-rabbit 0x41D464 ones ***")
        if len(S & RKEY_ONES) >= 8:
            print(f"    *** {lab} shares >=8 of 9 white-rabbit key bits ***")
    return full_rank, g


def control_reproduce_defective_baseline():
    """POSITIVE CONTROL: reproduce row 146's historical 3x23 reading from the
    69-token crop. The repair must not change this."""
    print("=== 0. POSITIVE CONTROL: reproduce the SUPPRESSED baseline ===")
    print(f"  crop tokens={len(DBBIB_CROP)}  authoritative tokens={len(DBBIB_91)}")
    assert len(DBBIB_CROP) == 69, len(DBBIB_CROP)
    assert len(DBBIB_91) == 91, len(DBBIB_91)
    # The gate at lattice_probe.py:133 is TRUE for the crop, FALSE for 91.
    print(f"  gate (len==69 or len==570) on crop    -> "
          f"{len(DBBIB_CROP) == 69 or len(DBBIB_CROP) == 570}")
    print(f"  gate (len==69 or len==570) on dbbib_91 -> "
          f"{len(DBBIB_91) == 69 or len(DBBIB_91) == 570}")
    print("  ^ second line FALSE == the defect: section-A reshapes are skipped")
    print("\n  -- historical crop reshapes (what row 146 actually measured) --")
    for kind in ("v0", "v1", "canon"):
        v = _lp.enc(DBBIB_CROP, kind)
        for r, c in _lp.factors(len(DBBIB_CROP)):
            _lp.report(f"CROP/{kind}", r, c, np.array(v).reshape(r, c))
    print(f"\n  crop factor pairs: {_lp.factors(69)}   "
          f"91-token factor pairs: {_lp.factors(91)}")
    print("  ^ row 146's dbbib rank/gcd evidence rests on 3x23 ONLY; 7x13/13x7 "
          "were never measured")


def main() -> int:
    print("=== lattice_probe_91: suppressed reshape fingerprint on dbbib_91 ===")
    control_reproduce_defective_baseline()

    print("\n=== 1. repaired reshape fingerprint on dbbib_91 (both orientations) ===")
    seen = []
    for kind in ("v0", "v1", "canon"):
        v = _lp.enc(DBBIB_91, kind)
        print(f"\n-- map {kind}: n={len(v)} sum={sum(v)} "
              f"unique={sorted(set(v))} --")
        for r, c in _lp.factors(len(v)):
            full_rank, g = reshape_report(f"dbbib91/{kind}", v, r, c)
            seen.append(full_rank)
            # transpose orientation, which factors() never returns
            full_rank_t, g_t = reshape_report(f"dbbib91/{kind}", v, c, r)
            seen.append(full_rank_t)

    print("\n=== 2. verdict ===")
    print(f"  reshapes measured: {len(seen)}  full-rank: {sum(seen)}")
    print(f"  rank-deficient: {len(seen) - sum(seen)}")
    print("  RESULT: row 146's structural claim is CONFIRMED on dbbib_91 iff")
    print("          every reshape above is full-rank with gcd 1.")
    print("  No oracle/gate calls were made by this tool.")
    return 0


if __name__ == "__main__":
    sys.exit(main())