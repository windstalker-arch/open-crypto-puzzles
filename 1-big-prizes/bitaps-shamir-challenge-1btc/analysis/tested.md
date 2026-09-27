# Tested: Bitaps Shamir secret-sharing challenge

Full negatives ledger. The README shows the summary table.

## 1. Wrong code base (rounds 1 and 2, superseded)

I first analyzed `pybtc`, a Python reimplementation of the same scheme, and found a
time-based coefficient bias in its `(a * i) % 255` construction, computing a residual of
119, 98, then 82 bits under 3 successive refinements. This turned out to be the wrong
target: `pybtc`'s Shamir index space is `x` in 1 to 5, and the real published share 2 has
index `x = 15`, which `pybtc` cannot produce. `pybtc` also only gained the embedded-index
feature it would need on 2020-07-11, three weeks after the challenge address was funded.
I dropped this line of analysis once the index mismatch was confirmed; it is kept in the
project history as a recorded wrong turn, not as a result.

## 2. Establishing the real code base

`bitaps-com/mnemonic-offline-tool`, commit `5b6dd995` (2020-06-19, the funding date),
bundles `jsbtc`, not `pybtc`. 3 checks confirm this: the trailing 4 bits of each share are
a data field (an index), not a checksum, since both published shares fail the BIP39
checksum in a way consistent with an embedded index rather than corruption; the observed
index values (3 and 15) fall inside `jsbtc`'s 4-bit index range (1 to 15) and outside
`pybtc`'s 3-bit range (1 to 5) as it existed on the funding date; and re-deriving from
both candidate implementations against the 2 published shares, only the `jsbtc` reading
produces internally consistent output. Method: source comparison plus the index-range
argument above. Witness: the public BIP84 test vector reproduces via `tools/oracle.py
--selftest`. Result: `jsbtc` established as the code of record. Date: 2026-08-03.

## 3. Residual entropy of the secret

See `data/entropy_measurements.csv` for the 3 measurements and their method. Summary: the
theoretical 128 bits narrows to 127.73 bits under the duplicate-value coefficient
rejection rule common to both `jsbtc` and `pybtc`, and to about 125 bits (124.90 to
125.19 across 3 independent measurements) once I added the effect of a real defect in the
deployed 2020 generator: its randomness self-check calls an undefined function
(`igam`, called from `igamc`), which throws and is silently caught, discarding a
disproportionate share of otherwise-valid random draws. None of this is small enough to
search; the point of measuring it is to state the true entropy accurately rather than by
assumption. Witness: the multiplication and interpolation tables underneath the
measurement were checked against an independent reference (65,536 GF(256) products, 0
discrepancies; 32,553 Lagrange evaluations, 0 discrepancies). Date: 2026-08-03.

## 4. Third-share search in the archives

14 archived captures of the challenge page and its regional mirrors (`bitaps.com`, plus
`ltc`, `tltc`, `tbtc`, `btc` subdomains), spanning 2020-07-04 to 2024-02-25 (Wayback CDX
and Common Crawl), all show the same 2 shares. Method: fetch every capture, extract any
12-word phrase, compare against the 2 known shares. Witness: the detector recovers both
known-good shares from every capture it reads, so an empty result is not a detector
failure. Result: 0 additional shares found across 14 captures. The interval between
2020-06-19 (funding) and 2020-07-04 (earliest capture), 15 days, is not covered by either
archive. Date: 2026-08-03.

## 5. Coefficient PRNG check

`bip39_mnemonic.js` in the bundled `jsbtc` uses `crypto.getRandomValues` or Node's
`randomBytes` for share coefficients, with no `Math.random` fallback path in the code I
read. Method: source review of the exact bundled file. Result: no exploitable seed bias
found in the coefficient generator itself (the bias found in section 1 was specific to
`pybtc`, the wrong code base). Date: 2026-08-03.

## 6. Degenerate coefficient case

The scheme's second coefficient can, with probability 1/255 per byte, be zero, which
would drop the polynomial's effective degree. This is not identifiable from only 2
shares; I enumerated the 16-byte space of this specific degenerate case and found no way
to test it without a 3rd share. Not pursued further as a standalone lead. Date:
2026-08-03.

## 7. zpub does not derive the target (2026-08-28)

The challenge page carries a shown `zpub`
`zpub6qdEDkv51FpxX6g1rpFGckmiL46vV8ccmtEgPAkj3qj8N4ZZHyXDRA9RwpTiFK2Kb8vRaDmSmwgX6rfB4t2K8Ktdq8ExQ6fumKpn2ndJCqL`.
This is a red herring / unrelated mnemonic. Using python-bitcoinlib + bech32 I verified its
`/0/0`, `/1/0`, `/2/0`, `/3/0` and indices 0..20 all derive to addresses other than the
target `bc1qyjwa0...`. It cannot be a path to the secret. Result: zpub excluded. Date:
2026-08-28.

## 8. boha public key matches the target (identity confirmed, no new search space)

The `oritwe/o` `boha` project lists the challenge with `public_key =
0385a3a591451ed7ed6c90dae882db918107d6f906d270cf4728d168126e0e89aa` and hash160
`249dd7ad2fccea67977d4078edad50d8603ff4ce`. I verified this pubkey's RIPEMD-160 hashes to
`249dd7ad2...` and bech32-encodes to exactly the target `bc1qyjwa0tf0en4x09magpuwmt2smpsrlaxwn85lh6`.
So `0385a3a5...` is genuinely the compressed public key of the target (the on-chain pubkey
derived from the unknown private key). This confirms target identity but is just the public
part of the key pair - it adds no secret information and does not shrink the ECDLP/Shamir
search. boha also labels the shares with indexes 1 and 2, which diverge from the oracle's
x=3/x=15 decode; this is a decoding convention difference and yields no new share. Date:
2026-08-28.

## 9. Common Crawl earliest capture agrees (2026-08-28)

Common Crawl index holds `bitaps.com/mnemonic/challenge` dated 2020-07-04 (CC-MAIN-2020-29).
Its share content is byte-identical (same 2 shares, session/cigar/... and
clock/fresh/...) to the 2020-10-28 Wayback capture and every later capture on main/tbtc/ltc
mirrors. Confirms no 3rd share at the earliest reachable point; narrows the archive-gap
lead. Date: 2026-08-28.
