#!/usr/bin/env python3
"""Keyed-BLAKE2b family from the hyperdivision/derive-key steer.

derive-key (index.js): output = BLAKE2b.batch(ns_blob || input, key=masterKey) where
ns_blob = str(len(ns)) + "\\n" + ns. Bounded committed reduction:
   - masterKey: sha256 of in-corpus anchors (gate A/B, seed, VIC plaintext, 7 tokens, dbbib/
     faed canon-map bytes) = 32B high-entropy keys, as the README demands.
   - ns: ascii puzzle namespaces (gsmg/gsmg-io-5btc-puzzle/halfandbetterhalf/interpreter/
     theinterpreter/salphaseion/alphanoises/derive-key/yyyy).
   - input/name: in-corpus names ("X", "thepassword", "password", "answer", "key", tokens,
     stream names, gate addresses, "theinterpreter", "interpreteralphabet", phrases).
Outputs fed straight as X candidates: .hex / .hex-upper / base64 / raw latin-1.
This primitive (keyed hash / BLAKE2) has never been oracled in the ledger.
"""
import json, pathlib, hashlib, base64
from Crypto.Hash import BLAKE2b

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
    "tok1": "yourlastcommand",
    "tok2": "secondanswer",
    "tok3": "leavethematrix",
    "tok4": "isolveditwithanabacus",
    "tok5": "matrixsumlist",
    "tok6": "shabef",
    "tok7": "enter",
    "dbbcanon": canon_bytes(STREAMS["dbbib_91"]),
    "faedcanon": canon_bytes(STREAMS["faed_570"]),
}
masters = {f"sha256({k})": hashlib.sha256(v if isinstance(v, bytes) else v.encode()).digest() for k, v in ANCHORS.items()}

NAMESPACES = [
    "gsmg", "gsmg-io-5btc", "gsmg-io-5btc-puzzle", "halfandbetterhalf",
    "interpreter", "theinterpreter", "salphaseion", "alphanoises",
    "derive-key", "theinterpreteralphabet", "", "GSMG", "thegate",
]
NAMES = [
    "X", "x", "thepassword", "password", "answer", "key", "thekey",
    "interpreter", "interpreteralphabet", "theinterpreter", "alphabet",
    "decode", "thecode", "reply", "causality", "primes", "yourlastcommand",
    "secondanswer", "leavethematrix", "matrixsumlist", "shabef", "enter",
    "dbbib_91", "faed_570", "dbbib", "faed", "gate", "the gate",
]


def derive(ns, master, name):
    ns_blob = f"{len(ns.encode('ascii'))}\n{ns}".encode("ascii")
    h = BLAKE2b.new(digest_bits=256, key=master)
    h.update(ns_blob)
    h.update(name if isinstance(name, bytes) else name.encode("utf-8"))
    return h.digest()


def main():
    cands = {}
    for mk, master in masters.items():
        for ns in NAMESPACES:
            for nm in NAMES:
                d = derive(ns, master, nm)
                for form, x in [("hex", d.hex()), ("hexU", d.hex().upper()),
                                ("b64", base64.b64encode(d).decode()),
                                ("latin1", d.decode("latin1"))]:
                    cands.setdefault(x, (mk, ns, nm, form))
    uniq = [(k, v) for k, v in cands.items() if k]
    with open("/data/data/com.termux/files/usr/tmp/opencode/blake2_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/blake2_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()