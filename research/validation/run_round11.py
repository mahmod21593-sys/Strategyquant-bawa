"""Round 11 (PREREGISTRATION.md A24): the index edges as StrategyQuant X would trade them (R1-R3), and FX / metals /
European-index families built for prop accounts (L, M, Q, R).

    python3 run_round11.py R1          -> results/round11_r1.json   (R1 and R2)
    python3 run_round11.py R3          -> results/round11_r3.json
    python3 run_round11.py L|M|Q|R     -> results/family_<x>.json, $ROUND9_DIR/family_<x>.npz
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
import run_family_a as fa
import vstats as vs
from data_histdata import NY
from data_minutes import C, H, L, O, day_of, group, local, price_at
from run_round4 import irx_map, tbill
from run_round10 import finish, weekday_calendar

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
fa.N_TRIALS = 6053
TOKYO, BERLIN, LONDON, PARIS = (ZoneInfo(z) for z in ("Asia/Tokyo", "Europe/Berlin", "Europe/London", "Europe/Paris"))
TSE_CUT = date(2024, 11, 5)  # Tokyo cash close 15:00 -> 15:30
METALS = ("XAUUSD", "XAGUSD")
YEARS = range(2013, 2027)

# ---------------------------------------------------------------- Part 1: R1, R2 (reversal family as SQX trades it)

# symbol: (name, tz, cash open, cash close for a date (local minutes), cost per entry, mark-up per held day, family A twin)
R1_MARKETS = {
    "SPXUSD": ("US500", NY, 570, lambda d: 960, 1.5e-4, fa.MARKUP, "SPY"),
    "NSXUSD": ("US100", NY, 570, lambda d: 960, 1.5e-4, fa.MARKUP, "QQQ"),
    "JPXJPY": ("JP225", TOKYO, 540, lambda d: 900 if d < TSE_CUT else 930, 3.0e-4, 0.0, "^N225"),
    "GRXEUR": ("GER40", BERLIN, 540, lambda d: 1050, 1.5e-4, 0.0, "^GDAXI"),
    "XAUUSD": ("XAUUSD", NY, 500, lambda d: 810, 2.5e-4, 0.0, None),
}
R1_START, R1_END = date(2014, 1, 1), date(2026, 8, 31)
EDGE_MARKETS = ("US500", "US100", "JP225")


def broker_bars(sym):
    """(a) 24-hour bars closing 17:00 NY, labelled by trading date (minutes from 17:00 belong to the next date).
    Metals leave out 16:45-19:00 NY (A24 data rule), so their bar runs 19:00 -> 16:45."""
    t, x = local(sym, YEARS, NY)
    if sym in METALS:
        mod = t % 1440
        k = (mod < 1005) | (mod >= 1140)
        t, x = t[k], x[k]
    keys, o, h, l, c, n, _ = group((t + 420) // 1440, x)
    ok = (n >= 120) & np.array([day_of(k).weekday() < 5 for k in keys])
    return [day_of(k) for k in keys[ok]], o[ok], h[ok], l[ok], c[ok]


def _session(day, mod, x, op, cl):
    ins = (mod >= op) & (mod < cl)
    k, _, h, l, _, n, _ = group(day[ins], x[ins])
    pre = (mod >= op) & (mod < cl - 5)
    k2, _, h2, l2, _, _, _ = group(day[pre], x[pre])
    hl2 = dict(zip(k2.tolist(), zip(h2.tolist(), l2.tolist())))
    po, pc, pm = price_at(day, mod, x, op, prefer_open=True), price_at(day, mod, x, cl), price_at(day, mod, x, cl - 5)
    out = {}
    for kk, hh, ll, nn in zip(k.tolist(), h.tolist(), l.tolist(), n.tolist()):
        if nn >= 0.5 * (cl - op) and kk in po and kk in pc and kk in pm and kk in hl2:
            out[kk] = (po[kk], hh, ll, pc[kk], pm[kk], hl2[kk][0], hl2[kk][1])
    return out


def session_bars(sym):
    """(b) cash-session bars and (c) the price and range 5 minutes before the close.
    -> dates, open, high, low, close, mark price, high and low up to the mark."""
    name, tz, op, close_of, *_ = R1_MARKETS[sym]
    t, x = local(sym, YEARS, tz)
    day, mod = t // 1440, t % 1440
    parts = {cl: _session(day, mod, x, op, cl) for cl in sorted({close_of(date(2014, 1, 1)), close_of(date(2026, 1, 1))})}
    rows = []
    for kk in sorted(set().union(*parts.values())):
        d = day_of(kk)
        r = parts[close_of(d)].get(kk)
        if d.weekday() < 5 and r:
            rows.append((d,) + r)
    return [r[0] for r in rows], *(np.array([r[i] for r in rows]) for i in range(1, 8))


def hybrid_signals(c, p, hh, ll):
    """fa.signals evaluated 5 minutes before the close, as an SQX M5 strategy with session-daily conditions sees them:
    today's close is the mark price p (today's high/low up to the mark), earlier closes are full session closes c."""
    n = len(c)
    s = {}
    run = np.zeros(n, dtype=int)
    for i in range(1, n):
        run[i] = run[i - 1] + 1 if c[i] < c[i - 1] else 0
    dnow = np.r_[False, p[1:] < c[:-1]]
    runp = np.r_[0, run[:-1]]
    for k in (2, 3, 4, 5):
        s[f"K{k}"] = dnow & (runp >= k - 1)
    G, Lq = np.zeros(n), np.zeros(n)
    for i in range(1, n):
        ch = c[i] - c[i - 1]
        up, dn = max(ch, 0.0), max(-ch, 0.0)
        G[i], Lq[i] = (up, dn) if i == 1 else ((G[i - 1] + up) / 2, (Lq[i - 1] + dn) / 2)
    rsi = np.full(n, 50.0)
    for i in range(2, n):
        ch = p[i] - c[i - 1]
        g_, l_ = (G[i - 1] + max(ch, 0.0)) / 2, (Lq[i - 1] + max(-ch, 0.0)) / 2
        rsi[i] = 100.0 if l_ == 0 else 100 - 100 / (1 + g_ / l_)
    for lvl in (5, 10, 20):
        s[f"R{lvl}"] = rsi < lvl
    rng_ = hh - ll
    ibs = np.where(rng_ > 0, (p - ll) / np.where(rng_ > 0, rng_, 1), 0.5)
    s["I10"], s["I25"] = ibs < 0.10, ibs < 0.25
    for N in (5, 10):
        low = np.zeros(n, dtype=bool)
        for i in range(N - 1, n):
            low[i] = p[i] <= c[i - N + 1:i].min()
        s[f"L{N}"] = low
    ret = np.r_[0.0, c[1:] / c[:-1] - 1]
    rp = np.r_[0.0, p[1:] / c[:-1] - 1]
    vol = np.full(n, np.inf)
    for i in range(21, n):
        vol[i] = np.r_[ret[i - 19:i], rp[i]].std(ddof=1)
    s["D15"] = rp < -1.5 * vol
    cs = np.r_[0.0, np.cumsum(c)]
    sma = np.full(n, np.nan)
    sma[199:] = (cs[199:n] - cs[0:n - 199] + p[199:]) / 200
    filt = {"F0": np.ones(n, dtype=bool), "UP": p > sma, "DN": p < sma}
    for k in s:
        s[k][:200] = False
    return s, filt


def positions_up(sig, flt, up, exit_rule, stop=None):
    """fa.positions with the exit test read from ``up`` (this bar's close is above the previous close). With ``stop``:
    no entry on a flagged bar, and an open trade exits at it (R2: the last session of a week)."""
    n = len(sig)
    pos, entry = np.zeros(n), np.zeros(n)
    i = 0
    while i < n - 1:
        if sig[i] and flt[i] and (stop is None or not stop[i]):
            j = i + 1
            entry[j] = 1
            if exit_rule == "X1":
                last = j
            elif exit_rule == "X3":
                last = min(i + 3, n - 1)
            else:
                last = j
                while last < min(i + 5, n - 1) and not up[last]:
                    last += 1
            if stop is not None:
                last = next((q for q in range(j, last + 1) if stop[q]), last)
            pos[j:last + 1] = 1
            i = last
            continue
        i += 1
    return pos, entry


def variant_grid(d, sig, filt, up, fwd, rf, cost, mark, stop=None):
    """108 variants -> {name: (raw P&L, timing value, entries, exposure)}; fwd[t] is the return earned while held on t.
    Timing value = raw - exposure x the same-year mean excess return of this bar series (family A convention)."""
    yr = np.array([x.year for x in d])
    ex = fwd - rf
    mu = {y: float(ex[yr == y].mean()) for y in set(yr.tolist())}
    muv = np.array([mu[y] for y in yr])
    out = {}
    for sn in fa.SIGNALS:
        for exr in fa.EXITS:
            for fn in fa.FILTERS:
                pos, entry = positions_up(sig[sn], filt[fn], up, exr, stop)
                pnl = pos * ex - pos * mark - entry * cost
                out[f"{sn}|{exr}|{fn}"] = (pnl, pnl - pos * muv, entry, pos)
    return out


def next_open_grid(d, o, h, l, c, cost, mark, rates, keys):
    """(a), (b): signal at the bar close, entry at the next bar's open, exit at the open after the exit condition."""
    n = len(c)
    ret = np.r_[0.0, c[1:] / c[:-1] - 1]
    sig, filt = fa.signals(c, h, l, c, ret)
    up = np.r_[False, c[1:] > c[:-1]]
    fwd = np.r_[o[1:] / o[:-1] - 1, 0.0]  # held on bar t: from its open to the next bar's open
    rf = np.array([tbill(rates, keys, d[i], d[i + 1]) for i in range(n - 1)] + [0.0])
    return variant_grid(d, sig, filt, up, fwd, rf, cost, mark)


def mark_grid(d, c, p, hh, ll, cost, mark, rates, keys, no_weekend=False):
    """(c): signal, entry and exit at the mark 5 minutes before the cash close."""
    n = len(c)
    sig, filt = hybrid_signals(c, p, hh, ll)
    up = np.r_[False, p[1:] > c[:-1]]
    fwd = np.r_[0.0, p[1:] / p[:-1] - 1]  # held on bar t: from the previous mark to this mark
    rf = np.array([0.0] + [tbill(rates, keys, d[i - 1], d[i]) for i in range(1, n)])
    stop = np.array([(d[i + 1] - d[i]).days >= 3 for i in range(n - 1)] + [True]) if no_weekend else None
    return variant_grid(d, sig, filt, up, fwd, rf, cost, mark, stop)


def window(d, grid_out, lo=R1_START, hi=R1_END):
    keep = np.array([lo <= x <= hi for x in d])
    names = sorted(grid_out)
    R = np.array([grid_out[k][0][keep] for k in names]).T
    T = np.array([grid_out[k][1][keep] for k in names]).T
    yrs = (hi - lo).days / 365.25
    meta = {k: (float(grid_out[k][2][keep].sum() / yrs), float(grid_out[k][3][keep].mean())) for k in names}
    return [x for x, k in zip(d, keep) if k], names, R, T, meta


def ensemble(X):
    sd = X.std(0, ddof=1)
    w = np.where(sd > 0, 1 / np.where(sd > 0, sd, 1), 0)
    return X @ (w / w.sum())


def describe(R, T, meta=None):
    sr_r, sr_t = mt.sharpe(R, 252), mt.sharpe(T, 252)
    er, et = ensemble(R), ensemble(T)
    out = {"n_days": int(R.shape[0]), "median_sharpe_raw": float(np.median(sr_r)), "median_sharpe_timing": float(np.median(sr_t)),
           "share_positive_raw": float((sr_r > 0).mean()), "share_positive_timing": float((sr_t > 0).mean()),
           "spa_raw": mt.spa(R, 10, 2000)["p_spa"], "spa_timing": mt.spa(T, 10, 2000)["p_spa"],
           "ensemble_sharpe_raw": float(mt.sharpe(er[:, None], 252)[0]), "ensemble_t_raw": vs.nw_t(list(er), 5),
           "ensemble_sharpe_timing": float(mt.sharpe(et[:, None], 252)[0]), "ensemble_t_timing": vs.nw_t(list(et), 5)}
    if meta:
        out["median_trades_per_year"] = float(np.median([m[0] for m in meta.values()]))
        out["median_exposure"] = float(np.median([m[1] for m in meta.values()]))
    return out, sr_r, sr_t, er, et


def combine(series_by_market, markets):
    """Equal-risk sum of per-market ensemble series on a common date set (days a market is closed count as 0)."""
    days = sorted({x for m in markets for x in series_by_market[m][0]})
    di = {x: i for i, x in enumerate(days)}
    cols = []
    for m in markets:
        d, s = series_by_market[m]
        col = np.zeros(len(days))
        col[[di[x] for x in d]] = s / s.std(ddof=1)
        cols.append(col)
    tot = np.sum(cols, 0)
    return {"sharpe": float(mt.sharpe(tot[:, None], 252)[0]), "t_hac": vs.nw_t(list(tot), 5), "n_days": len(days)}, days, tot


def family_a_twin(sym):
    """Family A's grid for the same index on Yahoo closes (entry at the close), same window, for reference."""
    p = np.load(os.path.join(R9, "family_a.npz"))
    cal = [date.fromordinal(int(x)) for x in p["dates"]]
    cols = [str(c) for c in p["cols"]]
    ks = [i for i, c in enumerate(cols) if c.startswith(sym + "|")]
    keep = np.array([R1_START <= x <= R1_END for x in cal])
    d = [x for x, k in zip(cal, keep) if k]  # family A's union calendar (0 on days this index is closed), as in round 9
    return d, p["X"][keep][:, ks], p["XA"][keep][:, ks], [cols[i].split("|", 1)[1] for i in ks]


def run_r1():
    rates = irx_map()
    keys = sorted(rates)
    res = {"window": [str(R1_START), str(R1_END)], "markets": {}, "ensembles": {}}
    ens = {}  # (impl, basis) -> {market: (dates, series)}
    names_ref = None
    per_variant = {}
    for sym, (name, tz, op, close_of, cost, mark, twin) in R1_MARKETS.items():
        grids = {}
        d, o, h, l, c = broker_bars(sym)
        grids["a"] = (d, next_open_grid(d, o, h, l, c, cost, mark, rates, keys))
        d, so, sh, sl, sc, sm, mh, ml = session_bars(sym)
        grids["b"] = (d, next_open_grid(d, so, sh, sl, sc, cost, mark, rates, keys))
        grids["c"] = (d, mark_grid(d, sc, sm, mh, ml, cost, mark, rates, keys))
        grids["c_no_weekend"] = (d, mark_grid(d, sc, sm, mh, ml, cost, mark, rates, keys, no_weekend=True))
        res["markets"][name] = {}
        for impl, (dd, g) in grids.items():
            dw, names, R, T, meta = window(dd, g)
            names_ref = names_ref or names
            summary, sr_r, sr_t, er, et = describe(R, T, meta)
            res["markets"][name][impl] = summary
            for k, n_ in enumerate(names):
                per_variant.setdefault(f"{name}|{n_}", {})[impl] = {"sharpe_raw": float(sr_r[k]), "sharpe_timing": float(sr_t[k]),
                                                                     "trades_per_year": meta[n_][0], "exposure": meta[n_][1]}
            ens.setdefault((impl, "raw"), {})[name] = (dw, er)
            ens.setdefault((impl, "timing"), {})[name] = (dw, et)
        if twin:
            dt, R, T, tn = family_a_twin(twin)
            summary, sr_r, sr_t, er, et = describe(R, T)
            res["markets"][name]["family_a_yahoo_close"] = summary
            ens.setdefault(("family_a_yahoo_close", "raw"), {})[name] = (dt, er)
            ens.setdefault(("family_a_yahoo_close", "timing"), {})[name] = (dt, et)
            # daily correlation of each implementation's ensemble with the family A ensemble of the same index
            ref = dict(zip(dt, et))
            for impl in grids:
                dw, s = ens[(impl, "timing")][name]
                common = [(ref[x], v) for x, v in zip(dw, s) if x in ref]
                a_, b_ = np.array(common).T
                res["markets"][name][impl]["corr_with_family_a_ensemble_timing"] = float(np.corrcoef(a_, b_)[0, 1])
        print(name, json.dumps({k: {kk: round(vv, 3) if isinstance(vv, float) else vv for kk, vv in v.items()}
                                for k, v in res["markets"][name].items()}), flush=True)
    for (impl, basis), per in ens.items():
        for label, mk in (("US500+US100", ("US500", "US100")), ("US500+US100+JP225", EDGE_MARKETS), ("GER40", ("GER40",)), ("XAUUSD", ("XAUUSD",))):
            if all(m in per for m in mk):
                res["ensembles"].setdefault(label, {}).setdefault(impl, {})[basis] = combine(per, mk)[0]
    # R2: the no-weekend version against unrestricted (c)
    r2 = {}
    for label in ("US500+US100", "US500+US100+JP225"):
        e = res["ensembles"][label]
        r2[label] = {basis: {"c": e["c"][basis]["sharpe"], "c_no_weekend": e["c_no_weekend"][basis]["sharpe"],
                             "ratio": e["c_no_weekend"][basis]["sharpe"] / e["c"][basis]["sharpe"] if e["c"][basis]["sharpe"] else None}
                     for basis in ("raw", "timing")}
    res["r2_no_weekend"] = r2
    res["variants"] = per_variant
    json.dump(res, open(os.path.join(OUT, "round11_r1.json"), "w"), indent=1, default=str)
    print(json.dumps(res["ensembles"], indent=1))
    print(json.dumps(r2, indent=1))


# ---------------------------------------------------------------- Part 1: R3 (SQX-native versions of N3)

def run_r3():
    res = {}
    for sym, ref_col, cost in (("NSXUSD", "NSXUSD|L14|b1|g30|flip", 1.5), ("SPXUSD", "SPXUSD|L14|b1|g30|flip", 1.5)):
        t, x = local(sym, YEARS, NY)
        day, mod = t // 1440, t % 1440
        ins = (mod >= 570) & (mod < 960)
        keys, _, sh, sl, _, cnt, st = group(day[ins], x[ins])
        xi, mi = x[ins], mod[ins]
        po, pc, pf = price_at(day, mod, x, 570, prefer_open=True), price_at(day, mod, x, 960), price_at(day, mod, x, 959)
        valid = [i for i, k in enumerate(keys.tolist()) if cnt[i] >= 300 and k in po and k in pc and k in pf and day_of(k).weekday() < 5]
        tr = {}
        prev = None
        info = []
        for i in valid:
            k = int(keys[i])
            if prev is not None:
                pcl = pc[int(keys[prev])]
                tr[i] = max(sh[i], pcl) - min(sl[i], pcl)
                info.append((i, prev))
            prev = i
        out = {}
        for base in ("range", "atr14"):
            for kk in (0.3, 0.5, 0.7):
                for mode in ("flat", "reverse"):
                    out[f"{base}|k{kk}|{mode}"] = {}
        trs = []
        for i, pv in info:
            k = int(keys[i])
            d = day_of(k)
            trs.append(tr[i])
            width = {"range": sh[pv] - sl[pv], "atr14": float(np.mean(trs[-15:-1])) if len(trs) > 14 else None}
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
                                hit = dnt[j0:] if pos == 1 else upt[j0:]
                                cand = np.nonzero(hit)[0]
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
        p = np.load(os.path.join(R9, f"family_b_{sym}.npz"))
        cols = [str(c) for c in p["cols"]]
        ref = {date.fromordinal(int(dd)): float(v) for dd, v in zip(p["dates"], p["X"][:, cols.index(ref_col)])}
        days = sorted(x for x in ref if R1_START <= x <= R1_END)
        rv = np.array([ref[x] for x in days])
        sr_ref = float(rv.mean() / rv.std(ddof=1) * math.sqrt(252))
        rs = {"reference": ref_col, "reference_sharpe": sr_ref, "reference_mean_bps": float(rv.mean() * 1e4), "reference_t": vs.nw_t(list(rv), 5),
              "n_days": len(days), "variants": {}}
        for name, rows_ in out.items():
            v = np.array([rows_.get(x, (0.0, 0))[0] for x in days])
            ent = np.array([rows_.get(x, (0.0, 0))[1] for x in days])
            rs["variants"][name] = {"sharpe": float(v.mean() / v.std(ddof=1) * math.sqrt(252)), "mean_bps": float(v.mean() * 1e4), "t_hac": vs.nw_t(list(v), 5),
                                    "corr_with_reference": float(np.corrcoef(v, rv)[0, 1]), "entries_per_day": float(ent.mean()),
                                    "sharpe_2014_2019": float(mt.sharpe(v[[x.year < 2020 for x in days]][:, None], 252)[0]),
                                    "sharpe_2020_2026": float(mt.sharpe(v[[x.year >= 2020 for x in days]][:, None], 252)[0])}
        sh_ = [v["sharpe"] for v in rs["variants"].values()]
        co_ = [v["corr_with_reference"] for v in rs["variants"].values()]
        rs["median_sharpe"], rs["median_corr"] = float(np.median(sh_)), float(np.median(co_))
        rs["recommend_native_build"] = bool(rs["median_sharpe"] >= 0.7 * sr_ref and rs["median_corr"] >= 0.5)
        res[sym] = rs
        print(sym, json.dumps({k: v for k, v in rs.items() if k != "variants"}), flush=True)
        for name, v in rs["variants"].items():
            print("   ", name, {k: round(x, 3) for k, x in v.items()})
    json.dump(res, open(os.path.join(OUT, "round11_r3.json"), "w"), indent=1, default=str)


# ---------------------------------------------------------------- Part 2: families L, M, Q, R

def open_at(day, mod, x, m, tol=2):
    """{day: open of the first bar in [m, m + tol]} (for marks at midnight, where price_at would look into the prior day)."""
    out = {}
    for mm in range(m + tol, m - 1, -1):
        sel = np.nonzero(mod == mm)[0]
        out.update(zip(day[sel].tolist(), x[sel, O].tolist()))
    return out


def gap_week(d: date) -> bool:
    """True in the US/EU daylight-saving gap weeks (London - New York = 4 h instead of 5 h)."""
    from data_histdata import clock_shift
    return clock_shift(d, NY) - clock_shift(d, LONDON) == -240


def to_matrix(per, cal):
    """per: {column: {date: pnl}} -> T x K matrix on ``cal``."""
    ci = {d: i for i, d in enumerate(cal)}
    names = sorted(per)
    X = np.zeros((len(cal), len(names)))
    for k, n in enumerate(names):
        for d, v in per[n].items():
            if d in ci:
                X[ci[d], k] += v
    return X, names


def trade_stats(per, names, split):
    """Per column: trades per year and mean net bps per trade, discovery and validation."""
    out = {}
    for n in names:
        rows = per[n]
        a = [v for d, v in rows.items() if d < split]
        b = [v for d, v in rows.items() if d >= split]
        yrs_a = max((split - min(rows)).days / 365.25, 1e-9) if a else None
        yrs_b = max((max(rows) - split).days / 365.25, 1e-9) if b else None
        out[n] = {"trades_disc": len(a), "trades_val": len(b), "trades_per_year_val": len(b) / yrs_b if b else 0.0,
                  "mean_bps_disc": float(np.mean(a) * 1e4) if a else None, "mean_bps_val": float(np.mean(b) * 1e4) if b else None,
                  "hit_rate_val": float(np.mean(np.array(b) > 0)) if b else None}
    return out


def bracket_exit(bars, pos, sl, tp, default):
    """Exit price of a position (pos = +1 long, -1 short) over minute bars with a stop-loss and an optional target.
    The stop is tested first inside a bar (conservative); a bar opening beyond the stop fills at its open."""
    if len(bars) == 0:
        return default
    bo, bh, bl = bars[:, O], bars[:, H], bars[:, L]
    s_hit = np.nonzero(bl <= sl if pos == 1 else bh >= sl)[0]
    t_hit = np.nonzero(bh >= tp if pos == 1 else bl <= tp)[0] if tp is not None else np.array([], dtype=int)
    a = int(s_hit[0]) if len(s_hit) else None
    b = int(t_hit[0]) if len(t_hit) else None
    if a is not None and (b is None or a <= b):
        return min(sl, bo[a]) if pos == 1 else max(sl, bo[a])
    if b is not None:
        return tp
    return default


L_INSTR = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "XAUUSD")
L_WINDOWS = {"ASIA": (0, 420), "EUROPE": (420, 720), "OVERLAP": (720, 960), "USPM": (960, 1260)}  # London minutes
L_SPLIT = date(2014, 1, 1)


