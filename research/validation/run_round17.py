"""Round 17 (PREREGISTRATION.md A31).

    python3 run_round17.py FM    FX / gold intraday momentum (session momentum + noise area) -> results/family_fm.json
    python3 run_round17.py RB    reversal breadth: 12 new SQX-native signals, 5 markets        -> results/family_rb.json
    python3 run_round17.py IM2   late-day momentum on US500 / US100                             -> results/family_im2.json
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
from data_histdata import NY, available_years, local_table
from data_minutes import day_of, local, price_at
from data_yahoo import daily
from run_noise_area import run as noise_run
from run_round4 import irx_map
from run_round10 import finish, weekday_calendar
from run_round11 import LONDON, to_matrix, trade_stats

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
fa.N_TRIALS = 13641
END = date(2026, 8, 31)

# ---------------------------------------------------------------- FM

FM_INSTR = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "XAUUSD")
FM_SPLIT = date(2017, 1, 1)


def session_momentum(sym, cost):
    out = {}
    for lab, tz, op, cl in (("LDN", LONDON, 480, 960), ("NY", NY, 480, 990)):
        t, x = local(sym, range(2010, 2027), tz)
        day, mod = t // 1440, t % 1440
        p0, p30 = price_at(day, mod, x, op, prefer_open=True), price_at(day, mod, x, op + 30)
        pl, pe = price_at(day, mod, x, cl - 30), price_at(day, mod, x, cl)
        for pred in ("R1", "REST"):
            rows = {}
            for k in p0:
                if not all(k in m for m in (p30, pl, pe)):
                    continue
                d = day_of(k)
                if d.weekday() >= 5:
                    continue
                s = (p30[k] / p0[k] - 1) if pred == "R1" else (pl[k] / p0[k] - 1)
                if s == 0:
                    continue
                rows[d] = math.copysign(1.0, s) * (pe[k] / pl[k] - 1) - cost
            out[f"{sym}|{lab}_{pred}|LAST30"] = rows
    return out


def noise_area(sym, cost_bps):
    keep = set(range(479, 1231))
    ses = local_table(sym, available_years(sym, range(2010, 2027)), LONDON, keep)
    out = {}
    for L in (7, 14, 28):
        for bnd in (1.0, 1.25):
            spec = (sym, LONDON, (8, 0), (20, 30), (8, 30), (20, 0), cost_bps, "flip")
            rows, _, _ = noise_run("FM", lookback=L, grid=30, spec=spec, ses=ses, band=bnd)
            out[f"{sym}|NOISE_L{L}_b{bnd:g}|FLIP"] = {d: v / 1e4 for d, v in rows}
    return out


def family_fm(syms=FM_INSTR):
    per = {}
    for sym in syms:
        cost = 2.5e-4 if sym == "XAUUSD" else 1.0e-4
        per.update(session_momentum(sym, cost))
        per.update(noise_area(sym, cost * 1e4))
        print("FM", sym, flush=True)
    cal = weekday_calendar(date(2010, 1, 1), max(max(v) for v in per.values() if v))
    X, names = to_matrix(per, cal)
    res = finish("FM", X, None, names, cal, FM_SPLIT, 2017)
    json.dump({"trade_stats": trade_stats(per, names, FM_SPLIT)}, open(os.path.join(OUT, "family_fm_trades.json"), "w"), indent=1)
    return res


# ---------------------------------------------------------------- RB

RB_MARKETS = ("SPY", "QQQ", "DIA", "IWM", "^N225")


def rolling(f, x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = f(x[i - n + 1:i + 1])
    return out


def wilder_rsi(x, n):
    out = np.full(len(x), 50.0)
    g = l_ = None
    for i in range(1, len(x)):
        ch = x[i] - x[i - 1]
        up, dn = max(ch, 0.0), max(-ch, 0.0)
        if g is None:
            g, l_ = up, dn
        else:
            g, l_ = (g * (n - 1) + up) / n, (l_ * (n - 1) + dn) / n
        out[i] = 100.0 if l_ == 0 else 100 - 100 / (1 + g / l_)
    return out


def rb_signals(c, h, l, craw, hr, lr):
    n = len(c)
    hh14, ll14 = rolling(np.max, h, 14), rolling(np.min, l, 14)
    hh5, ll5 = rolling(np.max, h, 5), rolling(np.min, l, 5)
    sma5, sma20, sd20 = rolling(np.mean, c, 5), rolling(np.mean, c, 20), rolling(np.std, c, 20)
    tr = np.r_[h[0] - l[0], np.maximum(h[1:], c[:-1]) - np.minimum(l[1:], c[:-1])]
    atr10 = rolling(np.mean, tr, 10)
    ema20 = np.full(n, np.nan)
    a = 2 / 21
    ema20[0] = c[0]
    for i in range(1, n):
        ema20[i] = a * c[i] + (1 - a) * ema20[i - 1]
    k14 = (c - ll14) / np.where(hh14 > ll14, hh14 - ll14, np.nan) * 100
    k5 = (c - ll5) / np.where(hh5 > ll5, hh5 - ll5, np.nan) * 100
    rsi3 = wilder_rsi(c, 3)
    streak = np.zeros(n)
    for i in range(1, n):
        streak[i] = (streak[i - 1] + 1 if streak[i - 1] > 0 else 1) if c[i] > c[i - 1] else \
            (streak[i - 1] - 1 if streak[i - 1] < 0 else -1) if c[i] < c[i - 1] else 0
    rsi_st = wilder_rsi(streak, 2)
    roc1 = np.r_[0.0, c[1:] / c[:-1] - 1]
    prank = np.full(n, np.nan)
    for i in range(100, n):
        prank[i] = (roc1[i - 100:i] < roc1[i]).mean() * 100
    crsi = (rsi3 + rsi_st + prank) / 3
    rsi2 = fa.rsi2(c)
    r5 = np.r_[np.full(5, np.nan), c[5:] / c[:-5] - 1]
    pr5 = np.full(n, np.nan)
    for i in range(257, n):
        w = r5[i - 251:i + 1]
        pr5[i] = (w <= r5[i]).mean()
    rngr = hr - lr
    ibs = np.where(rngr > 0, (craw - lr) / np.where(rngr > 0, rngr, 1), 0.5)
    ll3 = np.zeros(n, dtype=bool)
    ll3[3:] = (l[3:] < l[2:-1]) & (l[2:-1] < l[1:-2]) & (l[1:-2] < l[:-3])
    with np.errstate(invalid="ignore"):
        s = {"ST10": k14 < 10, "ST20": k14 < 20, "WR5": k5 < 5, "BB0": c < sma20 - 2 * sd20, "KC2": c < ema20 - 2 * atr10,
             "CR10": crsi < 10, "CR15": crsi < 15, "LL3": ll3, "ATP": c < sma5 - atr10,
             "CUM35": np.r_[False, rsi2[1:] + rsi2[:-1] < 35], "PR5": pr5 <= 0.10, "WRB": (ibs < 0.25) & (h - l > 1.5 * atr10)}
    for k in s:
        s[k] = np.nan_to_num(s[k]).astype(bool)
        s[k][:260] = False
    sma200 = rolling(np.mean, c, 200)
    with np.errstate(invalid="ignore"):
        filt = {"F0": np.ones(n, dtype=bool), "UP": np.nan_to_num(c > sma200).astype(bool), "DN": np.nan_to_num(c < sma200).astype(bool)}
    return s, filt, sma5


def xs5_positions(sig, flt, c, sma5):
    n = len(c)
    pos, entry = np.zeros(n), np.zeros(n)
    i = 0
    while i < n - 1:
        if sig[i] and flt[i]:
            j = i + 1
            entry[j] = 1
            last = j
            while last < min(i + 10, n - 1) and not (c[last] > sma5[last]):
                last += 1
            pos[j:last + 1] = 1
            i = last
            continue
        i += 1
    return pos, entry


def family_rb():
    rates = irx_map()
    keys = sorted(rates)
    cal = sorted({r["date"] for s in RB_MARKETS for r in daily(s) if fa.START <= r["date"] <= fa.END and r["date"].weekday() < 5})
    ci = {x: i for i, x in enumerate(cal)}
    cols, raw, tim, exp_, meta = [], [], [], [], []
    for sym in RB_MARKETS:
        d, c, h, l, craw, ret, rf = fa.load(sym, rates, keys)
        ha, la = h * c / craw, l * c / craw
        sig, filt, sma5 = rb_signals(c, ha, la, craw, h, l)
        idx = np.array([ci[x] for x in d if x in ci])
        keep = np.array([x in ci for x in d])
        mark = fa.MARKUP if sym in fa.US else 0.0
        yr = np.array([x.year for x in d])
        ex = ret - rf
        ymu = {y: float(ex[yr == y].mean()) for y in set(yr.tolist())}
        mu = np.array([ymu[y] for y in yr])
        cs = np.concatenate([[0.0], np.cumsum(ex)[:-1]])
        n_ = np.arange(len(ex), dtype=float)
        mu_e = np.where(n_ >= 252, cs / np.maximum(n_, 1), 0.0)
        for sn in sig:
            for exr in ("X1", "XU", "XS5"):
                for fn in ("F0", "UP", "DN"):
                    if exr == "XS5":
                        pos, entry = xs5_positions(sig[sn], filt[fn], c, sma5)
                    else:
                        pos, entry = fa.positions(sig[sn], filt[fn], c, exr)
                    pnl = pos * ex - pos * mark - entry * fa.COST
                    for store, v in ((raw, pnl), (tim, pnl - pos * mu), (exp_, pnl - pos * mu_e)):
                        col = np.zeros(len(cal))
                        col[idx] = v[keep]
                        store.append(col)
                    cols.append(f"{sym}|{sn}|{exr}|{fn}")
                    meta.append({"name": cols[-1], "trades_per_year": float(entry.sum() / (len(d) / 252)), "exposure": float(pos.mean())})
        print("RB", sym, flush=True)
    X, XA, XE = np.array(raw).T, np.array(tim).T, np.array(exp_).T
    np.savez_compressed(os.path.join(R9, "family_rb.npz"), X=X, XA=XA, XE=XE, dates=np.array([x.toordinal() for x in cal]), cols=np.array(cols))
    years = np.array([x.year for x in cal])
    disc = np.array([x < fa.SPLIT for x in cal])
    res = {"n_variants": len(cols)}
    for lab, M in (("timing", XA), ("raw", X), ("timing_expanding", XE)):
        res[lab] = fa.battery(M, cols, disc, ~disc, years)
    # overlap with family A on the same five markets (validation, timing value, equal risk on discovery volatility)
    pa = np.load(os.path.join(R9, "family_a.npz"))
    acal = [date.fromordinal(int(v)) for v in pa["dates"]]
    acols = [str(v) for v in pa["cols"]]
    sel = [i for i, cn in enumerate(acols) if cn.split("|")[0] in RB_MARKETS]
    adisc = np.array([x < fa.SPLIT for x in acal])
    A = pa["XA"][:, sel]
    sa = A[adisc].std(0, ddof=1)
    wa = np.where(sa > 0, 1 / np.where(sa > 0, sa, 1), 0)
    aens = dict(zip(acal, A @ (wa / wa.sum())))
    sb = XA[disc].std(0, ddof=1)
    wb = np.where(sb > 0, 1 / np.where(sb > 0, sb, 1), 0)
    bens = XA @ (wb / wb.sum())
    pairs = np.array([(b, aens[x]) for x, b, v in zip(cal, bens, ~disc) if v and x in aens])
    res["overlap_with_family_a"] = {"corr_validation": float(np.corrcoef(pairs[:, 0], pairs[:, 1])[0, 1]),
                                    "rb_ensemble_sharpe_validation": float(mt.sharpe(pairs[:, :1], 252)[0]),
                                    "a_ensemble_sharpe_validation": float(mt.sharpe(pairs[:, 1:], 252)[0]),
                                    "combined_sharpe_validation": float(mt.sharpe(((pairs[:, 0] / pairs[:, 0].std()) + (pairs[:, 1] / pairs[:, 1].std()))[:, None], 252)[0])}
    for mrow, a_, v, t_, p in zip(meta, res["raw"]["_sr_d"], res["raw"]["_sr_v"], res["timing"]["_sr_v"], res["timing"]["_p_rw"]):
        mrow.update({"sharpe_discovery": a_, "sharpe_validation_raw": v, "sharpe_validation_timing": t_, "rw_p_timing": p})
    for lab in ("timing", "raw", "timing_expanding"):
        for k in ("_sr_d", "_sr_v", "_p_rw"):
            res[lab].pop(k)
    res["variants"] = meta
    res["family_verdict"] = res["timing"]["verdict"]
    json.dump(res, open(os.path.join(OUT, "family_rb.json"), "w"), indent=1, default=str)
    for lab in ("timing", "raw"):
        b = res[lab]
        print(lab, {k: b[k] for k in ("spa_validation", "pbo_full_sample", "selection_test", "walk_forward_top5", "best_validation_variant", "verdict")})
        print(lab, "RW", len(b["romano_wolf_significant_5pct"]), b["romano_wolf_significant_5pct"][:20])
        for inst, v in b["per_instrument"].items():
            print("   ", inst, v)
    print("overlap", res["overlap_with_family_a"])


# ---------------------------------------------------------------- IM2

def family_im2():
    per = {}
    for sym, name in (("SPXUSD", "US500"), ("NSXUSD", "US100")):
        t, x = local(sym, range(2014, 2027), NY)
        day, mod = t // 1440, t % 1440
        p0, p10, p1530, p16 = (price_at(day, mod, x, m, prefer_open=(m == 570)) for m in (570, 600, 930, 960))
        ks = sorted(k for k in p0 if k in p10 and k in p1530 and k in p16 and day_of(k).weekday() < 5 and day_of(k) <= END)
        for pred in ("R1", "REST"):
            vals = [(p10[k] / p0[k] - 1) if pred == "R1" else (p1530[k] / p0[k] - 1) for k in ks]
            for thr in ("ALL", "STRONG"):
                rows = {}
                for i, k in enumerate(ks):
                    s = vals[i]
                    if s == 0:
                        continue
                    if thr == "STRONG":
                        if i < 20 or abs(s) <= np.median(np.abs(vals[i - 20:i])):
                            continue
                    rows[day_of(k)] = math.copysign(1.0, s) * (p16[k] / p1530[k] - 1) - 1.5e-4
                per[f"{name}|{pred}|{thr}"] = rows
        print("IM2", name, len(ks), flush=True)
    cal = weekday_calendar(date(2014, 1, 1), END)
    X, names = to_matrix(per, cal)
    res = finish("IM2", X, None, names, cal, date(2020, 1, 1), 2020)
    stats = trade_stats(per, names, date(2020, 1, 1))
    json.dump({"trade_stats": stats}, open(os.path.join(OUT, "family_im2_trades.json"), "w"), indent=1)
    for n_ in names:
        print("  ", n_, stats[n_])
    return res


if __name__ == "__main__":
    {"FM": family_fm, "RB": family_rb, "IM2": family_im2}[sys.argv[1]]()
