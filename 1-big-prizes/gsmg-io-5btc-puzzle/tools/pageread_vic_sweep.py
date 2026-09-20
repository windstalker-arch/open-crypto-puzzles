#!/usr/bin/env python3
"""pageread_vic_sweep.py -- test the page-own-text-as-keyed-alphabet reading of dbbib/faed.

User directive: the end-to-end joined word/letter sequence of the enhanced SalPhaseIon
image is the thing to "read". The author says the keyed alphabet is "in front of your
eyes". The most literal such reading: the page's OWN text, in reading order, IS the
keyed-alphabet source (keyword-style: unique letters in order, then remaining alphabet).

Method: build keyed-28 alphabets from (a) the unique-in-order letters of the saved
end-to-end joined line, (b) the unique-in-order letters of the human word tokens, and
(c) the unique-in-order letters of each stream separately; run each through the
CERTIFIED straddling-checkerboard decoder (tools/certified_vic.py, which reproduces
phase 3.2.2 verbatim) over dbbib/faed under the CANON/POS digit maps and the escape
pairs 0..9; oracle-test every clean (?-free) decode on both funded gates.

Public/authorized puzzle only. A hit is an oracle MATCH.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode, CANON, POS, DBBIB, FAED  # noqa

BASE = ROOT
ORACLE = os.path.join(BASE, "tools", "oracle.py")
ORACLE_DUAL = os.path.join(BASE, "tools", "oracle_dualite.py")
ENHANCED = os.path.expanduser("~/briefcase/salphaseion-enhanced-word.txt")

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def unique_in_order(s):
    out = ""
    for ch in s.upper():
        if ch in ALPHA and ch not in out:
            out += ch
    return out


def keyed28_from_seed(seed):
    """keyword-style 28-char alphabet: unique-in-order(seed)+remaining letters, and the
    same with '.' / '/' spliced to match the certified 28-length layout."""
    base = unique_in_order(seed) + "".join(c for c in ALPHA if c not in unique_in_order(seed))
    # 28-char: insert '.' after first 8 and '/' after >18? replicate dcode row split.
    a = base[:8] + "." + base[8:18] + "/" + base[18:26]
    return [a, base]  # both a 28-ish and the 26-letter variant


def main():
    line = Path(ENHANCED).read_text().strip().replace(" ", "")

    seeds = {}
    seeds["single_line_page"] = line
    # human word tokens only
    words = "shabefourfirsthintisyourlastcommandanstoomatrixsumlistenter"
    seeds["word_tokens"] = words
    seeds["all_words_7"] = words + "lastwordsbeforearchichoice" + "thispassword"
    seeds["line_dbbib_first"] = line
    # unique letters of each stream
    seeds["dbbib"] = DBBIB
    seeds["faed"] = FAED

    alphabets = []
    seen = set()
    for name, seed in seeds.items():
        for variant in keyed28_from_seed(seed):
            if variant and variant not in seen:
                seen.add(variant)
                alphabets.append((name, variant))

    candidate_set = []  # dict label->string
    cand_strs = set()

    streams = {"dbbib": DBBIB, "faed": FAED}
    maps = {"CANON": CANON, "POS": POS}
    escape_pairs = [(a, b) for a in range(10) for b in range(10) if a != b and a not in ()][:32]

    for aname, alpha in alphabets:
        for sname, stream in streams.items():
            for mname, mp in maps.items():
                digits = "".join(str(mp[c]) for c in stream if c in mp)
                for (e1, e2) in escape_pairs:
                    ctol = build_grid(alpha, e1, e2)
                    dec = decode(digits, ctol, e1, e2)
                    if "?" not in dec and len(dec) >= 8:
                        key = (aname, sname, mname, e1, e2)
                        if dec not in cand_strs:
                            cand_strs.add(dec)
                            candidate_set.append((dec, key))

    print("alpha count:", len(alphabets), " clean decodes:", len(candidate_set))

    scratch = "/data/data/com.termux/files/usr/tmp/opencode"
    os.makedirs(scratch, exist_ok=True)
    path = os.path.join(scratch, "pageread_vic_cands.txt")
    with open(path, "w") as f:
        f.writelines(s + "\n" for s, _ in candidate_set)

    for name, oracle in [("small", ORACLE), ("dualite", ORACLE_DUAL)]:
        r = subprocess.run([sys.executable, oracle, "--stdin"],
                           input=Path(path).read_bytes(), capture_output=True)
        lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
        hits = [ln for ln in lines if ln.startswith("MATCH")]
        print(f"[{name}] lines={len(lines)} MATCH={len(hits)}")
        for h in hits:
            print("HIT:", h)
            for s, key in candidate_set:
                if s in h:
                    print("   ->", s, key)
        if not hits:
            print(f"[{name}] NO MATCH")


if __name__ == "__main__":
    main()
