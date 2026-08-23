# Tested hypotheses, full ledger

Summary table is in the README. This file has the full detail behind each row. All
counts and witness claims below are re-read from the private research folder's own
established-facts register before being written here. A review on 2026-07-28 found
that an appearance-based acceptance filter used in about 46% of the folder's scripts
(98 of 213) had been silently rejecting the correct answer shape for years, because
it required decrypted plaintext to look like printable ASCII when the expected
plaintext is raw key material. The negatives below post-date that fix: nothing here
judges a candidate on how it looks, only on whether it reproduces the target address
exactly.

## 1. Letter-to-bit mask reduction of the 256-symbol object

The final odd-position stream of the puzzle's own Bifid decoding step reduces, after
removing the two Base58-ambiguous letters I and O, to exactly 256 symbols drawn from
a 23-letter alphabet. The most direct hypothesis is that each symbol maps to one bit
of a 256-bit key.

Method: every letter-to-bit mask, tested both in linear reading order and under 20
spatial reading orders (row-major, column-major, spiral, boustrophedon, and their
reverses).

Result: 335,000,000 submissions, 0 match. Witness: yes, two independent
implementations reproduced the same negative and an injected known-good object was
correctly flagged by both. Date: 2026-07-28.

## 2. 16+7 partitions of the 256-symbol object's alphabet

Hypothesis: the 23-letter alphabet splits into a 16-letter and a 7-letter group
(echoing "23 individuals, 16 female, 7 male" from the source text the final page's
prose is adapted from), each group indexing a different half of the key.

Method: all 245,157 possible 16+7 partitions of a 23-symbol alphabet, both
polarities.

Result: 490,314 submissions (245,157 x 2), 0 match. Witness: yes, autotest by
injecting a known-good partition into the same code path. Date: 2026-07-28.

## 3. The 32 target numbers as ASCII codes of a substring

Hypothesis: the 32 numbers the final gate expects are the ASCII codes of 32
consecutive characters taken from one of the puzzle's known decoded objects.

