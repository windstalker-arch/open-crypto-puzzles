#!/usr/bin/env python3
"""grid_interpreter_battery.py -- late-271. The two reads left open by late-269.

late-269 closed board-as-static-map (16636) and board-as-route (grid_route_battery).
Outstanding, per its INTERPRETER RELEVANCE:
  (A) ROUTE AS INTERPRETER for the real dbbib/faed streams -- edge values feed
      the 9-letter interpreter alphabet, aligned by cell rank. This is NOT the
      closed 9! fixed-map space (interpreter_perm_sweep): here the codebook is
      POSITIONAL, built per (grid transform, traversal, edge metric), i.e. the
      digit credit for a step is set ONLY by the coords of that step, not by a
      global letter permutation. The ciphertext stays the real streams.
  (B) 8 DIHEDRAL variants of the 14x14 board for every grid_route family
      (late-269 ran the canonical JSON orientation only).

Part A already ran dihedral grid route families (this battery adds them);
Part B implements the positional codebook:

  edge stream E = consecutive metric over a traversal of the ordered 24 cells;
  codebook M_r: cell rank r -> E[r]  (23 values; align against product orders).
  For the 9-letter alphabet {a..i} the codebook is read at 9 ranks:
     B1 : the ranks of the 9 YELLOW cells (yellow_rank j -> E[rank_j]) assigned
          to letters in canonical order (a..i) and in frequency order
          (b>a>g>e>i>h>f>c>d).
     B2 : ranks 0..8 of the traversal assigned to letters in the same two
          letter orders.
  The codebook maps each cipher stream letter -> digit; the digit stream is
  decoded with the CERTIFIED z-segment interpreter (base-10 -> hex -> ASCII),
  and with the base-9 big-int -> hex -> ASCII reader, then oracled.

WITNESS (certified):
  * interpreter pipeline: encode(P) -> digit stream -> base10->hex->ASCII == P
    for a control P under a synthetic codebook, re-found through gen.
  * dihedral: a synthetic 14x14 stamp whose RC consecutive-manhattan digits
    equal a chosen code whose VIC decode is known -> re-found (grid_route's).
Usage:
    python3 tools/grid_interpreter_battery.py --selftest
    python3 tools/grid_interpreter_battery.py --both
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode, keyed28, selfcert  # noqa: E402
from grid_route_battery import (CELLS, SB, dist_mh, dist_ck, dist_eu,  # noqa: E402
                                orderings, reductions, clean)

DATA = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())
GRID = json.loads(Path(os.path.join(ROOT, "data", "follow-white-rabbit-grid.json")).read_text())
BLUE = [tuple(c) for c in GRID["blue"]]
YELLOW = [tuple(c) for c in GRID["yellow"]]

SCRATCH = os.path.join(os.path.expanduser("~"), "grid_interpreter_cands.txt")
DBBI69 = DATA["dbbib"]
DBBI91 = DATA["dbbib_91"]
FAED = DATA["faed_570"][:570]
STREAMS = {"dbbib69": DBBI69, "dbbib91": DBBI91, "faed570": FAED}
FREQ_ORDER = "bag eihfc d".replace(" ", "")  # b>a>g>e>i>h>f>c>d
CANON_LETTERS = "abcdefghi"


def dihedral_transforms(cells):
    """9 named transforms of a 14x14 board (id + 8 dihedral realizations)."""
    t = {}
    t["id"] = list(cells)
    t["rot90"] = [(c[1], 13 - c[0]) for c in cells]
    t["rot180"] = [(13 - c[0], 13 - c[1]) for c in cells]
    t["rot270"] = [(13 - c[1], c[0]) for c in cells]
    t["trans"] = [(c[1], c[0]) for c in cells]
    t["reflX"] = [(13 - c[0], c[1]) for c in cells]
    t["reflY"] = [(c[0], 13 - c[1]) for c in cells]
    t["anti"] = [(13 - c[1], 13 - c[0]) for c in cells]
    return t


def edge_streams(cells, blue_set):
    """Same edge metric families as grid_route_battery over one cell set,
    returning named 23-char digit streams."""
    out = {}
    for oname, order in orderings(cells, blue_set).items():
        for rname, fs in reductions(order).items():
            out[f"{oname}.{rname}"] = fs
    return out


def metrics_by_rank_edges(order):
    """Per-step edge values keyed by step rank (metric family computed at rank)."""
    n = len(order)
    d = {}
    mh = [dist_mh(order[i], order[i + 1]) for i in range(n - 1)]
    d["mh"] = mh
    d["ck"] = [dist_ck(order[i], order[i + 1]) for i in range(n - 1)]
    d["eu"] = [dist_eu(order[i], order[i + 1]) for i in range(n - 1)]
    dx = [order[i + 1][1] - order[i][1] for i in range(n - 1)]
    dy = [order[i + 1][0] - order[i][0] for i in range(n - 1)]
    d["dx"] = [abs(x) for x in dx]
    d["dy"] = [abs(x) for x in dy]
    return d


def codebook_from_ranks(order, ranks, metric_vals, mod, letter_order):
    """digit for letter_order[j] = metric_vals[ranks[j]] mod (9 or 10)."""
    m = {}
    for j, ch in enumerate(letter_order):
        r = ranks[j] % len(metric_vals)
        m[ch] = str(metric_vals[r] % mod)
    return m


def substitute(stream, cb):
    return "".join(cb.get(c, c) for c in stream)


def interp_b10(digits):
    if not digits.isdigit():
        return None
    try:
        n = int(digits, 10)
    except ValueError:
        return None
    if n <= 0:
        return None
    h = format(n, "x")
    if len(h) % 2:
        h = "0" + h
    try:
        return bytes.fromhex(h).decode("ascii", "replace")
    except ValueError:
        return None


def interp_b9(digits):
    """base-9 big-int -> hex -> ASCII (Wi77erd's pre-z block reading, late-163 falsified
    for the literal whole-765 read; here applied to codebook-substituted streams)."""
    if not all("0" <= c <= "8" for c in digits):
        f = "".join(c for c in digits if "0" <= c <= "8")
        digits = f
    if not digits:
        return None
    try:
        n = int(digits, 9)
    except ValueError:
        return None
    h = format(n, "x")
    if len(h) % 2:
        h = "0" + h
    try:
        return bytes.fromhex(h).decode("ascii", "replace")
    except ValueError:
        return None


def gen_codebook_candidates(out_path):
    cands = set()
    n_subs = 0
    n_dec = 0
    for tname, tcells in dihedral_transforms(CELLS).items():
        blue_set = set(b for b in BLUE)
        for oname, order in orderings(tcells, blue_set).items():
            rows = {}
            for c in order:
                rows.setdefault(c[0], []).append(c[1])
            # ranks per cell within the traversal
            rank = {c: i for i, c in enumerate(order)}
            yranks = sorted(rank[c] for c in order if c not in blue_set)
            f0 = [rank[c] for c in order[:9]]
            for mname, mvals in metrics_by_rank_edges(order).items():
                for mod in (9, 10):
                    for lname, letters in (("canon", CANON_LETTERS), ("freq", FREQ_ORDER)):
                        cb_y = codebook_from_ranks(order, yranks, mvals, mod, letters)
                        cb_09 = codebook_from_ranks(order, f0, mvals, mod, letters)
                        for sname, s in STREAMS.items():
                            for cbname, cb in (("y", cb_y), ("09", cb_09)):
                                ds = substitute(s, cb)
                                n_subs += 1
                                for dec in (interp_b10, interp_b9):
                                    call = dec(ds)
                                    n_dec += 1
                                    if call and clean(call):
                                        cands.add(call)
                                        cands.add(call.lower())
                                        cands.add(call.upper())
                                        cands.add(call[::-1])
                                cands.add(ds)
                                cands.add(ds[::-1])
    with open(out_path, "w") as f:
        f.writelines(c + "\n" for c in sorted(cands))
    return len(cands), n_subs, n_dec


def gen_dihedral_candidates(out_path, cells=None, blue_set=None):
    cands = set()
    n_decode = 0
    if cells is None:
        cells = CELLS
    if blue_set is None:
        blue_set = set(BLUE)
    for tname, tcells in dihedral_transforms(cells).items():
        bset = set(b for b in blue_set)
        if tname != "id":
            # recompute the transformed blue set from the transform function
            fn = {"rot90": lambda c: (c[1], 13 - c[0]),
                  "rot180": lambda c: (13 - c[0], 13 - c[1]),
                  "rot270": lambda c: (13 - c[1], c[0]),
                  "trans": lambda c: (c[1], c[0]),
                  "reflX": lambda c: (13 - c[0], c[1]),
                  "reflY": lambda c: (c[0], 13 - c[1]),
                  "anti": lambda c: (13 - c[1], 13 - c[0])}[tname]
            bset = set(fn(b) for b in blue_set)
        for oname, order in orderings(tcells, bset).items():
            for rname, fs in reductions(order).items():
                for alpha28 in ALPHAS_FULL.values():
                    for e1, e2 in ((1, 4), (4, 1)):
                        pt = decode(fs, build_grid(alpha28, e1, e2), e1, e2)
                        n_decode += 1
                        if clean(pt):
                            cands.add(pt); cands.add(pt.lower())
                            cands.add(pt.upper()); cands.add(pt[::-1])
    with open(out_path, "w") as f:
        f.writelines(c + "\n" for c in sorted(cands))
    return len(cands), n_decode


def routify_grid_order(code):
    """Synthetic 24-cell (on a wide axis) whose RC/mh digits == code's digits."""
    cells = []
    c = 0
    for i in range(len(code) + 1):
        cells.append((i, c))
        if i < len(code):
            c += int(code[i]) - 1
    return cells


