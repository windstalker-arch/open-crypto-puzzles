#!/usr/bin/env python3
"""brainwallet_pass.py -- the third door's brainwallet dictionary pass.

WHAT THIS CLOSES. `analysis/tested.md` row ~:931 records the rockyou.txt pass on
the third door, both lock blobs and the gates as "still running when that session
closed and is not counted"; `analysis/leads.md` Note 41 (2026-09-12) finds the
8 rockyou-split chunks in `~/briefcase/chunk_00..07.txt` (14,344,391 lines) and
leaves a full file-level rerun "not scheduled". So a *certified* brainwallet pass
(SHA-256 construction) over the actual split dictionaries on the actual third door
(`1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9`, funded 2020-04-07, no OP_RETURN, no known
preimage) has NEVER been recorded. Lead 1 names it explicitly: "a GPU brainwallet
pass (SHA-256 construction) over large dictionaries". This device has no GPU, so
this is the CPU pass at the lead-1-corrected rate (R-COLORDOOR: 1,117 address
derivations/s/core) -- same construction, same target, honest about the engine.

CONSTRUCTIONS: exactly the two the lead singles out:
  sha256    key = sha256(line-bytes)          (the GPU-brainwallet construction)
  raw       key = int.from_bytes(line-bytes)  (CPU pass; lead: valid for <=32 B)
For each, the compressed AND uncompressed P2PKH address is derived (the CSV's own
rows use both forms) and compared against the third door, all other planted
addresses, and both funded gates.

The selftest re-derives the sha256 witnesses (causality, jacquefresco-sentence,
the 1GSMG1JC9 address) and the raw witness (gsmg.io/theseedisplanted) from the
CSV's verified rows, so a negative produced here is witnessed by construction.

Local only. No key is swept, nothing is broadcast.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import multiprocessing as mp
import os
import re
import sys
import time

import base58
from coincurve import PublicKey

SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

BASE = os.path.expanduser(
    "~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle")
CSV_PATH = os.path.join(BASE, "data", "planted-addresses.csv")
CHUNKS = [os.path.expanduser(f"~/briefcase/chunk_0{i}.txt") for i in range(8)]

GATES = {
    "small": "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "dualite": "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa",
}
THIRD_DOOR = "1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9"


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def hash160(d: bytes) -> bytes:
    return hashlib.new("ripemd160", sha256(d)).digest()


def p2pkh(priv_int: int, compressed: bool) -> str | None:
    if not 0 < priv_int < SECP256K1_ORDER:
        return None
    try:
        pub = PublicKey.from_valid_secret(priv_int.to_bytes(32, "big"))
    except Exception:
        return None
    return base58.b58encode_check(
        b"\x00" + hash160(pub.format(compressed))).decode()


# ------------------------------------------------------------------ targets

def load_targets() -> dict[str, str]:
    t = {}
    with open(CSV_PATH, newline="") as fh:
        for row in csv.DictReader(l for l in fh if not l.startswith("#")):
            t[row["address"]] = row["status"]
    t[THIRD_DOOR] = "third door (unmessaged, no known preimage)"
    for g, name in GATES.items():
        t[g] = f"funded gate ({name})"
    return t


# ------------------------------------------------------------------ witnesses

WITNESSES = [
    (b"causality", "1Jqq37KkZEt4F3Dt6qXdtyiMEFBBdawbkJ", "sha256", True),
    (b"jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
     "1K23RS1y2fnuZRkhw5nUpFr5Jk5WN11Zeq", "sha256", True),
    (b"1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
     "1GyT5WrLYpwFkuiVoPDJZa1Q6jtjbjuBff", "sha256", True),
    (b"gsmg.io/theseedisplanted", "148XH2YBmLr4oAJXQcG84FpNYoBmqnVPHQ",
     "raw", True),
]


def selftest() -> int:
    bad = 0
    for pre, want, cname, comp in WITNESSES:
        key = raw_int(sha256(pre)) if cname == "sha256" else raw_int(pre)
        got = p2pkh(key, comp)
        ok = got == want
        bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {cname:6s} {'c' if comp else 'u'} "
              f"{want}{'' if ok else f'  got {got}'}")
    print(f"SELFTEST {'PASS' if bad == 0 else 'FAIL'} ({len(WITNESSES)} witnesses)")
    return 1 if bad else 0


def raw_int(b: bytes) -> int:
    return int.from_bytes(b, "big")


# --------------------------------------------------------------- sweep worker

def sweep_range(args) -> tuple[int, str | None]:
    path, lo, hi, targets, const = args
    n = 0
    with open(path, "rb") as fh:
        for line in fh:
            if hi is not None and n >= hi:
                break
            if n < lo:
                n += 1
                continue
            n += 1
            raw = line.rstrip(b"\r\n")
            if not raw or len(raw) > 64:
                continue
            keys = ()
            if const in ("both", "sha256"):
                keys += (raw_int(sha256(raw)),)
            if const in ("both", "raw"):
                keys += (raw_int(raw),)
            for key in keys:
                for comp in (True, False):
                    a = p2pkh(key, comp)
                    if a in targets:
                        return n, a
    return n, None


def run(mode: str, limit: int | None, jobs: int) -> int:
    targets = load_targets()
    print(f"targets: {len(targets)} addresses "
          f"(third door {THIRD_DOOR} + planted + 2 funded gates)")
    ranges = []
    for path in CHUNKS:
        hi = limit if limit is not None else None
        ranges.append((path, 0, hi, set(targets), mode))
    print(f"work: {len(CHUNKS)} chunks (1 range each), {jobs} processes, "
          f"construction={mode}")
    t0 = time.time()
    done = 0
    hit = None
    with mp.Pool(jobs) as pool:
        for n, a in pool.imap_unordered(sweep_range, ranges):
            done += n
            if a:
                hit = a
                pool.terminate()
                break
    dt = time.time() - t0
    rate = done / dt if dt > 0 else 0.0
    print(f"[brainwallet] {done} lines swept, rate {rate:.0f} lines/s, "
          f"{dt:.0f}s")
    if hit:
        print(f"  MATCH  {hit}")
        return 1
    print("  0 MATCH against the third door, planted addresses, or either gate")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--limit", type=int, default=None,
                    help="cap lines-per-chunk (bench)")
    ap.add_argument("--jobs", type=int, default=mp.cpu_count())
    ap.add_argument("--const", choices=("both", "sha256", "raw"),
                    default="both", help="which construction(s) to sweep")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    return run(a.const, a.limit, a.jobs)


if __name__ == "__main__":
    sys.exit(main())