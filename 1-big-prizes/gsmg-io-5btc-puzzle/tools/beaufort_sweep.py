import os
import json
from pathlib import Path

d = json.loads(Path(os.path.expanduser("~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle/data/salphaseion-streams.json")).read_text())
djj = json.loads(Path(os.path.expanduser("~/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle/data/finalpage-digit-streams.json")).read_text())
object_256=d['object_256']; even=d['even_stream']; odd=d['odd_pre_reduction']; dropped=d['dropped_29']
dbbib=djj['dbbib']; faed=djj['faed_570'].rstrip('z')
def beaufort_dec(ct,key):
    k=key.upper();out=[];ki=0
    for c in ct.upper():
        if 'A'<=c<='Z':
            kd=ord(k[ki%len(k)])-65; out.append(chr(65+((kd-(ord(c)-65)+26)%26))); ki+=1
        else: out.append(c)
    return ''.join(out)
def vigenere_dec(ct,key):
    k=key.upper();out=[];ki=0
    for c in ct.upper():
        if 'A'<=c<='Z':
            kd=ord(k[ki%len(k)])-65; out.append(chr(65+((ord(c)-65-kd)%26))); ki+=1
        else: out.append(c)
    return ''.join(out)
keys=["DBIFHCEG","BTCSEED","CAUSALITY","ENTER","ENTERTHEKEYS","MATRIXSUMLIST","YINYANG",
 "PRIME","PRIMES","YELLOWBLUE","GOLDENRATIO","PHI","MATRIX","THEONE","FIRSTHINT",
 "SECONDANSWER","OURFIRSTHINTISYOURLASTCOMMAND","THEARCHITECTSCHOCICE",
 "HOPEISTHEQUINTESSENTIALHUMANDELUSION","THESEEDISPLANTED","WHITERABBIT","LASTWORDS",
 "THISPASSWORD","ARCHICHOICE","HALFANDBETTERHALF","PRIVATEKEY","SHA","MATRIXSUMLISTENTER"]
def map_ai_AI(s): return ''.join({'a':'A','b':'B','c':'C','d':'D','e':'E','f':'F','g':'G','h':'H','i':'I'}[c] for c in s)
def transpose(s,rows,cols):
    s=s[:rows*cols]; g=[s[i*cols:(i+1)*cols] for i in range(rows)]
    return ''.join(g[r][c] for c in range(cols) for r in range(rows))
cts={}
cts['obj256']=object_256; cts['even285']=even; cts['odd285']=odd; cts['drop29']=dropped
cts['faedAI']=map_ai_AI(faed); cts['dbbibAI']=map_ai_AI(dbbib)
cts['faed15x38T']=transpose(map_ai_AI(faed),15,38); cts['faed38x15T']=transpose(map_ai_AI(faed),38,15)
cts['dbbib3x23T']=transpose(map_ai_AI(dbbib),3,23); cts['dbbib23x3T']=transpose(map_ai_AI(dbbib),23,3)
cands=set()
for ct in cts.values():
    for k in keys:
        cands.add(beaufort_dec(ct,k)); cands.add(vigenere_dec(ct,k))
cands.discard('')
with open('beaufort_cands.txt','w') as f:
    f.writelines(c+'\n' for c in cands)
print(len(cands), "candidates written")
