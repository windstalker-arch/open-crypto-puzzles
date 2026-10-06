#!/usr/bin/env python3
"""
blob_8byte_xcheck.py -- the equivalence WITNESS for the `Salted__` 8-byte-block
sweep, and the thing `blob_8byte_cbc.c`'s header used to claim and never had.

WHY THIS EXISTS. `tools/blob_8byte_cbc.py` and `tools/blob_8byte_cbc.c` are two
implementations of one sweep, and the whole point of the C twin is to let the
framing-(c) sweep be finished as a MEASUREMENT rather than a projection. A clean
sweep is only worth that much if the verifier in the fast path actually fires.
Each file's `--selftest` proves its own cells round-trip in isolation, which is
necessary and not sufficient: both selftests bypass the candidate stream, and
the C file's own header documented a `--cross N` flag that was never implemented
(it silently only limited the candidate range and printed a normal RESULT line,
so a reader could mistake its output for a passed cross-check -- a witness-shaped
line with no witness behind it).

So this tool builds the witness in the only form that can survive a translation
bug: a KNOWN-ANSWER blob. It takes a real passphrase from the real 835,270-entry
candidate wordlist, encrypts a printable plaintext under one chosen cell using
the reference implementation's OWN key derivation, writes the result as a real
`Salted__` file, then requires BOTH implementations to report exactly that
passphrase as a survivor when fed the wordlist prefix that contains it. That
exercises the whole dispatch path neither selftest touches: the stdin arena, the
offset table, candidate ordering, the two IV readings, the PKCS7 final-block gate
and the printability floor.

It also pins the negative control: the same two runs over a prefix with NO
correct candidate must report zero survivors. Without it, "both found it" and
"both flag everything" are indistinguishable.

Read-only with respect to the puzzle: writes one synthetic blob under
analysis/tmp/, contacts no oracle, no gate, no network. The blob it writes is its
own construction and carries no puzzle bytes.

Usage:
    python3 tools/blob_8byte_xcheck.py --selftest      # self-checks of this file
    python3 tools/blob_8byte_xcheck.py --run           # build + run both twins
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from blob_8byte_cbc import (  # noqa: E402
    FAMILY, ROOT, cells_for, key_for, make_enc, printable_ratio, sweep,
)

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(ROOT, "analysis", "tmp", "wl")
XCHECK_BLOB = os.path.join(TMP, "xcheck_8byte.bin")
CBIN = os.path.join(ROOT, "tools", "build", "blob_8byte_cbc")

# The planted passphrase is a real entry of the real wordlist, chosen by index so
# the witness depends on the candidate stream rather than on a hand-written
# string that only this file knows about.
PLANT_INDEX = 137
WORDLIST = os.path.join(HERE, "gsmg_wordlist.py")

# One cell, chosen to exercise the less-travelled branch: 3-key 3DES at keylen 24
# with the EVP-MD5 stream KDF. blast5 at 16 and des at 8 share key/IV length
# handling with AES in ways a 24-byte 3DES key does not.
CELL = {"kdf": "evp-md5", "alg": "des-ede3", "klen": 24, "iv_reading": 0}

PLAINTEXT = (b"XCHECK-KNOWN-ANSWER: this plaintext is printable ASCII only, "
             b"so a correct key clears the printability floor and nothing else "
             b"does. ")
BS = 8


def wordlist(n):
    out = subprocess.run([sys.executable, WORDLIST], capture_output=True,
                         timeout=3600).stdout
    cands = [ln for ln in out.split(b"\n") if ln]
    seen, uniq = set(), []
    for c in cands:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq[:n]


def build_blob(pw, salt):
    """Encrypt under the reference implementation's own cell convention."""
    cells = cells_for(pw, salt, CELL["klen"], CELL["kdf"], ivlen=8)
    key, iv = cells[CELL["iv_reading"]]
    pad = BS - (len(PLAINTEXT) % BS)
    pt = PLAINTEXT + bytes([pad]) * pad
    enc = make_enc(CELL["alg"])(key, iv).encrypt
    ct = enc(pt)
    return b"Salted__" + salt + ct, pt


def run_python(prefix_n, path):
    r = subprocess.run(
        [sys.executable, os.path.join(HERE, "blob_8byte_cbc.py"),
         "--path", path, "--framing", "c", "--limit", str(prefix_n)],
        capture_output=True, text=True, timeout=7200)
    return r.stdout + r.stderr, r.returncode


