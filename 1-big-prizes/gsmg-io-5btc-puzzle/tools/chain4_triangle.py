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
salt=raw[8:16]; ct=raw[16:]
XK=bytes.fromhex('a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735')
k,iv=evp(XK,salt,'md5'); cc=AES.new(k,AES.MODE_CBC,iv).decrypt(ct); cc=cc[:-cc[-1]]
mask=bytes.fromhex('b657264f2f6e6921')
mystery=bytes(a^b for a,b in zip(cc[158:158+1168],(mask*146)[:1168]))
PW=bytes.fromhex('38d4f4c90cb45fdfc8cff50d0ed1c5740a25de4b8e946d0a5ae2667a23a259cc')
kk,ivv=evp(PW,mystery[8:16],'md5')
c4=AES.new(kk,AES.MODE_CBC,ivv).decrypt(mystery[16:]); c4=c4[:-c4[-1]]

TX='f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464'
def ok(priv):
    try:
        pk=PublicKey.from_valid_secret(priv).format(compressed=False)
        if pk[1:33].hex()==TX: return True
    except Exception: pass
    return False

body=c4[2:]  # skip '+-'
print('body len',len(body))
# try splits into 32-byte blocks
for nblk in [35,36,34,33,32]:
    if len(body)%nblk==0:
        bs=[body[i*nblk:(i+1)*nblk] for i in range(len(body)//nblk)]
        print('split',nblk,'blklen',len(bs[0]))
print()
# attempt XOR-pyramid over 32-byte aligned blocks
data=body
for align in [32,28,27,26,23]:
    if len(data)%align==0:
        blocks=[data[i*align:(i+1)*align] for i in range(len(data)//align)]
        # XOR all blocks -> 32-byte guess
        acc=bytes(align)
        for b in blocks: acc=bytes(x^y for x,y in zip(acc,b))
        if len(acc)>=32 and ok(acc[:32]):
            print('HIT xor-all align',align)
print('block xor candidates tested; no structural XOR-pyramid attempted yet')
# check entropy/printable
print('printable frac:', sum(32<=b<127 for b in body)/len(body))
