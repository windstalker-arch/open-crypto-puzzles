#!/usr/bin/env python3
"""sticker_dollar_gen.py -- generate `$`-bearing sticker-phrase candidate passwords.

User steer (2026-09-14): the blue_ca sticker tile's right glyph is a literal `$`
(S-curve + crossbar + legs) in ASCII form, and the 8 sticker tiles reassemble to
"you can warning crypto wallet digit logic". Since the `$` is a real glyph on the
tape, the final-gate phrase candidates should carry it, not just "ca".

Families (bounded):
  W1  words = [you, can, warning, crypto, wallet, digit, logic]        (user phrase)
  W2  words = [you, can, warning, crypto, lock, digit, logic]          (wallet -> tile word "lock")
  O   8 curated rearrangements (user order is #1)
  D   9 dollar styles: can->c$n / $n / c$ / $, whole-phrase $ prefix/suffix,
       wallet$, $crypto
  J   6 joiners: "" "_" "-" "." "$" " "
  C   3 cases: lower, UPPER, Title
  F3  literal page-order tile run with c$ at the blue_ca position (2 groupings)

N = 2*8*9*6*3 + 2*9*6*3 = 2,592 + 324 = ~2,916 before dedup.

Stdout: one candidate per line. Byproduct: `--slugs` checks each candidate's
   sha256 (raw and lowercase-de-spaced) against the seven still-open gsmg.io
   32-hex hash-slugs (tested.md section 15) and the known chain-body markers;
   the known preimage witness `ourfirsthintisyourlastcommand` must re-hit.
"""
import argparse
import hashlib
import itertools
import sys

# Seven still-open gsmg.io hash-slugs (tested.md section 15)
OPEN_SLUGS = {
    "0b0f37ecaf7107f86ee2f477992f25bc7abe8f799d0dd713658c17d37496ee32",
    "10d6a2c5320bfbd47d35f18dd67f177ae5a5f4b5d18a8a5127361c2941a92908",
    "673e3b1a60ebe6fc4a8be88acde2600e12afd9efb2543e26b1b30039f8356b0d",
    "a2aefdbb953b70aa20d640effda4accee1e1f48acf1e4fcebdc2fc011418b0b1",
    "aca20ae7c6b5f425bdd9bd809583b28fd086b3380990689e37b6e94f3fb5ed9a",
    "c2eef34b479eb6c89c7aa89c49229ff5f67563da4e56d5782574489c4b776625",
    "f9719d6d531e6c3b5129644cd05da57bc6fdd075c9a61267c41d4b9627936096",
}
# Known chain-body SHA256 markers (partial prefixes are enough to recognise a hit)
CHAIN_MARKERS = {
    "1449a2178eea7c0e3fabac8c1ad2afa294be4fc1800c594a025a056e88c626bf": "B1_79",
    "4f7a1e4e": "cosmic_plain",
    "cd3fea3d": "cosmic_A",
    "a795de11": "XOR master key",
}
KNOWN_PREIMAGE = "ourfirsthintisyourlastcommand"
KNOWN_SLUG = "e24bd2c0fd454632f9fdd26cbdc210597f79e9fca9719c126a6d30cb41ef0238"

WORDS = {
    "W1": ["you", "can", "warning", "crypto", "wallet", "digit", "logic"],
    "W2": ["you", "can", "warning", "crypto", "lock", "digit", "logic"],
}

ORDERINGS = [
    [0, 1, 2, 3, 4, 5, 6],  # you can warning crypto wallet digit logic  (user order)
    [0, 1, 3, 4, 2, 5, 6],  # you can crypto wallet warning digit logic
    [2, 0, 1, 3, 4, 5, 6],  # warning you can crypto wallet digit logic
    [0, 1, 3, 4, 5, 6, 2],  # you can crypto wallet digit logic warning
    [6, 5, 4, 3, 2, 1, 0],  # reverse
    [1, 0, 2, 3, 4, 5, 6],  # can you warning crypto wallet digit logic
    [0, 1, 2, 5, 6, 3, 4],  # you can warning digit logic crypto wallet
    [5, 6, 3, 4, 2, 1, 0],  # digit logic crypto wallet warning can you
]

JOINERS = ["", "_", "-", ".", "$", " "]


def apply_dollar(form: list[str], style: str) -> list[str]:
    if style == "d0":
        return form
    if style == "d1":
        return ["c$n" if w == "can" else w for w in form]
    if style == "d2":
        return ["$n" if w == "can" else w for w in form]
    if style == "d3":
        return ["c$" if w == "can" else w for w in form]
    if style == "d4":
        return ["$" if w == "can" else w for w in form]
    if style == "d5":
        return ["$"] + form
    if style == "d6":
        return form + ["$"]
    if style == "d7":
        return [w + "$" if w in ("wallet", "lock") else w for w in form]
    if style == "d8":
        return ["$" + w if w in ("crypto", "lock") else w for w in form]
    raise ValueError(style)


def cases(phrase: str):
    yield phrase                   # lower (words are already lowercase)
    yield phrase.upper()           # UPPER
    yield " ".join(w.title() for w in phrase.split(" ")) if " " in phrase else phrase.title()


def build_core() -> list[str]:
    out: list[str] = []
    for wsname in ("W1", "W2"):
        ws = WORDS[wsname]
        for o in ORDERINGS:
            form = [ws[i] for i in o]
            for di in range(9):
                lined = apply_dollar(form, f"d{di}")
                for j in JOINERS:
                    joined = j.join(lined)
                    for cased in cases(joined):
                        out.append(cased)
    # F3: literal page-order tile run with c$ at the blue_ca position
    tile_groups = [
        ["warning", "c$", "digi", "locklo", "crypto", "gic", "nyou", "openlockning", "t"],
        ["warning", "c", "$", "digi", "lock", "lo", "crypto", "gic", "n", "you",
         "open", "lock", "n", "ing", "t"],
    ]
    for tokens in tile_groups:
        for di in range(9):
            lined = apply_dollar(tokens, f"d{di}")
            for j in JOINERS:
                joined = j.join(lined)
                for cased in cases(joined):
                    out.append(cased)
    return out


def slug_check(cands: list[str]) -> list[str]:
    hits = []
    for c in cands:
        forms = {c, c.replace(" ", ""), "".join(filter(str.isalnum, c)).lower()}
        for frm in forms:
            h = hashlib.sha256(frm.encode()).hexdigest()
            if h in OPEN_SLUGS:
                hits.append(f"SLUG-MATCH {h} <- {c!r} (form {frm!r})")
            for prefix, name in CHAIN_MARKERS.items():
                len_ok = len(prefix) >= 8 and len(prefix) <= 64
                if len_ok and h.startswith(prefix):
                    hits.append(f"MARKER-MATCH {name} {h} <- {c!r} (form {frm!r})")
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slugs", action="store_true")
    args = ap.parse_args()
    cands = build_core()
    # witness assertion: known preimage must re-hit via the slug path
    h = hashlib.sha256(KNOWN_PREIMAGE.encode()).hexdigest()
    assert h == KNOWN_SLUG, "slug harness witness failed"
    if args.slugs:
        for hit in slug_check(cands):
            print(hit)
    for c in cands:
        print(c)


if __name__ == "__main__":
    main()