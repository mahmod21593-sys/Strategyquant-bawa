"""Round 19: append families GT (Tokyo fix on Gotobi days, with tiers) and FD (central-bank-day FX) to
../strategy_library.csv (idempotent).

    python3 library_round19.py
"""
from __future__ import annotations

import csv
import json
import os
from datetime import date

import numpy as np

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
LIB = os.path.join(HERE, "..", "strategy_library.csv")
LABELS = {"gt": "GT Tokyo fix on Gotobi days", "fd": "FD central-bank-day FX"}


def rows(f):
    res = json.load(open(os.path.join(RES, f"family_{f}.json")))
    rw = set(res["raw"]["romano_wolf_significant_5pct"])
    p = np.load(os.path.join(R9, f"family_{f}.npz"))
    cal = [date.fromordinal(int(v)) for v in p["dates"]]
    cols = [str(c) for c in p["cols"]]
    yrs = (cal[-1] - cal[int(np.argmax(np.abs(p["X"]).sum(1) > 0))]).days / 365.25
    tpy = {c: float((p["X"][:, i] != 0).sum() / yrs) for i, c in enumerate(cols)}
    out = []
    for v in res["variants"]:
        inst, *parts = v["name"].split("|")
        if f == "fd":
            tier = f"reject (family {res['family_verdict'].lower()})"
        elif v["name"] in rw:
            tier = "1 (Romano-Wolf significant)"
        elif v["sharpe_validation_raw"] >= 0.3 and v["sharpe_discovery"] > 0:
            tier = "2 (robust)"
        elif v["sharpe_validation_raw"] > 0:
            tier = "3 (positive)"
        else:
            tier = "reject"
        out.append({"family": LABELS[f], "strategy": v["name"], "instrument": inst, "params": "; ".join(parts),
                    "trades_per_year": round(tpy[v["name"]], 1), "exposure_pct": "",
                    "sharpe_discovery": round(v["sharpe_discovery"], 2), "sharpe_validation_raw": round(v["sharpe_validation_raw"], 2),
                    "sharpe_validation_timing": "", "rw_p_timing": round(v["rw_p_verdict_basis"], 3), "sharpe_holdout_2026": "", "tier": tier})
    return out


if __name__ == "__main__":
    with open(LIB, newline="") as fh:
        r = csv.DictReader(fh)
        fields = r.fieldnames
        old = [x for x in r if x["family"] not in LABELS.values()]
    new = rows("gt") + rows("fd")
    with open(LIB, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(old + new)
    from collections import Counter
    print("kept", len(old), "added", len(new), Counter(x["tier"] for x in new if x["family"] == LABELS["gt"]))
    for x in new:
        if x["tier"].startswith(("1", "2")):
            print(x["strategy"], x["tier"], x["sharpe_discovery"], x["sharpe_validation_raw"], x["trades_per_year"])
