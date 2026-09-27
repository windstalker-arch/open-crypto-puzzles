# GSMG artifact families — where each family actually lives

Written 2026-09-27, after a session in which I analysed `phase3.2.hex` as a novel
ciphertext. It was a hex re-encoding of `phase3.assets/phase3.2.txt`, which lives
in a **sibling repo** I had never searched. The same mistake class had already been
written down the day before, in `R-P32BLOB-2026-09-26`, along with the rule I then
failed to apply: *"Filename coverage is a worthless proxy; always content-grep
before spending a session."*

This file exists so that locating an artifact is a lookup, not a recollection.
**It is a map, not an authority** — when it disagrees with
`tools/sibling_index.py --name <artifact>`, the index is right and this file is a
stale copy that needs fixing. That is the intended relationship.

## The trap that caused the incident

`1-big-prizes/` contains two directories whose names differ only in hyphens:

| Path | Files | What it is |
|---|---|---|
| `gsmg-io-5btc-puzzle` | 284 | the working research repo (this one) |
| `gsmgio-5btc-puzzle` | 28 | a **fork-audit bundle**, not a copy |

Reconstructing a path from memory can silently consult the wrong tree and find
nothing — or find something that merely looks right. Both are silent failures.
`tools/sibling_index.py` removes the need to guess: it hashes every tree and a
twin is found by content, wherever it lives.

## Families

Paths are abbreviated: `~` = `/data/data/com.termux/files/home`,
`~SD` = `/storage/EA7B-C038` (external card), `~PFX` = `/data/data/com.termux/files`.
The external card matters: the solver group lives there, so the same file can be
reachable by two unrelated paths.

| # | Family | Canonical location | Provenance rule |
|---|---|---|---|
| 1 | **Certified ladder** — BLOB1/BLOB2, `B1_79`, `B2_79`, RAW_PW | `~/gsmg/`, mirrored `~/briefcase/gsmg-private/`, `~SD/briefcase/` | re-derive with `tools/verify_ladder.py`; never trust a copied value |
| 2 | **Phase assets** — `phase2-assets/`, `phase3-assets/` | `~/open-crypto-puzzles/1-big-prizes/**gsmg-community-hints-repo**/` + `~PFX/usr/tmp/opencode/quarantine/naddiseo/…` | **community-attested.** `R-FUBCD`: 0 author witnesses in 399 files. Always label as community |
| 3 | **Old-site archive** | `~/gsmg/gsmg-web-archive/` (`SHA256SUMS.txt`, `FETCH-LOG.md`) | **certified exhausted.** Do not re-fetch or reopen |
| 4 | **Live capture** | `~/gsmg/gsmg-io/gsmg.io.live-2026-09-27/` | author material; the only author-side tree |
| 5 | **Cosmic Duality** | `~/gsmg/cosmic_decrypted.bin`, `~/briefcase/gsmg-private/`, `~SD/briefcase/` | sha prefix `4f7a1e4e`; **reproducible, NOT authenticated** (valid PKCS#7 occurs ~1/256 by chance) |
| 6 | **Fork audit** — 5 GitHub forks, creator-clue ledgers, Telegram sender attribution | `~/open-crypto-puzzles/1-big-prizes/gsmgio-5btc-puzzle/usr/tmp/opencode/{fork-audit,halbgott}/` | third-party **solver** analysis. `usr/tmp/opencode/` is a packaging artifact, not a real path. **Under-inventoried**: `GSMG_CREATOR_AUTHORED_CLUE_LEDGER.md` and `hintgivers_names.txt` have 0 ledger coverage |
| 7 | **Community hints** | `~/briefcase/gsmg-community/` (`hints-consolidated/`, `phase3.png`) | community; provenance-label every claim |
| 8 | **Solver group** | `~SD/briefcase/gsmg-solver-group/` (109 files) | third-party. Re-packages families 1–5 **verbatim** — see below |
| 9 | **Private / author-wallet** | `~/briefcase/gsmg-private/` | **ours, not the author's.** `author-wallet.txt` says "Generated 2026-09-22"; a match inside it is circular |
| 10 | **Research ledger** (this repo) | `~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle/` | `analysis/tested.md` is the authoritative record |

## Rule the solver group taught us

The solver group is **not** a source of independent data. It re-packages
community and private artifacts under new names and encodings:

- `p3.b64.txt` ≡ `phase2-assets/phase2_aes.txt` (both sha `5e583d5b…a94d`)
- `p32b.b64.txt` = the **verbatim last two lines** of `phase3-assets/phase3.2.txt`
- `phase3.2.hex` = **hex** of `phase3-assets/phase3.2.txt` (sha `b82afeb8…`, 2422 B)
- `reproduce_all_bulbs_corrected (1).py` ≡ `reproduce_all_bulbs_corrected.py`
  (a browser-download duplicate, different filename, identical bytes)

Four cases, three distinct failure shapes: same name, different name, different
*encoding*. Filename matching catches none of them. Hence the procedure below.

## Procedure: triage before you analyse

Run this **first**, on anything newly arrived, before any structural reasoning:

```sh
python3 tools/sibling_index.py            # refresh index (incremental)
python3 tools/triage_new.py <file-or-dir> # EXACT / REENCODING / CONTAINED / DISTINCT
```

`triage_new.py` exits **1** unless every input is `DISTINCT`. That is the point:
it makes the cheap identity check the only step you can take first. Override with
`--force` only when a reason is recorded in `analysis/tested.md`.

Verdicts, in descending confidence: `EXACT` (sha256 match) → `REENCODING` (decoded
hex/base64 payload matches) → `CONTAINED` (bytes occur inside an indexed file) →
`DISTINCT`. Only the last licenses further analysis.

Containment is the expensive step and is bounded by `--max-scan-bytes`; when the
bound is hit the tool says so, because a truncated scan must not be mistaken for a
clean one. `--no-contain` skips it and is correspondingly blind to excerpts.

## Cost of skipping it, measured

On 2026-09-27 I spent a full analysis cycle (entropy, parity splits, XOR-residue
sweep, token-frequency histograms) on the 2086-byte tail of `phase3.2.hex`
before hashing it. The gate finds the same answer in milliseconds and, run over
the same 22-file batch, flagged **2 of 22** as already-held — `phase3.2.hex` and
`reproduce_all_bulbs_corrected (1).py`. The second would have been missed
entirely, since its filename differs from its twin's.

## Related

- `analysis/tested.md` — the ledger; `R-B91PRIME` (2026-09-27) is the most recent row
- `analysis/STATE_BRIEF.md` — reconciled current state and the corpus wall
- `tools/verify_ladder.py` — 41/41 ladder re-derivation; the model for these tools
