"""Round 4 tests S1-S7 and implementability check I1 (PREREGISTRATION.md amendment A8).

-> results/round4.json, results/series_round4.json
"""
from __future__ import annotations

import bisect
import json
import math
import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import vstats as vs
from data_calendar import fomc_days, treasury_auctions
from data_fred import series as fred
from data_histdata import NY, available_years, price, table
from data_yahoo import daily

OUT = os.path.join(os.path.dirname(__file__), "results")
BPS = 1e4
LDN = ZoneInfo("Europe/London")
N_TRIALS = 64
SERIES = {}


def summarize(key, dates, pnl, cost, lag=5, boot=True):
    res = vs.summarize(dates, pnl, 1, lag, cost, boot=boot)
    if boot:
        SERIES[key] = {"dates": [str(d) for d in dates], "pnl_bps": pnl, "cost_bps": cost, "lag": lag}
        res["dsr_N64"] = vs.deflated_sharpe(pnl, N_TRIALS) if len(pnl) > 10 else None
    return res


def window(rows, lo, hi, cost, lag=5):
    sel = [(d, x) for d, x in rows if lo <= d <= hi]
    return vs.summarize([d for d, _ in sel], [x for _, x in sel], 1, lag, cost, boot=False)


def sign(x):
    return (x > 0) - (x < 0)


# ---------------------------------------------------------------- S1 FOMC cycle

def hac_diff(r, dummy, lag=5):
    """Even-minus-odd mean difference with a Newey-West t (influence function of the dummy regression)."""
    n = len(r)
    n1 = sum(dummy)
    p = n1 / n
    m1 = sum(x for x, d in zip(r, dummy) if d) / n1
    m0 = sum(x for x, d in zip(r, dummy) if not d) / (n - n1)
    psi = [(x - (m1 if d else m0)) * (d / p - (1 - d) / (1 - p)) for x, d in zip(r, dummy)]
    s = sum(v * v for v in psi) / n
    for k in range(1, lag + 1):
        w = 1 - k / (lag + 1)
        s += 2 * w * sum(psi[i] * psi[i - k] for i in range(k, n)) / n
    se = math.sqrt(s / n)
    t = (m1 - m0) / se
    return {"n": n, "n_even": n1, "mean_even_bps": m1, "mean_odd_bps": m0, "diff_bps": m1 - m0, "t_hac": t,
            "p_one_sided": 1 - vs.N01.cdf(t)}


def fomc_week_days():
    rows = [r for r in daily("^GSPC") if r["date"] >= date(1993, 12, 1)]
    fomc = fomc_days()
    wd, d = {}, date(1993, 1, 4)
    k = 0
    while d <= date(2027, 12, 31):
        if d.weekday() < 5:
            wd[d] = k
            k += 1
        d += timedelta(days=1)
    out = []
    for a, b in zip(rows, rows[1:]):
        t = b["date"]
        if t < date(1994, 1, 1):
            continue
        prev = [f for f in fomc if f <= t]
        nxt = [f for f in fomc if f > t]
        day = None
        if nxt and wd[t] - wd[nxt[0]] >= -6:
            day = wd[t] - wd[nxt[0]]
        elif prev:
            day = wd[t] - wd[prev[-1]]
        if day is None or day > 33:
            continue
        week = (day + 1) // 5
        out.append((t, (b["c"] / a["c"] - 1) * BPS, week % 2 == 0))
    return out


def s1():
    rows = fomc_week_days()

    def part(lo, hi):
        x = [(d, r, e) for d, r, e in rows if lo <= d <= hi]
        return hac_diff([r for _, r, _ in x], [int(e) for _, _, e in x])

    res = part(date(2017, 1, 1), date(2026, 12, 31))
    res["net_mean_bps"] = res["diff_bps"]  # a difference of means; the trading version carries the cost
    res["in_paper_1994_2016"] = part(date(1994, 1, 1), date(2016, 12, 31))
    res["uppal_2004_2016"] = part(date(2004, 1, 1), date(2016, 12, 31))
    # trading version: long on even-week days only, 1.5 bps per switch
    tr, prev_e = [], False
    for d, r, e in rows:
        c = 1.5 if e != prev_e else 0.0
        prev_e = e
        tr.append((d, (r if e else 0.0) - c))
    post = [(d, x) for d, x in tr if d >= date(2017, 1, 1)]
    bh = [r for d, r, _ in rows if d >= date(2017, 1, 1)]
    res["trading_post"] = {"mean_bps_per_day_net": vs.mean([x for _, x in post]), "buy_hold_mean_bps_per_day": vs.mean(bh),
                           "even_share": sum(e for d, _, e in rows if d >= date(2017, 1, 1)) / len(bh)}
    SERIES["S1"] = {"dates": [str(d) for d, _, _ in rows], "ret_bps": [r for _, r, _ in rows], "even": [e for *_, e in rows]}
    return res


