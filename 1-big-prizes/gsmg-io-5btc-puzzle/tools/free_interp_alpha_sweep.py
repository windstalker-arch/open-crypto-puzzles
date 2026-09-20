#!/usr/bin/env python3
"""free_interp_alpha_sweep.py -- free interpreter x free alphabet, then
transposition/OE layers, under the escape-frequency constraint.

Rationale (leads.md note 1, fact 5): the final-gate VIC decode carries FIVE
joint unknowns -- alphabet, a..i->digit interpreter, escapes, transposition
key, over-encryption keystream -- and only the funded oracle can verify a
joint guess. Prior free-space runs fixed TWO of them:
  - leap_alphabet_sweep: 44 sentence alphabets x {CANON,POS}, 15 widths, 39 OE
  - interpreter_vic_sweep: 9! interpreters x 1 certified alphabet, no trans/OE
Neither left BOTH interpreter and alphabet free at once.

This sweep frees both, constrained by the strongest external evidence for the
interpreter: in the certified 3.2.2 template the stream's TWO MOST FREQUENT
letters map to the escape digits (community CANON: dbbib's b,e -> 1,4 == the
3.2.2 escapes). So the interpreter family here = all permutations mapping the
stream's top-2 letters onto {e1,e2} (2! orderings) x the other 7 letters onto
the 7 non-escape digits (7!) = 10,080 per (escape pair, digit domain,
frequency-source stream). This is 36x smaller than 9! but NOT covered by the
two fixed-map sweeps.

Stages (run big-to-small so a stage-1 hit is attributable):
  stage1: escape (1,4), both domains, faed+dbbi69 freq sources, 37+2 sentence
          alphas, faed/dbbi69/dbbi91 payloads, trans=none, OE=identity.
  stage2: escape (1,4), domain 0..8, faed freq source, 37 alphas, faed payload,
          trans widths {13,15,38}, OE identity + 3 hint-phrase keystreams.
Clean (?-free) decodes -> answer-forms -> both funded-gate oracles (file-stdin
+ communicate(); a write-then-read pipe loop deadlocks at the 64KB buffer).
"""
import itertools
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid
from leap_alphabet_sweep import (
    ALPHAS,
    OE_KEYS,
    TRANS_WIDTHS,
    col_undo,
    over_undo,
)

OGDIR = os.path.expanduser("~")
DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())
FAED = d["faed_570"].rstrip("z")
DBBI69 = d["dbbib"]
DBBI91 = Path(os.path.join(OGDIR, "tmp", "grid_dbbib.txt")).read_text().strip()
assert len(FAED) == 570 and len(DBBI69) == 69 and len(DBBI91) == 91

SCRATCH = os.path.join(OGDIR, "tmp", "free23_cands.txt")

NOVEL = {k: v for k, v in ALPHAS.items() if not k.startswith("control")}


def top2(stream):
    from collections import Counter
    return [c for c, _ in Counter(stream).most_common(2)]


def interpreter_permutations(stream, e1, e2, lo, hi):
    """All perms sending top2(stream) onto {e1,e2}; other 7 letters -> the 7
    non-escape digits in lo..hi. Returns list of translate tables (bytes)."""
    t2 = top2(stream)
    others = [c for c in "abcdefghi" if c not in t2]
    nonesc = [dd for dd in range(lo, hi + 1) if dd not in (e1, e2)]
    assert len(nonesc) == 7, (lo, hi, e1, e2, nonesc)
    tables = []
    for a, b in ((t2[0], t2[1]), (t2[1], t2[0])):
        for rest in itertools.permutations(others):
            tbl = bytearray(range(256))
            tbl[ord(a)] = ord(str(e1))
            tbl[ord(b)] = ord(str(e2))
            for ch, dd in zip(rest, nonesc):
                tbl[ord(ch)] = ord(str(dd))
            tables.append(bytes(tbl))
    return tables


def stranslate(stream: str, tbl: bytes) -> str:
    return stream.translate(tbl)


def clean(pt: str) -> bool:
    return "?" not in pt and 8 <= len(pt) <= 2000


def emit(cands: set, pt: str) -> None:
    cands.add(pt)
    cands.add(pt.lower())
    cands.add(pt.upper())
    cands.add(pt[::-1])


def stage1() -> None:
    t0 = time.time()
    alphas = dict(ALPHAS)
    payloads = {"faed": FAED, "dbbi69": DBBI69, "dbbi91": DBBI91}
    dec = make_fast_decoder(1, 4)
    cands = set()
    forms = 0
    for pname, payload in payloads.items():
        perms = interpreter_permutations(payload, 1, 4, 0, 8) + \
                interpreter_permutations(payload, 1, 4, 1, 9)
        print(f"[s1] {pname} top2={top2(payload)}: {len(perms)} interpreter "
              f"tables", flush=True)
        for tbl in perms:
            ds = stranslate(payload, tbl)
            for alpha28 in alphas.values():
                pt = dec(ds, alpha28)
                forms += 1
                if clean(pt):
                    emit(cands, pt)
    with open(SCRATCH, "w") as f:
        f.writelines(c + "\n" for c in sorted(cands))
    print(f"[s1] {forms} decode forms -> {len(cands)} candidate forms "
          f"({time.time()-t0:.0f}s)", flush=True)


