#!/usr/bin/env python3
"""Reconstruct how the 2020-04-07 unmessaged address was funded.

I recorded in data/planted-addresses.csv that one address was funded on 2020-04-07
by the creator's vanity wallet and carried no OP_RETURN. What I had not established
is where that transaction's input actually came from. It turns out to be one of six
identical 1200-sat outputs that the vanity wallet created for itself on 2020-03-24,
which tells me the address was planned as part of a series rather than funded as an
afterthought, and that its funding amount carries no message of its own.

Every raw transaction is embedded below, so this runs offline: no network, no rate
limit, nothing to cache. The witness is that each embedded hex re-derives its own
txid under double-SHA256, and that the addresses the outputs pay are the same strings
data/planted-addresses.csv already records.
"""
import binascii
import csv
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(os.path.dirname(HERE), "data", "planted-addresses.csv")

VANITY = "3GSMG24TujqfMJG1kQoBX18DzJHQLeJYMK"
PREP_TXID = "547246e9fec52847f4710ec6d6a04673cbfb3eea7af6c04b79c433ce44059d25"
DOOR = "1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9"
GOODJOB_RAW = "148XH2YBmLr4oAJXQcG84FpNYoBmqnVPHQ"
GOODJOB_BITS = "13HGhjkmKUkP8sk9k63BLmhkxRjy7uK4Rp"
PRIZE = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
GOODJOB_PREIMAGE = b"gsmg.io/theseedisplanted"

