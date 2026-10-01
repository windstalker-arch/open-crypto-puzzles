#!/usr/bin/env python3
"""xor_halfpair_sweep.py -- HALF-AND-BETTER-HALF (17/18) half-triangle XOR
candidate sweep of the digit streams, oracle-fed on both gate addresses.

Motive: a 35 = [1,2,3,4,5,6,7,7] unit splits as a 17-cell (1..5,2) and an
18-cell (1..5,3) half-triangle.  For every 17/18 half-pair of the streams we
reduce each half-triangle (row-XOR, col-XOR, apex) and combine the pair
(apex XOR, apex sum); cross-block sequences over all units form X candidates.

Certified oracle path: tools/oracle.py and tools/oracle_dualite.py --stdin,
upper+lower cases.  N is small (no t concern).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.loads(Path(os.path.join(BASE, "data",
                                   "finalpage-digit-streams.json")).read_text())
DBBIB = DATA["dbbib_91"].lower()   # authoritative; DATA["dbbib"] is the crop
FAED = DATA["faed_570"].rstrip("z").lower()
CANON = {"a": 8, "b": 1, "c": 5, "d": 0, "e": 6, "f": 3, "g": 7, "h": 4, "i": 2}

L17 = [1, 2, 3, 4, 5, 2]
L18 = [1, 2, 3, 4, 5, 3]


def val(stream, kind):
    if kind == "pos":
        return [ord(c) - 97 for c in stream]
    if kind == "one":
        return [ord(c) - 96 for c in stream]
    return [CANON[c] for c in stream]


def half_tri(vals, layout):
    rows, i = [], 0
    for ln in layout:
        rows.append(vals[i:i + ln])
        i += ln
    row_xor = []
    for r in rows:
        x = 0
        for v in r:
            x ^= v
        row_xor.append(x)
    col_xor = []
    for c in range(len(rows[0])):
        x = 0
        for r in rows:
            if c < len(r):
                x ^= r[c]
        col_xor.append(x)
    row = vals[:]
    while len(row) > 1:
        row = [row[i] ^ row[i + 1] for i in range(len(row) - 1)]
    apex = row[0] if row else 0
    return row_xor, col_xor, apex


def render(seq, fmt):
    if fmt == "dig":
        return "".join(str(v) for v in seq)
    if fmt == "sym":
        return "".join("abcdefghijklmno"[v % 15] for v in seq)
    return "".join(chr(65 + v % 26) for v in seq)


def main() -> int:
    cands = {}
    meta = {}
    for stream_name, stream in (("dbbib", DBBIB), ("faed", FAED)):
        for kind in ("pos", "one", "canon"):
            v = val(stream, kind)
            for start in (17, 18):
                units = []
                rest = v[:]
                cur = start
                while len(rest) >= cur:
                    units.append(rest[:cur])
                    rest = rest[cur:]
                    cur = 35 - cur
                a17 = [(half_tri(b, L17)[2], half_tri(b, L18)[2]) for b in units]
                a17_s = [p[0] for p in a17]
                a18_s = [p[1] for p in a17]
                ax = [p[0] ^ p[1] for p in a17]
                sm = [p[0] + p[1] for p in a17]
                for lab, seq in (("a17", a17_s), ("a18", a18_s),
                                 ("xor", ax), ("sum", sm)):
                    meta[f"{stream_name}/{kind}/s{start}/{lab}"] = (
                        len(units), seq)
                    for fmt in ("dig", "sym", "let"):
                        for seqv, order in ((seq, "fwd"), (seq[::-1], "rev")):
                            s = render(seqv, fmt)
                            cands[f"{stream_name}|{kind}|s{start}|{lab}|"
                                  f"{fmt}|{order}"] = s
            # axis+bounds cross-block apex/cx sequences for T35 too
            tot = 35
            blocks = [v[i:i + tot] for i in range(0, len(v), tot)
                      if len(v[i:i + tot]) == tot]
            for lab, seq in (
                ("apex35/sum", [sum(b) for b in blocks]),
                ("apex35/xor", [half_tri(b, L17 + [7])[2] for b in blocks]),
            ):
                for fmt in ("dig", "sym"):
                    cands[f"{stream_name}|{kind}|T35|{lab}|{fmt}"] = \
                        render(seq, fmt)

    print(f"{len(cands)} unique candidate strings", flush=True)
    lines = list(cands.values())
    hit = []
    for script in ("oracle.py", "oracle_dualite.py"):
        txt = "\n".join(lines + [s.lower() for s in lines]) + "\n"
        t0 = time.time()
        p = subprocess.run([sys.executable, os.path.join(BASE, "tools",
                                                         script), "--stdin"],
                           input=txt, capture_output=True, text=True)
        rc = p.returncode
        print(f"  {script}: exit={rc} ({time.time() - t0:.0f}s "
              f"{'MATCH' if rc == 0 else 'no match'})", flush=True)
        if rc == 0:
            hit.append(script)
    print(f"overall: {'MATCH FOUND' if hit else 'no match'}")
    return 0 if hit else 1


if __name__ == "__main__":
    raise SystemExit(main())