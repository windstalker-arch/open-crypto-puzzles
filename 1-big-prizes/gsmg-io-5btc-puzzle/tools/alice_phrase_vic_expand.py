#!/usr/bin/env python3
"""alice_phrase_vic_expand.py -- broaden the Alice-key VIC sweep:
- multiple row-splits for the 28-char alphabet (8/10/10 certified plus 7/11/10, 6/10/12, etc.)
- punctuation '.' '/' spliced at all boundary positions
- decode dbbib/faed under CANON/POS x escape pairs
- score each clean decode for English-likeness (common wordlets)
- oracle-test only the top English-scoring subset
The phrase "white rabbit nostalgic alice childhood" is the key family.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode, CANON, POS, DBBIB, FAED  # noqa

ORACLE = os.path.join(ROOT, "tools", "oracle.py")
ORACLE_DUAL = os.path.join(ROOT, "tools", "oracle_dualite.py")
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

PHRASE2 = "whiterabbitnostalgicalicechildhood"
# common English wordlets for scoring
WORDS = ("THE", "AND", "ING", "THA", "ENT", "ION", "YOU", "RABBIT", "ALICE",
         "KEY", "DOOR", "SEED", "PLANT", "PHASE", "PASSWORD", "WHITE", "OPEN",
         "LOCK", "DIGIT", "GATE", "FIND", "ANSWER", "BUNNY", "BITCOIN", "HTTPS",
         "GSMG", "SHA", "AES", "PRIVAT", "WALLET", "HALF", "BETTER", "TOKEN",
         "SECRET", "HIDDEN", "HINT", "CODE", "CRYPT", "THEFLOWER", "COSMIC")

def keyed26(seed):
    return "".join(dict.fromkeys("".join(ch for ch in seed.upper() if ch in ALPHA) + ALPHA))

def splice(keyed, p1_idx, p2_idx):
    """insert '.' before keyed[p1_idx] and '/' before keyed[p2_idx] -> 28 chars.
    certified layout is '.' at 8 and '/' at 18 (row boundaries); we try all."""
    s = list(keyed)
    p1 = min(p1_idx, len(s)); p2 = min(p2_idx, len(s))
    if p1 == p2:
        return None
    lo, hi = (p1, p2) if p1 < p2 else (p2, p1)
    s.insert(lo, "."); s.insert(hi + (1 if lo < hi else 0), "/")
    return "".join(s)

def english_score(dec):
    if "?" in dec:
        return -1
    s = dec.upper()
    score = 0
    n = len(s)
    for w in WORDS:
        score += 3 * s.count(w)
    # length bonus, punctuation being natural
    score += max(0, n - 20) // 4
    return score

def main():
    seeds = [PHRASE2,
             "whitenostalgicalicechildhoodrabbit",
             "whitealicechildhoodrabbitnostalgic",
             "whiterabbitnostalgicchildhoodalice",
             "rabbitalicewhitenostalgicchildhood"]
    alphabets = []
    seen = set()
    for seed in seeds:
        k = keyed26(seed)
        for p1 in range(0, 26, 1):
            for p2 in range(0, 26, 1):
                a28 = splice(k, p1, p2)
                if a28 and a28 not in seen:
                    seen.add(a28)
                    alphabets.append(a28)
    print("alphabets:", len(alphabets))

    cand = []
    cand_strs = set()
    streams = {"dbbib": DBBIB, "faed": FAED}
    maps = {"CANON": CANON, "POS": POS}
    split_variants = [1]  # build_grid uses row0=8,row1=10,row2=10 on the 28 string
    escape_pairs = [(a, b) for a in range(10) for b in range(10) if a != b][:32]

    for alpha in alphabets:
        for sname, stream in streams.items():
            for mname, mp in maps.items():
                digits = "".join(str(mp[c]) for c in stream if c in mp)
                for (e1, e2) in escape_pairs:
                    ctol = build_grid(alpha, e1, e2)
                    dec = decode(digits, ctol, e1, e2)
                    if "?" not in dec and len(dec) >= 12 and dec not in cand_strs:
                        cand_strs.add(dec)
                        cand.append((dec, english_score(dec), alpha, sname, mname, e1, e2))

    cand.sort(key=lambda t: -t[1])
    print("clean decodes:", len(cand))
    print("Top 15 by English score:")
    for t in cand[:15]:
        print(f"  score={t[1]:4d} {t[0][:60]}")

    scratch = "/data/data/com.termux/files/usr/tmp/opencode"
    os.makedirs(scratch, exist_ok=True)
    top = cand[:200]
    path = os.path.join(scratch, "alice_phrase_vic_expand_cands.txt")
    Path(path).write_text("\n".join(t[0] for t in top) + "\n")

    for name, oracle in [("small", ORACLE), ("dualite", ORACLE_DUAL)]:
        r = subprocess.run([sys.executable, oracle, "--stdin"],
                           input=Path(path).read_bytes(), capture_output=True)
        lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
        hits = [ln for ln in lines if ln.startswith("MATCH")]
        print(f"[{name}] tested={len(lines)} MATCH={len(hits)}")
        for h in hits:
            print("HIT:", h)

if __name__ == "__main__":
    main()