#!/usr/bin/env python3
"""ciphertools_ciphers.py -- faithful re-implementation of the ciphertools.co.uk
decode (cipher->plain) conventions, for the GSMG puzzle sweep.

The puzzle's phase-3.2 hint names this tool explicitly ("Go to
https://ciphertools.co.uk/decode.php ... choose Beaufort").  The tool is a
custom F#/Elmish SPA; its cipher menu is exactly 19 ciphers (leads.md):
  AFFINE AMSCO AUTOKEY BEAUFORT BIFID CADENUS CAESAR FOURSQUAREMANUAL HILL
  NIHILIST PLAYFAIR PORTA RAILFENCE SUBSTITUTION TRANSPOSITIONSIMP
  TRANSPOSITIONCOL VIGENERE

Conventions extracted from the live bundle (index-B_H4mUOu.js / KeyInfo):
  - alphabet = 26-letter A-Z (Language.alphabet)
  - Affine: two sliders AffineMultSize (multiplier), ShiftSize (shift)
  - Amsco: AmscoStartsWith2 bool -> 2-1-2-1-... or 1-2-1-2-... bigram pattern
  - Bifid: PolybiusKey (keyed square) + BifidPeriod (0 = full message length) +
          PolybiusCoordFirstNum (0/1), missing/replacing char
  - Cadenus: ColumnHeight (rows per column), keyword-derived alphabet
  - FourSquare: two Polybius squares (plaintext / ciphertext)
  - Hill: HillKey matrix, HillMatrixLen (2 or 3)
  - Nihilist: Polybius square key, PolybiusCoordFirstNum, VigenereKey (but as
          the Nihilist additive key)
  - Porta / Autokey / Beaufort / Vigenere: VigenereKey keyword
  - Railfence: NumberRails (2..12), StartingRail, StartingDirection
  - Substitution: SubstitutionKey = the 26-char ciphertext alphabet
  - Transposition simple: TranspositionKey = permutation (list of numbers),
          MaxNoTransCols, ExtraTransCols (block transposition)
  - Transposition columnar: TranspositionKey = keyword/permutation

All functions here DECODE (ciphertext -> plaintext).  Output alphabet is A-Z.
"""

from __future__ import annotations

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _norm(ct: str) -> str:
    """Upper-case, keep only A-Z letters (the tool filters alphabetically)."""
    return "".join(c for c in ct.upper() if c in ALPHABET)


# ---------------------------------------------------------------- Caesar / Affine
def caesar_decode(ct: str, shift: int) -> str:
    s = _norm(ct)
    return "".join(ALPHABET[(ALPHABET.index(c) - shift) % 26] for c in s)


def affine_decode(ct: str, mult: int, shift: int) -> str:
    s = _norm(ct)
    return "".join(
        ALPHABET[(ALPHABET.index(c) - shift) * pow(mult, -1, 26) % 26] for c in s)


# ---------------------------------------------------------------- Vigenere family
def _tabula(alphabet: str = ALPHABET) -> str:
    return "".join(ALPHABET[(ALPHABET.index(c) + k) % 26]
                   for c in alphabet for k in range(26))


def vigenere_decode(ct: str, key: str) -> str:
    s = _norm(ct)
    key = _norm(key) or "A"
    out = []
    for ki, c in enumerate(s):
        r = ALPHABET.index(c)
        k = ALPHABET.index(key[ki % len(key)])
        out.append(ALPHABET[(r - k) % 26])
    return "".join(out)


def beaufort_decode(ct: str, key: str) -> str:
    """Beaufort: P = K - C (vs Vigenere P = C - K)."""
    s = _norm(ct)
    key = _norm(key) or "A"
    out = []
    for ki, c in enumerate(s):
        r = ALPHABET.index(c)
        k = ALPHABET.index(key[ki % len(key)])
        out.append(ALPHABET[(k - r) % 26])
    return "".join(out)


def autokey_decode(ct: str, key: str) -> str:
    """Autokey (plaintext autokey): running key = key ++ already-recovered plaintext."""
    s = _norm(ct)
    key = _norm(key) or "A"
    running = list(key)
    out = []
    for c in s:
        r = ALPHABET.index(c)
        k = ALPHABET.index(running[0])
        running = running[1:]
        p = ALPHABET[(r - k) % 26]
        out.append(p)
        running.append(p)
    return "".join(out)


