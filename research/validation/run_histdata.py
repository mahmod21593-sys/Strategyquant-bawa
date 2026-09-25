"""Round 2 minute-data tests on HistData (PREREGISTRATION.md A3, A4, A5): Q7 (the original P7-P14) and Q6 (FX W1 + W4).

-> results/histdata.json, results/series_histdata.json
"""
from __future__ import annotations

import json
import math
import os
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import vstats as vs
from data_histdata import NY, available_years, price, table

OUT = os.path.join(os.path.dirname(__file__), "results")
BPS = 1e4
BER, LDN, UTC = ZoneInfo("Europe/Berlin"), ZoneInfo("Europe/London"), timezone.utc
SERIES = {}
YEARS_IDX = range(2014, 2026)
YEARS_FX = range(2004, 2024)
FX_END = date(2023, 9, 30)


def sign(x):
    return (x > 0) - (x < 0)


def block(key, dates, pnl, cut, cost, lag=5, pred=1):
    res = vs.summarize(dates, pnl, pred, lag, cost)
    SERIES[key] = {"dates": [str(d) for d in dates], "pnl_bps": pnl, "cost_bps": cost, "lag": lag}
    pre = [(d, p) for d, p in zip(dates, pnl) if d < cut]
    post = [(d, p) for d, p in zip(dates, pnl) if d >= cut]
    res["pre"] = vs.summarize([d for d, _ in pre], [p for _, p in pre], pred, lag, cost, boot=False)
    res["post_publication"] = vs.summarize([d for d, _ in post], [p for _, p in post], pred, lag, cost, boot=False)
    res["post_publication"]["from"] = str(cut)
    res["breakeven_cost_bps"] = res["mean_bps"] * pred
    return res


def pool(per):
    g = {}
    for rows in per.values():
        for d, v in rows:
            g.setdefault(d, []).append(v)
    ds = sorted(g)
    return ds, [vs.mean(g[d]) for d in ds]


# ---------------------------------------------------------------- US indices (P7-P11, P13, P14)

RTH = set(range(570, 961))  # bars starting 09:30 .. 16:00
EARLY = set(range(115, 186))  # 01:55 .. 03:05


def us_days(tab):
    return sorted(d for d, b in tab.items() if d.weekday() < 5 and 570 in b and 959 in b)


def us_rows(tab):
    """Per regular day: prior close, 10:00, 15:30 and 16:00 prices, next day's 16:00 price."""
    days = us_days(tab)
    rows = []
    for i in range(1, len(days)):
        d, pd = days[i], days[i - 1]
        pc, p10, p1530, p16 = price(tab, pd, 960), price(tab, d, 600), price(tab, d, 930), price(tab, d, 960)
        nxt = price(tab, days[i + 1], 960) if i + 1 < len(days) else None
        if pc and p10 and p1530 and p16:
            rows.append({"date": d, "rod": p1530 / pc - 1, "r1": p10 / pc - 1, "lh": p16 / p1530 - 1,
                         "next": (nxt / p16 - 1) if nxt else None})
    return rows


def p7_p9_p13(rows):
    p7 = [(r["date"], sign(r["rod"]) * r["lh"] * BPS) for r in rows if sign(r["rod"])]
    p8 = [(r["date"], sign(r["r1"]) * r["lh"] * BPS) for r in rows if sign(r["r1"])]
    p9 = []
    for i in range(60, len(rows)):
        thr = vs.sd([x["rod"] for x in rows[i - 60:i]])
        r = rows[i]
        if abs(r["rod"]) > thr and sign(r["rod"]):
            p9.append((r["date"], sign(r["rod"]) * r["lh"] * BPS))
    p13 = [(r["date"], -sign(r["lh"]) * r["next"] * BPS) for r in rows if r["next"] is not None and sign(r["lh"])]
    return p7, p8, p9, p13


