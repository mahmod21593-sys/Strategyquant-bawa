"""A13: challenge sizing (A12's recommendation) vs different funded-stage sizing. -> results/prop_lifecycle_funded.json"""
from __future__ import annotations

import json
import os
import random
from datetime import date

import vstats as vs
from prop_lifecycle import PRESETS, RULESETS, RUNS, demean, policies, to_days
from propsim.engine import run_challenge
from propsim.rules import load_rules
from propsim.sampling import stationary_bootstrap
from round4_followup import mr06_days
from run_noise_area import run

R = os.path.join(os.path.dirname(__file__), "results")


def funded_policies(book_name):
    out = {"same": None, "fixed 1x": (1.0, None), "fixed 2x": (2.0, None), "fixed 3x": (3.0, None),
           "CPPI k=40 cap=4x": (None, lambda a: max(0.0, min(4.0, 40 * a.cushion())))}
    if book_name != "B1":
        out["fixed 4x"] = (4.0, None)
    return out


def evaluate(days, preset, guard, scale, sizer, fpol):
    rules = load_rules(os.path.join(PRESETS, preset))
    rng = random.Random(7)
    kw = {}
    if fpol is not None:
        fs, fz = fpol
        kw = {"funded_scale": fs} if fz is None else {"funded_sizer": fz}
    outs = [run_challenge(stationary_bootstrap(days, rng, 5.0, 2520), rules, scale, daily_guard=guard, guard_slippage=0.0025,
                          sizer=sizer, **kw) for _ in range(RUNS)]
    dec = outs  # every run counts; an undecided challenge (no pass, no breach within the 2,520-day window) is a failure
    undecided = sum(not o.decided for o in outs) / len(outs)
    months = [(o.days_run + o.funded_days) / 30.4 for o in dec]
    ev = [o.value for o in dec]
    return {"p_undecided": undecided, "p_pass": sum(o.passed_all for o in dec) / len(dec), "p_any_payout": sum(o.funded_n_payouts > 0 for o in dec) / len(dec),
            "p_funded_breach_given_pass": (sum(o.funded_breached for o in dec if o.passed_all) / max(1, sum(o.passed_all for o in dec))),
            "mean_payouts_usd": vs.mean([o.funded_payouts * rules.initial_balance for o in dec]),
            "ev_per_attempt_usd": vs.mean(ev), "mean_months": vs.mean(months), "ev_per_account_month_usd": vs.mean(ev) / vs.mean(months)}


def main(only=None):
    a12 = json.load(open(os.path.join(R, "prop_lifecycle.json")))
    mr = mr06_days()
    n3 = {d: v for d, v in run("N3", path=True)[0] if date(2014, 1, 1) <= d <= date(2025, 12, 31)}
    n3t = {d: v for d, v in run("N3", variant="twap_stop", path=True)[0] if date(2014, 1, 1) <= d <= date(2025, 12, 31)}
    books = {"B1": mr, "B2": n3, "B3": n3t}
    res = {}
    out_path = os.path.join(R, f"prop_lifecycle_funded_{only}.json" if only else "prop_lifecycle_funded.json")
    for bname, book in books.items():
        if only and bname != only:
            continue
        real, zero = to_days(book), to_days(demean(book))
        res[bname] = {}
        for preset, guard in RULESETS:
            rec = a12.get(bname, {}).get(preset, {}).get("_recommended")
            if rec is None:
                res[bname][preset] = {"note": "no A12 policy with positive edge value"}
                continue
            scale, sizer = policies(bname)[rec]
            cell = {"_challenge_policy": rec}
            for fname, fpol in funded_policies(bname).items():
                a = evaluate(real, preset, guard, scale, sizer, fpol)
                z = evaluate(zero, preset, guard, scale, sizer, fpol)
                a["zero_edge_ev_per_attempt_usd"] = z["ev_per_attempt_usd"]
                a["edge_value_usd"] = a["ev_per_attempt_usd"] - z["ev_per_attempt_usd"]
                cell[fname] = a
                print(bname, preset, rec, "| funded:", fname, {k: round(v, 3) for k, v in a.items()}, flush=True)
            ok = {k: v for k, v in cell.items() if isinstance(v, dict) and v["edge_value_usd"] > 0}
            cell["_recommended_funded"] = max(ok, key=lambda k: ok[k]["ev_per_account_month_usd"]) if ok else None
            res[bname][preset] = cell
            json.dump(res, open(out_path, "w"), indent=1, default=str)


def merge():
    res = {}
    for b in ("B1", "B2", "B3"):
        res.update(json.load(open(os.path.join(R, f"prop_lifecycle_funded_{b}.json"))))
    json.dump(res, open(os.path.join(R, "prop_lifecycle_funded.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "merge":
        merge()
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else None)
