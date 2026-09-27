# Open leads, full notes

## 1. A photograph showing the individual plate seams, not just brick colors

Color separation is no longer the limiting factor: a local quantization step reliably reads
color at the resolution already available (proven at 13 pixels per stud on a sibling
piece). What is missing is a channel that has not yet been ruled out: whether adjacent studs
are one 1x2 brick or two separate 1x1 bricks, visible only as a seam between plates. This
needs diffuse lighting, a straight-on angle, and roughly 40 pixels per stud or more.

No image of COG at that fidelity is known to exist. The artist's own website declares
1,597 by 2,000 pixels as the original size of each panel image in its own file metadata,
which means the file already published is the highest resolution the artist has on hand;
asking the artist for "the full-resolution files" would not produce anything new. COG itself
sold at the show for $14,000 to a private collector (confirmed via the show's own Artsy
listing, archived captures from 2018-03-24 through 2018-09-21) and has not resurfaced at any
gallery, auction house, or consignment listing since, unlike another piece from the same
series that remained in consignment for years afterward. A new photograph would have to come
from that collector, from whoever handled the original 2018 sale, or from a chance future
resale or loan.

A separate video (a workshop interview filmed in the artist's studio, November 2017, 1080p)
contains macro shots at 46 to 68 pixels per stud where individual plate seams are clearly
resolved, proving the needed resolution is achievable by camera. Whether any frame of that
video actually shows COG specifically, rather than a different piece, is not settled.

## 2. Close the color-count gap in the region-search sweep

The localized-region search run on COG so far only tried a 4-color local palette. A sibling
piece in the series (SWAGBUCKS) needed a 5-color local palette to find its real payload at
the same character width; COG has not yet been swept at 5 or 6 colors, nor with a
rectangular (as opposed to square) search window. This is a bounded, inexpensive re-run
once the tooling is in place, not a new hypothesis.

**2026-08-31 status:** the original region-sweep tool was never committed, so `tools/region_sweep.py`
was reconstructed from the tested.md summary and committed (an early off-by-one in the
gray-level quantization produced spurious rows; those are superseded by the corrected run).
With the fix and the color->digit assignment set expanded to the full K! permutations plus an
S-prefix minikey gate, the 5-color (base-5, 3 cells/char, 30/34-char minikey, 3 window shapes,
8 reading orders) pass over all 3 panels derived every structurally-valid S-minikey candidate
(57,106) with 0 hits and is a CERTIFIED negative. The 6-color pass (720 permutations) exceeded
the 2 h phone budget and is UNCERTIFIED/incomplete. So lead 2 is now substantially closed for
the 5-color hypothesis under this model, but remains open for 6 colors and for model details
my reconstruction may diverge on (region shape set, char-width pairs, panel overlap,
repetition).

## 3. Brick-shape and macro analysis of pieces with no public photo yet

Several 2017 pieces in the same series have no known public image at all; OSINT and image
tooling for this are ready and calibrated from the work already done on COG and its solved
siblings.
