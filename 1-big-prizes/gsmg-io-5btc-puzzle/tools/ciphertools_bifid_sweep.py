#!/usr/bin/env python3
"""ciphertools.co.uk Bifid (blank period = full message) reproduction + oracle sweep.

1. Certify ciphertools' Bifid convention reproduces the puzzle's confirmed stage:
   given the faed ciphertext (570, trailing z stripped) and the documented keyed
   square DBIFHCEG, Bifid-DECRYPT with blank period must yield plaintext head
   BTCSEED.... (matches salphaseion-streams.json).
2. Then run ciphertools Bifid ENCRYPT and DECRYPT (blank period) over every open
   object/stream (object_256, even_stream, odd_pre_reduction, dropped_29, faed,
   dbbib) and push every resulting string + case/reversal through the oracle.
NOTE: the reproduction is a WITNESS that the tool variant matches the puzzle's
own Bifid step; the base object-level Bifid-on-Bifid is essentially a no-op for
the self-matching square, so the sweep mostly covers keyword variants and
encrypt-direction transformations.
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
    grid = [list(keyed[i * 5:(i + 1) * 5]) for i in range(5)]
    pos = {}
    for r in range(5):
        for c in range(5):
            pos[grid[r][c]] = (r, c)
    return grid, pos


def _to_upper(s):
    return "".join(ch.upper() for ch in s if ch.upper() in ALPHA)


def bifid_encrypt(pt, period, grid, pos):
    coords = [pos[ch] for ch in _to_upper(pt)]
    combined = []
    for r, c in coords:
        combined.append(r)
        combined.append(c)
    out = ""
    for start in range(0, 2 * len(coords), 2 * period):
        block = combined[start:start + 2 * period]
        rs, cs = block[:len(block) // 2], block[len(block) // 2:]
        for k in range(len(rs)):
            out += grid[rs[k]][cs[k]]
    return out


def bifid_decrypt(ct, period, grid, pos):
    coords = [pos[ch] for ch in _to_upper(ct)]
    combined = []
    for r, c in coords:
        combined.append(r)
        combined.append(c)
    out = ""
    for start in range(0, 2 * len(coords), 2 * period):
        block = combined[start:start + 2 * period]
        rs, cs = block[:len(block) // 2], block[len(block) // 2:]
        for k in range(len(rs)):
            out += grid[rs[k]][cs[k]]
    return out


def sh(s):
    return hashlib.sha256(s.encode()).hexdigest()


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    streams = json.loads(Path(os.path.join(base, "data", "salphaseion-streams.json")).read_text())
    obj = streams["object_256"]
    even = streams["even_stream"]
    odd = streams["odd_pre_reduction"]
    dropped = streams["dropped_29"]

    # --- 1. WITNESS: reproduce the confirmed stage with ciphertools convention ---
    print("== WITNESS: ciphertools Bifid(DBIFHCEG, blank period) reproduce stage ==")
    # faed ciphertext: take the decrypted direction input. We need faed 570 text.
    # The stored provenance gives plaintext_head but not raw faed here; use the
    # full decoded faed from tested.md / community: reconstruct by encrypting the
    # stage plaintext is circular. Instead reproduce using known faed from the
    # raw token stream if available, else report witness state.
    grid, pos = build_grid("DBIFHCEG")
    gs = "".join("".join(row) for row in grid)
    print("square row-major:", gs)

    # Attempt: the 256 object is the ODD-stream subset (I/O removed). The
    # even_stream is the even half. If ciphertools Bifid ENC(DBIFHCEG) over the
    # concatenation reproduces a known faed-derived string, that is the witness.
    # We instead directly verify with the known faed if present in raw streams.
    raw = None
    try:
        raw = json.loads(Path(os.path.join(base, "data", "finalpage-digit-streams.json")).read_text())
    except Exception:
        pass
    faed = None
    if raw:
        faed = raw.get("faed_570")
    if not faed:
        # fall back to building faed from the page's stored raw SPA text if present
        pass
    if faed:
        faed_clean = faed.rstrip("z")
        dec = bifid_decrypt(faed_clean, len(faed_clean), grid, pos)
        print("faed_clean len", len(faed_clean), "-> decrypt head:", dec[:20])
        print("expected head: BTCSEEDDEOEMC...")
        print("WITNESS match:", dec.startswith("BTCSEED"))
    else:
        print("no raw faed loaded; witness deferred (uses stored object only)")

    # --- 2. oracle sweep --------------------------------------------------------
    print("\n== sweep: Bifid over objects/streams, keyword variants, both directions ==")
    keywords = ["", "DBIFHCEG", "GSMG", "BTCSEED", "SALPHASEION", "THEMATRIXHASYOU",
                "COSMICDUALITY", "CAUSALITY", "BIFID", "POLYBIUS", "MATRIXSUM",
                "THISPASSWORD", "YINYANG", "YELLOWBLUE", "PRIMES"]
    objects = {
        "obj256": obj,
        "even": even,
        "odd": odd,
        "dropped29": dropped,
        "even+odd": even + odd,
        "odd+even": odd + even,
    }
    if faed:
        objects["faed"] = faed.rstrip("z")
    # dbbib raw
    dbbib = raw.get("dbbib_91") if raw else None
    if dbbib:
        objects["dbbib_91"] = dbbib   # authoritative; "dbbib" is the crop

    candidates = []
    for oname, otext in objects.items():
        if not otext:
            continue
        # strip I/O ambiguity letters when alphabet is ID-merged
        for kw in keywords:
            g, p = build_grid(kw)
            for direction, out in [("enc", bifid_encrypt(otext, len(otext), g, p)),
                                   ("dec", bifid_decrypt(otext, len(otext), g, p))]:
                if not out:
                    continue
                for var, ss in [("raw", out), ("lower", out.lower()),
                                ("rev", out[::-1]), ("revlower", out[::-1].lower()),
                                ("upper", out.upper())]:
                    candidates.append((oname, kw, direction, var, ss))

    seen = set()
    uniq = []
    for oname, kw, direction, var, ss in candidates:
        if ss not in seen:
            seen.add(ss)
            uniq.append((oname, kw, direction, var, ss))
    print("candidate count:", len(uniq))

    outpath = "/data/data/com.termux/files/usr/tmp/opencode/ciphertools_bifid_cands.txt"
    with open(outpath, "w") as f:
        f.writelines(c[4] + "\n" for c in uniq)

    r = subprocess.run(
        [sys.executable, os.path.join(base, "tools", "oracle.py"), "--stdin"],
        input=Path(outpath).read_bytes(), capture_output=True)
    lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
    hits = [ln for ln in lines if ln.startswith("MATCH")]
    print("oracle lines:", len(lines), " hits:", len(hits))
    for h in hits:
        print("HIT:", h)
    # map hits back
    if hits:
        hset = {h.split()[1] for h in hits}
        for c in uniq:
            if c[4] in hset or any(c[4] in h for h in hits):
                print("  ->", c)


if __name__ == "__main__":
    main()
