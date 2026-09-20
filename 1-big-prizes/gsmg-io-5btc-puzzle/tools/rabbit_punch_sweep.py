#!/usr/bin/env python3
"""Rabbit-punch family  -  "rabbit punch" (an illegal boxing blow to the back
of the neck). Steer continues the puzzle's rabbit-theme idiom sequence
(white rabbit -> out of a hat -> caught in the headlights -> punch). grep:
0 hits for rabbit punch / sucker punch / punch / neck blow / back of the
neck / prizefight / haymaker / uppercut / jab / knockout / feint.

Bounded faithful family:
  (a) boxing / rabbit-punch vocabulary literals (case/join variants)
  (b) the same keywords as interpreter alphabets through the CERTIFIED
      keyed-28 checkerboard (certified_vic SELFCERT 3.2.2 PASS) over
      dbbib_91/faed_570 (CANON/POS maps, {1,4},{0,4},{1,2} escapes).
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
    # the steer
    "rabbit punch",
    "the rabbit punch",
    "a rabbit punch",
    "rabbit-punch",
    "rabbit punch to the neck",
    "rabbit punch on the neck",
    "rabbit punch behind the neck",
    "punch the rabbit",
    "rabbit punched",
    "punched the rabbit",
    # boxing vocabulary
    "punch",
    "a punch",
    "the punch",
    "sucker punch",
    "the sucker punch",
    "haymaker",
    "the haymaker",
    "uppercut",
    "the uppercut",
    "jab",
    "cross",
    "right hook",
    "left hook",
    "hook",
    "one two",
    "the jolt",
    "jolt",
    "knockout",
    "the knockout",
    "ko",
    "knocked out",
    "fell to the canvas",
    "the blow",
    "blow",
    "a blow",
    "the strike",
    "strike",
    "he strikes",
    "feint",
    "the feint",
    "counterpunch",
    "counter",
    "break",
    "break move",
    "break the rabbit",
    "the rabbits guard",
    "guard down",
    "dropped guard",
    "illegal blow",
    "the illegal blow",
    "blow to the back of the neck",
    "back of the neck",
    "the neck",
    "nape",
    "nape of the neck",
    "neck strike",
    "strike to the neck",
    # boxing canon
    "boxing",
    "boxer",
    "the boxer",
    "prizefight",
    "prizefighter",
    "fighting",
    "fight",
    "the fight",
    "match",
    "the match",
    "round",
    "the round",
    "bell",
    "the bell",
    "ring",
    "the ring",
    "boxing ring",
    "the boxing ring",
    "gloves",
    "the gloves",
    "boxing gloves",
    "the contender",
    "contender",
    "rocky",
    "marvis frazier",
    "fight night",
    "fight the rabbit",
    "the fight the rabbit",
    "pull your punches",
    "pull your punch",
    "rabbit punches",
    # tied wording: "rabbits" = professional boxing synonym for fighters
    "a rabbit",
    "the rabbits",
    "rabbits punch",
    "rabbits fight",
]

KEYWORDS = [
    "RABBITPUNCH", "THERABBITPUNCH", "PUNCH", "PUNCHES", "PUNCHED",
    "SUCKERPUNCH", "HAYMAKER", "UPPERCUT", "JAB", "CROSS", "HOOK",
    "RIGHTHOOK", "LEFTHOOK", "ONETWO", "JOLT", "KNOCKOUT", "KO",
    "KNOCKEDOUT", "THEBLOW", "BLOW", "STRIKE", "STRIKER", "STRIKES",
    "FEINT", "COUNTERPUNCH", "COUNTER", "BREAK", "GUARD", "GUARDDOWN",
    "ILLEGALBLOW", "BACKOFTHENECK", "THERABBIT", "NECK", "NAPE",
    "NAPEOFTHENECK", "NECKSTRIKE", "BOXING", "BOXER", "THEBOXER",
    "PRIZEFIGHT", "PRIZEFIGHTER", "FIGHT", "BOXINGRING", "THEFIGHT",
    "THATCHER", "ROUND", "BRASS", "CONTENDER", "GLOVES", "BOXINGGLOVES",
    "THERING", "RING", "PULLYOURPUNCHES", "ROCKY", "THECONTENDER",
    "RABBITSFIGHT", "AMATEUR", "DIVISION", "WEIGHT", "WELTERWEIGHT",
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
    with open("/data/data/com.termux/files/usr/tmp/opencode/rabbit_punch_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/rabbit_punch_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()