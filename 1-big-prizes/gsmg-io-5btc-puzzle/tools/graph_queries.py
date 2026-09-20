import networkx as nx
from pypher import Pypher, __
from graph_import import build_graph, DATA

G = build_graph()


def q(label):
    return [n for n, d in G.nodes(data=True) if d.get("label") == label]


def out(nid):
    return [d["rel"] for _, _, d in G.out_edges(nid, data=True)]


def dc(nid):
    return [(v, G.nodes[v]["label"], G.nodes[v].get("name")) for v in G.successors(nid)]


def report_untested_keys():
    hits = []
    for nid, d in G.nodes(data=True):
        if d.get("label") not in ("Decoded", "Name"):
            continue
        if any(succ in q("Blob") for succ in G.successors(nid)):
            continue
        if d.get("label") == "Decoded" and any(succ in q("Blob") for succ in G.successors(nid)):
            continue
        hits.append((nid, d.get("status", "")))
    return hits


def names_without_key_edge():
    return [n for n in q("Name") if not any(succ in q("Key") for succ in G.successors(n))]


def hubs(top=10):
    deg = sorted(G.nodes(data=True), key=lambda nd: G.degree(nd[0]), reverse=True)
    return [(n, d.get("label"), G.degree(n)) for n, d in deg[:top]]


def shortest_hint_to_address():
    hints = q("Hint")
    addr = set(q("Address"))
    paths = []
    for h in hints:
        for a in addr:
            try:
                p = nx.shortest_path(G, h, a)
                paths.append((len(p), h, a, p))
            except nx.NetworkXNoPath:
                pass
    paths.sort()
    return paths


def unresolved_streams():
    streams = []
    for nid in q("Stream"):
        if not list(G.successors(nid)):
            streams.append(nid)
    return streams


if __name__ == "__main__":
    print("== graph ==", len(G.nodes), "nodes /", len(G.edges), "edges")
    print("== hubs ==")
    for n, lab, d in hubs(12):
        print(f"  {d:3d}  {lab:9s} {n}")
    print("== certified strings / name-words with no OPENS-edge (never a direct standalone password) ==")
    for nid, st in report_untested_keys():
        print(f"  {nid:50s} {st}")
    nk = names_without_key_edge()
    print("== name-words never wired as a Key ==")
    print("  ", ", ".join(nk))
    print("== unresolved streams (no DECODES_TO) ==")
    for s in unresolved_streams():
        print("  ", s)
    paths = shortest_hint_to_address()
    print("== shortest hint->address paths ==")
    for ln, h, a, p in paths[:6]:
        print(f"  len{ln:2d}  {h} -> {a}")
        for n in p:
            print("       ", G.nodes[n]["label"], G.nodes[n]["name"])
            if G.nodes[n]["label"] == "Address":
                break
    edge_kinds = {}
    for _, _, d in G.edges(data=True):
        edge_kinds[d["rel"]] = edge_kinds.get(d["rel"], 0) + 1
    print("== edge types ==", dict(sorted(edge_kinds.items(), key=lambda kv: -kv[1])))


def cypher_report():
    lines = []
    lines.append("// puzzle graph analysis queries (Cypher, Neo4j-compatible)")

    p = Pypher()
    p.MATCH.node("n", labels="Decoded")
    p.query = "MATCH (n:Decoded) WHERE NOT EXISTS { (n)-[:OPENS]->(:Blob) } "
    lines.append("// untested-as-password decoded strings")
    lines.append("MATCH (n:Decoded)\nWHERE NOT (n)-[:OPENS]->(:Blob)\nRETURN n.name AS candidate, n.status "
                 "AS status ORDER BY candidate")

    lines.append("// every key currently aimed at an open gate")
    lines.append("MATCH (k:Key)-[:OPENS]->(b:Blob)-[:TARGETS]->(a:Address)\n"
                 "RETURN k.name AS key, k.form AS form, b.name AS blob, a.name AS target, a.amount_btc AS amount")

    lines.append("// hubs: most-linked entities across the puzzle graph")
    lines.append("MATCH (n)\nRETURN n.name AS entity, labels(n)[0] AS type, count(*) AS degree\n"
                 "ORDER BY degree DESC LIMIT 12")

    lines.append("// streams that still have no decoded meaning")
    lines.append("MATCH (s:Stream)\nWHERE NOT (s)-[:DECODES_TO]->()\nRETURN s.name AS stream, s.length AS len")

    lines.append("// any path from a hint down to a funded address (missing links stand out)")
    lines.append("MATCH path = shortestPath((h:Hint)-[*]-(a:Address))\n"
                 "RETURN h.name AS hint, a.name AS address, length(path) AS hops\n"
                 "ORDER BY hops LIMIT 10")

    lines.append("// name/vanity words not yet wired as key candidates")
    lines.append("MATCH (n:Name)-[:EMBEDDED_IN]->(a:Address)\n"
                 "WHERE NOT (n)-[]-(:Key)\nRETURN n.name AS word, a.name AS vanity ORDER BY n.name")

    lines.append("// tests by volume")
    lines.append("MATCH (t:Test) RETURN t.name, t.count AS N, t.gate, t.result, t.date ORDER BY t.count DESC")

    out = "\n".join(lines)
    (DATA / "puzzle_queries.cypher").write_text(out)
    print("wrote", DATA / "puzzle_queries.cypher")