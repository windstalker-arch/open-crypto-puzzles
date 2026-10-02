#!/usr/bin/env python3
"""third_door_poem_rule.py - the creator's three named inputs applied to the
POEM, which is the one object every prior third-door row skipped.

THE GAP THIS FILLS, stated as a coverage fact rather than a hunch. The creator's
surviving third-door sentence names three inputs - "Yellow has a number and so does
Blue", "primes", "zeroed out" - and the README scopes them to "read on a non-textual
object". Every row that carried them to `1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9` honored
that scoping, on a non-textual object:

  R-THIRDDOOR-AUDIO   720 derivations   the 11-token audio stream, untransformed
  R-COLORDOOR       4,326 derivations   colour runs on the sticker strip and bands
  R-YELLOWBLUE-HASH   628 derivations   the certified scalars, 574061 and 17/41
  R-YBCOORDS        3,092 derivations   yellow/blue coordinates on the 14x14 matrix
  composition row   3,748 derivations   all three rules composed on the audio stream

And the poem itself was carried to the third door exactly once, by
`third_door_yellowblue.py:162`, as a single literal - `("hint/poem", POEM)` - i.e. the
whole string hashed directly. So the poem has been an OBJECT OF THE HASH but never an
OBJECT OF THE RULE. "primes" and "zeroed out" have never selected, dropped or zeroed a
character of it. That is the hole, and it is a real one: it is the reading in which the
April 2020 audio hint supplies the RULE and the January 2020 poem supplies the TEXT it is
applied to, which is the only arrangement under which those two artifacts are connected
to each other at all.

The rules are taken from the corpus rather than invented here, and every one is a
mechanical restatement of words the creator actually published:
  primes      - ranks that are prime. Both basings, keep-only and drop-only, because
                the hint does not say which side survives.
  zeroed out  - the creator's literal phrase, both polarities ('0' and NUL on the
                non-prime side, and on the prime side), because the hint does not say
                which side was zeroed. `third_door_colors` carries both for that reason.
  yb position - "Yellow has a number and so does Blue" as a position rule with the
                established Yellow=9 / Blue=15 (leads.md note 22, the 14x14 phase-1
                coloured-square counts), ranks that are multiples of 9 or 15 zeroed or
                dropped, per channel and both together, both basings.

Plus the one reading this file was written to test, `selfnum` below.

Local only: compares against addresses already public in data/planted-addresses.csv and
the two funded gates. No key is swept, nothing is broadcast.
"""
import argparse
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("third_door", os.path.join(HERE, "third_door.py"))
TD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(TD)

# The poem, verbatim as `third_door_yellowblue.py:79` already holds it. Imported from
# that tool rather than retyped, so the two cannot drift apart.
_sy = importlib.util.spec_from_file_location(
    "third_door_yellowblue", os.path.join(HERE, "third_door_yellowblue.py"))
SY = importlib.util.module_from_spec(_sy)
_sy.loader.exec_module(SY)
POEM = SY.POEM
POEM_TAIL = SY.POEM + " Go back to the first puzzle piece"

BLUE = 15
YELLOW = 9

# The 9/15 spellings `third_door_colors` and `third_door_yellowblue` already carried to
# the third door. Held here so this file cannot silently re-run a certified row.
_EXCLUDED = {"9 15", "915", "15 9", "159", "9,15", "15,9", "yellow9blue15",
             "yellow9andblue15", "blue15andyellow9", "yellow has 9 and blue has 15",
             "yellow9 blue15", "yellow_9_blue_15", "9and15", "9 and 15"}


def primes_upto(n: int) -> set[int]:
    s, out = set(), set()
    for k in range(2, n + 1):
        if all(k % d for d in range(2, int(k ** 0.5) + 1)):
            out.add(k)
    return out


def _add(out, seen, tag, v):
    if isinstance(v, int):
        v = str(v)
    if isinstance(v, str):
        v = v.encode()
    if not v or v in seen:
        return
    seen.add(v)
    out.append((tag, v))


