"""Round 7, family G (PREREGISTRATION.md A15). -> results/round7.json, results/series_round7.json

    python3 run_round7.py            # all tests
    python3 run_round7.py G7 G10     # a subset (results are merged into round7.json)
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import vstats as vs
from data_binance import funding, klines
from data_histdata import NY, available_years, local_table
from data_yahoo import daily
from run_round4 import hac_diff, irx_map, tbill

OUT = os.path.join(os.path.dirname(__file__), "results")
BPS = 1e4
BER, LDN = ZoneInfo("Europe/Berlin"), ZoneInfo("Europe/London")
N_TRIALS = 742
SERIES = {}


# ---------------------------------------------------------------- helpers

def excess_daily(sym, rates=None, keys=None):
    """[(date, daily excess return)] from adjusted closes minus the T-bill accrual."""
    rows = daily(sym)
    if rates is None:
        rates = irx_map()
        keys = sorted(rates)
    out = []
    for a, b in zip(rows, rows[1:]):
        out.append((b["date"], b["adj"] / a["adj"] - 1 - tbill(rates, keys, a["date"], b["date"])))
    return out


def ols_alpha(y, x, lag):
    """OLS y = a + b x with a Newey-West (Bartlett) t for a."""
    n = len(y)
    mx, my = vs.mean(x), vs.mean(y)
    b = sum((u - mx) * (v - my) for u, v in zip(x, y)) / sum((u - mx) ** 2 for u in x)
    a = my - b * mx
    g = [(v - a - b * u, (v - a - b * u) * u) for u, v in zip(x, y)]  # x_t * e_t with x_t = (1, u)

    def gamma(k):
        return [[sum(g[t][i] * g[t - k][j] for t in range(k, n)) for j in range(2)] for i in range(2)]

    S = gamma(0)
    for k in range(1, lag + 1):
        w, G = 1 - k / (lag + 1), gamma(k)
        S = [[S[i][j] + w * (G[i][j] + G[j][i]) for j in range(2)] for i in range(2)]
    sx, sxx = sum(x), sum(u * u for u in x)
    det = n * sxx - sx * sx
    inv = [[sxx / det, -sx / det], [-sx / det, n / det]]
    V = [[sum(inv[i][k] * S[k][l] * inv[l][j] for k in range(2) for l in range(2)) for j in range(2)] for i in range(2)]
    return {"alpha": a, "beta": b, "t_alpha": a / math.sqrt(V[0][0]), "n": n}


def verdict_stats(key, dates, pnl, cost=0.0, sign=1, lag=5):
    res = vs.summarize(dates, pnl, sign, lag, cost)
    SERIES[key] = {"dates": [str(d) for d in dates], "pnl_bps": pnl, "cost_bps": cost}
    if len(pnl) >= 10:
        res["dsr_N742"] = vs.deflated_sharpe([v - cost for v in pnl], N_TRIALS)
    return res


def split(dates, pnl, lo, hi, cost=0.0, sign=1, lag=5):
    sel = [(d, x) for d, x in zip(dates, pnl) if lo <= d <= hi]
    return vs.summarize([d for d, _ in sel], [x for _, x in sel], sign, lag, cost, boot=False)


def per_year(dates, pnl):
    g = {}
    for d, x in zip(dates, pnl):
        g.setdefault(d.year, []).append(x)
    return {y: round(vs.mean(v), 2) for y, v in sorted(g.items())}


def pool(per):
    g = {}
    for rows in per.values():
        for d, v in rows:
            g.setdefault(d, []).append(v)
    ds = sorted(g)
    return ds, [vs.mean(g[d]) for d in ds]


def third_friday(y, m):
    d = date(y, m, 15)
    return d + timedelta(days=(4 - d.weekday()) % 7)


# ---------------------------------------------------------------- G1 Halloween

def g1():
    ex = [(d, x * BPS) for d, x in excess_daily("SPY")]
    out = {}
    for label, lo, hi in (("primary_2002_11_2026_08", date(2002, 11, 1), date(2026, 8, 31)),
                          ("secondary_1993_2002_10", date(1993, 2, 1), date(2002, 10, 31))):
        sel = [(d, x) for d, x in ex if lo <= d <= hi]
        r = hac_diff([x for _, x in sel], [d.month in (11, 12, 1, 2, 3, 4) for d, _ in sel], 5)
        r["winter_minus_summer_bps_per_day"] = r.pop("diff_bps")
        r["mean_winter_bps"], r["mean_summer_bps"] = r.pop("mean_even_bps"), r.pop("mean_odd_bps")
        out[label] = r
    res = dict(out["primary_2002_11_2026_08"])
    res["secondary_1993_2002_10"] = out["secondary_1993_2002_10"]
    yr = {}
    for d, x in ex:
        if d >= date(2002, 11, 1):
            season = d.year + (1 if d.month >= 11 else 0)  # winter Nov(y-1)..Apr(y) and summer May..Oct(y) share label y
            yr.setdefault(season, {"w": [], "s": []})["w" if d.month in (11, 12, 1, 2, 3, 4) else "s"].append(x)
    res["per_season_year_winter_minus_summer"] = {y: round(vs.mean(v["w"]) - vs.mean(v["s"]), 2) for y, v in sorted(yr.items())
                                                  if v["w"] and v["s"]}
    res["secondary_ok"] = out["secondary_1993_2002_10"]["winter_minus_summer_bps_per_day"] > 0
    return res


# ---------------------------------------------------------------- G2, G3 option-expiration weeks

def weekly_excess():
    rows = daily("SPY")
    rates = irx_map()
    keys = sorted(rates)
    last = {}
    for r in rows:
        k = r["date"].isocalendar()[:2]
        last[k] = r  # last trading day of each ISO week
    wk = sorted(last)
    out = []
    for a, b in zip(wk, wk[1:]):
        ra, rb = last[a], last[b]
        out.append((b, rb["date"], rb["adj"] / ra["adj"] - 1 - tbill(rates, keys, ra["date"], rb["date"])))
    return out


def g2_g3():
    w = weekly_excess()
    opex = {third_friday(y, m).isocalendar()[:2] for y in range(1993, 2027) for m in range(1, 13)}
    post = set()
    for y in range(1993, 2027):
        for m in range(1, 13):
            post.add((third_friday(y, m) + timedelta(days=7)).isocalendar()[:2])
    lo, hi = date(2011, 1, 1), date(2026, 8, 31)
    sel = [(k, d, x * BPS) for k, d, x in w if lo <= d <= hi]
    g2 = hac_diff([x for _, _, x in sel], [k in opex for k, _, _ in sel], 2)
    g2["opex_minus_other_bps_per_week"] = g2.pop("diff_bps")
    non = [(k, d, x) for k, d, x in sel if k not in opex]
    g3 = hac_diff([x for _, _, x in non], [k in post for k, _, _ in non], 2)
    g3["post_opex_minus_other_bps_per_week"] = g3.pop("diff_bps")
    g3["p_one_sided"] = 1 - g3["p_one_sided"]  # predicted negative
    pre = [(k, d, x * BPS) for k, d, x in w if date(1993, 2, 1) <= d <= date(2010, 12, 31)]
    g2["secondary_1993_2010"] = hac_diff([x for _, _, x in pre], [k in opex for k, _, _ in pre], 2)
    pn = [(k, d, x) for k, d, x in pre if k not in opex]
    g3["secondary_1993_2010"] = hac_diff([x for _, _, x in pn], [k in post for k, _, _ in pn], 2)
    return g2, g3


# ---------------------------------------------------------------- G4 MR-06 by VIX regime

def g4():
    spx = daily("^GSPC")
    vix = {r["date"]: r["c"] for r in daily("^VIX")}
    vdates = sorted(vix)
    idx = {d: i for i, d in enumerate(vdates)}
    trades = []
    for i in range(3, len(spx) - 1):
        c = [spx[i - k]["c"] for k in range(4)]
        d = spx[i]["date"]
        if not (c[0] < c[1] < c[2] < c[3]) or d < date(1990, 1, 1) or d > date(2026, 8, 31) or d not in idx:
            continue
        j = idx[d]
        if j < 252:
            continue
        hist = sorted(vix[x] for x in vdates[j - 252:j])
        med = (hist[125] + hist[126]) / 2
        r = (spx[i + 1]["c"] / spx[i]["c"] - 1) * BPS
        trades.append((d, r, vix[d] > med))
    res = hac_diff([r for _, r, _ in trades], [h for _, _, h in trades], 5)
    res["high_minus_low_vix_bps"] = res.pop("diff_bps")
    res["mean_high_vix_bps"], res["mean_low_vix_bps"] = res.pop("mean_even_bps"), res.pop("mean_odd_bps")
    late = [(d, r, h) for d, r, h in trades if d >= date(2011, 1, 1)]
    res["secondary_2011_on"] = hac_diff([r for _, r, _ in late], [h for _, _, h in late], 5)
    res["secondary_ok"] = res["secondary_2011_on"]["diff_bps"] > 0
    # sizing view (post hoc, not in the verdict): trade return per unit of prior 20-day volatility
    return res


# ---------------------------------------------------------------- G5 volatility-managed index

def g5():
    ex = excess_daily("SPY")
    months = {}
    for d, x in ex:
        months.setdefault((d.year, d.month), []).append(x)
    keys = [k for k in sorted(months) if k <= (2026, 8)]
    f = {k: math.prod(1 + v for v in months[k]) - 1 for k in keys}
    rv = {k: sum(v * v for v in months[k]) for k in keys}
    pairs = [(keys[i], keys[i - 1]) for i in range(1, len(keys))]

    def managed(c):
        return {k: min(2.0, c / rv[p]) for k, p in pairs}

    cal = [k for k, _ in pairs if (1993, 3) <= k <= (2015, 12)]
    target = vs.sd([f[k] for k in cal])
    lo, hi = 1e-7, 1e-1
    for _ in range(100):
        c = math.sqrt(lo * hi)
        w = managed(c)
        if vs.sd([w[k] * f[k] for k in cal]) < target:
            lo = c
        else:
            hi = c
    w = managed(c)
    net = {}
    for k, p in pairs:
        turn = abs(w[k] - w.get(p, w[k])) if p in w else 0.0
        net[k] = w[k] * f[k] - 1e-4 * turn
    post = [k for k, _ in pairs if (2016, 1) <= k <= (2026, 8)]
    y = [net[k] for k in post]
    x = [f[k] for k in post]
    reg = ols_alpha(y, x, 3)
    res = {"n_months": len(post), "c": c, "alpha_monthly": reg["alpha"], "alpha_annual_pct": reg["alpha"] * 1200, "beta": reg["beta"],
           "t_hac": reg["t_alpha"], "p_one_sided": 1 - vs.N01.cdf(reg["t_alpha"]),
           "sharpe_managed": vs.mean(y) / vs.sd(y) * math.sqrt(12), "sharpe_unmanaged": vs.mean(x) / vs.sd(x) * math.sqrt(12),
           "mean_weight": vs.mean([w[k] for k in post]), "share_capped": vs.mean([w[k] >= 2.0 for k in post])}
    pre = [k for k, _ in pairs if (1993, 3) <= k <= (2015, 12)]
    rp = ols_alpha([net[k] for k in pre], [f[k] for k in pre], 3)
    res["in_sample_1993_2015"] = {"alpha_annual_pct": rp["alpha"] * 1200, "t_hac": rp["t_alpha"]}
    return res


# ---------------------------------------------------------------- G6 time-series momentum

G6_UNIVERSE = ["SPY", "QQQ", "DIA", "IWM", "EWG", "EWU", "EWJ", "GLD", "SLV", "USO", "FXE", "FXY", "FXB", "FXA", "FXC", "FXF", "BTC-USD"]


def g6():
    rates = irx_map()
    keys = sorted(rates)
    data = {}
    for s in G6_UNIVERSE:
        ex = excess_daily(s, rates, keys)
        ann = 365 if s == "BTC-USD" else 261
        delta = 60 / 61
        m = v = None
        rows = []
        for d, x in ex:
            if m is None:
                m, v = x, x * x
            else:
                m = delta * m + (1 - delta) * x
                v = delta * v + (1 - delta) * (x - m) ** 2
            rows.append((d, x, math.sqrt(v * ann)))
        data[s] = rows
    # month-end positions
    month_end = {}
    for s, rows in data.items():
        for i, (d, _, _) in enumerate(rows):
            if i + 1 == len(rows) or rows[i + 1][0].month != d.month:
                month_end.setdefault((d.year, d.month), {})[s] = i
    ms = sorted(month_end)
    port, prev_pos = {}, {}
    for a, b in zip(ms, ms[1:]):
        rets, turn = [], []
        pos_now = {}
        for s, i in month_end[a].items():
            rows = data[s]
            if i < 300 or s not in month_end[b]:
                continue
            j = month_end[b][s]
            past = math.prod(1 + x for _, x, _ in rows[i - 251:i + 1]) - 1
            sig = 1 if past > 0 else -1
            w = 0.40 / rows[i][2] if rows[i][2] > 0 else 0.0
            nxt = math.prod(1 + x for _, x, _ in rows[i + 1:j + 1]) - 1
            pos_now[s] = sig * w
            rets.append(sig * w * nxt)
            turn.append(abs(sig * w - prev_pos.get(s, 0.0)))
        if rets:
            port[b] = vs.mean(rets) - 2e-4 * vs.mean(turn)
        prev_pos = pos_now
    ds = [date(y, m, 28) for (y, m) in sorted(port)]
    xs = [port[k] * BPS for k in sorted(port)]
    main = split(ds, xs, date(2012, 1, 1), date(2026, 8, 31), lag=3)
    sec = split(ds, xs, date(2007, 1, 1), date(2011, 12, 31), lag=3)
    SERIES["G6"] = {"dates": [str(d) for d in ds], "pnl_bps": xs}
    main["sharpe_annual"] = main["mean_bps"] / main["sd_bps"] * math.sqrt(12)
    main["secondary_2007_2011"] = sec
    main["secondary_ok"] = sec.get("mean_bps", -1) > 0
    main["per_year_bps_per_month"] = per_year([d for d in ds if d.year >= 2007], [x for d, x in zip(ds, xs) if d.year >= 2007])
    return main


# ---------------------------------------------------------------- HistData sessions (corrected clock)

def sessions(sym, tz, open_hm, close_hm, years):
    o, c = open_hm[0] * 60 + open_hm[1], close_hm[0] * 60 + close_hm[1]
    tab = local_table(sym, years, tz, set(range(o - 61, c + 1)))
    return tab, o, c


def px(bars, m):
    if m - 1 in bars:
        return bars[m - 1][3]
    if m in bars:
        return bars[m][0]
    if m - 2 in bars:
        return bars[m - 2][3]
    return None


def full_days(tab, o, c):
    return sorted(d for d, b in tab.items() if d.weekday() < 5 and o in b and c - 1 in b and len(b) > 0.8 * (c - o))


YEARS = list(range(2013, 2027))
US = (("SPXUSD", NY), ("NSXUSD", NY))
TRIO = (("SPXUSD", NY, (9, 30), (16, 0)), ("NSXUSD", NY, (9, 30), (16, 0)), ("GRXEUR", BER, (9, 0), (17, 30)))


def hist_result(key, per, cost, lo=date(2014, 1, 1), hi=date(2025, 12, 31)):
    """cost: bps per trade, a number or {symbol: bps} (then averaged over the symbols trading each date)."""
    ds, ps = pool(per)
    if isinstance(cost, dict):
        c = {}
        for sym, rows in per.items():
            for d, _ in rows:
                c.setdefault(d, []).append(cost[sym])
        cost = vs.mean([vs.mean(c[d]) for d in ds if lo <= d <= hi])
    sel = [(d, x) for d, x in zip(ds, ps) if lo <= d <= hi]
    res = verdict_stats(key, [d for d, _ in sel], [x for _, x in sel], cost)
    res["holdout_2026"] = split(ds, ps, date(2026, 1, 1), date(2026, 12, 31), cost=cost)
    res["secondary_ok"] = res["holdout_2026"].get("net_mean_bps", -1) > 0
    res["cost_bps_avg"] = cost
    res["per_instrument"] = {s: vs.summarize([d for d, _ in v if lo <= d <= hi], [x for d, x in v if lo <= d <= hi], 1, 5, cost, boot=False)
                             for s, v in per.items()}
    res["per_year_bps"] = per_year([d for d, _ in sel], [x for _, x in sel])
    res["trades_per_year"] = len(sel) / 12
    return res


# ---------------------------------------------------------------- G7 last-hour reversal

def g7():
    per = {}
    for sym, tz in US:
        tab, o, c = sessions(sym, tz, (9, 30), (16, 0), available_years(sym, YEARS))
        days = full_days(tab, o, c)
        lh = []
        for d in days:
            a, b = px(tab[d], 900), px(tab[d], 960)
            lh.append((d, (b / a - 1) if a and b else None, b))
        out = []
        for i in range(1, len(lh) - 1):
            d, r, p = lh[i]
            nd, _, pn = lh[i + 1]
            if r is None or p is None or pn is None or (nd - d).days > 5:
                continue
            hist = [abs(x) for _, x, _ in lh[max(0, i - 250):i] if x is not None]
            if len(hist) < 100:
                continue
            thr = sorted(hist)[int(0.67 * len(hist))]
            if abs(r) >= thr and r != 0:
                s = -1 if r > 0 else 1
                out.append((nd, s * (pn / p - 1) * BPS))
        per[sym] = out
    return hist_result("G7", per, 1.5)


# ---------------------------------------------------------------- G8 Asian-range breakout (London)

def g8():
    per = {}
    for sym in ("EURUSD", "GBPUSD"):
        tab = local_table(sym, available_years(sym, YEARS), LDN, set(range(0, 961)))
        out = []
        for d in sorted(tab):
            if d.weekday() >= 5:
                continue
            b = tab[d]
            rng = [b[m] for m in range(0, 420) if m in b]
            if len(rng) < 0.8 * 420:
                continue
            hi, lo = max(v[1] for v in rng), min(v[2] for v in rng)
            pos = entry = None
            for m in range(420, 720):
                v = b.get(m)
                if v is None:
                    continue
                if v[1] >= hi and v[2] <= lo:
                    break
                if v[1] >= hi:
                    pos, entry, start = 1, hi, m
                    break
                if v[2] <= lo:
                    pos, entry, start = -1, lo, m
                    break
            if pos is None:
                continue
            exit_px = None
            for m in range(start + 1, 960):
                v = b.get(m)
                if v is None:
                    continue
                if pos == 1 and v[2] <= lo:
                    exit_px = lo
                    break
                if pos == -1 and v[1] >= hi:
                    exit_px = hi
                    break
            if exit_px is None:
                exit_px = px(b, 960)
            if exit_px is None:
                continue
            out.append((d, pos * (exit_px / entry - 1) * BPS))
        per[sym] = out
    return hist_result("G8", per, {"EURUSD": 1.0, "GBPUSD": 1.5})


# ---------------------------------------------------------------- G10, G11 index breakouts

def breakout(nr7):
    per = {}
    for sym, tz, oh, ch in TRIO:
        tab, o, c = sessions(sym, tz, oh, ch, available_years(sym, YEARS))
        days = full_days(tab, o, c)
        info = []
        for d in days:
            b = tab[d]
            vals = [b[m] for m in range(o, c) if m in b]
            info.append((d, max(v[1] for v in vals), min(v[2] for v in vals)))
        out = []
        for i in range(7, len(days)):
            d = days[i]
            pd, ph, pl = info[i - 1]
            if (d - pd).days > 5:
                continue
            b = tab[d]
            op, cl = px(b, o), px(b, c)
            if not op or not cl:
                continue
            if nr7:
                ranges = [h - l for _, h, l in info[i - 7:i]]
                if ph - pl > min(ranges):
                    continue
                up, dn = ph, pl
            else:
                up, dn = op + 0.5 * (ph - pl), op - 0.5 * (ph - pl)
            pos = entry = None
            if op >= up:
                pos, entry = 1, op
            elif op <= dn:
                pos, entry = -1, op
            else:
                for m in range(o, c):
                    v = b.get(m)
                    if v is None:
                        continue
                    if v[1] >= up and v[2] <= dn:
                        break
                    if v[1] >= up:
                        pos, entry = 1, up
                        break
                    if v[2] <= dn:
                        pos, entry = -1, dn
                        break
            if pos is None:
                continue
            out.append((d, pos * (cl / entry - 1) * BPS))
        per[sym] = out
    return hist_result("G11" if nr7 else "G10", per, 1.5)


# ---------------------------------------------------------------- G9 crypto funding

def g9():
    per, longonly = {}, {}
    for sym in ("BTCUSDT", "ETHUSDT"):
        fr = funding(sym, date(2020, 1, 1), date(2026, 8, 31))
        k = klines(sym, "1d", date(2020, 1, 1), date(2026, 9, 1))
        close = {t.date(): v[3] for t, v in k.items()}
        days = sorted(close)
        sig = {}
        j = 0
        for d in days:
            cut = datetime(d.year, d.month, d.day, tzinfo=timezone.utc) + timedelta(days=1)
            window = [r for t, r in fr if cut - timedelta(days=7) < t <= cut]
            if len(window) >= 15:
                sig[d] = vs.mean(window)
        sd_ = sorted(sig)
        out, lo_rows = [], []
        prev = 0
        for i, d in enumerate(sd_):
            if i < 365:
                continue
            nd = d + timedelta(days=1)
            if nd not in close or d not in close:
                continue
            hist = sorted(sig[x] for x in sd_[i - 365:i])
            med = (hist[182] + hist[183]) / 2
            pos = 1 if sig[d] <= med else -1
            r = (close[nd] / close[d] - 1) * BPS
            out.append((nd, pos * r - (5.0 if pos != prev and prev != 0 else 0.0)))
            lo_rows.append((nd, r))
            prev = pos
        per[sym] = out
        longonly[sym] = lo_rows
    ds, ps = pool(per)
    lo = date(2021, 1, 1)
    sel = [(d, x) for d, x in zip(ds, ps) if lo <= d <= date(2026, 8, 31)]
    res = verdict_stats("G9", [d for d, _ in sel], [x for _, x in sel], 0.0)
    ld, lp = pool(longonly)
    res["long_only_benchmark"] = split(ld, lp, lo, date(2026, 8, 31))
    res["per_instrument"] = {s: split([d for d, _ in v], [x for _, x in v], lo, date(2026, 8, 31)) for s, v in per.items()}
    res["per_year_bps"] = per_year([d for d, _ in sel], [x for _, x in sel])
    res["note"] = "Binance publishes funding files from 2020-01, so the 365-day median window starts the test in 2021-01 (A15 amendment)"
    return res


TESTS = {"G1": g1, "G4": g4, "G5": g5, "G6": g6, "G7": g7, "G8": g8, "G9": g9, "G10": lambda: breakout(False),
         "G11": lambda: breakout(True)}


def main(only):
    path = os.path.join(OUT, "round7.json")
    res = json.load(open(path)) if os.path.exists(path) and only else {}
    for k, fn in TESTS.items():
        if only and k not in only:
            continue
        res[k] = fn()
        print(k, {x: (round(v, 4) if isinstance(v, float) else v) for x, v in res[k].items() if not isinstance(v, (dict, list))}, flush=True)
        json.dump(res, open(path, "w"), indent=1, default=str)
    if not only or "G2" in only:
        res["G2"], res["G3"] = g2_g3()
        for k in ("G2", "G3"):
            print(k, {x: (round(v, 4) if isinstance(v, float) else v) for x, v in res[k].items() if not isinstance(v, (dict, list))}, flush=True)
    json.dump(res, open(path, "w"), indent=1, default=str)
    sp = os.path.join(OUT, "series_round7.json")
    old = json.load(open(sp)) if os.path.exists(sp) and only else {}
    old.update(SERIES)
    json.dump(old, open(sp, "w"), default=str)


def verdicts():
    path = os.path.join(OUT, "round7.json")
    res = json.load(open(path))
    fam = {k: v["p_one_sided"] for k, v in res.items() if k.startswith("G") and "p_one_sided" in v}
    holm, bh = vs.holm(fam), vs.bh(fam)
    tradeable = {"G6", "G7", "G8", "G9", "G10", "G11"}
    for k, v in res.items():
        if k not in fam:
            continue
        v["p_holm_G"], v["q_bh_G"] = holm[k], bh[k]
        net_ok = v.get("net_mean_bps", 1) > 0 if k in tradeable else True
        sec_ok = v.get("secondary_ok", True)
        v["verdict"] = ("CONFIRMED" if holm[k] < 0.05 and net_ok and sec_ok else "WEAK" if v["p_one_sided"] < 0.05 else "NOT CONFIRMED")
        print(f"{k:4s} {v['verdict']:14s} p={v['p_one_sided']:.4f} holm={holm[k]:.4f} net_ok={net_ok} secondary_ok={sec_ok}")
    json.dump(res, open(path, "w"), indent=1, default=str)


if __name__ == "__main__":
    if sys.argv[1:] == ["verdicts"]:
        verdicts()
    else:
        main(set(sys.argv[1:]))
