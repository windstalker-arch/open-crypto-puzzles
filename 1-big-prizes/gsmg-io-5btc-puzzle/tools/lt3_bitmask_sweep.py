#!/usr/bin/env python3
"""lt3_bitmask_sweep.py -- "tiny hint <3" positional-bitmask family (session 2026-09-14).

Premise (interpretive, NOT author-certified): the 2026-01-01 official hint ends
"here's a 'tiny hint' <3." Reading "<3" literally as "strictly less than three",
each digit stream is converted into a positional bitmask (1 = token value < 3,
0 = otherwise), packed to bytes, and every packed form is submitted as a candidate
answer X to BOTH gate addresses' oracles. Also tested: the kept-letter subsequence
and its digit-string, and, for the length-256 object, the packed bytes as a direct
private-key scalar.

Three documented value encodings are used for the token -> integer step:
  m_bi   D=0,B=1,I=2,F=3,H=4,C=5,E=6,G=7,A=8,K=9  (Bifid square row)
  m_hex  o=0,a=1,b=2,c=3,d=4,e=5,f=6,g=7,h=8,i=9   (page hex-letter encoding)
  m_nat  a=0,b=1,c=2,d=3,e=4,f=5,g=6,h=7,i=8       (plain ordinal)

Under "<3" the surviving symbol sets are respectively {d,b,i}, {o,a,b}, {a,b,c}.
For streams without 'o', m_hex/m_nat reduce to {a,b} resp. {a,b,c}.

Candidates per (stream, map): 4 packed byte strings (bit order x token order)
x 3 string forms (hex / sha256(hex) / sha256d(hex)), plus kept-subsequence and
digit-string = 14 X strings, each sent to the small-blob oracle (1GSMG1JC9) and
the Dualite oracle (17ucy1K9).

The small oracle's attempt() computes password = sha256(X).hexdigest(), decrypts
the 96-byte salted blob under both EVP digests, reduces the plaintext (first32 /
last32 / sha256 / sha256(first64)) to 32-byte scalars and compares the P2PKH to
the gate. The Dualite oracle's attempt() does the same over the cosmic blob with
an extended reading set. Both oracles passed --selftest immediately prior.

Gate h160s are decoded from the addresses at runtime (base58check), not hardcoded.
Witness checks are printed before the loop: the packer against a hand-computed
vector, and the pipeline against a known-good wrong answer ("causality") that must
produce NO MATCH through the exact attempt() code path used below.
"""

from __future__ import annotations
import os

import hashlib
import json
import time

import base58

from oracle import attempt as small_attempt
from oracle_dualite import attempt as dualite_attempt
from oracle_dualite import load_dualite_b64

ROOT = os.path.expanduser("~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle")


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def addr_h160(address: str) -> bytes:
    return base58.b58decode_check(address)[1:21]


G1 = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
G2 = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"
H160_G1 = addr_h160(G1)
H160_G2 = addr_h160(G2)

MAPS = {
    "m_bi": dict(d=0, b=1, i=2, f=3, h=4, c=5, e=6, g=7, a=8, o=9),
    "m_hex": dict(o=0, a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, i=9),
    "m_nat": dict(a=0, b=1, c=2, d=3, e=4, f=5, g=6, h=7, i=8, o=9),
}
LT = 3


def load_streams() -> dict:
    """Digit-encoded streams only. odd_pre_reduction / object_256 are already
    reduced over a mixed a-z alphabet (no digit encoding -> the value map, and
    therefore the <3 predicate, does not apply; excluded on that ground)."""
    fp = json.load(open(ROOT + "/data/finalpage-digit-streams.json"))
    sp = json.load(open(ROOT + "/data/salphaseion-streams.json"))
    dbbib_69 = fp["dbbib"]
    dbbib_91 = fp["dbbib_91"]
    faed_571 = fp["faed_570"]
    assert faed_571.endswith("z"), "expected trailing z separator"
    faed = faed_571[:-1]
    return {
        "dbbib_69": dbbib_69,
        "dbbib_91": dbbib_91,
        "faed_570": faed,
        "even_stream": sp["even_stream"],
        "dropped_29": sp["dropped_29"],
        "z_segment_1": fp["z_segment_1"],
        "z_segment_2": fp["z_segment_2"],
    }


