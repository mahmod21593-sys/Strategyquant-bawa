"""Round 9, family B (A22): noise-area intraday momentum, 324 variants on 9 markets (corrected HistData clock).

    python3 run_family_b.py build SYM [SYM ...]   -> $ROUND9_DIR/family_b_<SYM>.npz
    python3 run_family_b.py battery               -> results/family_b.json
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date
from zoneinfo import ZoneInfo

import numpy as np

import multitest as mt
import vstats as vs
from data_histdata import NY, available_years, local_table
from run_noise_area import run

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
Z = ZoneInfo
# symbol: (tz, open, close, cost bps, excluded marks (local minutes))
MARKETS = {"NSXUSD": (NY, (9, 30), (16, 0), 1.5, ()), "SPXUSD": (NY, (9, 30), (16, 0), 1.5, ()),
           "GRXEUR": (Z("Europe/Berlin"), (9, 0), (17, 30), 1.5, ()), "FRXEUR": (Z("Europe/Paris"), (9, 0), (17, 30), 2.0, ()),
           "UKXGBP": (Z("Europe/London"), (8, 0), (16, 30), 2.0, ()), "JPXJPY": (Z("Asia/Tokyo"), (9, 0), (15, 0), 3.0, (690, 720, 750)),
           "AUXAUD": (Z("Australia/Sydney"), (10, 0), (16, 0), 3.0, ()), "HKXHKD": (Z("Asia/Hong_Kong"), (9, 30), (16, 0), 4.0, (720, 750, 780)),
           "XAUUSD": (NY, (8, 20), (13, 30), 2.5, ())}
LOOKBACKS, BANDS, GRIDS, EXITS = (7, 14, 28), (0.8, 1.0, 1.25), (30, 60), ("flip", "twap_stop")
YEARS = list(range(2013, 2027))
DISC, VAL, HOLD = (date(2014, 1, 1), date(2019, 12, 31)), (date(2020, 1, 1), date(2025, 12, 31)), (date(2026, 1, 1), date(2026, 12, 31))


def build(sym):
    tz, oh, ch, cost, excl = MARKETS[sym]
    o, c = oh[0] * 60 + oh[1], ch[0] * 60 + ch[1]
    closes = [c] + ([930] if sym == "JPXJPY" else [])
    keep = set(range(o - 1, max(closes) + 1))
    ses = local_table(sym, available_years(sym, YEARS), tz, keep)
    out = {}
    for L in LOOKBACKS:
        for bnd in BANDS:
            for g in GRIDS:
                for ex in EXITS:
                    rows = {}
                    for cc in closes:
                        first, last = o + 30, cc - 30
                        spec = (sym, tz, oh, (cc // 60, cc % 60), (first // 60, first % 60), (last // 60, last % 60), cost, ex)
                        r = dict(run("R9", lookback=L, grid=g, spec=spec, ses=ses, band=bnd, exclude=set(excl))[0])
                        if sym == "JPXJPY":  # TSE session: 15:00 close until 2024-11-04, 15:30 from 2024-11-05
                            cut = date(2024, 11, 5)
                            r = {d: x for d, x in r.items() if (d < cut) == (cc == c)}
                        rows.update(r)
                    out[f"{sym}|L{L}|b{bnd:g}|g{g}|{ex}"] = rows
        print(sym, "L", L, "done", flush=True)
    names = sorted(out)
    dates = sorted({d for v in out.values() for d in v})
    X = np.array([[out[n].get(d, 0.0) / 1e4 for n in names] for d in dates])
    np.savez_compressed(os.path.join(R9, f"family_b_{sym}.npz"), X=X, dates=np.array([d.toordinal() for d in dates]), cols=np.array(names))


def load_all():
    parts = [np.load(os.path.join(R9, f"family_b_{s}.npz")) for s in MARKETS]
    cal = sorted({int(d) for p in parts for d in p["dates"]})
    ci = {d: i for i, d in enumerate(cal)}
    cols, mats = [], []
    for p in parts:
        idx = np.array([ci[int(d)] for d in p["dates"]])
        for j, n in enumerate(p["cols"]):
            col = np.zeros(len(cal))
            col[idx] = p["X"][:, j]
            cols.append(str(n))
            mats.append(col)
    return np.array([date.fromordinal(d) for d in cal]), np.array(mats).T, cols


def battery():
    from run_family_a import battery as bat
    cal, X, cols = load_all()
    np.savez_compressed(os.path.join(R9, "family_b.npz"), X=X, dates=np.array([d.toordinal() for d in cal]), cols=np.array(cols))
    inside = np.array([DISC[0] <= d <= VAL[1] for d in cal])
    Xs, cs = X[inside], cal[inside]
    disc = np.array([d <= DISC[1] for d in cs])
    years = np.array([d.year for d in cs])
    res = {"n_variants": len(cols), "all": bat(Xs, cols, disc, ~disc, years, first_wf=2020)}
    ex_nsx = [i for i, c in enumerate(cols) if not c.startswith("NSXUSD")]
    res["excluding_NSXUSD"] = bat(Xs[:, ex_nsx], [cols[i] for i in ex_nsx], disc, ~disc, years, first_wf=2020)
    hold = np.array([HOLD[0] <= d <= HOLD[1] for d in cal])
    sr_h = mt.sharpe(X[hold], 252)
    sr_v = np.array(res["all"]["_sr_v"])
    res["holdout_2026"] = {"n_days": int(hold.sum()), "median_sharpe_all": float(np.median(sr_h)),
                           "median_sharpe_of_rw_survivors": float(np.median([sr_h[cols.index(c)] for c in res["all"]["romano_wolf_significant_5pct"]]))
                           if res["all"]["romano_wolf_significant_5pct"] else None,
                           "corr_validation_vs_holdout_sharpe": float(np.corrcoef(sr_v, sr_h)[0, 1])}
    variants = [{"name": c, "sharpe_discovery": a, "sharpe_validation": v, "sharpe_holdout_2026": float(h), "rw_p": p}
                for c, a, v, h, p in zip(cols, res["all"]["_sr_d"], res["all"]["_sr_v"], sr_h, res["all"]["_p_rw"])]
    for lab in ("all", "excluding_NSXUSD"):
        for k in ("_sr_d", "_sr_v", "_p_rw"):
            res[lab].pop(k)
    res["variants"] = variants
    res["family_verdict"] = res["all"]["verdict"]
    json.dump(res, open(os.path.join(OUT, "family_b.json"), "w"), indent=1, default=str)
    for lab in ("all", "excluding_NSXUSD"):
        b = res[lab]
        print(lab, {k: b[k] for k in ("spa_validation", "pbo_full_sample", "selection_test", "walk_forward_top5", "best_validation_variant", "verdict")})
        print(lab, "RW", b["romano_wolf_significant_5pct"])
        print(lab, b["per_instrument"])
    print("holdout", res["holdout_2026"])


if __name__ == "__main__":
    if sys.argv[1] == "build":
        for s in sys.argv[2:]:
            build(s)
    else:
        battery()
