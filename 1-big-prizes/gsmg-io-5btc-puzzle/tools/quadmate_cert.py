#!/usr/bin/env python3
"""Certification of the GSMG page-2 chess position (part 7, "the buddhist move").

SOURCE
------
`data/wb_choiceisanillusion_20201112.html:55` publishes, verbatim:

    /(aBa, connected enf)
    B5KR/1r5B/6R1/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 w - - 0 1
    And now a buddhist is forced to move. What will be the next situation?

The same line of prose ends with `/(aBa, connected not enf)`, and the puzzle's
own answer form is the "avoid the mate" continuation recorded in ledger s34:

    B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 1 1   (Rc6+)

WHAT THIS TOOL ESTABLISHES
--------------------------
1. The position is legal, White to move, and Black is NOT already in check --
   so the page's "forced to move" is a real forced choice, not a position that
   was already lost.
2. Rc6+ is the UNIQUE legal move that gives check WITHOUT mating. Every one of
   the other 13 legal moves is immediate checkmate. That uniqueness is the
   certification: "avoid the mate" selects exactly one move out of fourteen, so
   the s34 answer is not one plausible reading among several, it is the only one
   consistent with the page's own "connected not enf" (not-enfolded) tag.
3. The four moves cited in discussion (Nc3#, Ng3#, Bxb7#, Rxg5#) are all mate,
   but they are four of THIRTEEN, not a distinguished set of four.
4. THE KNIGHTS ARE THE LOAD-BEARING PIECES (`--mvps`). Remove the white knights
   and NO mate survives -- not 9 of 13, none. Yet the knights supply only 4 of
   the 13, while the g6 rook supplies 8. Counting mates therefore inverts the
   result: the rook's 8 mates are all contingent on a knight already giving
   check, so the rook closes a cage the knight creates. The knights are also
   SUFFICIENT -- with both other white types removed they still deliver all 4
   (Ng3#, Nd2#, Nc3#, Nf2#), whereas rooks and bishop deliver 0 in isolation.
   That is a derived structural fact of the published position, and it is what
   makes "most valuable players" a defensible reading of the knights on the
   evidence rather than a pun.

FEN SHAPE GUARD
---------------
A hand-transcribed FEN is the obvious failure mode here, and the copy that
reached discussion was damaged twice:

    B5KR/1r5/6R1/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2w - - 01

  * rank 7 reads `1r5`, seven squares: the h7 bishop is missing. It must be
    `1r5B`, and that bishop is load-bearing -- it is part of the mate net.
  * rank 1 reads `3N1N2w`: `3N1N2` is already eight squares, so the trailing
    `w` is the side-to-move field welded onto the rank.

Either defect makes the string unparseable, so the damage is loud rather than
silent -- but a tool that merely hands the string to python-chess reports only
"expected 8 columns per row" and never says which rank is wrong. `check_shape`
below localises the fault per rank so a bad transcription is diagnosed, not just
rejected.

`--mvps` prints the necessity/sufficiency table, and `--selftest` (46 checks) proves every number printed above by re-deriving it
from the FEN, and pins both transcription defects by showing that each damaged
string is rejected for the named rank.

Read-only. 0 candidates, 0 oracle calls, no funded gate touched, no broadcast.
"""

from __future__ import annotations

import argparse
import sys

import chess

PUBLISHED = (
    "B5KR/1r5B/6R1/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 w - - 0 1"
)
DAMAGED_SHORT_RANK7 = (
    "B5KR/1r5/6R1/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 w - - 0 1"
)
DAMAGED_WELDED_SIDE = (
    "B5KR/1r5B/6R1/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2w - - 01"
)
AVOID_MATE_UCI = "g6c6"
CITED_FOUR = ("d1c3", "f1g3", "a8b7", "g6g5")


class ShapeError(ValueError):
    """A FEN position part that is not eight squares on every rank."""


def rank_widths(board_part: str) -> list[int]:
    """Square count per rank, expanding FEN run-length digits.

    Digits are single characters here; a multi-digit run is not legal FEN, so
    each digit is counted on its own rather than being joined.
    """
    widths = []
    for rank in board_part.split("/"):
        widths.append(sum(int(c) if c.isdigit() else 1 for c in rank))
    return widths


