#!/usr/bin/env python3
"""LOTR Gandalf's counsel family  -  "only a passing thing... even darkness must
pass". Steer in the same mythos sequence (Boromir Black Gates -> Ring verse ->
Gandalf). grep: 0 hits for "passing thing" / "even darkness must pass" /
"only a passing thing" / "this shadow" in tested.md.
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
    "in the end its only a passing thing this shadow",
    "in the end it is only a passing thing this shadow",
    "its only a passing thing this shadow",
    "only a passing thing this shadow",
    "only a passing thing",
    "a passing thing",
    "passing thing",
    "even darkness must pass",
    "even darkness must pass and so must this",
    "this shadow even darkness must pass",
    "this shadow is only a passing thing",
    "the shadow is only a passing thing",
    "a new day will come",
    "when the sun shines it will shine out the clearer",
    "those were the stories that stayed with you",
    "you can not pass",
    "you shall not pass",
    "gandalf the grey",
    "gandalf the white",
    "mirkwood",
    "lothlorien",
    "galadriel",
    "the shadow",
    "shadow",
    "passing",
    "pass",
    "darkness",
    "must pass",
    "ill that was old shall fade away",
    "frodo lives",
    "samwise the brave",
    "the grey havens",
    "grey havens",
]

KEYWORDS = [
    "PASSINGTHING", "ONLYAPASSINGTHING", "EVENDARKNESSMUSTPASS", "EVENDARKNESS",
    "DARKNESSMUSTPASS", "PASSING", "PASS", "MUSTPASS", "THESHADOW", "SHADOW",
    "DARKNESS", "GANDALF", "GANDALFTHEGREY", "GANDALFTHEWHITE", "THEGREY",
    "NEWDAYWILLCOME", "SUNSHINES", "SHINEOUTTHECLEARER", "YOUSHANNOTPASS",
    "YOUCANNOTPASS", "THEGREYHAVENS", "GREYHAVENS", "LOTHLORIEN",
    "MIRKWOOD", "GALADRIEL", "AELEN", "IAMANDSERVIENTOFSECRETFIRE",
    "MELTERTHEDARKNESS", "THEFLAMEOFANOR", "THEFLAME", "MAGICSFIRE",
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
    with open("/data/data/com.termux/files/usr/tmp/opencode/lotr_gandalf_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/lotr_gandalf_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()