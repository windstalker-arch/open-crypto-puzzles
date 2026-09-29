#!/usr/bin/env python3
"""third_door_colors.py -- the creator's 2020-01-14 colour rule read on a
NON-TEXTUAL object, against the third door.

WHY THIS TOOL EXISTS. `analysis/tested.md` row R-THIRDDOOR-AUDIO-2026-09-28
ends the third door's remaining directions as: "a rule the creator gave
between the January 2020 poem and the April 2020 audio hint ('Yellow has a
number and so does Blue', 'primes', 'zeroed out') read on a non-textual
object, or - with noise acceptable - a GPU brainwallet pass, which this device
cannot do." The second branch is closed twice over (R-BRAINWALLET-3D closes the
family directly, 84 derivations 0 MATCH, and the 149-digit preimage space is
~10^149, so t = N/D is not a number). So the first branch is the whole of what
is left, and it had never been run on the third door.

THE GAP. The colour-bearing non-textual objects in this puzzle were measured
from pixels and certified in the ledger, and every reading of them was fed to
the two funded AES GATES -- the small blob and the dualite -- via
`tools/oracle.py` / `tools/oracle_dualite.py`:

  * late-83/84/86/86b/90/93/193/201 -- the SalPhaseIon bottom band and the 8-tile
    second band, as class-run strings, hex literals, spelled colour names, colour
    initials, binary and keyed-alphabet cells. All 12-or-fewer-candidate closed
    sets, all negative, all on the GATES.
  * sections 121/122/123 -- the /theseedisplanted 8-tile sticker strip: 483,840
    permutations, ~118 transforms, the colour-count mask (1 black + 3 blue +
    4 red), letter-class sieves and the layered-construction keys. All on the
    GATES.
  * section 19b -- the 14x14 phase-1 matrix: 12 colour masks in 5 reading orders
    as 196/192 bits plus the yellow and blue cells' indices, sums, counts and
    prime-rank characters (1,300 candidates). This one DID target the third door.

So the two sticker/band objects were read only as GATE PASSWORDS, and the
prime / zeroed-out rules were applied to the phase-1 matrix but never to the
sticker strip or the colour bands. `tools/third_door.py` (shipped 2026-09-28)
made the third door testable at all, and it has been run once, on the audio
family. This tool runs it on the colour family, importing its six constructions
and its target set rather than re-deriving them, so every number below is
produced by certified code.

WHAT IS *NOT* REOPENED. The sticker TEXT lead stays killed. R-4E-PROV-2026-09-26
showed the reassembly `warningunlockwalletlockIOgicCAnyou+dig-it` is a
solver-group annotation and not creator text, and R-TILESTRUCT-2026-09-28 fixed
the strip's geometry without reopening it. Nothing here re-reads the stickers'
letters: this tool only ever uses per-tile COLOUR classes and counts, which are
PIL-certified, plus the two numbers the author's hint asks for.

THE OBJECTS (parsed from the certified artifacts at run time, never retyped):

  band46  46 tiles, the SalPhaseIon bottom strip      analysis/sticker_color_order/bottom_band_l2r.txt
  band8    8 tiles, the strip just above it          same file, second band
  bot13   13 tiles, the BOT-sticker row              analysis/sticker_bands_color.txt
  sec8     8 tiles, the SECOND row                   same file
  strip8   8 cells, black/blue/red, two groups of 4  R-TILESTRUCT-2026-09-28 (colours only)
  matrix   the author's own two numbers, 9 / 15      leads.md note 22 (cross-check cell)

Class letters are the artifacts' own: R red, O orange, Y yellow, C cyan, B blue,
b deep-blue, G green, '-' a run too short to certify. K is used here for the
R-TILESTRUCT black cell so that K/black never collides with b/deep-blue.

THE RULES, one family per reading:

  counts   "Yellow has a number and so does Blue" -- the number each colour HAS
  primes   "primes" -- the tiles at prime ranks, and their complement
  zeroed   "some characters need to be zeroed out" -- the run with the
           non-prime ranks replaced by '0' or NUL, and with the prime ranks zeroed
  indices  the tile NUMBERS at prime ranks, four joins
  cmap     the class->number map R1 O2 Y3 C4 B5 b6 G7, '-'->0, as text, as
           a1z26, as raw bytes (every value is < 32, so this is the one family
           that can be a RAW key), and spaced
  pairs    the (yellow, blue) count pair of whichever object has both, in
           spelled, joined, ordered and a1z26 forms
  bound    the hint words themselves with those numbers, the colour word joined
           to the count it has

Every candidate goes through all six constructions of `third_door.constructions`
in both pubkey forms, against the third door, the other 8 planted addresses and
both funded gates. A MATCH is printed with its preimage and derivation and the
run exits 1.

WITNESS. `third_door.selftest()` (5 CSV-verified rows re-derived) must pass rc=0
before the battery and again after it, and the battery additionally re-derives
those same 5 known preimages through its own loop in-process, so the candidate
path itself -- not just the imported functions -- is witnessed. Both gates'
selftests are run by the caller.

Local only. Every address compared is already public in
`data/planted-addresses.csv` or the README gate table. No key is swept, no
transaction is built, nothing is broadcast.
"""
from __future__ import annotations

