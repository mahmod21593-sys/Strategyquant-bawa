"""Round 12 (PREREGISTRATION.md A26): edge research with SQX-buildable designs.

    python3 run_round12.py S    short side of index reversal (Yahoo daily)         -> results/family_s.json
    python3 run_round12.py T    reversal anatomy: exit timing + overnight-drift check -> results/family_t.json
    python3 run_round12.py U    US macro-release shocks, follow or fade              -> results/family_u.json
    python3 run_round12.py V    precious-metals auction windows                      -> results/family_v.json
    python3 run_round12.py W    FX weekend-gap reversal (Dao, McGroarty & Urquhart 2016) -> results/family_w.json
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date, datetime, timedelta

import numpy as np

import multitest as mt
import run_family_a as fa
import vstats as vs
from data_histdata import NY
from data_minutes import EPOCH, day_of, local, price_at
from run_round4 import irx_map, tbill
from run_round10 import finish, positions_dir, weekday_calendar
from run_round11 import LONDON, R1_END, R1_MARKETS, TOKYO, gap_week, hybrid_signals, session_bars, to_matrix, trade_stats

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
fa.N_TRIALS = 7895


def ny_minutes(dt: datetime) -> int:
    """Aware datetime -> New York wall-clock minutes since 1970-01-01."""
    x = dt.astimezone(NY)
    return (x.date().toordinal() - EPOCH) * 1440 + x.hour * 60 + x.minute


class Tape:
    """Minute bars on the New York clock with price lookups at any NY minute."""

    def __init__(self, sym, years):
        self.t, self.x = local(sym, years, NY)

    def at(self, T, tol=5):
        """Price at NY minute T: close of the last bar starting in [T - tol, T - 1], else the open of the first bar
        starting in [T, T + tol]."""
        i = int(np.searchsorted(self.t, T))  # first bar starting >= T
        if i > 0 and self.t[i - 1] >= T - tol:
            return float(self.x[i - 1, 3])
        if i < len(self.t) and self.t[i] <= T + tol:
            return float(self.x[i, 0])
        return None

    def first_open_from(self, T, horizon=4 * 1440):
        i = int(np.searchsorted(self.t, T))
        if i < len(self.t) and self.t[i] <= T + horizon:
            return float(self.x[i, 0]), int(self.t[i])
        return None, None


# ---------------------------------------------------------------- family S: short side of index reversal

def family_s():
    rates = irx_map()
    keys = sorted(rates)
    from data_yahoo import daily
    cal = sorted({r["date"] for s in fa.US + fa.WORLD for r in daily(s) if fa.START <= r["date"] <= fa.END and r["date"].weekday() < 5})
    ci = {x: i for i, x in enumerate(cal)}
    cols, raw, tim, exp_, meta = [], [], [], [], []
    for sym in fa.US + fa.WORLD:
        d, c, h, l, craw, ret, rf = fa.load(sym, rates, keys)
        ha, la = h * c / craw, l * c / craw
        m = 2 * c.max()
        sig, filt = fa.signals(m - c, m - la, m - ha, m - c, -ret)  # mirror: strength signals
        flt = {"F0": filt["F0"], "TR": filt["UP"], "CT": filt["DN"]}  # mirror UP = below SMA(200): with the trend for a short
        idx = np.array([ci[x] for x in d if x in ci])
        keep = np.array([x in ci for x in d])
        mark = fa.MARKUP if sym in fa.US else 0.0
        yr = np.array([x.year for x in d])
        ex = ret - rf
        ymu = {y: float(ex[yr == y].mean()) for y in set(yr.tolist())}
        mu = np.array([ymu[y] for y in yr])
        cs = np.concatenate([[0.0], np.cumsum(ex)[:-1]])
        n_ = np.arange(len(ex), dtype=float)
        mu_e = np.where(n_ >= 252, cs / np.maximum(n_, 1), 0.0)
        for sn in fa.SIGNALS:
            for exr in fa.EXITS:
                for fn in ("F0", "TR", "CT"):
                    pos, entry = positions_dir(sig[sn], flt[fn], c, exr, -1)
                    pnl = pos * ex - np.abs(pos) * mark - entry * fa.COST
                    for store, v in ((raw, pnl), (tim, pnl - pos * mu), (exp_, pnl - pos * mu_e)):
                        col = np.zeros(len(cal))
                        col[idx] = v[keep]
                        store.append(col)
                    name = f"{sym}|S{sn}|{'XD' if exr == 'XU' else exr}|{fn}"
                    cols.append(name)
                    meta.append({"name": name, "trades_per_year": float(entry.sum() / (len(d) / 252)), "exposure": float(np.abs(pos).mean())})
        print("S", sym, flush=True)
    X, XA, XE = np.array(raw).T, np.array(tim).T, np.array(exp_).T
    np.savez_compressed(os.path.join(R9, "family_s.npz"), X=X, XA=XA, XE=XE, dates=np.array([x.toordinal() for x in cal]), cols=np.array(cols))
    years = np.array([x.year for x in cal])
    disc = np.array([x < fa.SPLIT for x in cal])
    res = {"n_variants": len(cols)}
    for lab, M in (("timing", XA), ("raw", X), ("timing_expanding", XE)):
        res[lab] = fa.battery(M, cols, disc, ~disc, years)
    for mrow, a, v, t_, p in zip(meta, res["raw"]["_sr_d"], res["raw"]["_sr_v"], res["timing"]["_sr_v"], res["timing"]["_p_rw"]):
        mrow.update({"sharpe_discovery": a, "sharpe_validation_raw": v, "sharpe_validation_timing": t_, "rw_p_timing": p})
    for lab in ("timing", "raw", "timing_expanding"):
        for k in ("_sr_d", "_sr_v", "_p_rw"):
            res[lab].pop(k)
    res["variants"] = meta
    res["family_verdict"] = res["timing"]["verdict"]
    json.dump(res, open(os.path.join(OUT, "family_s.json"), "w"), indent=1, default=str)
    for lab in ("timing", "raw", "timing_expanding"):
        b = res[lab]
        print(lab, {k: b[k] for k in ("spa_validation", "pbo_full_sample", "selection_test", "walk_forward_top5", "best_validation_variant", "verdict")})
        for inst, v in b["per_instrument"].items():
            print("   ", inst, v)


# ---------------------------------------------------------------- family T: where the reversal return is earned

T_MARKETS = ("SPXUSD", "NSXUSD", "JPXJPY", "GRXEUR")
T_SPLIT = date(2020, 1, 1)


def mark_minutes(sym, d):
    """NY minutes of the pre-close mark on session date d."""
    name, tz, op, close_of, *_ = R1_MARKETS[sym]
    m = close_of(d) - 5
    return ny_minutes(datetime(d.year, d.month, d.day, m // 60, m % 60, tzinfo=tz))


def next_0300(T):
    """First 03:00 NY strictly after NY minute T, on a weekday."""
    day = T // 1440
    cand = day * 1440 + 180
    if cand <= T:
        cand += 1440
    while day_of(cand // 1440).weekday() >= 5:
        cand += 1440
    return cand


def family_t():
    rates = irx_map()
    keys = sorted(rates)
    per, per_raw_all = {}, {}
    mech = {}
    for sym in T_MARKETS:
        name, tz, op, close_of, cost, mark, _ = R1_MARKETS[sym]
        d, so, sh, sl, sc, sm, mh, ml = session_bars(sym)
        tape = Tape(sym, range(2013, 2027))
        n = len(d)
        sig, filt = hybrid_signals(sc, sm, mh, ml)
        # exit prices for a trade entered at mark i
        e1, e2, e3, fin = np.full(n, np.nan), np.full(n, np.nan), np.full(n, np.nan), np.zeros(n)
        for i in range(n - 1):
            if (d[i + 1] - d[i]).days > 5:
                continue
            T0 = mark_minutes(sym, d[i])
            p1 = tape.at(next_0300(T0))
            e1[i] = p1 / sm[i] - 1 if p1 else np.nan
            e2[i] = so[i + 1] / sm[i] - 1
            e3[i] = sm[i + 1] / sm[i] - 1
            fin[i] = tbill(rates, keys, d[i], d[i + 1]) + mark
        exits = {"E1": e1, "E2": e2, "E3": e3}
        yr = np.array([x.year for x in d])
        for en, r in exits.items():
            ok = np.isfinite(r)
            mu = {y: float(np.nanmean((r - fin)[(yr == y) & ok])) for y in set(yr.tolist())}
            for sn in fa.SIGNALS:
                for fn in fa.FILTERS:
                    s = sig[sn] & filt[fn].astype(bool) & ok
                    rows_raw = {}
                    rows_tim = {}
                    for i in np.nonzero(s)[0]:
                        v = r[i] - fin[i] - cost
                        rows_raw[d[i + 1]] = v
                        rows_tim[d[i + 1]] = v - mu[yr[i]]
                    per.setdefault(en, {})[f"{name}|{sn}|{fn}"] = rows_tim
                    per_raw_all.setdefault(en, {})[f"{name}|{sn}|{fn}"] = rows_raw
        if sym in ("SPXUSD", "NSXUSD"):  # T3: the Boyarchenko mechanism, post-publication
            rows = []
            for i in range(1, n - 1):
                if (d[i + 1] - d[i]).days > 5 or (d[i] - d[i - 1]).days > 5:
                    continue
                T0 = mark_minutes(sym, d[i])
                t3 = next_0300(T0)
                p2, p3 = tape.at(t3 - 60), tape.at(t3)
                if not (p2 and p3):
                    continue
                rows.append((d[i], sc[i] < sc[i - 1], p3 / p2 - 1, so[i + 1] / sc[i] - 1))
            out = {}
            for lab, lo, hi in (("2014-2020", date(2014, 1, 1), date(2020, 12, 31)), ("2021-2026", date(2021, 1, 1), R1_END)):
                sel = [r_ for r_ in rows if lo <= r_[0] <= hi]
                for k, col in (("r_0200_0300", 2), ("r_1600_0930", 3)):
                    dn = np.array([r_[col] for r_ in sel if r_[1]])
                    up = np.array([r_[col] for r_ in sel if not r_[1]])
                    y = np.array([r_[col] for r_ in sel])
                    z = np.array([1.0 if r_[1] else 0.0 for r_ in sel])
                    b, t_ = ols_nw(y, z, 5)
                    out[f"{lab}|{k}"] = {"after_down_bps": float(dn.mean() * 1e4), "after_up_bps": float(up.mean() * 1e4), "all_bps": float(y.mean() * 1e4),
                                         "all_t": vs.nw_t(list(y), 5), "diff_down_minus_up_bps": float(b * 1e4), "diff_t_hac": t_, "n": int(len(sel))}
            mech[name] = out
            print("T3", name, json.dumps(out), flush=True)
        print("T", name, flush=True)
    res = {"mechanism_T3": mech, "exits": {}}
    ens = {}
    for en in ("E1", "E2", "E3"):
        cal = weekday_calendar(date(2014, 1, 1), R1_END)
        XT, names = to_matrix(per[en], cal)
        XR, _ = to_matrix(per_raw_all[en], cal)
        active = np.abs(XR).sum(1) > 0
        first = int(np.argmax(active))
        cal2, XT, XR = cal[first:], XT[first:], XR[first:]
        val = np.array([x >= T_SPLIT for x in cal2])
        years = np.array([x.year for x in cal2])
        r = {"timing": fa.battery(XT, names, ~val, val, years, first_wf=2020), "raw": fa.battery(XR, names, ~val, val, years, first_wf=2020)}
        for lab in r:
            for k in ("_sr_d", "_sr_v", "_p_rw"):
                r[lab].pop(k)
        # equal-risk ensemble over the three edge markets, validation and full window
        edge = [k for k, nm in enumerate(names) if not nm.startswith("GER40")]
        for lab, M in (("timing", XT), ("raw", XR)):
            E = M[:, edge]
            sd = E.std(0, ddof=1)
            w = np.where(sd > 0, 1 / np.where(sd > 0, sd, 1), 0)
            e = E @ (w / w.sum())
            ens[(en, lab)] = e
            r[f"ensemble_{lab}"] = {"sharpe_full": float(mt.sharpe(e[:, None], 252)[0]), "t_full": vs.nw_t(list(e), 5),
                                    "sharpe_2014_2019": float(mt.sharpe(e[~val][:, None], 252)[0]), "sharpe_2020_2026": float(mt.sharpe(e[val][:, None], 252)[0])}
        res["exits"][en] = r
        print(en, "timing", {k: r["timing"][k] for k in ("spa_validation", "pbo_full_sample", "walk_forward_top5", "verdict")}, flush=True)
        print(en, "ensembles", r["ensemble_timing"], r["ensemble_raw"], flush=True)
        for inst, v in r["timing"]["per_instrument"].items():
            print("   ", inst, v)
    # T2: bootstrap interval for the Sharpe differences (same calendar across exits)
    L = min(len(v) for v in ens.values())
    W = mt.boot_weights(L, 10, 2000, seed=11)
    for lab in ("timing", "raw"):
        base = ens[("E3", lab)][-L:]
        for en in ("E1", "E2"):
            x = ens[(en, lab)][-L:]
            def srw(v):
                m1 = W @ v / L
                m2 = W @ (v * v) / L
                return m1 / np.sqrt(np.maximum(m2 - m1 * m1, 1e-18)) * math.sqrt(252)
            dd = srw(x) - srw(base)
            res.setdefault("T2_sharpe_difference", {})[f"{en}-E3|{lab}"] = {
                "point": float(mt.sharpe(x[:, None], 252)[0] - mt.sharpe(base[:, None], 252)[0]),
                "ci95": [float(np.quantile(dd, 0.025)), float(np.quantile(dd, 0.975))], "corr": float(np.corrcoef(x, base)[0, 1])}
    print("T2", json.dumps(res["T2_sharpe_difference"]), flush=True)
    json.dump(res, open(os.path.join(OUT, "family_t.json"), "w"), indent=1, default=str)


def ols_nw(y, z, lag):
    """Slope of y on [1, z] with a Newey-West t."""
    X = np.column_stack([np.ones(len(y)), z])
    XtX = np.linalg.inv(X.T @ X)
    b = XtX @ X.T @ y
    e = y - X @ b
    S = (X * e[:, None]).T @ (X * e[:, None])
    for k in range(1, lag + 1):
        G = (X[k:] * e[k:, None]).T @ (X[:-k] * e[:-k, None])
        S += (1 - k / (lag + 1)) * (G + G.T)
    V = XtX @ S @ XtX
    return float(b[1]), float(b[1] / math.sqrt(V[1, 1]))


# ---------------------------------------------------------------- family U: US macro-release shocks

U_INSTR = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "XAUUSD", "XAGUSD", "SPXUSD", "NSXUSD")
U_NAME = {"SPXUSD": "US500", "NSXUSD": "US100"}
U_COST = {"XAUUSD": 3.0e-4, "XAGUSD": 6.0e-4, "SPXUSD": 2.0e-4, "NSXUSD": 2.0e-4}
U_SPLIT = date(2018, 1, 1)


def family_u():
    per = {}
    for sym in U_INSTR:
        is_idx = sym in ("SPXUSD", "NSXUSD")
        tape = Tape(sym, range(2013 if is_idx else 2010, 2027))
        days = sorted({int(v) for v in np.unique(tape.t // 1440)})
        cost = U_COST.get(sym, 1.5e-4)
        eod = 955 if is_idx else 1000
        name = U_NAME.get(sym, sym)
        for T in (510, 600, 840):
            hist = []
            for k in days:
                dd = day_of(k)
                if dd.weekday() >= 5:
                    continue
                base = k * 1440
                p0, p5 = tape.at(base + T), tape.at(base + T + 5)
                if not (p0 and p5):
                    continue
                r0 = p5 / p0 - 1
                ready = len(hist) >= 40
                med = float(np.median(hist[-60:])) if ready else None
                hist.append(abs(r0))
                if not ready or med <= 0:
                    continue
                exits = {}
                for en, m in (("H1", min(T + 65, eod)), ("H2", min(T + 125, eod)), ("EOD", eod)):
                    p = tape.at(base + m)
                    if p:
                        exits[en] = p
                for kk in (3, 6):
                    if abs(r0) <= kk * med:
                        continue
                    for how, sgn in (("FOLLOW", 1.0), ("FADE", -1.0)):
                        dr = sgn * math.copysign(1.0, r0)
                        for en, p in exits.items():
                            per.setdefault(f"{name}|{T // 60:02d}{T % 60:02d}|k{kk}|{how}|{en}", {})[dd] = dr * (p / p5 - 1) - cost
        print("U", sym, flush=True)
    cal = weekday_calendar(date(2010, 1, 1), max(max(v) for v in per.values()))
    X, names = to_matrix(per, cal)
    res = finish("U", X, None, names, cal, U_SPLIT, 2018)
    json.dump({"trade_stats": trade_stats(per, names, U_SPLIT)}, open(os.path.join(OUT, "family_u_trades.json"), "w"), indent=1)
    return res


# ---------------------------------------------------------------- family V: precious-metals auction windows

V_EVENTS = {"XAUUSD": (("LBMA_AM", LONDON, 630), ("LBMA_PM", LONDON, 900), ("COMEX", NY, 500)),
            "XAGUSD": (("LBMA", LONDON, 720), ("COMEX", NY, 505))}
V_SPLIT = date(2017, 1, 1)


def family_v():
    per = {}
    for sym, events in V_EVENTS.items():
        cost = 2.5e-4 if sym == "XAUUSD" else 5.0e-4
        tapes = {}
        for ev, tz, m in events:
            if tz not in tapes:
                tapes[tz] = local(sym, range(2009, 2027), tz)
            t, x = tapes[tz]
            day, mod = t // 1440, t % 1440
            px = {mm: price_at(day, mod, x, mm) for mm in (m - 60, m, m + 60, m + 180)}
            for wn, a, b in (("PRE60", m - 60, m), ("POST60", m, m + 60), ("POST180", m, m + 180)):
                for k, pa in px[a].items():
                    dd = day_of(k)
                    pb = px[b].get(k)
                    if dd.weekday() >= 5 or pb is None:
                        continue
                    r_ = pb / pa - 1
                    per.setdefault(f"{sym}|{ev}|{wn}|L", {})[dd] = r_ - cost
                    per.setdefault(f"{sym}|{ev}|{wn}|S", {})[dd] = -r_ - cost
        print("V", sym, flush=True)
    cal = weekday_calendar(date(2009, 1, 1), max(max(v) for v in per.values()))
    X, names = to_matrix(per, cal)
    res = finish("V", X, None, names, cal, V_SPLIT, 2017)
    json.dump({"trade_stats": trade_stats(per, names, V_SPLIT)}, open(os.path.join(OUT, "family_v_trades.json"), "w"), indent=1)
    return res


# ---------------------------------------------------------------- family W: FX weekend-gap reversal

W_INSTR = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "XAUUSD")
W_SPLIT = date(2015, 1, 1)


def family_w():
    per, gaps_out = {}, {}
    for sym in W_INSTR:
        tape = Tape(sym, range(2003, 2027))
        cost, markup = (3.0e-4, 0.02 / 365) if sym == "XAUUSD" else (1.5e-4, 0.005 / 365)
        first = day_of(int(tape.t[0] // 1440))
        f = first + timedelta(days=(4 - first.weekday()) % 7)  # first Friday
        last = day_of(int(tape.t[-1] // 1440))
        hist = []
        while f + timedelta(days=3) <= last:
            s, mon = f + timedelta(days=2), f + timedelta(days=3)
            k_f, k_s, k_m = (x.toordinal() - EPOCH for x in (f, s, mon))
            p_fri = tape.at(k_f * 1440 + 1005)
            p_sun = tape.first_open_from(k_s * 1440 + 1140, 60)[0]  # open of the first bar from 19:00 NY Sunday (A24 data rule)
            if p_fri and p_sun:
                g = p_sun / p_fri - 1
                ready = len(hist) >= 52
                window = np.array(hist[-104:]) if ready else None
                hist.append(g)
                if ready:
                    off = 240 if gap_week(mon) else 300  # London - New York, minutes
                    ex = {"MON0800L": tape.at(k_m * 1440 + 480 - off), "MON1300L": tape.at(k_m * 1440 + 780 - off),
                          "MON1645": tape.at(k_m * 1440 + 1005), "FRI1645": tape.at((k_m + 4) * 1440 + 1005)}
                    nights = {"MON0800L": 0, "MON1300L": 0, "MON1645": 0, "FRI1645": 6}
                    for q in (0.05, 0.10, 0.20):
                        lo, hi = np.quantile(window, q), np.quantile(window, 1 - q)
                        if lo < g < hi:
                            continue
                        for how, sgn in (("FADE", -1.0), ("FOLLOW", 1.0)):
                            dr = sgn * math.copysign(1.0, g)
                            for en, p in ex.items():
                                if p:
                                    per.setdefault(f"{sym}|q{int(q * 100)}|{how}|{en}", {})[mon] = dr * (p / p_sun - 1) - cost - markup * nights[en]
            f += timedelta(days=7)
        gaps_out[sym] = {"n_weeks": len(hist), "mean_abs_gap_bps": float(np.mean(np.abs(hist)) * 1e4)}
        print("W", sym, gaps_out[sym], flush=True)
    cal = weekday_calendar(date(2003, 1, 1), max(max(v) for v in per.values()))
    X, names = to_matrix(per, cal)
    res = finish("W", X, None, names, cal, W_SPLIT, 2015)
    json.dump({"trade_stats": trade_stats(per, names, W_SPLIT), "gaps": gaps_out}, open(os.path.join(OUT, "family_w_trades.json"), "w"), indent=1)
    return res


if __name__ == "__main__":
    {"S": family_s, "T": family_t, "U": family_u, "V": family_v, "W": family_w}[sys.argv[1]]()
