# Open leads: Bitaps Shamir secret-sharing challenge

Full notes. The README shows the ranked summary.

## 1. The archive gap around funding (2020-06-19)

The challenge page shows only the same 2 shares in every archived capture I can reach. As
of 2026-08-28 I have now confirmed this at the earliest bound of what was previously the
"15-day gap": Common Crawl holds a capture of `bitaps.com/mnemonic/challenge` dated
2020-07-04 (CC-MAIN-2020-29, WARC record digest `VL2EUR4KXMBSCLVXAJN3VAYCO7WRVUPB`), and it
contains exactly the same 2 shares as every later capture. That closes the "after" side of
the gap. The "before" side (2020-06-19 funding/2-share publication through the days right
after) is still not covered by any archive I can reach. If a 3rd share ever appeared in
that window and was then removed, only an uncaptured mirror/screenshot/forum post of that
specific window could reveal it; none has surfaced so far.
Cost: an afternoon of searching alternative archivers; no compute.

## 1. The unpublished 3rd share (author-held)

The scheme is 3-of-5. Two shares were published on 2020-06-19 and every later public
copy agrees on those two. The remaining shares were never posted in any channel I
could read. Same-day copies (Reddit, Telegram, X) already show only 2 shares, and the
2020-07-04 Common Crawl body (`challenge.warc`) shows the same pair, so a
"posted then deleted during the 15-day Wayback gap" story now has to explain why the
parallel announcements and the first crawl never carried a 3rd share either. What would confirm it: the
author publishing a 3rd share, or a dated copy of the challenge page that disagrees
with the 2-share text. What would close it: that still has not happened. Cost:
watching the author's remaining channels; no compute.

## 2. Memento TimeTravel, and the rest of the X reply tree

archive.today returned HTTP 429 on its own known-good witness page when I tried it
(2026-08-03), so I could not tell whether it holds anything for this challenge; Memento
TimeTravel was unreachable the same session; I found no verified anonymous read route for
X replies to `@bitaps_com`; the GitHub forks of `mnemonic-offline-tool` (23 as of
2026-08-28, most auto-generated) have not been individually reviewed for a diverged share
but the early ones show no divergence; and Telegram's `t.me/s/bitapscom` public preview
has not been read. None of these are established as empty, only as not yet checked with a
working method. What would confirm or kill each: a working read of the channel that either
surfaces a 3rd share or comes back clean with a witness proving the read method works.
Cost: minutes to hours per channel, no compute.

## 3. Direct computation

Not ranked as a lead. The residual entropy is about 125 bits (see
`data/entropy_measurements.csv`), which is not in range for search on any hardware I have
access to. This door is closed by the numbers, not by assumption.

## 4. Independent confirmation of unbreakability (recorded 2026-08-28)

Multiple independent researchers (matuta99, onvej-sl, Christopher Reid, the `oritwoen/boha`
project) independently conclude the challenge is information-theoretically secure with 2
shares of a 3-of-5 scheme: the known implementation quirks (coefficient bias, undefined
`igam` randomness self-check, degenerate second coefficient) do not reduce the residual
search space enough to brute-force. The 3rd share has never surfaced in the github
bug-bounty issues (62 issues on `jsbtc`, many 2025-2026 512xx-bounty reports) either. This
is the strongest available evidence that the only winning path is finding the 3rd share.
Meaning: this challenge is, on present evidence, effectively unsolvable - record this
honestly rather than cycling compute on ~125 bits.

## 2. Uncertified channels

archive.today returned HTTP 429 on its own known-good witness page when I tried it
(2026-08-03), so I could not tell whether it holds anything for this challenge; Memento
TimeTravel was unreachable the same session; I found no verified anonymous read route for
X replies to `@bitaps_com`; the GitHub forks of `mnemonic-offline-tool` (13 as of
2026-08-03) have not been individually reviewed for a diverged share; and Telegram's
`t.me/s/bitapscom` public preview has not been read. None of these are established as
empty, only as not yet checked with a working method. What would confirm or kill each:
a working read of the channel that either surfaces a 3rd share or comes back clean with a
witness proving the read method works. Cost: minutes to hours per channel, no compute.

Memento TimeTravel (`timetravel.mementoweb.org`) did not resolve on 2026-08-28 (DNS).
That aggregator is still unread. The X announcement was re-read, including the 3
replies returned with the post; one of those (2025-05-14) asks the author to reveal
1 or 2 words of the third share, and there is no author reply among those 3. A fuller
reply listing might still exist off that truncated view. What would confirm or kill
each: a working Memento read of the challenge URL, or a complete reply listing for
status 1274018817304379394 that either surfaces share words or comes back clean with
the known announcement text as witness. Cost: minutes, if the services answer.

## 3. Direct computation

Not ranked as a lead. The residual entropy is about 125 bits (see
`data/entropy_measurements.csv`). Every 2-share model that actually determines a
secret, or a 2^16 mix of two such models, is now tested and negative
(`analysis/tested.md` section 12). What remains is the unconstrained byte, which is
not in range for search on any hardware I have access to. This door is closed by the
numbers, not by assumption.

## Closed this round (2026-08-28)

The 15-day Wayback/Common Crawl gap is no longer an independent source of a hidden 3rd
share: the gap is still empty in those two indexes, but same-day Reddit and Telegram
copies exist, archive.today's one snapshot (2021-06-20) matches, and the live pages on
2026-08-28 still match. The Common Crawl payload itself is now in-folder
(`challenge.warc`, 2020-07-04T18:20:40Z) and carries the same 2 shares; the same-day
mnemonic tool WARCs (`tool-en.warc`, `tool-ru.warc`, `offline.warc`) have empty restore
slots. `offline.warc` is truncated at Common Crawl's 1 MiB cap inside the BIP39
dice wordlist (255 words, `abandon` through `cabin`); the split/restore UI is
above that cut and fully present. archive.today, Telegram `t.me/s/bitapscom`, the 13 reachable GitHub forks of
`mnemonic-offline-tool`, and the live regional mirrors are now read, not merely
uncertified. Determined 2-share algebraic models (unique coefficients, global `a1`/`a2`,
constructed 3rd shares, mixed 2^16 families) are negative. Details in
`analysis/tested.md` sections 7 to 13.
