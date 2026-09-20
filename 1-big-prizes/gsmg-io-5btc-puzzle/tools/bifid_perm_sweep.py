#!/usr/bin/env python3
"""bifid_perm_sweep.py -- joint decode-with-unknown-values attack.

The certified stage pipeline (tools/bifid_repro.py) maps tokens a..i onto
square cells of the keyed 5x5 "DBIFHCEG..." square by identity letter position
(== the canonical DBIFHCEGA value order).  That is exactly ONE bijection over
the 9! possible token->square-position assignments.  Here we parameterize that
assignment: for every bijection P (pos(token i) = P[i]), rebuild the mapped
ciphertext, run the exact certified bifid_decrypt, extract every certified
pipeline artifact (full plaintext, even/odd streams, I/O-dropped reduction,
dropped run), and stream all candidates into BOTH funded-gate oracles
(oracle.py small, oracle_dualite.py Dualite), both cases.

The identity-perm (CANON) output is self-checked against the stored
salphaseion-streams.json witness before the sweep runs.

Usage:
    python3 tools/bifid_perm_sweep.py
"""

from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "tools"))
from bifid_repro import build_grid

DATA = json.loads(Path(os.path.join(BASE, "data",
                                   "finalpage-digit-streams.json")).read_text())
STORED = json.loads(Path(os.path.join(BASE, "data",
                                     "salphaseion-streams.json")).read_text())

FAED = DATA["faed_570"].rstrip("z").lower().encode()
DBBIB = DATA["dbbib"].lower().encode()
TOKENS = b"abcdefghi"

_GRID, _POS = build_grid()
_PERMS = list(itertools.permutations(range(9)))

TOKEN_VAL = {chr(ord("a") + i): i for i in range(9)}
DB_SEQ = bytes(TOKEN_VAL[c] for c in DATA["dbbib"].lower())
FA_SEQ = bytes(TOKEN_VAL[c] for c in DATA["faed_570"].rstrip("z").lower())


def decode(assign: tuple, seq: bytes):
    """Full certified Bifid decode parameterized by the token->square-position
    bijection ``assign``.  No translate/dict: position of token i is assign[i],
    coordinates are (assign[i]//5, assign[i]%5), half-split rows/cols."""
    n = len(seq)
    comb = [0] * (2 * n)
    pos = 0
    for b in seq:
        a = assign[b]
        comb[pos] = a // 5
        comb[pos + 1] = a % 5
        pos += 2
    grid = _GRID
    full = "".join(grid[comb[k]][comb[k + n]] for k in range(n))
    even = full[0::2]
    odd_pre = full[1::2]
    odd = "".join(c for c in odd_pre if c not in ("I", "O"))
    dropped = "".join(c for c in odd_pre if c in ("I", "O"))
    return full, even, odd_pre, odd, dropped


def selfcheck():
    assign = (8, 1, 5, 0, 6, 3, 7, 4, 2)   # certified CANON token->position
    full, even, opre, odd, dropped = decode(assign, FA_SEQ)
    checks = [(full[:40], STORED["plaintext_head"]),
              (even, STORED["even_stream"]),
              (opre, STORED["odd_pre_reduction"]),
              (odd, STORED["object_256"]),
              (dropped, STORED["dropped_29"])]
    ok = all(a == b for a, b in checks)
    print(f"selfcheck (certified CANON assignment): {'PASS' if ok else 'FAIL'}")
    if not ok:
        for a, b in checks:
            print("  ", "M" if a == b else "X", a[:40], "!=", b[:40])
    return ok


def worker(script: str, case: str) -> int:
    path = os.path.join(BASE, "tools", script)
    lower = (case == "lower")
    p = subprocess.Popen([sys.executable, path, "--stdin"],
                         stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, text=True)
    t0 = time.time()
    try:
        for n, assign in enumerate(_PERMS, 1):
            for seq in (DB_SEQ, FA_SEQ):
                full, even, opre, odd, dropped = decode(assign, seq)
                for cand in (full, even, opre, odd, dropped):
                    if lower:
                        cand = cand.lower()
                    p.stdin.write(cand + "\n")
            if n % 2000 == 0:
                print(f"[{script} {case}] {n}/{len(_PERMS)} perms "
                      f"({time.time() - t0:.0f}s)", flush=True)
        p.stdin.flush()
    finally:
        try:
            p.stdin.close()
        except BrokenPipeError:
            pass
    rc = p.wait()
    print(f"[{script} {case}] DONE exit={rc} ({time.time() - t0:.0f}s) "
          f"{'MATCH' if rc == 0 else 'no match'}", flush=True)
    return rc


def main() -> int:
    if not selfcheck():
        return 2
    total = len(_PERMS) * 5 * 2
    print(f"{len(_PERMS)} perms x 5 artifacts x 2 streams x 2 cases "
          f"= {total} oracle lines per gate", flush=True)
    results: dict[str, int] = {}
    threads = []
    for sc in ("oracle.py", "oracle_dualite.py"):
        for i, cs in enumerate(("upper", "lower")):
            t = threading.Thread(
                target=lambda sc=sc, cs=cs: results.__setitem__(
                    f"{sc}:{cs}", worker(sc, cs)),
                daemon=True)
            t.start()
            threads.append(t)
            time.sleep(0.4)
    for t in threads:
        t.join()
    hit = [rc for rc in results.values() if rc == 0]
    print(f"overall: {results} "
          f"{'MATCH FOUND' if hit else 'no match'}", flush=True)
    return 0 if hit else 1


if __name__ == "__main__":
    raise SystemExit(main())