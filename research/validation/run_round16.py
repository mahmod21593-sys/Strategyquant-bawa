"""Round 16 (PREREGISTRATION.md A30): a VIX-free stress regime from US500 bars (FTMO has no VIX), and A29 re-run
without the same-day VIX look-ahead for ^N225.

    python3 run_round16.py   -> results/round16_regime_proxy.json
"""
from __future__ import annotations

import bisect
import json
import math
import os
from datetime import date

import numpy as np

import multitest as mt
import run_family_a as fa
from data_yahoo import daily
from run_round4 import irx_map

OUT = os.path.join(os.path.dirname(__file__), "results")
START, CAL_END, LATE = date(2007, 7, 1), date(2016, 12, 31), date(2017, 1, 1)


def us_regimes():
    """{name: {US date: stress bool}} for VIX/VIX3M and the four US500 proxies (thresholds matched to the VIX
    regime's 2007-07..2016 stress share)."""
    g = [r for r in daily("^GSPC") if r["date"] <= fa.END]
    gd = [r["date"] for r in g]
    c = np.array([r["c"] for r in g])
    h, l = np.array([r["h"] for r in g]), np.array([r["l"] for r in g])
    r_ = np.r_[0.0, c[1:] / c[:-1] - 1]
    n = len(c)
    tr = np.r_[h[0] - l[0], np.maximum(h[1:], c[:-1]) - np.minimum(l[1:], c[:-1])]
    p = {k: np.full(n, np.nan) for k in ("RVR", "ATRR", "DD", "RVL")}
    for i in range(60, n):
        p["RVR"][i] = r_[i - 4:i + 1].std(ddof=1) / r_[i - 59:i + 1].std(ddof=1)
        p["ATRR"][i] = tr[i - 4:i + 1].mean() / tr[i - 49:i + 1].mean()
        p["DD"][i] = 1 - c[i] / c[i - 59:i + 1].max()
        p["RVL"][i] = r_[i - 19:i + 1].std(ddof=1) * math.sqrt(252)
    vix = {x["date"]: x["c"] for x in daily("^VIX")}
    v3 = {x["date"]: x["c"] for x in daily("^VIX3M")}
    vreg = {x: vix[x] / v3[x] >= 1.0 for x in gd if x in vix and x in v3}
    cal_idx = [i for i, x in enumerate(gd) if START <= x <= CAL_END and x in vreg]
    share = float(np.mean([vreg[gd[i]] for i in cal_idx]))
    out = {"VIX": vreg}
    meta = {"vix_stress_share_2007_2016": share}
    vb = np.array([vreg[gd[i]] for i in cal_idx], dtype=float)
    for k, v in p.items():
        th = float(np.nanquantile(v[cal_idx], 1 - share))
        out[k] = {x: bool(v[i] >= th) for i, x in enumerate(gd) if np.isfinite(v[i])}
        pb = np.array([out[k].get(gd[i], False) for i in cal_idx], dtype=float)
        late = [i for i, x in enumerate(gd) if x >= LATE and x in vreg and np.isfinite(v[i])]
        agree_late = float(np.mean([out[k][gd[i]] == vreg[gd[i]] for i in late]))
        vl = np.array([vreg[gd[i]] for i in late], dtype=float)
        pl = np.array([out[k][gd[i]] for i in late], dtype=float)
        meta[k] = {"threshold": th, "phi_2007_2016": float(np.corrcoef(vb, pb)[0, 1]), "phi_2017_2026": float(np.corrcoef(vl, pl)[0, 1]),
                   "agreement_2017_2026": agree_late, "stress_share_2017_2026": float(pl.mean())}
    meta["primary_proxy"] = max(("RVR", "ATRR", "DD", "RVL"), key=lambda k: meta[k]["phi_2007_2016"])
    return out, sorted(gd), meta


def as_of(regime, us_dates, x, strictly_before):
    """Regime known at a signal close on date x: the same US date (US markets) or the previous US date (^N225)."""
    j = (bisect.bisect_left(us_dates, x) if strictly_before else bisect.bisect_right(us_dates, x)) - 1
    if j < 0 or (x - us_dates[j]).days > 5:
        return None
    return regime.get(us_dates[j])


