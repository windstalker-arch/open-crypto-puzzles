#!/usr/bin/env python3
"""vic_alphamap_grid.py -- checkerboard decode battery over "page-typed" a..i digit maps.

Lead-0 audit cell (2026-09-24): every prior checkerboard sweep used only two distinct
a..i->digit maps -- pos "abcdefghi" and canon "dbifhcega" (note: canon == DBIFHCEG ==
dbbib's first-occurrence order, so canon and the 'DBIFHCEG' row-194 map are identical).
This tool sweeps the never-tested family: for each keyed28 alphabet, use the ORDER in
which its own letters a..i appear ("as typed on page" interpreter), plus the
stream-derived faedgcbhi map, plus pos/canon as control baselines.

Certified 3.2.2 guarantees (imported from certified_vic.build_grid/decode): the decoder
is verbatim the phase-3.2.2 vector. A mapping is a 9-char permutation of a..i; the
mapped digit stream is checkerboard-decoded straight (no transposition) and under the
columnar transpose lengths proven for this family {13=matrixsumlist, 38=lastwordsbefore
archichoice 26 + thispassword 12, 7}, escapes {1,4} and {2,5}, fwd/rev.

Output: decodes filtered to alphabetic+space ratio; fed to oracle.py and
oracle_dualite.py via --stdin.
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
from keyed_vic_battery import DBBIB, FAED, keyed28, transposed, mapped, run_alphabet  # noqa: E402

CERT_ALPHA = "FUBCDORA.LETHINGKYMVPS.JQZXW"

KEYWORDS = [
    "salphasion", "cosmicduality", "yellowblue", "primes", "yinyang",
    "btcseed", "whiterabbit", "theseedisplanted", "matrixsumlist",
    "lastwordsbeforearchichoice", "yourlastcommand", "zeroedout",
    "shabef", "ourfirsthint", "infront", "halfandbetterhalf",
]

POS = "abcdefghi"
CANON = "dbifhcega"
FAED_MAP = "faedgcbhi"


def ai_suborder(alpha28: str) -> str:
    """a..i letters of an alphabet in their left-to-right order -> 9-char map."""
    return "".join(c.lower() for c in alpha28 if c.upper() in "ABCDEFGHI")


def stream_combos() -> list[tuple[str, str]]:
    return [
        ("dbbib+p", DBBIB + FAED),
        ("p+dbbib", FAED + DBBIB),
        ("dbbib+rep+faed", DBBIB + DBBIB + FAED),
        ("interleave(dp)", "".join(a + b for a, b in zip(DBBIB, FAED[: len(DBBIB)]))),
    ]


def run_grid() -> list[str]:
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
            for esc in ((1, 4), (2, 5)):
                for trans in ([], [13], [38], [7], [3], [15], [16], [19], [23]):
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
    print(f"grid: {len(alphabets)} alphabets x maps fwd/rev x esc x "
          f"trans{{none,13,38,7,3,15,16,19,23}} x 6 stream forms "
          f"= {cells} decode cells", flush=True)
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
    ok = selfcert()
    print("SELFCERT 3.2.2:", "PASS" if ok else "FAIL", flush=True)
    if not ok:
        return 1
    cands = run_grid()
    seen = set()
    uniq = [c for c in cands if not (c in seen or seen.add(c))]
    print(f"total {len(cands)} / unique {len(uniq)} decodes", flush=True)
    oracle_step(os.path.join(ROOT, "tools", "oracle.py"), uniq)
    oracle_step(os.path.join(ROOT, "tools", "oracle_dualite.py"), uniq)
    return 0


if __name__ == "__main__":
    sys.exit(main())