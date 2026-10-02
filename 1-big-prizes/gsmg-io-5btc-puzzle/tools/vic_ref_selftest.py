#!/usr/bin/env python3
"""Provenance stamp + selftest for the vendored kyrias/vic reference implementation.

Vendored from https://github.com/kyrias/vic at the commit recorded in
tools/vic_ref/UPSTREAM_COMMIT (see analysis/tested.md for the ledger row).

WHY THIS EXISTS. analysis/leads.md:500-504 ("fact 5, the verification problem")
states that a full VIC decode needs five unknowns JOINTLY - checkerboard
alphabet, a..i->digit mapping, escapes, transposition key, and mod-9
over-encryption keystream - and that "the only verifier is the closed end-to-end
loop (decode -> sha256(answer) -> opens the funded gate)". Every negative filed
in this folder under the direct-checkerboard model is therefore bounded only
over that subspace.

kyrias/vic is an independent, from-scratch implementation of the COMPLETE cipher
(checkerboard + both transpositions + disruption + message-id insertion). This
selftest establishes what it can and cannot tell us:

  CONTROL A (positive): a full 5-parameter encrypt/decrypt roundtrip returns the
  plaintext exactly. Proves the vendored code runs and is self-consistent.
  CONTROL B (negative): mutating ONE of the five parameters (the keyphrase) must
  destroy the plaintext. Proves the implementation is actually sensitive to the
  transposition/over-encryption layers rather than ignoring them - this is the
  property the direct-checkerboard sweeps lacked.
  CONTROL C (negative): a corrupted ciphertext must not decode to the plaintext.
  Proves we would notice a wrong answer.

Self-test only. It asserts nothing about the puzzle and submits nothing.
"""

import io
import contextlib
import hashlib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from vic_ref import encrypt, decrypt  # noqa: E402

# GENERIC 28-char toy board, NOT the certified GSMG.IO board.
#
# It has the certified board's shape - 26 letters plus the two '.' cells that the
# straddling checkerboard needs for the second/third layer - and nothing more.
# The genuine certified board is FUBCDORA.LETHINGKYMVPS.JQZXW, whose two dots sit
# interleaved after A and after S; this one carries its second dot at the end.
# That difference is deliberate and must not be "corrected": the ciphertext sha256
# printed by CONTROL A is pinned in analysis/tested.md R-VICREF-2026-10-01 as
# 5b6f21905194b41e0acfc505cda2755645a8cba0216b288be76465a3b368eb27, so changing a
# single character here would invalidate a recorded digest.
#
# An earlier version of this comment claimed the string below was "exactly the
# 28-char certified board". That was false, and the false claim is what made this
# read as puzzle-relevant. It is not: only the ALPHABET here has any relation to
# GSMG.IO, the other four parameters are upstream's own README example values.
ALPHABET = "FUBCDORA.LETHINGKYMVPSJQZXW."
CERTIFIED_BOARD = "FUBCDORA.LETHINGKYMVPS.JQZXW"  # reference only; NOT used below
CHECKERBOARD_KEY = "FU  BCDORA"  # 8 letters from ALPHABET + 2 spaces = 10 chars
KEYPHRASE = "perfect cherry woodx"  # 20 chars
PERSONAL_ID = 20
DATE = [6, 9, 1, 2, 1, 0]
MESSAGE_ID = [1, 2, 3, 4, 5]

PLAINTEXT = (
    "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALF"
    "ANDTHEYALSONEEDFUNDSTOLIVE"
)

PASS = "PASS"
FAIL = "FAIL"


def _ciphertext(keyphrase=KEYPHRASE, plaintext=PLAINTEXT):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        encrypt(
            ALPHABET,
            CHECKERBOARD_KEY,
            keyphrase,
            PERSONAL_ID,
            DATE,
            MESSAGE_ID,
            plaintext,
        )
    return buf.getvalue().strip()


def _decrypt(ciphertext, keyphrase=KEYPHRASE):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        decrypt(ALPHABET, CHECKERBOARD_KEY, keyphrase, PERSONAL_ID, DATE, ciphertext)
    return buf.getvalue().strip()


def _try_decrypt(ciphertext, keyphrase=KEYPHRASE):
    """Decrypt, tolerating the failure modes a wrong key actually produces.

    With a wrong keyphrase the untransposed digit groups fall outside the
    checkerboard, and upstream raises KeyError from
    inverted_checkerboard_lookup. That IS the plaintext being destroyed, so it
    counts as a successful negative rather than a crash in the self-test.
    """
    try:
        return _decrypt(ciphertext, keyphrase)
    except KeyError:
        return "<KeyError: decoded group outside checkerboard>"


def _upstream_commit():
    p = HERE / "vic_ref" / "UPSTREAM_COMMIT"
    return p.read_text().strip() if p.exists() else "UNKNOWN"


