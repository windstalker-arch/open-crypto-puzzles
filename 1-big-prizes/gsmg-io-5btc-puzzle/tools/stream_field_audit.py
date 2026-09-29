#!/usr/bin/env python3
"""Certify which tools read the AUTHORITATIVE dbbib stream and which read the
superseded one.

Background (tested.md late-150, "BUG 2"): `data/finalpage-digit-streams.json`
carries TWO dbbib fields. `dbbib_91` is the authoritative 91-token object
(live page + Wayback 2023-06-01/2026-04-05 + community README line 371).
`dbbib` is the superseded 69-token shallow-OCR crop, which is missing the
22-char middle run inserted at offset 45. BUG 2 named 5 stale readers and
asserted "recent sweep rows were all re-derived on the live 91-token object".
That assertion did not hold: a full scan finds the class is much wider, and
some tools print `dbbib(91)` in their own output while feeding the 69-token
crop -- a mislabeling bug, because the label is what a reader trusts.

This checker exists because the BUG-2 flag was prose, and prose was wrong.
The failure mode it prevents is a sweep silently testing the wrong artifact
and reporting a confident negative, which is exactly the late-58 / R-P15NULL
shape of error.

Usage:
    python3 tools/stream_field_audit.py --selftest
    python3 tools/stream_field_audit.py --check
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")

# A read of the superseded field. Three spellings occur in this repo:
#   d["dbbib"] / DATA["dbbib"]     - direct subscript off a loaded mapping
#   DATA["dbbib"].lower()          - the common chain form
#   streams["dbbib"]               - indirect, via a mapping returned by a loader
# The third was added after zseg_bifid_sweep.py escaped the first two, so the
# pattern is broad -- but NOT so broad that a dict KEY or a display label counts.
# phase322_literal_sweep.py hardcodes the correct 91-token literal and uses
# "dbbib" only as a key/label; a naive `"dbbib"` scan flags it as CRITICAL,
# which is why the negative-lookahead also rejects a key position.
BARE_91 = re.compile(r"""["']dbbib["'](?!_91)""")
# A key/label is followed by ":" or ","  (dict key, or a display tuple element).
# A READ is a subscript, so it is followed by "]" or a chained call.
# phase322_literal_sweep.py uses "dbbib" only as a dict key and a tuple label
# while hardcoding the correct 91-token literal; a naive scan flags it CRITICAL.
IS_KEY = re.compile(r"""^\s*["']dbbib["']\s*[:,]""")
CLAIM_91 = re.compile(r"dbbib\(91\)|91-token|dbbib_91")


def has_crop_read(src: str) -> bool:
    for line in src.splitlines():
        if "dbbib_91" in line:
            continue
        for m in BARE_91.finditer(line):
            tail = line[m.start():].lstrip()
            if IS_KEY.match(tail):
                continue          # dict key or display label, not a read
            return True
    return False

# The 22-char run that distinguishes the authoritative object from the crop:
# dbbib_91[45:67]. (phase322_literal_sweep.py uses a DIFFERENT but equally exact
# partition, 45+23+23 == dbbib_91[:45] + dbbib_91[45:68] + dbbib_91[68:91]; both
# reproduce the object, so neither is wrong -- but only the 22-char form is the
# crop's diff, and mixing them silently yields a 92-char string.)
MID_RUN = "bfdhbeffcdbbfcccgbfbee"
MID_OFFSET = 45
AUTHORITATIVE_LEN = 91
SUPERSEDED_LEN = 69


def classify(src: str) -> str:
    """OK      - uses dbbib_91 and never the crop
       DUAL    - deliberately reads both (naming them, so the intent is legible)
       CRITICAL- reads the crop while claiming the 91-token object
       STALE   - reads the crop, makes no 91 claim (still wrong, lower blast)
    """
    bare = has_crop_read(src)
    uses91 = "dbbib_91" in src
    if bare and uses91:
        return "DUAL"
    if bare and re.search(r"dbbib\(91\)|91-token", src):
        return "CRITICAL"
    if bare:
        return "STALE"
    if uses91:
        return "OK"
    return "NA"


SELF = os.path.basename(__file__)


def scan():
    out = []
    for name in sorted(os.listdir(TOOLS)):
        if not name.endswith(".py") or name == SELF:
            continue
        src = open(os.path.join(TOOLS, name), encoding="utf-8", errors="ignore").read()
        kind = classify(src)
        if kind != "NA":
            out.append((name, kind))
    return out


def data_invariants():
    d = json.loads(open(DATA, encoding="utf-8").read())
    crop, auth = d["dbbib"], d["dbbib_91"]
    problems = []
    if len(crop) != SUPERSEDED_LEN:
        problems.append(f"crop len {len(crop)} != {SUPERSEDED_LEN}")
    if len(auth) != AUTHORITATIVE_LEN:
        problems.append(f"authoritative len {len(auth)} != {AUTHORITATIVE_LEN}")
    rebuilt = crop[:MID_OFFSET] + MID_RUN + crop[MID_OFFSET:]
    if rebuilt != auth:
        problems.append("crop[:45] + 22-char run + crop[45:] != dbbib_91")
    if MID_RUN in crop:
        problems.append("crop unexpectedly contains the 22-char run")
    if not set(auth) <= set("abcdefghi"):
        problems.append("dbbib_91 has symbols outside a..i")
    if set(crop) - set(auth):
        problems.append("crop has symbols absent from the authoritative object")
    return d, problems


def selftest():
    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))

    d, probs = data_invariants()
    ck("data invariants hold", not probs)
    ck("crop is 69", len(d["dbbib"]) == 69)
    ck("authoritative is 91", len(d["dbbib_91"]) == 91)
    ck("22-char run absent from crop", MID_RUN not in d["dbbib"])
    ck("22-char run present in authoritative", MID_RUN in d["dbbib_91"])
    ck("22-char run is exactly dbbib_91[45:67]", d["dbbib_91"][45:67] == MID_RUN)
    ck("the 23-char MID variant is dbbib_91[45:68] (different partition, also exact)",
       d["dbbib_91"][45:68] == "bfdhbeffcdbbfcccgbfbeeg")
    ck("91 is exactly 7x13", AUTHORITATIVE_LEN % 13 == 0)
    ck("69 is NOT divisible by 13 (so a 7x13 grid silently truncates)",
       SUPERSEDED_LEN % 13 != 0)

    # classifier unit tests on synthetic sources
    ck("classify: authoritative only -> OK",
       classify('X = d["dbbib_91"]') == "OK")
    ck("classify: crop only, no claim -> STALE",
       classify('X = d["dbbib"]') == "STALE")
    ck("classify: dict KEY is not a read -> NA",
       classify('W = {"dbbib": [7,13] , "faed": [15]}') == "NA")
    ck("classify: display label tuple is not a read -> NA",
       classify('for s,st in [("dbbib", D), ("faed", F)]:') == "NA")
    ck("classify: tuple label + a real read -> STALE",
       classify('W={"dbbib":1}\nX = streams["dbbib"]') == "STALE")
    ck("classify: hardcoded 91-token literal + labels only -> NA (reads neither field)",
       classify('X="dbbibfbhccbeg"\nW={"dbbib":[7]}\nfor s,v in [("dbbib",X)]:') == "NA")
    ck("classify: crop + 91 claim -> CRITICAL",
       classify('X = d["dbbib"]\nprint("dbbib(91)")') == "CRITICAL")
    ck("classify: indirect dict read is caught too",
       classify('dbbib = streams["dbbib"]') == "STALE")
    ck("classify: chained .lower() read is caught too",
       classify('D = DATA["dbbib"].lower()') == "STALE")
    ck("classify: dbbib_91 is not flagged as a crop read",
       classify('X = d["dbbib_91"]') == "OK")
    ck("classify: crop + 91-token claim -> CRITICAL",
       classify("X = d['dbbib']\n# 91-token stream") == "CRITICAL")
    ck("classify: both fields -> DUAL",
       classify('A=d["dbbib"]\nB=d["dbbib_91"]') == "DUAL")
    ck("classify: unrelated -> NA", classify("x = 1") == "NA")

    # the real repo must have no CRITICAL tool
    rows = scan()
    crit = [n for n, k in rows if k == "CRITICAL"]
    ck(f"no CRITICAL tools remain (found {len(crit)}: {crit})", not crit)

    # the two fields must be genuinely different objects, or the whole class
    # of bug is vacuous
    ck("crop and authoritative really differ", d["dbbib"] != d["dbbib_91"])

    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {n}")
    print(f"\n{'SELFTEST PASS' if not bad else 'SELFTEST FAIL'}: {len(checks)-len(bad)}/{len(checks)}")
    return 1 if bad else 0


def check():
    d, probs = data_invariants()
    rows = scan()
    by = {}
    for name, kind in rows:
        by.setdefault(kind, []).append(name)
    print("data invariants:", "OK" if not probs else "PROBLEMS")
    for p in probs:
        print("   !", p)
    print(f"  crop d['dbbib']        len={len(d['dbbib'])}  (superseded OCR crop)")
    print(f"  authoritative dbbib_91 len={len(d['dbbib_91'])}  (live page)")
    print()
    order = ["CRITICAL", "STALE", "DUAL", "OK"]
    for kind in order:
        names = sorted(by.get(kind, []))
        if kind == "OK":
            print(f"{kind:9} {len(names)} tools  (authoritative reader)")
            continue
        print(f"{kind:9} {len(names)} tools")
        for n in names:
            print("   ", n)
    crit = len(by.get("CRITICAL", []))
    print()
    if crit:
        print(f"FAIL: {crit} tool(s) label themselves dbbib(91) while reading the 69-token crop.")
        return 1
    if probs:
        print("FAIL: data invariants broken.")
        return 1
    print("OK: no tool mislabels the 69-token crop as the 91-token object.")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--check" in sys.argv:
        sys.exit(check())
    print(__doc__)
    sys.exit(2)