def bits_for(tokens: str, mapping: dict) -> list[int]:
    return [1 if mapping[t.lower()] < LT else 0 for t in tokens]


def pack_fix(seq: list[int], lsb_first: bool) -> bytes:
    """Pack bit list to bytes (each input byte = 8 sequence bits). Order of the
    sequence is preserved; within a byte, bit i goes to bit (7-i) for MSB-first
    packing and to bit i for LSB-first packing. Partial final byte is LSB-zero-padded,
    i.e. MSB-first: pad at the low end; LSB-first: pad at the high end."""
    out = bytearray()
    for i in range(0, len(seq), 8):
        chunk = seq[i:i + 8]
        b = 0
        for j, bit in enumerate(chunk):
            if lsb_first:
                b |= bit << j
            else:
                b |= bit << (7 - j)
        out.append(b)
    return bytes(out)


def scalar_h160(priv: bytes) -> bytes | None:
    """Uncompressed secp256k1 pubkey HASH160 of a 32-byte scalar, or None."""
    if len(priv) != 32:
        return None
    try:
        from ecdsa import SECP256k1, SigningKey
        sk = SigningKey.from_string(priv, curve=SECP256k1)
        pub = b"\x04" + sk.get_verifying_key().to_string()
        return hashlib.new("ripemd160", sha256(pub)).digest()
    except Exception:
        return None
    return None


def main() -> None:
    streams = load_streams()
    dual_b64 = load_dualite_b64()

    # ---- witnesses -----------------------------------------------------------
    vec = pack_fix([1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], False)
    assert vec.hex() == "ff00", vec.hex()
    vec2 = pack_fix([1, 0, 1, 1, 0, 0, 1, 1], False)
    assert vec2.hex() == "b3", vec2.hex()
    vec3 = pack_fix([1, 0, 1, 1, 0, 0, 1, 1], True)
    assert vec3.hex() == "cd", vec3.hex()  # 0b11001101
    okk, _ = small_attempt("causality")            # known puzzle word: must be NO MATCH
    assert okk is False
    okd, _ = dualite_attempt("causality", dual_b64)
    assert okd is False
    print("WITNESS pack vectors OK (ff00, b3, cd); 'causality' -> NO MATCH on both gates")

    # ---- sweep ---------------------------------------------------------------
    started = time.time()
    n = 0
    hits = []
    for name, toks in sorted(streams.items()):
        for mname, mapping in MAPS.items():
            bits = bits_for(toks, mapping)
            kept_toks = "".join(t for t in toks if mapping[t.lower()] < LT)
            dstr = "".join(str(mapping[t.lower()]) for t in toks if mapping[t.lower()] < LT)
            for rev in (False, True):
                seq = bits[::-1] if rev else bits
                for lsb in (False, True):
                    B = pack_fix(seq, lsb)
                    forms = [B.hex(), sha256(B).hex(), sha256(sha256(B)).hex()]
                    for x in forms:
                        n += 1
                        ok, info = small_attempt(x)
                        if ok:
                            hits.append(("SMALL", name, mname, rev, lsb, "pack", x, info))
                        ok, info = dualite_attempt(x, dual_b64)
                        n += 1
                        if ok:
                            hits.append(("DUALITE", name, mname, rev, lsb, "pack", x, info))
                    if len(B) == 32:
                        h = scalar_h160(B)
                        n += 1
                        if h in (H160_G1, H160_G2):
                            hits.append(("SCALAR", name, mname, rev, lsb, "scalar", B.hex(), h.hex()))
            # kept-subsequence and digit-string, fwd and rev
            for label, base in (("kept", kept_toks), ("digits", dstr)):
                for x in (base, base[::-1]):
                    n += 1
                    ok, info = small_attempt(x)
                    if ok:
                        hits.append(("SMALL", name, mname, False, False, label, x, info))
                    ok, info = dualite_attempt(x, dual_b64)
                    n += 1
                    if ok:
                        hits.append(("DUALITE", name, mname, False, False, label, x, info))

    elapsed = time.time() - started
    print(f"sweep done: {n} candidates through both gates in {elapsed:.1f}s "
          f"({n/elapsed:.0f}/s)")
    if hits:
        for h in hits:
            print("HIT", h)
    else:
        print("NO MATCH on either gate")


if __name__ == "__main__":
    main()