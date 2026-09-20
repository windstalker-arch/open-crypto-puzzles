#!/usr/bin/env python3
"""ASL (JonathanReyess/asl-alphabet) faithful family.

Repo is a standard ML project (CNN+LSTM ASL letter recognition; data = plain A-Y image
folders + J/Z motion npy; 2025-08-18 eval logs). No puzzle content embedded. The thematic
tie to the crux is that ASL fingerspelling IS an "interpreter alphabet": a fixed 26-letter
manual alphabet, and the streams use 9 symbols over {a..i}.

Bounded faithful family:
  (a) literal ASL interpreters: the full manual alphabet string, ASL words, groupings by
      handshape family (the 9 primary handshape tokens), and their joins/cases.
  (b) ASL-family keyword ALPHABETS through the CERTIFIED keyed-28 straddling checkerboard
      (certified_vic self-cert: FUBCDORA.LETHINGKYMVPS.JQZXW + escapes 1/4 reproduces the
      3.2.2 VIC plaintext verbatim) applied to dbbib_91/faed_570 under CANON/POS digit maps
      and the {1,4},{0,4},{1,2} escape pairs - i.e. "sign language alphabet as the
      interpreter alphabet" exactly as the crux wording would predict.
"""
import json, pathlib, itertools

BASE = pathlib.Path(__file__).resolve().parents[1]
d = json.loads((BASE / "data" / "finalpage-digit-streams.json").read_text())
DBBIB = d["dbbib_91"]
FAED = d["faed_570"].rstrip("z")

CANON = {"d": 0, "b": 1, "i": 2, "f": 3, "h": 4, "c": 5, "e": 6, "g": 7, "a": 8}
POS = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9}
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed28(keyword):
    """Certified-shape 28-char keyed alphabet: dedupe(keyword+alphabet)=26 letters,
    splice '.' and '/' after cols 8 and 18 so row-major slices are 8/10/10 as the
    certified 3.2.2 grid FUBCDORA.LETHINGKYMVPS.JQZXW (build_grid slices [:8],[8:18],[18:28])."""
    kw = "".join(ch for ch in keyword.upper() if ch in ALPHA)
    keyed = ""
    for ch in kw + ALPHA:
        if ch not in keyed:
            keyed += ch
    assert len(keyed) == 26, keyed
    return keyed[:8] + "." + keyed[8:18] + "/" + keyed[18:]


from certified_vic import build_grid, decode  # certified machinery (selfcert PASS)


def dig(s, mp):
    return "".join(str(mp[c]) for c in s)


LITERALS = [
    "american sign language", "asl", "sign language", "signlanguage",
    "interpreter", "the interpreter", "theinterpreter",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz",
    "fingerspelling", "finger spelling", "manual alphabet", "the manual alphabet",
    "sign language interpreter", "signlanguageinterpreter",
]
# handshape family groups -> 9 primary ASL handshape tokens framed as a keyed alphabet keyword
HS = ["ASHT", "B", "C", "DF", "E", "GI", "JL", "K", "PQ", "RV", "UW", "XYZ",
      "base10", "abcdefghi", "sign", "hand", "palm", "deaf", "gesture", "motion",
      "static", "cnn", "lstm", "landmark", "ASL", "AmericanSignLanguage"]
KEYWORDS = HS + [w.replace(" ", "") for w in LITERALS] + ["ASLMANUAL", "SIGNLANG"]


def main():
    cands = {}
    for w in LITERALS + [k.lower() for k in KEYWORDS]:
        for form in {w, w.upper(), w.lower(), w.replace(" ", ""),
                     w.replace(" ", "").upper()}:
            cands.setdefault(form, ("literal", w))
    for kw in KEYWORDS:
        alpha = keyed28(kw)
        for stream_name, stream in (("dbbib_91", DBBIB), ("faed_570", FAED)):
            for mpn, mp in (("canon", CANON), ("pos", POS)):
                ds = dig(stream, mp)
                for e1, e2 in [(1, 4), (0, 4), (1, 2)]:
                    ctol = build_grid(alpha, e1, e2)
                    dec = decode(ds, ctol, e1, e2)
                    for form in {dec, dec.lower(), dec[::-1]}:
                        cands.setdefault(form, ("keyed28", kw, stream_name, mpn, e1, e2))
    uniq = [(k, v) for k, v in cands.items() if k]
    with open("/data/data/com.termux/files/usr/tmp/opencode/asl_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/asl_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()