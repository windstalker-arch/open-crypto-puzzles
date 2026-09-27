#!/usr/bin/env python3
"""Mandatory pre-analysis gate for newly arrived files.

Why this exists
---------------
The recurring failure in this project is not a wrong answer, it is an expensive
answer to a question nobody asked. Concretely, on 2026-09-27 I ran entropy,
parity, XOR-residue and token-frequency analysis on a 2086-byte tail, concluded
it was a novel interleaved cipher, and only afterwards discovered the file was a
hex re-encoding of an artifact already in the ledger. The structure analysis was
worthless and the identity check that would have prevented it takes milliseconds.

The same shape has now appeared repeatedly:

  * a double-hash of a hash160, reported as a new address conflation;
  * a base58check omission, reported as a fabricated artifact;
  * a "5 segments" claim that was really 2 segments and a two-stage decode;
  * the hex-re-encoding above, missed because the twin lived in a sibling repo
    whose name differs from the working repo only by hyphens.

Every one of these is a verification step performed after, or instead of, the
step that mattered. This tool makes the cheap step the only step you can take
first: it classifies files by identity before it is possible to reason about
their contents, and it exits non-zero when something is not actually new.

How identity is decided
-----------------------
In descending order of confidence, and all by content rather than by filename:

  1. EXACT      - sha256 matches an indexed file.
  2. REENCODING - the file is hex or base64 text whose *decoded payload* hashes
                  to an indexed file. This is the case that a path search cannot
                  be relied on to catch, because the twin may live in any tree.
                  Reporting requires an actual index hit, so a file that merely
                  looks like hex costs nothing.
  3. CONTAINED  - the file's bytes occur inside an indexed file, or an indexed
                  file's bytes occur inside it. Catches verbatim excerpts and
                  re-wrapped fragments. Bounded by --max-scan-bytes because this
                  is the expensive step.
  4. DISTINCT   - none of the above. Only this verdict licenses further analysis.

The exit code is the gate. Non-zero means at least one input is already known
material, and analysing it as new would repeat the error this tool exists to
prevent. Use --force to proceed anyway, and say why in the ledger.

Run:
    python3 tools/triage_new.py FILE_OR_DIR [FILE_OR_DIR ...]
    python3 tools/triage_new.py --json FILE_OR_DIR
    python3 tools/triage_new.py --no-contain FILE_OR_DIR

Exit 0 if every input is DISTINCT, 1 if any input is already known, 2 on error.
"""
import argparse
import base64
import binascii
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sibling_index  # noqa: E402

DEFAULT_MAX_SCAN_BYTES = 2 * 1024 * 1024 * 1024
MIN_DECODE_LEN = 32
# A containment match must be a real excerpt, not a degenerate one. Without this
# floor a 1-byte file (a bare newline is common in these trees) is trivially a
# substring of every text file, and the tool confidently reports all of them as
# already held. That false positive was found on 2026-09-27: 20 unrelated files
# were all "contained in" a 1-byte author_nb_pw_battery.txt. Found by direct test,
# not by reading the output, which is the only reason it was caught at all.
MIN_CONTAINMENT_LEN = 64
HEX_RE = re.compile(rb"\A[0-9a-fA-F\s]+\Z")
B64_RE = re.compile(rb"\A[A-Za-z0-9+/=\s]+\Z")

# Verdict ordering, worst (most already-known) first.
RANK = {"CONTAINED": 0, "REENCODING": 1, "EXACT": 2, "DISTINCT": 3}
COLOUR = {"CONTAINED": "red", "REENCODING": "red", "EXACT": "red", "DISTINCT": "green"}


def short(path, limit=72):
    home = os.path.expanduser("~")
    text = path.replace(home, "~") if path.startswith(home) else path
    return text if len(text) <= limit else "..." + text[-(limit - 3):]


