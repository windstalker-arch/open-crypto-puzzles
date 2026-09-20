#!/usr/bin/env python3
"""custom_keyed_seeds_sweep.py -- "custom substitution cipher keys" research battery.

Genuinely-new keyed-28 alphabet KEYWORD seeds (custom key constructions) over the
AUTHORITATIVE dbbib_91/faed_570 through the certified VIC checkerboard path, both
funded-gate oracles. Seed groups vs the ledger (late-204 F1-F4, late-205 fragments,
late-207 matrix/chess, late-213 script-name, late-163 braille, late-216+):

  G1 certified phrase words (never keyed-28 keywords before):
     WHITERABBIT, THESEEDISPLANTED, ALICE, NOSTALGIC, CHILDHOOD, NOSTALGICALICE,
     ALICECHILDHOOD, WHITERABBITNOSTALGIC, WHITERABBITNOSTALGICALICECHILDHOOD shifts,
     THEARCHITECTCHOICE, ARCHITECT, ARCHICHOICE, COSMICDUALITY, SALPHASEION,
     YINYANG, YELLOWBLUE, PRIMES, YELLOWBLUEPRIMES, THEGREATZION,... no: keep bounded.
  G2 yellow/blue/primes/yinyang ingredient words + pairwise joins (2023-02-23 hint
     parse): YELLOWBLUEPRIMESMATRIXSUMLISTLASTWORDSBEFOREARCHICHOICEYINYANG families.
  G3 keyboard-layout custom alphabets: QWERTY row order, DVORAK, COLEMAK, AZERTY,
     QWERTY alphabetical-by-row, PHONE/T9 keypad order, phone rows "23456789".
  G4 address-derived alphabets: from 1GSMG1JC9... and 17ucy1K9... letter spans;
     GSMG, GSMGIO, GSMG.IO, + numeric-key "1357913579" custom digit alphabets.
  G5 arithmetic-custom (keyed by digit sums): keyword+shift variants are already closed;
     include only "matrixsumlist"-concatenated and base58 alphabet.
"""
import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode, keyed28, CANON, POS, ALPHA  # noqa
from oracle import attempt as att_small        # noqa
from oracle_dualite import attempt as att_dual, load_dualite_b64  # noqa

DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())
FAED = d["faed_570"].rstrip("z")
DBBI = d["dbbib_91"]
assert len(FAED) == 570 and len(DBBI) == 91, (len(FAED), len(DBBI))

Q = "QWERTYUIOPASDFGHJKLZXCVBNM"
DVO = "PYFGCRLAOEUIDHTNSQJKXBMWVZ"
COL = "QWFPGJLUYARSTDHNEIOZXCVBKM"
AZE = "AZERTYUIOPQSDFGHJKLMWXCVBN"
COLE = "QWFGJLUYARSDHNEIOZXCVBKMPT"
T9R = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PHO = "ADGJLMPTWSXBEHKNQUYVZCFIOR"
rowkeys = [Q, DVO, COL, AZE, COLE, T9R, PHO, "PQWERTYUIOASDFGHJKLZXCVBNM",
           "QWERTYUIOPASDFGHJKLZXCVBNM1234567890", "2ABC3DEF4GHI5JKL6MNO7PQRS8TUV9WXYZ",
           "ABC2DEF3GHI4JKL5MNO6PQRS7TUV8WXYZ9"]
# G1
phrase = ["WHITERABBIT", "THESEEDISPLANTED", "ALICE", "NOSTALGIC", "CHILDHOOD",
          "NOSTALGICALICE", "ALICECHILDHOOD", "WHITERABBITNOSTALGICALICECHILDHOOD",
          "THEARCHITECTCHOICE", "ARCHITECT", "ARCHICHOICE", "COSMICDUALITY",
          "SALPHASEION", "YINYANG", "YELLOWBLUE", "PRIMES", "YELLOWBLUEPRIMES",
          "HAREWHITEOUAL", "THEWHITEHARE", "THEHARE"]
# G2
ingr = ["YELLOW", "BLUE", "PRIMES", "MATRIXSUMLIST", "LASTWORDSBEFOREARCHICHOICE",
        "YINYANG"]
G2 = [i+j for i in ["YELLOW", "BLUE"] for j in ingr[1:]] + ["YELLOWBLUEPRIMESMATRIXSUMLIST",
      "MATRIXSUMLISTLASTWORDSBEFOREARCHICHOICEYINYANG", "YINYANGYELLOWBLUE"]
# G4
G4 = ["GSMG", "GSMGIO", "GSMG.IO", "GSMGIO5BTC", "1GSMG1JC9", "17UCY1K9",
      "GSMG1JC9WTDWSWFAWS2XJCMJPA", "UCY1KZUA"]
seeds = list(dict.fromkeys([w for w in phrase + ingr + G2 + G4 if len(w) <= 28] + rowkeys))
SEEDS = list(dict.fromkeys([s.upper() for s in seeds]))

def variants(kw):
    out = set()
    out.add(kw)
    out.add(kw.replace(".", ""))
    out.add(kw.swapcase().upper())
    return sorted(out)

streams = {"DBBI": DBBI, "FAED": FAED}
escapes = [(1, 4), (4, 1), (1, 5), (5, 1)]
blob = load_dualite_b64()

n_small = n_dual = 0
clean = 0
for kw in SEEDS:
    for kwv in variants(kw):
        for mname, M in (("CANON", CANON), ("POS", POS)):
            for e1, e2 in escapes:
                keyed = keyed28(kwv, (".", "/"))
                alpha = keyed[:8] + "." + keyed[8:18] + "/" + keyed[18:]
                assert len(alpha) == 28, alpha
                grid = build_grid(alpha, e1, e2)
                for sname, stream in streams.items():
                    digits = "".join(str(M[ch]) for ch in stream if ch in M)
                    out = decode(digits, grid, e1, e2)
                    if "?" in out:
                        continue
                    if len("".join(ch for ch in out if ch.isalpha())) < 4:
                        continue
                    clean += 1
                    U = set()
                    for dec in (out, out.lower(), out.upper(), out[::-1]):
                        U.add(dec)
                        U.add(dec.replace(" ", ""))
                    for c in U:
                        if len(c) < 4:
                            continue
                        hit, _ = att_small(c)
                        n_small += 1
                        if hit:
                            print("SMALL MATCH:", kw, mname, e1, e2, sname, c)
                            raise SystemExit
                        hit, _ = att_dual(c, blob)
                        n_dual += 1
                        if hit:
                            print("DUALITE MATCH:", kw, mname, e1, e2, sname, c)
                            raise SystemExit
print(f"seeds={len(SEEDS)} clean_decodes={clean} small_gate_tries={n_small} dualite_tries={n_dual}")
print("NO MATCH both gates")