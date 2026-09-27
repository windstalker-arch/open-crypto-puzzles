# Tested (full negatives ledger)

No certified oracle exists for this puzzle: the target is a raw 256-bit private key with no
intermediate checksum, so every candidate below was checked by deriving its ETH address
(`eth_keys`, compressed public key) and comparing it byte-exact (case-insensitive on the hex)
against `0xFF2142E98E09b5344994F9bEB9C56C95506B9F17`. The derivation code itself (SHA-256,
Keccak-256, and secp256k1 point multiplication) is standard and was checked against public
test vectors, but I have no known-answer candidate specific to this puzzle to certify the
mapping from image to key, so every row below is "uncertified" in the sense that a clean run
proves the tested candidates are wrong, not that the harness would have caught every possible
right answer. I also flag near-misses (an ETH address starting with the same 2 bytes, `ff21`)
as an extra check; none occurred in any family below.

## Geometry-derived candidates

| Hypothesis | Space | Method | Result | Witness | Date |
|---|---|---|---|---|---|
| Building height/width/roof-y/x0 sequences (raw, sorted ascending, sorted descending, interleaved), joined with 5 separator styles, padded left/right to 32 bytes, first/last 32 bytes, 2-hex-digit encoding per value | about 460 candidates total across this and the next 3 rows | SHA-256, double SHA-256, Keccak-256, compared to target address | 0 match, 0 near-miss (no derived address even starts with `ff21`) | uncertified (no known-answer vector for this puzzle) | 2026-06-13 |
| Raw pixel hashes: grayscale channel, alpha channel, full PNG file, first/last 32 bytes of the flat grayscale array | included above | SHA-256, Keccak-256 | 0 match, 0 near-miss | uncertified | 2026-06-13 |
| cHRM chunk (32 bytes) and its byte-reversed form, raw and hashed | included above | direct, SHA-256, Keccak-256 | 0 match, 0 near-miss | uncertified | 2026-06-13 |
| Object counts (12 buildings, 1 large sail, 5 small sails, 2 clusters, left/right counts) as a byte sequence | included above | SHA-256 | 0 match, 0 near-miss | uncertified | 2026-06-13 |
| Matrix reshape of the grayscale channel at 7 column widths, first/last row and column strips | 56 strips | first 32 bytes, SHA-256 | 0 match, 0 near-miss | uncertified | 2026-06-13 |
| Value-band pixel masks (bands including 240 to 245, 235 to 254, 248 to 254, 1 to 30) | 4 bands | SHA-256, first 32 bytes | 0 match, 0 near-miss | uncertified | 2026-06-13 |

## Metadata-derived candidates (the date:create / date:modify anomaly)

The PNG's own `tEXt` chunks (confirmed present in `clues/arweave-puzzle-11.png`, reproduced
2026-08-16) read `date:create 2020-03-30T11:38:07+03:00` and
`date:modify 2020-03-30T11:34:44+03:00`: the modify timestamp precedes the create timestamp,
an anomaly present only in this puzzle and its sibling puzzle #9.

| Hypothesis | Space | Method | Result | Witness | Date |
|---|---|---|---|---|---|
| ISO date strings, digit strings, Unix epochs, and their difference/sum/XOR, in decimal and big/little-endian 4 and 8-byte encodings, alone and concatenated or XORed with the address and the cHRM bytes | dozens of encodings times {SHA-256, double SHA-256, Keccak-256, BLAKE2s, first 32 bytes, last 32 bytes} | direct address comparison | 0 match, 0 near-miss | uncertified | 2026-06-13 |

## Alpha channel and sibling-puzzle-calibrated candidates

| Hypothesis | Space | Method | Result | Witness | Date |
|---|---|---|---|---|---|
| 260 near-white pixels from the sibling puzzle #9's own 8-level image, tested as a carrier under many bit orders (raster, polar, radial), bit widths (1 to 3 bits per pixel, MSB and LSB first), and symbol mappings, plus several passphrase guesses hashed with SHA-256, double SHA-256, and Keccak-256 | several hundred combinations | address comparison, calibrated against puzzle #9's real (and already spent) address as a positive control | 0 match, 0 near-miss on #9 itself (so the method is confirmed not to reproduce the known #9 answer either) | yes, on the #9 positive control only | 2026-06-13 |
| Container-level myths (embedded executable or filesystem inside the PNG) | full file | binwalk, manual chunk inspection | refuted: file is a clean, valid PNG (IHDR, gAMA, cHRM, bKGD, pHYs, 22 IDAT, 3 tEXt, IEND chunks), 0 bytes after IEND; the "executable" reports from other solvers are binwalk false positives on near-random decompressed pixel bytes | yes (direct chunk inspection) | 2026-06-13 |
| Alpha channel as a data carrier | full channel | direct pixel inspection | 434 pixels have alpha under 255, all clustered on the large sailboat's outline (an anti-aliasing halo from a copy-paste), values 1 to 30, consistent with a smoothed edge rather than structured data | yes | 2026-06-13 |

## What the ~460-candidate geometry sweep and the metadata sweep together rule out

Between the two families above, on the order of 1,000 candidates were checked, all through the
same address-comparison harness, with 0 matches and 0 near-misses anywhere. This rules out
every direct, single-transform reading of the measured geometry and the metadata anomaly that I
was able to enumerate. It does not rule out a reading that depends on information outside this
image, such as the promised but never-delivered "$100" hint (see "Open leads, ranked").

## Bit-level windowed scan (Lead 1, run to exhaustion 2026-08-28)

This is the previously-untested, highest-ranked lead: a systematic bit-level scan of the two
continuous 8-bit channels (grayscale 256 levels, alpha 26 distinct values) with a tool built
for that exact purpose. Both channels, all 8 bit-planes (0-7), bit widths 1/2/4/8, LSB- and
MSB-first read orders, and every contiguous 256-bit window of each extracted bitstream, plus
whole-stream SHA-256 / double-SHA-256 / Keccak-256 / BLAKE2s and raw 32-byte prefixes. Every
candidate was checked by deriving its ETH address byte-exact against the target.

| Hypothesis | Space | Method | Result | Witness | Date |
|---|---|---|---|---|---|
| Raw contiguous 256-bit window of the grayscale and alpha extracted bitstreams (planes 0-7, widths 1/2/4/8, both read orders) | ~1.5 M window positions across both channels (22 configs x ~220k-1.77M windows) | `tools/lsb_window_scan.py`, `tools/plane_window_scan.py`, `tools/alpha_run.py` (parallel, 8 cores) | 0 exact match; only ~20 incidental derived addresses sharing the `0xff21` prefix but diverging at byte 3 (never `0xff2142...`) | uncertified | 2026-08-28 |
| Whole extracted bitstream and 32-byte-prefix hashed as a private key | 112 candidates (SHA-256, double-SHA-256, Keccak-256, BLAKE2s of each stream, both channels) | `tools/stream_hash_scan.py` | 0 match, 0 near-miss | uncertified | 2026-08-28 |

Result: Lead 1 (the direct pixel-value bit-level reading, the author's "format does not matter")
is now run to exhaustion with no match. Combined with the prior raw-pixel hashes and geometry
sweeps, every mechanical on-device reading of the image's pixel values and bit planes is now
closed. The two surviving leads (community Telegram group, and a published #9 method) both
depend on external information with no on-device channel.
