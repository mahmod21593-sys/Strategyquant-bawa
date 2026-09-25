"""Can the surviving edges be traded? Financing, CFD swap, spreads, drawdown, prop-challenge odds.

Post-validation analysis (not a pre-registered test). Uses the same Yahoo data.
Edges: E06 (next day after >= 3 down closes, S&P 500), P18 (pre-holiday, S&P 500), P17 (overnight premium, SPY).
"""
import json
import math
import os
import random
import sys
from datetime import date

import vstats as vs
from data_yahoo import daily

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools", "propsim"))
from propsim.engine import Day, run_challenge  # noqa: E402
from propsim.rules import load_rules  # noqa: E402
from propsim.sampling import stationary_bootstrap  # noqa: E402

R = os.path.join(os.path.dirname(__file__), "results")
BPS = 1e4
SPREAD_BPS = 0.75       # US500 CFD round-trip spread (~0.5 pt at ~6,600)
SWAP_MARKUP = 0.025     # CFD long financing = cash rate + 2.5% per year, charged per night (act/360)


def rate_map():
    return {r["date"]: r["c"] / 100 for r in daily("^IRX")}


def nearest(m, d, keys):
    import bisect
    i = bisect.bisect_right(keys, d) - 1
    return m[keys[max(i, 0)]]


def trades(start=date(1990, 1, 1)):
    spx = [r for r in daily("^GSPC") if r["date"] >= start]
    spy = [r for r in daily("SPY") if r["date"] >= date(1993, 2, 1)]
    out = {"E06": [], "P18": [], "P17": []}
    rets = [None] + [b["c"] / a["c"] - 1 for a, b in zip(spx, spx[1:])]
    for i in range(4, len(spx)):
        if rets[i - 1] < 0 and rets[i - 2] < 0 and rets[i - 3] < 0:
            d = spx[i]
            out["E06"].append({"date": d["date"], "ret": rets[i], "low": d["l"] / spx[i - 1]["c"] - 1,
                               "high": d["h"] / spx[i - 1]["c"] - 1, "nights": (d["date"] - spx[i - 1]["date"]).days})
    for a, b, c in zip(spx, spx[1:], spx[2:]):
        normal = 3 if b["date"].weekday() == 4 else 1
        if (c["date"] - b["date"]).days > normal:
            out["P18"].append({"date": b["date"], "ret": b["c"] / a["c"] - 1, "low": b["l"] / a["c"] - 1,
                               "high": b["h"] / a["c"] - 1, "nights": (b["date"] - a["date"]).days})
    for a, b in zip(spy, spy[1:]):
        g = b["o"] / a["c"] - 1
        out["P17"].append({"date": b["date"], "ret": g, "low": min(0.0, g), "high": max(0.0, g), "nights": (b["date"] - a["date"]).days})
    return out


def max_dd(pnl_frac):
    eq = peak = 1.0
    mdd = 0.0
    for x in pnl_frac:
        eq *= 1 + x
        peak = max(peak, eq)
        mdd = min(mdd, eq / peak - 1)
    return mdd


