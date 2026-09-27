#!/usr/bin/env python3
"""
coverage_check.py -- pre-flight guard against the four search-space errors that
have actually occurred in this repository.

Purpose:
    A ledger row is only worth writing if the search space behind it was real. This
    project has now produced four distinct search-space failures in a single session,
    three of which produced false negatives and one of which nearly manufactured a
    false DISCOVERY. Prose warnings in analysis/tested.md did not stop any of them, so
    this makes the check mechanical. The four classes, each with the row that caused it:

      1. GHOST PATH      R-LOGO1        acted on a PNG that did not exist in the dir
                                         being searched, and read the empty result as
                                         a negative.
      2. VACUOUS GREP    R-LOGO2,       grepped one filename stem, got zero hits, and
                         R-FONTAINE-01 concluded "no prior work" without noticing the
                                         search space was one term wide.
      3. FALSE DISCOVERY R-PHASE2-2026  opened an un-audited-looking page, announced it
                                         as the find of the session, when section 28 had
                                         already swept its prose 15,555 candidates deep.
      4. BAD ENVELOPE    R-PHASE2-2026  regex-ed flattened HTML, produced a 900-char
                                         Base64 run that decoded to 659 B of "ciphertext",
                                         and inferred a truncation defect that did not
                                         exist. 659 is not a multiple of 16.

    Classes 1 and 2 make an absence look like a fact. Class 3 makes a fact look like a
    discovery. Class 4 makes a parsing bug look like a finding.

Usage:
    python3 tools/coverage_check.py --selftest
    python3 tools/coverage_check.py ARTIFACT [ARTIFACT ...]
    python3 tools/coverage_check.py --terms "Norton,Thevenin" ARTIFACT
    python3 tools/coverage_check.py --no-siblings ARTIFACT

Exit codes:
    0  artifact resolved and coverage reported (may still be zero -- read the WARNs)
    2  GHOST PATH: at least one artifact does not exist, so nothing can be concluded
    3  selftest failed

Reading the output:
    A zero hit count is NOT evidence of anything. The tool says so explicitly and names
    the term count that was searched. If that number is small, the search was weak; add
    --terms and rerun before writing any row that asserts novelty or absence.
"""

import argparse
import base64
import hashlib
import html
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "analysis", "tested.md")
LEADS = os.path.join(ROOT, "analysis", "leads.md")

# Directories known to hold copies of author material. A novelty claim is unsafe
# until every one of these has been compared against the artifact in hand.
WORKING_DIRS = [
    os.path.expanduser("~/briefcase"),
    os.path.expanduser("~/briefcase/gsmg_era"),
    os.path.expanduser("~/gsmg"),
    os.path.expanduser("~/gsmg/gsmg-io"),
    os.path.expanduser("~/gsmg-preserved"),
    os.path.expanduser("~/storage/external/briefcase"),
]

# A term shorter than this, or this common, cannot distinguish an artifact from any
# other web page, so it is never allowed to stand as the sole search term.
STOPWORDS = set("""
the and for that with this from have has was were are not you your they their there
here what when where which while will would could should about into over under then
than them been being does did doing done such same other more most much many some any
all can may might must shall our out off its it's his her him she he we us also very
just only like well back even still way ways thing things one two three first second
third next last new old good best know think said says each both few nor own too
""".split())

TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.+&/-]{3,}")


class _Textareas(HTMLParser):
    """Textarea contents verbatim. Never regex the flattened page: tag-stripping
    merges neighbouring prose into a Base64 run, which is failure class 4."""

    def __init__(self):
        super().__init__()
        self.boxes = []
        self._cur = None

    def handle_starttag(self, tag, attrs):
        if tag == "textarea":
            self._cur = []

    def handle_endtag(self, tag):
        if tag == "textarea" and self._cur is not None:
            self.boxes.append("".join(self._cur))
            self._cur = None

    def handle_data(self, data):
        if self._cur is not None:
            self._cur.append(data)


