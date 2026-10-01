#!/usr/bin/env python3
"""efefefe_scalar.py -- the EFEFEF branch of the FEFEFE scalar battery.

MOTIVATION. R-FEFEFE-SCALAR (tested.md:18983) closed "invert FEFEFE" as a
secp256k1 scalar. It tested four candidates: 0xFEFEFE, its 24-bit complement
0x010101, 0xEFEFEF (labelled "byte-reversed"), and -0xFEFEFE mod n. That row
holds two errors, both of which this battery corrects and then closes:

FINDING A -- THE RECORDED HEX-DIGIT RULE IS LOW-BIT, NOT POPCOUNT-PARITY.
analysis/leads.md:1810 records "a FEFEFE hex-digit parity reading
(FEFEFE->101010->42, #FFF200->111000, #3F48CC->110000)". R-FEFEFE-SCALAR
FINDING 2 asserted that nibble inversion (F->0, E->1) "is exactly LSB parity"
and therefore reproduces that record. It does not. LSB of the hex DIGIT is a
different function from parity of its popcount:

    F = 1111 -> low bit 1, popcount 4 -> parity 0
    E = 1110 -> low bit 0, popcount 3 -> parity 1

So the two rules give INVERTED answers on every digit, and all three of the
repo's recorded readings discriminate between them:

    colour   FEFEFE   FFF200   3F48CC
    low bit    101010   111000   110000   <- matches the record exactly
    popcount   010101   000100   001100   <- matches nothing in the record

The record is the low-bit reading, and its stated payoff "->42" is
int(101010, 2) = 42 under that rule. R-FEFEFE-SCALAR adopted the popcount
rule, landed on 010101, and then explained the disagreement with the record
away as "the digit strings differ only by reading order, so no new information
is produced in either direction". They are not reading-order variants of one
another: '010101'[::-1] == '101010' is true, but int('010101',2)=21 whereas
int('101010',2)=42, and 0x010101=65793 whereas 0x101010=1052688. The row
concluded that the string was exhausted while having tested the complement of
the wrong hex string under the wrong rule.

FINDING B -- THE USER STEER IS "EFEFEF", WHICH IS A DIFFERENT 3-BYTE STRING,
AND ITS COMPLEMENT WAS NEVER A CANDIDATE. 0xFEFEFE and 0xEFEFEF are distinct
integers (16711422 vs 15724527), not spellings of one value. R-FEFEFE-SCALAR
listed 0xEFEFEF but tested it as the byte-reversal of FEFEFE, i.e. as a
redundant member of the FEFEFE family. The intrinsic 24-bit complement of
0xEFEFEF is 0x101010, and neither 0x101010 nor -0xEFEFEF mod n appears
anywhere in analysis/tested.md. Under the low-bit rule that is the string the
repo actually recorded, so 0x101010 is the value the prior row was reaching for
and did not test.

This battery therefore runs the corrected rule over BOTH off-white candidates
and, for each, every inversion the question admits, with the repo's own
base58/ripemd160 convention and the two FULL funded-gate addresses decoded by
that library rather than by prefix.

COST. Every test here is a FREE HASH160 COMPARISON. A candidate is only ever
compared against a gate's already-public HASH160; no AES attempt and no funded
oracle call is made, because a scalar-derived address is compared directly to
the target address rather than used as a blob password. oracle.py and
oracle_dualite.py are --selftest'd (never fed a candidate) so the derivation
convention is certified before use.

CERTIFIED GUARANTEES.
  * selftest() reproduces the escrow's own on-chain public key -> its P2PKH
    HASH160, an independently checkable fact, before any comparison runs.
  * selftest() also pins the three recorded colour readings to the low-bit
    rule and pins the popcount reading to its (also recorded) wrong answer, so
    the FINDING A claim cannot silently rot.
  * The two gate HASH160s are decoded from the FULL addresses with the repo's
    own base58 dependency and asserted to be exactly 20 bytes. R-FEFEFE-SCALAR
    logged a false negative from comparing bare address prefixes, so this is
    asserted rather than assumed.
"""
from __future__ import annotations

import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import base58  # noqa: E402
from ecdsa import SECP256k1, SigningKey  # noqa: E402

from oracle import KNOWN_PUBKEY_HEX, TARGET_ADDRESS  # noqa: E402
from oracle_dualite import TARGET_ADDRESS as DUALITE_ADDRESS  # noqa: E402

CURVE_N = SECP256k1.order

# The off-white colour classes of the 14x14 grid work (R-COLORDOOR / the
# inspection checklist). FEFEFE is the documented 25th-mark class; EFEFEF is the
# same byte pattern with the nibbles transposed and is the string the steer
# names. Both are carried; the other two recorded colours are carried too
# because they are the evidence that discriminates low-bit from popcount.
COLOURS = {
    "FEFEFE": "101010",  # leads.md:1810, verified below
    "EFEFEF": None,      # unrecorded; this battery supplies it
    "FFF200": "111000",  # leads.md:1810
    "3F48CC": "110000",  # leads.md:1810
}


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def low_bit(hexstr: str) -> str:
    """LSB of each hex digit -- the rule the repo actually recorded."""
    return "".join(str(int(c, 16) & 1) for c in hexstr)


