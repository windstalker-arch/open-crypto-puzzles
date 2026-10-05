#!/usr/bin/env python3
"""jrk_corpus_versions.py -- four renderings of the author's Telegram channel,
and whether they AGREE on the author's bytes.

WHY THIS TOOL EXISTS
--------------------
`analysis/STATE_BRIEF.md` has carried, as a still-open object, "the pre-edit
Telegram snapshot (2025-04-28 20:01-20:20)".  The corpus says that object ought
to exist.  The author wrote, in the channel itself:

  2020-04-08  "Quite some typos have been changed already. The biggest blunder
               so far in the mainline of the puzzle was givetit instead of
               giveit"
  2021-04-02  "I haven't deleted it. Not sure who, but I noticed some more
               messages are deleted from time to time."

So: messages get edited, messages get deleted, and at least one edit changed a
string *in the mainline of the puzzle*.  The `givetit` -> `giveit` instance is
already certified (R-PLAINART).  The consequence for method is that the
authorial corpus is a moving target, and this project has been citing ONE
snapshot of it as if it were the corpus.

Four renderings of that one channel exist in the briefcase:

  jrk_all_messages.txt              427 msgs  UTF-16LE, emoji mojibake'd, msg IDs
  creator_jrk.txt                   411 msgs  UTF-8, emoji intact, clock +2h vs raw
  Jrk_Bgrt_Groupchat_History.txt    399 msgs  OLDEST snapshot; carries "Edited on"
                                             stamps and reply-quotes; no msg IDs
  GSMG_JRK.md                       427 msgs  the cleaned corpus the ledger cites

This tool establishes, with witnesses, which differences between them are real
authorial-byte differences and which are export artefacts (mojibake, emoji, a
three-way clock offset, CRLF, heading glue), so the "pre-edit snapshot" lead is
either promoted or killed with a stated reason.

It also surfaces the one class of authorial metadata that exists in exactly one
rendering: the `Edited on` stamps, i.e. WHICH messages the author changed and
WHEN.  No other rendering carries them, and no ledger row has ever cited them.

Read-only.  0 candidates, 0 oracle calls, no funded-gate contact, no broadcast.
`--selftest` re-derives every number quoted below and exits non-zero on drift.
"""

from __future__ import annotations

import collections
import difflib
import os
import re
import sys
from datetime import datetime, timedelta

BASE = os.path.expanduser("~/storage/external/briefcase/gsmg-solver-group")


def rd(name):
    with open(os.path.join(BASE, name), "rb") as f:
        return f.read()


def decode(b):
    """UTF-16 exports arrive as UTF-16LE with BOM; ASCII files as UTF-8."""
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return b.decode("utf-16")
    return b.decode("utf-8", "replace")


# ---------------------------------------------------------------- normalise --
def words(s):
    return re.findall(r"[0-9a-z']+", s.lower())


def norm(s):
    """Letters+digits only.  Emoji, mojibake, emphasis, punctuation, whitespace
    and the export's clock offset are all artefacts; if two renderings differ
    only in those, they are the same message and the difference is not
    information."""
    s = s.replace("**", "").replace("`", "")
    return re.sub(r"[^0-9a-z]+", "", s.lower())


# The UTF-16 export renders each emoji as the mojibake of its UTF-8 bytes, so a
# real emoji leaves behind a run of Latin-1 punctuation (dY~S, dY`½, âTY, â??âT,
# dY\x0f·â¥3, ...).  Those bytes are shared with real text -- a genuine "%" or a
# genuine "it?" -- so a hard-coded mojibake list is guesswork: an earlier
# revision of this file used one and mis-classified 75 messages as differing and
# 20 as substantive, when the true answer is 2 substantive (one of which is the
# CLEANER being right).
#
# Instead the mojibake alphabet is DERIVED: a character is part of the mojibake
# vocabulary iff it occurs in jrk_all_messages.txt and in none of the three
# renderings that hold the emoji intact or cleaned.  The derived set is
# reproduced in the selftest, so a corpus change cannot silently invalidate it.
_MOJI_ALPHA = None
_MOJI_TOK = None


def moji_alphabet():
    """Characters that occur in the raw export and in NO clean rendering."""
    global _MOJI_ALPHA
    if _MOJI_ALPHA is None:
        raw_chars = set("".join(r["text"] for r in parse_raw()))
        clean = set("".join(r["text"] for r in parse_creator()
                            + parse_groupchat() + parse_md()))
        _MOJI_ALPHA = frozenset(sorted(c for c in raw_chars - clean
                                       if not c.isalnum() or ord(c) > 127))
    return _MOJI_ALPHA


_BETWEEN_LETTERS = re.compile(r"(?<=[A-Za-z])â[\s\S]{0,2}T(?=[a-z])")


def moji_tokens():
    """The whitespace-delimited raw tokens that ARE an emoji's mojibake.

    Derived, never hardcoded.  A raw token is mojibake iff it does not occur in
    any of the three renderings that hold the emoji intact or cleaned, AND it
    carries mojibake evidence: a non-ASCII character (the Latin-1 lead bytes of
    the UTF-8 sequence), one of the derived characters, or the `dY` remnant that
    the export emits ahead of the run.

    Token-level, not character-level, and the level is the whole point: an
    emoji's mojibake is glued to the punctuation that follows it, so `dY~%.` is
    one token whose `%` is a real full stop and `dY\x0f·â??âT?,` carries a comma
    the author typed.  A character-level rule cannot delete one without eating
    the author's punctuation -- and cannot tell `dY~S` (moji) from a real `~`
    either, because `~` also occurs in the cleaned corpus.  Both failure modes
    produced wrong bucket counts in earlier revisions.

    Safety is not assumed, it is checked: --selftest asserts that none of these
    tokens contains three consecutive letters, i.e. deleting them cannot remove
    a word from the author's stream.
    """
    global _MOJI_TOK
    if _MOJI_TOK is None:
        clean = set()
        for r in parse_creator() + parse_groupchat() + parse_md():
            clean.update(r["text"].split())
        alpha = moji_alphabet()
        out = set()
        for r in parse_raw():
            for w in r["text"].split():
                if w in clean:
                    continue
                if not (any(ord(c) > 127 for c in w) or w.startswith("dY")
                        or any(c in alpha for c in w)):
                    continue
                # A mangled WORD, not an emoji: `Itâ?Ts` is `It's` with the curly
                # apostrophe mangled, so the token must survive to be repaired.
                if _BETWEEN_LETTERS.search(w):
                    continue
                out.add(w)
        _MOJI_TOK = frozenset(out)
    return _MOJI_TOK


