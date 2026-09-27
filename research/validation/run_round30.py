"""Round 30 (PREREGISTRATION.md A44): quarter-end settlement days beyond the Gotobi dates.

    python3 run_round30.py   -> results/round30_quarter_end.json
"""
from __future__ import annotations

import json
import os
from datetime import date

import numpy as np

import vstats as vs
from data_calendar import gotobi_days, japan_holidays
from run_round23 import day_types, windows
from run_round27 import basket, hac, welch

OUT = os.path.join(os.path.dirname(__file__), "results")
CROSSES = ("GBPJPY", "CHFJPY", "AUDJPY", "CADJPY", "NZDJPY")


def qe_days(y0=2003, y1=2026, months=(3, 6, 9, 12)):
    """Last 4 Tokyo business days of the given months that are not Gotobi / holiday / day-after days."""
    typ = day_types(2002, 2026)
    hol = japan_holidays(y0, y1)
    out = set()
    for y in range(y0, y1 + 1):
        for m in months:
            nxt = date(y + (m == 12), m % 12 + 1, 1)
            biz = []
            d = date(y, m, 1)
            while d < nxt:
                if d.weekday() < 5 and d not in hol:
                    biz.append(d)
                d = date.fromordinal(d.toordinal() + 1)
            out |= {b for b in biz[-4:] if typ.get(b) == "NORMAL"}
    return out, typ


def main():
    D, typ = qe_days()
    P, _ = qe_days(months=(1, 2, 4, 5, 7, 8, 10, 11))  # placebo: other month ends
    uj = windows("USDJPY", range(2003, 2027), date(2003, 1, 1), date(2026, 9, 18))
    per = {s: windows(s, range(2006, 2027), date(2008, 1, 1), date(2026, 9, 18)) for s in CROSSES}
    b = {w: basket(per, w) for w in ("PRE", "POST")}
    sel = lambda rows, ds: [v for d, v in rows.items() if d in ds]
    norm = lambda rows, ds: [v for d, v in rows.items() if typ.get(d) == "NORMAL" and d not in ds and d not in P]
    prim = {"Q1": welch(sel(uj["POST"], D), norm(uj["POST"], D), 1), "Q2": welch(sel(b["POST"], D), norm(b["POST"], D), 1)}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    res = {"primary": prim}
    net = {d: v - 1e-4 for d, v in uj["POST"].items() if d in D}
    res["usdjpy_D_net"] = {**hac(list(net.values())),
                           "halves_bps": (float(np.mean([v for d, v in net.items() if d < date(2015, 1, 1)]) * 1e4),
                                          float(np.mean([v for d, v in net.items() if d >= date(2015, 1, 1)]) * 1e4))}
    n_pass = sum(prim[k]["p_holm"] < 0.05 for k in prim)
    ok = n_pass == 2 and all(h > 0 for h in res["usdjpy_D_net"]["halves_bps"])
    res["verdict"] = "CONFIRMED EXPANSION" if ok else "PARTIAL" if n_pass == 1 else "NOT CONFIRMED"
    res["descriptive"] = {"usdjpy_POST_D_gross": hac(sel(uj["POST"], D)), "usdjpy_POST_NORMAL": hac(norm(uj["POST"], D)),
                          "basket_POST_D_gross": hac(sel(b["POST"], D)), "basket_POST_NORMAL": hac(norm(b["POST"], D)),
                          "usdjpy_PRE_D": hac(sel(uj["PRE"], D)), "basket_PRE_D": hac(sel(b["PRE"], D)),
                          "usdjpy_POST_placebo_other_month_ends": hac(sel(uj["POST"], P)),
                          "basket_POST_placebo": hac(sel(b["POST"], P)),
                          "usdjpy_POST_fiscal_MarSep": hac([v for d, v in uj["POST"].items() if d in D and d.month in (3, 9)]),
                          "usdjpy_POST_JunDec": hac([v for d, v in uj["POST"].items() if d in D and d.month in (6, 12)])}
    json.dump(res, open(os.path.join(OUT, "round30_quarter_end.json"), "w"), indent=1, default=str)
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
