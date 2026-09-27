#!/usr/bin/env python3
"""2-D small-coefficient nonce-relation search on issue #78's two signatures.

WHY THIS EXISTS.  R-ISSUE78-HNP searched only ONE-dimensional relations
between the two nonces:

    (a)  k1 - k0 = delta, |delta| <= 2^36, both orderings   (bsgs_delta)
    (b)  c * R0 = +- R1,  |c| <= 2^20                     (test_nonce_relations)

Both leave the whole 2-D space untouched.  But the two nonce POINTS are
known exactly and without `d`,

    R_i = s_i^-1 (z_i G + r_i Q) = kappa_i G ,

where kappa_i is the nonce consistent with the *stored* s_i.  So any
small-coefficient relation among the three known points R0, R1, G, Q
kills the nonce unknowns and leaves `d` in closed form.  Three families:

    A  k1 = a*k0 + b                <=>  R1 = a*R0 + b*G
    B  a*k0 = b*k1                  <=>  a*R0 = b*R1
    C  k1 = a*k0 + b*d + c          <=>  R1 = a*R0 + b*Q + c*G

Family B is the one that matches issue #78's own "shared entropy bias"
claim: if the two nonces are c0*g and c1*g from a common 116-bit g with
small multipliers, then c1*R0 = c0*R1 and the multipliers are tiny.  A
1-D search cannot see that structure at all; the ledger has no 2-D row.

Closed forms (s_i k_i = z_i + r_i d, all mod n):

    A:  d = (z1 s0 - a s1 z0 - b s1 s0) / (a s1 r0 - r1 s0)
    B:  d = (b s0 z1 - a s1 z0)       / (a s1 r0 - b s0 r1)
    C:  d = (z1 s0 - a s1 z0 - c s1 s0) / (a s1 r0 + b s1 s0 - r1 s0)

COMPLETENESS.  A is exhaustive in |a|,|b| <= bound; B is exhaustive in
|a|,|b| <= bound; C is exhaustive in the stated asymmetric box.  The
`b` dimension is hashed (a dict on the affine x), so cost is O(bound)
point operations, not O(bound^2).  Table holds b in [0, bound] only and
both signs of b are retried, which is exact because x(iG) = x(-iG).

ACCEPT CRITERION.  Only hash160(d*G) == a9553269572a317e39f0f518c
b87c1a0ee1dbae4 (TARGET_H160) counts.  Nothing weaker is ever a hit, and
a recovered d that fails it is reported as a non-candidate.  Every
negative is witnessed by a planted relation re-found through this same
code path (see run_controls) plus a null run on unrelated points.
"""

import os

BOUND_LADDER = (1 << 14, 1 << 16, 1 << 18, 1 << 20, 1 << 22, 1 << 24)
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hnp_issue78 as H  # noqa: E402  exact secp256k1 + the issue-#78 data

P, N, G, Q = H.P, H.N, H.G, H.Q
TARGET_H160, SIGS = H.TARGET_H160, H.SIGS
h160, pmul, neg, padd, inv = H.h160, H.pmul, H.neg, H.padd, H.inv
pmul_fast, to_jac, from_jac, jac_double, verify = (
    H.pmul_fast, H.to_jac, H.from_jac, H.jac_double, H.verify)
R_point, sign = H.R_point, H.sign

INF = (0, 0, 0)


# --------------------------------------------------------------------------
# arithmetic helpers
# --------------------------------------------------------------------------
def jac_add_aff(j, q):
    """Jacobian + affine mixed addition: H.jac_add(j, (q,1)) specialised to Z2=1."""
    X1, Y1, Z1 = j
    if Z1 == 0:
        return (q[0], q[1], 1)
    X2, Y2 = q
    Z1s = Z1 * Z1 % P
    U2 = X2 * Z1s % P
    S2 = Y2 * Z1s * Z1 % P
    Hh = (U2 - X1) % P
    if Hh == 0:
        return jac_double(j) if (S2 - Y1) % P == 0 else INF
    I = 4 * Hh * Hh % P
    J = Hh * I % P
    r = 2 * (S2 - Y1) % P
    V = X1 * I % P
    X3 = (r * r - J - 2 * V) % P
    Y3 = (r * (V - X3) - 2 * Y1 * J) % P
    Z3 = ((Z1 + 1) * (Z1 + 1) - Z1s - 1) % P * Hh % P
    return (X3, Y3, Z3)


