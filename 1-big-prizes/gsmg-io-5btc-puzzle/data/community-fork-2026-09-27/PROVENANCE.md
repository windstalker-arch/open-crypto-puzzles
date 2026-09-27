# Community fork material (Naddiseo/gsmgio-5btc-puzzle, fetched 2026-09-27)

Source: `https://github.com/Naddiseo/gsmgio-5btc-puzzle` @ `master`, 87 blobs.
CORRECTION 2026-09-27 (`R-FORKWIRE`): this file first recorded "tarball sha256
`30b46159a34946a5a094edc8bb61e111`". That is 32 hex characters, so it was never a
sha256, and it does not reproduce: the current `master` tarball is 15,169,647 B
(recorded 15,169,507 B), md5 `5b175c1773a378d2a5a5d26fb3942e54`, sha256
`b9c095f31a9842d166fdf1b328ba4c2b341b7bb2ea3a2390579354584cb36598`. Archive
tarballs are not byte-stable, so **the pinned identity is the 87-file sha256
set**, now in `data/sibling_index.json` - and all 87 reproduce exactly. The fork is
by **Naddiseo** (GitHub `CONTRIBUTOR`, not an author), the de facto maintainer of
the community repo - see issue #93 ("Since I've wrote much of the current
README.md of this repo, I've been maintaining my own up-to-date fork") against the
abandoned official repo (issue #105). **No file here is author-published and none
is certified as authorial.** It is community work, kept separate for that reason.

Only the two small PLAINTEXTS are copied in. They are here because one of them
is a hard witness for the whole acquisition:

| file | bytes | sha256 | status |
|---|---|---|---|
| `phase2.1.txt` | 648 | `e2f9dd65604a3231f8b3301724e8d713a88fffc4b6c7c4aeeb20f58a582b593a` | **byte-identical to the phase-2 plaintext this repo derived independently** (`R-BLOBINV`, from the `06286612` envelope + `sha256("causality")`) |
| `phase3.txt` | 4090 | `c4ad94559a44a927c1032cc0e024515f9510a0806a2d14458dbf4a360af9865f` | phase-3 plaintext, previously known only by reference |

`phase2.1.txt` matching our own derivation hash-for-hash is what licenses
treating the rest of the fork as the same artifacts rather than fabrication.

Not copied in here (15 MB): 34 author `hints/*.png` images, 9
`phase2.1-assets/*.png`, 3 `decentraland-assets/*.png`, 6 `phase3-assets/*`, and
the 7 author-solve notebooks (`phase0`-`phase3.2`, `salphaseion`,
`decentraland`). See `analysis/tested.md` row `R-FORK-2026-09-27`.

WHERE THEY ARE NOW (corrected `R-FORKWIRE`, 2026-09-27). The full 87-file working
copy used to sit in a tool temp directory
(`$PREFIX/usr/tmp/opencode/quarantine/naddiseo/gsmgio-5btc-puzzle-HEAD/`) and has
been **deleted** - the tool temp dir was cleaned. It has been re-fetched and
restored to the external card, which survives that cleanup:

    ~/storage/external/briefcase/gsmg-fork-naddiseo/     87 files, 25 MB

All 87 sha256s match the deleted copy, so the restore is certified, not assumed.
Re-fetch any time with:

    curl -sL -o /tmp/x.tgz https://github.com/Naddiseo/gsmgio-5btc-puzzle/archive/refs/heads/master.tar.gz
    mkdir -p ~/storage/external/briefcase/gsmg-fork-naddiseo
    tar xzf /tmp/x.tgz -C ~/storage/external/briefcase/gsmg-fork-naddiseo --strip-components=1
    python3 tools/sibling_index.py --rebuild

`tools/sibling_index.py --stats` now flags any root that has vanished
(`STALE(missing on disk)`) precisely so that a cache answer is never mistaken for
a readable file.
