import json, sys, re
from pathlib import Path
sys.path.insert(0, "tools")
from certified_vic import build_grid, decode, keyed28, CANON, POS, DBBIB, FAED

D = json.loads(Path("data/finalpage-digit-streams.json").read_text())
dbbib = D["dbbib_91"].rstrip("z")
faed = D["faed_570"].rstrip("z")

WORDS = set(Path("/data/data/com.termux/files/home/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle/tools/english_top.txt").read_text().split()) if Path("/data/data/com.termux/files/home/open-crypto-puzzles/1-big-prizes/gsmg-io-5btc-puzzle/tools/english_top.txt").exists() else None

G1 = ["WHITERABBIT", "THESEEDISPLANTED", "ALICE", "NOSTALGIC", "CHILDHOOD",
      "THEARCHITECTCHOICE", "COSMICDUALITY", "YINYANG", "YELLOWBLUE", "PRIMES",
      "ENTER", "MATRIXSUMLIST", "LASTWORDSBEFOREARCHICHOICE", "THISPASSWORD"]
G2 = ["YELLOWBLUEPRIMES", "COSMICDUALITYYINYANG", "MATRIXSUMLISTENTER",
      "PRIMESMATRIXSUMLIST", "YINYANGYELLOWBLUE", "HOPEISTHEQUINTESSENTIALHUMANDELUSION"]
G3 = ["QWERTYUIOPASDFGHJKLZXCVBNM", "Dvorak", "Colemak", "AZERTYUIOPQSDFGHJKLMWXCVBN",
      "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "BACDEFGHIJKLMNOPQRSTUVWXYZ"]
seeds = G1 + G2 + G3

def score_words(t):
    if not WORDS: return 0
    toks = re.split(r"[^a-z]+", t.lower())
    return sum(1 for w in toks if len(w) > 2 and w in WORDS)

def clean(t):
    return "?" not in t and len(re.sub(r"[^A-Za-z]", "", t)) > 0

res = []
for kw in seeds:
    for M in (CANON, POS):
        mname = "CANON" if M is CANON else "POS"
        for e1, e2 in ((1, 4), (4, 1)):
            key = keyed28(kw, (".", "/"))
            alpha = key[:8] + "." + key[8:18] + "/" + key[18:]
            grid = build_grid(alpha, e1, e2)
            for name, stream in (("dbbib", dbbib), ("faed", faed)):
                dig = "".join(str(M[ch]) for ch in stream if ch in M)
                out = decode(dig, grid, e1, e2)
                if not clean(out): continue
                res.append((score_words(out), len(out), kw, mname, (e1, e2), name, out))

res.sort(key=lambda r: (-r[0], -len(res)))
seen = set()
n = 0
for score, ln, kw, mname, esc, name, out in res:
    h = out[:1] if len(out) < 60 else out[:60]
    if (name, h) in seen: continue
    seen.add((name, h))
    n += 1
    if n > 26: break
    print(f"[{name}] pair={score} esc={esc} {mname} key={kw}")
    print("   ", out[:160])