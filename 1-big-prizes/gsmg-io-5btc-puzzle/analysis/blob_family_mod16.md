> **SUPERSEDED 2026-10-06 — do not cite the headline.** The 24-byte-header
> premise in this document is wrong: the author's container is `Salted__` (8) +
> salt (8) = a **16-byte** header, which is how this project opens every blob it
> has ever opened. Read the **CORRECTION** at the bottom first; the conclusion
> about the AES-CBC framing is inverted, and the framings (a)/(b)/(c) swept here
> were reading an artifact of the header. (Line numbers in the CORRECTION below
> were measured before this 7-line banner existed: add 7 to read them in the file.)

# The `Salted__` family is not CBC: a structural fact about all five real blobs

Date: 2026-10-05 (corrected 2026-10-06 — see CORRECTION at the end)
Tool: `tools/urlblob_stream_modes.py` (`--selftest` 140/140)
Scope: local file reads and local arithmetic. No oracle call, no funded-gate
contact, no network.

## The observation

Every genuine `Salted__` blob in this project has a ciphertext length that is
**exactly half a block short of a whole number of blocks**.

| blob | salt | file bytes | ciphertext | CT mod 16 | CT / 8 |
|---|---|---|---|---|---|
| `phase_0` | `06286612d43ed7ed58f15b3eae5323c5` | 672 | 648 | **8** | 81 |
| `phase_1` | `9fbc451d13d071f4f12887d4b904befb` | 4112 | 4088 | **8** | 511 |
| `phase32` | `eefc4c5befc1656a1d1833bc8c573462` | 2448 | 2424 | **8** | 303 |
| `cosmic` | `2d3f6fe06dc950e6d359b83e2c868577` | 1344 | 1320 | **8** | 165 |
| `urlblob` | `74c974e3f92e64b59f7ea22a50dcb0d4` | 112 | 88 | **8** | 11 |

OpenSSL's `Salted__` container is `Salted__` (8) + salt (16) = a **24-byte**
header, so `ciphertext = filesize - 24`. Every file size above is a multiple of
16, so every ciphertext lands on 8 mod 16.

Five independent blobs, five different salts, sizes spanning 112 to 4112 bytes,
all landing on the same half-block offset.

**How strong is that, honestly? It depends on the null, and an earlier draft of
this file overstated it.** Two readings:

- If ciphertext lengths are arbitrary integers, residues mod 16 are uniform, and
  five of five at the same residue is about (1/16)^4 = 1 in 65,000.
- If an 8-byte block size is *already assumed*, every length is a multiple of 8,
  so the only two possible residues mod 16 are 0 and 8 with equal probability,
  and five of five at 8 is about (1/2)^4 = 1 in 16 to 1 in 32 depending on
  whether the first blob is conditioned on.

The second null is the one that matters, because the 8-byte-block idea is the
hypothesis being tested. So the residue pattern is **suggestive, not strong**. It
does not carry the argument on its own, and it must not be cited as if it did.

What does carry weight is the exclusion, which needs no statistics at all: a
16-byte block cipher in a padding mode cannot produce these lengths at all,
because the residue is 8 rather than 0. That is arithmetic, not inference.

Equivalently, and more cleanly: all five **file sizes** are exact multiples of
16, and since 24 is 8 mod 16, "ciphertext is 8 mod 16" is just a restatement of
"file size is 0 mod 16". There is one observation here, not two.

## What follows from it

A padded AES-CBC ciphertext is always a whole number of 16-byte blocks. 88, 648,
1320, 2424 and 4088 are not. So a pass that decrypted these blobs as **padded
AES-CBC** was working from a premise the bytes cannot satisfy.

Three framings survive, and they are not equally good:

| reading | ciphertext | 16-aligned | PKCS7 checkable |
|---|---|---|---|
| (a) header is 32 bytes | `d[32:]` | yes | yes |
| (b) file lost its final 8 bytes | `d[24:-8]` | yes | no, pad sits in the missing bytes |
| (c) 8-byte block cipher, 24-byte header | `d[24:]` | no | yes, 8-byte pad |

(c) is what `tools/blob_8byte_cbc.py` sweeps, and it is the reading with a
verifier. (a) and (b) are both 16-aligned and so keep AES alive, which is the
family the 30 tools assumed; neither has been separated yet, and they are not
distinguishable from the file lengths alone. The header is confirmed at offset 0
(magic `Salted__` then 16 distinct salt bytes) in all five, so the 8-byte surplus
is at the **tail**, not a shifted front.

The front-shift case is excluded on evidence rather than preference: a shift
would have moved `Salted__` off offset 0.

