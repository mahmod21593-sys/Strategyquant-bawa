"""Round 12: append families S, U, V, W to ../strategy_library.csv (idempotent). Family T is an exit-timing study of
family A's signals (REPORT §22), not a new strategy set, so it has no library rows.

    python3 library_round12.py
"""
from __future__ import annotations

import csv
import json
import os

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "results")
LIB = os.path.join(HERE, "..", "strategy_library.csv")
FAMILIES = {"s": "S short-side index reversal", "u": "U macro-release shocks", "v": "V metals auction windows", "w": "W FX weekend-gap reversal"}
PARAMS = {"s": ("signal", "exit", "filter"), "u": ("event", "k", "direction", "exit"), "v": ("event", "window", "side"), "w": ("gap_tail", "direction", "exit")}


def rows():
    out = []
    for f, label in FAMILIES.items():
        res = json.load(open(os.path.join(RES, f"family_{f}.json")))
        verdict = res["family_verdict"]
        if f == "s":
            for v in res["variants"]:
                inst, *parts = v["name"].split("|")
                out.append({"family": label, "strategy": v["name"], "instrument": inst, "params": "; ".join(f"{k}={p}" for k, p in zip(PARAMS[f], parts)),
                            "trades_per_year": round(v["trades_per_year"], 1), "exposure_pct": round(v["exposure"] * 100, 1),
                            "sharpe_discovery": round(v["sharpe_discovery"], 2), "sharpe_validation_raw": round(v["sharpe_validation_raw"], 2),
                            "sharpe_validation_timing": round(v["sharpe_validation_timing"], 2), "rw_p_timing": round(v["rw_p_timing"], 3),
                            "sharpe_holdout_2026": "", "tier": f"reject (family {verdict.lower()})"})
            continue
        trades = json.load(open(os.path.join(RES, f"family_{f}_trades.json")))["trade_stats"]
        for v in res["variants"]:
            inst, *parts = v["name"].split("|")
            out.append({"family": label, "strategy": v["name"], "instrument": inst, "params": "; ".join(f"{k}={p}" for k, p in zip(PARAMS[f], parts)),
                        "trades_per_year": round(trades[v["name"]]["trades_per_year_val"], 1), "exposure_pct": "",
                        "sharpe_discovery": round(v["sharpe_discovery"], 2), "sharpe_validation_raw": round(v["sharpe_validation_raw"], 2),
                        "sharpe_validation_timing": "", "rw_p_timing": round(v["rw_p_verdict_basis"], 3), "sharpe_holdout_2026": "",
                        "tier": f"reject (family {verdict.lower()})"})
    return out


if __name__ == "__main__":
    with open(LIB, newline="") as fh:
        r = csv.DictReader(fh)
        fields = r.fieldnames
        old = [x for x in r if x["family"] not in FAMILIES.values()]
    new = rows()
    with open(LIB, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(old + new)
    print("kept", len(old), "added", len(new))
