"""Round 9: rebuild the discovery-selected portfolio (results/portfolio.json) with intraday excursions, then run the
prop evaluation on its OUT-OF-SAMPLE 2020-2025 path. -> results/prop_portfolio.json

Lows are conservative: each leg's worst intraday point is summed as if all happened at once.
- A (daily reversal holds): position x (day low / prior close - 1), from Yahoo daily lows.
- B (intraday): the rule's own minute path (run_noise_area.run(path=True)).
- C (trend): each ETF position's worst excursion against the prior close.
- D (monthly FX): the monthly P&L booked on the month's last trading day, low = min(0, P&L).
"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import numpy as np

from data_histdata import available_years, local_table
from data_yahoo import daily
from prop_lifecycle import demean, evaluate, to_days
from run_family_a import COST, MARKUP, US, load, positions, signals
from run_family_b import MARKETS, YEARS
from run_noise_area import run
from run_round4 import irx_map, tbill
from run_round7 import G6_UNIVERSE

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
LO, HI = date(2020, 1, 1), date(2025, 12, 31)
TARGET = 0.10 / math.sqrt(252) / 2


def leg_a(name, rates, keys):
    sym, sn, ex, fn = name.split("|")
    d, c, h, l, craw, ret, rf = load(sym, rates, keys)
    sig, filt = signals(c, h, l, craw, ret)
    pos, entry = positions(sig[sn], filt[fn], c, ex)
    mark = MARKUP if sym in US else 0.0
    f = c / craw  # adjustment factor
    low = np.zeros(len(c))
    high = np.zeros(len(c))
    low[1:] = l[1:] * f[1:] / c[:-1] - 1
    high[1:] = h[1:] * f[1:] / c[:-1] - 1
    out = {}
    for i, dd in enumerate(d):
        if pos[i] == 0 and entry[i] == 0:
            continue
        k = pos[i] * mark + entry[i] * COST
        out[dd] = (pos[i] * (ret[i] - rf[i]) - k, pos[i] * min(0.0, low[i]) - k, pos[i] * max(0.0, high[i]))
    return out


def leg_b(name):
    sym, L, b, g, ex = name.split("|")
    tz, oh, ch, cost, excl = MARKETS[sym]
    o, c = oh[0] * 60 + oh[1], ch[0] * 60 + ch[1]
    closes = [c] + ([930] if sym == "JPXJPY" else [])
    ses = local_table(sym, available_years(sym, YEARS), tz, set(range(o - 1, max(closes) + 1)))
    rows = {}
    for cc in closes:
        first, last = o + 30, cc - 30
        spec = (sym, tz, oh, (cc // 60, cc % 60), (first // 60, first % 60), (last // 60, last % 60), cost, ex)
        r = dict(run("R9", lookback=int(L[1:]), grid=int(g[1:]), spec=spec, ses=ses, band=float(b[1:]), exclude=set(excl), path=True)[0])
        if sym == "JPXJPY":
            cut = date(2024, 11, 5)
            r = {dd: x for dd, x in r.items() if (dd < cut) == (cc == c)}
        rows.update(r)
    return rows


def leg_c(name, rates, keys):
    L = int(name.split("|")[0][1:])
    cal = sorted({r["date"] for r in daily("SPY") if date(2005, 1, 1) <= r["date"] <= HI})
    ci = {d: i for i, d in enumerate(cal)}
    T, A = len(cal), len(G6_UNIVERSE)
    px, ex, lo_, hi_ = (np.full((T, A), np.nan) for _ in range(4))
    for j, s in enumerate(G6_UNIVERSE):
        last = None
        for r in daily(s):
            d = r["date"]
            if d.weekday() >= 5 or d not in ci:
                continue
            i = ci[d]
            px[i, j] = r["adj"]
            if last is not None:
                ex[i, j] = r["adj"] / last[1] - 1 - tbill(rates, keys, last[0], d)
                lo_[i, j], hi_[i, j] = r["l"] / last[2] - 1, r["h"] / last[2] - 1
            last = (d, r["adj"], r["c"])
    for j in range(A):
        for i in range(1, T):
            if np.isnan(px[i, j]):
                px[i, j] = px[i - 1, j]
    exz, loz, hiz = np.nan_to_num(ex), np.nan_to_num(lo_), np.nan_to_num(hi_)
    vol = np.full((T, A), np.nan)
    delta = 60 / 61
    for j in range(A):
        m = v = None
        for i in range(T):
            if np.isnan(px[i, j]):
                continue
            x = exz[i, j]
            m = x if m is None else delta * m + (1 - delta) * x
            v = x * x if v is None else delta * v + (1 - delta) * (x - m) ** 2
            vol[i, j] = math.sqrt(v * 261)
    pos, cur = np.zeros((T, A)), np.zeros(A)
    for i in range(1, T):
        if (cal[i].year, cal[i].month) != (cal[i - 1].year, cal[i - 1].month):
            k = i - 1
            new = np.zeros(A)
            for j in range(A):
                if k < L + 60 or np.isnan(px[k - L, j]) or np.isnan(vol[k, j]):
                    continue
                new[j] = (1 if px[k, j] / px[k - L, j] > 1 else -1) * 0.40 / vol[k, j]
            n = (new != 0).sum()
            cur = new / n if n else new
        pos[i] = cur
    dpos = np.vstack([np.zeros(A), np.diff(pos, axis=0)])
    cost = 2e-4 * np.abs(dpos).sum(1)
    pnl = (pos * exz).sum(1) - cost
    worst = np.where(pos > 0, pos * loz, pos * hiz)
    best = np.where(pos > 0, pos * hiz, pos * loz)
    low = np.minimum(worst, 0).sum(1) - cost
    high = np.maximum(best, 0).sum(1)
    return {d: (float(pnl[i]), float(low[i]), float(high[i])) for i, d in enumerate(cal)}


def leg_d(name, trading_days):
    p = np.load(os.path.join(R9, "family_d.npz"))
    j = [str(c) for c in p["cols"]].index(name)
    last = {}
    for d in trading_days:
        last[(d.year, d.month)] = d
    out = {}
    for m, x in zip(p["months"], p["X"][:, j]):
        key = (int(m) // 100, int(m) % 100)
        if key in last:
            out[last[key]] = (float(x), min(0.0, float(x)), max(0.0, float(x)))
    return out


def combine(legs, rss=None):
    """Sum legs. With rss (a dict) also accumulate each leg's squared adverse excursion below its own close."""
    out = {}
    for w, leg in legs:
        for d, (p, l, h) in leg.items():
            if LO <= d <= HI and d.weekday() < 5:
                a = out.get(d, (0.0, 0.0, 0.0))
                out[d] = (a[0] + w * p, a[1] + w * l, a[2] + w * h)
                if rss is not None:
                    rss[d] = rss.get(d, 0.0) + (w * min(0.0, l - p)) ** 2
    return out


