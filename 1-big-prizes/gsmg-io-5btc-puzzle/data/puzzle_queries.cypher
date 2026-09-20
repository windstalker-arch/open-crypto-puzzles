// puzzle graph analysis queries (Cypher, Neo4j-compatible)
// untested-as-password decoded strings
MATCH (n:Decoded)
WHERE NOT (n)-[:OPENS]->(:Blob)
RETURN n.name AS candidate, n.status AS status ORDER BY candidate
// every key currently aimed at an open gate
MATCH (k:Key)-[:OPENS]->(b:Blob)-[:TARGETS]->(a:Address)
RETURN k.name AS key, k.form AS form, b.name AS blob, a.name AS target, a.amount_btc AS amount
// hubs: most-linked entities across the puzzle graph
MATCH (n)
RETURN n.name AS entity, labels(n)[0] AS type, count(*) AS degree
ORDER BY degree DESC LIMIT 12
// streams that still have no decoded meaning
MATCH (s:Stream)
WHERE NOT (s)-[:DECODES_TO]->()
RETURN s.name AS stream, s.length AS len
// any path from a hint down to a funded address (missing links stand out)
MATCH path = shortestPath((h:Hint)-[*]-(a:Address))
RETURN h.name AS hint, a.name AS address, length(path) AS hops
ORDER BY hops LIMIT 10
// name/vanity words not yet wired as key candidates
MATCH (n:Name)-[:EMBEDDED_IN]->(a:Address)
WHERE NOT (n)-[]-(:Key)
RETURN n.name AS word, a.name AS vanity ORDER BY n.name
// tests by volume
MATCH (t:Test) RETURN t.name, t.count AS N, t.gate, t.result, t.date ORDER BY t.count DESC