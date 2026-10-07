#!/usr/bin/env python3
"""ICE-cipher sweep over the GSMG gate objects (ledger row R-ICESWEEP-2026-10-06).

Cipher: ICE (Ian Colgate) as implemented by ~/ICECipher (RenardDev/CryptICE 2.1),
8-byte-block Feistel, tool-native mode (whole buffer, tail passed through).

Hypothesis: a gate blob or its raw ciphertext carries an ICE layer keyed by
material derivable from published/recovered strings. Detectors: inner b'Salted__'
envelope, WIF, PEM, >=95%% printable -> candidate X via tools/oracle.py --stdin.

Witness (required by AGENTS.md): a synthetic b'Salted__'+salt+80-byte envelope is
ICE-encrypted and pushed through the same detector; it must fire SALTED_AT_0.

Implementation findings (do not trust multi-instance use of this library):
  1. IceKey sets __bIsInitializedSBOX as an INSTANCE attribute, so the class flag
     never sticks and every construction rebuilds the 4x1024 S-box (~65 ms).
     This script forces the class flag once after a throwaway build.
  2. __KEY_SCHEDULE is a CLASS-level dict shared by all instances: constructing a
     second IceKey silently overwrites the first one's schedule. The script
     therefore constructs one key and immediately uses it before the next build.

Run:  python3 tools/ice_cipher_sweep.py
"""
import base64, hashlib, importlib.util, itertools, os, re, sys, time
sys.path.insert(0, os.path.expanduser("~/ICECipher"))
from ICECipher import IceKey

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

spec = importlib.util.spec_from_file_location("oracle", ROOT + "/tools/oracle.py")
o = importlib.util.module_from_spec(spec); spec.loader.exec_module(o)

SMALL = base64.b64decode("".join(re.findall(r'"([^"]+)"',
        re.search(r"BLOB_B64 = \((.*?)\)", open(ROOT+"/tools/oracle.py").read(), re.S).group(1))))
PHASE2 = base64.b64decode("".join(re.findall(r'"([^"]+)"',
        re.search(r"PHASE2_BLOB_B64 = \((.*?)\)", open(ROOT+"/tools/oracle.py").read(), re.S).group(1))))
DUALITE = open(ROOT + "/data/cosmic_duality_blob_2020.bin", "rb").read()
assert SMALL[:8]==b"Salted__" and PHASE2[:8]==b"Salted__" and DUALITE[:8]==b"Salted__"

TARGETS = {
    "small_96": SMALL, "small_ct80": SMALL[16:],
    "phase2_672": PHASE2, "phase2_ct656": PHASE2[16:],
    "dualite_1344": DUALITE, "dualite_ct1328": DUALITE[16:],
}

SEEDS = [
    "matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
    "matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist",
    "causality", "keymakers",
    "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
    "4447f552c0f76528be4df75028a3ecdb3878bccd46acb4b3fabe6442304fd9c4",
    "GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe", "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa",
    "salphaselon", "salphaseion", "cosmicduality", "SalPhaseIon", "CosmicDuality",
    "theseedisplanted", "followthewhiterabbit", "thematrixhasyou",
    "thematrashasyou", "openlocking", "fubcd", "oracle", "thingky", "mvps",
    "FUBCDORA.LETHINGKYMVPS.JQZXW",
    "a fubcd-king & oracle-queen, thingky mvps, on a sad board but as wide as the first one seen",
    "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE",
    "beautiful", "beaufort", "choiceisanillusion", "hushhush", "hush",
    "half", "betterhalf", "wise", "hundredfourty", "theoraclequeen",
    "btcseed", "dbbib", "faed", "dualite", "unicorn", "thesedisplanted",
]
RAW_SEEDS = [
    bytes.fromhex("a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735"),
]

def keys8n(seed: bytes):
    out = []
    h256, h512, md5 = hashlib.sha256(seed).digest(), hashlib.sha512(seed).digest(), hashlib.md5(seed).digest()
    for raw in (h256, h512, md5, seed):
        for n, L in ((0,8),(2,16),(4,32)):
            if len(raw) >= L:
                out.append((n, raw[:L]))
    return out

def detect(pt: bytes):
    hits = []
    i = pt.find(b"Salted__")
    if i >= 0:
        hits.append(f"SALTED_AT_{i}")
    if re.match(rb"[5KL][1-9A-HJ-NP-Za-km-z]{50,51}$", pt.strip()):
        hits.append("WIF")
    if b"-----BEGIN" in pt:
        hits.append("PEM")
    if len(pt) >= 24:
        ratio = sum(32 <= c < 127 or c in (9,10,13) for c in pt) / len(pt)
        if ratio >= 0.95:
            hits.append("PRINTABLE")
    return hits

# WITNESS: encrypt a synthetic envelope through the same path
wkey = keys8n(b"matrixsumlist")[0]
syn = b"Salted__" + bytes(8) + b"A"*80
enc = IceKey(wkey[0], wkey[1]).Encrypt(syn)
dec = IceKey(wkey[0], wkey[1]).Decrypt(enc)
w_ok = detect(dec) == ["SALTED_AT_0"]
print(f"WITNESS synthetic envelope round-trip detect: {'PASS' if w_ok else 'FAIL'}")
assert w_ok

# patch: IceKey sets __bIsInitializedSBOX as an INSTANCE attr, so every
# construction rebuilds the 4x1024 S-box (~65ms). Force the class flag once.
IceKey(0, b'\x00'*8)
setattr(IceKey, '_IceKey__bIsInitializedSBOX', True)

cands = []
counts = {"SALTED":0, "WIF":0, "PEM":0, "PRINTABLE":0}
t0 = time.time()
keysets = [keys8n(s.encode()) for s in SEEDS] + [keys8n(s) for s in RAW_SEEDS]
uniq = {}
for ks in keysets:
    for n, k in ks:
        uniq[(n, k)] = True
uniq_keys = list(uniq)
print(f"unique keys: {len(uniq_keys)}  targets: {len(TARGETS)}")
N = len(uniq_keys) * len(TARGETS)
done = 0
t_start = time.time()
for (n, k) in uniq_keys:
    ice = IceKey(n, k)  # construct once per key; use immediately (class-shared schedule)
    for tname, blob in TARGETS.items():
        pt = ice.Decrypt(blob)
        for h in detect(pt):
            if h.startswith("SALTED"): counts["SALTED"] += 1
            else: counts[h] += 1
            if h == "PRINTABLE":
                s = pt.strip()
                if 4 <= len(s) <= 300:
                    cands.append((tname, s.decode("ascii", "ignore")))
            elif h in ("WIF","PEM"):
                cands.append((tname, pt.decode("ascii","ignore")))
            elif h.startswith("SALTED"):
                cands.append((tname, f"<inner-envelope:{tname}:{h}>"))
    done += 1
    if done % 50 == 0:
        print(f"  progress {done}/{len(uniq_keys)} keys ({time.time()-t_start:.1f}s)", flush=True)
dt = time.time() - t0
print(f"trials: {N}  time: {dt:.1f}s  rate: {N/dt:.1f}/s")
print("counts:", counts)

# printable candidates -> oracle
seen = set(); lines = []
for tname, s in cands:
    if s not in seen:
        seen.add(s); lines.append(s)
print(f"unique candidates for oracle: {len(lines)}")
if lines:
    import subprocess
    r = subprocess.run([sys.executable, ROOT+"/tools/oracle.py", "--stdin"],
                       input="\n".join(lines), capture_output=True, text=True)
    out = r.stdout + r.stderr
    print("oracle out:", out[:2000])
