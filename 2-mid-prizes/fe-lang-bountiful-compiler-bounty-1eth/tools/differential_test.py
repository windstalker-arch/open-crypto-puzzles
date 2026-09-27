#!/usr/bin/env python3
"""
differential_test.py -- drive the deployed bountiful game contracts on a local
anvil chain and compare their boards against the Python reference (tools/oracle.py)
after every moveField call.

This is the mechanical core of Open Lead 2 (differential testing). Any divergence
between an on-chain board and the reference after the same call sequence is a
finding. Agreement over a large sample bounds the defect search rather than closing
it.

Usage (run from the puzzle folder, while `anvil` is running on :8545):
    python3 tools/differential_test.py --selftest
    python3 tools/differential_test.py --moves 200 --per-game 50 --seed 1

Notes:
  - Uses eth_sendTransaction with anvil's unlocked default account (auto-signed).
  - Moves a "random legal" move set: a valid move from the current empty cell plus
    occasional invalid/out-of-range moves, so both accepted and reverted calls are
    compared against the reference.
"""
import argparse
import json
import os
import random
import sys
import time
import urllib.request

FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(FOLDER, "data")
BOUNTIFUL = "/data/data/com.termux/files/usr/tmp/opencode/bountiful"
OUT = os.path.join(BOUNTIFUL, "contracts", "out")

RPC = os.environ.get("ANVIL_RPC", "http://127.0.0.1:8545")
FROM = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
UNSOLVABLE_BOARD = 0x0EFDCBA987654321
SOLVED = 0x0FEDCBA987654321

# Game -> (contract id, getBoard(single-index?) , moveField is 1-arg or 2-arg)
GAMES = [
    ("Game", "single"),
    ("Game2D", "two"),
    ("GameEnum", "single"),
    ("GameBitboard", "single"),
    ("GameMonadic", "single"),
    ("GameNested", "single"),
    ("GameTrait", "single"),
]

# reference adjacency (shared/game_util.fe, mirrored in tools/oracle.py)
ADJ = {
    0: [1, 4], 1: [0, 2, 5], 2: [1, 3, 6], 3: [2, 7],
    4: [0, 5, 8], 5: [1, 4, 6, 9], 6: [2, 5, 7, 10], 7: [3, 6, 11],
    8: [4, 9, 12], 9: [5, 8, 10, 13], 10: [6, 9, 11, 14], 11: [7, 10, 15],
    12: [8, 13], 13: [9, 12, 14], 14: [10, 13, 15], 15: [11, 14],
}

SELECTORS = {
    "getBoard1": "0x45e09e54",   # getBoard(uint256)
    "getBoard2": "0x58e4f026",   # getBoard(uint256,uint256)
    "moveField1": "0x8bf02f32",  # moveField(uint256)
    "moveField2": "0xc069fdaa",  # moveField(uint256,uint256)
    "isSolved": "0x64d98f6e",
}


class RpcError(Exception):
    pass


def rpc(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode())
    if "error" in body:
        raise RpcError(body["error"])
    return body["result"]


def call_read(to, data):
    return rpc("eth_call", [{"to": to, "data": data}, "latest"])


def call_write(to, data, value=0):
    """Send a tx (anvil auto-signs) and return True if it mined successfully,
    False if it reverted. A revert must be detected from the receipt status, not
    from eth_sendTransaction (which returns a hash regardless)."""
    txhash = rpc("eth_sendTransaction", [{"from": FROM, "to": to, "data": data, "value": hex(value)}])
    for _ in range(200):
        rec = rpc("eth_getTransactionReceipt", [txhash])
        if rec:
            return int(rec["status"], 16) == 1
        time.sleep(0.02)
    raise RuntimeError("tx %s never mined" % txhash)


def deploy(binpath, args_hex_wo0x):
    with open(binpath) as f:
        init = f.read().strip()
        if init.startswith("0x"):
            init = init[2:]
    data = "0x" + init + args_hex_wo0x
    txhash = rpc("eth_sendTransaction", [{"from": FROM, "data": data}])
    # wait for receipt and find created address
    addr = None
    for _ in range(100):
        rec = rpc("eth_getTransactionReceipt", [txhash])
        if rec and rec.get("contractAddress"):
            addr = rec["contractAddress"]
            break
        import time
        time.sleep(0.05)
    if not addr:
        raise RuntimeError("deploy did not return a contract address for %s" % binpath)
    return addr


def abi_uint(v):
    return "%064x" % v


def abi_addr(a):
    return a[2:].lower().rjust(64, "0")


def abi_bool(b):
    return ("%064x" % (1 if b else 0))


def read_board_single(addr):
    board = []
    for i in range(16):
        out = call_read(addr, SELECTORS["getBoard1"] + abi_uint(i))
        board.append(int(out, 16))
    return board