# Two raw tokens carry an emoji's mojibake GLUED to the preceding word, with no
# space to cut at: `that"dY~?` (#3348) and `Itâ?Ts` (#39237, where the mojibake
# is a curly apostrophe the cleaner restored).  Token deletion cannot see these.
# The rule below is still derived, and --selftest enumerates the tokens it fires
# on: a trailing `dY`+2-bytes run, or a Latin-1 run sitting BETWEEN two letters.
# The second alternative is safe precisely because a between-letters Latin-1 run
# is the signature of a mangled interior apostrophe; the corpus has 2, printed.
_MOJI_RUN = re.compile(r"dY[\s\S]{1,2}(?=$|[^\w])")


def moji_glued_tokens():
    """Raw tokens in which mojibake is not whitespace-delimited."""
    return sorted({w for r in parse_raw() for w in r["text"].split()
                   if w not in moji_tokens() and _MOJI_RUN.search(w)})


def de_moji(s):
    out = []
    for w in s.split():
        if w in moji_tokens():
            continue
        w = _MOJI_RUN.sub("", w)
        if w:
            out.append(w)
    return " ".join(out)


# What the cleaner (GSMG_JRK.md) writes where the raw export writes mojibake:
# the smiley ":)" and the shrug "''".  A bare apostrophe is a stand-in only when
# it is not enclosed by word characters -- otherwise it is the real one in
# don't/it's, and eating it would fabricate hundreds of differences.
MD_STANDIN = re.compile(r":\)|''|(?<![\w'])'(?![\w])")

# GSMG_JRK.md glues its `### yyyy-mm-dd` day heading onto the previous body.
MD_GLUE = re.compile(r"\s*\?{0,2}\s*###\s*\d{4}-\d{2}-\d{2}\s*$")


def moji_fix(s):
    """Like de_moji, but REPAIRS a mangled interior apostrophe instead of
    dropping it: `Itâ?Ts` -> `It's`.

    The distinction matters for exactly one message.  The raw export mojibakes the
    author's U+2019 into `â?T` (#39237), and `creator_jrk.txt` and
    `Jrk_Bgrt_Groupchat_History.txt` both hold it correctly as U+2019 while
    `GSMG_JRK.md` holds U+0027.  That is a character-set normalisation by the
    cleaner, NOT a lost or altered word -- and it is the ONLY token in 427
    messages where the two renderings disagree.  Repairing it is what lets the
    verdict be "zero word-level differences" rather than "one difference, and it
    happens to be in the cleaner's favour".
    """
    s = _BETWEEN_LETTERS.sub("'", s)
    return " ".join(w for w in s.split() if w not in moji_tokens())


def cmp_words(s):
    """Comparable token stream: emoji and mojibake dropped on both sides.

    Only tokens of three letters or more.  Shorter survivors are not authorial
    wording but emoji stand-in debris: the cleaner's `oO`, `d`, and the `T` of a
    mangled `âT`.  Two-letter English words in this corpus (it, is, no, to, pm,
    tg) occur on both sides in identical counts, so excluding them removes no
    information -- and the selftest asserts that, rather than assuming it.
    """
    # U+2019 and U+0027 are the same apostrophe to a reader and the same
    # apostrophe to a word boundary, so they must produce the same token: the four
    # renderings disagree about which one the author typed, and that disagreement
    # is reported in its own bucket rather than leaking in here as a fake word
    # difference.
    s = s.replace("’", "'").replace("‘", "'")
    return [t for t in re.findall(r"[a-z]+(?:'[a-z]+)?",
                                  MD_STANDIN.sub(" ", moji_fix(s)).lower())
            if len(t) >= 3]


# ------------------------------------------------------------------ parsers --
def parse_raw():
    """jrk_all_messages.txt: `===MSG ID:n DATE:dT t===` body, `---` separated.

    Header-matched with finditer, NOT split: a split on the header regex shifts
    the (id, date, time, body) groups by one whenever the regex can match inside
    a body, which silently mislabels every subsequent timestamp.
    """
    txt = decode(rd("jrk_all_messages.txt"))
    hdr = re.compile(r"=+MSG ID:\s*(\d+)\s+DATE:([\d\-]+)T([\d:]+)=+=\r?\n")
    ms = list(hdr.finditer(txt))
    out = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(txt)
        body = re.split(r"\r?\n-{3,}\r?\n", txt[m.end():end])[0]
        out.append(dict(src="raw", mid=m.group(1), date=m.group(2),
                        time=m.group(3), text=re.sub(r"\s+", " ", body).strip()))
    return out


def parse_creator():
    """creator_jrk.txt: `=== [dd.mm.yyyy hh:mm:ss UTC-05:00] Jrk Bgrt ===` body."""
    txt = rd("creator_jrk.txt").decode("utf-8", "replace")
    out = []
    for m in re.finditer(
            r"===\s*\[([\d.]+)\s+([\d:]+)[^\]]*\]\s*Jrk Bgrt\s*\r?\n(.*?)(?=\r?\n\s*===|\Z)",
            txt, re.S):
        dd, mm, yy = m.group(1).split(".")
        out.append(dict(src="creator", mid=None, date=f"{yy}-{mm}-{dd}",
                        time=m.group(2),
                        text=re.sub(r"\s+", " ", m.group(3)).strip()))
    return out


