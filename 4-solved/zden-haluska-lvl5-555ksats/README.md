# Zden Cryptopuzzle LVL.5 (555,550 sats, [SOLVED])

**Swept on 2026-09-22.** The escrow `1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7` was emptied in block 968,171 by
[transaction e2544433](https://mempool.space/tx/e2544433184d0fe4157ca10a8e1ce753bb52a7b0bbcf833740d7448ed25e8e8e),
551,745 sats to `bc1qw50q83k7psugw5z5548kwnxqqjxjxvx2pkvz0s`, a plain spend with no message,
reported in [issue #34](https://github.com/floflo777/open-crypto-puzzles/issues/34) by deviceio121.
Nobody has published the key or the reading of the hint as of 2026-09-26. The research below is
kept as it stood; if the solver reads this, an issue with the derivation gets full credit here.

## At a glance

| | |
|---|---|
| Author | Zden (Zdenek Haluska), [crypto.haluska.sk](https://crypto.haluska.sk/), [@Zd3N on X](https://twitter.com/Zd3N) |
| Published | 2018-11-09 (original image); corrected 2021-12-12 ([tweet](https://twitter.com/Zd3N/status/1060955171591766018)) |
| Prize | 555,550 sats (about $350 at BTC = $63,000, 2026-08-16) |
| Chain | bitcoin |
| Escrow | `1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7` ([explorer](https://mempool.space/address/1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7)) |
| Last on-chain check | 2026-08-16: funded and unspent (555,550 sats, across 4 funding transactions from 2018-10-20 to 2021-12-03) |
| Status | OPEN |
| Puzzle type | geometry, raw-private-key |
| Target format | a 256-bit private key as direct hex (not WIF, not BIP39), P2PKH |
| Certified oracle | yes: `tools/oracle.py --selftest` (certified against a standard public vector, private key 1; the puzzle's own rectangle-to-key reading is not certified, see below) |
| What remains | the exact meaning of 3 terms in the author's own published hint |
| Series | Zden's crypto.haluska.sk puzzle series (LTC, Codex, Demobit, Janus, HALV and others) |

## The puzzle as published

The puzzle is a single published image, `crypto5.png`, announced 2018-11-09 with the caption
"Level 5 - Find the private key in this image." A hint bundle followed on 2018-12-24: "Sum of
two consecutive following rectangles areas creates one byte of the private key. Apply more
operations to obtain the results in byte range." On 2021-12-12, after the puzzle had gone 3
years unsolved, the author republished the image as `crypto5fix.png` with the note "the
original release was uncomplete," struck out the word "consecutive" from the hint, and added
2 short white pixel lines plus a small 4-line pixel formula in the image's bottom-left
corner. No rectangle geometry changed between the two versions. Full quotes with links are in
[clues/author-posts.md](clues/author-posts.md).

## What is understood

### Mechanism

The image shows 64 rectangles in row-major 8x8 order. Each exposes 3 measurable quantities:
outer area (width times height), inner area (the area inside its border), and the shell (the
difference between the two). The hint states that the sum of 2 "following" rectangles' areas,
after an unspecified operation, forms 1 byte of the private key: 32 such bytes make the
256-bit key. The author's own MATLAB measurement script (in the community repository, see
Sources) defines 4 candidate spatial senses of "following" (simple consecutive order,
column blocks, column-major pairs, and interleaved columns). The 2021 pixel hint reads, once
corrected for an earlier transcription error, as "-1 times x plus 64 divided by x," where "x"
most likely refers to a per-rectangle border-thickness measurement, though this binding is
not confirmed by the author. The key is understood to be direct hex, not a WIF or BIP39
encoding: a base58/WIF character-stream reading was tried and never produces a valid checksum
(see [analysis/tested.md](analysis/tested.md)).

### Derivation and oracle

```
python3 tools/oracle.py --selftest
python3 tools/oracle.py "<64 hex chars>"
```

`MATCH <address> (<compressed|uncompressed>)` on a hit, `NO MATCH` otherwise, exit 0 or 1.
This oracle checks a finished 32-byte key candidate against the escrow; it does not implement
the still-open rectangle-to-key reading itself.

### Certified against

`tools/oracle.py --selftest` reproduces the address for private key 1 (the generator point),
a standard vector reproduced in Bitcoin educational material, unrelated to this puzzle. This
certifies the derivation pipeline (secp256k1, hash160, base58check) used by the oracle. The
rectangle geometry is separately certified: my measurements reproduce the author's own
published MATLAB script output on all 64 rectangles, exactly.

### Established facts

1. I confirmed the escrow is funded and unspent as of 2026-08-16 (checked via
   [mempool.space](https://mempool.space)), across 4 funding transactions from 2018-10-20 to
   2021-12-03.
2. My rectangle measurements (`data/rectangle-measurements.csv`) reproduce the author's own
   canonical output exactly, on all 64 rectangles, by 2 independent measurement methods.
3. The 2018 and 2021 images are pixel-identical except for 2 short white lines and the
   bottom-left mini-hint; no rectangle geometry changed.

## What has been tested

Full ledger in [analysis/tested.md](analysis/tested.md). Summary:

| Hypothesis | Volume | Result |
|---|---|---|
| Mini-hint formula bound to every channel, pairing and normalization | over 3,200 families | 0 match |
| Composed operations, offsets, 2-stage divide-and-modulo | about 3,000 keys | 0 match |
| Base/radix readings, nibble model, date-matrix reading | thousands of keys | 0 match |
| 1-byte author-error tolerance across 2,699 bases | about 155 million derivations | 0 match |
| 2-byte author-error tolerance across 12 bases | about 390 million derivations | 0 match |
| Raw sum over a constant divisor, 6 traversal orders | 212,406 configurations | 0 match |
| "Following" as a sorted-order neighbor | 153,736 unique keys | 0 match |

All of the above predate this folder's certified oracle; every row is reported as candidates
consumed, not as a witnessed negative in this project's strict sense.

## Open leads, ranked

1. **A clarification from the author on 3 exact bindings** (needs a person). What "x" means
   in the formula, the exact byte-range normalization, and the exact sense of "following."
   Full details in [analysis/leads.md](analysis/leads.md).
2. **A higher-fidelity source for the mini-hint glyphs** (needs new information).
3. **A wider author-error tolerance sweep** (bounded, low priority). About 660 million
   derivations per base tried, marginal expected value against lead 1.

## Solution

Swept on 2026-09-22 (block 968,171, [tx `e2544433`](https://mempool.space/tx/e2544433184d0fe4157ca10a8e1ce753bb52a7b0bbcf833740d7448ed25e8e8e)), 551,745 sats to `bc1qw50q83k7psugw5z5548kwnxqqjxjxvx2pkvz0s`, a plain spend with no message, after almost 8 years unsolved. Reported in [issue #34](https://github.com/floflo777/open-crypto-puzzles/issues/34). The solver did not announce and the reading of the hint's 3 undefined terms is not public; the sweep went to a fresh single-use address, which is consistent with a solver claiming the prize rather than the author reclaiming it, but this is not confirmed. If the solver reads this, a write-up gets full credit here.

## Visual inspection crops

These 20 files are exploratory crops kept from a visual pass over the published image. They sit
here because they were committed alongside the rest of that pass, not because any test depends on
them. Three facts, so the captions below are not read as more than they are:

- No test in [analysis/tested.md](analysis/tested.md) refers to any of them, and nothing in the
  repository references them before this section.
- None is a byte-exact crop of [clues/crypto5.png](clues/crypto5.png) or
  [clues/crypto5fix.png](clues/crypto5fix.png); each was compared against both at native scale and
  none matched, so the source region for each is unverified. Two of them are larger than those
  images in one dimension, so they cannot be crops of them at all.
- Every one holds only the values 0 and 255, meaning each is a two-colour black-and-white image
  rather than a greyscale crop.

Each caption therefore gives the region label from the filename, the pixel size, and the two-value
finding. None of them asserts what the puzzle image does or does not show.

![Formula-block region, 408x792, two-value black and white](images/formula_block.png)
*Figure 1. Formula-block region, 408x792, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![Column 40 of the image, first, 160x240, two-value black and white](images/glyph_00_col40.png)
*Figure 2. Column 40 of the image, first, 160x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![Column 44 of the image, sweep position 01, 160x240, two-value black and white](images/glyph_01_col44.png)
*Figure 3. Column 44 of the image, sweep position 01, 160x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![Column 48 of the image, sweep position 02, 160x240, two-value black and white](images/glyph_02_col48.png)
*Figure 4. Column 48 of the image, sweep position 02, 160x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![Column 55 of the image, sweep position 03, 160x240, two-value black and white](images/glyph_03_col55.png)
*Figure 5. Column 55 of the image, sweep position 03, 160x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![Column 59 of the image, sweep position 04, 160x240, two-value black and white](images/glyph_04_col59.png)
*Figure 6. Column 59 of the image, sweep position 04, 160x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![Column 63 of the image, sweep position 05, 160x240, two-value black and white](images/glyph_05_col63.png)
*Figure 7. Column 63 of the image, sweep position 05, 160x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![Column 70 of the image, sweep position 06, 160x240, two-value black and white](images/glyph_06_col70.png)
*Figure 8. Column 70 of the image, sweep position 06, 160x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![Column 74 of the image, sweep position 07, 160x240, two-value black and white](images/glyph_07_col74.png)
*Figure 9. Column 74 of the image, sweep position 07, 160x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![Column 78 of the image, sweep position 08, 160x240, two-value black and white](images/glyph_08_col78.png)
*Figure 10. Column 78 of the image, sweep position 08, 160x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![Column 82 of the image, sweep position 09, 160x240, two-value black and white](images/glyph_09_col82.png)
*Figure 11. Column 82 of the image, sweep position 09, 160x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![Column 86 of the image, sweep position 10, 160x240, two-value black and white](images/glyph_10_col86.png)
*Figure 12. Column 86 of the image, sweep position 10, 160x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![Column 90 of the image, sweep position 11, 160x240, two-value black and white](images/glyph_11_col90.png)
*Figure 13. Column 90 of the image, sweep position 11, 160x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![Column 94 of the image, sweep position 12, 160x240, two-value black and white](images/glyph_12_col94.png)
*Figure 14. Column 94 of the image, sweep position 12, 160x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![Column 98 of the image, sweep position 13, 160x240, two-value black and white](images/glyph_13_col98.png)
*Figure 15. Column 98 of the image, sweep position 13, 160x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![four-line region, 344x600, two-value black and white](images/minihint_4lines.png)
*Figure 16. four-line region, 344x600, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![digit band region, 1168x256, two-value black and white](images/minihint_digitband.png)
*Figure 17. digit band region, 1168x256, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![full-height region, 576x1176, two-value black and white](images/minihint_full.png)
*Figure 18. full-height region, 576x1176, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![lower-glyph region, 372x240, two-value black and white](images/minihint_lowerglyph.png)
*Figure 19. lower-glyph region, 372x240, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

![upper-glyph region, 372x252, two-value black and white](images/minihint_upperglyph.png)
*Figure 20. upper-glyph region, 372x252, only the values 0 and 255 present. Retained from the visual pass; source region unverified.*

## Files in this folder

| Path | What it is |
|---|---|
| `clues/crypto5.png` | the original 2018 puzzle image, byte-exact |
| `clues/crypto5fix.png` | the corrected 2021 puzzle image, byte-exact |
| `clues/author-posts.md` | dated quotes from the announcement, hint bundle, and 2021 correction, with links |
| `data/rectangle-measurements.csv` | width, height, outer area, inner area and shell for all 64 rectangles |
| `analysis/tested.md` | the complete negatives ledger |
| `analysis/leads.md` | full notes behind the 3 ranked leads |
| `tools/oracle.py` | candidate checker, certified against a standard public vector |

## Sources

- Zden, original announcement, X, 2018-11-09: https://twitter.com/Zd3N/status/1060955171591766018
- Zden, Christmas hint bundle, X, 2018-12-24: https://twitter.com/Zd3N/status/1077146640090316800
- Zden's puzzle site: https://crypto.haluska.sk/
- Community documentation and the author's own measurement script: https://github.com/HomelessPhD/Zden_LVL5
