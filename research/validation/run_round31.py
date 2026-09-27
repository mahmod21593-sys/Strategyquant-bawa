"""Round 31 (PREREGISTRATION.md A45): Kaufman's noise hypothesis (N1 cross-sectional, N2 time-series);
Davey's monkey tests and Pardo's walk-forward efficiency on the confirmed edges.

    python3 run_round31.py   -> results/round31_kaufman.json
"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import numpy as np

import vstats as vs
from data_yahoo import daily

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
E = date(1970, 1, 1).toordinal()
START, END = date(2013, 1, 1), date(2026, 8, 31)
MKTS = {"family_a": ("SPY", "QQQ", "DIA", "IWM", "^N225", "^GDAXI", "^FTSE", "^AXJO"),
        "family_j": ("^FCHI", "^HSI", "^IBEX", "^STOXX50E")}


def noise_series(sym):
    """{date: 1 - ER(10)} on adjusted closes."""
    rows = [r for r in daily(sym) if r["date"] <= END]
    d = [r["date"] for r in rows]
    c = np.array([r["c"] for r in rows])
    out = {}
    for i in range(10, len(c)):
        denom = float(np.abs(np.diff(c[i - 10:i + 1])).sum())
        if denom > 0:
            out[d[i]] = 1 - abs(c[i] - c[i - 10]) / denom
    return out


def spearman_perm(x, y, reps=10000, seed=17):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rho = float(np.corrcoef(rx, ry)[0, 1])
    rng = np.random.default_rng(seed)
    perm = [np.corrcoef(rx, rng.permutation(ry))[0, 1] for _ in range(reps)]
    p = float(np.mean([q >= rho for q in perm]))
    return rho, p


def main():
    res = {}
    # ------------------------------------------------ N1 cross-sectional
    sharpe = {}
    for fam, syms in MKTS.items():
        r = json.load(open(os.path.join("results", fam + ".json")))
        pi = r["raw"]["per_instrument"]
        for s in syms:
            sharpe[s] = pi[s]["median_validation_sharpe"]
    noise = {}
    for s in sharpe:
        ns = noise_series(s)
        noise[s] = float(np.mean([v for d, v in ns.items() if d >= START]))
    syms = sorted(sharpe)
    rho, p1 = spearman_perm(np.array([noise[s] for s in syms]), np.array([sharpe[s] for s in syms]))
    res["N1"] = {"spearman_rho": rho, "p_one_sided": p1, "n_markets": len(syms),
                 "table": {s: {"noise": round(noise[s], 4), "median_raw_val_sharpe": round(sharpe[s], 2)} for s in syms}}
    print("N1", rho, p1, flush=True)
    for s in sorted(syms, key=lambda q: -noise[q]):
        print("   ", s, round(noise[s], 4), round(sharpe[s], 2))
    # ------------------------------------------------ N2 time-series (SPY, QQQ)
    p = np.load(os.path.join(R9, "family_a.npz"))
    cal = [date.fromordinal(int(v)) for v in p["dates"]]
    cols = [str(c) for c in p["cols"]]
    hi_all, lo_all = [], []
    for sym in ("SPY", "QQQ"):
        idx = [i for i, c in enumerate(cols) if c.startswith(sym + "|")]
        M = p["XE"][:, idx]
        active = np.abs(M).sum(1) > 0
        ens = M.mean(1)
        ns = noise_series(sym)
        nd = sorted(d for d in ns if d >= date(2012, 1, 1))
        med = {}
        for i in range(252, len(nd)):
            med[nd[i]] = float(np.median([ns[nd[j]] for j in range(i - 252, i)]))
        prev = {}
        for i, d in enumerate(cal):
            if i > 0:
                prev[d] = cal[i - 1]
        for i, d in enumerate(cal):
            if not (START <= d <= END) or not active[i]:
                continue
            pd_ = prev.get(d)
            if pd_ is None or pd_ not in ns or pd_ not in med:
                continue
            (hi_all if ns[pd_] > med[pd_] else lo_all).append(float(ens[i]))
    se = math.sqrt(np.var(hi_all, ddof=1) / len(hi_all) + np.var(lo_all, ddof=1) / len(lo_all))
    t2 = float((np.mean(hi_all) - np.mean(lo_all)) / se)
    res["N2"] = {"high_noise_mean_bps": float(np.mean(hi_all) * 1e4), "low_noise_mean_bps": float(np.mean(lo_all) * 1e4),
                 "n": [len(hi_all), len(lo_all)], "t": t2, "p_one_sided": vs.p_one_sided(t2)}
    holm = vs.holm({"N1": res["N1"]["p_one_sided"], "N2": res["N2"]["p_one_sided"]})
    res["N1"]["p_holm"], res["N2"]["p_holm"] = holm["N1"], holm["N2"]
    res["KN_verdict"] = ("SUPPORTED" if all(h < 0.05 for h in holm.values()) else
                         "PARTIAL" if any(h < 0.05 for h in holm.values()) else "NOT SUPPORTED")
    print("N2", json.dumps(res["N2"]), res["KN_verdict"], flush=True)
    # ------------------------------------------------ MK: monkey tests
    rng = np.random.default_rng(23)
    mk = {}
    # REV monkeys: same number of long days, random weekdays, raw excess return
    from run_round4 import irx_map
    import run_family_a as fa
    rates = irx_map()
    keys = sorted(rates)
    for sym in ("SPY", "QQQ"):
        idx = [i for i, c in enumerate(cols) if c.startswith(sym + "|")]
        M = p["X"][:, idx]  # raw
        active = (np.abs(M).sum(1) > 0) & np.array([START <= d <= END for d in cal])
        d_, c_, h_, l_, craw, ret, rf = fa.load(sym, rates, keys)
        ex = {dd: float(r - f) for dd, r, f in zip(d_, ret, rf) if START <= dd <= END}
        # day-selection skill at unit exposure: the market's excess return on REV's active days vs random days
        act_days = [d for d, a in zip(cal, active) if a and d in ex]
        actual = float(np.mean([ex[dd] for dd in act_days]))
        vals = np.array([ex[dd] for dd in sorted(ex)])
        monkeys = np.array([vals[rng.integers(0, len(vals), len(act_days))].mean() for _ in range(2000)])
        mk[f"REV_{sym}"] = {"actual_bps": actual * 1e4, "monkey_mean_bps": float(monkeys.mean() * 1e4),
                            "percentile": float((monkeys < actual).mean() * 100), "n_days": len(act_days)}
    # N3 monkeys: random direction on the same sessions
    from run_noise_area import run as noise_run
    n3 = {dd: v for dd, v in noise_run("N3", path=False)[0] if START <= dd <= END}
    from data_minutes import local, price_at
    from data_histdata import NY
    t_, x_ = local("NSXUSD", range(2013, 2027), NY)
    dy, mo = t_ // 1440, t_ % 1440
    po, pc = price_at(dy, mo, x_, 570, prefer_open=True), price_at(dy, mo, x_, 959)
    ses = {date.fromordinal(int(k) + E): pc[k] / po[k] - 1 for k in po if k in pc}
    sv = np.array([v for dd, v in sorted(ses.items()) if START <= dd <= END])
    actual = float(np.mean(list(n3.values())))  # run() already returns bps/day
    nn = len(n3)
    monkeys = np.array([(sv[rng.integers(0, len(sv), nn)] * rng.choice([-1, 1], nn) - 3.0e-4).mean() * 1e4 for _ in range(2000)])
    mk["N3_US100"] = {"actual_bps": actual, "monkey_mean_bps": float(monkeys.mean()),
                      "percentile": float((monkeys < actual).mean() * 100), "n_days": nn}
    # GT monkeys: same count of random non-holiday weekdays, short post-fix
    from run_round23 import windows
    uj = windows("USDJPY", range(2014, 2027), date(2014, 1, 1), date(2026, 8, 31))
    from data_calendar import gotobi_days
    got = gotobi_days(2014, 2026)
    gt_days = [dd for dd in uj["POST"] if dd in got]
    actual = float(np.mean([uj["POST"][dd] for dd in gt_days]) - 1e-4)
    allv = np.array(list(uj["POST"].values()))
    monkeys = np.array([(allv[rng.integers(0, len(allv), len(gt_days))] - 1e-4).mean() for _ in range(2000)])
    mk["GT_USDJPY"] = {"actual_bps": actual * 1e4, "monkey_mean_bps": float(monkeys.mean() * 1e4),
                       "percentile": float((monkeys < actual).mean() * 100), "n_days": len(gt_days)}
    res["MK_monkey"] = mk
    print("MK", json.dumps(mk, indent=1), flush=True)
    # ------------------------------------------------ WF: Pardo walk-forward efficiency
    wf = {}
    for fam, key in (("family_a", "raw"), ("family_rb", "raw"), ("family_gt", "raw")):
        fp = os.path.join("results", fam + ".json")
        if not os.path.exists(fp):
            continue
        r = json.load(open(fp))
        best_is = max(v["sharpe_discovery"] for v in r["variants"])
        wf_s = r[key]["walk_forward_top5"]["sharpe"]
        wf[fam] = {"wf_sharpe": wf_s, "best_in_sample_sharpe": best_is, "wfe_pct": round(100 * wf_s / best_is, 1)}
    res["WF_pardo"] = wf
    print("WF", json.dumps(wf, indent=1))
    json.dump(res, open(os.path.join(OUT, "round31_kaufman.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
