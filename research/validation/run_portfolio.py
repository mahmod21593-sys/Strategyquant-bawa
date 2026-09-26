"""Round 9, portfolio P (PREREGISTRATION.md A22): strategies chosen on each family's discovery data only,
then evaluated out of sample 2020-01 -> 2025-12 (and the 2026 holdout). -> results/portfolio.json"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import numpy as np

import vstats as vs

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
DISC_END = {"A": date(2012, 12, 31), "B": date(2019, 12, 31), "C": date(2016, 12, 31), "D": date(2011, 12, 31)}
DISC_START = {"A": date(1993, 2, 1), "B": date(2014, 1, 1), "C": date(2007, 1, 1), "D": date(1999, 2, 1)}
OOS = (date(2020, 1, 1), date(2025, 12, 31))
HOLD = (date(2026, 1, 1), date(2026, 9, 30))
CAP_FAMILY, CAP_INSTRUMENT, CORR_MAX = 8, 2, 0.6


def load():
    fam = {}
    for f in ("a", "b", "c"):
        p = np.load(os.path.join(R9, f"family_{f}.npz"))
        fam[f.upper()] = ([date.fromordinal(int(d)) for d in p["dates"]], p["X"], [str(c) for c in p["cols"]])
    p = np.load(os.path.join(R9, "family_d.npz"))
    months = [(int(m) // 100, int(m) % 100) for m in p["months"]]
    fam["D"] = (months, p["X"], [str(c) for c in p["cols"]])
    return fam


def neighbours(f, cols):
    """Index lists of each column's one-step parameter neighbours (A22)."""
    parts = [c.split("|") for c in cols]
    nb = []
    for i, a in enumerate(parts):
        if f == "A":  # same instrument and signal; other exit (same filter) or other filter (same exit)
            js = [j for j, b in enumerate(parts) if j != i and b[0] == a[0] and b[1] == a[1] and ((b[2] != a[2]) ^ (b[3] != a[3]))]
        elif f == "B":  # one step in lookback or band, same instrument, grid, exit
            L, B = (7, 14, 28), (0.8, 1.0, 1.25)
            la, ba = L.index(int(a[1][1:])), B.index(float(a[2][1:]))
            js = []
            for j, b in enumerate(parts):
                if j == i or b[0] != a[0] or b[3] != a[3] or b[4] != a[4]:
                    continue
                lb, bb = L.index(int(b[1][1:])), B.index(float(b[2][1:]))
                if abs(la - lb) + abs(ba - bb) == 1:
                    js.append(j)
        elif f == "C":  # one step in lookback, same signal, sizing, rebalance
            L = (21, 63, 126, 252)
            la = L.index(int(a[0][1:]))
            js = [j for j, b in enumerate(parts) if b[1:] == a[1:] and abs(L.index(int(b[0][1:])) - la) == 1]
        else:
            js = []
        nb.append(js)
    return nb


def select(f, dates, X, cols):
    disc = np.array([DISC_START[f] <= (d if f != "D" else date(d[0], d[1], 1)) <= DISC_END[f] for d in dates])
    D = X[disc]
    sd = D.std(0, ddof=1)
    sr = np.where(sd > 0, D.mean(0) / np.where(sd > 0, sd, 1), -np.inf)
    thr = np.quantile(sr[np.isfinite(sr)], 0.8)
    nb = neighbours(f, cols)
    cand = [i for i in np.argsort(-sr) if sr[i] >= thr and sr[i] > 0 and all(sr[j] > 0 for j in nb[i])]
    chosen, per_inst = [], {}
    C = np.corrcoef(D.T) if D.shape[1] > 1 else np.ones((1, 1))
    for i in cand:
        inst = cols[i].split("|")[0]
        if f in ("A", "B") and per_inst.get(inst, 0) >= CAP_INSTRUMENT:
            continue
        if any(C[i, j] > CORR_MAX for j in chosen):
            continue
        chosen.append(i)
        per_inst[inst] = per_inst.get(inst, 0) + 1
        if len(chosen) >= CAP_FAMILY:
            break
    w = 1 / sd[chosen]
    w = w / w.sum()
    fam_disc = D[:, chosen] @ w
    return chosen, w, float(fam_disc.std(ddof=1)), {cols[i]: float(sr[i] * math.sqrt(12 if f == "D" else 252)) for i in chosen}


def stats(x, per_year=252):
    x = np.asarray(x)
    eq = np.cumsum(x)
    dd = float((eq - np.maximum.accumulate(eq)).min())
    return {"n": int(len(x)), "ann_return_pct": float(x.mean() * per_year * 100), "ann_vol_pct": float(x.std(ddof=1) * math.sqrt(per_year) * 100),
            "sharpe": float(x.mean() / x.std(ddof=1) * math.sqrt(per_year)) if x.std() > 0 else 0.0, "t_hac": float(vs.nw_t(list(x), 5)),
            "max_drawdown_pct": dd * 100}


