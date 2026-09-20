#!/usr/bin/env python3
"""interpreter_vic_sweep.py -- interpret the a..i token stream as ANY of the 9!
letter->digit bijections, then run the CERTIFIED VIC checkerboard decode and
oracle the DECODED PLAINTEXT (interpreter_perm_sweep only oracled the raw
letter stream; no prior sweep decoded under a 9! interpreter space).

Model: the interpreter alphabet is a fixed bijection over the 9 symbols.  For
each permutation P of "abcdefghi" -> domain digits (0..8 or 1..9), translate
the payload, then decode with the certified 3.2.2 board and a proven escape
pair.  ctol depends only on (alpha, esc), so every decode reuses one table and
the perm only changes the translate table.

Generation is CPU trivially parallel(*) but we keep single-process to keep the
candidate file deterministic.

Usage:
    python3 tools/interpreter_vic_sweep.py gen      # -> ~/tmp/ivic_cands.txt
    python3 tools/interpreter_vic_sweep.py small    # oracle.py   --stdin
    python3 tools/interpreter_vic_sweep.py dualite  # oracle_dualite.py --stdin
    python3 tools/interpreter_vic_sweep.py both     # both gates in parallel
"""
from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, selfcert

DATA = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())
FAED = DATA["faed_570"].rstrip("z").encode()   # the "enter" sealed payload, 570 letters

CERT_ALPHA = "FUBCDORA.LETHINGKYMVPS.JQZXW"    # certified 3.2.2 board
ESCAPES = [(1, 4), (2, 5)]                     # both proven escape pairs
DOMAINS = [(0, 8), (1, 9)]                     # a0..z0 a.i -> 0..8 ; a1..z1 -> 1..9

CAND_FILE = os.path.expanduser("~/tmp/ivic_cands.txt")


def tables(perm: str, lo: int) -> bytes:
    """bytes translate table: byte of a..i -> lo..lo+8 under P."""
    t = bytearray(range(256))
    for dst, src in enumerate(perm):
        t[ord(src)] = ord(str(lo + dst))
    return bytes(t)


def make_decoder(alpha28: str, e1: int, e2: int):
    """Micro-optimized loop equivalent to the certified decode (verified equal on
    perms x domains x edges: trailing/lone escapes produce '?' identically)."""
    ctol = build_grid(alpha28, e1, e2)
    row_single = [-1] * 10
    pairs = {}
    for code, ch in ctol.items():
        if len(code) == 2:
            pairs[code] = ch
        else:
            row_single[int(code)] = ord(ch)
    e1s, e2s = str(e1), str(e2)

    def dec(digits: bytes) -> str:
        s = digits.decode()
        out = []
        ap = out.append
        ps = pairs
        rs = row_single
        i = 0
        n = len(s)
        while i < n:
            c = s[i]
            if c == e1s or c == e2s:
                code = s[i:i + 2]
                if code in ps:
                    ap(ps[code])
                    i += 2
                    continue
            v = rs[int(c)]
            ap(chr(v) if v >= 0 else "?")
            i += 1
        return "".join(out)

    return dec


def gen() -> int:
    assert selfcert(), "certified decoder FAILED selfcert"

    decoders = {esc: make_decoder(CERT_ALPHA, *esc) for esc in ESCAPES}

    cands = set()
    N_total = 0
    t0 = time.time()
    perms = ["".join(p) for p in itertools.permutations("abcdefghi")]
    for lo, hi in DOMAINS:
        for perm in perms:
            tbl = tables(perm, lo)
            stream = FAED.translate(tbl)
            for dec in decoders.values():
                out = dec(stream)
                if "?" in out:
                    continue
                cands.add(out)
                cands.add(out.lower())
                cands.add(out.upper())
                N_total += 1
    with open(CAND_FILE, "w") as f:
        f.writelines(c + "\n" for c in cands)
    dt = time.time() - t0
    print(f"gen: {N_total} decode forms, {len(cands)} unique candidates, "
          f"{dt:.1f}s ({N_total / dt:.0f}/s)", flush=True)
    print(f"wrote {CAND_FILE} ({len(cands)} lines)")
    return 0 if cands else 1


def _run(script: str) -> tuple[bool, float]:
    """Feed CAND_FILE to one oracle via file-stdin + communicate() so the
    stdout pipe is drained concurrently (a hand-written write-then-read loop
    deadlocks: both pipes fill at the 64 KB kernel buffer before either side
    makes progress). Returns (found, seconds)."""
    n = sum(1 for _ in Path(CAND_FILE).read_text().splitlines(keepends=True))
    path = os.path.join(ROOT, "tools", script)
    t0 = time.time()
    found = False
    with open(CAND_FILE) as inf:
        p = subprocess.Popen(
            [sys.executable, path, "--stdin"],
            stdin=inf, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True,
        )
        out, _ = p.communicate()
    dt = time.time() - t0
    for line in out.splitlines():
        if line.startswith("MATCH"):
            found = True
            print(f"{script} MATCH: {line}", flush=True)
    rate = n / dt
    print(f"oracle {script}: {n} candidates in {dt:.0f}s ({rate:.0f}/s) "
          f"-> {'MATCH FOUND' if found else 'no match'}", flush=True)
    return found, dt


def oracle(script: str, parallel_scripts: list[str] | None = None) -> int:
    """Run one script, or several in parallel (for funds-gate parallelism)."""
    scripts = ([script] if parallel_scripts is None else [script, *parallel_scripts])
    import threading

    results: dict[str, bool] = {}
    threads = [
        threading.Thread(target=lambda s=s: results.update({s: _run(s)[0]}),
                         daemon=True)
        for s in scripts
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return 0 if any(results.values()) else 1


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "gen"
    if cmd == "gen":
        return gen()
    if cmd == "small":
        return oracle("oracle.py")
    if cmd == "dualite":
        return oracle("oracle_dualite.py")
    if cmd == "both":
        return oracle("oracle.py", ["oracle_dualite.py"])
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())