# ---------------------------------------------------------------- S2 Treasury end of month

def irx_map():
    return {r["date"]: r["c"] / 100 for r in daily("^IRX")}


def tbill(rates, keys, d0, d1):
    i = bisect.bisect_right(keys, d0) - 1
    rf = rates[keys[max(i, 0)]]
    return rf * (d1 - d0).days / 360


def month_ends(rows):
    ends = []
    for i in range(len(rows) - 1):
        if rows[i + 1]["date"].month != rows[i]["date"].month:
            ends.append(i)
    return ends  # the last month in the data is excluded (not known to be complete)


def eom(sym, t=3, cost=2.0):
    rows = daily(sym)
    rates = irx_map()
    keys = sorted(rates)
    out, other = [], []
    ends = month_ends(rows)
    for k, e in enumerate(ends):
        s = e - t
        if s < 1:
            continue
        ex = rows[e]["adj"] / rows[s]["adj"] - 1 - tbill(rates, keys, rows[s]["date"], rows[e]["date"])
        out.append((rows[e]["date"], ex * BPS))
        if k > 0:
            b = ends[k - 1]
            ex2 = rows[s]["adj"] / rows[b]["adj"] - 1 - tbill(rates, keys, rows[b]["date"], rows[s]["date"])
            other.append((rows[e]["date"], ex2 * BPS))
    return out, other


def s2():
    ief, ief_other = eom("IEF")
    tlt, _ = eom("TLT")
    post = [(d, x) for d, x in ief if d >= date(2019, 1, 1)]
    res = summarize("S2", [d for d, _ in post], [x for _, x in post], 2.0)
    res["in_paper_2002_2018"] = window(ief, date(2002, 8, 1), date(2018, 12, 31), 2.0)
    res["rest_of_month_post"] = window(ief_other, date(2019, 1, 1), date(2026, 12, 31), 0.0)
    res["tlt_post"] = window(tlt, date(2019, 1, 1), date(2026, 12, 31), 2.0)
    res["tlt_in_paper"] = window(tlt, date(2002, 8, 1), date(2018, 12, 31), 2.0)
    return res


# ---------------------------------------------------------------- S3 auction cycle

def auction_events(term, sym="IEF"):
    rows = daily(sym)
    idx = {r["date"]: i for i, r in enumerate(rows)}
    ends = set()
    for e in month_ends(rows):
        ends |= {rows[e - j]["date"] for j in range(3)}
    out = []
    for a in treasury_auctions(term):
        i = idx.get(a)
        if i is None or i < 6 or i + 5 >= len(rows):
            continue
        pre = rows[i - 1]["adj"] / rows[i - 6]["adj"] - 1
        post = rows[i + 5]["adj"] / rows[i]["adj"] - 1
        touches_eom = any(rows[j]["date"] in ends for j in range(i - 6, i + 6))
        out.append((a, (post - pre) * BPS, touches_eom))
    return out


def s3():
    ev10 = auction_events("10-Year")
    ev5 = auction_events("5-Year")
    prim = [(d, x) for d, x, _ in ev10 if d >= date(2013, 9, 1)]
    res = summarize("S3", [d for d, _ in prim], [x for _, x in prim], 4.0)
    res["in_paper_2002_2008"] = window([(d, x) for d, x, _ in ev10], date(2002, 8, 1), date(2008, 12, 31), 4.0)
    res["five_year_post"] = window([(d, x) for d, x, _ in ev5], date(2013, 9, 1), date(2026, 12, 31), 4.0)
    res["excluding_month_end_windows_post"] = window([(d, x) for d, x, t in ev10 if not t], date(2013, 9, 1), date(2026, 12, 31), 4.0)
    res["n_events_touching_month_end_post"] = sum(1 for d, _, t in ev10 if t and d >= date(2013, 9, 1))
    return res


# ---------------------------------------------------------------- S4, S5 month-end fix

