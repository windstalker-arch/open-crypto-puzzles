#!/usr/bin/env python3
"""cipher_battery.py -- late-273. Generic cipher battery harness.

One surface (a ciphertext stream, or the puzzle's built-in named streams) can
be pumped through EVERY registered cipher cell at once, deduped, and verified
against both funded gates. Each cell is a small function:

    cell(surface: str, params: dict) -> iterable[str]

over clean decoded candidate plaintexts. A battery run = {surface set} x
{cell set} x {param variants the cell declares}. Every run is certified:
  * --selftest injects, for EVERY cell, a synthetic plaintext P encoded under
    that cell's own convention; the harness must re-find P among the emitted
    forms through the exact same pipeline (no special-casing).
  * --both then feeds every unique candidate to oracle.py (small 1.25 BTC) and
    oracle_dualite.py (Dualite 3.75 BTC).

Surfaces offered: dbbib(69)/dbbib_91/faed(570)/z_segment_1/z_segment_2 from
data/finalpage-digit-streams.json, plus --string for any raw literal, and any
digit stream produced by the white-rabbit grid traversals (--grid).

Example:
    python3 tools/cipher_battery.py --selftest
    python3 tools/cipher_battery.py --both
    python3 tools/cipher_battery.py --string "dbbibfbhccbeg..." --only vic,interp10
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
from certified_vic import build_grid, decode  # noqa: E402
from leap_alphabet_sweep import ALPHAS  # noqa: E402

DATA = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())
GRID = json.loads(Path(os.path.join(ROOT, "data", "follow-white-rabbit-grid.json")).read_text())
BLUE = [tuple(c) for c in GRID["blue"]]
YELLOW = [tuple(c) for c in GRID["yellow"]]
CELLS_SRC = list(BLUE) + list(YELLOW)
SB = set(BLUE)
SCRATCH = os.path.join(os.path.expanduser("~"), "cipher_battery_cands.txt")

BUILTIN_SURFACES = {
    "dbbib69": DATA["dbbib"],
    "dbbib91": DATA["dbbib_91"],
    "faed570": DATA["faed_570"][:570],
    "zseg1": DATA["z_segment_1"],
    "zseg2": DATA["z_segment_2"],
}
CANON = {c: str(i + 1) for i, c in enumerate("abcdefghi")}
FREQ = "bag e i h f c d".replace(" ", "")


def grid_surfaces():
    from grid_route_battery import orderings, reductions
    out = {}
    for oname, order in orderings(CELLS_SRC, SB).items():
        for rname, fs in reductions(order).items():
            out[f"grid.{oname}.{rname}"] = fs
    return out


# ---------------------------------------------------------------- cipher cells
def cell_vic(surface, params):
    """VIC straddling-checkerboard decode under {alphas} x escapes."""
    for aname, alpha in ALPHAS.items():
        for e1, e2 in params.get("escapes", ((1, 4), (4, 1))):
            g = build_grid(alpha, e1, e2)
            num = [next((d for d, v in g.items() if v == ch), "?") for ch in surface]
            ds = "".join(num).replace("?", "")
            if not ds:
                continue
            pt = decode(ds, g, e1, e2)
            if "?" not in pt and 8 <= len(pt) <= 2000:
                yield pt


INTERP_ALPHAS = {"canon": {c: str(i + 1) for i, c in enumerate("abcdefghi")},
                 "pos": {c: str(i) for i, c in enumerate("abcdefghi")},
                 "freq": {c: str(i + 1) for i, c in enumerate(FREQ)}}


def _hex_ascii(n: int) -> str:
    h = format(n, "x")
    if len(h) % 2:
        h = "0" + h
    try:
        return bytes.fromhex(h).decode("ascii", "replace")
    except ValueError:
        return None


def cell_interp(surface, params):
    """Certified z-segment interpreter: letters -> digits, base-10 -> hex -> ASCII."""
    for aname, mp in (INTERP_ALPHAS.items() if not params.get("one") else [("one", INTERP_ALPHAS[params["one"]])]):
        digits = "".join(mp.get(c, c) for c in surface)
        if digits and digits.isdigit() and int(digits, 10) > 0:
            out = _hex_ascii(int(digits, 10))
            if out and 8 <= len(out) <= 2000:
                yield out


def cell_interp9(surface, params):
    """base-9 big-int -> hex -> ASCII (Wi77erd pre-z block reading)."""
    mp = INTERP_ALPHAS.get(params.get("one", "pos"), INTERP_ALPHAS["pos"])
    digits = "".join(mp.get(c, c) for c in surface)
    digits = "".join(c for c in digits if "0" <= c <= "8")
    if not digits:
        return
    try:
        n = int(digits, 9)
    except ValueError:
        return
    out = _hex_ascii(n)
    if out and 8 <= len(out) <= 2000:
        yield out


def cell_xor(surface, params):
    """Cycling byte-XOR (KyleBanks/HKTITAN family, late-270/272) hex renders."""
    for key in params.get("keys", ["KCQ", "matrixsumlist", "enter", "shabef", "salphasion"]):
        kb = key.encode()
        out = bytes(ord(c) ^ kb[i % len(kb)] for i, c in enumerate(surface))
        p = "" if not (out and all(32 <= x <= 126 for x in out)) else out.decode("ascii")
        if params.get("hex", True):
            yield out.hex()
        if p:
            yield p


CELLS = {
    "vic": cell_vic,
    "interp10": cell_interp,
    "interp9": cell_interp9,
    "xor": cell_xor,
}
DEFAULT_PARAMS = {"vic": {}, "interp10": {}, "interp9": {}, "xor": {}}


def encode_control(cellname: str, plaintext: str):
    """Plaintext -> surface-string under the cell's convention (for injection)."""
    if cellname == "vic":
        # cell_vic consumes LETTER surfaces and encodes internally via the board
        return plaintext
    if cellname == "interp10":
        dnum = str(int(plaintext.encode().hex(), 16))
        return "".join("abcdefghi"[int(d) - 1] for d in dnum)
    if cellname == "interp9":
        n = int(plaintext.encode().hex(), 16)
        ds = ""
        while n:
            n, r = divmod(n, 9)
            ds = str(r) + ds
        return "".join("abcdefghi"[int(d)] for d in (ds or "0"))
    if cellname == "xor":
        kb = b"KCQ"
        return "".join(chr(ord(c) ^ kb[i % 3]) for i, c in enumerate(plaintext))
    raise ValueError(cellname)


