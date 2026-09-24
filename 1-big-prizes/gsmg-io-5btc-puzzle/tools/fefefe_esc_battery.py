#!/usr/bin/env python3
"""fefefe_esc_battery.py -- checkerboard escapes keyed by the FEFEFE nest cell.

Lead-0 audit cell (2026-09-24, R-FEFEFE-LOCATE): the sole 625-px FEFEFE cell of
follow_white_rabbit.png sits at grid (r=7, c=4), and was so far only tested as a
URL low-bit cell (spiral index 163 = URL byte 20 bit 3, value 0 => decode-irrelevant
for the color plane). Its OTHER documented roles were never used as CHECKERBOARD ESCAPE
KEY material: the inspection checklist's "missing '.': the certified board keys escape
columns with '.' and '/' -- '/' appears once but '.' never; is a faint cell the omitted
second-escape keying?" Reading the nest cell as that faint marker yields escape-digit
sets derived from its own coordinates/index: (7,4) / (4,7); spiral index 163 -> (1,6),
(6,3), (1,3); URL-byte index 20 -> (2,0), (0,2). Sweeps all SEVEN pairs through the SAME
certified build_grid/decode family that R-VIC-ALPHAMAP-GRID/-2 closed for the old escape
set {(1,4),(2,5),(0,4),(1,5),(2,4),(1,2)} -- every pair below is absent from that closed
set, so no cell is repeated. Dimensions mirror the closed battery exactly (17 alphabets x
page-typed maps fwd/rev x trans {none,13,38,7,3,15,16,19,23} x 6 stream forms) so the new
axis is directly comparable.

Certified guarantees: selfcert() runs the phase-3.2.2 vector first (abort on FAIL);
every decode goes through certified_vic.build_grid/decode; every unique candidate is fed
to oracle.py and oracle_dualite.py --stdin (both are --selftest'd by their own selftest
line in the ledger convention).
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from certified_vic import build_grid, decode, selfcert  # noqa: E402
from keyed_vic_battery import DBBIB, FAED, keyed28, transposed, mapped  # noqa: E402
from vic_alphamap_grid import (  # noqa: E402
    CERT_ALPHA, KEYWORDS, POS, CANON, FAED_MAP, ai_suborder, stream_combos,
)

NEST_ESCAPES = [(7, 4), (4, 7), (2, 0), (0, 2), (1, 6), (6, 3), (1, 3)]
TRANSPOSES = ([], [13], [38], [7], [3], [15], [16], [19], [23])


def run_fefefe_grid() -> list[str]:
    alphabets = [(f"cert:{CERT_ALPHA}", CERT_ALPHA)]
    for kw in KEYWORDS:
        alphabets.append((f"keyed28:{kw}", keyed28(kw, 8, 18)))

    cands: list[str] = []
    cells = 0
    for aname, alpha28 in alphabets:
        ai = ai_suborder(alpha28)
        assert len(ai) == 9 and sorted(ai) == list("abcdefghi"), (aname, ai)
        maps = [("ai", ai), ("ai-rev", ai[::-1])]
        if aname.startswith("cert"):
            maps += [("pos", POS), ("canon", CANON), ("faed", FAED_MAP),
                     ("faed-rev", FAED_MAP[::-1])]
        for mname, mraw in maps:
            imap = {c: str(i) for i, c in enumerate(mraw)}
            for esc in NEST_ESCAPES:
                for trans in TRANSPOSES:
                    for rev in (False, True):
                        ctol = build_grid(alpha28, *esc)
                        streams = [("dbbib", DBBIB), ("faed", FAED)] + stream_combos()
                        for sname, stream in streams:
                            digits = mapped(stream, imap)
                            if rev:
                                digits = digits[::-1]
                            layers = [(f"{sname}", digits)]
                            for L in trans:
                                layers.append((f"{sname}-T{L}", transposed(digits, L)))
                            for lname, ldg in layers:
                                out = decode(ldg, ctol, *esc)
                                cands.append(out)
                                cells += 1
    print(f"fefefe-esc: {len(alphabets)} alphabets x maps fwd/rev x "
          f"{len(NEST_ESCAPES)} nest escapes {NEST_ESCAPES} x "
          f"trans{{none,13,38,7,3,15,16,19,23}} x 6 stream forms = {cells} decode cells",
          flush=True)
    return cands


def oracle_step(path: str, cands: list[str]) -> tuple[bool, float]:
    n = len(cands)
    t0 = time.time()
    found = False
    p = subprocess.Popen(
        [sys.executable, path, "--stdin"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, text=True,
    )
    out, _ = p.communicate("\n".join(cands) + "\n")
    dt = time.time() - t0
    for line in out.splitlines():
        if line.startswith("MATCH"):
            found = True
            print(f"MATCH via {path}: {line}", flush=True)
    print(f"oracle {os.path.basename(path)}: {n} candidates in {dt:.0f}s "
          f"({n/dt:.0f}/s) -> {'MATCH FOUND' if found else 'no match'}", flush=True)
    return found, dt


def main() -> int:
    print("NEST-ESC: N = alphabets x maps x 7 escapes x 9 trans-forms x ~6 streams x rev "
          "(expect ~50000 decode cells, uniques small after de-dup)", flush=True)
    ok = selfcert()
    print("SELFCERT 3.2.2:", "PASS" if ok else "FAIL", flush=True)
    if not ok:
        return 1
    cands = run_fefefe_grid()
    seen = set()
    uniq = [c for c in cands if not (c in seen or seen.add(c))]
    print(f"total {len(cands)} / unique {len(uniq)} decodes", flush=True)
    a = oracle_step(os.path.join(ROOT, "tools", "oracle.py"), uniq)
    b = oracle_step(os.path.join(ROOT, "tools", "oracle_dualite.py"), uniq)
    small_n, small_t = a[1], b[1]
    print(f"RATE: total oracle time {small_n + small_t:.0f}s for {len(uniq)} uniques", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())