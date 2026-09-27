#!/usr/bin/env python3
"""jyotiska_matrix_battery.py -- late-281.

Steer: github.com/jyotiska222/Custom-Cipher-Encryption-Decryption -- a 62-column
keyword-matrix polyalphabetic cipher (Vigenere-family over A-Z a-z 0-9 built from
a passkey keyword). Two passes against both funded gates:

  A. name-family candidates from the repo/author README (its own strings).
  B. the certified digit streams (dbbib69/91, faed570, zseg1/2) treated as cipher
     text: decrypt under every (passkey, key) drawn from the shared puzzle pool,
     then the raw cipher text x key-streams too.
"""
from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

DATA = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())
SURFACES = {
    "dbbib69": DATA["dbbib"],
    "dbbib91": DATA["dbbib_91"],
    "faed570": DATA["faed_570"][:570],
    "zseg1": DATA["z_segment_1"],
    "zseg2": DATA["z_segment_2"],
}
POOL = [
    "salphasion", "salphaseion", "salphaseionworld", "matrixsumlist", "enter",
    "lastwordsbeforearchichoice", "thispassword", "shabef",
    "ourfirsthintisyourlastcommand", "anstoo", "gsmg", "white", "rabbit",
    "alice", "bankingwar", "cryptogic", "digitallogic", "bitcoin", "escrow",
    "kccdclot", "digitalcryptologic", "trex", "adfgx", "adfgvx", "bifid",
    "vigenere", "autokey", "beaufort", "porta", "gronsfeld", "playfair",
    "columnar", "scytale", "zigzag", "keyword", "polybius", "atbash",
    "caesar", "affine", "nihilist", "straddlingcheckerboard", "railfence",
    "canyoulockwalletunlock", "thearchitectchoice", "theseedisplanted",
    "cthulhu", "matrix", "sumlist", "password", "notebook", "sha256",
    "followthewhiterabbit", "salphasionfinal", "realized", "durance",
    "phaseone", "somethingelse", "elaborate", "reasoning", "key",
]


def generate_matrix(keyword):
    base = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    filtered = "".join(c for c in base if c not in keyword)
    full = keyword + filtered
    return [full[i:] + full[:i] for i in range(62)]


def decrypt_message(enc, key, matrix):
    out = ""
    repeated = (key * (len(enc) // len(key))) + key[: len(enc) % len(key)]
    for i, ch in enumerate(enc):
        col = matrix[0].find(repeated[i])
        if col == -1:
            out += ch
            continue
        row = next((r for r in range(62) if matrix[r][col] == ch), None)
        out += ch if row is None else matrix[0][row]
    return out


def main() -> int:
    cands = set()
    names = ["CustomCipherEncryptionDecryption", "customcipher", "cipher",
             "jyotiska222", "jyotiska", "biswas", "PLgf6B", "62columnmatrix",
             "62matrix", "matrixcipher", "keywordmatrix", "dynamaticmatrix",
             "plgf6b", "passkey", "encryptiondecryption"]
    for w in names:
        for v in (w, w.lower(), w.upper(), w[::-1], "".join(x for x in w if x.isalnum())):
            cands.add(v)
    for sname, surface in SURFACES.items():
        letters = "".join(c for c in surface if c.isalnum())
        for pk, key in itertools.product(POOL, POOL):
            try:
                m = generate_matrix(pk)
            except Exception:
                continue
            pt = decrypt_message(letters, key, m)
            if pt and pt.isascii():
                cands.add(pt)
            # raw ciphertext itself under each key-stream is the same as above;
            # also test the stream x key interleave:
        for c in range(1, len(letters) + 1):
            pass
    out = os.path.join(os.path.expanduser("~"), "jyotiska_cands.txt")
    with open(out, "w") as f:
        f.writelines(c + "\n" for c in sorted(cands))
    print(f"[jyotiska_matrix_battery] {len(cands)} forms -> {out}")
    for prog in ("oracle.py", "oracle_dualite.py"):
        p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", prog), "--stdin"],
                           stdin=open(out), capture_output=True, text=True)
        lines = [l for l in p.stdout.splitlines() if l.strip()]
        print(f"[jyotiska_matrix_battery] {prog}: {lines[-1] if lines else 'NO MATCH'}")
        if "MATCH" in p.stdout and "NO MATCH" not in p.stdout:
            print(p.stdout)
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())