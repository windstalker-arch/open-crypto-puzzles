#!/usr/bin/env python3
"""R-P15FIX - why `R-P15NULL`'s chi-squared refutation of the Vigenere family failed.

`R-P15NULL` (2026-09-27) hill-climbed 15 free shifts against English on the 1,539-byte
phase-3.2 blob, scored chi 2357, found it inside its own validated noise band
(uniform random 2010-2354, own-marginals 2067-2501), and concluded the blob is NOT
"any single-alphabet shift model" but "15 independent monoalphabetic substitutions"
with "no shared alphabet to find".  It then told the next session not to re-run a
Vigenere and to hunt for 15-column key material instead.

That conclusion is false, and this tool shows why with a witness rather than an
argument.  The instrument is a 15-shift chi-squared hill-climb.  The cipher is a
fixed byte->letter substitution `L` composed with 15 shifts.  Fed the raw symbol
values, the hill-climb cannot fit a model whose alphabet is behind a substitution,
so it returns noise and the noise is read as a refutation.  Invert `L` first and the
SAME hill-climb, on the SAME data, recovers the key.

Measured (this run, real assets):

    raw symbol values, no L     total chi   3421.3   -> noise, "not a shift model"
    L applied first             total chi    511.0   -> recovers the key
                                            (~34 per column, df=25; R-P15NULL's own
                                             known-good column scored 20.4)

`R-P15NULL` reported 2357 rather than 3421 for the same regime; the difference is the
symbol->letter convention (here: the 26 byte values ranked by sorted byte order) and
not the verdict - both land an order of magnitude inside the noise band.  The point
is the contrast, not the digit.

This is the same defect as `R-P32BLOB`, reproduced one row up with better statistics:
`R-P32BLOB` also tested the blob against `yl` with a `K = P + C` periodicity test that
assumes a PURE Vigenere, got 0.108, and declared `yl` a coincidence.  Both rows
confused "my instrument cannot see the substitution" with "the substitution is absent".

Per `R-P15NULL`'s own closing note, the fix is a synthetic control measured on the
same code path.  `--selftest` supplies four: the L itself, a positive control where a
synthetic L+15-shift cipher must have its key recovered exactly, a negative control
where uniform-random symbols must stay in the noise band, and the real blob in both
directions.

Use:

    python3 tools/p15null_chitest.py --report     # the two-row chi contrast
    python3 tools/p15null_chitest.py --selftest   # rc=0 or fail
"""

from __future__ import annotations

import argparse
import hashlib
import random
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import p32key_verify as P  # noqa: E402
from p32blob_flagbit import load_blob  # noqa: E402
from p32key_verify import (  # noqa: E402
    KEY_NEGATED,
    KEY_PUBLISHED,
    PERIOD,
    build_L,
    column_maps,
    derive_key,
    load_yl,
)

A = "abcdefghijklmnopqrstuvwxyz"

# R-P15NULL's own calibration points, restated so the comparison is checkable.
GOOD_COLUMN_CHI = 20.4          # a known-good column scored this
GOOD_300_AVG_CHI = 24.8         # 300 known-good columns averaged this (df=25)
NOISE_UNIFORM = (2010, 2354)    # uniform random, 15 fitted shifts
NOISE_MARGINAL = (2067, 2501)   # blob's own marginals, 15 fitted shifts
R_P15NULL_REAL = 2357           # what it measured on the real blob

ENG = [8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153,
       0.772, 4.025, 2.406, 6.749, 7.507, 1.929, 0.095, 5.987, 6.327, 9.056,
       2.758, 0.978, 2.360, 0.150, 1.974, 0.074]


def chi(col: list[int]) -> float:
    """Unigram chi-square of a letter-index column against English, df = 25."""
    c = Counter(col)
    n = len(col)
    tot = 0.0
    for i in range(26):
        e = n * ENG[i] / 100.0
        tot += (c.get(i, 0) - e) ** 2 / e
    return tot


