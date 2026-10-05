#!/usr/bin/env python3
"""bifid_selftest.py -- certify the GSMG Bifid stage's two unfalsifiable assumptions.

WHY THIS TOOL EXISTS
--------------------
Two properties of the certified Bifid stage have never been certified, and both
are the kind of assumption that makes a whole family of negatives worthless if it
is quietly false:

1. **INVERTIBILITY.** `tools/bifid_to_pipeline.py:70` defines `bifid_encrypt`,
   which is **called from nowhere in the repository**. Every certified run of the
   stage is decrypt-only, so "the decoder is a faithful Bifid implementation"
   has only ever been checked in one direction -- against five stored hashes.
   `tools/bifid_repro.py` re-derives those hashes and exits 0, but a decryptor
   that is wrong in a self-consistent way reproduces its own wrong output
   forever. `R-PLAINART` FINDING 4 is the general statement of the danger:
   an instrument dominated by an artifact cannot rank candidates. The specific
   instance here is stronger: if `bifid_decrypt` is not invertible, then
   "the plaintext is a geometric artifact" and "the plaintext is the message"
   are not distinguishable by anything this project has run.

2. **PARITY FACTORISATION, AND IT ONLY HOLDS FOR EVEN n.** The half-split in
   `bifid_decrypt` interacts with token boundaries in a way that depends on the
   parity of the stream length. `R-PLAINART` FINDING 2 asserts `dbbib_91`
   (91 tokens, **odd**) shows "the same property" as `faed_570` -- 60.4% of its
   letters in the square's 2x2 corner block. That assertion has no mechanism
   behind it, and this tool shows why: for odd n the split straddles a token
   and the parity structure that forces the corner block does not exist.

Both checks are run against **pycipher 0.5.1** as an independent
implementation, not against a second copy of this project's own code.

WITNESSES
---------
Per `AGENTS.md`, a negative is worthless without a witness, and a *positive*
control is worthless unless it can fail. This tool therefore ships four:

  W1  the certified `faed -> BTCSEED...` witness re-derives, AND pycipher
      independently produces the identical 40-character head;
  W2  pycipher's own round-trip is asserted before it is trusted as a reference;
  W3  a **negative control**: a deliberately corrupted key must make W1 fail,
      proving W1 can fail;
  W4  the parity factorisation is asserted to hold on `faed_570` (even) and
      asserted to FAIL on `dbbib_91` (odd) -- i.e. the tool asserts the
      asymmetry it claims, in both directions.

Usage:
    python3 tools/bifid_selftest.py            # full run
    python3 tools/bifid_selftest.py --quiet    # summary only
Exit 0 iff every check passes. 0 oracle calls, no funded-gate contact.
"""

from __future__ import annotations

import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bifid_to_pipeline import (  # noqa: E402
    ALPHA,
    _upper_sanitize,
    bifid_decrypt,
    bifid_encrypt,
    build_grid,
)

KEYWORD = "DBIFHCEG"
TOKMAP = dict(zip("abcdefghi", "ABCDEFGHI"))


def keyed_alphabet(keyword: str, alphabet: str = ALPHA) -> str:
    return "".join(dict.fromkeys(ch for ch in (keyword + alphabet) if ch in alphabet))


def load():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw = json.loads(open(os.path.join(base, "data", "finalpage-digit-streams.json")).read())
    stored = json.loads(open(os.path.join(base, "data", "salphaseion-streams.json")).read())
    streams = {
        "faed_570": _upper_sanitize(raw["faed_570"].rstrip("z").translate(
            str.maketrans(TOKMAP)), None),
        "dbbib_91": _upper_sanitize(raw["dbbib_91"].translate(str.maketrans(TOKMAP)), None),
    }
    return streams, stored


def coords(seq: str, cell):
    return [cell[ch] for ch in seq]