Method: 10 candidate source objects x 2 letter cases x 2 reading directions x every
window of 32 consecutive characters x 2 value conventions (direct ASCII, or the
letter's rank in the reduced alphabet).

Result: 34,000 candidates, 0 match. Witness: yes. Date: 2026-07-28.

## 4. The 256-symbol object read as a single Base58 number

Hypothesis: the object, or the string it derives from, is a private key written
directly in Base58 (matching the object's own alphabet, which happens to exclude
the two Base58-ambiguous letters I and O).

Method: windows of 43, 44 and 45 characters (the length of a Base58-encoded 32-byte
value), every position, both reading directions, 2 extraction conventions, plus the
object read whole.

Result: 17,304 candidates, 0 match. Witness: yes. Date: 2026-07-28.

## 5. A substring of the object is Base58 to decode

A related but distinct hypothesis: some substring of the 256-symbol object, or of
the 570-character string it derives from with I and O removed, is a Base58Check
string with a valid checksum, rather than a raw private key encoding.

Method: every substring of length 21 to 64 characters, both reading directions, on
both source objects.

Result: 123,728 submissions, 0 match, and separately: zero valid Base58Check
checksum found anywhere in this space. That checksum observation is reported as a
fact, not used as a filter ahead of the address-comparison step. Witness: yes.
Date: 2026-07-28.

## 6. Direct readings of the large "Dualite" blob without a password

Hypothesis: the second, larger OpenSSL-format blob on the final page (titled
"Dualite" in the page's own markup) might be plain bits to read directly, rather
than something requiring a password.

Method: every 256-bit window (step 1 bit) of the decoded blob, submitted directly
to the address comparison, no key involved.

Result: 59,269 submissions, 0 match. A companion entropy measurement (byte
histogram, autocorrelation) on the same blob shows it is indistinguishable from
well-formed AES-CBC ciphertext, not from noise or a decorative filler value.
Witness: yes, on both the submission sweep and the entropy measurement.
Date: 2026-07-30. This narrows the interpretation (it is encrypted data with an
unknown key, not noise to read directly) without narrowing the space of possible
passwords, which has not been swept for this blob: see the README's mechanism
section for why this repository does not ship an oracle for it.

## 7. Taijitu (yin-yang) antisymmetry reading of the 256-symbol object

Hypothesis: the object, read as a binary image under some letter-to-bit mask, forms
a taijitu (rotationally antisymmetric) pattern, echoing a creator hint about a
"ying yang".

Method: analytic check, not a search: for every one of the 128 possible letter
pairings needed to test 180-degree rotational antisymmetry under any mask, checked
whether at least one pair of positions is forced to carry the same letter twice.

Result: every one of the 128 pairings fails this check, so no letter-to-bit mask can
produce a taijitu from this object. Refuted analytically; no submissions needed.
Date: 2026-07-28.

## 8. A partial replay of literal candidate strings from the folder's own history

Hypothesis: among literal password guesses tried by scripts written over several
years, some were built correctly but never reached a real address comparison,
because of the appearance-based filter bug described above.

Method: 13,090 literal strings harvested from 1,017 archived scripts that contain
password-guessing logic, submitted directly to an address comparison with zero
rejection ahead of that comparison; separately, the single most-repeated candidate
family across the same archive (69,454 variants).

Result: 46,589 plus 69,454 submissions, 0 match. Witness: yes, head, middle and
tail witnesses recovered. Date: 2026-07-28. This is explicitly a partial replay,
not a completed one: it covers literal strings only, not the patterns those same
scripts constructed dynamically at run time (concatenations, permutations, chained
derivations). Those dynamic patterns are the subject of the open lead ranked first
in the README; this row is why that lead is ranked first rather than closed.

## 9. The small-blob pipeline, first sweeps

The rows above test the 256-symbol object and the large blob. None of them tests the
small-blob pipeline `tools/oracle.py` implements (candidate answer to sha256 password to
AES decrypt to 32-byte key to address). These rows are the first sweeps of it.

Every sweep below was first run against the shipped oracle, which derived the AES key with
EVP_BytesToKey/MD5. That derivation is wrong for this puzzle (see section 10). The counts
and results here are from the re-run under EVP_BytesToKey/SHA-256; the earlier results are
void rather than negative, and are not reported.

Method: candidates pushed through the corrected oracle with no filter ahead of the address
comparison. PKCS7 padding rejects about 255 of every 256 wrong passwords before any
elliptic-curve work, measured at 0.35 percent of random passwords producing valid padding
against 0.39 percent expected, which is what makes this pipeline cheap to sweep. Measured
rate 76,803 candidates per second per core.

| Configuration | Candidates | Result |
|---|---|---|
| Puzzle vocabulary and stage names, each in four cases and reversed | 273 | 0 match |
| Ordered pairs of that vocabulary | 74,256 | 0 match |
| Suffixes and prefixes of the Architect message | 4,174 | 0 match |
| Every contiguous word window up to 14 words of the Architect message, the VIC plaintext, and the phase-2 and phase-3 decryptions | 49,808 | 0 match |
| Last-N-word readings of every stage text, in the conventions the pages state | 5,608 | 0 match |
| Live-page prose re-fetched from the site, SalPhaseIon and Cosmic Duality terms | 17,125 | 0 match |
| The system word list, each entry in four cases and reversed | 1,194,789 | 0 match |
| Confirmed stage passwords and their pairwise concatenations, including the phase-1 form password recovered from the hidden POST form on the theseedisplanted page | 12,544 | 0 match |

Result: 1,358,577 submissions, 0 match. Witness: yes, the corrected oracle reproduces two
real puzzle blobs from their known passwords (section 10). Date: 2026-08-19.

## 10. Key derivation: the shipped oracle used the wrong digest

Not a candidate sweep. `tools/oracle.py` derived the AES key with EVP_BytesToKey/MD5, and
its docstring described MD5 as "the scheme used throughout this puzzle's earlier stages".
That is false, and it is checkable against the puzzle's own material.

Method: the phase-2 and phase-3 blobs were re-fetched from the live page and decrypted
with their known stage passwords under both digests.

| blob | password | MD5 | SHA-256 |
|---|---|---|---|
| phase 2 | sha256 of the stage answer | padding invalid, 35 percent printable | padding valid, 100 percent printable, known plaintext |
| phase 3 | sha256 of the concatenated parts 1 to 7 | padding invalid, 38 percent printable | padding valid, 100 percent printable, known plaintext |

The phase-3 password digest was recomputed independently and reproduces the digest the
community published, which confirms the password string as well as the digest choice.

Why the old selftest passed anyway: its part 2 encrypted a self-made blob with the same
derivation it then decrypted with. A round trip certifies self-consistency, not the digest
choice, and cannot fail on a wrong constant used on both sides. `tools/oracle.py` now
certifies against the phase-2 blob instead, and asserts that MD5 fails on it.

Scope, corrected 2026-08-19: it is proven that MD5 fails on the phase-2 and phase-3
blobs, which is enough to establish that the shipped oracle's hardcoded MD5 was wrong.
It is NOT true that MD5 is unused in this puzzle. The Cosmic Duality blob decrypts only
under EVP_BytesToKey with MD5, verified by reproducing its published plaintext hash
4f7a1e4e...c081 at 1327 bytes from the live page (see section 11). The author therefore
used both digests on different blobs, and nothing determines which the small blob uses,
because its password is unknown. Hardcoding either digest is an error; `tools/oracle.py`
now tries both.

Consequence: any negative previously obtained through the shipped oracle is uncertified
and needs re-running. Date: 2026-08-19.


## 11. Cosmic Duality is decryptable, and it uses MD5

Not a candidate sweep, and a correction to this folder's account of the large blob. Row 6
and the README describe the "Dualite" / Cosmic Duality blob as never successfully
decrypted under any tested password. It has been decrypted, publicly, and the result
reproduces here from primary sources.

Method: the key is the XOR chain of the SHA-256 digests of seven tokens, in order --
matrixsumlist, enter, lastwordsbeforearchichoice, thispassword, matrixsumlist,
yourlastcommand, secondanswer -- giving
a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735. Those 32 raw bytes are
then used as the password to EVP_BytesToKey with MD5 against the blob published on the
SalPhaseIon page.

Result: 1327 bytes of high-entropy output, SHA-256
4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081. Both the key and the
plaintext hash were reproduced independently here from the live page, matching the
published values exactly. Witness: yes, the reproduction is the witness. Date: 2026-08-19.

Note that four of the seven tokens are the strings this folder already documents from the
SalPhaseIon page. They are ingredients in a key derivation, not the answer string the
small blob's password is built from; reading `lastwordsbeforearchichoice` and
`thispassword` as an instruction naming the small blob's password (section 9's last-words
sweeps) is therefore probably the wrong reading of them.

Consequence for the small blob: since the puzzle demonstrably mixes digests, sweeps that
assume one digest cover only half the space. Section 9's sweeps assumed SHA-256 and are
negative only for SHA-256.


## 12. The Half / Better Half derivation, reproduced end to end

Not a candidate sweep. The Cosmic Duality plaintext from section 11 carries the rest of
the chain, and the whole of it reproduces here from primary sources.

Method, applied to the 1327-byte plaintext:

1. Read as a bitstream, row-major, into a 103 x 103 binary matrix. 1327 bytes is 10,616
   bits and 103 x 103 is 10,609, leaving 7 padding bits; the fit is exact.
2. Take row_sums[i] (ones per row) and col_sums[i] (ones per column).
3. secondary[i] = chr((row_sums[i] + col_sums[(i + 7) mod 103]) and 0xFF), giving 103
   characters whose ordinals lie in 80..117, i.e. exactly 38 distinct symbols.
4. Decode those 103 characters as a base-38 number with digit = ord(ch) - 80, giving 68
   bytes: 32 for "Half", 32 for "Better half", and 4 trailing.

Result: the 103-character secondary string reproduces the value published in
puzzlehunt/gsmgio-5btc-puzzle#72 exactly, and the two 32-byte values reproduce the keys
published in that repository's issue #79, which derive to:

| | compressed | uncompressed |
|---|---|---|
| Half | 1JG648yaB7Wp2dpUfcZoRSD4q35oq47vCu | 15E3pcDDXSKhvi3CLVhRTHEgd8dbVKvSZg |
| Better half | 145ZQ9siLrsXBKf465wjdyQYAP5dRwhRhQ | 1FhbJnrdq1FmeiXrpTqnpQ8jvYV7naze96 |

The private keys are already public in that issue and are not repeated here; the four
addresses above are enough to check the derivation. All four were empty when checked on
2026-08-19. Witness: yes, the reproduction from the live page is the witness.
Date: 2026-08-19.

## 13. The trailing 4 bytes complete the phase-2 variable table

The 4 bytes left over from section 12's base-38 decode are `fc0c1b02`. Read as signed
bytes they are -4, 12, 27, 2.

Those are the four unknowns in the table the phase-2 page prints as
`# X 2 S H 4 Y 0 Q B 15 #`. Two of its variables were already public: S = 32, from the
Klingon arithmetic the page gives (cha' + vagh x jav = 2 + 5 x 6), and B = -16, from the
Intel processor model number the page gives ((4i)^2). X, H, Y and Q had no published
values. With the trailing bytes supplying X = -4, H = 12, Y = 27 and Q = 2, the table
resolves in full to:

    -4, 2, 32, 12, 4, 27, 0, 2, -16, 15

This closes an object that had been partially solved since 2019 and connects two stages
that were previously unrelated in this folder's account: the phase-2 riddle table and the
tail of the Cosmic Duality decode.

Tested as password material for the small blob (decimal joins with several separators,
absolute values, hex forms, the raw byte string, the concatenated and XORed key material,
each under both key-derivation digests): 32 forms, 0 match.

Provenance note: the same reading appears in puzzlehunt/gsmgio-5btc-puzzle#88. That issue
also asserts a hidden "Salted__" blob at offset 158 of the Cosmic Duality plaintext with
salt 5bbd88ac32481bca, which is false: there is no such marker anywhere in the 1327 bytes
and those eight salt bytes occur at no offset, checked against a file whose SHA-256
matches the one that issue itself publishes. The table reading is recorded here because it
was independently verified, not because it was posted.


## 14. The final page's letter streams: reproduction, two new objects, first readings

Working from the original-era capture of the SalPhaseIon page (2023-06-01 snapshot,
1075 single-character tokens), the body splits into: a 91-letter run over a to i
(starting `dbbi`), the 104-token ab-run decoding to `matrixsumlist`, a 570-letter run
over a to i (starting `faed`), the two z-separated instruction segments, and the small
blob halves with their 40-token `enter` run. The two long runs are letters, not digits:
read as uppercase they are exactly the alphabet of the Bifid square's first two rows
(D, B, I, F, H, C, E, G, A, K), which is why they were previously mislabelled digit
streams.

Reproduction witness: feeding the 570-letter run to a plain Bifid decryption with the
keyed square `DBIFHCEG` (J dropped, row-major) and period equal to the full length
reproduces the documented output byte for byte, starting `BTCSEED`, on 2026-08-23,
from this folder's own reconstruction of the archived page. The odd-position stream
again reduces to exactly 256 symbols over 23 letters after removing I and O.

Two objects fall out of the same reconstruction that no public source accounts for:

1. The even-position stream of the Bifid output is 285 symbols drawn from only four
   letters, B, C, D and E, with counts B=54, C=90, D=72, E=69. A random 25-letter
   stream restricted to four symbols for 285 positions is not plausible; this is an
   authored channel whose encoding is unknown.
2. The 29 dropped letters, in extraction order, are
   `OOIIOOOIIOOIOIIOIOOOOIOIIOIOI`: every dropped letter is I or O and the sequence
   reads naturally as binary.

The 91-letter run resists Bifid decryption at periods 91, 13, 7 and 1 under the same
square; it remains undecoded (uncertified probe, no address comparison involved).

First readings attempted on the even stream, all uncertified explorations rather than
sweeps: Morse role assignments (0 of 24 legible), Baconian five-bit readings under all
two-class partitions, both polarities and both directions (nothing English-like),
base-4 to bytes under all 24 digit orders (best printable ratio 0.46, none readable),
decimal-to-hex-to-ASCII conversions under four value maps, coordinate recombination
with the odd stream, and Vigenere shifts mod 25. None produced a legible string; the
object stays open.

## 15. Hash-slug routes: three sha256 preimages recovered, seven open

Enumeration of archived gsmg.io paths shows ten 32-hex-character slugs beyond the
SalPhaseIon route. Three fell to direct hashing of lowercase concatenated phrases from
the puzzle's own vocabulary:

    e24bd2c0fd454632f9fdd26cbdc210597f79e9fca9719c126a6d30cb41ef0238 = ourfirsthintisyourlastcommand
    c1780cbbaa105784949cd6a2924e1f51a947b4258a0655defd0cd2e6f6544046 = hopeisthequintessentialhumandelusion
    21ef053324184a4db5dc19b760e2d6ef61b07376a6f8a1514bb529d99de1fe0f = anstoo

`anstoo` is a new string: it ends the token stream (`shabefanstoo`), and the phrase
pattern of the other preimages confirms the segmentation. The page behind it has no
archived captures at all.

Still open, listed so nobody re-tests them by accident:

    0b0f37ecaf7107f86ee2f477992f25bc7abe8f799d0dd713658c17d37496ee32
    10d6a2c5320bfbd47d35f18dd67f177ae5a5f4b5d18a8a5127361c2941a92908
    673e3b1a60ebe6fc4a8be88acde2600e12afd9efb2543e26b1b30039f8356b0d
    a2aefdbb953b70aa20d640effda4accee1e1f48acf1e4fcebdc2fc011418b0b1
    aca20ae7c6b5f425bdd9bd809583b28fd086b3380990689e37b6e94f3fb5ed9a
    c2eef34b479eb6c89c7aa89c49229ff5f67563da4e56d5782574489c4b776625
    f9719d6d531e6c3b5129644cd05da57bc6fdd075c9a61267c41d4b9627936096

Related slug-route objects: two pages whose URLs are hex-encoded OpenSSL blobs
(`Salted__` header, salt `74c974e3f92e64b5`, one 40 bytes and one 112 bytes total).
An external sweep (puzzlehunt/gsmgio-5btc-puzzle#106) reports zero hits across four
key derivations, three password encodings and four cipher modes against roughly 56k
candidates including these; that sweep has not been repeated with this folder's
candidate families through the corrected oracle.

## 16. New instruction vocabulary through the certified oracle

The strings recovered in sections 14 and 15, as password candidates for the small
blob through `tools/oracle.py` (selftest passing): `anstoo` in three cases plus the
spaced form, `ourfirsthintisyourlastcommand` in four forms, 
`hopeisthequintessentialhumandelusion` in two cases, the four instruction tokens
individually, and the author-hint assembly
`yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang`.

Result: 16 submissions, 16 NO MATCH. Witness: yes, the selftest passes and the same
run re-confirms that a known stage answer decrypts its own blob. Date: 2026-08-23.


## Cumulative

Across the 7 completed hypothesis families above (rows 1 to 7), 335,724,615
candidate submissions were made against the real address-comparison logic used in
the private research, all negative. Row 8's 116,043 submissions are reported
separately because that replay is explicitly partial. Section 9's 1,358,577 submissions
are reported separately again, because they sweep a different half of the final gate (the
small blob) and because they postdate the key-derivation correction in section 10. Rows 1 to 5 test the
hypothesis that the 256-symbol object reduces directly to a 32-byte key, bypassing
the AES blob entirely; row 6 tests the large blob without a password. Rows 1 to 8 do not
test the small-blob pipeline that `tools/oracle.py` in this folder implements
(candidate answer to sha256 password to AES decrypt); as of the private research's last
update that publicly reproducible half of the final gate had not been isolated and swept
on its own. Section 9 is the first sweep of it, and section 10 records why every result
obtained through the shipped oracle before that point has to be discarded.
