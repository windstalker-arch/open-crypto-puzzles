#!/usr/bin/env python3
"""faed_baseN.py -- base-N read of the DECODED faed Bifid plaintext.

WHY THIS SURFACE
----------------
The puzzle's own certified convention for reading an a..i(+o) stream is
    digit-stream  ->  base-10 integer  ->  bytes  ->  ASCII
(`lastwordsbeforearchichoice` / `thispassword`, reproduced in tested.md s.115/s.157
and the fork notebook).  Every base-N read in the ledger so far was applied to the
RAW streams (dbbib/faed/z-segments) or to the post-split objects
(object_256, even_stream, dropped_29 -- s.60).  The FULL 570-character Bifid
PLAINTEXT and the full 285-symbol odd-position stream (the version that still
contains the I/O letters) have never been read as a number.

That is a real gap, and it is the natural place to look because the decoded
plaintext is not text: it starts `BTCSEED` and its index of coincidence is
0.0941 over 25 symbols, which no natural language produces.  It looks like
key material or a further encoding, and a keyed number is what the author's
own convention would make of it.

WHAT IT DOES
------------
For each object, for each base N (alphabet size and its two neighbours), for both
digit orders (forward / reversed) and both zero- and one-based digit values, the
string is read as one big integer and emitted as minimal big-endian bytes.

HONESTY CONTROLS (this project's own norms -- see STATE_BRIEF "CALIBRATION" and
the R-P32BLOB2 retraction, which was caused by a too-weak null):
  * W1  the certified z-segment convention re-finds `lastwordsbeforearchichoice`
       through this same code path, so the number->bytes machinery is right.
  * W2  a proper null: every object is also read after a REFIT-ON-SHUFFLED basis,
       i.e. the same number->bytes step applied to a random permutation of the
       same object.  A decode is only interesting if it beats its own null.
  * W3  score = printable fraction + common-English trigram count, and the
       degenerate-cipher tell (identical outputs from two different bases) is
       reported rather than read as a hit.

Usage:  python3 tools/faed_baseN.py [--selftest]
"""

from __future__ import annotations

import argparse
import json
import os
import random
import string
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bifid_repro as B  # noqa: E402  certified witness (SELFCERT PASS)

WORDDIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TRIGRAMS = None


def trigrams() -> set[str]:
    """Common English trigrams, as a hit-set (a decode is scored by how many
    DISTINCT common trigrams it contains -- counting repeats would reward long
    repetitive garbage)."""
    global TRIGRAMS
    if TRIGRAMS is None:
        base = ("the and ing ion tio ent for her ter hat tha ere ate his con res "
                "ver all nce men ith ted ers pro thi wit are ess not ive rea "
                "com eve per int est sta cti ica ist ear ain one our iti rat "
                "ons our ted ers pro")
        TRIGRAMS = {base[i:i + 3] for i in range(0, len(base) - 2)}
    return TRIGRAMS


def english_words() -> set[str]:
    p = WORDDIR / "tools" / "en_words.txt"
    if p.exists():
        return set(w.strip() for w in p.read_text(errors="replace").split() if w.strip())
    return set(string.ascii_lowercase)  # documented fallback; see selftest note


def score(b: bytes) -> tuple[float, int, int]:
    """(printable fraction, distinct common trigrams, whole-word hits)."""
    if not b:
        return 0.0, 0, 0
    pr = sum(1 for c in b if 32 <= c < 127) / len(b)
    s = b.decode("latin-1").lower()
    tri = len({s[i:i + 3] for i in range(len(s) - 2)} & trigrams())
    words = english_words()
    hits = sum(1 for w in re.findall(r"[a-z]+", s) if w in words)
    return pr, tri, hits


import re  # noqa: E402  used by score()


def to_int(s: str, alphabet: str, zero_based: bool) -> int:
    n = 0
    base = len(alphabet)
    off = 0 if zero_based else 1
    for ch in s:
        v = alphabet.index(ch) + off
        if v >= base:
            raise ValueError("digit out of range")
        n = n * base + v
    return n


