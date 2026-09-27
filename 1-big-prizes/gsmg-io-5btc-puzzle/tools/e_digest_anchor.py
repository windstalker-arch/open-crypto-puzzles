#!/usr/bin/env python3
"""e_digest_anchor.py -- E_S = truncated digest of an in-corpus / certified
decode string? E_S (B2_79[64:79] = 740a25de4b8e946d0a5ae2667a23a2, 15 bytes)
has never been tested as a truncated-DIGEST anchor. If the interpreter-alphabet
leap outputs a phrase and E_S is its sha256/md5[0:15], the corpus already holds
every certified phrase -> all directly checkable today.

Checks sha256/sha1/md5/ripemd160 digest[:15] == E_S over ~1k corpus strings
and variants. Selftest mirrors e_anchor_battery blob asserts.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys

BASE = os.path.expanduser(
    "~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle")
E_S_HEX = "740a25de4b8e946d0a5ae2667a23a2"
E_S = bytes.fromhex(E_S_HEX)


def digests(b: bytes):
    yield "sha256", hashlib.sha256(b).digest()
    yield "sha1", hashlib.sha1(b).digest()
    yield "md5", hashlib.md5(b).digest()
    yield "ripemd160", hashlib.new("ripemd160", b).digest()


def variants(s: str):
    yield s
    yield s.strip()
    yield s.strip().lower()
    yield s.strip().upper()
    yield s.replace(" ", "")
    yield s.replace(" ", "").lower()
    yield s.replace(" ", "_")
    yield s.replace(" ", "-")


def corpus() -> list[str]:
    out = []
    j = json.load(open(os.path.join(BASE, "data/finalpage-digit-streams.json")))
    # certified decodes + in-corpus keywords/assemblies
    out += [
        "lastwordsbeforearchichoice", "thispassword",
        "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALF"
        "ANDTHEYALSONEEDFUNDSTOLIVE",
        "yourlastcommand", "firsthintisyourlastcommand",
        "ourfirsthintisyourlastcommand", "matrixsumlist", "matrixsumlistenter",
        "shabef", "anstoo", "enter", "causality", "hopetothequintessentialhumandelusion",
        "thearchitectschoice", "archichoice", "halfandbetterhalf", "salphaseion",
        "cosmicduality", "theseedisplanted", "gsmg.io/theseedisplanted",
        "theprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive",
    ]
    out += list(j.keys())
    out += [str(v) for v in j.get("canonical_value_mapping", {}).values()]
    # blob field hex / key material frames
    for f in ("B1_79B.bin", "B2_79B.bin"):
        try:
            raw = open(os.path.join(BASE, "data", f), "rb").read()
        except OSError:
            continue
        out.extend([raw.hex(), raw[:32].hex(), raw[32:64].hex(), raw[64:].hex()])
    # gates + WIF + known pubkey ground
    out += [
        "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe", "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa",
        "5K2byJMssxFKuTgnk9YQjpBz5FhkwwF2LaZoAyTus8HjGEpz8AT",
    ]
    # live_salphaseion page text lines
    try:
        txt = open(os.path.join(BASE, "data/live_salphaseion.txt"),
                   encoding="utf-8", errors="replace").read()
        for line in txt.splitlines():
            line = line.strip()
            if line and line.isprintable() and len(line) >= 4:
                out.append(line)
    except OSError:
        pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        b1 = open(os.path.join(BASE, "data/B1_79B.bin"), "rb").read()
        b2 = open(os.path.join(BASE, "data/B2_79B.bin"), "rb").read()
        ok = (len(b2) == 79 and hashlib.sha256(b2).hexdigest()
              == "b40fce72ef5638e4f79b3233e653f8a5dbdb0d4ae2009d2d3da2c98b70f4d004"
              and b2[64:79].hex() == E_S_HEX
              and hashlib.sha256(b1).hexdigest()
              == "1449a2178eea7c0e3fabac8c1ad2afa294be4fc1800c594a025a056e88c626bf")
        print(f"[selftest] {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1

    seen = set()
    hits = []
    count = 0
    for base in corpus():
        for v in variants(base):
            if v in seen:
                continue
            seen.add(v)
            b = v.encode("utf-8")
            for hname, d in digests(b):
                # every 15-byte slice, not just [0:15]
                for off in range(0, len(d) - 14):
                    count += 1
                    if d[off:off + 15] == E_S:
                        hits.append(f"MATCH {hname}[{off}:{off+15}] of {v!r}")
                        print(f"  >>> {hname}({v!r})[{off}:{off+15}] == E_S")
    print(f"digest-anchor sweep: {len(seen)} strings x 4 digests x all slices = {count} checks")
    if hits:
        print("HITS PRESENT")
        return 0
    print("NO MATCH: E_S is not sha256/sha1/md5/ripemd160[:15] of any corpus string.")
    return 1


if __name__ == "__main__":
    sys.exit(main())