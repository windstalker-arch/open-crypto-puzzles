#!/usr/bin/env python3
"""Re-verify the whole certified GSMG ladder from first principles.

Why this exists: the ladder is recorded as facts in the ledger, but a ladder is
only worth as much as its weakest link, and a long chain of recorded values can
drift from the artifacts it claims to describe. This re-derives the entire chain
from two inputs -- canonical BLOB1 and RAW_PW -- and checks it against the
on-disk plaintexts, the recorded hashes, and the two funded gates.

The point is INDEPENDENCE. blob_inventory.py's evp()/dec() are used as a
cross-check, but the primary implementation here is written separately, so a bug
shared between the ledger and its original tool cannot hide. (Same lesson as
R-DIG149: assert against the artifact, never against a value typed by hand.)

Chain under test, all of it downstream of BLOB1 + RAW_PW:

    BLOB1 --RAW_PW/evp-md5--> B1_79  (79 B)
    B1_79[:32]  = K_C1        WIF(K_C1, uncompressed) is the BLOB2 password
    B1_79[32:64]= K_C2        BLOB1's K_C1 WIF re-encrypts B1_79 -> BLOB1
    B1_79[64:79]= E_C
    BLOB2 --WIF(K_C1)/md5--> B2_79  (79 B)
    B2_79[:32]  = K_S1        B2_79[:32] WIF re-encrypts B2_79 -> BLOB2
    B2_79[32:64]= K_S2
    B2_79[64:79]= E_S
    CHAIN4_PW = E_C || E_S || 59cc

Run:  python3 tools/verify_ladder.py
Exit 0 only if every check passes.
"""
import base64
import hashlib
import os
import re
import sys
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import RIPEMD160

FOLDER = Path(__file__).resolve().parent.parent
P = str(FOLDER)

# --- the two inputs. BLOB1 is the canonical 128-char base64 of the 96-byte
# --- envelope; RAW_PW is the published authorial password.
BLOB1 = ("U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z"
         "QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ")
RAW_PW = b"matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist"
DUALITE_XORKEY = bytes.fromhex(
    "a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735")

GATE1 = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
GATE1_H160 = "a9553269572a317e39f0f518cb87c1a0ee1dbae4"
GATE2 = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"

REC = {
    "B1_79": "1449a2178eea7c0e3fabac8c1ad2afa294be4fc1800c594a025a056e88c626bf",
    "B2_79": "b40fce72ef5638e4f79b3233e653f8a5dbdb0d4ae2009d2d3da2c98b70f4d004",
    "K_C1": "9fa9db91a9dee0e38b93694ec874630b30f32f33671987543b1cf913f4746439",
    "K_C2": "1517389608d55021dc436b66ec513a617c4f14cb0fed4708b535641a6dfe8210",
    "K_S1": "b06fa6f20561756c865dac7190f063480a371e4a13206e529ee7e9078f309c4b",
    "K_S2": "b11d211ca0a17cd68c580308f3e6f21d3f935c8da3c4373b6f73ab5ccfaea597",
    "E_C": "38d4f4c90cb45fdfc8cff50d0ed1c5",
    "E_S": "740a25de4b8e946d0a5ae2667a23a2",
    "ADDR_C1": "1GKJzHQkgTBwwEGeXetsTMDoUzvwzs9yb4",
    "ADDR_C2": "135Cf6ASyU2PDHuxA1Edc3mHYtxEsZNPCa",
    "ADDR_S1": "1MixpoELBvfkFSRUQtDCGXbdG53cjqknZT",
    "ADDR_S2": "176ysPe7FdevdQjZWaFCK2nnVbzX9Tgydy",
}

# envelope -> (salt, canonical ciphertext length, label)
ENV = {
    "BLOB1": ("3ab585348552415d", 80, "BLOB1"),
    "BLOB2": ("b45a5e3d827593ca", 80, "BLOB2"),
    "cc_1327": ("2d3f6fe06dc950e6", 1328, "cc_1327"),
    "causality": ("06286612d43ed7ed", 656, "causality"),
}

fails = []
npass = 0


def ck(name, cond, detail=""):
    global npass
    if cond:
        npass += 1
        print("  PASS  %-34s %s" % (name, detail))
    else:
        fails.append(name)
        print("  FAIL  %-34s %s" % (name, detail))
        if isinstance(detail, str) and len(detail) > 8:
            print("        ^ repr: %r" % (detail,))


