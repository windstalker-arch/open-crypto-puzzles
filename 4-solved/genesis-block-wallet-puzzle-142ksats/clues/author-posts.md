# Author posts, verbatim

Every message of this puzzle is an OP_RETURN output in a transaction that also pays the
escrow `bc1qfkhx02v89u2qyyyljeczw6hu9sr437y44t7ae5yf09thrdukfqesnjg2wj`. The author has no
other channel. The attribution below follows the transaction inputs: a message is the
author's when its inputs spend a change output of a previous author transaction (the
announcement is the anchor). Questions paid directly to an author change address were
re-posted by the author to the escrow before the answer; those re-posts are marked
"relayed". All times are UTC, read from the block timestamps on 2026-08-29.

## Announcement

2026-08-22 19:45:38, block 963,629, `b691de3657880d9a1eabd2783b1a9fa8c5313ced338495bf10e85727012d7a77`, 5,000 sats to the escrow:

> I made a Bitcoin puzzle using information contained in the genesis block created by Satoshi to generate the wallet.
>
> The entropy is extremely low. I didn't even need to back anything up. Everything I needed was already in the genesis block.
>
> Good luck!

The escrow had been funded with 20,000 sats 17 hours earlier
(`e2aaa928a965ee02b9c9a76227383113a62f350701a18d7792372712ce501ac7`, block 963,517,
2026-08-22 02:45:22, no message).

## Hint channel

2026-08-23 01:51:20, block 963,659, `248f690de194372564baa14e1bebf08154e2f2042ed205baa6157fdc0e3f22ea`, 5,000 sats:

> If you have a question, you can include it with a transaction sent directly to this address, and I will reply with a hint.
>
> Larger payments receive better hints. Dust transactions will be ignored.

## Questions and answers

| Time | Block | Txid | From | To escrow | Text |
|---|---|---|---|---|---|
| 2026-08-23 14:41:38 | 963,739 | `3b2f8aef7bb8f56dc939b34465906fd8a7693b2c8718d541ea635f8780313db6` | player 1 | 12,916 sats | Is the witness script a hash lock, a multisig, or something else? |
| 2026-08-23 15:43:56 | 963,744 | `0fb7a2f175dd7f9b8826cf2923ce4fcb56e4c7bfe252903e6dad1f87f177dfe3` | author | 12,916 sats | The witness script is a multisig. |
| 2026-08-23 18:19:26 | 963,758 | `268093b9ae56a59d2bb1a6acde588d6763fe859947b098c235031493208d3e22` | author (relayed, player 1) | 16,028 sats | How many keys, what threshold, and how are the keys derived from genesis? |
| 2026-08-23 21:08:58 | 963,768 | `ef63243d374d8eabeac7e17e06cc4b1b672146dc61a8e5180eeac980cec07302` | author | 16,028 sats | Two keys, both required. The rest is for you to derive. |
| 2026-08-24 06:40:09 | 963,823 | `fe27df994d658e79bea7b4cfe2427341ce024c70c5af21b76186807eebe57072` | author (relayed, player 1) | 6,345 sats | Are both keys from the same genesis field, and is the function a hash? |
| 2026-08-24 07:13:18 | 963,829 | `82a076b02643372769ac676d260ef4d9854c6bf49370ed61875fc63b8241dcfc` | author | 2,000 sats | Yes, both keys use the same Genesis field, and there is no hash. |
| 2026-08-24 08:58:20 | 963,837 | `2f5bbc7c0d031f54c9b7c8bee73eb2607d04b19019d1deac7f773eafdd1b91f8` | author (relayed, player 1) | 12,843 sats | Is the second key derived from the first, or both from genesis independently? |
| 2026-08-24 14:32:47 | 963,868 | `ff884832e937f972c92c012ba235ff45b549cd1702dfd02691056da6bc1ff913` | author | 2,000 sats | Both keys are derived independently from Genesis. |
| 2026-08-24 18:01:41 | 963,888 | `69d19cc41b8a5f1e711d46069e301bb4d29223bfcf1128eb6a9236e0d3e9b96c` | player 1 | 12,703 sats | Which genesis field, hash, merkle, nonce, time, headline, or pubkey? |
| 2026-08-24 21:35:20 | 963,910 | `eb609dfede7f61d3bf9fe79ae48e546c358ebd09c05b3cd64a22433cb784ea86` | author | 2,000 sats | The Genesis Block is public. Which part of it matters is for you to discover. |
| 2026-08-28 17:38:24 | 964,465 | `51b9f9521ca5bfae851b0f55dc3b151914b95f77eef156078a422396cd30cef2` | player 2 | 2,000 sats | Prize Address?Genesis field 32 bytes or smaller? |
| 2026-08-28 20:15:31 | 964,477 | `84fc5defe22590a02bbe0025831be110ed6f9e0bc53c3c835a4e42479b0bf050` | player 2 | 3,000 sats | Give a hint at your will! |
| 2026-08-28 22:45:35 | 964,486 | `610fc4d2ca1a214d99248c8188fd2973f4c51fca319ccf9ab983ac3edf4b1821` | player 2 | 3,500 sats | Can you give any hint about derivation offset/rule? |
| 2026-08-28 23:15:28 | 964,491 | `6e94cfcbc1350a138242f97310dfd0280371a0020380cb32b2512337470c1077` | author | 5,000 sats | Solve it to find out. Maybe both. (newline) If you can't check the Genesis block, you can also use The Times newspaper! |
| 2026-08-28 23:50:52 | 964,496 | `8be479605bc8f2facd2036fd1b7f5cfa3a3f3920eeffee75e0004a2cff4d25d6` | author | 3,500 sats | `Derivation rule: root -> multisig -> mainnet -> genesis_data -> script_type` |
| 2026-09-06 15:51:27 | 965,798 | `68e79190221d2b73089b523f7f5af2a11838339a788239f4eee30d6c1d4502e7` | player 3 | 1,000 sats | give another hint |
| 2026-09-06 19:41:00 | 965,824 | `64385a0cc5c4c712d1d9d8628e1e00364310d9ba50536ccd23c71b49ae66b96b` | author | 1,000 sats | I can't give hints without a question. Low-value transactions get bad hints; dust will be ignored. |
| 2026-09-10 20:47:36 | 966,402 | `75daa8e824abba4fe1b1a4b12f923b50291fab98743edaa1f03ef8c50bb70552` | player 4 | 10,000 sats | Root = Times text as BIP32 seed? BIP39? raw key? genesis_data = BIP48 account? |
| 2026-09-10 21:33:46 | 966,409 | `cb47c7a73c1aaa11bfe0edce41c2ef7c9c1fec1478efd15e40b226eb502dcc18` | author | 2,000 sats | root = the master key derived from the BIP39 seed; genesis_data = some data from the genesis block used as the BIP48 account number. |
| 2026-09-11 21:25:51 | 966,565 | `6497aef4be0d5be68644296d5fcdb709c66bb20db5972f4e53f90836e27862fe` | player 4 | 10,000 sats | BIP39 entropy: genesis bytes/puzzle text/img/other? words 12/24? passphrase Y/N? |
| 2026-09-11 23:26:17 | 966,576 | `f8f04fc04e2c4f34dc2264f85ff7944c6aa822446bc4cc082e95a52aed5c2a4c` | author | 2,000 sats | BIP39: 12 words; Passphrase: Y; Entropy: The data needed to solve it is publicly available in the genesis block. |