def orb5(b):
    first = [b.get(m) for m in range(570, 575)]
    if any(x is None for x in first) or 575 not in b:
        return None
    o, c = first[0][0], first[-1][3]
    if c == o:
        return None
    s = 1 if c > o else -1
    hi, lo = max(x[1] for x in first), min(x[2] for x in first)
    entry = b[575][0]
    stop = lo if s == 1 else hi
    risk = (entry - stop) * s
    if risk <= 0:
        return None
    target = entry + s * 10 * risk
    exit_px = None
    for m in range(575, 960):
        x = b.get(m)
        if x is None:
            continue
        xo, xh, xl, _ = x
        if s == 1:
            if xl <= stop:
                exit_px = min(stop, xo)
                break
            if xh >= target:
                exit_px = max(target, xo)
                break
        else:
            if xh >= stop:
                exit_px = max(stop, xo)
                break
            if xl <= target:
                exit_px = min(target, xo)
                break
    if exit_px is None:
        exit_px = b[959][3]
    return s * (exit_px / entry - 1) * BPS, s * (exit_px - entry) / risk


def orb30(b, tab, d):
    rng = [b[m] for m in range(570, 600) if m in b]
    if len(rng) < 25:
        return None
    hi, lo = max(x[1] for x in rng), min(x[2] for x in rng)
    s = None
    for m in range(600, 959):
        x = b.get(m)
        if x is None:
            continue
        up, dn = x[1] > hi, x[2] < lo
        if up and dn:
            return "ambiguous"
        if up or dn:
            s = 1 if up else -1
            entry = max(hi, x[0]) if up else min(lo, x[0])
            stop = lo if up else hi
            start = m + 1
            break
    if s is None:
        return None
    exit_px = None
    for m in range(start, 959):
        x = b.get(m)
        if x is None:
            continue
        if s == 1 and x[2] <= stop:
            exit_px = min(stop, x[0])
            break
        if s == -1 and x[1] >= stop:
            exit_px = max(stop, x[0])
            break
    if exit_px is None:
        exit_px = price(tab, d, 959)
    return s * (exit_px / entry - 1) * BPS


def us_tests():
    tabs = {s: table(s, YEARS_IDX, RTH | EARLY) for s in ("SPXUSD", "NSXUSD")}
    rows = {s: us_rows(t) for s, t in tabs.items()}
    p7, p8, p9, p13 = p7_p9_p13(rows["SPXUSD"])
    p7_us100 = p7_p9_p13(rows["NSXUSD"])[0]
    cut = date(2022, 1, 1)
    res = {"P7": block("Q7_P7", [d for d, _ in p7], [x for _, x in p7], cut, 1.5),
           "P8": block("Q7_P8", [d for d, _ in p8], [x for _, x in p8], cut, 1.5),
           "P9": block("Q7_P9", [d for d, _ in p9], [x for _, x in p9], cut, 1.5),
           "P13": block("Q7_P13", [d for d, _ in p13], [x for _, x in p13], cut, 1.5)}
    a, b = res["P7"]["pre"], res["P7"]["post_publication"]
    se = math.hypot(a["mean_bps"] / a["t_hac"], b["mean_bps"] / b["t_hac"])
    z = (b["mean_bps"] - a["mean_bps"]) / se
    res["P7"]["secondary_split_difference"] = {"post_minus_pre_bps": b["mean_bps"] - a["mean_bps"], "z": z,
                                               "p_two_sided": 2 * (1 - vs.N01.cdf(abs(z)))}
    res["P7"]["secondary_us100"] = vs.summarize([d for d, _ in p7_us100], [x for _, x in p7_us100], 1, 5, 1.5, boot=False)
    res["P7"]["secondary_us100"]["post_2022"] = vs.summarize([d for d, x in p7_us100 if d >= cut],
                                                             [x for d, x in p7_us100 if d >= cut], 1, 5, 1.5, boot=False)
    per_year = {}
    for d, x in p7:
        per_year.setdefault(d.year, []).append(x)
    res["P7"]["per_year_mean_bps"] = {y: round(vs.mean(v), 2) for y, v in sorted(per_year.items())}

    # P10, P11: US100 + US500 pooled by date
    p10, p10r, p11, amb = {}, {}, {}, {}
    for s, tab in tabs.items():
        p10[s], p10r[s], p11[s], amb[s] = [], [], [], 0
        for d in us_days(tab):
            b = tab[d]
            r = orb5(b)
            if r:
                p10[s].append((d, r[0]))
                p10r[s].append((d, r[1]))
            r = orb30(b, tab, d)
            if r == "ambiguous":
                amb[s] += 1
            elif r is not None:
                p11[s].append((d, r))
    cut10 = date(2023, 1, 1)
    ds, ps = pool(p10)
    res["P10"] = block("Q7_P10", ds, ps, cut10, 1.5)
    res["P10"]["per_symbol"] = {s: vs.summarize([d for d, _ in v], [x for _, x in v], 1, 5, 1.5, boot=False) for s, v in p10.items()}
    res["P10"]["secondary_R_multiple"] = {s: vs.summarize([d for d, _ in v], [x for _, x in v], 1, 5, 0.0, boot=False) for s, v in p10r.items()}
    ds, ps = pool(p11)
    res["P11"] = block("Q7_P11", ds, ps, cut10, 1.5)
    res["P11"]["per_symbol"] = {s: vs.summarize([d for d, _ in v], [x for _, x in v], 1, 5, 1.5, boot=False) for s, v in p11.items()}
    res["P11"]["ambiguous_days_skipped"] = amb

    # P14 control: long 02:00 -> 03:00 NY, US500
    t = tabs["SPXUSD"]
    p14 = []
    for d in sorted(t):
        if d.weekday() < 5:
            a2, a3 = price(t, d, 120), price(t, d, 180)
            if a2 and a3:
                p14.append((d, (a3 / a2 - 1) * BPS))
    res["P14"] = block("Q7_P14", [d for d, _ in p14], [x for _, x in p14], date(2021, 1, 1), 1.5)
    res["coverage"] = {s: {"regular_days": len(us_days(t)), "first": str(min(t)), "last": str(max(t))} for s, t in tabs.items()}
    return res


