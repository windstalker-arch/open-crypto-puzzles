#!/usr/bin/env python3
"""interpreter_perm_sweep.py -- brute-force the interpreter alphabet mapping.

The unconfirmed crux is the a..i token -> value -> symbol reading of the two raw
streams.  Any 9-symbol interpreter alphabet is isomorphic to A..I via a fixed
bijection, so testing every permutation P of "ABCDEFGHI" (9! = 362880) covers
every possible 0-based/1-based/canonical token reading.  For each P we emit
    X = P[token] for dbbib, faed, dbbib+faed, faed+dbbib, both cases,
and stream each candidate straight into BOTH funded-gate oracles in parallel
(oracle.py small, oracle_dualite.py Dualite).  No candidate file on disk.

Generation is C-speed: each permutation becomes a 256-byte translate table.

Usage:
    python3 tools/interpreter_perm_sweep.py
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
DATA = json.loads(Path(os.path.join(BASE, "data",
                                   "finalpage-digit-streams.json")).read_text())
TOKEN_VAL = {chr(ord("a") + i): i for i in range(9)}

DBBIB = DATA["dbbib"].lower().encode()
FAED = DATA["faed_570"].rstrip("z").lower().encode()
FORMATS = {
    "dbbib": DBBIB,
    "faed": FAED,
    "dbbib+faed": DBBIB + FAED,
    "faed+dbbib": FAED + DBBIB,
}

PERMS = ["".join(p) for p in itertools.permutations("ABCDEFGHI")]
_LOCK = threading.Lock()
_PROGRESS = {"done": 0, "rc": None}


def table_for(perm: str, lower: bool) -> bytes:
    t = bytearray(range(256))
    for ch, v in TOKEN_VAL.items():
        t[ord(ch)] = ord(perm[v].lower() if lower else perm[v])
    return bytes(t)


def worker(script: str, case: str) -> int:
    """Feed `case` (upper or lower) of every permutation x format to one oracle."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script)
    lower = (case == "lower")
    p = subprocess.Popen(
        [sys.executable, path, "--stdin"],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    t0 = time.time()
    try:
        for n, perm in enumerate(PERMS, 1):
            table = table_for(perm, lower)
            for stream in FORMATS.values():
                p.stdin.write(stream.translate(table) + b"\n")
            if n % 5000 == 0:
                with _LOCK:
                    print(f"[{script} {case}] {n}/{len(PERMS)} perms "
                          f"({time.time() - t0:.0f}s)", flush=True)
        p.stdin.flush()
    finally:
        try:
            p.stdin.close()
        except BrokenPipeError:
            pass
    rc = p.wait()
    with _LOCK:
        _PROGRESS["rc"] = rc
        print(f"[{script} {case}] DONE exit={rc} "
              f"({time.time() - t0:.0f}s) {'MATCH' if rc == 0 else 'no match'}",
              flush=True)
    return rc


def main() -> int:
    total = len(PERMS) * len(FORMATS)
    print(f"{len(PERMS)} perms x {len(FORMATS)} formats x 2 cases "
          f"= {total * 2} oracle lines per gate", flush=True)
    scripts = ["oracle.py", "oracle_dualite.py"]
    threads = []
    specs = [(sc, cs) for sc in scripts for cs in ("upper", "lower")]
    for idx, (sc, cs) in enumerate(specs):
        t = threading.Thread(target=worker, args=(sc, cs), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(0.5)  # stagger process starts
    for t in threads:
        t.join()
    rc = _PROGRESS.get("rc")
    print(f"overall rc={rc} ({'MATCH FOUND' if rc == 0 else 'no match'})",
          flush=True)
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())