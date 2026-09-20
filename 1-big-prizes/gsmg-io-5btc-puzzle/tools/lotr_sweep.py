#!/usr/bin/env python3
"""Lord of the Rings family  -  Boromir's Black Gates line (The Fellowship of
the Ring / Two Towers meme).

User steer (LOTR): "One does not simply walk into Mordor. Its Black Gates are
guarded by more than just Orcs."

The puzzle canon already had Matrix theme coverage (rows 42, 93-95, late-157);
the "white rabbit" keyword (whiterabbit) was an established checkerboard/
beaufort key from the MATRIX mythos. LOTR vocabulary has NEVER been tested:
grep confirms 0 hits for mordor / boromir / black gate(s) / lotr / lord of the
rings / fellowship / middle earth / "one does not simply" / "walk into mordor"
(the 44 "orc" matches in tested.md are substrings of oracle/forced/before, no
real orc content).

Bounded faithful family:
  (a) dialogue phrase literals never oracled (case/join variants)
  (b) mythos vocabulary keywords as the interpreter alphabet through the
      CERTIFIED keyed-28 checkerboard (certified_vic SELFCERT 3.2.2 PASS) over
      dbbib_91 / faed_570 (CANON/POS maps, {1,4},{0,4},{1,2} escapes) exactly
      as the crux wording would predict.
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
    # Boromir's line (exact scene)
    "one does not simply walk into mordor",
    "one does not simply walk into mordor its black gates are guarded by more than just orcs",
    "its black gates are guarded by more than just orcs",
    "its black gates are guarded by more than just orcs and madness combined",
    "black gates are guarded by more than just orcs",
    "guarded by more than just orcs",
    "more than just orcs",
    "simply walk into mordor",
    "walk into mordor",
    "one does not simply walk in",
    "one does not simply walk into",
    "you do not simply walk into mordor",
    "the black gate of mordor",
    "the black gates of mordor",
    "black gate of mordor",
    "black gates of mordor",
    "mordor",
    "the black gate",
    "the black gates",
    "black gate",
    "black gates",
    "more than orcs",
    "guarded by orcs",
    "orcs",
    "gondor",
    "boromir",
    "son of gondor",
    "the fellowship",
    "the fellowship of the ring",
    "the one ring",
    "one ring",
    "the ring",
    "ring of power",
    "the dark lord",
    "sauron",
    "the eye of sauron",
    "the eye",
    "mount doom",
    "minas morgul",
    "morgul",
    "the witch king",
    "anduins",  # gate marker twin towers (Argonath) - The Great Gate
    "the argonath",
    "argonath",
    "the great gate",
    "the great gates",
    "the hi kar",
    "east gate",
    "west gate",
    "the door of mordor",
    "entering mordor",
    "enter mordor",
]

# mythos vocabulary keywords as interpreter alphabets (keyed-28)
KEYWORDS = [
    "MORDOR", "BLACKGATE", "BLACKGATES", "BLACKGATESOFMORDOR", "BLACKGATEOFMORDOR",
    "THEBLACKGATE", "THEBLACKGATES", "THEBLACKGATESOFMORDOR", "THEBLACKGATEOFMORDOR",
    "ONEDOESNOTSIMPLYWALKINTMORDOR", "ONEDOESNOTSIMPLYWALKINTMORDOR",
    "NOTSIMPLYWALKINTMORDOR", "SIMPLYWALKINTMORDOR", "WALKINTMORDOR",
    "MORETHANJUSTORCS", "GUARDEDBYMORETHANJUSTORCS", "ORCS", "ORC",
    "BOROMIR", "GONDOR", "SONOFGONDOR", "THEFELLOWSHIP", "FELLOWSHIP",
    "FELLOWSHIPOFTHERING", "ONERING", "THEONERING", "THERING", "RINGOFPOWER",
    "SAURON", "THEDARKLORD", "DARKLORD", "THEEYEOFSAURON", "THEEYE", "EYE",
    "MOUNTDOOM", "OFTHEMOUNT", "MINASMORGUL", "MORGUL", "WITCHKING",
    "THEWITCHKING", "ARGONATH", "THEARGONATH", "GREATGATE", "THEGREATGATE",
    "GREATGATES", "THEGREATGATES", "EASTGATE", "WESTGATE", "MINAS", "TIRITH",
    "MINASTIRITH", "ISENGARD", "SARUMAN", "THEWHITEWIZARD", "RIVENDELL",
    "THEODEN", "ARAGORN", "LEGOLAS", "GIMLI", "FRODO", "GANDALF", "SAMWISE",
    "THELIGHTTHEEYE", "DARKTOWER", "BARRADUR", "DURTHANG", "DWARVES",
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
    with open("/data/data/com.termux/files/usr/tmp/opencode/lotr_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/lotr_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()