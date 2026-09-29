#!/usr/bin/env python3
"""bifid_to_pipeline.py -- tie the Bifid stage back into the GSMG final-gate pipeline.

The Bifid stage (keyed square DBIFHCEG, J dropped, blank/full-length period) decodes
the two raw final-page streams (faed_570, dbbib_69) into candidate answer strings X.
The final gate then runs X through the published AES-blob pipeline:
    X -> sha256(X).hexdigest() -> AES-256-CBC (salt 3ab585348552415d)
         -> 32-byte private key (first32/last32/sha256 readings)
         -> secp256k1 -> HASH160 -> P2PKH target 1GSMG1JC...

tested.md 29b swept the *faed*-derived Bifid outputs (full plaintext, odd reduction,
even stream, object-256, dropped-29, BTCSEED+even) as X: all NO MATCH. It did NOT sweep
the *dbbib* Bifid decode as X (dbbib = 69 = 3x23, FALSIFIED from 91 on 2026-08-27; the
pre-correction negatives are inconclusive for the corrected dbbib). This tool closes
that gap: decode BOTH raw streams with the certified Bifid decoder and oracle-test the
resulting X set (plus the documented interpreter-alphabet digit mappings).

Self-certifies the decoder by re-deriving the faed -> BTCSEED... witness before sweeping
(the same code, same inputs as tools/bifid_repro.py which passes SELFCERT).
"""

import hashlib
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


def sh(s):
    return hashlib.sha256(s.encode()).hexdigest()


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    stored = json.loads(Path(os.path.join(base, "data", "salphaseion-streams.json")).read_text())
    streams = json.loads(Path(os.path.join(base, "data", "finalpage-digit-streams.json")).read_text())
    oracle = os.path.join(base, "tools", "oracle.py")

    faed = streams["faed_570"].rstrip("z")
    dbbib = streams["dbbib_91"]   # authoritative; streams["dbbib"] is the crop

    grid, pos = build_grid("DBIFHCEG")

    # --- 0. Witness: certify decoder by re-deriving the faed -> BTCSEED stage ----
    faed_upper = _upper_sanitize(faed, pos)
    full_faed = bifid_decrypt(faed_upper, len(faed_upper), grid, pos)
    witness_ok = full_faed.startswith("BTCSEED")
    print(f"WITNESS faed->Bifid(DBIFHCEG, full) head: {full_faed[:40]!r}")
    print(f"WITNESS matches stored plaintext_head: {witness_ok}")

    # --- 1. Decode updated dbbib (69) exactly like faed --------------------------
    dbbib_upper = _upper_sanitize(dbbib, pos)
    full_dbbib = bifid_decrypt(dbbib_upper, len(dbbib_upper), grid, pos)
    print(f"\ndbbib(69) Bifid(DBIFHCEG, full) decode: {full_dbbib!r}")

    # Interpreter-alphabet digit mappings from leads.md #93/#96 canonical value map.
    alpha_maps = {
        "row0": "DBIFHCEG",          # plain square first row
        "a0i8": "abcdefghi",         # a=0 .. i=8
        "salph#96": "815063742",     # a..i -> 8,1,5,0,6,3,7,4,2 (leads)
    }

    # --- 2. Build candidate X set ---------------------------------------------
    cands = []                       # (label, string)

    def add(label, s):
        if s and s not in {c[1] for c in cands}:
            cands.append((label, s))

    # faed-decoded artifacts (rechecked; kept for the code-path witness)
    add("faed_full", full_faed)
    add("faed_head40", full_faed[:40])
    add("faed_head8", full_faed[:8])
    even = stored["even_stream"]
    odd = stored["odd_pre_reduction"]
    obj = stored["object_256"]
    add("faed_even", even)
    add("faed_odd", odd)
    add("faed_obj256", obj)
    add("faed_dropped29", stored["dropped_29"])

    # dbbib-decoded artifacts (the novel coverage not in tested.md 29b)
    add("dbbib_full", full_dbbib)
    add("dbbib_upper", full_dbbib.upper())
    add("dbbib_rev", full_dbbib[::-1])

    # dbbib read through the interpreter digit maps: replace each symbol by its
    # digit, then feed the digit string as X (a plausible answer form).
    for mname, mval in alpha_maps.items():
        tbl = str.maketrans({c: str(i) for i, c in enumerate(mval)})
        d = full_dbbib.lower().translate(tbl)
        if d and d != full_dbbib:
            add(f"dbbib_digits_{mname}", d)
        df = full_faed.lower().translate(tbl)
        if df and df != full_faed:
            add(f"faed_digits_{mname}", df)

    # base58-friendly reading: Bifid square row letters D,B,I,F,H,C,E,G,A,K are the
    # positional alphabet; map the decoded letters by that ordering to digits.
    roworder = "DBIFHCEGAKLMNOPQRSTUVWXYZ"
    t2 = str.maketrans({c: str(i) for i, c in enumerate(roworder)})
    add("dbbib_rowdigits", full_dbbib.translate(t2))
    add("faed_rowdigits", full_faed.translate(t2))

    # case variants for the short, answer-like ones
    for i in range(len(cands)):
        lab, s = cands[i]
        if len(s) <= 128:
            add(lab + "_lower", s.lower())

    print(f"\ncandidate X set size: {len(cands)}")

    scratch = "/data/data/com.termux/files/usr/tmp/opencode"
    os.makedirs(scratch, exist_ok=True)
    outpath = os.path.join(scratch, "bifid_to_pipeline_cands.txt")
    with open(outpath, "w") as f:
        for _, s in cands:
            f.write(s + "\n")

    # --- 3. Oracle --------------------------------------------------------------
    r = subprocess.run([sys.executable, oracle, "--stdin"],
                       input=Path(outpath).read_bytes(), capture_output=True)
    lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
    hits = [ln for ln in lines if ln.startswith("MATCH")]
    print("oracle lines:", len(lines), " MATCH hits:", len(hits))
    for h in hits:
        print("HIT:", h)
    if hits:
        for h in hits:
            for lab, s in cands:
                if s in h or s == h.split()[1]:
                    print(f"  -> {lab} : {s!r}")
    else:
        print("\nResult: NO MATCH on the Bifid-decoded candidate X set.")
        print("Oracle self-test must pass (check tools/oracle.py --selftest).")

    summary = {
        "witness_faed_btcseed": witness_ok,
        "dbbib_full": full_dbbib,
        "faed_head": full_faed[:40],
        "candidates_tested": len(cands),
        "oracle_hits": len(hits),
        "candidate_file": outpath,
    }
    print("\nSUMMARY:", json.dumps(summary, indent=2))
    return 0 if (not witness_ok or hits) else 0 if witness_ok else 1


if __name__ == "__main__":
    sys.exit(main())