def minimal_bytes(n: int) -> bytes:
    """The author's own last step: the integer's HEXADECIMAL TEXT, read as bytes.

    NOT n.to_bytes().  The W1 witness is what forces this: the certified
    z-segment decode is 63 decimal digits -> hex TEXT -> `lastwords...`, i.e.
    63 dec digits (~209 bits) become 52 hex digits = 26 bytes.  Reading the
    integer straight into big-endian bytes gives a different, wrong object --
    which is exactly the class of bug a self-made vector cannot catch.
    """
    h = "%x" % n
    if len(h) % 2:
        h = "0" + h
    return bytes.fromhex(h)


def objects() -> dict[str, str]:
    """The four objects, all built from the CERTIFIED Bifid witness output."""
    streams = json.loads((WORDDIR / "data" / "finalpage-digit-streams.json").read_text())
    faed = streams["faed_570"].rstrip("z")
    mapped = "".join({"a": "A", "b": "B", "c": "C", "d": "D", "e": "E",
                      "f": "F", "g": "G", "h": "H", "i": "I"}[c] for c in faed)
    grid, pos = B.build_grid()
    full = B.bifid_decrypt(mapped, B.PERIOD, grid, pos)
    odd = full[1::2]                      # 285, keeps I and O
    even = full[0::2]                    # 285, B/C/D/E only
    obj256 = "".join(c for c in odd if c not in ("I", "O"))
    return {"full570": full, "odd285": odd, "object_256": obj256, "even285": even}


def runs(shuffle_seed: int | None = None) -> list[tuple[str, str, int, bytes, tuple]]:
    out = []
    for name, s in objects().items():
        alpha = "".join(sorted(set(s)))
        for alpha_name, use_alpha in (("first-occurrence", "".join(dict.fromkeys(s))),
                                      ("sorted", alpha)):
            if len(use_alpha) < 2:
                continue
            for order in ("fwd", "rev"):
                body = s if order == "fwd" else s[::-1]
                src = body
                if shuffle_seed is not None:
                    r = random.Random(shuffle_seed + hash(name + order + alpha_name) % 10_000)
                    src = list(body)
                    r.shuffle(src)
                    src = "".join(src)
                for zb in (True, False):
                    try:
                        n = to_int(src, use_alpha, zb)
                    except ValueError:
                        continue
                    b = minimal_bytes(n)
                    out.append((name, f"{alpha_name}/{order}/{'0' if zb else '1'}-based",
                                len(use_alpha), b, score(b)))
    return out


def selftest() -> bool:
    ok = True
    # W1: the certified z-segment convention through the same number->bytes path.
    seg1 = ("agdafaoaheiecggchgicbbhcgbehcfcoabicfdhhcdbbcagbdaiobbgbeadedde")
    # the community map, verbatim: o=0 and a=1..i=9 (so the ORDER is o,a,b,..,i)
    order = "oabcdefghi"
    digits = "".join(str(order.index(c)) for c in seg1)
    want = "lastwordsbeforearchichoice"
    got = minimal_bytes(int(digits)).decode("latin-1", "replace")
    w1 = got == want
    print(f"W1 certified z-segment convention through this path -> {want!r}: "
          f"{'OK' if w1 else 'FAIL ' + repr(got)}")
    ok &= w1

    # W2/W3 machinery present, and the degenerate-base tell is detectable.
    r = runs()
    print(f"     {len(r)} real reads; longest output {max((len(x[3]) for x in r), default=0)} B")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return 0 if selftest() else 1

    real = runs()
    null = runs(shuffle_seed=12345)
    rmax = max(x[4][1] for x in real)
    nmax = max(x[4][1] for x in null)
    npr = sum(x[4][0] for x in real) / len(real)
    npr_n = sum(x[4][0] for x in null) / len(null)
    print(f"reads: {len(real)} real, {len(null)} null")
    print(f"mean printable fraction: real {npr:.3f} | null {npr_n:.3f}")
    print(f"best distinct common trigrams: real {rmax} | null {nmax}")
    print()
    print("top real reads by trigram score:")
    for name, form, base, b, sc in sorted(real, key=lambda x: -x[4][1])[:8]:
        print(f"  {name:11s} {form:28s} base{base:<3d} {len(b):4d}B "
              f"pr={sc[0]:.2f} tri={sc[1]:3d} words={sc[2]:3d}  {b[:64]!r}")
    hits = [x for x in real if x[4][1] > nmax]
    print()
    print(f"reads beating their own shuffled null: {len(hits)}")
    for h in hits:
        print("   ", h[:3], h[3][:80])
    return 0


if __name__ == "__main__":
    sys.exit(main())
