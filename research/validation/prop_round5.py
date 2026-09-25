"""I3 (PREREGISTRATION.md A9): prop books without Treasury strategies.

MR-06 (three down closes, entry 5 minutes before the cash close, exit at the next close, volatility-scaled size)
on US500, JP225 and AUS200; alone and combined; two-step, one-step and futures rule sets, each with a zero-edge
base rate. Also the JP225 split at the end of the Bank of Japan's ETF purchases (March 2024).
-> results/prop_round5.json
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import vstats as vs
from data_histdata import NY, available_years, bars30, price, table
from round4_followup import combine, mr06_days, simulate
from run_round5 import ASIA_KEEP, ny_min

R = os.path.join(os.path.dirname(__file__), "results")
BPS = 1e4
TKY, SYD = ZoneInfo("Asia/Tokyo"), ZoneInfo("Australia/Sydney")
# long-index CFD financing per night: local cash rate (approximation: JPY 0%, AUD 2.5% average) + 2.5% markup, act/360
SWAP = {"JPXJPY": 0.025 / 360, "AUXAUD": 0.05 / 360}
COST = {"JPXJPY": 3e-4, "AUXAUD": 3e-4}


def asia_trades(sym, tz, close_fn):
    """MR-06 trades keyed by exit date: (pnl, low, high) as fractions at 1x, volatility-scaled; path from 30-min bars."""
    yrs = available_years(sym, range(2010, 2026))
    tab = table(sym, yrs, ASIA_KEEP)
    b30 = bars30(sym, yrs)
    starts = {}
    for (d, i), v in b30.items():
        starts[datetime(d.year, d.month, d.day, i // 2, 30 * (i % 2), tzinfo=NY)] = v
    keys = sorted(starts)
    days = []
    d = date(2011, 1, 1)
    while d <= date(2025, 12, 31):
        if d.weekday() < 5:
            h, m = close_fn(d)
            ct = datetime(d.year, d.month, d.day, h, m, tzinfo=tz)
            c = price(tab, *ny_min(ct))
            e = price(tab, *ny_min(ct - timedelta(minutes=5)))
            if c and e:
                days.append((d, ct, c, e))
        d += timedelta(days=1)
    rets = {days[i][0]: days[i][2] / days[i - 1][2] - 1 for i in range(1, len(days))}
    out, sigdays = {}, []
    import bisect
    for i in range(20, len(days) - 1):
        d, ct, c, e = days[i]
        if not (e < days[i - 1][2] < days[i - 2][2] < days[i - 3][2]):
            continue
        nd, nct, nc, _ = days[i + 1]
        lo_i, hi_i = bisect.bisect_left(keys, ct.astimezone(NY)), bisect.bisect_left(keys, nct.astimezone(NY))
        path = [starts[k] for k in keys[lo_i:hi_i]]
        if not path:
            continue
        lo, hi = min(p[2] for p in path) / e - 1, max(p[1] for p in path) / e - 1
        nights = (nd - d).days
        cost = COST[sym] + SWAP[sym] * nights
        hist = [rets[x[0]] for x in days[i - 20:i] if x[0] in rets]
        size = min(2.0, 0.01 / vs.sd(hist)) if len(hist) >= 10 else 1.0
        out[nd] = (size, nc / e - 1 - cost, min(lo, 0.0) - cost, max(hi, 0.0))
        sigdays.append(d)
    k = 1 / vs.mean([v[0] for v in out.values()])
    scaled = {d: tuple(x * v[0] * k for x in v[1:]) for d, v in out.items()}
    return scaled, sigdays


def main():
    us = mr06_days()
    jp, jp_sig = asia_trades("JPXJPY", TKY, lambda d: (15, 30) if d >= date(2024, 11, 5) else (15, 0))
    au, au_sig = asia_trades("AUXAUD", SYD, lambda d: (16, 0))
    res = {}
    boj = [(d, v[0] * BPS) for d, v in jp.items()]
    res["jp225_boj_split"] = {"2011_to_2024_03": vs.summarize([d for d, _ in boj if d < date(2024, 4, 1)], [x for d, x in boj if d < date(2024, 4, 1)], 1, 5, 0.0, boot=False),
                              "2024_04_on": vs.summarize([d for d, _ in boj if d >= date(2024, 4, 1)], [x for d, x in boj if d >= date(2024, 4, 1)], 1, 5, 0.0, boot=False)}
    jp = {d: v for d, v in jp.items() if d >= date(2014, 1, 1)}  # same span as the US500 minute data
    au = {d: v for d, v in au.items() if d >= date(2014, 1, 1)}
    books = {"US500 x2": ([us], [2.0]), "JP225 x2": ([jp], [2.0]), "AUS200 x2": ([au], [2.0]),
             "US500+JP225+AUS200 x1 each": ([us, jp, au], [1.0, 1.0, 1.0]), "US500+JP225+AUS200 x1.5 each": ([us, jp, au], [1.5, 1.5, 1.5]),
             "US500+JP225+AUS200 x2 each": ([us, jp, au], [2.0, 2.0, 2.0])}
    res["trades_per_year_2014_2025"] = {name: round(len(b) / 12, 1) for name, b in (("US500", us), ("JP225", jp), ("AUS200", au))}
    res["overlap_exit_days"] = {"US500&JP225": len(set(us) & set(jp)), "US500&AUS200": len(set(us) & set(au)), "JP225&AUS200": len(set(jp) & set(au))}
    presets = (("two_step_10_5.json", 0.03), ("one_step_10_trailing.json", 0.02), ("futures_50k_eod_trailing.json", 0.02))
    for preset, guard in presets:
        res[preset] = {name: simulate(combine(l, w), preset, guard) for name, (l, w) in books.items()}
        comb = combine([us, jp, au], [1.5, 1.5, 1.5])
        m = vs.mean([v[0] for v in comb.values()])
        zero = {d: (v[0] - m, v[1] - m, v[2] - m) for d, v in comb.items()}
        res[preset]["zero_edge (combined book x1.5, demeaned)"] = simulate(zero, preset, guard)
    json.dump(res, open(os.path.join(R, "prop_round5.json"), "w"), indent=1, default=str)
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