def check_shape(fen: str) -> tuple[str, list[int]]:
    """Return (board_part, widths) or raise ShapeError naming the bad ranks."""
    parts = fen.split()
    if not parts:
        raise ShapeError("empty FEN: no board part present")
    board_part = parts[0]
    widths = rank_widths(board_part)
    if len(widths) != 8:
        raise ShapeError(
            f"expected 8 ranks, found {len(widths)}: {board_part!r}"
        )
    bad = [(8 - i, w) for i, w in enumerate(widths) if w != 8]
    if bad:
        detail = ", ".join(f"rank {r} has {w}" for r, w in bad)
        raise ShapeError(f"expected 8 squares per rank -- {detail}")
    if len(parts) < 4:
        raise ShapeError(
            f"expected at least 4 FEN fields (board, side, castling, ep), "
            f"found {len(parts)}"
        )
    return board_part, widths


def load(fen: str) -> chess.Board:
    """Shape-check then parse. Never hands a malformed string to python-chess."""
    check_shape(fen)
    board = chess.Board(fen)
    return board


def strip_white(board: chess.Board, symbol: str) -> chess.Board:
    """Remove every WHITE piece of the given type, leaving the rest untouched.

    `Piece.symbol()` is UPPERCASE for white and lowercase for black, so a
    filter written as `symbol == 'n'` matches only BLACK knights. This position
    has no black knights, so that filter removes nothing and the board comes
    back unmodified -- which reads as "the knights are unnecessary" rather than
    as the bug it is. The `color` test is load-bearing, not decoration.
    """
    out = board.copy()
    for sq in list(out.piece_map()):
        piece = out.piece_at(sq)
        if piece.color == chess.WHITE and piece.symbol() == symbol:
            out.remove_piece_at(sq)
    return out


def mates_of(board: chess.Board) -> list[str]:
    out = []
    for mv in list(board.legal_moves):
        san = board.san(mv)
        after = board.copy()
        after.push(mv)
        if after.is_checkmate():
            out.append(san)
    return out


def mvps() -> dict:
    """Necessity/sufficiency of each white piece type for mating at all.

    Necessity: with this type removed, does ANY mate survive?
    Sufficiency: with the other two white types also removed, do this type's
    own mates survive?
    """
    base = load(PUBLISHED)
    full = mates_of(base)
    result = {"full": full, "rows": []}
    for symbol, name in (("N", "knights"), ("R", "rooks"), ("B", "bishops")):
        without = mates_of(strip_white(base, symbol))
        # Sufficiency means "keep ONLY this type", so remove the OTHER TWO.
        # An earlier version stripped `symbol` first and then tried to strip an
        # "other", which had already deleted the piece under test -- hence a
        # uniform 0 in the survive-alone column.
        alone_board = base
        for other in ("N", "R", "B"):
            if other != symbol:
                alone_board = strip_white(alone_board, other)
        alone = [m for m in mates_of(alone_board) if m.startswith({"N": "N", "R": "R", "B": "B"}[symbol])]
        result["rows"].append({
            "symbol": symbol,
            "name": name,
            "own": [m for m in full if m.startswith(symbol)],
            "without": without,
            "alone": alone,
            "necessary": not without,
            "sufficient": bool(alone),
        })
    return result


def report_mvps() -> dict:
    m = mvps()
    print("=== which pieces carry the mate? ===")
    print(f"full position: {len(m['full'])} mates\n")
    print(f"  {'removed':10} {'mates left':>11}  verdict")
    for r in m["rows"]:
        if r["necessary"]:
            verdict = "NECESSARY -- no mate survives without it"
        elif r["sufficient"]:
            verdict = "contributes, but mate survives without it"
        else:
            verdict = "not load-bearing on its own"
        print(f"  {r['name']:10} {len(r['without']):11}  {verdict}")
    print(f"\n  {'type':10} {'own mates':>10} {'survive alone':>14}")
    for r in m["rows"]:
        print(f"  {r['name']:10} {len(r['own']):10} {len(r['alone']):14}  {r['alone']}")
    only_n = [r for r in m["rows"] if r["necessary"]]
    print(f"\nNECESSARY types: {[r['name'] for r in only_n]}")
    print("So the knights, not the rook's 8 mates, are the position's "
          "load-bearing floor:\n  the rook's mates are contingent on a knight "
          "already checking.")
    return m


