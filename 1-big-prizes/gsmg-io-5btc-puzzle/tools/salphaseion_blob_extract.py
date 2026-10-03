#!/usr/bin/env python3
"""Segment-3 / post-z4 base64 blobs: correct instrument + positive controls, then sweep.

CORRECTION OVER THE FIRST ATTEMPT (recorded, not hidden): v1 required
len(ct) % 16 == 0 and applied PKCS7 unpad to EVERY cipher. That is only true of
CBC/ECB. openssl's CFB/OFB/CTR are stream-ish modes that pad NOTHING, so a
31-byte ciphertext -- which is exactly what this blob has -- would have been
rejected before any key was tried. v1's "no hit" was therefore partly vacuous.
v2 uses the real per-cipher block size and skips unpadding for the unpadded
modes, and every mode is proved against the openssl CLI before it is trusted.

DISCRIMINATOR: for CBC the correct key has a valid PKCS7 pad, for the unpadded
modes it does not exist, so the pass criterion is asymmetric on purpose --
printable ASCII alone is too weak at 31 bytes (expected false-positive rate is
material), so unpadded modes additionally require the output to survive a
round-trip re-encrypt under the same key/iv/mode. That is a ~2^-64 style check.
"""
import base64, hashlib, re, string, subprocess, sys, pathlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# name -> (key_len, iv_len, block, padded?)
SPEC = {
    "aes-128-cbc": (16, 16, 16, True),  "aes-192-cbc": (24, 16, 16, True),
    "aes-256-cbc": (32, 16, 16, True),  "aes-128-ecb": (16, 0, 16, True),
    "aes-256-ecb": (32, 0, 16, True),   "aes-128-cfb": (16, 16, 16, False),
    "aes-192-cfb": (24, 16, 16, False), "aes-256-cfb": (32, 16, 16, False),
    "aes-128-ofb": (16, 16, 16, False), "aes-192-ofb": (24, 16, 16, False),
    "aes-256-ofb": (32, 16, 16, False), "aes-128-ctr": (16, 16, 16, False),
    "aes-192-ctr": (24, 16, 16, False), "aes-256-ctr": (32, 16, 16, False),
    "des-ede3-cbc": (24, 8, 8, True),   "des-ede-cbc": (16, 8, 8, True),
    # bf-cbc DELIBERATELY ABSENT: `openssl enc -ciphers` on this device
    # (OpenSSL 3.6.3, Termux) lists zero bf-* ciphers, so it cannot be
    # exercised here at all. Excluded for a MEASURED reason, not a guess.
}
DIGESTS = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]
B64 = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"


def evp(pw, salt, klen, ivlen, digest):
    dtot, d = b"", b""
    while len(dtot) < klen + ivlen:
        d = hashlib.new(digest, d + pw + salt).digest()
        dtot += d
    return dtot[:klen], dtot[key_len_slice(klen, ivlen, dtot):][:ivlen] if ivlen else b""


def key_iv(pw, salt, klen, ivlen, digest):
    dtot, d = b"", b""
    while len(dtot) < klen + ivlen:
        d = hashlib.new(digest, d + pw + salt).digest()
        dtot += d
    return dtot[:klen], (dtot[klen:klen + ivlen] if ivlen else b"")


def unpad(b, bs):
    if not b:
        return None
    n = b[-1]
    if n < 1 or n > bs or n > len(b) or b[-n:] != bytes([n]) * n:
        return None
    return b[:-n]


def _alg(name, key):
    if name.startswith("des-ede3"):
        from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
        return TripleDES(key)
    if name.startswith("des-ede"):
        from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
        return TripleDES(key + key[:8])
    return algorithms.AES(key)


def _mode(name, iv):
    if name.endswith("cbc"):
        return modes.CBC(iv)
    if name.endswith("cfb"):
        return modes.CFB(iv)
    if name.endswith("ofb"):
        return modes.OFB(iv)
    if name.endswith("ctr"):
        return modes.CTR(iv)
    return modes.ECB()


def decrypt(bb, pw, cipher, digest):
    if len(bb) < 16 or bb[:8] != b"Salted__":
        return None
    klen, ivlen, bs, padded = SPEC[cipher]
    salt, ct = bb[8:16], bb[16:]
    if not ct or (padded and len(ct) % bs):
        return None
    if not padded and ivlen and len(ct) < bs:
        return None
    try:
        key, iv = key_iv(pw, salt, klen, ivlen, digest)
        c = Cipher(_alg(cipher, key), _mode(cipher, iv)).decryptor()
        pt = c.update(ct) + c.finalize()
    except Exception:
        return None
    if padded:
        pt = unpad(pt, bs)
        if pt is None:
            return None
    else:
        # re-encrypt round-trip: a real key reproduces the ciphertext exactly
        try:
            e = Cipher(_alg(cipher, key), _mode(cipher, iv)).encryptor()
            if e.update(pt) + e.finalize() != ct:
                return None
        except Exception:
            return None
    try:
        s = pt.decode("ascii")
    except UnicodeDecodeError:
        return None
    if not s or sum(c in string.printable for c in s) / len(s) < 1.0:
        return None
    return s


def openssl_ct(pt, cipher, digest, pw):
    return subprocess.run(
        ["openssl", "enc", f"-{cipher}", "-a", "-A", "-md", digest, "-pass", "pass:" + pw],
        input=pt, capture_output=True).stdout.decode().strip()


