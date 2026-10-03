#!/usr/bin/env python3
"""Lead 0: recover the dbbib_91 substitution by SEARCH rather than by sampling.

WHAT THIS IS. A lead generator, NOT a certified checker. Its output is a RANKING.
Nothing it prints is a solution; only an exact address match from `tools/oracle.py` is.

WHAT IS BEING SOLVED. `data/finalpage-digit-streams.json` carries two streams over the
9-symbol alphabet {a..i}: `dbbib_91` (91 chars, authoritative) and `faed_570`. Under the
certified convention (CV.CANON) letters become digits, and digits 1 and 4 are ESCAPE
introducers that consume the next digit. `dbbib_91` is 91 digits -> 66 tokens over
**17 distinct tokens**, so the unknown is a map from 17 known tokens to 17 of the 26
letters. That is a search, not a sample: `abracadabra_sweep.py` drew 150 keyed-alphabet
maps, which is a tiny and structurally-biased subset of this space.

CERTIFIED PARTS ARE IMPORTED, NOT REIMPLEMENTED. The stream, the CANON table and the
escape/arithmetic come from `certified_vic`, which is the module the data file itself
names. An earlier version of this file carried its own CANON copy and its own tokenizer;
that is how the superseded 69-char crop and the BUG-2 stale-reader class stay alive, so
it is gone.

THE SCORER IS A QUADGRAM MODEL, AND WHY THAT IS NOT A MATTER OF TASTE. Measured on this
exact problem shape (`--selftest` re-measures all of it, in-process, every run):

  * A quadgram model has no notion of a word boundary. The dbbib_91 plaintext CANNOT
    contain spaces -- the certified board is 26 letters plus 2 punct cells and the
    certified phase-3.2 decode is one unbroken letter run -- so word coverage, which
    assumes unstated boundaries, is the wrong objective for it. Measured: word cover
    of a 66-letter real English window is ~0.78, and so is the best of 80 hill-climbed
    noise strings. It cannot separate them.
  * The bigram mean is worse. Measured on the same draws, the BEST of 200 random
    66-char strings scored -8.51 while real prose scored -9.86: the bigram mean ranks
    noise above English, because a short random string concentrates on frequent letters
    and never emits an out-of-vocabulary bigram.
  * The quadgram model separates them, and the separation is checked where it matters.

THE GATE IS A CLIMB COMPARISON, NOT A MIN/MAX COMPARISON. Separating English from noise
by worst-case-vs-best-case says nothing about a HILL CLIMB, which returns the maximum
over a huge space. What decides whether this attack can work at all is:

    best score reached by climbing PURE NOISE   vs   the WORST real English window

both at 66 letters, both on letter-only text. Measured: 80 noise climbs (same 17-symbol,
66-token shape, no message) top out at -5.28, while the worst English window is -4.83 --
**0 of 80 noise climbs beat it**. So a candidate ranked first here cannot be a mirage
manufactured by the scorer, which is the failure `R-SCORERCORPUS` is about. The margin is
re-measured on every run and the search refuses to start without it.

THE PREMISE IS FALSIFIED, AND THE TOOL THEREFORE REFUSES TO SEARCH. The whole attack
assumes a MONOALPHATIC SUBSTITUTION over English: 17 token-symbols standing for 17
letters. A substitution cannot change the index of coincidence, so if the streams were
English under an unknown letter assignment their IC would sit at English's value. Measured
in-process by `--selftest`:

    dbbib_91 letters (N=91, 9 symbols)  IC = 0.1509   english 5-95%: [0.0545, 0.0760]
    faed_570 letters (N=570, 9 symbols) IC = 0.1181   english 5-95%: [0.0612, 0.0702]

Both are far ABOVE English -- dbbib_91's is double the top of its band, on a sample where
its most common letter 'b' takes 27.5% where English's most common letter 'e' takes 12.6%.
At N=570 the sampling noise is negligible, so faed_570's 0.1181 against a band topping out
at 0.0702 is not a fluctuation. It is also not repetition: the longest repeated substring
of either stream is 3 characters.

So `abracadabra_sweep.py`'s 150 keyed-alphabet samples were not a small subset of a
searchable space, and neither is this one. No amount of hill climbing or restarts repairs a
model whose premise is false, so `premise_ic()` gates the search and the tool exits 2.
Keeping the file is still worth it: the IC test is the cheap witness that closes the
branch, and it is re-measable rather than remembered.

INSTRUMENT ERRORS FOUND AND CORRECTED IN THIS FILE'S OWN FIRST VERSION, recorded because
they moved the conclusion and would have moved it again silently:
  1. `ProseModel` was called with two arguments against a three-argument signature, and
     `selftest()` and `main()` both read discrimination keys (`nonenglish_control`,
     `random_max`, `gap_over_random`) that no method returned. The file had never run.
  2. The hand-written tokenizer expectation `tokenise("011213") == ["0","11","12","13"]`
     was WRONG and the tokenizer was RIGHT: '2' is not an escape, so it cannot fuse.
     The certified decoder agrees with the tokenizer ("FLUT", 4 characters). The witness
     is now anchored to `CV.decode` instead of to a list typed by hand.
  3. The token count was reported as `len(set("".join(toks)))` = 9, which counts the
     CHARACTERS of the joined token string, not the tokens. The real figure is 17.
     A witness that reported a different quantity from the one it named is worse than
     no witness.
  4. A scorer-separates-English measurement run BEFORE this file's own scorer existed
     reported English at -9.25 against random at -8.32 -- English losing. The cause was
     the reference windows: they contained SPACES, and a quadgram model has no notion of a
     word boundary, so every window quadgram straddling a space scored as unseen. Stripped
     to letters, the certified phase-3.2 plaintext scores -4.18 and English beats random
     comfortably. A gate that was measuring the instrument, not the thing.

FITNESS. Primary objective is the mean log10 quadgram probability. Word cover and the
bigram mean are reported alongside, never optimised, for the reasons measured above.

Corpora are read from outside the repository by path: AGENTS.md forbids adding book text
or wordlists to it. `--quadgram` points at an English quadgram frequency table,
`--prose-dir` at plain-text prose (used only for the gate's English reference window).
Neither is vendored here.
"""
from __future__ import annotations