def fit15(vals: list[int], period: int = PERIOD) -> tuple[float, list[int]]:
    """Greedy coordinate descent over `period` free shifts.

    Returns (total chi over all columns, recovered shift for each column).  This is
    the instrument `R-P15NULL` used; a stronger optimiser could only lower the chi it
    reports, so using it makes the raw-symbol result an upper bound on the fit.
    """
    s = [0] * period
    for _ in range(80):
        moved = False
        for r in range(period):
            col = vals[r::period]
            best_t, best_v = s[r], None
            for t in range(26):
                v = chi([(c - t) % 26 for c in col])
                if best_v is None or v < best_v:
                    best_v, best_t = v, t
            if best_t != s[r]:
                s[r] = best_t
                moved = True
        if not moved:
            break
    total = sum(chi([(vals[j] - s[j % period]) % 26
                     for j in range(r, len(vals), period)]) for r in range(period))
    return total, s


def invert_L(L: dict[str, int]) -> dict[int, int]:
    return {b: A.index(ch) for ch, b in L.items()}


def real_assets() -> tuple[bytes, dict[str, int]]:
    blob = load_blob()
    yl = load_yl()
    maps = column_maps(blob, yl)
    key, _ = derive_key(maps)
    L, _ = build_L(maps, key)
    return blob, L


def identity_alphabet(blob: bytes) -> list[int]:
    """Rank the 26 distinct byte values by sorted byte order -> a-z.

    This is the reading `R-P15NULL` would have used: the blob's symbols are not
    letters, so some fixed arbitrary order has to be assumed, and assuming the wrong
    one is exactly the instrument's blind spot.
    """
    syms = sorted(set(blob))
    return [syms.index(b) for b in blob]


def measure() -> dict:
    blob, L = real_assets()
    inv = invert_L(L)
    raw_tot, _ = fit15(identity_alphabet(blob))
    plain = [inv[b] for b in blob]
    l_tot, l_shifts = fit15(plain)
    rec = [(-c) % 26 for c in l_shifts]
    return {
        "raw_total": raw_tot,
        "l_total": l_tot,
        "l_per_column": l_tot / PERIOD,
        "recovered": "".join(A[i] for i in rec),
        "L_size": len(L),
    }


# ---------------------------------------------------------------- selftest ----

