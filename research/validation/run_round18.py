"""Round 18 (PREREGISTRATION.md A32).

    python3 run_round18.py JY    USDJPY intraday-momentum confirmation (USDJPY 2003-09, six JPY crosses) -> results/round18_jy.json
    python3 run_round18.py VS    volatility-scaled reversal book vs fixed size, FTMO lifecycle            -> results/round18_vs.json
    python3 run_round18.py RBC   RB signals in the SQX M5/15:55 build                                    -> results/round18_rbc.json
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date

import numpy as np

import multitest as mt
import run_family_a as fa
import vstats as vs
from data_histdata import available_years, local_table
from data_minutes import group, local, price_at, day_of
from data_yahoo import daily
from run_noise_area import run as noise_run
from run_round4 import irx_map
from run_round11 import LONDON, R1_END, R1_MARKETS, R1_START, R_RANGES, bracket_exit, session_bars
from run_round17 import rb_signals, xs5_positions

OUT = os.path.join(os.path.dirname(__file__), "results")
R9 = os.environ.get("ROUND9_DIR", "/tmp/round9")
fa.N_TRIALS = 13669
CROSSES = ("EURJPY", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY", "NZDJPY")


# ---------------------------------------------------------------- JY

def range_rules(sym, years, cost):
    """Family R's 8 rules for one symbol (A24), {name: {date: pnl}}."""
    t, x = local(sym, years, LONDON)
    day, mod = t // 1440, t % 1440
    per = {}
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
            bo, bh, bl = bars[:, 0], bars[:, 1], bars[:, 2]
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
                    if (pos == 1 and bl[j] <= sl) or (pos == -1 and bh[j] >= sl):
                        out_px = sl
                    else:
                        out_px = bracket_exit(bars[j + 1:], pos, sl, px + pos * R_ if ex == "TGT" else None, p_end[k])
                    per.setdefault(f"{rn}|{rule}|{ex}", {})[d] = pos * (out_px / px - 1) - cost
    return per


def noise_rules(sym, years, cost_bps):
    ses = local_table(sym, available_years(sym, years), LONDON, set(range(479, 1231)))
    out = {}
    for L in (7, 14, 28):
        for bnd in (1.0, 1.25):
            spec = (sym, LONDON, (8, 0), (20, 30), (8, 30), (20, 0), cost_bps, "flip")
            rows, _, _ = noise_run("JY", lookback=L, grid=30, spec=spec, ses=ses, band=bnd)
            out[f"NOISE_L{L}_b{bnd:g}"] = {d: v / 1e4 for d, v in rows}
    return out


def mean_test(rows):
    x = np.array([v for _, v in sorted(rows.items())])
    t = vs.nw_t(list(x), 5)
    return {"n": int(len(x)), "mean_bps": float(x.mean() * 1e4), "t_hac": t, "p_one_sided": vs.p_one_sided(t),
            "sharpe_per_trade_annualised": float(x.mean() / x.std(ddof=1) * math.sqrt(252))}


def grid_battery(per):
    names = sorted(per)
    days = sorted({d for v in per.values() for d in v})
    X = np.array([[per[n].get(d, 0.0) for n in names] for d in days])
    s = mt.spa(X, 10, 2000)
    sr = mt.sharpe(X, 252)
    return {"p_spa": s["p_spa"], "best": names[s["best_index"]], "share_positive": float((sr > 0).mean()),
            "sharpe": {n: float(v) for n, v in zip(names, sr)}}


