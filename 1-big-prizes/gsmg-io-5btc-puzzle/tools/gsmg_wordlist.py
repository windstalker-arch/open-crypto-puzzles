#!/usr/bin/env python3
"""
gsmg_wordlist.py -- synthesize GSMG AES-gate passphrase (X) candidates from the
decoded vocabulary and emit them on stdout, one per line, for feeding to
    python3 tools/oracle.py --stdin

Gate: password = sha256(X).hexdigest() (and MD5 variant) -> AES-256-CBC-Decrypt
      the small blob -> 32-byte key. So X is an arbitrary passphrase. The oracle
      is the certified checker; this script only produces candidate X strings.

Vocabulary (all recovered/decoded research facts, NOT guesses):
  sentence words from the certified homophone decode (§101)
  the faed Bifid head: BTCSEED + key DEOEMCKEADHBSCHDKBDCSDKDVBXCPCOCH (§104)
  author identity STOMASO FENZI MICHAEL SPINELLI (§106-109)
  phase stage names / page slug "theseedisplanted" / SalPhaseIon / Cosmic Duality
  TCP algo/interface vocab (§111)

Rules: singletons, joined without separator, with separators (-, ., _, space),
with l33t/upper/lower/capitalize variants. Deterministic; no random. Emits to
stdout; size is bounded and printed to stderr so the caller can budget N.
"""

import itertools
import sys

BROADEN = True  # expand to ordered pairs/triples + seps + case + digit suffix

SENTENCE = ["the", "seed", "making", "vision", "experience", "lost", "what", "you", "see"]
KEYSTR = "DEOEMCKEADHBSCHDKBDCSDKDVBXCPCOCH"
BTCH = "BTCSEED"
AUTHOR_TOKENS = ["stommaso", "stomaso", "fenzi", "michael", "spinelli", "spinelli tommaso fenzi michael"]
STAGES = ["salphaseion", "cosmicduality", "theseedisplanted", "btcseed", "gsmg", "insitula"]
TCP = ["bbr", "cubic", "reno", "vegas", "htcp", "wlan", "rmnetdata", "wifi", "cellular", "fqcodel", "fq"]
NOTES = ["theseed", "btcseed", "makingvision", "visionexperience", "experience lost"]

SEPARATORS = ["", "-", ".", "_", " "]
CASE = ["", " lower", " upper", " cap"]  # placeholders; handled by a transform

def transforms(words):
    out = set()
    for w in words:
        out.add(w)
        out.add(w.lower())
        out.add(w.upper())
        out.add(w.capitalize())
    return out

def joins(parts):
    out = set()
    for sep in SEPARATORS:
        out.add(sep.join(parts))
    return out

def main():
    base = transforms(SENTENCE)
    base |= transforms(AUTHOR_TOKENS)
    base |= transforms(STAGES)
    base |= transforms(TCP)
    base |= {BTCH, BTCH.lower(), KEYSTR, KEYSTR.lower(), "the " + BTCH}

    emited = set(base)

    def add(items):
        for i in items:
            if i and i not in emited and len(i) <= 80:
                emited.add(i)

    # pairwise joins of sentence words, all separators, with the BTCSEED head and key
    for a, b in itertools.combinations(SENTENCE, 2):
        add(joins([a, b]))
    # every single sentence word appended/prepended to key and vice versa
    for w in SENTENCE:
        add({KEYSTR + s + w for s in ["", " ", "-", "."]})
        add({w + s + KEYSTR for s in ["", " ", "-", "."]})
        add({BTCH + s + w for s in ["", " ", "-"]})
        add({w + s + BTCH for s in ["", " ", "-"]})
    # author + sentence / author + key joins
    for au in AUTHOR_TOKENS:
        for w in SENTENCE:
            add({au + s + w for s in ["", " ", "-"]})
            add({w + s + au for s in ["", " ", "-"]})
        add(joins([au, KEYSTR]))
        add(joins([KEYSTR, au]))
    # tcp algo/iface joined with sentence
    for t in TCP:
        for w in SENTENCE:
            add({t + s + w for s in ["", "-", " "]})
            add({w + s + t for s in ["", "-", " "]})
    # key + author + sentence triple (small)
    for au in AUTHOR_TOKENS:
        for w in SENTENCE:
            add({KEYSTR + " " + au + " " + w, au + " " + KEYSTR + " " + w})
    # case/l33t variants of the whole-key candidates
    for w in list(emited):
        if w.isalpha():
            add({w.upper(), w.capitalize(), w.lower()})

    # broadened: ordered pairs and triples across a compact core token set,
    # every separator, both orders, case variants, and digit suffixes (0-9,
    # 99, 123, 2020, 420, 777). Sized to stay well within the budget.
    if BROADEN:
        core = list(base)  # the transforms of all top-level tokens
        core += [BTCH, BTCH.lower(), KEYSTR, KEYSTR.lower(), "theseed", "btcseed"]
        seps = ["", "-", ".", "_", " "]
        digsuf = ["", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "99", "123", "2020", "420", "777", "1", "2", "3"]

        def marg(parts, kad):
            cand = sep.join(parts) + digit
            if not kad:
                add({cand, cand.upper(), cand.capitalize()})

        for sep in seps:
            for digit in digsuf:
                for a in core:
                    # singletons + single digit/sep suffix forms
                    add({a + digit})
                    add({a + sep + digit})
                    for b in core:
                        if a == b:
                            continue
                        for parts in ((a, b), (b, a)):
                            cand = sep.join(parts) + digit
                            add({cand, cand.upper(), cand.capitalize(), cand.lower()})
                # triples over a small promising subset to bound size
        tri_core = ["the", "seed", "making", "vision", "lost", "what", "you", "see", "btcseed", "theseed", "experience"]
        for sep in seps[:3]:  # "", "-", "." only for triples to bound size
            for a in tri_core:
                for b in tri_core:
                    if a == b:
                        continue
                    for c in tri_core:
                        if c == a or c == b:
                            continue
                        add({sep.join((a, b, c))})

    for x in sorted(emited):
        sys.stdout.write(x + "\n")
    sys.stderr.write(f"gsmg_wordlist: emitted {len(emited)} candidates\n")

if __name__ == "__main__":
    main()