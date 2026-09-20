#!/usr/bin/env python3
"""keyed_vic_battery.py -- one-keyword / one-alphabet VIC decode battery for the
final-page digit streams, built on the CERTIFIED 3.2.2 decoder.

Lead 0's crux is the interpreter-alphabet leap: the streams' keyed alphabet is
the one unprovided input. When a transcription (or any new hypothesis) supplies
a candidate alphabet source, this tool turns it into oracle candidates in one
step, with the decoder pre-certified against the puzzle's own phase 3.2.2 vector.

Certified pipeline (tools/certified_vic.py, verbatim build_grid/decode):
  28-char alphabet, dcode 3-row VIC grid (row0=8 on the non-escape digits,
  row1=10 under escape e1, row2=10 under escape e2). The exact vector:
  alphabet "FUBCDORA.LETHINGKYMVPS.JQZXW", escapes (1,4), applied as a pure
  straddling checkerboard to the 149-digit phase-3.2.2 ciphertext, reproduces
      INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDSETTERHALFANDTHEYALSONEEDFUNDSTOLIVE
  (verified against community README + dcode).

Alphabet input forms (mutually exclusive):
  --alphabet STR     use the 28-character alphabet verbatim (from a transcription)
  --keyword WORD     keyed alphabet = dedupe(WORD + A-Z) (26) with '.' and '/'
                     spliced in at --punct1/--punct2 (default positions 8,18)

Decode parameters:
  --map pos|canon   a..i -> digit interpreter (pos: a=0..i=8; canon: D=0..K=9)
  --map-raw STR     explicit 9-char interpreter alphabet (position i -> digit i
                    of this string), e.g. "--map-raw dbifhcega"
  --escapes 1 4     escape digits (both proven pairs (1,4) and (2,5) flag-tested)
  --trans L         digit-level columnar-decipher of the mapped stream with a
                    key length L before the checkerboard decode (repeatable;
                    the certified lengths to try are 13 = matrixsumlist and
                    38 = lastwordsbeforearchichoice(26)+thispassword(12))
  --reverse         also try the stream reversed (the author's first hint)

Output: decoded plaintext candidates for both streams, printed to stdout and
(unless --dry) fed to tools/oracle.py + oracle_dualite.py for a certified check.

Usage:
    python3 tools/keyed_vic_battery.py --keyword "white rabbit" --map canon
    python3 tools/keyed_vic_battery.py --alphabet "FUBCDORA.LETHINGKYMVPS.JQZXW" --map pos --escapes 1 4
    python3 tools/keyed_vic_battery.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from certified_vic import build_grid, decode, selfcert  # noqa: E402
from vic_checkerboard import columnar_transpose  # noqa: E402

DATA = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())
DBBIB = DATA["dbbib_91"]
FAED = DATA["faed_570"].rstrip("z")

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CANON = {"d": "0", "b": "1", "i": "2", "f": "3", "h": "4", "c": "5", "e": "6", "g": "7", "a": "8"}


def keyed26(keyword: str) -> str:
    kw = "".join(ch for ch in keyword.upper() if ch in ALPHA)
    keyed = ""
    for ch in kw + ALPHA:
        if ch not in keyed:
            keyed += ch
    assert len(keyed) == 26, keyed
    return keyed


def keyed28(keyword: str, p1: int, p2: int, pchr1: str = ".", pchr2: str = "/") -> str:
    k = keyed26(keyword)
    return k[:p1] + pchr1 + k[p1:p2 - 1] + pchr2 + k[p2 - 1:]


def interpreter_map(spec: str) -> dict[str, str]:
    if spec == "pos":
        return {c: str(i) for i, c in enumerate("abcdefghi")}
    if spec == "canon":
        return dict(CANON)
    if len(spec) == 9:
        return {c: str(i) for i, c in enumerate(spec)}
    raise ValueError("--map-raw must be 9 characters (interpreters a..i -> 0..8)")


def mapped(stream: str, imap: dict[str, str]) -> str:
    return "".join(imap.get(ch, "?") for ch in stream)


def transposed(digits: str, L: int) -> str:
    if L <= 1:
        return digits
    return columnar_transpose(digits, "A" * L)


def run_alphabet(alpha28: str, imap: dict[str, str], esc: tuple[int, int],
                 trans: list[int], reverse: bool) -> list[str]:
    assert len(alpha28) == 28, f"alphabet must be 28 chars, got {len(alpha28)}: {alpha28!r}"
    ctol = build_grid(alpha28, *esc)
    cands: list[str] = []
    for name, stream in (("dbbib", DBBIB), ("faed", FAED)):
        digits = mapped(stream, imap)
        variants = [(f"{name}", digits)]
        if reverse:
            variants.append((f"{name}-rev", digits[::-1]))
        for vname, dg in variants:
            layers = [(vname, dg)]
            for L in trans:
                layers.append((f"{vname}-T{L}", transposed(dg, L)))
            for lname, ldg in layers:
                out = decode(ldg, ctol, *esc)
                cands.append(out)
                cands.append(out.lower())
                cands.append(out.upper())
    return cands


def oracle_step(path: str, cands: list[str]) -> tuple[bool, float]:
    n = len(cands)
    t0 = time.time()
    found = False
    p = subprocess.Popen(
        [sys.executable, path, "--stdin"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, text=True,
    )
    out, _ = p.communicate("\n".join(cands) + "\n")
    dt = time.time() - t0
    for line in out.splitlines():
        if line.startswith("MATCH"):
            found = True
            print(f"MATCH via {path}: {line}", flush=True)
    print(f"oracle {os.path.basename(path)}: {n} candidates in {dt:.0f}s "
          f"({n / dt:.0f}/s) -> {'MATCH FOUND' if found else 'no match'}", flush=True)
    return found, dt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--alphabet", help="verbatim 28-char VIC alphabet")
    g.add_argument("--keyword", help="keyed-alphabet keyword (dedupe + splice)")
    ap.add_argument("--punct1", type=int, default=8, help="splice position of '.' (decoder row1 col0)")
    ap.add_argument("--punct2", type=int, default=18, help="splice position of '/' (decoder row2 col0)")
    ap.add_argument("--map", choices=["pos", "canon"], default="pos")
    ap.add_argument("--map-raw", help="explicit 9-char interpreter (position i -> digit i)")
    ap.add_argument("--escapes", nargs=2, type=int, default=[1, 4])
    ap.add_argument("--trans", type=int, action="append", default=[], help="columnar key length (repeatable)")
    ap.add_argument("--reverse", action="store_true")
    ap.add_argument("--dry", action="store_true", help="print decodes only, no oracle")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        ok = selfcert()
        print("SELFCERT 3.2.2:", "PASS" if ok else "FAIL")
        alpha = "FUBCDORA.LETHINGKYMVPS.JQZXW"
        for m, im in (("pos", interpreter_map("pos")), ("canon", interpreter_map("canon"))):
            from certified_vic import DBBIB as D
            _ = D
            cands = run_alphabet(alpha, im, (1, 4), [13, 38], False)
            print(f"selftest decode forms under {m}: {len(cands)} unique? (ops only)")
        return 0 if ok else 1

    if args.alphabet:
        alpha28 = args.alphabet.upper()
    elif args.keyword:
        alpha28 = keyed28(args.keyword, args.punct1, args.punct2)
        print(f"keyed28 from keyword: {alpha28}", flush=True)
    else:
        ap.print_help()
        return 2

    imap = interpreter_map(args.map_raw or args.map)
    esc = (args.escapes[0], args.escapes[1])

    cands = run_alphabet(alpha28, imap, esc, args.trans, args.reverse)
    uniq = list(dict.fromkeys(cands))
    print(f"config: alphabet={alpha28} map={args.map_raw or args.map} escapes={esc} "
          f"trans={args.trans or 'none'} reverse={args.reverse} -> {len(uniq)} unique candidates",
          flush=True)
    if args.dry:
        for c in uniq:
            print(c)
        return 0

    N = len(uniq)
    if N > 500_000:
        print(f"N={N:,} exceeds the 500k bound for a single oracle pass; use a family sweep.", flush=True)
        return 3

    hits = 0
    hit, d1 = oracle_step(os.path.join(ROOT, "tools", "oracle.py"), uniq)
    hits += hit
    hit, d2 = oracle_step(os.path.join(ROOT, "tools", "oracle_dualite.py"), uniq)
    hits += hit
    print(f"TOTAL: {N} candidates x both gates -> {'MATCH FOUND' if hits else '0 MATCH'}")
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())