"""Post hoc robustness of round 19's GT result (A33): entry delay, exit time, cost, tails, per-year, combined PRE+POST.
Labelled post hoc in REPORT.md; none of this changes the pre-registered verdict.

    python3 gt_robustness.py   -> results/round19_gt_robustness.json
"""
from __future__ import annotations

import json
import os
from datetime import date

import numpy as np

import vstats as vs
from data_calendar import gotobi_days, japan_holidays
from data_minutes import local, price_at
from run_round11 import TOKYO

OUT = os.path.join(os.path.dirname(__file__), "results")
START, END = date(2014, 1, 1), date(2026, 9, 18)
E = date(1970, 1, 1).toordinal()


def stats(v):
    x = np.array(v)
    t = vs.nw_t(list(x), 5)
    return {"n": int(len(x)), "gross_bps": float(x.mean() * 1e4), "t": t, "sd_bps": float(x.std(ddof=1) * 1e4),
            "hit_rate": float((x > 0).mean()), "worst_bps": float(x.min() * 1e4), "p1_bps": float(np.quantile(x, 0.01) * 1e4)}


def main():
    got = gotobi_days()
    hol = japan_holidays()
    res = {}
    for sym in ("USDJPY", "EURJPY"):
        t, x = local(sym, range(2003, 2027), TOKYO)
        day, mod = t // 1440, t % 1440
        marks = [540, 595, 596, 597, 600, 610, 625, 640, 655, 660, 690, 720, 780, 900]
        px = {m: price_at(day, mod, x, m) for m in marks}
        opn = price_at(day, mod, x, 595, prefer_open=True)  # the open of the 09:55 bar
        ok = [k for k in px[595] if START <= date.fromordinal(int(k) + E) <= END and date.fromordinal(int(k) + E).weekday() < 5
              and date.fromordinal(int(k) + E) not in hol]
        g = [k for k in ok if date.fromordinal(int(k) + E) in got]
        r = {}

        def short(a, b, keys, pa=None):
            pa = pa or px[a]
            return [pa[k] / px[b][k] - 1 for k in keys if k in pa and k in px[b]]
        # entry delay (exit 10:55)
        r["entry_delay"] = {"09:55 bar close (primary)": stats(short(595, 655, g)), "09:55 bar open": stats(short(595, 655, g, opn)),
                            "09:56": stats(short(596, 655, g)), "09:57": stats(short(597, 655, g)), "10:00": stats(short(600, 655, g))}
        # exit time (entry 09:55)
        r["exit_time"] = {f"{m // 60:02d}:{m % 60:02d}": stats(short(595, m, g)) for m in (600, 610, 625, 640, 655, 660, 690, 720, 780, 900)}
        # combined PRE (long 09:00 -> 09:55) + POST (short 09:55 -> 10:55), per Gotobi day
        comb = [px[595][k] / px[540][k] - 1 + px[595][k] / px[655][k] - 1 for k in g if k in px[540] and k in px[655]]
        r["combined_pre_post"] = stats(comb)
        post = short(595, 655, g)
        r["cost_sensitivity_net_bps"] = {f"{c:.1f}": {"POST": float(np.mean(post) * 1e4 - c), "PRE+POST": float(np.mean(comb) * 1e4 - 2 * c)}
                                         for c in (0.5, 0.7, 1.0, 1.5, 2.0)}
        yr = {}
        for k in g:
            if k in px[655]:
                yr.setdefault(date.fromordinal(int(k) + E).year, []).append(px[595][k] / px[655][k] - 1)
        r["per_year_post_gross_bps"] = {y: round(float(np.mean(v) * 1e4), 2) for y, v in sorted(yr.items())}
        r["years_positive_post"] = f"{sum(np.mean(v) > 0 for v in yr.values())}/{len(yr)}"
        # by weekday and by Gotobi type
        r["by_type"] = {typ: stats([px[595][k] / px[655][k] - 1 for k in g if k in px[655] and got[date.fromordinal(int(k) + E)] == typ])
                        for typ in ("510", "ME")}
        r["by_weekday"] = {wd: stats([px[595][k] / px[655][k] - 1 for k in g if k in px[655] and date.fromordinal(int(k) + E).weekday() == i])
                           for i, wd in enumerate(("Mon", "Tue", "Wed", "Thu", "Fri"))}
        res[sym] = r
        print(sym, json.dumps({k: r[k] for k in ("entry_delay", "combined_pre_post", "cost_sensitivity_net_bps", "years_positive_post")}, indent=0), flush=True)
        print(sym, "exit", {k: (round(v["gross_bps"], 2), round(v["t"], 2)) for k, v in r["exit_time"].items()})
        print(sym, "type", {k: (round(v["gross_bps"], 2), round(v["t"], 2), v["n"]) for k, v in r["by_type"].items()})
        print(sym, "weekday", {k: (round(v["gross_bps"], 2), round(v["t"], 2), v["n"]) for k, v in r["by_weekday"].items()})
    json.dump(res, open(os.path.join(OUT, "round19_gt_robustness.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
