#!/usr/bin/env python3
"""ANTIYBCORETNT: dbbib 7x13 column sums as zero-based-from-end word indices into the
Architect-adapted final-page text preceding the modified SELECT section.

    from data/finalpage-digit-streams.json   -> dbbib_91 (91 tokens, live page ground truth)
    first-appearance alphabet               -> DBIFHCEG = 0..8
    7x13 row-major grid, column sums         -> 13 numbers in 11..38
    zero-based-from-end word selection       -> 13 words
    first letter of each                     -> ANTIYBCORETNT

WHAT THIS SCRIPT IS FOR. Not to claim the decode. It exists because the claim was
made with the wrong control (a dbbib shuffle) and the right control was not run.
The extraction is fully DETERMINISTIC: there is no randomness in it at all. The
real multiplicity is over the free choice the extractor made -- WHICH WORD THE
SPAN ENDS ON -- so that is what this sweeps, against two English word lists.

Provenance: three independent transcriptions of the Architect monologue are loaded
and required to agree on the 13 selected words. The strongest is CORRECT.BIN, the
decrypted ASCII trailer of the SalPhaseIon AES blob (Tahap 14 - Cosmic Duality).
The three differ (twentythree / twenty-three, bruteforcing / brute forcing,
will power / willpower, wiseman / wise man, lifetime / life time), so this also
tests whether the extraction survives transcription noise.

Oracle: 0 calls. Nothing here is submitted anywhere; this is a structure check.
Run:  python3 tools/dbbib_7x13_wordindex.py
"""
import json
import pathlib
import re
import subprocess

BASE = pathlib.Path(__file__).resolve().parents[1]
HOME = pathlib.Path.home()

# --- the 13 column sums, stated independently of the script so the script
# --- actually has to reproduce them rather than inherit them
CLAIMED_COLSUMS = [19, 27, 26, 34, 13, 38, 11, 31, 25, 37, 18, 27, 33]
CLAIMED_OUTPUT = "ANTIYBCORETNT"

ROWS, COLS = 7, 13

# --- three sources, best provenance last
SOURCES = {
    "bookcipher_words_clean": HOME / "gsmg/bookcipher/beaufort_words_clean.csv",
    "community_phase3.2_notebook": HOME
    / "open-crypto-puzzles/1-big-prizes/gsmg-community-hints-repo/phase3.2.ipynb",
    "briefcase_CORRECT.BIN_trailer": HOME / "briefcase/gsmg_issues_all.json",
}
SELECT_MARKER = "select from over"


def norm(s: str) -> str:
    # CORRECT.BIN arrives as a JSON-embedded blob whose newlines are still the
    # two-character escape "\n"; unescape before the non-alpha sweep or the
    # literal 'n' fuses onto the following word ("nnow").
    s = s.replace("\\n", "\n").replace("\\r", "\n")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", s.lower())).strip()


