import json, time, urllib.request, urllib.parse

ADDRS = {
 "Half 1JG648":  "1JG648yaB7Wp2dpUfcZoRSD4q35oq47vCu",
 "Half 15E3pc":  "15E3pcDDXSKhvi3CLVhRTHEgd8dbVKvSZg",
 "Better 145ZQ9":"145ZQ9siLrsXBKf465wjdyQYAP5dRwhRhQ",
 "Better 1FhbJn":"1FhbJnrdq1FmeiXrpTqnpQ8jvYV7naze96",
}

def get(url, tries=8):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "curl/7.88"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(8 + 6 * i)
                continue
            if i == tries - 1:
                raise
            time.sleep(2 + 2 * i)
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2 + 2 * i)

def full_txrefs(addr):
    txrefs, before = [], None
    while True:
        p = {"limit": 50}
        if before:
            p["before"] = before
        url = "https://api.blockcypher.com/v1/btc/main/addrs/" + addr + "?" + urllib.parse.urlencode(p)
        d = get(url)
        batch = d.get("txrefs", [])
        if not batch:
            break
        txrefs.extend(batch)
        if len(batch) < 50:
            break
        before = batch[-1]["tx_hash"]
        time.sleep(2.5)
    # dedupe by tx_hash+index while preserving
    seen, uniq = set(), []
    for t in txrefs:
        k = (t["tx_hash"], t.get("tx_output_n"))
        if k not in seen:
            seen.add(k)
            uniq.append(t)
    return uniq

out = {}
for name, a in ADDRS.items():
    try:
        d0 = get("https://api.blockcypher.com/v1/btc/main/addrs/" + a)
        txrefs = full_txrefs(a)
        utxo = get("https://api.blockcypher.com/v1/btc/main/addrs/" + a + "?unspentOnly=true")
        out[name] = {
            "addr": a,
            "balance": d0.get("balance"),
            "total_received": d0.get("total_received"),
            "total_sent": d0.get("total_sent"),
            "n_tx": d0.get("n_tx"),
            "n_unspent": len(utxo.get("txrefs", [])),
            "txrefs": txrefs,
        }
        print(f"{name} {a}: summary={d0.get('balance')}/{d0.get('total_received')}/{d0.get('total_sent')} unspent={len(utxo.get('txrefs', []))} txrefs={len(txrefs)}", flush=True)
    except Exception as e:
        print(f"{name}: ERROR {e}", flush=True)
        out[name] = {"addr": a, "error": str(e)}
    time.sleep(6)

with open("/data/data/com.termux/files/usr/tmp/opencode/half_history_full.json", "w") as f:
    json.dump(out, f, indent=1)
print("saved half_history_full.json")