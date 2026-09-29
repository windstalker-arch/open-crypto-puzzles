#!/usr/bin/env python3
"""Lead 0 reframe: faed(570)/dbbib(91) as classical payload, not AES password.

Closes the ONE gap in the prior certified-checkerboard battery (tested.md:4711):
that sweep gave the checkerboard to 15 alphabets but NOT the certified FUBCDORA
board, and only ever used faed as payload with dbbib as VIC key. Here we decode
the streams themselves under the certified board, plus the exact-grid readings
that 91 = 7x13 and 570 = 15x38 imply, plus Beaufort under the 7 page tokens.
"""
from __future__ import annotations

import itertools
import json
import os
import re
import string
import sys
from collections import Counter
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())

DBBIB = d["dbbib_91"]   # authoritative 91-token object; d["dbbib"] is the
                        # superseded 69-token OCR crop (BUG-2 class, see tested.md)
FAED = d["faed_570"].rstrip("z")

CANON = {"d": 0, "b": 1, "i": 2, "f": 3, "h": 4, "c": 5, "e": 6, "g": 7, "a": 8}
POS = {c: i for i, c in enumerate("abcdefghi")}
ALPHA = string.ascii_uppercase

CERT_ALPHAS = {
    "FUBCDORA.LETHINGKYMVPS.JQZXW": "certified 3.2.2",
    "DBIFHCEG.ALMONQKRSUVWXYZ.TPJF": "bifid-dbifhceg-shape",
    "ABCDEFGHI.JKLMNOPQRSTUVWXYZ.": "trivial 28",
}

KEYWORDS = {
    "matrixsumlist", "matrix", "sumlist", "enter", "lastwords", "before",
    "archichoice", "archi", "thispassword", "password", "yinyang", "yang",
    "salphaseion", "cosmic", "duality", "primes", "yellow", "blue", "half",
    "betterhalf", "privatekey", "intertwined", "bruteforce", "incaseyou",
    "managed", "crack", "belong", "congratulations", "appearances", "deceive",
    "sixteen", "twentythree", "seven", "key", "vvic", "vic", "giveaway",
    "eyes", "seed", "planted", "white", "rabbit", "thinking", "triangular",
    "start", "thekey", "ourfirsthint", "lastcommand",
}

E_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ ."

def trans_digit(s, mp):
    return "".join(str(mp[c]) for c in s)

def build_grid(alpha28, e1, e2):
    row0, row1, row2 = alpha28[:8], alpha28[8:18], alpha28[18:28]
    ctol = {}
    non = [dd for dd in range(10) if dd not in (e1, e2)]
    for ch, dd in zip(row0, non):
        ctol[str(dd)] = ch
    for i, ch in enumerate(row1):
        ctol[f"{e1}{i}"] = ch
    for i, ch in enumerate(row2):
        ctol[f"{e2}{i}"] = ch
    return ctol

def decode(digits, ctol, e1, e2, reversed_alphabet=False):
    out, i = [], 0
    s = digits
    while i < len(s):
        c = s[i]
        if c in (str(e1), str(e2)):
            code = s[i:i + 2]
            if code in ctol:
                out.append(ctol[code]); i += 2; continue
        if c in ctol:
            ch = ctol[c]
            out.append(E_CHARS.replace(ch, "")[0] if reversed_alphabet else ch)
            i += 1; continue
        out.append("?"); i += 1
    return "".join(out)

def columnar_transpose(s, width, key, keyorder="asc", read="col"):
    n = len(s)
    rows = [s[i:i + width] for i in range(0, n, width)]
    nrows = len(rows)
    pad = width * nrows - n
    cols = [[(r[c] if c < len(r) else "") for r in rows] for c in range(width)]
    order = sorted(range(width), key=lambda c: (key[c], c), reverse=(keyorder == "desc"))
    if read == "col":
        return "".join("".join(cols[c]) for c in order)
    order2 = sorted(range(width), key=lambda c: (key[c], c))
    pos_of = {c: i for i, c in enumerate(order2)}
    out = ["?"] * n
    idx = 0
    for c in order2:
        for r in range(nrows):
            if c < len(rows[r]):
                out[r * width + c] = s[idx]
                idx += 1
    return "".join(out) if idx == n else "".join(out)

