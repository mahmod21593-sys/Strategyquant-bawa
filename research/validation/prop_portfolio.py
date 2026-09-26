"""Round 9 (A22): prop evaluation of the discovery-selected portfolio, bootstrapped from its OUT-OF-SAMPLE
2020-2025 daily returns. Daily-close P&L only (no intraday path): breach rates are optimistic. -> results/prop_portfolio.json"""
from __future__ import annotations

import json
import os
from datetime import date

import numpy as np

from prop_lifecycle import demean, evaluate, to_days

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")


def book(series, dates):
    return {d: (float(x), min(0.0, float(x)), max(0.0, float(x))) for d, x in zip(dates, series)
            if date(2020, 1, 1) <= d <= date(2025, 12, 31) and d.weekday() < 5}


def main():
    p = np.load(os.path.join(R9, "portfolio.npz"))
    dates = [date.fromordinal(int(d)) for d in p["dates"]]
    books = {"portfolio": book(p["port"], dates), "family_A": book(p["fam_A"], dates), "family_B": book(p["fam_B"], dates)}
    policies = {f"fixed {L:g}x": (L, None) for L in (1, 2, 3, 4, 6)}
    for k in (10, 20):
        for cap in (4, 6):
            policies[f"CPPI k={k} cap={cap}x"] = (1.0, (lambda a, k=k, cap=cap: max(0.0, min(cap, k * a.cushion()))))
    res = {}
    for name, bk in books.items():
        real, zero = to_days(bk), to_days(demean(bk))
        res[name] = {}
        for pol, (scale, sizer) in policies.items():
            a = evaluate(real, "ftmo_2step_100k.json", 0.03, scale, sizer)
            z = evaluate(zero, "ftmo_2step_100k.json", 0.03, scale, sizer)
            a["zero_edge_ev_per_attempt_usd"], a["zero_edge_p_pass"] = z["ev_per_attempt_usd"], z["p_pass"]
            a["edge_value_usd"] = a["ev_per_attempt_usd"] - z["ev_per_attempt_usd"]
            res[name][pol] = a
            print(name, pol, {k: round(v, 3) if isinstance(v, float) else v for k, v in a.items() if k in
                              ("p_pass", "zero_edge_p_pass", "ev_per_attempt_usd", "edge_value_usd", "mean_months", "ev_per_account_month_usd")}, flush=True)
    json.dump(res, open(os.path.join(OUT, "prop_portfolio.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
