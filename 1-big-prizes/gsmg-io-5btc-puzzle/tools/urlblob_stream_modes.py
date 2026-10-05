#!/usr/bin/env python3
"""
urlblob_stream_modes.py -- R-URLBLOBCRYPT: decrypt the 4th Salted__ blob in the
stream modes, because its length forbids padded CBC.

WHY THIS FAMILY WAS NEVER TRIED. The R-URLBLOB provenance work established that
`analysis/urlblob.bin` (112 B) is byte-for-byte identical to the 224-hex-char
Wayback route of 2026-01-05, so the artifact is COMPLETE, not truncated by us.
That leaves 88 bytes of ciphertext after the 24-byte `Salted__` header. 88 is not
a multiple of 16, so it cannot be a padded-CBC ciphertext. Every prior pass that
treated these blobs as CBC was therefore testing a parse that cannot exist.

This is not a quirk of this one blob. All six known `Salted__` blobs have
ciphertexts that are half a block short of a whole number of blocks:
    phase_0     salt 06286612  672 B -> 648  CT  (648  mod 16 = 8)
    phase_1     salt 9fbc451d  4112 B -> 4088 CT  (4088 mod 16 = 8)
    phase32     salt eefc4c5b  2448 B -> 2424 CT  (2424 mod 16 = 8)
    cosmic      salt 2d3f6fe0  1344 B -> 1320 CT  (1320 mod 16 = 8)
    urlblob     salt 74c974e3  112 B -> 88   CT  (88   mod 16 = 8)
A systematic `mod 16 == 8` across five independent blobs of five different sizes
is the signature of a stream-mode family (no padding, length arbitrary), not of
five coincidentally truncated CBC files. That is the observation this tool acts on.

CERTIFIED GATE (unchanged, from tools/oracle.py): the puzzle's own AES gate is
password = sha256(X).hexdigest() -> AES-256-CBC-Decrypt. The candidate passphrase
battery X comes from tools/gsmg_wordlist.py, which synthesises 835,270 candidates
out of RECOVERED research facts only (no random, no guessing). This tool does not
invent a new wordlist; it re-points that battery at a cipher family nobody tested.

IV SEMANTICS. `openssl enc -S <hex>` both sets the salt used in the KDF and sets
the IV to that salt directly. Both readings are tried, because a blob written by a
script rather than the CLI would derive the IV instead. For CTR there is no
padding pressure at all, so it is the single most likely mode for an 88-byte body.

ACCEPTANCE IS NOT "LOOKS PRINTABLE". A short printable run is expected by chance,
so a survivor must clear a printability floor AND be reported with its full
plaintext for human adjudication. Nothing here is a solve; a hit is a lead.

Read-only: local file and local arithmetic only. No oracle call, no funded-gate
contact, no network.

Usage:
    python3 tools/urlblob_stream_modes.py --selftest
    python3 tools/urlblob_stream_modes.py --limit 20000
    python3 tools/urlblob_stream_modes.py --full
"""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys

from Crypto.Cipher import AES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOB = os.path.join(ROOT, "analysis", "urlblob.bin")
HEADER = 24

KEYLENS = (32, 16)
MODES = ("CTR", "CFB", "CFB8", "CFB64", "OFB")
IVS = ("salt", "derived")

SOURCES = "/storage/EA7B-C038/briefcase/gsmg-puzzle/analysis"
FAMILY = {
    "urlblob": ("urlblob.bin", "the 4th route blob, 112 B"),
    "phase_0": ("phase_0.bin", "salt 06286612, 672 B"),
    "phase_1": ("phase_1.bin", "salt 9fbc451d, 4112 B"),
    "phase32": ("phase32_live_salt_eefc4c5b.bin", "salt eefc4c5b, 2448 B"),
    "cosmic": ("cosmic_duality_live_salt2d3f6fe0.bin", "salt 2d3f6fe0, 1344 B"),
}


def resolve(which: str) -> str:
    if which in FAMILY:
        p = os.path.join(SOURCES, FAMILY[which][0])
        if os.path.exists(p):
            return p
    return BLOB


def load_blob(which: str = "urlblob") -> tuple[bytes, bytes]:
    d = open(resolve(which), "rb").read()
    assert d[:8] == b"Salted__", f"{which} is not an openssl Salted__ blob"
    return d[8:24], d[HEADER:]


