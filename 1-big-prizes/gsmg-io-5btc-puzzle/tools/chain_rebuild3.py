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

raw = base64.b64decode(Path(os.path.expanduser("~/briefcase/CosmicDuality.txt")).read_bytes().strip())
salt=raw[8:16]; ct=raw[16:]
XORKEY=bytes.fromhex('a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735')
k,iv=evp(XORKEY,salt,'md5')
cc=AES.new(k,AES.MODE_CBC,iv).decrypt(ct)
cc=cc[:-cc[-1]]
print('cc len',len(cc),'sha256',sha256b(cc))

mask=bytes.fromhex('b657264f2f6e6921')
# mystery = cc[158:] trimmed to 1168
seg=cc[158:158+1168]
print('seg len',len(seg))
mystery=bytes(a^b for a,b in zip(seg,(mask*(1168//8+1))[:1168]))
print('mystery len',len(mystery),'sha256',sha256b(mystery))
print('mystery first 32:',mystery[:32].hex())
print('mystery head repr:',repr(mystery[:64]))

# Now try to reproduce chain4_decrypted (1151B, sha256 e4269ed5...) using the known password
PW=bytes.fromhex('38d4f4c90cb45fdfc8cff50d0ed1c5740a25de4b8e946d0a5ae2667a23a259cc')
# AES key might be raw PW or EVP-derived. #88 said "password = 38d4f4c9..." 
for dig in ['md5','sha256']:
    kk,ivv=evp(PW,b'\x00'*8,dig)  # no salt known
    # try raw too
for mode_pw in [PW]:
    # try EVP with the blob's own salt? The mystery likely is Salted__ format
    if mystery[:8]==b'Salted__':
        ms=mystery[8:16]; mc=mystery[16:]
        print('mystery is salted, msalt',ms.hex())
        kk,ivv=evp(PW,ms,'md5')
        p=AES.new(kk,AES.MODE_CBC,ivv).decrypt(mc)
        if p and p[-1]<=16 and p[-p[-1]:]==bytes([p[-1]])*p[-1]:
            p=p[:-p[-1]]
            print('chain4 via md5 len',len(p),'sha256',sha256b(p))
        kk,ivv=evp(PW,ms,'sha256')
        p=AES.new(kk,AES.MODE_CBC,ivv).decrypt(mc)
        if p and p[-1]<=16 and p[-p[-1]:]==bytes([p[-1]])*p[-1]:
            p=p[:-p[-1]]
            print('chain4 via sha256 len',len(p),'sha256',sha256b(p))
