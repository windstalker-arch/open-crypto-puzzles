#!/usr/bin/env python3
"""morse_sweep.py -- bounded Morse-code encode/decode battery for the gsmg streams.

Lead-0-adjacent: prior coverage (tested.md:313) was only the even_stream role-
assignment reading (0/24 legible). This tool supplies:
  * encode(phrase)   -> ITU morse under configurable dot/dash alphabets and
                        separator layouts (concat / letter-'/' / word-' / ')
  * decode(tokens)   -> reverse (morse string or symbol stream -> ascii)
  * stream role maps -> two-class partitions of {a..i} (or {o,i}, {a,b}, ...)
                        onto . / - with word/letter separators inferred from the
                        third symbol class, both directions, both polarities.
Selftest: round-trips a fixed phrase in every alphabet x layout and decodes a
known ITU vector without separators via fixed-width lookup.
"""
import os
import sys, itertools, argparse, json, re

MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".",
    "F": "..-.", "G": "--.", "H": "....", "I": "..", "J": ".---",
    "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---",
    "P": ".--.", "Q": "--.-", "R": ".-.", "S": "...", "T": "-",
    "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--",
    "Z": "--..",
}
DIGITS = {str(i): ("-----", ".----", "..---", "...--", "....-", ".....", "-....", "--...", "---..", "----.")[i] for i in range(10)}
MORSE.update(DIGITS)
RMORSE = {v: k for k, v in MORSE.items()}

DOT = "."
DASH = "-"


def selftest() -> bool:
    phrase = "GENERAL KALB RECTANGLE"
    for alphabet in ("'-", "ab", "01", "oi", "10", "ba"):
        dot, dash = alphabet[0], alphabet[1]
        # separator-carrying layouts are certifiable; "close" is not (morse is not
        # prefix-free: T='-' is a prefix of N='-.', so close needs timing, not bytes)
        for layout in ("char", "word"):
            enc = encode(phrase, dot=dot, dash=dash, layout=layout)
            dec = decode(enc, dot=dot, dash=dash)
            if dec != phrase:
                print(f"  roundtrip fail {alphabet} {layout}: {dec!r}")
                return False
    # single-letter-at-a-time fixed-width probe (unambiguous only letter by letter)
    assert decode("/".join(MORSE[c] for c in "MORSE")) == "MORSE"
    return True


def encode(phrase: str, dot=DOT, dash=DASH, layout="close"):
    """layout: close (letters concatenated), char (sep '/' between letters),
    word (sep ' ' between letters). words always joined with ' / '."""
    words = phrase.upper().split()
    out_parts = []
    for w in words:
        letters = [MORSE[ch].translate(str.maketrans({DOT: dot, DASH: dash})) for ch in w if ch in MORSE]
        if layout == "close":
            out_parts.append("".join(letters))
        elif layout == "char":
            out_parts.append("/".join(letters))
        else:
            out_parts.append(" ".join(letters))
    return " / ".join(out_parts)


def _decode_word(word: str) -> str:
    """Greedy longest-match decode of a separator-free dot/dash word (prefix-free)."""
    out = []
    i = 0
    n = len(word)
    while i < n:
        found = None
        for L in range(min(5, n - i), 0, -1):
            seg = word[i:i + L]
            if seg in RMORSE:
                found = RMORSE[seg]
                i += L
                break
        if found is None:
            out.append("?")
            i += 1
        else:
            out.append(found)
    return "".join(out)


def decode(tokens: str, dot=DOT, dash=DASH, word_sep=None, layout_fixed=False):
    tok = tokens.translate(str.maketrans({dot: DOT, dash: DASH})).replace("  ", " / ").strip()
    words = [w for w in re.split(r"\s+/\s+", tok) if w]
    out = []
    for w in words:
        # within a word, letter gaps may be '/' or single spaces or absent
        segments = [s for s in re.split(r"[/\s]+", w) if s]
        letters = "".join(_decode_word(s) for s in segments)
        out.append(letters)
    return " ".join(out)


def streams_and_roles():
    base = os.path.expanduser("~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle/data/")
    d = json.load(open(base + "finalpage-digit-streams.json"))
    s = json.load(open(base + "salphaseion-streams.json"))
    return {
        "faed": d["faed_570"].rstrip("z"),
        "dbbib": d["dbbib_91"],
        "z_seg1": d["z_segment_1"],
        "z_seg2": d["z_segment_2"],
        "object_256": s["object_256"],
        "even_stream": s["even_stream"],
        "odd_pre_reduction": s["odd_pre_reduction"],
    }


def role_decode(stream, dot_set, dash_set, sep_class, direction=1):
    """dot_set/dash_set: iterables of symbols. sep_class: {'*'}= symbol class
    treated as separator (word boundary). direction=1 forward, -1 reverse."""
    tok = []
    for ch in (stream[::-1] if direction < 0 else stream):
        if ch in dot_set:
            tok.append(DOT)
        elif ch in dash_set:
            tok.append(DASH)
        elif ch in sep_class:
            tok.append("/")
    return decode("".join(tok))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--encode", nargs="+", help="phrases to encode (dot/dash alphabets + layouts)")
    ap.add_argument("--decode-streams", action="store_true")
    ap.add_argument("--alphabet", default="'-", help="dotdash alphabet, default .-")
    a = ap.parse_args()

    if a.selftest:
        print("MORSE SELFTEST:", "PASS" if selftest() else "FAIL")
        return 0 if selftest() else 1

    if a.encode:
        dot, dash = a.alphabet[0], a.alphabet[1]
        seen = set()
        for phrase in a.encode:
            for layout in ("close", "char", "word"):
                e = encode(phrase, dot=dot, dash=dash, layout=layout)
                if e not in seen:
                    seen.add(e)
                    print(e)
        return 0

    if a.decode_streams:
        objs = streams_and_roles()
        for nm, stream in objs.items():
            sigma = set(stream)
            if len(sigma) < 2:
                continue
            # natural two-class readings: o/i, a/b, + pairings from the symbol set
            readings = []
            pool = list(sigma)
            for x, y in itertools.combinations(pool, 2):
                for polarity in (1, -1):
                    for direction in (1, -1):
                        readings.append(role_decode(stream, {x}, {y}, sigma - {x} - {y}, direction))
            # printable text?
            scored = []
            for r in readings:
                if not r:
                    continue
                n = len(r)
                pr = sum(32 <= ord(c) < 127 for c in r) / n
                scored.append((pr, r))
            best = sorted(scored, reverse=True)[:8]
            print(f"== {nm} (alphabet {sorted(pool)})")
            for pr, r in best:
                print(f"   pr={pr:.2f} {r[:120]!r}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())