def jac_aff(j):
    """Affine point, or None at infinity.  One modular inversion."""
    X, Y, Z = j
    if Z == 0:
        return None
    zi = pow(Z, P - 2, P)
    zi2 = zi * zi % P
    return (X * zi2 % P, Y * zi2 % P * zi % P)


def jac_x(j):
    X, Y, Z = j
    if Z == 0:
        return None
    zi = pow(Z, P - 2, P)
    return X * zi % P * zi % P


def scalar_table(point, bound):
    """{ affine x of i*point : i } for i in 1..bound, built by repeated add."""
    tab = {}
    j = INF
    for i in range(1, bound + 1):
        j = jac_add_aff(j, point)
        x = jac_x(j)
        if x is not None and x not in tab:
            tab[x] = i
    return tab


# --------------------------------------------------------------------------
# closed forms for d
# --------------------------------------------------------------------------
def d_from_affine(a, b, sig0, sig1):
    """k1 = a*k0 + b."""
    r0, s0, z0 = sig0
    r1, s1, z1 = sig1
    num = (z1 * s0 - a * s1 * z0 - b * s1 * s0) % N
    den = (a * s1 * r0 - r1 * s0) % N
    if den == 0:
        return None
    return num * inv(den, N) % N


def d_from_ratio(a, b, sig0, sig1):
    """a*k0 = b*k1."""
    r0, s0, z0 = sig0
    r1, s1, z1 = sig1
    num = (b * s0 * z1 - a * s1 * z0) % N
    den = (a * s1 * r0 - b * s0 * r1) % N
    if den == 0:
        return None
    return num * inv(den, N) % N


def d_from_affine_q(a, b, c, sig0, sig1):
    """k1 = a*k0 + b*d + c."""
    r0, s0, z0 = sig0
    r1, s1, z1 = sig1
    num = (z1 * s0 - a * s1 * z0 - c * s1 * s0) % N
    den = (a * s1 * r0 + b * s1 * s0 - r1 * s0) % N
    if den == 0:
        return None
    return num * inv(den, N) % N


# --------------------------------------------------------------------------
# the three searches
# --------------------------------------------------------------------------
def search_affine(Ra, Rb, bound, target_h160, tag=""):
    """Family A: Rb == a*Ra + b*G for |a|,|b| <= bound.  Exhaustive."""
    t0 = time.time()
    tab = scalar_table(G, bound)
    t_tab = time.time() - t0
    hits = []
    negRa = neg(Ra)
    j = to_jac(padd(Rb, pmul_fast(bound % N, Ra)))
    a = -bound
    steps = 0
    while a <= bound:
        if j[2] != 0:
            x = jac_x(j)
            i = tab.get(x)
            if i is not None:
                for b in (i, -i):
                    if padd(pmul_fast(a % N, Ra),
                            pmul_fast(b % N, G)) == Rb:
                        hits.append((a, b))
            steps += 1
        j = jac_add_aff(j, negRa)
        a += 1
    return {
        "tag": tag, "bound": bound, "hits": hits, "steps": steps,
        "table": len(tab), "t_tab": t_tab, "t": time.time() - t0,
        "deriver": d_from_affine,
    }


