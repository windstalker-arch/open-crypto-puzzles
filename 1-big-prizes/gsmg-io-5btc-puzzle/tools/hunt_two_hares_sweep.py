#!/usr/bin/env python3
"""To-hunt-two-hares family  -  "to hunt two hares" / "if you chase two hares,
you catch neither".

Steer continues the puzzle's rabbit/hare theme idiom sequence (white rabbit /
out of a hat / headlights / rabbit punch / cute furry creature -> two hares).
This is the proverb "he who chases two hares catches neither"  -  a statement
about the puzzle's TWO funded gates / HALF AND BETTER HALF. grep: 0 hits for
"two hares" / chase two / catch neither / run after two / hunts two / proverb.

Bounded faithful family:
  (a) proverb + hare-hunting vocabulary literals (case/join variants)
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
    # exact steer
    "to hunt two hares",
    "hunt two hares",
    "hunting two hares",
    "two hares",
    "if you hunt two hares",
    "he who hunts two hares",
    "he who chases two hares",
    "when you hunt two hares",
    "you hunt two hares",
    "chase two hares",
    "chase two rabbits",
    "run after two hares",
    "if you chase two rabbits",
    "if you run after two hares",
    "catch neither",
    "you will catch neither",
    "you catch neither",
    "two hares and you catch neither",
    "he who chases two hares catches neither",
    "he who runs after two hares will catch neither",
    "he who hunts two hares will catch none",
    "hunt two hares you catch none",
    "catch none",
    "you will catch none",
    "the twin hares",
    "the two hares",
    "the two rabbits",
    "better half better catch",
    "one hare at a time",
    "hunt one hare",
    "one hare",
    "the better hare",
    "the second hare",
    "the first hare",
    # hare-vs-rabbit / leporid vocabulary
    "hare",
    "the hare",
    "a hare",
    "the hares",
    "hares",
    "a startled hare",
    "the mad march hare",
    "march hare",
    "leporid",
    "lepus",
    "lepus europaeus",
    "brown hare",
    "the brown hare",
    "jackrabbit",
    "the jackrabbit",
    "jackalope",
    "the jackalope",
    "snowshoe hare",
    "the snowshoe hare",
    "tortoise and the hare",
    "the tortoise and the hare",
    "tortoise",
    "the tortoise",
    "slow and steady wins the race",
    "slow and steady",
    "hare and tortoise",
    "the hare and the hedgehog",
    "the hedgehog",
    "hedgehog",
    # hunting vocabulary
    "hunt",
    "the hunt",
    "hunting",
    "the hunting",
    "hunter",
    "the hunter",
    "a hunter",
    "hunters",
    "the hunting dog",
    "the hounds",
    "hounds",
    "greyhound",
    "the greyhound",
    "beagle",
    "the beagle",
    "pursuers",
    "the chase",
    "chase",
    "chaser",
    "the chaser",
    "give chase",
    "in pursuit",
    "pursuit",
    "the hunter and the hunted",
    "prey",
    "the prey",
    "game",
    "the game",
    "the hunted",
    "harrier",
    "the harrier",
    "bag",
    "a brace of hares",
    "two brace of hares",
    "beat the field",
    "the field",
    "shot",
    "the shot",
    "aim",
    "the prizefight of hares",
]

KEYWORDS = [
    "TOHUNTTWOHARES", "HUNTTWOHARES", "HUNTINGTWOHARES", "TWOHARES",
    "CHASETWOHARES", "CHASETWORABBITS", "RUNAFTERTWOHARES", "CATCHNEITHER",
    "YOUCATCHNEITHER", "CATCHNONE", "HEWHOCHASESTWOHARES",
    "HEWHOHUNTSTWOHARES", "IFYOUCHASETWOHARES", "TWOHARESANDYOUCAT",
    "TWINHARES", "ONEHARE", "ONEHAREATATIME", "HARE", "THEHARE", "HARES",
    "THEHARES", "MARCHHARE", "THEMARCHHARE", "MADMARCHHARE", "TWHARE",
    "TORTOISEANDTHEHARE", "THETORTOISE", "TORTOISE", "SLOWANDSTEADY",
    "SLOWANDSTEADYWINS", "HAREANDTHETORTOISE", "HAREANDHEDGEHOG",
    "HEDGEHOG", "JACKRABBIT", "JACKALOPE", "SNOWSHOEHARE", "LEPORID",
    "LEPUS", "BROWNHAIR", "HUNT", "THEHUNT", "HUNTING", "HUNTER", "THEHUNTER",
    "HUNTERS", "HOUNDS", "GREYHOUND", "BEAGLE", "PURSUER", "THECHASE",
    "CHASE", "CHASER", "GIVECHASE", "INPURSUIT", "PURSUIT", "PREY", "THEPREY",
    "GAME", "THEGAME", "THEHUNTED", "HARRIER", "ABRACEOFHARES", "FIELD",
    "THEFIELD", "MARKSHOT", "AM", "BUCK", "DOE", "TWOPATHS", "BOTHDOORS",
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
    with open("/data/data/com.termux/files/usr/tmp/opencode/hunt_two_hares_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/hunt_two_hares_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()