"""Round 27 (PREREGISTRATION.md A41): the Japanese-holiday morning and the day after, confirmed on the five
unexamined JPY crosses (2008-2026); Toshin month-start flows on USDJPY.

    python3 run_round27.py   -> results/round27_hd_ts.json
"""
from __future__ import annotations

import json
import os
from datetime import date

import numpy as np

import vstats as vs
from run_round23 import day_types, windows

OUT = os.path.join(os.path.dirname(__file__), "results")
E = date(1970, 1, 1).toordinal()
CROSSES = ("GBPJPY", "CHFJPY", "AUDJPY", "CADJPY", "NZDJPY")
LO, HI = date(2008, 1, 1), date(2026, 9, 18)


def hac(v):
    x = np.array(v, dtype=float)
    t = vs.nw_t(list(x), 5)
    return {"n": int(len(x)), "mean_bps": float(x.mean() * 1e4), "t": t}


def welch(a, b, sign):
    import math
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    t = float((a.mean() - b.mean()) / se)
    return {"diff_bps": float((a.mean() - b.mean()) * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t, sign), "n": [int(len(a)), int(len(b))]}


def basket(per, win, min_n=3):
    days = sorted({d for s in per for d in per[s][win]})
    return {d: float(np.mean([per[s][win][d] for s in per if d in per[s][win]])) for d in days
            if sum(d in per[s][win] for s in per) >= min_n}


def ts_days(typ, y0=2003, y1=2026):
    """The first 3 Tokyo business days of each month that are plain NORMAL days under the round-23 typing."""
    from data_calendar import japan_holidays
    hol = japan_holidays(y0, y1)
    out = set()
    for y in range(y0, y1 + 1):
        for m in range(1, 13):
            biz = []
            d = date(y, m, 1)
            while d.month == m and len(biz) < 3:
                if d.weekday() < 5 and d not in hol:
                    biz.append(d)
                d = date.fromordinal(d.toordinal() + 1)
            out |= {b for b in biz if typ.get(b) == "NORMAL"}
    return out