def stage2() -> None:
    t0 = time.time()
    dec = make_fast_decoder(1, 4)
    perms = interpreter_permutations(FAED, 1, 4, 0, 8)
    widths = {k: v for k, v in TRANS_WIDTHS.items() if v in (0, 15, 38)}
    oe_names = ["identity", "matrixsumlist_m9"]
    cands = set()
    forms = 0
    for tbl in perms:
        ds = stranslate(FAED, tbl)
        for oe_name in oe_names:
            if oe_name == "identity":
                ds2o = ds
            else:
                ds2o = over_undo(ds, OE_KEYS[oe_name], 9)
            for tw in widths.values():
                if tw == 0:
                    ds2 = ds2o
                else:
                    kk = [0] if oe_name == "identity" else OE_KEYS[oe_name]
                    order = sorted(range(tw),
                                   key=lambda i: (kk[i % len(kk)], i))
                    ds2 = col_undo(ds2o, tw, order)
                for alpha28 in NOVEL.values():
                    pt = dec(ds2, alpha28)
                    forms += 1
                    if clean(pt):
                        emit(cands, pt)
    with open(SCRATCH, "w") as f:
        f.writelines(c + "\n" for c in sorted(cands))
    print(f"[s2] {forms} decode forms -> {len(cands)} candidate forms "
          f"({time.time()-t0:.0f}s)", flush=True)


def make_fast_decoder(e1, e2):
    """Micro-optimized decode for fixed escapes; grid per alphabet."""
    e1s, e2s = str(e1), str(e2)

    def build(alpha28):
        ctol = build_grid(alpha28, e1, e2)
        row_single = [-1] * 10
        pairs = {}
        for code, ch in ctol.items():
            if len(code) == 2:
                pairs[code] = ch
            else:
                row_single[int(code)] = ord(ch)
        return pairs, row_single

    def dec(ds, alpha28):
        pairs, row_single = build(alpha28)
        out = []
        ap = out.append
        ps = pairs
        rs = row_single
        i = 0
        n = len(ds)
        while i < n:
            c = ds[i]
            if c == e1s or c == e2s:
                code = ds[i:i + 2]
                if code in ps:
                    ap(ps[code])
                    i += 2
                    continue
            v = rs[ord(c) - 48]
            ap(chr(v) if v >= 0 else "?")
            i += 1
        return "".join(out)

    return dec


def decode_lazy(ds, ctol, e1, e2):
    """Stacked rows; single-digit codes for non-escape digits ascending, plus
    e1+0..9 and e2+0..9 two-digit codes. Replicates certified decode() exactly.
    Retained for equivalence-checking only; sweeps use make_fast_decoder."""
    out = []
    i = 0
    n = len(ds)
    while i < n:
        c = ds[i]
        if c in (str(e1), str(e2)):
            code = ds[i:i + 2]
            if code in ctol:
                out.append(ctol[code])
                i += 2
                continue
        if c in ctol:
            out.append(ctol[c])
            i += 1
            continue
        out.append("?")
        i += 1
    return "".join(out)


def _oracle_feed(script: str) -> tuple[bool, float, int]:
    n = sum(1 for _ in Path(SCRATCH).read_text().splitlines(keepends=True))
    path = os.path.join(ROOT, "tools", script)
    t0 = time.time()
    found = False
    with open(SCRATCH) as inf:
        p = subprocess.Popen([sys.executable, path, "--stdin"],
                             stdin=inf, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True)
        out, _ = p.communicate()
    dt = time.time() - t0
    for line in out.splitlines():
        if line.startswith("MATCH"):
            found = True
            print(f"{script} MATCH: {line}", flush=True)
    print(f"{script}: {n} candidates, {dt:.0f}s ({n/dt:.0f}/s) "
          f"-> {'MATCH FOUND' if found else 'no match'}", flush=True)
    return found, dt, n


def both() -> int:
    import threading
    res = {}
    ts = [threading.Thread(target=lambda s=s: res.update({s: _oracle_feed(s)[0]}),
                           daemon=True)
          for s in ("oracle.py", "oracle_dualite.py")]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return 0 if any(res.values()) else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stage1"
    if cmd == "stage1":
        stage1()
    elif cmd == "stage2":
        stage2()
    elif cmd == "both":
        sys.exit(both())
    else:
        print(__doc__)
        sys.exit(2)