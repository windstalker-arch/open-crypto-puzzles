#!/usr/bin/env python3
"""Grayscale LSB1 windowed scan for Arweave Puzzle #11 (parallel).

Extract the LSB-first single-bit plane of the grayscale channel, pack into a byte
stream, then test EVERY contiguous 32-byte window (256 bits) as a candidate private
key across all cores. Also test the MSB-first bit plane similarly.

Only a window whose derived ETH address starts with the target's 0xff21 prefix is
reported in full; a near-miss (same 4 hex digits) is reported as a near. Everything
else is consumed. Intended as an exhaustive, bounded run of the "key hidden in the
image's pixels" mechanic.
"""
import multiprocessing as mp
from PIL import Image
import numpy as np
from eth_keys import keys

TARGET = "0xff2142e98e09b5344994f9beb9c56c95506b9f17"
PREFIX = TARGET[2:6]  # ff21
SCALAR = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

im = Image.open("clues/arweave-puzzle-11.png")
G = np.array(im)[..., 0].astype(np.uint8)
flat = G.flatten()  # 1600*1105 bytes, raster row-major


def make_stream(msb_first):
    bits = np.zeros(len(flat), dtype=np.uint8)
    if msb_first:
        bits = ((flat >> 7) & 1)
    else:
        bits = (flat & 1)
    # pack into bytes (MSB-first within each byte)
    out = bytearray()
    for i in range(0, len(bits), 8):
        b = 0
        for k in range(8):
            b = (b << 1) | int(bits[i + k])
        out.append(b)
    return bytes(out)


def worker(args):
    data, start, end, msb = args
    # each window is data[start:start+32]
    local_hits = []
    for off in range(start, end):
        w = data[off:off + 32]
        if len(w) < 32:
            break
        p = int.from_bytes(w, "big")
        if p == 0 or p >= SCALAR:
            continue
        a = keys.PrivateKey(w).public_key.to_checksum_address().lower()
        if a.startswith("0x" + PREFIX):
            local_hits.append((off, a, w.hex()))
    return local_hits


def run(msb_first):
    data = make_stream(msb_first)
    n = len(data) - 32 + 1
    print(f"msb_first={msb_first}: stream {len(data)} bytes, {n} windows", flush=True)
    cores = mp.cpu_count()
    chunk = (n + cores - 1) // cores
    ranges = []
    for i in range(cores):
        s = i * chunk
        e = min(s + chunk, n)
        if s < e:
            ranges.append((data, s, e, msb_first))
    with mp.Pool(cores) as pool:
        for res in pool.imap_unordered(worker, ranges):
            for off, a, hx in res:
                print(f"HIT off={off} {a} {hx}", flush=True)
    print(f"msb_first={msb_first} done", flush=True)


if __name__ == "__main__":
    run(False)
    run(True)
