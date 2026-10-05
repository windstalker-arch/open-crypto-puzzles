#!/usr/bin/env python3
"""
R-XORSUMFMT: submit the matrix-sum LISTS themselves as candidate X.

Why this cell is open
---------------------
The page's certified instruction is `matrixsumlist` + `enter`, and R-XORSUM
(2026-10-04) FINDING 3 named three submission formats -- (a) the raw sum list,
(b) the sums mod 26, (c) the XOR-reduced A-Z string -- while explicitly logging
"0 candidates, 0 oracle calls". R-LEAD0-FORMAT (2026-09-27) attacked the same
30 renderings but its acceptance test was a LOCAL one (digest[:12] == E_S / a
gate hash160 / a 79-byte record digest) and it too logged "0 oracle calls".

So the question "does the sum list, written down, open either funded gate?" has
never been put to tools/oracle.py or tools/oracle_dualite.py in the A-matrix
(dbbib_91-derived) form. late-207/208 put the *phase-1 pixel grid's* 28 sums
through both oracles; those are different numbers (total 101) from the
dbbib_91-derived A-matrix sums (total 844).

Witness
-------
A target-swapped in-family positive control: the certified 5-token password
`matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist`
(R-EXT-ISSUES, community issue #108) decrypts the small blob to the certified
79-byte record sha256 1449a217..., whose K_C1 field derives to
1GKJzHQkgTBwwEGeXetsTMDoUzvwzs9yb4. Retargeting the oracle at that address and
feeding that password through the SAME attempt() code must return MATCH. If it
does not, the harness is broken and every NO MATCH below is void.

Usage:  python3 tools/xorsum_format_oracle.py
"""

import hashlib
import itertools
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import oracle as O            # noqa: E402
import oracle_dualite as OD   # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

V1 = {c: i + 1 for i, c in enumerate("abcdefghi")}   # a=1 .. i=9  (certified A-matrix)
V0 = {c: i for i, c in enumerate("abcdefghi")}      # a=0 .. i=8  (alternative)

CONTROL_PW = ("matrixsumlistenterlastwordsbeforearchichoicethispassword"
              "matrixsumlist")
CONTROL_ADDR = "1GKJzHQkgTBwwEGeXetsTMDoUzvwzs9yb4"


def load_streams():
    d = json.loads(Path(os.path.join(BASE, "data",
                                    "finalpage-digit-streams.json")).read_text())
    return d["dbbib_91"], d["faed_570"].rstrip("z")


def load_grid():
    g = json.loads(Path(os.path.join(BASE, "data",
                                    "phase1-matrix-14x14-full.json")).read_text())
    return [list(r) for r in g["rows"]]


def amat(A, V, fill="row"):
    """14x14 symmetric, zero diagonal, strict upper triangle filled from A."""
    M = [[0] * 14 for _ in range(14)]
    k = 0
    if fill == "row":
        for i in range(14):
            for j in range(i + 1, 14):
                v = V[A[k]]; k += 1
                M[i][j] = M[j][i] = v
    else:  # col-major upper triangle
        for j in range(14):
            for i in range(j):
                v = V[A[k]]; k += 1
                M[i][j] = M[j][i] = v
    return M


def rowsums(M):
    return [sum(r) for r in M]


def colsums(M):
    return [sum(M[i][j] for i in range(14)) for j in range(14)]


def gmat(grid, dark, blue, yellow):
    """dark/blue/yellow: sets of glyphs counted as 1."""
    hot = set(dark) | set(blue) | set(yellow)
    return [[1 if c in hot else 0 for c in r] for r in grid]


# ---------------------------------------------------------------- renderings

def renderings(S):
    """Every way to write a list of small integers down as one string."""
    out = {}

    def add(tag, s):
        if s and s not in out.values():
            out[tag] = s

    add("concat", "".join(str(v) for v in S))
    add("comma", ",".join(str(v) for v in S))
    add("space", " ".join(str(v) for v in S))
    add("bracket_sq", "[" + ",".join(str(v) for v in S) + "]")
    add("bracket_pr", "(" + ",".join(str(v) for v in S) + ")")
    add("bracket_cu", "{" + ",".join(str(v) for v in S) + "}")
    add("pad2", "".join(f"{v:02d}" for v in S))
    add("pad3", "".join(f"{v:03d}" for v in S))

    # A1Z26-style reductions
    for tag, f in (("m26", lambda v: v % 26),
                   ("m26p1", lambda v: v % 26 + 1),
                   ("m9", lambda v: (v - 1) % 9 + 1),
                   ("m9_0", lambda v: (v - 1) % 9)):
        letters = ""
        for v in S:
            r = f(v)
            if tag.startswith("m26"):
                letters += chr((r - 1) % 26 + 65)
            else:
                letters += chr((r - 1) % 9 + 97) if tag == "m9" else chr(r % 9 + 97)
        if letters:
            add(tag, letters)
            add(tag + "_low", letters.lower())

    # reversed order of the digit forms
    add("concat_rev", "".join(str(v) for v in reversed(S)))
    add("comma_rev", ",".join(str(v) for v in reversed(S)))
    return out


