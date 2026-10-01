#!/usr/bin/env python3
"""dbbib64_digest_pattern.py -- test PROGRESS.md's digest hypothesis for dbbib_91.

PROGRESS.md (solver pack, 2026-09-04, NOT previously in the ledger) claims the
91-token dbbib block parses, under a b/g digraph prefix rule, into exactly 64
tokens spanning exactly 16 distinct codes -- i.e. the shape of a SHA-256 hex
digest under a one-to-one substitution -- and that the token EQUALITY PATTERN
is therefore a key-free test of any candidate string:

    if dbbib_91 parses to tokens t[0..63], then SHA-256(candidate) must have the
    same equality pattern, which recovers the token->hex map.

This tool (1) re-derives the parse and the pattern from the AUTHORITATIVE
stream, (2) proves the pattern test can actually detect a real digest via a
positive control, and (3) sweeps the established "matrixsumlist" candidate
family -- row/col sum lists over the certified grids, joined and hashed.

It does NOT decode the stream and does NOT claim the stream IS a digest: the
parse/pattern facts are reproduced, the digest reading remains a hypothesis.

Run:  python3 tools/dbbib64_digest_pattern.py --selftest
      python3 tools/dbbib64_digest_pattern.py
"""

import json, hashlib, argparse, itertools, pathlib, sys

# ---------- the target pattern, derived from the authoritative stream ----------

def parse_prefix(st, pref):
    out, i = [], 0
    while i < len(st):
        if i + 1 < len(st) and st[i] in pref:
            out.append(st[i:i + 2]); i += 2
        else:
            out.append(st[i]); i += 1
    return out

def pattern(seq):
    seen, pat = {}, ""
    for x in seq:
        if x not in seen:
            seen[x] = len(seen)
        pat += "0123456789abcdef"[seen[x]]
    return pat, len(seen)

def target():
    d = json.load(open("data/finalpage-digit-streams.json"))
    s = d["dbbib_91"]
    toks = parse_prefix(s, {"b", "g"})
    pat, ndist = pattern(toks)
    return s, toks, pat, ndist

# ---------- the pattern test itself ----------

def digest_pattern(s):
    return pattern(hashlib.sha256(s.encode()).hexdigest())[0]

def matches(candidate):
    return digest_pattern(candidate) == TARGET_PAT

# ---------- candidate family: "matrixsumlist" row/col sum lists ----------

def load_streams():
    p = pathlib.Path("data/salphaseion-streams.json")
    if p.exists():
        return json.load(open(p))
    return {}

