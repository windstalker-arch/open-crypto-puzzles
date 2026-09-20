import os
import base64
import hashlib
from pathlib import Path

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

# dump full hex in 32-byte rows
print("TOTAL",len(c4))
for i in range(0,len(c4),32):
    row=c4[i:i+32]
    print(f"{i:4d} {row.hex()}  {row!r}")
