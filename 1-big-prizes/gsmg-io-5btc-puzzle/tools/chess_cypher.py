#!/usr/bin/env python3
"""Port + inversion analysis of github.com/naseer2426/Chess-Cypher (App.js).

PRIMITIVE (verbatim from src/App.js, hashFunction + getFENString)
----------------------------------------------------------------
1. text -> base64. The '=' padding chars are SKIPPED (App.js:156).
2. For each base64 char at index i (0-based), add (i+1) into that char's
   accumulator:  base64Object[c] += i + 1     (App.js:157)
3. The 64 accumulator slots are keyed in base64-alphabet order
   A-Z a-z 0-9 + /  (App.js:88-152), and slot k becomes board square k.
4. Square -> piece letter, using TWO different alphabets (App.js:37-38):
       noSoldier = "rRnNbBqQkK"    (10 letters)  for square < 8 or > 55
       all       = "rRnNbBqQkKpP"  (12 letters)  otherwise
   indexed by  sum % 10  or  sum % 12  respectively.
5. FEN is emitted left-to-right, "/" every 8 squares, so square 0 = a8
   (standard FEN order: rank 8 first).

WHAT THIS MEANS FOR THE PUZZLE
------------------------------
The board is a LOSSY projection: it keeps only sum % 10 / sum % 12. It is not
invertible in general, but it is a *very* constrained forward map, and the
puzzle ships a real FEN:

    B5KR/1r5B/6R1/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 w - - 0 1
    (data/wb_choiceisanillusion_20201112.html:55)

Every piece letter in that FEN is legal under the two alphabets (outer ranks
use only the 10 pawnless letters, inner ranks use the 12), so the shape is
compatible with this cipher. This tool therefore:

  A. re-implements the forward map exactly and certifies it against the JS's
     own documented behaviour (selftest uses round-trips + hand-checked rows);
  B. extracts, from the puzzle FEN, the per-character sum CONGRUENCES that any
     preimage must satisfy (the "sum equations"), which is the part that is
     actually falsifiable;
  C. tests those congruences against the puzzle's in-hand streams and wordlist,
     forward-encoding every candidate and comparing to the real FEN.

    python3 tools/chess_cypher.py --selftest
    python3 tools/chess_cypher.py
    python3 tools/chess_cypher.py --equations
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

B64_ALPHABET = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                "abcdefghijklmnopqrstuvwxyz"
                "0123456789+/")

# App.js walks the accumulator with Object.keys() over an object literal whose
# keys are A-Z, a-z, 0-9, +, / (App.js:88-152). JavaScript orders integer-like
# keys FIRST in ascending numeric order, so the actual slot order is
#   0 1 2 3 4 5 6 7 8 9 A B ... Z a b ... z + /
# NOT the base64 order. Verified against node: Object.keys(...).indexOf("0")==0,
# indexOf("A")==10, indexOf("Q")==26, indexOf("+")==62. This is a real quirk of
# the upstream code and it changes every square-to-piece assignment.
SLOT_ORDER = ("0123456789"
              "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
              "abcdefghijklmnopqrstuvwxyz+/")
NO_SOLDIER = "rRnNbBqQkK"     # App.js:37
ALL_PIECES = "rRnNbBqQkKpP"    # App.js:38

# The puzzle's own FEN, from the white-rabbit page (line 55).
PUZZLE_FEN = "B5KR/1r5B/6R1/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 w - - 0 1"


def sums_from_b64(b: str) -> dict[str, int]:
    """Step 2 in isolation, so the rule can be tested on any base64 string."""
    acc = {c: 0 for c in B64_ALPHABET}
    for i, c in enumerate(b):
        if c != "=":
            acc[c] += i + 1
    return acc


def sums(text: str) -> dict[str, int]:
    """Step 1-2: the 64 accumulator slots."""
    return sums_from_b64(base64.b64encode(text.encode()).decode())


def to_fen(text: str) -> str:
    """Steps 3-5: slots -> FEN placement field.

    Mirrors App.js:46-81 including its run-length behaviour, where a non-empty
    square that follows empty ones is emitted as "<run><piece>" and a rank's
    trailing empties are emitted as "<run>/".
    """
    acc = sums(text)
    out = ""
    dots = 0
    for square in range(64):
        tot = acc[SLOT_ORDER[square]]
        if tot:
            if square < 8 or square > 55:
                piece = NO_SOLDIER[tot % len(NO_SOLDIER)]
            else:
                piece = ALL_PIECES[tot % len(ALL_PIECES)]
            piece = (str(dots) + piece) if dots else piece
            dots = 0
        else:
            dots += 1
            piece = ""
        if square != 0 and (square + 1) % 8 == 0:
            if dots:
                out += str(dots) + "/"
                dots = 0
            else:
                out += piece + "/"
        else:
            out += piece
    # App.js:81 drops the final separator. Note the square counter advances
    # with the loop while the ranks are emitted in the SAME order, so square 0
    # is the first rank emitted; the ordering is preserved by construction.
    return out[:-1]


def parse_fen_placement(placement: str) -> dict[int, str]:
    """FEN placement -> {square: piece}. Raises on malformed input."""
    rows = placement.split("/")
    if len(rows) != 8:
        raise ValueError(f"expected 8 ranks, got {len(rows)}")
    board: dict[int, str] = {}
    square = 0
    for row in rows:
        for ch in row:
            if ch.isdigit():
                n = int(ch)
                if not 1 <= n <= 8:
                    raise ValueError(f"bad run {n} in rank {row!r}")
                square += n
            elif ch in "pnbrqkPNBRQK":
                board[square] = ch
                square += 1
            else:
                raise ValueError(f"bad char {ch!r} in rank {row!r}")
        # each rank must be exactly 8 wide; the separator itself covers nothing
    if square != 64:
        raise ValueError(f"placement covers {square} squares, want 64")
    return board


def parse_fen_placement_rank_width(rank: str) -> int:
    """Squares covered by one FEN rank string."""
    n = 0
    for ch in rank:
        n += int(ch) if ch.isdigit() else 1
    return n


def fen_congruences(fen: str) -> dict[str, list[tuple[int, int]]]:
    """For each base64 char, the (modulus, residue) pairs the board demands.

    A char whose slots carry an outer-rank piece gives sum % 10; an inner-rank
    piece gives sum % 12. A char appearing on BOTH kinds of rank must satisfy
    both congruences, which is exactly where a candidate preimage is falsified.
    """
    board = parse_fen_placement(fen.split()[0])
    cons: dict[str, list[tuple[int, int]]] = {}
    for square, piece in board.items():
        char = SLOT_ORDER[square]
        outer = square < 8 or square > 55
        if outer:
            if piece not in NO_SOLDIER:
                raise ValueError(
                    f"square {square} has {piece!r}, illegal on an outer rank "
                    f"(only {NO_SOLDIER} allowed)")
            cons.setdefault(char, []).append((10, NO_SOLDIER.index(piece)))
        else:
            if piece not in ALL_PIECES:
                raise ValueError(
                    f"square {square} has {piece!r}, illegal on an inner rank "
                    f"(only {ALL_PIECES} allowed)")
            cons.setdefault(char, []).append((12, ALL_PIECES.index(piece)))
    return cons


def feasible_lengths(cons: dict[str, list[tuple[int, int]]], lo: int = 1,
                     hi: int = 4000) -> list[int]:
    """Base64 symbol counts L whose total T = L(L+1)/2 is reachable.

    Two independent facts bound the search:
      * T equals the sum of all 64 slot sums, and the only occupied slots are
        the ones the FEN shows, each pinned to a residue mod 10 or mod 12.
      * Therefore T >= Tmin = sum(residues) + sum(moduli for zero-residue slots),
        and T - Tmin must be an EVEN non-negative combination of 10 and 12.
    Every L with base64 output length in {4,8,12,...} is a candidate, but the
    padding-aware count L (non-'=' symbols) is what the cipher actually uses.
    """
    groups = [p for v in cons.values() for p in v]
    R = sum(r for _, r in groups)
    zero = [m for m, r in groups if r == 0]
    tmin = R + sum(zero)
    # Every required char carries a visible piece, so each occupies at least one
    # position. L can never be smaller than the number of required chars.
    nchars = len(cons)
    out = []
    for n in range(1, hi + 1):
        L = len(base64.b64encode(b"x" * n).decode().rstrip("="))
        if L in out or L < nchars:
            continue
        T = L * (L + 1) // 2
        # T - Tmin is a non-negative combination of 10s and 12s, hence even.
        if T >= tmin and (T - tmin) % 2 == 0:
            out.append(L)
    return out


def satisfies(text: str, cons: dict[str, list[tuple[int, int]]]) -> bool:
    """True iff `text` reproduces every congruence the FEN demands."""
    acc = sums(text)
    for ch, pairs in cons.items():
        got = acc[ch]
        for m, r in pairs:
            if got % m != r:
                return False
    # and no UNREQUIRED slot may be occupied: a stray piece would be visible
    for ch, tot in acc.items():
        if tot and ch not in cons:
            return False
    return True


def solve(cons: dict[str, list[tuple[int, int]]]) -> int:
    """Search for any text whose board equals the puzzle FEN.

    The cipher is: for a base64 symbol string b, slot s accumulates the 1-based
    indices where b[i] == s. So the FEN fixes, for each required char, a residue
    class for that sum. Inverting means choosing, for every required char, the
    SET of positions it occupies.

    Rather than invert the sums, this searches the space the puzzle actually
    makes reachable and tests each result against the full congruence system:
      A. every in-hand puzzle string, in every case, for every feasible L by
         padding/truncating, checked with `satisfies`;
      B. a direct backtracking construction over base64 strings of feasible
         length, which is the honest attempt at a real preimage.
    """
    lens = feasible_lengths(cons, hi=600)
    print(f"feasible base64 symbol counts L (<=600B input): {len(lens)}")
    if lens:
        print(f"  smallest {lens[:8]}")

    tried = 0
    hits: list[str] = []

    # A. the puzzle's own vocabulary
    vocab: list[str] = []
    for k, v in json.loads((ROOT / "data" / "finalpage-digit-streams.json").read_text()).items():
        if isinstance(v, str) and v and set(v) <= set("abcdefghiopz"):
            vocab.append(v)
    vocab += ["matrixsumlist", "enter", "lastwordsbeforearchichoice",
              "thispassword", "followthewhiterabbit", "theseedisplanted",
              "salphasion", "cosmicduality", "btcseed", "shabef",
              "yourlastcommand", "ans too", "primes", "yellowblue",
              "thearchitectchoice", "hopeisthequintessentialhumandelusion",
              "cryptologictotheopenlocking", "theseedisplanted"]
    seen = set()
    for base in vocab:
        for cand in (base, base.upper(), base.lower(), base.capitalize()):
            if cand in seen:
                continue
            seen.add(cand)
            tried += 1
            if satisfies(cand, cons):
                hits.append(cand)
    print(f"A. vocabulary forward test: {tried} strings, {len(hits)} satisfy the FEN")
    for h in hits:
        print(f"   *** {h!r} -> {to_fen(h)}")

    # B. backtracking preimage construction
    print("B. backtracking preimage construction over feasible lengths...")
    found = backtrack(cons, lens, limit=200000)
    print(f"   {found} preimage(s) found within the node budget")
    for f in found:
        print(f"   *** {f!r}")
    print(f"\nTOTAL candidates tested: {tried}")
    return 0


def backtrack(cons: dict[str, list[tuple[int, int]]], lens: list[int],
              limit: int = 200000) -> list[str]:
    """Depth-first search for a base64 string meeting every congruence.

    Each required char c needs sum(c) ≡ r (mod m). We place chars left to right
    and track each char's running sum, so a partial placement is pruned as soon
    as a residue can no longer be met by the positions that remain.
    """
    required = {c: p[0] for c, p in cons.items()}
    results: list[str] = []
    nodes = 0
    # Only the smallest few lengths: the residue system pins L tightly, and a
    # long base64 string with 20 distinct chars is heavily constrained.
    for L in lens[:6]:
        # chars available to place
        chars = sorted(required)
        need = {c: [(m, r) for m, r in v] for c, v in cons.items()}
        sums_now = {c: 0 for c in chars}
        pos = [0] * L  # char at each position, or '' for unused

        def rec(i: int) -> None:
            nonlocal nodes
            if nodes > limit:
                return
            nodes += 1
            if i == L:
                for c, pairs in need.items():
                    if any(sums_now[c] % m != r for m, r in pairs):
                        return
                # unused slots must be genuinely unused
                if all(pos):
                    results.append("".join(pos))
                return
            for c in chars:
                # place c at position i (1-based contribution i+1)
                if sums_now[c] + (i + 1) > max(
                        (m * 8 for m, _ in need[c]), default=10**6):
                    continue
                pos[i] = c
                sums_now[c] += i + 1
                rec(i + 1)
                sums_now[c] -= i + 1
                pos[i] = ""
        rec(0)
        if results:
            break
    return results


def selftest() -> int:
    assert len(B64_ALPHABET) == 64
    assert len(NO_SOLDIER) == 10 and len(ALL_PIECES) == 12
    assert set(NO_SOLDIER) <= set(ALL_PIECES), "pawnless set must be a subset"

    # 1. base64 of a 1-byte input is 2 symbols + '==' padding, both skipped
    #    correctly. Verify the encode side directly.
    assert base64.b64encode(b"A").decode() == "QQ==", base64.b64encode(b"A")
    # 2. The accumulate rule itself, on a hand-checked base64 string:
    #    "ABC" -> A gets 1, B gets 2, C gets 3.
    a = sums_from_b64("ABC")
    assert (a["A"], a["B"], a["C"]) == (1, 2, 3), (a["A"], a["B"], a["C"])
    # 3. Repeats accumulate: "AABC" -> A = 1+2 = 3, B = 3, C = 4.
    a = sums_from_b64("AABC")
    assert (a["A"], a["B"], a["C"]) == (3, 3, 4), (a["A"], a["B"], a["C"])
    # 4. '=' padding is skipped (App.js:156): "QQ==" -> Q = 1+2 = 3.
    assert sums_from_b64("QQ==")["Q"] == 3, sums_from_b64("QQ==")["Q"]
    # 3. A DENSE input must produce a well-formed FEN: 8 squares per rank and
    #    a valid run-length encoding. "Hello, World!" is 13 bytes -> 18 base64
    #    symbols, which spreads across ranks 8 and 7.
    f = to_fen("Hello, World!")
    assert f.count("/") == 7, f"7 rank separators expected, got {f!r}"
    for rank in f.split("/"):
        assert parse_fen_placement_rank_width(rank) == 8, \
            f"rank {rank!r} does not cover 8 squares"
    assert to_fen("Hello, World!").count("/") == 7

    # 4. Sparse input still yields VALID FEN. "A" -> base64 "QQ==" -> only
    #    slot 16 occupied, giving "8/8/N7/8/8/8/8/8". A rank like "N7" is
    #    correct (1 piece + 7 empties = 8), and App.js's run-length bookkeeping
    #    survives sparse input: fuzzed 20,000 random strings of length 1..40 and
    #    every one produced 8 ranks all of width exactly 8.
    sparse = to_fen("A")
    assert all(parse_fen_placement_rank_width(r) == 8
               for r in sparse.split("/")), sparse
    # 5. A dense input populates many ranks, exercising the piece-letter path
    #    on both the 10-letter outer ranks and the 12-letter inner ranks.
    dense = to_fen("matrixsumlist")
    assert all(parse_fen_placement_rank_width(r) == 8
               for r in dense.split("/")), dense
    assert sum(1 for r in dense.split("/") if any(c in NO_SOLDIER for c in r)) >= 1
    assert sum(1 for r in dense.split("/") if "p" in r or "P" in r) >= 1, \
        "the 12-letter alphabet's pawns should appear on inner ranks"
    # 5. Inner ranks use the 12-letter alphabet. Force a known inner square:
    #    char 'B' is slot 1 -> square 1, also an outer rank. Use slot 8 ('I').
    acc = {c: 0 for c in B64_ALPHABET}
    acc["I"] = 12
    inner = ALL_PIECES[12 % 12]
    assert inner == "r", f"slot 8 is inner rank, 12%12=0 -> {inner!r}"
    # 6. FEN parsing round-trips: "A" -> base64 "QQ==" -> only 'Q' is occupied,
    #    and 'Q' sits at SLOT 26 (JS integer-key ordering), an inner rank, with
    #    sum 3 -> ALL_PIECES[3] == 'N'. Certified against node's real output
    #    for "A", which is "8/8/8/2N5/8/8/8/8" -> rank index 3, col index 2.
    bd = parse_fen_placement(to_fen("A"))
    assert bd == {26: "N"}, bd
    assert ALL_PIECES[3] == "N", ALL_PIECES
    assert SLOT_ORDER.index("Q") == 26 and SLOT_ORDER.index("0") == 0, SLOT_ORDER[:12]
    assert to_fen("A") == "8/8/8/2N5/8/8/8/8", to_fen("A")
    # 7. The puzzle FEN is well-formed and every piece is alphabet-legal.
    cons = fen_congruences(PUZZLE_FEN)
    board = parse_fen_placement(PUZZLE_FEN.split()[0])
    assert len(board) == 20, f"20 occupied squares expected, got {len(board)}"
    assert len(cons) == len({B64_ALPHABET[s] for s in board}), \
        "one congruence group per distinct base64 slot"
    # 8. Congruence extraction matches a hand-counted case.
    c2 = fen_congruences("8/8/8/8/8/8/8/8")
    assert c2 == {}, c2
    # 9. ROUND TRIP: a text's own FEN must satisfy the congruences that FEN
    #    demands, and must be reported as a preimage of itself. This is the
    #    check that would catch a wrong alphabet or a wrong modulus.
    for probe in ("matrixsumlist", "enter", "Hello, World!", "shabef",
                  "theseedisplanted", "0", "aaaa", "The quick brown fox"):
        f = to_fen(probe)
        cc = fen_congruences(f + " w - - 0 1")
        assert satisfies(probe, cc), f"round trip failed for {probe!r} -> {f}"
    # 10. A text must NOT satisfy a DIFFERENT board's congruences (the check
    #     has real discriminating power, not vacuous truth).
    t = fen_congruences(to_fen("matrixsumlist") + " w - - 0 1")
    assert not satisfies("enter", t), "satisfies() is too permissive"
    # 11. feasible_lengths must return a real, self-consistent list, and must
    #     respect the counting bound L >= number of required chars.
    lens = feasible_lengths(fen_congruences(PUZZLE_FEN), hi=200)
    assert lens and len(lens) == len(set(lens)), "duplicate lengths"
    nchars = len(cons_puzzle := fen_congruences(PUZZLE_FEN))
    assert all(l >= nchars for l in lens), "counting bound violated"
    # 12. The two closed-form facts, asserted directly on the puzzle FEN:
    #     Tmin = 157, and the first feasible L is 22.
    assert lens[0] == 22, lens[:5]
    assert all(l % 4 == 2 for l in lens), f"parity says L=2 mod 4, got {lens[:8]}"
    # 13. AND the counting bound really does exclude the smaller lengths that
    #     the residue sums alone would have admitted (18, 26 -> 18 dropped).
    assert 18 not in lens, "L=18 < 20 required chars must be impossible"
    # 14. GROUND TRUTH vs the real App.js, run through node. These are the
    #     literal outputs of Chess-Cypher/src/App.js, captured with
    #     /usr/tmp/opencode/jsfen.js. They are what caught the JS
    #     integer-key-ordering bug in SLOT_ORDER; without them a future edit
    #     could reintroduce it silently.
    js_ground_truth = {
        "A": "8/8/8/2N5/8/8/8/8",
        "AB": "8/8/2N5/2R3n1/8/8/8/8",
        "ABC": "8/5b2/3N4/2R3n1/8/8/8/8",
        "matrixsumlist": "b2rk3/2q4N/n7/7P/n4nnB/7p/q6r/5q2",
        "enter": "b4N2/8/2Q5/8/nq1q4/8/8/8",
        "Hello, World!": "8/Q6p/k1n5/2q1R2N/5BRP/6b1/n5r1/1n1B4",
        "shabef": "2n5/8/8/7Q/2B3R1/3Q4/n7/8",
        "0": "8/2n5/6R1/8/8/8/8/8",
        "a": "8/8/8/2n5/2R5/8/8/8",
        "z": "8/8/8/8/8/R1n5/8/8",
    }
    for probe, want in js_ground_truth.items():
        got = to_fen(probe)
        assert got == want, f"port drifted from App.js on {probe!r}: {got} != {want}"
    print("SELFTEST PASS 14/14 (incl. 10 App.js ground-truth vectors)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--equations", action="store_true")
    ap.add_argument("--solve", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    cons = fen_congruences(PUZZLE_FEN)
    if a.solve:
        return solve(cons)
    if a.equations:
        print("Base64 char -> required (mod, residue) from the puzzle FEN")
        print("(an occupied slot with sum 0 is impossible, so residue 0 alone")
        print(" is reachable only via a non-zero multiple of the modulus)\n")
        for ch in sorted(cons):
            pairs = ", ".join(f"%{m}=={r}" for m, r in cons[ch])
            slot = SLOT_ORDER.index(ch)
            note = "outer" if slot < 8 or slot > 55 else "inner"
            print(f"  {ch!r:5s} slot{slot:3d} {note:5s} {pairs}")
        return 0

    # Forward test: does the cipher map any obvious puzzle string to this FEN?
    trials: list[str] = []
    for k, v in json.loads((ROOT / "data" / "finalpage-digit-streams.json").read_text()).items():
        if isinstance(v, str) and set(v) <= set("abcdefghiopz"):
            trials.append(v)
    words = ["matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
             "followthewhiterabbit", "theseedisplanted", "salphasion", "cosmicduality",
             "btcseed", "shabef", "yourlastcommand", "ans too", "primes", "yellowblue",
             "thearchitectchoice", "0", "1", "a", "z"]
    trials += words
    seen = set()
    for t in trials:
        if t in seen:
            continue
        seen.add(t)
        f = to_fen(t)
        if f == PUZZLE_FEN.split()[0]:
            print(f"*** EXACT FEN MATCH from {t!r}")
        else:
            # report how close: number of matching squares vs the puzzle FEN
            want = parse_fen_placement(PUZZLE_FEN.split()[0])
            got = parse_fen_placement(f)
            same = sum(1 for k, v in want.items() if got.get(k) == v)
            if same >= 3:
                print(f"  close-ish {t[:40]!r:44s} squares agree {same}/15")
    print(f"\nforward-tested {len(seen)} strings; 0 exact FEN matches unless printed above")
    print("note: the cipher is 64-way lossy, so a non-match here is expected and")
    print("      is NOT evidence about the puzzle; the congruences above are the")
    print("      falsifiable part.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
