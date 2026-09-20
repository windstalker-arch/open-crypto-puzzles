import base64
import hashlib

from coincurve import PublicKey
from Crypto.Cipher import AES


def evp(pw,salt,digest='md5'):
    H=hashlib.md5 if digest=='md5' else hashlib.sha256
    d=b'';prev=b''
    while len(d)<48: prev=H(prev+pw+salt).digest(); d+=prev
    return d[:32],d[32:48]
def dec(ct,pw,salt,digest='md5'):
    k,iv=evp(pw,salt,digest); return AES.new(k,AES.MODE_CBC,iv).decrypt(ct)
def b58(b):
    A='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n=int.from_bytes(b,'big');o=''
    while n>0:n,r=divmod(n,58);o=A[r]+o
    return '1'*(len(b)-len(b.lstrip(b'\x00')))+o
def wif(priv,comp):
    b=b'\x80'+priv+(b'\x01' if comp else b'')
    return b58(b+hashlib.sha256(hashlib.sha256(b).digest()).digest()[:4])

BLOB1='U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9zQvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ'
r=base64.b64decode(BLOB1); s1=r[8:16]; ct1=r[16:]
pw5=b'matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist'
P=dec(ct1,pw5,s1,'md5')
K_C1=P[:32]; K_C2=P[32:64]; E_C=P[64:79]
print('K_C1',K_C1.hex())
print('K_C2',K_C2.hex())
print('E_C(15)',E_C[:15].hex())
print('WIF K_C1 uncomp:', wif(K_C1,False))
pk=PublicKey.from_valid_secret(K_C1).format(compressed=False)
print('K_C1 pub uncomp:', pk.hex())
h=hashlib.new('ripemd160',hashlib.sha256(pk).digest()).hexdigest()
print('K_C1 H160:',h)
