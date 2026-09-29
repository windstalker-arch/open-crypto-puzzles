#!/usr/bin/env python3
"""ciphertools_combo_sweep.py -- two untested families from the author tool:

  A) COMPOSED cipher & transposition combos.  ciphertools.co.uk offers
     "Affine & Transposition", "Caesar & Transposition",
     "Substitution & Transposition", "Vigenere & Transposition" with
     Transposition = simple (block) or columnar.  Decode order:
     base_decode( transposition_decode(ct, tkey), ckey ).

  B) STREAMS-AS-KEYS.  dbbib(69)/faed(570) treated as cipher KEY material
     applied to the OTHER stream as ciphertext (and self), in both token-value
     conventions (ai: A..I; dbf: DBIFHCEGA).  Ciphers: vigenere, beaufort,
     autokey, porta, substitution, columnar, cadenus, playfair, bifid,
     foursquare, hill 2x2/3x3, amsco.

Both batches feed directly to oracle.py / oracle_dualite.py.
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
    playfair_decode,
    porta_decode,
    railfence_decode,
    substitution_decode,
    transposition_simple_decode,
    vigenere_decode,
)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.loads(Path(os.path.join(BASE, "data", "finalpage-digit-streams.json")).read_text())
DBBIB = DATA["dbbib_91"].lower()   # authoritative; DATA["dbbib"] is the crop
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


def to_ci(stream: str, mode: str) -> str:
    if mode == "ai":
        return "".join(AI[TOKEN_VAL[c]] for c in stream)
    return "".join(DBF[TOKEN_VAL[c]] for c in stream)


def trans_variants(ct: str) -> list[str]:
    """Transposition-decode outputs for the combo family (simple + columnar)."""
    outs = {ct}
    for cols in range(2, 15):
        ident = list(range(1, cols + 1))
        outs.add(transposition_simple_decode(ct, ident, cols))
        outs.add(transposition_simple_decode(ct, list(reversed(ident)), cols))
        outs.add(transposition_simple_decode(ct, ident[1:] + ident[:1], cols))
    for kw in KEYWORDS:
        outs.add(columnar_decode(ct, kw))
    return list(outs)


def base_decodes(ct: str) -> list[str]:
    """Base cipher decode families used by the combo menu."""
    outs = set()
    for shift in range(26):
        outs.add(caesar_decode(ct, shift))
    for mult in (1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25):
        for shift in range(26):
            outs.add(affine_decode(ct, mult, shift))
    for kw in KEYWORDS:
        outs.add(vigenere_decode(ct, kw))
        outs.add(substitution_decode(ct, kw))
    return list(outs)


def build_combo_candidates() -> set[str]:
    cands: set[str] = set()
    for stream in (DBBIB, FAED):
        for mode in ("ai", "dbf"):
            ct = to_ci(stream, mode)
            for t in trans_variants(ct):
                cands.update(base_decodes(t))
    return cands


def build_streamkey_candidates() -> set[str]:
    cands: set[str] = set()
    streams = {"dbbib": DBBIB, "faed": FAED}
    for mode in ("ai", "dbf"):
        mapped = {n: to_ci(s, mode) for n, s in streams.items()}
        for kn, kstream in mapped.items():
            for cn, cstream in mapped.items():
                if kn == cn:
                    continue
                ct = cstream
                key = kstream
                cands.add(vigenere_decode(ct, key))
                cands.add(beaufort_decode(ct, key))
                cands.add(autokey_decode(ct, key))
                cands.add(porta_decode(ct, key))
                cands.add(substitution_decode(ct, key))
                cands.add(columnar_decode(ct, key))
                for h in (25, 26):
                    cands.add(cadenus_decode(ct, key, h))
                cands.add(playfair_decode(ct, key))
                for period in [len(ct)] + list(range(1, min(len(ct), 100) + 1)):
                    cands.add(bifid_decode(ct, key, period))
                cands.add(foursquare_decode(ct, key, key))
                cands.add(foursquare_decode(ct, key, KEYWORDS[0]))
                letters = (key + ALPHABET)[: max(4, len(key))]
                if len(key) >= 4:
                    cands.add(hill_decode(ct, [
                        [ALPHABET.index(letters[0]), ALPHABET.index(letters[1])],
                        [ALPHABET.index(letters[2]), ALPHABET.index(letters[3])]]))
                if len(key) >= 9:
                    cands.add(hill_decode(ct, [
                        [ALPHABET.index(letters[i + 3 * j]) for i in range(3)]
                        for j in range(3)]))
                for cols in (2, 3, 5, 6, 7, 10, 12, 15):
                    cands.add(amsco_decode(ct, True, cols))
                    cands.add(amsco_decode(ct, False, cols))
                cands.add(railfence_decode(ct, 3, 0, True))
    return cands


def main() -> int:
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    cands = sorted(build_combo_candidates() | build_streamkey_candidates())
    if arg == "--dry":
        out = sorted(build_combo_candidates())
        print(f"combo: {len(out)} unique; "
              f"streamkey: {len(build_streamkey_candidates())} unique; "
              f"total: {len(cands)}")
        return 0
    tgt = "/data/data/com.termux/files/usr/tmp/opencode"
    out_path = os.path.join(tgt, "ciphertools_combo_cand.txt")
    with open(out_path, "w") as f:
        for c in cands:
            f.write(c + "\n")
            f.write(c.lower() + "\n")
    print(f"{len(cands)} unique candidates -> {out_path} "
          f"({len(cands) * 2} oracle lines)")

    for name, script in (("1GSMG", "oracle.py"), ("dualite", "oracle_dualite.py")):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script)
        out = os.path.join(tgt, f"oc_combo_{name}.txt")
        print(f"--- {name} ({script}) -> {out}")
        with open(out_path) as fin, open(out, "w") as fout:
            r = subprocess.run([sys.executable, path, "--stdin"],
                               stdin=fin, stdout=fout, stderr=subprocess.STDOUT)
        matches = [l for l in Path(out).read_text().splitlines(keepends=True) if l.startswith("MATCH")]
        print(f"exit={r.returncode}  lines={sum(1 for _ in Path(out).read_text().splitlines(keepends=True))}  "
              f"MATCH={len(matches)}")
        for m in matches[:5]:
            print(m.strip())
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())