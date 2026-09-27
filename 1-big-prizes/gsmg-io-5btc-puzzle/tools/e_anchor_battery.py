#!/usr/bin/env python3
"""e_anchor_battery.py -- E_S-anchored "deep keyed alphabet leap" tests.

Novelty (per 2026-09-21 red-team coverage audit of analysis/tested.md):
  - E_S (B2_79[64:79] = 740a25de...) has NEVER been used as a decode/anchoring
    TARGET. Every prior row treats it as a scalar/password-tail operand. This
    battery makes E_S the acceptance predicate for windowed reads of the
    a..i streams (the "interpreter-alphabet leap" produces a 15-byte blob).
  - B1_79/B2_79 fields have never been used as BIP32 root seeds or E_S-padded
    private-key scalars (late-65 only did x-coordinate and concat-hash reads).

Sections:
  A. E_S-anchored window scan: for each stream feed x digit map x base,
     slide every window of length L in 28..44, compare its integer value to
     int(E_S). Equality = E_S is exactly a contiguous token-window of the
     stream under that map (the "leap").
  B. E_S/blob scalars as private keys -> P2PKH(compressed+uncompressed) vs gates.
  C. B1_79/B2_79 fields as BIP32 root seeds (bip_utils) across standard paths
     -> P2PKH(compressed) vs gates.

All checks are LOCAL (gate addresses known); no oracle invocation.
Selftest asserts blob hashes + gate address mechanics.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys

import base58
from ecdsa import SECP256k1, SigningKey
from bip_utils import Bip32Slip10Secp256k1

BASE = os.path.expanduser(
    "~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle")

B1_SHA = "1449a2178eea7c0e3fabac8c1ad2afa294be4fc1800c594a025a056e88c626bf"
B2_SHA = "b40fce72ef5638e4f79b3233e653f8a5dbdb0d4ae2009d2d3da2c98b70f4d004"
E_S_HEX = "740a25de4b8e946d0a5ae2667a23a2"
G1 = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
G2 = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"
GATES = {"G1": G1, "G2": G2}

# maps: name -> {token char -> digit} ; base implied by max digit
MAPS = {
    "pos0":  {c: i for i, c in enumerate("abcdefghi")},   # a=0..i=8, base 9
    "revpos0": {c: 8 - i for i, c in enumerate("abcdefghi")},
    "canon": {c: i + 1 for i, c in enumerate("abcdefghi")},  # a=1..i=9, base10
    "revcanon": {c: 9 - i for i, c in enumerate("abcdefghi")},
}
BASE_OF = {"pos0": 9, "revpos0": 9, "canon": 10, "revcanon": 10}
O_TO_ZERO = {"canon": True, "revcanon": True}  # certified z-segment o=0

BIP_PATHS = [
    "m/0", "m/0h", "m/1", "m/0h/0", "m/0h/1",
    "m/44h/0h/0h/0/0", "m/44h/0h/0h/0/1", "m/44h/0h/0h/1/0",
    "m/49h/0h/0h/0/0", "m/84h/0h/0h/0/0",
]


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def hash160(d: bytes) -> bytes:
    return hashlib.new("ripemd160", sha256(d)).digest()


def p2pkh(priv_int: int, compressed: bool) -> str | None:
    try:
        sk = SigningKey.from_secret_exponent(priv_int, curve=SECP256k1)
    except Exception:
        return None
    vk = sk.verifying_key
    if compressed:
        prefix = b"\x02" if vk.pubkey.point.y() % 2 == 0 else b"\x03"
        pub = prefix + vk.pubkey.point.x().to_bytes(32, "big")
    else:
        pub = b"\x04" + vk.pubkey.point.x().to_bytes(32, "big") \
            + vk.pubkey.point.y().to_bytes(32, "big")
    return base58.b58encode_check(b"\x00" + hash160(pub)).decode()


def check_addr(addr: str, origin: str, hits: list):
    for g, target in GATES.items():
        if addr == target:
            hits.append(f"MATCH {g}  <-- {origin}")


def load_streams():
    j = json.load(open(os.path.join(BASE, "data/finalpage-digit-streams.json")))
    dbbib_91 = j["dbbib_91"]
    faed = j["faed_570"].rstrip("z")
    z1, z2 = j["z_segment_1"], j["z_segment_2"]
    return {
        "dbbib_91": dbbib_91,
        "faed_570(z)": faed,
        "dbbib_91+faed": dbbib_91 + faed,
        "faed+dbbib_91": faed + dbbib_91,
        "dbbib+faed+z1z2": dbbib_91 + faed + z1 + z2,
    }


def encode(stream: str, mname: str) -> list[int] | None:
    m = MAPS[mname]
    base = BASE_OF[mname]
    out = []
    for ch in stream:
        if ch in m:
            out.append(m[ch])
        elif ch == "o" and O_TO_ZERO.get(mname):
            out.append(0)
        else:
            return None
    # sanity: every digit < base
    if out and max(out) >= base:
        return None
    return out


def section_a(hits: list):
    """E_S-anchored windowed-value scan."""
    e_int = int(E_S_HEX, 16)
    n_win = 0
    feeds = load_streams()
    print("A. E_S-anchored window scan "
          f"(target int(E_S) = {e_int}, {e_int.bit_length()} bits)")
    for fname, stream in feeds.items():
        for mname in MAPS:
            d = encode(stream, mname)
            if d is None:
                continue
            base = BASE_OF[mname]
            n = len(d)
            for rev in (False, True):
                ds = d[::-1] if rev else d
                tag = f"{fname}/{mname}{'/rev' if rev else ''}"
                for L in range(28, 45):
                    p = base ** L
                    v = 0
                    for i in range(L):
                        v = v * base + ds[i]
                    if v == e_int:
                        hits.append(f"E_S = window len {L} @0 of {tag}")
                        print(f"  >>> {E_S_HEX} == window {L}@0 of {tag}")
                    for i in range(L, n):
                        v = (v - ds[i - L] * p) * base + ds[i]
                        n_win += 1
                        if v == e_int:
                            hits.append(f"E_S = window len {L} @{i - L + 1} of {tag}")
                            print(f"  >>> {E_S_HEX} == window {L}@{i - L + 1} of {tag}")
                    n_win += L
    print(f"A. scanned {n_win} windows; hits={len(hits)}")


def section_b(hits: list):
    """Blob fields as private-key scalars -> gate addresses."""
    b2 = open(os.path.join(BASE, "data/B2_79B.bin"), "rb").read()
    b1 = open(os.path.join(BASE, "data/B1_79B.bin"), "rb").read()
    ks1, ks2, es = b2[:32], b2[32:64], b2[64:79]
    cands = {
        "E_S(zpad_big)": es + b"\x00" * 17,
        "E_S(zpad_little)": b"\x00" * 17 + es,
        "sha256(E_S)": sha256(es),
        "sha256(sha256(E_S))": sha256(sha256(es)),
        "sha256(E_S)||E_S": sha256(es) + es,
        "E_S||sha256(E_S)": es + sha256(es),
        "sha256(B1_79)": sha256(b1),
        "sha256(B2_79)": sha256(b2),
        "K_S1 xor K_S2": bytes(a ^ b for a, b in zip(ks1, ks2)),
    }
    print("B. blob/E_S scalar private keys -> gates")
    for name, raw in cands.items():
        if len(raw) < 32:
            continue
        priv = int.from_bytes(raw[:32], "big")
        if not (0 < priv < SECP256k1.order):
            continue
        for comp in (False, True):
            check_addr(p2pkh(priv, comp), f"{name}/{'c' if comp else 'u'}", hits)
    print(f"B. {len(cands)} scalar candidates checked")


def section_c(hits: list):
    """Blob fields as BIP32 root seeds across standard paths."""
    b2 = open(os.path.join(BASE, "data/B2_79B.bin"), "rb").read()
    b1 = open(os.path.join(BASE, "data/B1_79B.bin"), "rb").read()
    es = b2[64:79]
    seeds = {
        "sha256(B1_79)": sha256(b1),
        "sha256(B2_79)": sha256(b2),
        "K_S1": b2[:32],
        "K_S2": b2[32:64],
        "E_S(zpad32)": es + b"\x00" * 17,
        "sha256(E_S)": sha256(es),
    }
    print("C. blob fields as BIP32 root seeds")
    n = 0
    for sname, ent in seeds.items():
        try:
            ctx0 = Bip32Slip10Secp256k1.FromSeed(ent)
        except Exception:
            continue
        for path in BIP_PATHS:
            try:
                dv = ctx0.DerivePath(path)
                cpub = dv.PublicKey().RawCompressed().ToBytes()
            except Exception:
                continue
            addr = base58.b58encode_check(b"\x00" + hash160(cpub)).decode()
            n += 1
            check_addr(addr, f"BIP32 {sname} {path}/c", hits)
    print(f"C. {n} BIP32 derivations checked")


def section_d(hits: list):
    """Histogram-feasibility: does any window of a stream have the SAME
    symbol-frequency histogram as the base-b digit expansion of int(E_S)?
    If yes, SOME keyed-alphabet map makes that window read exactly as E_S
    (necessary condition for the "deep keyed alphabet leap")."""
    e_int = int(E_S_HEX, 16)
    targets = {}
    for base in (9, 10):
        rem, digs = e_int, []
        # E_S is 119 bits; base-9 needs 38 digits, base-10 needs 36
        L = 36 if base == 10 else 40
        while rem:
            rem, r = divmod(rem, base)
            digs.append(r)
        digs.reverse()
        # leading digit set matters: possible under any assignment
        targets[base] = tuple(sorted(digs))
    feeds = load_streams()
    print("D. window-histogram feasibility of int(E_S)")
    n = 0
    for fname, stream in feeds.items():
        for mname in ("pos0", "canon"):
            d = encode(stream, mname)
            if d is None:
                continue
            base = BASE_OF[mname]
            tgt = targets[base]
            L = len(tgt)
            hist = [0] * base
            for i in range(L):
                hist[d[i]] += 1
            ms = tuple(sorted(i0 for i0 in range(base) for _ in range(hist[i0])))
            if ms == tgt:
                hits.append(f"histogram match @0 {fname}/{mname}/{base} L={L}")
                print(f"  >>> {fname}/{mname} window 0..{L} hist==E_S digit ms")
            for i in range(L, len(d)):
                hist[d[i - L]] -= 1
                hist[d[i]] += 1
                n += 1
                ms = tuple(sorted(i0 for i0 in range(base) for _ in range(hist[i0])))
                if ms == tgt:
                    hits.append(f"histogram match @{i-L+1} {fname}/{mname}/{base} L={L}")
                    print(f"  >>> {fname}/{mname} window {i-L+1}..{i+1} hist==E_S digit ms")
    print(f"D. {n} windows histogram-checked; feasible_hits={len(hits)}")


def _keyed_digit_map(seq: str, ndigits: int = 9) -> list[int] | None:
    """"Deep keyed alphabet leap": keyed DIGIT alphabet derived from bytes of
    a blob field (nibble hex chars), first-distinct then fill lowest missing.
    Returns an ordering of digits 0..9 (first `ndigits` used for a..i)."""
    order: list[int] = []
    seen: set[int] = set()
    for ch in seq:
        if '0' <= ch <= '9':
            v = int(ch)
        elif 'a' <= ch <= 'f':
            v = ord(ch) - ord('a') + 10
        else:
            continue
        if v not in seen:
            seen.add(v)
            order.append(v)
        if len(order) == 10:
            break
    for v in range(10):
        if v not in seen:
            order.append(v)
    return order[:10]


def section_e(hits: list):
    """Use blob-field bytes as the KEYED DIGIT ALPHABET source for the a..i
    interpreter leap; decode the streams and check for printable text, the
    E_S hex substring, and E_S window equality."""
    b2 = open(os.path.join(BASE, "data/B2_79B.bin"), "rb").read()
    b1 = open(os.path.join(BASE, "data/B1_79B.bin"), "rb").read()
    es = b2[64:79]
    es_hex = es.hex()
    sources = {
        "E_S": es_hex,
        "E_S_rev": es_hex[::-1],
        "sha256(E_S)": sha256(es).hex(),
        "sha256^2(E_S)": sha256(sha256(es)).hex(),
        "K_S2": b2[32:64].hex(),
        "K_S1": b2[:32].hex(),
        "K_C2": b1[32:64].hex(),
        "K_C1": b1[:32].hex(),
        "sha256(B1)": sha256(b1).hex(),
        "sha256(B2)": sha256(b2).hex(),
        "E_S_nibbles_bytewise": "".join(f"{x:02x}" for x in es),
        "E_S||K_S1crumb": (es + b2[0:17]).hex(),
    }
    feeds = load_streams()
    e_int = int(E_S_HEX, 16)
    print("E. blob-derived keyed digit alphabets (deep-keyed leap)")
    n = 0
    for sname, hx in sources.items():
        keyed = _keyed_digit_map(hx)
        if keyed is None:
            continue
        # map a..i -> keyed[0..8]
        m = {c: keyed[i] for i, c in enumerate("abcdefghi")}
        for fname, stream in feeds.items():
            if "z1z2" in fname:
                continue
            try:
                d = [m[c] for c in stream if c in m]
            except KeyError:
                continue
            if len(d) != len(stream):
                continue
            n += 1
            digits = "".join(map(str, d))
            val = int(digits, 10)
            hx_out = f"{val:x}"
            bts = bytes.fromhex(hx_out) if len(hx_out) % 2 == 0 else b""
            printable = bool(bts) and all(32 <= b < 127 for b in bts)
            found_sub = E_S_HEX in hx_out
            # window equality
            window_eq = False
            if len(d) >= 28:
                for L in range(28, min(45, len(d)) + 1):
                    v = 0
                    for i in range(L):
                        v = v * 10 + d[i]
                    if v == e_int:
                        window_eq = True
                        hits.append(f"E window {L}@0 {sname}/{fname}")
            txt = ""
            if len(hx_out) % 2 == 0:
                try:
                    txt = bytes.fromhex(hx_out).decode("latin1")
                except Exception:
                    pass
            if printable or found_sub or window_eq:
                hits.append(f"keyed-decode hit {sname}/{fname}: printable={printable} E_Ssub={found_sub} window_eq={window_eq}")
                print(f"  >>> {sname}/{fname} printable={printable} E_Ssub={found_sub} window_eq={window_eq}")
                if printable:
                    print(f"        ascii={txt[:120]!r}")
    print(f"E. {n} keyed-alphabet full-stream decodes checked")


def section_f(hits: list):
    """Positional/transposition merges: E_S as a window of a RE-ROUTED a..i
    stream. The interpreter leap+cipher model writes tokens in one route and
    reads in another (VIC transposition, diagonals, spirals, snake rows).
    For each (feed,width,route) produce the rerouted token list, encode under
    pos0/canon, window-scan for int(E_S)."""
    e_int = int(E_S_HEX, 16)
    feeds = load_streams()

    def columnar_read(s: list[str], w: int, rev_cols: bool,
                      snake: bool) -> list[str]:
        rows = [s[i:i + w] for i in range(0, len(s), w)]
        out = []
        for c in range(w):
            col = [r[c] for r in rows if c < len(r)]
            if rev_cols:
                col = col[::-1]
            if snake and c % 2 == 1:
                col = col[::-1]
            out.extend(col)
        return out

    def diagonal_read(s: list[str], w: int, up: bool) -> list[str]:
        rows = [s[i:i + w] for i in range(0, len(s), w)]
        h = len(rows)
        out = []
        if up:
            # anti-diagonal index k = r + (w-1-c); collect by k
            for k in range(h + w - 1):
                for r in range(h):
                    c = w - 1 - (k - r)
                    if 0 <= c < w and c < len(rows[r]):
                        out.append(rows[r][c])
        else:
            for ssum in range(h + w - 1):
                r0, r1 = max(0, ssum - w + 1), min(h - 1, ssum)
                for r in range(r0, r1 + 1):
                    c = ssum - r
                    if 0 <= c < w and c < len(rows[r]):
                        out.append(rows[r][c])
        return out

    def spiral_read(s: list[str], w: int, ccw: bool) -> list[str] | None:
        if len(s) % w != 0:
            return None
        rows = [list(s[i:i + w]) for i in range(0, len(s), w)]
        h = len(rows)
        out = []
        top, bot, left, right = 0, h - 1, 0, w - 1
        while top <= bot and left <= right:
            if ccw:
                for r in range(top, bot + 1):      # left col down
                    out.append(rows[r][left])
                left += 1
                if left > right: break
                for c in range(left, right + 1):    # bottom row right
                    out.append(rows[bot][c])
                bot -= 1
                if top > bot: break
                for r in range(bot, top - 1, -1):   # right col up
                    out.append(rows[r][right])
                right -= 1
                if left > right: break
                for c in range(right, left - 1, -1):  # top row left
                    out.append(rows[top][c])
                top += 1
            else:
                for c in range(left, right + 1):    # top row right
                    out.append(rows[top][c])
                top += 1
                if top > bot: break
                for r in range(top, bot + 1):       # right col down
                    out.append(rows[r][right])
                right -= 1
                if left > right: break
                for c in range(right, left - 1, -1):  # bottom row left
                    out.append(rows[bot][c])
                bot -= 1
                if top > bot: break
                for r in range(bot, top - 1, -1):   # left col up
                    out.append(rows[r][left])
                left += 1
        return out

    print("F. transposition merges -> E_S window scan")
    n = 0
    for fname in ("dbbib_91", "faed_570(z)"):
        stream = feeds[fname]
        s = list(stream)
        L = len(s)
        widths = [w for w in range(5, 41) if w <= L and (L % w == 0 or w < L)]
        for w in widths:
            for route in ("cols", "cols_rev", "snake", "diag_down", "diag_up"):
                if route == "cols":
                    t = columnar_read(s, w, False, False)
                elif route == "cols_rev":
                    t = columnar_read(s, w, True, False)
                elif route == "snake":
                    t = columnar_read(s, w, False, True)
                elif route == "diag_down":
                    t = diagonal_read(s, w, False)
                else:
                    t = diagonal_read(s, w, True)
                for rev in (False, True):
                    ts = t[::-1] if rev else t
                    for mname in ("pos0", "canon"):
                        d = encode("".join(ts), mname)
                        if d is None:
                            continue
                        base = BASE_OF[mname]
                        for Lwin in range(28, 45):
                            p = base ** Lwin
                            v = 0
                            for i in range(min(Lwin, len(d))):
                                v = v * base + d[i]
                            if v == e_int:
                                hits.append(f"E_S window @0 {fname}/w{w}/{route}/rev/win{Lwin}/{mname}")
                            for i in range(Lwin, len(d)):
                                v = (v - d[i - Lwin] * p) * base + d[i]
                                n += 1
                                if v == e_int:
                                    hits.append(f"E_S window @{i-Lwin+1} {fname}/w{w}/{route}/rev/win{Lwin}/{mname}")
                            n += Lwin
            if len(s) % w == 0:
                for route in ("spiral_cw", "spiral_ccw"):
                    t = spiral_read(s, w, route == "spiral_ccw")
                    if t is None:
                        continue
                    for mname in ("pos0", "canon"):
                        d = encode("".join(t), mname)
                        if d is None:
                            continue
                        base = BASE_OF[mname]
                        for Lwin in range(28, 45):
                            p = base ** Lwin
                            v = 0
                            for i in range(min(Lwin, len(d))):
                                v = v * base + d[i]
                            if v == e_int:
                                hits.append(f"E_S window @0 {fname}/w{w}/{route}/win{Lwin}/{mname}")
                            for i in range(Lwin, len(d)):
                                v = (v - d[i - Lwin] * p) * base + d[i]
                                n += 1
                                if v == e_int:
                                    hits.append(f"E_S window @{i-Lwin+1} {fname}/w{w}/{route}/win{Lwin}/{mname}")
                            n += Lwin
    print(f"F. {n} transposed windows checked; hits={len(hits)}")


def _select_by_e_s(stream: str, mname: str, scheme: str, ebytes: bytes) -> int | None:
    """Offset-by-value selection: positions driven by E_S bytes/nibbles."""
    m = MAPS[mname]
    d = [m[c] for c in stream if c in m]
    if len(d) != len(stream):
        return None
    base = BASE_OF[mname]
    n = len(d)
    if n == 0:
        return None
    sel: list[int] = []
    if scheme == "byte_direct":
        for b in ebytes:
            sel.append(d[b % n])
        sel = sel * 3
    elif scheme == "byte_nibble":
        for b in ebytes:
            hi, lo = b >> 4, b & 0x0F
            sel.append(d[hi % n])
            sel.append(d[lo % n])
        sel = sel * 2
    elif scheme == "byte_fold":
        for b in ebytes:
            sel.append(d[b % n])
            sel.append(d[(b * 7) % n])
        sel = sel * 2
    else:
        return None
    v = 0
    for x in sel:
        v = v * base + x
    return v & ((1 << 128) - 1)


def section_g(hits: list):
    """Offset-by-value selection: E_S bytes as indices INTO the streams, then
    the selected token values read as a big int whose low 120 bits could be
    E_S itself (self-referential 'deep keyed leap')."""
    e_int = int(E_S_HEX, 16)
    b2 = open(os.path.join(BASE, "data/B2_79B.bin"), "rb").read()
    es = b2[64:79]
    feeds = load_streams()
    print("G. offset-by-value selection (E_S-derived indices)")
    n = 0
    for fname in ("dbbib_91", "faed_570(z)"):
        stream = feeds[fname]
        for mname in ("pos0", "canon"):
            for scheme in ("byte_direct", "byte_nibble", "byte_fold"):
                v = _select_by_e_s(stream, mname, scheme, es)
                n += 1
                if v is not None and v == e_int:
                    hits.append(f"select hit {fname}/{mname}/{scheme}")
                    print(f"  >>> {fname}/{mname}/{scheme} -> E_S")
    print(f"G. {n} selection configs checked")


def section_h(hits: list):
    """multistream merge: the page body is z/role-delimited word-groups; emit
    the a..i ones ONE AFTER ANOTHER in every order (feross/multistream
    semantics) and window-scan the concatenation for int(E_S)."""
    import itertools
    e_int = int(E_S_HEX, 16)
    feeds = load_streams()
    groups = {
        "dbbib_91": feeds["dbbib_91"],
        "faed_570": feeds["faed_570(z)"],
        "z1": feeds["dbbib+faed+z1z2"][len(feeds["dbbib_91"]) + len(feeds["faed_570(z)"])
                                      :][:63],
        "z2": feeds["dbbib+faed+z1z2"][len(feeds["dbbib_91"]) + len(feeds["faed_570(z)"])
                                      + 63:],
    }
    print("H. multistream permutation-concat window scan")
    n = 0
    for perm in itertools.permutations(groups):
        stream = "".join(groups[g] for g in perm)
        for mname in ("pos0", "canon"):
            d = encode(stream, mname)
            if d is None:
                continue
            base = BASE_OF[mname]
            for Lwin in range(28, 45):
                p = base ** Lwin
                v = 0
                for i in range(min(Lwin, len(d))):
                    v = v * base + d[i]
                if v == e_int:
                    hits.append(f"E_S window @0 {perm}/{mname}/win{Lwin}")
                for i in range(Lwin, len(d)):
                    v = (v - d[i - Lwin] * p) * base + d[i]
                    n += 1
                    if v == e_int:
                        hits.append(f"E_S window @{i-Lwin+1} {perm}/{mname}/win{Lwin}")
                n += Lwin
    print(f"H. {n} multistream windows checked; hits={len(hits)}")


def section_i(hits: list):
    """lead-0 construction premise: certified VIC board 'FUBCDORA.LETHINGKYMVPS.
    JQZXW' as the keyed alphabet. Every a..i letter sits on the board; take each
    stream token's board POSITION INDEX as its code (the 'deep keyed alphabet
    leap' = board position-codebook). Checks: (a) full-stream decode to ASCII,
    (b) E_S window equality, (c) E_S = sha256/md5 truncated digest of decode."""
    import hashlib as _hl
    board = "FUBCDORA.LETHINGKYMVPS.JQZXW"
    pos = {}
    for i, ch in enumerate(board):
        c = ch.lower()
        if c in "abcdefghi" and c not in pos:
            pos[c] = i
    var = {
        "raw_pos": lambda i: i,
        "atbash15": lambda i: 15 - i,
        "mod10": lambda i: i % 10,
        "mod10_atbash": lambda i: (9 - (i % 10)),
    }
    hexmap = "0123456789abcdef"
    feeds = load_streams()
    e_int = int(E_S_HEX, 16)
    es_bytes = bytes.fromhex(E_S_HEX)
    print("I. VIC board position-codebook vector reads")
    n = 0
    for fname in ("dbbib_91", "faed_570(z)", "dbbib_91+faed"):
        stream = feeds[fname]
        for vn, fn in var.items():
            for rev in (False, True):
                toks = stream[::-1] if rev else stream
                hexstr = "".join(hexmap[fn(pos[c])] if c in pos else "" for c in toks)
                if not hexstr:
                    continue
                n += 1
                val = int(hexstr, 16)
                zh = f"{val:x}"
                if len(zh) % 2:
                    zh = "0" + zh
                raw = bytes.fromhex(zh)
                printable = bool(raw) and all(32 <= b < 127 for b in raw)
                tag = f"{fname}/{vn}/{'r' if rev else ''}"
                if printable:
                    hits.append(f"printable {tag}: {raw[:80]!r}")
                # E_S window (hex-digit values as base-16 windows)
                for L in range(28, 45):
                    if L > len(hexstr):
                        continue
                    v = int(hexstr[:L], 16)
                    if v == e_int:
                        hits.append(f"E_S window@0 {tag}/L{L}")
                    cur = v
                    pw = 16 ** L
                    for i in range(L, len(hexstr)):
                        cur = (cur - int(hexstr[i - L], 16) * pw) * 16 + int(hexstr[i], 16)
                        if cur == e_int:
                            hits.append(f"E_S window@{i-L+1} {tag}/L{L}")
                # E_S truncated hash
                for hname, hfn in (("sha256", _hl.sha256), ("md5", _hl.md5)):
                    dig = hfn(raw).digest()[:15]
                    if dig == es_bytes:
                        hits.append(f"E_S = {hname}(decode)[0:15] {tag}")
    print(f"I. {n} board-codebook reads checked")


def selftest() -> int:
    b2 = open(os.path.join(BASE, "data/B2_79B.bin"), "rb").read()
    ok = True
    if len(b2) != 79:
        print("FAIL: B2_79 not 79 bytes"); ok = False
    if sha256(b2).hex() != B2_SHA:
        print("FAIL: B2_79 sha256 mismatch"); ok = False
    if b2[64:79].hex() != E_S_HEX:
        print("FAIL: E_S mismatch"); ok = False
    b1 = open(os.path.join(BASE, "data/B1_79B.bin"), "rb").read()
    if sha256(b1).hex() != B1_SHA:
        print("FAIL: B1_79 sha256 mismatch"); ok = False
    # mechanics: known on-chain pubkey -> G1 (uncompressed, recovered on-chain)
    pub = bytes.fromhex(
        "04f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464"
        "9c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559")
    if base58.b58encode_check(b"\x00" + hash160(pub)).decode() != G1:
        print("FAIL: G1 pubkey->address check"); ok = False
    else:
        print("PASS: G1 pubkey->address confirmed")
    # streams present
    j = json.load(open(os.path.join(BASE, "data/finalpage-digit-streams.json")))
    if len(j["dbbib_91"]) != 91 or len(j["faed_570"]) != 571:
        print("FAIL: stream lengths"); ok = False
    print(f"[selftest] {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--section", default="ABCDE", help="e.g. A, AB, ACD")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    hits: list[str] = []
    if "A" in args.section:
        section_a(hits)
    if "B" in args.section:
        section_b(hits)
    if "C" in args.section:
        section_c(hits)
    if "D" in args.section:
        section_d(hits)
    if "E" in args.section:
        section_e(hits)
    if "F" in args.section:
        section_f(hits)
    if "G" in args.section:
        section_g(hits)
    if "H" in args.section:
        section_h(hits)
    if "I" in args.section:
        section_i(hits)
    if hits:
        print("\n".join(hits))
        print("HITS PRESENT")
        sys.exit(0)
    print("NO MATCH on any gate; E_S not reproduced by any stream window.")


if __name__ == "__main__":
    main()