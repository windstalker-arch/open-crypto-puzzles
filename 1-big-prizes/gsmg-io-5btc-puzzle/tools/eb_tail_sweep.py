#!/usr/bin/env python3
"""Is `E_B[:2] = 59cc` DERIVED or QUOTED? Exhaustive 2^16 sweep of the chain-4 key tail.

CADEIA 4 uses a 32-byte AES-256-CBC key

    E_C(15) || E_S(15) || E_B[:2]

The first 30 bytes are now derived on-puzzle (`tools/rung2_b2.py` certifies E_S from the
p32 outer envelope). The last TWO bytes, `59cc`, are still quoted from the community and
`tools/chain_rebuild.py` says so explicitly: they occur in neither B1, B2 nor chain4.

Two bytes is 65,536 possibilities, and the target is PUBLISHED: the chain-4 plaintext
hash `e4269ed5fbb202a81e5e1aa6b5190fdd1ea126b2c8547ea7cdbdf45387ea135b` (PR #68). So
this is a self-certifying search -- no oracle call, no gate, no private-key operation.
Exactly one of two outcomes, and both are informative:

  * exactly one tail reproduces the published hash
        -> E_B[:2] is DERIVED. The last community-sourced byte-pair in the chain closes,
           and chain-4 becomes fully on-puzzle.
  * zero tails reproduce it
        -> 59cc is not the key tail that produces the published hash, so the community
           value is wrong or garbled and "1151B chain4" does not rest on it.

This is a shrink-N step in the AGENTS.md sense: the space is 2^16, not 2^256, and it is
fully determined by the published anchor.

N = 65,536 candidates. D measured at run time and printed. Not an oracle row: the
acceptance test is a published SHA256, so a hit is verifiable by anyone re-running this.
"""
import base64
import hashlib
import os
import sys
import time
from pathlib import Path

from Crypto.Cipher import AES

FOLDER = Path(__file__).resolve().parent.parent
DUALITE_TXT = os.path.expanduser("~/briefcase/CosmicDuality.txt")

# published anchors
XORKEY = bytes.fromhex("a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735")
MASK = bytes.fromhex("b657264f2f6e6921")
CHAIN4_SHA = "e4269ed5fbb202a81e5e1aa6b5190fdd1ea126b2c8547ea7cdbdf45387ea135b"
CC_SHA = "4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081"
# E_C = B1[64:79], E_S = B2[64:79]; both on disk, both certified
E_C = (FOLDER / "data" / "B1_79B.bin").read_bytes()[64:79]
E_S = (FOLDER / "data" / "B2_79B.bin").read_bytes()[64:79]
HEAD = E_C + E_S  # 30 of the 32 key bytes
QUOTED = bytes.fromhex("59cc")


def sha256b(b):
    return hashlib.sha256(b).hexdigest()


def evp(pw, salt, digest="md5"):
    H = hashlib.md5 if digest == "md5" else hashlib.sha256
    d, prev = b"", b""
    while len(d) < 48:
        prev = H(prev + pw + salt).digest()
        d += prev
    return d[:32], d[32:48]


def unpad(p):
    n = p[-1]
    return p[:-n] if p and 0 < n <= 16 and p[-n:] == bytes([n]) * n else None


# --- rebuild `mystery` (identical to tools/chain_rebuild.py CADEIA 3 + 4)
raw3 = base64.b64decode(Path(DUALITE_TXT).read_bytes().strip())
k, iv = evp(XORKEY, raw3[8:16])
cc = unpad(AES.new(k, AES.MODE_CBC, iv).decrypt(raw3[16:]))
assert cc is not None and sha256b(cc) == CC_SHA, "CADEIA 3 anchor failed"
mystery = bytes(a ^ b for a, b in zip(cc[158 : 158 + 1168], (MASK * 146)[:1168]))
SALT, CT = mystery[8:16], mystery[16:]
print(f"mystery: salt={SALT.hex()} ct={len(CT)}B")
print(f"key head: E_C||E_S = {HEAD.hex()} ({len(HEAD)}B derived on-puzzle)")
print(f"key tail: 2 bytes = 65,536 candidates; acceptance = published chain4 sha256")
print(f"           {CHAIN4_SHA}")

# --- witness FIRST: the quoted value must reproduce the anchor, or the whole
# --- premise is wrong and the sweep is meaningless. Check before spending 2^16.
def decrypt(tail):
    k, iv = evp(HEAD + tail, SALT)
    return unpad(AES.new(k, AES.MODE_CBC, iv).decrypt(CT))


w = decrypt(QUOTED)
assert w is not None and sha256b(w) == CHAIN4_SHA, "WITNESS FAILED: 59cc does not reproduce the anchor"
print(f"\n[witness] quoted tail 59cc reproduces the anchor: PASS  (chain4={len(w)}B)")

# --- the sweep
t0 = time.time()
hits, padded = [], 0
for i in range(1 << 16):
    tail = i.to_bytes(2, "big")
    pt = decrypt(tail)
    if pt is None:
        continue
    padded += 1
    if sha256b(pt) == CHAIN4_SHA:
        hits.append(tail)
dt = time.time() - t0
print(f"[sweep]   N=65,536  D={65536/dt:,.0f} cand/s  t={dt:.1f}s")
print(f"[sweep]   valid-PKCS7 candidates: {padded}  (expected ~{65536/256:.0f} at 1/256)")
print(f"[sweep]   HITS reproducing the published chain4 hash: {len(hits)}")
for h in hits:
    print(f"          tail={h.hex()}   (quoted was {QUOTED.hex()})")
print()
if len(hits) == 1:
    print(f"RESULT: E_B[:2] = {hits[0].hex()} is DERIVED -- unique in 2^16. Chain-4 is now")
    print("        fully on-puzzle; no community-sourced bytes remain in the key.")
elif len(hits) == 0:
    print("RESULT: NEGATIVE, and the negative is decisive -- no 2-byte tail reproduces the")
    print("        published hash, so 59cc is not what produced it. The '1151B chain4'")
    print("        claim does not rest on this key tail. (Worth re-checking the published")
    print("        hash before believing this, but it is stated in tools/chain_rebuild.py.)")
else:
    print(f"RESULT: {len(hits)} tails collide -- the anchor is under-determined at 2^16.")
sys.exit(0)