def easter(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(y, month, day)


def uk_holidays(y):
    h = {easter(y) - timedelta(days=2), easter(y) + timedelta(days=1)}
    last_mon = lambda m: max(date(y, m, d) for d in range(1, 32) if _valid(y, m, d) and date(y, m, d).weekday() == 0)
    if y not in (2002, 2012, 2022):  # spring bank holiday moved for jubilees
        h.add(last_mon(5))
    h.add(last_mon(8))
    c = [date(y, 12, 25), date(y, 12, 26)]
    for x in c:
        h.add(x)
    if date(y, 12, 25).weekday() == 5:
        h |= {date(y, 12, 27), date(y, 12, 28)}
    elif date(y, 12, 25).weekday() == 6:
        h |= {date(y, 12, 27)}
    elif date(y, 12, 26).weekday() == 5:
        h |= {date(y, 12, 28)}
    return h


def _valid(y, m, d):
    try:
        date(y, m, d)
        return True
    except ValueError:
        return False


def fix_day(y, m):
    hol = uk_holidays(y)
    d = date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)
    while d.weekday() >= 5 or d in hol:
        d -= timedelta(days=1)
    return d


EQ = {"US": "^GSPC", "EUR": "^STOXX50E", "JPY": "^N225", "GBP": "^FTSE", "CAD": "^GSPTSE", "AUD": "^AXJO",
      "CHF": "^SSMI", "SEK": "^OMX", "NOK": "OSEBX.OL", "NZD": "^NZ50"}
FXP = {"EUR": ("EURUSD", False), "GBP": ("GBPUSD", False), "AUD": ("AUDUSD", False), "NZD": ("NZDUSD", False),
       "JPY": ("USDJPY", True), "CHF": ("USDCHF", True), "CAD": ("USDCAD", True), "SEK": ("USDSEK", True), "NOK": ("USDNOK", True)}


def close_on_or_before(rows, d, strict=False):
    keys = [r["date"] for r in rows]
    i = (bisect.bisect_left(keys, d) if strict else bisect.bisect_right(keys, d)) - 1
    return rows[i] if i >= 0 else None


def ny_min(dt):
    loc = dt.astimezone(NY)
    return loc.date(), loc.hour * 60 + loc.minute


def s4_s5():
    eq = {k: daily(v) for k, v in EQ.items()}
    gdaxi = daily("^GDAXI")
    stoxx_start = eq["EUR"][0]["date"]
    keep = set(range(5 * 60 + 50, 8 * 60 + 11)) | set(range(8 * 60 + 50, 12 * 60 + 11))
    months = [(y, m) for y in range(2004, 2026) for m in range(1, 13) if (y, m) >= (2004, 5)]
    fix = {ym: fix_day(*ym) for ym in [(2004, 4)] + months}
    fx, cover = {}, {}
    for c, (sym, base) in FXP.items():
        yrs = available_years(sym, range(2004, 2027))
        fx[c] = (table(sym, yrs, keep), base)
        cover[c] = [yrs[0], yrs[-1]] if yrs else None
    per4, per5, pairs4 = {}, {}, {}
    prev = (2004, 4)
    for ym in months:
        T, T0 = fix[ym], fix[prev]
        prev = ym

        def eret(k):
            rows = eq[k]
            if k == "EUR" and T0 < stoxx_start:
                rows = gdaxi
            a, b = close_on_or_before(rows, T0), close_on_or_before(rows, T, strict=True)
            if not a or not b or a["date"] >= b["date"] or (T0 - a["date"]).days > 7 or (T - b["date"]).days > 7:
                return None
            return b["c"] / a["c"] - 1

        eu = eret("US")
        if eu is None:
            continue
        nxt = T + timedelta(days=1)
        while nxt.weekday() >= 5:
            nxt += timedelta(days=1)
        v4, v5 = [], []
        for c, (tab, base) in fx.items():
            ec = eret(c)
            if ec is None or ec == eu:
                continue
            p15 = price(tab, *ny_min(datetime(T.year, T.month, T.day, 15, tzinfo=LDN)), tol=10)
            p16 = price(tab, *ny_min(datetime(T.year, T.month, T.day, 16, tzinfo=LDN)), tol=10)
            p12 = price(tab, *ny_min(datetime(nxt.year, nxt.month, nxt.day, 12, tzinfo=LDN)), tol=10)
            s = -1 if base else 1  # sign converting the pair's log return into "currency c strengthens vs USD"
            pos = -sign(ec - eu)
            if p15 and p16:
                x = pos * s * math.log(p16 / p15) * BPS
                v4.append(x)
                pairs4.setdefault(c, []).append((T, x))
            if p16 and p12:
                v5.append(-pos * s * math.log(p12 / p16) * BPS)
        if v4:
            per4[T] = vs.mean(v4)
        if v5:
            per5[T] = vs.mean(v5)
    out = {}
    for key, per, name in (("S4", per4, "hour before the fix"), ("S5", per5, "fix to next-day noon")):
        allr = sorted(per.items())
        post = [(d, x) for d, x in allr if d >= date(2013, 1, 1)]
        r = summarize(key, [d for d, _ in post], [x for _, x in post], 1.0)
        r["in_paper_2004_2012"] = window(allr, date(2004, 5, 1), date(2012, 12, 31), 1.0)
        r["post_reform_2015_02"] = window(allr, date(2015, 2, 1), date(2025, 12, 31), 1.0)
        r["window"] = name
        out[key] = r
    out["S4"]["per_pair_post"] = {c: window(v, date(2013, 1, 1), date(2025, 12, 31), 1.0) for c, v in pairs4.items()}
    out["S4"]["fx_coverage"] = cover
    return out


