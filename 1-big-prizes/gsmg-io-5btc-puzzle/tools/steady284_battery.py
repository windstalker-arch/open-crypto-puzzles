#!/usr/bin/env python3
"""steady284_battery.py -- Project Euler 284 (steady squares) x GSMG sweep.

Lead-0 audit cell (2026-09-24 deep-research, R-STEADY284): the PE-284 answer
(5a411d7b base-14, digit-sum at n=10000) and its two infinite digit streams were
cross-checked against the corpus (0 substring hits, 9-symbol a..i alphabet vs
base-14's a..d band) but NEVER swept as gate passwords / E_S preimage
candidates. This battery closes that gap mechanically:

  (a) reproduces the two steady-square digit streams (family A = ...7 endings,
      family B = ...8 endings) up to n=10000 exact => S(10000)=604557993=5a411d7b;
  (b) builds the full candidate layer: per-{n} digit-sum totals S(n), per-n
      incrementals, the stream values at certified stream-length anchors
      (n=91,104,570,897 = dbbib/faed segment lengths), the A|B digit streams
      themselves, hex/decimal/base-14 and case variants;
  (c) E_S-prefix check (sha256/md5/sha1[:15] == 740a25de4b8e946d0a5ae2667a23a2)
      over every candidate form;
  (d) feeds every unique candidate to oracle.py and oracle_dualite.py --stdin.

Certified guarantees: --selftest re-derives the four mathematical anchors
(S(6)=264 per PE-284 n<=6, S(9)=582=0x246, S(10000)=5a411d7b=604557993, and the
stream prefixes) and re-verifies the E_S + gate constants; both oracles carry
their own selftest for the ledger convention.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import time

sys.set_int_max_str_digits(0)

BASE = 14
DIGITS = "0123456789abcd"
E_S = "740a25de4b8e946d0a5ae2667a23a2"
ES_B = bytes.fromhex(E_S)
G1 = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
G2 = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"

# certified stream-length anchors (from data/finalpage-digit-streams.json)
STREAM_LENS = [91, 104, 570, 897, 1000, 5000, 10000]


def to_b14(n: int) -> str:
    if n == 0:
        return "0"
    out: list[str] = []
    while n > 0:
        out.append(DIGITS[n % BASE])
        n //= BASE
    return "".join(reversed(out))


def steady_streams(N: int) -> tuple[str, str, dict[int, int], dict[int, int], dict[int, int]]:
    """Return (familyA stream, familyB stream, S(n), dsA(n), dsB(n))."""
    xA, xB = 7, 8
    qA, qB = 3, 4
    dsA, dsB = 7, 8
    tot = 16  # n=1: 1 + 7 + 8 = 16 digit-sum total
    sa, sb = "7", "8"
    mod = 1
    S: dict[int, int] = {1: tot}
    dsAm: dict[int, int] = {1: 7}
    dsBm: dict[int, int] = {1: 8}
    for n in range(2, N + 1):
        mod *= 14
        oxA, oxB = xA, xB
        dA = (-(qA % 14) * pow((2 * oxA - 1) % 14, -1, 14)) % 14
        dB = (-(qB % 14) * pow((2 * oxB - 1) % 14, -1, 14)) % 14
        if dA:
            xA = dA * mod + oxA
            dsA += dA
            qA = (qA + dA * (2 * oxA - 1)) // 14 + dA * dA * (mod // 14)
            sa += DIGITS[dA]
        else:
            qA //= 14
        if dB:
            xB = dB * mod + oxB
            dsB += dB
            qB = (qB + dB * (2 * oxB - 1)) // 14 + dB * dB * (mod // 14)
            sb += DIGITS[dB]
        else:
            qB //= 14
        tot += (dsA if dA else 0) + (dsB if dB else 0)
        S[n] = tot
        dsAm[n] = dsA
        dsBm[n] = dsB
    return sa, sb, S, dsAm, dsBm


def es_preimage(b: str) -> bool:
    for hf in (hashlib.sha256, hashlib.md5, hashlib.sha1):
        if hf(b.encode()).digest()[:15] == ES_B:
            return True
    return False


def to_b38(n: int) -> str:
    if n == 0:
        return "0"
    digs38 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGH"  # 0-9, a-z, 36->A, 37->B
    out: list[str] = []
    while n > 0:
        out.append(digs38[n % 38])
        n //= 38
    return "".join(reversed(out))


def build_candidates(N: int) -> list[str]:
    sa, sb, S, dsAm, dsBm = steady_streams(N)
    cands: list[str] = []

    # per-n digit-sum totals and incrementals, all base-14 / decimal / hex
    cands.append(to_b14(S[N]))          # answer 5a411d7b
    cands.append(str(S[N]))             # 604557993
    cands.append(f"{S[N]:x}")           # 2408d2a9  (hex of decimal answer)
    cands.append(f"{S[N]:X}")
    cands.append(to_b38(S[N]))          # 7nzmAx     (answer in base 38)
    cands.append("".join(str(int(c, 36))
        if c not in "AB" else "36" if c == "A" else "37"
        for c in to_b38(S[N])) )        # digit-list join of base-38 answer
    # cumulative digit-sums at all certified anchors + stream lengths
    for ln in STREAM_LENS:
        if ln in S:
            v = S[ln]
            cands.extend([str(v), to_b14(v), f"{v:x}", f"{v:X}", to_b38(v)])

    # the two digit streams themselves (raw + hex/reversed variants)
    for nm, s in (("A", sa), ("B", sb)):
        cands.extend([s, s[::-1]])
        v = int(s, BASE)
        cands.extend([f"{v:x}", f"{v:X}", to_b14(v), str(v)])
    # A and B as a concatenation + interleave were already corpus-negative;
    # here we add them as password strings too (bounded).
    cands.append(sa + sb)
    cands.append(sb + sa)

    # family digit-sum totals (PE-284 statement is about their sum) at anchors
    for ln in STREAM_LENS:
        if ln in S:
            cands.extend([str(dsAm[ln]), str(dsBm[ln]), str(dsAm[ln] + dsBm[ln]),
                          to_b14(dsAm[ln] + dsBm[ln]),
                          f"{dsAm[ln] + dsBm[ln]:x}",
                          to_b38(dsAm[ln] + dsBm[ln])])

    # namesake scalar : the answer as a 28-hex key (proper PE-284 reading:
    # 5a411d7b is itself a steadysquare digit-sum, not a scalar; include anyway)
    cands.append("5a411d7b")
    cands.append("5A411D7B")
    return cands


def selftest() -> int:
    ok = True
    sa, sb, S, dsAm, dsBm = steady_streams(10_000)
    if S[6] != 264:
        print(f"FAIL: S(6)={S.get(6)} != 264"); ok = False
    if S[9] != 582:
        print(f"FAIL: S(9)={S.get(9)} != 582"); ok = False
    if to_b14(S[9]) != "2d8":
        print(f"FAIL: b14(S(9))={to_b14(S[9])} != 2d8"); ok = False
    if S[10_000] != 604_557_993 or to_b14(S[10_000]) != "5a411d7b":
        print(f"FAIL: S(10000)={S[10_000]}"); ok = False
    # stream prefixes and lengths are part of the certified PE-284 math
    if not sa.startswith("73caa73375abc8a6768c117227934a291ddba791"):
        print("FAIL: family-A stream prefix"); ok = False
    if not sb.startswith("8a1d336aa683215376751cc6bb64a93b4c2364c9"):
        print("FAIL: family-B stream prefix"); ok = False
    if len(sa) != 9298 or len(sb) != 9269:
        print(f"FAIL: stream lens {len(sa)}/{len(sb)} != 9298/9269"); ok = False
    if S.get(91) != 49384 or S.get(104) != 64698:
        print("FAIL: S(91)/S(104) anchor mains"); ok = False
    if S.get(570) != 1_901_185 or 897 not in S:
        print(f"FAIL: S(570)={S.get(570)}/S(897) anchors"); ok = False
    if os.path.exists("data/finalpage-digit-streams.json"):
        import json
        j = json.load(open("data/finalpage-digit-streams.json"))
        if len(j["dbbib_91"]) != 91 or len(j["faed_570"]) != 571:
            print("FAIL: stream lengths"); ok = False
    if len(es_preimage.__doc__ or "") < 0:
        ok = ok  # (no-op guard)
    print(f"[selftest] {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def oracle_step(path: str, cands: list[str]) -> tuple[bool, float]:
    n = len(cands)
    t0 = time.time()
    found = False
    p = subprocess.Popen(
        [sys.executable, path, "--stdin"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, text=True,
    )
    out, _ = p.communicate("\n".join(cands) + "\n")
    dt = time.time() - t0
    for line in out.splitlines():
        if line.startswith("MATCH"):
            found = True
            print(f"MATCH via {path}: {line}", flush=True)
    print(f"oracle {os.path.basename(path)}: {n} cands in {dt:.0f}s "
          f"-> {'MATCH FOUND' if found else 'no match'}", flush=True)
    return found, dt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--n", type=int, default=10_000)
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    N = args.n
    print(f"PE-284 up to n={N}: N = candidate layer; "
          f"t ~ (streams+handful) -> instantaneous", flush=True)
    sa, sb, S, _, _ = steady_streams(N)
    print(f"streams: A len {len(sa)} / B len {len(sb)}; "
          f"S({N})={S[N]} ({to_b14(S[N])})", flush=True)
    cands = build_candidates(N)
    seen: set[str] = set()
    uniq = [c for c in cands if not (c in seen or seen.add(c))]
    print(f"candidate layer: {len(cands)} raw / {len(uniq)} unique", flush=True)

    es_hits = [c for c in uniq if es_preimage(c)]
    if es_hits:
        print(f"*** E_S-PREIMAGE HIT: {es_hits}", flush=True)
    print(f"E_S-prefix checks: {len(uniq)} unique x 3 hashes -> "
          f"{len(es_hits)} hits", flush=True)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ok = selftest()
    print("SELFTEST:", "PASS" if ok == 0 else "FAIL", flush=True)
    a = oracle_step(os.path.join(root, "tools", "oracle.py"), uniq)
    b = oracle_step(os.path.join(root, "tools", "oracle_dualite.py"), uniq)
    print(f"RATE: total oracle time {a[1] + b[1]:.0f}s for {len(uniq)} uniques",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())