# ---------------------------------------------------------------- EVP_BytesToKey
def evp(pw, salt, dg):
    """Independent implementation of OpenSSL's EVP_BytesToKey with MD5/SHA-256.

    D_1 = H(P || S); D_i = H(D_{i-1} || P || S); key||iv = first 48 bytes.
    """
    h = getattr(hashlib, dg)
    d, prev = b"", b""
    while len(d) < 48:
        prev = h(prev + pw + salt).digest()
        d += prev
    return d[:32], d[32:48]


def unpad(pt):
    n = pt[-1]
    if not 0 < n <= 16 or pt[-n:] != bytes([n]) * n:
        return None
    return pt[:-n]


def dec(raw, pw, dg):
    if (len(raw) - 16) % 16:
        return None
    k, iv = evp(pw, raw[8:16], dg)
    return unpad(AES.new(k, AES.MODE_CBC, iv).decrypt(raw[16:]))


def enc(pt, pw, salt, dg):
    """Re-encrypt with PKCS7 padding. EVP derives the IV, so this is exact:
    a correct round-trip can only reproduce the original ciphertext."""
    n = 16 - (len(pt) % 16)
    k, iv = evp(pw, salt, dg)
    return b"Salted__" + salt + AES.new(k, AES.MODE_CBC, iv).encrypt(pt + bytes([n]) * n)


# ---------------------------------------------------------------- secp256k1
SECP_P = 2 ** 256 - 2 ** 32 - 977
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)


def padd(p, q):
    if p is None:
        return q
    if q is None:
        return p
    if p[0] == q[0] and (p[1] + q[1]) % SECP_P == 0:
        return None
    if p == q:
        lam = 3 * p[0] * p[0] * pow(2 * p[1], SECP_P - 2, SECP_P) % SECP_P
    else:
        lam = (q[1] - p[1]) * pow(q[0] - p[0], SECP_P - 2, SECP_P) % SECP_P
    x = (lam * lam - p[0] - q[0]) % SECP_P
    return x, (lam * (p[0] - x) - p[1]) % SECP_P


def pmul(k, p=G):
    r = None
    while k:
        if k & 1:
            r = padd(r, p)
        p = padd(p, p)
        k >>= 1
    return r


B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58enc(raw):
    n, o = int.from_bytes(raw, "big"), ""
    while n:
        n, r = divmod(n, 58)
        o = B58[r] + o
    return "1" * (len(raw) - len(raw.lstrip(b"\x00"))) + (o or "K")


def b58check(payload):
    chk = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    return b58enc(payload + chk)


def b58dec(s):
    n = 0
    for c in s:
        n = n * 58 + B58.index(c)
    b = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return b"\x00" * (len(s) - len(s.lstrip("1"))) + b


def wif(k32, compressed=False):
    p = b"\x80" + k32 + (b"\x01" if compressed else b"")
    return b58check(p)


def addr(k32, compressed=False):
    x, y = pmul(int.from_bytes(k32, "big") % SECP_N)
    pub = (bytes([2 + (y & 1)]) + x.to_bytes(32, "big")) if compressed else \
        b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")
    h = RIPEMD160.new(hashlib.sha256(pub).digest()).digest()
    return b58check(b"\x00" + h)


# ---------------------------------------------------------------- find envelopes
def find_envelopes():
    """Collect the canonical envelope for each salt of interest.

    Selection rule, and it is strict on purpose: a candidate counts only if its
    ciphertext length is EXACTLY the canonical length AND 16-aligned. The corpus
    also holds misaligned near-misses for these salts (e.g. 1349 and 1367-byte
    runs for salt 2d3f6fe0, which are text-level artefacts where the base64 run
    starts mid-blob), and trimming one of those to length yields bytes that are
    offset from the real ciphertext -- it looks plausible and silently fails to
    decrypt. So: no trimming, no guessing. Exact length or nothing.
    """
    roots = [os.path.expanduser("~/briefcase"), os.path.expanduser("~/gsmg"),
             "/storage/emulated/0/Download/Telegram", P + "/data", P + "/analysis",
             P + "/evidence", P + "/tools"]
    rx = re.compile(rb"U2FsdGVkX1[A-Za-z0-9+/=\s\\\"']{20,}")
    want = {v[0]: v[1] for v in ENV.values()}
    hits = {}
    for r in roots:
        if not os.path.isdir(r):
            continue
        for dp, dn, fn in os.walk(r):
            if ".git" in dp:
                continue
            for f in fn:
                p = os.path.join(dp, f)
                try:
                    if os.path.getsize(p) > 40_000_000:
                        continue
                    b = open(p, "rb").read()
                except Exception:
                    continue
                for m in rx.finditer(b):
                    t = re.sub(rb"[^A-Za-z0-9+/=]", b"", m.group(0))
                    try:
                        raw = base64.b64decode(t)
                    except Exception:
                        continue
                    if not raw.startswith(b"Salted__") or len(raw) < 24:
                        continue
                    s = raw[8:16].hex()
                    if s in want and len(raw) - 16 == want[s] and s not in hits:
                        hits[s] = (raw, p)
    out = {}
    for label, (salt, ctlen, _nm) in ENV.items():
        if salt in hits:
            out[label] = hits[salt]
    return out


