#!/usr/bin/env python3
"""XOR-triangle battery on certified in-repo artifacts (issue #88 "XOR triangle" hint).

Applies adjacent-pair XOR pyramids (and Pascal-mod-2 / binomial parity variants)
to every certified byte sequence we hold, and produces candidate password strings X
for the final-gate oracles (small blob + Dualite gate):

  inputs  - the 1327-byte cosmic plaintext (re-derived, certified pipeline)
          - the 103x103 bit-matrix row/col sum arrays
          - data/B1_79.bin, data/B2_79.bin (the two 79-byte artifacts)
          - the "base-38 sequence" (sec103) bytes

  triangle ops per input sequence s (bytes):
      apex    = repeated adjacent XOR down to 1 byte
      rows[1] = 1 level of adjacent XOR (len n-1) -> taken as candidate string
      pascal  = XOR-pair pyramid diagonal reads
  orderings: fwd, rev; encodings: raw bytes -> hex string, hexdigest, and
             printable-ASCII pass-through.

Every produced candidate is a plain string X (oracle takes X itself). No gate is
assumed; results are honest per-line. Writes candidate list to OUT (default
/data/data/com.termux/files/usr/tmp/opencode/xortri_cands.txt).
"""
import base64
import hashlib
import os
from functools import reduce
from pathlib import Path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("OUT", "/data/data/com.termux/files/usr/tmp/opencode/xortri_cands.txt")

BLOB_TXT = os.path.expanduser("~/briefcase/CosmicDuality.txt")


def sha256(b): return hashlib.sha256(b).digest()


def get_cosmic_plaintext():
    blob = "".join(Path(BLOB_TXT).read_text().split())
    raw = base64.b64decode(blob)
    salt = raw[8:16]
    ct = raw[16:]
    tokens = ["matrixsumlist","enter","lastwordsbeforearchichoice","thispassword",
              "matrixsumlist","yourlastcommand","secondanswer"]
    key = reduce(lambda a, t: bytes(x ^ y for x, y in zip(a, sha256(t.encode()))),
                 tokens, bytes(32))
    def evp(pw, salt, klen=32, ilen=16):
        d, prev = b"", b""
        while len(d) < klen + ilen:
            prev = hashlib.md5(prev + pw + salt).digest()
            d += prev
        return d[:klen], d[klen:klen + ilen]
    k, iv = evp(key, salt)
    pt = AES.new(k, AES.MODE_CBC, iv).decrypt(ct) if False else None
    from Crypto.Cipher import AES
    k, iv = evp(key, salt)
    pt = AES.new(k, AES.MODE_CBC, iv).decrypt(ct)
    return pt[:-pt[-1]]


def xor_triangle(seq):
    """adjacent-pair XOR pyramid; returns [apex_bytes, ...all level rows of bytes]."""
    levels = [bytes(seq)]
    cur = list(seq)
    while len(cur) > 1:
        cur = [a ^ b for a, b in zip(cur, cur[1:])]
        levels.append(bytes(cur))
    return levels


def pascal_rows(seq):
    """Pascal mod-2 (binomial-coefficient XOR) diagonal reads across the pyramid."""
    tri = []
    cur = list(seq)
    while cur:
        tri.append(cur)
        cur = [a ^ b for a, b in zip(cur, cur[1:])]
    out = []
    n = len(tri)
    for d in range(n):
        diag = bytes(tri[i][j] for i, j in
                     [(k, d - k) for k in range(max(0, d - n + 1), min(d, n - 1) + 1)]
                     if j < len(tri[i]))
        if diag:
            out.append(diag)
    return out