def evaluate(syms, regimes, us_dates, strictly_before, rates, keys):
    cal = sorted({r["date"] for s in syms for r in daily(s) if START <= r["date"] <= fa.END and r["date"].weekday() < 5})
    ci = {x: i for i, x in enumerate(cal)}
    names = list(regimes)
    cols_all, cols_calm = [], {k: [] for k in names}
    trades = {k: {"STRESS": [], "CALM": []} for k in names}
    trades_late = {k: {"STRESS": [], "CALM": []} for k in names}
    for sym in syms:
        d, c, h, l, craw, ret, rf = fa.load(sym, rates, keys)
        sig, filt = fa.signals(c, h, l, craw, ret)
        yr = np.array([x.year for x in d])
        ex = ret - rf
        ymu = {y: float(ex[yr == y].mean()) for y in set(yr.tolist())}
        mu = np.array([ymu[y] for y in yr])
        st = {k: np.array([bool(as_of(regimes[k], us_dates, x, strictly_before)) for x in d]) for k in names}
        keep = np.array([START <= x and x in ci for x in d])
        idx = np.array([ci[x] for x, k_ in zip(d, keep) if k_])
        mark = fa.MARKUP if sym in fa.US else 0.0
        n = len(d)
        for sn in fa.SIGNALS:
            for exr in fa.EXITS:
                for fn in fa.FILTERS:
                    pos, entry = fa.positions(sig[sn], filt[fn], c, exr)
                    tv = pos * ex - pos * mark - entry * fa.COST - pos * mu
                    col = np.zeros(len(cal))
                    col[idx] = tv[keep]
                    cols_all.append(col)
                    # trade id per held day and the regime at its signal close
                    tid = np.full(n, -1)
                    starts = []
                    cur = -1
                    for i in range(n):
                        if entry[i]:
                            cur = i
                            starts.append(i)
                        tid[i] = cur if pos[i] else -1
                    for k in names:
                        stress_trade = {s_: bool(st[k][s_ - 1]) for s_ in starts}
                        calm = np.array([pos[i] > 0 and not stress_trade[tid[i]] for i in range(n)])
                        cc = np.zeros(len(cal))
                        cc[idx] = np.where(calm, tv, 0.0)[keep]
                        cols_calm[k].append(cc)
                        for s_ in starts:
                            if not keep[s_]:
                                continue
                            j = s_
                            tot = 0.0
                            while j < n and pos[j] and tid[j] == s_:
                                tot += tv[j]
                                j += 1
                            lab = "STRESS" if stress_trade[s_] else "CALM"
                            trades[k][lab].append(tot)
                            if d[s_] >= LATE:
                                trades_late[k][lab].append(tot)
        print("  ", sym, flush=True)
    A = np.array(cols_all).T
    sd = A.std(0, ddof=1)
    w = np.where(sd > 0, 1 / np.where(sd > 0, sd, 1), 0)
    w /= w.sum()
    ea = A @ w
    late = np.array([x >= LATE for x in cal])
    out = {}
    for k in names:
        ec = np.array(cols_calm[k]).T @ w
        res_k = {}
        for lab, m in (("full", np.ones(len(cal), dtype=bool)), ("2017_2026", late)):
            a_, c_ = ea[m], ec[m]
            W = mt.boot_weights(len(a_), 10, 2000, seed=5)

            def srb(v):
                m1 = W @ v / len(v)
                m2 = W @ (v * v) / len(v)
                return m1 / np.sqrt(np.maximum(m2 - m1 * m1, 1e-18)) * math.sqrt(252)
            dd_ = srb(c_) - srb(a_)
            tr_ = trades[k] if lab == "full" else trades_late[k]
            res_k[lab] = {"sharpe_all": float(mt.sharpe(a_[:, None], 252)[0]), "sharpe_calm_only": float(mt.sharpe(c_[:, None], 252)[0]),
                          "diff": float(mt.sharpe(c_[:, None], 252)[0] - mt.sharpe(a_[:, None], 252)[0]),
                          "ci95": [float(np.quantile(dd_, 0.025)), float(np.quantile(dd_, 0.975))],
                          "worst_day_all_bps": float(a_.min() * 1e4), "worst_day_calm_bps": float(c_.min() * 1e4),
                          "per_trade_bps": {r: {"n": len(v), "mean": float(np.mean(v) * 1e4) if v else None} for r, v in tr_.items()}}
        out[k] = res_k
    return out


def main():
    rates = irx_map()
    keys = sorted(rates)
    regimes, us_dates, meta = us_regimes()
    print(json.dumps(meta, indent=1), flush=True)
    res = {"proxies": meta}
    for group, syms, lag in (("N225", ("^N225",), True), ("US", fa.US, False)):
        print(group, flush=True)
        res[group] = evaluate(syms, regimes, us_dates, lag, rates, keys)
        for k, v in res[group].items():
            print(group, k, json.dumps(v), flush=True)
    vfull, pl = res["N225"]["VIX"]["full"], res["N225"][meta["primary_proxy"]]["2017_2026"]
    res["jp225_filter_recommended"] = bool(vfull["ci95"][0] > 0 and pl["diff"] > 0)
    json.dump(res, open(os.path.join(OUT, "round16_regime_proxy.json"), "w"), indent=1)
    print("JP225 filter recommended:", res["jp225_filter_recommended"], "primary proxy:", meta["primary_proxy"])


if __name__ == "__main__":
    main()
