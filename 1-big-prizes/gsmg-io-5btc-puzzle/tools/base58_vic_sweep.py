#!/usr/bin/env python3
"""base58_vic_sweep.py -- Base58 / Bitcoin-charset readings of the a..i streams.

User directive: read the streams (a..i = 9 symbols) through the Base58 / Bitcoin
alphabet as the interpreter. The streams are natural base-9 digit strings; we
re-encode / decode them through Base58 in several concrete ways and test as password
X on BOTH gate addresses, and where the bytes could be a private key, reduce directly
to the gate address.

Public/authorized puzzle only. A hit is an oracle MATCH (or a direct address match).
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import base58

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())
DBBIB = d["dbbib_91"]   # authoritative; d["dbbib"] is the crop
FAED = d["faed_570"].rstrip("z")

ORACLE = os.path.join(ROOT, "tools", "oracle.py")
ORACLE_DUAL = os.path.join(ROOT, "tools", "oracle_dualite.py")
TARGET_DUAL = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"
TARGET_SMALL = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def base9_to_int(digits):
    v = 0
    for dg in digits:
        v = v * 9 + dg
    return v


def int_to_b58(v):
    if v == 0:
        return B58[0]
    out = ""
    while v > 0:
        v, rem = divmod(v, 58)
        out = B58[rem] + out
    return out


def b58_of_stream(digits):
    return int_to_b58(base9_to_int(digits))


def bytes_of_stream(digits):
    v = base9_to_int(digits)
    nbytes = (v.bit_length() + 7) // 8
    return v.to_bytes(max(nbytes, 1), "big")


def merge(a, b):
    n = min(len(a), len(b))
    out = []
    for i in range(n):
        out.append(a[i]); out.append(b[i])
    out.extend(a[n:]); out.extend(b[n:])
    return "".join(out)


def priv_to_addr(pk):
    from ecdsa import SECP256k1, SigningKey
    try:
        sk = SigningKey.from_string(pk[:32], curve=SECP256k1)
        pub = b"\x04" + sk.get_verifying_key().to_string()
        h = hashlib.new("ripemd160", hashlib.sha256(pub).digest()).digest()
        return base58.b58encode_check(b"\x00" + h).decode()
    except Exception:
        return None


def main():
    m0 = {c: i for i, c in enumerate("abcdefghi")}       # a=0..i=8
    m1 = {c: i + 1 for i, c in enumerate("abcdefghi")}   # a=1..i=9
    streams = {
        "dbbib": DBBIB,
        "faed": FAED,
        "merge_yinyang_12": merge(DBBIB, FAED),
        "merge_yinyang_21": merge(FAED, DBBIB),
    }

    cands = []
    seen = set()

    def add(label, s):
        if s and s not in seen:
            seen.add(s)
            cands.append((label, s))

    direct_addr_hits = []

    for sname, s in streams.items():
        for mname, m in [("a0i8", m0), ("a1i9", m1)]:
            digits = [m[c] for c in s]
            v = base9_to_int(digits)
            vb = bytes_of_stream(digits)
            add(f"{sname}_{mname}_b58_int", int_to_b58(v))
            add(f"{sname}_{mname}_b58_bytes", base58.b58encode(vb).decode())
            add(f"{sname}_{mname}_hex", vb.hex())
            if len(digits) >= 4:
                # read the a..i as base58-ish by mapping each symbol to its position
                # in the base58 alphabet (9 distinct slots) and to a 3-digit chunk
                pass
            # direct privkey reduction
            addr = priv_to_addr(vb)
            if addr in (TARGET_DUAL, TARGET_SMALL):
                direct_addr_hits.append((sname, mname, addr, vb.hex()))
            if addr is not None and len(vb) >= 32:
                pass

    # Also: map each a..i symbol to a *letter* in base58 space then base58-decode
    # positions 1..9 of the alphabet -> chars '1','2','3','4','5','6','7','8','9'
    # gives a base58 string directly
    idx2b58 = {c: B58[pos] for pos, c in enumerate("abcdefghi")}
    for sname, s in streams.items():
        b58like = "".join(idx2b58[c] for c in s)
        add(f"{sname}_symbol_to_b58chr", b58like)
        try:
            raw = base58.b58decode(b58like)
            add(f"{sname}_symbol_to_b58chr_decode", raw.hex())
            add(f"{sname}_symbol_to_b58chr_decode_ascii", raw.decode("latin1"))
        except Exception:
            pass

    print(f"candidate X count: {len(cands)}")
    scratch = "/data/data/com.termux/files/usr/tmp/opencode"
    os.makedirs(scratch, exist_ok=True)
    path = os.path.join(scratch, "base58_vic_cands.txt")
    with open(path, "w") as f:
        for _, s in cands:
            f.write(s + "\n")

    print("\nDirect privkey->addr hits:", direct_addr_hits if direct_addr_hits else "none")

    for name, oracle, tgt in [("small", ORACLE, TARGET_SMALL), ("dualite", ORACLE_DUAL, TARGET_DUAL)]:
        r = subprocess.run([sys.executable, oracle, "--stdin"],
                           input=Path(path).read_bytes(), capture_output=True)
        lines = [ln for ln in r.stdout.decode().splitlines() if ln.strip()]
        hits = [ln for ln in lines if ln.startswith("MATCH")]
        print(f"[{name}] lines={len(lines)} MATCH={len(hits)}")
        for h in hits:
            print("HIT:", h)
            for lab, ss in cands:
                if ss in h:
                    print("   ->", lab, repr(ss))
        if not hits:
            print(f"[{name}] NO MATCH")


if __name__ == "__main__":
    main()
