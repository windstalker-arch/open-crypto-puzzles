# Lead 0  -  Human inspection checklist (SalPhaseIon page image)

Goal: supply the ONE unprovided input the machine cannot invent  -  the
**interpreter alphabet** (the a..i -> digit mapping, and/or a keyed VIC
alphabet) that turns `dbbib` / `faed` into readable plaintext. The streams are
byte-exact (data/finalpage-digit-streams.json, verified against the live page);
therefore OCR/capturing is NOT the task. Eye-level pattern reading is.

## Viewing the evidence
- Screenshot: `usr/tmp/opencode/salphasion-page.png`  (668x619, 49,970 B)
  - terminal preview:  `img2txt -W 132 usr/tmp/opencode/salphasion-page.png`
  - native viewer:     `termux-open usr/tmp/opencode/salphasion-page.png`
- Live page (text-only, same content): `data/live_salphaseion.txt` / `.html`
- The image is a plain browser render: an h1 "SalPhaseIon" + a long textarea
  token-stream, then h1 "Cosmic Duality" + a second textarea. There are NO
  decorative elements, colors, fonts, or non-text glyphs visible.

## The page structure (1075 tokens, 62 distinct symbols)  -  verify with your eyes
| region | tokens | content |
|---|---|---|
| `dbbib`      | 0..90   | 91 a-i letters (69-char OCR crop + 22 = grid dbbib) |
| binary run 1 | 91..194 | a/b -> `matrixsumlist` (13 bytes) |
| `faed`       | 195..764| 570 a-i letters (+ trailing `z` @765) -> Bifid `BTCSEED...` |
| `z` @829, `z` @859 | separators | |
| z-segment 1  | 766..828| `agdafaoa...` (63, a-i+`o`) -> `lastwordsbeforearchichoice` |
| z-segment 2  | 830..858| `cfobfdhg...` (29, a-i+`o`) -> `thispassword` |
| literal      | 860..900| `s h a b e f our first hint is your last command` |
| blob         | 901..1068| base64 `U2FsdGVkX1...jJ` (== oracle BLOB_B64) |
| binary run 2 | 959..998| a/b inside blob -> `enter` (19 tokens zeroed out) |
| tail         | 1069..1074| `s h a b e f a n s t o o` |

Symbol inventory (counts): `a`138 `b`167 `c`72 `d`71 `e`99 `f`77 `g`127 `h`78
`i`91 `o`17 (z-segments + our/your/anstoo) `z`4 (@765,829,859,958) `s`10 `t`6
`n`6 `r`4 `u`4 `k`4 `j`4 `p`4 ... punctuation: `/` exactly 1 (blob tail),
`+` exactly 2 (blob), **`.` zero**. All base64 letters/digits inside the blob.

## What to look for (the interpreter-alphabet leap)
1. **Ambiguous glyphs / transcription traps**: `l` vs `I`(lowercase L vs capital
   i), `o` vs `0`, `1` vs `l`, `q`(1x,@1040) vs `g`. Any visual difference the
   transcription may have flattened is a candidate NEW symbol with special map.
2. **A keyed-alphabet source**: any ordering clue the page encodes implicitly  - 
   the title word `SalPhaseIon`/`Cosmic Duality`/`GSMG`, the first-token strings
   `dbbib`/`faed` themselves, letter-frequency ordering of the 9 + o symbols
   (b>a>g>e>i>h>f>c>d), or the certified board's own keyed alphabet
   `FUBCDORA.LETHINGKYMVPS.JQZXW`. Decide: does a..i -> digits follow
   alphabetical order, SALPHASION order, dbbib order, or a position-based map?
3. **The missing `.`**: the certified board's two escape columns are keyed by
   `.` and `/`. `/` appears once (blob) but `.` never. Is the single `/` field a
   marker for a second-escape keying (row2) that the page implies but omits?
4. **Case/punctuation asymmetry**: is the ONLY reason upper/lower mixes in the
   blob the base64 alphabet, or is there a non-base64 capitalization somewhere?
5. **Anything faint**: sub-pixel marks, margin glyphs, favicon-URL text
   (`/img/favicon.png`)  -  the 668x619 crop rejects nothing above the fold, but
   verify the bottom edge (last ~8 rows contain `anstoo`).

## Feedback grammar (feed an observation straight into the certified battery)
From `repo/tools/`:
- Alphabet hypothesis (28-char, `.`,`/` escape-keyed):
  `python3 keyed_vic_battery.py --alphabet "FULL28CHARSTRING" --map pos|canon`
- Keyed alphabet by keyword (dedupe + A..Z, splice `.`@8 `/`@18):
  `python3 keyed_vic_battery.py --keyword "salphasion" --map pos`
- Interpreter digit-map (9-char, position i -> digit i):
  `python3 keyed_vic_battery.py --alphabet <28ch> --map-raw "dbifhcega"`
- For upper/lower or `o`=0 / z handling variants, say what you observe; the
  sweep layers (lead0_layers.py, lead0_vicgap.py) can be pointed at new maps.

Every run does a certified 3.2.2-vector selftest first, decodes both streams,
and oracles all decoded plaintext candidates against BOTH funded gates
(1GSMG1JC9..., 17ucy1K9...). A MATCH prints immediately.

Convenience wrapper: `tools/lead0_try.sh <alphabet|keyword>` (see next file).