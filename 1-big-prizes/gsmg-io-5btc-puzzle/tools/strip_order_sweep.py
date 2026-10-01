#!/usr/bin/env python3
"""
R-ORDER (2026-09-27): candidate battery from the 8 theseedisplanted strips, in the
certified PAGE ORDER, against both gate addresses.

New this round (never established before):
  * the exact document order of the 8 <img> tags (from the 981-byte static page)
  * closed-vs-OPEN padlock states, proven from the shackle leg (see notes below)
  * fragment-joining ACROSS tiles is required, proven by dig_i + t -> DIGIT
  * the pixel text does NOT match the filename slug 1:1 (crypto_gic -> CRYPTO + BIG)
"""
import itertools
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# page order, certified from <body> of the 981-byte capture
SLUGS = [
    "black_banking - war",
    "blue_ca",
    "blue_dig_i",
    "blue_lock_lo",
    "red_crypto_gic",
    "red_n_you",
    "red_open_lock_n_ing",
    "red_t",
]
# machine transcription of the visible glyphs, same order
PIXELS = [
    "A" + "\u0001",   # big A + 26x6 micro-text (illegible at this size)
    "CA",
    "DIGIT",
    "bO",            # closed padlock glyph
    "CRYPTOBIG",
    "nYOU",
    "NING",          # OPEN padlock glyph
    "T",
]
FRAGMENTS = ["banking", "war", "ca", "dig", "i", "lock", "lo",
             "crypto", "gic", "n", "you", "open", "ing", "t"]

cands = set()


def add(*words):
    for sep in ("", " ", "_", "-", "."):
        for w in words:
            cands.add(sep.join(w))


# --- F1: slug concatenation, page order, separator-preserved and stripped
flat = "".join(s.replace(" ", "").replace("-", "").replace("_", "") for s in SLUGS)
for v in (flat, flat.upper(), flat.capitalize()):
    cands.add(v)
cands.add(" ".join(SLUGS))
cands.add("_".join(SLUGS))
cands.add("_".join(s.replace(" ", "_") for s in SLUGS))

# --- F2: pixel transcriptions in page order
px = "".join(PIXELS).replace("\u0001", "")
for v in (px, px.upper(), px.lower(), px.capitalize()):
    cands.add(v)

# --- F3: fragment-complete words (the DIGIT proof as template)
for w in ("digit", "cryptographic", "unlocking", "unlock", "locking",
          "online", "digital", "banking", "crypto", "big", "open", "close",
          "locked", "you", "cant", "cannot", "seed", "planted"):
    for v in (w, w.upper(), w.capitalize()):
        cands.add(v)
# crypto + micro + gic, micro unknown: enumerate the plausible fills
for micro in ("RAPH", "GRAPH", "RAPHIC", "ASE", "ASED", "AP", "RAP", "RAPHY"):
    cands.add("crypto" + micro + "gic")
    cands.add(("crypto" + micro + "gic").upper())

# --- F4: sentences assembled from the completed fragments
SENT = [
    "you cannot open the digital banking lock",
    "you cannot open the digital lock",
    "you cannot open the lock",
    "you can not unlock the banking war",
    "digital banking war",
    "digital online banking lock",
    "online banking",
    "big cryptographic",
    "a big cryptographic",
    "you cannot unlock the big cryptographic banking lock",
    "open the digital banking lock",
    "you cannot open the cryptographic lock",
    "the seed is planted",
    "good luck little bunny hunter",
    "follow the white rabbit",
    "locking and unlocking the digital banking war",
    "cannot unlock without the big cryptographic key",
]
for s in SENT:
    for v in (s, s.upper(), s.capitalize(), s.replace(" ", ""), s.replace(" ", "_"),
              s.replace(" ", "-"), s.replace(" ", "").upper()):
        cands.add(v)

# --- F5: the closed/open lock pair as a binary instruction
for s in ("closed", "open", "closed open", "open closed", "lock open",
          "open lock", "locklocked", "openopening"):
    for v in (s, s.upper(), s.capitalize(), s.replace(" ", ""), s.replace(" ", "_")):
        cands.add(v)

clean = sorted(c for c in cands
               if c and len(c) >= 6 and "\x00" not in c and " " not in c or c)
clean = sorted({c.strip() for c in cands if c and c.strip() and "\x00" not in c})
print("candidates: %d" % len(clean))
with open("/data/data/com.termux/files/usr/tmp/opencode/strip_cands.txt", "w") as fh:
    fh.write("\n".join(clean) + "\n")

if "--dry" in sys.argv:
    for c in clean:
        print("  %s" % c)
    sys.exit(0)

for tool in ("oracle.py", "oracle_dualite.py"):
    p = subprocess.run([sys.executable, os.path.join(HERE, tool), "--stdin"],
                       stdin=open("/data/data/com.termux/files/usr/tmp/opencode/strip_cands.txt"),
                       capture_output=True, text=True)
    real = [l for l in p.stdout.splitlines() if l.startswith("MATCH") and "NO MATCH" not in l]
    nom = [l for l in p.stdout.splitlines() if l.startswith("NO MATCH")]
    print("%-20s exit=%d  real MATCH=%d  NO MATCH=%d" % (tool, p.returncode, len(real), len(nom)))
    for l in real:
        print("   >>> %s" % l)
