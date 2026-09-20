#!/usr/bin/env python3
"""Three-battery run on certified faed/dbbib/285-plaintext (leads 1,2,3).

B1 (issue-#83 Lead-0 remainder via issue-#51): base-9 digit stream of the
pre-z block (faed_570, dbbib_91) under a=0..8, digitwise affine P=(A*C+B) mod 9
for all affine keys with gcd(A,9)=1 (A in {1,2,4,5,7,8}, B in 0..8), then
big-int->hex->ASCII. We first REPLAY the exact issue-#51 claim
(P=2(C-8) mod 9 === A=2,B=-8) on faed and report its bytes. Then keep, for
every affine key and stream, the byte-stream text and its hex form whenever the
byte text is printable-then-wordful, as oracle candidates.

B2 (positional 2-bit + 5-bit byte read): the certified 285-letter plaintext has
an even channel that is exactly {B,C,D,E} (2 bits/symbol) and an odd channel
with full 5x5 square positions (5 bits/symbol). Read each (even,odd) position
pair as a 7-bit value in both alignment orders and pack the 285 values to bytes
MSB-first and LSB-first; also try even-channel positions counted in row+col of
the 2x2 block. Report printable byte candidates.

B3 (interp-map first-occurrence names): prints first-occurrence orders for
faed/dbbib/z to confirm which are already covered by the canonical mapping.
Diagnostic only.
"""
import json
import os
from pathlib import Path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("OUT", "/data/data/com.termux/files/usr/tmp/opencode/lead123_cands.txt")

DATA = json.loads(Path(os.path.join(BASE, "data", "finalpage-digit-streams.json")).read_text())
SAL = json.loads(Path(os.path.join(BASE, "data", "salphaseion-streams.json")).read_text())

FAED = DATA["faed_570"].rstrip("z").lower()
DBBIB = DATA["dbbib_91"].lower()
CERT = "DBIFHCEGAKLMNOPQRSTUVWXYZ"


def num_to_bytes(digits):
    """digits: base-9 digit string -> (hex str, bytes, printability 0..1)."""
    if not digits:
        return None
    v = int(digits, 9)
    nbytes = (v.bit_length() + 7) // 8
    b = v.to_bytes(nbytes, "big")
    printable = sum(1 for c in b if 32 <= c < 127) / max(len(b), 1)
    return b.hex(), b, printable


def base9_digits(stream):
    m = {c: i for i, c in enumerate("abcdefghi")}
    return "".join(str(m[c]) for c in stream if c in m)


def affine_key_candidates(stream, label):
    D = base9_digits(stream)
    out = []
    for A in (1, 2, 4, 5, 7, 8):
        for B in range(9):
            P = "".join(str((A * int(ch) + B) % 9) for ch in D)
            r = num_to_bytes(P)
            if not r:
                continue
            h, b, printable = r
            tag = f"{label}_aff{A}_{B}"
            out.append((b, h, printable, tag))
    return out