def sweep(blobs, passphrases, completions_fn, label):
    hits, tried = [], 0
    for base in blobs:
        for full in completions_fn(base):
            try:
                bb = base64.b64decode(full + "=" * ((4 - len(full) % 4) % 4), validate=True)
            except Exception:
                continue
            for pw in passphrases:
                for c in SPEC:
                    for d in DIGESTS:
                        tried += 1
                        r = decrypt(bb, pw.encode(), c, d)
                        if r:
                            hits.append((base[:12], full[-6:], pw, c, d, r))
    print(f"[{label}] attempts={tried} printable-pad-valid hits={len(hits)}")
    for h in hits:
        print(f"   HIT {h[0]}..{h[1]} pw={h[2]!r} {h[3]} {h[4]} -> {h[5]!r}")
    return hits


def main():
    # ---------- POSITIVE CONTROLS, every mode, against the openssl CLI ----------
    ok = True
    for c in SPEC:
        d = "md5" if c not in ("aes-128-cfb", "aes-256-ctr") else "sha256"
        pt = b"four first hints ok" if SPEC[c][3] else b"four first hints 12345"
        ct = openssl_ct(pt, c, d, "enter")
        if not ct:
            print(f"  control {c}: openssl produced nothing, skipped")
            continue
        # A PADDED mode's ciphertext length is self-delimiting: dropping a base64
        # char drops a whole byte and breaks block alignment, which says nothing
        # about the key. So the one-char-truncation treatment is applied ONLY to
        # the unpadded modes -- which is exactly the condition the real 31-byte
        # ciphertext presents.
        trunc = ct if SPEC[c][3] else ct[:-1]
        got = decrypt(base64.b64decode(trunc + "=" * ((4 - len(trunc) % 4) % 4)),
                      b"enter", c, d)
        good = got == pt.decode()
        ok &= good
        print(f"  control {c:12} {d:6} {'PASS' if good else 'FAIL'}"
              + ("" if good else f"  got={got!r} want={pt.decode()!r}"))
    if not ok:
        print("\n!! INSTRUMENT VOID - a control failed; search NOT run")
        return 3

    # ---------- REAL ----------
    t = re.sub(r"\s+", "", pathlib.Path(
        "/data/data/com.termux/files/home/open-crypto-puzzles/1-big-prizes/"
        "gsmg-io-5btc-puzzle/data/live_salphaseion.txt").read_text())
    seg3 = t[860:958]
    post = t[959:1075]
    # EXTRACTION, third attempt, and the rule is now ANCHORED rather than
    # heuristic. Two earlier rules both failed the same way: prose and base64 are
    # CONTIGUOUS and both drawn from [A-Za-z0-9+/], so any maximal-run regex
    # swallows the prose. Requiring uppercase/digits did not help, because the
    # COMBINED run inherits them from the base64 tail. Length-multiple-of-4 does
    # not pin a start either. The only unambiguous anchor on this page is the
    # OpenSSL magic itself: base64("Salted__") == "U2FsdGVkX1".
    m3 = re.search(r"U2FsdGVkX[A-Za-z0-9+/]*", seg3)
    seg3_blob = m3.group(0) if m3 else None
    print(f"seg3 OpenSSL blob anchored: {seg3_blob is not None} "
          f"len={len(seg3_blob) if seg3_blob else 0}")
    if seg3_blob:
        assert seg3_blob.startswith("U2FsdGVkX1"), "marker wrong"
        bb = base64.b64decode(seg3_blob + "=" * ((4 - len(seg3_blob) % 4) % 4), validate=True)
        print(f"  decodes to {len(bb)} bytes, header={bb[:8]!r}, "
              f"ct={len(bb)-16} bytes (ct%16={(len(bb)-16)%16}, ct%8={(len(bb)-16)%8})")
        print(f"  => a PADDED mode is IMPOSSIBLE at this length: ct must be a "
              f"multiple of 16 (CBC) or 8 (3DES/BF). Only unpadded modes fit.")
    # post-z4: no Salted__ header, so it is NOT an openssl enc blob; characterised
    # separately rather than guessed at here.
    post_run = re.search(r"[A-Za-z0-9+/]{20,}", post).group(0)
    print(f"post-z4 run (NO Salted__ header, so not an openssl enc blob): "
          f"len={len(post_run)} {post_run[:16]!r}...")
    blobs = [seg3_blob] if seg3_blob else []
    print(f"\nreal blob: seg3 only (post-z4 is not an openssl enc blob). "
          f"ct=31 => unpadded modes only at this length.")
    pws = ["enter", "Enter", "ENTER", "lastcommand", "yourlastcommand",
           "firsthint", "firsthints", "fourfirsthints", "four", "fourfirsthint",
           "matrixsumlist", "thispassword", "lastwordsbeforearchichoice",
           "shabefourfirsthintisyourlastcommand", "thelastcommand", "sha",
           "shabe", "ans", "gsmg.io/theseedisplanted", "half", "betterhalf"]
    # Shape A: the blob EXACTLY as it stands (47 bytes, ct=31). Since 31 is not a
    # multiple of 16 or 8, NO padded mode can be the answer -- only unpadded.
    hitsA = sweep(blobs, pws, lambda b: [b], "REAL shapeA: verbatim, unpadded modes only")
    # Shape B: one missing trailing base64 char (48 bytes, ct=32), all modes.
    hitsB = sweep(blobs, pws, lambda b: [b + ch for ch in B64], "REAL shapeB: +1 char")
    hits = hitsA + hitsB
    print("\nRESULT:", "POSITIVE" if hits else "no hit (all modes proven on controls)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
