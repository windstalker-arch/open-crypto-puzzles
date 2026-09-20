#!/usr/bin/env python3
"""Layered dbbib/faed decode: certified VIC pure checkerboard (28-char alphabet) PLUS
digit-level columnar transposition PLUS mod-9/10 over-encryption, crossed with the
title-word keyed alphabets (salphaselon / cosmicduality = the two halves).

Pipeline to DECODE one stream's digit-string ds:
  (1) undo over-encryption: subtract repeating keystream (from a key word, mod M)
  (2) undo columnar transposition: write into columns by key order, read row-major
  (3) certified 28-char checkerboard decode -> letters
All outputs fed to the sanctioned oracle; a real hit wins regardless of decode detail.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from certified_vic import build_grid, decode

DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())
DBBIB = d["dbbib"]
FAED = d["faed_570"].rstrip("z")

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CANON = {"d":0,"b":1,"i":2,"f":3,"h":4,"c":5,"e":6,"g":7,"a":8}
POS   = {c:i for i,c in enumerate("abcdefghi")}

def keyed26(keyword):
    kw = "".join(ch for ch in keyword.upper() if ch in ALPHA)
    out = ""
    for ch in kw + ALPHA:
        if ch not in out:
            out += ch
    return out

def make_28(k26, i1=26, i2=26, s1=".", s2="/"):
    lst = list(k26)
    for idx, sym in sorted([(min(i1,26), s1), (min(i2,26), s2)], key=lambda x: x[0]):
        lst.insert(idx, sym)
    return "".join(lst)

def over_undo(ds, keystream, M):
    out = []
    for i, ch in enumerate(ds):
        k = keystream[i % len(keystream)]
        out.append(str((int(ch) - k) % M))
    return "".join(out)

def col_undo(ct, keyorder):
    W = len(keyorder)
    n = len(ct)
    nrows = (n + W - 1) // W
    full = n % W if n % W else W
    lens = [nrows if i < full else nrows - 1 for i in range(W)]
    placed = [None] * W
    ptr = 0
    for k in range(W):
        ci = keyorder[k]; placed[ci] = ct[ptr:ptr + lens[ci]]; ptr += lens[ci]
    out = []
    for r in range(nrows):
        for c in range(W):
            if r < len(placed[c]):
                out.append(placed[c][r])
    return "".join(out)

def order_for(key, W):
    keyl = (key.upper() * ((W // len(key)) + 1))[:W]
    return sorted(range(W), key=lambda i: (keyl[i], i))

def ks_from(key, M):
    kw = "".join(ch for ch in key.upper() if ch in ALPHA)
    return [ (ord(ch) - 65) % M for ch in (kw or "A") ]

def to_digits(stream, mp):
    return "".join(str(mp[c]) for c in stream if c in mp)

KEYWORDS = ["salphaselon", "cosmicduality"]
TRANSKEYS = ["matrixsumlist", "thispassword", "lastwordsbeforearchichoice",
             "enter", "yourlastcommand", "shabef", "salphaselon", "cosmicduality"]
MAPPINGS = {"CANON": CANON, "POS": POS}
ESCAPES = [(1,4),(2,5),(0,4),(1,3),(3,1),(1,2)]

cands = set()
count = 0
for kw in KEYWORDS:
    k28 = make_28(keyed26(kw), 26, 26, ".", "/")   # punctuation appended
    # also variants with punctuation inserted in row1/row2 head
    k28_variants = [k28,
                    make_28(keyed26(kw), 8, 18, ".", "/"),
                    make_28(keyed26(kw), 8, 22, ".", "/")]
    for alpha28 in k28_variants:
        pass
    nothing=0

# redo loop properly
cands = set()
total = 0
for kw in KEYWORDS:
    k26 = keyed26(kw)
    alpha_variants = [make_28(k26, 26, 26), make_28(k26, 8, 18), make_28(k26, 8, 22),
                      make_28(k26, 4, 22), make_28(k26, 12, 26)]
    for alpha28 in alpha_variants:
        for mp in MAPPINGS.values():
            for (e1, e2) in ESCAPES:
                ctol = build_grid(alpha28, e1, e2)
                for transkey in TRANSKEYS:
                    W = len("".join(c for c in transkey.upper() if c in ALPHA))
                    if W < 4:
                        continue
                    order = order_for(transkey, W)
                    for overkey in TRANSKEYS:
                        for M in (9, 10):
                            ks = ks_from(overkey, M)
                            for sn, stream in [("dbbib", DBBIB), ("faed", FAED)]:
                                ds = to_digits(stream, mp)
                                # no over-encryption
                                for ds_v in (ds, col_undo(ds, order)):
                                    pt = decode(ds_v, ctol, e1, e2)
                                    if "?" not in pt and len(pt) >= 6:
                                        for nrm in {pt.lower(), pt.upper(), pt}:
                                            cands.add(nrm)
                                        total += 1
                                # with over-encryption undo before col-undo
                                ds_ov = over_undo(ds, ks, M)
                                for ds_v in (ds_ov, col_undo(ds_ov, order)):
                                    pt = decode(ds_v, ctol, e1, e2)
                                    if "?" not in pt and len(pt) >= 6:
                                        for nrm in {pt.lower(), pt.upper(), pt}:
                                            cands.add(nrm)
                                        total += 1

print(f"[gen] {len(cands)} layered title candidates (expanded count {total})")
Path("/data/data/com.termux/files/usr/tmp/opencode/layered_title_cands.txt").write_text("\n".join(sorted(cands)))
common = {w for w in ["the", "and", "of", "to", "in", "you", "it", "that", "he", "was", "for", "on", "are", "with", "this", "is", "not", "half", "better", "enter", "password", "matrix", "sum", "list", "last", "words", "before", "archi", "choice", "key", "private", "cosmic", "duality", "salphas", "seed", "funded", "sender", "plant", "secret", "keymakers", "esdmatrix"]}
leg = [c for c in cands if sum(1 for w in re.findall(r'[a-z]{4,}', c.lower()) if w in common)>=2]
print(f"legible-ish (>=2 common words): {len(leg)}")
for s in leg[:8]:
    print("  leg:", s[:80])