def _sel_rank(s: str, keep: set[int], base: int) -> str:
    return "".join(ch for i, ch in enumerate(s) if (i + base) in keep)


def candidates():
    """Every reading of the rule set on the poem. Returns [(tag, preimage_bytes)]."""
    out, seen = [], set()
    n = len(POEM)
    p1 = primes_upto(n)                       # 1-based prime ranks
    p0 = {i for i in range(n) if i in primes_upto(n + 1)}   # 0-based prime ranks

    objects = [
        ("poem", POEM),
        ("poem-nospace", POEM.replace(" ", "")),
        ("poem-lower", POEM.lower()),
        ("poem-nospace-lower", POEM.replace(" ", "").lower()),
        ("poem-tail", POEM_TAIL),
        ("poem-nospace-tail", POEM_TAIL.replace(" ", "")),
    ]

    for oname, text in objects:
        base_txt = text
        m = len(base_txt)
        for label, base in (("1b", 1), ("0b", 0)):
            # Ranks are built in the SAME space the membership test uses. Building the
            # complement over range(m) instead put the last character out of reach on
            # 1-basing - rank m was never in the set - so the drop-only families
            # silently dropped the final character. Caught by W-B, not by inspection.
            ranks = {i + base for i in range(m)}
            pset = {r for r in ranks if _is_prime(r)}
            comp = ranks - pset
            # primes, keep-only and drop-only
            _add(out, seen, f"{oname}/primes-keep/{label}", _sel_rank(base_txt, pset, base))
            _add(out, seen, f"{oname}/primes-drop/{label}", _sel_rank(base_txt, comp, base))
            # zeroed out, both polarities, both fill characters
            for fill, fname in (("0", "zero"), ("\x00", "nul")):
                kept = "".join(ch if (i + base) in pset else fill
                               for i, ch in enumerate(base_txt))
                _add(out, seen, f"{oname}/zeroed-nonprime-{fname}/{label}", kept)
                kept2 = "".join(fill if (i + base) in pset else ch
                                for i, ch in enumerate(base_txt))
                _add(out, seen, f"{oname}/zeroed-prime-{fname}/{label}", kept2)
            # yb position rule, per channel and both, keep and drop
            for cname, num in (("yellow", YELLOW), ("blue", BLUE)):
                yranks = {r for r in ranks if r % num == 0 and r != 0}
                _add(out, seen, f"{oname}/yb-{cname}-drop/{label}",
                     _sel_rank(base_txt, ranks - yranks, base))
                for fill, fname in (("0", "zero"), ("\x00", "nul")):
                    _add(out, seen, f"{oname}/yb-{cname}-{fname}/{label}",
                         "".join(fill if (i + base) in yranks else ch
                                 for i, ch in enumerate(base_txt)))
            bothr = {r for r in ranks
                     if (r % YELLOW == 0 or r % BLUE == 0) and r != 0}
            _add(out, seen, f"{oname}/yb-both-drop/{label}",
                 _sel_rank(base_txt, ranks - bothr, base))

    # selfnum - "Yellow has a number and so does Blue" read as a statement about the
    # POEM'S OWN ordinals. In the poem, Yellow is the 7th word and Blue is the 14th.
    # That is a literal reading of the sentence on the object the sentence is in, and
    # 7 and 14 are both prime with 14 = 2*7, which is the kind of coincidence that is
    # either the rule or nothing. Not previously carried to the third door: the poem
    # was only ever hashed whole.
    words = POEM.replace(".", " ").split()
    wlow = [w.lower() for w in words]
    for wname in ("yellow", "blue"):
        if wname in wlow:
            r = wlow.index(wname) + 1
            _add(out, seen, f"selfnum/word-rank-{wname}", r)
            _add(out, seen, f"selfnum/word-rank-{wname}-0b", r - 1)
            _add(out, seen, f"selfnum/char-rank-{wname}",
                 POEM.lower().index(wname) + 1)
    y_rank = wlow.index("yellow") + 1 if "yellow" in wlow else 0
    b_rank = wlow.index("blue") + 1 if "blue" in wlow else 0
    for tag, v in (
        ("selfnum/y+b", f"{y_rank}{b_rank}"),
        ("selfnum/b+y", f"{b_rank}{y_rank}"),
        ("selfnum/y b", f"{y_rank} {b_rank}"),
        ("selfnum/y-b", f"{y_rank}-{b_rank}"),
        ("selfnum/y,b", f"{y_rank},{b_rank}"),
        ("selfnum/sum", y_rank + b_rank),
        ("selfnum/diff", abs(b_rank - y_rank)),
        ("selfnum/prod", y_rank * b_rank),
        ("selfnum/sentence", f"yellow is {y_rank} and blue is {b_rank}"),
        ("selfnum/sentence2", f"yellow {y_rank} blue {b_rank}"),
        ("selfnum/words", f"{words[y_rank - 1]}{words[b_rank - 1]}"),
        ("selfnum/word7", words[y_rank - 1] if y_rank else ""),
        ("selfnum/word14", words[b_rank - 1] if b_rank else ""),
        ("selfnum/char-at", POEM[y_rank - 1:b_rank]),
    ):
        _add(out, seen, tag, v)

    # The certified 574061 colour prime and the 17/41 prime sums are already carried by
    # R-YELLOWBLUE-HASH; they are re-added only in a POEM-derived reading (the prime
    # ranks of the poem) and never as bare scalars, which _EXCLUDED blocks.
    return [(t, v) for t, v in out if v.decode("latin1") not in _EXCLUDED]


