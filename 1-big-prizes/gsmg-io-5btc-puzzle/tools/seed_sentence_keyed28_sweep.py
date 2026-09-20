#!/usr/bin/env python3
"""Full seed-sentence keyed28 VIC sweep on dbbib(69) + faed(570).

GAP: joint_sweep.py tested keyed28("THESEEDISPLANTED") (fragment) and
leap_alphabet_sweep.py tested sentence-level *spliced* sources
(GSMGIOTHESEEDISPLANTED, YINYANGOPPOSITESATTRACT), but the complete author
seed sentence as ONE keyed28 keyword -- THESEEDISPLANTEDWHENOPPOSITESATTRACT --
was never run through the certified VIC pipeline. This fills exactly that gap:
full-sentence compact + spaced variants x {CANON,POS,BIFID} digit maps x escapes
{(1,4),(2,5)} x widths {0,13,5,26} x OE keys {identity, matrixsumlist_m9/m10,
lastwords_m9/m10, causality_m9/m10} = 3*3*2*4*7 = 504 forms -> oracle both gates.

WITNESS: same machinery (certified_vic.build_grid/decode) reproduces the
certified 3.2.2 VIC plaintext under the literal phase322 alphabet & escapes 1,4
(re-asserted in tools/phase322_literal_sweep.py WITNESS and verified 2026-09-14);
oracles selftest PASS.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = os.path.expanduser("~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle")
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode  # noqa: E402

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CANON = {"d":0,"b":1,"i":2,"f":3,"h":4,"c":5,"e":6,"g":7,"a":8}
POS   = {c:i for i,c in enumerate("abcdefghi")}
BIFID = {"a":8,"b":1,"c":5,"d":0,"e":6,"f":3,"g":7,"h":4,"i":2}
MAPPINGS = [("CANON", CANON), ("POS", POS), ("BIFID", BIFID)]
ESCAPES  = [(1,4), (2,5)]
WIDTHS   = [0, 13, 5, 26]

d = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())
DBBIB = d["dbbib"]          # 69 tokens
FAED  = d["faed_570"].rstrip("z")  # 570 tokens
_STREAMS = [("dbbib", DBBIB), ("faed", FAED)]

def keyed28(keyword: str) -> str:
    kw = "".join(ch for ch in keyword.upper() if ch.isalpha())
    out = ""
    for ch in kw + ALPHA:
        if ch not in out:
            out += ch
    return (out + "./")[:28]

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

def over_undo(ds, ks, M):
    return "".join(str((int(ch) - ks[i % len(ks)]) % M) for i, ch in enumerate(ds))

SENTENCES = {
    "full_compact": "THESEEDISPLANTEDWHENOPPOSITESATTRACT",
    "full_spaced": "THE SEED IS PLANTED WHEN OPPOSITES ATTRACT",
    "full_title": "The Seed Is Planted When Opposites Attract",
}
# controls: the fragment already tested (must reproduce old results, sanity only)
SENTENCES["ctl_fragment"] = "THESEEDISPLANTED"

OE_KEYS = {"identity": None}
for nm, phrase in [("matrixsumlist", "matrixsumlist"),
                   ("lastwords", "lastwordsbeforearchichoice"),
                   ("causality", "causality"),
                   ("salphaseion", "salphaseion"),
                   ("btcseed", "btcseed")]:
    h = hashlib.sha256(phrase.encode()).hexdigest()
    OE_KEYS[nm + "_m9"] = [int(c, 16) % 9 for c in h]
    OE_KEYS[nm + "_m10"] = [int(c, 16) % 10 for c in h]

total = 0
cands = set()
stats = {}
for sname, sentence in SENTENCES.items():
    alpha28 = keyed28(sentence)
    stats[sname] = {"alpha28": alpha28, "forms": 0}
    print(f"[alpha28][{sname}] {alpha28}", flush=True)
    for sni, stream in _STREAMS:
        for mpname, mp in MAPPINGS:
            ds0 = to_digits(stream, mp)
            for e1, e2 in ESCAPES:
                ctol = build_grid(alpha28, e1, e2)
                for tw in WIDTHS:
                    for oename, oek in OE_KEYS.items():
                        total += 1
                        stats[sname]["forms"] += 1
                        M = 9 if (oek and "_m9" in oename) else 10
                        if tw == 0:
                            ds2 = ds0 if oek is None else over_undo(ds0, oek, M)
                        else:
                            order = sorted(range(tw), key=lambda i: (oek[i % len(oek)], i)) if oek else list(range(tw))
                            ds2 = ds0 if oek is None else col_undo(over_undo(ds0, oek, M), tw, order)
                        pt = decode(ds2, ctol, e1, e2)
                        if "?" not in pt and 8 <= len(pt) <= 2048 and pt.isprintable():
                            for form in (pt.lower(), pt.upper(), pt.title(), pt):
                                cands.add(form)

print(f"\n[total forms] {total}")
print(f"[clean candidates] {len(cands)}")
out = "/data/data/com.termux/files/usr/tmp/opencode/seed_sentence_cands.txt"
with open(out, "w") as f:
    f.write("\n".join(sorted(cands)) + "\n")
print("written", out)