# MatrixEncryption: vendored reference implementation

Reference copy of <https://github.com/infinitless/MatrixEncryption>, kept for
comparison when reasoning about substitution and grid style ciphers. It is not a
lead and has no standing in the puzzle's solution chain. No oracle here consumes
its output.

Upstream commit `e68dce37d91d1c506ace3ea3b8d457ef53f7b3e9`, "Update main.py",
2022-03-09. Clone depth 1, no submodules. Upstream documentation lives at the
repository URL above and is deliberately not copied here.

## Licensing

`LICENSE` is the upstream GNU GPL v3, retained verbatim as GPL section 4(a)
requires. This directory is therefore a GPL-3.0 work.

- The code is isolated. Nothing in this repository imports `matrix_enc_ref`; the
  only entry point is `tools/matrix_enc_ref_selftest.py`, which runs the upstream
  module in a subprocess and asserts on its exit code.
- The upstream license file is preserved. Contrast `tools/vic_ref/`, whose
  upstream license is absent, as recorded in `analysis/tested.md` under the
  `R-VICREF` row.
- `main.py` is modified, and the diff is exactly the two lines quoted below, so
  the modification is disclosed rather than silent.

This does not remove the GPL-3.0 obligation. If this repository is redistributed
as a combined work, GPL-3.0 terms apply to that distribution. The tree carries no
root-level license of its own, so there is no existing license grant for a
combined work to conflict with. If GPL-3.0 is unacceptable here, delete this
directory; nothing else references it.

## Local patch to main.py

Upstream opens the pi-digit payload under the wrong filename case:

```python
with open("piDigits.txt", 'r') as f:   # the file on disk is PiDigits.TXT
```

That resolves on a case-insensitive filesystem and raises `FileNotFoundError` on
Linux and on Termux. The patch resolves the real filename relative to `__file__`,
which also makes the script runnable from any working directory:

```diff
+import os
-_PIDIGITS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PiDigits.TXT")
+with open(_PIDIGITS, 'r') as f:
     pidecimals = f.read()
```

No algorithmic change. Verified byte-identical to the patched working copy.

Do not convert the floating-point literals to integer division. `x ** (1 / 2)`
and `len(s) ** (1 / 4)` are deliberate, giving a square root and a fourth root,
and the chunk count depends on them.

## Known upstream defect

The key expansion `str(frac)[2:][:6]` assumes the fractional part of the square
root always renders with at least six decimals. Exactly representable short
values silently yield short keys: `0.5` gives `'5'`, `0.25` gives `'25'`,
`0.125` gives `'125'`, and `0.0` gives `'0'`.

A key of exactly `'0'` is fatal. `findkey()` then computes
`range(int(key) - 1, ...)` as `range(-1, 10)`, and the negative index wraps to
the last character of `pidecimals`, which is a newline:

```
creategrid('0') -> ValueError: invalid literal for int() with base 10: '\n'
```

Observed in roughly 1.75 percent of 14-character HARD-mode runs. It affects the
encode path in `genkeylist` and the decode path in `main.py`, which share the
arithmetic. The HARD level is the only one affected; EASY and MODERATE are
clean. `selftest.py` reports those runs rather than crashing.

## Files

| File | Role |
|---|---|
| `main.py` | upstream interactive CLI, levels EASY, MODERATE and HARD |
| `PiDigits.TXT` | pi decimal expansion, 1,000,001 characters |
| `LICENSE` | upstream GPL-3.0, retained verbatim |
| `UPSTREAM_COMMIT` | pinned upstream commit sha |
| `selftest.py` | deterministic round-trip harness, added locally |
| `PROVENANCE.md` | this file |

## Usage

```sh
python3 tools/matrix_enc_ref/selftest.py 400
python3 tools/matrix_enc_ref_selftest.py
```

## Algorithmic summary

The construction is a 6x6 grid over `a-z0-9`. Each character encodes to
`column_label + row_label`, concatenated with no delimiter. The default labels
are `["1", "2", "1,1", "1,2", "2,1", "2,2"]`, which are unique within each axis
but contain commas, so tokenisation of the ciphertext is genuinely ambiguous.
Upstream acknowledges this in its own documentation.

A 12-digit rotation key rotates the six rows and then the six columns. The key
is the seed followed by the pi digits starting at the seed's index in
`PiDigits.TXT`.

- EASY uses one grid and one key, the seed, giving a single-character
  monoalphabetic substitution across the whole message.
- MODERATE splits the message into `floor` or `ceil(len ** 0.25)` parts, with a
  fresh grid and key per part, and joins the parts with a dot.
- HARD uses a fresh grid and key per character, regenerated from one 12-digit
  master key.

This is a positional substitution with a seeded key schedule. It is neither a
transposition nor a polyalphabetic Vigenere. Although the grid space is bounded
by `36!`, the seed is recovered directly from EASY output and fully determines
the grid, so the effective security is that of the seed alone.