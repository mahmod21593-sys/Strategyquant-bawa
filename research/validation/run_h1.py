"""A17 H1: cross-sectional momentum across equity indices. -> results/h1.json"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import vstats as vs
from data_yahoo import daily

OUT = os.path.join(os.path.dirname(__file__), "results")
UNIVERSE = ["^GSPC", "^NDX", "^DJI", "^RUT", "^GDAXI", "^FTSE", "^FCHI", "^STOXX50E", "^N225", "^HSI", "^AXJO", "^IBEX", "^SSMI", "^AEX"]


def main():
    px = {s: {r["date"]: r["c"] for r in daily(s)} for s in UNIVERSE}
    me = {}
    for s, p in px.items():
        ds = sorted(p)
        for a, b in zip(ds, ds[1:] + [None]):
            if b is None or b.month != a.month:
                me.setdefault((a.year, a.month), {})[s] = a
    months = sorted(me)
    vol = {}
    for s, p in px.items():
        ds = sorted(p)
        r = [(b, p[b] / p[a] - 1) for a, b in zip(ds, ds[1:])]
        idx = {d: i for i, (d, _) in enumerate(r)}
        vol[s] = (r, idx)
    out, prev = {}, {}
    for i in range(13, len(months) - 1):
        m, nxt = months[i], months[i + 1]
        scores = {}
        for s in UNIVERSE:
            try:
                d0, d12, d1 = me[months[i - 12]][s], me[months[i - 1]][s], me[m][s]
                dn = me[nxt][s]
            except KeyError:
                continue
            r, idx = vol[s]
            j = idx.get(d1)
            if j is None or j < 60:
                continue
            sd = vs.sd([x for _, x in r[j - 59:j + 1]])
            scores[s] = (px[s][d12] / px[s][d0] - 1, sd, px[s][dn] / px[s][d1] - 1)
        if len(scores) < 8:
            continue
        ranked = sorted(scores, key=lambda s: scores[s][0])
        lo, hi = ranked[:3], ranked[-3:]
        pos = {}
        for leg, sign in ((hi, 1), (lo, -1)):
            inv = {s: 1 / scores[s][1] for s in leg}
            tot = sum(inv.values())
            for s in leg:
                pos[s] = sign * inv[s] / tot
        ret = sum(pos[s] * scores[s][2] for s in pos)
        turn = sum(abs(pos.get(s, 0) - prev.get(s, 0)) for s in set(pos) | set(prev))
        gross = sum(abs(v) for v in pos.values())
        out[nxt] = (ret - 2e-4 * turn - 0.02 / 12 * gross) * 1e4
        prev = pos
    ks = sorted(out)
    res = {}
    for label, a, b in (("primary_2013_2026_08", (2013, 1), (2026, 8)), ("secondary_2000_2012", (2000, 1), (2012, 12))):
        x = [out[k] for k in ks if a <= k <= b]
        t = vs.nw_t(x, 3)
        res[label] = {"n": len(x), "mean_bps_month_net": vs.mean(x), "t_hac": t, "p_one_sided": 1 - vs.N01.cdf(t),
                      "sharpe": vs.mean(x) / vs.sd(x) * math.sqrt(12)}
    p = res["primary_2013_2026_08"]
    res["verdict"] = ("CONFIRMED" if p["p_one_sided"] < 0.05 and p["mean_bps_month_net"] > 0 and res["secondary_2000_2012"]["mean_bps_month_net"] > 0
                      else "WEAK" if p["p_one_sided"] < 0.05 else "NOT CONFIRMED")
    res["dsr_N743"] = vs.deflated_sharpe([out[k] for k in ks if (2013, 1) <= k <= (2026, 8)], 743)
    print(json.dumps(res, indent=1))
    json.dump(res, open(os.path.join(OUT, "h1.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
