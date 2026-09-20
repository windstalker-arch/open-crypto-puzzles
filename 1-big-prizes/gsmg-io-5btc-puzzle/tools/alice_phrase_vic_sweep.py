#!/usr/bin/env python3
"""alice_phrase_vic_sweep.py -- test "white rabbit nostalgic alice childhood" words as
keyed-alphabet keywords in the certified straddling-checkerboard decoder over dbbib/faed.

The reassembled sticker phrase (human-confirmed exact: "white rabbit nostalgic alice
childhood") has NEVER been run as a keyed-28 alphabet keyword over the 91/570 streams.
This sweep builds keyed-28 alphabets from the words, orderings, and fusions; decodes
dbbib/faed under CANON/POS digit maps x escape pairs; oracle-tests every clean decode.
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

PHRASE = ["white", "rabbit", "nostalgic", "alice", "childhood"]
PHRASE2 = "whiterabbitnostalgicalicechildhood"
PHRASE_SP = " ".join(PHRASE)


def keyword28(seed):
    kw = "".join(ch for ch in seed.upper() if ch in ALPHA)
    keyed = "".join(dict.fromkeys(kw + ALPHA))
    a = keyed[:8] + "." + keyed[8:18] + "/" + keyed[18:26]
    b = keyed[:8] + "." + keyed[8:18] + "/" + keyed[18:]
    return [a, b, keyed]


def main():
    seeds = {}
    for w in PHRASE:
        seeds[f"word_{w}"] = w
    seeds["phrase_order"] = PHRASE2
    seeds["phrase_spaces"] = PHRASE_SP
    seeds["rabbit_first"] = "rabbitwhitenostalgicalicechildhood"
    seeds["alice_first"] = "alicechildhoodwhiterabbitnostalgic"
    seeds["nostalgic_first"] = "nostalgicalicechildhoodwhiterabbit"
    seeds["white_at_end"] = "rabbitnostalgicalicechildhoodwhite"
    seeds["rab_white_alice_nos_child"] = "rabbitwhitenostalgicalicechildhood"
    seeds["backward"] = "childhoodalicenostalgicrabbitwhite"
    seeds["title"] = "WhiteRabbitNostalgicAliceChildhood"
    seeds["no_e_variant"] = "rabbitnostalgicalicechildhoodwhite"

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
    path = os.path.join(scratch, "alice_phrase_vic_cands.txt")
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

    # show a few sample decodes for eyeballing
    print("\nSample decodes (unique, up to 12):")
    for s, key in candidate_set[:12]:
        print(f"  {s}  [{key}]")


if __name__ == "__main__":
    main()