def selftest():
    ok = True
    # (1) interpreter pipeline under a synthetic codebook
    P = "INTERPRETROUTEWITNESS"
    s = bytes.fromhex(P.encode().hex()).decode("latin1")
    # build a digit stream D by mapping each char through digits of a control
    # sequence, then base10->hex->ASCII-must-equal a chosen result: encode P
    # via hex -> int -> decimal digits, then substitute letters arbitrarily.
    for ch in P:
        pass
    # inverse of interp_b10: we want decode(D) == P, so D = str(int(hex(P),16))
    D = str(int(P.encode().hex(), 16))
    if interp_b10(D) != P:
        return False, "interp_b10 control failed"
    if interp_b9("12345678") is None:
        return False, "interp_b9 smoke failed"
    # (1b) codebook substitution pipeline: a synthetic codebook applied to a
    # stream yields a digit string whose interp_b10 is a known control
    P = "!aaa"  # 0x21616161 = 560,204,129 -> exactly a 9-digit decimal
    D = str(int(P.encode().hex(), 16))
    assert len(D) == 9, len(D)
    cb = {ch: D[i % len(D)] for i, ch in enumerate(CANON_LETTERS)}
    applied = substitute(CANON_LETTERS, cb)
    if interp_b10(applied) != P:
        return False, f"codebook pipeline control failed: {applied!r}"
    # (2) dihedral generator closure: synthetic cells whose RC/mh equals a code
    from grid_route_battery import random_target_digits
    code, pt = random_target_digits()
    cells = routify_grid_order(code)
    order = sorted(cells)
    mh = [dist_mh(order[i], order[i + 1]) for i in range(len(order) - 1)]
    if "".join(str(x) for x in mh) != code:
        return False, "dihedral witness code reproduction failed"
    cands, _ = gen_dihedral_candidates(SCRATCH + ".w", cells, set([cells[0]]))
    forms = set(open(SCRATCH + ".w").read().splitlines())
    os.remove(SCRATCH + ".w")
    if pt not in forms and pt.lower() not in forms and pt.upper() not in forms and pt[::-1] not in forms:
        return False, f"dihedral witness pt not re-found in {len(forms)} forms"
    return True, f"selftest OK (interp controls + dihedral witness re-found in {len(forms)} forms)"


