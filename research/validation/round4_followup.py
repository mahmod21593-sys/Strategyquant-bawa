"""Post-hoc follow-up to round 4 (not pre-registered; reported as such in REPORT.md §15).

1. Robustness of S2 (Treasury end of month): window length, last day alone, duration dose-response, years.
2. Prop books on 2014-2025: MR-06 (volatility-scaled, US500, 15:55 entry), S2 on a Treasury future proxy
   (IEF excess return), and both combined; two-step CFD rules and a futures 50K trailing-drawdown account.
-> results/round4_followup.json
"""
from __future__ import annotations

import json
import os
import random
import sys
from datetime import date, timedelta

import vstats as vs
from data_histdata import price, table
from data_yahoo import daily
from run_round4 import irx_map, month_ends, tbill

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools", "propsim"))
from propsim.engine import Day, run_challenge  # noqa: E402
from propsim.rules import load_rules  # noqa: E402
from propsim.sampling import stationary_bootstrap  # noqa: E402

R = os.path.join(os.path.dirname(__file__), "results")
PRESETS = os.path.join(os.path.dirname(__file__), "..", "..", "tools", "propsim", "presets")
BPS = 1e4


def f(x):
    return {"n": len(x), "mean_bps": round(vs.mean(x), 2), "t": round(vs.nw_t(x, 5), 2),
            "share_positive": round(sum(v > 0 for v in x) / len(x), 3) if x else None}


def eom_window(sym, t, start, end, last_only=False):
    rows = daily(sym)
    rates = irx_map()
    keys = sorted(rates)
    out = []
    for e in month_ends(rows):
        d = rows[e]["date"]
        if not (start <= d <= end):
            continue
        s = e - (1 if last_only else t)
        stop = e
        ex = rows[stop]["adj"] / rows[s]["adj"] - 1 - tbill(rates, keys, rows[s]["date"], rows[stop]["date"])
        out.append((d, ex * BPS))
    return out


def s2_robustness():
    res = {}
    for label, a, b in (("2002_2018", date(2002, 8, 1), date(2018, 12, 31)), ("2019_on", date(2019, 1, 1), date(2026, 12, 31))):
        res[label] = {f"IEF_last_{t}": f([x for _, x in eom_window("IEF", t, a, b)]) for t in (1, 2, 3, 4, 5)}
        res[label]["IEF_last_day_only"] = f([x for _, x in eom_window("IEF", 1, a, b, last_only=True)])
        for sym in ("SHY", "IEF", "TLT"):
            res[label][f"{sym}_last_3"] = f([x for _, x in eom_window(sym, 3, a, b)])
    yr = {}
    for d, x in eom_window("IEF", 3, date(2002, 8, 1), date(2026, 12, 31)):
        yr.setdefault(d.year, []).append(x)
    res["IEF_last_3_per_year_mean_bps"] = {y: round(vs.mean(v), 1) for y, v in sorted(yr.items())}
    res["IEF_last_3_years_positive"] = f"{sum(vs.mean(v) > 0 for v in yr.values())} of {len(yr)}"
    return res


# ---------------------------------------------------------------- books

def mr06_days():
    """MR-06 US500 trades keyed by exit date (pnl, low, high as fractions at 1x), volatility-scaled (I1 rule)."""
    import prop_mr06_minute as pm
    from implementability import rate_map
    from run_histdata import RTH, us_days
    rates = rate_map()
    tr = pm.trades("SPXUSD", rates, sorted(rates))
    tab = table("SPXUSD", range(2014, 2026), RTH)
    days = us_days(tab)
    close = {d: price(tab, d, 960) for d in days}
    ret = {b: close[b] / close[a] - 1 for a, b in zip(days, days[1:]) if close[a] and close[b]}
    prev_of = {b: a for a, b in zip(days, days[1:])}
    size = {}
    for d in tr:
        i = days.index(prev_of[d])
        hist = [ret[x] for x in days[max(1, i - 20):i] if x in ret]
        size[d] = min(2.0, 0.01 / vs.sd(hist)) if len(hist) >= 10 else 1.0
    k = 1 / vs.mean(list(size.values()))
    return {d: tuple(v * size[d] * k for v in tr[d]) for d in tr}