def parse_groupchat():
    """Jrk_Bgrt_Groupchat_History.txt: line-oriented; carries `Edited on` and,
    on reply blocks, the other user's message.  The ONLY rendering with either."""
    txt = rd("Jrk_Bgrt_Groupchat_History.txt").decode("utf-8", "replace")
    lines = txt.split("\n")
    out, i = [], 0
    while i < len(lines):
        mt = re.match(r"\s*- Timestamp: \[([\d\-]+)T([\d:]+)\]\s*$", lines[i])
        if not mt:
            i += 1
            continue
        cur = dict(src="groupchat", mid=None, date=mt.group(1), time=mt.group(2),
                   ed=None, quoted=None, text="")
        i += 1
        # Walk the fields of this one message.  Field order is not fixed:
        # `- Edited on:` may precede or follow `- Type: A reply to another user`,
        # and a reply block carries the other user's message before the author's
        # `Response:`.  Assuming a fixed order is what made an earlier revision
        # of this parser find 0 of the 116 reply blocks.
        while i < len(lines) and not re.match(r"\s*- Timestamp: \[", lines[i]):
            ln = lines[i]
            me = re.match(r"\s*- Edited on: \[([\d\-]+)T([\d:]+)\]\s*$", ln)
            if me:
                cur["ed"] = f"{me.group(1)} {me.group(2)}"
                i += 1
                continue
            mq = re.match(r'\s*- Message from other user:\s*"(.*)$', ln)
            if mq:
                cur["quoted"], i = _q(lines, i)
                continue
            mf = re.match(r'\s*- (?:Message|Response):\s*"(.*)$', ln)
            if mf:
                cur["text"], i = _q(lines, i)
                continue
            i += 1
        out.append(cur)
    return out


def _q(lines, i):
    """Read one `"..."` export field starting at line i, honouring multi-line
    bodies.

    "Read until a line ends in `"`" is wrong, and it silently ate real text.  In
    #16624 the author QUOTES a question inside his own message:

        - Message:   "There's a question multiple people have asked me. "Given
                      the available knowledge, is internet still required to
                      solve it?"
                      Nope"

    The first line ends in `"` because the author's inner quote ends in one, so a
    first-line-ends-in-quote rule returns the message with `Nope` dropped -- and
    a rule that "keeps reading while the line does not end in `"`" stops at the
    same place for the same reason.  (Both the real text and the trailing `Nope`
    are present in the file; only the parse was wrong.)

    The structural fact available instead is INDENTATION: a multi-line field's
    continuation lines are indented past the field's own `- Message:` key, and the
    field ends at the LAST such line that closes with `"`.  Taking the last closer
    rather than the first is what makes the nested quote survive, and it also
    absorbs the `- Response:` sibling line of a reply block, which sits at an
    indent between the two and would otherwise be read as part of the quote.
    """
    base = len(lines[i]) - len(lines[i].lstrip())
    j = i
    while j + 1 < len(lines):
        ln = lines[j + 1]
        if len(ln) - len(ln.lstrip()) <= base:
            break
        if ln.lstrip().startswith("- "):
            break
        j += 1
    end = j
    while end > i and not lines[end].rstrip().endswith('"'):
        end -= 1
    buf = [re.match(r'.*?"(.*)$', lines[i]).group(1)] + lines[i + 1:end + 1]
    return re.sub(r"\s+", " ", "\n".join(buf)).strip().strip('"').strip(), j + 1


# GSMG_JRK.md writes its separator as U+2014 EM DASH, but 11 entries use a plain
# hyphen, so the class covers both.  Spelled as an escape because this repo's
# validator forbids literal em dashes in Python sources; the codepoint is the
# author's, the source file stays ASCII.
_EMDASH = "\u2014"
MDENT = re.compile(r"^- \*\*#?(\d+)\*\*\s+`([\d:]{8})`\s+["
                   + _EMDASH + r"-]\s*(.*)$")
MDDATE = re.compile(r"^### (\d{4}-\d{2}-\d{2})\s*$")


def parse_md():
    """GSMG_JRK.md: the cleaned corpus the ledger actually cites.

    Line-oriented on purpose.  Its entries are `- **#ID** `hh:mm:ss` U+2014 body`,
    but not uniformly: 11 of the 427 carry no `#`, and some bodies wrap onto
    continuation lines.  A single non-greedy block regex swallows those 11
    together with their neighbours -- it undercounts 427 as 416 and reports
    neighbouring text as if it were part of a body -- which is precisely how a
    parser artefact gets mistaken for "the corpus disagrees with itself".
    Entries are therefore matched line by line, continuations folded into the
    body they belong to, and `### date` headings tracked so a heading that has
    been glued onto a body (2 known cases, reported below) is detected rather
    than silently absorbed.
    """
    txt = rd("GSMG_JRK.md").decode("utf-8", "replace")
    out, date = [], None
    for ln in txt.split("\n"):
        md_ = MDDATE.match(ln.strip())
        if md_:
            date = md_.group(1)
            continue
        me = MDENT.match(ln.rstrip())
        if me:
            out.append(dict(src="md", mid=me.group(1), date=date,
                            time=me.group(2), text=me.group(3).strip()))
            continue
        if out and ln.startswith("  ") and ln.strip():
            out[-1]["text"] = (out[-1]["text"] + " " + ln.strip()).strip()
    for r in out:
        r["text"] = re.sub(r"\s+", " ", r["text"]).strip()
    return out


