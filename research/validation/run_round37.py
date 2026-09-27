"""Round 37 (PREREGISTRATION.md A51): N3 momentum on earnings-reaction sessions ("stocks in play"), confirmed on 71 S&P 100
stocks not used in round 35 (Dukascopy minute candles; SEC EDGAR 8-K Item 2.02 filings; per-stock measured costs).

    python3 measure_stock_costs.py round37_costs.json <71 tickers>   # A51 cost procedure
    python3 run_round37.py                                           -> results/round37_stocks_in_play.json
"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import numpy as np

import run_family_a as fa
import vstats as vs
from data_audit import spike_mask
from data_duka_chart import local as dlocal
from data_edgar import earnings_filings
from data_histdata import NY
from data_minutes import H, L, O, day_of, group, price_at
from run_round34_minute import r3_grid

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 14289
END = date(2026, 9, 18)
PRIMARY = "range|k0.5|flat"
CIKS = {"BA": [12927], "AMGN": [318154], "BAC": [70858], "C": [831001], "CMCSA": [1166691], "CSCO": [858877], "CVX": [93410],
        "DIS": [1744489, 1001039], "GE": [40545], "GILD": [882095], "GS": [886982], "HD": [354950], "IBM": [51143], "INTC": [50863],
        "PFE": [78003], "T": [732717], "WFC": [72971], "ABT": [1800], "ADBE": [796343], "AIG": [5272], "AMAT": [6951], "BK": [1390777],
        "BMY": [14272], "CAT": [18230], "CI": [1739940, 701221], "CRM": [1108524], "DE": [315189], "KHC": [1637459], "LLY": [59478],
        "LMT": [936468], "MA": [1141391], "MMM": [66740], "ADP": [8670], "AXP": [4962], "CL": [21665], "COP": [1163165], "COST": [909832],
        "CVS": [64803], "F": [37996], "FDX": [1048911], "GM": [1467858], "HON": [773840], "KMI": [1506307], "LOW": [60667],
        "MDLZ": [1103982], "MET": [1099219], "MO": [764180], "MRK": [310158], "MS": [895421], "NKE": [320187], "ORCL": [1341439],
        "PEP": [77476], "PM": [1413329], "PYPL": [1633917], "QCOM": [804328], "SBUX": [829224], "SCHW": [316709], "SO": [92122],
        "TGT": [27419], "TMO": [97745], "TXN": [97476], "UNH": [731766], "BRKB": [1067983], "UPS": [1090727], "USB": [36104],
        "VZ": [732712], "WMT": [104169], "EMR": [32604], "EXC": [1109357], "ISRG": [1035267], "NEE": [753308]}


def reaction_sessions(ciks, sessions):
    """{session date: 'BMO' | 'AMC'} after 8-K Item 2.02 filings (before 09:30 ET -> same day; after 16:00 ET -> next session)."""
    ss = sorted(sessions)
    out = {}
    for cik in ciks:
        for acc in earnings_filings(cik):
            lt = acc.astimezone(NY)
            m, d = lt.hour * 60 + lt.minute, lt.date()
            if m < 570:
                cand, kind = [s for s in ss if s >= d][:1], "BMO"
            elif m >= 960:
                cand, kind = [s for s in ss if s > d][:1], "AMC"
            else:
                continue
            if cand and (cand[0] - d).days <= 5:
                out.setdefault(cand[0], kind)
    return out


def primary_detail(t, x, cost):
    """{date: (side, fill minute, net pnl)} for the native primary (first fill only), as r3_grid's flat mode."""
    day, mod = t // 1440, t % 1440
    ins = (mod >= 570) & (mod < 960)
    keys, _, sh, sl, _, cnt, st = group(day[ins], x[ins])
    xi, mi = x[ins], mod[ins]
    po, pc, pf = price_at(day, mod, x, 570, prefer_open=True), price_at(day, mod, x, 960), price_at(day, mod, x, 959)
    valid = [i for i, k in enumerate(keys.tolist()) if cnt[i] >= 300 and k in po and k in pc and k in pf and day_of(k).weekday() < 5]
    out = {}
    for a, b in zip(valid[:-1], valid[1:]):
        k = int(keys[b])
        w = sh[a] - sl[a]
        r = slice(st[b], st[b] + cnt[b])
        m_, xx = mi[r], xi[r]
        e = m_ < 959
        oo, hh, ll, mm = xx[e, O], xx[e, H], xx[e, L], m_[e]
        U, D = po[k] + 0.5 * w, po[k] - 0.5 * w
        c = np.nonzero((hh >= U) | (ll <= D))[0]
        if not len(c):
            out[day_of(k)] = (0, None, 0.0)
            continue
        j = int(c[0])
        lg = hh[j] >= U and (ll[j] > D or U - oo[j] <= oo[j] - D)
        px = max(U, oo[j]) if lg else min(D, oo[j])
        s = 1 if lg else -1
        out[day_of(k)] = (s, int(mm[j]), s * (pf[k] / px - 1) - cost / 1e4)
    return out


