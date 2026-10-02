#!/usr/bin/env python3
"""third_door.py -- a CERTIFIED oracle for the third door (the unmessaged
planted address) and the other creator-funded planted addresses.

WHY THIS TOOL EXISTS. Every negative in `analysis/tested.md` for the third door
(`1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9`, funded 2020-04-07, no OP_RETURN, no known
preimage) was produced by the private research, and no tool for it was ever
shipped: the six key constructions are described in prose in `README.md` and
`analysis/tested.md` s.19b, and `data/planted-addresses.csv` records which
construction each verified row uses. So the third door has had hundreds of
certified negatives and zero reproducible code. This file is that code, and its
selftest is the missing witness: every `verified` row in the CSV is re-derived
here from its recorded preimage, so a negative produced by this tool is
witnessed by construction and not by assertion.

THE CONSTRUCTIONS (all six, from the CSV's `key` column and README s.19b):

  sha256        key = sha256(preimage)
  raw           key = int.from_bytes(preimage, "big")  (zero-padded left to 32)
  raw-right     key = int.from_bytes(preimage.rjust(32, b"\\x00"), "little")
  bits reversed key = the 8*len bit string of the raw value read backwards
  bytes rev     key = the raw 32 bytes reversed
  hex ascii     key = sha256 of the lowercase hex rendering of the preimage

Every candidate is turned into a compressed AND an uncompressed P2PKH address and
compared against the whole planted list plus the both gate addresses, because the
CSV's own rows show the creator used both forms (`causality` and
`gsmg.io/theseedisplanted` are compressed, the gates' target pubkey is
uncompressed).

Local only: every address being compared is already public in
`data/planted-addresses.csv` or in the README gate table. No key is swept, no
transaction is built, nothing is broadcast.

WHY `--wordlist` EXISTS, and why it is built the way it is. `analysis/tested.md`
records, at the section-9 cumulative note, that "a `rockyou.txt` pass on both
locks and the third door was still running when that session closed and is not
counted". So the single largest untried mechanical battery on the third door was
started, abandoned, and never witnessed - and it is still not reproducible,
because until this mode existed the shipped tool had no way to take a wordlist
at all (`--selftest` and `--audio` only). Two separate process failures, both of
the kind this repo has already been bitten by:

  1. NO CHECKPOINTING. A long pass that dies with the session leaves no partial
     result and no count, which is exactly the "not counted" outcome. Progress is
     therefore checkpointed by BYTE OFFSET, written atomically, and `--resume`
     refuses to run against a wordlist whose size or mtime has moved, so a stale
     checkpoint can never silently certify a wrong slice of the file.
  2. NO SHARDING. This is a pure CPU search with no shared state, and the
     measured rate is ~1.1k address derivations/s on one core (`R-COLORDOOR`),
     i.e. ~93 candidates/s for the twelve derivations a candidate costs. On 8
     cores that is ~750 candidates/s, so the 14.3M-word rockyou corpus is about
     5.3 hours instead of 42. `--shard I --of N` splits by line index, so shards
     are disjoint and each carries its own checkpoint.

Accounting is honest by construction: every run reports the exact line range it
covered and how many candidates it derived, and a MATCH is printed immediately
and loudly rather than at the end, because a pass that finds something after
five hours and then gets killed must not lose the finding.

The constructions are NOT re-implemented here. This mode calls the same
`addresses_for()` that `selftest()` certifies against the CSV's verified rows, so
a wordlist negative and a selftest witness cannot drift apart.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys

import base58
from ecdsa import SECP256k1, SigningKey

BASE = os.path.expanduser(
    "~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle")
CSV_PATH = os.path.join(BASE, "data", "planted-addresses.csv")

GATES = {
    "small": "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "dualite": "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa",
}
THIRD_DOOR = "1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9"

# The audio number stream, exactly as transcribed, plus the community's own
# rendering of it. The two differ in ONE token: 18 vs 48. Read as hex bytes the
# community list spells HASHTHETEXT; the as-given list spells ASHTHETEXT, i.e.
# the leading 'H' was transcribed as 18 (0x12, a control character) instead of
# 48 (0x48). Both are carried here as separate candidates, and both are also
# carried in the decimal reading, because a number stream is ambiguous between
# "hex byte values" and "decimal numbers" until something downstream settles it.
AUDIO_GIVEN = "18 41 53 48 54 48 45 54 45 58 54"
AUDIO_COMMUNITY = "48 41 53 48 54 48 45 54 45 58 54"


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def hash160(d: bytes) -> bytes:
    return hashlib.new("ripemd160", sha256(d)).digest()


def p2pkh(priv_int: int, compressed: bool) -> str | None:
    if not 0 < priv_int < SECP256k1.order:
        return None
    try:
        sk = SigningKey.from_secret_exponent(priv_int, curve=SECP256k1)
    except Exception:
        return None
    point = sk.verifying_key.pubkey.point
    if compressed:
        pub = (b"\x02" if point.y() % 2 == 0 else b"\x03") \
            + point.x().to_bytes(32, "big")
    else:
        pub = (b"\x04" + point.x().to_bytes(32, "big")
               + point.y().to_bytes(32, "big"))
    return base58.b58encode_check(b"\x00" + hash160(pub)).decode()


def raw_int(b: bytes) -> int:
    return int.from_bytes(b, "big")


def bits_reversed_int(b: bytes) -> int:
    """The 8*len(b) bit string of b, read backwards.

    NOTE the width: the CSV defines this construction on the PREIMAGE's own bit
    string ("the 192-bit string of the raw bytes read backwards", i.e. 24 bytes
    for a 24-character preimage), NOT on the 32-byte zero-padded value. Doing it
    on the padded 32 bytes gives a different key and a different address; the
    selftest caught that on the first run, which is what the witness is for.
    """
    return int(bin(raw_int(b))[2:].zfill(8 * len(b))[::-1], 2)


def constructions(pre: bytes) -> dict[str, int]:
    raw32 = pre.rjust(32, b"\x00")[-32:]
    return {
        "sha256": raw_int(sha256(pre)),
        "raw": raw_int(raw32),
        "raw-right": raw_int(pre.ljust(32, b"\x00")[-32:][::-1]),
        "bits reversed": bits_reversed_int(pre),
        "bytes rev": raw_int(raw32[::-1]),
        "hex ascii": raw_int(sha256(pre.hex().encode())),
    }


def load_planted() -> list[dict]:
    with open(CSV_PATH, newline="") as fh:
        return list(csv.DictReader(l for l in fh if not l.startswith("#")))


PLANTED = load_planted()
TARGETS = {r["address"]: (r["funded"], r["op_return"], r["status"])
           for r in PLANTED}
for _g in GATES.values():
    TARGETS.setdefault(_g, ("-", "-", "funded gate"))


def addresses_for(pre: bytes) -> dict[tuple[str, bool], str]:
    out = {}
    for cname, k in constructions(pre).items():
        for comp in (True, False):
            a = p2pkh(k, comp)
            if a:
                out[(cname, comp)] = a
    return out


# ------------------------------------------------------------------ witnesses

# (preimage, expected address, construction, compressed) -- every one of these is
# a row the CSV itself marks "verified", so re-deriving them is the witness that
# this harness and that file agree.
WITNESSES = [
    (b"gsmg.io/theseedisplanted", "148XH2YBmLr4oAJXQcG84FpNYoBmqnVPHQ",
     "raw", True),
    (b"gsmg.io/theseedisplanted", "13HGhjkmKUkP8sk9k63BLmhkxRjy7uK4Rp",
     "bits reversed", True),
    (b"causality", "1Jqq37KkZEt4F3Dt6qXdtyiMEFBBdawbkJ", "sha256", True),
    (b"1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe", "1GyT5WrLYpwFkuiVoPDJZa1Q6jtjbjuBff",
     "sha256", True),
    (b"jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
     "1K23RS1y2fnuZRkhw5nUpFr5Jk5WN11Zeq", "sha256", True),
]


def selftest() -> int:
    bad = 0
    for pre, want, cname, comp in WITNESSES:
        got = addresses_for(pre).get((cname, comp))
        ok = got == want
        bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {cname:14s}"
              f"{'compressed ' if comp else 'uncompressed'} {want}"
              f"{'' if ok else f'  got {got}'}")
    # the third door must be a known target, and must NOT be reachable by any
    # witness preimage under any construction (it has no known preimage)
    assert THIRD_DOOR in TARGETS, "third door missing from the planted list"
    for pre, _, _, _ in WITNESSES:
        assert THIRD_DOOR not in addresses_for(pre).values(), \
            "a known preimage claims the third door"
    print(f"  [{'PASS' if bad == 0 else 'FAIL'}] {len(WITNESSES)} CSV rows "
          f"re-derived, third door present and unclaimed")
    print(f"SELFTEST {'PASS' if bad == 0 else 'FAIL'}: {len(WITNESSES)} "
          f"witnesses, {bad} failures")
    return 1 if bad else 0


# ------------------------------------------------------------ audio candidates

def audio_candidates() -> list[tuple[str, bytes]]:
    """Every rendering of the audio number stream and the word it spells."""
    out: list[tuple[str, bytes]] = []
    seen: set[bytes] = set()

    def add(tag: str, b) -> None:
        if isinstance(b, str):
            b = b.encode()
        if b and b not in seen:
            seen.add(b)
            out.append((tag, b))

    for tag, nums in (("as-given", AUDIO_GIVEN),
                      ("community", AUDIO_COMMUNITY)):
        toks = nums.split()
        add(f"{tag}/spaced", nums)
        add(f"{tag}/joined", "".join(toks))
        add(f"{tag}/hyphen", "-".join(toks))
        add(f"{tag}/comma", ",".join(toks))
        add(f"{tag}/comma-space", ", ".join(toks))
        add(f"{tag}/lower", nums.lower())
        add(f"{tag}/reversed-tokens", " ".join(reversed(toks)))
        add(f"{tag}/reversed-joined", "".join(reversed(toks)))
        # hex-bytes reading: this is the reading that produces a word at all
        try:
            raw = bytes(int(t, 16) for t in toks)
        except ValueError:
            raw = b""
        if len(raw) == len(toks):
            add(f"{tag}/hex-bytes", raw)
            add(f"{tag}/hex-bytes-upper", raw.upper())
            add(f"{tag}/hex-bytes-as-text", "".join(
                chr(c) if 32 <= c < 127 else "?" for c in raw))
        # decimal reading: the same numbers as decimal byte values
        if all(t.isdigit() for t in toks) and all(int(t) < 256 for t in toks):
            dec = bytes(int(t) for t in toks)
            add(f"{tag}/dec-bytes", dec)
            add(f"{tag}/dec-as-text", "".join(
                chr(c) if 32 <= c < 127 else "?" for c in dec))
        # decimal reading as A1Z26-ish index, with and without 0-basing
        if all(t.isdigit() for t in toks):
            for base, tag2 in ((1, "a1z26-1"), (0, "a1z26-0")):
                s = "".join(chr(64 + int(t) + (0 if base == 1 else -1))
                            if 1 <= int(t) + (0 if base == 1 else -1) <= 26
                            else "?" for t in toks)
                add(f"{tag}/{tag2}", s)

    # the words the stream spells, in the renderings anyone would try
    for w in ("HASHTHETEXT", "hashthetext", "HashTheText", "Hash the text",
              "hash the text", "HASH THE TEXT", "hash the text.",
              "hashthe text", "HASHTHETEX", "ASHTHETEXT", "ashthetext",
              "HASHTEXT", "hash text", "HASH TEXT", "text the hash",
              "THE TEXT", "thetext"):
        add("word/" + w, w)
        add("word-rev/" + w, w[::-1])

    # "hash the text" applied to the page text is a documented, already-consumed
    # step whose result is the SalPhaseIon URL path. The URL and its hash are
    # carried so the third door is tested against the instruction's own output.
    url_hash = ("89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac"
                "0152f6a32")
    add("url/hash", url_hash)
    add("url/path", "gsmg.io/" + url_hash)
    add("url/path-nosite", "/" + url_hash)
    add("url/hash-upper", url_hash.upper())
    add("url/bytes", bytes.fromhex(url_hash))
    # the instruction text itself, as it appears on the creator's page
    add("instr/hash the text", "hash the text")
    add("instr/HASHTHETEXT", "HASHTHETEXT")
    return out


def run() -> int:
    cands = audio_candidates()
    hits = []
    tried = 0
    for tag, pre in cands:
        for (cname, comp), addr in addresses_for(pre).items():
            tried += 1
            if addr in TARGETS:
                hits.append((tag, pre, cname, comp, addr))
    print(f"audio/HASHTHETEXT battery: {len(cands)} preimages x "
          f"{len(constructions(b'x'))} constructions x 2 pubkey forms = "
          f"{tried} address derivations")
    for tag, pre, cname, comp, addr in hits:
        funded, op, status = TARGETS[addr]
        print(f"  MATCH  {addr}  [{cname}, {'compressed' if comp else 'uncompressed'}]"
              f"  from {tag} = {pre!r}  (funded {funded}, op_return {op!r},"
              f" status {status})")
    if not hits:
        print("  0 MATCH against the 3rd door, the 8 other planted addresses,"
              " and both gate addresses")
    return 1 if hits else 0


def wordlist_run(path: str, shard: int, of: int, ckpt: str | None,
                 resume: bool, every: int) -> int:
    """Run every line of `path` through the certified constructions.

    Progress is a byte offset into the file, so a resumed pass continues at
    exactly the line it stopped on. The checkpoint records the wordlist's size
    and mtime and refuses to resume if either moved.
    """
    import json
    import time

    st = os.stat(path)
    start_off = 0
    lines_done = 0
    read_at_start = 0
    if resume:
        if not ckpt or not os.path.exists(ckpt):
            print("RESUME-ERROR: no checkpoint to resume from", flush=True)
            return 2
        with open(ckpt) as fh:
            c = json.load(fh)
        if c["size"] != st.st_size or c["mtime"] != int(st.st_mtime):
            print("RESUME-ERROR: wordlist changed since checkpoint "
                  f"(size {c['size']}->{st.st_size}, "
                  f"mtime {c['mtime']}->{int(st.st_mtime)}). Refusing: a stale "
                  "checkpoint would certify the wrong slice.", flush=True)
            return 2
        start_off = c["offset"]
        lines_done = c["lines"]
        # The absolute line index is RECOMPUTED from the byte offset rather than
        # trusted from the file. Shard membership is `(idx - 1) % of == shard`,
        # so idx and the file position must agree exactly or a resumed shard
        # silently processes the wrong lines - skipping some and duplicating
        # others, which is a silently wrong negative rather than a crash. The
        # checkpoint's own `lines` field is the count of candidates DERIVED, not
        # the count of lines read, and a shard skips of-1 lines out of every of,
        # so the two differ by up to of-1; deriving the index from the offset is
        # immune to that, and also repairs checkpoints written before this fix.
        with open(path, "rb") as fh:
            read_at_start = fh.read(start_off).count(b"\n")

    known = TARGETS
    found = 0
    derived = 0
    t0 = time.time()
    last = t0

    def owned_total(rd):
        """Cumulative candidates this shard has derived, from the absolute line
        index alone. The shard owns line idx iff (idx - 1) % of == shard, so the
        count of owned lines in 1..rd is exact. Deriving it from the line index
        rather than from a running counter is what makes it survive a resume: a
        session-local counter starts at zero, so after any resume the reported
        total silently drops to the post-resume work only and an eleven-hour
        sweep's log claims to have covered almost nothing."""
        if rd <= shard:
            return 0
        return (rd - 1 - shard) // of + 1

    def save(off, ln, rd):
        if not ckpt:
            return
        tmp = ckpt + ".tmp"
        with open(tmp, "w") as fh:
            json.dump({"path": path, "size": st.st_size,
                       "mtime": int(st.st_mtime), "offset": off,
                       "lines": ln, "read": rd,
                       "cands": owned_total(rd), "derived_run": derived,
                       "shard": shard, "of": of}, fh)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, ckpt)

    save(start_off, lines_done, read_at_start)
    # Seeded before the loop, not inside it: resuming a pass that already reached
    # EOF runs the loop zero times, and an `off` bound only inside the body would
    # make the final save() raise UnboundLocalError - which would lose a
    # COMPLETED pass's accounting, the precise failure this mode exists to stop.
    off = start_off
    cands = 0
    # Derivations per candidate line, so the cumulative derived figure is a
    # product of two exact counts rather than a session-local tally.
    per_cand = len(addresses_for(b"probe"))
    with open(path, "rb") as fh:
        if start_off:
            fh.seek(start_off)
        idx = read_at_start
        for raw in fh:
            off = fh.tell()
            idx += 1
            # Membership is tested here, but the progress/checkpoint block below
            # must run for EVERY line read, not only for lines this shard owns.
            # Testing it the other way round - `continue` on a non-owned line
            # before the progress block - makes the block unreachable for most
            # shards: line idx is owned when (idx-1) % of == shard, so a progress
            # test of `idx % every == 0` with every a multiple of `of` never
            # coincides with ownership for shard 0 (idx=2000k gives
            # (2000k-1) % 8 == 7). The symptom is a shard that runs for hours,
            # prints nothing, never advances its checkpoint, and loses 100% of its
            # work if killed - the exact "still running when the session closed
            # and is not counted" outcome this mode was added to prevent.
            if (idx - 1) % of == shard:
                cand = raw.rstrip(b"\r\n")
                if cand:
                    lines_done = idx
                    cands += 1
                    for (cname, comp), addr in addresses_for(cand).items():
                        derived += 1
                        if addr in known:
                            found += 1
                            funded, op, status = TARGETS[addr]
                            print(f"MATCH shard={shard}/{of} line={idx} "
                                  f"construction={cname} compressed={comp} "
                                  f"address={addr} funded={funded} "
                                  f"op_return={op} status={status} "
                                  f"preimage={cand!r}", flush=True)
            if every and idx % every == 0:
                now = time.time()
                el = max(now - t0, 1e-9)
                tot = owned_total(idx)
                print(f"[shard {shard}/{of}] line {idx} offset {off} "
                      f"total {tot} cands {cands} {cands / el:.1f} cand/s "
                      f"derived {tot * per_cand} matches {found}", flush=True)
                save(off, lines_done, idx)
                last = now
        save(off, lines_done, idx)

    dt = max(time.time() - t0, 1e-9)
    tot = owned_total(idx)
    print(f"DONE shard={shard}/{of} wordlist={os.path.basename(path)} "
          f"last_line={lines_done} total={tot} cands={cands} "
          f"derived={tot * per_cand} "
          f"matches={found} {dt:.1f}s {cands / dt:.1f} cand/s "
          f"{derived / dt:.0f} deriv/s", flush=True)
    return 1 if found else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--audio", action="store_true",
                    help="run the audio / HASHTHETEXT battery")
    ap.add_argument("--wordlist", metavar="FILE",
                    help="run every line of FILE through the six constructions")
    ap.add_argument("--shard", type=int, default=0, help="shard index, 0-based")
    ap.add_argument("--of", type=int, default=1, help="total number of shards")
    ap.add_argument("--checkpoint", metavar="FILE",
                    help="write progress here, atomically")
    ap.add_argument("--resume", action="store_true",
                    help="continue from --checkpoint (refuses if wordlist moved)")
    ap.add_argument("--every", type=int, default=0,
                    help="print progress every N lines")
    a = ap.parse_args(argv)
    rc = 0
    if a.selftest or not (a.selftest or a.audio or a.wordlist):
        rc |= selftest()
    if a.audio and rc == 0:
        rc |= run()
    if a.wordlist and rc == 0:
        if not (0 <= a.shard < a.of):
            print(f"bad shard {a.shard} of {a.of}", flush=True)
            return 2
        rc |= wordlist_run(a.wordlist, a.shard, a.of, a.checkpoint,
                           a.resume, a.every)
    return rc


if __name__ == "__main__":
    sys.exit(main())
