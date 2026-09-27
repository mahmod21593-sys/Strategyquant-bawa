"""Post hoc: the round-19 Gotobi rule (A33 G3) as a prop book, alone and with the REV (B8w) and US100 (B9) books of
round 11. FTMO 2-Step and 1-Step presets, close-only guard as in A25, zero-edge twins. Labelled post hoc in REPORT.md.

Books (per unit of notional = 1x equity):
  GT1   USDJPY short 09:55 -> 10:55 JST on Gotobi days, 1.0 bp per trade, exact minute path
  GT7   the same on USDJPY + six JPY crosses, equal weight, 1.0 / 2.0 bps (path: mean of per-pair lows and highs)

    python3 gt_prop.py   -> results/round19_gt_prop.json
"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import numpy as np

from data_calendar import gotobi_days, japan_holidays
from data_minutes import local, price_at
from run_round11 import TOKYO

OUT = os.path.join(os.path.dirname(__file__), "results")
P_LO, P_HI = date(2014, 1, 1), date(2026, 8, 31)
ONLY = os.environ.get("GT_ONLY")  # e.g. "stop20": run only the books whose name contains it
E = date(1970, 1, 1).toordinal()
PAIRS = {"USDJPY": 1.0e-4, "EURJPY": 2.0e-4, "GBPJPY": 2.0e-4, "AUDJPY": 2.0e-4, "CADJPY": 2.0e-4, "CHFJPY": 2.0e-4, "NZDJPY": 2.0e-4}


def gt_leg(sym, cost, stop_bps=None):
    """{date: (pnl, low, high, 1.0)} for the short 09:55 -> 10:55 JST on Gotobi days (at 1x notional); optional buy
    stop at entry + stop_bps (A34 GS), filled at max(stop, bar open)."""
    got, hol = gotobi_days(), japan_holidays()
    t, x = local(sym, range(2013, 2027), TOKYO)
    day, mod = t // 1440, t % 1440
    p0, p1 = price_at(day, mod, x, 595), price_at(day, mod, x, 655)
    ins = (mod >= 595) & (mod < 655)
    dk, xi = day[ins], x[ins]
    st = np.r_[0, np.nonzero(np.diff(dk))[0] + 1]
    hi = dict(zip(dk[st].tolist(), np.maximum.reduceat(xi[:, 1], st).tolist()))
    lo = dict(zip(dk[st].tolist(), np.minimum.reduceat(xi[:, 2], st).tolist()))
    en = np.r_[st[1:], len(dk)]
    rng = {int(dk[i]): (i, j) for i, j in zip(st, en)}
    out = {}
    for k, a in p0.items():
        d = date.fromordinal(int(k) + E)
        if d not in got or d in hol or d.weekday() >= 5 or not (P_LO <= d <= P_HI) or k not in p1 or k not in hi:
            continue
        exit_px, high = p1[k], hi[k]
        if stop_bps is not None:
            s_ = a * (1 + stop_bps / 1e4)
            i, j = rng[k]
            hit = np.nonzero(xi[i:j, 1] >= s_)[0]
            if len(hit):
                exit_px = max(s_, xi[i + hit[0], 0])
                high = exit_px
        out[d] = (a / exit_px - 1 - cost, a / high - 1 - cost, a / lo[k] - 1 - cost, 1.0)
    return out


def stats(book, label):
    x = np.array([v[0] for v in book.values()])
    n_years = (P_HI - P_LO).days / 365.25
    return {"label": label, "trades": int(len(x)), "trades_per_year": float(len(x) / n_years), "mean_bps": float(x.mean() * 1e4),
            "sd_bps": float(x.std(ddof=1) * 1e4), "sharpe_annual": float(x.mean() / x.std(ddof=1) * math.sqrt(len(x) / n_years)),
            "worst_trade_bps": float(min(v[1] for v in book.values()) * 1e4)}


def main():
    from prop_lifecycle import demean, evaluate, to_days
    from run_round4 import irx_map
    from run_round11 import add_books, n3_native_book, rev_leg, scaled
    rates = irx_map()
    keys = sorted(rates)
    legs = {s: gt_leg(s, c) for s, c in PAIRS.items()}
    common = sorted(set.intersection(*[set(v) for v in legs.values()]))
    gt1 = legs["USDJPY"]
    gt7 = {d: tuple(float(np.mean([legs[s][d][i] for s in PAIRS])) for i in range(3)) + (1.0,) for d in common}
    print("GT legs", {s: len(v) for s, v in legs.items()}, "common", len(common), flush=True)
    b8w = scaled(add_books([scaled(rev_leg(s, rates, keys, True))[0] for s in ("SPXUSD", "NSXUSD", "JPXJPY")]))[0]
    b9 = scaled(n3_native_book())[0]
    print("REV and N3 books", flush=True)
    res = {"stats": {"GT1": stats(gt1, "USDJPY"), "GT7": stats(gt7, "7 JPY pairs")}, "lifecycle": {}}
    x1 = np.array([gt1.get(d, (0.0,))[0] for d in sorted(b8w)])
    res["corr_GT1_with_REV"] = float(np.corrcoef(x1, [b8w[d][0] for d in sorted(b8w)])[0, 1])
    res["corr_GT1_with_N3"] = float(np.corrcoef([gt1.get(d, (0.0,))[0] for d in sorted(b9)], [b9[d][0] for d in sorted(b9)])[0, 1])
    print(json.dumps(res, indent=1), flush=True)

    cal = [d for d in b8w if P_LO <= d <= P_HI and d.weekday() < 5]

    def times(book, n):
        """n x notional on every weekday of the REV calendar (0 on days without a trade)."""
        z = (0.0, 0.0, 0.0, 0.0)
        return {d: tuple(n * q for q in book.get(d, z)) for d in cal}
    books = {f"GT1 at {n}x notional": times(gt1, n) for n in (5, 10, 20, 30)}
    books.update({f"GT7 at {n}x notional": times(gt7, n) for n in (10, 20, 30)})
    # round 20 (A34): the 20-bps disaster stop, and EURJPY at <= 1 bp allowed to join (C3)
    gs1 = gt_leg("USDJPY", 1.0e-4, 20)
    ge1 = gt_leg("EURJPY", 1.0e-4, 20)
    gs2 = {d: tuple(0.5 * (gs1[d][i] + ge1[d][i]) for i in range(3)) + (1.0,) for d in gs1 if d in ge1}
    res["stats"]["GT1_stop20"] = stats(gs1, "USDJPY, 20-bps stop")
    res["stats"]["GT2_stop20"] = stats(gs2, "USDJPY + EURJPY at 1 bp, 20-bps stop")
    books.update({f"GT1 stop20 at {n}x notional": times(gs1, n) for n in (10, 20, 30, 40)})
    books.update({f"GT2 stop20 at {n}x notional": times(gs2, n) for n in (20, 30, 40)})
    books["REV+N3 (B10 parts, 1x each)"] = add_books([b8w, b9])
    for n in (5, 10, 20):
        books[f"REV+N3+GT1 at {n}x"] = add_books([b8w, b9, times(gt1, n)])
    books = {k: v for k, v in books.items() if ONLY is None or ONLY in k}
    for name, book in books.items():
        bk = {d: v[:3] for d, v in book.items() if d.weekday() < 5}
        real, zero = to_days(bk), to_days(demean(bk))
        cell = {}
        for preset, guard, lab in (("ftmo_2step_100k.json", 0.03, "FTMO 2-Step"), ("ftmo_1step_100k.json", 0.02, "FTMO 1-Step")):
            a = evaluate(real, preset, guard, 1.0, None)
            z = evaluate(zero, preset, guard, 1.0, None)
            cell[lab] = {"p_pass": a["p_pass"], "zero_edge_p_pass": z["p_pass"], "median_days_to_pass": a["median_days_to_pass"],
                         "ev_per_account_month_usd": a["ev_per_account_month_usd"], "edge_value_usd": a["ev_per_attempt_usd"] - z["ev_per_attempt_usd"],
                         "mean_months": a["mean_months"]}
        x = np.array([v[0] for d, v in sorted(book.items()) if d.weekday() < 5])
        cell["ann_return_pct"] = float(x.mean() * 252 * 100)
        cell["ann_vol_pct"] = float(x.std(ddof=1) * math.sqrt(252) * 100)
        cell["worst_intraday_pct"] = float(min(v[1] for v in book.values()) * 100)
        res["lifecycle"][name] = cell
        print(name, json.dumps(cell), flush=True)
        json.dump(res, open(os.path.join(OUT, f"round19_gt_prop{'_' + ONLY if ONLY else ''}.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
