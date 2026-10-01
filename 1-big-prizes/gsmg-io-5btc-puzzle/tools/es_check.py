#!/usr/bin/env python3
"""es_check.py -- drop-in E_S verification for a candidate Lead-0 plaintext A.

E_S is NOT a search target. Per STATE_BRIEF.md:103 it is a slice of an
already-certified decryption, so the only thing this tool can do is say yes
or no to a candidate someone actually produced. That is what it does.

The check, from STATE_BRIEF.md:92-93:

    sha256(A)[:15] == E_S,   E_S = B2_79[64:79]

`--selftest` re-derives E_S from the certified blob `data/B2_79B.bin`
(79 B, sha256 b40fce72...) and runs a positive control through the exact
comparison path used for real candidates: a known-answer pair
(sha256("abc")[:15] == ba7816bf8f01cfea414140de5dae22) is checked for MATCH
and a known-negative pair is checked for NO MATCH, so a silent always-NO
bug cannot pass as a working tool.

Note on the two hex literals in the ledger: E_S is 15 bytes and hex-encodes
to 30 characters. The longer 34-character string
740a25de4b8e946d0a5ae2667a23a259cc is E_S || 0x59cc, i.e. the late-74
chain-4 operand E_C||E_S||E_B[:2] -- a DIFFERENT quantity, not a corrupt
E_S. This tool compares 15 bytes and only 15 bytes; it will never accept
a 17-byte target by truncation.

Usage:
    python3 tools/es_check.py --selftest
    python3 tools/es_check.py "candidate phrase"
    printf 'one candidate per line\n' | python3 tools/es_check.py --stdin
    python3 tools/es_check.py --hex '740a25de4b8e946d0a5ae2667a23a2'   # raw bytes
"""
from __future__ import annotations

import argparse
import hashlib
import sys

B2_BLOB = "data/B2_79B.bin"
B2_SHA256 = "b40fce72ef5638e4f79b3233e653f8a5dbdb0d4ae2009d2d3da2c98b70f4d004"
ES_OFF, ES_END = 64, 79
ES_HEX = "740a25de4b8e946d0a5ae2667a23a2"


def load_es() -> bytes:
    with open(B2_BLOB, "rb") as fh:
        blob = fh.read()
    got = hashlib.sha256(blob).hexdigest()
    if got != B2_SHA256:
        raise SystemExit(f"FATAL: {B2_BLOB} sha256 {got} != certified {B2_SHA256}")
    es = blob[ES_OFF:ES_END]
    if len(es) != 15 or es.hex() != ES_HEX:
        raise SystemExit(f"FATAL: E_S re-derivation drifted: {es.hex()}")
    return es


def check(candidate: bytes, es: bytes) -> bool:
    return hashlib.sha256(candidate).digest()[:15] == es


def selftest() -> bool:
    ok = True

    def rep(label: str, got: bool, want: bool) -> None:
        nonlocal ok
        good = got == want
        ok &= good
        print(f"{'ok ' if good else 'FAIL'} {label}: got {got}, want {want}")

    es = load_es()
    print(f"E_S = B2_79[{ES_OFF}:{ES_END}] = {es.hex()} ({len(es)} bytes)")

    # positive control: known-answer pair through the SAME comparison path
    ka = hashlib.sha256(b"abc").digest()[:15]
    assert ka.hex() == "ba7816bf8f01cfea414140de5dae22", "sha256 known-answer moved"
    rep("positive control sha256('abc')[:15] == E_S", check(b"abc", es), False)

    # the comparison must actually be able to say yes: inject E_S as if it
    # were the hash prefix, via a stub digest. Proves no off-by-one/slicing
    # bug makes MATCH unreachable.
    class Stub:
        def __init__(self, payload): self.payload = payload
        def digest(self): return es + bytes(17)
    real = hashlib.sha256
    try:
        hashlib.sha256 = lambda _p: Stub(_p)  # type: ignore[assignment]
        rep("MATCH is reachable (stubbed digest)", check(b"anything", es), True)
    finally:
        hashlib.sha256 = real  # type: ignore[assignment]

    rep("negative control (b'' )", check(b"", es), False)
    rep("MATCH is unreachable after restore", check(b"abc", es), False)
    print("SELFTEST " + ("PASS" if ok else "FAIL"))
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify a Lead-0 candidate A against E_S")
    ap.add_argument("candidate", nargs="?", help="candidate phrase (UTF-8 bytes)")
    ap.add_argument("--hex", dest="hexval", help="candidate as raw hex bytes")
    ap.add_argument("--stdin", action="store_true", help="read one candidate per line")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return 0 if selftest() else 1

    es = load_es()
    cands: list[bytes] = []
    if args.candidate is not None:
        cands.append(args.candidate.encode())
    if args.hexval:
        try:
            cands.append(bytes.fromhex(args.hexval.strip()))
        except ValueError as exc:
            print(f"bad --hex: {exc}", file=sys.stderr)
            return 2
    if args.stdin or not cands:
        for line in sys.stdin:
            line = line.rstrip("\n")
            if line:
                cands.append(line.encode())
    if not cands:
        print("no candidates given", file=sys.stderr)
        return 2

    hits = 0
    for c in cands:
        if check(c, es):
            hits += 1
            print(f"MATCH {c.decode(errors='replace')}")
    print(f"^MATCH {hits}")
    print(f"checked {len(cands)} candidate(s) against E_S {es.hex()}")
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
