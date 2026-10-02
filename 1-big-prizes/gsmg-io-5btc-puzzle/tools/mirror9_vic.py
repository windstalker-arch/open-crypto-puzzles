#!/usr/bin/env python3
"""mirror9 battery: the a..i mirror permutation as a NEW stream transform.

Motivation (R-CREATORPARODY-2026-10-02): the cross-solver creator audits recover a
`mirror9` map that turns the rail `HYE` into the dictionary word `BYE` by mapping
H->B, passing non-`a..i` Y through, and fixing E. That map is exactly the MIRROR
of the nine-letter native alphabet:

    a<->i  b<->h  c<->g  d<->f  e<->e

which is the same a..i alphabet our own certified finding ties to the puzzle (the
9 yellow cells == exactly the letters {a..i}, leads.md Note 22 / tested.md S182).
So mirror9 is not an arbitrary borrow: it is the puzzle's own native alphabet
reflected, and the audits use it as a cipher-level map rather than as a word map.

GAP THIS CLOSES: tested.md S54 ("through the looking glass" mirror sweep, 22
candidates, all negative) mirrored STREAM ORDER (whole/within-block/row-order/
transpose) and KEYED SQUARES under faed re-Bifid. It never applied the a..i
mirror PERMUTATION to the stream symbols themselves. The a-i permutation is a
different object: same lengths, same alphabet, every symbol systematically
swapped. Nothing in the ledger covers it.

Only the four NATIVE-alphabet streams can take a permutation at all; object_256 /
odd_pre_reduction are uppercase A-Z and even_stream is BCDE, so a..i is not a
subset of their alphabets and they are excluded (recorded here so the exclusion
is auditable rather than silent).

N is tiny by construction: 4 streams x 2 orderings (as-is / reversed) = 8
permuted streams; each is submitted as a raw password candidate and its
sha256/md5 digests are taken by the oracles.
"""
import hashlib
import re
import json
import pathlib
import subprocess
import sys

BASE = pathlib.Path(__file__).resolve().parents[1]
TOOLS = BASE / "tools"

NAT = "abcdefghi"
MIRROR9 = {c: NAT[::-1][i] for i, c in enumerate(NAT)}
INV = {v: k for k, v in MIRROR9.items()}


def selftest():
    # mirror9 is an involution with e as its only fixed point
    for c in NAT:
        assert MIRROR9[MIRROR9[c]] == c, c
    assert [c for c in NAT if MIRROR9[c] == c] == ["e"]
    # the audits' rail identity: HYE -> ByE (BYE uppercased)
    got = "".join(MIRROR9.get(ch.lower(), ch) for ch in "HYE")
    assert got.upper() == "BYE", got
    # sanity: a known-good stream round-trips under apply+invert
    d = json.loads((BASE / "data" / "finalpage-digit-streams.json").read_text())
    s = d["dbbib_91"]
    assert apply_perm(s, MIRROR9) != s
    assert apply_perm(apply_perm(s, MIRROR9), INV) == s
    print("mirror9 SELFTEST OK")


def apply_perm(stream, perm):
    return "".join(perm.get(ch, ch) for ch in stream)


def main():
    selftest()
    d = json.loads((BASE / "data" / "finalpage-digit-streams.json").read_text())
    native = {
        "dbbib_91": d["dbbib_91"],
        "faed_570": d["faed_570"].rstrip("z"),
        "z_segment_1": d.get("z_segment_1", ""),
        "z_segment_2": d.get("z_segment_2", ""),
    }
    native = {k: v for k, v in native.items() if v}

    cands = {}
    for name, s in native.items():
        for pname, perm in (("mirror9", MIRROR9), ("inverse", INV)):
            ps = apply_perm(s, perm)
            for order, val in (("fwd", ps), ("rev", ps[::-1])):
                for form, cand in (
                    (f"{pname}.{order}", val),
                    (f"{pname}.{order}.upper", val.upper()),
                    (f"{pname}.{order}.z", val + "z"),
                ):
                    cands.setdefault(cand, form)

    lines = [c for c in cands if c]
    out = pathlib.Path("/data/data/com.termux/files/usr/tmp/opencode/mirror9_cands.txt")
    out.write_text("\n".join(lines) + "\n")
    print(f"streams={list(native)}")
    print(f"unique candidates: {len(lines)}")

    for gate in ("oracle.py", "oracle_dualite.py"):
        r = subprocess.run(
            [sys.executable, str(TOOLS / gate), "--selftest"],
            capture_output=True, text=True, cwd=str(TOOLS),
        )
        ok = "SELFTEST OK" in r.stdout or "SELFCERT" in r.stdout
        print(f"{gate} --selftest before: {'PASS' if ok else 'FAIL'}")
        if not ok:
            print(r.stdout[-800:], r.stderr[-400:])
            sys.exit(1)
        r = subprocess.run(
            [sys.executable, str(TOOLS / gate), "--stdin"],
            input="\n".join(lines) + "\n", capture_output=True, text=True, cwd=str(TOOLS),
        )
        out = r.stdout + r.stderr
        # A hit prints "MATCH <address> reading=... priv_hex=... wif=..."; a miss
        # prints exactly "NO MATCH". The oracle exits 0 on any hit and 1 if none
        # matched, so the exit code is the authoritative witness -- do not rely on
        # text parsing alone. Earlier revision counted hits with a .isdigit() test
        # that could never match a real hit line; fixed.
        hit_lines = [ln for ln in out.splitlines() if ln.startswith("MATCH ")]
        n_nomatch = sum(1 for ln in out.splitlines() if ln.strip() == "NO MATCH")
        print(f"{gate}: submitted={len(lines)} exit={r.returncode} "
              f"NO MATCH lines={n_nomatch} HIT lines={len(hit_lines)}")
        for ln in hit_lines:
            # redact key material before echoing (AGENTS.md s3)
            red = re.sub(r"(priv_hex|wif)=\S+", r"\1=<redacted>", ln.strip())
            print("    HIT:", red)
        if r.returncode != 1 or hit_lines:
            print("  !! unexpected oracle outcome; treat as NOT a clean negative")

    for gate in ("oracle.py", "oracle_dualite.py"):
        r = subprocess.run(
            [sys.executable, str(TOOLS / gate), "--selftest"],
            capture_output=True, text=True, cwd=str(TOOLS),
        )
        ok = "SELFTEST OK" in r.stdout or "SELFCERT" in r.stdout
        print(f"{gate} --selftest after: {'PASS' if ok else 'FAIL'}")


if __name__ == "__main__":
    main()
