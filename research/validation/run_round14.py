"""Round 14 (PREREGISTRATION.md A28).

    python3 run_round14.py CT   COT positioning sentiment (Wang 2001)              -> results/family_ct.json
    python3 run_round14.py XR   the US index rebound traded through FX and gold    -> results/family_xr.json
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys
import zipfile
from bisect import bisect_left
from datetime import date, timedelta

import numpy as np

import run_family_a as fa
from data_yahoo import daily
from run_round4 import irx_map
from run_round10 import book_matrix, expanding_mean, finish, fx_daily, weekday_calendar
from run_round11 import positions_up
from run_round13 import fx_bars

OUT = os.path.join(os.path.dirname(__file__), "results")
COT = os.environ.get("COT_CACHE", "/tmp/cot_cache")
fa.N_TRIALS = 13013
SPLIT = date(2014, 1, 1)
END = date(2026, 8, 31)
MAJORS = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD")


def fetch_cot():
    os.makedirs(COT, exist_ok=True)
    files = ["deacot1986_2016.zip"] + [f"deacot{y}.zip" for y in range(2017, 2027)]
    for f in files:
        p = os.path.join(COT, f)
        if not os.path.exists(p) or not zipfile.is_zipfile(p):
            import subprocess
            subprocess.run(["curl", "-sS", "-m", "120", "-A", "Mozilla/5.0", "-o", p, f"https://www.cftc.gov/files/dea/history/{f}"], check=True)
    return [os.path.join(COT, f) for f in files]


def cot_series(codes):
    """{code: [(as-of date, open interest, noncomm long, noncomm short, comm long, comm short)]} sorted, de-duplicated."""
    out = {c: {} for c in codes}
    for path in fetch_cot():
        z = zipfile.ZipFile(path)
        for n in z.namelist():
            r = csv.reader(io.TextIOWrapper(z.open(n), encoding="latin-1"))
            head = [h.strip() for h in next(r)]
            ix = {k: head.index(k) for k in ("As of Date in Form YYYY-MM-DD", "CFTC Contract Market Code", "Open Interest (All)",
                                             "Noncommercial Positions-Long (All)", "Noncommercial Positions-Short (All)",
                                             "Commercial Positions-Long (All)", "Commercial Positions-Short (All)")}
            for row in r:
                code = row[ix["CFTC Contract Market Code"]].strip()
                if code not in out:
                    continue
                d = date.fromisoformat(row[ix["As of Date in Form YYYY-MM-DD"]].strip())
                vals = [float(row[ix[k]]) for k in ("Open Interest (All)", "Noncommercial Positions-Long (All)", "Noncommercial Positions-Short (All)",
                                                     "Commercial Positions-Long (All)", "Commercial Positions-Short (All)")]
                out[code][d] = vals
    return {c: sorted((d, *v) for d, v in m.items()) for c, m in out.items()}


# contract code -> (instrument, sign of the spot position for a long futures position)
CT_MAP = {"099741": ("EURUSD", 1), "097741": ("USDJPY", -1), "096742": ("GBPUSD", 1), "092741": ("USDCHF", -1), "090741": ("USDCAD", -1),
          "232741": ("AUDUSD", 1), "112741": ("NZDUSD", 1), "088691": ("XAUUSD", 1), "084691": ("XAGUSD", 1), "13874A": ("SPY", 1),
          "209742": ("QQQ", 1)}


def price_series(inst, rates, keys):
    """(dates, return, risk-free, cost, mark-up per calendar day, financing uses calendar gap)."""
    if inst in ("SPY", "QQQ"):
        d, c, h, l, craw, ret, rf = fa.load(inst, rates, keys)
        keep = np.array([date(2003, 1, 1) <= x <= END for x in d])
        return [x for x, k in zip(d, keep) if k], ret[keep], rf[keep], fa.COST, fa.MARKUP, False
    if inst in MAJORS:
        rows = [r for r in fx_daily(inst) if r["date"] <= END]
        d = [r["date"] for r in rows]
        c = np.array([r["c"] for r in rows])
    else:
        d, o, h, l, c = fx_bars(inst)
        keep = np.array([x <= END for x in d])
        d, c = [x for x, k in zip(d, keep) if k], c[keep]
    ret = np.r_[0.0, c[1:] / c[:-1] - 1]
    cost = {"XAUUSD": 2.5e-4, "XAGUSD": 5.0e-4}.get(inst, 1.0e-4)
    mark = (0.02 if inst in ("XAUUSD", "XAGUSD") else 0.005) / 365
    return d, ret, np.zeros(len(d)), cost, mark, True


def family_ct():
    rates = irx_map()
    keys = sorted(rates)
    series = cot_series(CT_MAP)
    per, per_e = [], []
    for code, (inst, sgn) in CT_MAP.items():
        d, ret, rf, cost, mark, calgap = price_series(inst, rates, keys)
        n = len(d)
        gap = np.r_[1.0, [(d[i] - d[i - 1]).days for i in range(1, n)]] if calgap else np.ones(n)
        ex = ret - rf
        mu = expanding_mean(ex)
        rep = series[code]
        dd, ddE = {}, {}
        for grp, (li, si) in (("SPEC", (2, 3)), ("HEDG", (4, 5))):
            np_ = np.array([(r[li] - r[si]) / r[1] if r[1] > 0 else np.nan for r in rep])
            sidx = np.full(len(rep), np.nan)
            for k in range(155, len(rep)):
                w = np_[k - 155:k + 1]
                lo, hi = np.nanmin(w), np.nanmax(w)
                if hi > lo:
                    sidx[k] = (np_[k] - lo) / (hi - lo)
            trade_idx = [bisect_left(d, r[0] + timedelta(days=6)) for r in rep]
            for th in (0.9, 0.8):
                for how in ("WITH", "AGAINST"):
                    for hold in (5, 10, 20):
                        pos, entry = np.zeros(n), np.zeros(n)
                        busy = -1
                        for k, e in enumerate(trade_idx):
                            s = 1 if sidx[k] >= th else -1 if sidx[k] <= 1 - th else 0
                            if s == 0 or e >= n - 1 or e < busy:
                                continue
                            dr = s * sgn * (1 if how == "WITH" else -1)
                            last = min(e + hold, n - 1)
                            pos[e + 1:last + 1] = dr
                            entry[e + 1] = 1
                            busy = last
                        pnl = pos * ex - np.abs(pos) * mark * gap - entry * cost
                        name = f"{inst}|{grp}|t{int(th * 100)}|{how}|H{hold}"
                        dd[name] = pnl
                        ddE[name] = pnl - pos * mu
        per.append((d, dd))
        per_e.append((d, ddE))
        print("CT", inst, len(rep), rep[0][0], flush=True)
    cal = weekday_calendar(date(2003, 1, 1), END)
    X, names = book_matrix(per, cal)
    XE, _ = book_matrix(per_e, cal)
    return finish("CT", X, XE, names, cal, SPLIT, 2014)


XR_LEGS = (("AUDJPY", 1), ("NZDJPY", 1), ("CADJPY", 1), ("EURJPY", 1), ("USDJPY", 1), ("AUDUSD", 1), ("NZDUSD", 1), ("USDCHF", 1),
           ("XAUUSD", 1), ("XAUUSD", -1))


def family_xr():
    g = [r for r in daily("^GSPC") if r["date"] <= END]
    gd = [r["date"] for r in g]
    gc = np.array([r["c"] for r in g])
    gh, gl = np.array([r["h"] for r in g]), np.array([r["l"] for r in g])
    gret = np.r_[0.0, gc[1:] / gc[:-1] - 1]
    sig, _ = fa.signals(gc, gh, gl, gc, gret)
    up = {x: bool(gc[i] > gc[i - 1]) for i, x in enumerate(gd) if i > 0}
    per, per_e = [], []
    for inst, side in XR_LEGS:
        if inst in MAJORS:
            rows = [r for r in fx_daily(inst) if date(2008, 1, 1) <= r["date"] <= END]
            d, c = [r["date"] for r in rows], np.array([r["c"] for r in rows])
        else:
            d, o, h, l, c = fx_bars(inst)
            keep = np.array([date(2008, 1, 1) <= x <= END for x in d])
            d, c = [x for x, k in zip(d, keep) if k], c[keep]
        n = len(d)
        ret = np.r_[0.0, c[1:] / c[:-1] - 1]
        gap = np.r_[1.0, [(d[i] - d[i - 1]).days for i in range(1, n)]]
        cost = 2.5e-4 if inst == "XAUUSD" else 2.0e-4 if inst.endswith("JPY") and inst != "USDJPY" else 1.0e-4
        mark = (0.02 if inst == "XAUUSD" else 0.005) / 365
        mu = expanding_mean(ret)
        gi = {x: i for i, x in enumerate(gd)}
        upfx = np.array([up.get(x, False) for x in d])
        dd, ddE = {}, {}
        for sn in ("I10", "R10", "K3", "L5"):
            s_fx = np.array([bool(sig[sn][gi[x]]) if x in gi else False for x in d])
            for ex in ("X1", "XU"):
                pos, entry = positions_up(s_fx, np.ones(n, dtype=bool), upfx, ex)
                pos = side * pos
                pnl = pos * ret - np.abs(pos) * mark * gap - entry * cost
                name = f"{inst}{'' if side == 1 else '_SHORT'}|{sn}|{ex}"
                dd[name] = pnl
                ddE[name] = pnl - pos * mu
        per.append((d, dd))
        per_e.append((d, ddE))
        print("XR", inst, side, n, flush=True)
    cal = weekday_calendar(date(2008, 1, 1), END)
    X, names = book_matrix(per, cal)
    XE, _ = book_matrix(per_e, cal)
    return finish("XR", X, XE, names, cal, SPLIT, 2014)


if __name__ == "__main__":
    {"CT": family_ct, "XR": family_xr}[sys.argv[1]]()
