#!/usr/bin/env python3
"""lead0_alphabet_exotic.py -- residual interpreter-ALPHABET constructions for the
dbbib_91 / faed_570 streams (late-310 follow-on, 2026-09-22).

Context: the community decoder a..i=1..9,o=0 (CANON) is CERTIFIED for the z1/z2 /
matrixsumlist regions of the 1075-token stream (z1 -> 'lastwordsbeforearchichoice',
z2 -> 'thispassword'). Under CANON, dbbib_91 and faed_570 decode to high-entropy
non-printable bytes, which is the lead-0 crux: those two regions need a DIFFERENT
interpreter alphabet before they emit their semantic phrase.

This tool sweeps the bounded family of still-untested, hint-anchored constructions:
  M_CANON   a..i=1..9, o=0                (certified anchor / selftest only)
  M_ALPHA10 a=0..i=8, o=9                 (the 10 glyphs a..i,o = the ten digits, alphabetic order)
  M_ROT_k   (CANON(v)-k) mod 10, k=1..9   (cyclic relabelings; "which glyph is zero")
  M_P2      a=2,b=3,c=5,d=7,e=1,f=3,g=7,h=9,i=3,o=0   (prime-value mod 10; "primes 2,3,5,7 necessary")
  M_PTXT    a..i -> {2,3,5,7,11,13,17,19,23}, o=0 concat -> decimal-to-hex-to-ascii ("primes" literal text)

For each map x region x reading it evaluates:
  (i)   is the full decode printable ASCII? (if yes -> candidate phrase for the gates)
  (ii)  does the E_S byte string (B2_79[64:79]) appear as a contiguous window
        of the decoded byte stream (the all-routes-layout class of late-299/300)?
  (iii) sha256/md5 of any printable decode's [0:15] == E_S (the digest-anchor class).

Writes printable decodes + variants to lead0_exotic_gate.txt for the funded-gate
oracles if --write-gates. Selftest certifies M_CANON reproduces the two known words.

Public/authorized puzzle only.
"""
from __future__ import annotations
import argparse, hashlib, json, sys, os

E_S_HEX = "740a25de4b8e946d0a5ae2667a23a2"
E_S_BYTES = bytes.fromhex(E_S_HEX)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STREAMS = os.path.join(ROOT, "data", "finalpage-digit-streams.json")

M_CANON = dict(a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, i=9, o=0)
M_ALPHA10 = dict(a=0, b=1, c=2, d=3, e=4, f=5, g=6, h=7, i=8, o=9)
PRIMES = dict(a=2, b=3, c=5, d=7, e=11, f=13, g=17, h=19, i=23, o=0)
M_P2 = {k: v % 10 for k, v in PRIMES.items()}


def maps():
    m = {"CANON": M_CANON, "ALPHA10": M_ALPHA10, "P2": M_P2, "PTXT": PRIMES}
    for k in range(1, 10):
        m[f"ROT{k}"] = {s: (M_CANON[s] - k) % 10 for s in M_CANON}
    return m


def digits_of(tok: str, m) -> str:
    return "".join(str(m[c]) for c in tok)


def bigint_ascii(ds: str):
    if not ds:
        return b""
    v = int(ds, 10)
    n = (v.bit_length() + 7) // 8
    return v.to_bytes(n, "big") if n else b""


def hex_pairs_ascii(ds: str):
    if len(ds) % 2:
        ds = ds[:-1]
    try:
        return bytes.fromhex(ds)
    except ValueError:
        return b""


def decimal_char(ds: str):
    out = bytearray()
    i = 0
    while i < len(ds):
        for L in (2, 3):
            if i + L <= len(ds) and 32 <= int(ds[i:i + L], 10) <= 255:
                out.append(int(ds[i:i + L], 10))
                i += L
                break
        else:
            i += 1
    return bytes(out)


def printable_ratio(b: bytes) -> float:
    if not b:
        return 0.0
    ok = sum(32 <= x < 127 or x in (9, 10, 13) for x in b)
    return ok / len(b)


def e_s_preimage(phrase: str):
    for alg, fn in (("sha256", hashlib.sha256), ("md5", hashlib.md5)):
        if fn(phrase.encode()).hexdigest()[:30] == E_S_HEX:
            return alg
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--write-gates", action="store_true")
    args = ap.parse_args()

    d = json.load(open(STREAMS))
    regs = {
        "dbbib_91": d["dbbib_91"],
        "faed_570_z": d["faed_570"][:570].rstrip("z"),
        "faed_570": d["faed_570"][:570],
        "z1": d["z_segment_1"],
        "z2": d["z_segment_2"],
    }

    if args.selftest:
        assert digits_of(regs["z1"], M_CANON) and bigint_ascii(digits_of(regs["z1"], M_CANON)).decode() == "lastwordsbeforearchichoice", "CANON(z1) anchor"
        assert bigint_ascii(digits_of(regs["z2"], M_CANON)).decode() == "thispassword", "CANON(z2) anchor"
        assert len(E_S_BYTES) == 15 and int(E_S_HEX, 16) >= 0
        print("SELFTEST OK  (CANON z1/z2 anchors reproduced; E_S slice constant)")
        return 0

    found_printable = []
    rows = []
    for mname, m in maps().items():
        for rname, tok in regs.items():
            ds = digits_of(tok, m)
            readings = {"bigint": bigint_ascii(ds), "hexpairs": hex_pairs_ascii(ds), "dc": decimal_char(ds)}
            for rtag, byts in readings.items():
                if not byts:
                    continue
                e_win = E_S_BYTES in byts
                if printable_ratio(byts) >= 0.95 and len(byts) >= 8:
                    ascii_s = byts.decode("latin1").rstrip()
                    hit = e_s_preimage(ascii_s)
                    found_printable.append((mname, rname, rtag, ascii_s))
                    rows.append((mname, rname, rtag, "PRINTABLE", len(byts), len(ascii_s), hit, ascii_s[:50]))
                elif e_win:
                    rows.append((mname, rname, rtag, "E_S-WINDOW", len(byts), 0, None, byts[:24].hex()))

    if rows:
        print("map    region     reading  status     len   desc")
        for m, r, rt, st, n, ln, hit, desc in rows:
            print(f"{m:<7} {r:<10} {rt:<9} {st:<10} {n:>4} {(hit or '')}  {desc}")
    else:
        print("NO printables and NO E_S-window occurrences across all maps/regions/readings.")

    if found_printable:
        for m, r, rt, s in found_printable:
            print(f"PRINTABLE CANDIDATE <- map={m} region={r} reading={rt}: {s!r}")

    if args.write_gates and found_printable:
        out = set()
        for _m, _r, _rt, s in found_printable:
            for v in (s, s.lower(), s.upper(), s.replace(" ", "")):
                out.add(v)
        path = os.path.join(os.path.dirname(__file__), "lead0_exotic_gate.txt")
        open(path, "w").write("\n".join(sorted(out)) + "\n")
        print(f"wrote {len(out)} gate candidates -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())