def candidate_decodings(data):
    """Yield (label, decoded_bytes) for plausible hex/base64 re-encodings.

    Only useful if the decoded payload actually hashes to something indexed, so
    this is deliberately permissive: a false candidate costs one hash.
    """
    squeezed = re.sub(rb"\s+", b"", data)
    if len(squeezed) >= MIN_DECODE_LEN and len(squeezed) % 2 == 0 and HEX_RE.match(data):
        try:
            yield "hex", binascii.unhexlify(squeezed)
        except (binascii.Error, ValueError):
            pass
    if len(squeezed) >= MIN_DECODE_LEN and B64_RE.match(data):
        padded = squeezed + b"=" * (-len(squeezed) % 4)
        try:
            decoded = base64.b64decode(padded, validate=True)
        except (binascii.Error, ValueError):
            return
        if len(decoded) >= MIN_DECODE_LEN:
            yield "base64", decoded


def index_by_sha(cache, exclude_inode=None):
    """sha256 -> paths, minus any path that IS the file being triaged.

    The index deliberately covers the source trees, so a file is normally present
    in it. A file therefore always "matches itself", which would make every
    verdict EXACT and the gate useless. Identity is compared by (dev, inode) as
    well as by path, so a copy reached through a different path -- an external
    card mounted at /storage/... while the index recorded /data/... -- is still
    reported as a twin, while the file itself never is.
    """
    out = {}
    for path, meta in cache["entries"].items():
        if exclude_inode is not None and same_file(path, exclude_inode):
            continue
        out.setdefault(meta["sha256"], []).append(path)
    return out


def same_file(path, ref):
    try:
        st = os.stat(path)
    except OSError:
        return False
    return (st.st_dev, st.st_ino) == ref


def classify(path, sha_index, held_reader, max_scan_bytes, do_contain):
    data = Path(path).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    ref = os.stat(path)
    ref_id = (ref.st_dev, ref.st_ino)

    hits = sha_index.get(digest)
    if hits:
        return {"file": path, "verdict": "EXACT", "size": len(data),
                "sha256": digest, "match": hits[0], "matches": hits,
                "encoding": None}

    for label, decoded in candidate_decodings(data):
        ddigest = hashlib.sha256(decoded).hexdigest()
        hits = sha_index.get(ddigest)
        if hits:
            return {"file": path, "verdict": "REENCODING", "size": len(data),
                    "sha256": digest, "match": hits[0], "matches": hits,
                    "encoding": "%s -> %d bytes" % (label, len(decoded))}

    if do_contain:
        found = held_reader(data)
        if found:
            return {"file": path, "verdict": "CONTAINED", "size": len(data),
                    "sha256": digest, "match": found, "matches": [found],
                    "encoding": None}

    return {"file": path, "verdict": "DISTINCT", "size": len(data),
            "sha256": digest, "match": None, "matches": [], "encoding": None}


def make_containment_reader(cache, max_scan_bytes):
    """Return data -> holding path, or None. Reads indexed files once, bounded.

    Files are visited smallest-first and the total read is capped, so a large
    binary tree cannot make this step unbounded. The cap is reported by the
    caller so a truncated containment scan is never mistaken for a clean one.
    """
    ordered = sorted(cache["entries"].items(), key=lambda kv: kv[1]["size"])
    state = {"budget": max_scan_bytes, "truncated": False, "scanned": 0}
    # Smallest-first maximises the number of candidates examined per byte spent.
    eligible = [(p, m) for p, m in ordered if 0 < m["size"] <= 8 * 1024 * 1024]

    def reader(data):
        if state["budget"] <= 0:
            state["truncated"] = True
            return None
        # Both sides of a containment claim must be substantial. A short new file
        # trivially sits inside a long container; a short container trivially sits
        # inside a long new file. Either degenerate direction is not evidence.
        if len(data) < MIN_CONTAINMENT_LEN:
            return None
        needle = data[:4096] if len(data) > 4096 else data
        for path, meta in eligible:
            size = meta["size"]
            if size < MIN_CONTAINMENT_LEN:
                continue
            if state["budget"] - size < 0:
                state["truncated"] = True
                break
            try:
                with open(path, "rb") as fh:
                    held = fh.read()
            except OSError:
                continue
            state["budget"] -= len(held)
            state["scanned"] += 1
            if len(data) >= len(held):
                if data in held:
                    return path
            else:
                if held in data:
                    return path
            if needle in held:
                # Prefilter hit: confirm the full containment properly.
                if data in held:
                    return path
        return None

    return reader, state


