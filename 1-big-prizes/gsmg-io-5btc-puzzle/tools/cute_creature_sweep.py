#!/usr/bin/env python3
"""Cute-little-furry-creature family  -  "cute little furry creature" (rabbit
as a term of endearment / fluffy pet vocabulary). Continues the rabbit-theme
idiom sequence. grep: 0 hits for cute/furry/fluffy/bunny/adorable/creature
in tested.md.

Bounded faithful family:
  (a) endearment/little-creature vocabulary literals (case/join variants)
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
    "cute little furry creature",
    "a cute little furry creature",
    "cute little furry creature rabbit",
    "cute little furry rabbit",
    "cute little furry bunny",
    "little furry creature",
    "cute furry creature",
    "furry creature",
    "the cute little furry creature",
    "the cute little creature",
    "cute little creature",
    # bunny / pet vocabulary
    "bunny",
    "the bunny",
    "a bunny",
    "little bunny",
    "cute bunny",
    "bunny rabbit",
    "the bunny rabbit",
    "fluffy",
    "fluffy bunny",
    "fluffy rabbit",
    "cute rabbit",
    "the cute rabbit",
    "adorable",
    "adorable rabbit",
    "a cuddly rabbit",
    "cuddly",
    "cuddle bunny",
    "snuggle",
    "the snuggle bunny",
    "soft fur",
    "soft",
    "fur",
    "the fur",
    "cottontail",
    "the cottontail",
    "cottontail rabbit",
    "a doe",
    "dorable",
    "wabbit",
    "the wabbit",
    "wascally wabbit",
    "bock bock",
    "peter rabbit",
    "peter",
    "the peter rabbit",
    "bg cullen",
    "bad bunnies",
    "thumper",
    "the thumper",
    "bambi",
    "the little creature",
    "creature",
    "the creature",
    "a creature",
    "little animal",
    "a little animal",
    "kill crazy",
    # terms of endearment
    "dear",
    "my dear",
    "sweet",
    "sweet rabbit",
    "cutie",
    "cutie pie",
    "sugar",
    "honey",
    "sweety",
    "sweetie",
    "darling",
    "love",
    "lover",
    "pet",
    "the pet",
    "my pet rabbit",
    "woolly",
    "fuzzy",
    "fuzz",
    "the furball",
    "furball",
    "little one",
    "the little one",
    "small",
    "tiny",
    "tiny rabbit",
]

KEYWORDS = [
    "CUTELITTLEFURRYCREATURE", "CUTELITTLEFURRYRABBIT",
    "CUTELITTLEFURRYBUNNY", "LITTLEFURRYCREATURE", "CUTEFURRYCREATURE",
    "FURRYCREATURE", "LITTLECREATURE", "CUTELITTLECREATURE", "BUNNY",
    "THEBUNNY", "LITTLEBUNNY", "CUTEBUNNY", "BUNNYRABBIT", "THEBUNNYRABBIT",
    "FLUFFY", "FLUFFYBUNNY", "FLUFFYRABBIT", "CUTERABBIT", "THERABBIT",
    "ADORABLE", "ADORABLERABBIT", "CUDDLY", "CUDDLEBUNNY", "SNUGGLE",
    "SNUGGLEBUNNY", "SOFTFUR", "SOFT", "FUR", "THEFUR", "COTTONTAIL",
    "COTTONTAILRABBIT", "THUMPER", "THETHUMPER", "BAMBI", "PETER",
    "PETERRABBIT", "THEPETERRABBIT", "WASCALLYWABBIT", "WABBIT", "TOY",
    "CREATURE", "THECREATURE", "LITTLEANIMAL", "TINYRABBIT", "LITTLEONE",
    "THELITTLEONE", "SMALL", "TINY", "FURBALL", "WOOL", "WOOD",
    "PET", "THEPET", "SWEET", "SWEETNESS", "DARLING", "DEAR", "SWEETIE",
    "CUTIE", "CUTIEPIE", "HONEY", "SUGAR", "LOVE", "MYLOVE", "SWEETBUNNY",
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
    with open("/data/data/com.termux/files/usr/tmp/opencode/cute_creature_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/cute_creature_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()