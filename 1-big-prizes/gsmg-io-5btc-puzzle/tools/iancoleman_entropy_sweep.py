#!/usr/bin/env python3
"""
iancoleman_entropy_sweep.py -- route the puzzle's digit streams through the EXACT
entropy->BIP39->BIP32 pipeline of the iancoleman.io/bip39 tool (iancoleman/bip39
src/js/entropy.js + jsbip39.js + index.js). This is the one BIP39-adjacent battery
never applied in analysis/tested.md:

  * prior rows read the streams as BIGINTs (base-N number -> hex -> bytes);
  * iancoleman instead reads the string as EVENTS and biased-packs each to bits
    (base 10: 0-7->3 bits, 8-9->1 bit; base 6/dice: 0-3->2 bits, 4-5->1 bit;
     hex: 4 bits/char), then builds a BIP39 mnemonic from the bitstream;
  * his hex matcher keeps ONLY [0-9A-F] and silently DROPS g/h/i/z -- so the raw
    a-f letters of dbbib_91/faed are themselves a valid (partial) hex entropy
    string under his own semantics;
  * his DEFAULT typed-entropy route is sha256(cleaned_entropy_string) -> 256-bit
    -> 24-word mnemonic (and 128-bit -> 12-word, etc. by truncation).

Routes:
  R1  hex-drop   : keep a-f as hex digits (4b/each), drop g/h/i/z -> bitstream
  R2  base-6     : letter->digit via POS / CANON interpreter, keep 0-5, biased pack
  R3  base-10    : letter->digit via POS / CANON interpreter, keep 0-9, biased pack
  R4  hash-branch: sha256(string) -> 256b -> 12/15/18/21/24-word mnemonics
  R5  bit-reverse variants of R1-R3 (hint chain stressed reversal repeatedly)

Each candidate mnemonic is then:
  (a) fed as candidate X to BOTH funded-gate oracles (oracle.py small,
      oracle_dualite.py Dualite) -- they already try X raw and sha256(X) hexify;
  (b) swept through BIP39 seed -> BIP44/49/84/m/* x passphrases x both gates
      via seed_battery.py --stdin --targets (reusing its certified derivation).

This pipeline motivates the pending seed_battery.py improvement (wire the
Dualite blob path); until then oracle_dualite stdin covers G2's blob.

Usage:
  python3 tools/iancoleman_entropy_sweep.py --selftest
  python3 tools/iancoleman_entropy_sweep.py            # full sweep
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_PATH = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
DATA = json.loads(Path(_DATA_PATH).read_text())
DBBIB_91 = DATA.get("dbbib_91", DATA["dbbib"])
DBBIB_69 = DATA["dbbib"]
FAED = DATA["faed_570"].rstrip("z")

from bip_utils import (
    Bip39MnemonicGenerator,
    Bip39Languages,
)

# ------------------------------------------------------------------ faithful
# port of iancoleman/bip39 src/js/entropy.js event-bit tables
# ---------------------------------------------------------------------------
BITS_HEX = {c: format(i, "04b") for i, c in enumerate("0123456789abcdef")}
BITS_BASE6 = {"0": "00", "1": "01", "2": "10", "3": "11", "4": "0", "5": "1"}
BITS_BASE10 = {"0": "000", "1": "001", "2": "010", "3": "011",
               "4": "100", "5": "101", "6": "110", "7": "111",
               "8": "0", "9": "1"}


def hex_events(s: str) -> list[str]:
    return [c for c in s if c in "0123456789abcdef"]

def base6_events(s: str) -> list[str]:
    return [c for c in s if c in "012345"]

def base10_events(s: str) -> list[str]:
    return [c for c in s if c in "0123456789"]

def to_bits(events: list[str], table: dict[str, str]) -> str:
    return "".join(table[e] for e in events)


def entropy_to_mnemonic(entropy_bytes: bytes) -> str | None:
    """BIP39 mnemonic (checksum computed) for a valid entropy length."""
    if len(entropy_bytes) not in (16, 20, 24, 28, 32):
        return None
    obj = Bip39MnemonicGenerator(Bip39Languages.ENGLISH).FromEntropy(entropy_bytes)
    return str(obj)


ENT_LENGTHS = (128, 160, 192, 224, 256)


def mnemonic_windows(bits: str) -> list[str]:
    """All (start,end) entropy windows -> 11-bit word mnemonics. iancoleman's
    raw branch keeps the 32-aligned tail; we also take aligned head, both."""
    ms: list[str] = []
    for blk in (bits[: len(bits) // 32 * 32] if len(bits) >= 128 else "",
                bits[len(bits) % 32:] if len(bits) >= 128 else ""):
        for entb in ENT_LENGTHS:
            if len(blk) < entb:
                continue
            b = blk[len(blk) - entb:] if len(blk) > entb else blk
            bar = bytes(int(b[j:j + 8], 2) for j in range(0, entb, 8))
            m = entropy_to_mnemonic(bar)
            if m:
                ms.append(m)
                break
    return ms


INTERPRETERS = {
    "POS": {c: i for i, c in enumerate("abcdefghi")},       # column order a=0..i=8
    "CANON": {"d":0, "b":1, "i":2, "f":3, "h":4, "c":5, "e":6, "g":7, "a":8},
}


def sha256s(s: str) -> bytes:
    return hashlib.sha256(s.encode()).digest()


def build_all():
    """Generate every candidate mnemonic across routes R1-R5."""
    cands: dict[str, str] = {}  # mnemonic -> source label
    streams = [("dbbib91", DBBIB_91), ("faed", FAED), ("dbbib69", DBBIB_69),
               ("db+faed", DBBIB_91 + FAED), ("faed+db", FAED + DBBIB_91)]

    def register(m, src):
        if m and m not in cands:
            cands[m] = src

    # R1: hex-drop on raw stream (a-f kept, g/h/i/z dropped)
    for sname, stream in streams:
        ev = hex_events(stream)
        if not ev:
            continue
        bits = to_bits(ev, BITS_HEX)
        for label, w in (("fwd", bits), ("rev", bits[::-1])):
            for m in mnemonic_windows(w):
                register(m, f"R1 hex:{sname}:{label}")

    # R2/R3: interpreted digits -> biased base-6 / base-10
    for mp_name, mp in INTERPRETERS.items():
        for sname, stream in streams:
            ds = "".join(str(mp[c]) for c in stream if c in mp)
            for base_name, table, keep in (("b6", BITS_BASE6, base6_events),
                                           ("b10", BITS_BASE10, base10_events)):
                ev = keep(ds)
                if len(ev) < 40:
                    continue
                bits = to_bits(ev, table)
                for label, w in (("fwd", bits), ("rev", bits[::-1])):
                    for m in mnemonic_windows(w):
                        register(m, f"R{base_name[1:]}:{mp_name}:{sname}:{label}")

    # R4: sha256-hash branch (both raw and interpreted digit strings)
    for sname, stream in streams:
        for ds_label, ds in (("raw", stream),
                             ("POS", "".join(str(INTERPRETERS["POS"][c]) for c in stream if c in INTERPRETERS["POS"])),
                             ("CANON", "".join(str(INTERPRETERS["CANON"][c]) for c in stream if c in INTERPRETERS["CANON"]))):
            if len(ds) < 40:
                continue
            dig = sha256s(ds)
            bits = format(int.from_bytes(dig, "big"), "0256b")
            for entb in ENT_LENGTHS:
                chunk = bits[:entb]
                bar = bytes(int(chunk[j:j + 8], 2) for j in range(0, entb, 8))
                m = entropy_to_mnemonic(bar)
                register(m, f"R4 sha256:{sname}:{ds_label}:{entb}")

    return cands


def oracle_stdin(cands: list[str], tool: str) -> int:
    p = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", tool), "--stdin"],
        input="\n".join(cands) + "\n", capture_output=True, text=True, timeout=1800)
    return p.stdout.count("\nMATCH ")


def seed_battery(cands: list[str]) -> int:
    """Delegate derivation sweep to the certified seed_battery.py --stdin."""
    p = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "seed_battery.py"), "--stdin"],
        input="\n".join(cands) + "\n", capture_output=True, text=True, timeout=7200)
    return p.stdout.count(">>> MATCH")


def self_test() -> bool:
    # entropy.js dice '12345' -> '01101101'
    assert to_bits(list("12345"), BITS_BASE6) == "01101101"
    assert to_bits(list("0123456789"), BITS_BASE10) == "00000101001110010111011101"
    # hex drop: g,h,i,z removed (only a-f kept)
    assert hex_events("dbhibzcfg") == ["d", "b", "b", "c", "f"]
    # known BIP39 vector: 128 zero bits -> abandon*11 + about
    m = entropy_to_mnemonic(bytes(16))
    assert m == " ".join(["abandon"] * 11 + ["about"]), m
    print("SELFTEST OK (dice pack, base-10 pack, hex-drop, BIP39 zero-entropy vector)")
    return True


def main() -> int:
    if "--selftest" in sys.argv:
        sys.exit(0 if self_test() else 1)
    if "--count" in sys.argv:
        cands = build_all()
        print(f"{len(cands)} unique mnemonics")
        for m, s in list(sorted(cands.items(), key=lambda kv: kv[1]))[:400]:
            print(f"  {s:36s} {m}")
        return 0

    cands = build_all()
    print(f"generated {len(cands)} unique checksum-valid mnemonics")
    if not cands:
        print("no candidates generated")
        return 1

    order = sorted(cands)
    print(f"-> oracle.py (small gate) over {len(order)} candidates ...")
    g1 = oracle_stdin(order, "oracle.py")
    print(f"   {g1} MATCH(es)")
    print(f"-> oracle_dualite.py (Dualite gate) over {len(order)} candidates ...")
    g2 = oracle_stdin(order, "oracle_dualite.py")
    print(f"   {g2} MATCH(es)")
    print(f"-> seed_battery.py BIP32/44/49/84 x passphrases over {len(order)} candidates ...")
    db = seed_battery(order)
    print(f"   {db} MATCH(es)")

    if g1 or g2 or db:
        print("\n*** MATCH FOUND ***")
        return 0
    print("\nNo match; iancoleman entropy family closed negative (bounded sweep).")
    return 1


if __name__ == "__main__":
    sys.exit(main())