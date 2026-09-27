#!/usr/bin/env python3
"""Generalized windowed bit-plane scan for Arweave Puzzle #11.

For each channel (grayscale, alpha) x bitplane (0..7) x bitwidth (1,2,4) x
read-order (LSB-first/MSB-first within the pixel window), build the packed byte
stream and window-scan every 32-byte window for a private key whose derived ETH
address equals the target.

The key insight is that a 256-bit key embedded at any offset in the stream is
caught by windowing. Runs are bounded (~50s/config) and parallel across cores.
"""
import multiprocessing as mp
from PIL import Image
import numpy as np
from eth_keys import keys

TARGET = "0xff2142e98e09b5344994f9beb9c56c95506b9f17"
PREFIX = TARGET[2:6]
SCALAR = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

im = Image.open("clues/arweave-puzzle-11.png")
arr = np.array(im)
G = arr[..., 0].astype(np.uint64)
A = arr[..., 1].astype(np.uint64)
H, W = G.shape


def make_stream(plane_vals, bitplane, bitwidth, lsb_first):
    """Collect `bitwidth` bits from each pixel starting at `bitplane`, pack to bytes."""
    bits = []
    if bitwidth == 1:
        sh = bitplane
        bits = ((plane_vals >> sh) & 1).astype(np.uint8)
    else:
        mask = ((1 << bitwidth) - 1) << bitplane
        v = (plane_vals & mask) >> bitplane
        if lsb_first:
            bits = v.astype(np.uint8)  # low `bitwidth` bits LSB-first -> just value
        else:
            # reverse the low bitwidth bits
            bits = np.zeros(len(v), dtype=np.uint8)
            for k in range(bitwidth):
                bits = bits | (((v >> k) & 1) << (bitwidth - 1 - k))
    # bits is an array of uint8 (0 or 1) if bitwidth==1, else a value 0..(2^bw-1)
    # For bw==1, pack 8 bits/byte. For bw>1, pack 8 bits/byte by taking each bit.
    out = bytearray()
    if bitwidth == 1:
        for i in range(0, len(bits) - 7, 8):
            b = 0
            for k in range(8):
                b = (b << 1) | int(bits[i + k])
            out.append(b)
    else:
        # treat each bit of each value as separate, pack
        bitarr = np.zeros(len(bits) * bitwidth, dtype=np.uint8)
        for k in range(bitwidth):
            bitarr[k::bitwidth] = (bits >> k) & 1
        for i in range(0, len(bitarr) - 7, 8):
            b = 0
            for k in range(8):
                b = (b << 1) | int(bitarr[i + k])
            out.append(b)
    return bytes(out)


def worker(args):
    data, start, end = args
    local = []
    n = len(data) - 31
    for off in range(start, end):
        if off + 32 > n + 1:
            break
        w = data[off:off + 32]
        if len(w) < 32:
            break
        p = int.from_bytes(w, "big")
        if p == 0 or p >= SCALAR:
            continue
        a = keys.PrivateKey(w).public_key.to_checksum_address().lower()
        if a.startswith("0x" + PREFIX):
            local.append((off, a, w.hex()))
    return local


def run_stream(data, label):
    n = len(data) - 31
    if n <= 0:
        print(f"{label}: too short", flush=True)
        return
    cores = mp.cpu_count()
    chunk = (n + cores - 1) // cores
    ranges = []
    for i in range(cores):
        s = i * chunk
        e = min(s + chunk, n)
        if s < e:
            ranges.append((data, s, e))
    with mp.Pool(cores) as pool:
        for res in pool.imap_unordered(worker, ranges):
            for off, a, hx in res:
                print(f"HIT {label} off={off} {a} {hx}", flush=True)


def main():
    configs = []
    for ch, chname in ((G, "G"), (A, "A")):
        for plane in (0, 1, 2, 3, 4, 5, 6, 7):
            configs.append((ch, chname, plane, 1, False))
        # multi-bit low window: the natural LSB embed = low N bits of each pixel
        for bw in (2, 4, 8):
            configs.append((ch, chname, 0, bw, False))
            configs.append((ch, chname, 0, bw, True))
    for ch, chname, plane, bw, lsbf in configs:
        label = f"{chname} p{plane} bw{bw} lsbf{int(lsbf)}"
        data = make_stream(ch.flatten() if plane < 8 else ch.flatten(), plane, bw, lsbf)
        print(f"scan {label} stream={len(data)}B", flush=True)
        run_stream(data, label)
    print("ALL DOT")


if __name__ == "__main__":
    main()
