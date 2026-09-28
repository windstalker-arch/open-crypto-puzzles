#!/usr/bin/env python3
"""xorencryption_steer.py -- late-270. STEER: "check ~/XOREncryption".

~/XOREncryption == KyleBanks/XOREncryption (MIT, 2013-2020; origin
https://github.com/KyleBanks/XOREncryption), the well-known "Simple XOR
Encryption/Decryption in any language" demo. Its primitive is a MULTI-KEY
CYCLING XOR: output[i] = input[i] ^ key[i % len(key)], canonical example key
=['K','C','Q'] encrypted over "kylewbanks.com". It has no puzzle content of its
own (generic tutorial repo); assessed against lead-0's question "is this the
tool/operation behind an unexplained object" by running the SAME primitive over
every currently-open digit surface and oracling the outputs against both funded
gates.

Surfaces (byte-exact puzzle data, data/finalpage-digit-streams.json):
  dbbib (69, image-verified), dbbib_91 (legacy), faed_570 (+trailing z),
  z_segment_1 (63), z_segment_2 (29).
Grid surfaces (data/follow-white-rabbit-grid.json, the late-267 static map):
  colour-bit serializations (blue=1/yellow=0, 9 orderings) and the route
  edge-digit streams (manhattan mod-9/mod-10 over the 9 orderings) reused as
  KEY material for the cycle-XOR over the letter streams, plus the colour
  serializations read as candidate answers themselves.

Key families for the cycle:
  A. literal KCQ family      : KCQ / kcq / QCK / CKQ / KC / KQ / CQ / KQCC etc.
  B. puzzle-token keys       : the decoded directives and page words used AS
       XOR keys (any-length cycle, XOREncryption allows any key length).
  C. grid key material       : colour-bit serializations + route digit streams
       (and reverses) as the cycling key over the real letter streams.
  D. digital-XOR interpreter : letters -> canon digits (a=1..i=9), cycle-XOR
       the DIGIT VALUES with a digit key (KCQ -> 11,3,17 -> mod-9/mod-10 form),
       then interpret output digits base-10 -> hex -> ASCII exactly like the
       certified z-segment decoder.

Candidate renderings of each XORd stream: raw-ascii (only if fully printable),
upper/lower/reversed, hex, big-int decimal, reversed-hex.

WITNESS (certified):
  * repo canonical vector  : cycle_xor("kylewbanks.com","KCQ") twice == original.
  * injection              : P="CYCLEXORWITNESS", key="matrixsumlist";
       F = cycle_xor(P, key) is threaded through the SAME generator and P is
       re-found among the emitted candidate forms.
Usage:
    python3 tools/xorencryption_steer.py --selftest
    python3 tools/xorencryption_steer.py --both
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from grid_route_battery import CELLS, SB, reductions  # noqa: E402
from grid_route_battery import orderings as grid_orderings  # noqa: E402

DATA = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())
GRID = json.loads(Path(os.path.join(ROOT, "data", "follow-white-rabbit-grid.json")).read_text())
BLUE = [tuple(c) for c in GRID["blue"]]
YELLOW = [tuple(c) for c in GRID["yellow"]]

SCRATCH = os.path.join(os.path.expanduser("~"), "xorencryption_cands.txt")

STREAMS = {
    "dbbib69": DATA["dbbib"],
    "dbbib91": DATA["dbbib_91"],
    "faed570": DATA["faed_570"][:570],
    "faed571": DATA["faed_570"],
    "zseg1": DATA["z_segment_1"],
    "zseg2": DATA["z_segment_2"],
}
CANON = {ch: str(i + 1) for i, ch in enumerate("abcdefghi")}
POS = {ch: str(i) for i, ch in enumerate("abcdefghi")}


def cycle_xor_bytes(b: bytes, key: str) -> bytes:
    kb = key.encode("utf-8")
    return bytes(x ^ kb[i % len(kb)] for i, x in enumerate(b))


def cycle_xor_raw(s: str, key: str) -> bytes:
    return cycle_xor_bytes(s.encode("latin1"), key)


def canon_digits(s: str) -> str:
    return "".join(CANON.get(c, c) for c in s)


def digital_xor(s: str, dkey: str, mod: int) -> str:
    out = []
    for i, c in enumerate(s):
        v = int(CANON[c]) if c in CANON else 0
        k = int(dkey[i % len(dkey)])
        out.append(str((v ^ k) % mod))
    return "".join(out)


def interp_base10_hex_ascii(digits: str) -> str | None:
    """Certified z-segment decoder: digits as base-10 big number -> hex -> ASCII."""
    try:
        n = int(digits, 10)
    except ValueError:
        return None
    if n <= 0:
        return None
    h = format(n, "x")
    if len(h) % 2:
        h = "0" + h
    try:
        return bytes.fromhex(h).decode("ascii", "replace")
    except ValueError:
        return None


def printable(b: bytes) -> str | None:
    if b and all(32 <= x <= 126 for x in b):
        return b.decode("ascii", "replace")
    return None


def renders(out: bytes) -> list[str]:
    r = []
    p = printable(out)
    if p is not None:
        r += [p, p.upper(), p.lower(), p[::-1], p[::-1].upper(), p[::-1].lower()]
    r.append(out.hex())
    r.append(out[::-1].hex())
    r.append(str(int.from_bytes(out, "big")))
    return r


def grid_keys() -> dict[str, str]:
    keys = {}
    orders = grid_orderings(CELLS, SB)
    for oname, order in orders.items():
        bits = "".join("1" if c in SB else "0" for c in order)
        keys[f"grid.{oname}.bits"] = bits
        keys[f"grid.{oname}.bits_rev"] = bits[::-1]
        for rname, fs in reductions(order).items():
            keys[f"grid.{oname}.{rname}"] = fs
    return keys


def key_set() -> dict[str, str]:
    keys = {}
    kcq = ["KCQ", "kcq", "Qck", "CKQ", "KC", "KQ", "CQ", "KQCKQC", "kylewbanks",
           "kylewbanks.com", "KyleWBanks"]
    for k in kcq:
        keys[f"kcq_{k}"] = k
    tokens = ["matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
              "shabef", "yourlastcommand", "secondanswer", "salphasion", "cosmicduality",
              "theseedisplanted", "btcseed", "followthewhiterabbit",
              "fubcdorale thingky mvps", "thearchitectchoice",
              "hopeisthequintessentialhumandelusion", "gsmg"]
    for t in tokens:
        keys[f"tok_{t}"] = t
        keys[f"tok_{t}_rev"] = t[::-1]
        keys[f"tok_{t}_dig"] = canon_digits(t)
    keys.update(grid_keys())
    return keys


def gen_candidates(out_path: str) -> int:
    cands: set[str] = set()
    keys_kcq = {k: v for k, v in key_set().items() if k.startswith(("kcq_", "tok_", "grid."))}
    # A/B/C : raw cycle-XOR over every stream with every key
    for sname, s in STREAMS.items():
        for kname, key in keys_kcq.items():
            for out in (cycle_xor_raw(s, key), cycle_xor_raw(s[::-1], key)):
                for r in renders(out):
                    cands.add(r)
        # D : digital-XOR with KCQ translated to digit keys (K=11,C=3,Q=17)
        for mod, dkey in ((9, "110317"), (10, "11317")):
            for sl in (s, s[::-1]):
                dg = digital_xor(sl, dkey, mod)
                cands.add(dg)
                both = [dg]
                for kname, key in keys_kcq.items():
                    if kname.startswith("grid.") and "_m9" in kname and key.isdigit():
                        kd = key
                        dg2 = digital_xor(sl, kd, mod)
                        both.append(dg2)
                for dg2 in both:
                    cands.add(dg2)
                    it = interp_base10_hex_ascii(dg2)
                    if it:
                        cands.add(it)
    with open(out_path, "w") as f:
        f.writelines(c + "\n" for c in sorted(cands))
    return len(cands)


def selftest() -> tuple[bool, str]:
    # 1. repo canonical double-XOR roundtrip (XOR is involutive at byte level)
    c0 = cycle_xor_raw("kylewbanks.com", "KCQ")
    if cycle_xor_bytes(c0, "KCQ").decode("latin1") != "kylewbanks.com":
        return False, "repo canonical KCQ roundtrip failed"
    # 2. injection through the same generator
    P = "CYCLEXORWITNESS"
    F = cycle_xor_raw(P, "matrixsumlist").decode("latin1")
    STREAMS["_wit"] = F
    n = gen_candidates(SCRATCH + ".wit")
    forms = set(open(SCRATCH + ".wit").read().splitlines())
    del STREAMS["_wit"]
    os.remove(SCRATCH + ".wit")
    if P not in forms and P.upper() not in forms and P[::-1] not in forms:
        return False, f"injection plaintext not re-found among {n} candidates"
    return True, f"selftest OK ({n} witness-form candidates, P re-found)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--both", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        st, msg = selftest()
        print(msg)
        return 0 if st else 1

    t0 = time.time()
    n = gen_candidates(SCRATCH)
    print(f"[xorencryption_steer] {n} candidates -> {SCRATCH} ({time.time()-t0:.0f}s)")
    if args.both:
        for prog in ("oracle.py", "oracle_dualite.py"):
            p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", prog), "--stdin"],
                               stdin=open(SCRATCH), capture_output=True, text=True)
            out = [l for l in p.stdout.splitlines() if l.strip()]
            print(f"[xorencryption_steer] {prog}: {out[-1] if out else 'NO MATCH'}")
            # Anchor to line-start: a bare `"MATCH" in p.stdout` is TRUE for the
            # literal "NO MATCH", so a fully negative batch would dump every
            # line and exit 0, falsely reporting success to any automation.
            if any(l.startswith("MATCH ") for l in out):
                print(p.stdout)
                return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())