# ---------------------------------------------------------------- GER40 (P12)

def ny_min(dt):
    loc = dt.astimezone(NY)
    return loc.date(), loc.hour * 60 + loc.minute


def ger_test():
    keep = set(range(585, 760))  # 09:45 .. 12:39 NY covers 17:00-17:30 Berlin in every DST combination
    tab = table("GRXEUR", YEARS_IDX, keep)
    pts = []
    for d in sorted(tab):
        if d.weekday() >= 5:
            continue
        p = [price(tab, *ny_min(datetime(d.year, d.month, d.day, h, m, tzinfo=BER))) for h, m in ((17, 0), (17, 30))]
        if all(p):
            pts.append((d, p[0], p[1]))
    out = []
    for (d0, _, c0), (d, p17, p1730) in zip(pts, pts[1:]):
        if (d - d0).days <= 4:
            s = sign(p17 / c0 - 1)
            if s:
                out.append((d, s * (p1730 / p17 - 1) * BPS))
    res = block("Q7_P12", [d for d, _ in out], [x for _, x in out], date(2022, 1, 1), 1.5)
    res["coverage"] = {"days": len(pts), "first": str(pts[0][0]), "last": str(pts[-1][0])}
    return res


# ---------------------------------------------------------------- FX (Q6)

PAIRS = {"EURUSD": False, "GBPUSD": False, "AUDUSD": False, "NZDUSD": False,
         "USDJPY": True, "USDCHF": True, "USDCAD": True, "USDNOK": True, "USDSEK": True}


def fx_keep():
    k = set()
    for h in (10, 11, 12, 17, 20, 21):
        k |= set(range(h * 60 - 11, h * 60 + 12))
    return k


def fx_windows(tab, usd_base, first_year, ny17=(17, 0)):
    s = 1 if usd_base else -1
    out = []
    d = date(first_year, 1, 1)
    while d <= FX_END:
        if d.weekday() < 5:
            prev = d - timedelta(days=1)
            tp = price(tab, *ny_min(datetime(prev.year, prev.month, prev.day, *ny17, tzinfo=NY)), tol=10)
            tt = price(tab, *ny_min(datetime(d.year, d.month, d.day, 1, tzinfo=UTC)), tol=10)
            tb = price(tab, *ny_min(datetime(d.year, d.month, d.day, 16, tzinfo=LDN)), tol=10)
            tc = price(tab, *ny_min(datetime(d.year, d.month, d.day, *ny17, tzinfo=NY)), tol=10)
            if tp and tt and tb and tc:
                out.append((d, s * math.log(tt / tp) * BPS, s * math.log(tc / tb) * BPS))
        d += timedelta(days=1)
    return out


