"""Round 9, family A (PREREGISTRATION.md A22): short-term reversal in equity indices, 864 variants.

-> results/family_a.json; variant P&L matrix -> $ROUND9_DIR/family_a.npz (for the portfolio stage)
"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import numpy as np

import multitest as mt
import vstats as vs
from data_yahoo import daily
from run_round4 import irx_map, tbill

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
US = ("SPY", "QQQ", "DIA", "IWM")
WORLD = ("^GDAXI", "^FTSE", "^N225", "^AXJO")
START, SPLIT, END = date(1993, 2, 1), date(2013, 1, 1), date(2026, 8, 31)
SIGNALS = ["K2", "K3", "K4", "K5", "R5", "R10", "R20", "I10", "I25", "L5", "L10", "D15"]
EXITS = ["X1", "XU", "X3"]
FILTERS = ["F0", "UP", "DN"]
COST, MARKUP = 1.5e-4, 1e-4
N_TRIALS = 747 + 1246


def load(sym, rates, keys):
    rows = [r for r in daily(sym) if START <= r["date"] <= END]
    d = [r["date"] for r in rows]
    c = np.array([r["adj"] for r in rows])
    h = np.array([r["h"] for r in rows])
    l = np.array([r["l"] for r in rows])
    craw = np.array([r["c"] for r in rows])
    ret = np.zeros(len(c))
    ret[1:] = c[1:] / c[:-1] - 1
    rf = np.zeros(len(c))
    for i in range(1, len(d)):
        rf[i] = tbill(rates, keys, d[i - 1], d[i])
    return d, c, h, l, craw, ret, rf


def rsi2(c):
    out = np.full(len(c), 50.0)
    g = l_ = None
    for i in range(1, len(c)):
        ch = c[i] - c[i - 1]
        up, dn = max(ch, 0), max(-ch, 0)
        if g is None:
            g, l_ = up, dn
        else:
            g, l_ = (g + up) / 2, (l_ + dn) / 2
        out[i] = 100.0 if l_ == 0 else 100 - 100 / (1 + g / l_)
    return out


def signals(c, h, l, craw, ret):
    n = len(c)
    s = {}
    down = np.zeros(n, dtype=bool)
    down[1:] = c[1:] < c[:-1]
    run = np.zeros(n, dtype=int)
    for i in range(1, n):
        run[i] = run[i - 1] + 1 if down[i] else 0
    for k in (2, 3, 4, 5):
        s[f"K{k}"] = run >= k
    r = rsi2(c)
    for lvl in (5, 10, 20):
        s[f"R{lvl}"] = r < lvl
    rng_ = h - l
    ibs = np.where(rng_ > 0, (craw - l) / np.where(rng_ > 0, rng_, 1), 0.5)
    s["I10"], s["I25"] = ibs < 0.10, ibs < 0.25
    for N in (5, 10):
        low = np.zeros(n, dtype=bool)
        for i in range(N - 1, n):
            low[i] = c[i] <= c[i - N + 1:i + 1].min()
        s[f"L{N}"] = low
    vol = np.full(n, np.nan)
    for i in range(21, n):
        vol[i] = ret[i - 19:i + 1].std(ddof=1)
    s["D15"] = np.nan_to_num(ret < -1.5 * np.nan_to_num(vol, nan=np.inf))
    sma = np.full(n, np.nan)
    cs = np.cumsum(c)
    sma[199:] = (cs[199:] - np.concatenate([[0], cs[:-200]])) / 200
    filt = {"F0": np.ones(n, dtype=bool), "UP": np.nan_to_num(c > sma), "DN": np.nan_to_num(c < sma)}
    for k in s:
        s[k][:200] = False  # common warm-up so every variant starts together
    return s, filt


def positions(sig, flt, c, exit_rule):
    n = len(c)
    pos = np.zeros(n)
    entry = np.zeros(n)
    i = 0
    while i < n - 1:
        if sig[i] and flt[i]:
            j = i + 1
            entry[j] = 1
            if exit_rule == "X1":
                last = j
            elif exit_rule == "X3":
                last = min(i + 3, n - 1)
            else:
                last = j
                while last < min(i + 5, n - 1) and not (c[last] > c[last - 1]):
                    last += 1
            pos[j:last + 1] = 1
            i = last  # the exit close can be a new entry close
            continue
        i += 1
    return pos, entry


def aspects(d, pnl, pos):
    """Descriptive P&L of held days by weekday, month, year (for SQX parameter choices; post hoc)."""
    held = pos > 0
    out = {"weekday": {}, "month": {}, "year": {}}
    for key, f in (("weekday", lambda x: x.weekday()), ("month", lambda x: x.month), ("year", lambda x: x.year)):
        g = {}
        for dd, p, h in zip(d, pnl, held):
            if h:
                g.setdefault(f(dd), []).append(p * 1e4)
        out[key] = {k: {"n": len(v), "mean_bps": round(float(np.mean(v)), 2)} for k, v in sorted(g.items())}
    return out


def battery(X, cols, disc, val, years, first_wf=2013):
    """The A22 battery on one P&L matrix."""
    sr_d, sr_v = mt.sharpe(X[disc], 252), mt.sharpe(X[val], 252)
    out = {"spa_validation": mt.spa(X[val], 10, 2000)}
    out["spa_validation"]["best"] = cols[out["spa_validation"]["best_index"]]
    p_rw, t_rw = mt.romano_wolf(X[val], 10, 2000)
    out["romano_wolf_significant_5pct"] = [cols[k] for k in np.argsort(p_rw) if p_rw[k] < 0.05]
    out["pbo_full_sample"] = mt.pbo(X, 16)
    top = sr_d >= np.quantile(sr_d, 0.9)
    out["selection_test"] = {"validation_sharpe_top10pct_median": float(np.median(sr_v[top])), "validation_sharpe_rest_median": float(np.median(sr_v[~top])),
                             "mann_whitney_z": mt.mann_whitney_z(sr_v[top], sr_v[~top])}
    wf = mt.walk_forward(X, years, first_wf, 5, 252 * 5)[val]
    out["walk_forward_top5"] = {"sharpe": float(wf.mean() / wf.std(ddof=1) * math.sqrt(252)), "t_hac": vs.nw_t(list(wf), 5),
                                "mean_bps_per_day": float(wf.mean() * 1e4)}
    b = int(np.argmax(sr_v))
    out["best_validation_variant"] = {"name": cols[b], "sharpe": float(sr_v[b]), "dsr": vs.deflated_sharpe(list(X[val][:, b]), N_TRIALS)}
    per_inst = {}
    for sym in sorted({c.split("|")[0] for c in cols}):
        ks = [i for i, cn in enumerate(cols) if cn.startswith(sym + "|")]
        s_ = mt.spa(X[val][:, ks], 10, 2000)
        per_inst[sym] = {"p_spa": s_["p_spa"], "best": cols[ks[s_["best_index"]]], "rw_significant": int(sum(p_rw[k] < 0.05 for k in ks)),
                         "median_validation_sharpe": float(np.median(sr_v[ks])), "share_validation_sharpe_positive": float((sr_v[ks] > 0).mean())}
    out["per_instrument"] = per_inst
    sp, pb, wfr = out["spa_validation"]["p_spa"], out["pbo_full_sample"]["pbo"], out["walk_forward_top5"]["sharpe"]
    out["verdict"] = "EDGE FAMILY" if sp < 0.05 and pb < 0.5 and wfr > 0 else "WEAK FAMILY" if sp < 0.10 or wfr > 0 else "NO EDGE"
    out["_sr_d"], out["_sr_v"], out["_p_rw"] = [float(x) for x in sr_d], [float(x) for x in sr_v], [float(x) for x in p_rw]
    return out


def main():
    os.makedirs(R9, exist_ok=True)
    rates = irx_map()
    keys = sorted(rates)
    cal = sorted({r["date"] for s in US + WORLD for r in daily(s) if START <= r["date"] <= END and r["date"].weekday() < 5})
    ci = {x: i for i, x in enumerate(cal)}
    cols, mats, adjm, expm, meta, asp = [], [], [], [], [], {}
    for sym in US + WORLD:
        d, c, h, l, craw, ret, rf = load(sym, rates, keys)
        sig, filt = signals(c, h, l, craw, ret)
        idx = np.array([ci[x] for x in d if x in ci])
        keep = np.array([x in ci for x in d])
        mark = MARKUP if sym in US else 0.0
        yr = np.array([x.year for x in d])
        ymean = {y: float((ret - rf)[yr == y].mean()) for y in set(yr)}
        mu = np.array([ymean[y] for y in yr])
        exr = ret - rf
        csum = np.concatenate([[0.0], np.cumsum(exr)[:-1]])
        cnt = np.arange(len(exr), dtype=float)
        mu_exp = np.where(cnt >= 252, csum / np.maximum(cnt, 1), 0.0)
        for sn in SIGNALS:
            for ex in EXITS:
                for fn in FILTERS:
                    pos, entry = positions(sig[sn], filt[fn], c, ex)
                    pnl = pos * (ret - rf) - pos * mark - entry * COST
                    col = np.zeros(len(cal))
                    col[idx] = pnl[keep]
                    acol = np.zeros(len(cal))
                    acol[idx] = (pnl - pos * mu)[keep]
                    adjm.append(acol)
                    ecol = np.zeros(len(cal))
                    ecol[idx] = (pnl - pos * mu_exp)[keep]
                    expm.append(ecol)
                    name = f"{sym}|{sn}|{ex}|{fn}"
                    cols.append(name)
                    mats.append(col)
                    meta.append({"name": name, "instrument": sym, "signal": sn, "exit": ex, "filter": fn,
                                 "trades_per_year": float(entry.sum() / (len(d) / 252)), "exposure": float(pos.mean())})
                    if sn == "K3" and ex == "X1" and fn == "F0":
                        asp[sym] = aspects(d, pnl, pos)
        print(sym, "done", flush=True)
    X = np.array(mats).T
    XA = np.array(adjm).T
    XE = np.array(expm).T
    dates = np.array([x.toordinal() for x in cal])
    np.savez_compressed(os.path.join(R9, "family_a.npz"), X=X, XA=XA, XE=XE, dates=dates, cols=np.array(cols))
    years = np.array([x.year for x in cal])
    disc = np.array([x < SPLIT for x in cal])
    val = ~disc
    res = {"n_variants": X.shape[1], "calendar": [str(cal[0]), str(cal[-1])], "aspects_K3_X1_F0": asp}
    for label, M in (("timing", XA), ("raw", X), ("timing_expanding", XE)):
        res[label] = battery(M, cols, disc, val, years)
    for m, sd_, sv, sva, p, pa in zip(meta, res["raw"]["_sr_d"], res["raw"]["_sr_v"], res["timing"]["_sr_v"], res["raw"]["_p_rw"], res["timing"]["_p_rw"]):
        m.update({"sharpe_discovery": sd_, "sharpe_validation": sv, "timing_sharpe_validation": sva, "rw_p_raw": p, "rw_p_timing": pa})
    for label in ("timing", "raw", "timing_expanding"):
        for k in ("_sr_d", "_sr_v", "_p_rw"):
            res[label].pop(k)
    res["variants"] = meta
    res["family_verdict"] = res["timing"]["verdict"]
    json.dump(res, open(os.path.join(OUT, "family_a.json"), "w"), indent=1, default=str)
    for label in ("timing", "raw", "timing_expanding"):
        b = res[label]
        print(label, json.dumps({k: b[k] for k in ("spa_validation", "pbo_full_sample", "selection_test", "walk_forward_top5", "best_validation_variant",
                                                    "verdict")}, indent=1, default=str))
        print(label, "RW significant", len(b["romano_wolf_significant_5pct"]), b["romano_wolf_significant_5pct"][:30])
        print(label, json.dumps(b["per_instrument"], indent=1, default=str))


if __name__ == "__main__":
    main()