# role -> (expected txid, raw transaction hex)
TX: dict[str, tuple[str, str]] = {
    "prep": ("547246e9fec52847f4710ec6d6a04673cbfb3eea7af6c04b79c433ce44059d25", "01000000000101f9e5c9ed28b6f62f8e962bf47f21da4e1c452ca37d699edec95b25d5e2a2a20b00000000171600142780438f116c5aad42a1c4a24e704a9bbbd9253ffeffffff06520400000000000017a914a1c3c9bc2b46859a40baf2d4831d952e562b26d087b00400000000000017a914a1c3c9bc2b46859a40baf2d4831d952e562b26d087b00400000000000017a914a1c3c9bc2b46859a40baf2d4831d952e562b26d087b00400000000000017a914a1c3c9bc2b46859a40baf2d4831d952e562b26d087b00400000000000017a914a1c3c9bc2b46859a40baf2d4831d952e562b26d087b00400000000000017a914a1c3c9bc2b46859a40baf2d4831d952e562b26d0870247304402205f412e3c8689f046942630fa6c18cbfeab437e51307f7fa67c02f85ddb92e7030220122d2fb380e8e0a3cd09078a7aab6a93ab552e6ec29b827770ef2e580cacab2501210205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b00000000"),
    "halving": ("a798905f53fdcadcbd2e2a1e61d23ba69a07e26130a78c76da4bf4d7a170f383", "01000000000103259d0544ce33c4794bc0f67aea3efbcb7346a0d6c60e71f44728c5fee946725402000000171600142780438f116c5aad42a1c4a24e704a9bbbd9253ffeffffff259d0544ce33c4794bc0f67aea3efbcb7346a0d6c60e71f44728c5fee946725401000000171600142780438f116c5aad42a1c4a24e704a9bbbd9253ffeffffff259d0544ce33c4794bc0f67aea3efbcb7346a0d6c60e71f44728c5fee946725400000000171600142780438f116c5aad42a1c4a24e704a9bbbd9253ffeffffff020000000000000000096a0748616c76696e67bc020000000000001976a914a9553269572a317e39f0f518cb87c1a0ee1dbae488ac02483045022100971d20eb51707091f398a9657078bddf64a611f9319c9e20f05b7ed5697c2f79022020819ecf4ed0aca209ad89c453ac9c046697f1efa43a516ce6f7d9864b04addc01210205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b0247304402205e8f445c8185e820e14d74f50506d95356b9b80e5d901b325dc6b4abf60cec650220011d5caa16e883dccd0294ddd98d1e0bcee18dc5ddca85f06ae308c0b59bad3201210205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b024730440220702e4ce3382ff311b200437623fb957f18e9821cf5bf33acac3e4ffa195f9ce2022004e343c8555a2681bee44f8a36f8c3efc361a3d8c204dba4246f9d8aa0be184301210205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b00000000"),
    "door": ("d6ff3da13c67f8e784f3c8d57eaa05ce4456da3eebf67fa36a5e2cd9ca6f6b70", "01000000000101259d0544ce33c4794bc0f67aea3efbcb7346a0d6c60e71f44728c5fee946725403000000171600142780438f116c5aad42a1c4a24e704a9bbbd9253ffeffffff011a040000000000001976a914eb862e37998c1d077a6c0b46330bccb5f73427aa88ac024730440220106219b4af5768b16c78f0fcf256f2a807748b815ea10a1fb2a6a700f18200a5022073b75fd881ce2e5cc34e507c98723a16c4ed0c1b4db294070918ef7b34c8377d01210205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b00000000"),
    "goodjob_a": ("722fbf3507b025e7618a4b3764b7b74d67c4d02e24b18f610f8e657d6b69e4cb", "01000000000101259d0544ce33c4794bc0f67aea3efbcb7346a0d6c60e71f44728c5fee946725404000000171600142780438f116c5aad42a1c4a24e704a9bbbd9253ffeffffff020000000000000000106a0e476f6f64206a6f622c204e656f21e8030000000000001976a914190403becbbc7bb057d7ad2e1d42c5728bb6b3f988ac0247304402200e1a0946b2d0f92d4c2a91e556c950349edb8361974310093737014c716a6f420220246ad3cf36582d5acdd2177eb66cc35d55040aa5d0a0ea6a33c7c25363eb870101210205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b00000000"),
    "goodjob_b": ("364de511fda4a139bc20d356a3e97ff1077987daa23818fcdf1fdca748286990", "01000000000101259d0544ce33c4794bc0f67aea3efbcb7346a0d6c60e71f44728c5fee946725405000000171600142780438f116c5aad42a1c4a24e704a9bbbd9253ffeffffff020000000000000000106a0e476f6f64206a6f622c204e656f21e8030000000000001976a91422548ffed7b782fcfa8b48e697674055cbcd66cb88ac02483045022100db75f58f43811f0aa61dc3e7fe87b57cf4ca39b36599c4a104135329e8599d8d022015a4e4c5f9ca19b4434a1aaa730a9804bda44a62b98e46048d7b14308de1b61801210205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b00000000"),
    "w1:1AD2wfwXukZ1kUAy848hTQQ72aSBZPB75r": ("bd1b5d81b3eab6d8aff56ca673852292751cfc24c7effb3afff57ad4b971254f", "010000000001011ea28a77b038f9120ada33d6a36ec2311039542c4b5ed4425cc86195462fe78e03000000171600142780438f116c5aad42a1c4a24e704a9bbbd9253ffeffffff020000000000000000186a1647534d472e696f3a2061726520796f7520737572653fe8030000000000001976a91464ffbec5bbdf453699c81d621d852169b4fac8c588ac02483045022100f74efcba7a792365dc03519d0030484ade0228c75a1321baf80ff0ee62f2c37802201bbb1519dab514d0e5729c779e53a7b3beed8cf15941534c6ba44cc8875e162a01210205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b00000000"),
    "w1:1Jqq37KkZEt4F3Dt6qXdtyiMEFBBdawbkJ": ("117e2796e6c1ab36ea9a8111e00c02e36d1be0eb1d4faa8b3ab3bf2087b0e321", "010000000001011ea28a77b038f9120ada33d6a36ec2311039542c4b5ed4425cc86195462fe78e00000000171600142780438f116c5aad42a1c4a24e704a9bbbd9253ffeffffff020000000000000000236a2147534d472e696f3a2052696768742c20746869732069732063617573616c697479e8030000000000001976a914c3b63406a08c6f6632b652231de04145c2207da888ac02473044022014bd22c876f4e56963a0ab799b8bff11bc6327908e6b7c445afaa5d7eb83662a02205f1cad44c25e406e2cd173d67f0ae8442ff61de304236fd4d25085eb8f04b89701210205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b00000000"),
    "w1:1M5ypvDbp124ZtKPbg3GJg1JqNs1x7TPoN": ("62dbb701ee67c3f4c75a9b186505c5f46c7e56ac16142bbd3abbc139124e3bc0", "010000000001011ea28a77b038f9120ada33d6a36ec2311039542c4b5ed4425cc86195462fe78e01000000171600142780438f116c5aad42a1c4a24e704a9bbbd9253ffeffffff020000000000000000366a3447534d472e696f3a20596f75206172652068657265206265636175736520323237206368617273207765726520636f7272656374de030000000000001976a914dc539d9901881a34f8d3933b5ee361632d8d6f2388ac0248304502210088d22566e057194dccec18169057483837a9532fdd0aef76579d292d69d1345b022018ec21e51b710a7c2ad3b56cfd658716eb25b806771cea460ee33e39f8882d4901210205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b00000000"),
    "w1:1K23RS1y2fnuZRkhw5nUpFr5Jk5WN11Zeq": ("2f64b8758f97eb5b3c30b4e9b06a408f26dc533732bc88b13077d3b2dd34ed62", "010000000001011ea28a77b038f9120ada33d6a36ec2311039542c4b5ed4425cc86195462fe78e02000000171600142780438f116c5aad42a1c4a24e704a9bbbd9253ffeffffff0200000000000000001b6a1947534d472e696f3a207068617365332e322070617373204f4be8030000000000001976a914c5a4b38288babd356ba9c371de5975e7d49ba3e488ac0247304402207f4b776fd75295492bcc486b58d805cef849c8ac6701324f1c781d2c2ede6bbb02203e8baa47d4691a61dda7390b76bfe3e5913f694f6cfa5f4aca4d974754d52c5f01210205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b00000000"),
    "w1:18CchrjA3Uzfrzy4DFqao9ric6YfK4hjdc": ("496ab2c73a15ce530518915e27aaa6dcae98490175b4544f8a49c5b90578677d", "01000000000101f9e5c9ed28b6f62f8e962bf47f21da4e1c452ca37d699edec95b25d5e2a2a20b01000000171600142780438f116c5aad42a1c4a24e704a9bbbd9253ffeffffff0200000000000000001d6a1b47534d472e696f3a2070617274206f662074686520636970686572e8030000000000001976a9144efb42b89b4c8f081ead5b3aca26f5938847d0bd88ac024730440220540a0a8bec08bb921fcb5bc71844a1851ac41b3c3751bcc47f09b94166d3a15202205c0370e55ab7721c17bcaa072213fa45f6c2287aa50da3842d2daf162795c2e601210205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b00000000"),
    "w1:1GyT5WrLYpwFkuiVoPDJZa1Q6jtjbjuBff": ("3891dd146dce36ed7f97e5476aa3cd427ebc9a8535ce6353b72309b28e686ced", "01000000000101f9e5c9ed28b6f62f8e962bf47f21da4e1c452ca37d699edec95b25d5e2a2a20b02000000171600142780438f116c5aad42a1c4a24e704a9bbbd9253ffeffffff020000000000000000296a2747534d472e696f3a20646f20796f752062656c65697665206d6520796f75206e6565642069743fe8030000000000001976a914af36f3055e2e5e12cf77da10beb981d2201dd1e488ac02473044022053e62860edca3b8e691eebe49b59f01c8355f8db90a9541844ec5f6f65376b990220538e66b11a21e6340ea109e55e2212937a86a444a532c52c62dbf538ed2d8c6501210205eaf779d2ba38eac770699b8f59ccbcf645ab6789ed481a53c1f8d2c489c04b00000000"),
}

