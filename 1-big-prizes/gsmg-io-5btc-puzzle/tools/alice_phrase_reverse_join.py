#!/usr/bin/env python3
"""alice_phrase_reverse_join.py -- Note-45 #1 reverse pipeline: the Alician phrase
joined with the certified prior decodes (the "password stream's own decodes") as
answer-X candidates for both gates.

Layered idea: dbbib/faed are intermediates; their verified partial decodes
(e.g. the certified 3.2.2 plaintext INCASEYOU..., the faed Bifid head
BTCSEEDDEOEM..., the dbbib-Bifid output) are themselves stream material. If the
answer X is woven from the phrase AND such a decode token, X = join(phrase,
decode) should open a gate. Built from literals computed by the certified tools
(faed-Bifid head re-derived via lead0_layers WITNESS A1 == True; dbbib-Bifid via
A2; VIC plaintext from certified_vic selfcert round-trip).
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORACLE = os.path.join(ROOT, "tools", "oracle.py")
ORACLE_DUAL = os.path.join(ROOT, "tools", "oracle_dualite.py")

PHRASE_C = "whiterabbitnostalgicalicechildhood"
PHRASE_S = "white rabbit nostalgic alice childhood"

DECODES = {
    "vic322": "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE",
    "faed_bifid_head": "BTCSEEDDEOEMCKEADHBSCHDKBDCSDKDVBXCPCOCH",
    "dbbib_bifid": "BDFCDCHLBEBQFCFWCDCDBCECAMDEDMDWGQBCACBEEEBMIWIEEECLEMECCMCCICECFCBCALAEIVIWGCBEBWBWBRFCERB",
}

SEPS = ["", " ", "_", "-", ".", ":", "/", "\n"]

def main():
    cands = set()
    for dname, dec in DECODES.items():
        for pname, phr in (("compact", PHRASE_C), ("spaced", PHRASE_S)):
            for sep in SEPS:
                cands.add(phr + sep + dec)
                cands.add(dec + sep + phr)
                # lowercase / uppercase variants of the whole join
                low = (phr + sep + dec).lower()
                up = (phr + sep + dec).upper()
                cands.add(low)
                cands.add(up)
            # title-ish: phrase capitalized
            cands.add(PHRASE_C.title() + dec)
            cands.add("White Rabbit Nostalgic Alice Childhood" + " " + dec)

    # also: phrase spaces version of decode joins with underscore keys, plus reversed
    for dname, dec in DECODES.items():
        cands.add(PHRASE_S + " " + dec[::-1])
        cands.add(dec[::-1] + " " + PHRASE_S)

    cands = sorted(c for c in cands if c)
    print("candidates:", len(cands))

    scratch = "/data/data/com.termux/files/usr/tmp/opencode"
    os.makedirs(scratch, exist_ok=True)
    path = os.path.join(scratch, "alice_phrase_reverse_join.txt")
    Path(path).write_text("\n".join(cands) + "\n")

    for name, oracle in [("small", ORACLE), ("dualite", ORACLE_DUAL)]:
        r = subprocess.run([sys.executable, oracle, "--stdin"],
                           input=Path(path).read_bytes(), capture_output=True)
        lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
        hits = [ln for ln in lines if ln.startswith("MATCH")]
        print(f"[{name}] tested={len(lines)} MATCH={len(hits)}")
        for h in hits:
            print("HIT:", h)

if __name__ == "__main__":
    main()