#!/usr/bin/env python3
"""
calldata_probe.py -- send malformed / raw calldata at the 7 deployed game
contracts (running on a local anvil chain) and check whether any call:

  (a) makes isSolved() return true from the UNSOLVABLE_BOARD start, or
  (b) mutates the board at all (a decoder miscompilation that accepts an
      illegal/unpacked index would corrupt the 4-bit packed cells).

This is the mechanical core of the malformed-calldata surface the puzzle
README flags ("an exploit may use raw calldata") and the surface the authors'
own ExploitSearch.t.sol only samples (a handful of dirty-high-bit indexes on
moveField). We probe far wider argument encodings and selector layouts.

Usage (from the puzzle folder, while `anvil` runs on :8545):
    python3 tools/calldata_probe.py
"""
import argparse
import json
import os
import random
import sys
import time
import urllib.request

FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOUNTIFUL = "/data/data/com.termux/files/usr/tmp/opencode/bountiful"
OUT = os.path.join(BOUNTIFUL, "contracts", "out")

RPC = os.environ.get("ANVIL_RPC", "http://127.0.0.1:8545")
FROM = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
UNSOLVABLE_BOARD = 0x0EFDCBA987654321
SOLVED = 0x0FEDCBA987654321

GAMES_1D = ["Game", "GameEnum", "GameBitboard", "GameMonadic", "GameNested", "GameTrait"]
GAME_2D = "Game2D"

SELECTORS = {
    "getBoard1": "0x45e09e54",
    "getBoard2": "0x58e4f026",
    "moveField1": "0x8bf02f32",   # moveField(uint256)
    "moveField2": "0xc069fdaa",   # moveField(uint256,uint256)
    "isSolved": "0x64d98f6e",
}


def rpc(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode())
    if "error" in body:
        raise RuntimeError(body["error"])
    return body["result"]


def deploy(binpath, args_hex_wo0x):
    with open(binpath) as f:
        init = f.read().strip()
        if init.startswith("0x"):
            init = init[2:]
    data = "0x" + init + args_hex_wo0x
    txhash = rpc("eth_sendTransaction", [{"from": FROM, "data": data}])
    addr = None
    for _ in range(200):
        rec = rpc("eth_getTransactionReceipt", [txhash])
        if rec and rec.get("contractAddress"):
            addr = rec["contractAddress"]
            break
        time.sleep(0.05)
    if not addr:
        raise RuntimeError("deploy failed for %s" % binpath)
    return addr


def abi_addr(a):
    return a[2:].lower().rjust(64, "0")


def abi_bool(b):
    return ("%064x" % (1 if b else 0))


def abi_uint(v, width=64):
    return ("%0*x" % (width, v))


def call_raw(to, calldata):
    """Send raw calldata (eth_sendTransaction). Return True if it mined without reverting."""
    # Normalize to even-length hex (right-pad with 0) so odd-length generator
    # artifacts can't crash anvil; semantic short/truncated calldata is preserved.
    if len(calldata) % 2 == 1:
        calldata += "0"
    txhash = rpc("eth_sendTransaction", [{"from": FROM, "to": to, "data": calldata}])
    for _ in range(200):
        rec = rpc("eth_getTransactionReceipt", [txhash])
        if rec:
            return int(rec["status"], 16) == 1
        time.sleep(0.02)
    raise RuntimeError("tx never mined")


def call_read(to, data):
    out = rpc("eth_call", [{"to": to, "data": data}, "latest"])
    return int(out, 16)


