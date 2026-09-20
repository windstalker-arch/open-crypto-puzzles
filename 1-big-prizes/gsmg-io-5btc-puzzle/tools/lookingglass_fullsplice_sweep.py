#!/usr/bin/env python3
"""lookingglass_fullsplice_sweep.py -- full 26x26 splice coverage over two NEW keyed-alphabet
families applied to dbbib_91 + faed_570 through the certified VIC checkerboard:

  (A) recovered stage PASSWORDS ALONE (no phrase join) -- row 163 only tried splice
      positions (8,18); rows 205E/F full-spliced only PHRASE x PASSWORD joins.
  (B) Through-the-Looking-Glass vocabulary (chess / backwards-memory / mirror themes;
      user hint "the world as a huge game of chess") -- never in any keyed family.

Witnesses: tools/certified_vic.py selftest (3.2.2 board reproduces INCASEYOU...) and both
gate oracles --selftest, all PASS before use. Every clean decode goes through both oracles.
"""
import itertools
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

PASSWORDS = [
    "matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
    "anstoo", "ourfirsthintisyourlastcommand", "yourlastcommand",
    "hopeisthequintessentialhumandelusion", "shabef", "firsttint",
    "thearchitectschoice", "causality",
]

LOOKINGGLASS = [
    "lookingglass", "through the lookingglass", "through the looking glass",
    "whiterabbit", "alice", "alice childhood", "white queen", "redqueen",
    "whiteknight", "redknight", "chessboard", "chess", "checkmate", "spot",
    "mirror", "mirrorimage", "backwardsmemory", "memorybackwards",
    "worldasachessboard", "jabberwocky", "jabberwock", "tweedledee",
    "tweedledum", "humptydumpty", "bandersnatch", "looking glass",
    "the world as a huge game of chess", "memory works backwards",
    "aliceinwonderland", "wonderland", "queen of hearts",
]

def keyed26(seed):
    return "".join(dict.fromkeys("".join(ch for ch in seed.upper() if ch in ALPHA) + ALPHA))

def splice(keyed, p1, p2):
    s = list(keyed)
    p1c = min(p1, len(s)); p2c = min(p2, len(s))
    if p1c == p2c:
        return None
    lo, hi = (p1c, p2c) if p1c < p2c else (p2c, p1c)
    s.insert(lo, "."); s.insert(hi + 1, "/")
    return "".join(s)

def english_score(dec):
    if "?" in dec:
        return -1
    s = dec.upper()
    score = sum(3 * s.count(w) for w in ("THE","AND","ING","THA","ENT","ION","YOU","KEY","DOOR","PHASE","WHITE","OPEN","LOCK","DIGIT","GATE","ANSWER","PRIVATE","WALLET","HALF","BETTER","SECRET","HINT","CODE","COSMIC","CHESS","MIRROR","RABBIT","QUEEN","KNGHT","ALICE"))
    score += max(0, len(s) - 20) // 4
    return score

def build_alphabets(seeds):
    alphabets = []
    seen_k26 = {}
    for seed in seeds:
        k = keyed26(seed)
        if not (len(k) == 26 and all(ch in ALPHA for ch in k)):
            continue
        if k not in seen_k26:
            seen_k26[k] = []
        for p1 in range(26):
            for p2 in range(26):
                if p1 == p2:
                    continue
                a28 = splice(k, p1, p2)
                if a28 and a28 not in seen_k26[k]:
                    seen_k26[k].append(a28)
                    alphabets.append(a28)
    return alphabets

def run(alphabets, label):
    cand = []
    cand_strs = set()
    streams = {"dbbib": DBBIB, "faed": FAED}
    maps = {"CANON": CANON, "POS": POS}
    escapes = [(1, 4), (2, 5)]

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
    print(f"[{label}] alphabets={len(alphabets)} clean decodes={len(cand)}")
    print(f"[{label}] Top 15 by English score:")
    for t in cand[:15]:
        print(f"   score={t[1]:4d} {t[0][:80]}")

    scratch = "/data/data/com.termux/files/usr/tmp/opencode"
    os.makedirs(scratch, exist_ok=True)
    all_path = os.path.join(scratch, f"lookingglass_fs_{label}_all.txt")
    Path(all_path).write_text("\n".join(t[0] for t in cand) + "\n")

    top_path = os.path.join(scratch, f"lookingglass_fs_{label}_top200.txt")
    Path(top_path).write_text("\n".join(t[0] for t in cand[:200]) + "\n")

    for name, oracle in [("small", ORACLE), ("dualite", ORACLE_DUAL)]:
        r = subprocess.run([sys.executable, oracle, "--stdin"],
                           input=Path(all_path).read_bytes(), capture_output=True)
        lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
        hits = [ln for ln in lines if ln.startswith("MATCH")]
        print(f"[{label}][{name}] total={len(lines)} MATCH={len(hits)}")
        for h in hits:
            print("[HIT]", h)
    return len(cand)

def main():
    print("WITNESS certified_vic selftest:")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "certified_vic.py")],
                       capture_output=True)
    print("  " + r.stdout.decode().strip())
    for name, oracle in [("small", ORACLE), ("dualite", ORACLE_DUAL)]:
        r = subprocess.run([sys.executable, oracle, "--selftest"], capture_output=True)
        print(f"  oracle[{name}] selftest: " + r.stdout.decode().strip().splitlines()[-1])

    alphas_a = build_alphabets(PASSWORDS)
    alphas_b = build_alphabets(LOOKINGGLASS)
    print("\n=== (A) recovered stage PASSWORDS alone, full splice ===")
    nA = run(alphas_a, "A_pw")
    print("\n=== (B) Looking-Glass / chess / backwards-memory vocabulary, full splice ===")
    nB = run(alphas_b, "B_lg")
    print(f"\nTOTAL clean decodes pushed through both oracles: {nA} + {nB}")

if __name__ == "__main__":
    main()