"""Round 2 tests Q1-Q5 (PREREGISTRATION.md amendment A3). -> results/round2.json, results/series_round2.json"""
from __future__ import annotations

import json
import math
import os
from datetime import date, timedelta

import vstats as vs
from data_calendar import employment_days, fomc_days
from data_yahoo import daily
from run_intraday_yahoo import bars60, NY

OUT = os.path.join(os.path.dirname(__file__), "results")
BPS = 1e4
SERIES = {}


def block(key, dates, pnl, cut=None, cost=0.0, lag=5, sign=1):
    res = vs.summarize(dates, pnl, sign, lag, cost)
    SERIES[key] = {"dates": [str(d) for d in dates], "pnl_bps": pnl, "cost_bps": cost, "lag": lag}
    if cut:
        pre = [(d, p) for d, p in zip(dates, pnl) if d < cut]
        post = [(d, p) for d, p in zip(dates, pnl) if d >= cut]
        res["pre"] = vs.summarize([d for d, _ in pre], [p for _, p in pre], sign, lag, cost, boot=False)
        res["post_publication"] = vs.summarize([d for d, _ in post], [p for _, p in post], sign, lag, cost, boot=False)
        res["post_publication"]["from"] = str(cut)
    return res


def year_base(rows, fn):
    g = {}
    for i in range(1, len(rows)):
        v = fn(i)
        if v is not None:
            g.setdefault(rows[i]["date"].year, []).append(v)
    return {y: vs.mean(v) for y, v in g.items()}


def q1():
    rows = [r for r in daily("^GSPC") if r["date"] >= date(1993, 12, 1)]
    base = year_base(rows, lambda i: (rows[i]["c"] / rows[i - 1]["c"] - 1) * BPS)
    fomc, emp = set(fomc_days()), set(employment_days())
    out = {}
    for name, ev in (("union", fomc | emp), ("fomc", fomc), ("employment", emp)):
        d, p = [], []
        for i in range(1, len(rows)):
            if rows[i]["date"] in ev and rows[i]["date"] >= date(1994, 1, 1):
                d.append(rows[i]["date"])
                p.append((rows[i]["c"] / rows[i - 1]["c"] - 1) * BPS - base[rows[i]["date"].year])
        out[name] = block("Q1" if name == "union" else f"Q1_{name}", d, p, date(2013, 1, 1), 1.5)
    trading = {r["date"] for r in rows}
    out["coverage"] = {"fomc_days_in_data": len(fomc & trading), "employment_days_in_data": len(emp & trading),
                       "employment_days_not_trading_days": sorted(str(x) for x in emp if x not in trading and x >= date(1994, 1, 1))[:20]}
    res = out["union"]
    res["fomc_only"], res["employment_only"], res["coverage"] = out["fomc"], out["employment"], out["coverage"]
    return res


def streak_rows(rows):
    rets = [None] + [(b["c"] / a["c"] - 1) for a, b in zip(rows, rows[1:])]
    return rets


def q2(hold_days=0):
    rows = [r for r in daily("SPY") if r["date"] >= date(1993, 2, 1)]
    rets = streak_rows(rows)
    if hold_days == 0:
        base = year_base(rows, lambda i: (rows[i]["c"] / rows[i]["o"] - 1) * BPS)
    else:
        base = year_base(rows, lambda i: (rows[i]["c"] / rows[i - 1]["c"] - 1) * BPS)
    d, p = [], []
    for i in range(3, len(rows) - 1 - hold_days):
        if rets[i] < 0 and rets[i - 1] < 0 and rets[i - 2] < 0:
            e = rows[i + 1]
            x = rows[i + 1 + hold_days]
            ret = (x["c"] / e["o"] - 1) * BPS
            adj = base[e["date"].year] * (1 if hold_days == 0 else 2)
            d.append(x["date"])
            p.append(ret - adj)
    return block("Q2" if hold_days == 0 else "Q2b", d, p, date(2013, 1, 1), 1.5)


def q3():
    per = []
    for sym in ["SPY", "QQQ", "IWM", "DIA"]:
        b = bars60(sym)
        days = {}
        for ts, (o, c) in b.items():
            loc = ts.astimezone(NY)
            days.setdefault(loc.date(), {})[loc.strftime("%H:%M")] = (o, c)
        rows = [(d, days[d]["15:30"][0], days[d]["15:30"][1]) for d in sorted(days) if "15:30" in days[d]]
        closes = {d: c for d, _, c in rows}
        yr = {}
        for (d0, _, c0), (d1, _, c1) in zip(rows, rows[1:]):
            yr.setdefault(d1.year, []).append((c1 / c0 - 1) * BPS)
        base = {y: vs.mean(v) for y, v in yr.items()}
        for i in range(3, len(rows) - 1):
            d, p1530, close = rows[i]
            c_1, c_2, c_3 = rows[i - 1][2], rows[i - 2][2], rows[i - 3][2]
            if c_1 < c_2 < c_3 and p1530 < c_1:
                nxt = rows[i + 1]
                per.append((nxt[0], (nxt[2] / p1530 - 1) * BPS - base[nxt[0].year], sym))
    g = {}
    for d, x, _ in per:
        g.setdefault(d, []).append(x)
    ds = sorted(g)
    res = block("Q3", ds, [vs.mean(g[x]) for x in ds], None, 1.5)
    res["n_signals_all_symbols"] = len(per)
    return res