def case_variants(tag, s):
    yield tag, s
    yield tag + ":lower", s.lower()
    yield tag + ":upper", s.upper()


# ---------------------------------------------------------------- battery

def build_candidates(A, B, grid):
    cands = {}

    def put(tag, s):
        for t2, v in case_variants(tag, s):
            cands[t2] = v

    # --- candidate-generation self-check -------------------------------------
    # A silently-wrong sum list produces a battery of zeros that "passes" as a
    # negative. Assert the two anchor totals before spending oracle calls:
    # R-GRID76 fixes the B/K-dark pixel total at 101 with per-row sums
    # [6,10,8,7,6,6,5,4,9,9,7,8,7,9], and R-XORSUM F2 fixes the a=1..i=9
    # A-matrix at total 844.
    g_bk = gmat(grid, ("B", "K"), (), ())
    assert rowsums(g_bk) == [6, 10, 8, 7, 6, 6, 5, 4, 9, 9, 7, 8, 7, 9], rowsums(g_bk)
    assert sum(rowsums(g_bk)) == 101
    assert colsums(g_bk) == [8, 10, 8, 10, 8, 7, 3, 6, 7, 5, 9, 6, 6, 8], colsums(g_bk)
    a_m = amat(A, V1, "row")
    assert rowsums(a_m) == [55, 62, 58, 68, 76, 50, 63, 56, 55, 63, 67, 53, 59, 59]
    assert sum(rowsums(a_m)) == 844

    # --- A-matrix (dbbib_91 as the strict upper triangle of 14x14) -----------
    for vtag, V in (("a1", V1), ("a0", V0)):
        for fill in ("row", "col"):
            M = amat(A, V, fill)
            for fn, F in (("rowsum", rowsums), ("colsum", colsums)):
                for k, s in renderings(F(M)).items():
                    put(f"A.{vtag}.{fill}.{fn}.{k}", s)
            rs = rowsums(M)
            put(f"A.{vtag}.{fill}.sum", str(sum(rs)))
            # row+col interleaved, both orders (symmetric => same values, but the
            # 28-value shape is what late-207 tested for the pixel grid)
            cs = colsums(M)
            put(f"A.{vtag}.{fill}.rc", "".join(f"{x}{y}" for x, y in zip(rs, cs)))

    # --- G-matrix (the 14x14 pixel grid), three colour readings -------------
    gspecs = (
        ("BK", ("B", "K"), (), ()),
        ("by", (), ("B",), ("Y",)),
        ("BKby", ("B", "K"), ("B",), ("Y",)),
    )
    for gtag, dark, blue, yellow in gspecs:
        M = gmat(grid, dark, blue, yellow)
        for fn, F in (("rowsum", rowsums), ("colsum", colsums)):
            for k, s in renderings(F(M)).items():
                put(f"G.{gtag}.{fn}.{k}", s)
        rs, cs = rowsums(M), colsums(M)
        put(f"G.{gtag}.rc", "".join(f"{x}{y}" for x, y in zip(rs, cs)))
        put(f"G.{gtag}.cr", "".join(f"{y}{x}" for x, y in zip(rs, cs)))
        put(f"G.{gtag}.total", str(sum(rs)))

    # --- other factorisations of the same two streams ------------------------
    for tag, s, n in (("dbbib7x13", A, 13), ("dbbib13x7", A, 7),
                      ("faed38x15", B, 15), ("faed15x38", B, 38),
                      ("faed30x19", B, 19), ("faed19x30", B, 30),
                      ("faed57x10", B, 10), ("faed10x57", B, 10)):
        V = V1
        rows = [sum(V[c] for c in s[j:j + n]) for j in range(0, len(s), n)]
        cols = [sum(V[c] for c in s[j::n]) for j in range(n)]
        for fn, F in (("rowsum", rows), ("colsum", cols)):
            for k, r in renderings(F).items():
                put(f"{tag}.{fn}.{k}", r)
        put(f"{tag}.total", str(sum(rows)))

    # --- the two lists concatenated, both orders -----------------------------
    K = rowsums(amat(A, V1, "row"))
    R = [sum(V1[c] for c in B[j:j + 15]) for j in range(0, len(B), 15)]
    for k, s in renderings(K).items():
        put(f"KR.K.{k}", s + renderings(R)[k])
    for k, s in renderings(R).items():
        put(f"KR.R.{k}", renderings(K)[k] + s)

    # --- the XOR-reduced A-Z baselines R-XORSUM named as format (c) -----------
    for off in range(14):
        base = "".join(chr(((R[i] ^ K[(i + off) % 14]) % 26) + 65)
                       for i in range(len(R)))
        for t2, v in case_variants(f"xor26.off{off}", base):
            cands[t2] = v

    return cands


