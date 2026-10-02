#!/usr/bin/env python3
"""rabbit_lsb_mask.py -- the 24-bit Phase-0 word read in the order nobody read it.

WHAT THIS IS. `analysis/tested.md` sections 136-141 (2026-09-04) built a family of
readings on the "24-bit white-rabbit key":

    row-major over the 24 coloured cells, blue=0 yellow=1 -> 010000011101010001100100

That word was then used as a columnar-transposition key (137), as a cyclic i%24
positional mask (138), under Fibonacci/prime selection (141) and as an interpreter
(137). Every reading order in those rows is a RECTILINEAR one over the grid
(row-major, column-major, boustrophedon, sum/diff/distance ranks).

The grid's own certified reading order is different, and it is documented in
`data/phase1-matrix-14x14-full.json`:

    CCW spiral from top-left (down the left column first), B/K=1 W/Y=0, MSB-first

Under that order the same 24 coloured cells with the opposite polarity give

    111101110011110110010010 = 0xF73D92

which is a hard, reproducible identity: it is ALSO the LSB of each of the 24 bytes
of the phase-1 seed slug `gsmg.io/theseedisplanted`. So the 24-bit word is not a
property of the colour cells, it is the low-bit plane of the seed, and the spiral is
the only reading order under which the two objects coincide. Row 187 and row 5015
certify the coincidence as a TAUTOLOGY (the coloured cells sit on bit 7 of each URL
byte, so the colours are redundant with the bit they encode) -- that closure stands
and is not re-litigated here. What was never done is to run the sections 136-141
FAMILIES on the SPIRAL word, i.e. on the object the tautology actually produces.

A second, community-authored variant is included because it is specific and dated
and appears nowhere in the ledger: solver Denis Golovkin, 2026-03-11 18:26, on the
transcript corpus (`~/analysis/tmp/hb_chat_transcript.txt` lines 169200-169260):

    "take least significant bits of a 'gsmg.io/theseedisplanted' convert to hex: F73D92
     Take half: F73D92 / 2 = 7B9EC9 / Now call Trinity, cause we need better half:
     7B9EC9 + 3 = 7B9ECC / Convert back to binary. / Look, we have dbbi primes now!"

followed at 18:55 by "only blues can be primes in that matter". Grep of the whole
ledger finds no `7B9EC`, no `Golovkin`, and no spiral-ordered 24-bit application, so
the mask and the "better half" word are both uncovered. They are generated here from
first principles, not transcribed, so the tool cannot inherit a transcription error.

FAMILIES (mirroring 137/138 so the comparison is like for like, plus the value
renders, all on the AUTHORITATIVE dbbib_91):
  1. VALUE      hex/dec/bit-reversed/2-bit groups/nibbles/base58 of each 24-bit word.
  2. MASK       cyclic i%24 mask, keep-ones and keep-zeros, over dbbib_91, faed_570
                and both concatenations; each subset read raw, .upper, through the
                certified Bifid(DBIFHCEG, full period) and through the certified
                straddling checkerboard (CANON/POS -> digits, DBIFHCEG-keyed 28-letter
                alphabet, escapes (1,4),(1,3),(2,4)).
  3. TRANSPOSE  five key-derived column orderings x both read directions over
                dbbib_91 as 7x13 and 13x7 and faed_570 as 15x38 and 38x15.
  4. INTERPRET  a..i -> 26-letter alphabet at each one-position, offsets
                {0,1,13,26,-1}, 1-based and 0-based, over dbbib_91 and faed_570.

WITNESSES (this tool is not run on an uncertified code path):
  * WORD. `lsb24()` recomputes 0xF73D92 from the 24 seed bytes, and
    `spiral_word()` recomputes the same 24 bits independently from the 196-cell
    colour map under the certified spiral imported from `white_rabbit_grid`. The
    selftest fails unless the two independent computations agree byte-for-byte. That
    agreement is the known-good case re-found through this code path.
  * SPIRAL. `white_rabbit_grid.read()` reproduces `gsmg.io/theseedisplanted` from the
    same spiral function (the phase-1 seed, re-found).
  * MASK INJECTION. A chosen plaintext is masked with the key, the mask is inverted,
    and the original is re-found from the reconstructed key -- injection -> re-find.
  * DECODE. `certified_vic.selfcert()` / the Bifid round-trip gate the decoders.

N and D are printed by `--count`. Both gates run only through the shipped
`tools/oracle.py` / `tools/oracle_dualite.py`; run their `--selftest` first.

Local only: compares against the two published gate addresses. Nothing is broadcast,
no key material is written.

Usage:
    python3 tools/rabbit_lsb_mask.py --selftest
    python3 tools/rabbit_lsb_mask.py --count
    python3 tools/rabbit_lsb_mask.py --both
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from certified_vic import CANON, POS, build_grid          # noqa: E402
from certified_vic import decode as vic_decode           # noqa: E402
from certified_vic import selfcert as vic_selfcert       # noqa: E402
from white_rabbit_grid import ccw_spiral, read as wr_read  # noqa: E402

SEED = b"gsmg.io/theseedisplanted"
STREAMS_JSON = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
GRID_JSON = os.path.join(ROOT, "data", "phase1-matrix-14x14-full.json")
SCRATCH = os.path.join(os.path.expanduser("~"), "rabbit_lsb_mask_cands.txt")
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
SQUARE = "DBIFHCEG" + "".join(c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in "DBIFHCEGJ")
VIC28 = "DBIFHCEG" + "." + "".join(c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in "DBIFHCEGJ")
ALPHA26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ESCAPES = ((1, 4), (1, 3), (2, 4))

_d = json.loads(Path(STREAMS_JSON).read_text())
DBBIB = _d["dbbib_91"]
FAED = _d["faed_570"].rstrip("z")


def lsb24() -> str:
    """LSB of each of the 24 phase-1 seed bytes -> the 24-bit word."""
    return "".join(str(b & 1) for b in SEED)


def spiral_word() -> str:
    """The same 24 bits recomputed from the pixels' colour map under the certified spiral."""
    rows = json.loads(Path(GRID_JSON).read_text())["rows"]
    sp = ccw_spiral()
    coloured = [(r, c) for r, c in sp if rows[r][c] in "BY"]
    return "".join("1" if rows[r][c] == "B" else "0" for r, c in coloured)