def vigenere_math(text, key, mode):
    out = []
    for i, ch in enumerate(text):
        if ch not in E_CHARS:
            out.append(ch); continue
        k = E_CHARS.index(key[i % len(key)])
        p = E_CHARS.index(ch)
        if mode == "beaufort":
            out.append(E_CHARS[(k - p) % len(E_CHARS)])
        elif mode == "vigenere":
            out.append(E_CHARS[(p - k) % len(E_CHARS)])
        elif mode == "decbeaufort":
            out.append(E_CHARS[(p - k) % len(E_CHARS)])
    return "".join(out)

def freq_score(text):
    letters = [c for c in text if c in ALPHA]
    if not letters:
        return -1e9
    ioc = 0.0
    n = len(letters)
    if n > 1:
        cc = Counter(letters)
        ioc = sum(v * (v - 1) for v in cc.values()) / (n * (n - 1))
    en = sum(letters.count(c) for c in "ETAOIN SHRDLU".replace(" ", "")) / n
    return ioc + 0.15 * en

def keyword_hit(text):
    return [k for k in KEYWORDS if k in text.lower()]

def report(tag, text):
    clean = re.sub(r"[^A-Z ]", "", text)
    if freq_score(clean) > 0.045:
        hits = keyword_hit(text)
        print(f"[{tag}] freq={freq_score(clean):.3f} kw={hits or '-'}")
        print("   ", text[:160])

