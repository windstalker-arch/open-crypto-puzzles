#!/usr/bin/env python3
"""Lord of the Rings Ring-verse family  -  "One Ring to rule them all".

Steer: "one ring to rule them all" (the Ring inscription, J.R.R. Tolkien).
Complements lotr_sweep.py (Boromir Black Gates line, closed late-158).
grep confirms 0 hits in tested.md for every Ring-phrase form: "one ring to
rule them all" / "find them" / "bring them all" / "in the land of mordor" /
"where the shadows lie" / "ash nazg" / "rule them all".

Bounded faithful family:
  (a) Ring-verse phrase literals never oracled (case/join variants)
  (b) Ring-verse keyword alphabets through the CERTIFIED keyed-28 checkerboard
      (certified_vic SELFCERT 3.2.2 PASS) over dbbib_91/faed_570
      (CANON/POS maps, {1,4},{0,4},{1,2} escapes).
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
    "one ring to rule them all",
    "one ring to rule them all one ring to find them",
    "one ring to rule them all one ring to find them one ring to bring them all and in the darkness bind them",
    "one ring to bring them all",
    "one ring to find them",
    "and in the darkness bind them",
    "in the darkness bind them",
    "rule them all",
    "find them",
    "bring them all",
    "bind them",
    "the one ring to rule them all",
    "one ring to rule them all in the land of mordor where the shadows lie",
    "in the land of mordor where the shadows lie",
    "in the land of mordor",
    "where the shadows lie",
    "the land of mordor",
    "three rings for the elven kings under the sky",
    "three rings for the elven kings",
    "elven kings under the sky",
    "seven for the dwarf lords in their halls of stone",
    "seven for the dwarf lords",
    "dwarf lords in their halls of stone",
    "nine for mortal men doomed to die",
    "nine for mortal men",
    "mortal men doomed to die",
    "doomed to die",
    "one for the dark lord on his dark throne",
    "one for the dark lord",
    "on his dark throne",
    "dark throne",
    "in the land of mordor where the shadows lie",
    "ash nazg thrakatuluk agh burzum ishi krimpatul",
    "ash nazg gimbatul",
    "ash nazg thrakatuluk",
    "ash nazg",
    "nazg",
    "burzum",
    "krimpatul",
    "gimbatul",
    "thrakatuluk",
    "one ring to rule them all one ring to find them one ring to bring them all and in the darkness bind them",
    "the ring inscription",
    "ring inscription",
    "ring verse",
    "the ring verse",
    "rule",
    "the onset of the balrog",  # "the rules" homophone tie
    "isildurs bane",
    "isildur",
    "precious",
    "my precious",
    "the one ring to rule them all the one ring to find them",
]

KEYWORDS = [
    "ONERINGTORULETHEMALL", "ONERING", "THERING", "RULE", "RULETHEMALL",
    "ONERINGTON", "ONE", "TWENTYONEGIN",  # aeiou poem puzzle number plays
    "ASHNAZG", "ASHNAZGTHRAKATULUK", "ASHNAZGTHRAKATULUKAGHBURZUMISHIKRIMPATUL",
    "ASHNAZGGIMBATUL", "ASHNAZGDURBATULUK", "BURZUM", "KRIMPATUL", "GIMBATUL",
    "THRAKATULUK", "NAZGUL", "NAZG",
    "DARKNESSBINDTHEM", "BINDTHEM", "BRINGTHEMALL", "FINDTHEM",
    "THELANDOFMORDOR", "MORDOR", "LANDOFMORDOR", "SHADOWSLIE", "WHERETHESHADOWS",
    "ELVENKINGSUNDERTHESKY", "ELFENKING", "DWARFLORDS", "HALSOFSTONE",
    "HALLSOFSTONE", "MORTALMEN", "DOOMEDTODIE", "DARKTHRONE", "THEDARKLORDS",
    "THEDARKLORDSONDARKTHRON", "THREERINGS", "SEVENRINGS", "NINERINGS",
    "ONERINGTOFIND", "ONERINTORTHERULE", "RINGING", "RINGSOFPOWER",
    "DARKLORD", "SAURON", "THEEYE", "EYEOFSAURON",
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
    with open("/data/data/com.termux/files/usr/tmp/opencode/lotr_ring_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/lotr_ring_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()