def run_c(prefix_n, path):
    """Feed the SAME prefix on stdin, which is the path the real sweep uses."""
    with open(os.path.join(TMP, "xcheck_prefix.txt"), "rb") as f:
        data = f.read()
    r = subprocess.run(
        [CBIN, "--path", path, "--framing", "c"],
        input=data, capture_output=True, timeout=7200)
    return r.stdout.decode() + r.stderr.decode(), r.returncode


def survivors(text):
    """Parse both twins' two-line SURVIVOR records into (pw, r, plaintext).

    The Python twin renders the plaintext as `    b'...'` and the C twin as
    `    "..."`; both are literal-evaluable, which is why the C twin was changed to
    print it at all (it used to print the passphrase only, so a hit found by the
    fast path arrived with nothing to read).
    """
    out = []
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if "SURVIVOR" not in ln or " pw=" not in ln:
            continue
        r = float(re.search(r"r=([0-9.]+)", ln).group(1))
        pw = ln.split(" pw=", 1)[1].strip()
        if pw.startswith("b'") or pw.startswith('b"'):
            pw = ast.literal_eval(pw)          # python twin -> bytes
        else:
            pw = pw.encode()                    # C twin -> str, normalise
        pt = b""
        if i + 1 < len(lines) and lines[i + 1].startswith("    "):
            lit = lines[i + 1].strip()
            try:
                pt = ast.literal_eval(lit if lit[0] in "b" else '"' + lit[1:])
            except (SyntaxError, ValueError):
                pt = b""
        out.append((pw, r, pt))
    return out


def selftest() -> int:
    """This file's own self-checks, before it is trusted with anyone else's data."""
    fails = 0

    # 1. The planted passphrase really is in the real wordlist at PLANT_INDEX.
    wl = wordlist(PLANT_INDEX + 1)
    if len(wl) != PLANT_INDEX + 1:
        print(f"  FAIL wordlist shorter than PLANT_INDEX ({len(wl)})")
        fails += 1
    else:
        pw = wl[PLANT_INDEX]
        print(f"  wordlist[{PLANT_INDEX}] = {pw!r}")

    # 2. The built blob round-trips through the reference implementation, pad
    #    check included -- so a later MISS is the twins' fault, not the builder's.
    salt = bytes(range(16, 32))
    blob, pt = build_blob(pw, salt)
    if blob[:8] != b"Salted__" or len(blob) != 24 + len(pt):
        print(f"  FAIL blob layout: magic={blob[:8]!r} len={len(blob)}")
        fails += 1
    if (len(blob) - 24) % BS:
        print("  FAIL ciphertext is not a whole number of 8-byte blocks")
        fails += 1
    hits, _ = sweep([pw], salt, blob[24:], [CELL["kdf"]], bs=BS, padded=True,
                    verbose=False)
    if not hits:
        print("  FAIL reference sweep cannot re-find its own construction")
        fails += 1
    else:
        r, kdf, alg, klen, hpw, hpt = max(hits, key=lambda h: h[0])
        if hpw != pw or not hpt.startswith(PLAINTEXT):
            print(f"  FAIL reference re-found the wrong thing: {hpw!r}")
            fails += 1
        else:
            print(f"  reference re-find OK: r={r:.3f} kdf={kdf} alg={alg} "
                  f"klen={klen} print={printable_ratio(hpt):.3f}")

    # 3. A wrong passphrase must NOT survive, i.e. the gate is not a sieve.
    hits2, _ = sweep([b"definitely-not-the-passphrase"], salt, blob[24:],
                     [CELL["kdf"]], bs=BS, padded=True, verbose=False)
    if hits2:
        print(f"  FAIL a wrong key survived {len(hits2)} time(s) -- the gate leaks")
        fails += 1
    else:
        print("  wrong-key negative control OK: 0 survivors")

    print(f"\nXCHECK SELFTEST {'PASS' if not fails else 'FAIL'} -- "
          f"{'no' if not fails else fails} check(s) failed")
    return 1 if fails else 0


