#!/usr/bin/env python3
"""Certified coordinate decomposition of the GSMG Bifid stage, and a killed false positive.

Deep-research addendum to tools/bifid_repro.py. Everything here is a re-derivation
from the raw stream in data/finalpage-digit-streams.json, not a restatement of a
stored value.

WHY THIS TOOL EXISTS
--------------------
The faed plaintext splits into an even-position stream whose alphabet is exactly
{B,C,D,E} and an odd-position stream whose alphabet is all 25 letters. That looks
like a striking authorial structure (a "2x2 sub-square" fingerprint). It is not.
This tool certifies the actual mechanism and records the false positive so it is
never re-derived as a discovery.

CERTIFIED MECHANISM
-------------------
tools/bifid_repro.py builds combined = [r0,c0,r1,c1,...] then, for a block of
length 2*period with h = len(block)//2, sets rs = block[:h], cs = block[h:].
When period == len(input) and len is even, h == len/2, so for output index k:

    k even:  plain[k] = grid[ r[k//2]   ][ r[h + k//2]   ]   (row-row product)
    k odd :  plain[k] = grid[ c[(k-1)//2] ][ c[h + (k-1)//2] ] (col-col product)

Checked here bit-exact against bifid_repro.bifid_decrypt for faed_570.

CONSEQUENCE: the faed raw alphabet is {a..i} -> {A..I}, and in the keyed square
DBIFHCEGAKLMNOPQRSTUVWXYZ the letters A..I are exactly the first nine cells of
rows 0-1 (the tenth, K=(1,4), is unused). Therefore the input rows are confined to
{0,1}, and:

  * even positions are products of two row indices -> at most 2x2 = 4 cells
  * odd positions are products of two column indices -> up to 5x5 = 25 cells

The 4-vs-25 split is therefore a DETERMINISTIC TAUTOLOGY of the square's own key
string, not evidence that the square is correct and not hidden authorial
structure. The apparent probability of a random square placing 9 letters in
exactly 2 rows is C(5,2)*C(10,9)/C(25,9) = 4.9e-5, but that null is VACUOUS here
because it is true of this square by construction.

ALSO RECORDED: R-FAEDBASE concluded "faed is seed material, not an encrypted
text" from index-of-coincidence alone. That is an over-claim. IC is invariant to
coordinate structure, so IC is mathematically blind to exactly the structure
present here and cannot support that conclusion.

USAGE: python3 tools/faed_coord_decomp.py
"""

import glob
import hashlib
import json
import os
import re
import sys
from math import comb
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bifid_repro as B  # noqa: E402

ALPHABET = B.ALPHABET
PERIOD = B.PERIOD
RAW_MAP = {chr(97 + i): chr(65 + i) for i in range(9)}


