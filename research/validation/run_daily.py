"""Primary tests on daily data (P1-P6, P16-P19). Specs are fixed in PREREGISTRATION.md.

Usage: YAHOO_CACHE=... python3 run_daily.py  -> results/daily.json
"""
from __future__ import annotations

import json
import math
import os
import random
from datetime import date

import vstats as vs
from data_yahoo import daily

OUT = os.path.join(os.path.dirname(__file__), "results")
BPS = 1e4
IDX_COST, ETF_COST = 1.5, 2.0
NON_US = ["^GDAXI", "^FTSE", "^FCHI", "^N225", "^STOXX50E", "^AXJO", "^HSI", "^GSPTSE", "^SSMI"]
ALL_IDX = ["^GSPC", "^NDX", "^DJI", "^RUT"] + NON_US
ETFS = ["SPY", "QQQ", "IWM", "EFA", "EEM", "EWJ", "TLT", "IEF", "SHY", "LQD", "HYG", "GLD", "SLV", "USO", "UNG",
        "DBC", "DBA", "UUP", "FXE", "FXY", "FXB", "FXA", "FXC", "FXF", "VNQ"]


def load(sym, start=None, real_hl=False):
    rows = daily(sym)
    if real_hl:
        first = next(i for i, r in enumerate(rows) if r["h"] > r["l"])
        rows = rows[first:]
    if start:
        rows = [r for r in rows if r["date"] >= start]
    return rows


def yearly_mean_ret(rows, key="c"):
    g = {}
    for a, b in zip(rows, rows[1:]):
        g.setdefault(b["date"].year, []).append((b[key] / a[key] - 1) * BPS)
    return {y: vs.mean(v) for y, v in g.items()}