import argparse
import re
import sys
import time

import third_door as TD

BASE_DIR = TD.BASE
BAND_FILE = f"{BASE_DIR}/analysis/sticker_color_order/bottom_band_l2r.txt"
BANDS_FILE = f"{BASE_DIR}/analysis/sticker_bands_color.txt"

# class -> number, in the order the artifact's own legend lists the classes
CMAP = {"R": 1, "O": 2, "Y": 3, "C": 4, "B": 5, "b": 6, "G": 7, "-": 0, "K": 0}
PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43}


def isprime(n: int) -> bool:
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


def load_objects() -> dict[str, str]:
    """Parse the certified colour runs straight out of the artifacts."""
    objs: dict[str, str] = {}

    band = [l.strip() for l in open(BAND_FILE)
            if l.strip() and not l.startswith("#")]
    assert len(band) == 2, band
    objs["band46"] = band[0]
    objs["band8"] = band[1]

    runs = []
    for line in open(BANDS_FILE):
        m = re.findall(r"\(\s*\d+\s*,\s*\d+\s*\)\s*([A-Za-z])", line)
        if m:
            runs.append("".join(m))
    assert len(runs) == 2, runs
    objs["bot13"] = runs[0]
    objs["sec8"] = runs[1]

    # R-TILESTRUCT-2026-09-28: 8 cells, colours 1 black + 3 blue + 4 red,
    # split by ONE 32px break into two groups of four. Colours only.
    objs["strip8"] = "KBBBRRRR"
    return objs


def certified_runs() -> list[tuple[str, str]]:
    """(label, run) straight from the artifacts, as a report line."""
    return [(k, v) for k, v in load_objects().items()]


