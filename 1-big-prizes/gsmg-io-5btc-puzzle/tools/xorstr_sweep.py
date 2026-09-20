#!/usr/bin/env python3
"""xorstr-faithful family: FNV-1a-over-string key schedule (xorstr key4/key8) used
as a repeating-key XOR decryptor applied to the dbbib_91 / faed_570 digit streams.

xorstr.h creates per-string keys:
    KEY4(S) = FNV1a(offset=2166136261+S, text="__TIME__", prime=16777619)
    KEY8(S) = (KEY4(2166136261+S) << 32) | KEY4(KEY4(2166136261+S))
and stores 8-byte blocks of  plaintext[i] ^ KEY((i//8) block) .
We replace "__TIME__" with each candidate keyword K and XOR the stream bytes under
three {a..i}->byte maps. This is the ONLY mechanical reading the library motivates;
a literal xorstr ciphertext cannot be the streams (they are constrained to {a..i}).
"""
import hashlib

FNV_OFFSET = 2166136261
FNV_PRIME = 16777619

DBIFHCEG_CANON = {  # #106 canonical: D=0,B=1,I=2,F=3,H=4,C=5,E=6,G=7,A=8
    "a": 8, "b": 1, "c": 5, "d": 0, "e": 6, "f": 3, "g": 7, "h": 4, "i": 2,
}
POS1 = {  # positional a=1..i=9
    "a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9,
}
POS0 = {  # positional a=0..i=8
    "a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7, "i": 8,
}
MAPS = {"canon": DBIFHCEG_CANON, "pos1": POS1, "pos0": POS0}


def key4(seed: int, text: str):
    value = seed & 0xFFFFFFFF
    for c in text:
        value = ((value ^ ord(c)) * FNV_PRIME) & 0xFFFFFFFF
    return value


def key8_blocks(seed: int, text: str, blocks: int):
    """xorstr key8: first = key4(2166136261+S), second = key4(first). One 64-bit
    key per 8-block is derived from a *different* S per call; xorstr's S increments
    per string. We reproduce the two halves literally from xorstr.hpp lines 61-67."""
    keys = []
    for b in range(blocks):
        first = key4((FNV_OFFSET + seed + b) & 0xFFFFFFFF, text)
        second = key4(first, text)
        key64 = (first << 32) | second
        keys.append(key64)
    return keys


def xor_keys_blockwise(data: bytes, keys):
    out = bytearray()
    for b in range(len(keys)):
        block = data[8 * b:8 * b + 8]
        k = keys[b].to_bytes(8, "big")
        out += bytes(x ^ y for x, y in zip(block, k))
    return bytes(out)


def xor_key_repeat(data: bytes, key: bytes):
    return bytes(x ^ key[i % len(key)] for i, x in enumerate(data))


def streams():
    import json, pathlib
    base = pathlib.Path(__file__).resolve().parents[1]
    d = json.loads((base / "data" / "finalpage-digit-streams.json").read_text())
    return d["dbbib_91"], d["faed_570"]


def to_bytes(s, mp):
    if s.endswith("z"):
        s = s[:-1]
    return bytes(mp[c] for c in s)


def emit(out: bytes):
    forms = set()
    s = out.decode("latin1")
    if "\n" not in s and "\r" not in s:
        forms.add(s)
        forms.add(s.lower())
        forms.add(out[::-1].decode("latin1"))
        forms.add(out[::-1].decode("latin1").lower())
    forms.add(out.hex())
    forms.add(out[::-1].hex())
    return forms


KEYWORDS = [
    "yourlastcommand", "matrixsumlist", "shabef", "enter", "thispassword",
    "anstoo", "lastwordsbeforearchichoice", "thearchitectschoice", "causality",
    "halfandbetterhalf", "firsthintisyourlastcommand",
    "hopeisthequintessentialhumandelusion",
    "theflowerblossomsandwiltsofthefaithfulservant",
    "blueyellowprimesmatrixsumlistlastwordsbeforearchichoiceyinyang",  # 35-char hint assembly
    "fans too", "there is no spoon", "the matrix has you",
    "follow the white rabbit", "i am the one", "the answer is women",
    "itisonlywiththeheartthatoneseesrightly",
    "whatisessentialisinvisibletotheeye",
    "seventeen", "primes", "yellowblue", "yinyang",
    "BTCSEED", "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE",
]

# trim the very long phrase to 91 chars to keep candidates sane; keep full for faed
KEYWORDS2 = [
    "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE",
]

def main():
    dbbib, faed = streams()
    cands = []
    prov = []
    for kw in KEYWORDS + KEYWORDS2:
        for mname, mp in MAPS.items():
            for name, s in (("dbbib", dbbib), ("faed", faed)):
                data = to_bytes(s, mp)
                blocks = (len(data) + 7) // 8
                keys = key8_blocks(0, kw, blocks)
                dec = xor_keys_blockwise(data, keys)
                for form in emit(dec):
                    cands.append(form)
                    prov.append(("key8-blockwise", kw, mname, name))
                # single-key repeating variant (key4 of first hash as 32-bit, cycled)
                k32 = key4(FNV_OFFSET, kw).to_bytes(4, "little")
                dec2 = xor_key_repeat(data, k32)
                for form in emit(dec2):
                    cands.append(form)
                    prov.append(("key4-repeat4", kw, mname, name))
                k64 = key8_blocks(0, kw, 1)[0].to_bytes(8, "big")
                dec3 = xor_key_repeat(data, k64)
                for form in emit(dec3):
                    cands.append(form)
                    prov.append(("key8-repeat8", kw, mname, name))
    # also reverse the keyword ('esrever' hint) and lowercase keyword
    extra = []
    for kw in ["esrever", "yourlastcommand", "matrixsumlist", "causality", "enter"]:
        extra += [kw[::-1], kw.lower()]
    for kw in extra:
        for mname, mp in MAPS.items():
            for name, s in (("dbbib", dbbib), ("faed", faed)):
                data = to_bytes(s, mp)
                blocks = (len(data) + 7) // 8
                keys = key8_blocks(0, kw, blocks)
                for form in emit(xor_keys_blockwise(data, keys)):
                    cands.append(form); prov.append(("key8-blockwise", kw, mname, name))
    uniq = []
    seen = set()
    for c, p in zip(cands, prov):
        if c not in seen:
            seen.add(c); uniq.append((c, p))
    return uniq


if __name__ == "__main__":
    u = main()
    out = "\n".join(c for c, p in u)
    with open("/data/data/com.termux/files/usr/tmp/opencode/xorstr_cands.txt", "w") as f:
        f.write(out + "\n")
    import pathlib
    with open("/data/data/com.termux/files/usr/tmp/opencode/xorstr_prov.txt", "w") as f:
        for c, p in u:
            f.write(f"{c}\t{p}\n")
    print("candidates:", len(u))