def selftest() -> int:
    fails = 0

    def check(name: str, ok: bool) -> None:
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
        if not ok:
            fails += 1

    blob, L = real_assets()
    yl = load_yl()
    inv = invert_L(L)

    print("T1  L is a total bijection a-z -> 26 distinct bytes, 0 conflicts")
    check("covers a-z", sorted(L) == list(A))
    check("26 distinct byte values", len(set(L.values())) == 26)

    print("T2  POSITIVE CONTROL - synthetic L + 15 shifts: key must be recovered")
    rng = random.Random(20260929)
    alpha = list(range(26))
    rng.shuffle(alpha)                      # a random stand-in for the real L
    Lsym = {A[i]: alpha[i] for i in range(26)}
    Lsym_inv = {v: A.index(k) for k, v in Lsym.items()}
    key = [rng.randrange(26) for _ in range(PERIOD)]
    # Natural English, and long enough that the 15 columns do not tie across shift
    # choices (a short word repeated ties, and the descent then fails for a reason that
    # has nothing to do with L). This reuses the VERIFIED real plaintext on purpose: the
    # thing under test here is the instrument (L-inversion + chi fit), so the control
    # varies L and the key, which are the two things the pipeline has to recover.
    pt = load_yl()
    syn = bytes(Lsym[A[(A.index(pt[j]) + key[j % PERIOD]) % 26]] for j in range(1539))
    stot, sshifts = fit15([Lsym_inv[b] for b in syn])
    check("chi %.1f is in the known-good band (< %d)"
          % (stot, GOOD_300_AVG_CHI * PERIOD * 2),
          stot < GOOD_300_AVG_CHI * PERIOD * 2)
    # The fit returns a DECRYPTING key, which is the negation of the encrypting key
    # (same sign convention R-P32KEYVERIFY documents). Compare against that, and prove
    # recovery the stronger way: feed the recovered shifts back through the cipher.
    rec = [(-c) % 26 for c in sshifts]
    check("recovered shifts == negation of planted shifts",
          rec == [(-k) % 26 for k in key])
    dec = "".join(A[(Lsym_inv[b] - sshifts[j % PERIOD]) % 26] for j, b in enumerate(syn))
    check("the recovered key decrypts the synthetic blob to the planted plaintext", dec == pt)

    print("T3  NEGATIVE CONTROL - uniform random symbols must stay in the noise band")
    rtot, _ = fit15([rng.randrange(26) for _ in range(1539)])
    check("chi %.1f is above the noise floor (> %d)" % (rtot, NOISE_UNIFORM[0] // 2),
          rtot > NOISE_UNIFORM[0] // 2)

    print("T4  THE REAL BLOB, BOTH DIRECTIONS (this is the row's whole claim)")
    raw_tot, _ = fit15(identity_alphabet(blob))
    l_tot, l_shifts = fit15([inv[b] for b in blob])
    rec = "".join(A[(-c) % 26] for c in l_shifts)
    check("raw symbols, no L: chi %.1f is in the noise regime (> %d)"
          % (raw_tot, NOISE_MARGINAL[0]), raw_tot > NOISE_MARGINAL[0])
    check("L applied: chi %.1f collapses out of the noise regime (< %d)"
          % (l_tot, NOISE_MARGINAL[0] // 3), l_tot < NOISE_MARGINAL[0] // 3)
    check("L applied: per-column chi %.1f is near R-P15NULL's known-good %.1f"
          % (l_tot / PERIOD, GOOD_COLUMN_CHI), l_tot / PERIOD < 60)
    # One check, not two: asserting the recovered key equals KEY_NEGATED and then
    # re-asserting it is the same tautology, which is exactly the R-CERTAUDIT
    # over-claim shape. Prove recovery by pushing the key back through the cipher.
    check("the SAME hill-climb recovers the published key (%s, negated)" % KEY_PUBLISHED,
          rec == KEY_NEGATED)
    dec = P.decode(blob, L, list(l_shifts), sign=+1)
    check("that key decrypts the real blob to the known plaintext", dec == yl)
    check("the contrast is what refutes R-P15NULL (raw > 4x the L-applied fit)",
          raw_tot > 4 * l_tot)

    print()
    if fails:
        print("SELFTEST FAILED: %d check(s)" % fails)
        return 1
    print("SELFTEST PASS: 11 checks")
    return 0


def report() -> int:
    m = measure()
    blob, L = real_assets()
    print("R-P15FIX   blob %d B sha256 %s" % (len(blob), hashlib.sha256(blob).hexdigest()[:16]))
    print("           L = %d letters -> %d distinct bytes, 0 conflicts"
          % (len(L), len(set(L.values()))))
    print()
    print("R-P15NULL's instrument, run both ways (total chi over 15 columns, df=25 each):")
    print("    raw symbol values, no L      %8.1f   -> noise; 'not a shift model'" % m["raw_total"])
    print("    L applied first              %8.1f   -> %.1f per column, key recovered"
          % (m["l_total"], m["l_per_column"]))
    print("       recovered key             %s" % m["recovered"])
    print("       published key             %s  (negation; R-P32KEYVERIFY shows these are"
          % KEY_PUBLISHED)
    print("                                           the same cipher under the other convention)")
    print()
    print("R-P15NULL's own calibration band, for comparison:")
    print("    known-good column            %8.1f   | 300 such average %.1f"
          % (GOOD_COLUMN_CHI, GOOD_300_AVG_CHI))
    print("    uniform random, 15 shifts    %8d-%d" % NOISE_UNIFORM)
    print("    own marginals, 15 shifts     %8d-%d" % NOISE_MARGINAL)
    print("    real blob, 15 shifts         %8d   <- R-P15NULL's number, its verdict: noise"
          % R_P15NULL_REAL)
    print()
    print("VERDICT: the 2357 was a property of the INSTRUMENT, not of the blob. A fixed")
    print("substitution in front of the Vigenere makes a correct model unfittable by an")
    print("identity-alphabet chi test, and `R-P15NULL` read that blindness as a refutation.")
    print("Same defect as `R-P32BLOB` (a pure-Vigenere K=P+C test) one row up.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.report:
        return report()
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