That is not a hypothetical. `analysis/tested.md:19722` records the standing
audit: *"Swept every file for AES-CBC / `Salted__` use. 30 tools touch the cipher
or the container; 26 ..."*, with exactly one tool (`tools/phase32_probe.py`)
actually decrypting, and it does so with a hand-picked IV. Thirty tools probing a
cipher mode that the container lengths exclude is the structural explanation for
why this family has never yielded plaintext.

## What is ruled out, and what is not

Ruled out by the above:

- **Padded CBC**, on length alone, for all five blobs.
- **ECB**, by direct test. Zero repeated 16-byte blocks in any blob. That is
  expected for CBC too, but it removes the remaining AES block mode.

Not ruled out:

- **Stream modes** (CFB, CFB8, CFB64, OFB, CTR). These apply no padding, so an
  8 mod 16 ciphertext is unremarkable. `tools/urlblob_stream_modes.py` sweeps
  exactly these.
- **A non-AES cipher**, or AES under a key the project has not reconstructed.

## Entropy

The five blobs are indistinguishable from uniform random, so this is real
encryption and not a partially-decoded or base64-wrapped container:

| blob | chi2/df | distinct 16-byte blocks | repeated blocks |
|---|---|---|---|
| `phase_0` | 1.010 | 40 / 40 | 0 |
| `phase_1` | 1.040 | 255 / 255 | 0 |
| `phase32` | 0.887 | 151 / 151 | 0 |
| `cosmic` | 0.981 | 82 / 82 | 0 |
| `urlblob` | 0.955 | 5 / 5 | 0 |

One blob is *not* uniform: `grid_embedded_chain1_salt3ab58534.bin` (135 B, 111 B
ciphertext, 15 mod 16) scores chi2/df = 2.721, clearly structured. Its name says
"embedded chain", so it is most likely a constructed artifact rather than a
ciphertext. It is excluded from the family argument above for that reason, and it
is also the only blob here whose length is 15 mod 16 rather than 8.

## Correction to `R-URLBLOB-2026-10-05`

That row states the public route certifies 54 of 112 bytes and that the trailing
58 bytes have no public corroboration. **That is wrong, and the error came from
the same too-narrow search that this project has now produced three times.**

A Wayback CDX query on the route prefix returns two captures:

| hex chars | bytes | timestamp | status |
|---|---|---|---|
| 80 | 40 | 2026-02-07 | 200 |
| **224** | **112** | **2026-01-05** | **200** |

The 224-hex-char route hex-decodes to **exactly `urlblob.bin`, all 112 bytes,
byte for byte**. So the whole artifact is certified, not 54 of it, and there is
no uncorroborated tail. The full salt is corroborated too, since bytes 8..24 sit
inside both routes.

Two further corrections:

- **There is no 109-hex-char (54-byte) route in the capture record.** A file named
  with that 109-character string exists under
  `gsmg.io.old-site-2026-09-27/_quarantine_wayback404/`, but its contents are a
  4672-byte Wayback "page not found" HTML page. The string was constructed
  locally, not captured, so it is not independent evidence of any length.
- **No 240-hex-char route exists**, so there is no 120-byte version of this blob
  in the record. The earlier `MEMORY.md` note claiming a 96-byte ciphertext in 6
  blocks would require a 120-byte blob, and that route does not exist. On this
  evidence the blob is complete at 112 bytes, its 88-byte ciphertext is the
  author's, and the half-block offset is a property of the family's construction
  rather than a truncation on our side.

## Status

Structural finding, certified by arithmetic on the bytes plus a self-test on the
sweep harness. **The passphrase sweeps are a separate matter and none has found a
decryption.** `tools/blob_8byte_cbc.py` now sweeps all three framings -- (a) a
32-byte header with PKCS7 gating, (b) a 24-byte header minus a lost 8-byte tail
with no pad gate, (c) a 24-byte header with 8-byte-block CBC (DES/3DES/Blowfish/
CAST5) -- and `--selftest` is 80/80, meaning every (kdf, algorithm, key length)
cell re-finds its own synthetic ciphertext, so a clean sweep is a real absence
rather than a broken verifier. Framing (a) has cleared four of five blobs with
no survivor; framing (c) is still running. A survivor of the printability screen
is a lead for human reading, never a solve.

The one thing this document does establish without any further assumption: for
all five blobs, the AES-CBC framing used across 30 tools is the wrong framing.
---

# CORRECTION 2026-10-06 — the header is 16 bytes, and the finding inverts

