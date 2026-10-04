#!/usr/bin/env python3
"""thirddoor_yinyang_sweep.py -- the Architect's-choice / yin-yang family against
EVERY creator-planted address, via the certified third-door harness.

WHY THIS TOOL EXISTS. Two threads were closed for the funded AES gates but were
never run against the planted-address oracle:

  1. The yin-yang thread. `analysis/tested.md:12123` fixes its status as
     "author-confirmed but unfound, a possible yinyang path that bypasses `ca`",
     and `R-DOORGlyph` FINDING 4 establishes that the author's ONLY portal word
     is "door", used six times and never enumerated -- so "second door" is a
     linguistic thread, not a numbered address. `R-YINYANG-MARKER` then resolves
     the authored yin-yang POSITIVE as the `aBa` polarity bracket, i.e. *the
     architect's choice*.
  2. The 2023-02-23 creator binary `#8446`. It decodes (witnessed below) to the
     author's own instruction phrase, which contains the segment
     `...lastwordsbeforearchichoiceyinyangwewontgiveaway...`.

Both are authorial, both are certified negative at the two funded gates, and a
grep of every third-door row in `analysis/tested.md` returns ZERO rows mentioning
"architect". The gates and the third door are different oracles; a gate negative
does not transfer. `README.md` records that the creator named the third door in
December 2020 as one of the two addresses to check findings against instead of
hitting the server, which is exactly a findings oracle -- so the family belongs
here.

WHAT IS ACTUALLY NEW, AND WHAT IS NOT. Nothing here re-runs a gate row: the
phrase and its segments were swept at the gates by `late-320`'s 53-candidate
differential battery and `tested.md:3809`, and the whole Architect two-doors
scene was swept by `tools/architect_twodoors_sweep.py` (N=2232, row at
`tested.md:9138-9140`). This file reuses that vocabulary against a different,
untouched target set.

The `bits reversed` construction in `third_door.py` is not incidental here: the
`#8446` blob is 161 bytes in which EVERY byte is even, so its low bit is always
0, and reversing the 1288-bit string lands those zeros on the high bit of each
output byte -- that is why the reading is printable ASCII at all. The blob is
therefore the strongest available example of the creator's own key-construction
idiom, and it is submitted here in four byte-forms plus its own hex/base64
renderings.

Local only. Every address compared is already public in
`data/planted-addresses.csv` or the README gate table. No key is swept, no
transaction is built, nothing is broadcast.
"""
import base64
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import third_door as td  # noqa: E402

# The creator's own 2023-02-23 message #8446, 161 octets, lifted verbatim from
# GSMG_JRK.md. Held as bits so the byte count is re-derivable, not asserted.
BLOB_BITS = (
    "00100110 10100110 11001110 10010110 10110110 11110110 01001110 00001110"
    " 10011110 10000110 11101110 10000110 10100110 01101110 10010110 11100110"
    " 10100110 10101110 01001110 00101110 10000110 11001110 10010110 00001110"
    " 10100110 00101110 11001110 00101110 11001110 10000110 00110110 10011110"
    " 01001110 10100110 01101110 00101110 10010110 11100110 01110110 10010110"
    " 10100110 10100110 11001110 00101110 11110110 01110110 10100110 01001110"
    " 10101110 11110110 10011110 00101110 10101110 01000110 11001110 10100110"
    " 10011110 10100110 01001110 10101110 11110110 10011110 01100110 11110110"
    " 00101110 01110110 11110110 01001110 01100110 01110110 10010110 11001110"
    " 00101110 10010110 00100110 01001110 11110110 11101110 11001110 11001110"
    " 10000110 00001110 10100110 00010110 00101110 10011110 10000110 11101110"
    " 10000110 10100110 01101110 10010110 11100110 00101110 01110110 11110110"
    " 11101110 10100110 11101110 11100110 01110110 10000110 10011110 01110110"
    " 10010110 10011110 10100110 11000110 10010110 11110110 00010110 11000110"
    " 10010110 00010110 11000110 01001110 10000110 10100110 01001110 11110110"
    " 01100110 10100110 01000110 11001110 00100110 01001110 11110110 11101110"
    " 00101110 11001110 10000110 00110110 00101110 11001110 10010110 00110110"
    " 10110110 10101110 11001110 00011110 10010110 01001110 00101110 10000110"
    " 10110110 11001110 10100110 10110110 10010110 01001110 00001110 10100110"
    " 10101110 00110110 01000110 11101110 11110110 00110110 00110110 10100110"
    " 10011110"
)
BLOB = bytes(int(b, 2) for b in BLOB_BITS.split())
PHRASE = (
    b"yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang"
    b"wewontgiveawaythepassworditsinfrontofyoureyesbutyourenotseeingit"
    b"verylaststepisatruegiveawaypromised"
)


