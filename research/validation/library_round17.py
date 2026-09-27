"""Round 17: append families RB (with robustness tiers), FM and IM2 to ../strategy_library.csv (idempotent).

    python3 library_round17.py
"""
from __future__ import annotations

import csv
import json
import os

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "results")
LIB = os.path.join(HERE, "..", "strategy_library.csv")
LABELS = {"rb": "RB reversal breadth (SQX-native signals)", "fm": "FM FX/gold intraday momentum", "im2": "IM2 late-day index momentum"}


def rb_rows():
    res = json.load(open(os.path.join(RES, "family_rb.json")))
    rw = set(res["timing"]["romano_wolf_significant_5pct"])
    sv = {v["name"]: v["sharpe_validation_timing"] for v in res["variants"]}
    out = []
    for v in res["variants"]:
        m, sig, ex, fl = v["name"].split("|")
        nb = [n for n in sv if n != v["name"] and n.startswith(f"{m}|{sig}|") and ((n.split("|")[2] != ex) ^ (n.split("|")[3] != fl))]
        t = v["sharpe_validation_timing"]
        tier = "1 (Romano-Wolf significant)" if v["name"] in rw else "2 (robust)" if t >= 0.3 and all(sv[n] > 0 for n in nb) else "3 (positive)" if t > 0 else "reject"
        out.append({"family": LABELS["rb"], "strategy": v["name"], "instrument": m, "params": f"signal={sig}; exit={ex}; filter={fl}",
                    "trades_per_year": round(v["trades_per_year"], 1), "exposure_pct": round(v["exposure"] * 100, 1),
                    "sharpe_discovery": round(v["sharpe_discovery"], 2), "sharpe_validation_raw": round(v["sharpe_validation_raw"], 2),
                    "sharpe_validation_timing": round(t, 2), "rw_p_timing": round(v["rw_p_timing"], 3), "sharpe_holdout_2026": "", "tier": tier})
    return out


def other_rows(f):
    res = json.load(open(os.path.join(RES, f"family_{f}.json")))
    trades = json.load(open(os.path.join(RES, f"family_{f}_trades.json")))["trade_stats"]
    out = []
    for v in res["variants"]:
        inst, *parts = v["name"].split("|")
        tier = f"reject (family {res['family_verdict'].lower()})"
        if f == "fm" and inst == "USDJPY" and "NOISE" in v["name"] and v["sharpe_validation_raw"] > 0 and v["sharpe_discovery"] > 0:
            tier = "lead (USDJPY intraday momentum; family weak)"
        out.append({"family": LABELS[f], "strategy": v["name"], "instrument": inst, "params": "; ".join(parts),
                    "trades_per_year": round(trades[v["name"]]["trades_per_year_val"], 1), "exposure_pct": "",
                    "sharpe_discovery": round(v["sharpe_discovery"], 2), "sharpe_validation_raw": round(v["sharpe_validation_raw"], 2),
                    "sharpe_validation_timing": "", "rw_p_timing": round(v["rw_p_verdict_basis"], 3), "sharpe_holdout_2026": "", "tier": tier})
    return out


if __name__ == "__main__":
    with open(LIB, newline="") as fh:
        r = csv.DictReader(fh)
        fields = r.fieldnames
        old = [x for x in r if x["family"] not in LABELS.values()]
    new = rb_rows() + other_rows("fm") + other_rows("im2")
    with open(LIB, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(old + new)
    from collections import Counter
    print("kept", len(old), "added", len(new), Counter(x["tier"] for x in new if x["family"] == LABELS["rb"]))
