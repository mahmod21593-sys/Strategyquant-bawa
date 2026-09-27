"""Round 10 (PREREGISTRATION.md A23): families E (reversal outside equities), F (per-market trend/breakout),
G (index-pair relative value), H (calendar). Uses the A22 battery.

    python3 run_round10.py E|F|G|H       -> results/family_<x>.json, $ROUND9_DIR/family_<x>.npz
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date, timedelta

import numpy as np

import run_family_a as fa
from data_yahoo import daily
from run_round4 import irx_map, tbill

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
END = date(2026, 8, 31)
fa.N_TRIALS = 5049
INDICES = ("SPY", "QQQ", "DIA", "IWM", "^GDAXI", "^FTSE", "^N225", "^AXJO")
US_ETF = ("SPY", "QQQ", "DIA", "IWM")
FX = ("EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X")
CMDTY = ("GLD", "SLV", "USO", "UNG")
CRYPTO = ("BTC-USD", "ETH-USD")


def cost_of(sym):
    """(cost per entry, mark-up per calendar day held) as fractions."""
    if sym in FX:
        return 1.0e-4, 0.005 / 365
    if sym in CMDTY:
        return 2.5e-4, 0.02 / 365
    if sym in CRYPTO:
        return 5.0e-4, 0.02 / 365
    return 1.5e-4, (0.02 / 365 if sym in US_ETF else 0.0)


def series(sym, rates, keys, start=date(1993, 2, 1)):
    rows = [r for r in daily(sym) if start <= r["date"] <= END]
    d = [r["date"] for r in rows]
    c = np.array([r["adj"] for r in rows])
    craw = np.array([r["c"] for r in rows])
    h = np.array([r["h"] for r in rows]) * c / craw
    l = np.array([r["l"] for r in rows]) * c / craw
    ret = np.zeros(len(c))
    ret[1:] = c[1:] / c[:-1] - 1
    rf = np.zeros(len(c))
    gap = np.ones(len(c))
    for i in range(1, len(d)):
        gap[i] = (d[i] - d[i - 1]).days
        if sym not in FX:
            rf[i] = tbill(rates, keys, d[i - 1], d[i])
    return d, c, h, l, ret, rf, gap


def expanding_mean(x):
    cs = np.concatenate([[0.0], np.cumsum(x)[:-1]])
    n = np.arange(len(x), dtype=float)
    return np.where(n >= 252, cs / np.maximum(n, 1), 0.0)


def book_matrix(per_inst, cal):
    """per_inst: list of (dates, {name: pnl array}); returns (X, names) on the weekday calendar."""
    ci = {d: i for i, d in enumerate(cal)}
    names, cols = [], []
    for dates, dd in per_inst:
        rowmap = []
        for d in dates:
            k = d if d.weekday() < 5 else d + timedelta(days=7 - d.weekday())
            rowmap.append(ci.get(k, -1))
        rowmap = np.array(rowmap)
        ok = rowmap >= 0
        for name, x in dd.items():
            col = np.zeros(len(cal))
            np.add.at(col, rowmap[ok], x[ok])
            names.append(name)
            cols.append(col)
    return np.array(cols).T, names


def weekday_calendar(start, end=END):
    out, d = [], start
    while d <= end:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def finish(key, X, XE, names, cal, split, first_wf):
    np.savez_compressed(os.path.join(R9, f"family_{key.lower()}.npz"), X=X, XE=X if XE is None else XE, dates=np.array([d.toordinal() for d in cal]), cols=np.array(names))
    active = np.abs(X).sum(1) > 0
    first = int(np.argmax(active))
    X, cal = X[first:], cal[first:]
    XE = None if XE is None else XE[first:]
    years = np.array([d.year for d in cal])
    val = np.array([d >= split for d in cal])
    res = {"n_variants": len(names), "first_active": str(cal[0]), "split": str(split)}
    labels = (("raw", X),) if XE is None else (("timing_expanding", XE), ("raw", X))
    for lab, M in labels:
        res[lab] = fa.battery(M, names, ~val, val, years, first_wf=first_wf)
    main_lab = labels[0][0]
    res["family_verdict"] = res[main_lab]["verdict"]
    res["verdict_basis"] = main_lab
    res["variants"] = [{"name": n, "sharpe_discovery": a, "sharpe_validation_raw": v, "sharpe_validation_verdict_basis": vb, "rw_p_verdict_basis": p}
                       for n, a, v, vb, p in zip(names, res["raw"]["_sr_d"], res["raw"]["_sr_v"], res[main_lab]["_sr_v"], res[main_lab]["_p_rw"])]
    for lab, _ in labels:
        for k in ("_sr_d", "_sr_v", "_p_rw"):
            res[lab].pop(k)
    json.dump(res, open(os.path.join(OUT, f"family_{key.lower()}.json"), "w"), indent=1, default=str)
    for lab, _ in labels:
        b = res[lab]
        print(key, lab, {k: b[k] for k in ("spa_validation", "pbo_full_sample", "selection_test", "walk_forward_top5", "best_validation_variant", "verdict")})
        print(key, lab, "RW", b["romano_wolf_significant_5pct"][:30])
        for inst, v in b["per_instrument"].items():
            print("   ", inst, v)
    return res


# ---------------------------------------------------------------- family E

def short_signals(c, h, l, ret):
    """Mirror images of family A's signals: strength instead of weakness."""
    s_long, filt = fa.signals(-c + 2 * c.max(), -l + 2 * c.max(), -h + 2 * c.max(), -c + 2 * c.max(), -ret)
    return s_long, filt