def fx_test():
    per_pair, cover = {}, {}
    comb = {"pre_registered": {}, "ny_16_55": {}, "ny_17_10": {}}
    w1, w4 = {}, {}
    for sym, base in PAIRS.items():
        years = available_years(sym, YEARS_FX)
        cover[sym] = {"years": [years[0], years[-1]] if years else None,
                      "missing_years": sorted(set(YEARS_FX) - set(years))}
        if not years:
            continue
        tab = table(sym, years, fx_keep())
        for label, t in (("pre_registered", (17, 0)), ("ny_16_55", (16, 55)), ("ny_17_10", (17, 10))):
            rows = fx_windows(tab, base, years[0], t)
            for d, a, b in rows:
                comb[label].setdefault(d, []).append(a - b)
                if label == "pre_registered":
                    w1.setdefault(d, []).append(a)
                    w4.setdefault(d, []).append(b)
            if label == "pre_registered":
                cover[sym]["pair_days"] = len(rows)
                per_pair[sym] = vs.summarize([d for d, _, _ in rows], [a - b for _, a, b in rows], 1, 5, 2.0, boot=False)
                per_pair[sym]["post_2019"] = vs.summarize([d for d, _, _ in rows if d.year >= 2019],
                                                          [a - b for d, a, b in rows if d.year >= 2019], 1, 5, 2.0, boot=False)
        del tab
    c = comb["pre_registered"]
    ds = sorted(c)
    res = block("Q6", ds, [vs.mean(c[d]) for d in ds], date(2019, 1, 1), 2.0)
    res["per_pair"] = per_pair
    res["coverage"] = cover
    res["secondary_W1_long_usd"] = vs.summarize(ds, [vs.mean(w1[d]) for d in ds], 1, 5, 1.0, boot=False)
    res["secondary_W4_usd_move"] = vs.summarize(ds, [vs.mean(w4[d]) for d in ds], -1, 5, 1.0, boot=False)
    per_year = {}
    for d in ds:
        per_year.setdefault(d.year, []).append(vs.mean(c[d]))
    res["per_year_mean_bps"] = {y: round(vs.mean(v), 2) for y, v in sorted(per_year.items())}
    rob = {}
    for label in ("ny_16_55", "ny_17_10"):
        dd = sorted(comb[label])
        rob[label] = vs.summarize(dd, [vs.mean(comb[label][d]) for d in dd], 1, 5, 2.0, boot=False)
        rob[label]["post_2019"] = vs.summarize([d for d in dd if d.year >= 2019],
                                               [vs.mean(comb[label][d]) for d in dd if d.year >= 2019], 1, 5, 2.0, boot=False)
    res["robustness_post_hoc"] = rob
    return res


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {}
    us = us_tests()
    for k in ("P7", "P8", "P9", "P10", "P11", "P13", "P14"):
        res["Q7_" + k] = us[k]
    res["Q7_P12"] = ger_test()
    res["Q7_coverage"] = us["coverage"]
    res["Q6"] = fx_test()
    json.dump(res, open(os.path.join(OUT, "histdata.json"), "w"), indent=2, default=str)
    json.dump(SERIES, open(os.path.join(OUT, "series_histdata.json"), "w"), default=str)
    for k, v in res.items():
        if "n" not in v:
            continue
        print(f"{k:7s} n={v['n']:5d} mean={v['mean_bps']:7.2f} net={v['net_mean_bps']:7.2f} t={v['t_hac']:5.2f} "
              f"p={v['p_one_sided']:.4f} yrs={v['years_pred_sign']} ci={[round(x, 1) for x in v['ci95_bps']]}")
        for part in ("pre", "post_publication"):
            x = v[part]
            if "mean_bps" in x:
                print(f"        {part:16s} n={x['n']:5d} mean={x['mean_bps']:7.2f} t={x['t_hac']:5.2f} p={x['p_one_sided']:.4f}")


if __name__ == "__main__":
    main()
