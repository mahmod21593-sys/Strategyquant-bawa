"""Round 34 (PREREGISTRATION.md A48): the native N3 momentum grid on US30 and US2000 from the independent Dukascopy
feed, plus a second-feed check of US100.

    python3 run_round34.py   -> results/round34_n3_breadth.json
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
from data_audit import spike_mask
from data_histdata import NY
from data_minutes import H, L, O, day_of, group, price_at
from run_round24 import to_battery

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 13998
END = date(2026, 9, 18)
ZERO_DTE = date(2022, 11, 14)
VARIANTS = [f"{b}|k{kk}|{m}" for b in ("range", "atr14") for kk in (0.3, 0.5, 0.7) for m in ("flat", "reverse")]
PRIMARY = "range|k0.5|flat"


def r3_grid(t, x, cost):
    """The round-11 R3 native grid (run_round11.run_r3 logic, unchanged): {variant: {date: (net pnl, entries)}}."""
    keep = ~spike_mask(x, 0.02)
    t, x = t[keep], x[keep]
    day, mod = t // 1440, t % 1440
    ins = (mod >= 570) & (mod < 960)
    keys, _, sh, sl, _, cnt, st = group(day[ins], x[ins])
    xi, mi = x[ins], mod[ins]
    po, pc, pf = price_at(day, mod, x, 570, prefer_open=True), price_at(day, mod, x, 960), price_at(day, mod, x, 959)
    valid = [i for i, k in enumerate(keys.tolist()) if cnt[i] >= 300 and k in po and k in pc and k in pf and day_of(k).weekday() < 5]
    out = {v: {} for v in VARIANTS}
    prev, trs = None, []
    for i in valid:
        k = int(keys[i])
        d = day_of(k)
        if prev is None:
            prev = i
            continue
        pcl = pc[int(keys[prev])]
        trs.append(max(sh[i], pcl) - min(sl[i], pcl))
        width = {"range": sh[prev] - sl[prev], "atr14": float(np.mean(trs[-15:-1])) if len(trs) > 14 else None}
        prev = i
        if d > END:
            continue
        rows = slice(st[i], st[i] + cnt[i])
        m_, xx = mi[rows], xi[rows]
        e = m_ < 959
        oo, hh, ll = xx[e, O], xx[e, H], xx[e, L]
        o0, exit_px = po[k], pf[k]
        for base in ("range", "atr14"):
            w = width[base]
            if not w:
                continue
            for kk in (0.3, 0.5, 0.7):
                U, D = o0 + kk * w, o0 - kk * w
                upt, dnt = hh >= U, ll <= D
                for mode in ("flat", "reverse"):
                    pnl, entries, pos, px, j0 = 0.0, 0, 0, None, 0
                    while True:
                        if pos == 0:
                            cand = np.nonzero(upt[j0:] | dnt[j0:])[0]
                            if not len(cand):
                                break
                            j = j0 + int(cand[0])
                            go_long = upt[j] and (not dnt[j] or U - oo[j] <= oo[j] - D)
                            pos, px = (1, max(U, oo[j])) if go_long else (-1, min(D, oo[j]))
                        else:
                            if mode == "flat":
                                break
                            cand = np.nonzero((dnt if pos == 1 else upt)[j0:])[0]
                            if not len(cand):
                                break
                            j = j0 + int(cand[0])
                            npx = min(D, oo[j]) if pos == 1 else max(U, oo[j])
                            pnl += pos * (npx / px - 1)
                            pos, px = -pos, npx
                        entries += 1
                        j0 = j + 1
                    if pos != 0:
                        pnl += pos * (exit_px / px - 1)
                    out[f"{base}|k{kk}|{mode}"][d] = (pnl - entries * cost / 1e4, entries)
    return out


def summary(rows):
    ds = sorted(rows)
    v = np.array([rows[d][0] for d in ds])
    mid = ds[len(ds) // 2]
    h1 = np.array([rows[d][0] for d in ds if d < mid])
    h2 = np.array([rows[d][0] for d in ds if d >= mid])
    t = vs.nw_t(list(v), 5)
    post = np.array([rows[d][0] for d in ds if d >= ZERO_DTE])
    return {"n": len(v), "first": str(ds[0]), "last": str(ds[-1]), "mean_bps": float(v.mean() * 1e4), "t_hac": t, "p_one_sided": vs.p_one_sided(t),
            "sharpe": float(v.mean() / v.std(ddof=1) * math.sqrt(252)), "halves_bps": (float(h1.mean() * 1e4), float(h2.mean() * 1e4)),
            "split_date": str(mid), "post_0dte_bps": float(post.mean() * 1e4) if len(post) else None,
            "entries_per_day": float(np.mean([rows[d][1] for d in ds]))}


def main():
    from data_duka_minutes import local as dlocal
    from data_minutes import local as hlocal
    res = {}
    grids = {}
    for lab, sym, cost in (("US30", "USA30IDXUSD", 1.5), ("US2000", "USSC2000IDXUSD", 3.0), ("US100_duka", "USATECHIDXUSD", 1.5)):
        t, x = dlocal(sym, range(2012, 2027), NY)
        grids[lab] = r3_grid(t, x, cost)
        print("N3B", lab, len(grids[lab][PRIMARY]), flush=True)
    t, x = hlocal("NSXUSD", range(2013, 2027), NY)
    grids["US100_histdata"] = r3_grid(t, x, 1.5)
    prim = {"B1": summary(grids["US30"][PRIMARY]), "B2": summary(grids["US2000"][PRIMARY])}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    ok = {k: prim[k]["p_holm"] < 0.05 and all(h > 0 for h in prim[k]["halves_bps"]) for k in prim}
    res["primary"] = prim
    res["verdict"] = "BREADTH CONFIRMED" if all(ok.values()) else "PARTIAL" if any(ok.values()) else "NOT CONFIRMED"
    res["grid"] = {lab: {v: summary(g[v]) for v in VARIANTS if g[v]} for lab, g in grids.items()}
    res["share_variants_positive"] = {lab: float(np.mean([s["mean_bps"] > 0 for s in d.values()])) for lab, d in res["grid"].items()}
    # second feed: Dukascopy vs HistData US100 primary variant
    a, b = grids["US100_duka"][PRIMARY], grids["US100_histdata"][PRIMARY]
    common = sorted(set(a) & set(b))
    if common:
        va, vb = np.array([a[d][0] for d in common]), np.array([b[d][0] for d in common])
        res["second_feed_US100"] = {"common_days": len(common), "corr": float(np.corrcoef(va, vb)[0, 1]),
                                    "mean_bps_duka": float(va.mean() * 1e4), "mean_bps_histdata": float(vb.mean() * 1e4)}
    per = {f"{lab}|{v}": {d: r[0] for d, r in grids[lab][v].items()} for lab in ("US30", "US2000") for v in VARIANTS}
    first = min(min(r) for r in per.values() if r)
    split = sorted(set(d for r in per.values() for d in r))
    res["battery"] = to_battery(per, "N3B", first, split[len(split) // 2], first.year + 3)
    json.dump(res, open(os.path.join(OUT, "round34_n3_breadth.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "verdict", "share_variants_positive", "second_feed_US100")}, indent=1, default=str))
    for lab, d in res["grid"].items():
        print(lab, {v: (round(s["mean_bps"], 2), round(s["t_hac"], 2)) for v, s in d.items()})


if __name__ == "__main__":
    main()
