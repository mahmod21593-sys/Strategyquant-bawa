"""Round 13 (PREREGISTRATION.md A27).

    python3 run_round13.py Y    reversal on 21 FX crosses (daily bars 19:00 -> 16:45 NY)   -> results/family_y.json
    python3 run_round13.py Z    VIX term-structure / spike / VRP entries on US index ETFs  -> results/family_z.json
    python3 run_round13.py ZM   noise-area momentum by VIX regime (N1, N3)                  -> results/family_zm.json
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date

import numpy as np

import multitest as mt
import run_family_a as fa
import vstats as vs
from data_histdata import NY
from data_minutes import day_of, group, local
from data_yahoo import daily
from run_round4 import irx_map
from run_round10 import book_matrix, expanding_mean, finish, positions_dir, weekday_calendar
from run_round12 import ols_nw

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
fa.N_TRIALS = 12669

# ---------------------------------------------------------------- family Y: FX crosses

Y_INSTR = ("EURGBP", "EURCHF", "AUDNZD", "EURCAD", "AUDCAD", "GBPCHF", "NZDCAD", "CADCHF", "AUDCHF", "EURAUD", "EURNZD",
           "GBPAUD", "GBPCAD", "GBPNZD", "EURJPY", "GBPJPY", "AUDJPY", "CHFJPY", "CADJPY", "NZDJPY", "NZDCHF")
Y_TIGHT = ("EURGBP", "EURCHF", "EURJPY")
Y_SPLIT = date(2017, 1, 1)


def fx_bars(sym):
    """Daily bars 19:00 NY (previous day) -> 16:45 NY, labelled by the 16:45 date; 16:45-19:00 NY left out (A23)."""
    path = os.path.join(R9, f"fxd13_{sym}.npz")
    if os.path.exists(path):
        p = np.load(path)
        return [date.fromordinal(int(v)) for v in p["d"]], p["o"], p["h"], p["l"], p["c"]
    t, x = local(sym, range(2008, 2027), NY)
    mod = t % 1440
    k = (mod < 1005) | (mod >= 1140)
    t, x = t[k], x[k]
    keys, o, h, l, c, n, _ = group((t + 300) // 1440, x)
    ok = (n >= 600) & np.array([day_of(v).weekday() < 5 for v in keys])
    d = [day_of(v) for v in keys[ok]]
    np.savez(path, d=np.array([v.toordinal() for v in d]), o=o[ok], h=h[ok], l=l[ok], c=c[ok])
    return d, o[ok], h[ok], l[ok], c[ok]


def bb_positions(sig, flt, done, maxd):
    """Enter at the close of a signal bar, exit at the close of the first bar where ``done`` holds (max ``maxd`` bars)."""
    n = len(sig)
    pos, entry = np.zeros(n), np.zeros(n)
    i = 0
    while i < n - 1:
        if sig[i] and flt[i]:
            j = i + 1
            entry[j] = 1
            last = j
            while last < min(i + maxd, n - 1) and not done[last]:
                last += 1
            pos[j:last + 1] = 1
            i = last
            continue
        i += 1
    return pos, entry


def family_y():
    per, per_e = [], []
    for sym in Y_INSTR:
        d, o, h, l, c = fx_bars(sym)
        n = len(c)
        ret = np.r_[0.0, c[1:] / c[:-1] - 1]
        gap = np.r_[1.0, [(d[i] - d[i - 1]).days for i in range(1, n)]]
        sl, filt = fa.signals(c, h, l, c, ret)
        m = 2 * c.max()
        ss, _ = fa.signals(m - c, m - l, m - h, m - c, -ret)
        up, dn = filt["UP"], filt["DN"]
        cost = 2.0e-4 if sym in Y_TIGHT else 3.0e-4
        mark = 0.005 / 365
        mu = expanding_mean(ret)
        dd, ddE = {}, {}

        def book(name, pos, entry):
            pnl = pos * ret - np.abs(pos) * mark * gap - entry * cost
            dd[name] = pnl
            ddE[name] = pnl - pos * mu

        for side, sigs in ((1, sl), (-1, ss)):
            flts = {"F0": filt["F0"], "TREND": up if side == 1 else dn, "COUNTER": dn if side == 1 else up}
            for sn in fa.SIGNALS:
                for exr in fa.EXITS:
                    for fn, flt in flts.items():
                        pos, entry = positions_dir(sigs[sn], flt, c, exr, side)
                        book(f"{sym}|{'L' if side == 1 else 'S'}{sn}|{exr}|{fn}", pos, entry)
            # Bollinger(20, 2) close outside the band, exit at the middle band, max 20 bars
            cs, cs2 = np.r_[0.0, np.cumsum(c)], np.r_[0.0, np.cumsum(c * c)]
            mid, sd = np.full(n, np.nan), np.full(n, np.nan)
            mid[19:] = (cs[20:] - cs[:-20]) / 20
            sd[19:] = np.sqrt(np.maximum((cs2[20:] - cs2[:-20]) / 20 - mid[19:] ** 2, 0))
            with np.errstate(invalid="ignore"):
                sig = (c < mid - 2 * sd) if side == 1 else (c > mid + 2 * sd)
                done = (c >= mid) if side == 1 else (c <= mid)
            sig[:200] = False
            for fn, flt in flts.items():
                pos, entry = bb_positions(sig, flt, done, 20)
                book(f"{sym}|{'L' if side == 1 else 'S'}BB2|XM|{fn}", side * pos, entry)
        per.append((d, dd))
        per_e.append((d, ddE))
        print("Y", sym, n, d[0], flush=True)
    cal = weekday_calendar(date(2008, 1, 1), max(p[0][-1] for p in per))
    X, names = book_matrix(per, cal)
    XE, _ = book_matrix(per_e, cal)
    return finish("Y", X, XE, names, cal, Y_SPLIT, 2017)


# ---------------------------------------------------------------- family Z: volatility-regime entries

Z_START, Z_SPLIT = date(2007, 7, 1), date(2017, 1, 1)


def z_triggers(dts, ret, vix, v3):
    n = len(dts)
    V = np.array([vix.get(x, np.nan) for x in dts])
    W = np.array([v3.get(x, np.nan) for x in dts])
    for arr in (V, W):  # carry the last close over a missing day
        for i in range(1, n):
            if not np.isfinite(arr[i]):
                arr[i] = arr[i - 1]
    prev = np.r_[np.nan, V[:-1]]
    sma = np.full(n, np.nan)
    cs = np.r_[0.0, np.cumsum(np.nan_to_num(V))]
    sma[19:] = (cs[20:] - cs[:-20]) / 20
    rv = np.full(n, np.nan)
    c2 = np.r_[0.0, np.cumsum(ret * ret)]
    rv[20:] = 252 * (c2[21:] - c2[:-21]) / 21
    vrp = (V / 100) ** 2 - rv
    pct = np.full(n, np.nan)
    for i in range(272, n):
        w = vrp[i - 251:i + 1]
        w = w[np.isfinite(w)]
        if len(w) > 200 and np.isfinite(vrp[i]):
            pct[i] = (w <= vrp[i]).mean()
    with np.errstate(invalid="ignore"):
        trig = {"BW100": V / W >= 1.00, "BW105": V / W >= 1.05, "BW110": V / W >= 1.10,
                "SP15": V / prev - 1 >= 0.15, "SP25": V / prev - 1 >= 0.25,
                "EL20": V / sma - 1 >= 0.20, "EL40": V / sma - 1 >= 0.40,
                "VRP67": pct >= 2 / 3, "VRP80": pct >= 0.80}
    return {k: np.nan_to_num(v).astype(bool) for k, v in trig.items()}


def z_positions(trig, rule):
    n = len(trig)
    pos, entry = np.zeros(n), np.zeros(n)
    if rule == "ST":
        pos[1:] = trig[:-1]
        entry[1:] = (pos[1:] == 1) & (pos[:-1] == 0)
        return pos, entry
    N = 5 if rule == "H5" else 10
    i = 0
    while i < n - 1:
        if trig[i]:
            last = min(i + N, n - 1)
            entry[i + 1] = 1
            pos[i + 1:last + 1] = 1
            i = last
            continue
        i += 1
    return pos, entry


def family_z():
    rates = irx_map()
    keys = sorted(rates)
    vix = {r["date"]: r["c"] for r in daily("^VIX")}
    v3 = {r["date"]: r["c"] for r in daily("^VIX3M")}
    cal = sorted({r["date"] for s in fa.US for r in daily(s) if Z_START <= r["date"] <= fa.END and r["date"].weekday() < 5})
    ci = {x: i for i, x in enumerate(cal)}
    cols, raw, tim, meta = [], [], [], []
    for sym in fa.US:
        d, c, h, l, craw, ret, rf = fa.load(sym, rates, keys)
        trig = z_triggers(d, ret, vix, v3)
        yr = np.array([x.year for x in d])
        ex = ret - rf
        ymu = {y: float(ex[yr == y].mean()) for y in set(yr.tolist())}
        mu = np.array([ymu[y] for y in yr])
        keep = np.array([Z_START <= x for x in d])
        idx = np.array([ci[x] for x, k in zip(d, keep) if k and x in ci])
        keep = np.array([k and x in ci for x, k in zip(d, keep)])
        for tn, tg in trig.items():
            for rule in ("ST", "H5", "H10"):
                pos, entry = z_positions(tg, rule)
                pnl = pos * ex - pos * fa.MARKUP - entry * fa.COST
                for store, v in ((raw, pnl), (tim, pnl - pos * mu)):
                    col = np.zeros(len(cal))
                    col[idx] = v[keep]
                    store.append(col)
                cols.append(f"{sym}|{tn}|{rule}")
                meta.append({"name": cols[-1], "trades_per_year": float(entry[keep].sum() / (keep.sum() / 252)), "exposure": float(pos[keep].mean())})
        print("Z", sym, flush=True)
    X, XA = np.array(raw).T, np.array(tim).T
    years = np.array([x.year for x in cal])
    disc = np.array([x < Z_SPLIT for x in cal])
    res = {"n_variants": len(cols)}
    for lab, M in (("timing", XA), ("raw", X)):
        res[lab] = fa.battery(M, cols, disc, ~disc, years, first_wf=2017)
    # novelty: validation Z ensemble vs family A's US ensemble (timing value), Newey-West alpha
    pa = np.load(os.path.join(R9, "family_a.npz"))
    acal = [date.fromordinal(int(v)) for v in pa["dates"]]
    acols = [str(v) for v in pa["cols"]]
    us = [i for i, cn in enumerate(acols) if cn.split("|")[0] in fa.US]
    adisc = np.array([x < fa.SPLIT for x in acal])
    A = pa["XA"][:, us]
    sdA = A[adisc].std(0, ddof=1)
    wA = np.where(sdA > 0, 1 / np.where(sdA > 0, sdA, 1), 0)
    a_ens = dict(zip(acal, A @ (wA / wA.sum())))
    sdZ = XA[disc].std(0, ddof=1)
    wZ = np.where(sdZ > 0, 1 / np.where(sdZ > 0, sdZ, 1), 0)
    z_ens = XA @ (wZ / wZ.sum())
    rows = [(z, a_ens[x]) for x, z, v in zip(cal, z_ens, ~disc) if v and x in a_ens]
    zz, aa = np.array(rows).T
    coef, tstat = ols_nw_full(zz, aa, 5)
    alpha_t = tstat[0]
    res["novelty_vs_family_a"] = {"validation_days": int(len(zz)), "corr": float(np.corrcoef(zz, aa)[0, 1]), "beta": float(coef[1]), "beta_t": tstat[1],
                                  "alpha_bps_per_day": float(coef[0] * 1e4), "alpha_t_hac": alpha_t,
                                  "z_ensemble_sharpe_validation": float(mt.sharpe(zz[:, None], 252)[0]),
                                  "new_edge": bool(alpha_t > 2)}
    for mrow, a, v, t_, p in zip(meta, res["raw"]["_sr_d"], res["raw"]["_sr_v"], res["timing"]["_sr_v"], res["timing"]["_p_rw"]):
        mrow.update({"sharpe_discovery": a, "sharpe_validation_raw": v, "sharpe_validation_timing": t_, "rw_p_timing": p})
    for lab in ("timing", "raw"):
        for k in ("_sr_d", "_sr_v", "_p_rw"):
            res[lab].pop(k)
    res["variants"] = meta
    res["family_verdict"] = res["timing"]["verdict"]
    json.dump(res, open(os.path.join(OUT, "family_z.json"), "w"), indent=1, default=str)
    for lab in ("timing", "raw"):
        b_ = res[lab]
        print(lab, {k: b_[k] for k in ("spa_validation", "pbo_full_sample", "selection_test", "walk_forward_top5", "best_validation_variant", "verdict")})
        print(lab, "RW", b_["romano_wolf_significant_5pct"])
        for inst, v in b_["per_instrument"].items():
            print("   ", inst, v)
    print("novelty", res["novelty_vs_family_a"])


def ols_nw_full(y, x, lag):
    """OLS of y on [1, x]: (coefficients, Newey-West t-statistics)."""
    X = np.column_stack([np.ones(len(y)), x])
    XtX = np.linalg.inv(X.T @ X)
    b = XtX @ X.T @ y
    e = y - X @ b
    S = (X * e[:, None]).T @ (X * e[:, None])
    for k in range(1, lag + 1):
        G = (X[k:] * e[k:, None]).T @ (X[:-k] * e[:-k, None])
        S += (1 - k / (lag + 1)) * (G + G.T)
    V = XtX @ S @ XtX
    return b, [float(b[i] / math.sqrt(V[i, i])) for i in range(2)]


# ---------------------------------------------------------------- family ZM: momentum by volatility regime

def family_zm():
    vix = sorted((r["date"], r["c"]) for r in daily("^VIX"))
    vd = [x for x, _ in vix]
    vv = np.array([v for _, v in vix])
    import bisect
    res = {}
    pvals = {}
    for sym, col, name in (("SPXUSD", "SPXUSD|L14|b1|g30|flip", "US500"), ("NSXUSD", "NSXUSD|L14|b1|g30|flip", "US100")):
        p = np.load(os.path.join(R9, f"family_b_{sym}.npz"))
        cols = [str(c) for c in p["cols"]]
        rows = [(date.fromordinal(int(dd)), float(x)) for dd, x in zip(p["dates"], p["X"][:, cols.index(col)])]
        rows = [r for r in rows if date(2014, 1, 1) <= r[0] <= date(2026, 8, 31)]
        hi, lo = [], []
        for dd, x in rows:
            j = bisect.bisect_left(vd, dd) - 1  # previous VIX close
            if j < 252:
                continue
            (hi if vv[j] > np.median(vv[j - 251:j + 1]) else lo).append(x)
        out = {}
        for lab, xs in (("high", hi), ("low", lo)):
            xs = np.array(xs)
            t_ = vs.nw_t(list(xs), 5)
            out[lab] = {"n": int(len(xs)), "mean_bps": float(xs.mean() * 1e4), "t_hac": t_, "sharpe": float(xs.mean() / xs.std(ddof=1) * math.sqrt(252)),
                        "p_one_sided": vs.p_one_sided(t_)}
        diff = np.r_[hi, lo]
        z = np.r_[np.ones(len(hi)), np.zeros(len(lo))]
        b, t_ = ols_nw(diff, z, 5)
        out["high_minus_low"] = {"bps": b * 1e4, "t": t_}
        res[name] = out
        pvals[name] = out["high"]["p_one_sided"]
    holm = vs.holm(pvals)
    for k in res:
        res[k]["high"]["p_holm"] = holm[k]
        res[k]["verdict"] = "CONFIRMED" if holm[k] < 0.05 and res[k]["high"]["mean_bps"] > 0 else "NOT CONFIRMED"
    json.dump(res, open(os.path.join(OUT, "family_zm.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"Y": family_y, "Z": family_z, "ZM": family_zm}[sys.argv[1]]()
