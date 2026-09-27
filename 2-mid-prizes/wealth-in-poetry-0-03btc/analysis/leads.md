# Open leads: Wealth in Poetry

## 1. Read the cipher table on the embedded Steganographia photo [CLOSED - 2026-08-31]

The embedded Steganographia image is the **1606 Frankfurt edition title page**, not a cipher
table. Verified by OCR of the full-resolution download (4000x2297, via the Wayback Machine of the
Medium article; direct Medium returns 403):

- OCR reads the complete title-page text: title panel, "Reuerendissimo ... Ioanne Trithemio,
  Abbate Spanhemensi", "PRAEFIXA EST HVIC OPERI SVA CLAVIS", and the printer imprint
  "Officina Typographica Matthaei Becker / Ioannis Berneri / A[nn]o M.DC.VI" (1606).
- The page contains **no numeric cipher table** - only the title panel, author line, the clavis
  note, and the imprint. A letter tabula recta lives in the book's body, not on this title page.
- Article HTML confirms the figure (caption "Fellows' Library M.7.7 Gall. (C) Jesus College,
  Oxford") sits in the **references/bibliography section**, and the bibliography itself cites
  "Trithemius, Johannes, Steganographia. Frankfurt, 1606." It is a citation illustration, not a
  puzzle key.
- The worked-example paragraphs ([33]-[35]) and the "clavis" line refer to the numeric-key
  mechanism already calibrated; no new key source is present on the photographed page.

Killed: the photographed page yields no numeric key table. No derivation space is added by this
lead.

## 2. Rule out an old-Electrum (non-BIP39) wallet [CLOSED - 2026-08-31]

Rule-out completed and certified by `tools/oracle.py`, which succeeds and exits 0 only when an
Electrum mnemonic's seed, its m/0/0 P2PKH address, and its m/0/0 child xprv all reproduce when
derived two independent ways (bip_utils and the electrum package). `SELFTEST OK` covers both
Electrum V1 (checksummed) and V2 (BIP39-word) formats.

    python3 tools/oracle.py --selftest   -> SELFTEST OK (exit 0)

With the oracle certified, the four clean example seeds (PHONE `faint ... payment`, GPS
`asset ... honey`, the broken WITCH `witch ... least`, and `abandon ... about`) were run through
it: 0 match. PHONE, GPS, and abandon are not even valid Electrum V1/V2 mnemonics; WITCH is valid
Electrum but its derived addresses do not hit the escrow. Killed: no old-Electrum-format wallet
is produced by any of the demonstration seeds, and the Electrum derivation path itself is now
proven (certified) to accept a correct candidate, so an Electrum-format answer, were one ever
found, would be caught. Lead closed on the same certification standard as leads 1 and 3.

## 3. Build a certified acceptance test for the derivation code [CLOSED - 2026-08-31]

The derivation is done by the central `tools/derive.py`. A `--selftest` command was added
enforcing four known-good BIP39 seed-and-address vectors end to end (bip44, bip49, bip84, eth,
for the standard `abandon ... about` test mnemonic with empty passphrase). It prints
`SELFTEST OK` and exits 0 only if every vector reproduces. Verified here:

    python3 tools/derive.py --selftest   -> SELFTEST OK (exit 0)

Because a passing run re-derives each known-good address from the seed, the
BIP39-mnemonic -> seed -> BIP32/44/49/84 -> address pipeline is now proven to accept a correct
candidate. Every address-comparison negative in analysis/tested.md from 2026-08-02 that ran
through this code is therefore certified on the derivation math: a "NO MATCH" there means the
derivation correctly recognized no match, not that the checker is unproven. (The negatives
still describe numeric-key / carrier search coverage, not the author-specific words.)