def partition_moves(board: chess.Board) -> tuple[list, list, list]:
    """Split White's legal moves into (mates, checks-not-mate, quiet).

    SAN is taken from the pre-move board; taking it after push() asserts,
    because a board already advanced one ply no longer considers the move legal.
    """
    mates, checks, quiet = [], [], []
    for mv in list(board.legal_moves):
        san = board.san(mv)
        after = board.copy()
        after.push(mv)
        if after.is_checkmate():
            mates.append((mv.uci(), san))
        elif after.is_check():
            checks.append((mv.uci(), san))
        else:
            quiet.append((mv.uci(), san))
    return mates, checks, quiet


def describe(fen: str = PUBLISHED) -> dict:
    board = load(fen)
    mates, checks, quiet = partition_moves(board)
    return {
        "fen": board.fen(),
        "valid": board.is_valid(),
        "status": int(board.status()),
        "white_to_move": board.turn == chess.WHITE,
        "black_in_check": board.is_check(),
        "legal": len(list(board.legal_moves)),
        "mates": mates,
        "checks": checks,
        "quiet": quiet,
    }


def report() -> dict:
    d = describe()
    print("=== GSMG page-2 chess position, part 7 ===")
    print(f"FEN           : {d['fen']}")
    print(f"legal board   : {d['valid']}  (status {d['status']})")
    print(f"white to move : {d['white_to_move']}")
    print(f"black in check: {d['black_in_check']}  (so the choice is real)")
    print(f"legal moves   : {d['legal']}")
    print(f"\ncheckmates    : {len(d['mates'])}")
    for u, s in d["mates"]:
        print(f"   {u:6} {s}")
    print(f"\nchecks, NOT mate: {len(d['checks'])}")
    for u, s in d["checks"]:
        print(f"   {u:6} {s}")
    print(f"quiet moves   : {len(d['quiet'])}")
    for u, s in d["quiet"]:
        print(f"   {u:6} {s}")
    print(f"\nthe four moves cited in discussion, all mate: "
          f"{all(any(u == c for u, _ in d['mates']) for c in CITED_FOUR)}")
    print(f"but they are 4 of {len(d['mates'])}, not a distinguished set of four.")
    print(f"\nAVOID-MATE UNIQUE: {len(d['checks']) == 1 and d['checks'][0][0] == AVOID_MATE_UCI}")
    print(f"  {AVOID_MATE_UCI} {d['checks'][0][1] if d['checks'] else '-'} is the "
          f"only check that does not mate.")
    after = load(PUBLISHED)
    after.push(chess.Move.from_uci(AVOID_MATE_UCI))
    print(f"  resulting FEN: {after.fen()}")
    return d


