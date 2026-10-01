#!/usr/bin/env python3
"""third_door_yellowblue.py -- the audio hint's own instruction ("hash the text")
applied to the certified yellow/blue-primes material, against the third door.

WHY THIS TOOL EXISTS. The creator's surviving third-door sentence is "a rule the
creator gave between the January 2020 poem and the April 2020 audio hint
('Yellow has a number and so does Blue', 'primes', 'zeroed out') read on a
non-textual object". Two of the three named inputs have now been certified
against the third door:

  * `third_door.py --audio` (R-THIRDDOOR-AUDIO-2026-09-28): HASHTHETEXT and all
    its renderings + the documented output of the instruction (the SalPhaseIon
    URL hash `89727c59...`). 720 derivations, 0 MATCH.
  * `third_door_colors.py --colors` (R-COLORDOOR-2026-09-28): the per-tile
    colour runs of the SalPhaseIon bands and the sticker strip under the
    counts/primes/zeroed/indices/cmap/pairs rules. 4,326 derivations, 0 MATCH.

THE GAP THIS TOOL CLOSES. The third named input -- the *numbers* of the phase-1
14x14 matrix ("Yellow has a number and so does Blue") -- has been read against
the third door ONLY in the mask/count forms that section 19b ran before the
color-prime was even established. The certified color-prime scalar itself
(0x08c26d = 574061, PRIME), the sum-of-primes pair 17 / 41 (the -41/-17
Decentraland coordinates), the colour word, its bit string, its run-lengths, and
the hint SENTENCE were all carried to both gate addresses by late-308 (16
candidates x 2 gates = 32 oracle attempts, 0 hits) but were never fed to the
third door. And the audio hint is an INSTRUCTION ("hash the text"), so the whole
family is naturally evaluated by the six keyed constructions of `third_door`
(in particular `sha256` and `hex ascii`), which is exactly this tool's harness.

WHAT IS *NOT* REOPENED. No ledger row is re-run: the 9/15 pair-spellings that
`third_door_colors.matrix_candidates()` already carried to the third door are
NOT repeated here (they are listed below as excluded). This tool adds only the
certified color-prime material and the hint sentence, in the forms that only
ever reached the funded gates.

THE PREIMAGE FAMILY (every string sourced from the certified constants of
tools/colorprime_matrix_battery.py -- selftest-pinned -- or typed from the
ledger's own quote of the author's hint):

  prime    574061, 0x08c26d, 08c26d, 8c26d, 0x8c26d, '574061' hex/dec joins
  primesum 17, 41, '17 41', '17-41', '17,41', '1741', '4117', '-17-41',
           '-41,-17', '1741f' joins, sum(primes<9)=17 sum(primes<15)=41 text
  word     BBBBYBBBYYBBBBYBBYYBYYBY (and reversed)
  bits     Y_BITS 000010001100001001101101 (and reversed, and int/hex again)
  runs     RLE 413241221211 + per-colour 121221 / 434211 + reversed joins
  ones     1-based Y_ONES 5,9,10,15,18,19,21,22,24 (+0-based) in 4 joins
  numbers  9, 15, '9 15', '9,15', '15 9' numbers the colours HAVE
  hint     the hint sentence verbatim + the 2020-01-14 poem line + "primes" +
           "zeroed out" and the roadmap token yellowblueprimes

Every candidate goes through all six constructions of `third_door.constructions`
in both pubkey forms, compared against the third door, the 8 other planted
addresses and both gate addresses (the same target set as `third_door`).

WITNESS. `third_door.selftest()` (5 CSV rows re-derived) must pass rc=0 before
and after the battery, and the audio family's two documented outputs
(`89727c59...` and `HASHTHETEXT`, reaching zero targets by design) plus the 5
CSV control preimages are pushed through THIS loop in-process, so the candidate
path itself -- not just the imported functions -- is witnessed.

Local only. All addresses compared are already public in
`data/planted-addresses.csv` or the README gate table. Nothing is broadcast.
"""
from __future__ import annotations

import argparse
import sys
import time

import third_door as TD
from colorprime_matrix_battery import COLOR_WORD, Y_BITS

RUN_LENS = [4, 1, 3, 2, 4, 1, 2, 2, 1, 2, 1, 1]
Y_ONES_1 = [5, 9, 10, 15, 18, 19, 21, 22, 24]   # 1-based, certified spiral
BLUE = 15
YELLOW = 9
PRIME = 574061                                   # int(Y_BITS, 2)
HINT = "Yellow has a number and so does Blue"
POEM = "Roses are White but often Red. Yellow has a number and so does Blue."

