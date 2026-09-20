#!/usr/bin/env python3
"""Option 2 second layer: the two freshly-certified Bifid outputs as mutual
co-keys (Beaufort/Vigenere) and keyed-alphabet source, bounded small.

Witness: bifid_repro_decoder reproduces faed(570)->BTCSEEDDEOEM... (A1 PASS);
dbbib(91)->Bifid = BDFCDCHLBEBQFCFW... derived here as A2 (lead0_layers).
Only legible-window outputs become scalar candidates (point-checked vs gate).
"""
from __future__ import annotations

import hashlib
import json
import string
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
streams = json.loads((ROOT / "data" / "finalpage-digit-streams.json").read_text())
stored = json.loads((ROOT / "data" / "salphaseion-streams.json").read_text())

import sys
sys.path.insert(0, str(ROOT / "tools"))
from bifid_repro import build_grid, bifid_decrypt  # noqa: E402
from lead0_layers import is_gate, GATE_H160  # noqa: E402

ALPHA = string.ascii_uppercase
grid, pos = build_grid()
U = {c: c.upper() for c in "abcdefghi"}

full = bifid_decrypt("".join(U[c] for c in streams["faed_570"].rstrip("z")), 570, grid, pos)
S = bifid_decrypt("".join(U[c] for c in streams["dbbib_91"]), 91, grid, pos)
assert full[:40] == stored["plaintext_head"], "A1 witness failed"
print("WITNESS A1 pass; S =", S)

KEYWORDS = {"BTCSEED", "MATRIX", "SUMLIST", "ENTER", "LASTWORDS", "PASSWORD",
            "YIN", "YANG", "PRIME", "HALF", "BETTERHALF", "KEY", "ARCHI",
            "COSMIC", "DUALITY", "SEED", "FRIEND", "SOLVE", "SECRET"}


def beaufort_keyed(k, c):
    return ALPHA[(k - c) % 26]


def vc(text, key, mode):
    out = []
    for i, ch in enumerate(text):
        k = ord(key[i % len(key)]) - 65
        c = ord(ch) - 65
        if mode == "beaufort":
            out.append(ALPHA[(k - c) % 26])
        else:
            out.append(ALPHA[(c - k) % 26])
    return "".join(out)


def score(t):
    import re
    words = [w for w in re.sub(r"[^A-Z]", " ", t).split() if len(w) >= 3]
    kw = [w for w in KEYWORDS if w in t]
    return kw, len([w for w in words if len(w) >= 5])


msg_pool = {
    "full": full,
    "body40+": full[40:],
    "head40": full[:40],
    "body7+": full[7:],
}
keys = {
    "S.dbbiBifid91": S,
    "S.rev": S[::-1],
    "S.root": "".join(dict.fromkeys(S)),
    "faedBifidKey40": full[7:40],          # the 33-key DEOEMCK...
    "faedBifidKey33": full[7:40][:33],
    "dbbi.raw": streams["dbbib_91"].upper(),
    "BTCSEED+key": stored["plaintext_head"][:40],
}
con = {}
for mn, m in msg_pool.items():
    for kn, k in keys.items():
        for mode in ("beaufort", "vig"):
            t = vc(m, k, mode)
            kw, longw = score(t)
            if kw or longw >= 2:
                con[f"{mn}<{kn}:{mode}"] = (t, kw, longw)
                print(f"!! {mn} < {kn} [{mode}] kw={kw} long5+={longw}")
                print("   ", t[:180])
print(f"\n{len(con)} legible-window second-layer decodes; {len(msg_pool)*len(keys)*2} total")

if con:
    for tag, (t, kw, longw) in con.items():
        for fld in (t, t[::-1], "".join(sorted(set(t)))):
            h = hashlib.sha256(fld.encode()).digest()
            sn = hashlib.sha256(fld.encode()).hexdigest()[:16]
            ok, kind = is_gate(h)
            print(f"  gate-check sha({tag[:60]}) {sn} ->", "MATCH" if ok else "-")
print("RESULT:", "MATCH" if any(is_gate(hashlib.sha256(f.encode()).digest())[0] for f, *_ in con.values()) else "no gate match")