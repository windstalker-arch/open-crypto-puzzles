# RAW_PW - research dossier (2026-09-24)

Companion to `STATE_BRIEF.md` and `leads.md`. Everything here is byte-verified against the
2023-06-01 Wayback textarea capture (third independent primary, `leads.md` 1820-1832) unless
flagged.

## The formula

    RAW_PW = matrixsumlist + enter + lastwordsbeforearchichoice + thispassword + matrixsumlist
           = 13 + 5 + 26 + 12 + 13 = 69 chars

## Component provenance (all verified)

| Token | n | Source on the page | Decode |
|---|---|---|---|
| `matrixsumlist` | 13 | a/b run 1, 104 chips at tokens 94-197 | a=0, b=1, 8 bits/byte |
| `enter` | 5 | a/b run 2, 40 chips (splits the printed base64 blob) | a=0, b=1, 8 bits/byte |
| `lastwordsbeforearchichoice` | 26 | `z_segment_1` (63, contains `o`) | a=1..i=9 / o=0 -> base10 -> hex -> ASCII |
| `thispassword` | 12 | `z_segment_2` (29) | same certified hex decode |

The first two tokens decode from binary runs; the last two are what the "TO SET HEX"
instruction language refers to (the phrases ARE the hex-decoded output). All four are
therefore literal, certified strings in the password.

## Crypto chain (certified)

    RAW_PW --EVP-MD5(salt 3ab585348552415d)--> B1_79B.bin (79 B, sha256 1449a217...)
    B1_79 fields: K_C1=9fa9db91..., K_C2, E_C
    WIF(K_C1) --EVP-MD5(salt b45a5e3d827593ca)--> B2_79B.bin (79 B, sha256 b40fce72...)
    B2_79 fields: K_S1, K_S2, E_S; E_S = B2_79[64:79] = 740a25de4b8e946d0a5ae2667a23a2
    (both legs certified with firing controls in tools/rung2_b2.py; the second password
    is DERIVED, not authored - which is why earlier sweeps over authorial strings missed it)

    chain-4 AES key = E_C(15) || E_S(15) || E_B[:2]; all 32 bytes are now on-puzzle.
    E_B[:2] = 59cc is DERIVED, not quoted: an exhaustive 2^16 sweep of the two-byte
    tail against the published chain-4 hash e4269ed5... returns exactly one hit
    (tools/eb_tail_sweep.py, row R-EBTAIL-2026-09-27).

Gate premise: E_S is the 64-bit check on phrase A, where sha256(A)[0:15] == 740a25de4b8e946
and A = decode of the streams under the author's keyed 28-char alphabet (Lead 0 - the sole
unprovided input). RAW_PW decrypts the small blob in-process (oracle control), but no B1_79
reading (19 forms) reaches `1GSMG1JC9...` (tested.md ~9853).

## Structural observations

- RAW_PW length **69 == the image-verified `dbbib_69` token count**; the token lengths
  **13+5+26+12+13 partition dbbib_69 exactly** (chunks: dbbibfbhccbeg / bihab /
  ebeihbeggegebebbgehhebhhfb / aggecbedcibf / bffgigbeeeabe). The 13-char head matches the
  `matrixsumlist`=13 tie to `dbbib_91 = 7x13`.
- `matrixsumlist` = "sum the matrix" is the instruction the two raw digit streams
  (`dbbib`-headed, `faed`-headed) answer; the numeric value it must supply remains the open
  local point.
- Overall 70-char form appears if one misreads `lastwordsbeforearchichoice` as 27; verified
  length is 26.
- `ourfirsthintisyourlastcommand` (29) is the `shabef...` stack's preimage slug family
  (different object from RAW_PW).

## Test status of the RAW_PW family (oracle-certified, both funded gates)

- Literal 5-token RAW_PW and case/space variants: NEGATIVE (earlier rows; token products
  row ~9853: 21 cands x extended oracle x both gates = 0 MATCH).
- Certified grammar with matrixsumlist = faed-38 row-sums / hex / z-big-number forms
  (late-296): N=57 -> 0.
- IFS (Barnsley black-spleenwort) matrix-sum lists (late-297): N=15 -> 0.
- RAW_PW-length 5-chunk partition of dbbib_69 with chunk sum/base-9/hex legs (late-298):
  N=72 -> 0.
- Prior rows: matrixsumlist as literal bit-string / reversed / inverted (row 39);
  matrixsumlist+faed(+rev) and matrixsumlist+dbbib+faed compositions (row 36).

## Open crux

The precise A (literate phrase under the keyed alphabet) whose sha256 prefix is E_S is the
only live input. Unblockers per STATE_BRIEF: alphabet hypothesis -> `tools/lead0_try.sh`,
human visual read (missing `.`, lone `/`, FEFEFE nest (7,4)), or a new author artifact.