# Leads, in full

## 1. Retry the West lock (`wt1jy`) in Title Case

The puzzle-wide "always lowercase" assumption is refuted (see analysis/tested.md): the site
is case sensitive, and the South branch's passwords are Title Case. About 1,560 of the
roughly 2,100 West candidates tried so far were submitted almost entirely in lowercase, on
the strength of that now-refuted assumption. The Title Case form of the same candidate list
has not been meaningfully tried. This costs minutes: it is a re-submission of an
already-generated word list with the case changed, not new research. Confirmed if any
candidate opens the page; there is no clean way to kill this lead short of trying it, since
the case question was never actually tested on this specific gate.

## 2. Retry the East lock (`c2ozw`) on the exact Gandalf "does not end here" phrasing

The East riddle chain traces a "Rime of the Ancient Mariner" retelling crossed with a
Fellowship of the Ring beat: the semaphore-decoded password on an earlier page,
`youshallpass47`, is a direct reference to Gandalf at the bridge of Khazad-dum, and the
locked page's riddle text ends on "is this the end?", which matches Pippin's line to Gandalf
after his fall and return, the well known film reply beginning "End? No,...doesn't end
here." The exact phrasing of that line as a password has not been tried; variants that were
tried and failed are
`gandalfthewhite`, `theturnofthetide`, `flyyoufools`, `mithrandir`, and `endno`. Costs
minutes.

## 3. Reverse image search the `LifeFlashBeforeEyes.mp4` clip stills

This video sits on `pxsqo`, the page immediately before the locked `c2ozw` gate, and shows a
sequence of memory-like clips: a couple pointing at the sky, a woman in a white dress on a
dune, yellow flowers, a campsite, pizza on a boat. If any of these frames is a still from an
identifiable film or music video, that title is a strong candidate for the East password.
This has not been attempted; it needs a reverse image search tool and costs on the order of
an hour.

## 4. Treat the South lock (`b3vye`) as the branch's master key, with a fresh reading of its pun

Opening `b3vye` is worth more than opening West or East, since its password also opens the
entire downstream South chain (a further "escape the island" sequence of pages) in one step.
The full enumerable Gilligan's Island canon (radio pilot, opening and closing credits, reunion
films, animated spinoffs, comics) has been checked with no hit, so the answer is more likely
an off-canon play on the page's own slug,
`havingfunwiththeurl-ilovedthisshowasakid` ("having fun with the url, I loved this show as a
kid"), possibly following the same style of planted, deliberate detail the author used on the
West riddle (the misspelling "unbridaled"). This is the highest-value lead but has no bounded
cost: it needs a new interpretation of the pun, not a longer list of candidates. A community
Reddit thread on this hunt (88 comments) contains one reader's guess ("use a different
title"), explicitly not an author-confirmed answer, and it did not lead anywhere when tried.

## 5. The page URL slugs (locations) are a live, under-read clue channel (NEEDS NEW READING)

Reading the site's own routing table (pageId -> title -> pageUriSEO) turns up three
facts not previously recorded anywhere, so they qualify as genuinely missing clues:

- The South lock's real location is longer than the author-post quote:
  `havingfunwiththeurl-ilovedthisshowasakid` is missing a trailing
  `-sosomuch`; the live slug is `havingfunwiththeurl-ilovedthisshowasakid-sosomuch`.
  The "sosomuch" doubling reads as the author emphasizing "I loved this show as a kid,
  so so much", still consistent with an off-canon wordplay answer, but it may itself be
  a token the author expects a solver to notice.
- The East lock `c2ozw` is titled `resurface` and its location is `take-a-big-breath`
  (neither appears in any clue file). The East branch's open-page locations are all
  cultural-song quotes (`celine-dion`, `weallliveinayellowsubmarine`), confirming the
  "forced cultural quotation naming a BIP39 word" channel in mechanism.md, of which
  `take-a-big-breath` is the next (locked) example.
- The West lock `wt1jy` is titled `a message` and its location is `message`.

Each lock's own slug was tested as a password (with and without dashes / expanded) and
did not open it, and slug-as-password is refuted generally because the open South page
`neyhh` opens with `Gilligan`, not its slug `name-1`. The value of this channel is
therefore not "the slug is the password" but that the locations are author-chosen
cultural references worth mining (especially the musical ones on the East branch) and
that the South slug needs re-quoting to include `-sosomuch`.

## External help

I have not contacted the band or its community about this puzzle. The site's own "get hints"
mechanism only covers the first 3 introductory steps (the EXIF coordinates and the compass),
all of which are already solved; it does not reach the 3 insight locks, so it offers no
lever here even if used.
