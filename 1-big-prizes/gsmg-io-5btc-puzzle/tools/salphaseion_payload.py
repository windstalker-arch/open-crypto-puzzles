#!/usr/bin/env python3
"""Extract the SalPhaseIon <textarea> payload and its hidden binary channel.

The 2020-11-12 archived SalPhaseIon page (data/wb_dbbib-page_20201112.html) is a
single <textarea> holding space-separated single characters.  A stream of
lowercase a-i noise is interleaved through it.  Most noise bursts are 1-3
characters long, but exactly two bursts are pure a/b and byte-aligned in
length; read as bits (a=0, b=1, MSB first, 8-bit ASCII) they are clean text.

    104 bits -> "matrixsumlist"
     40 bits -> "enter"

144 bits total == 18 bytes == len("matrixsumlistenter").  No leftover bits.

Usage:
    python3 tools/salphaseion_payload.py [html] [--matrix]
"""
import re
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, os.pardir, "data", "wb_dbbib-page_20201112.html")

# The 14x14 matrix implied by A (91 chars = upper triangle incl. diagonal-free
# strict upper triangle of a 14x14 symmetric matrix, values a=1..i=9).
A = "dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe"


def payload(html_path):
    raw = open(html_path, errors="ignore").read()
    m = re.search(r"(?is)<textarea[^>]*>(.*?)</textarea>", raw)
    if not m:
        raise SystemExit("no <textarea> in %s" % html_path)
    return re.sub(r"\s+", "", m.group(1))


def ab_runs(body, min_len=1):
    return [(x.start(), x.end(), x.group()) for x in re.finditer(r"[ab]+", body)]


def bits_to_ascii(bits, zero="a", one="b"):
    """MSB-first 8-bit ASCII.  Returns (text, leftover_bit_count)."""
    v = [0 if c == zero else 1 for c in bits]
    out = []
    for i in range(0, len(v) - len(v) % 8, 8):
        n = 0
        for b in v[i:i + 8]:
            n = n * 2 + b
        out.append(chr(n) if 32 <= n < 127 else ".")
    return "".join(out), len(v) % 8


def matrix_row_sums():
    V = {c: i + 1 for i, c in enumerate("abcdefghi")}
    assert len(A) == 91, len(A)
    M = [[0] * 14 for _ in range(14)]
    k = 0
    for i in range(14):
        for j in range(i + 1, 14):
            M[i][j] = M[j][i] = V[A[k]]
            k += 1
    assert k == 91
    return M, [sum(r) for r in M]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    html = args[0] if args else DEFAULT
    body = payload(html)

    print("source          : %s" % html)
    print("textarea payload: %d chars" % len(body))
    print("A stream (head) : %s..." % body[:91])
    print()

    runs = ab_runs(body)
    total = sum(len(r) for _, _, r in runs)
    print("a/b runs        : %d  (total %d bits)" % (len(runs), total))

    channel = ""
    carried = 0
    aligned = 0
    print()
    print("byte-aligned pure a/b runs (a=0, b=1, MSB first):")
    for s, e, r in runs:
        if len(r) >= 8 and len(r) % 8 == 0:
            txt, left = bits_to_ascii(r)
            channel += txt
            carried += len(r)
            aligned += 1
            print("  off=%-5d len=%-4d leftover=%d  %r" % (s, len(r), left, txt))
    print()
    print("  others         : %d runs, all 1-3 bits (decoy noise)"
          % (len(runs) - aligned))
    print("  carried bits   : %d  = %d bytes" % (carried, carried // 8))
    print()
    print("HIDDEN COMMAND   : %r" % channel)

    if "--matrix" in sys.argv:
        M, rs = matrix_row_sums()
        print()
        print("A-matrix 14x14 row sums (a=1..i=9, a=0,b=1 forced diagonal 0):")
        print("  %s" % rs)
        print("  total = %d" % sum(rs))


if __name__ == "__main__":
    main()
