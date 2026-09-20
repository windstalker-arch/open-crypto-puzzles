#!/usr/bin/env python3
"""run_lt3_cpp.py -- bridge for the independent C++ re-implementation of the
late-70 "<3" positional-bitmask family (tools/bitmask/lt3_convert.cpp).

Pipeline:
  1. regenerate tools/bitmask/lt3_streams.txt from the certified JSON streams
  2. run the C++ converter (uses oliora/bitmask for byte packing)
  3. cross-check: the C++ packed-hex SET must equal the Python packer's set
     byte-for-byte (witness that the independent impl matches the sweep)
  4. expand each packed form to {hex, sha256(hex), sha256d(hex)} and run every
     X through BOTH funded gate oracles (small blob -> 1GSMG1JC9, Dualite
     cosmic blob -> 17ucy1K9); also run the kept/digits subsequence forms.
  5. report hits (expected 0; late-70 was already certified negative).
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time

TOOLS = os.path.expanduser("~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle/tools")
BM = TOOLS + "/bitmask"
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
from oracle import attempt as small_attempt
from oracle_dualite import attempt as dualite_attempt
from oracle_dualite import load_dualite_b64


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


MAPS = {
    "m_bi": dict(d=0, b=1, i=2, f=3, h=4, c=5, e=6, g=7, a=8, o=9),
    "m_hex": dict(o=0, a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, i=9),
    "m_nat": dict(a=0, b=1, c=2, d=3, e=4, f=5, g=6, h=7, i=8, o=9),
}


def load_streams() -> dict:
    fp = json.load(open(ROOT + "/data/finalpage-digit-streams.json"))
    sp = json.load(open(ROOT + "/data/salphaseion-streams.json"))
    return {
        "dbbib_69": fp["dbbib"],
        "dbbib_91": fp["dbbib_91"],
        "faed_570": fp["faed_570"][:-1],
        "even_stream": sp["even_stream"],
        "dropped_29": sp["dropped_29"],
        "z_segment_1": fp["z_segment_1"],
        "z_segment_2": fp["z_segment_2"],
    }


def py_pack_hex(toks: str, mapping: dict, rev: bool, lsb: bool) -> str:
    bits = [1 if mapping[t.lower()] < 3 else 0 for t in toks]
    seq = bits[::-1] if rev else bits
    out = bytearray()
    for i in range(0, len(seq), 8):
        b = 0
        for j, bit in enumerate(seq[i:i + 8]):
            if bit:
                b |= (1 << j) if lsb else (1 << (7 - j))
        out.append(b)
    return out.hex()


def main() -> None:
    dual_b64 = load_dualite_b64()
    streams = load_streams()

    with open(BM + "/lt3_streams.txt", "w") as f:
        for k, v in streams.items():
            f.write(f"{k}\t{v}\n")

    exe = BM + "/build/lt3_convert"
    raw = subprocess.run([exe, BM + "/lt3_streams.txt"],
                         check=True, capture_output=True, text=True).stdout

    ph = {}
    ss = []
    for line in raw.splitlines():
        parts = line.split("|")
        if parts[0] == "PH":
            _, mp, st, rev, lsb, hexv = parts
            ph[(mp, st, int(rev), int(lsb))] = hexv
        elif parts[0] == "SS":
            _, mp, st, label, d, val = parts
            ss.append((mp, st, label, d, val))

    expect = {(mp, st, rev, lsb): py_pack_hex(streams[st], MAPS[mp], rev, lsb)
              for mp in MAPS for st, toks in streams.items()
              for rev in (0, 1) for lsb in (0, 1)}
    assert ph == expect, "C++ packing diverges from Python packer!"
    print(f"PACKING CROSS-CHECK OK: {len(ph)} packed records identical "
          "(C++ oliora/bitmask == Python packer, byte-for-byte)")

    started = time.time()
    n = hits = 0
    for (mp, st, rev, lsb) in ph:
        for h in (ph[(mp, st, rev, lsb)],
                  sha256(bytes.fromhex(ph[(mp, st, rev, lsb)])).hex(),
                  sha256(sha256(bytes.fromhex(ph[(mp, st, rev, lsb)]))).hex()):
            for gate, attempt in (("small", small_attempt),
                                  ("dualite", lambda x: dualite_attempt(x, dual_b64))):
                n += 1
                ok, info = attempt(h)
                if ok:
                    hits += 1
                    print("HIT", gate, mp, st, rev, lsb, h, info)
    for mp, st, label, d, val in ss:
        for gate, attempt in (("small", small_attempt),
                              ("dualite", lambda x: dualite_attempt(x, dual_b64))):
            n += 1
            ok, info = attempt(val)
            if ok:
                hits += 1
                print("HIT", gate, mp, st, label, d, val, info)

    elapsed = time.time() - started
    print(f"oracle re-run: {n} attempts both gates in {elapsed:.1f}s -> "
          f"{hits} HITS")
    print("NO MATCH on either gate" if hits == 0 else f"{hits} HITS!")


if __name__ == "__main__":
    main()