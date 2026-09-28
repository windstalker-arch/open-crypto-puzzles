#!/usr/bin/env python3
"""cipher_battery.py -- late-273. Generic cipher battery harness.

One surface (a ciphertext stream, or the puzzle's built-in named streams) can
be pumped through EVERY registered cipher cell at once, deduped, and verified
against both funded gates. Each cell is a small function:

    cell(surface: str, params: dict) -> iterable[str]

over clean decoded candidate plaintexts. A battery run = {surface set} x
{cell set} x {param variants the cell declares}. Every run is certified:
  * --selftest injects, for EVERY cell, a synthetic plaintext P encoded under
    that cell's own convention; the harness must re-find P among the emitted
    forms through the exact same pipeline (no special-casing).
  * --both then feeds every unique candidate to oracle.py (small 1.25 BTC) and
    oracle_dualite.py (Dualite 3.75 BTC).

Surfaces offered: dbbib(69)/dbbib_91/faed(570)/z_segment_1/z_segment_2 from
data/finalpage-digit-streams.json, plus --string for any raw literal, and any
digit stream produced by the white-rabbit grid traversals (--grid).

Example:
    python3 tools/cipher_battery.py --selftest
    python3 tools/cipher_battery.py --both
    python3 tools/cipher_battery.py --string "dbbibfbhccbeg..." --only vic,interp10
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import build_grid, decode  # noqa: E402
from leap_alphabet_sweep import ALPHAS  # noqa: E402

DATA = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())
GRID = json.loads(Path(os.path.join(ROOT, "data", "follow-white-rabbit-grid.json")).read_text())
BLUE = [tuple(c) for c in GRID["blue"]]
YELLOW = [tuple(c) for c in GRID["yellow"]]
CELLS_SRC = list(BLUE) + list(YELLOW)
SB = set(BLUE)
SCRATCH = os.path.join(os.path.expanduser("~"), "cipher_battery_cands.txt")

BUILTIN_SURFACES = {
    "dbbib69": DATA["dbbib"],
    "dbbib91": DATA["dbbib_91"],
    "faed570": DATA["faed_570"][:570],
    "zseg1": DATA["z_segment_1"],
    "zseg2": DATA["z_segment_2"],
    # late-297: DCL puzzlepiece audio number-stream (user steer), hex-ascii
    # byte pairs. dcl_audio48 = "4841534854484554455854" decodes to HASHTHETEXT;
    # the 18-leading reading as-given by the audio ("18 41 53 48 54 48 45 54
    # 45 58 54") carries a leading 0x18 control byte (transcription of 48) and
    # decodes to ASHTHETEXT after stripping non-printables -- both retained.
    "dcl_audio48": "4841534854484554455854",
    "dcl_audio18": "1841534854484554455854",
    "dcl_hashthetext": "HASHTHETEXT",
}
CANON = {c: str(i + 1) for i, c in enumerate("abcdefghi")}
FREQ = "bag e i h f c d".replace(" ", "")


def grid_surfaces():
    from grid_route_battery import orderings, reductions
    out = {}
    for oname, order in orderings(CELLS_SRC, SB).items():
        for rname, fs in reductions(order).items():
            out[f"grid.{oname}.{rname}"] = fs
    return out


def sticker_surfaces():
    """Tile surfaces from the 8 theseedisplanted sticker strips (color classes as
    letter/digit streams). Certified pixel read, no OCR (late-83/84 artifacts):
      - bottom band: 46 tile classes L2R (bottom_band_l2r.txt)
      - BOT/SECOND rows: 13 + 8 tile class runs (sticker_bands_color.txt)
    Each tile's class token (R,O,Y,C,b,B,G,...) becomes one surface symbol; the
    code-order position of first appearance is the digit map for interp cells."""
    import re
    out = {}
    rows = []
    band46 = ""
    p46 = Path(os.path.join(ROOT, "analysis", "sticker_color_order", "bottom_band_l2r.txt"))
    if p46.exists():
        for l in p46.read_text().splitlines():
            l = l.strip()
            if not l or l.startswith("#"):
                continue
            m = re.match(r"^([A-Z]+):\s*(\d+)\s*tiles.*?:\s*(\S+)\s*$", l)
            if m:
                rows.append((m.group(1), re.split(r"[- ]", m.group(3))))
            elif len(l) > 20 and not l.startswith(("(", "BOT", "SECOND")):
                band46 = re.split(r"-", l)
        if band46:
            out["st.band46"] = "".join(band46)
    pbands = Path(os.path.join(ROOT, "analysis", "sticker_bands_color.txt"))
    if pbands.exists():
        for l in pbands.read_text().splitlines():
            m = re.match(r"^([A-Z-]+):\s*\d+\s*tiles.*?:\s*(\S+)\s*$", l.strip())
            if m:
                rows.append((m.group(1), list(m.group(2))))
    tokens = band46 + [t for _, r in rows for t in r]
    if not tokens:
        return out
    code = {}
    for t in tokens:
        if t and t not in code:
            code[t] = str(len(code) + 1)
    code = {k: str((int(v) - 1) % 9) for k, v in code.items()}  # 0..8 conv
    for rname, r in rows:
        key = "st." + rname.lower()
        out[key] = "".join(r)
        out[key + ".cd9"] = "".join(code.get(t, "0") for t in r)
    if band46:
        out["st.band46.cd9"] = "".join(code.get(t, "0") for t in band46)
    n = len(code)
    out["st.classorder1"] = "".join(code[k] for k in code)
    out["st.classcount"] = str(n)
    return out


# ---------------------------------------------------------------- cipher cells
def cell_vic(surface, params):
    """VIC straddling-checkerboard decode under {alphas} x escapes."""
    for aname, alpha in ALPHAS.items():
        for e1, e2 in params.get("escapes", ((1, 4), (4, 1))):
            g = build_grid(alpha, e1, e2)
            num = [next((d for d, v in g.items() if v == ch), "?") for ch in surface]
            ds = "".join(num).replace("?", "")
            if not ds:
                continue
            pt = decode(ds, g, e1, e2)
            if "?" not in pt and 8 <= len(pt) <= 2000:
                yield pt


INTERP_ALPHAS = {"canon": {c: str(i + 1) for i, c in enumerate("abcdefghi")},
                 "pos": {c: str(i) for i, c in enumerate("abcdefghi")},
                 "freq": {c: str(i + 1) for i, c in enumerate(FREQ)}}


def _hex_ascii(n: int) -> str:
    h = format(n, "x")
    if len(h) % 2:
        h = "0" + h
    try:
        return bytes.fromhex(h).decode("ascii", "replace")
    except ValueError:
        return None


def cell_interp(surface, params):
    """Certified z-segment interpreter: letters -> digits, base-10 -> hex -> ASCII."""
    for aname, mp in (INTERP_ALPHAS.items() if not params.get("one") else [("one", INTERP_ALPHAS[params["one"]])]):
        digits = "".join(mp.get(c, c) for c in surface)
        if digits and digits.isdigit() and int(digits, 10) > 0:
            out = _hex_ascii(int(digits, 10))
            if out and 8 <= len(out) <= 2000:
                yield out


def cell_interp9(surface, params):
    """base-9 big-int -> hex -> ASCII (Wi77erd pre-z block reading)."""
    mp = INTERP_ALPHAS.get(params.get("one", "pos"), INTERP_ALPHAS["pos"])
    digits = "".join(mp.get(c, c) for c in surface)
    digits = "".join(c for c in digits if "0" <= c <= "8")
    if not digits:
        return
    try:
        n = int(digits, 9)
    except ValueError:
        return
    out = _hex_ascii(n)
    if out and 8 <= len(out) <= 2000:
        yield out


def cell_xor(surface, params):
    """Cycling byte-XOR (KyleBanks/HKTITAN family, late-270/272) hex renders."""
    for key in params.get("keys", ["KCQ", "matrixsumlist", "enter", "shabef", "salphasion"]):
        kb = key.encode()
        out = bytes(ord(c) ^ kb[i % len(kb)] for i, c in enumerate(surface))
        p = "" if not (out and all(32 <= x <= 126 for x in out)) else out.decode("ascii")
        if params.get("hex", True):
            yield out.hex()
        if p:
            yield p


def cell_hexpairs(surface, params):
    """late-298. Hex-ascii byte-pair decoder for the DCL audio number-stream.

    The digit surface is a run of 2-hex-digit ASCII byte values
    (e.g. dcl_audio48 = "484153485448455854" -> HASHTHETEXT). Bootstrap the
    audio steer (18 41 53 48 54 48 45 54 45 58 54) where the leading 18 is a
    transcription of 48: decode byte-pairs, drop any unprintable control from
    the head (the 18 variant -> ASHTHETEXT), and emit the plaintext plus its
    spacing/case/epistle variants."""
    h = "".join(c for c in surface if c in "0123456789abcdefABCDEF")
    if len(h) % 2:
        return
    try:
        b = bytes.fromhex(h)
    except ValueError:
        return
    txt = b.decode("ascii", "replace")
    if not txt or not any(ch.isalpha() for ch in txt):
        return
    variants = {txt}
    clean = "".join(ch for ch in txt if ch.isalpha())
    for v in (clean.upper(), clean, clean.title(), " ".join(clean)):
        variants.add(v)
        variants.add(v.replace(" ", ""))
        variants.add(v.replace(" ", "-"))
    for v in variants:
        if 4 <= len(v) <= 64:
            yield v


# ------------------------------------------------- classical ciphers (late-279):
# steer: user pointed at SecretPy (classical cipher library) + ciphermuseum.com
# timeline. Interp the certified a-i stream to text first (canon interp10), then
# run the classical decipher under every usable key from the puzzle + cipher names.
from secretpy import (ADFGX, ADFGVX, Affine, Atbash, Autokey, Beaufort,  # noqa: E402
                      Bifid, Caesar, ColumnarTransposition, FourSquare, Gronsfeld,
                      Keyword, MyszkowskiTransposition, Playfair, Porta, Rot13,
                      Rot47, Scytale, Trifid, TwoSquare, Vigenere, Zigzag)
import secretpy.alphabets as SPA            # noqa: E402

CANON_ALPHABET = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'ij', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')

CLASSIC_KEYWORDS = [
    "adfgx", "adfgvx", "affine", "atbash", "autokey", "beaufort", "bifid",
    "caesar", "columnar", "foursquare", "gronsfeld", "keyword", "myszkowski",
    "playfair", "porta", "rot13", "rot47", "scytale", "trifid", "twosquare",
    "vigenere", "zigzag", "polybius", "straddlingcheckerboard", "railfence",
    "nihilist", "salphaseion", "salphaseion", "salphaseionworld",
    "matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
    "shabef", "ourfirsthintisyourlastcommand", "anstoo", "gsmg",
    "white", "rabbit", "alice", "bankingwar", "cryptogic", "digitallogic",
    "cryptocraft", "astralbutton", "mempool", "escrow", "bitcoin",
    "thearchitectchoice", "followthewhiterabbit", "theseedisplanted",
]


class _Classic():
    """Thin dispatch so one cell loop covers every SecretPy cipher signature."""
    def __init__(self, ctor, needs_key, shifts=False, affine=False, numeric=False):
        self.ctor = ctor
        self.needs_key = needs_key
        self.shifts = shifts
        self.affine = affine
        self.numeric = numeric

    def decrypt(self, text, key, alphabet):
        try:
            return self.ctor().decrypt(text, key, alphabet)
        except Exception:
            return None


def _classic_ciphers():
    yield "atbash", _Classic(Atbash, False)
    yield "rot13", _Classic(Rot13, False)
    yield "rot47", _Classic(Rot47, False)
    for name, c in (("vigenere", Vigenere), ("autokey", Autokey),
                    ("beaufort", Beaufort), ("porta", Porta),
                    ("keyword", Keyword), ("adsfk", Keyword)):
        # 'keyword' rarely accepts braces; keep the sane family
        if name == "adsfk":
            continue
        yield name, _Classic(c, True)
    yield "bifid", _Classic(Bifid, True)
    yield "trifid", _Classic(Trifid, True)
    yield "twosquare", _Classic(TwoSquare, True)
    yield "foursquare", _Classic(FourSquare, True)
    yield "playfair", _Classic(Playfair, True)
    yield "adfgx", _Classic(ADFGX, True)
    yield "adfgvx", _Classic(ADFGVX, True)
    yield "columnar", _Classic(ColumnarTransposition, True)
    yield "myszkowski", _Classic(MyszkowskiTransposition, True)
    yield "zigzag", _Classic(Zigzag, True)
    yield "scytale", _Classic(Scytale, True)
    yield "gronsfeld", _Classic(Gronsfeld, True, numeric=True)
    yield "caesar", _Classic(Caesar, False, shifts=True)
    for a, b in ((7, 8), (5, 8), (3, 10), (7, 11)):
        yield "affine-%d-%d" % (a, b), _Classic(Affine, False, affine=(a, b))
    yield "polybius", _Classic(None, False)  # placeholder filtered below


def cell_classical(surface, params):
    """Two passes:
      1) interp10(canon) -> ASCII, then the classical decipher (needs a readable
         span); 2) optionally the classical decipher applied DIRECTLY to the
         surface's letters (params['direct'] - the 'cipher the digit stream'
         reading of the steer)."""
    def _run(ct_text, tag):
        if params.get("direct_only") and tag == "interp":
            return
        for name, c in _classic_ciphers():
            if name == "polybius":
                continue
            if c.shifts:
                keys = list(range(1, 26))
            elif c.affine:
                keys = [c.affine]
            elif c.numeric:
                keys = [str(n) for n in range(1, 10)]
            else:
                keys = CLASSIC_KEYWORDS
            for key in keys:
                pt = c.decrypt(ct_text, key,
                               CANON_ALPHABET if name in ("adfgx", "adfgvx") else SPA.ENGLISH)
                if pt is None:
                    continue
                if pt and pt.isascii():
                    yield pt
                    ptu = pt.upper()
                    if ptu != pt:
                        yield ptu

    mp = INTERP_ALPHAS["canon"]
    digits = "".join(mp.get(c, c) for c in surface)
    interp_txt = None
    if digits and digits.isdigit() and int(digits, 10) > 0:
        mid = _hex_ascii(int(digits, 10))
        if mid and mid.isascii():
            interp_txt = "".join(ch for ch in mid.lower() if ch.isalpha())
    if interp_txt and len(interp_txt) >= 8:
        yield from _run(interp_txt, "interp")
    clean = "".join(ch for ch in surface.lower() if ch.isalpha())
    if params.get("direct") and len(clean) >= 8:
        yield from _run(clean, "direct")


def cell_keyed(surface, params):
    """late-283. Keyword-keyed mixed-alphabet interpreter (lead-0 reading).

    Bridges the 62-column keyword-matrix steer (jyotiska222) and the jpillora
    cipher-disk (custom alphabet on a ring) into the interpreter crux: build a
    KEYED alphabet over the digit domain from a keyword (keyword symbols first,
    then the remaining symbols in natural order -- the same construction the two
    steers use), substitute the certified digit stream through it (both keying
    directions), then read the result as a big integer in that base -> hex ->
    ASCII. Domains: the 1..9 canon ring and the 1..9 plus o=0 -> 0..9 ring."""
    canon10 = {c: str(i + 1) for i, c in enumerate("abcdefghi")}
    canon10["o"] = "0"
    digits = "".join(canon10.get(c, c) for c in surface.lower() if canon10.get(c) is not None or c.isdigit())
    digits = "".join(ch for ch in digits if ch.isdigit())
    if not digits:
        return
    for domain in ("123456789", "0123456789"):
        base = len(domain)
        for key in CLASSIC_KEYWORDS:
            for krev in (False, True):
                k = key[::-1] if krev else key
                seen, A = set(), ""
                for ch in k:
                    if ch in domain and ch not in seen:
                        A += ch
                        seen.add(ch)
                for ch in domain:
                    if ch not in seen:
                        A += ch
                        seen.add(ch)
                fwd = {domain[i]: A[i] for i in range(base)}
                bwd = {A[i]: domain[i] for i in range(base)}
                for mp in (fwd, bwd):
                    out = "".join(mp.get(c, c) for c in digits)
                    if not out or not all(c in domain for c in out):
                        continue
                    try:
                        n = int(out, base)
                    except ValueError:
                        continue
                    txt = _hex_ascii(n)
                    if txt and 8 <= len(txt) <= 2000:
                        yield txt


def _stream_first9(surface):
    """First 9 distinct a..i symbols of a surface, in order of appearance ->
    9-char keyed ring candidate over the stream's own alphabet (community #93:
    'dbbib' is the key side of the pair)."""
    out, seen = [], set()
    for c in surface.lower():
        if "a" <= c <= "i" and c not in seen:
            out.append(c)
            seen.add(c)
        if len(out) == 9:
            break
    return "".join(out) if len(out) == 9 else None


ALBERTI_FIXED_RINGS = [
    "abcdefghi",                     # canonical plaintext ring
    "dbifhcega",                     # Bifid-keyed-square row (D B I F H C E G A)
    "abcdefghi"[::-1],               # reversed canonical
    "dbifhcega"[::-1],               # reversed Bifid row
]
ALBERTI_MOVABLE_RINGS = ["abcdefghi", "dbifhcega"] + [
    r for r in (  # stream-derived keyed rings (the 'key' side, community #93)
        _stream_first9(s) for s in
        (DATA["dbbib_91"], DATA["faed_570"],
         DATA["z_segment_1"], DATA["z_segment_2"],
         DATA["dbbib_91"][::-1], DATA["faed_570"][::-1])
    ) if r and r not in ("abcdefghi", "dbifhcega")
]


def cell_alberti(surface, params):
    """Alberti-cipher-disk interpreter: TWO rings over the 9-symbol alphabet.
    The puzzle's streams are read as a cipher disk  --  a FIXED ring (plaintext
    side, canon/Bifid-row orders) against a MOVABLE ring (a *keyed/mixed*
    alphabet: stream-derived first-9 rings, i.e. the 'dbbib' key side, or the
    fixed orders themselves) --  with the movable ring rotated:

      fixed   k in 0..8            = disk pre-set to sector k
      rotor                        = advance +1 per symbol (variable period)
      marker                      = advance +1 whenever the symbol equals an
                                    index letter m in a..i (Alberti's own
                                    index-letter rotation; variable period)

    For each (fixed ring, movable ring, rotation mode) the ciphertext symbol c
    is matched on the movable ring and read off the fixed ring at the aligned,
    rotated position (both directions); the resulting plaintext over {a..i} is
    then mapped to digits (pos: a=0..i=8; canon: a=1..i=9) and read as a big
    int (base-9 / base-10) -> hex -> ASCII, like the other interp cells."""
    syms = [c for c in surface.lower() if "a" <= c <= "i"]
    if len(syms) < 8:
        return
    rings = {"abcdefghi": "abcdefghi", "dbifhcega": "dbifhcega"}
    for i, r in enumerate(ALBERTI_MOVABLE_RINGS):
        if r not in rings.values():
            rings[f"ring{i}"] = r
    maps = {"pos": {c: str(i) for i, c in enumerate("abcdefghi")},
            "canon": {c: str(i + 1) for i, c in enumerate("abcdefghi")}}
    seen = set()
    for fname, fixed in [("abc", "abcdefghi"), ("bifid", "dbifhcega")]:
        for mname, movable in rings.items():
            for rev in (False, True):
                A = fixed
                B = movable if not rev else movable[::-1]
                # mode fixed: pre-rotate disk to sector k
                for k in range(9):
                    def ring_sub(offset):
                        o = []
                        for c in syms:
                            try:
                                p = B.index(c)
                            except ValueError:
                                o.append("?"); continue
                            o.append(A[(p + offset) % 9])
                        return "".join(o)
                    pt = ring_sub(k)
                    for x in _alberti_emit(pt, maps, seen):
                        yield x
                # mode rotor: offset = position (advance +1 per symbol)
                o = []
                for j, c in enumerate(syms):
                    try:
                        p = B.index(c)
                    except ValueError:
                        o.append("?"); continue
                    o.append(A[(p + j) % 9])
                for x in _alberti_emit("".join(o), maps, seen):
                    yield x
                # mode marker: advance +1 whenever c == index letter m
                for m in "abcdefghi":
                    off = 0
                    o = []
                    for c in syms:
                        try:
                            p = B.index(c)
                        except ValueError:
                            o.append("?"); continue
                        o.append(A[(p + off) % 9])
                        if c == m:
                            off = (off + 1) % 9
                    for x in _alberti_emit("".join(o), maps, seen):
                        yield x


def _alberti_emit(pt, maps, seen):
    """Emit candidate X forms for one disk-read plaintext string `pt`: the
    big-int in the a..i ring value-base (ring as digits is EITHER pos
    a=0..i=8 / base-9 OR canon a=1..i=9 / base-10, the certified interpreter
    readings of this puzzle) -> hex -> ASCII, printable only. (A direct yield
    of the {a..i} disk output is not emitted: a-i letters cannot spell any of
    the puzzle's real words -- m/x/t/s are not in the ring.) Dedup via `seen`
    (per surface invocation)."""
    if "?" in pt:
        return []
    out = []
    for wine, mp in maps.items():
        digits = "".join(mp.get(c, c) for c in pt)
        if not digits or not all(c.isdigit() for c in digits):
            continue
        base = 9 if max(digits) <= "8" else 10
        try:
            n = int(digits, base)
        except ValueError:
            continue
        if n <= 0:
            continue
        txt = _hex_ascii(n)
        if (txt and 8 <= len(txt) <= 2000
                and all(32 <= ord(ch) <= 126 for ch in txt)):
            key = (wine, txt)
            if key not in seen:
                seen.add(key)
                out.append(txt)
    return out


def _alberti_read(pt, maps, seen):
    """DEPRECATED wrapper -- kept for compatibility with any external callers;
    delegates to _alberti_emit."""
    return _alberti_emit(pt, maps, seen)


def cell_rotring(surface, params):
    """late-284. Cipher-disk reading on the DIGIT ring itself: the jpillora disk
    rotates an alphabet by k sectors; applied to the interpreter this is a cyclic
    / affine bijection of the digit-ring INDEX (letter canon value-1, 0..8, or
    0..9 with o=0) BEFORE the big-int base read -- a family no cell sweeps (prior
    caesar cell rotated the ENGLISH alphabet, not the digit ring). Covers k=0..8
    rotations plus coprime affine maps (idx -> idx*slope+off mod ring), base-9
    and base-10 reads. Config is a =val-1 bijection: canon a=1..i=9 maps to index
    0..8, so rotating/modding stays inside valid base digits."""
    idx9 = [(ord(c) - 97) for c in surface.lower() if "a" <= c <= "i"]
    if idx9:
        for k in range(9):
            out = "".join(str((i + k) % 9) for i in idx9)
            try:
                txt = _hex_ascii(int(out, 9))
            except ValueError:
                continue
            if txt and 8 <= len(txt) <= 2000:
                yield txt
        for slope in (1, 2, 4, 5, 7, 8):
            for off in range(9):
                out = "".join(str((i * slope + off) % 9) for i in idx9)
                try:
                    txt = _hex_ascii(int(out, 9))
                except ValueError:
                    continue
                if txt and 8 <= len(txt) <= 2000:
                    yield txt
    val10 = []
    for c in surface.lower():
        if "a" <= c <= "i":
            val10.append(ord(c) - 96)
        elif c == "o":
            val10.append(0)
    if val10:
        for k in range(10):
            out = "".join(str((v + k) % 10) for v in val10)
            try:
                txt = _hex_ascii(int(out, 10))
            except ValueError:
                continue
            if txt and 8 <= len(txt) <= 2000:
                yield txt


CELLS = {
    "vic": cell_vic,
    "interp10": cell_interp,
    "interp9": cell_interp9,
    "xor": cell_xor,
    "hexpairs": cell_hexpairs,
    "classical": cell_classical,
    "keyed": cell_keyed,
    "rotring": cell_rotring,
    "alberti": cell_alberti,
}
DEFAULT_PARAMS = {"vic": {}, "interp10": {}, "interp9": {}, "xor": {},
                  "classical": {"direct": True}, "keyed": {}, "rotring": {},
                  "alberti": {}, "hexpairs": {}}


CLASSIC_WITNESS_CANDIDATES = [
    "CLASSICALTESTWITNESS", "VELOCIRAPTOR", "PTERODACTYL", "DIGITALLOGIC",
    "REDQUEEN", "MOBIUSSTRIP", "BILLIONDOLLARSOAP",
]


def _classic_witness_ok(P: str) -> bool:
    """P must round-trip through interp10(canon)+atbash: its interp digit string
    (the decimal expansion of atbash(P)'s hex) must contain no '0' (canon is
    a=1..i=9 and has no zero symbol)."""
    at = Atbash().encrypt(P.lower(), None, SPA.ENGLISH)
    dnum = str(int(at.encode().hex(), 16))
    return "0" not in dnum


def _pick_classic_witness():
    """Search a T (interp text) whose interp digit-string has no '0' (canon has
    no zero symbol), then use P = atbash(T) as the navigable control; atbash is
    self-inverse so the cell re-decodes P through interp10+atbash."""
    for P in ("VELOCIRAPTOR", "PTERODACTYL", "REDQUEEN", "MOBIUSSTRIP"):
        if _classic_witness_ok(P):
            return P
    import random
    rng = random.Random(19820)
    for length in range(16, 9, -1):
        for _ in range(6000):
            t = "".join(rng.choice("etnaroism") for _ in range(length))
            dnum = str(int(t.encode().hex(), 16))
            if "0" not in dnum:
                return Atbash().encrypt(t, None, SPA.ENGLISH).upper()
    raise RuntimeError("no zero-free classical witness found")


def _b9_str(t: str) -> str:
    n = int(t.encode().hex(), 16)
    if n == 0:
        return "0"
    ds = ""
    while n:
        n, r = divmod(n, 9)
        ds = str(r) + ds
    return ds


def _pick_rotring_witness():
    """Any P works: the base-9 digit expansion maps bijectively onto a-i via
    index = digit (letter value-1), so no zero-free constraint applies."""
    return "ROTRINGTEST"


def encode_control(cellname: str, plaintext: str):
    """Plaintext -> surface-string under the cell's convention (for injection)."""
    if cellname == "vic":
        # cell_vic consumes LETTER surfaces and encodes internally via the board
        return plaintext
    if cellname == "interp10":
        dnum = str(int(plaintext.encode().hex(), 16))
        return "".join("abcdefghi"[int(d) - 1] for d in dnum)
    if cellname == "interp9":
        n = int(plaintext.encode().hex(), 16)
        ds = ""
        while n:
            n, r = divmod(n, 9)
            ds = str(r) + ds
        return "".join("abcdefghi"[int(d)] for d in (ds or "0"))
    if cellname == "xor":
        kb = b"KCQ"
        return "".join(chr(ord(c) ^ kb[i % 3]) for i, c in enumerate(plaintext))
    if cellname == "classical":
        # control: cell = interp10(surface) then classical decipher; atbash is
        # self-inverse, so the surface must be interp10(atbash(P)).
        at = Atbash().encrypt(plaintext.lower(), None, SPA.ENGLISH)
        dnum = str(int(at.encode().hex(), 16))
        return "".join("abcdefghi"[int(d) - 1] for d in dnum)
    if cellname == "keyed":
        # control: keyword 'matrixsumlist' over the 0..9 domain. encloses P's
        # decimal so the cell's fwd substitution reproduces it after reading.
        domain = "0123456789"
        key = "matrixsumlist"
        seen, A = set(), ""
        for ch in key:
            if ch in domain and ch not in seen:
                A += ch
                seen.add(ch)
        for ch in domain:
            if ch not in seen:
                A += ch
                seen.add(ch)
        fwd = {domain[i]: A[i] for i in range(10)}
        inv = {v: k for k, v in fwd.items()}
        dnum = str(int(plaintext.encode().hex(), 16))
        x = "".join(inv.get(c, c) for c in dnum)
        return "".join("o" if d == "0" else "abcdefghi"[int(d) - 1] for d in x)
    if cellname == "rotring":
        # control: base-9 expansion d (0..8) -> surface letter = index d+3 on the
        # a-i ring (letter value-1); the cell's k-sweep re-finds P at k=6.
        b9 = _b9_str(plaintext)
        return "".join("abcdefghi"[(int(d) + 3) % 9] for d in b9)
    if cellname == "alberti":
        # control: identity rings + k=0 read: surface letter = pos map digit
        # (a=0..i=9) of P's base-9 expansion; the cell's (abc,abcdefghi,k=0,pos)
        # arm re-finds P. Never contains the marker letters watch-free this way.
        b9 = _b9_str(plaintext)
        return "".join("abcdefghi"[int(d)] for d in b9)
    if cellname == "hexpairs":
        return plaintext.encode("ascii").hex()
    raise ValueError(cellname)


def gen(battery_surfaces, only=None, one_map_extra=None):
    cands = set()
    n_cell_forms = 0
    for sname, surface in battery_surfaces.items():
        for cname, cell in CELLS.items():
            if only and cname not in only:
                continue
            for form in cell(surface, DEFAULT_PARAMS[cname]):
                n_cell_forms += 1
                if form:
                    cands.add(form)
                    cands.add(form[::-1])
    return cands, n_cell_forms


def selftest():
    ok = True
    for cname in CELLS:
        P = {"vic": "BATTERYWITNESS", "interp10": "INTERPRET",
             "interp9": "PUZZLETEST", "xor": "XORTESTWITNESS",
             "classical": _pick_classic_witness(), "keyed": "KEYEDWITNESS",
             "rotring": _pick_rotring_witness(),
             "alberti": "ALBERTIDISKTEST",
             "hexpairs": "AUDIONUMBERSTREAM"}[cname]
        s = encode_control(cname, P)
        cands, _ = gen({cname + ".wit": s}, only=[cname])
        forms = set(cands)
        if P not in forms and P[::-1] not in forms:
            return False, f"{cname}: control {P!r} not re-found"
    return True, "selftest OK (all cells re-find their injection control)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--both", action="store_true")
    ap.add_argument("--string", help="raw literal surface")
    ap.add_argument("--names", help="comma list of builtin surface names (default all raw streams)")
    ap.add_argument("--grid", action="store_true", help="add the grid traversal digit surfaces")
    ap.add_argument("--sticker", action="store_true", help="add the sticker tile color-class surfaces")
    ap.add_argument("--only", help="comma list of cells to run")
    args = ap.parse_args()

    if args.selftest:
        st, msg = selftest()
        print(msg)
        return 0 if st else 1

    surfaces = {}
    if args.string is not None:
        surfaces["arg"] = args.string
    if args.names:
        for n in args.names.split(","):
            n = n.strip()
            if n in BUILTIN_SURFACES:
                surfaces[n] = BUILTIN_SURFACES[n]
    if args.names is None and not args.string and not args.grid and not args.sticker:
        surfaces = dict(BUILTIN_SURFACES)
    if args.grid:
        surfaces.update(grid_surfaces())
    if args.sticker:
        surfaces.update(sticker_surfaces())

    only = args.only.split(",") if args.only else None
    t0 = time.time()
    cands, n_forms = gen(surfaces, only=only)
    with open(SCRATCH, "w") as f:
        f.writelines(c + "\n" for c in sorted(cands))
    print(f"[cipher_battery] {len(surfaces)} surfaces x cells -> {n_forms} cell forms, "
          f"{len(cands)} unique candidates ({time.time()-t0:.0f}s) -> {SCRATCH}")
    if args.both:
        for prog in ("oracle.py", "oracle_dualite.py"):
            p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", prog), "--stdin"],
                               stdin=open(SCRATCH), capture_output=True, text=True)
            lines = [l for l in p.stdout.splitlines() if l.strip()]
            print(f"[cipher_battery] {prog}: {lines[-1] if lines else 'NO MATCH'}")
            # A real hit prints a line STARTING with "MATCH " (oracle.py:366).
            # Substring tests are wrong in both directions here: bare
            # `"MATCH" in stdout` fires on "NO MATCH", while adding
            # `and "NO MATCH" not in stdout` SUPPRESSES a genuine hit, because
            # a batch containing one match also contains many NO MATCH lines.
            if any(l.startswith("MATCH ") for l in lines):
                print(p.stdout)
                return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())