"""Round 9, post hoc: the family-A reversal ensemble as a prop book.

Every variant on an instrument is weighted by 1 / its discovery volatility (data before 2013 only). Because all
variants on the same index share one price path, the book's net exposure per index and its intraday low are exact
per index; lows are summed across indices (conservative). Bootstrapped from the validation years 2013-2026.
-> results/prop_ensemble.json
"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import numpy as np

from prop_lifecycle import demean, evaluate, to_days
from run_family_a import COST, EXITS, FILTERS, MARKUP, SIGNALS, SPLIT, US, load, positions, signals
from run_round4 import irx_map, tbill

OUT = os.path.join(os.path.dirname(__file__), "results")
TARGET_DAILY_VOL = 0.01  # book scaled to 1% daily volatility at 1x (discovery estimate)


def instrument_book(sym, rates, keys):
    d, c, h, l, craw, ret, rf = load(sym, rates, keys)
    sig, filt = signals(c, h, l, craw, ret)
    disc = np.array([x < SPLIT for x in d])
    f = c / craw
    lowr = np.zeros(len(c))
    highr = np.zeros(len(c))
    lowr[1:] = l[1:] * f[1:] / c[:-1] - 1
    highr[1:] = h[1:] * f[1:] / c[:-1] - 1
    mark = MARKUP if sym in US else 0.0
    expo, cost = np.zeros(len(c)), np.zeros(len(c))
    for sn in SIGNALS:
        for ex in EXITS:
            for fn in FILTERS:
                pos, entry = positions(sig[sn], filt[fn], c, ex)
                pnl = pos * (ret - rf) - pos * mark - entry * COST
                sd = pnl[disc].std()
                if sd <= 0:
                    continue
                w = 1 / sd
                expo += w * pos
                cost += w * (pos * mark + entry * COST)
    return d, expo, cost, ret - rf, np.minimum(lowr, 0), np.maximum(highr, 0)


def main():
    rates = irx_map()
    keys = sorted(rates)
    res = {}
    for label, insts in (("US_4_indices", US), ("US_plus_JP225", US + ("^N225",))):
        parts = {s: instrument_book(s, rates, keys) for s in insts}
        # normalise so each index gets equal risk, then scale the book to 1% daily vol on discovery data
        daily = {}
        for s, (d, expo, cost, exr, lo, hi) in parts.items():
            pnl = expo * exr - cost
            disc = np.array([x < SPLIT for x in d])
            k = 1 / pnl[disc].std()
            for i, x in enumerate(d):
                a = daily.get(x, [0.0, 0.0, 0.0])
                a[0] += k * pnl[i]
                a[1] += k * (expo[i] * lo[i] - cost[i])
                a[2] += k * expo[i] * hi[i]
                daily[x] = a
        disc_pnl = np.array([v[0] for x, v in sorted(daily.items()) if x < SPLIT])
        scale = TARGET_DAILY_VOL / disc_pnl.std()
        book = {x: (scale * v[0], scale * v[1], scale * v[2]) for x, v in daily.items() if x >= SPLIT and x.weekday() < 5}
        x = np.array([v[0] for v in book.values()])
        res[label] = {"validation_days": len(x), "validation_sharpe": float(x.mean() / x.std() * math.sqrt(252)),
                      "ann_vol_pct_at_1x": float(x.std() * math.sqrt(252) * 100), "ann_return_pct_at_1x": float(x.mean() * 252 * 100),
                      "mean_low_minus_close_bps": float(np.mean([v[1] - v[0] for v in book.values()]) * 1e4)}
        print(label, res[label], flush=True)
        real, zero = to_days(book), to_days(demean(book))
        for preset, guard in (("ftmo_2step_100k.json", 0.03), ("ftmo_1step_100k.json", 0.02)):
            cells = {}
            pols = {f"fixed {L:g}x": (L, None) for L in (0.5, 1, 1.5, 2, 3)}
            for k in (10, 20):
                pols[f"CPPI k={k} cap=3x"] = (1.0, (lambda a, k=k: max(0.0, min(3.0, k * a.cushion()))))
            for pol, (sc, sz) in pols.items():
                a = evaluate(real, preset, guard, sc, sz)
                z = evaluate(zero, preset, guard, sc, sz)
                a["zero_edge_ev_per_attempt_usd"], a["zero_edge_p_pass"] = z["ev_per_attempt_usd"], z["p_pass"]
                a["edge_value_usd"] = a["ev_per_attempt_usd"] - z["ev_per_attempt_usd"]
                cells[pol] = a
                print(label, preset, pol, {kk: round(float(v), 3) for kk, v in a.items() if kk in ("p_pass", "zero_edge_p_pass", "ev_per_attempt_usd",
                                                                                                "edge_value_usd", "mean_months", "ev_per_account_month_usd")}, flush=True)
            res[label][preset] = cells
    json.dump(res, open(os.path.join(OUT, "prop_ensemble.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
