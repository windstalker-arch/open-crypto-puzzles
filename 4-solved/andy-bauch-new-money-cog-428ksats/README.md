# Andy Bauch: New Money, COG (428,206 sats, [SOLVED])

Andy Bauch, a Los Angeles LEGO-mosaic artist, exhibited a series called "New Money" at
Castelli Art Space in March 2018: each piece hides the private key to a cryptocurrency
wallet inside its brick pattern. Eight of the abstract "Bitcoin Initially Valued at $N"
pieces plus 2 others in the series have had their encoding reconstructed and their wallets
matched exactly, all from the artist's own published photos; I reproduced that reconstruction
myself from the same public images. COG, a photographic LEGO portrait triptych from the same
series, has never been solved and, as far as I can establish, was never publicly attacked
before this research: its escrow held 428,206 sats, untouched since 2017, until an unknown party swept it on
2026-09-25. The solver has not published the method. The research below is kept as it stood at
the time of the solve; if the solver reads this, an explanation of the plate-seam channel gets
full credit here.

## At a glance

| | |
|---|---|
| Author | Andy Bauch, [andybauch.com](https://andybauch.com/) |
| Published | 2018-03-23, opening night, Castelli Art Space, Los Angeles ([show listing, archived](http://web.archive.org/web/20180921114353/https://www.artsy.net/show/hijinx-new-money)) |
| Prize | 428,206 sats (about $270 at BTC = $63,000, 2026-08-16) |
| Chain | bitcoin |
| Escrow | `1HLodS8H2GoWbnBXWcz7EkY773dKdD4JEv` ([explorer](https://mempool.space/address/1HLodS8H2GoWbnBXWcz7EkY773dKdD4JEv)) |
| Last on-chain check | 2026-09-25: swept in block 968,565, tx `230bba19`, 427,072 sats out after fee; escrow now empty (the 428,206 sats had been untouched since 2017-12-31) |
| Status | SOLVED; swept 2026-09-25 by an unknown party, method not published |
| Puzzle type | pixel-code, physical-object |
| Target format | unknown; the address's one on-chain spend reveals a compressed public key, so a 52-character compressed WIF private key is the expected shape, P2PKH |
| Certified oracle | yes: `tools/oracle.py --selftest` (certified against the private key behind a solved sibling piece in the same series, BITCOIN $60) |
| What remains | nothing on-chain; the solving method is not public |
| Series | Andy Bauch, "New Money" (2016-2018); 10 of the series' pieces are solved and used here as ground truth |

## The puzzle as published

The gallery's press release for the show states: "Each artwork is imbued with secret keys to
bitcoin wallets, with initial values ranging between $20 and $90," and closes with an
explicit invitation: "assuming a clever viewer doesn't reverse-engineer the Bitcoin pattern
embedded in each piece and use it to empty out the digital wallet of its value." The gallery
cartel for COG itself reads: "Cog, 30,981 LEGO pieces, 141 3/4 x 36 in triptych, 2017." COG
sold during the show, for $14,000, to a private collector, and has not surfaced publicly
since. In an August 2024 podcast appearance the artist named COG directly as the one piece
from the show that remains unsolved, calling it "much, much harder in some ways than the
other pieces," and said "I think the puzzle is still waiting." Full quotes with dates and
links are in [clues/author-posts.md](clues/author-posts.md).

## What is understood

### Mechanism

Across the series, a private key is transformed into a pattern of colored LEGO bricks, then
read back the same way to recover it. Two approaches are documented in the artist's own
words: sometimes the whole canvas is an algorithmically generated tiling of the key (used and
proven on the abstract "$N" pieces, where the piece's own title gives the numeral base, for
example $60 means base 6), and sometimes an existing image has data embedded into one of its
regions (proven on 2 other pieces, DOGECOIN $10 and CANNABISCOIN $10, where the payload
occupies a 32x32 sub-region). COG is a portrait built from an existing photograph, not an
abstract pattern, which by the artist's own description of his two approaches points to the
second, region-based method for this piece specifically. Each panel is estimated at about
114 by 150 studs from the framed piece's physical dimensions; direct measurement on the
photos available finds 113 by 148 studs clearly visible, with the remainder likely hidden
under the frame.

### Derivation and oracle

```
python3 tools/oracle.py --selftest
python3 tools/oracle.py "<64 hex chars or a WIF string>"
```

`MATCH <address> (<compressed|uncompressed>)` on a hit, `NO MATCH` otherwise, exit 0 or 1.

### Certified against

`tools/oracle.py --selftest` reproduces the private key behind BITCOIN $60, an already-solved
sibling piece in the same series (its minikey, SHA-256'd per the series' own published
method, derives the piece's real, on-chain address). This certifies the general secp256k1,
hash160 and base58check pipeline used here; it does not depend on COG's own unresolved
encoding.

### Established facts

1. I confirmed the escrow holds a 428,206 sats residue, unspent since 2017-12-31 (checked via
   [mempool.space](https://mempool.space)).
2. I checked the address's one on-chain spend, from 2017-12-30, directly against the
   transaction: it reveals a compressed public key in its signature script.
3. James Stanley, a researcher unaffiliated with this project, solved 3 pieces of the same
   series within 48 hours in March 2018 using no special tooling: manual brick-color
   transcription, a brute-force script over 720 color-to-digit permutations, and a public
   brainwallet tool to check candidate addresses. I found COG absent from every one of 22
   archived captures of his published writeup: nobody had attacked it before this research.
4. I applied local color quantization at the same pixel density already available for COG and
   recovered a sibling piece's payload (CANNABISCOIN) with 0.92 agreement, so color
   resolution is not the limiting channel for a region-based reading.

## What has been tested

Full ledger in [analysis/tested.md](analysis/tested.md). Summary:

| Hypothesis | Volume | Result | Witness |
|---|---|---|---|
| Global tiling across the whole canvas | tens of thousands of configurations | 0 valid candidates | yes |
| Data in one region (9 assumptions relaxed one at a time) | about 2.3 million windows, 484 million decodings | 0 hits | yes |
| Raw key laid out as a pixel block | 6,290,064 keys | 0 hits | yes |
| XOR between the 3 panels | 2,616,768 keys | 0 hits | yes |
| Row-to-row displacement | 1,421,160 combinations | 0 valid checksum | yes |
| Mask to base58/ASCII text | all 3 panels | 0 valid checksum | no |
| Artist-vocabulary brainwallet phrases | 902 phrases | 0 hits | no |

## Open leads, ranked

1. **A photograph resolving individual plate seams, about 40 pixels per stud or more**
   (needs new information, from a specific person). Color is no longer the bottleneck; the
   remaining unruled-out channel is whether adjacent studs are one 1x2 brick or two 1x1
   bricks. COG sold to a private collector in 2018 and has not surfaced since; the artist's
   own site declares its published file as the original size, so a higher-resolution copy
   would have to come from the collector or the original sale's intermediary, not the artist.
   Full details in [analysis/leads.md](analysis/leads.md).
2. **Close the color-count gap in the region search** (bounded re-run). The sweep on COG only
   tried a 4-color local palette; a sibling piece needed 5 colors at the same character width.
3. **Pieces from the same series with no public photo yet** (OSINT, tooling ready).

## Solution

The escrow was swept on 2026-09-25 (block 968,565,
[tx `230bba19`](https://mempool.space/tx/230bba19d8e60803f36cb88f428c20dcc88fb431e0f611ddb05d3432fa8c5947)),
427,072 sats to `bc1qvzc2cgm99ewfmhrdadq6ru2m7296em7wefl6ca` after fee, a plain spend with no
message. Reported in [issue #35](https://github.com/floflo777/open-crypto-puzzles/issues/35) by
Andy00L. Whoever recovered the key has not published the reading of the piece; the method below the
line above is our own reconstruction and the exact plate-seam channel that COG uses is still not
public knowledge. If the solver reads this, a write-up of how the triptych was read gets full
credit here.

## Files in this folder

| Path | What it is |
|---|---|
| `clues/COG_PANEL_1.jpg`, `COG_PANEL_2.jpg`, `COG_PANEL_3.jpg` | the 3 panels as published on the artist's own site, byte-exact, 1,597 by 2,000 pixels each (the highest resolution known to exist) |
| `clues/author-posts.md` | dated quotes from the gallery listing, an artist interview, and an August 2024 podcast, with links |
| `analysis/tested.md` | the complete negatives ledger |
| `analysis/leads.md` | full notes behind the 3 ranked leads |
| `tools/oracle.py` | candidate checker, certified against a solved sibling piece's private key |

## Sources

- Andy Bauch, artist site: https://andybauch.com/
- "New Money" show listing, Artsy (archived 2018-09-21): http://web.archive.org/web/20180921114353/https://www.artsy.net/show/hijinx-new-money
- "New Money" show listing showing COG's $14,000 price (archived 2018-03-24): http://web.archive.org/web/20180324080626/https://www.artsy.net/show/hijinx-new-money
- ESCAPUZZLED Podcast, episode 7, 2024-08-14: https://www.youtube.com/watch?v=nAz4DogvdPA
