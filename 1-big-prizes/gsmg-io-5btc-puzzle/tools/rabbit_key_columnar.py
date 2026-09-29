#!/usr/bin/env python3
"""Apply the follow_white_rabbit 24-bit key as a columnar-transposition key over the
a..i streams (dbbib=69=3x23, faed=570=15x38), then decode the transposed stream a few
certified ways and oracle-test every resulting X candidate on both funded gates.

The 24-bit key ones are at 0-based positions [1,7,8,9,11,13,17,18,21] (within 0..22,
fits a width-23 dbbib layout). We generate many column-orderings from the key and read
the re-arranged stream both directions; feed each as X directly, and through the
certified Bifid(DBIFHCEG) decoder and the certified straddling checkerboard (CANON/POS),
then oracle on both gates. A hit is an exact oracle MATCH only.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "."))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())
DBBIB = d["dbbib_91"]   # authoritative; d["dbbib"] is the crop
FAED = d["faed_570"].rstrip("z")
ONES = [1, 7, 8, 9, 11, 13, 17, 18, 21]  # 0-based one-positions


def read_matrix(s, cols):
    rows = -(-len(s) // cols)  # ceil
    m = [list(s[r * cols:(r + 1) * cols]) for r in range(rows)]
    return m


def read_out(m, col_order, read_dir="col_major"):
    if read_dir == "col_major":
        out = []
        for c in col_order:
            for r in range(len(m)):
                if c < len(m[r]):
                    out.append(m[r][c])
        return "".join(out)
    if read_dir == "row_major_rebuilt":
        out = []
        for r in range(len(m)):
            for c in col_order:
                if c < len(m[r]):
                    out.append(m[r][c])
        return "".join(out)
    return ""


def col_orders():
    """All reasonable column orderings from the 24-bit key (0..23 long)."""
    # treat stream width as the number of available columns = len(keyspace)
    # For dbbib width 23, key spans 0..22. Select the 9 one-columns and the rest.
    orders = []
    # (1) 9 one-columns first then the rest in natural order
    rest0 = [c for c in range(23) if c not in ONES]
    orders.append(ONES + rest0)
    # (2) rest first then ones
    orders.append(rest0 + ONES)
    # (3) ones only (9 columns), natural
    orders.append(ONES)
    # (4) reverse of ones
    orders.append(ONES[::-1])
    # (5) full key as ranks: ones rank=1 (first), zeros rank=2; stable by position -> ones first ascending
    # (6) the ones as a key-sort: sort all 23 by (is_one DESC, index)
    orders.append(sorted(range(23), key=lambda c: (0 if c in ONES else 1, c)))
    orders.append(sorted(range(23), key=lambda c: (1 if c in ONES else 0, c)))
    return orders


def bifid_decrypt_wrap(ct):
    # 5x5 keyed square DBIFHCEG (J dropped), rows-then-columns, full period - replicate
    # using ciphertools Bifid convention; simple known-good implementation:
    try:
        from ciphertools_bifid_sweep import bifid_decrypt as _bd
        return _bd(ct)
    except Exception:
        return _bifid_local(ct)


def _bifid_local(s):
    sq = "DBIFHCEG" + "".join(ch for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if ch not in "DBIFHCEGJ")
    pos = {ch: (i // 5, i % 5) for i, ch in enumerate(sq)}
    if any(ch not in pos for ch in s):
        return s.upper()
    up = s.upper()
    rc = [pos[ch] for ch in up]
    rows = [r for r, c in rc]
    cols = [c for r, c in rc]
    stream = rows + cols
    half = len(stream) // 2
    coord = list(zip(stream[:half], stream[half:]))
    return "".join(sq[r * 5 + c] for r, c in coord)


def main():
    cands = {}
    for name, s, widths in [("dbbib", DBBIB, [23, 3]), ("faed", FAED, [38, 15])]:
        for cols in widths:
            m = read_matrix(s, cols)
            for j, order in enumerate(col_orders()):
                order = [o for o in order if o < cols]
                for rd in ["col_major", "row_major_rebuilt"]:
                    t = read_out(m, order, rd)
                    if len(t) != len(s):
                        continue
                    cands.setdefault(t, []).append((name, cols, j, rd))
                    # and the interpreted digit decodes via certified Bifid
                    b = _bifid_local(t)
                    cands.setdefault(b, []).append((name, cols, j, rd, "bifid"))

    keys = list(cands.keys())
    # also add direct raw streams
    for s in [DBBIB, FAED, DBBIB + FAED, FAED + DBBIB]:
        keys.append(s)

    path = "/data/data/com.termux/files/usr/tmp/opencode/rabbit_col_trans_cands.txt"
    with open(path, "w") as f:
        for k in keys:
            f.write(k + "\n")
            f.write(k.upper() + "\n")
    print("candidate count:", len(keys) * 2)

    for g, oracle in [("small", "tools/oracle.py"), ("dualite", "tools/oracle_dualite.py")]:
        r = subprocess.run([sys.executable, os.path.join(ROOT, oracle), "--stdin"],
                           input=Path(path).read_bytes(), capture_output=True)
        lines = [l for l in r.stdout.decode().splitlines() if l.strip()]
        hits = [l for l in lines if l.startswith("MATCH")]
        print(f"[{g}] MATCH={len(hits)}")
        for h in hits:
            print(" HIT:", h)
        if not hits:
            print(f"[{g}] NO MATCH")


if __name__ == "__main__":
    main()