The three relayed questions were first paid by player 1 directly to the author's change
address of the moment, off the escrow's history: 32,357 sats on 2026-08-23 16:20:06
(`d271c37d8ce26247`), 6,465 sats on 2026-08-23 19:37:09 (`a2209eef7490846b`), 12,963 sats on
2026-08-24 03:35:54 (`f6579e67ff234ddb`). Player 1 also paid its first question twice, once
to the author (12,909 sats, `1b4bde84af7df419`, 14:34:56) and once to the escrow.


Player 4's two questions (2026-09-10 and 2026-09-11, 10,000 sats each) are, word for word, the
draft questions written in this folder's `analysis/leads.md` on 2026-08-29. I did not send them;
a reader did, and the author answered both within the hour.

## Solve period (2026-09-13 to 2026-10-17)

From 2026-09-13 a single solver ran a sustained, paid shape-only campaign on the escrow:
dozens of transactions, most of them asking the author to confirm or deny structural facts
(cut range widths, hex source, Ian Coleman settings, BIP48 account shape, passphrase
character classes) without revealing values. The full OP_RETURN log, both directions, is
readable on the escrow address; the arc and the load-bearing messages are below.

2026-09-13 (block 969,361): the solver's model hardens into `cut -b` on genesis raw hex.
Author answers the same day (block 969,361, `3678a0e393de3e66`):

> 1) hex; 2) substring/cut; 3) N

2026-09-13 (block 969,390, `b050d6450f7d12ee` and `41a68f4a564a4fc5`), author:

> 1) Y; 2) N (bitcoin-cli/explorer); 3) Y; 4) N

> 1) N; 2) genesis block; 3) Y; 4) Y

2026-09-15 (block 969,576, `d98ac606deeb8f2d`), author, shape-only on cosigner 0852014c
(questions 1-4), and the solver's question about the passphrase hint's meaning:

