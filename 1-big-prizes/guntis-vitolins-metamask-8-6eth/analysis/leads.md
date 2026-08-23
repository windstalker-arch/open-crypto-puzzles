# Open leads, full notes

Ranked summary is in the README. This file has the reasoning behind the
ranking. All 3 leads below are priced and specified; none has been run.

## 1. Extend the swept word pool with connecting words (liaisons)

Every completed sweep (`analysis/tested.md`) draws its non-anchor words from
full words in the 5 planted sentences and confirmed metadata (tags, title,
hook line). None of them include short connecting words from the same
sentences: prepositions, articles, and conjunctions such as "there", "will",
"also", "you", "more", "can", "then" (video side) or "only", "because",
"there", "like" (post side). These words are cheap to add: the private
research's own P2 estimate, before the metadata extension, priced this
addition at 15/14 words per side, 1.36x10^10 derivations, about 3.8 hours on
one GPU. Extending the already-metadata-inclusive R1 pool the same way is a
comparable-sized addition.

What would confirm it: a match within the extended set.
What would kill it: exhausting the extended set with 0 match, the same witness
protocol as every prior sweep.
Cost: hours on one rented GPU.

## 2. Extend further to substrings of longer words

The author, asked directly whether a list word could be hidden inside a
longer written word, answered yes and gave "possible" inside its own
negation, formed with the prefix "im-", as his own example, though the
surrounding conversation suggests he may have
meant the paraphrase-hint mechanism rather than a substring mechanism (see
README, "What is understood"). This is confirmed as an open question, not a
confirmed mechanism. If it is real, plausible substrings already identified in
the source texts include "cat" (cattle), "ill" (will), "hen" (then), "like"
(likely), "cause" and "use" (because), "health" (healthy), "hunt" (hunter),
and "inner" (dinner). The private research's own P3 estimate for a
substring-inclusive sweep, before the metadata extension, was 21/20 words per
side, 2.78x10^11 derivations, about 77 hours on one GPU (later re-priced
downward once a faster kernel was validated at 792,000 derivations/second).

What would confirm it: a match within the substring-extended set.
What would kill it: exhausting it with 0 match.
Cost: on the order of a day on one rented GPU at the validated 792,000
derivations/second rate; re-price before running, since kernel throughput
changes this estimate directly.

## 3. Read the video and post one more time for a metadata-style hidden word

If leads 1 and 2 both return negative, the most likely remaining explanation
is that one word lives in a part of the source material not yet identified as
a metadata surface, the same way the blog post's tags were missed until
2026-08-15. The video's own metadata (its tags, description formatting, or
on-screen text) and the post's remaining unread surfaces (any HTML attribute
resembling `article:tag`, image alt text) have not been re-examined with the
same "check every metadata field" method that found `fork` in the post's tags.

What would confirm it: a new word found in an unexamined metadata field,
tested through `tools/oracle.py` after being combined with the already-mapped
words.
What would kill it: a full metadata re-read producing nothing new; there is no
natural exhaustion point for this lead beyond a careful, complete pass.
Cost: an hour of directed reading, not a sweep.

### Status: executed 2026-08-23; it found new words

Both 2020 Wayback captures were re-read field by field (`20200626184951` for
the video, `20201026062858` for the blog). Surfaces never previously read as
word sources:

- the video page's `keywords` meta element (YouTube's own tag field):
  "mining rig, mining hardware, guntis vitolins, bitcoin, ethereum, top
  altcoins, altseason, portfolio, altcoins for 2020, bitcoin generator".
  Filtered against the BIP39 list, nothing new: none of these are dictionary
  members beyond already-pooled `top`;
- the video description's formatting layer: 26 identical `hole` emoji
  characters (U+1F573) framing the contact and link blocks, plus the literal
  strings "Follow me", "Signup", "Share this Video", "Telegram chat". New
  BIP39 members among these: `hole`, `share`, `chat`;
- the blog `<head>` `og:description` ("Crypto is of the chain... what 2020
  will bring... it should be a good year... if they not going to act as soon
  as possible they might be left"): new BIP39 members `possible`, `bring`,
  `good`, `act`, `soon`, `left`, `month`, `year`. Notably `possible` is the
  very word the author used in his own substring example;
- the blog `<title>` element and site categories: nothing additional beyond
  pooled `update`.

New candidates by source side:

| Side | New candidates | Source |
|---|---|---|
| video (6-word half) | `hole`, `share`, `chat` | description emoji framing and link-block labels |
| post (6-word half) | `possible`, `bring`, `good`, `act`, `soon`, `left`, `month`, `year` | og:description |

The `hole` finding has a second reading worth recording: 26 identical emoji
are also a countable marker. If they are a tally rather than a word, they may
index a position or pick between the `fog`/`cloud` branches instead of
contributing a list element.

Sizing an exhaustive sweep with all 11 additions under the R1b protocol
(anchors fixed, `fork`/`fiber` floating) prices out above the R1b run itself
(10.75 billion derivations, about 4.5 hours on the validated GPU kernel).
Treat it as the next GPU-priced run alongside lead 1's liaison extension;
it is not phone work.

## Community correction: R1 pool provenance (issue #10)

HPreziosa (issue #10) grepped the 2020 Wayback captures of the video and blog and reports
that three words in the R1 pool are mis-sourced in the "title and hook line" row of
`tested.md`:

- `top` is not in the video title or og:description; it appears in the blog body ("top ten
  altcoins") and in the video description trailer ("top mining equipment").
- `finish` does not appear as a bare stem; only `finished` does, in the og:description
  ("Crypto Winter finished?"), so it is a morphological derivative, not a literal.
- `cloud` appears in no authored 2020 surface; the README itself says only `fog` and `lake`
  do, yet still carries `cloud` on semantic grounds.

Verified against the archives on 2026-08-21 (Wayback `20200626184951` of the video,
`20201026062858` of the blog), all three confirmed:

- the video title is "10 ETH challenge | Ethereum Parabolic | Bitcoin generator portfolio
  update !?"; `top` is not in it. `top` appears only as "top altcoins", "top mining", and
  "top supporting" in the video description, and as "top ten altcoins" in the blog body.
- the bare stem `finish` appears in neither surface; only `finished` does, nine times in the
  video ("Crypto Winter finished?").
- `cloud` has zero occurrences in either the video or the blog.

Consequence for the pool: `top` and `finish` stay in the corpus but are re-sourced (the
description and the blog body, not the title; `finish` as an inflection of `finished`). More
usefully, since `cloud` is in no authored 2020 surface while `fog` is ("dark fog on the
lake"), position 5 resolves to `fog`, and `cloud` is dropped as a candidate.