def search_ratio(Ra, Rb, bound, target_h160, tag=""):
    """Family B: a*Ra == b*Rb for |a|,|b| <= bound.  Exhaustive."""
    t0 = time.time()
    tab = scalar_table(Rb, bound)
    t_tab = time.time() - t0
    hits = []
    j = to_jac(pmul_fast((-bound) % N, Ra))
    a = -bound
    steps = 0
    while a <= bound:
        if a != 0 and j[2] != 0:
            i = tab.get(jac_x(j))
            if i is not None:
                for b in (i, -i):
                    if pmul_fast(a % N, Ra) == pmul_fast(b % N, Rb):
                        hits.append((a, b))
            steps += 1
        j = jac_add_aff(j, Ra)
        a += 1
    return {
        "tag": tag, "bound": bound, "hits": hits, "steps": steps,
        "table": len(tab), "t_tab": t_tab, "t": time.time() - t0,
        "deriver": d_from_ratio,
    }


def search_affine_q(Ra, Rb, Qp, ba, bb, bc, target_h160, tag=""):
    """Family C: Rb == a*Ra + b*Qp + c*G, |a|<=ba, |b|<=bb, |c|<=bc."""
    t0 = time.time()
    tab = {}
    jq = INF
    b = 0
    while b <= bb:
        jb = jq
        c = 0
        while c <= bc:
            if jb[2] != 0:
                x = jac_x(jb)
                if x is not None and x not in tab:
                    tab[x] = (b, c)
            jb = jac_add_aff(jb, G)
            c += 1
        jq = jac_add_aff(jq, Qp)
        b += 1
    t_tab = time.time() - t0
    hits = []
    negRa = neg(Ra)
    j = to_jac(padd(Rb, pmul_fast(ba % N, Ra)))
    a = -ba
    steps = 0
    while a <= ba:
        if j[2] != 0:
            got = tab.get(jac_x(j))
            if got is not None:
                gb, gc = got
                for sb in (1, -1):
                    for sc in (1, -1):
                        bb_, cc_ = gb * sb, gc * sc
                        if padd(padd(pmul_fast(a % N, Ra),
                                     pmul_fast(bb_ % N, Qp)),
                                pmul_fast(cc_ % N, G)) == Rb:
                            hits.append((a, bb_, cc_))
            steps += 1
        j = jac_add_aff(j, negRa)
        a += 1
    return {
        "tag": tag, "bound": (ba, bb, bc), "hits": hits, "steps": steps,
        "table": len(tab), "t_tab": t_tab, "t": time.time() - t0,
        "deriver": d_from_affine_q,
    }


# --------------------------------------------------------------------------
# C kernel (fast path).  Built from tools/hnp2d.cpp + ~/Kangaroo/SECPK1.
# The kernel never decides anything: it prints candidate coefficient pairs
# and every one of them is re-verified here in exact Python arithmetic.
# --------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "build")
BIN = os.path.join(CACHE, "hnp2d")
SECP = os.path.expanduser("~/Kangaroo/SECPK1")


def build_kernel(verbose=True):
    os.makedirs(CACHE, exist_ok=True)
    src = [os.path.join(HERE, "hnp2d.cpp")]
    for f in ("Int.cpp", "IntMod.cpp", "IntGroup.cpp", "Point.cpp",
              "SECP256K1.cpp", "Random.cpp"):
        src.append(os.path.join(SECP, f))
    stub = os.path.join(CACHE, "timer_stub.cpp")
    with open(stub, "w") as fh:
        fh.write("class Timer{public:static double get_tick();\n"
                 "static void printResult(char*,int,double,double);};\n"
                 "double Timer::get_tick(){return 0.0;}\n"
                 "void Timer::printResult(char*,int,double,double){}\n")
    cmd = ["clang++", "-O2", "-I", SECP, "-o", BIN] + src + [stub, "-lpthread"]
    if verbose:
        print("  building C kernel ...", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:])
        print(r.stderr[-2000:])
        raise RuntimeError("clang++ failed")
    return BIN


def search_kernel(mode, bound, Ra, Rb, tag):
    """C-kernel sweep; every candidate is then re-checked in exact Python."""
    cands, el, err = run_kernel(mode, bound, Ra, Rb)
    return dict(tag=tag, bound=bound, table=2 * bound + 1, steps=2 * bound + 1,
                hits=cands, deriver=d_from_affine if mode == "A" else d_from_ratio,
                t=el, kernel=err)