**The premise of this document is false, and the ledger's own certified rows say
so.** Line 28 asserts `Salted__` (8) + salt (16) = a 24-byte header. This
project's blobs are opened with an **8-byte** salt and a **16-byte** header --
`openssl enc` has never written a 16-byte salt -- and `analysis/tested.md:14391`
already lists the consequences in plaintext:

| salt (8 B) | file | ct = file − 16 | blocks | state |
|---|---|---|---|---|
| `2d3f6fe06dc950e6` | 1344 | 1328 | 83 | **OPENED** (1327 B) |
| `06286612d43ed7ed` | 672 | 656 | 41 | **OPENED** (648 B) |
| `3ab585348552415d` | 96 | 80 | 5 | **OPENED** |
| `b45a5e3d827593ca` | 96 | 80 | 5 | **OPENED** |
| `9fbc451d13d071f4` | 4112 | 4096 | 256 | **OPENED** (4090 B) |
| `eefc4c5befc1656a` | 2448 | 2432 | 152 | BLOCKED |
| `74c974e3f92e64b5` (`urlblob`) | 112 | 96 | 6 | unopened |

Three running tools assert the same 16-byte header and are the ones a negative in
this folder is judged against: `tools/oracle.py:134`
(`salt, ciphertext = raw[8:16], raw[16:]`, with `:48` spelling out "Salted__ +
8-byte salt + 80 bytes of ciphertext" and `:327` pinning the gate blob to
`len(raw) == 96 and raw[8:16].hex() == "3ab585348552415d"`),
`tools/ladder_census.py:160` (`salt, ct = d[8:16], d[16:]`, with `:138`
asserting `len(d) - 16 == 80`), and `tools/p32_evp_verify.py:80`
(`salt, ct = blob[8:16], blob[16:]`), whose run re-derives phase 3's 4090-byte
plaintext as `sha256 c4ad94559a44a927…` and reports **MATCH True** against the
fork's `phase3.txt`. None of the three could have produced that match on a
24-byte header. The claim was never unverified -- it was simply not read back
into this document.

**Six of seven are 16-aligned under a 16-byte header, and five of them are
already open.** The "half a block short of a whole number of blocks" pattern in
the table above is what you get by subtracting 24 from sizes the author padded
to 16. It is an artifact of the header assumption, not a property of the family.

## The discriminating test, not an argument about residues

`phase_0.bin` opened with its certified password `sha256("causality").hexdigest()`
under `EVP_BytesToKey SHA-256`, run through `tools/blob_8byte_cbc.c` today:

| framing | salt | ct | survivors |
|---|---|---|---|
| (a) 32-byte header | 16 B | 640 | **0** |
| (b) 24-byte header, tail dropped | 16 B | 640 | **0** |
| (c) 24-byte header, 8-byte blocks | 16 B | 648 | **0** |
| **(d) 16-byte header** | **8 B** | **656** | **1** |

The (d) survivor decrypts to 656 B, PKCS7-cleans to **648 B**, and its SHA-256 is
`e2f9dd65604a3231f8b3301724e8d713a88fffc4b6c7c4aeeb20f58a582b593a` -- the hash
recorded in `tested.md:14391` and `:15172` **before today**, from a different
code path. That is a known-good input re-found through the same code a negative
would be reported through, plus three negative controls on the competing
framings. The same run on `phase_0` under (d) prints `alg=AES-256-CBC klen=32`.

So the question is not how surprising five matching residues are. A password the
project recovered independently opens exactly one of the four framings, and it is
the one this document did not consider.

## What this inverts

- Line 50: *"a 16-byte block cipher in a padding mode cannot produce these
  lengths at all"* -- it produces exactly these lengths, under a 16-byte header.
- Line 61: *"a pass that decrypted these blobs as padded AES-CBC was working from
  a premise the bytes cannot satisfy"* -- `tools/oracle.py`, `tools/ladder_census.py`,
  `tools/p32_evp_verify.py` and `tools/urlblob_stream_modes.py`'s own IV
  semantics all did that, and they opened five of six blobs.
- Line 168 (end of the original file): *"the AES-CBC framing used across 30 tools is the wrong framing"* --
  **backwards.** Padded AES-CBC with a 16-byte header is the right framing; the
  24-byte-header readings (a)/(b)/(c) were sweeping an artifact. The 217,170,200
  cells already spent on them are a measurement of the wrong object.
- Lines 63-79: the three surviving framings are the wrong three. The correct one
  is `(d): salt = d[8:16], ct = d[16:]`, and it was never swept before
  2026-10-06.

