#!/usr/bin/env python3
"""sticker_color_vic_sweep.py -- the SalPhaseIon sticker-strip COLOR ORDER as keyed-28
vowel-ish alphabet keywords over dbbib(91)/faed(570), certified VIC decoder, both gates.

STREAM CORRECTION (2026-09-19): the dbbib textarea on the archived live page holds 91
letters; both Wayback captures (2023-06-01 and 2026-04-05, HTTP 200) reproduce the
91-token stream `dbbib_91` byte-for-byte and the binary runs [91:195]="matrixsumlist",
[959:999]="enter", z-segments and faed(570) identically. The 69-token `dbbib` field is a
shallow-OCR crop that dropped chars [44:66]; every 69-stream decode is void and every
'??_vic69_*' artifact is superseded. This tool therefore reads the AUTHORITATIVE 91-token
form d["dbbib_91"] (same stream certified_vic.py already uses).

Genuinely-new cell vs the recorded rows:
- late-83/84/86/86b/90/93: the strip's color ORDER was oracle-fed only as raw LITERAL
  strings (class-run concat, hex ladders, RGB tuples, binary) -- never as KEYED-ALPHABET
  KEYWORDS for the certified straddling-checkerboard decoder.
- sticker_kw_alphabet_sweep / sticker_kw_freeinterp / sticker_phrase_vic_sweep: used the
  /theseedisplanted sticker FRAGMENT words / reassembled sentences as keywords; the
  SalPhaseIon page's own color strips (bottom 13 tiles RbRRbbRbRRORR, second 8 tiles
  bbbRRbRR) were never used as the alphabet-source words.

Families (bounded, all derived from the pixel-certified class runs):
  F1 letter-fold keywords: bottom/second/both in {raw, lower, upper, b->B fold, deep-blue
     as "deepblue"/"blue", black as "black", orange as "orange/amber/red"}
  F2 color-word keywords: each tile -> its color NAME word, joined in strip order and
     reversed, with O handled as {orange, red, escape(gap)}:
       bottom: RbRRbbRbRRORR  -> red+black+red+red+black+black+red+black+red+red+O+red+red
       second: bbbRRbRR       -> black+black+black+red+red+black+red+red
  F3 binary/digit keywords: R=1,b=0,O={gap,2,escape}, read as bit-string words and as
     decimal strings of runs.
  F4 cross-joins: bottom+second, second+bottom, interleaved, and both bands with the
     matrixsumlist/enter page tokens fused (13-token bottom / 8-token second lengths).
  F5 the "21-color ladder": 13+8 = 21 tiles treated as the row0..row2 letter ORDER source
     (the checkerboard row0 needs 8 letters: second band bbbRRbRR; rows 1-2 from bottom).

Example output: for each keyword seed, keyed28 -> certified build_grid/decode over
dbbib(69)/faed(570) x {CANON,POS} x escape pairs (1,4) + followed-by-all; clean (?-free)
decodes -> raw/lower/upper/reversed -> both funded-gate oracles (tools/oracle.py attempt,
oracle_dualite.py attempt), and the literal keyword words themselves also direct-fed.

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
OUT = os.path.join(OGDIR, "tmp", "sticker_color_vic91_cands.txt")
OUT_LIT = os.path.join(OGDIR, "tmp", "sticker_color_vic91_literals.txt")

# Pixel-certified strip class runs (analysis/sticker_bands_color.txt, two-pass identical)
BOTTOM = "RbRRbbRbRRORR"   # 13 tiles L->R
SECOND = "bbbRRbRR"        # 8 tiles L->R

def ntiles(s):
    return len(s)

def keyed28(seed):
    kw = "".join(ch for ch in seed.upper() if ch in ALPHA)
    keyed = ""
    for ch in kw + ALPHA:
        if ch not in keyed:
            keyed += ch
    return (keyed + "./")[:28]

def to_digits(stream, mp):
    return "".join(str(mp[c]) for c in stream if c in mp)

# ---------- F1 letter-fold keywords ----------
def f1():
    out = set()
    for band in (BOTTOM, SECOND):
        up = band.upper()                    # RBRRBBRBRRORR / BBBRRBRR
        lo = band.lower()
        bB = band.replace("b", "B")          # deep-blue folded to B
        out.update([band, up, lo, bB, bB.upper(), bB.lower()])
    both = BOTTOM + SECOND
    bothu = both.upper()
    out.update([both, bothu, both.lower()])
    rev = SECOND + BOTTOM
    out.update([rev, rev.upper()])
    return sorted(out)

# ---------- F2 color-word keywords ----------
def color_words(band, blue_name="black", orange_name="orange", blue_first_letter_by_word=False):
    words = []
    for ch in band:
        if ch == "R":
            words.append("red")
        elif ch == "b":
            words.append(blue_name)
        elif ch == "O":
            words.append(orange_name)
    return words

def f2():
    out = set()
    for blu in ("black", "blue", "deepblue", "darkblue"):
        for ora in ("orange", "amber", "red", "goldenorange"):
            for band in (BOTTOM, SECOND):
                w = color_words(band, blu, ora)
                joined = "".join(w)
                sp = "".join(w)
                out.update([joined, sp])
                ww = "".join(x[0] for x in w)   # first letters
                out.add(ww)
                out.add(joined[::-1])
            # combined bands, word order
            wb = color_words(BOTTOM, blu, ora) + color_words(SECOND, blu, ora)
            ws = color_words(SECOND, blu, ora) + color_words(BOTTOM, blu, ora)
            out.add("".join(wb)); out.add("".join(ws))
            out.add("".join(wb)[::-1]); out.add("".join(ws)[::-1])
    return sorted(out)

# ---------- F3 binary/digit keywords ----------
def f3():
    out = set()
    for rb, orep in [("10", "2"), ("01", "2"), ("10", "9"), ("01", "9"), ("10", ""), ("01", ""), ("10", "3"), ("01", "3")]:
        for band in (BOTTOM, SECOND, BOTTOM + SECOND, SECOND + BOTTOM):
            s = "".join("1" if c == "R" else "0" if c == "b" else orep for c in band)
            out.add(s)
            out.add(s[::-1])
    # run-length reading: lengths of contiguous same-color runs in each band
    for band in (BOTTOM, SECOND):
        runs = []
        prev = None
        for c in band:
            if c != prev:
                runs.append(1)
                prev = c
            else:
                runs[-1] += 1
        s = "".join(map(str, runs))
        out.add(s)
        out.add(s[::-1])
    return sorted(out)

# ---------- F4 cross-joins with page tokens ----------
def f4():
    out = set()
    tokens = ["matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword"]
    for band in (BOTTOM, SECOND, BOTTOM + SECOND, SECOND + BOTTOM, BOTTOM.upper(), SECOND.upper()):
        for tok in tokens:
            out.add(band + tok); out.add(tok + band)
            out.add(band.upper() + tok.upper()); out.add(tok.upper() + band.upper())
    return sorted(out)

# ---------- F5 21-ladder row0..row2 order ----------
def f5():
    out = set()
    # second band is 8 chars = row0 length; bottom 13 = rows 1-2 (10+3 etc.)
    row0 = SECOND
    rest = BOTTOM
    out.add(row0 + rest)                      # bbbRRbR RRbRRbbRbRRORR
    out.add(row0.upper() + rest.upper())
    out.add(row0 + rest[::-1])
    out.add(row0.upper() + BOTTOM.upper())
    # row0 = first 8 of bottom, rows1-2 = rest of bottom + second
    out.add(BOTTOM[:8] + BOTTOM[8:] + SECOND)
    out.add(BOTTOM[:8].upper() + BOTTOM[8:].upper() + SECOND.upper())
    out.add(BOTTOM + SECOND)
    out.add(SECOND + BOTTOM)
    return sorted(out)

def build_all():
    seeds = set()
    for fn in (f1, f2, f3, f4, f5):
        seeds.update(fn())
    prints = []
    for s in sorted(seeds):
        prints.append(s)
    return prints

def main(gen_only=False):
    seeds = build_all()
    print(f"keyword seeds: {len(seeds)}", flush=True)

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

def unfold(dec):
    out = {dec}
    out.add(dec.lower())
    out.add(dec.upper())
    out.add(dec[::-1])
    return out

if __name__ == "__main__":
    main(gen_only="--gen-only" in sys.argv[1:])