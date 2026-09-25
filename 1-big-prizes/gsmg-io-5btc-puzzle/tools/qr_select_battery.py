#!/usr/bin/env python3
"""qr_select_battery.py -- late-__x__. The sQRt ("follow the white rabbit")
CTF technique applied to the GSMG token streams.

Source technique (AFFCTF writeup, ~/gsmg/'sQRt(follow the white rabbit).md'):
  encode the message text as a QR symbol, take its boolean module matrix, and
  use the dark (true) modules as a SELECTOR over a parallel bitstream: scan the
  QR matrix cell by cell; every time a module is true, consume the NEXT input
  token. The consumed sequence (optionally further segmented per QR row) is the
  hidden payload.

Analog applied here (all streams certified, data/finalpage-digit-streams.json):
  payload phrase -> QR module matrix (row-major and column-major flat booleans)
  selector over the certified token streams (dbbib69/dbbib91/faed570/concats,
  fwd+rev). Three selection modes:
    A. positional non-cyclic: keep stream i for i < nmod if module[i] true
    B. positional cyclic:     keep stream i for all i if module[i % nmod] true
    C. sQRt-exact sequential: consume next token once per true module, in QR
       scan order (row-major), both as one long block and segmented per QR row.
  Decodes of each kept sequence: verbatim letters, CANON digit string
  (a=1..i=9), and bigint(base10/CANON digits)->bytes ascii.

Ledger: NO prior row generates a QR matrix over the token streams (QR pixel
audit at tested.md:8591 closed only image-embedded barcodes; matrix-as-mask
rows 3234/11532-11537 used the rabbit grid and color word, never a QR matrix).
Expected-negative structure but a genuinely-untested family.

Usage:
    python3 tools/qr_select_battery.py --selftest
    python3 tools/qr_select_battery.py --gen                # writes candidates
    python3 tools/qr_select_battery.py --both               # selftest + gen + feed both gates
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import qrcode
except ImportError:
    print("need: pkg install python-qrcode  (and pillow for non-matrix paths)")
    sys.exit(1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.loads(Path(os.path.join(ROOT, "data", "finalpage-digit-streams.json")).read_text())

DBBI69 = DATA["dbbib"]
DBBI91 = DATA["dbbib_91"]
FAED = DATA["faed_570"][:570]
CANON = dict(a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, i=9)

STREAMS = {
    "dbbib69": DBBI69,
    "dbbib91": DBBI91,
    "faed570": FAED,
    "dbbib69+faed570": DBBI69 + FAED,
    "faed570+dbbib69": FAED + DBBI69,
}

# payload phrases: puzzle nouns / certified key material in the sQRt frame
PHRASES = [
    "THISISACODE",                          # selftest anchor phrase
    "THISISTHEKEYNOWFOLLOWTHEWHITERABBIT",
    "FOLLOWTHEWHITERABBIT",
    "FOLLOW THE WHITE RABBIT",
    "the seed is planted",
    "THESEEDISPLANTED",
    "THESEEDISPLANTEDWHENOPPOSITESATTRACT",
    "OURFIRSTHINTISYOURLASTCOMMAND",
    "WAKEUPKISSTHEFLOORINGORTHEDOORWAY",
    "HOPEISTHEQUINTESSENTIALHUMANDELUSION",
    "DREAMS",
    "the bitcoin is yours",
    "GSMGIO",
    "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "gsmgio5btcpuzzle",
    "THEPHASEPASSWORD",
    "DBIFHCEG",
    "BANKINGWAR",
    "CA",
    "MATRIX",
]


def qr_matrices(payload: str) -> dict:
    """Return flat boolean module lists: {fit_version: {'row': [...], 'col': [...]}}."""
    out = {}
    for ver in (1, 2, 3, 4, 5, 6, 7):
        try:
            qr = qrcode.QRCode(version=ver, error_correction=qrcode.constants.ERROR_CORRECT_L,
                               box_size=1, border=0)
            qr.add_data(payload, optimize=0)
            qr.make(fit=False)
            m = qr.get_matrix()
        except (ValueError, Exception):
            break
        n = len(m)
        if n * n > 570 * 2:
            break
        row = [cell for r in m for cell in r]
        col = [m[r][c] for c in range(n) for r in range(n)]
        out[ver] = {"row": row, "col": col, "n": n}
    return out


def select_pos_noncyclic(stream: str, mod: list) -> str:
    return "".join(ch for i, ch in enumerate(stream) if i < len(mod) and mod[i])


def select_pos_cyclic(stream: str, mod: list) -> str:
    n = len(mod)
    return "".join(ch for i, ch in enumerate(stream) if mod[i % n])


def select_seq_block(stream: str, mod: list) -> str:
    i = 0
    out = []
    for cell in mod:
        if not cell or i >= len(stream):
            continue
        out.append(stream[i])
        i += 1
    return "".join(out)


def select_seq_rows(stream: str, mod: list, n: int) -> str:
    out = []
    i = 0
    for r in range(n):
        rowset = mod[r * n:(r + 1) * n]
        for cell in rowset:
            if not cell:
                continue
            if i >= len(stream):
                return "".join(out)
            out.append(stream[i])
            i += 1
    return "".join(out)


def bigint_bytes(ds: str) -> bytes:
    if not ds or not all(c.isdigit() for c in ds):
        return b""
    v = int(ds)
    return v.to_bytes((v.bit_length() + 7) // 8, "big")


def decodes(kept: str) -> list:
    if not kept:
        return []
    out = [kept]
    ds = "".join(str(CANON.get(ch, 0)) for ch in kept)
    if ds.isdigit():
        out.append(ds)
        bb = bigint_bytes(ds)
        s = bb.decode("ascii", "replace") if bb else ""
        if s and all(32 <= ord(x) < 127 for x in s):
            out.append(s)
    return out


def gen():
    cands = []
    for phrase in PHRASES:
        for ver, mats in qr_matrices(phrase).items():
            n = mats["n"]
            for fname in ("row", "col"):
                mod = mats[fname]
                for sname in ("dbbib69", "dbbib91", "faed570",
                              "dbbib69+faed570", "faed570+dbbib69"):
                    s = STREAMS[sname]
                    for rev in (False, True):
                        src = s[::-1] if rev else s
                        rtag = "rev" if rev else "fwd"
                        pairs = [
                            (f"A.ncyc.{fname}.{sname}.{rtag}",
                             select_pos_noncyclic(src, mod)),
                            (f"B.cyc.{fname}.{sname}.{rtag}",
                             select_pos_cyclic(src, mod)),
                            (f"C.seq.{fname}.{sname}.{rtag}",
                             select_seq_block(src, mod)),
                            (f"D.rowseq.{fname}.{sname}.{rtag}.v{ver}",
                             select_seq_rows(src, mod, n)),
                        ]
                        for tag, kept in pairs:
                            for d in decodes(kept):
                                cands.append(f"{tag}: '{d}'")
                                cands.append(d)
    return [c for c in dict.fromkeys(cands)
            if c and not any(x in c for x in ("\n", "\r", "\t"))
            and all(32 <= ord(x) < 127 for x in c)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--gen", action="store_true")
    ap.add_argument("--both", action="store_true")
    args = ap.parse_args()

    import qrcode as _q
    _m = _q.QRCode(version=1, box_size=1, border=0)
    _m.add_data("THISISACODE", optimize=0)
    _m.make(fit=False)
    assert len(_m.get_matrix()) == 21
    assert len(DBBI69) == len(DATA["dbbib"]) and len(FAED) == 570
    assert STREAMS["faed570+dbbib69"] == FAED + DBBI69

    if args.selftest:
        mats = qr_matrices("THISISACODE")
        v1 = mats[1]
        assert len(v1["row"]) == 441 == len(v1["col"])
        assert v1["n"] == 21
        assert sum(v1["row"]) > 100
        kept = select_seq_block(FAED, v1["row"])
        assert len(kept) == sum(v1["row"])
        assert select_seq_rows(FAED, v1["row"], 21) == kept
        c = gen()
        assert c and len(c) > 500
        print(f"SELFTEST OK ({len(c)} unique candidates)")
        return 0

    if args.gen:
        c = gen()
        out = os.path.join(os.path.expanduser("~"), "qr_select_cands.txt")
        Path(out).write_text("\n".join(c) + "\n")
        print(f"wrote {len(c)} unique candidates -> {out}")
        return 0

    if args.both:
        assert select_seq_rows(FAED, qr_matrices("THISISACODE")[1]["row"], 21) == select_seq_block(FAED, qr_matrices("THISISACODE")[1]["row"]), "sanity"
        c = gen()
        out = os.path.join(os.path.expanduser("~"), "qr_select_cands.txt")
        Path(out).write_text("\n".join(c) + "\n")
        print(f"SELFTEST+GEN OK ({len(c)} unique candidates)")
        for gate in ("oracle.py", "oracle_dualite.py"):
            print(f"--- {gate} ---")
            r = subprocess.run(["python3", os.path.join(ROOT, "tools", gate),
                                "--selftest"], capture_output=True, text=True)
            print(r.stdout.strip(), r.stderr.strip())
            if r.returncode:
                return r.returncode
        for gate in ("oracle.py", "oracle_dualite.py"):
            print(f"--- {gate} stdin ({len(c)} lines) ---")
            r = subprocess.run(["python3", os.path.join(ROOT, "tools", gate),
                                "--stdin"], input="\n".join(c) + "\n",
                               capture_output=True, text=True)
            print(r.stdout.strip())
            print(r.stderr.strip()[-2000:] if r.stderr.strip() else "")
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())