def s2_days(start=date(2014, 1, 1), end=date(2025, 12, 31)):
    """S2 on a Treasury-future proxy: IEF daily excess returns on the last 3 trading days, intraday path from the
    daily high/low, 2 bps cost on the first day."""
    rows = daily("IEF")
    rates = irx_map()
    keys = sorted(rates)
    out = {}
    for e in month_ends(rows):
        if not (start <= rows[e]["date"] <= end):
            continue
        for j, i in enumerate(range(e - 2, e + 1)):
            a, b = rows[i - 1], rows[i]
            rf = tbill(rates, keys, a["date"], b["date"])
            r = b["adj"] / a["adj"] - 1 - rf
            lo, hi = b["l"] / a["c"] - 1 - rf, b["h"] / a["c"] - 1 - rf
            c = 2e-4 if j == 0 else 0.0
            out[b["date"]] = (r - c, min(lo, 0.0) - c, max(hi, 0.0))
    return out


def combine(legs, weights):
    book = {}
    for leg, w in zip(legs, weights):
        for d, v in leg.items():
            b = book.setdefault(d, [0.0, 0.0, 0.0])
            for i in range(3):
                b[i] += w * v[i]
    return book


def simulate(book, preset, guard, n=1500):
    d0, d1 = min(book), max(book)
    days, d = [], d0
    while d <= d1:
        if d.weekday() < 5:
            days.append(Day(d, *book[d], traded=True, n_trades=1) if d in book else Day(d))
        d += timedelta(days=1)
    rules = load_rules(os.path.join(PRESETS, preset))
    rules.funded = None
    rng = random.Random(7)
    outs = [run_challenge(stationary_bootstrap(days, rng, 5.0, 2520), rules, 1.0, daily_guard=guard, guard_slippage=0.0025)
            for _ in range(n)]
    dec = [o for o in outs if o.decided]
    passed = sorted(o.days_to_pass for o in dec if o.passed_all)
    pnl = [book[k][0] * BPS for k in sorted(book)]
    return {"p_pass": round(len(passed) / len(dec), 3) if dec else None, "median_days": passed[len(passed) // 2] if passed else None,
            "trade_days_per_year": round(len(book) / ((d1 - d0).days / 365.25), 1), "mean_bps_per_trade_day": round(vs.mean(pnl), 2)}


def books():
    mr, s2 = mr06_days(), s2_days()
    both = set(mr) & set(s2)
    corr_days = sorted(both)
    out = {"overlap_days": len(corr_days)}
    grid = {"MR-06 x2": ([mr], [2.0]), "S2 x4": ([s2], [4.0]), "S2 x8": ([s2], [8.0]),
            "MR-06 x2 + S2 x4": ([mr, s2], [2.0, 4.0]), "MR-06 x2 + S2 x8": ([mr, s2], [2.0, 8.0]),
            "MR-06 x1 + S2 x4": ([mr, s2], [1.0, 4.0])}
    for preset, guard in (("two_step_10_5.json", 0.03), ("futures_50k_eod_trailing.json", 0.02)):
        out[preset] = {name: simulate(combine(l, w), preset, guard) for name, (l, w) in grid.items()}
    return out


def zero_edge():
    """Base rate: the S2 book with its mean removed (same costs, path shape and guard)."""
    s2 = s2_days()
    m = vs.mean([v[0] for v in s2.values()])
    zero = {d: (v[0] - m, v[1] - m, v[2] - m) for d, v in s2.items()}
    return {preset: {f"x{w:g}": simulate(combine([zero], [w]), preset, guard) for w in (4.0, 8.0)}
            for preset, guard in (("two_step_10_5.json", 0.03), ("futures_50k_eod_trailing.json", 0.02))}


def main():
    res = {"s2_robustness": s2_robustness(), "prop_books_2014_2025": books(), "zero_edge_base_rates": zero_edge()}
    json.dump(res, open(os.path.join(R, "round4_followup.json"), "w"), indent=1, default=str)
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