def candify(label, seqs, out):
    """seqs: list of (name, bytes); produce candidate strings (hex / printable / apex)."""
    seen = set()
    for name, s in seqs:
        if len(s) == 0:
            continue
        levels = xor_triangle(s)
        apex = levels[-1]
        for rev in (False, True):
            s2 = s[::-1] if rev else s
            tag = f"{name}|rev" if rev else name
            for prod in _produce(s2, apex if not rev else xor_triangle(s2)[-1]):
                k = tag + "|" + prod[0]
                if prod[1] and prod[1] not in seen:
                    seen.add(prod[1])
                    out.append((prod[1], k))
        # pascal diagonals
        for i, dg in enumerate(pascal_rows(s[::-1] if False else s)):
            for prod in _produce(dg, None):
                k = f"{name}|pascal{i}|{prod[0]}"
                if prod[1] and prod[1] not in seen:
                    seen.add(prod[1])
                    out.append((prod[1], k))


def _produce(seq, apex):
    """raw bytes/hex/printable/hexdigest variants of a byte sequence."""
    result = []
    raw = bytes(seq) if not isinstance(seq, bytes) else seq
    hexs = raw.hex()
    result.append((f"hex{len(raw)}", hexs))
    try:
        txt = raw.decode("ascii")
        if txt.isprintable():
            result.append((f"txt{len(raw)}", txt))
    except Exception:
        pass
    if apex is not None:
        result.append((f"apex{len(raw)}", apex.hex()))
    return result


def load_artifacts():
    arr = {}
    for label, path in (("B1", os.path.join(BASE, "data", "B1_79.bin")),
                        ("B2", os.path.join(BASE, "data", "B2_79.bin"))):
        arr[label] = Path(path).read_bytes()
    return arr


def main():
    import sys
    sys.path.insert(0, os.path.join(BASE, "tools"))
    from Crypto.Cipher import AES  # noqa: F401  (ensure availability early)

    pt = get_cosmic_plaintext()
    print(f"[cosmic] plaintext {len(pt)}B sha256={sha256(pt).hex()[:16]}...")

    bits = "".join(format(b, "08b") for b in pt)
    R = C = 103
    total = R * C
    b = bits[:total]
    m = [[int(b[r * C + c]) for c in range(C)] for r in range(R)]
    row = bytes(min(sum(m[r]), 255) for r in range(R))
    col = bytes(min(sum(m[r][c] for r in range(R)), 255) for c in range(C))
    sec103 = bytes(((row[i] + col[(i + 7) % C]) & 0xFF) for i in range(R))

    # base-38 decode of sec103 (community path)
    val = 0
    for dig in sec103:
        val = val * 38 + (dig - 80)
    b38 = val.to_bytes((val.bit_length() + 7) // 8, "big")

    artifacts = load_artifacts()
    print("[artifacts]", {k: len(v) for k, v in artifacts.items()})

    out = []
    inputs = [
        ("cosmic_pt", pt),
        ("cosmic_sha256", sha256(pt)),
        ("row_sums", row),
        ("col_sums", col),
        ("sec103", sec103),
        ("base38", b38),
        ("B1", artifacts["B1"]),
        ("B2", artifacts["B2"]),
        ("B1xorB2", bytes(a ^ b for a, b in zip(artifacts["B1"], artifacts["B2"]))),
    ]
    candify("inputs", inputs, out)

    # also XOR triangle on the cosmic plaintext bit-stream as row-parities
    row_bitxor = bytes(reduce(int.__xor__, [0] + m[r]) for r in range(R))
    col_bitxor = bytes(reduce(int.__xor__, [0] + [m[r][c] for r in range(R)]) for c in range(C))
    candify("bitxor", [("row_bitxor", row_bitxor), ("col_bitxor", col_bitxor),
                       ("row_bitxor+col_bitxor", row_bitxor + col_bitxor)], out)

    dedup = {}
    for s, tag in out:
        dedup.setdefault(s, tag)
    final = [(s, t) for s, t in dedup.items()]

    Path(OUT).write_text("\n".join(s for s, _ in final) + "\n")
    Path(OUT.replace(".txt", "_tags.txt")).write_text("\n".join(t for _, t in final) + "\n")
    print(f"[out] {len(final)} candidates -> {OUT}")


if __name__ == "__main__":
    main()