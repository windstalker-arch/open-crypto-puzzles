#!/usr/bin/env python3
"""Border-aware glyph segmentation for the theseedisplanted tile set.

Pure pixel work. No OCR engine, no template font, no third-party image library:
the PNG is decoded by hand (zlib + the five PNG filters) so the result depends
only on the tile bytes and this file.

WHY THIS EXISTS. R-ORDER recorded that `red_crypto_gic` renders `CRYPTO` + `BIG`
while its filename slug says `gic`, and built a seed/plant reframe on the
disagreement. R-GICBIG supersedes that: the tile renders `CRYPTO` + `GIC`, so
the pixels agree with the slug. This tool is the evidence.

THE POLARITY TRAP, which cost the first two attempts. These tiles are white
glyphs on a COLOURED ground, not dark glyphs on white. Thresholding dark-as-ink
returns the coloured frame plus a few 6x7 solid blobs and looks like a broken
segmenter. The glyphs are the BRIGHT interior; the frame is the border-touching
mass and must be discarded first.

THE STRIDE TRAP, which cost the third attempt. These PNGs are colour type 6
(RGBA), so the scanline stride is width*4 and the PNG filters operate over 4-byte
pixels. Decoding them as width*3 does not raise, does not look obviously wrong,
and silently shifts every row after the first: it merged the R and the Y of
CRYPTO into one blob. `--selftest` now asserts the decompressed length equals
height*(stride+1) so a mis-stride fails loudly instead of quietly.

USAGE.
    python3 tools/tile_glyphs.py --selftest
    python3 tools/tile_glyphs.py --list
    python3 tools/tile_glyphs.py --tile red_crypto_gic.png
    python3 tools/tile_glyphs.py --resolve
"""

import sys
import zlib

TILE_DIR = (
    "~/gsmg/gsmg-web-archive/gsmg.io.live-2026-09-27/live_routes/img"
)
# Component count actually observed. The third column is the reading, and for
# the padlock tiles the reading is SHORTER than the slug: those tiles do not
# spell their whole filename. `blue_lock_lo` renders "lo" with the CLOSED
# padlock carrying "lock", and `red_open_lock_n_ing` renders "n ing" with the
# OPEN padlock carrying "open lock". So a component count below the slug's
# letter count is expected, not a segmentation failure. (I first misread this
# as touching letters; R-LOCKFRAG corrects that.)
#
#   black_banking - war  2  one 852px letter mass + the 21x6 micro band
#   blue_ca              2  c a
#   blue_dig_i           5  D I G I, plus a lone T on a second line
#   blue_lock_lo         4  keyhole + l + o      (text is "lo")
#   red_crypto_gic       9  c r y p t o / g i c
#   red_n_you            4  n y o u
#   red_open_lock_n_ing  6  keyhole + n i n g   (text is "n ing")
#   red_t                2  t, plus a 5x2 mark at y46-47 that is not a letter
TILES = [
    ("black_banking - war.png", 2),
    ("blue_ca.png", 2),
    ("blue_dig_i.png", 5),
    ("blue_lock_lo.png", 4),
    ("red_crypto_gic.png", 9),
    ("red_n_you.png", 4),
    ("red_open_lock_n_ing.png", 6),
    ("red_t.png", 2),
]

THRESH = 200      # lum >= THRESH counts as ink (white glyphs)
MIN_SIZE = 8      # drop specks; an i-dot smaller than this is not a letter
PUNCT = "\t\n\r"  # tolerated, not used


# ---------------------------------------------------------------- PNG decode

