#!/usr/bin/env python3
"""SSKR minimum-length encode check: each byte byteword written as its unique
first-3 (or first-2) letters, concatenated with no separators.  If any decoded
puzzle stream is an SSKR share in min-form, greedy segmentation must land only
on valid 2/3-letter prefixes of the 256 word dictionary."""
import json
import os

def load_words(path):
    with open(path) as fh:
        words = fh.read().split()
    assert len(words) == 256
    pref3 = {}
    for i, w in enumerate(words):
        p = w[:3]
        assert p not in pref3, p
        pref3[p] = i
    pref2 = {}
    for i, w in enumerate(words):
        p = w[:2]
        pref2.setdefault(p, set()).add(i)
    return words, pref3, pref2

def greedy(s, L, pref3, pref2):
    out = []
    i = 0
    n = len(s)
    while i < n:
        if i + L <= n:
            chunk = s[i:i + L]
            if chunk in pref3:
                out.append((chunk, L))
                i += L
                continue
        tryextra = False
        while L > 2:
            L -= 1
            if i + L <= n and s[i:i + L] in pref3:
                out.append((s[i:i + L], L))
                i += L
                tryextra = True
                break
        if tryextra:
            continue
        return None, i
    return out, n

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    words, pref3, pref2 = load_words("/data/data/com.termux/files/usr/tmp/opencode/sskr_words.txt")
    print("%d words, %d unique 3-char prefixes" % (len(words), len(pref3)))

    streams = {}
    for name in ("faed_bifid570", "even_stream", "odd_pre_reduction", "object_256", "dropped_29"):
        p = "/data/data/com.termux/files/usr/tmp/opencode/%s.txt" % name
        if os.path.exists(p):
            streams[name] = open(p).read().strip()
    d = json.load(open(os.path.join(here, "..", "data", "finalpage-digit-streams.json")))
    streams["dbbib69"] = d["dbbib"]
    streams["dbbib91"] = d["dbbib_91"]
    streams["faed570"] = d["faed_570"].rstrip("z")
    streams["zseg1"] = d["z_segment_1"]
    streams["zseg2"] = d["z_segment_2"]

    for name, s in streams.items():
        for L in (3, 4):
            seg, stop = greedy(s, L, pref3, pref2)
            if seg is not None:
                seg3 = sum(1 for _, l in seg if l == 3)
                # report byte values
                vals = [(pref3[c], l) for c, l in seg]
                raw = bytes(v for v, _ in vals)
                tail = raw.hex()[:32]
                print("%-12s L=%d: SEGMENTS to %d words (full-3=%d), stop=%d, bytes head=%s"
                      % (name, L, len(vals), seg3, stop, tail))
                # SSKR share = meta(5)+value+crc(4); check crc on interior windows
                import binascii
                for split in (5, 0):
                    for vlen in (16, 20, 24, 32):
                        if vlen + 4 + split <= len(raw):
                            crc = binascii.crc32(raw[split:split + vlen]) & 0xffffffff
                            have = raw[split + vlen:split + vlen + 4]
                            if int.from_bytes(have, "big") == crc:
                                print("   -> CRC MATCH at split=%d vlen=%d meta=%s" %
                                      (split, vlen, raw[:split].hex()))
            else:
                print("%-12s L=%d: STALLS at %d+%d" % (name, L, stop, len(s)))

if __name__ == "__main__":
    main()