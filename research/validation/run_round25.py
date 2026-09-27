"""Round 25 (PREREGISTRATION.md A39).

    python3 run_round25.py OX   COMEX gold/silver option expiry (4 business days before month-end) -> results/round25_ox.json
    python3 run_round25.py JM   Japanese fiscal year-end flows in USDJPY                            -> results/round25_jm.json
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date

import numpy as np

import run_family_a as fa
import vstats as vs
from data_fred import series as fred
from run_round10 import weekday_calendar, finish
from run_round24 import rv_bars, to_battery, ttest

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 13867
END = date(2026, 9, 18)
COST = {"XAUUSD": 2.5e-4, "XAGUSD": 5.0e-4}


# ---------------------------------------------------------------- OX

def opex_days(first_year=2010, last_year=2026):
    """The 4th-to-last US business day of each month (weekdays minus US federal holidays)."""
    import holidays
    us = set(holidays.UnitedStates(years=range(first_year, last_year + 1)))
    out = []
    for y in range(first_year, last_year + 1):
        for m in range(1, 13):
            nxt = date(y + (m == 12), m % 12 + 1, 1)
            bd = []
            d = date(y, m, 1)
            while d < nxt:
                if d.weekday() < 5 and d not in us:
                    bd.append(d)
                d = date.fromordinal(d.toordinal() + 1)
            if len(bd) >= 4:
                out.append(bd[-4])
    return [d for d in out if d <= END]


def family_ox():
    us3 = {(d.year, d.month): v / 100 for d, v in fred("IR3TIB01USM156N")}
    px = {s: rv_bars(s) for s in ("XAUUSD", "XAGUSD")}
    days = {s: sorted(p) for s, p in px.items()}
    idx = {s: {d: i for i, d in enumerate(days[s])} for s in px}
    ox = opex_days()
    res, per = {}, {}
    ev = {}
    for sym in ("XAUUSD", "XAGUSD"):
        dd, pp, ii = days[sym], px[sym], idx[sym]
        rows = []
        for o in ox:
            # OpEx close = the last trading day <= o
            j = ii.get(o)
            if j is None:
                cand = [d for d in dd if d <= o]
                if not cand:
                    continue
                j = ii[cand[-1]]
            if j < 5 or j + 5 >= len(dd):
                continue
            fin = (us3.get((o.year, o.month), 0.04) + 0.02) / 365
            r = {"opex": o}
            for w in (3, 5):
                into = pp[dd[j]] / pp[dd[j - w]] - 1
                after = pp[dd[j + w]] / pp[dd[j]] - 1
                cal_in, cal_af = (dd[j] - dd[j - w]).days, (dd[j + w] - dd[j]).days
                r[f"into{w}"], r[f"after{w}"] = into, after
                r[f"net_short_into{w}"] = -into - COST[sym] - fin * cal_in
                r[f"net_long_after{w}"] = after - COST[sym] - fin * cal_af
            rows.append(r)
        ev[sym] = rows
        for w in (3, 5):
            per[f"{sym}|SHORTINTO|{w}d"] = {r["opex"]: r[f"net_short_into{w}"] for r in rows}
            per[f"{sym}|LONGAFTER|{w}d"] = {r["opex"]: r[f"net_long_after{w}"] for r in rows}
        print("OX", sym, len(rows), flush=True)
    g = ev["XAUUSD"]
    into = [r["into3"] for r in g]
    after = [r["after3"] for r in g]
    ox1, ox2 = ttest(into), ttest(after)
    ox1["p_one_sided"] = vs.p_one_sided(ox1["t"], -1)  # into < 0
    holm = vs.holm({"OX1": ox1["p_one_sided"], "OX2": ox2["p_one_sided"]})
    ox1["p_holm"], ox2["p_holm"] = holm["OX1"], holm["OX2"]
    res["primary"] = {"OX1_gold_into_3d": ox1, "OX2_gold_after_3d": ox2}
    halves = lambda key, cut=date(2018, 1, 1): (float(np.mean([r[key] for r in g if r["opex"] < cut]) * 1e4),
                                                float(np.mean([r[key] for r in g if r["opex"] >= cut]) * 1e4))
    res["gold_halves_bps"] = {"into3": halves("into3"), "after3": halves("after3")}
    res["net_trades_bps"] = {"short_into3": ttest([r["net_short_into3"] for r in g]), "long_after3": ttest([r["net_long_after3"] for r in g])}
    e1 = ox1["p_holm"] < 0.05 and res["net_trades_bps"]["short_into3"]["mean_bps"] > 0 and all(h < 0 for h in res["gold_halves_bps"]["into3"])
    e2 = ox2["p_holm"] < 0.05 and res["net_trades_bps"]["long_after3"]["mean_bps"] > 0 and all(h > 0 for h in res["gold_halves_bps"]["after3"])
    res["verdict"] = "EDGE" if (e1 or e2) else "NO EDGE"
    res["silver"] = {"into3": ttest([r["into3"] for r in ev["XAGUSD"]]), "after3": ttest([r["after3"] for r in ev["XAGUSD"]])}
    res["battery"] = to_battery(per, "OX", date(2010, 1, 1), date(2019, 1, 1), 2013)
    json.dump(res, open(os.path.join(OUT, "round25_ox.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "gold_halves_bps", "net_trades_bps", "verdict", "silver")}, indent=1, default=str))


# ---------------------------------------------------------------- JM

def family_jm():
    from data_calendar import japan_holidays
    from run_round13 import fx_bars
    d, o, h, l, c = fx_bars("USDJPY")
    px = dict(zip(d, c))
    days = sorted(px)
    hol = japan_holidays(2003, 2026)
    biz = [x for x in days if x not in hol]
    res = {"events": []}
    marv, aprv = [], []
    for y in range(2003, 2027):
        mar = [x for x in biz if x.year == y and x.month == 3]
        apr = [x for x in biz if x.year == y and x.month == 4]
        if len(mar) < 7 or len(apr) < 6:
            continue
        r_mar = -(px[mar[-1]] / px[mar[-6]] - 1) - 1e-4      # short USDJPY, last 5 business days of March
        r_apr = (px[apr[4]] / px[mar[-1]] - 1) - 1e-4        # long USDJPY, first 5 business days of April
        marv.append((y, r_mar))
        aprv.append((y, r_apr))
        res["events"].append({"year": y, "march_short_net_bps": round(r_mar * 1e4, 1), "april_long_net_bps": round(r_apr * 1e4, 1)})
    jm1, jm2 = ttest([v for _, v in marv]), ttest([v for _, v in aprv])
    holm = vs.holm({"JM1": jm1["p_one_sided"], "JM2": jm2["p_one_sided"]})
    jm1["p_holm"], jm2["p_holm"] = holm["JM1"], holm["JM2"]
    res["JM1_march_short"] = jm1
    res["JM2_april_long"] = jm2
    hv = lambda vv: (float(np.mean([v for y, v in vv if y <= 2014]) * 1e4), float(np.mean([v for y, v in vv if y >= 2015]) * 1e4))
    res["halves_bps"] = {"JM1": hv(marv), "JM2": hv(aprv)}
    e1 = jm1["p_holm"] < 0.05 and all(h > 0 for h in res["halves_bps"]["JM1"])
    e2 = jm2["p_holm"] < 0.05 and all(h > 0 for h in res["halves_bps"]["JM2"])
    res["verdict"] = "EDGE" if (e1 or e2) else "NO EDGE"
    json.dump(res, open(os.path.join(OUT, "round25_jm.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("JM1_march_short", "JM2_april_long", "halves_bps", "verdict")}, indent=1, default=str))
    print({e["year"]: (e["march_short_net_bps"], e["april_long_net_bps"]) for e in res["events"]})


if __name__ == "__main__":
    {"OX": family_ox, "JM": family_jm}[sys.argv[1]]()