# ---------------------------------------------------------------- S6 rebalancing (Calendar signal)

def s6():
    spy = {r["date"]: r["adj"] for r in daily("SPY")}
    ief = {r["date"]: r["adj"] for r in daily("IEF")}
    ds = sorted(set(spy) & set(ief))
    rs = {d: spy[d] / spy[p] - 1 for p, d in zip(ds, ds[1:])}
    rb = {d: ief[d] / ief[p] - 1 for p, d in zip(ds, ds[1:])}
    last = {ds[i] for i in range(len(ds) - 1) if ds[i + 1].month != ds[i].month}
    # position of each day within the month's last five trading days
    in_last5 = set()
    month_days = {}
    for d in ds:
        month_days.setdefault((d.year, d.month), []).append(d)
    for (y, m), dd in month_days.items():
        if dd[-1] in last:
            in_last5 |= set(dd[-5:])
    w, sig = None, {}
    for p, d in zip(ds, ds[1:]):
        if w is None:
            if p not in last:
                continue
            w = 0.60
        w = w * (1 + rs[d]) / (w * (1 + rs[d]) + (1 - w) * (1 + rb[d]))
        sig[d] = w - 0.60
        if d in last:
            w = 0.60
    spread, spy_only = [], []
    for p, d in zip(ds, ds[1:]):
        if p in sig and p in in_last5 and sign(sig[p]):
            spread.append((d, -sign(sig[p]) * (rs[d] - rb[d]) * BPS))
            spy_only.append((d, -sign(sig[p]) * rs[d] * BPS))
    res = summarize("S6", [d for d, _ in spread], [x for _, x in spread], 1.0)
    res["in_paper_to_2023_03_17"] = window(spread, date(2002, 8, 1), date(2023, 3, 17), 1.0)
    res["post_2023_03_18"] = window(spread, date(2023, 3, 18), date(2026, 12, 31), 1.0)
    res["spy_only"] = window(spy_only, date(2002, 8, 1), date(2026, 12, 31), 1.0)
    res["spy_only_post"] = window(spy_only, date(2023, 3, 18), date(2026, 12, 31), 1.0)
    return res


# ---------------------------------------------------------------- S7 bond reversal, 1962-2001

def bond_returns():
    y = [(d, v / 100) for d, v in fred("DGS10") if d <= date(2001, 12, 31)]
    out = []
    for (d0, y0), (d1, y1) in zip(y, y[1:]):
        dur = (1 - (1 + y0 / 2) ** -20) / y0
        out.append((d1, -dur * (y1 - y0) + y0 / 252))
    return out


def s7():
    r = bond_returns()
    g = {}
    for d, x in r:
        g.setdefault(d.year, []).append(x)
    base = {k: vs.mean(v) for k, v in g.items()}
    ev = [(r[i + 1][0], (r[i + 1][1] - base[r[i + 1][0].year]) * BPS) for i in range(2, len(r) - 1)
          if r[i][1] < 0 and r[i - 1][1] < 0 and r[i - 2][1] < 0]
    res = summarize("S7", [d for d, _ in ev], [x for _, x in ev], 0.5)
    res["1962_1989"] = window(ev, date(1962, 1, 1), date(1989, 12, 31), 0.5)
    res["1990_2001"] = window(ev, date(1990, 1, 1), date(2001, 12, 31), 0.5)
    tl = daily("TLT")
    rr = [(b["date"], b["adj"] / a["adj"] - 1) for a, b in zip(tl, tl[1:])]
    g = {}
    for d, x in rr:
        g.setdefault(d.year, []).append(x)
    base = {k: vs.mean(v) for k, v in g.items()}
    ev2 = [(rr[i + 1][0], (rr[i + 1][1] - base[rr[i + 1][0].year]) * BPS) for i in range(2, len(rr) - 1)
           if rr[i][1] < 0 and rr[i - 1][1] < 0 and rr[i - 2][1] < 0]
    res["comparison_tlt_2002_on_seen_in_Q4"] = window(ev2, date(2002, 8, 1), date(2026, 12, 31), 2.0)
    return res


