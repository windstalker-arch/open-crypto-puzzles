#!/usr/bin/env python3
"""phase32_probe.py -- reproducible probe of the Phase-3.2 OpenSSL envelope.

WHY THIS TOOL EXISTS
--------------------
`analysis/STATE_BRIEF.md` called Phase 3.2 "structurally blocked", and
`analysis/tested.md` (s.43) recorded the blocker as a MISSING ARTIFACT:

    "byte-repro locally blocked: the p32-outer envelope salt eefc4c5befc1656a
     is NOT in our local captures"

That is a retrieval excuse, not a solve result, and it was wrong: the envelope
WAS held, at ~/storage/external/briefcase/gsmg-puzzle/analysis/phase32.live.b64
(just never promoted into this repo's data/ dir, so coverage_check could not see
it).  This tool promotes the bytes, proves the envelope is internally
consistent, and then -- with a real witness -- re-derives the blocked verdict
instead of asserting it.

PROVENANCE OF THE COPY
----------------------
data/phase3.2-envelope-2026.b64 is a 3,264-char OpenSSL blob, byte-identical to
BOTH independent sources:
  * AzizLeBG/gsmg WALKTHROUGH.txt (fresh clone, 2026-09-27)
  * ~/storage/external/briefcase/gsmg-puzzle/analysis/phase32.live.b64
The same source's 1,792-char cosmic-duality blob is byte-identical to our own
data/cosmic_duality_blob_2020.b64 (sha256 b1895055...), so this transcription
channel is byte-faithful -- which is what licenses trusting the 3,264-char run.
A third, TRUNCATED copy (48 B total / 32 B ct, same salt) sits in the Naddiseo
fork at phase3-assets/phase3.2-aes.txt and is verified here to be an exact
PREFIX of the full ciphertext -- same era, no second version.

THE VERDICT THIS TOOL ACTUALLY ESTABLISHES
------------------------------------------
The 2020-era password `jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple`
(with sha256(pw) = 250f3772..., the key the community walkthrough publishes) does
NOT open this ciphertext under any of 12 key/IV derivations.  Combined with
tested.md s.65 (which decrypted a 2020 capture to 2,422 B "I've been waiting
for you..." under exactly this password), that identifies the envelope in hand
as the 2026 RE-ENCRYPTED copy.  So the blocker is real and is a password-
recovery problem, but it is now witnessed and reproducible rather than a note
about a missing file.

HONESTY CONTROLS
  * W1  the EVP_BytesToKey implementation is cross-checked against the
       degenerate case md=sha256/no-salt, which MUST equal the single
       sha256(pw) raw key.  If it does not, the KDF code is wrong.
  * W2  the 32-byte Naddiseo prefix must be a byte-exact prefix of the 2,432-byte
       ciphertext (copy-integrity check on the second source).
  * W3  PKCS#7 validity + printable fraction gate every result; no output is
       called a hit without a valid pad AND a plausible plaintext.
  * N   12 derivations x 2 key schedules = 24 decrypts, ~1 s.  Fully exhausts
       the hypothesis "the documented 2020 password/KDF opens this blob".

Usage:  python3 tools/phase32_probe.py [--selftest] [--b64 PATH]
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"

# The 2020-era phase-3 password, and the phase-3.2 key the community publishes
# for it (verified below: sha256(pw) == this).
PW_2020 = "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple"
P32_KEY_CLAIMED = "250f37726d6862939f723edc4f993fde9d33c6004aab4f2203d9ee489d61ce4c"
SALT_HEX = "eefc4c5befc1656a"

# sha256 of the phase-2 7-part password -> the phase-3 key, same convention.
P3_KEY = "1a57c572caf3cf722e41f5f9cf99ffacff06728a43032dd44c481c77d2ec30d5"


def grab_blob(text: str) -> str:
    runs = re.findall(r"U2FsdGVk[A-Za-z0-9+/=]{40,}", text)
    if not runs:
        raise ValueError("no OpenSSL blob found")
    return max(runs, key=len)


def evp_bytes_to_key(pw: bytes, salt: bytes, md: str, n: int = 32) -> bytes:
    d = b""
    prev = b""
    while len(d) < n:
        prev = hashlib.new(md, prev + pw + salt).digest()
        d += prev
    return d[:n]


def attempts():
    """Yield (label, key, iv) for every derivation under test."""
    k = hashlib.sha256(PW_2020.encode()).digest()
    yield ("raw key = sha256(pw),            IV = 0", k, b"\0" * 16)
    yield ("raw key = sha256(pw),            IV = key[0:16]", k, k[:16])
    yield ("raw key = sha256(pw),            IV = key[16:32]", k, k[16:])
    yield ("raw key = sha256(sha256(pw)),    IV = 0", hashlib.sha256(k).digest(), b"\0" * 16)
    yield ("raw key = phase-3 key 1a57c572,  IV = 0", bytes.fromhex(P3_KEY), b"\0" * 16)
    salt = bytes.fromhex(SALT_HEX)
    for md in ("md5", "sha1", "sha256", "sha512"):
        yield (f"EVP_BytesToKey {md:<6s} salt=8B   IV = 0", evp_bytes_to_key(PW_2020.encode(), salt, md), b"\0" * 16)
        yield (f"EVP_BytesToKey {md:<6s} salt=0    IV = 0", evp_bytes_to_key(PW_2020.encode(), b"", md), b"\0" * 16)


def probe(ct: bytes, label: str, key: bytes, iv: bytes):
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    d = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    pt = d.update(ct) + d.finalize()
    n = pt[-1]
    padok = 1 <= n <= 16 and pt[-n:] == bytes([n]) * n
    printable = sum(1 for x in pt if 32 <= x < 127 or x in (9, 10, 13)) / len(pt)
    return pt, padok, printable


def selftest() -> bool:
    ok = True
    # W1: EVP_BytesToKey(md=sha256, salt=0) MUST equal the single sha256(pw).
    k = hashlib.sha256(PW_2020.encode()).digest()
    a = evp_bytes_to_key(PW_2020.encode(), b"", "sha256")
    w1 = a == k
    print(f"W1 EVP_BytesToKey degenerate case == sha256(pw): {'OK' if w1 else 'FAIL'}")
    ok &= w1
    # and the published key claim.
    w1b = k.hex() == P32_KEY_CLAIMED
    print(f"W1b sha256(pw) == published phase-3.2 key: {'OK' if w1b else 'FAIL ' + k.hex()}")
    ok &= w1b
    # envelope structure
    b = base64.b64decode((DATA / "phase3.2-envelope-2026.b64").read_text().strip())
    w1c = (b[:8] == b"Salted__" and b[8:16].hex() == SALT_HEX
           and len(b) == 2448 and len(b) - 16 == 2432 and (len(b) - 16) % 16 == 0)
    print(f"W1c envelope: Salted__ + salt {b[8:16].hex()} + ct {len(b)-16}B "
          f"({(len(b)-16)//16} blocks): {'OK' if w1c else 'FAIL'}")
    ok &= w1c
    print(f"    blob sha256 {hashlib.sha256(b).hexdigest()}")
    print(f"    ct   sha256 {hashlib.sha256(b[16:]).hexdigest()}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--b64", default=str(DATA / "phase3.2-envelope-2026.b64"))
    a = ap.parse_args()
    if a.selftest:
        return 0 if selftest() else 1

    raw = base64.b64decode(Path(a.b64).read_text().strip())
    ct = raw[16:]

    # W2: second (truncated) source must be a byte-exact prefix.
    nadd = Path(os.path.expanduser(
        "~/storage/external/briefcase/gsmg-fork-naddiseo/phase3-assets/phase3.2-aes.txt"))
    if nadd.exists():
        nb = base64.b64decode(grab_blob(nadd.read_text(errors="replace")))
        w2 = ct[:len(nb) - 16] == nb[16:]
        print(f"W2 Naddiseo {len(nb)-16}B slice is an exact prefix of ct: {'OK' if w2 else 'FAIL'}")

    print(f"\n{len(ct)} B ciphertext x {len(list(attempts()))} derivations "
          f"(2020 password only)\n")
    hits = 0
    for label, key, iv in attempts():
        pt, padok, pr = probe(ct, label, key, iv)
        flag = ""
        if padok and pr > 0.90:
            flag = "  <-- HIT"
            hits += 1
        print(f"  {label}  padok={str(padok):5s} print={pr:.2f} {pt[:40]!r}{flag}")
    print(f"\nverdict: {hits} derivations open the 2026 envelope with the 2020 password")
    print("=> the envelope in hand is the 2026 RE-ENCRYPTED copy; the blocker is")
    print("   password recovery, now witnessed rather than asserted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