def family_l():
    """Session seasonality (Breedon & Ranaldo 2013): long or short each London-time window, every weekday."""
    per = {}
    for sym in L_INSTR:
        t, x = local(sym, range(2003, 2027), LONDON)
        day, mod = t // 1440, t % 1440
        cost = 2.5e-4 if sym in METALS else 1.0e-4
        px = {0: open_at(day, mod, x, 0)}
        for m in (420, 720, 960, 1245, 1260):
            px[m] = price_at(day, mod, x, m)
        for w, (a, b) in L_WINDOWS.items():
            lo, sh = {}, {}
            for k, pa in px[a].items():
                d = day_of(k)
                if d.weekday() >= 5:
                    continue
                bb = 1245 if (b == 1260 and gap_week(d)) else b  # A24: no window may reach 16:45 NY
                pb = px[bb].get(k)
                if pb is None:
                    continue
                r_ = pb / pa - 1
                lo[d], sh[d] = r_ - cost, -r_ - cost
            per[f"{sym}|{w}|L"], per[f"{sym}|{w}|S"] = lo, sh
        print("L", sym, len(lo), flush=True)
    cal = weekday_calendar(date(2003, 1, 1), max(max(v) for v in per.values()))
    X, names = to_matrix(per, cal)
    res = finish("L", X, None, names, cal, L_SPLIT, 2014)
    json.dump({"trade_stats": trade_stats(per, names, L_SPLIT)}, open(os.path.join(OUT, "family_l_trades.json"), "w"), indent=1)
    return res


