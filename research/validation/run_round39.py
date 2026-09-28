"""Round 39 (PREREGISTRATION.md A53): volume-conditioned reversal / continuation (Campbell, Grossman & Wang 1993) on FX majors,
gold and index CFDs; Dukascopy hourly candles with volume, rebuilt into 17:00 New York daily bars (the FTMO MT5 server day).

    python3 run_round39.py   -> results/round39_volume.json
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import time
from datetime import date, datetime, timedelta, timezone

import numpy as np

import run_family_a as fa
import vstats as vs
from data_duka_chart import UA
from data_histdata import NY
from run_round24 import to_battery

OUT = os.path.join(os.path.dirname(__file__), "results")
CACHE = os.environ.get("DUKA_H1_CACHE", "/tmp/duka_h1")
fa.N_TRIALS = 14601
END = date(2026, 9, 18)
# name: (Dukascopy instrument, start, cost per round trip, financing per night, group)
MARKETS = {"EURUSD": ("EUR/USD", 2004, 1.0e-4, 0.5e-4, "FX"), "GBPUSD": ("GBP/USD", 2004, 1.0e-4, 0.5e-4, "FX"),
           "USDJPY": ("USD/JPY", 2004, 1.0e-4, 0.5e-4, "FX"), "AUDUSD": ("AUD/USD", 2004, 1.0e-4, 0.5e-4, "FX"),
           "USDCAD": ("USD/CAD", 2004, 1.0e-4, 0.5e-4, "FX"), "USDCHF": ("USD/CHF", 2004, 1.0e-4, 0.5e-4, "FX"),
           "NZDUSD": ("NZD/USD", 2004, 1.0e-4, 0.5e-4, "FX"), "XAUUSD": ("XAU/USD", 2004, 2.0e-4, 0.5e-4, "GOLD"),
           }  # A53a: index CFDs dropped (Dukascopy index volume unusable)
PRIMARY_REV, PRIMARY_CON = "rev|1.5|h1|f", "con|0.75|h1|f"


def hourly(ins, y0):
    d = os.path.join(CACHE, ins.replace("/", "_").replace(".", ""))
    os.makedirs(d, exist_ok=True)
    ts = int(datetime(y0 - 1, 12, 1, tzinfo=timezone.utc).timestamp() * 1000)
    stop = int(datetime(2026, 9, 20, tzinfo=timezone.utc).timestamp() * 1000)
    parts = []
    while ts < stop:
        p = os.path.join(d, f"{ts}.npy")
        if os.path.exists(p):
            a = np.load(p)
        else:
            u = (f"https://freeserv.dukascopy.com/2.0/?path=chart/json3&instrument={ins}&offer_side=B&interval=1HOUR&splits=true"
                 f"&stocks=true&limit=30000&time_direction=N&timestamp={ts}&jsonp=_cb")
            for _ in range(8):
                s = subprocess.run(["curl", "-sS", "-m", "120", "-A", UA, "-H", "Referer: https://freeserv.dukascopy.com/2.0/?path=chart/index", u],
                                   capture_output=True, text=True).stdout
                try:
                    rows = json.loads(s[s.find("(") + 1:s.rfind(")")])
                    if isinstance(rows, list):
                        break
                except ValueError:
                    pass
                time.sleep(5)
            a = np.array([r for r in rows if r], dtype=float).reshape(-1, 6)
            if len(a):
                np.save(p, a)
        if not len(a):
            ts += 30 * 86_400_000  # A53a: step past gaps instead of stopping
            continue
        parts.append(a)
        ts = int(a[-1, 0]) + 3_600_000
    a = np.concatenate(parts)
    _, i = np.unique(a[:, 0], return_index=True)
    return a[np.sort(i)]


def daily(ins, y0):
    """Daily bars closing 17:00 New York: {date: (O, H, L, C, V, hours)}; filler hours (volume 0, flat) dropped."""
    a = hourly(ins, y0)
    a = a[~((a[:, 5] == 0) & (a[:, 1] == a[:, 4]))]
    bars = {}
    for r in a:
        lt = datetime.fromtimestamp(r[0] / 1000, timezone.utc).astimezone(NY)
        lab = (lt + timedelta(hours=7)).date()
        if lab.weekday() >= 5 or lab.year < y0 or lab > END:
            continue
        b = bars.get(lab)
        if b is None:
            bars[lab] = [r[1], r[2], r[3], r[4], r[5], 1]
        else:
            b[1], b[2], b[3], b[4], b[5] = max(b[1], r[2]), min(b[2], r[3]), r[4], b[4] + r[5], b[5] + 1
    return {d: tuple(v) for d, v in sorted(bars.items()) if v[5] >= 18}


def variants(bars, cost, fin):
    """{variant: {entry date: net pnl}} for both arms; primary names PRIMARY_REV / PRIMARY_CON."""
    ds = sorted(bars)
    c = np.array([bars[d][3] for d in ds])
    v = np.array([bars[d][4] for d in ds])
    r = np.r_[np.nan, c[1:] / c[:-1] - 1]
    out = {}
    for i in range(21, len(ds) - 3):
        sig = float(np.std(r[i - 20:i], ddof=1))
        base = float(np.mean(v[i - 20:i]))
        if not (sig > 0 and base > 0) or not np.isfinite(r[i]) or r[i] == 0:
            continue
        rv = v[i] / base
        for arm, ths, cmp_, sgn in (("rev", (1.25, 1.5, 2.0), lambda x, t: x >= t, -1), ("con", (0.6, 0.75, 0.9), lambda x, t: x <= t, 1)):
            for th in ths:
                if not cmp_(rv, th):
                    continue
                for hold in (1, 3):
                    for filt in ("f", "n"):
                        if filt == "f" and abs(r[i]) < 0.5 * sig:
                            continue
                        side = sgn * np.sign(r[i])
                        pnl = side * (c[i + hold] / c[i] - 1) - cost - fin * hold
                        out.setdefault(f"{arm}|{th}|h{hold}|{filt}", {})[ds[i]] = float(pnl)
    return out


def mech_rows(bars):
    """(date, z_t, z_t1, log RV_t) with returns standardized by the prior 20-day sigma."""
    ds = sorted(bars)
    c = np.array([bars[d][3] for d in ds])
    v = np.array([bars[d][4] for d in ds])
    r = np.r_[np.nan, c[1:] / c[:-1] - 1]
    out = []
    for i in range(21, len(ds) - 1):
        sig, base = float(np.std(r[i - 20:i], ddof=1)), float(np.mean(v[i - 20:i]))
        if sig > 0 and base > 0 and v[i] > 0:
            out.append((ds[i], r[i] / sig, r[i + 1] / sig, math.log(v[i] / base)))
    return out


def stats(x):
    a = np.array(x, dtype=float)
    t = vs.nw_t(list(a), 5)
    return {"n": int(len(a)), "mean_bps": float(a.mean() * 1e4), "t_hac": t, "p_one_sided": vs.p_one_sided(t)}


def portfolio(series, cal):
    ci = {d: i for i, d in enumerate(cal)}
    out = np.zeros(len(cal))
    for s in series:
        for d, v in s.items():
            if d in ci:
                out[ci[d]] += v / len(series)
    return out


def summ(p, cal):
    s = stats(p)
    h = len(p) // 2
    s["halves_bps"] = (float(p[:h].mean() * 1e4), float(p[h:].mean() * 1e4))
    s["split"] = str(cal[h])
    return s


def main():
    from run_round10 import weekday_calendar
    grids, mech = {}, []
    for name, (ins, y0, cost, fin, grp) in MARKETS.items():
        bars = daily(ins, y0)
        grids[name] = variants(bars, cost, fin)
        mech += [(name,) + m for m in mech_rows(bars)]
        print("VOL", name, len(bars), "days;", {k: len(v) for k, v in grids[name].items() if k in (PRIMARY_REV, PRIMARY_CON)}, flush=True)
    fx = [n for n in MARKETS if MARKETS[n][4] == "FX"]
    idx = [n for n in MARKETS if MARKETS[n][4] == "IDX"]
    cal_fx = weekday_calendar(date(2004, 2, 1), END)
    cal_ix = weekday_calendar(date(2013, 2, 1), END)
    prim = {"V1": summ(portfolio([grids[n].get(PRIMARY_REV, {}) for n in fx], cal_fx), cal_fx),
            "V2": summ(portfolio([grids["XAUUSD"].get(PRIMARY_REV, {})], cal_fx), cal_fx),
            "V4": summ(portfolio([grids[n].get(PRIMARY_CON, {}) for n in fx], cal_fx), cal_fx)}
    # V5: CGW slope c in z_{t+1} = a + b z_t + c z_t log RV_t (Frisch-Waugh; date-clustered HAC)
    z = np.array([m[2] for m in mech]); y = np.array([m[3] for m in mech]); w = z * np.array([m[4] for m in mech])
    X = np.c_[np.ones(len(z)), z]
    wt = w - X @ np.linalg.lstsq(X, w, rcond=None)[0]
    cslope = float((wt * y).sum() / (wt ** 2).sum())
    by = {}
    for m, u in zip(mech, wt * y):
        by[m[1]] = by.get(m[1], 0.0) + u
    tser = [by[d] for d in sorted(by)]
    t5 = vs.nw_t(tser, 5)
    prim["V5"] = {"c": cslope, "t_hac": t5, "p_one_sided": vs.p_one_sided(-t5), "n_obs": len(mech)}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    verdict = {k: ("EDGE" if prim[k]["p_holm"] < 0.05 and all(h > 0 for h in prim[k]["halves_bps"]) else "NO EDGE") for k in ("V1", "V2", "V4")}
    verdict["V5_mechanism"] = "PRESENT" if prim["V5"]["p_holm"] < 0.05 else "ABSENT"
    res = {"primary": prim, "verdict": verdict}
    res["per_market_primary"] = {f"{n}|{a}": stats(list(grids[n].get(p, {}).values()) or [0.0])
                                 for n in MARKETS for a, p in (("rev", PRIMARY_REV), ("con", PRIMARY_CON))}
    per = {f"{n}|{k}": v for n in grids for k, v in grids[n].items()}
    res["share_variants_positive"] = float(np.mean([np.mean(list(v.values())) > 0 for v in per.values() if v]))
    res["battery"] = to_battery(per, "VOL", date(2004, 2, 1), date(2015, 6, 1), 2008)
    json.dump(res, open(os.path.join(OUT, "round39_volume.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "verdict", "share_variants_positive", "battery")}, indent=1, default=str))
    for k, s in res["per_market_primary"].items():
        print(k, round(s["mean_bps"], 2), round(s["t_hac"], 2), s["n"])


if __name__ == "__main__":
    main()
