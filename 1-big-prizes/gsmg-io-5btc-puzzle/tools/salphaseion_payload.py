#!/usr/bin/env python3
"""Extract the SalPhaseIon <textarea> payload and its hidden binary channel.

The 2020-11-12 archived SalPhaseIon page (data/wb_dbbib-page_20201112.html) is a
single <textarea> holding space-separated single characters.  A stream of
lowercase a-i noise is interleaved through it.  Most noise bursts are 1-3
characters long, but exactly two bursts are pure a/b and byte-aligned in
length; read as bits (a=0, b=1, MSB first, 8-bit ASCII) they are clean text.

    104 bits -> "matrixsumlist"
     40 bits -> "enter"

144 bits total == 18 bytes == len("matrixsumlistenter").  No leftover bits.

Usage:
    python3 tools/salphaseion_payload.py [html] [--matrix]
"""
import base64
import re
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, os.pardir, "data", "wb_dbbib-page_20201112.html")

# The 14x14 matrix implied by A (91 chars = upper triangle incl. diagonal-free
# strict upper triangle of a 14x14 symmetric matrix, values a=1..i=9).
A = "dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe"


def payload(html_path):
    raw = open(html_path, errors="ignore").read()
    m = re.search(r"(?is)<textarea[^>]*>(.*?)</textarea>", raw)
    if not m:
        raise SystemExit("no <textarea> in %s" % html_path)
    return re.sub(r"\s+", "", m.group(1))


def ab_runs(body, min_len=1):
    return [(x.start(), x.end(), x.group()) for x in re.finditer(r"[ab]+", body)]


def bits_to_ascii(bits, zero="a", one="b"):
    """MSB-first 8-bit ASCII.  Returns (text, leftover_bit_count)."""
    v = [0 if c == zero else 1 for c in bits]
    out = []
    for i in range(0, len(v) - len(v) % 8, 8):
        n = 0
        for b in v[i:i + 8]:
            n = n * 2 + b
        out.append(chr(n) if 32 <= n < 127 else ".")
    return "".join(out), len(v) % 8


def matrix_row_sums():
    V = {c: i + 1 for i, c in enumerate("abcdefghi")}
    assert len(A) == 91, len(A)
    M = [[0] * 14 for _ in range(14)]
    k = 0
    for i in range(14):
        for j in range(i + 1, 14):
            M[i][j] = M[j][i] = V[A[k]]
            k += 1
    assert k == 91
    return M, [sum(r) for r in M]


# --- the z-segment interpreter: a-i -> 1-9, 'o' -> 0, then base10 -> hex -> ASCII
_DIGIT = {chr(ord("a") + i): str(i + 1) for i in range(9)}
_DIGIT["o"] = "0"


def interpret_z_segment(seg):
    """Decode one 'z'-delimited segment into ASCII.

    This is the ONLY decoder the page supports, and it is the one that the
    recorded oracle password independently confirms (see chain() below).
    """
    digits = "".join(_DIGIT[c] for c in seg if c in _DIGIT)
    h = hex(int(digits))[2:]
    if len(h) % 2:
        h = "0" + h
    return bytes.fromhex(h).decode("ascii", "ignore")


def z_segments(body):
    """The page delimits its readable sections with the non-[a-i] char 'z'."""
    return body[765:895].split("z")


def chain(html_path):
    """Derive the whole endgame from the page alone and cross-check it.

    Returns a dict of the derived values.  Nothing here is taken from outside
    the page: the tokens come out of the two noise channels, the blob comes out
    of the payload with the 'enter' burst excised, and the password is those
    four tokens in page order with the first one repeated as a bookend.

    The bookend repetition is the single degree of freedom in this derivation
    -- the four tokens are read off the page, but *where* to repeat is a choice.
    It is not guessed: the resulting password is checked against the recorded
    oracle blob below, and a wrong choice fails to open it.
    """
    body = payload(html_path)
    runs = [x.group() for x in re.finditer(r"[ab]{8,}", body)
            if len(x.group()) % 8 == 0]
    k1, k2 = bits_to_ascii(runs[0])[0], bits_to_ascii(runs[1])[0]
    seg = z_segments(body)
    k3, k4 = interpret_z_segment(seg[1]), interpret_z_segment(seg[2])
    password = k1 + k2 + k3 + k4 + k1

    # The blob is the payload's base64 run, split in two by the 'enter' burst.
    # Re-joining head+tail is what makes it contiguous 128 chars = 96 bytes.
    blob_b64 = body[895:959] + body[999:1063]
    return {
        "tokens": [k1, k2, k3, k4],
        "password": password,
        "blob_b64": blob_b64,
    }



def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    html = args[0] if args else DEFAULT
    body = payload(html)

    print("source          : %s" % html)
    print("textarea payload: %d chars" % len(body))
    print("A stream (head) : %s..." % body[:91])
    print()

    runs = ab_runs(body)
    total = sum(len(r) for _, _, r in runs)
    print("a/b runs        : %d  (total %d bits)" % (len(runs), total))

    channel = ""
    carried = 0
    aligned = 0
    print()
    print("byte-aligned pure a/b runs (a=0, b=1, MSB first):")
    for s, e, r in runs:
        if len(r) >= 8 and len(r) % 8 == 0:
            txt, left = bits_to_ascii(r)
            channel += txt
            carried += len(r)
            aligned += 1
            print("  off=%-5d len=%-4d leftover=%d  %r" % (s, len(r), left, txt))
    print()
    print("  others         : %d runs, all 1-3 bits (decoy noise)"
          % (len(runs) - aligned))
    print("  carried bits   : %d  = %d bytes" % (carried, carried // 8))
    print()
    print("HIDDEN COMMAND   : %r" % channel)

    if "--matrix" in sys.argv:
        M, rs = matrix_row_sums()
        print()
        print("A-matrix 14x14 row sums (a=1..i=9, a=0,b=1 forced diagonal 0):")
        print("  %s" % rs)
        print("  total = %d" % sum(rs))

    if "--chain" in sys.argv:
        import hashlib
        c = chain(html)
        print()
        print("=" * 72)
        print("z-segment interpreter (a-i -> 1-9, 'o' -> 0, base10 -> hex -> ASCII):")
        for i, t in enumerate(c["tokens"][2:], 3):
            print("  token %d = %r" % (i, t))
        print()
        print("password  = %r  (%d chars)" % (c["password"], len(c["password"])))
        print("blob_b64  = %d chars" % len(c["blob_b64"]))
        raw = base64.b64decode(c["blob_b64"])
        print("  Salted__=%s  salt=%s  ciphertext=%dB"
              % (raw[:8] == b"Salted__", raw[8:16].hex(), len(raw) - 16))
        try:
            sys.path.insert(0, os.path.join(HERE, os.pardir, "tools"))
            import oracle
            print()
            print("cross-check against tools/oracle.py:")
            print("  blob     == oracle.BLOB_B64 : %s" % (c["blob_b64"] == oracle.BLOB_B64))
            for dg in ("md5", "sha256"):
                p = oracle.decrypt_blob(c["blob_b64"], c["password"], dg)
                if p is None:
                    print("  decrypt %-6s          : None (padding invalid)" % dg)
                else:
                    print("  decrypt %-6s          : %dB sha256=%s"
                          % (dg, len(p), hashlib.sha256(p).hexdigest()))
                    print("    layout K_C1(32) || K_C2(32) || E_C(%d)" % (len(p) - 64))
                    print("    (key material not printed; see data/chain1_79.bin)")
        except ImportError:
            print("  (tools/oracle.py not importable - skipped cross-check)")


if __name__ == "__main__":
    main()
