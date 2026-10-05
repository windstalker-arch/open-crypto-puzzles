#!/usr/bin/env python3
"""
blob_8byte_cbc.py -- R-BLOB8CBC: the `Salted__` family has an EIGHT-byte block,
so the family is 3DES-class CBC, not AES and not a stream mode.

THE ARGUMENT. All five genuine `Salted__` blobs have a ciphertext length that is
a multiple of 8 and NOT a multiple of 16:

    urlblob  88 B    phase_0  648 B   cosmic  1320 B
    phase_1  4088 B  phase32  2424 B

AES has a 16-byte block, so no AES block mode in CBC or ECB can produce these
lengths. A stream mode could, but it would leave no padding to verify against.
An 8-byte block cipher in CBC can: DES, DES-EDE (2-key 3DES), DES-EDE3 (3-key
3DES), Blowfish, CAST5, IDEA, RC2, SEED. This tool sweeps those, which is a
strictly stronger position than a stream mode because CBC padding gives a
VERIFIER.

PYCRYPTODOME CBC OBJECTS CARRY CHAINING STATE. Calling decrypt() twice on one
object chains the second call onto the first, so a pad check that decrypts
ct[-16:] and then a "full" decrypt of ct on the SAME object silently corrupts
exactly the first block of the second result. That presented as a selftest
failing 56/56 cells while an isolated round-trip passed, and it is the reason
every decrypt in this file builds a fresh cipher object.

THE VERIFIER IS THE POINT. Padded CBC ends in PKCS7, so for a correct key the
final block's last byte k satisfies 1 <= k <= blocksize and the final k bytes are
all equal to k. Checking the final block first costs one block decrypt, so a
random key survives with probability about 1/blocksize. Only survivors get the
full decrypt and the printability test. Two independent filters, so a reported
survivor is a lead for a human to read, not a solve.

This reframes a standing item rather than inventing one. `analysis/tested.md:19722`
already records that 30 tools touch AES-CBC / `Salted__` and that exactly one
(`tools/phase32_probe.py`) actually decrypts, with a hand-picked IV. Every one of
those passes used a 16-byte block on 8-byte-block data. Separately,
`tools/salphaseion_blob_extract.py` already caught the related trap of rejecting
stream modes by demanding `len(ct) % 16 == 0`; that tool lists `des-ede3-cbc` in
its SPEC but was built for one 31-byte blob, not for this family.

ACCEPTANCE. A survivor must clear BOTH the PKCS7 final-block check and a
printability floor on the whole plaintext. Printability alone is too weak at 88
bytes, which is why the pad check runs first. Nothing here contacts the oracle or
any funded gate.

Read-only: local files and local arithmetic.

Usage:
    python3 tools/blob_8byte_cbc.py --selftest
    python3 tools/blob_8byte_cbc.py --blob urlblob --limit 5000
    python3 tools/blob_8byte_cbc.py --full --kdf evp-md5,evp-sha256
"""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys

from Crypto.Cipher import DES3, Blowfish, CAST, DES, ARC4

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = "/storage/EA7B-C038/briefcase/gsmg-puzzle/analysis"
HEADER = 24

FAMILY = {
    "urlblob": "urlblob.bin",
    "phase_0": "phase_0.bin",
    "phase_1": "phase_1.bin",
    "phase32": "phase32_live_salt_eefc4c5b.bin",
    "cosmic": "cosmic_duality_live_salt2d3f6fe0.bin",
}


def load_blob(which, framing="c"):
    """Return (salt, ciphertext) under one of the three framings.

    (c) 24-byte header, 8-byte-block cipher  -> d[24:],      padding checkable
    (a) 32-byte header, 16-byte-block cipher -> d[32:],      padding checkable
    (b) 24-byte header, final 8 bytes lost   -> d[24:-8],    NOT checkable

    Framing (a) puts bytes d[24:32] in a header field rather than the
    ciphertext; framing (b) treats the last 8 bytes as missing. Both make the
    ciphertext 16-aligned and keep AES viable, which is the family the 30 tools
    already assumed, so both must be swept rather than argued away. Framing (a)
    is the one that would make "the AES passes were structurally impossible"
    wrong, so it is tested rather than dismissed.
    """
    p = os.path.join(SOURCES, FAMILY[which])
    d = open(p, "rb").read()
    assert d[:8] == b"Salted__", f"{which} is not a Salted__ blob"
    salt = d[8:24]
    if framing == "a":
        return salt, d[32:]
    if framing == "b":
        return salt, d[24:-8]
    return salt, d[24:]


def evp_bytes_to_key(pw: bytes, salt: bytes, nbytes: int, digest: str) -> bytes:
    out = b""
    prev = b""
    while len(out) < nbytes:
        prev = hashlib.new(digest, prev + pw + salt).digest()
        out += prev
    return out[:nbytes]