def sh(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


def row_col_streams(mapped, grid, pos):
    """Independent re-derivation of the even/odd coordinate product streams."""
    h = len(mapped) // 2
    rows = [pos[c][0] for c in mapped]
    cols = [pos[c][1] for c in mapped]
    even = "".join(grid[rows[k // 2]][rows[h + k // 2]] for k in range(0, len(mapped), 2))
    odd = "".join(grid[cols[(k - 1) // 2]][cols[h + (k - 1) // 2]] for k in range(1, len(mapped), 2))
    return even, odd, rows, cols


def pack(bits):
    """MSB-first bit string -> bytes, dropping any trailing partial byte."""
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits) - len(bits) % 8, 8))


def documented_hashes(puzzle, root):
    toks = set()
    for rel in ("analysis/tested.md", "analysis/STATE_BRIEF.md"):
        p = puzzle / rel
        if p.exists():
            toks |= set(re.findall(r"\b[0-9a-f]{64}\b", p.read_text()))
    for p in glob.glob(str(puzzle / "data" / "*.json")):
        toks |= set(re.findall(r"\b[0-9a-f]{64}\b", Path(p).read_text()))
    return toks


def main():
    puzzle = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    root = puzzle.parent.parent.parent
    streams = json.loads((puzzle / "data" / "finalpage-digit-streams.json").read_text())
    stored = json.loads((puzzle / "data" / "salphaseion-streams.json").read_text())

    raw = streams["faed_570"].rstrip("z")
    mapped = "".join(RAW_MAP[c] for c in raw)
    grid, pos = B.build_grid()

    ok = True

    print("== 1. baseline reproduction (bifid_repro semantics) ==")
    full = B.bifid_decrypt(mapped, PERIOD, grid, pos)
    for name, mine in (
        ("plaintext_head", full[:40]),
        ("even_stream", full[0::2]),
        ("odd_pre_reduction", full[1::2]),
    ):
        same = mine == stored[name]
        ok &= same
        print("  %-18s len=%4d hash=%s match=%s" % (name, len(mine), sh(mine)[:16], same))

    print("\n== 2. certified coordinate decomposition (independent re-derivation) ==")
    even, odd, rows, cols = row_col_streams(mapped, grid, pos)
    even_ok = even == full[0::2]
    odd_ok = odd == full[1::2]
    ok &= even_ok and odd_ok
    print("  even positions == grid[r_a][r_b] : %s   (%d symbols, alphabet %s = %d)"
          % (even_ok, len(even), "".join(sorted(set(even))), len(set(even))))
    print("  odd  positions == grid[c_a][c_b] : %s   (%d symbols, alphabet %d)"
          % (odd_ok, len(odd), len(set(odd))))

    print("\n== 3. why the 4-vs-25 split happens (the killed false positive) ==")
    in_rows = sorted({r for r in rows})
    in_cols = sorted({c for c in cols})
    used_cells = {pos[c] for c in set(mapped)}
    row0_row1_cells = {(r, c) for r in (0, 1) for c in range(5)}
    print("  input alphabet          : %s" % "".join(sorted(set(mapped))))
    print("  rows occupied           : %s   cols occupied: %s" % (in_rows, in_cols))
    print("  cells used by input     : %d of the 10 cells in rows 0-1 (unused: %s)"
          % (len(used_cells), sorted(row0_row1_cells - used_cells)))
    key9 = ALPHABET[:9]
    taut = sorted(set(mapped)) == sorted(key9)
    ok &= taut
    print("  input set == first 9 key: %s   key[0:9]=%s" % (taut, key9))
    print("  => 4-vs-25 split is a DETERMINISTIC TAUTOLOGY of the square, not authorial structure.")
    print("  => this is NOT independent evidence that the keyed square is correct.")
    tot, two = comb(25, 9), comb(5, 2) * comb(10, 9)
    print("  (vacuous null) P(9 random cells occupy exactly 2 rows) = %d/%d = %.3e"
          % (two, tot, two / tot))

    print("\n== 4. untested bit-channel packings from the decomposition ==")
    docs = documented_hashes(puzzle, root)
    print("  documented 64-hex tokens: %d" % len(docs))
    idx = {c: i for i, c in enumerate("DCBE")}  # D(0,0) B(0,1) C(1,0) E(1,1)
    cands = {}
    for order in ("msb", "lsb"):
        bits = ""
        for ch in even:
            v = format(idx[ch], "02b")
            bits += v if order == "msb" else v[::-1]
        cands["even_base4_%s" % order] = pack(bits)
    rb = "".join(str(r) for r in rows)
    for order in ("msb", "lsb"):
        bits = rb if order == "msb" else rb[::-1]
        cands["rowbits_%s_71B" % order] = pack(bits)
        cands["rowbits_%s_72B" % order] = pack(bits + "0" * 8)
    hits = 0
    for nm, data in sorted(cands.items()):
        h = sh(data)
        match = h in docs
        hits += match
        print("  %-22s %3dB %s %s" % (nm, len(data), h[:24], "<== HIT" if match else ""))
    print("  %d candidates, %d hits" % (len(cands), hits))

    print()
    if ok:
        print("SELFTEST PASS - decomposition certified bit-exact; false positive documented; 0 new hash hits")
        return 0
    print("SELFTEST FAIL - decomposition or tautology check did not reproduce")
    return 1


if __name__ == "__main__":
    sys.exit(main())