import argparse
import collections
import glob
import importlib.util
import math
import os
import pathlib
import random
import statistics
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent

# The certified module. Imported, never copied: see the docstring.
_spec = importlib.util.spec_from_file_location("certified_vic", HERE / "certified_vic.py")
CV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CV)

E1, E2 = 1, 4
LETTERS = "abcdefghijklmnopqrstuvwxyz"
ALPHA28 = "FUBCDORA.LETHINGKYMVPS.JQZXW"          # the certified board, from CV's docstring
WIN = 66                                           # dbbib_91 decodes to exactly 66 characters

# Known-good plaintexts the scorer must rank above noise. Two are this puzzle's own
# certified decode outputs, so a model that cannot rank them is plainly unfit.
CONTROL_ENGLISH = [
    ("incaseyoumanagetocrackthisprivatekeys", "certified phase-3.2 decode (excerpt)"),
    ("thequickbrownfoxjumpsoverthelazydog", "pangram"),
    ("itistruthuniversallyacknowledgedthatasinglemaninpossessionofagoodfortune", "prose opening"),
]


def tokenise(digits: str) -> list[str]:
    """Split a digit string into tokens using the certified escape rule.

    An escape digit (1 or 4) plus the following digit is ONE token; anything else is a
    single-digit token. Mirrors `CV.decode`'s consumption order, including its one
    asymmetry: `CV.decode` fuses only when the PAIR is in the code table, and every
    "1X"/"4X" pair is, so the rules agree everywhere except on a trailing lone escape
    digit, where `CV.decode` emits "?" and this returns that digit as its own token.
    `--selftest` checks both behaviours rather than asserting the rule from memory.
    """
    toks: list[str] = []
    i = 0
    while i < len(digits):
        d = digits[i]
        if int(d) in (E1, E2) and i + 1 < len(digits):
            toks.append(digits[i:i + 2])
            i += 2
        else:
            toks.append(d)
            i += 1
    return toks


def certified_tokens() -> tuple[str, list[str], list[str]]:
    """The authoritative stream as digits, as tokens, and the certified decode length."""
    digits = "".join(str(CV.CANON[c]) for c in CV.DBBIB)
    return digits, tokenise(digits), CV.decode(digits, CV.build_grid(ALPHA28, E1, E2), E1, E2)


def apply_map(toks: list[str], m: dict) -> str:
    return "".join(m.get(t, "?") for t in toks)


