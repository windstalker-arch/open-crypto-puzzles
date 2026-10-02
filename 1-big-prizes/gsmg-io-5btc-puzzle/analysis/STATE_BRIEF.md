# GSMG 5-BTC Puzzle - Solve-State Brief (2026-09-24, addendum 2026-09-27)

> **VERIFIED STATUS (2026-09-27, `R-VERIFY`).** The certified chain below is no longer a set of
> recorded claims - it has been **re-derived from first principles and re-verified**: run
> `python3 tools/verify_ladder.py` (41 checks, exits 0). The whole ladder follows from **canonical
> BLOB1 + RAW_PW** alone, including `WIF(K_C1)` being the BLOB2 password, so the chain closes on
> itself. All five opened envelopes confirm by **exact re-encryption round-trip**. All four ladder
> addresses re-derive and **all four differ from both gate addresses**. No key recovered; both gates
> open; that null is now verified rather than assumed.
>
> **One identifier was corrupted in a session summary and is corrected here:** `ADDR_C2` =
> `135Cf6ASyU2PDHuxA1Edc3mHYtxEsZNPCa` (34 chars, h160 uncompressed
> `16bba55c93148e78ce946caad0115bb8248f2f09`). A 33-char `...ASy2PD...` form has circulated in
> summaries; it is a dropped `U` and appears nowhere in the artifacts. If you reuse any identifier
> from a summary rather than the ledger, re-derive it once.
>
> **Cheap leads are exhausted.** The `abbaabab...` residue is a certified author-page artifact
> (`R-DIGRUN`), and the phase-3.2 prose is closed by `R-EBCDIC1141` plus the FINDING 3/5 rows.
> ~~The 1539-byte period-15 blob has failed three independent parameterisations under proper held-out
> testing and a corpus-wide sweep found no second ciphertext. Exactly **one** direction survives from
> `R-P32BLOB`: treat the 26 byte-values as non-alphabetic data (base-N / bit-packed). It is
> expensive, speculative, and unguided.~~ **CORRECTED 2026-09-29 (`R-BRIEFAUDIT`, `R-P32KEYVERIFY`):
> THE 1539-BYTE BLOB IS SOLVED.** `R-P32KEY` (key `amphtaclwmtbvfz`, 2026-09-26) decoded it;
> `tools/p32key_verify.py` re-derives and round-trips it (`R-P32KEYVERIFY`), and the headers of
> `R-P32BLOB`/`R-P32BLOB2`/`R-P32BLOB3`/`R-P32FLAG` now carry retraction tags (`R-CERTAUDIT`). The
> "one surviving direction - treat the 26 byte-values as non-alphabetic data" is **WITHDRAWN as
> moot**: the bytes ARE a letter substitution and it was decoded. **Do not re-attack this blob.**
> The remaining gap looks **interpretive, not mechanical** (Lead 0's map-search).
>
> **Tile corpus is now CLOSED as gate input (2026-09-28).** Four rows land after this brief's 2026-09-27
> addendum and none of them opens a gate; they retire false leads so no session re-treads them.
> Read them in order, they are one narrative:
> - `R-GICBIG` - `red_crypto_gic` renders `CRYPTO + GIC`, not `CRYPTO + BIG`. The slug was right all
>   along, which kills the seed/plant split's only supporting tile.
> - `R-LOCKFRAG` - the two "unreadable, letters touch" padlock tiles are readable. They do not spell
>   their whole slugs: they render `lo` and `n ing`, with the padlock icon supplying "lock" and "open
>   lock". 6 text glyphs; the 7x9 keyholes are excluded as pictures, not transcribed as `T`.
> - `R-MICROBAND` - retracts a false claim that a connector rectangle was cut between the banking icon
>   and the band below it. Rows 46-53 are empty; the three 6px blobs need no cut and are non-letter
>   scale for this face.
> - `R-ASSEMBLY` - the slugs are a `COLOUR_REST` template, the colour prefix is not text, and 7 of 7
>   testable slugs agree with their pixels. Page order is exactly `sorted()`, so it is a directory
>   listing and carries no authorial signal. No anaglyph offset, no hidden channel.
>
> Net effect on the crux: **none.** No new candidates, no oracle calls, `X` still unsolved. What
> changed is that the tile set is no longer a place where a session can spend a cycle: the four
> questions it used to invite - seed vs plant, the "touching letters", the cut connector, and page
> order - are all answered, three of them against the earlier claim. `tools/tile_glyphs.py` is the
> reproducer (35 selftest assertions, `--selftest`).
>
> One tile item is still open and needs eyes rather than thought: the 44px icon in
> `black_banking - war`, whose upper mass reads as a caret/lambda shape (two diagonals meeting at a
> top apex) rather than the padlocks' arch (a dome), and whose lower box is undescribed. It is not
> blocking, because `R-ASSEMBLY` closes the tile corpus either way.

One-page onboarding for any solver/agent/contributor. Companion to `AUDIT-2026-09-20.md`
(invariant + certified-boundary audit) and `analysis/leads.md` (ranked, dated leads).
Ledger: `analysis/tested.md` (all rows below).

## The situation

gsmg.io (2019), 5 BTC split across two funded gate addresses. All *solved* stages were
solved by 2021. We certify ORACLE-level negatives for every mechanical decode family; the
single live crux is Lead 0 = the **interpreter-alphabet leap**. The funded gate remains OPEN.

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
  *cross-validation* -- looking for those 15 bytes independently -- not a search for something unknown.

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

> **SUPERSEDED 2026-09-28, by `R-BOARD28B` and `R-BOARD28B-ADDENDUM` (both 2026-09-26), which are
> later than the paragraph above and win.** There is **no missing 28-char interpreter alphabet to
> find**. 28 is cipher arithmetic, not a clue (10 digits - 2 escapes = 8 plain cells, + 10 + 10
> escape-row cells = 28, `tools/certified_vic.py:58-71`), and the letters were never missing: they
> are the author's, from the Phase-3.2 sentence "A fubcd-king & oracle-queen, thingky mvps, on a sad
> board but as wide as the first one seen." `R-BOARD28`'s "the missing alphabet must be a
> permutation of the board" is WITHDRAWN as unfounded. Lead 0's open quantity is the
> **application** (digit map / escapes / transposition) on `dbbib_91 + faed_570`.
> `R-BOARD28B-ADDENDUM` goes further: the mechanical surface is EXHAUSTED and the crux is
> **unspecifiable, not merely unsolved**, so do not run another cipher sweep on
> `dbbib_91` / `faed_570`; meet any such proposal with `tested.md:8842`. The paragraph above is
> retained for history only.

## What unblocks (pick any)

> **REWRITTEN 2026-09-28.** The previous version of this list was three items and every one of them
> was wrong in the direction the addendum warns about. It is struck rather than amended, because
> `R-BOARD28B-ADDENDUM` FINDING 1 holds that "a pointer that sends the next session into a closed
> surface is worse than no pointer". Detail on each retraction is in the note below the list.

1. **A new authorial string or artifact** - the only class that has ever produced a result. Per
   FINDING 5, the productive work is reading the author's own pages, transcript, images and groupchat
   *for semantics*, never decoding the streams. Still-open objects: the pre-edit Telegram snapshot
   (2025-04-28 20:01-20:20), the restated "ca" formula text, and any post-2026-09-24
   hint or statement. Note that the two best-looking files have already been mined: `GSMG_JRK.md`
   (427 creator messages) is closed by `R-JRKCORPUS`, and the solver-group image surface is closed
   by `R-SOLVERGRP-STR` and `R-MATRIX69`.
2. **A human visual read** - the one acknowledged gap, and the only item here that is not a
   speculative guess. `analysis/lead0-inspection-checklist.md` still applies, but its three "live
   micro-items" are closed and must not be re-offered:
   - the FEFEFE nest cell at grid (7,4) is **pinned and closed** by `R-FEFEFE-LOCATE` (it holds a 0
     bit, so the URL decode is unchanged) and its escape-key axis is closed by `R-FEFEFE-ESC-KEYBOARD`
     at 0 MATCH;
   - the missing `.` marker and the lone `/` are **mechanically exhausted** by `R-BOARD28B`, which
     enumerated every punctuation variant of the board on both gates at 0 MATCH. That row explicitly
     preserved the *human* question of which dot is the anomaly, but the follow-on `R-BOARD28B`
     withdrew the missing-alphabet framing that the question depended on, so the item no longer has a
     well-posed mechanical form.
   - the one tile question still genuinely open is the 44px `black_banking - war` icon, which is not a
     Lead 0 micro-item at all: it is a tile-corpus item, and `R-ASSEMBLY` treats the tile corpus as
     closed gate input.

3. ~~**Alphabet hypothesis** (any word/phrase) -> `tools/lead0_try.sh`~~ - **RETRACTED.** "Any word or
   phrase" is not an unblocker, it is a guess, and `R-BOARD28B-ADDENDUM` FINDING 4 records this
   session twice proposing a mechanical direction and withdrawing it on contact with the ledger.
   `tools/lead0_try.sh` still works and is still the fastest path *if* an alphabet ever arrives from
   an authorial string under item 1, but the tool's existence is not a reason to try one. Its
   `fubcdora/lethingkymvpszjqwx.` default board is the withdrawn `R-FORK` hypothesis.

No further battery is warranted without item 1 or item 2; per `AGENTS.md` we do not re-run closed
rows. The honest standing position is FINDING 4: the mechanical surface is exhausted and the crux is
**unspecifiable, not merely unsolved**. That is a statement about the search, not a licence to
manufacture activity, and a session that produces zero candidates after honest inventory has
succeeded, exactly as `R-JRKCORPUS` did.
---

# Addendum 2026-09-26 (rows `R-LOGO2`, `R-PACKCRYPTO`, `R-PHASE2-2026-09-26`, `R-COVERAGE-2026-09-26`)

The crux is unchanged: **Lead 0's keyed 28-char alphabet is still the only live gate**, and
no battery below was widened. Four sessions' work closed negatives and removed process
risk. Three items change how you should work.

> **SUPERSEDED 2026-09-28: see the note under "The crux (Lead 0)" above.** `R-BOARD28B` and
> `R-BOARD28B-ADDENDUM` (2026-09-26) retire the "28-char alphabet is the only live gate" framing:
> no such alphabet is missing to be found. The live gate is the **application** on
> `dbbib_91 + faed_570`, and the mechanical surface is declared exhausted. Retained for history
> only.

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

**Phase 3.2 is SOLVED (2026-10-01, `R-P32OPEN`).** ~~is structurally blocked, not search-limited.~~
The passphrase is `jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple` and it
**does** open the envelope, byte-exactly. The blocker below was an artifact of a battery that
could not have detected success: `tools/phase32_probe.py` never derived the IV, and its
`padok` test is **IV-blind** (PKCS#7 validity depends on the key alone). Correct derivation:
`EVP_BytesToKey(md=sha256)` with the password as the **hex-digest ASCII string**
`250f3772...1ce4c`, **key = stream[0:32], IV = stream[32:48]**. Certifier
`tools/p32_evp_verify.py` (selftest 4/4); plaintext promoted to `data/phase3.2-plaintext.b64`,
2,422 B, sha256 `b82afeb8...`, byte-identical to the community fork. **The "2026
re-encryption" inference is retracted - there is one era, not two.**

**What is actually open now** is unchanged apart from this: Lead 0's 28-char alphabet, the
`faed`/`dbbib` map-search application. **NOT** the 149-digit number line in the
phase-3.2 prose: that is decoded and independently re-verified (`R-VIC149`,
`tools/certified_vic.py`, 91-char message reproduced byte-exact). An earlier
version of this sentence here said "150-digit" and left it open; the count is
**149** and the item is closed.
NOT the trailing `U2FsdGVkX1+0Wl49gnWTyiimluu7V3...` blob in that plaintext - I briefly wrote that
as an unopened fifth envelope and it is wrong: it is byte-identical to the **already-solved** B2
envelope (`salt b45a5e3d827593ca`, ct 80 B, `tools/rung2_b2.py`, password = derived
`WIF(K_C1)`, plaintext `data/B2_79B.bin`; `ALL ANCHORS HOLD` re-verified).

**Historical note (retracted, kept for provenance).** The reasoning that led here:
The obvious derivation was already tried and is the *correct* one
(`jacquefresco` + `giveitjustonesecond` + `heisenbergsuncertaintyprinciple` maps onto all
three riddles) and it returned nothing, so the password is not recoverable from the visible
clues - consistent with the 2026 capture being re-encrypted. No battery warranted per AGENTS.md.

**Now witnessed rather than asserted (R-P32BYTES).** The `s.43` note that the envelope was
"NOT in our local captures" was wrong: it was held all along in the briefcase and had simply
never been promoted into `data/`, so the blocker was recorded from a directory listing instead
of a search. The bytes are now certified (`data/phase3.2-envelope-2026.b64`, blob sha256
`9d172dc0...`, ct sha256 `48a77592...`, 2,432 B = 152 blocks), with provenance proved by the
fact that the same source's 1,792-char cosmic blob is **byte-identical** to ours
(`b1895055...`) and its truncated 32-byte fork copy is an exact **prefix** of the ciphertext -
one era only, no second version. **[SUPERSEDED 2026-10-01 by `R-P32OPEN` - the "13 key/IV
derivations" listed here never include the IV that OpenSSL actually uses, and `padok` is
IV-blind, so this battery was structurally incapable of detecting the correct derivation.
The envelope is NOT a re-encryption and the password is NOT unrecovered. Text retained
below as the record of the wrong turn.]** Against that, the 2020 password under **13** key/IV
derivations (raw `sha256(pw)` at three IVs, `sha256(sha256(pw))`, the phase-3 key, and
`EVP_BytesToKey` md5/sha1/sha256/sha512 with and without the salt) gives **0 valid pads** and
printable 0.36-0.40. Since the 2020 copy opens under exactly that password, the envelope in
hand is the 2026 re-encryption. The blocker stands, reclassified from *missing artifact* to
*password unrecovered* - same outcome, no longer resting on a retrieval excuse.

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

> **SUPERSEDED 2026-09-28: see the note under "The crux (Lead 0)" above.** The sentence above is
> wrong on the "missing 28-char alphabet" point, per `R-BOARD28B` / `R-BOARD28B-ADDENDUM`
> (2026-09-26). The letters are the author's and were never missing; the open quantity is the
> application. Retained for history only.

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
  currently-specifiable reads of the crux are negative on both gate addresses").
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

## ADDENDUM 2026-09-27 (2) - `R-FAEDBASE`: the DECODED faed plaintext is MEASURED RANDOM. Stop reading it as text.
- The only lever that survived `R-P32BLOB2`'s retraction is the **IC curve**, because IC is permutation-invariant. Applied to the
  full 570-character Bifid **plaintext** - never before done, since every prior base-N read hit the RAW streams or the post-split
  objects (s.60) - it settles the question with a measurement instead of a failed sweep:
  - `even285` (285 symbols, 4 letters): **IC 0.2554** vs random 0.25. `odd285` (285 symbols, 25 letters): **IC 0.0503** vs
    random 0.04. Both **flat across p = 1..15** (no Vigenere period), in explicit contrast to the 1539-byte blob's clean
    1.52x period-15 signal. `full570` IC(1) = 0.0941 is itself just the mod-2 signature.
  - **CORRECTION (see ADDENDUM 2026-09-27 (h) / `R-FAEDCOORD`): the "seed material, not an encrypted text" clause above is
    WITHDRAWN as an over-claim.** What the measurement actually supports is the narrow statement that no *frequency-invariant*
    read of the streams recovers natural language. IC is invariant under relabelling and therefore blind to positional structure,
    and there IS a hard positional structure here. The even/odd 4-vs-25 alphabet split below is fully explained and is NOT a
    discovery. Retained table is still valid; the inference drawn from it was too strong.
- The base-N read is separately dead: 16 reads over 4 objects x 2 alphabet orders x 2 directions x 2 offsets, **0 beat their own
  refit-on-shuffled null** (printable 0.387 real vs 0.386 null; 0 trigrams both sides). The author's own digits->integer->**hex
  text**->bytes convention is the code path, and the certified z-segment witness is what forced the two details I had wrong.
- **Cross-check (new):** 25 byte-forms (utf8 / lowercased / 5-bit packed over the cipher's own 25-letter square / idx0 / idx1) of
  `full570`/`odd285`/`even285`/`object256`/`dbbib91` x 4 digests = 100 hashes against 119 documented hash tokens: **4 matches, all
  already the `salphaseion` set.** No derived form links faed to any other artifact. The 5-bit packings are new and unreferenced
  - `full570` -> **356 B**, sha256 `8d2f2f83...`; `odd285` -> 178 B `672d0f92...`; `object256` -> `fb347d36...`;
  `dbbib91` -> `56e74a8d...`. Role undetermined, and the only genuinely new byte-objects this session produced.

## ADDENDUM 2026-09-27 (3) - `R-P32BYTES`: Phase-3.2's bytes were never missing. Blocker reclassified, still stands.
- The `s.43` blocker note ("salt `eefc4c5befc1656a` is NOT in our local captures") was **wrong** - the envelope was in the briefcase
  the whole time and had simply never been promoted into `data/`, so a directory listing was mistaken for a search result. Now
  certified at `data/phase3.2-envelope-2026.b64` (blob `9d172dc0...`, ct `48a77592...`, 2,432 B = 152 blocks), with provenance
  proved rather than assumed: the same source's 1,792-char cosmic blob is **byte-identical** to ours (`b1895055...`) and its
  truncated 32-byte fork copy is an exact **prefix** of the ciphertext. **One era only - there is no second version to diff.**
- The 2020 password fails under **13** key/IV derivations with **0 valid PKCS#7 pads** (printable 0.36-0.40). Since the 2020
  copy opens under exactly that password, the envelope in hand is the 2026 re-encryption. Practical outcome unchanged, but the
  blocker no longer rests on a retrieval excuse. Do not re-run the retrieval; it already succeeded.

## ADDENDUM 2026-09-27 (4) - correction to the source re-check.
- Naddiseo issue **#15** (`Claude/neo continuous puzzle oc0qvx`, 2026-09-25) is a **different** puzzle; #13/#14 are the DBBI/FAED
  threads already covered. `halbgott29a/gsmgio-5btc-puzzle` is **not** a new source (already audited at `late-321`, 7.1 MB, 51,177
  msgs).
- **The live-fetch route is CLOSED (`R-LIVEFETCH`), and it was never the open item I treated it as.** `gsmg.io/robots.txt` is
  `User-agent: *` / `Disallow: /` - already recorded at line 3024 - and the routes are 404 regardless: `/salphaseion`,
  `/phase1verification`, `/door`, `/choice`, `/ca` all 404; only `/puzzle` (29,931 B, sha256 `38125bbf...`, **not** our stored
  `live_salphaseion.html` at 4,536 B) and `robots.txt` return 200, and `/puzzle` carries **none** of
  `dbbib`/`faed`/`salphaseion`/`cosmic`/`matrixsumlist`/`lastwordsbeforearchichoice`/`thispassword`/the two salts. Per line 3720
  the SalPhaseIon page was reached once and consumed. **The 404 is NOT a site-state delta** and must not be written up as one.
  I issued six GETs before re-reading line 3024; nothing was promoted into `data/` and no finding rests on them, but that
  fetch should not have happened.

## ADDENDUM 2026-09-27 (5) - where the frontier stands after this session.
- Unchanged and not moved by anything above: both gates funded, no key recovered, Lead 0's keyed 28-char alphabet still the only
  live semantic crux, and (CORRECTED 2026-09-29, `R-BRIEFAUDIT`: this line was already stale when written - `R-P32BLOB` was SOLVED the previous day by `R-P32KEY`, key `amphtaclwmtbvfz`) the surviving mechanical direction is **none**. What changed is that **one whole family is now
  closed by measurement** (faed is not text) and the last "blocked because missing" object is **certified present and confirmed
  re-encrypted**. **[CORRECTED 2026-10-01, `R-P32OPEN`: "confirmed re-encrypted" is FALSE. The Phase-3.2 envelope decrypts
  byte-exactly under the community passphrase via `EVP_BytesToKey` with IV = stream[32:48]; one era, not two.]**
- **Both cheap next moves from this session are now spent or closed.** The live re-fetch is closed by robots + known 404s. The
  only untried item left is genuinely small: the **five new 5-bit-packed byte-objects** (`full570` -> 356 B `8d2f2f83...`,
  `odd285` -> 178 B `672d0f92...`, `object256` -> `fb347d36...`, `dbbib91` -> `56e74a8d...`, plus the faed substreams) have
  never been tried as *inputs* to the 103x103 application, only as candidate plaintexts. **[CLOSED 2026-09-29 - run as `R-PACK5-103INPUT`: INAPPLICABLE, not untried. The 103x103 application consumes exactly 10609 bits (1327 B); every one of these objects is 18-356 B, i.e. 1.4%-26.8% of that, and all six raise `IndexError` before emitting any output. Zero-padding to 1327 B was tested too and fails the tool's own base-38 band check on all four, so the negative does not rest on the crash alone. Witness-backed: the real 1327 B anchor re-found through the same code reproduces the documented `1JG648ya...`/`145ZQ9si...` with `all chars in 80..117 = True`. The standing "only untried item" is therefore spent. Separately, the `dbbib91` anchor `56e74a8d...` in this same list does not reproduce - see `R-PACK5-103INPUT` FINDING 3.]**
- Per AGENTS.md §3 the next move must **shrink N**, and after `R-LIVEFETCH` the sanctioned routes to a new information class are
  exactly two: the Wayback/`gsmg-archive` captures already in hand, or a primary authorial artifact. If neither yields a new
  surface, the correct answer is to **stop searching and say so** - not to keep sweeping material we already hold.

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
  `:8849` (rotation family exhausted, certified-negative on both gate addresses), `:8845` (convention blocker already resolved), `:12254` F4
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
**Additionally, the chain-4 key is now 32/32 on-puzzle.** `E_B[:2] = 59cc` was the last community-sourced byte-pair; `tools/eb_tail_sweep.py` sweeps all 2^16 two-byte tails against the published chain-4 hash `e4269ed5...` and finds **exactly one**, `59cc` (N=65,536, D=20,666/s, t=3.2 s, 267 PKCS#7 survivors vs 256 expected, 1 hash hit, 0 oracle calls). It is *determined*, not quoted. This does not make the chain creator-authenticated -- the acceptance anchor is community-published -- but the quoted value and an exhaustive independent search now agree.
**Consequence for the frontier:** the chain-4 key is no longer a blocker. The missing operand is `ca`/`cosmic_A`, referenced only by the 32-bit SHA-256 prefix `cd3fea3d...` (#92), with the creator disavowing a "step after Cosmic Duality" (#104). Chain-4 is a 31-byte header (`+-` marker) plus 35 x 32-byte blocks, printable fraction 0.346 -- an XOR-triangle operand grid, not text.

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
`as wide as the first`) -- raw and whitespace-stripped. **All zero.** Controls passed
(whitespace-insensitive SalPhaseIon controls in 4--5 witnesses), so the nulls are witnessed, not
uncertified. Phase-3.2 is not among the only two archived real puzzle pages. The earliest dated
community witnesses are issues #74/#75/#76, all 2026-02-16, inside a batch the ledger itself flags
as partly AI-slop -- one lineage, not independent corroboration.
Consequence: even **granting** the community sentence, the exact string is **1 of 84,240**
(`5!` orderings × 27 × 26 punctuation placements), so `METHOD-I` remains valid only for the one
string it actually tests. Do not let "we have the alphabet" slide into "we have the sentence."

### 2. The solver-group pack is now fully triaged, and one of its files is a rickroll.
42 -> 89 files (121 MB); the 52 newest were triaged. `4E.zlib` is a pure 4.2% recompression of bare
`4E` (sha `d4a224bc…`, zero new information); `4E` is binary 4-byte-expanded sparse pixel data, not
whitespace-prefixed text. `found.txt` is a failed 1GSMG vanity scan (30 MB, 459,300 lines, 153,100
key triples) containing neither gate nor target pubkey. `jrk-history.txt` decodes -- MSB bytes, byte
reversal -- to a payload prefixed `BASE64` and is a **Rick Astley rickroll**
(`aHR0cHM6…` -> `https://www.youtube.com/watch?v=dQw4w9WgXcQ`), positively identifying the file as a
solver shitpost. Do not promote its "13 is default / C is the 2nd hint". A 227-char community
`phase_3_password` and 28 headline restorations both fail both blocked blobs. 19 candidates drawn
from all four ladder keys × 6 blobs × 2 KDFs = 228 attempts, 0 decrypts. **Nothing here is a lead.**

### 3. `author-wallet.txt` is OURS, not the author's -- filename trap.
`~/briefcase/gsmg-private/author-wallet.txt` says "Generated 2026-09-22" and its body is our own
certified chain, our own field layout, our own gate balances and DCL findings. `K_C1`'s hash160
matches inside it, which is **circular, not evidence**. In a directory named `gsmg-private` that
also reads as "the author's private material." Never cite it as authorial attestation.
(`gsmg-solved.json` and `keyFOUND.txt` are, by contrast, fully correct and honestly self-retracting --
only their filenames mislead.)

### 4. Where this actually leaves the puzzle -- read before proposing another battery.
Every surface reachable from this device is now accounted for. The two blocked envelopes remain
password-blocked (`9fbc451d`, 4,090 B; `eefc4c5b`, 2,432 B), `ca/cosmic_A` is still missing, the
Phase-5 ciphertext location is genuinely lost with its Scribd document (the recovered command line
is truncated at `-pass`), and Lead 0's interpreter *application* is the only live semantic crux.
The author-quote vocabulary is not a fresh option: `late-310` already swept 325 forms of it.

**Per AGENTS.md §3, the next move must shrink N, not add compute.** No amount of further sweeping
over material we already hold can open a gate that needs a key we do not have. A productive next step
requires a **new information class** -- a source surface not in `gsmg-web-archive` or either
`gsmg-private` tree -- or a genuinely new *semantic* hypothesis about the 103×103 application, stated
with its N, measured rate D, and t = N/D. Anything else is a repeat.

### 5. Stale-item bookkeeping (so it stops being carried as pending).
`analysis/RAW_PW.md` needed no B2 update: lines 27-30 already carry the certified ladder through
`B2_79` (sha `b40fce72…`) and `E_S = B2_79[64:79]`, completed in `5a9062d`. It is done, not pending.

## ADDENDUM 2026-09-27 (h) - `R-FAEDCOORD`: the 4-vs-25 even/odd split is a TAUTOLOGY of the keyed square. One over-claim withdrawn.

This is a genuine false positive, killed before it entered the frontier. It is recorded because the
surface looks extremely promising and would otherwise be re-derived by the next session.

**The observation.** `even285` has a 4-letter alphabet, `odd285` has 25. The 4 letters are exactly
`BCDE` = square indices `{0,1,5,6}` = cells `(0,0),(0,1),(1,0),(1,1)` -- the **top-left 2x2
sub-square**. Under a uniform-random plaintext, every even position landing in one 2x2 cell block
has probability `(4/25)^285 ~ 1e-152`. That reads as a hard authorial constraint, and as the first
new structural find in this puzzle.

**The certified mechanism (`tools/faed_coord_decomp.py`, `SELFTEST PASS`).** From
`tools/bifid_repro.py:39-52`: `combined = [r0,c0,...]`, `h = len(block)//2`, `rs = block[:h]`,
`cs = block[h:]`; with `period == len(input)` and `len` even, `h = 285`, so
`plain[k] = grid[r[k//2]][r[285+k//2]]` for even `k` and `grid[c[(k-1)//2]][c[285+(k-1)//2]]` for odd
`k` - a **row-row** product at even positions, **col-col** at odd. Reproduced bit-exact.

The faed raw alphabet is `{a..i}` -> `{A..I}`, and in the keyed square `A..I` occupy **9 of the 10
cells of rows 0-1** (`K=(1,4)` unused). So input rows are confined to `{0,1}`:
- even positions = product of two row indices -> at most `2x2 = 4` cells = `{D,B,C,E}`
- odd positions = product of two column indices -> up to `5x5 = 25` cells

The split is **forced**, and `{A..I}` is exactly `ALPHABET[0:9] == "DBIFHCEGA"` - the first nine
characters of the square's own key string.

**Killed false positive.** `P(9 random cells occupy exactly 2 of 5 rows) = C(5,2)*C(10,9)/C(25,9)
= 100/2042975 = 4.9e-5` (1 in 20,430) looks like a 1-in-20,000 endorsement of the community square.
It is **vacuous**: the square was built from the key string `DBIFHCEGA...` and the faed alphabet is
that string's first nine letters, so the property is true by construction. **A square search must not
score candidates on "places the faed letters in exactly 2 rows" - that scores an artifact.**

**Over-claim withdrawn.** ADDENDUM (2)'s "seed material, not an encrypted text" is **retracted**.
IC is invariant under relabelling, hence invariant to positional/coordinate structure, hence blind
to the 2x2 confinement. IC(1) = 0.0503 on `odd285` is fully compatible with hard positional
structure. IC supports only: *no frequency-invariant read recovers natural language.* This is now a
standing correction on how IC evidence may be used anywhere in this puzzle.

**Cheap closure of a newly opened surface.** The decomposition exposes two bit channels never
extracted before: `even285` as a **2-bit (base-4)** channel, 285 symbols = 570 bits; and the raw
faed **row channel** at exactly **1 bit/symbol** = 570 bits. 6 packings (base-4 MSB/LSB; row-channel
MSB/LSB at 71 B and 72 B) vs **1,974** documented 64-hex tokens from `analysis/tested.md`,
`analysis/STATE_BRIEF.md`, `data/*.json`: **0 hits.** N = 6, t negligible. The 570-bit channels are
new unreferenced objects; `even_base4_msb` 71 B `2604de566aa7d78b359c6063...`,
`rowbits_msb_71B` 71 B `2133ae9cc5e35678ca4cd0b5...`.

**Reusable byproduct.** The whole downstream object family (`full570`, `even_stream`,
`odd_pre_reduction`, `object_256`, `dropped_29`) is a **deterministic function of
(raw faed, period, square)**. A candidate square is rejected by a single `plaintext_head`
comparison - **O(1) per candidate**, not O(570) plus a full reduction. Any future square search
should exploit this and must not re-run the reduction per candidate.

**Net frontier effect: none.** No gate input, no oracle call. Two gates verified funded earlier this
session. (CORRECTED 2026-09-29, `R-BRIEFAUDIT`: there is no surviving mechanical frontier - `R-P32BLOB` was SOLVED by `R-P32KEY`.) The only live semantic crux is
still Lead 0's keyed 28-char alphabet application. This row adds a retracted over-claim, a killed
false positive, a standing methodological correction, and a square-search screening rule.

## ADDENDUM 2026-09-29 - `R-BRIEFAUDIT`: this brief's OWN status block was stale on the one object a new session meets first.

- The top "VERIFIED STATUS" block asserted the 1539-byte period-15 blob "has failed three independent
  parameterisations ... a corpus-wide sweep found no second ciphertext", and named "exactly one direction
  survives from `R-P32BLOB`: treat the 26 byte-values as non-alphabetic data". Both were **stale**: the blob
  was SOLVED 2026-09-26 by `R-P32KEY` (key `amphtaclwmtbvfz`) and certified 2026-09-29 by
  `tools/p32key_verify.py` in `R-P32KEYVERIFY`. The recommended direction is **moot** - the bytes ARE a
  letter substitution, already decoded.
- The same staleness appeared twice more: ADDENDUM 2026-09-27 (5)'s "the surviving mechanical direction still
  `R-P32BLOB`" (already false the day it was written, since `R-P32KEY` predates it) and `R-FAEDCOORD`'s closing
  "the surviving mechanical frontier is still `R-P32BLOB`". All three now carry dated inline corrections.
- **This is the `R-P32FLAG` failure mode one document level up.** `tested.md` carried **four** rows telling a
  future session the blob was unsolved (`R-P32BLOB`, `R-P32BLOB2`, `R-P32BLOB3`, `R-P32FLAG`; `R-CERTAUDIT` tagged
  three and missed `R-P32BLOB`, whose refutation was outright false - `R-BRIEFAUDIT` fixed it); this brief - the
  document read FIRST - had three more. A frontier summary that
  mis-states its own headline object is worse than a stale ledger row, because it is the entry point.
- **Method rule (extends `R-CERTAUDIT`):** when a solve supersedes a row, sweep BOTH the ledger and every summary
  document that names the object (`STATE_BRIEF.md`, the README "open leads" list, `leads.md`). A correction that
  lands only in `tested.md` is half a correction.
- Status: documentation only. No new key, no new plaintext, 0 candidates, 0 oracle calls, `X` unsolved, both
  gates unchanged.

---

## 2026-09-29 addendum: "Swept" and "swept the right object" are not the same claim (`R-DBBIBFIELD`)

- `data/finalpage-digit-streams.json` carries two dbbib fields. `dbbib_91` (91 tokens) is
  authoritative; `dbbib` (69) is the superseded OCR crop, which is the authoritative object
  with a 22-char run DELETED at offset 45. 91 = 7x13 exactly; 69 is not, so a 7x13 grid on the
  crop silently truncates.
- The crop is not a benign degraded copy: the deleted 22 chars are the evidence that motivated
  the 2026-09-07 reinstatement in the first place.
- `tools/lead0_vicgap.py` read the crop while printing `dbbib(91)` on every output line. So
  late-58's "the last structural gap is now closed ... applied to dbbib(91)" certified a
  family that was never run on the 91-token object. late-150's BUG-2 assurance that "recent
  sweep rows were all re-derived on the live 91-token object" is FALSIFIED by it, and BUG-2
  named 5 stale readers where a full scan finds 34.
- Re-run on the authoritative object: 393 candidates x both oracles, 0 MATCH, top scores all
  degenerate. late-58's CONCLUSION is unchanged and now actually earned; its date and basis
  were wrong. The faed half was never affected.
- `tools/stream_field_audit.py` (17/17 selftest, --check rc=0) now enforces the split
  mechanically and classifies tools OK / DUAL / STALE / CRITICAL, where CRITICAL is the
  late-58 shape (reads the crop while claiming 91). CRITICAL = 0 today. 34 STALE remain:
  flagged, not fixed - they are historical sweeps and this claims nothing about their results
  beyond the mechanical fact that a future re-run would mis-test.
- **Method rule (new):** a negative is only certified if the row records WHICH FIELD the
  instrument loaded, and the instrument's own printed label is checked against it. A tool that
  labels its output `dbbib(91)` while reading 69 tokens defeats every downstream reader, because
  the label is what gets trusted. Prose flags ("remaining stale readers flagged") failed here
  exactly the way a prose retraction once did - the flag has to be a checker.
- Status: one tool load-line fixed, one optional `--emit` added, one new checker. No new key, no
  new plaintext, 0 candidates, 0 oracle MATCH, `X` unsolved, the funded gate unchanged
  (125635374 partially-spent / 375055856 funded-unspent, both OK 2026-09-29).

---

## 2026-09-29 addendum 2: four more "closed" families were closed on the crop (`R-DBBIBFIELD2`)

- `R-DBBIBFIELD` fixed the single tool that mislabeled the 69-token crop as the 91-token
  object and left the other 34 flagged. Testing that flag found it wrong twice over:
  - 18 PRE-2026-09-07 rows cite a crop-reading tool, so their dbbib side is void under
    BUG-2's own rule. Grouped by family, four had NO post-reinstatement `dbbib_91`
    coverage at all: the ciphertools 19-cipher suite, its composed combinations, the
    z-segment Bifid family, and the keep-one-position / XOR half-triangle readings.
    `leads.md` described the ciphertools menu and its four combinations as "closed" -
    on the crop.
- All four re-run on `dbbib_91`: 1,270,255 oracle-line evaluations, 0 MATCH on either
  funded gate. The closures now hold on the authoritative object, which is the first
  time that has been true for these families. The z-segment family carries its own
  soundness witness (faed -> Bifid(DBIFHCEG, full) reproduces the stored plaintext head).
- A truncated oracle run was caught, not trusted: the combo sweep's dualite result file
  held 191,310 records against a 237,824-line input, 46,514 candidates unevaluated, cut
  mid-stream with no trailing newline. Byte-comparison showed it was a strict prefix of
  a fresh full run, so it was a killed process rather than a divergent answer; re-run to
  237,824/237,824. A wrapper printing `MATCH=0` after a truncated child is the same
  failure shape as the rest of this session, and checking was what caught it.
- `stream_field_audit.py` is 24/24 with CRITICAL 0 / STALE 29 / DUAL 10 / OK 51. It was
  itself corrected twice while being used: broadening the pattern from two read
  spellings to three exposed `zseg_bifid_sweep.py` (previously invisible), and the
  broadened pattern then over-corrected into a false positive on `phase322_literal_sweep.py`,
  which hardcodes the correct 91-token literal and uses `"dbbib"` only as a key/label. That
  false positive is now a pinned regression test.
- **Method rule (new):** a sweep wrapper's own `exit=1 lines=N MATCH=0` is not evidence
  that N candidates were tested. Check the record count against the input line count and
  confirm the output ends in a newline; a short file is a truncated child, not a negative.
  And a checker written to prevent a specific failure must itself be regression-tested
  against the tools it is supposed to clear, or it will clear a correct tool by accident.
- NOT claimed: 12 rows remain void-but-unrepaired and 29 tools remain unrepaired. No
  blanket clearance, no positive altered, nothing retracted. X unsolved, 0 new candidates,
  0 oracle MATCH, the funded gate unchanged.

---

## 2026-09-29 addendum 3: the void list worked down; one family skipped on N/D grounds (`R-DBBIBFIELD3`)

- Precise accounting: 18 rows are void on the dbbib side, not the 14 stated in
  `R-DBBIBFIELD2` (over-count, corrected). 6 were cleared by the previous pass, leaving 12.
- Six of those families are now re-run on `dbbib_91` - ciphertools Bifid blank-period (480),
  Bifid-into-pipeline (19), Base58 (34), white-rabbit columnar (56), section-title keywords
  (2,576 lines), Beaufort/Vigenere (560) - **3,314 oracle-line evaluations, 0 MATCH on both
  gates**, each confirmed by matching the oracle's record count to the candidate file's line
  count, so none is a truncated child.
- The exhaustive 9! interpreter-permutation sweep (row 145) is fixed to read `dbbib_91` but
  **deliberately not run**: N = 2,903,040 lines per gate, D = 263.2 perms/s measured,
  t = 6.1 h for both gates. Above the two-hour line the rule is a constraint that shrinks N,
  not more compute. Its dbbib side stays void and that is stated, not hidden.
- `lattice_probe`, `xor_pyramid_research`, `matrix_solver`, `cosmicd_base64idx_sweep` have
  their load line corrected but are **not** re-run, so their dbbib sides are still void.
  A fixed load line is not a re-run.
- Two of my own errors, both caught before any claim: a `ciphertools_bifid_sweep.py` edit
  that renamed the dict KEY while leaving the read as `raw.get("dbbib")` - relabelling the
  bug rather than fixing it; and a `beaufort_sweep.py` one-line patch to a compound
  statement that swallowed the `faed=` assignment into a comment and broke the tool with a
  `NameError`. Every patched tool was executed or its candidate file re-validated after the
  edit. A patch that silences a checker while breaking the instrument is worse than none.
- Checker: CRITICAL 0 / STALE 18 / DUAL 10 / OK 62, down from 34 STALE / 44 OK. The 18
  remaining STALE tools are cited by no void row and no live claim rests on them.
- X unsolved, 0 new candidates, 0 oracle MATCH, the funded gate unchanged. Nothing retracted.

---

## 2026-09-29 addendum 4: one unrecorded out-of-repo Lead 0 note found and adjudicated (`R-LEAD0-STAGED`)

- `~/storage/external/briefcase/LEAD0_FINDINGS_2026-09-28.md` had zero coverage anywhere in
  the repo. Re-measured instead of trusted: capture drift CONFIRMED (four captures, one sha256,
  4536 bytes, zero drift 2020->2026, 2 textareas), its `anstoo` offset WRONG (the page has the
  spaced `a n s t o o` at char 2139, not a contiguous `anstoo` at 2143), and its three binarized
  renders are absent from disk so its pixel measurements are unconfirmed.
- Useful consequence, which the note stated against itself: the below-fold 21% of textarea 1 is
  NOT unrecoverable. The full bytes are in `data/live_salphaseion.html`, so the "read the tail"
  human-eye item is answerable from text and needs no fresh screenshot. Two human-eye items
  remain open: the `theseedisplanted` tile and the 14x14 FEFEFE cell at row 7 col 4.
- **SECOND CORRECTION, larger than the first: `tested.md:330` asserted the page has "no archived
  captures at all". That is FALSE.** `data/wb_dbbib-page_20201112.html` is a 2020-11-12 Wayback
  capture of this exact page, byte-identical to the live copy. The sentence was written 2026-09-07
  and the capture reached disk 2026-09-20, so it was true when written and the corpus has since
  outgrown it. It mattered because that capture is what makes the zero-drift claim checkable and
  it holds the below-fold 21% of the stream. Rule added: any "never archived" claim is re-tested
  against `data/` before being repeated. The other three "no capture" mentions in the ledger are
  about different objects (API routes, the SPA shell) and stand.
- 0 oracle calls, 0 candidates, no lead promoted, X unsolved, the funded gate unchanged. Standing
  process note: a second session's uncommitted notes sat outside the repo for a day.

---

## 2026-09-29 addendum 5: the `theseedisplanted` human-eye item closed from pixels (`R-STRIPGLYPH`)

- All three disputed glyphs resolved without eyes or OCR, from the 8 strip PNGs on disk (md5s
  verify against the evidence manifest; tiles are pure two-tone white-on-colour at 82x70).
  `ca` = plain `C`, no circumflex. The disputed narrow run is a 1px vertical rule, not a
  letter. `lock` is a padlock ICON with `LO` below it, not a glyph row, so `1ock` was never
  available. `red_crypto_gic` re-confirmed as `CRYPTO` + `BIG` from pixels, reproducing
  row 13406.
- My first read was wrong and is logged: I read the padlock body as a block `L` from a cropped
  region, and only dumping the whole tile showed the "foot" was a full-width band 28px across
  against a 5px stroke. Cropping a tile to the question is how the wrong answer looks certain.
- The checklist framed this as needing human eyes on a solver-made image. It needed neither eyes
  nor a model - it needed the observation that the files were on disk and two-tone. "Needs a
  human" is a claim about the question, not the data.
- 0 oracle calls, 0 candidates, no lead promoted, X unsolved, the funded gate unchanged. ONE
  human-eye item remains: the 14x14 FEFEFE cell at row 7, col 4.

---

## 2026-09-29 addendum 6: the last human-eye item closed, and the human-eye class is now empty (`R-GRID14`)

- The 14x14 grid is 785x785, 785/14 = 56.07px pitch, true 14x14, no drawn borders. Full census
  of all 196 cells: field `#F5F5F5`, blue `#4285F4` x15, yellow `#FBBC05` x9, red `#F02828` x1,
  pure white `#FFFFFF` 504px total. The cell-centre read reproduces the ledger grid exactly.
- **Cell (7,4) is RED and is the only red cell in the grid.** Both the red px (x225-279,
  y393-447) and the white px (x230-274, y398-442) lie entirely within that one cell. The
  "FEFEFE cell" is not a cell colour: it is a 45x45 white ring with a small field-coloured
  void, i.e. a nest glyph drawn on a red tile. The checklist item asked whether a colour sits
  at a position; the object at that position is a pictogram.
- Two adjacent misdescriptions corrected while measuring: the grey `#B4B4B4` is image border,
  not a cell value, and the field is `#F5F5F5`, not `#FEFEFE`. Three distinct near-whites are
  in play and none is FEFEFE, which separately falsifies the standing "the page background may
  be FEFEFE on purpose" note.
- 0 oracle calls, 0 candidates, no lead promoted, X unsolved, the funded gate unchanged. The red cell
  is 1-in-196 and the grid's colour channel is already swept 12 masks x 5 orders, so this is a
  closed item, not an opening.
- **ZERO human-eye items remain open.** Two items, both filed as needing eyes on solver-made
  images, both fell to a threshold on the white channel. That closes the class the addendum
  called the one acknowledged gap, and it closes it without a human.

---

## 2026-09-29 addendum 7: corpus pointer audit - all 33 resolve, and I reproduced a documented false alarm doing it (`R-POINTERS`)

- Every `~/briefcase/...` pointer in `analysis/*.md` resolves: 33 unique, 0 broken. The one
  apparent exception is the glob prefix `gsmg_era/app_` from row 3444, whose `app_*.js` targets
  both exist. The `halfhalfbetter-tx.txt` dossier I could not find earlier IS present. Only the
  three `LEAD0_CLEAN_*.png` from the Lead 0 note are genuinely absent, already recorded there.
- **This is the first all-clear on corpus integrity in the project.** No live negative rests on
  a file that is not on disk, so the remaining Lead 0 blockage is the absence of a construction
  premise, not the absence of evidence.
- Two roots exist and are NOT the same tree: `~/briefcase` (canonical; `gsmg_issues_all.json`,
  `gsmg-community/`, `gsmg_era/`, `repo_assets/`, `MEMORY.md`) and
  `~/storage/external/briefcase` (solver-side and image material). Searching the wrong one
  yields a confident false negative.
- **My own "17 files missing" claim was entirely wrong and is retracted.** I swept
  `storage/external/briefcase/` because that is where I had been working, and 17 of 20 looked
  absent; all but the 3 `LEAD0_CLEAN` files are present under `~/briefcase`. This is the exact
  trap row 15207 documents, it has now fired on `gsmg_issues_all.json` twice and on these paths
  a third time, and I had the positive control available and skipped it. The fix that works is
  one `expanduser` helper that asserts its own control, not a hand-assembled prefix per check.
- `gsmg-dusttransactions.txt` is a reformatting, not a gap: 24/24 of its distinct OP_RETURN
  strings are already in the ledger at rows 4572/9024, including `Turing Complete.` and
  `The answer is women`, which score 0 on a naive grep only because row 4572 wraps them across a
  line break. Whitespace-normalised search is required before believing any zero count here.
- 0 oracle calls, 0 candidates, no lead promoted, X unsolved, the funded gate unchanged.

---

## 2026-09-29 addendum 8: a second group-chat corpus found, with 15 unmined creator messages (`R-GRPCHAT23`)

- `~/storage/external/briefcase/gsmg-solver-group/jan2023-aug2023.txt` (199,267 B, 759 messages,
  35 participants, 2023-01-01..2023-08-06) is NOT a subset of the creator-only `GSMG_JRK.md`. It
  carries 38 creator messages, **15 of which are not in the corpus `R-SOLVERGRP-NEW` declared
  exhausted**. The gap is in the direction that matters: the hint -> VALIDATION chain needs the
  solver thread, not the hint alone.
- 13 of the 15 are noise. Two survive, both 0 ledger hits on their distinctive phrases:
  - **2023-08-06 07:56, creator, in reply to solvers pressing for detail: "The main risk is to
    fall into the wrong rabbit hole."** `Zil` had just asked for exactly the specification
    ("we should definitely know more than just 'be careful what you get yourselves into'") and
    the creator gave the risk but not the which. Same burst: "I really feel like it's close to
    being solved. I think if I had one good day to actually focus on it I could almost do it."
    This is a METHOD constraint, not a candidate string, which is why the existing sweep missed
    it - rows 9155/9156/9244 swept "rabbit hole" as a cipher candidate, a different claim class.
    Not promoted to a lead: honouring it needs the right hole, which is the crux.
  - **2023-05-02: "Still remarkable that scene. Especially the expiration date of his passport."**
    An authorial pointer at a date in a document, whose antecedent scene is NOT in this corpus
    (the file jumps 04-30 -> 05-02). A genuine artifact gap and a pointer into the already-known
    halving-date family, not a new class.
- Method note carried: the "unmined" screen is a filename/stem test and produces false zeros
  (the `R-POINTERS` dust file scored 0 by name, 24/24 by content), so its 180-file zero set is a
  screening list, not a claim.
- 0 oracle calls, 0 candidates, no lead promoted, X unsolved, the funded gate unchanged. First NEW
  authorial object found this session, and both surviving items are semantics rather than
  ciphers - consistent with `R-SOLVERGRP-NEW`.

---

## 2026-09-29 addendum 9: an unledgered verbatim creator hint, and the community's only argument for it is a hex-digit coincidence (`R-NEOPASSPORT`)

- **The hint, 2021-12-31 17:14, `Jrk Bgrt` (@SoWut), verbatim from `Msgs.txt`: "The only date I
  give away is the expiry date of neo's passport."** `only date I give away` = **0** in
  tested.md, leads.md, STATE_BRIEF.md; `expiry date of neo` = 0. Unprompted and standalone: it
  answers `Lazy Prophet`'s "how old are you? or are you married?" with a date in NEO'S PASSPORT,
  and **no one responds** - the next message is `Zil` six hours later wishing happy new year.
  Negative-space form ("the ONLY date") makes it falsifiable, and a hint the group walked past
  matches the `R-SOLVERGRP-NEW` profile exactly.
- This RECURSES 17 months later in the 2023-05-02 message `R-GRPCHAT23` recorded as a gap.
  `R-GRPCHAT23`'s "antecedent scene missing" framing is CORRECTED: the antecedent is Neo's passport
  in Mr. Robot, and the authoritative 2021 statement sits in the same corpus, in `Msgs.txt`, which
  spans 2017-07-03..2024-12-31 and is the most complete export present. I had compared only
  `jan2023-aug2023.txt` and creator-only `GSMG_JRK.md`, both of which truncate it - so the corpus
  was blind to its own recurrence.
- I also over-weighted the reply-parent metadata: 23 of 62 creator records carry
  `Type: A reply to another user`, and the 2023-05-02 one does not, which is true but only proves
  the antecedent is not a chat message - it is a FILM SCENE, so it was never in the chat. The
  metadata was a red herring for one step; the recurrence claim stands on the 2021 hit.
- **The community's sole supporting argument is FALSE, tested.** The 2024-10-09 note claims
  `01911` is "only thing in the puzzle that has 01911 in it". On the 30,000,943-byte `found.txt`:
  `01911` = 1, and `9/11`, `09/11`, `9-11`, `11-9`, `11/9`, `09-11`, `20010911`,
  `11 September`, `11.9.2001`, `1/9/2001` = **0 each**. The single hit is inside
  `Priv (HEX): 0x484264AB79F501A3CB0803451F19D8B7F0191185D227EAE43C0D34A1D23A99F8`, a
  solver-derived WIF key in a vanity-key dump. In hex, `01911` is four DIGITS, not a date. So the
  uniqueness is real and the reading is void, and the downstream stack (BIP32 `m/44'/0'/0'/9/11`,
  base91, "every 9th and 11th letter", 1EHxfmrG birthday subliminals) is authorless numerology.
  The community does not even agree on the digits: 11/September/2001 vs 11-9-2001 vs 09.11.2001.
- NOT established: the date VALUE (I will not inherit it from the thread) and any USE (a scalar
  salt/index/path component is not an N/D/t premise for `dbbib_91` + `faed_570`). Recorded as a
  new authorial datum, not a lead.
- STANDING RULE, earned twice this session: a negative from my own regex is not evidence of
  absence. Both the `R-POINTERS` 17-missing-files alarm and today's "0 passport mentions" were my
  scripts, not the corpus - the latter because the export puts an `@handle` between name and text
  and my pattern excluded `@` (literal count: 29 `passport`, 4 `expirat`). Any negative search
  result is now reported only after a literal-substring confirmation with a known-present control.

---

## 2026-09-29 addendum 10: correction - the passport is a MATRIX prop, its surface form is `11 Sep/Sep 01`, and my previous attribution was fabricated (`R-NEOPASSPORT-ADDENDUM`)

- **CORRECTION, AND IT WAS A FABRICATION.** `R-NEOPASSPORT` called the antecedent "a Mr. Robot
  reference". Unverified and wrong: Neo's passport is from **The Matrix (1999)**, the Agent Smith
  interrogation at ~18m22s. The cheap check I skipped: `grep -ci "mr. robot" analysis/tested.md`
  returns **2**, and both hits are lines I wrote in that row - so my own error was the sole source
  and no corpus evidence supported it. Mr. Robot is a **separate** creator hint thread ("I hope to
  witness the day that the last scene of mr. Robot becomes a reality"); I conflated two threads
  because both concern a "scene". Recorded, not silently deleted - the error shipped in 5b05f2e and
  the record should show that a fabrication entered it.
- **THE PROP'S SURFACE FORM IS `11 Sep/Sep 01`** (ICAO day-month-month / 2-digit-year, bottom-right
  of a late-1990s passport). Not `09/11/2001`, not `01911`. So the community's `01911` theory was
  wrong on provenance (four hex digits inside a solver's WIF key) AND on notation; the solver who
  wrote "YY-MM-DD format tho" guessed a format the prop does not use.
- **THE 9/11 COINCIDENCE IS NON-LOAD-BEARING.** The prop is internally consistent - issued
  12/Sep/91, expiring 11/Sep/01, the ordinary ten-year passport rule. The ICAO convention produced
  the date; treating it as planted numerology inverts cause and effect. The authorial signal is the
  creator pointing at it, not the arithmetic.
- **SOURCE TYPING, honestly labelled.** I did NOT watch the film and have no primary access. The
  value rests on two INDEPENDENT fact-checks (Snopes; Yahoo/Screen Geek - both rate the claim TRUE,
  both quote the same `11 Sep/Sep 01` string, Yahoo noting the screenshot is unaltered), which
  outranks the excluded solver thread but remains SECONDARY. Ordering used: PRIMARY (not obtained)
  < SECONDARY FACT-CHECK (two, agreeing) < SOLVER THREAD (excluded).
- **THE FIRST MECHANISM-SHAPED OBSERVATION IN THIS THREAD:** a date **printed in words** is a
  different KIND of puzzle object from the digit strings this project has been sweeping. Recorded,
  not acted on: deciding what it indexes into is exactly the rabbit-hole error just documented.
- Unchanged: the hint's status (verbatim, negative-space, zero ledger presence, restated 17 months
  apart, ignored by the group). Only the ATTRIBUTION was wrong. Date now better sourced, USE still
  unestablished, still NOT promoted to a lead.

---

## 2026-09-29 addendum 11: the words-format date battery is 0/51 on both gates, and the periodicity "signal" is noise (`R-DATEBATT`)

- **Part 1, literal: 0, and for a structural reason.** `sep`/`sepsp`/`sepsep`/`september`/`11sep`/
  `sep01`/`sepsep01`/`11sepsp01`/`twoseptember` = 0 in both `dbbib_91` and `faed_570`. The
  alphabet is `a`-`i`, so `s` and `p` are unavailable - I confirmed `s`=0 and `p`=0 in both
  streams. Recording the order honestly: I ran the substring sweep BEFORE the alphabet argument,
  so the sweep alone could not have separated "absent" from "impossible".
- **Part 2, structure: noise, and this is the part worth keeping.** The prop is shaped 2+3+3+2, so
  I scanned same-letter rate at lags 1..30 in both streams. `faed_570`: nothing above threshold.
  `dbbib_91`: lag 6 = 18/85 = 0.212 and lag 7 = 20/84 = 0.238 against a 0.167 baseline - both
  promoted-looking. **Neither survives.** A 200,000-trial multiset-preserving shuffle null puts
  lag-6 at one-sided **p = 0.0715** (14,296/200,000), i.e. NOT significant at alpha=0.05, and
  lag 7 has the LARGER raw value and is pure selection. `sum(p_i^2)` = 14.58 for `dbbib_91`'s
  multiset, predicting ~0.160, which the observed 0.167 baseline already matches - so there is no
  periodic structure to find here at all. A 91-token sample across 30 lags will top its own
  baseline by chance; reporting the raw ratio would have shipped a false positive carrying a
  p-value, which is worse than reporting nothing. This is `R-GRPCHAT23`'s rabbit-hole lesson
  applied to me in reverse: there I documented a hole I could not name, here I nearly entered one
  that merely LOOKED quantitative.
- **Part 3, oracle: 0/51 on the small gate AND 0/51 on the `17ucy1K9...` halving address.** Candidates = the
  prop's printed form and 20 near spellings, 22 numeric forms (`01911`, `110901`, `11092001`,
  `20010911`, `09012001`, `110101`, `9112001`, `091101`, `911`, `101`, `1101`, `11`, `9`, `1`,
  `1109`, `0901`, ...), and 10 semantic forms (`neo`, `passport`, `expired`, `the matrix`,
  `matrix`, `thearchitect`, `architect`, `mr robot`, `mr. robot`, `the only date`).
- **Scope of the negative, stated precisely.** The oracle applies no normalisation, so this tests
  LITERAL strings and rules out the date **AS THE ANSWER** - the only claim the battery was built
  to make. It does NOT rule out the date as a salt, index, stride, key component or intermediate,
  because those feed a transformation whose output would then need oracling, and that
  transformation is precisely the unspecified part. `R-NEOPASSPORT-ADDENDUM` (d) logged the
  words-format shape as the first mechanism-shaped observation in this thread; the right response
  to a shape without a mechanism is a bounded negative plus an explicit list of what remains
  unspecified. I am deliberately NOT expanding into combinations - that is the rabbit hole with a
  51-row table in front of it.
- Unchanged: 0 candidates promoted, no lead, X unsolved, gates funded at 125,635,374 sats (small,
  partially spent) and 375,055,856 sats (dualite, unspent).

---

## 2026-09-29 addendum 12: the rabbit-hole warning resolves - named twice, and it is not the hole we are stuck on; plus an exact complement relation between two grids (`R-RABBIT-HOLE`)

- **I OVERTURNED MY OWN `R-GRPCHAT23` FINDING 1.** It said the 2023-08-06 warning could not be
  honoured without knowing the right hole. That reasoning was backwards: a warning to avoid a
  specific attractor is a POSITIVE constraint if the corpus documents what solvers converged on.
  Screened all 372 creator messages in `Msgs.txt` for direction-giving vocabulary; 25 match, 20 are
  conversational/procedural/key-custody, **5 are substantive and name the hole**.
- **The creator names the hazard TWICE.** (a) 2023-08-06: "The main risk is to fall into the wrong
  rabbit hole." (b) **2024-03-26 10:46: "Yeah, being lost is a common aspect of being on this
  planet I guess, or at least when tempering with rabbit holes."** - an explicit reply to a solver
  who used the word, and `tempering` = **0** in all three docs, so `R-GRPCHAT23` found only the
  first occurrence.
- **The specifying hint is 2020-01-14:** "It might have shown you only one door, beware that the
  rabbit's nest may contain a whole lot more." The clause is a **PLURALITY** claim, and the ledger
  reads exactly ONE nest (`R-GRID14`'s single nest glyph). Already ledgered at `tested.md:13884`,
  so this is not a new transcription - what is new is that the plurality was never tested.
- **Multiplicity is FALSIFIED for the nest reading on the 14x14.** Rebuilt the grid from
  `~/storage/external/briefcase/gsmg-solver-group/gsmgio_bunny_nest.py` SOURCE (not from any
  transcription), then scanned all 169 possible 2x2 windows: exactly ONE all-`r` window, 0-based
  (6,6) = rows 7-8, cols 7-8, 1-based. The nest is 2x2 and unique on this grid, so "a whole lot
  more" is not about more `r` cells here. I am NOT guessing where else it points.
- **INCIDENTAL BUT EXACT:** `~/briefcase/gsmg-community/gsmg_finalgrid.txt` is **14 rows x 14 cols**
  of 0/1 (I earlier mis-read 13 from a truncated preview; corrected by parsing the file), and it is
  the **bitwise complement** of the bunny-nest grid: `o->1`, `w->0`, **167/167 inverted, 0
  exceptions** over cells where the nest has a plain `o`/`w`. Re-derived by re-parsing the `.py`
  source independently rather than reusing my own transcription, so the comparison is not
  self-confirming. The 28 colored (`b`/`y`/`r`) cells do NOT follow the rule: 13 map to `0`, 15 to
  `1`, i.e. not a consistent third value - the color channel is discarded rather than complemented.
  **Significance deliberately OPEN:** an exact complement is also what any image-inversion
  preprocessing yields, so I cannot distinguish "deliberate second reading" from "someone inverted
  the PNG to get a 0/1 matrix". Recording it as measured, not as meaning - the `01911` error was a
  pattern observed and a meaning asserted.
- **LIVE RISK, flagged not reopened:** `R-GRID14`'s single-nest conclusion may be a partial read, and
  per this hint "found the nest" is precisely the rabbit-hole progress the creator warns against.
  Applied to this session's own work: the `R-DATEBATT` 51-candidate battery and the passport chase
  are both rabbit holes in the plain sense; recording them as negatives is the correct handling, but
  neither should be reported as progress.
- 0 oracle calls, 0 candidates, no lead promoted, X unsolved, the funded gate unchanged.

---

## 2026-09-29 addendum 13 (audit): THREE COMMITTED ROWS CORRECTED; NO STATE CHANGE

`R-VOIDROWS`, `R-GRPCHAT23-CORRECTION` and `R-RABBIT-HOLE-CORRECTION` in `tested.md`. This is an
audit of committed claims, not new exploration: 0 oracle calls, 0 candidates, no lead promoted, no
positive claimed, altered or retracted, X unsolved, the funded gate unchanged. It supersedes addenda 8
and 12 and corrects a figure in addendum 2. Four corrections, in descending order of consequence.

**1. THE "COMPLIMENT" IS THE PROJECT'S OWN PHASE-1 BIT FIELD - `R-RABBIT-HOLE` FINDING 4 IS
RETIRED.** The last line of addendum 3 calls `gsmg_finalgrid.txt` an "INCIDENTAL BUT EXACT"
bitwise complement, 167/167, and leaves significance open. Three things settle it, all verified
from source:
  - **168/168, not 167/167.** The substrate is 168 cells and `o`->1 / `w`->0 holds on every one,
    0 exceptions. 167 was a parser that dropped the first cell of row 0; the old row's own
    arithmetic reached 195 of 196 and did not notice the shortfall.
  - **The colours are consistent, not inconsistent.** `b`->1 15/15, `y`->0 9/9, `r`->0 4/4. The
    "13 and 15, not a consistent third value" reading mistook a merged total for a failed rule.
  - **It is a threshold, not a complement, and the polarity is already ours.**
    `data/phase1-matrix-14x14-full.json` documents `_read: ... B/K=1 W/Y=0`, which is exactly this
    mapping. Compared under that rule, `gsmg_finalgrid.txt` equals the certified phase-1 field on
    **195 of 196 cells**; the one difference is 0-based (7,6), inside the 2x2 `r` block, which
    overwrites 1 black + 3 white cells of the base grid. 102 ones vs 101 ones.
  So `gsmg_finalgrid.txt` is a lossy 5-to-2 reduction of a grid we already hold, adds zero
  information, and cannot be the "whole lot more" the 2020-01-14 hint points at. The one open
  visual thread that `R-NEST-SEARCH` left standing is now CLOSED as a negative. The keepable result
  is positional, not semantic: the nest letter matrix and the phase-1 colour map agree on **15/15
  blue and 9/9 yellow cell positions**, an exact cross-render check of the same 14x14 object.
  `R-GRID14`'s single nest glyph is untouched and remains the only verified nest object.

**2. THE CREATOR-MESSAGE COUNTS WERE WRONG AND BOTH PROMOTED FINDINGS ARE A SOLVER'S - `R-GRPCHAT23`
IS CORRECTED.** Its headline "38 creator messages, of which **15 are not in the creator-only
corpus**" does not survive:
  - The real figures: **943 records / 39 participants** (the row said 759 / 35), of which **62 are
    `Jrk Bgrt`** - 23 replies, 39 non-replies, 58 carrying text, all 58 distinct, 4 blank. "38" is
    none of 62 / 58 / 39 / 23 and I could not construct it from any predicate. The cause is
    mechanical: in this export a reply's words live in `- Response:`, not `- Message:`, so reading
    `Message` alone silently discards all 23 replies.
  - **The 15-message gap is 0.** Joining every creator record to `GSMG_JRK.md` on time
    (`GSMG_JRK = jan - 5h` before 2023-03-26, `- 4h` after; the DST switch, fixed on 26
    independently text-matched pairs) gives **62/62 present, 0 missing** - 57 byte-exact, 1
    case/emoji variant, 4 blank-but-present. So the corpus is not a source of unmined creator
    material, which removes the reason that row existed.
  - **"The main risk is to fall into the wrong rabbit hole" is `omaru (@oomaruu)`, a solver**
    (2023-08-06 10:57 UTC), not the creator. The creator's line in that burst is "You know if you
    know." **"I really feel like it's close to being solved..." is `ArchOptic (@Saberto_0th)`, a
    solver** (2023-08-06 12:45 UTC), not the creator - so it cannot be read as a statement about
    puzzle difficulty. Both of the row's two promoted findings lose their author, and the
    "the creator named the hole TWICE" characterisation collapses with them.
  - **The constraint survives on one leg, not two.** `R-RABBIT-HOLE` FINDING 1, the 2024-03-26
    "tempering with rabbit holes" reply, is independent of both and still stands. Treat
    rabbit-hole material as non-progress - that instruction is unchanged and still the right
    default. `R-NEOPASSPORT` and its addendum are UNAFFECTED: the 2023-05-02 passport pointer is
    verified present in `GSMG_JRK.md`, and its 23-of-62 reply split reproduces exactly.
  - **New data-quality note:** `GSMG_JRK.md:431` has a `### 2023-04-07` header glued to the end of
    the previous bullet, so date-attributed parsers misfile the 2023-03-03 `🐰` message into April.

**3. THE 18 VOID-ROW COUNT REPRODUCES, BUT ROW 180 IS A FALSE POSITIVE - AND THE TWO
BOOKKEEPING NUMBERS IN ADDENDUM 2 ARE WRONG.** Re-derived the `R-DBBIBFIELD3` rule by rebuilding
the 34-tool crop-reading set from the pre-fix tree at `fb67667` (STALE 34 / CRITICAL 0 reproduces)
and cutting rows on `#`-level headers. The count is exactly 18: rows 68, 123, 124, 125, 129, 131,
137, 138, 143, 144, 145, 146, 147, 149, 158, 164, 180 plus UNNUMBERED row `## 65`
(`cosmicd_base64idx_sweep`, listed only by tool name - which is why a reader cannot see the 12th
member). The `6 + 12 = 18` and `7 + 4 + 1 = 12` arithmetic is sound and is insensitive to the
header cut. But **row 180 tests the 593-char RENDER, not dbbib** - dbbib appears there only as a
control (duplicating row 149) and as a witness - and it reuses `xor_halfpair_sweep.py`'s math
rather than running the tool, so its 304 candidates are not re-derivable from `dbbib_91` and it is
not a void row at all. **True count: 17 void rows, 11 remaining, 5 cleared** (row 180 is
double-counted as a clear against a claim it never made). The net unresolved count is therefore
unchanged at 11, and **addendum 2's "12 rows remain void-but-unrepaired" is wrong on both sides**
- it disagrees with the row it summarises (`tested.md:17925` says 14) and it predates this audit.
  Also note: `R-DBBIBFIELD`'s "DUAL 12 / OK 44" no longer reproduces (current checker on that same
  commit gives DUAL 10 / OK 46; the checker was corrected twice since), so the "from 44 OK"
  baseline quoted in `R-DBBIBFIELD3` is a dead number.

**4. WITHDRAWN - THE ONE "NEW FINDING" THIS AUDIT APPEARED TO SURFACE WAS WRONG, AND IT IS THE
INVERSE OF THE SETTLED PROVENANCE.** Item 4 of my first draft of this addendum read: row 180's
witness `render[:69] == stored dbbib byte-exact` means two independent OCR artifacts agree on the
same 22-char gap, so those tokens are absent from the image and the real question is why the pixels
do not carry them. **Retracted - both halves were wrong.** The witness is a CONTAINMENT identity,
not corroboration: row 180's own method says the render is the page's continuous field
`dbbib(69) + ab-run + faed(570+z) + z + seg1 + z + seg2`, so `dbbib` is a 69-char PREFIX of the
render by construction and the assertion only checks that two views of the same shallow OCR of the
same page agree on a shared prefix. It is an in-run PASS sanity check and nothing more. And the
direction was inverted: `finalpage-digit-streams.json` `_provenance` records the 91-token stream as
tokens 0-90 of the LIVE PAGE TEXTAREA - byte-identical on the live site (HTTP 200, gsmg.io/89727c...),
in Wayback 2023-06-01 and 2026-04-05, and at community README line 371 - with the 69-token value the
SUPERSEDED shallow-OCR crop kept only for tool back-compat. The 22-char run is therefore PRESENT in
four non-image sources; nothing is missing from the pixels and the question is moot. Structurally,
`dbbib[:45] + 'bfdhbeffcdbbfcccgbfbee' + dbbib[45:]` == `dbbib_91` exactly, so the 91 is the 69 with
the run restored at [44:66]. **Net effect on this audit: nothing. It produces no new lead, and
findings 1-3 stand unaltered.** The lesson is the one the ledger already pays for twice
(`R-BASELINE-SUPERSEDED`, `R-MATRIX69`): a witness that looks like independent corroboration is
often a within-run assertion about two views of one source, and a contradiction between two ledger
sections is resolved by reading `_provenance` and the newest row - never by re-deriving from the
weaker artifact. **Navigability hazard, worth fixing in a future row:** the stale position still
reads as current at `tested.md:3443` and the 2026-09-03 vision-LLM audit at `:3474` (69
authoritative, 91 a "spurious middle run"), which is superseded by the 2026-09-12 correction. The
file contains both positions and the wrong one is not marked at the point of use.

Gates re-run 2026-09-29, all green: `stream_field_audit` selftest 24/24 and `--check` rc=0
(CRITICAL 0 / STALE 18 / DUAL 10 / OK 62); `retraction_audit --check` 0 problems; `p32key_verify`
24/24; `p15null_chitest` 11/11; `oracle` and `oracle_dualite` `--selftest` rc=0; `validate.py`
14 pass / 1 warn (pre-existing French leftovers) / 0 fail; escrow check rc=0 with 1GSMG1JC9 =
125635374 sats partially-spent and 17ucy1K9 = 375055856 sats funded-unspent, both OK. **Crux
unchanged: X is still the decode of dbbib_91/faed_570 under the interpreter alphabet.**

## ADDENDUM 2026-09-29 (d) - `R-PACK5-103INPUT`: the last standing "untried item" is INAPPLICABLE, and one of its own anchors does not reproduce
- **Item run and closed.** The 2026-09-27 addendum closed by pointing at one untried surface: the five 5-bit-packed byte-objects as *inputs* to the 103x103 application. It is not untried-able. `matrix_formula.py:30-37` slices 103 rows out of `bits[:103*103]`, so any input under 1327 B produces short rows and `matrix_col_sums` (`:44-46`) raises `IndexError`. **All six objects (18-356 B = 1.4%-26.8% of the required 10609 bits) are rejected on length**, identically, before any output.
- **The negative does not rest on the crash.** Zero-padding each to 1327 B and re-running gives `all chars in 80..117 (base-38)? False` on all four - 73-99% of each matrix is padding, so the row/col sums fall below the band the tool itself checks. No key pair, nothing reached the oracle.
- **Two witnesses, both established before the negative counts.** Packing: **3 of 3** faed-derived anchors reproduce EXACTLY (`full570` 356 B `8d2f2f83...`, `odd285` 178 B `672d0f92...`, `object256` 160 B `fb347d36...`) under `pack5` = 5-bit index in `DBIFHCEGAKLMNOPQRSTUVWXYZ`, MSB-first, floored to whole bytes, `full570` = interleave(even, odd). Application: the real 1327 B anchor re-found through the same code reproduces the documented `1JG648ya...`/`145ZQ9si...` with the band check True.
- **`dbbib91 -> 56e74a8d...` does not reproduce.** Same code and alphabet give `743703b3586df24d...`; 200 alternative natural mappings (5 orderings x 25 offsets x 2 step directions x 2 bit orders) miss it too. Since the other three anchors confirm the scheme, this object was almost certainly built via one of the `idx0`/`idx1` forms in the original 25 byte-forms. **Annotated in place as UNVERIFIED, not as wrong** - only the 8-hex prefix was recorded.
- **Consequence for the frontier.** The brief's last named mechanical surface is spent, and the 103x103 layer takes **no** input from the `dbbi`/`faed` material - consistent with `R-BRIEFAUDIT` (faed is 356 B of measured-random seed material, not a decode). This is the second standing "untried" item in two sessions to rest on a premise that did not survive contact with the artefact (first: `R-P15NULL`).
- **Not claimed:** no key material newly derived or written (witness cites only the two already-public addresses), no packing promoted to a lead, no existing row deleted, no negative re-opened, no oracle call, no positive.
- Gates re-run 2026-09-29, green: `stream_field_audit --check` rc=0 (CRITICAL 0 / STALE 18 / DUAL 10 / OK 62); `oracle` and `oracle_dualite` `--selftest` rc=0; `validate.py` 14 pass / 1 warn (pre-existing) / 0 fail; escrow rc=0, both gates OK. **Crux unchanged: X is still the decode of dbbib_91/faed_570 under the interpreter alphabet.**

