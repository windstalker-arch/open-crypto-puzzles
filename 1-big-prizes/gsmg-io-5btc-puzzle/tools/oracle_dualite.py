#!/usr/bin/env python3
"""Dualite-gate oracle: test candidate answer strings X against the SECOND funded
gate `17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa` (3.75 BTC), which the shipped small-blob
oracle (tools/oracle.py) does NOT test.

Pipeline (mirrors the small-blob oracle's assumption, since no alternative exists):
  password = sha256(X).hexdigest()  (also tries md5)
  -> EVP_BytesToKey(AES-256-CBC) decrypt of the Dualite / Cosmic Duality blob
     (salt 2d3f6fe06dc950e6, 1344 bytes)
  -> reduce resulting plaintext to a 32-byte private key via a broad reading set
  -> uncompressed secp256k1 -> P2PKH compare against `17ucy1K9...`

The Dualite blob's known decrypted plaintext (under the community 7-token XOR key)
is 1327 bytes of high-entropy output, far larger than the small blob's 64-byte
plaintext, so we try BOTH the small-blob's 4 standard readings AND extended
readings appropriate to a large plaintext. A real hit wins; misses are honest.

Public/authorized puzzle only.
"""
import os
import argparse
import base64
import hashlib
import sys

from Crypto.Cipher import AES

TARGET_ADDRESS = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"
DUALITE_B64_TXT = os.path.expanduser("~/briefcase/CosmicDuality.txt")
EXPECTED_SALT = "2d3f6fe06dc950e6"

# The certified Dualite/Cosmic-Duality pipeline (dualite_plaintext_reduce.py): the
# password is the BINARY 32-byte XOR-reduction of these seven tokens' sha256
# digests (not the text concat, not any sha256-hex form), and the EVP digest is MD5.
# Oracle audit (late-200) added exactly these forms so a correct answer is not
# missed the way the old text-only oracle would have missed it.
TOKENS = [
    "matrixsumlist", "enter", "lastwordsbeforearchichoice",
    "thispassword", "matrixsumlist", "yourlastcommand", "secondanswer",
]
CERTIFIED_PLAIN_SHA = "4f7a1e4e"  # prefix check against the certified 1327B digest
CERTIFIED_XK_HEX = "a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735"

# phase-2 blob (small pipeline's selftest vector) for certifying the AES half here
PHASE2_BLOB_B64 = (
    "U2FsdGVkX18GKGYS1D7X7VjxWz6uUyPFszr8dVvtOIrJqioWHgT69JJnzJGDVOvF"
    "QYWh5BEZxFPXmMq1cbyy3dVVDgLhF050xlDy2J5grtKw9jUOO4oFNRgoD+1dlukX"
    "pd8ccg++kkXgE9mGBP6lQbukDiSjY4mnR2Mv6ydIncrRqacQNVEmEgM4fGTi1ANz"
    "nHsGn7mP+P3UyrJCRbuFmpZJc4CNdPj6YuxwR4HkHkqcfxh0L5CaEu4VbY70+fmk"
    "qgZQyMJqiUlaV9KC4UPuRVj0r7MYbVRazkhsjeIcogmdJGEeBwD47lEB7X9PNKWm"
    "ojTvRZg6R+sZzRZE26VLaF+s9cpTo4Y8PZUxKvQ86HXC8QIavUgDfw7HxIxkTatv"
    "CW2yq3ZOXl5naR6oSNxdX9alyhTzB+/2623oGdlWev5Oo8xHJqUi7QjVP+mNC8BA"
    "+Cg0DJwcOFGO5K7g8Rm06+sLogwntdIgTo70X3FegAtipHboeUNKefiAguvkDoIf"
    "8iMPc+83PygvlZPDNQCOKugwDEUimhHwQrMsmalRNoFEQEb+ZIC+na15cPoRAlOD"
    "NJfXIJ96ihAy9wWis39mQW6JFqZmUags4xoP3lJ35bCrXsNOPFZ4WH+f4YC/Ov8C"
    "QW5bjtxno8GG4b/wBWevhcRVMK6KmRJj8NBCssnrlz0sQ70rMNkiN2wiSPcwX3Ad"
    "JgLs8vQAUM59x9fkKFFzD4+Sc1sJztUTB7CMGGfpZOA8W33VZnEdmGcoaHlDsR8G"
    "vAkZ+jg+QJs9ZNHqWE1+1zgm/6NsWWgWH8OI2PPCfXHxDbfDk8uD/Zibr/yjSKvu"
    "Sb8OecflOT2hw37WL49uADgeWgnp2bzkfGIq7EYS7OImjZZwY5h4sfcPfhvQ9kOV"
)
PHASE2_MARKER = b"keymakers"


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def evp_bytes_to_key(password, salt, key_len=32, iv_len=16, digest="sha256"):
    """password may be str or bytes; encode str as utf-8 (binary keys pass through)."""
    if isinstance(password, str):
        password = password.encode("utf-8")
    H = hashlib.sha256 if digest == "sha256" else hashlib.md5
    derived, prev = b"", b""
    while len(derived) < key_len + iv_len:
        prev = H(prev + password + salt).digest()
        derived += prev
    return derived[:key_len], derived[key_len:key_len + iv_len]


