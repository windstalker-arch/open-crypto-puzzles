#!/usr/bin/env python3
"""Inventory every `Salted__` blob in the local GSMG corpus and classify it.

This answers, with a definite answer, the question the B2 rows left open as a
prediction ("is there a missing envelope nobody has captured?"). The answer is
no: the corpus holds six real encrypted blobs, five of which are open, plus one
that is documented as blocked.

Method note (the lesson from the B2 rung): the candidate passwords are DERIVED
values - WIFs of the ladder keys, h160s, field concatenations, and readings of
every artifact already decoded - plus the published authorial passwords we
actually hold. Authorial-string dictionaries are not the right space.

Classification, per 16-aligned blob:
  OPENED      decrypts to a plaintext we can name and cross-check
  PREFIX      its ciphertext is a byte-prefix of a longer blob with the same salt
              (a truncated copy in some transcript, not a distinct payload)
  DAMAGED     base64 transcription of a known blob with a few characters broken
  BLOCKED     no password in the set opens it (phase 3.2; see the ledger)
  FRAGMENT    ciphertext not 16-aligned: a text-level split, not a blob

Run:  python3 tools/blob_inventory.py
"""
import base64
import hashlib
import os
import re
import sys
from pathlib import Path

from Crypto.Cipher import AES

FOLDER = Path(__file__).resolve().parent.parent
P = str(FOLDER)

BLOB1 = ("U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z"
         "QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ")
RAW_PW = b"matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist"
PHASE5 = "4447f552c0f76528be4df75028a3ecdb3878bccd46acb4b3fabe6442304fd9c4"
DUALITE_XORKEY = bytes.fromhex(
    "a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735")

sys.path.insert(0, P + "/tools")


def sha256b(b):
    return hashlib.sha256(b).digest()


def evp(pw, salt, dg):
    h = getattr(hashlib, dg)
    d, prev = b"", b""
    while len(d) < 48:
        prev = h(prev + pw + salt).digest()
        d += prev
    return d[:32], d[32:48]


def dec(raw, pw, dg):
    if (len(raw) - 16) % 16:
        return None
    k, iv = evp(pw, raw[8:16], dg)
    pt = AES.new(k, AES.MODE_CBC, iv).decrypt(raw[16:])
    n = pt[-1]
    return pt[:-n] if 0 < n <= 16 and pt[-n:] == bytes([n]) * n else None


def b58enc(raw):
    A = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    n, o = int.from_bytes(raw, "big"), ""
    while n:
        n, r = divmod(n, 58)
        o = A[r] + o
    return "1" * (len(raw) - len(raw.lstrip(b"\x00"))) + (o or "K")


def wif(k32, comp=False):
    p = b"\x80" + k32 + (b"\x01" if comp else b"")
    return b58enc(p + sha256b(sha256b(p))[:4]).encode()


def passwords(B1, B2, extra):
    d = {"RAW_PW": RAW_PW,
         "XORKEY_dualite": DUALITE_XORKEY,
         "sha256(causality)_hex": sha256b(b"causality").hex().encode(),
         "PHASE5_hex_ascii": PHASE5.encode(),
         "PHASE5_hex_raw": bytes.fromhex(PHASE5),
         "B1": B1, "B2": B2}
    for nm, k in (("K_C1", B1[:32]), ("K_C2", B1[32:64]),
                  ("K_S1", B2[:32]), ("K_S2", B2[32:64]),
                  ("E_C", B1[64:79]), ("E_S", B2[64:79])):
        k = k.ljust(32, b"\x00")[:32]
        d["WIF_" + nm] = wif(k)
        d["WIFc_" + nm] = wif(k, True)
        d["hex_" + nm] = k.hex().encode()
        d["HEX_" + nm] = k.hex().upper().encode()
        d["raw_" + nm] = k
        d["sha_" + nm] = sha256b(k).hex().encode()
        d["sha_raw_" + nm] = sha256b(k)
    d["K_C1|K_C2"] = B1[:64]
    d["K_S1|K_S2"] = B2[:64]
    d["B1|B2"] = B1 + B2
    d["E_C|E_S"] = B1[64:79] + B2[64:79]
    d["E_S|E_C"] = B2[64:79] + B1[64:79]
    for nm, a in extra.items():
        if len(a) < 32:
            continue
        d["%s.raw" % nm] = a
        d["%s.shahex" % nm] = sha256b(a).hex().encode()
        d["%s.sharaw" % nm] = sha256b(a)
        d["%s.head32" % nm] = a[:32]
        d["%s.tail32" % nm] = a[-32:]
    return d


def b64_ndiff(a, b):
    n = max(len(a), len(b))
    a, b = a.ljust(n, "="), b.ljust(n, "=")
    return sum(1 for x, y in zip(a, b) if x != y)


