"""Round 20 (PREREGISTRATION.md A34, A34a): the Gotobi effect on unseen 2002-07 JPY-cross data (GC), the build's exit time
(GX) and disaster stop (GS).

    python3 run_round20.py            -> results/round20_gotobi_confirm.json (A34a rule on)
    A34A=0 python3 run_round20.py     -> results/round20_gotobi_confirm_first_run.json (the first, pre-amendment run)
"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import numpy as np

import vstats as vs
from data_calendar import gotobi_days, japan_holidays
from data_minutes import local, price_at
from run_round11 import TOKYO

OUT = os.path.join(os.path.dirname(__file__), "results")
E = date(1970, 1, 1).toordinal()
CROSSES = ("EURJPY", "GBPJPY", "AUDJPY", "CHFJPY", "CADJPY", "NZDJPY")
LO, HI = date(2002, 1, 1), date(2007, 12, 31)
EXITS = {"10:25": 625, "10:55": 655, "11:30": 690, "12:00": 720, "15:00": 900}
CLEAN = os.environ.get("A34A", "1") == "1"  # A34a data-integrity rule (the first run had it off)
DROPPED = []


def hac(v):
    x = np.array(v, dtype=float)
    t = vs.nw_t(list(x), 5)
    return {"n": int(len(x)), "mean_bps": float(x.mean() * 1e4), "sd_bps": float(x.std(ddof=1) * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t),
            "mean_over_sd": float(x.mean() / x.std(ddof=1))}


def welch(a, b):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    t = float((a.mean() - b.mean()) / se)
    return {"diff_bps": float((a.mean() - b.mean()) * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t)}


def cross_windows(sym, hol):
    """{window: {date: signed gross return}}: short 09:55 -> each exit, and long 09:00 -> 09:55."""
    t, x = local(sym, range(2002, 2008), TOKYO)
    if not len(t):
        return {}
    day, mod = t // 1440, t % 1440
    if CLEAN:  # A34a: drop symbol-years with > 100 one-minute moves beyond +/-3%
        yr = np.array([date.fromordinal(int(v) + E).year for v in day])
        big = np.r_[False, np.abs(np.diff(np.log(x[:, 3]))) > 0.03]
        drop = [y for y in set(yr.tolist()) if big[yr == y].sum() > 100]
        if drop:
            keep = ~np.isin(yr, drop)
            t, x, day, mod = t[keep], x[keep], day[keep], mod[keep]
            DROPPED.append((sym, sorted(drop)))
    px = {m: price_at(day, mod, x, m) for m in {540, 595, *EXITS.values()}}
    out = {w: {} for w in [*EXITS, "PRE"]}
    for k, p0 in px[595].items():
        d = date.fromordinal(int(k) + E)
        if d.weekday() >= 5 or d in hol or not (LO <= d <= HI):
            continue
        for w, m in EXITS.items():
            if k in px[m] and not (CLEAN and abs(p0 / px[m][k] - 1) > 0.05):
                out[w][d] = p0 / px[m][k] - 1
        if k in px[540] and not (CLEAN and abs(p0 / px[540][k] - 1) > 0.05):
            out["PRE"][d] = p0 / px[540][k] - 1
    return out


def basket(per, w, min_n=3):
    days = sorted({d for s in per for d in per[s].get(w, {})})
    out = {}
    for d in days:
        v = [per[s][w][d] for s in per if d in per[s].get(w, {})]
        if len(v) >= min_n:
            out[d] = float(np.mean(v))
    return out


def stop_study(got, hol):
    """GS: USDJPY 2014-26, short 09:55 -> 10:55 on Gotobi days with a buy stop at entry + k bps."""
    t, x = local("USDJPY", range(2014, 2027), TOKYO)
    day, mod = t // 1440, t % 1440
    p0, p1 = price_at(day, mod, x, 595), price_at(day, mod, x, 655)
    ins = (mod >= 595) & (mod < 655)
    dk, xi = day[ins], x[ins]
    st = np.r_[0, np.nonzero(np.diff(dk))[0] + 1]
    en = np.r_[st[1:], len(dk)]
    res = {}
    rows = []
    for a, b in zip(st, en):
        k = int(dk[a])
        d = date.fromordinal(k + E)
        if d not in got or d in hol or d.weekday() >= 5 or not (date(2014, 1, 1) <= d <= date(2026, 9, 18)) or k not in p0 or k not in p1:
            continue
        rows.append((p0[k], p1[k], xi[a:b, 0], xi[a:b, 1]))
    for kb in (None, 20, 30, 50, 80):
        r, hit = [], 0
        for e0, e1, o, h in rows:
            out = e1
            if kb is not None:
                s = e0 * (1 + kb / 1e4)
                j = np.nonzero(h >= s)[0]
                if len(j):
                    out = max(s, o[j[0]])
                    hit += 1
            r.append(e0 / out - 1 - 1e-4)
        r = np.array(r)
        res["none" if kb is None else f"{kb} bps"] = {"net_mean_bps": float(r.mean() * 1e4), "worst_bps": float(r.min() * 1e4), "share_stopped": hit / len(r), "n": len(r)}
    base = res["none"]["net_mean_bps"]
    ok = [kb for kb in (20, 30, 50, 80) if res[f"{kb} bps"]["net_mean_bps"] >= 0.95 * base]
    res["decision"] = f"{ok[0]} bps" if ok else "no stop (EA guard only)"
    return res


def main():
    got, hol = gotobi_days(2002, 2026), japan_holidays(2002, 2026)
    per = {}
    for s in CROSSES:
        w = cross_windows(s, hol)
        if w:
            per[s] = w
        print("GC", s, {k: len(v) for k, v in w.items()}, flush=True)
    b = basket(per, "10:55")
    g = [v for d, v in b.items() if d in got]
    o = [v for d, v in b.items() if d not in got]
    eur = [v - 1e-4 for d, v in per["EURJPY"]["10:55"].items() if d in got]
    prim = {"C1": hac(g), "C2": welch(g, o), "C3": hac(eur)}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    c12 = [prim[k]["p_holm"] < 0.05 for k in ("C1", "C2")]
    verdict = "CONFIRMED" if all(c12) else "PARTIAL" if any(c12) else "NOT CONFIRMED"
    res = {"primary": prim, "verdict": verdict, "eurjpy_may_join_build": bool(prim["C3"]["p_holm"] < 0.05)}
    res["per_cross"] = {s: {"gotobi": hac([v for d, v in w["10:55"].items() if d in got]), "other": hac([v for d, v in w["10:55"].items() if d not in got])}
                        for s, w in per.items() if len(w["10:55"]) > 50}
    res["month_end_vs_other_gotobi"] = {"ME": hac([v for d, v in b.items() if got.get(d) == "ME"]), "510": hac([v for d, v in b.items() if got.get(d) == "510"])}
    pre = basket(per, "PRE")
    res["pre_fix_long_basket"] = {"gotobi": hac([v for d, v in pre.items() if d in got]), "other": hac([v for d, v in pre.items() if d not in got])}
    # GX
    gx = {w: hac([v for d, v in basket(per, w).items() if d in got]) for w in EXITS}
    switch = gx["11:30"]["mean_over_sd"] > gx["10:55"]["mean_over_sd"] and gx["11:30"]["t"] >= 2
    res["GX_exit"] = {"by_exit": gx, "decision": "11:30" if switch else "10:55"}
    # GS
    res["GS_stop"] = stop_study(got, hol)
    res["a34a_clean"] = CLEAN
    res["a34a_dropped_symbol_years"] = DROPPED
    name = "round20_gotobi_confirm.json" if CLEAN else "round20_gotobi_confirm_first_run.json"
    json.dump(res, open(os.path.join(OUT, name), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "verdict", "eurjpy_may_join_build")}, indent=1, default=str))
    for s, v in res["per_cross"].items():
        print(s, {k: (round(q["mean_bps"], 2), round(q["t"], 2), q["n"]) for k, q in v.items()})
    print("ME/510", {k: (round(q["mean_bps"], 2), round(q["t"], 2), q["n"]) for k, q in res["month_end_vs_other_gotobi"].items()})
    print("PRE", {k: (round(q["mean_bps"], 2), round(q["t"], 2), q["n"]) for k, q in res["pre_fix_long_basket"].items()})
    print("GX", {k: (round(q["mean_bps"], 2), round(q["t"], 2), round(q["mean_over_sd"], 3)) for k, q in gx.items()}, res["GX_exit"]["decision"])
    print("GS", json.dumps(res["GS_stop"]))


if __name__ == "__main__":
    main()