def family_jy():
    res = {}
    uj = range_rules("USDJPY", range(2003, 2010), 1.0e-4)
    uj.update(noise_rules("USDJPY", range(2003, 2010), 1.0))
    uj = {k: {d: v for d, v in rows.items() if date(2003, 1, 1) <= d <= date(2009, 12, 31)} for k, rows in uj.items()}
    print("USDJPY 2003-09 done", flush=True)
    cr = {}
    for sym in CROSSES:
        p = range_rules(sym, range(2008, 2027), 2.0e-4)
        p.update(noise_rules(sym, range(2008, 2027), 2.0))
        cr[sym] = p
        print("cross", sym, flush=True)
    avg = {}
    for rule in cr[CROSSES[0]]:
        days = sorted({d for s in CROSSES for d in cr[s][rule]})
        avg[rule] = {d: float(np.mean([cr[s][rule][d] for s in CROSSES if d in cr[s][rule]])) for d in days}
    prim = {"H1": mean_test(uj["LDNAM|BRK|END"]), "H2": mean_test(uj["NOISE_L14_b1.25"]),
            "H3": mean_test(avg["LDNAM|BRK|END"]), "H4": mean_test(avg["NOISE_L14_b1.25"])}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    h12 = [k for k in ("H1", "H2") if prim[k]["p_holm"] < 0.05]
    h34 = any(prim[k]["mean_bps"] > 0 for k in ("H3", "H4"))
    verdict = "CONFIRMED EDGE" if h12 and h34 else "WEAK" if any(v["p_holm"] < 0.05 for v in prim.values()) else "NOT CONFIRMED"
    res["primary"] = prim
    res["verdict"] = verdict
    res["secondary_usdjpy_2003_2009"] = grid_battery(uj)
    res["secondary_crosses_avg"] = grid_battery(avg)
    res["per_cross"] = {s: {r: mean_test(cr[s][r]) for r in ("LDNAM|BRK|END", "NOISE_L14_b1.25")} for s in CROSSES}
    res["per_year_usdjpy"] = {r: {y: float(np.mean([v for d, v in uj[r].items() if d.year == y]) * 1e4) for y in range(2003, 2010)}
                              for r in ("LDNAM|BRK|END", "NOISE_L14_b1.25")}
    json.dump(res, open(os.path.join(OUT, "round18_jy.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "verdict")}, indent=1, default=str))
    print("secondary USDJPY", {k: v for k, v in res["secondary_usdjpy_2003_2009"].items() if k != "sharpe"})
    print("secondary crosses", {k: v for k, v in res["secondary_crosses_avg"].items() if k != "sharpe"})
    print(json.dumps(res["per_cross"], indent=0, default=str)[:3000])


# ---------------------------------------------------------------- VS

VS_START, VS_SCALE_END = date(2007, 7, 1), date(2012, 12, 31)


def family_vs():
    from prop_lifecycle import demean, evaluate, to_days
    rates = irx_map()
    keys = sorted(rates)
    cal = sorted({r["date"] for s in fa.US for r in daily(s) if VS_START <= r["date"] <= fa.END and r["date"].weekday() < 5})
    ci = {x: i for i, x in enumerate(cal)}
    books = {"fixed": [], "volscaled": []}
    for sym in fa.US:
        d, c, h, l, craw, ret, rf = fa.load(sym, rates, keys)
        ex = ret - rf
        sd20 = np.full(len(c), np.nan)
        for i in range(20, len(c)):
            sd20[i] = ret[i - 19:i + 1].std(ddof=1)
        keep = np.array([VS_START <= x and x in ci for x in d])
        idx = np.array([ci[x] for x, k in zip(d, keep) if k])
        sigA, filtA = fa.signals(c, h, l, craw, ret)
        ha, la = h * c / craw, l * c / craw
        sigB, filtB, sma5 = rb_signals(c, ha, la, craw, h, l)
        variants = [(sigA[s], filtA[f], e, None) for s in fa.SIGNALS for e in fa.EXITS for f in fa.FILTERS] + \
                   [(sigB[s], filtB[f], e, sma5) for s in sigB for e in ("X1", "XU", "XS5") for f in ("F0", "UP", "DN")]
        for sg, fl, e, s5 in variants:
            pos, entry = xs5_positions(sg, fl, c, s5) if e == "XS5" else fa.positions(sg, fl, c, e)
            # scale fixed at the entry signal close
            scale = np.zeros(len(c))
            cur = 1.0
            for i in range(len(c)):
                if entry[i]:
                    v = sd20[i - 1]
                    cur = min(2.0, 0.01 / v) if np.isfinite(v) and v > 0 else 1.0
                scale[i] = cur if pos[i] else 0.0
            for lab, ps in (("fixed", pos), ("volscaled", pos * scale)):
                pnl = ps * ex - ps * fa.MARKUP - entry * fa.COST * (scale if lab == "volscaled" else 1.0)
                col = np.zeros(len(cal))
                col[idx] = pnl[keep]
                books[lab].append(col)
        print("VS", sym, flush=True)
    early = np.array([x <= VS_SCALE_END for x in cal])
    res = {}
    for lab, cols in books.items():
        M = np.array(cols).T
        sd = M[early].std(0, ddof=1)
        w = np.where(sd > 0, 1 / np.where(sd > 0, sd, 1), 0)
        e = M @ (w / w.sum())
        e = e * (0.01 / e[early].std(ddof=1))
        eq = np.cumsum(e)
        res[lab] = {"sharpe": float(mt.sharpe(e[:, None], 252)[0]), "ann_return_pct": float(e.mean() * 252 * 100),
                    "ann_vol_pct": float(e.std(ddof=1) * math.sqrt(252) * 100), "worst_day_pct": float(e.min() * 100),
                    "max_drawdown_pct": float((eq - np.maximum.accumulate(eq)).min() * 100),
                    "sharpe_2017_2026": float(mt.sharpe(e[[x >= date(2017, 1, 1) for x in cal]][:, None], 252)[0])}
        book = {x: (float(v), min(0.0, float(v)), max(0.0, float(v))) for x, v in zip(cal, e)}
        real, zero = to_days(book), to_days(demean(book))
        for pol, (sc, sz) in {"fixed 1x": (1.0, None), "CPPI k=10 cap=3x": (1.0, (lambda a: max(0.0, min(3.0, 10 * a.cushion()))))}.items():
            a = evaluate(real, "ftmo_2step_100k.json", 0.03, sc, sz)
            z = evaluate(zero, "ftmo_2step_100k.json", 0.03, sc, sz)
            res[lab][pol] = {"p_pass": a["p_pass"], "zero_edge_p_pass": z["p_pass"], "ev_per_account_month_usd": a["ev_per_account_month_usd"],
                             "edge_value_usd": a["ev_per_attempt_usd"] - z["ev_per_attempt_usd"], "mean_months": a["mean_months"]}
        print(lab, json.dumps(res[lab]), flush=True)
    f, v = res["fixed"], res["volscaled"]
    res["recommend_volscaling"] = bool(v["worst_day_pct"] > f["worst_day_pct"] and v["sharpe"] >= 0.8 * f["sharpe"]
                                       and (v["fixed 1x"]["p_pass"] - v["fixed 1x"]["zero_edge_p_pass"]) >= (f["fixed 1x"]["p_pass"] - f["fixed 1x"]["zero_edge_p_pass"]))
    json.dump(res, open(os.path.join(OUT, "round18_vs.json"), "w"), indent=1)
    print("recommend vol-scaling:", res["recommend_volscaling"])


# ---------------------------------------------------------------- RBC

def family_rbc():
    from run_round4 import tbill
    rates = irx_map()
    keys = sorted(rates)
    res = {}
    for sym, twin in (("SPXUSD", "SPY"), ("NSXUSD", "QQQ"), ("JPXJPY", "^N225")):
        name, tz, op, close_of, cost, mark, _ = R1_MARKETS[sym]
        d, so, sh, sl, sc, sm, mh, ml = session_bars(sym)
        n = len(d)
        # the 15:55 snapshot as the daily bar (disclosed approximation: earlier days' closes also at 15:55)
        sig, filt, sma5 = rb_signals(sm, mh, ml, sm, mh, ml)
        fwd = np.r_[0.0, sm[1:] / sm[:-1] - 1]
        rf = np.array([0.0] + [tbill(rates, keys, d[i - 1], d[i]) for i in range(1, n)])
        ex = fwd - rf
        yr = np.array([x.year for x in d])
        ymu = {y: float(ex[yr == y].mean()) for y in set(yr.tolist())}
        mu = np.array([ymu[y] for y in yr])
        win = np.array([R1_START <= x <= R1_END for x in d])
        cols = []
        for s in sig:
            for e in ("X1", "XU", "XS5"):
                for f in ("F0", "UP", "DN"):
                    pos, entry = xs5_positions(sig[s], filt[f], sm, sma5) if e == "XS5" else fa.positions(sig[s], filt[f], sm, e)
                    tv = pos * ex - pos * mark - entry * cost - pos * mu
                    cols.append(tv[win])
        M = np.array(cols).T
        sr = mt.sharpe(M, 252)
        sd = M.std(0, ddof=1)
        w = np.where(sd > 0, 1 / np.where(sd > 0, sd, 1), 0)
        ens = M @ (w / w.sum())
        # the daily-close RB result on the same window
        p = np.load(os.path.join(R9, "family_rb.npz"))
        rcal = [date.fromordinal(int(v)) for v in p["dates"]]
        rcols = [str(c) for c in p["cols"]]
        k = [i for i, cn in enumerate(rcols) if cn.startswith(twin + "|")]
        rwin = np.array([R1_START <= x <= R1_END for x in rcal])
        R = p["XA"][rwin][:, k]
        rsr = mt.sharpe(R, 252)
        rsd = R.std(0, ddof=1)
        rw = np.where(rsd > 0, 1 / np.where(rsd > 0, rsd, 1), 0)
        rens = R @ (rw / rw.sum())
        res[name] = {"sqx_build": {"median_sharpe_timing": float(np.median(sr)), "share_positive": float((sr > 0).mean()),
                                   "ensemble_sharpe_timing": float(mt.sharpe(ens[:, None], 252)[0]), "spa": mt.spa(M, 10, 2000)["p_spa"]},
                     "daily_close": {"median_sharpe_timing": float(np.median(rsr)), "share_positive": float((rsr > 0).mean()),
                                     "ensemble_sharpe_timing": float(mt.sharpe(rens[:, None], 252)[0])}}
        res[name]["kept_share_of_ensemble_sharpe"] = res[name]["sqx_build"]["ensemble_sharpe_timing"] / res[name]["daily_close"]["ensemble_sharpe_timing"]
        print(name, json.dumps(res[name]), flush=True)
    json.dump(res, open(os.path.join(OUT, "round18_rbc.json"), "w"), indent=1)


if __name__ == "__main__":
    {"JY": family_jy, "VS": family_vs, "RBC": family_rbc}[sys.argv[1]]()
