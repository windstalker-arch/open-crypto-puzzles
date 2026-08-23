# ncodemus: As Above, So Below (0.0617 ETH + 0.0617 WBTC, [DEAD END])

A multi-step image treasure hunt published on Reddit in August 2021 by an author signing as
"ncodemus": a single 5701 x 5701 pixel PNG packed with ciphers, memes, constellations and
red herrings, with a prize locked at the Ethereum address
`0xf91A8DcE13AD25E2c256235852F0E7220De2f3fe` (0.0617 WBTC from day one, native ETH added
later, about USD 1,800 at announcement). The first step of the hunt was revealed only to
buyers of an OpenSea NFT edition. No public solver ever documented reaching step one. On
2025-08-23, four years after publication, the entire prize was swept in a single day by an
unknown solver; I verified this on-chain on 2026-08-23. Whatever path they used was never
published, so there is no reusable method here - only the fact that the puzzle fell.

## At a glance

| | |
|---|---|
| Author | "ncodemus" (Reddit, OpenSea) |
| Published | 2021-08-28, [Reddit r/bitcoinpuzzles](https://www.reddit.com/r/bitcoinpuzzles/comments/p9dhjv/currently_over_us3100_in_this_puzzle/) (image on IPFS from 2021-08) |
| Prize | 0.0617 ETH + 0.0617 WBTC at sweep time (about $4,000 on 2025-08-23; ~$1,800 when announced) |
| Chain | ethereum |
| Escrow | `0xf91A8DcE13AD25E2c256235852F0E7220De2f3fe` ([explorer](https://etherscan.io/address/0xf91A8DcE13AD25E2c256235852F0E7220De2f3fe)) |
| Last on-chain check | 2026-08-23: swept 2025-08-23, only 0.0000642439 ETH dust remains |
| Status | DEAD END |
| Puzzle type | image-stego, pixel-code |
| Target format | unknown private key or seed phrase for the prize address (the author answered "private key or seed phrase?" with "... yes. ;-)") |
| Certified oracle | no: no derivation method was ever published by anyone |
| What remains | nothing claimable; the sweep is the end state |
| Series | none |

## Why this is a dead end

The escrow is empty. Blockscout's transaction history shows exactly one active day:
2025-08-23, when 0.0617 ETH went out (tx
`0x129d88a09e2b18acbafbae23b080228349f1a4af33fc8004972d6debd7a1451c`) and the 0.0617 WBTC
balance left in two transfers to two different addresses (`0x774eaBd...`, `0x774ed5a...`). The address
had been untouched otherwise since October 2021 apart from unsolicited airdrop dust
(wbtc.fi spam tokens, Unisocks drops in 2025). Whether the sweeper solved the intended path,
bought step-one knowledge from an NFT buyer, or found a shortcut, none of it was shared:
no write-up, no forum post, nothing. A puzzle whose prize is gone and whose solution was
never documented offers nothing further to test. This entry exists so nobody re-runs the
image through the same public leads that went nowhere for three years.

## The puzzle as published

The author's own description (OpenSea listing and Reddit thread): the image hides "easter-
eggs, memes, codes, hidden messages, historical tidbits, symbols, cryptocurrency lore, and
nods to famous puzzle artists (pip, coin artist, etc.) and internet mysteries (cicada 3301,
ascent, etc.)"; "buyers of this nft will get learn which of the many hidden wonders is the
actual first step of the hunt." In the Reddit thread the author confirmed the target is
wallet key material ("you are looking for the private key to a crypto wallet", then, asked
private key or seed phrase: "... yes. ;-)") and stated repeatedly that no first step would
be confirmed publicly. Full quotes with links live in the community notes repository linked
below; nothing is reproduced here.

## What is understood

### Mechanism

Not established, and now never certifiably establishable: the chain starts behind a paid NFT
gate ("which hidden wonder is step one"), so the public material alone is known to be
insufficient by design. Community research (HomelessPhD's repository, 2021-2025) mapped
several embedded elements without reaching step one:

- binary dot-groups in the corners spelling the meme text "this is fine";
- a Morse stream along one edge decoding to garbled English around "THE MOON GOD WENT TO
  MEET THE SUN GOD", partially corrupted or null-ciphered;
- five mermaids quoting the legend of Thessalonike with "He lives and reigns" changed to
  "It lives and reigns";
- eleven zodiac constellations with digits on their main stars;
- leetspeak on the Bitcoin logo reading "Selene says I'm just gazing at another easter egg,
  do you really think it's gonna be that easy";
- iceberg inscriptions including ALBERTI and FINNEY; Moon River lyrics; a Kanye Quest 3030
  reference; Photoshop document-ancestor EXIF chains; and more.

None of it produced key material before the sweep.

### Derivation and oracle

No oracle: the derivation chain is unpublished and its entry point was sold rather than
published. Any candidate would have been checkable only against the (now empty) address.

### Established facts

1. The prize address held 0.0617 WBTC from 2021-08-01; the author's Reddit updates tracked
   its value from ~$3,100 upward.
2. The full prize moved out on 2025-08-23 (ETH native + WBTC, two recipient addresses);
   verified via Blockscout history on 2026-08-23.
3. No public solve documentation exists anywhere I could find, before or since.
4. The original PNG lives on IPFS
   ([QmUVA5tq...](https://ipfs.io/ipfs/QmUVA5tq1qrUyQc6mLXUfcL5euw4tm3CXrVky2Jj4AJmbu/nft.png));
   the community notes warn that JPEG recompressions corrupt the fine detail elements.

## What has been tested

By me here: only the on-chain verification above; I did not attempt any image analysis,
because the entry point was paywalled by design and the prize was already gone when this
folder was created. The pre-sweep community effort (binary corner dots, Morse extraction,
edge detection, EXIF mining) is summarized in the linked notes repository with scripts; it
produced structure but no key material over roughly four years of intermittent work.

## Open leads, ranked

None. Reopening condition: the unknown solver publishing their path, which would be of
historical interest only.

## Files in this folder

| Path | What it is |
|---|---|
| `puzzle.json` | machine-readable manifest for the index |

## Sources

- Reddit announcement and status updates: https://www.reddit.com/r/bitcoinpuzzles/comments/p9dhjv/currently_over_us3100_in_this_puzzle/
- Original puzzle PNG on IPFS: https://ipfs.io/ipfs/QmUVA5tq1qrUyQc6mLXUfcL5euw4tm3CXrVky2Jj4AJmbu/nft.png
- Step-one NFT on OpenSea: https://opensea.io/assets/ethereum/0x9b54e03cb137e4157029e915fa00d76830251072/3
- Community research notes (HomelessPhD/AsAbove_SoBelow): https://github.com/HomelessPhD/AsAbove_SoBelow
- Prize address history (Blockscout): https://eth.blockscout.com/address/0xf91A8DcE13AD25E2c256235852F0E7220De2f3fe