def certified_plaintext():
    mapped = "".join({"a": "A", "b": "B", "c": "C", "d": "D", "e": "E", "f": "F",
                      "g": "G", "h": "H", "i": "I"}[c] for c in FAED)
    pg = [CERT[i * 5:(i + 1) * 5] for i in range(5)]
    pos = {CERT[i]: (i // 5, i % 5) for i in range(25)}
    combined = []
    for ch in mapped:
        r, c = pos[ch]
        combined.append(r)
        combined.append(c)
    plain = ""
    period = 570
    for start in range(0, len(combined), 2 * period):
        blk = combined[start:start + 2 * period]
        h = len(blk) // 2
        for k in range(h):
            plain += pg[blk[k]][blk[h + k]]
    assert plain[:40] == SAL["plaintext_head"], plain[:40]
    return plain


def pack7(vals):
    """vals: list of 7-bit ints -> dict of packed byte strings."""
    out = {}
    bits_msb = []
    for v in vals:
        bits_msb.extend((v >> k) & 1 for k in range(6, -1, -1))
    while len(bits_msb) % 8:
        bits_msb.append(0)
    out["msb"] = bytes(int("".join(map(str, bits_msb[i:i + 8])), 2)
                      for i in range(0, len(bits_msb), 8))
    bits_lsb = []
    for v in vals:
        bits_lsb.extend((v >> k) & 1 for k in range(7))
    while len(bits_lsb) % 8:
        bits_lsb.append(0)
    out["lsb"] = bytes(int("".join(map(str, bits_lsb[i:i + 8])), 2)
                      for i in range(0, len(bits_lsb), 8))
    return out


def b2_byte_reads():
    plain = certified_plaintext()
    even = plain[0::2]
    odd = plain[1::2]
    assert len(even) == len(odd) == 285
    assert set(even) <= set("BCDE"), set(even)

    pos = {ch: (i // 5, i % 5) for i, ch in enumerate(CERT)}

    even_maps = [
        ("c1", {"B": 0, "C": 1, "D": 2, "E": 3}),
        ("c2", {"B": 1, "C": 0, "D": 3, "E": 2}),
        ("row", {"B": 0, "C": 1, "D": 0, "E": 1}),   # row index of the 2x2 block
        ("col", {"B": 1, "C": 0, "D": 0, "E": 1}),   # col index of the 2x2 block
        ("dmaj", {"B": 3, "C": 2, "D": 1, "E": 0}),
    ]

    cands = []
    for name, evmap in even_maps:
        for align in ("even_low", "even_high"):
            vals = []
            for e, o in zip(even, odd):
                e2 = evmap.get(e, 0) & 0x3
                o5 = pos[o][0] * 5 + pos[o][1] if o in pos else 24
                o5 &= 0x1F
                vals.append((o5 << 2) | e2 if align == "even_low"
                            else (e2 << 5) | o5)
                vals[-1] &= 0x7F
            packed = pack7(vals)
            for packname, pbytes in packed.items():
                printable = (sum(1 for c in pbytes if 32 <= c < 127)
                             / max(len(pbytes), 1))
                cands.append((pbytes, f"b2_{name}_{align}_{packname}",
                              printable))
    return cands


def b3_orders():
    for name, stream in (("faed", FAED), ("dbbib", DBBIB),
                         ("z1", DATA["z_segment_1"]),
                         ("z2", DATA["z_segment_2"])):
        order = []
        for c in stream:
            if c not in order:
                order.append(c)
        print(f"  first-occurrence {name}: {''.join(order)}")


def main():
    print("== B3 first-occurrence orders (diagnostic) ==")
    b3_orders()

    print("\n== B1 affine family (issue-#51 route) ==")
    # exact issue-#51 replay first
    D = base9_digits(FAED)
    P_claim = "".join(str((2 * (int(ch) - 8)) % 9) for ch in D)
    r = num_to_bytes(P_claim)
    h, b, printable = r
    print(f"  issue#51 exact replay on faed: hex_head={h[:16]}... "
          f"printable={printable:.3f} ascii_head={b[:48]!r}")
    print("  NOTE: issue #51's claimed 'Cryptography is the practice...' "
          "does NOT reproduce on certified faed (this exact replay).")

    cands = []
    for stream_label, stream in (("faed", FAED), ("dbbib", DBBIB)):
        for b, h, printable, tag in affine_key_candidates(stream, stream_label):
            text = ""
            try:
                text = b.decode("ascii")
            except UnicodeDecodeError:
                continue
            wordy = sum(1 for c in text if c.isalpha() or c == " ") / max(len(text), 1)
            if wordy > 0.85:
                cands.append((text, tag + "_txt"))
            cands.append((h, tag + "_hex"))

    print("\n== B2 positional 2+5 bit byte reads ==")
    b2 = b2_byte_reads()
    for pbytes, tag, printable in b2:
        text = ""
        try:
            text = pbytes.decode("ascii")
        except UnicodeDecodeError:
            text = ""
        if text and text.isprintable():
            cands.append((text, tag + "_txt"))
        cands.append((pbytes.hex(), tag + "_hex"))

    dedup = {}
    for s, tag in cands:
        dedup.setdefault(s, tag)
    cands = [(s, t) for s, t in dedup.items()]
    print(f"\nB1+B2 candidate count: {len(cands)}")
    Path(OUT).write_text("\n".join(s for s, _ in cands) + "\n")
    Path(OUT.replace(".txt", "_tags.txt")).write_text("\n".join(t for _, t in cands) + "\n")
    print(f"wrote -> {OUT}")


if __name__ == "__main__":
    main()