#!/usr/bin/env python3
"""Certified, re-runnable reproduction of the GSMG Bifid stage.

Reproduces from first principles the documented pipeline (tested.md 49/63/64):
  stored faed(570, trailing z stripped) --Bifid(period 570, keyed square
  DBIFHCEG, J dropped, row-major, ID square, half-split rows/cols)-->
  full 570-char plaintext (head BTCSEEDDEOEMC...) --position split-->
    * 0-indexed even positions (1-indexed odd)  = even_stream       (285)
    * 0-indexed odd  positions (1-indexed even) = odd_pre_reduction (285)
  odd_pre_reduction minus {I,O} (29 dropped positions) = object_256  (256)

Self-checks every output sha256 against the stored salphaseion-streams.json
values. Exits 0 (SELFCERT PASS) only if all hashes match exactly.

Usage: python3 tools/bifid_repro.py
"""

import hashlib
import json
import os
import sys
from pathlib import Path

ALPHABET = "DBIFHCEGAKLMNOPQRSTUVWXYZ"  # keyed 5x5, J dropped (25 cells)
PERIOD = 570  # full length; documented construction is not parametrically short


def build_grid(alphabet=ALPHABET):
    grid = [list(alphabet[i * 5:(i + 1) * 5]) for i in range(5)]
    pos = {}
    for r in range(5):
        for c in range(5):
            pos[grid[r][c]] = (r, c)
    return grid, pos


def bifid_decrypt(ct, period, grid, pos):
    """Bifid decipher over a 5x5 square, half-split rows/cols, per period block."""
    coords = [pos[ch] for ch in ct]
    combined = []
    for r, c in coords:
        combined.append(r)
        combined.append(c)
    plain = ""
    for start in range(0, len(combined), 2 * period):
        block = combined[start:start + 2 * period]
        h = len(block) // 2
        rs = block[:h]
        cs = block[h:]
        for k in range(h):
            plain += grid[rs[k]][cs[k]]
    return plain


def sh(obj):
    return hashlib.sha256(obj.encode()).hexdigest()


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    streams = json.loads(Path(os.path.join(base, "data", "finalpage-digit-streams.json")).read_text())
    stored = json.loads(Path(os.path.join(base, "data", "salphaseion-streams.json")).read_text())

    faed = streams["faed_570"].rstrip("z")
    mapped = "".join(
        {"a": "A", "b": "B", "c": "C", "d": "D",
         "e": "E", "f": "F", "g": "G", "h": "H", "i": "I"}[c] for c in faed)

    grid, pos = build_grid()
    full = bifid_decrypt(mapped, PERIOD, grid, pos)

    even = full[0::2]          # 0-indexed even = 1-indexed odd  -> even_stream
    odd_pre = full[1::2]       # 0-indexed odd  = 1-indexed even -> odd_pre_reduction

    dropped = []
    object256 = []
    for i, ch in enumerate(odd_pre):
        if ch in ("I", "O"):
            dropped.append(ch)
        else:
            object256.append(ch)
    dropped_s = "".join(dropped)
    object_s = "".join(object256)

    checks = {
        "plaintext_head": (full[:40], stored["plaintext_head"]),
        "even_stream": (even, stored["even_stream"]),
        "odd_pre_reduction": (odd_pre, stored["odd_pre_reduction"]),
        "object_256": (object_s, stored["object_256"]),
        "dropped_29": (dropped_s, stored["dropped_29"]),
    }

    ok = True
    for name, (mine, theirs) in checks.items():
        same = mine == theirs
        ok = ok and same
        print(f"{name:18} len={len(mine):4}  hash={sh(mine)[:12]}  match={same}")

    print()
    print(f"full plaintext head : {full[:40]}")
    print(f"stored head         : {stored['plaintext_head']}")
    if ok:
        print("SELFCERT PASS - all stored salphaseion-streams.json values reproduced exactly")
        return 0
    print("SELFCERT FAIL - divergence from stored values")
    return 1


if __name__ == "__main__":
    sys.exit(main())
