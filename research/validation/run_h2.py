"""A19 H2: earnings-announcement premium in large US stocks (stock CFDs). -> results/h2.json"""
from __future__ import annotations

import bisect
import json
import math
import os
from datetime import date, timedelta

import vstats as vs
from data_edgar import earnings_filings
from data_histdata import NY
from data_yahoo import daily
from run_round4 import irx_map, tbill

OUT = os.path.join(os.path.dirname(__file__), "results")
BPS = 1e4
UNIVERSE = {"AAPL": [320193], "XOM": [34088], "GOOGL": [1288776, 1652044], "MSFT": [789019], "GE": [40545], "JNJ": [200406],
            "WMT": [104169], "CVX": [93410], "WFC": [72971], "JPM": [19617], "PG": [80424], "PFE": [78003], "IBM": [51143],
            "T": [732717], "KO": [21344], "AMZN": [1018724], "ORCL": [777676, 1341439], "BAC": [70858], "VZ": [732712]}
COST = 6.5
DEDUP_DAYS = 45  # at most one event per stock per 45 days (quarterly releases; later 2.02 filings are usually amendments or extra data)


def reaction_day(ts_utc, days):
    """First trading day whose close reflects a release accepted at ts_utc."""
    loc = ts_utc.astimezone(NY)
    d = loc.date()
    if loc.hour * 60 + loc.minute >= 16 * 60:
        d += timedelta(days=1)
    i = bisect.bisect_left(days, d)
    return days[i] if i < len(days) else None


def main():
    spy = {r["date"]: r["adj"] for r in daily("SPY")}
    rates = irx_map()
    rk = sorted(rates)
    windows = {"primary_E-2_to_E": (-2, 0), "pre_E-6_to_E-1": (-6, -1), "day_E": (-1, 0), "post_E_to_E+5": (0, 5)}
    ev = {w: {} for w in windows}
    raw = {}
    per_stock = {}
    counts = {}
    for tic, ciks in UNIVERSE.items():
        px = {r["date"]: r["adj"] for r in daily(tic)}
        days = sorted(d for d in px if d in spy)
        idx = {d: i for i, d in enumerate(days)}
        stamps = sorted(t for c in ciks for t in earnings_filings(c))
        events, last = [], None
        for t in stamps:
            e = reaction_day(t, days)
            if e is None or (last and (e - last).days < DEDUP_DAYS):
                continue
            events.append(e)
            last = e
        counts[tic] = len(events)
        for e in events:
            i = idx[e]
            for w, (a, b) in windows.items():
                if i + a < 0 or i + b >= len(days):
                    continue
                d0, d1 = days[i + a], days[i + b]
                x = ((px[d1] / px[d0]) - (spy[d1] / spy[d0])) * BPS
                ev[w].setdefault(e, []).append(x)
                if w == "primary_E-2_to_E":
                    per_stock.setdefault(tic, []).append((e, x))
                    raw.setdefault(e, []).append((px[d1] / px[d0] - 1 - tbill(rates, rk, d0, d1)) * BPS)
    res = {"events_per_stock": counts}
    for w in windows:
        ds = sorted(ev[w])
        xs = [vs.mean(ev[w][d]) for d in ds]
        for label, lo, hi in (("2014_2026", date(2014, 1, 1), date(2026, 8, 31)), ("2005_2013", date(2005, 1, 1), date(2013, 12, 31))):
            sel = [(d, x) for d, x in zip(ds, xs) if lo <= d <= hi]
            r = vs.summarize([d for d, _ in sel], [x for _, x in sel], 1, 5, COST, boot=(w == "primary_E-2_to_E" and label == "2014_2026"))
            res.setdefault(w, {})[label] = r
    p = res["primary_E-2_to_E"]["2014_2026"]
    ds = sorted(raw)
    sel = [(d, vs.mean(raw[d])) for d in ds if date(2014, 1, 1) <= d <= date(2026, 8, 31)]
    res["unhedged_excess_2014_2026"] = vs.summarize([d for d, _ in sel], [x for _, x in sel], 1, 5, 5.0, boot=False)
    res["per_stock_2014_2026"] = {t: vs.summarize([d for d, _ in v if d.year >= 2014], [x for d, x in v if d.year >= 2014], 1, 5, COST, boot=False)
                                  for t, v in per_stock.items()}
    yr = {}
    for d in sorted(ev["primary_E-2_to_E"]):
        yr.setdefault(d.year, []).extend(ev["primary_E-2_to_E"][d])
    res["per_year_mean_bps"] = {y: round(vs.mean(v), 1) for y, v in sorted(yr.items())}
    sel_all = [(d, vs.mean(ev["primary_E-2_to_E"][d])) for d in sorted(ev["primary_E-2_to_E"]) if date(2014, 1, 1) <= d <= date(2026, 8, 31)]
    res["dsr_N746"] = vs.deflated_sharpe([x - COST for _, x in sel_all], 746)
    ok = p["p_one_sided"] < 0.05 and p["net_mean_bps"] > 0 and res["primary_E-2_to_E"]["2005_2013"].get("mean_bps", -1) > 0
    res["verdict"] = "CONFIRMED" if ok else "WEAK" if p["p_one_sided"] < 0.05 else "NOT CONFIRMED"
    print("events", counts)
    for w in windows:
        a, b = res[w]["2014_2026"], res[w]["2005_2013"]
        print(f"{w:18s} 2014-26 n={a['n']} mean={a['mean_bps']:.1f} net={a['net_mean_bps']:.1f} t={a['t_hac']:.2f} p={a['p_one_sided']:.4f} | 2005-13 mean={b['mean_bps']:.1f} t={b['t_hac']:.2f}")
    print("verdict", res["verdict"], "dsr", round(res["dsr_N746"], 3), "unhedged", round(res["unhedged_excess_2014_2026"]["mean_bps"], 1))
    json.dump(res, open(os.path.join(OUT, "h2.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
