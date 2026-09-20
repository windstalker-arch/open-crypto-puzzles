#!/usr/bin/env python3
"""Fresh alphabet sweep through the certified VIC pipeline + oracle.

Tests new keyed-alphabet constructions derived from puzzle elements that were
not in the ~75k community+joint forms already swept. Each alphabet goes through
the full joint decode: digit mapping -> straddling checkerboard -> oracle.
"""
import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode

DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())
DBBIB = d["dbbib"]  # 69 tokens
FAED = d["faed_570"].rstrip("z")  # 569 tokens (z removed)

CANON = {"d":0,"b":1,"i":2,"f":3,"h":4,"c":5,"e":6,"g":7,"a":8}
POS   = {c:i for i,c in enumerate("abcdefghi")}
MAPPINGS = [("CANON", CANON), ("POS", POS)]
ESCAPES = [(1,4), (2,5), (1,2), (3,7), (0,9), (2,7), (3,5), (1,8)]
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def keyed28(keyword):
    """Standard dedupe-then-alpha to 28 chars."""
    kw = "".join(ch for ch in keyword.upper() if ch.isalpha())
    out = ""
    for ch in kw + ALPHA:
        if ch not in out:
            out += ch
    return (out + "./")[:28]

def keyed23(keyword):
    """Dedupe-then-alpha, 23 chars (Bifid lean alphabet)."""
    kw = "".join(ch for ch in keyword.upper() if ch.isalpha())
    out = ""
    for ch in kw + ALPHA:
        if ch not in out:
            if len(out) >= 23:
                break
            out += ch
    return out

def to_digits(stream, mp):
    return "".join(str(mp[c]) for c in stream if c in mp)

def score_legibility(pt):
    """Simple English-frequency + common-word score."""
    import re
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
              "case","manage","crack","belong","need","funds","live"}
    ug = sum(0.01 * G.get(ch, 0) for ch in pl.replace(" ", ""))
    w = sum(5.0 + len(t) for t in toks if t in COMMON)
    # penalize lots of '?' (decode failures)
    qcount = pt.count("?")
    penalty = qcount * 2.0
    return ug + w - penalty

# ---- Fresh alphabet sources ----

alphabets = {}

# 1. Bifid square full row as keyword
alphabets["bifid_row_full"] = keyed28("DBIFHCEGAKLMNOPQRSTUVWXYZ")

# 2. Bifid square columns read down
#    Col1: D,A,L,T,Y; Col2: B,K,M,U; Col3: I,N,O,V; Col4: F,O,P,W; Col5: H,Q,X; Col6: C,R; Col7: E,S; Col8: G,Z
alphabets["bifid_cols"] = keyed28("DALTYBKMOUINOVFOPWHQXCRGZES")

# 3. Even stream letters (B,C,D,E) as a "keyword" (the yinyang channel)
alphabets["even_stream_letters"] = keyed28("BCDE")

# 4. dbbib most frequent letters as keyword (b=19, e=15, g=9, h=7, f=5, i=5, c=4)
alphabets["dbbib_freq"] = keyed28("BEGHFCIDA")

# 5. faed most frequent letters (g=107, i=75, e=69, h=58, f=57, c=52, a=54, b=49, d=49)
alphabets["faed_freq"] = keyed28("GIEHCFABD")

# 6. The "lean 23" alphabet (section 30) as keyword
alphabets["lean23"] = keyed28("ABCDEFGHKLMNPQRSTUVWXYZ")

# 7. Bifid key "DBIFHCEG" as keyword
alphabets["bifid_key"] = keyed28("DBIFHCEG")

# 8. The known phase-3.2.2 alphabet
alphabets["phase322"] = "FUBCDORA.LETHINGKYMVPS.JQZXW"

# 9. Author's "yellow blue primes" as keyword
alphabets["yellow_blue_primes"] = keyed28("YELLOWBLUEPRIMES")

# 10. Author's "yinyang" as keyword
alphabets["yinyang"] = keyed28("YINYANG")

# 11. "in front of your eyes" as keyword
alphabets["in_front_of_eyes"] = keyed28("INFRONTOFOUREYES")

# 12. "theseedisplanted" from the image
alphabets["seed_is_planted"] = keyed28("THESEEDISPLANTED")

