#!/usr/bin/env python3
"""Running-key 5x5 square-shift decode battery (lead: "what next" -- a family the
ledger does not list as swept).

Certified plaintext (285 letters over the certified 25-alphabet) is treated as a
ciphertext over a 5x5 square. For each square in our established set
(cert DBIFHCEGA..., keyed UAETOGKDJ..., first-occurrence orders), each plaintext
letter is un-shifted within its square ROW (Vigenere-in-plain, shift = key digit)
or its square COLUMN, or with row+col combined from two long keystreams. Keystreams
are the certified base-9 digit streams (a=0..8) of faed, dbbib, and z segments, and
the certified even_stream recoded 0..3 (2-bit). Both shift directions and both
running orders. Output printable/wordy strings become oracle candidates.

No gate assumed; results honest per line.
"""
import itertools
import json
import os
from pathlib import Path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("OUT", "/data/data/com.termux/files/usr/tmp/opencode/sqshift_cands.txt")

DATA = json.loads(Path(os.path.join(BASE, "data", "finalpage-digit-streams.json")).read_text())
SAL = json.loads(Path(os.path.join(BASE, "data", "salphaseion-streams.json")).read_text())

FAED = DATA["faed_570"].rstrip("z").lower()
DBBIB = DATA["dbbib_91"].lower()
CERT = "DBIFHCEGAKLMNOPQRSTUVWXYZ"


def certified_plaintext():
    mapped = "".join({"a": "A", "b": "B", "c": "C", "d": "D", "e": "E", "f": "F",
                      "g": "G", "h": "H", "i": "I"}[c] for c in FAED)
    pg = [CERT[i * 5:(i + 1) * 5] for i in range(5)]
    pos = {CERT[i]: (i // 5, i % 5) for i in range(25)}
    combined = []
    for ch in mapped:
        r, c = pos[ch]
        combined.append(r)
        combined.append(c)
    plain = ""
    for start in range(0, len(combined), 2 * 570):
        blk = combined[start:start + 2 * 570]
        h = len(blk) // 2
        for k in range(h):
            plain += pg[blk[k]][blk[h + k]]
    assert plain[:40] == SAL["plaintext_head"], plain[:40]
    return plain


def squares():
    order = []
    for c in FAED:
        if c not in order:
            order.append(c)
    o1 = CERT
    o2 = "UAETOGKDJFHCNQLVZYRMIWPSBX"
    o3 = "".join(FAED[i] for i in range(len(FAED)) if FAED[i] not in FAED[:i])[:25]
    o3 = o3 + "".join(ch for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if ch not in o3)
    o3 = o3[:25]
    sq = {}
    for name, alpha in (("cert", o1), ("keyed", o2), ("faed_fo", o3)):
        rows = [list(alpha[i * 5:(i + 1) * 5]) for i in range(5)]
        pos = {alpha[i]: (i // 5, i % 5) for i in range(25)}
        sq[name] = (rows, pos, alpha)
    return sq


def keystreams():
    m9 = {c: i for i, c in enumerate("abcdefghi")}
    ks = {}
    ks["faed9"] = [m9[c] for c in FAED]
    ks["dbbib9"] = [m9[c] for c in DBBIB]
    ks["z1"] = [m9[c] for c in DATA["z_segment_1"] if c != "o"]
    ks["z2"] = [m9[c] for c in DATA["z_segment_2"] if c != "o"]
    # recode even_stream {B,C,D,E} -> 0..3
    ev = {"B": 0, "C": 1, "D": 2, "E": 3}
    ks["even2"] = [ev[c] for c in SAL["even_stream"]]
    return ks


def unshift(words, rows, pos, mode, shifts, rev):
    out = []
    L = len(words)
    for i, ch in enumerate(words):
        if ch not in pos:
            out.append(ch)
            continue
        r, c = pos[ch]
        k = shifts[i % len(shifts)]
        if rev:
            k = -k
        if mode == "row":
            out.append(rows[r][(c - k) % 5])
        elif mode == "col":
            out.append(rows[(r - k) % 5][c])
    return "".join(out)


def wordiness(s):
    alpha = sum(1 for c in s if c.isalpha())
    sp = sum(1 for c in s if c in " ")
    return (alpha + sp) / max(len(s), 1)


def main():
    plain = certified_plaintext()
    sq = squares()
    ks = keystreams()
    cands = []
    log = []

    for sqname, (rows, pos, alpha) in sq.items():
        for mode in ("row", "col"):
            for ksname, stream in ks.items():
                for rev in (False, True):
                    for use_shift in (lambda s: s % 5, lambda s: (s + 2) % 5):
                        shifts = [use_shift(x) for x in stream]
                        out = unshift(plain, rows, pos, mode, shifts, rev)
                        log.append((f"{sqname}/{mode}/{ksname}/rev={rev}", out, wordiness(out)))
                        if wordiness(out) > 0.72:
                            cands.append(out)

    dedup = {}
    for s in cands:
        dedup.setdefault(s, s)
    cands = list(dedup)
    Path(OUT).write_text("\n".join(cands) + "\n")
    print(f"[square-shift battery] {len(log)} combos, {len(cands)} wordy candidates")
    # top candidates by wordiness
    top = sorted([(w, s) for _, s, w in log], reverse=True)[:6]
    for w, s in top:
        print(f"  top wordy={w:.2f}: {s[:70]}")
    print("wrote ->", OUT)


if __name__ == "__main__":
    main()