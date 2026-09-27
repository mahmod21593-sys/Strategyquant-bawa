"""Round 33 (PREREGISTRATION.md A47): the 0DTE regime as a natural experiment for intraday reversal on US500/US100.

    python3 run_round33.py   -> results/round33_0dte.json
"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import numpy as np

import run_family_a as fa
import vstats as vs
from data_histdata import NY
from data_minutes import price_at
from run_round24 import clean_local, to_battery

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 13974
E = date(1970, 1, 1).toordinal()
PRE_END, POST_START, END = date(2022, 4, 29), date(2022, 11, 14), date(2026, 9, 18)
MID = date(2024, 7, 1)
COST = 3.0e-4


def hac(v):
    x = np.array(v, dtype=float)
    t = vs.nw_t(list(x), 5)
    return {"n": int(len(x)), "mean_bps": float(x.mean() * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t)}


def welch(a, b):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    t = float((a.mean() - b.mean()) / se)
    return {"diff_bps": float((a.mean() - b.mean()) * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t), "n": [int(len(a)), int(len(b))]}


def day_rows(sym):
    """{date: {'r_am@m': ..., 'r_pm@m': ...}} for entry marks 13:00, 14:00, 15:00; exit 15:55."""
    t, x = clean_local(sym, range(2013, 2027), NY)
    day, mod = t // 1440, t % 1440
    marks = (570, 780, 840, 900, 955)
    px = {m: price_at(day, mod, x, m, prefer_open=(m == 570)) for m in marks}
    out = {}
    for k, p0 in px[570].items():
        d = date.fromordinal(int(k) + E)
        if d.weekday() >= 5 or d > END or any(k not in px[m] for m in marks):
            continue
        row = {}
        for m in (780, 840, 900):
            am, pm = px[m][k] / p0 - 1, px[955][k] / px[m][k] - 1
            if abs(am) > 0.12 or abs(pm) > 0.12:
                row = None
                break
            row[m] = (am, pm)
        if row:
            out[d] = row
    return out


def rule(rows, m, cond):
    """{date: gross reversal P&L} for entry mark m; cond 'ALL' or 'S1' (|r_am| > 1 sigma20)."""
    ds = sorted(rows)
    am = [rows[d][m][0] for d in ds]
    out = {}
    for i, d in enumerate(ds):
        a, p = rows[d][m]
        if a == 0:
            continue
        if cond == "S1":
            if i < 20:
                continue
            s = float(np.std(am[i - 20:i], ddof=1))
            if not (s > 0 and abs(a) > s):
                continue
        out[d] = float(-np.sign(a) * p)
    return out


def main():
    data = {"US500": day_rows("SPXUSD"), "US100": day_rows("NSXUSD")}
    for k, v in data.items():
        print("0DTE", k, len(v), flush=True)
    pre = lambda g: {d: v for d, v in g.items() if d <= PRE_END}
    post = lambda g: {d: v for d, v in g.items() if d >= POST_START}
    g5, g1 = rule(data["US500"], 840, "ALL"), rule(data["US100"], 840, "ALL")
    z1 = hac([v - COST for _, v in sorted(post(g5).items())])
    z2 = welch(list(post(g5).values()), list(pre(g5).values()))
    z3 = hac([v - COST for _, v in sorted(post(g1).items())])
    prim = {"Z1": z1, "Z2": z2, "Z3": z3}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    halves = (float(np.mean([v - COST for d, v in post(g5).items() if d < MID]) * 1e4),
              float(np.mean([v - COST for d, v in post(g5).items() if d >= MID]) * 1e4))
    res = {"primary": prim, "z1_post_halves_net_bps": halves}
    edge = prim["Z1"]["p_holm"] < 0.05 and all(h > 0 for h in halves) and prim["Z3"]["mean_bps"] > 0
    res["verdict"] = "EDGE" if edge else "REGIME SHIFT, NOT TRADEABLE" if prim["Z2"]["p_holm"] < 0.05 else "NO EDGE"
    # descriptive: the full grid, gross, by period; am/pm correlation by period
    desc = {}
    per = {}
    for mk, rows in data.items():
        for m in (780, 840, 900):
            for cond in ("ALL", "S1"):
                g = rule(rows, m, cond)
                key = f"{mk}|{m // 60:02d}{m % 60:02d}|{cond}"
                desc[key] = {"pre_gross": hac(list(pre(g).values())), "post_gross": hac(list(post(g).values()))}
                per[key] = {d: v - COST for d, v in g.items() if d <= PRE_END or d >= POST_START}
        for m in (780, 840, 900):
            for lab, sel in (("pre", lambda d: d <= PRE_END), ("post", lambda d: d >= POST_START)):
                a = [rows[d][m][0] for d in rows if sel(d)]
                p_ = [rows[d][m][1] for d in rows if sel(d)]
                desc[f"{mk}|corr_am_pm|{m}|{lab}"] = float(np.corrcoef(a, p_)[0, 1])
    res["descriptive"] = desc
    # N3 risk check
    from run_noise_area import run as noise_run
    n3 = {d: v for d, v in noise_run("N3", path=False)[0]}
    res["N3_risk_check_bps_per_day"] = {"pre": hac([v / 1e4 for d, v in n3.items() if d <= PRE_END]),
                                        "post": hac([v / 1e4 for d, v in n3.items() if d >= POST_START])}
    res["battery"] = to_battery(per, "ZD", date(2013, 1, 1), POST_START, 2016)
    json.dump(res, open(os.path.join(OUT, "round33_0dte.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "z1_post_halves_net_bps", "verdict", "N3_risk_check_bps_per_day")}, indent=1, default=str))
    for k, v in desc.items():
        if isinstance(v, dict):
            print(k, "pre", round(v["pre_gross"]["mean_bps"], 2), round(v["pre_gross"]["t"], 2), "| post", round(v["post_gross"]["mean_bps"], 2),
                  round(v["post_gross"]["t"], 2), v["post_gross"]["n"])
        else:
            print(k, round(v, 3))


if __name__ == "__main__":
    main()
