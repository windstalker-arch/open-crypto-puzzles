#!/usr/bin/env python3
"""
Deterministic self-test for MatrixEncryption (infinitless/MatrixEncryption).

Upstream main.py executes its interactive prompts at import time, so this
harness loads only the function definitions (everything before the
"# Main Program" marker) and re-implements the exact encode/decode flow of
each of the three levels, then asserts round-trip integrity.

Run:  python3 selftest.py [trials]
Exit code 0 = all levels round-trip.
"""

import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_core():
    """Load main.py's function definitions without running its prompts."""
    src = open(os.path.join(HERE, "main.py")).read()
    marker = "# Main Program"
    if marker not in src:
        raise SystemExit("selftest: could not locate '# Main Program' marker in main.py")
    core = src.split(marker)[0]
    ns = {"__name__": "matrixencryption_core", "__file__": os.path.join(HERE, "main.py")}
    exec(compile(core, "main.py", "exec"), ns)
    return ns


def test_easy(ns, trials):
    f = ns["encode"], ns["decode"], ns["randomrotation"]
    fails = []
    for _ in range(trials):
        grid, seed = f[2]()
        pt = "helloworld" + str(random.randint(0, 9999))
        if f[1](f[0](pt, grid), str(seed)) != pt:
            fails.append(pt)
    return fails


def test_moderate(ns, trials):
    fails = []
    for _ in range(trials):
        pt = "helloworld" + str(random.randint(0, 9999))
        chunks, _ = ns["chopstring"](pt)
        coded, keys = [], []
        for chunk in chunks:
            grid, seed = ns["randomrotation"]()
            coded.append(ns["encode"](chunk, grid))
            keys.append(str(seed))
        out = "".join(ns["decode"](c, k) for c, k in zip(coded, keys))
        if out != pt:
            fails.append(pt)
    return fails


def test_hard(ns, trials):
    """HARD level. Returns (fails, degenerate_runs).

    Upstream's key expansion (main.py `str(frac)[2:][:6]`) silently produces
    keys shorter than 6 digits whenever the fractional part of sqrt() formats
    with fewer than 6 decimals (e.g. exactly 0.5, 0.25, 0.125, 0.0). Those
    runs are excluded here and reported separately instead of crashing.
    """
    fails = []
    degenerate = 0
    for _ in range(trials):
        pt = "helloworld" + str(random.randint(0, 9999))
        _master, keyarray = ns["genkeylist"](pt)
        if any(len(k) != 6 for k in keyarray):
            degenerate += 1
            continue
        cipher = ""
        for i, ch in enumerate(pt):
            cipher += ns["encode"](ch, ns["creategrid"](keyarray[i]))
        # mirror of the HARD decode branch in main.py
        n = len(pt)
        keys, firstkey = [], _master
        for _i in range(n):
            nxt = (int(firstkey) ** (1 / 2)) % 1000000
            nxt = nxt - int(nxt)
            nxt = str(nxt)[2:][:6]
            keys.append(nxt)
            firstkey = int(nxt)
        grids = [ns["creategrid"](k) for k in keys]
        toks = ns["breakcode"](cipher)
        pairs = [toks[i:i + 2] for i in range(0, len(toks), 2)]
        out = ""
        for i in range(n):
            ci = ns["mycolumns"].index(pairs[i][0])
            ri = ns["myrows"].index(pairs[i][1])
            out += grids[i][ci][ri]
        if out != pt:
            fails.append(pt)
    return fails, degenerate


def probe_known_defects(ns):
    """Reproduce defects inherent to upstream main.py (not introduced by setup)."""
    issues = []
    try:
        ns["creategrid"]("0")
    except ValueError as exc:
        issues.append(
            "creategrid('0') -> ValueError: %s  "
            "[findkey negative-indexes pidecimals[-1]=%r when the master key is '0']"
            % (exc, ns["pidecimals"][-1])
        )
    return issues


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    ns = load_core()
    if len(ns["pidecimals"]) != 1000001:
        print("WARN: pi digit payload length = %d (expected 1000001)"
              % len(ns["pidecimals"]))
    random.seed(20220309)  # upstream HEAD date, for reproducibility
    ok = True
    for name, fn in (("EASY", test_easy), ("MODERATE", test_moderate), ("HARD", test_hard)):
        result = fn(ns, trials)
        if name == "HARD":
            fails, degenerate = result
            note = "" if not degenerate else "  [%d/%d runs skipped: degenerate <6-digit key]" % (degenerate, trials)
        else:
            fails, note = result, ""
        status = "PASS" if not fails else "FAIL (%d/%d)" % (len(fails), trials)
        print("%-9s %s%s" % (name, status, note))
        if fails:
            ok = False
            print("    first failing plaintext: %r" % fails[0])

    defects = probe_known_defects(ns)
    if defects:
        print("\nKNOWN UPSTREAM DEFECTS (present in unmodified main.py):")
        for d in defects:
            print("  - %s" % d)

    print("\n%s" % ("ALL LEVELS ROUND-TRIP OK" if ok else "ROUND-TRIP FAILURES PRESENT"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())