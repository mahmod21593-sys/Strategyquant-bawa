"""Round 34 (PREREGISTRATION.md A48, A48a): the N3 momentum rule on US30 and US2000 from the independent Dukascopy
feed, on hourly candles (HN3), after a calibration gate on HistData US100.

    python3 run_round34.py CAL   calibration gate: HN3 vs minute-exact native N3 on HistData US100 -> results/round34_calibration.json
    python3 run_round34.py DIAG  post hoc: why the gate failed (09:30 vs 10:00 session start)      -> results/round34_diagnostic.json
    python3 run_round34.py RUN   the breadth test on Dukascopy US30 / US2000 (+ US100 second feed)  -> results/round34_n3_breadth.json
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date

import numpy as np

import run_family_a as fa
import vstats as vs
from data_histdata import NY
from data_minutes import local as hlocal

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 13986
E = date(1970, 1, 1).toordinal()
END = date(2026, 9, 18)
ZERO_DTE = date(2022, 11, 14)
HN3_VARIANTS = [f"{b}|k{kk}" for b in ("range", "atr14") for kk in (0.3, 0.5, 0.7)]
PRIMARY = "range|k0.5"


def to_hourly(t, x):
    """Resample minute bars (local minutes, OHLC) to hour bars keyed by the hour's start minute."""
    hk = t // 60
    st = np.r_[0, np.nonzero(np.diff(hk))[0] + 1]
    en = np.r_[st[1:], len(hk)]
    th = hk[st] * 60
    xh = np.stack([x[st, 0], np.maximum.reduceat(x[:, 1], st), np.minimum.reduceat(x[:, 2], st), x[en - 1, 3]], 1)
    return th, xh


def hn3(th, xh, cost_bps):
    """{variant: {date: net pnl}} for the hourly adaptation (A48a). th: local minutes at hour-bar starts."""
    day, hour = th // 1440, (th % 1440) // 60
    sess = {}
    for i in np.nonzero((hour >= 10) & (hour <= 15))[0]:
        sess.setdefault(int(day[i]), {})[int(hour[i])] = xh[i]
    days = sorted(k for k, v in sess.items() if len(v) == 6 and date.fromordinal(k + E).weekday() < 5)
    out = {v: {} for v in HN3_VARIANTS}
    ranges = []
    prev = None
    for k in days:
        bars = [sess[k][h] for h in range(10, 16)]
        hi, lo = max(b[1] for b in bars), min(b[2] for b in bars)
        if prev is not None and k - prev <= 5:
            d = date.fromordinal(k + E)
            pr = ranges[-1]
            atr = float(np.mean(ranges[-14:])) if len(ranges) >= 14 else None
            o0, close = bars[0][0], bars[-1][3]
            for base, w in (("range", pr), ("atr14", atr)):
                if not w:
                    continue
                for kk in (0.3, 0.5, 0.7):
                    U, D = o0 + kk * w, o0 - kk * w
                    pnl = 0.0
                    for b in bars:
                        up, dn = b[1] >= U, b[2] <= D
                        if not (up or dn):
                            continue
                        long_r = close / max(U, b[0]) - 1
                        short_r = -(close / min(D, b[0]) - 1)
                        pnl = min(long_r, short_r) if (up and dn) else long_r if up else short_r
                        pnl -= cost_bps / 1e4
                        break
                    if d <= END:
                        out[f"{base}|k{kk}"][d] = pnl
        ranges.append(hi - lo)
        prev = k
    return out


