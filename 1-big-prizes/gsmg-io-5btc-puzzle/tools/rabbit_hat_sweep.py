#!/usr/bin/env python3
"""Magician's-rabbit family  -  "pull a rabbit out of a hat".

Steer: the magician idiom "pull a rabbit out of a hat"  -  follows the puzzle's
established WHITERABBIT / FOLLOWTHEWHITERABBIT keywords (already closed as
checkerboard + beaufort keys in earlier rows). The IDIOM and all conjuring
vocabulary were never tested (grep: 0 hits for "rabbit out of a hat", "pull a
rabbit", magician/magic trick/prestidigitation/sleight of hand/conjur,
prestige/top hat/hat trick/abracadabra/hocus pocus/open sesame, escape artist/
houdini).

Bounded faithful family:
  (a) idiom + magician-vocabulary literals never oracled (case/join variants)
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
    # the idiom (exact steer)
    "pull a rabbit out of a hat",
    "pull the rabbit out of the hat",
    "pull a rabbit out of the hat",
    "pull the rabbit out of a hat",
    "pulling a rabbit out of a hat",
    "rabbit out of a hat",
    "rabbit from a hat",
    "rabbit and the hat",
    "the rabbit and the hat",
    "rabbit in the hat",
    "the rabbit in the hat",
    "out of a hat",
    "out of the hat",
    "a rabbit a hat",
    "possustridigitrabits",
    # white rabbit canon with the hat splice (previously only foo without hat)
    "white rabbit",
    "follow the white rabbit",
    "follow white rabbit",
    "whiterabbit",
    "followthewhiterabbit",
    "white rabbit out of a hat",
    "rabbit hole",
    "down the rabbit hole",
    "the rabbit hole",
    "rabbit",
    "the white rabbit and the red pill",
    "alice in wonderland",
    "alice",
    "cheshire cat",
    "mad hatter",
    "the mad hatter",
    "mad hatters tea party",
    "tea party",
    "march hare",
    "the march hare",
    # conjuring vocabulary
    "magic",
    "magic trick",
    "a magic trick",
    "the magic trick",
    "magician",
    "the magician",
    "prestidigitation",
    "prestidigitator",
    "sleight of hand",
    "sleight",
    "conjurer",
    "conjuror",
    "conjuring trick",
    "conjure",
    "the prestige",
    "prestige",
    "abra cadabra",
    "abracadabra",
    "hocus pocus",
    "hocus",
    "open sesame",
    "open sail",
    "sim sala bim",
    "simsalabim",
    "alacazam",
    "alakazam",
    "avada kedavra",
    "the trick",
    "trick",
    "the hat trick",
    "hat trick",
    "top hat",
    "the top hat",
    "a top hat",
    "the hat",
    "hat",
    "magic hat",
    "the magic hat",
    # escape artist (the hat conceals)
    "the great escapist",
    "escape artist",
    "houdini",
    "hary houdini",
    "harry houdini",
    "escapology",
    "erich weiss",
    "the hand is quicker than the eye",
    "hand is quicker than the eye",
    "quicker than the eye",
    "now you see it now you dont",
    "now you see me",
    "smoke and mirrors",
    "misdirection",
    "misdirection",
]

KEYWORDS = [
    "RABBITOUTOFAHAT", "PULLARABBITOUTOFAHAT", "RABBITOUTOFTHEHAT",
    "RABBITANDTHEHAT", "RABBITFROMHAT", "OUTOFAHAT", "RABBIT", "HAT",
    "THEHAT", "TOPHAT", "RABBITHOLE", "DOWNTHERABBITHOLE", "WHITERABBIT",
    "FOLLOWTHEWHITERABBIT", "ALICE", "ALICEINWONDERLAND", "CHESHIRECAT",
    "MADHATTER", "THEMADHATTER", "MARCHHARE", "TEAPARTY", "HATTER",
    "MAGIC", "MAGICTRICK", "TRICK", "HATTRICK", "MAGICIAN", "THEMAGICIAN",
    "PRESTIDIGITATION", "PRESTIDIGITATOR", "SLEIGHTOFHAND", "SLEIGHT",
    "CONJURER", "CONJUROR", "CONJURINGTRICK", "CONJURE", "PRESTIGE",
    "THEPRESTIGE", "ABRACADABRA", "HOCUSPOCUS", "OPENSESAME", "SIMSAALA BIM",
    "SIMSALABIM", "ALACAZAM", "ALAKAZAM", "AVADAKEDAVRA", "MAGICHAT",
    "GREATESCAPIST", "ESCAPEARTIST", "HOUDINI", "HARRYHOUDINI",
    "ESCAPOLOGY", "HANDQUICKERTHANEYE", "NOWYOUSEETT", "SMOKEANDMIRRORS",
    "MISDIRECTION", "MAGICANDMIRRORS", "THEGREATESCAPE",
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
    with open("/data/data/com.termux/files/usr/tmp/opencode/rabbit_hat_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/rabbit_hat_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()