#!/usr/bin/env python3
"""Re-derive candidate reductions of the 1327-byte Dualite/Cosmic-Duality plaintext
into a single 32-byte private key, and check each against the Dualite gate
`17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa`.

Rationale: the small-blob reduction (first32/last32/sha256 of a 64-byte plaintext)
cannot apply to a 1327-byte plaintext. The decoded instruction token `matrixsumlist`
arguably names the reduction: matrix sum list. §12 packed the plaintext as a 103x103
binary matrix and combined row/col sums into two 32-byte values (Half/Better-half,
already public + unfunded). Here we enumerate matrix-sum and structural reductions to
a SINGLE 32-byte key and test each directly against the Dualite gate as a private key.

Public/authorized puzzle only. Direct address comparison is the ground truth.
"""
import os
import base64
import hashlib
from functools import reduce
from pathlib import Path

import base58
from Crypto.Cipher import AES
from ecdsa import SECP256k1, SigningKey

TARGET = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"
BLOB_TXT = os.path.expanduser("~/briefcase/CosmicDuality.txt")

def sha256(b): return hashlib.sha256(b).digest()

def priv_to_p2pkh(pk: bytes):
    vk = SigningKey.from_string(pk, curve=SECP256k1).get_verifying_key()
    pub = b"\x04" + vk.to_string()
    h = hashlib.new("ripemd160", sha256(pub)).digest()
    return base58.b58encode_check(b"\x00" + h).decode()

def get_plaintext():
    blob = "".join(Path(BLOB_TXT).read_text().split())
    raw = base64.b64decode(blob); salt = raw[8:16]; ct = raw[16:]
    tokens = ["matrixsumlist","enter","lastwordsbeforearchichoice","thispassword",
              "matrixsumlist","yourlastcommand","secondanswer"]
    key = reduce(lambda a,t: bytes(x^y for x,y in zip(a,hashlib.sha256(t.encode()).digest())),tokens,bytes(32))
    def evp(pw,salt,klen=32,ilen=16):
        d=b"";prev=b""
        while len(d)<klen+ilen:
            prev=hashlib.md5(prev+pw+salt).digest(); d+=prev
        return d[:klen],d[klen:klen+ilen]
    k,iv=evp(key,salt)
    pt=AES.new(k,AES.MODE_CBC,iv).decrypt(ct)
    return pt[:-pt[-1]]

def main():
    pt = get_plaintext()
    N = len(pt)
    bits = "".join(format(b,"08b") for b in pt)
    # matrix dims: try all r x c where r*c <= len(bits); prefer ~square. Drop pad bits.
    cand_sets = {}

    def add(name, key_bytes):
        if len(key_bytes) == 32:
            cand_sets.setdefault(name, set()).add(key_bytes.hex())

    # --- family A: byte-level direct reductions ---
    add("first32", pt[:32]); add("last32", pt[-32:])
    add("sha256(pt)", sha256(pt)); add("sha256d(pt)", sha256(sha256(pt)))
    add("sha256(pt[::-1])", sha256(pt[::-1]))
    add("sha256(sha256(first1k))", sha256(sha256(pt[:1000])))

    # --- family B: matrix-sum reductions across square-ish matrices ---
    for R in [101, 102, 103, 104, 105]:
        C = R
        total = R*C
        if total > len(bits):
            continue
        b = bits[:total]
        m = [[int(b[r*C+c]) for c in range(C)] for r in range(R)]
        row = [sum(m[r]) for r in range(R)]
        col = [sum(m[r][c] for r in range(R)) for c in range(C)]
        # ensure within byte range
        rows_b = bytes(min(x,255) for x in row)
        cols_b = bytes(min(x,255) for x in col)
        add(f"sha256(row_sums_{R}x{C})", sha256(rows_b))
        add(f"sha256(col_sums_{R}x{C})", sha256(cols_b))
        add(f"sha256(row+col_{R}x{C})", sha256(rows_b+cols_b))
        add(f"sha256(col+row_{R}x{C})", sha256(cols_b+rows_b))
        # alternating interleave row/col
        inter = bytes(x for pair in zip(rows_b, cols_b) for x in pair)
        add(f"sha256(interleave_{R}x{C})", sha256(inter))
        # xor row and col bytewise (pad shorter)
        n = min(len(rows_b), len(cols_b))
        xored = bytes(a^b for a,b in zip(rows_b[:n], cols_b[:n]))
        add(f"sha256(row_xor_col_{R}x{C})", sha256(xored))
        # digit->char secondary from §12 with shift, hashed
        for shift in [0,7,13]:
            sec = bytes(((row[i]+col[(i+shift)%len(col)])&0xFF) for i in range(len(row)))
            add(f"sha256(sec_shift{shift}_{R}x{C})", sha256(sec))

    # --- family C: the §12 exact 103x103 secondary string as various keys ---
    for R in [103]:
        C=103; b=bits[:R*C]
        m=[[int(b[r*C+c]) for c in range(C)] for r in range(R)]
        row=[sum(m[r]) for r in range(R)]; col=[sum(m[r][c] for r in range(R)) for c in range(C)]
        sec=bytes(((row[i]+col[(i+7)%C])&0xFF) for i in range(R))
        add("sec103_first32", sec[:32])
        add("sec103_last32", sec[-32:])
        add("sha256(sec103)", sha256(sec))
        # base-38 decode of sec -> 68 bytes, then use its first/last 32 & sha256
        d38=[(c-80) for c in sec]
        # treat as big base-38 number to bytes
        val=0
        for dig in d38:
            val=val*38+dig
        big=val.to_bytes((val.bit_length()+7)//8, 'big')
        add("base38_bytes_first32", big[:32])
        add("base38_bytes_last32", big[-32:])
        add("sha256(base38_bytes)", sha256(big))
        # sub-blobs 32 bytes each at offsets reconstructing Half/Better
        # (already public; include for completeness)
        add("half_better_concat32", big[32:64])
        add("better_half_concat32", big[:32])

    # --- collect and check ---
    total_cand = sum(len(v) for v in cand_sets.values())
    print(f"[derive] {total_cand} candidate keys across {len(cand_sets)} families")
    hits = 0
    for name, hexset in sorted(cand_sets.items()):
        for h in hexset:
            pk = bytes.fromhex(h)
            try:
                addr = priv_to_p2pkh(pk)
            except Exception:
                continue
            mark = "MATCH" if addr == TARGET else ""
            if addr == TARGET:
                hits += 1
            print(f"  {name:44s} -> {addr}  {mark}")
            if addr == TARGET:
                print(f"  *** PRIV KEY FOUND *** {pk.hex()}")
    print(f"\n[check] {hits} hits for gate {TARGET}")

if __name__ == "__main__":
    main()
