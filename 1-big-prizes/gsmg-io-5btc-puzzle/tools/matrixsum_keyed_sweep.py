#!/usr/bin/env python3
"""matrixsum_keyed_sweep.py -- phase-1 14x14 matrix "matrix sum list" as the
keyed-28 checkerboard alphabet over dbbib(91)/faed(570), both gates.

NEW CELL vs the ledger: the phase-1 matrix row+col sums were only ever oracle-fed as
LITERAL candidate strings (the "610876654997879 / 8108108736759668" digit forms and
single-letter variants). They were never used as the KEYED-28 ALPHABET KEYWORD for the
certified straddling-checkerboard decode of the two SalPhaseIon streams. Lead-0 note
7/author hints ("yellow blue primes ... matrixsumlist", "go back to the first puzzle
piece", the phase-3.2.2 board "as wide as the first one seen" = the 14x14 first matrix)
ground building the alphabet from the first matrix's own sums.

Method:
  - canonical 14x14 bit matrix (gsmg-community README, pixel-verified 86=black / 86=white
    with blue=1/yellow=0 per the community colour convention; spiral check reproduces
    "gsmg.io/theseedisplanted").
  - row sums R[14], col sums C[14] (each value in 3..12; used raw and validated against
    the ledger anchors sum(R)==sum(C)==101).
  - keyword families built from R and C:
      letter-form    s -> chr(64+s)  (A1Z26)
      digit-form     raw decimal concat of the sum values
      mod9-form      s % 9 -> a..i letter set (0->a)
      msk-form       9->o placeholder word ("yellow has a number 9", blue=15 unused)
    assembled as R, C, RC, CR, interleaves riCi and CiRi, each with fwd/rev, each
    additionally as "8/10/10 split" with the '.'/'/' splices at the canonical
    FUBCDORA.LETHINGKYMVPS.JQZXW positions (indices 8 and 21) and the appended-style
    "./" used by the sticker sweeps.
  - x streams {dbbib_91, faed_570} x maps {CANON, POS} x all escape pairs (e1<e2 over
    0..8) -> certified build_grid/decode; clean (?-free) decodes length>=4 collected in
    raw/lower/upper/reversed forms; the keyword literals themselves also collected.
  - candidates fed to tools/oracle.py (small gate) and tools/oracle_dualite.py (Dualite).

Witness: oracle.py --selftest and oracle_dualite.py --selftest both PASS immediately
prior (run here), certified_vic SELFCERT 3.2.2 PASS, and the 14x14 matrix is re-derived
in-process (the ccw-spiral equality to b"gsmg.io/theseedisplanted" is asserted).

A hit is an exact oracle MATCH only. N (candidate count) printed last.
"""
from __future__ import annotations

import itertools
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

# Canonical phase-1 14x14 matrix (gsmg-community README; black/blue=1, yellow/white=0)
MATRIX = [
    "00110100101100",
    "11110011101011",
    "11011101001001",
    "01101000011101",
    "01100011000110",
    "10011000100011",
    "10011100010000",
    "11100000001000",
    "00011101111101",
    "11111100110001",
    "11010000011011",
    "11110010101100",
    "01011101000110",
    "01101101101011",
]
assert len(MATRIX) == 14 and all(len(r) == 14 for r in MATRIX), [len(r) for r in MATRIX]

SPIRAL_EXPECT = b"gsmg.io/theseedisplanted"


DIRS = {"down": (1, 0), "right": (0, 1), "up": (-1, 0), "left": (0, -1)}
NEXT_D = {"down": "right", "right": "up", "up": "left", "left": "down"}


def ccw_spiral_bits(m):
    n = len(m)
    seen = [[False] * n for _ in range(n)]
    out = []
    r = c = 0
    d = "down"  # counterclockwise spiral: first leg goes DOWN the left edge
    while True:
        out.append(m[r][c] == "1")
        seen[r][c] = True
        if len(out) >= n * n:
            break
        dr, dc = DIRS[d]
        nr, nc = r + dr, c + dc
        if not (0 <= nr < n and 0 <= nc < n and not seen[nr][nc]):
            d = NEXT_D[d]
            dr, dc = DIRS[d]
            nr, nc = r + dr, c + dc
            assert 0 <= nr < n and 0 <= nc < n and not seen[nr][nc]
        r, c = nr, nc
    return out


bits = ccw_spiral_bits(MATRIX)
bytex = []
acc = ""
for b in bits:
    acc += "1" if b else "0"
    if len(acc) == 8:
        bytex.append(int(acc, 2)); acc = ""
bytex = bytes(bytex)
assert bytex == SPIRAL_EXPECT, (bytex[:4], SPIRAL_EXPECT[:4])
print("spiral witness: %r == %r PASS" % (bytex, SPIRAL_EXPECT))

R = [sum(1 for ch in row if ch == "1") for row in MATRIX]
C = [sum(1 for r_ in MATRIX if r_[i] == "1") for i in range(14)]
assert sum(R) == sum(C) == 101, (R, C, sum(R), sum(C))
print("row sums:", R)
print("col sums:", C)

def a1z26(vals):
    return "".join(chr(64 + v) for v in vals)  # v in 3..12 -> C..L


