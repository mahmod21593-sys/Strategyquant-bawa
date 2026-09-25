"""W1 (PREREGISTRATION.md A10): MR-06 on 15 untested world indices, 2000 -> 2026-09. -> results/world_mr06.json"""
from __future__ import annotations

import json
import os
from datetime import date

import vstats as vs
from data_yahoo import daily

OUT = os.path.join(os.path.dirname(__file__), "results")
BPS = 1e4
DEV = ["^IBEX", "^AEX", "FTSEMIB.MI", "^BFX", "^ATX", "^TA125.TA", "^STI"]
EM = ["^KS11", "^TWII", "^BSESN", "^BVSP", "^MXX", "^JKSE", "^KLSE", "^MERV"]
US_BROAD = ["^NYA", "^MID", "^XAX"]


def events(sym, start=date(2000, 1, 1)):
    rows = [r for r in daily(sym) if r["date"] >= date(1999, 1, 1)]
    rets = [None] + [b["c"] / a["c"] - 1 for a, b in zip(rows, rows[1:])]
    g = {}
    for i in range(1, len(rows)):
        g.setdefault(rows[i]["date"].year, []).append(rets[i] * BPS)
    ym = {y: vs.mean(v) for y, v in g.items()}
    out = []
    for i in range(3, len(rows) - 1):
        if rets[i] < 0 and rets[i - 1] < 0 and rets[i - 2] < 0 and rows[i + 1]["date"] >= start:
            d = rows[i + 1]["date"]
            out.append((d, rets[i + 1] * BPS - ym[d.year]))
    return out


def pool(syms, lo=date(2000, 1, 1), hi=date(2026, 12, 31)):
    g = {}
    for s in syms:
        for d, x in EV[s]:
            if lo <= d <= hi:
                g.setdefault(d, []).append(x)
    ds = sorted(g)
    return ds, [vs.mean(g[d]) for d in ds]


EV = {}


def main():
    for s in DEV + EM + US_BROAD:
        EV[s] = events(s)
    ds, xs = pool(DEV + EM)
    res = {"W1": vs.summarize(ds, xs, 1, 5, 1.5)}
    t = res["W1"]["t_hac"]
    res["W1"]["p_two_sided"] = 2 * (1 - vs.N01.cdf(abs(t)))
    res["W1"]["verdict"] = "CONFIRMED" if res["W1"]["p_one_sided"] < 0.05 and res["W1"]["net_mean_bps"] > 0 else "NOT CONFIRMED"
    for name, syms in (("developed", DEV), ("emerging", EM)):
        d, x = pool(syms)
        res[name] = vs.summarize(d, x, 1, 5, 1.5, boot=False)
    for name, lo, hi in (("2000_2012", date(2000, 1, 1), date(2012, 12, 31)), ("2013_on", date(2013, 1, 1), date(2026, 12, 31))):
        d, x = pool(DEV + EM, lo, hi)
        res[name] = vs.summarize(d, x, 1, 5, 1.5, boot=False)
    res["per_index"] = {s: vs.summarize([d for d, _ in EV[s]], [x for _, x in EV[s]], 1, 5, 1.5, boot=False) for s in DEV + EM}
    res["us_broad_secondary"] = {s: vs.summarize([d for d, _ in EV[s]], [x for _, x in EV[s]], 1, 5, 1.5, boot=False) for s in US_BROAD}
    json.dump(res, open(os.path.join(OUT, "world_mr06.json"), "w"), indent=1, default=str)
    w = res["W1"]
    print(f"W1 {w['verdict']} n={w['n']} mean={w['mean_bps']:.2f} net={w['net_mean_bps']:.2f} t={w['t_hac']:.2f} p1={w['p_one_sided']:.4f} "
          f"p2={w['p_two_sided']:.4f} yrs={w['years_pred_sign']:.2f} ci={[round(c, 1) for c in w['ci95_bps']]}")
    for k in ("developed", "emerging", "2000_2012", "2013_on"):
        x = res[k]
        print(f"  {k:10s} n={x['n']} mean={x['mean_bps']:.2f} t={x['t_hac']:.2f}")
    for grp in ("per_index", "us_broad_secondary"):
        for s, x in res[grp].items():
            print(f"  {s:11s} n={x['n']:4d} mean={x['mean_bps']:7.2f} t={x['t_hac']:5.2f}")


if __name__ == "__main__":
    main()
