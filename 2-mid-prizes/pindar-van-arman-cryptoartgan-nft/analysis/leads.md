# Open leads, full notes

## 1. Frame-by-frame analysis of the "Act 1 - Review" artwork archive

The artist has published a zip of frame-by-frame renders of the Act 1 series on Arweave:
[arweave.net/jz0h8lraiEZlzJn2_e53vNi-tg2lYNljdu6PXukb55E](https://arweave.net/jz0h8lraiEZlzJn2_e53vNi-tg2lYNljdu6PXukb55E).
On a separate journal page (bitgans.com/journal, the entry titled "Prime skullGANs"), the
artist frames a "glitch" as a genuine visual artifact tied to prime-numbered pieces. This
image archive has not been analyzed frame by frame in this research; it is the one channel
untouched by every metadata-based search tried so far, and the place where a set of exactly
11 could live without showing up in any attribute table.

## 2. ~~Finish the on-chain metadata sweep~~ (INVALIDATED 2026-08-28)

The 513-row table only covers pieces that were assumed to have a supply of 1 when their
on-chain token IDs were constructed. About 132 token indices between 1 and 700 return 404
under that assumption and may hide undiscovered Act 1 pieces with metadata not present in the
table used here.

STATUS 2026-08-28: premise is invalid for this collection. Investigating to run the sweep I
re-derived the real on-chain identity of the prize NFT and the metadata mechanism:

- The prize "Magic Internet moneyGAN (445/512)" is an **ERC-1155 on the OpenSea Shared
  Storefront** contract `0x495f947276749ce646f68ac8c248420045cb7b5e`, confirmed via
  `balanceOf(0x18f87ec9c527aba1db44f715456bf28b0dae478d, id) = 1` against a public RPC.
- The on-chain token id is a **composite storefront id**, not a simple index:
  `0x55372173689c288552885d897d32f5f706f79aa6000000000002940000000001` (collection hash
  `0x55372173689c288552885d897d32f5f706f79aa6`, template 660, serial 1). 445/512 is an
  OpenSea *display* label, not the id.
- The contract's own `uri(id)` returns a **centralized** OpenSea URL
  (`https://api.opensea.io/api/v1/metadata/0x495f9.../0x{id}`); OpenSea marks the collection
  metadata "Centralized". There is no on-chain token-URI endpoint that returns 404.

Therefore "132 indices between 1 and 700 return 404" cannot refer to real addressable on-chain
token ids for this collection: the ids are huge composite storefront values (each
`collectionHash<<... | template<<... | serial`), not 1-700. Re-scoping the sweep to composite ids
collapses to the OpenSea API, which only returns whatever OpenSea has already indexed; it
cannot surface "undiscovered" Act 1 pieces that are absent from the table. The original
premise rested on a false linear-index assumption. Lead closed as a dead path; the genuinely
open on-device channel is Lead 1 (frame-by-frame of the Arweave "Act 1 - Review" archive).

## 3. A bounded 11! x 128 sweep, once an 11-word set is likely

If a specific 11-word set becomes a strong candidate without its exact order being known,
checking all 11! orderings against all 128 checksum-valid 12th words is a bounded computation
(reported at roughly 59 hours on 24 CPU cores), not an open-ended brute force. This is a
proposal to run once a specific set is argued for, not a search to run blindly across many
candidate sets.
