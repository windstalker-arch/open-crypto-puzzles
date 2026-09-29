# Open leads, full notes

Ranked summary is in the README. This file has the reasoning behind the ranking.

## 0. Decode the two raw digit streams on the final page (top open item)

The final page's token stream carries two digit strings over the alphabet {a..i}
(plus one trailing `z` marker on the longer): `dbbib`-headed at 91 tokens and
`faed`-headed at 570 tokens. These are transcribed verbatim into
`data/finalpage-digit-streams.json` (ingested 2026-08-27; they were not in this
folder before, which itself was a gap: the folder's `data/salphaseion-streams.json`
holds only the already Bifid-decoded output, not these raw final-page streams).

Why they are the tie point: the puzzle's own decoded instruction token
`matrixsumlist` calls for summing a matrix, and the only objects left unexplained
on the final page are these two streams. An independent multi-session community
analysis (puzzlehunt/gsmgio-5btc-puzzle issues #93 and #106, ~2.5B tests overall)
concluded the same: the decode method of these streams is the last unexplained step
and "likely what matrixsumlist instructs", and swept all mechanical dimensions
(KDFs x modes x all four blobs x ~56k principled candidates, zero genuine hits)
without it. #93 diagnoses `dbbib`=key vs `faed`=payload (VIC / straddling-checkerboard
style, escape digits ~1 and 4), and #106 proposes the canonical value mapping from
the Bifid square rows (D=0,B=1,I=2,F=3,H=4,C=5,E=6,G=7,A=8,K=9).

What would confirm it: a decode yielding a legible instruction or a string X whose
sha256 decrypts the small blob to `1GSMG1JC9` (or a password for the Dualite blob,
gate `17ucy1K9...`).
What would kill it: showing the streams are a decoy or padding, or exhausting the
keyed-checkerboard constructions (the construction needs the keyed alphabet, which
is the crux).
Cost: this is an insight problem, not a sweep; the naive reads are already negative
(see `analysis/tested.md` section 23).

The vocabulary-keyword family of keyed alphabets (the most direct candidate set) is
now closed as negative: the Wayback-era (Nov 2020) static captures' vocabulary clue
tiles give keywords `banking-war`, `ca`, `dig-i`, `lock-lo`, `crypto-gic`, `n-you`,
`open-lock-n-ing`, `t` and their fusions, and the straddling checkerboard of both
streams under both plausible digit mappings fails for all of them (`analysis/tested.md`
section 25). The deck/alphabet families are closed too: Solitaire-generated
alphabets (section 26) and two-joker (triple-cut) rearranged alphabets using the
trailing `z` as the joker marker (section 27) are negative. The Bifid-derived
alphabets (the Bifid keyed-square row, the lean-23 constructed alphabet, and the
literal `dbbib`/`faed` streams as keywords), plus the `matrixsumlist`-as-digit-sum and
`faed`-paired-to-even_stream readings, are negative too (section 32). The keyed alphabet
remains the crux and is still not reconstructed.

2026-09-13 status: the last structural gap is now closed  -  the certified
FUBCDORA.LETHINGKYMVPS.JQZXW board (phase-3.2.2 gate) applied to dbbib(91)/faed(570)
as straight checkerboard, as transpose-then-checkerboard (7x13 & 15x38 grids),
as matrix-sum readings, and via Beaufort/Vigenere under the 7 page tokens, plus
base-9 pair reading, is all negative (`analysis/tested.md` late-58). The two
streams remain the author-cited never-decoded artifacts; every single-classical
reading in the tested toolbook now returns noise.
2026-09-29 CORRECTION (second pass, `R-DBBIBFIELD2`): the dbbib half of late-58
and FOUR further families  -  the ciphertools 19-cipher suite, its composed
combinations, the z-segment Bifid family, and the keep-one-position / XOR
half-triangle readings  -  were all closed on the superseded 69-token crop, not
on the authoritative 91-token object. Cross-referencing every stale tool against
the rows that cite it found 18 PRE-2026-09-07 rows whose dbbib side is void under
BUG-2's own rule; four families had no post-reinstatement `dbbib_91` coverage at
all, including the ciphertools menu this file calls "closed". All four have now
been re-run on `dbbib_91`: 1,270,255 oracle-line evaluations, 0 MATCH on either
funded gate, so the closures now hold on the right object. A truncated dualite
oracle run (191,310 of 237,824 lines, cut mid-stream) was caught and re-run to
completion rather than reported as `MATCH=0`. `tools/stream_field_audit.py`
(24/24) enforces the field split and was itself corrected twice: broadening it
exposed `zseg_bifid_sweep.py`, and it then over-corrected into a false positive
on `phase322_literal_sweep.py`, which is now pinned as a key/label false-positive
regression test. That pass left 12 rows void-but-unrepaired (an earlier count of 14 in the
same paragraph was an over-count, corrected in `R-DBBIBFIELD3`) and 29 tools stale;
neither is claimed as cleared.
2026-09-29 CORRECTION to the paragraph above (`R-DBBIBFIELD`): the dbbib half of
late-58 was computed on the WRONG OBJECT. `tools/lead0_vicgap.py` read
`d["dbbib"]` - the superseded 69-token OCR crop - while printing `dbbib(91)` on
every line, so the certified 91-token object was never actually tested by that
family. The crop is the authoritative object with a 22-char run deleted at
offset 45, and 91 = 7x13 while 69 is not, so the grid was silently truncated
too. late-58 has now been re-run on `dbbib_91`: 393 candidates x both oracles,
0 MATCH, all top scores degenerate - so the CONCLUSION stands, but it is a 2026-09-29
conclusion, not a 2026-09-13 one. This also falsifies late-150's BUG-2 assurance
that "recent sweep rows were all re-derived on the live 91-token object", and 34
tools (not the 5 BUG-2 named) still read the crop; `tools/stream_field_audit.py`
now enforces the split mechanically. The faed half of late-58 is unaffected.
2026-09-13 addendum: chain-2 (C2, salt b45a5e3d827593ca) is confirmed ALREADY
decrypted in the ledger (briefcase/MEMORY.md)  -  not a lock to attack.
2026-09-27 addendum: that "already decrypted" is now certified rather than reported -
C2 opens under the DERIVED password WIF(K_C1) and reproduces `B2_79B.bin` byte-exactly
plus its own ciphertext on re-encryption (`R-B2RUNG2`, `tools/rung2_b2.py`). Read the
earlier "B2 has no envelope" claims (`R-B2FAIL`, `R-YINYANG-B1B2`) as superseded: they
swept authorial strings, and this password is a value computed out of B1. B2 is therefore
a dead end on-chain (all four ladder keys unfunded, none a gate) and the search frontier
stays on the image, not on the ladder. New object
this session: Bifid(DBIFHCEG) decode of the AUTHORITATIVE 91-token dbbib =
`BDFCDCHLBEBQFCFW...` (sha ac4f5a9f..., tested.md late-59); it fails as a
mutual co-key vs the faed Bifid output, and the four chain keys
(K_C1/K_C2/K_S1/K_S2) plus 525 chain4 block hybrids all point-check != gate.
Lead 0 rank unchanged.

## 1. Replay the dynamically-constructed candidates that a filter bug never reached

## 1. The third door: the preimage of the unmessaged planted address

The creator funded, from the vanity wallet `3GSMG24TujqfMJG1kQoBX18DzJHQLeJYMK`, one
address per stage answer with the SHA-256 of the answer as its private key, and two
"Good job, Neo!" addresses whose keys are the raw and bit-reversed bytes of the image
URL (README, "Planted addresses"; `data/planted-addresses.csv`). The one address funded
without a message, on 2020-04-07, `1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9`, has no known
preimage. It was planted four days after the two door markers, between the January
2020 poem and the April 2020 audio hint, and the creator named it in December 2020 as
a verification address and a year later said that door was "still a thing"
(Telegram, reported). It is an exact, free, offline oracle: a candidate is hashed (or
padded, or bit-reversed) into a key and its compressed and uncompressed P2PKH
addresses compared to the list, at about 176,000 keys/s per core.

Everything textual is negative under the six constructions (`analysis/tested.md`
sections 18 and 19): the puzzle's vocabulary, the system dictionary, short word
windows of every text and of the three films, `gsmg.io/` paths, the image's text and
numbers and colour masks, the 8 image texts, every page hashed, the phase 2.1 riddle,
prime-rank derivatives of the digit objects.

What would confirm it: an address match.
What would kill it, family by family: the creator's rules from that window, "Yellow
has a number and so does Blue", "primes", "zeroed out", read on a non-textual object
and exhausted; then, when noise is acceptable, a GPU brainwallet pass (SHA-256
construction) over large dictionaries and a CPU pass for the raw construction, which
is at most 32 bytes and therefore a short phrase.
Cost: seconds per family on a CPU; the GPU pass is minutes.

## 2. Both 80-byte locks, with extended readings

The phase 3.2.2 blob (2019, inside the phase 3.2 plaintext) and the SalPhaseIon small
blob (2021) have the same shape: `Salted__`, 80 bytes of ciphertext, 64 to 80 bytes of
plaintext. "The private keys belong to half and better half" precedes the first,
"yinyang" is announced as the phase after the second, and the creator's 2021-07-18
"neighbors, half and double" transaction pays the uncompressed addresses of 2P and P/2
of the prize key. A working hypothesis is that the two plaintexts are the two halves,
two keys or a key and its double or half. Every password is therefore tested against
both locks, and every plaintext with valid padding is read 40 ways (as is, reversed,
bit-reversed, doubled, halved, plus or minus one modulo n) before the oracle. The
11,473 valid-padding plaintexts from sections 15 to 17 have been re-read that way, 0
match.

What would confirm it: either lock opening.
What would kill it: nothing bounded; it is a discipline applied to every password
family, not a space of its own.
Cost: none beyond the families themselves.

## 3. Replay the dynamically-constructed candidates that a filter bug never reached

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

Status check 2026-09-06 (batch 2): the on-device replay approximations are now RUN for
both lead halves -- residue-RUN insertion at all 129 blob cut points + transforms
(section 179, 258 cands), the index-scheme family (sections 177/178), and the rendered
continuous digit field through every certified triangle/half-pair/join technique
(section 180, 304 cands) -- all NO MATCH on both gates; the esrever/ROT/Atbash keyword
route is checked closed by cross-section (section 181). The private script archive itself
still cannot be replayed here; the slug-literal half remains bounded by row 8's 116,043.

Status check 2026-08-27: the historical scripts that constructed candidates
dynamically at run time (token concatenations, permutations of decoded fragments,
chained transforms) live in the private research and are not in this catalog, so
their exact generation logic cannot be replayed here; this is the same blocker as
lead 2/5. The literal half is already bounded by row 8's 116,043 substrings plus
section 9's vocabulary/pair/window sweeps (all negative). The wording-mining half
was advanced: the newly-recovered phase-2 and phase-3 passwords, the coinbase
phrase, and both raw final-page digit streams were pushed through the certified
oracle as answer X (11 candidates, 11 NO MATCH, section 31) - all negative. The
remaining untried untranscribed source is the phase-1 image wording, which this
folder does not hold.

## 2. Determine whether the 256-symbol object is the right object at all

## 7. Determine whether the 256-symbol object is the right object at all

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

Resolved (section 30, 2026-08-27): the redirect case wins. The object's alphabet is
exactly the 23 contiguous uppercase letters A-Z minus {I,J,O} (a constructed Bifid/square
lean alphabet, not a random base58 subset), its letter counts are strongly non-uniform
(S=26,N=26 versus Z=1,V=4,Y=4 - the fingerprint of an encoded message, not key material),
and its direct reductions are exhausted (rows 1-5, 335M+). The uppercase-only object cannot
be a literal Base58 key. The key comes through the AES-blob pipeline (answer X, sha256,
decrypt) or the Dualite blob, and the unknown X must be sought in untranscribed puzzle
wording rather than in this object. Re-score this lead as effectively closed as a
"correct-target" question; it redirects to finding X in wording.

## 3. Identify the tool the author says was used at every phase

## 4. Identify the tool the author says was used at every phase

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

Status check 2026-08-27: the discriminating convention (Bifid with period left blank
= full message length, i.e. no forced period parameter) is confirmed present in at
least one major public cipher site (Boxentriq's Bifid tool documents "Period length:
Optional ... Leave blank to use the full message length"). But that site's cipher menu
is large (40+ ciphers), which contradicts this lead's "short menu (fewer than a dozen)"
premise, so the fingerprint does not uniquely select a tool from public sources alone.
The identification that would let us enumerate the short menu lives in the private
research and is not in this folder, so this lead cannot be advanced to its terminating
test (exhaust the exact short menu) here; it stays open but is not locally actionable
without that identification. The common-denominator ciphers of any realistic short
menu (Vigenere, Beaufort, Bifid, straddling checkerboard/VIC). CORRECTION (2026-09-04): Beaufort was previously claimed "already swept" here, but a full-tree audit found it was NEVER run as a candidate; tested.md section 131 now actually sweeps it (560 candidates, all NO MATCH on the small gate). The other common ciphers here have been swept
against the open objects with the recovered keys (sections 14, 25-29).

Status check 2026-09-04: the puzzle's own phase-3.2 hint names a concrete tool -- "Go to
https://ciphertools.co.uk/decode.php ... choose Beaufort". Inspected that tool (pulled its
JS bundle `index-B_H4mUOu.js`): it is a custom F#/Elmish SPA (Bulma CSS, renders into
`#elmish-app`, legacy PHP at /decode.php), NOT a WordPress plugin/site (no WP engine, no
wp-content). Its full cipher menu is exactly 19 ciphers -- AFFINE, AMSCO, AUTOKEY, BEAUFORT,
BIFID, CADENUS, CAESAR, FOURSQUAREMANUAL, HILL, NIHILIST, PLAYFAIR, PLAYFAIRMANUAL, PORTA,
RAILFENCE, SUBSTITUTION, SUBSTITUTIONMANUAL, TRANSPOSITIONSIMP, TRANSPOSITIONCOL, VIGENERE
(+2 helpers TOSINGLECHARTXT, SPLITTEXTINTOWORDS). It includes Bifid with a numeric
`BifidPeriod` field defaulting to 0 (blank -> full-message-length convention, the lead's
discriminating feature), so it satisfies the Bifid fingerprint -- but its menu is 19 ciphers,
NOT "fewer than a dozen", and it has NO VIC/straddling-checkerboard entry. So ciphertools.co.uk
is a closer real-world candidate than Boxentriq for the "single tool" (it is the one the puzzle
itself names), yet it still does not fully match the private-lead's short-menu premise, and its
VIC-lacking menu means the community's checkerboard dbbib/faed decodes could not come from it.
The WordPress hypothesis is not supported by the puzzle's named tool.

## 4. Follow "esrever" the first published hint

## 5. Follow "esrever" on the remaining objects

The earliest hint attributed to the author reads "esrever" ("reverse" spelled
backwards). On the object it was paired with, the image's binary code, it is now
explained: the 192 bits of `gsmg.io/theseedisplanted` reversed are the private key
of the second "Good job, Neo!" address (`data/planted-addresses.csv`). It has not
been exhausted on the current final-gate objects (the 256-symbol object, the two
locks' plaintexts beyond the extended readings of lead 2, or the "Dualite" blob).

What would confirm it: applying a reversal (of reading order, of case, or of the
described object itself) to one of the current final-gate objects and getting a
match.
What would kill it: exhausting the small set of reasonable "reverse" readings
(string reversal, bit reversal, reading-order reversal) on all three current
objects with no match.
Cost: minutes to hours; this is a small, well-defined space, not a sweep.

## 6. Read the 29 symbols dropped during the object-256 reduction

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
STATUS: the gating direction is now closed. Sections 178 (mask over first-29 of
faed/dbbib) and 183 (2026-09-06: mask + DIRECT/CUM position-walk over
even_stream/object_256/odd_pre_reduction/plaintext interleave, both bit orders,
104 unique x 2 gates) -> NO MATCH. dropped_29 as a select-mask/gate on every open
channel obiect is oracle-negative on both funded gates. See tested.md 178/183.

## Where the "Dualite" blob and the second address fit

The "Dualite" blob (see the README's mechanism section) is confirmed to be
well-formed AES-CBC ciphertext, not noise, and has never been decrypted: the
community's "decrypt" is a padding accident (`analysis/tested.md` section 14), and
9,252 passwords tested for a nested layer inside it found none (section 17b). The
second address is the halving split-off, not a payout (README, "The puzzle as
published"), and nothing published links the blob to it. No lead above targets the
blob with a password sweep of its own; leads 3 and 4 are the routes most likely to
produce a password hypothesis for it.

## 8. Re-run anything that was tested through the shipped oracle

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

## 9. The small blob is on the SalPhaseIon page, not the final page (the literal reading is closed)

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

Clarified in section 29 (2026-08-27): the even stream is not a separate message but the
plaintext's own even slots, and its four-letter restriction is explained by geometry -
B,C,D,E are exactly the Bifid square's top-left 2x2 corner (D=(1,1),B=(1,2),C=(2,1),
E=(2,2)), i.e. each even symbol is a 2-bit coordinate (570 bits total). Direct 2-bit to
byte, 5-bit/3-bit grouped root-4, and 29-bit gating reads are all negative (section 29).
The structural "why four letters" is now answered; section 29b (2026-08-27) further
shows the correct interleave is even-first, reconstructs the full 570-letter plaintext
(starting `BTCSEED`, not legible English), and feeds it plus every sub-object (odd, even,
object-256, the 29 dropped letters) as the oracle-answer X through `tools/oracle.py`: all
NO MATCH. So the even channel's direct contribution to the small-blob password is
exhausted/negative. What remains open is only whether the 570-bit coordinate channel is a
select/mask over the odd 256-symbol object it interleaves with (README gating), which the
ad-hoc XOR alignments do not resolve

What would confirm it: any encoding that turns the 285 symbols into a legible string,
a key that matches an address, or a mask that reduces the 256-symbol object to a match.
What would kill it: exhausting the reasonable encodings of a four-symbol alphabet at
length 285 with nothing; note the length factors as 3 x 5 x 19, and 57 five-bit groups
and 95 three-bit groups both divide it exactly.
Cost: hours of directed reasoning, not a sweep.
STATUS: the lead-8 open "is even_stream a select/mask over object_256 (README
gating)" direction is now closed. Section 183 (2026-09-06): even_stream 2-bit values
{B,C,D,E}->{0..3}/{1..4} driving object_256/odd_pre_reduction reads in the
DIRECT0/DIRECT1/CUM/CUM1 framework, and dropped_29 masking/gating the four channels,
104 unique x 2 gates -> NO MATCH. Even/odd direct contributions remain exhausted
(sections 14/29/175/183).

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

The community source (puzzlehunt/gsmgio-5btc-puzzle, issues #56, #106; see
`analysis/tested.md` section 20) transcribes the phase-1 wording this lead was waiting
for. That wording is the known SalPhaseIon preimage
(`GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9...`, recovered by OCR of the phase-1 page) and a
2023 author hint; both are in section 20's vocabulary, which remains negative against
the seven open slugs.

Section 28 (2026-08-27) additionally swept the Wayback-era phase-2 prose (Thevenin/Norton
riddle, "5binary code", Bitcoin-origin channel line, chess FEN, `parts 1..7` handoff) as
single/pair/triple preimage candidates: 15,555 tested, 0 hits, witness re-finding all
three known preimages. Section 28b adds the reported Phase-3.2 passphrase and its
component nouns (`jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple`,
The Thinker / Venus Project words): 9,560 more candidates, 0 hits; that report's key
hash is verified as sha256 of the passphrase, and its full path is the section-21
Cosmic Duality dead-end. So lead 9 has now consumed the phase-1, phase-2, and phase-3.2
transcribed wording. The Phase-2 riddle answer string (thevenin/norton + chess
next-move, which the page feeds `sha-256 -dgst` into Phase 3) is now derived and
exhausted too: its 7 parts resolve to the already-recovered password and every
individually-derived component and name has been run through the oracle and against the
seven slugs with 0 hits (section 34). So the one phrase the page explicitly names as a
"password" is no longer an outstanding candidate. The seven slugs' 2025-26 CDX snapshots are only the
clearly and is now effectively terminal: section 28 (phase-2 prose), 28b (phase-3.2
passphrase) and 28c (the full phase-3 seven-part password `causalitySafenetLunaHSM...`
plus its verified `1a57c572...` digest and the Bitcoin-genesis coinbase phrase) have all
been swept against the seven open slugs with 0 hits, and the phase-2 password
(`theflowerblossomsthroughwhatseemstobeaconcretesurface`) also does not hit. In total
the transcribed wording of phases 1, 2, 3, and 3.2 has now been exhausted as slug
preimages; the only remaining theoretical candidate is a not-yet-transcribed pixel-only
string, which this folder does not hold. Section 33 further covered the phase-1 wording
that is transcribed (the first phrase "the seed is planted when opposites attract" and
the seed text `GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9...`) through the oracle as X and
against the seven slugs, both negative. Re-score lead 9 as low-priority: bounded by the
sources now essentially fully enumerated.
8 (hash-slug preimages, 3/10 partial success) and lead 5 (tool-identity) have the
strongest partial progress; lead 1 remains #1 but only narrowed (all alphabet families
closed). Report the ranked nearness assessment to the user with the evidence.

