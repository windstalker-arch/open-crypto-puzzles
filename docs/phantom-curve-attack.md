# Phantom Curve Attack: recovering an ECDSA key from a weak nonce

Reference page, not a puzzle. It records how I run the nonce-reuse and weak-nonce
cryptanalysis described in [demining/Phantom-Curve-Attack](https://github.com/demining/Phantom-Curve-Attack)
(2026-08-16), what I measured on this phone, and the boundary I hold.

## The method in one paragraph

An ECDSA signature is `(r, s)` with `s = k^-1 * (z + r*d) mod n`, where `d` is the private
key, `k` is the nonce and `z` is the message hash. If the same `k` signs two messages, the two
`r` values are equal and both `k` and `d` fall out in closed form. When the nonce is not
repeated but weak, say 8 bytes, the same algebra gives the public point `R = k*G` from public
data alone, and finding `k` becomes a discrete logarithm on a known interval. Kangaroo solves
that in time proportional to the square root of the interval width, so a 2^64 nonce costs about
2^33 operations rather than 2^64.

The point `R` comes out of the signature without knowing the public key:

```
R = s^-1 * (z*G + r*Q) mod n
```

`Q` is recovered from `(r, s, z)` by the standard four-candidate public key recovery, then
filtered against the pubkey hash in the spent output's `scriptPubKey`. A match on that hash is
what makes the recovery confirmed rather than a guess.

## What I measured, 2026-09-26

I built a harness and ran it against wallets I generated myself, with the nonce widths the
paper describes. The answers were known before each run, so every run is a pass or a fail with
no judgement call.

| Nonce width | Expected operations | Result |
|---|---|---|
| 20 bits | 2^11.6 | recovered the nonce exactly, under 1s at `-t 2` |
| 64 bits | 2^33.1 | 1.75 MK/s at `-t 3`, about 1h28m average |

Harness self-test, all confirmed:

```
1. group law, order-N reduction, compressed serialisation
2. two low-entropy nonces produced by an in-memory signer
3. R rebuilt from (r, s, z, Q) equals k*G for both signatures
4. Q rebuilt from the signature alone, matched on pubkey hash
5. the r-reuse closed form returns both the right k and the right d
6. legacy and BIP143 sighash, and the P2PKH, P2WPKH, P2SH-P2WPKH script matchers
7. the real Kangaroo binary recovers the nonce from R over the interval
```

Two device notes, both cost me a cycle:

- This phone has no `/usr/bin/env` and no `/bin/bash`. A `#!/usr/bin/env bash` shebang fails
  with "No such file or directory" even though the file is executable. Use the prefix path,
  `#!/data/data/com.termux/files/usr/bin/bash`. The same trap applies to any script in this
  repository that is run directly rather than through `python3`.
- Kangaroo builds here with `make CXX=clang++ all`. GCC 14 fails at link on the Termux libc++.
- KeySilentLeak's `requirements.txt` asks for `zmq>=0.0.0`. That is a different package from
  `pyzmq`, and no Termux wheel exists for the name it gives, so `pip install -r` resolves it to
  a 1,089-byte placeholder on PyPI and installs it. Install `pyzmq` by name instead. I checked
  what the placeholder had claimed before removing it: its record listed only its own
  `dist-info`, no file inside `zmq/`, so the removal left the working pyzmq 27.1.0 in place and
  a REP socket still bound and tore down afterwards.

## Where the code is

The paper repository holds no code, only the write-up and its figures. The harness I wrote is
outside this repository, at `~/Phantom-Curve-Attack/tools/`, with the run script
`run_64bit_selftest.sh`. It parses a raw transaction you supply, prints `Q` and `R`, and writes
a Kangaroo input file. It contacts no service and broadcasts nothing.

The KeySilentLeak package I took from the author's site does ship Python source, and I read all
of it. What is in the archive: an OP_RETURN transaction generator, written twice, once as a
widget front end (`colab.py`, the notebook) and once on `input()` (`main.py`); an 18-line
broadcaster that POSTs a raw transaction to `blockchain.info/pushtx` (`pushtx.py`); and four
reusable modules for signing (`secp256k1.py`, `sighash.py`, `sign.py`, `signing.py`). What is
not in it: any key recovery. I grepped every file for kangaroo, Pollard, BSGS, interval search
and weak-nonce logic and there are no matches. So the interval discrete logarithm is the part
that has to be built, and the Kangaroo binary already here is that part. Two other things in
that package I did not run: `pushtx.py` broadcasts, which the rules in `AGENTS.md` forbid
outright, and `setup.py` pip-installs five modules and downloads two further archives from a
third-party host at import time. `demining/CryptoDeepTools` directory `50PhantomCurveAttack`
is a README and no code. The Kangaroo source in `06KangarooJeanLucPons` is the same
JeanLucPons code I already build.

## When this applies to a puzzle here

Only when the puzzle publishes a signed transaction whose signer had a faulty nonce source.
No puzzle folder in this repository rests on that. I searched every manifest for the terms
nonce, ECDSA, duplicate signature, reused r and Phantom: the only hit is an Ethereum account
nonce recorded in a prize note, which is a transaction counter and has nothing to do with
ECDSA nonces.

The check is cheap and it is worth running before dismissing the idea. Two signatures from
the same public key with the same `r` are a closed-form key. One signature from a signer with
a documented 32-bit or 64-bit nonce is a 2^16 or 2^32 Kangaroo run, minutes to an hour on this
phone. Neither needs rented hardware.

## Boundary

I run this only on transactions I own or on published research material, and I do not point it
at a live third-party address. Recovering a key from someone else's broadcast transaction is
theft, not research, and the fact that the mathematics is public does not change that. Nothing
in this repository sweeps funds, signs anything, or contacts an exchange. If a puzzle author
publishes a vulnerable transaction and invites recovery, that is a puzzle and it gets a folder
like any other, with the escrow check and an oracle like any other.

## Sources

- [demining/Phantom-Curve-Attack](https://github.com/demining/Phantom-Curve-Attack), the
  cryptanalysis of the Dark Skippy attack and of nonce reuse in ECDSA. 2026-08-16.
- [Dark Skippy disclosure](https://x.com/utxoclub/status/1820520960476561825), the August 2024
  hardware wallet finding the paper analyses. 2024-08-07.
- [JeanLucPons/Kangaroo](https://github.com/JeanLucPons/Kangaroo), the interval discrete log
  solver, v2.2 as built here. 2026-08-22.
- [CVE-2025-27840](https://nvd.nist.gov/vuln/detail/CVE-2025-27840), the ESP32 fault behind
  the weak nonces in a later wallet recovery. Reported 2025.
- [ECDSA on Wikipedia](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)
  and [Pollard's kangaroo algorithm](https://en.wikipedia.org/wiki/Pollard%27s_kangaroo_algorithm),
  for the formulas. 2026-08-16.
