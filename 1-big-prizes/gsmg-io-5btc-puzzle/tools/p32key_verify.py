#!/usr/bin/env python3
"""R-P32KEYVERIFY - certify the phase-3.2 blob solve, and the sign-convention trap.

WHY THIS TOOL EXISTS
====================
`R-P32KEY` (2026-09-26) solved the 1539-byte blob, but shipped NO tool: the solve
lived only as prose in `analysis/tested.md`.  Two days later `R-P32FLAG` analysed
the same blob, reported "Key and plaintext NOT recovered", and told the next
session the per-column mixture was still an open attack.  An uncertified solve is
an invisible solve, so this tool re-derives the whole thing from raw bytes and
pins it.  Everything here is recomputed; nothing is copied from the ledger.

THE CERTIFIED RESULT
====================
    key (shift-then-substitute) : amphtaclwmtbvfz
    key (substitute-then-shift) : aolthaypeohzfvb      <- the same key, negated
    decode(blob) == yl          : True   (1539/1539)
    encode(yl) == blob          : True   (byte-exact round trip)

`yl` is the 1539-char community plaintext already on disk in
`gsmg-solver-group/"Last solved and unsolved parts.txt"`, sha256
`90829b51...`, described there as "Solved, but unused string".

THE TRAP THIS ROW RECORDS.  The two keys above are the SAME cipher under opposite
sign conventions, and they differ in every position.  A test that fixes one
convention and then declares the published key invalid reports **1182/1539
contradictions** - 77% wrong - while the other convention gives **0**.  So:

  * this happened to me while writing this very row: a sign-restricted harness
    reported the PUBLISHED key invalid, and only a 2-sign sweep exonerated it;
  * always sweep BOTH conventions before calling a published key wrong;
  * "the key does not apply" (e.g. `R-VIC149`'s 0.101 against the 149-digit
    string) is only meaningful if the convention was swept, because a
    sign-restricted harness manufactures a false negative.

F-FLAGARTIFACT.  `R-P32FLAG` (2026-09-28) read the blob's 17-high / 9-low byte
split as a designed "flag bit" gesturing at the page's "one for one, four for
one".  The split is real but it is an **artifact of the author's arbitrary
substitution L**: L maps 17 letters to bytes >= 0x80 (`abcdeklmnopqswxyz`) and 9
to low bytes (`fghijrtuv`).  Nothing about it is signalled by the text.  This is
the `R-FAEDCOORD` failure mode - scoring an artifact - repeated on a solved
object, and it is why the flag-bit interpretation is withdrawn.

USAGE
=====
    python3 tools/p32key_verify.py --selftest
    python3 tools/p32key_verify.py --report
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from p32blob_flagbit import load_blob  # noqa: E402  (same 26-symbol isolation)

PERIOD = 15
YL_SHA = "90829b510c3697569da47d2817f545f1e2a1cddd78e45f821dafcdab3dc0c281"
KEY_PUBLISHED = "amphtaclwmtbvfz"   # shift-then-substitute
KEY_NEGATED = "aolthaypeohzfvb"     # substitute-then-shift

YL_SOURCES = [
    Path("~/storage/external/briefcase/gsmg-solver-group/Last solved and unsolved parts.txt"),
    Path("~/storage/external/briefcase/gsmg-solver-group/Msgs.txt"),
    REPO.parent / "gsmg-community-hints-repo/solver-group/Last solved and unsolved parts.txt",
]


def sh(p: str, k: int) -> str:
    return chr((ord(p) - 97 + k) % 26 + 97)


def load_yl() -> str:
    for p in YL_SOURCES:
        q = p.expanduser()
        if not q.exists():
            continue
        m = re.search(r"yourlifeisthesum[a-z]*", q.read_text(encoding="utf-8", errors="replace"))
        if m and hashlib.sha256(m.group(0).encode()).hexdigest() == YL_SHA:
            return m.group(0)
    raise SystemExit("plaintext not found; tried:\n  " + "\n  ".join(str(p.expanduser()) for p in YL_SOURCES))


def column_maps(blob: bytes, yl: str) -> list[dict]:
    maps = []
    for c in range(PERIOD):
        m: dict[int, str] = {}
        for k in range(c, len(blob), PERIOD):
            b, p = blob[k], yl[k]
            if m.setdefault(b, p) != p:
                raise AssertionError("column %d: byte %#04x maps to two letters" % (c, b))
        maps.append(m)
    return maps


def derive_key(maps: list[dict]) -> tuple[list[int], int]:
    """Per-column letter shift, in the SHIFT-THEN-SUBSTITUTE convention, i.e. the
    key k with   blob[k] = L(shift(+k[k % 15], plaintext[k])).

    Column maps give M_c(b) = shift(ds_c, M_0(b)), so L = M_0^-1 and
    blob = L(shift(-ds_c, p));  hence k = -ds."""
    ds, conflicts = [], 0
    for c in range(PERIOD):
        d = {(ord(maps[c][b]) - ord(maps[0][b])) % 26 for b in set(maps[0]) & set(maps[c])}
        if len(d) != 1:
            conflicts += 1
            continue
        ds.append((-d.copy().pop()) % 26)
    return ds, conflicts


def build_L(maps: list[dict], key: list[int]) -> tuple[dict, int]:
    """letter -> byte, for the single convention  blob[k] = L(shift(+k_c, plaintext[k]))."""
    L: dict[str, int] = {}
    conflicts = 0
    for c in range(PERIOD):
        for b, p in maps[c].items():
            ch = sh(p, key[c])
            if L.setdefault(ch, b) != b:
                conflicts += 1
    return L, conflicts


def contradictions(key: list[int], yl: str, blob: bytes, sign: int) -> tuple[int, int]:
    """Non-circular test: does ONE letter->byte map explain every position?
    sign=+1 is the published convention; sign=-1 is its negation."""
    L, bad = {}, 0
    for k in range(len(yl)):
        ch, b = sh(yl[k], sign * key[k % PERIOD]), blob[k]
        if L.setdefault(ch, b) != b:
            bad += 1
    return bad, len(L)


def decode(blob: bytes, L: dict, key: list[int], sign: int = +1) -> str:
    """Unknown bytes decode to '?' rather than raising, so a corrupted ciphertext
    yields a WRONG STRING (a detectable failure) instead of an exception."""
    inv = {v: k for k, v in L.items()}
    return "".join(sh(inv[blob[k]], -sign * key[k % PERIOD]) if blob[k] in inv else "?"
                   for k in range(len(blob)))


def encode(yl: str, L: dict, key: list[int], sign: int = +1) -> bytes:
    return bytes(L[sh(yl[k], sign * key[k % PERIOD])] for k in range(len(yl)))


def solve():
    blob, yl = load_blob(), load_yl()
    maps = column_maps(blob, yl)
    key, colconf = derive_key(maps)
    L, lconf = build_L(maps, key)
    return blob, yl, maps, key, L, colconf, lconf


def report() -> int:
    blob, yl, maps, key_v, L, colconf, lconf = solve()
    key = "".join(chr(97 + s) for s in key_v)
    neg = [(26 - s) % 26 for s in key_v]
    key_neg = "".join(chr(97 + s) for s in neg)
    print("R-P32KEYVERIFY   blob %d B  sha256 %s" % (len(blob), hashlib.sha256(blob).hexdigest()[:16]))
    print("                 yl   %d ch sha256 %s" % (len(yl), YL_SHA[:16]))
    print("\ncolumn maps: %d columns, sizes %s, multi-value conflicts %d"
          % (len(maps), sorted({len(m) for m in maps}), colconf))
    print("L: %d letters -> %d distinct bytes, conflicts %d, covers a-z: %s"
          % (len(L), len(set(L.values())), lconf, "".join(sorted(L)) == "abcdefghijklmnopqrstuvwxyz"))
    print("\nkey (shift-then-substitute) : %s   %s" % (key, "== R-P32KEY" if key == KEY_PUBLISHED else "DIFFERS"))
    print("key (substitute-then-shift) : %s   %s" % (key_neg, "== negation of published" if key_neg == KEY_NEGATED else "DIFFERS"))
    print("negated published == derived: %s" % ("".join(chr(97 + (26 - (ord(c) - 97)) % 26) for c in KEY_PUBLISHED) == key_neg))
    print("\ndecode(blob) == yl : %s" % (decode(blob, L, key_v) == yl))
    print("encode(yl) == blob : %s" % (encode(yl, L, key_v) == blob))
    print("plaintext head     : %s" % yl[:64])
    print("plaintext tail     : %s" % yl[-48:])
    print("\nF-FLAGARTIFACT - the 17/9 split is L's arbitrary byte assignment, not a designed bit:")
    hi = sorted(c for c, b in L.items() if b >= 0x80)
    lo = sorted(c for c, b in L.items() if b < 0x80)
    print("  %d letters -> bytes >= 0x80 : %s" % (len(hi), "".join(hi)))
    print("  %d letters -> bytes <  0x80 : %s" % (len(lo), "".join(lo)))
    print("  R-P32FLAG called this a FLAG BIT and linked it to 'one for one, four for one'.")

    print("\nTHE TRAP - the same key under a sign-restricted harness:")
    pub = [ord(c) - 97 for c in KEY_PUBLISHED]
    for sign, label in ((+1, "shift-then-substitute"), (-1, "substitute-then-shift")):
        bad, n = contradictions(pub, yl, blob, sign)
        print("  published key, %-24s contradictions %-5d / %d  -> %s"
              % (label, bad, len(yl), "VALID" if bad == 0 else "FALSE NEGATIVE"))
    return 0


def selftest() -> int:
    blob, yl, maps, key_v, L, colconf, lconf = solve()
    ok, fail = 0, []

    def check(name, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append(name)

    # --- the certified solve, every leg recomputed from raw bytes ---
    check("blob is 1539 bytes", len(blob) == 1539)
    check("yl is 1539 chars", len(yl) == 1539)
    check("yl is a-z only", "".join(sorted(set(yl))) == "abcdefghijklmnopqrstuvwxyz")
    check("yl sha256 pinned", hashlib.sha256(yl.encode()).hexdigest() == YL_SHA)
    check("blob has exactly 26 distinct bytes", len(set(blob)) == 26)
    check("15 columns, each single-valued", len(maps) == 15 and colconf == 0)
    check("L is a total bijection a-z -> 26 bytes", lconf == 0 and len(L) == 26 and len(set(L.values())) == 26)
    check("derived key == R-P32KEY's amphtaclwmtbvfz", "".join(chr(97 + s) for s in key_v) == KEY_PUBLISHED)
    check("decode(blob) == yl exactly", decode(blob, L, key_v) == yl)
    check("encode(yl) == blob byte-exactly", encode(yl, L, key_v) == blob)
    check("decode is gauge-invariant (negated key also decodes)",
          decode(blob, L, [(26 - s) % 26 for s in key_v], -1) == yl)
    check("the two published keys are exact negations",
          "".join(chr(97 + (26 - (ord(c) - 97)) % 26) for c in KEY_PUBLISHED) == KEY_NEGATED)

    # --- THE TRAP: a sign-restricted harness must be shown to fail ---
    pub = [ord(c) - 97 for c in KEY_PUBLISHED]
    bad_neg, n_neg = contradictions(pub, yl, blob, -1)
    check("published key is VALID under + convention", contradictions(pub, yl, blob, +1) == (0, 26))
    check("published key is FALSELY rejected under - convention (the trap fires)",
          bad_neg > 1000 and n_neg == 26)
    check("the trap is not symmetric: 0 vs %d is a 2-sign sweep, not luck" % bad_neg, bad_neg != 0)

    # --- F-FLAGARTIFACT: measure the 17/9 split as an artifact of L ---
    hi = [c for c, b in L.items() if b >= 0x80]
    lo = [c for c, b in L.items() if b < 0x80]
    check("L sends 17 letters to high bytes", len(hi) == 17)
    check("L sends 9 letters to low bytes", len(lo) == 9)
    check("the 17/9 split is determined by L, i.e. an artifact",
          sorted(hi) == list("abcdeklmnopqswxyz") and sorted(lo) == list("fghijrtuv"))
    check("ciphertext alphabet is exactly L's 26 bytes", set(blob) == set(L.values()))

    # --- NEGATIVE CONTROLS: the harness must be able to FAIL ---
    # Without these, a passing round trip could just be a self-consistent identity.
    corrupt = list(yl)
    corrupt[0] = "z" if corrupt[0] != "z" else "q"
    check("NC: one flipped plaintext char breaks the round trip",
          encode("".join(corrupt), L, key_v) != blob)
    corrupt2 = bytearray(blob)
    corrupt2[7] ^= 0x01
    check("NC: one flipped ciphertext byte breaks the decode",
          decode(bytes(corrupt2), L, key_v) != yl)
    wrong = list(key_v)
    wrong[3] = (wrong[3] + 1) % 26
    check("NC: a one-column key error breaks the round trip", encode(yl, L, wrong) != blob)
    check("NC: the contradictions() detector fires on a corrupted key",
          contradictions(wrong, yl, blob, +1)[0] > 0)
    check("NC: column_maps rejects a byte that maps to two letters",
          _raises(lambda: column_maps_blob(blob, yl[:100] + "q" * (len(yl) - 100))))

    print("SELFTEST %s %d/%d" % ("PASS" if not fail else "FAIL " + ",".join(fail), ok, ok + len(fail)))
    return 0 if not fail else 1


def column_maps_blob(blob: bytes, yl: str) -> None:
    """column_maps on a deliberately misaligned pair - must raise."""
    maps = []
    for c in range(PERIOD):
        m = {}
        for k in range(c, min(len(blob), len(yl)), PERIOD):
            b, p = blob[k], yl[k]
            if m.setdefault(b, p) != p:
                raise AssertionError("column %d: byte %#04x maps to two letters" % (c, b))
        maps.append(m)


def _raises(fn) -> bool:
    try:
        fn()
    except AssertionError:
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    report()
    return 0


if __name__ == "__main__":
    sys.exit(main())
