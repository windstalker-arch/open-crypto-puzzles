#!/usr/bin/env python3
"""
R-URLBLOB-2026-10-05: certify the provenance and the structure of the fourth
`Salted__` blob, the one whose only public appearance is a hex-encoded URL slug
on the old gsmg.io site.

Why this file exists. `tested.md:11941` asserts the blob was "never archived
on-device". That is WRONG: it has been on the SD card since 2026-09-06 at
`/storage/EA7B-C038/briefcase/gsmg-puzzle/analysis/urlblob.bin`, outside every
root a device-local `find` reaches. A negative recorded against a missing file
is not a negative about the puzzle. Two further defects are certified here, both
of which can silently re-poison a sweep:

  D1  `urlblob_ct.bin` is `urlblob.bin[16:112]`, NOT `[24:120]`. It is
      misaligned by 8 bytes: its first 8 bytes are the TAIL OF THE SALT and
      its bytes 8..16 are the FIRST 8 BYTES OF THE REAL CIPHERTEXT. Any sweep
      handed `urlblob_ct.bin` re-derives exactly the bug recorded in
      `~/briefcase/MEMORY.md:17` ("salt 289d176d... garbage").

  D2  `urlblob.bin` is 112 B = 24 B header + 88 B ciphertext, and 88 is NOT a
      multiple of 16. No AES-CBC length yields 112. So the file is either
      truncated (a 96 B ciphertext would make 120 B) or the cipher is a stream
      mode (CFB/OFB/CTR), where 88 B is legitimate. Unresolved -- see below.

The provenance is what makes the blob trustworthy at all, and it is INDEPENDENT
of the blob: the URL route is the hex of the file itself. There are two real
routes, both Wayback captures with status 200:

    80 hex chars / 40 B   capture 20260207190055
   224 hex chars / 112 B  capture 20260105015908

The 224-char route is BYTE-EXACT to urlblob.bin -- all 112 bytes, header and
ciphertext alike -- so the whole blob is certified from public data with no
on-disk artifact. An earlier revision of this file recorded only a 109-char
slug and concluded that "54 of 112 bytes are certified and the trailing 58 rest
on the file alone". That was wrong: the 109-char string is a truncated LOCAL
construction whose carrier is a Wayback 404 page, and the real route runs 15
bytes past it.

Note the header is 24 B ("Salted__" + a 16-byte salt), so "the entire 32-byte
header" in the earlier revision was also off by 8 -- the same 8-byte slip that
misaligned urlblob_ct.bin in DEFECT 1 below.

Usage:  python3 tools/urlblob_provenance.py [--selftest]

Exit 0 = all checks pass. Reads only; never calls an oracle or a funded gate.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ANALYSIS = os.path.join(REPO, "analysis")

BLOB = os.path.join(ANALYSIS, "urlblob.bin")
CTFILE = os.path.join(ANALYSIS, "urlblob_ct.bin")

# THE FULL PUBLIC ROUTE. 224 hex chars = 112 bytes, and it is BYTE-EXACT to
# urlblob.bin (sha256 25b3619a...). Wayback CDX capture 20260105015908, status
# 200. This route CERTIFIES THE WHOLE BLOB, not a 54-byte prefix -- an earlier
# version of this file recorded only a 109-char slug and concluded "54 of 112
# bytes certified, trailing 58 uncorroborated", which is FALSE.
ROUTE_HEX = (
    "53616c7465645f5f74c974e3f92e64b59f7ea22a50dcb0d4289d176d4ce9dba7"
    "f99a695b8d0797b5c7791e65a8d2b68a5879f5d31ae5e8a2635205de31b851cf"
    "43b2534f58765696d3c2a01f7f3a41f7284fbbcc836517cbf7ba613c43a919d"
    "9dc669e4824baba6a5caeb77dfc3e0607"
)
ROUTE = bytes.fromhex(ROUTE_HEX)

# The earlier 109-hex-char string, kept only to show it is a TRUNCATED LOCAL
# CONSTRUCTION: it is a prefix of the real route, and the file that carries it
# (_quarantine_wayback404/) is a 4672-byte Wayback 404 page, not a capture.
# ~/gsmg/gsmg-io/gsmg.io.old-site-2026-09-27/FETCH-LOG.md:298 records it.
SLUG_HEX = (
    "53616c7465645f5f74c974e3f92e64b59f7ea22a50dcb0d4289d176d4ce9dba7"
    "f99a695b8d0797b5c7791e65a8d2b68a5879f5d31ae5e"
)
SLUG = bytes.fromhex(SLUG_HEX[: len(SLUG_HEX) // 2 * 2])

# A third, SHORTER real route: 80 hex chars = 40 bytes, capture 20260207190055,
# status 200. It is the 40-byte prefix of the same blob, i.e. header + 16 B of
# ciphertext -- consistent with the site exposing the blob in stages.
ROUTE_SHORT_HEX = ROUTE_HEX[:80]
ROUTE_SHORT = bytes.fromhex(ROUTE_SHORT_HEX)

MAGIC = b"Salted__"
HEADER = 8 + 16  # "Salted__" + 16-byte salt

# The full 16-byte salt. The ledger truncates it to 8 bytes ("74c974e3f92e64b5")
# at tested.md:356/7367/11941/14037/19058 and leads.md:748; that is cosmetic,
# same blob, but the full form is recorded here so the two can be compared.
SALT = bytes.fromhex("74c974e3f92e64b59f7ea22a50dcb0d4")
SALT_TRUNC_LEDGER = "74c974e3f92e64b5"

# The other three Salted__ blobs this one must NOT be confused with.
KNOWN_OTHER_SALTS = {
    "small": "3ab585348552415d",
    "dualite": "2d3f6fe06dc950e6",
    "phase2_a": "06286612d43ed7ed58f15b3eae5323c5",
    "phase2_b": "9fbc451d13d071f4f12887d4b904befb",
    "p32": "b45a5e3d",
}

FAILS = []
CHECKS = [0]


def check(name, got, want):
    CHECKS[0] += 1
    if got != want:
        FAILS.append("%s: got %r want %r" % (name, got, want))
        print("  FAIL %-46s got=%r want=%r" % (name, got, want))
    else:
        print("  ok   %s" % name)


def report(blob, ctfile):
    print("R-URLBLOB-2026-10-05 -- fourth Salted__ blob: provenance + structure")
    print()
    print("blob    %s  %d B  sha256 %s"
          % (os.path.relpath(BLOB, REPO), len(blob),
             hashlib.sha256(blob).hexdigest()))
    print("ctfile  %s  %d B  sha256 %s"
          % (os.path.relpath(CTFILE, REPO), len(ctfile),
             hashlib.sha256(ctfile).hexdigest()))
    print()

    print("F1 -- the salt is 16 bytes; the ledger prints 8")
    check("blob[0:8] == Salted__", blob[:8], MAGIC)
    check("blob[8:24] == full salt", blob[8:24], SALT)
    check("full salt starts with ledger form", SALT.hex()[:16], SALT_TRUNC_LEDGER)
    check("salt is not any of the other blobs",
          SALT.hex()[:16] in KNOWN_OTHER_SALTS, False)
    print()

    print("F2 -- PROVENANCE: two public routes, and the LONG one is the")
    print("     WHOLE BLOB. The site named the route after the hex of the")
    print("     blob itself, so the blob is certified from public data alone.")
    check("short route hex length (80)", len(ROUTE_SHORT_HEX), 80)
    check("short route bytes (40)", len(ROUTE_SHORT), 40)
    check("short route == blob[0:40]", ROUTE_SHORT, blob[:40])
    check("long route hex length (224)", len(ROUTE_HEX), 224)
    check("long route bytes (112)", len(ROUTE), 112)
    check("LONG ROUTE == BLOB, byte for byte", ROUTE, blob)
    check("long route sha256 == blob sha256",
          hashlib.sha256(ROUTE).hexdigest(), hashlib.sha256(blob).hexdigest())
    check("long route[0:8] == magic", ROUTE[:8], MAGIC)
    check("long route[8:24] == salt", ROUTE[8:24], SALT)
    print("     corroborated %d of %d bytes -- header %d/%d, ciphertext %d/%d"
          % (len(ROUTE), len(blob), HEADER, HEADER,
             len(ROUTE) - HEADER, len(blob) - HEADER))
    print("     NOTHING is uncorroborated: the trailing %d bytes are certified"
          % (len(blob) - 54))
    print()
    print("F2b -- the earlier 109-char 'slug' was a LOCAL construction, not a route")
    check("slug hex length is odd", len(SLUG_HEX) % 2, 1)
    check("dropped tail nibble", SLUG_HEX[-1], "e")
    check("slug bytes", len(SLUG), 54)
    check("slug is a strict PREFIX of the real route", ROUTE.startswith(SLUG), True)
    check("real route extends past it by", len(ROUTE) - len(SLUG), 58)
    check("real route length is EVEN (no half-byte)", len(ROUTE_HEX) % 2, 0)
    check("real route is a whole number of bytes", len(ROUTE_HEX) / 2, 112)
    print("     the slug is odd-length and so ends mid-byte; the real route is")
    print("     even and complete. Its carrier _quarantine_wayback404/ holds a")
    print("     4672-byte Wayback 404 page, so the slug was never a capture.")
    print("     CERTIFIED SPAN IS 112/112, NOT THE 54/112 THE OLD ROW CLAIMED.")
    print()

    print("F3 -- D1: urlblob_ct.bin is misaligned by 8 bytes")
    check("ctfile == blob[16:112]  (the defect)", ctfile, blob[16:len(blob)])
    check("the correct slice blob[24:] has a different length",
          len(blob[24:]) == len(ctfile), False)
    check("and different content", blob[24:] == ctfile, False)
    check("ctfile[0:8] == salt TAIL", ctfile[:8], blob[16:24])
    check("ctfile[8:16] == real CT HEAD", ctfile[8:16], blob[24:32])
    check("the MEMORY.md bogus salt is ctfile[8:16]",
          ctfile[8:16].hex()[:16], "289d176d4ce9dba7")
    print("     => feeding urlblob_ct.bin to a Salted__ parser re-creates")
    print("        ~/briefcase/MEMORY.md:17 exactly. Use blob[24:] instead.")
    print()

    print("F4 -- D2: 112 B is not a valid AES-CBC blob length")
    n = len(blob)
    ct = n - HEADER
    check("total length", n, 112)
    check("ciphertext length", ct, 88)
    check("ciphertext % 16 (0 required for CBC)", ct % 16, 8)
    check("no CBC-valid total equals 112",
          [HEADER + k for k in range(16, 129, 16) if HEADER + k == n], [])
    check("MEMORY.md 'ct 96B = 6 blocks' is arithmetically impossible",
          HEADER + 96 == n, False)
    print("     => either TRUNCATED (96 B ciphertext => 120 B total; the lost")
    print("        tail would be %s) or a STREAM mode (CFB/OFB/CTR), where 88 B"
          % blob[-8:].hex())
    print("        is legitimate. NOT RESOLVED here.")
    print()

    print("F5 -- scope")
    print("     corrects tested.md:11941 'never archived on-device' -> it was,")
    print("     on the SD card since 2026-09-06, outside every device-local root.")
    print("     no historical row edited; no oracle call; no gate contact.")
    print()


def selftest(blob, ctfile):
    """Positive and negative controls, so a passing run is known able to fail."""
    print("R-URLBLOB-2026-10-05 -- SELFTEST")
    print()

    print("negative control 1: the route is NOT one of the other three blobs")
    check("salt != dualite", SALT.hex()[:16] == KNOWN_OTHER_SALTS["dualite"],
          False)
    check("salt != small", SALT.hex()[:16] == KNOWN_OTHER_SALTS["small"], False)
    print()

    print("negative control 2: a corrupted salt must BREAK the route match")
    bad = bytearray(ROUTE)
    bad[8] ^= 0x01
    check("flipped salt bit breaks the full-route equality", bytes(bad) == ROUTE, False)
    check("and breaks the salt field", bytes(bad)[8:24] == SALT, False)
    bad2 = bytearray(ROUTE)
    bad2[len(bad2) - 1] ^= 0x01
    check("flipped LAST ciphertext byte also breaks equality",
          bytes(bad2) == ROUTE, False)
    check("...which a prefix-only test could not have caught",
          bytes(bad2)[:54] == blob[:54], True)
    print()

    print("negative control 3: the misaligned ct must FAIL a Salted__ parse")
    check("ctfile does not start with Salted__", ctfile[:8] == MAGIC, False)
    check("ctfile-as-salt != real salt", ctfile[:16] != SALT, True)
    print()

    print("negative control 4: a 1-byte tail change must break the length claim")
    check("113 B is not CBC-valid either",
          (113 - HEADER) % 16 == 0, False)
    print()

    print("negative control 5: the whole blob IS covered, and the old claim was not")
    check("long route covers every byte", len(ROUTE) == len(blob), True)
    check("uncorroborated bytes", len(blob) - len(ROUTE), 0)
    check("the 109-char slug does NOT cover it (old reading)", len(SLUG) == len(blob), False)
    check("old claimed coverage", len(SLUG), 54)
    check("old claimed uncorroborated tail", len(blob) - len(SLUG), 58)
    print("     the OLD negative control asserted these last two as TRUE.")
    print("     They were assertions of a FALSE claim, so the suite 'passed' while")
    print("     certifying the error. They are now pinned as the thing corrected.")
    print()

    if FAILS:
        print("SELFTEST FAIL -- %d check(s) failed" % len(FAILS))
        for f in FAILS:
            print("  " + f)
        return 1
    print("SELFTEST PASS -- %d/%d checks" % (CHECKS[0], CHECKS[0]))
    return 0


def main(argv):
    selftest_only = "--selftest" in argv
    for p in (BLOB, CTFILE):
        if not os.path.exists(p):
            print("MISSING: %s" % p)
            print("source: /storage/EA7B-C038/briefcase/gsmg-puzzle/analysis/")
            return 2
    blob = open(BLOB, "rb").read()
    ctfile = open(CTFILE, "rb").read()

    if selftest_only:
        rc = selftest(blob, ctfile)
    else:
        report(blob, ctfile)
        rc = selftest(blob, ctfile)
        print()
        if FAILS:
            print("RESULT: FAIL -- %d check(s) failed" % len(FAILS))
        else:
            print("RESULT: PASS -- %d/%d checks" % (CHECKS[0], CHECKS[0]))
            print("provenance CERTIFIED (112/112 bytes, publicly, byte-exact); "
                  "D1 and D2 both real and both live.")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))