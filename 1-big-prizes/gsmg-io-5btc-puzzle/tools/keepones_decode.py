#!/usr/bin/env python3
"""Keep the 9 one-position subset (per the 24-bit white-rabbit key) of dbbib/faed, then
run the certified Bifid(DBIFHCEG) decode and certified checkerboard decode on each subset,
and oracle-test every resulting candidate on both gate addresses.

The 24-bit key is applied cyclically (i%24) over the stream; symbols at key-bit=1 are kept.
Subsets are then decoded with the certified Bifid(DBIFHCEG, width-5 square, full-period)
convention and the certified straddling checkerboard (DBIFHCEG/CANON/POS keyed alphabets),
plus the raw subset itself, and every X candidate hashed per gate.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "."))
from certified_vic import CANON, POS, build_grid
from certified_vic import decode as vic_decode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())
DBBIB = d["dbbib_91"]   # authoritative; d["dbbib"] is the crop
FAED = d["faed_570"].rstrip("z")
KEYBITS = "010000011101010001100100"
KB = [int(b) for b in KEYBITS]
ONES = [i for i, b in enumerate(KB) if b == 1]
print("key one-positions (0-based):", ONES)

# Certified Bifid DBIFHCEG (5x5, J dropped), rows-then-columns, full period (reconstructs BTCSEED stage)
SQUARE = ("DBIFHCEG" + "".join(c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in "DBIFHCEGJ"))
def bifid_decrypt(s):
    s = s.upper()
    pos = {ch: (i // 5, i % 5) for i, ch in enumerate(SQUARE)}
    if any(ch not in pos for ch in s):
        return s
    rc = [pos[ch] for ch in s]
    stream = [r for r, c in rc] + [c for r, c in rc]
    half = len(stream) // 2
    return "".join(SQUARE[r * 5 + c] for r, c in zip(stream[:half], stream[half:]))

def keep_ones(s):
    return "".join(ch for i, ch in enumerate(s) if KB[i % 24] == 1)

def keep_zeros(s):
    return "".join(ch for i, ch in enumerate(s) if KB[i % 24] == 0)

def main():
    cands = {}
    streams = {"dbbib": DBBIB, "faed": FAED, "dbbib+faed": DBBIB + FAED, "faed+dbbib": FAED + DBBIB}
    for sname, s in streams.items():
        k1 = keep_ones(s)
        k0 = keep_zeros(s)
        for label, sub in [("keep1", k1), ("keep0", k0)]:
            cands.setdefault(sub, []).append((sname, label, "raw"))
            cands.setdefault(sub.upper(), []).append((sname, label, "raw.upper"))
            b = bifid_decrypt(sub)
            cands.setdefault(b, []).append((sname, label, "bifid"))
            cands.setdefault(b.upper(), []).append((sname, label, "bifid.upper"))
        # checkerboard decode of keep1/keep0 under DBIFHCEG/CANON/POS alphabets
        for label, sub in [("keep1", k1), ("keep0", k0)]:
            for mname, mp in [("CANON", CANON), ("POS", POS)]:
                if any(c not in mp for c in sub):
                    continue
                digits = "".join(str(mp[c]) for c in sub)
                for alpha_name, alpha in [("DBIFHCEG", "DBIFHCEG"), ("CANON", "DBIFHCEG"), ("POS", "DBIFHCEG")]:
                    a28 = alpha + "." + "".join(c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in alpha)
                    # just use the 26-letter DBIFHCEG-keyed alphabet and a couple alpha variants
                    for e1, e2 in [(1, 4), (1, 3), (2, 4)]:
                        ctol = build_grid(a28, e1, e2)
                        dec = vic_decode(digits, ctol, e1, e2)
                        if "?" not in dec and len(dec) >= 7:
                            cands.setdefault(dec, []).append((sname, label, f"vic_{mname}_{e1}{e2}"))

    keys = list(cands.keys())
    path = "/data/data/com.termux/files/usr/tmp/opencode/keepones_decode_cands.txt"
    with open(path, "w") as f:
        f.writelines(k + "\n" for k in keys)
    print("candidate count:", len(keys))
    for k in keys: print("  ", repr(k[:60]))

    for gname, oracle in [("small", "tools/oracle.py"), ("dualite", "tools/oracle_dualite.py")]:
        r = subprocess.run([sys.executable, os.path.join(ROOT, oracle), "--stdin"],
                           input=Path(path).read_bytes(), capture_output=True)
        hits = [l for l in r.stdout.decode().splitlines() if l.startswith("MATCH")]
        print(f"[{gname}] MATCH={len(hits)}")
        for h in hits:
            print(" HIT:", h)
        if not hits:
            print(f"[{gname}] NO MATCH")

if __name__ == "__main__":
    main()