def run() -> int:
    os.makedirs(TMP, exist_ok=True)
    wl = wordlist(PLANT_INDEX + 1)
    pw = wl[PLANT_INDEX]
    salt = bytes(range(16, 32))
    blob, pt = build_blob(pw, salt)
    with open(XCHECK_BLOB, "wb") as f:
        f.write(blob)
    prefix_n = PLANT_INDEX + 1
    with open(os.path.join(TMP, "xcheck_prefix.txt"), "wb") as f:
        f.write(b"\n".join(wl) + b"\n")

    print(f"known-answer blob: {XCHECK_BLOB} ({len(blob)} B, ciphertext "
          f"{len(blob) - 24} B, ct%16={(len(blob) - 24) % 16})")
    print(f"planted passphrase: {pw!r} at wordlist index {PLANT_INDEX} "
          f"(prefix of {prefix_n} candidates)")
    print(f"cell: kdf={CELL['kdf']} alg={CELL['alg']} klen={CELL['klen']} "
          f"iv_reading={CELL['iv_reading']}")

    py_out, py_rc = run_python(prefix_n, XCHECK_BLOB)
    c_out, c_rc = run_c(prefix_n, XCHECK_BLOB)
    py_hits, c_hits = survivors(py_out), survivors(c_out)

    print("\n--- python twin ---")
    print(py_out.strip())
    print("--- C twin ---")
    print(c_out.strip())

    ok = True
    parsed = {}
    for name, hits, rc in (("python", py_hits, py_rc), ("C", c_hits, c_rc)):
        parsed[name] = hits
        if rc != 0:
            print(f"FAIL {name} twin exited {rc}")
            ok = False
        if not hits:
            print(f"FAIL {name} twin reported 0 survivors -- the known-answer "
                  f"blob was not re-found, so the sweep's negative is worthless")
            ok = False
            continue
        wrong = [h for h in hits if h[0] != pw]
        if wrong:
            print(f"FAIL {name} twin reported {len(wrong)} survivor(s) that are "
                  f"not the planted passphrase: {wrong}")
            ok = False
        else:
            print(f"WITNESS OK ({name} twin re-found the planted passphrase "
                  f"through the stdin path, {len(hits)} IV reading(s))")

    # The twins must agree on the SET OF PASSPHRASES. Their lines differ in
    # algorithm spelling (des-ede3 vs DES-EDE3-CBC) and quoting, so comparing
    # raw lines would report a false divergence.
    if parsed.get("python") and parsed.get("C"):
        if {h[0] for h in parsed["python"]} != {h[0] for h in parsed["C"]}:
            print(f"FAIL the twins disagree on the survivor set: "
                  f"{[h[0] for h in parsed['python']]} vs "
                  f"{[h[0] for h in parsed['C']]}")
            ok = False
        else:
            print("TRANSLATION OK (both twins report the same passphrase set)")

    # INVARIANT, and the most useful thing this tool found. In CBC the IV enters
    # only the first block: P1 = D(C1) XOR IV, and every later block uses the
    # ciphertext as its IV. So the two IV readings, given the right key, must
    # return plaintexts that DISAGREE on block 1 and AGREE byte-for-byte from
    # offset BS onward. Checking it turns the twin-survivor pair from a mystery
    # into a certified property -- and it is also the reason a printability floor
    # is nearly vacuous for these blobs: with an 88-to-4088-byte ciphertext, the
    # first block is 0.9%-9% of the text, so a correct key clears 0.90 under a
    # WRONG IV anyway. The floor filters wrong keys, not wrong IVs.
    for name, hits in parsed.items():
        if len(hits) >= 2 and all(h[2] for h in hits):
            agree = all(h[2][BS:] == hits[0][2][BS:] for h in hits)
            head_diff = all(h[2][:BS] != hits[0][2][:BS]
                             for h in hits[1:])
            if agree and head_diff:
                print(f"INVARIANT OK ({name} twin: the {len(hits)} survivors "
                      f"differ only in block 1 and agree from byte {BS} on)")
            else:
                print(f"FAIL {name} twin: survivors agree_from_bs={agree} "
                      f"heads_differ={head_diff}, which the CBC IV property "
                      f"forbids")
                ok = False

    # Negative control: same prefix, but a blob no candidate in it can open.
    ctrl = os.path.join(TMP, "xcheck_control.bin")
    with open(ctrl, "wb") as f:
        f.write(build_blob(b"a-passphrase-not-in-any-wordlist", salt)[0])
    for name, fn in (("python", run_python), ("C", run_c)):
        out, rc = fn(prefix_n, ctrl)
        hits = survivors(out)
        if hits or rc != 0:
            print(f"FAIL {name} negative control produced {len(hits)} survivor(s)"
                  f" rc={rc}")
            ok = False
        else:
            print(f"NEGATIVE CONTROL OK ({name} twin: 0 survivors on a blob no "
                  f"candidate opens)")

    print(f"\nXCHECK {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        raise SystemExit(selftest())
    raise SystemExit(run())