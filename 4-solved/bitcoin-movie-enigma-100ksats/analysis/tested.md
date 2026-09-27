# Tested hypotheses, full ledger

Summary table is in the README. This file has the full detail behind each row. All
counts below were re-read from my own private research notes before writing this
folder.

## Both published image sets are identical

The rules page mentions "an alternative release, as a single image." I compared
every one of the 34 individual panel images against the corresponding region of the
combined alternative-release image, byte for byte (MD5).

Result: 34 of 34 panels match exactly. This channel is closed: the alternative
release carries no additional or different information, it is the same 34 stills
republished as one file. Date: 2026-08-03.

## Intruder criterion: MPAA rating equals R

Hypothesis: the 10 "intruder" films are exactly the ones rated R by the MPAA, and
the IMDb page field the rules point to is the certificate rating.

Method: count the films confirmed R-rated as more panels were identified.

Result: this criterion looked correct early, when only a partial set of films was
identified (10 of 18 identified films rated R at one point). It broke as soon as 2
more films were confirmed: with panel #4 (Mad Max, R) and panel #34 (rated R under
either of its 2 disputed identifications) added, the R-rated count reached 16 to 18
out of the identified films, well past 10. Refuted. Witness: this is a direct count
over the film corpus, not a search that could produce a false negative; re-counting
is immediate from `data/films.csv`. Date: 2026-08-04.

## Intruder criterion: won at least one Oscar

Hypothesis: the 10 intruders are the films that won at least one Academy Award.

Method: same approach, counting Oscar-winning films as identifications accumulated.

Result: looked correct at 10 of 21 identified films early on, refuted once panel
#24 (Ordinary People, a 4-Oscar winner including Best Picture) was confirmed
through a route independent of the reverse-image search used for most other
panels, pushing the count to 11 of 34. Date: 2026-08-04.

## Intruder criterion: adapted from a novel

Hypothesis: the 10 intruders are the films adapted from a published novel.

Method: same approach.

Result: looked correct at 10 of 31 identified films, refuted at 12 of 34 once
further identifications landed. Date: 2026-08-04.

## About 25 further intruder criteria

Method: the same accumulate-and-recount approach applied to about 25 further
candidate IMDb fields and binary properties (examples: country of origin,
decade of release, director's other Bitcoin-relevant work, runtime bracket, color
versus black and white, single-word versus multi-word title).

Result: none produced an exact 24-versus-10 split against the identified film set,
either from the start or after refutation by a later identification. Witness: each
criterion is a direct count over the film corpus and is immediately re-checkable;
no witness protocol beyond re-counting applies here. Date: 2026-08-04.

Methodological note, kept because it explains why no criterion is locked in below:
3 different criteria (MPAA=R, Oscar win, novel adaptation) each looked like the
answer while the film corpus was still incomplete, and each was broken by the very
next identification. With about 25 to 30 criteria tried against a set of only 34
films, landing on an exact 10-film split by chance is not strong evidence on its
own. My working rule is to not treat any criterion as confirmed before all 34
panels are identified with confidence.

## PNG EXIF and XMP on the published stills

Hypothesis: the 34 published `NN_crop.png` files carry the movie title, the BIP39
word, or some other payload in EXIF/XMP.

Method: download all 34 crops from bitcoinmovieenigma.com and read PIL `Image.info`
plus the TIFF EXIF block.

Result: every file carries the same payload, byte for byte in the XMP packet:
`dc:description` / `ImageDescription` is the literal string "nope", and
`dc:creator` / `Artist` is `@cryptop1r4t3`. That is a decoy, not a channel.
Witness: all 34 XMP packets compare equal; re-download and re-read to confirm.
Date: 2026-08-27.

## Title-to-word rule: unique 4-letter BIP39 prefix in the compact title

Hypothesis: the transform is "find the unique BIP39 4-letter prefix (or the whole
word, if it is 3 letters) as a substring of the title with spaces and punctuation
removed." Under that reading, "raidersofthe" contains `soft`, "theshining"
contains `shin` -> `shine`, "leontheprofessional" contains `prof` -> `profit`,
and "sharknado" contains `shar` -> `share`.

Method: run every 4-letter window of each compact title against the English BIP39
wordlist's unique prefixes.

Result: this produces at least one word for 33 of 34 community-identified titles.
The only title with no prefix and no literal substring is The Goonies (panel 8).
This is a measurement, not a match against the escrow. Date: 2026-08-27.

