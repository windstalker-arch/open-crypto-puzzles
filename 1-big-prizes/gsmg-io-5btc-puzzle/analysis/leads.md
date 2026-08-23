# Open leads, full notes

Ranked summary is in the README. This file has the reasoning behind the ranking.

## 1. Replay the dynamically-constructed candidates that a filter bug never reached

The 2026-07-28 review (see `analysis/tested.md`) found that an appearance-based
acceptance filter had been silently rejecting the correct answer shape in 98 of 213
historical scripts. A first replay already resubmitted 116,043 literal strings
harvested from those scripts directly to the real address comparison (0 match, see
`analysis/tested.md` row 8), but that replay covers literal strings only. The same
scripts also constructed candidates dynamically at run time: token concatenations,
permutations of decoded fragments, and chained transforms (for example, applying a
Vigenere step and then a substitution step in sequence). Those dynamic candidates
were generated, passed through the same broken filter, and discarded, but were
never logged as literal strings, so this first replay cannot reach them.

What would confirm it: re-running each script's own candidate-generation logic
(not just its final output) with the filter bug fixed, and finding a match.
What would kill it: exhausting the same generation logic with no match; since the
scripts number in the hundreds, this is judged in stages, not as one pass.
Cost: hours to days, since the generation logic differs script by script and each
needs re-reading before it can be replayed correctly.

## 2. Determine whether the 256-symbol object is the right object at all

Every hypothesis in `analysis/tested.md` rows 1 to 5 assumes the final key comes
directly from the 256-symbol, 23-letter object produced by the puzzle's Bifid
decoding step. That assumption has one point in its favor: of the 7 possible
letter-pairs that could be removed from the 285-letter pre-reduction stream to
leave exactly 256 symbols, exactly one (the pair I and O) yields a Base58-valid
alphabet, which is unlikely to be accidental. But the object itself is written
entirely in uppercase letters, and an all-uppercase Base58 encoding of 32 bytes has
a chance of about 1 in 10^17 of arising by coincidence, which argues against reading
it as a literal Base58 string (consistent with row 4 and row 5 both being negative).

What would confirm it: a reduction of the object to 32 bytes, other than the ones
already tried, that matches an address.
What would kill it, or redirect it: establishing that the final key instead comes
from the AES-blob route this folder's oracle implements (`tools/oracle.py`), or
from the still-unopened "Dualite" blob, making the 256-symbol object a waypoint
rather than the key's direct source.
Cost: an afternoon of directed reasoning, not a sweep; this lead is about which
object to target next, not about enumerating more of the current one.

## 3. Identify the tool the author says was used at every phase

An authenticated statement from the puzzle's author says the same software was used
to build every phase of the puzzle. Comparing the cipher conventions confirmed on
already-solved stages against one specific, publicly available cipher tool's source
code shows an exact match on non-obvious implementation details: the tool's Bifid
implementation takes no period parameter (it always uses a period equal to the full
message length, which is exactly the convention confirmed on this puzzle's own
Bifid step), and its available cipher list is short. If this identification is
right, it bounds every remaining cipher hypothesis to that tool's own menu, instead
of the space of all published ciphers.

What would confirm it: a cipher from that tool's menu, applied with its default
conventions, producing a match on a currently unexplained object (most plausibly
the "Dualite" blob's password, or the reduction step from the 256-symbol object).
What would kill it: the author naming a different tool, or every cipher on the
identified tool's menu being exhausted with no match.
Cost: the tool's menu is short (documented in the private research as fewer than a
dozen ciphers); testing all of them against the currently open objects is a matter
of hours.

## 4. Follow "esrever" the first published hint

The earliest hint attributed to the author reads "esrever" ("reverse" spelled
backwards) applied to a specific decoded object early in the puzzle. This hint
predates most of the puzzle's later stages and has not been exploited on the
current final-gate objects (the 256-symbol object, the small blob, or the
"Dualite" blob), only on the object it was originally paired with.

What would confirm it: applying a reversal (of reading order, of case, or of the
described object itself) to one of the current final-gate objects and getting a
match.
What would kill it: exhausting the small set of reasonable "reverse" readings
(string reversal, bit reversal, reading-order reversal) on all three current
objects with no match.
Cost: minutes to hours; this is a small, well-defined space, not a sweep.

## 5. Read the 29 symbols dropped during the object-256 reduction

Reducing the 285-letter pre-reduction stream to the 256-symbol object drops exactly
29 letters (the I's and O's removed to reach the Base58-safe alphabet). Every
hypothesis so far treats those 29 letters as discard.

Status as of 2026-08-23: the sequence is now extracted, in extraction order:
`OOIIOOOIIOOIOIIOIOOOOIOIIOIOI`. Every element is I or O, so the object is binary or
nothing. Read as a 29-bit integer it gives 103993525 (I=1) or 432877386 (O=1); neither
is a recognizable constant, and Morse and Baconian readings do not resolve. The simple
readings are exhausted without a legible fragment; what remains open is whether the
bits select positions, gate another object (the even-position stream of lead 8 is a
natural candidate), or encode a short instruction under a framing not yet guessed.

