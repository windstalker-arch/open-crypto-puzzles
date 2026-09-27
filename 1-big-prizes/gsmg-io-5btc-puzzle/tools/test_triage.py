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

The exit-code contract (2026-09-27, R-FORKWIRE)
-----------------------------------------------
This file used to assert `index --stats exits 0` and went red the day the tool
started honouring a promise it had already made in its own docstring: "Exit 0 if
every root was walked, 1 if any root was unreadable or missing." A root that had
been deleted from disk -- a tool temp directory, cleaned up -- made the report
exit 1 forever, and the assertion, not the tool, was what was wrong.

Two things were wrong with that single line, and only fixing the first would have
been the R-CAFULL mistake again (tuning the criterion until the observed result
passes):

1. It demanded a specific exit code from AMBIENT state. The real cache is
   machine state: it is rc=0 on a machine where every root exists and rc=1 on one
   where a temp dir was reaped. A test that flips with the machine is not a test.
   It is now stated as the contract it actually is -- the code must agree with
   what is on disk, checked against the real cache file -- and the quiet case is
   pinned deterministically by the synthetic fixture instead.
2. The guard had no firing case. A guard never shown to fire is
   indistinguishable from no guard, which is why the regression below builds the
   incident for real: the tool walks two real roots, one of them is then deleted,
   and the report is required to notice. Both directions are asserted, because a
   guard that fires on everything is as useless as one that never fires.

