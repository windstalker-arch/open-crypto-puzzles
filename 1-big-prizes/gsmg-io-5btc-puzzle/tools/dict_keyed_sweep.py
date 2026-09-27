import json, os, sys, time, re
from pathlib import Path
sys.path.insert(0, "tools")
from certified_vic import build_grid, decode, keyed28, CANON, POS
from oracle import attempt as att_small
from oracle_dualite import attempt as att_dual, load_dualite_b64

WORDS = Path(os.environ.get("GSMG_WORDLIST", "~/briefcase/english-words/words_alpha.txt")).expanduser()
D = json.loads(Path("data/finalpage-digit-streams.json").read_text())
streams = {"dbbib": D["dbbib_91"].rstrip("z"), "faed": D["faed_570"].rstrip("z")}
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0

words = [w.strip().upper() for w in WORDS.read_text().splitlines() if 4 <= len(w.strip()) <= 18]
words = list(dict.fromkeys(words))[:limit] if limit else list(dict.fromkeys(words))

blob = load_dualite_b64()
seen_keyed = set(); n = clean = tries = 0; t0 = time.time()
fname = os.environ.get("GSMG_SWEEP_OUT", "/tmp/dict_sweep.txt")
with open(fname, "w") as f:
    for kw in words:
        k26 = keyed28(kw, (".", "/"))
        if k26 in seen_keyed: continue
        seen_keyed.add(k26)
        alpha = k26[:8] + "." + k26[8:18] + "/" + k26[18:]
        for e1, e2 in ((1, 4), (4, 1)):
            grid = build_grid(alpha, e1, e2)
            for name, stream in streams.items():
                for Mm in (CANON, POS):
                    dig = "".join(str(Mm[ch]) for ch in stream if ch in Mm)
                out = decode(dig, grid, e1, e2)
                n += 1
                if "?" in out: continue
                clean += 1
                for c in {out, out.lower(), out.upper()}:
                    tries += 1
                    h1, _ = att_small(c)
                    if h1:
                        f.write(f"SMALL MATCH key={kw} name={name} out={out[:120]}\n"); f.flush()
                    h2, _ = att_dual(c, blob)
                    if h2:
                        f.write(f"DUALITE MATCH key={kw} name={name} out={out[:120]}\n"); f.flush()
print(f"words={len(words)} swapped_keyed={len(seen_keyed)} decodes={n} clean={clean} oracle_tries={tries} done in {time.time()-t0:.0f}s -> {n/(time.time()-t0):.0f} decodes/s results={fname}")