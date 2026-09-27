"""Round 24 (PREREGISTRATION.md A38).

    python3 run_round24.py PB   PBoC-fix reaction momentum in AUD/NZD/JPY (natural experiment, 2015-08-11) -> results/round24_pb.json
    python3 run_round24.py RV   gold-silver relative value (ratio z-score)                                  -> results/round24_rv.json
    python3 run_round24.py FG   festival gold demand (Dhanteras/Diwali)                                     -> results/round24_fg.json
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
from data_audit import spike_mask
from data_fred import series as fred
from data_histdata import NY
from data_minutes import group, local, price_at
from run_round10 import finish, weekday_calendar
from run_round21 import SHANGHAI

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
fa.N_TRIALS = 13857
E = date(1970, 1, 1).toordinal()
END = date(2026, 9, 18)
REFORM = date(2015, 8, 11)


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
    t = float(x.mean() / (x.std(ddof=1) / math.sqrt(len(x)))) if len(x) > 2 else math.nan
    return {"n": int(len(x)), "mean_bps": float(x.mean() * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t)}


def welch(a, b, sign=1):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    t = float((a.mean() - b.mean()) / se)
    return {"diff_bps": float((a.mean() - b.mean()) * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t, sign), "n": [int(len(a)), int(len(b))]}


def to_battery(per, key, start, split, first_wf):
    cal = weekday_calendar(start, END)
    ci = {d: i for i, d in enumerate(cal)}
    names = sorted(per)
    X = np.zeros((len(cal), len(names)))
    for j, n in enumerate(names):
        for d, v in per[n].items():
            if d in ci:
                X[ci[d], j] = v
    bat = finish(key, X, None, names, cal, split, first_wf)
    return {k: bat["raw"][k] for k in ("spa_validation", "pbo_full_sample", "walk_forward_top5", "verdict", "romano_wolf_significant_5pct")}


# ---------------------------------------------------------------- PB

def pb_rows(sym, y0):
    """[(date, jump, reaction 09:20->10:15, reaction 09:20->11:15)] on weekdays, Beijing clock, |window| < 5%."""
    t, x = clean_local(sym, range(y0, 2027), SHANGHAI)
    day, mod = t // 1440, t % 1440
    px = {m: price_at(day, mod, x, m) for m in (550, 560, 615, 675)}
    out = []
    for k, p20 in px[560].items():
        d = date.fromordinal(int(k) + E)
        if d.weekday() >= 5 or d > END or any(k not in px[m] for m in (550, 615, 675)):
            continue
        j = p20 / px[550][k] - 1
        r1, r2 = px[615][k] / p20 - 1, px[675][k] / p20 - 1
        if max(abs(j), abs(r1), abs(r2)) < 0.05:
            out.append((d, j, r1, r2))
    return out


def family_pb():
    import holidays
    cn = set(holidays.China(years=range(2005, 2027)))
    res, per = {}, {}
    data = {}
    for sym, y0 in (("AUDUSD", 2005), ("NZDUSD", 2005), ("USDJPY", 2005)):
        rows = pb_rows(sym, y0)
        data[sym] = rows
        print("PB", sym, len(rows), flush=True)
        # grid: filter x exit, daily pnl (net of 1 bp)
        jumps = [r[1] for r in rows]
        sig20 = {}
        for i in range(20, len(rows)):
            sig20[rows[i][0]] = float(np.std(jumps[i - 20:i], ddof=1))
        for flt in ("ALL", "S1"):
            for exn, ri in (("x1015", 2), ("x1115", 3)):
                per[f"{sym}|{flt}|{exn}"] = {r[0]: math.copysign(1, r[1]) * r[ri] - 1e-4 for r in rows
                                             if r[1] != 0 and r[0] >= date(2005, 1, 1)
                                             and (flt == "ALL" or (r[0] in sig20 and abs(r[1]) > sig20[r[0]]))}
    rows = data["AUDUSD"]
    fix = lambda d: d not in cn
    post = [r for r in rows if r[0] > REFORM and fix(r[0]) and r[1] != 0]
    pre = [r for r in rows if r[0] < REFORM and fix(r[0]) and r[1] != 0]
    hol = [r for r in rows if r[0] > REFORM and not fix(r[0]) and r[1] != 0]
    net = lambda rs: [math.copysign(1, r[1]) * r[2] - 1e-4 for r in rs]
    gross = lambda rs: [math.copysign(1, r[1]) * r[2] for r in rs]
    prim = {"P1": hac(net(post)), "P2": welch(gross(post), gross(pre)), "P3": welch(gross(post), gross(hol))}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    h1 = [v for r, v in zip(post, net(post)) if r[0] <= date(2020, 12, 31)]
    h2 = [v for r, v in zip(post, net(post)) if r[0] > date(2020, 12, 31)]
    res["primary"] = prim
    res["halves_net_bps"] = (float(np.mean(h1) * 1e4), float(np.mean(h2) * 1e4))
    edge = prim["P1"]["p_holm"] < 0.05 and all(h > 0 for h in res["halves_net_bps"])
    mech = prim["P2"]["p_holm"] < 0.05 or prim["P3"]["p_holm"] < 0.05
    res["verdict"] = "EDGE" if edge else "MECHANISM ONLY" if mech else "NO EDGE"
    res["descriptive"] = {"post_reform_gross": hac(gross(post)), "pre_reform_gross": hac(gross(pre)), "holiday_placebo_gross": hac(gross(hol)),
                          "jump_size_bps_post": float(np.mean([abs(r[1]) for r in post]) * 1e4),
                          "jump_size_bps_pre": float(np.mean([abs(r[1]) for r in pre]) * 1e4)}
    res["battery"] = to_battery(per, "PB", date(2005, 1, 1), date(2021, 1, 1), 2017)
    json.dump(res, open(os.path.join(OUT, "round24_pb.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "halves_net_bps", "verdict", "descriptive")}, indent=1, default=str))


# ---------------------------------------------------------------- RV

def rv_bars(sym):
    """Daily 16:45-NY closes from minute data with spike bars dropped (A35a), {date: close}."""
    path = os.path.join(R9, f"rv24_{sym}.npz")
    if os.path.exists(path):
        p = np.load(path)
        return {date.fromordinal(int(a)): float(b) for a, b in zip(p["d"], p["c"])}
    t, x = clean_local(sym, range(2009, 2027), NY)
    mod = t % 1440
    k = (mod < 1005) | (mod >= 1140)
    t, x = t[k], x[k]
    keys, o, h, l, c, n, _ = group((t + 300) // 1440, x)
    ok = (n >= 600) & np.array([date.fromordinal(int(v) + E).weekday() < 5 for v in keys])
    d = [int(v) + E for v in keys[ok]]
    np.savez(path, d=np.array(d), c=c[ok])
    return {date.fromordinal(a): float(b) for a, b in zip(d, c[ok])}


def rv_trades(dates, au, ag, L, k, exit_mode):
    """Simulate the spread book. Signal z at close t; enter at close t+1; exit at the first close with |z| < 0.5
    (Z mode, capped at 20 trading days) or after exactly 20 trading days (T20). Returns trade dicts."""
    lr = np.log(np.array([au[d] for d in dates]) / np.array([ag[d] for d in dates]))
    n = len(dates)
    z = np.full(n, np.nan)
    for i in range(L, n):
        w = lr[i - L:i + 1]
        sd = w.std(ddof=1)
        if sd > 0:
            z[i] = (lr[i] - w.mean()) / sd
    rau = np.r_[0.0, np.diff(np.array([au[d] for d in dates])) / np.array([au[d] for d in dates])[:-1]]
    rag = np.r_[0.0, np.diff(np.array([ag[d] for d in dates])) / np.array([ag[d] for d in dates])[:-1]]
    trades = []
    i = L
    while i < n - 2:
        if not np.isfinite(z[i]) or abs(z[i]) <= k:
            i += 1
            continue
        side = 1 if z[i] > k else -1  # +1: long silver, short gold
        e = i + 1  # enter at the next close
        j = e + 1
        while j < n - 1:
            held = j - e
            if (exit_mode == "Z" and (not np.isfinite(z[j]) or abs(z[j]) < 0.5)) or held >= 20:
                break
            j += 1
        spread = 0.5 * side * float(np.sum(rag[e + 1:j + 1] - rau[e + 1:j + 1]))
        caldays = (dates[j] - dates[e]).days
        net = spread - 15e-4 - 0.04 / 365 * caldays
        trades.append({"entry": dates[e], "exit": dates[j], "side": side, "gross": spread, "net": net, "days": j - e})
        i = j
    return trades


def family_rv():
    au, ag = rv_bars("XAUUSD"), rv_bars("XAGUSD")
    dates = sorted(set(au) & set(ag))
    dates = [d for d in dates if date(2010, 1, 1) <= d <= END]
    print("RV common days", len(dates), dates[0], dates[-1], flush=True)
    res, per = {}, {}
    grid = {}
    for L in (30, 60, 120):
        for k in (1.5, 2.0, 2.5):
            for ex in ("Z", "T20"):
                tr = rv_trades(dates, au, ag, L, k, ex)
                grid[(L, k, ex)] = tr
                pnl = {}
                for t_ in tr:
                    pnl[t_["exit"]] = pnl.get(t_["exit"], 0.0) + t_["net"]
                per[f"RV|L{L}|k{k:g}|{ex}"] = pnl
    tr = grid[(60, 2.0, "Z")]
    prim = {"RV1": ttest([t_["net"] for t_ in tr]), "RV2": ttest([t_["gross"] for t_ in tr])}
    holm = vs.holm({k_: v["p_one_sided"] for k_, v in prim.items()})
    for k_ in prim:
        prim[k_]["p_holm"] = holm[k_]
    h1 = [t_["net"] for t_ in tr if t_["entry"] < date(2018, 1, 1)]
    h2 = [t_["net"] for t_ in tr if t_["entry"] >= date(2018, 1, 1)]
    res["primary"] = prim
    res["halves_net_bps"] = (float(np.mean(h1) * 1e4) if h1 else None, float(np.mean(h2) * 1e4) if h2 else None)
    edge = prim["RV1"]["p_holm"] < 0.05 and all(h is not None and h > 0 for h in res["halves_net_bps"])
    res["verdict"] = "EDGE" if edge else "REVERSION, NOT TRADEABLE" if prim["RV2"]["p_holm"] < 0.05 else "NO EDGE"
    res["primary_trades"] = {"n": len(tr), "mean_days_held": float(np.mean([t_["days"] for t_ in tr])),
                             "by_side_gross_bps": {"long_silver": ttest([t_["gross"] for t_ in tr if t_["side"] == 1]),
                                                   "short_silver": ttest([t_["gross"] for t_ in tr if t_["side"] == -1])}}
    res["grid_net_mean_bps"] = {f"L{L}|k{k_:g}|{ex}": (round(float(np.mean([t_["net"] for t_ in v]) * 1e4), 1), len(v))
                                for (L, k_, ex), v in grid.items() if v}
    res["battery"] = to_battery(per, "RV", date(2010, 1, 1), date(2019, 1, 1), 2013)
    json.dump(res, open(os.path.join(OUT, "round24_rv.json"), "w"), indent=1, default=str)
    print(json.dumps({k_: res[k_] for k_ in ("primary", "halves_net_bps", "verdict", "primary_trades", "grid_net_mean_bps")}, indent=1, default=str))


# ---------------------------------------------------------------- FG

def family_fg():
    import holidays
    from run_round22 import daily_1645
    ind = holidays.India(years=range(2010, 2027))
    diwali = sorted(d for d, n in ind.items() if "Diwali" in n or "Deepavali" in n)
    px = daily_1645("XAUUSD")
    days = sorted(px)
    us3 = {(d.year, d.month): v / 100 for d, v in fred("IR3TIB01USM156N")}
    res = {"events": []}
    pre_ev, post_ev = [], []
    for dw in diwali:
        if not (2011 <= dw.year <= 2025):
            continue
        dh = dw - timedelta(days=2)  # Dhanteras
        upto = [d for d in days if d <= dh]
        after = [d for d in days if d > dw]
        if len(upto) < 17 or len(after) < 16:
            continue
        w = upto[-16:]  # close before the window + 15 weekdays
        g = px[w[-1]] / px[w[0]] - 1
        fin = ((us3.get((dw.year, dw.month), 0.04) + 0.02) / 365) * (w[-1] - w[0]).days
        net = g - 2.5e-4 - fin
        ga = px[after[14]] / px[after[0]] - 1
        pre_ev.append((dw.year, g, net))
        post_ev.append(ga)
        res["events"].append({"diwali": str(dw), "gross_pct": round(g * 100, 2), "net_pct": round(net * 100, 2), "after_pct": round(ga * 100, 2)})
    prim = ttest([e[2] for e in pre_ev])
    res["F1_net"] = prim
    res["gross"] = ttest([e[1] for e in pre_ev])
    res["after_diwali_15d_gross"] = ttest(post_ev)
    h1 = [e[2] for e in pre_ev if e[0] <= 2017]
    h2 = [e[2] for e in pre_ev if e[0] >= 2018]
    res["halves_net_pct"] = (float(np.mean(h1) * 100), float(np.mean(h2) * 100))
    res["verdict"] = "EDGE" if prim["p_one_sided"] < 0.05 and all(h > 0 for h in res["halves_net_pct"]) else "NO EDGE"
    json.dump(res, open(os.path.join(OUT, "round24_fg.json"), "w"), indent=1, default=str)
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    {"PB": family_pb, "RV": family_rv, "FG": family_fg}[sys.argv[1]]()
