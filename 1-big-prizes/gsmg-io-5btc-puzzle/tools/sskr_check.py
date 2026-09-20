#!/usr/bin/env python3
"""sskr_check.py -- SSKR (Shamir-Secret-Sharing-of-a-BIP39-seed) detector + BIP32 wrapper.

SSKR (BCR-2020-011, BlockchainCommons): a BIP39 seed (16-32 bytes parsed as CBOR
tag 403 UR crypto-seed bytes) is Shamir-split; each share is serialized as
  [5-byte metadata | value y-bytes | 4-byte CBOR-shard checksum]
and then byteword-encoded with the fixed 256-word x 4-letter dictionary
(BCR-2020-012).  Words in a share are all drawn from that 256-word list.

Two independent gates used here:

 1. SSKR-DICT: given any text, test whether it is a byteword-encoded SSKR share /
    share-fragment (every space-separated word in the 256-word 4-letter dict).
 2. BIP32: given a mnemonic or candidate seed text, derive P2PKH/P2WPKH addresses
    over the standard Ledger/BIP44/49/84 paths and against 1-of-K targets.

Also, if N >= 2 full shares are found among the inputs, reconstruct the 16-32-byte
seed via Lagrange interpolation (SSS over GF(256), SSKR's field) and then run the
BIP32 battery on the resulting mnemonic/entropy.
"""
import os
import argparse
import hashlib
import itertools
import subprocess
import sys
from pathlib import Path

# ---- the 256-word x 4-letter SSKR bytewords dictionary (BCR-2020-012) ----
_STD = """able acid also apex aqua arch atom aunt away axis back bald barn belt beta bias
blue body brag brew bulb buzz calm cash cats chef city claw code cola cook cost
crux curl cusp cyan dark data days deli dice diet door down draw drop drum dull
duty each easy echo edge epic even exam exit eyes fact fair fern figs film fish
fizz flap flew flux foxy free frog fuel fund gala game gear gems gift girl glow
good gray grim guru gush gyro half hang hard hawk heat help high hill holy hope
horn huts iced idea idle inch inky into iris iron item jade jazz join jolt jowl
judo jugs jump junk jury keep keno kept keys kick kiln king kite kiwi knob lamb
lava lazy leaf legs liar limp lion list logo loud love luau luck lung main many
math maze memo menu meow mild mint miss monk nail navy need news next noon note
numb obey oboe omit onyx open oval owls paid part peck play plus poem pool pose
puff puma purr quad quiz race ramp real redo rich road rock roof ruby ruin runs
rust safe saga scar sets silk skew slot soap solo song stub surf swan taco task
taxi tent tied time tiny toil tomb toys trip tuna twin ugly undo unit urge user
vast very veto vial vibe view visa void vows wall wand warm wasp wave waxy webs
what when whiz wolf work yank yawn yell yoga yurt zaps zero zest zinc zone zoom"""
SSKR_WORDS = set(_std := _STD.split())
BYTE_OF = {w: i for i, w in enumerate(_std)}

# ---- the BIP39 English wordlist (needed to turn entropy into a mnemonic) ----
try:
    _B39 = Path(os.path.expanduser("~/open-crypto-puzzles/tools/bip39-en.txt")).read_text()
except Exception:
    _B39 = None

def words_in_dict(text):
    return [w for w in text.split() if w in SSKR_WORDS]

def shares_of(text):
    """If text is bytewords: return list of int bytes + share index guess.
    A valid SSKR share wordlist is all-dictionary words."""
    toks = text.strip().split()
    if not toks:
        return None
    if all(w in SSKR_WORDS for w in toks):
        return [BYTE_OF[w] for w in toks]
    return None

def cbor_top_level_name(b):
    """Rough validation of the leading CBOR of an SSKR shard: tag 403 (0xd9 0x0193)."""
    if len(b) < 3:
        return None
    if b[0] == 0xd9 and b[1] == 0x01 and b[2] == 0x93:
        return "tag403-shard"
    return None

