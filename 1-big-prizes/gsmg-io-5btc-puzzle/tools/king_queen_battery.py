#!/usr/bin/env python3
"""king_queen_battery.py -- regenerate the candidate file for R-FUBCDKING-ORACLEQUEEN.

The user steered: check "fucbking" and "oracle queen".  Those are the two
authorial nouns of the Phase-3.2 sentence on the page itself:

    "Raising the stakes without extra chances of winning.
     A fubcd-king & oracle-queen, thingky mvps, on a sad board but as wide as
     the first one seen."

This generator builds the X-candidate family for BOTH funded gates from that
sentence only.  Three seed groups, each expanded by the repo's standard
7-form separator/case matrix (exact, lower, upper, strip, strip_lower, dash,
underscore), so nothing depends on my guess of the author's spacing:

  1. the two steered tokens, spelled every plausible way -- including the
     user's own "fucbking", which is `fubcdking` with the D deleted, so the
     deletion-of-a-letter reading the recipe itself uses ("drop the repeated
     letters") gets its own slot;
  2. the pair joined as the author wrote it (with the ampersand) and as the
     display groups the community derived from it;
  3. the whole sentence, with and without the leading "A" and the trailing
     full stop.

Regenerates byte-identically:

    python3 tools/king_queen_battery.py > /tmp/fkq_cands.txt
    python3 tools/oracle.py         --stdin < /tmp/fkq_cands.txt
    python3 tools/oracle_dualite.py --stdin < /tmp/fkq_cands.txt

Public/authorized puzzle only.  No network, no writes.
"""
from __future__ import annotations

import re
import string
import sys

SENTENCE = (
    "A fubcd-king & oracle-queen, thingky mvps, on a sad board "
    "but as wide as the first one seen."
)

# 1. the two steered tokens.
SEEDS_TOKEN = [
    # as the author spelled them
    "fubcd-king", "fubcd king", "fubcdking",
    "oracle-queen", "oracle queen", "oraclequeen",
    # the user's spelling: fubcdking with the D dropped
    "fucbking", "fucb-king", "fucb king", "fucb", "fucbkingqueen",
    # censored / near-homophone readings of the same token
    "fuckking", "fuck-king", "fuck king", "fucking", "fuckingking",
    "fukking", "fukkingking", "fcking", "fckingking", "fuckingk ing",
    # dropped-letter and swapped-letter variants of fubcdking
    "fubcking", "fubdking", "fubckin", "fubcdkin", "fubcdkng",
    "fcbcdking", "fubcdikng", "kubcdking",
    # the bare nouns on their own
    "king", "queen", "oracle",
    # oracle-queen as one lexical unit, and its halves
    "oraclequeenking", "kingoracle", "kingoraclequeen",
    "queenoracle", "queenoracle", "oraclequeensing",
]

# 2. the pair joined as the author wrote it, and the community display groups.
SEEDS_PAIR = [
    "fubcd-king & oracle-queen", "fubcd-king&oracle-queen",
    "fubcd-king and oracle-queen", "fubcd-king,oracle-queen",
    "fucbking & oracle-queen", "fucbking and oracle queen",
    "fubcdkingoraclequeen", "fubcdkingoraclequeen",
    "fubcdking_oraclequeen", "fubcdking-oraclequeen",
    "oracle-queen, thingky mvps", "thingky mvps",
    # the certified display groups, raw and in their sounded form
    "fubcdora", "lethingkymvps", "jqzxw", "jokes", "pandora",
    "lething", "thingky", "mvps", "keymvps", "fubcdoraking",
    "jokesoraclequeen", "fubcdora.lethingkymvps.jqzxw",
]

# 3. the sentence itself.
SEEDS_SENTENCE = [
    SENTENCE,
    SENTENCE.rstrip("."),
    SENTENCE[2:],                                  # drop the leading "A "
    SENTENCE[2:].rstrip("."),
    "A fubcd-king & oracle-queen, thingky mvps",
    "fubcd-king & oracle-queen, thingky mvps, on a sad board but as wide as "
    "the first one seen",
    "on a sad board but as wide as the first one seen",
    "as wide as the first one seen",
]

PUNCT = set(string.punctuation)


def strip_punct(s: str) -> str:
    return "".join(ch for ch in s if ch not in PUNCT)


def forms(s: str) -> list[str]:
    """The repo's standard 7-form separator/case matrix."""
    bare = strip_punct(s).lower()
    return [
        s,
        s.lower(),
        s.upper(),
        bare,
        bare,
        s.replace(" ", "-"),
        s.replace(" ", "_"),
    ]


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--count":
        print(len(build()))
        return 0
    for c in build():
        print(c)
    return 0


def build() -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for seed in SEEDS_TOKEN + SEEDS_PAIR + SEEDS_SENTENCE:
        for f in forms(seed):
            if not f or f in seen:
                continue
            seen.add(f)
            out.append(f)
    # a final normalised pass: the recipe that built the board alphabet is
    # "strip the punctuation, drop the repeated letters", so also offer every
    # seed with adjacent repeats collapsed and with all separators removed.
    for seed in SEEDS_TOKEN + SEEDS_PAIR + SEEDS_SENTENCE:
        b = strip_punct(seed)
        b = re.sub(r"(.)\1+", r"\1", b)
        flat = b.replace(" ", "")
        for f in (b, flat, flat.lower(), flat.upper()):
            if f and f not in seen:
                seen.add(f)
                out.append(f)
    return out


if __name__ == "__main__":
    sys.exit(main())