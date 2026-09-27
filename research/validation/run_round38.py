"""Round 38 (PREREGISTRATION.md A52): the native N3 momentum grid on FTMO energy and silver CFDs.

    python3 run_round38.py COST   A52 cost procedure (median session ask - bid, page from 2025-03-03, + 0.5 bp) -> results/round38_costs.json
    python3 run_round38.py RUN    the test                                                                    -> results/round38_commodity_momentum.json
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from datetime import date, datetime, timezone

import numpy as np

import run_family_a as fa
import vstats as vs
from data_audit import spike_mask
from data_duka_chart import UA
from data_duka_chart import local as dlocal
from data_histdata import NY
from run_round24 import clean_local, to_battery
from run_round34_minute import r3_grid

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 14337
END = date(2026, 9, 18)
SPLIT_T1 = date(2020, 6, 1)
PRIMARY = "range|k0.5|flat"
# name: (source, instrument, session start, session end (NY minutes), Dukascopy instrument for the spread)
MARKETS = {"WTI": ("duka", "LIGHT.CMD/USD", 540, 870, "LIGHT.CMD/USD"),
           "BRENT": ("duka", "BRENT.CMD/USD", 540, 870, "BRENT.CMD/USD"),
           "NATGAS": ("duka", "GAS.CMD/USD", 540, 870, "GAS.CMD/USD"),
           "XAGUSD": ("histdata", "XAGUSD", 505, 805, "XAG/USD")}


def page(ins, side, ts):
    u = (f"https://freeserv.dukascopy.com/2.0/?path=chart/json3&instrument={ins}&offer_side={side}&interval=1MIN&splits=true"
         f"&stocks=true&limit=30000&time_direction=N&timestamp={ts}&jsonp=_cb")
    for _ in range(6):
        s = subprocess.run(["curl", "-sS", "-m", "120", "-A", UA, "-H", "Referer: https://freeserv.dukascopy.com/2.0/?path=chart/index", u],
                           capture_output=True, text=True).stdout
        try:
            rows = json.loads(s[s.find("(") + 1:s.rfind(")")])
            if rows and rows[0]:
                return {r[0]: r for r in rows}
        except ValueError:
            pass
    raise RuntimeError(ins + side)


def cost():
    ts = int(datetime(2025, 3, 3, tzinfo=timezone.utc).timestamp() * 1000)
    out = {}
    for name, (_, _, op, cl, ins) in MARKETS.items():
        b, a = page(ins, "B", ts), page(ins, "A", ts)
        sp = []
        for t in sorted(set(a) & set(b)):
            lt = datetime.fromtimestamp(t / 1000, timezone.utc).astimezone(NY)
            if op <= lt.hour * 60 + lt.minute < cl:
                ca, cb = a[t][4], b[t][4]
                sp.append((ca - cb) / ((ca + cb) / 2) * 1e4)
        med = float(np.median(sp))
        out[name] = {"session_minutes": len(sp), "median_spread_bps": med, "cost_per_entry_bps": med + 0.5}
        print(name, out[name], flush=True)
    json.dump(out, open(os.path.join(OUT, "round38_costs.json"), "w"), indent=1)


def load(name):
    src, ins, *_ = MARKETS[name]
    if src == "duka":
        t, x = dlocal(ins, NY, END)
        sp = spike_mask(x, 0.02)
        return t[~sp], x[~sp]
    return clean_local(ins, range(2010, 2027), NY)


def stats(v):
    a = np.array(v, dtype=float)
    t = vs.nw_t(list(a), 5)
    return {"n": int(len(a)), "mean_bps": float(a.mean() * 1e4), "t_hac": t, "p_one_sided": vs.p_one_sided(t),
            "sharpe": float(a.mean() / a.std(ddof=1) * math.sqrt(252)) if len(a) > 2 and a.std(ddof=1) > 0 else None}


def summ(rows):
    ds = sorted(rows)
    mid = ds[len(ds) // 2]
    s = stats([rows[d] for d in ds])
    s["first"], s["last"], s["split"] = str(ds[0]), str(ds[-1]), str(mid)
    s["halves_bps"] = (float(np.mean([rows[d] for d in ds if d < mid]) * 1e4), float(np.mean([rows[d] for d in ds if d >= mid]) * 1e4))
    s["pre_2020_06_bps"] = float(np.mean([rows[d] for d in ds if d < SPLIT_T1]) * 1e4)
    s["post_2020_06_bps"] = float(np.mean([rows[d] for d in ds if d >= SPLIT_T1]) * 1e4)
    return s


def run():
    costs = json.load(open(os.path.join(OUT, "round38_costs.json")))
    grids, grids2x = {}, {}
    for name, (_, _, op, cl, _) in MARKETS.items():
        t, x = load(name)
        c = costs[name]["cost_per_entry_bps"]
        g = r3_grid(t, x, c, op, cl)
        grids[name] = {v: {d: r[0] for d, r in rows.items() if d <= END} for v, rows in g.items()}
        grids2x[name] = {d: r[0] - r[1] * c / 1e4 for d, r in g[PRIMARY].items() if d <= END}
        print("CM", name, len(grids[name][PRIMARY]), "sessions, cost", round(c, 2), flush=True)

    def basket(src):
        days = sorted(set(d for s in src.values() for d in s))
        return {d: float(np.mean([s[d] for s in src.values() if d in s])) for d in days}

    b = basket({n: grids[n][PRIMARY] for n in grids})
    c0 = summ(b)
    per = {f"C_{n}": summ(grids[n][PRIMARY]) for n in grids}
    holm = vs.holm({k: v["p_one_sided"] for k, v in per.items()})
    for k in per:
        per[k]["p_holm"] = holm[k]
    res = {"C0_portfolio": c0, "per_instrument": per,
           "verdict": {"family": "EDGE" if (c0["p_one_sided"] < 0.05 and all(h > 0 for h in c0["halves_bps"])) else "NO EDGE"}}
    for k, v in per.items():
        res["verdict"][k] = "EDGE" if (v["p_holm"] < 0.05 and all(h > 0 for h in v["halves_bps"])) else "NO EDGE"
    res["portfolio_2x_cost"] = summ(basket(grids2x))
    res["grid"] = {n: {v: summ(g[v]) for v in g if g[v]} for n, g in grids.items()}
    res["share_variants_positive"] = float(np.mean([s["mean_bps"] > 0 for g in res["grid"].values() for s in g.values()]))
    # silver second feed (Dukascopy XAG/USD from 2014-07)
    try:
        t, x = dlocal("XAG/USD", NY, END)
        sp = spike_mask(x, 0.02)
        g2 = {d: r[0] for d, r in r3_grid(t[~sp], x[~sp], costs["XAGUSD"]["cost_per_entry_bps"], 505, 805)[PRIMARY].items() if d <= END}
        hd = grids["XAGUSD"][PRIMARY]
        com = sorted(set(g2) & set(hd))
        res["silver_second_feed"] = {"common_days": len(com), "corr": float(np.corrcoef([g2[d] for d in com], [hd[d] for d in com])[0, 1]),
                                     "duka": stats([g2[d] for d in com]), "histdata": stats([hd[d] for d in com])}
    except Exception as ex:
        res["silver_second_feed"] = {"error": repr(ex)}
    th, xh = clean_local("NSXUSD", range(2013, 2027), NY)
    n3 = {d: r[0] for d, r in r3_grid(th, xh, 1.5)[PRIMARY].items()}
    com = sorted(set(n3) & set(b))
    res["corr_portfolio_vs_US100_N3"] = float(np.corrcoef([b[d] for d in com], [n3[d] for d in com])[0, 1])
    pv = {f"{n}|{v}": grids[n][v] for n in grids for v in grids[n]}
    alld = sorted(set(d for r in pv.values() for d in r))
    res["battery"] = to_battery(pv, "CM", alld[0], alld[len(alld) // 2], alld[0].year + 3)
    json.dump(res, open(os.path.join(OUT, "round38_commodity_momentum.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in res if k != "grid"}, indent=1, default=str))
    for n, g in res["grid"].items():
        print(n, {v: (round(s["mean_bps"], 2), round(s["t_hac"], 2)) for v, s in g.items()})


if __name__ == "__main__":
    {"COST": cost, "RUN": run}[sys.argv[1]]()
