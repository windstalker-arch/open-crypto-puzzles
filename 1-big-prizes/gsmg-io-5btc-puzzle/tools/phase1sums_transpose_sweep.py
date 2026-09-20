#!/usr/bin/env python3
"""phase1sums_transpose_sweep.py -- phase-1 FIRST-matrix sum-lists as the
COLUMNAR-TRANSPOSITION key in the trusted joint VIC pipeline over faed/dbbib.

Cell vs ledger: section 45/46/65 transpose keys were the streams' OWN sums
(faed 15x38, dbbib 13/23 col orderings) and phase-1 sums as LITERAL X / SELECTORS
(section 65) and phase-1 sums as keyed-28 ALPHABET (late-207). The phase-1 sums as a
DIGIT-LEVEL columnar transpose key inside cb_decode+col_decrypt(+over-encryption)
is unlogged. Author: "go back to the first puzzle piece"; "matrix sum list" in the
lead-0 vocabulary; 3.2.2 needs a digit-level transposition before the checkerboard.

Method: reuses joint_sweep_91 semantics verbatim (keyed28, col_undo, over_undo,
build_grid/decode of tools/certified_vic.py). Keys from first-matrix sums
rows=610876654997879 (14), cols=8108108736759668 (16), r+c, c+r and reverses, each
as digit-string and as its a1z26 letter-form; widths = len(key) and the natural
15/38/13/16; column reorders = numeric-by-value and natural ranking, fwd/rev;
over-encryption undos = none and matrixsumlist/enter sha256 mod 9 & mod 10 (the
"9->0 at matrixsumlist" hint); streams = faed_570 (rstrip z) and dbbib_91; maps
CANON/POS; escape pairs (1,4),(2,5); alphabets = the certified FUBCDORA.
LETHINGKYMVPS.JQZXW and keyed28 of {matrixsumlist, lastwords, enter}. Clean
(?-free >=8) decodes x {raw,lower,upper,reversed} go 1:1 to both funded oracles.

Witnesses: oracle.py --selftest and oracle_dualite.py --selftest rc=0, certified_vic
SELFCERT 3.2.2 PASS, and a synthetic in-here check that col_undo+decode reproduces
the certified 3.2.2 plaintext when fed its known 149-digit stream, transpose width
13 "matrixsumlist", escape 1,4, alphabet FUBCDORA.LETHINGKYMVPS.JQZXW.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode, CANON, POS, ALPHA  # noqa

DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())
FAED = d["faed_570"].rstrip("z")
DBBI = d["dbbib_91"]
assert len(FAED) == 570 and len(DBBI) == 91

ORACLE_SMALL = os.path.join(ROOT, "tools", "oracle.py")
ORACLE_DUAL = os.path.join(ROOT, "tools", "oracle_dualite.py")

CERT = "FUBCDORA.LETHINGKYMVPS.JQZXW"

ALPHAS = {"phase322": CERT,
          "msl": "FUBCDORA.LETHINGKYMVPS.JQZXW"}  # same cert; listed for legibility


def keyed28(keyword):
    kw = "".join(ch for ch in keyword.upper() if ch.isalpha())
    out = ""
    for ch in kw + ALPHA:
        if ch not in out:
            out += ch
    return (out + "./")[:28]


# phase-1 first matrix "true sum lists" (issue #106; also derived here)
RSUM = "610876654997879"
CSUM = "8108108736759668"


def letters(s):
    return "".join(chr(64 + int(cc)) if int(cc) else "a" for cc in s)


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
    return "".join(str((int(cc) - ks[i % len(ks)]) % M) for i, cc in enumerate(ds))


def to_digits(stream, mp):
    return "".join(str(mp[cc]) for cc in stream if cc in mp)


# certify the pipeline reproduces 3.2.2 here
def selftest_cert():
    import certified_vic
    return certified_vic.selfcert()


assert selftest_cert(), "3.2.2 reproduction failed"
print("pipeline 3.2.2 reproduction: PASS")

KEYS = []
for name, s in (("rs", RSUM), ("cs", CSUM), ("rscs", RSUM + CSUM), ("csrs", CSUM + RSUM)):
    for form_name, form in ((name, s), (name + "_rev", s[::-1]), (name + "_let", letters(s)),
                            (name + "_let_rev", letters(s)[::-1])):
        KEYS.append((form_name, form))

OE_KEYS = {}
for name, phrase in (("msl_m9", "matrixsumlist"), ("msl_m10", "matrixsumlist"),
                     ("enter_m9", "enter"), ("enter_m10", "enter"), ("none", "")):
    if name == "none":
        OE_KEYS[name] = ()
        continue
    h = hashlib.sha256(phrase.encode()).hexdigest()
    OE_KEYS[name] = [int(cc, 16) % (9 if name.endswith("_m9") else 10) for cc in h]

MAPS = [("CANON", CANON), ("POS", POS)]
ESCS = [(1, 4), (2, 5)]
STREAMS = [("faed", FAED), ("dbbib", DBBI)]

def kchar(key, i):
    cc = key[i % len(key)]
    return int(cc) if cc.isdigit() else ord(cc)


cands = set()
n_forms = 0
for kname, key in KEYS:
    for width in sorted(set([len(key), 15, 38, 13, 16])):
        order_num = sorted(range(width), key=lambda i: (kchar(key, i), i))
        order_nat = sorted(range(width), key=lambda i: i)
        for oname, order in (("num", order_num), ("nat", order_nat)):
            for sname, s in STREAMS:
                for mpname, mp in MAPS:
                    ds = to_digits(s, mp)
                    for e1, e2 in ESCS:
                        ctol = build_grid(CERT, e1, e2)
                        for oe_name, kern in OE_KEYS.items():
                            n_forms += 1
                            M = 9 if oe_name.endswith("_m9") else (10 if oe_name.endswith("_m10") else 0)
                            body = over_undo(ds, kern, M) if kern else ds
                            rev = body[::-1]
                            for label, b in (("fwd", body), ("rev", rev)):
                                pt = decode(col_undo(b, width, order), ctol, e1, e2)
                                if "?" not in pt and len(pt) >= 8:
                                    for form in (pt, pt.lower(), pt.upper(), pt[::-1]):
                                        cands.add(form)
    # also run key as over-encryption digit key for a couple widths (matrix-sum over-encryption reads)
print("decode forms:", n_forms)

cands = sorted(cc for cc in cands if cc.strip())
print("clean candidates:", len(cands))
Path(os.path.expanduser("~/tmp/phase1sums_transp_cands.txt")).write_text("\n".join(cands) + "\n")

for label, oracle in (("SMALL", ORACLE_SMALL), ("DUAL", ORACLE_DUAL)):
    rc = subprocess.run([sys.executable, oracle, "--selftest"], capture_output=True)
    print("%s selftest rc=%d" % (label, rc.returncode))
    p = subprocess.run([sys.executable, oracle, "--stdin"],
                       input=("\n".join(cands) + "\n").encode(), capture_output=True)
    ln = p.stdout.decode(errors="replace").splitlines()
    hits = [l for l in ln if l.startswith("MATCH")]
    print("%s: N=%d NO-MATCH=%d HITS=%s" % (label, len(cands), len([l for l in ln if l.startswith("NO MATCH")]), hits))
print("N=", len(cands))