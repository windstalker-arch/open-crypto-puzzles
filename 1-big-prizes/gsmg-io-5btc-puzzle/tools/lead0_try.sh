#!/usr/bin/env bash
# lead0_try.sh <alphabet|keyword> [--keyword] [--dry]
# One-command human->battery bridge for the Lead-0 interpreter-alphabet leap.
# Usage:
#   tools/lead0_try.sh "FUBCDORA.LETHINGKYMVPS.JQZXW"          # verbatim 28-char board
#   tools/lead0_try.sh --keyword "salphasion"                 # keyed board from keyword
#   tools/lead0_try.sh --dry "MYALPHABET..."                  # decode only, no oracle
#
# Runs the CERTIFIED 3.2.2 VIC battery (keyed_vic_battery.py) under the proven
# parameter grid: maps {pos, canon}, escapes {(1,4),(2,5)}, trans lengths
# {13 (matrixsumlist), 38 (lastwordsbeforearchichoice+thispassword), 7},
# with and without --reverse. Every decode is oracled against BOTH funded gates
# (1GSMG1JC9..., 17ucy1K9...) -> a MATCH prints immediately.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/tools"

DRY=0
SRC=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --keyword) SRC=(--keyword "$2"); shift 2 ;;
        --dry)     DRY=1; shift 1 ;;
        *)         SRC=(--alphabet "$1"); shift 1 ;;
    esac
done

if [[ ${#SRC[@]} -eq 0 ]]; then
    echo "usage: lead0_try.sh <28char-alphabet|--keyword WORD> [--dry]" >&2
    exit 2
fi

FAIL=0
for MAP in pos canon; do
    for ESC in "1 4" "2 5"; do
        for TRANS in 13 38 7; do
            for REV in "" "--reverse"; do
                E=($ESC)
                LABEL="map=$MAP esc=${E[0]},${E[1]} trans=$TRANS rev=${REV:-no}"
                echo "== $LABEL =="
                CMD=(python3 keyed_vic_battery.py "${SRC[@]}" --map "$MAP"
                     --escapes "${E[0]}" "${E[1]}" --trans "$TRANS")
                [[ -n "$REV" ]] && CMD+=(--reverse)
                [[ "$DRY" -eq 1 ]] && CMD+=(--dry)
                "${CMD[@]}" || FAIL=$((FAIL+1))
            done
        done
    done
done
echo "grid complete (failures=$FAIL; a nonzero failure count is EXPECTED for a wrong alphabet)"