class QuadgramModel:
    """Mean log10 quadgram probability over an English frequency table.

    Unseen quadgrams take a floor of log10(0.01/total), the usual convention: it keeps a
    single unseen 4-gram from dominating without making it free.
    """

    def __init__(self, table_path: str):
        self.tab: dict[str, int] = {}
        self.total = 0
        for ln in pathlib.Path(table_path).read_text(errors="replace").splitlines():
            parts = ln.split()
            if len(parts) != 2:
                continue
            try:
                c = int(parts[1])
            except ValueError:
                continue
            q = parts[0].lower()
            if not q.isalpha():
                continue
            self.tab[q] = self.tab.get(q, 0) + c
            self.total += c
        if not self.tab:
            raise SystemExit(f"no quadgrams parsed from {table_path!r}")
        self.floor = math.log10(0.01 / self.total)
        self.n = len(self.tab)

    def score(self, s: str) -> float:
        s = s.lower()
        if len(s) < 4:
            return -99.0
        v = 0.0
        tab = self.tab
        for i in range(len(s) - 3):
            c = tab.get(s[i:i + 4], 0)
            v += math.log10(c / self.total) if c else self.floor
        return v / (len(s) - 3)


class BigramModel:
    """Character unigram+bigram model over real English prose. Reported, never primary."""

    def __init__(self, prose_dir: str, prose_glob: str):
        uni: collections.Counter = collections.Counter()
        bi: collections.Counter = collections.Counter()
        letters = 0
        files = sorted(glob.glob(os.path.join(prose_dir, prose_glob)))
        if not files:
            raise SystemExit(f"no prose matched {prose_glob!r} in {prose_dir!r}")
        for path in files:
            text = pathlib.Path(path).read_text(errors="replace")
            body = "".join(c.lower() for c in text if c.isalpha())
            for w in body.split():
                if len(w) < 2:
                    continue
                uni.update(w)
                bi.update(zip(w, w[1:]))
                letters += len(w)
        self.n_files = len(files)
        self.letters = letters
        total = sum(uni.values()) or 1
        self.uniprob = {c: math.log(max(uni.get(c, 0) / total, 1e-8)) for c in LETTERS}
        self.floor = math.log(1.0 / 676)
        self.biprob = {a + b: math.log((n + 1) / (uni.get(a, 0) + 26)) for (a, b), n in bi.items()}

    def score(self, s: str) -> float:
        s = s.lower()
        if not s:
            return -99.0
        tot = sum(self.uniprob.get(c, -18.0) for c in s)
        tot += sum(self.biprob.get(a + b, self.floor) for a, b in zip(s, s[1:]))
        return tot / len(s)


def wordcover(s: str, words: set) -> float:
    """Fraction of letters inside dictionary words of length >= 3, by greedy longest match.

    REPORTED ONLY. Measured unsound for this object: dbbib_91's plaintext has no spaces,
    and without word boundaries a greedy matcher fuses adjacent words and a noise string
    scores as well as English does. Kept because it is a genuinely independent signal and
    because the measurement that disqualified it should stay reproducible.
    """
    s = "".join(c for c in s.lower() if c.isalpha())
    if not s or not words:
        return 0.0
    toks, i = [], 0
    while i < len(s):
        for j in range(min(len(s), i + 20), i + 1, -1):
            if s[i:j] in words:
                toks.append(s[i:j])
                i = j
                break
        else:
            toks.append(s[i])
            i += 1
    return sum(len(t) for t in toks if len(t) >= 3) / len(s)


def load_words(path: str | None) -> set:
    words: set = set()
    if path and os.path.exists(path):
        for ln in pathlib.Path(path).read_text(errors="replace").splitlines():
            w = ln.strip().lower()
            if 1 <= len(w) <= 20:
                words.add(w)
    return words


def hill_climb(toks, distinct, score, rng, iters, swap_p=0.25):
    """Maximise `score` over assignments of distinct letters to the distinct tokens.

    Two moves: reassign one token to an unused letter, or SWAP the letters of two tokens.
    The swap matters because letters must stay distinct, so a pure reassign neighbourhood
    has to cross a plateau one unused letter at a time.
    """
    cur = dict(zip(distinct, rng.sample(LETTERS, len(distinct))))
    cur_f = score(apply_map(toks, cur))
    best, best_f, best_s = dict(cur), cur_f, apply_map(toks, cur)
    for _ in range(iters):
        sym = rng.choice(distinct)
        old = cur[sym]
        if rng.random() < swap_p:
            other = rng.choice([t for t in distinct if t != sym])
            new = cur[other]
            cur[sym], cur[other] = new, old
            f = score(apply_map(toks, cur))
            if f > cur_f:
                cur_f = f
                if f > best_f:
                    best_f, best_s, best = f, apply_map(toks, cur), dict(cur)
            else:
                cur[sym], cur[other] = old, new
            continue
        pool = [c for c in LETTERS if c not in cur.values()]
        if not pool:
            break
        cur[sym] = new = rng.choice(pool)
        f = score(apply_map(toks, cur))
        if f > cur_f:
            cur_f = f
            if f > best_f:
                best_f, best_s, best = f, apply_map(toks, cur), dict(cur)
        else:
            cur[sym] = old
    return best, best_f, best_s