What would confirm it: any reading of those 29 bits that yields a legible fragment or,
combined with another object, a match.
Cost: minutes per reading; this is a reasoning lead now, not an extraction one.

## Where the "Dualite" blob and the second address fit

The "Dualite" blob (see the README's mechanism section) is confirmed to be
well-formed AES-CBC ciphertext, not noise, and has never been successfully
decrypted under any tested password (`analysis/tested.md` row 6). No lead above
targets it directly with a password sweep, because no password-generation
hypothesis for it currently has more support than any other; leads 2 to 4 are the
routes most likely to produce one.

## 6. Re-run anything that was tested through the shipped oracle

Not a hypothesis about the puzzle, but the precondition for trusting any result from this
folder's own tool. Until 2026-08-19 `tools/oracle.py` derived the AES key with
EVP_BytesToKey/MD5, which fails on every blob in this puzzle whose password is known
(`analysis/tested.md` section 10). Any candidate previously pushed through it was compared
against a key the puzzle does not produce.

What would confirm it: nothing further; the derivation is now certified against the
phase-2 blob, and the selftest asserts that MD5 fails on the same blob.
What this changes: negatives obtained through the shipped oracle are void rather than
negative. Section 9's sweeps have been re-run under the corrected derivation. Anyone who
swept this pipeline independently before this date should assume the same.
Cost: the pipeline runs at about 76,800 candidates per second per core, so re-running a
past sweep costs roughly what the original cost.

## 7. The small blob is on the SalPhaseIon page, not the final page

The README described the small blob as published on the final page reached after the
Architect Choice. It is published on the SalPhaseIon page,
`gsmg.io/89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32`, reached by a
different route: hashing the text of the first puzzle page. Verified by reassembling the
blob from that page's own single-character token run, where the two 64-character halves sit
at token positions 916 and 1020 with a 40-character run of a and b between them; reading
that run as a=0, b=1 gives the five bytes `enter`.

Why it matters as a lead, not just a correction: the password should be sought in the
instructions on the page that carries the blob. That page decodes to exactly two
directives, `lastwordsbeforearchichoice` and `thispassword`, which read together as a
statement that the last words before the Architect Choice are this blob's password.
What would confirm it: a reading of those "last words" that matches.
What would kill it: exhausting the candidate texts. Section 9's last-N-word sweeps are a
first pass over the texts currently held and are negative; they do not exhaust the
instruction, because the phase-1 page is an image whose own wording is not transcribed
anywhere in this folder.
Cost: hours, and it needs sources rather than compute.

## 8. Decode the even-position stream of the Bifid output

The Bifid reconstruction on the original-era SalPhaseIon capture (see
`analysis/tested.md` section 14) exposes an object no public source accounts for: the
even-position stream of the 570-letter output, 285 symbols drawn from only four
letters (B=54, C=90, D=72, E=69). A quarter of the alphabet carrying every
even-position slot for 285 slots is an authored channel, not chance. The odd-position
stream is already accounted for (it is the 256-symbol object), so this channel is
either a second message, a key or mask for the first one, or the "second way" the
author said exists and was never found.

First readings (Morse roles, Baconian partitions, base-4 to bytes under all digit
orders, decimal-to-hex conversions, coordinate recombination with the odd stream,
Vigenere shifts) all failed to produce anything legible; see section 14 for the list.

What would confirm it: any encoding that turns the 285 symbols into a legible string,
a key that matches an address, or a mask that reduces the 256-symbol object to a match.
What would kill it: exhausting the reasonable encodings of a four-symbol alphabet at
length 285 with nothing; note the length factors as 3 x 5 x 19, and 57 five-bit groups
and 95 three-bit groups both divide it exactly.
Cost: hours of directed reasoning, not a sweep.

## 9. Preimage the seven remaining hash-slug routes

Ten 32-hex gsmg.io slugs exist beyond SalPhaseIon; three fell in one evening to
sha256 of lowercase concatenated puzzle phrases (`ourfirsthintisyourlastcommand`,
`hopeisthequintessentialhumandelusion`, `anstoo`; see `analysis/tested.md` section 15).
Seven remain open, listed there. The pattern is confirmed: lowercase, spaces removed,
phrases from the puzzle's own text. Each new transcription of stage wording (the
phase-1 image wording above all, which is not held anywhere in this folder) is also a
batch of preimage candidates.

What would confirm it: a preimage whose page carries content (the `anstoo` page has
no archived captures, so its value could not be checked).
What would kill it: exhausting the transcribed vocabulary against all seven.
Cost: minutes per batch through sha256; bounded by sources, not compute.
