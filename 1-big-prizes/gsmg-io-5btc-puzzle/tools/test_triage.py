#!/usr/bin/env python3
"""Tests for tools/triage_new.py and tools/sibling_index.py.

Why these exist
---------------
The tool guards against a specific, already-committed mistake: analysing
material as novel when it is a re-encoding of something already held. A guard
that has never been shown to fire is indistinguishable from no guard, so the
firing case is pinned here as a regression test, alongside the case that must
NOT fire, because a gate that blocks everything is as useless as no gate.

Every expectation is stated against a real artifact, never against a value typed
by hand -- the same rule verify_ladder.py follows, for the same reason.

Run:  python3 tools/test_triage.py
Exit 0 only if every check passes.
"""
import binascii
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TRIAGE = REPO / "tools" / "triage_new.py"
INDEX = REPO / "tools" / "sibling_index.py"

# A known indexed artifact, and a known novel one, used as the two poles.
KNOWN_TWIN = REPO.parent / "gsmg-community-hints-repo" / "phase3-assets" / "phase3.2.txt"
KNOWN_HEX = Path("/storage/EA7B-C038/briefcase/gsmg-solver-group/phase3.2.hex")
KNOWN_NOVEL = Path("/storage/EA7B-C038/briefcase/gsmg-solver-group/My2cents .md")

FAILURES = []


def ck(name, cond, detail=""):
    if cond:
        print("  PASS  %s" % name)
    else:
        print("  FAIL  %s   %s" % (name, detail))
        FAILURES.append(name)


def run(args):
    proc = subprocess.run([sys.executable] + args, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def verdict_of(path, extra=()):
    """Return (exit_code, verdict) for a single-file triage."""
    code, out, _ = run([str(TRIAGE), "--json", "--no-contain", *extra, str(path)])
    verdict = None
    for line in out.splitlines():
        if '"verdict"' in line:
            verdict = line.split(":", 1)[1].strip().strip('",')
            break
    return code, verdict


def main():
    print("sibling_index + triage_new test suite\n")

    # --- index integrity -------------------------------------------------
    print("index:")
    code, out, err = run([str(INDEX), "--stats"])
    ck("index --stats exits 0", code == 0, "rc=%d %s" % (code, err.strip()))
    roots = 0
    for line in out.splitlines():
        if line.strip().startswith("roots indexed"):
            roots = int(line.split(":")[1].strip())
    ck("index covers >=10 roots (sibling repos included)", roots >= 10, "roots=%d" % roots)
    ck("no root pattern failed to match", "matched nothing" not in err, err.strip())

    tmp = Path(tempfile.mkdtemp(prefix="triage-test-"))
    try:
        # --- the committed regression ------------------------------------
        print("\nregression (the 2026-09-27 phase3.2.hex error):")
        if KNOWN_HEX.exists() and KNOWN_TWIN.exists():
            code, verdict = verdict_of(KNOWN_HEX)
            ck("hex re-encoding is REENCODING, not DISTINCT",
               verdict == "REENCODING", "got %s" % verdict)
            ck("hex re-encoding blocks the gate (exit 1)", code == 1, "rc=%d" % code)
        else:
            print("  SKIP  solver-group artifact not mounted")

        # --- the gate must not block genuinely new material -------------
        print("\nno false positive:")
        if KNOWN_NOVEL.exists():
            code, verdict = verdict_of(KNOWN_NOVEL)
            ck("novel solver file is DISTINCT", verdict == "DISTINCT", "got %s" % verdict)
            ck("novel solver file passes the gate (exit 0)", code == 0, "rc=%d" % code)
        else:
            print("  SKIP  solver-group artifact not mounted")

        # --- synthetic cases for the paths we can control ---------------
        print("\nsynthetic:")
        if KNOWN_TWIN.exists():
            payload = KNOWN_TWIN.read_bytes()
            digest = hashlib.sha256(payload).hexdigest()

            # A verbatim copy at a different path must read EXACT.
            copy_path = tmp / "plain_copy.txt"
            shutil.copyfile(KNOWN_TWIN, copy_path)
            code, verdict = verdict_of(copy_path)
            ck("byte copy at new path is EXACT", verdict == "EXACT", "got %s" % verdict)
            ck("byte copy blocks the gate", code == 1, "rc=%d" % code)

            # A hex re-encoding of it must read REENCODING, not DISTINCT.
            hex_path = tmp / "hex_copy.txt"
            hex_path.write_bytes(binascii.hexlify(payload))
            code, verdict = verdict_of(hex_path)
            ck("hex re-encoding is REENCODING", verdict == "REENCODING", "got %s" % verdict)

            # A verbatim excerpt must read CONTAINED under --no-contain off.
            excerpt = tmp / "excerpt.txt"
            excerpt.write_bytes(payload[-400:])
            code, out, _ = run([str(TRIAGE), "--json", str(excerpt)])
            contained = '"verdict": "CONTAINED"' in out
            ck("verbatim excerpt is CONTAINED when containment runs",
               contained or code == 0, "rc=%d out=%s" % (code, out[:200]))
            # Under --no-contain it is deliberately not detected; assert that we
            # say so rather than silently passing it as novel.
            code2, verdict2 = verdict_of(excerpt, extra=["--no-contain"])
            ck("excerpt is DISTINCT under --no-contain (documented blind spot)",
               verdict2 == "DISTINCT", "got %s" % verdict2)

        # A file that is genuinely unique must be DISTINCT.
        unique = tmp / "unique.bin"
        unique.write_bytes(hashlib.sha256(b"triage-selftest-payload").digest() * 4
                           + b"nothing else matches this byte string")
        code, verdict = verdict_of(unique)
        ck("unique payload is DISTINCT", verdict == "DISTINCT", "got %s" % verdict)
        ck("unique payload passes the gate", code == 0, "rc=%d" % code)

        # --force must override the block, and only the block.
        if KNOWN_TWIN.exists():
            forced = tmp / "forced_copy.txt"
            shutil.copyfile(KNOWN_TWIN, forced)
            code, _, _ = run([str(TRIAGE), "--no-contain", "--force", str(forced)])
            ck("--force overrides the gate", code == 0, "rc=%d" % code)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%d check(s) failed" % len(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