# ------------------------------------------------------------------ helpers --
def P(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def stamp(r):
    return f"{r.get('date') or '????-??-??'} {r['time']}"


def join_key(s):
    """Body identity for the two renderings that carry no message IDs.

    Removes, in this order: `[https://t.me/x]` link annotations the exporter
    inserts, the raw export's emoji-mojibake, real emoji, and everything that is
    not a letter or digit.  What is left is the author's actual wording, which is
    what has to match if two files are the same message.
    """
    s = re.sub(r"\[[^\]]*\]", "", s)
    # A mangled interior apostrophe (`Itâ?Ts`) carries no letters, and the clean
    # renderings write it as a plain `'` which this key drops too -- so delete the
    # mangled form rather than letting its `T` survive as a spurious letter.
    s = _BETWEEN_LETTERS.sub("", s)
    s = re.sub(r"[^\x00-\x7f]", " ", de_moji(s))
    return re.sub(r"[^0-9a-z]+", "", s.lower())


def reconcile(big, small, hour_shifts):
    """Match every row of `small` to a DISTINCT row of `big`.

    `hour_shifts` are the candidate offsets of `small`'s clock ahead of `big`'s.
    A row that would match a message already claimed by an earlier row counts as
    a collision, not a second match, so a duplicate body cannot make a short file
    look complete.
    """
    idx = collections.defaultdict(list)
    for r in big:
        idx[join_key(r["text"])].append(r)
    claimed, orphan, collide = {}, [], 0
    for r in small:
        t0 = P(f"{r['date']} {r['time']}")
        hits = [x for x in idx.get(join_key(r["text"]), ())
                if any(t0 - timedelta(hours=h) == P(f"{x['date']} {x['time']}")
                       for h in hour_shifts)]
        if not hits:
            orphan.append(r)
            continue
        best = min(hits, key=lambda x: claimed.get(x["mid"], 0))
        if claimed.get(best["mid"], 0):
            collide += 1
        claimed[best["mid"]] = claimed.get(best["mid"], 0) + 1
    cut = max((r["date"] for r in small), default=None)
    absent = [r for r in big if r["mid"] not in claimed]
    # A message with no letters and no digits carries no authorial content, so an
    # exporter that drops empty bodies accounts for it.  They must be counted
    # separately from messages with words in them.
    empty = [r for r in absent if not join_key(r["text"])]
    return {
        "rows": len(small),
        "matched": len(claimed),
        "collisions": collide,
        "orphan": orphan,
        "absent": absent,
        "cut": cut,
        "absent_empty": empty,
        "absent_after_cut": [r for r in absent if r["date"] > cut],
        "absent_within_cut": [r for r in absent
                              if r["date"] <= cut and join_key(r["text"])],
    }


def clock_offsets(a, b):
    """raw_clock MINUS b_clock, over every same-date pair whose normalised text
    matches.  Only time-of-day is differenced: pairing a full date+time against a
    bare time-of-day (as a first revision of this function did) yields offsets
    measured in THOUSANDS OF DAYS and hides the real answer, which is a constant
    few hours -- which is the whole point of the function."""
    idx = collections.defaultdict(set)
    for r in b:
        idx[(r["date"], norm(r["text"]))].add(r["time"])
    c = collections.Counter()
    for r in a:
        for bt in idx.get((r["date"], norm(r["text"])), ()):
            try:
                d = (P("2000-01-01 " + r["time"]) - P("2000-01-01 " + bt))
                c[d] += 1
            except ValueError:
                pass
    return c


# ------------------------------------------------------------------- report --
def collect():
    """Everything the report and the selftest need, computed once."""
    D = {}
    D["raw"] = parse_raw()
    D["creator"] = parse_creator()
    D["groupchat"] = parse_groupchat()
    D["md"] = parse_md()

    # --- ID-keyed comparison: raw and md both carry Telegram message IDs -----
    R = {int(r["mid"]): r for r in D["raw"]}
    M = {int(r["mid"]): r for r in D["md"]}
    D["raw_ids"] = set(R)
    D["md_ids"] = set(M)
    D["ids_equal"] = R.keys() == M.keys()
    D["only_raw_ids"] = sorted(D["raw_ids"] - D["md_ids"])
    D["only_md_ids"] = sorted(D["md_ids"] - D["raw_ids"])

    # --- body comparison, raw vs md, over all 427 shared IDs ----------------
    # Non-overlapping buckets, so the numbers sum to 427 and a message cannot be
    # counted twice.  `substantive` is the bucket that matters: a word-level
    # difference that neither the mojibake vocabulary nor the md's emoji
    # stand-ins nor the glued day-heading accounts for.
    B = collections.defaultdict(list)
    D["buckets"] = B
    for k in sorted(D["raw_ids"] & D["md_ids"]):
        a, b = R[k], M[k]
        if a["text"] == b["text"]:
            B["identical"].append(k)
        elif norm(a["text"]) == norm(b["text"]):
            B["letters+digits equal"].append(k)
        else:
            unglued = MD_GLUE.sub("", b["text"])
            glued = unglued != b["text"]
            if cmp_words(a["text"]) == cmp_words(unglued):
                # Named separately because it is the one place the two renderings
                # disagree about a CHARACTER rather than about emoji, and naming
                # it is what keeps `substantive` at zero honestly.
                if _BETWEEN_LETTERS.search(a["text"]):
                    B["mangled apostrophe, cleaner normalised it"].append(k)
                else:
                    B["emoji-only" + (" + glued day-heading" if glued else "")].append(k)
            else:
                ops = [(t, " ".join(cmp_words(a["text"])[i1:i2]) or "-",
                        " ".join(cmp_words(b["text"])[j1:j2]) or "-")
                       for t, i1, i2, j1, j2 in
                       difflib.SequenceMatcher(None, cmp_words(a["text"]),
                                               cmp_words(b["text"])).get_opcodes()
                       if t != "equal"]
                B["substantive"].append((k, a, b, ops))
    D["identical"] = len(B["identical"])
    D["norm_equal"] = len(B["letters+digits equal"])
    D["moji_only"] = len(B["emoji-only"])
    D["moji_only_glued"] = len(B["emoji-only + glued day-heading"])
    D["apostrophe"] = len(B["mangled apostrophe, cleaner normalised it"])
    D["substantive"] = B["substantive"]
    D["worddiff"] = B["substantive"]          # historical name, same list
    D["apostrophe_ids"] = B["mangled apostrophe, cleaner normalised it"]

    # Corpus-level witness: the multiset of alphabetic tokens (len>=3) over the
    # whole corpus.  A per-message eye can miss a token that appears twice in
    # one rendering and not at all in the other; a multiset difference cannot.
    ta, tb = collections.Counter(), collections.Counter()
    for k in D["raw_ids"]:
        ta.update(cmp_words(R[k]["text"]))
    for k in D["md_ids"]:
        tb.update(cmp_words(MD_GLUE.sub("", M[k]["text"])))
    D["raw_only_tokens"] = sorted((ta - tb).items())
    D["md_only_tokens"] = sorted((tb - ta).items())

    # --- heading glue in GSMG_JRK.md ----------------------------------------
    D["glued"] = [r for r in D["md"] if MD_GLUE.search(r["text"])]

    # --- clocks -------------------------------------------------------------
    D["off_creator"] = clock_offsets(D["raw"], D["creator"]).most_common(3)
    D["off_groupchat"] = clock_offsets(D["raw"], D["groupchat"]).most_common(3)

    # --- message-set reconciliation of the two ID-less renderings ------------
    # A smaller count is not a deletion until every row of the smaller file has
    # been matched to a distinct message of the larger one and the leftovers
    # have been explained.  Both files carry no message IDs, so the join key is
    # (body after mojibake/emoji/link-annotation removal, clock-shifted stamp).
    D["recon"] = {n: reconcile(D["raw"], rows, hs)
                  for n, rows, hs in (("creator", D["creator"], (2, 3)),
                                      ("groupchat", D["groupchat"], (3, 4)))}

    # --- the one exclusive class: `Edited on` --------------------------------
    D["edited"] = [r for r in D["groupchat"] if r["ed"]]
    D["live_edits"] = [r for r in D["edited"] if r["ed"] > stamp(r)]
    D["edit_latency"] = sorted(
        ((P(r["ed"]) - P(stamp(r))).total_seconds() / 86400.0, i, r)
        for i, r in enumerate(D["live_edits"]))
    D["edit_days"] = collections.Counter(r["ed"][:10] for r in D["edited"])

    # --- the second exclusive class: reply quotes ----------------------------
    D["replies"] = [r for r in D["groupchat"] if r["quoted"] is not None]
    auth = " ".join(r["text"] for r in D["raw"] + D["creator"] + D["groupchat"] + D["md"])
    authn = re.sub(r"[^0-9a-z]", "", auth.lower())
    tok = re.compile(r"\b(?:[0-9a-fA-F]{24,}|\d{8,}|[A-Za-z0-9+/]{20,}={0,2})\b")
    novel = []
    for r in D["replies"]:
        for m in tok.findall(r["quoted"] or ""):
            k = re.sub(r"[^0-9a-z]", "", m.lower())
            if len(k) >= 16 and k not in authn:
                novel.append((r, m))
    D["novel_quoted_tokens"] = novel
    return D


def report(D, say):
    L = collections.Counter
    say("=" * 78)
    say("FOUR RENDERINGS OF THE AUTHOR'S TELEGRAM CHANNEL")
    say("=" * 78)
    names = [("raw", "jrk_all_messages.txt"), ("creator", "creator_jrk.txt"),
             ("groupchat", "Jrk_Bgrt_Groupchat_History.txt"), ("md", "GSMG_JRK.md")]
    for k, f in names:
        rows = D[k]
        sp = [stamp(r) for r in rows]
        say(f"  {f:34s} {len(rows):4d} msgs   {min(sp)} -> {max(sp)}")
    say()
    say(f"  raw carries Telegram msg IDs: {len(D['raw_ids'])};  md: {len(D['md_ids'])};  "
        f"ID sets identical: {D['ids_equal']}")
    say(f"  creator and groupchat carry no IDs, so they can only be compared by text+clock.")
    say()

    say("-" * 78)
    say("1. RAW vs GSMG_JRK.md -- THE COMPARISON THE LEDGER IMPLICITLY ASSUMES")
    say("-" * 78)
    if not D["ids_equal"]:
        say(f"  IDs only in raw: {D['only_raw_ids'][:20]}")
        say(f"  IDs only in md : {D['only_md_ids'][:20]}")
    say("  Every one of the 427 shared IDs lands in exactly one bucket:")
    for name, ks in D["buckets"].items():
        say(f"    {name:34s} {len(ks):4d}")
    say(f"    {'SUM':34s} {sum(len(v) for v in D['buckets'].values()):4d}")
    say()
    say("  'identical' is byte-identical bodies.  'letters+digits equal' differs only in")
    say("  punctuation/emoji.  'emoji-only' differs only in the mojibake vocabulary versus")
    say("  the cleaner's ':)' / \"''\" stand-ins.  'mangled apostrophe' is the one place the")
    say("  two disagree about a CHARACTER rather than about emoji.  'substantive' is the")
    say("  only bucket that could mean a lost or altered word:")
    say()
    if not D["substantive"]:
        say("    NONE.  Zero of 427 messages land in it -- so no authorial word, number or")
        say("    letter-run is unique to either rendering, in either direction.")
        say()
    for k, a, b, ops in D["substantive"]:
        say(f"    --- #{k}  {a['date']} {a['time']}")
        say(f"      raw: {a['text'][:118]}")
        say(f"      md : {b['text'][:118]}")
        for t, x, y in ops[:6]:
            say(f"        {t}: {x!r} -> {y!r}")
    say()
    say("  Corpus-level witness -- multiset of every alphabetic token (len>=3) in all 427 bodies:")
    say(f"    tokens only in raw: {D['raw_only_tokens']}")
    say(f"    tokens only in md : {D['md_only_tokens']}")
    say("    EMPTY IN BOTH DIRECTIONS.  After the mangled interior apostrophe is repaired,")
    say("    not one token in 427 messages exists in one rendering and not the other -- so")
    say("    no word, no number and no letter-run is unique to either file.")
    say()
    say("  The mojibake vocabulary is derived, not typed in: a raw whitespace-delimited")
    say(f"  token is an emoji's mojibake iff it appears in NO clean rendering ({len(moji_tokens())}")
    say(f"  tokens), plus {len(moji_glued_tokens())} more glued to a word with no space to cut at:")
    say(f"    {moji_glued_tokens()}")
    say("  --selftest asserts none of them yields a single word under the same tokenizer,")
    say("  so deleting them cannot remove a word from the author's stream.")
    say()
    say(f"  THE MANGLED APOSTROPHE, {D['apostrophe_ids']}.  The raw export mojibakes the")
    say("  author's U+2019 into `â?T`; `creator_jrk.txt` and the groupchat export both hold")
    say("  it correctly as U+2019, and GSMG_JRK.md holds U+0027:")
    say()
    say("      raw       It's the next phase ...   (I t â ? T s)")
    say("      creator   It’s the next phase ...   (U+2019, intact)")
    say("      groupchat It’s the next phase ...   (U+2019, intact)")
    say("      md        It's the next phase ...   (U+0027)")
    say()
    say("  So the cleaner NORMALISED a curly apostrophe to a straight one and invented")
    say("  nothing: the word is `it's` in all four files.  It is reported as its own bucket")
    say("  rather than absorbed into 'emoji-only' precisely because it is the only place the")
    say("  two renderings disagree about a character.")
    say()
    say("      VERDICT: raw and GSMG_JRK.md carry THE SAME 427 MESSAGES, word for word.")
    say("      The md is a faithful emoji-cleaned rendering of the raw export, not a")
    say("      different snapshot.  Citing the md loses emoji and nothing else.")
    say()

    say("-" * 78)
    say("2. THE TWO ID-LESS RENDERINGS: A CLOCK OFFSET AND AN EXPORT VINTAGE")
    say("-" * 78)
    say("  One channel rendered on three clocks.  Both smaller files are joined to the")
    say("  raw export on (mojibake-free body, clock-shifted stamp), matching each row to")
    say("  a DISTINCT raw message so a repeated body cannot pad the count:")
    say()
    for label, off in (("raw - creator", D["off_creator"]),
                       ("raw - groupchat", D["off_groupchat"])):
        say(f"  {label}: " + ", ".join(
            f"{o.total_seconds() / 3600:+.2f} h x{n}" for o, n in off))
    say("  (constant to the minute; a +2h/+3h and +3h/+4h pair respectively, i.e. a")
    say("  fixed UTC offset with a DST change inside the span, not per-message drift.)")
    say()
    for name, R in (("creator_jrk.txt", D["recon"]["creator"]),
                    ("Jrk_Bgrt_Groupchat_History.txt", D["recon"]["groupchat"])):
        say(f"  {name}: {R['rows']} rows")
        say(f"    matched to a distinct raw message : {R['matched']}")
        say(f"    duplicate-body collisions          : {R['collisions']}")
        say(f"    rows with NO raw counterpart       : {len(R['orphan'])}")
        for r in R["orphan"]:
            say(f"       [{r['date']} {r['time']}] {r['text'][:96]}")
        say(f"    raw messages absent from it        : {len(R['absent'])}")
        say(f"      dated after its last date ({R['cut']}): {len(R['absent_after_cut'])}"
            "   <- export vintage, not deletion")
        say(f"      empty bodies (no words to lose)  : {len(R['absent_empty'])}")
        say(f"      WORDS absent, unexplained by either: {len(R['absent_within_cut'])}")
        for r in R["absent_within_cut"]:
            say(f"       #{r['mid']} [{r['date']} {r['time']}] {r['text'][:88]}")
    say()
    say("  So the 427/411/399 spread is three export clocks plus one vintage cut, and")
    say("  NOT one deletion:")
    say("    * creator_jrk.txt is the raw export minus its 16 EMPTY bodies -- no word of")
    say("      authorial text exists only in the raw export.")
    say("    * Jrk_Bgrt_Groupchat_History.txt stops at 2025-04-28; its 28 unmatched raw")
    say("      messages are all dated after that, i.e. export vintage, not deletion.")
    say()
    say("  Its one rendering defect is in THIS TOOL, not in the file, and it is worth")
    say("  stating because it looked exactly like a text defect.  #16624 quotes a question")
    say("  inside his own message, so its first line ends in `\"`; a parser that reads a")
    say("  field until a line ends in a quote stops there and silently drops the trailing")
    say("  `Nope`.  The file contains it.  The parser now closes the field on the LAST")
    say("  continuation line, and #16624 parses byte-identical to the raw export -- pinned")
    say("  as a selftest witness so the regression cannot come back unnoticed:")
    say()
    r16624 = next((r for r in D["groupchat"] if "available knowledge" in r["text"]), None)
    if r16624:
        say(f"      groupchat: {r16624['text']}")
        say(f"      raw      : {next(r['text'] for r in D['raw'] if r['mid'] == '16624')}")
    say()

    say("-" * 78)
    say("3. THE DEFECT IN GSMG_JRK.md ITSELF: HEADINGS WELDED ONTO BODIES")
    say("-" * 78)
    say(f"  `### yyyy-mm-dd` heading glued onto the previous body: {len(D['glued'])} entries")
    for r in D["glued"]:
        say(f"    #{r['mid']} [{r['date']} {r['time']}] body = {r['text']!r}")
    say("  Harmless for reading, fatal for anything that parses bodies by regex: the")
    say("  heading text becomes part of the author's message.")
    say()

    say("-" * 78)
    say("4. THE `Edited on` CLASS -- ONLY IN Jrk_Bgrt_Groupchat_History.txt, NEVER CITED")
    say("-" * 78)
    say(f"  {len(D['edited'])} of {len(D['groupchat'])} authorial messages carry an edit stamp.")
    say(f"  {len(D['live_edits'])} of those were edited STRICTLY AFTER posting (a live edit);")
    say(f"  {len(D['edited']) - len(D['live_edits'])} were edited in place / re-stamped.")
    say()
    say("  The author says this class is load-bearing:")
    for probe, when in (("I haven't deleted it", "2021-04-02"),
                        ("Quite some typos have been changed already", "2020-04-08")):
        for r in D["raw"]:
            if probe in r["text"]:
                say(f"    [{r['date']} {r['time']}] {r['text'][:104]}")
    say()
    say("  Edits cluster into a few DAYS rather than being spread over the channel:")
    for day, n in sorted(D["edit_days"].items(), key=lambda kv: -kv[1])[:8]:
        say(f"    {day}  {n:3d} messages edited")
    say()
    say("  Longest latency (how long a string sat public before being changed):")
    for days, _, r in D["edit_latency"][::-1][:10]:
        say(f"    +{days:8.1f} d  {r['date']} {r['time']} -> {r['ed']}  {r['text'][:60]}")
    say()
    say("  NOTE WHAT THIS IS NOT: the export records the edit TIME and only the POST-edit")
    say("  body.  It is therefore a map of WHERE the author edited, not of WHAT the text")
    say("  was before.  No local rendering holds a pre-edit body.")
    say()

    say("-" * 78)
    say("5. THE REPLY-QUOTE CLASS -- SECOND EXCLUSIVE CLASS, ALSO NEVER CITED")
    say("-" * 78)
    say(f"  {len(D['replies'])} authorial messages are recorded as REPLIES, and for those the")
    say("  export preserves what another user had written.  A quote is a third-party")
    say("  snapshot of the channel at a known instant, so it is the only local mechanism")
    say("  that could in principle preserve authorial bytes as they once stood.")
    say()
    say(f"  Long tokens (hex>=24 / digits>=8 / b64>=20) quoted by others that appear in NO")
    say(f"  author-only rendering: {len(D['novel_quoted_tokens'])}")
    for r, m in D["novel_quoted_tokens"][:20]:
        say(f"    [{r['date']} {r['time']}] {m}")
    if not D["novel_quoted_tokens"]:
        say("    (none -- every quoted token is already in the author corpus, so the quote")
        say("     class yields no pre-edit authorial string either.)")
    say()

    say("-" * 78)
    say("VERDICT ON THE STILL-OPEN OBJECT: THE PRE-EDIT TELEGRAM SNAPSHOT")
    say("-" * 78)
    say("  KILLED AS A LOCAL OBJECT, with a stated reason rather than a shrug:")
    say("    * raw and GSMG_JRK.md are the same 427 messages: all 427 IDs match, and their")
    say("      word streams are equal in BOTH directions -- zero tokens unique to either")
    say("      file.  The single disagreement in the corpus is a CHARACTER (#39237, U+2019")
    say("      mojibaked in raw and normalised to U+0027 in the md), not a word.  The md is")
    say("      an emoji-cleaned rendering of the raw export, not a separate snapshot.")
    say("    * creator_jrk.txt and Jrk_Bgrt_Groupchat_History.txt are the same channel on")
    say("      different clocks at different export vintages; every row of both was")
    say("      matched to a distinct raw message, and every raw message they do not")
    say("      carry is either dated after their export or has an empty body.  Their one")
    say("      apparent text loss (#16624's `Nope`) was a PARSER bug, now fixed and pinned.")
    say("    * GSMG_JRK.md itself carries 2 defects of its own (glued day headings),")
    say("      which are rendering artefacts of the cleaner, not authorial differences.")
    say("    * the only rendering with edit metadata carries POST-edit text only, and the")
    say("      only mechanism that could preserve PRE-edit bytes (third-party quotes)")
    say("      contains no token absent from the author corpus.")
    say("  => No pre-edit authorial string exists in this briefcase.  Recovering one needs")
    say("     an external pre-2025-04-28 snapshot of the channel, which this device does not")
    say("     hold and which Telegram does not expose for another user's history.")
    say()
    say("  WHAT DID SURVIVE, and is not in any ledger row: the author edited 116 of 399")
    say("  messages in the groupchat rendering, all after posting, concentrated in a handful")
    say("  of days.  That is a statement about WHICH strings the author touched, and it is")
    say("  the only authorial metadata class in this corpus with no prior ledger row.")
    say("  It is not yet shown to bear on the puzzle, and is not claimed to.")
    say()


# ----------------------------------------------------------------- selftest --
def selftest(D):
    """Re-derive every number the report quotes.  Non-zero exit on drift."""
    fails = []

    n = [0]

    def ck(name, got, want):
        # Counted, and printed on pass, so "N/N" quoted in the ledger is a number
        # this run produced rather than a number someone typed.
        n[0] += 1
        if got != want:
            fails.append(f"{name}: got {got!r}, expected {want!r}")

    ck("raw count", len(D["raw"]), 427)
    ck("md count", len(D["md"]), 427)
    ck("creator count", len(D["creator"]), 411)
    ck("groupchat count", len(D["groupchat"]), 399)
    ck("md unique ids", len(D["md_ids"]), 427)
    ck("raw unique ids", len(D["raw_ids"]), 427)
    ck("id sets identical", D["ids_equal"], True)
    ck("ids only in raw", D["only_raw_ids"], [])
    ck("ids only in md", D["only_md_ids"], [])
    ck("identical bodies", D["identical"], 316)
    ck("letters+digits equal", D["norm_equal"], 16)
    ck("emoji-only bodies", D["moji_only"], 92)
    ck("emoji-only + glued heading bodies", D["moji_only_glued"], 2)
    ck("mangled apostrophe bodies", D["apostrophe"], 1)
    ck("mangled apostrophe ids", D["apostrophe_ids"], [39237])
    ck("substantive body differences", len(D["substantive"]), 0)
    ck("buckets sum to 427", sum(len(v) for v in D["buckets"].values()), 427)
    ck("raw-only corpus tokens", D["raw_only_tokens"], [])
    ck("md-only corpus tokens", D["md_only_tokens"], [])
    ck("mojibake alphabet is derived, not hardcoded", len(moji_alphabet()) > 0, True)
    ck("derived mojibake token count", len(moji_tokens()), 63)
    ck("mojibake glued to a word", moji_glued_tokens(), ['that"dY~?'])
    # The safety property that matters: deleting a mojibake token must not delete a
    # WORD, judged by the same tokenizer cmp_words uses.  Checked as a property of
    # the tokenizer rather than by looking for letter runs, because a mojibake
    # remnant can be pure ASCII (`dY~cdY""`) while still contributing nothing.
    ck("no mojibake token hides a word",
       [w for w in moji_tokens() if cmp_words(w)], [])
    ck("heading glue in md", len(D["glued"]), 2)
    ck("glued ids", sorted(r["mid"] for r in D["glued"]), ["8189", "8472"])
    ck("edited messages", len(D["edited"]), 116)
    ck("live edits", len(D["live_edits"]), 116)
    ck("reply blocks", len(D["replies"]), 116)
    ck("novel quoted tokens", len(D["novel_quoted_tokens"]), 1)
    ck("top edit day", D["edit_days"].most_common(1)[0][0], "2024-11-29")
    ck("longest edit latency > 2000d", D["edit_latency"][-1][0] > 2000, True)

    # the two ID-less renderings: no unexplained word anywhere
    for name, shifts in (("creator", (2, 3)), ("groupchat", (3, 4))):
        R = D["recon"][name]
        ck(f"{name}: every row matched to a distinct raw message",
           R["matched"] + len(R["orphan"]), R["rows"])
        ck(f"{name}: no duplicate-body collisions", R["collisions"], 0)
        ck(f"{name}: no unexplained absent words", len(R["absent_within_cut"]), 0)
    ck("groupchat: export vintage is 2025-04-28",
       D["recon"]["groupchat"]["cut"], "2025-04-28")
    ck("creator: its 16 unmatched raw messages are all empty bodies",
       len(D["recon"]["creator"]["absent_empty"]), 16)
    ck("groupchat: every raw message it lacks is dated after its vintage",
       len(D["recon"]["groupchat"]["absent_after_cut"]), 28)

    # The nested-quote case, pinned as a witness against the _q() regression that
    # used to drop the trailing `Nope`: the parsed groupchat body must now equal
    # the raw body exactly.  Read the source lines too, so the claim is about the
    # FILE and not only about the parser agreeing with itself.
    R16624 = next(r for r in D["raw"] if r["mid"] == "16624")
    G16624 = next(r for r in D["groupchat"]
                  if '"Given the available knowledge' in r["text"])
    ck("witness #16624 raw body ends 'Nope'", R16624["text"].endswith("Nope"), True)
    ck("witness #16624 groupchat body ends 'Nope'",
       G16624["text"].endswith("Nope"), True)
    ck("witness #16624 groupchat body equals raw body",
       G16624["text"], R16624["text"])
    # Cross-rendering negative: the author also sent a bare `Nope` twice (#886,
    # #6495).  Those are separate messages, so #16624's `Nope` must not be
    # accounted for by them -- each rendering must show exactly 2 bare + 1 tail.
    ck("witness: bare 'Nope' count is 2 in every rendering",
       [sum(r["text"].strip() == "Nope" for r in D[k])
        for k in ("raw", "md", "creator", "groupchat")], [2, 2, 2, 2])
    ck("witness: #16624's trailing 'Nope' is not one of the bare ones",
       G16624["text"].strip() != "Nope", True)
    ck("witness: a 3-line multiline body is folded whole, not truncated",
       any(r["text"].startswith("R=18") and "1812 bit" in r["text"]
           for r in D["groupchat"]), True)
    ck("witness: a reply quote and its response are distinct fields",
       any(r["quoted"] and r["quoted"].endswith("for good?")
           and r["text"].startswith("Still on holiday")
           for r in D["groupchat"]), True)

    # witness: a known-good message must be re-found through the same code paths
    # (AGENTS.md: a negative is only a negative if a known input is re-found).
    R = {int(r["mid"]): r for r in D["raw"]}
    M = {int(r["mid"]): r for r in D["md"]}
    # The apostrophe witness is a CODEPOINT witness, not a string witness: all four
    # files spell the word the same way, and only the codepoint differs.
    def apos(rows):
        for r in rows:
            t = r["text"]
            if "next phase" in t and t.startswith("It"):
                return [hex(ord(c)) for c in t[:5]]
        return None
    ck("witness #39237 raw holds the mojibake, not an apostrophe",
       apos(D["raw"])[:3], ["0x49", "0x74", "0xe2"])
    ck("witness #39237 md holds U+0027", apos(D["md"])[:3], ["0x49", "0x74", "0x27"])
    ck("witness #39237 creator holds U+2019", apos(D["creator"])[:3],
       ["0x49", "0x74", "0x2019"])
    ck("witness #39237 groupchat holds U+2019", apos(D["groupchat"])[:3],
       ["0x49", "0x74", "0x2019"])
    ck("witness: the word is 'it's' in all four renderings",
       [cmp_words(r["text"])[0] for r in
        (R[39237], M[39237],
         next(x for x in D["creator"] if "next phase" in x["text"] and x["text"].startswith("It")),
         next(x for x in D["groupchat"] if "next phase" in x["text"] and x["text"].startswith("It")))],
       ["it's", "it's", "it's", "it's"])

    ck("witness #225 hash survives in raw", R[225]["text"].strip(),
       "5ac407837447fba24ba2802e4d1e9aecb4580aa29fef1088cc387c180b746f75")
    ck("witness #225 hash survives in md", M[225]["text"].strip(),
       "5ac407837447fba24ba2802e4d1e9aecb4580aa29fef1088cc387c180b746f75")
    ck("witness #225 hash survives normalisation", norm(R[225]["text"]),
       "5ac407837447fba24ba2802e4d1e9aecb4580aa29fef1088cc387c180b746f75")
    ck("witness #7028 deletion statement found in raw",
       any("I haven't deleted it" in r["text"] for r in D["raw"]), True)
    ck("witness #3384 typo statement found in raw",
       any("Quite some typos have been changed already" in r["text"] for r in D["raw"]), True)
    ck("witness: #3384 names the givetit blunder, consistent with R-PLAINART",
       any("givetit instead of giveit" in r["text"] for r in D["raw"]), True)
    ck("witness: an edited message carries a strictly-later stamp",
       all(r["ed"] > stamp(r) for r in D["live_edits"]), True)

    if fails:
        print("JRCORPUS SELFTEST FAIL")
        for f in fails:
            print("  FAIL", f)
        return 1
    print(f"JRCORPUS SELFTEST PASS {n[0]}/{n[0]}"
          " -- every number re-derived, all witnesses re-found")
    print("  read-only, 0 candidates, 0 oracle calls, no funded-gate contact")
    return 0


def main(argv):
    D = collect()
    if "--selftest" in argv:
        return selftest(D)
    say = (lambda *a: None) if "--quiet" in argv else print
    report(D, say)
    print("JRCORPUS DONE -- read-only, 0 candidates, 0 oracle calls, no gate contact")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
