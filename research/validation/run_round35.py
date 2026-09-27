"""Round 35 (PREREGISTRATION.md A49): the native N3 momentum grid on 12 FTMO US mega-cap stock CFDs (Dukascopy minute
candles 2017-26), with per-stock measured costs (results/round35_costs.json from measure_stock_costs.py).

    python3 run_round35.py   -> results/round35_stock_momentum.json
"""
from __future__ import annotations

import json
import math
import os
from datetime import date, datetime, timezone

import numpy as np

import run_family_a as fa
import vstats as vs
from data_audit import spike_mask
from data_duka_chart import local as dlocal
from data_histdata import NY
from measure_stock_costs import STOCKS
from run_round24 import clean_local, to_battery
from run_round34_minute import r3_grid

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 14154
END = date(2026, 9, 18)
ZERO_DTE = date(2022, 11, 14)
PRIMARY = "range|k0.5|flat"
CIKS = {"AAPL": [320193], "AMZN": [1018724], "MSFT": [789019], "NVDA": [1045810], "TSLA": [1318605], "META": [1326801],
        "GOOGL": [1652044], "JPM": [19617], "V": [1403161], "AMD": [2488], "AVGO": [1730168, 1649338], "NFLX": [1065280]}


def stats(v, lag=5):
    x = np.array(v, dtype=float)
    t = vs.nw_t(list(x), lag)
    return {"n": int(len(x)), "mean_bps": float(x.mean() * 1e4), "t_hac": t, "p_one_sided": vs.p_one_sided(t),
            "sharpe": float(x.mean() / x.std(ddof=1) * math.sqrt(252)) if x.std(ddof=1) > 0 else None}


def halves(rows):
    ds = sorted(rows)
    mid = ds[len(ds) // 2]
    return (float(np.mean([rows[d] for d in ds if d < mid]) * 1e4), float(np.mean([rows[d] for d in ds if d >= mid]) * 1e4), str(mid))


def reaction_sessions(sym, sessions):
    """Sessions after an 8-K Item 2.02 filing: same day if accepted before 09:30 ET, next session if after 16:00 ET."""
    from data_edgar import earnings_filings
    ss = sorted(sessions)
    out = set()
    for cik in CIKS[sym]:
        for acc in earnings_filings(cik):
            lt = acc.astimezone(NY)
            m = lt.hour * 60 + lt.minute
            d = lt.date()
            if m < 570:
                cand = [s for s in ss if s >= d][:1]
            elif m >= 960:
                cand = [s for s in ss if s > d][:1]
            else:
                continue
            if cand and (cand[0] - d).days <= 5:
                out.add(cand[0])
    return out


def welch(a, b):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    t = float((a.mean() - b.mean()) / se)
    return {"diff_bps": float((a.mean() - b.mean()) * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t), "n": [int(len(a)), int(len(b))]}


def main():
    costs = json.load(open(os.path.join(OUT, "round35_costs.json")))
    grids, grids2x, info = {}, {}, {}
    for sym, ins in STOCKS.items():
        t, x = dlocal(ins, NY, END)
        spikes = spike_mask(x, 0.03)
        t, x = t[~spikes], x[~spikes]
        c = costs[sym]["cost_per_entry_bps"]
        g = r3_grid(t, x, c)
        grids[sym] = {v: {d: r[0] for d, r in rows.items() if d <= END} for v, rows in g.items()}
        grids2x[sym] = {d: r[0] - r[1] * c / 1e4 for d, r in g[PRIMARY].items() if d <= END}
        info[sym] = {"minutes": int(len(t)), "spike_bars_dropped": int(spikes.sum()), "sessions": len(grids[sym][PRIMARY]),
                     "first": str(min(grids[sym][PRIMARY])), "cost_per_entry_bps": c}
        print("SM", sym, info[sym], flush=True)

    def basket(src):
        days = sorted(set(d for s in src.values() for d in s))
        return {d: float(np.mean([s[d] for s in src.values() if d in s])) for d in days}

    b1 = basket({s: grids[s][PRIMARY] for s in grids})
    b2 = basket(grids2x)
    ds = sorted(b1)
    s1 = stats([b1[d] for d in ds])
    h = halves(b1)
    per_stock = {s: stats(list(grids[s][PRIMARY].values())) for s in grids}
    n_pos = sum(v["mean_bps"] > 0 for v in per_stock.values())
    s1_ok = s1["p_one_sided"] < 0.05 and h[0] > 0 and h[1] > 0
    s2_ok = n_pos >= 10
    verdict = "EDGE" if (s1_ok and s2_ok) else "PARTIAL" if s1["p_one_sided"] < 0.05 else "NO EDGE"
    res = {"data": info, "S1_basket_primary": s1, "S1_halves_bps": h, "S2_stocks_positive": n_pos, "per_stock_primary": per_stock,
           "verdict": verdict, "basket_2x_cost": stats([b2[d] for d in sorted(b2)]),
           "basket_0dte_era": stats([b1[d] for d in ds if d >= ZERO_DTE]), "basket_pre_0dte": stats([b1[d] for d in ds if d < ZERO_DTE])}
    # stocks in play (earnings-reaction sessions), stock-day level
    er, other = [], []
    for s in grids:
        rs = reaction_sessions(s, grids[s][PRIMARY].keys())
        for d, v in grids[s][PRIMARY].items():
            (er if d in rs else other).append(v)
    res["earnings_sessions_vs_other"] = {"earnings": stats(er, 0), "other": stats(other, 0), "welch": welch(er, other)}
    # grid
    res["grid_basket"] = {v: stats([bb[d] for d in sorted(bb)]) for v in grids["AAPL"]
                          for bb in [basket({s: grids[s][v] for s in grids})]}
    res["share_variant_stock_positive"] = float(np.mean([np.mean(list(grids[s][v].values())) > 0 for s in grids for v in grids[s]]))
    # correlation with US100 N3 (HistData)
    th, xh = clean_local("NSXUSD", range(2013, 2027), NY)
    n3 = {d: r[0] for d, r in r3_grid(th, xh, 1.5)[PRIMARY].items()}
    com = sorted(set(n3) & set(b1))
    res["corr_basket_vs_US100_N3"] = float(np.corrcoef([b1[d] for d in com], [n3[d] for d in com])[0, 1])
    per = {f"{s}|{v}": grids[s][v] for s in grids for v in grids[s]}
    alld = sorted(set(d for r in per.values() for d in r))
    res["battery"] = to_battery(per, "SM", alld[0], alld[len(alld) // 2], alld[0].year + 3)
    json.dump(res, open(os.path.join(OUT, "round35_stock_momentum.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in res if k not in ("grid_basket", "per_stock_primary", "data")}, indent=1, default=str))
    for s, v in per_stock.items():
        print(s, round(v["mean_bps"], 2), round(v["t_hac"], 2), v["n"])
    for v, st in res["grid_basket"].items():
        print(v, round(st["mean_bps"], 2), round(st["t_hac"], 2))


if __name__ == "__main__":
    main()
