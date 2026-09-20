#!/usr/bin/env python3
"""HKDF (RFC 5869) faithful family from the casebeer/python-hkdf steer.

Algorithm (hkdf.py, exceeds nothing): PRK = HMAC-hash(salt, IKM); OKM = T(1)||T(2)...
with T(i) = HMAC-hash(PRK, T(i-1) || info || bytes([i])). Default hash sha512 in the
freestanding funcs, sha256 in the Hkdf class; both run. length=32 (the blob-key size).
Bounded committed reduction:
   - IKM (input key material): sha256 of the same 15 in-corpus anchors as derive-key
     (gates, seed, VIC plaintext, 7 tokens, dbbib/faed canon bytes) - 32B each.
   - salt: '' (-> all-zero per standard), 'gsmg', 'salphaseion', 'theinterpreter',
     gateA, 'explosion', 'thecode'.
   - info: in-corpus names (X, thepassword, answer, key, tokens, stream names, gate
     addresses, interpreter labels).
   - output: ether via hkdf_extract+expand with either hash, forms hex/hexU/b64/latin1.
Halves the "KDF thread" accounting: derive-key (BLAKE2b, late-147) used the same anchor
set; HKDF implements the same role (key derivation needing a separate master/IKM), never
oracled before.
"""
import json, pathlib, hashlib, hmac, base64

BASE = pathlib.Path(__file__).resolve().parents[1]
STREAMS = json.loads((BASE / "data" / "finalpage-digit-streams.json").read_text())
S = json.loads((BASE / "data" / "salphaseion-streams.json").read_text())

CANON = {"a": 8, "b": 1, "c": 5, "d": 0, "e": 6, "f": 3, "g": 7, "h": 4, "i": 2}


def canon_bytes(s):
    if s.endswith("z"):
        s = s[:-1]
    return bytes(CANON[c] for c in s)


ANCHORS = {
    "gateA": "1gsmg1jc9wtdswfwapgj2xcmjpawx7prbe",
    "gateB": "17ucy1k9zuaaoy6jvtm932w9jup5lxfyha",
    "seed": "btcseed",
    "vic": "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE",
    "tok1": "yourlastcommand", "tok2": "secondanswer", "tok3": "leavethematrix",
    "tok4": "isolveditwithanabacus", "tok5": "matrixsumlist", "tok6": "shabef",
    "tok7": "enter",
    "dbbcanon": canon_bytes(STREAMS["dbbib_91"]),
    "faedcanon": canon_bytes(STREAMS["faed_570"]),
}
ikms = {f"sha256({k})": hashlib.sha256(v if isinstance(v, bytes) else v.encode()).digest()
        for k, v in ANCHORS.items()}

SALTS = ["", "gsmg", "salphaseion", "theinterpreter", "explosion", "thecode",
         "1gsmg1jc9wtdswfwapgj2xcmjpawx7prbe", "halfandbetterhalf"]
INFOS = ["X", "x", "thepassword", "password", "answer", "key", "thekey",
         "interpreter", "interpreteralphabet", "theinterpreter", "alphabet", "decode",
         "thecode", "causality", "yourlastcommand", "secondanswer", "leavethematrix",
         "matrixsumlist", "shabef", "enter", "dbbib_91", "faed_570", "dbbib", "faed",
         "gate", "the gate", "derive-key", "halfandbetterhalf"]


def hkdf_extract(salt, ikm, h):
    hlen = h().digest_size
    if salt is None or len(salt) == 0:
        salt = bytes(hlen)
    return hmac.new(salt, ikm, h).digest()


def hkdf_expand(prk, info, length, h):
    hlen = h().digest_size
    okm = b""
    t = b""
    for i in range(1, (length // hlen) + 2):
        t = hmac.new(prk, t + info + bytes([i]), h).digest()
        okm += t
        if len(okm) >= length:
            break
    return okm[:length]


def derive(salt, ikm, info, h):
    return hkdf_expand(hkdf_extract(salt, ikm, h), info, 32, h)


def main():
    cands = {}
    for ik, ikm in ikms.items():
        for salt in SALTS:
            for info in INFOS:
                for hn, h in (("sha256", hashlib.sha256), ("sha512", hashlib.sha512)):
                    d = derive(salt.encode(), ikm, info.encode(), h)
                    for form, x in [("hex", d.hex()), ("hexU", d.hex().upper()),
                                    ("b64", base64.b64encode(d).decode()),
                                    ("latin1", d.decode("latin1"))]:
                        cands.setdefault(x, (ik, salt, info, hn, form))
    uniq = [(k, v) for k, v in cands.items() if k]
    with open("/data/data/com.termux/files/usr/tmp/opencode/hkdf_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/hkdf_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()