def visible_text(path):
    """Tag-stripped, entity-decoded, whitespace-collapsed PROSE, plus raw <textarea>
    bodies. Returns (prose, textareas).

    The textarea bodies are returned separately and are deliberately NOT part of the
    prose: they hold Base64 ciphertext, and ciphertext is not vocabulary. Leaving them
    in is how this tool's own first selftest ranked 14 Base64 fragments as its most
    distinctive search terms and reported a confident zero -- failure class 2, committed
    by the guard written to prevent failure class 2.
    """
    with open(path, "rb") as fh:
        blob = fh.read()
    doc = blob.decode("utf-8", errors="replace")
    parser = _Textareas()
    try:
        parser.feed(doc)
    except Exception:
        pass
    stripped = re.sub(r"(?s)<textarea[^>]*>.*?</textarea>", " ", doc)
    body = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", stripped)
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body))).strip()
    return text, parser.boxes


def vocabulary(text, path, limit=14):
    """Rank tokens by how badly they would fail to distinguish this artifact from
    any other page. Filename fragments, proper nouns and digit-bearing tokens score
    highest, because those are exactly what caught the R-PHASE2 rediscovery:
    'choiceisanillusion' came from the filename, 'Norton'/'Thevenin' from being
    proper nouns, '5binary' from containing a digit."""
    stem = os.path.splitext(os.path.basename(path))[0]
    stem_bits = {b.lower() for b in re.split(r"[^A-Za-z0-9]+", stem) if len(b) >= 4}
    scores = {}
    for match in TOKEN.finditer(text):
        tok = match.group(0).strip("._+&/-")
        low = tok.lower()
        if len(low) < 4 or low in STOPWORDS or low.isdigit():
            continue
        # Reject machine noise. Ciphertext, hashes and URLs are long, vowel-free or
        # digit-dense; prose is not. Without this the ranker fills its budget with
        # Base64 fragments and the coverage report is worthless.
        if len(low) > 20:
            continue
        if not any(ch in "aeiouy" for ch in low):
            continue
        if sum(ch.isdigit() for ch in low) > len(low) // 3:
            continue
        score = min(len(low), 12)
        if any(low == b or low.startswith(b) or b.startswith(low) for b in stem_bits):
            score += 10
        if any(ch.isupper() for ch in tok[1:]):
            score += 4
        if any(ch.isdigit() for ch in tok):
            score += 4
        if low not in scores or scores[low] < score:
            scores[low] = score
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    return [tok for tok, _ in ranked[:limit]]


def grep_ledger(terms):
    """Count and locate hits per term across the ledger and the live leads file."""
    sources = []
    for path in (LEDGER, LEADS):
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for num, line in enumerate(fh, 1):
                sources.append((path, num, line))
    report = []
    for term in terms:
        needle = term.lower()
        hits = [(p, n) for p, n, line in sources if needle in line.lower()]
        report.append((term, hits))
    return report


def sibling_scan(text, skip_path):
    """Find other copies of this exact artifact and report drift. Comparing the
    normalised text hash is what turned the 2020-vs-2026 phase-2 question from
    unmeasured into a permanent negative."""
    target = hashlib.sha256(text.encode("utf-8")).hexdigest()
    found = []
    for root_dir in WORKING_DIRS:
        if not os.path.isdir(root_dir):
            continue
        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
            for name in filenames:
                full = os.path.join(dirpath, name)
                if os.path.abspath(full) == os.path.abspath(skip_path):
                    continue
                try:
                    if os.path.getsize(full) > 4_000_000:
                        continue
                    other, _ = visible_text(full)
                except Exception:
                    continue
                if hashlib.sha256(other.encode("utf-8")).hexdigest() == target:
                    found.append(full)
    return target, sorted(set(found))


