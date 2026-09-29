#!/usr/bin/env python3
"""R-COOKIE - what does the old gsmg.io site's *cookie* layer actually contain?

WHY THIS TOOL EXISTS
====================
A reader of the Cookies Policy PDF reasonably asks whether the archived site data
carries any cookie material worth having.  Until now the answer "there is nothing
here" was an argument from absence: nobody had actually parsed the front-end
bundles for cookie usage.  This tool parses them, and the answer is a mechanism
rather than a shrug:

F1. THE SPA NEVER WRITES A COOKIE.  `js-cookie` v2.2.0 is bundled, and the
    application uses it with exactly ONE verb - `remove` - on exactly one name,
    `token`.  There is no `set` and no `get` anywhere in the app bundle.  The one
    place a token is persisted client-side, the `SAVE_TOKEN` Vuex mutation, writes
    `localStorage.setItem('token', token)` and does not touch js-cookie at all.

F2. SO THE `token` COOKIE IS SERVER-SET, AND AUTH IS A BEARER CREDENTIAL, NOT A
    COOKIE SESSION.  Vuex `state.token` is initialised from
    `localStorage.getItem('token')`, and an axios request interceptor sends
    `request.headers['Authorization'] = 'Bearer ' + token`.  A token the app can
    only clear and never write, and which travels as a bearer header, is a token
    the server hands out per login.

F3. LOGOUT AND 401-FAILURE CLEAR BOTH STORES, WHICH IS THE SIGNATURE OF F1/F2.
    `FETCH_USER_FAILURE` and `LOGOUT` each call `localStorage.removeItem('token')`
    *and* `Cookies.remove('token')` - 2 sites each, byte-deterministic.  That is
    defensive cleanup of a server cookie the app cannot re-create, not app logic
    that uses it.

F4. THE BACKEND IS LARAVEL, PROVABLY.  The vendor bundle ships axios with
    `xsrfCookieName: 'XSRF-TOKEN'` and `xsrfHeaderName: 'X-XSRF-TOKEN'`, and 73
    archived SPA shells carry a `csrf-token` meta tag.  The app also has a
    response interceptor with an `isRefreshing` flag and a subscriber list, i.e. a
    refresh-token path - again a bearer flow, not a cookie session.

F5. THE ARCHIVE CONTAINS ZERO CAPTURED COOKIE VALUES.  399 files / 17,936,642
    bytes, no WARC, no HAR, no header capture, and no file begins with WARC magic.
    The single `set-cookie` string in the entire tree is js-cookie v2.2.0's own
    response-header parser source (identifiable by the neighbouring
    `ignoreDuplicateOf` table), not a captured header.  The archive is response
    BODIES only, so a token minted in a `Set-Cookie` header at login could never
    have been saved.  This is a structural closure, not an unexamined corner.

F6. THE GATE'S ONLY COOKIE IS A THROWAWAY CAPABILITY PROBE.  FingerprintJS 3.4.0
    writes `cookietest=1` to test whether cookies are enabled, then expires it in
    the same expression.  `visitorId` is a localStorage key, and the gate bounces
    `?tr_uuid=&fp=visitorId`.

F7. THE POLICY NAMES NO COOKIE, AND THE FRONT END NEEDED NONE.  The 2021-05-31
    Cookies Policy declares three classes (Necessary/Session, Notice-Acceptance,
    Functionality) but never names a cookie; the only user preference in the app,
    `nightmode`, is localStorage.  Policy and code agree: no preference cookie was
    ever implemented.

LEDGER DELTA.  Before this row, `analysis/tested.md` contained 0 occurrences of
`localStorage`, `js-cookie`, `XSRF` and "token cookie" - the mechanism was
unmined even though the bundles were parsed for routes and for library churn.
0 oracle calls.  NOT SOLVED, and not a lead: this closes an avenue rather than
opening one.

USAGE
=====
    python3 tools/cookie_audit.py --selftest
    python3 tools/cookie_audit.py --report
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

ARCHIVE_CANDIDATES = [
    Path(os.environ.get("GSMG_ARCHIVE", "")) if os.environ.get("GSMG_ARCHIVE") else None,
    Path("~/gsmg/gsmg-web-archive"),
    REPO / "archive",
]

OLD = "gsmg.io.old-site-2026-09-27"
APP = OLD + "/js/app_20190428.js"
VENDOR = OLD + "/js/vendor_20190428.js"
FPJS = OLD + "/alpha/js/fingerprint/iife.min.js"
POLICY = OLD + "/pdf/20210531-Cookies-Policy-v1.0.txt"

# The only js-cookie call shape the app uses, and the only name it is used on.
JSCOOKIE_CALL = re.compile(r"js_cookie___default\.a\.(\w+)\(\s*'([^']*)'")
LOCALSTORAGE_CALL = re.compile(r"localStorage\.(\w+)\(\s*('[^']*'|\"[^\"]*\")")
# A captured Set-Cookie *header line* - value-bearing, unlike a library string.
SET_COOKIE_HEADER = re.compile(rb"(?im)^[ \t]*Set-Cookie[ \t]*:")

# File-name shapes that would hold response headers, which the archive lacks.
CAPTURE_SUFFIX = re.compile(r"\.(warc(\.gz)?|har|hdr|headers?)$", re.I)


def find_archive() -> Path:
    for cand in ARCHIVE_CANDIDATES:
        if cand is None:
            continue
        p = cand.expanduser()
        if p.is_dir():
            return p
    raise SystemExit("archive not found; tried:\n  " + "\n  ".join(
        str((c or Path()).expanduser()) for c in ARCHIVE_CANDIDATES if c))


def read(root: Path, rel: str) -> str:
    p = root / rel
    if not p.exists():
        raise SystemExit("missing archive file: " + str(p))
    return p.read_text(encoding="utf-8", errors="replace")


def iter_files(root: Path):
    return sorted(p for p in root.rglob("*") if p.is_file())


def captured_cookie_files(root: Path) -> list[Path]:
    """Files carrying a real Set-Cookie header line (F5).  Library source that
    merely mentions the word does not qualify - the regex is line-anchored."""
    out = []
    for p in iter_files(root):
        try:
            data = p.read_bytes()
        except OSError:
            continue
        if SET_COOKIE_HEADER.search(data):
            out.append(p)
    return out


def header_capture_files(root: Path) -> list[Path]:
    return [p for p in iter_files(root) if CAPTURE_SUFFIX.search(p.name)]


def csrf_meta_files(root: Path) -> list[Path]:
    out = []
    for p in iter_files(root):
        if p.suffix.lower() not in (".html", ".htm", ".dec", ".json", ".txt", ""):
            continue
        try:
            if re.search(r"csrf-token", p.read_text(encoding="utf-8", errors="replace"), re.I):
                out.append(p)
        except OSError:
            continue
    return out


def save_token_body(app: str) -> str:
    """Isolate the SAVE_TOKEN Vuex mutation body (F1's positive proof)."""
    m = re.search(r"/\* SAVE_TOKEN \*/.{0,400}?\}\)", app, re.S)
    return m.group(0) if m else ""


def report(archive: Path) -> int:
    app, vendor, fp = (read(archive, r) for r in (APP, VENDOR, FPJS))
    files = iter_files(archive)
    nbytes = sum(p.stat().st_size for p in files)

    print("R-COOKIE  archive: %s" % archive)
    print("  %d files, %d bytes" % (len(files), nbytes))

    calls = JSCOOKIE_CALL.findall(app)
    verbs = sorted({v for v, _ in calls})
    names = sorted({n for _, n in calls})
    ls = LOCALSTORAGE_CALL.findall(app)
    ls_token = sorted((fn, k) for fn, k in ls if "token" in k)
    print("\nF1 SPA never writes a cookie")
    print("  js-cookie verbs used: %s   names: %s   call sites: %d"
          % (verbs or "NONE", names or "NONE", len(calls)))
    print("  localStorage('token') sites: %d  %s"
          % (len(ls_token), [f"{f}{k}" for f, k in ls_token]))
    body = save_token_body(app)
    print("  SAVE_TOKEN writes localStorage: %s   touches js-cookie: %s"
          % ("setItem" in body, "js_cookie" in body))

    print("\nF2 auth is a bearer header, not a cookie session")
    print("  state.token <- localStorage.getItem('token'): %s"
          % bool(re.search(r"token:\s*function\s*\(\)\s*\{[^}]*getItem\('token'\)", app, re.S)))
    print("  axios request interceptor sets Authorization: %s"
          % bool(re.search(r"request\.headers\['Authorization'\]\s*=\s*'Bearer '\s*\+\s*token", app)))

    print("\nF3 both stores cleared on logout / 401-failure")
    print("  localStorage.removeItem('token'): %d   Cookies.remove('token'): %d"
          % (sum(1 for f, k in ls if f == "removeItem" and "token" in k),
             sum(1 for v, n in calls if v == "remove" and n == "token")))

    print("\nF4 backend is Laravel")
    print("  axios xsrfCookieName: 'XSRF-TOKEN'  : %d"
          % vendor.count("xsrfCookieName: 'XSRF-TOKEN'"))
    print("  axios xsrfHeaderName: 'X-XSRF-TOKEN': %d"
          % len(re.findall(r"xsrfHeaderName:\s*'X-XSRF-TOKEN'", vendor)))
    shells = csrf_meta_files(archive)
    print("  archived shells with a csrf-token meta: %d" % len(shells))
    print("  js-cookie library version: %s"
          % (re.search(r"JavaScript Cookie v([\d.]+)", vendor) or ["?"])[1] if
          re.search(r"JavaScript Cookie v([\d.]+)", vendor) else "not found")
    print("  response interceptor refresh path (isRefreshing): %d"
          % app.count("isRefreshing"))

    print("\nF5 zero captured cookie values in the archive")
    print("  files with a captured Set-Cookie header line: %d" % len(captured_cookie_files(archive)))
    print("  files named like a header/WARC capture       : %d" % len(header_capture_files(archive)))
    mentions = [p for p in files if b"set-cookie" in _safe(p).lower()]
    print("  files merely MENTIONING 'set-cookie'          : %d %s"
          % (len(mentions), [p.name for p in mentions]))
    if mentions:
        t = _safe(mentions[0]).decode("utf-8", "replace")
        i = t.lower().find("set-cookie")
        print("    -> library parser, not a header: %s"
              % ("ignoreDuplicateOf" in t[max(0, i - 400):i + 400]))

    print("\nF6/F7 gate probe and policy")
    print("  FingerprintJS version: %s" % sorted(set(re.findall(r'version:"([\d.]+)"', fp))))
    print("  cookietest probe writes: %d (written then expired in one expression)"
          % fp.count("cookietest=1"))
    if (archive / POLICY).exists():
        pol = read(archive, POLICY)
        classes = re.findall(r"●\s*([A-Z][A-Za-z /]+Cookies)", pol)
        print("  policy classes declared: %s" % classes)
        print("  policy names any cookie: %s"
              % bool(re.search(r"cookie (?:named|called)|`\w+=|PHPSESSID|laravel_session", pol, re.I)))
    print("  nightmode preference stored in: %s"
          % ("localStorage" if "localStorage" in app and "nightmode" in app else "?"))
    return 0


def _safe(p: Path) -> bytes:
    try:
        return p.read_bytes()
    except OSError:
        return b""


def selftest() -> int:
    root = find_archive()
    app, vendor, fp = (read(root, r) for r in (APP, VENDOR, FPJS))
    ok, fail = 0, []

    def check(name: str, cond: bool) -> None:
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append(name)

    calls = JSCOOKIE_CALL.findall(app)
    ls = LOCALSTORAGE_CALL.findall(app)
    body = save_token_body(app)

    # F1 - the app uses js-cookie with one verb, on one name, and never writes.
    check("F1 only the 'remove' verb is used", {v for v, _ in calls} == {"remove"})
    check("F1 only the name 'token' is used", {n for _, n in calls} == {"token"})
    check("F1 exactly 2 remove sites", sum(1 for v, _ in calls if v == "remove") == 2)
    check("F1 no js-cookie set verb", "js_cookie___default.a.set(" not in app)
    check("F1 no js-cookie get verb", "js_cookie___default.a.get(" not in app)
    # F1's positive proof: the persistence site is localStorage, not a cookie.
    check("F1 SAVE_TOKEN body located", bool(body))
    check("F1 SAVE_TOKEN writes localStorage", "setItem" in body)
    check("F1 SAVE_TOKEN does not touch js-cookie", "js_cookie" not in body)
    check("F1 localStorage token sites are 1 set / 1 get / 2 remove",
          sorted((f, k) for f, k in ls if "token" in k) ==
          [("getItem", "'token'"), ("removeItem", "'token'"),
           ("removeItem", "'token'"), ("setItem", "'token'")])

    # F2 - bearer, not cookie session.
    check("F2 token state is seeded from localStorage",
          bool(re.search(r"token:\s*function\s*\(\)\s*\{[^}]*getItem\('token'\)", app, re.S)))
    check("F2 Authorization Bearer interceptor present",
          bool(re.search(r"request\.headers\['Authorization'\]\s*=\s*'Bearer '\s*\+\s*token", app)))
    check("F2 interceptor reads the auth/token getter",
          "'auth/token'" in app)

    # F4 - Laravel.
    check("F4 axios xsrfCookieName is XSRF-TOKEN",
          vendor.count("xsrfCookieName: 'XSRF-TOKEN'") == 1)
    check("F4 axios xsrfHeaderName is X-XSRF-TOKEN",
          len(re.findall(r"xsrfHeaderName:\s*'X-XSRF-TOKEN'", vendor)) == 1)
    check("F4 js-cookie v2.2.0 banner", "JavaScript Cookie v2.2.0" in vendor)
    check("F4 at least one shell carries a csrf-token meta", len(csrf_meta_files(root)) >= 1)
    check("F4 refresh-token interceptor present", app.count("isRefreshing") >= 2)

    # F5 - the negative that closes the avenue, with a WORKING detector.
    captured = captured_cookie_files(root)
    check("F5 zero captured Set-Cookie headers in the archive", not captured)
    check("F5 no WARC/HAR/header-capture files", not header_capture_files(root))
    mentions = [p for p in iter_files(root) if b"set-cookie" in _safe(p).lower()]
    check("F5 the only 'set-cookie' mention is the js-cookie parser",
          len(mentions) == 1 and "ignoreDuplicateOf" in _safe(mentions[0]).decode("utf-8", "replace"))

    # F6 - the gate probe.
    check("F6 FingerprintJS 3.4.0", 'version:"3.4.0"' in fp)
    check("F6 cookietest probe written and expired", fp.count("cookietest=1") == 2)

    # F7 - policy and code agree on no preference cookie.
    pol = read(root, POLICY)
    check("F7 policy declares exactly 3 cookie classes",
          len(re.findall(r"●\s*[A-Z][A-Za-z /]+Cookies", pol)) == 3)
    check("F7 policy names no cookie value", "laravel_session" not in pol and "PHPSESSID" not in pol)
    check("F7 nightmode is a localStorage key, not a cookie",
          "localStorage" in app and "'nightmode'" in app
          and "js_cookie___default.a.set('nightmode'" not in app)

    # ---- NEGATIVE CONTROLS: the detectors must be able to fire. ----
    # Without these, F1 and F5 are unfalsifiable: "we found nothing" would be
    # indistinguishable from "we looked for the wrong thing".
    synth = "x.js_cookie___default.a.set('token', t);"
    check("NC-A a bundle that WRITES the cookie is detected as writing",
          {v for v, _ in JSCOOKIE_CALL.findall(synth)} == {"set"})
    check("NC-A a bundle that READS the cookie is detected as reading",
          {v for v, _ in JSCOOKIE_CALL.findall("js_cookie___default.a.get('token')")} == {"get"})
    hdr = b"HTTP/1.1 200 OK\r\nSet-Cookie: token=eyJhbGciOi\r\n\r\n"
    check("NC-B a real Set-Cookie header line IS detected",
          bool(SET_COOKIE_HEADER.search(hdr)))
    check("NC-B library-source mention is NOT a false positive",
          not SET_COOKIE_HEADER.search(b"if (key === 'set-cookie') { parsed[key] = ..."))
    check("NC-B the archive detector returns zero on the real archive",
          captured_cookie_files(root) == [])
    synth2 = "/* SAVE_TOKEN */ function(){js_cookie___default.a.set('token', t);}) rest"
    check("NC-C SAVE_TOKEN detector fires on a cookie-writing mutation",
          "js_cookie" in save_token_body(synth2) and "'token'" in save_token_body(synth2))
    check("NC-C SAVE_TOKEN detector is blind to an unrelated mutation",
          save_token_body("/* LOGOUT */ function(){localStorage.removeItem('token');}) rest") == "")

    print("SELFTEST %s %d/%d" % ("PASS" if not fail else "FAIL " + ",".join(fail), ok, ok + len(fail)))
    return 0 if not fail else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--archive", type=Path, default=None)
    a = ap.parse_args()
    if a.archive:
        globals()["ARCHIVE_CANDIDATES"] = [a.archive]
    if a.selftest:
        return selftest()
    report(find_archive() if a.archive is None else a.archive.expanduser())
    return 0


if __name__ == "__main__":
    sys.exit(main())
