"""Round 32 (PREREGISTRATION.md A46).

    python3 run_round32.py KS   annual return seasonality across the FTMO universe (KLN 2016)  -> results/round32_ks.json
    python3 run_round32.py HP   intraday half-hour periodicity (HKS 2010)                      -> results/round32_hp.json
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
from data_histdata import NY
from data_minutes import price_at
from data_yahoo import daily
from run_round10 import fx_daily
from run_round11 import LONDON
from run_round24 import clean_local, rv_bars, to_battery, ttest

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 13962
E = date(1970, 1, 1).toordinal()
END = date(2026, 8, 31)
IDX = ("SPY", "QQQ", "DIA", "IWM", "^N225", "^GDAXI", "^FTSE", "^AXJO", "^FCHI", "^HSI", "^IBEX", "^STOXX50E")
FX = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD")
SIDE_COST = {**{s: 1.5e-4 for s in IDX}, **{s: 1.0e-4 for s in FX}, "XAUUSD": 2.5e-4, "XAGUSD": 5.0e-4}


# ---------------------------------------------------------------- KS

def monthly_returns():
    """{instrument: {(year, month): return}} from month-end closes."""
    out = {}
    for s in IDX:
        rows = [r for r in daily(s) if r["date"] <= END]
        px = {}
        for r in rows:
            px[(r["date"].year, r["date"].month)] = r["c"]  # last write per month = month-end close
        out[s] = px
    for s in FX:
        px = {}
        for r in fx_daily(s):
            if r["date"] <= END:
                px[(r["date"].year, r["date"].month)] = r["c"]
        out[s] = px
    for s in ("XAUUSD", "XAGUSD"):
        b = rv_bars(s)
        px = {}
        for d in sorted(b):
            if d <= END:
                px[(d.year, d.month)] = b[d]
        out[s] = px
    rets = {}
    for s, px in out.items():
        ms = sorted(px)
        rets[s] = {b: px[b] / px[a] - 1 for a, b in zip(ms[:-1], ms[1:]) if (b[0] - a[0]) * 12 + b[1] - a[1] == 1}
    return rets


def ks_run(rets, months, n_side, min_obs):
    """Monthly long-short book. Returns [(month, gross, net)]."""
    hist = {s: {} for s in rets}  # per instrument: {calendar month: [past returns]}
    seen = {s: sorted(rets[s]) for s in rets}
    rows = []
    for ym in months:
        y, m = ym
        scores = {}
        for s in rets:
            past = [rets[s][(yy, m)] for yy in range(1990, y) if (yy, m) in rets[s]]
            if len(past) >= min_obs and ym in rets[s]:
                scores[s] = float(np.mean(past))
        if len(scores) < 2 * n_side + 2:
            continue
        rank = sorted(scores, key=lambda q: -scores[q])
        k = max(1, len(rank) // 3) if n_side == 0 else n_side
        long, short = rank[:k], rank[-k:]
        g = float(np.mean([rets[s][ym] for s in long]) - np.mean([rets[s][ym] for s in short]))
        cost = float(np.mean([2 * SIDE_COST[s] for s in long + short]))  # in and out, averaged per unit of each leg
        net = g - 2 * cost - 0.04 / 12  # both legs' costs + 4%/yr financing on the two gross legs
        rows.append((ym, g, net))
    return rows


def family_ks():
    rets = monthly_returns()
    months = sorted({ym for s in rets for ym in rets[s] if (2003, 2) <= ym <= (2026, 8)})
    res = {"universe_size_by_2017": sum(1 for s in rets if len([1 for ym in rets[s] if ym < (2017, 1)]) > 100)}
    per = {}
    grids = {}
    for lab, n_side, mo in (("T3m8", 3, 8), ("T3m15", 3, 15), ("TERm8", 0, 8), ("TERm15", 0, 15)):
        rows = ks_run(rets, months, n_side, mo)
        grids[lab] = rows
        per[f"KS|{lab}"] = {date(ym[0], ym[1], 28): net for ym, g, net in rows}
    rows = grids["T3m8"]
    k1 = ttest([g for _, g, _ in rows])
    post = [(ym, g, n) for ym, g, n in rows if ym >= (2017, 1)]
    k2 = ttest([g for _, g, _ in post])
    holm = vs.holm({"K1": k1["p_one_sided"], "K2": k2["p_one_sided"]})
    k1["p_holm"], k2["p_holm"] = holm["K1"], holm["K2"]
    res["K1_gross_full"] = k1
    res["K2_gross_post_pub"] = k2
    res["net_full"] = ttest([n for _, _, n in rows])
    res["net_post_pub"] = ttest([n for _, _, n in post])
    res["net_post_halves_bps"] = (float(np.mean([n for ym, _, n in post if ym < (2022, 1)]) * 1e4),
                                  float(np.mean([n for ym, _, n in post if ym >= (2022, 1)]) * 1e4))
    both = k1["p_holm"] < 0.05 and k2["p_holm"] < 0.05
    res["verdict"] = ("EDGE" if both and all(h > 0 for h in res["net_post_halves_bps"]) else
                      "SEASONAL, NOT TRADEABLE" if both else "NO EDGE")
    res["grid_gross_monthly_bps"] = {lab: {"mean": round(float(np.mean([g for _, g, _ in r]) * 1e4), 1),
                                           "t": round(float(ttest([g for _, g, _ in r])["t"]), 2), "n": len(r)} for lab, r in grids.items()}
    res["battery"] = to_battery(per, "KS", date(2003, 1, 1), date(2017, 1, 1), 2010)
    json.dump(res, open(os.path.join(OUT, "round32_ks.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in res if k != "battery"}, indent=1, default=str))
    print("battery", json.dumps({k: res["battery"][k] for k in ("spa_validation", "walk_forward_top5", "verdict")}, default=str))


# ---------------------------------------------------------------- HP

HP_SPEC = {"SPXUSD": (NY, 570, 960, 2013, 1.5e-4), "NSXUSD": (NY, 570, 960, 2013, 1.5e-4),
           "EURUSD": (LONDON, 420, 1200, 2003, 1.0e-4), "USDJPY": (LONDON, 420, 1200, 2003, 1.0e-4)}


def bin_matrix(sym):
    tz, m0, m1, y0, cost = HP_SPEC[sym]
    t, x = clean_local(sym, range(y0, 2027), tz)
    day, mod = t // 1440, t % 1440
    marks = list(range(m0, m1 + 1, 30))
    px = {m: price_at(day, mod, x, m) for m in marks}
    days = sorted(set.intersection(*[set(px[m]) for m in marks]))
    days = [k for k in days if date.fromordinal(int(k) + E).weekday() < 5 and date.fromordinal(int(k) + E) <= END]
    R = np.full((len(days), len(marks) - 1), np.nan)
    for i, k in enumerate(days):
        for j in range(len(marks) - 1):
            r = px[marks[j + 1]][k] / px[marks[j]][k] - 1
            if abs(r) < 0.03:
                R[i, j] = r
    dts = [date.fromordinal(int(k) + E) for k in days]
    return dts, R, cost


def family_hp():
    res, per = {}, {}
    pool_prod, pool_daily_g, pool_daily_n3 = [], {}, {}
    desc = {}
    for sym in HP_SPEC:
        dts, R, cost = bin_matrix(sym)
        prev = R[:-1]
        cur = R[1:]
        d1 = dts[1:]
        ok = np.isfinite(prev) & np.isfinite(cur)
        # H1 products per day (for pooled corr via bootstrap on days)
        for i in range(len(d1)):
            m = ok[i]
            if m.any():
                pool_prod.append((d1[i], prev[i][m], cur[i][m]))
        g = np.where(ok, np.sign(prev) * cur, np.nan)
        gd = {d: float(np.nanmean(g[i])) for i, d in enumerate(d1) if np.isfinite(g[i]).any()}
        # H3 filter: |prev| above that bin's trailing-60-day 80th percentile
        nb = R.shape[1]
        thr = np.full_like(prev, np.nan)
        for j in range(nb):
            col = R[:, j]
            for i in range(60, len(d1) + 1):
                w = col[max(0, i - 60):i]
                w = np.abs(w[np.isfinite(w)])
                if len(w) >= 30 and i - 1 < len(d1):
                    thr[i - 1, j] = np.quantile(w, 0.8)
        sel = ok & np.isfinite(thr) & (np.abs(prev) > thr)
        n3 = np.where(sel, np.sign(prev) * cur - 2 * cost, np.nan)
        nd = {d: float(np.nansum(n3[i])) for i, d in enumerate(d1) if np.isfinite(n3[i]).any()}
        per[f"{sym}|ALL"] = {d: float(np.nansum(np.where(ok[i], np.sign(prev[i]) * cur[i] - 2 * cost, np.nan))) for i, d in enumerate(d1)
                            if ok[i].any()}
        per[f"{sym}|TOPQ"] = nd
        for d, v in gd.items():
            pool_daily_g.setdefault(d, []).append(v)
        for d, v in nd.items():
            pool_daily_n3.setdefault(d, []).append(v)
        m = ok
        r_own = float(np.corrcoef(prev[m], cur[m])[0, 1])
        desc[sym] = {"days": len(d1), "bins": nb, "lag1_same_bin_corr": r_own,
                     "gross_rule_bps_per_bin": float(np.nanmean(g) * 1e4),
                     "net_filtered_bps_per_day": float(np.mean(list(nd.values())) * 1e4) if nd else None,
                     "filtered_trades_per_day": float(np.mean([np.isfinite(n3[i]).sum() for i in range(len(d1))]))}
        print("HP", sym, json.dumps(desc[sym]), flush=True)
    res["descriptive"] = desc
    # H1: pooled correlation with day-block bootstrap
    rng = np.random.default_rng(29)
    days_all = list(range(len(pool_prod)))
    a = np.concatenate([p for _, p, _ in pool_prod])
    b = np.concatenate([c for _, _, c in pool_prod])
    rho = float(np.corrcoef(a, b)[0, 1])
    bs = []
    for _ in range(2000):
        pick = rng.integers(0, len(pool_prod), len(pool_prod))
        aa = np.concatenate([pool_prod[i][1] for i in pick])
        bb = np.concatenate([pool_prod[i][2] for i in pick])
        bs.append(np.corrcoef(aa, bb)[0, 1])
    se = float(np.std(bs, ddof=1))
    h1 = {"rho": rho, "se": se, "z": rho / se, "p_one_sided": vs.p_one_sided(rho / se), "n_pairs": int(len(a))}
    g_series = [float(np.mean(v)) for d, v in sorted(pool_daily_g.items())]
    h2 = {**ttest(g_series)}
    h2["t"] = vs.nw_t(g_series, 5)
    h2["p_one_sided"] = vs.p_one_sided(h2["t"])
    n_series = {d: float(np.mean(v)) for d, v in sorted(pool_daily_n3.items())}
    h3_vals = [v for _, v in sorted(n_series.items())]
    h3 = {**ttest(h3_vals)}
    h3["t"] = vs.nw_t(h3_vals, 5)
    h3["p_one_sided"] = vs.p_one_sided(h3["t"])
    holm = vs.holm({"H1": h1["p_one_sided"], "H2": h2["p_one_sided"], "H3": h3["p_one_sided"]})
    h1["p_holm"], h2["p_holm"], h3["p_holm"] = holm["H1"], holm["H2"], holm["H3"]
    cut = date(2020, 1, 1)
    h3_halves = (float(np.mean([v for d, v in n_series.items() if d < cut]) * 1e4),
                 float(np.mean([v for d, v in n_series.items() if d >= cut]) * 1e4))
    res["primary"] = {"H1": h1, "H2_gross_per_bin": h2, "H3_net_per_day_filtered": {**h3, "halves_bps": h3_halves}}
    res["verdict"] = ("EDGE" if h3["p_holm"] < 0.05 and all(h > 0 for h in h3_halves) else
                      "MECHANISM, NOT TRADEABLE" if h1["p_holm"] < 0.05 or h2["p_holm"] < 0.05 else "NO EDGE")
    res["battery"] = to_battery(per, "HP", date(2003, 1, 1), cut, 2010)
    json.dump(res, open(os.path.join(OUT, "round32_hp.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "verdict")}, indent=1, default=str))


if __name__ == "__main__":
    {"KS": family_ks, "HP": family_hp}[sys.argv[1]]()
