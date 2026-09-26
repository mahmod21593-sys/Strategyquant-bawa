"""A16: prop lifecycle on published firm terms (FTMO 2-Step Standard/Swing, FTMO 1-Step, Topstep 50K).

    python3 prop_lifecycle_real.py ftmo2_standard|ftmo2_swing|ftmo1|topstep   -> results/prop_lifecycle_real_<group>.json
    python3 prop_lifecycle_real.py merge                                        -> results/prop_lifecycle_real.json
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date, timedelta

import vstats as vs
from data_calendar import fomc_days
from data_histdata import table
from data_yahoo import daily
from prop_lifecycle import demean, evaluate, to_days
from round4_followup import mr06_days
from run_histdata import RTH, us_days
from run_noise_area import run
from run_round4 import irx_map, tbill
from run_round7 import G6_UNIVERSE

R = os.path.join(os.path.dirname(__file__), "results")
LO, HI = date(2014, 1, 1), date(2025, 12, 31)
GROUPS = {
    "ftmo2_standard": [("ftmo_2step_100k.json", 0.03, b) for b in ("B1s", "B2n", "B5s")],
    "ftmo2_swing": [("ftmo_2step_100k.json", 0.03, b) for b in ("B1", "B2", "B4", "B5")],
    "ftmo1": [("ftmo_1step_100k.json", 0.02, b) for b in ("B1s", "B2n", "B5s")],
    "topstep": [("topstep_50k.json", 0.02, "B2")],
}


def news_skip(session_days):
    """{date: minutes} for FTMO's high-impact blackout: ISM (10:00, 1st and 3rd trading day), FOMC (14:00, 14:30), minutes (14:00)."""
    skip = {}
    by_month = {}
    for d in session_days:
        by_month.setdefault((d.year, d.month), []).append(d)
    for ds in by_month.values():
        ds.sort()
        for i in (0, 2):
            if i < len(ds):
                skip.setdefault(ds[i], set()).add(600)
    sd = set(session_days)
    for f in fomc_days():
        if f in sd:
            skip.setdefault(f, set()).update({840, 870})
        m = f + timedelta(days=21)
        if m in sd:
            skip.setdefault(m, set()).add(840)
    return skip


def tsmom_days(markup=0.02):
    """G6 as daily P&L (fractions at 1x): {weekday: (pnl, low, high)}; weekend crypto P&L is booked on Monday."""
    rates = irx_map()
    keys = sorted(rates)
    rows = {s: daily(s) for s in G6_UNIVERSE}
    ex, ohlc = {}, {}
    for s, rs in rows.items():
        ex[s], ohlc[s] = [], {}
        for a, b in zip(rs, rs[1:]):
            ex[s].append((b["date"], b["adj"] / a["adj"] - 1 - tbill(rates, keys, a["date"], b["date"])))
            ohlc[s][b["date"]] = (b["l"] / a["c"] - 1, b["h"] / a["c"] - 1)
    vol = {}
    for s, e in ex.items():
        ann = 365 if s == "BTC-USD" else 261
        delta, m, v = 60 / 61, None, None
        vol[s] = {}
        for d, x in e:
            if m is None:
                m, v = x, x * x
            else:
                m = delta * m + (1 - delta) * x
                v = delta * v + (1 - delta) * (x - m) ** 2
            vol[s][d] = math.sqrt(v * ann)
    idx = {s: {d: i for i, (d, _) in enumerate(e)} for s, e in ex.items()}
    month_end = {}
    for s, e in ex.items():
        for i, (d, _) in enumerate(e):
            if i + 1 == len(e) or e[i + 1][0].month != d.month:
                month_end.setdefault((d.year, d.month), {})[s] = d
    ms = sorted(month_end)
    pos_by_month = {}
    for a, b in zip(ms, ms[1:]):
        pos = {}
        for s, d in month_end[a].items():
            i = idx[s][d]
            if i < 300:
                continue
            past = math.prod(1 + x for _, x in ex[s][i - 251:i + 1]) - 1
            w = 0.40 / vol[s][d] if vol[s][d] > 0 else 0.0
            pos[s] = (1 if past > 0 else -1) * w
        n = len(pos)
        pos_by_month[b] = {s: v / n for s, v in pos.items()} if n else {}
    out = {}
    prev_pos, prev_day = {}, None
    all_days = sorted({d for e in ex.values() for d, _ in e})
    exd = {s: dict(e) for s, e in ex.items()}
    for d in all_days:
        if not (LO <= d <= HI):
            continue
        pos = pos_by_month.get((d.year, d.month), {})
        book = d if d.weekday() < 5 else d + timedelta(days=7 - d.weekday())
        pnl = lo = hi = 0.0
        for s, w in pos.items():
            if d not in exd[s]:
                continue
            pnl += w * exd[s][d]
            l, h = ohlc[s][d]
            worst, best = (l, h) if w > 0 else (h, l)
            lo += min(0.0, w * worst)
            hi += max(0.0, w * best)
        gross = sum(abs(w) for w in pos.values())
        if d.weekday() < 5:
            cal = (d - prev_day).days if prev_day else 1
            fin = markup * gross * cal / 360
            if (d.year, d.month) != ((prev_day.year, prev_day.month) if prev_day else None):
                fin += 2e-4 * sum(abs(pos.get(s, 0) - prev_pos.get(s, 0)) for s in set(pos) | set(prev_pos))
                prev_pos = pos
            prev_day = d
        else:
            fin = 0.0
        p0, l0, h0 = out.get(book, (0.0, 0.0, 0.0))
        out[book] = (p0 + pnl - fin, l0 + lo - fin, h0 + hi)
    return {d: v for d, v in out.items() if LO <= d <= HI}