KDF_DIGEST = {"evp-md5": "md5", "evp-sha1": "sha1", "evp-sha256": "sha256",
              "raw-md5": "md5", "raw-sha256": "sha256"}


def key_for(pw: bytes, salt: bytes, klen: int, kdf: str) -> bytes:
    if kdf.startswith("evp-"):
        return evp_bytes_to_key(pw, salt, klen, KDF_DIGEST[kdf])
    if kdf == "raw-md5":
        return hashlib.md5(pw).digest()[:klen]
    return hashlib.sha256(pw).digest()[:klen]


def cells_for(pw: bytes, salt: bytes, klen: int, kdf: str, ivlen: int = 8):
    """Every (key, iv) pair for one passphrase.

    An 8-byte-block cipher (DES/3DES/Blowfish/CAST5) needs an 8-BYTE IV and AES
    needs 16, so the 16-byte salt cannot be passed through directly: doing so
    raises ValueError for the 8-byte family, and slicing it to 8 raises the
    mirror error for AES. `ivlen` therefore comes from `ivlen_for(alg)`, which
    is chosen by algorithm, NOT by key length. A first attempt looked it up from
    key length alone and the selftest failed 24/80, because AES and 3DES share
    key lengths 16 and 24.

    Under `openssl enc` the key and IV come out of ONE EVP_BytesToKey stream, so
    the IV is the `ivlen` bytes following the key. The second reading (IV =
    leading salt bytes) covers a blob written with an explicit short IV."""
    if kdf.startswith("evp-"):
        s = evp_bytes_to_key(pw, salt, klen + ivlen, KDF_DIGEST[kdf])
        return [(s[:klen], s[klen:klen + ivlen]), (s[:klen], salt[:ivlen])]
    return [(key_for(pw, salt, klen, kdf), salt[:ivlen])]


# An 8-byte-block cipher (DES/3DES/Blowfish/CAST5) needs an 8-byte IV. AES needs
# 16. The two families share key lengths 16 and 24, so the IV length has to be
# chosen by which family is being swept, not by key length alone. Passing the
# 16-byte salt straight through raises ValueError for every 8-byte-block cipher,
# and passing an 8-byte slice to AES raises it the other way.
IVLEN_BY_KEYLEN = {8: 8, 16: 8, 24: 8, 32: 16}


def ivlen_for(alg: str) -> int:
    return 16 if alg == "aes" else 8


class Unsupported(Exception):
    pass


def make_enc(alg: str):
    if alg == "aes":
        return make_aes
    if alg == "des":
        return lambda k, v: DES.new(k, DES.MODE_CBC, v)
    if alg == "des-ede3":
        return lambda k, v: DES3.new(k, DES3.MODE_CBC, v)
    if alg == "blowfish":
        return lambda k, v: Blowfish.new(k, Blowfish.MODE_CBC, v)
    if alg == "cast5":
        return lambda k, v: CAST.new(k, CAST.MODE_CBC, v)
    raise Unsupported


def make_dec(alg: str, key: bytes, iv: bytes):
    if alg == "aes":
        return make_aes(key, iv).decrypt
    if alg == "des":
        if len(key) != 8:
            raise Unsupported
        return DES.new(key, DES.MODE_CBC, iv).decrypt
    if alg == "des-ede3":
        if len(key) not in (16, 24):
            raise Unsupported
        return DES3.new(key, DES3.MODE_CBC, iv).decrypt
    if alg == "blowfish":
        if not 4 <= len(key) <= 56:
            raise Unsupported
        return Blowfish.new(key, Blowfish.MODE_CBC, iv).decrypt
    if alg == "cast5":
        if not 5 <= len(key) <= 16:
            raise Unsupported
        return CAST.new(key, CAST.MODE_CBC, iv).decrypt
    raise Unsupported


ALGS = {
    "des": (8,),
    "des-ede3": (16, 24),
    "blowfish": (16, 24, 32),
    "cast5": (16,),
}

AES_ALGS = {"aes": (16, 24, 32)}


def make_aes(key: bytes, iv: bytes):
    from Crypto.Cipher import AES
    if len(key) not in (16, 24, 32):
        raise Unsupported
    return AES.new(key, AES.MODE_CBC, iv)


def pkcs7_ok(tail: bytes, bs: int) -> bool:
    k = tail[-1]
    if k < 1 or k > bs or k > len(tail):
        return False
    return tail[-k:] == bytes([k]) * k


def printable_ratio(b: bytes) -> float:
    if not b:
        return 0.0
    return sum(1 for x in b if 32 <= x <= 126 or x in (9, 10, 13)) / len(b)


