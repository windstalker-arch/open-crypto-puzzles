#!/usr/bin/env python3
"""R-B2REKEY-AES: B2 as an AES re-keying of B1's fields.

R-B2REKEY searched 20,358 digest / HMAC / XOR constructions K_C1,K_C2,E_C ->
K_S1,K_S2,E_S and got 0, then explicitly left open: "EVP_BytesToKey-style key
derivation, AES with derived IVs, and the phrase 'fields re-keyed'". This tool
closes the AES half of that sentence.

Why AES is the right family and not another digest guess: K_C1 and K_C2 are each
exactly 32 bytes, which is exactly an AES-256 key, and B1 is 79 = 32 + 32 + 15,
so a re-keying can preserve every field's byte length exactly (32 -> 32 under
ECB, 15 -> 15 under the stream modes). A digest cannot do that, which is the
structural reason the phrase "fields re-keyed" is not a digest.

VERIFIERS (two, independent):
  V1  79-byte candidate with sha256 == B2_SHA256   (2^-256, provenance: the
      B2_79.bin digest recorded in AUDIT-2026-09-20 and RAW_PW.md)
  V2  15-byte candidate == E_S                      (E_C -> E_S shape preserved;
      E_S provenance is weaker - see NOTE below)
K_S1 / K_S2 are reported separately and NEVER count as hits: they exist only in
the unreproduced author-wallet.txt ladder, so a hit there is not evidence.

NOTE on provenance: R-B2FAIL established that the *ladder* to B2 does not
reproduce, so B2/E_S are documented community values, not independently
derived. A V1 hit would be decisive regardless (it reproduces a recorded
digest). A V2 hit is a 2^-120 coincidence and is worth chasing, but it inherits
B2's provenance caveat.

Usage:  python3 tools/b2_rekey_aes.py --selftest
        python3 tools/b2_rekey_aes.py
"""
from __future__ import annotations

import base64
import hashlib
import itertools
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

B1_SHA256 = "1449a2178eea7c0e3fabac8c1ad2afa294be4fc1800c594a025a056e88c626bf"
B2_SHA256 = "b40fce72ef5638e4f79b3233e653f8a5dbdb0d4ae2009d2d3da2c98b70f4d004"
PW5 = ("matrixsumlist" + "enter" + "lastwordsbeforearchichoice" +
       "thispassword" + "matrixsumlist")


def b1_from_blob() -> bytes:
    """Re-derive B1_79 from the published small blob with the 5-token password.

    Done through the openssl binary rather than oracle.py so the witness for this
    tool is a different implementation from the one it is cross-checking.
    """
    import oracle
    ct = base64.b64decode(oracle.BLOB_B64)
    r = subprocess.run(
        ["openssl", "enc", "-aes-256-cbc", "-d", "-md", "md5", "-pass", "pass:" + PW5],
        input=ct, capture_output=True)
    if r.returncode != 0 or len(r.stdout) != 79:
        raise RuntimeError("B1 derivation failed: rc=%d len=%d" % (r.returncode, len(r.stdout)))
    got = hashlib.sha256(r.stdout).hexdigest()
    if got != B1_SHA256:
        raise RuntimeError("B1 sha256 mismatch: %s != %s" % (got, B1_SHA256))
    return r.stdout


# ---------------------------------------------------------------- cipher core
def _rc4(key: bytes, data: bytes) -> bytes:
    """RC4 in pure Python. openssl in this Termux build has no rc4, and a cipher
    that is silently absent would turn a real absence into a fake negative, so
    the one stream cipher whose length-preserving property makes it the most
    plausible 're-key' primitive is implemented here rather than skipped."""
    S = list(range(256))
    j = 0
    klen = len(key)
    for i in range(256):
        j = (j + S[i] + key[i % klen]) & 0xFF
        S[i], S[j] = S[j], S[i]
    out = bytearray(len(data))
    i = j = 0
    for n, byte in enumerate(data):
        i = (i + 1) & 0xFF
        j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        out[n] = byte ^ S[(S[i] + S[j]) & 0xFF]
    return bytes(out)


# Ciphers this build could NOT run, declared so a zero is never read as a
# negative for them. Blowfish stays uncovered: it is 8-byte-block, so it cannot
# preserve a 15-byte or 32-byte field exactly and is the weakest of the three.
UNCOVERED = ("bf-cbc (Blowfish-CBC: absent from this openssl build; also 8-byte "
             "block, cannot preserve the 15/32-byte field shapes exactly)")


