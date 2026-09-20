import json
import networkx as nx
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

BLANK = ("\x00", "")


def _clean(v):
    if v is None:
        return ""
    if isinstance(v, bytes):
        return v.hex()
    s = str(v)
    if len(s) > 240:
        return s[:237] + "..."
    return s


def build_graph():
    G = nx.DiGraph()

    def node(label, name, **props):
        nid = f"{label}:{name}"
        props = {k: _clean(v) for k, v in props.items() if v not in BLANK}
        props["label"] = label
        G.add_node(nid, name=name, **props)
        return nid

    def edge(src, dst, rel, **props):
        props = {k: _clean(v) for k, v in props.items() if v not in BLANK}
        G.add_edge(src, dst, rel=rel, **props)

    streams = json.loads((DATA / "finalpage-digit-streams.json").read_text())
    sal = json.loads((DATA / "salphaseion-streams.json").read_text())

    dbbib = node("Stream", "dbbib_91", alphabet="a..i", length=streams["dbbib_91_len"],
                 text=streams["dbbib_91"], status="authoritative", src=streams["_provenance"].get("status", ""))
    faed = node("Stream", "faed_570", alphabet="a..i", length=streams["faed_570_len"],
                text=streams["faed_570"], trailing_z=streams["faed_trailing_z"], status="authoritative")
    z1 = node("Stream", "z_segment_1", alphabet="a..i", length=streams["z_segment_1_len"],
              text=streams["z_segment_1"])
    z2 = node("Stream", "z_segment_2", alphabet="a..i", length=streams["z_segment_2_len"],
              text=streams["z_segment_2"])
    bin1 = node("Stream", "binary_run_1", alphabet="{a,b}", length=104, decoder="8 bits/byte a=0 b=1",
                status="certified")
    bin2 = node("Stream", "binary_run_2", alphabet="{a,b}", length=40, decoder="8 bits/byte a=0 b=1",
                status="certified")
    ob = node("Stream", "object_256", length=sal["object_256_len"], alphabet_size=sal["object_256_alphabet_size"],
              text=sal["object_256"], sha256=sal["sha256"].get("object_256", ""))
    odd = node("Stream", "odd_pre_reduction", text=sal["odd_pre_reduction"],
               sha256=sal["sha256"].get("odd_pre_reduction", ""))
    even = node("Stream", "even_stream", alphabet="BCDE", text=sal["even_stream"],
                counts=sal["even_alphabet_counts"], sha256=sal["sha256"].get("even_stream", ""))
    drop = node("Stream", "dropped_29", text=sal["dropped_29"], sha256=sal["sha256"].get("dropped_29", ""))
    ph = node("Stream", "plaintext_head", text=sal["plaintext_head"], src=sal["_provenance"].get("decoding", ""))

    decoded = {}
    decode_tbl = [
        ("matrixsumlist", dec := node("Decoded", "matrixsumlist", text="matrixsumlist", status="certified",
                                      decoder="binary ab-run (8 bits/byte)", src="page run_1"), bin1),
        ("enter", e2 := node("Decoded", "enter", text="enter", status="certified",
                             decoder="binary ab-run (8 bits/byte)", src="page run_2"), bin2),
        ("lastwordsbeforearchichoice", lw := node("Decoded", "lastwordsbeforearchichoice", status="certified",
                                                  decoder="z_segment_1 base-10 (a=1..i=9, o=0)"), z1),
        ("thispassword", tp := node("Decoded", "thispassword", status="certified",
                                    decoder="z_segment_2 base-10 (a=1..i=9, o=0)"), z2),
        ("ourfirsthintisyourlastcommand", of := node("Decoded", "ourfirsthintisyourlastcommand", status="certified",
                                                     decoder="sha256 preimage of page slug", src="shabef line"), faed),
        ("hopeisthequintessentialhumandelusion", hp := node("Decoded", "hopeisthequintessentialhumandelusion",
                                                            status="certified", decoder="sha256 preimage"), faed),
        ("anstoo", at := node("Decoded", "anstoo", status="certified", decoder="sha256 preimage of page slug",
                              src="shabef ans too"), faed),
        ("INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSO"
         "NEEDFUNDSTOLIVE", ic := node("Decoded", "phase3.2.2_plaintext", status="certified",
                                       text="IN CASE YOU MANAGE TO CRACK THIS THE PRIVATE KEYS BELONG TO HALF "
                                            "AND BETTER HALF AND THEY ALSO NEED FUNDS TO LIVE",
                                       decoder="VIC straddling checkerboard", src="tested.md sec 12"), None),
        ("theflowerblossomsthroughwhatseemstobeaconcretesurface",
         fb := node("Decoded", "phase2_password_lyric", status="certified", decoder="community walkthrough"), None),
        ("causality", ca2 := node("Decoded", "causality", status="certified", src="phase-2 early"), None),
        ("matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist",
         mxc := node("Decoded", "small_blob_raw_password_string", status="certified",
                     text="matrixsumlist enter lastwordsbeforearchichoice thispassword matrixsumlist",
                     decoder="concatenated page instruction tokens"), None),
    ]
    for name, node_id, src_stream in decode_tbl:
        decoded[name] = node_id
        if src_stream is not None:
            edge(src_stream, node_id, "DECODES_TO")

    chain_7 = [
        ("matrixsumlist", decoded["matrixsumlist"]),
        ("enter", decoded["enter"]),
        ("lastwordsbeforearchichoice", decoded["lastwordsbeforearchichoice"]),
        ("thispassword", decoded["thispassword"]),
        ("firsttint", node("Decoded", "firsttint", status="hypothesis", text="first hint value", src="sec 58 note")),
        ("secondanswer", node("Decoded", "secondanswer", status="on-chain-passphrase", src="burn OP_RETURN")),
        ("yourlastcommand", node("Decoded", "yourlastcommand", status="on-chain-passphrase", src="burn OP_RETURN")),
    ]
    for i, (token, node_id) in enumerate(chain_7):
        if i:
            edge(chain_7[i - 1][1], node_id, "NEXT_IN_CHAIN")

    jk = node("Decoded", "p3.2_keys", text="Half=0423d911...cc35 Better=48cc46e6...3971",
              status="certified", src="tested.md sec 40")

    blobs = {}
    small = node("Blob", "small_blob", salt="3ab585348552415d", ct_len=96, plaintext_len=79,
                 plaintext_head="9fa9db91a9...", cipher="AES-256-CBC", kdf="EVP_BytesToKey MD5",
                 status="chain-1 solved / final gate OPEN", src="tested.md late-29")
    dualite = node("Blob", "dualite_blob", salt="2d3f6fe06dc950e6", ct_len=1344, plaintext_len=1327,
                   plaintext_sha256="4f7a1e4e...", cipher="AES-256-CBC", kdf="EVP + 32B XOR",
                   status="plaintext recovered / final gate OPEN", src="tested.md late-29")
    phase2 = node("Blob", "phase2_blob", cipher="AES-256-CBC", status="navigation stage (solved)")
    p32 = node("Blob", "p32_inner_aes", status="RETRACTED", src="issue #111 / author retraction")

    keys = {}
    kr = node("Key", "raw_password_small_blob", form="raw text", text="matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist",
              status="certified", src="tested.md late-29")
    cau = node("Key", "sha256_causality_hex", form="sha256 hex", opens="phase2_blob")
    xor = node("Key", "dualite_xor_key_32B", form="raw 32B XOR", value="a795de11...0735", src="tested.md late-29")
    hk = node("Key", "half_key_32B", form="hex", value="0423d911...cc35")
    bk = node("Key", "better_half_key_32B", form="hex", value="48cc46e6...3971")

    edge(kr, small, "OPENS", note="decrypts small blob to 79B chain-1 (K_C1||K_C2||E_C)")
    edge(cau, phase2, "OPENS", note="sha256('causality').hexdigest()")
    edge(xor, dualite, "OPENS", note="32B XOR key, EVP-MD5 wrapper")
    edge(hk, jk, "DERIVES", note="half matrixsumlist key")
    edge(bk, jk, "DERIVES", note="better half matrixsumlist key")

    addresses = {}
    g1 = node("Address", "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe", amount_btc="1.2563451", h160="a9553269...",
              role="gate small", status="funded unspent")
    g2 = node("Address", "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa", amount_btc="3.7505531", h160="4bc46844...",
              role="gate dualite", status="funded unspent")
    esc = node("Address", "escrow_tx_73e48ff5", txid="73e48ff571a7e9a4387574a50cf2fcb7b21b6ea5702c777a035664df57cbce02",
               funded="2019-04-13")
    sibling = node("Address", "1GSMG1CLxGXuFtnKbwh1QWfp4xA6reAet3", role="sibling vanity")
    author_w = node("Address", "1GSMG9VDLTU6jyuG7bkNMdmnHBLtbbM51M", role="author wallet (OP_RETURN spender)")
    burn = node("Address", "11111119536NnU2vPAvoQhvkheQ8ejYJ", role="burn address (third-party passphrases)")
    for name, addr in [("1BEN1x8p", "1BEN1x8p"), ("1BEN1Kdr", "1BEN1Kdr"), ("1HansB1D2", "1HansB1D2"),
                       ("1Jorik1e", "1Jorik1e"), ("1GSMG9VD", "1GSMG9VD"), ("1GKJzHQ", "1GKJzHQ"),
                       ("135Cf6AS", "135Cf6AS"), ("12ZdDsYJ", "12ZdDsYJ"), ("14zJ3RHP", "14zJ3RHP"),
                       ("JEDYY", "JEDYY")]:
        addresses[name] = node("Address", name, address=addr, role="name/vanity family")

    edge(small, g1, "TARGETS", amount="1.2563451 BTC")
    edge(dualite, g2, "TARGETS", amount="3.7505531 BTC")
    edge(esc, g1, "FUNDS")
    edge(esc, g2, "FUNDS")

    names = {}
    for word, addr in [("BEN", "1BEN1x8p"), ("BEN", "1BEN1Kdr"), ("HANS", "1HansB1D2"), ("JORIK", "1Jorik1e")]:
        nm = node("Name", word, word=word)
        edge(nm, addresses.get(addr, addresses["1BEN1x8p"]), "EMBEDDED_IN")
    node("Name", "SoWut", role="author Telegram handle")
    node("Name", "Jrk Bgrt", role="author platform handle", disputed="legally contested")
    node("Name", "Naddiseo", role="community maintainer (insider-aligned)")

    payloads = {}
    jh = node("Payload", "GSMGJH_opreturn", tag="GSMGJH ", body_len=64,
              body_head="0495c689eb5aef53f7fa1ef650c56eac", txid="808f812f13a3137e...")
    bh = node("Payload", "GSMGBH_opreturn", tag="GSMGBH", body_len=65, body_head="1f3afc610c1befe34300a07ec01e74c6b7f1e870dd3ff7e46e726363d0c9f1845165 || 0af99010f0495f43...",
              body_tail="0af99010f0495f43c1a332d45190631275191e429aa2dc1aae3b25ec79b35f",
              txid="22381b6013973fed...")
    edge(author_w, jh, "SENT", tx="808f812f13a3137e48a0c95a818ae661a80fafaf409237efbb4b62b8198a4c13")
    edge(author_w, bh, "SENT", tx="22381b6013973fedbe7821eb82e60d50ef61ee6e430896bd47f209b12157614b")

    for pw in ["secondanswer", "yourlastcommand", "isolveditwithanabacus", "leavethematrix", "hereismysecret"]:
        pd = node("Decoded", "burn_passphrase_" + pw, text=pw, status="third-party OP_RETURN passphrase")
        edge(burn, pd, "CARRIES")

    hints = {}
    hint_rows = [
        ("hint_esrever", "2023-06-01", "esrever", "earliest published hint (reverse)"),
        ("hint_primes", "2023-01-09", "primes important", ""),
        ("hint_toe", "2023-01-12", "theory of everything", ""),
        ("hint_2023_02_23", "2023-02-23",
         "yellow blue primes matrix sumlist last words before archichoice yinyang we wont give away thepassword "
         "its in front of your eyes but youre not seeing it very last step is a true give away promised",
         "decoded hidden binary message"),
        ("hint_2023_08_03", "2023-08-03", "are you really looking for just the btc... (...=key)", ""),
        ("hint_yinyang", "2023-08-06", "once you hit a yinyang you'll solve it the same day", ""),
        ("hint_opposites", "", "the seed is planted when opposites attract", ""),
        ("hint_roses", "", "Roses are White but often Red", ""),
        ("hint_yellow_blue", "", "Yellow has a number and so does Blue. Go back to the first puzzle piece", ""),
        ("hint_zeroed", "", "some characters need to be zeroed out", ""),
        ("hint_rabbit", "", "follow the white rabbit", ""),
        ("hint_small_rabbit", "", "use the small white rabbit only", ""),
        ("hint_2026_01_01", "2026-01-01",
         "Happy new year! Make the best of everything. Oh, and here's a 'tiny hint' <3.", "binary text decode"),
        ("hint_2026_07_12", "2026-07-12",
         "My close friends have the best chance of solving it (a few tried). But they don't have the skills some "
         "of you do. NOTE: that is a hint.", "official"),
        ("hint_2026_07_12_other", "2026-07-12",
         "The '5' btc was never the actual prize. That was only a tiny fraction.", "other message"),
        ("hint_last_command", "", "shabef our first hint is your last command", "on-page; shabef=sha256 a1z26"),
        ("hint_ans_too", "", "shabef ans too", "on-page"),
    ]
    for slug, date, text, note in hint_rows:
        hints[slug] = node("Hint", slug, date=date or "", text=text, note=note, src="README/tested.md")

    edge(hints["hint_2026_01_01"], small, "POINTS_TO", note="tiny/fraction meta-hint")
    edge(hints["hint_2026_07_12_other"], small, "POINTS_TO", note="5btc never the prize; tiny fraction")
    edge(hints["hint_esrever"], faed, "POINTS_TO")
    edge(hints["hint_last_command"], decoded["ourfirsthintisyourlastcommand"], "DECODES_TO")
    edge(hints["hint_last_command"], decoded["anstoo"], "DECODES_TO")
    edge(hints["hint_yinyang"], bin1, "POINTS_TO", note="black/white runs")
    edge(hints["hint_yinyang"], bin2, "POINTS_TO")
    edge(hints["hint_zeroed"], drop, "POINTS_TO", note="dropped 29 = zeroed chars")
    edge(hints["hint_rabbit"], odd, "POINTS_TO")
    edge(hints["hint_2023_02_23"], decoded["matrixsumlist"], "MENTIONS")
    edge(hints["hint_2023_02_23"], decoded["lastwordsbeforearchichoice"], "MENTIONS")

    tools = {}
    tool_rows = [
        ("oracle.py", "small gate checker (sha256(X).hex -> EVP AES)", "certified"),
        ("oracle_dualite.py", "dualite gate checker (XOR/EVP)", "certified"),
        ("certified_vic.py", "VIC straddling checkerboard decoder", "certified"),
        ("bifid_repro.py", "Bifid reproduction (DBIFHCEG convention)", "uncertified convention"),
        ("bifid_perm_sweep.py", "Bifid keyed-square permutation sweep", "certified sweep"),
        ("base58_vic_sweep.py", "base58->VIC keyed alphabets", "certified sweep"),
        ("lead0_vicgap.py", "lead-0 gap VIC forms", "certified sweep"),
        ("lt3_bitmask_sweep.py", "'<3' positional bitmask family", "swamped"),
        ("chain_build.py", "7-token XOR/intertwined chain reconstruction", "chapter-2"),
        ("graph_import.py", "graph model builder (this file)", "new"),
        ("graph_queries.py", "graph analysis + Cypher emission", "new"),
    ]
    for name, fn, status in tool_rows:
        tools[name] = node("Tool", name, function=fn, status=status)
    edge(tools["oracle.py"], small, "CHECKS")
    edge(tools["oracle_dualite.py"], dualite, "CHECKS")
    edge(tools["certified_vic.py"], ic, "DECODES", decoder="FUBCDORA.LETHINGKYMVPS.JQZXW")

    tests = {}
    test_rows = [
        ("sec19_esrever", 116, "2 gates", "0 match", "2026-08-27", "reversal of final-gate objects"),
        ("sec41_joint_vic", 75000, "2 gates", "0 match", "2026-08-27", "joint VIC forms"),
        ("sec58_7token", 208, "small gate", "0 match", "2026-08-31", "7-token concatenated chain"),
        ("sec58_first_second", 1668, "small gate", "0 match", "2026-08-31", "[first tint][second answer] family"),
        ("sec77_firsthint_key", 848, "2 gates", "0 hits", "2026-09-01", "sha256(first-hint) as dbbib/faed decode key"),
        ("sec_shabef_befour", 14, "2 gates", "NO MATCH", "2026-09-09", "befour/our first hint is your last command"),
        ("sec109_identity", 2562, "2 gates", "0 match", "2026-09-06", "author identity keyword family"),
        ("late29_falsification", 2649762, "2 gates", "0 MATCH / premise falsified", "2026-09-11",
         "oracle cumulative; RAW-password, not sha256(X)"),
        ("late39_opreturn_battery", 335, "2 gates", "ALL NO MATCH", "2026-09-12",
         "GSMGJH/GSMGBH split semantics GF(2^8)/XOR"),
        ("late68_even_object_grid", 0, "2 gates", "negative", "2026-09-14", "even/object grid"),
        ("late69_p9_p5b", 0, "2 gates", "negative", "2026-09-14", "P-9/P-5b"),
        ("late70_lt3_bitmask", 0, "2 gates", "swamped", "2026-09-14", "'<3' positional bitmask family"),
    ]
    for name, count, gate, result, date, family in test_rows:
        tests[name] = node("Test", name, count=count, gate=gate, result=result, date=date, family=family)
    edge(tests["sec19_esrever"], faed, "COVERS")
    edge(tests["sec58_7token"], kr, "COVERS")
    edge(tests["late29_falsification"], small, "COVERS")
    edge(tests["late29_falsification"], dualite, "COVERS")
    edge(tests["late39_opreturn_battery"], jh, "COVERS")
    edge(tests["late39_opreturn_battery"], bh, "COVERS")

    return G


