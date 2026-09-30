#!/usr/bin/env python3
"""king_queen_board_eanchor.py -- the two non-oracle halves of R-FUBCDKING-ORACLEQUEEN.

Companion to tools/king_queen_battery.py (which feeds the funded gates).  This
script answers two questions about the steered tokens "fucbking" and
"oracle queen" that do NOT need a gate call, so they can be settled once and
for all:

PART A - E_S DIGEST ANCHOR.  E_S = B2_79[64:79] = 740a25de4b8e946d0a5ae2667a23a2
is the standing check on a phrase A: if some phrase A hashes to it, the puzzle
produced it.  Here every base phrase derived from the Phase-3.2 sentence is
hashed under sha256/md5/sha1/ripemd160 and compared at [0:15] and [0:30].

PART B - BOARD REACHABILITY.  Can the certified 26-cell board alphabet
FUBCDORA.LETHINGKYMVPSJQZXW actually PRODUCE the two steered nouns?  Tested as
an ordered subsequence (the only reading under which the board is a text),
then relaxed to set containment, then under the two adjacency relaxations the
corpus already licenses (QWERTY king-move, VIC 3x10 grid), allowing 1 and then
2 substitutions.  For each failure it prints the SPECIFIC reason, because the
reason is the finding: it says why the community had to DERIVE the board from
the sentence rather than read the sentence off the board.

Public/authorized puzzle only.  No network, no writes.
"""
from __future__ import annotations

import hashlib
import string
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from king_queen_battery import (  # noqa: E402
    SEEDS_PAIR, SEEDS_SENTENCE, SEEDS_TOKEN, SENTENCE,
)

E_S = "740a25de4b8e946d0a5ae2667a23a2"

BOARD = "FUBCDORA.LETHINGKYMVPSJQZXW"      # 26 cells, punctuation removed
PUNCT_AT = (8, 22)                          # 0-based positions of '.' and '/'

TARGETS = ["FUCBKING", "FUBCDKING", "KING", "ORACLEQUEEN", "ORACLE", "QUEEN",
           "THINGKY"]

QWERTY_ROWS = [
    "1234567890", "qwertyuiop", "asdfghjkl", "zxcvbnm",
]
KEYMAP = {
    "1": "2QWERTYUIO", "2": "3WERTYUIO", "3": "4ERTYUIO", "4": "5RTYUIOP",
    "5": "6TYUIO", "6": "7YUIOP", "7": "8UIOP", "8": "9IOP", "9": "0IO",
    "0": "IO",
    "Q": "12WASDFG", "W": "23EASDFGH", "E": "34RDFGHJ", "R": "45TFGHJK",
    "T": "56YGHJKL", "Y": "67UHJKL", "U": "78IJKL", "I": "89JKL", "O": "90KL",
    "P": "0L",
    "A": "QWSZXC", "S": "WAEDXCV", "D": "SERFXCVB", "F": "DRT GVCB",
    "G": "FTYHVCB", "H": "GYUJBN", "J": "HUKNM", "K": "JL M", "L": "K",
    "Z": "ASX", "X": "ZSDC", "C": "XDVF", "V": "CFGB", "B": "VGHN",
    "N": "BHM", "M": "N",
}

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def qwerty_neighbours(letters: str) -> str:
    """Pool = the letters themselves plus every QWERTY king-move neighbour."""
    pool = set(c for c in letters if c in ALPHA)
    for ch in list(pool):
        for c in KEYMAP.get(ch, "").replace(" ", ""):
            if c.isalpha():
                pool.add(c)
    return "".join(sorted(pool))


def vic_neighbours(letters: str) -> str:
    """Pool = the letters plus every VIC 3x10 king-move neighbour.

    A 26-letter alphabet only spans rows 0-2 of a 3x10 grid, so row 2 holds
    columns 0-5; the neighbour test must respect the real length, not a
    hardcoded 3x10 that overruns ALPHA on the last row.
    """
    pool = set(c for c in letters if c in ALPHA)
    for ch in list(pool):
        r, c = divmod(ALPHA.index(ch), 10)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                rr, cc = r + dr, c + dc
                i = rr * 10 + cc
                if 0 <= rr < 3 and 0 <= cc < 10 and i < len(ALPHA):
                    pool.add(ALPHA[i])
    return "".join(sorted(pool))


