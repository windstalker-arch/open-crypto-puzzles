#!/usr/bin/env python3
"""Fast, bounded LSB scan for Arweave Puzzle #11.

A private key is exactly 256 bits. For each (channel, bit-read), the meaningful
candidate is the FIRST 256 bits of the extracted bitstream (standard stego: payload
at start, rest of image is carrier). So each config yields a single 32-byte key.
Scan is small and fast.
"""
from PIL import Image
import numpy as np
from eth_keys import keys

TARGET = "0xff2142e98e09b5344994f9beb9c56c95506b9f17"
PREFIX = "ff21"

im = Image.open("clues/arweave-puzzle-11.png")
arr = np.array(im)
G = arr[..., 0].astype(np.uint32)
A = arr[..., 1].astype(np.uint32)

SCALAR = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def ck(privbytes, label):
    if len(privbytes) < 32:
        return None
    p = int.from_bytes(privbytes, "big")
    if p == 0 or p >= SCALAR:
        return None
    a = keys.PrivateKey(privbytes).public_key.to_checksum_address().lower()
    if a.endswith(a) and a.startswith("0x" + PREFIX):
        return a
    return None


def scan_plane(plane, name, maxbw=8, rasters=("raster", "col")):
    hits = 0
    if rasters == "raster" or "raster" in rasters:
        flat = plane.flatten()
    else:
        flat = plane.T.flatten()
    for bw in range(1, maxbw + 1):
        mask = (1 << bw) - 1
        v = flat & mask
        # need 256 bits = 32 bytes. Collect 32*8/bw pixels worth = 256/bw pixels.
        need = (256 + bw - 1) // bw
        for lsb_first in (True, False):
            bits = []
            cnt = 0
            for x in v[:need]:
                for k in range(bw):
                    sh = k if lsb_first else (bw - 1 - k)
                    bits.append((x >> sh) & 1)
                cnt += 1
                if len(bits) >= 256:
                    break
            bits = bits[:256]
            while len(bits) % 8:
                bits.append(0)
            data = bytes(int("".join(str(b) for b in bits[i:i+8]), 2) for i in range(0, len(bits), 8))
            a = ck(data, f"{name} bw={bw} lsb_first={lsb_first}")
            if a:
                print("HIT", name, bw, lsb_first, a, data.hex())
                hits += 1
            # also try MSB-first reading of the 8-bit grayscale bytes directly (bit plane 7 first)
    return hits


def main():
    total = 0
    for ch, name in ((G, "GRAY"), (A, "ALPHA")):
        for raster in ("raster", "col"):
            total += scan_plane(ch, f"{name}-{raster}", maxbw=4 if ch is A else 8, rasters=(raster,))
    print("scan done; hits =", total)


if __name__ == "__main__":
    main()
