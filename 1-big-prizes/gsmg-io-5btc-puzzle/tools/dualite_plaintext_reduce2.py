#!/usr/bin/env python3
"""Extended matrix-sum / structural reductions of the 1327-byte Dualite plaintext
into a single 32-byte private key, checked directly against gate `17ucy1K9...`.

Extends tools/dualite_plaintext_reduce.py with:
  - non-square bit matrices (8x1327, 16x664, 53x200, 100x106, 50x212, 40x265,
    206x52, 104x102, 4x2654) row/col sum reductions
  - the 103x103 row/col concatenations -> sha256 / big-int truncated to 32 bytes
  - the resulting keys also emitted as candidate password-X strings for the
    Dualite-gate oracle.
Public/authorized puzzle only. Direct address compare is ground truth.
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
def p2pkh(pk):
    vk = SigningKey.from_string(pk[:32], curve=SECP256k1).get_verifying_key()
    pub = b"\x04" + vk.to_string()
    h = hashlib.new("ripemd160", sha256(pub)).digest()
    return base58.b58encode_check(b"\x00" + h).decode()

def plaintext():
    blob = "".join(Path(BLOB_TXT).read_text().split())
    raw = base64.b64decode(blob); salt = raw[8:16]; ct = raw[16:]
    toks = ["matrixsumlist","enter","lastwordsbeforearchichoice","thispassword",
            "matrixsumlist","yourlastcommand","secondanswer"]
    key = reduce(lambda a,t: bytes(x^y for x,y in zip(a,sha256(t.encode()))), toks, bytes(32))
    def evp(pw,salt,kl=32,il=16):
        d=b"";p=b""
        while len(d)<kl+il:
            p=hashlib.md5(p+pw+salt).digest(); d+=p
        return d[:kl],d[kl:kl+il]
    k,iv=evp(key,salt)
    pt=AES.new(k,AES.MODE_CBC,iv).decrypt(ct)
    return pt[:-pt[-1]]

def main():
    pt = plaintext()
    bits = "".join(format(b,"08b") for b in pt)
    keys = []          # 32-byte candidate private keys
    x_strings = set()  # candidate password-X strings

    def addkey(k):
        if len(k) >= 32:
            k = k[:32]
            keys.append(k)
            x_strings.add(k.hex())

    def matrix_keys(R, C):
        if R*C > len(bits): return
        b = bits[:R*C]
        m = [[int(b[r*C+c]) for c in range(C)] for r in range(R)]
        row = [(sum(m[r])&0xFF) for r in range(R)]
        col = [(sum(m[r][c] for r in range(R))&0xFF) for c in range(C)]
        addkey(sha256(bytes(row)))
        addkey(sha256(bytes(col)))
        addkey(sha256(bytes(row)+bytes(col)))
        addkey(sha256(bytes(col)+bytes(row)))
        addkey(bytes(row)+bytes(col))        # raw 2*R bytes (truncated to 32)
        addkey(bytes(col)+bytes(row))

    for (R,C) in [(8,1327),(16,664),(53,200),(100,106),(50,212),(40,265),(206,52),
                  (104,102),(4,2654),(103,103),(102,102),(101,101)]:
        matrix_keys(R,C)

    # 103x103 concatenations -> big-int reduced mod 2^256
    R=C=103; b=bits[:R*C]
    m=[[int(b[r*C+c]) for c in range(C)] for r in range(R)]
    row=[(sum(m[r])&0xFF) for r in range(R)]; col=[(sum(m[r][c] for r in range(R))&0xFF) for c in range(C)]
    bigrow=int("".join(f"{x:02x}" for x in row),16)
    bigcol=int("".join(f"{x:02x}" for x in col),16)
    addkey(((bigrow+bigcol) & ((1<<256)-1)).to_bytes(32,'big'))
    addkey(((bigrow^bigcol) & ((1<<256)-1)).to_bytes(32,'big'))
    # typed as printable if possible
    try:
        addkey(((bigrow+bigcol) % (1<<255)).to_bytes(32,'big'))
    except Exception:
        pass
    # raw plaintext direct forms
    addkey(sha256(pt)); addkey(sha256(sha256(pt))); addkey(pt[:32]); addkey(pt[-32:])

    # de-dup
    seen=set(); uniq=[]
    for k in keys:
        if k not in seen: seen.add(k); uniq.append(k)

    hits=0
    print(f"[derive] {len(uniq)} unique 32-byte keys")
    for k in uniq:
        try:
            addr=p2pkh(k)
        except Exception:
            continue
        print("  ", addr, "MATCH" if addr==TARGET else "")
        if addr==TARGET:
            hits+=1
            print("  *** PRIVATE KEY:", k.hex())
    print(f"[check] {hits} hits for gate {TARGET}")

    with open("/data/data/com.termux/files/usr/tmp/opencode/dualite_red_x.txt","w") as f:
        f.writelines(x+"\n" for x in sorted(x_strings))
    print("X candidate strings written:", len(x_strings))

if __name__ == "__main__":
    main()
