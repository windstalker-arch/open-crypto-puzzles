#!/usr/bin/env python3
"""Architect (The Matrix Reloaded) two-doors / function-of-the-One family.

User steers (three messages, same scene):
  S1: "there are two doors, the door to your right leads to the source and the
      salvation of Zion"
  S2: "the function of the One is now to return to the source allowing a
      temporary dissemination of the code you carry reinserting the prime
      program, after which you will be required to select from the matrix 23
      individuals, 16 female 7 male, to rebuild Zion"
  S3: "failure to comply with this process will result in a cataclysmic system
      crash"

Distinct from prior Matrix rows: row 42 (2016-08-27, ledgers lines ~1059-1071)
tested the BARE theme NOUNS (ZION, THEONE, NEO, MORPHEUS, TRINITY, "choice is
an illusion", etc.) -- 47 literals; and sec 93 tested the OTHER Architect
quote ("Hope it is the quintessential human delusion..."). This scene's
PHRASE vocabulary (two doors / right door / the source / salvation of zion /
return to the source / the code you carry / prime program / twenty-three /
rebuild zion / failure to comply / cataclysmic system crash) has NEVER been
flattened (grep: 0 hits in tested.md) and none of ZION/THEONE/ARCHITECT/SOURCE
was ever a keyed-28 alphabet.

Bounded faithful family:
  (a) dialogue phrase literals never oracled (case/join variants)
  (b) dialogue-vocabulary keywords as the interpreter alphabet through the
      CERTIFIED keyed-28 checkerboard (certified_vic SELFCERT 3.2.2 PASS) over
      dbbib_91 / faed_570 (CANON/POS maps, {1,4},{0,4},{1,2} escapes) exactly
      as the crux wording "the streams could be a perm over something DERIVED
      from them" / "interpreter alphabet" would predict.
"""
import json, pathlib

BASE = pathlib.Path(__file__).resolve().parents[1]
d = json.loads((BASE / "data" / "finalpage-digit-streams.json").read_text())
DBBIB = d["dbbib_91"]
FAED = d["faed_570"].rstrip("z")

CANON = {"d": 0, "b": 1, "i": 2, "f": 3, "h": 4, "c": 5, "e": 6, "g": 7, "a": 8}
POS = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9}
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed28(keyword):
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
    # S1 two-doors scene
    "there are two doors",
    "two doors",
    "the two doors",
    "the door to your right",
    "the door to my right",
    "door to your right",
    "door to my right",
    "your right",
    "the right door",
    "right door",
    "the door on your right",
    "the source",
    "the source and the salvation of zion",
    "the salvation of zion",
    "salvation of zion",
    "salvation",
    "leads to the source",
    "leads to the source and the salvation of zion",
    "the door to your left",
    "door to your left",
    "the left door",
    "left door",
    # S2 function-of-the-One process
    "the function of the one",
    "function of the one",
    "function of the one is now to return to the source",
    "return to the source",
    "returning to the source",
    "temporary dissemination of the code you carry",
    "dissemination of the code you carry",
    "temporary dissemination",
    "dissemination",
    "the code you carry",
    "code you carry",
    "carry the code",
    "reinserting the prime program",
    "reinsert the prime program",
    "the prime program",
    "prime program",
    "prime program reinserted",
    "twenty three individuals",
    "twenty three",
    "twenty third",
    "16 female 7 male",
    "sixteen female seven male",
    "sixteen female",
    "seven male",
    "select from the matrix",
    "selection from the matrix",
    "the matrix twenty three individuals",
    "rebuild zion",
    "to rebuild zion",
    "rebuilding zion",
    "rebuild",
    # S3 compliance/process line
    "failure to comply",
    "failure to comply with this process",
    "comply with this process",
    "this process",
    "the process",
    "failure to comply with this process will result in a cataclysmic system crash",
    "cataclysmic system crash",
    "cataclysmic",
    "system crash",
    "a cataclysmic system crash",
    # speakers / scene
    "the architect", "architect",
    "choice is an illusion",  # row-42 noun tag link
    "the one", "theone",
]

# phrase keywords as interpreter alphabets (keyed-28); none previously keyed-28
KEYWORDS = [
    "THESOURCE", "SOURCE", "THESOURCEANDSALVATIONOFZION",
    "TWODOORS", "THEREARETWODOORS", "THETWODOORS", "TWO DOORS",
    "RIGHTDOOR", "THEDOORTOYOURRIGHT", "DOORTOYOURRIGHT", "LEFTDOOR",
    "THEDOORTOYOURLEFT", "DOORTOYOURLEFT",
    "SALVATIONOFZION", "SALVATION", "ZION", "REBUILDZION", "REBUILD",
    "ZIONREBUILD", "THEONESOURCE", "THETONE", "THEONE", "ONE",
    "FUNCTIONOFTHEONE", "RETURNTOTHESOURCE", "DISSEMINATION",
    "THECODEYOUCARRY", "CODECARRY", "REINSERTINGTHEPRIMEPROGRAM",
    "REINSERTTHEPRIMEPROGRAM", "PRIMEPROGRAM", "PRIME", "PRIMEPROGRAMREINSERTED",
    "TWENTYTHREE", "TWENTYTHREEINDIVIDUALS", "23INDIVIDUALS",
    "SIXTEENFEMALESEVENMALE", "16FEMALE7MALE", "SIXTEENFEMALE", "SEVENMALE",
    "FEMALE", "MALE", "SELECTFROMTHEMATRIX", "MATRIX23",
    "THEARCHITECT", "ARCHITECT", "ARCH", "THEMASTERARCHITECT",
    "FAILURETOCOMPLY", "CATACLYSMICSYSTEMCRASH", "CATACLYSMIC", "SYSTEMCRASH",
    "COMPLY", "PROCESS", "THEPROCESS", "THESOURCEANDTHESALVATIONOFZION",
    "THEDOORTOYOURRIGHTLEADSTOTHESOURCE", "RIGHT", "LEFT",
]


def main():
    cands = {}
    for w in LITERALS:
        for form in {w, w.upper(), w.lower(), w.replace(" ", ""),
                     w.replace(" ", "").upper() if w else w}:
            if form:
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
                        if form:
                            cands.setdefault(form, ("keyed28", kw, stream_name, mpn, e1, e2))
    uniq = [(k, v) for k, v in cands.items()]
    with open("/data/data/com.termux/files/usr/tmp/opencode/architect_twodoors_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/architect_twodoors_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()