def closes(t, x):
    """{date: (09:30 open, 16:00 close)} on weekdays."""
    day, mod = t // 1440, t % 1440
    po, pc = price_at(day, mod, x, 570, prefer_open=True), price_at(day, mod, x, 960)
    return {day_of(k): (po[k], v) for k, v in sorted(pc.items()) if k in po and day_of(k).weekday() < 5}


def gap_sessions(oc):
    """A51a: sessions whose |open / prior close - 1| exceeds 2x the mean of the previous 20 sessions' absolute gaps."""
    ds = sorted(oc)
    g = [abs(oc[ds[i]][0] / oc[ds[i - 1]][1] - 1) for i in range(1, len(ds))]
    out = set()
    for i in range(20, len(g)):
        m = float(np.mean(g[i - 20:i]))
        if m > 0 and g[i] > 2 * m:
            out.add(ds[i + 1])
    return out


def stats(v, lag=5):
    a = np.array(v, dtype=float)
    t = vs.nw_t(list(a), lag)
    return {"n": int(len(a)), "mean_bps": float(a.mean() * 1e4), "t_hac": t, "p_one_sided": vs.p_one_sided(t)}


def welch(a, b):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    t = float((a.mean() - b.mean()) / se)
    return {"diff_bps": float((a.mean() - b.mean()) * 1e4), "t": t, "p_one_sided": vs.p_one_sided(t), "n": [int(len(a)), int(len(b))]}


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    rho = float(np.corrcoef(ra, rb)[0, 1])
    n = len(a)
    t = rho * math.sqrt((n - 2) / (1 - rho ** 2))
    return {"rho": rho, "n": n, "t": t, "p_one_sided": vs.p_one_sided(t)}


def load_stock(ins, cost):
    t, x = dlocal(ins, NY, END)
    sp = spike_mask(x, 0.03)
    t, x = t[~sp], x[~sp]
    g = r3_grid(t, x, cost)
    grid = {v: {d: r[0] for d, r in rows.items() if d <= END} for v, rows in g.items()}
    det = {d: r for d, r in primary_detail(t, x, cost).items() if d <= END}
    return grid, det, closes(t, x)


def evaluate(universe, costs, ciks, inst=None):
    events, per_stock, vol, other_mean, gap_events = [], {}, {}, {}, []
    grid_ev = {}
    for sym in universe:
        grid, det, cl = load_stock((inst or {}).get(sym, f"{sym}.US/USD"), costs[sym]["cost_per_entry_bps"])
        rs = reaction_sessions(ciks[sym], grid[PRIMARY].keys())
        ds = sorted(grid[PRIMARY])
        cds = sorted(cl)
        lr = np.diff(np.log([cl[d][1] for d in cds[:251]]))
        gp = gap_sessions(cl)
        gap_events.extend({"sym": sym, "date": d, "pnl": grid[PRIMARY][d]} for d in ds if d in gp)
        vol[sym] = float(lr.std(ddof=1) * math.sqrt(252)) if len(lr) > 50 else None
        cut = cds[250] if len(cds) > 250 else None
        oth = [grid[PRIMARY][d] for d in ds if d not in rs and cut and d > cut]
        other_mean[sym] = float(np.mean(oth)) if oth else None
        for d in ds:
            if d in rs:
                s, fm, _ = det.get(d, (0, None, 0.0))
                events.append({"sym": sym, "date": d, "pnl": grid[PRIMARY][d], "kind": rs[d], "side": s, "fill_min": fm})
                for v in grid:
                    if d in grid[v]:
                        grid_ev.setdefault(v, []).append((d, grid[v][d]))
        per_stock[sym] = {"sessions": len(ds), "events": sum(1 for d in ds if d in rs), "cost_bps": costs[sym]["cost_per_entry_bps"],
                          "all": stats(list(grid[PRIMARY].values())), "other": [grid[PRIMARY][d] for d in ds if d not in rs]}
        print("SIP", sym, per_stock[sym]["sessions"], per_stock[sym]["events"], round(per_stock[sym]["all"]["mean_bps"], 2), flush=True)
    return events, per_stock, vol, other_mean, grid_ev, gap_events


def event_portfolio(events):
    by = {}
    for e in events:
        by.setdefault(e["date"], []).append(e["pnl"])
    ds = sorted(by)
    return ds, [float(np.mean(by[d])) for d in ds]


