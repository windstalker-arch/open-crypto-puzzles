#!/usr/bin/env python3
"""grid_route_interp_sweep.py -- late-270. Route-EDGE geometry of the 24
coloured white-rabbit-grid cells as the a..i -> digit INTERPRETER for the REAL
ciphertext streams dbbib_91 / faed_570 (unlike late-269, which decoded grid-born
digit streams; unlike rows 182/196-198, the 9 interpreter values are derived from
route edges/cumulative geometry, not from flat cell coordinates or the rabbit body).

Interpreter construction: for each of the 8 dihedral transforms of the grid, 9
traversals (row/col-major, sum/diff, dist-from-corner/center, blue-then-yellow,
yellow-then-blue, boustrophedon) and 3 edge metrics (manhattan/chebyshev/
rounded-euclidean), the 9 YELLOW waypoints are the alphabet's 9 symbols; their
route values (cumulative metric at arrival, the arriving edge's metric, distance
to nearest blue) are clamped by mod 9 / mod 10 to digits {a..i}->digit tables,
in natural and reversed waypoint order; a rank-based family (waypoint rank by
value, off 0/1) complements the value-based family. Same families over the
first-9 blue cells and the color-run segment lengths.

Decode chain (certified): certified build_grid/decode (tools/certified_vic.py)
with escapes (1,4)/(4,1) over every ALPHAS entry (47 alphabets incl. the
verified phase-322 literal). Clean (?-free, len 8..2000) decodes of the real
dbbib/faed are pushed raw/lower/upper/reversed into the candidate file and fed
to BOTH funded-gate oracles.

WITNESS (certified): a synthetic grid + an injected letter stream. A target
plaintext P is searched whose VIC code under the certified board avoids digit 9;
the synthetic route's model-9 value table maps each code digit back to the
driving letter; the generator's own translator re-derives that table from the
synthetic geometry, decodes the injected stream, and the plaintext P re-appears
among the candidate forms -- injection -> re-find through the SAME code path.

Usage:
    python3 tools/grid_route_interp_sweep.py --selftest
    python3 tools/grid_route_interp_sweep.py --both    # gen + both oracles
    python3 tools/grid_route_interp_sweep.py           # gen -> ~/grid_route_interp_cands.txt
"""
from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode  # noqa: E402
from leap_alphabet_sweep import ALPHAS         # noqa: E402

D = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())
DBBI = D["dbbib_91"]
FAED = D["faed_570"].rstrip("z")
assert len(DBBI) == 91 and len(FAED) == 570
GRID = json.loads(Path(os.path.join(ROOT, "data", "follow-white-rabbit-grid.json")).read_text())
BLUE = [tuple(c) for c in GRID["blue"]]
YELLOW = [tuple(c) for c in GRID["yellow"]]
SCRATCH = os.path.join(os.path.expanduser("~"), "grid_route_interp_cands.txt")
CONTROL = ALPHAS["control_phase322"]
STREAMS = {"dbbi91": DBBI, "faed": FAED}
RNG = random.Random(0xC010)


def transform(cells, kid):
    """Dihedral transform of a 14x14 grid's cell list."""
    r, c = 0, 1
    if kid == "id":      f = lambda p: (p[r], p[c])
    elif kid == "r90":   f = lambda p: (p[c], 13 - p[r])
    elif kid == "r180":  f = lambda p: (13 - p[r], 13 - p[c])
    elif kid == "r270":  f = lambda p: (13 - p[c], p[r])
    elif kid == "rx":    f = lambda p: (13 - p[r], p[c])
    elif kid == "ry":    f = lambda p: (p[r], 13 - p[c])
    elif kid == "rd":    f = lambda p: (p[c], p[r])
    elif kid == "rad":   f = lambda p: (13 - p[c], 13 - p[r])
    else: raise ValueError(kid)
    return [f(p) for p in cells]


def dist(fn, a, b):
    if fn == "mh": return abs(a[0] - b[0]) + abs(a[1] - b[1])
    if fn == "ck": return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    return round((abs(a[0] - b[0]) ** 2 + abs(a[1] - b[1]) ** 2) ** 0.5)


def cortex(order, fn):
    """Edge values along an ordered cell list (length-1 list)."""
    return [dist(fn, order[i], order[i + 1]) for i in range(len(order) - 1)]


