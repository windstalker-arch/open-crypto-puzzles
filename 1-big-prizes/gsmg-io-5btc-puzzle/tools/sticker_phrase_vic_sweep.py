#!/usr/bin/env python3
"""sticker_phrase_vic_sweep.py -- test the user-reassembled sticker phrase words as
keyed-alphabet keywords in the certified straddling-checkerboard decoder over dbbib/faed.

The 8 /theseedisplanted stickers, reassembled per the user hint "you can open lock digit
banking warning", resolve to the natural words: you, can, open, lock, digit, banking,
warning (with leftover crypto/gic/lo fragments). Prior Note 26 (tested.md 25) only swept
the RAW fragment strings and the fused concatenation; it never used these FULL words as
checkerboard keyed-alphabet keywords.

Method: build keyed-28 alphabets from each word, the sentence order, and the fused phrase;
decode dbbib/faed under CANON/POS digit maps x escape pairs; oracle-test every clean
(?-free) decode on both funded gates. A hit is an exact oracle MATCH only.
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

PHRASE = ["you", "can", "open", "lock", "digit", "banking", "without", "warning"]
PHRASE2 = "youcanopenlockdigitbankingwithoutwarning"


def unique_in_order(s):
    out = ""
    for ch in s.upper():
        if ch in ALPHA and ch not in out:
            out += ch
    return out


def keyword28(seed):
    kw = "".join(ch for ch in seed.upper() if ch in ALPHA)
    keyed = "".join(dict.fromkeys(kw + ALPHA))
    base = keyed + "."  # placeholder; will use variants below
    # certified 28 form mirrors FUBCDORA.LETHINGKYMVPS.JQZXW: 8 + '.' + 10 + '/' + 10
    a = keyed[:8] + "." + keyed[8:18] + "/" + keyed[18:26]
    b = keyed[:8] + "." + keyed[8:18] + "/" + keyed[18:]
    return [a, b, keyed]


def main():
    seeds = {}
    for w in PHRASE:
        seeds[f"word_{w}"] = w
    seeds["phrase_order"] = PHRASE2
    seeds["phrase_spaces"] = " ".join(PHRASE)
    seeds["fused_banking_first"] = "bankingwarningwithoutyoucanopenlockdigit"
    seeds["fused_digit_first"] = "digitbankingwithoutwarningyoucanopenlock"
    seeds["fused_open_first"] = "openlockdigitbankingwithoutwarningyoucan"
    seeds["fused_can_first"] = "canopenlockdigitbankingwithoutwarningyou"
    # leftover fragments as candidates too
    seeds["leftover"] = "cryptogiclo"
    seeds["full_all_frags"] = "bankingwarcadigilocklocryptogicnyouopenlockningt"

    alphabets = []
    seen = set()
    for name, seed in seeds.items():
        for variant in keyword28(seed):
            if variant and variant not in seen:
                seen.add(variant)
                alphabets.append((name, variant))

    candidate_set = []
    cand_strs = set()
    streams = {"dbbib": DBBIB, "faed": FAED}
    maps = {"CANON": CANON, "POS": POS}
    escape_pairs = [(a, b) for a in range(10) for b in range(10) if a != b][:32]

    for aname, alpha in alphabets:
        for sname, stream in streams.items():
            for mname, mp in maps.items():
                digits = "".join(str(mp[c]) for c in stream if c in mp)
                for (e1, e2) in escape_pairs:
                    ctol = build_grid(alpha, e1, e2)
                    dec = decode(digits, ctol, e1, e2)
                    if "?" not in dec and len(dec) >= 8 and dec not in cand_strs:
                        cand_strs.add(dec)
                        candidate_set.append((dec, (aname, sname, mname, e1, e2)))

    print("alpha count:", len(alphabets), " clean decodes:", len(candidate_set))

    scratch = "/data/data/com.termux/files/usr/tmp/opencode"
    os.makedirs(scratch, exist_ok=True)
    path = os.path.join(scratch, "sticker_phrase_vic_cands.txt")
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
