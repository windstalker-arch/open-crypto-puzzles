# Wonderabbit: Prometheus (1,031,123 sats, [SOLVED])

WONDERABBIT, the performance-puzzle arm of the Bitcoin-only venue Cyphermunk House in London,
staged "Prometheus," billed as the world's first Bitcoin performance puzzle, in 2025. A 12-word
BIP39 seed was worked into the show's dramaturgy, music, text and design, expressed as words,
BIP39 wordlist indices, or 11-bit binaries, with some parts under an extra layer of encryption. A
paper companion programme was handed out at the show specifically to help solve it, but that
programme has never been published online, and no full recording of the show exists. I found the
escrow, confirmed a funding trap that could make it look already spent, and mapped every public
promotional trace, but there is currently no ciphertext to test against the rules: the puzzle is
gated on a physical object, not on computation.

## At a glance

| | |
|---|---|
| Author | WONDERABBIT (Cyphermunk House), author credited as PSyfer |
| Published | 2025 (Cyphermunk House anniversary show); spoken version at Camden Fringe, 2025-08-23 and 2025-08-24 |
| Prize | 1,031,123 sats (about $650 at BTC = $63,000, 2026-08-16) |
| Chain | bitcoin |
| Escrow | `bc1q3nxe7436s3mlrkyrg3uv2a40yt5dcmfu7tggx5` ([explorer](https://mempool.space/address/bc1q3nxe7436s3mlrkyrg3uv2a40yt5dcmfu7tggx5)) |
| Last on-chain check | 2026-09-28: swept in block 968,978, tx `2f5f60f6`, 1,030,810 sats out; escrow now empty |
| Status | SOLVED; swept 2026-09-28 by an unknown party, method not published |
| Puzzle type | bip39-seed, physical-object, text-cipher |
| Target format | BIP39 12 words; each word expressed as text, a 1-2048 wordlist index, or an 11-bit binary; derivation path (BIP44/49/84) not established |
| Certified oracle | no: see "Derivation and oracle" below |
| What remains | nothing on-chain; the solving method is not public |
| Series | none |

## The puzzle as published

The rules, published verbatim on cyphermunkhouse.com/wonderabbit: "1. A bitcoin private key is
hidden within Prometheus. 2. Part of the key is expressed with words. 3. Part of the key is
expressed with index numbers applicable to a list numbered 1-2048. 4. Part of the key is
expressed with 11 digit binaries. 5. Some parts of the key have a further layer of encryption.
6. The companion puzzle programme is intended to make the puzzle easier to solve." From
wonderabbit.org: "A seed is created through the rehearsal process and worked into the
dramaturgy, music, text and design of the show... The show is presented to a live audience who
must decipher the 12 words hidden within." The escrow address is published directly in the
WONDERABBIT Nostr account bio: "PROMETHEUS UNSTOLEN, https://mempool.space/address/bc1q3nxe7436s3mlrkyrg3uv2a40yt5dcmfu7tggx5,
Live seed puzzles since 889868," a block number matching the funding transaction one block later.
As of 2026-08-11 press coverage, the puzzle "remains unsolved."

## What is understood

### Mechanism

The rules describe three interchangeable native representations of a BIP39 word (the word
itself, its 1-2048 wordlist index, or its 11-bit binary form), with an unspecified subset of the
12 positions under an additional layer of encryption, and a paper programme meant to make the
whole thing solvable in the room. No script, recording, or programme scan has ever surfaced
online, confirmed by diffing three archived snapshots of the collective's own site
(2025-06-22, 2025-09-13, 2026-04-13). Only 10 short promotional clips (7 images, 3 videos)
survive. One image, captioned by the author "Massive clue on the floor," shows a word written in
red on a mirror at the venue, legible as either "FREE" or "TREE" at the available resolution.

### Derivation and oracle

No certified oracle exists in this folder, and none can be built yet: there is a documented
alphabet (the three word representations above) but no ciphertext (no words, indices, or
binaries have been extracted from the public material), so there is nothing for a checker to
compare against a candidate. A solver checks a candidate the same way I would: derive the BIP44,
BIP49 and BIP84 first receiving addresses for a 12-word candidate and compare each, byte for
byte, to the escrow address at
[mempool.space](https://mempool.space/address/bc1q3nxe7436s3mlrkyrg3uv2a40yt5dcmfu7tggx5).

### Established facts

1. The escrow held 1,052,123 sats funded across 4 transactions between 2025-03-28 and
   2025-06-15; 21,000 sats were spent back to the author on the same day as the first funding, 38
   minutes after being sent and 10 minutes before the 1,000,000-sats prize itself was funded.
   This is a documented self-test, not the prize moving; the current balance is 1,031,123 sats.
2. No puzzle programme, script, or PDF has ever appeared online, checked across three dated
   archive snapshots of the collective's own site.
3. The same collective ran a different, since-solved puzzle ("Hidden in Plain Sight," with
   Seedsafe.io): funded 500,000 sats on 2026-03-05, swept 2026-03-09, about 4 days later. When
   this collective hides a prize in material the public can walk through and see directly, it
   gets solved quickly; Prometheus has held for about 16 months specifically because the
   programme was never made public, not because a cipher is holding.
4. A third party publicly asked the WONDERABBIT Nostr account on 2025-09-03 whether the word
   "claw" appears in the seed; no public reply is on record.

## What has been tested

Full ledger in [analysis/tested.md](analysis/tested.md). Summary:

| Hypothesis | Space | Method | Result | Witness | Date |
|---|---|---|---|---|---|
| Puzzle programme findable via web archaeology | 3 archived site snapshots | diff across dates | no programme, script, or PDF ever appeared online | n/a: absence check, not a candidate search | 2026-08-02 |
| Encoded content hidden in the 10 recovered promotional media files | 10 files (7 images, 3 videos) | visual inspection | no cipher grid, wordlist, or anomalous glyph found; whiteboard numbers illegible at available resolution | n/a: absence check | 2026-08-02 |
| Other prize addresses hidden in the collective's Nostr history | 9,620 events | full scan | only 2 prize addresses found: this one and one already solved and swept by someone else | n/a: absence check | 2026-08-02 |

## Open leads, ranked

1. **Obtain the companion puzzle programme** (needs a person, low cost). The programme is
   explicitly designed, by the author's own rule 6, to make the puzzle solvable, and the
   collective has a stated incentive to circulate it: it sells re-stagings of the show. Emailing
   `emily.wonderabbit@proton.me` to ask whether the programme can be shared or purchased is the
   direct path.
2. **Ask the WONDERABBIT Nostr account a specific yes-or-no question** (needs a person, low
   cost). A precedent exists (the 2025-09-03 "claw" question), though unanswered so far.
3. **Watch for a third staging of the show** (ongoing, no cost). The author hinted at one on
   2026-01-22 ("needs a new stage. Any ideas?"); a new performance would mean a new programme.

## Solution

Swept on 2026-09-28 (block 968,978,
[tx `2f5f60f6`](https://mempool.space/tx/2f5f60f69779e32c87829203d000ebfe5fbf6dd82707a560d7f252d3b462365c)),
1,030,810 sats to `bc1qrzcf6kuh84nyk03lh9s2hlktcxm0ggydnn5nld`, a plain spend with no message.
Reported in [issue #36](https://github.com/floflo777/open-crypto-puzzles/issues/36) by Andy00L. The
solver has not published the method, and the companion puzzle programme was never made public. If
the solver reads this, a write-up gets full credit here.

## Files in this folder

| Path | What it is |
|---|---|
| `clues/author-posts.md` | the published rules, the Nostr bio, and dated quotes, verbatim with links |
| `analysis/tested.md` | the complete negatives ledger |
| `analysis/leads.md` | full notes behind the ranked leads |

## Sources

- Rules, Cyphermunk House: https://cyphermunkhouse.com/wonderabbit
- Show description: https://wonderabbit.org
- WONDERABBIT on Nostr: https://njump.me/npub1gclc9l83teatpeymmyawc8u4mzal9r0kvh58hq9rwvfy7ys2qn4sr6wdfh
- Escrow address: https://mempool.space/address/bc1q3nxe7436s3mlrkyrg3uv2a40yt5dcmfu7tggx5
- Fountain podcast, "Prometheus in Bloomsbury": https://fountain.fm/episode/j1EqMSvXTVqCfAo7b9eH