def positions_dir(sig, flt, c, exit_rule, direction):
    """direction +1: exit on the first up close (XU); -1: on the first down close."""
    if direction == 1:
        return fa.positions(sig, flt, c, exit_rule)
    pos, entry = fa.positions(sig, flt, -c, exit_rule)  # a down close of c is an up close of -c
    return -pos, entry


def family_e():
    rates = irx_map()
    keys = sorted(rates)
    per = []
    per_e = []
    for sym in CMDTY + FX[:4] + CRYPTO:
        d, c, h, l, ret, rf, gap = series(sym, rates, keys, date(2003, 1, 1))
        craw = c  # adjusted OHLC already consistent
        sl, filt = fa.signals(c, h, l, craw, ret)
        # short side: mirror price path so that "weakness" signals of the mirror are "strength" signals of c
        m = 2 * c.max()
        ss, _ = fa.signals(m - c, m - l, m - h, m - c, -ret)
        up, dn = filt["UP"], filt["DN"]
        cost, mark = cost_of(sym)
        ex = ret - rf
        mu = expanding_mean(ex)
        dd, ddE = {}, {}
        for side, sigs in ((1, sl), (-1, ss)):
            for sn in fa.SIGNALS:
                for exr in fa.EXITS:
                    for fn in ("F0", "TREND", "COUNTER"):
                        if fn == "F0":
                            flt = filt["F0"]
                        elif fn == "TREND":
                            flt = up if side == 1 else dn
                        else:
                            flt = dn if side == 1 else up
                        pos, entry = positions_dir(sigs[sn], flt, c, exr, side)
                        pnl = pos * ex - np.abs(pos) * mark * gap - entry * cost
                        name = f"{sym}|{'L' if side == 1 else 'S'}{sn}|{exr}|{fn}"
                        dd[name] = pnl
                        ddE[name] = pnl - pos * mu
        per.append((d, dd))
        per_e.append((d, ddE))
        print("E", sym, flush=True)
    cal = weekday_calendar(date(2003, 1, 1))
    X, names = book_matrix(per, cal)
    XE, _ = book_matrix(per_e, cal)
    return finish("E", X, XE, names, cal, date(2015, 1, 1), 2015)


# ---------------------------------------------------------------- family F

