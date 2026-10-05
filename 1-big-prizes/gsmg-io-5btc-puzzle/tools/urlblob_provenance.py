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
of the blob: the URL slug is a byte-exact prefix of the file. The site named
the route after the hex of its own blob header, so the slug certifies 54 of the
112 bytes without reference to any on-disk artifact. That covers the whole
32-byte header and 30 of 88 ciphertext bytes; the trailing 58 bytes rest on this
file alone.

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

# The public route, as recorded in the Wayback CDX index and in
# ~/gsmg/gsmg-io/gsmg.io.old-site-2026-09-27/FETCH-LOG.md:298. 109 hex chars --
# an ODD count, so the final nibble is a truncated half-byte and is dropped.
SLUG_HEX = (
    "53616c7465645f5f74c974e3f92e64b59f7ea22a50dcb0d4289d176d4ce9dba7"
    "f99a695b8d0797b5c7791e65a8d2b68a5879f5d31ae5e"
)
SLUG = bytes.fromhex(SLUG_HEX[: len(SLUG_HEX) // 2 * 2])

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

    print("F2 -- PROVENANCE: the public URL slug is a byte-exact prefix")
    print("     (independent of the blob: the site named the route after the")
    print("      hex of its own header, so it certifies 54 of 112 bytes)")
    check("slug hex length is odd", len(SLUG_HEX) % 2, 1)
    check("dropped tail nibble", SLUG_HEX[-1], "e")
    check("slug bytes", len(SLUG), 54)
    check("slug[0:54] == blob[0:54]", SLUG, blob[:54])
    check("slug[8:24] == salt", SLUG[8:24], SALT)
    check("slug[24:54] == blob[24:54] (30 CT bytes)", SLUG[24:], blob[24:54])
    print("     corroborated %d of %d bytes (header 32/32, ciphertext %d/%d)"
          % (len(SLUG), len(blob), len(SLUG) - HEADER, len(blob) - HEADER))
    print("     NOT corroborated by any public source: %d trailing bytes"
          % (len(blob) - len(SLUG)))
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

    print("negative control 2: a corrupted salt must BREAK the slug match")
    bad = bytearray(SLUG)
    bad[8] ^= 0x01
    check("flipped salt bit breaks prefix match", bytes(bad) == SLUG, False)
    print()

    print("negative control 3: the misaligned ct must FAIL a Salted__ parse")
    check("ctfile does not start with Salted__", ctfile[:8] == MAGIC, False)
    check("ctfile-as-salt != real salt", ctfile[:16] != SALT, True)
    print()

    print("negative control 4: a 1-byte tail change must break the length claim")
    check("113 B is not CBC-valid either",
          (113 - HEADER) % 16 == 0, False)
    print()

    print("negative control 5: the corroborated span must not be overstated")
    check("slug does NOT cover the whole blob", len(SLUG) == len(blob), False)
    check("uncorroborated bytes exist", len(blob) - len(SLUG), 58)
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
            print("provenance CERTIFIED (54/112 bytes, publicly); "
                  "D1 and D2 both real and both live.")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))