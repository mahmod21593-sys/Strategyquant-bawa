"""Round 9, family D (A22): G10 currency carry and momentum from FRED, 10 variants.
-> results/family_d.json; P&L matrix -> $ROUND9_DIR/family_d.npz"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import numpy as np

import multitest as mt
import vstats as vs
from data_fred import series

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
# currency: (FRED FX series, True if quoted as USD per unit, OECD 3-month rate)
CCY = {"EUR": ("DEXUSEU", True, "IR3TIB01EZM156N"), "GBP": ("DEXUSUK", True, "IR3TIB01GBM156N"), "JPY": ("DEXJPUS", False, "IR3TIB01JPM156N"),
       "AUD": ("DEXUSAL", True, "IR3TIB01AUM156N"), "CAD": ("DEXCAUS", False, "IR3TIB01CAM156N"), "CHF": ("DEXSZUS", False, "IR3TIB01CHM156N"),
       "NZD": ("DEXUSNZ", True, "IR3TIB01NZM156N"), "NOK": ("DEXNOUS", False, "IR3TIB01NOM156N"), "SEK": ("DEXSDUS", False, "IR3TIB01SEM156N")}
US_RATE = "IR3TIB01USM156N"
SPLIT = (2012, 1)


def month_end(sid, usd_per_unit):
    out = {}
    for d, v in series(sid):
        out[(d.year, d.month)] = v if usd_per_unit else 1 / v
    return out


def monthly(sid):
    return {(d.year, d.month): v / 100 for d, v in series(sid)}


def main():
    os.makedirs(R9, exist_ok=True)
    fx = {c: month_end(s, u) for c, (s, u, _) in CCY.items()}
    rate = {c: monthly(r) for c, (_, _, r) in CCY.items()}
    usr = monthly(US_RATE)
    months = sorted(m for m in fx["EUR"] if (1999, 1) <= m <= (2026, 8))
    names = list(CCY) + ["USD"]
    # excess return of holding currency c over month m (bought at the end of m-1): spot change + (i_c - i_us)/12 known at m-1
    ret, carry = {}, {}
    for a, b in zip(months, months[1:]):
        rb, cb = {}, {}
        for c in CCY:
            if a in fx[c] and b in fx[c] and a in rate[c] and a in usr:
                rb[c] = fx[c][b] / fx[c][a] - 1 + (rate[c][a] - usr[a]) / 12
                cb[c] = rate[c][a] - usr[a]
        rb["USD"], cb["USD"] = 0.0, 0.0
        ret[b], carry[a] = rb, cb
    ms = sorted(ret)
    cols, mats = [], []
    specs = [("carry", k, f) for k in (2, 3) for f in ("none", "volfilter")] + [("mom", k, L) for k in (2, 3) for L in (1, 3, 12)]
    for kind, k, arg in specs:
        prev, pnl = {}, []
        for i, m in enumerate(ms):
            a = months[months.index(m) - 1]
            if kind == "carry":
                sc = carry.get(a, {})
            else:
                if i < arg:
                    pnl.append(0.0)
                    continue
                sc = {c: math.prod(1 + ret[ms[j]].get(c, 0.0) for j in range(i - arg, i)) - 1 for c in names}
            avail = [c for c in names if c in sc and c in ret[m]]
            if len(avail) < 2 * k + 1:
                pnl.append(0.0)
                continue
            rank = sorted(avail, key=lambda c: sc[c])
            pos = {c: 0.0 for c in names}
            for c in rank[-k:]:
                pos[c] = 1 / k
            for c in rank[:k]:
                pos[c] = -1 / k
            if kind == "carry" and arg == "volfilter" and i >= 37:
                rv = [np.std([ret[ms[j]].get(c, 0.0) for c in names]) for j in range(i - 36, i)]
                if np.std([ret[ms[i - 1]].get(c, 0.0) for c in names]) > np.quantile(rv, 0.8):
                    pos = {c: 0.0 for c in names}
            gross = sum(abs(v) for v in pos.values())
            turn = sum(abs(pos[c] - prev.get(c, 0.0)) for c in names)
            pnl.append(sum(pos[c] * ret[m][c] for c in names if c in ret[m]) - 3e-4 * turn - 0.01 / 12 * gross)
            prev = pos
        cols.append(f"{kind}|k{k}|{arg}")
        mats.append(pnl)
    X = np.array(mats).T
    np.savez_compressed(os.path.join(R9, "family_d.npz"), X=X, months=np.array([m[0] * 100 + m[1] for m in ms]), cols=np.array(cols))
    val = np.array([m >= SPLIT for m in ms])
    years = np.array([m[0] for m in ms])
    sr_d, sr_v = mt.sharpe(X[~val], 12), mt.sharpe(X[val], 12)
    res = {"n_variants": len(cols), "months": [f"{ms[0]}", f"{ms[-1]}"]}
    res["spa_validation"] = mt.spa(X[val], 3, 2000)
    res["spa_validation"]["best"] = cols[res["spa_validation"]["best_index"]]
    p_rw, t_rw = mt.romano_wolf(X[val], 3, 2000)
    res["romano_wolf_significant_5pct"] = [cols[k] for k in np.argsort(p_rw) if p_rw[k] < 0.05]
    res["pbo_full_sample"] = mt.pbo(X, 16)
    wf = mt.walk_forward(X, years, 2012, 2, 60)[val]
    res["walk_forward_top2"] = {"sharpe": float(wf.mean() / wf.std(ddof=1) * math.sqrt(12)), "t_hac": vs.nw_t(list(wf), 3), "mean_bps_per_month": float(wf.mean() * 1e4)}
    res["variants"] = [{"name": c, "sharpe_discovery": float(a), "sharpe_validation": float(v), "rw_p": float(p), "t_validation": float(t),
                        "mean_bps_month_validation": float(X[val][:, j].mean() * 1e4)}
                       for j, (c, a, v, p, t) in enumerate(zip(cols, sr_d, sr_v, p_rw, t_rw))]
    sp, pb, wfr = res["spa_validation"]["p_spa"], res["pbo_full_sample"]["pbo"], res["walk_forward_top2"]["sharpe"]
    res["family_verdict"] = "EDGE FAMILY" if sp < 0.05 and pb < 0.5 and wfr > 0 else "WEAK FAMILY" if sp < 0.10 or wfr > 0 else "NO EDGE"
    json.dump(res, open(os.path.join(OUT, "family_d.json"), "w"), indent=1, default=str)
    print({k: res[k] for k in ("months", "spa_validation", "pbo_full_sample", "walk_forward_top2", "family_verdict", "romano_wolf_significant_5pct")})
    for v in res["variants"]:
        print(v["name"], round(v["sharpe_discovery"], 2), round(v["sharpe_validation"], 2), round(v["mean_bps_month_validation"], 1), round(v["rw_p"], 3))


if __name__ == "__main__":
    main()