> Shape only, no secret values requested. For cosigner 0852014c (the one you confirmed used
> Coleman Hex): 1) Before sha256sum, did any command delete, translate or squeeze hex digits,
> beyond letter-case conversion and whitespace removal? Y/N; if Y, which operation? 2) Procedure
> = one SHA-256 of the UTF-8 hex text, first 32 hex digits of the digest as raw entropy,
> standard English BIP39, 12 words? Y/N; if N, which step differs? 3) Your hint 'first
> transaction' = a) genesis coinbase b) the 10 BTC payment in block 170 c) other: which
> block/tx? 4) Does the passphrase contain any character other than ASCII letters A-Z/a-z or
> a space (any digit, punctuation, accent, non-Latin letter)? Y/N

2026-09-16 (block 969,650, `719623a4f2c94413`), author. The passphrase nudge, paid for by
the solver and the only public sentence the author ever gave on the subject:

> 1) Y; cut -b N-M: it deleted everything outside the selected range.
> 2) Y.
> 3) Key question of the passphrase: Who received the first transaction? That's all I've got to say.
> 4) N.

2026-09-17 (block 969,708, `8c1e0c1b1e70d70c`), author, on fingerprint 0852014c and the
full path shape:

> 1) Is 0852014c the fingerprint of the depth-0 BIP32 master public key derived from the
> 12-word mnemonic with the BIP39 passphrase applied? Y/N. If N, which node does it identify
> (no account number needed)?
> 2) Are both escrow public keys at the complete path m/48h/0h/Xh/2h/c/i (any X), with either
> c=0 and i=0..9, or c=1 and i=0..4? Y/N. If N: a larger index, or a different path?
> 3) How many space characters does the passphrase contain, counting any leading or trailing
> space: 0, 1, 2, or 3+?

2026-09-26 to 2026-10-01: the author declines step-level test vectors as equivalent to
revealing the keys piece by piece (block 971,743, `3de07be481e97c9a`):

> Declined. For a test vector with predefined inputs, I can only provide the final result.
> Step-level answers would be the same as uncovering the individual secrets one by one.

but does answer fixed-cut final fingerprints (blocks 971,770 and 971,789, `39a7dd0c` and
`484fef192e43bd6c`):

> 1) e4caa034; 2) 9fb54bad; 3) e4caa034; 4) e79c9765; 5) 8b9b2fea; 6) 68ab4226; 7) 9290f941.

> 1) e4caa034; 2) 9fb54bad; 3) 3bc42789.

The same evening the solver paid 10,000+1,000 sats for a test vector with a substituted cut
range and BIP39 passphrase "Test Example" (blocks 971,753 and 971,770,
`f1aeed6d1fb79335` and `5b7ff44c779abced`); the author's final-fingerprint replies above
are the answers to those vectors, and the solver's own pipeline disagreed with them
(block 971,734, `f1027314f59377f9`), which is how the last pipeline mismatch was pinned
down before the sweep.

## Close (2026-10-17)

2026-10-17 03:40:20, block 971,803, `1c70c4745fad5bf891b9ee2a9f8b0b5cd3f328eb847eb09c9bebb92f5f7e900b`:
the sweep. 117 escrow inputs, 935,266 sats to `bc1qdu8mh9qjtjhy89mvhmcgf66ul6ld92rdr6qzad`,
no message.

2026-10-17 04:43:33, block 971,810, `bcfc8cbeb5498d803dc1b1384233eb5e9f2da79c2077b9a0907bc0187e2e4465`
(inputs from a third-party address, not the author's change chain; recorded as posted):

> "Shoutout to the player who cracked the puzzle!
>
> Thanks to everyone who joined in."

2026-10-17 05:43:52, block 971,814, `3367997d30d4b0363ff96e9fb587c28622a691044ab3ea9ce5c30c5d730b422f`
(inputs from the payout address; solver):

> "Thank you for the fascinating puzzle!"

2026-10-17 10:29:04, block 971,840, `4b2d29ec21e2c9a37dae5ca7ddc49d6f34b0efbf4b0aa1afed6405dec8067b78`
(inputs from the escrow's last two dust outputs; solver):

> "My GPU searched everywhere except the PBKDF2 settings. Well played!"

2026-10-17 17:01:47, block 971,886, `473a314bcb3f5abc8dc4500e8d0ab80525ff65a846d55406c1e1e10fa8c8e46c`
(author, PGP-signed):

> -----BEGIN PGP SIGNED MESSAGE-----
> Hash: SHA512
>
>               [ PUZZLE AUTHOR ]
>
>   Handle : CaesarCoder
>   GitHub : github.com/caesrcd
>
>   PGP Fingerprint:
>   E2A0 BF0D 72D7 4483 064D
>   4FF9 3049 5240 7A6E 5C38
>
>   "Every cipher tells a story.
>    Every puzzle bears its creator's mark."
>
>               -- CaesarCoder
>
> -----BEGIN PGP SIGNATURE-----
> (signature as posted on chain)
> -----END PGP SIGNATURE-----

Later same day the remaining dust that had trickled in after the sweep (question payments
relayed by third parties who had not yet seen the spend) was swept as well, bringing the
escrow's lifetime total received to 947,620 sats, fully spent.
