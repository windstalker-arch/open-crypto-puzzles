#!/usr/bin/env python3
"""wl case-style battery (late-290).

github.com/s0md3v/wl is a wordlist case-STYLE converter: detect one casing style
and re-render every line into it. Its 15 documented styles are:
    foobar  foo_bar  fooBar  FooBar  FOOBAR  FOO_BAR
    foo-bar FOO-BAR  foo.bar FOO.BAR Foo.Bar Foo_Bar Foo-Bar foo.Bar foo_Bar foo-Bar

Prior sweeps in this folder only ever applied WHOLE-STRING case modes
{plain, UPPER, Title} to candidate passwords. The *mixed per-token* styles above
were never sent for the multi-word candidate phrases across their known word
boundaries, so this battery renders each candidate phrase under every wl style.
Each rendered line is fed to both certified oracles as X (raw AND sha256(X)-hex
x both EVP digests handled internally by the oracle).
"""
import sys

SEG = {
    # phrase -> known word segmentation (certified/traced in this folder)
    "enterthekey": ["enter", "the", "key"],
    "matrixsumlist": ["matrix", "sum", "list"],
    "thispassword": ["this", "password"],
    "lastwordsbeforearchichoice": ["last", "words", "before", "archi", "choice"],
    "cosmicduality": ["cosmic", "duality"],
    "salphasion": ["salphasion"],
    "salphaseion": ["salphaseion"],
    "thesedisplanted": ["these", "dis", "planted"],
    "theseedisplanted": ["the", "seed", "is", "planted"],
    "followthewhiterabbit": ["follow", "the", "white", "rabbit"],
    "thearchitectschoice": ["the", "architects", "choice"],
    "thearchitectchoice": ["the", "architect", "choice"],
    "hopeisthequintessentialhumandelusion": ["hope", "is", "the", "quintessential", "human", "delusion"],
    "yourlastcommand": ["your", "last", "command"],
    "secondanswer": ["second", "answer"],
    "whiterabbit": ["white", "rabbit"],
    "btcseed": ["btc", "seed"],
    "ourfirsthintisyourlastcommand": ["our", "first", "hint", "is", "your", "last", "command"],
    "enter": ["enter"],
    "salphasioncosmicduality": ["salphasion", "cosmic", "duality"],
    "matrixsumlistenter": ["matrix", "sum", "list", "enter"],
    "entermatrixsumlist": ["enter", "matrix", "sum", "list"],
    "lastwordsbeforearchichoicethispassword": ["last", "words", "before", "archi", "choice", "this", "password"],
    "thispasswordlastwordsbeforearchichoice": ["this", "password", "last", "words", "before", "archi", "choice"],
    "matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist": [
        "matrix", "sum", "list", "enter", "last", "words", "before", "archi",
        "choice", "this", "password", "matrix", "sum", "list"],
    "enterthekeymatrixsumlist": ["enter", "the", "key", "matrix", "sum", "list"],
    "matrixsumlistenterthekey": ["matrix", "sum", "list", "enter", "the", "key"],
}


def low(s):
    return s.lower()


def title(s):
    return s[0].upper() + s[1:].lower() if s else s


def high(s):
    return s.upper()


def render(segs, style):
    if style == "foobar":
        return "".join(low(t) for t in segs)
    if style == "fooBar":
        return low(segs[0]) + "".join(title(t) for t in segs[1:])
    if style == "FooBar":
        return "".join(title(t) for t in segs)
    if style == "FOOBAR":
        return "".join(high(t) for t in segs)
    if style == "foo_bar":
        return "_".join(low(t) for t in segs)
    if style == "FOO_BAR":
        return "_".join(high(t) for t in segs)
    if style == "Foo_Bar":
        return "_".join(title(t) for t in segs)
    if style == "foo-bar":
        return "-".join(low(t) for t in segs)
    if style == "FOO-BAR":
        return "-".join(high(t) for t in segs)
    if style == "Foo-Bar":
        return "-".join(title(t) for t in segs)
    if style == "foo.bar":
        return ".".join(low(t) for t in segs)
    if style == "FOO.BAR":
        return ".".join(high(t) for t in segs)
    if style == "Foo.Bar":
        return ".".join(title(t) for t in segs)
    if style == "foo.Bar":
        return low(segs[0]) + "".join("." + title(t) for t in segs[1:])
    if style == "foo-Bar":
        return low(segs[0]) + "".join("-" + title(t) for t in segs[1:])
    raise ValueError(style)


STYLES = ["foobar", "foo_bar", "fooBar", "FooBar", "FOOBAR", "FOO_BAR",
          "foo-bar", "FOO-BAR", "foo.bar", "FOO.BAR", "Foo.Bar",
          "Foo_Bar", "Foo-Bar", "foo.Bar", "foo-Bar"]


def main():
    cands = set()
    for phrase, segs in SEG.items():
        # the raw phrase itself (authoritative spelling) is always included
        cands.add(phrase)
        for style in STYLES:
            cands.add(render(segs, style))
    out = "\n".join(sorted(cands)) + "\n"
    sys.stdout.write(out)


if __name__ == "__main__":
    main()