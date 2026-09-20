#!/usr/bin/env python3
"""23-shift cipher family: ROT23 (= ROT-3) over every in-corpus text candidate, plus
+23 mod 9 over the {a..i} digit maps, plus certified Bifid decode outputs shifted 23.

Sections 105/60/143 closed generic ROT0..25 on the CORE objects, but the specific
shift 23 as a targeted steer over the BROAD token/tagged/decoded corpus has never been
isolated; and a {a..i}->{a..i} rotation by 23 (mod 9 = +5) applied to the raw streams
is a fresh digit-map twist absent from the fixed 9! permutation sweeps.
"""
import json, pathlib, hashlib

BASE = pathlib.Path(__file__).resolve().parents[1]
STREAMS = json.loads((BASE / "data" / "finalpage-digit-streams.json").read_text())
S = json.loads((BASE / "data" / "salphaseion-streams.json").read_text())

DBIFHCEG_CANON = {"a": 8, "b": 1, "c": 5, "d": 0, "e": 6, "f": 3, "g": 7, "h": 4, "i": 2}
POS1 = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9}
POS0 = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7, "i": 8}

A2I = "abcdefghi"


def rot23(s):
    out = []
    for ch in s:
        if 'a' <= ch <= 'z':
            out.append(chr((ord(ch) - 97 + 23) % 26 + 97))
        elif 'A' <= ch <= 'Z':
            out.append(chr((ord(ch) - 65 + 23) % 26 + 65))
        else:
            out.append(ch)
    return "".join(out)


def rot23_9alphabet(s):
    """shift each of the 9 stream symbols forward by 23 mod 9 = 5 in {a..i}."""
    return "".join(A2I[(A2I.index(c) + 23) % 9] for c in s)


def remap(s, mp):
    if s.endswith("z"):
        s = s[:-1]
    return bytes(mp[c] for c in s)


CORPUS = [
    "yourlastcommand", "secondanswer", "leavethematrix", "isolveditwithanabacus",
    "matrixsumlist", "shabef", "enter", "thispassword", "anstoo",
    "lastwordsbeforearchichoice", "thearchitectschoice", "causality",
    "halfandbetterhalf", "firsthintisyourlastcommand",
    "hopeisthequintessentialhumandelusion",
    "theflowerblossomsandwiltsofthefaithfulservant",
    "blueyellowprimesmatrixsumlistlastwordsbeforearchichoiceyinyang",
    "itisonlywiththeheartthatoneseesrightly",
    "whatisessentialisinvisibletotheeye",
    "followthewhiterabbit", "i am the one", "fans too", "entertherabbithole",
    "redpill", "there is no spoon", "happy xmas everything that has a beginning has an end",
    "from neo", "thematrixhasyou", "salphaseion", "alphanoises", "turing complete",
    "causality transcended", "#solution", "the answer is women", "halving",
    "fromn0ehalfabetterhalfbuiltitbellaciao1", "bellaciao", "n0e",
    "1gsmg1jc9wtdswfwapgj2xcmjpawx7prbe", "17ucy1k9zuaaoy6jvtm932w9jup5lxfyha",
    "btcseed", "the seed is planted", "keys belong to half and better half",
    "they also need funds to live", "open the gates", "the password",
    "followthewhiterabbitandsalphaseioncreatedthegateofthefuture",
]
DIG = ["dbbib_91", "faed_570"]


def main():
    cands = {}
    prov = []
    # (a) ROT23 of corpus text, plus upper/lower/reverse forms
    for w in CORPUS:
        r = rot23(w)
        forms = {r, r.upper(), r.lower(), rot23(w[::-1]), rot23(w[::-1]).lower(),
                 w + "23", r + "23", w.replace(" ", "") + "23",
                 ("23" + w.replace(" ", "")), ("23" + r.replace(" ", ""))}
        for f in forms:
            cands.setdefault(f, ("rot23-corpus", w))
    # (b) digit streams rotated in the 9-alphabet
    for name in DIG:
        s = STREAMS[name].rstrip("z")
        for sh in (23, 23 % 9, 23 - 9, 23 - 18, 5):  # +5 mod9; also raw +23/-4 readings
            shifted = "".join(A2I[(A2I.index(c) + sh) % 9] for c in s)
            for mpname, mp in (("canon", DBIFHCEG_CANON), ("pos1", POS1), ("pos0", POS0)):
                data = bytes(mp[c] for c in shifted)
                forms = {data.decode("latin1"), data.hex(), data[::-1].hex()}
                for f in forms:
                    cands.setdefault(f, ("9rot-shift", name, sh, mpname))
    # (c) certified Bifid outputs rotated 23
    pt = S["plaintext_head"] + S["odd_pre_reduction"]  # head + odd (reversed-ish) -> full approx
    for src_name, src in (("plaintext_head", S["plaintext_head"]),
                          ("full_570", S["plaintext_head"] + S["odd_pre_reduction"] + S["even_stream"][::-1])):
        r = rot23(src)
        for f in {r, r.lower(), r[::-1], rot23(src + "thepassword"),
                  rot23(src[::-1] + "thepassword")}:
            cands.setdefault(f, ("rot23-bifid", src_name))
    uniq = [(k, v) for k, v in cands.items() if k]
    out = "\n".join(k for k, _ in uniq)
    with open("/data/data/com.termux/files/usr/tmp/opencode/rot23_cands.txt", "w") as f:
        f.write(out + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/rot23_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()