#!/usr/bin/env python3
"""alice_phrase_layer_fullsplice.py -- full 26x26 splice coverage on the joint phrase+password
keyed-28 alphabets (expanding the 8-position subset tested in alice_phrase_layer_sweep.py).
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode, CANON, POS, DBBIB, FAED

ORACLE = os.path.join(ROOT, "tools", "oracle.py")
ORACLE_DUAL = os.path.join(ROOT, "tools", "oracle_dualite.py")
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PHRASE = "whiterabbitnostalgicalicechildhood"
PASSWORDS = [
    "matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
    "anstoo", "ourfirsthintisyourlastcommand", "yourlastcommand",
    "hopeisthequintessentialhumandelusion", "shabef", "firsttint",
]

def keyed26(seed):
    return "".join(dict.fromkeys("".join(ch for ch in seed.upper() if ch in ALPHA) + ALPHA))

def splice(keyed, p1, p2):
    s = list(keyed)
    p1c = min(p1, len(s)); p2c = min(p2, len(s))
    if p1c == p2c:
        return None
    lo, hi = (p1c, p2c) if p1c < p2c else (p2c, p1c)
    s.insert(lo, "."); s.insert(hi + (1 if lo < hi else 0), "/")
    return "".join(s)

def english_score(dec):
    if "?" in dec:
        return -1
    s = dec.upper()
    score = sum(3 * s.count(w) for w in ("THE","AND","ING","THA","ENT","ION","YOU","KEY","DOOR","PHASE","WHITE","OPEN","LOCK","DIGIT","GATE","ANSWER","PRIVATE","WALLET","HALF","BETTER","SECRET","HINT","CODE","COSMIC"))
    score += max(0, len(s) - 20) // 4
    return score

def main():
    seeds = set()
    for p in PASSWORDS:
        seeds.add(PHRASE + p); seeds.add(p + PHRASE)
    seeds.update((PHRASE+"thispassword"+"enter", PHRASE+"matrixsumlist"+"enter",
                   "enter"+PHRASE+"thispassword", PHRASE+"ourfirsthintisyourlastcommand",
                   "alice"+PHRASE, PHRASE+"alice"))

    alphabets = []
    seen = set()
    for seed in seeds:
        k = keyed26(seed)
        for p1 in range(26):
            for p2 in range(26):
                if p1 == p2:
                    continue
                a28 = splice(k, p1, p2)
                if a28 and a28 not in seen:
                    seen.add(a28)
                    alphabets.append(a28)
    print("full-splice alphabets:", len(alphabets))

    cand = []
    cand_strs = set()
    streams = {"dbbib": DBBIB, "faed": FAED}
    maps = {"CANON": CANON, "POS": POS}
    escapes = [(1,4), (2,5)]

    for alpha in alphabets:
        for sname, stream in streams.items():
            for mname, mp in maps.items():
                digits = "".join(str(mp[c]) for c in stream if c in mp)
                for (e1, e2) in escapes:
                    ctol = build_grid(alpha, e1, e2)
                    dec = decode(digits, ctol, e1, e2)
                    if "?" not in dec and len(dec) >= 12 and dec not in cand_strs:
                        cand_strs.add(dec)
                        cand.append((dec, english_score(dec), alpha, sname, mname, e1, e2))

    cand.sort(key=lambda t: -t[1])
    print("clean decodes:", len(cand))
    print("Top 20 by English score:")
    for t in cand[:20]:
        print(f"  score={t[1]:4d} {t[0][:80]}")

    scratch = "/data/data/com.termux/files/usr/tmp/opencode"
    os.makedirs(scratch, exist_ok=True)
    top = cand[:500]
    path = os.path.join(scratch, "alice_phrase_layer_fullsplice_cands.txt")
    Path(path).write_text("\n".join(t[0] for t in top) + "\n")

    for name, oracle in [("small", ORACLE), ("dualite", ORACLE_DUAL)]:
        r = subprocess.run([sys.executable, oracle, "--stdin"],
                           input=Path(path).read_bytes(), capture_output=True)
        lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
        hits = [ln for ln in lines if ln.startswith("MATCH")]
        print(f"[{name}] tested={len(lines)} MATCH={len(hits)}")
        for h in hits:
            print("HIT:", h)

    # also full oracle on all
    all_path = os.path.join(scratch, "alice_phrase_layer_fullsplice_all.txt")
    all_dec = [t[0] for t in cand]
    Path(all_path).write_text("\n".join(all_dec) + "\n")
    print(f"\nAll {len(all_dec)} decodes -> oracle check:")
    for name, oracle in [("small", ORACLE), ("dualite", ORACLE_DUAL)]:
        r = subprocess.run([sys.executable, oracle, "--stdin"],
                           input=Path(all_path).read_bytes(), capture_output=True)
        hits = [ln for ln in r.stdout.decode().splitlines() if ln.startswith("MATCH")]
        print(f"  [{name}] total={sum(1 for ln in r.stdout.decode().splitlines() if ln.strip())} MATCH={len(hits)}")
        for h in hits:
            print("  HIT:", h)

if __name__ == "__main__":
    main()
