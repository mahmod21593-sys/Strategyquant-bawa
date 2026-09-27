"""Rounds 13-14: append families Y, Z, CT, XR to ../strategy_library.csv (idempotent).

    python3 library_round13.py
"""
from __future__ import annotations

import csv
import json
import os

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "results")
LIB = os.path.join(HERE, "..", "strategy_library.csv")
FAMILIES = {"y": "Y FX-cross reversal", "z": "Z VIX-regime index entries", "ct": "CT COT positioning", "xr": "XR index rebound via FX and gold"}
PARAMS = {"y": ("signal", "exit", "filter"), "z": ("trigger", "exit"), "ct": ("group", "threshold", "direction", "hold"), "xr": ("signal", "exit")}


def rows():
    out = []
    for f, label in FAMILIES.items():
        res = json.load(open(os.path.join(RES, f"family_{f}.json")))
        tier = f"reject (family {res['family_verdict'].lower()})"
        for v in res["variants"]:
            inst, *parts = v["name"].split("|")
            timing = v.get("sharpe_validation_timing", v.get("sharpe_validation_verdict_basis"))
            out.append({"family": label, "strategy": v["name"], "instrument": inst, "params": "; ".join(f"{k}={p}" for k, p in zip(PARAMS[f], parts)),
                        "trades_per_year": round(v["trades_per_year"], 1) if "trades_per_year" in v else "",
                        "exposure_pct": round(v["exposure"] * 100, 1) if "exposure" in v else "",
                        "sharpe_discovery": round(v["sharpe_discovery"], 2), "sharpe_validation_raw": round(v["sharpe_validation_raw"], 2),
                        "sharpe_validation_timing": round(timing, 2), "rw_p_timing": round(v.get("rw_p_timing", v.get("rw_p_verdict_basis")), 3),
                        "sharpe_holdout_2026": "", "tier": tier})
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