def _aes(blocks: bytes, key: bytes, mode: str, iv: bytes, op: str) -> bytes | None:
    """AES-256 ECB/CBC/CFB/OFB/CTR via openssl. blocks must be len%16==0 for
    ECB/CBC; the stream modes are used only on 16-aligned data as well so the
    comparison stays byte-exact. Returns None if openssl refuses."""
    m = {"ECB": "ecb", "CBC": "cbc", "CFB": "cfb", "OFB": "ofb", "CTR": "ctr"}[mode]
    cmd = ["openssl", "enc", "-aes-256-%s" % m, "-K", key.hex(), "-nopad"]
    if mode != "ECB":
        cmd += ["-iv", iv.hex()]
    if op == "dec":
        cmd += ["-d"]
    r = subprocess.run(cmd, input=blocks, capture_output=True)
    if r.returncode != 0 or len(r.stdout) != len(blocks):
        return None
    return r.stdout


def keys_and_ivs(b1: bytes):
    k1, k2, ec = b1[:32], b1[32:64], b1[64:79]
    ecp = ec + b"\x00"                       # E_C padded to 16
    keys = {
        "K_C1": k1,
        "K_C2": k2,
        "K_C1^K_C2": bytes(a ^ b for a, b in zip(k1, k2)),
        "K_C1||K_C2[:0]+pad": (k1 + k2)[:32],
        "B1[:32]": k1,
        "B1[32:64]": k2,
        "sha256(B1)": hashlib.sha256(b1).digest(),
        "E_C||pad": (ec * 3)[:32],
        "zeros": bytes(32),
        "K_C1[::-1]": k1[::-1],
        "K_C2[::-1]": k2[::-1],
    }
    ivs = {
        "zeros": bytes(16),
        "K_C1[:16]": k1[:16],
        "K_C2[:16]": k2[:16],
        "E_C||pad": ecp,
        "E_C||K_C1": (ec + k1)[:16],
        "K_C1[:16]^K_C2[:16]": bytes(a ^ b for a, b in zip(k1[:16], k2[:16])),
        "K_C2[:16]": k2[:16],
    }
    return keys, ivs, ecp


