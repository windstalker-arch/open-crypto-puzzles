import json, sys, time
sys.path.insert(0, "tools")
sys.path.insert(0, ".")
from oracle import attempt as a_small
import oracle_dualite as od
from pycipher import Beaufort

blob = od.load_dualite_b64()
d = json.load(open("data/finalpage-digit-streams.json"))
DB = d["dbbib_91"]
FA = d["faed_570"].rstrip("z")

kws = [
    "LASTWORDSBEFOREARCHICHOICE", "ENTER", "FIRSTHINT", "LASTCOMMAND",
    "BTCSEEDONESIGNKEY", "HALF", "HALFANDSETTERHALF", "MATRIXSUMMLIST",
    "THISPASSWORD", "FIRSTHINTISLASTCOMMAND", "THEGREENINGKEEPSHOUROCKSAMPLING",
    "ARCHICHOICE",
]

cands = {}
for kw in kws:
    for kwv in {kw, kw.lower(), kw.replace(" ", "")}:
        if kwv == "":
            continue
        for sn, st in (("dbbib_91", DB), ("faed_570", FA)):
            for enc in (True, False):
                try:
                    out = Beaufort(kwv).encipher(st) if enc else Beaufort(kwv).decipher(st)
                except Exception:
                    continue
                for form in {out, out.lower(), out.replace(" ", "")}:
                    cands.setdefault(form, ("beaufort-xcheck", kwv[:18], sn, "enc" if enc else "dec"))

N = len(cands)
hl = []
hu = []
t0 = time.time()
for x, p in list(cands.items()):
    mk, _ = a_small(x)
    nk, _ = od.attempt(x, blob)
    if mk:
        hl.append((x, p))
    if nk:
        hu.append((x, p))
dt = time.time() - t0
print(f"N={N} x2 gates (independent pycipher Beaufort cross-check), t={dt:.1f}s")
print("SMALL:", hl)
print("DUALITE:", hu)