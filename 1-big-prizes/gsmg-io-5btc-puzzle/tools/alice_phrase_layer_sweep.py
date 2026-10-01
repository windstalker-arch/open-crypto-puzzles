#!/usr/bin/env python3
"""alice_phrase_layer_sweep.py -- Note-25d layered co-sweep: "white rabbit nostalgic
alice childhood" is woven with the ~7 recovered stage passwords into JOINT keyed-28
alphabets applied as the certified VIC checkerboard to dbbib/faed.

Construction (the layered idea from leads.md Note 25d): the streams are NOT a
one-step plaintext; they are the product of ~16 encryptions woven with ~7
passwords. One cheap, previously-untested reading (grep: no tool mixes the Alice
phrase with the recovered passwords) is that the KEYED ALPHABET of the final
checkerboard is itself built by deduping a JOIN of the phrase and one of the
recovered passwords, e.g. keyed26(phrase+pwd) or keyed26(pwd+phrase), possibly
with the certified '.'/'/' splices. All clean decodes are English-scored and the
top set is pushed through both gate addresses.

Recovered stage passwords (from leads.md:881 and tested.md rows 1544/1776/204):
  matrixsumlist, enter, lastwordsbeforearchichoice, thispassword, anstoo,
  ourfirsthintisyourlastcommand, yourlastcommand, hopeisthequintessentialhumandelusion,
  shabef, firsttint(unverified).
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

PHRASE = "whiterabbitnostalgicalicechildhood"
PASSWORDS = [
    "matrixsumlist",
    "enter",
    "lastwordsbeforearchichoice",
    "thispassword",
    "anstoo",
    "ourfirsthintisyourlastcommand",
    "yourlastcommand",
    "hopeisthequintessentialhumandelusion",
    "shabef",
    "firsttint",
]

WORDS = ("THE", "AND", "ING", "THA", "ENT", "ION", "YOU", "RABBIT", "ALICE",
         "KEY", "DOOR", "SEED", "PLANT", "PHASE", "PASSWORD", "WHITE", "OPEN",
         "LOCK", "DIGIT", "GATE", "FIND", "ANSWER", "BUNNY", "BITCOIN", "HTTPS",
         "GSMG", "SHA", "AES", "PRIVAT", "WALLET", "HALF", "BETTER", "TOKEN",
         "SECRET", "HIDDEN", "HINT", "CODE", "CRYPT", "COSMIC")

def keyed26(seed):
    return "".join(dict.fromkeys("".join(ch for ch in seed.upper() if ch in ALPHA) + ALPHA))

def splice(keyed, p1_idx, p2_idx):
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
    score = sum(3 * s.count(w) for w in WORDS)
    score += max(0, len(s) - 20) // 4
    return score

def main():
    # joint seeds: phrase+pwd and pwd+phrase, then a few multi-token joins
    seeds = set()
    for p in PASSWORDS:
        seeds.add(PHRASE + p)
        seeds.add(p + PHRASE)
    seeds.update((
        PHRASE + "thispassword" + "enter",
        PHRASE + "matrixsumlist" + "enter",
        "enter" + PHRASE + "thispassword",
        PHRASE + "ourfirsthintisyourlastcommand",
        "alice" + PHRASE,
        PHRASE + "alice",
    ))

    alphabets = []
    seen = set()
    for seed in sorted(seeds):
        k = keyed26(seed)
        for p1 in (0, 7, 8, 9, 17, 18, 19, 25):
            for p2 in (0, 7, 8, 9, 17, 18, 19, 25):
                a28 = splice(k, p1, p2)
                if a28 and a28 not in seen:
                    seen.add(a28)
                    alphabets.append(a28)
    print("joint alphabets:", len(alphabets), "from seeds:", len(seeds))

    cand = []
    cand_strs = set()
    streams = {"dbbib": DBBIB, "faed": FAED}
    maps = {"CANON": CANON, "POS": POS}
    escape_pairs = [(e1, e2) for e1 in range(10) for e2 in range(10) if e1 != e2][:16]

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
        print(f"  score={t[1]:4d} {t[0][:70]}")

    scratch = "/data/data/com.termux/files/usr/tmp/opencode"
    os.makedirs(scratch, exist_ok=True)
    top = cand[:250]
    path = os.path.join(scratch, "alice_phrase_layer_cands.txt")
    Path(path).write_text("\n".join(t[0] for t in top) + "\n")

    for name, oracle in [("small", ORACLE), ("dualite", ORACLE_DUAL)]:
        r = subprocess.run([sys.executable, oracle, "--stdin"],
                           input=Path(path).read_bytes(), capture_output=True)
        lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
        hits = [ln for ln in lines if ln.startswith("MATCH")]
        print(f"[{name}] tested={len(lines)} MATCH={len(hits)}")
        for h in hits:
            print("HIT:", h)

    # English-limit sanity: dump the best decodes regardless of oracle
    Path(os.path.join(scratch, "alice_phrase_layer_decodes.txt")).write_text(
        "\n".join(f"{t[1]}\t{t[0]}\t{t[2]}\t{t[3]}\t{t[4]}\t{t[5]},{t[6]}" for t in cand) + "\n")

if __name__ == "__main__":
    main()