def lcp(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return n


def split_presentation(tok, known_b64):
    """Is this run a known blob SPLIT across document lines rather than damaged?

    The run regex spans whitespace, so a blob printed as two base64 halves with
    prose between them comes back as one concatenated string. If some subset of
    the whitespace-separated pieces, kept in order, reproduces a known blob
    exactly, then the dropped pieces are document text and nothing was corrupted.
    Returns (label, dropped_pieces) or None.
    """
    pieces = [p for p in re.split(r"\s+", tok) if p]
    if not 2 <= len(pieces) <= 12:
        return None
    n = len(pieces)
    for mask in range(1, 1 << n):
        if bin(mask).count("1") < 2:
            continue
        cand = "".join(pieces[i] for i in range(n) if mask >> i & 1)
        for label, kb in known_b64:
            if cand == kb:
                dropped = [pieces[i] for i in range(n) if not (mask >> i & 1)]
                return label, dropped
    return None


def repair_note(raw, blob1, b1_b64, tok=None, known_b64=()):
    """How much of a damaged BLOB1 copy is byte-exact, and can it be repaired.

    Reports the intact byte prefix and whether every ciphertext byte survived.
    The trailing bytes past that prefix are transcription damage, not page text.
    """
    n = lcp(raw, blob1)
    ct_intact = raw[16:len(blob1)] == blob1[16:]
    bits = ("%d of %d B byte-exact" % (n, len(blob1)))
    if ct_intact:
        bits += "; every ciphertext byte intact, so the salt can be repaired " \
                "from the canonical copy and the blob recovered in full"
    else:
        bits += "; ciphertext damaged from byte %d on, so the copy is NOT " \
                "repairable" % max(n, 16)
    if len(raw) > len(blob1):
        bits += "; %d trailing B are transcription damage, not page text" % (
            len(raw) - len(blob1))
    if tok and known_b64:
        sp = split_presentation(tok, known_b64)
        if sp:
            label, dropped = sp
            bits += ("; NOT damage either: the base64 is printed as separate "
                     "document lines and whitespace-joining merged them - pieces "
                     "re-concatenate to %s exactly, and the line(s) between are "
                     "document text: %s" % (label, " | ".join(dropped)))
    return bits


def main():
    B1 = (FOLDER / "data/B1_79B.bin").read_bytes()
    B2 = (FOLDER / "data/B2_79B.bin").read_bytes()
    extra = {}
    for nm, p in (("cc_1327", os.path.expanduser("~/gsmg/cosmic_decrypted.bin")),
                  ("dualite_1344", P + "/data/cosmic_duality_blob_2020.bin")):
        if os.path.exists(p):
            extra[nm] = open(p, "rb").read()
    PW = passwords(B1, B2, extra)

    roots = [os.path.expanduser("~/briefcase"), os.path.expanduser("~/gsmg"),
             "/storage/emulated/0/Download/Telegram",
             P + "/data", P + "/analysis", P + "/evidence", P + "/tools"]
    B64RE = re.compile(rb"U2FsdGVkX1[A-Za-z0-9+/=\s\\\"']{20,}")
    env = {}
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
                for m in B64RE.finditer(b):
                    # keep the laid-out token too: decoding needs whitespace
                    # gone, but a blob printed as separate document lines can
                    # only be recognised as a split presentation while the
                    # line breaks are still visible
                    laid = m.group(0).replace(b"\\", b"").replace(b'"', b"").replace(b"'", b"")
                    tok = b"".join(laid.split())
                    try:
                        raw = base64.b64decode(tok[:len(tok) // 4 * 4] + b"=" * ((-len(tok)) % 4))
                    except Exception:
                        continue
                    if raw[:8] == b"Salted__" and len(raw) >= 24:
                        env.setdefault(raw, set()).add(
                            (p, tok.decode("ascii", "replace"),
                             laid.decode("ascii", "replace")))
    print("distinct Salted__ blobs: %d   passwords tried per blob: %d x 3 KDFs"
          % (len(env), len(PW)))

    KNOWN = {sha256b(B1).hex(): "B1_79 (79 B, the small half)",
             sha256b(B2).hex(): "B2_79 (79 B, CADEIA 2)"}
    for nm, a in extra.items():
        KNOWN.setdefault(sha256b(a).hex(), nm)
    # blobs the ledger already certifies as open, whose password is a long
    # authorial string we do not keep in the repo - named so this tool does not
    # report them as unexplained
    KNOWN_OPEN = {"9fbc451d13d071f4":
                  "phase 3, 4090 B - open per the phase 2->3 row; its 227-char "
                  "password is derived from the page, not stored here"}
    blob1 = base64.b64decode(BLOB1)
    # every aligned blob in the corpus, grouped by salt, longest first: this is
    # what lets a short copy be recognised as a truncation or an OCR mangling
    known_ct = {}
    for r in env:
        if (len(r) - 16) % 16 == 0:
            known_ct.setdefault(r[8:16], []).append((r[16:], r))
    for s_ in known_ct:
        known_ct[s_].sort(key=lambda t: -len(t[0]))
    known_ct[blob1[8:16]] = [(blob1[16:], blob1)] + known_ct.get(blob1[8:16], [])
    rows = []
    for raw, srcs in env.items():
        ct = len(raw) - 16
        where = sorted({p.replace(os.path.expanduser("~"), "~") for p, _t, _l in srcs})
        tok, laid = sorted(srcs)[0][1], sorted(srcs)[0][2]
        if ct % 16:
            rows.append((raw[8:16].hex(), ct, "FRAGMENT", "ct not 16-aligned", where))
            continue
        ident, text_open = None, None
        for dg in ("sha256", "md5", "sha1"):
            for pn, pw in PW.items():
                pt = dec(raw, pw, dg)
                if pt is None:
                    continue
                pr = sum(32 <= c < 127 or c in (9, 10, 13) for c in pt) / max(1, len(pt))
                if ident is None and sha256b(pt).hex() in KNOWN:
                    ident = KNOWN[sha256b(pt).hex()]
                    ident += "  <-- %s / EVP-%s" % (pn, dg)
                if text_open is None and pr > 0.85:
                    text_open = ("%d B, %s / EVP-%s, %.0f%% printable, sha256 %s"
                                 % (len(pt), pn, dg, pr * 100, sha256b(pt).hex()[:16]))
        if ident or text_open:
            rows.append((raw[8:16].hex(), ct, "OPENED", ident or text_open, where))
            continue
        mine = raw[16:]
        tok = tok if isinstance(tok, str) else tok.decode("ascii", "replace")
        pref = [len(c) for (c, _r) in known_ct.get(raw[8:16], [])
                if len(c) > ct and c.startswith(mine)]
        if pref:
            rows.append((raw[8:16].hex(), ct, "PREFIX",
                         "ct is a byte-prefix of a %d B blob with the same salt "
                         "(truncated transcript)" % pref[0], where))
            continue
        dmg = None
        # labelled base64 of every known blob, for split-presentation detection
        known_b64 = []
        for _salt, _lst in known_ct.items():
            for _c, _o in _lst:
                _lab = KNOWN.get(sha256b(_c).hex())
                if _lab:
                    known_b64.append((_lab, base64.b64encode(_c).decode()))
        known_b64.append(("canonical BLOB1", BLOB1))
        # a copy of BLOB1 with characters broken and/or junk swallowed into the
        # base64 run: judged at the character level, since the damage is textual
        nd = b64_ndiff(tok[:len(BLOB1)], BLOB1)
        nd_head = b64_ndiff(tok[:64], BLOB1[:64])
        if nd_head <= 8 and (nd == 0 or nd > 12):
            rows.append((raw[8:16].hex(), ct, "DAMAGED",
                         "BLOB1 copy: first 64 base64 chars differ in %d places; "
                         % nd_head + repair_note(raw, blob1, BLOB1, laid, known_b64), where))
            continue
        if 0 < nd <= 12:
            note2 = ("base64 differs from BLOB1 in %d of %d chars"
                     % (nd, min(len(tok), len(BLOB1))))
            if raw[16:] == blob1[16:]:
                note2 += "; ciphertext identical, the SALT alone is damaged"
            note2 += "; " + repair_note(raw, blob1, BLOB1, laid, known_b64)
            rows.append((raw[8:16].hex(), ct, "DAMAGED", note2, where))
            continue
        pool = [(c, o) for lst in known_ct.values() for (c, o) in lst]
        for c, other in pool:
            if other == raw or len(c) < 64 or ct < 64:
                continue
            m = min(len(c), ct)
            if m < 64:
                continue
            d = sum(1 for i in range(m) if c[i] != mine[i])
            if 0 < d <= 8 and d < m:
                dmg = ("%d of %d ciphertext bytes differ from a known %d B blob "
                       "(salt %s)" % (d, m, len(c), other[8:16].hex()))
        if dmg:
            rows.append((raw[8:16].hex(), ct, "DAMAGED",
                         "OCR/mangling of a known blob: " + dmg, where))
            continue
        note = KNOWN_OPEN.get(raw[8:16].hex())
        rows.append((raw[8:16].hex(), ct, "OPENED" if note else "BLOCKED",
                     note or "no password in the derived set opens it", where))

    order = {"OPENED": 0, "BLOCKED": 1, "DAMAGED": 2, "PREFIX": 3, "FRAGMENT": 4}
    rows.sort(key=lambda r: (order[r[2]], -r[1]))
    print()
    print("%-17s %6s  %-9s %s" % ("salt", "ct", "class", "detail"))
    for s, ct, cl, de, where in rows:
        print("%-17s %6d  %-9s %s" % (s, ct, cl, de))
        print("%26s%s" % ("", where[0]))
    tally = {}
    for r in rows:
        tally[r[2]] = tally.get(r[2], 0) + 1
    print()
    print("tally:", tally)
    real = [r for r in rows if r[2] in ("OPENED", "BLOCKED")]
    print("real distinct blobs: %d  (opened %d, blocked %d)"
          % (len(real), sum(1 for r in real if r[2] == "OPENED"),
             sum(1 for r in real if r[2] == "BLOCKED")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