## Intruders = G, PG, and TV-14 (keep R and PG-13, plus unrated)

Hypothesis: on the reconciled community film list, the 10 intruders are the
films whose IMDb / MPAA certificate is G, PG, or TV-14, i.e. panels 7, 8, 12,
18, 24, 25, 26, 30, 31, and 32. That set includes both wordless-under-literal
titles The Goonies and Sharknado, so the remaining 24 titles all have a BIP39
reading. Paths of Glory (APPROVED) and Spartacus (no MPAA claim on Wikidata)
were kept, not dropped.

Method: take the 24 keepers in panel order and, for each title with more than
one reading, the Cartesian product of the short alternative list in
`data/films.csv` (leftmost unique-prefix word plus the community substring
reading). 55,296 raw 24-word strings, of which 227 pass the BIP39 checksum.
Each checksum-valid mnemonic was run through `tools/oracle.py` (BIP84/49/44
and the 3 raw paths).

Result: 0 match. Uncertified: no known-good 24-word mnemonic for this escrow
exists to plant as a head/middle/tail witness in the same loop; the oracle
self-test against the public BIP39/BIP84 vectors passed the same day. Rate:
about 18,000 raw strings/s, checksum filter first, then the full derivation
only on the 227 valid mnemonics. Date: 2026-08-27.

## Title-to-word rule: base rate measurement

