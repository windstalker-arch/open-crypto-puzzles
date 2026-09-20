#!/usr/bin/env python3
"""Stream->digit mapping search for dbbib/faed under the CERTIFIED VIC checkerboard.

Searches the 9! = 362,880 mappings of the 9 stream symbols {a..i} -> digits {0..8} by
hill-climbing / simulated annealing on a legibility objective (English unigram log-probs
+ common-word hits) of the checkerboard decode. Checkerboard (alphabet+escapes) fixed per
run; the best found mappings are printed for oracle verification.

Legibility is a valid signal here because a CORRECT alphabet+mapping+escapes must yield
readable instruction English (the 3.2.2 phase decoded to a full English sentence under the
identical pure scheme). We score the decoded letters directly.
"""
from __future__ import annotations

import json
import os
import random
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
SYM = "abcdefghi"

# English unigram frequencies (log10)
LG = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    G = {"e":12.7,"t":9.1,"a":8.2,"o":7.5,"i":7.0,"n":6.7,"s":6.3,"h":6.1,"r":6.0,
         "d":4.3,"l":4.0,"c":2.8,"u":2.8,"m":2.4,"w":2.4,"f":2.2,"g":2.0,"y":2.0,
         "p":1.9,"b":1.5,"v":1.0,"k":0.8,"j":0.15,"x":0.15,"q":0.10,"z":0.07}
except Exception:
    G = {}

COMMON = {"the","and","you","that","this","with","not","have","from","they","your",
          "half","better","enter","password","matrix","sumlist","last","words","before",
          "archi","choice","key","private","cosmic","duality","salphas","seed","funded",
          "solar","sender","answer","command","first","hint","yourlast","second"}

def score(pt):
    pt = re.sub(r"[^a-zA-Z]", " ", pt)
    pt = pt.lower()
    toks = pt.split()
    if not toks:
        return -1e9
    # unigram score
    ug = 0.0
    valid = 0
    for ch in pt.replace(" ", ""):
        if ch in G:
            ug += 0.01 * G[ch]
            valid += 1
    wscore = 0.0
    for w in toks:
        if w in COMMON:
            wscore += 5.0 + len(w)
    return ug + wscore - 20.0 * (0 if valid else 1)

def decode_map(stream, mp, ctol, e1, e2):
    ds = "".join(str(mp[c]) for c in stream)
    return decode(ds, ctol, e1, e2)

def hillclimb(ctol, e1, e2, stream, mp_start, iters=1500):
    best = dict(mp_start)
    bestscore = score(decode_map(stream, best, ctol, e1, e2))
    cur = dict(best); curscore = bestscore
    syms = list(SYM)
    temp = 2.0
    for it in range(iters):
        i, j = random.sample(range(9), 2)
        ci, cj = syms[i], syms[j]
        nxt = dict(cur); nxt[ci], nxt[cj] = nxt[cj], nxt[ci]
        ns = score(decode_map(stream, nxt, ctol, e1, e2))
        if ns > curscore or random.random() < math_exp((ns - curscore) / temp):
            cur = nxt; curscore = ns
        if curscore > bestscore:
            best = dict(cur); bestscore = curscore
        temp = max(0.1, temp * 0.9995)
    return best, bestscore

def math_exp(x):
    import math
    try:
        return math.exp(max(-30, min(30, x)))
    except Exception:
        return 0

if __name__ == "__main__":
    random.seed(7)
    alphamap = {
       "3.2.2": "FUBCDORA.LETHINGKYMVPS.JQZXW",
       "plain": "ABCDEFGHIJKLMNOPQRSTUVWXYZ./",
       "salphaselon": None,  # built below
    }
    def keyed28(kw):
        kw = "".join(c for c in kw.upper() if c.isalpha())
        out = ""
        for ch in kw + "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if ch not in out:
                out += ch
        return out + "./"
    alphamap["salphaselon"] = keyed28("salphaselon")[:28]
    alphamap["cosmicduality"] = keyed28("cosmicduality")[:28]

    top = []
    for aname, alpha in alphamap.items():
        for (e1, e2) in [(1,4),(2,5)]:
            ctol = build_grid(alpha, e1, e2)
            for sn, stream in [("dbbib", DBBIB), ("faed", FAED)]:
                for run in range(3):
                    start = {c: i for i, c in enumerate(SYM)} if run == 0 else \
                            (dict(zip(SYM, random.sample(range(9), 9))) if run == 1 else
                             dict(zip(SYM, [ ("a","d","b","i","f","h","c","e","g").index(c) if c in "dbifhcega" else 0 for c in SYM ])))
                    mp, sc = hillclimb(ctol, e1, e2, stream, start)
                    pt = decode_map(stream, mp, ctol, e1, e2)
                    top.append((sc, aname, e1, e2, sn, mp, pt))
    top.sort(reverse=True, key=lambda x: x[0])
    print("=== top 12 mapping solutions by legibility ===")
    for sc, aname, e1, e2, sn, mp, pt in top[:12]:
        mapstr = "".join(f"{c}:{mp[c]}" for c in "abcdefghi")
        print(f"[{sc:.1f}] {aname} e{e1}{e2} {sn} map={mapstr}")
        print(f"        {pt[:90]}")
