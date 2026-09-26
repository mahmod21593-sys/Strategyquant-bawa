"""A20 H3: MR-06 (three down closes) on single large stocks. -> results/h3.json"""
from __future__ import annotations

import json
import os
from datetime import date

import vstats as vs
from data_yahoo import daily
from run_h2 import UNIVERSE

OUT = os.path.join(os.path.dirname(__file__), "results")
BPS = 1e4


def signals(rows):
    out = []
    base = {}
    for a, b in zip(rows, rows[1:]):
        base.setdefault(b["date"].year, []).append((b["adj"] / a["adj"] - 1) * BPS)
    base = {y: vs.mean(v) for y, v in base.items()}
    for i in range(3, len(rows) - 1):
        c = [rows[i - k]["adj"] for k in range(4)]
        if c[0] < c[1] < c[2] < c[3]:
            nd = rows[i + 1]["date"]
            r = (rows[i + 1]["adj"] / rows[i]["adj"] - 1) * BPS
            out.append((rows[i]["date"], nd, r, r - base[nd.year]))
    return out


def main():
    spy_rows = daily("SPY")
    spy = {r["date"]: r["adj"] for r in spy_rows}
    idx_sig = {s for s, *_ in signals(spy_rows)}
    per, mkt, overlap = {}, {}, []
    for tic in UNIVERSE:
        rows = [r for r in daily(tic) if r["date"] in spy]
        sig = signals(rows)
        per[tic] = [(nd, x) for _, nd, _, x in sig]
        mkt[tic] = [(nd, r - (spy[nd] / spy[s] - 1) * BPS) for s, nd, r, _ in sig]
        overlap += [s in idx_sig for s, *_ in sig]
    res = {}
    for name, book in (("primary", per), ("market_adjusted", mkt)):
        g = {}
        for rows in book.values():
            for d, x in rows:
                g.setdefault(d, []).append(x)
        ds = sorted(g)
        xs = [vs.mean(g[d]) for d in ds]
        for label, lo, hi in (("2014_2026", date(2014, 1, 1), date(2026, 8, 31)), ("2005_2013", date(2005, 1, 1), date(2013, 12, 31))):
            sel = [(d, x) for d, x in zip(ds, xs) if lo <= d <= hi]
            res.setdefault(name, {})[label] = vs.summarize([d for d, _ in sel], [x for _, x in sel], 1, 5, 5.0,
                                                           boot=(name == "primary" and label == "2014_2026"))
        if name == "primary":
            sel = [x for d, x in zip(ds, xs) if date(2014, 1, 1) <= d <= date(2026, 8, 31)]
            res["dsr_N747"] = vs.deflated_sharpe([x - 5.0 for x in sel], 747)
    res["share_on_index_mr06_days"] = vs.mean(overlap)
    res["per_stock_2014_2026"] = {t: vs.summarize([d for d, _ in v if d.year >= 2014], [x for d, x in v if d.year >= 2014], 1, 5, 5.0, boot=False)
                                  for t, v in per.items()}
    p = res["primary"]["2014_2026"]
    ok = p["p_one_sided"] < 0.05 and p["net_mean_bps"] > 0 and res["primary"]["2005_2013"]["mean_bps"] > 0
    res["verdict"] = "CONFIRMED" if ok else "WEAK" if p["p_one_sided"] < 0.05 else "NOT CONFIRMED"
    for name in ("primary", "market_adjusted"):
        a, b = res[name]["2014_2026"], res[name]["2005_2013"]
        print(f"{name:16s} 2014-26 n={a['n']} mean={a['mean_bps']:.1f} net={a['net_mean_bps']:.1f} t={a['t_hac']:.2f} p={a['p_one_sided']:.4f} | 2005-13 mean={b['mean_bps']:.1f} t={b['t_hac']:.2f}")
    print("verdict", res["verdict"], "dsr", round(res["dsr_N747"], 3), "share on index MR-06 days", round(res["share_on_index_mr06_days"], 2))
    json.dump(res, open(os.path.join(OUT, "h3.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
