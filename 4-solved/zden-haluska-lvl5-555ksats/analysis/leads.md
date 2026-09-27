# Open leads, full notes

## 1. A clarification from the author on 3 exact bindings

The geometry is fully certified and the mini-hint formula is read at the pixel level, but 3
specific meanings are not fixed by anything the author has published:

- What "x" refers to in "64/x - x": a value that varies per rectangle or per pair (most
  likely a border-thickness measurement), or a single fixed constant.
- The exact normalization meant by "apply more operations to obtain the results in byte
  range": which specific rounding or scaling step turns a raw sum into a single byte.
- The exact sense of "following": which of the several spatially plausible pairings (or a
  sorted-order pairing not yet fully explored) the author means.

Once any one of these is fixed by new information, the already-certified geometry becomes
the 32 key bytes by direct calculation, with no further search needed. The author has a
track record of eventually clarifying hints for other puzzles in the same series (a
correction was already issued once, in 2021, for this puzzle itself), so a direct question
to the author is the highest-ranked lead here.

## 2. A higher-fidelity source for the mini-hint glyphs

The 2021 mini-hint is read at the pixel level from the published image itself; a source
image at higher resolution than what has been published (if one exists) could resolve
ambiguity in the glyph reading directly, without needing the author's own clarification.

## 2b. The digit band and extra mini-hint glyphs (RESOLVED via OCR -- not a lead)

Pixel-level re-extraction (`tools/extract_minihint.py`, see tested.md #10) shows the 2021
mini-hint is a composite of 4 stacked formula lines (rows 806-872), a 14-glyph dot-matrix
digit band (rows 926-931), and two further glyphs (rows 913-923, 932-942). The digit band
was never documented before. However, best-effort fixed-font OCR AND tesseract both resolve
it as the **`09111819` / `11122111` date pair** (publish/fix dates), which tested.md already
ruled out as key data. So this is corroboration, not a new key source; it is NOT a live
lead. The remaining blocker stays the meaning of the 3 formula terms (lead #1) and any
higher-fidelity source for the formula glyphs (lead #2).

## 3. A wider author-error tolerance sweep

A 3-byte wildcard tolerance sweep on 1 or 2 of the candidate bases already tried (roughly
660 million derivations per base) is a bounded search, not an open-ended one, but its
expected value is marginal against the leads above and it has not been run.
