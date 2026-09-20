#!/usr/bin/env python3
"""Two-blob mirror battery for the GSMG.io 5-BTC puzzle.

Now that BOTH 79-byte chain blobs are recovered on disk,

  B1 = K_C1(32) || K_C2(32) || E_C(15)   (sha256 1449a217...)
  B2 = K_S1(32) || K_S2(32) || E_S(15)   (sha256 b40fce72...)

everything below is fully executable. This tests the hypothesis that the
two blobs form a mirror 2x2 MATRIX of 32-byte keys,

           col A       col B
  row C    K_C1        K_C2
  row S    K_S1        K_S2

and that the gate private key k (with k*G == X = f4d1bbd91e65e2a019566a17574e9
7dae908b784b388891848007e4f55d5a464, odd y, == small-gate h160 a9553269... and
the Dualite-gate h160 4bc46844...) is produced by SUMming the matrix /
list of its rows and columns, or by other closed-form two-blob combinations.

A candidate scalar is a SOLUTION iff k*G == X exactly (both x and y bytes).
That is the certified answer test used by the corrected oracles.

Battery sections (all new, not in late-59 / tested.md):
  A. 2x2 matrixsumlist: row/col/diag/total SUMs mod n, XORs, directed diffs,
     bytewise mod-256 sums/XORs of the four keys.
  B. pointer-add subset sums: X == +/-P1 +/-P2 +/-Q1 +/-Q2 (3^4 = 81).
  C. concat readings of B1||B2 / B2||B1 and key-pair concatenations.
  D. tails E_C vs E_S: xor/sum-mod-256/30B-concat/chain4-pw-32B-as-scalar.
  E. cyclic-extension matrixsumlist over each 79B block and the 158B concats
     (shapes area = 79*k, k=1..8): rowsums/colsums/secondary -> sha256 scalar.
  F. hex-string / digest-slug forms -> corrected oracles (small + dualite),
     deduped by the persistent gsmg_uniq.fbf1 bloom.

No loop runs longer than seconds; N,D,t printed per loop per AGENTS.md.
"""
from __future__ import annotations
import os

import hashlib
import itertools
import sys
import time
from pathlib import Path

import coincurve

FOLDER = Path(__file__).resolve().parent.parent
DATA = FOLDER / "data"
B1 = (DATA / "B1_79.bin").read_bytes()
B2 = (DATA / "B2_79.bin").read_bytes()

# B2 redrived from the issue-#22 base64 (cross-check against on-disk file):
import base64  # noqa: E402
_B2B64 = (
    "U2FsdGVkX1+0Wl49gnWTyiimluu7V3+vl7st0gUt9sWDzNLxDmlPMsDSiuW2a46zg"
    "KlIi8aaqY5gpJPPEzW1n9n3/26qs4zstWtPKF8Zs/BTNN4IiEh4qu18mdC0NAv4"
)
_raw2 = base64.b64decode(_B2B64)
_salt2, _ct2 = _raw2[8:16], _raw2[16:]

X = int("f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464", 16)
Y_expect = 0x9c73D25FC5ED8FD7227CAB0BE4E576C0C6404DB5AA546286563E4BE12BF33559
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F  # field prime
G = coincurve.PublicKey.from_valid_secret((1).to_bytes(32, "big"))

K_C1 = B1[0:32]
K_C2 = B1[32:64]
E_C = B1[64:79]
K_S1 = B2[0:32]
K_S2 = B2[32:64]
E_S = B2[64:79]

CHAIN4_PW = bytes.fromhex(
    "38d4f4c90cb45fdfc8cff50d0ed1c5740a25de4b8e946d0a5ae2667a23a259cc"
)  # = E_C || E_S || E_B[:2]

KEYS = {"K_C1": K_C1, "K_C2": K_C2, "K_S1": K_S1, "K_S2": K_S2}
E_TAILS = {"E_C": E_C, "E_S": E_S}