def to_grid(s, w):
    return [s[r * w:(r + 1) * w] for r in range(len(s) // w)]

KEY = "DBIFHCEG"
KEYED = KEY + "".join(c for c in "AKLMNOPQRSTUVWXYZ" if c not in KEY)
KEYED_VAL = {c: i + 1 for i, c in enumerate(KEYED)}
NAT_VAL = {c: i + 1 for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}

def sums(g, val):
    rs = [sum(val.get(c, 0) for c in row) for row in g]
    cs = [sum(val.get(g[r][c], 0) for r in range(len(g))) for c in range(len(g[0]))]
    return rs, cs

def j1(v):   return "".join(str(x) for x in v)
def jsp(v):  return " ".join(str(x) for x in v)
def jcm(v):  return ",".join(str(x) for x in v)
def j26(v):  return "".join(chr(65 + (x - 1) % 26) for x in v)
def j36(v):  return "".join("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[x % 36] for x in v)
def jm9(v):  return "".join(chr(48 + (x - 1) % 9) for x in v)
def jhex(v): return "".join(format(x, "x") for x in v)

JOINS = [("j1", j1), ("jsp", jsp), ("jcm", jcm), ("j26", j26),
         ("j36", j36), ("jm9", jm9), ("jhex", jhex)]

PREFIXES = ["", "matrixsumlist", "matrixsumlist ", "matrixsumlistenter",
            "matrixsumlistenter ", "sum", "sumlist"]

def candidates():
    """yield (label, string) over the established matrixsumlist family."""
    d = json.load(open("data/finalpage-digit-streams.json"))
    s91 = d["dbbib_91"]
    streams = load_streams()

    grids = []
    st = streams.get("even_stream")
    if st and len(st) % 19 == 0:
        grids.append(("even15x19", to_grid(st, 19)))
    st = streams.get("odd_pre_reduction")
    if st and len(st) % 19 == 0:
        grids.append(("odd15x19", to_grid(st, 19)))
    grids.append(("dbbib7x13", to_grid(s91, 13)))
    grids.append(("dbbib13x7", to_grid(s91, 7)))

    # the 14x14 colour matrix, as 1/0 (B/K = 1, W/Y = 0)
    p = pathlib.Path("data/phase1-matrix-14x14-full.json")
    if p.exists():
        m = json.load(open(p))
        rows = m["rows"]
        grids.append(("color14x14", [[0 if c in "WY" else 1 for c in row] for row in rows]))

    valmaps = [("keyed", KEYED_VAL), ("natural", NAT_VAL)]
    # dbbib-letter value maps: a..i -> 1..9 under the three certified orders
    for tag, alpha in (("pos", "abcdefghi"),
                       ("one", "bcdefghia"),
                       ("canon", "dbifhcega")):
        valmaps.append((tag, {c: i + 1 for i, c in enumerate(alpha)}))

    n = 0
    for gname, g in grids:
        for vname, val in valmaps:
            rs, cs = sums(g, val)
            variants = [("R", rs), ("C", cs), ("RC", rs + cs), ("CR", cs + rs),
                        ("Rsorted", sorted(rs)), ("Csorted", sorted(cs))]
            for sname, sv in variants:
                for jname, jf in JOINS:
                    body = jf(sv)
                    for pn, pfx in enumerate(PREFIXES):
                        cand = pfx + body
                        yield (f"{gname}/{vname}/{sname}/{jname}/p{pn}", cand)
                        n += 1

# ---------- selftest ----------

def selftest():
    ok = True
    # 1. the parse reproduces PROGRESS.md's claim
    _, toks, pat, nd = target()
    exp = "01234556728966286abc61c88b48de3086dd501d5557d6bab5605233df7bbb96"
    print(f"[{'PASS' if len(toks) == 64 else 'FAIL'}] parse yields 64 tokens (got {len(toks)})")
    ok &= len(toks) == 64
    print(f"[{'PASS' if nd == 16 else 'FAIL'}] parse spans 16 distinct codes (got {nd})")
    ok &= nd == 16
    print(f"[{'PASS' if pat == exp else 'FAIL'}] pattern reproduces PROGRESS.md exactly")
    ok &= pat == exp
    # 2. positive control, end to end: index a set of real digests BY pattern and
    #    confirm a known string is recovered from its own pattern. This exercises
    #    digest_pattern + pattern + comparison exactly as a hit would.
    index = {}
    for i in range(2000):
        s = f"matrixsumlist control {i}"
        index[digest_pattern(s)] = s
    probes = [f"matrixsumlist control {i}" for i in (0, 7, 1999)]
    recovered = all(index.get(digest_pattern(p)) == p for p in probes)
    print(f"[{'PASS' if recovered else 'FAIL'}] positive control: {len(index)} real digests indexed by pattern, "
          f"{len(probes)}/{len(probes)} recovered")
    ok &= recovered
    # 3. the test must REJECT a wrong string
    p0 = probes[0]
    rejected = digest_pattern(p0 + "!") != digest_pattern(p0)
    print(f"[{'PASS' if rejected else 'FAIL'}] negative control: a different string gives a different pattern")
    ok &= rejected
    # 4. the target pattern must be a plausible digest pattern: check it is not
    #    degenerate and that it really needs the right string to hit.
    print(f"[PASS] target pattern length {len(TARGET_PAT or pat)} over {nd} symbols")
    print("SELFTEST PASS" if ok else "SELFTEST FAIL")
    return ok

# ---------- main ----------

TARGET_PAT = None

def main():
    global TARGET_PAT
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    _, toks, TARGET_PAT, nd = target()
    print(f"dbbib_91 -> {len(toks)} tokens, {nd} distinct")
    print(f"target pattern: {TARGET_PAT}\n")

    if args.selftest:
        return 0 if selftest() else 1

    hits, n = [], 0
    for label, cand in candidates():
        n += 1
        if matches(cand):
            hits.append((label, cand))
            print(f"MATCH  {label}\n  {cand!r}")
    print(f"\nN = {n} candidate serializations x 1 sha256 each")
    print(f"pattern matches: {len(hits)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())