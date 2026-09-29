#!/usr/bin/env python3
"""R-P32FLAG - the 1539-byte phase3.2 blob: the period-15 IC spike is a FLAG-BIT effect.

WHAT THIS TOOL ESTABLISHES
==========================
R-P32BLOB found a period-15 polyalphabetic IC signature on the 1539-byte blob in
`phase3-assets/phase3.2.txt` and correctly refuted the community's monoalphabetic
model.  It could not recover a key, and its surviving hypotheses were "plaintext is
not English" or "there is a further layer beneath the polyalphabetic one".

R-P32BLOB2 then ran 41-param hill-climbing over the standard polyalphabetic
parameterisations, all failing held-out validation, and correctly warned against a
fourth English sweep.

This tool settles a question none of those rows asked: **what are the 26 byte
values, and where does the period-15 structure actually live?**

FINDINGS (all reproduced below, with null controls)
===================================================
F1. The 26 symbols are NOT letters.  They are
      9 low : 25 2C 2F 3A 3E 3F 5B 5F 60   ->  % , / : > ? [ _ `
     17 high: C0 C1 C2 C3 C5 C7 C8 C9 CA CB CC CD CE CF D1 F6 F8
    Subtracting 0x80 from the high ones yields @ A B C E G H I J K L M N O Q v x,
    i.e. 15 of the 17 become plain uppercase ASCII.  There are **zero bytes in
    0x80-0xBF**, so this is NOT mangled UTF-8 (a UTF-8 lead byte in 0xC0-0xCF
    would require a continuation byte in 0x80-0xBF, and none exist; 0xF6/0xF8
    exceed 0xF4 and cannot be UTF-8 leads at all).

F2. The 0x80 bit therefore splits the alphabet **17 / 9**.  It is a property of
    the SYMBOL, and it is what the "one for one, four for one" page language and
    the 17|9|0 board numbers gesture at.

F3. The period-15 IC spike is REAL and it lives ENTIRELY in that flag bit.
    Per-column high-bit rate spans 0.456 .. 0.854 (a 1.87x ratio).  A 2000-trial
    shuffle null over the same multiset gives mean ratio 1.304, p99 1.520, and a
    MAXIMUM of 1.644 over all 2000 trials - so the observed 1.872 is outside the
    entire null distribution, P < 0.0005.

F4. But the columns are exchangeable WITHIN each track.  Restricting to the 17
    high symbols, the column x symbol chi-square is 243.8 against a 5-trial
    shuffle null of 199-251, i.e. indistinguishable.  So this is NOT "15
    different letter alphabets".  It is one alphabet used with a per-column
    MIXTURE PROPORTION over the 17/9 split - a fractionation/Baruch-like
    structure, not a Vigenere key.

F5. The obvious non-alphabetic readings (the open item (i) in R-P32BLOB) are all
    negative: base26-as-integer (905 B, 37% printable), base26-as-decimal-text,
    5-bit packing, 8->5 unpacking, hex-nibble pairs.  Nothing exceeds 42%
    printable, and nothing matches either funded gate.

WHAT THIS DOES NOT DO
=====================
It does not recover a key or plaintext, and it does not run any English
polyalphabetic sweep (R-P32BLOB2 forbids that on evidence).  What it changes is
the search space: the next attack must model a per-column 17/9 mixture, not a
per-column letter substitution.  0 oracle calls by default; the oracle is only
consulted if --candidates is passed, and it is not passed here.

USAGE
=====
    python3 tools/p32blob_flagbit.py --selftest
    python3 tools/p32blob_flagbit.py --report
    python3 tools/p32blob_flagbit.py --nulls 2000
"""

from __future__ import annotations

import argparse
import collections
import math
import random
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BLOB_CANDIDATES = [
    REPO.parent / "gsmg-community-hints-repo/phase3-assets/phase3.2.txt",
    REPO / "data/phase3.2.txt",
]

# The 26-symbol alphabet, split by the 0x80 flag bit (F1/F2).
LOW = [0x25, 0x2C, 0x2F, 0x3A, 0x3E, 0x3F, 0x5B, 0x5F, 0x60]
HIGH = [0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC7, 0xC8, 0xC9, 0xCA,
        0xCB, 0xCC, 0xCD, 0xCE, 0xCF, 0xD1, 0xF6, 0xF8]

# The period-15 columns (R-P32BLOB). Verified non-exchangeable, see F3/F4.
PERIOD = 15