def architect_text(path: pathlib.Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".ipynb":
        chunks = []
        for c in json.loads(raw).get("cells", []):
            chunks.append("".join(c.get("source", [])))
            o = c.get("outputs") or []
            for out in o:
                t = out.get("text") or (out.get("data", {}) or {}).get("text/plain") or []
                chunks.append("".join(t) if isinstance(t, list) else str(t))
        raw = "\n".join(x for x in chunks if x)
    i = raw.lower().find("exceedingly efficient")
    assert i >= 0, f"no Architect monologue in {path}"
    return norm(raw[i - 200 :])  # a little left context so the window is covered


def preselect_words(t: str):
    """word list of the text BEFORE the modified SELECT section"""
    i = t.find(SELECT_MARKER)
    assert i >= 0, f"no '{SELECT_MARKER}' marker"
    return t[:i].split()


# --- 1. the stream and the alphabet
d = json.loads((BASE / "data" / "finalpage-digit-streams.json").read_text())
A = d["dbbib_91"]
assert len(A) == ROWS * COLS == 91, len(A)

first: dict[str, int] = {}
for ch in A:
    first.setdefault(ch, len(first))
ALPHA = {ch: v for ch, v in first.items()}
print("alphabet (first appearance):", "".join(first), "->", ALPHA)
assert "".join(first) == "dbifhcega", first
# and it is the Bifid-square order already logged as a lead, not a new find
assert d["canonical_value_mapping"]["note"].startswith("proposed by the puzzle")

# --- 2. the grid and the column sums
grid = [[ALPHA[c] for c in A[r * COLS : (r + 1) * COLS]] for r in range(ROWS)]
for r in grid:
    print("  ", "".join(str(v) for v in r))
colsums = [sum(grid[r][c] for r in range(ROWS)) for c in range(COLS)]
print("column sums:", colsums)
assert colsums == CLAIMED_COLSUMS, colsums
assert sum(colsums) == 339 == sum(ALPHA[c] for c in A)  # sanity: sums partition the stream

# --- 3. the word selection, across all three transcriptions
def dictionary_words(candidates):
    """Which of `candidates` the SYSTEM dictionary (hunspell en_US) accepts.

    `hunspell -l` prints the words it does NOT recognise, so membership is the
    complement. Going through hunspell rather than a hand-picked list means the
    scoring cannot be tuned by choosing which words count -- and affix rules are
    applied, so "its"/"his" are recognised while they are absent as bare .dic
    lines. No wordlist is stored in this repo.
    """
    out = subprocess.run(
        ["hunspell", "-l", "-d", "en_US"],
        input="\n".join(sorted(candidates)) + "\n",
        capture_output=True,
        text=True,
    )
    unknown = {u.lower() for u in out.stdout.split()}
    assert out.returncode == 0, out.stderr
    known = {c for c in candidates if c.lower() not in unknown}
    # CANARY. This exact bug shipped once: hunspell echoes unknowns in the input's
    # case, so matching its output against lowercased candidates marked every
    # candidate as a dictionary word and printed "1670 candidates, 1670 in
    # dictionary". An impossible score must fail loudly rather than be read.
    assert unknown, "hunspell reported no unknowns -- the membership test is broken"
    assert len(known) < len(candidates), f"everything matched ({len(known)}/{len(candidates)}) -- test is broken"
    assert len(known) > 0, "nothing matched either -- dictionary unusable"
    return known


def substrings(s, n):
    return {s[i : i + n] for i in range(len(s) - n + 1)}


def select(w, cols, end):
    """end = index of the span's last word; all indices are from the end, 0-based"""
    if end - max(cols) < 0:
        return None
    return [w[end - c] for c in cols]


results = {}
for name, path in SOURCES.items():
    w = preselect_words(architect_text(path))
    end = len(w) - 1
    sel = select(w, colsums, end)
    out = "".join(x[0] for x in sel).upper()
    results[name] = (w, end, sel, out)
    print(f"\n[{name}]  span={len(w)} words  end-anchor={end}")
    print("  words:", " / ".join(x.upper() for x in sel))
    print("  out  :", out, "<-- MATCHES CLAIM" if out == CLAIMED_OUTPUT else "<-- DIFFERS")
    lo, hi = min(colsums), max(colsums)
    print(f"  window ({min(colsums)+1}th..{max(colsums)+1}th from end): " + " ".join(w[end - hi : end - lo + 1]))

outs = {v[3] for v in results.values()}
assert outs == {CLAIMED_OUTPUT}, f"transcription-sensitive! {outs}"
print(f"\nall {len(SOURCES)} independent transcriptions agree on {CLAIMED_OUTPUT}")
print("NOTE: this is robustness to transcription noise, NOT independent confirmation --")
print("      all three are the same underlying monologue.")

# --- 4. the control that should have been run: sweep the span end-anchor
#
# The free choice the extractor made is WHICH WORD THE SPAN ENDS ON. The span is
# "the Architect text immediately before the modified SELECT section", so the
# honest search space is the end-anchors of the FINAL PAGE's pre-SELECT span
# (255 words -> 217 valid anchors). Anything wider is invalid: an earlier draft of
# this script swept the whole 55,682-word community walkthrough notebook and
# reported p = 1/55644. That number is meaningless -- the extractor never saw that
# text, and widening the domain after seeing a result inflates significance
# rather than measuring it. The domain is fixed by the method, not by the outcome.
#
# The free choice the extractor made is WHICH WORD THE SPAN ENDS ON. The span is
# "the Architect text immediately before the modified SELECT section", so the
# honest search space is the end-anchors of the FINAL PAGE's pre-SELECT span
# (255 words -> 217 valid anchors). Anything wider is invalid: an earlier draft of
# this script swept the whole 55,682-word community walkthrough notebook and
# reported p = 1/55644. That number is meaningless -- the extractor never saw that
# text, and widening the domain after seeing a result inflates significance
# rather than measuring it. The domain is fixed by the method, not by the outcome.
#
# "Hit" = a substring of the output that the system dictionary accepts. Every
# length-3 and length-4 substring is tested, so the score cannot be inflated by
# choosing which words count.
w = preselect_words(norm(SOURCES["bookcipher_words_clean"].read_text(encoding="utf-8", errors="replace")))
target = CLAIMED_OUTPUT
lo, hi = min(colsums), max(colsums)
rows = [(e, "".join(w[e - c][0] for c in colsums).upper()) for e in range(hi, len(w))]
n = len(rows)
for k in (3, 4):
    cand = set()
    for _, s in rows:
        cand |= substrings(s, k)
    cand |= substrings(target, k)
    known = dictionary_words(cand)
    print(f"\ncontrol ({k}-letter substrings, hunspell en_US): {len(cand)} candidates, {len(known)} in dictionary")
    scored = [(e, s, sorted(substrings(s, k) & known)) for e, s in rows]
    dist = {}
    for _, _, h in scored:
        dist[len(h)] = dist.get(len(h), 0) + 1
    th = sorted(substrings(target, k) & known)
    ge = sum(v for key, v in dist.items() if key >= len(th))
    print(f"  final-page pre-SELECT span = {len(w)} words, {n} end-anchors")
    print(f"  hit-count dist {dict(sorted(dist.items()))}")
    print(f"  target {target} -> {th}")
    print(f"  p(>={len(th)} hits) = {ge}/{n} = {ge/n:.4f}   rank {ge}/{n}")
    for e, s, h in sorted(scored, key=lambda t: -len(t[2]))[:5]:
        print(f"    {len(h)} hits  end@{e}  {s}  {h}")
print("\nVerdict framing: a dbbib shuffle tests the wrong axis -- the extraction is")
print("deterministic, and it is the ANCHOR that carries the multiplicity.")
print("Also: 12 of 13 indices land inside one 28-word window, and index 27 is used twice,")
print("so this is NOT 13 independent draws from the monologue.")
print("And 'yb' is not a word: 2 of the 3 claimed correspondences (anti, core) are English;")
print("the Yellow/Blue and 84-cell-core links were assigned after seeing the output.")