def noise_floor(model, distinct, shape, rng, restarts=80, iters=1500):
    """Climb PURE NOISE of the same shape and return the best score reached.

    This is the gate's right-hand side. `shape` is the real token sequence of dbbib_91
    with its token IDENTITIES replaced by random draws from the same symbol set, so the
    climb faces the same search geometry while carrying no message at all.
    """
    best = -99.0
    for _ in range(restarts):
        _, f, _ = hill_climb([rng.choice(distinct) for _ in shape], distinct,
                             model.score, rng, iters)
        best = max(best, f)
    return best


def english_windows(corpus_dir: str, globpat: str, length: int, count: int, rng) -> list[str]:
    """Letter-only windows of the given length. No spaces: see the docstring."""
    blob = "".join(
        "".join(c.lower() for c in pathlib.Path(p).read_text(errors="replace") if c.isalpha())
        for p in sorted(glob.glob(os.path.join(corpus_dir, globpat))))
    if len(blob) < length * 4:
        raise SystemExit(f"corpus in {corpus_dir!r} too small for {count} windows of {length}")
    out = []
    for _ in range(count):
        i = rng.randrange(0, len(blob) - length)
        out.append(blob[i:i + length])
    return out


def premise(stream: str, corpus_dir: str, prose_glob: str, label: str, trials: int = 3000) -> dict:
    """Can this stream be a MONOALPHATIC substitution of English at all?

    A substitution cipher cannot change a symbol's frequency, so substituted English must
    look English in every frequency statistic. TWO are measured, because at N=91 they
    disagree and the disagreement is the answer rather than a nuisance:

      * IC (index of coincidence), the classic substitution invariant.
      * MAX SYMBOL SHARE, which needs no correction for the escape rule and is the
        statistic that transfers straight through the board's injective code->letter map.

    Each is compared against a SIMULATED null of English windows at the same length, never
    against a textbook constant, and the verdict is three-valued on purpose:

      refuted      - outside the null's 95% band: the stream cannot be substituted English
      consistent   - comfortably inside the band
      inconclusive - inside on one statistic, outside on the other, i.e. the sample is too
                     small to decide, and saying "refuted" would be claiming more than N allows

    The longest repeated substring is reported too, so that "too repetitive" and
    "substituted" cannot be confused as alternative explanations.
    """
    seq = stream if isinstance(stream, str) else list(stream)
    c = collections.Counter(seq)
    n = len(seq)
    ic_obs = sum(v * (v - 1) for v in c.values()) / (n * (n - 1))
    max_obs = max(c.values()) / n

    blob = "".join(
        "".join(ch.lower() for ch in pathlib.Path(p).read_text(errors="replace") if ch.isalpha())
        for p in sorted(glob.glob(os.path.join(corpus_dir, prose_glob))))
    ic_null, max_null = [], []
    for st in range(0, n * (trials + 2), n):
        w = blob[st:st + n]
        if len(w) < n:
            break
        cc = collections.Counter(w)
        ic_null.append(sum(v * (v - 1) for v in cc.values()) / (n * (n - 1)))
        max_null.append(max(cc.values()) / n)
    ic_null.sort()
    max_null.sort()

    def pct(dist, v):
        return sum(1 for x in dist if x <= v) / len(dist) * 100

    ic_pct, max_pct = pct(ic_null, ic_obs), pct(max_null, max_obs)
    lo, hi = 2.5, 97.5
    outside = [(ic_pct < lo or ic_pct > hi), (max_pct < lo or max_pct > hi)]
    if all(outside):
        verdict = "REFUTED"
    elif any(outside):
        verdict = "INCONCLUSIVE"
    else:
        verdict = "consistent"

    def longest_repeat(seq, minlen: int = 3) -> int:
        # Joined with a separator no token can contain, so a repeat must be
        # TOKEN-ALIGNED. Joining raw would invent repeats that straddle a boundary.
        s = "\x00".join(seq) if not isinstance(seq, str) else seq
        for L in range(minlen, len(s) + 1):
            if len({s[i:i + L] for i in range(len(s) - L + 1)}) < len(s) - L + 1:
                return L
        return minlen - 1

    return {"label": label, "n": n, "symbols": len(c), "verdict": verdict,
            "ic": ic_obs, "ic_pct": ic_pct,
            "ic_band": (ic_null[int(0.025 * len(ic_null))], ic_null[int(0.975 * len(ic_null))]),
            "max_share": max_obs, "max_pct": max_pct,
            "max_band": (max_null[int(0.025 * len(max_null))], max_null[int(0.975 * len(max_null))]),
            "top": ", ".join(f"{ch}:{v/n:.1%}" for ch, v in c.most_common(4)),
            "longest_repeat": longest_repeat(stream)}


