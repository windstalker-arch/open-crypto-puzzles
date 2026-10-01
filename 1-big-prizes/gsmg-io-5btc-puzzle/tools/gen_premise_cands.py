#!/usr/bin/env python3
"""Premise-corrected candidate generator for the small final gate.

The verified password form for the 96-byte small blob (salt 3ab585348552415d) is a
RAW concatenation of the SalPhaseIon page tokens - the oracle's old sha256(X) hex
premise is falsified. Certified anchor: the raw string
  matrixsumlist + enter + lastwordsbeforearchichoice + thispassword + matrixsumlist
decrypts (EVP-MD5) to the 79-byte chain-1 artifact B1_79B.bin.

This emits every ordering / repetition / joiner / case family over the page tokens
(and the known community 7-token superset), one candidate per line on stdout.
Feed through bloomfast (incremental, skips already-swept strings), then the
corrected oracle which tries each candidate as RAW X and as sha256(X) hex, under
both digests, against both gate addresses.

N before dedup ~= 128k; D ~= 6.6k cand/s corrected oracle; t ~= 20s after bloom.
"""
from __future__ import annotations

import itertools
import sys

CORE = ["matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword"]
EXTRAS = ["yourlastcommand", "secondanswer", "anstoo", "firsttint", "shabef",
          "firsthint", "ourfirsthintisyourlastcommand", "hopeisthequintessentialhumandelusion"]
ALL = CORE + EXTRAS

SEPS = ["", "_", "-", "."]


def cases(s: str) -> list[str]:
    return [s, s.upper(), s.title()]


def emit(c: str) -> None:
    sys.stdout.write(c + "\n")


def main() -> int:

    # 1. The certified family: p1..p4 with p1 wrapped at both ends (the anchored
    #    password shape), all orderings of the middle three.
    for perm in itertools.permutations(CORE[1:]):
        for p1rep in [CORE[0], CORE[0] + CORE[0]]:
            seq = [p1rep] + list(perm) + [CORE[0]]
            for sep in SEPS:
                for c in cases(sep.join(seq)):
                    emit(c)

    # 2. All sequences over CORE of length 3..6 (repetition allowed) - covers
    #    "weave" password shapes beyond the anchored one.
    for L in (3, 4, 5, 6):
        for seq in itertools.product(CORE, repeat=L):
            joined = "".join(seq)
            for c in cases(joined):
                emit(c)

    # 3. All orderings of CORE (perms) with every joiner and case.
    for perm in itertools.permutations(CORE):
        for sep in SEPS:
            for c in cases(sep.join(perm)):
                emit(c)

    # 4. Core in fixed order + one extra token (leading or trailing) + joiners.
    for ext in EXTRAS:
        for lead, _ in ((0, 0), (1, 0)):
            seq = [ext] + CORE if lead else CORE + [ext]
            for sep in SEPS:
                for c in cases(sep.join(seq)):
                    emit(c)

    # 5. Pairs / triples of ALL tokens (short-key booms need repeats too).
    for L in (2, 3):
        for seq in itertools.product(ALL, repeat=L):
            joined = "".join(seq)
            for c in cases(joined):
                emit(c)

    # 6. The seven community tokens in their canonical XOR order.
    seven = ["matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
             "matrixsumlist", "yourlastcommand", "secondanswer"]
    for sep in SEPS:
        for c in cases(sep.join(seven)):
            emit(c)

    return 0


if __name__ == "__main__":
    sys.exit(main())