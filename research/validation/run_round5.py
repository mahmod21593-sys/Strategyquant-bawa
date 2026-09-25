"""Round-5 literature tests T1-T8 and implementability checks I2 (PREREGISTRATION.md amendment A9).

-> results/round5.json, results/series_round5.json
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import vstats as vs
from data_binance import klines
from data_histdata import NY, available_years, price, table
from run_round4 import hac_diff

OUT = os.path.join(os.path.dirname(__file__), "results")
BPS = 1e4
UTC = timezone.utc
TKY, SYD = ZoneInfo("Asia/Tokyo"), ZoneInfo("Australia/Sydney")
H30 = timedelta(minutes=30)
N_TRIALS = 64 + 8 + 653
SERIES = {}


def sign(x):
    return (x > 0) - (x < 0)


def summarize(key, rows, cost, lo, hi, boot=True):
    sel = [(d, x) for d, x in rows if lo <= d <= hi]
    res = vs.summarize([d for d, _ in sel], [x for _, x in sel], 1, 5, cost, boot=boot)
    if boot and sel:
        SERIES[key] = {"dates": [str(d) for d, _ in sel], "pnl_bps": [x for _, x in sel], "cost_bps": cost}
        res["dsr"] = vs.deflated_sharpe([x for _, x in sel], N_TRIALS) if len(sel) > 10 else None
    return res


def ny_min(dt):
    loc = dt.astimezone(NY)
    return loc.date(), loc.hour * 60 + loc.minute


def minutes_ny(hms):
    return {h * 60 + m + k for h, m in hms for k in range(-3, 4)}


# ---------------------------------------------------------------- session momentum (T1, T7)

ASIA_KEEP = set(range(0, 181)) | set(range(1380, 1440))  # NY 23:00-03:00 covers Tokyo and Sydney closes in every DST mix


def session_momentum(sym, close_fn, tz, years):
    """Baltussen rule: sign(prior close -> close-30) x (close-30 -> close). close_fn(d) -> (h, m) local."""
    if tz is NY:
        h, m = close_fn(date(2020, 1, 6))
        keep = minutes_ny([(h, m), ((h * 60 + m - 30) // 60, (h * 60 + m - 30) % 60)])
    else:
        keep = ASIA_KEEP
    tab = table(sym, years, keep)
    pts = []
    d = date(years[0], 1, 1)
    while d <= date(years[-1], 12, 31):
        if d.weekday() < 5:
            h, m = close_fn(d)
            c = datetime(d.year, d.month, d.day, h, m, tzinfo=tz)
            a = price(tab, *ny_min(c - H30))
            b = price(tab, *ny_min(c))
            if a and b:
                pts.append((d, a, b))
        d += timedelta(days=1)
    out = []
    for (d0, _, c0), (d1, a1, b1) in zip(pts, pts[1:]):
        if (d1 - d0).days <= 4 and sign(a1 / c0 - 1):
            out.append((d1, sign(a1 / c0 - 1) * (b1 / a1 - 1) * BPS))
    return out


def pooled(per, costs):
    g, c = {}, {}
    for sym, rows in per.items():
        for d, x in rows:
            g.setdefault(d, []).append(x)
            c.setdefault(d, []).append(costs[sym])
    ds = sorted(g)
    rows = [(d, vs.mean(g[d])) for d in ds]
    avg_cost = vs.mean([vs.mean(c[d]) for d in ds])
    return rows, avg_cost


def t1():
    specs = {"XAUUSD": (13, 30), "XAGUSD": (13, 25), "WTIUSD": (14, 30)}
    costs = {"XAUUSD": 2.5, "XAGUSD": 5.0, "WTIUSD": 4.0}
    per = {s: session_momentum(s, lambda d, hm=hm: hm, NY, available_years(s, range(2010, 2026))) for s, hm in specs.items()}
    rows, cost = pooled(per, costs)
    res = summarize("T1", rows, cost, date(2020, 6, 1), date(2025, 12, 31))
    res["in_paper_2011_2020_05"] = summarize("T1_pre", rows, cost, date(2011, 1, 1), date(2020, 5, 31), boot=False)
    res["per_instrument_primary"] = {s: summarize(s, r, costs[s], date(2020, 6, 1), date(2025, 12, 31), boot=False) for s, r in per.items()}
    res["brent_secondary"] = summarize("BCO", session_momentum("BCOUSD", lambda d: (14, 30), NY, available_years("BCOUSD", range(2010, 2026))),
                                       4.0, date(2020, 6, 1), date(2025, 12, 31), boot=False)
    res["cost_bps_avg"] = cost
    return res


def t7():
    jp = session_momentum("JPXJPY", lambda d: (15, 30) if d >= date(2024, 11, 5) else (15, 0), TKY, available_years("JPXJPY", range(2010, 2026)))
    au = session_momentum("AUXAUD", lambda d: (16, 0), SYD, available_years("AUXAUD", range(2010, 2026)))
    rows, cost = pooled({"JPXJPY": jp, "AUXAUD": au}, {"JPXJPY": 3.0, "AUXAUD": 3.0})
    res = summarize("T7", rows, cost, date(2020, 6, 1), date(2025, 12, 31))
    res["in_paper_2011_2020_05"] = summarize("T7_pre", rows, cost, date(2011, 1, 1), date(2020, 5, 31), boot=False)
    res["per_instrument_primary"] = {"JPXJPY": summarize("j", jp, 3.0, date(2020, 6, 1), date(2025, 12, 31), boot=False),
                                     "AUXAUD": summarize("a", au, 3.0, date(2020, 6, 1), date(2025, 12, 31), boot=False)}
    return res


# ---------------------------------------------------------------- crude oil (T2, T3)

def us_federal_holidays(y):
    def nth(month, weekday, n):
        d = date(y, month, 1)
        while d.weekday() != weekday:
            d += timedelta(days=1)
        return d + timedelta(days=7 * (n - 1))

    def last(month, weekday):
        d = date(y, month + 1, 1) - timedelta(days=1) if month < 12 else date(y, 12, 31)
        while d.weekday() != weekday:
            d -= timedelta(days=1)
        return d

    def observed(d):
        return d + timedelta(days=1) if d.weekday() == 6 else d - timedelta(days=1) if d.weekday() == 5 else d

    h = {observed(date(y, 1, 1)), nth(1, 0, 3), nth(2, 0, 3), last(5, 0), observed(date(y, 7, 4)), nth(9, 0, 1),
         nth(10, 0, 2), observed(date(y, 11, 11)), nth(11, 3, 4), observed(date(y, 12, 25))}
    if y >= 2021:
        h.add(observed(date(y, 6, 19)))
    return h


def oil_rows(sym, years, signal_window, rule_days=None):
    keep = minutes_ny([(10, 0), (10, 30), (11, 0), (15, 30), (16, 0)])
    tab = table(sym, years, keep)
    days = sorted(d for d in tab if d.weekday() < 5)
    close = {d: price(tab, d, 960) for d in days}
    out = []
    for d0, d in zip(days, days[1:]):
        if rule_days is not None and d not in rule_days:
            continue
        a_t, b_t = signal_window
        if a_t == "prev_close":
            a = close[d0] if (d - d0).days <= 4 else None
        else:
            a = price(tab, d, a_t)
        b = price(tab, d, b_t)
        p1530, p16 = price(tab, d, 930), close[d]
        if a and b and p1530 and p16 and sign(b / a - 1):
            out.append((d, sign(b / a - 1) * (p16 / p1530 - 1) * BPS))
    return out


def eia_wednesdays(y0, y1):
    out = set()
    for y in range(y0, y1 + 1):
        hol = us_federal_holidays(y) | us_federal_holidays(y + 1)
        d = date(y, 1, 1)
        while d.year == y:
            if d.weekday() == 2 and not any((d - timedelta(days=k)) in hol for k in range(3)):
                out.add(d)
            d += timedelta(days=1)
    return out


def t2():
    rows = oil_rows("WTIUSD", available_years("WTIUSD", range(2010, 2026)), ("prev_close", 600))
    res = summarize("T2", rows, 4.0, date(2019, 1, 1), date(2025, 12, 31))
    res["in_paper_period_2011_2018"] = summarize("T2_pre", rows, 4.0, date(2011, 1, 1), date(2018, 12, 31), boot=False)
    b = oil_rows("BCOUSD", available_years("BCOUSD", range(2010, 2026)), ("prev_close", 600))
    res["brent_secondary_2019_2025"] = summarize("b", b, 4.0, date(2019, 1, 1), date(2025, 12, 31), boot=False)
    res["data_note"] = "HistData serves WTIUSD only to 2023-12; the primary sample is therefore 2019-01 to 2023-12"
    return res


def t3():
    eia = eia_wednesdays(2010, 2025)
    rows = oil_rows("WTIUSD", available_years("WTIUSD", range(2010, 2026)), (630, 660), eia)
    res = summarize("T3", rows, 4.0, date(2019, 1, 1), date(2025, 12, 31))
    res["in_paper_period_2011_2018"] = summarize("T3_pre", rows, 4.0, date(2011, 1, 1), date(2018, 12, 31), boot=False)
    b = oil_rows("BCOUSD", available_years("BCOUSD", range(2010, 2026)), (630, 660), eia)
    res["brent_secondary_2019_2025"] = summarize("b", b, 4.0, date(2019, 1, 1), date(2025, 12, 31), boot=False)
    return res


# ---------------------------------------------------------------- crypto (T4, T5, T6)

_BTC = {}


def btc():
    if not _BTC:
        _BTC.update(klines("BTCUSDT", "30m", date(2017, 8, 1), date(2026, 8, 31)))
    return _BTC


def cpx(bars, t):
    """Crypto price at aware datetime t: close of the 30-min bar ending at t, else the open of the bar starting at t."""
    t = t.astimezone(UTC)
    b = bars.get(t - H30)
    if b:
        return b[3]
    b = bars.get(t)
    return b[0] if b else None


def t4():
    k = btc()
    out = []
    d = date(2017, 9, 1)
    while d <= date(2026, 8, 31):
        p = d - timedelta(days=1)
        a = cpx(k, datetime(p.year, p.month, p.day, 17, tzinfo=NY))
        b = cpx(k, datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY))
        c = cpx(k, datetime(d.year, d.month, d.day, 16, 30, tzinfo=NY))
        e = cpx(k, datetime(d.year, d.month, d.day, 17, tzinfo=NY))
        if a and b and c and e and sign(b / a - 1):
            out.append((d, sign(b / a - 1) * (e / c - 1) * BPS))
        d += timedelta(days=1)
    res = summarize("T4", out, 5.0, date(2021, 1, 1), date(2026, 8, 31))
    res["in_paper_period_2017_09_2020"] = summarize("T4_pre", out, 5.0, date(2017, 9, 1), date(2020, 12, 31), boot=False)
    return res


def t5():
    k = btc()
    out = []
    d = date(2017, 9, 1)
    while d <= date(2026, 8, 30):
        a = cpx(k, datetime(d.year, d.month, d.day, 22, tzinfo=UTC))
        n = d + timedelta(days=1)
        b = cpx(k, datetime(n.year, n.month, n.day, 0, tzinfo=UTC))
        if a and b:
            out.append((d, (b / a - 1) * BPS))
        d += timedelta(days=1)
    res = summarize("T5", out, 5.0, date(2022, 1, 1), date(2026, 8, 31))
    res["in_paper_period_2017_09_2021"] = summarize("T5_pre", out, 5.0, date(2017, 9, 1), date(2021, 12, 31), boot=False)
    allday = []
    d = date(2022, 1, 1)
    while d <= date(2026, 8, 30):
        a = cpx(k, datetime(d.year, d.month, d.day, tzinfo=UTC))
        n = d + timedelta(days=1)
        b = cpx(k, datetime(n.year, n.month, n.day, tzinfo=UTC))
        if a and b:
            allday.append((b / a - 1) * BPS / 12)
        d += timedelta(days=1)
    res["benchmark_mean_2h_drift_bps_post"] = vs.mean(allday)
    return res


def t6():
    k = btc()
    rows = []
    d = date(2018, 1, 1)
    while d <= date(2026, 8, 30):
        a = cpx(k, datetime(d.year, d.month, d.day, tzinfo=UTC))
        n = d + timedelta(days=1)
        b = cpx(k, datetime(n.year, n.month, n.day, tzinfo=UTC))
        if a and b:
            rows.append((d, (b / a - 1) * BPS, d.weekday() == 0))
        d += timedelta(days=1)
    res = hac_diff([x for _, x, _ in rows], [int(m) for *_, m in rows])
    res["mean_bps"] = res["diff_bps"]
    res["net_mean_bps"] = res["diff_bps"]
    return res


# ---------------------------------------------------------------- T8 crypto weekend -> Monday US500

def t8():
    k = btc()
    tab = table("SPXUSD", available_years("SPXUSD", range(2014, 2026)), set(range(1077, 1095)) | set(range(952, 962)))
    neg, sym_rows = [], []
    d = date(2018, 1, 1)
    while d <= date(2025, 12, 31):
        if d.weekday() == 0:
            fri, sun = d - timedelta(days=3), d - timedelta(days=1)
            a = cpx(k, datetime(fri.year, fri.month, fri.day, 16, tzinfo=NY))
            b = cpx(k, datetime(sun.year, sun.month, sun.day, 18, tzinfo=NY))
            s0 = price(tab, sun, 18 * 60, tol=10)
            s1 = price(tab, d, 960)
            if a and b and s0 and s1 and 959 in tab.get(d, {}):
                w = b / a - 1
                r = (s1 / s0 - 1) * BPS
                sym_rows.append((d, sign(w) * r))
                if w < 0:
                    neg.append((d, -r))
        d += timedelta(days=1)
    res = summarize("T8", neg, 1.5, date(2021, 1, 1), date(2025, 6, 30))
    res["backward_2018_2020"] = summarize("T8_pre", neg, 1.5, date(2018, 1, 1), date(2020, 12, 31), boot=False)
    res["symmetric_2021_2025_06"] = summarize("T8s", sym_rows, 1.5, date(2021, 1, 1), date(2025, 6, 30), boot=False)
    res["flag"] = "in-paper period: tests tradeability of a published effect, not out-of-sample persistence"
    return res


# ---------------------------------------------------------------- I2 MR-06 on JP225 / AUS200

def i2():
    out = {}
    for sym, tz, close_fn in (("JPXJPY", TKY, lambda d: (15, 30) if d >= date(2024, 11, 5) else (15, 0)),
                              ("AUXAUD", SYD, lambda d: (16, 0))):
        tab = table(sym, available_years(sym, range(2010, 2026)), ASIA_KEEP)
        days = []
        d = date(2011, 1, 1)
        while d <= date(2025, 12, 31):
            if d.weekday() < 5:
                h, m = close_fn(d)
                c = price(tab, *ny_min(datetime(d.year, d.month, d.day, h, m, tzinfo=tz)))
                e = price(tab, *ny_min(datetime(d.year, d.month, d.day, h, m, tzinfo=tz) - timedelta(minutes=5)))
                if c and e:
                    days.append((d, c, e))
            d += timedelta(days=1)
        yr = {}
        for (d0, c0, _), (d1, c1, _) in zip(days, days[1:]):
            yr.setdefault(d1.year, []).append((c1 / c0 - 1) * BPS)
        ym = {y: vs.mean(v) for y, v in yr.items()}
        rows = []
        for i in range(3, len(days) - 1):
            d, c, e = days[i]
            if e < days[i - 1][1] < days[i - 2][1] < days[i - 3][1]:
                nd, nc, _ = days[i + 1]
                rows.append((nd, (nc / e - 1) * BPS - ym[nd.year]))
        out[sym] = {"all_2011_2025": vs.summarize([d for d, _ in rows], [x for _, x in rows], 1, 5, 3.0, boot=False),
                    "2018_2025": vs.summarize([d for d, _ in rows if d.year >= 2018], [x for d, x in rows if d.year >= 2018], 1, 5, 3.0, boot=False)}
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"T1": t1(), "T2": t2(), "T3": t3(), "T4": t4(), "T5": t5(), "T6": t6(), "T7": t7(), "T8": t8()}
    fam = {k: v["p_one_sided"] for k, v in res.items()}
    holm, bh = vs.holm(fam), vs.bh(fam)
    for k, v in res.items():
        v["p_holm_T"], v["q_bh_T"] = holm[k], bh[k]
        m, net = v.get("mean_bps", v.get("diff_bps")), v.get("net_mean_bps", v.get("diff_bps"))
        ok = m > 0 and holm[k] < 0.05 and net > 0
        v["verdict"] = ("TRADEABLE IN-SAMPLE" if ok else "NOT TRADEABLE") if k == "T8" else \
            "CONFIRMED" if ok else "WEAK" if v["p_one_sided"] < 0.05 else "NOT CONFIRMED"
    res["I2"] = i2()
    json.dump(res, open(os.path.join(OUT, "round5.json"), "w"), indent=2, default=str)
    json.dump(SERIES, open(os.path.join(OUT, "series_round5.json"), "w"), default=str)
    for k, v in res.items():
        if k == "I2":
            for s, x in v.items():
                for p, y in x.items():
                    print(f"I2 {s} {p}: n={y['n']} mean={y['mean_bps']:.2f} net={y['net_mean_bps']:.2f} t={y['t_hac']:.2f}")
            continue
        m = v.get("mean_bps", v.get("diff_bps"))
        print(f"{k} {v['verdict']:20s} n={v['n']} mean={m:.2f} net={v.get('net_mean_bps', m):.2f} t={v['t_hac']:.2f} "
              f"p={v['p_one_sided']:.4f} holmT={v['p_holm_T']:.4f}")
        for sub, x in v.items():
            if isinstance(x, dict) and "mean_bps" in x and "n" in x:
                print(f"     {sub:32s} n={x['n']} mean={x['mean_bps']:.2f} t={x.get('t_hac', float('nan')):.2f} p={x.get('p_one_sided', float('nan')):.4f}")
            elif isinstance(x, dict) and all(isinstance(y, dict) for y in x.values()):
                for s, y in x.items():
                    if "mean_bps" in y:
                        print(f"     {sub}:{s:10s} n={y['n']} mean={y['mean_bps']:.2f} t={y['t_hac']:.2f}")


if __name__ == "__main__":
    main()
