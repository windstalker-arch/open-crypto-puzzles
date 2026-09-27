# GPU sweep spec G2: metadata-extension words (+ optional liaison extension)

Written 2026-08-23 after lead 3's execution found 11 new BIP39-dictionary words in
never-read metadata surfaces (see `leads.md`, lead 3 status). This file is the runnable
specification for the next big-prize sweep on this puzzle, priced so the operator can rent
exactly enough GPU time. It follows the same protocol as every witnessed sweep in
`tested.md`.

## Target

12-word BIP39 English mnemonic, no passphrase, MetaMask default path `m/44'/60'/0'/0/0`,
compare derived address case-insensitively against
`0x9C2F44EFAd0c1E852a09dF9939e6DaF061140CaF`. Oracle: `tools/oracle.py` (certified against
the canonical BIP-0039 vector; run `--selftest` before the sweep and log its output).

## Word pools (defined by rule, built by the runner)

Filter every pool through the official BIP39 English list; non-members are dropped before
enumeration (they cannot form valid mnemonics).

- **Post pool P**: full words of sentences A1, A2, A3 ("Round dutch cattle...", "Only
  because there is a lot of healthy fiber.", "Hunter like the rib roast dinner fresh.");
  footer tags (`season`, `market`, `round`; `fork` is handled as floating below);
  `og:description` additions found 2026-08-23 (`possible`, `bring`, `good`, `act`, `soon`,
  `left`, `month`, `year`); natural inflections of included words (R1b rule).
- **Video pool V**: full words of V1, V2 ("Don't expect anything easy there will be dark
  fog on the lake.", "Do you think its more likely for parrot can sing a song then for a
  goat to whistle?"); title/hook-line words (`top`, `update`, `winter`, `finish`);
  formatting-layer additions found 2026-08-23 (`hole`, `share`, `chat`); natural
  inflections.
- **Optional liaison set L** (lead 1): BIP39-member connecting words drawn from the same
  five sentences, added to their own side's pool: `there`, `will`, `more`, `can`, `then`
  (video); `only`, `because`, `like` (post). Non-members such as "anything", "healthy",
  "whistle", "living" are already excluded automatically by the dictionary filter.

## Constraints

- position 1 = `dutch`; position 12 = `parrot` (confirmed).
- position 5 = `fog` (primary branch; per the verified issue #10 correction `cloud` is
  dropped as a candidate. If the operator wants belt-and-braces, a second pass with
  position 5 = `cloud` doubles the space; not part of the base quote.)
- `fiber` and `fork` are confirmed members and must each appear once, in any of the free
  slots.
- partition preserved: post half contributes exactly 6 words (dutch + fiber + fork + 3
  chosen from P), video half exactly 6 (fog + parrot + 4 chosen from V).
- free slots are positions {2, 3, 4, 6, 7, 8, 9, 10, 11}; post fills any 5 of them, video
  the remaining 4.

## Enumeration and cost formula

    subsets      = C(|P|,3) x C(|V|,4)
    orderings    = C(9,5) x 5! x 4!            = 362,880 per subset
    enumerated   = subsets x 362,880
    derivations  ~= enumerated / 16             (BIP39 checksum filter, measured 6.25%)
    t            = derivations / kernel_rate

Reference points from this repository's own ledger: R1 ran 3.38 billion derivations in
87 minutes at 648,936/s; R1b ran 10.75 billion in about 4.5 hours at 668,827/s; the
validated kernel peak is 792,000/s.

With R1-era baseline pool sizes backed out of R1b's own subset count (|P| about 20,
|V| about 11 including inflections), adding the 11 new words gives roughly:

    G2a  new words only, no liaisons:  |P| ~ 28, |V| ~ 14
         subsets ~ 3.3 million  ->  ~7.4e10 derivations  ->  ~26 h @ 792k/s
    G2b  new words + liaisons:         |P| ~ 31, |V| ~ 17
         subsets ~ 11.8 million ->  ~2.7e11 derivations  ->  ~4 days @ 792k/s

The runner MUST print its own exact `subsets`, `enumerated`, `derivations` (projected) and
measured rate before and during the run; these estimates are planning numbers only.

**2026-08-28 exact numbers from `tools/sweep_g2.py --pool-report`** (these supersede the
planning numbers above; the tool's pools exclude liaisons for G2a per the definitions below,
and include the four video title/hook words top finish winter update, re-sourced per issue
#10):

    G2a: post_full = 22 (19 choose-3), video_full = 16 (14 choose-4)
         subsets = C(19,3) x C(14,4) = 969 x 1001 = 969,969
         enumerated = 351,982,350,720 ; derivations(proj) = 21,998,896,920
         ~7.7 h @ 792k/s
    G2b (add --liaisons): re-derive with the tool (larger, roughly 4x).

The reference executor `tools/sweep_g2.py` builds the pools, runs the witness protocol,
and (on a capable machine) runs the whole sieve; see `analysis/g2-runbook.md`.

## Witness protocol (mandatory, same standard as tested.md)

Before the real enumeration, plant candidates known in advance to be in the swept set, one
per corner, and require their addresses to be recovered:

1. highest-index P/V choices, `fiber` in slot 2, `fork` in slot 11;
2. lowest-index P/V choices, `fiber` in slot 11, `fork` in slot 2;
3. one witness containing a new 2026-08-23 word on each side (`possible` post-side, `hole`
   video-side);
4. one witness using a liaison word on each side (G2b only).

A negative counts only if all planted witnesses are recovered; otherwise report the run as
unwitnessed, not as a negative.

## What a match means

Stop immediately, print the full mnemonic ONLY to the operator locally (it is key material;
never paste it into any shared channel), verify by importing into an offline reference
wallet at `m/44'/60'/0'/0/0`, then sweep the 8.61 ETH privately. Announce only after funds
are moved.
