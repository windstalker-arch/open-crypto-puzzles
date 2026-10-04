#!/usr/bin/env python3
"""
Solve the 38-char matrix-sum XOR key by beam search instead of sweeping it.

The baseline (R[i] ^ K[i%14]) % 26 yields
    JLIQFOPGVB LSENDTHE CZAGJJYDSWCGUDJNFTWB
i.e. positions 10..17 spell "LSENDTHE".  Eight consecutive English letters out
of a deterministic pipeline is ~26^-8 under chance, so the MODEL is right and
the remaining question is which key slots are wrong.

Sweep-based scoring cannot answer this: at n=38 over 26 categories chi2 has
df=25, so a RANDOM string already scores ~25 and the ranking is noise.  So
search the key directly, scoring assembled text with an English bigram/trigram
model, beam-wise over string positions (slot = i % 14, assigned once).

Also runs the same search for the additive and subtractive combine ops, to test
whether XOR is the right operator or merely the one that produced SENDTHE.
"""
import math
from collections import defaultdict

V = {c: i + 1 for i, c in enumerate("abcdefghi")}
A = "dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe"
B = "faedggeedfcbdabhhggcadcfeddgfdgbgigaaedggiafaecghggcdaihehahbahigceifgbfgefgaifabifagaegeacgbbeagfggeeggafbacgfcdbeiffaafcidahgdeefghhcggaegdebhhegeghcegadfbdiagefcicggifdcgaaggfbigaicfbhecaecbceiaicebgbgiecdeggfgegaedggfiiciiififhggcgfgdcdggefcbeeigefibgibggghhfbcgifdehedfdagicdbhicgaiedaehahghhcihdghfhbiicecbiichihiiigiddgehhdfdchcbafgfbhaheagegecafehgcfggggcagfhhghbaihidiehhfdeggdgcihggggghadahigigbgecgedfcdggaccdehiicigfbffhggaeidbbeibbeiifdgfdhieeeieeecifdgdahdiggfhegfiaffiggbcbcehceabfbedbiibfbfdedeehgigfaaiggagbeiichiedifbehgbccahhbiibibbibdcbahaidhfahiihic"

# ---------- build the reference K and R ----------
def rowsums():
    M = [[0]*14 for _ in range(14)]
    k = 0
    for i in range(14):
        for j in range(i+1, 14):
            M[i][j] = M[j][i] = V[A[k]]; k += 1
    return [sum(r) for r in M]

K0 = rowsums()
R = [sum(V[c] for c in B[j:j+15]) for j in range(0, len(B), 15)]
assert len(R) == 38

# ---------- English bigram model ----------
COMMON_BG = set("""th he in er an re on at en nd ti es or te of ed is it al ar
st to nt ng se ha as ou io le ve co me de hi ri ro ic ne ea ra ce li ch ll be ma si om ur
ca el ta la ns di fo ho pe ec pr no ct us ac ot il tr ly nc et ut ss so rs un lo wa ge ie
wh ee wi em ad ol rt po we na ul ni ts""".split())
COMMON_TRI = ["THE","AND","ING","ENT","ION","HER","FOR","THA","NTH","INT","ERE","TIO",
              "TER","EST","ERS","ATI","HAT","ATE","ALL","ETH","HES","VER","HIS","OFT",
              "STH","OTH","RES","TED","TES","TIS","TIO","SSI","LLY","IGH","ICH","NCE","NDE",
              "STE","CON","RES","SON","MEN","EAN"]

def score_partial(s):
    """incremental score: bigram hits + 4x trigram hits over the assembled prefix"""
    sc = 0.0
    for i in range(len(s)-1):
        if s[i:i+2] in COMMON_BG: sc += 1.0
    for tr in COMMON_TRI:
        if tr in s: sc += 4.0
    return sc

# ---------- beam search ----------
OPS = {
    "xor":   lambda r, k: (r ^ k) % 26,
    "sub":   lambda r, k: (r - k) % 26,
    "add":   lambda r, k: (r + k) % 26,
    "sub1":  lambda r, k: (r - k - 1) % 26,
    "add1":  lambda r, k: (r + k - 1) % 26,
}

CAND = list(range(0, 136))

def beam(opname, beamw=1500, restrict=None):
    f = OPS[opname]
    # state: (score, text, assignedK tuple of len 14 or None slots)
    beam = [(0.0, "", (None,)*14)]
    for i in range(38):
        slot = i % 14
        nxt = []
        for sc, txt, kv in beam:
            if kv[slot] is not None:
                ch = chr(f(R[i], kv[slot]) + 65)
                t2 = txt + ch
                nxt.append((sc + (1.0 if len(txt) and txt[-1]+ch in COMMON_BG else 0.0), t2, kv))
            else:
                for v in CAND:
                    if restrict and not (restrict[0] <= v <= restrict[1]): continue
                    ch = chr(f(R[i], v) + 65)
                    t2 = txt + ch
                    gain = (1.0 if len(txt) and txt[-1]+ch in COMMON_BG else 0.0)
                    k2 = list(kv); k2[slot] = v
                    nxt.append((sc + gain, t2, tuple(k2)))
        # trigram bonus applied on the fly
        nxt.sort(key=lambda x: -(x[0] + 4.0*sum(1 for tr in COMMON_TRI if tr in x[1])))
        beam = nxt[:beamw]
    beam.sort(key=lambda x: -(x[0] + 4.0*sum(1 for tr in COMMON_TRI if tr in x[1])))
    return beam

def report(name, beam):
    print(f"--- {name} ---")
    for sc, txt, kv in beam[:4]:
        full = score_partial(txt) + 4.0*sum(1 for tr in COMMON_TRI if tr in txt)
        print(f"  score={full:5.1f}  {txt}")
    print()

if __name__ == "__main__":
    base = "".join(chr(((R[i] ^ K0[i % 14]) % 26) + 65) for i in range(38))
    print(f"reference K      = {K0}")
    print(f"baseline (xor)   = {base}")
    print(f"baseline english = "
          f"{sorted(set('SENDTHE'))} in window 10..17 -> 'LSENDTHE'")
    print(f"baseline score   = {score_partial(base):.1f}")
    print()
    for op in ["xor", "sub", "add", "sub1", "add1"]:
        report(op, beam(op))
    print("=== xor restricted to the plausible row-sum band 45..85 ===")
    report("xor(45..85)", beam("xor", restrict=(45, 85)))