def read_board(addr, two):
    b = 0
    if two:
        for i in range(16):
            v = call_read(addr, SELECTORS["getBoard2"] + abi_uint(i // 4) + abi_uint(i % 4))
            b |= v << (4 * i)
    else:
        for i in range(16):
            v = call_read(addr, SELECTORS["getBoard1"] + abi_uint(i))
            b |= v << (4 * i)
    return b


def read_solved(addr):
    return call_read(addr, SELECTORS["isSolved"]) == 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fuzz", type=int, default=0,
                        help="number of random malformed calldata blobs to throw per game")
    parser.add_argument("--seed", type=int, default=1234)
    args = parser.parse_args()
    rng = random.Random(args.seed)

    # deploy validator(false) + games
    validator = deploy(os.path.join(OUT, "DummyLockValidator.bin"), abi_bool(False))
    print("DummyLockValidator(false) @", validator, flush=True)
    addrs = {}
    for name in GAMES_1D:
        addrs[name] = deploy(os.path.join(OUT, name + ".bin"), abi_addr(validator) + abi_uint(UNSOLVABLE_BOARD))
        print("deployed %-10s @ %s" % (name, addrs[name]), flush=True)
    addrs[GAME_2D] = deploy(os.path.join(OUT, GAME_2D + ".bin"), abi_addr(validator) + abi_uint(UNSOLVABLE_BOARD))
    print("deployed %-10s @ %s" % (GAME_2D, addrs[GAME_2D]), flush=True)

    mf1 = SELECTORS["moveField1"]
    mf2 = SELECTORS["moveField2"]

    # ---- malformed calldata variants ------------------------------------
    # Each is (label, calldata) applied to the moveField selector of 1-d games.
    enc32 = abi_uint
    probes = []
    tags = []

    # (1) A big batch of dirty-high-bit indexes (numeric value >15 but low nibble legal).
    #     Legal neighbors of empty (cell 15) are 11 and 14. Try aliases of both.
    for lo in (11, 14):
        for hi in (0x10, 0x100, 1 << 8, 1 << 16, 1 << 32, 1 << 64, 1 << 128, 1 << 192,
                   0xFFFFFFFFFFFFFFFF, 0xF00000000000000F):
            v = hi | lo
            probes.append(abi_uint(v))
            tags.append("dirty-hi low=%d hi=%#x" % (lo, hi))
            # truncated encodings of the same value (8/16/24 bytes)
            for w in (8, 16, 24):
                probes.append(abi_uint(v % (1 << (w * 4)), width=w))
                tags.append("dirty-trunc w=%d low=%d" % (w, lo))

    # (2) argument encoded as fewer bytes (uint8/uint16/uint32 style), no padding
    for w in (2, 4, 8, 16):
        probes.append(abi_uint(11, width=w))
        tags.append("uint%dbits index=11" % (w * 4))

    # (3) extra trailing bytes appended after the 32-byte arg
    probes.append(abi_uint(11) + "00")            ; tags.append("trailing 1 byte")
    probes.append(abi_uint(11) + "00000000")      ; tags.append("trailing 4 bytes")
    probes.append(abi_uint(11) + "ab" * 32)       ; tags.append("trailing 32 bytes")

    # (4) truncated calldata (selector only, selector+partial arg)
    probes.append("")                             ; tags.append("empty (selector-only)")
    probes.append(abi_uint(11)[:32])              ; tags.append("half arg")
    probes.append(abi_uint(11)[:48])              ; tags.append("3/4 arg")

    # (5) two 32-byte args to the 1-arg function (extra ignored or misdecoded?)
    probes.append(abi_uint(11) + abi_uint(14))    ; tags.append("two args (row,col to 1-arg)")
    probes.append(abi_uint(14) + abi_uint(11))    ; tags.append("two args swapped")

    # (6) full board / solved word as the index word
    probes.append(abi_uint(SOLVED))               ; tags.append("index=SOLVED word")
    probes.append(abi_uint(UNSOLVABLE_BOARD))     ; tags.append("index=UNSOLVABLE word")

    # (7) any value that aliases the solved board via low bits (dirty, low nibbles = 15,14,...,0)
    solved_low = 0x0FEDCBA987654321 & 0xF
    probes.append(abi_uint((1 << 64) | solved_low)); tags.append("dirty-hi low=solved-bit0")

    print("\n%d raw-calldata probes -> each 1-d game + Game2D\n" % len(probes), flush=True)

    # extra probes specific to Game2D (2-arg moveField): 1-arg, 3-arg, oversized
    g2d_probes = [
        (abi_uint(0), "2d 1-arg row"),
        (abi_uint(3, width=1) + abi_uint(3), "2d row as uint8 + col"),
        (abi_uint(3) + abi_uint(3) + abi_uint(0), "2d 3-arg"),
        (abi_uint(0, width=8)[:16], "2d truncated"),
        (abi_uint(0) + abi_uint(3) + abi_uint(9), "2d 3rd arg"),
        (abi_uint(0x1000000000000000000000000000000000000000000000000000000000000000) + abi_uint(3), "2d dirty row"),
    ]

    any_solved = False

    def try_game(name, addr, two, lbl, cd):
        nonlocal any_solved
        ok = call_raw(addr, cd)
        solved = read_solved(addr)
        if solved:
            any_solved = True
            after = read_board(addr, two)
            print("*** SOLVED EXPLOIT  %-10s probe[%s] ok=%s after=%#x" % (
                name, lbl, ok, after), flush=True)

    # 1-d games: apply every generic probe
    for name in GAMES_1D:
        addr = addrs[name]
        for cd, lbl in zip(probes, tags):
            try_game(name, addr, False, lbl, mf1 + cd)
    # Game2D: generic probes (interpreted as row=word,col?) plus dedicated 2-arg probes
    for cd, lbl in zip(probes, tags):
        try_game(GAME_2D, addrs[GAME_2D], True, "g2d:" + lbl, mf2 + cd)
    for cd, lbl in g2d_probes:
        try_game(GAME_2D, addrs[GAME_2D], True, "g2d:" + lbl, mf2 + cd)

    # bare selector invocations (whole-selector aliases / no such function)
    for sel, lbl in [("0x8bf02f32", "mf1 alone"), ("0xc069fdaa", "mf2 alone"),
                     ("0x00000000", "zero selector"), ("0xffffffff", "ff selector")]:
        for name in GAMES_1D:
            try_game(name, addrs[name], False, lbl, sel)
        try_game(GAME_2D, addrs[GAME_2D], True, lbl, sel)

    # ---- random calldata fuzz -------------------------------------------
    # Throw arbitrary byte strings (both moveField-prefixed and bare/random) at
    # the ABI decoder. This is what a decoder miscompilation would surface on:
    # a wrong decode that maps a malformed blob to a legal index and, worse,
    # to an index that walks the packed board toward the solved word.
    if args.fuzz > 0:
        print("\nfuzzing %d random calldata blobs per game..." % args.fuzz, flush=True)
        for i in range(args.fuzz):
            nbytes = rng.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 16, 31, 32, 33, 40, 64, 65])
            if rng.random() < 0.7:
                blob = "".join("%02x" % rng.getrandbits(8) for _ in range(nbytes))
            else:
                # bias a chunk toward a legal small index (low bits) to
                # exercise "dirty high bits but legal low nibble" aliasing.
                lo = rng.choice([0, 1, 11, 14, 15])
                blob = "%02x" % lo + "".join("%02x" % rng.getrandbits(8) for _ in range(max(nbytes - 1, 0)))
            for name in GAMES_1D:
                try_game(name, addrs[name], False, "fuzz%d" % i, mf1 + blob)
            try_game(GAME_2D, addrs[GAME_2D], True, "fuzz%d" % i, mf2 + blob)

    print("\nRESULT:", "EXPLOIT FOUND" if any_solved else "no solve reached over %d raw probes + %d fuzz probes" % (len(probes) + len(g2d_probes), args.fuzz * 7), flush=True)
    return 1 if any_solved else 0


if __name__ == "__main__":
    sys.exit(main())
