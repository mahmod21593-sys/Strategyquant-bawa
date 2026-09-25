"""Round 3 confirmation tests R1-R6 on unseen data (PREREGISTRATION.md amendment A6).

-> results/round3.json, results/series_round3.json
"""
from __future__ import annotations

import json
import math
import os
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import vstats as vs
from data_histdata import NY, available_years, price, table
from data_yahoo import daily
from run_histdata import BPS, RTH, orb5, orb30, pool, sign, us_days

OUT = os.path.join(os.path.dirname(__file__), "results")
PAR, BER, LDN, UTC = ZoneInfo("Europe/Paris"), ZoneInfo("Europe/Berlin"), ZoneInfo("Europe/London"), timezone.utc
SERIES = {}
N_TRIALS = 57


def ny_min(dt):
    loc = dt.astimezone(NY)
    return loc.date(), loc.hour * 60 + loc.minute


def summarize(key, dates, pnl, cost, lag=5):
    res = vs.summarize(dates, pnl, 1, lag, cost)
    SERIES[key] = {"dates": [str(d) for d in dates], "pnl_bps": pnl, "cost_bps": cost, "lag": lag}
    res["dsr_N57"] = vs.deflated_sharpe(pnl, N_TRIALS)
    return res


def close_momentum(sym, years, tz, sig=(17, 0), close=(17, 30)):
    """P12 rule: sign(prior close -> sig) held sig -> close, local exchange time. Returns [(date, pnl_bps, |signal|)]."""
    tab = table(sym, years, set(range(585, 760)))  # 09:45-12:39 NY covers 16:00-17:30 London/Paris in every DST combination
    pts = []
    for d in sorted(tab):
        if d.weekday() >= 5:
            continue
        p = [price(tab, *ny_min(datetime(d.year, d.month, d.day, *hm, tzinfo=tz))) for hm in (sig, close)]
        if all(p):
            pts.append((d, p[0], p[1]))
    out = []
    for (d0, _, c0), (d, ps, pc) in zip(pts, pts[1:]):
        if (d - d0).days <= 4:
            s = sign(ps / c0 - 1)
            if s:
                out.append((d, s * (pc / ps - 1) * BPS, abs(ps / c0 - 1)))
    return out


def top_tercile(rows):
    k = len(rows) // 3
    thr = sorted(r[2] for r in rows)[2 * k] if rows else 0
    sel = [(d, x) for d, x, a in rows if a >= thr]
    return vs.summarize([d for d, _ in sel], [x for _, x in sel], 1, 5, 1.5, boot=False)


def r1():
    per, sec, tert = {}, {}, {}
    for sym, tz, sig, close in (("FRXEUR", PAR, (17, 0), (17, 30)), ("ETXEUR", PAR, (17, 0), (17, 30)),
                                ("UKXGBP", LDN, (16, 0), (16, 30))):
        yrs = available_years(sym, range(2014, 2026))
        rows = close_momentum(sym, yrs, tz, sig, close)
        per[sym] = [(d, x) for d, x, _ in rows]
        sec[sym] = vs.summarize([d for d, _, _ in rows], [x for _, x, _ in rows], 1, 5, 1.5, boot=False)
        sec[sym]["years"] = [yrs[0], yrs[-1]] if yrs else None
        tert[sym] = top_tercile(rows)
    ds, ps = pool(per)
    res = summarize("R1", ds, ps, 1.5)
    res["per_index"], res["post_hoc_top_tercile"] = sec, tert
    return res


def r2():
    yrs = available_years("GRXEUR", range(2000, 2014))
    rows = close_momentum("GRXEUR", yrs, BER)
    res = summarize("R2", [d for d, _, _ in rows], [x for _, x, _ in rows], 1.5)
    res["years"] = [yrs[0], yrs[-1]] if yrs else None
    res["post_hoc_top_tercile"] = top_tercile(rows)
    return res


def r3_r4():
    p10, p11, cover = {}, {}, {}
    for sym in ("SPXUSD", "NSXUSD"):
        yrs = available_years(sym, range(2000, 2014))
        cover[sym] = [yrs[0], yrs[-1]] if yrs else None
        if not yrs:
            continue
        tab = table(sym, yrs, RTH)
        p10[sym], p11[sym] = [], []
        for d in us_days(tab):
            r = orb5(tab[d])
            if r:
                p10[sym].append((d, r[0]))
            r = orb30(tab[d], tab, d)
            if r not in (None, "ambiguous"):
                p11[sym].append((d, r))
    out = {}
    for key, per in (("R3", p11), ("R4", p10)):
        ds, ps = pool(per)
        out[key] = summarize(key, ds, ps, 1.5)
        out[key]["per_symbol"] = {s: vs.summarize([d for d, _ in v], [x for _, x in v], 1, 5, 1.5, boot=False) for s, v in per.items()}
        out[key]["years"] = cover
    return out


def r5():
    per, sec = {}, {}
    for sym in ("DIA", "IWM"):
        rows = daily(sym)
        g = {}
        for r in rows:
            g.setdefault(r["date"].year, []).append((r["c"] / r["o"] - 1) * BPS)
        base = {y: vs.mean(v) for y, v in g.items()}
        out = []
        for i in range(3, len(rows) - 1):
            if all(rows[j]["c"] < rows[j - 1]["c"] for j in (i, i - 1, i - 2)):
                e = rows[i + 1]
                if e["date"] >= date(2013, 1, 1):
                    out.append((e["date"], (e["c"] / e["o"] - 1) * BPS - base[e["date"].year]))
        per[sym] = out
        sec[sym] = vs.summarize([d for d, _ in out], [x for _, x in out], 1, 5, 1.5, boot=False)
    ds, ps = pool(per)
    res = summarize("R5", ds, ps, 1.5)
    res["per_etf"] = sec
    return res


