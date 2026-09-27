# Negatives ledger, FTPK Season 2

Dated 2026-07-26 unless noted otherwise.

## Page-naming scheme as a direct word oracle

Tested whether a game's page name, `sha256(word).html`, could be recomputed directly
from a BIP39 word to search for the right one without solving the game itself: all 2048
BIP39 words, 7 case and format variants each, against MD5, SHA1, SHA256, SHA512, and
SHA3-256, plus double-hashing, plus template variants ("game1", "jeu1", "level1" and
similar, with several salts), plus a 104,334-word system dictionary. 0 hits against the
11 known page names. Refuted as a word oracle: a positive control (recomputing
`sha256("game")`-style names against the dictionary) correctly reproduces all 11 known
page names, proving the negative is real and not a harness bug. The naming scheme's real
function is the meta-puzzle: the 11 known preimages, in game order, spell "the last game
has for url this sentence that is hashed", which names the URL of a 12th, hidden game.

## Per-game structural checks

- Game 1 candidate matching a famous Cold War barrier: an image of it sits behind an invisible link on the
  page. Decrypting Game 1's own cipher (a Vigenere cipher keyed to a well-known 2012-14
  puzzle series) reveals the author's own text naming both this image and a second
  hidden image layer as decoys. Refuted directly by the puzzle's own plaintext, not by a
  candidate sweep.
- Game 5: an early reading of a digit grid, taken as a matrix-diagonal transcription,
  produced a number that returned HTTP 404 when probed as a page name. A corrected
  reading, taken as a plain visual diagonal of the same rendered block, returned HTTP
  200, confirming the corrected transcription rule advances to a further step; the word
  itself is not yet fixed.
- Game 12 audio track: spectrogram analysis of the left, right, and left-minus-right
  channels (window size 16384) found no hidden image encoded in the spectrum. The track
  is genuine music, meaning the intended reading is a note-to-digit transcription (the
  method a Season 1 page by the same author uses), not identifying the recording itself.
- Game 10: 2 short sub-poems on the page were checked for an acrostic (first letter of
  each line spelling a word). Neither does.
- Image steganalysis: the second decoy image from Game 1 was checked for an LSB payload
  across 30 channel and bit-order layouts. Nothing found; no appended bytes past the file
  end either.
- No HTML comments or `data-*` attributes exist anywhere on the mirrored site.
- A public code repository for the author or any variant of the puzzle's name does not
  exist (checked via the GitHub search API, 0 results).
- `robots.txt`, `sitemap.xml`, and `sitemap-index.xml` all return HTTP 404 on the puzzle
  site: they do not exist and hide nothing.

None of these checks carries a planted witness proving a full 12-word sweep would find a
real answer if one were in scope, since 0 of the 12 words are confirmed yet; each row's
witness column reflects only whether that specific check's own harness was proven to
work (a positive control), not whether the derivation oracle has been exercised on a
real solution.

## Solid-red clue image (2026-08-27)

The 2025-06-03 post https://x.com/FTPKgame/status/1929833486514278892 is a 624x402 PNG
of uniform RGB(255, 0, 0): 250,848 pixels, 1 colour, no yellow, no EXIF/XMP strings, no
bytes past the IEND. Three days later the author wrote that "a little yellow in all
this red" would help, so if that yellow exists it is on a game page, not in this file.
Uncertified as a stego negative (no planted payload was pushed through the same
decoder and re-found); it is a pixel-count of this one file only.

## Live-site fetch (2026-08-27)

`findtheprivatekeys2.vercel.app/` and a hashed game URL both returned a Vercel
Security Checkpoint (HTTP 429 on `/`, HTTP 403 on a game page). The Season 4 hidden
page returned the same checkpoint. The hub `findtheprivatekeys.vercel.app/` returned
HTTP 200, as did Season 1 (`findtheprivatekey.vercel.app/home.html`). Wayback CDX
for `findtheprivatekeys2.vercel.app` has only the 2025-05-19 landing page as HTTP 200;
`home.html` and the hashed game URLs were never archived. This matches the author's
2025-06-05 posts announcing they would enable "Attack Challenge Mode" because
page-name probing was running up the request bill. A headed browser session the
same day reached the same checkpoint on Season 2, on every hashed game URL
tried, and on the Season 4 hidden page, and failed with "Failed to verify your
browser - Code 11". The hub still loaded in that session. A later fetch the
same date did get the pages; see "Live-site fetch, second pass" below.

## Player-comment harvest (2026-08-27)