def read_board_two(addr):
    board = []
    for i in range(16):
        out = call_read(addr, SELECTORS["getBoard2"] + abi_uint(i // 4) + abi_uint(i % 4))
        board.append(int(out, 16))
    return board


def move_single(addr, index):
    return call_write(addr, SELECTORS["moveField1"] + abi_uint(index))


def move_two(addr, row, col):
    return call_write(addr, SELECTORS["moveField2"] + abi_uint(row) + abi_uint(col))

def reference_apply(board, index):
    """Return (new_board, ok). ok=False means the reference reverts (invalid index or not movable)."""
    if index < 0 or index > 15:
        return None, False
    e = board.index(0)
    if index not in ADJ[e]:
        return None, False
    out = list(board)
    out[e] = out[index]
    out[index] = 0
    return out, True


def setup():
    # deploy validator(false)
    vbin = os.path.join(OUT, "DummyLockValidator.bin")
    validator = deploy(vbin, abi_bool(False))
    print("DummyLockValidator(false) @", validator, flush=True)
    deployed = {}
    for name, kind in GAMES:
        binp = os.path.join(OUT, name + ".bin")
        addr = deploy(binp, abi_addr(validator) + abi_uint(UNSOLVABLE_BOARD))
        deployed[name] = (addr, kind)
        print("deployed %-14s @ %s" % (name, addr), flush=True)
    return validator, deployed


def check_initial(deployed):
    for name, (addr, kind) in deployed.items():
        board = read_board_two(addr) if kind == "two" else read_board_single(addr)
        packed = 0
        for i, v in enumerate(board):
            packed |= v << (4 * i)
        ok = (packed == UNSOLVABLE_BOARD)
        print("%-14s initial %s packed=%#018x %s" % (
            name, "OK" if ok else "MISMATCH", packed, "" if ok else "expected %#x" % UNSOLVABLE_BOARD), flush=True)
        if not ok:
            return False
    return True


def random_legal_index(board, rng, misuse=0.05):
    # mostly a legal move from the empty cell; sometimes an invalid/out-of-range call
    if rng.random() < misuse:
        # 40% out-of-range, 60% a non-adjacent valid-range field
        if rng.random() < 0.4:
            return rng.choice([16, 17, 99, 255])
        e = board.index(0)
        legal = set(ADJ[e])
        nonlegal = [i for i in range(16) if i not in legal]
        return rng.choice(nonlegal) if nonlegal else legal[0]
    e = board.index(0)
    return rng.choice(ADJ[e])


def diff_one(name, addr, kind, n_moves, rng, results):
    # Always source the reference from the true on-chain board, read fresh each step,
    # so a missed revert or unexpected accept cannot desync the tracker.
    for step in range(n_moves):
        before = read_board_two(addr) if kind == "two" else read_board_single(addr)
        idx = random_legal_index(before, rng)
        ref_board, ref_ok = reference_apply(before, idx)
        # drive on-chain (returns whether the tx mined without reverting)
        if kind == "two":
            succeeded = move_two(addr, idx // 4, idx % 4)
        else:
            succeeded = move_single(addr, idx)
        after = read_board_two(addr) if kind == "two" else read_board_single(addr)

        results["agreements"] += 1
        if succeeded:
            results["accepted"] += 1
        else:
            results["reverted"] += 1
        if not succeeded:
            if not ref_ok:
                continue  # agreed: both reverted
        else:
            if ref_ok and after == ref_board:
                continue  # agreed: both accepted and produced the same board

        # divergence
        results["divergences"].append({
            "game": name, "step": step, "index": idx,
            "before": before, "ref_ok": ref_ok, "ref_board": ref_board,
            "reverted_chain": not succeeded, "after": after,
        })
        results["finding"] = {
            "game": name, "step": step, "index": idx,
            "before": before, "ref_ok": ref_ok, "ref_board": ref_board,
            "reverted_chain": not succeeded, "after": after,
        }
        return  # stop this game at first divergence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--moves", type=int, default=200)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    if args.selftest:
        b = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 14, 0]
        # empty at index 15; legal neighbours are 11 and 14. Move the tile at 14 into it.
        nb, ok = reference_apply(b, 14)
        assert ok and nb[14] == 0 and nb[15] == 14
        # an unrelated in-range field (0) is not adjacent to the empty cell -> reject
        assert reference_apply(b, 0)[1] is False
        # an out-of-range index is rejected
        assert reference_apply(b, 16)[1] is False
        print("SELFTEST OK")
        return 0

    validator, deployed = setup()
    if not check_initial(deployed):
        print("INITIAL BOARD MISMATCH - aborting", flush=True)
        return 1

    rng = random.Random(args.seed)
    results = {"agreements": 0, "divergences": [], "boards": {}, "finding": None,
               "accepted": 0, "reverted": 0}
    for name, (addr, kind) in deployed.items():
        if results["finding"]:
            print("stopping early at first finding", flush=True)
            break
        diff_one(name, addr, kind, args.moves, rng, results)
        print("%-14s %d moves: %d agreements, %d divergences (accepted=%d reverted=%d)" % (
            name, args.moves, results["agreements"], len(results["divergences"]),
            results["accepted"], results["reverted"]), flush=True)

    if results["finding"]:
        print("FINDING:", json.dumps(results["finding"]), flush=True)
        return 2
    print("NO DIVERGENCE over %d comparisons across all games" % results["agreements"], flush=True)
    print("DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