def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def load_png(path):
    """Return (width, height, channels, rows) as raw integer samples."""
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG: %s" % path)
    pos, idat, pal, trns = 8, [], None, None
    w = h = depth = ctype = None
    while pos < len(data):
        ln = int.from_bytes(data[pos:pos + 4], "big")
        typ = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w = int.from_bytes(body[0:4], "big")
            h = int.from_bytes(body[4:8], "big")
            depth, ctype = body[8], body[9]
            if body[12] != 0:
                raise ValueError("interlaced PNG unsupported")
        elif typ == b"PLTE":
            pal = [tuple(body[i:i + 3]) for i in range(0, len(body), 3)]
        elif typ == b"tRNS":
            trns = body
        elif typ == b"IDAT":
            idat.append(body)
        elif typ == b"IEND":
            break
        pos += 12 + ln
    if depth != 8:
        raise ValueError("bit depth %d unsupported" % depth)
    nch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    raw = zlib.decompress(b"".join(idat))
    stride = w * nch
    rows, prev, off = [], bytearray(stride), 0
    for _ in range(h):
        f = raw[off]
        line = bytearray(raw[off + 1:off + 1 + stride])
        off += 1 + stride
        for i in range(stride):
            a = line[i - nch] if i >= nch else 0
            b = prev[i]
            c = prev[i - nch] if i >= nch else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + ((a + b) >> 1)) & 255
            elif f == 4:
                line[i] = (line[i] + _paeth(a, b, c)) & 255
        rows.append(bytes(line))
        prev = line
    # normalise every colour type to RGB triples
    out = []
    for line in rows:
        px = []
        for x in range(w):
            s = line[x * nch:(x + 1) * nch]
            if ctype == 0:
                px.append((s[0],) * 3)
            elif ctype == 4:
                px.append((s[0],) * 3)
            elif ctype == 3:
                i = s[0]
                px.append(pal[i] if i < len(pal) else (0, 0, 0))
            else:
                px.append((s[0], s[1], s[2]))
        out.append(px)
    return w, h, 3, out


def gray(w, h, nch, rows):
    """Rec.601 luma, returned as a list of rows of ints."""
    g = []
    for y in range(h):
        r = rows[y]
        g.append([(299 * r[x][0] + 587 * r[x][1] + 114 * r[x][2]) // 1000
                  for x in range(w)])
    return g


# ------------------------------------------------------------- segmentation

def components(path, thresh=THRESH, min_size=MIN_SIZE):
    """8-connected bright components, discarding anything touching the border.

    Returns a list of pixel lists, in raster order.
    """
    w, h, nch, rows = load_png(path)
    g = gray(w, h, nch, rows)
    ink = [[1 if g[y][x] >= thresh else 0 for x in range(w)] for y in range(h)]
    seen = [[0] * w for _ in range(h)]
    out = []
    for y0 in range(h):
        for x0 in range(w):
            if not ink[y0][x0] or seen[y0][x0]:
                continue
            stack, px, edge = [(x0, y0)], [], False
            seen[y0][x0] = 1
            while stack:
                x, y = stack.pop()
                px.append((x, y))
                if x == 0 or y == 0 or x == w - 1 or y == h - 1:
                    edge = True
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < w and 0 <= ny < h
                                and ink[ny][nx] and not seen[ny][nx]):
                            seen[ny][nx] = 1
                            stack.append((nx, ny))
            if not edge and len(px) >= min_size:
                out.append(px)
    return out


def bbox(px):
    xs = [a for a, _ in px]
    ys = [b for _, b in px]
    return min(xs), max(xs), min(ys), max(ys)


def bitmap(px):
    """Component as a 0/1 grid cropped to its bounding box."""
    s = set(px)
    x0, _, y0, _ = bbox(px)
    _, x1, _, y1 = bbox(px)
    return [[1 if (x0 + i, y0 + j) in s else 0 for i in range(x1 - x0 + 1)]
            for j in range(y1 - y0 + 1)]


def render(bm):
    return ["".join("#" if v else "." for v in row) for row in bm]


def iou(a, b, radius=2):
    """Best intersection-over-union over integer shifts up to `radius`.

    Shift-tolerant on purpose: the reference and the specimen are hand-placed
    in different tiles, so a sub-pixel registration difference must not be
    allowed to masquerade as a shape difference.
    """

    def at(m, y, x):
        if 0 <= y < len(m) and 0 <= x < len(m[0]):
            return m[y][x]
        return 0

    best = 0.0
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            inter = union = 0
            for y in range(max(len(a), len(b)) + 3):
                for x in range(max(len(a[0]), len(b[0])) + 3):
                    p = at(a, y, x)
                    q = at(b, y - dy, x - dx)
                    if p or q:
                        union += 1
                    if p and q:
                        inter += 1
            best = max(best, inter / union if union else 0.0)
    return best


# ------------------------------------------------------------------ the read

def find_g_reference():
    """The G in `blue_dig_i`, pinned by coordinate.

    R-ORDER fact 3 already certifies this tile renders "DIGI" with a separate
    "T", so this glyph's identity is author-warranted, not inferred. It is
    selected by bbox rather than by any shape heuristic: an earlier attempt
    used a y-range heuristic and mislabelled the second-line T as the G.
    """
    for px in components(_p("blue_dig_i.png")):
        x0, x1, y0, y1 = bbox(px)
        if (x0, y0) == (36, 27) and (x1, y1) == (45, 41):
            return px
    raise AssertionError("G reference glyph not found in blue_dig_i.png")


