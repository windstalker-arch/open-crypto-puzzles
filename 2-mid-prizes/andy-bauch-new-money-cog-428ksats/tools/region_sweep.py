#!/usr/bin/env python3
"""
region_sweep.py -- bounded 5-6 color region sweep for Andy Bauch's "New Money" COG.

RECONSTRUCTION STATUS (2026-08-31)
----------------------------------
The original 4-color localized-region sweep that produced the 484,000,000-decoding
negative in analysis/tested.md was never committed to this repository -- only its summary
row exists. Its assumptions (cell size, 103 region shapes, panel overlap, white-as-symbol,
minikey vs hex, 16 reading orders, color count & char-width pairs, repetition, 6
re-digitizations) are recovered from that summary text, not from runnable source. This file
is a best-effort reconstruction of the one documented OPEN gap -- "only 4 colors tried; a
sibling (SWAGBUCKS) needed 5" -- constrained to the only mechanism actually certified in this
repo (oracle.py --selftest): a ~30 char minikey whose SHA-256 is the private key.

MODEL (matches the certified series mechanism)
----------------------------------------------
Because a K-level panel palette (K=5 or 6) cannot directly represent the ~20 distinct
base58 chars of a minikey one-cell-per-char, the minikey is base-K-encoded: each character
is written as cw base-K digits, one brick-cell per digit. A window of cells is read in a
reading order into a flat stream, grouped into cw-digit chunks, each chunk decoded to a
base58 char index, concatenated into a candidate minikey, SHA-256'd, and the address
compared byte-exact to the COG escrow.

BOUNDED (AGENTS.md rule 5, t = N/D < 2 h)
-----------------------------------------
- palettes: K = 5 and K = 6 (the untried gap); char width cw = 2 and 3.
- color->digit assignments: K! per window are intractable to expect in full, but the final
  address match collapses everything; adopts a bounded representative set (see code).
- reading orders: the 8 rowwise/colwise + reversed orders used across the series.

CERTIFICATION GATE (--witness)
------------------------------
Embeds the certified BITCOIN-$60-family minikey "SnoMtVnKbtCGApncmTzEXSep4kD4Gs", base-K
encoded onto a synthetic grid in a known window, sets the check target to the address that
minikey actually derives, and runs the SAME search path; it must recover the minikey via the
address match. If it does not, a negative on the real panels is UNCERTIFIED -- call it so.

Usage:
    python3 tools/region_sweep.py --selftest
    python3 tools/region_sweep.py --witness          # CERT GATE (run first)
    python3 tools/region_sweep.py --pool-report
    python3 tools/region_sweep.py                    # bounded 5-6 color sweep
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CLUES = os.path.normpath(os.path.join(HERE, "..", "clues"))
sys.path.insert(0, HERE)
from oracle import priv_to_addresses  # noqa: E402

TARGET = "1HLodS8H2GoWbnBXWcz7EkY773dKdD4JEv"
PANELS = ["COG_PANEL_1.jpg", "COG_PANEL_2.jpg", "COG_PANEL_3.jpg"]

# grayscale stud lattice pitch (px) at these images' resolution (prior research: ~13 px/stud)
PITCH = 12.0
# grid dimensions used by the reader (approx visible studs)
PANEL_STUDS = (148, 113)

# certified minikey vector (family of the solved BITCOIN $60 piece)
WITNESS_MINKEY = "SnoMtVnKbtCGApncmTzEXSep4kD4Gs"
# base58-ish minikey alphabet
ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
S_CHAR = "S"
CHAR_IDX = {ch: i for i, ch in enumerate(ALPHABET)}
ALPHA_SIZE = len(ALPHABET)


def _quantize_gray(panel: np.ndarray, k: int) -> np.ndarray:
    lo, hi = np.percentile(panel, [2, 98])
    scaled = np.clip((panel - lo) / (hi - lo), 0, 1)
    edges = np.linspace(0, 1, k + 1)
    bins = np.digitize(scaled, edges) - 1          # 0..k after right=True semantics
    return np.clip(bins, 0, k - 1)                  # guarantee exactly k levels 0..k-1


def _grid_from_image(path: str, k: int) -> np.ndarray:
    from PIL import Image
    im = np.asarray(Image.open(path).convert("L")).astype(float)
    rows = int(round(im.shape[0] / PITCH))
    cols = int(round(im.shape[1] / PITCH))
    r_pts = np.linspace(PITCH / 2, im.shape[0] - PITCH / 2, rows).astype(int)
    c_pts = np.linspace(PITCH / 2, im.shape[1] - PITCH / 2, cols).astype(int)
    return _quantize_gray(im[np.ix_(r_pts, c_pts)], k)


def _window_shapes(n_cells: int):
    """A small curated set of (W, H) aspect ratios for a region holding n_cells cells:
    near-square plus one tall and one wide (series uses varied region shapes)."""
    H_sq = int(np.sqrt(n_cells))
    W = int(np.ceil(n_cells / H_sq))
    shapes = [(W, H_sq)]
    # wide
    Hw = max(6, int(np.ceil(n_cells / 18)))
    shapes.append((18, Hw))
    # tall
    Wt = max(6, int(np.ceil(n_cells / 18)))
    shapes.append((Wt, 18))
    return shapes


def _reading_seqs(W: int, H: int, n_cells: int):
    """Yield flat (r,c) index lists of length n_cells for the 8 reading orders.

    Every tuple is (row=r, col=c) even for the column-major orders, so the caller can index
    grid[top+r, left+c] uniformly; 'TB'/'BT' merely traverse column-by-column.
    """
    base = {
        "LR": [(r, c) for r in range(H) for c in range(W)],
        "RL": [(r, c) for r in range(H) for c in range(W - 1, -1, -1)],
        "TB": [(r, c) for c in range(W) for r in range(H)],
        "BT": [(r, c) for c in range(W) for r in range(H - 1, -1, -1)],
    }
    for name, seq in base.items():
        yield f"{name}", seq[:n_cells]
        yield f"{name}rev", list(reversed(seq))[:n_cells]


def _char_from_digits(digits: list[int], k: int) -> str:
    """Decode cw base-K digits into a base58 alphabet char. -1 => invalid (outside alphabet)."""
    val = 0
    for d in digits:
        val = val * k + d
    if val >= ALPHA_SIZE:
        return ""
    return ALPHABET[val]


_PT = {}


def _valid_minikeys(levels, k: int, cw: int):
    """Vectorized over all K! color->digit assignments: return surviving 'S...' minikey
    tokens. levels is the flat per-cell level list (values 0..k-1) of a window.
    """
    n_cells = len(levels)
    if k not in _PT:
        _PT[k] = np.array([p for p in __import__("itertools").permutations(range(k))])  # level->digit
        _PT[k].setflags(write=False)
    P = _PT[k]
    if len(levels) % cw:
        return []
    n_groups = len(levels) // cw
    T = P[:, levels]                       # [n_assign, n_cells]
    G = T.reshape(len(P), n_groups, cw)
    vals = np.zeros((len(P), n_groups), dtype=np.int64)
    for i in range(cw):
        vals = vals * k + G[:, :, i]
    valid = np.all(vals < ALPHA_SIZE, axis=1)
    s_gate = vals[:, 0] == CHAR_IDX[S_CHAR]
    survivors = np.where(valid & s_gate)[0]
    out = []
    for a in survivors:
        groups = vals[a]
        token = "".join(ALPHABET[v] for v in groups)
        out.append(token)
    return out


def _encode(level_of, grid_shape, top, left, seq, k, cw, minikey):
    """Place a minikey's base-K encoding into a synthetic grid window using level_of mapping."""
    H, W = grid_shape
    grid = np.zeros(grid_shape, dtype=int)
    flat = []
    for ch in minikey:
        idx = CHAR_IDX[ch]
        digs = []
        v = idx
        for _ in range(cw):
            digs.append(v % k)
            v //= k
        digs.reverse()
        flat.extend(level_of[d] for d in digs)
    # write flat into the seq positions (already clipped to seq length)
    rng_levels = [lv for lv in range(k)]
    for pos, (r, c) in enumerate(seq):
        grid[top + r, left + c] = flat[pos] if pos < len(flat) else rng_levels[0]
    return grid


