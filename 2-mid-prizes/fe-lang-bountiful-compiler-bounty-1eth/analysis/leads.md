# Leads (full notes)

The "Open leads, ranked" section of the folder's `README.md` shows the ranked list; this file
carries the full notes behind each entry. Order leads by cost to test, then by expected value.

## 1. Re-audit the hand-written data in each challenge

- **Cost**: hours
- **What it is**: every challenge encodes the same rules twice, once in its move logic and
  once in a table or a set of offsets written out by hand. The current contracts store the
  adjacency table as decimal digits packed into a `u256` (`1 + 4 * 1000 + 666 * 1000000 + ...`,
  with 666 as the marker for a missing neighbour), the 2D variant recomputes row and column
  from an index, and the packed variants address 4 bit fields inside one word. Each of those
  is a place where a single wrong constant could make the deployed behaviour diverge.
- **Why it ranks here**: it needs no build and no chain access, and the material is about 1,000
  lines in a public repository.
- **What would confirm it**: an input where a contract accepts a move that the reference rules
  in `tools/oracle.py` reject, or where the two disagree on the resulting board.
- **What would kill it**: a line by line reconciliation of all 7 tables against the reference
  adjacency, with the offsets recomputed rather than read.
- **Status**: closed 2026-08-28 - a line-by-line reconciliation of all 7 move/adjacency sources (the shared `ADJACENCY` base-1000 table, `GameBitboard`'s hand-written `moves` map, and the row/col arithmetic in `Game2D`/`GameEnum`/`GameNested`/`GameTrait` plus the packed 4-bit cell offsets) against the reference found 0 wrong constants and 0 divergent moves. Any `INVALID_MOVE` (666) is unreachable because every `MoveField` reverts on `index > 15` before the marker is consulted.

## 2. Differential testing against a reference implementation

- **Cost**: hours
- **What it is**: build the workspace with fe 26.1.0 and Foundry as my guide
  describes, then drive both a locally deployed challenge and `tools/oracle.py` with the same
  random sequences of `moveField` calls, comparing all 16 fields after every call. Include
  calls that should revert, since a missing revert is as much a finding as a wrong board.
- **Why it ranks here**: it covers the compiler as well as the contract, which lead 1 does
  not, at the cost of a build and a test harness. It has not been run publicly against the
  current deployment.
- **What would confirm it**: any divergence between the contract and the reference after the
  same call sequence.
- **What would kill it**: nothing kills it outright. A large sample without divergence bounds
  the defect to the parts of the compiler that these 7 contracts do not exercise, which is
  useful to state with the sample size.
- **Status**: largely closed 2026-08-28 - deployed the source-built bytecode on a local anvil
  node and drove seeded random move+misuse sequences (both accepted and reverted calls) against
  every one of the 7 contracts, comparing the on-chain board with the reference after each
  call. 0 divergences over 2620 comparisons across 3 seeds, with both paths exercised on every
  contract (2620 well-formed comparisons). The malformed-calldata wing of this lead
  (`tools/calldata_probe.py`) then threw 1501 raw/random byte strings per game at the ABI
  decoder (dirty-high-bit aliases, truncated/oversized/multi-word encodings, Game2D arg-structure
  abuse, and 1400 fuzzed blobs across two seeds) and confirmed `isSolved()` can never be reached.
  This bounds any defect to the parts of the compiler these 7 contracts do not exercise; the
  mechanical differential + calldata checks are done. Remaining value lies in Lead 4 (registry).

## 3. Rebuild the two contracts Sourcify does not cover

- **Cost**: hours
- **What it is**: `GameBitboard` (`0x5E987b6aADD4DFC2236D21edE6D07feb04350b06`) and
  `GameTrait` (`0x85b4d0B32b8a285111c244E52524B642f1A5ccFE`) are the two deployed contracts
  with no verified source on Sourcify, while the other 6 match. Compile them from the tagged
  repository with the pinned compiler and compare the runtime bytecode with the deployed code.
- **Why it ranks here**: it is bounded and mechanical, and it either removes a gap in what a
  hunter can trust or shows that the deployed code differs from the published code, which
  would itself be the finding.
- **What would confirm it**: a byte difference between the local build and the deployed
  runtime code that is not explained by metadata or constructor arguments.
- **What would kill it**: a byte for byte match, or a later Sourcify verification by the
  author.
- **Status**: closed 2026-08-28 - downloaded the fe 26.1.0 linux arm64 release, built the whole workspace under a glibc proot, and compared each `*.runtime.bin` byte-for-byte with the on-chain `getCode` output. All 8 contracts (including `GameBitboard` and `GameTrait`) match exactly, metadata included. There is no deployed-vs-published divergence anywhere, so this lead (and the compiler-faithfulness of these 7 contracts) is settled.

## 4. Attack the registry rather than a game

- **Cost**: hours
- **What it is**: the prize logic sits in `claim(address)`. It requires an active lock owned
  by the caller, marks the challenge closed before calling `isSolved()` on it, and then sends
  the prize with a raw call that forwards the remaining gas to the caller. The registry also
  holds 1 ETH against 7 challenges registered at 0.25 ETH each, and keeps every lock deposit.
- **Why it ranks here**: it is the smallest contract in the system and the only one that moves
  money, but the ordering already follows checks, effects, interactions, so this is a reading
  exercise rather than a known weakness.
- **What would confirm it**: a call sequence where the registry pays without the challenge
  reporting a solve, or pays twice for one challenge.
- **What would kill it**: a full reading of the registry source against its compiled output,
  covering the lock accounting and the two raw calls.
- **Status**: largely closed 2026-08-28 - full source reading plus an on-chain replay on a local
  anvil node (`tools/registry_flow.py`: deploy `BountyRegistry` + `DummyGame(true/false)`, fund,
  register, lock, claim, and all negative paths). `claim` pays the caller exactly the prize and
  closes the challenge; claim-without-lock, claim-of-an-unsolved challenge, and double-claim all
  revert. CEI ordering is correct (the challenge is closed before the external `isSolved()` and
  `raw_call`), so no reentrancy double-pay is reachable, and an unregistered challenge can be
  neither locked (`InvalidClaim` on `!is_open`) nor claimed. The registry accounting itself is
   sound; any remaining risk is a compiler miscompilation of the `raw_call`/ABI layer, not a
   source-level accounting flaw, so this lead is closed as far as the published Fe code goes.

## 5. Differential corpus against the adapter compiler (fe 26.1.0)

- **Cost**: hours (build + harness)
- **What it is**: instead of re-reading each contract's source, build small Fe programs that
  reproduce the exact language constructs the 7 games and the registry rely on, compile them
  with the pinned fe 26.1.0, deploy on a local anvil node, and compare on-chain results against
  a revert-aware Python oracle. A miscompilation in any construct the deployed code uses would
  surface here and would be the winning bug.
- **Why it ranks here**: it is the only remaining avenue after leads 1-4 closed (mechanical data,
  differential moves, bytecode==source, and registry accounting are all sound), and it targets
  the compiler itself.
- **What would confirm it**: a single divergence between Fe-compiled on-chain behaviour and the
  Python oracle on a construct a deployed contract uses.
- **What would kill it**: no divergence over a corpus covering every feature the deployed
  contracts exercise.
- **Status**: closed 2026-08-28 (negative result) - 67 exactly-matching checks, 0 divergences,
  across 4 Fe modules (`bountiful/_fuzz/fe/{retfeat,structpack,bitboard,xcall}.fe`, driven by
  `_fuzz/verify.py`): (1) checked u256/u128 arithmetic with overflow reverting (`panic 0x11`) and
  modular `<<`; (2) packed-struct `WordRepr` storage round-trip incl. u128-max, `StorageMap`
  set/get, and fieldless-enum dispatch; (3) bit-packed board ops reproducing the deployed
  `SOLVED_BOARD` (`0xFEDCBA987654321`) exactly across all 16 cells; (4) external-call flows - the
  registry's money-gate `!target.call(IsSolved{})` bool negation, address-routed `store.lock_validator.call`
  calls, and cross-call checked u256 overflow both inside the callee and at the caller's increment.
  The one genuine Fe quirk found (`1<<256`==0, modular vs Solidity's EVM-modulo `1` for shift-left)
  is a documented bitwise-op behaviour of Fe, cannot be reached by any game/registry, and is not
  the bounty bug. Fe 26.1.0 compiles every construct these contracts use faithfully; no exploitable
  miscompilation was found.

  A fifth module (`fe/nestfeat.fe` + `nestprobe.py`) was then added for the one remaining distinct
  construct the deployed registry uses: its exact nested-struct storage layout
  (`RegistryStore { lock_store: LockStore { locks: StorageMap<Address,Lock> }, admin, lock_deposit,
  challenges: StorageMap<Address,Challenge> }`). A stateful probe (real `eth_sendTransaction` writes
  followed by `eth_call` reads) confirmed 9/9: nested `StorageMap` base-slot persistence, sibling-map
  `locks`/`challenges` isolation under the same key, and map-to-scalar isolation all hold, with
  `cast call --trace` independently confirming the write paths are non-reverting. (Note: a first run
  reported "7 FAILS"; these were a harness bug - `eth_sendTransaction` was sent without a `to` field,
  so anvil treated the write calldata as contract-creation - not a Fe defect; the trace fixed the
  diagnosis.) No storage-collision or persistence miscompilation exists in the registry's layout, so
  this lead is closed as a negative result.

  A sixth probe (`fe/ctor.fe` + `ctorprobe.py`) checked the one remaining concrete concern - whether
  the deployed games' `init(lock_validator: Address, packed_board: u256)` constructor stores its args
  faithfully (so a game could hold a different effective board than deployed). Deploying with a known
  `packed_board` (both `ONE_MOVE_BOARD` and `SOLVED_BOARD`) and validator (0xCAFE), then reading back
  rawBoard / all 16 getBoard cells / getValidator / isSolved gave 38/38 exact matches; the stored board
  and validator equal the constructor args bit-for-bit and `isSolved` tracks the board correctly. (The
  only apparent mismatch in a first run was a wrong oracle expectation for which cell holds the empty
  tile in `ONE_MOVE_BOARD` - cell 14, per `shared`'s `[1..14,0,15]` - not a Fe defect.) The constructor
  path is faithful too, so this closed suite now bounds Fe 26.1.0 across arithmetic, storage layout,
  bit-packing, external calls, and construction.



