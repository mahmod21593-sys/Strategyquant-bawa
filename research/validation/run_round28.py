"""Round 28 (PREREGISTRATION.md A42): the Toshin month-start flow confirmed on the five crosses' mornings,
a category never isolated on them.

    python3 run_round28.py   -> results/round28_ts_confirm.json
"""
from __future__ import annotations

import json
import os
from datetime import date

import numpy as np

import vstats as vs
from run_round23 import day_types, windows
from run_round27 import basket, hac, ts_days, welch

OUT = os.path.join(os.path.dirname(__file__), "results")
CROSSES = ("GBPJPY", "CHFJPY", "AUDJPY", "CADJPY", "NZDJPY")
LO, HI = date(2008, 1, 1), date(2026, 9, 18)


def main():
    typ = day_types(2002, 2026)
    tsd = ts_days(typ)
    per = {s: windows(s, range(2006, 2027), LO, HI) for s in CROSSES}
    for s, w in per.items():
        print("cross", s, len(w["PRE"]), flush=True)
    b = basket(per, "PRE")
    ts = {d: v for d, v in b.items() if d in tsd}
    norm = {d: v for d, v in b.items() if typ.get(d) == "NORMAL" and d not in tsd}
    c1 = hac([v for _, v in sorted(ts.items())])
    c1["p_one_sided"] = vs.p_one_sided(c1["t"], 1)
    prim = {"C1": c1, "C2": welch(list(ts.values()), list(norm.values()), 1)}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    n_pass = sum(prim[k]["p_holm"] < 0.05 for k in prim)
    res = {"primary": prim, "verdict": "CONFIRMED EDGE" if n_pass == 2 else "PARTIAL" if n_pass == 1 else "NOT CONFIRMED"}
    res["halves_bps"] = (float(np.mean([v for d, v in ts.items() if d < date(2015, 1, 1)]) * 1e4),
                         float(np.mean([v for d, v in ts.items() if d >= date(2015, 1, 1)]) * 1e4))
    res["per_cross"] = {}
    for s, w in per.items():
        a = [v for d, v in w["PRE"].items() if d in tsd]
        n = [v for d, v in w["PRE"].items() if typ.get(d) == "NORMAL" and d not in tsd]
        res["per_cross"][s] = {"TS": hac(a), "NORMAL": hac(n), "diff": welch(a, n, 1)}
    au = {s: per[s] for s in ("AUDJPY", "NZDJPY")}
    ot = {s: per[s] for s in ("GBPJPY", "CHFJPY", "CADJPY")}
    for lab, grp in (("toshin_currencies_AUD_NZD", au), ("other_crosses", ot)):
        bb = basket(grp, "PRE", min_n=2)
        res[lab] = {"TS": hac([v for d, v in bb.items() if d in tsd]),
                    "NORMAL": hac([v for d, v in bb.items() if typ.get(d) == "NORMAL" and d not in tsd])}
    from run_round27 import ts_days as _t  # day ranks on the basket
    from data_calendar import japan_holidays
    hol = japan_holidays(2003, 2026)
    rank = {}
    for y in range(2008, 2027):
        for m in range(1, 13):
            biz, d = [], date(y, m, 1)
            while d.month == m and len(biz) < 3:
                if d.weekday() < 5 and d not in hol:
                    biz.append(d)
                d = date.fromordinal(d.toordinal() + 1)
            for i, bd in enumerate(biz, 1):
                rank[bd] = i
    res["by_day_rank"] = {f"day{i}": hac([v for d, v in ts.items() if rank.get(d) == i]) for i in (1, 2, 3)}
    json.dump(res, open(os.path.join(OUT, "round28_ts_confirm.json"), "w"), indent=1, default=str)
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