def main():
    fam = load()
    # common daily calendar: family A's calendar (US + world weekdays), restricted to the portfolio windows
    cal = [d for d in fam["A"][0] if OOS[0] <= d <= HOLD[1]]
    ci = {d: i for i, d in enumerate(cal)}
    series, picks, disc_vol = {}, {}, {}
    for f, (dates, X, cols) in fam.items():
        chosen, w, vol, srs = select(f, dates, X, cols)
        picks[f] = {"strategies": srs, "weights": dict(zip([cols[i] for i in chosen], [float(v) for v in w]))}
        s = np.zeros(len(cal))
        if f == "D":  # monthly P&L booked on the month's last calendar-day trading date
            last = {}
            for d in cal:
                last[(d.year, d.month)] = d
            for m, row in zip(dates, X[:, chosen] @ w):
                if m in last:
                    s[ci[last[m]]] += row
            disc_vol[f] = vol / math.sqrt(21)  # monthly -> daily scale
        else:
            for d, row in zip(dates, X[:, chosen] @ w):
                if d in ci:
                    s[ci[d]] += row
            disc_vol[f] = vol
        series[f] = s
    # equal risk across families (discovery volatility), target 10%/yr for the combined book's scale reference
    target = 0.10 / math.sqrt(252) / 2
    scaled = {f: series[f] * (target / disc_vol[f]) for f in series}
    oos = np.array([OOS[0] <= d <= OOS[1] for d in cal])
    hold = np.array([HOLD[0] <= d <= HOLD[1] for d in cal])
    port = sum(scaled.values())
    res = {"selection": picks, "discovery_daily_vol": disc_vol}
    res["oos_2020_2025"] = {"portfolio": stats(port[oos]), **{f"family_{f}": stats(scaled[f][oos]) for f in scaled}}
    res["holdout_2026"] = {"portfolio": stats(port[hold]), **{f"family_{f}": stats(scaled[f][hold]) for f in scaled}}
    fs = list(scaled)
    res["oos_correlation"] = {a: {b: float(np.corrcoef(scaled[a][oos], scaled[b][oos])[0, 1]) for b in fs} for a in fs}
    res["oos_contribution_pct_of_return"] = {f: float(scaled[f][oos].sum() / port[oos].sum() * 100) for f in fs}
    # comparisons: (i) every variant equal-risk within family, families equal-risk; (ii) single best discovery variant
    naive = np.zeros(len(cal))
    best = (None, -np.inf)
    for f, (dates, X, cols) in fam.items():
        disc = np.array([DISC_START[f] <= (d if f != "D" else date(d[0], d[1], 1)) <= DISC_END[f] for d in dates])
        sd = X[disc].std(0, ddof=1)
        ok = sd > 0
        w = np.where(ok, 1 / np.where(ok, sd, 1), 0)
        w = w / w.sum()
        row = X @ w
        s = np.zeros(len(cal))
        if f == "D":
            last = {}
            for d in cal:
                last[(d.year, d.month)] = d
            for m, v in zip(dates, row):
                if m in last:
                    s[ci[last[m]]] += v
            v_ = row[disc].std(ddof=1) / math.sqrt(21)
        else:
            for d, v in zip(dates, row):
                if d in ci:
                    s[ci[d]] += v
            v_ = row[disc].std(ddof=1)
        naive += s * (target / v_)
        srd = np.where(ok, X[disc].mean(0) / np.where(ok, sd, 1), -np.inf) * math.sqrt(12 if f == "D" else 252)
        j = int(np.argmax(srd))
        if srd[j] > best[1] and f != "D":
            bs = np.zeros(len(cal))
            for d, v in zip(dates, X[:, j]):
                if d in ci:
                    bs[ci[d]] += v
            best = (f"{f}:{cols[j]}", srd[j], bs)
    res["comparison_oos"] = {"all_variants_equal_risk": stats(naive[oos]), "single_best_discovery_variant": {"name": best[0], **stats(best[2][oos])}}
    np.savez_compressed(os.path.join(R9, "portfolio.npz"), dates=np.array([d.toordinal() for d in cal]),
                        **{f"fam_{f}": scaled[f] for f in scaled}, port=port)
    json.dump(res, open(os.path.join(OUT, "portfolio.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("oos_2020_2025", "holdout_2026", "oos_correlation", "oos_contribution_pct_of_return", "comparison_oos")}, indent=1))
    for f, p in picks.items():
        print(f, p["strategies"])


if __name__ == "__main__":
    main()
