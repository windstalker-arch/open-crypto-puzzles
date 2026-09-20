#!/usr/bin/env python3
"""wordjoin_sweep.py -- test X = the join of all the puzzle's word sequences.

The recovered word tokens from the SalPhaseIon page (z-separated / binary-decoded /
flag tokens) are joined in every order and with simple separators, and tested as the
password X against BOTH funded gates. "Joining all those words sequence" is the
hypothesis: the answer is the concatentation of all the on-page words.

Prior brush-force (sections 114-119) swept pairs/triples/bounded-token phrases but
not the FULL 7-token all-permutation join(s). 7! = 5040 orders x 3 separators x case
variants is cheap for the oracle.

Public/authorized puzzle only. A hit is an oracle MATCH, nothing less.
"""

import itertools
import os
import subprocess
import sys
import time
from pathlib import Path

WORDS = [
    "shabef",
    "matrixsumlist",
    "enter",
    "lastwordsbeforearchichoice",
    "thispassword",
    "ourfirsthintisyourlastcommand",
    "anstoo",
]

SEGI = "agdafaoaheiecggchgicbbhcgbehcfcoabicfdhhcdbbcagbdaiobbgbeadedde"
SEGII = "cfobfdhgdobdgooigdocdaoofidh"

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

    seps = ["", "_", "."]
    for order_tuple in itertools.permutations(WORDS):
        for sep in seps:
            joined = sep.join(order_tuple)
            add(joined)
            add(joined.lower())
            add(joined.upper())
            # capitalize each word (TitleCase) as an alternate joining style
            add(sep.join(w.title() for w in order_tuple))

    # add the seg1/seg2 raw a-i streams appended/prepended to the full page-order join
    page_order_join = "".join(WORDS)
    add(page_order_join)
    add(page_order_join.upper())
    for seg in (SEGI, SEGII):
        add(seg + page_order_join)
        add(page_order_join + seg)
        add(seg + "_" + page_order_join)
        add(page_order_join + "_" + seg)

    print(f"candidate X count: {len(cands)}")

    # write to scratch
    scratch = "/data/data/com.termux/files/usr/tmp/opencode"
    os.makedirs(scratch, exist_ok=True)
    path = os.path.join(scratch, "wordjoin_cands.txt")
    with open(path, "w") as f:
        f.writelines(s + "\n" for s in cands)

    for name, oracle in [("small", ORACLE), ("dualite", ORACLE_DUAL)]:
        t0 = time.time()
        r = subprocess.run([sys.executable, oracle, "--stdin"],
                           input=Path(path).read_bytes(), capture_output=True)
        lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
        hits = [ln for ln in lines if ln.startswith("MATCH")]
        dt = time.time() - t0
        print(f"[{name}] lines={len(lines)} MATCH={len(hits)} in {dt:.1f}s")
        for h in hits:
            print("HIT:", h)
        if not hits:
            print(f"[{name}] NO MATCH")


if __name__ == "__main__":
    main()
