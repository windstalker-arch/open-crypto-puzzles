# urlblob.bin / urlblob_ct.bin -- provenance

Added 2026-10-05 by row `R-URLBLOB-2026-10-05`. Read-only; never an oracle input
as-shipped (see DEFECT 1).

## What these are

The **fourth** `Salted__` blob in the GSMG chain. The other four known salts are
`3ab585348552415d` (small), `2d3f6fe06dc950e6` (dualite / Cosmic Duality),
`06286612...` + `9fbc451d...` (phase 2), `b45a5e3d` (p32). This one is
`74c974e3f92e64b5 9f7ea22a50dcb0d4` and matches none of them.

Its **only public appearance is a URL slug** on the old gsmg.io site:

    /53616c7465645f5f74c974e3f92e64b59f7ea22a50dcb0d4289d176d4ce9dba7f99a695b8d0797b5c7791e65a8d2b68a5879f5d31ae5e

The route name is the **hex of the blob's own first bytes**. 109 hex chars, an
odd count, so the last nibble is a truncated half-byte. The site never served a
body for it -- the route returns the Vue SPA shell, and the longer CDX variant
has no replayable capture at all.

## Where they came from

    /storage/EA7B-C038/briefcase/gsmg-puzzle/analysis/urlblob.bin
    /storage/EA7B-C038/briefcase/gsmg-puzzle/analysis/urlblob_ct.bin

Both dated 2026-09-06, i.e. the session recorded at `~/briefcase/MEMORY.md:17`.
They were **never copied into this repository**, and they sat outside every root
a device-local `find` reaches -- which is why `tested.md:11941` recorded
"never archived on-device". That claim is wrong. Copied here 2026-10-05;
hashes verified equal on copy:

| file | size | sha256 |
|---|---|---|
| `urlblob.bin`   | 112 B | `25b3619a18174794d4ddd0d743f78f04007c0cf1830f6cf9301bc671631799bb` |
| `urlblob_ct.bin` | 96 B  | `2a2e830ac1bad9b638bccd7d532a79afdc52f52fc9d5542b5a1f950cbbeda207` |

## Structure

    offset  0..7    53 61 6c 74 65 64 5f 5f    "Salted__"
    offset  8..23   74c974e3f92e64b5 9f7ea22a50dcb0d4    salt (16 B)
    offset 24..111  88 B ciphertext

The ledger prints the salt truncated to 8 bytes (`74c974e3f92e64b5`) at
`tested.md:356/7367/11941/14037/19058` and `leads.md:748`. Same blob; the full
16 bytes are recorded here so the two renderings can be compared directly.

## Provenance is INDEPENDENT of the blob

This is what makes the file trustworthy, and it does not depend on the file.
Hex-decoding the public route slug and comparing:

    slug[0:54]  == urlblob.bin[0:54]        -> True
    slug[8:24]  == salt                     -> True
    slug[24:54] == urlblob.bin[24:54]       -> True   (30 ciphertext bytes)

So the route name certifies **54 of 112 bytes** with no reference to any on-disk
artifact: the entire 32-byte header plus 30 of 88 ciphertext bytes. The
**trailing 58 ciphertext bytes rest on this file alone** and have no public
corroboration. Stated so the certified span is not read as the whole blob.

## DEFECT 1 -- `urlblob_ct.bin` is misaligned by 8 bytes

    urlblob_ct.bin == urlblob.bin[16:112]     (NOT [24:120])

| slice | content |
|---|---|
| `ctfile[0:8]`  | `9f7ea22a50dcb0d4` -- the **last 8 bytes of the salt** |
| `ctfile[8:16]` | `289d176d4ce9dba7` -- the **first 8 bytes of the real ciphertext** |

Any sweep handed `urlblob_ct.bin` reads salt `289d176d4ce9dba7...` and so
re-creates **exactly** the bug logged at `~/briefcase/MEMORY.md:17` ("salt
289d176d... garbage"), which invalidated every historical urlblob sweep. The
defect is still on disk under a filename that invites exactly that use.

**Use `urlblob.bin[24:]`, or parse the file's own header. Do not read
`urlblob_ct.bin` as a `Salted__` blob.**

## DEFECT 2 -- 112 B is not a valid AES-CBC blob length

24 B header + 88 B ciphertext, and **88 is not a multiple of 16**. No CBC-valid
length yields 112. Two readings, unresolved:

- **Truncated.** A 96 B ciphertext would make 120 B total. The lost tail would be
  `5caeb77dfc3e0607`.
- **Stream mode.** CFB/OFB/CTR need no padding, so 88 B is legitimate.

`~/briefcase/MEMORY.md:17` describes the blob as "112B ... ct 96B=6 blocks",
which cannot be true: `24 + 96 = 120`, not 112. Recorded as a defect in
that note's arithmetic, not as a defect in the file's mode.

## Verifying

    python3 tools/urlblob_provenance.py            # full report + selftest
    python3 tools/urlblob_provenance.py --selftest

29/29, exit 0. Includes five negative controls (corrupted salt must break the
prefix match; the misaligned ct must fail a `Salted__` parse; the slug must
*not* be allowed to cover the whole blob), so a passing run is known to be
capable of failing. Never calls an oracle or a funded gate.