def counts(run: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for ch in run:
        out[ch] = out.get(ch, 0) + 1
    return out


def a1z26(s: str) -> str:
    return "".join(chr(96 + int(c)) for c in s if c.isdigit() and int(c) <= 26)


def candidates(run: str, name: str) -> list[tuple[str, bytes]]:
    """Every reading of one colour object under the three hint rules."""
    out: list[tuple[str, bytes]] = []
    seen: set[bytes] = set()

    def add(tag: str, v) -> None:
        if isinstance(v, int):
            v = str(v)
        if isinstance(v, str):
            v = v.encode()
        if v and v not in seen:
            seen.add(v)
            out.append((f"{name}/{tag}", v))

    n = len(run)
    cs = counts(run)
    # '-' is an uncertified run, NOT a tile. Ranks, prime positions and tile
    # indices are therefore taken over the CERTIFIED TILES ONLY; the dashed
    # string is carried separately in the zeroed-out family, where an
    # uncertified run reads as a character that had to be zeroed out.
    tiles = [c for c in run if c != "-"]
    nc = counts(tiles)
    cells = "".join(tiles)
    m = len(cells)

    # --- counts: the number each colour HAS
    for c, k in sorted(nc.items()):
        add(f"counts/{c}{k}", f"{c}{k}")
        add(f"counts/{c}{k}-lower", f"{c}{k}".lower())
        add(f"counts/number-of-{c}", k)
    add("counts/concat-class-order",
        "".join(f"{c}{nc[c]}" for c in sorted(nc)))
    add("counts/concat-numbers-class-order", "".join(str(nc[c]) for c in sorted(nc)))
    add("counts/prime-count-classes",
        "".join(c for c in sorted(nc) if isprime(nc[c])))
    add("counts/composite-count-classes",
        "".join(c for c in sorted(nc) if not isprime(nc[c])))
    add("counts/n-tiles", n)
    add("counts/n-certified", len(tiles))
    add("counts/n-uncertified-runs", n - m)
    add("counts/has-a-number", f"{name}{m}")
    # the number each colour HAS, read as a letter (a1z26) and as a run-length
    add("counts/a1z26-per-class",
        "".join(chr(96 + nc[c]) for c in sorted(nc) if 1 <= nc[c] <= 26))
    add("counts/runs-classes",
        "".join(f"{c}{nc[c]}" for c in sorted(nc)))
    add("counts/blue-merged",
        f"B{nc.get('B', 0) + nc.get('b', 0)}R{nc.get('R', 0)}"
        + (f"O{nc.get('O', 0)}" if "O" in nc else ""))
    # the colour's OWN number: the alphabet position of the colour word's first
    # letter, R=18 O=15 Y=25 C=3 B=2 G=7 K=11. All are < 32, so the byte
    # reading is a legal RAW key as well.
    alpha = "".join(str(ord(_colour_word(c)[0].upper()) - 64) for c in cells)
    add("cmap/alpha-digits", alpha)
    add("cmap/alpha-a1z26", a1z26(alpha))
    add("cmap/alpha-bytes", bytes(int(x) for x in alpha))
    add("cmap/alpha-cells-bytes-rev",
        bytes(int(x) for x in alpha[::-1]))
    add("cmap/alpha-dashed-digits",
        "".join(str(ord(_colour_word(c)[0].upper()) - 64) if c != "-" else "0"
                for c in run))

    # --- primes: the tiles at prime ranks (0- and 1-based) and the complement
    for base in (0, 1):
        idx = {i for i in range(m) if isprime(i + base)}
        keep = "".join(cells[i] for i in sorted(idx))
        drop = "".join(cells[i] for i in range(m) if i not in idx)
        add(f"primes/keep-base{base}", keep)
        add(f"primes/drop-base{base}", drop)
        add(f"primes/keep-base{base}-reversed", keep[::-1])

    # --- zeroed out: the run with the non-prime ranks zeroed, and vice versa
    for base in (0, 1):
        idx = {i for i in range(m) if isprime(i + base)}
        for fill, tag in ((b"0", "char0"), (b"\x00", "nul")):
            add(f"zeroed/nonprime-{tag}-base{base}",
                bytes(cells[i].encode()[0] if i in idx else fill[0]
                      for i in range(m)))
            add(f"zeroed/prime-{tag}-base{base}",
                bytes(fill[0] if i in idx else cells[i].encode()[0]
                      for i in range(m)))
        # the same mask on the DASHED string, uncertified runs zeroed out first:
        # the gaps keep the string's geometry and lose their content
        t = ["0" if c == "-" else c for c in run]
        gidx = sorted(i for i, c in enumerate(run) if c != "-"
                      and isprime(i + base))
        add(f"zeroed/dashed-nonprime0-base{base}",
            "".join(t[i] if i in gidx else "0" for i in range(len(run))))
        add(f"zeroed/dashed-prime0-base{base}",
            "".join("0" if i in gidx else t[i] for i in range(len(run))))

    # --- indices: the tile numbers at prime ranks, over CERTIFIED ranks
    for base in (0, 1):
        idx = sorted(i for i in range(m) if isprime(i + base))
        add(f"indices/prime-concat-base{base}", "".join(str(i + base) for i in idx))
        add(f"indices/prime-comma-base{base}", ",".join(str(i + base) for i in idx))
        add(f"indices/prime-space-base{base}", " ".join(str(i + base) for i in idx))
        add(f"indices/prime-pad2-base{base}",
            "".join(f"{i + base:02d}" for i in idx))
        add(f"indices/prime-class-idx-base{base}",
            "".join(f"{cells[i]}{i + base}" for i in idx))

    # --- cmap: the class -> number map, as text / a1z26 / raw bytes / spaced
    digits = "".join(str(CMAP[c]) for c in run)
    cdigits = "".join(str(CMAP[c]) for c in cells)
    add("cmap/digits", digits)
    add("cmap/digits-spaced", " ".join(digits))
    add("cmap/digits-comma", ",".join(digits))
    add("cmap/digits-reversed", digits[::-1])
    add("cmap/a1z26", a1z26(digits))
    add("cmap/bytes", bytes(int(c) for c in digits))
    add("cmap/bytes-reversed", bytes(int(c) for c in digits[::-1]))
    add("cmap/cells-digits", cdigits)
    add("cmap/cells-a1z26", a1z26(cdigits))
    add("cmap/cells-bytes", bytes(int(c) for c in cdigits))
    add("cmap/colour-words", "".join(_colour_word(c) for c in run if c != "-"))
    add("cmap/colour-words-initial",
        "".join(_colour_word(c)[0] for c in run if c != "-"))

    # --- pairs: the (yellow, blue) count pair, where the object has both
    if "Y" in nc and ("B" in nc or "b" in nc):
        blue = nc.get("B", 0) + nc.get("b", 0)
        for yname, yv in (("yellow", nc["Y"]), ("yellow1", 1)):
            for bname, bv in (("blue", blue), ("blueB", nc.get("B", 0)),
                              ("blueb", nc.get("b", 0))):
                for sep, stag in ((" ", "space"), ("", "join"), ("-", "dash"),
                                  ("and", "and")):
                    add(f"pairs/{yname}-{bname}-{stag}",
                        f"{yname}{sep}{yv}{sep}{bname}{sep}{bv}")
                add(f"pairs/nums-{yname}-{bname}", f"{yv}{bv}")
                add(f"pairs/nums-{yname}-{bname}-rev", f"{bv}{yv}")
                add(f"pairs/nums-{yname}-{bname}-comma", f"{yv},{bv}")
    if name == "strip8":
        # the strip's own three numbers, 1 black + 3 blue + 4 red
        for order in ("134", "314", "143", "431"):
            add(f"pairs/strip-colour-order-{order}", order)
        add("pairs/black-blue-red", "black1blue3red4")
        add("pairs/black-blue-red-n", "1 3 4")
        add("pairs/groups-of-four", "4444")
        add("pairs/break", "32")

    # --- bound: the hint words with the numbers the colours have
    for c, k in sorted(nc.items()):
        word = _colour_word(c)
        for form in (f"{word}{k}", f"{word}_{k}", f"{word}{k}{word}",
                     f"{k}{word}", f"{word} has {k}"):
            add(f"bound/{form}", form)
    return out


def _colour_word(c: str) -> str:
    return {"R": "red", "O": "orange", "Y": "yellow", "C": "cyan", "B": "blue",
            "b": "deepblue", "G": "green", "K": "black", "-": ""}[c]


def matrix_candidates() -> list[tuple[str, bytes]]:
    """The author's own two numbers, cross-check cell.

    leads.md note 22 resolves "Yellow has a number and so does Blue. Go back to
    the first puzzle piece" as YELLOW = 9, BLUE = 15 from the phase-1 matrix
    squares. Section 19b tested that matrix's colour masks, indices, sums, counts
    and prime-rank characters against the third door, but in prose and with no
    shipped code, so the 12-candidate number-pair cell is re-run here and
    reported SEPARATELY from the genuinely new sticker/band cells.
    """
    out: list[tuple[str, bytes]] = []
    for y, b in ((9, 15), (15, 9)):
        for form in (f"{y} {b}", f"{y}{b}", f"{b}{y}", f"{y},{b}",
                     f"yellow{y}blue{b}", f"yellow{y}andblue{b}",
                     f"blue{b}andyellow{y}", f"yellow has {y} and blue has {b}",
                     f"yellow{y} blue{b}", f"yellow_{y}_blue_{b}",
                     f"9and15", f"9 and 15", f"1519", "io", "9o"):
            out.append((f"matrix/{form}", form.encode()))
        out.append((f"matrix/a1z26-{y}{b}", a1z26(f"{y}{b}").encode()))
    return out


def control_candidates() -> list[tuple[str, bytes]]:
    """The CSV-verified preimages, run through THIS loop as its witness.

    Deduplicated by preimage, and NOT counted by preimage length 5: the two
    "Good job, Neo!" rows of the CSV share ONE preimage under two constructions,
    so five witness ROWS are four distinct preimages reaching six addresses. A
    witness check that counted hits against rows would fail on a correct run --
    which is exactly what the first run of this tool did, so the check is written
    as "every distinct control preimage produces at least one hit" instead.
    """
    out: list[tuple[str, bytes]] = []
    seen: set[bytes] = set()
    for w in TD.WITNESSES:
        if w[0] not in seen:
            seen.add(w[0])
            out.append((f"control/{w[0].decode()[:24]}", w[0]))
    return out


def run(include_matrix: bool) -> tuple[int, int, list]:
    objs = load_objects()
    t0 = time.time()
    hits: list = []
    tried = 0
    ncand = 0
    groups = [(k, v) for k, v in objs.items()]
    if include_matrix:
        groups.append(("matrix", ""))

    # the witness goes through the identical candidate loop
    pool: list[tuple[str, bytes]] = list(control_candidates())
    for name, run_str in groups:
        if name == "matrix":
            pool += matrix_candidates()
        else:
            pool += candidates(run_str, name)

    nctl = len(control_candidates())
    ctl_pres = {pre for _t, pre in control_candidates()}
    for tag, pre in pool:
        ncand += 1
        for (cname, comp), addr in TD.addresses_for(pre).items():
            tried += 1
            if addr in TD.TARGETS:
                hits.append((tag, pre, cname, comp, addr))
    dt = time.time() - t0

    ctl_found = {h[1] for h in hits if h[0].startswith("control/")}
    ctl_hits = [h for h in hits if h[0].startswith("control/")]
    real = [h for h in hits if not h[0].startswith("control/")]
    if ctl_found != ctl_pres:
        missing = [p[:24] for p in ctl_pres - ctl_found]
        print(f"  WITNESS FAILED: {len(ctl_found)}/{len(ctl_pres)} distinct "
              f"control preimages re-found through this loop; missing {missing}")
        return ncand, tried, hits, False

    print(f"objects: " + ", ".join(
        f"{k}({len(v)} raw, {len([c for c in v if c != '-'])} certified)"
        for k, v in objs.items()) + f", matrix(cross-check)")
    print(f"witness: {len(ctl_found)}/{len(ctl_pres)} distinct control preimages "
          f"re-found through this loop, {len(ctl_hits)} target addresses "
          f"(5 CSV rows; one preimage under two constructions)")
    for tag, pre, cname, comp, addr in ctl_hits:
        print(f"  [CTL] {addr} from {pre[:34]!r} [{cname},"
              f"{'compressed' if comp else 'uncompressed'}]")
    print(f"third door in target set and unclaimed: "
          f"{TD.THIRD_DOOR in TD.TARGETS} (asserted by third_door.selftest)")
    print(f"{ncand - nctl} candidates x 6 constructions x 2 pubkey forms = "
          f"{tried - nctl * 12} address derivations in {dt:.1f}s")
    for tag, pre, cname, comp, addr in real:
        funded, op, status = TD.TARGETS[addr]
        print(f"  MATCH  {addr}  [{cname}, "
              f"{'compressed' if comp else 'uncompressed'}]  from {tag} = "
              f"{pre!r}  (funded {funded}, op_return {op!r}, status {status})")
    if not real:
        print("  0 MATCH on the third door, the 8 other planted addresses and "
              "both funded gates")
    return ncand, tried, hits, True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true",
                    help="certify: third_door.selftest() then the witness loop")
    ap.add_argument("--colors", action="store_true",
                    help="run the colour-rule battery against the third door")
    a = ap.parse_args(argv)
    if a.selftest or not (a.selftest or a.colors):
        print("== third_door.selftest ==")
        if TD.selftest():
            return 1
        print("== this tool's witness loop ==")
        ncand, _tried, _hits, ok = run(include_matrix=False)
        if not ok:
            print("SELFTEST FAIL: the witness loop did not re-find the controls")
            return 1
        print(f"SELFTEST PASS: 5 CSV rows re-derived by third_door, "
              f"witness loop intact, {ncand - len(control_candidates())} "
              f"non-control candidates carried")
        return 0
    if a.colors:
        print("== third_door.selftest (pre) ==")
        if TD.selftest():
            return 1
        _ncand, _tried, hits, ok = run(include_matrix=True)
        print("== third_door.selftest (post) ==")
        if TD.selftest():
            return 1
        if not ok:
            return 1
        real = [h for h in hits if not h[0].startswith("control/")]
        return 1 if real else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