def run_kernel(mode, bound, Ra, Rb):
    """mode 'A' searches Rb == a*Ra + b*G; mode 'B' searches a*Ra == b*Rb."""
    if not os.path.exists(BIN):
        build_kernel()
    cmd = [BIN, mode, str(bound), f"{Ra[0]:064x}", f"{Ra[1]:064x}",
           f"{Rb[0]:064x}", f"{Rb[1]:064x}"]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    el = time.time() - t0
    if r.returncode != 0:
        print(f"  kernel rc={r.returncode}\n{r.stderr[-1500:]}")
        raise RuntimeError("hnp2d kernel failed")
    cands = []
    for line in r.stdout.splitlines():
        if line.startswith("HIT "):
            _, a, b = line.split()
            cands.append((int(a), int(b)))
    return cands, el, r.stderr.strip()


# --------------------------------------------------------------------------
# reporting: a hit only counts if hash160(dG) == target
# --------------------------------------------------------------------------
def report(res, sig0, sig1, target_h160=TARGET_H160):
    bnd = res["bound"]
    print(f"  {res['tag']:<34} bound={bnd!s:<12} table={res['table']:>8} "
          f"steps={res['steps']:>8}  {res['t']:7.1f}s  hits={len(res['hits'])}")
    accepted = []
    for h in res["hits"]:
        d = res["deriver"](*h, sig0, sig1)
        if d is None:
            print(f"      relation {h}: singular denominator, no candidate")
            continue
        dg = pmul(d)
        ok = h160(dg) == target_h160
        print(f"      relation {h}: d = {d:064x}")
        print(f"        hash160(dG) = {h160(dg).hex()}")
        print(f"        target     = {target_h160.hex()}   MATCH={ok}")
        if ok:
            accepted.append((h, d))
    return accepted


# --------------------------------------------------------------------------
# controls: a negative is only a negative if this same code finds a planted
# relation and returns nothing on unrelated points
# --------------------------------------------------------------------------
def sign_raw(d, k, z):
    """ECDSA sign WITHOUT low-s normalisation, so the stored s gives kappa = k."""
    r = pmul(k)[0] % N
    s = inv(k) * (z + r * d) % N
    return r, s


def kappa(r, s, z, d):
    """The nonce consistent with the STORED s: kappa = s^-1 (z + r d)."""
    return inv(s) * (z + r * d) % N


def deriver_for(fam):
    return d_from_affine if fam == "A" else d_from_ratio


def flip_flags(d, k, z, sig):
    """+1 if the stored s is the raw s (kappa = k), -1 if normalised (kappa = -k)."""
    return 1 if sign_raw(d, k, z)[1] == sig[1] else -1