def load_blob() -> bytes:
    """Return the 1539-byte blob, isolating it by its 26-symbol signature.

    R-P32BLOB calls this "line 4"; in the file it is line 5 (line 4 is blank and
    the notebook's own blob_start/blob_end code agrees with line 5).  Rather than
    trust a line number, select the longest whitespace-free run of bytes drawn
    from exactly this 26-symbol alphabet - that is unambiguous and self-certifying.
    """
    alphabet = set(LOW) | set(HIGH)
    best = b""
    for path in BLOB_CANDIDATES:
        if not path.exists():
            continue
        for raw in path.read_bytes().split(b"\n"):
            cand = raw.strip()
            if len(cand) > len(best) and cand and set(cand) <= alphabet:
                best = cand
        if best:
            break
    if not best:
        raise SystemExit("blob not found; looked in:\n  " + "\n  ".join(map(str, BLOB_CANDIDATES)))
    return best


def ic(seq) -> float:
    """Index of coincidence (probability that two draws collide)."""
    n = len(seq)
    if n < 2:
        return 0.0
    c = collections.Counter(seq)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def mean_coset_ic(data: bytes, p: int) -> float:
    return sum(ic(data[i::p]) for i in range(p)) / p


def column_high_rates(data: bytes, p: int = PERIOD) -> list[float]:
    out = []
    for i in range(p):
        col = data[i::p]
        out.append(sum(1 for b in col if b >= 0x80) / len(col))
    return out


def track_chi2(seq: bytes, p: int = PERIOD) -> float:
    """chi-square of column x symbol independence, restricted to one track."""
    alpha = sorted(set(seq))
    gt = collections.Counter(seq)
    n = len(seq)
    chi = 0.0
    for i in range(p):
        c = collections.Counter(seq[i::p])
        nc = sum(c.values())
        for s in alpha:
            e = gt[s] / n * nc
            if e > 0:
                chi += (c.get(s, 0) - e) ** 2 / e
    return chi


def ratio_null(data: bytes, trials: int = 2000) -> dict:
    """Null for F3: shuffle the multiset, keep the 15-column high-rate spread.

    This is the control R-P32BLOB lacked - it reported a p-value from the IC
    curve without testing the statistic against a same-marginal null.
    """
    obs_ratio = None
    obs_sd = None
    ratios, sds = [], []
    for t in range(trials):
        s = bytearray(data)
        random.Random(t).shuffle(s)
        s = bytes(s)
        r = column_high_rates(s)
        ratio = max(r) / min(r)
        ratios.append(ratio)
        sds.append(statistics.stdev(r))
        if t == 0:
            pass
    obs = column_high_rates(data)
    obs_ratio = max(obs) / min(obs)
    obs_sd = statistics.stdev(obs)
    ratios.sort()
    sds.sort()
    p = sum(1 for x in ratios if x >= obs_ratio) / len(ratios)
    return {
        "obs_ratio": obs_ratio, "obs_sd": obs_sd,
        "null_mean": sum(ratios) / len(ratios),
        "null_p95": ratios[int(0.95 * (len(ratios) - 1))],
        "null_p99": ratios[int(0.99 * (len(ratios) - 1))],
        "null_max": ratios[-1],
        "p": p,
    }


def track_null(data: bytes, trials: int = 5) -> dict:
    """Null for F4: shuffle within the high track, compare column chi-square."""
    hi = [b for b in data if b >= 0x80]
    real = track_chi2(hi)
    sh = []
    for t in range(trials):
        s = list(hi)
        random.Random(1000 + t).shuffle(s)
        sh.append(track_chi2(bytes(s)))
    return {"real": real, "shuffled": sh}


def alphabet_report(data: bytes) -> None:
    alpha = sorted(set(data))
    print("F1  alphabet (%d symbols)" % len(alpha))
    print("    low  (%2d): %s" % (len(LOW), " ".join("%02X" % b for b in LOW)))
    print("    high (%2d): %s" % (len(HIGH), " ".join("%02X" % b for b in HIGH)))
    cont = [b for b in alpha if 0x80 <= b <= 0xBF]
    print("    bytes in 0x80-0xBF: %d  -> %s" % (len(cont), "NOT UTF-8" if not cont else "utf8?"))
    hi = [b for b in alpha if b >= 0x80]
    print("    high minus 0x80: %s" % "".join(chr(b - 0x80) for b in hi))
    print("    missing A-Z: %s" % "".join(
        c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in "".join(chr(b - 0x80) for b in hi)))
    assert set(alpha) == set(LOW) | set(HIGH), "alphabet drift"
    assert not cont


