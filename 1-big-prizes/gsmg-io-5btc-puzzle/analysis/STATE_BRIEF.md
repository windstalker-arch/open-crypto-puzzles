# GSMG 5-BTC Puzzle - Solve-State Brief (2026-09-24, addendum 2026-09-27)

> **VERIFIED STATUS (2026-09-27, `R-VERIFY`).** The certified chain below is no longer a set of
> recorded claims - it has been **re-derived from first principles and re-verified**: run
> `python3 tools/verify_ladder.py` (41 checks, exits 0). The whole ladder follows from **canonical
> BLOB1 + RAW_PW** alone, including `WIF(K_C1)` being the BLOB2 password, so the chain closes on
> itself. All five opened envelopes confirm by **exact re-encryption round-trip**. All four ladder
> addresses re-derive and **all four differ from both funded gates**. No key recovered; both gates
> open; that null is now verified rather than assumed.
>
> **One identifier was corrupted in a session summary and is corrected here:** `ADDR_C2` =
> `135Cf6ASyU2PDHuxA1Edc3mHYtxEsZNPCa` (34 chars, h160 uncompressed
> `16bba55c93148e78ce946caad0115bb8248f2f09`). A 33-char `...ASy2PD...` form has circulated in
> summaries; it is a dropped `U` and appears nowhere in the artifacts. If you reuse any identifier
> from a summary rather than the ledger, re-derive it once.
>
> **Cheap leads are exhausted.** The `abbaabab...` residue is a certified author-page artifact
> (`R-DIGRUN`), the 1539-byte period-15 blob has failed three independent parameterisations under
> proper held-out testing and a corpus-wide sweep found no second ciphertext, and the phase-3.2 prose
> is closed by `R-EBCDIC1141` plus the FINDING 3/5 rows. Exactly **one** direction survives from
> `R-P32BLOB`: treat the 26 byte-values as non-alphabetic data (base-N / bit-packed). It is
> expensive, speculative, and unguided. The remaining gap looks **interpretive, not mechanical**.


One-page onboarding for any solver/agent/contributor. Companion to `AUDIT-2026-09-20.md`
(invariant + certified-boundary audit) and `analysis/leads.md` (ranked, dated leads).
Ledger: `analysis/tested.md` (all rows below).

## The situation

gsmg.io (2019), 5 BTC split across two funded gate addresses. All *solved* stages were
solved by 2021. We certify ORACLE-level negatives for every mechanical decode family; the
single live crux is Lead 0 = the **interpreter-alphabet leap**. Both gates remain OPEN.

## Gates (live-verified 2026-09-24)

| Gate | Address | Balance | Target pubkey X / h160 |
|---|---|---|---|
| small | 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe | 125,634,510 sat (1.2563 BTC) | f4d1bbd9...55d5a464 / a9553269572a317e39f0f518cb87c1a0ee1dbae4 |
| dualite | 17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa | 375,055,856 sat (3.7506 BTC) | - / - |

Each gate: candidate answer X must satisfy BOTH legs of its oracle
(`tools/oracle.py` small / `tools/oracle_dualite.py` dualite), which try
`salted__`-CBC-EVP decryption under `md5` and `sha256`, raw-X and `sha256(X)`-hex legs,
and P2PKH(h160) address matching. `--selftest` must pass (rc=0) before AND after every run.

## Certified chain (the knot)

- Page textarea (pinned 2023-06-01): streams `dbbib` (91 tokens, {a..i}) = KEY-ish;
  `faed` (570 + z) = PAYLOAD-ish; a/b runs decode to `matrixsumlist` / `enter`.
- RAW_PW = `matrixsumlist + enter + lastwordsbeforearchichoice + thispassword + matrixsumlist`
  -> EVP-MD5 of small blob (salt 3ab585348552415d) -> B1_79B.bin (79 B, sha256 1449a217...);
  fields K_C1=9fa9db91..., K_C2, E_C; B2_79 sha256 b40fce72...; **E_S = B2_79[64:79] =
  740a25de4b8e946d0a5ae2667a23a2**.
- dualite blob (salt 2d3f6fe0, 1344 B) vía 7-token XOR key XK -> a795de11... -> 1327 B
  certified plaintext (sha256 4f7a1e4e...); binary-XK MD5 -> cosmic 1327 B.
- Certified VIC vector (community 3.2.2): alphabet `FUBCDORA.LETHINGKYMVPS.JQZXW`,
  escapes (1,4) -> plaintext `INCASEYOUMANAGETOCRACKTHIS...FUNDSTOLIVE`
  (reproduced by `tools/certified_vic.py`, SELFCERT).

Gate premise of the crux: E_S is the check on a phrase A produced by decoding the streams with
the **community-attested** keyed alphabet -> `sha256(A)[0:15] == 740a25de4b8e946`. Two corrections
to what this line used to say, both from 2026-09-27:
- **"the author's keyed alphabet" was wrong, and contradicted line 57 of this same brief**, which
  already labels the VIC vector "community 3.2.2". `R-FUBCD` established there is **no archived
  author witness** for `FUBCDORA.LETHINGKYMVPS.JQZXW` or the Phase-3.2 seed sentence: the exact
  board and every seed token return 0 across all 399 archive files. The vector is reproducible and
  self-consistent, which is not the same as authorial. Keep the two apart.
- **"64-bit" was simply a miscount.** The check is `sha256(A)[0:15]` = **15 bytes = 120 bits**, and
  `E_S` is 15 bytes by construction (`B2_79[64:79]`). 64 appears nowhere in this comparison.
- Also worth stating plainly, because it is implicit everywhere and explicit nowhere: **`E_S` is not
  a value to be found.** It is a slice of an already-certified decryption. The "E_S anchor" rows are
  *cross-validation* — looking for those 15 bytes independently — not a search for something unknown.

## Exhausted map (all oracle-certified 0 MATCH unless noted)

1. **Interpreter base-9/base-10 -> bigint -> hex -> ASCII**: all injective a..i->digit maps
   and orientations - excluded by the byte-ceiling bound + swept maps. CLOSED.
2. **Certified checkerboard** `build_grid/decode`: maps {pos, canon, page-typed a..i order,
   faedgcbhi, all reverses} × escapes {(1,4),(2,5),(0,4),(1,5),(2,4),(1,2)} × widths
   {none,3,7,13,15,16,19,23,38} × {dbbib, faed, concats, interleave} × 17+ alphabets
   (2,128 + 15,504 cells), plus the nest-escape axis (7 pairs derived from the FEFEFE
   cell (7,4), 54,264 cells). CLOSED (late-337/338/341, tools/vic_alphamap_grid.py +
   tools/fefefe_esc_battery.py).
3. **Keyword-keyed alphabets** (VIC family): 98 + 81 + 15 + 17 alphabets, all maps/escapes.
   CLOSED (row194, 3337, 4716).
4. **drop-g 463-token uniform-8 payload**: checkerboard + ciphertools 19-cipher menu sweep,
   slope readings, run-gaps. CLOSED (R-LEAD0-DROPG-463/-CT).
5. **Channel reads**: even/odd (2-bit+5-bit), 3-bit groups, first-occurrence interpreters,
   interleaves/remerges. CLOSED (late-187/190).
6. **Stream-construction**: alberti/keyed rings, sqshift, xorstr key-schedule, book-cipher
   triplets, concat/interleave (verbatim AND decoded). CLOSED.
7. **XOR-triangle / ca**: ylxc4 window-XOR msets, all chain pairings, N≈9.2M windows vs
   anchors cd3fea3d/c3b87356 - 0; ca not pairwise-constructible; chain4/mystery families.
   CLOSED (late-189, R-CA-WINDOWXOR/-XOR2, R-CA-FORMULA-BASED).
8. **Off-chain key reduction**: K-fields scalar/x-coord reads, EVP key/IV objects, XORs,
   BIP32 seedsx10 paths, x<->B1/B2 fields. CLOSED (late-192, R-E-ANCHOR-BATTERY).
9. **E_S preimage sweeps** (all 0 prefix-15 hits): pipeline cascades, yinyang (before/after
   open, 62+62 cands), genesis-block object family (276), drop-g windowed reads, issue#56
   vocab (42), fork-constructed half+enter+betterhalf (32), JRK prime-sieve 128-bit,
   brainwallet/decoy family, jacobian/phase-3.3/issue-56 vocab families, all external claim
   strings. CLOSED.