# 13. "followthewhiterabbit" 
alphabets["white_rabbit"] = keyed28("FOLLOWTHEWHITERABBIT")

# 14. Bifid square read in spiral from top-left
#    DBIFHCEG -> rows: DBIFHCEG, AKLMNOPQ, RSTUVWXY
#    spiral: D,B,I,F,H,C,E,G,Q,P,O,N,M,L,K,A,R,S,T,U,V,W,X,Y
alphabets["bifid_spiral"] = keyed28("DBIFHCEGQPONMLKARSTUVWXY")

# 15. dbbib stream itself as keyword (69 chars, deduped)
alphabets["dbbib_stream"] = keyed28(DBBIB)

# 16. faed stream first 28 unique chars as keyword
alphabets["faed_prefix"] = keyed28(FAED[:100])

# 17. The 29 dropped I/O bits - treat I=9, O=15, read as letters
#    OOIIOOOIIOOIOIIOIOOOOIOIIOIOI -> numeric: 15,15,9,9,15,15,15,9,9,15,15,9,15,9,9,15,9,15,15,15,15,9,15,9,9,15,9,15,9
#    not useful as keyword; skip

# 18. "primes" 
alphabets["primes"] = keyed28("PRIMES")

# 19. "someneedstobezeroed" (from author hint)
alphabets["zeroed_out"] = keyed28("SOMECHARACTERSNEEDTOBEZEROEDOUT")

# 20. The sha256 slug of the SalPhaseIon page as keyword letters
alphabets["slug_8972"] = keyed28("SALPHASEION")

# 21. "cosmicduality" 
alphabets["cosmic_duality"] = keyed28("COSMICDUALITY")

# 22. Combined author hint phrase
alphabets["author_combined"] = keyed28("YELLOWBLUEPRIMESMATRIXSUMLASTWORDSBEFOREARCHICHOICEYINYANG")

# 23. "btcseed" from the Bifid plaintext head
alphabets["btcseed"] = keyed28("BTCSEED")

# 24. Phase-3 riddle answer
alphabets["venus_thinker"] = keyed28("JACQUEFRESCOHEISENBERG")

# 25. "theflowerblossoms" (phase-2 password)
alphabets["flower"] = keyed28("THEFLOWERBLOSSOMSTHROUGHWHATSEEMSTOBEACONCRETESURFACE")

# Generate all alphabets
print(f"Generated {len(alphabets)} alphabets")
print(f"Streams: dbbib={len(DBBIB)} tokens, faed={len(FAED)} tokens")
print(f"Mappings: {len(MAPPINGS)}, Escape pairs: {len(ESCAPES)}")
total = len(alphabets) * len(MAPPINGS) * len(ESCAPES) * 2  # x2 for dbbib/faed
print(f"Total decode forms: {total}")
print()

# Run all combinations
results = []
for aname, alpha28 in alphabets.items():
    for mpname, mp in MAPPINGS:
        for e1, e2 in ESCAPES:
            ctol = build_grid(alpha28, e1, e2)
            for sname, stream in [("dbbib", DBBIB), ("faed", FAED)]:
                ds = to_digits(stream, mp)
                pt = decode(ds, ctol, e1, e2)
                sc = score_legibility(pt)
                q = pt.count("?")
                if sc > -100:  # only keep non-garbage
                    results.append((sc, aname, mpname, e1, e2, sname, pt, q))

results.sort(key=lambda x: -x[0])

# Show top 30
print("=== Top 30 by legibility ===")
for sc, aname, mpname, e1, e2, sname, pt, q in results[:30]:
    print(f"[{sc:6.1f}] {aname:25s} {mpname:5s} e{e1}{e2} {sname:5s} ?={q:2d}")
    print(f"       {pt[:100]}")

# Collect candidates with no '?' for oracle testing
cands = set()
for sc, aname, mpname, e1, e2, sname, pt, q in results:
    if q == 0 and len(pt) >= 8:
        for form in (pt.lower(), pt.upper(), pt.title()):
            cands.add(form)

print(f"\n[gen] {len(cands)} clean candidates (no decode failures)")
# Write candidates
candfile = os.path.join(ROOT, "tools", "fresh_cands.txt")
with open(candfile, "w") as f:
    f.writelines(c + "\n" for c in sorted(cands))
print(f"Written to {candfile}")
