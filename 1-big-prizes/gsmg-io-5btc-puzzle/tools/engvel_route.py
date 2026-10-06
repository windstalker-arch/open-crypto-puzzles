#!/usr/bin/env python3
"""engvel_route.py - dictionary-scored route-reading search over the certified
Bifid output channels, using the english-words lexicon as the acceptance set.

Targets: object_256 (256 ch, 23-letter alphabet) and odd_pre_reduction (285 ch,
25-letter alphabet) from data/salphaseion-streams.json.

Readings: for every divisor shape (w x h) of each length, render the grid in a
set of standard routes and greedy-segment the resulting string with the lexicon.
Controls: a plain English sentence (HINT = the hint-1 phrase) and n shuffled
permutations of the target itself, scored identically.

RS1 = route-reading English search; RS2 = does any live substring of any
channel already sit verbatim in the lexicon (existence probe).
Output: prints a summary and writes analysis/tmp/engvel_route_results.json
"""
import json, itertools, random, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "salphaseion-streams.json")
LEX = os.path.expanduser("~/briefcase/english-words/words_alpha.txt")
OUT = os.path.join(HERE, "..", "analysis", "tmp", "engvel_route_results.json")

HINT = "rosesarewhitebutoftenredyellowhasanumberandso doesbluegobacktothefirstpuzzlepiece".replace(" ", "")

def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]

def render(s, w):
    """Return list of route-read strings for a w-column grid of len(s)."""
    h = len(s) // w if w else 0
    assert w * h == len(s)
    g = [list(s[i * w:(i + 1) * w]) for i in range(h)]
    routes = []
    # row-major
    routes.append("".join(c for r in g for c in r))
    # row-major, rows reversed (boustrophedon)
    routes.append("".join((c if i % 2 == 0 else c) for i, r in enumerate(g) for c in (r if i % 2 == 0 else r[::-1])))
    # reverse of row-major
    routes.append(routes[0][::-1])
    # column-major
    routes.append("".join(g[i][j] for j in range(w) for i in range(h)))
    # reverse of column-major
    routes.append(routes[-1][::-1])
    # spiral CW from top-left, perimeter-in
    def spiral_cw():
        out = []
        t, b, l, r = 0, h - 1, 0, w - 1
        while t <= b and l <= r:
            for j in range(l, r + 1): out.append(g[t][j])
            t += 1
            for i in range(t, b + 1): out.append(g[i][r])
            r -= 1
            if t <= b:
                for j in range(r, l - 1, -1): out.append(g[b][j])
                b -= 1
            if l <= r:
                for i in range(b, t - 1, -1): out.append(g[i][l])
                l += 1
        return "".join(out)
    routes.append(spiral_cw())
    routes.append(spiral_cw()[::-1])
    # spiral CCW from top-left
    def spiral_ccw():
        out = []
        t, b, l, r = 0, h - 1, 0, w - 1
        while t <= b and l <= r:
            for i in range(t, b + 1): out.append(g[i][l])
            l += 1
            for j in range(l, r + 1): out.append(g[b][j])
            b -= 1
            if l <= r:
                for i in range(b, t - 1, -1): out.append(g[i][r])
                r -= 1
            if t <= b:
                for j in range(r, l - 1, -1): out.append(g[t][j])
                t += 1
        return "".join(out)
    routes.append(spiral_ccw())
    routes.append(spiral_ccw()[::-1])
    # dedupe
    seen = set(); out = []
    for r in routes:
        if r not in seen:
            seen.add(r); out.append(r)
    return out

class Scorer:
    def __init__(self, words):
        self.words = words
        self.maxlen = max((len(w) for w in words), default=0)

    def score(self, s):
        if not s:
            return 0.0, 0.0, 0, ""
        words = self.words
        maxlen = self.maxlen
        covered = 0
        n_words = 0
        best_contig = 0
        i = 0
        cur_run = 0
        while i < len(s):
            best = None
            hi = min(len(s), i + maxlen)
            for j in range(i + 3, hi + 1):
                if s[i:j].lower() in words:
                    best = s[i:j]
            if best is not None:
                covered += len(best)
                n_words += 1
                cur_run += len(best)
                i += len(best)
            else:
                if cur_run > best_contig:
                    best_contig = cur_run
                cur_run = 0
                i += 1
        if cur_run > best_contig:
            best_contig = cur_run
        return covered / len(s), best_contig, n_words, ""

def main():
    d = json.load(open(DATA))
    targets = {
        "object_256": d["object_256"],
        "odd_pre_reduction": d["odd_pre_reduction"],
    }
    lex = {w.lower() for w in open(LEX).read().split() if 3 <= len(w) <= 20}
    scorer = Scorer(lex)

    results = {"lexicon_size": len(lex), "targets": {}, "rs2": {}}
    print(f"lexicon: {len(lex)} words (3..20 alpha-only)")

    for name, s in targets.items():
        divs = divisors(len(s))
        per = []
        best_overall = None
        for w in divs:
            for rd in render(s, w):
                cov, contig, nw, _ = scorer.score(rd)
                row = {"w": w, "h": len(s) // w, "reading": cov, "best_contig": contig, "n_words": nw}
                per.append(row)
                if best_overall is None or cov > best_overall["reading"]:
                    best_overall = dict(row, reading_name=rd[:80])
        best_overall_routed = max(per, key=lambda r: r["reading"])
        results["targets"][name] = {
            "len": len(s),
            "n_readings": len(per),
            "best_coverage": best_overall_routed,
        }
        print(f"\n[{name}] len={len(s)} n_shapes={len(divs)} n_readings={len(per)}")
        print("  best greedy coverage:", best_overall_routed)
        print("  best contiguous span (ch):", max(r["best_contig"] for r in per))

    # RS2: substrings that are real words
    chans = {
        "even_stream": d["even_stream"],
        "odd_pre_reduction": d["odd_pre_reduction"],
        "object_256": d["object_256"],
        "dropped_29": d["dropped_29"],
        "plaintext_head": d["plaintext_head"],
    }
    found = {}
    for name, s in chans.items():
        hits = set()
        for L in range(3, 16):
            for i in range(0, len(s) - L + 1):
                sub = s[i:i + L]
                if sub.lower() in lex:
                    hits.add(sub)
        found[name] = sorted(hits, key=len, reverse=True)
        print(f"\nRS2 [{name}]: {len(hits)} verbatim lexicon substrings; top: {sorted(hits, key=len, reverse=True)[:5]}")

    results["rs2"] = found
    # Controls
    ref = scorer.score(HINT)
    rng = random.Random(20261006)
    ctrl = {}
    for tname, t in targets.items():
        covs = []
        for _ in range(50):
            s = list(t); rng.shuffle(s)
            covs.append(scorer.score("".join(s))[0])
        covs.sort()
        ctrl[tname] = {
            "median": covs[25], "mean": sum(covs) / len(covs),
            "p50_max": max(covs)
        }
    results["controls"] = {"english_hint": ref, "shuffled_targets": ctrl}
    print(f"\nControl: English hint coverage={ref[0]:.3f} best_contig={ref[1]}")
    for k, v in ctrl.items():
        print(f"Control shuffle [{k}]: median={v['median']:.3f} mean={v['mean']:.3f} max={v['p50_max']:.3f}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(results, open(OUT, "w"))
    print("\nwrote", OUT)

if __name__ == "__main__":
    main()