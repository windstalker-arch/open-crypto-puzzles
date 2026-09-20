#!/usr/bin/env python3
"""salph_wordjoin_sweep.py -- test X = the join of the word sequences visible on
salphaseion_enhanced.png (the top/enhanced SalPhaseIon section), per user directive
that these words should be joined as the password.

Distinct human-readable word tokens on this image (OCR-cleaned), in reading order:
  shabef, ourfirsthintisyourlastcommand, anstoo, matrixsumlist, enter
plus the ledger's other z-separated tokens lastwordsbeforearchichoice, thispassword.
The raw a-i z-segment streams (seg1/seg2) are also joined in where natural.

Public/authorized puzzle only. A hit is an oracle MATCH.
"""
import itertools
import os
import subprocess
import sys
from pathlib import Path

# Distinct word tokens actually printed on the enhanced image, in reading order.
TOKENS = [
    "shabef",
    "ourfirsthintisyourlastcommand",
    "anstoo",
    "matrixsumlist",
    "enter",
]

# z-separated middle-band a-i streams (raw)
SEG1 = "agdafaoaheiecggchgicbbhcgbehcfcoabicfdhhcdbbcagbdaiobbgbeadedde"
SEG2 = "cfobfdhgdobdgooigdocdaoofidh"

# other ledger tokens
EXTRA = ["lastwordsbeforearchichoice", "thispassword"]

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORACLE = os.path.join(BASE, "tools", "oracle.py")
ORACLE_DUAL = os.path.join(BASE, "tools", "oracle_dualite.py")


def main():
    cands = []
    seen = set()

    def add(s):
        if s and s not in seen:
            seen.add(s)
            cands.append(s)

    # 1) the 5 tokens of THIS image, all orders, plain joins
    for perm in itertools.permutations(TOKENS):
        add("".join(perm))
    # 2) page-order join with each token optionally included (vector of booleans)
    n = len(TOKENS)
    for mask in range(1, 1 << n):
        sub = [TOKENS[i] for i in range(n) if mask & (1 << i)]
        add("".join(sub))
    # 3) page-order join of ALL 7 (5 image + 2 ledger words)
    all7 = TOKENS + EXTRA
    for perm in itertools.permutations(all7):
        add("".join(perm))
    # 4) prepend/append the raw seg streams and 'shabef'
    po = "".join(TOKENS)
    for seg in (SEG1, SEG2):
        add(seg + po)
        add(po + seg)
        add(seg + "shabef")
        add("shabef" + seg)
    # 5) 'shabef' variants as prefix (shabef = sha256 hint word)
    for perm in itertools.permutations(TOKENS):
        add("shabef" + "".join(perm))

    # dedupe already done; write and test
    print("candidate X count:", len(cands))
    scratch = "/data/data/com.termux/files/usr/tmp/opencode"
    os.makedirs(scratch, exist_ok=True)
    path = os.path.join(scratch, "salph_wordjoin_cands.txt")
    with open(path, "w") as f:
        f.writelines(s + "\n" for s in cands)

    for name, oracle in [("small", ORACLE), ("dualite", ORACLE_DUAL)]:
        r = subprocess.run([sys.executable, oracle, "--stdin"],
                           input=Path(path).read_bytes(), capture_output=True)
        lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
        hits = [ln for ln in lines if ln.startswith("MATCH")]
        print(f"[{name}] lines={len(lines)} MATCH={len(hits)}")
        for h in hits:
            print("HIT:", h)
        if not hits:
            print(f"[{name}] NO MATCH")


if __name__ == "__main__":
    main()
