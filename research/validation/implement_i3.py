"""A18 I3 (implementability, not a test): N3 with the paper's volatility-targeted sizing. -> results/i3.json"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import vstats as vs
from data_histdata import table
from prop_lifecycle import evaluate, to_days
from run_noise_area import run

R = os.path.join(os.path.dirname(__file__), "results")


def main():
    rows = run("N3", path=True, y1=2027)[0]
    tab = table("NSXUSD", range(2013, 2027), {959})
    days = sorted(d for d in tab if 959 in tab[d] and d.weekday() < 5)
    close = {d: tab[d][959][3] for d in days}
    ret = {b: close[b] / close[a] - 1 for a, b in zip(days, days[1:]) if (b - a).days <= 5}
    rd = sorted(ret)
    pos = {d: i for i, d in enumerate(rd)}
    lev = {}
    for d, _ in rows:
        i = next((pos[x] for x in (d,) if x in pos), None)
        prior = [ret[x] for x in rd if x < d][-14:] if i is None else [ret[x] for x in rd[max(0, i - 14):i]]
        if len(prior) >= 10:
            lev[d] = min(4.0, 0.02 / vs.sd(prior)) if vs.sd(prior) > 0 else 4.0
    ins = [(d, v) for d, v in rows if date(2014, 1, 1) <= d <= date(2025, 12, 31) and d in lev]
    k = 1 / vs.mean([lev[d] for d, _ in ins])
    res = {"mean_raw_leverage": vs.mean([lev[d] for d, _ in ins]), "rescale": k}
    for label, lo, hi in (("2014_2025", date(2014, 1, 1), date(2025, 12, 31)), ("holdout_2026", date(2026, 1, 1), date(2026, 12, 31))):
        sel = [(d, v) for d, v in rows if lo <= d <= hi and d in lev]
        flat = [v[0] * 1e4 for _, v in sel]
        vt = [v[0] * lev[d] * k * 1e4 for d, v in sel]
        res[label] = {"n": len(sel), "flat_mean_bps": vs.mean(flat), "flat_sharpe": vs.mean(flat) / vs.sd(flat) * math.sqrt(252),
                      "vt_mean_bps": vs.mean(vt), "vt_sharpe": vs.mean(vt) / vs.sd(vt) * math.sqrt(252), "vt_t": vs.nw_t(vt, 5), "flat_t": vs.nw_t(flat, 5)}
    flat_book = {d: v for d, v in ins}
    vt_book = {d: tuple(x * lev[d] * k for x in v) for d, v in ins}
    for name, book in (("flat", flat_book), ("vol_target", vt_book)):
        a = evaluate(to_days(book), "ftmo_2step_100k.json", 0.03, 4.0, None)
        res[f"ftmo2_fixed4x_{name}"] = {x: a[x] for x in ("p_pass", "ev_per_attempt_usd", "mean_months", "ev_per_account_month_usd")}
    print(json.dumps(res, indent=1))
    json.dump(res, open(os.path.join(R, "i3.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
