# R-POSTCAP-RESWEEP-2026-10-19 — post-cap creator window: on device after all, swept null

Scoping + resweep row for the post-2026-05-28 creator window. Motivation: two standing rows
scope their negatives to IDs ≤ 63966 — `R-CORPUS-COVERAGE-2026-10-08` F1 ("anything after
#63966 is absent from every local text corpus") and the 2026-10-16 topology row ("the gap is
exactly sixteen creator replies … unrecoverable until an export covering 2026-07-13 and
2026-07-17 exists"). Both are correct for the corpora held **in this repository**; both are
wrong device-wide.

- F1 - THE POST-CAP CREATOR TEXT IS ON DEVICE. `~/gsmg-research/remote/content__sowut-data.js`
  (sibling workspace, fetched 2026-10-11, generated 2026-09-22) holds **65 verbatim creator
  messages with ID > 63966**: 2026-07-13 / 2026-07-16 (55) and **2026-09-01 (10, IDs
  70307–70377)**. All 65 are annotated in that workspace's `CREATOR-LOG.md`. The topology
  file's sixteen-reply inventory is a strict subset (16/16 contained); the other 49 are
  standalone messages — including #66568 (hidden laptop), #66573/#66574 (close friends,
  "NOTE: that is a hint"), #66593 ("5 btc was never the actual prize"), #66600 ("some
  already found it").
- F2 - TEN IDS SIT BEYOND THE OVERLAY BASELINE. 70307–70377 (2026-09-01) exceed
  `GSMG_TELEGRAM_EXPORT_OVERLAY_BASELINE.md`'s end (70186 / 2026-08-30): #70307 "Pfff.
  Coincidence.", #70336 "Couple hours, and no.", #70377 "Same same". Post-2026-05-28
  creator coverage therefore runs to **2026-09-22**, not to 2026-07-16 and not to 70186.
- F3 - SOURCE PROVENANCE + BYTE IDENTITY. Origin located: `https://hosterjackagv.github.io/
  gsmg-5btc-puzzle/content/sowut-data.js` (repo last commit 2026-09-22, "Add the Creator
  log: every @SoWut Telegram message, annotated"). Fetched 2026-10-19, **byte-identical to
  the local copy** (sha256 `db76ac2eb8901478…`, full-string compare). Because the source
  bills itself as *every* @SoWut message, the id windows **63967–66539 (2026-05-28→07-12)
  and 66977–70306 (07-17→08-31) are creator silence**, not missing data — the "sixteen
  replies or nothing" framing should read "sixty-five messages, complete through 09-22".
- F4 - RESWEEP OF THE 65 TEXTS: NULL. Family regexes (`satan/santa/natas`, `lilith`,
  `demon`, `avesatana`, `dualit`, twenty-three-ciphers menu, ciao/bella/bye/keynote tail,
  guide-be, prime) over all 65 texts yield exactly 2 matches, both non-substantive (#66609
  Ibiza banter containing "ciao"; #66931 "You have to be in your prime for that", a pun).
  Candidate build: every text in raw / lowercase / alnum-collapsed / whitespace-normalized /
  sentence-split forms plus 30 explicit phrase forms from the new lines → **406 candidate
  lines**. Gate (the community clean-set three-envelope PKCS7 sweep, same gate family as
  recent rows): selftest PASS immediately prior, then `406 candidates; pad>=3: 0; strong: 0;
  flukes: 7 (~chance); DBBI-L5: 0; keyhits: 0` (rc=0). Session total for the day across two
  sweeps: 619 candidates, 0 pad≥3, 0 L5, 0 keyhits.
- F5 - REMAINING WINDOW IS MANUAL-ONLY. Dead routes verified 2026-10-19: `t.me/s/SoWut` and
  guessed public usernames return the private-contact page (no preview); the group is
  invite-only (invite link on gsmg-archive.org); the full-ChatExport route stays closed per
  `R-EXPORT-SEAM-CLOSED-2026-10-09`. The only uncaptured window is **2026-09-22 → present**,
  reachable only by a human joining the group. Issue #114's ask is satisfied by this device
  for everything ≤ 2026-09-22; Naddiseo's 2026-10-09 reply ("just do it manually … highly
  likely that the passwords … can be derived from within that page itself") stands as the
  maintainer's position.
- WITNESS. The corpus claim rests on the byte-identity compare (F3, sha256 over both full
  files, equal). The sweep negative rests on the gate selftest controls run immediately
  prior (pad1→fluke, pad4→weak, pad16→strong, L5-pattern PASS) with the candidate file
  hash-pinned beside the session record. Escrow re-checked same day: `1GSMG1JC9…`
  125,635,374 sats partially-spent OK; `17ucy1K9…` 375,055,856 sats funded-unspent OK.
- COUNT: 406 candidates, 2436 decrypt attempts (406 × 3 envelopes × 2 profiles), 0 pad≥3,
  0 L5, 0 keyhits, 0 oracle-or-escrow contact beyond the read-only checks above. No
  historical rows edited (`tested.md`/`leads.md` were left untouched — they carry
  uncommitted work from another session; this standalone row carries the delta instead).
  Date 2026-10-19. Cross-refs: `R-CORPUS-COVERAGE-2026-10-08` (F1 stale device-wide),
  `R-EXPORT-SEAM-CLOSED-2026-10-09` (unchanged), the 2026-10-16 topology row (F1's
  "sixteen replies" now a subset), issue #114, LEAD-0 crux unchanged (`dbbib_91`/`faed_570`
  decode under the authored interpreter board).
