# Negatives ledger, Andy Bauch COG

Method for every row: a candidate reconstruction of the brick grid is decoded under the
stated hypothesis into a private key, both compressed and uncompressed P2PKH addresses are
derived, and each is compared byte-exact against `1HLodS8H2GoWbnBXWcz7EkY773dKdD4JEv` and
against 13 other addresses in the same series (some already solved, used as controls).
Acceptance requires exact address equality; a plausible-looking decoded string never counts
on its own.

| Hypothesis | Volume | Result | Witness | Date |
|---|---|---|---|---|
| Global tiling across the whole canvas (the method proven on the abstract "$N" pieces): a color-field offset scan (about 11,000 offsets per panel) plus a structural sweep over color count 2 to 32, character width 2 to 8, 8 reading orders, all offsets, and candidate lengths 30, 51 and 52 | tens of thousands of configurations across the 2 sweeps | 0 structurally valid candidates; period-30 multiples statistically indistinguishable from non-multiple control points | yes: the same detector finds the real, known periodic signal on other pieces in the series (BITCOIN $60, $70) and recovers a synthetic pattern reinjected after randomly repainting 85% of the grid | 2026 |
| Data inserted into one region of the image (the method proven on DOGECOIN $10 and CANNABISCOIN $10), 9 assumptions relaxed one at a time: cell size, region shape (103 shapes), panel overlap, white-as-symbol, minikey vs. hex, 16 reading orders, color count and character width pairs, repetition, 6 re-digitizations of the source images | about 2.3 million candidate windows, about 484 million decodings | 0 hits | yes: a known payload planted at signal-to-noise ratios up to 30, in several shapes and reading orders, is recovered every time before any negative is declared; the same 103 shapes pointed at DOGECOIN's own image correctly find DOGECOIN's real payload, not noise | 2026 |
| The raw 256-bit key laid out as a block (16x16, 8x32, 4x64) | 6,290,064 keys | 0 hits | yes: a known key replanted in all 3 arrangements is recovered | 2026 |
| XOR between the 3 panels | 2,616,768 keys | 0 hits | yes | 2026 |
| Row-to-row displacement (whole-row granularity only; segment-level displacement not tested) | 1,421,160 combinations | 0 valid WIF checksum | yes: an estimator for this channel is validated at 85.8% correct rows on a known injection | 2026 |
| Mask decoded as base58/ASCII text, 2 axes x 12 widths x 2 polarities | all 3 panels | 0 valid WIF checksum | no known-good calibration example for this specific test; reported as tried, not certified | 2026 |
| Brainwallet phrases built from the artist's own vocabulary | 902 phrases | 0 hits | no; a weak test by the researcher's own account | 2026 |
| Region-search at a 5-color local palette: base-5, 3 cells/char, minikey (30/34 char, SHA-256 -> key) decoded, full 120-permutation color->digit assignment set, S-prefix + alphabet minikey gate, 3 window shapes x 8 reading orders, sliding all 3 panels | 57,106 structurally-valid S-minikey candidates derived (every S-gated survivor; construction vectorized) | 0 hits | yes: a known minikey planted as a base-5 color block on a synthetic grid is recovered through the same reader/derive path (witness passes for K=5, cw=3) | 2026-08-31 |
| Region-search at a 6-color local palette, same wider model (720 permutations) | did not complete; terminated after >2 h of construction (exceeds AGENTS.md rule 5 budget) | — | NO: sweep abandoned mid-panel-1; a negative here would be uncertified. K=6 is also low-probability (COG's gray ramp is read as ~5 real levels per the 4/5-color precedent) | 2026-08-31 |

## What is confirmed, to prevent re-testing a false negative

- The color-extraction pipeline itself works: SWAGBUCKS, a sibling piece that initially looked
  mute, shows a genuine periodic signal once color extraction is corrected; a separate piece's
  translucent material caused an unrelated extraction problem. Neither piece "has no signal."
- A local 4-color quantization step lifted an early resolution ceiling: it recovers
  CANNABISCOIN's payload at 13 pixels per stud with 0.92 agreement, so color identity is no
  longer the blocking factor for a region-based reading of COG.
- The localized-region sweep run on COG covered color counts of 4 only; a sibling piece
  (SWAGBUCKS) needed color count 5 to find its real payload at the same character width. The
  same gap has not yet been closed on COG: this is a real hole in the coverage above, not a
  new hypothesis.
- **2026-08-31 update (corrected):** `tools/region_sweep.py` (committed now; the original 4-color
  region tool was never committed and was reconstructed here from the summary rows). An
  off-by-one in the gray-level quantization meant the first run produced k+1 distinct levels
  instead of exactly k, so its rows are SUPERSEDED by the corrected run below. With the
  quantization fixed and the color->digit assignment set expanded to the full K! permutations
  (plus an S-prefix minikey gate so full-`_assignments` stays bounded), the 5-color pass over
  all 3 panels derives every structurally-valid S-minikey candidate (57,106) with 0 hits and
  is a CERTIFIED negative (witness passes). The 6-color pass (720 permutations) did not
  complete within the 2 h phone budget and is UNCERTIFIED. Lead 2 is therefore substantially
  closed for the 5-color hypothesis under this reconstructed model, but remains open for
  6 colors and for any detail my reconstruction diverges from the original method (region
  shape set, char-width pairs, panel-overlap, repetition).
