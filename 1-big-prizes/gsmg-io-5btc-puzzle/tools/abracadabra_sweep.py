#!/usr/bin/env python3
"""Abracadabra diminishing-triangle family.

Steer: "abracadabra" (given alone, after the magician's-rabbit idiom).
ABRACADABRA is the classic 'magic word' written as a diminishing triangle
(the word writ small one letter per line)  -  a talismanic word-square/triangle
used since Serenus Sammonicus. Two bounded faithful hooks:

  (A) Geometry hook: dbbib_91 has EXACTLY T13 = 91 cells (1+2+...+13).
      Lay the 91-token stream rows 13,12,...,1 in a right triangle and read
      paths (rows, columns, diagonals, boustrophedon, spiral) -> candidate X.
      (Row 193 reinstated 91-token dbbib as the live object; no prior row laid
       it as T13. XOR-triangle rows 147/3537 were bit/digit-collapse reads, not
       this stream-into-triangle layout.)

  (B) Alphabet hook: 'abracadabra' as the diminishing triangle, its columns /
      spines / growing pyramid columns used as KEYED-28 interpreter alphabets
      over dbbib_91 / faed_570 (certified checkerboard).

Late-159 closed plain ABRACADABRA literally + as one keyed28 keyword (no
triangle). This row is only the triangular constructions.
"""
import json, pathlib

BASE = pathlib.Path(__file__).resolve().parents[1]
d = json.loads((BASE / "data" / "finalpage-digit-streams.json").read_text())
DBBIB = d["dbbib_91"]
FAED = d["faed_570"].rstrip("z")

CANON = {"d": 0, "b": 1, "i": 2, "f": 3, "h": 4, "c": 5, "e": 6, "g": 7, "a": 8}
POS = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9}
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed28(keyword):
    kw = "".join(ch for ch in keyword.upper() if ch in ALPHA)
    keyed = ""
    for ch in kw + ALPHA:
        if ch not in keyed:
            keyed += ch
    assert len(keyed) == 26, keyed
    return keyed[:8] + "." + keyed[8:18] + "/" + keyed[18:]


from certified_vic import build_grid, decode  # certified machinery (selfcert PASS)


def dig(s, mp):
    return "".join(str(mp[c]) for c in s)


WORD = "ABRACADABRA"
N = len(WORD)  # 11

# diminishing triangle rows: first row full word, each next row drops last char
def dim_rows(w):
    return [w[: k] for k in range(len(w), 0, -1)]


def grow_rows(w):
    return [w[: k] for k in range(1, len(w) + 1)]


def triangle_columns(rows):
    """Left-justified triangle: column j collects cell (r,j) for rows with len>j."""
    return ["".join(r[j] for r in rows if len(r) > j) for j in range(len(rows[0]))]


def triangle_diagonals(rows):
    n = len(rows)
    m = len(rows[0])
    out = []
    for d in range(-(n - 1), m):  # diagonal index along 45deg
        s = "".join(rows[r][c] for r in range(n) for c in range(len(rows[r])) if c - r == d)
        if s:
            out.append(s)
    return out


def paths():
    """Column/row/diagonal readings of the diminishing & growing triangles -> alphabets."""
    alphas = []
    for rows_fn in (dim_rows, grow_rows):
        rows = rows_fn(WORD)
        alphas += triangle_columns(rows)
        alphas += triangle_diagonals(rows)
        # columns of the right-justified triangle
        rj = [r.rjust(len(rows[0])) for r in rows]
        alphas += ["".join(r[j] for r in rj if r[j] != " ") for j in range(len(rj[0]))]
    # central spine (a-column of left triangle), cross words at each row length
    for rows in (dim_rows(WORD), grow_rows(WORD)):
        alphas.append("".join(r[0] for r in rows))
        alphas.append("".join(r[-1] for r in rows if r))
    return [a for a in dict.fromkeys(alphas) if a]


# (A) triangle layout of the 91-token stream: rows of length 13,12,...,1
def triangle_layout_candidates(stream):
    def read(grid_flat_rows):
        # grid_flat_rows: list of (rowlen, tokens) already sized
        return "".join(grid_flat_rows)
    rowsizes = list(range(13, 0, -1))
    assert sum(rowsizes) == 91
    idx = 0
    rows = []
    for k in rowsizes:
        rows.append(stream[idx: idx + k])
        idx += k
    cands = {}
    # contiguous top-down
    cands.setdefault(read(rows), "flat rows 13..1")
    cands.setdefault(read(rows[::-1]), "flat rows 1..13")
    # columns (slice positions)
    for j in range(13):
        col = "".join(r[j] for r in rows if len(r) > j)
        if col:
            cands.setdefault(col, f"column j={j}")
    # columns right-justified
    rj = [r.rjust(13) for r in rows]
    for j in range(13):
        col = "".join(r[j] for r in rj if r[j] != " ")
        if col:
            cands.setdefault(col, f"rj column j={j}")
    # diagonals c-r
    for d in range(-12, 13):
        diag = "".join(rows[r][c] for r in range(13) for c in range(13)
                       if c - r == d and c < len(rows[r]))
        if diag:
            cands.setdefault(diag, f"diag c-r={d}")
    # diagonals c+r (anti-diagonal)
    for s in range(0, 24):
        anti = "".join(rows[r][c] for r in range(13) for c in range(13)
                       if r + c == s and c < len(rows[r]))
        if anti:
            cands.setdefault(anti, f"anti s={s}")
    # boustrophedon: even rows forward, odd reversed
    b = "".join(r if i % 2 == 0 else r[::-1] for i, r in enumerate(rows))
    cands.setdefault(b, "boustrophedon 13..1")
    # inverse boustrophedon
    b2 = "".join(r if i % 2 == 1 else r[::-1] for i, r in enumerate(rows))
    cands.setdefault(b2, "boustrophedon rev-start")
    # column-then-row
    cols = "".join(r[j] for j in range(13) for r in rows if len(r) > j)
    cands.setdefault(cols, "columns then rows")
    return cands


def main():
    cands = {}
    for k, prov in triangle_layout_candidates(DBBIB).items():
        for form in {k, k.upper(), k.lower(), k[::-1]}:
            if form:
                cands.setdefault(form, ("tri91", prov))
    # also the same layout on the FIRST 171 of faed? No: only 91 fits T13.
    # spell-out abracadabra-token alphabets (B) through the certified checkerboard
    for a in paths():
        alpha = keyed28(a)
        for stream_name, stream in (("dbbib_91", DBBIB), ("faed_570", FAED)):
            for mpn, mp in (("canon", CANON), ("pos", POS)):
                ds = dig(stream, mp)
                for e1, e2 in [(1, 4), (0, 4), (1, 2)]:
                    ctol = build_grid(alpha, e1, e2)
                    dec = decode(ds, ctol, e1, e2)
                    for form in {dec, dec.lower(), dec[::-1]}:
                        if form:
                            cands.setdefault(form, ("tri28", a, stream_name, mpn, e1, e2))
    # a few whole-token alphabets for the triangle geometry (positions 1..91)
    position_alpha = "".join(chr(65 + (i % 26)) for i in range(26))  # spacer not needed
    uniq = [(k, v) for k, v in cands.items()]
    with open("/data/data/com.termux/files/usr/tmp/opencode/abracadabra_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/abracadabra_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()