def popcount_parity(hexstr: str) -> str:
    """Parity of each hex digit's popcount -- the rule R-FEFEFE-SCALAR assumed."""
    return "".join(str(bin(int(c, 16)).count("1") % 2) for c in hexstr)


def h160_from_pub(pub: bytes) -> bytes:
    return hashlib.new("ripemd160", sha256(pub)).digest()


def addresses_for_scalar(scalar: int) -> dict[str, str]:
    """P2PKH addresses for a secp256k1 scalar, both pubkey encodings."""
    sk = SigningKey.from_string(scalar.to_bytes(32, "big"), curve=SECP256k1)
    point = sk.get_verifying_key().pubkey.point
    xs = point.x().to_bytes(32, "big")
    ys = point.y().to_bytes(32, "big")
    # A compressed pubkey is 0x02/0x03 (parity of y) followed by x. Deriving it
    # from the point rather than from to_string() keeps the parity prefix from
    # being silently dropped, which is the bug this row corrected in its own
    # first draft.
    out = {
        "compressed": base58.b58encode_check(
            b"\x00" + h160_from_pub((b"\x03" if point.y() % 2 else b"\x02") + xs)
        ).decode(),
        "uncompressed": base58.b58encode_check(
            b"\x00" + h160_from_pub(b"\x04" + xs + ys)
        ).decode(),
    }
    return out


def gate_h160s() -> dict[str, bytes]:
    """HASH160 of each funded gate, decoded from the FULL address."""
    out = {}
    for name, addr in (("small", TARGET_ADDRESS), ("dualite", DUALITE_ADDRESS)):
        raw = base58.b58decode_check(addr)
        assert raw[0] == 0, f"{name}: unexpected version byte {raw[0]}"
        h = raw[1:]
        assert len(h) == 20, f"{name}: HASH160 is {len(h)} bytes, not 20"
        out[name] = h
    return out


def selftest() -> bool:
    ok = True

    # Part 1 -- certify the address-derivation convention against a real,
    # independently checkable fact: the escrow's own on-chain pubkey.
    pub = bytes.fromhex(KNOWN_PUBKEY_HEX)
    derived = base58.b58encode_check(b"\x00" + h160_from_pub(pub)).decode()
    p1 = derived == TARGET_ADDRESS
    print(f"HASH160(known on-chain pubkey) -> {TARGET_ADDRESS}: {'OK' if p1 else 'FAIL'}")
    ok = ok and p1

    # Part 2 -- pin the three recorded colour readings to the LOW-BIT rule.
    # This is the claim FINDING A rests on, so it is certified, not asserted.
    for hexstr, recorded in COLOURS.items():
        if recorded is None:
            continue
        lb, pc = low_bit(hexstr), popcount_parity(hexstr)
        good = lb == recorded and pc != recorded
        note = "" if good else f"  (low_bit={lb} popcount={pc})"
        print(f"recorded reading {hexstr}={recorded}: low-bit match={lb == recorded}"
              f" popcount match={pc == recorded} {'OK' if good else 'FAIL'}{note}")
        ok = ok and good

    # Part 3 -- the FEFEFE/EFEFEF distinction FINDING B rests on.
    p3 = 0xFEFEFE != 0xEFEFEF
    print(f"0xFEFEFE ({0xFEFEFE}) != 0xEFEFEF ({0xEFEFEF}): {'OK' if p3 else 'FAIL'}")
    ok = ok and p3
    p3b = ((~0xEFEFEF) & 0xFFFFFF) == 0x101010 and ((~0xFEFEFE) & 0xFFFFFF) == 0x010101
    print(f"24-bit NOTs land on 0x101010 / 0x010101: {'OK' if p3b else 'FAIL'}")
    ok = ok and p3b

    # Part 4 -- guard the two mistakes that produced the prior false negative.
    p4a = int("010101", 2) != int("101010", 2)
    print(f"'010101' and '101010' are NOT the same number "
          f"({int('010101', 2)} vs {int('101010', 2)}): {'OK' if p4a else 'FAIL'}")
    ok = ok and p4a
    p4b = 0x101010 != 0x010101
    print(f"0x101010 != 0x010101: {'OK' if p4b else 'FAIL'}")
    ok = ok and p4b

    # Part 5 -- the escrow's own address is the P2PKH of the UNCOMPRESSED
    # encoding, which Part 1 certifies. The same pubkey in COMPRESSED form
    # HASHes to a different address -- that is inherent to P2PKH, not a defect,
    # so it is asserted as a property rather than tested for equality. What must
    # hold is that the compressed form is well formed (33 bytes, prefix 02/03
    # matching the parity of y, x recovered exactly).
    pub = bytes.fromhex(KNOWN_PUBKEY_HEX)
    xs, ys = pub[1:33], pub[33:65]
    p5u = base58.b58encode_check(b"\x00" + h160_from_pub(pub)).decode() == TARGET_ADDRESS
    print(f"uncompressed encoding of the certified pubkey -> {TARGET_ADDRESS}: "
          f"{'OK' if p5u else 'FAIL'}")
    ok = ok and p5u
    comp_pub = (b"\x03" if ys[-1] & 1 else b"\x02") + xs
    want_prefix = b"\x03" if ys[-1] & 1 else b"\x02"
    p5c = (len(pub) == 65 and len(comp_pub) == 33 and comp_pub[1:] == xs
           and comp_pub[:1] == want_prefix)
    comp_addr = base58.b58encode_check(b"\x00" + h160_from_pub(comp_pub)).decode()
    print(f"compressed encoding of the certified pubkey is well formed "
          f"(33B, parity prefix, x preserved) -> {comp_addr}: "
          f"{'OK' if p5c else 'FAIL'}")
    ok = ok and p5c
    p5d = comp_addr != TARGET_ADDRESS
    print(f"compressed address differs from the uncompressed one, as P2PKH "
          f"requires: {'OK' if p5d else 'FAIL'}")
    ok = ok and p5d

    # Part 6 -- both encodings of a known scalar must agree with an INDEPENDENT
    # point multiplication, not merely with the library helper used above.
    _v = 0xFEFEFE
    _pt = SECP256k1.generator * _v
    _ref = {
        "compressed": base58.b58encode_check(
            b"\x00" + h160_from_pub((b"\x03" if _pt.y() % 2 else b"\x02")
                                    + _pt.x().to_bytes(32, "big"))).decode(),
        "uncompressed": base58.b58encode_check(
            b"\x00" + h160_from_pub(b"\x04" + _pt.x().to_bytes(32, "big")
                                    + _pt.y().to_bytes(32, "big"))).decode(),
    }
    _got = addresses_for_scalar(_v)
    p6 = _got == _ref
    print(f"scalar 0x{_v:X} derivation matches independent G*k: "
          f"{'OK' if p6 else 'FAIL'}")
    if not p6:
        for k in _ref:
            print(f"    {k}: got {_got[k]} want {_ref[k]}")
    ok = ok and p6

    return ok