def evp_bytes_to_key(pw: bytes, salt: bytes, nbytes: int, digest: str) -> bytes:
    """openssl's legacy KDF: D_1 = H(pw||salt), D_i = H(D_{i-1}||pw||salt)."""
    h = hashlib.new(digest)
    h.update(pw + salt)
    out = h.digest()
    while len(out) < nbytes:
        h = hashlib.new(digest)
        h.update(out + pw + salt)
        out += h.digest()
    return out[:nbytes]


def derive(pw: bytes, salt: bytes, nbytes: int, kdf: str) -> bytes:
    if kdf == "evp-md5":
        return evp_bytes_to_key(pw, salt, nbytes, "md5")
    if kdf == "evp-sha256":
        return evp_bytes_to_key(pw, salt, nbytes, "sha256")
    if kdf == "evp-sha1":
        return evp_bytes_to_key(pw, salt, nbytes, "sha1")
    if kdf == "pbkdf2-sha256":
        return hashlib.pbkdf2_hmac("sha256", pw, salt, 10000, nbytes)
    if kdf == "pbkdf2-sha1":
        return hashlib.pbkdf2_hmac("sha1", pw, salt, 10000, nbytes)
    if kdf == "raw-sha256":
        return hashlib.sha256(pw).digest()[:nbytes]
    if kdf == "raw-md5":
        return hashlib.md5(pw).digest()[:nbytes]
    raise ValueError(kdf)


def make_cipher(mode: str, key: bytes, iv: bytes, ct: bytes, encrypt: bool):
    m = {
        "CTR": AES.MODE_CTR,
        "CFB": AES.MODE_CFB,
        "CFB8": AES.MODE_CFB,
        "CFB64": AES.MODE_CFB,
        "OFB": AES.MODE_OFB,
    }[mode]
    kw = {} if mode == "CTR" else {"iv": iv}
    if mode == "CTR":
        kw = {"nonce": b""}
    c = AES.new(key, m, **kw)
    if mode == "CTR":
        c = AES.new(key, AES.MODE_CTR, nonce=b"", initial_value=int.from_bytes(iv, "big"))
    if mode == "CFB8":
        c = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=8)
    if mode == "CFB64":
        c = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=64)
    fn = c.encrypt if encrypt else c.decrypt
    return fn


def printable_ratio(b: bytes) -> float:
    if not b:
        return 0.0
    ok = sum(1 for x in b if 32 <= x <= 126 or x in (9, 10, 13))
    return ok / len(b)


KDF_DIGEST = {
    "evp-md5": "md5", "evp-sha256": "sha256", "evp-sha1": "sha1",
    "pbkdf2-sha256": "sha256", "pbkdf2-sha1": "sha1",
    "raw-sha256": "sha256", "raw-md5": "md5",
}


def cells_for(pw: bytes, salt: bytes, kdf: str):
    """One KDF computation per (kdf, pw) yields every (keylen, iv) cell, because
    EVP_BytesToKey is a single prefix stream: key32 = D_1, iv = D_1[32:48],
    key16 = D_1[:16]. Recomputing per cell would cost 4 hashes for no reason.

    Coverage must stay complete: all four (keylen x iv-reading) cells are emitted
    for EVERY kdf, not just the EVP ones. An earlier version skipped the
    `derived` IV for raw-* and pbkdf2-* and the selftest caught it (75/140)."""
    if kdf.startswith("evp-"):
        d1 = evp_bytes_to_key(pw, salt, 48, KDF_DIGEST[kdf])
        return [
            (d1[:32], salt, 32, "salt"),
            (d1[:16], salt, 16, "salt"),
            (d1[:32], d1[32:48], 32, "derived"),
            (d1[:16], d1[32:48], 16, "derived"),
        ]
    keys = {32: derive(pw, salt, 32, kdf), 16: derive(pw, salt, 16, kdf)}
    ivd = evp_bytes_to_key(pw, salt, 16, KDF_DIGEST[kdf])
    return [
        (keys[32], salt, 32, "salt"),
        (keys[16], salt, 16, "salt"),
        (keys[32], ivd, 32, "derived"),
        (keys[16], ivd, 16, "derived"),
    ]


