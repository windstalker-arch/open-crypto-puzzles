# Community fork material (Naddiseo/gsmgio-5btc-puzzle, fetched 2026-09-27)

Source: `https://github.com/Naddiseo/gsmgio-5btc-puzzle` @ HEAD, tarball
sha256 `30b46159a34946a5a094edc8bb61e111`, 87 blobs. The fork is by **Naddiseo**
(GitHub `CONTRIBUTOR`, not an author), the de facto maintainer of the community
repo - see issue #93 ("Since I've wrote much of the current README.md of this
repo, I've been maintaining my own up-to-date fork") against the abandoned
official repo (issue #105). **No file here is author-published and none is
certified as authorial.** It is community work, kept separate for that reason.

Only the two small PLAINTEXTS are copied in. They are here because one of them
is a hard witness for the whole acquisition:

| file | bytes | sha256 | status |
|---|---|---|---|
| `phase2.1.txt` | 648 | `e2f9dd65604a3231f8b3301724e8d713a88fffc4b6c7c4aeeb20f58a582b593a` | **byte-identical to the phase-2 plaintext this repo derived independently** (`R-BLOBINV`, from the `06286612` envelope + `sha256("causality")`) |
| `phase3.txt` | 4090 | `c4ad94559a44a927c1032cc0e024515f9510a0806a2d14458dbf4a360af9865f` | phase-3 plaintext, previously known only by reference |

`phase2.1.txt` matching our own derivation hash-for-hash is what licenses
treating the rest of the fork as the same artifacts rather than fabrication.

Not copied in (15 MB, still in quarantine pending a mining pass): 34 author
`hints/*.png` images, 9 `phase2.1-assets/*.png`, 3 `decentraland-assets/*.png`,
6 `phase3-assets/*`, and the 7 author-solve notebooks (`phase0`-`phase3.2`,
`salphaseion`, `decentraland`). See `analysis/tested.md` row `R-FORK-2026-09-27`.