def positive_control(model, corpus_dir: str, prose_glob: str, rng,
                     windows: int = 3, restarts: int = 8, iters: int = 2000) -> dict:
    """Can this optimiser recover a plaintext we ALREADY KNOW, at the target's shape?

    This is the instrument test, and it is the only one that settles the question. Every
    other gate here is a proxy: the noise floor asks whether junk climbs too high, the
    premise test asks whether the stream looks like English at all. Neither asks the
    question that actually matters, which is whether a high score MEANS the right
    decoding.

    So: take real English windows of the target's length whose distinct-letter count
    equals the target's, scramble each letter's identity, and hand the result to the very
    same hill_climb with the very same scoring. The answer is known, so the recovery rate
    is measurable. A rate near zero means the scorer cannot separate a correct solution
    from an incorrect one at this shape, and then a dbbib_91 hit is no more meaningful
    than a dbbib_91 miss.

    Deliberately seeded from a fixed rng so the number in tested.md is reproducible.
    """
    n_target, k_target = certified_tokens()[1], None
    n = len(n_target)
    k_target = len(set(n_target))

    blob = "".join(
        "".join(ch.lower() for ch in pathlib.Path(p).read_text(errors="replace") if ch.isalpha())
        for p in sorted(glob.glob(os.path.join(corpus_dir, prose_glob))))
    picked = []
    off = 0
    while off + n <= len(blob) and len(picked) < windows:
        w = blob[off:off + n]
        if len(set(w)) == k_target:
            picked.append(w)
        off += 5

    if not picked:
        return {"verdict": "SKIPPED", "why": f"no corpus window of {n} letters has "
                                             f"exactly {k_target} distinct letters",
                "rate": float("nan"), "k": k_target, "n": n, "tries": 0}

    tries = hits = 0
    beat = []
    for w in picked:
        toks = list(w)
        true_map = dict(zip(toks, w))
        distinct = sorted(set(toks))
        true_f = model.score(w)
        for _ in range(restarts):
            m, f, _s = hill_climb(toks, distinct, model.score, rng, iters)
            tries += 1
            hits += m == true_map
            beat.append(f - true_f)
    rate = hits / tries
    return {"verdict": "SOUND" if rate >= 0.25 else "INVALID", "rate": rate, "k": k_target,
            "n": n, "tries": tries, "mean_excess": statistics.mean(beat),
            "constraints": n - k_target + 1}


