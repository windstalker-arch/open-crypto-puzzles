#!/usr/bin/env python3
"""sticker_kw_freeinterp.py -- the /theseedisplanted sticker-fragment words as keyed-28
alphabets x TOP2-CONSTRAINED FREE INTERPRETER x escapes (1,4), certified decoder,
both gates.

Closes the tested.md 200-201 residual "any non-sentence (visual-layer) alphabet under
the free-interpreter family": the sticker fragments are the visual-layer alphabet
source. This runs the SAME top2-constrained free-interpreter construction as
free_interp_alpha_sweep stage1, but with the sticker-keyword alphabets (26 variants)
instead of the 47 sentence alphabets.

Method: for each payload (faed 570 / dbbib69 / dbbib91), build the top2->{1,4} free
interpreter perms under both digit domains (2 x 7! tables), translate payload, decode
with the certified checkerboard over every sticker-alpha; clean (?-free decodes) ->
raw/lower/upper/reversed -> oracle feed, both gates.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

OGDIR = os.path.expanduser("~")
ORACLE_SMALL = os.path.join(ROOT, "tools", "oracle.py")
ORACLE_DUAL = os.path.join(ROOT, "tools", "oracle_dualite.py")
OUT = os.path.join(OGDIR, "tmp", "sticker_kw_freeinterp_cands.txt")

import importlib.util

spec = importlib.util.spec_from_file_location("skw", os.path.join(ROOT, "tools", "sticker_kw_alphabet_sweep.py"))
skw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(skw)  # runs module code: builds FAED etc. and prints counts

from certified_vic import build_grid
from free_interp_alpha_sweep import (
    clean,
    emit,
    interpreter_permutations,
    stranslate,
    top2,
)


def make_fast_decoder(e1, e2, alphas):
    """Per-alphabet grids precomputed once; decode loop lifted per grid."""
    e1s, e2s = str(e1), str(e2)
    grids = {}
    for aname, alpha28 in alphas.items():
        ctol = build_grid(alpha28, e1, e2)
        row_single = [-1] * 10
        pairs = {}
        for code, ch in ctol.items():
            if len(code) == 2:
                pairs[code] = ch
            else:
                row_single[int(code)] = ord(ch)
        grids[aname] = (pairs, row_single)
    return grids, e1s, e2s


def main():
    t0 = time.time()
    alphab = {}
    for name, seed in skw.seeds.items():
        alphab[name] = skw.keyed28(seed)
    print(f"sticker keyword alphabets: {len(alphab)}", flush=True)

    payloads = {"faed": skw.FAED, "dbbi69": skw.DBBI69, "dbbi91": skw.DBBI91}
    grids, e1s, e2s = make_fast_decoder(1, 4, alphab)
    cands = set()
    forms = 0
    for pname, payload in payloads.items():
        perms = interpreter_permutations(payload, 1, 4, 0, 8) + \
                interpreter_permutations(payload, 1, 4, 1, 9)
        print(f"[s] {pname} top2={top2(payload)}: {len(perms)} tables", flush=True)
        for tbl in perms:
            ds = stranslate(payload, tbl)
            for (pairs, row_single) in grids.values():
                out = []
                ap = out.append
                ps = pairs
                rs = row_single
                i = 0
                n = len(ds)
                while i < n:
                    c = ds[i]
                    if c == e1s or c == e2s:
                        code = ds[i:i + 2]
                        if code in ps:
                            ap(ps[code])
                            i += 2
                            continue
                    v = rs[ord(c) - 48]
                    ap(chr(v) if v >= 0 else "?")
                    i += 1
                pt = "".join(out)
                forms += 1
                if clean(pt):
                    emit(cands, pt)
            if forms % 50000 == 0:
                with open(OUT, "w") as f:
                    for c in sorted(cands):
                        f.write(c + "\n")
                print(f"[s] {pname} checkpoint {forms} forms -> {len(cands)} cands "
                      f"({time.time()-t0:.0f}s)", flush=True)
    with open(OUT, "w") as f:
        for c in sorted(cands):
            f.write(c + "\n")
    print(f"[s] {forms} decode forms -> {len(cands)} candidates "
          f"({time.time()-t0:.0f}s)", flush=True)

    for label, oracle in [("small", ORACLE_SMALL), ("dualite", ORACLE_DUAL)]:
        r = subprocess.run([sys.executable, oracle, "--stdin"],
                           input=Path(OUT).read_bytes(), capture_output=True)
        lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
        hits = [ln for ln in lines if ln.startswith("MATCH")]
        print(f"[{label}] lines={len(lines)} MATCH={len(hits)}")
        for h in hits:
            print("HIT:", h)
        if not hits:
            print(f"[{label}] NO MATCH")


if __name__ == "__main__":
    main()