# the 9/15 spellings that third_door_colors already carried to the third door;
# excluded here so no ledger row is re-run. Kept for the record only.
_EXCLUDED_915 = {"9 15", "915", "15 9", "159", "9,15", "15,9",
                 "yellow9blue15", "yellow9andblue15",
                 "blue15andyellow9", "yellow has 9 and blue has 15",
                 "yellow9 blue15", "yellow_9_blue_15", "9and15", "9 and 15"}


def _add(out: list[tuple[str, bytes]], seen: set[bytes], tag: str, v) -> None:
    if isinstance(v, int):
        v = str(v)
    if isinstance(v, str):
        v = v.encode()
    if not v or v in seen:
        return
    seen.add(v)
    out.append((tag, v))


def candidates() -> list[tuple[str, bytes]]:
    out: list[tuple[str, bytes]] = []
    seen: set[bytes] = set()
    hexprime = format(PRIME, "x")              # 8c26d
    zbits = Y_BITS.split("0")
    # "0x" forms and their spacings
    for tag, v in (
        ("prime/dec", PRIME),
        ("prime/hex-0x", "0x" + hexprime),
        ("prime/hex-0x-pad6", "0x" + hexprime.zfill(6)),
        ("prime/hex", hexprime),
        ("prime/hex-pad6", hexprime.zfill(6)),
    ):
        if v is not None:
            _add(out, seen, tag, v)
    # sum(primes < 9) = 17 and sum(primes < 15) = 41, in every obvious join
    for tag, v in (
        ("primesum/17", 17),
        ("primesum/41", 41),
        ("primesum/17-41", "17 41"),
        ("primesum/17-41-dash", "17-41"),
        ("primesum/17-41-comma", "17,41"),
        ("primesum/1741", "1741"),
        ("primesum/4117", "4117"),
        ("primesum/neg-dash", "-17-41"),
        ("primesum/neg-comma", "-41,-17"),
        ("primesum/1741-primehex", "1741" + hexprime),
        ("primesum/dec-coords", "(-41,-17)"),
        ("primesum/sums-sentence",
         "sum of primes less than nine is seventeen and less than fifteen"
         " is forty one"),
    ):
        _add(out, seen, tag, v)
    # the colour word and bit string and runs, all readings
    for tag, v in (
        ("word/fwd", COLOR_WORD),
        ("word/rev", COLOR_WORD[::-1]),
        ("bits/fwd", Y_BITS),
        ("bits/rev", Y_BITS[::-1]),
        ("bits/ones-1based-join", "".join(map(str, Y_ONES_1))),
        ("bits/ones-1based-comma", ",".join(map(str, Y_ONES_1))),
        ("bits/ones-1based-space", " ".join(map(str, Y_ONES_1))),
        ("bits/ones-1based-dash", "-".join(map(str, Y_ONES_1))),
        ("bits/ones-0based-join",
         "".join(str(o - 1) for o in Y_ONES_1)),
        ("runs/join", "".join(map(str, RUN_LENS))),
        ("runs/rev", "".join(map(str, RUN_LENS[::-1]))),
        ("runs/dash", "-".join(map(str, RUN_LENS))),
        ("runs/per-colour-yellow", "121221"),
        ("runs/per-colour-blue", "434211"),
        ("runs/per-colour-yellow-rev", "122121"),
        ("runs/per-colour-blue-rev", "112434"),
    ):
        _add(out, seen, tag, v)
    # the numbers each colour HAS: 9 and 15. Third_door_colors already ran the
    # 9/15 SPELLING family on the third door; only the two bare scalars have not
    # been carried as third-door preimages (late-308 carried them to the gates).
    for tag, v in (("numbers/yellow", YELLOW), ("numbers/blue", BLUE)):
        _add(out, seen, tag, v)
    # the hint sentence itself, the poem line, and the two other quoted rules
    for tag, v in (
        ("hint/sentence", HINT),
        ("hint/poem", POEM),
        ("hint/poem-go-back",
         POEM + " Go back to the first puzzle piece"),
        ("hint/primes", "primes"),
        ("hint/prime-number", "prime number"),
        ("hint/zeroed-out", "zeroed out"),
        ("hint/some-characters", "some characters need to be zeroed out"),
        ("hint/roadmap-token", "yellowblueprimes"),
        ("hint/roadmap-token-spaced", "yellow blue primes"),
    ):
        _add(out, seen, tag, v)
    # the audio-instruction interpretation applied to the scalars: "hash the
    # text" is the instruction, and each scalar IS text under the six
    # constructions' `sha256`/`hex ascii` readings. Two explicit digest forms
    # close the loop so the instruction is testable as an output, not just a
    # construction.
    for scalar, name in ((PRIME, "574061"), (17, "17"), (41, "41"),
                         (BLUE, "15"), (YELLOW, "9")):
        _add(out, seen, f"hash-text/{name}", TD.sha256(str(scalar).encode()))
        _add(out, seen, f"hash-text-hex/{name}",
             TD.sha256(str(scalar).encode()).hex())
    return out


