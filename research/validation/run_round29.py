"""Round 29 (PREREGISTRATION.md A43): the ECB 14:15 CET fix in EUR pairs, with the 2016-07-01 publication reform as
the natural experiment; plus the GT quarter-end implementation measurement.

    python3 run_round29.py   -> results/round29_ecb_fix.json
"""
from __future__ import annotations

import json
import os
from datetime import date
from zoneinfo import ZoneInfo

import numpy as np

import run_family_a as fa
import vstats as vs
from data_minutes import price_at
from run_round24 import clean_local, to_battery
from run_round27 import hac, welch

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 13935
E = date(1970, 1, 1).toordinal()
END = date(2026, 9, 18)
REFORM = date(2016, 7, 1)
BERLIN = ZoneInfo("Europe/Berlin")
PAIRS = {"EURUSD": (2003, 1.0e-4), "EURJPY": (2002, 2.0e-4), "EURGBP": (2008, 1.5e-4)}


def fix_rows(sym, y0):
    """[(date, PRE 13:45->14:15, POST 14:15->15:00, POST30 14:15->14:45)] on weekdays, Berlin clock."""
    t, x = clean_local(sym, range(y0, 2027), BERLIN)
    day, mod = t // 1440, t % 1440
    p = {m: price_at(day, mod, x, m) for m in (825, 855, 885, 900)}
    out = []
    for k, a in p[855].items():
        d = date.fromordinal(int(k) + E)
        if d.weekday() >= 5 or d > END or any(k not in p[m] for m in (825, 885, 900)):
            continue
        pre, post, post30 = a / p[825][k] - 1, p[900][k] / a - 1, p[885][k] / a - 1
        if max(abs(pre), abs(post)) < 0.05 and pre != 0:
            out.append((d, pre, post, post30))
    return out


def main():
    data = {s: fix_rows(s, y0) for s, (y0, _) in PAIRS.items()}
    for s, rows in data.items():
        print("EF", s, len(rows), rows[0][0], flush=True)
    rev = lambda rows: {r[0]: float(-np.sign(r[1]) * r[2]) for r in rows}
    pre_of = lambda rows: [r for r in rows if r[0] < REFORM]
    post_of = lambda rows: [r for r in rows if r[0] >= REFORM]
    eu = data["EURUSD"]
    r_eu = rev(eu)
    days = sorted(set(d for s in data for d, *_ in data[s]))
    bask = {}
    for d in days:
        v = [rev(data[s]).get(d) for s in data]
        v = [q for q in v if q is not None]
        if v:
            bask[d] = float(np.mean(v))
    e1 = hac([v for d, v in sorted(r_eu.items()) if d < REFORM])
    e1["p_one_sided"] = vs.p_one_sided(e1["t"], 1)
    e3 = hac([v for d, v in sorted(bask.items()) if d < REFORM])
    e3["p_one_sided"] = vs.p_one_sided(e3["t"], 1)
    prim = {"E1": e1, "E2": welch([v for d, v in r_eu.items() if d < REFORM], [v for d, v in r_eu.items() if d >= REFORM], 1), "E3": e3}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    res = {"primary": prim}
    # post-reform net for the tradeable-edge gate
    cost = PAIRS["EURUSD"][1]
    post_net = {d: v - cost for d, v in r_eu.items() if d >= REFORM}
    res["post_reform_net_eurusd"] = {**hac(list(post_net.values())),
        "halves_bps": (float(np.mean([v for d, v in post_net.items() if d < date(2022, 1, 1)]) * 1e4),
                       float(np.mean([v for d, v in post_net.items() if d >= date(2022, 1, 1)]) * 1e4))}
    passed = any(prim[k]["p_holm"] < 0.05 for k in ("E1", "E3"))
    net_ok = all(h > 0 for h in res["post_reform_net_eurusd"]["halves_bps"])
    res["verdict"] = ("TRADEABLE EDGE" if passed and net_ok else
                      "MECHANISM, REGIME OVER" if passed and prim["E2"]["p_holm"] < 0.05 else
                      "MECHANISM PRE-REFORM ONLY" if passed else "NO EDGE")
    # descriptive
    res["descriptive"] = {}
    for s, rows in data.items():
        r_ = rev(rows)
        res["descriptive"][s] = {"reversal_pre_reform": hac([v for d, v in r_.items() if d < REFORM]),
                                 "reversal_post_reform": hac([v for d, v in r_.items() if d >= REFORM]),
                                 "abs_pre_move_bps_pre_reform": float(np.mean([abs(r[1]) for r in pre_of(rows)]) * 1e4),
                                 "abs_pre_move_bps_post_reform": float(np.mean([abs(r[1]) for r in post_of(rows)]) * 1e4),
                                 "post_window_uncond_pre": hac([r[2] for r in pre_of(rows)]),
                                 "month_end_reversal_pre": hac([-np.sign(r[1]) * r[2] for r in pre_of(rows)
                                                                if (r[0].month != (r[0] + __import__('datetime').timedelta(days=3)).month)])}
        print(s, json.dumps(res["descriptive"][s], default=str), flush=True)
    per = {}
    for s, rows in data.items():
        for rule, sgn in (("R", -1), ("M", 1)):
            for exn, ri in (("x1500", 2), ("x1445", 3)):
                per[f"{s}|{rule}|{exn}"] = {r[0]: float(sgn * np.sign(r[1]) * r[ri] - PAIRS[s][1]) for r in rows}
    res["battery"] = to_battery(per, "EF", date(2003, 1, 1), REFORM, 2010)
    # GT quarter-end implementation measurement
    from data_calendar import gotobi_days, japan_holidays
    from data_minutes import local
    from run_round11 import TOKYO
    got, hol = gotobi_days(2003, 2026), japan_holidays(2003, 2026)
    t, x = clean_local("USDJPY", range(2003, 2027), TOKYO)
    day, mod = t // 1440, t % 1440
    p0, p1 = price_at(day, mod, x, 595), price_at(day, mod, x, 655)
    me_q, me_o = [], []
    for k, a in p0.items():
        d = date.fromordinal(int(k) + E)
        if got.get(d) == "ME" and d not in hol and d.weekday() < 5 and k in p1 and d <= END:
            (me_q if d.month in (3, 6, 9, 12) else me_o).append(a / p1[k] - 1)
    res["gt_quarter_end_measurement"] = {"quarter_end_ME_post_gross": hac(me_q), "other_ME_post_gross": hac(me_o)}
    json.dump(res, open(os.path.join(OUT, "round29_ecb_fix.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "post_reform_net_eurusd", "verdict", "gt_quarter_end_measurement")}, indent=1, default=str))


if __name__ == "__main__":
    main()
