#!/usr/bin/env python3
"""Derived-stream family (Note 35 remainder): decoder over streams DERIVED
from raw dbbib_91/faed_570, then keyed28 checkerboard decode (certified board
expansion only reaches via keyword -> build_grid). The certified checkerboard
needs a 28-char alphabet; the canonical board B is FUBCDORA.LETHINGKYMVPS.JQZXW.

The unmatched Note-35 cell is: alphabet perm applied over a DERIVED stream
(position/diff/sum constructions), which rows 199/201/204/213 closed for raw
streams only. This sweep:
  (A) builds derived digit streams: forward/backward differences mod9,
      cumulative sum mod9, position-adjusted sums, first digit + i, mod9
      variants on both value maps (canon a=0..8, pos a=1..9);
  (B) decodes each via the CERTIFIED board under the two value maps and the
      certified checkerboard; emits plaintext/lower/reverse.
Barring a hit, the remaining genuinely-open derived layer is the 9! perms on
those derived streams = 91 or 570 digits x 362,880 perms -> reported as a
costed next step (N=~2 x 362,880, rate ~4.9k/s -> ~2 x 74s) rather than run
blind unenriched.
"""
import json, pathlib, itertools

BASE = pathlib.Path(__file__).resolve().parents[1]
d = json.loads((BASE / "data" / "finalpage-digit-streams.json").read_text())
DBBIB = d["dbbib_91"]
FAED = d["faed_570"].rstrip("z")

CANON = {"d": 0, "b": 1, "i": 2, "f": 3, "h": 4, "c": 5, "e": 6, "g": 7, "a": 8}
POS = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9}
BOARD = "FUBCDORA.LETHINGKYMVPS.JQZXW"

from certified_vic import build_grid, decode  # certified machinery (selfcert PASS)


def dig(s, mp):
    return "".join(str(mp[c]) for c in s)


def derived_streams(s, mp):
    """Position/sum/diff derived digit streams (mod 9), one per convention."""
    vals = [mp[c] for c in s]
    n = len(vals)
    def m9(x):
        return str(x % 9)
    out = {}
    out["raw"] = "".join(m9(v) for v in vals)
    # forward difference mod 9
    out["fwd_diff"] = "".join(m9(vals[i + 1] - vals[i]) for i in range(n - 1))
    # backward difference mod 9
    out["bak_diff"] = "".join(m9(vals[i] - vals[i - 1]) for i in range(1, n))
    # cumulative sum mod 9 (prefix)
    acc, cs = 0, []
    for v in vals:
        acc = (acc + v) % 9
        cs.append(str(acc))
    out["cumsum"] = "".join(cs)
    # val + 0-based position mod 9
    out["pos_add"] = "".join(m9(vals[i] + i) for i in range(n))
    # val - 0-based position mod 9
    out["pos_sub"] = "".join(m9(vals[i] - i) for i in range(n))
    # val + 1-based position mod 9
    out["pos_add1"] = "".join(m9(vals[i] + (i + 1)) for i in range(n))
    # val - 1-based position mod 9
    out["pos_sub1"] = "".join(m9(vals[i] - (i + 1)) for i in range(n))
    # alternating + / -	spiral walk
    out["alt"] = "".join(m9(-vals[i]) if i % 2 else m9(vals[i]) for i in range(n))
    # reversed raw
    out["rev"] = "".join(m9(v) for v in reversed(vals))
    # pair-first-half vs pair-second-half mod 9
    half = len(vals) // 2
    out["pairx"] = "".join(m9(vals[i] + vals[n - 1 - i]) for i in range(n // 2))
    return out


def main():
    cands = {}
    for stream_name, stream in (("dbbib_91", DBBIB), ("faed_570", FAED)):
        for mpn, mp in (("canon", CANON), ("pos", POS)):
            for dname, ds in derived_streams(stream, mp).items():
                # only digit strings == the alphabet built by keying the board
                for kw, alpha in (("BOARD", BOARD),):
                    ctol = build_grid(alpha, 1, 4)  # certified board escapes
                    dec = decode(ds, ctol, 1, 4)
                    for form in {dec, dec.lower(), dec[::-1]}:
                        if form:
                            cands.setdefault(form, ("derived", stream_name, mpn, dname))
    uniq = [(k, v) for k, v in cands.items()]
    with open("/data/data/com.termux/files/usr/tmp/opencode/derived_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/derived_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    # report fraction of decodes that are all-printable-useful
    tally = {}
    for k, v in uniq:
        tally.setdefault(v[2], []).append(k)
    summary = {dn: len(v) for dn, v in tally.items()}
    print("candidates:", len(uniq))
    print("per-derived:", summary)


if __name__ == "__main__":
    main()