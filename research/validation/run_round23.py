"""Round 23 (PREREGISTRATION.md A37): the Japanese-holiday Tokyo-morning effect on unseen 2002-07 JPY-cross data, and
the day after a holiday.

    python3 run_round23.py   -> results/round23_jpy_holidays.json
"""
from __future__ import annotations

import json
import math
import os
from datetime import date, timedelta

import numpy as np

import vstats as vs
from data_audit import spike_mask
from data_calendar import gotobi_days, japan_holidays
from data_minutes import local, price_at
from run_round11 import TOKYO

OUT = os.path.join(os.path.dirname(__file__), "results")
E = date(1970, 1, 1).toordinal()
CROSSES = ("EURJPY", "GBPJPY", "CHFJPY", "AUDJPY", "NZDJPY", "CADJPY")


def hac(v):
    x = np.array(v, dtype=float)
    t = vs.nw_t(list(x), 5)
    return {"n": int(len(x)), "mean_bps": float(x.mean() * 1e4), "t": t}


def welch(a, b, sign):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    t = float((a.mean() - b.mean()) / se)
    return {"diff_bps": float((a.mean() - b.mean()) * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t, sign), "n": [int(len(a)), int(len(b))]}


def day_types(y0, y1):
    import holidays
    nat = {d for d in holidays.Japan(years=range(y0, y1 + 1)) if d.weekday() < 5 and not (d.month == 1 and d.day <= 3) and not (d.month == 12 and d.day == 31)}
    bank = japan_holidays(y0, y1)
    got = gotobi_days(y0, y1)
    out = {}
    d = date(y0, 1, 1)
    while d <= date(y1, 12, 31):
        if d.weekday() < 5:
            if d in nat:
                out[d] = "HOL"
            elif d not in bank:
                prev = d - timedelta(days=1)
                while prev.weekday() >= 5:
                    prev -= timedelta(days=1)
                after = prev in nat
                out[d] = "GOTO" if d in got else "AFTER" if after else "NORMAL"
        d += timedelta(days=1)
    return out


def windows(sym, years, lo, hi):
    t, x = local(sym, years, TOKYO)
    keep = ~spike_mask(x, 0.01)
    t, x = t[keep], x[keep]
    if sym == "AUDJPY":  # A34a: the corrupt 2005 file
        yr = np.array([date.fromordinal(int(v) + E).year for v in t // 1440])
        t, x = t[yr != 2005], x[yr != 2005]
    day, mod = t // 1440, t % 1440
    p0, p1, p2 = price_at(day, mod, x, 540), price_at(day, mod, x, 595), price_at(day, mod, x, 655)
    out = {"PRE": {}, "POST": {}}
    for k, a in p1.items():
        d = date.fromordinal(int(k) + E)
        if not (lo <= d <= hi) or k not in p0 or k not in p2:
            continue
        pre, post = a / p0[k] - 1, a / p2[k] - 1
        if abs(pre) < 0.05 and abs(post) < 0.05:
            out["PRE"][d], out["POST"][d] = pre, post
    return out


def main():
    typ = day_types(2002, 2026)
    per = {s: windows(s, range(2002, 2008), date(2002, 1, 1), date(2007, 12, 31)) for s in CROSSES}
    for s, w in per.items():
        print("cross", s, len(w["PRE"]), flush=True)
    basket = {}
    for win in ("PRE", "POST"):
        days = sorted({d for s in per for d in per[s][win]})
        basket[win] = {d: float(np.mean([per[s][win][d] for s in per if d in per[s][win]])) for d in days
                       if sum(d in per[s][win] for s in per) >= 3}
    uj = windows("USDJPY", range(2014, 2027), date(2014, 1, 1), date(2026, 9, 18))
    by = lambda rows, lab: [v for d, v in rows.items() if typ.get(d) == lab]
    prim = {"H1": hac(by(basket["PRE"], "HOL")), "H2": welch(by(basket["PRE"], "HOL"), by(basket["PRE"], "NORMAL"), -1),
            "D1": welch(by(uj["POST"], "AFTER"), by(uj["POST"], "NORMAL"), 1), "D2": welch(by(basket["POST"], "AFTER"), by(basket["POST"], "NORMAL"), 1)}
    prim["H1"]["p_one_sided"] = vs.p_one_sided(prim["H1"]["t"], -1)
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    res = {"primary": prim,
           "holiday_leg": "CONFIRMED" if prim["H1"]["p_holm"] < 0.05 and prim["H2"]["p_holm"] < 0.05 else "NOT CONFIRMED",
           "day_after": "DAY-AFTER EFFECT" if prim["D1"]["p_holm"] < 0.05 and prim["D2"]["p_holm"] < 0.05 else "NOT CONFIRMED"}
    # the build checks
    uj_all = windows("USDJPY", range(2003, 2027), date(2003, 1, 1), date(2026, 9, 18))
    res["build_check_holiday_short_usdjpy_2003_2026_net_bps"] = hac([-v - 1e-4 for v in by(uj_all["PRE"], "HOL")])
    res["build_check_day_after_post_usdjpy_2014_2026_net_bps"] = hac([v - 1e-4 for v in by(uj["POST"], "AFTER")])
    res["per_cross_holiday_pre"] = {s: hac(by(w["PRE"], "HOL")) for s, w in per.items() if len(by(w["PRE"], "HOL")) > 10}
    res["per_cross_day_after_post"] = {s: hac(by(w["POST"], "AFTER")) for s, w in per.items() if len(by(w["POST"], "AFTER")) > 10}
    res["basket_by_type"] = {win: {lab: hac(by(basket[win], lab)) for lab in ("HOL", "AFTER", "NORMAL", "GOTO")} for win in ("PRE", "POST")}
    res["usdjpy_2014_2026_by_type"] = {win: {lab: hac(by(uj[win], lab)) for lab in ("HOL", "AFTER", "NORMAL", "GOTO")} for win in ("PRE", "POST")}
    json.dump(res, open(os.path.join(OUT, "round23_jpy_holidays.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "holiday_leg", "day_after", "build_check_holiday_short_usdjpy_2003_2026_net_bps",
                                          "build_check_day_after_post_usdjpy_2014_2026_net_bps")}, indent=1, default=str))
    for k in ("per_cross_holiday_pre", "per_cross_day_after_post"):
        print(k, {s: (round(v["mean_bps"], 2), round(v["t"], 2), v["n"]) for s, v in res[k].items()})
    for k in ("basket_by_type", "usdjpy_2014_2026_by_type"):
        print(k, {w: {l: (round(v["mean_bps"], 2), round(v["t"], 2), v["n"]) for l, v in d.items()} for w, d in res[k].items()})


if __name__ == "__main__":
    main()
