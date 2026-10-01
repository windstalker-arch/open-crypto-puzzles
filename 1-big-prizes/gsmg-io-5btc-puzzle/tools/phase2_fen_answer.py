#!/usr/bin/env python3
"""phase2_fen_answer.py -- independent re-derivation of the Phase-2 chess answer.

WHY THIS EXISTS. `R-CHAIN23-2026-09-26` (`tested.md:12315`) RESOLVED the Phase-2
FEN component: the page publishes the STARTING position
`B5KR/1r5B/6R1/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 w - - 0 1` and asks "And now a
buddhist is forced to move. What will be the next situation?"; the Phase-3
password instead carries the POST-MOVE position
`B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1`. That row argued
the second FEN is the answer to the page's question rather than a transcription
slip, and moved on. This tool re-derives the move from the STARTING position
alone, so the conclusion rests on an enumeration rather than on that argument.

THE ANSWER, AND WHY ENUMERATION IS THE POINT. Of the 14 legal moves, 13 are
checkmate. Exactly ONE is not: `Rc6+` (rook g6-c6). So the puzzle's answer is
the odd one out, and it is found by classifying all 14 rather than by guessing
one. This is also why a naive "find the mating move" search cannot find it -
every mating move ends the game immediately and is therefore wrong.

CERTIFIED GUARANTEES (`--selftest`, all must pass):
  * the page FEN is a legal position;
  * `Rc6+` is the UNIQUE non-mating legal move (13 of 14 mate);
  * playing it lands on black in check with exactly ONE legal reply;
  * the resulting placement, side-to-move, castling and en-passant fields are
    byte-identical to the FEN carried in the Phase-3 password.

DEPENDENCY NOTE. This tool imports `chess` (python-chess, verified at 1.11.2),
which is NOT in `tools/requirements.txt`. `chess_cypher.py` deliberately avoids
that dependency by parsing FEN by hand; this tool does not, because legal-move
generation and checkmate detection are the entire point and re-implementing them
would defeat the purpose. It is a tool-only dependency, not a puzzle one: no
other tool in the folder imports `chess`, and nothing else in the pipeline
depends on this file.

    python3 tools/phase2_fen_answer.py --selftest
    python3 tools/phase2_fen_answer.py
"""
from __future__ import annotations

import argparse
import sys

try:
    import chess
except ImportError:  # pragma: no cover
    print("python-chess is required for this tool: pip install chess", file=sys.stderr)
    raise

# data/wb_choiceisanillusion_20201112.html:55 -- the published STARTING position.
PAGE_FEN = "B5KR/1r5B/6R1/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 w - - 0 1"

# The FEN the Phase-3 password ends with, i.e. the position AFTER the answer.
LEDGER_FEN = "B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1"

FIELDS = ("placement", "turn", "castling", "ep", "halfmove", "fullmove")


def classify() -> tuple[list[str], list[str], int]:
    """Return (mating SANs, non-mating SANs, total legal moves)."""
    board = chess.Board(PAGE_FEN)
    mates: list[str] = []
    rest: list[str] = []
    for mv in board.legal_moves:
        san = board.san(mv)
        board.push(mv)
        (mates if board.is_checkmate() else rest).append(san)
        board.pop()
    return mates, rest, board.legal_moves.count()


def selftest() -> bool:
    ok = True

    board = chess.Board(PAGE_FEN)
    p1 = board.is_valid()
    print(f"page FEN is a legal position: {'OK' if p1 else 'FAIL'}")
    ok = ok and p1

    mates, quiet, total = classify()
    p2 = total == 14 and len(mates) == 13 and quiet == ["Rc6+"]
    print(f"legal moves {total}, mates {len(mates)}, non-mating {quiet}: "
          f"{'OK' if p2 else 'FAIL'}")
    ok = ok and p2

    # The answer must force exactly one reply, which is what makes it "the next
    # situation" rather than the end of the game.
    board.push_san(quiet[0])
    p3 = board.is_check() and board.legal_moves.count() == 1
    reply = [board.san(m) for m in board.legal_moves]
    print(f"after {quiet[0]}: black in check={board.is_check()}, "
          f"legal replies={reply}: {'OK' if p3 else 'FAIL'}")
    ok = ok and p3

    # Agreement with the Phase-3 password, field by field.
    got, want = board.fen().split(), LEDGER_FEN.split()
    p4 = got[:4] == want[:4]
    for name, a, b in zip(FIELDS, got, want):
        mark = "==" if a == b else "!="
        print(f"    {name:10s} {a:<42s} {mark} phase-3 password")
    print(f"first four fields identical: {'OK' if p4 else 'FAIL'}")
    ok = ok and p4

    # The halfmove clock is expected to differ and is NOT part of the claim: a
    # quiet rook move advances the clock 0 -> 1, and the page wrote 0. Asserted
    # so that a future change in this direction would be noticed rather than
    # quietly absorbed.
    p5 = got[4] == "1" and want[4] == "0"
    print(f"halfmove clock {got[4]} vs password {want[4]} "
          f"(quiet move; recorded as expected, not part of the match): "
          f"{'OK' if p5 else 'FAIL'}")
    ok = ok and p5

    print("SELFTEST PASS" if ok else "SELFTEST FAIL")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true",
                    help="run the certification checks")
    args = ap.parse_args()
    if args.selftest:
        return 0 if selftest() else 1

    mates, quiet, total = classify()
    print(f"Phase-2 chess question: starting position, {total} legal moves\n")
    print(f"  {len(mates)} are checkmate, {len(quiet)} is not: {quiet}\n")
    print("  mating (all WRONG -- they end the game):")
    for san in mates:
        print(f"    {san}")
    print("\n  not mating:")
    for san in quiet:
        board = chess.Board(PAGE_FEN)
        board.push_san(san)
        replies = [board.san(m) for m in board.legal_moves]
        print(f"    {san}  ->  black in check, replies {replies}")
        print(f"       {board.fen()}")
    print("\n  the Phase-3 password carries that post-move position, so the")
    print("  answer to 'what will be the next situation' is the move that does")
    print("  NOT mate. A search for a mating move cannot find it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
