# GSMG 5-BTC Puzzle - Solve-State Brief (2026-09-24)

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
  -> EVP-MD5 of small blob (salt 3ab585348552415d) -> B1_79.bin (79 B, sha256 1449a217...);
  fields K_C1=9fa9db91..., K_C2, E_C; B2_79 sha256 b40fce72...; **E_S = B2_79[64:79] =
  740a25de4b8e946d0a5ae2667a23a2**.
- dualite blob (salt 2d3f6fe0, 1344 B) vía 7-token XOR key XK -> a795de11... -> 1327 B
  certified plaintext (sha256 4f7a1e4e...); binary-XK MD5 -> cosmic 1327 B.
- Certified VIC vector (community 3.2.2): alphabet `FUBCDORA.LETHINGKYMVPS.JQZXW`,
  escapes (1,4) -> plaintext `INCASEYOUMANAGETOCRACKTHIS...FUNDSTOLIVE`
  (reproduced by `tools/certified_vic.py`, SELFCERT).

Gate premise of the crux: E_S is the 64-bit check on a phrase A produced by decoding the
streams with the author's keyed alphabet -> `sha256(A)[0:15] == 740a25de4b8e946`.

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