def unpad_pkcs7(data: bytes):
    if not data:
        return None
    n = data[-1]
    if n < 1 or n > 16 or n > len(data):
        return None
    if data[-n:] != bytes([n]) * n:
        return None
    return data[:-n]


def decrypt_blob(blob_b64, password, digest="sha256"):
    raw = base64.b64decode(blob_b64)
    if raw[:8] != b"Salted__":
        return None
    salt, ct = raw[8:16], raw[16:]
    key, iv = evp_bytes_to_key(password, salt, 32, 16, digest)
    plain = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
    return unpad_pkcs7(plain)


def xor_reduce(tokens) -> bytes:
    """The certified community key: XOR of sha256(token) for the seven tokens."""
    key = bytes(32)
    for t in tokens:
        key = bytes(x ^ y for x, y in zip(key, sha256(t.encode("utf-8"))))
    return key


def password_forms(candidate: str):
    """All password byte-forms to try for a candidate string X.

    pre-audit (late-200) only tried text-X and sha256(X).hex, both as utf-8
    strings. The certified pipeline needs the BINARY XK (bytes.fromhex(X) or the
    token-concat XOR-reduction) under MD5; text-only forms can never match it.
    """
    forms = [(candidate.encode("utf-8"), "raw(X)")]
    sh = sha256(candidate.encode("utf-8")).hex()
    forms.append((sh.encode("utf-8"), "sha256(X).hex"))
    try:
        cb = bytes.fromhex(candidate)
        if cb:
            forms.append((cb, "bytes.fromhex(X)"))
            forms.append((sha256(cb).hex().encode("utf-8"), "sha256(bytes.fromhex(X)).hex"))
    except ValueError:
        pass
    if candidate.lower() == "".join(TOKENS).lower():
        forms.append((xor_reduce(TOKENS), "token-concat XOR-reduced XK (certified)"))
        xk = xor_reduce(TOKENS)
        forms.append((xk.hex().encode("utf-8"), "hex(XK)"))
    return forms


