#!/usr/bin/env python3
"""zseg_bifid_sweep.py -- decrypt the SalPhaseIon z-segment streams all-at-once
through the certified Bifid decoder (keyed square DBIFHCEG, J dropped), then
oracle-test the decodes on BOTH funded gates.

Gap closed: tested.md sections 123/124 ran the ciphertools Bifid/(DBIFHCEG) over
dbbib, faed, even, odd, object_256, dropped_29 -- but NOT the two z-segment streams
(seg1 `agdafaoaheiecggchgicbbhcgbehcfcoabicfdhhcdbbcagbdaiobbgbeadedde`,
seg2 `cfobfdhgdobdgooii...ooofidh`). The author calls the pages' words 'last words
before archi choice' and the yinyang clue says to merge the two streams. This tool
decrypts seg1/seg2 (and their yin/yang merges) all-at-once through the certified
decoder and pushes every legible/cipher decode through the final-gate oracle.

Self-certifies the decoder by re-deriving the faed -> BTCSEED witness first.

Public/authorized puzzle only. A hit is a MATCH from the oracle, nothing less.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ALPHA = "ABCDEFGHIKLMNOPQRSTUVWXYZ"


def build_grid(keyword, alphabet=None):
    alphabet = alphabet or ALPHA
    keyed = ""
    for ch in (keyword + alphabet).upper():
        if ch not in keyed and ch in alphabet:
            keyed += ch
    if len(keyed) != 25:
        return None, None
    grid = [list(keyed[i * 5:(i + 1) * 5]) for i in range(5)]
    pos = {}
    for r in range(5):
        for c in range(5):
            pos[grid[r][c]] = (r, c)
    return grid, pos


def _upper_sanitize(s, pos=None):
    out = []
    for ch in s.upper():
        if pos is not None:
            if ch in pos:
                out.append(ch)
        elif ch in ALPHA:
            out.append(ch)
    return "".join(out)


def bifid_decrypt(ct, period, grid, pos):
    coords = [pos[ch] for ch in _upper_sanitize(ct, pos)]
    combined = []
    for r, c in coords:
        combined.append(r)
        combined.append(c)
    out = ""
    n = len(combined)
    eff = period if period > 0 else n // 2
    if eff <= 0:
        return out
    for start in range(0, n, 2 * eff):
        block = combined[start:start + 2 * eff]
        h = len(block) // 2
        rs, cs = block[:h], block[h:]
        for k in range(h):
            out += grid[rs[k]][cs[k]]
    return out


def bifid_encrypt(pt, period, grid, pos):
    pts = _upper_sanitize(pt, pos)
    coords = [pos[ch] for ch in pts]
    combined = []
    for r, c in coords:
        combined.append(r)
        combined.append(c)
    out = ""
    n = len(combined)
    eff = period if period > 0 else n // 2
    if eff <= 0:
        return out
    for start in range(0, n, 2 * eff):
        block = combined[start:start + 2 * eff]
        h = len(block) // 2
        rs, cs = block[:h], block[h:]
        for k in range(h):
            out += grid[rs[k]][cs[k]]
    return out


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def merge(a, b):
    """yinyang: alternate then pad tail."""
    n = min(len(a), len(b))
    out = []
    for i in range(n):
        out.append(a[i])
        out.append(b[i])
    out.extend(a[n:])
    out.extend(b[n:])
    return "".join(out)


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    streams = json.loads(Path(os.path.join(base, "data", "finalpage-digit-streams.json")).read_text())
    oracle = os.path.join(base, "tools", "oracle.py")
    oracle_dual = os.path.join(base, "tools", "oracle_dualite.py")

    faed = streams["faed_570"].rstrip("z")
    dbbib = streams["dbbib"]

    seg1 = "agdafaoaheiecggchgicbbhcgbehcfcoabicfdhhcdbbcagbdaiobbgbeadedde"
    seg2 = "cfobfdhgdobdgooigdocdaoofidh"

    grid, pos = build_grid("DBIFHCEG")

    # --- 0. Witness: certify the decoder by re-deriving faed -> BTCSEED ---------
    faed_upper = _upper_sanitize(faed, pos)
    full_faed = bifid_decrypt(faed_upper, len(faed_upper), grid, pos)
    witness_ok = full_faed.startswith("BTCSEED")
    print(f"WITNESS faed->Bifid(DBIFHCEG, full) head: {full_faed[:40]!r}")
    print(f"WITNESS matches stored plaintext_head: {witness_ok}")

    # --- Interpreter-alphabet digit maps (leads #93/#96) ------------------------
    alpha_maps = {
        "row0": "DBIFHCEG",
        "a0i8": "abcdefghi",
        "salph#96": "815063742",
    }

    cands = []  # (label, string)

    def add(label, s):
        if s and s not in {c[1] for c in cands}:
            cands.append((label, s))

    # source strings to Bifid-decrypt all-at-once (each segment has relevant
    # letter-count = even, so full period = n is natural; try all divisor periods)
    sources = {
        "seg1": seg1,
        "seg2": seg2,
        "seg1+seg2": seg1 + seg2,
        "seg2+seg1": seg2 + seg1,
        "merge_yinyang_12": merge(seg1, seg2),
        "merge_yinyang_21": merge(seg2, seg1),
        "seg1+seg2+faed": seg1 + seg2 + faed,
        "dbbib+seg1+seg2": dbbib + seg1 + seg2,
    }

    for sname, s in sources.items():
        su = _upper_sanitize(s, pos)
        if not su:
            continue
        periods = set(divisors(len(su)) + [len(su)])
        for per in sorted(periods):
            dec = bifid_decrypt(su, per, grid, pos)
            enc = bifid_encrypt(su, per, grid, pos)
            add(f"{sname}_dec_p{per}", dec)
            add(f"{sname}_enc_p{per}", enc)
        # digit-map readings of the source (a..i -> digit) as X
        for mname, mval in alpha_maps.items():
            tbl = str.maketrans({c: str(i) for i, c in enumerate(mval)})
            d = s.lower().translate(tbl)
            if d and d != s:
                add(f"{sname}_digits_{mname}", d)
        # reversed
        add(f"{sname}_rev", su[::-1])

    # a few cases for short, answer-like decodes
    length = len(cands)
    for i in range(length):
        lab, s = cands[i]
        if len(s) <= 128:
            add(lab + "_lower", s.lower())
            add(lab + "_upper", s.upper())

    print(f"\ncandidate X set size: {len(cands)}")

    scratch = "/data/data/com.termux/files/usr/tmp/opencode"
    os.makedirs(scratch, exist_ok=True)
    outpath = os.path.join(scratch, "zseg_bifid_cands.txt")
    with open(outpath, "w") as f:
        for _, s in cands:
            f.write(s + "\n")

    print("\n--- printing legible-ish decodes for inspection ---")
    import re
    for lab, s in cands:
        # show decodes that look like they might contain words / letters only
        if ("dec_" in lab or "enc_" in lab) and len(s) >= 6:
            pass
    for lab, s in cands:
        if ("dec_" in lab and len(s) <= 200):
            alpha = re.sub(r"[^A-Z]", "", s.upper())
            # crude word-heuristic: long runs of common letters / low entropy
            print(f"  {lab:34s} {s[:70]}")

    # --- Oracle: small gate then dualite gate ------------------------------------
    for name, oracle_path in [("small", oracle), ("dualite", oracle_dual)]:
        r = subprocess.run([sys.executable, oracle_path, "--stdin"],
                           input=Path(outpath).read_bytes(), capture_output=True)
        lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
        hits = [ln for ln in lines if ln.startswith("MATCH")]
        print(f"\n[{name}] oracle lines: {len(lines)}  MATCH: {len(hits)}")
        for h in hits:
            print("HIT:", h)
            for lab, s in cands:
                if s in h:
                    print(f"   -> {lab} : {s!r}")
        if not hits:
            print(f"[{name}] NO MATCH")

    summary = {
        "witness_faed_btcseed": witness_ok,
        "candidates_tested": len(cands),
        "candidate_file": outpath,
    }
    print("\nSUMMARY:", json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
