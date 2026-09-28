"""Round 43 (PREREGISTRATION.md A57): crypto-day N3 momentum confirmed on 13 FTMO altcoins (Binance minute 2019-26) and on
unseen 2017-18 BTC/ETH. C1: FTMO server-day anchor (New York + 7 h); C2: 00:00 UTC anchor with a swap per trade.

    python3 run_round43.py   -> results/round43_crypto_day.json
"""
from __future__ import annotations

import io
import json
import math
import os
import zipfile
from datetime import date

import numpy as np

import run_family_a as fa
import vstats as vs
from data_binance import _month_zip
from data_histdata import NY
from run_round24 import to_battery
from run_round34_minute import r3_grid
from run_round42 import to_local

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 14996
ALTS = ["ADA", "DOT", "DASH", "LTC", "XRP", "DOGE", "XMR", "NEO", "SOL", "BNB", "XLM", "AAVE", "LINK"]
ETF = date(2024, 1, 11)
PRIMARY = "range|k0.5|flat"


def minutes(sym, start, end):
    ts, xs = [], []
    y, m = start
    while (y, m) <= end:
        p = _month_zip(sym, "1m", y, m)
        if p:
            z = zipfile.ZipFile(p)
            a = np.genfromtxt(io.StringIO(z.read(z.namelist()[0]).decode("ascii")), delimiter=",", usecols=(0, 1, 2, 3, 4), invalid_raise=False)
            a = a[np.isfinite(a[:, 0])]
            t = a[:, 0].astype(np.int64)
            ts.append(np.where(t > 10 ** 14, t // 1000, t))
            xs.append(a[:, 1:5])
        m += 1
        if m == 13:
            y, m = y + 1, 1
    if not ts:
        return None, None
    t, x = np.concatenate(ts), np.concatenate(xs)
    o = np.argsort(t, kind="stable")
    return t[o], x[o]


def grid(t, x, cost, anchor, until):
    tl = to_local(t, NY) + 420 if anchor == "server" else to_local(t, None)
    g = r3_grid(tl, x, cost, 5, 1435)
    return {v: {d: r[0] for d, r in rows.items() if d <= until} for v, rows in g.items()}


def stats(v, lag=5):
    a = np.array(v, dtype=float)
    t = vs.nw_t(list(a), lag) if len(a) >= 10 else math.nan
    return {"n": int(len(a)), "mean_bps": float(a.mean() * 1e4) if len(a) else None, "t_hac": t, "p_one_sided": vs.p_one_sided(t) if np.isfinite(t) else 1.0}


def basket(src):
    days = sorted(set(d for s in src.values() for d in s))
    return days, [float(np.mean([s[d] for s in src.values() if d in s])) for d in days]


def with_halves(ds, v):
    s = stats(v)
    mid = len(v) // 2
    s["halves_bps"] = (float(np.mean(v[:mid]) * 1e4), float(np.mean(v[mid:]) * 1e4))
    s["split"] = str(ds[mid])
    return s


def main():
    until = date(2026, 8, 31)
    g1, g2, info = {}, {}, {}
    for c in ALTS:
        t, x = minutes(f"{c}USDT", (2019, 1), (2026, 8))
        if t is None:
            print("no data", c, flush=True)
            continue
        g1[c] = grid(t, x, 15.0, "server", until)
        g2[c] = grid(t, x, 20.0, "utc", until)
        n = len(g1[c][PRIMARY])
        info[c] = {"sessions": n, "first": str(min(g1[c][PRIMARY])) if n else None, "last": str(max(g1[c][PRIMARY])) if n else None}
        print("CD", c, info[c], flush=True)
    d1, v1 = basket({c: g1[c][PRIMARY] for c in g1})
    d2, v2 = basket({c: g2[c][PRIMARY] for c in g2})
    c1, c2 = with_halves(d1, v1), with_halves(d2, v2)
    g3 = {}
    for c in ("BTC", "ETH"):
        t, x = minutes(f"{c}USDT", (2017, 8), (2018, 12))
        g3[c] = grid(t, x, 15.0, "utc", date(2018, 12, 31))
        print("CD unseen", c, len(g3[c][PRIMARY]), flush=True)
    d3, v3 = basket({c: g3[c][PRIMARY] for c in g3})
    c3 = with_halves(d3, v3)
    prim = {"C1": c1, "C2": c2, "C3": c3}
    holm = vs.holm({k: p["p_one_sided"] for k, p in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    ok1 = c1["p_holm"] < 0.05 and all(h > 0 for h in c1["halves_bps"])
    ok2 = c2["p_holm"] < 0.05 and all(h > 0 for h in c2["halves_bps"])
    res = {"primary": prim, "data": info,
           "verdict": "EDGE (server-day anchor)" if ok1 else "EDGE (UTC anchor, swap paid)" if ok2 else "NO EDGE"}
    res["per_coin"] = {c: {"server": stats(list(g1[c][PRIMARY].values())), "utc": stats(list(g2[c][PRIMARY].values()))} for c in g1}
    res["share_coins_positive"] = {"server": float(np.mean([s["server"]["mean_bps"] > 0 for s in res["per_coin"].values()])),
                                   "utc": float(np.mean([s["utc"]["mean_bps"] > 0 for s in res["per_coin"].values()]))}
    res["pre_post_etf"] = {a: {"pre": stats([x for d, x in zip(ds, v) if d < ETF]), "post": stats([x for d, x in zip(ds, v) if d >= ETF])}
                           for a, ds, v in (("server", d1, v1), ("utc", d2, v2))}
    res["by_year_server"] = {y: stats([x for d, x in zip(d1, v1) if d.year == y]) for y in sorted({d.year for d in d1})}
    res["cost_plus5"] = {"server": stats([x - 5e-4 for x in v1]), "utc": stats([x - 5e-4 for x in v2])}
    res["grid"] = {a: {v: stats(basket({c: g[c][v] for c in g})[1]) for v in g[next(iter(g))]} for a, g in (("server", g1), ("utc", g2))}
    per = {f"{a}|{c}|{v}": g[c][v] for a, g in (("server", g1), ("utc", g2)) for c in g for v in g[c] if g[c][v]}
    alld = sorted(set(d for r in per.values() for d in r))
    res["battery"] = to_battery(per, "CD", alld[0], alld[len(alld) // 2], alld[0].year + 3)
    json.dump(res, open(os.path.join(OUT, "round43_crypto_day.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in res if k not in ("grid", "per_coin", "by_year_server")}, indent=1, default=str))
    for c, s in res["per_coin"].items():
        print(c, "server", round(s["server"]["mean_bps"], 1), round(s["server"]["t_hac"], 2), "| utc", round(s["utc"]["mean_bps"], 1), round(s["utc"]["t_hac"], 2), s["server"]["n"])
    for a, g in res["grid"].items():
        print(a, {v: (round(s["mean_bps"], 1), round(s["t_hac"], 2)) for v, s in g.items()})
    for y, s in res["by_year_server"].items():
        print(y, round(s["mean_bps"], 1), round(s["t_hac"], 2))


if __name__ == "__main__":
    main()