def porta_decode(ct: str, key: str) -> str:
    """Porta: 13 mirror pairs (AB..YZ).  Keyword picks the row; cipher char is
    looked up in that row and mapped back to the alphabet column label."""
    s = _norm(ct)
    key = _norm(key)
    if not key:
        key = "A"
    out = []
    for i, c in enumerate(s):
        p = ALPHABET.index(key[i % len(key)]) // 2  # 0..12 -> AB..YZ
        row = (
            "".join(ALPHABET[13 + (p + j) % 13] for j in range(13))
            + "".join(ALPHABET[(p + j) % 13] for j in range(13))
        )
        j = row.index(c)
        out.append(ALPHABET[j])
    return "".join(out)


# ---------------------------------------------------------------- Bifid
def polybius_square(keyword: str) -> str:
    """Build a keyed 5x5 square string (J dropped), like the tool/Bifid stage."""
    kw = "".join(dict.fromkeys(_norm(keyword)))
    rest = "".join(c for c in ALPHABET if c not in kw and c != "J")
    return (kw + rest)[:25]


def bifid_decode(ct: str, keyword: str = "DBIFHCEG", period: int = 0) -> str:
    s = _norm(ct)
    # symbols not in the square are the tool's "missing->replacing" handling;
    # filter to square letters only.
    sq = polybius_square(keyword)
    s = "".join(c for c in s if c in sq)
    pos = {ch: (i // 5, i % 5) for i, ch in enumerate(sq)}
    coords = [pos[c] for c in s]
    combined = []
    for r, c in coords:
        combined.append(r)
        combined.append(c)
    period = period or len(s)
    out = []
    for start in range(0, len(combined), 2 * period):
        block = combined[start:start + 2 * period]
        h = len(block) // 2
        rs = block[:h]
        cs = block[h:]
        for k in range(h):
            out.append(sq[rs[k] * 5 + cs[k]])
    return "".join(out)


# ---------------------------------------------------------------- Playfair
def _psq(keyword: str) -> str:
    kw = "".join(dict.fromkeys(_norm(keyword)))
    rest = "".join(c for c in ALPHABET if c not in kw and c != "J")
    return (kw + rest)[:25]


def _find(pp: dict, ch: str) -> tuple[int, int]:
    return pp.get(ch, (0, 0))


def playfair_decode(ct: str, keyword: str = "DBIFHCEG") -> str:
    s = _norm(ct)
    s = "".join(c for c in s if c in _psq(keyword))
    sq = _psq(keyword)
    pos = {ch: (i // 5, i % 5) for i, ch in enumerate(sq)}
    out = []
    i = 0
    while i < len(s):
        a, b = s[i], s[i + 1] if i + 1 < len(s) else "X"
        ar, ac = pos[a]
        br, bc = pos[b]
        if ar == br:
            out.append(sq[ar * 5 + (ac - 1) % 5])
            out.append(sq[br * 5 + (bc - 1) % 5])
        elif ac == bc:
            out.append(sq[((ar - 1) % 5) * 5 + ac])
            out.append(sq[((br - 1) % 5) * 5 + bc])
        else:
            out.append(sq[ar * 5 + bc])
            out.append(sq[br * 5 + ac])
        i += 2
    return "".join(out)


# ---------------------------------------------------------------- Nihilist
def nihilist_decode(ct_digits: str, square_keyword: str, additive_key: str,
                    coord: int = 0) -> str:
    """Nihilist decoder over a digit string.

    Input ``ct_digits`` is the cipher as polybius-sum numbers (each cipher
    number = square_coord(disguised plain) + square_coord(key letter), 0/1
    based).  ``coord`` selects the PolybiusCoordFirstNum convention.  Decode:
    subtract the running key letter's square value, map back through the 5x5
    keyed square.  Also accepts a run of a..i/A..I letters treated as the
    digits 1..9 / 0..8 (auto coerce) parsed into 2-digit groups."""
    sq = polybius_square(square_keyword)
    base = 1 if coord else 0
    pos = {ch: (i // 5, i % 5) for i, ch in enumerate(sq)}
    def coordval(ch):
        r, c = pos[ch]
        return (r + base) * 10 + (c + base)
    nums = []
    t = ct_digits.strip()
    if t and any(c.isdigit() for c in t):
        import re
        nums = [int(x) for x in re.findall(r"\d+", t)]
    else:
        # treat a..i / A..I as digits 1..9 (i=9) or 0..8 (a=0); try both
        s = _norm(t)
        if not s:
            return ""
        seq1 = [("ABCDEFGHI".index(c) + 1) for c in s]        # 1..9
        seq0 = ["ABCDEFGHI".index(c) for c in s]              # 0..8
        for seq in (seq1, seq0):
            pairs = [seq[i] * 10 + seq[i + 1] for i in range(0, len(seq) - 1, 2)]
            nums = pairs
            if nums:
                break
    additive = _norm(additive_key) or "A"
    out = []
    for i, num in enumerate(nums):
        k = coordval(additive[i % len(additive)])
        residual = num - k
        r0 = (residual // 10) - base
        c0 = (residual % 10) - base
        if 0 <= r0 < 5 and 0 <= c0 < 5:
            out.append(sq[r0 * 5 + c0])
    return "".join(out)


# ---------------------------------------------------------------- Four Square
def _inv_mod(a: int, m: int) -> int:
    return pow(a % m, -1, m)


def hill_decode(ct: str, key_matrix) -> str:
    """Hill decipher (n x n over Z26).  ``key_matrix`` is a list of rows, each
    a list of ints (n=2 or n=3, matching HillMatrixLen)."""
    import numpy as np
    K = np.array(key_matrix, dtype=int)
    n = K.shape[0]
    s = _norm(ct)
    s = s[:len(s) // n * n]
    det = round(np.linalg.det(K)) % 26
    if (det % 26) == 0 or np.gcd(det, 26) != 1:
        return s
    dinv = _inv_mod(det, 26)
    adj = np.round(np.linalg.inv(K) * np.linalg.det(K)).astype(int)
    Ki = (adj * dinv) % 26
    out = []
    for i in range(0, len(s), n):
        v = np.array([ALPHABET.index(c) for c in s[i:i + n]])
        r = (np.matmul(Ki, v) % 26).astype(int)
        out.append("".join(ALPHABET[x] for x in r))
    return "".join(out)


def foursquare_decode(ct: str, key1: str, key2: str) -> str:
    s = _norm(ct)
    sqp = _psq(key1)  # top-left plain & bottom-right (same key1)
    sqc = _psq(key2)  # top-right & bottom-left (same key2)
    posc = {ch: (i // 5, i % 5) for i, ch in enumerate(sqc)}
    out = []
    i = 0
    while i < len(s):
        a, b = s[i], s[i + 1] if i + 1 < len(s) else "X"
        ar, ac = posc[a]
        br, bc = posc[b]
        out.append(sqp[ar * 5 + bc])
        out.append(sqp[br * 5 + ac])
        i += 2
    return "".join(out)


# ---------------------------------------------------------------- Railfence
def railfence_decode(ct: str, rails: int = 3, start_rail: int = 0,
                     direction_down: bool = True) -> str:
    s = _norm(ct)
    n = len(s)
    if rails <= 1:
        return s
    # build the rail indices pattern
    idx = 0
    step = 1 if direction_down else -1
    rail = start_rail
    rails_order = []
    for _ in range(n):
        rails_order.append(rail)
        nxt = rail + step
        if nxt < 0 or nxt >= rails:
            step = -step
            rail += step
        else:
            rail = nxt
    rails_counts = [rails_order.count(r) for r in range(rails)]
    # fill the rails with slices of the ciphertext in rail order
    chunks = []
    pos = 0
    for r in range(rails):
        chunks.append(list(s[pos:pos + rails_counts[r]]))
        pos += rails_counts[r]
    idxr = [0] * rails
    out = []
    for r in rails_order:
        out.append(chunks[r][idxr[r]])
        idxr[r] += 1
    return "".join(out)


# ---------------------------------------------------------------- Amsco
def amsco_decode(ct: str, starts_with_2: bool = True, cols: int = 1) -> str:
    """Amsco: period 'cols' columns, alternating 2-1-2-1 / 1-2-1-2 fill pattern
    read down each column.  Decode = reconstruct then read row-major."""
    s = _norm(ct)
    n = len(s)
    cols = max(1, cols)
    pat = [2, 1] if starts_with_2 else [1, 2]
    # column fill lengths (how many chars land in each column, read column-major)
    fill = [0] * cols
    total = 0
    row = 0
    while total < n:
        for c in range(cols):
            take = min(pat[(row + c) % 2], n - total)
            if take <= 0:
                break
            fill[c] += take
            total += take
        row += 1
    # split ciphertext across columns (column-major read reconstruction)
    chunks = []
    pos = 0
    for c in range(cols):
        chunks.append(list(s[pos:pos + fill[c]]))
        pos += fill[c]
    # read back row-major with the same pattern
    out = []
    ci = [0] * cols
    placed = 0
    r = 0
    while placed < n:
        for c in range(cols):
            take = pat[(r + c) % 2]
            for _ in range(take):
                if ci[c] < len(chunks[c]):
                    out.append(chunks[c][ci[c]])
                    ci[c] += 1
                    placed += 1
        r += 1
    return "".join(out)


# ---------------------------------------------------------------- Cadenus
def cadenus_decode(ct: str, keyword: str, height: int = 25) -> str:
    """Cadenus transposition (ACA convention).

    Keyword gives the column order.  Plaintext is written into a grid of
    ``len(keyword)`` columns; ciphertext is read off column-by-column in the
    order of the alphabetically-ranked keyword letters.  Decode reverses that:
    read the ciphertext back into the columns in keyword order, then read the
    grid row-major.  ``height`` is the grid row count (25/26 toggle)."""
    s = _norm(ct)
    n = len(s)
    kw = _norm(keyword) or "A"
    cols = max(1, min(len(kw), n))
    order = sorted(range(cols), key=lambda c: (kw[c % len(kw)], c))
    rows = -(-n // cols)
    full = n % cols if rows else 0
    if full == 0:
        full = cols
    col_len = {c: rows if c < full else rows - 1 for c in range(cols)}
    grid = [[""] * cols for _ in range(rows)]
    pos = 0
    for c in order:
        for r in range(col_len[c]):
            if pos < n:
                grid[r][c] = s[pos]
                pos += 1
    return "".join(grid[r][c] for r in range(rows) for c in range(cols)
                   if grid[r][c])


# ---------------------------------------------------------------- Substitution
def substitution_decode(ct: str, key_alphabet: str) -> str:
    s = _norm(ct)
    kw = _norm(key_alphabet)
    keyed = "".join(dict.fromkeys(kw)) + "".join(
        c for c in ALPHABET if c not in kw)
    keyed = keyed[:26]
    # keyed[i] is the cipher for plaintext letter i; decode maps cipher->plain
    mapping = {keyed[i]: ALPHABET[i] for i in range(26)}
    return "".join(mapping.get(c, c) for c in s)


# ---------------------------------------------------------------- Transposition simple
def transposition_simple_decode(ct: str, trans_key: list[int], cols: int = 10,
                                extra: int = 0) -> str:
    """Block/simple transposition: plaintext written into ``cols`` columns
    row-major; ciphertext read out column-by-column in the ``trans_key`` order
    (1-based column numbers).  Decode: read the ciphertext back into the
    columns in key order, then read the grid row-major."""
    s = _norm(ct)
    n = len(s)
    cols = max(1, cols)
    rows = (n + cols - 1) // cols
    order = [x - 1 for x in (trans_key or []) if 1 <= x <= cols]
    if not order:
        order = list(range(cols))
    full = n % cols if rows else 0
    if full == 0:
        full = cols
    col_len = {c: rows if c < full else rows - 1 for c in range(cols)}
    # columns whose index >= full have rows-1 (partial last row), as written
    # row-major.  The ciphertext lists columns in `order`; length per column is
    # fixed by the grid, not the order.
    chunks = {}
    pos = 0
    for c in order:
        ln = col_len.get(c, min(rows, n - pos))
        chunks[c] = list(s[pos:pos + ln])
        pos += ln
    out = []
    for r in range(rows):
        for c in range(cols):
            if r < len(chunks.get(c, [])):
                out.append(chunks[c][r])
    return "".join(out)


# ---------------------------------------------------------------- Transposition columnar
def columnar_decode(ct: str, key_word: str) -> str:
    """Columnar transposition (keyword-derived).  Decode: ciphertext is read out
    column-by-column in keyword-letter-rank order; the plaintext is the
    row-major read of the resulting grid."""
    s = _norm(ct)
    kw = _norm(key_word) or "A"
    cols = len(kw)
    rows = (len(s) + cols - 1) // cols
    order = sorted(range(cols), key=lambda c: (kw[c], c))
    full = len(s) % cols
    col_len = {c: rows if (full == 0 or c < full) else rows - 1 for c in range(cols)}
    chunks = {}
    pos = 0
    for c in order:
        ln = col_len[c]
        chunks[c] = list(s[pos:pos + ln])
        pos += ln
    out = []
    for r in range(rows):
        for c in range(cols):
            if r < len(chunks[c]):
                out.append(chunks[c][r])
    return "".join(out)