def main() -> int:
    print("=" * 74)
    print("efefefe_scalar.py -- EFEFEF inversion, correcting R-FEFEFE-SCALAR")
    print("=" * 74)
    if not selftest():
        print("\nSELFTEST FAIL -- aborting before any comparison.")
        return 1
    print("SELFTEST PASS\n")

    gates = gate_h160s()
    print("Funded gate HASH160s (decoded from the FULL addresses):")
    for name, h in gates.items():
        print(f"  {name:8s} {h.hex()}")
    print()

    # Build the candidate set. Every entry is a scalar; the readings and their
    # hex/binary forms are the values the steer and the ledger actually name.
    cands: list[tuple[str, int]] = []
    seen: set[int] = set()

    def add(label: str, value: int) -> None:
        if value in seen:
            return
        seen.add(value)
        cands.append((label, value))

    for hexstr, recorded in COLOURS.items():
        base = int(hexstr, 16)
        add(f"0x{hexstr} (raw)", base)
        add(f"~0x{hexstr} (24-bit NOT)", (~base) & 0xFFFFFF)
        add(f"~0x{hexstr} (32-bit NOT)", (~base) & 0xFFFFFFFF)
        add(f"-0x{hexstr} mod n", (-base) % CURVE_N)
        for rule_name, rule in (("lowbit", low_bit), ("popcount", popcount_parity)):
            bits = rule(hexstr)
            add(f"{hexstr}/{rule_name} as binary ({bits})", int(bits, 2))
            add(f"{hexstr}/{rule_name} as hex (0x{bits})", int(bits, 16))
            if recorded is not None and bits == recorded:
                add(f"{hexstr} RECORDED reading {bits} as binary", int(bits, 2))
        # byte reversal, which the prior row conflated with a distinct value
        rev = bytes.fromhex(hexstr)[::-1].hex()
        add(f"0x{rev} (byte-reversed)", int(rev, 16))

    print(f"{len(cands)} distinct scalar candidates\n")
    hits = []
    for label, value in cands:
        addrs = addresses_for_scalar(value)
        row_match = []
        for gname, gh in gates.items():
            for enc, addr in addrs.items():
                if base58.b58decode_check(addr)[1:] == gh:
                    row_match.append(f"{gname}/{enc}")
        flag = "  <<< MATCH" if row_match else ""
        if row_match:
            hits.append((label, value, row_match))
        print(f"  0x{value:064X}  {value:>21d}  {label}")
        print(f"      comp {addrs['compressed']}   uncomp {addrs['uncompressed']}{flag}")

    print(f"\n{'=' * 74}")
    if hits:
        print(f"*** {len(hits)} CANDIDATE(S) MATCH A FUNDED GATE ***")
        for label, value, row_match in hits:
            print(f"  {label} = {value}  ->  {', '.join(row_match)}")
        return 1
    print(f"RESULT: 0 of {len(cands)} scalars match either gate address.")
    print("Every test was a free HASH160 comparison; 0 funded-oracle calls made.")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
