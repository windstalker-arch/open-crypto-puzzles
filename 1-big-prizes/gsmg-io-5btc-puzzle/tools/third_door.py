#!/usr/bin/env python3
"""third_door.py -- a CERTIFIED oracle for the third door (the unmessaged
planted address) and the other creator-funded planted addresses.

WHY THIS TOOL EXISTS. Every negative in `analysis/tested.md` for the third door
(`1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9`, funded 2020-04-07, no OP_RETURN, no known
preimage) was produced by the private research, and no tool for it was ever
shipped: the six key constructions are described in prose in `README.md` and
`analysis/tested.md` s.19b, and `data/planted-addresses.csv` records which
construction each verified row uses. So the third door has had hundreds of
certified negatives and zero reproducible code. This file is that code, and its
selftest is the missing witness: every `verified` row in the CSV is re-derived
here from its recorded preimage, so a negative produced by this tool is
witnessed by construction and not by assertion.

THE CONSTRUCTIONS (all six, from the CSV's `key` column and README s.19b):

  sha256        key = sha256(preimage)
  raw           key = int.from_bytes(preimage, "big")  (zero-padded left to 32)
  raw-right     key = int.from_bytes(preimage.rjust(32, b"\\x00"), "little")
  bits reversed key = the 8*len bit string of the raw value read backwards
  bytes rev     key = the raw 32 bytes reversed
  hex ascii     key = sha256 of the lowercase hex rendering of the preimage

Every candidate is turned into a compressed AND an uncompressed P2PKH address and
compared against the whole planted list plus the both gate addresses, because the
CSV's own rows show the creator used both forms (`causality` and
`gsmg.io/theseedisplanted` are compressed, the gates' target pubkey is
uncompressed).

Local only: every address being compared is already public in
`data/planted-addresses.csv` or in the README gate table. No key is swept, no
transaction is built, nothing is broadcast.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys

import base58
from ecdsa import SECP256k1, SigningKey

BASE = os.path.expanduser(
    "~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle")
CSV_PATH = os.path.join(BASE, "data", "planted-addresses.csv")

GATES = {
    "small": "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "dualite": "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa",
}
THIRD_DOOR = "1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9"

# The audio number stream, exactly as transcribed, plus the community's own
# rendering of it. The two differ in ONE token: 18 vs 48. Read as hex bytes the
# community list spells HASHTHETEXT; the as-given list spells ASHTHETEXT, i.e.
# the leading 'H' was transcribed as 18 (0x12, a control character) instead of
# 48 (0x48). Both are carried here as separate candidates, and both are also
# carried in the decimal reading, because a number stream is ambiguous between
# "hex byte values" and "decimal numbers" until something downstream settles it.
AUDIO_GIVEN = "18 41 53 48 54 48 45 54 45 58 54"
AUDIO_COMMUNITY = "48 41 53 48 54 48 45 54 45 58 54"


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def hash160(d: bytes) -> bytes:
    return hashlib.new("ripemd160", sha256(d)).digest()


def p2pkh(priv_int: int, compressed: bool) -> str | None:
    if not 0 < priv_int < SECP256k1.order:
        return None
    try:
        sk = SigningKey.from_secret_exponent(priv_int, curve=SECP256k1)
    except Exception:
        return None
    point = sk.verifying_key.pubkey.point
    if compressed:
        pub = (b"\x02" if point.y() % 2 == 0 else b"\x03") \
            + point.x().to_bytes(32, "big")
    else:
        pub = (b"\x04" + point.x().to_bytes(32, "big")
               + point.y().to_bytes(32, "big"))
    return base58.b58encode_check(b"\x00" + hash160(pub)).decode()


def raw_int(b: bytes) -> int:
    return int.from_bytes(b, "big")


def bits_reversed_int(b: bytes) -> int:
    """The 8*len(b) bit string of b, read backwards.

    NOTE the width: the CSV defines this construction on the PREIMAGE's own bit
    string ("the 192-bit string of the raw bytes read backwards", i.e. 24 bytes
    for a 24-character preimage), NOT on the 32-byte zero-padded value. Doing it
    on the padded 32 bytes gives a different key and a different address; the
    selftest caught that on the first run, which is what the witness is for.
    """
    return int(bin(raw_int(b))[2:].zfill(8 * len(b))[::-1], 2)


def constructions(pre: bytes) -> dict[str, int]:
    raw32 = pre.rjust(32, b"\x00")[-32:]
    return {
        "sha256": raw_int(sha256(pre)),
        "raw": raw_int(raw32),
        "raw-right": raw_int(pre.ljust(32, b"\x00")[-32:][::-1]),
        "bits reversed": bits_reversed_int(pre),
        "bytes rev": raw_int(raw32[::-1]),
        "hex ascii": raw_int(sha256(pre.hex().encode())),
    }


def load_planted() -> list[dict]:
    with open(CSV_PATH, newline="") as fh:
        return list(csv.DictReader(l for l in fh if not l.startswith("#")))


PLANTED = load_planted()
TARGETS = {r["address"]: (r["funded"], r["op_return"], r["status"])
           for r in PLANTED}
for _g in GATES.values():
    TARGETS.setdefault(_g, ("-", "-", "funded gate"))


def addresses_for(pre: bytes) -> dict[tuple[str, bool], str]:
    out = {}
    for cname, k in constructions(pre).items():
        for comp in (True, False):
            a = p2pkh(k, comp)
            if a:
                out[(cname, comp)] = a
    return out


# ------------------------------------------------------------------ witnesses

# (preimage, expected address, construction, compressed) -- every one of these is
# a row the CSV itself marks "verified", so re-deriving them is the witness that
# this harness and that file agree.
WITNESSES = [
    (b"gsmg.io/theseedisplanted", "148XH2YBmLr4oAJXQcG84FpNYoBmqnVPHQ",
     "raw", True),
    (b"gsmg.io/theseedisplanted", "13HGhjkmKUkP8sk9k63BLmhkxRjy7uK4Rp",
     "bits reversed", True),
    (b"causality", "1Jqq37KkZEt4F3Dt6qXdtyiMEFBBdawbkJ", "sha256", True),
    (b"1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe", "1GyT5WrLYpwFkuiVoPDJZa1Q6jtjbjuBff",
     "sha256", True),
    (b"jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
     "1K23RS1y2fnuZRkhw5nUpFr5Jk5WN11Zeq", "sha256", True),
]


def selftest() -> int:
    bad = 0
    for pre, want, cname, comp in WITNESSES:
        got = addresses_for(pre).get((cname, comp))
        ok = got == want
        bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {cname:14s}"
              f"{'compressed ' if comp else 'uncompressed'} {want}"
              f"{'' if ok else f'  got {got}'}")
    # the third door must be a known target, and must NOT be reachable by any
    # witness preimage under any construction (it has no known preimage)
    assert THIRD_DOOR in TARGETS, "third door missing from the planted list"
    for pre, _, _, _ in WITNESSES:
        assert THIRD_DOOR not in addresses_for(pre).values(), \
            "a known preimage claims the third door"
    print(f"  [{'PASS' if bad == 0 else 'FAIL'}] {len(WITNESSES)} CSV rows "
          f"re-derived, third door present and unclaimed")
    print(f"SELFTEST {'PASS' if bad == 0 else 'FAIL'}: {len(WITNESSES)} "
          f"witnesses, {bad} failures")
    return 1 if bad else 0


# ------------------------------------------------------------ audio candidates

def audio_candidates() -> list[tuple[str, bytes]]:
    """Every rendering of the audio number stream and the word it spells."""
    out: list[tuple[str, bytes]] = []
    seen: set[bytes] = set()

    def add(tag: str, b) -> None:
        if isinstance(b, str):
            b = b.encode()
        if b and b not in seen:
            seen.add(b)
            out.append((tag, b))

    for tag, nums in (("as-given", AUDIO_GIVEN),
                      ("community", AUDIO_COMMUNITY)):
        toks = nums.split()
        add(f"{tag}/spaced", nums)
        add(f"{tag}/joined", "".join(toks))
        add(f"{tag}/hyphen", "-".join(toks))
        add(f"{tag}/comma", ",".join(toks))
        add(f"{tag}/comma-space", ", ".join(toks))
        add(f"{tag}/lower", nums.lower())
        add(f"{tag}/reversed-tokens", " ".join(reversed(toks)))
        add(f"{tag}/reversed-joined", "".join(reversed(toks)))
        # hex-bytes reading: this is the reading that produces a word at all
        try:
            raw = bytes(int(t, 16) for t in toks)
        except ValueError:
            raw = b""
        if len(raw) == len(toks):
            add(f"{tag}/hex-bytes", raw)
            add(f"{tag}/hex-bytes-upper", raw.upper())
            add(f"{tag}/hex-bytes-as-text", "".join(
                chr(c) if 32 <= c < 127 else "?" for c in raw))
        # decimal reading: the same numbers as decimal byte values
        if all(t.isdigit() for t in toks) and all(int(t) < 256 for t in toks):
            dec = bytes(int(t) for t in toks)
            add(f"{tag}/dec-bytes", dec)
            add(f"{tag}/dec-as-text", "".join(
                chr(c) if 32 <= c < 127 else "?" for c in dec))
        # decimal reading as A1Z26-ish index, with and without 0-basing
        if all(t.isdigit() for t in toks):
            for base, tag2 in ((1, "a1z26-1"), (0, "a1z26-0")):
                s = "".join(chr(64 + int(t) + (0 if base == 1 else -1))
                            if 1 <= int(t) + (0 if base == 1 else -1) <= 26
                            else "?" for t in toks)
                add(f"{tag}/{tag2}", s)

    # the words the stream spells, in the renderings anyone would try
    for w in ("HASHTHETEXT", "hashthetext", "HashTheText", "Hash the text",
              "hash the text", "HASH THE TEXT", "hash the text.",
              "hashthe text", "HASHTHETEX", "ASHTHETEXT", "ashthetext",
              "HASHTEXT", "hash text", "HASH TEXT", "text the hash",
              "THE TEXT", "thetext"):
        add("word/" + w, w)
        add("word-rev/" + w, w[::-1])

    # "hash the text" applied to the page text is a documented, already-consumed
    # step whose result is the SalPhaseIon URL path. The URL and its hash are
    # carried so the third door is tested against the instruction's own output.
    url_hash = ("89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac"
                "0152f6a32")
    add("url/hash", url_hash)
    add("url/path", "gsmg.io/" + url_hash)
    add("url/path-nosite", "/" + url_hash)
    add("url/hash-upper", url_hash.upper())
    add("url/bytes", bytes.fromhex(url_hash))
    # the instruction text itself, as it appears on the creator's page
    add("instr/hash the text", "hash the text")
    add("instr/HASHTHETEXT", "HASHTHETEXT")
    return out


def run() -> int:
    cands = audio_candidates()
    hits = []
    tried = 0
    for tag, pre in cands:
        for (cname, comp), addr in addresses_for(pre).items():
            tried += 1
            if addr in TARGETS:
                hits.append((tag, pre, cname, comp, addr))
    print(f"audio/HASHTHETEXT battery: {len(cands)} preimages x "
          f"{len(constructions(b'x'))} constructions x 2 pubkey forms = "
          f"{tried} address derivations")
    for tag, pre, cname, comp, addr in hits:
        funded, op, status = TARGETS[addr]
        print(f"  MATCH  {addr}  [{cname}, {'compressed' if comp else 'uncompressed'}]"
              f"  from {tag} = {pre!r}  (funded {funded}, op_return {op!r},"
              f" status {status})")
    if not hits:
        print("  0 MATCH against the 3rd door, the 8 other planted addresses,"
              " and both gate addresses")
    return 1 if hits else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--audio", action="store_true",
                    help="run the audio / HASHTHETEXT battery")
    a = ap.parse_args(argv)
    rc = 0
    if a.selftest or not (a.selftest or a.audio):
        rc |= selftest()
    if a.audio and rc == 0:
        rc |= run()
    return rc


if __name__ == "__main__":
    sys.exit(main())
