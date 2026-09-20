import os
import base64
import hashlib
from pathlib import Path

from Crypto.Cipher import AES


def sha256b(b): return hashlib.sha256(b).hexdigest()

raw = base64.b64decode(Path(os.path.expanduser("~/briefcase/CosmicDuality.txt")).read_bytes().strip())
print('raw b64 len:', len(raw))
salt=raw[8:16]; ct=raw[16:]
print('salt:', salt.hex())

# try EVP sha256 and md5 decrypts with the dualite blob's community password
# The known L1 key from issue 68: a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735
XORKEY=bytes.fromhex('a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735')
# oracle_dualite: password = sha256(X).hexdigest(), digest sha256. But L1 = XOR with XORKEY? 
# Let's see: oracle says password->sha256->AES. But research says L1 decrypt under XOR-key a795de11..
# Approach: decrypt AES-256-CBC with EVP(password=XORKEY as bytes?, sha256) and also try md5.
def evp(pw,salt,digest):
    H=hashlib.md5 if digest=='md5' else hashlib.sha256
    d=b'';prev=b''
    while len(d)<48:
        prev=H(prev+pw+salt).digest(); d+=prev
    return d[:32],d[32:48]
for pw in [XORKEY, XORKEY.hex().encode()]:
    for dig in ['sha256','md5']:
        k,iv=evp(pw,salt,dig)
        try:
            p=AES.new(k,AES.MODE_CBC,iv).decrypt(ct)
            if p and p[-1]<=16 and p[-p[-1]:]==bytes([p[-1]])*p[-1]:
                p=p[:-p[-1]]
                print('digest',dig,'pw len',len(pw),'plain len',len(p))
                print('sha256:', sha256b(p))
        except Exception as e:
            print('err',dig,e)
