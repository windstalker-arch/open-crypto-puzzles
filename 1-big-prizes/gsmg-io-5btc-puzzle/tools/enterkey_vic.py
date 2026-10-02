#!/usr/bin/env python3
"""enterkey_vic.py -- the SalPhaseIon endgame chain, with the "first hint" resolved
to `enter`, tested as the dbbib_91 / faed_570 decode key.

THE THREAD (analysis/leads.md, "endgame" item 4; named untested by R-PAGEANATOMY
2026-10-01 and recorded in R-LEAD0-STAGED). The page's two literal runs are

    raw[860:895]  = shabefourfirsthintisyourlastcommand   ("sha bef" + the phrase)
    raw[1063:1075]= shabefanstoo                          ("sha bef" + "ans too")

read as `sha256(our first hint)` and `sha256(ANSWER)`. The page carries exactly TWO
decoded command tokens -- `matrixsumlist` (raw[91:195]) and `enter` (raw[959:999]) --
so "your LAST command" names `enter`, which makes the first hint `enter` and the
decode key sha256("enter") = e08d706b3e4ce964b632746cf568913cb93f1ed36476fbb0494b80ed17c5975c.

`tools/decodekey_vic.py` tested this chain with the first hint taken to be the
SalPhaseIon slug (89727c.../db14474e.../f9719d6d...). The `enter` value is a DIFFERENT
preimage and was never run. This tool runs exactly that value, under the same four
decode-key interpretations, and oracles every resulting string against BOTH funded
gates.

Decoder is the CERTIFIED one (tools/certified_vic.py build_grid/decode, verbatim) and
--selftest re-derives the phase-3.2.2 vector before anything is scored, so a hand-rolled
decoder cannot silently produce a confident negative (the R-BOARD28B-ADDENDUM rule).

Usage:
    python3 tools/enterkey_vic.py --selftest     # witness only, no oracle
    python3 tools/enterkey_vic.py --dry          # decode + rank, no oracle
    python3 tools/enterkey_vic.py                # decode + oracle both gates
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from certified_vic import build_grid, decode, selfcert, drift_witness  # noqa: E402

DATA = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())
# dbbib_91 is the AUTHORITATIVE stream (live textarea + Wayback 2023-06-01/2026-04-05);
# the 69-token "dbbib" field is the superseded shallow-OCR crop. decodekey_vic.py still
# reads the crop -- see R-CROSSCHECK Error 1.
DBBIB = DATA["dbbib_91"]
FAED = DATA["faed_570"].rstrip("z")

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CANON = {"d": "0", "b": "1", "i": "2", "f": "3", "h": "4", "c": "5", "e": "6", "g": "7", "a": "8"}
POS = {c: str(i) for i, c in enumerate("abcdefghi")}

# The certified 3.2.2 board, plus the title-word keyed boards decodekey_vic.py used, so
# the `enter` key is tested on the SAME board set the slug key was tested on and the
# comparison is like-for-like.
ALPHAS = {
    "cert322": "FUBCDORA.LETHINGKYMVPS.JQZXW",
    "salp": "SALPHASELONBCDFGHIJKMQTUVWXYZ./"[:28],
}


def keyed28(keyword: str, p1: int = 8, p2: int = 18, c1: str = ".", c2: str = "/") -> str:
    kw = "".join(ch for ch in keyword.upper() if ch in ALPHA)
    keyed = ""
    for ch in kw + ALPHA:
        if ch not in keyed:
            keyed += ch
    k = keyed[:26]
    return k[:p1] + c1 + k[p1:p2 - 1] + c2 + k[p2 - 1:]


ALPHAS["salp"] = keyed28("salphaselon")
ALPHAS["cosm"] = keyed28("cosmicduality")
ALPHAS["both"] = keyed28("salphaseloncosmicduality")


def ks_from_hex(keyhex: str, M: int) -> list[int]:
    return [int(c, 16) % M for c in keyhex]


def over_undo(ds: str, ks: list[int], M: int) -> str:
    return "".join(str((int(ch) - ks[i % len(ks)]) % M) for i, ch in enumerate(ds))


def col_undo(ct: str, order: list[int]) -> str:
    W = len(order)
    n = len(ct)
    nrows = (n + W - 1) // W
    full = n % W if n % W else W
    lens = [nrows if i < full else nrows - 1 for i in range(W)]
    placed: list[str | None] = [None] * W
    ptr = 0
    for k in range(W):
        oi = order[k]
        placed[oi] = ct[ptr:ptr + lens[oi]]
        ptr += lens[oi]
    out = []
    for r in range(nrows):
        for c in range(W):
            if r < len(placed[c]):
                out.append(placed[c][r])
    return "".join(out)


def order_for(keyhex: str, W: int) -> list[int]:
    return sorted(range(W), key=lambda i: (keyhex[i % len(keyhex)], i))


def col_trans(ct: str, W: int, order: list[int]) -> str:
    """Columnar-transpose the mapped digit stream with the key as the column ORDER.
    The other documented role these words have (leads.md: "decoded instruction words
    are transposition-key LENGTHS"), so the key is also tried AS the transposition.
    W is 13 = matrixsumlist or 38 = lastwordsbeforearchichoice(26)+thispassword(12).
    """
    n = len(ct)
    nrows = (n + W - 1) // W
    full = n % W if n % W else W
    lens = [nrows if i < full else nrows - 1 for i in range(W)]
    cols: list[str] = [""] * W
    ptr = 0
    for k in range(W):
        di = order[k]
        cols[di] = ct[ptr:ptr + lens[di]]
        ptr += lens[di]
    return "".join("".join(cols[c][r] for c in range(W) if r < len(cols[c]))
                   for r in range(nrows))


def to_digits(stream: str, mp: dict[str, str]) -> str:
    return "".join(mp[c] for c in stream)


def score(pt: str) -> float:
    """Same crude legibility proxy decodekey_vic.py ranked with, kept identical on
    purpose so the two runs' orderings are comparable."""
    pl = re.sub(r"[^a-zA-Z]", " ", pt).lower()
    toks = pl.split()
    if not toks:
        return -1e9
    G = {"e": 12.7, "t": 9.1, "a": 8.2, "o": 7.5, "i": 7.0, "n": 6.7, "s": 6.3,
         "h": 6.1, "r": 6.0, "d": 4.3, "l": 4.0, "c": 2.8, "u": 2.8, "m": 2.4,
         "w": 2.4, "f": 2.2, "g": 2.0, "y": 2.0, "p": 1.9, "b": 1.5, "v": 1.0,
         "k": 0.8, "j": 0.15, "x": 0.15, "q": 0.10, "z": 0.07}
    COMMON = {"the", "and", "you", "that", "this", "with", "not", "have", "from",
              "they", "your", "half", "better", "enter", "password", "matrix",
              "sumlist", "last", "words", "before", "archi", "choice", "key",
              "private", "cosmic", "duality", "salphas", "seed", "funded", "sender",
              "answer", "command", "first", "hint", "yourlast"}
    ug = sum(0.01 * G.get(ch, 0) for ch in pl.replace(" ", ""))
    w = sum(5.0 + len(t) for t in toks if t in COMMON)
    return ug + w


# The decode keys. `enter` is the new value; the slug family is carried as the
# KNOWN-NEGATIVE control so the run proves it reproduces row 77's verdict.
KEY_SOURCES = {
    "sha256(enter)": "enter",
    "sha256(ENTER)": "ENTER",
    "sha256(Enter)": "Enter",
    "sha256(matrixsumlist+enter)": "matrixsumlistenter",
    "sha256(enter+matrixsumlist)": "entermatrixsumlist",
    "sha256(sha256(enter))": hashlib.sha256(b"enter").hexdigest(),
}
CONTROL_KEY = hashlib.sha256(
    b"GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe").hexdigest()


def run(dry: bool) -> int:
    if not selfcert():
        print("SELFCERT FAILED -- refusing to score anything (R-BOARD28B-ADDENDUM rule)")
        return 2
    print("witness: phase-3.2.2 certified decode reproduced before scoring  [PASS]")

    keys = {n: hashlib.sha256(v.encode()).hexdigest() for n, v in KEY_SOURCES.items()}
    keys["CONTROL sha256(slug) [row 77]"] = CONTROL_KEY

    results = []
    cands: set[str] = set()
    t0 = time.time()
    for kname, dk in keys.items():
        for aname, alpha28 in ALPHAS.items():
            for mpn, mp in (("CANON", CANON), ("POS", POS)):
                for e1, e2 in ((1, 4), (2, 5)):
                    ctol = build_grid(alpha28, e1, e2)
                    order = order_for(dk, 64)
                    for sname, stream in (("dbbib_91", DBBIB), ("faed_570", FAED)):
                        ds = to_digits(stream, mp)
                        forms = [("none", ds)]
                        for M in (9, 10):
                            forms.append((f"ks{M}", over_undo(ds, ks_from_hex(dk, M), M)))
                        forms.append(("col", col_undo(ds, order)))
                        forms.append(("ks9+col", col_undo(over_undo(ds, ks_from_hex(dk, 9), 9), order)))
                        # the key AS the transposition order, at the two certified widths
                        for W in (13, 38):
                            forms.append((f"trans{W}", col_trans(ds, W, order_for(dk, W))))
                        # and the key as the transposition order AFTER keystream undo
                        for W in (13, 38):
                            forms.append((f"ks9+trans{W}",
                                          col_trans(over_undo(ds, ks_from_hex(dk, 9), 9), W, order_for(dk, W))))
                        for fname, ds2 in forms:
                            pt = decode(ds2, ctol, e1, e2)
                            sc = score(pt)
                            results.append((sc, kname, aname, mpn, e1, e2, sname, fname, pt))
                            for v in (pt.lower(), pt.upper(), pt):
                                if "?" not in v and len(v) >= 8:
                                    cands.add(v)

    results.sort(key=lambda x: -x[0])
    print(f"\ndecodes: {len(results)}  elapsed {time.time()-t0:.1f}s")
    print("=== top 15 by legibility ===")
    for sc, kname, aname, mpn, e1, e2, sname, fname, pt in results[:15]:
        print(f"[{sc:6.1f}] {kname:32s} {aname:9s} {mpn:5s} e{e1}{e2} {sname:9s} {fname:7s} {pt[:52]}")

    best = results[0][0]
    print(f"\n[decode] best legibility {best:.1f}  (row 77's slug-key peak was ~31, English ~96)")
    if best < 40:
        print("[read] nothing near English: these are ciphertext, not plaintext.")

    if dry:
        print(f"[dry] {len(cands)} candidates NOT oracled")
        return 0

    print(f"\n[gen] {len(cands)} distinct candidates -> both funded gates")
    hit = False
    for tool, tag in (("oracle.py", "small 1GSMG1JC9"), ("oracle_dualite.py", "dualite 17ucy1K9")):
        p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", tool), "--stdin"],
                           input="\n".join(sorted(cands)), capture_output=True, text=True)
        if p.returncode == 0:
            print(f"MATCH via {tool} ({tag}):\n{p.stdout}")
            hit = True
        else:
            print(f"{tool:20s} {tag:18s} {len(cands)} candidates  NO MATCH")
    print("\nRESULT:", "MATCH -- see above" if hit else "NO MATCH on either gate")
    return 0 if hit else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        ok = selfcert()
        dw = drift_witness()
        print("SELFCERT 3.2.2:", "PASS" if ok else "FAIL")
        print("DRIFT WITNESS (must FAIL):", "PASS" if dw else "FAIL")
        raise SystemExit(0 if (ok and dw) else 1)
    raise SystemExit(run(a.dry))