def selftest(qg, corpus_dir: str, prose_glob: str, rng) -> int:
    """Checks that can fail, in the order they would stop a run."""
    bad = 0

    # 1. the certified module, on the authoritative field
    if CV.DBBIB == CV.d["dbbib_91"] and len(CV.DBBIB) == 91:
        print(f"  [PASS] stream is d['dbbib_91'], {len(CV.DBBIB)} chars (not the 69-char crop)")
    else:
        print("  [FAIL] certified_vic is not on the 91-char field")
        return 1
    try:
        CV.selfcert()
        print("  [PASS] certified_vic.selfcert()")
    except Exception as exc:  # noqa: BLE001
        print(f"  [FAIL] certified_vic.selfcert(): {exc}")
        bad += 1

    # 2. TOKENIZER vs the certified decoder, not vs a hand-typed list.
    digits, toks, dec = certified_tokens()
    if len(toks) == len(dec):
        print(f"  [PASS] tokenizer agrees with CV.decode on dbbib_91: "
              f"{len(toks)} tokens == {len(dec)} characters")
    else:
        print(f"  [FAIL] tokenizer {len(toks)} tokens vs CV.decode {len(dec)} characters")
        bad += 1
    if "?" not in dec:
        print("  [PASS] every dbbib_91 token is a valid code in the certified table")
    else:
        print(f"  [FAIL] {dec.count('?')} invalid tokens in dbbib_91")
        bad += 1

    # 2b. the trailing lone escape, where the two rules DIFFER, asserted explicitly.
    if tokenise("01121") == ["0", "11", "2", "1"] and CV.decode("01121", CV.build_grid(ALPHA28, E1, E2), E1, E2) == "FLU?":
        print("  [PASS] trailing lone escape: tokenizer keeps it, CV.decode marks it '?'")
    else:
        print(f"  [FAIL] trailing lone escape: {tokenise('01121')} vs "
              f"{CV.decode('01121', CV.build_grid(ALPHA28, E1, E2), E1, E2)!r}")
        bad += 1

    # 3. TOKENS, not CHARACTERS of the joined token string. This distinction is the
    #    whole reason the previous version of this file printed 9 instead of 17.
    distinct = sorted(set(toks))
    if len(distinct) == 17 and len(set("".join(toks))) == 9:
        print(f"  [PASS] {len(toks)} tokens, {len(distinct)} distinct tokens "
              f"(the joined string has {len(set(''.join(toks)))} distinct CHARACTERS - "
              f"not the token count)")
    else:
        print(f"  [FAIL] distinct tokens = {len(distinct)} (expected 17)")
        bad += 1

    # 4. scorer calibration on known plaintexts of THIS puzzle
    for s, name in CONTROL_ENGLISH:
        v = qg.score(s)
        if -6.0 < v < -3.0:
            print(f"  [PASS] quadgram {v:+.4f}  {name}")
        else:
            print(f"  [FAIL] quadgram {v:+.4f} out of the English band for {name}")
            bad += 1

    # 5. THE PREMISE, tested before any search. Two statistics, and the tool is careful
    #    about which of them can carry a conclusion at which sample size.
    verdicts = []
    for label, toks_or_letters in (("dbbib_91", CV.DBBIB), ("faed_570", CV.FAED.rstrip("z"))):
        digits = "".join(str(CV.CANON[c]) for c in toks_or_letters)
        v = premise(tokenise(digits), corpus_dir, prose_glob, label)
        verdicts.append(v)
        print(f"  premise {v['label']} (token stream, the substitution-invariant one): "
              f"N={v['n']} {v['symbols']} symbols, longest repeat {v['longest_repeat']}")
        print(f"    IC          {v['ic']:.5f}  english 95% [{v['ic_band'][0]:.5f}, "
              f"{v['ic_band'][1]:.5f}]  at {v['ic_pct']:.1f}th pct")
        print(f"    max share   {v['max_share']:.3f}   english 95% [{v['max_band'][0]:.3f}, "
              f"{v['max_band'][1]:.3f}]  at {v['max_pct']:.1f}th pct")
        print(f"    top symbols {v['top']}")
        print(f"    VERDICT: {v['verdict']}")
    refuted = [v for v in verdicts if v["verdict"] == "REFUTED"]
    incon = [v for v in verdicts if v["verdict"] == "INCONCLUSIVE"]
    if refuted:
        print(f"  [FAIL] premise REFUTED for {', '.join(v['label'] for v in refuted)}: outside the "
              "English null on BOTH statistics. A substitution cannot change symbol frequency, so "
              "that stream is not substituted English and no search over it can succeed.")
    if incon:
        print(f"  [PASS-ONLY] premise INCONCLUSIVE for {', '.join(v['label'] for v in incon)}: "
              "the two statistics disagree, which at this N means undecided, NOT refuted. "
              "Recorded rather than rounded to a verdict.")
    if not refuted and not incon:
        print("  [PASS] premise survives on both statistics for both streams")

    # 6. THE INSTRUMENT. Positive control first, because it is the test that decides
    #    whether anything else in this file can be believed.
    pc = positive_control(qg, corpus_dir, prose_glob, rng)
    if pc["verdict"] == "SKIPPED":
        print(f"  [SKIP] positive control not runnable: {pc['why']}")
    else:
        print(f"  positive control: real English, {pc['n']} letters with {pc['k']} distinct "
              f"(same shape as dbbib_91), {pc['constraints']} quadgram constraints")
        print(f"    exact recoveries of a KNOWN map: {pc['rate']:.0%} over {pc['tries']} climbs "
              f"(mean excess over the true text {pc['mean_excess']:+.4f})")
        if pc["verdict"] == "SOUND":
            print("  [PASS] the optimiser recovers known plaintexts of this shape, so a hit "
                  "here would mean something")
        else:
            print(f"  [FAIL] the optimiser recovers NO known plaintext of this shape "
                  f"({pc['rate']:.0%} of {pc['tries']} climbs). The scorer therefore cannot "
                  "separate a correct decoding from an incorrect one here, so this search "
                  "returns no evidence in EITHER direction.")

    # 7. The old heuristic, kept as corroboration rather than as the gate.
    win = english_windows(corpus_dir, prose_glob, WIN, 200, rng)
    eng = sorted(qg.score(s) for s in win)
    nf = noise_floor(qg, sorted(set(certified_tokens()[1])), certified_tokens()[1], rng)
    margin = eng[0] - nf
    print(f"  corroborating noise floor: {qg.n:,} quadgrams, floor {qg.floor:+.4f}")
    print(f"    english {WIN}-letter windows : worst {eng[0]:+.4f}  median {statistics.median(eng):+.4f}")
    print(f"    best hill-climbed NOISE      : {nf:+.4f}   margin vs worst {margin:+.4f}")

    bad += len(refuted)
    if pc["verdict"] == "INVALID":
        bad += 1
    print("SELFTEST PASS" if bad == 0 else f"SELFTEST FAIL: {bad}")
    return 0 if bad == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quadgram", default=str(
        pathlib.Path.home() / "colossus/ngram_data/english/english_quadgrams.txt"),
        help="English quadgram frequency table, 'QUAD COUNT' per line. External by rule.")
    ap.add_argument("--prose-dir", default=str(pathlib.Path.home() / "briefcase/corpus/english"),
                    help="plain-text prose dir, used ONLY for the gate's English reference")
    ap.add_argument("--prose-glob", default="pg*.txt",
                    help="matched inside --prose-dir; must not match the quadgram table")
    ap.add_argument("--wordlist", default=str(
        pathlib.Path.home() / "briefcase/corpus/english/words_alpha.txt"),
        help="dictionary, for the REPORTED-ONLY word-cover figure")
    ap.add_argument("--restarts", type=int, default=400)
    ap.add_argument("--iters", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=20261003)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    t0 = time.time()
    qg = QuadgramModel(a.quadgram)
    print(f"quadgram model: {qg.n:,} entries, total {qg.total:,}, floor {qg.floor:+.4f} "
          f"({time.time()-t0:.1f}s)")
    words = load_words(a.wordlist)
    rng = random.Random(a.seed)

    if a.selftest:
        return selftest(qg, a.prose_dir, a.prose_glob, rng)

    # Gate unconditionally, not only under --selftest. The premise comes first: a search
    # over a refuted model is worse than no search, because it produces a confident
    # ranking of nothing.
    verdicts = [premise(tokenise("".join(str(CV.CANON[c]) for c in s)),
                        a.prose_dir, a.prose_glob, lbl)
                for lbl, s in (("dbbib_91", CV.DBBIB), ("faed_570", CV.FAED.rstrip("z")))]
    for v in verdicts:
        print(f"premise {v['label']}: {v['verdict']}  IC {v['ic']:.5f} "
              f"({v['ic_pct']:.1f}th pct)  max share {v['max_share']:.3f} "
              f"({v['max_pct']:.1f}th pct)  longest repeat {v['longest_repeat']}")
    refuted = [v for v in verdicts if v["verdict"] == "REFUTED"]
    incon = [v for v in verdicts if v["verdict"] == "INCONCLUSIVE"]
    # The gate is about the TARGET. A refuted sibling stream is a negative control on the
    # cipher family, not a veto over this search, so it is reported and then set aside.
    target = next(v for v in verdicts if v["label"] == "dbbib_91")
    if target["verdict"] == "REFUTED":
        print(f"REFUSING TO SEARCH: target {target['label']} is outside the English null on "
              f"both statistics (IC {target['ic']:.5f} vs 95% band topping at "
              f"{target['ic_band'][1]:.5f}; max symbol share {target['max_share']:.3f} vs "
              f"{target['max_band'][1]:.3f}; longest repeat {target['longest_repeat']}, so not "
              "repetition either). A monoalphabetic substitution cannot change symbol frequency, "
              "so this stream is not substituted English and no hill climb can recover it. "
              "See analysis/tested.md R-SUBSTPREMISE.", file=sys.stderr)
        return 2
    if refuted:
        print("NOTE: " + ", ".join(f"{v['label']} is REFUTED ({v['ic_pct']:.1f}th pct IC, "
                                   f"{v['max_pct']:.1f}th pct share)" for v in refuted)
              + ". That is not the search target, but if both streams come from one cipher it "
                "makes the family itself doubtful, and any hit here should be treated as a "
                "coincidence until proven otherwise.", file=sys.stderr)
    if incon:
        print("NOTE: premise UNDECIDED for target "
              + ", ".join(f"{v['label']} (IC {v['ic_pct']:.1f}th pct, share {v['max_pct']:.1f}th pct)"
                          for v in incon)
              + ". The two statistics disagree, which at this N means undecided, not refuted. "
                "A result from this search is a hit over an UNSUPPORTED model and cannot be "
                "reported as recovering a plaintext.")

    pc = positive_control(qg, a.prose_dir, a.prose_glob, rng)
    print(f"positive control: {pc['verdict']}  exact recoveries {pc['rate']:.0%} "
          f"of {pc['tries']} climbs at n={pc['n']}, k={pc['k']}")
    if pc["verdict"] == "INVALID":
        print(f"REFUSING TO SEARCH: the optimiser recovered NO known plaintext of dbbib_91's "
              f"shape ({pc['tries']} climbs, {pc['rate']:.0%}; {pc['constraints']} quadgram "
              f"constraints over {pc['k']} free symbols, mean excess over the true text "
              f"{pc['mean_excess']:+.4f}). When a scorer cannot separate a correct decoding from "
              "an incorrect one, neither a hit nor a miss is evidence about dbbib_91. "
              "See analysis/tested.md R-SUBST-INSTRUMENT.", file=sys.stderr)
        return 2

    digits, toks, dec = certified_tokens()
    distinct = sorted(set(toks))
    win = english_windows(a.prose_dir, a.prose_glob, WIN, 200, rng)
    eng = sorted(qg.score(s) for s in win)
    nf = noise_floor(qg, distinct, toks, rng)
    if eng[0] - nf <= 0:
        print(f"REFUSING TO SEARCH: best noise climb {nf:+.4f} is not below the worst "
              f"English window {eng[0]:+.4f} (R-SCORERCORPUS class).", file=sys.stderr)
        return 2
    print(f"gate ok: worst english {eng[0]:+.4f} > best noise {nf:+.4f} "
          f"(margin {eng[0]-nf:+.4f})")

    print(f"dbbib_91: {len(CV.DBBIB)} chars -> {len(toks)} tokens, {len(distinct)} distinct")
    print(f"certified board decode of this stream ({len(dec)} ch, WRONG alphabet, shape only): "
          f"{dec}")

    # N, D, t before the loop, per AGENTS.md.
    N = a.restarts * a.iters
    t1 = time.time()
    hill_climb(toks, distinct, qg.score, rng, 200)
    D = 200 / (time.time() - t1)
    est = N / D
    print(f"N={N:,} proposals  D={D:,.0f}/s  t={est:.1f}s  (t<2h: {est < 7200})")

    bg = None
    try:
        bg = BigramModel(a.prose_dir, a.prose_glob)
        print(f"bigram model (reported only): {bg.n_files} files, {bg.letters:,} letters")
    except SystemExit as exc:
        print(f"bigram model unavailable ({exc}); continuing with quadgram only")

    rng = random.Random(a.seed)
    seen: dict[str, tuple] = {}
    t2 = time.time()
    for i in range(a.restarts):
        m, f, s = hill_climb(toks, distinct, qg.score, rng, a.iters)
        if s not in seen or f > seen[s][1]:
            seen[s] = (m, f)
        if (i + 1) % 50 == 0:
            print(f"  ..{i+1}/{a.restarts} restarts, {len(seen)} distinct, "
                  f"{time.time()-t2:.0f}s", flush=True)
    ranked = sorted(seen.items(), key=lambda kv: -kv[1][1])

    print(f"\n=== top {a.top} decodes ({time.time()-t2:.0f}s, {len(ranked)} distinct) ===")
    for s, (m, f) in ranked[: a.top]:
        wc = wordcover(s, words)
        bgs = f"{bg.score(s):+.4f}" if bg else "n/a"
        print(f"  quad={f:+.4f}  wordcover={wc:.3f}  bigram={bgs}  {s}")
    print(f"\nreference: english worst {eng[0]:+.4f}, english median {statistics.median(eng):+.4f}, "
          f"best noise climb {nf:+.4f}")
    print("RANKING ONLY. No address was derived and no oracle was called. "
          "A candidate is a solution only on an exact match from tools/oracle.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