def structure_note() -> None:
    """Print what the rule can and cannot reach on this object, before the run, so a
    thin candidate count cannot pass for a thick sweep."""
    words = POEM.replace(".", " ").split()
    wlow = [w.lower() for w in words]
    y = wlow.index("yellow") + 1 if "yellow" in wlow else None
    b = wlow.index("blue") + 1 if "blue" in wlow else None
    print("STRUCTURE")
    print(f"  poem chars           : {len(POEM)}")
    print(f"  poem words           : {len(words)}")
    print(f"  'Yellow' word rank   : {y}  prime={y in primes_upto(len(words)) if y else None}")
    print(f"  'Blue'   word rank   : {b}  prime={b in primes_upto(len(words)) if b else None}")
    print(f"  yellow=9 fires on    : ranks 9,18,27,36,45,54 of {len(POEM)} chars")
    print(f"  blue=15 fires on     : rank 15,30,45,60 of {len(POEM)} chars")
    print(f"  blue=15 on words     : "
          f"{'FIRES' if len(words) >= 15 else 'CANNOT FIRE - only %d words' % len(words)}")
    print()


def _is_prime(k: int) -> bool:
    return k > 1 and all(k % d for d in range(2, int(k ** 0.5) + 1))


def _is_prime_sieve(k: int) -> bool:
    """Primality by a SIEVE, deliberately not sharing code with `_is_prime`.

    `_expected_from_poem()` has to be able to disagree with the generator. While it
    called `_is_prime` as well, a wrong `_is_prime` moved both sides together and W-B
    was blind to it - shown by fault injection, where stubbing `_is_prime` to a
    constant did not trip the witness. Two implementations that must not agree by
    construction.
    """
    if k < 2:
        return False
    sieve = [True] * (k + 1)
    sieve[0] = sieve[1] = False
    for p in range(2, int(k ** 0.5) + 1):
        if sieve[p]:
            for m in range(p * p, k + 1, p):
                sieve[m] = False
    return sieve[k]


