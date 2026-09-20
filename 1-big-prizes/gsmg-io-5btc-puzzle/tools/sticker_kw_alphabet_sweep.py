#!/usr/bin/env python3
"""sticker_kw_alphabet_sweep.py -- the /theseedisplanted color-sticker fragment WORDS as
keyed-28 straddling-checkerboard alphabets over dbbib/faed, certified decode, both gates.

Genuinely-new cell vs the recorded rows:
- tested.md 121/122/123 / Note 26: fragments tested as direct PASSWORD strings X.
- tested.md ~3437: sticker_phrase_vic_sweep.py rebuilt the stickers into NATURAL words
  ("you can open lock digit banking without warning") and used THOSE as keywords.
The color-grouped per-file FRAGMENT words -- blue group cadigilocklo, red group
cryptogicnyouopenlockningt, black bankingwar, the 8 per-file words, and the page-order
fused -- have never been used as keyed-28 ALPHABET keywords feeding the certified
checkerboard.

Method: keyed28(seed) for the fragment seeds, map each payload (faed 570 / dbbib69 /
dbbib91) to digits via CANON and POS, decode with the certified checkerboard under the
proven escape pair (1,4); also sweep ALL escape pairs for completeness. Clean (no '?')
decodes -> raw/lower/upper/reversed answer-forms -> both funded-gate oracles.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode, CANON, POS  # noqa

OGDIR = "/data/data/com.termux/files/home"
DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())
FAED = d["faed_570"].rstrip("z")
DBBI69 = d["dbbib"]
DBBI91 = Path(os.path.join(OGDIR, "tmp", "grid_dbbib.txt")).read_text().strip()
assert len(FAED) == 570 and len(DBBI69) == 69 and len(DBBI91) == 91

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ORACLE_SMALL = os.path.join(ROOT, "tools", "oracle.py")
ORACLE_DUAL = os.path.join(ROOT, "tools", "oracle_dualite.py")
OUT = os.path.join(OGDIR, "tmp", "sticker_kw_cands.txt")


def keyed28(seed):
    kw = "".join(ch for ch in seed.upper() if ch.isalpha())
    out = ""
    for ch in kw + ALPHA:
        if ch not in out:
            out += ch
    return (out + "./")[:28]


def to_digits(stream, mp):
    return "".join(str(mp[c]) for c in stream if c in mp)


seeds = {
    # 8 per-file words (Note 26 / tested.md 121 pixel+OCR read)
    "file_bankingwar": "bankingwar",
    "file_ca": "ca",
    "file_digi": "digi",
    "file_locklo": "locklo",
    "file_cryptogic": "cryptogic",
    "file_nyou": "nyou",
    "file_openlockning": "openlockning",
    "file_t": "t",
    # color groups
    "blue_3": "cadigilocklo",
    "blue_dogi": "cadigi",        # first two blue
    "red_4": "cryptogicnyouopenlockningt",
    "red_3_nyou_short": "cryptogicnyouopenlockning",   # without t
    # black + color groups
    "black_blue_red": "bankingwarcadigilocklocryptogicnyouopenlockningt",
    "blue_red": "cadigilocklocryptogicnyouopenlockningt",
    "red_blue": "cryptogicnyouopenlockningtcadigilocklo",
    # per-color first letters (color-key interpolation)
    "acrostic_blue": "cdl",
    "acrostic_red": "cnot",
    "acrostic_br": "bcdlcnot",
    # fragment variants
    "banking": "banking",
    "war": "war",
    "dig": "dig",
    "crypto": "crypto",
    "gic": "gic",
    "you": "you",
    "open": "open",
    "lock": "lock",
    "ing": "ing",
    "lo": "lo",
    "n": "n",
}


def main():
    alphab = []
    seen = set()
    for name, seed in seeds.items():
        a = keyed28(seed)
        if a not in seen:
            seen.add(a)
            alphab.append((name, seed, a))

    streams = {"faed570": FAED, "dbbi69": DBBI69, "dbbi91": DBBI91}
    maps = {"CANON": CANON, "POS": POS}
    escape_pairs = [(a, b) for a in range(10) for b in range(10) if a != b]
    escape_pairs = [(1, 4)] + [p for p in escape_pairs if p != (1, 4)]

    cands = set()
    records = []
    for name, seed, a in alphab:
        for sname, stream in streams.items():
            for mname, mp in maps.items():
                digits = to_digits(stream, mp)
                for (e1, e2) in escape_pairs:
                    ctol = build_grid(a, e1, e2)
                    dec = decode(digits, ctol, e1, e2)
                    if "?" not in dec and 8 <= len(dec):
                        for form in unfold(dec):
                            if form not in cands:
                                cands.add(form)
                                records.append((form, name, seed, sname, mname, e1, e2))

    print(f"alphabets={len(alphab)}  escape_pairs={len(escape_pairs)}  "
          f"decode_forms={len(alphab)*len(streams)*len(maps)*len(escape_pairs)}  "
          f"clean_answers={len(cands)}")

    with open(OUT, "w") as f:
        for form, *_ in records:
            f.write(form + "\n")

    for label, oracle in [("small", ORACLE_SMALL), ("dualite", ORACLE_DUAL)]:
        r = subprocess.run([sys.executable, oracle, "--stdin"],
                           input=Path(OUT).read_bytes(), capture_output=True)
        lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
        hits = [ln for ln in lines if ln.startswith("MATCH")]
        print(f"[{label}] lines={len(lines)} MATCH={len(hits)}")
        for h in hits:
            print("HIT:", h)
            for form, name, seed, sname, mname, e1, e2 in records:
                if form in h:
                    print("   ->", form, "|", name, "|", sname, mname, (e1, e2))
        if not hits:
            print(f"[{label}] NO MATCH")


def unfold(dec):
    out = {dec}
    out.add(dec.lower())
    out.add(dec.upper())
    out.add(dec[::-1])
    return out


if __name__ == "__main__":
    main()