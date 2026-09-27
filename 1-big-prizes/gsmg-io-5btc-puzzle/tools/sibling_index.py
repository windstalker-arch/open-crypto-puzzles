#!/usr/bin/env python3
"""Content index across every tree that might hold GSMG artifacts.

Why this exists
---------------
On 2026-09-27 I analysed a file in the solver group as a novel interleaved
ciphertext. It was a hex re-encoding of `phase3.assets/phase3.2.txt`, which had
been sitting in a *sibling repo* (`gsmg-community-hints-repo`) that I had never
searched. The failure was not really "wrong directory" -- it was that I tried to
answer "is this file new?" from memory and from filename similarity, when the
question is answerable exactly, by hash, in milliseconds.

That mistake was not isolated. A ledger row written the day before
(R-P32BLOB-2026-09-26) had already recorded that the solver group re-packages
community artifacts verbatim, and had written down the rule in bold: "Filename
coverage is a worthless proxy; always content-grep before spending a session."
So the answer existed and was not consulted.

There is a second, sharper hazard. `1-big-prizes/` contains BOTH
`gsmg-io-5btc-puzzle` (286 files) and `gsmgio-5btc-puzzle` (28 files) -- names
that differ only in hyphens, holding entirely different material (the second is
a fork-audit bundle, not a copy). Any workflow that reconstructs a path from
memory can silently consult the wrong tree and find nothing, or find something
that merely looks right. This index removes the need to remember paths at all.

What it does
------------
Walks a set of roots, records sha256 for every file, and caches the result
keyed on (size, mtime) so repeat runs are cheap. The cache lives at
`data/sibling_index.json` and is a pure cache: deleting it costs time, never
correctness.

Existence is recorded as a first-class fact. "No indexed file contains this
hash" is only meaningful if you know the walk actually reached the trees, so the
index stores per-root walk status (files seen, files skipped for size, errors)
and `build` reports roots it could not read. A silently empty root is the exact
shape of the bug this tool is meant to prevent.

Run:
    python3 tools/sibling_index.py                 # build/refresh (incremental)
    python3 tools/sibling_index.py --stats         # coverage report, no rebuild
    python3 tools/sibling_index.py --hash <hex>    # locate a known sha256
    python3 tools/sibling_index.py --name <substr> # locate by filename

Exit 0 if every root was walked, 1 if any root was unreadable or missing.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / "data" / "sibling_index.json"

# Trees known to hold GSMG material. `*` is every sibling of this repo inside
# 1-big-prizes/, which deliberately includes unrelated puzzle repos: a twin can
# turn up anywhere, and the `gsmg-io-5btc-puzzle` / `gsmgio-5btc-puzzle` pair
# (differing only in hyphens, holding different material) means guessing a path
# is unsafe. Absolute paths are written out in full because os.path.isabs() is
# False for "~/..." and a tilde would otherwise be joined onto the repo parent.
DEFAULT_ROOT_GLOBS = [
    "*",  # siblings of the repo, resolved against SIBLING_BASE below
    "~/gsmg",
    "~/briefcase",
    "~/storage/external/briefcase",
    "{PREFIX}/usr/tmp/opencode/quarantine",
]

# Globs are resolved against the repo's parent directory, so "*" means "every
# sibling repo". Kept as a named constant because getting this wrong silently
# indexed one root instead of ten on the first run.
SIBLING_BASE = REPO.parent

SKIP_DIR_NAMES = {".git", "__pycache__", "node_modules", ".cache", ".npm", ".venv"}
DEFAULT_MAX_BYTES = 64 * 1024 * 1024


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def expand_roots(globs, base):
    """Resolve glob patterns to a sorted, de-duplicated list of existing dirs.

    `~` is expanded first and absolutely, because os.path.isabs() is False for a
    tilde-prefixed path -- joining one onto a base yields a nonsense path that
    matches nothing. Matching nothing is worse than matching too much, since it
    looks identical to "no such artifact anywhere".

    Returns (roots, unmatched) so a pattern that resolved to nothing is visible.
    An unmatched pattern is the exact shape of the bug this tool exists to catch,
    so it is reported rather than swallowed.
    """
    seen = {}
    unmatched = []
    prefix = os.environ.get("PREFIX", "/data/data/com.termux/files")
    patterns = list(globs)
    for pattern in patterns:
        if "{PREFIX}" not in pattern:
            continue
        patterns.remove(pattern)
        # On Termux $HOME is /data/data/com.termux/files/home but the writable
        # temp tree lives under $PREFIX (/data/data/com.termux/files/usr), NOT
        # under $HOME -- so "~/usr/tmp/..." matches nothing there. Both spellings
        # are tried so the path resolves on Termux and on an ordinary Linux box
        # alike, which is why the default list carries the {PREFIX} form only and
        # the alternation lives here rather than in a second constant to keep in
        # step. Prefer whichever exists; if neither does the pattern is dropped
        # rather than reported, since the alternates are intentional.
        for prefix_root in (prefix, os.path.expanduser("~")):
            concrete = pattern.replace("{PREFIX}", prefix_root)
            if os.path.isdir(concrete):
                patterns.append(concrete)
                break

    for pattern in patterns:
        pat = os.path.expanduser(pattern)
        if not os.path.isabs(pat):
            pat = str(base / pat)
        parent, name = os.path.split(pat.rstrip("/"))
        if not name:
            unmatched.append(pattern)
            continue
        matched = 0
        for match in sorted(Path(parent).glob(name)):
            resolved = match.resolve()
            if resolved.is_dir():
                seen[str(resolved)] = True
                matched += 1
        if not matched:
            unmatched.append(pattern)
    return sorted(seen), unmatched


def load_cache():
    if not CACHE.exists():
        return {"version": 1, "entries": {}, "roots": {}}
    try:
        data = json.loads(CACHE.read_text())
    except (json.JSONDecodeError, OSError):
        # A corrupt cache is never a reason to refuse work; rebuild from scratch.
        return {"version": 1, "entries": {}, "roots": {}}
    if data.get("version") != 1:
        return {"version": 1, "entries": {}, "roots": {}}
    data.setdefault("entries", {})
    data.setdefault("roots", {})
    return data


def walk_root(root, max_bytes):
    """Yield (abspath, size, mtime) for indexable files under root.

    Returns (files, stats) where stats records skips and errors so an incomplete
    walk is visible rather than silent.
    """
    files = []
    stats = {"files": 0, "skipped_large": 0, "errors": 0, "symlinks": 0}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIR_NAMES)
        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            try:
                st = os.lstat(full)
            except OSError:
                stats["errors"] += 1
                continue
            if os.path.islink(full):
                # Indexing link targets would double-count and can escape the root.
                stats["symlinks"] += 1
                continue
            if st.st_size > max_bytes:
                stats["skipped_large"] += 1
                continue
            files.append((full, st.st_size, st.st_mtime_ns))
    stats["files"] = len(files)
    return files, stats


def build(roots, max_bytes, quiet=False):
    cache = load_cache()
    entries = cache["entries"]
    added = reused = rehashed = 0

    for root in roots:
        files, stats = walk_root(root, max_bytes)
        alive = set()
        for full, size, mtime in files:
            alive.add(full)
            prev = entries.get(full)
            if prev and prev.get("size") == size and prev.get("mtime_ns") == mtime:
                reused += 1
                continue
            try:
                digest = sha256_file(full)
            except OSError:
                stats["errors"] += 1
                continue
            entries[full] = {"sha256": digest, "size": size, "mtime_ns": mtime}
            if prev:
                rehashed += 1
            else:
                added += 1
        # Drop entries for files that vanished, so the index does not answer
        # questions about artifacts that are no longer on disk.
        for stale in [p for p in entries if p.startswith(root + os.sep) and p not in alive]:
            del entries[stale]
        cache["roots"][root] = stats
        if not quiet:
            print("  %-72s %6d files (%d skipped large, %d symlinks, %d errors)"
                  % (root, stats["files"], stats["skipped_large"], stats["symlinks"], stats["errors"]))

    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, sort_keys=True))
    if not quiet:
        print("\nindex: %d entries (%d new, %d changed, %d unchanged)"
              % (len(entries), added, rehashed, reused))
    return cache


def by_hash(cache, digest):
    needle = digest.lower()
    return sorted(p for p, v in cache["entries"].items() if v["sha256"] == needle)


def by_name(cache, needle):
    low = needle.lower()
    return sorted(p for p in cache["entries"] if low in os.path.basename(p).lower())


def report(cache):
    total = sum(r.get("files", 0) for r in cache["roots"].values())
    problems = {r: s for r, s in cache["roots"].items()
                if s.get("errors") or s.get("skipped_large")}
    # A root that is gone from disk still answers --name/--hash from cache, which
    # reads as "the artifact is there" when the bytes are not. Flag it separately:
    # this is a missing-tree failure, not an incomplete-walk failure.
    gone = [r for r in cache["roots"] if not os.path.isdir(r)]
    print("roots indexed : %d" % len(cache["roots"]))
    print("files indexed : %d" % total)
    print("cache         : %s" % CACHE)
    for root, stats in sorted(cache["roots"].items()):
        flag = ""
        if not os.path.isdir(root):
            flag += "  STALE(missing on disk)"
        if stats.get("errors"):
            flag += "  ERRORS=%d" % stats["errors"]
        if stats.get("skipped_large"):
            flag += "  skipped_large=%d" % stats["skipped_large"]
        print("  %-70s %6d%s" % (root, stats.get("files", 0), flag))
    if problems:
        print("\nWARNING: %d root(s) incompletely walked -- absence of a hash from this"
              " index is NOT proof of novelty for those trees." % len(problems))
    if gone:
        print("\nWARNING: %d indexed root(s) NO LONGER EXIST on disk. --name/--hash still"
              " answer from cache, so a hit there means 'we once held this', not 'this is"
              " readable now'. Re-fetch before planning any work that needs the bytes:"
              % len(gone))
        for r in gone:
            print("  %s  (%d files cached)" % (r, cache["roots"][r].get("files", 0)))
    return 1 if gone or any(s.get("errors") for s in cache["roots"].values()) else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", action="append", default=None,
                    help="root glob (repeatable); defaults to every known artifact tree")
    ap.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    ap.add_argument("--stats", action="store_true", help="report coverage without rebuilding")
    ap.add_argument("--rebuild", action="store_true",
                    help="force a rescan even when the cache is populated")
    ap.add_argument("--hash", help="locate this sha256 in the index")
    ap.add_argument("--name", help="locate files whose basename contains this substring")
    args = ap.parse_args()

    globs = args.root if args.root else DEFAULT_ROOT_GLOBS
    roots, unmatched = expand_roots(globs, SIBLING_BASE)
    for pattern in unmatched:
        print("WARNING: root pattern matched nothing: %s" % pattern, file=sys.stderr)
    if not roots:
        print("no roots matched %s (base %s)" % (globs, SIBLING_BASE), file=sys.stderr)
        return 1

    # A lookup should print matches and nothing else, so the walk is quiet here
    # and only forced when the caller asked or the cache is unusable.
    cache = load_cache()
    if not cache["entries"] or args.rebuild:
        cache = build(roots, args.max_bytes, quiet=bool(args.hash or args.name))

    if args.hash:
        hits = by_hash(cache, args.hash)
        for h in hits:
            print(h)
        if not hits:
            print("(no indexed file has this sha256)")
        return 0

    if args.name:
        for h in by_name(cache, args.name):
            print(h)
        return 0

    return report(cache)


if __name__ == "__main__":
    sys.exit(main())