10. **Page-grid readings**: 14x14 colors = URL low-bit plane only; yinyang diagonal 91/91
    real but no yield; FEFEFE nest cell (7,4) decode-irrelevant. CLOSED. NOTE (2026-09-24
    live deep-check, R-SITE-SNAPSHOT-2026-09-24): the new shutdown homepage "SYSTEM
    FAILURE" animation carries a hardcoded 14x14 binary finalGrid re-rendering the SAME
    24-cell white-rabbit board (all 15 blue cells present, 0/9 yellow; P~3e-5) - an homage,
    not new data; /puzzle poster unchanged; site wind-down confirmed (register/help-center
    404, beta/help DNS dead, robots Disallow /).
11. **Community/external**: issues #2..#111, both Bitcointalk threads, SolvingGSMG/puzzle,
    Track-B (39237 post-edit text verified; pre-edit unrecoverable), Jrk Telegram histogram,
    2025-2026 "solution" claims (all fabrication-class). No bankable artifact. CLOSED.
    Issue #78's two pasted signatures ARE the puzzle key's (their only shared consistent
    pubkey is exactly Q) but they yield no `d`: the "140 bits of nonce bias" claim needs
    m >= 5 signatures and only 2 exist, and an exact two-sided BSGS finds no nonce
    difference up to 2^36 either way. Ledgered UNPROVEN, not a solve. See R-ISSUE78-HNP.

## The crux (Lead 0)

The streams are ciphertext under the author's **keyed 28-char alphabet** (with '.' and '/'
punct), which is the one unprovided input. All mechanisable guesses are exhausted; the
answer phrase also obeys a case/spacing requirement (insider-corroborated) that only the
sound decode can supply. Remaining forms are strictly **visual/layered reads** of the
SalPhaseIon page.

## What unblocks (pick any)

1. **Alphabet hypothesis** (any word/phrase) -> `tools/lead0_try.sh "<keyword>"`
   (or `--alphabet "<28 chars>"`) fires both gates immediately.
2. **A human visual read** -> `analysis/lead0-inspection-checklist.md`; live micro-items:
   the missing `.` marker, the lone `/`, the FEFEFE nest cell at grid (7,4).
3. **A new author artifact** - e.g. pre-edit Telegram snapshot (2025-04-28 20:01-20:20),
   restated "ca" formula text, or any post-2026-09-24 hint/statement.

No further battery is warranted without one of the three; per AGENTS.md we do not re-run
closed rows.
---

# Addendum 2026-09-26 (rows `R-LOGO2`, `R-PACKCRYPTO`, `R-PHASE2-2026-09-26`, `R-COVERAGE-2026-09-26`)

The crux is unchanged: **Lead 0's keyed 28-char alphabet is still the only live gate**, and
no battery below was widened. Four sessions' work closed negatives and removed process
risk. Three items change how you should work.

## 1. Run `tools/coverage_check.py` before writing ANY row

This project has produced four search-space failures, three of which made an absence look
like a fact and one of which nearly made an old page look like a discovery. Prose warnings
did not prevent any of them, so the check is now executable:

    python3 tools/coverage_check.py --selftest          # 4 controls, rc=0
    python3 tools/coverage_check.py ARTIFACT [...]     # rc=2 if the path is a ghost

It refuses coverage numbers for files that do not exist, refuses to call a zero an absence
without naming the term count behind it, greps the ledger for the artifact's content
vocabulary and diffs every working-dir copy before any novelty claim, and enforces 16-byte
block alignment on every OpenSSL envelope. Its own first selftest ranked 14 Base64
fragments as search terms and reported a confident zero; that failure is recorded in the row
because a guard never seen failing has not been tested.

## 2. The live/Wayback corpus is already organised - and contains a trap

Use `~/storage/external/briefcase/gsmg-puzzle/` (`live/`, `wayback/`, `pages/`, `img/`,
`img/ocr/`, `seedimg/`, plus 16 extracted binaries in `analysis/`), assembled 2026-09-06.

**TRAP.** The bare slugs `phase1`, `phase2`, `phase3`, `phase3_2_2`, `phase3_2_2_2`,
`architect`, `ca`, `hope1`-`hope4`, `whiterabbit` return the 9-byte body `Hello :-)`, while
the real pages sit in the sibling `.html` files (`phase2.html` is 10,243 B). The author
served `/puzzle/phase2.html`, not `/puzzle/phase2`. A sweep keyed on filename reads the
stubs as blank and reports five stages as empty while their content sits beside them. Sweep
by content, never by name. Related: the `wb2_*` files are stored gzipped and were never
decompressed here; 8 of 10 inflate to the generic SPA shell whose entire prose is `GSMG`.

## 3. Closed since 2026-09-24 (all permanent negatives, no oracle hits)

- **Phase-2 page is unchanged 2020->2026.** Five copies, all text-identical
  (`5fae3f80...`); both ciphertexts identical; zero drift in ~5.5 years.
- **Five unmeasured slugs are content-free:** `digilog`, `eps34`, `hope_full`, `hope_short`,
  `puzzlesupposethisone`. Their 0/0 ledger coverage is correct, not a gap.
- **Logo:** current blue/gold pair is a pure palette remap (alpha masks 100% identical); the
  gold file is a 2026 redesign, not a recovered original; the 2020 blue original is
  recovered and digest-verified at `~/gsmg-preserved/gsmg-site-assets/logo_medium_2020.png`;
  no stego in any of them.
- **Solver pack:** of 10 ciphertexts, 3 are author material (Cosmic Duality 1,344 B plus the
  phase-2 and phase-3 blobs, now identified by Base64 digest) and 7 are solver scratch.
  `cosmic_decrypted_verified.bin` is grade C - byte-exact but not authenticated.

## Still open, deliberately

- **Lead 0** - unchanged; needs the alphabet or a human visual read.
- **`wb2_ca` (10,035 B)** - NOT open. Already characterised by the corpus README: no
  `Salted__`, entropy ~7.979, not gzip/bz2/lzma/AES-CBC-aligned, no-salt EVP sweep 0 hits.
  My `R-COVERAGE` row wrongly listed it as uncharacterised because I inventoried the corpus
  by filename instead of reading its 30-line README first.
- **Pre-redesign favicon** (`R-LOGO2`) - CDX row exists, bytes never recovered. Not a blocker.
- **HNP #78** - parked at 2^140; not negative, just out of reach.

## Phase 2 -> Phase 3 chain: independently reproduced 2026-09-26 (`R-CHAIN23-2026-09-26`)

Both stages were re-extracted from the live page and decrypted from scratch; neither was
taken on trust. **Byte-exact** against `analysis/phase2_dec.txt` and `analysis/phase3_dec.txt`.

| stage | password | KDF | salt | ct | plaintext |
|---|---|---|---|---|---|
| 2 | `sha256("causality")` = `eb3efb51...` | EVP-SHA256 | `06286612d43ed7ed` | 656 B | 648 B |
| 3 | `sha256(<227 chars>)` = `1a57c572...` | EVP-SHA256 | `9fbc451d13d071f4` | 4,096 B | 4,090 B |

Conventions are uniquely pinned, not merely consistent: five of six phase-2 configurations
tried (hex digest / raw digest / literal, each under EVP-SHA256 and EVP-MD5) failed padding.

