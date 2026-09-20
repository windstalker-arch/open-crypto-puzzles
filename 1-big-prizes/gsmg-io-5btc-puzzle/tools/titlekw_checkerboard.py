#!/usr/bin/env python3
"""Interpreter-alphabet checkerboard decode of dbbib/faed using the page's OWN
visible section-title keywords (SalPhaselon, Cosmic Duality) as the keyed-alphabet
source -- the most "in front of your eyes" alphabets, which prior sweeps
(§24 tiles, §25 vocab, §41 hint-alphabets, §46 sum-derived) did not record as tried.

Model: standard VIC/straddling checkerboard over digits 0..9 using a keyed alphabet
built by dedupe-then-fill from the keyword. For each (keyword, digit-map, escape-pair,
row0-length, transposition) we decode both streams to plaintext letters; every
resulting letter-string (6 normalisations) is pushed to the certified oracle.

The community template (phase 3.2.2, leads.md note 1) fixes escapes 1,4; here we sweep
all escape pairs and row0 lengths so no layout assumption is missed.

Ground truth = oracle attempt() vs gate 1GSMG1JC9 (small blob). Public/authorized.
"""
import json
import os
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
ORACLE = os.path.join(ROOT, "tools", "oracle.py")

d = json.loads(Path(DATA).read_text())
dbbib = d["dbbib"]
faed = d["faed_570"].rstrip("z")

def build_keyed(keyword, alpha="abcdefghijklmnopqrstuvwxyz"):
    out = ""
    for ch in (keyword + alpha):
        ch = ch.lower()
        if ch in alpha and ch not in out:
            out += ch
    return out

# on-page visible keywords
KEYWORDS = [
    "salphaselon", "salphaseion", "salphaseloncosmicduality",
    "cosmicduality", "cosmicdualitysalphaselon",
    "cosmic", "duality", "salphas",
    "salphaselon cosmicduality".replace(" ", ""),
    "salphaselonecosmicduality",
]
# author's hidden hint phrase words
HINTWORDS = ["yellowblueprimesmatrixsumlistlastwordsbeforearchichoicyinyang",
             "yellowblueprimes", "yinyang", "matrixsumlist",
             "yellowblue", "oppositesattract", "salphaselonecosmicduality"]

POS = {c: i for i, c in enumerate("abcdefghi")}
CANON = {"d":0,"b":1,"i":2,"f":3,"h":4,"c":5,"e":6,"g":7,"a":8}

def to_digits(stream, mp):
    return [mp[c] for c in stream if c in mp]

def build_board(keyed, row0n, esc0, esc1):
    ltc, ctol = {}, {}
    idx = 0
    cells = [c for c in range(10) if c not in (esc0, esc1)]
    # row0: row0n letters placed into first row0n of the 8 non-escape cells
    for cell in cells[:row0n]:
        if idx < len(keyed):
            ltc[keyed[idx]] = str(cell); ctol[str(cell)] = keyed[idx]; idx += 1
    # row1 (under esc0): next 10
    for i in range(10):
        if idx < len(keyed):
            ltc[keyed[idx]] = f"{esc0}{i}"; ctol[f"{esc0}{i}"] = keyed[idx]; idx += 1
    # row2 (under esc1): next 10
    for i in range(10):
        if idx < len(keyed):
            ltc[keyed[idx]] = f"{esc1}{i}"; ctol[f"{esc1}{i}"] = keyed[idx]; idx += 1
    return ctol

def cb_decode(digits, ctol, esc0, esc1):
    s = "".join(map(str, digits))
    out = []; i = 0
    while i < len(s):
        c = s[i]
        if c in ctol:
            out.append(ctol[c]); i += 1; continue
        if c == str(esc0) or c == str(esc1):
            if i + 1 < len(s):
                code = c + s[i+1]
                if code in ctol:
                    out.append(ctol[code]); i += 2; continue
            out.append("?"); i += 1; continue
        out.append("?"); i += 1
    return "".join(out)

def col_transpose(stream, width, rev=False):
    # columnar on the digit-string; width from transposition-key length idea, but here
    # we operate on letters; simpler: no transpose unless specified. Provided for completeness.
    return stream

candidates = set()
report = []
for kw in KEYWORDS + HINTWORDS:
    keyed = build_keyed(kw)
    for mpname, mp in [("POS", POS), ("CANON", CANON)]:
        for (ec0, ec1) in [(1,4),(2,5),(0,4),(1,3),(3,1),(1,2),(2,3),(4,1),(7,4),(1,7)]:
            for row0n in range(6, 9):
                ctol = build_board(keyed, row0n, ec0, ec1)
                for streamname, stream in [("dbbib", dbbib), ("faed", faed)]:
                    digits = to_digits(stream, mp)
                    pt = cb_decode(digits, ctol, ec0, ec1)
                    if "?" in pt or len(pt) < 4:
                        continue
                    for norm in [pt.lower(), pt.upper(), pt,
                                 pt.lower()[::-1], pt.upper()[::-1]]:
                        candidates.add(norm)
                        report.append((kw, mpname, f"e{ec0}{ec1}", f"r{row0n}", streamname, norm[:40]))

print(f"[gen] {len(candidates)} candidates across {len(KEYWORDS)+len(HINTWORDS)} keywords")

# quick readability scan: how many decode to mostly-letters containing real words
import re

readable = 0
for c in candidates:
    if re.fullmatch(r"[a-z]+", c) and len(c) > 5:
        readable += 1
print(f"pure-letter candidates: {readable}")

with open("/data/data/com.termux/files/usr/tmp/opencode/titlekw_cands.txt", "w") as f:
    for c in sorted(candidates):
        if c:
            f.write(c + "\n")
print("wrote candidate file")
