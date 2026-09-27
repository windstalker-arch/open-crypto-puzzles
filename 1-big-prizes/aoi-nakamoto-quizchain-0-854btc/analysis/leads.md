# Open leads, full notes

Ranked summary is in the README. This file has the reasoning behind the ranking.

## 1. Reconstruct the 2019 browser-copy rendering of the Wattpad chapter

The author states she typed the chapter with a blank line between paragraphs
("two line breaks... one 13 and one 10 for each"), but the chapter's current
storage (fetched through Wattpad's API, `modifyDate` 2019-07-23, matching the
2019-07-30 funding of the current escrow) contains no blank paragraphs at all:
Wattpad's storage format normalizes them away. What she actually hashed was most
likely whatever her browser produced when she selected and copied the rendered
page in 2019, not the raw API storage read today. A first attempt at simulating
this (Chromium's `selection.toString` and `innerText` rendering rules) is
included in the "simulated browser copy" row of `analysis/tested.md`, but it
used only one rendering assumption; the actual 2019 Wattpad reader page layout
(paragraph spacing, non-breaking spaces around punctuation, title block) has not
been reconstructed and tested as its own base text.

What would confirm it: rendering `data/chapitre_second_page.html` the way a 2019
browser would have displayed it, extracting the resulting paragraph text, and
running it (with the certified case-flip rule applied to the same candidate
paragraph groups already tested) through `tools/oracle.py`.
What would kill it: a faithful reconstruction still not matching after the
already-tested paragraph-selection hypotheses are re-applied to it.
Cost: hours, mostly in getting the 2019 rendering right; the derivation itself is
seconds per candidate.

## 2. Read the 27 posts and comments between the rehash and the shutdown

The author rehashed and refunded the Real Big Block on 2019-07-30, then stopped
posting shortly after. The 27 posts and comments she made between 2019-07-30 and
2019-08-04 have been read once for an explicit "twist" statement, but not
re-read systematically against the current, narrower list of untested paragraph
combinations.

What would confirm it: a stated detail (an extra modification, a further
paragraph, a corrected count) that, applied to the certified rule and re-tested,
matches the address.
What would kill it: a full re-read producing no new candidate paragraph or rule
variant beyond what `analysis/tested.md` already covers.
Cost: an hour of reading.

## 3. Two-character edits on the strongest base texts

The single-character-edit sweep (266,038,400 candidates, `analysis/tested.md`)
covers every one-character difference from 40 base texts and is exhaustive for
that distance. It does not cover 2-character differences, which would catch a
base text that is off by, for example, one inserted invisible character AND one
capitalization slip. A 2-character sweep restricted to the small set of NBSP and
line-ending pairs (rather than all positions) is a bounded space, not a full
40-base x 2-character search.

What would confirm it: a match within the bounded 2-character space.
What would kill it: exhausting that bounded space with 0 match; the full,
unbounded 2-character space is not proposed here, since its cost is
disproportionate without a narrower reason to expect the answer lives there.
Cost: on the order of an hour on a rented GPU for the bounded version described
above; the private research folder priced this at roughly 45 minutes per base
text for a similarly scoped variant.

## 4. Identify what "76" indexes for Block 76

A method confirmed on 3 other blocks in the same series (56, 57, 58) uses the
block's own number as a position index into a specific corpus (a numbered post
by Satoshi Nakamoto or Hal Finney on bitcointalk, read in a specific order). The
same method, tried against every corpus and ordering available (Satoshi's and
Hal Finney's bitcointalk posts, Hal Finney's tweets), does not produce a post
containing "change" or "from" at position 76. The corpus this method should
index for block 76 has not been identified; candidates not yet tried include the
complete list of Hal Finney's tweets (only 58 were recovered through the
official API; a fuller archive may exist), Satoshi's SourceForge posts, the
Bitcoin whitepaper or v0.1 source code read as a sequence of numbered units, and
the author's own r/Grycoin posts read as their own numbered sequence.

What would confirm it: a position-76 item in the right corpus containing "change
to" or "from change to", tested through `tools/oracle.py --block76-filter` and
then a full derivation.
What would kill it: exhausting the remaining candidate corpora with no match at
position 76.
Cost: minutes per corpus once a candidate corpus is assembled.

## 5. A short, human-reasoned answer to "change to" / "from change to"

The author's own hint structure (a short, freeform-text question plus a short
TOMI expansion, confirmed on more than a dozen other blocks) argues for a short,
punchy answer rather than a long dictionary phrase. The scripted sweep in
`analysis/tested.md` covers dictionary and corpus vocabulary exhaustively within
its stated bounds, but a human-reasoned short answer with unusual capitalization
or punctuation (the author's own confirmed style on other blocks, for example
"NGD" for "net zero" or "JD6" for "QWERTY") is a different kind of hypothesis
than a word-list sweep can reach.

What would confirm it: any short candidate, tested through
`tools/oracle.py --block76-filter` first (a near-instant filter) and then
through a full derivation.
What would kill it, in the useful sense: nothing kills this lead outright; it
stays open as a standing invitation, same as any human-reasoned wordplay block
in the series.
Cost: minutes per candidate; no sweep implied.

## Chapter-internal STNM hint passage (2026-08-28)

The "Second" chapter contains a self-referential passage (its paragraphs roughly
227-244) in which the author explains her own planted mechanism: every paragraph
starts with one of I/T/A/S/M except four, which start with F, F, W, W; taking the
last letters of those four F/F/W/W paragraphs (which carry the Hal Finney
quotation, with one I-starting paragraph between two of them) spells S-T-N-M, and
the nearby I paragraph combines to "I STNM", a deliberate echo of the "Nm ST"
signature in the genesis block and of the "I" that begins Satoshi Nakamoto. The
passage then points at "the first four and last four words of the paragraph
hinting at the solution" and closes the quote pair with "Today, Satoshi's real
identity" / "I recognize the signs" -> "Today, I" / "today I come out as
Satoshi".

This is a real, verifiable embedded pattern (the F/F/W/W last letters do spell
STNM), but it is the author's in-chapter *explanation* of the decoration layer,
not a new search space on its own: every selection it points to (the F/W/H
starters, the Finney-quote paragraphs, subsets of those candidate paragraphs) is
already covered by the 2^17 subset sweep and the F/W selector rows in
`analysis/tested.md`. A quick re-test of the Finney-quote paragraph set alone,
with and without the case-flip rule, plus the STNM/I paragraphs, joined with
`\n\n` (5 base texts), gave 0 matches. Recorded so the passage is not mistaken
for a fresh lead; it chiefly re-confirms lead 1 (the exact rendered byte
sequence, incl. blank-line separators, is what matters, not the paragraph
selection).

## Stage One reproduction: the MD5 and two reimplementation gotchas (issue #1)

stakeados (issue #1) wrote down the exact Stage One value, which this folder reproduced during
research but never recorded as a number:

- source: bitcointalk topic 155054, first post, raw HTML (ISO-8859-1, ASCII body)
- md5: `9dd2efb9bc976c2095bd534d7b8d431c`
- derives to `19TbyN5KCg1Lg7qHwezifsLVcdSa2Rj5KN` at `m/44'/0'/0'/0/0`

Both reimplementation gotchas they flag are already handled in `tools/oracle.py`, but neither
was stated in prose: a paragraph break is `<br><br>`, so a single `<br>` (as in the
"[edited slightly]" line) does not start a new paragraph; and the byte encoding is ISO-8859-1,
not UTF-8. Recording the MD5 makes the Stage One reproduction checkable without re-deriving
from the post.
