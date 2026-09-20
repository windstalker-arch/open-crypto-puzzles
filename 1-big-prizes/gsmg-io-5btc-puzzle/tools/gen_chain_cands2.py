
# instruction words p1..p4 (verified page tokens)
p1 = "matrixsumlist"
p2 = "enter"
p3 = "lastwordsbeforearchichoice"
p4 = "thispassword"

# first hint value candidates (text on first puzzle piece / its hash / variants)
firsthint = [
    "GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "gsmgio5btcpuzzlechallenge1gsmg1jc9wtdswfwapgj2xcmjpawx7prbe",
    "GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9",
    "gsmgio5btcpuzzlechallenge1gsmg1jc9",
    "89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32",
    "theflowerblossomsthroughwhatseemstobeaconcretesurface",
    "causality",
    "hop" ,
    "hop",
]

# second answer value candidates (ans too)
secondanswer = [
    "causality",
    "theflowerblossomsthroughwhatseemstobeaconcretesurface",
    "yourlastcommand",
    "secondanswer",
    "anstoo",
    "theanswer",
    "hopeisthequintessentialhumandelusion",
]

p7s = ["", "yourlastcommand", "anstoo", "firsthint"]
seps = ["", "_", "-", ""]

cands = set()
for fh in firsthint:
    for sa in secondanswer:
        # structural: p1-p4 + fh + sa + p7
        for p7 in p7s:
            for sep in ["", "_", "-", " "]:
                seq = [p1, p2, p3, p4, fh, sa] + ([p7] if p7 else [])
                cands.add(sep.join(seq))
        # alternate: fh + sa alone (the two hinted values)
        for sep in ["", "_", "-", " "]:
            cands.add(sep.join([fh, sa]))
        # fh + sa + the command
        cands.add(f"{fh}{sa}yourlastcommand")
        # instruction words + fh
        cands.add(f"{p1}{p2}{p3}{p4}{fh}")
        cands.add(f"{fh}{sa}")

# also: the two hint values by themselves and with case
for sep in ["", "_", "-", " "]:
    cands.add(sep.join(["GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
                        "theflowerblossomsthroughwhatseemstobeaconcretesurface"]))

for c in sorted(cands):
    print(c)
