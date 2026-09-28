"""Round 42 (PREREGISTRATION.md A56): the native N3 momentum grid on BTC and ETH, anchored at 09:30 New York; the spot-ETF
launch (2024-01-11) as a natural experiment; a 00:00 UTC anchor as control. Binance spot one-minute klines 2019-01 -> 2026-08.

    python3 run_round42.py   -> results/round42_crypto_n3.json
"""
from __future__ import annotations

import io
import json
import math
import os
import zipfile
from datetime import date, datetime, timezone

import numpy as np

import run_family_a as fa
import vstats as vs
from data_binance import _month_zip
from data_histdata import NY
from data_minutes import EPOCH
from run_round24 import to_battery
from run_round34_minute import r3_grid

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 14681
ETF = date(2024, 1, 11)
END = date(2026, 8, 31)
COST, COST_HI = 10.0, 15.0
PRIMARY = "range|k0.5|flat"


def minutes(sym, y0=2019, y1=2026, m1=8):
    """(UTC ms, OHLC) arrays from the monthly zips."""
    ts, xs = [], []
    for y in range(y0, y1 + 1):
        for m in range(1, 13):
            if (y, m) > (y1, m1):
                break
            p = _month_zip(sym, "1m", y, m)
            if not p:
                print("missing", sym, y, m, flush=True)
                continue
            z = zipfile.ZipFile(p)
            raw = z.read(z.namelist()[0]).decode("ascii")
            a = np.genfromtxt(io.StringIO(raw), delimiter=",", usecols=(0, 1, 2, 3, 4), invalid_raise=False)
            a = a[np.isfinite(a[:, 0])]
            t = a[:, 0].astype(np.int64)
            t = np.where(t > 10 ** 14, t // 1000, t)
            ts.append(t)
            xs.append(a[:, 1:5])
    t = np.concatenate(ts)
    x = np.concatenate(xs)
    o = np.argsort(t, kind="stable")
    return t[o], x[o]


def to_local(t_ms, tz):
    um = t_ms // 60_000
    ud = um // 1440
    u, inv = np.unique(ud, return_inverse=True)
    off = np.array([int(datetime.fromordinal(int(v) + EPOCH).replace(hour=12, tzinfo=timezone.utc).astimezone(tz).utcoffset().total_seconds() // 60)
                    for v in u], dtype=np.int64) if tz is not None else np.zeros(len(u), dtype=np.int64)
    return um + off[inv]


def stats(v, lag=5):
    a = np.array(v, dtype=float)
    t = vs.nw_t(list(a), lag)
    return {"n": int(len(a)), "mean_bps": float(a.mean() * 1e4), "t_hac": t, "p_one_sided": vs.p_one_sided(t),
            "sharpe": float(a.mean() / a.std(ddof=1) * math.sqrt(252)) if len(a) > 2 and a.std(ddof=1) > 0 else None}


def welch(a, b):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    t = float((a.mean() - b.mean()) / se)
    return {"diff_bps": float((a.mean() - b.mean()) * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t), "n": [int(len(a)), int(len(b))]}


def main():
    grids, grids_hi, utc = {}, {}, {}
    for sym in ("BTCUSDT", "ETHUSDT"):
        t, x = minutes(sym)
        tl = to_local(t, NY)
        g = r3_grid(tl, x, COST)
        grids[sym] = {v: {d: r[0] for d, r in rows.items() if d <= END} for v, rows in g.items()}
        grids_hi[sym] = {d: r[0] - r[1] * (COST_HI - COST) / 1e4 for d, r in g[PRIMARY].items() if d <= END}
        gu = r3_grid(to_local(t, None), x, COST, 5, 1435)
        utc[sym] = {v: {d: r[0] for d, r in rows.items() if d <= END} for v, rows in gu.items()}
        print("CN3", sym, len(grids[sym][PRIMARY]), "NY sessions;", len(utc[sym][PRIMARY]), "UTC days", flush=True)

    def basket(src):
        days = sorted(set(d for s in src.values() for d in s))
        return days, [float(np.mean([s[d] for s in src.values() if d in s])) for d in days]

    ds, v = basket({s: grids[s][PRIMARY] for s in grids})
    k1 = stats(v)
    mid = len(v) // 2
    k1["halves_bps"] = (float(np.mean(v[:mid]) * 1e4), float(np.mean(v[mid:]) * 1e4))
    k1["split"] = str(ds[mid])
    pre = [x for d, x in zip(ds, v) if d < ETF]
    post = [x for d, x in zip(ds, v) if d >= ETF]
    k2 = welch(post, pre)
    prim = {"K1": k1, "K2": k2}
    holm = vs.holm({k: p["p_one_sided"] for k, p in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    post_s = stats(post)
    if k1["p_holm"] < 0.05 and all(h > 0 for h in k1["halves_bps"]):
        verdict = "EDGE"
    elif k2["p_holm"] < 0.05 and post_s["mean_bps"] > 0 and post_s["t_hac"] > 2:
        verdict = "EDGE (ETF ERA ONLY)"
    else:
        verdict = "NO EDGE"
    res = {"primary": prim, "verdict": verdict, "pre_etf": stats(pre), "post_etf": post_s}
    res["per_coin"] = {s: {"all": stats(list(grids[s][PRIMARY].values())),
                           "pre": stats([x for d, x in grids[s][PRIMARY].items() if d < ETF]),
                           "post": stats([x for d, x in grids[s][PRIMARY].items() if d >= ETF])} for s in grids}
    dh, vh = basket(grids_hi)
    res["basket_at_15bps"] = stats(vh)
    res["by_year"] = {y: stats([x for d, x in zip(ds, v) if d.year == y]) for y in sorted({d.year for d in ds})}
    du, vu = basket({s: utc[s][PRIMARY] for s in utc})
    res["control_utc_anchor"] = {"all": stats(vu), "pre": stats([x for d, x in zip(du, vu) if d < ETF]),
                                 "post": stats([x for d, x in zip(du, vu) if d >= ETF])}
    res["grid"] = {s: {k: stats(list(g.values())) for k, g in grids[s].items() if g} for s in grids}
    per = {f"{s}|{k}": g for s in grids for k, g in grids[s].items()}
    alld = sorted(set(d for r in per.values() for d in r))
    res["battery"] = to_battery(per, "CN3", alld[0], alld[len(alld) // 2], alld[0].year + 3)
    json.dump(res, open(os.path.join(OUT, "round42_crypto_n3.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in res if k not in ("grid", "by_year")}, indent=1, default=str))
    for y, st in res["by_year"].items():
        print(y, round(st["mean_bps"], 2), round(st["t_hac"], 2), st["n"])
    for s, g in res["grid"].items():
        print(s, {k: (round(x["mean_bps"], 1), round(x["t_hac"], 2)) for k, x in g.items()})


if __name__ == "__main__":
    main()
