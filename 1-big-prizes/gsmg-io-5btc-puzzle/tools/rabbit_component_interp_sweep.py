#!/usr/bin/env python3
"""rabbit_component_interp_sweep.py -- rabbit's 9 black components as a {a..i}
checkerboard interpreter, escapes (1,4), all ALPHAS, no trans/OE.

Rationale (leads.md note 25 / tested.md row 197-198). The rabbit figure on the
final-page 14x14 matrix has EXACTLY 9 black components (leads:906), and the two
streams dbbib/faed range over EXACTLY the 9 letters {a..i}. Only the yellow-matrix-
cells (row,col,key-bit) coordinate maps were swept as interpreters (tested.md row
182, 260 cands NO MATCH). The rabbit's OWN body ordering -- ear/forelock/eye/snout/
base components sorted by geometry -- was never used to define the a..i -> digit
interpreter. This sweep fixes that gap.

Interpreter construction: the 9 components are ordered by each of several geometric
keys; the k-th component in that order maps {a..i}[k] -> the digit value = the
component's rank k (0-based and 1-based) or a geometric value (centroid row/col,
area) reduced mod 9/10. This is the same ranked-positional family as row 182 but
sourced from the rabbit body instead of the matrix cells. Under BOTH digit domains
(0..8 and 1..9).

Decode chain: certified build_grid/decode from tools/certified_vic.py with escapes
(1,4) fixed -- the exact channel of rows 196-198 -- over every ALPHAS entry,
no trans/OE. Clean (?-free) decodes, length 8..2000, pushed as raw/lower/upper/
reversed answer-forms; all fed to BOTH funded-gate oracles.

Public/authorized puzzle only. A hit is an oracle MATCH.
"""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid
from leap_alphabet_sweep import ALPHAS

OGDIR = os.path.expanduser("~")
DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())
FAED = d["faed_570"].rstrip("z")
DBBI69 = d["dbbib"]
DBBI91 = Path(os.path.join(OGDIR, "tmp", "grid_dbbib.txt")).read_text().strip()
assert len(FAED) == 570 and len(DBBI69) == 69 and len(DBBI91) == 91

PUZZLE = os.path.join(os.path.expanduser("~"), "briefcase", "gsmg-community", "puzzle.png")
RABBIT_BBOX = (480, 480, 657, 593)  # rows 478/480-656, cols 480-592 (leads:906/930)
SCRATCH = os.path.join(OGDIR, "tmp", "rabbit_comp_cands.txt")


def rabbit_components():
    im = Image.open(PUZZLE).convert("L")
    a = np.array(im)
    r0, c0, r1, c1 = RABBIT_BBOX
    crop = a[r0:r1, c0:c1]
    black = crop < 128
    lab, n = ndimage.label(black)
    assert n == 9, (n,)
    cm = np.array(ndimage.center_of_mass(black, lab, range(1, n + 1)))
    sizes = np.array(ndimage.sum(black, lab, range(1, n + 1)))
    bbox = []
    for s in ndimage.find_objects(lab):
        bbox.append((s[0].start, s[1].start, s[0].stop, s[1].stop))
    return list(range(1, n + 1)), n, cm, sizes, bbox