def main():
    failures = []
    total = 0

    commit = _upstream_commit()
    print(f"vendored kyrias/vic @ {commit}  (ISC, see vic_ref/LICENSE)")
    print(f"alphabet        : {ALPHABET} (len {len(ALPHABET)})")
    print(f"                  GENERIC 28-char toy board - not puzzle evidence")
    print(f"certified board : {CERTIFIED_BOARD} (reference only, unused here)")

    # ISC requires the copyright and permission notice to appear in all copies.
    # The upstream LICENSE had never been vendored, which is the defect this
    # check exists to catch; matrix_enc_ref/ got the same treatment for GPL-3.0.
    lic = HERE / "vic_ref" / "LICENSE"
    if lic.is_file():
        text = lic.read_text(errors="replace")
        # ISC's operative grant and warranty disclaimer, quoted as upstream
        # writes them. Deliberately NOT "WITHOUT WARRANTY OF ANY KIND": that is
        # BSD-3-clause phrasing and its absence here is what proves this is ISC
        # rather than a copyleft or BSD variant.
        ok_lic = ("Copyright (c) 2016, Johannes" in text
                  and "Permission to use, copy, modify, and/or distribute" in text
                  and "with or without fee is hereby granted" in text
                  and "THE AUTHOR DISCLAIMS ALL WARRANTIES" in text)
        total += 1
        print(f"  [{PASS if ok_lic else FAIL}] LICENSE is upstream ISC "
              f"({len(text)} chars, sha256 "
              f"{hashlib.sha256(text.encode()).hexdigest()[:16]}...)")
        if not ok_lic:
            failures.append("LICENSE is upstream ISC")
    else:
        total += 1
        print(f"  [{FAIL}] LICENSE file present in vic_ref/")
        failures.append("LICENSE file present in vic_ref/")
    print(f"checkerboard key: {CHECKERBOARD_KEY!r} "
          f"(len {len(CHECKERBOARD_KEY)}, {CHECKERBOARD_KEY.count(' ')} spaces)")
    print(f"keyphrase       : {KEYPHRASE!r} (len {len(KEYPHRASE)})")
    print(f"date            : {DATE}  personal_id: {PERSONAL_ID}  "
          f"message_id: {MESSAGE_ID}")
    print()

    # Sanity-check the argument shapes the upstream validator enforces, so a
    # malformed self-test can't pass silently.
    for name, ok in (
        ("alphabet is 28 chars", len(ALPHABET) == 28),
        ("checkerboard key is 10 chars", len(CHECKERBOARD_KEY) == 10),
        ("checkerboard key has 2 spaces", CHECKERBOARD_KEY.count(" ") == 2),
        ("keyphrase is 20 chars", len(KEYPHRASE) == 20),
        ("every checkerboard-key letter is in the alphabet",
         all(c in ALPHABET for c in CHECKERBOARD_KEY.replace(" ", ""))),
        ("every plaintext char is in the alphabet",
         all(c in ALPHABET for c in PLAINTEXT)),
    ):
        total += 1
        print(f"  [{PASS if ok else FAIL}] precondition: {name}")
        if not ok:
            failures.append(name)

    ct = _ciphertext()
    rt = _try_decrypt(ct)
    ok = rt == PLAINTEXT
    total += 1
    print(f"\n  [{PASS if ok else FAIL}] CONTROL A roundtrip: "
          f"encrypt->decrypt recovers plaintext exactly")
    if not ok:
        failures.append("control A roundtrip")
    print(f"        ciphertext sha256 = "
          f"{hashlib.sha256(ct.encode()).hexdigest()}")
    print(f"        ciphertext[0:48]  = {ct[:48]}")

    # CONTROL B: one parameter changed must destroy the plaintext. This is the
    # property that the direct-checkerboard sweeps could not test.
    bad = _ciphertext(keyphrase="perfect cherry woody")
    bad_rt = _try_decrypt(bad)
    ok = bad_rt != PLAINTEXT
    total += 1
    print(f"\n  [{PASS if ok else FAIL}] CONTROL B sensitivity: one keyphrase "
          f"change breaks the plaintext")
    if not ok:
        failures.append("control B sensitivity")

    # CONTROL C: corrupted ciphertext must not decode to the plaintext.
    corrupt = ct[:-5] + ("99999" if not ct[-5:] == "99999" else "88888")
    corrupt_rt = _try_decrypt(corrupt)
    ok = corrupt_rt != PLAINTEXT
    total += 1
    print(f"  [{PASS if ok else FAIL}] CONTROL C corruption: altered tail "
          f"breaks the plaintext")
    if not ok:
        failures.append("control C corruption")

    print()
    if failures:
        print(f"SELFTEST FAIL ({len(failures)}): {', '.join(failures)}")
        return 1
    print(f"SELFTEST PASS (0 failures, {total} checks)")
    print("NOTE: this certifies the vendored implementation only. It says "
          "nothing about the puzzle: the 5 parameters above are the README's own "
          "toy values, NOT recovered from GSMG.IO evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())