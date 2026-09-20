#!/usr/bin/env python3
"""Joint decode sweep (91-token dbbi variant, sticker phrase added).

Full VIC pipeline on faed: checkerboard (fresh alphabets incl. the sticker
reassembly), columnar transposition, over-encryption (mod 9 / mod 10). The
difference vs plain joint_sweep.py is that the key/over-encryption streams use
the live-page 91-token dbbi (issue 106 "dbbi/91") instead of the data-file's
69-token crop, and the thispassword/sticker phrase appears as both a keyed
alphabet and a sha256-based over-encryption key.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode

DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())
DBBIB = Path(os.path.join(os.path.expanduser("~"), "tmp", "grid_dbbib.txt")).read_text().strip()
assert len(DBBIB) == 91, len(DBBIB)
FAED = d["faed_570"].rstrip("z")

CANON = {"d":0,"b":1,"i":2,"f":3,"h":4,"c":5,"e":6,"g":7,"a":8}
POS   = {c:i for i,c in enumerate("abcdefghi")}
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def keyed28(keyword):
    kw = "".join(ch for ch in keyword.upper() if ch.isalpha())
    out = ""
    for ch in kw + ALPHA:
        if ch not in out:
            out += ch
    return (out + "./")[:28]

def to_digits(stream, mp):
    return "".join(str(mp[c]) for c in stream if c in mp)

def col_undo(ct, width, key_order):
    """Reverse columnar transposition."""
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
    """Reverse mod-M over-encryption."""
    return "".join(str((int(ch) - ks[i % len(ks)]) % M) for i, ch in enumerate(ds))

def score(pt):
    pl = re.sub(r"[^a-zA-Z]", " ", pt).lower()
    toks = pl.split()
    if not toks:
        return -1e9
    G = {"e":12.7,"t":9.1,"a":8.2,"o":7.5,"i":7.0,"n":6.7,"s":6.3,"h":6.1,"r":6.0,
         "d":4.3,"l":4.0,"c":2.8,"u":2.8,"m":2.4,"w":2.4,"f":2.2,"g":2.0,"y":2.0,
         "p":1.9,"b":1.5,"v":1.0,"k":0.8}
    COMMON = {"the","and","you","that","this","with","not","have","from","they","your",
              "half","better","enter","password","matrix","sumlist","last","words",
              "before","archi","choice","key","private","cosmic","duality","salphas",
              "seed","funded","sender","answer","command","first","hint","yourlast",
              "case","manage","crack","belong","need","funds","live","incase",
              "crypto","wallet","warning","digit","logic","banking","lock","open"}
    ug = sum(0.01 * G.get(ch, 0) for ch in pl.replace(" ", ""))
    w = sum(5.0 + len(t) for t in toks if t in COMMON)
    q = pt.count("?")
    return ug + w - q * 2.0

alphabets = {
    "bifid_row": keyed28("DBIFHCEGAKLMNOPQRSTUVWXYZ"),
    "lean23": keyed28("ABCDEFGHKLMNPQRSTUVWXYZ"),
    "phase322": "FUBCDORA.LETHINGKYMVPS.JQZXW",
    "salphaselon": keyed28("SALPHASELON"),
    "cosmicduality": keyed28("COSMICDUALITY"),
    "yellow_blue": keyed28("YELLOWBLUE"),
    "primes": keyed28("PRIMES"),
    "yinyang": keyed28("YINYANG"),
    "btcseed": keyed28("BTCSEED"),
    "white_rabbit": keyed28("FOLLOWTHEWHITERABBIT"),
    "seed_planted": keyed28("THESEEDISPLANTED"),
    "in_eyes": keyed28("INFRONTOFOUREYES"),
    "zeroed": keyed28("ZEROEDOUT"),
    "dbbib_freq": keyed28("BEGHFCIDA"),
    "faed_freq": keyed28("GIEHCFABD"),
    "sticker_phrase": keyed28("CRYPTOWALLETWARNINGDIGITLOGIC"),
    "sticker_stems": keyed28("CADIGILOCKLOCRYPTOGICNYOUOPENLOCKNINGT"),
    "sticker_sep": keyed28("CRYPTOGICNYOUOPENLOCKNINGTCADIGILOCKLO"),
    "digital_logic": keyed28("DIGITLOGICCARDIGILOCKLOCRYPTOGIC"),
    "enterthekeys": keyed28("ENTERTHEKEYS"),
    "deoemckeadhbschdkbdcsdkdvbxcpcoch": keyed28("DEOEMCKEADHBSCHDKBDCSDKDVBXCPCOCH"),
}

TRANS_WIDTHS = {
    "matrixsumlist": 13,
    "lastwords": 26,
    "thispassword": 12,
    "enter": 5,
    "stickerlen": 23,
    "seedplanted": 17,
    "none": 0,
}

OE_KEYS = {}
for name, phrase in [
    ("matrixsumlist", "matrixsumlist"),
    ("enter", "enter"),
    ("lastwords", "lastwordsbeforearchichoice"),
    ("thispassword", "thispassword"),
    ("causality", "causality"),
    ("salphaseion", "salphaseion"),
    ("yinyang", "yinyang"),
    ("btcseed", "btcseed"),
    ("sticker_phrase", "crypto wallet warning digit logic"),
    ("sticker_stems", "cadigilocklocryptogicnyouopenlockningt"),
    ("enterthekeys", "enterthekeys"),
    ("deoemck", "DEOEMCKEADHBSCHDKBDCSDKDVBXCPCOCH"),
]:
    h = hashlib.sha256(phrase.encode()).hexdigest()
    OE_KEYS[name + "_m9"] = [int(c, 16) % 9 for c in h]
    OE_KEYS[name + "_m10"] = [int(c, 16) % 10 for c in h]

D91 = dbbi = [CANON[c] for c in DBBIB]
OE_KEYS["dbbi_canon"] = D91
OE_KEYS["dbbi_pos"] = [POS[c] for c in DBBIB]
OE_KEYS["dbbi_canon_inv"] = [9 - v for v in D91]

MAPPINGS = [("CANON", CANON), ("POS", POS)]
ESCAPES = [(1,4), (2,5)]

results = []
total = 0
for aname, alpha28 in alphabets.items():
    for mpname, mp in MAPPINGS:
        for e1, e2 in ESCAPES:
            ctol = build_grid(alpha28, e1, e2)
            ds = to_digits(FAED, mp)
            for tname, tw in TRANS_WIDTHS.items():
                for oe_name, oe_key in OE_KEYS.items():
                    total += 1
                    M = 9 if "_m9" in oe_name else (10 if "_m10" in oe_name else 9)
                    if tw == 0:
                        ds2 = over_undo(ds, oe_key, M)
                    else:
                        order = sorted(range(tw), key=lambda i: (oe_key[i % len(oe_key)], i))
                        ds2 = col_undo(over_undo(ds, oe_key, M), tw, order)
                    pt = decode(ds2, ctol, e1, e2)
                    sc = score(pt)
                    q = pt.count("?")
                    pl = re.sub(r"[^a-zA-Z]", " ", pt).lower()
                    words_found = [w for w in pl.split() if len(w) >= 4]
                    if sc > 25 or words_found:
                        results.append((sc, aname, mpname, e1, e2, tname, oe_name, pt, q, words_found))

results.sort(key=lambda x: -x[0])
print(f"Tested {total} joint decode forms (91-token dbbi)")
print(f"Results with score>25 or words found: {len(results)}")
print()
print("=== Top 40 by legibility ===")
for sc, aname, mpname, e1, e2, tname, oe_name, pt, q, wf in results[:40]:
    words = ",".join(wf[:6]) if wf else "-"
    print(f"[{sc:6.1f}] {aname:36s} {mpname:5s} e{e1}{e2} t={tname:12s} oe={oe_name:15s} ?={q:2d}")
    print(f"       words={words}")
    print(f"       {pt[:120]}")

cands = set()
for sc, aname, mpname, e1, e2, tname, oe_name, pt, q, wf in results:
    if q == 0 and len(pt) >= 8:
        for form in (pt.lower(), pt.upper(), pt.title()):
            cands.add(form)
print(f"\n[gen] {len(cands)} clean candidates")
candfile = os.path.join(ROOT, "tools", "joint_cands_91.txt")
with open(candfile, "w") as f:
    f.writelines(c + "\n" for c in sorted(cands))
print(f"Written to {candfile}")