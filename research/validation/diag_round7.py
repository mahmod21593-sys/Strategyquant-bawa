"""Round 7 post-hoc diagnostics (labelled post hoc in the report). -> results/round7_diagnostics.json"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import vstats as vs
import run_round7 as r7

OUT = os.path.join(os.path.dirname(__file__), "results")


def tsmom(universe, mode):
    """mode: 'tsmom' (pre-registered G6), 'long' (same weights, always long), 'timing' (tsmom - long)."""
    rates = r7.irx_map()
    keys = sorted(rates)
    data = {}
    for s in universe:
        ex = r7.excess_daily(s, rates, keys)
        ann = 365 if s == "BTC-USD" else 261
        delta, m, v, rows = 60 / 61, None, None, []
        for d, x in ex:
            if m is None:
                m, v = x, x * x
            else:
                m = delta * m + (1 - delta) * x
                v = delta * v + (1 - delta) * (x - m) ** 2
            rows.append((d, x, math.sqrt(v * ann)))
        data[s] = rows
    month_end = {}
    for s, rows in data.items():
        for i, (d, _, _) in enumerate(rows):
            if i + 1 == len(rows) or rows[i + 1][0].month != d.month:
                month_end.setdefault((d.year, d.month), {})[s] = i
    ms = sorted(month_end)
    port, prev = {}, {}
    for a, b in zip(ms, ms[1:]):
        rets, turn, now = [], [], {}
        for s, i in month_end[a].items():
            rows = data[s]
            if i < 300 or s not in month_end[b]:
                continue
            j = month_end[b][s]
            past = math.prod(1 + x for _, x, _ in rows[i - 251:i + 1]) - 1
            sig = 1 if past > 0 else -1
            if mode == "long":
                sig = 1
            w = 0.40 / rows[i][2] if rows[i][2] > 0 else 0.0
            nxt = math.prod(1 + x for _, x, _ in rows[i + 1:j + 1]) - 1
            if mode == "timing":
                rets.append((sig - 1) * w * nxt)
            else:
                rets.append(sig * w * nxt)
            now[s] = sig * w
            turn.append(abs(sig * w - prev.get(s, 0.0)))
        if rets:
            port[b] = vs.mean(rets) - (2e-4 * vs.mean(turn) if mode != "timing" else 0.0)
        prev = now
    ks = [k for k in sorted(port) if (2012, 1) <= k <= (2026, 8)]
    x = [port[k] * 1e4 for k in ks]
    t = vs.nw_t(x, 3)
    return {"n": len(x), "mean_bps_month": vs.mean(x), "t_hac": t, "sharpe": vs.mean(x) / vs.sd(x) * math.sqrt(12)}, dict(zip(ks, x))


def main():
    res = {}
    full = r7.G6_UNIVERSE
    for label, uni in (("all", full), ("ex_btc", [s for s in full if s != "BTC-USD"]),
                       ("ex_equity", [s for s in full if s not in ("SPY", "QQQ", "DIA", "IWM", "EWG", "EWU", "EWJ")]),
                       ("equity_only", ["SPY", "QQQ", "DIA", "IWM", "EWG", "EWU", "EWJ"]),
                       ("fx_only", ["FXE", "FXY", "FXB", "FXA", "FXC", "FXF"]),
                       ("commodities_only", ["GLD", "SLV", "USO"])):
        res[label] = {}
        for mode in ("tsmom", "long", "timing"):
            res[label][mode], ser = tsmom(uni, mode)
            if label == "all":
                res[label][mode + "_series"] = {f"{k[0]}-{k[1]:02d}": v for k, v in ser.items()}
        print(label, {m: {k: round(v, 2) for k, v in res[label][m].items()} for m in ("tsmom", "long", "timing")}, flush=True)
    # correlation of G6 with SPY monthly excess
    spy = r7.excess_daily("SPY")
    mo = {}
    for d, x in spy:
        mo.setdefault((d.year, d.month), []).append(x)
    s = res["all"]["tsmom_series"]
    ks = [k for k in s if (int(k[:4]), int(k[5:])) in mo]
    a = [s[k] for k in ks]
    b = [(math.prod(1 + v for v in mo[(int(k[:4]), int(k[5:]))]) - 1) * 1e4 for k in ks]
    ma, mb = vs.mean(a), vs.mean(b)
    cov = sum((u - ma) * (v - mb) for u, v in zip(a, b)) / len(a)
    res["corr_with_spy"] = cov / (vs.sd(a) * vs.sd(b))
    print("corr with SPY", round(res["corr_with_spy"], 3))
    json.dump(res, open(os.path.join(OUT, "round7_diagnostics.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
