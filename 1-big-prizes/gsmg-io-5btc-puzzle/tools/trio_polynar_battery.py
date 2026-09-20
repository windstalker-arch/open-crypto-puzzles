#!/usr/bin/env python3
"""Trio hint-repo battery: Polynar (Phaen), sserangecoding (richgel999),
AlphabetEncoder (CypherPoet). Emits candidate answer strings.

Part A - distinctive vocabulary from the three repos.
Part B - technique: mixed-radix ("polynary") re-read of the a..i digit
streams. Unfold stream -> one big integer V (base-9), then re-read V via
repeated `% radix / radix` with a per-position radix sequence derived from
the page (row/col matrix-sums, decoded directive lengths), emitting the
recovered per-position values as letters. Also whole-number -> toBase(charset)
using the certified 3.2.2 alphabet and lowalpha (AlphabetEncoder route).

Not covered by prior rows: base9_number_route read V -> hex bytes and per-digit
mod-26; base58 sweep did V -> Base58. Per-position mixed-radix re-read and
whole-number base-27/base-26 charset emission are new.
"""
import os
import json
import sys
from pathlib import Path

CERTS = Path(os.path.expanduser("~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle"))
CERTS_ALPHA = "FUBCDORA.LETHINGKYMVPS.JQZXW"
LOWALPHA = "abcdefghijklmnopqrstuvwxyz"
CANON = {c: i for i, c in enumerate("abcdefghi")}


def fold(digits, base, little=False):
    v = 0
    it = reversed(digits) if not little else digits
    for d in it:
        v = v * base + d
    return v


def unfold_mixed(v, radix_seq, n):
    vals = []
    for i in range(n):
        r = radix_seq[i % len(radix_seq)]
        if r < 1:
            r = 9
        vals.append(v % r)
        v //= r
    return vals


def emit_letters(vals, upper=False):
    base = 65 if upper else 97
    return "".join(chr(base + x) for x in vals)


def to_charset(v, charset):
    b = len(charset)
    out = []
    while v:
        out.append(charset[v % b])
        v //= b
    return "".join(reversed(out)) or ""


def letters(d):
    return "".join(d)


def main():
    streams = {}
    d = json.loads((CERTS / "data/finalpage-digit-streams.json").read_text())
    streams["dbbib69"] = d["dbbib"]
    streams["faed570"] = d["faed_570"].rstrip("z")
    live = (CERTS / "data/live_salphaseion.txt").read_text().split()
    streams["dbbib91"] = "".join(live[:91])
    assert len(streams["faed570"]) == 570 and len(streams["dbbib91"]) == 91

    # ---- Part A: vocabulary ----
    vocab = [
        "polynar", "Polynar", "polynary", "polynarybitpacking",
        "polynarmixedradix", "polynarbitpacker", "polynarencoder",
        "composeterm", "composeweighted", "charsetsurlsafe", "charsetlowalpha",
        "theransfoldisabigintegerrans", "terminatedbasethreerun",
        "polynaryisnotencryption", "polynarbrokitzips?",
        "matrixsumlistpolynar", "faedpolynar", "polynarbasininebfixed",
        "sserangecoding", "richgel999sserangecoding", "sserangecodingmatrixsumlist",
        "rangecoderpavlovsubbotin", "24bitinterleavedrangecoder",
        "rangecodingforeightbitalphabets", "book1huffmanpackagemerge",
        "rangecoder4intercompswizzle",
        "alphabetencoder", "cypherpoetalphabetencoder",
        "alphabetencoderencodesintegersfrombasealphabets",
        "encodeintegersfrombasealphabets", "alphabettolab", "basealphabets",
        "polynarserangecodingalphabetencoder", "rangepolynarencode",
    ]

    cands = list(dict.fromkeys(vocab))

    # ---- Part B: mixed-radix re-read ----
    rows = [int(c) or 9 for c in "610876654997879"]   # 0 -> 9 (radix >=1)
    cols = [int(c) or 9 for c in "8108108736759668"]
    directs = [13, 5, 26, 12, 7, 7, 14]   # four directives + firsttint/secondanswer/yourlastcommand? keep directive cycle
    radix_seqs = {
        "rows": rows,
        "cols": cols,
        "directs": directs,
        "base26": [26],
        "base9": [9],
    }

    for name, chars in streams.items():
        n = len(chars)
        digits = [CANON[c] for c in chars]
        for little in (False, True):
            V = fold(digits, 9, little=little)
            for rn, rseq in radix_seqs.items():
                vals = unfold_mixed(V, rseq, n)
                for upper in (False, True):
                    s = emit_letters(vals, upper)
                    cands += [s, s[::-1]]
            # AlphabetEncoder/toBase route: whole integer -> certified charset and lowalpha
            cands.append(to_charset(V, CERTS_ALPHA))
            cands.append(to_charset(V, LOWALPHA))

    cands = list(dict.fromkeys(cands))
    print("\n".join(cands))


if __name__ == "__main__":
    sys.exit(main() if True else 0)