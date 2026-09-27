#!/usr/bin/env python3
"""
registry_flow.py -- run the BountyRegistry's real lock->claim payment flow on a
local anvil node and confirm: claim pays the caller exactly the prize, closes the
challenge, cannot double-pay, cannot claim without a lock, and cannot claim an
unsolved challenge. This is the on-chain confirmation of the CEI audit for Lead 4.
"""
import json
import os
import sys
import time
import urllib.request

FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOUNTIFUL = "/data/data/com.termux/files/usr/tmp/opencode/bountiful"
OUT = os.path.join(BOUNTIFUL, "contracts", "out")
RPC = os.environ.get("ANVIL_RPC", "http://127.0.0.1:8545")
FROM = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
PRETEND_DIR = "/data/data/com.termux/files/usr/tmp/opencode"
WEI = 10**18

SEL = {
    "lock": "0xf435f5a7",              # lock(address)
    "isLocked": "0x4a4fbeec",          # isLocked(address)
    "register": "0xe8317be0",          # registerChallenge(address,uint128)
    "isOpen": "0x6a520bd5",            # isOpenChallenge(address)
    "claim": "0x1e83409a",             # claim(address)
    "fund": "0xb60d4288",              # fund()
    "getBalance": "0x12065fe0",        # getBalance()
    "getPrize": "0x8c0d6cdc",          # getPrizeAmount(address)
    "isSolved": "0x64d98f6e",          # isSolved()
}


def rpc(method, params):
    p = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=p, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            b = json.loads(r.read().decode())
    except Exception as e:
        raise RuntimeError("rpc %s failed: %s" % (method, e))
    if "error" in b:
        raise RuntimeError(b["error"])
    return b["result"]


def deploy(binpath, args_hex_wo0x="", value=0):
    init = open(binpath).read().strip()
    if init.startswith("0x"):
        init = init[2:]
    tx = rpc("eth_sendTransaction", [{"from": FROM, "data": "0x" + init + args_hex_wo0x, "value": hex(value)}])
    for _ in range(200):
        rec = rpc("eth_getTransactionReceipt", [tx])
        if rec and rec.get("contractAddress"):
            return rec["contractAddress"]
        time.sleep(0.05)
    raise RuntimeError("deploy %s returned no address" % binpath)


def send(to, data, value=0, from_=FROM):
    tx = rpc("eth_sendTransaction", [{"from": from_, "to": to, "data": data, "value": hex(value)}])
    for _ in range(200):
        rec = rpc("eth_getTransactionReceipt", [tx])
        if rec:
            return int(rec["status"], 16) == 1, rec
        time.sleep(0.02)
    raise RuntimeError("tx never mined")


def view(to, data):
    return rpc("eth_call", [{"to": to, "data": data}, "latest"])


def a_uint(v, w=64):
    return "%0*x" % (w, v)


def a_addr(a):
    return a[2:].lower().rjust(64, "0")


def bal(addr):
    return int(rpc("eth_getBalance", [addr, "latest"]), 16)


def main():
    print("selectors:", SEL, flush=True)
    admin = FROM
    deposit = int(0.01 * WEI)
    prize = int(0.25 * WEI)

    reg = deploy(os.path.join(OUT, "BountyRegistry.bin"), a_addr(admin) + a_uint(deposit))
    print("BountyRegistry @", reg, flush=True)
    game_yes = deploy(os.path.join(OUT, "DummyGame.bin"), a_uint(1), value=0)
    game_no = deploy(os.path.join(OUT, "DummyGame.bin"), a_uint(0), value=0)
    print("DummyGame(solved) @", game_yes, " DummyGame(unsolved) @", game_no, flush=True)

    # Fund registry
    ok, _ = send(reg, SEL["fund"], value=int(1 * WEI))
    print("fund ok=", ok, " balance=", int(view(reg, SEL["getBalance"]), 16) // WEI, "ETH", flush=True)

    # Register solved + unsolved challenges
    ok, _ = send(reg, SEL["register"] + a_addr(game_yes) + a_uint(prize))
    ok2, _ = send(reg, SEL["register"] + a_addr(game_no) + a_uint(prize))
    print("register solved ok=", ok, " unsolved ok=", ok2, flush=True)
    print("prize game_yes=", int(view(reg, SEL["getPrize"] + a_addr(game_yes)), 16) // WEI, "ETH", flush=True)

    # negative: claim without lock must revert
    ok, _ = send(reg, SEL["claim"] + a_addr(game_yes))
    print("claim-without-lock ok (want False)=", ok, flush=True)

    # lock the solved challenge
    ok, _ = send(reg, SEL["lock"] + a_addr(game_yes), value=deposit)
    print("lock solved ok=", ok, " isLocked=", int(view(reg, SEL["isLocked"] + a_addr(game_yes)), 16), flush=True)

    # claim -> should pay prize to caller (same as admin here), close challenge
    bal_before = bal(FROM)
    ok, _ = send(reg, SEL["claim"] + a_addr(game_yes))
    bal_after = bal(FROM)
    print("claim ok=", ok, flush=True)
    print("caller delta (excl gas, want ~+%.2f ETH): %+.6f ETH" % (prize / WEI, (bal_after - bal_before) / WEI), flush=True)
    print("challenge open after claim (want 0)=", int(view(reg, SEL["isOpen"] + a_addr(game_yes)), 16), flush=True)
    print("registry balance after claim (want ~%.2f ETH)" % ((1 - 0.25) / WEI) + "=", int(view(reg, SEL["getBalance"]), 16) // WEI, "ETH", flush=True)

    # double claim must revert (challenge now closed)
    ok, _ = send(reg, SEL["claim"] + a_addr(game_yes))
    print("double-claim ok (want False)=", ok, flush=True)

    # unsolved challenge: lock then claim must revert
    send(reg, SEL["lock"] + a_addr(game_no), value=deposit)
    ok, _ = send(reg, SEL["claim"] + a_addr(game_no))
    print("claim-unsolved ok (want False)=", ok, flush=True)

    print("\nDONE", flush=True)


if __name__ == "__main__":
    main()
