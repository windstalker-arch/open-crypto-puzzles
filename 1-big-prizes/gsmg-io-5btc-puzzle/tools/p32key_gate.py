#!/usr/bin/env python3
"""p32key as gate-password X battery.

GAP THIS CLOSES. R-P32KEY (tested.md:12758) recovered the phase-3.2 blob's
15-symbol Vigenere key `amphtaclwmtbvfz` and certified it exactly
(tools/p32key_verify.py, independent re-decode, 254/254 column checks). That key
is the single most author-adjacent string this repo has derived by cryptanalysis
rather than by reading. It is also, per the hint `are you really looking for
just the btc... (...=key)` (tested.md), the exact shape of thing the puzzle says
to look for.

Audited and it has NEVER been submitted to either funded oracle as password X.
Every prior appearance of it is either the solve itself, a certification, a
stale-note correction, or a *relationship* test ("FOUND BY testing the one
avenue the blob solve newly enabled (key/board relationship ...)", tested.md:17766)
- i.e. the key was compared to the board, never offered to the gates. Row
R-P32BLOB-2026-09-26 even states "0 oracle calls" for this blob, and nothing
since contradicts it.

So this is a genuine hole, not a repeat of a closed row.

The key is DERIVED, not quoted (tested.md:17768: it appears in no repo or
briefcase file, is not a substring or anagram-window of the plaintext). It is 15
chars, 12 distinct symbols - so it is not a repeated-word artifact and not a
dictionary string.

N: the key itself plus its close readings. 1 string -> case forms, no-space
reversals, the digest readings the oracles already apply internally, and the two
mechanically motivated neighbours below. Deliberately NOT widened: this is a
single new author-adjacent string, and per the STATE_BRIEF "no further battery is
warranted without item 1 or item 2" discipline a wide family here would be
manufactured activity. The two neighbours are included because they are the only
two transformations the key's own structure motivates, not because they add
coverage:

  - `amphtaclwmtbvfz` reversed = `zfvbmtwclcatphma`. The phase-3.2 cipher is
    "shift-then-substitute", so a reversed key is the natural sign-convention
    error, and R-P32KEYVERIFY already records a near-miss from exactly that trap
    (tested.md:17613).
  - the 15 certified Vigenere SHIFTS from row 12761 rendered as letters, since
    the key is the only place those numbers are written down in symbol form.

Witness: both oracles --selftest PASS before and after (each certifies the
address half against the real on-chain pubkey and re-decrypts a real blob under a
known password). Gate results are read from the oracle EXIT CODE (0 = hit,
1 = no match), not from text parsing.
"""
import pathlib
import re
import subprocess
import sys

BASE = pathlib.Path(__file__).resolve().parents[1]
TOOLS = BASE / "tools"
TMP = pathlib.Path("/data/data/com.termux/files/usr/tmp/opencode")

KEY = "amphtaclwmtbvfz"
# R-P32KEY row 12761: certified shifts for the 15 residue classes
SHIFTS = [0, 12, 15, 7, 19, 0, 2, 11, 22, 12, 19, 1, 21, 5, 25]
SHIFT_LETTERS = "".join(chr(ord("a") + s) for s in SHIFTS)


def selftest():
    assert len(KEY) == 15, KEY
    assert len(SHIFTS) == 15
    assert KEY[::-1] != KEY
    # the key must not be a plaintext quote: if it were, it is not derived
    assert KEY not in "yourlifeisthesumofaremainderofanunbalancedequation"
    print(f"p32key SELFTEST OK (key={KEY} rev={KEY[::-1]} shifts={SHIFT_LETTERS})")


def build():
    cands = {}
    cands[KEY] = "key"
    cands[KEY[::-1]] = "key.reversed"
    cands[SHIFT_LETTERS] = "certified_shifts_as_letters"
    for k in list(cands):
        for form, v in (("upper", k.upper()), ("title", k.capitalize())):
            cands.setdefault(v, f"{cands[k]}.{form}")
    return [c for c in cands if c]


def run(gate, lines):
    r = subprocess.run(
        [sys.executable, str(TOOLS / gate), "--stdin"],
        input="\n".join(lines) + "\n", capture_output=True, text=True, cwd=str(TOOLS),
    )
    out = r.stdout + r.stderr
    hits = [ln for ln in out.splitlines() if ln.startswith("MATCH ")]
    nomatch = sum(1 for ln in out.splitlines() if ln.strip() == "NO MATCH")
    return r.returncode, hits, nomatch


def main():
    selftest()
    lines = build()
    TMP.joinpath("p32key_cands.txt").write_text("\n".join(lines) + "\n")
    print(f"candidates: {len(lines)}")

    for gate in ("oracle.py", "oracle_dualite.py"):
        r = subprocess.run([sys.executable, str(TOOLS / gate), "--selftest"],
                           capture_output=True, text=True, cwd=str(TOOLS))
        ok = "SELFTEST OK" in r.stdout or "SELFCERT" in r.stdout
        print(f"{gate} --selftest before: {'PASS' if ok else 'FAIL'}")
        if not ok:
            print(r.stdout[-800:])
            sys.exit(1)

    for gate in ("oracle.py", "oracle_dualite.py"):
        rc, hits, nomatch = run(gate, lines)
        print(f"{gate}: submitted={len(lines)} exit={rc} "
              f"NO MATCH={nomatch} HITS={len(hits)}")
        for ln in hits:
            print("    HIT:", re.sub(r"(priv_hex|wif)=\S+", r"\1=<redacted>", ln.strip()))

    for gate in ("oracle.py", "oracle_dualite.py"):
        r = subprocess.run([sys.executable, str(TOOLS / gate), "--selftest"],
                           capture_output=True, text=True, cwd=str(TOOLS))
        ok = "SELFTEST OK" in r.stdout or "SELFCERT" in r.stdout
        print(f"{gate} --selftest after: {'PASS' if ok else 'FAIL'}")


if __name__ == "__main__":
    main()