M_INSTR = ("EURGBP", "EURCHF", "AUDNZD", "EURCAD", "AUDCAD", "GBPCHF", "USDCAD", "USDCHF", "EURUSD")
M_MAJORS = ("USDCAD", "USDCHF", "EURUSD")
M_SPLIT = date(2016, 1, 1)


def family_m():
    """Night mean reversion on M15 bars: fade a close outside BB(20, k) or an RSI(3) extreme, entries 19:00-00:45 NY."""
    per = {}
    for sym in M_INSTR:
        t, x = local(sym, range(2008, 2027), NY)
        mod = t % 1440
        k_ = (mod < 1005) | (mod >= 1140)  # A24 data rule: nothing from 16:45 to 19:00 NY
        keys, _, _, _, c, _, _ = group(t[k_] // 15, x[k_])
        start = keys * 15  # bar start, local minutes since epoch
        close_t = start + 15
        n = len(c)
        cs, cs2 = np.r_[0.0, np.cumsum(c)], np.r_[0.0, np.cumsum(c * c)]
        sma, sd = np.full(n, np.nan), np.full(n, np.nan)
        sma[19:] = (cs[20:] - cs[:-20]) / 20
        sd[19:] = np.sqrt(np.maximum((cs2[20:] - cs2[:-20]) / 20 - sma[19:] ** 2, 0))
        rsi = np.full(n, 50.0)
        g = l_ = None
        for i in range(1, n):
            ch = c[i] - c[i - 1]
            up, dn = max(ch, 0.0), max(-ch, 0.0)
            g, l_ = (up, dn) if g is None else ((g * 2 + up) / 3, (l_ * 2 + dn) / 3)
            rsi[i] = 100.0 if l_ == 0 else 100 - 100 / (1 + g / l_)
        sm = start % 1440
        night = (sm >= 1140) | (sm <= 45)
        entry_ok = (sm >= 1140) | (sm <= 30)
        nid = (start + 300) // 1440  # trading date: the night from 19:00 NY belongs to the next date
        idx = np.nonzero(night)[0]
        cost = 1.5e-4 if sym in M_MAJORS else 3.0e-4
        for sig in ("BB1.5", "BB2", "BB2.5", "RSI3"):
            if sig.startswith("BB"):
                kk = float(sig[2:])
                long_s, short_s = c < sma - kk * sd, c > sma + kk * sd
                mid_long, mid_short = c >= sma, c <= sma
            else:
                long_s, short_s = rsi < 10, rsi > 90
                mid_long, mid_short = rsi >= 50, rsi <= 50
            for ex in ("MID", "T1H", "0100"):
                rows = {}
                pos, px, t_in = 0, 0.0, 0
                for j, i in enumerate(idx):
                    last_of_night = j == len(idx) - 1 or nid[idx[j + 1]] != nid[i]
                    if pos != 0:
                        done = last_of_night or (ex == "MID" and (mid_long[i] if pos == 1 else mid_short[i])) \
                            or (ex == "T1H" and close_t[i] >= t_in + 60)
                        if done:
                            d = day_of(nid[i])
                            rows[d] = rows.get(d, 0.0) + pos * (c[i] / px - 1) - cost
                            pos = 0
                    if pos == 0 and entry_ok[i] and not last_of_night and not np.isnan(sma[i]):
                        if long_s[i]:
                            pos, px, t_in = 1, c[i], close_t[i]
                        elif short_s[i]:
                            pos, px, t_in = -1, c[i], close_t[i]
                per[f"{sym}|{sig}|{ex}"] = rows
        print("M", sym, n, flush=True)
    cal = weekday_calendar(date(2008, 1, 1), max(max(v) for v in per.values() if v))
    X, names = to_matrix(per, cal)
    res = finish("M", X, None, names, cal, M_SPLIT, 2016)
    json.dump({"trade_stats": trade_stats(per, names, M_SPLIT)}, open(os.path.join(OUT, "family_m_trades.json"), "w"), indent=1)
    return res


Q_MARKETS = {"GRXEUR": ("GER40", BERLIN, 540, 1050, 1.5e-4), "UKXGBP": ("UK100", LONDON, 480, 990, 2.0e-4),
             "FRXEUR": ("FRA40", PARIS, 540, 1050, 2.0e-4)}
Q_SPLIT = date(2020, 1, 1)


def family_q():
    """European cash-open gap: fade or follow a gap larger than k x its 20-day mean."""
    per = {}
    for sym, (name, tz, op, cl, cost) in Q_MARKETS.items():
        t, x = local(sym, YEARS, tz)
        day, mod = t // 1440, t % 1440
        po, pc = price_at(day, mod, x, op, prefer_open=True), price_at(day, mod, x, cl)
        p11, p13 = price_at(day, mod, x, 660), price_at(day, mod, x, 780)
        ins = (mod >= op) & (mod < cl)
        keys, _, _, _, _, cnt, st = group(day[ins], x[ins])
        xi = x[ins]
        sessions = [(int(k), s_, n_) for k, s_, n_ in zip(keys.tolist(), st.tolist(), cnt.tolist())
                    if n_ >= 0.5 * (cl - op) and k in po and k in pc and day_of(k).weekday() < 5]
        gaps = []
        for q in range(1, len(sessions)):
            k, s_, n_ = sessions[q]
            kp = sessions[q - 1][0]
            if k - kp > 5:
                gaps.append(None)
                continue
            gaps.append((k, s_, n_, pc[kp], po[k] / pc[kp] - 1))
        hist = []
        for g_ in gaps:
            if g_ is None:
                continue
            k, s_, n_, prev_c, gap = g_
            ready = len(hist) >= 20
            mean20 = float(np.mean(hist[-20:])) if ready else None
            hist.append(abs(gap))
            if not ready or gap == 0:
                continue
            d = day_of(k)
            o0 = po[k]
            bars = xi[s_:s_ + n_]
            for kk in (0.5, 1.0, 1.5):
                if abs(gap) <= kk * mean20:
                    continue
                for how in ("FADE", "FOLLOW"):
                    dr = -np.sign(gap) if how == "FADE" else np.sign(gap)
                    for ex in ("1100", "1300", "CLOSE", "FILL"):
                        if ex == "FILL":
                            dist = abs(o0 - prev_c)
                            tp, sl = o0 + dr * dist, o0 - dr * dist
                            out_px = bracket_exit(bars, dr, sl, tp, pc[k])
                        else:
                            out_px = {"1100": p11, "1300": p13, "CLOSE": pc}[ex].get(k)
                            if out_px is None:
                                continue
                        per.setdefault(f"{name}|k{kk:g}|{how}|{ex}", {})[d] = dr * (out_px / o0 - 1) - cost
        print("Q", name, len(sessions), flush=True)
    cal = weekday_calendar(date(2013, 1, 1), max(max(v) for v in per.values()))
    X, names = to_matrix(per, cal)
    res = finish("Q", X, None, names, cal, Q_SPLIT, 2020)
    json.dump({"trade_stats": trade_stats(per, names, Q_SPLIT)}, open(os.path.join(OUT, "family_q_trades.json"), "w"), indent=1)
    return res


R_INSTR = ("XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD")
R_RANGES = {"ASIA": (0, 420, 420, 720), "LDNAM": (420, 780, 780, 960)}  # range from, to; traded from, to (London minutes)
R_SPLIT = date(2017, 1, 1)


def family_r():
    """Session-range breakout (stop at the edge, stop-loss at the other edge) or fade (limit at the edge, stop 50% of
    the range beyond it); exit at the window end or a 1x-range target. One trade per day per variant."""
    per = {}
    for sym in R_INSTR:
        t, x = local(sym, range(2010, 2027), LONDON)
        day, mod = t // 1440, t % 1440
        cost = {"XAUUSD": 2.5e-4, "XAGUSD": 5.0e-4}.get(sym, 1.0e-4)
        for rn, (ra, rb, ta, tb) in R_RANGES.items():
            rin = (mod >= ra) & (mod < rb)
            rk, _, rh, rl, _, rc, _ = group(day[rin], x[rin])
            rng_ = {int(k): (h_, l_) for k, h_, l_, n_ in zip(rk.tolist(), rh.tolist(), rl.tolist(), rc.tolist()) if n_ >= 0.5 * (rb - ra)}
            tin = (mod >= ta) & (mod < tb)
            tk, _, _, _, _, tc, ts = group(day[tin], x[tin])
            xt = x[tin]
            p_end = price_at(day, mod, x, tb)
            for k, s_, n_ in zip(tk.tolist(), ts.tolist(), tc.tolist()):
                d = day_of(k)
                if d.weekday() >= 5 or k not in rng_ or k not in p_end or n_ < 0.5 * (tb - ta):
                    continue
                Hh, Ll = rng_[k]
                R_ = Hh - Ll
                if R_ <= 0:
                    continue
                bars = xt[s_:s_ + n_]
                bo, bh, bl = bars[:, O], bars[:, H], bars[:, L]
                up_t, dn_t = bh >= Hh, bl <= Ll
                touch = np.nonzero(up_t | dn_t)[0]
                if not len(touch):
                    continue
                j = int(touch[0])
                first_up = bool(up_t[j]) and (not dn_t[j] or Hh - bo[j] <= bo[j] - Ll)
                for rule in ("BRK", "FADE"):
                    if rule == "BRK":
                        pos = 1 if first_up else -1
                        px = max(Hh, bo[j]) if pos == 1 else min(Ll, bo[j])
                        sl = Ll if pos == 1 else Hh
                    else:
                        pos = -1 if first_up else 1
                        px = Hh if pos == -1 else Ll
                        sl = Hh + 0.5 * R_ if pos == -1 else Ll - 0.5 * R_
                    for ex in ("END", "TGT"):
                        if (pos == 1 and bl[j] <= sl) or (pos == -1 and bh[j] >= sl):  # stop inside the entry bar
                            out_px = sl
                        else:
                            out_px = bracket_exit(bars[j + 1:], pos, sl, px + pos * R_ if ex == "TGT" else None, p_end[k])
                        per.setdefault(f"{sym}|{rn}|{rule}|{ex}", {})[d] = pos * (out_px / px - 1) - cost
        print("R", sym, flush=True)
    cal = weekday_calendar(date(2010, 1, 1), max(max(v) for v in per.values()))
    X, names = to_matrix(per, cal)
    res = finish("R", X, None, names, cal, R_SPLIT, 2017)
    json.dump({"trade_stats": trade_stats(per, names, R_SPLIT)}, open(os.path.join(OUT, "family_r_trades.json"), "w"), indent=1)
    return res


if __name__ == "__main__":
    {"R1": run_r1, "R3": run_r3, "L": family_l, "M": family_m, "Q": family_q, "R": family_r}[sys.argv[1]]()
