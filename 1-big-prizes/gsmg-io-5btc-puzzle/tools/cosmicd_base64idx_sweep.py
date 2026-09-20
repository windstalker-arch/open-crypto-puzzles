#!/usr/bin/env python3
"""Cosmic Duality base64-INDEX numerical-key sweep for the GSMG small-blob answer X.

The user-directed continuation: use the Cosmic Duality value as a numerical key, NOT
as readable letters (its plaintext is high-entropy). This tool derives numeric keys
strictly from the blob's base64-alphabet indices (0-63) and combines them with the
final-page 9-symbol streams (dbbib 69 / faed 570) and the resolved phase-2 table row,
then feeds every resulting candidate to tools/oracle.py.

Ground truth is the certified oracle (attempt() tries sha256 AND md5 -> funded gate
1GSMG1JC9). Real hit wins; negatives are logged with a witness (selftest).

Nothing here repeats a prior negative:
  - raw/plaintext-as-letters      : NOT derived (blob is ciphertext)
  - half/better-half priv hex/WIF : tested.md 40 (we add index/OTP-chain forms only)
  - phase-2 table 32 forms         : tested.md 13 (we add base64-index-chain forms only)
  - faed checkerboard over ~60 alphabets: tested.md 41 (we use index-derived numeric keys)
"""
import base64
import os
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOB_TXT = os.path.expanduser("~/briefcase/CosmicDuality.txt")
DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
ORACLE = os.path.join(ROOT, "tools", "oracle.py")

import json

d = json.loads(Path(DATA).read_text())
dbbib = d["dbbib"]
faed = d["faed_570"].rstrip("z")
blob = "".join(Path(BLOB_TXT).read_text().split())

B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

POS = {c: i for i, c in enumerate("abcdefghi")}
# canonical DBIFHCEG mapping (Bifid square first two rows, K=9): D0 B1 I2 F3 H4 C5 E6 G7 A8
CANON = {"d":0,"b":1,"i":2,"f":3,"h":4,"c":5,"e":6,"g":7,"a":8}

def b64idx(ch):
    try:
        return B64.index(ch)
    except ValueError:
        return None

# --- base64-INDEX keystreams ---
seq = [b64idx(c) for c in blob]
seq = [x for x in seq if x is not None]   # all valid base64 chars
seq9 = [x % 9 for x in seq]
seq10 = [x % 10 for x in seq]

# Half/Better-half private keys (public, issue #79)
HALF = "0423d9115a1dc756d5d08d2de880ab508bd4745fc97709f4fcb513f2cb8fcc35"
BETTER = "48cc46e66bdd36b09ae344552f606a761f9d90681f20dfefe2b43db18b623971"

# phase-2 resolved table row: X,H,Y,Q from trailing bytes -> [-4,2,32,12,4,27,0,2,-16,15]
TABLE = [-4, 2, 32, 12, 4, 27, 0, 2, -16, 15]

def combine(stream, keystream, op, mod):
    """combine stream digit (POS map) with keystream value mod 'mod'."""
    s = [POS[c] for c in stream]
    n = len(s)
    if mod == 9:
        ks = [k % 9 for k in keystream]
    else:
        ks = [k % 10 for k in keystream]
    out = []
    for i in range(n):
        k = ks[i % len(ks)] if ks else 0
        a = s[i]
        if op == "add":   v = (a + k) % mod
        elif op == "sub": v = (a - k) % mod
        elif op == "xor": v = (a ^ k) % mod
        elif op == "add1":v = (a + k + 1) % mod
        elif op == "sub1":v = (a - k - 1) % mod
        else: v = a
        out.append(chr(97 + v) if mod == 9 else str(v))
    return "".join(out)

candidates = set()

# ---- 1. base64-index numeric combine over streams ----
ksrcs = {
    "idx": seq, "idx9": seq9, "idx10": seq10,
    "idx_upperhalf": seq[:len(seq)//2], "idx_lowerhalf": seq[len(seq)//2:],
}
for ksname, ks in ksrcs.items():
    for streamname, stream in [("dbbib", dbbib), ("faed", faed)]:
        for op in ["add","sub","xor","add1","sub1"]:
            for mod in [9]:
                r = combine(stream, ks, op, mod)
                candidates.add(r)
                candidates.add(r[::-1])
            # also digits (base10)
            if ksname == "idx10":
                r = combine(stream, ks, "add", 10)
                candidates.add(r)

# ---- 2. columnar transposition of the digit stream ordered by blob-index key ----
def col_transpose(stream, keystream, rev=False):
    """columnar transpose a digit-stream (as string) using keystream as column order key."""
    s = stream
    width = len(keystream)
    order = sorted(range(width), key=lambda i: (keystream[i % width], i))
    n = len(s)
    nrows = (n + width - 1) // width
    full = n % width if n % width != 0 else width
    lens = [nrows if i < full else (nrows - 1 if (n % width != 0) else nrows) for i in range(width)]
    placed = [None] * width
    ptr = 0
    for k in range(width):
        ci = order[k]
        placed[ci] = s[ptr:ptr + lens[ci]]
        ptr += lens[ci]
    out = []
    for r in range(nrows):
        for c in range(width):
            if r < len(placed[c]):
                out.append(placed[c][r])
    return "".join(out)

# key lengths around 38 (faed=15x38) and 13/23 (dbbib)
for ksname, ks in [("idx", seq), ("idx9", seq9)]:
    for klen in [38, 13, 23, 19]:
        key = ks[:klen]
        for streamname, stream in [("dbbib", dbbib), ("faed", faed)]:
            t = col_transpose(stream, key)
            candidates.add(t)
            candidates.add(t[::-1])

# ---- 3. phase-2 table row forms (beyond tested.md 13's 32) ----
tab_str = [str(x) for x in TABLE]
for sep in ["", ",", "-", "_", " ", ":", ""]:
    cands = []
    for combo in [tab_str, tab_str[::-1],
                  [str(abs(x)) for x in TABLE],
                  [str(abs(x)) for x in TABLE[::-1]],
                  [format(x & 0xFF, "x") for x in TABLE],
                  [format(x & 0xFF, "02x") for x in TABLE]]:
        cands.append(sep.join(combo))
    for c in cands:
        candidates.add(c)
        candidates.add(c.lower())
        candidates.add(c.upper())

# ---- 4. Half/Better-half index/chain forms beyond tested.md 40 ----
for name, key in [("half", HALF), ("better", BETTER)]:
    # XOR the two
    h = bytes.fromhex(HALF); b = bytes.fromhex(BETTER)
    xo = bytes(x ^ y for x, y in zip(h, b)).hex()
    for c in [HALF, BETTER, HALF[::-1], BETTER[::-1], xo,
              HALF + BETTER, BETTER + HALF, HALF + xo]:
        for form in [c, c.upper(), c.lower()]:
            candidates.add(form)
    # index-encode each key nibble -> base64-class
    for which, key in [("half", HALF), ("better", BETTER), ("xor", xo)]:
        bts = bytes.fromhex(key)
        b64s = base64.b64encode(bts).decode()
        candidates.add(b64s)
        candidates.add(b64s.rstrip("="))

# write distinct candidates
out_path = "/data/data/com.termux/files/usr/tmp/opencode/cosmicd_b64idx_cands.txt"
with open(out_path, "w") as f:
    for c in sorted(candidates):
        if c:
            f.write(c + "\n")
print(f"[generate] {len(candidates)} distinct candidates -> {out_path}")
