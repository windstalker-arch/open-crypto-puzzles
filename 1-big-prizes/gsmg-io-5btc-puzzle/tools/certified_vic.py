#!/usr/bin/env python3
"""Certified VIC checkerboard decoder for dbbib/faed under the title-word keyed
alphabet (salphaselon / cosmicduality = the two halves).

CERTIFIED against phase 3.2.2 (community README + dcode VIC): the 28-char alphabet
"FUBCDORA.LETHINGKYMVPS.JQZXW" with escapes digit1=1 digit2=4, applied as a pure
straddling checkerboard (NO columnar transposition, NO over-encryption) to the
149-digit ciphertext, reproduces verbatim:
  "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE"

dcode VIC grid layout (28-char alphabet row-major over 3 rows):
  row0 = first 8 letters on digits 0..9 minus the two escapes (ascending)
  row1 = next 10 on escape-e1 codes e1+0..e1+9
  row2 = last 10 on escape-e2 codes e2+0..e2+9
The 9-symbol streams (a..i) are mapped to digits (CANON/POS), then decoded.
Whole sweeps feed tools/oracle.py (small gate, 1.25 BTC) and oracle_dualite.py (Dualite).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())
DBBIB = d["dbbib_91"]  # authoritative 91-token live stream (rows 193-199, 2026-09-07/08; 69-token 'dbbib' field is the superseded OCR artifact)
FAED = d["faed_570"].rstrip("z")

CANON = {"d":0,"b":1,"i":2,"f":3,"h":4,"c":5,"e":6,"g":7,"a":8}
POS   = {c:i for i,c in enumerate("abcdefghi")}
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def keyed28(keyword, punct_letter_pair):
    """MISNAMED / INCOMPLETE. Despite the name and the old docstring, this does
    NOT build a 28-char alphabet: it returns the 26 LETTERS only, with no
    punctuation spliced in at all. `punct_letter_pair` is unpacked into `_p1, _p2`
    and then never used, so the argument has no effect.

    Callers that need a real 28-char board must splice it themselves; three
    modules (dict_keyed_sweep.py, lead0_eyeball.py, custom_keyed_seeds_sweep.py)
    import this and re-splice by hand, which is why the gap went unnoticed. For
    reference the genuine certified board is FUBCDORA.LETHINGKYMVPS.JQZXW, whose
    two punct cells are BOTH '.' at 0-based 8 and 22 (letter runs 8|13|5) - not
    '.' and '/'. Behaviour here is left unchanged on purpose; correcting the
    splice would break those three callers. See analysis/tested.md
    R-STRUCT8-13-5-2026-09-26.
    """
    kw = "".join(ch for ch in keyword.upper() if ch in ALPHA)
    keyed = ""
    for ch in kw + ALPHA:
        if ch not in keyed:
            keyed += ch
    assert len(keyed) == 26, keyed
    _p1, _p2 = punct_letter_pair   # UNUSED - see docstring; no splice is performed
    return keyed

def build_grid(alpha28, e1, e2):
    row0, row1, row2 = alpha28[:8], alpha28[8:18], alpha28[18:28]
    ctol = {}
    non = [dd for dd in range(10) if dd not in (e1, e2)]
    for ch, dd in zip(row0, non):
        ctol[str(dd)] = ch
    for i, ch in enumerate(row1):
        ctol[f"{e1}{i}"] = ch
    for i, ch in enumerate(row2):
        ctol[f"{e2}{i}"] = ch
    return ctol

def decode(digits_str, ctol, e1, e2):
    out, i = [], 0
    s = digits_str
    while i < len(s):
        c = s[i]
        if c in (str(e1), str(e2)):
            code = s[i:i+2]
            if code in ctol:
                out.append(ctol[code]); i += 2; continue
        if c in ctol:
            out.append(ctol[c]); i += 1; continue
        out.append("?"); i += 1
    return "".join(out)

def selfcert():
    ct = ("151659431219724091691712137589518131415431314124281541913121812194"
          "33121171617137149110916631213131281491109166131412199114371612126021664313711154112")
    alpha = "FUBCDORA.LETHINGKYMVPS.JQZXW"
    ctol = build_grid(alpha, 1, 4)
    got = decode(ct, ctol, 1, 4)
    want = "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE"
    return got == want

if __name__ == "__main__":
    ok = selfcert()
    print("SELFCERT 3.2.2:", "PASS" if ok else "FAIL")