def main():
    pws = ["matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
           "matrixsumlist", "salphaselon", "cosmicduality", "yinyang", "primes"]
    best = []
    streams = {"dbbib(91)": DBBIB, "faed(rstrip)": FAED}

    # --- A: straight checkerboard under certified board (the gap) ---
    for name, raw in streams.items():
        for mname, mp in (("canon", CANON), ("pos", POS)):
            ds = trans_digit(raw, mp)
            for alpha, aname in CERT_ALPHAS.items():
                for e1, e2 in [(1, 4), (4, 1), (2, 5), (5, 2)]:
                    ctol = build_grid(alpha, e1, e2)
                    for rev in (False, True):
                        t = decode(ds, ctol, e1, e2, reversed_alphabet=rev)
                        f = freq_score(re.sub(r"[^A-Z ]", "", t))
                        kw = keyword_hit(t)
                        if f > 0.05 or kw:
                            best.append((f, f"A-{name}-{mname}-{aname}-e{e1}{e2}-rev{int(rev)}", t))
                            report(f"A {name} {mname} {aname[:8]} e{e1}{e2} rev{int(rev)}", t)

    # --- B: exact-grid columnar transpose then checkerboard ---
    # 91 = 7x13 (key matrixsumlist, len 13); 570 = 15x38 (key lastwords..+thispassword, len 38)
    CANONZ = dict(CANON, **{"z": 9})
    POSZ = dict(POS, **{"z": 9})
    grids = [(DBBIB, 13, "matrixsumlist", "b-dbbi"),
             (d["faed_570"], 38, "lastwordsbeforearchichoicethispassword", "b-faed")]  # full 570 incl z
    for raw, width, key, tag in grids:
        for keyorder in ("asc", "desc"):
            for mname, mp in (("canon", CANONZ), ("pos", POSZ)):
                t = columnar_transpose(raw, width, key, keyorder=keyorder, read="col")
                for alpha, aname in CERT_ALPHAS.items():
                    for e1, e2 in [(1, 4), (2, 5)]:
                        ctol = build_grid(alpha, e1, e2)
                        t2 = decode("".join(str(mp[c]) for c in t), ctol, e1, e2)
                        f = freq_score(re.sub(r"[^A-Z ]", "", t2))
                        kw = keyword_hit(t2)
                        if f > 0.05 or kw:
                            best.append((f, f"{tag}-{keyorder}-{mname}-{aname[:8]}-e{e1}{e2}", t2))
                            report(f"{tag} trans{width} {keyorder} {mname} {aname[:8]} e{e1}{e2}", t2)

    # --- C: matrix sum-list readings -> candidate lettersets, then Beaufort with page pwds ---
    for name, raw, width in (("dbbib", DBBIB, 13), ("faed", FAED, 38)):
        nrows = len(raw) // width
        grid = [raw[r * width:(r + 1) * width] for r in range(nrows)]
        for mname, mp in (("canon", CANON), ("pos", POS)):
            g = [[mp[c] for c in row] for row in grid]
            rs = [sum(r) for r in g]
            cs = [sum(g[r][c] for r in range(nrows)) for c in range(width)]
            diags = [sum(g[r][r] for r in range(min(nrows, width)))]
            variants = {
                "rs": rs, "cs": cs, "rs+cs": [a + b for a, b in zip(rs, cs)],
                "rsxcs": [a * b for a, b in zip(rs, cs)],
                "isect": [g[r][c] for r in range(min(nrows, width)) for c in range(min(nrows, width))],
            }
            for vname, vals in variants.items():
                for base in (0, 1):
                    dl = "".join(str((v + base) % 10) for v in vals)
                    for alpha, aname in CERT_ALPHAS.items():
                        for e1, e2 in [(1, 4)]:
                            ctol = build_grid(alpha, e1, e2)
                            t = decode(dl, ctol, e1, e2)
                            f = freq_score(re.sub(r"[^A-Z ]", "", t))
                            if f > 0.05:
                                best.append((f, f"C-{name}-{vname}-b{base}", t))
                                report(f"C {name} {vname} +{base}", t)

    # --- D: map to 9 letters (cert alpha[:9]) then Beaufort/Vigenere under the 7 tokens ---
    nine = {"cert9": "FUBCDORA.", "abc9": "ABCDEFGHI", "dbif9": "DBIFHCEG."}
    for name, raw in streams.items():
        for nm, n9 in nine.items():
            text = "".join(n9[POS[c]] if c in POS else "" for c in raw)
            for pw in pws:
                ku = "".join(ch for ch in pw.upper() if ch in E_CHARS)
                for mode in ("beaufort", "vigenere"):
                    t = vigenere_math(text, ku, mode)
                    f = freq_score(re.sub(r"[^A-Z ]", "", t))
                    kw = keyword_hit(t)
                    if f > 0.05 or kw:
                        best.append((f, f"D-{name}-{nm}-{mode}-{pw[:10]}", t))
                        report(f"D {name} {nm} {mode} {pw}", t)

    # --- E: 2-digit pair reading as base-9 values into 28-alphabet / A-Z ---
    PAIRS = [("cert", "FUBCDORA.LETHINGKYMVPS.JQZXW"), ("abc", "ABCDEFGHIJKLMNOPQRSTUVWXYZ")]

    def pairread(s, alphabet, mod, rev=False):
        s2 = s[::-1] if rev else s
        out = []
        for i in range(0, len(s2) - 1, 2):
            v = int(s2[i]) * 9 + int(s2[i + 1])
            out.append(alphabet[v % mod])
        return "".join(out)

    for name, raw in streams.items():
        for mname, mp in (("canon", CANON), ("pos", POS)):
            ds = "".join(str(mp[c]) for c in raw)
            for aname, alpha in PAIRS:
                for mod in {min(m, len(alpha)) for m in (len(alpha), 26, 28)}:
                    for rev in (False, True):
                        t = pairread(ds, alpha, mod, rev)
                        f = freq_score(re.sub(r"[^A-Z ]", "", t))
                        kw = keyword_hit(t)
                        if f > 0.06 or kw:
                            best.append((f, f"E-{name}-{mname}-{aname}-m{mod}-rev{int(rev)}", t))
                            report(f"E {name} {mname} {aname} mod{mod} rev{int(rev)}", t)

    best.sort(key=lambda x: -x[0])
    print("\n=== TOP DECODES BY ENGLISH-LIKE SCORE ===")
    for f, tag, t in best[:15]:
        print(f"{f:.3f}  {tag}")
        print("   ", t[:200])
    print(f"candidates>0.05: {len(best)}")

    if len(sys.argv) > 2 and sys.argv[1] == "--emit":
        with open(sys.argv[2], "w") as fh:
            for _f, _tag, t in best:
                fh.write(t + "\n")
        print(f"wrote {len(best)} candidates to {sys.argv[2]}")

if __name__ == "__main__":
    main()