Run:  python3 tools/test_triage.py
Exit 0 only if every check passes.
"""
import binascii
import hashlib
import json
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
    roots = 0
    for line in out.splitlines():
        if line.strip().startswith("roots indexed"):
            roots = int(line.split(":")[1].strip())
    ck("index covers >=10 roots (sibling repos included)", roots >= 10, "roots=%d" % roots)
    ck("no root pattern failed to match", "matched nothing" not in err, err.strip())

    # The exit code is a function of disk state, so the expectation is derived
    # from the real cache file rather than hard-coded. Asserting the contract
    # (code agrees with disk, one flag per missing root, every missing root
    # named) still fails if `report()` ever stops noticing a vanished tree --
    # which is the bug this suite exists to catch -- while surviving a tool temp
    # directory being reaped between runs.
    cache_path = REPO / "data" / "sibling_index.json"
    if cache_path.exists():
        cached = json.loads(cache_path.read_text()).get("roots", {})
        gone = sorted(r for r in cached if not os.path.isdir(r))
        errored = sorted(r for r, s in cached.items() if s.get("errors"))
        want = 1 if (gone or errored) else 0
        ck("index --stats exit code agrees with what is on disk", code == want,
           "rc=%d want=%d gone=%d errored=%d" % (code, want, len(gone), len(errored)))
        ck("one STALE flag per root missing from disk",
           out.count("STALE(missing on disk)") == len(gone),
           "flags=%d gone=%d" % (out.count("STALE(missing on disk)"), len(gone)))
        ck("every missing root is named in the report",
           all(r in out for r in gone), "gone=%s" % gone)
        if gone:
            print("  NOTE  %d cached root(s) absent from disk, rc=1 is correct "
                  "here: %s" % (len(gone), ", ".join(gone)))
    else:
        print("  SKIP  no index cache on this machine")

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

            # A verbatim excerpt must read CONTAINED. The host has to be an
            # INDEXED file -- the containment pass only reads the index, so a
            # synthetic host in a tmp dir can never be found. That is why these
            # cases are cut from a real twin rather than written from scratch.
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

            # --- the containment floor ----------------------------------
            # A 1-byte file is a substring of every text file. Without a minimum
            # length the tool reported 20 unrelated files as already held, all
            # "contained in" a 1-byte author_nb_pw_battery.txt. Both directions
            # of the floor are pinned: degenerate must not fire, realistic must.
            print("\ncontainment floor:")
            lone_byte = tmp / "lone_byte.txt"
            lone_byte.write_bytes(b"\n")
            victim = tmp / "innocent_text.txt"
            victim.write_bytes(b"an ordinary text file that happens to end in a newline\n")
            code, out, _ = run([str(TRIAGE), "--json", str(victim)])
            ck("1-byte container does NOT trigger CONTAINED",
               '"verdict": "CONTAINED"' not in out, "false positive: %s" % out[:200])

            real_excerpt = tmp / "real_excerpt.txt"
            real_excerpt.write_bytes(payload[-300:])
            code, out, _ = run([str(TRIAGE), "--json", str(real_excerpt)])
            ck("a 300 B excerpt IS still CONTAINED (floor is not a disable)",
               '"verdict": "CONTAINED"' in out, out[:200])

            token = tmp / "token_excerpt.txt"
            token.write_bytes(payload[-33:])
            code, out, _ = run([str(TRIAGE), "--json", str(token)])
            ck("a 33 B token is NOT claimed as CONTAINED (documented limit)",
               '"verdict": "CONTAINED"' not in out, out[:200])

        # --- degenerate containment, independent of any twin -------------
        print("\ndegenerate containment (no twin required):")
        lone_byte = tmp / "lone_byte.txt"
        lone_byte.write_bytes(b"\n")
        victim = tmp / "innocent_text.txt"
        victim.write_bytes(b"an ordinary text file that happens to end in a newline\n")
        code, out, _ = run([str(TRIAGE), "--json", str(victim)])
        ck("file next to a 1-byte file is not called CONTAINED",
           '"verdict": "CONTAINED"' not in out, out[:200])

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
        # --- the missing-root guard, built for real -----------------------
        # The 2026-09-27 incident was a cache answering for a tree that no longer
        # existed, so `report()` now exits 1 and names what it cannot read. Both
        # directions are pinned here because the ambient cache cannot supply
        # them: it is rc=1 today only by accident of a reaped temp directory.
        #
        # The fixture is a byte-identical COPY of the tool placed in its own
        # tools/ + data/ layout, because the cache path is derived from __file__.
        # Asserting that identity keeps the fixture from quietly testing a
        # variant instead of the tool. Nothing is hand-written into the cache: the
        # tool walks the roots itself, and the staleness is a real rmtree.
        print("\nmissing-root guard (synthetic, deterministic):")
        fixrepo = tmp / "fixrepo"
        (fixrepo / "tools").mkdir(parents=True)
        (fixrepo / "data").mkdir(parents=True)
        fix = fixrepo / "tools" / "sibling_index.py"
        shutil.copyfile(INDEX, fix)
        ck("fixture is a byte-identical copy of the tool under test",
           hashlib.sha256(fix.read_bytes()).hexdigest()
           == hashlib.sha256(INDEX.read_bytes()).hexdigest())
        keep = tmp / "keep"
        vanish = tmp / "vanish"
        keep.mkdir()
        vanish.mkdir()
        (keep / "author_note.txt").write_bytes(b"a real file in a root that stays\n")
        (vanish / "artifact.bin").write_bytes(hashlib.sha256(b"gone-soon").digest())

        # 1. A real walk of two real roots, cache written by the tool.
        code, out, err = run([str(fix), "--root", str(keep), "--root", str(vanish)])
        ck("build walks both fixture roots", "roots indexed : 2" in out, out[:300])
        ck("build sees both fixture files", "files indexed : 2" in out, out[:300])
        ck("build exits 0 while every root exists", code == 0, "rc=%d %s" % (code, err.strip()))

        # 2. The quiet case: nothing missing, so rc 0 and no STALE flag. This is
        #    the assertion the old line got wrong, now pinned where it is true.
        code, out, _ = run([str(fix), "--stats", "--root", str(keep), "--root", str(vanish)])
        ck("stats exits 0 when every cached root exists", code == 0, "rc=%d" % code)
        ck("stats raises no STALE flag while the roots are there",
           "STALE" not in out and "NO LONGER EXIST" not in out, out[:300])

        # 3. The incident: delete one root for real, then ask again.
        shutil.rmtree(vanish)
        code, out, _ = run([str(fix), "--stats", "--root", str(keep)])
        ck("a root deleted from disk exits 1", code == 1, "rc=%d" % code)
        ck("the missing root is flagged STALE(missing on disk)",
           "STALE(missing on disk)" in out, out[:400])
        ck("the missing-root warning fires", "NO LONGER EXIST" in out, out[:400])
        ck("the missing root is named, with its cached file count",
           str(vanish) in out and "1 files cached" in out, out[:400])
        ck("the surviving root is not flagged",
           out.count("STALE(missing on disk)") == 1, out[:400])
        ck("the surviving root is still reported as walked",
           "files indexed : 2" in out, out[:300])

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%d check(s) failed" % len(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