def main():
    typ = day_types(2002, 2026)
    per = {s: windows(s, range(2006, 2027), LO, HI) for s in CROSSES}
    for s, w in per.items():
        print("cross", s, len(w["PRE"]), flush=True)
    b = {win: basket(per, win) for win in ("PRE", "POST")}
    by = lambda rows, lab: [v for d, v in rows.items() if typ.get(d) == lab]
    res = {}
    h1 = hac(by(b["PRE"], "HOL"))
    h1["p_one_sided"] = vs.p_one_sided(h1["t"], -1)
    prim = {"H1": h1, "H2": welch(by(b["PRE"], "HOL"), by(b["PRE"], "NORMAL"), -1),
            "H3": welch(by(b["POST"], "AFTER"), by(b["POST"], "NORMAL"), 1)}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    res["primary"] = prim
    res["holiday_leg"] = "CONFIRMED" if prim["H1"]["p_holm"] < 0.05 and prim["H2"]["p_holm"] < 0.05 else "NOT CONFIRMED"
    res["day_after"] = "CONFIRMED" if prim["H3"]["p_holm"] < 0.05 else "NOT CONFIRMED"
    # build checks on USDJPY
    uj_all = windows("USDJPY", range(2003, 2027), date(2003, 1, 1), HI)
    hol_short = {d: -v - 1e-4 for d, v in uj_all["PRE"].items() if typ.get(d) == "HOL"}
    res["build_check_usdjpy_holiday_short_net"] = {**hac(list(hol_short.values())),
        "halves_bps": (float(np.mean([v for d, v in hol_short.items() if d < date(2015, 1, 1)]) * 1e4),
                       float(np.mean([v for d, v in hol_short.items() if d >= date(2015, 1, 1)]) * 1e4)),
        "per_year_positive": f"{sum(np.mean([v for d, v in hol_short.items() if d.year == y]) > 0 for y in range(2003, 2027) if any(d.year == y for d in hol_short))}"
                             f"/{len({d.year for d in hol_short})}"}
    da_post = {d: v - 1e-4 for d, v in uj_all["POST"].items() if typ.get(d) == "AFTER" and d >= date(2014, 1, 1)}
    res["build_check_usdjpy_day_after_post_net_2014_26"] = hac(list(da_post.values()))
    res["per_cross"] = {s: {"PRE_HOL": hac(by(w["PRE"], "HOL")), "POST_AFTER": hac(by(w["POST"], "AFTER"))} for s, w in per.items()}
    res["basket_POST_HOL"] = hac(by(b["POST"], "HOL"))
    res["basket_by_type"] = {win: {lab: hac(by(b[win], lab)) for lab in ("HOL", "AFTER", "NORMAL", "GOTO")} for win in ("PRE", "POST")}
    # ---------------- TS
    tsd = ts_days(typ)
    uj = uj_all
    t1 = hac([v for d, v in uj["PRE"].items() if d in tsd])
    prim_ts = {"T1": {**t1, "p_one_sided": vs.p_one_sided(t1["t"], 1)},
               "T2": welch([v for d, v in uj["PRE"].items() if d in tsd], [v for d, v in uj["PRE"].items() if typ.get(d) == "NORMAL" and d not in tsd], 1)}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim_ts.items()})
    for k in prim_ts:
        prim_ts[k]["p_holm"] = holm[k]
    net = {d: v - 1e-4 for d, v in uj["PRE"].items() if d in tsd}
    halves = (float(np.mean([v for d, v in net.items() if d < date(2015, 1, 1)]) * 1e4),
              float(np.mean([v for d, v in net.items() if d >= date(2015, 1, 1)]) * 1e4))
    res["TS"] = {"primary": prim_ts, "net_halves_bps": halves,
                 "verdict": "CANDIDATE" if all(prim_ts[k]["p_holm"] < 0.05 for k in prim_ts) and all(h > 0 for h in halves) else "NO EDGE"}
    # TS descriptive: day rank 1/2/3, POST, session, EURJPY
    from data_calendar import japan_holidays
    hol = japan_holidays(2003, 2026)
    rank = {}
    for y in range(2003, 2027):
        for m in range(1, 13):
            biz, d = [], date(y, m, 1)
            while d.month == m and len(biz) < 3:
                if d.weekday() < 5 and d not in hol:
                    biz.append(d)
                d = date.fromordinal(d.toordinal() + 1)
            for i, bd in enumerate(biz, 1):
                rank[bd] = i
    res["TS_descriptive"] = {f"day{i}_PRE": hac([v for d, v in uj["PRE"].items() if rank.get(d) == i and d in tsd]) for i in (1, 2, 3)}
    res["TS_descriptive"]["POST_TS"] = hac([v for d, v in uj["POST"].items() if d in tsd])
    ej = windows("EURJPY", range(2008, 2027), LO, HI)
    res["TS_descriptive"]["EURJPY_PRE_TS"] = hac([v for d, v in ej["PRE"].items() if d in tsd])
    res["TS_descriptive"]["EURJPY_PRE_NORMAL"] = hac([v for d, v in ej["PRE"].items() if typ.get(d) == "NORMAL" and d not in tsd])
    json.dump(res, open(os.path.join(OUT, "round27_hd_ts.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "holiday_leg", "day_after", "build_check_usdjpy_holiday_short_net",
                                          "build_check_usdjpy_day_after_post_net_2014_26", "TS")}, indent=1, default=str))
    print("per_cross", {s: {k: (round(q["mean_bps"], 2), round(q["t"], 2), q["n"]) for k, q in v.items()} for s, v in res["per_cross"].items()})
    print("basket_by_type", {w: {l: (round(q["mean_bps"], 2), round(q["t"], 2), q["n"]) for l, q in d.items()} for w, d in res["basket_by_type"].items()})
    print("TS_desc", {k: (round(v["mean_bps"], 2), round(v["t"], 2), v["n"]) for k, v in res["TS_descriptive"].items()})


if __name__ == "__main__":
    main()