def sma(vals, n):
    out, s = [None] * len(vals), 0.0
    for i, v in enumerate(vals):
        s += v
        if i >= n:
            s -= vals[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def split(dates, pnl, cut: date):
    a = [(d, p) for d, p in zip(dates, pnl) if d < cut]
    b = [(d, p) for d, p in zip(dates, pnl) if d >= cut]
    return a, b


def block(dates, pnl, sign=1, lag=5, cost=0.0, cuts=(), boot=True):
    res = vs.summarize(dates, pnl, sign, lag, cost, boot=boot)
    res["splits"] = []
    edges = [None, *cuts, None]
    for lo, hi in zip(edges, edges[1:]):
        sel = [(d, p) for d, p in zip(dates, pnl) if (lo is None or d >= lo) and (hi is None or d < hi)]
        if len(sel) >= 10:
            s = vs.summarize([d for d, _ in sel], [p for _, p in sel], sign, lag, cost, boot=False)
            s["from"] = str(lo) if lo else "start"
            s["to"] = str(hi) if hi else "end"
            res["splits"].append(s)
    return res


def ibs_trades(rows):
    closes = [r["c"] for r in rows]
    s200 = sma(closes, 200)
    base = yearly_mean_ret(rows)
    dates, pnl, signal_days = [], [], []
    for t in range(len(rows) - 1):
        r, nx = rows[t], rows[t + 1]
        if s200[t] is None or r["h"] <= r["l"]:
            continue
        up = r["c"] > s200[t]
        ibs = (r["c"] - r["l"]) / (r["h"] - r["l"])
        excess = (nx["c"] / r["c"] - 1) * BPS - base[nx["date"].year]
        if up:
            signal_days.append((nx["date"], excess, ibs, r["date"]))
        if up and ibs < 0.2:
            dates.append(nx["date"])
            pnl.append(excess)
    return dates, pnl, signal_days


def regime_randomization(obs_mean, pool, k):
    vals = [p for _, p, _, _ in pool]
    return vs.randomization_p(obs_mean, lambda rng: vs.mean(rng.sample(vals, k)), reps=5000)


def p1():
    rows = load("^GSPC", date(1990, 1, 1))
    d, p, pool = ibs_trades(rows)
    res = block(d, p, cost=IDX_COST, cuts=(date(2014, 1, 1),))
    res["randomization_p"] = regime_randomization(vs.mean(p), pool, len(p))
    return res, (d, p, pool)


def by_date_average(trade_lists):
    g = {}
    for d, p in trade_lists:
        g.setdefault(d, []).append(p)
    ds = sorted(g)
    return ds, [vs.mean(g[x]) for x in ds]


def p2():
    pooled, per = [], {}
    for s in NON_US:
        rows = load(s, real_hl=True)
        d, p, _ = ibs_trades(rows)
        pooled += list(zip(d, p))
        per[s] = vs.summarize(d, p, 1, 5, IDX_COST, boot=False)
    ds, ps = by_date_average(pooled)
    res = block(ds, ps, cost=IDX_COST, cuts=(date(2014, 1, 1),))
    res["per_index"] = per
    return res


def p3():
    trades = []
    for s in ["^GSPC", "^NDX"]:
        rows = load(s, date(1990, 1, 1))
        closes = [r["c"] for r in rows]
        s200 = sma(closes, 200)
        base = yearly_mean_ret(rows)
        t = 5
        while t < len(rows) - 3:
            if s200[t] is not None and closes[t] < min(closes[t - 5:t]) and closes[t] > s200[t]:
                ex = (closes[t + 3] / closes[t] - 1) * BPS - 3 * base[rows[t + 3]["date"].year]
                trades.append((rows[t + 3]["date"], ex))
                t += 3
            t += 1
    trades.sort()
    return block([d for d, _ in trades], [p for _, p in trades], cost=IDX_COST, cuts=(date(2014, 1, 1),))


def p4():
    port, per = [], {}
    for s in ALL_IDX:
        rows = load(s, date(1999, 12, 1))
        d, p = [], []
        pos_prev = 0
        for a, b, c in zip(rows, rows[1:], rows[2:]):
            if b["date"] < date(2000, 1, 1):
                continue
            r_prev = b["c"] / a["c"] - 1
            pos = -1 if r_prev > 0 else (1 if r_prev < 0 else 0)
            gross = pos * (c["c"] / b["c"] - 1) * BPS
            cost = 0.75 * abs(pos - pos_prev) * IDX_COST / 1.5  # 0.75 bps per unit of position change
            pos_prev = pos
            d.append(c["date"])
            p.append(gross - cost)
        per[s] = vs.summarize(d, p, 1, 5, 0.0, boot=False)
        port += list(zip(d, p))
    ds, ps = by_date_average(port)
    res = block(ds, ps, cost=0.0, cuts=(date(2017, 1, 1),))
    res["note"] = "P&L already net of 0.75 bps per unit of position change (1.5 bps per flip)"
    res["per_index"] = per
    return res


def tom_flags(rows):
    months = {}
    for i, r in enumerate(rows):
        months.setdefault((r["date"].year, r["date"].month), []).append(i)
    flag = set()
    for idx in months.values():
        flag.update(idx[:3])
        flag.add(idx[-1])
    return flag


def p5():
    rows = load("^GSPC", date(1970, 1, 1))
    flag = tom_flags(rows)
    other = {}
    for i in range(1, len(rows)):
        if i not in flag:
            other.setdefault(rows[i]["date"].year, []).append((rows[i]["c"] / rows[i - 1]["c"] - 1) * BPS)
    base = {y: vs.mean(v) for y, v in other.items()}
    d, p = [], []
    for i in range(1, len(rows)):
        if i in flag:
            d.append(rows[i]["date"])
            p.append((rows[i]["c"] / rows[i - 1]["c"] - 1) * BPS - base[rows[i]["date"].year])
    return block(d, p, cost=0.0, cuts=(date(2001, 1, 1),))


def ewma_sigma(rets, com=60.0):
    dlt = com / (com + 1)
    m = v = None
    out = []
    for r in rets:
        if m is None:
            m, v = r, r * r
        else:
            m = dlt * m + (1 - dlt) * r
            v = dlt * v + (1 - dlt) * (r - m) ** 2
        out.append(math.sqrt(261 * v))
    return out


def p6():
    data = {}
    for s in ETFS:
        rows = daily(s)
        rets = [0.0] + [b["adj"] / a["adj"] - 1 for a, b in zip(rows, rows[1:])]
        sig = ewma_sigma(rets)
        month_end = {}
        for i, r in enumerate(rows):
            month_end[(r["date"].year, r["date"].month)] = i
        data[s] = (rows, sig, month_end)
    months = sorted({k for _, _, me in data.values() for k in me})
    months = [m for m in months if m >= (2006, 12)]
    tsmom, bh, dates, turnover = [], [], [], []
    prev_pos = {}
    for m0, m1 in zip(months, months[1:]):
        rs, bs, turn = [], [], []
        for s, (rows, sig, me) in data.items():
            if m0 not in me or m1 not in me:
                continue
            i0 = me[m0]
            y0 = (m0[0] - 1, m0[1])
            if y0 not in me or i0 < 90 or sig[i0] <= 0:
                continue
            past = rows[i0]["adj"] / rows[me[y0]]["adj"] - 1
            nxt = rows[me[m1]]["adj"] / rows[i0]["adj"] - 1
            lev = 0.40 / sig[i0]
            pos = (1 if past > 0 else -1) * lev
            rs.append(pos * nxt)
            bs.append(lev * nxt)
            turn.append(abs(pos - prev_pos.get(s, 0.0)))
            prev_pos[s] = pos
        if len(rs) >= 5 and m0 >= (2007, 1):
            dates.append(date(m1[0], m1[1], 28))
            cost = 5.0 / BPS * vs.mean(turn)
            tsmom.append((vs.mean(rs) - cost) * BPS)
            bh.append(vs.mean(bs) * BPS)
            turnover.append(vs.mean(turn))
    res = block(dates, tsmom, lag=3, cost=0.0, cuts=(date(2013, 1, 1), date(2020, 1, 1)))
    res["note"] = "monthly P&L in bps of capital, net of 5 bps x turnover; 40% vol target per instrument, equal weight"
    res["sharpe_annual"] = vs.mean(tsmom) / vs.sd(tsmom) * math.sqrt(12)
    res["vol_scaled_buy_hold_sharpe_annual"] = vs.mean(bh) / vs.sd(bh) * math.sqrt(12)
    diff = [a - b for a, b in zip(tsmom, bh)]
    res["tsmom_minus_scaled_bh"] = vs.summarize(dates, diff, 1, 3, 0.0, boot=False)
    return res


def month_end_index(rows):
    me = {}
    for i, r in enumerate(rows):
        me[(r["date"].year, r["date"].month)] = i
    return me


def p16():
    spy, tlt = daily("SPY"), daily("TLT")
    tmap = {r["date"]: r for r in tlt}
    spy = [r for r in spy if r["date"] in tmap and r["date"] >= date(2002, 8, 1)]
    tl = [tmap[r["date"]] for r in spy]
    me = month_end_index(spy)
    keys = sorted(me)
    spreads, d, p = [], [], []
    for k0, k1 in zip(keys, keys[1:]):
        i0, i1 = me[k0], me[k1]
        s = (spy[i1]["adj"] / spy[i0]["adj"] - 1) - (tl[i1]["adj"] / tl[i0]["adj"] - 1)
        if len(spreads) >= 36 and i1 + 1 < len(spy):
            z = s / vs.sd(spreads[-36:])
            pos = -max(-2.0, min(2.0, z))
            nxt = (spy[i1 + 1]["adj"] / spy[i1]["adj"] - 1) * BPS
            d.append(spy[i1 + 1]["date"])
            p.append(pos * nxt - ETF_COST * abs(pos))
        spreads.append(s)
    res = block(d, p, lag=1, cost=0.0, cuts=(date(2023, 4, 1),))
    res["note"] = "P&L net of 2 bps x |position|"
    return res


def p17():
    trades = []
    for s in ["SPY", "QQQ"]:
        rows = [r for r in daily(s) if r["date"] >= date(1999, 3, 10)]
        for a, b in zip(rows, rows[1:]):
            trades.append((b["date"], (b["o"] / a["c"] - 1) * BPS, (b["c"] / b["o"] - 1) * BPS))
    ds, on = by_date_average([(d, x) for d, x, _ in trades])
    _, intra = by_date_average([(d, y) for d, _, y in trades])
    res = block(ds, on, cost=ETF_COST, cuts=(date(2013, 1, 1),))
    res["intraday_open_to_close"] = vs.summarize(ds, intra, 1, 5, 0.0, boot=False)
    res["note"] = "price (not dividend-adjusted) opens/closes; ex-dividend gaps fall overnight, biasing overnight returns DOWN"
    return res


def p18():
    rows = load("^GSPC", date(1970, 1, 1))
    base = yearly_mean_ret(rows)
    d, p = [], []
    for a, b, c in zip(rows, rows[1:], rows[2:]):
        gap = (c["date"] - b["date"]).days
        normal = 3 if b["date"].weekday() == 4 else 1
        if gap > normal:
            d.append(b["date"])
            p.append((b["c"] / a["c"] - 1) * BPS - base[b["date"].year])
    return block(d, p, cost=IDX_COST, cuts=(date(2001, 1, 1),))


def p19(pool):
    vix = {r["date"]: r["c"] for r in daily("^VIX")}
    vdates = sorted(vix)
    vvals = [vix[x] for x in vdates]
    pos = {x: i for i, x in enumerate(vdates)}
    hi, lo = [], []
    for nd, excess, ibs, sd_ in pool:
        if ibs >= 0.2 or sd_ not in pos or pos[sd_] < 252:
            continue
        i = pos[sd_]
        window = sorted(vvals[i - 252:i])
        pct = sum(v <= vix[sd_] for v in window) / 252
        if pct >= 2 / 3:
            hi.append(excess)
        elif pct < 1 / 3:
            lo.append(excess)
    diff = vs.mean(hi) - vs.mean(lo)
    se = math.sqrt(vs.sd(hi) ** 2 / len(hi) + vs.sd(lo) ** 2 / len(lo))
    t = diff / se
    return {"n_high": len(hi), "n_low": len(lo), "mean_high_bps": vs.mean(hi), "mean_low_bps": vs.mean(lo),
            "diff_bps": diff, "t_welch": t, "p_one_sided": vs.p_one_sided(t), "note": "VIX tercile vs trailing 252 days"}


def main():
    os.makedirs(OUT, exist_ok=True)
    out = {}
    r1, (_, _, pool) = p1()
    out["P1"] = r1
    out["P2"] = p2()
    out["P3"] = p3()
    out["P4"] = p4()
    out["P5"] = p5()
    out["P6"] = p6()
    out["P16"] = p16()
    out["P17"] = p17()
    out["P18"] = p18()
    out["P19"] = p19(pool)
    json.dump(out, open(os.path.join(OUT, "daily.json"), "w"), indent=2, default=str)
    for k, v in out.items():
        print(k, {x: (round(y, 4) if isinstance(y, float) else y) for x, y in v.items()
                  if x in ("n", "mean_bps", "net_mean_bps", "t_hac", "p_one_sided", "years_pred_sign", "sharpe_annual",
                           "diff_bps", "t_welch", "randomization_p")})
        for s in v.get("splits", []):
            print("   ", s["from"], "->", s["to"], "n", s["n"], "mean", round(s["mean_bps"], 2), "t", round(s["t_hac"], 2),
                  "p", round(s["p_one_sided"], 4))


if __name__ == "__main__":
    main()