SLUGS7 = {
    "0b0f37ec", "10d6a2c5", "673e3b1a", "a2aefdbb",
    "aca20ae7", "c2eef34b", "f9719d6d",
}


def sha256b(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


B58A = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58check(prefix: bytes, payload: bytes) -> str:
    raw = prefix + payload
    cs = hashlib.sha256(hashlib.sha256(raw).digest()).digest()[:4]
    n = int.from_bytes(raw + cs, "big")
    o = ""
    while n > 0:
        n, r = divmod(n, 58)
        o = B58A[r] + o
    return "1" * (len(raw + cs) - len((raw + cs).lstrip(b"\x00"))) + o


def address_of(point: tuple[int, int]) -> str:
    x, y = point
    fmt = b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")
    h = hashlib.new("ripemd160", sha256b(fmt)).digest()
    return b58check(b"\x00", h)


def i2b(i: int) -> bytes:
    return (i & ((1 << 256) - 1)).to_bytes(32, "big")


def b2i(b: bytes) -> int:
    return int.from_bytes(b, "big")


def evidence() -> bool:
    """Witnesses: B1/B2 hashes, WIF, ECC identity, gate-1 certification."""
    ok = True
    h1 = hashlib.sha256(B1).hexdigest()
    h2 = hashlib.sha256(B2).hexdigest()
    assert h1 == "1449a2178eea7c0e3fabac8c1ad2afa294be4fc1800c594a025a056e88c626bf", h1
    assert h2 == "b40fce72ef5638e4f79b3233e653f8a5dbdb0d4ae2009d2d3da2c98b70f4d004", h2
    print(f"  B1 79B sha256={h1}")
    print(f"  B2 79B sha256={h2}")
    # WIF(K_C1) == the chain-2 password
    wif = b58check(b"\x80", K_C1)
    print(f"  WIF(K_C1)={wif}")
    assert wif == "5K2byJMssxFKuTgnk9YQjpBz5FhkwwF2LaZoAyTus8HjGEpz8AT", wif
    # ECC identity + gate certification: P_C1 = K_C1*G
    p_c1 = coincurve.PublicKey.from_valid_secret(K_C1)
    print(f"  K_C1*G x={p_c1.x() if hasattr(p_c1,'x') else hex(p_c1.point()[0]) if hasattr(p_c1,'point') else '?'}")
    # gate-1 pubkey as a point, and verify h160
    known_pub = bytes.fromhex(
        "04f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464"
        "9c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559"
    )
    ph = hashlib.new("ripemd160", sha256b(known_pub)).digest().hex()
    print(f"  h160(gate1 known pubkey)={ph}")
    assert ph == "a9553269572a317e39f0f518cb87c1a0ee1dbae4", ph
    # sanity: (K_C1^K_S1)*G should equal P_C1+P_S1 (additive group)
    p_s1 = coincurve.PublicKey.from_valid_secret(K_S1)
    xor_g = coincurve.PublicKey.from_valid_secret(
        bytes(a ^ b for a, b in zip(K_C1, K_S1)))
    sum_g = coincurve.PublicKey.combine_keys([p_c1, p_s1])
    assert xor_g.format() != sum_g.format()  # XOR != addition, sanity of the two notions
    # POSITIVE CONTROL through the same point->address path as point_is_gate():
    # K_C1 * G (computed by coincurve) must reproduce K_C1's known address
    # (recorded in compressed form: pub 0293d665.., addr 14zJ3RHP...).
    x1, y1 = p_c1.point()
    h1 = hashlib.new("ripemd160", sha256b(p_c1.format())).digest()
    addr_c = b58check(b"\x00", h1)
    addr_u = address_of(p_c1.point())
    print(f"  K_C1*G comp -> {addr_c}")
    print(f"  K_C1*G uncomp -> {addr_u}")
    assert addr_c == "14zJ3RHPxiRJAmYHUNTvPoCTxhFB6gACgf", addr_c
    print("  evidence OK")
    return ok


def point_is_gate(pub: coincurve.PublicKey) -> int:
    """0 not-gate; 1 == gate-1 X (odd y); 2 == gate-2 address h160."""
    try:
        x, y = pub.point()
    except Exception:
        return 0
    if x == X and pub.point()[1] == Y_expect:
        return 1
    for fmt in (pub.format(), b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")):
        h = hashlib.new("ripemd160", sha256b(fmt)).digest().hex()
        if h in ("a9553269572a317e39f0f518cb87c1a0ee1dbae4",
                 "4bc468447fe1b048ad030a2f9a125478eabc4ed6"):
            return 2
    return 0


def scan_scalars(name_prefix: str, scalars: list[tuple[str, bytes]]) -> list[str]:
    """Point-check each scalar k (as bytes) against the gate. Returns matches."""
    hits = []
    for name, kb in scalars:
        try:
            pub = coincurve.PublicKey.from_valid_secret(i2b(b2i(kb) % N))
        except Exception:
            continue
        r = point_is_gate(pub)
        if r:
            hits.append(f"{name_prefix}:{name}:gate{r}")
    return hits


def bat_a() -> list[tuple[str, bytes]]:
    """2x2 matrixsumlist  -  row/col/diag/total sums (== X?) over the 4 keys."""
    out: list[tuple[str, bytes]] = []
    rows = {"rC": (K_C1, K_C2), "rS": (K_S1, K_S2)}
    cols = {"c1": (K_C1, K_S1), "c2": (K_C2, K_S2)}
    # sums and XORs
    for name, (a, b) in {**rows, **cols}.items():
        out.append((f"sum_{name}", i2b((b2i(a) + b2i(b)) % N)))
        out.append((f"xor_{name}", bytes(x ^ y for x, y in zip(a, b))))
        out.append((f"sum256_{name}", bytes((x + y) & 0xFF for x, y in zip(a, b))))
        out.append((f"diff_{name}", i2b((b2i(a) - b2i(b)) % N)))
    # diagonals
    out.append(("sum_diag1", i2b((b2i(K_C1) + b2i(K_S2)) % N)))
    out.append(("sum_diag2", i2b((b2i(K_C2) + b2i(K_S1)) % N)))
    out.append(("xor_diag1", bytes(x ^ y for x, y in zip(K_C1, K_S2))))
    out.append(("xor_diag2", bytes(x ^ y for x, y in zip(K_C2, K_S1))))
    # total
    tot = sum(b2i(k) for k in KEYS.values())
    out.append(("sum_total", i2b(tot % N)))
    allx = K_C1
    for k in (K_C2, K_S1, K_S2):
        allx = bytes(x ^ y for x, y in zip(allx, k))
    out.append(("xor_total", allx))
    # bytewise mod-256 total
    totm = bytes((K_C1[i] + K_C2[i] + K_S1[i] + K_S2[i]) & 0xFF for i in range(32))
    out.append(("sum256_total", totm))
    return out


def bat_b():
    """Point-addition subset sums: X == +/-P_C1 +/-P_C2 +/-P_S1 +/-P_S2."""
    hits, count = [], 0
    pts = [coincurve.PublicKey.from_valid_secret(k) for k in KEYS.values()]
    names = list(KEYS.keys())
    points_x_y = []
    for p in pts:
        x, y = p.point()
        points_x_y.append((x, y))
    for signs in itertools.product((1, -1, 0), repeat=4):
        # at least one nonzero
        if not any(signs):
            continue
        acc = None
        for (x, y), s in zip(points_x_y, signs):
            if s == 0:
                continue
            if s == -1:
                y = P - y if y else y  # point negation over the FIELD prime P
            pb = b"\x02" if y % 2 == 0 else b"\x03"
            pb += x.to_bytes(32, "big")
            term = coincurve.PublicKey(pb)
            acc = term if acc is None else coincurve.PublicKey.combine_keys([acc, term])
        count += 1
        if acc.point()[0] == X and acc.point()[1] == Y_expect:
            hits.append(f"bat_b:{'+'.join(str(s) + n for s, n in zip(signs, names))}:gate1")
        for fmt in (acc.format(),):
            h = hashlib.new("ripemd160", sha256b(fmt)).digest().hex()
            if h in ("a9553269572a317e39f0f518cb87c1a0ee1dbae4",
                     "4bc468447fe1b048ad030a2f9a125478eabc4ed6"):
                hits.append(f"bat_b:{'+'.join(str(s) + n for s, n in zip(signs, names))}:h160")
    return hits, count


def bat_c() -> list[tuple[str, bytes]]:
    """Concat readings over B1||B2 / B2||B1 and key-pair concats."""
    out: list[tuple[str, bytes]] = []
    B12, B21 = B1 + B2, B2 + B1
    for nm, blk in (("B1B2", B12), ("B2B1", B21)):
        out.append((f"{nm}_first32", blk[:32]))
        out.append((f"{nm}_last32", blk[-32:]))
        out.append((f"{nm}_sha256", sha256b(blk)))
    for i, j in itertools.permutations(KEYS.keys(), 2):
        out.append((f"sha_{i}_{j}", sha256b(KEYS[i] + KEYS[j])))
    order4 = ["K_C1", "K_S1", "K_C2", "K_S2"]
    kb = b"".join(KEYS[k] for k in order4)
    out.append(("sha_C1S1C2S2", sha256b(kb)))
    out.append(("sha_C1S1C2S2_first64", sha256b(kb[:64])))
    return out


def bat_d() -> list[tuple[str, bytes]]:
    """Tails E_C vs E_S interplay + the chain4 password (32B) as a scalar."""
    out: list[tuple[str, bytes]] = []
    ec, es = E_C, E_S
    out.append(("ec_xor_es", sha256b(bytes(x ^ y for x, y in zip(ec, es)))))
    out.append(("ec_add_es", sha256b(bytes((x + y) & 0xFF for x, y in zip(ec, es)))))
    out.append(("sha_ec_es", sha256b(ec + es)))
    out.append(("sha_es_ec", sha256b(es + ec)))
    out.append(("ec_es_pad_00", (ec + es + b"\x00\x00")))         # 32B scalar
    out.append(("ec_es_pad_ff", (ec + es + b"\xff\xff")))         # 32B scalar
    out.append(("chain4pw_scalar", CHAIN4_PW))                    # E_C||E_S||E_B[:2]
    out.append(("sha_chain4pw", sha256b(CHAIN4_PW)))
    out.append(("sha_ec", sha256b(ec)))
    out.append(("sha_es", sha256b(es)))
    out.append(("ec_xor_es_rev", sha256b(bytes(x ^ y for x, y in zip(ec, es[::-1])))))
    out.append(("ec_add_es_rev", sha256b(bytes((x + y) & 0xFF for x, y in zip(ec, es[::-1])))))
    return out


def bat_e() -> list[tuple[str, bytes]]:
    """Cyclic-extension matrixsumlist on each 79B and the 158B concats."""
    out: list[tuple[str, bytes]] = []
    blocks = {"B1": B1, "B2": B2, "B1B2": B1 + B2, "B2B1": B2 + B1}
    for bnm, blk in blocks.items():
        L = len(blk)
        # shapes with a*b = L*k for k = 1..8, plus 14x14 (196), 7x14 (98) mirror
        areas = sorted({L * k for k in range(1, 9)} | {196, 98, 79, 158})
        for area in areas:
            pairs = [(a, b) for a in range(1, area + 1)
                     if area % a == 0 and (b := area // a) >= 2]
            for a, b in pairs:
                # cyclic extension of blk to a*b bytes
                ext = (blk * (area // L + 2))[: area]
                rows = [ext[r * b:(r + 1) * b] for r in range(a)]
                rs = bytes(sum(row) & 0xFF for row in rows)
                cs = bytes(sum(rows[r][c] for r in range(a)) & 0xFF for c in range(b))
                sec = bytes((rs[i] + cs[(i + 7) % b]) & 0xFF for i in range(a))
                out.append((f"{bnm}_{a}x{b}_rowsums", sha256b(rs)))
                out.append((f"{bnm}_{a}x{b}_colsums", sha256b(cs)))
                out.append((f"{bnm}_{a}x{b}_rowcol", sha256b(rs + cs)))
                out.append((f"{bnm}_{a}x{b}_colrow", sha256b(cs + rs)))
                out.append((f"{bnm}_{a}x{b}_sec", sha256b(sec)))
    return out


def bat_f(scalars: list[tuple[str, bytes]]) -> None:
    """Hex-string candidates to the corrected oracles (small + dualite gates)."""
    cands: set[str] = set()
    for _, kb in scalars:
        h = kb.hex()
        cands.add(h)
        cands.add(hashlib.sha256(h.encode()).hexdigest())
    for b in (B1, B2, B1 + B2, B2 + B1, CHAIN4_PW):
        cands.add(b.hex())
        cands.add(hashlib.sha256(b).hexdigest())
    # slug check vs the 7 open slugs and vs the two prefix targets
    for c in sorted(cands):
        if c[:8] in SLUGS7:
            print(f"  !! derived hex slug {c} matches an OPEN SLUG prefix")
        if c.startswith("cd3fea3d"):
            print(f"  !! derived hex prefix cd3fea3d (cosmic_A-like): {c}")
        if c.startswith("c3b87356"):
            print(f"  !! derived hex prefix c3b87356: {c}")

    # persistent bloom dedup
    bloom = "/data/data/com.termux/files/usr/tmp/opencode/gsmg_uniq.fbf1"
    bloom_bin = (os.path.expanduser("~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle/tools/bloomfast/target/release/bloomfast"))
    import subprocess
    inp = "\n".join(sorted(cands)) + "\n"
    r = subprocess.run([bloom_bin, bloom], input=inp.encode(),
                       capture_output=True)
    new = r.stdout.decode(errors="replace").splitlines()
    print(f"  bloom: {len(cands)} candidates, {len(new)} unseen")

    if not new:
        print("  nothing unseen; oracles skipped")
        return

    for label, script in (("small", "oracle.py"), ("dualite", "oracle_dualite.py")):
        inp2 = "\n".join(new) + "\n"
        rr = subprocess.run(
            [sys.executable, str(FOLDER / "tools" / script), "--stdin"],
            input=inp2, capture_output=True, text=True, timeout=600)
        print(f"  oracle {label}: rc={rr.returncode} (0 == a MATCH was printed)")
        hits = [l for l in rr.stdout.splitlines() if l.strip() and l.strip() != "NO MATCH"]
        for l in hits:
            print(f"    {l}")


def main() -> int:
    t0 = time.time()
    print(f"[mirror79] B1={B1.hex()[:16]}... B2={B2.hex()[:16]}...")
    evidence()

    buckets = {
        "A_matrixsumlist2x2": bat_a(),
        "C_concat": bat_c(),
        "D_tails": bat_d(),
        "E_matrix_cyclic": bat_e(),
    }
    all_scalars: list[tuple[str, bytes]] = []
    for name, lst in buckets.items():
        n = len(lst)
        print(f"[{name}] N={n} (points, D~2k/s, t~{n/2000:.2f}s)")
        t1 = time.time()
        hits = scan_scalars(name, lst)
        all_scalars += lst
        if hits:
            print("  HITS:", hits)
        dt = time.time() - t1
        print(f"[{name}] done in {dt:.2f}s, hits={len(hits)}")

    hits_b, n_b = bat_b()
    print(f"[B_pointer_subsets] N={n_b}, done, hits={len(hits_b)}")
    if hits_b:
        print("  HITS:", hits_b)

    total_hits = [h for h in all_scalars
                  if h[0].startswith(("sum_total", "xor_total", "sum256_total"))]
    print(f"[A] total-matrix candidates tested: {len(total_hits)} special")

    print("[F] hex-string/digest candidates -> oracles (N small):")
    bat_f(all_scalars)

    print(f"[mirror79] battery finished in {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())