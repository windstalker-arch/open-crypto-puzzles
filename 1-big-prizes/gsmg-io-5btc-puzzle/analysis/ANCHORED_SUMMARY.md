# GSMG 5-BTC Puzzle  -  Research Anchored Summary

## Current State (updated 2026-09-11)

### What We Have

1. **Gate targets verified** (on-disk, base58check):
   - `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe` -> h160 `a9553269572a317e39f0f518cb87c1a0ee1dbae4`
   - `17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa` -> h160 `4bc468447fe1b048ad030a2f9a125478eabc4ed6`
   - Target pubkey X = `f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464`
   - X with odd-Y compressed -> h160 matches T1 (1GSMG). **Real on-chain anchor.**

2. **Oracle premise falsified** (late-29):
   - Small blob (96B, salt `3ab585348552415d`) decrypts under **raw text password** `matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist` -> 79B, SHA256 `1449a217...`, head = K_C1 (WIF `5K2byJMssxFKuTgnk9YQjpBz5FhkwwF2LaZoAyTus8HjGEpz8AT`)
   - Dualite blob (1344B, salt `2d3f6fe06dc950e6`) decrypts under **raw 32-byte XOR key** `a795de11...5535` + EVP-MD5 -> 1327B, SHA256 `4f7a1e4e...` byte-identical to `~/gsmg/cosmic_plain.bin`
   - The oracle's `sha256(X).hexdigest()` transform **fails PKCS7 padding**  -  all prior oracle line candidates are UNCERTIFIED. Effective certified candidate count = 0.

3. **Yourlife string reconstructed** (late-30):
   - 1539-char stripped lowercase text from Beaufort-decoded directive lines (README gh_readme.md lines 302-320)
   - Head: `yourlifeisthesumofaremainderofanunbalanc`, tail: `rthelessireallyhopeyouretheoneciaobellao`