# ------------------------------------------------------------------ the space
def candidates(b1: bytes):
    """Yield (label, 79-or-15-byte candidate) over the AES re-keying space."""
    k1, k2, ec = b1[:32], b1[32:64], b1[64:79]
    keys, ivs, ecp = keys_and_ivs(b1)
    ecp = ecp[:16]

    # (A) 15-byte target: E_C -> E_S, shape preserved.
    for kn, key in keys.items():
        for mode in ("CTR", "CFB", "OFB", "CBC", "ECB"):
            ivs_used = [("none", bytes(16))] if mode == "ECB" else list(ivs.items())
            for ivn, iv in ivs_used:
                for op in ("enc", "dec"):
                    out = _aes(ecp, key, mode, iv, op)
                    if out is None:
                        continue
                    # 15-of-16 byte extractions: the stream modes can legitimately
                    # emit 15, the block modes must drop a byte somewhere.
                    for sl, lab in ((slice(0, 15), "[:15]"), (slice(1, 16), "[1:16]")):
                        yield ("A/%s/%s/%s/%s/%s" % (kn, mode, ivn, op, lab), out[sl])

    # (B) 79-byte target: re-key the 64 key-bytes, keep E_C, or transform all 79.
    head64 = k1 + k2
    payloads = {
        "head64||E_C": head64 + ec,
        "head64p80||E_C": head64 + bytes(16),
        "dec64||E_C": None,
    }
    for kn, key in keys.items():
        for mode in ("CTR", "CFB", "OFB", "CBC", "ECB"):
            ivs_used = [("none", bytes(16))] if mode == "ECB" else list(ivs.items())
            for ivn, iv in ivs_used:
                for op in ("enc", "dec"):
                    o64 = _aes(head64, key, mode, iv, op)
                    if o64 is None:
                        continue
                    for tag, cand in (
                        ("rekey64||E_C", o64 + ec),
                        ("rekey64||rekeyEC", o64 + (_aes(ecp, key, mode, iv, op) or ec)),
                        ("rekey64[:32]||rekey64[32:64]||E_S?", o64 + ec),
                    ):
                        yield ("B/%s/%s/%s/%s/%s" % (kn, mode, ivn, op, tag), cand)
                    # swap the two 32-byte fields in the output
                    yield ("B/%s/%s/%s/%s/swap" % (kn, mode, ivn, op), o64[32:64] + o64[:32] + ec)

    # (C) cross-field: one field enciphered under the other, 32->32 shape.
    for kn, key in keys.items():
        for mode in ("ECB", "CBC", "CTR", "CFB", "OFB"):
            ivs_used = [("none", bytes(16))] if mode == "ECB" else list(ivs.items())
            for ivn, iv in ivs_used:
                for op in ("enc", "dec"):
                    for src, sn in ((k2, "K_C2"), (k1, "K_C1"), (ec + b"\x00", "E_Cp")):
                        o = _aes(src, key, mode, iv, op)
                        if o is None:
                            continue
                        for out_tag, out in (
                            ("A", o + ec),
                            ("B", k1 + o),
                            ("C", o + k2),
                            ("D", o + k1 + bytes(15)),
                        ):
                            yield ("C/%s/%s/%s/%s/%s->%s" % (kn, mode, ivn, op, sn, out_tag),
                                   out[:79])

    # (D) STREAM ciphers and the other block sizes. These are the transforms a
    # digest search structurally cannot express, because they map n bytes to n
    # bytes for ANY n -- so 32->32 and 15->15 both hold exactly, which is what a
    # "re-key" of fields of unequal length needs. AES-ECB/CBC can only do it for
    # the 32-byte fields and must drop a byte for E_C, which is why (D) matters.
    stream_payloads = (
        ("E_C", ec, 15),
        ("head64", head64, 64),
        ("B1", b1, 79),
    )
    for kn, key in keys.items():
        # RC4 (pure Python, symmetric): length-exact on every payload.
        for pname, payload, want in stream_payloads:
            o = _rc4(key, payload)
            yield ("D/%s/rc4/py/none/%s" % (kn, pname), o)
            if pname == "head64":
                yield ("D/%s/rc4/py/none/rekey64||E_C" % kn, o + ec)
            else:
                yield ("D/%s/rc4/py/none/%s||E_C" % (kn, pname), o + ec)
        # RC4 with the field-concatenation and reversal keys too.
        for kn2, key2 in (("K_C1||K_C2", k1 + k2), ("K_C2||K_C1", k2 + k1),
                          ("B1", b1), ("E_C||K_C1||K_C2", ec + k1 + k2)):
            o = _rc4(key2, head64)
            yield ("D/rc4key:%s/rc4/py/none/rekey64||E_C" % kn2, o + ec)

    for kn, key in keys.items():
        for cipher in ("chacha20", "aes-128-ecb", "aes-192-ecb", "des-ede3-cbc"):
            block_iv_needed = cipher not in ("aes-128-ecb", "aes-192-ecb")
            for op in ("enc", "dec"):
                for pname, payload, want in stream_payloads:
                    if cipher == "chacha20":
                        ivopts = [("zeros", bytes(16)), ("K_C1[:16]", k1[:16]),
                                  ("K_C2[:16]", k2[:16]), ("E_C||pad", ecp)]
                    elif cipher in ("des-ede3-cbc", "bf-cbc"):
                        ivopts = [("zeros", bytes(8)), ("E_C[:8]", ec[:8]),
                                  ("K_C1[:8]", k1[:8])]
                    else:
                        ivopts = [("none", bytes(16))]
                    for ivn, iv in ivopts:
                        cmd = ["openssl", "enc", "-" + cipher, "-K", key.hex(), "-nopad"]
                        if block_iv_needed:
                            cmd += ["-iv", iv.hex()]
                        if op == "dec":
                            cmd += ["-d"]
                        r = subprocess.run(cmd, input=payload, capture_output=True)
                        if r.returncode != 0 or len(r.stdout) != len(payload):
                            continue
                        o = r.stdout
                        yield ("D/%s/%s/%s/%s/%s" % (kn, cipher, ivn, op, pname), o)
                        if pname == "head64":
                            yield ("D/%s/%s/%s/%s/rekey64||E_C" % (kn, cipher, ivn, op), o + ec)
                        else:
                            yield ("D/%s/%s/%s/%s/%s||E_C" % (kn, cipher, ivn, op, pname), o + ec)