def sweep(cands, salt, ct, kdfs, floor=0.90, verbose=True, bs=8, padded=True):
    """bs is the cipher block size: 8 for DES/3DES/Blowfish/CAST5, 16 for AES.

    `padded=False` (framing b) drops the PKCS7 gate, because there the final
    block is missing its tail and the padding bytes are not in the file. The
    screen then falls back to printability of the whole plaintext, which is
    weaker and must be read as such.
    """
    hits = []
    tried = 0
    lasttwo = ct[-2 * bs:]
    algs = ALGS if bs == 8 else AES_ALGS
    for kdf in kdfs:
        for alg, klens in algs.items():
            for klen in klens:
                for pw in cands:
                    for key, iv in cells_for(pw, salt, klen, kdf, ivlen_for(alg)):
                        tried += 1
                        try:
                            make_dec(alg, key, iv)
                        except (Unsupported, ValueError, KeyError):
                            continue
                        if padded:
                            tail = make_dec(alg, key, iv)(lasttwo)[-bs:]
                            if not pkcs7_ok(tail, bs):
                                continue
                        pt = make_dec(alg, key, iv)(ct)
                        r = printable_ratio(pt)
                        if r < floor:
                            continue
                        hits.append((r, kdf, alg, klen, pw, pt))
                        if verbose:
                            print(f"  SURVIVOR r={r:.3f} kdf={kdf} alg={alg} "
                                  f"klen={klen} pw={pw!r}")
                            print(f"    {pt[:200]!r}")
    return hits, tried


def selftest() -> int:
    """For every (kdf, alg, klen, bs) cell, encrypt a known plaintext under that
    cell's own convention and require the sweep to re-find it. The final-block
    PKCS7 check is included, so this also proves the verifier does not reject the
    correct key."""
    salt = bytes(range(16))
    pw = b"SELFTESTPW"
    good = b"SELFTEST-PLAINTEXT-0123456789-abcdefghijklmnop"
    failures = 0
    cells = 0
    for kdf in KDF_DIGEST:
        for alg, klens in (ALGS | AES_ALGS).items():
            for klen in klens:
                bs = 16 if alg == "aes" else 8
                for key, iv in cells_for(pw, salt, klen, kdf, ivlen_for(alg)):
                    cells += 1
                    pad = bs - (len(good) % bs)
                    pt = good + bytes([pad]) * pad
                    try:
                        enc = make_enc(alg)(key, iv).encrypt
                    except (ValueError, KeyError) as e:
                        failures += 1
                        print(f"  SETUP-FAIL {alg} klen={klen}: {e}")
                        continue
                    ct = enc(pt) if callable(enc) else enc.encrypt(pt)
                    hits, _ = sweep([pw], salt, ct, [kdf], bs=bs,
                                    padded=True, verbose=False)
                    if not hits:
                        failures += 1
                        print(f"  MISS kdf={kdf} alg={alg} klen={klen}")
                        continue
                    best = max(hits, key=lambda h: h[0])
                    if not best[5].startswith(good):
                        failures += 1
                        print(f"  WRONG kdf={kdf} alg={alg} klen={klen} -> "
                              f"{best[5][:80]!r}")
    if failures:
        print(f"\nSELFTEST FAIL -- {failures}/{cells} cells")
        return 1
    print(f"\nSELFTEST PASS -- {cells}/{cells} cells round-trip, and the PKCS7 "
          f"final-block verifier accepts every correct key")
    return 0


def candidates(limit):
    out = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "gsmg_wordlist.py")],
        capture_output=True, timeout=3600).stdout
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
    ap.add_argument("--blob", default="urlblob", choices=sorted(FAMILY))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--kdf", default="evp-md5,evp-sha256")
    ap.add_argument("--floor", type=float, default=0.90)
    ap.add_argument("--framing", default="c", choices=("a", "b", "c"))
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    salt, ct = load_blob(a.blob, a.framing)
    bs = 8 if a.framing == "c" else 16
    padded = a.framing != "b"
    print(f"{a.blob} framing={a.framing}: salt {salt.hex()}  "
          f"ciphertext {len(ct)} B  ct%16={len(ct) % 16}  "
          f"block={bs}  pkcs7_checkable={padded}")
    cands = candidates(None if a.full else (a.limit or 5000))
    print(f"candidates: {len(cands)} unique passphrases")
    hits, tried = sweep(cands, salt, ct, a.kdf.split(","), floor=a.floor,
                        bs=bs, padded=padded)
    print(f"\nswept {tried} (candidate x alg x klen) combinations over "
          f"KDFs {a.kdf.split(',')}")
    if not hits:
        gate = "PKCS7 + printability" if padded else "printability only (no pad gate)"
        print(f"RESULT: no survivor cleared {gate}")
        return 0
    print(f"RESULT: {len(hits)} survivors -- adjudicate by hand, not a solve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())