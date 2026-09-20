import hashlib, itertools, secrets
try:
    import coincurve
except Exception:
    coincurve = None

S4 = bytes.fromhex("42f5f4b7cbf78cf078a24a6ca7179b462eac13504c9791c8f1192ef8a7a352a4ef756397ea74234a97a95f01ae37f8c9")
G1617 = bytes.fromhex("3be6ecf1d5c126e50f25ded3bc8fb6d9")
FH = bytes.fromhex("8048c428a6faf6d3df77db13ca68766d")

GATE1_H160 = "a9553269572a317e39f0f518cb87c1a0ee1dbae4"
GATE2_H160 = "4bc468447fe1b048ad030a2f9a125478eabc4ed6"

assert len(S4) == 48 and len(G1617) == 16 and len(FH) == 16

def ripemd160(b):
    h = hashlib.new("ripemd160")
    h.update(b)
    return h.digest()

def pubkey_h160(pub):
    return ripemd160(hashlib.sha256(pub).digest())

KEYN = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def check(candidate_bh):
    joins = {
        "FH||BH": FH + candidate_bh,
        "BH||FH": candidate_bh + FH,
        "FH^BH": bytes(a ^ b for a, b in zip(FH, candidate_bh)),
        "BH^FH": bytes(a ^ b for a, b in zip(candidate_bh, FH)),
    }
    hits = []
    for name, key in joins.items():
        k = int.from_bytes(key, "big")
        if not (0 < k < KEYN):
            continue
        if coincurve is None:
            continue
        pub = coincurve.PublicKey.from_valid_secret(k.to_bytes(32, "big")).format(compressed=True)
        h = pubkey_h160(pub).hex()
        if h == GATE1_H160 or h == GATE2_H160:
            hits.append((name, key.hex()))
    return hits

def reductions():
    cands = set()
    for i in range(0, 33):
        cands.add(bytes(S4[i:i+16]))
    for step in range(1, 49):
        for i in range(0, 48 - 16 * step + 1, step):
            cands.add(bytes(S4[i:i + 16 * step:step]))
    pairs = [bytes(S4[i] ^ S4[j] for _ in range(0, 0))]  # placeholder no-op
    for i in range(0, 24):
        for j in range(i + 1, 24):
            b = bytes(S4[2*i] ^ S4[2*j] for _ in [0]) * 16
            cands.add(b)
    for a in range(0, 24):
        for b in range(24):
            v = S4[2*a] ^ S4[2*b]
            cands.add(bytes([v] * 16))
    tri = [S4[i] ^ S4[i+24] for i in range(24)]
    cands.add(bytes(tri[:16]))
    cands.add(bytes(tri[8:24]))
    diffs = bytes((S4[i] - S4[i+1]) & 0xFF for i in range(32))
    cands.add(diffs[:16]); cands.add(diffs[16:32])
    csums = bytes((S4[i] + S4[i+16] + S4[i+32]) & 0xFF for i in range(16))
    cands.add(csums)
    csums2 = bytes((S4[i] ^ S4[i+16] ^ S4[i+32]) for i in range(16))
    cands.add(csums2)
    for half in (S4[:24], S4[24:], S4[::2], S4[1::2]):
        if len(half) >= 16:
            cands.add(half[:16]); cands.add(bytes(half[8:24]) if len(half) >= 24 else half[:16])
    xor3 = bytes(S4[i] ^ S4[i+16] ^ S4[i+32] for i in range(16))
    cands.add(xor3)
    h = hashlib.sha256(S4).digest()
    cands.add(h[:16]); cands.add(h[16:32])
    cands.add(hashlib.md5(S4).digest())
    cands.add(hashlib.sha1(S4).digest()[:16])
    m = hashlib.sha256(S4[:24]).digest()[:16]
    cands.add(m)
    m2 = hashlib.sha256(S4[24:]).digest()[:16]
    cands.add(m2)
    xn = bytes((S4[i] ^ S4[47 - i]) for i in range(24))[:16]
    cands.add(xn)
    step2 = bytes(S4[i] for i in range(0, 48, 3))[:16]
    cands.add(step2)
    step23 = bytes(S4[i] for i in range(0, 48, 3))[16:32]
    cands.add(step23)
    black, white = S4[::2], S4[1::2]
    cands.add(bytes((black[i] ^ white[i]) for i in range(16)))
    return cands

def bh_for(r16):
    return bytes(a ^ b for a, b in zip(r16, G1617))

def main():
    cands = reductions()
    print(f"reduction primitives: {len(cands)}")
    seen = set()
    hits = []
    n = 0
    seed = secrets.token_bytes(32)
    for r16 in cands:
        bh = bh_for(r16)
        h = check(bh)
        n += 1
        if h:
            hits.append((r16.hex(), bh.hex(), h))
    variants = set()
    for r16 in cands:
        variants.add(r16)
        variants.add(r16[::-1])
    for r16 in variants:
        bh = bh_for(r16)
        for name, key in {
            "FH||BH": FH + bh, "BH||FH": bh + FH,
            "FH^BH": bytes(a ^ b for a, b in zip(FH, bh)),
            "BH^FH": bytes(a ^ b for a, b in zip(bh, FH)),
        }.items():
            k = int.from_bytes(key, "big")
            if not (0 < k < KEYN) or coincurve is None:
                continue
            try:
                pub = coincurve.PublicKey.from_valid_secret(k.to_bytes(32, "big")).format(compressed=True)
            except Exception:
                continue
            h = pubkey_h160(pub).hex()
            if h in (GATE1_H160, GATE2_H160):
                hits.append((r16.hex(), bh.hex(), (name, key.hex())))
    if not hits:
        print("0 MATCH on both funded gates (gate-h160 check); BH candidates:", n)
    else:
        for x in hits[:20]:
            print("HIT", x)
    return hits

if __name__ == "__main__":
    main()