def traversal(cells, blue_set, name):
    b = sorted(c for c in cells if c in blue_set)
    y = sorted(c for c in cells if c not in blue_set)
    if name == "rc": return sorted(cells)
    if name == "cr": return sorted(cells, key=lambda c: (c[1], c[0]))
    if name == "sum": return sorted(cells, key=lambda c: (c[0] + c[1], c[0], c[1]))
    if name == "diff": return sorted(cells, key=lambda c: (c[0] - c[1], c[0], c[1]))
    if name == "d0": return sorted(cells, key=lambda c: (abs(c[0]) + abs(c[1]), c[0], c[1]))
    if name == "dc": return sorted(cells, key=lambda c: (abs(c[0] - 13) + abs(c[1] - 13), c[0], c[1]))
    if name == "by": return b + y
    if name == "yb": return y + b
    rows = {}
    for c in cells: rows.setdefault(c[0], []).append(c[1])
    out = []
    for r in sorted(rows):
        cs = sorted(rows[r])
        out += [(r, x) for x in (cs if r % 2 == 0 else cs[::-1])]
    return out


def interp_tables(synth=None):
    """Return {name: table} where table is a 9-list indexed by ord('a'..'i').
    synth=(blue_set, cells) overrides the real grid for the witness."""
    if synth is not None:
        cells, blue_set = synth
        cb = [c for c in cells if c in blue_set]
        cy = [c for c in cells if c not in blue_set]
        d4 = {"id": None}
    else:
        cells, blue_set = BLUE + YELLOW, set(BLUE)
        cb, cy = None, None
        d4 = {k: None for k in ("id", "r90", "r180", "r270", "rx", "ry", "rd", "rad")}
    tables = {}
    for dname in d4:
        if synth is not None:
            allc, bset = cells, blue_set
        else:
            cb, cy = transform(BLUE, dname), transform(YELLOW, dname)
            allc = cb + cy
            bset = set(cb)
        for tname in ("rc", "cr", "sum", "diff", "d0", "dc", "by", "yb", "boust"):
            order = traversal(allc, bset, tname)
            edges = {fn: cortex(order, fn) for fn in ("mh", "ck", "eu")}
            for fn, ev in edges.items():
                # cumulative value at arrival of each of the 9 yellow waypoints
                cum, acc = [], 0
                wp = sorted(cy)
                for i, p in enumerate(order):
                    if i > 0: acc += ev[i - 1]
                    if p in wp and len(cum) < 9:
                        cum.append(acc)
                if len(cum) != 9:
                    continue
                arr = []
                for wp_i, p in enumerate(wp):
                    idx = order.index(p)
                    arr.append(ev[idx - 1] if idx > 0 else 0)
                # distance to nearest blue
                nblue = [min(dist(fn, p, q) for q in bset) if bset else 0 for p in wp]
                for kind, vals in (("cum", cum), ("arr", arr), ("nblue", nblue)):
                    for mod in (9, 10):
                        for rev in (False, True):
                            seq = vals[::-1] if rev else vals
                            for off in range(2):
                                tab = [((seq[k] + off) % mod) % 10 for k in range(9)]
                                tables[f"{dname}/{tname}/{fn}/{kind}m{mod}{'r' if rev else ''}v{off}"] = tab
                # rank family: digit = position of waypoint sorted by value (0/1-base)
                for mod in (9, 10):
                    for rev in (False, True):
                        for off in range(2):
                            for kind, vals in (("cum", cum), ("arr", arr), ("nblue", nblue)):
                                seq = vals[::-1] if rev else vals
                                order_v = sorted(range(9), key=lambda k: (seq[k], k))
                                rank = [0] * 9
                                for pos, k in enumerate(order_v):
                                    rank[k] = (pos + off) % mod % 10
                                tables[f"{dname}/{tname}/{fn}/{kind}rankm{mod}{'r' if rev else ''}o{off}"] = rank
            # color-run segment lengths over the traversal
            runs = []
            run = 1
            for i in range(1, len(order)):
                if (order[i] in bset) == (order[i - 1] in bset):
                    run += 1
                else:
                    runs.append(run); run = 1
            runs.append(run)
            for mod in (9, 10):
                base = runs[:]
                while len(base) < 9:
                    base = (base + runs)[:9]
                for rev in (False, True):
                    seq = base[::-1] if rev else base
                    tables[f"{dname}/{tname}/runrunsm{mod}{'r' if rev else ''}"] = [x % mod % 10 for x in seq[:9]]
    return tables


def clean(pt):
    return "?" not in pt and 8 <= len(pt) <= 2000


def gen(cells, blue_set, out_path):
    is_real = cells == BLUE + YELLOW and blue_set == set(BLUE)
    tables = interp_tables() if is_real else interp_tables(synth=(cells, blue_set))
    cands = set()
    forms = 0
    for sname, stream in STREAMS.items():
        for tname, tab in tables.items():
            ds = "".join(str(tab[ord(ch) - 97]) for ch in stream if "a" <= ch <= "i")
            for alpha28 in ALPHAS.values():
                for e1, e2 in ((1, 4), (4, 1)):
                    pt = decode(ds, build_grid(alpha28, e1, e2), e1, e2)
                    forms += 1
                    if clean(pt):
                        cands.add(pt); cands.add(pt.lower()); cands.add(pt.upper()); cands.add(pt[::-1])
    with open(out_path, "w") as f:
        f.writelines(c + "\n" for c in sorted(cands))
    return len(cands), forms, len(tables)


