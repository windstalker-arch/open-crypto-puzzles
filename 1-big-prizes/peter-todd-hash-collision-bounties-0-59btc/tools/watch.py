#!/usr/bin/env python3
"""Peter Todd hash-collision bounty: passive issue monitor.

Status is WATCH (see README): winning requires a published full collision on SHA-256,
RIPEMD-160, HASH160 or HASH256, which is a research result, not a scheduled computation.
The one zero-cost, on-device action is to watch the 4 live escrow addresses for any spend
(a third party claiming first). Run this periodically; it prints each address's current
state and loudly flags a divergence from the recorded baseline.

Exit code: 0 if all live addresses remain unspent (or any address data could not be
fetched, reported as UNKNOWN), 1 if a live address has become spent (a claim happened),
2 if one is funded/empty but the pattern is ambiguous. Read the printed lines, don't
rely on the code alone.
"""

import json
import sys
import urllib.request

MEMPOOL_API = "https://mempool.space/api/address/{}"

# (hash_function, address) for the 4 live targets. The SHA-1 reference was claimed in
# 2023 and is excluded; it is the calibration vector, not a target.
LIVE = [
    ("sha256", "35Snmmy3uhaer2gTboc81ayCip4m9DT4ko"),
    ("ripemd160", "3KyiQEGqqdb4nqfhUzGKN6KPhXmQsLNpay"),
    ("hash160", "39VXyuoc6SXYKp9TcAhoiN1mb4ns6z3Yu6"),
    ("hash256", "3DUQQvz4t57Jy7jxE86kyFcNpKtURNf1VW"),
]

# Baseline recorded from the on-chain check on 2026-08-16 (redeem_scripts.csv).
BASELINE_SPENT = {"sha256": False, "ripemd160": False, "hash160": False, "hash256": False}


def fetch(address: str):
    req = urllib.request.Request(MEMPOOL_API.format(address), headers={"User-Agent": "curl/8"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main():
    changed = False
    unreadable = False
    any_spent = False
    for name, addr in LIVE:
        try:
            d = fetch(addr)
            cs = d["chain_stats"]
            funded = cs["funded_txo_sum"]
            spent = cs["spent_txo_sum"]
            balance = funded - spent
            status = "UNSPENT" if spent == 0 else "SPENT"
            if spent > 0:
                any_spent = True
            baseline = BASELINE_SPENT.get(name)
            changed_flag = ""
            if spent > 0 and not baseline:
                changed_flag = "  <-- CHANGED: was unspent, now spent (CLAIMED)"
                changed = True
            print(f"{name:10s} {addr}  status={status}  balance_sat={balance} "
                  f"funded_sat={funded} spent_sat={spent}{changed_flag}")
        except Exception as e:  # network/parse error
            unreadable = True
            print(f"{name:10s} {addr}  UNKNOWN (could not fetch: {e.__class__.__name__}: {e})")
    if any_spent:
        print("\nALERT: one or more live bounty addresses has been spent. "
              "A collision pair has likely been claimed on-chain.")
        return 1
    if unreadable:
        print("\nOne or more addresses could not be checked; retry later.")
        return 0
    if not changed:
        print("\nAll 4 live addresses remain unspent (unchanged from baseline). No claim.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