def subseq_positions(board: str, target: str) -> list[int] | None:
    """Greedy ordered match; returns cell indices, or None."""
    out, j = [], 0
    for t in target:
        k = board.find(t, j)
        if k < 0:
            return None
        out.append(k)
        j = k + 1
    return out


def subseq_with_misses(board: str, target: str, allowed_misses: int
                       ) -> tuple[list[int], int] | None:
    """Ordered match where up to `allowed_misses` target letters may be absent
    from the pool (each miss consumes one relaxation). Returns (cells, misses)."""
    cells, misses, cur = [], 0, 0
    for ch in target:
        k = board.find(ch, cur)
        if k < 0:
            misses += 1
            if misses > allowed_misses:
                return None
            continue
        cells.append(k)
        cur = k + 1
    return cells, misses


def part_a() -> int:
    print("PART A - E_S DIGEST ANCHOR  (target E_S = %s)" % E_S)
    bases: list[str] = []
    seen: set[str] = set()
    for s in SEEDS_TOKEN + SEEDS_PAIR + SEEDS_SENTENCE + [SENTENCE]:
        for f in (s, s.lower(), s.upper(),
                  "".join(c for c in s if c not in string.punctuation),
                  s.replace(" ", "-"), s.replace(" ", "_")):
            if f and f not in seen:
                seen.add(f)
                bases.append(f)
    digests = ("sha256", "md5", "sha1", "ripemd160")
    hits = checks = 0
    for b in bases:
        raw = b.encode("utf-8")
        for d in digests:
            h = hashlib.new(d, raw).hexdigest()
            for tag, w in (("[0:15]", h[:15]), ("[0:30]", h[:30])):
                checks += 1
                if w == E_S[:len(w)]:
                    hits += 1
                    print("  ANCHOR HIT %s%s base=%r" % (d, tag, b))
    print("  %d base phrases x %d digests x 2 windows = %d checks -> %d hits"
          % (len(bases), len(digests), checks, hits))
    return hits


def why_not(board: str, target: str) -> str:
    """The specific reason `target` is not an ordered subsequence of `board`."""
    absent = [c for c in target if c not in board]
    if absent:
        return "letter(s) %s absent from the board" % "".join(absent)
    prefix: list[int] = []
    for i, ch in enumerate(target):
        lo = prefix[-1] + 1 if prefix else 0
        k = board.find(ch, lo)
        if k < 0:
            first = board.find(ch)
            where = ("after cell %d (%r, which the preceding letter already used)"
                     % (prefix[-1], board[prefix[-1]]) if prefix else
                     "at its only cell %d" % first)
            return "%r cannot be placed %s; its only cell is %d" % (ch, where, first)
        prefix.append(k)
    return "matches"


def part_b() -> int:
    print("\nPART B - BOARD REACHABILITY  (board %r, punct at %s)" % (BOARD, PUNCT_AT))
    for i, ch in enumerate(BOARD):
        print("  cell %2d  %s   punct=%s" % (i, ch, i in PUNCT_AT))
    print()
    unreachable = 0
    for t in TARGETS:
        pos = subseq_positions(BOARD, t)
        if pos is not None:
            print("  %-13s ORDERED SUBSEQUENCE ok -> cells %s" % (t, pos))
            continue
        reason = why_not(BOARD, t)
        in_set = set(t) <= set(BOARD)
        print("  %-13s FAIL  %s  [set containment: %s]"
              % (t, reason, "yes" if in_set else "NO"))
        unreachable += 1
    print("  strict ordered reachability: %d of %d targets UNREACHABLE"
          % (unreachable, len(TARGETS)))
    for label, relax in (("QWERTY king-move", qwerty_neighbours),
                         ("VIC 3x10 king-move", vic_neighbours)):
        pool = relax(BOARD)
        for misses in (1, 2):
            reached = []
            for t in TARGETS:
                r = subseq_with_misses(pool, t, misses)
                if r is not None:
                    reached.append("%s(%d miss)" % (t, r[1]))
            print("  %s, <=%d substitution(s): reachable %s"
                  % (label, misses, reached or "NONE"))
    return 0


def main() -> int:
    hits = part_a()
    part_b()
    return 0 if hits == 0 else 1


if __name__ == "__main__":
    sys.exit(main())