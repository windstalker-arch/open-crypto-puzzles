#!/usr/bin/env python3
"""Certify the Phase-2/3/3.2 envelope convention and Phase-3.2's plaintext.

`tools/phase32_probe.py` reported Phase-3.2 blocked after 12-13 key/IV
derivations. The miss was the IV: OpenSSL's EVP_BytesToKey emits key||IV from
ONE digest stream, so for AES-256 the key is stream[0:32] and the IV is
stream[32:48]. That probe only ever tried IV = 0, key[0:16] or key[16:32].

  K = stream[0:32], IV = stream[32:48]

Under that convention the 2020 community passphrase opens the envelope in
hand, byte-exactly. This script re-derives all three stages from the
ciphertexts and prints the hashes so nothing is taken on trust.

Run:  python3 tools/p32_evp_verify.py
"""

from __future__ import annotations

import base64
import hashlib
import re
import sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent

# --- the objects under test -------------------------------------------------

ENVELOPE_2026 = FOLDER / "data" / "phase3.2-envelope-2026.b64"
FORK_PHASE3 = FOLDER / "data" / "community-fork-2026-09-27" / "phase3.txt"
FORK_PHASE32 = Path.home() / "storage/external/briefcase/gsmg-fork-naddiseo/phase3-assets/phase3.2.txt"

# The passphrase the community walkthrough publishes. Never modified.
PW_2020 = "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple"

# Known-good plaintexts, so the selftest can prove the detector fires.
EXPECT = {
    "phase3": "c4ad94559a44a927c1032cc0e024515f9510a0806a2d14458dbf4a360af9865f",
    "phase3.2": "b82afeb86f9e50848220f9b64b744b821400308aea273a1c949b9d2d0e408a34",
}


# --- the convention ---------------------------------------------------------

def evp_key_iv(pw: bytes, salt: bytes, md: str = "sha256") -> tuple[bytes, bytes]:
    """OpenSSL EVP_BytesToKey for AES-256-CBC: key and IV from one stream.

    D_1 = MD(pw || salt); D_i = MD(D_{i-1} || pw || salt).
    key = D_1 || D_2, iv = D_3[0:16] -- i.e. stream[0:32] and stream[32:48].
    """
    stream = b""
    prev = b""
    while len(stream) < 48:
        prev = hashlib.new(md, prev + pw + salt).digest()
        stream += prev
    return stream[:32], stream[32:48]


def unbase64(text: str) -> bytes:
    """Decode a `Salted__` blob, tolerating the `</textarea>` scrape tail."""
    s = re.sub(r"\s", "", text)
    for tail in ("/textarea", "</textarea"):
        if tail in s:
            s = s.split(tail)[0]
    # keep only the longest b64-legal prefix
    m = re.match(r"[A-Za-z0-9+/=]+", s)
    s = m.group(0)
    s = s[: len(s) - len(s) % 4] if len(s) % 4 else s
    return base64.b64decode(s)


def decrypt(blob: bytes, pw: bytes) -> bytes:
    """Decrypt a `Salted__` AES-256-CBC blob; raise if PKCS#7 padding is bad."""
    if blob[:8] != b"Salted__":
        raise ValueError("not an OpenSSL salted blob")
    salt, ct = blob[8:16], blob[16:]
    if len(ct) % 16:
        raise ValueError(f"ciphertext not block-aligned: {len(ct)} B")
    key, iv = evp_key_iv(pw, salt)
    d = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    pt = d.update(ct) + d.finalize()
    n = pt[-1]
    if not 1 <= n <= 16 or pt[-n:] != bytes([n]) * n:
        raise ValueError("bad PKCS#7 padding")
    return pt[:-n]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# --- checks -----------------------------------------------------------------

def _dec_raw(key: bytes, ct: bytes, iv: bytes) -> bytes:
    d = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    return d.update(ct) + d.finalize()