def selftest():
    # 1. certified pipeline roundtrip
    for e1, e2 in ((1, 4), (4, 1)):
        ctol = build_grid(CONTROL, e1, e2)
        num = [next(cc for cc, v in ctol.items() if v == ch) for ch in "ROUTEWITNESS"]
        if decode("".join(num), ctol, e1, e2) != "ROUTEWITNESS":
            return False, "pipeline roundtrip failed"
    # 2. build a synthetic 24-cell geometry (deterministic), compute the generator's
    #    own interpreter tables for it, pick one table T reachable also by direct
    #    construction, encode a 9-free plaintext under the certified board, drive each
    #    code digit through T back to a letter, and confirm translate+decode re-finds
    #    the plaintext through the SAME alpha/escape loop the real sweep uses.
    cb, cy = [], []
    while len(cb) < 15 or len(cy) < 9:
        p = (RNG.randrange(0, 14), RNG.randrange(0, 14))
        if p not in cb and p not in cy:
            if len(cb) < 15 and RNG.random() < 0.6: cb.append(p)
            elif len(cy) < 9: cy.append(p)
    cells = cb + cy
    tset = interp_tables(synth=(cells, set(cb)))
    # direct cum/mh-related table must appear among generator tables
    order = sorted(cells)
    ev = cortex(order, "mh")
    wp = sorted(cy)
    cum, acc = [], 0
    for i, p in enumerate(order):
        if i > 0: acc += ev[i - 1]
        if p in wp and len(cum) < 9: cum.append(acc)
    if len(cum) != 9:
        return False, "synthetic geometry did not produce 9 waypoints"
    synth_tab = [x % 9 for x in cum]
    if not any(tab == synth_tab for tab in tset.values()):
        return False, "directly-constructed table not reproduced by interp_tables"
    # 9-free plaintext whose code digits are all reachable via synth_tab
    reach = set(synth_tab)
    ctol = build_grid(CONTROL, 1, 4)
    codes = sorted(cc for cc in ctol if "9" not in cc and all(int(d) in reach for d in cc))
    letters = sorted({ctol[cc] for cc in codes})
    for _ in range(4000):
        p = "".join(RNG.choice(letters) for _ in range(11))
        num = [next(cc for cc, v in ctol.items() if v == ch) for ch in p]
        ds = "".join(num)
        if all(int(d) in reach for d in ds):
            break
    else:
        return False, "no plaintext matching reachable digit set found"
    # map ds digits to letters through synth_tab
    inv = {}
    for i in range(9): inv.setdefault(synth_tab[i], []).append(chr(97 + i))
    ltr = []
    for dd in ds:
        pool = inv.get(int(dd))
        if not pool: return False, f"digit {dd} not reachable via table"
        ltr.append(pool[0])
    injected = "".join(ltr)
    # same translate+decode loop as gen(), on the injected stream only
    found = None
    for tname, tab in tset.items():
        if tab != synth_tab: continue
        for alpha28 in ALPHAS.values():
            for e1, e2 in ((1, 4), (4, 1)):
                out = decode("".join(str(tab[ord(ch) - 97]) for ch in injected), build_grid(alpha28, e1, e2), e1, e2)
                if out == p:
                    found = p
    if not found:
        return False, "injected plaintext not re-found via generator tables"
    return True, f"selftest OK (synthetic table re-derived; witness pt {found!r})"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true", help="run certification")
    ap.add_argument("--both", action="store_true", help="gen + run both oracles")
    args = ap.parse_args()
    if args.selftest:
        st, msg = selftest()
        print(msg)
        return 0 if st else 1
    t0 = time.time()
    n_c, n_f, n_t = gen(BLUE + YELLOW, set(BLUE), SCRATCH)
    print(f"[grid_route_interp] {n_t} interpreter tables -> {n_f} decode forms "
          f"= {n_c} candidates -> {SCRATCH} ({time.time()-t0:.0f}s)")
    if args.both:
        for prog in ("oracle.py", "oracle_dualite.py"):
            p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", prog), "--stdin"],
                               stdin=open(SCRATCH), capture_output=True, text=True)
            out = [l for l in p.stdout.splitlines() if l.strip()]
            print(f"[grid_route_interp] {prog}: {out[-1] if out else 'NO MATCH'}")
            if "MATCH" in p.stdout: print(p.stdout); return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())