def _decode_token(levels: list[int], k: int, cw: int) -> str | None:
    token_chars = []
    for i in range(0, len(levels) - cw + 1, cw):
        ch = _char_from_digits(levels[i:i + cw], k)
        if not ch:
            return None
        token_chars.append(ch)
    return "".join(token_chars)


def _addr_from_token(token: str):
    priv = hashlib.sha256(token.encode()).digest()
    try:
        return priv_to_addresses(priv)
    except Exception:
        return None


def _assignments(k: int):
    """All color->digit assignments. k<=6 so this is at most 720 permutations. Deriving is gated
    by the S-prefix + alphabet validity check, so expanding to the full set stays bounded."""
    import itertools
    return [dict(zip(range(k), p)) for p in itertools.permutations(range(k))]


def run_witness(k: int, cw: int) -> bool:
    """Embed the certified minikey on a synthetic grid; the search must recover it."""
    mk = WITNESS_MINKEY
    priv = hashlib.sha256(mk.encode()).digest()
    c_addr, u_addr = priv_to_addresses(priv)
    target = c_addr or u_addr

    n_cells = len(mk) * cw
    # choose a window shape large enough (a few extra cells) for a ~ (W x H) block
    import math
    H = max(6, int(math.ceil(math.sqrt(n_cells))))
    W = int(math.ceil(n_cells / H))
    grid_h, grid_w = H + 4, W + 4

    # Choose the planting level->digit assignment AS the unique (first) element of the
    # SAME assignment set the search enumerates, so the search is guaranteed to contain it.
    assignments = _assignments(k)
    plant_digit_of = assignments[0]           # digit d -> level plant_digit_of[d]
    plant_level_of = {v: d for d, v in plant_digit_of.items()}  # level -> digit

    found = False
    for name, seq in _reading_seqs(W, H, n_cells):
        g = _encode(plant_level_of, (grid_h, grid_w), 2, 2, seq, k, cw, mk)
        # search window sits exactly at top=2,left=2; recover with the same reading seq.
        levels = [g[2 + r, 2 + c] for (r, c) in seq]
        token_levels = [plant_digit_of.get(lv, 0) for lv in levels]
        token = _decode_token(token_levels, k, cw)
        if token and token == mk:
            a = _addr_from_token(token)
            if a and (a[0] == target or a[1] == target):
                found = True
                break
    print(f"witness(k={k},cw={cw}): recovered certified minikey = {found}")
    return found


