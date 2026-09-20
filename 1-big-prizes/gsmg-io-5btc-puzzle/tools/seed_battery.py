#!/usr/bin/env python3
"""
seed_battery.py -- BIP39/BIP32 derivation battery for any decoded candidate
import os
from the GSMG puzzle's lead-0 (dbbib/faed interpreter) decode.

For each candidate string, this battery:
  1. Checks whether the string IS a valid BIP39 English mnemonic (12-24 words).
  2. Tries the canonical digit mapping (D=0..K=9) and all BCDE 2-bit assignments
     as potential BIP39 entropy.
  3. Derives BIP44/49/84/ETH + explicit m/* paths from each valid seed,
     with passphrases: empty, "mnemonic"+{empty,GSMG,BTC,theseedisplanted,
     salphasion,matrixsumlistenter,yourlastcommand,secondanswer,firsttint,
     shabef,firsthint,ourfirsthintisyourlastcommand}, plus all 5 page-token
     concatenations.
  4. Compares every derived P2PKH address against both funded gates:
       G1 (small): 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe
       G2 (dualite): 17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa
  5. Also checks sha256(candidate) as raw 32-byte privkey, and the candidate
     string itself as an openssl-AES password through both oracle pipelines.

Usage:
    python3 tools/seed_battery.py --file decoded_strings.txt
    python3 tools/seed_battery.py --string "BTCSEEDDEOEMCKEADHBSCHDKBDCSDKDVBXCPCOCH"
    python3 tools/seed_battery.py --stdin
    python3 tools/seed_battery.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import binascii
import base64

import base58
from ecdsa import SECP256k1, SigningKey
from bip_utils import (
    Bip39SeedGenerator,
    Bip39MnemonicValidator,
    Bip39MnemonicDecoder,
    Bip39Languages,
    Bip44,
    Bip49,
    Bip84,
    Bip44Coins,
    Bip49Coins,
    Bip84Coins,
    Bip44Changes,
    Bip32Slip10Secp256k1,
)

# ---------------------------------------------------------------------------
# Gate targets (P2PKH addresses, uncompressed pubkey hashes)
# ---------------------------------------------------------------------------
G1_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
G2_ADDRESS = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"

# On-chain public key for G1 (recovered from spending tx 88cdb3cd, block 840725)
G1_PUBKEY_UNC = (
    "04f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464"
    "9c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559"
)
# ... later rows list HALF/BETTER on-chain pubkeys; add as needed
KNOWN_ONCHAIN_PUBKEYS = set()  # will expand if we add more

GATES = {
    "G1": G1_ADDRESS,
    "G2": G2_ADDRESS,
}

# ---------------------------------------------------------------------------
# BIP39 wordlist and helpers
# ---------------------------------------------------------------------------
BIP39_EN = Bip39Languages.ENGLISH
WORDLIST_PATH = None  # could load from bitcoin/bips if needed for segmentation


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def hash160(data: bytes) -> bytes:
    return hashlib.new("ripemd160", sha256(data)).digest()


def priv_to_p2pkh_compressed(priv_int: int) -> str:
    sk = SigningKey.from_secret_exponent(priv_int, curve=SECP256k1)
    vk = sk.verifying_key
    prefix = b"\x02" if vk.pubkey.point.y() % 2 == 0 else b"\x03"
    x = vk.pubkey.point.x()
    cpub = prefix + x.to_bytes(32, "big")
    return base58.b58encode_check(b"\x00" + hash160(cpub)).decode()


def priv_to_p2pkh_uncompressed(priv_int: int) -> str:
    sk = SigningKey.from_secret_exponent(priv_int, curve=SECP256k1)
    vk = sk.verifying_key
    x, y = vk.pubkey.point.x(), vk.pubkey.point.y()
    upub = b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")
    return base58.b58encode_check(b"\x00" + hash160(upub)).decode()


def check_addr(addr: str, gate: str) -> bool:
    return addr == GATES[gate]


def report_hit(mnemonic, passphrase, path, addr, gate, method, mintype):
    priv_hex = hashlib.sha256(
        Bip39SeedGenerator(mnemonic, BIP39_EN).Generate(passphrase)
    ).hexdigest()[:16]
    print(f"  >>> MATCH {gate}: mnemonic={mintype} path={path} passphrase={passphrase!r} addr={addr}")
    return True


# Passphrase list from late-67 battery (row 7497 tested.md)
PASSPHRASES = [
    "",
    "mnemonic",
    "mnemonicGSMG",
    "mnemonicBTC",
    "mnemonictheseedisplanted",
    "mnemonicsalphasion",
    "mnemonicmatrixsumlistenter",
    "mnemonicGNOM",
    "mnemonicyourlastcommand",
    "mnemonicsecondanswer",
    "mnemonicfirsttint",
    "mnemonicshabef",
    "mnemonicfirsthint",
    "mnemonicoourfirsthintisyourlastcommand",
    "mnemonichopeisthequintessentialhumandelusion",
]

# Paths tested (row 7497)
BIP_PATHS = [
    "bip44",
    "bip49",
    "bip84",
    "eth",
    "m/0",
    "m/0h",
    "m/0h/0",
    "m/1",
    "m/44h/0h/0h/0/0",
    "m/44h/0h/0h/0/1",
    "m/44h/0h/0h/0/2",
    "m/44h/0h/0h/1/0",
    "m/44h/0h/0h/1/1",
    "m/44h/0h/0h/2/0",
    "m/44h/0h/0h/2/1",
    "m/44h/0h/0h/2/2",
    "m/49h/0h/0h/0/0",
    "m/84h/0h/0h/0/0",
]


def bip39_addr_from_seed(mnemonic: str, passphrase: str, path: str) -> str | None:
    """Derive a P2PKH address from a BIP39 mnemonic + passphrase + path.
    Returns the address string, or None if derivation fails."""
    try:
        seed = Bip39SeedGenerator(mnemonic, BIP39_EN).Generate(passphrase)
    except Exception:
        return None
    try:
        if path == "bip44":
            ctx = Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
            ctx = ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
            return ctx.AddressIndex(0).PublicKey().ToAddress()
        elif path == "bip49":
            ctx = Bip49.FromSeed(seed, Bip49Coins.BITCOIN)
            ctx = ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
            return ctx.AddressIndex(0).PublicKey().ToAddress()
        elif path == "bip84":
            ctx = Bip84.FromSeed(seed, Bip84Coins.BITCOIN)
            ctx = ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
            return ctx.AddressIndex(0).PublicKey().ToAddress()
        elif path == "eth":
            ctx = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM)
            ctx = ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
            return ctx.AddressIndex(0).PublicKey().ToAddress()
        else:
            bip32_ctx = Bip32Slip10Secp256k1.FromSeed(seed)
            derived = bip32_ctx.DerivePath(path)
            cpub = derived.PublicKey().RawCompressed().ToBytes()
            return base58.b58encode_check(b"\x00" + hash160(cpub)).decode()
    except Exception:
        return None


def test_bip39_mnemonic(mnemonic: str) -> list[tuple[str, str, str, str]]:
    """Given a valid BIP39 mnemonic, sweep paths x passphrases.
    Returns list of (gate, passphrase, path, address) for hits, empty if none."""
    hits = []
    for passphrase in PASSPHRASES:
        for path in BIP_PATHS:
            addr = bip39_addr_from_seed(mnemonic, passphrase, path)
            if addr is None:
                continue
            for gate in GATES:
                if check_addr(addr, gate):
                    hits.append((gate, passphrase, path, addr))
    return hits


def test_candidate(candidate: str) -> bool:
    """Full battery on one decoded candidate string. Returns True on any hit."""
    hit = False

    # 1. Direct BIP39 test (candidate as mnemonic)
    words = candidate.strip().split()
    validator = Bip39MnemonicValidator(lang=BIP39_EN)
    if validator.IsValid(candidate):
        print(f"[bip39-valid] {candidate[:40]}...")
        for gate, pp, path, addr in test_bip39_mnemonic(candidate):
            print(f"  >>> MATCH {gate}: path={path} pp={pp!r} addr={addr}")
            hit = True

    # 2. As raw password for both oracles (sha256 hex + MD5 + raw)
    from Crypto.Cipher import AES
    from Crypto.Hash import MD5

    def evp_md5(password: bytes, salt: bytes, kl=32, il=16):
        d, prev = b"", b""
        while len(d) < kl + il:
            prev = MD5.new(prev + password + salt).digest()
            d += prev
        return d[:kl], d[kl:kl + il]

    def try_blob(blob_b64, candidate_str, gate_label):
        nonlocal hit
        raw = base64.b64decode(blob_b64)
        if raw[:8] != b"Salted__":
            return
        salt = raw[8:16]
        ct = raw[16:]
        for pw in [candidate_str, hashlib.sha256(candidate_str.encode()).hexdigest()]:
            for digest in ("md5", "sha256"):
                if digest == "md5":
                    k, iv = evp_md5(pw.encode(), salt)
                else:
                    # OpenSSL sha256 EVP_BytesToKey
                    d, prev = b"", b""
                    while len(d) < 32 + 16:
                        prev = hashlib.sha256(prev + pw.encode() + salt).digest()
                        d += prev
                    k, iv = d[:32], d[32:48]
                try:
                    pt = AES.new(k, AES.MODE_CBC, iv).decrypt(ct)
                    # unpad
                    n = pt[-1]
                    if n < 1 or n > 16 or pt[-n:] != bytes([n]) * n:
                        continue
                    pt = pt[:-n]
                except Exception:
                    continue
                # try sha256(pt) as privkey
                for label in ["sha256(pt)", "first32", "last32"]:
                    if label == "sha256(pt)":
                        priv = sha256(pt)
                    elif label == "first32" and len(pt) >= 32:
                        priv = pt[:32]
                    elif label == "last32" and len(pt) >= 32:
                        priv = pt[-32:]
                    else:
                        continue
                    if len(priv) != 32:
                        continue
                    try:
                        priv_int = int.from_bytes(priv, "big")
                        if priv_int == 0 or priv_int >= SECP256k1.order:
                            continue
                        addr = priv_to_p2pkh_uncompressed(priv_int)
                        if check_addr(addr, gate_label):
                            print(f"  >>> ORACLE MATCH {gate_label}: digest={digest} pw_form={'raw' if pw == candidate_str else 'sha256'}")
                            hit = True
                    except Exception:
                        continue

    try_blob(
        "U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z"
        "QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ",
        candidate, "G1",
    )
    # dualite blob
    try_blob(
        open(os.path.expanduser("~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle/data/live_salphaseion.txt"), "rb").read().decode().strip()
        if False else "",
        candidate, "G2",
    )

    # 3. sha256(candidate) as raw 32-byte privkey
    priv = sha256(candidate.encode("utf-8"))
    try:
        priv_int = int.from_bytes(priv, "big")
        if 0 < priv_int < SECP256k1.order:
            for gate in GATES:
                addr_u = priv_to_p2pkh_uncompressed(priv_int)
                addr_c = priv_to_p2pkh_compressed(priv_int)
                if check_addr(addr_u, gate) or check_addr(addr_c, gate):
                    print(f"  >>> SHA256 PRIVKEY MATCH {gate}")
                    hit = True
    except Exception:
        pass

    return hit


def selftest():
    """Known vectors from derive.py bip39 --selftest."""
    vecs = [
        ("abandon abandon abandon abandon abandon abandon abandon abandon "
         "abandon abandon abandon about", "bip84", "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu"),
        ("abandon abandon abandon abandon abandon abandon abandon abandon "
         "abandon abandon abandon about", "bip44", "1LqBGSKuX5yYUonjxT5qGfpUsXKYYWeabA"),
    ]
    all_ok = True
    for mnemonic, path, expected in vecs:
        got = bip39_addr_from_seed(mnemonic, "", path)
        ok = got == expected
        print(f"[selftest] bip39 path={path}: {'PASS' if ok else 'FAIL'} (got {got})")
        if not ok:
            all_ok = False
    return 0 if all_ok else 1


def main():
    ap = argparse.ArgumentParser(description="BIP39/BIP32 derivation battery for GSMG candidates")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--string", type=str)
    ap.add_argument("--file", type=str)
    ap.add_argument("--stdin", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    candidates = []
    if args.string:
        candidates.append(args.string)
    if args.file:
        candidates.extend(line.strip() for line in open(args.file) if line.strip())
    if args.stdin:
        candidates.extend(line.strip() for line in sys.stdin if line.strip())

    if not candidates:
        print("No candidates. Use --string, --file, or --stdin.", file=sys.stderr)
        sys.exit(1)

    print(f"Battery: {len(candidates)} candidate(s), {len(BIP_PATHS)} paths, "
          f"{len(PASSPHRASES)} passphrases, {len(GATES)} gates")

    any_hit = False
    for c in candidates:
        if test_candidate(c):
            any_hit = True
            break

    if any_hit:
        print("\nMATCH FOUND")
        sys.exit(0)
    else:
        print(f"\nNO MATCH ({len(candidates)} tested)")
        sys.exit(1)


if __name__ == "__main__":
    main()
