"""Round 9: descriptive "aspects" of family A (index reversal) for portfolio building and SQX parameter choices.
Post hoc and descriptive (A22 lists aspects reports as non-tests). -> results/family_a_aspects.json"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import numpy as np

import multitest as mt
import vstats as vs

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
SPLIT = date(2013, 1, 1)
US = ("SPY", "QQQ", "DIA", "IWM")


def sr(x):
    return float(x.mean() / x.std(ddof=1) * math.sqrt(252)) if x.std() > 0 else 0.0


def main():
    p = np.load(os.path.join(R9, "family_a.npz"))
    dates = [date.fromordinal(int(d)) for d in p["dates"]]
    cols = [str(c) for c in p["cols"]]
    X, XA = p["X"], p["XA"]
    val = np.array([d >= SPLIT for d in dates])
    disc = ~val
    meta = {c: c.split("|") for c in cols}
    res = {}
    # 1) ensembles: equal-risk average of every variant (discovery vol) per instrument group
    for label, keep in (("US_all_432", lambda m: m[0] in US), ("QQQ_all_108", lambda m: m[0] == "QQQ"), ("SPY_all_108", lambda m: m[0] == "SPY"),
                        ("US_plus_N225_540", lambda m: m[0] in US + ("^N225",)), ("world_ex_US_JP_324", lambda m: m[0] in ("^GDAXI", "^FTSE", "^AXJO"))):
        ks = [i for i, c in enumerate(cols) if keep(meta[c])]
        sd = X[disc][:, ks].std(0, ddof=1)
        w = 1 / np.where(sd > 0, sd, np.inf)
        w = w / w.sum()
        e, ea = X[:, ks] @ w, XA[:, ks] @ w
        res.setdefault("ensembles", {})[label] = {
            "n_variants": len(ks), "discovery_sharpe": sr(e[disc]), "validation_sharpe": sr(e[val]), "validation_t": vs.nw_t(list(e[val]), 5),
            "validation_timing_sharpe": sr(ea[val]), "validation_timing_t": vs.nw_t(list(ea[val]), 5),
            "validation_ann_return_pct_at_10pct_vol": float(e[val].mean() / e[val].std() * 0.10 * 100)}
    # 2) effective number of independent bets among US variants (validation correlations)
    ks = [i for i, c in enumerate(cols) if meta[c][0] in US and X[val][:, i].std() > 0]
    C = np.corrcoef(X[val][:, ks].T)
    ev = np.clip(np.linalg.eigvalsh(C), 0, None)
    res["effective_bets_US"] = {"n_variants": len(ks), "effective_n_(sum ev)^2/sum ev^2": float(ev.sum() ** 2 / (ev ** 2).sum()),
                                "share_variance_first_pc": float(ev.max() / ev.sum()), "median_pairwise_corr": float(np.median(C[np.triu_indices(len(ks), 1)]))}
    # 3) the same rule across markets
    rule = "K3|X1|F0"
    inst = US + ("^N225", "^GDAXI", "^FTSE", "^AXJO")
    idx = [cols.index(f"{s}|{rule}") for s in inst]
    Cm = np.corrcoef(X[val][:, idx].T)
    res["cross_market_corr_K3_X1_F0_validation"] = {a: {b: round(float(Cm[i, j]), 2) for j, b in enumerate(inst)} for i, a in enumerate(inst)}
    # 4) heat map: validation timing Sharpe by signal x exit x filter, per US market and N225
    hm = {}
    for s in US + ("^N225",):
        hm[s] = {}
        for c in cols:
            m = meta[c]
            if m[0] == s:
                hm[s][f"{m[1]}|{m[2]}|{m[3]}"] = round(sr(XA[val][:, cols.index(c)]), 2)
    res["validation_timing_sharpe_map"] = hm
    by_sig = {}
    for c in cols:
        m = meta[c]
        if m[0] in US:
            by_sig.setdefault(m[1], []).append(sr(XA[val][:, cols.index(c)]))
    res["median_validation_timing_sharpe_by_signal_US"] = {k: round(float(np.median(v)), 2) for k, v in sorted(by_sig.items())}
    for key, pos in (("exit", 2), ("filter", 3)):
        g = {}
        for c in cols:
            m = meta[c]
            if m[0] in US:
                g.setdefault(m[pos], []).append(sr(XA[val][:, cols.index(c)]))
        res[f"median_validation_timing_sharpe_by_{key}_US"] = {k: round(float(np.median(v)), 2) for k, v in sorted(g.items())}
    # 5) cost sensitivity: extra cost per entry (entries = first held day after a flat day)
    fa = json.load(open(os.path.join(OUT, "family_a.json")))
    tpy = {v["name"]: v["trades_per_year"] for v in fa["variants"]}
    for extra in (1.5, 3.0):
        adj = np.array([sr(X[val][:, i] - extra * 1e-4 * tpy[c] / 252) for i, c in enumerate(cols)])
        us = [i for i, c in enumerate(cols) if meta[c][0] in US]
        res.setdefault("cost_sensitivity", {})[f"+{extra}bps_per_trade"] = {"median_validation_sharpe_US": float(np.median(adj[us])),
                                                                             "share_positive_US": float((adj[us] > 0).mean())}
    res["baseline_median_validation_sharpe_US"] = float(np.median([sr(X[val][:, i]) for i, c in enumerate(cols) if meta[c][0] in US]))
    json.dump(res, open(os.path.join(OUT, "family_a_aspects.json"), "w"), indent=1)
    for k in ("ensembles", "effective_bets_US", "median_validation_timing_sharpe_by_signal_US", "median_validation_timing_sharpe_by_exit_US",
              "median_validation_timing_sharpe_by_filter_US", "cost_sensitivity", "baseline_median_validation_sharpe_US"):
        print(k, json.dumps(res[k], indent=1))
    print("cross-market", json.dumps(res["cross_market_corr_K3_X1_F0_validation"]))


if __name__ == "__main__":
    main()