def to_cypher(G):
    lines = []
    for nid, d in G.nodes(data=True):
        label = d.get("label", "Node")
        props = {k: v for k, v in d.items() if k not in ("label",)}
        esc = {k: f"'{str(v).replace(chr(92), chr(92)*2).replace(chr(39), chr(92)+chr(39))}'" for k, v in props.items()}
        attrs = ", ".join(f"{k}: {v}" for k, v in esc.items())
        lines.append(f"CREATE (n:{label} {{ {attrs} }})")
    rel = {}
    for u, v, d in G.edges(data=True):
        rel.setdefault(u, []).append((v, d))
    for u, targets in rel.items():
        ul = G.nodes[u].get("label", "Node")
        for v, d in targets:
            vl = G.nodes[v].get("label", "Node")
            lines.append(f"MATCH (a:{ul}) MERGE (b:{vl}) "
                         f"WITH a, b WHERE a.name = '{G.nodes[u]['name']}' AND b.name = '{G.nodes[v]['name']}' "
                         f"CREATE (a)-[:{d['rel']}]->(b)")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    G = build_graph()
    counts = {}
    for _, d in G.nodes(data=True):
        counts[d["label"]] = counts.get(d["label"], 0) + 1
    print("nodes:", len(G.nodes), "edges:", len(G.edges))
    print(dict(sorted(counts.items(), key=lambda kv: -kv[1])))
    if "--cypher" in sys.argv:
        (DATA / "puzzle.cypher").write_text(to_cypher(G))
        print("wrote", DATA / "puzzle.cypher")
    if "--graphml" in sys.argv:
        nx.write_graphml(G, ROOT / "analysis" / "puzzle_graph.graphml")
        print("wrote", ROOT / "analysis" / "puzzle_graph.graphml")