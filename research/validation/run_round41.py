"""Round 41 (PREREGISTRATION.md A55): overseas cash sessions fade the prior US session — confirmation on unseen 2000-2012
Yahoo daily data (Nikkei, Hang Seng, ASX 200, DAX), then 2013-26 net on HistData minute data, costs from Dukascopy spreads.

    python3 run_round41.py COST   -> results/round41_costs.json
    python3 run_round41.py RUN    -> results/round41_overseas_fade.json
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np

import run_family_a as fa
import vstats as vs
from data_histdata import NY
from data_minutes import price_at
from data_yahoo import daily
from run_round24 import clean_local

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 14655
E = date(1970, 1, 1).toordinal()
# market: (Yahoo symbol, HistData symbol, tz, cash open, cash close (local minutes), Dukascopy instrument)
JP_SWITCH = date(2024, 11, 5)
MARKETS = {"JP225": ("^N225", "JPXJPY", "Asia/Tokyo", 540, lambda d: 930 if d >= JP_SWITCH else 900, "JPN.IDX/JPY"),
           "HK50": ("^HSI", "HKXHKD", "Asia/Hong_Kong", 570, lambda d: 960, "HKG.IDX/HKD"),
           "AUS200": ("^AXJO", "AUXAUD", "Australia/Sydney", 600, lambda d: 960, "AUS.IDX/AUD"),
           "GER40": ("^GDAXI", "GRXEUR", "Europe/Berlin", 540, lambda d: 1050, "DEU.IDX/EUR")}
SPLIT_UNSEEN = date(2006, 7, 1)


def cost():
    from run_round38 import page
    ts = int(datetime(2025, 3, 3, tzinfo=timezone.utc).timestamp() * 1000)
    out = {}
    for m, (_, _, tzn, op, close_of, ins) in MARKETS.items():
        tz = ZoneInfo(tzn)
        b, a = page(ins, "B", ts), page(ins, "A", ts)
        sp = []
        for t in sorted(set(a) & set(b)):
            lt = datetime.fromtimestamp(t / 1000, timezone.utc).astimezone(tz)
            if op <= lt.hour * 60 + lt.minute < close_of(lt.date()):
                sp.append((a[t][4] - b[t][4]) / ((a[t][4] + b[t][4]) / 2) * 1e4)
        med = float(np.median(sp))
        out[m] = {"session_minutes": len(sp), "median_spread_bps": med, "cost_round_trip_bps": med + 0.5}
        print(m, out[m], flush=True)
    json.dump(out, open(os.path.join(OUT, "round41_costs.json"), "w"), indent=1)


def us_signal_yahoo():
    rows = daily("^GSPC")
    ds = [r["date"] for r in rows]
    c = np.array([r["c"] for r in rows])
    r = np.r_[np.nan, c[1:] / c[:-1] - 1]
    sig20 = np.array([np.nanstd(r[max(1, i - 20):i], ddof=1) if i > 21 else np.nan for i in range(len(r))])
    return ds, r, sig20


def rows_yahoo(m, y0, y1):
    """[(date, US return, US sigma20, overseas open->close)] on overseas dates in [y0, y1]."""
    ysym = MARKETS[m][0]
    ud, ur, us = us_signal_yahoo()
    ov = daily(ysym)
    out = []
    prev_c = None
    for r in ov:
        d, o, c = r["date"], r["o"], r["c"]
        bad = prev_c is not None and m == "AUS200" and math.isclose(o, prev_c, rel_tol=1e-6)
        prev_c = c
        if not (y0 <= d.year <= y1) or d.weekday() >= 5 or bad or o <= 0:
            continue
        j = int(np.searchsorted(np.array(ud), d)) - 1  # last US date strictly before d
        if j < 22 or not np.isfinite(ur[j]) or ur[j] == 0:
            continue
        oc = c / o - 1
        if abs(oc) > 0.12:
            continue
        out.append((d, float(ur[j]), float(us[j]), float(oc)))
    return out


def rows_histdata(m):
    """2013-26 rows from minute data (round 26 construction: US mark 15:55 NY, overseas cash open -> close)."""
    from run_round26 import us_closes
    uc = us_closes()
    times = np.array([a for a, _ in uc])
    vals = np.array([b for _, b in uc])
    _, sym, tzn, om, close_of, _ = MARKETS[m]
    tz = ZoneInfo(tzn)
    t, x = clean_local(sym, range(2012, 2027), tz)
    day, mod = t // 1440, t % 1440
    tn, _ = clean_local(sym, range(2012, 2027), NY)
    pos = {int(v): int(w) for v, w in zip((day * 1440 + mod).tolist(), tn.tolist())}
    marks = {mm: price_at(day, mod, x, mm) for mm in sorted({om, close_of(date(2015, 1, 1)), close_of(date(2026, 1, 1))})}
    out = []
    for k in sorted(set(day.tolist())):
        d = date.fromordinal(int(k) + E)
        if d.weekday() >= 5 or not (date(2013, 1, 1) <= d <= date(2026, 9, 18)):
            continue
        po, pc = marks[om].get(k), marks[close_of(d)].get(k)
        ony = pos.get(int(k) * 1440 + om)
        if po is None or pc is None or ony is None:
            continue
        j = int(np.searchsorted(times, ony)) - 1
        if j < 21:
            continue
        s = vals[j] / vals[j - 1] - 1
        rr = np.diff(vals[j - 21:j]) / vals[j - 21:j - 1]
        oc = pc / po - 1
        if s == 0 or abs(oc) > 0.12:
            continue
        out.append((d, float(s), float(np.std(rr, ddof=1)), float(oc)))
    return out


def fade(rows, c=0.0):
    return {d: -np.sign(u) * oc - c for d, u, _, oc in rows}


def portfolio(per):
    days = sorted(set(d for p in per.values() for d in p))
    return days, [float(np.mean([p[d] for p in per.values() if d in p])) for d in days]


def stats(v, lag=5):
    a = np.array(v, dtype=float)
    t = vs.nw_t(list(a), lag)
    return {"n": int(len(a)), "mean_bps": float(a.mean() * 1e4), "t_hac": t, "p_one_sided": vs.p_one_sided(t)}


def welch(a, b):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    t = float((a.mean() - b.mean()) / se)
    return {"diff_bps": float((a.mean() - b.mean()) * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t)}


def run():
    costs = {m: v["cost_round_trip_bps"] / 1e4 for m, v in json.load(open(os.path.join(OUT, "round41_costs.json"))).items()}
    unseen = {m: rows_yahoo(m, 2000, 2012) for m in MARKETS}
    for m, r in unseen.items():
        print("OSF unseen", m, len(r), flush=True)
    dg, vg = portfolio({m: fade(r) for m, r in unseen.items()})
    dn, vn = portfolio({m: fade(r, costs[m]) for m, r in unseen.items()})
    f1, f2 = stats(vg), stats(vn)
    f2["halves_bps"] = (float(np.mean([v for d, v in zip(dn, vn) if d < SPLIT_UNSEEN]) * 1e4),
                        float(np.mean([v for d, v in zip(dn, vn) if d >= SPLIT_UNSEEN]) * 1e4))
    big = [-np.sign(u) * oc for r in unseen.values() for _, u, s, oc in r if np.isfinite(s) and abs(u) > s]
    small = [-np.sign(u) * oc for r in unseen.values() for _, u, s, oc in r if np.isfinite(s) and abs(u) <= s]
    f3 = welch(big, small)
    prim = {"F1": f1, "F2": f2, "F3": f3}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    res = {"primary": prim, "costs_bps": {m: c * 1e4 for m, c in costs.items()}}
    res["unseen_per_market"] = {m: {"gross": stats(list(fade(r).values())), "net": stats(list(fade(r, costs[m]).values())),
                                    "after_US_up_bps": float(np.mean([oc for _, u, _, oc in r if u > 0]) * 1e4),
                                    "after_US_down_bps": float(np.mean([oc for _, u, _, oc in r if u < 0]) * 1e4)} for m, r in unseen.items()}
    res["unseen_big_vs_small_bps"] = (float(np.mean(big) * 1e4), float(np.mean(small) * 1e4))
    # 2013-26 on HistData minute data, net of measured costs
    recent = {m: rows_histdata(m) for m in MARKETS}
    d2, v2 = portfolio({m: fade(r, costs[m]) for m, r in recent.items()})
    res["recent_2013_26_net"] = stats(v2)
    res["recent_per_market_net"] = {m: stats(list(fade(r, costs[m]).values())) for m, r in recent.items()}
    res["recent_legs_net"] = {f"{m}|{leg}": stats([-np.sign(u) * oc - costs[m] for _, u, _, oc in r if (u > 0) == (leg == "short")], 0)
                              for m, r in recent.items() for leg in ("long", "short")}
    ok = (f1["p_holm"] < 0.05 and f2["p_holm"] < 0.05 and all(h > 0 for h in f2["halves_bps"]) and res["recent_2013_26_net"]["mean_bps"] > 0)
    res["verdict"] = "EDGE" if ok else "NO EDGE"
    # 1990-1999 check (reported, not a test)
    old = {m: rows_yahoo(m, 1990, 1999) for m in MARKETS}
    do, vo = portfolio({m: fade(r) for m, r in old.items() if r})
    res["check_1990s_gross"] = stats(vo) if vo else None
    # correlation with REV (round 11 build, US500+US100+JP225) on 2013-26
    try:
        from run_round4 import irx_map
        from run_round11 import rev_leg
        rates = irx_map()
        keys = sorted(rates)
        rev = {}
        for s in ("SPXUSD", "NSXUSD", "JPXJPY"):
            for d, r in rev_leg(s, rates, keys, False).items():
                rev[d] = rev.get(d, 0.0) + r[0] / 3
        pv = dict(zip(d2, v2))
        com = sorted(set(rev) & set(pv))
        res["corr_with_REV_2013_26"] = float(np.corrcoef([rev[d] for d in com], [pv[d] for d in com])[0, 1])
    except Exception as ex:
        res["corr_with_REV_2013_26"] = repr(ex)
    json.dump(res, open(os.path.join(OUT, "round41_overseas_fade.json"), "w"), indent=1, default=str)
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    {"COST": cost, "RUN": run}[sys.argv[1]]()
