import itertools

core = ["matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
        "firsttint", "secondanswer"]
p7s = ["yourlastcommand", "ourfirsthintisyourlastcommand", "anstoo", "firsthint",
       "shabef", ""]

cands = set()

for p7 in p7s:
    for sep in ["", " ", "_", "-", ".", "|"]:
        seq = [t for t in core] + ([p7] if p7 else [])
        cands.add(sep.join(seq))
        cands.add(sep.join(seq).upper())
        cands.add(sep.join(seq).lower())

for ft in ["firsttint", "first_tint", "FirstTint", "firstTint"]:
    for sba in ["secondanswer", "second_answer", "SecondAnswer"]:
        core2 = ["matrixsumlist", "enter", "lastwordsbeforearchichoice",
                 "thispassword", ft, sba]
        for sep in ["", " ", "_", "-"]:
            cands.add(sep.join(core2))
            cands.add(sep.join(core2).upper())

for perm in itertools.permutations(["firsttint", "secondanswer", "yourlastcommand",
                                    "anstoo", "firsthint"]):
    core3 = ["matrixsumlist", "enter", "lastwordsbeforearchichoice",
             "thispassword"] + list(perm[:2])
    cands.add("".join(core3))
    cands.add("_".join(core3))

singles = ["firsttint", "secondanswer", "yourlastcommand",
           "ourfirsthintisyourlastcommand", "firsthintisyourlastcommand",
           "matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
           "first hint is your last command", "ans too", "second answer",
           "first tint", "firsttintsecondanswer"]
cands.update(singles)
cands.update(s.upper() for s in singles)
cands.update(s.title() for s in singles)

for c in sorted(cands):
    print(c)