def _expected_from_poem() -> dict:
    """Recompute this family's load-bearing facts straight from POEM, WITHOUT calling
    the generator's helpers.

    This exists because the first version of the witness in this file validated only
    `third_door`, which layer 1 already covers, and therefore passed rc=0 with
    `candidates()` returning an EMPTY list - proven by fault injection, both by
    stubbing `candidates()` and by stubbing `_add`. A witness that cannot disagree with
    the thing it is witnessing is decorative, so these values are derived a second,
    independent way here and the witness asserts the generator agrees with them.
    """
    words = POEM.replace(".", " ").split()
    wlow = [w.lower() for w in words]
    return {
        "yellow_word_rank": wlow.index("yellow") + 1,
        "blue_word_rank": wlow.index("blue") + 1,
        "primes_keep_1b": "".join(c for i, c in enumerate(POEM) if _is_prime_sieve(i + 1)),
        "zeroed_nonprime_1b": "".join(c if _is_prime_sieve(i + 1) else "0"
                                      for i, c in enumerate(POEM)),
        "primes_drop_1b": "".join(c for i, c in enumerate(POEM) if not _is_prime_sieve(i + 1)),
        "n_chars": len(POEM),
        "n_words": len(words),
    }


def _witness_own_path() -> int:
    """Witnesses that can FAIL when this tool's own generator is broken.

    W-A INJECTION. A certified preimage is pushed through THIS file's `_add` and must
    survive dedup and still derive its certified address, so the add/dedup path is
    exercised rather than assumed.
    W-B INDEPENDENT RECOMPUTATION. `_expected_from_poem()` derives the primes-keep,
    primes-drop and zeroed-nonprime strings a second way, directly from the POEM
    constant. The generator's output must CONTAIN all three, byte for byte. This is the
    witness that a stubbed-out or inverted selector cannot pass.
    W-C THE RULES MUST DO WORK. The rule outputs must differ from the object and from
    each other; a selector that returned the input unchanged, or every family the same
    string, would otherwise pass B and look like a sweep.
    W-D STRUCTURE. The reachability claim `structure_note()` prints is asserted against
    the poem, so the "blue=15 cannot fire on word ranks" finding cannot rot into a
    comment that is no longer true of the text.
    """
    bad = 0
    cands = candidates()
    have = {v for _t, v in cands}
    exp = _expected_from_poem()

    # W-B0 the two primality implementations must agree over the whole rank range.
    # Neither is assumed correct; a disagreement is reported rather than resolved by
    # picking a winner, because "the witness and the tool agree" is not evidence.
    disagree = [k for k in range(exp["n_chars"] + 1)
                if _is_prime(k) != _is_prime_sieve(k)]
    if disagree:
        print(f"  [FAIL] W-B0 primality implementations disagree at {disagree}")
        bad += 1

    # W-A injection through this file's own add/dedup path.
    probe = b"gsmg.io/theseedisplanted"
    out, seen = [], set()
    _add(out, seen, "witness/inject", probe)
    _add(out, seen, "witness/inject-dupe", probe)      # must dedup away
    if len(out) != 1:
        print(f"  [FAIL] W-A dedup: 2 adds of one preimage yielded {len(out)} entries")
        bad += 1
    elif not any(a == "148XH2YBmLr4oAJXQcG84FpNYoBmqnVPHQ"
                 for (_c, _k), a in TD.addresses_for(out[0][1]).items()):
        print("  [FAIL] W-A injection: the certified address was not re-derived "
              "through this file's _add path")
        bad += 1

    # W-B independent recomputation.
    for key in ("primes_keep_1b", "primes_drop_1b", "zeroed_nonprime_1b"):
        if exp[key].encode() not in have:
            print(f"  [FAIL] W-B {key}: generator does not contain the independently "
                  f"recomputed value {exp[key]!r}")
            bad += 1
    if not cands:
        print("  [FAIL] W-B generator returned NO candidates - the search is empty")
        bad += 1

    # W-C the rules must actually change the object, and differently per family.
    if exp["primes_keep_1b"].encode() == POEM.encode():
        print("  [FAIL] W-C primes-keep returned the poem unchanged - selector inert")
        bad += 1
    for a, b in (("primes_keep_1b", "primes_drop_1b"),
                 ("primes_keep_1b", "zeroed_nonprime_1b")):
        if exp[a] == exp[b]:
            print(f"  [FAIL] W-C {a} == {b} - families collapsed")
            bad += 1

    # W-D the structure claim, asserted rather than assumed.
    if exp["n_words"] < BLUE:
        print(f"  [PASS] W-D blue={BLUE} still cannot fire on word ranks "
              f"(poem has {exp['n_words']} words)")
    else:
        print(f"  [WARN] W-D poem now has {exp['n_words']} words, so blue={BLUE} "
              f"CAN fire on word ranks - structure_note() text is stale")

    print(f"  [W-A..D] {len(cands)} candidates, {bad} failures, "
          f"yellow={exp['yellow_word_rank']} blue={exp['blue_word_rank']} "
          f"chars={exp['n_chars']} words={exp['n_words']}")
    return bad