def selftest() -> int:
    failures = 0
    checks = 0

    def want(cond: bool, label: str) -> None:
        nonlocal failures, checks
        checks += 1
        if not cond:
            failures += 1
            print(f"  FAIL {label}")

    d = describe()

    # 1. shape and turn
    want(d["valid"], "published FEN is a legal position")
    want(d["status"] == 0, "board status is 0 / no problem")
    want(d["white_to_move"], "it is White to move as the page states")
    want(not d["black_in_check"], "Black is not already in check")

    # 2. the census itself
    want(d["legal"] == 14, f"14 legal moves, got {d['legal']}")
    want(len(d["mates"]) == 13, f"13 checkmates, got {len(d['mates'])}")
    want(len(d["checks"]) == 1, f"1 check-not-mate, got {len(d['checks'])}")
    want(len(d["quiet"]) == 0, f"0 quiet moves, got {len(d['quiet'])}")
    want(
        len(d["mates"]) + len(d["checks"]) + len(d["quiet"]) == d["legal"],
        "the three buckets partition the legal moves",
    )

    # 3. the certification: exactly one avoid-mate move, and it is Rc6+
    want(
        len(d["checks"]) == 1 and d["checks"][0][0] == AVOID_MATE_UCI,
        "the unique non-mating check is g6c6",
    )
    want(d["checks"][0][1] == "Rc6+", "and it is Rc6+ in SAN")
    after = load(PUBLISHED)
    after.push(chess.Move.from_uci(AVOID_MATE_UCI))
    want(after.turn == chess.BLACK, "after Rc6+ it is Black to move")
    want(after.is_check(), "after Rc6+ Black is in check")
    want(not after.is_checkmate(), "after Rc6+ Black is not mated")
    want(
        after.fen() == "B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 1 1",
        "and the resulting FEN matches ledger s34's answer form",
    )

    # 4. the four cited moves are mates, but are not special
    for u in CITED_FOUR:
        want(
            any(u == m[0] for m in d["mates"]),
            f"cited move {u} is checkmate",
        )
    want(
        len(CITED_FOUR) < len(d["mates"]),
        "the four cited moves are a proper subset of all mates",
    )
    for u, _s in d["mates"]:
        b = load(PUBLISHED)
        b.push(chess.Move.from_uci(u))
        want(b.is_checkmate(), f"{u} really is mate when replayed independently")

    # 5. shape guard: both damaged transcriptions are caught, and named
    try:
        load(DAMAGED_SHORT_RANK7)
        failures += 1
        checks += 1
        print("  FAIL short rank-7 FEN was accepted")
    except ShapeError as e:
        checks += 1
        if "rank 7 has 7" not in str(e):
            failures += 1
            print(f"  FAIL rank-7 defect not localised: {e}")
    try:
        load(DAMAGED_WELDED_SIDE)
        failures += 1
        checks += 1
        print("  FAIL welded-side-to-move FEN was accepted")
    except ShapeError as e:
        checks += 1
        if "rank 1 has 9" not in str(e):
            failures += 1
            print(f"  FAIL welded-rank defect not localised: {e}")

    # 6. guard is width-based, so a repaired transcription is accepted
    try:
        load(PUBLISHED)
        checks += 1
    except ShapeError as e:
        failures += 1
        checks += 1
        print(f"  FAIL published FEN rejected: {e}")

    # 7. necessity/sufficiency of each piece type, plus the symbol-case trap
    m = mvps()
    by = {r["symbol"]: r for r in m["rows"]}
    want(by["N"]["necessary"], "removing the knights leaves NO mate")
    want(by["N"]["without"] == [], "and the surviving-mate list is empty")
    want(not by["R"]["necessary"], "the rooks are NOT necessary (8 survive)")
    want(not by["B"]["necessary"], "the bishop is NOT necessary (4 survive)")
    want(by["N"]["sufficient"], "the knights are sufficient for their 4 mates")
    want(
        by["N"]["alone"] == ["Ng3#", "Nd2#", "Nc3#", "Nf2#"],
        "knights alone mate exactly on g3, d2, c3, f2",
    )
    want(
        not by["R"]["sufficient"] and not by["B"]["sufficient"],
        "neither rooks nor bishop can mate without the knights",
    )
    want(
        sum(len(r["own"]) for r in m["rows"]) == len(m["full"]),
        "own-mate counts partition the 13 mates",
    )
    # the case trap: a lowercase-only filter must be shown to remove nothing
    base = load(PUBLISHED)
    lowercase = base.copy()
    for sq in list(lowercase.piece_map()):
        piece = lowercase.piece_at(sq)
        if piece.symbol() == "n":
            lowercase.remove_piece_at(sq)
    want(
        len(mates_of(lowercase)) == len(m["full"]),
        "filtering symbol=='n' removes nothing (no black knights) -- the trap",
    )
    want(
        len(mates_of(strip_white(base, "N"))) == 0,
        "the colour-aware strip does remove the knights",
    )

    print()
    if failures:
        print(f"SELFTEST FAIL -- {failures} of {checks} checks failed")
        return 1
    print(f"SELFTEST PASS -- {checks}/{checks} checks")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--mvps", action="store_true",
                    help="piece necessity/sufficiency table for mating")
    ap.add_argument("--fen", help="check a FEN for shape instead of reporting")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.mvps:
        report_mvps()
        return 0
    if args.fen:
        try:
            board, widths = check_shape(args.fen)
        except ShapeError as e:
            print(f"SHAPE FAIL: {e}")
            return 1
        print(f"SHAPE OK: 8 ranks x 8 squares; board part {board}")
        print(f"widths: {widths}")
        return 0
    report()
    return 0


if __name__ == "__main__":
    sys.exit(main())