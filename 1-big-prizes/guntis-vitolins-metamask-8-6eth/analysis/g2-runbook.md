# G2 sweep - execution runbook

Companion to `analysis/gpu-sweep-g2.md` and the reference executor `tools/sweep_g2.py`.

## What was built (2026-08-28)

`tools/sweep_g2.py` is a correct, data-driven reference implementation of the G2 spec. It:

- builds the post pool P and video pool V from the source surfaces defined inside it,
  auto-filtering every word through the official BIP39 English list;
- excludes the liaison words for the base G2a run, and includes them when asked
  (`--liaisons` = G2b);
- enforces the confirmed anchors and the 6/6 partition exactly as the spec does;
- enumerates every candidate (subsets x C(9,5) x 5! x 4!),
- filters each by the BIP39 checksum, derives the MetaMask address at
  `m/44'/60'/0'/0/0`, and compares against the target;
- runs the mandatory witness protocol before anything else;
- prints its own exact pool sizes, subsets, enumerated and projected derivations, so the
  planning numbers in the spec are replaced by real ones.

## Verified on-device (2026-08-28, this phone)

- `--pool-report` prints the exact pools:
  - post_full (22): act bring cattle dinner dutch fiber forest fork fresh good left market
    month possible rib roast round season soon there wood year
  - video_full (16): chat easy expect finish fog goat hole lake parrot share sing song top
    update winter you  (the four title/hook words top finish winter update are in; per
    issue #10 they are video-side members re-sourced to the description/body)
  - G2a cost (no liaisons): subsets = 969,969; enumerated = 351,982,350,720;
    derivations(proj) = 21,998,896,920  (~22e9 post-checksum derives; ~7.7 h @ 792k/s)
- `--witness-only`: all 3 planted in-set witnesses recover the correct structure.
- `--count-check 200000`: first 200k candidates all distinct, correctly anchored
  (dutch@1, fog@5, parrot@12), and in-set - the enumerator is structurally correct.
- `--limit 1`: full execution path (multiprocessing derive+compare) runs clean.

Local throughput is far too low to finish (== 1,886/s single process here; ~15k/s over the
8 phone cores, so the whole 7.25e9-derive run would take weeks). This is exactly what the
spec warned: "not phone work."

## How to run the real sweep

1. Rent the GPU/server used for prior witnessed sweeps (validated kernel peak
   792,000 derivations/s). Bring `tools/sweep_g2.py` and `tools/oracle.py`.
2. Run `python3 tools/oracle.py --selftest` and log its output (certification gate).
3. Decide G2a (base, no liaisons) vs G2b (add `--liaisons`). G2a is the primary/budget
   run; G2b nearly 4x larger.
4. Run `python3 tools/sweep_g2.py --pool-report` on the target machine and log it.
5. Run `python3 tools/sweep_g2.py` (full). It first runs the witness protocol, then
   enumerates+derives. A negative counts only if the witnesses all recovered (the tool
   halts with a message otherwise).
6. The full Python path is a correct reference and will finish on a capable machine, but
   for speed reproduce the same candidate stream in the fast kernel that hit 792k/s. This
   tool is the reference to validate the kernel against (`--count-check N` on the first N
   candidates).

## If a match is found

Follow `gpu-sweep-g2.md` "What a match means": the tool prints the mnemonic only to the
operator locally (it is key material - never paste it into a shared channel); verify by
importing into an offline reference wallet at `m/44'/60'/0'/0/0`, then sweep the ~8.61 ETH
privately; announce only after funds are moved.

## Pool caveats worth knowing

- `there` remains a **post** pool word in G2a (it is in post sentence A2 but is not in the
  post liaison set `{only, because, like}`); it is excluded from the video pool where it is
  a liaison. This is exactly what `gpu-sweep-g2.md` specifies.
- `you` is a base video word (V2), not a liaison.
- `cloud` is dropped (position 5 = `fog`), per the verified issue #10 correction.
- If the operator wants belt-and-braces on position 5, a second pass with POS5="cloud"
  doubles the space; edit the `POS5` constant in `sweep_g2.py`.
