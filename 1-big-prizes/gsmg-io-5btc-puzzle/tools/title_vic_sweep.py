#!/usr/bin/env python3
"""Feed certified title-word VIC decodes to the oracle. Uses tools/certified_vic.py
for the certified 3.2.2 pipeline, sweeps title-word keyed alphabets (punct placement,
escape pairs, digit mappings), decodes dbbib & faed, oracle-tests all letter outputs.
"""
import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from certified_vic import build_grid, decode

DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())
DBBIB = d["dbbib"]
FAED = d["faed_570"].rstrip("z")
CANON = {"d":0,"b":1,"i":2,"f":3,"h":4,"c":5,"e":6,"g":7,"a":8}
POS   = {c:i for i,c in enumerate("abcdefghi")}
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def keyed26(keyword):
    kw = "".join(ch for ch in keyword.upper() if ch in ALPHA)
    out = ""
    for ch in kw + ALPHA:
        if ch not in out:
            out += ch
    return out  # 26 letters

def make_28(k26, p1, p2):
    """insert '.' and '/' at indices i1,i2 into the 26-letter keyed alphabet -> 28."""
    out = []
    for i in range(26):
        # emit punctuation before certain indices
        pass
    # generic: build 28-char with two punctuation symbols at chosen slots
    lst = list(k26)
    # place p1,p2 as the 27th/28th cells appended (dcode fills leftover row cells last)
    return k26 + p1 + p2

def make_28_inner(k26, i1, i2, s1, s2):
    lst = list(k26)
    for idx, sym in sorted([(i1,s1),(i2,s2)], key=lambda x: x[0]):
        lst.insert(idx, sym)
    return "".join(lst)

def to_digits(stream, mp):
    return "".join(str(mp[c]) for c in stream if c in mp)

KEYWORDS = ["salphaselon","salphaseion","cosmicduality","salphaseloncosmicduality",
            "cosmicdualitysalphaselon"]
ESCAPES = [(1,4),(2,5),(0,4),(1,3),(3,1),(1,2),(2,3),(7,4),(1,7),(4,1),(5,2)]

cands = set()
for kw in KEYWORDS:
    k26 = keyed26(kw)
    # punctuation placements: try inside at various boundaries + appended
    punct_variants = [make_28(k26,".","/")]
    for i1 in (0,4,8,13,18,26):
        for i2 in (0,4,8,13,18,26):
            if i1==i2: continue
            punct_variants.append(make_28_inner(k26,i1,i2,".","/"))
    for mpname, mp in [("CANON",CANON),("POS",POS)]:
        for (e1,e2) in ESCAPES:
            for alpha28 in punct_variants:
                ctol = build_grid(alpha28, e1, e2)
                for sn, stream in [("dbbib",DBBIB),("faed",FAED)]:
                    ds = to_digits(stream, mp)
                    pt = decode(ds, ctol, e1, e2)
                    if "?" in pt or len(pt) < 5:
                        continue
                    for norm in {pt.lower(), pt.upper(), pt}:
                        cands.add(norm)

print(f"[gen] {len(cands)} title-word certified-VIC candidates")
Path("/data/data/com.termux/files/usr/tmp/opencode/certified_title_cands.txt").write_text("\n".join(sorted(cands)))
# readability scan
import re

common={w for w in ["the", "and", "of", "to", "in", "you", "it", "that", "he", "was", "for", "on", "are", "with", "this", "is", "not", "half", "better", "enter", "password", "matrix", "sum", "list", "last", "words", "before", "archi", "choice", "key", "private", "cosmic", "duality", "salphas", "seed", "funded", "sender", "plant", "halfandbetter", "ys"]}
leg=[c for c in cands if sum(1 for w in re.findall(r'[a-z]{4,}',c.lower()) if w in common)>=2]
print(f"legible-ish (>=2 common words): {len(leg)}")
for s in leg[:8]:
    print("  leg:",s[:80])
