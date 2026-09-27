# Tested (full negatives ledger)

The summary table in `README.md` shows the highlights; this file is the complete record.
Every row checks candidate passphrases against the fixed 24-word mnemonic under BIP84
`m/84'/0'/0'/0/0`, empty change and index 0, using `tools/oracle.py`'s derivation. Witness
for every row below: a control passphrase (`control_test_pw_42`) was planted in the same
engine run, recovered by the GPU pass, and independently reproduced by a second, separate
tool (btcrecover) on a subset of the corpus. The position of the control within each run
was not separately logged (no head/middle/tail triad recorded), so by this repository's
own standard this is a well-instrumented negative, not a formally exhaustive one.

| Hypothesis | Space (N) | Method | Result | Witness | Rate | Date |
|---|---|---|---|---|---|---|
| Author's own bundled wordlists (skullsecurity, as referenced in his own hints) | 705,613 | CPU derivation, BIP84 index 0 | 0 match | yes: control passphrase recovered | 12,700/s on CPU | 2026-06-13 |
| rockyou.txt raw | 14,343,467 | GPU derivation | 0 match | yes | 315,000/s on a rented GPU | 2026-06-13 |
| rockyou.txt with best64 mangling rules | 1,104,459,484 | GPU derivation | 0 match | yes | 690,000/s on a rented GPU | 2026-06-13 |
| Corey-specific corpus (108 words mined from his Medium articles, GitHub, and employer), raw plus 8 rule sets (best64, leetspeak, T0XlC, toggles3, rockyou-30000, OneRuleToRuleThemAll, d3ad0ne, dive) | 23,735,781 | GPU derivation | 0 match | yes | 690,000/s on a rented GPU | 2026-06-13 |
| Corey in-joke phrases (taglines from his articles), raw plus best64 and OneRuleToRuleThemAll | 2,808,334 | GPU derivation | 0 match | yes | 690,000/s on a rented GPU | 2026-06-13 |
| Two-word thematic combinator, 35 curated words, 6 join styles (none, space, underscore, dash, camelCase, PascalCase) | 7,350 | GPU derivation | 0 match | yes | 690,000/s on a rented GPU | 2026-06-13 |
| Human password lists: probable-v2-top12000, darkweb2017-top10k, xato-top-1M, ncsc-100k, raw and with best64 | 8,967,534 | GPU derivation | 0 match | yes | 690,000/s on a rented GPU | 2026-06-13 |
| Famous quotes plus the full BIP39 wordlist as a single-word passphrase | 29,201 | GPU derivation | 0 match | yes | 690,000/s on a rented GPU | 2026-06-13 |
| The decoded audio-puzzle message ("i am 24 words long and found on path 84") and 32 minimal variants (case, punctuation, spacing, spelled-out path) | 32 | GPU derivation | 0 match | yes | 690,000/s on a rented GPU | 2026-06-13 |
| Alternate BIP84 index paths (change/index 0/1, 1/0, 1'/0/0, 0/2) replayed on the Corey-specific corpus | 432 | GPU derivation | 0 match | yes | 690,000/s on a rented GPU | 2026-06-13 |
| Independent cross-check with a second, separate tool (btcrecover) on the Corey-specific corpus and combinator | 7,454 | CPU, btcrecover | 0 match | yes: recovers the same planted control | 1,000/s on CPU | 2026-06-13 |
| Safety-net replay on alternate purpose paths BIP44/BIP49: m/44'/0'/0'/{0,1}/{0,1} and m/49'/0'/0'/{0,1}/{0,1}, bech32 P2WPKH encoding compared to the target. Corpus caveat: the original 108-word file is not committed, so this ran on a rebuilt approximation (137 single words mined from his quoted articles/GitHub/employer + 16 signature phrases) | 153 candidates x 6 paths = 918 derivations | CPU derivation, oracle code with PATH varied | 0 match | yes: public BIP84 test vector (abandon...about -> bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu) re-found through the identical PATH-walk code; sister address reproduced | ~150 derivations/s | 2026-08-23 |
| Three-word thematic combinator (leads.md lead #3 extension). 39 curated words reconstructed from the puzzle's own material (original 35-word file not committed), ordered triples with replacement, 6 homogeneous join styles (none, space, underscore, dash, camel, pascal) = 39^3 x 6 | 355,914 | CPU derivation, multiprocessing Pool, oracle code, target-address equality gate | 0 match | yes: oracle selftest reproduced sister address + negative control; the `check` gate (return candidate only when address_for == target) verified reachable end-to-end; sister-address derivation reproduced in the same run path | ~440/s burst, sagging to ~90-115/s sustained under mobile power throttling (run took ~35 min) | 2026-08-27 |
| Parity brain-wallet word list (openethereum/wordlist res/wordlist.txt, 7,776 words), each word as a single-word passphrase, verbatim | 7,776 | CPU derivation, oracle code, `--stdin` | 0 match | yes: oracle selftest reproduced sister address + negative control in the same code path immediately before this run (oracle is target-address-specific, so no in-stream positive is plantable) | ~141/s CPU (7.1 ms each), run ~55 s | 2026-08-30 |
| 51 curated dev/thematic/mnemonic-word passphrases (each of the 24 fixed mnemonic words; the full mnemonic in lower/upper/title; famous "correct horse battery staple"; author/employer/tool names; article phrases "this is not meant to be solved", "prove the viability"; mnemonic fragments "please pull glide", "leopard alter piano") | 51 | CPU derivation, oracle code, `--stdin` | 0 match | yes: oracle selftest reproduced sister address + negative control in the same code path immediately before this run | ~141/s CPU, run <1 s | 2026-08-30 |
| 66 ecosystem/canonical example passphrases (hardware-wallet demo passphrases TREZOR/abc/123, common dev throwaways test/password/letmein, bitcoin/satoshi/nakamoto/mnemonic/passphrase nouns, thematic case variants, "the quick brown fox...") | 66 | CPU derivation, oracle code, `--stdin` | 0 match | yes: oracle selftest reproduced sister address + negative control in the same code path immediately before this run | ~141/s CPU, run <1 s | 2026-08-30 |
| New curated thematic/foreign family, not in any earlier row: single-word kitten/photo/secret/key terms in Spanish/French/German/Italian/Japanese romanized/Korean/Chinese; author and tool names not already in the 51-item curated or 108-word corpus list (coreyphillips, bitimage, bitbip, synonym); hyphenated and spaced variants; filename-style guesses (kitten.jpg, kitten.jpeg); thematic two-word foreign and English compounds; reversed names; numeric-appended (kitten2019/2020/2021, 0119, 1001900) | 49 + 37 = 86 | CPU derivation, oracle code, `--stdin` | 0 match | yes: oracle selftest reproduced sister address + negative control in the same code path immediately before both runs (oracle is target-address-specific, so no in-stream positive is plantable) | ~141/s CPU, both runs <1 s | 2026-08-31 |

Cumulative: 1,155,420,596 + 7,893 + 86 = 1,155,428,575 candidates tested plus the 918-derivation path replay above, 0 matches, across 17 families.

## Other channels checked, not passphrase sweeps

- **Steganography in `clues/kitten.jpeg`**: checked with exiftool (clean metadata),
  binwalk (finds only the JPEG structure, no appended data), and `strings` (compression
  noise only). The image is confirmed to be purely the entropy source for the fixed
  mnemonic; nothing else is hidden in it. Date: 2026-06-13.
- **"Part 3 of 3" of the author's article series**: does not exist. His Medium index lists
  exactly 4 posts (Bitbip, Part 1, the audio puzzle, Part 2) and nothing further, so there
  is no undiscovered article to mine for a passphrase hint. Date: 2026-06-13.
- **The author's separate "Bitcoin Audio Puzzle"**: fully decoded (FSK tones at 1080 and
  1260 Hz, demodulated with minimodem, yielding a Bitcoin transaction with an OP_RETURN
  message). The message describes a 24-word seed on BIP84, the same structure as this
  puzzle, but is not itself a usable passphrase (tested as one above, row 9).