What the document got right: the entropy table (line 108) still holds -- those
are real ciphertexts. The ECB exclusion (line 93) still holds. The self-correction
at lines 35-47, which walked back the statistical overstatement, was the right
instinct applied to the wrong null; the arithmetic at lines 46-48 ("file size is
0 mod 16" is the same observation restated) was correct and is in fact the clue
at line 55 that was missed: **file size ≡ 0 (mod 16) is what a 16-byte header plus padded
CBC requires.**

## Consequent corrections to `R-URLBLOB-2026-10-05`

- **F3** (*"the salt is 16 bytes, `74c974e3f92e64b59f7ea22a50dcb0d4`"*) -- the
  salt is 8 bytes, `74c974e3f92e64b5`; bytes 16..24 of the file are the first
  block of ciphertext. The 16-byte rendering is the same artifact.
- **F5** (*"112 B is not a valid AES-CBC blob length … no CBC-valid length equal
  to 112"*) -- refuted: 112 = 16 + 96 and 96 = 6 AES blocks. The "truncated"
  reading (which needed a 120-byte file and a lost tail `5caeb77dfc3e0607`) and
  the "stream mode" escape were both consequences of subtracting 24. The blob is
  complete and is padded-CBC-shaped.
- **F4** (*"`urlblob_ct.bin` is misaligned by 8 bytes"*) -- the *operational*
  warning stands: never read it as a `Salted__` blob. But `urlblob_ct.bin` is
  byte-identical to `urlblob.bin[16:]` (verified, 96 B), which under the correct
  header is **the ciphertext itself**, correctly aligned. Its `[0:8]` is not "the
  salt tail"; it is the first ciphertext block.

## Status after the correction

Framing (d) is now the swept framing, on the one unopened blob:

| battery | cells | result |
|---|---|---|
| (d) AES-CBC, 5 KDFs × 3 key lengths, 1,670,540 candidates | 25,058,100 | 0 survivors (95 s) |
| (d) 8-byte-block CBC (`--bs 8`: DES/3DES/BF/CAST5 = 7 key lengths), 5 KDFs, evp KDFs take 2 IV readings at ivlen 8 and raw KDFs 1 | 93,550,240 | 0 survivors (5,731 s; D = 16,325 cells/s wall) |
| (d) stream modes (CTR/CFB/CFB8/CFB64/OFB), 3 EVP KDFs × 2 key lengths | 50,116,200 | see `analysis/tmp/wl/logs/d_stream_urlblob.log` |

Candidate set: `analysis/tmp/wl/gsmg_formed_raw+sha256hex.txt`, 1,670,540 unique
-- every one of the 835,270 vocabulary entries in both the literal form and its
`sha256(X)` hex form, because this project has certified both forms as author
conventions (literal for phase 3.2, hex for phases 1-3 and the gate).

A survivor of the printability screen is a lead for human reading, never a solve.

# CORRECTION 2026-10-06 (b) — the stream row's "five modes" were four distinct ciphers

See `R-STREAMMODEDUP-2026-10-06` in `analysis/tested.md`. The table row above
`(d) stream modes (CTR/CFB/CFB8/CFB64/OFB) ... 50,116,200 ... see
analysis/tmp/wl/logs/d_stream_urlblob.log` is corrected, appended not edited:

| battery | cells | result |
|---|---|---|
| (d) stream modes, **after fix** (`CFB`=full 128-bit), 3 EVP KDFs × 2 key lengths | 50,116,200 | 17 heuristic survivors, 0 authentic plaintext (uncertified). Logs: `d_stream_{md5,sha1,sha256}.log` |

- The named `d_stream_urlblob.log` is an empty dead run (`R-STREAMSWEEPDONE`'s liveness gap); the real
  shard logs are `d_stream_{md5,sha1,sha256}.log`.
- `CFB` was `AES.new(key, AES.MODE_CFB, iv=iv)` with no `segment_size`, and PyCryptodome defaults it to
  **8** — byte-for-byte the `CFB8` cell. Full-block CFB was swept **zero** times. Fixed: `CFB` →
  `segment_size=128`. `--selftest` is now **143/143** (was 140/140), the extra check a
  mode-distinctness witness that fails under the old default.
- The 16-byte printability screen (`d[0:16]`, floor 0.95) is mode-blind for CTR / full-CFB / OFB: all
  three share the first-block keystream `E(iv)`, so one screened candidate yields three survivor lines.
  Dedupe survivors by (passphrase, first block); a survivor count is not a count of independent events.
- Result unchanged: all survivors r in [0.45,0.54], none a solve. `X` UNSOLVED; crux unchanged.
