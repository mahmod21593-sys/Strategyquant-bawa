"""Post hoc checks of round 19's GT result: breadth across the JPY crosses, a non-JPY placebo, and a second data feed
(Yahoo USDJPY=X 5-min and 60-min bars against HistData on the same days). Labelled post hoc in REPORT.md.

    python3 gt_breadth.py   -> results/round19_gt_breadth.json
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import date, datetime, timedelta, timezone

import numpy as np

import vstats as vs
from data_calendar import gotobi_days, japan_holidays
from data_minutes import local, price_at
from run_round11 import TOKYO

OUT = os.path.join(os.path.dirname(__file__), "results")
START, END = date(2014, 1, 1), date(2026, 9, 18)
E = date(1970, 1, 1).toordinal()
CACHE = os.environ.get("YAHOO_CACHE", "/tmp/yahoo_cache")


def window(sym, a, b, sgn):
    t, x = local(sym, range(2008, 2027), TOKYO)
    day, mod = t // 1440, t % 1440
    pa, pb = price_at(day, mod, x, a), price_at(day, mod, x, b)
    hol = japan_holidays()
    out = {}
    for k, p0 in pa.items():
        d = date.fromordinal(int(k) + E)
        if k in pb and d.weekday() < 5 and d not in hol and START <= d <= END:
            out[d] = sgn * (pb[k] / p0 - 1)
    return out


def stats(v):
    x = np.array(v)
    return {"n": int(len(x)), "gross_bps": float(x.mean() * 1e4), "t": vs.nw_t(list(x), 5)}


def yahoo(interval, rng):
    path = os.path.join(CACHE, f"yahoo_USDJPY_{interval}_{rng}.json")
    if not os.path.exists(path):
        r = subprocess.run(["curl", "-sS", "-m", "60", "-A", "Mozilla/5.0",
                            f"https://query1.finance.yahoo.com/v8/finance/chart/USDJPY=X?interval={interval}&range={rng}"], capture_output=True, text=True)
        open(path, "w").write(r.stdout)
    d = json.load(open(path))["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    return [(datetime.fromtimestamp(ts, timezone.utc), o, c) for ts, o, c in zip(d["timestamp"], q["open"], q["close"]) if o and c]


def main():
    got = gotobi_days()
    res = {"breadth_post_09:55_10:55_short": {}, "placebo_non_jpy": {}}
    for sym in ("USDJPY", "EURJPY", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY", "NZDJPY"):
        w = window(sym, 595, 655, -1)
        res["breadth_post_09:55_10:55_short"][sym] = {"gotobi": stats([v for d, v in w.items() if d in got]),
                                                      "other": stats([v for d, v in w.items() if d not in got])}
        print(sym, res["breadth_post_09:55_10:55_short"][sym], flush=True)
    # non-JPY pairs: long the pair 09:55 -> 10:55 (positive = the pair rose; for XXXUSD that is USD weakening)
    for sym in ("EURUSD", "GBPUSD", "AUDUSD", "USDCHF", "USDCAD"):
        w = window(sym, 595, 655, 1)
        res["placebo_non_jpy"][sym] = {"gotobi": stats([v for d, v in w.items() if d in got]), "other": stats([v for d, v in w.items() if d not in got])}
        print(sym, res["placebo_non_jpy"][sym], flush=True)
    # second feed: Yahoo 5-min (last 60 days) and 60-min (730 days) against HistData
    jst = timedelta(hours=9)
    hd = {m: None for m in (540, 595, 600, 655, 660)}
    t, x = local("USDJPY", range(2023, 2027), TOKYO)
    day, mod = t // 1440, t % 1440
    for m in hd:
        hd[m] = {date.fromordinal(int(k) + E): v for k, v in price_at(day, mod, x, m, prefer_open=True).items()}
    y5 = {}
    for ts, o, c in yahoo("5m", "60d"):
        lt = ts + jst
        y5[(lt.date(), lt.hour * 60 + lt.minute)] = o
    both = [d for d in hd[595] if (d, 595) in y5 and (d, 655) in y5 and d in hd[655]]
    a = np.array([hd[595][d] / hd[655][d] - 1 for d in both])
    b = np.array([y5[(d, 595)] / y5[(d, 655)] - 1 for d in both])
    res["second_feed_5m"] = {"days": len(both), "corr_post_window": float(np.corrcoef(a, b)[0, 1]) if len(both) > 5 else None,
                             "mean_abs_diff_bps": float(np.abs(a - b).mean() * 1e4) if len(both) else None}
    y60 = {}
    for ts, o, c in yahoo("60m", "730d"):
        lt = ts + jst
        y60[(lt.date(), lt.hour)] = (o, c)
    # the 10:00-11:00 JST hourly bar, short, against HistData 10:00 -> 11:00
    both = [d for d in hd[600] if (d, 10) in y60 and d in hd[660] and d.weekday() < 5]
    a = np.array([hd[600][d] / hd[660][d] - 1 for d in both])
    b = np.array([y60[(d, 10)][0] / y60[(d, 10)][1] - 1 for d in both])
    g = np.array([d in got for d in both])
    res["second_feed_60m_10_11_short"] = {"days": len(both), "corr": float(np.corrcoef(a, b)[0, 1]),
                                          "gotobi_mean_bps_histdata": float(a[g].mean() * 1e4), "gotobi_mean_bps_yahoo": float(b[g].mean() * 1e4),
                                          "other_mean_bps_histdata": float(a[~g].mean() * 1e4), "other_mean_bps_yahoo": float(b[~g].mean() * 1e4),
                                          "n_gotobi": int(g.sum())}
    # the 09:00-10:00 JST hourly bar (PRE + fix + first 5 minutes), long
    both = [d for d in hd[540] if (d, 9) in y60 and d in hd[600] and d.weekday() < 5]
    a = np.array([hd[600][d] / hd[540][d] - 1 for d in both])
    b = np.array([y60[(d, 9)][1] / y60[(d, 9)][0] - 1 for d in both])
    g = np.array([d in got for d in both])
    res["second_feed_60m_09_10_long"] = {"days": len(both), "corr": float(np.corrcoef(a, b)[0, 1]),
                                         "gotobi_mean_bps_histdata": float(a[g].mean() * 1e4), "gotobi_mean_bps_yahoo": float(b[g].mean() * 1e4),
                                         "n_gotobi": int(g.sum())}
    print(json.dumps({k: res[k] for k in ("second_feed_5m", "second_feed_60m_10_11_short", "second_feed_60m_09_10_long")}, indent=1))
    json.dump(res, open(os.path.join(OUT, "round19_gt_breadth.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