## 10. The cosmic XOR branch does not reach a funded gate

The community's flagship "solution" is a Cosmic Duality AES decryption keyed by XOR of
seven token sha256 digests, producing the "Half / Better Half" keys. Section 21
reproduces the XOR_KEY (`a795de11...`) and confirms the mechanism exactly, but the
derived addresses (and the individual token keys) are not either funded escrow.
What this changes: that branch is confirmed terminal relative to the published prize;
the small-blob gate (`1GSMG1JC9`) and the Dualite gate (`17ucy...`) remain the only
funded targets, and no lead here finds a password that reaches them.

## Research note 1 (2026-08-27): the unsolved core, verified against the community cryptanalysis

Deep-research pass over the community's primary material (PR #93 FINDINGS.md by
halbgott29a; the Naddiseo curated fork's phase3.2.ipynb and SalPhaseIon.ipynb; the
2020-2026 official-hint timeline) confirms and sharpens this folder's lead-0 account.
Established facts:

1. `dbbib` is a structured key, `faed` an encrypted payload (Index of Coincidence 0.151
   vs ~0.118, the latter near-uniform - section 23's diagnosis, verified independently).
2. The cipher family is VIC / straddling checkerboard, and the template is PROVEN at
   phase 3.2.2: escapes `1,4`; alphabet derived from the phrase
   "fubcd oracle thingky mvps" -> working alphabet `fubcdora/lethingkymvpszjqwx.`;
   plaintext `INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE`.
   With the `a=0..i=8` mapping, `dbbib`'s two most frequent letters are `b,e` = digits
   `1,4` - the SAME escape digits as 3.2.2.
3. The decoded instruction words are transposition-key LENGTHS: `matrixsumlist`=13
   (faed = 15x38) and `lastwordsbeforearchichoice`+`thispassword`=38.
   NOTE (2026-08-27, image-corrected): the old dbbib=13x7 (91) is FALSIFIED - OCR of
   SalPhaselonCosmicDuality.png shows section 1 is 69 = 3x23 tokens (the 91-token
   community README value carried a 22-char middle run not present in the image), so
   dbbib does NOT match matrixsumlist=13.
4. The endgame reads `shabef our first hint is your last command` + `shabef ans too` as
   `sha256(first hint)` -> decode key for dbbib/faed -> ANSWER -> sha256(ANSWER) = AES key.
5. THE VERIFICATION PROBLEM (community, reproduced): a full VIC decode needs FIVE
   unknowns jointly - checkerboard alphabet, a..i->digit mapping, escapes, transposition
   key, and mod-9 over-encryption keystream. Each guessed key fixes only ONE; the only
   verifier is the closed end-to-end loop (decode -> sha256(answer) -> opens the funded
   gate), which requires all five correct simultaneously. A correct alphabet alone yields
   ciphertext-looking gibberish, so intermediate "legibility" scoring cannot recognise it.

### Correction this forces on this folder's own negatives

This folder's lead-0 checkerboard sweeps (tested.md sections 24, 25, 26, 27, 32) decode
the streams with the transposition and over-encryption layers held at their trivial
defaults and score for "real instruction words." Under fact 5, even the CORRECT alphabet
would not produce legible output in those tests. Those negatives are therefore
**uncertified as complete negatives of the final-gate decode**: they bound only the
direct-checkerboard subspace, not the full construction. They remain valid as negatives
of the specific {alphabet,mapping,escapes} combinations they tried, but the joint layers
were never co-swept here. The community's own joint attack (PR #93 joint_attack.py)
enumerated {alphabet x mapping x escapes x transposition x over-encryption} = 4,904
decode-forms over ~16 natural keyword alphabets, oracle-verified: 0 hits.

### What this means / what would move it

The alphabet is a 26! space with a binary oracle and no gradient; it cannot be searched.
The block is interpretive, not computational: the single missing input is the correct
keyed-alphabet source, which the puzzle's own hints suggest is "the first hint" (see
lead 6; the 2023-02-23 decoded hint lists `yellow blue primes matrix sumlist last words
before archichoice yinyang`; the 2026-07-12 hint "my close friends..." is an author hint
about the source). A remaining untried-but-conditional avenue is a joint decode of faed
only (fully: alphabet + a..i mapping + escapes 1,4 + the 13/38 transpositions + mod-9
over-encryption) with the subset of hint-derived alphabets NOT in the ~16 community set
(note: this folder's section 32 already oracle-swept the Bifid/lean/literal dbbib-faed
alphabets, which did NOT include transposition+over-encryption - see the correction
above - so a genuinely joint retry there is still open). Given fact 5 this is low-probability
but is the only sound computational path left, and the verifier is the funded oracle.
Date: 2026-08-27.

## Research note 2 (2026-08-27): late-2026 community pass - what is still genuinely missing

