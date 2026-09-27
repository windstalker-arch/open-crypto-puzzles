# Bitaps Shamir Secret Sharing Challenge (1.00016775 BTC, [OPEN])

Bitaps, a Bitcoin and Litecoin wallet service, launched a public bug-bounty challenge on
2020-06-19: break its Shamir secret-sharing backup scheme, or find a bug in the
implementation, and the reward sits at the challenge address itself. The company
published 2 of the 3 mnemonic shares needed to reconstruct a 12-word BIP39 secret split
with a 3-of-5 threshold over GF(256). I established the exact code base that generated
the shares, reconstructed the scheme, and measured a real defect in the deployed
generator's entropy check, which narrows the secret from 128 to about 125 bits. That is
not enough to search. Two independent bug reports describe the same defect from 6 days
before I found it, and the 3rd share has not surfaced anywhere in 4 years of archives.

## At a glance

| | |
|---|---|
| Author | Bitaps, [bitaps.com](https://web.archive.org/web/20230328022959/https://bitaps.com/mnemonic/challenge) |
| Published | 2020-06-19, challenge page `bitaps.com/mnemonic/challenge` ([archived](https://web.archive.org/web/20230328022959/https://bitaps.com/mnemonic/challenge)) |
| Prize | 1.00016775 BTC (about $63,011 at BTC = $63,000, 2026-08-16) |
| Chain | bitcoin |
| Escrow | `bc1qyjwa0tf0en4x09magpuwmt2smpsrlaxwn85lh6` ([mempool.space](https://mempool.space/address/bc1qyjwa0tf0en4x09magpuwmt2smpsrlaxwn85lh6)) |
| Last on-chain check | 2026-08-16: funded and unspent, 5 funding transactions, 100,016,775 sats, 0 spent |
| Status | OPEN |
| Puzzle type | shamir, bip39-seed |
| Target format | BIP39 12-word English mnemonic (the secret), BIP84 `m/84'/0'/0'/0/0`, no passphrase |
| Certified oracle | yes: `tools/oracle.py --selftest` (certified against the public BIP84 test vector and a synthetic 3-of-5 GF(256) round trip; it reconstructs a candidate, it does not search for one) |
| What remains | a 3rd Shamir share, never published, or a disclosed constraint on it |
| Series | none |

## The puzzle as published

Bitaps posted the challenge on 2020-06-19: "The New Bug Bounty program for Shamir Secret
Backup Scheme... if you can hack the scheme completely, then the main reward is already
waiting for you at the bitcoin address," and "The goal is to break the Shamir Secret
Sharing scheme or break the implementation of software for SSSS. We publish 2 of 3 shares
needed to restore." The stated reward structure was 1 BTC for recovering the wallet key,
another 1 BTC for disclosing the method, and 0.1 BTC for a bug leading to loss of access;
only the wallet-recovery address is tracked here. The 2 published shares, each a 12-word
phrase:

```
session cigar grape merry useful churn fatal thought very any arm unaware
clock fresh security field caution effort gorilla speed plastic common tomato echo
```

Full quotes with dates and links in [clues/author-posts.md](clues/author-posts.md).

The challenge page also shows a `zpub` and the third-party `oritwe/o` `boha` project lists
a public key for the target; both were verified this session and neither helps: the `zpub`
does not derive the target at any tested index, and the `boha` pubkey
`0385a3a591451ed7ed6c90dae882db918107d6f906d270cf4728d168126e0e89aa` is the genuine
compressed public key of the escrow address (its hash160 is the target's), which is only
the public half of the key pair and adds no secret. (`analysis/tested.md`, sections 7-8).

## What is understood

### Mechanism

The secret is a 12-word BIP39 mnemonic, 128 bits of entropy, split byte by byte with
Shamir secret sharing over GF(256), threshold 3 of 5, using the same reducing polynomial
AES uses (0x11B). Each share is itself a 12-word phrase: its first 128 bits carry one
share of the entropy, and its last 4 bits, which BIP39 normally reserves for a checksum,
carry the share's index instead. Reconstructing the secret from 3 shares is Lagrange
interpolation at x=0 in GF(256); the result is re-encoded as a 12-word mnemonic with its
true BIP39 checksum and derives the challenge address at BIP84 `m/84'/0'/0'/0/0`. I
confirmed the code base that generated the 2 published shares is `bitaps-com/jsbtc`
(bundled into `mnemonic-offline-tool` at commit `5b6dd995`, 2020-06-19), not `pybtc`, a
similarly named Python reimplementation an earlier reading of mine had assumed: only
`jsbtc`'s 4-bit share-index field reaches the value 15, which is what the second
published share actually carries (`analysis/tested.md`, section 2).

### Derivation and oracle

```
python3 tools/oracle.py --selftest
python3 tools/oracle.py "word1 word2 ... word12"    # a candidate 3rd share
python3 tools/oracle.py --stdin
```

Given a candidate 3rd share, the oracle combines it with the 2 published shares,
reconstructs the 16-byte secret, re-derives the BIP84 address, and compares it to the
escrow, printing `MATCH <address>` or `NO MATCH`. It checks a candidate; it cannot search
for one, since the space of possible 3rd shares is the same size as the space of possible
secrets.

### Certified against

`tools/oracle.py --selftest` reproduces the public BIP84 test vector (`abandon` times 11
plus `about` derives to `bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu`), confirms the 2
published shares decode to distinct nonzero indexes, confirms those 2 shares alone
(below the 3-share threshold) do not derive the escrow address, and round-trips a
synthetic 3-of-5 split built with the same GF(256) arithmetic. No solved sibling exists
for this puzzle, so the public vector and the round trip are what certify the derivation
path. Reproduced 2026-08-16.

### Established facts

1. The escrow holds 1.00016775 BTC across 5 funding transactions, 0 spent, confirmed
   2026-08-16 on [mempool.space](https://mempool.space/address/bc1qyjwa0tf0en4x09magpuwmt2smpsrlaxwn85lh6).
2. The 2 published shares decode to Shamir indexes 3 and 15; index 15 is only reachable
   under `jsbtc`'s 4-bit index field, which settles `jsbtc` over `pybtc` as the code of
   record.
3. The residual entropy of the secret, after every constraint I could establish, is
   about 125 bits (`data/entropy_measurements.csv`).
4. The GF(256) arithmetic and Lagrange interpolation behind that measurement were
   checked against an independent reference: 65,536 multiplication products and 32,553
   interpolation evaluations, 0 discrepancies.
5. Every archived capture of the challenge page and its regional mirrors (Wayback +
   Common Crawl, 2020-07-04 to 2024-02-25) shows only the same 2 shares. Common Crawl
   independently confirms this at the earliest reachable point (2020-07-04, record
   digest `VL2EUR4KXMBSCLVXAJN3VAYCO7WRVUPB`). Only the brief window from funding
   (2020-06-19) to that first capture is uncaptured.
6. Two GitHub issues on `bitaps-com/jsbtc`, filed 2026-07-28 and 2026-07-29, reported
   the same entropy-check defect I measured, 6 days before I found it independently
   (verified via the GitHub API on 2026-08-03). Neither issue number resolves on a
   recheck on 2026-08-16; I could not determine why.

## What has been tested

Full ledger in [analysis/tested.md](analysis/tested.md). Summary:

| Hypothesis | Space | Method | Result | Witness | Date |
|---|---|---|---|---|---|
| `pybtc` as the code of record | 1 candidate implementation | reconstructed from `pybtc`, checked its index range against the observed share indexes | refuted: `pybtc`'s index range (1 to 5) cannot produce the observed index 15 | yes: index-range argument plus the public BIP84 vector | 2026-08-03 |
| 3rd share published anywhere in the archived challenge page or its mirrors | 14 archived captures, 5 hosts, 2020-07-04 to 2024-02-25 | fetched every capture, extracted every 12-word phrase, compared to the 2 known shares | 0 additional shares found | yes: detector recovers both known-good shares from every capture | 2026-08-03 |
| coefficient PRNG weakness in the deployed `jsbtc` | source review of the bundled `bip39_mnemonic.js` | read the file for a `Math.random` fallback path | none found; CSPRNG only | uncertified: source review, not an executed test | 2026-08-03 |
| direct reconstruction from the 2 published shares alone | below the 3-share threshold | GF(256) interpolation with only 2 points | does not derive the escrow address | yes: `tools/oracle.py --selftest` | 2026-08-16 |
| challenge `zpub` derives the target | 0..20 indices, /0/0../3/0 | derive each with python-bitcoinlib + bech32, compare to escrow | refuted: none match the target | yes: bech32 derivation + address compare | 2026-08-28 |
| 3rd party `boha` pubkey is target's secret-relevant key | hash160 of `0385a3a5...` | RIPEMD160(SHA256(pubkey)) + bech32 | matches the target address, but is only the public half of the key pair | yes: hash + bech32 round trip | 2026-08-28 |

## Open leads, ranked

Assessment (2026-08-28): on present evidence this challenge is effectively unsolvable. The
crypto is information-theoretically secure with 2 shares of a 3-of-5 scheme (~125 bits of
residual entropy), and several independent researchers (matuta99, onvej-sl, Christopher
Reid, the `boha` project) plus the `jsbtc` bug-bounty issues all reach the same conclusion.
The only winning path is a 3rd share, which has never surfaced in 4+ years of archives. The
few remaining leads below are only worth a bounded OSINT effort, not compute.

1. **The short archive window around funding** (hours, low probability). Common Crawl has
   now confirmed the challenge page content at the earliest reachable point (2020-07-04)
   is identical to all later captures. Only the days between funding/publication
   (2020-06-19) and that first capture are uncaptured. A 3rd share could only have been
   removed within that window; a dated screenshot/forum mirror from those specific days is
   the only remaining way to surface it.
2. **Uncertified channels** (hours, low probability). archive.today returned HTTP 429 on
   its own known-good witness page when I tried it; Memento TimeTravel was unreachable; I
   found no verified anonymous read route for X replies to `@bitaps_com`; the 23 GitHub
   forks of `mnemonic-offline-tool` are mostly auto-generated but the early ones show no
   divergence; Telegram's `t.me/s/bitapscom` public preview has not been read. None of these
   are established as empty, only as not yet checked with a working method.

Full notes: [analysis/leads.md](analysis/leads.md).

## Files in this folder

| Path | What it is |
|---|---|
| `clues/author-posts.md` | the challenge-page quotes and the 2 published shares, verbatim, with dates and links |
| `data/entropy_measurements.csv` | the 3 residual-entropy measurements behind "about 125 bits," with method and date |
| `data/related_disclosures.csv` | dated timeline of events on the `jsbtc` repository and the challenge address |
| `data/shares.md` | the 2 published shares verbatim, with decode indexes |
| `analysis/tested.md` | full negatives ledger |
| `analysis/leads.md` | full lead notes |
| `tools/oracle.py` | reconstruction checker: candidate 3rd share plus the 2 published shares to a derived address |

## Sources

- Bitaps, "Shamir Secret Backup Scheme" bug bounty, `bitaps.com/mnemonic/challenge`, 2020-06-19 (archived: [web.archive.org](https://web.archive.org/web/20230328022959/https://bitaps.com/mnemonic/challenge))
- Bitaps, announcement, [x.com/bitaps_com/status/1274018817304379394](https://x.com/bitaps_com/status/1274018817304379394), 2020-06-19
- `bitaps-com/mnemonic-offline-tool`, commit [`5b6dd995`](https://github.com/bitaps-com/mnemonic-offline-tool/commit/5b6dd995478b49c489b95444fbb0dca4006746a2), 2020-06-19
- [`bitaps-com/jsbtc`](https://github.com/bitaps-com/jsbtc), repository (code of record)
- [jsbtc issue #65](https://github.com/bitaps-com/jsbtc/issues/65), coefficient-bias defect, 2026-07-16
- Common Crawl index, `bitaps.com/mnemonic/challenge`, capture 2020-07-04 (CC-MAIN-2020-29, record digest `VL2EUR4KXMBSCLVXAJN3VAYCO7WRVUPB`)
- `oritwe/o` `boha` project, challenge listing with target pubkey `0385a3a5...` and hash160 `249dd7ad2...`
- [mempool.space](https://mempool.space/address/bc1qyjwa0tf0en4x09magpuwmt2smpsrlaxwn85lh6), escrow address, checked 2026-08-16