def main():
    costs = json.load(open(os.path.join(OUT, "round37_costs.json")))
    universe = [s for s in CIKS if s in costs]
    events, per_stock, vol, other_mean, grid_ev, gap_events = evaluate(universe, costs, CIKS)
    ds, ev = event_portfolio(events)
    e1 = stats(ev)
    mid = ds[len(ds) // 2]
    e1["halves_bps"] = (float(np.mean([v for d, v in zip(ds, ev) if d < mid]) * 1e4), float(np.mean([v for d, v in zip(ds, ev) if d >= mid]) * 1e4))
    e1["split_date"] = str(mid)
    e1["events"] = len(events)
    other = [v for s in per_stock.values() for v in s["other"]]
    e2 = welch([e["pnl"] for e in events], other)
    names = [s for s in universe if vol.get(s) is not None and other_mean.get(s) is not None]
    e3 = spearman([vol[s] for s in names], [other_mean[s] for s in names])
    gds, gev = event_portfolio(gap_events)
    e4 = stats(gev)
    gmid = gds[len(gds) // 2]
    e4["halves_bps"] = (float(np.mean([v for d, v in zip(gds, gev) if d < gmid]) * 1e4), float(np.mean([v for d, v in zip(gds, gev) if d >= gmid]) * 1e4))
    e4["sessions"] = len(gap_events)
    ev_keys = {(e["sym"], e["date"]) for e in events}
    e4["share_that_are_earnings_sessions"] = float(np.mean([(e["sym"], e["date"]) in ev_keys for e in gap_events]))
    prim = {"E1": e1, "E2": e2, "E3": e3, "E4": e4}
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    verdict = {"stocks_in_play": "CONFIRMED" if (e1["p_holm"] < 0.05 and all(h > 0 for h in e1["halves_bps"])) else "NOT CONFIRMED",
               "volatility_link": "CONFIRMED" if e3["p_holm"] < 0.05 else "NOT CONFIRMED",
               "gap_proxy": "CONFIRMED" if (e4["p_holm"] < 0.05 and all(h > 0 for h in e4["halves_bps"])) else "NOT CONFIRMED"}
    res_gap_other = [e["pnl"] for e in gap_events if (e["sym"], e["date"]) not in ev_keys]
    res = {"primary": prim, "verdict": verdict, "gap_sessions_not_earnings": stats(res_gap_other, 0)}
    res["per_event_stats"] = stats([e["pnl"] for e in events], 0)
    res["by_kind"] = {k: stats([e["pnl"] for e in events if e["kind"] == k], 0) for k in ("BMO", "AMC")}
    res["by_side"] = {k: stats([e["pnl"] for e in events if e["side"] == s], 0) for k, s in (("long", 1), ("short", -1))}
    res["no_fill_share"] = float(np.mean([e["side"] == 0 for e in events]))
    res["fill_before_1000"] = stats([e["pnl"] for e in events if e["fill_min"] is not None and e["fill_min"] < 600], 0)
    res["fill_after_1000"] = stats([e["pnl"] for e in events if e["fill_min"] is not None and e["fill_min"] >= 600], 0)
    res["by_year"] = {y: stats([e["pnl"] for e in events if e["date"].year == y], 0) for y in sorted({e["date"].year for e in events})}
    res["grid_on_events"] = {v: stats([p for _, p in sorted(r)], 0) for v, r in grid_ev.items()}
    res["share_stocks_event_mean_positive"] = float(np.mean([np.mean([e["pnl"] for e in events if e["sym"] == s]) > 0
                                                             for s in universe if any(e["sym"] == s for e in events)]))
    res["per_stock"] = {s: {k: v for k, v in d.items() if k != "other"} | {"ex_ante_vol": vol.get(s), "other_mean_bps": (other_mean[s] or 0) * 1e4,
                                                                            "event_mean_bps": float(np.mean([e["pnl"] for e in events if e["sym"] == s]) * 1e4)
                                                                            if any(e["sym"] == s for e in events) else None}
                        for s, d in per_stock.items()}
    # combined with the round-35 stocks (83 in all), for the build estimate
    try:
        from measure_stock_costs import STOCKS
        from run_round35 import CIKS as CIKS35
        c35 = json.load(open(os.path.join(OUT, "round35_costs.json")))
        ev35, *_ = evaluate(list(STOCKS), {s: c35[s] for s in STOCKS}, {s: CIKS35[s] for s in STOCKS}, STOCKS)
        allev = events + ev35
        d2, v2 = event_portfolio(allev)
        res["combined_83"] = {"event_portfolio": stats(v2), "per_event": stats([e["pnl"] for e in allev], 0), "events": len(allev),
                              "event_days_per_year": len(d2) / ((d2[-1] - d2[0]).days / 365.25)}
    except Exception as ex:  # reported, not fatal
        res["combined_83"] = {"error": repr(ex)}
    json.dump(res, open(os.path.join(OUT, "round37_stocks_in_play.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "verdict", "per_event_stats", "by_kind", "by_side", "no_fill_share", "fill_before_1000",
                                          "fill_after_1000", "share_stocks_event_mean_positive", "combined_83")}, indent=1, default=str))
    for v, s in res["grid_on_events"].items():
        print(v, round(s["mean_bps"], 2), round(s["t_hac"], 2), s["n"])
    for y, s in res["by_year"].items():
        print(y, round(s["mean_bps"], 2), round(s["t_hac"], 2), s["n"])


if __name__ == "__main__":
    main()