4. **Ca segment reconstructed** (late-30):
   - `c4[246:278] XOR 38d7c0b10bda...bd25 = "ntheendpleasejusthelpusbuilditin" = yl[633:665]` (32/32 bytes, exact match)
   - True alignment: **off=633** (briefing said 634; off-by-one)
   - `ca[0:905] = c4[246:1151] XOR yl[633:1538]`
   - `ca[:32] == 38d7c0b1...bd25` (the published "keystream" IS `ca[0:32]`)
   - ca SHA256 = `5940983cfa61...` — **RESOLVED 2026-09-27 (`R-CAFULL-2026-09-27`): this row reproduces bit-exactly, and the old parenthetical ("that was for full file, not 905B segment") is RETIRED as an unfalsified assumption.** The alignment `c4[i] <-> yl[i+387]` extrapolates to `ca_full = c4[0:1151] XOR yl[387:1538]` (1151 B, never swept: `R-CA-WINDOWXOR` capped `L` at 905) -> `2b2493c1...`, and the 246 B head -> `1d0eb750...`. Neither hits `cd3fea3d` or `c3b87356`, and the head carries no `+-` marker. `cd3fea3d` is unreachable at ANY length of this alignment and is fabrication-class (#88 anonymous quote, #92 "APPEARS to be"). Scoping: `ca[0:32]` is verified (two independent community artifacts XOR to the English phrase); `ca[32:905]` is propagated, unverified — neither region has ASCII words >=5 chars, and printable fraction (0.378 vs 0.382) does NOT discriminate. **The 10.7M-candidate sweep was aimed at a false anchor; `ca` is closed, not merely unswept.**

5. **k_new from reconstructed ca** (late-30):
   - `k_new = cc[833:865] XOR ca[280:312] = 158cb6a02a13f27e...`
   - h160 LCP vs T1/T2 = **0** (does NOT reproduce andersonbig's claimed LCP=5)

6. **c4 file verified** (on-disk):
   - `chain4_decrypted_1151.bin` SHA256 = `e4269ed5...` [OK] (community anchor)
   - `c4[246:1151]` SHA256 = `9f06936a...` [OK] (WabiLipa anchor)
   - `chain1_79.bin` SHA256 = `1449a217...` [OK] (oracle anchor)

### What Changed This Session

1. **Rebuilt yl** from 19 Beaufort-decoded directive lines, strip_non normalization -> exactly 1539 chars
2. **Verified keystream**: c4 XOR yl[633:665] = 32-byte ASCII "ntheendpleasejusthelpusbuilditin"  -  offset corrected to 633
3. **Reconstructed ca[0:905]**: head = published keystream; ca[280:312] computed; k_new derived -> LCP=0 (miss)
4. **CRITICAL NEW FINDING  -  maintainer refutes entire chain4/mirage framework:**
   - **Naddiseo** (repo owner, insider-aligned with creator JRK) in GitHub issues #55 and #104 (Aug 2026):
     - Calls the 1327-byte plaintext "nonsense" built on jackdevs66's repos
     - Says "there is no credible evidence of a step after Cosmic Duality"
     - Key quote: **"once we got to salph the internet is no longer required"**  -  puzzle solvable with on-puzzle data only; no external unpublished files like `cosmic_A.bin` should be needed
     - States the `gsmg.io/4f7a1e4e...` URL "was never a url related to the puzzle"
   - Origin of 1327B chain = jackdevs66's `GSMG5_CDuality` repo (2025-08), refuted by Naddiseo's entropy/structure/padding arguments
   - Community (andersonbig, WabiLipa, Anvexis, valleytainment, marcofortina) all blocked on same ca/cosmic_A/row1-4 items
   - Implication: the entire chain1->chain4->cosmic_A->k_new pipeline may be a community-constructed mirage

### What Changed Most Recent Session (2026-09-13)

1. **Confirmed oracle blob is embedded ON-PAGE**: page text = `shabef` + "your first hint is your last command" + L(64 b64) + binary "enter"(40) + R[:64]+`shabefanstoo`. `L+R[:-12]` == `oracle.py BLOB_B64` exactly. The oracle's target blob lives in the SalPhaseIon text itself.
2. **Verified interpreter mechanism on z_segments**: `a=1..i=9, o=0` -> base10 -> hex -> ASCII gives `lastwordsbeforearchichoice` / `thispassword`. This is the ONLY certified decoder; it needs an `o`->0 symbol.
3. **CLOSED the interpreter-permutation route on dbbib/faed**: swept all P(10,9)=3,628,800 injective a..i->digit maps × 8 orientations (dbbib/faed + reverses + joins), decoding each via the verified base10->hex->ASCII interpreter in C (gmpy cross-checked). Zero ≥80%/≥90% printable outputs. Byte-ceiling kills it structurally: 91 tokens always -> 37-38 bytes; 570 tokens always -> 236 bytes. The interpreter only works for the `o`-carrying z_segments, i.e. seg1/seg2 passwords; dbbib/faed are the VIC ciphertexts, not interpreter streams.

### What Changed 2026-09-14 session

1. **Both 79B blobs now on disk**: added `data/B2_79B.bin` (chain-2, salt `b45a5e3d827593ca`,
   pw=WIF(K_C1), EVP-MD5) -> 79B = K_S1 `b06fa6f2...` || K_S2 `b11d211c...` || E_S `740a25de...`,
   SHA256 `b40fce72...` (was already verified in late-59 / MEMORY.md). Corrects any lingering
   "C2 not archived" note: the chain is complete, both inner blobs local.

2. **Two-blob mirror battery certified negative** (`tools/mirror79_research.py`, all exact-pubkey
   k*G==X checks + gate-address checks): 2×2 matrixsumlist over {K_C1,K_C2,K_S1,K_S2} (sum/xor/diff
   mod n, mod-256, row/col/diag/total), point-addition subset sums (± four known pubkeys),
   B1||B2/B2||B1 concat readings, E_C<->E_S tail interplay incl. chain4-pw-32B-as-scalar, and
   1150 cyclic-extension matrixsumlist scalars -> ALL no match. 2244 hex/digest forms already in
   bloom (0 unseen). Positive control re-finds K_C1 addr `14zJ3RHPxiRJAmYHUNTvPoCTxhFB6gACgf`
    through the same path.

3. **clearmatics/zion and bavlayan/...-OpenSSL---RSA repo checks**: both ruled out as sources /
   leads (research notes at end of `analysis/tested.md`).

### What Changed 2026-09-14 (latest session: gsmg.io page + Gematria route)

1. **`gsmg.io/theseedisplanted` live page inspected**: title "GSMG Puzzle", HTML comment
   "Nice to see you around! Good luck little bunny hunter ;)". Body = 8 jigsaw-strip PNGs
   (blue/black pieces have white strip on RIGHT, red pieces on LEFT; all ~78x70, FLAT edges,
   no physical teeth  -  order not derivable from connectors) plus a hidden
   `<form method=post action=/phase1verification><input type=password name=password>`. **No JS
   anywhere on the page.**
2. **`/phase1verification` is a DUMMY**: it returns `Hello :-)` HTTP 404 byte-identically for
   every input (any password, empty, query-param, referer/cookie variants). It is a decoy, not
   a real gate. `robots.txt` = ASCII-art rocket (rhymes with the "launch" theme), no real
   directives. No other endpoints found (phase2/3, sitemap, security.txt, manifest all 404).
3. **Full assembled piece text is EXACTLY: `white rabbit nostalgic alice childhood`**
   (confirmed explicitly by human). OCR of the small PNGs remains unreadable; the text is
   known from the human, not from pixel extraction.
4. **Gematria route closed (certified negative)**: simple-English Gematria of the full phrase
   = 325 (Jewish = 1630; per-word mod-10 digits = 52008 / 08052). Tested the raw phrase, all
   no-space variants, reorderings, and the numeric values 325 / 1630 / 52008 / 08052 and each
   per-word value (white 65, rabbit 52, nostalgic 100, alice 30, childhood 78) through
   `oracle.py` AND `oracle_dualite.py`  -  all NO MATCH. Also negative: `nostalgic`,
   `childhood`, `alice`, `white rabbit`, `mr rabbit`, `queen of hearts`, `king and queen`,
   `mad hatter`, `mirror mirror on the wall`, `key`, `drink me`, `eat me` individually
   through oracle.py  -  all NO MATCH. These are ASCII passwords; the oracle blob equal-password
   test remains void (padding-fail), so label = uncertified negatives unless run via stdin
   (they were; still NO MATCH).
5. **Page fragments do NOT spell the Alice phrase from filenames**: file fragments
   (banking/war/ca/dig/i/lock/lo/crypto/gic/n/you/open/ing/t) contain 48 letters with NO
   S/H/E-duplicates needed for "white rabbit nostalgic alice childhood"; the filenames are
   decoys. Real text is a separate rendered message on the pieces (per human).
6. "weiss wise man" -> human clarified the intended cipher is **Gematria** (also explored
   "wizard"). Not VIC/Bifid/Vigenere.

### Open Questions (if continuing)

0. **How is "white rabbit nostalgic alice childhood" used, if not the oracle line / Gematria
   number?** The page's dummy form and the lack of any other endpoint leave the phase-1 use of
   this phrase unproven. Possibly: (a) it is filler color text on the jigsaw, (b) it keys a
   transposition/cipher on the 91/570 digit streams, (c) the human is exploring a route that
   is off the certified chain and it will not converge.

1. **Is the 1327B chain actually the puzzle's intended path?** Naddiseo says no; community says yes. Without creator confirmation, unresolvable from code alone.
2. **What does "once we got to salph the internet is no longer required" mean operationally?** Does it mean: (a) cosmic_A.bin was never needed (chain4->XOR triangle is wrong), (b) there exists a local-only derivation using chain1/chain2/chain3 structures, or (c) something else entirely?
3. **Where is the "second door" / yinyang path?** (admin hint, unexplored)
4. **Can the hidden blob in cc[158:] (salt `5bbd88ac32481bca`, CT 1152B) be cracked?** (150+ passwords tried)
5. **K_I1/K_I2**  -  referenced in issue #87 but never defined; part of the XOR triangle?

### Ledger

`analysis/tested.md` current tail: late-59, late-60, 2026-09-14 research notes (clearmatics/zion,
bavlayan), late-65 (two-blob mirror battery negative, B2 on disk), late-66 (2026-09-14, NEW:
ca/cosmic_A "LCP" claims tested as REAL Base58Check addresses  -  statistical noise, certified
negative). Oracle line still void; effective certified candidates = 0.

### What Changed 2026-09-14 (later session: ca/LCP verified in real base58)

- chain4 independently re-derived and WRITTEN to disk as chain4_good.bin: cc[158:1326] XOR
  mask b657264f2f6e6921 (repeat, off 0) -> `Salted__` + salt 5bbd88ac32481bca + 1152B CT; EVP-MD5
  pw = 38d4f4c90cb45fdfc8cff50d0ed1c57 40a25de4b8e946d0a5ae2667a23a259cc -> 1151B,
  sha256 e4269ed5fbb202a81e5e1aa6b5190fdd1ea126b2c8547ea7cdbdf45387ea135b (matches #68/#88
  anchor); tail chain4[246:1151] sha256 9f06936a... matches WabiLipa anchor.
- Full Base58Check P2PKH verification harness built (coincurve; witness: the known-uncompressed
  target 04f4d1bb...55a464 re-encodes to exactly 1GSMG1JC9...prBe). Every published "LCP" claim
  re-checked as a real address against BOTH escrow gates:
  - k_new = cc[833:865] XOR ca[280:312] for ca = cc / chain4 / cosmic_duality (and the exact
    table-offset alignments {-4,12,27,2} × bases {0,158,246}): max address-LCP observed = 1-2,
    no partial ≥4.
  - valleytainment "Door-2 LCP7 = ascii_hex(M3DGNJTGMZTCMZTG) ⊕ Half ⊕ Better" (all swap orders,
    comp+uncomp): max address-LCP = 1.
  - NO candidate produced any real base58 gate address or LCP≥3.
- NOISE BINDING: 65,536 uniform random XOR-window scalars give LCP≥4 vs Gate1/Gate2/target-X at
  exactly the null rate (≈N/65536; observed 1,1,2 ≈ expected 1.0). Conclusion: andersonbig's
  "4 pairs LCP=4 (deterministic, table-derived)" and "best LCP=5 (statistical)" are the upper
  tail of a ~millions-window sweep  -  statistical, not structural. libbase58 repo (archived Apr
  2025) is canonical-alphabet only, no puzzle content.

### What Changed 2026-09-20 (audit + certified-oracle reconciliation; see analysis/AUDIT-2026-09-20.md)

1. **Certified-boundary reconciliation (important correction to older notes):** the old
   statement "effective certified candidates = 0" referred only to legacy candidates fed
   through the `sha256(X)` SHA-256 leg that fail padding. The current oracle tools run BOTH
   legs (phase-2/3 sha256-leg, Cosmic-Duality raw X + EVP-MD5) and are selftest-certified
   against blobs with known passwords ("causality"; raw+MD5 -> B1_79). Therefore every
   pos-ra-rebuild battery (lead-0 sweeps, mirror, island GCM, mod-n/scalar/2-of-3, ASL x2,
   braille, chardet, script-keyword, BaseN, whole-stream, Beaufort x2) is genuinely
   certified-negative against BOTH funded gates. Ledger now spans 241 rows (late-208..226
   added 2026-09-19/20), committed at 7a0cf2a.
2. **Island re-certified offline (late-223):** puzzlepiece.mp3 (212,031 B) found locally
   at ~/briefcase/gsmg-private/; sha256 ef17a96d...; CIDv0 recomputes to the exact
   published Qm...GiDK; island = 212 B @ #8064-8276, entropy 6.368, base64-ratio 0.193;
   ID3v2 tag ends 4096; first MPEG-1 Layer III sync 0xfffb at 8276; no recognized framing.
3. **Lead-0 visual checklist completed (late-226):** live https://www.gsmg.io/ is now a
   JS SPA shell (no content); the archived data/live_salphaseion.html is authoritative and
   re-verified byte-exact. Faithful monospace render + pixel scan: all ink lies on the
   token text lattice (rows 0..918 of 991, cols 20..970) - zero non-text glyphs, blank
   margins/bottom. Page symbol census b167 a138 g127 e99 i91 h78 f77 c72 d71 o17 z4; the
   on-page "." is the certified 28-char alphabet's keying artifact, not a PDF symbol.
4. **Escrow re-verified live (2026-09-20, mempool.space):** small gate 125,635,374 sat
   (1.25635374 BTC, 120 UTXO); dualite gate 375,055,856 sat (3.75055856 BTC, 45 UTXO).
   Both targets intact; each shows a fresh ~block-964501 dust credit (864 / 546+555 sat).
5. **Remaining input is external:** lead 0's interpreter alphabet is closed on every
   mechanical family (9!, keyed-28, Bifid periods 91/13/7/1, Beaufort x2, base-N charsets,
   whole-stream pipelines, ASL/braille/codepages, transposes/matrix/scalar/mod-n/2-of-3).
   Progress now depends on a new clue/repo/steer or creator-side confirmation of the
   Naddiseo "once we got to salph the internet is no longer required" guidance (issues
   #55/#104).

### Ledger (2026-09-20)

`analysis/tested.md` tail: late-208..226 (2026-09-19/20) - all closed, committed at 7a0cf2a;
steers processed: laplaces42 ASL, Aitzaz-Saleem braille, chardet, IBM OpenCryptographyKitC
(inert), BaseX gist (inert family), alphabet_detector, compact_enc_det (inert), ~/Mixer
(inert), mathyourlife gist (inert). pycipher installed (wheel) + Beaufort x2 cross-check.