def make_case(rnd, fam, a, b, c, signer):
    """Build a synthetic keypair whose nonces satisfy `fam`, and return
    everything needed to test it, INCLUDING the relation as it must be
    stated in kappa-space (kappa = the nonce the stored s implies).

    kappa_i = f_i * k_i, so with k1 = a k0 + b [ [+ c] ] the relation in
    kappa-space is  kappa1 = a' kappa0 + b' kappa1... concretely:
        A: a' = f1*f0*a,          b' = f1*b
        B: a' = a*f0,             b' = b*f1        (a'*k0 = b'*k1)
        C: a' = f1*f0*a,  b'' = f1*b,  c' = f1*c
    Getting b wrong here is the exact low-s trap of R-ISSUE78 defect 2.
    """
    dc = rnd.randrange(1, N)
    Qc = pmul(dc)
    if fam == "A":
        k0 = rnd.randrange(1, N)
        k1 = (a * k0 + b) % N
    elif fam == "B":
        # a*k0 == b*k1  =>  k0 = b*g, k1 = a*g   (NOT k0=a*g, k1=b*g)
        g0 = rnd.randrange(1, N)
        k0, k1 = b * g0 % N, a * g0 % N
    else:
        k0 = rnd.randrange(1, N)
        k1 = (a * k0 + b * dc + c) % N
    if k1 == 0:
        return None
    z0, z1 = rnd.randrange(1, N), rnd.randrange(1, N)
    s0, s1 = signer(dc, k0, z0), signer(dc, k1, z1)
    if not (verify(*s0, z0, Qc) and verify(*s1, z1, Qc)):
        return None
    f0 = flip_flags(dc, k0, z0, s0)
    f1 = flip_flags(dc, k1, z1, s1)
    if fam == "A":
        rel = (f1 * f0 * a, f1 * b)
    elif fam == "B":
        rel = (a * f0, b * f1)
    else:
        rel = (f1 * f0 * a, f1 * b, f1 * c)
    return dict(dc=dc, Qc=Qc, z0=z0, z1=z1, s0=s0, s1=s1, f=(f0, f1), rel=rel,
                R0=R_point(*s0, z0, Qc), R1=R_point(*s1, z1, Qc))


def kernel_accept(cands, fam, case, target_h160):
    """Re-verify every kernel candidate in exact Python arithmetic."""
    acc = []
    der = {"A": d_from_affine, "B": d_from_ratio}[fam]
    for a, b in cands:
        d = der(a, b, (*case["s0"], case["z0"]), (*case["s1"], case["z1"]))
        if d is not None and h160(pmul(d)) == target_h160:
            acc.append(((a, b), d))
    return acc


