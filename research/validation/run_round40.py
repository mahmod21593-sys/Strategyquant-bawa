"""Round 40 (PREREGISTRATION.md A54): ME — month-end rebalancing fade into the close (US500, US100, US30);
SPM — the native N3 rule on the dollar-neutral US100 minus US500 spread.

    python3 run_round40.py   -> results/round40_me_spm.json
"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import numpy as np

import run_family_a as fa
import vstats as vs
from data_audit import spike_mask
from data_duka_chart import local as dlocal
from data_histdata import NY
from data_minutes import C, O, price_at
from run_round24 import clean_local, to_battery

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 14652
E = date(1970, 1, 1).toordinal()
END = date(2026, 9, 18)
COST = 1.5e-4


def load(name):
    if name == "US30":
        t, x = dlocal("USA30.IDX/USD", NY, END)
        sp = spike_mask(x, 0.02)
        return t[~sp], x[~sp]
    return clean_local({"US500": "SPXUSD", "US100": "NSXUSD"}[name], range(2013, 2027), NY)


# ---------------------------------------------------------------- ME

def me_events(name):
    t, x = load(name)
    day, mod = t // 1440, t % 1440
    ins = (mod >= 570) & (mod < 960)
    k, n = np.unique(day[ins], return_counts=True)
    sess = sorted(int(a) for a, b in zip(k, n) if b >= 300 and date.fromordinal(int(a) + E).weekday() < 5)
    px = {m: price_at(day, mod, x, m) for m in (930, 950, 960)}
    p10 = price_at(day, mod, x, 600)
    last = {}
    for s in sess:
        d = date.fromordinal(s + E)
        last[(d.year, d.month)] = s  # sessions are sorted: the last one wins
    months = sorted(last)
    out = []
    for a, b in zip(months[:-1], months[1:]):
        s0, s1 = last[a], last[b]
        d1 = date.fromordinal(s1 + E)
        if d1 > END or s0 not in px[960]:
            continue
        nxt = [s for s in sess if s > s1][:1]
        row = {"date": d1, "quarter_end": d1.month in (3, 6, 9, 12)}
        for em in (930, 950):
            if s1 not in px[em]:
                continue
            mtd = px[em][s1] / px[960][s0] - 1
            row[f"mtd{em}"] = mtd
            for ex, pmap, key in (("close", px[960], s1), ("next10", p10, nxt[0] if nxt else None)):
                if key is None or key not in pmap:
                    continue
                row[f"{em}|{ex}"] = -np.sign(mtd) * (pmap[key] / px[em][s1] - 1) - COST
        if "930|close" in row:
            out.append(row)
    return out


def me_part():
    ev = {m: me_events(m) for m in ("US500", "US100", "US30")}
    for m, e in ev.items():
        print("ME", m, len(e), "month-ends", flush=True)
    by = {}
    for m, e in ev.items():
        for r in e:
            by.setdefault(r["date"], []).append(r["930|close"])
    ds = sorted(by)
    port = [float(np.mean(by[d])) for d in ds]
    t1 = vs.nw_t(port, 1)
    mid = ds[len(ds) // 2]
    me1 = {"n": len(port), "mean_bps": float(np.mean(port) * 1e4), "t_hac": t1, "p_one_sided": vs.p_one_sided(t1),
           "halves_bps": (float(np.mean([v for d, v in zip(ds, port) if d < mid]) * 1e4), float(np.mean([v for d, v in zip(ds, port) if d >= mid]) * 1e4)),
           "hit_rate": float(np.mean([v > 0 for v in port]))}
    xs = np.array([abs(r["mtd930"]) for e in ev.values() for r in e])
    ys = np.array([r["930|close"] for e in ev.values() for r in e])
    X = np.c_[np.ones(len(xs)), xs]
    b = np.linalg.lstsq(X, ys, rcond=None)[0]
    res_ = ys - X @ b
    xtx = np.linalg.inv(X.T @ X)
    cov = xtx @ (X.T * res_ ** 2) @ X @ xtx
    t2 = float(b[1] / math.sqrt(cov[1, 1]))
    me2 = {"slope_bps_per_pct": float(b[1] * 1e4 / 100), "t_white": t2, "p_one_sided": vs.p_one_sided(t2), "n": int(len(xs))}
    var = {}
    for m, e in ev.items():
        for em in (930, 950):
            for thr in (0.0, 0.01, 0.02):
                for ex in ("close", "next10"):
                    var[f"{m}|{em}|{thr}|{ex}"] = {r["date"]: r[f"{em}|{ex}"] for r in e if f"{em}|{ex}" in r and abs(r[f"mtd{em}"]) >= thr}
    grid = {k: {"n": len(v), "mean_bps": float(np.mean(list(v.values())) * 1e4) if v else None,
                "t": vs.nw_t(list(v.values()), 1) if len(v) >= 10 else None} for k, v in var.items()}
    qe = [r["930|close"] for e in ev.values() for r in e if r["quarter_end"]]
    return me1, me2, grid, {"quarter_end_events": len(qe), "quarter_end_mean_bps": float(np.mean(qe) * 1e4),
                            "per_market": {m: {"n": len(e), "mean_bps": float(np.mean([r["930|close"] for r in e]) * 1e4),
                                               "t": vs.nw_t([r["930|close"] for r in e], 1)} for m, e in ev.items()}}


# ---------------------------------------------------------------- SPM

def sessions_pair():
    """{day: (minutes, P100 closes, P500 closes, P100 open, P500 open)} on minutes present in both, 09:30-15:59."""
    out = {}
    per = {}
    for nm, sym in (("100", "NSXUSD"), ("500", "SPXUSD")):
        t, x = clean_local(sym, range(2013, 2027), NY)
        day, mod = t // 1440, t % 1440
        sel = (mod >= 570) & (mod < 960)
        per[nm] = (t[sel], x[sel])
    t1, x1 = per["100"]
    t2, x2 = per["500"]
    common, i1, i2 = np.intersect1d(t1, t2, return_indices=True)
    day = common // 1440
    st = np.r_[0, np.nonzero(np.diff(day))[0] + 1]
    en = np.r_[st[1:], len(day)]
    for a, b in zip(st, en):
        d = date.fromordinal(int(day[a]) + E)
        m = common[a:b] % 1440
        if b - a < 300 or m[0] > 572 or d.weekday() >= 5 or d > END:
            continue
        out[d] = (m, x1[i1[a:b], C], x2[i2[a:b], C], x1[i1[a], O], x2[i2[a], O])
    return out


def spm_grid(sp, cost=3.0e-4):
    ds = sorted(sp)
    ranges, res = [], {f"{b}|k{kk}|{md}": {} for b in ("range", "atr14") for kk in (0.3, 0.5, 0.7) for md in ("flat", "reverse")}
    prev = None
    for d in ds:
        m, c1, c2, o1, o2 = sp[d]
        S = c1 / o1 - c2 / o2
        if prev is not None:
            w = {"range": ranges[-1], "atr14": float(np.mean(ranges[-14:])) if len(ranges) >= 14 else None}
            for base, wd in w.items():
                if not wd:
                    continue
                for kk in (0.3, 0.5, 0.7):
                    up, dn = S >= kk * wd, S <= -kk * wd
                    for md in ("flat", "reverse"):
                        pnl, pos, j0, e1, e2, entries = 0.0, 0, 0, None, None, 0
                        while j0 < len(S) - 1:
                            hit = np.nonzero((up[j0:] | dn[j0:]) if pos == 0 else (dn[j0:] if pos == 1 else up[j0:]))[0]
                            if not len(hit):
                                break
                            j = j0 + int(hit[0])
                            if j >= len(S) - 1:
                                break
                            if pos != 0:
                                pnl += pos * ((c1[j] / e1 - 1) - (c2[j] / e2 - 1))
                                if md == "flat":
                                    break
                            pos = (1 if up[j] else -1) if pos == 0 else -pos
                            e1, e2 = c1[j], c2[j]
                            entries += 1
                            j0 = j + 1
                            if md == "flat":
                                break
                        if pos != 0:
                            pnl += pos * ((c1[-1] / e1 - 1) - (c2[-1] / e2 - 1))
                        res[f"{base}|k{kk}|{md}"][d] = pnl - entries * cost
        ranges.append(float(S.max() - S.min()))
        prev = d
    return res


def main():
    me1, me2, me_grid, me_desc = me_part()
    sp = sessions_pair()
    print("SPM sessions", len(sp), flush=True)
    g = spm_grid(sp)
    prim = g["range|k0.5|flat"]
    ds = sorted(prim)
    v = [prim[d] for d in ds]
    t = vs.nw_t(v, 5)
    mid = len(v) // 2
    sp1 = {"n": len(v), "mean_bps": float(np.mean(v) * 1e4), "t_hac": t, "p_one_sided": vs.p_one_sided(t),
           "sharpe": float(np.mean(v) / np.std(v, ddof=1) * math.sqrt(252)),
           "halves_bps": (float(np.mean(v[:mid]) * 1e4), float(np.mean(v[mid:]) * 1e4)), "split": str(ds[mid])}
    prim_all = {"ME1": me1, "ME2": me2, "SP1": sp1}
    holm = vs.holm({k: x["p_one_sided"] for k, x in prim_all.items()})
    for k in prim_all:
        prim_all[k]["p_holm"] = holm[k]
    verdict = {"ME": "EDGE" if (me1["p_holm"] < 0.05 and all(h > 0 for h in me1["halves_bps"])) else "NO EDGE",
               "SPM": "EDGE" if (sp1["p_holm"] < 0.05 and all(h > 0 for h in sp1["halves_bps"])) else "NO EDGE"}
    from run_round34_minute import r3_grid
    th, xh = clean_local("NSXUSD", range(2013, 2027), NY)
    n3 = {d: r[0] for d, r in r3_grid(th, xh, 1.5)["range|k0.5|flat"].items()}
    com = sorted(set(n3) & set(prim))
    res = {"primary": prim_all, "verdict": verdict, "me_descriptive": me_desc, "me_grid": me_grid,
           "spm_grid": {k: {"mean_bps": float(np.mean(list(x.values())) * 1e4), "t_hac": vs.nw_t(list(x.values()), 5), "n": len(x)} for k, x in g.items()},
           "spm_corr_with_US100_N3": float(np.corrcoef([prim[d] for d in com], [n3[d] for d in com])[0, 1]),
           "US100_N3_sharpe_same_days": float(np.mean([n3[d] for d in com]) / np.std([n3[d] for d in com], ddof=1) * math.sqrt(252))}
    res["battery_spm"] = to_battery({f"SPM|{k}": x for k, x in g.items()}, "SPM", date(2013, 1, 1), date(2019, 11, 1), 2016)
    json.dump(res, open(os.path.join(OUT, "round40_me_spm.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "verdict", "me_descriptive", "spm_corr_with_US100_N3", "US100_N3_sharpe_same_days")},
                     indent=1, default=str))
    for k, s in res["spm_grid"].items():
        print("SPM", k, round(s["mean_bps"], 2), round(s["t_hac"], 2))
    for k, s in me_grid.items():
        if s["mean_bps"] is not None:
            print("ME", k, s["n"], round(s["mean_bps"], 2), s["t"] and round(s["t"], 2))


if __name__ == "__main__":
    main()
