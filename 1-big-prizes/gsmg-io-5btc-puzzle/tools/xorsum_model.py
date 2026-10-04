#!/usr/bin/env python3
"""
GSMG XOR research in the CORRECT domain.

Context: the page's certified instruction is "matrixsumlist" + "enter"
(104 + 40 + 144 bits = len("matrixsumlistenter"), zero leftover).  dbbib_91 is
the strict upper triangle of a 14x14 symmetric matrix (14*13/2 = 91), so the
"matrix sum list" is the 14 row sums.  Rows 147 / R-XOR / R-XORP13 pyramided
the raw a..i token streams instead -- a family the page never asked for.

This tool sweeps the model class that the page DID ask for:
    key construction x key functional x key alignment x combine operator

Positive control: reproduces ~/gsmg/dbbi_sum_faed.py output byte for byte.
"""
import itertools, math, sys

V = {c: i + 1 for i, c in enumerate("abcdefghi")}   # a=1 .. i=9
A = "dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe"
B = "faedggeedfcbdabhhggcadcfeddgfdgbgigaaedggiafaecghggcdaihehahbahigceifgbfgefgaifabifagaegeacgbbeagfggeeggafbacgfcdbeiffaafcidahgdeefghhcggaegdebhhegeghcegadfbdiagefcicggifdcgaaggfbigaicfbhecaecbceiaicebgbgiecdeggfgegaedggfiiciiififhggcgfgdcdggefcbeeigefibgibggghhfbcgifdehedfdagicdbhicgaiedaehahghhcihdghfhbiicecbiichihiiigiddgehhdfdchcbafgfbhaheagegecafehgcfggggcagfhhghbaihidiehhfdeggdgcihggggghadahigigbgecgedfcdggaccdehiicigfbffhggaeidbbeibbeiifdgfdhieeeieeecifdgdahdiggfhegfiaffiggbcbcehceabfbedbiibfbfdedeehgigfaaiggagbeiichiedifbehgbccahhbiibibbibdcbahaidhfahiihic"

ENG = [.08167,.01492,.02782,.04253,.12702,.02228,.02015,.06094,.06966,.00153,
       .00772,.04025,.02406,.06749,.07507,.01929,.00095,.05987,.06327,.09056,
       .02758,.00978,.02360,.00150,.01974,.00074]