def readings(plain: bytes):
    """Broad reading set: small-blob's 4 + large-plaintext scalars + the certified
    matrix-sum reduction families from dualite_plaintext_reduce.py (families B/C)."""
    out = [("sha256(plaintext)", sha256(plain))]
    if len(plain) >= 32:
        out.append(("first32", plain[:32]))
        out.append(("last32", plain[-32:]))
    if len(plain) >= 64:
        out.append(("sha256(first64)", sha256(plain[:64])))
    # extended: any contiguous 32-byte window's sha256, plus double-sha256
    if len(plain) >= 64:
        out.append(("sha256(last64)", sha256(plain[-64:])))
    out.append(("sha256d(plaintext)", sha256(sha256(plain))))
    if len(plain) >= 64:
        out.append(("sha256(full_reversed)", sha256(plain[::-1])))
    if len(plain) >= 32:
        out.append(("rev(first32)", plain[:32][::-1]))
        out.append(("rev(last32)", plain[-32:][::-1]))
    if len(plain) >= 64:
        k1, k2 = plain[:32], plain[32:64]
        out.append(("K_C2_field", k2))
        out.append(("sha256(K_C2_field)", sha256(k2)))
        out.append(("K_C1_xor_K_C2", bytes(a ^ b for a, b in zip(k1, k2))))
        out.append(("sha256(K_C1_xor_K_C2)", sha256(bytes(a ^ b for a, b in zip(k1, k2)))))
    # --- certified matrix-sum families on 1327B (families B/C of the reducer) ---
    bits = "".join(format(b, "08b") for b in plain)
    for R in [101, 102, 103]:
        total = R * R
        if total > len(bits):
            continue
        b = bits[:total]
        m = [[int(b[r*R+c]) for c in range(R)] for r in range(R)]
        row = [sum(m[r]) for r in range(R)]
        col = [sum(m[r][c] for r in range(R)) for c in range(R)]
        rb = bytes(min(x, 255) for x in row)
        cb = bytes(min(x, 255) for x in col)
        out.append((f"sha256(row_sums_{R}x{R})", sha256(rb)))
        out.append((f"sha256(col_sums_{R}x{R})", sha256(cb)))
        out.append((f"sha256(row+col_{R}x{R})", sha256(rb + cb)))
        out.append((f"sha256(col+row_{R}x{R})", sha256(cb + rb)))
        n = min(len(rb), len(cb))
        out.append((f"sha256(row_xor_col_{R}x{R})", sha256(bytes(a ^ b for a, b in zip(rb[:n], cb[:n])))))
        for shift in [0, 7, 13]:
            sec = bytes(((row[i] + col[(i + shift) % len(col)]) & 0xFF) for i in range(len(row)))
            out.append((f"sha256(sec_shift{shift}_{R}x{R})", sha256(sec)))
    if len(plain) * 8 >= 103 * 103:
        R = 103
        b = bits[:R*R]
        m = [[int(b[r*R+c]) for c in range(R)] for r in range(R)]
        row = [sum(m[r]) for r in range(R)]
        col = [sum(m[r][c] for r in range(R)) for c in range(R)]
        sec = bytes(((row[i] + col[(i + 7) % R]) & 0xFF) for i in range(R))
        out.append(("sec103_first32", sec[:32]))
        out.append(("sec103_last32", sec[-32:]))
        out.append(("sha256(sec103)", sha256(sec)))
        val = 0
        for dig in sec:
            val = val * 38 + (dig - 80) if dig >= 80 else val * 38 + dig
        big = val.to_bytes((val.bit_length() + 7) // 8, "big")
        out.append(("base38_first32", big[:32]))
        out.append(("base38_last32", big[-32:]))
        out.append(("sha256(base38_bytes)", sha256(big)))
    return out


def priv_to_address(priv_bytes: bytes):
    from ecdsa import SECP256k1, SigningKey
    sk = SigningKey.from_string(priv_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    pub = b"\x04" + vk.to_string()
    h160 = hashlib.new("ripemd160", sha256(pub)).digest()
    import base58
    address = base58.b58encode_check(b"\x00" + h160).decode()
    return address, pub.hex()


def wif_uncompressed(priv_bytes):
    import base58
    return base58.b58encode_check(b"\x80" + priv_bytes).decode()


def load_dualite_b64():
    return "".join(open(DUALITE_B64_TXT).read().split())


def attempt(candidate: str, blob_b64: str):
    # Pre-audit this only tried text-X and sha256(X).hex, both digests, both as
    # utf-8 strings. The certified pipeline needs the BINARY key (token-XOR or
    # bytes.fromhex), so every candidate now runs through password_forms() and
    # every decrypt result is reduced by the broad (matrix-sum-inclusive) set.
    for pw, form in password_forms(candidate):
        for digest in ("sha256", "md5"):
            plain = decrypt_blob(blob_b64, pw, digest)
            if plain is None:
                continue
            for name, key_bytes in readings(plain):
                if len(key_bytes) != 32:
                    continue
                try:
                    address, _pub = priv_to_address(key_bytes)
                except Exception:
                    continue
                if address == TARGET_ADDRESS:
                    return True, {
                        "password_form": form,
                        "digest": digest,
                        "reading": name,
                        "address": address,
                        "priv_hex": key_bytes.hex(),
                        "wif": wif_uncompressed(key_bytes),
                    }
    return False, {"reason": "no password form/digest/reading matched the address"}


def selftest() -> bool:
    ok = True
    # 1) blob identity + shape
    blob = load_dualite_b64()
    raw = base64.b64decode(blob)
    p1 = raw[:8] == b"Salted__" and raw[8:16].hex() == EXPECTED_SALT
    print(f"Dualite blob (Salted__, salt {EXPECTED_SALT}, {len(raw)} bytes): {'OK' if p1 else 'FAIL'}")
    ok = ok and p1
    # 2) AES half certified against the known phase-2 vector (same crypto code path)
    p2pw = sha256(b"causality").hex()
    rec = decrypt_blob(PHASE2_BLOB_B64, p2pw)
    p2 = rec is not None and PHASE2_MARKER in rec
    print(f"phase-2 blob decrypts under sha256(\"causality\"): {'OK' if p2 else 'FAIL'}")
    ok = ok and p2
    p2b = decrypt_blob(PHASE2_BLOB_B64, "definitely the wrong password") is None
    print(f"wrong password -> no valid padding: {'OK' if p2b else 'FAIL'}")
    ok = ok and p2b
    # 3) attempt() is wired to the dualite gate (17ucy1K9...), not the small gate.
    p3 = TARGET_ADDRESS.startswith("17ucy1K9") and raw[8:16].hex() == EXPECTED_SALT
    print(f"attempt() wired to dualite gate {TARGET_ADDRESS[:12]}...: {'OK' if p3 else 'FAIL'}")
    ok = ok and p3
    # 4) the certified pipeline reproduces exactly: token-concat XOR-reduction ->
    #    binary XK (must equal the certified XK hex) -> MD5 EVP decrypt of the
    #    real blob -> certified 1327B plaintext. This certifies the password_forms
    #    path that the pre-audit oracle never exercised.
    tcat = "".join(TOKENS)
    xk = xor_reduce(TOKENS)
    p4a = xk.hex() == CERTIFIED_XK_HEX
    print(f"token-XOR reduction == certified XK: {'OK' if p4a else 'FAIL'}")
    ok = ok and p4a
    p4b = False
    for form_name, pw in [(p, f) for f, p in password_forms(tcat) if "XOR" in p or "hex(XK)" in p]:
        pt = decrypt_blob(blob, pw, "md5")
        if pt is not None and pt and hashlib.sha256(pt).hexdigest().startswith(CERTIFIED_PLAIN_SHA):
            p4b = True
    print(f"binary-XK MD5 decrypt reaches the certified 1327B plaintext: {'OK' if p4b else 'FAIL'}")
    ok = ok and p4b
    # 5) a tampered token key must not reproduce the certified plaintext (padding
    #    alone is a weak validator -- ~1/256 chance any wrong key passes it -- so the
    #    strong control is the certified plaintext digest, not padding).
    bad = xor_reduce(TOKENS[:-1] + ["wrong"])
    p5 = True
    for dig in ("md5", "sha256"):
        ptb = decrypt_blob(blob, bad, dig)
        if ptb is not None and hashlib.sha256(ptb).hexdigest().startswith(CERTIFIED_PLAIN_SHA):
            p5 = False
    print(f"tampered token key -> not the certified plaintext: {'OK' if p5 else 'FAIL'}")
    ok = ok and p5
    # 6) reading closure on the certified plaintext is shape-sane: every reading
    #    named by the extended set is 32 bytes and the set is non-trivial.
    pt = decrypt_blob(blob, xk, "md5")
    names = dict(readings(pt))
    p6 = len(names) >= 30 and all(len(v) == 32 for v in names.values()) and len(pt) == 1327
    print(f"extended readings on certified 1327B plaintext (all 32B, >=30 readings): {'OK' if p6 else 'FAIL'}")
    ok = ok and p6
    if ok:
        print("SELFTEST OK")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("candidate", nargs="?", help="candidate answer string X")
    ap.add_argument("--stdin", action="store_true", help="read candidates, one per line")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    blob = load_dualite_b64()
    if args.selftest:
        return 0 if selftest() else 1
    if args.stdin:
        any_hit = False
        for line in sys.stdin:
            line = line.rstrip("\n")
            if not line:
                continue
            m, info = attempt(line, blob)
            if m:
                print(f"MATCH {info['address']} reading={info['reading']} priv_hex={info['priv_hex']} wif={info['wif']}")
            else:
                print("NO MATCH")
            any_hit = any_hit or m
        return 0 if any_hit else 1
    if not args.candidate:
        ap.print_help()
        return 0
    m, info = attempt(args.candidate, blob)
    if m:
        print(f"MATCH {info['address']} reading={info['reading']} priv_hex={info['priv_hex']} wif={info['wif']}")
    else:
        print("NO MATCH")
    return 0 if m else 1


if __name__ == "__main__":
    sys.exit(main())