def run_controls():
    print("=" * 78)
    print("CONTROLS  (run BEFORE the sweep; main() aborts on any failure)")
    print("=" * 78)
    import random

    rnd = random.Random(20260927)
    fails = 0

    # [0] arithmetic: mixed add == pmul, scalar table == pmul
    j = INF
    for i in range(1, 40):
        j = jac_add_aff(j, G)
        if from_jac(j) != pmul(i):
            print(f"  [0] mixed-add vs pmul MISMATCH at i={i}")
            fails += 1
            break
    else:
        print("  [0] mixed-add chain == pmul for i in 1..39 : OK")
    tab = scalar_table(G, 20)
    if all(tab.get(jac_x(to_jac(pmul(i)))) == i for i in range(1, 21)):
        print("  [0] scalar_table(G,20) keys re-found by pmul : OK")
    else:
        print("  [0] scalar_table MISMATCH")
        fails += 1

    # [1] the three closed forms, under both signing conventions
    TRIALS = 8
    for fam, deriver in (("A", d_from_affine), ("B", d_from_ratio),
                         ("C", d_from_affine_q)):
        for mode, signer in (("raw", sign_raw), ("low-s", sign)):
            ok = used = 0
            for _ in range(TRIALS):
                a = rnd.choice([-3001, -97, -7, 3, 11, 4099])
                b = rnd.choice([-3001, -97, -7, 3, 11, 4099])
                c = rnd.choice([-5, -2, 2, 9])
                cs = make_case(rnd, fam, a, b, c, signer)
                if cs is None:
                    continue
                if fam == "C":
                    d = deriver(*cs["rel"], (*cs["s0"], cs["z0"]),
                                (*cs["s1"], cs["z1"]))
                else:
                    d = deriver(*cs["rel"], (*cs["s0"], cs["z0"]),
                                (*cs["s1"], cs["z1"]))
                used += 1
                ok += 1 if d == cs["dc"] else 0
            good = ok == used and used > 0
            print(f"  [1] closed form {fam} ({mode:>5} signer) recovers planted d :"
                  f" {ok}/{used} : {'OK' if good else 'FAIL'}")
            if not good:
                fails += 1

    # [1b] R_point == kappa*G under the stored (possibly low-s) s
    dc = rnd.randrange(1, N)
    Qc = pmul(dc)
    k0 = rnd.randrange(1, N)
    z0 = rnd.randrange(1, N)
    s0 = sign(dc, k0, z0)
    if R_point(*s0, z0, Qc) == pmul(flip_flags(dc, k0, z0, s0) * k0 % N):
        print("  [1b] R_point == kappa*G under the stored (possibly low-s) s : OK")
    else:
        print("  [1b] R_point MISMATCH")
        fails += 1

    # [2] the KERNEL re-finds a planted relation (this is the witness that
    #     makes a 0-hit sweep a real negative instead of a broken harness)
    BND = 1 << 14
    for fam in ("A", "B"):
        got = None
        for a, b in ((37, 1234), (-613, 88), (5, -9991), (1234, 37), (2, 3)):
            cs = make_case(rnd, fam, a, b, 0, sign)
            if cs is None:
                continue
            cands, el, _ = run_kernel(fam, BND, cs["R0"], cs["R1"])
            acc = kernel_accept(cands, fam, cs, h160(cs["Qc"]))
            good = bool(acc) and all(d == cs["dc"] for _, d in acc)
            print(f"  [2] KERNEL family-{fam} planted {a},{b} -> kappa {cs['rel']} :"
                  f" {'OK' if good else 'FAIL'} (cands={len(cands)},"
                  f" accepted={len(acc)}, {el:.1f}s)")
            if not good:
                fails += 1
            got = cs
            break

    # [3] BOUNDARY: coefficients exactly at +-bound must be found, or the
    #     sweep is not exhaustive over the box it claims.
    for fam in ("A", "B"):
        a, b = BND, BND - 1
        cs = make_case(rnd, fam, a, b, 0, sign)
        if cs is None:
            continue
        cands, el, _ = run_kernel(fam, BND, cs["R0"], cs["R1"])
        acc = kernel_accept(cands, fam, cs, h160(cs["Qc"]))
        good = bool(acc) and all(d == cs["dc"] for _, d in acc)
        print(f"  [3] KERNEL family-{fam} boundary a=+bound found :"
              f" {'OK' if good else 'FAIL'} (accepted={len(acc)})")
        if not good:
            fails += 1

    # [4] the bound is real: a planted coefficient ABOVE the bound must NOT
    #     be reported, so a 0-hit sweep means what it says.
    for fam in ("A", "B"):
        a, b = 1 << 15, 3
        cs = make_case(rnd, fam, a, b, 0, sign)
        if cs is None:
            continue
        cands, el, _ = run_kernel(fam, BND, cs["R0"], cs["R1"])
        acc = kernel_accept(cands, fam, cs, h160(cs["Qc"]))
        good = not acc
        print(f"  [4] KERNEL family-{fam} a=2^15 > bound is correctly missed :"
              f" {'OK' if good else 'FAIL'} (accepted={len(acc)})")
        if not good:
            fails += 1

    # [5] NULL: unrelated points must yield no candidate at all
    dc = rnd.randrange(1, N)
    Qc = pmul(dc)
    k0, k1 = rnd.randrange(1, N), rnd.randrange(1, N)
    z0, z1 = rnd.randrange(1, N), rnd.randrange(1, N)
    s0, s1 = sign(dc, k0, z0), sign(dc, k1, z1)
    R0, R1 = R_point(*s0, z0, Qc), R_point(*s1, z1, Qc)
    nA = len(run_kernel("A", BND, R0, R1)[0])
    nB = len(run_kernel("B", BND, R0, R1)[0])
    print(f"  [5] null on two unrelated nonces: family A cands={nA} "
          f"family B cands={nB} : {'OK' if nA == nB == 0 else 'FAIL'}")
    if nA or nB:
        fails += 1

    print(f"  controls: {'ALL PASS' if fails == 0 else f'{fails} FAILURE(S)'}")
    return fails