def collect_inputs(paths):
    out = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = sorted(d for d in dirnames if d != ".git")
                for name in sorted(filenames):
                    out.append(os.path.join(dirpath, name))
        elif p.exists():
            out.append(str(p))
        else:
            raise FileNotFoundError(raw)
    return sorted(set(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="+", help="files or directories to triage")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--no-contain", action="store_true",
                    help="skip the containment pass (much faster, misses excerpts)")
    ap.add_argument("--max-scan-bytes", type=int, default=DEFAULT_MAX_SCAN_BYTES)
    ap.add_argument("--force", action="store_true",
                    help="exit 0 even if something is not distinct")
    args = ap.parse_args()

    try:
        inputs = collect_inputs(args.paths)
    except FileNotFoundError as exc:
        print("no such path: %s" % exc, file=sys.stderr)
        return 2
    if not inputs:
        print("no files found", file=sys.stderr)
        return 2

    roots, unmatched = sibling_index.expand_roots(sibling_index.DEFAULT_ROOT_GLOBS,
                                                  sibling_index.SIBLING_BASE)
    for pattern in unmatched:
        print("WARNING: root pattern matched nothing: %s" % pattern, file=sys.stderr)
    cache = sibling_index.load_cache()
    if not cache["entries"]:
        print("(index empty; building -- this happens once)")
        cache = sibling_index.build(roots, sibling_index.DEFAULT_MAX_BYTES, quiet=True)

    state = None
    if args.no_contain:
        reader = lambda _d: None  # noqa: E731
    else:
        reader, state = make_containment_reader(cache, args.max_scan_bytes)

    results = []
    for path in inputs:
        try:
            ref = os.stat(path)
        except OSError as exc:
            print("unreadable: %s (%s)" % (path, exc), file=sys.stderr)
            return 2
        # Rebuild the sha view per file so each input excludes only itself.
        sha_index = index_by_sha(cache, (ref.st_dev, ref.st_ino))
        try:
            results.append(classify(path, sha_index, reader,
                                    args.max_scan_bytes, not args.no_contain))
        except OSError as exc:
            print("unreadable: %s (%s)" % (path, exc), file=sys.stderr)
            return 2

    results.sort(key=lambda r: (RANK[r["verdict"]], r["file"]))
    worst = results[0]["verdict"] if results else "DISTINCT"

    if args.as_json:
        print(json.dumps({"results": results, "worst": worst}, indent=2, sort_keys=True))
    else:
        print("%-9s %-10s %s" % ("VERDICT", "SIZE", "FILE"))
        for r in results:
            line = "%-9s %-10d %s" % (r["verdict"], r["size"], short(r["file"]))
            if r["verdict"] != "DISTINCT":
                line += "\n          -> already held as: %s" % short(r["match"])
                if r["encoding"]:
                    line += "   (%s)" % r["encoding"]
            print(line)
        if state is not None and state["truncated"]:
            print("\nnote: containment scan hit --max-scan-bytes; some files were not "
                  "examined, so CONTAINED negatives are weaker than they look.")
        print("\n%d file(s); %d distinct, %d already known"
              % (len(results),
                 sum(1 for r in results if r["verdict"] == "DISTINCT"),
                 sum(1 for r in results if r["verdict"] != "DISTINCT")))

    if worst != "DISTINCT" and not args.force:
        print("\nGATE: %s material is already held. Analysing it as new repeats the "
              "2026-09-27 phase3.2.hex error.\n      Use --force only with a reason recorded "
              "in analysis/tested.md." % worst, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
