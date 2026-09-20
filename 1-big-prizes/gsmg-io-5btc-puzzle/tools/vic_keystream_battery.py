#!/usr/bin/env python3
"""VIC over-encryption battery with a WIDER keystream family (lead-0 residual cell).

Extends vic_chain_oe_battery.py's sub-then-trans / trans-then-sub joint to fresh
keystream sources never used before:
  - digest/hex streams (sha256/md5 of puzzle strings), hex digits as 0..15
  - base64-index keystreams from the two visible blob halves (live tokens 895..958, 999..1062)
  - the 104-token a/b binary run (live tokens 91..194)
  - phone-keypad digits of the FULL directive sentence and the two hint words
    (firsttint / ans too / secondanswer / yourlastcommand)
  - digits of universal constants pi, e, sqrt2, golden ratio (sympy)
  - object_256 / even_stream / odd_pre_reduction as digit streams
    (letter-position mod 9/10 and phone)
  - 14x14 matrix row/column bit values as decimal-digit streams
  - blue/yellow coordinate-digit streams
  - prime numbers first-N concatenation

Same decode pipeline as the certified row-199 core: map -> digits (CANON/POS),
optionally subtract a chain keystream mod {9,10}, optionally de-transpose at the
payload's full-rectangle widths ({0,3,23}/{0,7,13}/{0,15,38}), certified 28-char
board decode (escapes 1,4). Emits clean (question-free) decodes + answer-forms.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from certified_vic import build_grid, decode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.loads((Path(ROOT) / "data" / "finalpage-digit-streams.json").read_text())
MOV = json.loads((Path(ROOT) / "data" / "salphaseion-streams.json").read_text())
LIVE = (Path(ROOT) / "data" / "live_salphaseion.txt").read_text().split()

DBBIB69 = d["dbbib"]
FAED = d["faed_570"].rstrip("z")
DBBIB91 = "".join(LIVE[:91])
OBJ = MOV["object_256"]
EVEN = MOV["even_stream"]
ODD = MOV["odd_pre_reduction"]

ALPHA = "FUBCDORA.LETHINGKYMVPS.JQZXW"
CANON = {"d": 0, "b": 1, "i": 2, "f": 3, "h": 4, "c": 5, "e": 6, "g": 7, "a": 8}
POS = {c: i for i, c in enumerate("abcdefghi")}

PHONE = {c: dg for c, dg in zip(
    "abcdefghijklmnopqrstuvwxyz",
    "22233344455566677778889999")}

BLUE = [(0,5),(1,2),(1,10),(2,7),(3,4),(4,1),(6,3),(7,0),(8,5),(8,13),(9,2),(11,8),(12,1),(13,2),(13,10)]
YELLOW = [(0,13),(4,9),(5,6),(5,10),(6,11),(7,12),(9,6),(10,7),(12,9)]

B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def phone_digits(word):
    return [int(PHONE[c]) for c in word if c in PHONE]


def hex_digits(s):
    return [int(c, 16) for c in s.hexdigest()]


def b64_idx(n, half):
    toks = LIVE[895 + n * 64: 895 + n * 64 + 64] if n == 0 else LIVE[999:999 + 64]
    out = []
    for t in toks:
        code = -1
        for i, ch in enumerate(B64):
            if ch == t:
                code = i
                break
        if code >= 0:
            out.append(code)
    return out


def spiral_bits():
    ccw = []
    top, left, bottom, right = 0, 0, 13, 13
    while len(ccw) < 196:
        for r in range(top, bottom + 1):
            ccw.append((r, left))
        left += 1
        if len(ccw) >= 196:
            break
        for c in range(left, right + 1):
            ccw.append((bottom, c))
        bottom -= 1
        if len(ccw) >= 196:
            break
        for r in range(bottom, top - 1, -1):
            ccw.append((r, right))
        right -= 1
        if len(ccw) >= 196:
            break
        for c in range(right, left - 1, -1):
            ccw.append((top, c))
        top += 1
    url = b"gsmg.io/theseedisplanted"
    bits = []
    for b in url:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    bits += [0, 0, 0, 0]
    grid = {}
    for i, (r, c) in enumerate(ccw):
        grid[(r, c)] = bits[i]
    matrix = [[grid[(r, c)] for c in range(14)] for r in range(14)]
    return matrix


def seed_set():
    grid = spiral_bits()
    s = {}
    # digest/hex families
    for name, txt in [
        ("sha_seed", "theseedisplanted"),
        ("sha_slug", "gsmg.io/theseedisplanted"),
        ("sha_pw", "thispassword"),
        ("sha_obj", OBJ),
        ("sha_even", EVEN),
        ("sha_odd", ODD),
        ("sha_faed", FAED),
        ("sha_dbbib91", DBBIB91),
        ("sha_322", "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE"),
        ("sha_directives", "matrixsumlist enter lastwordsbeforearchichoice thispassword matrixsumlist yourlastcommand secondanswer"),
    ]:
        s[name] = hex_digits(hashlib.sha256(txt.encode()))
        s[name.replace("sha_", "md5_")] = hex_digits(hashlib.md5(txt.encode()))
    # base64 halves
    for n in (0, 1):
        s[f"b64half{n}"] = b64_idx(n, n)
    # a/b 104-token run (tokens 91..194)
    s["abrun104"] = [0 if t == "a" else 1 for t in LIVE[91:195]]
    # phone digits (full directive sentence + hint words never used)
    s["phone_full_directives"] = phone_digits(
        "matrixsumlistenterlastwordsbeforearchichoicepasswordmatrixsumlistyourlastcommandsecondanswer")
    s["phone_yourlastcommand"] = phone_digits("yourlastcommand")
    s["phone_secondanswer"] = phone_digits("secondanswer")
    s["phone_firsttint"] = phone_digits("firsttint")
    s["phone_anstoo"] = phone_digits("anstoo")
    s["phone_enterlastwords"] = phone_digits("enterlastwordsbeforearchichoice")
    # universal constants via sympy
    try:
        import sympy as sp
        for name, ex in [("pi", sp.pi), ("e", sp.E), ("sqrt2", sp.sqrt(2)),
                         ("phi", (1 + sp.sqrt(5)) / 2)]:
            digs = str(sp.N(ex, 600))
            digs = digs.replace(".", "")
            s[f"const_{name}"] = [int(c) for c in digs if c.isdigit()]
    except Exception as e:
        sys.stderr.write(f"consts unavailable: {e}\n")
    # object/even/odd as digit streams
    s["obj_pos"] = [(ord(c) - 64) for c in OBJ]           # 1..23
    s["obj_phone"] = phone_digits(OBJ.lower())
    s["even_pos"] = [("BCDE".index(c)) for c in EVEN]
    s["odd_pos"] = [(ord(c) - 64) for c in ODD]
    # matrix rows/cols as decimal digits
    rowdigs, coldigs = [], []
    for r in range(14):
        rowbits = [grid[r][c] for c in range(14)]
        rowdigs.extend([int(x) for x in str(sum(b << (13 - i) for i, b in enumerate(rowbits)))])
    for c in range(14):
        colbits = [grid[r][c] for r in range(14)]
        coldigs.extend([int(x) for x in str(sum(b << (13 - i) for i, b in enumerate(colbits)))])
    s["matrix_rows"] = rowdigs
    s["matrix_cols"] = coldigs
    # coordinate digit streams
    s["blue_coords"] = [int(dg) for (r, c) in BLUE for dg in f"{r}{c}"]
    s["yellow_coords"] = [int(dg) for (r, c) in YELLOW for dg in f"{r}{c}"]
    s["my_coords"] = [int(dg) for (r, c) in BLUE + YELLOW for dg in f"{r}{c}"]
    # primes digits
    primes = []
    cand = 2
    while len(primes) < 120:
        if all(cand % p for p in primes if p * p <= cand):
            primes.append(cand)
        cand += 1
    s["primes"] = [int(dg) for pstr in [str(p) for p in primes] for dg in pstr]
    return s


def chain(seed, n, rule, mod):
    out = list(seed)
    L = len(seed)
    idx = 0
    while len(out) < n:
        if rule == "fib":
            nxt = (out[-1] + out[-2]) % mod
        elif rule == "lag":
            nxt = (out[-1] + out[-L]) % mod
        elif rule == "rep":
            nxt = out[idx]
            idx += 1
            if idx >= L:
                idx = 0
        out.append(nxt)
    return out[:n]


def sub_mod(digits, ks, mod):
    return [(dg - k) % mod for dg, k in zip(digits, ks)]


def detr(digits, w):
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
    seen = set()
    out = []
    for s in cands:
        if s not in seen and len(s) > 0:
            seen.add(s)
            out.append(s)
    sys.stderr.write(f"seeds={len(seeds)} forms={total_forms} clean_cands={len(out)}\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()