#!/usr/bin/env python3
"""ThalesGroup/luna-openssl-provider (luna-openssl-provider) faithful family.

Repo = "Luna Crypto Provider (lunaprov)": a real OpenSSL 3.x provider plugin granting
access to crypto algorithms on Luna Network HSMs (PKCS#11 + liboqs PQC). No digit-stream
decoder, no keyed-28/VIC/stream machinery, no embedded puzzle content. Thematic tie to the
crux ONLY through naming: "provider" keywords as the interpreter alphabet, tested exactly
as the late-151 ASL handshape-family pattern (keyed28 certified checkerboard).

Bounded faithful family:
  (a) distinctive literals never oracled (grep-verified absent from tested.md): lunaprov,
      "Luna Crypto Provider", "Thales Luna Provider" (provider-name string in
      lunaProvider.c, #define LUNA_PROV_NAME_SZ), VERSION file 1.7beta16, source version
      1.7.9.3, oqsprov2, liboqs, pkcs11, keysecure/e_gem/sautil/passdll engineperf module
      names -- plus case variants, joins, and phase-3 'causality'-prefix joins.
  (b) provider-family keyword ALPHABETS through the CERTIFIED keyed-28 straddling
      checkerboard (certified_vic SELFCERT 3.2.2 PASS: FUBCDORA.LETHINGKYMVPS.JQZXW +
      escapes 1/4 reproduces the 3.2.2 VIC plaintext verbatim) applied to dbbib_91 /
      faed_570 under CANON/POS digit maps and the {1,4},{0,4},{1,2} escape pairs -- i.e.
      "OpenSSL provider name as the interpreter alphabet" exactly as the crux wording
      would predict.
"""
import json, pathlib

BASE = pathlib.Path(__file__).resolve().parents[1]
d = json.loads((BASE / "data" / "finalpage-digit-streams.json").read_text())
DBBIB = d["dbbib_91"]
FAED = d["faed_570"].rstrip("z")

CANON = {"d": 0, "b": 1, "i": 2, "f": 3, "h": 4, "c": 5, "e": 6, "g": 7, "a": 8}
POS = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9}
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed28(keyword):
    kw = "".join(ch for ch in keyword.upper() if ch in ALPHA)
    keyed = ""
    for ch in kw + ALPHA:
        if ch not in keyed:
            keyed += ch
    assert len(keyed) == 26, keyed
    return keyed[:8] + "." + keyed[8:18] + "/" + keyed[18:]


from certified_vic import build_grid, decode  # certified machinery (selfcert PASS)


def dig(s, mp):
    return "".join(str(mp[c]) for c in s)


LITERALS = [
    "lunaprov", "luna crypto provider", "luna crypto",
    "thales luna provider", "thales luna", "luna provider",
    "luna openssl provider", "luna-openssl-provider",
    "openssl provider", "open ssl provider", "crypto provider",
    "luna crypto provider 1.7beta16", "1.7beta16", "1.7.9.3",
    "oqsprov2", "oqs provider", "liboqs", "pkcs11", "pkcs 11",
    "keysecure", "e_gem", "sautil", "passdll", "engineperf",
    "luna network hsm", "luna network", "luna hsm provider",
]

FAM = ["lunaprov", "lunaprovider", "lunacryptoprovider", "lunacryptoprovider7beta16",
       "thaleslunaprovider", "thalesluna", "lunaopensslprovider", "lunaopenssl",
       "lunahsm", "lunahsmprovider", "lunahsmprovider12793", "lunanetworkhsm",
       "luna", "opensslprovider", "openSSLprovider", "cryptoprovider",
       "pkcs11", "pkcs", "liboqs", "oqsprov", "oqsprov2", "oqs",
       "keysecure", "egem", "gem", "sautil", "passdll", "engineperf",
       "thales", "gemalto", "safenet", "safenetluna", "gemaltoluna",
       "luna crypto", "lunaProvider", "LUNAProv"]

# causality-prefix joins (phase-3 password 'causality' + provider naming)
PREFIX_JOINS = ["causality" + "".join(ch for ch in f if ch in ALPHA).lower()
                for f in ["lunaprov", "thaleslunaprovider", "lunacryptoprovider",
                          "lunaopensslprovider", "lunaprovider"]] + [
    "causalitySafenetLunaProvider", "causalityLunaProvider",
    "causalityThalesLunaProvider", "CausalityLunaProvider",
]
PREFIX_JOINS += [p.upper() for p in PREFIX_JOINS]

KEYWORDS = FAM + [w.replace(" ", "") for w in LITERALS] + ["THALESLUNAPROVIDER",
              "LUNACRYPTAPROVIDER", "OPENSSLPROVIDER", "CRYPTAPROVIDER"]


def main():
    cands = {}
    for w in LITERALS + PREFIX_JOINS:
        for form in {w, w.upper(), w.lower(), w.replace(" ", ""),
                     w.replace(" ", "").upper()}:
            cands.setdefault(form, ("literal", w))
    for kw in KEYWORDS:
        alpha = keyed28(kw)
        for stream_name, stream in (("dbbib_91", DBBIB), ("faed_570", FAED)):
            for mpn, mp in (("canon", CANON), ("pos", POS)):
                ds = dig(stream, mp)
                for e1, e2 in [(1, 4), (0, 4), (1, 2)]:
                    ctol = build_grid(alpha, e1, e2)
                    dec = decode(ds, ctol, e1, e2)
                    for form in {dec, dec.lower(), dec[::-1]}:
                        cands.setdefault(form, ("keyed28", kw, stream_name, mpn, e1, e2))
    uniq = [(k, v) for k, v in cands.items() if k]
    with open("/data/data/com.termux/files/usr/tmp/opencode/lunaprov_cands.txt", "w") as f:
        f.write("\n".join(k for k, _ in uniq) + "\n")
    with open("/data/data/com.termux/files/usr/tmp/opencode/lunaprov_prov.txt", "w") as f:
        for k, v in uniq:
            f.write(f"{k}\t{v}\n")
    print("candidates:", len(uniq))


if __name__ == "__main__":
    main()