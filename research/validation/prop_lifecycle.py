"""Round 6 (PREREGISTRATION.md A12): prop lifecycle decision analysis.

Challenge + funded stage, fixed vs CPPI sizing, each book against its zero-edge twin.
-> results/prop_lifecycle.json
"""
from __future__ import annotations

import json
import os
import random
import sys
from datetime import date, timedelta

import vstats as vs
from round4_followup import mr06_days
from run_noise_area import run

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools", "propsim"))
from propsim.engine import Day, run_challenge  # noqa: E402
from propsim.rules import load_rules  # noqa: E402
from propsim.sampling import stationary_bootstrap  # noqa: E402

R = os.path.join(os.path.dirname(__file__), "results")
PRESETS = os.path.join(os.path.dirname(__file__), "..", "..", "tools", "propsim", "presets")
RULESETS = (("two_step_10_5.json", 0.03), ("one_step_10_trailing.json", 0.02), ("futures_50k_eod_trailing.json", 0.02))
RUNS = 1500


def to_days(book):
    d0, d1 = min(book), max(book)
    out, d = [], d0
    while d <= d1:
        if d.weekday() < 5:
            out.append(Day(d, *book[d], traded=True, n_trades=1) if d in book else Day(d))
        d += timedelta(days=1)
    return out


def demean(book):
    m = vs.mean([v[0] for v in book.values()])
    return {d: (v[0] - m, v[1] - m, v[2] - m) for d, v in book.items()}


def policies(book_name):
    fixed = (0.5, 1.0, 1.5, 2.0, 3.0) if book_name == "B1" else (1.0, 2.0, 3.0, 4.0)
    caps = (2.0, 3.0) if book_name == "B1" else (3.0, 4.0)
    out = {f"fixed {L:g}x": (L, None) for L in fixed}
    for k in (10, 20, 40):
        for cap in caps:
            out[f"CPPI k={k} cap={cap:g}x"] = (1.0, (lambda a, k=k, cap=cap: max(0.0, min(cap, k * a.cushion()))))
    return out


def evaluate(days, preset, guard, scale, sizer, reliability=1.0):
    rules = load_rules(os.path.join(PRESETS, preset))
    rng = random.Random(7)
    outs = [run_challenge(stationary_bootstrap(days, rng, 5.0, 2520), rules, scale, payout_reliability=reliability,
                          daily_guard=guard, guard_slippage=0.0025, sizer=sizer) for _ in range(RUNS)]
    dec = outs  # every run counts; an undecided challenge (no pass, no breach within the 2,520-day window) is a failure
    undecided = sum(not o.decided for o in outs) / len(outs)
    passed = [o for o in dec if o.passed_all]
    days_pass = sorted(o.days_to_pass for o in passed)
    months = [(o.days_run + o.funded_days) / 30.4 for o in dec]
    ev = [o.value for o in dec]
    return {"p_undecided": undecided, "p_pass": len(passed) / len(dec), "median_days_to_pass": days_pass[len(days_pass) // 2] if days_pass else None,
            "p_any_payout": sum(o.funded_n_payouts > 0 for o in dec) / len(dec),
            "mean_payouts_usd": vs.mean([o.funded_payouts * rules.initial_balance * reliability for o in dec]),
            "ev_per_attempt_usd": vs.mean(ev), "mean_months": vs.mean(months),
            "ev_per_account_month_usd": vs.mean(ev) / vs.mean(months), "fee": rules.fee}


def main(only=None):
    mr = mr06_days()
    n3 = {d: v for d, v in run("N3", path=True)[0] if date(2014, 1, 1) <= d <= date(2025, 12, 31)}
    n3t = {d: v for d, v in run("N3", variant="twap_stop", path=True)[0] if date(2014, 1, 1) <= d <= date(2025, 12, 31)}
    books = {"B1": mr, "B2": n3, "B3": n3t}
    res = {}
    out_path = os.path.join(R, f"prop_lifecycle_{only}.json" if only else "prop_lifecycle.json")
    for bname, book in books.items():
        if only and bname != only:
            continue
        real, zero = to_days(book), to_days(demean(book))
        res[bname] = {}
        for preset, guard in RULESETS:
            cell = {}
            for pname, (scale, sizer) in policies(bname).items():
                a = evaluate(real, preset, guard, scale, sizer)
                z = evaluate(zero, preset, guard, scale, sizer)
                a["zero_edge_ev_per_attempt_usd"] = z["ev_per_attempt_usd"]
                a["zero_edge_p_pass"] = z["p_pass"]
                a["edge_value_usd"] = a["ev_per_attempt_usd"] - z["ev_per_attempt_usd"]
                cell[pname] = a
                print(bname, preset, pname, {k: round(v, 3) if isinstance(v, float) else v for k, v in a.items()}, flush=True)
            ok = {k: v for k, v in cell.items() if v["edge_value_usd"] > 0}
            best = max(ok, key=lambda k: ok[k]["ev_per_account_month_usd"]) if ok else None
            if best:
                scale, sizer = policies(bname)[best]
                cell["_recommended"] = best
                cell["_recommended_reliability_0.7"] = evaluate(real, preset, guard, scale, sizer, reliability=0.7)
            res[bname][preset] = cell
            json.dump(res, open(out_path, "w"), indent=1, default=str)


def merge():
    res = {}
    for b in ("B1", "B2", "B3"):
        res.update(json.load(open(os.path.join(R, f"prop_lifecycle_{b}.json"))))
    json.dump(res, open(os.path.join(R, "prop_lifecycle.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "merge":
        merge()
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else None)