# ---------------------------------------------------------------- I1 MR-06 volatility-scaled size

def i1():
    import prop_mr06_minute as pm
    from implementability import rate_map
    from run_histdata import RTH, us_days
    rates = rate_map()
    rk = sorted(rates)
    tr = pm.trades("SPXUSD", rates, rk)  # {exit date: (pnl, low, high)}
    tab = table("SPXUSD", range(2014, 2026), RTH)
    days = us_days(tab)
    close = {d: price(tab, d, 960) for d in days}
    ret = {b: close[b] / close[a] - 1 for a, b in zip(days, days[1:]) if close[a] and close[b]}
    nxt = {a: b for a, b in zip(days, days[1:])}
    prev_of = {b: a for a, b in zip(days, days[1:])}
    size = {}
    for exit_d in tr:
        sig_d = prev_of[exit_d]
        i = days.index(sig_d)
        hist = [ret[x] for x in days[max(1, i - 20):i] if x in ret]  # up to the day before the signal day
        size[exit_d] = min(2.0, 0.01 / vs.sd(hist)) if len(hist) >= 10 else 1.0
    scale = 1 / vs.mean(list(size.values()))
    scaled = {d: tuple(v * size[d] * scale for v in tr[d]) for d in tr}
    out = {"mean_size_before_normalising": 1 / scale,
           "fixed": pm.simulate({"SPXUSD": tr}, levs=(2, 4))["prop_two_step_10_5"],
           "vol_scaled": pm.simulate({"SPXUSD": scaled}, levs=(2, 4))["prop_two_step_10_5"],
           "fixed_mean_sd_bps": [vs.mean([v[0] for v in tr.values()]) * BPS, vs.sd([v[0] for v in tr.values()]) * BPS],
           "scaled_mean_sd_bps": [vs.mean([v[0] for v in scaled.values()]) * BPS, vs.sd([v[0] for v in scaled.values()]) * BPS]}
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"S1": s1(), "S2": s2(), "S3": s3(), **s4_s5(), "S6": s6(), "S7": s7()}
    fam = {k: v["p_one_sided"] for k, v in res.items()}
    holm, bh = vs.holm(fam), vs.bh(fam)
    for k, v in res.items():
        v["p_holm_S"], v["q_bh_S"] = holm[k], bh[k]
        net = v.get("net_mean_bps", v.get("diff_bps"))
        mean = v.get("mean_bps", v.get("diff_bps"))
        ok = mean > 0 and holm[k] < 0.05 and net > 0
        if k == "S6":
            ok = ok and v["post_2023_03_18"].get("mean_bps", -1) > 0
        v["verdict"] = "CONFIRMED" if ok else "WEAK" if v["p_one_sided"] < 0.05 else "NOT CONFIRMED"
    res["I1"] = i1()
    json.dump(res, open(os.path.join(OUT, "round4.json"), "w"), indent=2, default=str)
    json.dump(SERIES, open(os.path.join(OUT, "series_round4.json"), "w"), default=str)
    for k, v in res.items():
        if k == "I1":
            print("I1", json.dumps(v, default=str))
            continue
        mean = v.get("mean_bps", v.get("diff_bps"))
        print(f"{k} {v['verdict']:14s} n={v['n']} mean={mean:.2f} net={v.get('net_mean_bps', mean):.2f} t={v['t_hac']:.2f} "
              f"p={v['p_one_sided']:.4f} holmS={v['p_holm_S']:.4f}")
        for sub, x in v.items():
            if isinstance(x, dict) and ("mean_bps" in x or "diff_bps" in x):
                m = x.get("mean_bps", x.get("diff_bps"))
                print(f"     {sub:34s} n={x['n']} mean={m:.2f} t={x['t_hac']:.2f} p={x['p_one_sided']:.4f}")


if __name__ == "__main__":
    main()
