# Solved and paid out

The exact solution and confirmed payout are now recorded in the README.
The earlier leads below are preserved as historical community research.

# Open leads, full notes

Ranked summary is in the README. This file has the reasoning behind the ranking.
The gate on this puzzle is entirely cultural (the title-to-word rule and an IMDb
field), not computational: once the 34 words and the intruder rule are both known,
checking a candidate is a single `tools/oracle.py` call.

## Frame-level reconciliation, 2026-08-27

The nine panels that still disagreed between `data/films.csv` (2026-08-04 pass)
and `data/films_community_issue9.csv` were checked against the published stills
at bitcoinmovieenigma.com. Community identifications that the still itself
settles, and that are now merged into `data/films.csv`:

| panel | 2026-08-04 pass | community / still |
|---|---|---|
| 3 | Alien | Aliens (1986): M41A pulse rifle, facehugger jar, Hadley's Hope ops console marked 70 |
| 5 | Star Trek: The Motion Picture | Alien (1979): Ripley in the Narcissus EVA suit; a shelf label reads RIPLEY |
| 14 | Eyes Wide Shut | The Man in the Iron Mask (1998): gold lorgnette masks, Louis XIV court dress; settled 2026-09-03 by deviceio121's frame from MGM's official clip (issue #9) |
| 16 | The 13th Warrior | The Visitors (1993): headless knight standing in a meadow |
| 23 | Valerian | Guardians of the Galaxy (2014): Nova Corps command table over Xandar |
| 27 | The Lost Boys | Terminator 2 (1991): biker-bar boots on wet asphalt at night |

Three panels stay `confirmed-community` rather than `confirmed`, because the still
alone did not give me an independent match and I am relying on the issue #9
sources (YouTube / IMDb / blog stills cited there): panel 9 Spartacus, panel 13
Leon: The Professional, panel 24 Close Encounters of the Third Kind.

Panel 8 (The Goonies) and panel 26 (Sharknado) were already agreed and hold at
the frame: trench-coat men, umbrellas, coloured mailboxes and a cargo ship in
Astoria; John Heard at Fin's bar under the SANTA MIRA BEACH 1986 poster.

## 1. The title-to-word rule, now only The Goonies is wordless

Under a literal substring scan, five community titles yield no English BIP39
word: The Goonies, Leon: The Professional, Sharknado, Raiders of the Lost Ark,
The Shining.

Under the unique 4-letter BIP39 prefix scan of the title with spaces removed,
four of those five resolve: Leon -> `profit`, Sharknado -> `share`, Raiders of
the Lost Ark -> `soft` (the compact string `raidersofthe` contains `soft`),
The Shining -> `shine`. Barry Lyndon is `bar` / `barrel` either way. That leaves
**The Goonies as the only title with no BIP39 reading of either kind**.

What would confirm a Goonies word: a single rule that also produces the 33
already-read words, checked against the escrow with `tools/oracle.py` once the
24-word set is assembled.
What would kill a candidate Goonies word: a full 24-word mnemonic that uses it
and still returns NO MATCH under every remaining intruder rule. That is not a
bounded exhaustion.
Cost: an insight; no compute action available that stays under two hours without
a rule that first shrinks the 10-intruder set.

## 2. The IMDb metadata field that splits 24 keepers from 10 intruders

About 25 to 30 binary IMDb-field criteria were tried against the old film list
and refuted (`analysis/tested.md`). On 2026-08-22, timothy-barus reported three
exhaustive GPU sweeps on the community list (shares-a-year, released-2000-or-later,
ten-shortest-by-runtime), about 1.23 billion checksum-valid seeds, all empty
(his numbers, not reproduced here). SmallCakekoo reported 17 certificate/genre
pairings that select exactly 10 panels, all empty against a fixed word list.

A new certificate reading was tested on 2026-08-27: drop G, PG, and TV-14
(panels 7, 8, 12, 18, 24, 25, 26, 30, 31, 32), keep the rest, and vary the
short per-title word lists. 55,296 raw strings, 227 checksum-valid, 0 match,
uncertified (see `analysis/tested.md`).

What would confirm a field: an IMDb column that splits the reconciled 34-film
set into exactly 24 and 10, tested against the escrow once combined with the
word rule.
Cost: an insight; the Goonies word and this field are coupled, so a rule that
drops panel 8 is cheaper than one that keeps it.

## 3. Kubrick x5 plus Jean Reno x5 at two wildcards

The author's Nostr note names director and actors as the fields to read on IMDb. On
the consensus list exactly 5 films are by Stanley Kubrick (panels 2, 9, 17, 25, 33) and
exactly 5 star Jean Reno (10, 11, 13, 15, 16); together they are 10, and the split needs
panel 14 to be The Man in the Iron Mask rather than a sixth Kubrick, which is now
settled. The 24 keepers then contain three titles with no literal word (The Goonies,
Sharknado, Raiders of the Lost Ark). With panel 8 free over the 2048 words and panels
26 and 32 read as `share`/`tornado` and `soft`, the sweep is negative (3.1e6 raw
candidates, `analysis/tested.md`), and so is the widened-ambiguity version (1.0e9).

What remains is two free positions: (8, 26) with 32 in {`soft`, `ride`}, and (8, 32)
with 26 in {`share`, `tornado`, `ski`}, about 6.4e9 raw candidates and 2.5e7
derivations per pair, about 3 minutes each on one GPU with the shared 24-word engine.
Three free positions is 2048 times more and is not proposed.

What would confirm it: a MATCH on either pair.
What would kill it: both pairs empty with head, middle and tail witnesses recovered.
Cost: minutes of GPU; the enumeration and witness harness already exist.

## 4. Regional IMDb titles and AKAs for the wordless titles (issue #9, couldes)

couldes raised that IMDb pages differ by region, some carrying a subtitle. The word
step reads from the film, so a regional subtitle is not in the search space by default.
For the titles that yield no literal word, an alternate release title is the cheapest
place a word could hide: Sharknado's German title "Dark Skies" gives `ski`, which the
widened sweep already covers; The Goonies and Raiders have no such reading yet. No
confirmed channel to the author exists to ask.

## 5. Panels 9, 13 and 24 as the last identification risk

If any one of Spartacus, Leon: The Professional, or Close Encounters is wrong,
every word list built from this table is underivable. The issue #9 sources are
the next check, not another still-only pass.

## Community identifications, 2026-08 (issues #9 and #3)

Two readers who watched the films posted panel identifications, one with per-scene
notes (issue #9, garrou), one confirming two panels after re-watching (issue #3,
CryptoBlueprint), plus a full 34-title list with IMDb ids in the issue #9 thread.

**They close the two panels this folder had left open.** Panel 11 is Godzilla (1998),
the footprint scene, and panel 34 is The Human Centipede (First Sequence), which
settles the Dead Ringers / Human Centipede dispute in favour of Human Centipede.

**By 2026-08-27 the nine remaining disagreements are settled or narrowed as above.**
The full community list, with IMDb ids and the community's own title-to-word
reading, remains in `data/films_community_issue9.csv` as the alternative fork.
`data/films.csv` is now the merged canonical list.

---

# Prior on-device research notes (2026-08-29), preserved on sync

The solve above supersedes these notes; they are kept only because they record
what was tried on this device before the community solve landed.


## Community reading, recomputed word pool (2026-08-29, computational delta)

Going with the community readings first (per the table above), I rebuilt the
single-best 34-title sequence and recomputed, for every panel, the English BIP39
words that occur as a *literal substring* of the title (the rule the repo's
README established as the working hypothesis). Result, panel | candidate words:

```
 1 Die Hard | hard
 2 Paths of Glory | glory,path
 3 Aliens | alien
 4 Going Places | place
 5 Alien | alien
 6 Apocalypse Now | now
 7 Escape from Alcatraz | cat,escape
 8 The Goonies | NONE
 9 Spartacus | art
10 Mission (the Cruise spy film) | miss,possible
11 Godzilla | ill
12 Life of Pi | life
13 Leon: The Professional | NONE
14 The Man in the Iron Mask | ask,iron,man,mask
15 The Crimson Rivers | river
16 The Visitors | visit
17 A Clockwork Orange | clock,lock,orange,range,work
18 Star Wars: A New Hope | hope
19 Gravity | gravity
20 First Man | first,man
21 Solaris | solar
22 Blade Runner 2049 | blade,run
23 Guardians of the Galaxy | galaxy,guard
24 Close Encounters of the Third Kind | close,kind
25 Barry Lyndon | bar
26 Sharknado | NONE
27 Terminator 2 | term
28 Scream 3 | cream
29 The Matrix Reloaded | load,matrix
30 Toy Story 2 | story,toy
31 Ghostbusters II | bus,ghost,host
32 Raiders of the Lost Ark | NONE
33 The Shining | NONE
34 The Human Centipede (First Sequence) | first,human,man,tip
```

Two structural observations, both of which argue the *substring* rule is only a
rough proxy and the real title-to-word transform is something else (synonym,
theme, key character, or an IMDb field):

1. **Five community panels still have NO substring word** (#8 The Goonies, #13
   Leon: The Professional, #26 Sharknado, #32 Raiders of the Lost Ark, #33 The
   Shining), up from four under the older pass. If the rule were pure literal
   substring, these five would need a non-literal treatment on top of the rule.
2. **Eight panels give only short, semantically-silly incidental substrings**
   (Spartacus -> art, Godzilla -> ill, Barry Lyndon -> bar, Terminator 2 -> term,
   Ghostbusters II -> bus/host plus ghost, Going Places -> place, Mission ->
   miss/possible, Blade Runner -> run). A human puzzle author is unlikely to have
   minted an 24-word mnemonic built from words like "art", "ill", "bar", "term",
   "bus", "host", "place". That these occur as accidental substrings is strong
   circumstantial evidence the intended rule is *not* blind substring.

Consequence: a C(34,10) reduction via `tools/oracle.py` still cannot be run
faithfully, because (a) the 34-word sequence is incomplete (5 zero-word panels),
(b) the word rule is not pinned by substring, and (c) the intruder-10 field is
unsettled. The substring sweep is therefore NOT worth running on this community
reading yet; the compute budget is better spent closing the film IDs / word rule
first, exactly as the README already warns. Verified 2026-08-29: escrow still
funded (100,000 sats), oracle `SELFTEST OK`.

## OSINT reconciliation and a de-risked negative (2026-08-29)

The community-resolved 34-title list, with IMDb ids and the thread's title-to-word
reading, is preserved verbatim as a fork at `data/films_community_issue9.csv` (next
to the repo's older `data/films.csv`); either can be fed to `tools/oracle.py`.

Community thread `gh issue #9` (deviceio121, SmallCakekoo, couldes, timothy-barus,
2026-08-21/22) advances this puzzle well past the repo's `data/films.csv`:

- **Panel 4 is settled as Mad Max** (community self-corrected away from "Going
  Places"; IMDb mediaviewer proof for Mad Max; deviceio121 agreed). This matches
  `films.csv`.
- **Panel 30 is settled as Toy Story 2** (couldes + IMDb proof; word is `story`
  either way).
- **timothy-barus independently confirmed the substring/prefix/stem/cross-token
  word rule** for the other 31 panels (identical to what I derived on-device in
  2026-08-29) and proved **The Goonies, Leon and Sharknado have NO BIP39 word** as
  substring/prefix/stem/  token-join - so those three are the genuine remaining gate
  of the *word* problem.
- **timothy-barus already swept the IMDb-metadata intruder space exhaustively on a
  GPU**: three exact-10 rules (shares a release year; released >= 2000; ten
  shortest by runtime) give 1.23 billion checksum-valid seeds across all word
  choices, all zero hits (`m/84'/0'/0'/0/{0,1,2}` vs escrow hash160). Two further
  exact-10 rules (pre-1980; ten longest) leave a third panel wordless and are
  2048^3 beyond reach.

### New on-device contribution (2026-08-29)

I proposed simple, non-substring words for the three wordless films, on the
author's own hint ("no complex calculations", "something simple"): The Goonies ->
`never` (iconic tagline "Goonies never say die"), Leon -> `lion` (the hitman's
name is a homophone of the BIP39 word lion), Sharknado -> `tornado` (portmanteau's
second half, itself a BIP39 word).

Then, for each of the three already-swept intruder rules, I re-derived the 
24-keeper sequence with these three words **fixed** and exhaustively varied the
word choice on every multi-word panel (glory/path, miss/possible, man/iron/mask/ask,
orange/clock/lock/range/work, man/first, blade/run, galaxy/guard, close/kind,
day/term, matrix/load, story/toy, human/first). Using the local certified oracle
(`tools/oracle.py`, BIP84/49/44 + 3 raw paths):

| Intruder rule (filmed panels dropped) | Word combos | Checksum-valid 24-words | MATCH |
|---|---|---|---|
| shares a release year (4,5,6,7,11,14,18,19,24,26) | 2560 | 9 | 0 |
| released >= 2000 (12,15,19,20,21,22,23,26,29,34) | 640 | 2 | 0 |
| ten shortest by runtime (2,4,15,16,19,21,26,30,31,34) | 2560 | 20 | 0 |

Scope of this negative, read honestly: it does **not** independently cut the
search space, because timothy-barus's GPU sweep already gave panels 8 and 13 a
**full 2048-word wildcard** under these exact three intruder rules and found zero
hits. My specific `never`/`lion` values for panels 8/13 were therefore subsets of
an already-exhausted space under these rules; the local run re-verifies that on
this device's oracle but adds no new exclusion there. Note all three intruder
rules drop panel 26 (Sharknado), so my `tornado` word is a *keeper-excluded*
panel here - its correctness is untouched by this test.

The genuinely open compute remains only under the two other exact-10 rules the
community found (`pre-1980`, `ten longest`), which keep Sharknado as a _keeper_
and leave three panels (8, 13, 26) wordless - a 2048^3 wildcard that is out of
reach on this device or any single GPU. The puzzle, on every clean evidence
path, now reduces to one non-computational ask: **cracking the simple title-to-word
transform for exactly The Goonies, Leon: The Professional, and Sharknado**, per
the author's "no fancy cryptic enigma, no complex calculations". My on-device
phonetic/thematic guesses (`never`, `lion`, `tornado`) are reasonable and simple,
but they are not yet placed under a rule that keeps them as meaningful keepers.

## IMDb plot/review text pass (2026-08-29) - refined candidates

Checked the "additional information on IMDb" angle via the films' IMDb plot
summaries (IMDb pages are gated in this environment; synopsis content pulled via
search-snippet retrieval of the IMDb plotsummary text; Wikipedia/TMDB/RT plots used
as cross-checks - content matches IMDb's synopsis).

Findings for the three wordless films - the concept word most grounded in the
plot text:

- **Leon: The Professional** -> **orphan** (BIP39). Multiple synopses call Mathilda
  "Orphaned by the massacre"; she and her brother are children. This is a stronger
  *plot-grounded* candidate than the homophone `lion` (which is title-grounded).
  Other BIP39 plot words: child, love, city, song ("Shape of My Heart"), school.
  (`cleaner`, `plant` are NOT in BIP39.)
- **Sharknado** -> **tornado** (BIP39). The plot is literally about a shark-filled
  tornado ("A tornado throws shoals of sharks onto the boat", "three tornadoes
  develop", "sharknados"). Confirms the portmanteau-half reading.
- **The Goonies** -> **chunk** (BIP39, a named main character, recurring in the
  plot) or the setting word **cave**/**tunnel**/**ship**/**beach** (BIP39). Character
  `chunk` remains the strongest; `sloth`/`data` are NOT in BIP39.

This does not yet crack the seed (still need all 24 keeper words + the correct
intruder rule jointly), but it upgrades the believability of `orphan` for Leon and
strengthens the case that the rule is concept/plot-grounded rather than substring.
The three plot-confirmed words (orphan, tornado, chunk) are a concrete hypothesis
to hand to whoever reconciles the remaining panels or re-runs a full 34-word
conceptual seed.

### Systematic BIP39 scan of the review/plot text (2026-08-29)

Ran the full 2048-word BIP39 list against the plot/review text of the three
wordless films (with light stemming, e.g. "Orphaned" -> `orphan`). Distinctive
words (generic fillers removed), per film:

- **The Goonies**: `chunk` x6 dominant (named main character), plus brand, beach,
  cave, ship. -> **`chunk`**
- **Leon: The Professional**: `orphan` (from "Orphaned by the massacre"), plus
  twelve, family, city, lonely, escape, love. -> **`orphan`**
- **Sharknado**: `tornado` x4 dominant (the film's literal subject), plus giant,
  huge, boat, ocean, wave. -> **`tornado`**

Caveat, stated honestly: these words appear because they ARE the films' core
subjects/anonymous characters, so scanning confirmatory text re-finds what the
concept hypothesis predicts rather than discovering something independent. Value:
it pins a concrete, self-consistent three-word reading (Goonies=`chunk`,
Leon=`orphan`, Sharknado=`tornado`) that a human can carry into a full 34-word
re-derivation, replacing the earlier (lion/tornado/chunk) set with `orphan` in the
Leon slot.