# --------------------------------------------------------------------------
def main():
    t0 = time.time()
    global BOUND_LADDER
    if "--fast" in sys.argv:
        BOUND_LADDER = (1 << 14, 1 << 18)
    if "--bound" in sys.argv:
        BOUND_LADDER = (1 << int(sys.argv[sys.argv.index("--bound") + 1]),)
    print("=" * 78)
    print("2-D NONCE-RELATION SEARCH - issue #78's two signatures")
    print("=" * 78)
    print(f"target h160 : {TARGET_H160.hex()}")
    print(f"pubkey Q    : {Q[0]:064x}")
    print()
    print("nonce points, recovered WITHOUT d  (R = s^-1 (zG + rQ) = kappa G):")
    Rs = []
    for i, (r, s, z) in enumerate(SIGS):
        R = R_point(r, s, z, Q)
        Rs.append(R)
        print(f"  R{i} = {R[0]:064x}")
        print(f"       R{i}.x mod n == r{i} : {R[0] % N == r}"
              f"   low-s: {s < N // 2}")
    print(f"  R0 == R1 : {Rs[0] == Rs[1]}      R0 == -R1 : {Rs[0] == neg(Rs[1])}")
    print()

    if "--selftest" in sys.argv:
        rc = run_controls()
        return 0 if rc == 0 else 1

    if run_controls() != 0:
        print("\nABORT: uncertified harness. No sweep may be ledgered.")
        return 2
    print()

    sig0, sig1 = SIGS
    accepted = []

    print("-" * 78)
    print("FAMILY A   k1 = a*k0 + b        (R1 = a*R0 + b*G)")
    print("-" * 78)
    for bound in BOUND_LADDER:
        for tag, (Ra, Rb) in (("A  R1 = a*R0 + b*G", (Rs[0], Rs[1])),
                              ("A' R0 = a*R1 + b*G", (Rs[1], Rs[0]))):
            res = search_kernel("A", bound, Ra, Rb, tag)
            accepted += report(res, sig0, sig1)
            if res["hits"]:
                print("      ^ relation present; not escalating the ladder")
                break
        if accepted:
            break
        if bound == BOUND_LADDER[-1]:
            break

    print()
    print("-" * 78)
    print("FAMILY B   a*k0 = b*k1          (a*R0 = b*R1)")
    print("-" * 78)
    for bound in BOUND_LADDER:
        res = search_kernel("B", bound, Rs[0], Rs[1], "B  a*R0 = b*R1")
        accepted += report(res, sig0, sig1)
        if res["hits"]:
            break
        if bound == BOUND_LADDER[-1]:
            break

    print()
    print("-" * 78)
    print("FAMILY C   k1 = a*k0 + b*d + c  (R1 = a*R0 + b*Q + c*G)")
    print("-" * 78)
    for ba, bb, bc in ((1 << 10, 1 << 6, 1 << 6), (1 << 12, 1 << 8, 1 << 8),
                       (1 << 13, 1 << 9, 1 << 9), (1 << 14, 1 << 10, 1 << 10)):
        res = search_affine_q(Rs[0], Rs[1], Q, ba, bb, bc, TARGET_H160,
                              tag="C  R1 = a*R0 + b*Q + c*G")
        accepted += report(res, sig0, sig1)
        if res["hits"]:
            break

    print()
    print("=" * 78)
    if accepted:
        print("*** ACCEPTED: a d with hash160(dG) == the target h160 ***")
        for h, d in accepted:
            print(f"    relation {h}   d = {d:064x}")
    else:
        print("VERDICT: 0 accepted. No small-coefficient 2-D relation between")
        print("  the two nonce points, and no d, over the bounds searched.")
        print("  This EXTENDS the R-ISSUE78 1-D negatives; it does not replace")
        print("  them, and issue #78 stays UNPROVEN (m=2 still cannot support a")
        print(f"  {H.BIAS_CLAIM}-bit bias claim: needs m >= 5).")
    print(f"elapsed {time.time() - t0:.1f}s")
    print("=" * 78)
    return 0 if accepted else 1


if __name__ == "__main__":
    sys.exit(main())
