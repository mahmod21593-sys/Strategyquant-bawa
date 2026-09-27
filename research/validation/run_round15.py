"""Round 15 (PREREGISTRATION.md A29): the index-reversal edge by VIX term-structure regime (decision analysis).

    python3 run_round15.py   -> results/round15_regime.json
"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import numpy as np

import multitest as mt
import run_family_a as fa
import vstats as vs
from data_yahoo import daily
from run_round4 import irx_map

OUT = os.path.join(os.path.dirname(__file__), "results")
START = date(2007, 7, 1)


def welch(a, b):
    a, b = np.asarray(a), np.asarray(b)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return float((a.mean() - b.mean()) / se)


def main():
    rates = irx_map()
    keys = sorted(rates)
    vix = {r["date"]: r["c"] for r in daily("^VIX")}
    v3 = {r["date"]: r["c"] for r in daily("^VIX3M")}
    res = {}
    for group, syms in (("US", fa.US), ("N225", ("^N225",))):
        cal = sorted({r["date"] for s in syms for r in daily(s) if START <= r["date"] <= fa.END and r["date"].weekday() < 5})
        ci = {x: i for i, x in enumerate(cal)}
        cols_all, cols_calm, per_trade = [], [], {"STRESS": [], "CALM": []}
        for sym in syms:
            d, c, h, l, craw, ret, rf = fa.load(sym, rates, keys)
            sig, filt = fa.signals(c, h, l, craw, ret)
            yr = np.array([x.year for x in d])
            ex = ret - rf
            ymu = {y: float(ex[yr == y].mean()) for y in set(yr.tolist())}
            mu = np.array([ymu[y] for y in yr])
            # regime at each close (US VIX; for ^N225 the latest US close on or before the Tokyo date)
            vd = sorted(v3)
            import bisect
            stress = np.zeros(len(d), dtype=bool)
            for i, x in enumerate(d):
                j = bisect.bisect_right(vd, x) - 1
                if j >= 0 and vd[j] in vix and (x - vd[j]).days <= 4:
                    stress[i] = vix[vd[j]] / v3[vd[j]] >= 1.0
            keep = np.array([START <= x and x in ci for x in d])
            idx = np.array([ci[x] for x, k in zip(d, keep) if k])
            mark = fa.MARKUP if sym in fa.US else 0.0
            for sn in fa.SIGNALS:
                for exr in fa.EXITS:
                    for fn in fa.FILTERS:
                        pos, entry = fa.positions(sig[sn], filt[fn], c, exr)
                        pnl = pos * ex - pos * mark - entry * fa.COST
                        tv = pnl - pos * mu
                        # regime of each trade = regime at the signal close (the bar before the entry bar)
                        reg = np.zeros(len(d), dtype=bool)
                        cur = False
                        for i in range(len(d)):
                            if entry[i]:
                                cur = stress[i - 1]
                            reg[i] = cur if pos[i] else False
                        calm_mask = (pos > 0) & ~reg
                        for store, v in ((cols_all, tv), (cols_calm, np.where(calm_mask, tv, 0.0))):
                            col = np.zeros(len(cal))
                            col[idx] = v[keep]
                            store.append(col)
                        # per-trade timing value
                        i = 0
                        n = len(d)
                        while i < n:
                            if entry[i] and keep[i]:
                                j = i
                                s_ = 0.0
                                while j < n and pos[j] and (j == i or not entry[j]):
                                    s_ += tv[j]
                                    j += 1
                                per_trade["STRESS" if stress[i - 1] else "CALM"].append(s_)
                                i = j
                                continue
                            i += 1
            print(group, sym, flush=True)
        A, Cm = np.array(cols_all).T, np.array(cols_calm).T
        sd = A.std(0, ddof=1)
        w = np.where(sd > 0, 1 / np.where(sd > 0, sd, 1), 0)
        w /= w.sum()
        ea, ec = A @ w, Cm @ w
        W = mt.boot_weights(len(ea), 10, 2000, seed=5)

        def srb(v):
            m1 = W @ v / len(v)
            m2 = W @ (v * v) / len(v)
            return m1 / np.sqrt(np.maximum(m2 - m1 * m1, 1e-18)) * math.sqrt(252)

        dsr = srb(ec) - srb(ea)

        def dd(v):
            e = np.cumsum(v)
            return float((e - np.maximum.accumulate(e)).min())
        st, cm = np.array(per_trade["STRESS"]), np.array(per_trade["CALM"])
        res[group] = {"RG1_per_trade_timing_bps": {"STRESS": {"n": int(len(st)), "mean": float(st.mean() * 1e4)}, "CALM": {"n": int(len(cm)), "mean": float(cm.mean() * 1e4)},
                                                   "welch_t_stress_minus_calm": welch(st, cm)},
                      "RG2_ensemble": {"all": {"sharpe": float(mt.sharpe(ea[:, None], 252)[0]), "worst_day_bps": float(ea.min() * 1e4), "max_dd_bps": dd(ea) * 1e4,
                                               "mean_bps": float(ea.mean() * 1e4)},
                                       "calm_only": {"sharpe": float(mt.sharpe(ec[:, None], 252)[0]), "worst_day_bps": float(ec.min() * 1e4), "max_dd_bps": dd(ec) * 1e4,
                                                     "mean_bps": float(ec.mean() * 1e4)},
                                       "sharpe_diff_calm_minus_all": float(mt.sharpe(ec[:, None], 252)[0] - mt.sharpe(ea[:, None], 252)[0]),
                                       "ci95": [float(np.quantile(dsr, 0.025)), float(np.quantile(dsr, 0.975))]}}
        ok = res[group]["RG2_ensemble"]
        # A29 rule: CALM-only Sharpe not lower (upper end of the difference interval >= 0) and the worst day improves
        res[group]["recommend_calm_filter"] = bool(ok["ci95"][1] >= 0 and ok["calm_only"]["worst_day_bps"] > ok["all"]["worst_day_bps"])
        print(group, json.dumps(res[group], indent=1), flush=True)
    vd = sorted(v3)
    res["share_of_days_in_stress_2007_2026"] = float(np.mean([vix[x] / v3[x] >= 1.0 for x in vd if START <= x <= fa.END and x in vix]))
    json.dump(res, open(os.path.join(OUT, "round15_regime.json"), "w"), indent=1)
    print("stress share", res["share_of_days_in_stress_2007_2026"])


if __name__ == "__main__":
    main()