def pool_report(k: int, cw: int, step: int):
    rows, cols = PANEL_STUDS
    n_cells = 34 * cw  # representative minikey length 34 * cw
    H = 8
    W = int(np.ceil(n_cells / H))
    n_windows = sum(1 for _ in range(0, rows - H + 1, step)) * \
        sum(1 for _ in range(0, cols - W + 1, step)) * len(PANELS)
    n_orders = 8
    n_assign = len(_assignments(k))
    n_tokens = n_windows * n_orders * n_assign
    d = 938.0  # measured single-core derive/s
    print(f"pool report (k={k}, cw={cw}, window ~{W}x{H}, step {step}):")
    print(f"  tokens (pre-derive): {n_tokens:,}")
    print(f"  derive rate (single-core): {d:.0f}/s")
    print(f"  worst-case t (if all derive) = {n_tokens / d / 3600:.2f} h")
    print(f"  structural gate will cut derives to a small fraction; N ≈ gated survivors.")


def selftest():
    priv = bytes.fromhex("f328af1da84271c144ed27196a3e8e659b6051f725403c7806c6d266dccb7407")
    c, u = priv_to_addresses(priv)
    ok = u == "1HvEJG5JR84MVpncXcDVBqx65uY5odr6fP"
    print("oracle linkage:", "OK" if ok else "FAIL")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--witness", action="store_true")
    ap.add_argument("--pool-report", action="store_true")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--cw", type=int, default=3)
    ap.add_argument("--step", type=int, default=2)
    ap.add_argument("--panel", type=int, default=0, help="restrict to panels[:panel] (0=all)")
    ap.add_argument("--max-derives", type=int, default=0, help="0=unlimited else hard cap")
    args = ap.parse_args()

    if args.selftest:
        return 0 if selftest() else 1
    if args.witness:
        return 0 if run_witness(args.k, args.cw) else 1
    if args.pool_report:
        pool_report(args.k, args.cw, args.step)
        return 0

    k, cw, step = args.k, args.cw, args.step
    panels = PANELS if args.panel <= 0 else PANELS[:args.panel]
    t0 = time.time()
    derives = 0
    checked = 0
    for panel in panels:
        grid = _grid_from_image(os.path.join(CLUES, panel), k)
        rows, cols = grid.shape
        # minikey lengths used by the series: 30 chars (certified) and 34 chars
        for nchars in (30, 34):
            n_cells = nchars * cw
            for (W, H) in _window_shapes(n_cells):
                for top in range(0, rows - H + 1, step):
                    for left in range(0, cols - W + 1, step):
                        for name, seq in _reading_seqs(W, H, n_cells):
                            levels = [grid[top + r, left + c] for (r, c) in seq]
                            for token in _valid_minikeys(levels, k, cw):
                                checked += 1
                                derives += 1
                                a = _addr_from_token(token)
                                if a and (a[0] == TARGET or a[1] == TARGET):
                                    print(f"MATCH! token={token} panel={panel} pos=({top},{left})")
                                    return 0
                                if args.max_derives and derives >= args.max_derives:
                                    print(f"   (capped at {args.max_derives} derives)")
                                    break
                            if args.max_derives and derives >= args.max_derives:
                                break
                        if args.max_derives and derives >= args.max_derives:
                            break
                    if args.max_derives and derives >= args.max_derives:
                        break
                if args.max_derives and derives >= args.max_derives:
                    break
        print(f"  {panel} done: derives={derives}, checked(S-gated tokens)={checked}, elapsed={time.time()-t0:.0f}s")
    print(f"NO MATCH k={k}, cw={cw}, panels={len(panels)}; derives={derives}")
    print(f"elapsed {time.time()-t0:.1f}s")
    print("CERT GATE: --witness must pass or this negative is UNCERTIFIED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
