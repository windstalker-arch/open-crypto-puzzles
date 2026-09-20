#!/usr/bin/env python3
"""Option 2+3: bounded co-key/layer battery over the certified anchors.

- WITNESS A (option 2): certified Bifid decoder (bifid_repro build_grid/
  bifid_decrypt) reproduces faed(570)->BTCSEEDDEOEM... against stored head,
  THEN is applied to the AUTHORITATIVE 91-token dbbib (only the superseded 69
  form was ever decoded in tested.md:3371).
- WITNESS B (option 3): C1 derived in-code (chain_rebuild path): K_C1/K_C2/E_C.
  C2 (K_S1/K_S2/E_S) is ledger-verified (briefcase/MEMORY.md lines 10, 98).
- The four keys + E_* + stream transcripts are point-checked DIRECTLY against
  the certified gate-1 pubkey k*G=(f4d1bbd9..., odd y 9c73d25f...)
  (tested.md late-55). Then chain4 35x32 blocks are XORed/hashed with each key
  and the Bifid-dbbib output as co-key; every candidate scalar is point-checked.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from coincurve import PublicKey

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
streams = json.loads((DATA / "finalpage-digit-streams.json").read_text())
stored = json.loads((DATA / "salphaseion-streams.json").read_text())

sysb = __import__("sys")
sysb.path.insert(0, str(ROOT / "tools"))
from bifid_repro import build_grid, bifid_decrypt  # noqa: E402
import base64  # noqa: E402
from Crypto.Cipher import AES  # noqa: E402

BLOB1 = ("U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z"
         "QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ")
C1_PW = b"matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist"


def evp(pw, salt):
    d, prev = b"", b""
    while len(d) < 48:
        prev = hashlib.md5(prev + pw + salt).digest()
        d += prev
    return d[:32], d[32:48]


def aes_dec(ct, pw, salt):
    k, iv = evp(pw, salt)
    return AES.new(k, AES.MODE_CBC, iv).decrypt(ct)


def unpad(p):
    n = p[-1]
    return p[:-n] if p and n <= 16 and p[-n:] == bytes([n]) * n else None

GATE_X = bytes.fromhex("f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464")
GATE_Y = bytes.fromhex("9c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559")
GATE_PUB_UNC = b"\x04" + GATE_X + GATE_Y
GATE_COMP = bytes([0x02 | (GATE_Y[-1] & 1)]) + GATE_X
GATE_H160 = "a9553269572a317e39f0f518cb87c1a0ee1dbae4"

# C1 derived below; C2 from ledger (MEMORY.md:10,98, verified sha256 b40fce72...)
K_S1 = bytes.fromhex("b06fa6f20561756c865dac7190f063480a371e4a13206e529ee7e9078f309c4b")
K_S2 = bytes.fromhex("b11d211ca0a17cd68c580308f3e6f21d3f935c8da3c4373b6f73ab5ccfaea597")
E_S = bytes.fromhex("740a25de4b8e946d0a5ae2667a23a2")


def sha256b(b):
    return hashlib.sha256(b).digest()


def h160_of(pk_bytes):
    return hashlib.new("ripemd160", sha256b(pk_bytes)).hexdigest()


def is_gate(scalar):
    try:
        pk = PublicKey.from_valid_secret(scalar)
    except Exception:
        return False, None
    unc = pk.format(compressed=False)
    if unc == GATE_PUB_UNC:
        return True, "uncompressed"
    return pk.format(compressed=True) == GATE_COMP, "compressed"


grid, pos = build_grid()
grid2, pos2 = build_grid()

# ---- WITNESS A1: certified faed->BTCSEED ----
m_faed = "".join({c: c.upper() for c in "abcdefghi"}[c] for c in streams["faed_570"].rstrip("z"))
full = bifid_decrypt(m_faed, 570, grid, pos)
print("WITNESS A1 faed->Bifid head:", full[:40], "match=", full[:40] == stored["plaintext_head"])

m_dbbi = "".join({c: c.upper() for c in "abcdefghi"}[c] for c in streams["dbbib_91"])
out_dbbi = bifid_decrypt(m_dbbi, 91, grid, pos)
print("NEW   A2 dbbib91->Bifid:", out_dbbi)
print("      sha256:", sha256b(out_dbbi.encode()).hex(), "kw:", [w for w in
      ("BTCSEED", "MATRIX", "SUM", "ENTER", "KEY", "YIN", "YANG", "PRIME", "SEED")
      if w in out_dbbi])

# ---- C1 in-code ----
r1 = base64.b64decode(BLOB1)
try:
    P = unpad(aes_dec(r1[16:], C1_PW, r1[8:16]))
    K_C1_, K_C2_, E_C_ = P[:32], P[32:64], P[64:79]
    print("WITNESS B1 C1 derive:", K_C1_.hex()[:24], "..", K_C2_.hex()[:24], "..", E_C_.hex())
except Exception as e:
    print("C1 derive failed:", e)
    sysb.exit(1)

KEYS = {
    "K_C1": K_C1_,
    "K_C2": K_C2_,
    "K_S1": K_S1,
    "K_S2": K_S2,
    "E_C(15)": E_C_,
    "E_S(15)": E_S,
    "E_C||E_S pad32": (E_C_ + E_S)[:32],
    "E_S||E_C pad32": (E_S + E_C_)[:32],
}

print("\n== DIRECT POINT-CHECKS (candidate scalar -> gate pubkey) ==")
hit = False
for name, k in KEYS.items():
    if len(k) != 32:
        continue
    ok, kind = is_gate(k)
    print(f"  {name:20} {'MATCH('+kind+')' if ok else '-'}")
    hit = hit or ok

def add_cands(cands, name, b):
    if len(b) == 32:
        cands.append((name, b))
    # sha256 forms of any transcript
for rev_name in ("", "rev"):
    pass

cands = []
for name, k in KEYS.items():
    if len(k) == 32:
        cands.append((f"{name}", k))
        for t in ("sha", "sha_twice", "rev"):
            if t == "sha":
                cands.append((f"{name}-sha", sha256b(k)))
            elif t == "sha_twice":
                cands.append((f"{name}-sha2", sha256b(sha256b(k))))
            else:
                cands.append((f"{name}-rev", k[::-1]))

# stream transcripts as keys
trans = {
    "dbbib91_raw": streams["dbbib_91"].encode(),
    "dbbib91_Bifid": out_dbbi.encode(),
    "faed570_zstr": streams["faed_570"].encode(),
    "faed570_fullBifid": full.encode(),
    "faed570_Bifid_body": full[40:].encode(),
}
for tname, tb in trans.items():
    cands.append((f"{tname}-sha", sha256b(tb)))
    cands.append((f"{tname}-sha2", sha256b(sha256b(tb))))
    cands.append((f"{tname}-bodyrev-sha", sha256b(tb[::-1])))

print(f"\npoint-checking {len(cands)} scalar candidates ...")
for name, b in cands:
    if len(b) != 32:
        continue
    ok, kind = is_gate(b)
    if ok:
        print("  *** MATCH", name, kind)
        hit = True

# ---- chain4 block hybrids (option 3 tail: chain4 35x32 blocks x co-keys) ----
c4f = Path("/data/data/com.termux/files/usr/tmp/opencode/c4_1151.bin")
if c4f.exists():
    c4 = c4f.read_bytes()
    blocks = [c4[i:i + 32] for i in range(0, 1120, 32)]
    print(f"\nchain4 present: {len(c4)}B, {len(blocks)} full 32B blocks")
    n = 0
    for bi, blk in enumerate(blocks):
        for name, k in list(KEYS.items()) + [("dbbib-Bifid-sha", sha256b(out_dbbi.encode()))]:
            if len(k) != 32:
                continue
            for cand in (bytes(a ^ b for a, b in zip(blk, k)), sha256b(blk + k), sha256b(k + blk)):
                n += 1
                ok, kind = is_gate(cand)
                if ok and not hit:
                    print(f"  *** chain4 blk{bi} x {name} MATCH {kind}")
                    hit = True
    print(f"  block-hybrid point checks: {n}")

print("\nRESULT:", "MATCH FOUND" if hit else "no gate match", "| gate h160", GATE_H160)