def summary(rows):
    ds = sorted(rows)
    v = np.array([rows[d] for d in ds])
    mid = ds[len(ds) // 2]
    t = vs.nw_t(list(v), 5)
    post = [rows[d] for d in ds if d >= ZERO_DTE]
    return {"n": len(v), "first": str(ds[0]), "last": str(ds[-1]), "mean_bps": float(v.mean() * 1e4), "t_hac": t, "p_one_sided": vs.p_one_sided(t),
            "sharpe": float(v.mean() / v.std(ddof=1) * math.sqrt(252)),
            "halves_bps": (float(np.mean([rows[d] for d in ds if d < mid]) * 1e4), float(np.mean([rows[d] for d in ds if d >= mid]) * 1e4)),
            "split_date": str(mid), "post_0dte_bps": float(np.mean(post) * 1e4) if post else None}


def calibration():
    from run_round34_minute import r3_grid  # minute-exact native rule (round 11 R3 logic)
    t, x = hlocal("NSXUSD", range(2013, 2027), NY)
    minute = r3_grid(t, x, 1.5)["range|k0.5|flat"]
    th, xh = to_hourly(t, x)
    hourly = hn3(th, xh, 1.5)[PRIMARY]
    common = sorted(d for d in set(minute) & set(hourly) if date(2014, 1, 1) <= d <= date(2026, 8, 31))
    a = np.array([minute[d][0] for d in common])
    b = np.array([hourly[d] for d in common])
    res = {"common_days": len(common), "corr": float(np.corrcoef(a, b)[0, 1]),
           "minute_mean_bps": float(a.mean() * 1e4), "minute_t": vs.nw_t(list(a), 5),
           "hourly_mean_bps": float(b.mean() * 1e4), "hourly_t": vs.nw_t(list(b), 5)}
    res["gate_passed"] = bool(res["corr"] >= 0.60 and res["hourly_mean_bps"] > 0)
    json.dump(res, open(os.path.join(OUT, "round34_calibration.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


def diagnostic():
    """Post hoc (not a test): why the gate failed. The minute-exact rule started at 10:00 separates the bar-size effect
    from the session-start effect."""
    from run_round34_minute import r3_grid
    t, x = hlocal("NSXUSD", range(2013, 2027), NY)
    g = {s: r3_grid(t, x, 1.5, s)["range|k0.5|flat"] for s in (570, 600)}
    h = hn3(*to_hourly(t, x), 1.5)[PRIMARY]
    common = sorted(d for d in set(g[570]) & set(g[600]) & set(h) if date(2014, 1, 1) <= d <= date(2026, 8, 31))
    a, b, c = (np.array([g[570][d][0] for d in common]), np.array([g[600][d][0] for d in common]), np.array([h[d] for d in common]))
    res = {"verdict": "UNTESTABLE WITH HOURLY DATA", "common_days": len(common),
           "mean_bps_t": {"minute_from_0930": [float(a.mean() * 1e4), vs.nw_t(list(a), 5)], "minute_from_1000": [float(b.mean() * 1e4), vs.nw_t(list(b), 5)],
                          "hourly_from_1000": [float(c.mean() * 1e4), vs.nw_t(list(c), 5)]},
           "corr": {"minute0930_vs_minute1000": float(np.corrcoef(a, b)[0, 1]), "minute1000_vs_hourly": float(np.corrcoef(b, c)[0, 1]),
                    "minute0930_vs_hourly": float(np.corrcoef(a, c)[0, 1])}}
    json.dump(res, open(os.path.join(OUT, "round34_diagnostic.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


def run():
    from data_duka_minutes import hours_local
    from run_round24 import to_battery
    cal = json.load(open(os.path.join(OUT, "round34_calibration.json")))
    res = {"calibration": cal}
    grids = {}
    for lab, sym, cost in (("US30", "USA30IDXUSD", 1.5), ("US2000", "USSC2000IDXUSD", 3.0), ("US100_duka", "USATECHIDXUSD", 1.5)):
        th, xh = hours_local(sym, range(2012, 2027), NY)
        if len(th) == 0:
            continue
        grids[lab] = hn3(th, xh, cost)
        print("HN3", lab, len(grids[lab][PRIMARY]), flush=True)
    if not cal["gate_passed"]:
        res["verdict"] = "UNTESTABLE WITH HOURLY DATA"
    else:
        prim = {"B1": summary(grids["US30"][PRIMARY]), "B2": summary(grids["US2000"][PRIMARY])}
        holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
        for k in prim:
            prim[k]["p_holm"] = holm[k]
        ok = {k: prim[k]["p_holm"] < 0.05 and all(h > 0 for h in prim[k]["halves_bps"]) for k in prim}
        res["primary"] = prim
        res["verdict"] = "BREADTH CONFIRMED" if all(ok.values()) else "PARTIAL" if any(ok.values()) else "NOT CONFIRMED"
    res["grid"] = {lab: {v: summary(g[v]) for v in HN3_VARIANTS if g[v]} for lab, g in grids.items()}
    res["share_variants_positive"] = {lab: float(np.mean([s["mean_bps"] > 0 for s in d.values()])) for lab, d in res["grid"].items()}
    if "US100_duka" in grids:
        th, xh = to_hourly(*hlocal("NSXUSD", range(2013, 2027), NY))
        hd = hn3(th, xh, 1.5)[PRIMARY]
        dk = grids["US100_duka"][PRIMARY]
        common = sorted(set(hd) & set(dk))
        va, vb = np.array([dk[d] for d in common]), np.array([hd[d] for d in common])
        res["second_feed_US100_hourly"] = {"common_days": len(common), "corr": float(np.corrcoef(va, vb)[0, 1]),
                                           "mean_bps_duka": float(va.mean() * 1e4), "mean_bps_histdata": float(vb.mean() * 1e4)}
    per = {f"{lab}|{v}": grids[lab][v] for lab in ("US30", "US2000") if lab in grids for v in HN3_VARIANTS}
    alld = sorted(set(d for r in per.values() for d in r))
    res["battery"] = to_battery(per, "HN3", alld[0], alld[len(alld) // 2], alld[0].year + 3)
    json.dump(res, open(os.path.join(OUT, "round34_n3_breadth.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in res if k not in ("grid", "battery")}, indent=1, default=str))
    for lab, d in res["grid"].items():
        print(lab, {v: (round(s["mean_bps"], 2), round(s["t_hac"], 2), s["n"]) for v, s in d.items()})


if __name__ == "__main__":
    {"CAL": calibration, "DIAG": diagnostic, "RUN": run}[sys.argv[1]]()