def main():
    A, B = load_streams()
    grid = load_grid()
    dual_blob = OD.load_dualite_b64()

    print("=" * 78)
    print("WITNESS 1 -- in-family positive control (target-swapped)")
    ctrl = O.decrypt_blob(O.BLOB_B64, CONTROL_PW, "md5")
    assert ctrl is not None and hashlib.sha256(ctrl).hexdigest().startswith("1449a217")
    addr = O.priv_to_address(ctrl[:32])[0]
    w1 = addr == CONTROL_ADDR
    print(f"  control pw -> B1_79B (sha256 1449a217): OK")
    print(f"  control K_C1 -> {addr}: {'OK' if w1 else 'FAIL'}")
    if not w1:
        print("WITNESS FAIL - every NO MATCH below would be void")
        return 1

    # same password through the REAL attempt(), asserting the real gate rejects it
    hit, _ = O.attempt(CONTROL_PW)
    w2 = not hit
    print(f"  same pw through real oracle.attempt() -> NO MATCH (gate is not it): "
          f"{'OK' if w2 else 'FAIL -- IMPOSSIBLE, investigate'}")
    if not w2:
        print("WITNESS FAIL")
        return 1

    junk_hit, _ = O.attempt("not-a-real-candidate-zzz")
    w3 = not junk_hit
    print(f"  junk candidate -> NO MATCH: {'OK' if w3 else 'FAIL'}")
    if not (w2 and w3):
        return 1

    # END-TO-END hit detection: retarget attempt() at the control address and
    # require the SAME password to register a MATCH. Without this, "0 MATCH"
    # below would be indistinguishable from a harness that cannot detect hits.
    saved = O.TARGET_ADDRESS
    O.TARGET_ADDRESS = CONTROL_ADDR
    try:
        end_hit, end_info = O.attempt(CONTROL_PW)
    finally:
        O.TARGET_ADDRESS = saved
    w4 = end_hit and end_info.get("address") == CONTROL_ADDR
    print(f"  attempt() retargeted at {CONTROL_ADDR[:12]}.. reports MATCH on the "
          f"control pw: {'OK' if w4 else 'FAIL'}"
          + (f"  [{end_info.get('password_form')}/{end_info.get('digest')}/"
             f"{end_info.get('reading')}]" if w4 else ""))
    if not w4:
        print("WITNESS FAIL - the battery cannot detect a hit; NO MATCH below is void")
        return 1

    # and the retarget must still reject a junk candidate
    O.TARGET_ADDRESS = CONTROL_ADDR
    try:
        j2, _ = O.attempt("not-a-real-candidate-zzz")
    finally:
        O.TARGET_ADDRESS = saved
    w5 = not j2
    print(f"  retargeted attempt() rejects junk: {'OK' if w5 else 'FAIL'}")
    if not w5:
        return 1

    cands = build_candidates(A, B, grid)
    print()
    print(f"=" * 78)
    print(f"BATTERY -- {len(cands)} literal sum-list renderings as candidate X")
    print()

    small_hits, dual_hits = [], []
    lines = 0
    for tag in sorted(cands):
        c = cands[tag]
        hit, info = O.attempt(c)
        lines += 1
        if hit:
            small_hits.append((tag, c, info))
        hit2, info2 = OD.attempt(c, dual_blob)
        lines += 1
        if hit2:
            dual_hits.append((tag, c, info2))

    print(f"  small  gate 1GSMG1JC9 : {len(cands)} candidates -> "
          f"{len(small_hits)} MATCH")
    print(f"  dualite gate 17ucy1K9 : {len(cands)} candidates -> "
          f"{len(dual_hits)} MATCH")
    print(f"  total oracle attempts : {lines}")
    for t in small_hits + dual_hits:
        print(f"  *** MATCH {t[0]} = {t[1]!r} {t[2]}")

    print()
    print("=" * 78)
    print("WITNESS 2 -- oracles still certified after the batch")
    ok1 = O.selftest()
    ok2 = OD.selftest()
    print()
    print(f"RESULT: small={len(small_hits)} dualite={len(dual_hits)} "
          f"candidates={len(cands)} selftest_small={ok1} selftest_dualite={ok2}")
    return 0 if (not small_hits and not dual_hits and ok1 and ok2) else 1


if __name__ == "__main__":
    sys.exit(main())