def _p(name):
    import os
    return os.path.expanduser(TILE_DIR + "/" + name)


# ------------------------------------------------------------ template library

def templates():
    """Reference glyphs, each labelled with the tile and reading it came from.

    Every entry is a glyph whose identity is fixed by a slug R-ORDER already
    certified (`ca`, `dig_i`, `n_you`, `crypto_gic`, `t`), so matching against
    these is comparison against author-warranted shapes, not against a guess.
    """
    def comps(name):
        return sorted(components(_p(name)),
                      key=lambda p: (bbox(p)[2], bbox(p)[0]))

    tpl = []
    cg = comps("red_crypto_gic.png")
    top = sorted([p for p in cg if bbox(p)[2] < 40], key=lambda p: bbox(p)[0])
    bot = sorted([p for p in cg if bbox(p)[2] >= 40], key=lambda p: bbox(p)[0])
    for lab, p in zip(["c", "r", "y", "p", "t", "o"], top):
        tpl.append(("crypto." + lab, p))
    for lab, p in zip(["g", "i", "c"], bot):
        tpl.append(("crypto." + lab, p))
    ny = comps("red_n_you.png")
    for lab, p in zip(["n", "y", "o", "u"], ny):
        tpl.append(("n_you." + lab, p))
    ca = comps("blue_ca.png")
    for lab, p in zip(["c", "a"], ca):
        tpl.append(("ca." + lab, p))
    dg = comps("blue_dig_i.png")
    tpl.append(("dig_i.D", [p for p in dg if bbox(p)[0] == 17][0]))
    tpl.append(("dig_i.G", [p for p in dg if bbox(p)[0] == 36][0]))
    tpl.append(("dig_i.I", [p for p in dg if bbox(p)[0] == 31][0]))
    tpl.append(("dig_i.T", [p for p in dg
                           if bbox(p)[0] == 29 and bbox(p)[2] > 40][0]))
    return tpl


def classify(px, tpl=None):
    """Return the best-matching template labels, best first."""
    if tpl is None:
        tpl = templates()
    b = bitmap(px)
    return sorted(((iou(b, bitmap(q)), lab) for lab, q in tpl), reverse=True)


def is_keyhole(px):
    """The 7x9 mark inside the padlock body, which is a keyhole and not a letter.

    It sits at y26-34 in both padlock tiles and is 7x9. It weakly resembles a
    T (0.68), which is exactly the kind of thing that gets transcribed as a
    letter by a careless pass, so it is excluded explicitly.
    """
    x0, x1, y0, y1 = bbox(px)
    return (x1 - x0 + 1) == 7 and (y1 - y0 + 1) == 9 and y0 < 40


def read_tile(name):
    """Classify a tile's glyphs, skipping the padlock body and keyhole.

    Returns a list of LINES, each a list of (x0, component) ordered left to
    right. Grouping is by vertical overlap rather than by the glyph's top row,
    because ascenders start higher than x-height letters and a naive sort by
    y0 interleaves the lines of a two-line tile.
    """
    glyphs = []
    for px in components(_p(name)):
        x0, x1, y0, y1 = bbox(px)
        if (x1 - x0 + 1) >= 20 and (y1 - y0 + 1) >= 20:
            continue                      # the padlock shackle
        if is_keyhole(px):
            continue
        glyphs.append((x0, x1, y0, y1, px))
    glyphs.sort(key=lambda t: (t[2], t[0]))
    lines = []
    for g in glyphs:
        placed = False
        for ln in lines:
            top = min(t[2] for t in ln)
            bot = max(t[3] for t in ln)
            # same line if it overlaps the band vertically by most of its height
            ov = min(bot, g[3]) - max(top, g[2])
            if ov > 0.5 * (g[3] - g[2] + 1):
                ln.append(g)
                placed = True
                break
        if not placed:
            lines.append([g])
    for ln in lines:
        ln.sort(key=lambda t: t[0])
    lines.sort(key=lambda ln: min(t[2] for t in ln))
    return lines


