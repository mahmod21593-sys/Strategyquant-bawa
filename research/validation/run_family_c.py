"""Round 9, family C (A22): time-series trend on G6's 17 ETFs + BTC, 48 portfolio-level variants.
-> results/family_c.json; P&L matrix -> $ROUND9_DIR/family_c.npz"""
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
from run_round7 import G6_UNIVERSE

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
START, SPLIT, END = date(2005, 1, 1), date(2017, 1, 1), date(2026, 8, 31)
LOOKBACKS = (21, 63, 126, 252)
SIGNALS = ("sign", "sma", "cross")
SIZING = ("vol40", "equal")
REBAL = ("monthly", "weekly")


def main():
    os.makedirs(R9, exist_ok=True)
    rates = irx_map()
    keys = sorted(rates)
    cal = sorted({r["date"] for r in daily("SPY") if START <= r["date"] <= END})
    ci = {d: i for i, d in enumerate(cal)}
    T, A = len(cal), len(G6_UNIVERSE)
    px = np.full((T, A), np.nan)
    ex = np.zeros((T, A))
    for j, s in enumerate(G6_UNIVERSE):
        rows = [r for r in daily(s) if START <= r["date"] <= END]
        last = None
        for r in rows:
            d = r["date"]
            if d.weekday() >= 5:
                continue  # BTC weekend moves accrue into the next weekday close
            if d in ci:
                i = ci[d]
                px[i, j] = r["adj"]
                if last is not None:
                    ex[i, j] = r["adj"] / last[1] - 1 - tbill(rates, keys, last[0], d)
                last = (d, r["adj"])
    # forward-fill prices for signals
    for j in range(A):
        for i in range(1, T):
            if np.isnan(px[i, j]):
                px[i, j] = px[i - 1, j]
    vol = np.full((T, A), np.nan)
    delta = 60 / 61
    for j in range(A):
        m = v = None
        for i in range(T):
            x = ex[i, j]
            if np.isnan(px[i, j]):
                continue
            m = x if m is None else delta * m + (1 - delta) * x
            v = x * x if v is None else delta * v + (1 - delta) * (x - m) ** 2
            vol[i, j] = math.sqrt(v * 261)
    ym = [(d.year, d.month) for d in cal]
    yw = [d.isocalendar()[:2] for d in cal]
    yrs = np.array([d.year for d in cal])
    mu = np.zeros((T, A))  # same-year mean daily excess return per asset (timing-value benchmark, A22 amendment)
    for y in set(yrs):
        m = yrs == y
        mu[m] = np.nanmean(np.where(np.isnan(px[m]), np.nan, ex[m]), axis=0)
    mu = np.nan_to_num(mu)
    exz = np.nan_to_num(ex)
    have = (~np.isnan(px)).astype(float)
    csum = np.vstack([np.zeros(A), np.cumsum(exz * have, axis=0)[:-1]])
    cnt = np.vstack([np.zeros(A), np.cumsum(have, axis=0)[:-1]])
    mu_exp = np.where(cnt >= 252, csum / np.maximum(cnt, 1), 0.0)
    cols, raw, adj, expd, turnover = [], [], [], [], []
    for L in LOOKBACKS:
        for sg in SIGNALS:
            for sz in SIZING:
                for rb in REBAL:
                    period = ym if rb == "monthly" else yw
                    pos = np.zeros((T, A))
                    cur = np.zeros(A)
                    for i in range(1, T):
                        if period[i] != period[i - 1]:  # rebalance on the first day of the period with the prior close's information
                            k = i - 1
                            new = np.zeros(A)
                            for j in range(A):
                                if k < L + 60 or np.isnan(px[k - L, j]) or np.isnan(vol[k, j]):
                                    continue
                                if sg == "sign":
                                    sgn = 1 if px[k, j] / px[k - L, j] > 1 else -1
                                elif sg == "sma":
                                    sgn = 1 if px[k, j] > np.nanmean(px[k - L + 1:k + 1, j]) else -1
                                else:
                                    sgn = 1 if np.nanmean(px[k - L // 4 + 1:k + 1, j]) > np.nanmean(px[k - L + 1:k + 1, j]) else -1
                                new[j] = sgn * (0.40 / vol[k, j] if sz == "vol40" else 1.0)
                            n = (new != 0).sum()
                            cur = new / n if n else new
                        pos[i] = cur
                    dpos = np.vstack([np.zeros(A), np.diff(pos, axis=0)])
                    cost = 2e-4 * np.abs(dpos).sum(1)
                    raw.append((pos * ex).sum(1) - cost)
                    adj.append((pos * (ex - mu)).sum(1) - cost)
                    expd.append((pos * (ex - mu_exp)).sum(1) - cost)
                    turnover.append(float(np.abs(pos).sum(1).mean()))
                    cols.append(f"L{L}|{sg}|{sz}|{rb}")
    X, XA, XE = np.array(raw).T, np.array(adj).T, np.array(expd).T
    np.savez_compressed(os.path.join(R9, "family_c.npz"), X=X, XA=XA, XE=XE, dates=np.array([d.toordinal() for d in cal]), cols=np.array(cols))
    first = next(i for i in range(T) if np.abs(X[i]).sum() > 0)
    X, XA, XE, calx = X[first:], XA[first:], XE[first:], cal[first:]
    years = np.array([d.year for d in calx])
    val = np.array([d >= SPLIT for d in calx])
    from run_family_a import battery
    res = {"n_variants": len(cols), "first_active": str(calx[0]), "mean_gross_exposure": dict(zip(cols, turnover))}
    for label, M in (("timing_same_year_invalid", XA), ("raw", X), ("timing_expanding", XE)):
        res[label] = battery(M, cols, ~val, val, years, first_wf=2017)
    res["variants"] = [{"name": c, "sharpe_discovery": a, "sharpe_validation": v, "timing_sharpe_validation": va, "rw_p_raw": p, "rw_p_timing": pa}
                       for c, a, v, va, p, pa in zip(cols, res["raw"]["_sr_d"], res["raw"]["_sr_v"], res["timing_expanding"]["_sr_v"], res["raw"]["_p_rw"], res["timing_expanding"]["_p_rw"])]
    for label in ("timing_same_year_invalid", "raw", "timing_expanding"):
        for k in ("_sr_d", "_sr_v", "_p_rw"):
            res[label].pop(k)
    res["family_verdict"] = res["raw"]["verdict"]
    json.dump(res, open(os.path.join(OUT, "family_c.json"), "w"), indent=1, default=str)
    for label in ("raw", "timing_expanding"):
        b = res[label]
        print(label, {k: b[k] for k in ("spa_validation", "pbo_full_sample", "selection_test", "walk_forward_top5", "best_validation_variant", "verdict")})
        print(label, "RW significant", b["romano_wolf_significant_5pct"])
    for v in sorted(res["variants"], key=lambda v: -v["sharpe_validation"])[:10]:
        print(v["name"], round(v["sharpe_discovery"], 2), round(v["sharpe_validation"], 2), round(v["timing_sharpe_validation"], 2))


if __name__ == "__main__":
    main()
