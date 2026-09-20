# Author posts and quotes

The puzzle's author posts as "Jrk Bgrt" (handle `@SoWut`) inside a puzzle-specific
Telegram group; the group is not indexed at a stable public URL, so this file does
not quote it. What follows is the material that is verifiable at a public URL.

## GSMG.io, platform site

https://www.gsmg.io/

The platform presents itself as an automated crypto-trading service. The puzzle is
a separate, unpaid challenge hosted on the same domain; the escrow address was
first funded on 2019-04-13.

## bitcointalk topic 5532424, "Need help Puzzle GSMG.IO 5BTC"

https://bitcointalk.org/index.php?topic=5532424.0

Community discussion thread, active since 2025-02-18, including several solvers'
notes on the stage chain. Used here only to corroborate the public stage order, not
quoted directly.

## Reddit, r/bitcoinpuzzles

https://www.reddit.com/r/bitcoinpuzzles/comments/bf7siz/gsmgio_5_btc_puzzle_challenge/

https://www.reddit.com/r/bitcoinpuzzles/comments/dfwcqk/gsmgio_5_btc_puzzle/

Two community discussion threads, also linked from the community repository below.

## Community repository

https://github.com/puzzlehunt/gsmgio-5btc-puzzle

A community-maintained repository documenting the solved stages, referenced here
for the public stage-chain order (see `data/stage-chain.json`). Not mirrored in
this folder; consult it directly for the community's own write-ups.

## The puzzle's own published page content

The final page (reached after "the Architect Choice" stage) publishes its content
directly in the page body: a sequence of 1075 single-character tokens, an
image, and a base64-encoded block. This folder quotes only the short strings
that are the deterministic decoding of that published content, not an
interpretation: `matrixsumlist` and `enter` from the two ab-runs,
`lastwordsbeforearchichoice` and `thispassword` from the two z-separated digit
segments, `shabefourfirsthintisyourlastcommand` and `shabefanstoo` read directly,
and `anstoo` recovered as the sha256 preimage of the page slug that ends the
stream's phrase (see "What is understood / Mechanism" in the README and
`analysis/tested.md` sections 14 and 15 for how each is decoded). The
128-character base64 blob is reproduced in `tools/oracle.py` because it is itself
the object the final gate is built on.

## 2026-01-01 and 2026-07-12 official hints (NR additions, transcribed 2026-09-07)

The community repo `Naddiseo/gsmgio-5btc-puzzle` carries three hint screenshots
from 2026 that this folder did not previously mirror (`hints/2026-01-01-new-
year-hint.png`, `hints/2026-07-12-official-hint.png`, `hints/2026-07-12-other-
msg.png`). OCR transcriptions from the PNGs (tesseract, 3x upscale, 2026-09-07):

- 2026-01-01: binary text; decodes to "Happy new year! Make the best of
  everything. Oh, and here's a "tiny hint" <3." (higher and lower halves are
  spaced ~1 minute apart in the original screenshot.)
- 2026-07-12 official: "My close friends have the best chance of solving it (a
  few tried). But they don't have the skills some of you do." with the appended
  "NOTE: that is a hint."
- 2026-07-12 other message: "You know what. @SoWut this isn't a request for a
  hint but I don't thin... Oh....and before I fall asleep. I want to assume it is
  quite clear I held quite a secret in my head which I seriously wanted to share
  with the planet... for those who can understand what I meant... The "5" btc was
  never the actual prize. That was only a tiny fraction."

Interpretive read only, no mechanism deduced (nothing here is a candidate
string; nothing has been sent to the oracle): the "5 BTC was never the actual
prize, only a tiny fraction" line joins the "close friends" line as meta-hints
pointing at a personal/identity-level message held by the author rather than a
further mechanical cipher stage. Consistent with the author-identity candidate
family already swept negative (`analysis/tested.md` sections 106 and 108). No new
actionable input. See `analysis/tested.md` section 188 for the formal non-test
registration.