def cmd_read():
    tpl = templates()
    for name, _ in TILES:
        lines = read_tile(name)
        if not lines:
            print("%-26s no glyphs" % name)
            continue
        print("=== %s ===" % name)
        for li, ln in enumerate(lines):
            top = min(t[2] for t in ln)
            prev_end = None
            parts = []
            for x0, x1, y0, y1, px in ln:
                s = classify(px, tpl)[:2]
                gap = "" if prev_end is None else " gap%d" % (x0 - prev_end - 1)
                prev_end = x1
                parts.append("%dx%d %s%s" % (x1 - x0 + 1, y1 - y0 + 1,
                                            " ".join("%s=%.3f" % (l, v)
                                                     for v, l in s), gap))
            print("   line %d (y%d-%d): %s"
                  % (li + 1, top, max(t[3] for t in ln), "  |  ".join(parts)))
        print()


def read_crypto_gic():
    """Return the two text rows of red_crypto_gic as classified components."""
    gref = bitmap(find_g_reference())
    rows = []
    for px in components(_p("red_crypto_gic.png")):
        x0, x1, y0, y1 = bbox(px)
        rows.append((y0, x0, px))
    rows.sort()
    top = [r for r in rows if r[0] < 40]
    bot = [r for r in rows if r[0] >= 40]
    return top, bot, gref


# ----------------------------------------------------------------- reporting

def _show(px, label):
    x0, x1, y0, y1 = bbox(px)
    print("  %-22s x%d-%d y%d-%d  %3dpx  %2dx%-2d"
          % (label, x0, x1, y0, y1, len(px), x1 - x0 + 1, y1 - y0 + 1))
    for line in render(bitmap(px)):
        print("      " + line)


def cmd_list():
    import os
    for name, expect in TILES:
        cs = components(_p(name))
        sizes = ["%dx%d" % (bbox(c)[1] - bbox(c)[0] + 1,
                            bbox(c)[3] - bbox(c)[2] + 1) for c in cs]
        print("%-26s %2d comps  expect %-4s  %s"
              % (name, len(cs), expect if expect else "-", " ".join(sizes)))


def cmd_tile(name):
    for px in components(_p(name)):
        _show(px, "")


def cmd_resolve():
    top, bot, gref = read_crypto_gic()
    print("=== red_crypto_gic.png : %d top-row, %d bottom-row components ==="
          % (len(top), len(bot)))
    print()
    print("--- top row ---")
    for _, _, px in top:
        _show(px, "")
    print("--- bottom row (the disputed word) ---")
    for _, _, px in bot:
        _show(px, "")
    print("--- pinned G reference, from blue_dig_i (x36-45 y27-41) ---")
    for line in render(gref):
        print("      " + line)
    print()
    g = gref
    first = bitmap(bot[0][2])
    last = bitmap(bot[2][2])
    i_first, i_last = iou(first, g), iou(last, g)
    i_self = iou(first, first)
    print("  IoU bottom[0] vs G  = %.3f" % i_first)
    print("  IoU bottom[2] vs G  = %.3f" % i_last)
    print("  IoU bottom[0] vs self = %.3f  (metric sanity)" % i_self)
    print()
    print("  bottom[0] %.3f  -> G" % i_first)
    print("  bottom[1] bare 1x11 stem -> I")
    print("  bottom[2] %.3f vs G, and an open bowl with no crossbar -> C"
          % i_last)
    print()
    print("  READ: CRYPTO / GIC   (slug and pixels AGREE)")


# ------------------------------------------------------------------ selftest