@N4Khjir and @thedragon8383, the two accounts the author named on 2025-06-06, for
the Season 2 clue window through 2025-06-15. This is a source harvest, not a
candidate sweep: N4's pasted titles and body text, and the dragon's progress
replies, are recorded in `analysis/leads.md`. 0 twelve-word candidates were
run against the oracle in this pass besides the selftest teaching example.
Witness: the selftest mnemonic still derives
`0x50D7e097e61121140c19871F06eA6FeB6d14105b`. Uncertified as a negative on any
word, because no word was claimed.

## Extra 50-letter page names as concatenated BIP39 (2026-08-27)

N4's two extra paths,
`hdvpvgyqxzplxefvngacfsdsljxajfhtweksvlkihugghszomf` (Game 6) and
`gdjztvzuojmmsmuwrsudjhzdvvlkftfehnxxkbpilscjfljyyg` (Game 1 extra), 50
lowercase letters each. Hypothesis: either string is the order-helper named by
the 12 seed words concatenated with no spaces. Method: DP word-break against
the 2048-word English BIP39 list (max word length 8). Result: 0 reconstructions
of any word count, including 12. Witness: the author's teaching mnemonic
concatenated without spaces
(`claimcyclestaffclumpdomainjudgeboysessionrazortinyshouldercoconut`, 65
letters) is re-found as exactly those 12 words through the same code. Rate:
instant on one CPU. Date: 2026-08-27. These pages are not the concatenation
oracle.

## Game 9 digit strings as a lone index or as A1Z26 (2026-08-27)

Title `1211920`, body `3114`, from
https://x.com/N4Khjir/status/1927621634828939664.

- As a single 0-based or 1-based BIP39 index: both numbers are out of range
  (English list indices run 0 to 2047 / 1 to 2048). 2 candidates, 0 in range.
- A1Z26 partitions (digits grouped into values 1 to 26, each group a letter):
  title 8 letter strings, 0 English BIP39 words; body 3 letter strings, 1
  English BIP39 word (not printed; the page still has to show the grouping);
  title and body concatenated 24 letter strings, 0 English BIP39 words.
- Index-splits into two or more in-range numbers: title 54 (0-based) / 26
  (1-based) splits, body 7 / 7, concatenated 462 / 266. None of those is a
  12-word mnemonic. I did not treat a pair of list words as a seed.

Witness for the A1Z26 splitter: grouping the title as 12, 1, 19, 20 yields the
Game 2 page-name preimage already listed in `analysis/leads.md`, so the decoder
reproduces a known-good grouping. Applying that same splitter to the body, the
only English BIP39 partition is 3, 1, 14 = `can`. That is now the working
reading for Game 9, not a MATCH. Rate: instant. Date: 2026-08-27.

## Game 12 tweet screenshot (2026-08-27)

The author's 2025-05-27 image https://x.com/FTPKgame/status/1927326950692941869
is still served as tweet media: 329x188 PNG, black field, white text "Click
here to view the file". No Google Drive id is in those pixels. The Game 7
screenshot from N4 (`GsBJNjIW0AAW146.png`) returns HTTP 404.

## Live-site fetch, second pass (2026-08-27)

A later fetch reached Season 2 and the Season 4 hint page. Eleven listed
games, the extras, and the helpers returned HTTP 200. Two URLs that the
2026-07 notes treated as live now 404:

- Game 12 hashed path
  `2d80326b034b1aa616625ecb0febf8e9f58b125c5c43bc65f5d8ab6bd6cc1d36.html`.
  Witness: the same host still serves Game 11 at
  `1a06df824ed741b53c785079a6347f00eec5af82f9850775409ca69dff4068a6.html`
  (title `44 . C`, teaching address reproduced). The sha256 of the
  sentence "the last game has for url this sentence that is hashed" still
  equals that Game 12 hex, so the name is right and the file is gone.
- Game 5 continuation pages named by 13-digit readings of the on-page
  13x25 digit block. Five strings, all Vercel 404:
  `5578700735424` (main diagonal of 13x25), `2930362455644` (anti-diagonal
  of 13x25), `5687754201452` (main diagonal of 25x13), `5299334053960`
  (anti-diagonal of 25x13), `5532639166513` (column 0 of 13x25). Witness:
  Game 9 at its hashed URL still returns 200 with title `1211920` and body
  `3114`. A July 2026 note said one diagonal then returned 200; that helper
  is not hosted now.

Rate: one fetch per URL. Date: 2026-08-27. Not a negative on any seed
word. It is why Game 12 audio and the Game 5 number-URL step cannot be
finished from the current site.

## Game 10 Text 4 cipher (2026-08-27)

Monoalphabetic substitution on the fourth Game 10 text page. Method: crib
`QHO` = `THE`, then unique fill of the remaining letters. Plaintext is the
eight-line city poem quoted in `analysis/leads.md`. Witness: every
ciphertext letter maps to one plaintext letter and the result is grammatical
English. This is a decode, not a MATCH. Date: 2026-08-27.
