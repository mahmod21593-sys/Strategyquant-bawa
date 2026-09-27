"""Round 22 (PREREGISTRATION.md A36).

    python3 run_round22.py GS   the autumn effect in gold and silver (Baur 2013)        -> results/round22_gs.json
    python3 run_round22.py AB   the Asian bid in gold after New York sell-offs           -> results/round22_ab.json
    python3 run_round22.py JH   the Tokyo fix on Japanese holidays (GT mechanism check)  -> results/round22_jh.json
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date, timedelta
from zoneinfo import ZoneInfo

import numpy as np

import run_family_a as fa
import vstats as vs
from data_audit import spike_mask
from data_calendar import gotobi_days, japan_holidays
from data_fred import series as fred
from data_histdata import NY
from data_minutes import local, price_at
from run_round10 import finish, weekday_calendar
from run_round11 import TOKYO

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 13822
E = date(1970, 1, 1).toordinal()
END = date(2026, 9, 18)
COST = {"XAUUSD": 2.5e-4, "XAGUSD": 5.0e-4}
SHANGHAI = ZoneInfo("Asia/Shanghai")


def clean_local(sym, years, tz):
    t, x = local(sym, years, tz)
    keep = ~spike_mask(x, 0.02 if sym.startswith("XA") else 0.01)
    return t[keep], x[keep]


def hac(v, lag=5):
    x = np.array(v, dtype=float)
    t = vs.nw_t(list(x), lag)
    return {"n": int(len(x)), "mean_bps": float(x.mean() * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t)}


def ttest(v):
    x = np.array(v, dtype=float)
    t = float(x.mean() / (x.std(ddof=1) / math.sqrt(len(x))))
    return {"n": int(len(x)), "mean_pct": float(x.mean() * 100), "t": t, "p_one_sided": vs.p_one_sided(t)}


def welch(a, b, sign=1):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    t = float((a.mean() - b.mean()) / se)
    return {"diff_bps": float((a.mean() - b.mean()) * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t, sign)}


# ---------------------------------------------------------------- GS

def daily_1645(sym):
    t, x = clean_local(sym, range(2009, 2027), NY)
    day, mod = t // 1440, t % 1440
    p = price_at(day, mod, x, 1005)
    return {date.fromordinal(int(k) + E): v for k, v in p.items() if date.fromordinal(int(k) + E).weekday() < 5}


def family_gs():
    us3 = {(d.year, d.month): v / 100 for d, v in fred("IR3TIB01USM156N")}
    res = {}
    for sym in ("XAUUSD", "XAGUSD"):
        px = daily_1645(sym)
        days = sorted(px)
        last = {}
        for d in days:
            last[(d.year, d.month)] = d
        months = sorted(last)
        rows = []
        for a, b in zip(months[:-1], months[1:]):
            if b > (2026, 8):
                continue
            r = px[last[b]] / px[last[a]] - 1
            prev = (b[0], b[1] - 1) if b[1] > 1 else (b[0] - 1, 12)
            fin = (us3.get(prev, 0.0) + 0.02) / 12
            rows.append((b, r, r - fin - COST[sym]))
        post = [x for x in rows if x[0][0] >= 2011]
        so = [x for x in post if x[0][1] in (9, 11)]
        other = [x for x in post if x[0][1] not in (9, 11)]
        r = {"GS1_net_sep_nov": ttest([x[2] for x in so]), "GS2_gross_sep_nov_minus_other": welch([x[1] for x in so], [x[1] for x in other]),
             "sep_gross": ttest([x[1] for x in so if x[0][1] == 9]), "nov_gross": ttest([x[1] for x in so if x[0][1] == 11]),
             "by_month_gross_pct": {m: ttest([x[1] for x in post if x[0][1] == m]) for m in range(1, 13)},
             "in_sample_2009_2010": {m: float(np.mean([x[1] for x in rows if x[0][0] < 2011 and x[0][1] == m]) * 100) if any(
                 x[0][0] < 2011 and x[0][1] == m for x in rows) else None for m in (9, 11)}}
        # turn of month: long from the close before the last trading day to the close of the 3rd trading day, daily
        idx = {d: i for i, d in enumerate(days)}
        tom = []
        for m in months:
            if m[0] < 2011 or m > (2026, 8):
                continue
            ld = last[m]
            i = idx[ld]
            if i - 1 < 0 or i + 3 >= len(days):
                continue
            g = px[days[i + 3]] / px[days[i - 1]] - 1
            tom.append(g - COST[sym] - 4 * (us3.get(m, 0.0) + 0.02) / 365 * 1.4)
        r["turn_of_month_net"] = ttest(tom)
        res[sym] = r
        print("GS", sym, json.dumps({k: v for k, v in r.items() if k != "by_month_gross_pct"}, default=str), flush=True)
        print("   by month", {m: (round(v["mean_pct"], 2), round(v["t"], 2)) for m, v in r["by_month_gross_pct"].items()})
    g = res["XAUUSD"]
    prim = {"GS1": g["GS1_net_sep_nov"], "GS2": g["GS2_gross_sep_nov_minus_other"]}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    both = g["sep_gross"]["mean_pct"] > 0 and g["nov_gross"]["mean_pct"] > 0
    res["primary"] = prim
    res["verdict"] = "EDGE" if prim["GS1"]["p_holm"] < 0.05 and both else "SEASONAL, NOT TRADEABLE" if prim["GS2"]["p_holm"] < 0.05 else "NO EDGE"
    json.dump(res, open(os.path.join(OUT, "round22_gs.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "verdict")}, indent=1, default=str))


# ---------------------------------------------------------------- AB

def family_ab():
    res, per = {}, {}
    for sym in ("XAUUSD", "XAGUSD"):
        t, x = clean_local(sym, range(2009, 2027), NY)
        day, mod = t // 1440, t % 1440
        a, b = price_at(day, mod, x, 510), price_at(day, mod, x, 960)
        ny = {date.fromordinal(int(k) + E): b[k] / a[k] - 1 for k in a if k in b and date.fromordinal(int(k) + E).weekday() < 5}
        del t, x, day, mod
        t, x = clean_local(sym, range(2009, 2027), SHANGHAI)
        day, mod = t // 1440, t % 1440
        s0, s1, s2 = price_at(day, mod, x, 540), price_at(day, mod, x, 690), price_at(day, mod, x, 900)
        asia = {}
        for k, p0 in s0.items():
            d = date.fromordinal(int(k) + E)
            if d.weekday() < 5 and k in s2 and k in s1:
                r15, r1130 = s2[k] / p0 - 1, s1[k] / p0 - 1
                if abs(r15) < 0.05:
                    asia[d] = (r15, r1130)
        nd = sorted(ny)
        rows = []  # (NY date, NY return, z, next Beijing date's Asian returns)
        for i in range(20, len(nd)):
            d = nd[i]
            sd = float(np.std([ny[nd[j]] for j in range(i - 20, i)], ddof=1))
            nxt = d + timedelta(days=3 if d.weekday() == 4 else 1)
            if sd > 0 and nxt in asia and d <= END:
                rows.append((d, ny[d], ny[d] / sd, asia[nxt]))
        c = COST[sym]
        sig = [r for r in rows if r[2] < -1.0]
        oth = [r for r in rows if r[2] >= -1.0]
        out = {"AB1_net": hac([r[3][0] - c for r in sig]), "AB2_gross_signal_minus_other": welch([r[3][0] for r in sig], [r[3][0] for r in oth]),
               "halves_net_bps": (float(np.mean([r[3][0] - c for r in sig if r[0] < date(2018, 1, 1)]) * 1e4),
                                  float(np.mean([r[3][0] - c for r in sig if r[0] >= date(2018, 1, 1)]) * 1e4)),
               "asia_all_days_gross": hac([r[3][0] for r in rows]),
               "after_big_rise_gross_long": hac([r[3][0] for r in rows if r[2] > 1.0])}
        for lab, cond, sgn in (("dn1.0", lambda z: z < -1.0, 1), ("dn1.5", lambda z: z < -1.5, 1), ("up1.0short", lambda z: z > 1.0, -1)):
            for ex, j in (("x15", 0), ("x1130", 1)):
                per[f"{sym}|{lab}|{ex}"] = {r[0]: sgn * r[3][j] - c for r in rows if cond(r[2])}
        res[sym] = out
        print("AB", sym, json.dumps(out, default=str), flush=True)
    g = res["XAUUSD"]
    prim = {"AB1": g["AB1_net"], "AB2": g["AB2_gross_signal_minus_other"]}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    res["primary"] = prim
    ok = prim["AB1"]["p_holm"] < 0.05 and all(h > 0 for h in g["halves_net_bps"])
    res["verdict"] = "EDGE" if ok else "DEMAND EFFECT, NOT TRADEABLE" if prim["AB2"]["p_holm"] < 0.05 else "NO EDGE"
    cal = weekday_calendar(date(2009, 1, 1), END)
    ci = {d: i for i, d in enumerate(cal)}
    names = sorted(per)
    X = np.zeros((len(cal), len(names)))
    for jn, n in enumerate(names):
        for d, v in per[n].items():
            if d in ci:
                X[ci[d], jn] = v
    bat = finish("AB", X, None, names, cal, date(2018, 1, 1), 2011)
    res["battery"] = {k: bat["raw"][k] for k in ("spa_validation", "pbo_full_sample", "walk_forward_top5", "verdict", "romano_wolf_significant_5pct")}
    json.dump(res, open(os.path.join(OUT, "round22_ab.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "verdict")}, indent=1, default=str))


# ---------------------------------------------------------------- JH

def family_jh():
    got = gotobi_days(2003, 2026)
    import holidays
    nat = set(holidays.Japan(years=range(2003, 2027)))
    bank = japan_holidays(2003, 2026)
    res = {}
    for sym, y0 in (("USDJPY", 2003), ("EURJPY", 2008)):
        t, x = clean_local(sym, range(y0, 2027), TOKYO)
        day, mod = t // 1440, t % 1440
        p0, p1, p2 = price_at(day, mod, x, 540), price_at(day, mod, x, 595), price_at(day, mod, x, 655)
        hol, norm = {"PRE": [], "POST": []}, {"PRE": [], "POST": []}
        for k, a in p1.items():
            d = date.fromordinal(int(k) + E)
            if d.weekday() >= 5 or d > END or k not in p0 or k not in p2:
                continue
            is_hol = d in nat and not (d.month == 1 and d.day <= 3) and not (d.month == 12 and d.day == 31)
            if is_hol:
                tgt = hol
            elif d not in bank and d not in got:
                tgt = norm
            else:
                continue
            tgt["PRE"].append(a / p0[k] - 1)
            tgt["POST"].append(a / p2[k] - 1)
        r = {"J1_post_holiday_minus_normal": welch(hol["POST"], norm["POST"], -1), "J2_pre_holiday_minus_normal": welch(hol["PRE"], norm["PRE"], -1),
             "holiday": {w: hac(v) for w, v in hol.items()}, "normal": {w: hac(v) for w, v in norm.items()}}
        res[sym] = r
        print("JH", sym, json.dumps(r, default=str), flush=True)
    json.dump(res, open(os.path.join(OUT, "round22_jh.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    {"GS": family_gs, "AB": family_ab, "JH": family_jh}[sys.argv[1]]()