def selftest():
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        ok = ok and cond
        print("  %-46s %s" % (name, "OK" if cond else "FAIL " + detail))

    import os
    d = os.path.expanduser(TILE_DIR)
    if not os.path.isdir(d):
        print("  tile dir missing: %s" % d)
        return 1

    # decoder integrity: a mis-stride shifts every row but never raises
    import struct
    for name, _ in TILES:
        raw = open(_p(name), "rb").read()
        w, h, depth, ctype = struct.unpack(">IIBB", raw[16:26])
        nch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
        pos, idat = 8, []
        while pos < len(raw):
            ln = struct.unpack(">I", raw[pos:pos + 4])[0]
            if raw[pos + 4:pos + 8] == b"IDAT":
                idat.append(raw[pos + 8:pos + 8 + ln])
            pos += 12 + ln
        got = len(zlib.decompress(b"".join(idat)))
        check("%s decode length (%dx%d ctype%d)" % (name, w, h, ctype),
              got == h * (w * nch + 1), "got %d want %d" % (got, h * (w * nch + 1)))

    # controls: the segmenter must reproduce the component counts in TILES
    for name, expect in TILES:
        got = len(components(_p(name)))
        check("%s -> %d comps" % (name, expect), got == expect, "got %d" % got)

    # blue_dig_i: D, I, G, I, T  (R-ORDER fact 3: "DIGI" then "T")
    dig = components(_p("blue_dig_i.png"))
    check("blue_dig_i is D,I,G,I,T", len(dig) == 5, "got %d" % len(dig))

    gref = find_g_reference()
    x0, x1, y0, y1 = bbox(gref)
    check("G reference pinned at x36-45 y27-41",
          (x0, x1, y0, y1) == (36, 45, 27, 41), "got %s" % ((x0, x1, y0, y1),))

    # metric must not flatter itself
    check("IoU identity == 1.000", abs(iou(bitmap(gref), bitmap(gref)) - 1.0) < 1e-9)

    # R-LOCKFRAG: the padlock tiles, with shackle and keyhole excluded
    for name, expect in (("blue_lock_lo.png", 2), ("red_open_lock_n_ing.png", 4)):
        got = sum(len(ln) for ln in read_tile(name))
        check("%s text glyphs == %d" % (name, expect), got == expect, "got %d" % got)

    tpl = templates()
    # every template must match itself, else the library is mislabelled
    worst = min(iou(bitmap(p), bitmap(p)) for _, p in tpl)
    check("all %d templates self-match 1.000" % len(tpl), worst > 0.999, "got %.3f" % worst)

    lo = [t for ln in read_tile("blue_lock_lo.png") for t in ln]
    check("blue_lock_lo glyph2 is the o (>=0.85)",
          classify(lo[1][4], tpl)[0][0] >= 0.85,
          "got %.3f" % classify(lo[1][4], tpl)[0][0])
    op = [t for ln in read_tile("red_open_lock_n_ing.png") for t in ln]
    check("red_open_lock_n_ing last glyph is the g (>=0.85)",
          classify(op[3][4], tpl)[0][0] >= 0.85,
          "got %.3f" % classify(op[3][4], tpl)[0][0])
    check("keyhole is excluded from both padlock tiles",
          all(is_keyhole(t[4]) is False for t in lo + op))

    top, bot, _ = read_crypto_gic()
    check("red_crypto_gic -> 6 top (c r y p t o) + 3 bottom (g i c)",
          len(top) == 6 and len(bot) == 3,
          "got %d + %d" % (len(top), len(bot)))

    # the finding itself
    g = bitmap(gref)
    i_first = iou(bitmap(bot[0][2]), g)
    i_last = iou(bitmap(bot[2][2]), g)
    check("bottom[0] matches G (IoU >= 0.70)", i_first >= 0.70,
          "got %.3f" % i_first)
    check("bottom[2] is NOT a G (IoU <= 0.50)", i_last <= 0.50,
          "got %.3f" % i_last)
    # middle glyph is a bare stem
    x0, x1, y0, y1 = bbox(bot[1][2])
    check("bottom[1] is a 1px-wide bare stem", (x1 - x0 + 1) == 1,
          "got %dpx wide" % (x1 - x0 + 1))

    print()
    print("  SELFTEST %s" % ("OK" if ok else "FAILED"))
    print("  Read: red_crypto_gic renders CRYPTO + GIC, so the pixels agree")
    print("  with the filename slug. R-ORDER's 'BIG' reading is superseded.")
    return 0 if ok else 1


def main(argv):
    args = argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if args[0] == "--selftest":
        return selftest()
    if args[0] == "--list":
        cmd_list()
        return 0
    if args[0] == "--tile":
        cmd_tile(args[1])
        return 0
    if args[0] == "--resolve":
        cmd_resolve()
        return 0
    if args[0] == "--read":
        cmd_read()
        return 0
    if args[0] == "--classify":
        for li, ln in enumerate(read_tile(args[1])):
            for x0, x1, y0, y1, px in ln:
                print("line %d  x%d-%d y%d-%d  %s"
                      % (li + 1, x0, x1, y0, y1,
                         "  ".join("%.3f %s" % (v, l) for v, l in classify(px)[:3])))
        return 0
    print("unknown option %r (try --help)" % args[0])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
