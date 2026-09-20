#!/usr/bin/env python3
"""Use sha256(first-hint) as the decode key for dbbib/faed (leads.md line 344 endgame):
sha256(first hint) -> decode key for dbbib/faed -> ANSWER -> sha256(ANSWER) = AES key.
The decode key is a 64-hex string; interpret it as (a) over-encryption keystream, (b)
transposition key, (c) keyed-alphabet keyword, crossed with the title-word alphabets
under the CERTIFIED checkerboard. Legibility + oracle.
"""
from __future__ import annotations

import hashlib
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
DBBIB = d["dbbib"]; FAED = d["faed_570"].rstrip("z")
SYM = "abcdefghi"
CANON = {"d":0,"b":1,"i":2,"f":3,"h":4,"c":5,"e":6,"g":7,"a":8}
POS   = {c:i for i,c in enumerate("abcdefghi")}

def keyed28(kw):
    kw = "".join(c for c in kw.upper() if c.isalpha())
    out = ""
    for ch in kw + "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if ch not in out:
            out += ch
    return (out + "./")[:28]

first_string = "GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
KH_8972 = hashlib.sha256(first_string.encode()).hexdigest()   # 89727c...
KH_DB14 = hashlib.sha256(KH_8972.encode()).hexdigest()         # db14474e...
KH_F971 = hashlib.sha256(bytes.fromhex(KH_8972)).hexdigest()   # f9719d6d...
DECODEKEYS = {"sha256(firststring)":"89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32",
              "sha256(slughex)":"db14474e9c8fe5e600da3061264597c105794f215399c9694e9da26ef54c1d19",
              "sha256d":"f9719d6d531e6c3b5129644cd05da57bc6fdd075c9a61267c41d4b9627936096"}

def ks_from_hex(keyhex, M):
    return [ (int(c,16) % M) for c in keyhex ]

def over_undo(ds, ks, M):
    return "".join(str((int(ch) - ks[i % len(ks)]) % M) for i, ch in enumerate(ds))

def col_undo(ct, order):
    W = len(order); n = len(ct); nrows = (n + W - 1) // W
    full = n % W if n % W else W
    lens = [nrows if i < full else nrows - 1 for i in range(W)]
    placed = [None] * W; ptr = 0
    for k in range(W):
        oi = order[k]; placed[oi] = ct[ptr:ptr + lens[oi]]; ptr += lens[oi]
    out = []
    for r in range(nrows):
        for c in range(W):
            if r < len(placed[c]):
                out.append(placed[c][r])
    return "".join(out)

def order_for(keyhex, W):
    return sorted(range(W), key=lambda i: (keyhex[i], i))

def to_digits(stream, mp):
    return "".join(str(mp[c]) for c in stream)

ALPHAS = {"title_salp": keyed28("salphaselon"),
          "title_cosm": keyed28("cosmicduality"),
          "title_both": keyed28("salphaseloncosmicduality"),
          "322": "FUBCDORA.LETHINGKYMVPS.JQZXW"}

def score(pt):
    pl = re.sub(r"[^a-zA-Z]", " ", pt).lower(); toks = pl.split()
    if not toks: return -1e9
    G = {"e":12.7,"t":9.1,"a":8.2,"o":7.5,"i":7.0,"n":6.7,"s":6.3,"h":6.1,"r":6.0,"d":4.3,
         "l":4.0,"c":2.8,"u":2.8,"m":2.4,"w":2.4,"f":2.2,"g":2.0,"y":2.0,"p":1.9,"b":1.5,
         "v":1.0,"k":0.8,"j":0.15,"x":0.15,"q":0.10,"z":0.07}
    COMMON = {"the","and","you","that","this","with","not","have","from","they","your",
              "half","better","enter","password","matrix","sumlist","last","words",
              "before","archi","choice","key","private","cosmic","duality","salphas",
              "seed","funded","sender","answer","command","first","hint","yourlast"}
    ug = sum(0.01 * G.get(ch, 0) for ch in pl.replace(" ", ""))
    w = sum(5.0 + len(t) for t in toks if t in COMMON)
    return ug + w

out = []
for dkn, dk in DECODEKEYS.items():
    hexlen = len(dk)  # 64
    for aname, alpha28 in ALPHAS.items():
        for mpn, mp in [("CANON",CANON),("POS",POS)]:
            for (e1,e2) in [(1,4),(2,5)]:
                ctol = build_grid(alpha28, e1, e2)
                order = order_for(dk, hexlen)
                for sn, stream in [("dbbib",DBBIB),("faed",FAED)]:
                    ds = to_digits(stream, mp)
                    # (a) keystream over-encryption undo, then maybe col-undo, then decode
                    for M in (9,10):
                        ks = ks_from_hex(dk, M)
                        for mode, ds2 in [("keystream", over_undo(ds, ks, M)),
                                          ("keystream+col", col_undo(over_undo(ds, ks, M), order)),
                                          ("col", col_undo(ds, order)),
                                          ("none", ds)]:
                            pt = decode(ds2, ctol, e1, e2)
                            sc = score(pt)
                            out.append((sc, dkn, aname, mpn, e1, e2, sn, mode, pt))

out.sort(key=lambda x: -x[0])
print("=== top 20 by legibility (decode-key interpretation) ===")
for sc, dkn, aname, mpn, e1, e2, sn, mode, pt in out[:20]:
    print(f"[{sc:6.1f}] {dkn[:10]} {aname} {mpn} e{e1}{e2} {sn} {mode}")
    print(f"       {pt[:80]}")

cands = set()
for sc, dkn, aname, mpn, e1, e2, sn, mode, pt in out:
    for n in (pt.lower(), pt.upper(), pt):
        if "?" not in n and len(n) >= 8:
            cands.add(n)
print(f"\n[gen] {len(cands)} candidates")
Path("/data/data/com.termux/files/usr/tmp/opencode/decodekey_cands.txt").write_text("\n".join(sorted(cands)))