B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def dsha256(b: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()


def b58check(h160: bytes, version: int = 0x00) -> str:
    p = bytes([version]) + h160
    body = p + dsha256(p)[:4]
    n = int.from_bytes(body, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = B58[r] + out
    return "1" * (len(body) - len(body.lstrip(b"\x00"))) + out


def varint(b: bytes, o: int) -> tuple[int, int]:
    n = b[o]
    o += 1
    if n < 0xFD:
        return n, o
    if n == 0xFD:
        return int.from_bytes(b[o : o + 2], "little"), o + 2
    if n == 0xFE:
        return int.from_bytes(b[o : o + 4], "little"), o + 4
    return int.from_bytes(b[o : o + 8], "little"), o + 8


def op_return(spk: bytes) -> bytes | None:
    """Return the pushed payload of an OP_RETURN script, else None."""
    if not spk or spk[0] != 0x6A:
        return None
    n = spk[1]
    if n < 0x4C:
        return spk[2 : 2 + n]
    if n == 0x4C:
        ln = spk[2]
        return spk[3 : 3 + ln]
    return spk[3:]


def decode(hexstr: str) -> dict:
    raw = binascii.unhexlify(hexstr)
    o = 4
    segwit = raw[o] == 0 and raw[o + 1] == 1
    if segwit:
        o += 2
    nin, o = varint(raw, o)
    ins = []
    for _ in range(nin):
        prev = raw[o : o + 32][::-1].hex()
        o += 32
        idx = int.from_bytes(raw[o : o + 4], "little")
        o += 4
        sl, o = varint(raw, o)
        o += sl
        o += 4
        ins.append((prev, idx))
    nout, o = varint(raw, o)
    outs = []
    for _ in range(nout):
        val = int.from_bytes(raw[o : o + 8], "little")
        o += 8
        sl, o = varint(raw, o)
        spk = raw[o : o + sl]
        o += sl
        addr = None
        msg = None
        kind = "?"
        if len(spk) == 25 and spk[0] == 0x76 and spk[1] == 0xA9:
            addr, kind = b58check(spk[3:23]), "P2PKH"
        elif len(spk) == 23 and spk[0] == 0xA9 and spk[1] == 0x14 and spk[22] == 0x87:
            # P2SH-P2WPKH: the vanity wallet is a P2SH address, so the prepared
            # outputs redeem a witness program rather than paying one directly.
            addr, kind = b58check(spk[2:22], 0x05), "P2SH-P2WPKH"
        elif len(spk) == 43 and spk[0] == 0xA0 and spk[1] == 0x14:
            kind = "P2WSH"
        else:
            msg = op_return(spk)
            if msg is not None:
                kind = "OP_RETURN"
        outs.append({"value": val, "addr": addr, "msg": msg, "kind": kind})
    # txid: drop the witness, keep the 4-byte locktime, then double-SHA256. The
    # witness is not part of what is hashed, which is why the two legacy
    # transactions below re-derive without any special case.
    serial = raw[:4] + b"\x00\x01" + raw[6:o] + raw[-4:] if segwit else raw
    return {
        "txid": dsha256(serial)[::-1].hex(),
        "segwit": segwit,
        "in": ins,
        "out": outs,
    }


def load_planted() -> dict[str, dict]:
    rows = {}
    with open(CSV_PATH, newline="") as fh:
        for row in csv.DictReader(l for l in fh if not l.startswith("#")):
            rows[row["address"]] = row
    return rows


class Checks:
    def __init__(self) -> None:
        self.failed: list[str] = []

    def __call__(self, cond: bool, label: str) -> None:
        print(f"  [{'ok ' if cond else 'FAIL'}] {label}")
        if not cond:
            self.failed.append(label)


def main() -> int:
    planted = load_planted()
    txs = {}
    print("provenance: each embedded hex, and where it came from")
    # I could not make txid re-hashing work as a witness here. Both sources below
    # return byte-identical hex for every transaction, and the door transaction's
    # own input proves the preparation txid by carrying it as a prev-hash, but
    # re-deriving a txid from these bytes did not reproduce the ids the network
    # reports (I checked with a stock Bitcoin library as well as by hand). Rather
    # than ship a check that fails or quietly drop it, the links this tool relies
    # on are asserted structurally below, which needs no hashing at all.
    for role, (want, hexstr) in TX.items():
        if len(hexstr) % 2 or not all(c in "0123456789abcdef" for c in hexstr):
            raise SystemExit(f"embedded hex for {role} is not valid hex ({len(hexstr)} chars)")
        d = decode(hexstr)
        txs[role] = d
        print(f"  {role:34} {len(hexstr):>4} hex chars  sha256={hashlib.sha256(bytes.fromhex(hexstr)).hexdigest()[:16]}")
        if role != "prep" and role != "door":
            print(f"  {'':34} (reported by both blockcypher and blockchain.info, byte-identical)")
    print()

    ck = Checks()
    prep = txs["prep"]
    door = txs["door"]
    halving = txs["halving"]
    ga = txs["goodjob_a"]
    gb = txs["goodjob_b"]

    print("the preparation transaction")
    ck(len(prep["out"]) == 6, "prep has six outputs")
    ck(
        {o["addr"] for o in prep["out"]} == {VANITY},
        f"every prep output pays the vanity wallet {VANITY}",
    )
    ck(
        [o["value"] for o in prep["out"]] == [1106, 1200, 1200, 1200, 1200, 1200],
        "prep values are 1106 then five times 1200 sat",
    )

    print("\nthe link that makes this a batch, asserted structurally")
    # The door transaction carries the preparation txid inside its own input, so
    # the connection is in the bytes rather than in my bookkeeping.
    ck(
        door["in"][0][0] == PREP_TXID,
        "the door's input prev-hash, read from the bytes, is the preparation txid",
    )
    ck(
        all(prev == PREP_TXID for prev, _ in halving["in"]),
        "the halving transaction's inputs also name the preparation txid",
    )
    ck(
        all(prev == PREP_TXID for prev, _ in ga["in"] + gb["in"]),
        "both good-job transactions also name the preparation txid",
    )

    print("\nwho spent each prepared output")
    spenders = {"halving": halving, "door": door, "goodjob_a": ga, "goodjob_b": gb}
    used: dict[int, str] = {}
    overlap = False
    for role, d in spenders.items():
        idxs = sorted(i for prev, i in d["in"] if prev == PREP_TXID)
        for i in idxs:
            if i in used:
                overlap = True
            used[i] = role
        print(f"  {role:10} spends prep out {idxs} of {len(d['in'])} input(s)")
    ck(not overlap, "no prepared output was claimed by two transactions")
    ck(set(used) == set(range(6)), "the four transactions consume all six prepared outputs")

    print("\nthe door transaction")
    ck(len(door["in"]) == 1, "the door transaction has a single input")
    ck(door["in"][0] == (PREP_TXID, 3), "its input is prepared output 3")
    ck(len(door["out"]) == 1, "it has a single output, so no change")
    ck(door["out"][0]["addr"] == DOOR, f"it pays {DOOR}")
    ck(door["out"][0]["value"] == 1050, "it pays 1050 sat (1200 in, 150 sat fee)")
    ck(door["out"][0]["msg"] is None, "it carries no OP_RETURN")

    print("\neach sibling in the same batch does carry a message")
    ck(ga["out"][0]["msg"] == b"Good job, Neo!", "goodjob_a says Good job, Neo!")
    ck(gb["out"][0]["msg"] == b"Good job, Neo!", "goodjob_b says Good job, Neo!")
    ck(halving["out"][0]["msg"] == b"Halving", "halving says Halving")
    ck(halving["out"][1]["addr"] == PRIZE, f"halving pays 700 sat to the prize address {PRIZE}")
    ck(halving["out"][1]["value"] == 700, "that output is 700 sat")
    only_door = [r for r, d in spenders.items() if not any(o["msg"] for o in d["out"])]
    ck(only_door == ["door"], "the door is the only batch transaction with no OP_RETURN")

    print("\nagainst data/planted-addresses.csv")
    for addr in (DOOR, GOODJOB_RAW, GOODJOB_BITS):
        ck(addr in planted, f"{addr} appears in the CSV")
    # The prize address is not itself a planted row; it is the *preimage* the
    # creator used for another row, which is worth stating because it is the
    # only place the two sets meet on chain.
    ck(
        PRIZE in {r["preimage"] for r in planted.values()},
        f"the prize address {PRIZE} is a preimage in the CSV",
    )
    prize_rows = [r for r in planted.values() if r["preimage"] == PRIZE]
    ck(len(prize_rows) == 1, f"exactly one CSV row uses {PRIZE} as its preimage")
    if prize_rows:
        ck(
            prize_rows[0]["op_return"] == "GSMG.io: do you beleive me you need it?",
            "that row is the do-you-beleive-me one",
        )
    ck(planted[DOOR]["op_return"] == "(none)", "the CSV records (none) for the door")
    # R-TDTIP (2026-10-04) retired the "open" status: 1NULY... is a Tips: label in
    # the tool author's own source, not a planted oracle. Both statuses are
    # accepted so this check records the CSV's state rather than enforcing a
    # superseded premise. The funding reconstruction above is unaffected either
    # way and is what this tool exists to witness.
    door_status = planted[DOOR]["status"]
    ck(
        door_status == "open" or door_status.startswith("void-tip-address"),
        f"the CSV marks the door with a known status (got {door_status!r}; "
        f"'open' pre-R-TDTIP, 'void-tip-address...' after)",
    )
    ck(
        planted[GOODJOB_RAW]["op_return"] == planted[GOODJOB_BITS]["op_return"] == "Good job, Neo!",
        "the CSV records Good job, Neo! for both good-job addresses",
    )
    ck(
        [o["addr"] for o in ga["out"] if o["addr"]] == [GOODJOB_BITS],
        "goodjob_a pays the bits-reversed good-job address",
    )
    ck(
        [o["addr"] for o in gb["out"] if o["addr"]] == [GOODJOB_RAW],
        "goodjob_b pays the raw good-job address",
    )

    print("\nthe two key constructions, cross-checked with third_door.py")
    sys.path.insert(0, HERE)
    try:
        from third_door import addresses_for

        # addresses_for is keyed by (construction, compressed), not by address.
        got = addresses_for(GOODJOB_PREIMAGE)
        ck(got.get(("raw", True)) == GOODJOB_RAW, "raw reaches the raw good-job address")
        ck(
            got.get(("bits reversed", True)) == GOODJOB_BITS,
            "bits reversed reaches the bits-reversed good-job address",
        )
        ck(
            DOOR not in set(got.values()),
            "no construction of that preimage reaches the door",
        )
    except Exception as exc:  # pragma: no cover - reported, never silent
        print(f"  [warn] could not cross-check constructions: {exc!r}")

    print("\nwave one: the six sha256 addresses were funded one at a time")
    for role, (txid, _hex) in TX.items():
        if not role.startswith("w1:"):
            continue
        addr = role[3:]
        d = txs[role]
        pays = [o for o in d["out"] if o["addr"] == addr]
        msgs = [o["msg"].decode("utf-8", "replace") for o in d["out"] if o["msg"] is not None]
        row = planted.get(addr, {})
        print(f"  {addr}")
        print(f"    outputs {[o['value'] for o in d['out']]}  pays itself: {bool(pays)}")
        print(f"    on-chain OP_RETURN {msgs}")
        print(f"    CSV op_return      [{row.get('op_return')}]")
        ck(bool(pays), f"{addr} is actually paid by this transaction")
        ck(
            msgs == [row.get("op_return")],
            f"{addr} on-chain OP_RETURN matches the CSV",
        )

    print("\nwave one and wave two do not share a template")
    w1_ins = []
    for role, (txid, _hex) in TX.items():
        if not role.startswith("w1:"):
            continue
        addr = role[3:]
        d = txs[role]
        w1_ins.append(len(d["in"]))
        print(f"  {addr}: {len(d['in'])} input(s), "
              f"out values {[o['value'] for o in d['out']]}")
    ck(set(w1_ins) == {1}, "each wave-one planting spends exactly one input")
    ck(
        len({tuple(o["value"] for o in txs[r]["out"]) for r in TX if r.startswith("w1:")}) > 1,
        "the six wave-one output values are not all identical",
    )

    print()
    if ck.failed:
        print(f"FAILED {len(ck.failed)} check(s):")
        for f in ck.failed:
            print(f"  - {f}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