def q4():
    out = {}
    pooled = []
    for sym in ["TLT", "IEF", "GLD", "SLV", "USO", "FXE", "FXY", "UUP", "BTC-USD", "ETH-USD"]:
        rows = daily(sym)
        rets = streak_rows(rows)
        base = year_base(rows, lambda i: rets[i] * BPS)
        d, p = [], []
        for i in range(4, len(rows)):
            if rets[i - 1] < 0 and rets[i - 2] < 0 and rets[i - 3] < 0:
                d.append(rows[i]["date"])
                p.append(rets[i] * BPS - base[rows[i]["date"].year])
        s = vs.summarize(d, p, 1, 5, 0.0, boot=False)
        s["p_two_sided"] = 2 * min(s["p_one_sided"], 1 - s["p_one_sided"])
        out[sym] = s
        if sym not in ("BTC-USD", "ETH-USD"):
            pooled += list(zip(d, p))
    g = {}
    for d, x in pooled:
        g.setdefault(d, []).append(x)
    ds = sorted(g)
    res = block("Q4", ds, [vs.mean(g[x]) for x in ds], date(2013, 1, 1), 0.0)
    res["p_two_sided"] = 2 * min(res["p_one_sided"], 1 - res["p_one_sided"])
    res["per_asset"] = out
    res["note"] = "pooled over the 8 non-crypto ETFs; crypto reported per asset. Prediction: approx 0 (two-sided)"
    return res


def q5():
    trades = []
    per = {}
    for sym, start in (("BTC-USD", date(2014, 9, 22)), ("ETH-USD", date(2017, 11, 13))):
        rows = [r for r in daily(sym) if r["date"] >= start]
        px = {r["date"]: r["c"] for r in rows}
        # weekly closes on Sundays (7-day crypto weeks)
        d = start + timedelta(days=(6 - start.weekday()) % 7)
        sundays = []
        while d <= rows[-1]["date"]:
            if d in px:
                sundays.append(d)
            d += timedelta(days=7)
        prev_pos = 0
        dd, pp = [], []
        for a, b, c in zip(sundays, sundays[1:], sundays[2:]):
            past = px[b] / px[a] - 1
            pos = 1 if past > 0 else -1
            r = (px[c] / px[b] - 1) * BPS
            cost = 10.0 if pos != prev_pos else 0.0
            prev_pos = pos
            dd.append(c)
            pp.append(pos * r - cost)
        per[sym] = vs.summarize(dd, pp, 1, 2, 0.0, boot=False)
        trades += list(zip(dd, pp))
    g = {}
    for d, x in trades:
        g.setdefault(d, []).append(x)
    ds = sorted(g)
    res = block("Q5", ds, [vs.mean(g[x]) for x in ds], date(2021, 1, 1), 0.0, lag=2)
    res["per_asset"] = per
    res["note"] = "weekly P&L in bps, already net of 10 bps per position flip"
    # comparison: buy-and-hold weekly
    bh = []
    for sym, start in (("BTC-USD", date(2014, 9, 22)), ("ETH-USD", date(2017, 11, 13))):
        rows = [r for r in daily(sym) if r["date"] >= start]
        px = {r["date"]: r["c"] for r in rows}
        ks = sorted(k for k in px if k.weekday() == 6)
        bh += [(b, (px[b] / px[a] - 1) * BPS) for a, b in zip(ks, ks[1:])]
    res["buy_hold_weekly_mean_bps"] = vs.mean([x for _, x in bh])
    return res


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"Q1": q1(), "Q2": q2(0), "Q2b": q2(1), "Q3": q3(), "Q4": q4(), "Q5": q5()}
    fam = {k: v["p_one_sided"] for k, v in res.items() if k != "Q4"}
    holm, bh = vs.holm(fam), vs.bh(fam)
    for k in fam:
        res[k]["p_holm_Q"] = holm[k]
        res[k]["q_bh_Q"] = bh[k]
    json.dump(res, open(os.path.join(OUT, "round2.json"), "w"), indent=2, default=str)
    json.dump(SERIES, open(os.path.join(OUT, "series_round2.json"), "w"), default=str)
    for k, v in res.items():
        print(f"{k:4s} n={v['n']:5d} mean={v['mean_bps']:7.2f} net={v['net_mean_bps']:7.2f} t={v['t_hac']:5.2f} "
              f"p={v['p_one_sided']:.4f} holmQ={v.get('p_holm_Q', float('nan')):.4f} yrs={v['years_pred_sign']} ci={[round(x, 1) for x in v['ci95_bps']]}")
        for part in ("pre", "post_publication"):
            if part in v and "mean_bps" in v[part]:
                x = v[part]
                print(f"      {part:16s} n={x['n']:5d} mean={x['mean_bps']:7.2f} t={x['t_hac']:5.2f} p={x['p_one_sided']:.4f}")
    for k in ("fomc_only", "employment_only"):
        x = res["Q1"][k]
        print("  Q1", k, "n", x["n"], "mean", round(x["mean_bps"], 2), "t", round(x["t_hac"], 2),
              "post", round(x["post_publication"]["mean_bps"], 2), round(x["post_publication"]["t_hac"], 2))
    print("  Q1 coverage", res["Q1"]["coverage"]["fomc_days_in_data"], res["Q1"]["coverage"]["employment_days_in_data"])
    for s, x in res["Q4"]["per_asset"].items():
        print("  Q4", s, "n", x["n"], "mean", round(x["mean_bps"], 2), "t", round(x["t_hac"], 2))
    for s, x in res["Q5"]["per_asset"].items():
        print("  Q5", s, "n", x["n"], "mean", round(x["mean_bps"], 1), "t", round(x["t_hac"], 2))
    print("  Q5 buy-hold weekly", round(res["Q5"]["buy_hold_weekly_mean_bps"], 1))


if __name__ == "__main__":
    main()
