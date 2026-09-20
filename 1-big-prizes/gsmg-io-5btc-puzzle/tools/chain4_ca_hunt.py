import os
import base64
import hashlib
from pathlib import Path

from coincurve import PublicKey
from Crypto.Cipher import AES


def sha256b(b): return hashlib.sha256(b).hexdigest()
def evp(pw,salt,digest='md5'):
    H=hashlib.md5 if digest=='md5' else hashlib.sha256
    d=b'';prev=b''
    while len(d)<48:
        prev=H(prev+pw+salt).digest(); d+=prev
    return d[:32],d[32:48]
raw=base64.b64decode(Path(os.path.expanduser("~/briefcase/CosmicDuality.txt")).read_bytes().strip())
XK=bytes.fromhex('a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735')
k,iv=evp(XK,raw[8:16],'md5'); cc=AES.new(k,AES.MODE_CBC,iv).decrypt(raw[16:]); cc=cc[:-cc[-1]]
mask=bytes.fromhex('b657264f2f6e6921')
mystery=bytes(a^b for a,b in zip(cc[158:158+1168],(mask*146)[:1168]))
PW=bytes.fromhex('38d4f4c90cb45fdfc8cff50d0ed1c5740a25de4b8e946d0a5ae2667a23a259cc')
kk,ivv=evp(PW,mystery[8:16],'md5')
c4=AES.new(kk,AES.MODE_CBC,ivv).decrypt(mystery[16:]); c4=c4[:-c4[-1]]
TX='f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464'
def isk(priv):
    try: return PublicKey.from_valid_secret(priv).format(compressed=False)[1:33].hex()==TX
    except Exception: return False
def hit_priv(acc):
    if len(acc)>=32:
        for w in [acc[:32],acc[-32:],hashlib.sha256(acc).digest() if len(acc)!=32 else acc]:
            if isk(w): print("  >>> PRIVATE KEY HIT:",w.hex()); return True
    return False
CA='cd3fea3d'

body=c4[2:]
print("body len",len(body))
# sweep header offset h, then 35 blocks of 32 bytes
found=False
for h in range(30):
    seg=body[h:]
    if len(seg)>=35*32:
        blocks=[seg[i*32:(i+1)*32] for i in range(35)]
        # XOR all 35 -> 32B
        acc=bytes(32)
        for b in blocks: acc=bytes(x^y for x,y in zip(acc,b))
        hx=sha256b(acc)
        tag=''
        if hx.startswith(CA): tag+=" CA-PREFIX-XORALL!!"
        if hit_priv(acc): tag+=" PRIV-HIT"
        # also scan each block individually
        for i,b in enumerate(blocks):
            if hit_priv(b): tag+=f" BLK{i}-PRIV"
            if sha256b(b).startswith(CA): tag+=f" BLK{i}-CA"
        if tag:
            print(f"offset {h}: acc_sha={hx[:16]}...{tag}")
            found=True
print("done. found=",found)

# Also check the direct formula operand cc[833:865]
seg833=cc[833:865]
print("cc[833:865] =",seg833.hex())
print("  is key? ", isk(seg833))
print("  sha256 prefix:", sha256b(seg833)[:8])
# If ca absent, check a few derived guesses for ca[280:312] via xor with k if k were derivable -- skip, can't.
