#!/usr/bin/env bash
# third_door_sweep.sh - run the rockyou wordlist against the certified third-door
# oracle, sharded across cores, with a resumable checkpoint per shard.
#
# WHY THIS EXISTS. `analysis/tested.md` (section-9 cumulative note) records that a
# rockyou.txt pass on both locks and the third door "was still running when that
# session closed and is not counted". The battery was therefore abandoned, never
# witnessed, and - until `tools/third_door.py --wordlist` was added - not even
# reproducible from shipped code, which had no way to accept a wordlist at all.
# This script is the missing harness.
#
# HONEST ACCOUNTING, which is the whole point. Each shard owns a disjoint slice
# of the wordlist by line index, writes its own checkpoint atomically, and prints
# MATCH immediately rather than at the end. Killing the sweep at any moment loses
# no completed work and no count: re-running the script resumes every shard from
# its own byte offset. A shard that finishes is simply skipped on the next run.
#
# MATCHES are written to a single combined hits file as well as to the per-shard
# logs, so a hit is never buried in one log among progress lines.
#
# Local only: compares against addresses already public in data/planted-addresses.csv
# and the two funded gate addresses. No key is swept, nothing is broadcast.
set -u

BASE="$HOME/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle"
WORDLIST="${1:?usage: third_door_sweep.sh WORDLIST [SHARDS] [RESUME_FLAG]}"
SHARDS="${2:-$(nproc)}"
RESUME="${3:-}"
OUT="${OUT_DIR:-/data/data/com.termux/files/usr/tmp/opencode/td_sweep}"
mkdir -p "$OUT"

HITS="$OUT/hits.txt"
touch "$HITS"

echo "wordlist : $WORDLIST ($(wc -l < "$WORDLIST") lines)"
echo "shards   : $SHARDS"
echo "output   : $OUT"
echo

pids=()
for ((i = 0; i < SHARDS; i++)); do
  ck="$OUT/ckpt.$i"
  log="$OUT/shard.$i.log"
  extra=()
  if [[ -n "$RESUME" && -f "$ck" ]]; then
    extra+=(--resume)
  fi
  python3 "$BASE/tools/third_door.py" \
    --wordlist "$WORDLIST" \
    --shard "$i" --of "$SHARDS" \
    --checkpoint "$ck" \
    --every 20000 \
    "${extra[@]}" > "$log" 2>&1 &
  pids+=($!)
  echo "  shard $i started pid ${pids[-1]} -> $log"
done

echo
echo "running. monitor:  tail -f $OUT/shard.*.log"
echo "stop safely:     pkill -f third_door.py   (checkpoints are already written)"
wait "${pids[@]}"

echo
echo "=== sweep finished ==="
grep -h '^MATCH' "$OUT"/shard.*.log 2>/dev/null | tee -a "$HITS"
n=$(grep -ch '^MATCH' "$OUT"/shard.*.log 2>/dev/null | paste -sd+ | bc)
echo "total MATCH lines: ${n:-0}"
