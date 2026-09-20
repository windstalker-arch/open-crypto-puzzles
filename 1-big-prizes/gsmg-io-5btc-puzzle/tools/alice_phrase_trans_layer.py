#!/usr/bin/env python3
"""alice_phrase_trans_layer.py -- the phrase as TRANSPOSITION/over-encryption layer
inside the certified VIC pipeline on faed/dbbib (Note-46 ranked #1/#2).

Prior sweeps used the phrase only as the CHECKERBOARD alphabet. Here the phrase
plays the pipeline steps it was never given: (i) columnar-undo WIDTH derived from
the phrase length with column order from the phrase letters; (ii) mod-9/mod-10
over-encryption key = sha256(phrase variants) hex digits; and (iii) the reverse
order (OE first, then width). All four certified alphabets, both maps, certified
escape pairs.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode, CANON, POS, DBBIB, FAED

ORACLE = os.path.join(ROOT, "tools", "oracle.py")
ORACLE_DUAL = os.path.join(ROOT, "tools", "oracle_dualite.py")

PHRASES = {
    "compact": "whiterabbitnostalgicalicechildhood",
    "spaced": "white rabbit nostalgic alice childhood",
    "title": "White Rabbit Nostalgic Alice Childhood",
    "reversed": "whiterabbitnostalgicalicechildhood"[::-1],
    "alice_head": "whiterabbitnostalgicalice",
    "child_head": "whiterabbitnostalgicchildhood",
}

ALPHAS = {
    "phase322": "FUBCDORA.LETHINGKYMVPS.JQZXW",
    "keyed_compact": None,  # built below
    "keyed_spaced": None,
    "lean": "ABCDEFGHKLMNPQRSTUVWXYZ",
}

def keyed28(keyword):
    kw = "".join(ch for ch in keyword.upper() if ch.isalpha())
    out = ""
    for ch in kw + "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if ch not in out:
            out += ch
    return (out + "./")[:28]

ALPHAS["keyed_compact"] = keyed28(PHRASES["compact"])
ALPHAS["keyed_spaced"] = keyed28(PHRASES["spaced"])

def to_digits(stream, mp):
    return "".join(str(mp[c]) for c in stream if c in mp)

def col_undo(ct, width, key_order):
    n = len(ct)
    nrows = (n + width - 1) // width
    full = n % width if n % width else width
    lens = [nrows if i < full else nrows - 1 for i in range(width)]
    placed = [None] * width
    ptr = 0
    for k in range(width):
        ci = key_order[k]
        placed[ci] = ct[ptr:ptr + lens[ci]]
        ptr += lens[ci]
    out = []
    for r in range(nrows):
        for c in range(width):
            if r < len(placed[c]):
                out.append(placed[c][r])
    return "".join(out)

def over_undo(ds, ks, M):
    return "".join(str((int(ch) - ks[i % len(ks)]) % M) for i, ch in enumerate(ds))

def order_from_keyword(kw, width):
    """Column order: sort positions by (letter, index) -- standard columnar key."""
    return sorted(range(width), key=lambda i: (kw[i % len(kw)], i))

def english_score(dec):
    if "?" in dec:
        return -1
    s = dec.upper()
    score = sum(3 * s.count(w) for w in ("THE","AND","ING","THA","ENT","ION","YOU","KEY",
        "DOOR","PHASE","WHITE","OPEN","LOCK","GATE","ANSWER","PRIVATE","WALLET","HALF",
        "BETTER","SECRET","HINT","CODE","COSMIC","SEED","RABBIT","ALICE"))
    score += max(0, len(s) - 20) // 4
    return score

def main():
    cand = []
    cand_strs = set()
    streams = {"dbbib": DBBIB, "faed": FAED}
    maps = {"CANON": CANON, "POS": POS}
    escapes = [(1,4), (2,5)]

    # OE keys from phrase hashes
    oe_keys = {}
    for pname, phr in PHRASES.items():
        h = hashlib.sha256(phr.encode()).hexdigest()
        oe_keys[pname + "_m9"] = [int(c, 16) % 9 for c in h]
        oe_keys[pname + "_m10"] = [int(c, 16) % 10 for c in h]
        # raw letter-order too (phrase letter positions as digits 0..9)
        letters = [ch.upper() for ch in phr if ch.isalpha()]
        oe_keys[pname + "_letter_m9"] = [(ord(ch) - 65) % 9 for ch in letters]
        oe_keys[pname + "_letter_m10"] = [(ord(ch) - 65) % 10 for ch in letters]

    widths = {}
    for pname, phr in PHRASES.items():
        w = len([ch for ch in phr if ch.isalpha()])
        widths[pname] = w  # e.g. compact=34

    total = 0
    for aname, alpha in ALPHAS.items():
        for sname, stream in streams.items():
            for mname, mp in maps.items():
                ds = to_digits(stream, mp)
                for e1, e2 in escapes:
                    ctol = build_grid(alpha, e1, e2)
                    for oe_name, oe_key in oe_keys.items():
                        M = 9 if "_m9" in oe_name else 10
                        # (i) transposition first, then decode
                        for wname, w in widths.items():
                            order = order_from_keyword(PHRASES[wname], w)
                            ds2 = col_undo(over_undo(ds, oe_key, M), w, order)
                            pt = decode(ds2, ctol, e1, e2)
                            total += 1
                            if "?" not in pt and len(pt) >= 12 and pt not in cand_strs:
                                cand_strs.add(pt)
                                cand.append((english_score(pt), pt, aname, sname, mname, e1, e2, wname, oe_name))
                            # plain transpose, no OE
                            ds3 = col_undo(ds, w, order)
                            pt3 = decode(ds3, ctol, e1, e2)
                            total += 1
                            if "?" not in pt3 and len(pt3) >= 12 and pt3 not in cand_strs:
                                cand_strs.add(pt3)
                                cand.append((english_score(pt3), pt3, aname, sname, mname, e1, e2, wname, "no-oe"))

    cand.sort(key=lambda t: -t[0])
    print(f"total pipeline forms: {total}, clean decodes: {len(cand)}")
    print("Top 20 by English score:")
    for t in cand[:20]:
        print(f"  score={t[0]:4d} {t[1][:80]}")

    scratch = "/data/data/com.termux/files/usr/tmp/opencode"
    os.makedirs(scratch, exist_ok=True)
    path = os.path.join(scratch, "alice_phrase_trans_cands.txt")
    Path(path).write_text("\n".join(t[1] for t in cand) + "\n")
    print("wrote cands:", len(cand))

    for name, oracle in [("small", ORACLE), ("dualite", ORACLE_DUAL)]:
        r = subprocess.run([sys.executable, oracle, "--stdin"],
                           input=Path(path).read_bytes(), capture_output=True)
        lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
        hits = [ln for ln in lines if ln.startswith("MATCH")]
        print(f"[{name}] tested={len(lines)} MATCH={len(hits)}")
        for h in hits:
            print("HIT:", h)

    # full decode dump for diagnosis
    Path(os.path.join(scratch, "alice_phrase_trans_all.txt")).write_text(
        "\n".join(f"{t[0]}\t{t[1]}" for t in cand) + "\n")

if __name__ == "__main__":
    main()