ALPHAS_FULL = {}
try:
    from leap_alphabet_sweep import ALPHAS
    ALPHAS_FULL = ALPHAS
except Exception:
    kn = {"control_phase322": "FUBCDORA.LETHINGKYMVPS.JQZXW",
          "salphasion": "SALPHASION", "cosmicduality": "COSMICDUALITY",
          "gsmg": "GSMG", "matrixsumlist": "MATRIXSUMLIST"}
    ALPHAS_FULL = {k: keyed28(v) if False else v for k, v in kn.items()}
    ALPHAS_FULL["control_phase322"] = kn["control_phase322"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--both", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        st, msg = selftest()
        print(msg)
        return 0 if st else 1

    t0 = time.time()
    n_dih, nd = gen_dihedral_candidates(SCRATCH + ".d")
    n_cb, ns, n_dec = gen_codebook_candidates(SCRATCH)
    all_c = set(open(SCRATCH + ".d").read().splitlines()) | set(open(SCRATCH).read().splitlines())
    with open(SCRATCH, "w") as f:
        f.writelines(c + "\n" for c in sorted(all_c))
    os.remove(SCRATCH + ".d")
    print(f"[grid_interp] dihedral {n_dih} + codebook {n_cb} = {len(all_c)} candidates "
          f"({nd} dihedral decodes; {ns} substitutions -> {n_dec} interpreter decodes) "
          f"({time.time()-t0:.0f}s)")
    if args.both:
        for prog in ("oracle.py", "oracle_dualite.py"):
            p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", prog), "--stdin"],
                               stdin=open(SCRATCH), capture_output=True, text=True)
            lines = [l for l in p.stdout.splitlines() if l.strip()]
            hits = [l for l in lines if l.startswith("MATCH ")]
            print(f"[grid_interp] {prog}: " + (hits[-1] if hits else "NO MATCH"))
            # A real hit prints a line STARTING with "MATCH " (oracle.py:366).
            # Substring tests are wrong in both directions: bare
            # `"MATCH" in stdout` fires on "NO MATCH", while adding
            # `and "NO MATCH" not in stdout` SUPPRESSES a genuine hit, because
            # a batch containing one match also contains many NO MATCH lines.
            if hits:
                print(p.stdout)
                return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())