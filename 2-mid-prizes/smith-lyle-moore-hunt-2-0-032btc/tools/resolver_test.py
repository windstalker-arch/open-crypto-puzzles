#!/usr/bin/env python3
"""Certified password oracle for the Smith/Lyle/Moore Glimmer hunt.

Posts to Wix's resolve_protected_page_urls endpoint. Extracts siteId/metaSiteId
straight from the homepage HTML so we never hardcode stale ids. Reads candidate
passwords from stdin (one per line), tests them against a given pageId, and
prints only hits (success=true).

Positive control: page 'neyhh' password 'Gilligan' -> success.
Negative control: any wrong password -> -17005 access denied.
"""
import json
import re
import subprocess
import sys
import time
import urllib.request

HOST = "https://www.smithlylemoore.com"
RESOLVER = "https://site-pages.wix.com/_api/wix-public-html-info-webapp/resolve_protected_page_urls"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
RT_S = 0.35  # seconds between requests, polite to avoid Cloudflare blocks


def fetch(url, data=None, headers=None, timeout=25):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace"), dict(r.headers)


def get_ctx():
    # 1) load homepage to get siteId + metaSiteId and warm up any cookies
    status, body, headers = fetch(HOST + "/treasure-hunt")
    site = re.search(r'"siteId":"([a-f0-9-]{36})"', body)
    meta = re.search(r'"metaSiteId":"([a-f0-9-]{36})"', body)
    if not site or not meta:
        raise RuntimeError("could not extract site/meta ids from homepage")
    return {"siteId": site.group(1), "metaSiteId": meta.group(1)}


def test_password(ctx, page_id, password):
    payload = {
        "siteId": ctx["siteId"],
        "metaSiteId": ctx["metaSiteId"],
        "pageId": page_id,
        "url": "",
        "profileUrl": "",
        "password": password,
    }
    data = json.dumps(payload).encode()
    headers = {
        "User-Agent": UA,
        "Content-Type": "application/json",
        "Origin": HOST,
        "Referer": HOST + "/",
    }
    try:
        status, body, _ = fetch(RESOLVER, data=data, headers=headers)
    except Exception as e:
        return None
    try:
        j = json.loads(body)
    except Exception:
        return None
    if j.get("success"):
        return True
    return False


def main():
    page_id = sys.argv[1] if len(sys.argv) > 1 else None
    if not page_id:
        print("usage: resolver_test.py <pageId>  (passwords on stdin)", file=sys.stderr)
        sys.exit(2)
    ctx = get_ctx()
    print(f"[ctx] siteId={ctx['siteId']} metaSiteId={ctx['metaSiteId']} testing page {page_id}",
          file=sys.stderr)

    total = 0
    hits = []
    for line in sys.stdin:
        pw = line.rstrip("\n").rstrip("\r")
        if not pw:
            continue
        total += 1
        ok = test_password(ctx, page_id, pw)
        if ok:
            hits.append(pw)
            print(f"HIT {page_id}: {pw!r}", flush=True)
        time.sleep(RT_S)
        if total % 100 == 0:
            print(f"[{page_id}] tested {total} ...", file=sys.stderr, flush=True)

    print(f"[{page_id}] done: {total} tested, {len(hits)} hits", file=sys.stderr)
    if hits:
        print("HITS=" + ",".join(repr(h) for h in hits))


if __name__ == "__main__":
    main()