**All seven parts** (the page's "parts 1..7"): `causality`, `Safenet`, `Luna`, `HSM`,
`11110`, `0x736B6E...656854`, and a FEN. Part 6, read reversed, is
`The Times 03/Jan/2009 Chancellor on brink of second bailout for banks` - the Bitcoin genesis
coinbase headline, hex-encoded and byte-reversed.

**Six of the seven are DERIVED, not transcribed.** The decisive one is the FEN. The page
publishes the STARTING position (`6R1`, white to move, 14 legal moves); the password uses
`2R5`, black to move, in check with 1 legal move - the position AFTER the rook goes g6-c6+,
i.e. the puzzle's ANSWER. A FEN in a password is the post-move state. Pasting the page's
string verbatim yields plausible-looking wrong answers, and both FENs are `Status.VALID`, so
only the move count and check flag separate them.

**Phase 3.2 (salt `eefc4c5befc1656a`, 2,448 B) is structurally blocked, not search-limited.**
The obvious derivation was already tried and is the *correct* one
(`jacquefresco` + `giveitjustonesecond` + `heisenbergsuncertaintyprinciple` maps onto all
three riddles) and it returned nothing, so the password is not recoverable from the visible
clues - consistent with the 2026 capture being re-encrypted. No battery warranted per AGENTS.md.

## Yin-yang: RESOLVED POSITIVE 2026-09-26 (R-YINYANG-MARKER)

The authored yin-yang is the author's OWN polarity bracket on the PHASE 2/3 page, around the chess FEN:
`/(aBa, connected enf)` ... `/(aBa, connected not enf)` - one token, a predicate and its negation. It is the
ONLY polarity bracket in the corpus (D=4 marker pairs over 155 author-source files; `aBa` the sole dual-polarity
token), occurs exactly once, is attested in the 2020 Wayback copy, and is already consumed: the axis is FEN
side-to-move (`w`/`6R1` published vs `b`/`2R5` in the password, after `Rg6-c6+`), byte-verified in R-CHAIN23.

=> The thread CLOSES POSITIVE. Run no yinyang battery; there is no second bracket and no second site. The
community's even/odd Bifid split (superseded note 18) was never it. Do not generalise enf/not-enf into an
inversion rule. Taijitu geometry is chance-level negative on all four decrypted plaintexts. Lead 0's missing
28-char alphabet is unchanged and remains the real open item.

## Lead 0 reframed: the 28-char alphabet is CLOSED twice over (R-BOARD28B, 2026-09-26)

- **28 is cipher arithmetic, not a clue**: 10 digits - 2 escapes = 8 plain cells, + 10 + 10 escape-row
  cells = 28. `certified_vic.py:58-71`. This identity appears NOWHERE in the ledger before this row.
- **The letters were never missing either** - they are the author's, from the Phase-3.2 sentence
  "A fubcd-king & oracle-queen, thingky mvps, on a sad board but as wide as the first one seen."
  Community dedups it and appends J,Q,Z,X,W to get the 26.
- => There is NO missing 28-char interpreter alphabet to find. Lead 0's open quantity is the
  APPLICATION (digit map / escapes / transposition) on dbbib_91 + faed_570 - the late-261 "map-search"
  reframe, now with its justification.
- `R-BOARD28`'s "the missing alphabet must be a permutation of the board" is WITHDRAWN as unfounded.
- `briefcase/MEMORY.md:102` is WRONG on the dots: they are live cells at codes `10` and `44`; `10`
  decodes twice in the witness, `44` never occurs; W sits at code 49, not 48. Pipeline is fine, prose is not.
- The board's dots are exactly 14 apart, so at width 14 they stack in one column - but a straddling
  checkerboard is 8+10+10, so no 14-wide layout exists. Do not build a 14-wide sweep.

## RETRACTION + STRATEGY (R-BOARD28B-ADDENDUM, 2026-09-26) - READ BEFORE PROPOSING ANY SWEEP

- **RETRACTED**: the earlier claim that "the next target is the digit-stream grid" is WRONG. That surface
  is certified-closed (tested.md:8842: visual-leap route closed with a human-eyes witness; late-138
  mechanical positional surface exhaustive; late-139 7-token weave space complete; "ALL
  currently-specifiable reads of the crux are negative on both funded gates").
- **THE MECHANICAL SURFACE IS EXHAUSTED.** 43 "exhaustive", 10 "certified-closed", 15 of 24 R- sections
  with 0 candidates. The crux is UNSPECIFIABLE, not merely unsolved. Do not run another cipher sweep on
  dbbib_91 / faed_570; meet any such proposal with tested.md:8842.
- **Rule: never re-implement a decoder that has a certified witness - run the witness.** A hand-rolled
  decoder that is wrong yields a confident negative. Use `tools/bifid_repro.py` (currently SELFCERT PASS,
  all 5 artifacts hash-match), `tools/certified_vic.py` (SELFCERT 3.2.2 PASS), `tools/oracle.py --selftest`.
- **Only two classes remain, and only one of them works without help:**
  1. NEW AUTHORIAL STRINGS / ARTIFACTS - read the author's pages, transcript, groupchat and IMAGERY for
     semantics; do not decode anything. R-YINYANG-MARKER is the template: it found a real authored
     artifact (the aBa polarity bracket) that 108 prior ledger rows had missed.
  2. HUMAN VISUAL INPUT - the one acknowledged gap; without it the image surfaces stay shut.
- Controlled comparison from this session: the mechanical direction produced a retraction and zero yield;
  the semantic direction produced the marker find, the 28=8+10+10 arithmetic, and a MEMORY.md bug fix.

## NEW UNMINED SURFACE (R-SOLVERGRP-IMG, 2026-09-26) - `gsmg-solver-group/` had 4 files with ZERO ledger coverage

Inventory of `~/storage/external/briefcase/gsmg-solver-group` (42 entries) found four files scoring 0 in both
`tested.md` and `leads.md`. The `img/` corpus was empty (only an empty `ocr/` dir), so nothing in this
directory had ever been rendered.

- `puzzle.bin` - despite the name, a **PNG 1048x1556**. Contains the banner text `GSMG.IO 5 BTC PUZZLE
  CHALLENGE` (solid, 3 PSM modes agree) plus a bracketed mixed-case token on a second line that is
  **OCR-ambiguous and deliberately NOT transcribed** - preserved at
  `evidence/gsmg-solver-group-2026-09-26/crop_string_1to1.png` for a human read. Its rows 1079-1556 had
  never been rendered by anyone.
- `1752411872456.h` - an **ESP32/Arduino PROGMEM array wrapping a JPEG that is a crop of `puzzle.bin`'s top
  1078 rows** (98.33% agreement vs 48.56% for the bottom). Filename = epoch-ms = 2025-07-13, so a device was
  flashed with this image. No companion sketch in the corpus.
- The image's upper region is a **69x69 binary matrix at 15.00px pitch** (52% ink). NOT a QR (cv2 and zbarimg
  both empty), NOT text, NOT a floorplan (3 components, one spanning the frame). Meaning unknown; not guessed.
- `GSMG_JRK.md` - **all 427 creator (jrk) messages, 2019-04-20 to 2026-05-28**, cleaned and dated. This is the
  most concentrated authorial-primary-source object in the corpus and the best next target.
- `Jrksplain.txt`, `canihaveallhint.txt`, `Last solved and unsolved parts.txt` - also uncovered.

PROVENANCE CAVEAT: the banner says GSMG, but that fits a solver-made artifact as well as an author-made one.
Nothing is promoted to authorial. Two standing rules: **invert before OCR** on this corpus (the text is
light-on-dark; not inverting is what made me briefly record "no text"), and **never transcribe an
OCR-ambiguous token into this ledger** - preserve the pixels and write "untranscribed".

## CREATOR-MESSAGE CORPUS IS ALSO ALREADY MINED (R-JRKCORPUS, 2026-09-26) - corrects the R-SOLVERGRP-IMG recommendation

`GSMG_JRK.md` (427 creator messages, 2019-04-20..2026-05-28, all parsed) looked like the best untapped
authorial object. It is not. Cross-reference: roses/yellow-blue poem, `giveit = givetit`, the
`{1 },{4},{21}` door hint, "theory of everything", `-41,-17`, `1357`, "ASCII 127" and `gnomad` are ALL
already in the ledger - `gnomad` via the 53-candidate 2026-tail battery in `R-HINTS`, which OCR'd all 32
hint images. The corpus's only hex token is the already-solved stage-1 hash. **Its marginal value is
SEQUENCE, not strings**: `#6884` hint `{1 },{4},{21}` -> `#6913` "R=18 A=1 B=2 Could also be 21 or 1812 bit"
shows the creator AFFIRMATIVELY VALIDATING a numeric reading, which the hint image alone cannot preserve.

Genuinely unrecorded, and the only new artifact: **`#8446` (2023-02-23) is 161 bytes of raw binary posted
by the creator** - all bytes even, 22 distinct values, 7-bit-aligned, no corpus context. Unexplained; NOT
promoted to a lead. (The ledger's existing "8446" hit is msg 39237 and is unrelated - do not conflate.)

CONSTRAINT worth respecting: `#1806` (2020-02-22) "No clues to be found in those typos might you wonder" -
the creator EXPLICITLY disclaims typos as clue-bearing. The ledger has 28 'typo' mentions; this should
temper typo-hunting. Counterweight, same corpus: his own typos exist (`#23200` "Sqaures and a rabbit?").
Both recorded; neither refutes the other.

CONSEQUENCE: `R-SOLVERGRP-IMG`'s "read GSMG_JRK.md next" recommendation is DEPRIORITISED. `Jrksplain.txt`
is a rougher dump of the same corpus and `canihaveallhint.txt` was already OCR'd into
`gsmg-community/hints-consolidated/`. On this evidence the authorial-semantics seam is largely exhausted
too - stated plainly rather than manufacturing activity to fill the gap.

## R-SOLVERGRP-STR (2026-09-26): the banner string is the known small gate; the solver-group image surface is now fully read

The ambiguous line in `evidence/gsmg-solver-group-2026-09-26/puzzle.bin` is NOT a bracketed token and NOT an
encoded payload. It is the P2PKH **address `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`**, the funded "small" gate.

How the ambiguity was killed without guessing: per-position majority vote over 70 unconstrained OCR passes gave
28/34 characters unanimous; my assembly was base58check-INVALID (contains `O`, not a base58 char), the ledger's
existing reading is VALID, and its decoded HASH160 `a9553269572a317e39f0f518cb87c1a0ee1dbae4` matches the
open-problem pubkey `f4d1bbd9...5d464` already recorded at `tested.md:3033`. An oracle unrelated to OCR picked the
same string. Re-derived from scratch: `sha256("GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe")`
= `89727c598b9cd1cf...` = the existing SalPhaseIon slug, so the space-stripped concat is the intended form.

Two of my own claims from `R-SOLVERGRP-IMG` are RETRACTED: the banner text is dark-on-light (not light-on-dark;
inversion only helped thresholding), and there are no brackets (the two `1`s are address characters).

0 candidates, 0 oracle calls - correct disposition, since an address is not a password candidate and section 150
already swept this string against both gates for 0 matches. The whole solver-group image surface (PNG, 69x69 upper
matrix, banner) is now fully read and contributes NO new lead. Do not re-run this OCR; the value is already banked.

## R-MATRIX69 (2026-09-26): the 69x69 matrix is decorative; whole solver-group image surface now closed

Corrections to `R-SOLVERGRP-IMG`, which I had wrong in two ways:
- Entropy is 1.5703 bits/symbol over the 5-colour palette (67.6% of max), not "52.3%". Binarised it is 99.9% of max.
- The rows are **BLOCKED** in groups of 5 identical rows (14 blocks, all mutually different, 99.05% cell agreement with
  their block), **not periodic with period 5**. Every row j differs from row j-5. Blocking and periodicity make opposite
  predictions; do not conflate them again.

Tested and rejected: QR version 13 (69 = 17+4*13 is a valid QR size, but zero finder patterns, no timing pattern, and
`zbarimg` finds nothing across 8 binarisations x 4 orientations); all 256 elementary CAs; cyclic-shift relations
between blocks; and the possibility that the PNG was tampered with relative to the firmware. On that last point the
decisive test is structural, not pixel-level: diffing the 69x69 module grid of both images gives exactly 220 differing
cells and **all 220 are the identical substitution 218->231** (plus 84->85) from JPEG requantisation. Same source
image, no edits. The earlier "98.33% agreement, possible tampering" hook is closed.

The sole internal anomaly - blocks 6-7, rows 30-39 breaking the 5-cell run quantum - is a basket-weave band crossing,
not hidden data. Not read as text, not promoted.

Standing conclusion: the image is a solver group's own banner (generated weave + `GSMG.IO 5 BTC PUZZLE CHALLENGE` +
the already-known gate address `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`), compiled into ESP32 firmware to drive a
screen. No creator content. With `R-SOLVERGRP-STR` and `R-JRKCORPUS`, every file in that folder is now accounted for.
0 candidates, 0 oracle calls. Do not re-run image work here; there is nothing left in it.

---

## R-4E-BITMAP-2026-09-26 - the `4E` file is a RENDERED IMAGE, not encoded data

`4E` is **21,910 bytes and is a 313 x 70 8-bit grayscale raster** (21910 = 313 x 70 exactly, SHA-256
`d4a224bc22eb65b1d107efe962b985a2d3aed27b69262daf9b482763033048fb`). Autocorrelation of the solid-ink indicator peaks
overwhelmingly at **lag 313** (r=0.5489; every other lag 20..1200 sits at 0.52-0.54, the noise floor).

This kills the old reading of its profile. "33 distinct values / 0.694 bits/byte / 88% 0x00 / no 0x4E byte" is not a weak
cipher - it is a **mostly-blank image**. The proof of rendering is the edge ramps: `0x3a, 0x66, 0x90, 0xb6, 0xdb` appear
as mirror-symmetric pairs around 0xFF cores (e.g. bytes 8591-8619 = `ff 3a 66 b6 ff db db [20x ff] db db b6 ff 90 66
3a ff`). Cipher output cannot produce symmetric alpha-blend borders. **Do not run any cipher/compression hypothesis on
`4E` again - it is moot.**

Content inventory: 1px dotted ruling at 4px pitch on rows 27-30/32-37/39-40/55/59; solid rectangles (largest at cols
268-312); a symmetric lens/bowtie curve at rows 27-40 cols 124-200; diagonal strokes upper-right (rows 2-20, cols
196-244); a long dotted rule at row 25 with a gap near col 158; a dense 3px-pitch run field at rows 54-59 cols 93-175;
axis-like ticks on col 0. Overall it reads as a **chart/plot**. What it depicts is **NOT identified**.

The rows 54-59 field has an exact 4px glyph pitch giving 21 candidate 3x6 cells. Template-matched against a 3x5
font over 24 configurations: best error 39/315, all outputs noise. **It is not text.** Not promoted.
Renders: `evidence/gsmg-solver-group-2026-09-26/4E_render_5x{,_contrast}.png`.

## R-JRK8446-2026-09-26 - creator message #8446 is provably NON-RANDOM, still unread

161 space-separated 8-bit groups, 1288 bits (1288 = 7x184, 161 = 7x23). **Every group's low 3 bits are `110`**
(every byte = 6 mod 8), stripping to 805 payload bits = 161 x 5.

The real finding is statistical: only **22 of 32** 5-bit symbols occur; absent are
{0, 7, 10, 11, 15, 17, 23, 26, 27, 31}. Under a uniform 32-ary stream the expected number absent is 0.193 and
P(>=10 absent) is **~1.6e-14**. So the payload is **not** random 5-bit data - there is a genuine restricted
22-symbol alphabet. Conditioning on those 22, chi-square = **69.2 on df=21** (p<1e-5); value 20 occurs 19x vs 7.32
expected (2.60x), value 3 only 1x (0.14x). Doubly non-uniform.

Open thread, **not** a conclusion: treating value 20 as a separator gives 20 segments of lengths
[1,10,3,7,8,6,0,4,8,1,24,6,7,8,10,3,24,4,7,1] - loose 6-10 cluster plus two outliers of exactly 24.

Negative battery: 7x23 and 23x7 bitmaps at 3 thresholds; raw 1288-bit stream at every width dividing 1288 in 4..199;
A1Z26 at offsets 0/1; the earlier 7-bit decode is 85% printable but wordless. Run structure is 158 runs / 161 symbols
(155 of length 1) - no looping plaintext.

**Retracted as evidence:** the "best width 184/56/8, score 0.375" result. Those widths just preserve my own 8-bit
grouping, and the constant `110` pad forces 3 uniform columns per 8 by itself. Circular. The only genuine evidence
for structure is the alphabet restriction above.

Banked: authorial, 161 bytes, constant `110` pad, restricted non-uniform 22-symbol alphabet. No reading. 0 candidates.

### R-JRK8446B follow-up - the delta-77 repeat is the live #8446 lead

Longest exact repeated substring of the 161-symbol 5-bit stream is `[19,16,29,16,20,13,18,28]` at positions
**8-15 and 85-92 (delta 77)**. It does not extend. Significance: empirical symbol match rate 0.0650, so an exact
8-gram repeat is expected 3.8e-6 times over all 11781 position pairs -> **p ~ 4e-6**.

Delta 77 is the global outlier: 13 matches vs 5.5 expected (z=3.23) and the **longest consecutive match run in the
whole stream (8)**; next-best run is 5 at an unremarkable delta 11. The odd part is the lead-in - both mismatches sit
at the FRONT of the window: `v[6..7]=(9,1)` vs `v[83..84]=(2,5)`, then 8 identical symbols. Not a copy-paste artefact,
not periodicity. Unexplained.

Everything else negative: all bit-unpackings widths 2-8 x 2 bit orders x all offsets; A1Z26 both cases / base32 /
base32hex / hex / Hebrew at offsets 0-3; 7x23 and 23x7 grids row- and column-major; first differences. Best English
score 10.0, no trigrams. **Hebrew-22 is specifically REFUTED** - sequential Alef-Tav would make samekh (rare) the most
frequent symbol (19x) and give yod (commonest) only 3x. Do not re-try it blind.

## ADDENDUM 2026-09-26 (late) - rows `R-JRK8446E`, `R-JRK8446F`, `R-JRK8446G`, `R-4E-PROV`, `R-XREF`, `R-MP3STRUCT`
This addendum SUPERSEDES the `R-JRK8446` / `R-JRK8446B` sections above. Read this first.

### 1. `#8446` IS SOLVED (`R-JRK8446G`). It was an encoding-identification, not a cryptanalysis.
Transform, both steps required: **reverse the 161-group byte order, then bit-reverse each byte.**
Output is 161/161 lowercase a-z and re-encodes exactly (161 groups, sha-stable round trip):
`yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyangwewontgiveawaythepassworditsinfrontofyoureyesbutyourenotseeingitverylaststepisatruegiveawaypromised`
`2023-02-23.txt` is the same hint, OCR-damaged, 149 valid groups. The family was already closed at
`tested.md:7248`/`:7259`, so this yields **0 new candidates and no reason to re-run that battery**.
The "reverse binary string" label in the community README is consistent.

### 2. Both earlier `#8446` "statistical findings" were ARTIFACTS OF THE UNKNOWN TRANSFORM. Do not re-bank them.
- **The constant `110` pad is forced, not a signal.** `a`-`z` = `0x61..0x7A`, so bit7=0, bit6=1, bit5=1 always.
  Bit-reversal sends bit7->bit0, bit6->bit1, bit5->bit2, so the low 3 bits are ALWAYS `110` for any lowercase
  letter (verified 26/26). The pad is a fingerprint of lowercase ASCII, nothing more.
- **The "only 22 of 32 symbols, P(>=10 absent) ~ 1.6e-14" claim used the wrong null.** It assumed a uniform
  32-ary stream. The plaintext simply uses **22 distinct letters**; a 161-char lowercase English string using 22
  distinct letters is entirely ordinary. There is no restricted 5-bit alphabet and no hidden second layer.
  (My own verification pass briefly re-asserted a 26-vs-22 "match" before this was corrected - flagging it here
  rather than quietly dropping it, per the `R-DOORGlyph`/`R-CLEANCLAIM` norm.)
- The `delta-77` eight-symbol repeat (`R-JRK8446B`) is likewise unremarkable in hindsight: both windows are the
  `giveaway` region, i.e. the word `giveaway` appearing twice. **Closed, do not re-open.**
- **GENERAL LESSON, and the reusable part of this whole session:** find the transform FIRST, then ask whether every
  "structural anomaly" is derivable from it. Both anomalies were. A structure that is *forced* by a known
  transform carries zero information, and a p-value against the wrong null model manufactures significance.

### 3. `4E` provenance CLOSED as a solver-group artifact (`R-4E-PROV`).
21,910 B = 313x70, mark density 0.1020. Against 27 authorial hint PNGs x 216 alignment variants: best
density-normalized lift 3.283 vs a real-vs-real baseline of 3.375 +/- 2.095 over 351 pairs, **p=0.3732, z=-0.04**.
Not a crop/rotation/rescale/inversion of any authorial hint. `warningunlockwalletlockIOgicCAnyou+dig-it` is solver
annotation, not creator text. Its geometry (three bars + diagonal strokes) remains uninterpreted. `tested.md:12101`
already flagged it unidentified. Method note that matters: authorial hint images have wildly varying ink density, so
image-similarity nulls MUST be density-normalized and same-reference-class; unnormalized and random-mask nulls
produced false positives earlier in this project.

### 4. The hint BINARY surface is now FULLY ENUMERATED and closed (`R-XREF`).
All 33 files in `~/briefcase/gsmg-community/hints-consolidated/` were parsed and tested against all four known
authorial encodings. **Only 2 contain binary:** `2023-02-23.txt` (149 groups, 100% end `110`, reverse+bitrev) and
`2026-01-01-new-year-hint.txt` (77 groups, 12% end `110`, plain MSB-first 8-bit ASCII). So the creator used **two
different binary encodings**, cheaply separable by the `110`-suffix statistic (100% vs 12%). No third binary
transcript exists. The `2023-02-23.txt` decode independently reproduces its OCR damage at exactly the same 12
characters, corroborating `R-BINSELF` from a second artifact.

### 5. `puzzlepiece.mp3` IS FULLY ACCOUNTED FOR - there is no mp3 blob (`R-MP3STRUCT`). This corrects `late-209`/`late-223`.
- **The "212-byte ID3 gap island" is the tail of one MPEG frame.** 212 = 1045 - 833 exactly: byte 8064 sits at
  offset 833 inside audio frame #3 (7231..8275), so 212 bytes remain to the frame end. The trailing 33 bytes are
  the standard MP3 zero-fill before the next sync. The "high-entropy 212 B" is an ordinary audio fluctuation; true
  data is 179 B (entropy 6.865, not the recorded 6.368, which averaged in 33 zero bytes).
- **Complete accounting: 199 contiguous MP3 frames, ZERO gaps, ZERO unclaimed bytes.** 0..280 = ID3**v2.2** tag
  (TSS "Logic Pro X 10.4.1", COM TunNORM, COM TunSMPB); 281..4095 = 3815 bytes ALL ZERO; 4096..EOF = 199 frames at
  320 kbps/44.1 kHz (frame length 1044/1045 by padding bit), duration 199*1152/44100 = 5.198 s, matching ffmpeg
  exactly. No ID3v1 trailer. `8276` is a real sync but the FIFTH frame boundary, not the first as `late-223` recorded.
- **The only structural defect is a malformed tag that hides nothing:** the v2.2 size field declares 8054 B while only
  271 B of frames exist (they end at 281). Beware: v2.2 uses **3-byte** frame IDs and sizes, so a v2.3/v2.4-style
  4-byte parse returns "0 frames" and makes the file look tagless.
- **Chronology refutes my own lead.** The community README dates the Decentraland hint - whose asset IS this mp3 - to
  **2020-02-20**, a year before the 2021-02-12 note, and records it already solved: download the sound, split L/R,
  **invert one track**, remix -> `HASHTHETEXT`. So a Feb 2021 remark about "blobs in mp3" cannot be an unrecovered
  blob here. The corpus contains ZERO occurrences of "mp3"/"blob" in all 427 messages. `late-92`'s literal closure is
  UPHELD and now has a byte-level reason to be believed. The `salphaseion.ipynb` "AES Blob" is a phase-3.2 artifact,
  not this file, and is off-limits per `AGENTS.md`.

### 6. THE ONLY GENUINELY OPEN SURFACE FOUND TODAY: hint dates #7 and #8 are mined by NOBODY (`R-XREF`)
The community README lists **2021-01-21** and **2021-02-12** as official hint dates #7 and #8, embedding both PNGs
with placeholder alt text and **no analysis**. They are the only two official hint dates in the series that neither
this ledger nor the community has ever mined. 2021-01-21's prose half is corpus `#5717`; its letter-spaced
`S R A S` token appears in NO ledger row (same artifact class as `#7914` "There is Another D O O R", never mined).
**BOTH ARE BLOCKED ON A HUMAN EYE READ OF THE TWO PNGs - not on compute.** I have no image-input capability, and
per `R-DOORGlyph` bad OCR of this corpus has twice manufactured false leads; these two transcripts contain no binary
groups, so they have **no self-validating internal check** (contrast `2023-02-23.txt`). Do not run a battery on the
OCR strings. Reading order: `S R A S` on 2021-01-21, and the "blobs in mp3" line on 2021-02-12 (which section 5
now says is NOT about `puzzlepiece.mp3`, so the read should also establish what it actually refers to).

## ADDENDUM 2026-09-26 (final) - `R-XREF-READ`: the two open hint gaps are CLOSED. `S R A S` never existed.
Supersedes section 6 of the previous addendum. **The "blocked on a human eye read" blocker was wrong and is removed** - the
images are text and text is recoverable from pixels. Method: 5-variant x 3-PSM OCR cross-validation, connected-component
line/word segmentation, and font-independent glyph template matching that uses band 1 of `2021-01-21.png` as its own
labelled dictionary (that band's text is corpus `#5717`).
- `2021-01-21.png` (604x140, 3 bands) = bubble "January 21, 2021" + "Not to give any hints but a few might not require the
  internet" (13 word groups, exact match) + a HEART + `anymore.` **It is a plain render of `#5717` and nothing else.**
- **`S R A S` IS NOT IN THE IMAGE.** It was an OCR fabrication in `hints-consolidated/2021-01-21.txt`. GAP 1 REFUTED; the
  "letter-spaced token like `#7914` Another D O O R" thread is WITHDRAWN - no referent.
- `2021-02-12-salph-mention.png` text is CONFIRMED by 9 identical OCR passes: `blobs in mp3 didnt recovered` etc. GAP 2's
  text is real, but `R-MP3STRUCT` already refuted the `puzzlepiece.mp3` link on chronology. No hidden symbol in the image.
- **ALL 27 HINT IMAGES ARE NOW READ/CHARACTERISED and the binary surface over all 33 transcripts is enumerated. There is
  NO unmined artifact identified anywhere in this project.** `X` remains unsolved. Stop working known files: the next move
  must be a NEW source surface. Treat `hints-consolidated/*.txt` as hypothesis-generating only - one of them is provably corrupt.

## ADDENDUM 2026-09-26 (2) - `R-P32BLOB`: a NEW OPEN LEAD exists. Supersedes "no unmined artifact identified".
- The `phase*-assets` tree (28 files, ~4.1 MB) was inventoried for the first time. Most was already covered **by content**
  despite zero filename hits - **filename coverage is a worthless proxy, always content-grep first.**
- 2 of the 4 new solver b64 blobs are byte-copies of community files (`p3.b64.txt` == `phase2_aes.txt`; `p32b.b64.txt` is
  the verbatim tail of `phase3.2.txt`). The solver group contributed no independent data.
- `phase3.2.txt` line 4 = a 1539-byte, 26-symbol blob with a **decisive period-15 polyalphabetic IC signature**
  (period 15/30 IC 0.065 vs 0.043 off-period, where random-over-26-symbols is 0.0385). This **rules out the community's
  monoalphabetic-only attack** in `phase3.2.ipynb` cells 3/5/6/10, which was the wrong cipher class.
- **Key NOT recovered.** Vigenere, Beaufort, a cipher-symmetry key-recovery attack, and Quagmire/per-column-mixed-alphabet
  were all tried and all rejected on evidence (best 14 word-hits vs 115-180 for English). The `yl` 1539-length match is
  REFUTED (K periodicity 0.108, not 1.0).
- Live hypotheses, in order: (1) plaintext is NOT English - phase-2.1/3.2 theming is explicitly non-English (Klingon,
  Persian `vagh`/`jav`, EBCDIC/cp1141); (2) a further layer sits beneath the polyalphabetic one. Do NOT run another
  English polyalphabetic sweep.
- Also open: the 149-digit string (149 is prime, '1' = 37.6%, not A1Z26 as pairs) and `phase2.1.txt`'s closing
  `Ok kid, on the highway, let put it in the worst gear.`
- CALIBRATION: <~40 common-word hits in 1539 chars is noise. Never log a decode as a hit on word-count alone.

## ADDENDUM 2026-09-26 (3) - `R-P32BLOB2`: the 1539-byte blob is NOT SOLVED. I retract this session's own 8x claim.
- The "8x held-out gap" I reported mid-session was a **too-weak null** (shuffled permutation instead of refit-on-shuffled).
  Honest control: real 133.8 vs null 89.6, real wins only **6/15 columns = coin flip**. **No letter-frequency signal exists.**
- Per-column substitution (390 params) merely OVERFITS: train chi ~5/column beats real English's ~26, and its "325 word hits"
  were inflated by 2-letter words. Shared-substitution+shift (41 params) gives held-out 952 = random range, 0 trigrams.
- Beaufort is frequency-identical to Vigenere - that model arm can never be distinguished by letter statistics.
- Language test: english fits ~2x WORSE than uniform (75.0 vs 39.2) => plaintext is **not English**; but russian(28.5)/persian(34.9)/
  uniform(39.2) are indistinguishable at this sample size, so "russian wins" is **not** a result.
- **Only the IC curve survives, because IC is permutation-invariant:** period 15/30 IC 0.0645/0.0654 vs off-period 0.0427
  (random = 0.0385). Column plaintext is natural-language-SHAPED but the key and language are not identifiable from 1539 bytes.
- **STOP RULE: do not run a 4th English/Russian/Persian polyalphabetic sweep on this blob.** Three parameterisations have
  failed proper held-out testing. Remaining angles are all non-trivial: non-substitution byte encoding, finding a SECOND
  ciphertext sharing the period-15 key, or the untried 149-digit string / "One for one, four for one".

## ADDENDUM 2026-09-26 (4) - `R-P32BLOB3`: the 1539-byte blob and the 149-digit string are both CLOSED as leads.
- **Corpus sweep (489 files, IC periods 1-40) found NO second period-15 ciphertext** - all 6 real hits are the same blob
  (phase3.2.txt, 4 notebook cells, and a newly-noted **4th copy in `gsmg-community/README.md`**). The key is therefore
  unrecoverable *information-theoretically*, not for lack of search. **Do not retry a key-recovery sweep.**
- The 149-digit string survived ~30 decodings (2/3/4-digit groups, reversed, digit-swapped, mod26/27, split-on-'1',
  T9, coordinate readings) with best result 2 trigrams / 0 words vs 5-10 / 20-40 expected. **No candidate.**
- Nothing in the `phase*-assets` tree yields a candidate. Remaining angles are all prose-interpretation or
  non-alphabetic-encoding, both with poor historical hit rates in this project.

## ADDENDUM 2026-09-26 (5) - `R-P32KEY`: **phase-3.2 blob SOLVED. Key `amphtaclwmtbvfz`.** And I was wrong about why my earlier search failed.
- Cipher = fixed byte->letter substitution L + 15-symbol Vigenere. 15 residue classes are each an exact bijection; 254/254
  cross-column shift checks agree; **independent re-decode reproduces the plaintext exactly.**
- **The plaintext was already on disk** in gsmg-solver-group/"Last solved and unsolved parts.txt", a file `R-SOLVERGRP-NEW`
  inventoried and dismissed without mining. That was the actual failure - not the cryptanalysis.
- `phase2.1.txt` "worst gear" = REVERSE -> coords `51 52 28.0 N 4 24 23.2 E` (SafeNet BV).
- **RETRACTION:** `R-P32BLOB2`'s "no signal / unrecoverable" was an OPTIMISATION failure, not a model failure. Model B's
  41-parameter model was correct; 2500 iterations x 3 restarts cannot find a 26! permutation. Its calibration warnings
  stand; its conclusion about the cipher does not. `R-P32BLOB3`'s corpus sweep still stands, but its "unrecoverable"
  corollary is retracted.
- **Lesson for this project: before running a search, CHECK THE OTHER LOCAL FILES FOR THE PLAINTEXT.** A ciphertext with an
  unknown 26-symbol substitution is near-infeasible to attack statistically, but trivial given known plaintext.
- Still open: the 149-digit string (not an A1Z26 concatenation; recovered key does not apply).

## ADDENDUM 2026-09-27 - `R-SOLVE`: 149-digit string DECODED; gsmg-private progress snapshot found; small-gate harness REFUTED.
- **149-digit string SOLVED** (`R-VIC149`): straddling-checkerboard, board **`FUBCDORA.LETHINGKYMVPS.JQZXW`** (the author's own line-8 acrostic,
  punct `.` at 0-based 8 and 22 - issue #76's `/` is a mis-transcription), escapes **1,4** (line 2 "One for one, four for one").
  Reproduces the 91-char message byte-exact, 0 unmapped digits. `SELFCERT 3.2.2: PASS`. With `R-P32KEY` (`amphtaclwmtbvfz`) that is
  both of phase 3.2's cryptic components solved from authorial hints.
- **`~/storage/external/briefcase/gsmg-private/PROGRESS-2026-09-08.md` is a verified prior-session snapshot that was never in this tree.**
  It carries a **MODEL CORRECTION**: the small gate blob's real password is **EVP-MD5 over the RAW 5-token string**, not
  `sha256(X).hexdigest()`. => the **185 / 2,942 / 15,876 negatives are INVALID for the small gate** and must be re-run under the
  corrected harness before they can be cited as closed. Highest-value open item.
- Community prize-claim for `Half`/`BetterHalf` is a **scam**: signatures do not verify; keys control only their own empty addresses.
- Cosmic Duality 1327 B verified (sha256 4f7a1e4e...); it IS a bit-packed 103x103 + 7 pad bits, density 0.4895, but spatially
  **uncorrelated** (adjacent 0.495, lag-103 0.495) - reconfirms the Rule-90 falsification. My initial "dimensionally impossible"
  objection was wrong; the community arithmetic was right.
- **Crux unchanged:** interpreter-alphabet decode of `dbbi`(91)/`faed`(570) -> X. All surrounding local layers now certified.

## ADDENDUM 2026-09-27 (b) - `R-BOTH`: re-keying + OEIS leads both executed and bounded; neither broke through.
- `R-B2REKEY`: **20,358** digest/HMAC/XOR constructions from `K_C1`/`K_C2`/`E_C` -> documented `K_S1`/`K_S2`/`E_S` = **0 hits**.
  **UNCERTIFIED** (no witness - the targets exist only in unverified `author-wallet.txt`). Only rules out a bare digest; EVP_BytesToKey / derived-IV AES / literal "re-keying" remain open.
- `R-OEIS141920`: hook is **exact** - A141920 = primes = 16 mod 23, and **1327 is term #9** and the Cosmic blob is **1327 bytes**; `1327 mod 23 = 16`.
  But **103 mod 23 = 11**, so 103 is *not* in the sequence - the hook is about the byte-length only.
  **28** sum/arithmetic operations over `dbbi`/`faed` tested against the 44-term set: **0 hits** (certified).
- `R-DBBI91-NOTPAIRED`: `dbbi`(91) is **not** a cipher of the 91-char message - no period <91 consistent (period 91 is vacuous).
  **Certified, witness = same method finds period-15 322/322 on the 1539-byte blob.** The 91-length match is coincidence.

## ADDENDUM 2026-09-27 (c) - `R-EBCDIC+DBBI`: EBCDIC-1141 is DEAD; dbbi Bifid analogue is not English.
- **EBCDIC-1141: closed dead end (certified).** `1` occurs 56x / `4` 14x in the 149 digits (so the phrase is not a frequency claim); no
  artifact is EBCDIC text (blob entropy 7.870 b/B, graphic ratios at chance); CP1141-specific bytes 0x9F/0x15/0x25 show no enrichment;
  0xC1-0xC9 occupancy at chance; strides 11/41/114/141 give nothing. The phrase is already **verbatim consumed** by the certified escapes-1,4
  reading. Do not re-raise from issue text.
- **dbbi(91) through the certified square `DBIFHCEGAKLMNOPQRSTUVWXYZ`:** the a..i map is plain identity a->A..i->I (CANON is the induced
  position map). faed witness reproduces all 5 stored hashes + `BTCSEED...` head, so the code path is proven.
  dbbi -> 91 chars / 15 distinct letters / no label, sha256 `ac4f5a9f...` => **dbbi is not the faed pipeline run twice.**
  Still open for dbbi: other periods, rotated squares, the uncertified alphabet-rotation re-decodes, or a non-Bifid construction.

## ADDENDUM 2026-09-27 (d) - `R-POSTER` DECODED: `poster_tagline.txt` is the known title, not a hidden container.
- ASCII art (129x930, `#`/space only) = GSMG logo at rows 0-128/cols 0-91 + tagline at rows 52-86/cols 146-922.
- Tagline segmented into **26 glyphs / 18 distinct bitmaps** -> **`GSMG.IO5BTCPUZZLECHALLENGE`**.
  Glyphs 5-8 are `.` `I` `O` `5` (a bare full-height bar and a closed oval), so it is `GSMG.IO`, not `.105`.
- Re-derived `sha256("GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe")` = `89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32` **MATCH**
  (7 variants, 1 match; the literal-period form does not match). Confirms the canonical title/hash input; **no new information, do not re-open.**
- **Remaining crux is still only:** interpreter-alphabet decode of `dbbi`(91)/`faed`(570) -> X. Other dbbi periods, rotated keyed squares
  and non-Bifid constructions untested.

## ADDENDUM 2026-09-27 (e) - proposed dbbib sweep DECLINED: already certified-closed (`R-POSTER2`)
- The dbbib_91 "Bifid all periods 1..91 x rotated keyed squares + non-Bifid variants" sweep I proposed after `R-POSTER` is **already done**:
  `:8849` (rotation family exhausted, certified-negative on both funded gates), `:8845` (convention blocker already resolved), `:12254` F4
  (Bifid across 15+ keyed squares + full 25-letter rotation family + 9! token-cell permutations; crux "unspecifiable, not merely unsolved"),
  `:12258` (mechanical surface CLOSED; `AGENTS.md` bars a battery without an authorial unblocker).
- The `a..i -> 8,1,5,0,6,3,7,4,2` digit stream I derived reproduces `:905` verbatim and is already swept at `:3613`, `:8084`, `:11673`, `:3687`, `:1302`, `:4223`.
- **0 runs, 0 oracle calls.** Live directions = `:12258` (a) new authorial strings/imagery semantics, (b) human visual input.

## ADDENDUM 2026-09-27 (f) - `R-SLUGPRE`: direction (a) yields its first result - 4/7 hash-slug preimages + 8 unrecorded authorial slugs

Working the sanctioned class (a) "new authorial strings, read for semantics, do not decode anything"
(`:591`, `tested.md:12258`) produced the first new banked object since `R-POSTER`. 0 candidates, 0 oracle
calls, no cipher touched.

- **The method gap was the CDX index, not the pages.** `gsmg.io` is content-addressed -
  `slug = sha256(lower_concatenated_post_text)` - and the law self-tests **3/3** against the preimages
  `tested.md:326-328` before being used. The Wayback CDX index for the domain (413 unique urlkeys) exposes
  both the 13 hex slugs **and 72 plaintext slugs**, so the seven "still open" preimages at
  `tested.md:336-342` had their answers sitting in plain URL text.
- **4 recovered** (independent `sha256sum` witness, not Python):
  `0b0f37ec`=`hopeitisthequintessentialhumandelusion`,
  `10d6a2c5`=`humphhopeisthequintessentialhumendelusionsimultaneouslythesourceofyourgreateststrengthandyourgreatestweakness`,
  `c2eef34b`=`youmeizandself`,
  `a2aefdbb`=`GSMG.IO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`.
  The last one **retires a `R-POSTER` loose end**: `a2aefdbb` is the period-retained twin of the `89727c59`
  slug. Both `R-POSTER` statements were true - the literal-period form is simply a different, also-real post.
- **3 remain open** (`673e3b1a`, `aca20ae7`, `f9719d6`); bounded negative = 129 candidates, 0 preimages
  (`youmean<X>andself` x26, 20x2 hope-prefix forms, 31 short slugs). UNRESOLVED, not a semantic claim.
- **8 authorial slugs have ZERO corpus coverage** after normalising 1,707,076 chars of
  `tested.md`+`STATE_BRIEF.md`+issues+README: `digitallogiccryptography`,
  `hopeisthequintessentialhumandelusionsimultaneously...`, `humphhope...`, `thSeedisplanted`,
  `thepuzzlestartshere`, `youarewrongaboutdirhunt`, `youmeisandself`, `youmeizandself`.
- **Semantics, not decode:** the author publishes *minimal variants as separate posts* and the content
  address is the only thing distinguishing them - hope `is`/`it`, with and without a leading `humph`;
  self `d`/`i`/`s`/`z`. Also `thSeedisplanted` (camel-case **S**, one `e`) is the author's own slug and is
  NOT the corpus token `theseedisplanted`.
- **Why the pages themselves are a dead end (do not retry):** all 7 archived bodies are byte-identical
  except 40 bytes in a `csrf-token` meta - a client-rendered Laravel SPA with the text absent. The 2026
  `js/app.js` captures are the current trading frontend, not the puzzle site. Wayback `id_` captures are
  **brotli** (no magic number, so `file` says `data`); decode with `brotli -d` or python `brotli` 1.2.0.
- **Norm reinforced (`R-XREF`):** every one of the 7 hashes already had a ledger line, yet 4 preimages were
  recoverable and 8 real slugs unrecorded. The check that counts is *is the TEXT in the corpus*, never
  *is the URL mentioned*.

**Crux unchanged:** `X` remains unsolved; the mechanical `dbbib`/`faed` surface stays closed. Live
directions remain (a) and (b); (a) has now produced a real artifact and is worth continuing, with the next
target being the 8 unrecorded slugs' page text and the 3 remaining preimages.


> **Correction 2026-09-27:** `aca20ae7c6b5` preimage RECOVERED = `GSMG.IO5BTCPUZZLECHALLENGE` (case+period preserved, witness 5/5). Open now 2: `673e3b1a`, `f9719d6d`. The 8-slug list is really 7 - it wrongly repeats `youmeizandself`, recovered in section 15.

## ADDENDUM 2026-09-27 (g) - the slug/archive route is CLOSED end to end, and B2's "re-keyed" clause is answered

Three rows: `R-SLUGF971`, `R-CDXFULL`, `R-B2REKEY-AES`. Net effect: two open items
recorded yesterday are now closed, and one of them was closed because it was never
really open.

**1. `f9719d6d` was not an open preimage - it is `sha256(raw 32 bytes of 89727c59)`.**
Verified with `sha256sum` (the same one-liner also reproduces `db14474e` from the
ASCII-hex form). So the "still open (2)" is **open (1)**. Do not read the 2^-256
match as an authorial content-address chain: `tools/decodekey_vic.py:39` already built
that exact value as a hypothesis, the 2026 archived bodies for `f9719d6d`/`673e3b1a`/
`c2eef34b` are **byte-identical modulo csrf-token** (36,627 B, masked sha256
`504655235d403b30` - the SPA catch-all), and live `/f9719d6d` is **404**. A 200 from
that era proves a path was requested, not that a post exists. This is the project's
third "our own generator read as an authorial fact" (after `R-SOLVERGRP-IMG` and the two
retracted `R-JRK8446` findings) - the standing defence is unchanged and still works:
ask what in *our* tooling could have produced the pattern.

**2. `673e3b1a` - downgrade it.** The five recovered preimages are confirmed by an
independent route (real authorial phrase -> recorded slug, under a law that self-tests
3/3). `673e3b1a` has none, so its existence as a post is **unconfirmed**: it is an
unexplained path in an archive index. It is not a battery target without a new text
source.

**3. The whole archive-URL route is a certified negative.** All **620** gsmg.io CDX
urlkeys enumerated and diffed against the corpus (raw and URL-decoded): every
significant path is already recorded, including the three a filename-keyed read had
called unmined. The remainder is the 2026 trading site (`/shared/*`, `/register?referral=*`,
~90 help-centre articles) and crawler accidents (`%20`-mangled lodash comments).
**0 new surface. Do not re-run slug recovery from archives** - and the blocker that
motivated it is moot, because Wayback alone held everything.

**4. B2's "re-keyed" clause is answered (`R-B2REKEY-AES`).** `R-B2REKEY` left "AES with
derived IVs" open after 20,358 digest/HMAC/XOR constructions hit 0. AES belonged in
that sentence for a structural reason the digest search could not express: `K_C1` and
`K_C2` are each exactly 32 bytes = exactly an AES-256 key, and `E_C`->`E_S` is
15->15, so a cipher re-keying preserves every field's length and a digest never can.
**10,758 candidates / 4,604 unique, two verifiers (79 B sha256 == `b40fce72...`, and
15 B == `E_S`), 0 hits.** Witnesses: B1 re-derived through the `openssl` binary rather
than `oracle.py`; RC4 against RFC 6229; a positive control; and a **printed per-cipher
coverage table** - the first run of this row nearly became a fake negative because
`rc4` and `bf-cbc` were silently absent from this `openssl` build. RC4 was then
implemented properly; **Blowfish-CBC is declared UNCOVERED in the tool's output**
rather than allowed to read as a negative. `K_S1`/`K_S2` were deliberately not scored
(they exist only in the unreproduced `author-wallet.txt`).

**Standing caution, CORRECTED 2026-09-27 (`R-EBTAIL-2026-09-27`; supersedes the text previously here):** this caution was **stale and is withdrawn.** `E_S`/`B2` are **not** unanchored community values. `R-B2FAIL` swept `{small 96 B, PHASE2}` and never touched the p32 outer envelope (salt `b45a5e3d827593ca`, ct 80 B); `tools/rung2_b2.py --selftest` re-run today returns `ALL ANCHORS HOLD`, rc=0, with the re-encryption control and the distinct-envelope control both passing. `leads.md:59` was always the correct position. Row 4's `EVP_BytesToKey` / derived-IV / non-derived-IV clauses remain closed as `R-B2REKEY` and `R-B2REKEY-AES` closed them.
**Additionally, the chain-4 key is now 32/32 on-puzzle.** `E_B[:2] = 59cc` was the last community-sourced byte-pair; `tools/eb_tail_sweep.py` sweeps all 2^16 two-byte tails against the published chain-4 hash `e4269ed5...` and finds **exactly one**, `59cc` (N=65,536, D=20,666/s, t=3.2 s, 267 PKCS#7 survivors vs 256 expected, 1 hash hit, 0 oracle calls). It is *determined*, not quoted. This does not make the chain creator-authenticated — the acceptance anchor is community-published — but the quoted value and an exhaustive independent search now agree.
**Consequence for the frontier:** the chain-4 key is no longer a blocker. The missing operand is `ca`/`cosmic_A`, referenced only by the 32-bit SHA-256 prefix `cd3fea3d...` (#92), with the creator disavowing a "step after Cosmic Duality" (#104). Chain-4 is a 31-byte header (`+-` marker) plus 35 x 32-byte blocks, printable fraction 0.346 — an XOR-triangle operand grid, not text.

**Also closed by direct inspection:** the 2023-06-01 server-rendered capture of
`89727c59` (4,556 B) contains the two known textareas and **nothing else** - no hidden
input, no comment, no third field. "The post body holds more than the textarea" is
closed by reading, not by inference.

**Crux unchanged:** `X` remains unsolved; the mechanical `dbbib`/`faed` surface stays
closed. Direction (a) is now thinner than it looked - the authorial-post route is
exhausted at the URL layer, so the next (a) target must be a *new source surface*
(imagery, the creator corpus' sequence, or a new artifact class), not another archive.

## RECONCILIATION 2026-09-27 (R-FUBCD, R-SOLVERGRP-NEW/PW, R-JRKHIST, R-UNUSEDKEYS, R-TREE-B-AUDIT)

This section exists because three items above had gone stale, and because the honest summary of
the puzzle's position is now narrower and more precise than it was.

### 1. The board has no author witness. Stop calling the VIC vector the author's.
`R-FUBCD` swept all 399 files in `~/gsmg/gsmg-web-archive` for the exact board, the Phase-3.2 seed
sentence, and every seed token (`fubcd`, `oracle-queen`, `thingky`, `jqzxw`, `sad board`,
`as wide as the first`) — raw and whitespace-stripped. **All zero.** Controls passed
(whitespace-insensitive SalPhaseIon controls in 4–5 witnesses), so the nulls are witnessed, not
uncertified. Phase-3.2 is not among the only two archived real puzzle pages. The earliest dated
community witnesses are issues #74/#75/#76, all 2026-02-16, inside a batch the ledger itself flags
as partly AI-slop — one lineage, not independent corroboration.
Consequence: even **granting** the community sentence, the exact string is **1 of 84,240**
(`5!` orderings × 27 × 26 punctuation placements), so `METHOD-I` remains valid only for the one
string it actually tests. Do not let "we have the alphabet" slide into "we have the sentence."

### 2. The solver-group pack is now fully triaged, and one of its files is a rickroll.
42 -> 89 files (121 MB); the 52 newest were triaged. `4E.zlib` is a pure 4.2% recompression of bare
`4E` (sha `d4a224bc…`, zero new information); `4E` is binary 4-byte-expanded sparse pixel data, not
whitespace-prefixed text. `found.txt` is a failed 1GSMG vanity scan (30 MB, 459,300 lines, 153,100
key triples) containing neither gate nor target pubkey. `jrk-history.txt` decodes — MSB bytes, byte
reversal — to a payload prefixed `BASE64` and is a **Rick Astley rickroll**
(`aHR0cHM6…` -> `https://www.youtube.com/watch?v=dQw4w9WgXcQ`), positively identifying the file as a
solver shitpost. Do not promote its "13 is default / C is the 2nd hint". A 227-char community
`phase_3_password` and 28 headline restorations both fail both blocked blobs. 19 candidates drawn
from all four ladder keys × 6 blobs × 2 KDFs = 228 attempts, 0 decrypts. **Nothing here is a lead.**

### 3. `author-wallet.txt` is OURS, not the author's — filename trap.
`~/briefcase/gsmg-private/author-wallet.txt` says "Generated 2026-09-22" and its body is our own
certified chain, our own field layout, our own gate balances and DCL findings. `K_C1`'s hash160
matches inside it, which is **circular, not evidence**. In a directory named `gsmg-private` that
also reads as "the author's private material." Never cite it as authorial attestation.
(`gsmg-solved.json` and `keyFOUND.txt` are, by contrast, fully correct and honestly self-retracting —
only their filenames mislead.)

### 4. Where this actually leaves the puzzle — read before proposing another battery.
Every surface reachable from this device is now accounted for. The two blocked envelopes remain
password-blocked (`9fbc451d`, 4,090 B; `eefc4c5b`, 2,432 B), `ca/cosmic_A` is still missing, the
Phase-5 ciphertext location is genuinely lost with its Scribd document (the recovered command line
is truncated at `-pass`), and Lead 0's interpreter *application* is the only live semantic crux.
The author-quote vocabulary is not a fresh option: `late-310` already swept 325 forms of it.

**Per AGENTS.md §3, the next move must shrink N, not add compute.** No amount of further sweeping
over material we already hold can open a gate that needs a key we do not have. A productive next step
requires a **new information class** — a source surface not in `gsmg-web-archive` or either
`gsmg-private` tree — or a genuinely new *semantic* hypothesis about the 103×103 application, stated
with its N, measured rate D, and t = N/D. Anything else is a repeat.

### 5. Stale-item bookkeeping (so it stops being carried as pending).
`analysis/RAW_PW.md` needed no B2 update: lines 27-30 already carry the certified ladder through
`B2_79` (sha `b40fce72…`) and `E_S = B2_79[64:79]`, completed in `5a9062d`. It is done, not pending.