def blob_selftest() -> int:
    """Re-derive the #8446 reading from the bits, and prove the harness works.

    Two independent witnesses:
      W1  the bit-reversal of the 161 octets reproduces the documented phrase
          byte-exactly, and the phrase is 161 chars -- which is also the ledger
          correction: `tested.md:11666` records "1280 bits / 160 bytes", but
          161 octets is 1288 bits and the phrase is 161 characters. There is no
          leftover byte; the "160" was a typo.
      W2  a known-good planted row is re-found through `td.addresses_for`, so a
          NO MATCH from this harness means the same thing the CSV's `verified`
          rows mean.
    """
    ok = True

    bits = "".join(format(v, "08b") for v in BLOB)
    got = bytes(int(bits[::-1][i:i + 8], 2) for i in range(0, len(bits), 8))
    if got == PHRASE:
        print(f"  [PASS] W1 #8446 bit-reversal re-decodes byte-exactly "
              f"({len(BLOB)} octets / {len(bits)} bits -> {len(PHRASE)} chars)")
    else:
        ok = False
        print("  [FAIL] W1 #8446 decode did not reproduce the phrase")
    if len(BLOB) == 161 and len(bits) == 1288 and len(PHRASE) == 161:
        print("  [PASS] W1b 161 octets / 1288 bits / 161 chars all agree "
              "(contradicts tested.md:11666's '160 bytes')")
    else:
        ok = False
        print(f"  [FAIL] W1b counts disagree: {len(BLOB)}/{len(bits)}/{len(PHRASE)}")
    if all(v % 2 == 0 for v in BLOB):
        print(f"  [PASS] W1c every octet even, {len(set(BLOB))} distinct values")
    else:
        ok = False
        print("  [FAIL] W1c evenness property broken")

    for pre, want, cname, comp in td.WITNESSES:
        if td.addresses_for(pre).get((cname, comp)) == want:
            print(f"  [PASS] W2 {cname:<14} {'compressed' if comp else 'uncompressed'}  {want}")
        else:
            ok = False
            print(f"  [FAIL] W2 {cname} {pre!r} did not re-find {want}")
    return 0 if ok else 1


def blob_forms() -> list[tuple[str, bytes]]:
    """The #8446 blob itself, in the byte-forms a preimage could plausibly take."""
    f = [
        ("blob raw 161", BLOB),
        ("blob bits-reversed (= the phrase)", PHRASE),
        ("blob first 160", BLOB[:160]),
        ("blob last 160", BLOB[-160:]),
        ("blob hex ascii", BLOB.hex().encode()),
        ("blob base64", base64.b64encode(BLOB)),
    ]
    return f


def literals() -> list[str]:
    """Authorial yinyang / Architect's-choice vocabulary, case+join variants."""
    seeds = [
        # the phrase and its documented prefixes / segments
        PHRASE.decode(),
        "yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang",
        "yellowblueprimesmatrixsumlist",
        "matrixsumlist", "lastwordsbefore", "lastwordsbeforearchichoice",
        "archichoice", "thearchitectchoice", "thearchitectschoice",
        "archi", "choice", "thearchitect", "architect", "arch",
        "yinyang", "yingyang",
        "yinyangwewontgiveawaythepassworditsinfrontofyoureyesbutyourenotseeingit",
        "verylaststepisatruegiveawaypromised", "isatruegiveawaypromised",
        "wontgiveawaythepassworditsinfrontofyoureyes",
        "lastwords", "lastword", "yourlastcommand",
        # the authored polarity bracket itself (R-YINYANG-MARKER's `aBa`)
        "aBa", "aba", "AB A", "aBab",
        # the {1},{4},{21} door hint with the author-confirmed R=18 A=1 B=2
        "12421", "1421", "21421", "1,4,21", "{1}{4}{21}", "214", "421",
        "1812", "211812", "181221", "r18a1b2", "18a1b2", "rab2",
        "2121", "124", "4121",
    ]
    out = []
    for s in seeds:
        for v in {s, s.upper(), s.lower(), s.replace(" ", ""),
                  s.replace(" ", "").upper(), s.replace(" ", "").lower()}:
            if v:
                out.append(v)
    return out


def main() -> int:
    if "--selftest" in sys.argv:
        return blob_selftest()

    cands: list[tuple[str, bytes]] = []
    seen = set()
    for tag, pre in blob_forms():
        if pre and pre not in seen:
            seen.add(pre)
            cands.append((tag, pre))
    for s in literals():
        b = s.encode()
        if b not in seen:
            seen.add(b)
            cands.append((f"lit:{s[:48]}", b))

    n_der = 0
    matches = []
    for tag, pre in cands:
        for (cname, comp), addr in td.addresses_for(pre).items():
            n_der += 1
            if addr in td.TARGETS:
                matches.append((tag, pre, cname, comp, addr))

    print(f"candidates: {len(cands)}  derivations: {n_der}  "
          f"targets: {len(td.TARGETS)}")
    print(f"rate assumption D ~ 1117 addr/s -> ~{n_der/1117:.3f} s of work")
    if matches:
        print("*** MATCH ***")
        for tag, pre, cname, comp, addr in matches:
            print(f"  {addr}  {cname} {'compressed' if comp else 'uncompressed'}  {tag}")
        return 0
    print("NO MATCH on any planted address or gate")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
