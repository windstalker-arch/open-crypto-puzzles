#!/usr/bin/env python3
"""
Integrity + round-trip self-test for the vendored MatrixEncryption reference.

Scope: this is a *reference cipher implementation* kept for comparison. It has
no standing in the puzzle's solution chain and no oracle here ever consumes its
output. This test exists only to prove the vendored copy is intact and behaves
as documented.

Checks provenance recorded in tools/matrix_enc_ref/PROVENANCE.md, verifies the
upstream GPL-3.0 LICENSE survived vendoring (the gap flagged for
tools/vic_ref/UPSTREAM_COMMIT and analysis/tested.md), and runs the upstream
round-trip harness.

Usage:  python3 tools/matrix_enc_ref_selftest.py [trials]
Exit 0 = all checks pass.
"""

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REF = HERE / "matrix_enc_ref"

UPSTREAM = "e68dce37d91d1c506ace3ea3b8d457ef53f7b3e9"
TRIALS_DEFAULT = 120

failures = []
notes = []


def check(label, condition, detail=""):
    if condition:
        print("  PASS  %s" % label)
    else:
        print("  FAIL  %s %s" % (label, detail))
        failures.append(label)


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else TRIALS_DEFAULT

    print("matrix_enc_ref provenance")
    check("directory present", REF.is_dir(), str(REF))

    required = ["main.py", "PiDigits.TXT", "LICENSE",
                "UPSTREAM_COMMIT", "selftest.py", "PROVENANCE.md"]
    for name in required:
        check("file present: %s" % name, (REF / name).is_file())

    # The gap that bit tools/vic_ref/: an upstream copy with no license file.
    lic = REF / "LICENSE"
    if lic.is_file():
        text = lic.read_text(errors="replace")[:400]
        check("LICENSE is GPL-3.0",
              "GNU GENERAL PUBLIC LICENSE" in text and "Version 3" in text)

    up = REF / "UPSTREAM_COMMIT"
    if up.is_file():
        raw = up.read_text()
        check("UPSTREAM_COMMIT is 40-hex sha + newline",
              bool(re.fullmatch(r"[0-9a-f]{40}\n", raw)), repr(raw))
        check("UPSTREAM_COMMIT matches PROVENANCE pin",
              raw.strip() == UPSTREAM, raw.strip())

    print("\npayload")
    if (REF / "PiDigits.TXT").is_file():
        digits = (REF / "PiDigits.TXT").read_text()
        check("pi payload length == 1000001", len(digits) == 1000001, len(digits))
        check("pi payload starts correctly",
              digits.startswith("14159265358979323846264338327950288419716939937510"))

    print("\nlocal patch disclosure")
    if (REF / "main.py").is_file():
        src = (REF / "main.py").read_text()
        check("main.py declares _PIDIGITS", "_PIDIGITS" in src)
        check("main.py resolves PiDigits.TXT via __file__",
              os_uses_filedir := ('os.path.join' in src and '__file__' in src
                                  and 'PiDigits.TXT' in src))
        check("main.py has no stale lowercase filename",
              '"piDigits.txt"' not in src)
        # the literals that must NOT be "fixed" to integer division
        check("float literals preserved (1/2 and 1/4)",
              "(1 / 2)" in src and "(1 / 4)" in src)

    print("\nround-trip (%d trials/level)" % trials)
    proc = subprocess.run([sys.executable, str(REF / "selftest.py"), str(trials)],
                          capture_output=True, text=True, timeout=900)
    for line in proc.stdout.strip().splitlines():
        print("    " + line)
    check("upstream selftest exit 0", proc.returncode == 0,
          proc.stderr.strip()[-300:])

    print("")
    if failures:
        print("FAILED: %d check(s): %s" % (len(failures), ", ".join(failures)))
        return 1
    print("ALL CHECKS PASS (reference implementation intact; no puzzle bearing)")
    return 0


if __name__ == "__main__":
    sys.exit(main())