#!/usr/bin/env python3
"""Literal phase-3.2.2 board sweep on the TRUE 91-token dbbib + faed.

Row 194 / rekey91.py fed every keyword through keyed28() (non-alpha stripped,
deduped), so the literal 28-char board `FUBCDORA.LETHINGKYMVPS.JQZXW` -- the only
author-verified keyed alphabet in the puzzle (certified_vic.selfcert round-trips
the 149-digit VIC message verbatim under escapes (1,4)) -- was never applied to
the true 91-token dbbib or faed. This fills exactly that gap with the same
mappings/escapes/widths/over-encryption machinery as row 194, then feeds every
clean form to both certified gates.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = os.path.expanduser("~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle")
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode

HEAD = "dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfba"
MID  = "bfdhbeffcdbbfcccgbfbeeg"
TAIL = "gecbedcibfbffgigbeeeabe"
DBBIB = HEAD + MID + TAIL          # 91 = 45+23+23, live page
assert len(DBBIB) == 91

d = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())
FAED = d["faed_570"].rstrip("z")   # 569 after z strip

CANON = {"d":0,"b":1,"i":2,"f":3,"h":4,"c":5,"e":6,"g":7,"a":8}
POS   = {c:i for i,c in enumerate("abcdefghi")}
BIFID = {"a":8,"b":1,"c":5,"d":0,"e":6,"f":3,"g":7,"h":4,"i":2}
MAPPINGS = [("CANON", CANON), ("POS", POS), ("BIFID", BIFID)]
ESCAPES  = [(1,4), (2,5), (0,4), (1,2)]
WIDTHS = {"dbbib": [7, 13, 0], "faed": [15, 38, 19, 13, 0]}

# the literal author-verified 28-char board (dots AT indexes 8 and 18)
LITERAL = "FUBCDORA.LETHINGKYMVPS.JQZXW"
assert len(LITERAL) == 28

def to_digits(stream, mp):
    return "".join(str(mp[c]) for c in stream if c in mp)

def col_undo(ct, width, key_order):
    n = len(ct)
    nrows = (n + width - 1) // width
    full = n % width if n % width else width
    lens = [nrows if i < full else nrows - 1 for i in range(width)]
    placed = [None] * width
    ptr = 0
    for k in range(width):
        ci = key_order[k]
        placed[ci] = ct[ptr:ptr + lens[ci]]
        ptr += lens[ci]
    out = []
    for r in range(nrows):
        for c in range(width):
            if r < len(placed[c]):
                out.append(placed[c][r])
    return "".join(out)

OE_KEYS = {"none": None}
for nm, phrase in [("matrixsumlist", "matrixsumlist"), ("enter", "enter"),
                   ("lastwords", "lastwordsbeforearchichoice"),
                   ("thispassword", "thispassword"), ("causality", "causality"),
                   ("salphaseion", "salphaseion"), ("yinyang", "yinyang"),
                   ("btcseed", "btcseed")]:
    h = hashlib.sha256(phrase.encode()).hexdigest()
    OE_KEYS[nm + "_m9"] = [int(c, 16) % 9 for c in h]
    OE_KEYS[nm + "_m10"] = [int(c, 16) % 10 for c in h]
OE_KEYS["dbbib_canon"] = [CANON[c] for c in DBBIB]
OE_KEYS["dbbib_bifid"] = [BIFID[c] for c in DBBIB]

def over_undo(ds, ks, M):
    return "".join(str((int(ch) - ks[i % len(ks)]) % M) for i, ch in enumerate(ds))

results = []
stats = {"total_forms": 0, "clean_cands": 0}
for mpname, mp in MAPPINGS:
    for e1, e2 in ESCAPES:
        ctol_ = build_grid(LITERAL, e1, e2)
        for sname, stream in [("dbbib", DBBIB), ("faed", FAED)]:
            ds0 = to_digits(stream, mp)
            for tw in WIDTHS[sname]:
                for oename, oek in OE_KEYS.items():
                    stats["total_forms"] += 1
                    M = 9 if (oek and "_m9" in oename) else 10
                    if tw == 0:
                        ds2 = ds0 if oek is None else over_undo(ds0, oek, M)
                    else:
                        order = sorted(range(tw), key=lambda i: (oek[i % len(oek)], i)) if oek else list(range(tw))
                        ds2 = ds0 if oek is None else col_undo(over_undo(ds0, oek, M), tw, order)
                    pt = decode(ds2, ctol_, e1, e2)
                    q = pt.count("?")
                    pl = re.sub(r"[^a-zA-Z]", " ", pt).lower()
                    toks = [w for w in pl.split() if len(w) >= 3]
                    if q == 0 and len(toks) >= 2:
                        for form in (pt.lower(), pt.upper(), pt.title()):
                            results.append(form)
                            stats["clean_cands"] += 1

results = sorted(set(results))
print(f"total forms: {stats['total_forms']}")
print(f"clean candidates: {len(results)}")
out = "/data/data/com.termux/files/usr/tmp/opencode/phase322_literal_cands.txt"
with open(out, "w") as f:
    f.write("\n".join(results) + "\n")
print("written", out)