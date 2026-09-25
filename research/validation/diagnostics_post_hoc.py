"""Post-hoc diagnostics referenced in REPORT.md §7.3, §8 and §9. None of these is a pre-registered test; they are
used to check and (where needed) downgrade the pre-registered results. -> results/diagnostics_post_hoc.json
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
from run_histdata import BPS, PAIRS, RTH, fx_keep, ny_min, orb5, sign, us_days

R = os.path.join(os.path.dirname(__file__), "results")
BER, LDN, UTC = ZoneInfo("Europe/Berlin"), ZoneInfo("Europe/London"), timezone.utc
MAJORS6 = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCHF", "USDCAD"]


def f(rows):
    x = [r[1] for r in rows]
    return {"n": len(x), "mean_bps": round(vs.mean(x), 2), "t": round(vs.nw_t(x, 5), 2)}


def by_period(rows):
    return {f"{lo}-{hi}": f([r for r in rows if lo <= r[0].year <= hi]) for lo, hi in ((2004, 2018), (2019, 2023))}


def fx_rollover_dip():
    """Mean ln(bid_t) - ln(bid_16:30) in bps, Mon-Thu. A dip common to USD-base and USD-quote pairs is spread, not price."""
    times = [(16, 45), (16, 55), (16, 58), (17, 0), (17, 2), (17, 5), (17, 10), (17, 15), (17, 30), (18, 0), (18, 30)]
    keep = set(range(16 * 60 + 25, 18 * 60 + 36))
    out = {}
    for sym in PAIRS:
        tab = table(sym, available_years(sym, range(2004, 2024)), keep)
        for lo, hi in ((2004, 2018), (2019, 2023)):
            acc = {t: [] for t in times}
            for d in tab:
                if lo <= d.year <= hi and d.weekday() <= 3:
                    base = price(tab, d, 16 * 60 + 30)
                    for t in times:
                        p = price(tab, d, t[0] * 60 + t[1], tol=1)
                        if base and p:
                            acc[t].append(math.log(p / base) * BPS)
            out[f"{sym} {lo}-{hi}"] = {f"{h:02d}:{m:02d}": round(vs.mean(v), 2) for (h, m), v in acc.items()}
    return out


def fx_clean_segments():
    """USD-signed returns with boundaries away from the NY 17:00 rollover (to 2023-09, the Q6 sample)."""
    keep = fx_keep() | set(range(16 * 60 + 35, 16 * 60 + 56)) | set(range(18 * 60 + 20, 18 * 60 + 41))
    segs = {}
    for sym, base in PAIRS.items():
        yrs = available_years(sym, range(2004, 2024))
        tab = table(sym, yrs, keep)
        s = 1 if base else -1

        def px(dd, h, m, tz):
            return price(tab, *ny_min(datetime(dd.year, dd.month, dd.day, h, m, tzinfo=tz)), tol=10)

        d = date(yrs[0], 1, 1)
        while d <= date(2023, 9, 30):
            if d.weekday() < 5:
                pv = d - timedelta(days=1)
                l16, n1645, n1830 = px(d, 16, 0, LDN), px(d, 16, 45, NY), px(d, 18, 30, NY)
                p1830, t01 = px(pv, 18, 30, NY), px(d, 1, 0, UTC)
                for k, a, b in (("A_london16_to_ny1645", l16, n1645), ("B_ny1645_to_1830", n1645, n1830),
                                ("C_ny1830_to_0100utc", p1830, t01)):
                    if a and b:
                        segs.setdefault((sym, k), {})[d] = s * math.log(b / a) * BPS
            d += timedelta(days=1)
    out = {}
    for k in ("A_london16_to_ny1645", "B_ny1645_to_1830", "C_ny1830_to_0100utc"):
        out[k] = {sym: by_period(sorted(segs[(sym, k)].items())) for sym in PAIRS}
        for name, grp in (("basket9", list(PAIRS)), ("majors6", MAJORS6)):
            g = {}
            for sym in grp:
                for d, v in segs[(sym, k)].items():
                    g.setdefault(d, []).append(v)
            out[k][name] = by_period([(d, vs.mean(g[d])) for d in sorted(g)])
    for name, grp in (("basket9", list(PAIRS)), ("majors6", MAJORS6)):
        g = {}
        for sym in grp:
            a, b = segs[(sym, "C_ny1830_to_0100utc")], segs[(sym, "A_london16_to_ny1645")]
            for d in a:
                if d in b:
                    g.setdefault(d, []).append(a[d] - b[d])
        out[f"C_minus_A_{name}"] = by_period([(d, vs.mean(g[d])) for d in sorted(g)])
    return out


def p7_cross_source():
    """P7 P&L on the days both sources cover: Yahoo 60-min ETF bars vs HistData SPXUSD."""
    import run_intraday_yahoo as y
    s = json.load(open(os.path.join(R, "series_histdata.json")))["Q7_P7"]
    hd = {date.fromisoformat(d): p for d, p in zip(s["dates"], s["pnl_bps"])}
    out = {}
    for sym in ("SPY", "QQQ"):
        yp = {r["date"]: (1 if r["rod"] > 0 else -1) * r["lh"] * BPS for r in y.us_series(sym)}
        common = sorted(set(yp) & set(hd))
        a, b = [yp[d] for d in common], [hd[d] for d in common]
        ma, mb = vs.mean(a), vs.mean(b)
        corr = sum((x - ma) * (z - mb) for x, z in zip(a, b)) / (len(a) - 1) / vs.sd(a) / vs.sd(b)
        out[sym] = {"days": len(common), "from": str(common[0]), "to": str(common[-1]), "yahoo_mean": round(ma, 2),
                    "yahoo_t": round(vs.nw_t(a, 5), 2), "histdata_mean": round(mb, 2), "histdata_t": round(vs.nw_t(b, 5), 2),
                    "corr": round(corr, 3)}
    return out


def p12_perturbations():
    tab = table("GRXEUR", range(2014, 2026), set(range(585, 760)))

    def run(sig_end=(17, 0), entry=(17, 0), exit_=(17, 30)):
        pts = []
        for d in sorted(tab):
            if d.weekday() < 5:
                p = [price(tab, *ny_min(datetime(d.year, d.month, d.day, *hm, tzinfo=BER))) for hm in (sig_end, entry, exit_)]
                if all(p):
                    pts.append((d, *p))
        res = []
        for (d0, _, _, c0), (d, a, b, c) in zip(pts, pts[1:]):
            if (d - d0).days <= 4 and sign(a / c0 - 1):
                res.append((d, sign(a / c0 - 1) * (c / b - 1) * BPS, abs(a / c0 - 1), sign(a / c0 - 1)))
        return res, pts

    base, pts = run()
    yr = {}
    for d, x, *_ in base:
        yr.setdefault(d.year, []).append(x)
    srt = sorted(base, key=lambda r: r[2])
    k = len(srt) // 3
    return {"per_year": {y: round(vs.mean(v), 2) for y, v in sorted(yr.items())},
            "signal_to_16_58": f(run((16, 58))[0]), "entry_17_02": f(run((17, 0), (17, 2))[0]),
            "exit_17_29": f(run(exit_=(17, 29))[0]), "exit_17_35": f(run(exit_=(17, 35))[0]),
            "long_leg": f([r for r in base if r[3] > 0]), "short_leg": f([r for r in base if r[3] < 0]),
            "unconditional_drift": f([(d, (c / a - 1) * BPS) for d, _, a, c in pts]),
            "signal_terciles": [f(srt[:k]), f(srt[k:2 * k]), f(srt[2 * k:])]}


def p10_r_multiples():
    out = {}
    for sym in ("SPXUSD", "NSXUSD"):
        tab = table(sym, range(2014, 2026), RTH)
        rs, rnet, risks = [], [], []
        for d in us_days(tab):
            b = tab[d]
            r = orb5(b)
            if not r:
                continue
            first = [b[m] for m in range(570, 575)]
            s = 1 if first[-1][3] > first[0][0] else -1
            stop = min(x[2] for x in first) if s == 1 else max(x[1] for x in first)
            risk = abs(b[575][0] - stop) / b[575][0] * BPS
            risks.append(risk)
            rs.append((d, r[1]))
            rnet.append((d, r[1] - 1.5 / risk))
        risks.sort()
        out[sym] = {"median_risk_bps": round(risks[len(risks) // 2], 1), "R_gross": f(rs), "R_net_1.5bps": f(rnet),
                    "R_net_2023_on": f([x for x in rnet if x[0] >= date(2023, 1, 1)])}
    return out


def mr06_entry_timing():
    """Same data and years: MR-06 entered at the exact 16:00 close vs at 15:55 (raw next-close return), and Yahoo index."""
    out = {}
    for sym, ysym in (("SPXUSD", "^GSPC"), ("NSXUSD", "^NDX")):
        tab = table(sym, range(2014, 2026), RTH)
        days = us_days(tab)
        c = {d: price(tab, d, 960) for d in days}
        a, b = [], []
        for i in range(3, len(days) - 1):
            d, n = days[i], days[i + 1]
            if c[d] < c[days[i - 1]] < c[days[i - 2]] < c[days[i - 3]]:
                a.append((n, (c[n] / c[d] - 1) * BPS))
            p = price(tab, d, 955)
            if p and p < c[days[i - 1]] < c[days[i - 2]] < c[days[i - 3]]:
                b.append((n, (c[n] / p - 1) * BPS))
        rows = [r for r in daily(ysym) if date(2014, 1, 1) <= r["date"] <= date(2025, 12, 31)]
        yv = [(rows[i + 1]["date"], (rows[i + 1]["c"] / rows[i]["c"] - 1) * BPS) for i in range(3, len(rows) - 1)
              if rows[i]["c"] < rows[i - 1]["c"] < rows[i - 2]["c"] < rows[i - 3]["c"]]
        out[sym] = {"close_entry": f(a), "entry_15_55": f(b), f"yahoo_{ysym}_close": f(yv)}
    return out


def main():
    res = {"fx_rollover_dip": fx_rollover_dip(), "fx_clean_segments": fx_clean_segments(), "p7_cross_source": p7_cross_source(),
           "p12_perturbations": p12_perturbations(), "p10_r_multiples": p10_r_multiples(), "mr06_entry_timing": mr06_entry_timing()}
    json.dump(res, open(os.path.join(R, "diagnostics_post_hoc.json"), "w"), indent=1, default=str)
    for k in ("p7_cross_source", "p12_perturbations", "p10_r_multiples", "mr06_entry_timing"):
        print(k, json.dumps(res[k], default=str))
    for k in ("C_minus_A_basket9", "C_minus_A_majors6"):
        print(k, res["fx_clean_segments"][k])
    for k in ("A_london16_to_ny1645", "C_ny1830_to_0100utc"):
        print(k, res["fx_clean_segments"][k]["basket9"])


if __name__ == "__main__":
    main()
