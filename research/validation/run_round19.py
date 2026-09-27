"""Round 19 (PREREGISTRATION.md A33).

    python3 run_round19.py GT   the Tokyo fix on Gotobi days (Ito & Yamada 2017)                     -> results/round19_gt.json
    python3 run_round19.py FD   FOMC- and BoJ-day currency premia (Mueller, Tahbaz-Salehi & Vedolin 2017) -> results/round19_fd.json
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date, timedelta

import numpy as np

import run_family_a as fa
import vstats as vs
from data_calendar import boj_days, fomc_days, gotobi_days, japan_holidays
from data_fred import series as fred
from data_histdata import NY
from data_minutes import local, price_at
from run_round10 import finish, weekday_calendar
from run_round11 import TOKYO

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 13722
START, END = date(2014, 1, 1), date(2026, 9, 18)
HALF = date(2020, 1, 1)
SPLIT = date(2020, 1, 1)


def mean_test(v):
    x = np.array(v, dtype=float)
    t = vs.nw_t(list(x), 5)
    return {"n": int(len(x)), "mean_bps": float(x.mean() * 1e4) if len(x) else None, "t_hac": t, "p_one_sided": vs.p_one_sided(t)}


def event_test(v):
    """Plain t on non-overlapping event returns."""
    x = np.array(v, dtype=float)
    t = float(x.mean() / (x.std(ddof=1) / math.sqrt(len(x)))) if len(x) > 2 else math.nan
    return {"n": int(len(x)), "mean_bps": float(x.mean() * 1e4), "sd_bps": float(x.std(ddof=1) * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t)}


def welch(a, b):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    t = float((a.mean() - b.mean()) / se)
    return {"diff_bps": float((a.mean() - b.mean()) * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t)}


def halves(rows):
    """rows: {date: pnl}; mean (bps) in 2014-19 and 2020-26."""
    a = [v for d, v in rows.items() if START <= d < HALF]
    b = [v for d, v in rows.items() if HALF <= d <= END]
    return (float(np.mean(a) * 1e4) if a else None, float(np.mean(b) * 1e4) if b else None)


def to_daily(per, cal):
    names = sorted(per)
    ci = {d: i for i, d in enumerate(cal)}
    X = np.zeros((len(cal), len(names)))
    for j, n in enumerate(names):
        for d, v in per[n].items():
            if d in ci:
                X[ci[d], j] = v
    return X, names


# ---------------------------------------------------------------- GT

GT_WINDOWS = {"PRE": (540, 595, 1), "PRELATE": (570, 595, 1), "PREEARLY": (510, 595, 1), "POST5": (595, 600, -1),
              "POST": (595, 655, -1), "POST12": (595, 720, -1), "POST15": (595, 900, -1)}
GT_COST = {"USDJPY": 1.0e-4, "EURJPY": 2.0e-4}


def gt_returns(sym):
    """{window: {Tokyo date: gross signed return}} for every Tokyo business day."""
    t, x = local(sym, range(2003, 2027), TOKYO)
    day, mod = t // 1440, t % 1440
    marks = sorted({m for a, b, _ in GT_WINDOWS.values() for m in (a, b)})
    px = {m: price_at(day, mod, x, m) for m in marks}
    del t, x, day, mod
    hol = japan_holidays()
    out = {}
    for w, (a, b, sgn) in GT_WINDOWS.items():
        rows = {}
        for k, p0 in px[a].items():
            p1 = px[b].get(k)
            d = date.fromordinal(int(k) + date(1970, 1, 1).toordinal())
            if p1 is None or d.weekday() >= 5 or d in hol or d > END:
                continue
            rows[d] = sgn * (p1 / p0 - 1)
        out[w] = rows
    return out


def family_gt():
    got = gotobi_days()
    res = {}
    per = {}
    data = {}
    for sym in ("USDJPY", "EURJPY"):
        g = gt_returns(sym)
        data[sym] = g
        c = GT_COST[sym]
        for w, rows in g.items():
            for dset, keep in (("GOTO", lambda d: d in got), ("G510", lambda d: got.get(d) == "510"), ("ME", lambda d: got.get(d) == "ME")):
                per[f"{sym}|{w}|{dset}"] = {d: v - c for d, v in rows.items() if keep(d)}
        print("GT", sym, {w: len(r) for w, r in g.items()}, flush=True)
    uj = data["USDJPY"]
    c = GT_COST["USDJPY"]
    inwin = lambda d: START <= d <= END
    pre_g = {d: v - c for d, v in uj["PRE"].items() if d in got and inwin(d)}
    post_g = {d: v - c for d, v in uj["POST"].items() if d in got and inwin(d)}
    prim = {"G1": mean_test([v for _, v in sorted(pre_g.items())]), "G3": mean_test([v for _, v in sorted(post_g.items())])}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k, rows in (("G1", pre_g), ("G3", post_g)):
        prim[k]["p_holm"] = holm[k]
        prim[k]["halves_bps"] = halves(rows)
        gross = [v + c for v in rows.values()]
        tg = vs.nw_t(gross, 5)
        prim[k]["gross_mean_bps"] = float(np.mean(gross) * 1e4)
        prim[k]["gross_p_one_sided"] = vs.p_one_sided(tg)
    g2 = welch([v for d, v in uj["PRE"].items() if d in got and inwin(d)], [v for d, v in uj["PRE"].items() if d not in got and inwin(d)])
    edge = [k for k in ("G1", "G3") if prim[k]["p_holm"] < 0.05 and all(h is not None and h > 0 for h in prim[k]["halves_bps"])]
    weak = any(prim[k]["p_holm"] < 0.05 or (prim[k]["gross_p_one_sided"] < 0.05) for k in ("G1", "G3"))
    res["primary"] = prim
    res["G2_mechanism_pre_gotobi_minus_other"] = g2
    res["verdict"] = "EDGE" if edge else "WEAK" if weak else "NO EDGE"
    # descriptive: every window x day set x period, gross bps
    desc = {}
    for sym, g in data.items():
        for w, rows in g.items():
            for per_lab, lo, hi in (("2003_2013", date(2003, 1, 1), date(2013, 12, 31)), ("2014_2026", START, END)):
                for dset, keep in (("GOTO", lambda d: d in got), ("OTHER", lambda d: d not in got), ("ME", lambda d: got.get(d) == "ME"),
                                   ("G510", lambda d: got.get(d) == "510"), ("GOTO_FRI", lambda d: d in got and d.weekday() == 4),
                                   ("GOTO_NONFRI", lambda d: d in got and d.weekday() != 4)):
                    v = [x for d, x in rows.items() if lo <= d <= hi and keep(d)]
                    if len(v) > 10:
                        m = mean_test(v)
                        desc[f"{sym}|{w}|{dset}|{per_lab}"] = {"n": m["n"], "gross_bps": m["mean_bps"], "t": m["t_hac"]}
    res["descriptive_gross"] = desc
    res["per_year_usdjpy_gross_bps"] = {w: {y: float(np.mean([v for d, v in uj[w].items() if d in got and d.year == y]) * 1e4)
                                            for y in range(2003, 2027)} for w in ("PRE", "POST")}
    cal = weekday_calendar(date(2003, 1, 1), END)
    X, names = to_daily(per, cal)
    bat = finish("GT", X, None, names, cal, SPLIT, 2016)
    res["battery"] = {k: bat["raw"][k] for k in ("spa_validation", "pbo_full_sample", "walk_forward_top5", "verdict", "romano_wolf_significant_5pct")}
    json.dump(res, open(os.path.join(OUT, "round19_gt.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "G2_mechanism_pre_gotobi_minus_other", "verdict")}, indent=1, default=str))
    for k in sorted(desc):
        if k.startswith("USDJPY|PRE|") or k.startswith("USDJPY|POST|"):
            print(k, desc[k])


# ---------------------------------------------------------------- FD

MAJORS = {"EURUSD": ("EUR", 1), "GBPUSD": ("GBP", 1), "USDJPY": ("JPY", -1), "AUDUSD": ("AUD", 1), "USDCAD": ("CAD", -1),
          "USDCHF": ("CHF", -1), "NZDUSD": ("NZD", 1)}
JPYB = ("USDJPY", "EURJPY", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY", "NZDJPY")
RATE_ID = {"EUR": "EZ", "GBP": "GB", "JPY": "JP", "AUD": "AU", "CAD": "CA", "CHF": "CH", "NZD": "NZ"}


def ny_marks(sym):
    """{NY date: (price 13:55, price 16:45)}."""
    t, x = local(sym, range(2003, 2027), NY)
    day, mod = t // 1440, t % 1440
    a, b = price_at(day, mod, x, 835), price_at(day, mod, x, 1005)
    e = date(1970, 1, 1).toordinal()
    return {date.fromordinal(int(k) + e): (a.get(k), b[k]) for k in b}


def window_returns(marks, sgn):
    """{NY date: {DAY, PRE, POST: return of the long-foreign position}} using the previous weekday's 16:45."""
    out = {}
    for d, (p1355, p1645) in marks.items():
        if d.weekday() >= 5:
            continue
        prev = d - timedelta(days=3 if d.weekday() == 0 else 1)
        if prev not in marks:
            continue
        p0 = marks[prev][1]

        def r(a, b):
            if a is None or b is None:
                return None
            return b / a - 1 if sgn == 1 else a / b - 1
        out[d] = {"DAY": r(p0, p1645), "PRE": r(p0, p1355), "POST": r(p1355, p1645)}
    return out


