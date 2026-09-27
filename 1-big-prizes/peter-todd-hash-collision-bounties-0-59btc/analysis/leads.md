# Open leads: Peter Todd hash-collision bounties

Full notes. The README shows the ranked summary.

## 1. A published practical or academic collision on a live target

The only event that changes this puzzle is a genuine, practical full collision on SHA-256,
RIPEMD-160, or their composite forms HASH160 and HASH256, published the way SHAttered was
for SHA-1 in 2017. This is a cryptography research result, not a search I can mount or
schedule. What would confirm it: an academic paper or public disclosure with a verifiable
example pair. What would let me claim it here: feeding that pair straight into
`tools/oracle.py`.

## 2. RIPEMD-160 and HASH160 as the most-watched sub-targets

Of the 4 live functions, RIPEMD-160 (and its composite, HASH160) carries the smallest
generic bound (2^80 versus SHA-256's 2^128) and the more active reduced-round literature.
If any of the 4 falls first, this is the most likely candidate. Not an action, a
prioritization for what to watch.

## 3. Passive monitoring

I recommend watching the `spent` flag on the 4 live addresses, to catch a third party
claiming first, and watching RIPEMD-160/SHA-256 collision announcements.

STATUS 2026-08-28: a zero-dependency monitor is now shipped at `tools/watch.py` (stdlib
urllib + json, mempool.space API). Run it periodically; it reports each live address's
state and returns exit 1 with an ALERT if any live address has become spent (a collision
pair claimed on-chain). First run 2026-08-28 confirmed all 4 still UNSPENT (sha256
0.27734251, ripemd160 0.11576888, hash160 0.10026873, hash256 0.10026873 BTC). Also watch
RIPEMD-160 / SHA-256 collision announcements; this stays a WATCH puzzle until a real
collision is published.
