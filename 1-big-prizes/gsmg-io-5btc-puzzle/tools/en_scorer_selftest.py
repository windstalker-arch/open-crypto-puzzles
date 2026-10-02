#!/usr/bin/env python3
import sys,re,math,collections,random,glob,os
os=__import__('os')
sys.path.insert(0,'tools')
import certified_vic as V
# English quadgram scorer, calibrated. See analysis/tested.md R-ENSCORE-2026-10-01.
# Reference corpus is SYSTEM English only (no puzzle artifact, no certified answer)
# -- scoring the model on the very string it must judge is what made v1 and v2
# silently useless.
import glob as _glob
BANNED=("open-crypto-puzzles","briefcase","gsmg",".agents","tmp/opencode")
WANT="INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE"
def _load():
    t=[]
    for pat in ("/usr/share/dict/*","/data/data/com.termux/files/usr/lib/python3.14/*.py",
                "/data/data/com.termux/files/usr/share/doc/*/*"):
        for q in _glob.glob(pat):
            if any(b in q for b in BANNED): continue
            try:
                if os.path.isdir(q) or os.path.getsize(q)>4_000_000: continue
                t.append(open(q,encoding="utf-8",errors="ignore").read())
            except Exception: pass
    b="\n".join(t).upper().replace(WANT,"")
    return re.sub(r"[^A-Z]+"," ",b)
REF=_load()
Q=collections.Counter(REF[i:i+4] for i in range(len(REF)-3))
BIG=sum(Q.values())
FLOOR=math.log(1.0/BIG,26**4)
def score(s):
    s=re.sub(r"[^A-Z]","",s.upper())
    if len(s)<4: return FLOOR
    return sum(math.log(Q.get(s[i:i+4],0)+0.01)-math.log(BIG) for i in range(len(s)-3))/(len(s)-3)
ct=V.phase32_digit_line()
def dec(b,e1=1,e2=4): return V.decode(ct,V.build_grid(b,e1,e2),e1,e2)
GOOD="FUBCDORA.LETHINGKYMVPS.JQZXW"
CORRUPT="UFBCCDORALETHINGKYMVPS.JQZXW"   # head swap F<->U, verified to change output
g,b = score(dec(GOOD)), score(dec(CORRUPT))
r = score("".join(random.Random(5).choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(91)))
print("ACCEPTANCE TEST v3 (control chosen to alter the output)")
print("  corpus %d chars / %d quadgrams   random floor %.3f"%(len(REF),BIG,FLOOR))
print("  A known-good decode     : %.3f   %r"%(g,dec(GOOD)[:52]))
print("  B head-corrupted decode : %.3f   %r"%(b,dec(CORRUPT)[:52]))
print("  C uniform random        : %.3f"%r)
print()
A = g > r + 1.0
Bc = (g-b) > 0.5
print("  A  good >> random      :",A,"  margin %.2f"%(g-r))
print("  B  good >> corrupted   :",Bc,"  margin %.2f"%(g-b))
print("  CALIBRATION","PASS" if (A and Bc) else "FAIL")
raise SystemExit(0 if (A and Bc) else 1)