def main():
    print("=" * 78)
    print("GSMG LADDER VERIFICATION - independent re-derivation from BLOB1 + RAW_PW")
    print("=" * 78)

    # --- 0. cross-check my EVP against the tool's, so neither can be wrong alone
    sys.path.insert(0, P + "/tools")
    import blob_inventory as bi
    for dg in ("md5", "sha256"):
        ck("evp cross-check vs blob_inventory (%s)" % dg,
           evp(RAW_PW, b"\x01" * 8, dg) == bi.evp(RAW_PW, b"\x01" * 8, dg))

    envs = find_envelopes()
    for label in ENV:
        ck("envelope located: %s" % label, label in envs,
           envs[label][1] if label in envs else "not found in corpus")

    # --- 1. BLOB1 -> B1_79
    print("\n[1] BLOB1 --RAW_PW/evp-md5--> B1_79")
    b1raw = base64.b64decode(BLOB1)
    ck("BLOB1 is Salted__ + salt + 80B ct", len(b1raw) == 96 and (len(b1raw) - 16) % 16 == 0,
       "%d B, salt %s" % (len(b1raw), b1raw[8:16].hex()))
    B1 = dec(b1raw, RAW_PW, "md5")
    ck("B1_79 decrypts (PKCS7 valid)", B1 is not None and len(B1) == 79,
       "%d B" % (len(B1) if B1 else -1))
    if B1 is None:
        return 1
    ck("sha256(B1_79) == recorded", hashlib.sha256(B1).hexdigest() == REC["B1_79"],
       hashlib.sha256(B1).hexdigest()[:16])
    disk = (FOLDER / "data/B1_79.bin").read_bytes()
    ck("B1_79 == data/B1_79.bin on disk", B1 == disk, "%d B" % len(disk))
    ck("BLOB1 re-encrypts from B1_79", enc(B1, RAW_PW, b1raw[8:16], "md5") == b1raw,
       "round-trip exact")

    # --- 2. ladder keys from B1_79
    print("\n[2] ladder keys cut from B1_79")
    K_C1, K_C2, E_C = B1[:32], B1[32:64], B1[64:79]
    ck("K_C1 == recorded", K_C1.hex() == REC["K_C1"], K_C1.hex()[:16])
    ck("K_C2 == recorded", K_C2.hex() == REC["K_C2"], K_C2.hex()[:16])
    ck("E_C  == recorded", E_C.hex() == REC["E_C"], E_C.hex()[:16])

    # --- 3. addresses, and the gate comparison
    print("\n[3] secp256k1 -> P2PKH addresses, vs both funded gates")
    for nm, k, want in (("K_C1", K_C1, REC["ADDR_C1"]), ("K_C2", K_C2, REC["ADDR_C2"])):
        a = addr(k)
        ck("addr(%s) == recorded" % nm, a == want, a)
        ck("addr(%s) != either gate" % nm, a not in (GATE1, GATE2))

    # --- 4. BLOB2 opens with WIF(K_C1): the loop closes on itself
    print("\n[4] BLOB2 --WIF(K_C1)/evp-md5--> B2_79")
    pw2 = wif(K_C1).encode()
    ck("WIF(K_C1) is the recorded B2 password",
       pw2 == b"5K2byJMssxFKuTgnk9YQjpBz5FhkwwF2LaZoAyTus8HjGEpz8AT", pw2[:16].decode() + "...")
    b2raw = envs["BLOB2"][0] if "BLOB2" in envs else None
    if b2raw is None:
        ck("BLOB2 available", False)
        return 1
    B2 = dec(b2raw, pw2, "md5")
    ck("B2_79 decrypts (PKCS7 valid)", B2 is not None and len(B2) == 79,
       "%d B" % (len(B2) if B2 else -1))
    if B2 is None:
        return 1
    ck("sha256(B2_79) == recorded", hashlib.sha256(B2).hexdigest() == REC["B2_79"],
       hashlib.sha256(B2).hexdigest()[:16])
    disk2 = (FOLDER / "data/B2_79.bin").read_bytes()
    ck("B2_79 == data/B2_79.bin on disk", B2 == disk2, "%d B" % len(disk2))
    ck("BLOB2 re-encrypts from B2_79", enc(B2, pw2, b2raw[8:16], "md5") == b2raw,
       "round-trip exact")

    K_S1, K_S2, E_S = B2[:32], B2[32:64], B2[64:79]
    ck("K_S1 == recorded", K_S1.hex() == REC["K_S1"], K_S1.hex()[:16])
    ck("K_S2 == recorded", K_S2.hex() == REC["K_S2"], K_S2.hex()[:16])
    ck("E_S  == recorded", E_S.hex() == REC["E_S"], E_S.hex()[:16])
    for nm, k, want in (("K_S1", K_S1, REC["ADDR_S1"]), ("K_S2", K_S2, REC["ADDR_S2"])):
        a = addr(k)
        ck("addr(%s) == recorded" % nm, a == want, a)
        ck("addr(%s) != either gate" % nm, a not in (GATE1, GATE2))

    # --- 5. CHAIN4_PW
    print("\n[5] CHAIN4_PW = E_C || E_S || 59cc")
    c4 = E_C + E_S + b"\x59\xcc"
    ck("CHAIN4_PW length == 15+15+2", len(c4) == 32, "%d B" % len(c4))
    ck("CHAIN4_PW hex", c4.hex() == REC["E_C"] + REC["E_S"] + "59cc", c4.hex()[:32] + "...")

    # --- 6. the other two opened envelopes
    print("\n[6] cc_1327 and causality")
    if "cc_1327" in envs:
        cc = dec(envs["cc_1327"][0], DUALITE_XORKEY, "md5")
        ck("cc_1327 decrypts", cc is not None and len(cc) == 1327,
           "%d B, sha %s" % (len(cc) if cc else -1,
                             hashlib.sha256(cc).hexdigest()[:16] if cc else "-"))
        if cc:
            ck("cc plaintext sha starts 4f7a1e4e",
               hashlib.sha256(cc).hexdigest().startswith("4f7a1e4e"),
               hashlib.sha256(cc).hexdigest()[:16])
            ccd = os.path.expanduser("~/gsmg/cosmic_decrypted.bin")
            if os.path.exists(ccd):
                ck("cc_1327 == ~/gsmg/cosmic_decrypted.bin on disk",
                   cc == open(ccd, "rb").read(), "%d B" % len(cc))
            ck("cc re-encrypts from its plaintext",
               enc(cc, DUALITE_XORKEY, envs["cc_1327"][0][8:16], "md5") == envs["cc_1327"][0],
               "round-trip exact")
    if "causality" in envs:
        pw = hashlib.sha256(b"causality").hexdigest().encode()
        cz = dec(envs["causality"][0], pw, "sha256")
        pr = (sum(1 for b in cz if chr(b).isprintable() or b in (9, 10, 13)) / len(cz)) if cz else 0
        ck("causality decrypts (evp-sha256)", cz is not None and len(cz) == 648,
           "%d B, %.0f%% printable, sha %s" % (len(cz) if cz else -1, 100 * pr,
                                               hashlib.sha256(cz).hexdigest()[:16] if cz else "-"))
        if cz:
            ck("causality sha starts e2f9dd65",
               hashlib.sha256(cz).hexdigest().startswith("e2f9dd65"),
               hashlib.sha256(cz).hexdigest()[:16])
            ck("causality is printable-or-whitespace throughout", pr == 1.0,
               "%.0f%% (CRLF endings count as text)" % (100 * pr))
            ck("causality re-encrypts from its plaintext",
               enc(cz, hashlib.sha256(b"causality").hexdigest().encode(),
                   envs["causality"][0][8:16], "sha256") == envs["causality"][0],
               "round-trip exact")

    # --- 7. the gate itself
    print("\n[7] funded gate")
    h = b58dec(GATE1)[1:21]
    ck("GATE1 base58 -> hash160 == recorded", h.hex() == GATE1_H160, h.hex())

    print("\n" + "=" * 78)
    print("passed %d / %d" % (npass, npass + len(fails)))
    if fails:
        print("FAILURES: %s" % ", ".join(fails))
        return 1
    print("LADDER VERIFIED. Neither funded gate is open; no key recovered.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
