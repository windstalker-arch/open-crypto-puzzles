#!/usr/bin/env python3
"""VIC chain-addition over-encryption battery (lead B).

For dbbib69 / dbbib91 / faed570:
  map -> digits (CANON/POS), subtract a chain-generated keystream mod m
  (m in {9,10}), undo a full-rectangle digit-level columnar de-transpose
  (width in {0,3,23}/{0,7,13}/{0,15,38}), then certified checkerboard decode
  (literal 28-char board, escapes 1,4). Order variants: subtract-then-trans
  (canonical VIC) and trans-then-subtract. Clean (?-free) decodes -> oracle
  answer-forms (raw/lower/upper/reversed).

Keystream seeds are all page-grounded: phone-keypad digits of the decoded
page tokens (matrixsumlist=6287497865478 = 13 digits, enter, thispassword,
lastwordsbeforearchichoice, shabef, shabefourfirsthintisyourlastcommand),
the 29-symbol I/O drop string, the 14x14 matrix row/col sums, the live
40-token a/b run that decodes to "enter", and the certified 3.2.2
ciphertext itself.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from certified_vic import build_grid, decode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())
DBBIB69 = d["dbbib"]
FAED = d["faed_570"].rstrip("z")
LIVE = (Path(ROOT) / "data" / "live_salphaseion.txt").read_text().split()
DBBIB91 = "".join(LIVE[:91])

ALPHA = "FUBCDORA.LETHINGKYMVPS.JQZXW"
CANON = {"d": 0, "b": 1, "i": 2, "f": 3, "h": 4, "c": 5, "e": 6, "g": 7, "a": 8}
POS = {c: i for i, c in enumerate("abcdefghi")}

PHONE = {c: dg for c, dg in zip(
    "abc defghi jkl mno pqrs tuv wxyz".replace(" ", ""),
    "22233344455566677778889999")}

CT_322 = ("151659431219724091691712137589518131415431314124281541913121812194"
          "33121171617137149110916631213131281491109166131412199114371612126021664313711154112")


def phone_digits(word):
    return [int(PHONE[c]) for c in word if c in PHONE]


def seed_set():
    abrun = [0 if c == "a" else 1 for c in LIVE[959:999]]
    seeds = {
        "matrixsumlist_phone": phone_digits("matrixsumlist"),
        "enter_phone": phone_digits("enter"),
        "thispassword_phone": phone_digits("thispassword"),
        "lastwordsbeforearchichoice_phone": phone_digits("lastwordsbeforearchichoice"),
        "shabef_phone": phone_digits("shabef"),
        "shabefourfirsthintisyourlastcommand_phone": phone_digits("shabefourfirsthintisyourlastcommand"),
        "dropped29_O0I1": [1 if c == "I" else 0 for c in "OOIIOOOIIOOIOIIOIOOOOIOIIOIOI"],
        "dropped29_O1I0": [1 if c == "O" else 0 for c in "OOIIOOOIIOOIOIIOIOOOOIOIIOIOI"],
        "rowsums": [int(c) for c in "610876654997879"],
        "colsums": [int(c) for c in "8108108736759668"],
        "enter_abrun": abrun,
        "ct322": [int(c) for c in CT_322],
    }
    return seeds


def chain(seed, n, rule, mod):
    """Extend seed to length n by chain addition mod m. Returns list of len n."""
    out = list(seed)
    L = len(seed)
    idx = 0
    while len(out) < n:
        if rule == "fib":
            nxt = (out[-1] + out[-2]) % mod
        elif rule == "lag":
            nxt = (out[-1] + out[-L]) % mod
        elif rule == "rep":
            nxt = out[idx]  # periodic repeat of the seed
            idx += 1
            if idx >= L:
                idx = 0
        else:
            raise ValueError(rule)
        out.append(nxt)
    return out[:n]


def sub_mod(digits, ks, mod):
    return [(dg - k) % mod for dg, k in zip(digits, ks)]


def detr(digits, w):
    """Invert 'write row-major into w columns, read column-major'."""
    n = len(digits)
    if n % w:
        raise ValueError("non full-rectangle")
    rows = n // w
    grid = [[0] * w for _ in range(rows)]
    k = 0
    for c in range(w):
        for r in range(rows):
            grid[r][c] = digits[k]
            k += 1
    out = []
    for r in range(rows):
        out.extend(grid[r])
    return out


def main():
    payloads = {
        "dbbib69": (DBBIB69, [0, 3, 23]),
        "dbbib91": (DBBIB91, [0, 7, 13]),
        "faed570": (FAED, [0, 15, 38]),
    }
    seeds = seed_set()
    ctol = build_grid(ALPHA, 1, 4)
    cands = []
    total_forms = 0

    for pname, (stream, widths) in payloads.items():
        for mname, mp in (("CANON", CANON), ("POS", POS)):
            digits = [mp[c] for c in stream]
            n = len(digits)
            for sname, seed in seeds.items():
                for rule in ("fib", "lag", "rep"):
                    for mod in (9, 10):
                        ks = chain(seed, n, rule, mod)
                        for w in widths:
                            for order in ("sub_trans", "trans_sub"):
                                if order == "sub_trans":
                                    sub = sub_mod(digits, ks, mod)
                                    dec_digits = detr(sub, w) if w else list(sub)
                                else:
                                    tr = detr(digits, w) if w else list(digits)
                                    dec_digits = sub_mod(tr, ks, mod)
                                dec = decode("".join(str(x) for x in dec_digits), ctol, 1, 4)
                                total_forms += 1
                                if "?" in dec:
                                    continue
                                cands += [dec, dec.lower(), dec.upper(), dec[::-1]]
    # dedupe, keep order
    seen = set()
    out = []
    for s in cands:
        if s not in seen:
            seen.add(s)
            out.append(s)
    sys.stderr.write(f"forms={total_forms} clean_cands={len(out)}\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()