def trend_positions(c, kind, p, longshort):
    n = len(c)
    pos = np.zeros(n)
    if kind == "DON":
        N = p
        state = 0
        for i in range(N + 1, n):
            hi, lo = c[i - N:i].max(), c[i - N:i].min()
            xhi, xlo = c[i - N // 2:i].max(), c[i - N // 2:i].min()
            if state == 1 and c[i] < xlo:
                state = 0
            elif state == -1 and c[i] > xhi:
                state = 0
            if state == 0:
                if c[i] > hi:
                    state = 1
                elif c[i] < lo and longshort:
                    state = -1
            pos[i] = state  # position held from the close of i
    elif kind == "MA":
        f, s = p
        cs = np.cumsum(np.concatenate([[0.0], c]))
        for i in range(s, n):
            mf = (cs[i + 1] - cs[i + 1 - f]) / f
            ms = (cs[i + 1] - cs[i + 1 - s]) / s
            pos[i] = 1 if mf > ms else (-1 if longshort else 0)
    else:
        L = p
        for i in range(L, n):
            pos[i] = 1 if c[i] > c[i - L] else (-1 if longshort else 0)
    held = np.zeros(n)
    held[1:] = pos[:-1]  # decided at the close, earns the next day's return
    entry = np.zeros(n)
    entry[1:] = np.abs(np.diff(held))
    return held, entry


def family_f():
    rates = irx_map()
    keys = sorted(rates)
    per, per_e = [], []
    rules = [("DON", 20), ("DON", 55), ("DON", 100), ("MA", (10, 50)), ("MA", (20, 100)), ("MA", (50, 200)), ("MOM", 20), ("MOM", 60), ("MOM", 120)]
    for sym in INDICES + CMDTY + FX + CRYPTO + ("^HSI",):
        d, c, h, l, ret, rf, gap = series(sym, rates, keys, date(1993, 2, 1))
        cost, mark = cost_of(sym)
        ex = ret - rf
        mu = expanding_mean(ex)
        dd, ddE, ddN = {}, {}, {}
        for kind, p in rules:
            for ls in (False, True):
                pos, entry = trend_positions(c, kind, p, ls)
                base = pos * ex - entry * cost
                pnl = base - np.abs(pos) * mark * gap
                pn = p if kind != "MA" else f"{p[0]}-{p[1]}"
                name = f"{sym}|{kind}{pn}|{'LS' if ls else 'L'}"
                dd[name] = pnl
                ddE[name] = pnl - pos * mu
        per.append((d, dd))
        per_e.append((d, ddE))
        print("F", sym, flush=True)
    cal = weekday_calendar(date(1993, 2, 1))
    X, names = book_matrix(per, cal)
    XE, _ = book_matrix(per_e, cal)
    return finish("F", X, XE, names, cal, date(2015, 1, 1), 2015)


# ---------------------------------------------------------------- family G

PAIRS = (("QQQ", "SPY"), ("IWM", "SPY"), ("DIA", "SPY"), ("QQQ", "IWM"), ("^GDAXI", "^FCHI"), ("^FTSE", "^GDAXI"))


def family_g():
    rates = irx_map()
    keys = sorted(rates)
    per = []
    for a, b in PAIRS:
        da = {r["date"]: r["adj"] for r in daily(a) if date(1993, 2, 1) <= r["date"] <= END}
        db = {r["date"]: r["adj"] for r in daily(b) if date(1993, 2, 1) <= r["date"] <= END}
        d = sorted(set(da) & set(db))
        pa, pb = np.array([da[x] for x in d]), np.array([db[x] for x in d])
        ra, rb = np.zeros(len(d)), np.zeros(len(d))
        ra[1:], rb[1:] = pa[1:] / pa[:-1] - 1, pb[1:] / pb[:-1] - 1
        gap = np.ones(len(d))
        gap[1:] = [(d[i] - d[i - 1]).days for i in range(1, len(d))]
        lr = np.log(pa / pb)
        spread = ra - rb  # long a, short b
        cost, mark = 1.5e-4, 0.02 / 365
        dd = {}
        for L in (20, 60, 120):
            z = np.full(len(d), np.nan)
            for i in range(L, len(d)):
                w = lr[i - L + 1:i + 1]
                sd = w.std()
                z[i] = (lr[i] - w.mean()) / sd if sd > 0 else 0
            for k in (1.5, 2.0, 2.5):
                for mode in ("REV", "MOM"):
                    for exr in ("Z0", "T5", "T20"):
                        pos = np.zeros(len(d))
                        state, age = 0, 0
                        for i in range(L, len(d) - 1):
                            if state != 0:
                                age += 1
                                if exr == "Z0":  # z back through zero (reversion) or back to zero (momentum); 60-day cap
                                    done = (np.sign(z[i]) == state if mode == "REV" else np.sign(z[i]) == -state) or age >= 60
                                else:
                                    done = age >= (5 if exr == "T5" else 20)
                                if done:
                                    state, age = 0, 0
                            if state == 0 and abs(z[i]) > k:
                                state = (-np.sign(z[i]) if mode == "REV" else np.sign(z[i]))  # +1: long a / short b
                                age = 0
                            pos[i + 1] = state
                        entry = np.zeros(len(d))
                        entry[1:] = np.abs(np.diff(pos))
                        pnl = pos * spread - entry * 2 * cost - np.abs(pos) * 2 * mark * gap
                        dd[f"{a}/{b}|L{L}|k{k:g}|{mode}|{exr}"] = pnl
        per.append((d, dd))
        print("G", a, b, flush=True)
    cal = weekday_calendar(date(1993, 2, 1))
    X, names = book_matrix(per, cal)
    return finish("G", X, None, names, cal, date(2013, 1, 1), 2013)


# ---------------------------------------------------------------- family H

def family_h():
    rates = irx_map()
    keys = sorted(rates)
    spy_days = sorted(r["date"] for r in daily("SPY"))
    hol = set()  # US market holidays = weekdays with no SPY session
    for a_, b_ in zip(spy_days, spy_days[1:]):
        t = a_ + timedelta(days=1)
        while t < b_:
            if t.weekday() < 5:
                hol.add(t)
            t += timedelta(days=1)
    per, per_e = [], []
    for sym in INDICES:
        d, c, h, l, ret, rf, gap = series(sym, rates, keys, date(1993, 2, 1))
        cost, mark = cost_of(sym)
        ex = ret - rf
        mu = expanding_mean(ex)
        n = len(d)
        last_of_month = np.array([i + 1 == n or d[i + 1].month != d[i].month for i in range(n)])
        dd, ddE = {}, {}

        def add(name, held):
            entry = np.zeros(n)
            entry[1:] = np.maximum(0, np.diff(held))
            entry[0] = held[0]
            pnl = held * ex - held * mark * gap - entry * cost
            dd[name] = pnl
            ddE[name] = pnl - held * mu

        idx_last = np.where(last_of_month)[0]
        for k in (1, 2, 3, 4):
            for m in (1, 2, 3, 4):
                held = np.zeros(n)
                for e in idx_last:
                    a, b = e - k + 1, e + m  # hold the returns of days e-k+1 .. e+m (enter at close of e-k)
                    held[max(a, 0):min(b, n - 1) + 1] = 1
                add(f"{sym}|TOM-{k}+{m}", held)
        for wd in range(5):
            add(f"{sym}|DOW{wd}", np.array([1.0 if x.weekday() == wd else 0.0 for x in d]))
        if sym in US_ETF:
            for kk in (1, 2):
                held = np.zeros(n)
                for i in range(n - 1):
                    # sessions i with a US holiday between this session and the next one within 1..kk sessions ahead
                    for j in range(1, kk + 1):
                        if i + j < n:
                            gapdays = [d[i + j - 1] + timedelta(days=t) for t in range(1, (d[i + j] - d[i + j - 1]).days)]
                            if any(g in hol and g.weekday() < 5 for g in gapdays):
                                held[i] = 1
                add(f"{sym}|PREHOL{kk}", held)
        per.append((d, dd))
        per_e.append((d, ddE))
        print("H", sym, flush=True)
    cal = weekday_calendar(date(1993, 2, 1))
    X, names = book_matrix(per, cal)
    XE, _ = book_matrix(per_e, cal)
    return finish("H", X, XE, names, cal, date(2013, 1, 1), 2013)


if __name__ == "__main__":
    os.makedirs(R9, exist_ok=True)
    {"E": family_e, "F": family_f, "G": family_g, "H": family_h}[sys.argv[1]]()
