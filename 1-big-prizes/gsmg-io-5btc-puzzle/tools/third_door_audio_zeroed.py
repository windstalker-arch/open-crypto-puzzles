#!/usr/bin/env python3
"""third_door_audio_zeroed.py -- the creator's "some characters need to be zeroed
out" applied to the AUDIO NUMBER STREAM, against the third door.

WHY THIS TOOL EXISTS, AND WHY IT IS A SMALL ONE. The creator's surviving
third-door sentence names three inputs: "Yellow has a number and so does Blue",
"primes", "zeroed out", read on a non-textual object. All three have now been
carried to the third door separately, and this file covers the one composition
the ledger never had:

  * `third_door.py --audio` (R-THIRDDOOR-AUDIO-2026-09-28): the audio stream
    `18 41 53 48 54 48 45 54 45 58 54` and the community's `48 ...` rendering,
    all spellings, the instruction's documented output. 720 derivations, 0 MATCH.
    NOTE: that battery NEVER applies a zeroing rule -- it only renders the
    stream as given.
  * `third_door_colors.py --colors` (R-COLORDOOR-2026-09-28): the primes and
    zeroed-out rules applied to the colour RUNS of the pixel artifacts
    (non-prime ranks -> '0' or NUL, prime ranks -> '0' or NUL, both basings).
  * `third_door_yellowblue.py --yellowblue` (R-YELLOWBLUE-HASH-2026-09-30): the
    certified scalars 574061 / 17 / 41 and the hint sentence. 628 derivations.

So the zeroing rule has a certified definition (from third_door_colors) and a
certified carrier (the audio stream, from third_door), and the two were never
applied to each other. That is a genuine composition gap, and it is a cheap one:
the stream is 11 tokens, so the whole space is a few hundred candidates.

WHAT IS *NOT* REOPENED. No ledger row is re-run. The untransformed stream
spellings stay closed by R-THIRDDOOR-AUDIO and are NOT repeated here except as
this tool's own negative controls. The colour-run readings stay closed by
R-COLORDOOR. This file adds only the composition.

THE HONEST CAVEAT, STATED IN THE LEDGER ROW TOO. `late-92` certified that
`puzzlepiece.mp3` carries NO painted glyphs at any spectrogram resolution, so
this number stream is a community TRANSCRIPTION, not a measurement. "Some
characters need to be zeroed out" therefore has no ground truth to zero
*against* -- we cannot tell which characters the creator meant, only that a
zeroing was announced. That is a reason this row is weak evidence either way,
and it is why the result is reported as a formality rather than as a
constraint on the puzzle. What the row CAN establish is that the announced rule
does not open the third door in any of its mechanical readings.

THE RULES (each from the corpus, not invented here):

  primes     the tokens at prime ranks; keep-only, drop-only, both basings.
             (`third_door_colors`: "the tiles at prime ranks, and their
             complement"; and tested.md:8994 rule (a) on the digit streams.)
  zeroed     the creator's literal words: replace a rank with '0' or NUL.
             Both polarities -- non-prime ranks zeroed, and prime ranks zeroed
             -- because the colors tool carries both and the hint does not say
             which side was zeroed. Both basings.
  yb         "Yellow has a number and so does Blue" with the established
             Yellow=9 / Blue=15 (phase-1 matrix counts, leads note 22) as a
             POSITION rule: ranks that are multiples of 9 or 15 are zeroed or
             dropped, in each colour's channel and both together.
             (tested.md:8994 rules (b)(c)(d).)

Each resulting token list is then rendered the way `third_door.audio_candidates`
renders a stream -- spaced / joined / hyphen / comma / comma-space, the hex-byte
reading (the reading that produces a word), the decimal-byte reading, and A1Z26
at 1- and 0-basing -- so that a zeroed stream is compared exactly the way an
unzeroed one would be.

WITNESS. `third_door.selftest()` (5 CSV rows re-derived) must pass rc=0 before
AND after. This tool's own loop additionally pushes the 5 CSV POSITIVE control
preimages (which MUST re-find their target addresses, proving this candidate
path sees targets at all) and the two audio-instruction outputs as NEGATIVE
controls (documented by R-THIRDDOOR-AUDIO as reaching zero targets by design,
so each MUST stay unmatched). A witness that only ever agrees would not
discriminate; these do.

Local only. Every address compared is already public in
`data/planted-addresses.csv` or the README gate table. Nothing is broadcast.
"""
from __future__ import annotations

import argparse
import sys
import time

import third_door as TD

# The two renderings of the audio stream, taken from the certified harness so
# they are never retyped here (R-THIRDDOOR-AUDIO: the two differ in ONE token,
# 18 vs 48, and the leading 18 is a transcription slip -- read as hex bytes the
# community list spells HASHTHETEXT and the as-given list spells ASHTHETEXT).
STREAMS = [("as-given", TD.AUDIO_GIVEN), ("community", TD.AUDIO_COMMUNITY)]

YELLOW = 9      # phase-1 matrix coloured-square counts, leads note 22
BLUE = 15
AUDIO_URL = ("89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac"
             "0152f6a32")