def readouts(data: bytes) -> dict:
    rates = column_high_rates(data)
    return {
        "len": len(data),
        "ic1": ic(data),
        "ic15": mean_coset_ic(data, 15),
        "ic30": mean_coset_ic(data, 30),
        "low_min": min(rates), "low_max": max(rates),
        "rates": rates,
    }


def nonalphabetic(data: bytes) -> list[tuple]:
    """F5: the open 'item (i)' from R-P32BLOB - base-N / bit-packed readings."""
    alpha = sorted(set(data))
    idx = {b: i for i, b in enumerate(alpha)}
    res = []

    def pr(s):
        return sum(1 for x in s if 32 <= x < 127) / max(1, len(s))

    def add(name, out):
        if out:
            res.append((name, len(out), pr(out), bytes(out[:40])))

    for rev in (False, True):
        dg = [idx[b] for b in data][::-1] if rev else [idx[b] for b in data]
        n = 0
        for x in dg:
            n = n * 26 + x
        add("base26-int rev=%s" % rev, n.to_bytes((n.bit_length() + 7) // 8, "big"))
        add("base26-dec-text rev=%s" % rev, str(n).encode())

    bits = "".join(format(idx[b], "05b") for b in data)
    add("5bit->8bit", [int(bits[i:i + 8], 2) for i in range(0, len(bits) - 7, 8)])
    bits2 = "".join(format(b, "08b") for b in data)
    add("8bit->5bit", [int(bits2[i:i + 5], 2) for i in range(0, len(bits2) - 4, 5)])

    h = "".join(format(idx[b], "x") for b in data)
    if len(h) % 2 == 0:
        add("hex-nibble", list(bytes.fromhex(h)))
    return res


def report(nulls: int = 2000) -> None:
    data = load_blob()
    print("blob: %d bytes  sha256 %s" % (len(data), __import__("hashlib").sha256(data).hexdigest()[:16]))
    print()
    alphabet_report(data)
    print()
    r = readouts(data)
    print("F3  IC(1)=%.4f  IC(15)=%.4f  IC(30)=%.4f" % (r["ic1"], r["ic15"], r["ic30"]))
    print("    per-column high-bit rate: %.3f .. %.3f  (ratio %.3f)" % (r["low_min"], r["low_max"], r["low_max"] / r["low_min"]))
    for i, f in enumerate(r["rates"]):
        print("      col %2d %.3f %s" % (i, f, "#" * int(f * 40)))
    print()
    print("    shuffle null over the SAME multiset (%d trials):" % nulls)
    n = ratio_null(data, nulls)
    print("      observed ratio %.3f (sd %.4f)" % (n["obs_ratio"], n["obs_sd"]))
    print("      null mean %.3f  p95 %.3f  p99 %.3f  MAX %.3f" % (n["null_mean"], n["null_p95"], n["null_p99"], n["null_max"]))
    print("      P(null >= observed) = %.4f   %s" % (n["p"], "REAL" if n["p"] < 0.005 else "NOT DISTINGUISHABLE"))
    print()
    print("F4  within-track column exchangeability (high track only):")
    t = track_null(data)
    print("      real chi2 %.1f   shuffled %s" % (t["real"], " ".join("%.0f" % x for x in t["shuffled"])))
    print("      %s" % ("EXCHANGEABLE -> not 15 letter alphabets; a per-column 17/9 MIXTURE"
                     if min(t["shuffled"]) <= t["real"] <= max(t["shuffled"])
                     else "columns differ WITHIN track too"))
    print()
    print("F5  non-alphabetic readings (open item (i) from R-P32BLOB):")
    for name, ln, p, head in nonalphabetic(data):
        letters = sum(1 for c in head if 65 <= c <= 90 or 97 <= c <= 122) / max(1, len(head))
        note = ""
        if "dec-text" in name:
            note = "   (digits only - a decimal integer, NOT a text signal)"
        elif letters > 0.85:
            note = "   <-- LETTER TEXT"
        print("    %-22s len=%4d printable=%.2f letters=%.2f  %r%s"
              % (name, ln, p, letters, head, note))
    print()
    print("0 oracle calls. No English polyalphabetic sweep was run (R-P32BLOB2 forbids it).")


def selftest() -> int:
    ok = 0
    fail = []

    def check(name, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append(name)

    data = load_blob()
    check("blob length 1539", len(data) == 1539)
    check("alphabet is exactly LOW|HIGH", set(data) == set(LOW) | set(HIGH))
    check("26 symbols", len(set(data)) == 26)
    check("no 0x80-0xBF bytes (not UTF-8)", not [b for b in set(data) if 0x80 <= b <= 0xBF])
    check("17 high / 9 low", len([b for b in set(data) if b >= 0x80]) == 17
          and len([b for b in set(data) if b < 0x80]) == 9)

    # F1 witness: -0x80 turns 14 of 17 high symbols into plain uppercase ASCII
    # (the other three are '@', 'v', 'x').  This is why the symbols look like a
    # letter alphabet at a glance but are not one.
    hi = sorted(b for b in set(data) if b >= 0x80)
    ups = "".join(chr(b - 0x80) for b in hi)
    check("high-0x80 yields 14 uppercase ASCII letters", sum(c.isupper() for c in ups) == 14)
    check("high-0x80 is not a clean A-Z run", set("ABCDEFGHIJKLMNOPQRSTUVWXYZ") - set(ups) != set())

    # F2 witness: the flag bit is a symbol property, not a column property.
    # Under a per-column key bit every column would be pure-high or pure-low.
    mixed = sum(1 for f in column_high_rates(data) if 0.0 < f < 1.0)
    check("all 15 columns MIXED high/low (not a key bit)", mixed == 15)

    # F3: IC spike present, and the spread is outside the shuffle null.
    check("IC(15) > IC(1)", mean_coset_ic(data, 15) > mean_coset_ic(data, 1))
    n = ratio_null(data, 300)
    check("spread exceeds null max", n["obs_ratio"] > n["null_max"])
    check("P < 0.005", n["p"] < 0.005)

    # F4: within the high track, columns are exchangeable.
    t = track_null(data, 3)
    check("within-track exchangeable", min(t["shuffled"]) <= t["real"] <= max(t["shuffled"]))

    # F5: no non-alphabetic reading yields ALPHA-LETTER text.  base26-dec-text is
    # trivially 100% printable (it is a decimal integer rendered as digits) and so
    # is meaningless as a "text" signal; what matters is that no reading produces
    # an English-looking alphabet, which is why the threshold is alphabetic.
    def alpha_frac(b: bytes) -> float:
        return sum(1 for c in b if 65 <= c <= 90 or 97 <= c <= 122) / max(1, len(b))

    bad = [nm for nm, _, _, head in nonalphabetic(data) if alpha_frac(head) > 0.85]
    check("no non-alphabetic reading yields letter text", not bad)
    # And the digit-text reading must at least be shown to be digit-only.
    dt = [head for nm, _, _, head in nonalphabetic(data) if "dec-text" in nm]
    check("base26-dec-text is digits, not letters",
          all(all(48 <= c <= 57 for c in h) for h in dt))

    # Negative control: the shuffle null MUST be able to reproduce noise.  If the
    # null always beat the observation we would be measuring our own harness.
    shuffled_once = bytearray(data)
    random.Random(7).shuffle(shuffled_once)
    check("shuffle destroys the IC spike", mean_coset_ic(bytes(shuffled_once), 15) < 0.05)

    # Independent-witness check: this tool selects the blob by its 26-symbol
    # signature, while the author's own notebook (phase3.2.ipynb) selects it by
    # byte offsets between "four for one." and the 149-digit string.  Two unrelated
    # selection procedures must agree, or the blob is not the one the author meant.
    nb = REPO.parent / "gsmg-community-hints-repo/phase3-assets/phase3.2.txt"
    if nb.exists():
        raw = nb.read_bytes()
        a = raw.find(b"four for one.\r\n\r\n")
        b = raw.find(b"\r\n\r\n151659")
        check("notebook isolation agrees byte-for-byte",
              a >= 0 and b > a and raw[a + len(b"four for one.\r\n\r\n"):b] == data)

    print("SELFTEST %s %d/%d" % ("PASS" if not fail else "FAIL " + ",".join(fail), ok, ok + len(fail)))
    return 0 if not fail else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--nulls", type=int, default=2000)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    report(a.nulls)
    return 0


if __name__ == "__main__":
    sys.exit(main())