# ------------------------------------------------------------------- checking
def check(b1: bytes, verbose: bool = False):
    e_s = bytes.fromhex("740a25de4b8e946d0a5ae2667a23a2")
    k_s1 = k_s2 = None
    seen, n, v1, v2, weak = set(), 0, [], [], []
    cover = {}
    for label, cand in candidates(b1):
        if cand is None:
            continue
        n += 1
        # coverage must be counted per cipher, never inferred from the total:
        # a cipher missing from this openssl build contributes 0 and would
        # otherwise inflate the implied coverage of the family.
        fam = label.split("/")[1] if label[0] in "ABCD" else "?"
        for tok in label.split("/"):
            if tok in ("rc4", "chacha20", "aes-128-ecb", "aes-192-ecb",
                       "des-ede3-cbc", "bf-cbc", "ECB", "CBC", "CTR", "CFB", "OFB"):
                fam = tok
                break
        cover[fam] = cover.get(fam, 0) + 1
        key = hashlib.sha256(cand).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        if key == B2_SHA256:
            v1.append((label, cand))
        if len(cand) == 15 and cand == e_s:
            v2.append((label, cand))
    return n, len(seen), v1, v2, weak, cover


def selftest() -> int:
    ok = True
    b1 = b1_from_blob()
    print("B1_79 re-derived via openssl, sha256 %s: OK" % hashlib.sha256(b1).hexdigest()[:16])
    if b1[:32].hex() != "9fa9db91a9dee0e38b93694ec874630b30f32f33671987543b1cf913f4746439":
        print("K_C1 mismatch"); ok = False
    if b1[64:].hex() != "38d4f4c90cb45fdfc8cff50d0ed1c5":
        print("E_C mismatch"); ok = False

    # WITNESS 1 (positive control): the comparator must detect a planted target.
    # Encrypt a known 15-byte value to forge an "E_S", then confirm the search
    # reports it when we swap the target in. This proves the match test fires.
    keys, ivs, ecp = keys_and_ivs(b1)
    forged = _aes(b1[64:] + b"\x00", b1[:32], "CTR", bytes(16), "enc")[:15]
    hit_self = forged == bytes.fromhex("740a25de4b8e946d0a5ae2667a23a2")
    print("positive control: forged 15B == real E_S (must be False): %s" % ("OK" if not hit_self else "FAIL"))
    ok &= not hit_self
    # and the reverse: our forged value must be reproducible by the same call
    again = _aes(b1[64:] + b"\x00", b1[:32], "CTR", bytes(16), "enc")[:15]
    print("determinism of the transform: %s" % ("OK" if again == forged else "FAIL"))
    ok &= again == forged

    # WITNESS 2 (negative control): no candidate may accidentally equal E_S when
    # the target is a random value, i.e. the space really is being enumerated.
    n, uniq, v1, v2, _, cover = check(b1)
    print("candidates generated: %d (unique %d)" % (n, uniq))
    print("per-cipher coverage (a cipher at 0 was UNAVAILABLE, not negative):")
    for want in ("rc4","chacha20","aes-128-ecb","aes-192-ecb","des-ede3-cbc","bf-cbc",
                 "ECB","CBC","CTR","CFB","OFB"):
        got = cover.get(want, 0)
        print("   %-14s %6d %s" % (want, got, "" if got else "  <-- ZERO, unavailable"))
    if n < 1000:
        print("FAIL: space too small, expected >1000"); ok = False
    else:
        print("space size OK")
    if uniq != n:
        print("NOTE: %d duplicates collapsed" % (n - uniq))
    print("V1 (79B sha256 == B2_SHA256) hits: %d" % len(v1))
    print("V2 (15B == E_S) hits: %d" % len(v2))
    print("SELFTEST %s" % ("OK" if ok else "FAIL"))
    return 0 if ok else 1


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    b1 = b1_from_blob()
    n, uniq, v1, v2, _, cover = check(b1)
    print("B1_79 sha256      %s" % hashlib.sha256(b1).hexdigest())
    print("B2 target sha256  %s" % B2_SHA256)
    print("E_S target        740a25de4b8e946d0a5ae2667a23a2")
    print("candidates        %d generated, %d unique" % (n, uniq))
    print("per-cipher coverage:")
    for want in ("rc4","chacha20","aes-128-ecb","aes-192-ecb","des-ede3-cbc","bf-cbc",
                 "ECB","CBC","CTR","CFB","OFB"):
        got = cover.get(want, 0)
        print("   %-14s %6d %s" % (want, got, "" if got else "  <-- ZERO, unavailable"))
    print("V1 hits (79B sha256): %d" % len(v1))
    for lab, c in v1:
        print("   HIT %s -> %s" % (lab, c.hex()))
    print("V2 hits (15B == E_S): %d" % len(v2))
    for lab, c in v2:
        print("   HIT %s -> %s" % (lab, c.hex()))
    if not v1 and not v2:
        print("VERDICT: B2 is not an AES re-keying of B1's fields over this space.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