def selftest() -> int:
    """Three witness layers, and every one of them must be able to fail.

    Layer 1 delegates to third_door's own 5 CSV witnesses. Layer 2 pushes the CSV
    POSITIVE controls through `TD.addresses_for` and the audio NEGATIVE controls, which
    must STAY unmatched - a witness that could only agree would not catch a candidate
    path that never sees a target. Layer 3 (`_witness_own_path`) is the one that makes
    this file's selftest mean anything: the first two layers pass with an EMPTY
    candidate generator, which is demonstrated by fault injection in the ledger row.
    """
    bad = 0
    bad += TD.selftest()
    verified = [r for r in TD.PLANTED
                if r.get("status", "").strip().lower() == "verified"]
    pre_seen, found = set(), set()
    for r in verified:
        pre = r["preimage"].encode() if r.get("preimage") else None
        if not pre or pre in pre_seen:
            continue
        pre_seen.add(pre)
        for (cname, _c), addr in TD.addresses_for(pre).items():
            if addr in TD.TARGETS:
                found.add(addr)
    print(f"  [layer2] {len(found)}/{len({r['address'] for r in verified})} distinct "
          f"verified addresses re-found through TD.addresses_for over "
          f"{len(pre_seen)} distinct preimages")
    if not found:
        print("  [FAIL] layer 2 re-found nothing - the target set is not being seen")
        bad += 1
    for name, stream in (("audio/HASHTHETEXT", TD.audio_candidates()),):
        for tag, pre in stream:
            for (_c, _k), addr in TD.addresses_for(pre).items():
                if addr in TD.TARGETS:
                    print(f"  [FAIL] audio negative control {tag} matched {addr}")
                    bad += 1
    print(f"negative controls stayed unmatched: {bad == 0}")
    bad += _witness_own_path()
    print("SELFTEST PASS" if bad == 0 else f"SELFTEST FAIL: {bad}")
    return 0 if bad == 0 else 1


def run() -> int:
    cands = candidates()
    structure_note()
    fams = {}
    for tag, _v in cands:
        fams[tag.split("/")[0]] = fams.get(tag.split("/")[0], 0) + 1
    print(f"CANDIDATES: {len(cands)} unique preimages")
    for k in sorted(fams, key=lambda k: -fams[k]):
        print(f"  {k:<22} {fams[k]}")
    hits = []
    deriv = 0
    for tag, pre in cands:
        for (cname, comp), addr in TD.addresses_for(pre).items():
            deriv += 1
            if addr in TD.TARGETS:
                hits.append((tag, cname, comp, addr, TD.TARGETS[addr]))
                print(f"MATCH tag={tag} construction={cname} compressed={comp} "
                      f"address={addr} {TD.TARGETS[addr]} preimage={pre!r}", flush=True)
    print(f"\n{deriv} address derivations, {len(hits)} MATCH")
    if not hits:
        print("0 MATCH on the third door, the other 8 planted addresses and both gates.")
    return 1 if hits else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--poem", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.poem:
        return run()
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
