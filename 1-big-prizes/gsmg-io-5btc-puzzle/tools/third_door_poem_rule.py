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
        pp1 = primes_upto(m)
        pp0 = {i for i in range(m) if i in primes_upto(m + 1)}
        for label, pset, base in (("1b", pp1, 1), ("0b", pp0, 0)):
            comp = set(range(m)) - pset
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
                ranks = {i for i in range(m) if (i + base) % num == 0 and (i + base) != 0}
                _add(out, seen, f"{oname}/yb-{cname}-drop/{label}",
                     _sel_rank(base_txt, set(range(m)) - ranks, base))
                for fill, fname in (("0", "zero"), ("\x00", "nul")):
                    _add(out, seen, f"{oname}/yb-{cname}-{fname}/{label}",
                         "".join(fill if (i + base) in ranks else ch
                                 for i, ch in enumerate(base_txt)))
            both = {i for i in range(m)
                    if ((i + base) % YELLOW == 0 or (i + base) % BLUE == 0) and (i + base) != 0}
            _add(out, seen, f"{oname}/yb-both-drop/{label}",
                 _sel_rank(base_txt, set(range(m)) - both, base))

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


def selftest() -> int:
    """Two witness layers, and both must discriminate.

    Layer 1 delegates to third_door's own 5 CSV witnesses. Layer 2 pushes the CSV
    POSITIVE controls through THIS file's candidate path, and the audio negative
    controls, which must STAY unmatched - a witness that could only agree would not
    catch a candidate path that never sees a target.
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