This is a measurement, not a hypothesis test with a pass or fail result: of the 33
titles identified as of 2026-08-04, 29 contain at least one English BIP39 word as a
literal substring of the title (for example, "Die Hard" contains "hard"; "A
Clockwork Orange" contains 4 candidates: "clock," "orange," "range," "work"). Four
titles contain none: The Goonies, Barry Lyndon, Sharknado, and Raiders of the Lost
Ark. The literal-substring rate across the 33 identified titles is about 14%,
counted per candidate word against the full BIP39 wordlist. This measurement rules
out "every title contains exactly one obvious word" as the full rule (4 titles have
none, several have more than one), but does not by itself say which of several
candidate words is the intended one, or what the rule is for the 4 titles with none.

## Community metadata-rule sweeps (issue #9, 2026-08-22 to 2026-08-23)

Contributed in issue #9 and recorded here as reported by the runners, not re-run by me.
They test the intruder criterion under the community film list, so a match would need both
that list and the rule to be right at once.

timothy-barus: every intruder predicate expressible from IMDb metadata that selects exactly
10 of the 34 panels, three of which leave at most two panels wordless and so are fully
coverable with 2048-word wildcards. Three rules swept exhaustively (shares a release year,
released 2000 or later, ten shortest by runtime): 314,069,483,520 raw candidates,
1,226,826,312 checksum-valid seeds, derived at BIP84 m/84'/0'/0'/0/{0,1,2} and matched
against the escrow hash160. Witnessed: GPU reproduces the CPU reference byte for byte, three
planted witness mnemonics recovered from head, middle and tail, checksum rate within 0.6
sigma of raw/256. Result: 0 match.

SmallCakekoo: 25 single-field IMDb boolean criteria cross-tested pairwise with AND/OR, 600
combinations, 17 of which produce an exact 10-panel split; all 17 run through full derivation
and address check, 0 match. Separately, an IMDb-connections hypothesis (30 documented
cross-references among the 34 films, exactly 10 films with zero in-set connections) tested two
ways: 1,828,915,200 candidates over every sourced IMDb-keyword word for the titles with no
literal BIP39 substring, and all 131,128,140 ways to choose which 10 of 34 to drop under one
fixed word per panel. Result: 0 match in either.

Standing after these: every clean IMDb-metadata rule that leaves at most two panels wordless
has been swept and is empty. The open problem is the title-to-word rule for the three titles
that yield no BIP39 word under the community list (The Goonies, Leon, Sharknado), which is a
reading question, not a compute one. See leads.md.

## Sweeps on the consensus film list, 2026-09-01 and 2026-09-02

Oracle: the public BIP84 vector (`abandon` x 23 plus `art`) reproduced, target the
escrow's hash160; enumeration with a BIP39 checksum filter in C (OpenMP), derivation on
CPU (BIP84, BIP44, BIP49, BIP86 and raw paths) or on a 24-word port of the shared GPU
engine (BIP84 `0/0` only). "Witness 3/3" means 3 synthetic 24-word mnemonics planted at
head, middle and tail of that run and recovered by the normal path; "vector only" means
no witness was planted in that run and it is uncertified.

| Hypothesis | Raw candidates | Derivations | Witness | Result |
|---|---|---|---|---|
| Older identifications: the titles without a literal word fixed as intruders, plus 5 of the remaining 29 | 4.0e8 | 1,563,007 | 3/3 | 0 match |
| Same, with panels 3 and 5 as Aliens and Alien | 2.2e8 | 875,811 | 3/3 | 0 match |
| Consensus list: 6 wordless or ambiguous panels fixed as intruders plus 4 of the other 28, literal words | 5.95e7 | 231,806 | 3/3 | 0 match |
| Same, with panel 14 as The Man in the Iron Mask (`iron`, `mask`, `man`, `ask`) | 1.67e8 | 651,882 | 3/3 | 0 match |
| Consensus list, words from substrings of 3 or more letters, 4 wordless panels fixed plus 6 of 30 (GPU, 445 s) | 1.52e10 | 59,321,852 | 3/3 | 0 match |
| The natural partition (the 24 titles with an obvious word), 178 derivation paths, 4 seed constructions, no checksum filter | 512 | 512 x 712 | vector only | 0 match |
| Natural partition, forward and backward, one position free over the 2048 words | 5.0e7 | 955,206 | vector only | 0 match |
| Kubrick x5 plus Jean Reno x5 as the 10 intruders (panel 14 = Iron Mask), panel 8 free, `share` or `tornado` for 26, `soft` for 32 | 3.1e6 | 12,344 | vector only | 0 match |
| Same, ambiguities widened (`eye`/`wide`, `cat`, `run`, `load`, `host`, `ski`, `ride`, `tip`) | 1.0e9 | 3,981,013 | vector only | 0 match |
| Release year or runtime read as a BIP39 index (10 variants), 11 intruders plus 9 of 33 | 3.9e8 | 1,502,910 | vector only | 0 match |
| 6 deterministic 4-letter-prefix rules, 4 wordless panels fixed plus 6 of 30 | 3.6e6 | 13,914 | vector only | 0 match |
| 40 neighbour rules (alphabetical neighbour, longest common prefix, letter counts), keepers = 20th-century films | 1.8e7 | 68,958 | vector only | 0 match |

Totals: about 1.6e10 raw candidates and 62,644,358 derivations with witnesses (5 runs),
about 1.5e9 raw candidates and 6,534,857 derivations without (7 runs), 0 match. Two runs
were interrupted and are not counted: substrings of 3 or more letters with panel 14 as
Iron Mask (85 million of 178 million lines), and a no-checksum pilot on the GPU. Rate:
about 13,000 derivations/s on 24 CPU cores across 7 paths; about 170,000 derivations/s on
one GPU for BIP84 `0/0`. Dates: 2026-09-01 and 2026-09-02.

What this closes: on the consensus list, the intruders are not "the titles with no
literal word plus a few others" at any depth up to substrings of 3 letters, and the
Kubrick plus Reno split does not solve with a single free position. What it leaves: that
split at two free positions, and the two rules themselves.

## Panel 14, settled 2026-09-03

I had kept panel 14 as Eyes Wide Shut against the community's The Man in the Iron
Mask. On 2026-08-29 deviceio121 posted two frames from
[youtube 3PcEZNC7IPw at 2:18](https://www.youtube.com/watch?v=3PcEZNC7IPw), which is
MGM's official "Judgement Day" scene from The Man in the Iron Mask (the video's own
title). The frame shows the same masked group as the panel: the woman in the gold mask
and red-and-gold turban at left, the man in the long wig holding a gold bearded mask
on a stick at centre. Panel 14 is The Man in the Iron Mask, and the Kubrick plus Reno
split stands at exactly 10.


## Confirmed solve, 2026-09-07

The title-opening-prefix reading and five thematic film groups yield an exact
escrow-address match at m/84'/0'/0'/0/0. The 24-word phrase fails the BIP39
checksum (encoded 47, expected 119); checksum-filtered negatives therefore
do not cover this answer. The oracle now derives without that assumption and
its self-test reproduces the actual solution. Independent manual BIP32 and
Bech32 calculations agree. The payout of 99,766 sats (234 sats fee) confirmed
in block 965998. See the README and
[payout verification](payout-verification-2026-09-07.json).

---

# Prior on-device research notes (2026-08-29), preserved on sync

The solve above supersedes these notes; they are kept only because they record
what was tried on this device before the community solve landed.


## The two unswept intruder rules, my 3-word hypothesis (2026-08-29)

Context: timothy-barus's GPU sweep (issue #9) exhausted every clean IMDb-metadata
rule that leaves at most two panels wordless, under substring words for the 31
worded panels. It swept `shares a release year`, `released >= 2000`, and `ten
shortest`. It could NOT touch the two rules that leave panels 8, 13 AND 26 all
wordless-and-kept (`pre-1980`, `ten longest`), because those need three words at
once (2048^3 wildcard). The thread's explicit note: solving even one of the three
words unlocks those two as ~an-hour two-wildcard runs.

Hypothesis under test here (not previously run anywhere): the three wordless films'
words are Leon->`lion` (homophone, community-concurred), Sharknado->`tornado`
(portmanteau second half; BIP39 word), The Goonies-> one of `never` (tagline
"Goonies never say die"), `goose` (diploux's phonetic read), `chunk`, `brand`
(names of main Goonies characters). Under this reading the two unswept rules become
a *single seed per rule*, not a wildcard sweep.

Method: for each rule, fixed the other keepers' words from the community substring
table (timothy-barus issue #9), enumerated every multi-word keeper panel
(sparTACUS/GOTG/etc.), and oracle-checked every 24-word seed with each Goonies
candidate substituted at panel 8.

| Rule | Drop set | Word combos | Seeds tested | MATCH |
|---|---|---|---|---|
| pre-1980 (year<1980) | {2,4,5,6,7,9,17,18,24,25} = 10 | 256 multi × 4 Goonies | 1024 | 0 |
| ten-longest, 137-min tie=panel 3 | {9,25,22,6,33,20,11,24,29,3} | 5120 × 4 | 20480 | 0 |
| ten-longest, 137-min tie=panel 27 | {9,25,22,6,33,20,11,24,29,27} | 2560 × 4 | 10240 | 0 |

Total **31,744** seeds, no match. Witness: oracle=`tools/oracle.py` (`SELFTEST OK`,
BIP84 `m/84'/0'/0'/0/{0,1,2}` against the escrow hash160=100,000 sats address);
isolation = each seed is the literal join of the per-panel word dict, re-derivable
from the table above. Rate ~18/s (CPython+BIP39 on this phone), so t=1770s for the
largest run - under the 2-hour bound.

Meaning, read honestly: this negative is only as strong as the substring-word base
for the other 24-26 keepers. If the title-to-word rule is conceptual instead of
substring (as the late issue-#9 argument contends: Godzilla="ill", Life of Pi="life"
are absurd as picks, vs concept `lizard`/`tiger`), then the whole base is wrong and
this test cannot hit regardless. It does however rule out my exact 3-word reading in
the substring hypothesis against BOTH the rules that keep 8/13/26.

## Conceptual word-rule sweep (2026-08-29)

The late issue-#9 argument holds that the substring rule is wrong and the intended
word per film is its single most-iconic BIP39 *concept* (Godzilla->lizard, Life of
Pi->tiger), which would change nearly every word and explain every substring sweep
coming back empty. Tested that hypothesis.

Base conceptual assignment (best single guess per film), with BIP39 membership
verified against the 2048-wordlist:
`1 hard, 2 glory, 3 alien, 4 mad, 5 alien, 6 now, 7 escape, 8 chunk, 9 arena,
10 spy, 11 dragon, 12 tiger, 13 lion, 14 mask, 15 river, 16 visit, 17 orange,
18 hope, 19 gravity, 20 moon, 21 solar, 22 blade, 23 galaxy, 24 close, 25 bar,
26 tornado, 27 term, 28 ghost, 29 matrix, 30 toy, 31 ghost, 32 whip, 33 shine,
34 human`.

Method: for each of the 6 exact-10 intruder rules (shared-year, >=2000, ten-shortest,
pre-1980, ten-longest x2 ties), build the 24-keeper seed in panel order and
oracle-check (BIP84 0,1,2). Sub-sweeps, all empty:

| Sweep | Seeds | Rules | MATCH |
|---|---|---|---|
| base assignment, all 6 rules | 6 | 6 | 0 |
| one-variable-at-a-time candidates (7,8,9,10,11,12,14,17,18,20,23,24,27,28,32) | 28 | 6 | 0 |
| joint 2-variable over 8,9,11,12,20,32 (base+alt words) | 216 | 6 | 0 |

Total 250 concept-conditioned seeds, all `no match`. Witness: `tools/oracle.py
--selftest OK`; escrow re-verified OPEN at 100,000 sats. t for the largest sweep
well under the 2-hour bound (each seed <1s).

Read honestly: the conceptual hypothesis is NOT falsified by this - it simply is not
searchable by enumeration, because a single wrong word in any keeper breaks all 6
rules and guessing ~24 author-intent words at once with no gradient signal has near-
zero success rate. The value of this pass is the per-film candidate base above, which
a human who knows the films can correct one panel at a time; the oracle test for any
corrected full wordlist is a single `check()` per rule.

## Plot/IMDb-review conceptual 34-word sweep (2026-08-29)

Carried the IMDb-review/plot-grounded hypothesis to a full 34-word reading: each
film gets its single most-iconic BIP39 concept word from its IMDb plot/review
content (e.g. Leon->orphan from "Orphaned by the massacre", Goonies->chunk,
Sharknado->tornado, Godzilla->lizard, Life of Pi->tiger, First Man->moon,
Scream 2->ghost/Ghostface, Raiders->whip). Base assignment:
`1 hard,2 glory,3 alien,4 mad,5 alien,6 river,7 island,8 chunk,9 arena,10 spy,
11 lizard,12 tiger,13 orphan,14 mask,15 river,16 visit,17 orange,18 force,
19 gravity,20 moon,21 solar,22 blade,23 galaxy,24 alien,25 bar,26 tornado,
27 machine,28 ghost,29 matrix,30 toy,31 ghost,32 whip,33 shine,34 human`,
with per-panel BIP39-verified alternates for the uncertain ones.

Method: each of the 6 exact-10 intruder rules, 24-keeper seed in panel order,
oracle-checked (BIP84 0/1/2). Sweeps:

| Sweep | Seeds | Rules | MATCH |
|---|---|---|---|
| plot base assignment | 6 | 6 | 0 |
| 1-variable-at-a-time alternates (13 panels) | 22 | 6 | 0 |
| 2-variable joint pairs (12 uncertain panels, alternates) | 221 | 6 | 0 |

Total 249 plot-conditioned seeds, all no match. Witness: local `tools/oracle.py
--selftest OK`; escrow verified OPEN (100,000 sats, balance==received). t<<2h.

Read honestly: with 34 subjective author-intent words and no gradient signal, this
cannot converge by enumeration even if the conceptual rule is correct - I likely
have wrong words in more than a couple of keeper panels. The output value is the
candidate table above + analysis/leads.md, which a film-literate human can correct
one panel at a time; a corrected full 34-word list is then one check() call per rule.

## Plot-identity words x diploux rating<=7 rule (2026-08-29)

Community thread shows SmallCakekoo already closed the metadata-intruder space:
25 single-field IMDb criteria cross-tested as AND/OR pairs = 600 combos, of which
17 yield exactly 10 discards - all 17 already fully derived, none matched; plus his
IMDb-Connections hypothesis (10 zero-connection films; ~1.96B seeds) also empty.
diploux then proposed `IMDb rating <= 7` as a 10-intruder rule, and independently
argued the WORD reading is plot/character-identity (Goonies->chunk, Godzilla->
lizard, Life of Pi->tiger, Spartacus->arena, Escape from Alcatraz->prison/island) -
matching the plot-based derivation I had independently produced.

Here I combined the two: my 34-panel plot/character-identity word list, tested
under diploux's rating<=7 intruder set {4,11,14,15,16,21,26,28,31,34} (keeps 24,
panel 26 Sharknado is an intruder so its word is irrelevant).

| Sweep | Seeds | MATCH |
|---|---|---|
| plot-identity base (rating<=7) | 1 | 0 |
| 1-variable alternates (16 panels) | 25 | 0 |
| 2-variable joint pairs (16 panels, alternates) | 444 | 0 |

Total 470 seeds, all no match. Witness: local `oracle.py` SELFTEST OK; escrow
OPEN (100,000 sats). t<<2h.

Verdict: even the community's most-plausible rule agreement + two independent
solvers converging on the same plot-word reading fails to land a single checksum.
This strongly supports SmallCakekoo's own conclusion that the bottleneck is the
WORD LIST (per-panel author-intent word), not the intruder criterion - several
keeper panels' exact words are still wrong.

## Cross-check vs authoritative IMDb runtimes: ten-longest tie resolved (2026-08-29)

Re-pulled `title.basics.tsv.gz` (IMDb) and read the 34 runtimes directly;
the repo's ten-longest handling was already correct (two tie variants, both on
record as 0 matches). Key authoritative values at the cut line: Godzilla
(p11) = 139 min, Aliens (p3) = 137, Terminator 2 (p27) = 137. Ten longest =
{25,9,22,6,33,20,11,24,29,3} (Godzilla IN, p3 is the 10th at 137; p27 ties at 137
so the boundary is ambiguous -> the two-variant treatment in the table above is
the right call). A scratch re-check of the plot-identity word list under this
confirmed set (base + 1-var + 2-var pairs, alternates): 472 seeds, 0 matches.
Also re-confirmed diploux rating<=7 intruder set = {4,11,14,15,16,21,26,28,31,34}
from a fresh `title.ratings.tsv.gz` pull. Witness: local `oracle.py` SELFTEST OK;
escrow OPEN (100,000 sats). t<<2h.

## Deterministic longest-BIP39-substring 34-word reading (2026-08-29)

New, fully non-subjective reading derived from the "longest words" hint: for each
canonical title, take the LONGEST contiguous BIP39 word that appears as a substring
of the space/strip-normalized title. Computed against the official 2048-word list
sorted by length desc. Result per panel:
`1 hard,2 glory,3 alien,4 mad,5 alien,6 now,7 escape,8 (wordless),9 art,
10 possible,11 ill,12 life,13 (wordless),14 iron,15 river,16 visit,17 orange,
18 hope,19 gravity,20 first,21 solar,22 blade,23 galaxy,24 close,25 bar,
26 (wordless),27 term,28 cream,29 matrix,30 story,31 ghost,32 soft,
33 (wordless),34 human`.
Exactly four titles have NO BIP39 substring at all (8 Goonies, 13 Leon, 26
Sharknado, 33 Shining); filled those with concept words (chunk/orphan/tornado/
shine) in the sweep. Interesting by-products: longest reading gives p9 art (not
arena), p11 ill (godz-ILL-a, matching timothy-barus's "ill"), p28 cream, p10
possible.

Tested across 6 intruder rules {shared_year, >=2000, pre-1980, ten_shortest,
ten_longest, rating<=7}: base + 1-var alternates (42) + 2-var joint pairs (834)
= 877 seeds, 0 matches. Witness: local `oracle.py` SELFTEST OK; escrow OPEN
(100,000 sats). t<<2h.

## Ordering hypothesis (2026-08-29)

Tested whether the 24-keeper seed order is NOT panel order. For the plot-word
set and the longest-substring set x 6 intruder rules, tried 4 orderings of the
keepers: panel order, alphabetical-by-film-title, alphabetical-by-BIP39-word,
reverse-alphabetical-by-title. 48 seeds, 0 matches. So ordering is not the free
variable - the failure is in the per-panel words themselves (multiple keeper
panels wrong simultaneously), independent of how the surviving words are
arranged. Witness: local `oracle.py` SELFTEST OK; escrow OPEN. t<<2h.

## Target: pre-1980 rule, all three wordless panels joint keepers (2026-08-29)

pre-1980 drops release-year<1980 = {2,4,5,6,7,9,17,18,24,25}; keepers =
{1,3,8,10,11,12,13,14,15,16,19,20,21,22,23,26,27,28,29,30,31,32,33,34}. This is the
one intruder rule where The Goonies (8), Leon (13) AND Sharknado (26) - the three
titles needing a single conceptual transform - are all keepers at once, so a correct
word for each is required jointly.

Swept the 24-keep seed (panel order + alpha-by-title) with best-words base plus
1-variable and 2-variable joint alternates over all uncertain keepers, including
chunk/goose/truffle (8) x lion/orphan (13) x tornado (26). 1001 seeds, 0 matches.
Witness: `oracle.py --selftest OK`; escrow OPEN. t<<2h.

Read: even the rule that exercises all three transforms together, with all classic
alternates, fails - consistent with the bad-word bottleneck being on several keeper
panels at once, not a single panel. Pre-1980 remains not excluded as THE rule; it
just needs the correct word set.

## Famous-phrase-word reading for the three wordless titles (2026-08-29)

Hypothesis: each wordless title's BIP39 word is a keyword from a famous quoted
line/phrase of that film (pattern like the user's "the quick brown fox jumps over
the lazy dog" example). Candidate phrase-words, all BIP39-verified:
final, clean, word, master, record, tonight (client-supplied) + never (Goonies
"never say die"), rain (Sharknado "it's raining sharks"). Best map: Leon =
"clean" ("I'm a cleaner").

Tested under pre-1980 (where kids 8/13/26 are all keepers): wordless slots 8,13,26
each over {chunk|lion|tornado + final,clean,word,master,record,tonight,never,rain}
at best-words for the other 21 keepers. 512 seeds, 0 matches.
Witness: `oracle.py --selftest OK`; escrow OPEN. t<<2h.

Read: phrase-words for the three transforms still do not land alone - the remaining
24-keep seed needs correct words on several non-wordless keeper panels too
(e.g. panels whose word I set to lizard/moon/whip/hotel/etc.). Nothing here points
to a wrong intruder rule; it points at the word set again.

## Tight never/clean/tornado transform test, all 6 rules (2026-08-29)

Client proposed the three/four transform words tornado, never, clean, rain.
Mapped: Goonies(8)=never ("Goonies never say die"), Leon(13)=clean ("I'm a
cleaner"), Sharknado(26)=tornado (portmanteau; rain alternate).

Tested the full 34-panel seed (8=never,13=clean,26=tornado, others=best-words)
under all 6 major intruder rules {shared_year, >=2000, pre-1980, ten_shortest,
ten_longest, rating<=7}: base 0 hits; then 3-slot sweep of {never,clean,tornado,
rain,final,word,master,record,tonight,lion,orphan,chunk} across panels 8/13/26 =
392 seeds, 0 matches.

Decisive read: even the most plausible transform words for ALL THREE wordless
titles, under every rule where they are keepers, cannot land a checksum - so the
seed is blocked by wrong words on the other keeper panels as well. This closes
the "transform-only" hypothesis: the missing words are on the 21 non-wordless
keepers too, several at once.

## Wordpool scripted sweep (bounded) (2026-08-29)

Scripted the user's 212-word BIP39-validated candidate pool into per-panel
candidate maps and swept all 6 major intruder rules.
PASS 1: single-position scan - every pool word tried at every keeper position of
every rule (30,384 checks) - detects any base-wrong-in-one-place; no hit.
PASS 2: bounded multi-panel - per rule varied the most-uncertain keeper panels
(6 panels, product 8k-16k/rule, ~82k total) jointly incl. the 3 wordless 8/13/26;
no hit.
Total 112,304 checks, 0 matches. IMPORTANT rate correction: `check()` fast-rejects checksum-invalid seeds (~2,650/s)
before any address derivation; the expensive path is checksum-VALID seeds needing
full BIP84/49/44 derivation (~11/s). Of the 112,304 candidates, only ~0.4% (~450)
were checksum-valid, so this negative exercised only ~450 real derivations. The
honest 2-hour budget is ~79k checksum-valid derivations, most still unexplored.
Witness: `oracle.py --selftest OK`, escrow OPEN.

## Pre-1980 rule, joint 3-wordless deep sweep (2026-08-29)

Deep enumeration of the pre-1980 rule (drops {2,4,5,6,7,9,17,18,24,25}; keeps
{1,3,8,10,11,12,13,14,15,16,19,20,21,22,23,26,27,28,29,30,31,32,33,34}) over the
genre/plot word pool, joint over the three wordless keepers 8/13/26 (Goonies, Leon,
Sharknado) plus uncertain keeper alternates. ~5M raw panel combos, of which ~0.4%
are checksum-valid and get full BIP84/49/44 derivation (~20k real derivations);
ran to completion in the background, `/tmp/MATCH.txt` never written. 0 matches.
Witness: `oracle.py --selftest OK`; escrow OPEN (100,000 sats). Bounded under the
2-hour cap by design (see rate model in the wordpool entry above). Read: consistent
with the established bottleneck - multiple keeper panels' author-intent words are
wrong at once, so a bounded pool sweep of the one rule that keeps all three wordless
panels together still cannot land.