def scaled_sum(books, target=0.005):
    days = sorted({d for b in books for d in b})
    wd = [d for d in days if d.weekday() < 5]
    out = {}
    for b in books:
        s = vs.sd([b.get(d, (0.0,))[0] for d in wd])
        k = target / s
        for d, (p, l, h) in b.items():
            p0, l0, h0 = out.get(d, (0.0, 0.0, 0.0))
            out[d] = (p0 + k * p, l0 + k * l, h0 + k * h)
    return out


def build_books(names):
    need = set(names)
    books = {}
    if need & {"B1", "B1s", "B5", "B5s"}:
        mr = mr06_days()
        tab = table("SPXUSD", range(2014, 2026), RTH)
        days = us_days(tab)
        prev = {b: a for a, b in zip(days, days[1:])}
        books["B1"] = mr
        books["B1s"] = {d: v for d, v in mr.items() if (d - prev[d]).days <= 1}
    if need & {"B2", "B2n", "B5", "B5s"}:
        n3 = {d: v for d, v in run("N3", path=True)[0] if LO <= d <= HI}
        books["B2"] = n3
        skip = news_skip(sorted(n3))
        books["B2n"] = {d: v for d, v in run("N3", path=True, skip=skip)[0] if LO <= d <= HI}
    if need & {"B4", "B5"}:
        books["B4"] = tsmom_days(0.02)
    if "B5" in need:
        books["B5"] = scaled_sum([books["B1"], books["B2"], books["B4"]])
    if "B5s" in need:
        books["B5s"] = scaled_sum([books["B1s"], books["B2n"]])
    return books


def policies(book):
    intraday = book in ("B2", "B2n")
    fixed = (1.0, 2.0, 3.0, 4.0) if intraday else (0.5, 1.0, 1.5, 2.0, 3.0)
    caps = (3.0, 4.0) if intraday else (2.0, 3.0)
    out = {f"fixed {L:g}x": (L, None) for L in fixed}
    for k in (10, 20, 40):
        for cap in caps:
            out[f"CPPI k={k} cap={cap:g}x"] = (1.0, (lambda a, k=k, cap=cap: max(0.0, min(cap, k * a.cushion()))))
    return out


def main(group):
    cells = GROUPS[group]
    books = build_books([b for _, _, b in cells])
    stats = {b: {"trading_days": sum(1 for v in books[b].values() if v[0] != 0), "mean_bps_per_day_1x": vs.mean([v[0] for v in books[b].values()]) * 1e4,
                 "sd_bps_1x": vs.sd([v[0] for v in books[b].values()]) * 1e4} for b in books}
    print("books", stats, flush=True)
    res = {"_books": stats}
    out_path = os.path.join(R, f"prop_lifecycle_real_{group}.json")
    for preset, guard, b in cells:
        real, zero = to_days(books[b]), to_days(demean(books[b]))
        cell = {}
        for pname, (scale, sizer) in policies(b).items():
            a = evaluate(real, preset, guard, scale, sizer)
            z = evaluate(zero, preset, guard, scale, sizer)
            a["zero_edge_ev_per_attempt_usd"], a["zero_edge_p_pass"] = z["ev_per_attempt_usd"], z["p_pass"]
            a["edge_value_usd"] = a["ev_per_attempt_usd"] - z["ev_per_attempt_usd"]
            cell[pname] = a
            print(group, b, preset, pname, {k: round(v, 3) if isinstance(v, float) else v for k, v in a.items()}, flush=True)
        ok = {k: v for k, v in cell.items() if v["edge_value_usd"] > 0}
        best = max(ok, key=lambda k: ok[k]["ev_per_account_month_usd"]) if ok else None
        cell["_recommended"] = best
        if best:
            scale, sizer = policies(b)[best]
            cell["_recommended_reliability_0.7"] = evaluate(real, preset, guard, scale, sizer, reliability=0.7)
            if b in ("B4", "B5"):
                for mk in (0.0, 0.04):
                    alt = dict(books)
                    alt["B4"] = tsmom_days(mk)
                    bk = alt["B4"] if b == "B4" else scaled_sum([alt["B1"], alt["B2"], alt["B4"]])
                    cell[f"_recommended_markup_{mk:g}"] = evaluate(to_days(bk), preset, guard, scale, sizer)
        res[f"{b}|{preset}"] = cell
        json.dump(res, open(out_path, "w"), indent=1, default=str)


def merge():
    res = {}
    for g in GROUPS:
        p = os.path.join(R, f"prop_lifecycle_real_{g}.json")
        if os.path.exists(p):
            res[g] = json.load(open(p))
    json.dump(res, open(os.path.join(R, "prop_lifecycle_real.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    if sys.argv[1] == "merge":
        merge()
    else:
        main(sys.argv[1])
