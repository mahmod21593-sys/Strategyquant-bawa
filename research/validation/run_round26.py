"""Round 26 (PREREGISTRATION.md A40).

    python3 run_round26.py SP   the US session traded in the next overseas session (5 FTMO index CFDs) -> results/round26_sp.json
    python3 run_round26.py ED   reaction momentum after NFP / FOMC prints on US500/US100               -> results/round26_ed.json
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from zoneinfo import ZoneInfo

import numpy as np

import run_family_a as fa
import vstats as vs
from data_calendar import employment_days, fomc_days
from data_histdata import NY
from data_minutes import local, price_at
from run_round24 import clean_local, hac, to_battery, ttest

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 13895
E = date(1970, 1, 1).toordinal()
START, END = date(2013, 1, 1), date(2026, 9, 18)
HALF = date(2020, 1, 1)

# market -> (tz, open minute, close-of(date), cost per side)
JP_SWITCH = date(2024, 11, 5)
SP_MKTS = {"JP225": ("JPXJPY", "Asia/Tokyo", 540, lambda d: 930 if d >= JP_SWITCH else 900, 3.0e-4),
           "HK50": ("HKXHKD", "Asia/Hong_Kong", 570, lambda d: 960, 3.0e-4),
           "AUS200": ("AUXAUD", "Australia/Sydney", 600, lambda d: 960, 3.0e-4),
           "GER40": ("GRXEUR", "Europe/Berlin", 540, lambda d: 1050, 1.5e-4),
           "UK100": ("UKXGBP", "Europe/London", 480, lambda d: 990, 1.5e-4)}


def us_closes():
    """Sorted [(absolute NY minute of the 15:55 mark, close)] for SPXUSD."""
    t, x = clean_local("SPXUSD", range(2012, 2027), NY)
    day, mod = t // 1440, t % 1440
    p = price_at(day, mod, x, 955)
    return sorted((int(k) * 1440 + 955, v) for k, v in p.items() if date.fromordinal(int(k) + E).weekday() < 5)


def family_sp():
    uc = us_closes()
    times = np.array([a for a, _ in uc])
    vals = np.array([b for _, b in uc])
    print("SP US closes", len(uc), flush=True)
    res, per, legs = {}, {}, {}
    for mkt, (sym, tzname, om, close_of, cost) in SP_MKTS.items():
        tz = ZoneInfo(tzname)
        t, x = clean_local(sym, range(2012, 2027), tz)
        day, mod = t // 1440, t % 1440
        # absolute UTC-ish reference: convert each local session open back to an absolute NY minute via the raw t?
        # local() returns local wall-clock minutes; comparing across zones needs a common clock. Use the NY-clock copy.
        tn, xn = clean_local(sym, range(2012, 2027), NY)
        dn, mn = tn // 1440, tn % 1440
        marks = {}
        for m in sorted({om, om + 240} | {close_of(date(2015, 1, 1)), close_of(date(2026, 1, 1))}):
            marks[m] = price_at(day, mod, x, m)
        # map each local session day to the absolute NY minute of its open, using the NY-clock series
        first_ny = {}
        st = np.r_[0, np.nonzero(np.diff(day))[0] + 1]
        for i in st:
            k = int(day[i])
            first_ny.setdefault(k, None)
        # NY absolute minute of the local open: find, per local day, the NY timestamp of the bar at the local open
        loc_min = day * 1440 + mod
        ny_min = dn * 1440 + mn
        pos = {int(v): int(w) for v, w in zip(loc_min.tolist(), ny_min.tolist())}
        rows = []
        for k in sorted(set(day.tolist())):
            d = date.fromordinal(int(k) + E)
            if d.weekday() >= 5 or not (START <= d <= END):
                continue
            cm = close_of(d)
            po, ph, pc = marks[om].get(k), marks[om + 240].get(k), marks[cm].get(k)
            if po is None or pc is None or ph is None:
                continue
            ony = pos.get(int(k) * 1440 + om)
            if ony is None:
                continue
            j = np.searchsorted(times, ony) - 1
            if j < 1:
                continue
            sig = vals[j] / vals[j - 1] - 1
            r_full, r_half = pc / po - 1, ph / po - 1
            if max(abs(r_full), abs(r_half)) > 0.12 or sig == 0:
                continue
            rows.append((d, sig, r_full, r_half))
        legs[mkt] = rows
        print("SP", mkt, len(rows), flush=True)
        for rule in ("LS", "LO"):
            for exn, ri in (("close", 2), ("h4", 3)):
                per[f"{mkt}|{rule}|{exn}"] = {r[0]: (np.sign(r[1]) if rule == "LS" else (r[1] > 0)) * r[ri] - 2 * cost * (1 if rule == "LS" or r[1] > 0 else 0)
                                              for r in rows}
                per[f"{mkt}|{rule}|{exn}"] = {d: float(v) for d, v in per[f"{mkt}|{rule}|{exn}"].items() if v != 0 or rule == "LS"}
    ls = lambda rows, cost: {r[0]: float(np.sign(r[1]) * r[2] - 2 * cost) for r in rows}
    jp = ls(legs["JP225"], 3.0e-4)
    pool_days = sorted(set(legs["JP225"][i][0] for i in range(len(legs["JP225"]))) | {r[0] for r in legs["HK50"]} | {r[0] for r in legs["AUS200"]})
    m3 = {m: ls(legs[m], 3.0e-4) for m in ("JP225", "HK50", "AUS200")}
    pool = {}
    for d in pool_days:
        v = [m3[m][d] for m in m3 if d in m3[m]]
        if v:
            pool[d] = float(np.mean(v))
    prim = {"SP1": hac([v for _, v in sorted(jp.items())]), "SP2": hac([v for _, v in sorted(pool.items())])}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k, rows in (("SP1", jp), ("SP2", pool)):
        prim[k]["p_holm"] = holm[k]
        prim[k]["halves_bps"] = (float(np.mean([v for d, v in rows.items() if d < HALF]) * 1e4),
                                 float(np.mean([v for d, v in rows.items() if d >= HALF]) * 1e4))
    res["primary"] = prim
    edge = any(prim[k]["p_holm"] < 0.05 and all(h > 0 for h in prim[k]["halves_bps"]) for k in prim)
    res["verdict"] = "EDGE" if edge else "NO EDGE"
    res["descriptive"] = {}
    for mkt, rows in legs.items():
        up = [r[2] for r in rows if r[1] > 0]
        dn = [r[2] for r in rows if r[1] < 0]
        res["descriptive"][mkt] = {"n": len(rows), "session_after_US_up_bps": float(np.mean(up) * 1e4), "after_US_down_bps": float(np.mean(dn) * 1e4),
                                   "gross_LS_bps": float(np.mean([np.sign(r[1]) * r[2] for r in rows]) * 1e4),
                                   "corr_sign": float(np.corrcoef([np.sign(r[1]) for r in rows], [r[2] for r in rows])[0, 1])}
        print(mkt, res["descriptive"][mkt], flush=True)
    res["battery"] = to_battery(per, "SP", START, HALF, 2016)
    json.dump(res, open(os.path.join(OUT, "round26_sp.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "verdict")}, indent=1, default=str))


# ---------------------------------------------------------------- ED

def family_ed():
    nfp = {d for d in employment_days(2013) if START <= d <= END}
    fmc = {d for d in fomc_days(2013) if START <= d <= END}
    res, per, ev = {}, {}, {}
    for mkt, sym in (("US500", "SPXUSD"), ("US100", "NSXUSD")):
        t, x = clean_local(sym, range(2012, 2027), NY)
        day, mod = t // 1440, t % 1440
        p = {m: price_at(day, mod, x, m) for m in (510, 525, 615, 840, 855, 945, 955)}
        rows = {"NFP": [], "FOMC": []}
        for k, c955 in p[955].items():
            d = date.fromordinal(int(k) + E)
            if d in nfp and all(k in p[m] for m in (510, 525, 615)):
                r = p[525][k] / p[510][k] - 1
                if r != 0 and abs(c955 / p[525][k] - 1) < 0.12:
                    rows["NFP"].append((d, r, c955 / p[525][k] - 1, p[615][k] / p[525][k] - 1))
            if d in fmc and all(k in p[m] for m in (840, 855, 945)):
                r = p[855][k] / p[840][k] - 1
                if r != 0 and abs(c955 / p[855][k] - 1) < 0.12:
                    rows["FOMC"].append((d, r, c955 / p[855][k] - 1, p[945][k] / p[855][k] - 1))
        ev[mkt] = rows
        for evn in ("NFP", "FOMC"):
            for exn, ri in (("x1555", 2), ("x90m", 3)):
                per[f"{mkt}|{evn}|{exn}"] = {r[0]: float(np.sign(r[1]) * r[ri] - 3.0e-4) for r in rows[evn]}
        print("ED", mkt, {k: len(v) for k, v in rows.items()}, flush=True)
    prim = {}
    for key, evn in (("E1", "NFP"), ("E2", "FOMC")):
        rows = ev["US500"][evn]
        net = [float(np.sign(r[1]) * r[2] - 3.0e-4) for r in rows]
        prim[key] = ttest(net)
        prim[key]["halves_bps"] = (float(np.mean([v for r, v in zip(rows, net) if r[0] < HALF]) * 1e4),
                                   float(np.mean([v for r, v in zip(rows, net) if r[0] >= HALF]) * 1e4))
        prim[key]["gross"] = ttest([float(np.sign(r[1]) * r[2]) for r in rows])
        prim[key]["hit_rate"] = float(np.mean([np.sign(r[1]) * r[2] > 0 for r in rows]))
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    res["primary"] = prim
    edge = any(prim[k]["p_holm"] < 0.05 and all(h > 0 for h in prim[k]["halves_bps"]) for k in prim)
    res["verdict"] = "EDGE" if edge else "NO EDGE"
    res["battery"] = to_battery(per, "ED", START, HALF, 2016)
    json.dump(res, open(os.path.join(OUT, "round26_ed.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "verdict")}, indent=1, default=str))


if __name__ == "__main__":
    {"SP": family_sp, "ED": family_ed}[sys.argv[1]]()