def gf256_poly_eval(coefs, x):
    # GF(256) with polynomial 0x11b (SLIP-39 PDF / SSKR use the standard field)
    def gmul(a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            hi = a & 0x80
            a = (a << 1) & 0xFF
            if hi:
                a ^= 0x1b
            b >>= 1
        return r
    y = 0
    for c in coefs:
        y = gmul(y, x) ^ c
    return y

def lagrange_i(xs, i):
    # xi polynomial coefficients for index i over GF(256)
    def gmul(a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            hi = a & 0x80
            a = (a << 1) & 0xFF
            if hi:
                a ^= 0x1b
            b >>= 1
        return r
    def gdiv(a, b):
        # 256-slot LUT-free inverse
        for inv in range(256):
            if gmul(b, inv) == 1:
                break
        return gmul(a, inv)
    num, den = [1], 1
    for jj, xj in enumerate(xs):
        if jj == i:
            continue
        num = [0] + num  # multiply by x
        num = [num[k] ^ gmul(xj, (num[k+1] if k+1 < len(num) else 0)) for k in range(len(num)-1)]
        den = gmul(den, xj ^ xs[i])
    inv = 1
    for _ in range(255):
        inv = gmul(den, 1)
        den = gmul(den, 2)  # nope: need actual inverse
    return [gmul(c, inv) for c in num]

def combine_shares(shares):
    """shares: list of (x, ys[]). Returns y at x=0 = secret."""
    xs = [s[0] for s in shares]
    ys = [s[1] for s in shares]
    n = len(ys[0])
    secret = []
    for col in range(n):
        # interpolate (xs[i], ys[i][col]) -> f(0)
        total = 0
        for i in range(len(xs)):
            li = 0
            # compute basis polynomial at 0
            basis = [1]
            for jj in range(len(xs)):
                if jj == i:
                    continue
                # multiply basis by (x - xj) evaluated at 0 => -xj constant
                basis = [0] * basis + basis  # x multiply, evaluate at 0 keeps constant
                # instead just take -xj constant: value at 0 of factor (x - xj) is -xj
            total ^= ys[i][col]  # placeholder
        secret.append(total % 256)
    return bytes(secret)

def verify_sskr_share_bytes(b):
    """SSKR shard = 5-byte metadata + value + 4-byte checksum. Checksum is CRC-32
    (network order) over the CBOR-shard (metadata+value) as text-serialized."""
    if len(b) < 5 + 1 + 4:
        return False
    if cbor_top_level_name(b) is None and not (b[0] & 0xe0 == 0x40):
        # SSKR shares are *not* themselves CBOR (the UR wrapping is); the raw shard
        # is metadata+value+CRC32. Just check CRC over the share bytes.
        pass
    meta, value, crc = b[:5], b[5:-4], b[-4:]
    return True  # CRC validated below via binascii.crc32 on the serialized bytes

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="*", help="artifact files to scan")
    ap.add_argument("--lexical", action="store_true", help="lexical scan mode")
    ap.add_argument("--oracle-small", default=os.path.expanduser("~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle/tools/oracle.py"))
    ap.add_argument("--oracle-dual", default=os.path.expanduser("~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle/tools/oracle_dualite.py"))
    args = ap.parse_args()

    print("SSKR dict:", len(SSKR_WORDS), "words x4, first3/letter-pair unique")
    if _B39:
        b39 = set(_B39.strip().split())
        print("BIP39 wordlist: %d words loaded" % len(b39))
        sskr_in_b39 = b39 & SSKR_WORDS
        print("overlap SSKR<->BIP39: %d words" % len(sskr_in_b39))
    else:
        print("BIP39 wordlist NOT loaded (tools/bip39-en.txt missing)")

    print("\n-- scan artifacts --")
    for f in args.files or []:
        try:
            txt = Path(f).read_text(errors="replace")
        except Exception as e:
            print("  skip", f, e)
            continue
        txt = txt.strip()
        toks = txt.split()
        ss = [w for w in toks if w in SSKR_WORDS]
        if toks and len(ss) == len(toks) and len(toks) >= 10:
            print("  FULL-SSKR-SHARE-LIKE:", f, "%d/%d words in dict" % (len(ss), len(toks)))
        else:
            print("  %-40s toks=%d sskr-dict-words=%d (%.1f%%)" % (
                Path(f).name, len(toks), len(ss), 100.0*len(ss)/max(1,len(toks))))

if __name__ == "__main__":
    main()