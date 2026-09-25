"""Post-hoc implementability: prop-challenge pass rates for MR-06 with the realistic 15:55 entry (R7 rule) on
HistData US500 + US100, 2014-2025. Raw (not excess) returns, net of 1.5 bps and one night of CFD swap
(T-bill + 2.5%/yr). Intraday path: worst/best price from entry to exit using RTH minute bars. -> results/prop_mr06_minute.json
"""
import json
import os
import random
import sys
from datetime import timedelta

import vstats as vs
from data_histdata import price, table
from implementability import SWAP_MARKUP, nearest, rate_map
from run_histdata import RTH, us_days

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools", "propsim"))
from propsim.engine import Day, run_challenge  # noqa: E402
from propsim.rules import load_rules  # noqa: E402
from propsim.sampling import stationary_bootstrap  # noqa: E402

R = os.path.join(os.path.dirname(__file__), "results")
COST = 1.5e-4


def trades(sym, rates, rk):
    tab = table(sym, range(2014, 2026), RTH)
    days = us_days(tab)
    close = {d: price(tab, d, 960) for d in days}
    out = {}
    for i in range(3, len(days) - 1):
        d, n = days[i], days[i + 1]
        c1, c2, c3, nx, p = close[days[i - 1]], close[days[i - 2]], close[days[i - 3]], close[n], price(tab, d, 955)
        if None in (c1, c2, c3, nx, p) or not (p < c1 < c2 < c3):
            continue
        bars = [b for m, b in sorted(tab[n].items()) if m < 960] + [b for m, b in sorted(tab[d].items()) if 955 <= m < 960]
        lo, hi = min(b[2] for b in bars) / p - 1, max(b[1] for b in bars) / p - 1
        rf = nearest(rates, n, rk)
        nights = (n - d).days
        cost = COST + (rf + SWAP_MARKUP) * nights / 360
        out[n] = (nx / p - 1 - cost, min(lo, 0.0) - cost, max(hi, 0.0))
    return out


def main():
    rates = rate_map()
    rk = sorted(rates)
    allper = {s: trades(s, rates, rk) for s in ("SPXUSD", "NSXUSD")}
    res = {name: simulate({s: allper[s] for s in syms}) for name, syms in (("US500+US100", ("SPXUSD", "NSXUSD")), ("US500 only", ("SPXUSD",)))}
    # diagnostic: how much the intraday path and the EA guard matter (US500, 2x)
    sp = allper["SPXUSD"]
    diag = {}
    for label, f in (("close_only_path", lambda v: (v[0], min(v[0], 0.0), max(v[0], 0.0))), ("intraday_path", lambda v: v)):
        for guard in (0.03, None):
            diag[f"{label}_guard_{guard}"] = simulate({"SPXUSD": {d: f(v) for d, v in sp.items()}}, levs=(2,), guard=guard)["prop_two_step_10_5"]["2x"]
    lows = [v[1] for v in sp.values()]
    diag["mean_adverse_excursion_bps_1x"] = vs.mean(lows) * 1e4
    diag["sd_trade_bps_1x"] = vs.sd([v[0] for v in sp.values()]) * 1e4
    res["US500 path and guard diagnostic (2x)"] = diag
    json.dump(res, open(os.path.join(R, "prop_mr06_minute.json"), "w"), indent=2, default=str)
    for name, r in res.items():
        print(name, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items() if k != "prop_two_step_10_5"})
        for lev, x in r.get("prop_two_step_10_5", {}).items():
            print("   ", lev, x)


def simulate(per, levs=(2, 4, 6, 8), guard=0.03):
    book = {}
    for s, tr in per.items():
        for d, v in tr.items():
            book.setdefault(d, []).append(v)
    agg = {d: tuple(sum(x[i] for x in v) / len(v) for i in range(3)) for d, v in book.items()}
    d0, d1 = min(agg), max(agg)
    days, d = [], d0
    while d <= d1:
        if d.weekday() < 5:
            days.append(Day(d, *agg[d], traded=True, n_trades=1) if d in agg else Day(d))
        d += timedelta(days=1)
    rules = load_rules(os.path.join(os.path.dirname(__file__), "..", "..", "tools", "propsim", "presets", "two_step_10_5.json"))
    rules.funded = None
    prop = {}
    for lev in levs:
        rng = random.Random(7)
        outs = [run_challenge(stationary_bootstrap(days, rng, 5.0, 2520), rules, float(lev), daily_guard=guard, guard_slippage=0.0025)
                for _ in range(1500)]
        dec = [o for o in outs if o.decided]
        passed = sorted(o.days_to_pass for o in dec if o.passed_all)
        prop[f"{lev}x"] = {"p_pass_all": len(passed) / len(dec) if dec else None,
                           "median_days": passed[len(passed) // 2] if passed else None,
                           "fail_daily": sum(o.fail_reason == "daily_loss" for o in dec) / len(dec),
                           "fail_max": sum(o.fail_reason == "max_loss" for o in dec) / len(dec)}
    pnl = [agg[k][0] * 1e4 for k in sorted(agg)]
    return {"trade_days": len(pnl), "per_year": len(pnl) / ((d1 - d0).days / 365.25), "mean_net_raw_bps": vs.mean(pnl),
            "t": vs.nw_t(pnl, 5), "per_symbol_n": {s: len(v) for s, v in per.items()}, "prop_two_step_10_5": prop}


if __name__ == "__main__":
    main()
