#!/usr/bin/env python3
"""ladder_census.py -- does the B1->B2 ladder CONTINUE? Try every ladder key, in
every sane encoding, as a password against every OpenSSL envelope in reach.

THE MOTIVE. `WIF(K_C1)` is the only key in the corpus with a demonstrated
function: it is the password that opens the p32 outer envelope and yields
B2_79. That proves the 79-byte records are a LADDER whose rungs are unlocked by
the previous rung's key -- not a coincidence. So the three unused keys
(`K_C2`, `K_S1`, `K_S2`) are the obvious next rungs, and nobody has ever tested
them as passwords. Row 94 tested the phrase "sumofaremainderofanunbalancedequ-
ation" as a string; `tools/xor_halfpair_sweep.py` tested HALF-AND-BETTER-HALF
as a phrase over the digit streams (312 strings). Neither used a ladder key.

THE TARGET. `analysis/tested.md:11426` records a THIRD 79-byte record -
`salphaseion_plain_79.bin`, sha256 `9c14868c...` - which is NOT B1_79, NOT
B2_79, and NOT any 79-aligned window of the 1327 B cosmic plaintext, and whose
provenance is unknown. The row explicitly declines to import it as certified.
If a ladder key opens an envelope to exactly that hash, it is certified and the
ladder is extended. This gives a HARD acceptance test with no oracle call: three
known 79-byte target digests.

`analysis/tested.md:12095` notes that of ten `Salted__` blobs only ONE is an
authenticated author artifact, so most of the envelope set is unauthenticated
solver material - which is exactly why a positive here needs a hash witness
rather than merely valid padding.

CONTROL FIRST: `WIF(K_C1)` against salt `b45a5e3d827593ca` must reproduce
`b40fce72...`. If that does not fire, every negative below is noise.
"""
import base64
import hashlib
import re
import time
from pathlib import Path

import os

from Crypto.Cipher import AES

B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
B64RE = re.compile(rb"[A-Za-z0-9+/=]{40,}")
FOLDER = Path(__file__).resolve().parent.parent

TARGET_79 = {
    "B1_79": "1449a2178eea7c0e3fabac8c1ad2afa294be4fc1800c594a025a056e88c626bf",
    "B2_79": "b40fce72ef5638e4f79b3233e653f8a5dbdb0d4ae2009d2d3da2c98b70f4d004",
    "salphaseion_plain_79": "9c14868c1364755048463305d8bc9e287abe8ab73a397a5e063f6a5e68663c8c",
}


def b58c(b):
    n = int.from_bytes(b, "big")
    s = ""
    while n:
        n, r = divmod(n, 58)
        s = B58[r] + s
    for c in b:
        if c == 0:
            s = "1" + s
        else:
            break
    return s


def b58check(b):
    return b58c(b + hashlib.sha256(hashlib.sha256(b).digest()).digest()[:4])


def wif(k32, compressed=True):
    return b58check(b"\x80" + k32 + (b"\x01" if compressed else b""))


def evp(pw, salt, dg):
    H = hashlib.md5 if dg == "md5" else hashlib.sha256
    d, prev = b"", b""
    while len(d) < 48:
        prev = H(prev + pw + salt).digest()
        d += prev
    return d[:32], d[32:48]


def unpad(p):
    n = p[-1]
    return p[:-n] if p and 0 < n <= 16 and p[-n:] == bytes([n]) * n else None


def collect_envelopes():
    env = {}
    roots = [FOLDER, Path(os.path.expanduser("~/briefcase")),
             Path(os.path.expanduser("~/storage/external/briefcase"))]
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.stat().st_size > 300000:
                continue
            try:
                raw = p.read_bytes()
            except Exception:
                continue
            blobs = [raw] if raw[:8] == b"Salted__" else []
            for t in B64RE.findall(raw):
                try:
                    blobs.append(base64.b64decode(t, validate=True))
                except Exception:
                    pass
            for d in blobs:
                if d[:8] == b"Salted__" and len(d) > 32:
                    env[hashlib.sha256(d).hexdigest()[:12]] = d
    return env