def gen(battery_surfaces, only=None, one_map_extra=None):
    cands = set()
    n_cell_forms = 0
    for sname, surface in battery_surfaces.items():
        for cname, cell in CELLS.items():
            if only and cname not in only:
                continue
            for form in cell(surface, DEFAULT_PARAMS[cname]):
                n_cell_forms += 1
                if form:
                    cands.add(form)
                    cands.add(form[::-1])
    return cands, n_cell_forms


def selftest():
    ok = True
    for cname in CELLS:
        P = {"vic": "BATTERYWITNESS", "interp10": "INTERPRET",
             "interp9": "PUZZLETEST", "xor": "XORTESTWITNESS"}[cname]
        s = encode_control(cname, P)
        cands, _ = gen({cname + ".wit": s}, only=[cname])
        forms = set(cands)
        if P not in forms and P[::-1] not in forms:
            return False, f"{cname}: control {P!r} not re-found"
    return True, "selftest OK (all cells re-find their injection control)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--both", action="store_true")
    ap.add_argument("--string", help="raw literal surface")
    ap.add_argument("--names", help="comma list of builtin surface names (default all raw streams)")
    ap.add_argument("--grid", action="store_true", help="add the grid traversal digit surfaces")
    ap.add_argument("--only", help="comma list of cells to run")
    args = ap.parse_args()

    if args.selftest:
        st, msg = selftest()
        print(msg)
        return 0 if st else 1

    surfaces = {}
    if args.string is not None:
        surfaces["arg"] = args.string
    if args.names:
        for n in args.names.split(","):
            n = n.strip()
            if n in BUILTIN_SURFACES:
                surfaces[n] = BUILTIN_SURFACES[n]
    if not surfaces:
        surfaces = dict(BUILTIN_SURFACES)
    if args.grid:
        surfaces.update(grid_surfaces())

    only = args.only.split(",") if args.only else None
    t0 = time.time()
    cands, n_forms = gen(surfaces, only=only)
    with open(SCRATCH, "w") as f:
        f.writelines(c + "\n" for c in sorted(cands))
    print(f"[cipher_battery] {len(surfaces)} surfaces x cells -> {n_forms} cell forms, "
          f"{len(cands)} unique candidates ({time.time()-t0:.0f}s) -> {SCRATCH}")
    if args.both:
        for prog in ("oracle.py", "oracle_dualite.py"):
            p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", prog), "--stdin"],
                               stdin=open(SCRATCH), capture_output=True, text=True)
            lines = [l for l in p.stdout.splitlines() if l.strip()]
            print(f"[cipher_battery] {prog}: {lines[-1] if lines else 'NO MATCH'}")
            if "MATCH" in p.stdout and "NO MATCH" not in p.stdout:
                print(p.stdout)
                return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())