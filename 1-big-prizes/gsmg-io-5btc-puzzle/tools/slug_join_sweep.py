#!/usr/bin/env python3
"""slug_join_sweep.py -- hash-slug preimage sweep for the 7 OPEN gsmg.io slugs.

The wordjoin universe of section 126/wordjoin_sweep.py was oracle-tested as answer X
(45,368 candidates, both gates, 0 MATCH) but was NEVER hashed against the 7 open
hash-slugs. The recovered preimages are lowercase, often-separator-free phrase joins,
so this sweep sha256-hashes the exact same wordjoin universe plus the author-hint
assemblies and pairs/triples of the on-page word tokens, and compares each digest to
the 7 open slugs (tested.md section 15).

Self-witness: the three known preimages (`ourfirsthintisyourlastcommand`,
`hopeisthequintessentialhumandelusion`, `anstoo`) MUST re-match their slugs here, or
the negative is not certified.
"""

import hashlib
import itertools

WORDS = [
    "shabef",
    "matrixsumlist",
    "enter",
    "lastwordsbeforearchichoice",
    "thispassword",
    "ourfirsthintisyourlastcommand",
    "anstoo",
]

SEGI = "agdafaoaheiecggchgicbbhcgbehcfcoabicfdhhcdbbcagbdaiobbgbeadedde"
SEGII = "cfobfdhgdobdgooigdocdaoofidh"

OPEN_SLUGS = [
    "0b0f37ecaf7107f86ee2f477992f25bc7abe8f799d0dd713658c17d37496ee32",
    "10d6a2c5320bfbd47d35f18dd67f177ae5a5f4b5d18a8a5127361c2941a92908",
    "673e3b1a60ebe6fc4a8be88acde2600e12afd9efb2543e26b1b30039f8356b0d",
    "a2aefdbb953b70aa20d640effda4accee1e1f48acf1e4fcebdc2fc011418b0b1",
    "aca20ae7c6b5f425bdd9bd809583b28fd086b3380990689e37b6e94f3fb5ed9a",
    "c2eef34b479eb6c89c7aa89c49229ff5f67563da4e56d5782574489c4b776625",
    "f9719d6d531e6c3b5129644cd05da57bc6fdd075c9a61267c41d4b9627936096",
]

KNOWN = {
    "ourfirsthintisyourlastcommand":
    "e24bd2c0fd454632f9fdd26cbdc210597f79e9fca9719c126a6d30cb41ef0238",
    "hopeisthequintessentialhumandelusion":
    "c1780cbbaa105784949cd6a2924e1f51a947b4258a0655defd0cd2e6f6544046",
    "anstoo":
    "21ef053324184a4db5dc19b760e2d6ef61b07376a6f8a1514bb529d99de1fe0f",
}

EXTRA_PHRASES = [
    "yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang",
    "blueyellowprimesmatrixsumlistlastwordsbeforearchichoiceyinyang",
    "thearchitectschoice",
    "halfandbetterhalf",
    "causality",
    "theseedisplanted",
    "yourlastcommand",
    "secondanswer",
    "shabefanstoo",
    "shabefour",
    "theflowerblossomsandwiltsofthefaithfulservant",
    "followthewhiterabbit",
]


def main():
    slugs = set(OPEN_SLUGS)
    hits = []
    count = 0

    def test(s):
        nonlocal count
        count += 1
        if hashlib.sha256(s.encode()).hexdigest() in slugs:
            hits.append(s)

    # witness block FIRST: known preimages must re-find their slugs
    for pre, slug in KNOWN.items():
        d = hashlib.sha256(pre.encode()).hexdigest()
        if d != slug:
            print(f"WITNESS FAIL for {pre!r}: {d} != {slug}")
            return 2
    print("WITNESS OK: all 3 known preimages re-found their slugs")

    seps = ["", "_", "."]
    for order_tuple in itertools.permutations(WORDS):
        for sep in seps:
            joined = sep.join(order_tuple)
            test(joined)
            test(joined.lower())
            test(joined.upper())
            test(sep.join(w.title() for w in order_tuple))

    page_order_join = "".join(WORDS)
    test(page_order_join)
    test(page_order_join.upper())
    for seg in (SEGI, SEGII):
        test(seg + page_order_join)
        test(page_order_join + seg)
        test(seg + "_" + page_order_join)
        test(page_order_join + "_" + seg)

    for k in range(2, 4):
        for combo in itertools.permutations(WORDS, k):
            for sep in seps:
                j = sep.join(combo)
                test(j)
                test(j.lower())

    for p in EXTRA_PHRASES:
        test(p)

    print(f"candidates sha256-hashed: {count}")
    if hits:
        for h in hits:
            print("HIT:", h)
        return 0
    print("0 of the 7 open slugs matched")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())