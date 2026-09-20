#!/usr/bin/env python3
"""Two-prong battery from lead 0 + the certified plaintext's even/odd structure.

PART A  even/odd coordinate remerge
  The certified Bifid decode (285 letters) has even positions = {B,C,D,E} only
  and odd positions = the rest (minus I,O, the 29 dropped). Reading hypothesis:
  even stream carries one coordinate digit and odd stream the other; remerge into
  5x5 grid cells via each square under test, digits taken as keyed-alphabet
  index (mod 5) or row*5+col position, in both orientations. Only printable/
  English-looking outputs are kept as oracle candidates.

PART B  first-occurrence interpreter alphabets (visual/Lead-0 read)
  "The order the author typed the 9 symbols" = first-occurrence order in a
  stream is the closest computational proxy to a visual read. Maps distinct to
  0..8 and 1..9 (forward/reverse), applied to faed/dbbib/z as digit strings;
  digit-join and grouped-byte forms become candidates when printable words.

Every returned candidate is saved to /data/data/com.termux/files/usr/tmp/opencode/r17_cands.txt
one per line; the caller oracles them. This script itself runs no oracle.
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name):
    return json.loads(open(os.path.join(BASE, "data", name)).read())


CERT = "DBIFHCEGAKLMNOPQRSTUVWXYZ"          # certified 5x5 (I/J)
KEYD = "UAETOGKDJFHCNQLVZYRMIWPSBX"         # user key = 26-letter alphabet, first 25 used
# index position of each letter in each alphabet
CERT_POS = {ch: i for i, ch in enumerate(CERT)}
KEYD_POS = {ch: i for i, ch in enumerate(KEYD)}


def square_rows(alpha):
    n = 25
    rows = [list(alpha[i*5:(i+1)*5]) for i in range(5)]
    imp = {}
    for i in range(25):
        imp[alpha[i]] = (i//5, i % 5)
    return rows, imp


def canon_index_sentence(full, posmap):
    """285 letters -> (pos mod 5) digit string, or positional split remerge."""
    even = full[0::2]
    odd = full[1::2]
    return even, odd


def remerge_squares(full, even_map, odd_map, squares):
    """For each square, produce row-major/col-major remerges of coordinate digit pairs."""
    even = full[0::2]
    odd = full[1::2]
    assert len(even) == len(odd)
    out = []
    for name, alpha in squares.items():
        rows, imp = square_rows(alpha)
        for odd_digit_fn, even_digit_fn, label in (
                (lambda o: o % 5, lambda e: e % 5, "mod5"),
                (lambda o: o // 5, lambda e: e // 5, "div5"),
                (lambda o: o % 25, lambda e: e % 25, "pos25"),
        ):
            odd_digits = [odd_digit_fn(odd_map[c]) for c in odd if c in odd_map]
            even_digits = [even_digit_fn(even_map[c]) for c in even if c in even_map]
            if len(odd_digits) != len(even_digits):
                continue
            # (row=odd, col=even)
            s1 = "".join(rows[o][e] for o, e in zip(odd_digits, even_digits)
                         if 0 <= o < 5 and 0 <= e < 5)
            # (row=even, col=odd)
            s2 = "".join(rows[e][o] for e, o in zip(even_digits, odd_digits)
                         if 0 <= e < 5 and 0 <= o < 5)
            if s1:
                out.append((name, label + "_odd_row", s1))
            if s2:
                out.append((name, label + "_even_row", s2))
    return out


def first_occurrence_map(stream):
    order = []
    for c in stream:
        if c not in order:
            order.append(c)
    return order


def interp_candidates(streams, samefreq_okays=None):
    """Produce digit-string candidates from first-occurrence maps."""
    cands = []
    names = list(streams.keys())
    alphas = [list(range(9))]          # 0..8
    alphas.append([i+1 for i in range(9)])  # 1..9
    for name, stream in streams.items():
        order = first_occurrence_map(stream)
        seen = set()
        for base in alphas:
            for rev in (False, True):
                m = {ch: (value if not rev else 8 - index) for index, (ch, value)
                     in enumerate(zip(order, base))}
                m = {ch: m.get(ch, 0) for ch in set(stream)}
                digits = "".join(str(m[ch]) for ch in stream if ch in m)
                chord = "".join(str(d) for d in range(9))
                tag = f"fo:{name}/{'1-9' if base[0] else '0-8'}/rev={rev}"
                # digit string itself
                cands.append((digits, tag))
                # grouped bytes
                if len(digits) % 2 == 0:
                    by = bytes(int(digits[i:i+2]) for i in range(0, len(digits), 2))
                    try:
                        s = by.decode("ascii")
                        if s.isprintable():
                            cands.append((s, tag + ":bytes"))
                    except UnicodeDecodeError:
                        pass
                # first-occurrence-key string (letters of the order)
                cands.append(("".join(order), tag + ":order"))
    return cands


def printability(cands):
    out = []
    for s, tag in cands:
        if not s:
            continue
        try:
            if s.isprintable() and len(s) < 600:
                out.append((s, tag))
        except Exception:
            pass
    return out


def main():
    final = load("finalpage-digit-streams.json")
    sal = load("salphaseion-streams.json")
    faed = final["faed_570"]
    dbbib = final["dbbib_91"]
    z1 = final["z_segment_1"]
    z2 = final["z_segment_2"]

    full = faed.rstrip("z")
    mapped = "".join({"a": "A", "b": "B", "c": "C", "d": "D",
                      "e": "E", "f": "F", "g": "G", "h": "H", "i": "I"}[c] for c in full)
    # rebuild certified plaintext via bifid_decrypt (period=570) inline
    grid, pos = square_rows(CERT)
    coords = [pos[ch] for ch in mapped]
    combined = []
    for r, c in coords:
        combined.append(r)
        combined.append(c)
    plain = ""
    period = 570
    for start in range(0, len(combined), 2*period):
        block = combined[start:start + 2*period]
        h = len(block)//2
        for k in range(h):
            plain += grid[block[k]][block[h + k]]
    assert plain[:40] == sal["plaintext_head"]

    keyed_plain = "".join({"A": "U", "B": "A", "C": "E", "D": "T", "E": "O", "F": "G",
                           "G": "K", "H": "D", "I": "J", "J": "F", "K": "H", "L": "C",
                           "M": "N", "N": "Q", "O": "L", "P": "V", "Q": "Z", "R": "Y",
                           "S": "R", "T": "M", "U": "I", "V": "W", "W": "P", "X": "S",
                           "Y": "B", "Z": "X"}[c] for c in plain)

    out = []
    out += remerge_squares(plain, CERT_POS, CERT_POS, {"cert": CERT})
    out += remerge_squares(plain, KEYD_POS, KEYD_POS, {"keyd": KEYD})
    out += remerge_squares(keyed_plain, CERT_POS, CERT_POS, {"cert_on_keyed": CERT})
    out += remerge_squares(keyed_plain, KEYD_POS, KEYD_POS, {"keyd_on_keyed": KEYD})

    print("PART A coordinate remerges:")
    for name, label, s in out:
        print(f"  [{name}/{label}] {s[:60]}{'...' if len(s) > 60 else ''}")

    streams = {"faed": faed, "dbbib": dbbib, "z1": z1, "z2": z2}
    interp = interp_candidates(streams)
    print(f"\nPART B first-occurrence interpreter: {len(interp)} raw, printable:")
    printable = printability(interp)
    for s, tag in printable[:40]:
        print(f"  [{tag}] {s[:60]}")
    print(f"  ... {len(printable)} printable total")

    # assemble final candidate file: PART A printable strings + PART B printable
    cands = []
    for name, label, s in out:
        if s.isprintable() and len(s) < 600:
            cands.append((s, f"A:{name}:{label}"))
    cands += [(s, tag) for s, tag in printable]
    # dedup keep tag
    d = {}
    for s, tag in cands:
        d.setdefault(s, tag)
    cands = [(s, tag) for s, tag in d.items()]

    outp = os.environ.get("OUT", "/data/data/com.termux/files/usr/tmp/opencode/r17_cands.txt")
    with open(outp, "w") as fh:
        for s, _ in cands:
            fh.write(s + "\n")
    print(f"\nWrote {len(cands)} candidates to {outp}")
    with open(outp.replace(".txt", "_tags.txt"), "w") as fh:
        for s, tag in cands:
            fh.write(tag + "\n")


if __name__ == "__main__":
    main()