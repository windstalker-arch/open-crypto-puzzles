#!/usr/bin/env python3
"""3DES-EDE3 faithful family from the sanatb97/3DES-Implementation-in-C steer.

Repo is textbook Triple-DES (IP/PC1/PC2/S-boxes standard; E-D-E with 3 keys), does NOT
compile (nR stray at 3des.c:148), placeholder 40-bit keys, random input vecs. The
algorithm family 3DES/EDE has never been oracled in the ledger, so run it bounded:
   - key sets: (a) repo's own 3 default key hex values, (b) sha256(gate1/seed/gate2)
     first-8-byte commits, (c) sha256(first 3 seven-token) commits
   - inputs (8-byte block texts): dbbib_91/faed_570 under the 3 digit maps (canon/pos1/
     pos0); plus certified plaintext_head and phase-3.2.2 VIC plaintext (truncated blocks)
   - operations: EDE-encrypt -> hex X; EDE-decrypt -> hex and latin-1 X
   - IV = zero for CBC variants on >8B inputs
All candidate lines single-line.
"""
import json, pathlib, hashlib
from Crypto.Cipher import DES3

BASE = pathlib.Path(__file__).resolve().parents[1]
STREAMS = json.loads((BASE / "data" / "finalpage-digit-streams.json").read_text())
S = json.loads((BASE / "data" / "salphaseion-streams.json").read_text())

CANON = {"a": 8, "b": 1, "c": 5, "d": 0, "e": 6, "f": 3, "g": 7, "h": 4, "i": 2}
POS1 = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9}
POS0 = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7, "i": 8}


def parity_bytes(b):
    out = bytes()
    for x in b:
        low7 = x & 0x7F
        ones = bin(low7).count("1")
        out += bytes([low7 | (0x80 if ones % 2 == 0 else 0)])
    return out


def key_from_sha(anchor, i):
    d = hashlib.sha256(anchor.encode()).digest()
    return d[i * 8:(i + 1) * 8]


def map_bytes(s, mp):
    if s.endswith("z"):
        s = s[:-1]
    return bytes(mp[c] for c in s)


def pad8(b):
    n = (-len(b)) % 8
    return b + bytes(n)  # zero pad


def chunks(b, k=8):
    return [b[i:i + k] for i in range(0, len(b), k)]


def main():
    cands = {}
    prov = []
    GATE_A = "1gsmg1jc9wtdswfwapgj2xcmjpawx7prbe"
    GATE_B = "17ucy1k9zuaaoy6jvtm932w9jup5lxfyha"
    SEED = "theseedisplanted"
    TOKENS = ["yourlastcommand", "secondanswer", "leavethematrix", "isolveditwithanabacus",
              "matrixsumlist", "shabef", "enter"]
    keysets = {
        "repo-defaults": (0x9837239487).to_bytes(8, "big") + (0x5812938832).to_bytes(8, "big") + (0x3719827398).to_bytes(8, "big"),
        "sha-gateA-seed-gateB": key_from_sha(GATE_A, 0) + key_from_sha(SEED, 0) + key_from_sha(GATE_B, 0),
        "sha-tok123": key_from_sha(TOKENS[0], 0) + key_from_sha(TOKENS[1], 0) + key_from_sha(TOKENS[2], 0),
    }
    texts = {}
    for nm in ("dbbib_91", "faed_570"):
        for mpn, mp in (("canon", CANON), ("pos1", POS1), ("pos0", POS0)):
            texts[f"{nm}:{mpn}"] = map_bytes(STREAMS[nm], mp)
    texts["plaintext_head"] = S["plaintext_head"][:48].encode()
    texts["vic322"] = ("INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE").encode()

    def add(x, src):
        if x:
            cands.setdefault(x, src)

    for kn, key in keysets.items():
        pkey = parity_bytes(key)
        for tn, pt in texts.items():
            blk = pad8(pt)
            try:
                c = DES3.new(pkey, DES3.MODE_ECB)
                ct = b"".join(c.encrypt(b) for b in chunks(blk))
                add(ct.hex(), f"3des-ede3-ecb-enc:{kn}:{tn}")
                add(ct.hex().upper(), f"3des-ede3-ecb-encUP:{kn}:{tn}")
                d = DES3.new(pkey, DES3.MODE_ECB)
                dct = b"".join(d.decrypt(b) for b in chunks(blk))
                add(dct.hex(), f"3des-ede3-ecb-dec:{kn}:{tn}")
                if all(32 <= x < 127 for x in dct):
                    add(dct.decode("latin1"), f"3des-ede3-ecb-declat:{kn}:{tn}")
            except ValueError as e:
                prov.append(f"skip:{kn}:{tn}:{e}")
    # CBC variants (zero IV) on full blocks
    for kn, key in keysets.items():
        pkey = parity_bytes(key)
        for tn, pt in texts.items():
            n = len(pad8(pt)) // 8
            if n == 0:
                continue
            try:
                c = DES3.new(pkey, DES3.MODE_CBC, bytes(8))
                full = pad8(pt)
                cp = b"".join(c.encrypt(full[i:i + 8]) for i in range(0, len(full), 8))
                add(cp.hex(), f"3des-ede3-cbc-enc:{kn}:{tn}")
                d = DES3.new(pkey, DES3.MODE_CBC, bytes(8))
                dp = b"".join(d.decrypt(full[i:i + 8]) for i in range(0, len(full), 8))
                add(dp.hex(), f"3des-ede3-cbc-dec:{kn}:{tn}")
            except ValueError as e:
                prov.append(f"skipCBC:{kn}:{tn}:{e}")
    uniq = [(k, v) for k, v in cands.items() if k]
    with open("/data/data/com.termux/files/usr/tmp/opencode/tdes_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/tdes_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
        f.write("\n".join(prov) + "\n")
    print("candidates:", len(uniq), "skips:", len(prov))


if __name__ == "__main__":
    main()