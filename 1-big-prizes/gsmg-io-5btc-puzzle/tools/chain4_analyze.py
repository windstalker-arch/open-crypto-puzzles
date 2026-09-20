import os
import base64
import hashlib
from pathlib import Path

from Crypto.Cipher import AES


def evp_dict(pw,salt,digest='md5'):
    H=hashlib.md5 if digest=='md5' else hashlib.sha256
    d=b'';prev=b''
    while len(d)<48:
        prev=H(prev+pw+salt).digest(); d+=prev
    return d[:32],d[32:48]

raw = base64.b64decode(Path(os.path.expanduser("~/briefcase/CosmicDuality.txt")).read_bytes().strip())
salt=raw[8:16]; ct=raw[16:]
XORKEY=bytes.fromhex('a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735')
k,iv=evp_dict(XORKEY,salt,'md5')
cc=AES.new(k,AES.MODE_CBC,iv).decrypt(ct); cc=cc[:-cc[-1]]
mask=bytes.fromhex('b657264f2f6e6921')
mystery=bytes(a^b for a,b in zip(cc[158:158+1168],(mask*(146))[:1168]))
msalt=mystery[8:16]; mc=mystery[16:]
PW=bytes.fromhex('38d4f4c90cb45fdfc8cff50d0ed1c5740a25de4b8e946d0a5ae2667a23a259cc')
kk,ivv=evp_dict(PW,msalt,'md5')
chain4=AES.new(kk,AES.MODE_CBC,ivv).decrypt(mc); chain4=chain4[:-chain4[-1]]
print('chain4 len',len(chain4))
print('first 64:',chain4[:64])
print('hex first 128:')
for i in range(0,128,16): print(chain4[i:i+16].hex())
# find '+-' marker
print('has +- at', chain4.find(b'+-'))
print('visible:',repr(chain4[:200]))
