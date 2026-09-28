#!/usr/bin/env python3
"""sticker_column_combine.py -- late-276.

The 8 theseedisplanted strips render as two text rows. "Combine the text on
the same line position" = for each horizontal column, join the top-row and
bottom-row symbols. This generator emits every such positional combination
plus the user's own reading-out-loud, for the certified oracles.

Rows (from the strip file names, /theseedisplanted page order):
  TOP    : BLACK(banking-war) blue_ca blue_dig_i blue_lock_lo
  BOTTOM : red_crypto_gic red_n_you red_open_lock_n_ing red_t
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TOP = ["bankingwar", "ca", "digi", "locklo"]
BOT = ["cryptogic", "nyou", "openlocking", "t"]


def clean(s: str) -> str:
    return "".join(c for c in s if c.isalnum() or c in "+-")


def pairs(t: str, b: str) -> list[str]:
    n = max(len(t), len(b))
    t = t.ljust(n)
    b = b.ljust(n)
    return [t[i] + b[i] for i in range(n)]


def cands() -> dict[str, str]:
    out = {}
    tt = "".join(TOP)
    bb = "".join(BOT)
    out["row_top_concat"] = tt
    out["row_bot_concat"] = bb
    out["bot_then_top"] = bb + tt
    out["top_then_bot"] = tt + bb
    for name, fn in (("col_inter_then_b", lambda: "".join(pairs(tt, bb))),
                     ("col_inter_b_then_t", lambda: "".join(p[1] + p[0] for p in pairs(tt, bb))),
                     ("cols_space", lambda: " ".join(pairs(tt, bb)))):
        out[name] = fn()
    user = ["canyou", "lock", "wallet", "unlock", "digit", "warning"]
    for tag, toks in (("user_compact", user),
                      ("user_plusminus", user + ["+-"]),
                      ("user_plusminusword", user + ["plusminus"]),
                      ("user_ca_upper", ["CA", "n", "you", "lock", "wallet", "unlock", "dig", "it", "warning", "+-"])):
        out[tag] = "".join(toks)
    # late-276-fix: user corrected reading (2026-09-20) - "dig it logic" = digital-logic family
    for tag, head in (("fix_logic", ["canyou", "lock", "wallet", "unlock", "dig", "it", "logic", "warning"]),
                      ("fix_digitallogic", ["canyou", "lock", "wallet", "unlock", "digitallogic", "warning"]),
                      ("fix_digital_logic", ["canyou", "lock", "wallet", "unlock", "digital", "logic", "warning"]),
                      ("fix_digital", ["canyou", "lock", "wallet", "unlock", "digital", "warning"])):
        out[tag] = "".join(head)
        out[tag + "_pm"] = "".join(head + ["+-"])
        out[tag + "_pmw"] = "".join(head + ["plusminus"])
    return out


def main() -> int:
    cs = cands()
    forms = set()
    for tag, c in cs.items():
        for v in (c, c.lower(), c.upper(), c.replace("+-", " plus minus ").lower().replace(" ", "")):
            forms.add(v)
            forms.add(v[::-1])
    out_path = os.path.join(os.path.expanduser("~"), "sticker_column_cands.txt")
    with open(out_path, "w") as f:
        f.writelines(x + "\n" for x in sorted(forms))
    print(f"[sticker_column_combine] {len(cs)} generators -> {len(forms)} forms -> {out_path}")
    for prog in ("oracle.py", "oracle_dualite.py"):
        p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", prog), "--stdin"],
                           stdin=open(out_path), capture_output=True, text=True)
        lines = [l for l in p.stdout.splitlines() if l.strip()]
        print(f"[sticker_column_combine] {prog}: {lines[-1] if lines else 'NO MATCH'}")
        # A real hit prints a line STARTING with "MATCH ". Substring tests are
        # wrong both ways: bare `"MATCH" in stdout` fires on "NO MATCH", while
        # `and "NO MATCH" not in stdout` suppresses a genuine hit in a batch.
        if any(l.startswith("MATCH ") for l in lines):
            print(p.stdout)
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())