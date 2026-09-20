#!/usr/bin/env python3
"""late-198 rebuild (2026-09-17): matrix-sum battery reduction on the CERTIFIED
scan() union (scalar k*G + 02/03 x-coordinate decompression + gate point/h160),
with explicit skip accounting, injection spike test, and determinism fixed-point.

Reuses offchain_premise_battery.scan() verbatim (late-192 row, the same code that
was positively control-certified for the X-branch and h160-branch to fire on real
matches and stay silent otherwise).
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
import types
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offchain_premise_battery as OCB

FOLDER = Path(__file__).resolve().parent.parent
DATA = FOLDER / "data"
d = json.load(open(DATA / "finalpage-digit-streams.json"))
m = {"o": 0, "a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9}


def comm(s):
    return [m[c] for c in s]


g1 = comm(d["z_segment_1"]); g2 = comm(d["z_segment_2"])
dbb69 = comm(d["dbbib"]); dbb91 = comm(d["dbbib_91"])
faed = comm(d["faed_570"].rstrip("z"))
streams = {"g1": g1, "g2": g2, "dbb69": dbb69, "dbb91": dbb91, "faed": faed}


def facts(n):
    out = []
    for w in range(1, int(math.isqrt(n)) + 1):
        if n % w == 0:
            out.append((w, n // w))
    return out


def matrix_sums(digits, rows):
    cols = len(digits) // rows
    M = [digits[r * cols:(r + 1) * cols] for r in range(rows)]
    rs = [sum(r) for r in M]
    cs = [sum(M[r][c] for r in range(rows)) for c in range(cols)]
    return rs, cs, sum(digits)


# --- build every 32-byte reduction exactly as late-198 defined them (red(n):
# hex bytes -> first32 / last32 / sha256), for every matrix-sum construction ---
def hexb(v):
    if v == 0:
        return b"\x00"
    h = hex(v)[2:]
    return bytes.fromhex(h if len(h) % 2 == 0 else "0" + h)

intsrc = []          # (tag, int value)
count = 0
for sname, digs in streams.items():
    n = len(digs)
    for rows, cols in facts(n):
        rs, cs, tot = matrix_sums(digs, rows)
        tag = f"{sname}{rows}x{cols}"
        for jname, seq in (("r", rs), ("c", cs), ("r+c", rs + cs), ("c+r", cs + rs),
                           ("rt", rs + [tot]), ("ct", cs + [tot])):
            s = "".join(str(x) for x in seq)          # separatorless join (the int-readable forms)
            intsrc.append((f"{tag}:{jname}", int(s)))
            count += 1
        intsrc.append((f"{tag}:tot", tot))
        count += 1

cands = {}
for tag, v in intsrc:
    raw = hexb(v)
    if len(raw) >= 32:
        cands[f"{tag}:first32"] = raw[:32]
        cands[f"{tag}:last32"] = raw[-32:]
    else:
        cands[f"{tag}:padded"] = raw.rjust(32, b"\x00")[:32]
    cands[f"{tag}:sha256"] = hashlib.sha256(raw).digest()
print(f"union-candidate reductions: {len(cands)} (matrix combos: {count})")


# --- determinism fixed-point: hash the exact candidate set ---
fixed = hashlib.sha256(repr(sorted((t, b.hex()) for t, b in cands.items())).encode()).hexdigest()
print(f"FIXEDPOINT candidate-set sha256: {fixed}")


# --- injection spike: prove the full pipeline fires when a match exists ---
SPIKE_TAG = "SPIKE_INJECTED"
k2 = (2).to_bytes(32, "big")
_, sy = OCB.coincurve.PublicKey.from_valid_secret(k2).point()
spk = k2
h2 = OCB.h160((b"\x03" if sy & 1 else b"\x02") + k2)   # compressed h160 of key=2
orig_gates = dict(OCB.GATES)
OCB.GATES = {"g1": h2, "g2": "0" * 40}
spike_hits = []
OCB.scan(SPIKE_TAG, spk, spike_hits)
OCB.GATES = orig_gates
assert spike_hits == [SPIKE_TAG + "@xcoord"] or spike_hits == [SPIKE_TAG + "@scalar"], spike_hits
print(f"SPIKE OK: injected key=2 (h160 {h2}) fired through full scan(): {spike_hits}")


# --- the union run, with skip accounting ---
hits = []
stats = Counter()
t0 = time.time()
N = OCB.N; Pp = OCB.Pp
for tag, kb in cands.items():
    z = int.from_bytes(kb, "big")
    if not (0 < z < N):
        stats["scalar-skipped"] += 1
    if not (0 < z < Pp):
        stats["xcoord-skipped(>=p)"] += 1
    else:
        try:
            OCB.scan(tag, kb, hits)
            stats["scanned-union"] += 1
        except Exception:
            stats["scan-error"] += 1

print(f"[union] {len(cands)} candidates scanned, {time.time()-t0:.1f}s")
print("[union] stats:", dict(stats))
print(f"[union] HITS: {len(hits)}")
for h in hits:
    print("  HIT:", h)
