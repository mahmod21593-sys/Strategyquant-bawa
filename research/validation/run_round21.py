"""Round 21 (PREREGISTRATION.md A35, A35a: audited spike bars are dropped).

    python3 run_round21.py RN   round-number barriers in FX and gold (Osler 2003; Aggarwal & Lucey 2007) -> results/round21_rn.json
    python3 run_round21.py SG   the Shanghai Gold Benchmark auctions (natural experiment, 2016-04-19)     -> results/round21_sg.json
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date
from zoneinfo import ZoneInfo

import numpy as np

import run_family_a as fa
import vstats as vs
from data_audit import spike_mask
from data_minutes import local, price_at
from run_round10 import finish, weekday_calendar
from run_round11 import LONDON

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 13802
E = date(1970, 1, 1).toordinal()
END = date(2026, 9, 18)
FX = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD")
COST = {**{s: 1.0e-4 for s in FX}, "XAUUSD": 2.5e-4, "XAGUSD": 5.0e-4}
H = 120


def hac(v):
    x = np.array(v, dtype=float)
    t = vs.nw_t(list(x), 5)
    return {"n": int(len(x)), "mean_bps": float(x.mean() * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t)}


# ---------------------------------------------------------------- RN

def grids(sym):
    """{grid name: (spacing, [offsets])} in price units."""
    if sym == "XAUUSD":
        return {"R10": (10.0, [0.0]), "R50": (50.0, [0.0]), "A10": (10.0, [3.3, 6.7])}
    if sym == "XAGUSD":
        return {"R10": (0.5, [0.0]), "R50": (1.0, [0.0]), "A10": (0.5, [0.165, 0.335])}
    pip = 0.01 if sym.endswith("JPY") else 0.0001
    return {"R10": (50 * pip, [0.0]), "R50": (100 * pip, [0.0]), "A10": (50 * pip, [17 * pip, 33 * pip])}
# names: R10 = the primary round grid (FX Round50, gold Round10), R50 = the coarser round grid (FX Round100, gold Round50),
# A10 = the arbitrary control for R10


def touch_events(day, mod, xo, xh, xl, xc, spacing, offset, s0, s1, shift=0.0):
    """First touch per (session day, level, side) of the levels offset + n*spacing, each scaled by (1 + side*shift).
    Returns arrays (row index, level price, side) with side +1 = approached from below."""
    rows, levels, sides = [], [], []
    ok = (mod >= s0) & (mod < s1)
    prev_c = np.r_[np.nan, xc[:-1]]
    same_day = np.r_[False, day[1:] == day[:-1]]
    ok &= same_day & np.isfinite(prev_c)
    idx = np.nonzero(ok)[0]
    for side in (1, -1):
        # from below: the level T = L * (1 + shift) lies in (prev close, high]; from above: in [low, prev close)
        m = 1 + side * shift
        if side == 1:
            lo_n = np.floor((prev_c[idx] / m - offset) / spacing) + 1
            hi_n = np.floor((xh[idx] / m - offset) / spacing)
        else:
            lo_n = np.ceil((xl[idx] / m - offset) / spacing)
            hi_n = np.ceil((prev_c[idx] / m - offset) / spacing) - 1
        has = hi_n >= lo_n
        for i, a, b in zip(idx[has], lo_n[has], hi_n[has]):
            for n in range(int(a), int(b) + 1):
                rows.append(i)
                levels.append((offset + n * spacing) * m)
                sides.append(side)
    rows, levels, sides = np.array(rows, dtype=np.int64), np.array(levels), np.array(sides)
    if not len(rows):
        return rows, levels, sides
    o = np.argsort(rows, kind="stable")
    rows, levels, sides = rows[o], levels[o], sides[o]
    key = np.stack([day[rows], np.round(levels / spacing * 1000).astype(np.int64), sides], 1)
    _, first = np.unique(key, axis=0, return_index=True)
    first = np.sort(first)
    return rows[first], levels[first], sides[first]


def outcomes(rows, levels, direction, k, day, mod, xh, xl, xc, cost, horizon_end=1245):
    """Trades entered at `levels` on bar `rows` in `direction` (+1 long) with take-profit and stop k (fraction) and a
    120-minute / 20:45 timeout. Returns (net pnl, outcome: +1 target first, -1 stop first, 0 timeout, 2 tie)."""
    n = len(rows)
    if not n:
        return np.zeros(0), np.zeros(0, dtype=int)
    N = len(xh)
    fwd = rows[:, None] + np.arange(1, H + 1)[None, :]
    valid = fwd < N
    fwd_c = np.minimum(fwd, N - 1)
    valid &= (day[fwd_c] == day[rows][:, None]) & (mod[fwd_c] < horizon_end)
    tp = levels * (1 + direction * k)
    sl = levels * (1 - direction * k)
    hh, ll = np.where(valid, xh[fwd_c], np.nan), np.where(valid, xl[fwd_c], np.nan)
    hit_tp = np.where(direction[:, None] == 1, hh >= tp[:, None], ll <= tp[:, None])
    hit_sl = np.where(direction[:, None] == 1, ll <= sl[:, None], hh >= sl[:, None])
    # adverse move already inside the entry bar = stop first (conservative)
    adverse0 = np.where(direction == 1, xl[rows] <= sl, xh[rows] >= sl)
    any_tp, any_sl = hit_tp.any(1), hit_sl.any(1)
    ftp = np.where(any_tp, hit_tp.argmax(1), H + 1)
    fsl = np.where(any_sl, hit_sl.argmax(1), H + 1)
    last = np.where(valid.any(1), valid.sum(1) - 1, 0)
    c_end = xc[fwd_c[np.arange(n), last]]
    c_end = np.where(valid.any(1), c_end, xc[rows])
    out = np.zeros(n, dtype=int)
    pnl = direction * (c_end / levels - 1)
    tie = any_tp & any_sl & (ftp == fsl)
    tpw = any_tp & (ftp < fsl)
    slw = any_sl & (fsl < ftp)
    out[tpw], pnl[tpw] = 1, k
    out[slw], pnl[slw] = -1, -k
    out[tie], pnl[tie] = 2, -k
    out[adverse0], pnl[adverse0] = -1, -k
    return pnl - cost, out


def rn_instrument(sym):
    years = range(2009 if sym == "XAUUSD" else 2010 if sym == "XAGUSD" else 2003, 2027)
    t, x = local(sym, years, LONDON)
    keep = ~spike_mask(x, 0.02 if sym in ("XAUUSD", "XAGUSD") else 0.01)  # A35a
    t, x = t[keep], x[keep]
    day, mod = t // 1440, t % 1440
    xo, xh, xl, xc = x[:, 0], x[:, 1], x[:, 2], x[:, 3]
    s0, s1 = (60, 1200) if sym in ("XAUUSD", "XAGUSD") else (420, 1200)
    cost = COST[sym]
    res = {}
    for g, (sp, offs) in grids(sym).items():
        for rule in ("fade", "follow"):
            R, L, S = [], [], []
            for o in offs:
                r, lv, sd = touch_events(day, mod, xo, xh, xl, xc, sp, o, s0, s1, shift=3e-4 if rule == "follow" else 0.0)
                R.append(r)
                L.append(lv)
                S.append(sd)
            r, lv, sd = np.concatenate(R), np.concatenate(L), np.concatenate(S)
            direction = -sd if rule == "fade" else sd
            d = np.array([date.fromordinal(int(v) + E) for v in day[r]])
            for k in (10e-4, 20e-4):
                pnl, oc = outcomes(r, lv, direction, k, day, mod, xh, xl, xc, cost)
                res[(g, int(round(k * 1e4)), rule)] = {"dates": d, "pnl": pnl, "out": oc, "side": sd}
    print("RN", sym, {f"{g}|k{k}|{r}": len(v["pnl"]) for (g, k, r), v in res.items()}, flush=True)
    return res


def freq_diff(dr, da, reps=2000, seed=11):
    """Reversal-first frequency (target-first among decided events), round minus arbitrary, with a day-block bootstrap.
    dr / da: {date: (n target-first, n decided)}."""
    days = sorted(set(dr) | set(da))
    a = np.array([dr.get(d, (0, 0)) for d in days], dtype=float)
    b = np.array([da.get(d, (0, 0)) for d in days], dtype=float)
    est = a[:, 0].sum() / a[:, 1].sum() - b[:, 0].sum() / b[:, 1].sum()
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(reps):
        i = rng.integers(0, len(days), len(days))
        bs.append(a[i, 0].sum() / a[i, 1].sum() - b[i, 0].sum() / b[i, 1].sum())
    bs = np.array(bs)
    se = float(bs.std(ddof=1))
    return {"round": float(a[:, 0].sum() / a[:, 1].sum()), "arbitrary": float(b[:, 0].sum() / b[:, 1].sum()), "diff": float(est),
            "se": se, "z": float(est / se), "p_one_sided": vs.p_one_sided(est / se), "n_round": int(a[:, 1].sum()), "n_arb": int(b[:, 1].sum())}


def per_day(ev, what="freq"):
    out = {}
    for d, p, o in zip(ev["dates"], ev["pnl"], ev["out"]):
        if what == "freq":
            a, b = out.get(d, (0, 0))
            if o in (1, -1):
                out[d] = (a + (o == 1), b + 1)
        else:
            out[d] = out.get(d, 0.0) + p
    return out


def merge_days(dicts, what):
    out = {}
    for dd in dicts:
        for d, v in dd.items():
            if what == "freq":
                a, b = out.get(d, (0, 0))
                out[d] = (a + v[0], b + v[1])
            else:
                out[d] = out.get(d, 0.0) + v
    return out


def family_rn():
    data = {s: rn_instrument(s) for s in FX + ("XAUUSD", "XAGUSD")}
    res = {}
    # RN1 / RN2: Osler's first prediction on the fade events (k = 10 bps)
    fx_r = merge_days([per_day(data[s][("R10", 10, "fade")]) for s in FX], "freq")
    fx_a = merge_days([per_day(data[s][("A10", 10, "fade")]) for s in FX], "freq")
    au_r, au_a = per_day(data["XAUUSD"][("R10", 10, "fade")]), per_day(data["XAUUSD"][("A10", 10, "fade")])
    rn1, rn2 = freq_diff(fx_r, fx_a), freq_diff(au_r, au_a)
    fx_p = merge_days([per_day(data[s][("R10", 10, "fade")], "pnl") for s in FX], "pnl")
    au_p = per_day(data["XAUUSD"][("R10", 10, "fade")], "pnl")
    rn3, rn4 = hac([v for _, v in sorted(fx_p.items())]), hac([v for _, v in sorted(au_p.items())])
    prim = {"RN1": rn1, "RN2": rn2, "RN3": rn3, "RN4": rn4}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]

    def halves(rows, cut):
        a = [v for d, v in rows.items() if d < cut]
        b = [v for d, v in rows.items() if d >= cut]
        return float(np.mean(a) * 1e4), float(np.mean(b) * 1e4)
    prim["RN3"]["halves_bps"] = halves(fx_p, date(2015, 1, 1))
    prim["RN4"]["halves_bps"] = halves(au_p, date(2018, 1, 1))
    edge = [k for k in ("RN3", "RN4") if prim[k]["p_holm"] < 0.05 and all(h > 0 for h in prim[k]["halves_bps"])]
    mech = any(prim[k]["p_holm"] < 0.05 for k in ("RN1", "RN2"))
    res["primary"] = prim
    res["verdict"] = "EDGE" if edge else "MECHANISM ONLY" if mech else "NO EDGE"
    # Osler's second prediction: follow continuation, round minus arbitrary
    res["follow_continuation_fx"] = freq_diff(merge_days([per_day(data[s][("R10", 10, "follow")]) for s in FX], "freq"),
                                              merge_days([per_day(data[s][("A10", 10, "follow")]) for s in FX], "freq"))
    res["follow_continuation_gold"] = freq_diff(per_day(data["XAUUSD"][("R10", 10, "follow")]), per_day(data["XAUUSD"][("A10", 10, "follow")]))
    # per instrument and by side (descriptive)
    desc = {}
    for s, ev in data.items():
        for (g, k, rule), v in ev.items():
            m = np.isin(v["out"], (1, -1))
            desc[f"{s}|{g}|k{k}|{rule}"] = {"n": int(len(v["pnl"])), "net_mean_bps": float(v["pnl"].mean() * 1e4) if len(v["pnl"]) else None,
                                            "target_first_share": float((v["out"][m] == 1).mean()) if m.any() else None,
                                            "from_below_net_bps": float(v["pnl"][v["side"] == 1].mean() * 1e4) if (v["side"] == 1).any() else None,
                                            "from_above_net_bps": float(v["pnl"][v["side"] == -1].mean() * 1e4) if (v["side"] == -1).any() else None}
    res["descriptive"] = desc
    # battery: 8 instruments x {fade, follow} x {R10, R50} x k {10, 20}
    per = {}
    for s in FX + ("XAUUSD",):
        for g in ("R10", "R50"):
            for k in (10, 20):
                for rule in ("fade", "follow"):
                    per[f"{s}|{g}|k{k}|{rule}"] = per_day(data[s][(g, k, rule)], "pnl")
    cal = weekday_calendar(date(2003, 1, 1), END)
    ci = {d: i for i, d in enumerate(cal)}
    names = sorted(per)
    X = np.zeros((len(cal), len(names)))
    for j, n in enumerate(names):
        for d, v in per[n].items():
            if d in ci:
                X[ci[d], j] = v
    bat = finish("RN", X, None, names, cal, date(2016, 1, 1), 2008)
    res["battery"] = {k: bat["raw"][k] for k in ("spa_validation", "pbo_full_sample", "walk_forward_top5", "verdict", "romano_wolf_significant_5pct")}
    json.dump(res, open(os.path.join(OUT, "round21_rn.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "verdict", "follow_continuation_fx", "follow_continuation_gold")}, indent=1, default=str))
    for k in sorted(desc):
        if "|k10|" in k:
            print(k, desc[k])


# ---------------------------------------------------------------- SG

SHANGHAI = ZoneInfo("Asia/Shanghai")
LAUNCH = date(2016, 4, 19)
SG_WIN = {"AMPRE": (555, 615, 1), "AMPOST": (615, 675, -1), "PMPRE": (810, 855, 1), "PMPOST": (855, 915, -1)}


def family_sg():
    import holidays
    cn = set(holidays.China(years=range(2009, 2027)))
    res, per = {}, {}
    for sym in ("XAUUSD", "XAGUSD"):
        t, x = local(sym, range(2009, 2027), SHANGHAI)
        keep = ~spike_mask(x, 0.02)  # A35a
        t, x = t[keep], x[keep]
        day, mod = t // 1440, t % 1440
        px = {m: price_at(day, mod, x, m) for m in sorted({m for a, b, _ in SG_WIN.values() for m in (a, b)})}
        wins = {}
        for w, (a, b, sgn) in SG_WIN.items():
            rows, hol_rows = {}, {}
            for k, p0 in px[a].items():
                d = date.fromordinal(int(k) + E)
                if k not in px[b] or d.weekday() >= 5 or d > END:
                    continue
                r = sgn * (px[b][k] / p0 - 1)
                if abs(r) > 0.05:
                    continue
                (hol_rows if d in cn else rows)[d] = r
            wins[w] = (rows, hol_rows)
            per[f"{sym}|{w}"] = {d: v - COST[sym] for d, v in rows.items()}
        pre = {d: wins["AMPRE"][0][d] + wins["PMPRE"][0][d] for d in wins["AMPRE"][0] if d in wins["PMPRE"][0]}
        post = {d: wins["AMPOST"][0][d] + wins["PMPOST"][0][d] for d in wins["AMPOST"][0] if d in wins["PMPOST"][0]}
        both = {d: pre[d] + post[d] for d in pre if d in post}
        after = lambda rows: [v for d, v in sorted(rows.items()) if d >= LAUNCH]
        before = lambda rows: [v for d, v in sorted(rows.items()) if d < LAUNCH]
        r = {"PRE_post_launch": hac(after(pre)), "POST_post_launch": hac(after(post)), "PRE_pre_launch": hac(before(pre)),
             "POST_pre_launch": hac(before(post))}
        a_, b_ = np.array(after(both)), np.array(before(both))
        se = math.sqrt(a_.var(ddof=1) / len(a_) + b_.var(ddof=1) / len(b_))
        r["natural_experiment"] = {"diff_bps": float((a_.mean() - b_.mean()) * 1e4), "t": float((a_.mean() - b_.mean()) / se),
                                   "p_one_sided": vs.p_one_sided(float((a_.mean() - b_.mean()) / se))}
        r["per_window"] = {w: {"post_launch": hac(after(v[0])), "pre_launch": hac(before(v[0])),
                               "holiday_placebo": hac(list(v[1].values())) if len(v[1]) > 10 else None} for w, v in wins.items()}
        r["net_per_day_post_launch_bps"] = {"PRE": float(np.mean(after(pre)) * 1e4 - 2 * COST[sym] * 1e4),
                                            "POST": float(np.mean(after(post)) * 1e4 - 2 * COST[sym] * 1e4)}
        res[sym] = r
        print("SG", sym, json.dumps({k: v for k, v in r.items() if k != "per_window"}, default=str), flush=True)
        for w, v in r["per_window"].items():
            print("   ", sym, w, {k: (round(q["mean_bps"], 2), round(q["t"], 2), q["n"]) if q else None for k, q in v.items()})
    g = res["XAUUSD"]
    prim = {"SG1": g["PRE_post_launch"], "SG2": g["POST_post_launch"], "SG3": g["natural_experiment"]}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    net = g["net_per_day_post_launch_bps"]
    ok = [k for k, w in (("SG1", "PRE"), ("SG2", "POST")) if prim[k]["p_holm"] < 0.05 and net[w] > 0]
    flow = any(prim[k]["p_holm"] < 0.05 for k in ("SG1", "SG2"))
    res["primary"] = prim
    res["verdict"] = "EDGE" if ok and prim["SG3"]["p_holm"] < 0.05 else "FLOW, NOT TRADEABLE" if flow else "NO EDGE"
    cal = weekday_calendar(date(2009, 1, 1), END)
    ci = {d: i for i, d in enumerate(cal)}
    names = sorted(per)
    X = np.zeros((len(cal), len(names)))
    for j, n in enumerate(names):
        for d, v in per[n].items():
            if d in ci:
                X[ci[d], j] = v
    bat = finish("SG", X, None, names, cal, LAUNCH, 2011)
    res["battery"] = {k: bat["raw"][k] for k in ("spa_validation", "pbo_full_sample", "walk_forward_top5", "verdict", "romano_wolf_significant_5pct")}
    json.dump(res, open(os.path.join(OUT, "round21_sg.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "verdict")}, indent=1, default=str))


if __name__ == "__main__":
    {"RN": family_rn, "SG": family_sg}[sys.argv[1]]()