def fx_w1(sym, usd_base, start, end):
    yrs = available_years(sym, range(start.year - 1, end.year + 1))
    keep = set(range(18 * 60 + 19, 18 * 60 + 42)) | set(range(19 * 60 + 49, 20 * 60 + 12)) | set(range(20 * 60 + 49, 21 * 60 + 12))
    tab = table(sym, yrs, keep)
    s = 1 if usd_base else -1
    out = []
    d = start
    while d <= end:
        if d.weekday() < 5:
            pv = d - timedelta(days=1)
            a = price(tab, *ny_min(datetime(pv.year, pv.month, pv.day, 18, 30, tzinfo=NY)), tol=10)
            b = price(tab, *ny_min(datetime(d.year, d.month, d.day, 1, 0, tzinfo=UTC)), tol=10)
            if a and b:
                out.append((d, s * math.log(b / a) * BPS))
        d += timedelta(days=1)
    return out, yrs


def r6():
    start, end = date(2024, 1, 1), date(2025, 12, 31)
    quote = {"EURUSD": False, "GBPUSD": False, "AUDUSD": False, "NZDUSD": False}
    base = {"USDJPY": True, "USDCHF": True, "USDCAD": True, "USDNOK": True, "USDSEK": True}
    per, sec, cover = {}, {}, {}
    for sym, b in {**quote, **base}.items():
        rows, yrs = fx_w1(sym, b, start, end)
        per[sym], cover[sym] = rows, yrs
        sec[sym] = vs.summarize([d for d, _ in rows], [x for _, x in rows], 1, 5, 1.0, boot=False)
    ds, ps = pool({k: per[k] for k in quote})
    res = summarize("R6", ds, ps, 1.0)
    res["per_pair"], res["coverage"] = sec, cover
    ds, ps = pool({k: per[k] for k in base})
    res["secondary_usd_base_pairs"] = vs.summarize(ds, ps, 1, 5, 1.0, boot=False)
    return res


def r7():
    per, agree = {}, {}
    for sym in ("SPXUSD", "NSXUSD"):
        tab = table(sym, range(2014, 2026), RTH)
        days = us_days(tab)
        close = {d: price(tab, d, 960) for d in days}
        g = {}
        for a, b in zip(days, days[1:]):
            if close[a] and close[b]:
                g.setdefault(b.year, []).append((close[b] / close[a] - 1) * BPS)
        base = {y: vs.mean(v) for y, v in g.items()}
        out, hits = [], 0
        for i in range(3, len(days) - 1):
            d = days[i]
            c1, c2, c3, c0, nx = close[days[i - 1]], close[days[i - 2]], close[days[i - 3]], close[d], close[days[i + 1]]
            p = price(tab, d, 955)
            if None in (c1, c2, c3, c0, nx, p):
                continue
            if p < c1 < c2 < c3:
                out.append((days[i + 1], (nx / p - 1) * BPS - base[days[i + 1].year]))
                hits += c0 < c1
        per[sym] = out
        agree[sym] = hits / len(out) if out else None
    ds, ps = pool(per)
    res = summarize("R7", ds, ps, 1.5)
    res["per_symbol"] = {s: vs.summarize([d for d, _ in v], [x for _, x in v], 1, 5, 1.5, boot=False) for s, v in per.items()}
    res["share_signals_that_are_true_3_down_closes"] = agree
    return res


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"R1": r1(), "R2": r2(), **r3_r4(), "R5": r5(), "R6": r6(), "R7": r7()}
    fam = {k: v["p_one_sided"] for k, v in res.items()}
    holm, bh = vs.holm(fam), vs.bh(fam)
    for k, v in res.items():
        v["p_holm_R"], v["q_bh_R"] = holm[k], bh[k]
        ok = v["mean_bps"] > 0 and holm[k] < 0.05 and v["net_mean_bps"] > 0
        v["verdict"] = "REPLICATED" if ok else "WEAK" if v["p_one_sided"] < 0.05 else "NOT REPLICATED"
    json.dump(res, open(os.path.join(OUT, "round3.json"), "w"), indent=2, default=str)
    json.dump(SERIES, open(os.path.join(OUT, "series_round3.json"), "w"), default=str)
    for k, v in res.items():
        print(f"{k:3s} {v['verdict']:15s} n={v['n']:5d} {v['first']}..{v['last']} mean={v['mean_bps']:7.2f} net={v['net_mean_bps']:6.2f} "
              f"t={v['t_hac']:5.2f} p={v['p_one_sided']:.4f} holmR={v['p_holm_R']:.4f} yrs={v['years_pred_sign']} "
              f"ci={[round(x, 1) for x in v['ci95_bps']]} dsr={v['dsr_N57']:.3f}")
        for sub in ("per_index", "per_symbol", "per_etf", "per_pair", "post_hoc_top_tercile"):
            if sub in v and isinstance(v[sub], dict):
                items = v[sub].items() if "n" not in v[sub] else [("all", v[sub])]
                for s, x in items:
                    if "mean_bps" in x:
                        print(f"      {sub:20s} {s:7s} n={x['n']:5d} mean={x['mean_bps']:7.2f} t={x['t_hac']:5.2f}")
        if "secondary_usd_base_pairs" in v:
            x = v["secondary_usd_base_pairs"]
            print(f"      usd_base_pairs      n={x['n']:5d} mean={x['mean_bps']:7.2f} t={x['t_hac']:5.2f}")


if __name__ == "__main__":
    main()