def selftest() -> bool:
    """Positive control, negative control, and a fact about the old detector.

    W1 proves this row is not a zero from looking at the wrong object. W2 is
    the negative control that pins the difference from the 13-derivation sweep
    it overturns: with the RIGHT key but a wrong IV the first block is garbage.
    W3 records why the old tool could not see it -- PKCS#7 padding validity
    depends on the key alone, never on the IV, so `padok` is blind to exactly
    the byte this row turns on.
    """
    ok = True
    blob = unbase64(ENVELOPE_2026.read_text())
    ct = blob[16:]
    hexpw = hashlib.sha256(PW_2020.encode()).hexdigest()

    # W1 -- the convention recovers the certified plaintext.
    try:
        pt = decrypt(blob, hexpw.encode())
        good = sha(pt) == EXPECT["phase3.2"]
    except ValueError:
        good = False
    print(f"W1 EVP key=stream[0:32] IV=stream[32:48] opens phase-3.2: {'OK' if good else 'FAIL'}")
    ok &= good

    # W2 -- right key, wrong IV: padding still validates, plaintext does not.
    # This is the control that makes W1 mean something.
    key, iv = evp_key_iv(hexpw.encode(), blob[8:16])
    bad = _dec_raw(key, ct, b"\0" * 16)
    n = bad[-1]
    padok = 1 <= n <= 16 and bad[-n:] == bytes([n]) * n
    # A wrong IV corrupts ONLY block 0; blocks 1.. stay readable. So the
    # discriminating test is block 0, not the whole-buffer printable ratio.
    good = padok and not bad[:16].startswith(b"I've been")
    print(
        f"W2 wrong IV still passes PKCS#7 (padok={padok}) but garbles block 0 "
        f"(first 16 = {bad[:16]!r}): {'OK' if good else 'FAIL'}"
    )
    ok &= good

    # W3 -- the old detector was blind here: padok is identical for the right
    # and wrong IV because only the last block's key-dependence matters.
    good_pt = _dec_raw(key, ct, iv)
    n2 = good_pt[-1]
    padok_good = 1 <= n2 <= 16 and good_pt[-n2:] == bytes([n2]) * n2
    print(
        f"W3 padok cannot distinguish IVs (right={padok_good}, wrong={padok}); "
        f"phase32_probe.py's criterion was IV-blind: {'OK' if padok_good == padok else 'FAIL'}"
    )
    ok &= padok_good == padok

    # W4 -- the passphrase really is the hex digest the community published,
    # and it is the hex STRING, not its bytes, that is the EVP password.
    print(
        f"W4 sha256(passphrase) == 250f3772...: "
        f"{'OK' if hexpw.startswith('250f3772') else 'FAIL'}"
    )
    ok &= hexpw.startswith("250f3772")
    return ok


def main() -> int:
    print("== selftest ==")
    if not selftest():
        print("SELFTEST FAIL - not searching")
        return 1
    print("SELFTEST PASS\n")

    print("== phase-3.2 (the envelope in hand) ==")
    blob = unbase64(ENVELOPE_2026.read_text())
    hexpw = hashlib.sha256(PW_2020.encode()).hexdigest()
    pt = decrypt(blob, hexpw.encode())
    print(f"envelope   {len(blob)} B  sha256 {sha(blob)}")
    print(f"salt       {blob[8:16].hex()}")
    print(f"ct         {len(blob) - 16} B")
    print(f"plaintext  {len(pt)} B  sha256 {sha(pt)}")
    print(f"expected   {EXPECT['phase3.2']}")
    print(f"MATCH      {sha(pt) == EXPECT['phase3.2']}")

    print("\n== independence vs the community fork ==")
    if FORK_PHASE32.exists():
        fork = FORK_PHASE32.read_bytes().strip()
        print(f"fork phase3.2.txt {len(fork)} B sha256 {sha(fork)}")
        print(f"BYTE-IDENTICAL to our decryption: {pt == fork}")
    if FORK_PHASE3.exists():
        fork3 = FORK_PHASE3.read_bytes()
        print(f"fork phase3.txt   {len(fork3)} B sha256 {sha(fork3)}")

    print("\n== phase-3 (same convention, re-derived from the 2020 blob) ==")
    p3 = Path.home() / "tmp/phase3_blob_2020.txt"
    if p3.exists():
        b3 = unbase64(p3.read_text())
        p3key = "1a57c572caf3cf722e41f5f9cf99ffacff06728a43032dd44c481c77d2ec30d5"
        pt3 = decrypt(b3, p3key.encode())
        print(f"plaintext  {len(pt3)} B  sha256 {sha(pt3)}")
        print(f"MATCH      {sha(pt3) == EXPECT['phase3']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())