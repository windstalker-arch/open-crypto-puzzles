#!/usr/bin/env python3
"""base9_number_route.py -- issue #83's "without the o it turns to base 9" reading
applied to the FULL still-undecoded streams (previous base-9 tests were on the
z-segments, or on prime-position EXTRACTS of dbbi/faed -- never on the full stream).

Method mirrors the verified z-segment decode exactly, except in base 9: map each
letter to a digit (a=1..i=9 bijective / a=0..i=8 standard), read the ENTIRE digit
string as ONE number in that base, convert to base-16 hex, hex->bytes, and try
every plausible text reading of those bytes. Also chunked (2-digit) readings and
with-stream-reversed variants. Every readable candidate is pushed through both
funded-gate oracles (small 1GSMG1JC9, dualite 17ucy1K9ZUA).

Public/authorized puzzle only. A hit is an oracle MATCH.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())
FAED = d["faed_570"].rstrip("z")
DBBI69 = d["dbbib"]
DBBI91 = Path(os.path.join(os.path.expanduser("~"), "tmp", "grid_dbbib.txt")).read_text().strip()

STREAMS = [("faed", FAED), ("dbbi69", DBBI69), ("dbbi91", DBBI91)]
MAPS = {
    "a1i9": {c: str(i + 1) for i, c in enumerate("abcdefghi")},   # digits 1..9
    "a0i8": {c: str(i) for i, c in enumerate("abcdefghi")},       # digits 0..8
}

OUT = os.path.join(os.path.expanduser("~"), "tmp", "base9_cands.txt")


def digits(stream, mp):
    return "".join(mp[c] for c in stream if c in mp)


def num_to_bytes(ndigits, base):
    n = 0
    for ch in ndigits:
        n = n * base + int(ch)
    h = format(n, "x")
    if len(h) % 2:
        h = "0" + h
    try:
        return bytes.fromhex(h)
    except ValueError:
        return None


def printable_ratio(b):
    if not b:
        return 0.0
    return sum(1 for x in b if 32 <= x < 127 or x in (10, 13, 9)) / len(b)


def readings(b):
    out = set()
    if not b:
        return out
    if printable_ratio(b) > 0.95:
        out.add(b.decode("latin1"))
    try:
        t = b.decode("utf-8")
        if all(c.isprintable() or c in "\n\r\t" for c in t):
            out.add(t)
    except UnicodeDecodeError:
        pass
    for enc in ("utf-16", "utf-16-le", "utf-16-be", "utf-32-le"):
        try:
            t = b.decode(enc)
            if printable_ratio(t.encode(enc)) > 0.9:
                out.add(t)
        except (UnicodeDecodeError, UnicodeError):
            pass
    if printable_ratio(b) > 0.7:
        out.add("".join(chr(x) if 32 <= x < 127 else "?" for x in b))
    return out


def main():
    cands = set()
    per = {}
    sr = sys.argv[1] if len(sys.argv) > 1 else "gen"
    if sr == "gen":
        for sname, stream in STREAMS:
            for mname, mp in MAPS.items():
                ds = digits(stream, mp)
                base = 9
                for rname, nds in (("fwd", ds), ("rev", ds[::-1])):
                    b = num_to_bytes(nds, base)
                    if b is None:
                        continue
                    for text in readings(b):
                        cands.add(text)
                    # 2-digit chunks as base-9 -> chr  (valid only for a0i8 map)
                    if mname == "a0i8":
                        out = "".join(chr(int(nds[i:i+2], 9)) for i in range(0, len(nds) - 1, 2))
                        cands.add(out)
                        out26 = "".join(chr(ord("a") + (int(nds[i:i+2], 9) % 26))
                                        for i in range(0, len(nds) - 1, 2))
                        cands.add(out26)
        with open(OUT, "w") as f:
            for c in sorted(cands):
                if 4 <= len(c) <= 3000:
                    f.write(c + "\n")
            f.write(hashlib.sha256((DBBI91 + FAED).encode()).hexdigest() + "\n")
        print(f"[base9] {sum(len(s) for s in STREAMS)} stream-chars; "
              f"{len(cands)} unique candidates -> {OUT}")
        return

    oracle = os.path.join(ROOT, "tools", "oracle.py" if sr == "small" else "oracle_dualite.py")
    r = subprocess.run([sys.executable, oracle, "--stdin"],
                       input=Path(OUT).read_bytes(), capture_output=True)
    lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
    hits = [ln for ln in lines if ln.startswith("MATCH")]
    print(f"[base9][{sr}] oracle lines={len(lines)} MATCH={len(hits)}")
    for h in hits[:10]:
        print("  HIT:", h)


if __name__ == "__main__":
    main()