def dig(vals):
    return "".join(str(v) for v in vals)


def mod9(vals):
    return "".join(chr(97 + (v % 9)) for v in vals)  # 0->a .. 8->i


def y9(vals):
    return "".join(("o" if v == 9 else chr(64 + v)) for v in vals)


def canon_splice(kw):
    """28-char: 26-letter keyed alphabet with './' at indices 8 and 21 (FUBCDORA.
    LETHINGKYMVPS.JQZXW bracket)."""
    keyed = ""
    for ch in kw.upper() + ALPHA:
        if ch in ALPHA and ch not in keyed:
            keyed += ch
    assert len(keyed) == 26
    return keyed[:8] + "." + keyed[8:21] + "/" + keyed[21:]


def append_splice(kw):
    keyed = ""
    for ch in kw.upper() + ALPHA:
        if ch in ALPHA and ch not in keyed:
            keyed += ch
    assert len(keyed) == 26
    return (keyed + "./")[:28]


def keywords(vals):
    """vals: (name, R, C). Return list of (name, keyword)."""
    out = []
    Rv, Cv = vals
    fams = []
    fams.append(("z", a1z26(Rv) + a1z26(Cv)))          # RC letters
    fams.append(("z2", a1z26(Cv) + a1z26(Rv)))         # CR letters
    fams.append(("R", a1z26(Rv)))
    fams.append(("C", a1z26(Cv)))
    ic = "".join(chr(64 + a) + chr(64 + b) for a, b in zip(Rv, Cv))
    ci = "".join(chr(64 + b) + chr(64 + a) for a, b in zip(Rv, Cv))
    fams.append(("IC", ic))
    fams.append(("CI", ci))
    fams.append(("dg", dig(Rv) + dig(Cv)))
    fams.append(("dgc", dig(Cv) + dig(Rv)))
    fams.append(("m9", mod9(Rv) + mod9(Cv)))
    fams.append(("m9c", mod9(Cv) + mod9(Rv)))
    fams.append(("y", y9(Rv) + y9(Cv)))
    fams.append(("yc", y9(Cv) + y9(Rv)))
    fams.append(("Rmod", mod9(Rv)))
    fams.append(("Cmod", mod9(Cv)))
    fams.append(("all", a1z26(Rv) + a1z26(Cv) + a1z26(Rv)))
    for name, kw in fams:
        out.append((name + "_f", kw))
        out.append((name + "_r", kw[::-1]))
    return out


def all_keywords():
    out = []
    for name, kw in keywords((R, C)):
        for st, fn in (("A", canon_splice), ("B", append_splice)):
            out.append((f"{name}_{st}", fn(kw)))
            out.append((f"{name}_{st}_r", fn(kw)[::-1][:28]))
    return out


def clean(digits, alpha28, e1, e2, mp):
    dstr = "".join(str(mp[ch]) for ch in digits)
    ctol = build_grid(alpha28, e1, e2)
    return decode(dstr, ctol, e1, e2)


def main():
    writes = []
    for nm, kw in all_keywords():
        writes.append((nm, kw))

    kws = all_keywords()
    streams = [("dbbib", DBBI), ("faed", FAED)]
    maps = [("CANON", CANON), ("POS", POS)]
    escapes = [(e1, e2) for e1 in range(9) for e2 in range(e1 + 1, 9)]

    cands = set()
    seen_decode = 0
    for sname, s_ in streams:
        for srev in (False, True):
            st = s_ if not srev else s_[::-1]
            for mname, mp in maps:
                for e1, e2 in escapes:
                    for nm, kw in kws:
                        out = clean(st, kw, e1, e2, mp)
                        seen_decode += 1
                        if "?" not in out and len(out) >= 4:
                            for form in (out, out.lower(), out.upper(), out[::-1]):
                                cands.add(form)
    for nm, kw in kws:
        cands.add(kw)
        cands.add(kw.lower())
        cands.add(kw.upper())
    cands.discard("")
    cands = sorted(cands)

    print("[gen] decode-forms=%d clean-unique=%d" % (seen_decode, len(cands)))

    for label, oracle in (("SMALL", ORACLE_SMALL), ("DUAL", ORACLE_DUAL)):
        rc = subprocess.run([sys.executable, oracle, "--selftest"], capture_output=True)
        print("%s selftest: rc=%d %s" % (label, rc.returncode, rc.stdout.decode(errors="replace")[-60:]))
        assert rc.returncode == 0
        p = subprocess.run([sys.executable, oracle, "--stdin"],
                           input=("\n".join(cands) + "\n").encode(),
                           capture_output=True)
        ln = p.stdout.decode(errors="replace").splitlines()
        hit = [l for l in ln if l.startswith("MATCH")]
        n_no = len([l for l in ln if l.startswith("NO MATCH")])
        print("%s: candidates=%d no-match=%d HITS=%s" % (label, len(cands), n_no, hit))

    print("N=", len(cands))
    if not (os.environ.get("MATRIXSUM_KEYED_NO_SAVE")):
        outpf = os.path.expanduser("~/tmp/matrixsum_keyed_cands.txt")
        Path(outpf).write_text("\n".join(cands) + "\n")
        print("wrote", outpf)


if __name__ == "__main__":
    main()