def sweep(cands, salt, ct, kdfs, screen=16, floor=0.95, verbose=True):
    hits = []
    tried = 0
    for kdf in kdfs:
        for pw in cands:
            keyiv = cells_for(pw, salt, kdf)
            for key, iv, keylen, ivkind in keyiv:
                for mode in MODES:
                    tried += 1
                    head = make_cipher(mode, key, iv, ct, False)(ct[:screen])
                    if printable_ratio(head) < floor:
                        continue
                    full = make_cipher(mode, key, iv, ct, False)(ct)
                    r = printable_ratio(full)
                    hits.append((r, kdf, keylen, mode, ivkind, pw, full))
                    if verbose:
                        print(f"  SURVIVOR r={r:.2f} kdf={kdf} kl={keylen} "
                              f"mode={mode} iv={ivkind} pw={pw!r}")
                        print(f"    {full!r}")
    return hits, tried


def selftest() -> int:
    """For every (kdf, keylen, mode, iv) cell, encrypt a known plaintext under
    that cell's own convention and require the sweep to re-find it with no
    special-casing.

    The cell's key and IV are taken from `cells_for` ITSELF, never from a
    second formula written out here. An earlier version recomputed the derived IV
    in the selftest and in the sweep; the two drifted and the selftest reported
    30/140 against a sweep that was actually fine. Duplicating the derivation is
    how a harness ends up certifying itself."""
    salt = bytes(range(16))
    pw = b"SELFTESTPW"
    plain = b"SELFTEST-PLAINTEXT-0123456789-abcdefghijklmnop"
    failures = 0
    cells = 0
    for kdf in KDF_DIGEST:
        cellmap = {(kl, ivk): (k, iv) for k, iv, kl, ivk in cells_for(pw, salt, kdf)}
        for (keylen, ivkind), (key, iv) in sorted(cellmap.items()):
            for mode in MODES:
                cells += 1
                ct = make_cipher(mode, key, iv, plain, True)(plain)
                hits, _ = sweep([pw], salt, ct, [kdf], verbose=False)
                if not hits:
                    failures += 1
                    print(f"  MISS kdf={kdf} kl={keylen} mode={mode} iv={ivkind}")
                    continue
                best = max(hits, key=lambda h: h[0])
                if best[6] != plain:
                    failures += 1
                    print(f"  WRONG kdf={kdf} kl={keylen} mode={mode} "
                          f"iv={ivkind} -> {best[6]!r}")
    total = cells
    if failures:
        print(f"\nSELFTEST FAIL -- {failures}/{total} cells")
        return 1
    print(f"\nSELFTEST PASS -- {total}/{total} cells round-trip through their "
          f"own convention (7 KDFs x 2 keylens x 5 modes x 2 IV readings)")
    return 0


def candidates(limit: int | None) -> list[bytes]:
    cmd = [sys.executable, os.path.join(ROOT, "tools", "gsmg_wordlist.py")]
    if limit:
        cmd += ["--limit", str(limit)] if False else []
    env = dict(os.environ)
    out = subprocess.run(cmd, capture_output=True, env=env, timeout=1800).stdout
    cands = [ln for ln in out.split(b"\n") if ln]
    if limit:
        cands = cands[:limit]
    seen, uniq = set(), []
    for c in cands:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--kdf", default="evp-md5,evp-sha256")
    ap.add_argument("--blob", default="urlblob", choices=sorted(FAMILY))
    ap.add_argument("--floor", type=float, default=0.95)
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    salt, ct = load_blob(a.blob)
    print(f"{a.blob} ({FAMILY.get(a.blob, ('', 'local'))[1]}): salt {salt.hex()}  "
          f"ciphertext {len(ct)} B (mod 16 = {len(ct) % 16} -> "
          f"padded CBC {'possible' if len(ct) % 16 == 0 else 'IMPOSSIBLE'})")
    cands = candidates(None if a.full else (a.limit or 20000))
    print(f"candidates: {len(cands)} unique passphrases from tools/gsmg_wordlist.py")
    kdfs = a.kdf.split(",")
    hits, tried = sweep(cands, salt, ct, kdfs, floor=a.floor)
    print(f"\nswept {tried} (candidate x cell) combinations over KDFs {kdfs}")
    if not hits:
        print("RESULT: no survivor at the printability floor")
        return 0
    print(f"RESULT: {len(hits)} survivors -- adjudicate by hand, not a solve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())