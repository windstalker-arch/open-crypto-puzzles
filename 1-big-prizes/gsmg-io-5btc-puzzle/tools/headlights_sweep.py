#!/usr/bin/env python3
"""Headlight-stunned-rabbit family  -  "like a rabbit caught in the headlights".

Steer: the idiom "like a rabbit caught in the headlights" (the classical form
is a DEER caught in headlights; here transposed to the rabbit theme that the
puzzle already carries via WHITERABBIT/FOLLOWTHEWHITERABBIT). The frozen/stun /
light-beam vocabulary has NEVER been tested (grep: 0 hits for headlight /
caught in the / in the headlights / deer / stunned / frozen / hypnotize /
searchlight / flashlight / spotlight / torch / beam / freeze).

Bounded faithful family:
  (a) idiom + headlight/light/lantern + freeze vocabulary literals (case/join)
  (b) the same keywords as interpreter alphabets through the CERTIFIED keyed-28
      checkerboard (certified_vic SELFCERT 3.2.2 PASS) over dbbib_91/faed_570
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
    # the idiom (exact steer + canonical deer form + rabbit transpose)
    "like a rabbit caught in the headlights",
    "a rabbit caught in the headlights",
    "rabbit caught in the headlights",
    "rabbit in the headlights",
    "a rabbit in the headlights",
    "caught in the headlights",
    "caught in the headlights like a rabbit",
    "like a deer caught in the headlights",
    "a deer caught in the headlights",
    "deer caught in the headlights",
    "deer in the headlights",
    "caught in the headlights like a deer",
    "in the headlights",
    "the headlights",
    "headlights",
    "headlight",
    "caught in the lights",
    "caught in the beam",
    "stunned",
    "stunned rabbit",
    "frozen rabbit",
    "frozen in the headlights",
    "the rabbit froze",
    "froze in the headlights",
    "paralyzed by the light",
    "paralyzed",
    "hypnotized",
    "hypnotized rabbit",
    "the rabbit is hypnotized",
    "glassy eyed",
    "glassy eyes",
    "startled",
    "petrified",
    "petrified rabbit",
    "stock still",
    "motionless",
    "unable to move",
    "frozen motionless",
    # light / lamp / lantern vocabulary (the "headlight" source)
    "headlight beam",
    "beam of light",
    "light beam",
    "the beam",
    "beam",
    "light",
    "the light",
    "bright light",
    "blinding light",
    "the light blinds",
    "spotlight",
    "the spotlight",
    "searchlight",
    "the searchlight",
    "flashlight",
    "car headlights",
    "the cars headlights",
    "headlamp",
    "lantern",
    "the lantern",
    "a lantern",
    "jack o lantern",
    "jaoca lantern",
    "torch",
    "the torch",
    "flash of light",
    "ray of light",
    "a ray of light",
    "the lamp",
    "lamp",
    "the light of day",
    "light and dark",
    "the light and the dark",
    # freeze verbs + rabbit canon splice
    "freeze",
    "froze",
    "freeze in place",
    "rabbit freeze",
    "the freeze",
    "stop",
    "stop the rabbit",
    "wait",
    "halt",
    "white rabbit frozen",
    "follow the white rabbit frozen",
    "the white rabbit stared",
    "the rabbit stared back",
    "stared into the headlights",
]

KEYWORDS = [
    "RABBITHTL", "HEADLIGHTS", "HEADLIGHT", "THEHEADLIGHTS", "CATCHINHEAD",
    "RABBITCAUGHTINTHEHEADLIGHTS", "CAUGHTINTHEHEADLIGHTS",
    "CAUGHTINTHEHEADLIGHTSLIKERABBIT", "DEERCAUGHTINTHEHEADLIGHTS",
    "DEERINTHEHEADLIGHTS", "INTHEHEADLIGHTS", "HEADLIGHTSRABBIT",
    "WHITERABBITHEADLIGHTS", "RABBITHOLDEADLIGHTS", "HADLITEM",
    "STUNNED", "STUNNEDRABBIT", "FROZEN", "FROZENRABBIT", "FROZENINTHEHEADLIGHTS",
    "RABBITFROZE", "FROZES", "PARALYZED", "PARALYZEDBYTHELIGHT", "HYPNOTIZED",
    "HYPNOTIZEDRABBIT", "GLASSYEYE", "GLASSYEYED", "STARTLED", "PETRIFIED",
    "PETRIFIEDRABBIT", "STOCKSTILL", "MOTIONLESS", "UNABLETOMOVE",
    "FROZENMOTIONLESS", "LIGHT", "THELIGHT", "BRIGHTLIGHT", "BLINDINGLIGHT",
    "BEAM", "BEAMOFLIGHT", "LIGHTBEAM", "HEADLIGHTBEAM", "THEBEAM",
    "SPOTLIGHT", "THESPOTLIGHT", "SEARCHLIGHT", "THESEARCHLIGHT", "FLASHLIGHT",
    "HEADLAMP", "LANTERN", "THELANTERN", "JACKOLANTERN", "TORCH", "THETORCH",
    "FLASHOFLIGHT", "RAYOFLIGHT", "THELAMP", "LAMP", "THEDAY", "LIGHTANDDARK",
    "LIGHTANDTHELIGHT", "THELIGHTANDTHEDARK", "FREEZE", "FROZE", "FROZEINPLACE",
    "RABBITFREEZER", "THEFREEZE", "HOUSE", "HALT", "WHITERABBITFROZEN",
    "STARE", "STARED", "RABBITSTARE", "THEEYE", "EYES", "GLAZED", "POSSUM",
    "CATATONIC", "TRANCE", "INATRANCE", "DOGED", "DRAW", "DRAWN", "STOP",
    "HALTED", "CEASE", "BLOCK", "BLOCKED", "THEBLOCK", "TRAFFIC", "CAR",
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
    with open("/data/data/com.termux/files/usr/tmp/opencode/headlights_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/headlights_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()