# The `Salted__` family is not CBC: a structural fact about all five real blobs

Date: 2026-10-05
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