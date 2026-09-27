#!/usr/bin/env python3
"""nato_vic_sweep.py -- NATO/ICAO phonetic codeword family as (A) literal X
candidates and (B) keyed-28 checkerboard alphabet keywords over dbbib(91)/faed(570),
certified VIC decoder, both funded gates.

SOURCE REPO (user steer): https://github.com/justindmartin/NATO-ICAO-Alphabet-Translator
- A PHP class translating phrases into the NATO(ICAO) phonetic alphabet.
  Codeword list (repo spelling, from src/NATOAlphabetTranslator.php):
    Alpha, Bravo, Charlie, Delta, Echo, Foxtrot, Golf, Hotel, India, Juliet,
    Kilo, Lima, Mike, November, Oscar, Papa, Quebec, Romeo, Sierra, Tango,
    Uniform, Victor, Whiskey, X-ray, Yankee, Zulu.
- Official-gear spelling variants included: Alfa, Juliett, Xray.

WHY (genuinely-new cell vs the ledger):
- The final-page streams are over {a..i} plus o=17/z separators: a..i map onto the
  NATO codewords Alpha..India, o onto Oscar (== digit 0 homophone, matching the
  certified z-segment interpreter o->0 reading), z onto Zulu. All prior alphabet
  sweeps used puzzle-vocabulary keywords; the NATO codeword family (nor any
  phrase->codeword translation) has never been a seed source (tested.md has no row
  for it; section 71 is phonetic/homophone JOKES reads, a different mechanism).
- The recent sessions closed color-order (late-201/204), sticker-fragment
  (late-205) and check/chess (late-206) keyword families; the interpreter-alphabet
  crux under lead 0 is unchanged.
- Repo purpose is translating phrases to codewords: so the most direct application
  is (A) translating the puzzle's own known phrases (decoded instructions, stage
  answers, page wording) into codeword strings and testing those as password X on
  the small-blob oracle AND the dualite oracle, and (B) using the codeword strings
  as keyed-28 VIC alphabets over dbbib_91/faed_570 exactly as the sticker battery.

Mechanics are identical to tools/sticker_color_vic_sweep.py (late-201/204 pattern):
keyed28(seed) -> dedupe+alpha to 26, append './' -> build_grid/decode (certified
3.2.2 decode logic) x {dbbib91, faed570} x {CANON, POS} x 90 escape pairs; clean
(?-free, len>=8) decodes -> {raw, lower, upper, reverse}; both funded-gate oracles.

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
OUT = os.path.join(OGDIR, "tmp", "nato_vic_cands.txt")
OUT_LIT = os.path.join(OGDIR, "tmp", "nato_vic_literals.txt")

# ---- canonical codewords (official-ICAO spelling and the repo spelling) ----
NATO_OFF = {
    "a": "Alfa", "b": "Bravo", "c": "Charlie", "d": "Delta", "e": "Echo",
    "f": "Foxtrot", "g": "Golf", "h": "Hotel", "i": "India", "j": "Juliett",
    "k": "Kilo", "l": "Lima", "m": "Mike", "n": "November", "o": "Oscar",
    "p": "Papa", "q": "Quebec", "r": "Romeo", "s": "Sierra", "t": "Tango",
    "u": "Uniform", "v": "Victor", "w": "Whiskey", "x": "Xray",
    "y": "Yankee", "z": "Zulu",
}
NATO_REPO = {
    "a": "Alpha", "b": "Bravo", "c": "Charlie", "d": "Delta", "e": "Echo",
    "f": "Foxtrot", "g": "Golf", "h": "Hotel", "i": "India", "j": "Juliet",
    "k": "Kilo", "l": "Lima", "m": "Mike", "n": "November", "o": "Oscar",
    "p": "Papa", "q": "Quebec", "r": "Romeo", "s": "Sierra", "t": "Tango",
    "u": "Uniform", "v": "Victor", "w": "Whiskey", "x": "Xray",
    "y": "Yankee", "z": "Zulu",
}

# Every letter that appears in any phrase/stream alphabet we translate
ALL_LETTERS = sorted(set(NATO_OFF))

# ---- phrases whose NATO translation is a candidate X / keyword ----
# decoded page tokens, stage answers, assembled passwords, page wording
PHRASES = [
    "matrixsumlist",
    "enter",
    "enterthispassword",
    "enterthekey",
    "enterthekeys",
    "lastwordsbeforearchichoice",
    "thispassword",
    "enterlastwordsbeforearchichoicethispassword",
    "matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist",
    "ourfirsthintisyourlastcommand",
    "yourfirsthintisyourlastcommand",
    "shabef",
    "anstoo",
    "shabefanstoo",
    "shabefourfirsthintisyourlastcommand",
    "whiterabbit",
    "followthewhiterabbit",
    "theseedisplanted",
    "theseedisplanted",
    "hopeisthequintessentialhumandelusion",
    "causality",
    "halfandbetterhalf",
    "theprivatekeysbelongtohalfandbetterhalf",
    "yinyang",
    "thearchitectschoice",
    "salphaseion",
    "cosmicduality",
    "whiterabbitnostalgicalicechildhood",
    "nostalgicalicechildhood",
    "yellowblueprimes",
    "faed",
    "dbbib",
    "dbbibfaed",
    "matrixsumlistenter",
    "ourfirsthint"
]

def translate(phrase, tbl=NATO_OFF):
    return "".join(tbl.get(ch, ch) for ch in phrase if ch.isalpha() and ch in tbl)

def f_literal_seeds():
    """Literal NATO-family strings: phrase translations + codeword joins + specials."""
    out = set()
    # (A1) phrase -> codeword translations in every join/case
    for ph in PHRASES:
        # concat, dash, space, title-case, lower, upper for both spellings
        for tblname, tbl in (("off", NATO_OFF), ("repo", NATO_REPO)):
            t = translate(ph, tbl)
            ins = [("", ""), ("-", "-"), (" ", " ")]
            for sep, joiner in ins:
                words = [tbl[ch] for ch in ph if ch.isalpha() and ch in tbl]
                joined = joiner.join(words)
                out.add(joined)
                out.add(joined.lower())
                out.add(joined.upper())
                out.add(joined.title())
                out.add(joined[::-1])
            out.add(t)
            out.add(t.lower())
            out.add(t.upper())
    # (A2) codeword-stream of the digits: NATO words of the full a..z alphabet
    for tblname, tbl in (("off", NATO_OFF), ("repo", NATO_REPO)):
        ai = "".join(tbl[c] for c in "abcdefghi")
        aio = "".join(tbl[c] for c in "abcdefghio")
        az = "".join(tbl[c] for c in ALL_LETTERS)
        for s in (ai, aio, az):
            for v in (s, s.lower(), s.upper(), s[::-1], s.title()):
                out.add(v)
            # dash-joined
            dash = "-".join(tbl[c] for c in "abcdefghi")
            out.add(dash); out.add(dash.lower()); out.add(dash.upper())
        # o=0 Oscar tie-in
        out.add(tbl["o"]); out.add(tbl["o"].lower()); out.add(tbl["o"].upper())
        out.add(tbl["z"]); out.add(tbl["z"].upper())
    # (A3) dbbib/faed headers translated letter-by-letter
    for hdr in ("dbbib", "faed"):
        for tblname, tbl in (("off", NATO_OFF), ("repo", NATO_REPO)):
            t = "".join(tbl[c] for c in hdr)
            words = [tbl[c] for c in hdr]
            joined = "".join(words)
            for v in (t, joined, joined.lower(), joined.upper(), joined[::-1]):
                out.add(v)
            dash = " ".join(words)
            out.add(dash); out.add(dash.upper())
    # (A4) specials
    for sp in ("nato", "NATO", "natoalphabet", "natophonetic", "icao", "icaophonetic",
               "phoneticalphabet", "phonetic", "bravo", "alfabravocharlie",
               "alfabravocharliedeltaechofoxtrotgolfhotelindia",
               "alphabravocharliedeltaechofoxtrotgolfhotelindia",
               "oscar", "zulu", "whiskey", "yankee", "foxtrot", "golffoxtrot"):
        out.add(sp)
    # (A5) cross-joins with page tokens (F4 style)
    for base in ("alfabravocharliedeltaechofoxtrotgolfhotelindia",
                 "alphabravocharliedeltaechofoxtrotgolfhotelindia",
                 "nato", "natoalphabet", "phoneticalphabet"):
        for tok in ("matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword"):
            for bt, tt in ((base, tok), (base.upper(), tok.upper()), (base, tok.upper())):
                out.add(bt + tt); out.add(tt + bt)
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
    out = {dec, dec.lower(), dec.upper(), dec[::-1]}
    return out

def main(gen_only=False):
    seeds = f_literal_seeds()
    print(f"seed count: {len(seeds)}", flush=True)

    alphab = []
    seen = set()
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

    cands = set()
    records = []
    for seed, a in alphab:
        for sname, stream in streams.items():
            for mname, mp in maps.items():
                digits = to_digits(stream, mp)
                for (e1, e2) in escape_pairs:
                    ctol = build_grid(a, e1, e2)
                    dec = decode(digits, ctol, e1, e2)
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