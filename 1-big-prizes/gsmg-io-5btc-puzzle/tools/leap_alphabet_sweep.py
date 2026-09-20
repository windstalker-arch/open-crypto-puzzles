#!/usr/bin/env python3
"""leap_alphabet_sweep.py -- the interpreter-alphabet leap.

The 3.2.2 precedent (leads.md note 1) fixes the checkerboard alphabet as the dedupe
of a full SENTENCE, not a keyword: "A fubcd-king & oracle-queen, thingky mvps, on a
sad board but as wide as the first one seen". Every prior sweep keyed the board with
page-literal KEYWORDS (joint_sweep_91, fresh_alpha_sweep, titlekw_checkerboard,
pageread_vic_sweep). This sweep uses SENTENCE-LEVEL alphabet sources never used as a
keyed time alphabet: the final-page instruction line, the "first hint" content and its
2023-02-23 poem, the phase-3.2 "first clue" (matrix line), the 3.2.2 hint sentence,
the inner-blob hint, earlier-phase full answers, and the 7-password chain joins.

Pipeline is the certified one (tools/certified_vic.py: build_grid/decode, digit-level
columnar transposition, over-encryption), exactly as joint_sweep_91.py. Any clean
(?-free) decode is pushed as an answer-form candidate to both funded-gate oracles.

Control alphabets (phase322, bifid_row) ride along: they must still decode to their
known outputs (pipeline witness), but their oracle results are expected negatives
(they are already in tested.md).

Public/authorized puzzle only. A hit is an oracle MATCH.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from certified_vic import ALPHA, CANON, POS, build_grid, decode

OGDIR = os.path.expanduser("~")
DATA = os.path.join(ROOT, "data", "finalpage-digit-streams.json")
d = json.loads(Path(DATA).read_text())

FAED = d["faed_570"].rstrip("z")
DBBI69 = d["dbbib"]                                   # image-verified 69 tokens (3x23)
DBBI91 = Path(os.path.join(OGDIR, "tmp", "grid_dbbib.txt")).read_text().strip()  # live 91
assert len(DBBI69) == 69, len(DBBI69)
assert len(DBBI91) == 91, len(DBBI91)
assert len(FAED) == 570, len(FAED)

SCRATCH = os.path.join(OGDIR, "tmp", "leap_cands.txt")


def keyed28(keyword):
    kw = "".join(ch for ch in keyword.upper() if ch.isalpha())
    out = ""
    for ch in kw + ALPHA:
        if ch not in out:
            out += ch
    return (out + "./")[:28]


def to_digits(stream, mp):
    return "".join(str(mp[c]) for c in stream if c in mp)


def col_undo(ct, width, key_order):
    n = len(ct)
    nrows = (n + width - 1) // width
    full = n % width if n % width else width
    lens = [nrows if i < full else nrows - 1 for i in range(width)]
    placed = [None] * width
    ptr = 0
    for k in range(width):
        ci = key_order[k]
        placed[ci] = ct[ptr:ptr + lens[ci]]
        ptr += lens[ci]
    out = []
    for r in range(nrows):
        for c in range(width):
            if r < len(placed[c]):
                out.append(placed[c][r])
    return "".join(out)


def over_undo(ds, ks, M):
    return "".join(str((int(ch) - ks[i % len(ks)]) % M) for i, ch in enumerate(ds))


def score(pt):
    pl = re.sub(r"[^a-zA-Z]", " ", pt).lower()
    toks = pl.split()
    if not toks:
        return -1e9
    G = {"e":12.7,"t":9.1,"a":8.2,"o":7.5,"i":7.0,"n":6.7,"s":6.3,"h":6.1,"r":6.0,
         "d":4.3,"l":4.0,"c":2.8,"u":2.8,"m":2.4,"w":2.4,"f":2.2,"g":2.0,"y":2.0,
         "p":1.9,"b":1.5,"v":1.0,"k":0.8}
    COMMON = {"the","and","you","that","this","with","not","have","from","they","your",
              "half","better","enter","password","matrix","sumlist","last","words",
              "before","archi","choice","key","private","cosmic","duality","salphas",
              "seed","funded","sender","answer","command","first","hint","yourlast",
              "case","manage","crack","belong","need","funds","live","shabe","second",
              "white","blue","rose","roses","yellow","prime","yinyang","wake","rabbit",
              "crybaby","zeroed","stakes","chance","winning","fubcd","oracle","queen",
              "thingky","mvps","board","wide","clue","order","keys","flower",
              "concrete","surface","causality","uncertainty","principle","warning","logic"}
    ug = sum(0.01 * G.get(ch, 0) for ch in pl.replace(" ", ""))
    w = sum(5.0 + len(t) for t in toks if t in COMMON)
    q = pt.count("?")
    return ug + w - q * 2.0


# ---- novel SENTENCE-level alphabet sources (never keyed before) ----
alphas = {
    # final-page instruction line
    "ourfirsthintisyourlastcommand": "OURFIRSTHINTISYOURLASTCOMMAND",
    "firsthintisyourlastcommand": "FIRSTHINTISYOURLASTCOMMAND",
    "yourlastcommand": "YOURLASTCOMMAND",
    "thefirsthintisyourlastcommand": "THEFIRSTHINTISYOURLASTCOMMAND",
    "ourfirsthintisyourlastcommandandsecondanswer":
        "OURFIRSTHINTISYOURLASTCOMMANDANDSECONDANSWER",
    "firsthintisyourlastcommandandsecondanswer":
        "FIRSTHINTISYOURLASTCOMMANDANDSECONDANSWER",
    "yourlastcommandandsecondanswer": "YOURLASTCOMMANDANDSECONDANSWER",
    # "the first hint" = the first puzzle page / slug
    "gsmgio5btcpuzzlechallenge1gsmg1jc9wtdswfwapgjxcmjpawx7prbe":
        "GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9WTDSWFWAPGJXCMJPAWX7PRBE",
    "gsmgio5btcpuzzlechallenge": "GSMGIO5BTCPUZZLECHALLENGE",
    "gsmgiothesesedisplanted": "GSMGIOTHESEEDISPLANTED",
    "hashthetext": "HASHTHETEXT",
    "thefirstpuzzlepiece": "THEFIRSTPUZZLEPIECE",
    "gobacktothefirstpuzzlepiece": "GOBACKTOTHEFIRSTPUZZLEPIECE",
    "gsmgiothefirstpuzzlepiece": "GSMGIOTHEFIRSTPUZZLEPIECE",
    # phase-3.2 "first clue" (matrix line)
    "thefirstclueamtherewakeupyou": "THEFIRSTCLUEAMTHEREWAKEUPYOU",
    "amtherewakeupyou": "AMTHEREWAKEUPYOU",
    "thematrixhasyou": "THEMATRIXHASYOU",
    "wakeupyouthematrixhasyou": "WAKEUPYOUTHEMATRIXHASYOU",
    "amtherewakeupyouthematrixhasyou": "AMTHEREWAKEUPYOUTHEMATRIXHASYOU",
    # author first-hint poem (2023-02-23)
    "rosesarewhitebutoftenred": "ROSESAREWHITEBUTOFTENRED",
    "yellowhasanumberandsodoesblue": "YELLOWHASANUMBERANDSODOESBLUE",
    "rosesarewhitebutoftenredyellowhasanumberandsodoesblue":
        "ROSESAREWHITEBUTOFTENREDYELLOWHASANUMBERANDSODOESBLUE",
    "gobacktothefirstpuzzlepiecewithou": "GOBACKTOTHEFIRSTPUZZLEPIECEWIT",
    "rosesarewhitebutoftenredgobacktothefirstpuzzlepiece":
        "ROSESAREWHITEBUTOFTENREDGOBACKTOTHEFIRSTPUZZLEPIECE",
    # 3.2.2 hint sentence (the alphabet-construction precedent itself)
    "aswideasthefirstonesseen": "ASWIDEASTHEFIRSTONESSEEN",
    "thefirstonesseen": "THEFIRSTONESSEEN",
    "onasadboardbutaswideasthefirstonesseen":
        "ONASADBOARDBUTASWIDEASTHEFIRSTONESSEEN",
    "afubcdkingandoraclequeenthingkymvpsonasadboardbutaswideasthefirstonesseen":
        "AFUBCDKINGANDORACLEQUEENTHINGKYMVPSONASADBOARDBUTASWIDEASTHEFIRSTONESSEEN",
    # inner-blob instruction phrases
    "raisingthestakeswithoutextrachancesofwinning":
        "RAISINGTHESTAKESWITHOUTEXTRACHANCESOFWINNING",
    "withoutextrachancesofwinning": "WITHOUTEXTRACHANCESOFWINNING",
    "incaseyoumanagetocrackthis": "INCASEYOUMANAGETOCRACKTHIS",
    "incaseyoumanagetocrackthisthenyouwillknowthatthesefactsareyours":
        "INCASEYOUMANAGETOCRACKTHISTHENYOUWILLKNOWTHATTHESEFACTSAREYOURS",
    "theprivatekeysbelongtohalfandbetterhalf":
        "THEPRIVATEKEYSBELONGTOHALFANDBETTERHALF",
    "halfandbetterhalftogether": "HALFANDBETTERHALFTOGETHER",
    # earlier-phase full answers
    "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple":
        "JACQUEFRESCOGIVEITJUSTONESECONDHEISENBERGSUNCERTAINTYPRINCIPLE",
    "causalitysafemetluna": "CAUSALITYSAFENETLUNA",
    "oneforonefourforone": "ONEFORONEFOURFORONE",
    "ibmexcedictransformer": "IBMEXCEDICTRANSFORMER",
    "thewarningbylogic": "THEWARNINGBYLOGIC",
    # 7-password chain joins
    "matrixsumlistenterlastwordsbeforearchichoicethispassword":
        "MATRIXSUMLISTENTERLASTWORDSBEFOREARCHICHOICETHISPASSWORD",
    "matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist":
        "MATRIXSUMLISTENTERLASTWORDSBEFOREARCHICHOICETHISPASSWORDMATRIXSUMLIST",
    "matrixsumlistyourlastcommandsecondanswer":
        "MATRIXSUMLISTYOURLASTCOMMANDSECONDANSWER",
    "enterlastwordsbeforearchichoicethispassword":
        "ENTERLASTWORDSBEFOREARCHICHOICETHISPASSWORD",
    # author's own whisper words
    "someneedstobezeroedout": "SOMENEEDSTOBEZEROEDOUT",
    "yinyangoppositesattract": "YINYANGOPPOSITESATTRACT",
    # controls (already swept) -- pipeline witness only
    "control_phase322": "FUBCDORA.LETHINGKYMVPS.JQZXW",
    "control_bifid_row": "DBIFHCEGAKLMNOPQRSTUVWXYZ",
}
ALPHAS = {k: keyed28(v) for k, v in alphas.items()}
ALPHAS["control_phase322"] = alphas["control_phase322"]  # keep the certified literal

TRANS_WIDTHS = {
    "none": 0,
    "matrixsumlist13": 13,
    "lastwords26": 26,
    "enter5": 5,
    "tw12": 12,
    "tw23": 23,
    "seedplanted17": 17,
    "your4": 4,
    "command7": 7,
    "shabefour9": 9,
    "thefirstoneseen15": 15,
    "yourlastcommand16": 16,
    "firsthintline31": 31,
    "ourfirsthintline36": 36,
    "board38": 38,
}

# phases that get a sha256-based over-encryption key (mod 9 and mod 10)
OE_PHRASES = [
    "matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
    "salphaseion", "salphaselon", "cosmicduality", "causality", "yinyang",
    "btcseed", "yourlastcommand", "secondanswer", "shabefour",
    "ourfirsthintisyourlastcommand", "thefirsthintisyourlastcommand",
    "gsmgio5btcpuzzlechallenge", "thematrixhasyou",
    "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
    "theflowerblossomsthroughwhatseemstobeaconcretesurface",
    "raisingthestakeswithoutextrachancesofwinning",
    "rosesarewhitebutoftenredyellowhasanumberandsodoesblue",
    "matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist",
]
OE_KEYS = {}
for name in OE_PHRASES:
    h = hashlib.sha256(name.encode()).hexdigest()
    OE_KEYS[name + "_m9"] = [int(c, 16) % 9 for c in h]
    OE_KEYS[name + "_m10"] = [int(c, 16) % 10 for c in h]
for label, stream in (("dbbi69", DBBI69), ("dbbi91", DBBI91)):
    OE_KEYS[label + "_canon"] = [CANON[c] for c in stream]
    OE_KEYS[label + "_pos"] = [POS[c] for c in stream]
    OE_KEYS[label + "_inv"] = [9 - CANON[c] for c in stream]

MAPPINGS = [("CANON", CANON), ("POS", POS)]
ESCAPES = [(1, 4), (2, 5), (1, 2), (2, 1), (0, 4), (3, 7)]

# payloads: faed is the certified ciphertext; the two dbbi windows ride along as
# controls (interpreted the same way, oracle-tested but expected not to match)
PAYLOADS = [("faed", FAED), ("dbbi69", DBBI69), ("dbbi91", DBBI91)]

WORDS = {"the", "and", "you", "that", "this", "with", "not", "have", "from", "they",
         "your", "half", "better", "enter", "password", "matrix", "sumlist", "last",
         "words", "before", "archi", "choice", "key", "private", "cosmic", "duality",
         "salphas", "seed", "funded", "sender", "answer", "command", "first", "hint",
         "case", "manage", "crack", "belong", "need", "funds", "live", "shabe",
         "second", "white", "blue", "rose", "roses", "yellow", "prime", "yinyang",
         "wake", "rabbit", "crybaby", "zeroed", "stakes", "chance", "winning", "fubcd",
         "oracle", "queen", "thingky", "mvps", "board", "wide", "clue", "order",
         "keys", "flower", "concrete", "surface", "causality", "uncertainty",
         "principle", "warning", "logic"}


def main():
    t0 = time.time()
    # cache the digit-level (over-encryption + transposition) stages so each is
    # computed once per (payload, map, oe, tw) instead of once per (alpha, escape)
    ctol_cache = {}
    totals = {"forms": 0, "interesting": 0, "clean": 0}
    results = []
    for pname, payload in PAYLOADS:
        for mpname, mp in MAPPINGS:
            ds = to_digits(payload, mp)
            for oe_name, oe_key in OE_KEYS.items():
                M = 9 if "_m9" in oe_name or oe_name.endswith(("_canon", "_pos", "_inv")) else 10
                ds2o = over_undo(ds, oe_key, M)
                for tname, tw in TRANS_WIDTHS.items():
                    if tw == 0:
                        ds2 = ds2o
                    else:
                        order = sorted(range(tw), key=lambda i: (oe_key[i % len(oe_key)], i))
                        ds2 = col_undo(ds2o, tw, order)
                    for aname, alpha28 in ALPHAS.items():
                        for (e1, e2) in ESCAPES:
                            totals["forms"] += 1
                            key = (alpha28, e1, e2)
                            ctol = ctol_cache.get(key)
                            if ctol is None:
                                ctol = build_grid(alpha28, e1, e2)
                                ctol_cache[key] = ctol
                            pt = decode(ds2, ctol, e1, e2)
                            sc = score(pt)
                            wf = [w for w in re.sub(r"[^a-zA-Z]", " ", pt).lower().split()
                                  if w in WORDS]
                            if sc > 25 or wf:
                                totals["interesting"] += 1
                                results.append((sc, aname, mpname, e1, e2, pname,
                                                tname, oe_name, pt, wf))
    print(f"[leap] tested {totals['forms']} decode forms in {time.time()-t0:.0f}s; "
          f"interesting {totals['interesting']}", flush=True)

    cands = set()
    for sc, aname, mpname, e1, e2, pname, tname, oe_name, pt, wf in results:
        if "?" not in pt and 8 <= len(pt) <= 2000:
            totals["clean"] += 1
            cands.add(pt)
            cands.add(pt.lower())
            cands.add(pt.upper())
            cands.add(pt[::-1])
    with open(SCRATCH, "w") as f:
        f.writelines(c + "\n" for c in sorted(cands))
    print(f"[leap] clean decodes {totals['clean']}; unique answer-forms "
          f"{len(cands)} -> {SCRATCH}", flush=True)
    print(f"[leap] gen done {time.time()-t0:.0f}s", flush=True)


def run_oracle(gate):
    oracle = os.path.join(ROOT, "tools", "oracle.py" if gate == "small" else "oracle_dualite.py")
    r = subprocess.run([sys.executable, oracle, "--stdin"],
                       input=Path(SCRATCH).read_bytes(), capture_output=True)
    out = r.stdout.decode()
    lines = [ln for ln in out.splitlines() if ln.strip()]
    hits = [ln for ln in lines if ln.startswith("MATCH")]
    print(f"[leap][{gate}] oracle lines={len(lines)} MATCH={len(hits)}", flush=True)
    for h in hits[:10]:
        print("  HIT:", h, flush=True)
    return len(hits)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "oracle":
        gate = sys.argv[2] if len(sys.argv) > 2 else "small"
        sys.exit(0 if run_oracle(gate) else 1)
    main()