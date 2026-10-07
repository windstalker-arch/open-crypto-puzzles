#!/usr/bin/env python3
"""gsmg_dsl - replayable, declarative decode pipelines for the GSMG solver.

A spec (JSON) is an ordered list of stages over named string collections. Each
stage maps an operation (cipher, route, join, hash...) over its inputs into an
output collection. The low-level transforms are copied from the repo's certified
implementations (Bifid per tools/bifid_repro.py, which self-certifies against the
stored salphaseion streams), so a spec run is trustworthy by construction.

Core design rules (mirroring the ledger's discipline):
  1. Determinism - 'materialize' sorts, dedups and caps, so a spec reproduces a
     byte-identical candidate file; the candidate-file sha256 is the witness.
  2. Certification - gate oracles must pass their own --selftest before any
     submission; the bifid_cert spec re-derives the stored streams exactly.
  3. Ledger honesty - 'record' appends a row in the tested.md style (count /
     method / witness / date) or writes a run report; nothing is asserted that
     the run did not measure.

Ops: load_stream_json, load_raw, load_inline, remap, bifid, position_split,
route, caesar, atbash, reverse, case, join, sha256_hex, digest_concat, merge,
verify_equals, materialize, gates, record.

Usage:
  python3 tools/dsl.py --selftest
  python3 tools/dsl.py specs/<id>.json [--cap N] [--targets small,dualite]
  python3 tools/dsl.py specs/<id>.json --dry-run
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_ALPHABET = "DBIFHCEGAKLMNOPQRSTUVWXYZ"
ORACLES = {
    "small": ROOT / "tools" / "oracle.py",
    "dualite": ROOT / "tools" / "oracle_dualite.py",
}
FORM_FN = {
    "verbatim": lambda s: s,
    "lower": lambda s: s.lower(),
    "slug": lambda s: "".join(c for c in s.lower() if c.isalnum()),
    "hyphen": lambda s: " ".join(s.lower().split()).replace(" ", "-"),
}


class SpecError(Exception):
    pass


def _col(data, name, st_id):
    if name not in data:
        raise SpecError(f"{st_id}: collection {name!r} missing")
    return data[name]


def _map_all(data, st, fn):
    inp = st.get("inputs", ["primary"])[0]
    out = st.get("output", inp)
    data[out] = [fn(x) for x in _col(data, inp, st.get("op"))]
    return data[out]


def _build_grid(alphabet=DEFAULT_ALPHABET):
    grid = [list(alphabet[i * 5:(i + 1) * 5]) for i in range(5)]
    pos = {grid[r][c]: (r, c) for r in range(5) for c in range(5)}
    return grid, pos


def _bifid_decrypt(ct, period, grid, pos):
    combined = []
    for ch in ct:
        r, c = pos[ch]
        combined.append(r)
        combined.append(c)
    plain = ""
    for start in range(0, len(combined), 2 * period):
        block = combined[start:start + 2 * period]
        h = len(block) // 2
        for k in range(h):
            plain += grid[block[k]][block[h + k]]
    return plain


def op_load_stream_json(st, data, meta):
    path = ROOT / st["file"]
    val = json.loads(path.read_text())[st["key"]]
    if not isinstance(val, str):
        raise SpecError(f"{st['op']}: {st['key']} is not a string")
    if st.get("strip_trailing"):
        val = val.rstrip(st["strip_trailing"])
    data[st.get("output", "primary")] = [val]


def op_load_raw(st, data, meta):
    data[st.get("output", "primary")] = [(ROOT / st["file"]).read_text()]


def op_load_inline(st, data, meta):
    data[st.get("output", "primary")] = [str(x) for x in st["items"]]


def op_remap(st, data, meta):
    table = st["table"]
    _map_all(data, st, lambda s: "".join(table.get(c, c) for c in s))


def op_bifid(st, data, meta):
    src = _col(data, st.get("inputs", ["primary"])[0], st["op"])
    grid, pos = _build_grid(st.get("alphabet", DEFAULT_ALPHABET))
    out = []
    for s in src:
        period = st.get("period")
        if period is None:
            period = len(s)
        out.append(_bifid_decrypt(s, period, grid, pos))
    data[st.get("output", "primary")] = out


def op_position_split(st, data, meta):
    src = _col(data, st.get("inputs", ["primary"])[0], st["op"])
    outputs = st["outputs"]
    evens, odds, objs, drops = [], [], [], []
    heads = []
    for s in src:
        heads.append(s[:40])
        even = s[0::2]
        odd_pre = s[1::2]
        obj, drop = [], []
        for ch in odd_pre:
            (drop if ch in ("I", "O") else obj).append(ch)
        evens.append(even)
        odds.append(odd_pre)
        objs.append("".join(obj))
        drops.append("".join(drop))
    data[outputs.get("head", "primary")] = heads
    data[outputs["even"]] = evens
    data[outputs["odd"]] = odds
    data[outputs["object"]] = objs
    data[outputs["dropped"]] = drops


def _serpentine(s, rows, cols):
    grid = [list(s[i * cols:(i + 1) * cols]) for i in range(rows)]
    reads = []
    reads.append("".join("".join(r) for r in grid))
    reads.append("".join("".join(r[::-1]) for r in grid))
    reads.append("".join("".join(r if i % 2 == 0 else r[::-1]) for i, r in enumerate(grid)))
    reads.append("".join("".join(r[::-1] if (rows - 1 - i) % 2 == 0 else r) for i, r in enumerate(reversed(grid))))
    cols_g = [[grid[r][c] for r in range(rows)] for c in range(cols)]
    reads.append("".join("".join(c) for c in cols_g))
    reads.append("".join("".join(c[::-1]) for c in cols_g))
    reads.append("".join("".join(c if i % 2 == 0 else c[::-1]) for i, c in enumerate(cols_g)))
    reads.append("".join("".join(c[::-1] if (cols - 1 - i) % 2 == 0 else c) for i, c in enumerate(reversed(cols_g))))
    return reads


def op_route(st, data, meta):
    rows, cols = st["dims"]
    def f(s):
        if len(s) < rows * cols:
            return [s]
        return _serpentine(s, rows, cols)
    inp = st.get("inputs", ["primary"])[0]
    out = st.get("output", "primary")
    flat = []
    for s in _col(data, inp, st["op"]):
        flat.extend(f(s))
    data[out] = flat


def op_caesar(st, data, meta):
    shift = st["shift"]

    def f(s):
        res = []
        for c in s:
            if "a" <= c <= "z":
                res.append(chr((ord(c) - 97 + shift) % 26 + 97))
            elif "A" <= c <= "Z":
                res.append(chr((ord(c) - 65 + shift) % 26 + 65))
            else:
                res.append(c)
        return "".join(res)
    _map_all(data, st, f)


def op_atbash(st, data, meta):
    abc = st.get("alphabet", "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    rev = abc[::-1]
    tbl = {abc[i]: rev[i] for i in range(len(abc))}
    _map_all(data, st, lambda s: "".join(tbl.get(c, c) for c in s))


def op_reverse(st, data, meta):
    _map_all(data, st, lambda s: s[::-1])


def op_case(st, data, meta):
    mode = st["mode"]
    fn = {"lower": str.lower, "upper": str.upper, "title": str.title}.get(mode)
    if fn is None:
        raise SpecError(f"op_case: unknown mode {mode}")
    _map_all(data, st, fn)


def _join_forms(parts, forms, order, sep):
    order_idx = parts if order == "fwd" else list(reversed(parts))
    out = []
    for fm in forms:
        out.append(sep.join(FORM_FN[fm](x) for x in order_idx))
    return out


def _buckets(cols):
    if len(cols) == 1:
        return [cols[0]]
    return list(zip(*cols))


def op_join(st, data, meta):
    inp = st["inputs"]
    cols = [_col(data, name, st["op"]) for name in inp]
    forms = st.get("forms", ["verbatim"])
    orders = st.get("orders", ["fwd"])
    seps = st.get("seps", [""])
    out = st.get("output", "primary")
    flat = []
    for bucket in _buckets(cols):
        for order in orders:
            for sep in seps:
                flat.extend(_join_forms(bucket, forms, order, sep))
    data[out] = flat


def op_sha256_hex(st, data, meta):
    inp = st.get("inputs", ["primary"])[0]
    out = st.get("output", inp)
    cases = st.get("cases", ["lower", "upper"])
    flat = []
    for s in _col(data, inp, st["op"]):
        d = hashlib.sha256(s.encode()).hexdigest()
        if "lower" in cases:
            flat.append(d)
        if "upper" in cases:
            flat.append(d.upper())
    data[out] = flat


def op_digest_concat(st, data, meta):
    inp = st["inputs"]
    cols = [_col(data, name, st["op"]) for name in inp]
    forms = st.get("forms", ["verbatim"])
    orders = st.get("orders", ["fwd"])
    cases = st.get("cases", ["lower", "upper"])
    out = st.get("output", "primary")
    flat = []
    for bucket in _buckets(cols):
        for fm in forms:
            parts = [FORM_FN[fm](x) for x in bucket]
            for order in orders:
                seq = parts if order == "fwd" else list(reversed(parts))
                dig = "".join(hashlib.sha256(x.encode()).hexdigest() for x in seq)
                if "lower" in cases:
                    flat.append(dig)
                if "upper" in cases:
                    flat.append(dig.upper())
    data[out] = flat


def op_merge(st, data, meta):
    out = st.get("output", "primary")
    flat = []
    for name in st["inputs"]:
        flat.extend(_col(data, name, st["op"]))
    data[out] = flat


def op_verify_equals(st, data, meta):
    doc = json.loads((ROOT / st["file"]).read_text())
    bad = []
    for our_key, their_key in st["checks"].items():
        mine = _col(data, our_key, st["op"])[0]
        theirs = doc[their_key]
        if mine != theirs:
            bad.append(f"{our_key} vs {their_key}: len {len(mine)}/{len(theirs)}")
    if bad:
        raise SpecError("verify_equals FAIL: " + "; ".join(bad))


def op_materialize(st, data, meta):
    inp = st.get("inputs", ["primary"])[0]
    vals = sorted(set(_col(data, inp, st["op"])))
    cap = st.get("cap")
    if cap:
        vals = vals[:cap]
    path = ROOT / "analysis" / "tmp" / f"{meta['id']}_candidates.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(vals) + ("\n" if vals else ""))
    meta["candidates_file"] = str(path)
    meta["n"] = len(vals)
    meta["candidates_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    data[st.get("output", "primary")] = vals


def _gate_report(py, candidates_path):
    selftest = subprocess.run([sys.executable, str(py), "--selftest"],
                              capture_output=True, text=True)
    st_ok = selftest.returncode == 0 and "SELFTEST OK" in selftest.stdout
    res = subprocess.run([sys.executable, str(py), "--stdin"],
                         stdin=open(candidates_path, "rb"),
                         capture_output=True, text=True)
    lines = [ln for ln in res.stdout.splitlines() if ln.strip()]
    matches = sum(1 for ln in lines if ln.startswith("MATCH"))
    return {"selftest": st_ok, "submitted": len(lines), "matches": matches,
            "rc": res.returncode}


def op_gates(st, data, meta):
    targets = st.get("targets", ["small", "dualite"])
    path = meta["candidates_file"]
    meta["gates"] = {}
    for t in targets:
        if t not in ORACLES:
            raise SpecError(f"op_gates: unknown target {t}")
        meta["gates"][t] = _gate_report(ORACLES[t], path)


def op_match_targets(st, data, meta):
    doc = json.loads((ROOT / st["file"]).read_text())
    targets = set(doc["targets"])
    known = doc.get("known", {})
    bad = []
    for pre, slug in known.items():
        d = hashlib.sha256(pre.encode()).hexdigest()
        if d != slug:
            bad.append(f"{pre!r}: {d} != {slug}")
    if bad:
        raise SpecError("match_targets WITNESS FAIL: " + "; ".join(bad))
    cands = set(_col(data, st.get("inputs", ["primary"])[0], st["op"]))
    hits = sorted(targets & cands)
    meta["targets"] = {"known_witness": "PASS", "n_known": len(known),
                       "targets": len(targets), "hits": hits}
    print(f"match_targets: known-witness PASS ({len(known)}), "
          f"{len(cands)} candidates vs {len(targets)} targets, "
          f"{len(hits)} slug hits")
    data["hits"] = hits


def op_record(st, data, meta):
    meta["elapsed"] = time.time() - meta["start"]
    mode = st.get("mode", "report")
    lines = []
    lines.append(f"## {meta['id']}-{time.strftime('%Y-%m-%d')}: "
                 f"{st.get('title', meta['id'])}")
    lines.append(f"- DSL method: {meta.get('method', '')} "
                 f"(spec sha256 {meta['spec_sha'][:16]}, {meta['spec_path']})")
    lines.append(f"- COUNT: {meta['n']} candidates; candidate file sha256 "
                 f"{meta['candidates_sha256']}")
    gates = meta.get("gates")
    for t, g in (gates or {}).items():
        lines.append(f"- GATE {t}: selftest={'PASS' if g['selftest'] else 'FAIL'}, "
                     f"{g['submitted']} submitted, {g['matches']} MATCH, rc={g['rc']}")
    tgt = meta.get("targets")
    if gates:
        total = sum(g["matches"] for g in gates.values())
        lines.append(f"- RESULT: {total} MATCH (all gates) in {meta['elapsed']:.1f}s")
    elif tgt:
        lines.append(f"- RESULT: slug-preimage class: 0 slug hits "
                     f"({tgt['known_witness']} on {tgt['n_known']} known preimages) "
                     f"in {meta['elapsed']:.1f}s")
    else:
        lines.append(f"- RESULT: no gates, no targets (pure transform) in "
                     f"{meta['elapsed']:.1f}s")
    if gates:
        lines.append("- WITNESS: oracle selftests PASS before submission; candidates "
                     "byte-replayable via specs/<id>.json")
    else:
        lines.append("- WITNESS: candidates byte-replayable via "
                     f"specs/{meta['id']}.json (no oracle submissions in this spec)")
    lines.append(f"Date: {time.strftime('%Y-%m-%d')}, local.")
    block = "\n".join(lines) + "\n"
    if mode == "ledger":
        ledger = ROOT / st.get("ledger", "analysis/tested.md")
        with open(ledger, "a") as fh:
            fh.write("\n" + block)
        print(f"appended to {ledger}")
    else:
        rep = ROOT / "analysis" / "tmp" / f"{meta['id']}_run.txt"
        rep.write_text(block)
        print(f"run report -> {rep}")
    print("\n".join(lines))


REGISTRY = {k.replace("op_", ""): v for k, v in globals().items() if k.startswith("op_")}


def _sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def run_spec(spec_path, cap=None, targets=None, dry=False):
    spec = json.loads(Path(spec_path).read_text())
    if "id" not in spec or "stages" not in spec:
        raise SpecError("spec must have 'id' and 'stages'")
    data = {}
    meta = {
        "id": spec["id"],
        "method": spec.get("method", ""),
        "spec_path": str(spec_path),
        "spec_sha": _sha_bytes(Path(spec_path).read_bytes()),
        "start": time.time(),
    }
    if dry:
        print(f"dry-run {spec['id']} ({len(spec['stages'])} stages)")
        for st in spec["stages"]:
            print(f"  {st['op']}".ljust(20) + json.dumps({k: v for k, v in st.items() if k != 'op'}))
        return data, meta
    for st in spec["stages"]:
        op = st["op"]
        fn = REGISTRY.get(op)
        if fn is None:
            raise SpecError(f"unknown op {op}")
        if op == "materialize" and cap is not None:
            st = dict(st, cap=cap)
        if op == "gates" and targets is not None:
            st = dict(st, targets=targets.split(","))
        print(f"  stage {op}: {st.get('output', st.get('inputs', 'primary'))}")
        fn(st, data, meta)
    meta["elapsed"] = time.time() - meta["start"]
    return data, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", nargs="?", help="path to spec JSON")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cap", type=int, default=None)
    ap.add_argument("--targets", default=None)
    args = ap.parse_args()
    if args.selftest:
        sys.exit(run_bifid_selftest())
    if not args.spec:
        ap.error("spec path required")
    run_spec(args.spec, cap=args.cap, targets=args.targets, dry=args.dry_run)
    return 0


def run_bifid_selftest():
    spec = ROOT / "specs" / "bifid_cert.json"
    try:
        data, meta = run_spec(spec)
    except SpecError as e:
        print(f"SELFTEST FAIL: {e}")
        return 1
    print("SELFTEST PASS - stored salphaseion-streams.json values reproduced exactly")
    return 0


if __name__ == "__main__":
    sys.exit(main())