def mat(fill):
    """14x14 symmetric, diag 0, strict upper triangle filled from A in `fill` order."""
    M = [[0]*14 for _ in range(14)]
    k = 0
    for i in range(14):
        for j in range(i+1, 14):
            v = V[A[k]]; k += 1
            M[i][j] = M[j][i] = v
    if fill == "rev":
        for i in range(14):
            for j in range(i+1, 14):
                M[i][j] = M[j][i] = 14 - M[i][j]
    elif fill == "colmaj":
        M = [[0]*14 for _ in range(14)]
        k = 0
        for j in range(14):
            for i in range(j):
                v = V[A[k]]; k += 1
                M[i][j] = M[j][i] = v
    elif fill == "diagA":
        for i in range(14):
            M[i][i] = V[A[(i*13)//2]]
    return M

def rowsums(M):
    return [sum(r) for r in M]

def chunks(s, n):
    return [sum(V[c] for c in s[j:j+n]) for j in range(0, len(s), n)]

def align(K, i, mode, off):
    if mode == "mod14":  return K[(i+off) % 14]
    if mode == "mod14r": return K[13-((i+off) % 14)]
    if mode == "mod13":  return K[(i+off) % 13]
    if mode == "mod15":  return K[(i+off) % 15] if (i+off) % 15 < 14 else K[0]
    if mode == "mod38":  return K[i] if i < 14 else K[0]
    if mode == "mod7":   return K[(i+off) % 7]
    return K[(i+off) % 14]

def combine(R, k, op):
    if op == "xor26":    return (R ^ k) % 26
    if op == "sub26":    return (R - k) % 26
    if op == "add26":    return (R + k) % 26
    if op == "add1_26":  return (R + k - 1) % 26
    if op == "sub1_26":  return (R - k - 1) % 26
    if op == "modxor":   return ((R % 26) ^ (k % 26)) % 26
    if op == "xorsub":   return ((R ^ k) - 1) % 26
    if op == "xor_then_sub1": return ((R ^ k) - 1) % 26
    if op == "r26k26sub":return (R % 26 - k % 26) % 26
    if op == "r26k26add":return (R % 26 + k % 26) % 26
    if op == "xorfull":  return (R ^ k) & 31
    return (R ^ k) % 26

def chi2(s):
    n = len(s); c = [0]*26
    for ch in s: c[ord(ch)-65] += 1
    return sum((c[i] - n*ENG[i])**2 / (n*ENG[i]) for i in range(26) if n*ENG[i] > 0)

COMMON = ["THE","AND","ING","ENT","ION","HER","FOR","THA","NTH","INT","ERE","TIO","TER","EST","ERS","ATI","HAT","ATE","ALL","ETH","HES","VER","HIS","OFT","STH","OTH","RES","ON","IT","IN","IS","AT","ES","OR","TE","OF","ED"]

def runlen(s):
    """longest run of plausible English bigram-trigram territory (crude but monotone)"""
    best = cur = 0
    for i in range(len(s)-1):
        bg = s[i:i+2]
        ok = bg in COMMON or bg in ("TH","HE","IN","ER","AN","RE","ON","EN","AT","ES","ED","OR","TE","OF","ND","TI","ES","AL","ST","NT","NG","SE","LE","SA","SI","AR","MA","IL")
        cur = cur + 1 if ok else 0
        best = max(best, cur)
    return best+1 if s else 0

def best_run(s):
    """longest run containing at least one common trigram"""
    hits = set()
    for tr in COMMON[:24]:
        i = s.find(tr)
        if i >= 0: hits.add(i)
    if not hits: return 0, ""
    i = min(hits)
    lo = 0
    for h in sorted(hits):
        if h - lo > 14: break
        lo = h
    hi = max(h for h in hits if h <= lo+10)
    return hi-lo+3, s[max(0,lo-2):hi+3]

def decode(R, K, amode, off, op):
    out = []
    for i, r in enumerate(R):
        v = combine(r, align(K, i, amode, off), op)
        out.append(chr((v % 26) + 65))
    return "".join(out)

def main():
    # ---- positive control ----
    M = mat("row"); K = rowsums(M); R = chunks(B, 15)
    base = decode(R, K, "mod14", 0, "xor26")
    exp = "JLIQFOPGVBLSENDTHECZAGJJYDSWCGUDJNFTWB"
    assert base == exp, f"CONTROL FAIL {base}"
    print(f"POSITIVE CONTROL PASS  K={K}")
    print(f"                       baseline={base}")
    print(f"                       chi2={chi2(base):.1f}")
    print()

    results = []
    for fill in ["row", "rev", "colmaj", "diagA"]:
        K = rowsums(mat(fill))
        for kname, Kv in [("rowsum", K), ("rowsum26", [x % 26 for x in K]),
                          ("rowsum26p", [x % 26 + 1 for x in K]),
                          ("colsum", K), ("max", [max(mat(fill)[i]) for i in range(14)]),
                          ("min", [min(mat(fill)[i]) for i in range(14)])]:
            for amode in ["mod14", "mod14r", "mod13", "mod15", "mod38", "mod7"]:
                for off in range(14):
                    for op in ["xor26","sub26","add26","add1_26","sub1_26","modxor",
                               "xorsub","r26k26sub","r26k26add"]:
                        s = decode(R, Kv, amode, off, op)
                        results.append((chi2(s), -runlen(s), fill, kname, amode, off, op, s))
    results.sort()
    print(f"swept {len(results)} variants")
    print()
    print("=== TOP 12 BY ENGLISH CHI-SQUARE (lower=better; English text ~ 38-60 at n=38) ===")
    for r in results[:12]:
        print(f"  chi2={r[0]:6.1f} run={-r[1]:2}  {r[2]:6}/{r[3]:8}/{r[4]:6}/off{r[5]:2}/{r[6]:8}  {r[7]}")
    print()
    print("=== TOP 8 BY LONGEST COMMON-TRIGRAM RUN ===")
    for s in sorted(results, key=lambda r: (-r[1], r[0]))[:8]:
        n, frag = best_run(s[7])
        print(f"  run={n:2} chi2={s[0]:6.1f}  {s[2]:6}/{s[3]:8}/{s[4]:6}/off{s[5]:2}/{s[6]:8}  frag={frag!r}")
        print(f"        full={s[7]}")

if __name__ == "__main__":
    main()