AUDIO_URL = ("89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac"
             "0152f6a32")


def control_candidates() -> list[tuple[str, bytes]]:
    """The 5 CSV POSITIVE control preimages (each must re-find a target
    address), plus the two audio-instruction outputs as NEGATIVE controls
    (R-THIRDDOOR-AUDIO documented them as reaching zero targets by design, so
    each must stay unmatched)."""
    out: list[tuple[str, bytes]] = []
    seen: set[bytes] = set()
    for w in TD.WITNESSES:
        _add(out, seen, f"control/{w[0].decode()[:24]}", w[0])
    _add(out, seen, "negative/url-hash", AUDIO_URL)
    _add(out, seen, "negative/HASHTHETEXT", b"HASHTHETEXT")
    return out


def run() -> tuple[int, int, list, bool]:
    t0 = time.time()
    pool = control_candidates() + candidates()
    ctl = control_candidates()
    hits: list = []
    tried = 0
    for tag, pre in pool:
        for (cname, comp), addr in TD.addresses_for(pre).items():
            tried += 1
            if addr in TD.TARGETS:
                hits.append((tag, pre, cname, comp, addr))
    dt = time.time() - t0
    ctl_found = {h[1] for h in hits if h[0].startswith("control/")}
    pos = {p for t, p in ctl if t.startswith("control/")}
    neg = [p for t, p in ctl if t.startswith("negative/")]
    neg_hit = {h[1] for h in hits if h[0].startswith("negative/")}
    ctl_hits = {h[1] for h in hits if h[0].startswith("control/")}
    real = [h for h in hits if not h[0].startswith("control/")
            and not h[0].startswith("negative/")]
    ok = True
    if ctl_found != pos:
        missing = sorted(p[:24] for p in pos - ctl_found)
        print(f"  WITNESS FAILED: {len(ctl_found)}/{len(pos)} distinct "
              f"control preimages re-found; missing {missing}")
        ok = False
    if neg_hit:
        print(f"  WITNESS FAILED: {len(neg_hit)} negative control(s) "
              f"matched: {[h[1][:24] for h in hits if h[0].startswith('negative/')]}")
        ok = False
    ncand = len(cand := candidates())
    ctrl_n = len(ctl)
    ncand_derive = sum(1 for tag, pre in pool if not
                       tag.startswith(("control/", "negative/")) for _a in TD.addresses_for(pre))
    print(f"controls: {len(ctl_hits)}/{len(pos)} distinct preimages claim "
          f"target addresses ({len(ctl_hits)} of {len(ctl)} control rows, "
          f"incl. both theseedisplanted constructions); negatives unmatched: "
          f"{not neg_hit}")
    print(f"yellow/blue-primes battery: {ncand} preimages x 6 constructions "
          f"x 2 pubkey forms = {ncand_derive} address derivations "
          f"in {dt:.1f}s")
    for tag, pre, cname, comp, addr in real:
        funded, op, status = TD.TARGETS[addr]
        print(f"  MATCH  {addr}  [{cname}, "
              f"{'compressed' if comp else 'uncompressed'}]  from {tag} = "
              f"{pre!r}  (funded {funded}, op_return {op!r}, status {status})")
    if not real:
        print("  0 MATCH on the third door, the 8 other planted addresses and"
              " both gate addresses")
    return ncand, tried, len(real), ok


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--yellowblue", action="store_true",
                    help="run the yellow/blue-primes battery against the "
                         "third door")
    a = ap.parse_args(argv)
    rc = 0
    if a.selftest or not (a.selftest or a.yellowblue):
        print("== third_door.selftest ==")
        rc |= TD.selftest()
        print("== this tool's witness loop ==")
        ncand, _tried, _hits, ok = run()
        if not ok:
            print("SELFTEST FAIL: witness loop did not re-find the controls")
            return 1
        print(f"SELFTEST PASS: 5 CSV rows + audio outputs through this loop, "
              f"{ncand} non-control candidates carried")
    if a.yellowblue and rc == 0:
        print("== third_door.selftest (pre) ==")
        rc |= TD.selftest()
        _ncand, _tried, nhits, ok = run()
        print("== third_door.selftest (post) ==")
        rc |= TD.selftest()
        if not ok:
            rc |= 1
        if nhits:
            rc |= 1
    return rc


if __name__ == "__main__":
    sys.exit(main())