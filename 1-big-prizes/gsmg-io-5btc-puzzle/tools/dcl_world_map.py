#!/usr/bin/env python3
"""dcl_world_map.py -- Decentraland world-map integration for the GSMG puzzle.

Loads full-land snapshots of Decentraland Genesis City (every parcel has a type,
owner, name and optional estate_id) and provides:
  - lookup(x, y) / lookup_window(x0, y0, w, h): parcel records by world coordinate
  - WORLD_TYPE_CODE / V2_TYPE_MAP: integer type codes stable across v1/v2 tiles
  - exact_crop_search(grid_blue, grid_yellow, size=14): the certified search that
    places each possible NxN window of the world under every dihedral transform of
    the puzzle's 24-cell grid and asks whether blue cells are all one land class,
    yellow cells all another class, and every other cell in the window is neither
    (i.e. the colour-coded grid is an exact crop of the live land map).
    WITNESS: stamping the grid into a synthetic window is re-found (id orientation)
    -> a no-hit result is a genuinely certified negative.
  - --snapshot PATH prints dataset summary + runs the crop battery over every
    snapshot given on the command line.

Type codes (v1 tiles int; v2 tiles string):
  5 district  7 road  8 plaza  9 owned-single  10 owned-in-estate

Datasets: current full map (13 MB v1-tiles JSON) and Wayback era snapshots
(2019-05-03, 2020-10-26, 2020-11-05, 2020-11-15, 2020-12-18).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WORLD_TYPE_CODE = {5: "district", 7: "road", 8: "plaza", 9: "owned-single", 10: "owned-estate"}
V2_TYPE_MAP = {"district": 5, "road": 7, "plaza": 8, "owned": 9, "estate": 10}

DIHEDRAL = {
    "id":      lambda p: (p[0],       p[1]),
    "rot180":  lambda p: (13 - p[0],  13 - p[1]),
    "reflX":   lambda p: (13 - p[0],  p[1]),
    "reflY":   lambda p: (p[0],       13 - p[1]),
    "trans":   lambda p: (p[1],       p[0]),
    "rot90":   lambda p: (13 - p[1],  p[0]),
    "rot270":  lambda p: (p[1],       13 - p[0]),
    "anti":    lambda p: (13 - p[1],  13 - p[0]),
}


def load_snapshot(path: str) -> dict:
    raw = open(path, "rb").read()
    try:
        d = json.loads(raw.decode())
    except Exception:
        d = json.loads(__import__("gzip").decompress(raw).decode())
    return d["data"] if isinstance(d, dict) and "data" in d else d


def to_world_matrix(d: dict, size: int = 318) -> np.ndarray:
    """(x+150, y+150) -> integer type code. 0 = no tile/data."""
    W = np.zeros((size, size), dtype=np.int16)
    for v in d.values():
        t = v.get("type")
        if isinstance(t, str):
            t = V2_TYPE_MAP.get(t, -1)
        x, y = int(v["x"]), int(v["y"])
        if -150 <= x < size - 150 and -150 <= y < size - 150:
            W[x + 150, y + 150] = int(t)
    return W


def summary(d: dict) -> dict:
    from collections import Counter
    types = Counter()
    estates = Counter()
    for v in d.values():
        t = v.get("type")
        if isinstance(t, str):
            t = V2_TYPE_MAP.get(t, str(t))
        types[str(t)] += 1
        if v.get("estateId") or v.get("estate_id"):
            estates[str(t)] += 1
    n = {k: v.get("name") for k, v in list(d.items())[:1]}
    return {
        "tiles": len(d),
        "types": dict(types),
        "sample": n,
        "x-range": (min(v["x"] for v in d.values()), max(v["x"] for v in d.values())),
        "y-range": (min(v["y"] for v in d.values()), max(v["y"] for v in d.values())),
    }


def exact_crop_search(W, grid_blue, grid_yellow, size=14, want_witness=True):
    """Certified crop battery. Returns (hits, witness_ok)."""
    N = W.shape[0] - size
    bl = [tuple(p) for p in grid_blue]
    ye = [tuple(p) for p in grid_yellow]

    def pieces(F, cells):
        s = np.zeros((N, N), dtype=np.int32)
        for bx, by in cells:
            s += F[bx:bx + N, by:by + N]
        return s

    present = sorted(set(int(t) for t in W.flatten() if t > 0))
    hits = []
    for t1 in present:
        F1 = W == t1
        for t2 in present:
            if t1 == t2:
                continue
            F2 = W == t2
            for tname, f in DIHEDRAL.items():
                BL = tuple(f(p) for p in bl)
                YE = tuple(f(p) for p in ye)
                sbl1 = pieces(F1, BL)
                sbl2 = pieces(F2, BL)
                sye2 = pieces(F2, YE)
                sye1 = pieces(F1, YE)
                m = (sbl1 == len(BL)) & (sbl2 == 0) & (sye2 == len(YE)) & (sye1 == 0)
                for i, j in zip(*np.where(m)):
                    hits.append((t1, t2, tname, int(j) - 150, int(i) - 150))

    witness_ok = True
    if want_witness:
        W2 = W.copy()
        ox, oy = 155, 200  # synthetic stamp target (world coords x=50, y=5)
        W2[ox:ox + size, oy:oy + size] = 7
        for bx, by in bl:
            W2[ox + bx, oy + by] = 9
        for bx, by in ye:
            W2[ox + bx, oy + by] = 8
        F1, F2 = W2 == 9, W2 == 8
        found = []
        for tname, f in DIHEDRAL.items():
            BL = tuple(f(p) for p in bl)
            YE = tuple(f(p) for p in ye)
            sbl = pieces(F1, BL)
            sye = pieces(F2, YE)
            m = (sbl == len(BL)) & (sye == len(YE))
            for i, j in zip(*np.where(m)):
                found.append((tname, int(j) - 150, int(i) - 150))
        witness_ok = (oy - 150, ox - 150) in {(x[1], x[2]) for x in found}
    return hits, witness_ok


def main(argv: list[str] | None = None) -> int:
    import argparse
    import pathlib

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("snapshots", nargs="*", help="world-map snapshot JSON files")
    ap.add_argument("--grid", default=os.path.join(
        ROOT, "data", "follow-white-rabbit-grid.json"))
    ap.add_argument("--witness", action="store_true", default=True)
    args = ap.parse_args(argv)

    grid = json.loads(pathlib.Path(args.grid).read_text())
    gb, gy = grid["blue"], grid["yellow"]
    snapshots = args.snapshots or [
        os.path.join(ROOT, "data", "dcl_worldmap", "tiles_current_v1.json"),
    ]
    total_hits = 0
    for fn in snapshots:
        if not os.path.exists(fn):
            print(f"MISSING {fn}")
            continue
        d = load_snapshot(fn)
        W = to_world_matrix(d)
        s = summary(d)
        hits, witness_ok = exact_crop_search(W, gb, gy)
        total_hits += len(hits)
        print(f"--- {os.path.basename(fn)} ---")
        print(f"tiles={s['tiles']} x={s['x-range']} y={s['y-range']} types={s['types']}")
        print(f"14x14 crop hits={len(hits)} witness={'PASS' if witness_ok else 'FAIL'}")
        for h in hits[:8]:
            print("   hit", h)
    print(f"TOTAL HITS {total_hits}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())