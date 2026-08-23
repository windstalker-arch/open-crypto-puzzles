# Negatives ledger, RushWallet contest #30

Method for every row: candidate passphrase taken verbatim, SHA-256, uncompressed
secp256k1 public key, P2PKH address, compared byte-exact to `13Q8hJqagtd77ojTJcEZPjTz2sBFSsYxyj`.
Oracle certified against 3 known passphrase/address pairs from sibling brainwallets in the
same contest (`tools/oracle.py --selftest`), so zero false positives are possible: a match
can only be declared on exact address equality.

One caveat applies to every row below: the oracle itself is certified, but no known-good
passphrase was planted inside the actual corpus streams at head, middle and tail before
each run. That means these negatives are not witnessed in the strict sense of this
project's own standard; they are honestly reported as candidates consumed with 0 hits,
not as a certified-exhaustive sweep of each corpus.

| Hypothesis | Candidates | Result | Date |
|---|---|---|---|
| Structured passphrases built from the video/contest's own text (Dmitri phrase variants, whitepaper title and sections, KryptoKit slogans, Cicada/John Donne references, coin numbers, x2 to x6 repetitions, case variants) | about 3,000 | 0 match | 2026 (round 1-2) |
| rockyou.txt, 5 case variants each (as-is, lower, UPPER, Title, capitalized-first) | 14,344,391 lines to 37,523,253 candidates | 0 match | 2026 (round 2) |
| Dedicated brainwallet dictionaries: bitcoin-brainwallet.lst and milw0rm | 478,946 lines to 2,292,116 candidates | 0 match | 2026 (round 2) |
| Full King James Bible, one verse per line | 60,100 lines to 725,198 candidates | 0 match | 2026 (round 2) |
| Canonical-source exact windows (Bitcoin whitepaper, KryptoKit press release, John Donne's "Meditation XVII", the genesis-block text, name masks, repetition masks), case and punctuation preserved | 1,959,326 candidates | 0 match | 2026 (round 2) |
| Song lyrics, most-viewed 301,000-song slice of a genius-song-lyrics corpus | 12,000,079 lines to 52,299,649 candidates | 0 match | 2026 (round 3) |
| OCR text from video frames (original, RuTube, HQ and 720p sources) plus 20 community guesses from the BitcoinTalk thread | about 1,588 OCR lines plus 20 guesses, about 501,600 to 509,399 candidates with variants | 0 match | 2026 (round 3) |
| Quotes-500K corpus (Goel/Madhok/Garg, ECIR 2018; original Drive link dead, run off the Hugging Face mirror jstet/quotes-500k, sha256 `8fa4c686...b69941` verified before use), quote field taken verbatim | 499,711 streamed (499,708 rows), 493,789 unique after dropping 5,919 in-corpus duplicates | 0 match | yes: the 3 sibling passphrases were planted at stream head/middle/tail and all 3 re-found by the same code path | ~362/s average CPU over 23 min (853/s cold, throttled) | 2026-08-23 |
| Genesis-block byte-string micro-family from SVN r133 main.cpp: coinbase scriptSig hex upper/lower, the backwards-text scriptSig string and its reverse, genesis pubkey literal, nBits/nonce/timestamp/block-hash literals, composite "486604799 4 <hex>" forms | 21 | 0 match | yes: 3/3 selftest vectors re-derived in the same process | - | 2026-08-23 |

Cumulative: about 95.5 million candidates across the rounds above, `FOUND` list empty every
time. The Quotes-500K and genesis-family rows above are witnessed negatives in this
project's strict sense; the pre-2026-08-23 rows carry the caveat below.

## Media channels checked, not brute-forced

- QR codes across 443 video frames: 4 QR payloads decoded; one is the passphrase for a
  different, already-claimed puzzle (#19), the rest are dust/tip addresses. None is #30's.
- OCR across 4 video sources at up to 720p (221 + 370 + 116 + 443 frames): recovers known
  passphrases for other, already-solved puzzles in the contest (#16, #18, #20) when tested
  against their own addresses, so the OCR and text-recovery pipeline itself is shown
  working; it recovers nothing that solves #30 at this resolution.
- Audio: the Morse tone is a single 1000 Hz layer, no secondary DTMF signal, fully
  re-decoded from scratch; nothing further is extractable from the audio track itself.
- No video source above 720p is currently reachable: both known YouTube video IDs for the
  original upload are dead (`sr8lBrtd9U4`, `Mbu9dD8ahgE`); a Wayback Machine index lookup
  for the video content itself (not the page) returns no archived stream, only the HTML
  page.

## Explicitly demoted, not an open lead

- The Cicada 3301 references surrounding this contest (a rail-fence cipher fragment, a PGP
  signature, the number "3302"): the PGP signature uses a non-standard header, "3302" is
  not prime (unlike the real Cicada 3301 group's own use of 3301, which is), and an
  associated image circulated with this material was found to be fabricated. Treated as
  contest flavor, not a channel to search.