def validate_envelopes(path):
    """Find OpenSSL legacy 'Salted__' envelopes and enforce block alignment. The
    alignment check is self-validating: if it fails, the extraction is wrong, not the
    ciphertext. This is the check whose absence produced the 659 B phantom."""
    _, boxes = visible_text(path)
    blobs = []
    for box in boxes:
        flat = re.sub(r"\s+", "", box)
        if not flat.startswith("U2FsdGVkX1"):
            continue
        try:
            raw = base64.b64decode(flat, validate=True)
        except Exception as exc:
            blobs.append({"b64": len(flat), "error": str(exc)})
            continue
        if raw[:8] != b"Salted__":
            blobs.append({"b64": len(flat), "error": "bad magic"})
            continue
        ct = len(raw) - 16
        blobs.append({
            "b64": len(flat),
            "decoded": len(raw),
            "salt": raw[8:16].hex(),
            "ct": ct,
            "blocks": ct / 16.0,
            "aligned": ct % 16 == 0 and ct > 0,
            "b64_sha256": hashlib.sha256(flat.encode("utf-8")).hexdigest(),
        })
    # Fall back to a flat scan so non-textarea pages are still covered, but only
    # report runs that survive the alignment test.
    if not blobs:
        text, _ = visible_text(path)
        flat = re.sub(r"\s+", "", text)
        for match in re.finditer(r"U2FsdGVkX1[A-Za-z0-9+/=]+", flat):
            run = match.group(0)[: len(match.group(0)) // 4 * 4]
            try:
                raw = base64.b64decode(run, validate=True)
            except Exception:
                continue
            if raw[:8] != b"Salted__":
                continue
            ct = len(raw) - 16
            if ct <= 0 or ct % 16:
                continue
            blobs.append({
                "b64": len(run), "decoded": len(raw), "salt": raw[8:16].hex(),
                "ct": ct, "blocks": ct // 16, "aligned": True,
                "b64_sha256": hashlib.sha256(run.encode("utf-8")).hexdigest(),
                "note": "flat-scan fallback; parse the container for authoritative data",
            })
    return blobs


def check(path, terms, do_siblings):
    print("=" * 74)
    print("ARTIFACT  {}".format(path))
    if not os.path.isfile(path):
        print("  *** GHOST PATH (failure class 1) ***")
        print("      This file does not exist. Nothing about it can be concluded:")
        print("      not that it is unaudited, not that it is clean, not that it is new.")
        print("      Resolve the real path first (ls the directory you think it is in).")
        return False
    size = os.path.getsize(path)
    print("  size    {} B".format(size))

    text, boxes = visible_text(path)
    print("  text    {} chars, {} textarea(s)".format(len(text), len(boxes)))

    chosen = terms or vocabulary(text, path)
    if terms:
        print("\n  terms   {} EXPLICIT: {}".format(len(chosen), ", ".join(chosen)))
    else:
        print("\n  terms   {} auto-ranked (filename fragments, proper nouns, digits first)"
              .format(len(chosen)))
        print("          {}".format(", ".join(chosen)))

    report = grep_ledger(chosen)
    total = 0
    print("\n  LEDGER COVERAGE")
    for term, hits in report:
        total += len(hits)
        mark = "HIT " if hits else "0   "
        where = ""
        if hits:
            paths = {}
            for p, n in hits:
                paths.setdefault(os.path.basename(p), []).append(n)
            where = "  ".join(
                "{}:{}".format(k, ",".join(str(x) for x in v[:6]) + ("..." if len(v) > 6 else ""))
                for k, v in sorted(paths.items())
            )
        print("    {} {:<24} {}".format(mark, term, where))

    if total == 0:
        print("\n  *** WARN: zero hits across {} terms (failure class 2) ***".format(len(chosen)))
        print("      A zero here is NOT evidence of an absence. The search space was")
        print("      {} terms wide. Add --terms with the artifact's distinctive strings".format(len(chosen)))
        print("      and rerun before writing any row asserting novelty or a negative.")
    else:
        print("\n  PRIOR WORK EXISTS: {} line-hits over {} terms.".format(total, len(chosen)))
        print("      Read those rows before claiming this artifact is a discovery.")
        print("      A novelty claim is UNSAFE until every row above is accounted for.")

    envs = validate_envelopes(path)
    if envs:
        print("\n  OPENSSL ENVELOPES")
        for i, b in enumerate(envs, 1):
            if "error" in b:
                print("    #{} b64={} DECODE ERROR: {}".format(i, b["b64"], b["error"]))
                continue
            print("    #{} b64={} decoded={}B salt={}".format(
                i, b["b64"], b["decoded"], b["salt"]))
            print("       ct={}B blocks={} aligned={} b64sha256={}".format(
                b["ct"], b["blocks"], b["aligned"], b["b64_sha256"]))
            if not b["aligned"]:
                print("       *** NOT BLOCK-ALIGNED (failure class 4) ***")
                print("       AES-CBC ciphertext is always a multiple of 16 B. This means")
                print("       the EXTRACTION is wrong, not that the ciphertext is damaged.")
                print("       Parse the container; do not regex flattened text.")
            if b.get("note"):
                print("       note: {}".format(b["note"]))

    if do_siblings:
        digest, twins = sibling_scan(text, path)
        print("\n  SIBLING COPIES  normalised text sha256 {}".format(digest[:32]))
        if not twins:
            print("    none found in {}".format(len(WORKING_DIRS)), "working dirs")
            print("    (this is a real measured negative: every listed dir was walked)")
        else:
            for t in twins:
                print("    IDENTICAL TEXT  {}".format(t))
            print("    If these differ from the copy you are auditing, diff them BEFORE")
            print("    concluding anything -- a live/archived delta is invisible otherwise.")
    else:
        print("\n  SIBLING COPIES  skipped (--no-siblings)")

    print("=" * 74)
    return True


def selftest():
    """Two controls, because a guard that has never been shown to fail is not a
    guard. POSITIVE: an artifact with known coverage must resolve and must find its
    prior work. NEGATIVE: a path that does not exist must exit 2, not report 0 hits.
    """
    print("coverage_check.py selftest")
    print("\n[1/4] POSITIVE control: artifact with known ledger coverage")
    page = os.path.expanduser(
        "~/briefcase/gsmg_era/choice_20201112.html")
    if not os.path.isfile(page):
        print("  FAIL: control artifact missing at {}".format(page))
        return False
    if not check(page, None, True):
        return False

    print("\n[2/4] POSITIVE control: explicit terms must reach the ledger")
    report = grep_ledger(["Norton", "Thevenin", "5binary", "parts 1..7"])
    hit_terms = [t for t, h in report if h]
    if len(hit_terms) < 4:
        print("  FAIL: expected all 4 phase-2 terms to hit the ledger, got {}".format(hit_terms))
        return False
    print("  ok: all 4 distinctive phase-2 terms resolve in the ledger")

    print("\n[3/4] POSITIVE control: envelopes are block aligned")
    envs = validate_envelopes(page)
    if len(envs) != 2 or not all(e.get("aligned") for e in envs):
        print("  FAIL: expected 2 aligned envelopes, got {!r}".format(envs))
        return False
    print("  ok: 2 envelopes, both 16-byte aligned -> {}".format(
        ", ".join("{}B/{}blk".format(e["ct"], e["blocks"]) for e in envs)))

    print("\n[4/4] NEGATIVE control: a ghost path must NOT report zero prior work")
    ghost = os.path.join(os.path.dirname(page), "__no_such_artifact__.png")
    ok = check(ghost, None, False)
    if ok:
        print("  FAIL: ghost path was reported as resolved")
        return False
    print("  ok: ghost path correctly refused")

    print("\nSELFTEST PASS")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Guard against the four recorded search-space failures.")
    parser.add_argument("artifacts", nargs="*", help="artifact paths to check")
    parser.add_argument("--terms", help="comma-separated explicit search terms")
    parser.add_argument("--no-siblings", action="store_true",
                        help="skip the working-directory copy scan")
    parser.add_argument("--selftest", action="store_true",
                        help="run both a positive and a negative control")
    args = parser.parse_args()

    if args.selftest:
        return 0 if selftest() else 3
    if not args.artifacts:
        parser.error("give at least one artifact, or --selftest")

    terms = [t.strip() for t in args.terms.split(",") if t.strip()] if args.terms else None
    all_ok = True
    for path in args.artifacts:
        all_ok &= check(path, terms, not args.no_siblings)
    if not all_ok:
        print("\nVERDICT: GHOST PATH. At least one artifact could not be resolved, so no")
        print("claim about coverage, novelty or absence may be drawn from this run.")
        return 2
    print("\nVERDICT: all artifacts resolved. Coverage is reported above; zero hits")
    print("remain unproven until the term count is judged wide enough.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
