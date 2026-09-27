# Open leads, full notes

## 1. A higher-fidelity copy of the original video

The whiteboard and the Bitcoin whitepaper page held by a person in the video ("Dmitri")
only become legible above 720p, and no source above 720p is currently reachable: both
known YouTube video IDs are dead, and a direct video-index lookup on the Wayback Machine
returns "not archived or indexed" (the HTML page for the video is archived; the video
stream itself is not, in this index). A full-site WARC capture of the original upload may
exist under archive.org outside the indexes already checked, since archive.org keeps some
video content outside the standard video index. This is the highest-ranked lead because it
is the only channel identified so far where the puzzle's own material (not a wordlist) is
suspected to contain the answer, and it is currently unread rather than ruled out.

- **Status**: archive-WARC sweep executed 2026-08-27, closed as a negative (details below).
  What still remains is a *non-archive* higher-res copy (a living source kept by someone),
  which is not something this device's tooling can reach.

### WARC sweep delta (executed 2026-08-27)

- **Video identity confirmed from the contest page itself.** The archived contest page
  (`web/20150208172337/https://rushwallet.com/contest`, 9,573 B raw) embeds the promo video
  from YouTube: `<iframe ... src="https://www.youtube.com/embed/sr8lBrtd9U4">`. Title on the
  page: "Fundraising with Bitcoin | Find The Bitcoins Contest"; video is the "RushWallet
  Fundraiser." So `sr8lBrtd9U4` is the video the clues live in.
- **No video file was ever hosted on rushwallet.com.** A full CDX dump of every unique URL
  captured under `rushwallet.com` for 2013-2016 (the original-site era, ~90 unique assets)
  contains zero video assets (no mp4/webm/flv/ogv/mov). The only media files ever served by
  the original site were audio: `baron.mp3` (3,341,259 B), `turn.mp3` (152,234 B),
  `balance.wav` (7,149 B). So there is no site-hosted >720p copy sitting in the full-site
  WARC.
- **No archive.org item contains the video.** `advancedsearch.php` returns numFound 0 for
  `rushwallet`, `kryptokit`, and the video ID `sr8lBrtd9U4`; the only hits for "find the
  bitcoins contest" are unrelated (a WIA news broadcast, a VOA broadcast, a DEF CON 23
  brainwallet talk).
- **Highest-res archived single frame is 1280x720 and not legible.** The Wayback captured
  the video's thumbnails at `web/20141121043107/https://i.ytimg.com/vi/sr8lBrtd9U4/`:
  `maxresdefault.jpg` (60,303 B, 1280x720), `sddefault.jpg` (29,124 B, 640x480),
  `hqdefault.jpg` (19,893 B, 480x360), `mqdefault.jpg` (10,094 B, 320x180). The maxres
  frame is a bright (mean 223.7, 68.7% pixels > 215) scene with all fine detail in the
  central band (x≈440-900, y≈120-520) - consistent with the person/whiteboard shot. OCR
  (tesseract 5.5.3) on the raw, on 2-4x cubic upscales, and on central crops returns only
  noise ("o9", "- N,"), i.e. the whiteboard/paper text is not recoverable at 720p - matching
  the prior finding that 720p is the legibility ceiling.
- **The archived YouTube watch pages retain no stream URLs.** The DOM/stream URLs
  (`googlevideo.com/videoplayback`) are absent from every archived capture of the watch page
  (2016: shell page "YouTube"; 2025: 194 KB consent/shell). CDX returns no
  `get_video_info` WARC for the ID. A domain-wide CDX scan of `*.googlevideo.com` filtered
  for the ID cannot complete within a 60 s timeout (huge host block), but the standard
  Wayback video index already reported the stream "not archived or indexed," so a stream
  WARC is not expected to be recoverable in practice.
- **Bottom line.** No >720p copy of the specific video is recoverable from archive.org's
  Wayback WARC or item store. The only remaining path to a higher-fidelity source is a
  living copy held by a person (author, a re-uploader, or a community member), i.e. outreach
  rather than archive tooling.

### Living-copy check (executed 2026-09-12, partially positive)

- The surviving re-upload `x0LqsUOIw0M` is still live on YouTube as of 2026-09-12 (the
  ledger's older finding that both original-upload IDs `sr8lBrtd9U4` and `Mbu9dD8ahgE` are
  dead remains true; the re-upload is a third ID and is alive). Metadata via yt-dlp:
  title "rushwallet", uploader Josh91 (`@Josh-zr2rm`, channel UCnV692nc7SnsmGlPh4LKLzQ),
  uploaded 2024-03-02, 111 s, 16 likes, no description, no tags. Its top format is
  1280x720 (avc1, 357 k, 4.71 MiB); no resolution above 720p is offered, and a 720p
  download attempt from this device was blocked by HTTP 403 so the frame stream was not
  re-OCR'd here.
- The re-upload's 4 comment threads (timestamps 2025-09-12, i.e. live hunters) are new
  material that was never in the ledger:
  1. `@edas12000`: "Hi, are you still looking for wallet 30? Or do you already have the
     seed?" / later "Nothing yet. I don't know if there's any help with that last wallet."
  2. `@Brutal_Jazzy`: "i'm still looking for it are you? do you have confirmation where it
     belongs?"
  3. `@mjscaruaru` (score 2): "1:16 deve ter um segredo." (Portuguese: "there must be a
     secret at 1:16"). A specific in-video timestamp claim, made 2025-09-12, i.e. after the
     last OCR pass; untested because the legibility ceiling is still 720p. This is the new
     specifier to re-check the moment any higher-fidelity copy appears.
- New outreach surface from this check (contact list): (1) re-uploader `Josh91`/`@Josh-zr2rm`
  uploaded 2024, can plausibly provide their source file or a 1080p upload if asked;
  (2) `@edas12000` and `@Brutal_Jazzy`, active fellow hunters as of 2025-09-12, potentially
  willing to compare notes; (3) `@mjscaruaru`, who flagged the 1:16 moment and may know why
  that specific time.
- Not re-run: the archive WARC sweep (2026-08-27 negative), the 720p frame OCR over the
  4 earlier sources (negative), and the audio Morse track (fully decoded). The 1:16 still is
  the only new claimant-specific pixel to check, blocked on fidelity.

## 2. An unabsorbed public quote corpus

The Quotes-500K corpus (compiled by ShivaliGoel, linked from the original source as
`goo.gl/R3Sa34`) has not been run against the oracle. Given the contest's other clues favor
short, quotable, thematically loaded phrases (see the John Donne and whitepaper-title
material already tested), a quote corpus of this kind is a plausible next family at a low
cost, on the order of minutes once prepared.

- **Status**: executed 2026-08-23, closed. The original Google Drive link is dead; the run
  used the Hugging Face mirror `jstet/quotes-500k` (sha256 verified). 493,789 unique quotes,
  verbatim, 0 matches, witnessed (3/3 sibling passphrases planted and re-found). Row added
  to `tested.md`.

## 3. The uncovered tail of the lyrics corpus

The lyrics sweep in the tested ledger covered the most-viewed 301,000-song, 12-million-line
slice of a larger corpus. The remaining tail, roughly 4.7 million further songs, was never
ingested. This is ranked below leads 1 and 2 because it is a much larger, much lower
signal-to-noise family: nothing in the contest's own material specifically points to an
obscure song.

## Explicitly not recommended

A blind character-mask search (fixed length, unconstrained charset) is not recommended
unless a new constraint fixes the structure of #30's passphrase; without that, a masked
brute force over an open charset has no realistic bound and would not be a bounded search
in the sense this project otherwise requires.