def isprime(n: int) -> bool:
    """The same primality test `third_door_colors` uses."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def _add(out: list, seen: set, tag: str, b) -> None:
    if isinstance(b, str):
        b = b.encode()
    if b and b not in seen:
        seen.add(b)
        out.append((tag, b))


def render(tag: str, toks: list[str], out: list, seen: set) -> None:
    """Render a token list exactly the way `third_door.audio_candidates` renders
    the stream, so a zeroed stream is compared like an unzeroed one."""
    if not toks:
        return
    # a token that is not a clean decimal/hex value cannot be rendered as a byte
    # stream, but its TEXT forms still can, so those go first.
    _add(out, seen, f"{tag}/spaced", " ".join(toks))
    _add(out, seen, f"{tag}/joined", "".join(toks))
    _add(out, seen, f"{tag}/hyphen", "-".join(toks))
    _add(out, seen, f"{tag}/comma", ",".join(toks))
    _add(out, seen, f"{tag}/comma-space", ", ".join(toks))
    _add(out, seen, f"{tag}/reversed-tokens", " ".join(reversed(toks)))
    _add(out, seen, f"{tag}/reversed-joined", "".join(reversed(toks)))

    if all(t.replace("0", "x", 1).isalnum() and t for t in toks):
        try:
            raw = bytes(int(t, 16) for t in toks)
        except ValueError:
            raw = b""
        if len(raw) == len(toks):
            _add(out, seen, f"{tag}/hex-bytes", raw)
            _add(out, seen, f"{tag}/hex-bytes-upper", raw.upper())
            _add(out, seen, f"{tag}/hex-bytes-as-text", "".join(
                chr(c) if 32 <= c < 127 else "?" for c in raw))

    if all(t.isdigit() for t in toks) and all(int(t) < 256 for t in toks):
        dec = bytes(int(t) for t in toks)
        _add(out, seen, f"{tag}/dec-bytes", dec)
        _add(out, seen, f"{tag}/dec-as-text", "".join(
            chr(c) if 32 <= c < 127 else "?" for c in dec))

    if all(t.isdigit() for t in toks):
        for base, t2 in ((1, "a1z26-1"), (0, "a1z26-0")):
            s = "".join(chr(64 + int(t) + (0 if base == 1 else -1))
                        if 1 <= int(t) + (0 if base == 1 else -1) <= 26
                        else "?" for t in toks)
            _add(out, seen, f"{tag}/{t2}", s)


def zeroed_candidates() -> list[tuple[str, bytes]]:
    """The primes / zeroed / yellow-blue rules applied to both streams."""
    out: list[tuple[str, bytes]] = []
    seen: set[bytes] = set()

    for sname, nums in STREAMS:
        toks = nums.split()
        m = len(toks)

        # --- primes: keep-only, drop-only, both basings -------------------
        for base in (0, 1):
            idx = {i for i in range(m) if isprime(i + base)}
            keep = [toks[i] for i in range(m) if i in idx]
            drop = [toks[i] for i in range(m) if i not in idx]
            render(f"{sname}/primes/keep-base{base}", keep, out, seen)
            render(f"{sname}/primes/drop-base{base}", drop, out, seen)

        # --- zeroed out: the creator's literal words, BOTH polarities -----
        for base in (0, 1):
            idx = {i for i in range(m) if isprime(i + base)}
            # non-prime ranks zeroed -> the prime ranks survive
            for ztag, zed in (("0", "0"), ("NUL", "\x00")):
                nonprime = [zed if i not in idx else toks[i] for i in range(m)]
                prime = [zed if i in idx else toks[i] for i in range(m)]
                render(f"{sname}/zeroed/nonprime-{ztag}-base{base}",
                       nonprime, out, seen)
                render(f"{sname}/zeroed/prime-{ztag}-base{base}",
                       prime, out, seen)
                # dropping the zeroed ranks instead of blanking them
                render(f"{sname}/zeroed/drop-nonprime-{ztag}-base{base}",
                       [toks[i] for i in range(m) if i in idx], out, seen)

        # --- yellow/blue as a POSITION rule: ranks that are multiples of 9
        # or 15 (Yellow=9 / Blue=15, the phase-1 counts) --------------------
        for label, mults in (("yellow", [YELLOW]), ("blue", [BLUE]),
                             ("both", [YELLOW, BLUE])):
            hit = {i for i in range(m) if any((i + 1) % k == 0 for k in mults)}
            for bname, base in (("1-based", 1), ("0-based", 0)):
                h = {i for i in range(m) if any((i + base) % k == 0
                                                for k in mults)}
                render(f"{sname}/yb-{label}/zeroed-{bname}",
                       ["0" if i in h else toks[i] for i in range(m)],
                       out, seen)
                render(f"{sname}/yb-{label}/keep-{bname}",
                       [toks[i] for i in range(m) if i not in h], out, seen)
                render(f"{sname}/yb-{label}/drop-{bname}",
                       [toks[i] for i in range(m) if i in h], out, seen)
            del hit

    return out


def structure_note() -> None:
    """Report the arithmetic that makes part of the family vacuous, before the
    run, so a small candidate count is not mistaken for a thin sweep.

    The audio stream is 11 tokens. "Yellow has a number and so does Blue" with
    the established Yellow=9 / Blue=15 (phase-1 matrix counts, leads note 22)
    applied as a POSITION rule therefore cannot touch the blue channel at
    1-basing at all: 11 < 15, so no rank is a multiple of 15. Only 9 lands (rank
    9 of 11). At 0-basing rank 0 is a multiple of BOTH, so blue becomes a
    one-position rule. This is the same class of observation as R-COLORDOOR's
    "the rule's YELLOW side has no referent on any certified colour object" --
    recorded here rather than left as a silently-empty branch.
    """
    for sname, nums in STREAMS:
        toks = nums.split()
        m = len(toks)
        print(f"  {sname}: {m} tokens; yellow(9) hits at 1-basing "
              f"{[i + 1 for i in range(m) if (i + 1) % YELLOW == 0]}; "
              f"blue(15) hits at 1-basing "
              f"{[i + 1 for i in range(m) if (i + 1) % BLUE == 0] or 'NONE - '
                 'vacuous, 11 < 15'}")


def control_candidates() -> list[tuple[str, bytes]]:
    """5 CSV POSITIVE controls (must re-find a target) + 2 audio NEGATIVE
    controls (documented as reaching zero targets, so must stay unmatched)."""
    out: list[tuple[str, bytes]] = []
    seen: set[bytes] = set()
    for w in TD.WITNESSES:
        _add(out, seen, f"control/{w[0].decode()[:24]}", w[0])
    _add(out, seen, "negative/url-hash", AUDIO_URL)
    _add(out, seen, "negative/HASHTHETEXT", b"HASHTHETEXT")
    return out


def run() -> tuple[int, int, int, bool]:
    t0 = time.time()
    ctl = control_candidates()
    cands = zeroed_candidates()
    pool = ctl + cands

    hits: list = []
    tried = 0
    for tag, pre in pool:
        for (cname, comp), addr in TD.addresses_for(pre).items():
            tried += 1
            if addr in TD.TARGETS:
                hits.append((tag, pre, cname, comp, addr))

    dt = time.time() - t0
    pos = {p for t, p in ctl if t.startswith("control/")}
    neg = {p for t, p in ctl if t.startswith("negative/")}
    ctl_hits = {h[1] for h in hits if h[0].startswith("control/")}
    neg_hit = {h[1] for h in hits if h[0].startswith("negative/")}
    real = [h for h in hits if not h[0].startswith(("control/", "negative/"))]

    ok = True
    if ctl_hits != pos:
        print(f"  WITNESS FAILED: {len(ctl_hits)}/{len(pos)} distinct control "
              f"preimages re-found; missing "
              f"{sorted(p[:24] for p in pos - ctl_hits)}")
        ok = False
    if neg_hit:
        print("  WITNESS FAILED: negative control(s) matched: "
              f"{sorted(p[:24] for p in neg_hit)}")
        ok = False

    nderive = sum(len(TD.addresses_for(p)) for _t, p in cands)
    nctl_rows = len([t for t, _p in ctl if t.startswith("control/")])
    print(f"controls: {len(ctl_hits)}/{len(pos)} DISTINCT control preimages "
          f"claim target addresses (from {nctl_rows} control rows - "
          f"gsmg.io/theseedisplanted legitimately claims two addresses across "
          f"two constructions); negatives unmatched: {not neg_hit}")
    print(f"audio x zeroed-out battery: {len(cands)} preimages x 6 "
          f"constructions x 2 pubkey forms = {nderive} address derivations "
          f"in {dt:.1f}s")
    print("  position-rule reachability (recorded before the run):")
    structure_note()
    for tag, pre, cname, comp, addr in real:
        funded, op, status = TD.TARGETS[addr]
        print(f"  MATCH  {addr}  [{cname}, "
              f"{'compressed' if comp else 'uncompressed'}]  from {tag} = "
              f"{pre!r}  (funded {funded}, op_return {op!r}, "
              f"status {status})")
    if not real:
        print("  0 MATCH on the third door, the 8 other planted addresses and"
              " both gate addresses")
    return len(cands), nderive, len(real), ok


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--zeroed", action="store_true",
                    help="run the audio x zeroed-out/primes battery against "
                         "the third door")
    a = ap.parse_args(argv)
    rc = 0
    if a.selftest or not (a.selftest or a.zeroed):
        print("== third_door.selftest ==")
        rc |= TD.selftest()
        print("== this tool's witness loop ==")
        ncand, _nd, _hits, ok = run()
        if not ok:
            print("SELFTEST FAIL: witness loop did not behave as documented")
            return 1
        print(f"SELFTEST PASS: 5 CSV positives re-found + 2 audio negatives "
              f"held, {ncand} composed candidates carried")
    if a.zeroed and rc == 0:
        print("== third_door.selftest (pre) ==")
        rc |= TD.selftest()
        _ncand, _nd, nhits, ok = run()
        print("== third_door.selftest (post) ==")
        rc |= TD.selftest()
        if not ok:
            rc |= 1
        if nhits:
            rc |= 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
