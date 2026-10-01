#!/usr/bin/env python3
"""nato_check_sweep.py -- user steer "check" inside the NATO-codeword frame:
chess/check/checkerboard vocabulary NATO-translated (CharlieHotelEchoCharlieKilo...)
as literal X candidates and as keyed-28 checkerboard alphabet keywords over
dbbib(91)/faed(570), both gate addresses.

Complements the NATO phrase-translation sweep (tools/nato_vic_sweep.py, late-207):
that batch translated the puzzle's own phrases; this one translates the
check/chess/checkerboard steer vocabulary (the checkerboard cipher family, the
phase-2 "buddhist move" chess link, and Willie GNU/dcode naming) through the same
justindmartin/NATO-ICAO-Alphabet-Translator codeword set. Raw (untranslated) check/
chess keywords over the streams were already swept in late-206 (0 clean decodes);
the NATO-joined codeword keyword forms are the new cell here.

Mechanics identical to sticker_color_vic_sweep/nato_vic_sweep: keyed28(seed) ->
dedupe+alpha -> 26, append './' -> build_grid/decode (certified 3.2.2 decode) x
{dbbib91, faed570} x {CANON, POS} x 90 escape pairs; clean (?-free, len>=8) decodes
-> {raw, lower, upper, reverse}; both funded-gate oracles.

A hit is an exact oracle MATCH only.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode, CANON, POS, ALPHA  # noqa

OGDIR = os.path.expanduser("~")
DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())
FAED = d["faed_570"].rstrip("z")
DBBI = d["dbbib_91"]
assert len(FAED) == 570 and len(DBBI) == 91, (len(FAED), len(DBBI))

ORACLE_SMALL = os.path.join(ROOT, "tools", "oracle.py")
ORACLE_DUAL = os.path.join(ROOT, "tools", "oracle_dualite.py")
OUT = os.path.join(OGDIR, "tmp", "nato_check_cands.txt")
OUT_LIT = os.path.join(OGDIR, "tmp", "nato_check_literals.txt")

NATO_OFF = {
    "a": "Alfa", "b": "Bravo", "c": "Charlie", "d": "Delta", "e": "Echo",
    "f": "Foxtrot", "g": "Golf", "h": "Hotel", "i": "India", "j": "Juliett",
    "k": "Kilo", "l": "Lima", "m": "Mike", "n": "November", "o": "Oscar",
    "p": "Papa", "q": "Quebec", "r": "Romeo", "s": "Sierra", "t": "Tango",
    "u": "Uniform", "v": "Victor", "w": "Whiskey", "x": "Xray",
    "y": "Yankee", "z": "Zulu",
}
NATO_REPO = dict(NATO_OFF, **{"a": "Alpha", "j": "Juliet"})

# check / chess / checkerboard steer vocabulary (cipher apps, sworn/dcode naming,
# phase-2 "buddhist move Rc6/Ke4" linkage, the certified 3.2.2 plaintext frame)
VOCAB = [
    "check", "checks", "checked", "checking", "checkcheck", "checkit",
    "checkmate", "checker", "checkers", "chequer", "chequers", "checkerboard",
    "checkered", "checkerboardcipher", "straddling", "straddlingcheckerboard",
    "chess", "chessboard", "chessboardcipher", "chessmatch", "board", "cipher",
    "code", "dcode", "vic", "scap", "chap", "schap", "wille", "gnu", "carlsen",
    "fischer", "tal", "kasparov", "buddhist", "buddhistmove", "move",
    "king", "queen", "rook", "bishop", "knight", "pawn", "castle", "mate",
    "rc6", "g6c6", "rg6c6", "ke4", "kg8", "halfandbetterhalf",
    "incaseyoumanagetocrackthis",
    # spellings of the steer itself
    "chk", "xraycheck", "checkertown", "checkmark",
]

def tr(word, tbl):
    return "".join(tbl.get(ch, ch) for ch in word.lower() if ch.isalpha() and ch in tbl)

def nato_words(word, tbl):
    return [tbl[ch] for ch in word.lower() if ch.isalpha() and ch in tbl]

def f_seeds():
    out = set()
    for v in VOCAB:
        for tblname, tbl in (("off", NATO_OFF), ("repo", NATO_REPO)):
            words = nato_words(v, tbl)
            joiner_forms = ["", "-", " "]
            for joiner in joiner_forms:
                joined = joiner.join(words)
                for f in (joined, joined.lower(), joined.upper(), joined.title(),
                          joined[::-1]):
                    out.add(f)
            out.add(tr(v, tbl))
            out.add(tr(v, tbl).lower())
            out.add(tr(v, tbl).upper())
            # per-letter word.sep forms
            sp = " ".join(words)
            out.add(sp); out.add(sp.lower()); out.add(sp.upper())
    # cross-joins with the page tokens (NATO-joined forms only)
    tokens = ["matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword"]
    bases = ["check", "checker", "checkerboard", "chess", "chessboard", "straddling",
             "straddlingcheckerboard", "buddhist"]
    for base in bases:
        for tok in tokens:
            for tblname, tbl in (("off", NATO_OFF), ("repo", NATO_REPO)):
                b = "".join(tbl[c] for c in base)
                t = "".join(tbl[c] for c in tok)
                out.add(b + t); out.add(t + b)
                out.add(b.upper() + t.upper()); out.add((b + t).lower())
    # chess SAN wrappers with NATO digits
    for san in ("rc6", "g6c6", "rg6c6", "ke4", "kg8", "kxf6"):
        for tblname, tbl in (("off", NATO_OFF), ("repo", NATO_REPO)):
            words = []
            for ch in san:
                if ch.isalpha():
                    words.append(tbl[ch])
                elif ch.isdigit():
                    words.append({"0": "Zero", "1": "One", "2": "Two", "3": "Three",
                                  "4": "Four", "5": "Five", "6": "Six", "7": "Seven",
                                   "8": "Eight", "9": "Nine"}[ch])
                elif ch == "x":
                    words.append(tbl["x"])
            joined = "".join(words)
            out.add(joined); out.add(joined.lower()); out.add(joined.upper())
            sp = " ".join(words)
            out.add(sp); out.add(sp.lower())
    return sorted(out)

def keyed28(seed):
    kw = "".join(ch for ch in seed.upper() if ch in ALPHA)
    keyed = ""
    for ch in kw + ALPHA:
        if ch not in keyed:
            keyed += ch
    return (keyed + "./")[:28]

def to_digits(stream, mp):
    return "".join(str(mp[c]) for c in stream if c in mp)

def unfold(dec):
    return {dec, dec.lower(), dec.upper(), dec[::-1]}

def main(gen_only=False):
    seeds = f_seeds()
    print(f"seed count: {len(seeds)}", flush=True)
    alphab, seen = [], set()
    for seed in seeds:
        a = keyed28(seed)
        if a not in seen:
            seen.add(a)
            alphab.append((seed, a))
    print(f"keyed-28 alphabets: {len(alphab)}", flush=True)

    streams = {"dbbib91": DBBI, "faed570": FAED}
    maps = {"CANON": CANON, "POS": POS}
    escape_pairs = [(a, b) for a in range(10) for b in range(10) if a != b]
    escape_pairs = [(1, 4)] + [p for p in escape_pairs if p != (1, 4)]

    cands, records = set(), []
    for seed, a in alphab:
        for sname, stream in streams.items():
            for mname, mp in maps.items():
                digits = to_digits(stream, mp)
                for (e1, e2) in escape_pairs:
                    dec = decode(digits, build_grid(a, e1, e2), e1, e2)
                    if "?" not in dec and len(dec) >= 8:
                        for form in unfold(dec):
                            if form not in cands:
                                cands.add(form)
                                records.append((form, seed, sname, mname, e1, e2))
    print(f"escape_pairs={len(escape_pairs)}  "
          f"decode_forms={len(alphab)*len(streams)*len(maps)*len(escape_pairs)}  "
          f"clean_candidates={len(cands)}", flush=True)

    with open(OUT, "w") as f:
        for form, *_ in records:
            f.write(form + "\n")
    with open(OUT_LIT, "w") as f:
        for seed in seeds:
            f.write(seed + "\n")
            f.write(seed.lower() + "\n")
            f.write(seed.upper() + "\n")

    if gen_only:
        print(f"wrote {OUT} ({len(cands)} unique) and {OUT_LIT} ({len(seeds)*3} lines)",
              flush=True)
        return

    for label, oracle in [("small", ORACLE_SMALL), ("dualite", ORACLE_DUAL)]:
        for name, path in [("decodes", OUT), ("literals", OUT_LIT)]:
            r = subprocess.run([sys.executable, oracle, "--stdin"],
                               input=Path(path).read_bytes(), capture_output=True)
            lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
            hits = [ln for ln in lines if ln.startswith("MATCH")]
            print(f"[{label} {name}] lines={len(lines)} MATCH={len(hits)}")
            for h in hits:
                print("HIT:", h)
                for form, seed, sname, mname, e1, e2 in records:
                    if form in h:
                        print("   ->", form, "| seed", seed, "|", sname, mname, (e1, e2))
            if not hits:
                print(f"[{label} {name}] NO MATCH")

if __name__ == "__main__":
    main(gen_only="--gen-only" in sys.argv[1:])