def month_rates():
    """{(year, month): {ccy: 3-month rate at the previous month-end}} with the last value carried forward."""
    raw = {c: {(d.year, d.month): v for d, v in fred(f"IR3TIB01{k}M156N")} for c, k in RATE_ID.items()}
    out, last = {}, {}
    for y in range(2002, 2027):
        for m in range(1, 13):
            py, pm = (y, m - 1) if m > 1 else (y - 1, 12)
            for c in RATE_ID:
                if (py, pm) in raw[c]:
                    last[c] = raw[c][(py, pm)]
            out[(y, m)] = dict(last)
    return out


def family_fd():
    fomc = {d for d in fomc_days(1994) if d <= END}
    boj = {d for d in boj_days() if d <= END}
    legs = {}
    for sym, (ccy, sgn) in MAJORS.items():
        legs[sym] = window_returns(ny_marks(sym), sgn)
        print("FD", sym, len(legs[sym]), flush=True)
    for sym in JPYB[1:]:
        legs[sym] = window_returns(ny_marks(sym), 1)
        print("FD", sym, len(legs[sym]), flush=True)
    legs["XAUUSD"] = window_returns(ny_marks("XAUUSD"), 1)
    rates = month_rates()
    cost = {s: (2.0e-4 if s in JPYB[1:] else 2.5e-4 if s == "XAUUSD" else 1.0e-4) for s in legs}
    usdjpy_long_usd = {d: {k: (None if v is None else (1 / (1 + v) - 1)) for k, v in w.items()} for d, w in legs["USDJPY"].items()}

    def basket(days, members, win, leg_map=None):
        """{date: net return} of an equal-weight basket (members may depend on the date)."""
        out = {}
        for d in sorted(days):
            ms = members(d) if callable(members) else members
            vals = []
            for s in ms:
                src = (leg_map or legs)[s]
                if d not in src or src[d][win] is None:
                    vals = None
                    break
                vals.append(src[d][win] - cost[s])
            if vals:
                out[d] = float(np.mean(vals))
        return out

    def hy(d):
        r = rates[(d.year, d.month)]
        top = sorted(RATE_ID, key=lambda c: -r.get(c, -99))[:3]
        return [s for s, (c, _) in MAJORS.items() if c in top]
    jpyb_map = dict(legs)
    jpyb_map["USDJPY"] = usdjpy_long_usd
    all_days = set(legs["EURUSD"])
    per = {}
    for win in ("DAY", "PRE", "POST"):
        per[f"DOL|FOMC|{win}"] = basket(fomc & all_days, list(MAJORS), win)
        per[f"HY|FOMC|{win}"] = basket(fomc & all_days, hy, win)
        per[f"GOLD|FOMC|{win}"] = basket(fomc & set(legs["XAUUSD"]), ["XAUUSD"], win)
    per["JPYB|BOJ|DAY"] = basket(boj & all_days, list(JPYB), "DAY", jpyb_map)
    per["DOL|BOJ|DAY"] = basket(boj & all_days, list(MAJORS), "DAY")
    inwin = lambda rows: {d: v for d, v in rows.items() if START <= d <= END}
    prim = {"F1": event_test(list(inwin(per["DOL|FOMC|DAY"]).values())), "F2": event_test(list(inwin(per["HY|FOMC|DAY"]).values())),
            "F3": event_test(list(inwin(per["JPYB|BOJ|DAY"]).values()))}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    src = {"F1": "DOL|FOMC|DAY", "F2": "HY|FOMC|DAY", "F3": "JPYB|BOJ|DAY"}
    for k in prim:
        prim[k]["p_holm"] = holm[k]
        prim[k]["halves_bps"] = halves(per[src[k]])
    # mechanism: announcement day minus other weekdays (gross DAY returns)
    other_dol = basket({d for d in all_days if d not in fomc and START <= d <= END}, list(MAJORS), "DAY")
    other_hy = basket({d for d in all_days if d not in fomc and START <= d <= END}, hy, "DAY")
    other_jpyb = basket({d for d in all_days if d not in boj and START <= d <= END}, list(JPYB), "DAY", jpyb_map)
    mech = {"F1": welch(list(inwin(per["DOL|FOMC|DAY"]).values()), list(other_dol.values())),
            "F2": welch(list(inwin(per["HY|FOMC|DAY"]).values()), list(other_hy.values())),
            "F3": welch(list(inwin(per["JPYB|BOJ|DAY"]).values()), list(other_jpyb.values()))}
    edge = [k for k in prim if prim[k]["p_holm"] < 0.05 and all(h is not None and h > 0 for h in prim[k]["halves_bps"])]
    weak = any(prim[k]["p_one_sided"] < 0.05 for k in prim)
    res = {"primary": prim, "mechanism_event_minus_other_days": mech, "verdict": "EDGE" if edge else "WEAK" if weak else "NO EDGE"}
    res["replication_2003_2013"] = {n: event_test([v for d, v in rows.items() if d < date(2014, 1, 1)]) for n, rows in per.items()
                                    if sum(1 for d in rows if d < date(2014, 1, 1)) > 10}
    res["secondary_2014_2026"] = {n: event_test(list(inwin(rows).values())) for n, rows in per.items()}
    res["per_year_dol_fomc_bps"] = {y: float(np.mean([v for d, v in per["DOL|FOMC|DAY"].items() if d.year == y]) * 1e4) for y in range(2003, 2027)}
    cal = weekday_calendar(date(2003, 1, 1), END)
    X, names = to_daily(per, cal)
    bat = finish("FD", X, None, names, cal, SPLIT, 2016)
    res["battery"] = {k: bat["raw"][k] for k in ("spa_validation", "pbo_full_sample", "walk_forward_top5", "verdict", "romano_wolf_significant_5pct")}
    json.dump(res, open(os.path.join(OUT, "round19_fd.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "mechanism_event_minus_other_days", "verdict")}, indent=1, default=str))
    for n, v in res["secondary_2014_2026"].items():
        print("2014-26", n, v)
    for n, v in res["replication_2003_2013"].items():
        print("2003-13", n, v)


if __name__ == "__main__":
    {"GT": family_gt, "FD": family_fd}[sys.argv[1]]()
