#!/usr/bin/env python3
"""grid_route_battery.py -- late-269. The 24 coloured cells of
follow-white-rabbit-grid.json are NOT a photography-based crop of the DCL land
map (late-268: certified negative over 7 snapshots, ~460 M windows, 0 hits).
The remaining "world-map integrated" reading is to treat the 14x14 board as a
ROUTE MAP: connect the 24 coloured cells in various traversals and read the
edge metrics (walk distances, turn vectors) as digit streams, then decode those
streams under the certified VIC checkerboard family and oracle the plaintexts.

Families generated here:
  A. route distances  : for each ordering of the 24 cells, consecutive
        manhattan / chebyshev / rounded-euclidean / |dx| / |dy| distances,
        reduced by mod 9 and mod 10 -> 23-digit streams.
  B. turn vectors     : each step encoded as 9-state signed (dx,dy) and as a
        4-state manhattan direction -> digit streams.
  C. colour bits      : blue=1 yellow=0 over each ordering -> 24-bit integer ->
        charset renders (hex, base58, base64, decimal, ascii-bin) as candidates.
All digit streams are decoded under ALPHAS (47 keyed alphabets incl. the
certified phase 3.2.2 literal) x escapes (1,4)/(4,1); clean decodes enter the
candidate file raw/lower/upper/reversed. Candidates feed BOTH funded gates
(oracle.py small 1.25 BTC, oracle_dualite.py Dualite 3.75 BTC).

WITNESS (certified):
  * pipeline: decode(encode(P,'control'), 'control') == P for the certified
    phase-322 checkerboard under both escape pairs.
  * route: a synthetic 24-cell set on a wide column axis is built whose
    consecutive manhattan distances equal a chosen 23-digit code (digits in
    0..8, no VIC escape digits); the generator re-finds exactly that code and
    the VIC decode of the code (a known plaintext) appears among the candidate
    forms. Injection -> re-find through the SAME code path.
Usage:
    python3 tools/grid_route_battery.py --selftest
    python3 tools/grid_route_battery.py          # gen -> ~/grid_route_cands.txt
    python3 tools/grid_route_battery.py --both   # gen + run both oracles
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode, keyed28, selfcert  # noqa: E402
from leap_alphabet_sweep import ALPHAS                            # noqa: E402

GRID = json.loads(Path(os.path.join(ROOT, "data", "follow-white-rabbit-grid.json")).read_text())
BLUE = [tuple(c) for c in GRID["blue"]]      # (row, col)
YELLOW = [tuple(c) for c in GRID["yellow"]]
CELLS = BLUE + YELLOW
SB = set(BLUE)
SCRATCH = os.path.join(os.path.expanduser("~"), "grid_route_cands.txt")
CONTROL = ALPHAS["control_phase322"]
WIT = "IGNEOUSROUTEWITNESS"
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def dist_mh(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def dist_ck(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def dist_eu(a, b):
    return round((abs(a[0] - b[0]) ** 2 + abs(a[1] - b[1]) ** 2) ** 0.5)


def orderings(cells, blue_set=SB):
    """Deterministic traversals of the 24 coloured cells -> named ordered lists."""
    b = sorted(c for c in cells if c in blue_set)
    y = sorted(c for c in cells if c not in blue_set)
    by_rc = sorted(cells)
    by_cr = sorted(cells, key=lambda c: (c[1], c[0]))
    by_sum = sorted(cells, key=lambda c: (c[0] + c[1], c[0], c[1]))
    by_diff = sorted(cells, key=lambda c: (c[0] - c[1], c[0], c[1]))
    by_d0 = sorted(cells, key=lambda c: (dist_mh((0, 0), c), c[0], c[1]))
    by_dc = sorted(cells, key=lambda c: (dist_mh((6, 6), c), c[0], c[1]))
    orders = {
        "rc": by_rc, "cr": by_cr, "sum": by_sum, "diff": by_diff,
        "d0": by_d0, "dc": by_dc,
        "blue_yellow": b + y, "yellow_blue": y + b,
    }
    rows = {}
    for c in cells:
        rows.setdefault(c[0], []).append(c[1])
    rowmax = max(rows) + 1
    boust = []
    for r in range(rowmax):
        cs = sorted(rows.get(r, []))
        boust += [(r, c) for c in (cs if r % 2 == 0 else cs[::-1])]
    orders["boust"] = boust
    return orders


def reductions(ds):
    """Distance-metric streams for one ordered cell list -> dict of digit strings."""
    out = {}
    n = len(ds)
    for name, fn in (("mh", dist_mh), ("ck", dist_ck), ("eu", dist_eu)):
        d = [fn(ds[i], ds[i + 1]) for i in range(n - 1)]
        out[f"{name}m9"] = "".join(str(x % 9) for x in d)
        out[f"{name}m10"] = "".join(str(x % 10) for x in d)
        out[f"{name}raw"] = "".join(str(x) for x in d)
    dx = [ds[i + 1][1] - ds[i][1] for i in range(n - 1)]
    dy = [ds[i + 1][0] - ds[i][0] for i in range(n - 1)]
    out["dxm9"] = "".join(str(x % 9) for x in dx)
    out["dxm10"] = "".join(str((x + 9) % 10) for x in dx)
    out["dym9"] = "".join(str(x % 9) for x in dy)
    out["dym10"] = "".join(str((x + 9) % 10) for x in dy)
    nine = [str((a + 1) * 3 + (b + 1)) for a, b in zip(dx, dy)]
    out["dir9"] = "".join(nine)
    dirm = []
    for a, b in zip(dx, dy):
        if b < 0: dirm.append("0")
        elif b > 0: dirm.append("1")
        elif a < 0: dirm.append("2")
        else: dirm.append("3")
    out["dir4"] = "".join(dirm)
    return out


def color_bits(order, blue_set=SB):
    bits = "".join("1" if c in blue_set else "0" for c in order)
    v = int(bits, 2)
    b3 = v.to_bytes(3, "big")
    b3r = v.to_bytes(3, "little")
    b58 = ""
    x = v
    while x:
        x, r = divmod(x, 58)
        b58 = B58[r] + b58
    b58 = b58 or "1"
    return {"bits_raw": bits, "hex": format(v, "06X"), "dec": str(v),
            "dec_rev": str(int(bits[::-1], 2)), "hex_rev": format(int(bits[::-1], 2), "06X"),
            "b58": b58, "b64": base64.b64encode(b3).decode(),
            "b64_le": base64.b64encode(b3r).decode()}


def clean(pt):
    return "?" not in pt and 8 <= len(pt) <= 2000


def gen_candidates(cells, blue_set, out_path):
    cands = set()
    streams = {}
    for oname, order in orderings(cells, blue_set).items():
        for rname, f in reductions(order).items():
            streams[f"{oname}.{rname}"] = f
    bits = {}
    for oname, order in orderings(cells, blue_set).items():
        for k, v in color_bits(order, blue_set).items():
            bits[f"{oname}.{k}"] = v
    n_digits = 0
    for ds in streams.values():
        for alpha28 in ALPHAS.values():
            for e1, e2 in ((1, 4), (4, 1)):
                pt = decode(ds, build_grid(alpha28, e1, e2), e1, e2)
                n_digits += 1
                if clean(pt):
                    cands.add(pt)
                    cands.add(pt.lower())
                    cands.add(pt.upper())
                    cands.add(pt[::-1])
    cands.update(bits.values())
    with open(out_path, "w") as f:
        f.writelines(c + "\n" for c in sorted(cands))
    return len(cands), n_digits, len(streams), len(bits)


def synthetic_cells(targets):
    """24 cells reproducing `targets` (each digit in 1..9) as consecutive
    manhattan distances under the rc (sort by row,col) ordering: rows strictly
    increasing 0..23, columns = prefix sum of (target-1). No 14x14 bound is
    asserted on the synthetic witness grid."""
    cells = []
    c = 0
    for i in range(len(targets) + 1):
        row, col = i, c
        cells.append((row, col))
        if i < len(targets):
            c += targets[i] - 1
    assert len(cells) == 24
    return cells


def random_target_digits(seed=0xBEEF, n=23):
    """Deterministic 23-digit string over 1..9 whose VIC decode under the
    certified board (escapes 1,4) is clean (no '?' and length >= 8)."""
    import random
    r = random.Random(seed)
    for _ in range(200000):
        t = "".join(r.choice("123456789") for _ in range(n))
        pt = decode(t, build_grid(CONTROL, 1, 4), 1, 4)
        if "?" not in pt and len(pt) >= 8:
            return t, pt
    raise RuntimeError("no clean witness target found")


def selftest():
    ok = True
    ctol = build_grid(CONTROL, 1, 4)
    for e1, e2 in ((1, 4), (4, 1)):
        c2 = build_grid(CONTROL, e1, e2)
        num = [next(cc for cc, v in c2.items() if v == ch) for ch in WIT]
        if not (num and decode("".join(num), c2, e1, e2) == WIT):
            return False, "pipeline roundtrip failed"
    # build a 23-digit code (1..9) that VIC-decodes cleanly under the certified
    # board, place 24 cells that reproduce those distances RC-row-major
    target, pt = random_target_digits()
    cells = synthetic_cells([int(x) for x in target])
    order = sorted(cells)  # rc ordering used by the generator
    mh = [dist_mh(order[i], order[i + 1]) for i in range(len(order) - 1)]
    got = "".join(str(x) for x in mh)
    if got != target:
        return False, f"route reproduction mismatch: {got} vs {target}"
    # inject the synthetic cells through the SAME candidate pipeline
    blue_set = set([cells[0]])
    n_c, _, n_s, n_b = gen_candidates(cells, blue_set, SCRATCH + ".wit")
    forms = set(open(SCRATCH + ".wit").read().splitlines())
    if pt not in forms and pt.lower() not in forms and pt.upper() not in forms and pt[::-1] not in forms:
        return False, f"witness plaintext not re-found in {n_c} candidates"
    os.remove(SCRATCH + ".wit")
    return True, f"selftest OK (witness pt {pt!r} re-found in {n_c} forms)"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true", help="run certification")
    ap.add_argument("--both", action="store_true", help="also run both oracles over candidates")
    args = ap.parse_args()

    if args.selftest:
        st, msg = selftest()
        print(msg)
        return 0 if st else 1

    t0 = time.time()
    n_c, n_d, n_s, n_b = gen_candidates(CELLS, SB, SCRATCH)
    print(f"[grid_route] {n_s} digit-stream families -> {n_d} decode forms "
          f"+ {n_b} colour-bit renders = {n_c} candidates -> {SCRATCH} ({time.time()-t0:.0f}s)")
    if args.both:
        for prog in ("oracle.py", "oracle_dualite.py"):
            p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", prog), "--stdin"],
                               stdin=open(SCRATCH), capture_output=True, text=True)
            out = [l for l in p.stdout.splitlines() if l.strip()]
            print(f"[grid_route] {prog}: {out[-1] if out else 'NO MATCH'}")
            if "MATCH" in p.stdout:
                print(p.stdout)
                return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())