Deep pass over the 2026 material that post-dates the local 100-issue dump (issues #72,
#82, #88, #91, #104, #106). Confirmed anchors and the resulting gap analysis:

1. The funded gate is UNCHANGED and not opened: `1GSMG1JC9` via the small blob
   (salt `3ab585348552415d`). Re-certified: HASH160(target uncompressed pubkey) =
   `a9553269572a317e39f0f518cb87c1a0ee1dbae4` (issue #88), matches the local oracle's
   selftest constant exactly.
2. Community status: Cosmic Duality 1327-byte decrypt verifies (SHA256 `4f7a1e4e...`,
   #72/#82/#106), the "7 passwords" XOR chain and the Half/Better-Half 103x103 ->
   base-38 -> 68-byte split all reproduce, but land on UNFUNDED or spent addresses - not
   the funded gate. Issue #82's own audit declares Phase 3 "algorithmically terminal"
   for `1GSMG1JC9` (no reproducible F(artifacts)->k reaches the prize address).
3. Creator (issue #104) explicitly disavows a "step after Cosmic Duality"; calls the
   1327-byte plaintext path "nonsense"; reaffirms "the internet is no longer required"
   after SalPhaseIon and the recurring "it's in front of your eyes" line. This voids the
   non-public operands the community chased (cosmic_A.bin SHA256-prefix `cd3fea3d...`,
   the XOR-triangle row1-4, the ZION/BLOB1+z+BLOB2 79-byte artifact - whose SHA256 does
   NOT repro the `e2590f15...` anchor): they are either non-public or non-connecting and
   are NOT a funded-gate route.
4. Issue #83's two-part correction (Wi77erd, 2026-02-27): the z-delimited middle band
   decodes with `o=0` base-10 (verified correct), but the PRE-FIRST-`z` block
   (`dbbib`/`faed`, 9-symbol `{a..i}`, no `o`) "does not use the same trick (hint: there is
   no o=0)" and "without the o it turns to base 9". Re-scored PARTIAL in tested.md late-163:
   base-10 confirmed for the z-segment words; base-9 big-int->hex->ASCII reading of the
   765-token pre-`z` block now falsified; the base-9 DIGIT/alphabet (interpretive) reading
   of `dbbib`/`faed` = Lead 0, open.

Gap analysis - what is genuinely missing vs not:
MISSING (open): (a) the small-blob password X (salt `3ab585...`), the only funded gate,
~250+ oracle-verified candidates across us and community, 0 match; (b) the
interpreter-alphabet leap that fixes the SalPhaseIon/`faed` decode (the base-9 alphabet
read of the pre-`z` streams per issue #83; big-int forms closed in late-163, the
digit/interpretive form remains); (c) any complete independent
decode of the 570-symbol `faed` to a full instruction.
NOT missing (bounded/terminal): VIC/straddling-checkerboard machinery (verified against
3.2.2, extended to faed, ~70k oracle negatives, section 41); the Cosmic-Duality 7-password
chain (verified, #82 terminal audit); Half/Better-Half branch (section 40); non-public
community operands (voided per item 3).

The single most actionable untried computational avenue is issue #83's base-9 DIGIT/word
reading of the PRE-`z` block (big-int->hex->ASCII now closed in late-163), since it could
yield different instruction words and therefore different transposition keys and a different
AES password than everything tested to date. Date: 2026-08-27 (addendum corrected 2026-09-17).

### Research note 2 addendum (2026-08-27, CORRECTED 2026-09-17): base-9 lead re-scored PARTIAL

The base-9 re-reading of the SalPhaseIon z-SEGMENTS (item 4 / priority-1 of research note
2) is FALSIFIED (tested.md section 43 + late-163): the community's base-10 decode of the
two segments is verifiably correct (`lastwordsbeforearchichoice`, `thispassword`, lengths
26+12=38, matching faed=15x38), and all base-9 alternatives on those segments produce
garbage. BUT the base-9 claim is NOT dead: per issue #83 (Wi77erd), base-9 applies to the
PRE-FIRST-`z` block (`dbbib`+`faed`, 9-symbol `{a..i}`, no `o`), which is a DIFFERENT
object from the z-segments. The big-int->hex->ASCII reading of the ENTIRE 765-token pre-`z`
block is now also falsified (late-163: 303B, printable 0.38-0.41, both maps), but the base-9
DIGIT/alphabet (interpretive) reading of `dbbib`/`faed` is exactly Lead-0's crux and remains
the open interpreter-alphabet leap below.

So what remains genuinely missing is exactly what was missing before this pass:
1. The small-blob password X (salt `3ab585348552415d`, gate `1GSMG1JC9`) - the only
   funded target; ~250+ oracle-verified candidates (us + community), 0 match.
2. A correct decode of the two 9-symbol streams `dbbib`(91)/`faed`(570) to a full
   instruction - the crux, bounded but unsolved by ~75k joint VIC forms (section 41 +
   community 4.9k). The single missing input is the interpreter-alphabet leap (creator:
   "it's in front of your eyes, you're just not seeing it").
3. Any complete independent decode of `faed` to a legible instruction (issue #51's
   base-9-affine -> generic crypto-paragraph is unverified/apophenia, not accepted).

No new public security/puzzle lead from the 2026 issues changes these. Date: 2026-08-27,
local.

### Research note 3 (2026-08-27): full-page literal enumeration terminal

A complete enumeration of every literal token/composite on the decoded SalPhaseIon page
was queried through the certified oracle (tested.md section 44): 22 fresh page strings
(`shabef`, sha256-prefixed compositions, instruction concatenations, phrase uppercase/
punctuated/alt-word variants, `yourlastcommand`, `salphaseion`, `cosmicduality`) -> 22
NO MATCH, plus all previously-tested page literals. Combined, the entire decoded page
text is exhausted as password-candidate strings. So the "hunt a hidden instruction
string that IS X" avenue resolves honestly to a dead stop: there is no on-page literal
that opens the small blob. X must therefore be derived, not read off the page - the
remaining path is a correct decode of `dbbib`/`faed` (the interpreter-alphabet leap),
which compute-bound sweeps (~75k joint VIC forms + community 4.9k) have not cracked.
Note: the SalPhaseIon PNG could not be opened by this model's tooling; the page text
came from the community README's authoritative transcription. Date: 2026-08-27, local.

### Research note 4 (2026-08-27): crux re-pass confounded

A focused re-pass at the crux (decode dbbib/faed) tested the matricial readings not
explicitly enumerated before: exact matrix row/column sums of dbbib (69 = 3x23 after the
2026-08-27 image correction) and faed
(15x38) under 3 digit mappings read as ASCII/mod26/mod256/base9-hex, and the
dbbib-sums-keyed columnar transpositions of faed. All negative (tested.md section 45).
A keyed-alphabet variant (alphabet sorted by dbbib's matrix sums) was conceived but NOT
run: this session's from-memory checkerboard failed to reproduce the verified phase
3.2.2 oracle, so results through it would be untrustworthy; the validated sweeps
(sections 24/41) already cover the keyword-alphabet family. So the crux advances no
further on mechanics. The remaining interpretive avenues from the author's own hints
("yellow blue primes matrixsumlist... yinyang", "some characters need to be zeroed out",
"once you hit a yinyang you'll solve it the same day", "in front of your eyes") point
at a non-mechanical leap still not identified. Date: 2026-08-27, local.

### Research note 5 (2026-08-27): the sum-derived-alphabet family is now oracle-tested, negative

Closes the "conceived but NOT run" gap left in note 4 / tested.md section 45. The
digit-sum-derived alphabet family (alphabets built from dbbib/faed's own matrix
row/column sums rather than from a keyword) was the last genuinely-novel, untested
interpretation of the two streams. This session found the trusted pipeline (the
community-validated VIC checkerboard + digit-level columnar transposition, at
`~/..`/usr/tmp/opencode/joint_ext.py) and ran the full family through it, oracle-verified
against the funded small-blob gate: 12 sum-derived alphabets (stream x digit-mapping x
{row, col, row+col} sums -> mod26 -> pad28) crossed with 13/38-col columnar transforms,
3 mappings, 3 escape pairs, and 3 over-encryptions => 7776 candidates, ALL NEGATIVE
(tested.md section 46).

Also proved structurally (tested.md section 46) that phase 3.2.2 requires a DIGIT-LEVEL
columnar transposition before the checkerboard decode (no simple 2-escape checkerboard
maps its 149 digits -> 91/113 letters), which the trusted pipeline already implements
and which explains the earlier from-memory NGO?ST?ABM? artifact.

Updated crux picture: the two-stream keyed alphabet is NOT produced by the streams' own
digit sums, nor by any keyword alphabet (~75k community+joint forms), nor by page
literals (sections 42/44). The interpreter-alphabet must come from visible/on-image
content ("in front of your eyes"; author's hidden 2023 message "yellow blue primes
matrixsumlist lastwordsbeforearchichoice yinyang ... some characters need to be zeroed
out"). Since this model cannot read the SalPhaseIon PNG, that leap is blocked here; the
only sound next step requires human/vision access to that image. Date: 2026-08-27, local.

### Research note 6 (2026-08-27): image OCR identifies the Cosmic Duality blob as the known swept "dualite" blob -- no new lead

The user granted access to `~/briefcase/SalPhaselonCosmicDuality.png`. [PROVENANCE 2026-09-26: this file is a COMMUNITY RENDER, not an author artifact - sha256 a3810ba24250c5a0, unattributed, present in no capture of the SalPhaseIon page and sourced from the misnamed `1-big-prizes/gsmg-community-hints-repo/` which is actually Naddiseo's community repo. Findings below describe THIS FILE only and carry no weight about authorial intent. See `analysis/tested.md` R-STRUCT8-13-5-2026-09-26.] Image has a
SalPhaseIon section (the documented streams) and a Cosmic Duality section (one OpenSSL
blob). OCR of the blob's header line gives salt `2d3f6fe06dc950e6`, which EXACTLY
matches the community's already-swept "dualite" blob (part of the 4-blob sweep set:
small `3ab585348552415d`, dualite `2d3f6fe0...`, p32 `b45a5e3d...`, urlblob
`74c974e3...`). So the image blob is a known, exhausted gate (community ~2.5B verified
tests, zero hits) and is NOT the oracle small final blob. OCR cannot recover byte-exact
multi-line base64 (breaks AES-CBC+PKCS7), so direct decryption is unreliable here.
The crux -- password X of the small final blob / the two-stream keyed alphabet -- is
unchanged and still requires interpretation not recoverable by OCR or mechanics.
Nothing new sent to the funded oracle. Date: 2026-08-27, local.

### Research note 7 (2026-08-27): issue #94 `flag{8KJ}` assessed -- dualite-gate, padding-evidence-only, not a small-blob route

Verified issue #94's full source (moetneos-maker, NONE association, 0 comments, 2026-06-13).
It is a "cosmic_decrypt.py" whose COSMIC_DATA is the DUALITE blob (salt
`2d3f6fe06dc950e6`) - the known swept gate, NOT the oracle's small final blob
(`3ab585348552415d`). It decrypts with the known 7-token XOR chain
(matrixsumlist/enter/lastwordsbeforearchichoice/thispassword/matrixsumlist/
yourlastcommand/secondanswer) -> 1327 bytes -> SHA256 `4f7a1e4e...c081` (the verified
legacy hash, already reproduced and audited terminal in issue #82). The `flag{8KJ}`
is then extracted by a known-plaintext CRC hack: it brute-forces 3 unknown middle
bytes of the XOR key while ASSUMING the plaintext is exactly "flag{?}{?}{?}" (prefix
`salt "flag{"` + suffix `}`) and hard-codes the XOR-key prefix
`9f 94 3b c7 a9 _ _ _ b0`. This only self-confirms the first 5 + last bytes of the
dualite XOR key against an assumed 9-byte plaintext - the same padding-evidence-only
status that led to #32 being falsified. It yields NO small-blob password X and sends
nothing to the funded oracle. Verdict: log-and-close, no further treatment; it does
not change the crux. Date: 2026-08-27, local.

### Research note 8 (2026-08-27): full openssl-dimension closure reconfirmed (issue #106) + label/KDF clarifications; crux unchanged

User steered back to the SalPhaseIon/Cosmic Duality structure; consolidated three
confirmations and acted on the one fresh data point.

1. **Label fix (applied):** the SalPhaseIon stream is `dbbib` (d-b-b-i-b), not
   `dbbi`; corrected the label across `finalpage-digit-streams.json`
   (`dbbi_91`->`dbbib`, etc.), leads.md, tested.md, README.md without corrupting the
   raw stream values. Content was never wrong; only the name. (See research note 9 for
   the follow-up length correction: 69, not 91, verified against the image.)
2. **Blob identity (reconfirmed):** Cosmic Duality region = dualite gate
   `U2FsdGVkX18tP2/gbclQ5t...` (salt `2d3f6fe06dc950e6`), DISTINCT from the funded final
   blob oracle.py checks (`U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4K...`, salt
   `3ab585348552415d`, gate `1GSMG1JC9`). Both share the `U2FsdGVkX18` = `Salted__`
   base64 header. Verified: oracle.py's BLOB_B64 is the FULL 128-char blob (two 64-char
   lines), salt `3ab585...`, 96 bytes; matches the funded gate. The small blob IS
   embedded on the SalPhaseIon page flanked by the `matrixsumlist`/`enter` binary runs
   (leads.md section 7, reconfirmed verbatim).
3. **KDF concern from issue #106 Part A (allayed):** the public open-crypto-puzzles
   oracle was MD5-only and thus structurally void. This folder's oracle.py `attempt()`
   already tries BOTH sha256 and md5 (`tools/oracle.py:172`) and the phase-2/Cosmic
   selftests certify both digests, so this folder's prior negative sweeps are valid under
   both KDFs; nothing needs re-running.
4. **Issue #106 Part B color-frame "true sum lists" tested directly:** rows
   `610876654997879` / cols `8108108736759668` (and composites, `theseedisplanted`,
   permutations of the four decoded directives `matrixsumlist`/`lastwordsbeforearchichoice`/
   `thispassword`/`enter`) - all NO MATCH via the funded oracle.
5. **Community closure reconfirmed:** issue #106's own 2.5B-test sweep
   ({MD5,SHA1,SHA256,PBKDF2} x {raw,hex,string} x {CBC,CFB,OFB,CTR} x 4 blobs x ~56k
   candidates, incl. matrix-sum lists + selection masks) = zero genuine hits, padding at
   chance rate. Issue #106 independently identifies the `dbbib`/`faed`(570) two-stream
   decode as "the last unexplained step" - matching this folder's crux exactly.

Net: every mechanical/openssl route across all blobs is confirmed closed by independent
sources; the small-blob password X still requires the interpreter-alphabet leap from the
visible SalPhaseIon content ("in front of your eyes") that neither this folder nor the
community has mechanized. Date: 2026-08-27, local.

### Research note 9 (2026-08-27): SECTION 1 dbbib LENGTH CORRECTION -- image says 69, not 91

User flagged that the section-1 stream I showed (91 tokens, from the community README) is
longer than the image. OCR of `~/briefcase/SalPhaselonCosmicDuality.png` (section 1, [PROVENANCE 2026-09-26: community render, provenance unattributed - see `analysis/tested.md` R-STRUCT8-13-5-2026-09-26. This OCR is of a solver-made file, so it is evidence about that file, NOT about the author's page. The 69-token reading it produced was already reversed by note 32; do not re-derive from this image.]
SalPhaseIon region, a-i whitelist, multiple PSM passes) reads section 1 as TWO lines:
  line1 `dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfba` (45)
  line2 `ggecbedcibfbffgigbeeeabe`                          (24)
= 69 tokens. 69 = 3 x 23.

The 91-token community-README value = 45 + 22-char middle run `bfdhbeffcdbbfcccgb...` +
24 tail. OCR across 3 independent crops/PSMs consistently reads the middle run as ABSENT
in the image (line 2 starts directly at `ggecbedci...`). User confirmed ground truth:
image = 69; prior record over-long. 

Applied changes:
- `data/finalpage-digit-streams.json`: `dbbib_91` -> `dbbib` (69 chars), `dbbib_len`=69,
  `dbbib_counts` recomputed {a:3,b:19,c:4,d:2,e:15,f:5,g:9,h:7,i:5}; provenance note updated
  to record the image-verified correction.
- README.md + tested.md + leads.md: references to `dbbib`(91=13x7) fixed to 69 = 3x23.

### Research note 10 (2026-08-27): issue #56 "1Hxxxxxx/1Bxxxxxx" = redacted donation-bait, not our gates

Flagged by user: issue #56's Cosmic Duality decode text contains "BTC: 1Hxxxxxx (valid
address, balance 0)" and "BTC: 1Bxxxxxx (valid address, balance 0)". Assessed as a dead end:

- Both literals contain `xxxxxx` INSIDE the issue text - the poster deliberately redacted
  the address halves and withholds the full values behind a donation ("We will give the
  above results to those who donated."). Not actionable.
- The quoted addresses are stated to be balance-0 / unfunded, so they are NOT our two
  funded gates (small-blob `1GSMG1JC9...` or Dualite `17ucy1K9...`).
- Our own primary-source reproduction (tested.md section 12) already derived the real
  HALF/BETTER HALF addresses from the Cosmic Duality plaintext (Half
  `1JG648yaB7Wp2dpUfcZoRSD4q35oq47vCu`/`15E3pcDDXSKhvi3CLVhRTHEgd8dbVKvSZg`, Better half
  `145ZQ9siLrsXBKf465wjdyQYAP5dRwhRhQ`/`1FhbJnrdq1FmeiXrpTqnpQ8jvYV7naze96`) and confirmed
  all four empty on 2026-08-19. None lead with `1H`/`1B`.

Net: `1Hxxxxxx`/`1Bxxxxxx` cannot map to any funded target we hold; treat as resolved
(no re-chase). Date: 2026-08-27, local.

### Research note 9 (2026-08-27): SECTION 1 dbbib LENGTH CORRECTION -- image says 69, not 91

User flagged that the section-1 stream I showed (91 tokens, from the community README) is
longer than the image. OCR of `~/briefcase/SalPhaselonCosmicDuality.png` (section 1, [PROVENANCE 2026-09-26: community render, provenance unattributed - see `analysis/tested.md` R-STRUCT8-13-5-2026-09-26. This OCR is of a solver-made file, so it is evidence about that file, NOT about the author's page. The 69-token reading it produced was already reversed by note 32; do not re-derive from this image.]
SalPhaseIon region, a-i whitelist, multiple PSM passes) reads section 1 as TWO lines:
FALSIFIED by the image [PROVENANCE 2026-09-26: THIS INFERENCE IS UNSOUND AND MUST NOT BE RELIED ON. The image is a community render, not the author's page, so it cannot falsify the 91-token reading. It is also simply wrong about the data: the middle run is present in both machine-readable primaries, per note 32 and row 16X, and 91 = 7x13 is the reinstated ground truth. See `analysis/tested.md` R-STRUCT8-13-5-2026-09-26. - dbbib is 69 = 3x23, which does not match any transposition
key-length token. all prior matrix-sum / keyed-alphabet sweeps that used the 91/13x7
reading baked in the WRONG dbbib stream (with the spurious 22-char middle), so their
negatives against the funded small blob are inconclusive for dbbib and would need
re-running on the corrected 69-token dbbib. faed (570=15x38) is unaffected. This is a
fresh, image-grounded input to the crux. Date: 2026-08-27, local.

### Research note 11 (2026-08-27): corrected 69-token dbbib re-swept -- still negative

Per note 9's correction, re-ran the full VIC/keyed-alphabet/matrix/prime family on the
image-verified 69 = 3 x 23 dbbib (widths 3 and 23; the old 13-column reading was for the
now-deleted 91-token string). Route: same trusted pipeline (cb_decode+col_decrypt) ->
funded oracle 1GSMG1JC9:
  - keyword-padded + sums alphabets, widths 3/23: 56,196 candidates, NO MATCH
  - matrix-sum alphabets under prime/yinyang masks, widths 3/23: 80,178, NO MATCH
  - prime-position extraction (hex-ASCII / base-9): 101, NO MATCH
Net: the corrected true stream gives no mechanical keyed-alphabet read either. The
prior 91-token negatives were invalid for dbbib; these 69-token negatives now validly
close the mechanical alphabet space for dbbib. faed (570) unaffected. X still needs the
author's visual/interpretive leap. Tests recorded in tested.md section 49.
Date: 2026-08-27, local.

### Research note 12 (2026-08-27): second corrected-dbbib wave -- sum-alphas, Bifid@3/23, dbbib-key x faed-payload -- all negative

Re-investigated the corrected 69 = 3 x 23 dbbib after note 11. Fresh angles, all oracle-
verified negative:
- recomputed matrix-sum alphabets straight from the corrected stream (widths 3/23; prior
  SUM_ALPHAS were from the corrupted 91) -> 15,928, NO MATCH
- Bifid-decoded dbbib at its real divisors 3/23/69 (section 14 had only tried 91/13/7/1
  on the old 91) -> non-legible square-alphabet text, no instruction, NO answer
- dbbib-key x (faed/object_256/even/full-plaintext)-payload VIC with dbbib-derived
  alphabets, escape {1,4} (#93) -> 540, NO MATCH
Full reproduce of the faed->BTCSEED Bifid path reconfirmed (gives the 570 plaintext /
object_256 over 23 letters / even B,C,D,E corner). The 23 in both dbbib-width and the
object alphabet is noted but yields no mechanical combination. Crux unchanged: X = the
author's single visual/interpretive layer. tested.md section 50. Date: 2026-08-27, local.

### Research note 13 (2026-08-27): ~/GSMG5_CDuality repo debunked (donation-bait, padding false positive)

Third-party repo at `~/GSMG5_CDuality` (cloned 2026-08-27) claims reproducible SalPhaseIon/
Cosmic Duality solution: p1 matrixsumlist, p2 enter, p3 lastwordsbeforearchichoice,
p4 thispassword, p5 matrixsumlist, p6 yourlastcommand, p7 secondanswer; XOR-of-SHA256 of
those 7 -> 32-byte hex key -> OpenSSL AES-256-CBC (EVP_BytesToKey, MD5) on the Cosmic
Duality blob; output hash 4f7a1e4e... . Independently reproduced: key and padding and
hash all check out against OUR authoritative Cosmic Duality blob - but the decrypted
output is 1327 bytes of meaningless binary (~39% printable, 0 base58/addrs, 0 alpha
runs>=4). It is a padding-only false positive engineered by choice of p7; the author's
candidate set is pre-picked so exactly one XOR lands on valid PKCS7. README top = donation
solicitation. Same class as note 10/issue #56. Irrelevant to our funded small-blob gate
(targets only Cosmic Duality, salt 2d3f6fe0, gate 17ucy1K9; never 1GSMG1JC9 salt 3ab58534).
Recorded tested.md section 51. No re-chase. Date: 2026-08-27, local.

### Research note 14 (2026-08-27): note-1's named "joint faed retry" gap now closed -- negative

Executed the one sound computational path research note 1 (lines 372-378) left open: a
GENUINELY joint decode of faed = hint-derived alphabet (the faed/dbbi sum-alphabet family
plus non-community kbws) x a..i map x escapes x 15/38 columnar transposition x mod-9
over-encryption. testeded.md section 52. 10,080 joint settings -> only 24 clean checkerboard
outputs, all non-legible, all oracle-negative vs 1GSMG1JC9.

This removes the last named mechanical gap. Combined with notes 9/11/12/13, EVERY public
computational avenue is now individually closed and oracle-certified negative. The crux
converges to exactly one unprovided input: the interpreter-alphabet leap visible only in
the SalPhaseIon PNG / author's color/yinyang message ("in front of your eyes"). Compute is
exhausted; vision or a new author-hint is required. Also: 23-column keyed transposition of
the corrected 69-token dbbib (A0/A1/canon col-sums as key, row/col reads + Bifid variants)
-> 86 candidates, NO match (coltrans_69.py). Date: 2026-08-27, local.

### Research note 15 (2026-08-27): CMYK/channel separation of SalPhaselonCosmicDuality.png -- anaglyph, no hidden channel extractable

[PROVENANCE 2026-09-26: the file analysed here is a COMMUNITY RENDER (sha256 a3810ba24250c5a0, unattributed, referenced by no capture of the SalPhaseIon page; it entered this repo via the misnamed `1-big-prizes/gsmg-community-hints-repo/`, which is Naddiseo's community repository, not the author's). Every pixel-level finding below - including the anaglyph offset and the "yellow blue" match - is a property of that unattributed render and is NOT evidence about the author's intent. It also retires the broader "hidden layer in the PNG" idea: there is no author image in which anything could be hidden. See `analysis/tested.md` R-STRUCT8-13-5-2026-09-26.]

User: "check it with CMYK". Converted 668x619 RGB PNG to C/M/Y/K and analyzed each plane.

Findings:
- K channel is ENTIRELY zero: the render is C/M/Y only (no true black; "black" text = ink in all of C,M,Y).
- The page text is a YELLOW/BLUE ANAGLYPH: each glyph has a yellow copy and a blue copy offset
  horizontally by ~1px (cross-correlation peak at (0,-1)), with some glyph rows at -3..-5px.
  Matches the "yellow blue" hint; the offset is the "yinyang" juxtaposition (two-color depth).
- black-only channel OCRs CLEAN to the headers "SalPhaseIon / Cosmic Duality" (prior known).
- No LSB steganography in any C/M/Y/R/G/B plane. The PNG is a heavily re-encoded 50KB raster
  (593 unique colors, anti-aliased), so pixel-level stego would not survive re-encoding; none present.
- Yellow-only vs blue-only regions are the SAME text (>=~85% of pixels have a same-stroke counter-
  part in the other color at 5x5): NOT two different messages.

Net: the "yellow blue" is a rendering/interpretive cue (2-color anaglyph depth), at ~1px offset that
no OCR/symbol analysis can resolve into per-glyph codes. Same conclusion as notes 9/14: the hidden
layer is VISUAL (needs human eyes on the color bands/depth), not mechanically extractable by this
model. No new candidate to oracle-test. Date: 2026-08-27, local.

### Research note 16 (2026-08-27): RGB channel separation -- two-hue anaglyph, same text in all channels, no hidden message

Follow-on to note 15 at the user's "check on RGB" request. Separated R/G/B planes and OCR'd
each channel mask + pure-color masks:

- The PNG contains EXACTLY two hues: pure R (yellow/orange, 2375 px) and pure B (blue, 2197 px),
  ZERO pure-green pixels. Green appears only where R and B mix. Consistent with a dual-color
  (yellow/blue anaglyph) render of a single message.
- All three channel masks OCR the SAME underlying text (SalPhaseIon header, the 69-token dbbib
  stream, the abba binary runs, faed) with per-channel anaglyph offset distortion - i.e. each
  channel is the SAME content viewed at a different ~1px depth offset, NOT a distinct message.
- Full-page grayscale OCR (4x upscale) additionally reads the Cosmic Duality base64 blob region
  and the sha256 slug URL at top; it finds NO hidden margin/footer/watermark/instruction line.
  The page image contains exactly the content already held and verified from the raw HTML.

Net: RGB (like CMYK) yields no second message and no mechanically extractable channel. The
"yellow blue" + "yinyang" hints point at the VISUAL depth/color juxtaposition, requiring human
eyes; no new candidate to oracle-test. Streams re-consistent with ground truth (dbbib 69,
faed 570, blob U2FsdGVkX18tP2/gbcl...) across independent OCR passes. Date: 2026-08-27, local.

### Research note 17 (2026-08-27): exact-anchor color classification (#ffffff / #000000) -- black text on white with colored glow, no hidden color channel

User anchored the model with "White = #ffffff" and "Black = #000000". Reclassified the
668x619 PNG on EXACT per-channel tri-state (0 / 255 / mixed):

- Exact #ffffff: 337,884 px (background).
- Exact #000000: 10,364 px (core text), distributed across ALL stream rows (50-624) - i.e.
  the streams/headers are genuinely BLACK, not colored.
- NO exact primary pixels (#f00/#0f0/#00f/#0ff/#ff0/#f0f): zero. Every colored pixel is a
  MIXED-channel (anti-aliased) value, present only as a fringe/glow around the black glyphs
  (~luminous gold/cyan edges). Colors exist but only as edge gradients of the single black
  text layer.
- Consistent with notes 15/16: the image is a black-on-white render with a yellow/blue
  (and red/cyan/green) anti-aliasing "glow" - the "yellow blue" hint is the glow/depth
  nudge ("yinyang"), NOT a steganographic second channel.

RGB/CMYK/exact-anchor + additive + subtractive + pure-color-mask + LSB are now ALL checked:
no color plane carries a second message; the content is black #000000 text on #ffffff with a
colored glow. No new candidate to oracle-test. The visual leap (color-band interpretation)
still requires human eyes. Date: 2026-08-27, local.

### Research note 18 (2026-08-27): "yinyang is black and white" -- the yinyang = the even/odd two-stream split, not a color channel

> **SUPERSEDED IN PART by the creator's own definition - read this first.** The central claim below, "That even/odd split IS the yin/yang", is WRONG as a statement about the puzzle and must not be used as the working model. Primary source (`Jrk_Bgrt_Groupchat_History.txt` :1616, 2025-04-28T13:01:36): a solver asked "is yinyang found after decoding an AES ciphertext?" and the creator answered, verbatim, **"It's the next phase, but I await the day someone finally gets there."** So by the author's own account the yinyang is (a) a distinct PHASE lying AFTER the AES ciphertext, and (b) unreached by anyone as of 2025-04-28. The even/odd Bifid split is a structure *inside the current phase* that solvers had already reconstructed - it cannot be the next phase. The "black/white, not a colour channel" sub-claim below survives and is still useful; the identification does not. The correct ordering (`get material -> open AES -> interpret yinyang`) was already actioned and certified negative at `R-YINYANG-AFTEROPEN` + `-RERUN` (2026-09-24), sourced from the same message via silver_ant's export #39237. Kept below for its negative results, which remain valid, and demoted from "this IS the yinyang" to "this is a current-phase structure the community nicknamed yinyang". See `R-YINYANG-DEF-2026-09-26`.
>
> **RESOLVED POSITIVE - `R-YINYANG-MARKER-2026-09-26`. Do not run a yinyang battery; the artifact has been found and it is a one-off.** The author's actual yin-yang is a polarity bracket he wrote himself, on the PHASE 2/3 page, immediately around the chess FEN: the same token `aBa` under a predicate and its negation, `/(aBa, connected enf)` ... `/(aBa, connected not enf)`. Enumerating every `/(token, polarity)` marker across 155 author-source files gives D=4 pairs, and `aBa` is the ONLY token carrying both polarities; `aa` and `aaa` are single-polarity terminators for the Phase-3 components, not brackets. So the bracket occurs exactly ONCE in the whole corpus, it is attested in the 2020 Wayback capture (bracket region byte-identical, `83241c25147f`, across all 4 copies), and it is already CONSUMED: the polarity axis is the FEN side-to-move (`w`/`6R1` published, `b`/`2R5` in the working password = after `Rg6-c6+`), byte-verified in `R-CHAIN23-2026-09-26`. There is no second bracket to carry it to, so "apply the yinyang elsewhere" has no referent - this is a positive identification that CLOSES the thread, not a deferral. Separately, taijitu/rotational-antisymmetry is negative at chance level on all four DECRYPTED plaintexts (0.005-0.032 vs 0.5 for a real taijitu), including the tempting 36x36 framing of the 1,296 B cosmic payload, which has 249/256 distinct bytes and is a further cipher layer, not a 2-colour image. Do NOT promote `enf`/`not enf` into a general inversion rule - that is the `R-DOORGlyph` trap and is explicitly not claimed. Note also that `R-YINYANG-DEF`'s "no battery, the yinyang is downstream of the AES boundary" was a VOID gate: we are past four AES boundaries, so the thread was parked, not blocked. Lead 0's missing 28-char alphabet remains open and is unaffected by any of this.

User insight: the yinyang (classical) is black and white. Applied to the image (exact#ffffff
+ exact#000000 established in note 17 as the ONLY two solid colors; all else = anti-alias
glow), the "once you hit a yinyang you'll solve it the same day" hint is not about hidden
colored content - it names the BLACK/WHITE (binary, two-tone) structure of the data itself.

The concrete yinyang in the puzzle is already reconstructed and witnessed: the Bifid output
of faed (570) splits into its EVEN slots (285 letters, only {B,C,D,E} = the 2x2 square corner,
2-bit coordinates -> a black/white-ish binary channel) and ODD slots (285 letters, I/O removed
-> the 256-symbol object over 23 letters). That even/odd split IS the yin/yang. Both halves and
every reading (2-bit bytes, 3/5-bit base-4, gating with dropped I/O bits, direct-as-password)
are oracle-negative (tested.md sections 17/29/29b/30/32).

No yinyang-dot artifact exists in the image: all 3,214 tiny black components are the regular
individual stream glyphs, none are isolated coordinate dots. The page is pure #000000 text on
#ffffff (notes 15-17).

Net: the black/white yinyang confirms the two-stream split as the intended structure but does
not supply a new mechanical reading; all splits and readings remain oracle-negative. The 23 in
both dbbib-width (3x23) and the object alphabet (23 letters) is still the one recurring,
unexploited numeric bridge. Date: 2026-08-27, local.

2026-09-26 addendum (ledger consolidation): the "unexploited" claim above is STALE and is
superseded; it is retained above only as the 2026-08-27 state of belief. The 23-bridge was
closed in its joint form by `analysis/tested.md` section 185 (2026-09-07), whose own opening
line reads "Closes the two recurring 'unexploited numeric bridge' leads in their JOINT forms":
dbbib 3x23 row/column sums used as a KEY over the 23-letter object alphabet, and the even
B/C/D/E stream as a SHIFT over object_256, were the only untried combinations, and both are
oracle-negative on both funded gates (15 small / 14 dualite candidates). Each 23 had already
been closed individually beforehand (sections 45/49/50/52 for the 3x23 sums, mod-9 and columnar
forms; 184 for object_256 grid routes; 183 for even-stream 2-bit drives). This note's own
softer reading -- research note 12 at line 707, "yields no mechanical combination" -- was
already the accurate one. Do NOT re-open the 23-bridge from this note.
Second caveat, from the 91-vs-69 stream correction (note 32 below, 2026-09-07): the 3x23
geometry underpinning half of these tests rests on the 69-token stream, which is a stale
OCR-derived variant, not ground truth. The true dbbib is 91 = 7x13, for which 23 is not an
exact divisor. See `analysis/tested.md` R-LEDGER-GAP-2026-09-26.

### Research note 19 (2026-08-27): corrected color-model labeling -- red/blue anaglyph, green is absent, not a primary palette

User correction: BLACK and WHITE are TONES, not color primaries. Re-labeled the image on true
additive primaries:

- Saturated/"colored" ink (mx-mn>60, lum<250): pure Red 2,524 | pure Blue 2,624 | Yellow(R+G)
  3,345 | Cyan(G+B) 3,485 | Magenta(R+B) 747 | pure GREEN only 64 (essentially ABSENT).
- So the image's real color system is RED and BLUE (the two RGB primaries present). The
  "yellow"(=R with a trace of G) and "cyan"(=B with a trace of G) are just R and B; green
  (~64 px) is negligible. => the page is a RED/BLUE anaglyph (stereo) of #000000 text on
  #ffffff, NOT a primary-color palette and NOT a color-class stego channel.

Separation into R-dominant vs B-dominant anaglyph eyes, OCR'd at 6x: BOTH eyes carry the SAME
text (the dbbib 69 / abba / faed 570 streams), each with different per-letter offset corruption
- the stereo-depth signature, not two messages. Consistent with notes 15-17: the black/white
(yin/yang) two-stream structure + red/blue stereo depth are the intended visual layers; the
colored content is depth/glow, not a second channel. "yellow blue primes" = the R/B depth
anaglyph + prime/depth reading that still needs human stereo-viewing/vision.

Net: no new mechanical channel from color. The page is black-on-white text rendered with a
red-blue stereo/glow; no hidden message per color plane. Date: 2026-08-27, local.

## Note 20 - CMYK/pigment masking definitively closed
- User insight: R=100% G=100% B=100% = black => image is **composite black** (C+M+Y overlap on a print). Confirmed: extracting the **C, M, Y CMYK separations** (PIL `convert('CMYK')`, ink >50) yields three masks that **each OCR to the full identical page text** (slug, SalPhaselon, the 69-token dbbib, abba binary runs, faed, Cosmic Duality + blob). No hidden message is split across separations.
- **Cleanest OCR ever:** C-channel separation (`~/usr/tmp/opencode/CMYK_C.png` -> `c_channel_ocr.txt`) independently recovers the **exact 69-char dbbib** `dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbaggecbedcibfbffgigbeeeabe` - byte-for-byte match with our stored value. Third independent confirmation (raw HTML + community + now image-OCR) of the corrected 69-token stream.
- Colored-fringe anatomy: exclusive ink = **C_only 6,133 px** and **Y_only 6,015 px**; **M_only = 0** (magenta absent). So the "color glow" = cyan+yellow fringes (their RGB collapse = the red/blue anaglyph; green ≈ 0 consistent).
- Fringe-direction test (cyan vs yellow per-glyph left/right): C mean col 290.9 vs Y 283.5 (cyan ~7px right); per-row split 98 cyan-left / 173 cyan-right = **1.76:1, non-binary, noisy** => **not a clean per-glyph yin/yang mask**; it's anti-alias dither, not a depth code.
- **Conclusion (closed, per user): the page is one black (composite-CMY) text; color is only anti-alias fringe. No hidden channel, no second message, no yinyang depth code in the pigment planes.** All C/M/Y separation content equals the streams we already hold and already tested negative via the oracle.

## Note 21 - rendered-image faed omits 183 chars vs stored (HTML-source) faed
- User's manual transcription of the SalPhaseIon image better matches OCR of the rendered image than the stored faed: the rendered faed starts `eedfcbdab...` (NOT stored `faedggeedfcbdab...`), and omits 183 chars that the HTML-source faed (570) contains.
- Aligning rendered(387) vs stored faed: 11 omitted regions = `faedgg | gcdaih | hahbahigceifgbf | faafcidahgdeefghhcggaeg | ... | hieeeieeecifdgdahdiggf | gagbeiichiedifbehgbcca`. Omitted len 183, rendered len 387; omitted starts with the deleted `faed`/`faedgg` prefix.
- Direct oracle of rendered(387), omitted(183), reversed, atbash variants: all NO MATCH (§62).
- Echoes the author's hint "some characters need to be zeroed out." INTERPRETATION OPEN: (a) image genuinely renders only a subset (the omitted 183 = colored/hidden = small-blob source, "red=small blob"); or (b) transcription+OCR merely dropped chunks (no signal). Only the user's eyes can distinguish faint/colored/absent glyphs.
- verification date: 2026-08-28.

## Note 22 (2026-08-31): phase-1 matrix colored-square counts pinned  -  BLUE=15, YELLOW=9
- Direct pixel analysis of `~/briefcase/gsmg-community/puzzle.png` grid region (1048x1048, 14x14 matrix), center-sampled per cell and cross-validated against the documented 14x14 bit matrix (README): every BLUE cell sits on a bit-1 square and every YELLOW cell on a bit-0 square (assertions passed). Counts: **BLUE=15, YELLOW=9**. Red pixels exist only on row-14 (the union-jack bottom strip, 74-85 px/cell in row 14, no red cell at any interior center)  -  the red is a flag/border element, NOT a hidden second-channel cipher. So "Roses are White but often Red" = the union-jack strip, not a code in the squares.
- This resolves the hint "Yellow has a number and so does Blue. Go back to the first puzzle piece": the two numbers are **9 (yellow) and 15 (blue)**.
- Strong structural echo: **faed = 570 = 15 x 38**, so **Blue=15 matches faed's column count** (the canonical 15x38 / 38x15 layout, cf. research note 1 fact 3). Yellow=9 has no clean dbbib(69=3x23) fit.
- Tested and closed this session (all oracle NO MATCH / no legible decode):
  * all 45 distinct escape-digit pairs x 2 stream->digit mappings (POS a=0..i=8, CANON D=0..K=9) on dbbib under the certified §3.2.2 alphabet -> reproduce escapes=(1,4) frequency conclusion, all output ciphertext-looking (no word structure); the pair (1,4)+CANON gives `FLUTHCCNOEXNNUVDOODODNLOD.DHSKOODCNFCUTTBOUONDDRN` (correct alphabet+escapes, wrong mapping/layer -> §76 negative reconfirmed).
  * numeric/name oracle candidates from {9,15}: 159,915,0915,1509,15and9,9and15,blue15yellow9,yellow9blue15,blueyellow,yellowblue,159matrix,B15Y0,Y0B15,x2sh4y0qb15 -> all NO MATCH.
  * columnar-transposition reads of dbbib/faed with matrix-derived widths {9,15,38,23,19,13,8}: only symbol gibberish (symbol stream needs digit/checkerboard first), no text.
- OPEN: exact cryptographic role of 9 and 15 beyond confirming faed's 15 dimension. Candidates: (a) 9 = a1z26 "i" and 15 = "o" (and o=0 in base-9/10)  -  ties to the a-i/o alphabet; (b) two transposition-mask lengths; (c) the "sumlist"/primes overlay. The interpreter alphabet (26! space, binary oracle only) remains the crux.
- STATUS §182 (2026-09-06): the coordinate/interpreter family from this geometry is now CLOSED. The 9 yellow cells == exactly the 9 letters {a..i}; all coordinate-VALUE digit maps (row%10, col%10, (r+c)%10, (r-c)%10, |r-c|, r*c%10, row%9, col%9, row+1) over yellow(9) / first-9 blue / key 0x41D464 one-positions={2,5,6,10,12,14,15,16,22}, under BOTH (r,c) and (c,r) axis conventions, fed as a..i->digit interpreters over {dbbib, faed, dbbib+faed, faed+dbbib} x {fwd, rev} + the 9-digit map-passphrases: 260 unique x 2 gates -> NO MATCH. Only CANON/POS/1-based maps and the now-closed coordinate maps have been applied; any future interpreter must come from a NEW source (e.g. the grid's own D-column/N-row geometry as a 10x~32 addressing rule).

## Research note 23 (2026-08-31): the endgame is a LAYERED 16-encryption x 7-password construction, not a single checkerboard decode -- reframing the crux

Author's own decoded phase-3.1 wording (community README lines 315-320), adjacent to where the certified single-checkerboard example (3.2.2) was found:

  "REINSERTING THE PRIME BASICS AFTER WHICH YOU WILL BE REQUIRED TO SELECT FROM OVER
   TWENTY-THREE CIPHERS SIXTEEN ENCRYPTIONS AND OR SEVEN INTERTWINED PASSWORDS TO FIND
   THE ACTUAL PRIVATE KEYNOTE THAT ALSO BRUTE FORCING MIGHT BE REQUIRED ... SELF GOOD
   LUCK NEVERTHELESS ... CIAO BELLA O"

Key numerics: 23 ciphers / 16 encryptions / 7 intertwined passwords / PRIME basics / find the PRIVATE KEYNOTE (the private key). The same triple (23/16/7) recurs as "23 individuals, 16 female, 7 male" in the source prose the final page is adapted from (already swept as a 16+7 partition of the 23-letter Bifid object alphabet in tested.md section 2 -- negative, but that is a DIFFERENT reading than 16 encryptions x 7 passwords).

This reframes the crux: dbbib/faed are NOT necessarily a single VIC/straddling-checkerboard plaintext (all such single-mechanism sweeps closed negative in notes 1/9/11/12/14, 52, 68-79). They are more likely the PRODUCT OF / intermediate in a layered construction: the answer/private-keynote X is recovered by REVERSING ~16 encryptions woven with ~7 passwords plus a prime-basics step. The certified 3.2.2 example (escapes 1,4) is a controlled single-layer demonstration, not the full gate.

Concrete construction to investigate (not yet implemented anywhere):
1. 7 intertwined passwords = the SalPhaseIon page tokens in order: matrixsumlist, enter, lastwordsbeforearchichoice, thispassword, first hint("firsttint"), ("ans too") secondanswer, + last command/shabef.
2. "Intertwined" = the passwords are woven per-chain (not just concat/XOR); combine with the user's chain-5 correction p5=firsttint, p6=secondanswer.
3. "Prime basics" + "twenty-three ciphers" = the 23 primes / prime-index steps select which of 23 ciphers each of the 16 encryption layers uses (or a prime sieve over the 23-letter Bifid object alphabet).
4. "Sixteen" with the 256-symbol / 570-token object: e.g. 16 sequential CIPHER layers, or 16 base-16 / hex steps, or 16 columnar rounds.
Verifier: only the funded oracle (1GSMG1JC9 small blob / 17ucy1K9 dualite). Legibility of dbbib/faed intermediates is a weak signal under fact 5.
Date: 2026-08-31.

## Note 24 (2026-08-31): SalPhaselonCosmicDuality.png has NO visual/colored-character layer beyond OCR -- anti-alias only
Vertical-slice (beyond-OCR) forensics of `~/briefcase/gsmg-community/SalPhaselonCosmicDuality.png` (668x619 RGB), requested to hunt for any visual element (colored chars, "zeroed-out" marks, prime/16/7 markings) the OCR pipeline dropped. Full pixel analysis:
- Stepped area map (90x45 downsample): page = header, dense SalPhaseIon text block (rows 8-22), the Cosmic-Duality section with the base64 blob, and a bottom strip. No visual grid/pattern beyond plain text.
- Tint forensics: red/blue-tinted pixels in EVERY text row (blue systematically ~1.5x red). Distance test vs ink: 99% of red and 98% of blue tint lie WITHIN 1px of ink; ~0% far from ink -> pure anti-alias dithering, not selected characters.
- Saturated (whole-glyph) color test (red>150,blue>150 with strong deltas): of 44 glyphs in the SalPhaseIon block, 42 have ZERO saturated-blue and 0 saturated-red; the 2 with slight blue are letter-rounding anti-alias. No glyph subset is colored.
- Edge-frac via binary dilation = 1.00 in the cosmic (55-90) and bottom (115-130) regions too: uniform rendering bloom, no colored element.
CONCLUSION (decisive negative): the phase image carries NO colored-character / zeroed-out / highlighted-glyph / visual-structure channel that OCR missed. The only real colored-pixel cipher in this puzzle family is the phase-1 14x14 matrix (Note 22: BLUE=15, YELLOW=9). "Roses are White but often Red" / "some characters need to be zeroed out" are matrix-pixel mechanics, NOT hidden text tinting. The SalPhaseIon content = the streams we already hold (object_256, even_stream, dropped_29, plaintext_head + the 7 page tokens). This closes the "look at the phase image beyond OCR" branch: no new cipher-sequence/key present to define the 23^16 x 7! construction. Date: 2026-08-31.

## Research correction (2026-09-01): object_256 vs odd_pre_reduction are distinct

Precise relation between the two salphaseion-stream objects (user correction):
  * odd_pre_reduction = 285 chars, 25-letter alphabet (A-Z minus J), STILL contains
    the 29 I/O letters. == odd-position stream of the Bifid output, pre-IO-drop.
  * object_256        = 256 chars, 23-letter alphabet (A-Z minus J,I,O). ==
    odd_pre_reduction with all I/O removed.
  * dropped_29        = the 29 removed letters in order = OOIIOOOIIOOIOIIOIOOOOIOIIOIOI.
  Direct check: ''.join(c for c in opr if c not in 'IO') == object_256 (True);
  ''.join(c for c in opr if c in 'IO') == dropped_29 (True).
They are NOT interchangeable candidates: different alphabets (25 vs 23) and different
lengths. Both, plus their difference (dropped_29), were tested as literal X against the
funded oracle -> all negative (salphaseion-streams.json fields, data provenance). The
distinction matters for any decode: the pipeline's "23-letter object" = object_256;
odd_pre_reduction is the pre-drop form. Date: 2026-09-01.

## Note 25 (2026-09-02): the final-page image carries a white rabbit as a central structural element

The final-page scan `puzzle.png` / `whiterabbit.png` (the 14x14 blue/yellow matrix page,
Note 22) has the ORIGINAL conveyor-belt / matrix art PLUS a small hand-drawn-in-black
element at the image center that had been missed: a WHITE RABBIT (white body with black
outline), sitting inside the central white cells of the bit grid.

Pixel forensics (whiterabbit.png, 1048x1046, RGBA; 5 colors: black #000, white #FFF,
off-white #FEFEFE, blue #3F48CC, yellow #FFF200):
- Rabbit figure black-line bbox x[480-592] y[480-656] (113x177 px), 9 black components.
- Anatomy, bottom-up: a large solid body/base (4.3k px, x510-592 y600-656); a lower
  horizontal snout/mouth band (x495-524 y585-599); ONE eye -- a vertical black glyph at
  x525-539 y540-569 (user-confirmed: the feature in the face centre is the EYE, not a nose);
  a single centered face feature; and at the top THREE upright bars (x510-524, x540-554,
  x570-584, y478-509/524) = two ears + a central forelock.
- Reads as a FRONT-facing rabbit head (three top bars = 2 ears + forelock) with one central
  eye and a snout/mouth below, standing on a solid base.
- Artifact extracted to a clean 1-bit PNG (white body on white, black outline) for any
  future glyph matching; the source region sits purely in the white cells, NOT overlapping
  any of the 15 blue / 9 yellow bit-squares.

Interpretive tie-in (untested): the "Follow the White Rabbit" motif is a Chekhov's-gun on
the final page -- every prior foreground mechanic in this family is the matrix bit-read
(Note 22) and the layered 23-cipher/16-encryption/7-password construction (Note 23). The
rabbit itself may encode nothing (pure thematic garnish) or may be the "in front of your
eyes" / "white rabbit" pointer under leads 62-79. Not yet swept: compare the rabbit's
3-bar / single-eye silhouette against a letter or a glyph in the object_256 23-letter
alphabet, or its outline as a one-cell-per-pixel mask over the 14x14 matrix. No brute force
run yet; recorded as the missing earlier structural element. Date: 2026-09-02.
CLOSED (2026-09-10): the 9-best black components -> {a..i}->digit interpreter reading
(tested.md 203) is certified negative on both funded gates (41 rank/value tables x 5
streams x 47 alphabets = 20,424 candidates, escapes (1,4)). The remaining OPEN rabbit
reading is the object_256 silhouette/glyph match and the matrix-cell mask above.

### Note 25a (2026-09-02): uniform 16px pen across the whole rabbit -- eye == outline stroke width

Quantitative stroke measurement (distance transform half-width at the exact center of each
feature) on `whiterabbit.png` (rabbit region x480-592 / y478-656):

  Feature            | center half-width | stroke width
  -------------------|-------------------|-------------
  left ear bar       | 8.0               | 16px
  right ear bar      | 8.0               | 16px
  right ear outer    | 8.0               | 16px
  left face outline  | 8.0               | 16px
  EYE (x525-539,y540-569, 16x30 solid) | 8.0 | 16px
  snout/mouth band   | 8.0               | 16px

The rabbit is drawn entirely with ONE uniform ~16px pen; the EYE (the small 16x30 solid
black zone) is the SAME stroke width as the outline, confirming the user's observation that
"the eye and the outline are drawn at the same pixel size." Any reading of the eye as a
separate / differently-sized element is excluded.

Pixel-size relationships observed (no decode yet):
- Grid cells are 75px; rabbit stroke = 16px ~ 75/4.7. 75 = 5 x 15, and the blue-square count
  is 15 (yellow = 9). Stroke 16px and cell 75px do NOT divide evenly (75/16 = 4.6875), so
  the pen is NOT a clean 1/N sub-division of the cell.
- The rabbit sits at the exact CENTER of the 14x14 bit-matrix. Its black strokes map onto
  precisely 6 matrix cells: rows 6-8 x cols 6-7 = the central 2x3 block (NOT the whole 2x3
  = rows 6,7,8 x cols 6,7), all of which are WHITE cells (overlap NO blue and NO yellow
  square). Blue cells at (5,0),(2,1),(10,1),(7,2),(4,3),(1,4),(3,6),(0,7),(5,8),(13,8),
  (2,9),(8,11),(1,12),(2,13),(10,13); yellow at (13,0),(9,4),(6,5),(10,5),(11,6),(12,7),
  (6,9),(7,10),(9,12). The surrounding centre plateau rows 5-9/cols 5-9 is free of blue/yellow
  except (5,6)Y and (9,6)Y -- so the rabbit occupies the largest all-white central region.
  (A first mapping pass that scanned the WHOLE image's black pixels, not just the rabbit
  bbox, falsely listed 93 cells -- that was the grid line-work, not the rabbit; corrected
  to 6 centre cells by bounding the scan to the rabbit bbox x480-592/y478-656.)
- Glyph check (negative): the 16x30 eye is a solid vertical bar; its only letter matches are
  I / 1 / l, and I is EXCLUDED from the object_256 alphabet (A-Z minus {I,J,O}). A
  font-render IoU sweep over the full silhouette likewise returned IoU=0 for all 24
  alphabet letters + digits -> the rabbit is NOT a single filled-font glyph. Its strokes are
  deliberately uniform, not glyph-shaped.

Open question for the next sweep: whether the uniform 16px pen (and its odd 4.6875 ratio to
the 75px cell) is a deliberate "draw every stroke the same width" constraint (interpretive,
points to center) or carries a key. Not yet run as a brute-force candidate. Date: 2026-09-02.

### Note 25b (2026-09-02): the "follow the white rabbit" formula == the whole-pixel traversal read, now pinned exactly

User direction: the whole-pixel-matrix FORMULA is the "follow the white rabbit" formula (the
rabbit lives in the center of the 14x14 matrix; its read path is the formula). This session
pinned the EXACT read that earlier work had asserted but not locked down, then applied it.

Pinned read (reproduces the published decode exactly, from cell-center samples of the 14x14
matrix in `~/storage/external/briefcase/puzzle.png`, cells at 75px, sample at cell centre):
- Path: COUNTER-CLOCKWISE spiral from the top-left corner (ccw, not cw).
- Per-pixel bit (from the pixel's color): BLUE (63,72,204) = 1, BLACK/dark (0,0,0) = 1,
  WHITE (255/254,255/254,255/254) = 0, YELLOW (255,242,0) = 0.
- 196 bits -> 24 bytes (192 used + 4 trailing) spells, verbatim, the first 24 bytes:
  `gsmg.io/theseedisplanted`. This is the "low bit of each pixel's color" read. Witness:
  bit function + ccw spiral reproduced by an independent re-derivation in this session;
  matches README lines 79-81 and 179.

Structural counts along the bit function: 15 B + 9 Y + 85 W + 87 K per 196 cells.

Follow-the-rabbit re-reads (all oracle-tested this session via oracle.py attempt(), the
funded small-blob gate; selftest PASS immediately before):
- cw spiral, ring (center-out) spirals starting at the rabbit's cells (6,6)/(6,7)/(7,6)/(7,7),
  and other rabbit-anchored orders: each re-orders the same 196 bits into a non-ASCII
  binary blob; oracle attempt() on the raw/reversed/lower/upper string -> NO MATCH for all.
  Rationale for negatives: the bit pattern is sparse/high-entropy when reordered; only the
  designed ccw-spiral order aligns the bits into readable ASCII.
Net: the formula is confirmed identical to the matrix traversal read; its determinable output
is `gsmg.io/theseedisplanted` (the seed page slug, already swept as a keyword/key-seed in many
contexts, tested.md 2313/2407 -> 0 hits). No new oracle candidate produced. The rabbit's added
value is interpretive: it (a) sits at the center, (b) is drawn with the uniform 16px pen, and
(c) together names the traversal formula. Date: 2026-09-02.

### Note 25c (2026-09-02): whole-pixel formula reproduced via Pillow threshold + binary search on vector values

Same "follow the white rabbit" whole-matrix read, recovered a THIRD independent way using
Pillow (`PIL.Image.convert("L")` luminance + a binary-search over the luminance threshold
that binarizes the 14x14 matrix, then the ccw spiral):
- Cell-center luminances are exactly {black=0, blue=84, yellow=218, white=254/255}.
- Binary search over luminance threshold on the 14x14 cell-center vector: Tmin that still
  yields the known read is **T=84** (blue). Reading bit=1 if luminance <= T else 0, ccw
  spiral -> `gsmg.io/theseedisplanted` (verbatim). Adjacent levels: T=0 -> "frlf.hn.thdrd...",
  T=218 -> "gsmg/io/uieseeeisqmaouee", T=255 -> all-0xff (junk).
Witness: threshold/bit-function is just another encoding of the SAME bit assignment
(B,K dark=1; W,Y light=0) already proven in Note 25b; results identical.
Net: no new oracle candidate; confirms the whole-pixel formula == threshold+spiral read ==
seed slug once more. Rabbit-pixel bit-level comparison vs the whole matrix also performed:
rabbit's 16px micro-grid (11x7) bit string (29 one / 48 zero = 37.7% density) does NOT match
the whole 14x14 bit map at any scale (IoU ~0.22), and the rabbit only crosses W/K cells
(never B/Y); its under-footprint 3x2 cells row6-8/col6-7 read WK.../K/... bits = `001001`=9.
The rabbit is not a scaled image of the whole matrix; its role stays interpretive (names the
traversal), consistent with Note 25b. Date: 2026-09-02.

## Note 26 (2026-09-02): deep sweep of the gsmg.io/theseedisplanted page  -  8 color-coded sticker images + hidden POST form (new, not previously catalogued)

Live fetch of `https://gsmg.io/theseedisplanted` (200, 832 B, all images + form saved to
`~/storage/external/briefcase/theseedisplanted_page/`). Page body is tiny: an HTML comment
"Nice to see you around! Good luck little bunny hunter ;)", 8 `<img>` stickers, and a hidden
`<form method="post" action="/phase1verification">` with a single `password` field. No other
text/script/CSS. The 8 images are ~78x70 color-sticker reaction tiles; each is an
anti-aliased block-letter word (and in 2 cases a padlock icon) layered on a solid color
matching its filename prefix: BLACK/blue/red. OCR + pixel-read of each (prior work only mined
this page for the recovered form password, tested.md:153; the images were un-catalogued):

- `black_banking_-_war.png` black: banking-war meme icon (building/roof + small "DB"-style
  mark), no clean word.
- `blue_ca.png` blue   -> "CA"
- `blue_dig_i.png` blue  -> "dig i"
- `blue_lock_lo.png` blue -> padlock icon + "lo"
- `red_crypto_gic.png` red -> "crypto gic"
- `red_n_you.png` red     -> "n you"
- `red_open_lock_n_ing.png` red -> open-padlock icon + "n ing"
- `red_t.png` red          -> "t"

Reassembly attempts (fragment concat in page order, color-grouped, spaced variants) were
run through the funded small-blob oracle.py attempt() (selftest PASS): all NO MATCH
(cadigilocklocryptogicnyouopenlockningt, color groups, bankingwar, SALPHASEION re-test,
theseedisplanted, etc.).

Endpoint `/phase1verification` (the hidden form target): GET and empty POST both return
HTTP 404 empty body; blind POST probes with candidate passwords (SALPHASEION, the seed slug,
fragment joins) all 404 with empty body  -  no content/signal leaked, consistent with
404-on-wrong-password design. No new gate password obtained from this page this session.
Significance: the page is the same "follow the white rabbit"-named seed gateway the matrix
decodes to (Note 25); its only practical content beyond the known form password are these 8
stickers, whose fragment text (ca/digi/locklo + cryptogic/nyou/openlockning/t + bankingwar)
has not yet been reassembled into a reading that oracle-verifies. Date: 2026-09-02.

## Note 22 - grayscale conversion destroys the yellow/blue distinction (date: 2026-09-04)
Investigated "check yellow/blue value when the image turns to grayscale" directly on the pixel
data. Grayscale keeps only LUMINANCE and discards hue, so the yellow-vs-blue steering cannot
survive a grayscale conversion. Measured on the SalPhaseIon render:
- Yellow (R-dominant) pixels -> gray(lum) mean 205, spread 18-249
- Green  (G-dominant) pixels -> gray(lum) mean 218, spread 37-242
- Blue   (B-dominant) pixels -> gray(lum) mean 209, spread 17-239
- Black text                 -> gray(lum) < 80
All three colored classes collapse into the SAME bright mid-gray band (~205-218); the
anti-alias spread (each class runs the full 17->240 range) makes even those mean differences
noise. The only gray-separable information is black-text vs white-background  -  the binary
two-tone structure that note 18 already maps to the even/odd stream split (oracle-negative).
Consequence: any "yellow blue primes" decode step MUST be done on the color image (or per-hue
plane), never on a grayscale render; grayscale cannot separate the two colors. Consistent with
notes 15-21 (yellow/blue = anti-alias fringe/glow, not a distinct channel). No new candidate to
oracle-test. Date: 2026-09-04, local.

## Note 23 - F# SPA Bifid fixed: encrypt/decrypt now certified (date: 2026-09-04)
While building the ciphertools.co.uk-mirror SPA (F#/Elmish) its Bifid module had a wrong
ENCRYPT direction. Root cause, two parts:
1. My F# list-comprehension `[ for (r,c) in coords -> r; c ]` does NOT flatten to
   r0;c0;r1;c1 in F#  -  it silently corrupts the coordinate stream. Fixed by collecting
   with an explicit mutable List.
2. The half-split re-pairing op IS the true Bifid DECRYPT (matches CyberChef
   BifidCipherDecode and the certified Python `bifid_repro.py`: stage witness
   faed->"BTCSEED..." PASSES), but ENCRYPT is different: rows-fractionated stream
   (all row digits then all col digits) read in pairs (CyberChef Encode / pycipher).

Verification (F# compiled assembly, `cipherspa` Ciphers.fs):
- Stage witness: keyedSquare25("DBIFHCEG") + bifidDecrypt(faed_570, period 0) head
  == "BTCSEEDDEOEMCKEADHBSCHDKBDCSDKDVBXCPCOCH"  (SELFCERT PASS)
- Round-trips Decrypt.Encrypt == plaintext for periods 5, 8, 0 (all True)
- pycipher vector Bifid("PHQGMEAYLNOFDXKRCVSZWBUTI",5).encipher(
  "DEFENDTHEEASTWALLOFTHECASTLE") == "FFYHMKHYCPLIASHADTRLHCCHLBLR" (exact match)

This is the puzzle-side significance of the ciphertools Bifid stage: period 0 = full
message length, decrypt = interleave->half-split->re-pair, exactly what the documented
pipeline (tested.md 49/63/64) uses. The SPA's decrypt now reproduces the stage head.
Date: 2026-09-04, local.

## Note 24 - ciphertools SPA made to compile on a real Fable 5 stack (date: 2026-09-04)
The F#/Elmish mirror SPA (`/usr/tmp/opencode/cipherspa`) originally pinned package
versions that DO NOT EXIST on nuget (Fable.Core 4.3.0? no: 4.3.0 ok; the broken ones were
Fable.Elmish.React 4.0.7 and Fable.Browser.Dom 3.0.2)  -  it never restored or compiled.
Aligned it to a real, coherent Fable 5.x stack and fixed the modern-API UI calls:
- Packages: Fable.Core 5.2.0, Fable.Elmish.React 5.6.0, Feliz 3.3.3, Feliz.Bulma 5.0.0.
- Removed the nonexistent Fable.Browser.Dom pin (unused in source).
- UI fixes: keep Program.withReactBatched (withReact not present), plain Html.button
  instead of removed Bulma.button/Bulma.control, prop.readOnly true instead of removed
  Bulma textarea.isReadOnly, wrap button lists in prop.children, onChange handlers return
  unit.
Result: `dotnet build` -> Build succeeded, 0 warnings, 0 errors. The cipher logic
(`src/Ciphers.fs`) is unchanged from Note 23's certification (stage BTCSEED witness +
period-5/8/0 round-trips + pycipher vector all still pass).
Still blocked: generating the JS bundle needs the `dotnet fable` tool, whose nupkg is
defective (no DotnetToolSettings.xml + targets .NET 10; only .NET 8.0.30 installed). No
usable Fable compiler is installable on this device. Deploy path: install a .NET 10 SDK
then `dotnet tool install fable`, or run the certified `src/Ciphers.fs` from a plain
console (certc project) with no Fable at all. Date: 2026-09-04, local.

## Note 25 - Fable JS-bundle build: definitive platform blocker (date: 2026-09-04)
Final attempt to make the ciphertools.co.uk SPA JS bundle. Installed the .NET 10
runtime AND .NET 10 SDK on this Termux device, then ran the Fable 5 compiler two ways
(5.8.0 and 5.16.0, both targeting net10):
- `dotnet tool install fable` fails: the nupkg ships no DotnetToolSettings.xml the
  SDK tool installer accepts -> workaround = extract nupkg, run fable.dll with the
  .NET 10 host. `fable.dll --version` works; argument validation works (a nonexistent
  project prints "File does not exist").
- BUT any real compile (`fable <fsproj> -o out`) exits 1 with NO output, no error, no
  crash dump, no partial artifacts, on both versions and on .NET 8+10 runtimes/SDKs.
  Stack limit, memory, CoreCLR presence (libcoreclr.so) all fine. Conclusion: silent
  failure inside FSharp.Compiler.Service on this Termux linux-bionic-arm64 CoreCLR
  build - an environment incompatibility, not config-fixable.
Consequence: JS bundle cannot be generated on this device. The cipher logic is NOT
blocked - `src/Ciphers.fs` runs from a plain .NET console (`certc` project) with the
full certification intact (CTCSEED... stage witness, period-5/8/0 round-trips,
pycipher vector). The SPA source builds cleanly (`dotnet build`: 0 errors). Ship
source + README and run Fable+vite on a normal host. Kept `.fablel/` (extracted Fable
 5.16.0) in the project for use once a working host/container is available.
Date: 2026-09-04, local.

## Note 26 - Fable JS build unblocked: `/` EACCES crash root-cause found and IL-patched (date: 2026-09-04)
The "definitive platform blocker" in Note 25 was WRONG to the extent it labelled the
failure unfixable. strace showed Fable's very first action after its banner was a direct
`openat("/", O_RDONLY|O_DIRECTORY) -> EACCES` ONLY when a `.fsproj` arg was passed (bare
`fable` runs scanned cwd and worked). Chasing it through Fable's source:
`Fable.Compiler.Util.File.getExactFullPath` (src/Fable.Compiler/Util.fs, used only in the
`[path]` command path) recursively walks EVERY ancestor of a path up to `/`, calling
`di.Parent.GetFileSystemInfos(di.Name)` at each step to fix filename casing. On Android,
`/` is `drwxr-xr-x` but SELinux-blocked for the app (`u:object_r:rootfs:s0` vs
`untrusted_app` context) -> the `/` enumeration throws -> silent exit 1.
Fix: rewrote `getExactFullPath`'s IL with Mono.Cecil (ilpatch project, .NET 10, Mono.Cecil
0.11.5, NuGet reachable). In this Fable build `getExactPath` is a local closure invoked by a
trailing `callvirt FSharpFunc<..>::Invoke` right after `call Path.GetFullPath`; I replaced
that one `callvirt`/closure`Invoke` (offset 001B) with `ret`, so the method now just returns
`Path.GetFullPath(path)` (casing-fix is moot on case-sensitive Linux). Result: the `/`
EACCES crash is GONE - Fable 5.16.0 now loads all assemblies and proceeds. Backup kept as
`Fable.Compiler.dll.bak`.
State after the fix: Fable prints its banner then still exits 1 SILENTLY with no output and
NO failing syscall, on every project (even a trivial one-line fsproj with no Fable.Core),
before/at the MSBuild/FSharp.Compiler.Service project-cracking step. No subprocess spawned
(no `dotnet restore`/`npm` via execve), stack raised to 64MB, PTY, --verbose: all still
silent RC=1. So a SECOND, deeper Termux-linux-bionic-arm64 issue remains in FCS project
evaluation (empty/undisplayable error). The cipher logic is unaffected: `src/Ciphers.fs` is
still certified via the plain `certc` console. Next: either keep patching FCS/MSBuild on
Termux, or ship the same author-algorithm faithfully reimplemented for the web in plain JS
(no Fable) using the certified vectors as oracle.
Date: 2026-09-04, local.

## Note 27 - Vowpal Wabbit live lead: repo validated as stock clone + first successful Termux Android build (date: 2026-09-05)
The ~/vowpal_wabbit tree is a pristine clone of the official github.com/VowpalWabbit/vowpal_wabbit, branch master, HEAD 9c8600b77 (release 9.11.3), clean tree, cloned this afternoon - NO local puzzle content, no hidden strings, no modifications. Relationship to the puzzle is still UNCONFIRMED; the working theory is thematic/hint value: VW is the "online/ interactive" machine-learning toolkit whose mascot is a wabbit/rabbit, matching the robots.txt ASCII wabbit glyph-art, and its own tagline-space ("wabbit will support solve complex interactive machine learning problems, sort of") is a Dada-style sentence that smells like the machines robots.txt alt-text verse. That sentence is a strong candidate shape for the 12-run glyph ciphertext (ABBCDEFGHFIJ), see tested.md 151.
Build achieved on Termux (aarch64, bionic):
- cmake configure needs ext_libs submodules OR the *_SYS_DEP flags. Used SYS_DEP=ON for rapidjson/fmt/spdlog/zlib/gtest/boost_math; boost-math headers come from pkg boost-headers (1.91). Configures clean. help2man missing = manpages only, not blocking.
- gcc-14 fails: (1) <sys/timeb.h> absent on bionic (ftime never used - guard with !defined(__ANDROID__)); (2) std::riemann_zeta not in this libstdc++; needs boost::math::zeta (public API, not boost::math::riemann_zeta) with <boost/math/special_functions/zeta.hpp>; (3) missing netinet/in.h + arpa/inet.h in parser.cc for htonl/htons/INADDR_ANY; (4) archive link dies in ld.bfd "access beyond end of merged section" on libc++ std::__ndk1 string sections - gcc-14 here is configured --with-ld=/usr/bin/ld.bfd full-path so -fuse-ld=lld is IGNORED.
- Fix: rebuild with clang 21 (Termux clang++ drives ld.lld by default, std lib is still libc++ v1/_ndk1 so ABI-consistent). Ninja rebuild 190 objects + link, all clean. Result: build/vowpalwabbit/cli/vw -v -> "9.11.3 (git commit 9c8600b77) Compiled features in binary: LDA;SEARCH;NETWORKING"; smoke-tested --quiet on a 3-line dataset, RC 0. Install prefix layout set so vw lands at $HOME/.local/bin/vw (run cmake --install build after a make target if needed).
Unresolved: what a whitespace/online-learning toolkit contributes to a BTC escrow puzzle. Candidates to test: (a) treat the 12-run glyph cipher as VW-lattice/rank-labels to emit the "wabbit will support solve ... sort of" sentence; (b) use VW as a transposition solver over the final-page digit streams; (c) pure rabbit thematic red-herring. VS of building it: it is now buildable on-device, so any text-fitting/online-search use is cheap.
Date: 2026-09-05, local.

## Note 28 - ~/ninja and ~/samurai: companion stock clones, likely part of the same checkout batch (date: 2026-09-05)
Alongside ~/vowpal_wabbit, two more build-tooling trees were cloned this afternoon, both pristine stock:
- ~/ninja = official ninja-build/ninja, master, HEAD de08982 (merge "jobserver-pool"), clean tree, unbuilt.
- ~/samurai = michaelforney/samurai (the samu ninja-reimplementation in C), master, HEAD 531ba70, clean tree, unbuilt (build via `make` per its Makefile; C only, no deps).
If the wabbit/rabbit lead is thematic, this batch pattern (ninja + samurai aka "samurai/ninja" build tools + Vowpal Wabbit ML tool) suggests someone pre-staged build tooling to run computation on-device, OR these were cloned by a prior agent session to compile VW/ninja. No puzzle content inside any of the three trees. Not a cipher lead by itself; noted so future sessions don't re-audit them.
Setup state (all three built + installed to ~/.local/bin on this device, date 2026-09-05):
- ninja 1.14.0.git: `python3 configure.py --bootstrap` compiles all .cc, but the final link `c++ -Lbuild -o ninja build/ninja.o -lninja` fails with the same gcc-14 bfd/lld merged-section issue as VW. Workaround identical: `clang++ -fuse-ld=lld -o ninja build/ninja.o -Lbuild -lninja` relinks the gcc-built libninja.a fine. Binary: ~/.local/bin/ninja.
- samu 1.9.0: `make` alone fails (Makefile hardcodes `c99`, absent on Termux); `make CC=cc` builds clean (C only, links with cc default which is clang/lld). Binary: ~/.local/bin/samu.
- vw 9.11.3: cmake --install . installed headers/libs to ~/.local; the CLI binary target is NOT in the install set, so copy build/vowpalwabbit/cli/vw to ~/.local/bin/vw manually. All three `--version`-verified working on-device.
- ~/rsa-elgamal-algorithm (newest clone, 16:55): michaelforney... no - stock Eldoov/rsa-elgamal-algorithm, a BU CS789 Fall 2022 student project (RSA + ElGamal toy CipherMachines with Eve-crack role; tools/ = BBSrand, BBstepGNstep, MRprimalityTest, NRrand, PRfactorFind, basicTools; 'Autorun Samples.pdf' = its demo output doc). Clean tree, no puzzle strings. Purely classic-crypto teaching code; if the "single tool that built every phase" lead is a real piece of software, this is one more candidate-family entry (classical primitives, small-prime factoring), but nothing ties it to GSMG.
Date: 2026-09-05, local.

## Note 29 - Full ~/ audit: all folders stock clones + one custom toolkit (date: 2026-09-05)
Complete scan of ~/ (ls -lat + per-dir git status): ~95 git repos, all clean stock clones with these exceptions:
- ~/briefcase/ (no git): ~70 custom puzzle scripts including run_mnemonic_crack.sh (ACTIVE, running against wallet.hash in 20-way chunks), wallet.dat, wallet.hash, mnem_chunks/; scripts cover AES-256-CBC, hill_cipher.py, vigenere.py, kangaroo, BIP39, ECDSA steps-hex, and various crack runs (15036, rockyou, wallet108, wallet255, qwert). This is the pre-assembled puzzle toolkit.
- ~/solitaire_cipher/ (mathie/solitaire_cipher): dirty=4  -  modified lib/solitaire_cipher.rb + lib/string_ext.rb, added untracked lib/solitaire_deck.rb and bin/; local additions to a Solitaire cipher implementation.
- ~/vowpal_wabbit/: dirty=4 = the four source patches from Note 27 (confidence_sequence.cc, parser.cc, bfgs.cc, allreduce_sockets.cc).
All other dirty trees (open-crypto-puzzles=125, CryptoDeepTools=65, BIT_SHARK=36, rsz=14, simple-bitcoin-wallet-recovery=10, etc.) are local build artifacts (compiling .o/.a/.so in place)  -  their git status confirms this.
No new, unidentified puzzle content was found. The ~/ workspace is entirely stock clones + our own analysis + the pre-assembled briefcase toolkit.
Date: 2026-09-05, local.

## Note 30 (2026-09-06): pixel-pass corrections to Note 21, and the render's a/b middle run + Dualite-head visibility

Follow-up from tested.md section 176 (fresh-eyes pixel pass on SalPhaselonCosmicDuality.png).
- CORRECTION to Note 21's "rendered faed = 387 (omits 183 vs stored 570)": glyph-column
  segmentation gives 46/line x 13 lines = 598 rendered tokens, and tesseract independently
  reads 593 clean chars (first 69 == stored dbbib byte-for-byte). The "387" was that
  session's OCR under-read; the real render deficit vs stored (69+571=640) is ~42-47 tokens.
- The render DOES carry the a/b "middle run" after the 69-char dbbib head (the ~22-char run
  the README says the final-page image lacks)  -  present on the SalPhaseIon page, so the
  91-token dbbib variant corresponds to this page, not the final page.
- The render's Cosmic-Duality body is the DUALITE blob's own base64 (salt 2d3f6fe06dc950e6
  decoded from its visible head) truncated at ~842/1792 chars by the bottom rule; no unseen
  ciphertext bytes.
- 10 fresh candidates (rendered 593-string + variants, visible Cosmic b64 head + prefix
  slices) oracle-tested NO MATCH on both gates. No new key material on this page.
- Lead ranking impact: open-lead #1 (decode the two digit streams) is unchanged; the render
  vs stored discrepancy is now a MEASURED ~42-token gap, not a 183-token gap, so "some
  characters need to be zeroed out" remains an interpretive matrix/union-jack mechanic
  (Note 22/24) rather than evidence of hidden glyphs on this page. Date: 2026-09-06.

## Note 31 (2026-09-06): yin-yang-svgtiler (edemaine) audited  -  not the matrix's structure/tool; yin-yang rules negative on the phase-1 14x14 in all four polarities

User-supplied lead: audit https://github.com/edemaine/yin-yang-svgtiler (Erik Demaine, Jayson
Lynch, Mikhail Rudoy, Yushi Uno; "Yin-Yang Puzzles are NP-complete", CCCG 2021). Yin-Yang
(Shiromaru-Kuromaru) rules: (1) every 2x2 block must be non-monochromatic; (2) exactly two
4-connected components, one per color. The GSMG "yin yang = both had to be equal" hint
(sections 65/66, row==col total 101, vacuous identity) and the phase-1 14x14 matrix
(87 black / 85 white / 15 blue / 9 yellow) were the connection to test.

METHOD (read-only, clone + local checker): (a) cloned repo; (b) verified the SIMPLE
message's spinner vs. our own checker semantics against the repo's canonical test.coffee
(the 2x2 check and 4-neighbor DFS are byte-identical in meaning); (c) regenerated the full
14x14 from ~/briefcase/gsmg-community/puzzle.png cell-center sampling (74.86 px pitch):
row counts 87/85/15/9 EXACTLY matching tested.md 3222, and every blue/yellow coordinate
byte-equal to data/follow-white-rabbit-grid.json (W-pass).

STRUCTURAL RESULT (our checker, 4 polarities):
  K/B=1 W/Y=0 (canonical) : mono-2x2=19, black_cc=18, white_cc=21 (102/94)
  inverted                : mono-2x2=19, black_cc=21, white_cc=18 (94/102)
  K-only=1 (colors->0)    : mono-2x2=24, black_cc=19, white_cc=11 (87/109)
  W-only=1 (colors->0)    : mono-2x2=13, black_cc=36, white_cc=23 (85/111)
Yin-Yang validity needs mono-2x2==0 and components==1+1. NO polarity gives either. The
phase-1 matrix is therefore NOT a yin-yang solution configuration, a yin-yang puzzle input,
or a yin-yang filled board under any reading of which cells are given vs. added (blue/yellow
as "dotted-added" %/0 vs. as pre-colored X/o). No yin-yang structure is present.

VISUAL-STYLE MISMATCH: yin-yang-svgtiler renders every cell via yinyang.coffee as a 20x20
viewBox gray (lighter) cell containing a black/white CIRCLE; the phase-1 matrix is SOLID
black/white SQUARES with blue/yellow marks (puzzle.png pixel reads). The two are not the
same visual language. Other 14x14 candidates on device (follow-white-rabbit tile, 25px
cells) also use solid squares, not circles.

AUTHORSHIP: no signal links Erik Demaine to the GSMG author; the Note-29 ~/ audit found
no yin-yang-svgtiler clone on device; the "778" bit-width and spiral-motif are generic.
The repo's "spiral puzzle" (5x4, yin-yang-symbol-inspired, README) shares only THEMATIC
spiral language with the matrix's ccw-spiral read (sections 2748/3138)  -  the read itself
(196 bits -> gsmg.io/theseedisplanted) was already oracle-closed as X-source.

VERDICT: the yin-yang-svgtiler is structurally, visually and attributionally NOT the
phase-1 matrix generator nor a usable formula source for X. The "yin yang both equal"
hint stays closed as the row==col total identity (section 65). Both funded gates remain
open. (Full 14x14 extraction now pinned in this session's scratch:
grid14x14 = the 14 strings in tested.md 3222 area / reproducible via note-31 script.)
Date: 2026-09-06.

## Note 32 (2026-09-07): CORRECTION QUEUE  -  note 9's "section 1 = 69, not 91" is source-disputed; live-page middle run reinstated

Note 9 (2026-08-27) "corrected" dbbib to 69 = 3x23 by OCR of `briefcase/SalPhaselonCosmicDuality.png`,
declaring the 22-char middle run `bfdhbeffcdbbfcccgb...` (tokens 45-67 of the 91-token stream)
"spurious". Deep source audit (tested.md row 193) shows the middle run is REAL page data:
it is present in BOTH machine-readable primaries  -  the 2023-06-01 archive `data/live_salphaseion.html`
and the live 2026 fetch (contiguous `bfdhbeffcdbbfcccgbfbeeg`, tokens 45-67, before the
104-token a/b run at 91-194)  -  and Note 30 (2026-09-06) already reports the render DOES carry
the ~22-token middle run after the 69-token head. Impact: (1) dbbib 91 = 7x13 reinstated, and
91 + 104 = 195 = 15x13, restoring the match between dbbib's 13-column forms and the decoded
directive `matrixsumlist` (=13) that note 9 dropped; (2) sweeps keyed to the 69-token truncated
dbbib (tests 21-23, 48-50, and note-9-era matrix-sum/keyed-alphabet results) were computed on a
misread stream and are invalid for the live object. 125 fresh oracle-certified candidates over
middle-run literals + 15x13 / 7x13 matrix-sum reads and boundary merges -> 0 MATCH (row 193).
Action: reverse note 9's length correction in README/data notes; treat the 69-char stored dbbib
in `data/finalpage-digit-streams.json` as a stale OCR-derived variant, not ground truth; the
91-token page stream is the live object for lead-0 interpretation. Date: 2026-09-07.

## Note 33 (2026-09-07): the gates' full funding lifecycle is now closed on-chain  -  original escrow, funder, and both relay spends

Page-completed the gate history (blockchain.info/rawaddr pages 0/50/100, 126 txs) and traced
the origin + the other gate:
- ORIGINAL ESCROW: tx `73e48ff571a7e9a43875...`, block 571,497, 2019-04-13 16:32:40 UTC,
  created `1GSMG1JC9...` with exactly 5.00000000 BTC from 7 inputs of `1EtbTvVB8QTGN4mduSdy7n4cZQm4iYTpQ1`
  (865,890,724 sat, change 365,857,304 back to sender). `1EtbTvVB8...` is a dedicated
  pass-through wallet (50 lifetime txs, 2014-12-12 -> 2026-01-22, no OP_RETURN ever); its 7
  UTXOs were accumulated from different sources over 2017-03 -> 2019-01, a deliberate staging.
- RELAYS (the address's only spends, total 750,353,498 sat = 7.5035 BTC, matching addr stats):
  - block 630,001, 2020-05-11 (2020 halving block +1): spent 5.00001366 BTC, sent
    exactly 2.50000000 to `17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa`, change 2.49815966 kept.
  - block 840,725, 2024-04-20 (2024 halving day): spent 2.50352132 BTC, sent exactly
    1.25000000 to `17ucy1K9...`, change 1.25324300 kept.
  So `17ucy1K9...`'s 3.75 BTC principal = 2.5 + 1.25 from this gate; prize split 5 BTC = 1.25
  (small) + 3.75 (large) is fully explained by these two halving-day relays.
- AUTHOR REVISIT: on 2025-09-09 (block 913,830) the funder cluster sent dust "pings" to BOTH
  gates in one tx `3775e974b0ace913...` (1,070 sats -> `1GSMG1JC9...`, 9,500 -> `17ucy1K9...`),
  i.e. the identity that created the escrow re-touched both gates 6.5 years later.
- No OP_RETURN/string content anywhere in the funding path; the 2026 dust-tag runs (546-sat
  batches from `1JG648ya...`/`145ZQ9si...` and the "From N0E"/BellaCiao1 family, already
  audited row 191) remain unrelated noise on top.
Impact: the on-chain route's open items (original funding creation + funder + the gates'
relation) are now closed with a fully consistent ledger; the funding path carries no
alphabets/keys, so lead 0 (dbbib/faed interpreter-alphabet) is unaffected and remains THE
crux. No ranking change: this removes route-2's residual gap, it adds no candidate. Date:
2026-09-07.

## Note 34 (2026-09-07): deep-research closes the last discovered alphabet gap; #110 witness reproduction; gros false positive

1. Re-auditing row 194 exposed a real mechanical gap: rekey91.py keyworded every alphabet
   through keyed28() (dot-stripping dedupe), so the LITERAL 28-char board
   `FUBCDORA.LETHINGKYMVPS.JQZXW`  -  the only keyed alphabet in the puzzle, but call it
   AUTHOR-SEEDED / COMMUNITY-PERMUTED, not "author-verified": the 26 letters come from the
   author's own Phase-3.2 sentence ("A fubcd-king & oracle-queen, thingky mvps, ..."), but the
   letter ORDER, the dot placement and the 8/18 splice are the community's. See
   `R-BOARD28B-2026-09-26` FINDING 3, which also retires the permutation framing.
   (certified_vic.selfcert round-trips the 149-digit VIC message verbatim under escapes
   (1,4))  -  was never applied to the true 91-token dbbib or faed. Tools/phase322_literal_sweep.py
   fills it: 1824 forms, 2502 clean, 0 MATCH on both gates (tested.md row 196; all witnesses
   PASS before the run). This removes the last untested alphabet-family instance I can derive
   from verified author material. Lead 0's interpreter-alphabet remains the crux and is now
   bounded to non-mechanical on-page/visual reads.
2. Issue #110's 12-address construction reproduces: both published witnesses (X=4 -> 1Bwq9PK,
   X=10 -> 1Hby7BY) exact from certified cc; 39 unique addresses, none a gate (row 197).
3. The `sha256^3("theseedisplanted")` EVP-MD5 read of the cosmic blob gives a 1327-byte
   plaintext that is a padding false positive (9075d816..., high entropy, no structure);
   the gros 2432B object #111 used is not reproducible from this folder and is in the
   #104-disavowed branch.
Net: no new candidates; row-194's negative families are now provably complete for the
literate keyword family. Lead 0 unchanged. Date: 2026-09-07.

## Note 35 (2026-09-08): exhaustive interpreter-perm x certified-VIC decode swept to 0 MATCH; a prior false negative corrected

1. Row 199 closes the last formally-open mechanical gap under lead 0. Section 145's
   interpreter_perm_sweep.py fed 8 documented intermediates (incl. raw dbbib/faed under each of
   the 9! perms of a..i) straight to the oracles with NO VIC decode layer; section 76's
   mapping_hillclimb.py was annealing, not exhaustive. New tools/experm_vic.c enumerates all
   362,880 perms, VIC-decodes the mapped 91-token dbbib and faed_570 under the CERTIFIED board
   (escapes 1,4), emits 725,760 candidates. Decoder verified byte-exact vs the certified Python
   (identity `BLRIGU...` and CANON map 815063742 `FLUTHCC...` both reproduced, plus 25 random
   perms). Result: 725,760 x NO MATCH on BOTH gates, 0 genuine MATCH (passes small ~3m26s,
   dualite ~5m32s, oracles --selftest PASS immediately prior).
2. CORRECTION: during verification the first build of experm_vic.c was found to have a decode
   bug (a fall-through `i += 1` double-consumed every plain digit, producing e.g. `BKIGU...`
   against Python's `BLRIGU...`). The anterior 725,760-line oracle negatives produced from that
   build are INVALID and are superseded by this row's corrected run. Lesson reasserted: a
   negative is only a negative when the known-good witness re-found through the same code.
3. Impact: lead 0 (dbbib/faed interpreter-alphabet) remains the crux, but the "pure 9-letter
   perm applied to raw dbbib/faed, then VIC-decoded under a 28-char board" reading is now fully
   closed. Remaining live readings are necessarily layered: the alphabet perm over something
   DERIVED from the streams (position/sum/diff constructions, transposition before substitution)
   rather than over raw dbbib/faed alone. List of what remains in note-1's "bounded to
   non-mechanical on-page/visual reads" is unchanged. Date: 2026-09-08.

---
## NOTE 27 (2026-09-10): Decentraland Estate #955 RESOLVED  -  "gsmg.io magic puzzle piece"
Source: Decentraland Marketplace API (marketplace-api.decentraland.org) `/v1/nfts?contractAddress=0x959e104e1a4db6317fa58f8295f586e1a978c297&tokenId=955` (live, accessible).
- contractAddress 0x959e104e1a4db6317fa58f8295f586e1a978c297 = **Decentraland Estate (ERC-721 EST)** registry. tokenId **955**.
- **name: "gsmg.io magic puzzle piece"**  -  direct corroboration that this token is named for the puzzle.
- **description: "White Rabbits everywhere"**  -  matches the white-rabbit theme of the gsmg.io Weebly-era posters.
- **size: 2**  -  ESTATE makes it 2 LAND parcels. **parcels: (-41,-16) and (-41,-17)** (adjacent in y, i.e. a 2-high stack).
- owner 0x5d801b2b0b216790a49898b322246282547b546b, created 2018-11-08, URL /contracts/0x959e104e1a4db6317fa58f8295f586e1a978c297/tokens/955.
- estate preview API map.png (api.decentraland.org/v1/estates/955/map.png, 1024x1024): 2 BLUE parcel blocks top-left (estate fill color 80,84,212), NO green fill in the preview; red 255,0,68 used ONLY as the marker pin around (x500-525,y480-525) with pink 255,153,144 halo. The "blue AND green / red 2x small block" reading therefore comes from the LIVE ATLAS VIEW, not the estate preview PNG.
- Atlas tile endpoints (api.decentraland.org/v2/map.png, peer.decentraland.org/map) return empty/404 from this network; atlas.decentraland.org v2 tiles/parcels endpoints empty too, subgraph & etherscan V1 blocked. So the live color layout of the 2 parcels vs district colors around (-41,-16/-17) is NOT yet machine-verifiable here.
- Pragmatic follow-up: LAND contract 0xf87e31492faf9a91b02ee0deaad50d51d56d5d4d encodes coords as (x+150)<<12 | (y+150)<<? ; -41,-16 => (-41+150)=109 => 0x6D; need exact bit layout to confirm mapping via any RPC. Marketplace API already gave resolved parcels, so no need.
- Possible interpretative bridge: estate = 2 LAND = "2 blocks". Sticker colors black/blue/red + gi.../lo (lock/ca/dig_i) might map to district colors on the DCL atlas around these coords (districts are colored blocks on the atlas). If the puzzle owner's district/independent parcels around (-41,-16/-17) are colored, the SIGNAL could be the district's color-code text (each DCL district name). Still needs the atlas tiles.
- Actionable: (1) keep the estate/parcel facts (they anchor "magic puzzle piece" to gsmg). (2) If the user sees blue+green+red on the atlas live view, ask them to dump the visible parcel coordinates + what color each parcel shows, and/or screenshot; map.png renders I can analyze, raw visuals I cannot.
- UPDATE 2026-09-10: PARKED / closed as probably a DIFFERENT puzzle. User: "skip decentraland, might be a different puzzle from gsmg". The estate's name
  "gsmg.io magic puzzle piece" + "White Rabbits everywhere" is suggestive but the 2-parcel blue/green/red-atlas reading was never machine-verifiable and may be
  unrelated (possibly a distinct DCL scavenger hunt). Do NOT route further puzzle effort here unless a concrete cross-link reappears.

---
## Note 36 (2026-09-12): sealed-split reconstruction capability - `tools/shamir_combine.py` (GF(2^8), GF(p), XOR)

The "Just Half"/"Better Half" and 36 x 32-byte mystery-block material may be a 2-of-2
mechanical split (Shamir byte-field, Shamir over a big prime such as the secp256k1 group
order N, or a plain XOR one-time pad). Until 2026-09-12 the folder had no reconstruction
tool for any of the three layouts; that gap is now filled and certified.

- **Tool:** `tools/shamir_combine.py`. Stdlib only. Three modes:
  - `gf256` - shares as hex, layout `{y1..yN, x}` with the x byte **LAST**. Tables and
    arithmetic are a verbatim Python port of hashicorp/vault/shamir (samiam.org tables,
    generator 0xe5); privy-io/shamir-secret-sharing replicates them byte-for-byte, so
    shares from either library combine here. NOTE the x byte is NOT 1,2,3: vault assigns
    a random permutation of 1..255, so the last byte can be anything distinct.
  - `gfp` - shares as `<x>:<yHex>` big-integers; Lagrange at x=0 recovers the integer
    mod p. Default p = secp256k1 order N; `--prime` overrides (e.g. any published mod,
    AES prime, NIST prime).
  - `xor` - every share XOR-combines to the secret (k-of-k one-time pad; exactly what a
    2-of-2 "two halves" split would be).
  - `--selftest` certifies all three. The GF(2^8) witness is REAL shares produced by TWO
    OTHER libraries: hashicorp/vault (Go) and privy-io (TS) each split
    b"cross-check-secret" (3 parts, threshold 2); both share pairs re-decrypt here.
    GF(p) is certified by a deterministic polynomial vector f(x)=123+7x plus round trips;
    XOR by a fixed vector plus a random-pad round trip. `SELFTEST OK` on 2026-09-12.
- **Registration of prior art:** the briefing elsewhere ("Shamir GF(256) recovery from
  mystery blocks (multiple x combos) -> MISS", "Shamir mod256 and Lagrange over N from
  mystery blocks -> MISS") is treated as UNCERTIFIED here: this folder has no witness that
  re-finds anything through the same code from those blocks, so per repo rules it is not a
  closed negative. Any re-run now goes through this certified tool and earns a real row.
- **New angles this enables that the briefing did NOT cover:**
  1. XOR 2-of-2: pair the 36 x 32-byte blocks (adjacent or cross-ordered) and XOR each
     pair; any pair whose XOR is a 32-byte scalar in [1, N-1] is immediately an oracle
     candidate.
  2. GF(p) over the two printed gadget halves/content-blocks under N (mod N) and under
     any other published mod - big-int Lagrange, not the byte field the libraries use.
  3. GF(2^8) re-check of the mystery blocks via THIS port (the certified vector gives the
     missing witness the briefing's negatives lacked).
- **Feeding the oracle:** any reconstructed 32-byte material must still pass
  `tools/oracle.py` (it is fed as the AES password via sha256(X), and as a private key it
  must HASH160 to 1GSMG1...). The oracle `--selftest` passed 2026-09-12 before this note;
  run it again before any search that uses it.
- Current status: sweep EXECUTED 2026-09-12 (tested.md late-37): all 36 blocks + tail +
  OP_RETURN halves under XOR / GF(2^8) / GF(p)=N 2-of-2 layouts -> 5109 unique candidates
  x both gates = 10218 submissions, 0 MATCH, with shamir_combine and both oracle
  self-tests as witness. The 36-block 2-of-2 split reading is now a certified negative.
  Not yet swept: 3+ share (higher-threshold) recombination and x-layouts beyond
  first/last/sequential byte placement.

## Note 37  OP_RETURN payloads corrected on-chain + split-semantics battery = certified negative (2026-09-12)

- **Data correction (tested.md late-38):** pulled both puzzle OP_RETURN txs straight off
  blockstream.info. GSMGJH = PUSH71 "GSMGJH " + 64B (exact match to briefing). GSMGBH =
  PUSH71 "GSMGBH" + **65B body**, NOT the 34B the briefing recorded: the body is
  34B `1f3afc...5165` || **31B `0af99010f0495f43c1a332d45190631275191e429aa2dc1aae3b25ec79b35f`**.
  The 31B tail had never been in any candidate space. Both txs: block 949653, spent from
  author wallet 1GSMG9VDLTU6jyuG7bkNMdmnHBLtbbM51M, 546 sats each to burn address
  11111119536NnU2vPAvoQhvkheQ8ejYJ. The burn address additionally holds five third-party
  ASCII passphrases ("secondanswer"/"yourlastcommand"/"isolveditwithanabacus"/
  "leavethematrix"/"hereismysecret") - NOT author-signed, noise.
- **Split-semantics battery (tested.md late-39):** every natural way to treat the two
  "halves" as shares, over {jh halves, BH head/tail, matrixsumlist half/better,
  xor_key, trail}: GF(2^8) 32/33/34-byte-share pairs in x-last and x-first layouts;
  GF(p) mod N 2-point and 3-point Lagrange; additive/XOR/signed-diff 2-of-2 over all 32B
  pairs; 149-digit phase-3.2 sequence as bytes/sha/sums; sha256 of passphrase variants
  (tags, price-is-in-half, Matrix phrases, alpha, 3.2.2 output). 335 unique candidates,
  ALL NO MATCH on both funded gates (670 submissions), oracle self-tests OK before run.
- **Pubkey check:** JH body and BH slices are not secp256k1 curve points; the 64B/65B
  payloads are not (truncated) public keys.
- **2026 community status (web, 2026-09-12):** prize 1GSMG1JC... remains unclaimed;
  naddiseo dismisses every claimed internal solution (issues #97 prize-claim, #91
  "12 addresses", #108 CADEIA typo, #69 comprehensive solution with invented master key
  818af53d... - the certified key is a795de11...0735). Bitcointalk claims "Half & Better
  Half funded Feb 5 / spent Feb 15 2026"; my chain check of those two addresses shows only
  small dust movements, consistent with third-party noise, not a funded mechanism.
- **Status of the split branch:** 2-of-2 mystery-block split (late-37) AND all OP_RETURN
  split semantics (late-39) are now certified negatives. Both gates still only answer to
  the private key of 1GSMG1JC...; no derived material has ever matched.
- **Only remaining vectors that stay open:** (interpreter-alphabet line) the dbbib 69 /
  faed 570 VIC decode still needs the on-page keyed alphabet, the single unprovided
  input. The Beaufort 225B to E_B structural link (briefing vector 1) and the
  blocks[0..6]-as-AES-key idea (briefing vector 2) are now BOTH certified negatives on
  both funded gates (late-40). None of the OP_RETURN material opens either gate.

## Note 38  Beaufort 225B + blocks[0..6]-as-key vectors closed on both gates; full VtotheN fresh-vector family now certified on the Dualite gate (2026-09-12)

Brings the last two open briefing vectors of the 2026-05-26 brief to a certified end.

- **Beaufort 225B (vector 1).** The committed head (VtotheN/GSMG-PUZZLE-WORK derived/
  beaufort_225_head.bin) is 59cfc26c...d08d0c (32B), first byte 59 matching E_B[:2]=59cc
  only at byte 0. An independent clean base-9 reconstruction of phase3.2.txt[336:1990]
  (568 symbol tokens over the 9-symbol alphabet) reconstructs to a DIFFERENT head
  (01 64 36 cb...), so the two paths disagree and were swept as independent sources.
  Neither head, nor their XOR/reverse/slice/sha256 forms against K_B1/K_B2/K_H1/K_H2/
  half/better/xor_key/c4_pwd/E_B/E_H, opens either gate.
- **blocks[0..6] as key (vector 2).** c4 (1151B, sha256 e4269ed5...) and the 36 mystery
  blocks at c3[158:158+1152] (chain3 cosmic correct, sha256 4f7a1e4e..., first block ==
  K_B1) yield no key: cumulative/masked XOR over the high-entropy tails, block XORs,
  sha256(concat blocks 0..7), raw blocks, and 40 AES-256-CBC/AES-128-CBC decryptions of
  the block-7..34 and chain4[255:] regions under 5 key families x 4 IVs all negative;
  no decrypt ever carried PKCS7 padding plus printable ASCII.
- **Re-certification on the Dualite gate.** The VtotheN gsmg_fresh_vectors.py family
  (2026-05-25 session, 218+ candidate checks) was originally tested against the small gate
  only. The rebuilt family (316 unique candidates) is now a clean 316 x NO MATCH on the
  small gate and 316 x NO MATCH on the Dualite gate; oracle self-tests OK before both
  runs, zero stderr. This removes the one large family that had never been checked
  against the second funded address.
- **Bottom line:** tested.md late-40 closes the last two open briefing vectors. The
  only live open line remains the interpreter-alphabet crux: the a-i dbbib/faed streams
  ~ the keyed alphabet, untestable until the exact on-page interpreter key is recovered.
  The true password X of the published OpenSSL blobs remains unknown; prize and Dualite
  gates both still funded and unspent, no race on-chain.

## Note 39  cocert/vault Shamir semantics certified; t>=3 mystery-block cascade closed (2026-09-12)

The user pointed me at ~/cocert as a model for the puzzle's "step". Cocert's split/combine
step is a thin wrapper over hashicorp/vault/shamir (pkg/signed), which is now both READ
and executed on this device:

- Vault format (GF(2^8), generator 0xe5, one polynomial per byte, share = y-bytes then the
  x-coordinate as the LAST byte, x in 1..255 distinct, threshold = required shares) is
  byte-for-byte what our tools/shamir_combine.py x-last combiner implements. Live witness:
  vault v1.7.0 splits of b"cross-check-secret" (3-of-2 and 5-of-3) and of a random 32-byte
  key reconstruct exactly through combine_gf256. So the ledger's GF(2^8) rows were always
  running vault-exact math; late-41 records that certification.
- The late-37 gap (threshold 3 and up) is now closed: all C(36,3) triples x 4 x-layouts,
  C(36,4) quads x 2 layouts, and the all-36 sequential combine = 143,963 unique combined
  secrets, vault-faithful (duplicate/zero x subsets skipped; no t=36 byte-x combine exists
  because the trailing bytes repeat 0x3d and the first bytes repeat several values).
- Result: 0 of 143,963 combined secrets derive (00-pad or sha256 reading) to either funded
  gate, and 143,963 x NO MATCH on each oracle gate (287,926 submissions). The Shamir line
  over the mystery region is exhausted at thresholds 2, 3, 4 and 36 under the three x
  placement conventions every mainstream library uses.
- Interpretation: if the "half and better half" split is real, the combined private key is
  not recoverable from the mystery blocks, the OP_RETURNs, or the matrixsumlist halves
  under any tested split protocol; it lives behind the still-missing interpreter-alphabet
  step (the only live route) or is expressed in some non-shamir framing.

---
## Note 41 (2026-09-12): ECDSA-recovery closed as a reading of every long decrypted file; new-repo audit found nothing; rockyou splits identified and dualite-infeasible

1. ECDSA/window closure (extends tested.md late-43): sliding 64B windows over the full
   decrypted chain3 (1264 windows) and chain4 (1088 windows), each read as r||s and s||r,
   public-key-recovered under recid 0..3 against messages GSMGJH/GSMGBH/"IMGINE A 6 DIGIT
   FOR THE KEYS"/"price is in half"/GSMG.io/"yourwillpower"/"visit the seph" and their
   sha256s: 0 matches (coincurve/libsecp256k1, positive-control-verified). No 64B region of
   either chain is a recoverable ECDSA signature over plausible committed text. Mystery 36
   blocks could not be pairwise-shared-key-tested in this session (myst_blocks.bin is not
   saved; block scalars only live in memory during the cascade script), so add that only if
   the blocks are re-materialized.
2. Community audit for NEW information since the last sweep: pinned repo is
   puzzlehunt/gsmgio-5btc-puzzle (Aug 2023). Two newer repos surfaced: nineeeai-ux
   (2026, README only, no content) and mkno03/GSMG-5BTC-Crypto-Puzzle-Solver (Apr 2025;
   analysis reports are Turkish LLM-slop rediscovering the already-known matrixsumlist
   binary reading and the "b as separator" grouping, plus an unfounded parkour "5" claim;
   no new certified parameter). Nothing new to consume.
3. Identification gap closed: briefcase/chunk_00..07 (8 x ~17.5MB) are rockyou-split
   passphrase dictionaries (14,283,386 lines total, first lines match rockyou). They are
   NOT the row-128 1,181,466-candidate sha3 phrase set and are NOT stored in any
   dualite-enumerated form; at the dualite gate's measured ~353 cand/s any full rerun is
   ~11h and is not scheduled. The dualite gate remains brute-force-incomplete for: (a) the
   #####-deleted/lost large phrase files (row 119-128 sets), and (b) any rockyou-level
   dictionary; every locally present, bounded candidate list is now dualite-certified.
   Date: 2026-09-12.

## Note 42 (2026-09-12): live /puzzle image closed as a seed bearer (LSB/QR/14x14 matrix all negative) + gsmg101adressapril battery made Dualite-complete

User pushed "the seed is planted in puzzle.png", so the CURRENT gsmg.io/puzzle asset
(1048x1556 RGBA) got the full machine-extraction pass rather than trusting the community
spiral claim. Results in late-44: low-bit planes are noise in all three color orders; the
strict 75px lattice over the top-left 975x975 yields a balanced-but-opaque 14x14 bit
matrix that no traversal reproduces "gsmg.io/theseedisplanted" with; and QR finder
template correlation peaks far below the finder threshold. The claim originates from the
2017 ImageMatrix render, whose terminal output is already the tested-negative phase-2
blob. Residual (untouched) vectors: the row-128, 1,181,466-candidate phrase sets remain
dualite-unverified only because the files no longer exist locally and the gate's ~353
cand/s makes a networked rerun an 11h+ undertaking; dust-ping monitoring remains armed
via ~/briefcase/dust_watch.py in case the author ever funds a hint block.
   Date: 2026-09-12.

## Note 43 (2026-09-12): original repo assets pulled; puzzle.png matrix authoritative; blue/yellow-position and color-channel readings negative

Fetched the original assets (and the 28,936-byte solution README) from the pinned solver
repo directly. The 14x14 matrix in the live image calibrates at x0=0,y0=0,pitch 74 with
100% agreement to the community transcription, and the CCW spiral from the upper left
reproduces gsmg.io/theseedisplanted byte-exactly; the 4 leftover center bits are 0000.
The "Yellow/Blue has a number" position reading (15 blue + 9 yellow spiral indices) was
joined 16 ways and swept on both gates = ALL NO MATCH (late-45). "Roses are White but
often Red" has no red-tinted cell in the modern asset; the only red is the decorative
banner stripe in the page art below the matrix. The image holds exactly the documented
URL and nothing more. The author's intended end-state per the README remains: fund the
half and better-half keys with dust ("they also need funds to live").
   Date: 2026-09-12.

## 2026-09-13 (session 3) addendum  -  on-chain funding tree, sibling vanity, JEDYY noise

Gate-pair structure (all via mempool.space, no oracle change):
1. G1 1GSMG1JC9 was CREATED with exactly 5.0 BTC at block 571497 (tx 73e48ff5), from mining wallet
   1EtbTvVB8QTGN4mduSdy7n4cZQm4iYTpQ1; no OP_RETURN. G1 is therefore a 2019-era escrow.
2. At block 630001 (first block after the 2020 halving) tx 2aa9a4a9 spent 73e48ff5:1 (500M) + 666 (JEDYY dust,
   tx a2d2481d blk 622713) + 700 (tx a798905f blk 630001, which carries OP_RETURN "Halving") ->
   OUT0 249,815,966 -> G1, OUT1 250,000,000 -> G2 17ucy. Both current gates are DIRECTLY paired in one tx.
3. The 666-sat "beast" dust is actually JEDYY's signature trolling (their 2020 OP_RETURN series sends 666
   to many addresses; "JEDY / --JEDYY" signoffs). Not a gsmg-author 666 clue. The 700 coin and "Halving"
   OP_RETURN also from the same halving-era self-noise. The real gsmg messaging layer is the
   145ZQ9...+1JG648yaB7 dust-spray spiral (secondanswer/...matrixsumlistpassword) documented previously.
4. Sibling vanity 1GSMG1CLxGXuFtnKbwh1QWfp4xA6reAet3 (0.0135 BTC, funded 2017/2024/2025, ALL unspent) and
   block 913830 mass-ping (G1+G2+sibling+1BEN1x8p/1BEN1Kdr/1HansB1D2/1Jorik1e)  -  creator vanity-family &
   attention-dust; NOT escrow. Kept for reference; not worth a sweep.
5. JEDYY BIP39 seed "proof rack sausage sick couch pyramid domain final tiny custom obscure kingdom"
   (block 620205 OP_RETURN) is valid but derives no path to G1/G2/sibling  -  separate 0x420024/btckeygen.com
   puzzle. CLOSED as noise.
6. Abacus region-sums as X (176 forms incl. 140/264/117/381/1182/666 & word-number joins) through both
   blobs x both password modes x both digests: NEGATIVE, certified (tested.md session-3).
Lead 0 (dbbib/faed interpreter) rank unchanged; the on-chain twin-funding reinforces a single-seed
derivation but adds no new cipher material.

2026-09-13 (session 3) final addendum  -  WITNESS payloads: block-949653 txs 808f812f ("GSMGJH"+0x20+64B) and
22381b60 ("GSMGBH"+0x1f+64B), labeled by blk-949664 as "GSMG WITNESS", fail ECDSA pubkey-recovery over 70
plausible z combos and show no nonce reuse (tested.md session-3 rows). Treated as opaque commitment; the
"GSMGJH/GSMGBH" tags may be vanity initials (J.H./B.H.) or a hash-family tag. If the OPRETURN is meant as a
self-signature, the message hash (z) is the unknown  -  a candidate only if a ledger/README string matching a
recovered pubkey appears later. Ranked below Lead 0.

2026-09-13 (session 4) addendum  -  WITNESS closed (certified): tx 808f812f's scriptSig proves the chain source
address 1GSMG9VD (pubkey 04d3b822...770ac)  -  a self-witness, unrelated to blob keys K1/K2. Nonce-reuse sweep of the
whole chain (29 sigs, 9+20 by two distinct keys) = 0 collisions; corrected 32B payload halves fail as private keys
and as ECDSA (r,s) over a 113-256 candidate message-hash universe vs K1/K2/witness/consolidation pubkeys. No leak,
no signed message, no commitment key recovered. WORK DONE. The 64B OPRETURN stays "opaque commitment".
NEXT: Lead 0 (dbbib/faed keyed-alphabet)  -  needs a specific construction premise for a decisive sweep.

2026-09-13 (session 4): Lead-0 broad fresh sweep NEGATIVE (tested.md session-4 row): double-Bifid(2-92) on the
570 plaintext, columnar transpose of faed by dbbib_91/69 matrix sums, abacus pair/triple sums, dbbib full-period
Bifid + marker drops, even-stream position-selector gating, keyed Vigenere/Beaufort on the plaintext, and direct
object-scalars vs G1 pubkey all = no signal. G1 pubkey now known (04f4d1bb..., from spend tx 88cdb3cd). Lead 0
remains: certified Bifid output is real but its semantics (beyond "BTCSEED" label) unexplained; even-channel gating
and "our first hint is your last command" are the two live structural threads. New info (esp. a hint) most valuable.

---
## 2026-09-14 (community sync) addendum  -  issue #111 retraction arc, 2026 official hints, Phase-0 colour tautology closed

Sync against the current live community surface: the puzzlehunt tracker and the Naddiseo
curated-fork mirrors (both fetched 2026-09-14). Prize unchanged, no valid claim anywhere;
the community is stopped at exactly our Lead 0.

1. **Issue #111 (0xyph3r 2026-09-05, closed)  -  the "Reduction(SOURCE_4)" edge is author-retracted.** Its
   full 4-comment arc: posted FH = gros[0::4][:16] XOR gros[1145:1161] and BetterHalf =
   Reduction(SOURCE_4) XOR gros[1161:1177] against G1's H160 a9553269...; Naddiseo rebutted on the
   #55 verifiability criterion (no verifiable output structure = indistinguishable from failure);
   0xyph3r then retracted BOTH items with an entropy table (gros 2432B = 7.92-bit / longest ASCII
   run 8; 1327B blob 7.87 / 7; chain4 7.84 / 6 = noise, vs Phase-3/3.2 plaintexts 6.06/292 and
   5.78/332 = readable) and withdrew the "Reduction" block as "very likely a phantom, and a lot of
   compute has been spent on it". Net: nothing new for either gate; the gros/dualite branch remains
   a false-positive reading exactly as our rows already concluded, and the only community-open
   questions left in the thread (p32 inner-blob password, colour-cell payload) map onto known items.
   Their VIC re-derivation (board FUBCDORA.LETHINGKYMVPS.JQZXW, escapes 1,4, 149-digit stream ->
   INCASEYOU...NEEDFUNDSTOLIVE) and p32 blob identity (b45a5e3d...) are already certified in this
   folder; nothing new to test.
2. **Phase-0 24-colour-cell mystery CLOSED as a tautology (community, verified against README matrix).**
   0xyph3r's "CW spiral ≡5 mod 8" was the wrong direction; counter-clockwise from upper-left the 24
   coloured cells land on indices 7,15,23...191 = bit 7 (LSB) of each of the 24 characters of
   `gsmg.io/theseedisplanted`. Colours are decorative and redundant with the LSB they encode  -  they
   carry no payload. This retires the "blue/yellow positions" open thread of Note 43. The single
   off-white RGB (254,254,254) cell at row 7, col 4 (spiral 177) remains the only unexplained grid
   cell and is possibly a red herring; no password connection shown.
3. **Two new official hints not previously in this folder (from the Naddiseo mirror, both interpretive, not executable):**
   - 2026-01-01: "Happy new year! Make the best of everything. Oh, and here's a 'tiny hint' <3."
     "<3" = literally less-than-three: numbers < 3 -> stream values {a,b,c}/0,1,2 and/or "tiny" = the
     small blob. Candidate, unformed; not yet a testable premise.
   - 2026-07-12: "@Jrk Bgrk  -  My close friends have the best chance of solving it (a few tried). But
     they don't have the skills some of you do. NOTE: that is a hint." Suggests the crux uses
     something personal/social (creator's inner circle), or that some trail is not public. Unformed.
4. **Operational: the puzzlehunt tracker is community-developed and abandoned (#105)  -  the creator
   does not answer there.** Mirror state: Naddiseo/gsmgio-5btc-puzzle pushed 2026-09-05, full
   walkthrough through Phase 3.2 + SalPhaseIon (their SalPhaseIon section ends at
   "everything else hasn't been solved" = our dbbib/faed Lead 0 exactly), Cosmic Duality unsolved.
   No community solver is past our frontier.

Ranking: Lead 0 unchanged and still the only real path; the two 2026 hints are the only new raw
material and are worth holding as interpretive threads ("<3" -> values below 3 / tiny -> small blob;
"close friends" -> crucible hint). Date: 2026-09-14.

### Follow-up (same day): Naddiseo notebook/unverified scan  -  no content beyond the walkthrough

Cloned the mirror (shallow) and read all cell sources: phase0.ipynb (14x14 b/y unroll only),
phase3.2.ipynb (ends exactly at the p32 inner AES `U2FsdGVkX1+0Wl49...`, "has not been solved"),
salphaseion.ipynb (agda/cfob z-section decode via a=1.. / o=0 hex; ends at "Remaining sections"
= dbbib/faed, unsolved), decentraland.ipynb (audio inversal only). Nothing reaches past Lead 0.
`unverified/` adds two items already covered here: the 23/16/7 "1141 slice" (research note 23)
and a FEFEFE hex-digit parity reading (FEFEFE->101010->42, #FFF200->111000, #3F48CC->110000)
which the author of that note himself tags as "thematically apt and nothing more"; the "104"
half contradicts our note record (off-white cell sits at (7,4) spiral 163/177 by indexing).
Conclusion: Lead 0 unchanged; spent nothing further. Date: 2026-09-14.

## Note 44 (2026-09-14): live-site forensics closed  -  no live gate exists; Alician-phrase VIC battery negative (row 205)

1. **Live gsmg.io has no verification door.** `Hello :-)` + 404 is the server's default for every
   nonexistent path (`/phase1verification`, `/validate`, `/secret`, `/admin`, ... all
   byte-identical catch-all). The `/phase1verification` form is a decoy: GET==POST==same 9-byte
   body, flat timing 1.33-1.42s vs 1.41-1.83s baseline GET  -  no password branch. Only 4 real
   pages: `/`, `/puzzle`, `/theseedisplanted`, `/robots.txt`. The `/` terminal animates the
   true phase-1 14x14 matrix (`finalGrid` inlined): 101 ones/95 zeros, all 15 blue on 1-bit,
   all 9 yellow on 0-bit, 86/86 black/white  -  verified byte-identical to the documented read
   (CCW spiral from top-left, MSB-first, 8-bit ASCII reproduces `gsmg.io/theseedisplanted`
   exactly). Current site = memorial/rebuilt landing replaying the known phase-1 material; no
   gate, no oracle, no hidden endpoint. Escrows still funded/unspent (small 875988872 fund /
   750353498 spent; Dualite 375055856 fund / 0 spent) so the offline crux remains live.
2. **Alician phrase `white rabbit nostalgic alice childhood`  -  no match in any single-application
   form.** sha256-slug preimage variants: 0 of 7 open slugs. Keyed-28 VIC feedstock over
   dbbib/faed: 22 alphabets -> 1,760 clean decodes; full-splice 1,300 alphabets -> 97,884
   decodes; 0 MATCH on small gate, 0 MATCH on Dualite; top English-scored decodes are noise.
   This was the one literal keyword family never applied to the certified streams; now closed
   (tested.md row 205, both sweeps + certified_vic selftest witness PASS).
3. **Lead-0 interpretation unchanged.** dbbib/faed are not a one-step VIC checkerboard under any
   documented keyword family (all rows 140-205). Note 25d framing (intermediate of a layered
   ~16-encryption chain woven with ~7 passwords + prime-basics step) remains the standing model;
   the phrase is best held as ONE candidate password inside that layered construction (its only
   verified role so far), and the recovered stage passwords the chain's other members  -  their
   co-sweep in joint/ordered constructions over dbbib+faed is the next available move.

Ranking: Lead 0 (dbbib/faed interpreter-alphabet / layered chain) still THE crx; Note-25d
layered co-sweep is the highest-ranked testable next step; site forensics (route-2) closed.
Date: 2026-09-14.

## Note 45 (2026-09-14): Note-25d layered co-sweep (phrase x recovered passwords) closed negative (row 205E)

The highest-ranked testable next move from Note 44 was realized: the Alician phrase joined
with each of the 10 recovered stage passwords (both orders) as keyed-28 checkerboard
alphabets over dbbib/faed, 504 alphabets x CANON/POS x 16 escape pairs = 24,353 clean decodes,
ALL tested against both funded gates (counted 24,353 NO MATCH per gate; oracle selftests PASS
on both -- witness re-run this session). All top-English decodes are consonant-heavy noise.
This was the first concrete act on Note 25d's "layered construction" premise using the phrase
as one member of a join; it returns negative without shrinking the premise (a 2-keyword join
is far from all done). Lead 0 unchanged: the interpreter-alphabet/layered crux stands, now
with phrase-only, phrase-as-single-VIC-keyword, phrase+password-join, and phrase-sha256-slug
families all exhaustively negative.

Ranking: Lead 0 unchanged. Next-best testable acts, in order: (1) phrase x password joins in
the REVERSE pipeline direction -- use the password stream's own decodes (the year's worth of
joint_sweep/lead0 candidates) rather than phrase-only as the second stream half; (2) expand
the (E) splice set beyond the 6 tested pairs to all 26x26 on the joint seeds only (cheap);
(3) on-chain author-revisit is closed; site forensics closed (row 205 A/B). Date: 2026-09-14.

## Note 46 (2026-09-14): full-splice and reverse-pipeline branches of Note 45 also closed (row 205 F,G)

Executed both remaining ranked moves from Note 45:
1. (F) Full 26x26 splice expansion on the joint phrase+password alphabets: 5,850 alphabets,
   32,111 clean decodes, ALL oracle-tested both gates, 0 MATCH. The phrase is not a keyed
   alphabet with any recovered password at ANY punctuation splice position.
2. (G) Reverse pipeline: phrase joined (both orders, 8 separators, case variants) with the
   three certified prior decodes (3.2.2 VIC plaintext, faed-Bifid head, dbbib-Bifid output)
   as composing an answer X: 228 candidates, 0 MATCH both gates. The phrase does not combine
   with a verified decode into a gate-opening X.
Row 205 now spans the full Alician battery: site forensics (A/B), pure-phrase VIC (C),
sha256-slug (D), joint-password alphabets (E), full splice (F), reverse pipeline (G), pipeline
witness reruns (H). Lead 0 (dbbib/faed interpreter-alphabet / layered chain) unchanged: the
phrase is fully exhausted as a keyword, a join-component, and a slug.
Remaining unexplored (ranked): (1) the phrase as a TRANSPOSITION key (columnar width =
phrase length) or over-encryption key inside the certified VIC pipeline on faed -- a distinct
layer from the alphabet; (2) phrase-lengthed columnar undo on the raw streams before any VIC
decode; (3) holding the phrase for a future premise correction (only the human can supply new
phrase variants, e.g. different word order from re-OCR). Date: 2026-09-14.

## Note 47 (2026-09-14): transposition/OE layer closed -- full Alician battery summary

1. (F) Full 26x26 splice on joint phrase+password alphabets: 32,111 clean decodes, 0 MATCH
   both gates.
2. (G) Reverse pipeline: phrase joined with three certified prior decodes (3.2.2 VIC
   plaintext, faed-Bifid head, dbbib-Bifid output): 228 candidates, 0 MATCH both gates.
3. (I) Phrase as transposition-width + over-encryption key layer in the certified VIC
   pipeline (six phrase variants x 24 OE keys, both OE and plain-transpose modes): 1,678
   clean decodes, 0 MATCH both gates.
Grand total this session: 157,930 certified negatives (A-I) against both gates, pipeline
witnesses re-run PASS.

Lead 0 unchanged. The Alician phrase is now exhaustively exhausted as: checkerboard keyword,
sha256 slug preimage, joint password joiner, reverse-decode joiner, and transposition/OE-key
layer. No variant of the phrase opens either gate in any certified-eligible pipeline form.

What remains: the puzzle's answer X still lies within the ~16-encryption layered chain (Note
25d). The phrase is one of the 7 passwords feeding that chain (its only verified role so far),
but is NOT the final answer X in any of its literal, joined, or layered constructions tested.
The true layered construction may involve: (a) different word ordering of the 5 phrase words
only supplyable via a corrected OCR of the original form, (b) the phrase used as a meta-key
deriving one of the intermediate alphabets/keys in a way not captured by the keyed28 model,
(c) a one-time pad where the phrase is the only key material and the ciphertext is not
dbbib/faed but one of the intermediate blobs (b45a5e3d, etc.), or (d) a non-VIC/non-classical
encoding of the 14x14 matrix whose low bits encode something beyond gsmg.io/theseedisplanted
(a possibility noted since the spiral yields 24 cf bytes with 4 unused cells).

The human retains the option of re-supplying the phrase with a different word order or with
an exact original transcription correction. Without that, the phrase branch is closed. Lead
0 still THE crux. Date: 2026-09-14.

## LEAD 15 - ON-CHAIN DUST STRUCTURES: recurrence of sats-values 4460 leaf / 4690 step / 13370 (=13.37 leet) (2026-09-15)

- REOPENED via live blockstream (after network came back): sibling-vanity 1GSMG1CL dust TXOs deep-traced.
  1) 6400-sat UTXO created by 3775e974 (b913830), a FAMILY DUST-DISTRIBUTION tx paying in ONE tx: 1BEN1x8p.. 1030, small gate 1GSMG1JC9 1070, 1BEN1Kdr 1100, 1HansB1D2 4900, sibling 6400, dualite gate 17ucy 9500, 1Jorik1e 9500, escrow funder 1EtbTv 13370, new bc1436me.. 34010. Its input feeds a ~39+-hop dust-ladder ending at b891717 (~0.9M sats): each hop sheds EXACTLY 4460 sats to a fresh 1-time P2PKH leaf and steps backward by exactly 4690 (=4460+fee). Leaves are all 2-tx addresses funded 4460 only. Nobody ever spends the 4460; all balance dust.
  2) 4534-sat UTXO traced to 2017-era consolidation web via bc1n7hvu aggregator - generic churn, dead end.
- WHY IT MATTERS: the puzzle values 13.37 leet (13370 sat exit + 1337000 in gsmg-era art) and the avenue pattern "salty salt small" use structured sats as data. 4460 (leaves), 4690 (step) are new integers never suggested in repo. 4690 = 7*670; 4460 = 44.6 -> "4460" reads 'DD'@? candidate cypher/chess/sat-values.
- NEW ADDRESS FAMILY to sweep: bc1436me2xr9fsp2d9vmvqrhqhcmxff2qwq2jvlr5 (34,010, totally unspent, 1 tx) - segment 34010, P2WPKH h160 ac75bca8c32a601534acdb003b82f8d9929501c0. 34010 = 3-4010? 4010 ~ ASCCUt? Also 'n7hvu'/'csa5v' var prefixes appear in ladder - contain hex-nibble data.
- NEXT: (a) oracle 4460/4690/44604690/34010/340104460/13.37 string expansions as X on both gates; (b) dump all ladder leaf addresses (n=~39) and all family-distribution output addrs (n=9) to a kept file; (c) mine the 34,010 recipient's redeem/h160 for pattern (not hex-ascii, checked).
- STATUS: open, informative-only (no X candidate yet bankable; dust-ledger not the blob gate).

## LEAD 16 - KDF-library audit thread (2026-09-16): all five steered repos no-fit; ESAPI substring mild-positive, KDF/HKDF below-noise; book-cipher digit-layout negative

- Steering: user fed repos esapi-java (ESAPI KeyDerivationFunction), terrapane/libkdf, smuellerDD/leancrypto kdf/api/lc_hkdf.h, xianghuzhao/kdfcrypt, chrisveness/scrypt-kdf. All are generic KDF libraries (SP800-108 counter-mode / ACKDF / RFC5869 HKDF / Go argon2-scrypt-pbkdf2-hkdf / JS OpenSSL-scrypt). None can be the Salted__ EVP_BytesToKey blob KDF (ACKDF 32-byte-only; others not password-string or not Salted__). Verdict: THEMATIC (the author-name/crypto-library concept), not artifacts.
- Stats verdict on candidate files: ESAPI only token > noise (4.6x lines / ~6.4x occ, explained largely by ESAP 2.1x + SAPI 1.7x transition bias); KDF 0.65x, HKDF 0.67x (below expectation), ACKDF 1.25x noise, PBKDF/scrypt/argon/bcrypt/kdfcrypt absent. Reading: no embedded KDF-name clue; coincidence.
- Book cipher: 271 triplets -> 975 base-9 digits; faed(570)/dbbib(91) do not occur at any offset in either direction; subfield reads (line/char/len/char||len) also don't fit the stream lengths/shapes. Closed negative for this positional rule.
- STATUS: crux unchanged; KDF-name decode-candidates do NOT warrant an oracle run (below-noise / absence); book-cipher digit-layout reading closed.
- 2026-09-17 USER-ADJUDICATED RED HERRING (tested.md late-137): the whole Warning/Beaufort book-cipher chain (Warning=Logic 21-letter key doc, Beaufort monologue in obfusee, Alice books as key documents) is RELEGATED. Extended the late-96b digit-layout test to the five un-ledgered in-book encodes (warning/beaufort into wonderland/lookingglass/alicepair; 3732 triplets total): ZERO window/prefix match of dbbib_91/faed_570 in any direction or subfield; witness = warning_in_beaufort re-negative reproduces late-96b. Not a live lead; do not re-chase without a new positional rule or key-document text from the user.

## LEAD 17 - XORSTR repo audit (2026-09-17): compile-time-XOR string obfuscator; its faithful key-schedule family swept  -  NO-FIT, all decodes binary noise

- Steering: user fed https://github.com/JustasMasiulis/xorstr (C++17 header, ~242 lines). Mechanism audited end-to-end: per-string keys key8(S) = (FNV-1a(2166136261+S, __TIME__, prime 16777619) << 32) | FNV-1a(FNV-1a(...)); string stored as 16-byte blocks XORed with that 64-bit key; decrypt = identical XOR (symmetric).
- WHY IT LOOKED RELEVANT: FNV multiplier 16777619 is PRIME -> in-corpus author hint "primes important"; and prior FNV sweeps only ever used FNV output as the literal hash == X, never as a repeating-key XOR decryptor on dbbib/faed under xorstr's exact schedule.
- SWEEP (new mechanical family, tested.md late-144): 25 in-corpus keywords/assemblies as the __TIME__ source x 3 digit maps (DBIFHCEG canonical a=8..i=2 / pos1 / pos0) x 3 key derivations (key8-blockwise / key4-repeat / key8-repeat) x both streams (dbbib_91, faed_570 minus z) x output forms (hex/revhex/latin1/rev/lower). N=2306 unique, both gates --stdin: 2306 NO MATCH / 0 MATCH each (witness selftests PASS prior; single-line-safe regen). ZERO of 2306 decodes even resemble text -> streams are not xorstr-style XOR ciphertext.
- VERDICT: THEMATIC NO-FIT. xorstr is a binary-string-hiding obfuscation, its ciphertext is arbitrary bytes  -  the {a..i}-constrained streams cannot be its output, and neither interpretation yields X. Do not re-chase. Crux (lead 0, interpreter alphabet) unchanged.

## Note 34 (2026-09-20): byte-exact provenance of the small-blob gate chain, re-derived from a fresh decode of the 2023-06-01 archive textarea

Previous provenance steps (Notes 32/30, tested.md row 193) used the stored primaries
`data/live_salphaseion.html` and the live 2026 fetch. This pass re-extracted the textarea
of the byte-exact 2023-06-01 Wayback capture independently (zstd-decompressed, tokenized
per single character  -  the textarea is one space-separated char-per-token stream) and
re-derived every node of the funded-gate chain directly from those bytes:

- `dbbib` run: 91 tokens, byte-identical to the canonical `dbbib_91` (22-token middle run
  `bfdhbeffcdbbfcccgbfbeeg` at tokens 45-67 INCLUSIVE). Third independent primary for Note
  32's reversal.
- a/b run 1 (tokens 94-197, 104 chips): `a`/`b` only; a=0, b=1, 8 bits/byte decodes to
  **`matrixsumlist`**  -  now VERIFIED from the bytes, not asserted.
- `faed` run: 570 tokens, starts `faedggeedfcbdabhhggcadcfeddg...`, letter counts
  g107 e68 i75 h58 f56 c52 a55 b49 d49; `z` terminator at token 765; z-segments 63 + 29
  (contain `o`). All match the stored model exactly.
- phrase `shabef our first hint is your last command` verbatim; tail `shabef anstoo`.
- THE SMALL BLOB IS ON THE ORIGINAL PAGE, PRINTED SPLIT: the textarea shows
  `U2FsdGVkX18...+...fvdrd9z` then the a/b run 2 (40 chips) then `QvX0...N/jJ`. Joining the
  two base64 pieces AND dropping the embedded run 2 yields EXACTLY the published 128-char
  `BLOB_B64` (96 bytes: `Salted__` + salt `3ab585348552415d` + 80 ciphertext), byte-for-byte.
  Run 2 with the same a/b decode reads **`enter`**  -  VERIFIED, closing the last asserted
  token of `RAW_PW` (`matrixsumlist + enter + lastwordsbeforearchichoice + thispassword +
  matrixsumlist`).
- No dualite/Cosmic-Duality blob is in the 2023 textarea (it lives in the page's visible
  "Cosmic Duality" section and is a separate element); no divergence from the live page.

Closed: every byte feeding the gate password and `BLOB_B64` is now date-pinned 2023-06-01
and verified from an independent decode. oracle.py Part 4 certifies this provenance in the
self-test. OPEN and unchanged: the funded-gate key reduction from the `B1_79B.bin` fields
(sha256/first32/last32 family) to `1GSMG1JC9...` (1.2563451 BTC). Date: 2026-09-20.

### Lead 9 correction, 2026-09-27 (`R-SLUGF971`, `R-CDXFULL`)

**Open slugs: 1, not 7 - and its existence is unconfirmed.** `f9719d6d` is not a
post preimage at all: it equals `sha256(raw 32 bytes of 89727c59)`, verified with
`sha256sum`. So the count of unexplained 64-hex slugs is down to `673e3b1a` alone, and
that one has **no preimage**, so whether a post ever existed at that path is
unconfirmed - the archived body is the SPA catch-all, byte-identical (modulo the
csrf-token meta) to two other paths', and live `/f9719d6d` is 404. The five recovered
preimages are on firmer ground precisely because a real authorial phrase hashing to the
recorded slug confirms both the law and the post.

**Re-score: terminal, not low-priority.** The premise of this lead was "a new
transcription of stage wording is also a batch of preimage candidates". That premise is
now spent - phase-1, phase-2, phase-3 and phase-3.2 wording are all exhausted, and
`R-CDXFULL` closes the other supply route by showing the **entire** 620-urlkey CDX
surface is already in the corpus, so no archive can yield an unmined post. Any further
preimage would have to come from a pixel-only string this folder does not hold, i.e.
from direction (b), not from more transcription.

**Standing lesson worth carrying to the other leads (it has now fired three times:**
`R-SOLVERGRP-IMG`, the two retracted `R-JRK8446` findings, and now `f9719d6d`):** before
promoting an authorial artefact, ask what in *our own tooling* could have produced the
pattern. In this case `tools/decodekey_vic.py:39` had already computed the exact value
and listed it as a decode-key target, so any sweep that requested the path put it in the
index. A 2^-256 coincidence is exactly what a self-fulfilling generator looks like.

Status 2026-09-02: the literal reading is closed. Every window of up to 20 words,
every suffix and prefix, of every text the solver holds, including the Architect scene
of the film and the transcripts of the three films up to 15 words, is negative as the
password of both locks under 7 forms and 2 key derivations (`analysis/tested.md`
section 15b). The phase 1 image's text is transcribed and tested too (section 19b). What
survives is a non-literal reading of the two directives.
Cost: an insight, not a sweep.

## Note 35 (2026-09-27): the "read the 29 dropped letters as their own message" lead is DEAD, not open; the merge had resurrected it

The origin/main merge brought in a ranked lead, "read the 29 dropped letters as their
own message", whose own stated kill criterion is "killed by exhausting the small set of
reasonable reading orders". That criterion has been met three separate times, in
`analysis/tested.md` entries dated well after the lead was written:

- section 60: the direct binary->ascii of `OOIIOOOIIOOIOIIOIOOOOIOIIOIOI` is garbage.
- section 81 (2026-09-01): the drop token tested directly as the answer X against the
  funded gate `1GSMG1JC9`, raw plus both polarities = NO MATCH over 5 attempts, with
  the oracle self-test passing immediately before. "As a standalone X it does not open
  the gate." The entry also names this as a research-correction already recorded in
  `leads.md`: the I/O string is the drop-mask record, not a payload.
- the 2026-09-05 letter-suppression derivation: removing every I and O from
  `odd_pre_reduction` yields `object_256` exactly, so `dropped_29` is the suppression
  set re-encoded as redundant 29-bit binary, and its binary content "is not itself a
  message". That entry closes the "29" ambiguity outright.

Dating settles which side is stale. The lead entered the README in `e924aa3` on
2026-08-16, the repository's opening "open source my research" commit, and has sat
untouched since. The exhaustion result is dated 2026-09-01 and 2026-09-05. So this is
not a conflict between two live hypotheses: it is a lead whose kill condition was met a
month later, and the merge had re-listed it as open directly beneath our own lead 8,
which states the same conclusion ("standalone readings are exhausted with no legible
fragment, so the open question is what they select or gate").

Removed from the ranked list in `README.md` and from `puzzle.json`. The surviving
question is not the letters read alone but what the 29 bits select or gate, possibly
combined with the even stream, which is what lead 8 now says on its own.

Status 2026-09-27: closed as a standalone-message route. If a future pass wants to
revive it, it has to say what reading order the three existing negatives did not cover.

- `LEAD0_FINDINGS_2026-09-28.md` (briefcase root, 175 lines) was an unrecorded Lead 0 note
  from a session that found the worktree busy. It is now in the ledger as `R-LEAD0-STAGED`. The
  one durable fact: all four captures of the page are byte-identical, zero drift 2020->2026, so
  the below-fold 21% of textarea 1 is already on disk in the HTML and the `anstoo` human-read
  item needs no image. Its own `anstoo` character offset was wrong (spaced, not contiguous) and
  its three CLEAN renders are absent from disk, so its measurements are probable, not certified.

- The `theseedisplanted` human-glyph item is CLOSED from pixels (`R-STRIPGLYPH`): `ca` is a plain
  `C` with no circumflex, the disputed narrow run is a 1px vertical rule (layout furniture, not a
  letter), and `lock` is a padlock ICON with `LO` beneath it rather than a glyph row, so
  `1ock` was never on the table. The strips are two-tone white-on-colour at 82x70 and are
  legible as bitmaps without a human. One human-eye item remains: the 14x14 FEFEFE cell.

- The last human-eye item is CLOSED (`R-GRID14`): cell (7,4) of the 14x14 grid is RED, the only
  red cell in the grid, and the "FEFEFE cell" is a white-outlined nest glyph drawn on it - a
  45x45 `#FFFFFF` ring with a small field-coloured void, not a cell colour and not a letter. The
  grid field is `#F5F5F5` and the grey is image border, not a cell value. No human, no image
  modality. Zero human-eye items remain open; the "needs eyes" class is now empty.

- The corpus is INTACT (`R-POINTERS`): all 33 `~/briefcase` pointers in the analysis docs
  resolve, so no live negative rests on a missing file. Two roots exist (`~/briefcase` is
  canonical, `storage/external/briefcase` holds solver-side and image material) and they are
  NOT the same tree - searching the wrong one produces a confident false negative, which is
  what I did and then caught with a positive control.