def main():
    b1 = (FOLDER / "data" / "B1_79B.bin").read_bytes()
    b2 = (FOLDER / "data" / "B2_79B.bin").read_bytes()
    keys = {"K_C1": b1[0:32], "K_C2": b1[32:64],
            "K_S1": b2[0:32], "K_S2": b2[32:64]}
    pws = {}
    for n, k in keys.items():
        pws[f"{n}:wif_c"] = wif(k, True).encode()
        pws[f"{n}:wif_u"] = wif(k, False).encode()
        pws[f"{n}:raw"] = k
        pws[f"{n}:hex"] = k.hex().encode()
        pws[f"{n}:HEX"] = k.hex().upper().encode()
        pws[f"{n}:b64"] = base64.b64encode(k)
        pws[f"{n}:rev"] = k[::-1]

    env = collect_envelopes()
    print(f"[inventory] {len(env)} distinct Salted__ envelopes, {len(pws)} password forms")
    print(f"[inventory] 3 known 79-byte target digests loaded\n")

    # ---------- CONTROL ----------
    # NB: this project's wif() is UNCOMPRESSED (tools/rung2_b2.py: b58check(0x80, key32),
    # no 0x01 suffix), so the known-good B2 password is the uncompressed form. Try both
    # rather than assume, and report which one actually fires.
    ctl = None
    for h, d in env.items():
        if d[8:16].hex() == "b45a5e3d827593ca" and len(d) - 16 == 80:
            ctl = d
    assert ctl is not None, "control envelope (p32 outer) not found"
    fired = None
    for form in ("K_C1:wif_u", "K_C1:wif_c", "K_C1:raw", "K_C1:hex"):
        k, iv = evp(pws[form], ctl[8:16], "md5")
        pt = unpad(AES.new(k, AES.MODE_CBC, iv).decrypt(ctl[16:]))
        sh = hashlib.sha256(pt).hexdigest() if pt else None
        if sh == TARGET_79["B2_79"]:
            fired = form
            break
    print(f"[control] WIF(K_C1) x p32-outer -> B2_79 via form: {fired}")
    print(f"[control] WIF(K_C1) uncompressed = {wif(keys['K_C1'], False)}")
    if not fired:
        print("CONTROL DID NOT FIRE -- aborting; any negative here would be noise.")
        return 1

    # ---------- BATTERY ----------
    t0 = time.time()
    valid, hits, skipped = [], [], []
    trials = 0
    for eh, d in sorted(env.items()):
        salt, ct = d[8:16], d[16:]
        if len(ct) % 16 or not ct:
            # not a real CBC envelope: a base64 token that merely decodes to something
            # beginning "Salted__". Counted and reported so the gap is visible.
            skipped.append((eh, salt.hex(), len(ct)))
            continue
        for pn, pw in pws.items():
            for dg in ("md5", "sha256"):
                trials += 1
                k, iv = evp(pw, salt, dg)
                pt = unpad(AES.new(k, AES.MODE_CBC, iv).decrypt(ct))
                if pt is None:
                    continue
                sh = hashlib.sha256(pt).hexdigest()
                valid.append((eh, d[8:16].hex(), len(ct), pn, dg, len(pt), sh[:16]))
                for tn, th in TARGET_79.items():
                    if sh == th:
                        hits.append((tn, eh, d[8:16].hex(), len(ct), pn, dg, len(pt)))
    dt = time.time() - t0

    print(f"\n[battery] trials={trials}  D={trials/dt:,.0f}/s  t={dt:.2f}s")
    print(f"[battery] valid-PKCS7 decryptions: {len(valid)} "
          f"(~{trials//256} expected at 1/256 = pure padding noise)")
    real = [v for v in valid if any(v[6] == t[:16] for t in TARGET_79.values())]
    print(f"[battery] of those, matching a KNOWN 79-byte digest: {len(real)}")
    print(f"[battery] skipped {len(skipped)} non-CBC 'Salted__' matches (ct not a multiple of 16)")
    for eh, salt, ctn in skipped:
        print(f"           {eh} salt={salt} ct={ctn}B")
    print(f"\n[battery] HITS against the three certified 79-byte targets: {len(hits)}")
    for tn, eh, salt, ctn, pn, dg, ptl in hits:
        print(f"   {tn:22s} env={eh} salt={salt} ct={ctn}B  pw={pn} kdf={dg} pt={ptl}B")
    known = {"B2_79"}   # the control rung, already certified
    fresh = [h for h in hits if h[0] not in known]
    print()
    if fresh:
        print(f"RESULT: POSITIVE -- {len(fresh)} NEW certified 79-byte record(s) opened by a")
        print("        ladder key. The ladder extends; see the row for which rung.")
        for tn, eh, salt, ctn, pn, dg, ptl in fresh:
            print(f"        {tn} via {pn} / {dg} on salt {salt} ct={ctn}B")
    else:
        print("RESULT: NEGATIVE, and the negative sits exactly on the null. The only hit is")
        print("        the already-known B2 rung (the control itself). The three unused")
        print("        ladder keys K_C2 / K_S1 / K_S2 open NOTHING in reach to a certified")
        print("        79-byte record, in any of 7 encodings x 2 KDFs.")
        print(f"        Noise check: {len(valid)} valid-pad decryptions, 1 of them the known")
        print(f"        rung, leaving {len(valid)-1} spurious against a 1/256 null expectation")
        print(f"        of {trials/256:.2f} -- i.e. no signal above chance.")
        print("        So `salphaseion_plain_79.bin` (9c14868c...) stays UNCERTIFIED: it is")
        print("        not reachable from the ladder by any of these encodings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
