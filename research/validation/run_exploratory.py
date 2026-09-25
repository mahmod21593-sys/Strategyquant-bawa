"""Exploratory edge scan (PREREGISTRATION.md amendment A1).

Stage 1 (discovery, 1990-2012) is computed and saved BEFORE stage 2 (confirmation, 2013+) is computed.
"""
from __future__ import annotations

import json
import math
import os
from datetime import date, timedelta

import vstats as vs
from data_yahoo import daily

OUT = os.path.join(os.path.dirname(__file__), "results")
BPS = 1e4
DISC_END = date(2013, 1, 1)
COST = 1.5


def third_friday(y, m):
    d = date(y, m, 15)
    while d.weekday() != 4:
        d += timedelta(days=1)
    return d


def index_events(rows):
    """Map candidate id -> list of (date, excess_bps) for a daily index series."""
    rets = [None] + [(b["c"] / a["c"] - 1) for a, b in zip(rows, rows[1:])]
    yr = {}
    for i in range(1, len(rows)):
        yr.setdefault(rows[i]["date"].year, []).append(rets[i] * BPS)
    base = {y: vs.mean(v) for y, v in yr.items()}
    months = {}
    for i, r in enumerate(rows):
        months.setdefault((r["date"].year, r["date"].month), []).append(i)
    first = {v[0] for v in months.values()}
    last = {v[-1] for v in months.values()}
    tf = {third_friday(y, m) for (y, m) in months}
    ev = {k: [] for k in [f"E{n:02d}" for n in range(1, 18)]}
    for i in range(4, len(rows)):
        d = rows[i]["date"]
        x = rets[i] * BPS - base[d.year]
        r1, r2, r3 = rets[i - 1], rets[i - 2], rets[i - 3]
        wd = d.weekday()
        if wd < 5:
            ev[f"E{wd + 1:02d}"].append((d, x))
        if r1 < 0 and r2 < 0 and r3 < 0:
            ev["E06"].append((d, x))
        if r1 > 0 and r2 > 0 and r3 > 0:
            ev["E07"].append((d, x))
        if r1 < 0:
            ev["E08"].append((d, x))
        if r1 > 0:
            ev["E09"].append((d, x))
        if i in first:
            ev["E10"].append((d, x))
        if i in last:
            ev["E11"].append((d, x))
        if d.month in (11, 12, 1, 2, 3, 4):
            ev["E12"].append((d, x))
        if d in tf:
            ev["E13"].append((d, x))
        if rows[i - 1]["date"] in tf:
            ev["E14"].append((d, x))
        f = third_friday(d.year, d.month)
        if f - timedelta(days=4) <= d <= f:
            ev["E15"].append((d, x))
        if r1 <= -0.02:
            ev["E16"].append((d, x))
        if r1 >= 0.02:
            ev["E17"].append((d, x))
    return ev


def etf_events(rows):
    ev = {"E18": [], "E19": [], "E20": []}
    for a, b, c in zip(rows, rows[1:], rows[2:]):
        prev_ret = b["c"] / a["c"] - 1
        on = (c["o"] / b["c"] - 1) * BPS
        ev["E18"].append((c["date"], on if prev_ret < 0 else -on))  # long ON after down, short ON after up
        gap = c["o"] / b["c"] - 1
        intra = (c["c"] / c["o"] - 1) * BPS
        if gap < -0.005:
            ev["E19"].append((c["date"], intra))
        if gap > 0.005:
            ev["E20"].append((c["date"], intra))
    return ev


def stats_for(pairs, lo=None, hi=None, sign=1):
    sel = [(d, x) for d, x in pairs if (lo is None or d >= lo) and (hi is None or d < hi)]
    if len(sel) < 20:
        return {"n": len(sel)}
    s = vs.summarize([d for d, _ in sel], [x for _, x in sel], sign, 5, COST, boot=False)
    s["p_two_sided"] = 2 * min(s["p_one_sided"], 1 - s["p_one_sided"])
    return s


def load(sym, start):
    return [r for r in daily(sym) if r["date"] >= start]


def main():
    os.makedirs(OUT, exist_ok=True)
    gspc = index_events(load("^GSPC", date(1989, 12, 1)))
    gspc.update(etf_events(load("SPY", date(1993, 1, 29))))
    disc = {k: stats_for(v, date(1990, 1, 1), DISC_END) for k, v in gspc.items()}
    pv = {k: v["p_two_sided"] for k, v in disc.items() if "p_two_sided" in v}
    q = vs.bh(pv)
    for k in disc:
        disc[k]["bh_q"] = q.get(k)
        disc[k]["discovered"] = bool(q.get(k) is not None and q[k] < 0.10)
        disc[k]["sign"] = 1 if disc[k].get("mean_bps", 0) > 0 else -1
    json.dump(disc, open(os.path.join(OUT, "exploratory_discovery.json"), "w"), indent=2, default=str)
    print("DISCOVERY 1990-2012 (^GSPC; E18-E20 on SPY)")
    for k, v in sorted(disc.items()):
        if "mean_bps" in v:
            print(f"  {k} n={v['n']:5d} mean={v['mean_bps']:7.2f} t={v['t_hac']:6.2f} q={v['bh_q']:.3f} {'DISCOVERED' if v['discovered'] else ''}")

    # Stage 2 only after discovery is saved
    ndx = index_events(load("^NDX", date(1989, 12, 1)))
    ndx.update(etf_events(load("QQQ", date(1999, 3, 10))))
    conf = {}
    for k, v in disc.items():
        if not v.get("discovered"):
            continue
        g = stats_for(gspc[k], DISC_END, None, v["sign"])
        n = stats_for(ndx[k], DISC_END, None, v["sign"])
        net_ok = g.get("mean_bps", 0) * v["sign"] - COST > 0
        passed = (g.get("p_one_sided", 1) < 0.05 and n.get("mean_bps", 0) * v["sign"] > 0 and net_ok)
        conf[k] = {"gspc_2013": g, "ndx_2013": n, "net_of_cost_positive": net_ok, "CONFIRMED": passed}
    json.dump(conf, open(os.path.join(OUT, "exploratory_confirmation.json"), "w"), indent=2, default=str)
    print("CONFIRMATION 2013-> (^GSPC and ^NDX; ETF signals on SPY and QQQ)")
    for k, v in conf.items():
        g, n = v["gspc_2013"], v["ndx_2013"]
        print(f"  {k} gspc mean={g.get('mean_bps', math.nan):7.2f} t={g.get('t_hac', math.nan):5.2f} p1={g.get('p_one_sided', math.nan):.3f} | "
              f"ndx mean={n.get('mean_bps', math.nan):7.2f} t={n.get('t_hac', math.nan):5.2f} -> {'CONFIRMED' if v['CONFIRMED'] else 'not confirmed'}")


if __name__ == "__main__":
    main()
