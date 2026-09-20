#!/usr/bin/env python3
"""ciphertools_sweep.py -- full 19-cipher sweep of the ciphertools.co.uk suite
against the GSMG raw streams (dbbib 69, faed 570), feeding every decoded
candidate to both funded-gate oracles (oracle.py / oracle_dualite.py).

Usage:
    python3 tools/ciphertools_sweep.py --dry        # count candidates only
    python3 tools/ciphertools_sweep.py --peek N     # print first N candidates
    python3 tools/ciphertools_sweep.py              # build candidate list, run oracles

Input streams: raw a..i tokens.  Two ciphertext-alphabet conventions:
  - 'ai':  token value v -> letter A+v   (A=0..I=8)
  - 'dbf': token value v -> D,B,I,F,H,C,E,G,A[v]   (canonical Bifid-row lead)
Candidates are the ciphers' A-Z plaintext outputs (uppercase + lowercase),
deduplicated across conventions and ciphers, then line-fed to each oracle.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ciphertools_ciphers import (
    ALPHABET,
    affine_decode,
    amsco_decode,
    autokey_decode,
    beaufort_decode,
    bifid_decode,
    cadenus_decode,
    caesar_decode,
    columnar_decode,
    foursquare_decode,
    hill_decode,
    nihilist_decode,
    playfair_decode,
    porta_decode,
    railfence_decode,
    substitution_decode,
    transposition_simple_decode,
    vigenere_decode,
)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.loads(Path(os.path.join(BASE, "data", "finalpage-digit-streams.json")).read_text())
DBBIB = DATA["dbbib"]
FAED = DATA["faed_570"].rstrip("z").lower()
TOKEN_VAL = {chr(ord("a") + i): i for i in range(9)}
AI = "ABCDEFGHI"
DBF = "DBIFHCEGA"

KEYWORDS = [
    "DBIFHCEG", "WHITERABBIT", "ZEBRAFISH", "GSMG", "MONARCHY", "POTATO",
    "CIPHER", "FORTIFICATION", "LEMON", "LEMONKEY", "KEYWORD", "CARDANO",
    "CAUSALITY", "CHOICE", "ILLUSION", "FREEDOM", "POWER", "DESSERT",
    "MATRIX", "SPOON", "REDPILL", "FOLLOWTHEWHITERABBIT", "RABBIT",
    "BTCSEED", "BITCOIN", "KEYMAKERS", "SALPHASION", "COSMICDUALITY",
    "DUALITY", "MOON", "TOTHEMOON", "INTERPRETER", "ALPHABET", "SECRET",
    "ALICE", "WONDERLAND", "SOLVE", "PRIZE",
]
KEYWORDS = list(dict.fromkeys(k.upper() for k in KEYWORDS))
FS_KEYS = [k for k in KEYWORDS if 4 <= len(k) <= 12][:10]


def to_ci(stream: str, mode: str) -> str:
    if mode == "ai":
        return "".join(AI[TOKEN_VAL[c]] for c in stream)
    return "".join(DBF[TOKEN_VAL[c]] for c in stream)


def to_digits(stream: str) -> str:
    return "".join(str(TOKEN_VAL[c]) for c in stream)


def build_candidates() -> set[str]:
    cands: set[str] = set()
    for stream_name, stream in (("dbbib", DBBIB), ("faed", FAED)):
        for mode in ("ai", "dbf"):
            ct = to_ci(stream, mode)
            n = len(ct)

            # ---- Caesar / Affine
            for shift in range(26):
                cands.add(caesar_decode(ct, shift))
            for mult in (1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25):
                for shift in range(26):
                    cands.add(affine_decode(ct, mult, shift))

            # ---- Vigenere / Beaufort / Autokey / Porta
            for kw in KEYWORDS:
                cands.add(vigenere_decode(ct, kw))
                cands.add(beaufort_decode(ct, kw))
                cands.add(autokey_decode(ct, kw))
                cands.add(porta_decode(ct, kw))

            # ---- Bifid (all periods x keyed squares)
            for kw in [""] + KEYWORDS:
                for period in [n] + list(range(1, n + 1)):
                    cands.add(bifid_decode(ct, kw, period))

            # ---- Playfair / FourSquare
            for kw in [""] + KEYWORDS:
                cands.add(playfair_decode(ct, kw))
            for k1 in FS_KEYS:
                for k2 in FS_KEYS:
                    cands.add(foursquare_decode(ct, k1, k2))

            # ---- Railfence / Amsco
            for rails in range(2, 13):
                for start in range(rails):
                    cands.add(railfence_decode(ct, rails, start, True))
                    cands.add(railfence_decode(ct, rails, start, False))
            for cols in range(2, 13):
                cands.add(amsco_decode(ct, True, cols))
                cands.add(amsco_decode(ct, False, cols))

            # ---- Cadenus / Substitution
            for kw in KEYWORDS:
                cands.add(cadenus_decode(ct, kw, 25))
                cands.add(cadenus_decode(ct, kw, 26))
                cands.add(substitution_decode(ct, kw))

            # ---- Transposition simple / columnar
            for cols in range(2, 15):
                identity = list(range(1, cols + 1))
                cands.add(transposition_simple_decode(ct, identity, cols))
                cands.add(transposition_simple_decode(
                    ct, list(reversed(identity)), cols))
                cands.add(transposition_simple_decode(
                    ct, identity[1:] + identity[:1], cols))
            for kw in KEYWORDS:
                cands.add(columnar_decode(ct, kw))

            # ---- Hill (keyword-derived 2x2 / 3x3 + small integer matrices)
            for kw in KEYWORDS:
                letters = (kw + ALPHABET)[: max(4, len(kw))]
                if len(kw) >= 4:
                    k2 = [[ALPHABET.index(letters[0]), ALPHABET.index(letters[1])],
                          [ALPHABET.index(letters[2]), ALPHABET.index(letters[3])]]
                    cands.add(hill_decode(ct, k2))
                if len(kw) >= 9:
                    k3 = [[ALPHABET.index(letters[i + 3 * j])
                           for i in range(3)] for j in range(3)]
                    cands.add(hill_decode(ct, k3))
            for a in range(8):
                for b in range(8):
                    for c in range(8):
                        for d in range(8):
                            m = [[a, b], [c, d]]
                            if __import__("math").gcd((a * d - b * c) % 26, 26) == 1:
                                cands.add(hill_decode(ct, m))

            # ---- Nihilist (raw-token digit pairs, both coord conventions)
            digits = to_digits(stream)
            for sq in [""] + KEYWORDS:
                for add in [""] + KEYWORDS:
                    cands.add(nihilist_decode(digits, sq, add, 0))
                    cands.add(nihilist_decode(digits, sq, add, 1))
    return cands


def main() -> int:
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    cands = sorted(build_candidates())
    if arg == "--dry":
        print(f"{len(cands)} unique candidates")
        return 0
    if arg == "--peek":
        lim = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        for c in cands[:lim]:
            print(c)
        return 0

    out = os.path.join("/data/data/com.termux/files/usr/tmp/opencode",
                       "ciphertools_cand.txt")
    with open(out, "w") as f:
        for c in cands:
            f.write(c + "\n")
            f.write(c.lower() + "\n")
    print(f"{len(cands)} unique candidates -> {out} "
          f"({len(cands) * 2} oracle lines)")

    for name, script in (("1GSMG", "oracle.py"), ("dualite", "oracle_dualite.py")):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script)
        print(f"--- {name} ({script})")
        with open(out) as fin:
            r = subprocess.run([sys.executable, path, "--stdin"],
                               stdin=fin, capture_output=True, text=True)
            print(r.stdout[-2000:])
            print(f"exit={r.returncode}")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())