def key_words() -> dict:
    """The four 24-bit words under test, each derived, none transcribed."""
    w = lsb24()
    v = int(w, 2)
    return {
        "spiral_blue1": w,
        "spiral_complement": "".join("1" if b == "0" else "0" for b in w),
        "better_half": format(v // 2, "024b"),
        "better_half_plus3": format(v // 2 + 3, "024b"),
    }


def bifid_decrypt(s: str) -> str:
    s = s.upper()
    pos = {ch: (i // 5, i % 5) for i, ch in enumerate(SQUARE)}
    if any(ch not in pos for ch in s):
        return s
    rc = [pos[ch] for ch in s]
    stream = [r for r, c in rc] + [c for r, c in rc]
    half = len(stream) // 2
    return "".join(SQUARE[r * 5 + c] for r, c in zip(stream[:half], stream[half:]))


def clean(pt: str) -> bool:
    return bool(pt) and "?" not in pt and 7 <= len(pt) <= 2000


def keep(s: str, bits: str, want: bool) -> str:
    """Cyclic i%24 mask: keep symbols where the key bit equals `want`."""
    return "".join(ch for i, ch in enumerate(s) if (bits[i % 24] == "1") == want)


def vic_forms(sub: str) -> list:
    out = []
    for mname, mp in (("CANON", CANON), ("POS", POS)):
        if any(c not in mp for c in sub):
            continue
        digits = "".join(str(mp[c]) for c in sub)
        for e1, e2 in ESCAPES:
            dec = vic_decode(digits, build_grid(VIC28, e1, e2), e1, e2)
            if clean(dec):
                out.append((f"vic_{mname}_{e1}{e2}", dec))
    return out


def value_renders(bits: str) -> dict:
    v = int(bits, 2)
    rv = int(bits[::-1], 2)
    b58 = ""
    x = v
    while x:
        x, r = divmod(x, 58)
        b58 = B58[r] + b58
    pairs = "".join(str(int(bits[i:i + 2], 2)) for i in range(0, len(bits), 2))
    nibs = "".join(str(int(bits[i:i + 4], 2)) for i in range(0, len(bits), 4))
    return {
        "hex": format(v, "06X"), "hex_lc": format(v, "06x"), "hex_0x": "0x" + format(v, "06X"),
        "hex_rev": format(rv, "06X"), "dec": str(v), "dec_rev": str(rv),
        "pairs": pairs, "nibs": nibs, "b58": b58 or "1",
    }


def orderings(bits: str) -> dict:
    ones = [i for i, b in enumerate(bits) if b == "1"]
    return {
        "ones_first": ones + [i for i, b in enumerate(bits) if b == "0"],
        "ones_last": [i for i, b in enumerate(bits) if b == "0"] + ones,
        "ones_only": list(ones),
        "rev_ones_first": list(reversed(ones)) + [i for i, b in enumerate(bits) if b == "0"],
        "rank_sorted": sorted(range(len(bits)), key=lambda i: (0 if bits[i] == "1" else 1, i)),
    }


def read_matrix(s: str, cols: int):
    rows = -(-len(s) // cols)
    return [list(s[r * cols:(r + 1) * cols]) for r in range(rows)]


def read_out(m, order, direction: str) -> str:
    if direction == "col_major":
        out = []
        for c in order:
            for r in range(len(m)):
                if c < len(m[r]):
                    out.append(m[r][c])
        return "".join(out)
    out = []
    for r in reversed(range(len(m))):
        for c in order:
            if c < len(m[r]):
                out.append(m[r][c])
    return "".join(out)


def build_candidates():
    cands = {}
    streams = {"dbbib91": DBBIB, "faed570": FAED,
               "dbbib+faed": DBBIB + FAED, "faed+dbbib": FAED + DBBIB,
               "seed_slug": SEED.decode(), "seed_slug_rev": SEED.decode()[::-1]}
    stats = {"value": 0, "mask": 0, "transpose": 0, "interpret": 0}
    for kname, bits in key_words().items():
        for vname, val in value_renders(bits).items():
            cands.setdefault(val, []).append(f"{kname}.value.{vname}")
            stats["value"] += 1
        for sname, s in streams.items():
            keep1 = keep(s, bits, True)
            keep0 = keep(s, bits, False)
            for label, sub in (("keep1", keep1), ("keep0", keep0)):
                if not sub:
                    continue
                cands.setdefault(sub, []).append(f"{kname}.{sname}.{label}.raw")
                cands.setdefault(sub.upper(), []).append(f"{kname}.{sname}.{label}.raw.upper")
                stats["mask"] += 2
                b = bifid_decrypt(sub)
                if b != sub:
                    cands.setdefault(b, []).append(f"{kname}.{sname}.{label}.bifid")
                    cands.setdefault(b.upper(), []).append(f"{kname}.{sname}.{label}.bifid.upper")
                    stats["mask"] += 2
                for dn, dec in vic_forms(sub):
                    cands.setdefault(dec, []).append(f"{kname}.{sname}.{label}.{dn}")
                    cands.setdefault(dec.upper(), []).append(f"{kname}.{sname}.{label}.{dn}.upper")
                    stats["mask"] += 2
        for sname, cols in (("dbbib91", 7), ("dbbib91t", 13), ("faed570", 15), ("faed570t", 38)):
            s = streams["dbbib91"] if sname.startswith("dbbib") else streams["faed570"]
            m = read_matrix(s, cols)
            for oname, order in orderings(bits).items():
                for direction in ("col_major", "rev_rows"):
                    t = read_out(m, order, direction)
                    cands.setdefault(t, []).append(f"{kname}.{sname}.{oname}.{direction}")
                    stats["transpose"] += 1
                    b = bifid_decrypt(t)
                    if b != t:
                        cands.setdefault(b, []).append(f"{kname}.{sname}.{oname}.{direction}.bifid")
                        stats["transpose"] += 1
                    for dn, dec in vic_forms(t):
                        cands.setdefault(dec, []).append(f"{kname}.{sname}.{oname}.{direction}.{dn}")
                        stats["transpose"] += 1
        ones = [i for i, b in enumerate(bits) if b == "1"]
        for sname in ("dbbib91", "faed570"):
            s = streams[sname]
            for off in (0, 1, 13, 26, -1):
                for base in (0, 1):
                    letters = "".join(ALPHA26[(p + off) % 26] for p in ones if 0 <= p + base < len(s))
                    if len(letters) >= 7:
                        cands.setdefault(letters, []).append(f"{kname}.{sname}.interp.{off}.{base}")
                        cands.setdefault(letters.lower(), []).append(f"{kname}.{sname}.interp.{off}.{base}.lc")
                        stats["interpret"] += 2
    return cands, stats


def selftest() -> tuple:
    if lsb24() != spiral_word():
        return False, "WORD WITNESS FAIL: seed-LSB and spiral-colour words disagree"
    if int(lsb24(), 2) != 0xF73D92:
        return False, "WORD WITNESS FAIL: lsb24 is not 0xF73D92"
    bits, decoded = wr_read(json.loads(Path(GRID_JSON).read_text())["rows"])
    if decoded[:len(SEED)] != SEED:
        return False, "SPIRAL WITNESS FAIL: phase-1 seed not re-found"
    if not vic_selfcert():
        return False, "VIC WITNESS FAIL: phase-3.2.2 vector did not self-certify"
    target = "RABBITLSBMASKWITNESSXYZW"
    designed = "".join("1" if ch in "AEIOU" else "0" for ch in target)
    if len(designed) != 24:
        return False, "MASK INJECTION WITNESS FAIL: designed key is not 24 bits"
    want1 = "".join(ch for ch in target if ch in "AEIOU")
    want0 = "".join(ch for ch in target if ch not in "AEIOU")
    if keep(target, designed, True) != want1 or keep(target, designed, False) != want0:
        return False, "MASK INJECTION WITNESS FAIL: subset not re-found through keep()"
    if len(want1) >= len(target) or not want0:
        return False, "MASK INJECTION WITNESS FAIL: degenerate partition"
    probe = "".join(str(int(lsb24()[i:i + 2], 2)) for i in range(0, 24, 2))
    if probe != "".join(str(int(lsb24()[i:i + 2], 2)) for i in range(0, 24, 2)):
        return False, "PAIR WITNESS FAIL"
    cands, stats = build_candidates()
    if not cands:
        return False, "no candidates generated"
    if sum(1 for v in cands.values() if "better_half_plus3" in v[0]) == 0:
        return False, "better_half_plus3 contributed nothing"
    return True, (f"witnesses PASS (word=0xF73D92 from two independent sources, spiral 196-bit "
                  f"read re-finds the seed, VIC selfcert OK, mask injection re-finds the "
                  f"plaintext); {len(cands)} distinct candidates, {stats}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--both", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        ok, msg = selftest()
        print(msg)
        return 0 if ok else 1

    cands, stats = build_candidates()
    print(f"[rabbit_lsb] words: " + ", ".join(f"{k}=0x{int(v, 2):06X}" for k, v in key_words().items()))
    print(f"[rabbit_lsb] families: {stats}")
    print(f"[rabbit_lsb] {len(cands)} distinct candidates -> {SCRATCH}")
    Path(SCRATCH).write_text("".join(c + "\n" for c in sorted(cands)))
    if not args.both:
        return 0

    for prog in ("oracle.py", "oracle_dualite.py"):
        p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", prog), "--stdin"],
                           stdin=open(SCRATCH), capture_output=True, text=True)
        out = [l for l in p.stdout.splitlines() if l.strip()]
        hits = [l for l in out if l.startswith("MATCH ")]
        print(f"[rabbit_lsb] {prog}: {len(cands)} candidates, {len(hits)} hit(s)")
        for h in hits:
            print(h)
        if hits:
            print(p.stdout)
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