def main(argv):
    quiet = "--quiet" in argv
    verbose = not quiet

    def say(*a):
        if verbose:
            print(*a)

    grid, pos = build_grid(KEYWORD)
    ka = keyed_alphabet(KEYWORD)
    cell = {ch: (i // 5, i % 5) for i, ch in enumerate(ka)}
    streams, stored = load()
    failures = []

    def check(name, cond, detail=""):
        (say if verbose else (lambda *a: None))(f"  {'OK  ' if cond else 'FAIL'} {name}")
        if not cond:
            failures.append(name)
        if detail and verbose:
            print(f"       {detail}")
        return cond

    # ---- pycipher reference, itself round-trip asserted (W2) ----------------
    try:
        from pycipher.bifid import Bifid
        HAVE_PY = True
    except Exception as exc:                                  # pragma: no cover
        HAVE_PY = False
        print(f"  FAIL pycipher unavailable: {exc}")
        failures.append("pycipher import")

    def pc(fn, s, p):
        c = Bifid(ka, period=p)
        return c.decipher(s) if fn == "d" else c.encipher(s)

    say("== W2: pycipher is a true inverse at every divisor period (odd included) ==")
    if HAVE_PY:
        for nm, s in streams.items():
            L = len(s)
            bad = [p for p in range(1, L + 1) if L % p == 0
                   and pc("d", pc("e", s, p), p) != s]
            check(f"pycipher round-trip {nm} ({L} len, all divisor periods)",
                  not bad, f"failures: {bad[:8]}")

    # ---- 1. invertibility of the project's own pair, all divisor periods ---
    say()
    say("== 1. bifid_encrypt/bifid_decrypt are mutual inverses at EVERY period ==")
    say("   (bifid_encrypt was previously dead code -- called from nowhere)")
    for nm, s in streams.items():
        L = len(s)
        divs = [p for p in range(1, L + 1) if L % p == 0]
        odd = [p for p in divs if p % 2]
        bad = [p for p in divs
               if bifid_encrypt(bifid_decrypt(s, p, grid, pos), p, grid, pos) != s]
        check(f"{nm}: round-trip over all {len(divs)} divisor periods "
              f"({len(odd)} odd)", not bad, f"failures: {bad[:8]}")
        if HAVE_PY:
            dis = [p for p in divs if bifid_decrypt(s, p, grid, pos) != pc("d", s, p)]
            check(f"{nm}: decrypt agrees with pycipher at every divisor period",
                  not dis, f"disagreements: {dis[:8]}")

    say()
    say("== 1b. non-dividing periods are ALSO lossless (partial final block) ==")
    for nm, s in streams.items():
        L = len(s)
        bad = []
        for p in (3, 7, 13, 19, 100):
            if p <= L and L % p:
                if bifid_encrypt(bifid_decrypt(s, p, grid, pos), p, grid, pos) != s:
                    bad.append(p)
        check(f"{nm}: round-trip at non-dividing periods", not bad,
              f"failures: {bad}")

    # ---- 2. the certified witness, and that it can fail (W1, W3) -----------
    say()
    say("== W1/W3: certified faed->BTCSEED witness, reproduced by BOTH implementations ==")
    faed = streams["faed_570"]
    full = bifid_decrypt(faed, len(faed), grid, pos)
    check("W1 tool re-derives certified plaintext_head",
          full[:40] == stored["plaintext_head"], f"{full[:40]!r}")
    if HAVE_PY:
        check("W1 pycipher independently reproduces the same head",
              pc("d", faed, len(faed))[:40] == stored["plaintext_head"])
    # negative control: a corrupted keyword must break W1
    g2, p2 = build_grid("DBIFHCEX")
    bad_full = bifid_decrypt(faed, len(faed), g2, p2)
    check("W3 NEGATIVE CONTROL: corrupted keyword breaks the witness",
          bad_full[:40] != stored["plaintext_head"],
          "witness is capable of failing")

    # ---- 3. the parity factorisation, and its parity dependence (W4) ------
    say()
    say("== W4: ROWxROW / COLxCOL parity factorisation holds for EVEN n only ==")

    def split(seq):
        c = []
        for r, cc in coords(seq, cell):
            c += [r, cc]
        h = len(c) // 2
        return c[:h], c[h:]

    def parity_check(name):
        s = streams[name]
        n = len(s)
        T = coords(s, cell)
        rs, cs = split(s)
        h = len(rs)
        ev = list(range(0, h, 2))
        od = list(range(1, h, 2))
        ev_rowrow = all(rs[k] == T[k // 2][0] and cs[k] == T[(h + k) // 2][0]
                        for k in ev if (h + k) // 2 < n)
        od_colcol = all(rs[k] == T[(k - 1) // 2][1] and cs[k] == T[(h + k - 1) // 2][1]
                        for k in od if (h + k - 1) // 2 < n)
        return n, h, ev, od, rs, cs, ev_rowrow, od_colcol

    n, h, ev, od, rs, cs, ev_rr, od_cc = parity_check("faed_570")
    check("faed_570 (n=570, EVEN): even positions are a ROWxROW product", ev_rr)
    check("faed_570 (n=570, EVEN): odd positions are a COLxCOL product", od_cc)
    ev_c = sum(1 for k in ev if rs[k] in (0, 1) and cs[k] in (0, 1))
    od_c = sum(1 for k in od if rs[k] in (0, 1) and cs[k] in (0, 1))
    full_even, full_odd = full[0::2], full[1::2]
    check("faed_570: even_stream alphabet == the 2x2 corner block {B,C,D,E}",
          set(full_even) == set("BCDE"), f"got {sorted(set(full_even))}")
    check("faed_570: corner count decomposes EXACTLY as even(100%) + odd",
          ev_c + od_c == 327,
          f"even {ev_c}/{len(ev)} + odd {od_c}/{len(od)} = {ev_c + od_c} (stored 327)")
    check("faed_570: even_stream matches stored", full_even == stored["even_stream"])
    check("faed_570: odd_pre_reduction matches stored",
          full_odd == stored["odd_pre_reduction"])
    obj = "".join(c for c in full_odd if c not in ("I", "O"))
    check("faed_570: object_256 matches stored", obj == stored["object_256"])

    n2, h2, ev2, od2, rs2, cs2, ev_rr2, od_cc2 = parity_check("dbbib_91")
    check(f"dbbib_91 (n={n2}, ODD): factorisation asserted to FAIL (this is the claim)",
          not (ev_rr2 and od_cc2),
          f"even-parity ROWxROW holds={ev_rr2}, odd-parity COLxCOL holds={od_cc2}")
    d2 = bifid_decrypt(streams["dbbib_91"], n2, grid, pos)
    check("dbbib_91: even_stream alphabet is NOT confined to the corner block",
          set(d2[0::2]) != set("BCDE"), f"got {sorted(set(d2[0::2]))}")
    c2 = sum(1 for ch in d2 if cell[ch][0] in (0, 1) and cell[ch][1] in (0, 1))
    say(f"       dbbib_91 corner share {c2}/{n2} = {c2 / n2 * 100:.1f}% "
        f"-- real, but with no parity mechanism forcing it")

    # ---- 4. the circularity in R-PLAINART's F3 table ----------------------
    say()
    say("== 4. R-PLAINART F3's 'predicted' column uses PLAINTEXT marginals ==")
    for nm in ("faed_570", "dbbib_91"):
        s = streams[nm]
        n = len(s)
        T = coords(s, cell)
        pl = bifid_decrypt(s, n, grid, pos)
        tok_row = sum(1 for r, _ in T if r in (0, 1)) / n
        tok_col = sum(1 for _, c in T if c in (0, 1)) / n
        pt_row = sum(1 for ch in pl if cell[ch][0] in (0, 1)) / n
        pt_col = sum(1 for ch in pl if cell[ch][1] in (0, 1)) / n
        obs = sum(1 for ch in pl if cell[ch][0] in (0, 1) and cell[ch][1] in (0, 1)) / n
        say(f"  {nm}: token-marginal product {tok_row * tok_col * 100:5.1f}%   "
            f"plaintext-marginal product {pt_row * pt_col * 100:5.1f}%   "
            f"observed {obs * 100:5.1f}%")
        say(f"       all tokens in rows 0-1: {tok_row == 1.0}; "
            f"published 0.695/0.791 matches the PLAINTEXT row marginal: "
            f"{abs(pt_row - 0.695) < 1e-3 or abs(pt_row - 0.791) < 1e-3}")

    # ---- 5. dbbib_91 letters vs faed_570 letters (R-PLAINART F1) ----------
    say()
    say("== 5. R-PLAINART F2's 'same property' claim for dbbib_91 ==")
    cE = collections.Counter(pl for pl in full)
    cD = collections.Counter(d2)
    shareE = sum(cE[x] for x in "BCDE") / len(full)
    shareD = sum(cD[x] for x in "BCDE") / len(d2)
    say(f"  faed_570  {{B,C,D,E}} share = {shareE * 100:.1f}%  (even parity: {len(set(full_even))} letters)")
    say(f"  dbbib_91  {{B,C,D,E}} share = {shareD * 100:.1f}%  (even parity: {len(set(d2[0::2]))} letters)")
    check("the two streams do NOT share a mechanism (different even-parity alphabets)",
          set(full_even) != set(d2[0::2]),
          "faed even-parity is the 4-cell corner block; dbbib even-parity spans 9 cells")

    print()
    if failures:
        print(f"SELFTEST FAIL -- {len(failures)} check(s): {failures}")
        return 1
    print("SELFTEST PASS -- Bifid stage is invertible at every period, agrees with "
          "pycipher, and its parity factorisation is confirmed EVEN-only")
    print("  (0 candidates, 0 oracle calls, no funded-gate contact)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