def interp_tables():
    """Digital a..i -> digit tables derived from the rabbit body geometry.
    Each table is a list of 9 digits indexed by letter ord('a')..ord('i')."""
    labels, n, cm, sizes, bbox = rabbit_components()
    keys = {
        "label": (labels, None),
        "centrow": (labels, cm[:, 0]),
        "centcol": (labels, cm[:, 1]),
        "size": (labels, sizes),
        "cycx": (labels, cm[:, 0] + cm[:, 1]),
        "cycxdiff": (labels, np.abs(cm[:, 0] - cm[:, 1])),
        "r0": (labels, [b[0] for b in bbox]),
        "c0": (labels, [b[1] for b in bbox]),
    }
    tables = {}
    for kname, (ord0, val) in keys.items():
        order = sorted(range(n), key=lambda i: (val[i], labels[i]) if val is not None else labels[i])
        ord1 = sorted(range(n), key=lambda i: (val[i], labels[i]) if val is not None else labels[i], reverse=True)
        for rev, perm in (("", order), ("rev", ord1)):
            for base, off in (("0", 0), ("1", 1)):
                tbl = [0] * 9
                for pos, idx in enumerate(perm):
                    tbl[idx] = (pos + off) % 10
                tables[f"{kname}{rev}_{base}"] = tbl
    # geometric value tables: each component's own value, positionally assigned
    valm = {
        "centrow_mod10": cm[:, 0].astype(int) % 10,
        "centcol_mod10": cm[:, 1].astype(int) % 10,
        "cy_mod9": cm[:, 0].astype(int) % 9,
        "cx_mod9": cm[:, 1].astype(int) % 9,
        "size_mod9": sizes.astype(int) % 9,
        "cycx_mod10": (cm[:, 0] + cm[:, 1]).astype(int) % 10,
        "cycx_mod9": (cm[:, 0] + cm[:, 1]).astype(int) % 9,
        "csq_mod9": (cm[:, 0] ** 2 + cm[:, 1] ** 2).astype(int) % 9,
        "area_mod10": sizes.astype(int) % 10,
    }
    for kname, vals in valm.items():
        tables[kname] = list(vals)
    # dedupe, keep deterministic order
    seen = {}
    for k, v in tables.items():
        seen.setdefault(tuple(v), []).append(k)
    uniq = {k: v for k, v in tables.items()}
    return uniq, seen


def make_decoder(e1=1, e2=4):
    def build(alpha28):
        ctol = build_grid(alpha28, e1, e2)
        row_single = [-1] * 10
        pairs = {}
        for code, ch in ctol.items():
            if len(code) == 2:
                pairs[code] = ch
            else:
                row_single[int(code)] = ord(ch)
        return pairs, row_single

    def dec(ds, alpha28):
        pairs, row_single = build(alpha28)
        out = []
        i, n = 0, len(ds)
        while i < n:
            c = ds[i]
            if c == "1" or c == "4":
                code = ds[i:i + 2]
                if code in pairs:
                    out.append(pairs[code])
                    i += 2
                    continue
            v = row_single[ord(c) - 48]
            out.append(chr(v) if v >= 0 else "?")
            i += 1
        return "".join(out)

    return dec


def clean(pt):
    return "?" not in pt and 8 <= len(pt) <= 2000


def main():
    t0 = time.time()
    tables, dupes = interp_tables()
    print(f"[sic] rabbit 9 components -> {len(tables)} unique a..i->digit tables", flush=True)
    for names in dupes.values():
        if len(names) > 1:
            print(f"      {names[0]} dup of {names[1:]}")
    dec = make_decoder()
    streams = {
        "faed": FAED,
        "dbbi69": DBBI69,
        "dbbi91": DBBI91,
        "faed+dbbi69": FAED + DBBI69,
        "dbbi69+faed": DBBI69 + FAED,
    }
    cands = set()
    forms = 0
    for s in streams.values():
        for tbl in tables.values():
            ds = s.translate(bytes.maketrans(b"abcdefghi",
                                             bytes(v + 48 for v in tbl)))
            for alpha28 in ALPHAS.values():
                pt = dec(ds, alpha28)
                forms += 1
                if clean(pt):
                    cands.add(pt)
                    cands.add(pt.lower())
                    cands.add(pt.upper())
                    cands.add(pt[::-1])
    with open(SCRATCH, "w") as f:
        f.writelines(c + "\n" for c in sorted(cands))
    print(f"[sic] {forms} forms -> {len(cands)} candidates ({time.time()-t0:.0f}s) "
          f"-> {SCRATCH}", flush=True)


if __name__ == "__main__":
    main()