def main():
    sel = json.load(open(os.path.join(OUT, "portfolio.json")))
    volf = sel["discovery_daily_vol"]
    rates = irx_map()
    keys = sorted(rates)
    fam = {"A": [], "B": [], "C": [], "D": []}
    for name, w in sel["selection"]["A"]["weights"].items():
        fam["A"].append((w, leg_a(name, rates, keys)))
    for name, w in sel["selection"]["B"]["weights"].items():
        fam["B"].append((w, leg_b(name)))
        print("B leg", name, flush=True)
    for name, w in sel["selection"]["C"]["weights"].items():
        fam["C"].append((w, leg_c(name, rates, keys)))
    days = sorted({d for w, leg in fam["C"] for d in leg})
    for name, w in sel["selection"]["D"]["weights"].items():
        fam["D"].append((w, leg_d(name, days)))
    books = {f: combine(legs) for f, legs in fam.items()}
    scale = {f: TARGET / volf[f] for f in fam}
    portfolio = combine([(scale[f], books[f]) for f in fam])
    sq = {}
    combine([(scale[f] * w, leg) for f in fam for w, leg in fam[f]], rss=sq)
    port_mid = {d: (p, min(0.0, p) - math.sqrt(sq.get(d, 0.0)), h) for d, (p, l, h) in portfolio.items()}
    port_close = {d: (p, min(0.0, p), max(0.0, p)) for d, (p, l, h) in portfolio.items()}
    fa = combine([(scale["A"], books["A"])])
    fb = combine([(scale["B"], books["B"])])
    x = np.array([v[0] for v in portfolio.values()])
    lows = np.array([v[1] for v in portfolio.values()])
    res = {"path_check": {"days": len(x), "sharpe": float(x.mean() / x.std() * math.sqrt(252)), "ann_vol_pct": float(x.std() * math.sqrt(252) * 100),
                          "mean_low_minus_close_bps": float((lows - x).mean() * 1e4), "worst_low_pct_at_1x": float(lows.min() * 100)}}
    print(res["path_check"], flush=True)
    policies = {f"fixed {L:g}x": (L, None) for L in (1, 2, 3, 4)}
    for k in (10, 20):
        policies[f"CPPI k={k} cap=4x"] = (1.0, (lambda a, k=k: max(0.0, min(4.0, k * a.cushion()))))
    for name, bk in (("portfolio_pessimistic_sum_of_worst", portfolio), ("portfolio_middle_independent_excursions", port_mid),
                     ("portfolio_optimistic_close_only", port_close), ("family_A", fa), ("family_B", fb)):
        real, zero = to_days(bk), to_days(demean(bk))
        res[name] = {}
        for preset, guard in (("ftmo_2step_100k.json", 0.03), ("ftmo_1step_100k.json", 0.02)):
            res[name][preset] = {}
            for pol, (sc, sz) in policies.items():
                a = evaluate(real, preset, guard, sc, sz)
                z = evaluate(zero, preset, guard, sc, sz)
                a["zero_edge_ev_per_attempt_usd"], a["zero_edge_p_pass"] = z["ev_per_attempt_usd"], z["p_pass"]
                a["edge_value_usd"] = a["ev_per_attempt_usd"] - z["ev_per_attempt_usd"]
                res[name][preset][pol] = a
                print(name, preset, pol, {k: round(v, 3) for k, v in a.items() if k in ("p_pass", "zero_edge_p_pass", "ev_per_attempt_usd", "edge_value_usd",
                                                                                      "mean_months", "ev_per_account_month_usd")}, flush=True)
    json.dump(res, open(os.path.join(OUT, "prop_portfolio.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