def main():
    rates = rate_map()
    rk = sorted(rates)
    tr = trades()
    table = {}
    for k, rows in tr.items():
        for scen in ("gross", "futures_or_cash_net", "cfd_net"):
            vals, ds = [], []
            for r in rows:
                if r["date"] < date(1994, 1, 1):
                    continue
                rf = nearest(rates, r["date"], rk)
                x = r["ret"]
                if scen == "futures_or_cash_net":
                    x -= 1.5 / BPS + rf * r["nights"] / 360          # pre-registered 1.5 bps + financing
                elif scen == "cfd_net":
                    x -= SPREAD_BPS / BPS + (rf + SWAP_MARKUP) * r["nights"] / 360
                vals.append(x * BPS)
                ds.append(r["date"])
            yrs = (ds[-1] - ds[0]).days / 365.25
            per_year = len(vals) / yrs
            sd_ = vs.sd(vals)
            table[f"{k}:{scen}"] = {
                "n": len(vals), "trades_per_year": per_year, "mean_bps": vs.mean(vals), "t": vs.nw_t(vals, 5),
                "ann_return_pct_1x": vs.mean(vals) * per_year / 100, "sharpe_1x": vs.mean(vals) / sd_ * math.sqrt(per_year),
                "max_dd_pct_1x": max_dd([v / BPS for v in vals]) * 100,
                "post2013_mean_bps": vs.mean([v for d, v in zip(ds, vals) if d >= date(2013, 1, 1)]),
            }
    # prop challenge: combined daily book (E06 + P18 on US500 CFD, P17 on US500 CFD), CFD-net, 2013+
    prop_all = {}
    for book_name, edges in (("E06+P18", ("E06", "P18")), ("E06+P18+P17", ("E06", "P18", "P17"))):
        prop_all[book_name] = prop_for(tr, rates, rk, edges)
    json.dump({"edges": table, "prop_two_step_10_5_bootstrap_cfd_2013_on": prop_all},
              open(os.path.join(R, "implementability.json"), "w"), indent=2, default=str)
    for k, v in table.items():
        print(f"{k:28s} n={v['n']:5d} /yr={v['trades_per_year']:5.1f} mean={v['mean_bps']:6.2f} t={v['t']:5.2f} "
              f"ann={v['ann_return_pct_1x']:5.2f}% sharpe={v['sharpe_1x']:5.2f} mdd={v['max_dd_pct_1x']:6.1f}% post13={v['post2013_mean_bps']:6.2f}")
    for b, v in prop_all.items():
        print("book", b, v["book"])
        for k, x in v["prop"].items():
            print("   prop", k, x)


def prop_for(tr, rates, rk, edges):
    book = {}
    for k in edges:
        for r in tr[k]:
            if r["date"] < date(2013, 1, 1):
                continue
            rf = nearest(rates, r["date"], rk)
            cost = SPREAD_BPS / BPS + (rf + SWAP_MARKUP) * r["nights"] / 360
            b = book.setdefault(r["date"], [0.0, 0.0, 0.0])
            b[0] += r["ret"] - cost
            b[1] += min(r["low"], 0.0) - cost
            b[2] += max(r["high"], 0.0)
    # include flat weekdays so calendar time (days to pass) is realistic
    from datetime import timedelta
    d0, d1 = min(book), max(book)
    days, d = [], d0
    while d <= d1:
        if d.weekday() < 5:
            days.append(Day(d, *book[d], traded=True, n_trades=1) if d in book else Day(d))
        d += timedelta(days=1)
    rules = load_rules(os.path.join(os.path.dirname(__file__), "..", "..", "tools", "propsim", "presets", "two_step_10_5.json"))
    rules.funded = None
    prop = {}
    for lev in (2, 4, 6, 8):
        rng = random.Random(7)
        outs = [run_challenge(stationary_bootstrap(days, rng, 5.0, 2520), rules, float(lev), daily_guard=0.03, guard_slippage=0.0025)
                for _ in range(1500)]
        dec = [o for o in outs if o.decided]
        passed = sorted(o.days_to_pass for o in dec if o.passed_all)
        prop[f"{lev}x"] = {"p_pass_all": len(passed) / len(dec) if dec else None,
                           "median_days": passed[len(passed) // 2] if passed else None,
                           "fail_daily": sum(o.fail_reason == "daily_loss" for o in dec) / len(dec),
                           "fail_max": sum(o.fail_reason == "max_loss" for o in dec) / len(dec)}
    pnl = [d.pnl for d in days if d.traded]
    book_stats = {"trade_days": len(pnl), "days_per_year": len(pnl) / ((days[-1].date - days[0].date).days / 365.25),
                  "mean_bps_per_trade_day": vs.mean(pnl) * BPS, "t": vs.nw_t([x * BPS for x in pnl], 5)}
    return {"book": book_stats, "prop": prop}


if __name__ == "__main__":
    main()
