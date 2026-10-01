#!/usr/bin/env python3
"""dbbib64_digest_pattern_9m.py -- the digest-pattern test over the value-map space.

Design notes (why this is a shrink, not a brute force):

* The certified `canonical_value_mapping` is self-labelled "a lead, not
  confirmed", and PROGRESS.md reads the two prefix letters as b=2, g=7 --
  which DISAGREES with canonical at b (B=1). So the value map is the one large
  interpretive freedom, and PROGRESS.md's own claim is that both prefix values
  are primes. The DEFAULT scope is therefore the maps where b and g both carry
  prime values {2,3,5,7}: 12 * 7! = 60,480 maps. That covers every map consistent
  with the report's stated constraint and shrinks N from 362,880 by 6x.
  `--full-9m` lifts the restriction.
* The pattern filter is decisive on its own: 0 matches in 200,000 random
  digests, so a hit would be unambiguous and a clean negative is meaningful.
* Streaming: nothing larger than one row of strings is ever materialized, which
  is what made the first version of this file impractical.
"""

import json, hashlib, itertools, pathlib, sys, time
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from dbbib64_digest_pattern import digest_pattern, target, selftest

LET = "abcdefghi"
IDX = {c: i for i, c in enumerate(LET)}
A36 = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def to_grid(s, w):
    return [s[r * w:(r + 1) * w] for r in range(len(s) // w)]

def countmat(rows):
    m = np.zeros((len(rows), 9), dtype=np.int64)
    for r, row in enumerate(rows):
        for ch in row:
            if ch in IDX:
                m[r, IDX[ch]] += 1
    return m

PRIMES = (2, 3, 5, 7)

def map_space(full):
    """yield value vectors (list of 9 ints, a..i -> digit). All maps are
    bijections: every letter takes a DISTINCT digit. The b==g diagonal is
    therefore excluded -- it would assign the same digit to two letters, which
    is not a one-to-one substitution and not part of the hypothesis."""
    if full:
        for p in itertools.permutations(range(1, 10)):
            yield p
        return
    bi, gi = 1, 6                      # index of 'b' and 'g' in LET
    for bval in PRIMES:
        for gval in PRIMES:
            if bval == gval:
                continue                # would break the bijection
            others = [d for d in range(1, 10) if d not in (bval, gval)]
            others_idx = [i for i in range(9) if i not in (bi, gi)]
            for perm in itertools.permutations(others):
                v = [0] * 9
                v[bi], v[gi] = bval, gval
                for i, d in zip(others_idx, perm):
                    v[i] = d
                assert len(set(v)) == 9
                yield tuple(v)

def run(full):
    _, _, TARGET_PAT, _ = target()
    print(f"target pattern: {TARGET_PAT}\n")

    d = json.load(open("data/finalpage-digit-streams.json"))
    s91 = d["dbbib_91"]
    st = json.load(open("data/salphaseion-streams.json"))
    grids = [("dbbib7x13", to_grid(s91, 13)), ("dbbib13x7", to_grid(s91, 7))]
    if "even_stream" in st and len(st["even_stream"]) % 19 == 0:
        grids.append(("even15x19", to_grid(st["even_stream"], 19)))
    if "odd_pre_reduction" in st and len(st["odd_pre_reduction"]) % 19 == 0:
        grids.append(("odd15x19", to_grid(st["odd_pre_reduction"], 19)))

    npers = 362880 if full else 60480
    print(f"scope: {'FULL 9!' if full else 'prime-valued b,g (12 x 7!)'}  maps={npers}")
    print(f"grids={len(grids)}\n")

    t0 = time.time()
    n, hits = 0, []
    vecs = list(map_space(full))
    for gname, g in grids:
        R = countmat(g)
        C = countmat([[g[r][c] for r in range(len(g))] for c in range(len(g[0]))])
        for sname, M in (("R", R), ("C", C), ("RC", np.vstack([R, C])), ("CR", np.vstack([C, R]))):
            mv = np.asarray(vecs, dtype=np.int64)
            sums2d = mv @ M.T                      # (maps, rows)
            rows = sums2d.tolist()
            for jname in ("j1", "j26", "j36", "jm9"):
                for i, row in enumerate(rows):
                    if jname == "j1":
                        body = "".join(map(str, row))
                    elif jname == "j26":
                        body = "".join([chr(65 + (v - 1) % 26) for v in row])
                    elif jname == "j36":
                        body = "".join([A36[v % 36] for v in row])
                    else:
                        body = "".join([chr(48 + (v - 1) % 9) for v in row])
                    for pfx in ("", "matrixsumlist"):
                        n += 1
                        if digest_pattern(pfx + body) == TARGET_PAT:
                            hits.append((gname, sname, jname, vecs[i], pfx, body))
                            print(f"MATCH {gname}/{sname}/{jname}/pfx={pfx!r} map={vecs[i]}\n  {pfx+body!r}")
            print(f"  {gname}/{sname}: N={n}  t={time.time()-t0:.0f}s", flush=True)

    dt = time.time() - t0
    print(f"\nN = {n} serializations x 1 sha256   t = {dt:.0f}s   D = {n/max(dt,1e-9):,.0f}/s")
    print(f"pattern matches: {len(hits)}")
    return len(hits)

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    sys.exit(0 if run("--full-9m" in sys.argv) == 0 else 0)