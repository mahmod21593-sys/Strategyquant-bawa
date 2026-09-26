"""Round 8 (PREREGISTRATION.md A21): X2, E1, S1, S2, F1, C1. -> results/round8.json"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
from datetime import date, datetime, timezone

import vstats as vs
from data_histdata import NY
from data_yahoo import daily
from prop_lifecycle import evaluate, to_days
from run_noise_area import run

OUT = os.path.join(os.path.dirname(__file__), "results")
CACHE = os.environ.get("YAHOO_CACHE", "/tmp/yahoo_cache")
BPS = 1e4


def yahoo_h60(sym):
    """{NY date: {minute: (o, h, l, c)}} from Yahoo 60-minute regular-session bars, keyed at each bar's start and last minute."""
    path = os.path.join(CACHE, "h60ohlc_" + sym.replace("^", "_") + ".json")
    if not os.path.exists(path):
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym.replace('^', '%5E')}?range=730d&interval=60m"
        for a in range(6):
            r = subprocess.run(["curl", "-sS", "-m", "60", "-A", "Mozilla/5.0", url], capture_output=True, text=True)
            try:
                if json.loads(r.stdout)["chart"]["result"]:
                    os.makedirs(CACHE, exist_ok=True)
                    open(path, "w").write(r.stdout)
                    break
            except Exception:
                pass
            time.sleep(3 + 3 * a)
    d = json.load(open(path))["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    ses, starts = {}, {}
    for i, t in enumerate(d["timestamp"]):
        o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
        if None in (o, h, l, c):
            continue
        loc = datetime.fromtimestamp(t, timezone.utc).astimezone(NY)
        s = loc.hour * 60 + loc.minute
        if s < 570 or s >= 960:
            continue
        e = min(s + 60, 960)
        b = ses.setdefault(loc.date(), {})
        b[s] = (o, h, l, c)
        b[e - 1] = (o, h, l, c)
        starts[s] = starts.get(s, 0) + 1
    return ses, starts


def x2():
    res = {}
    series = {}
    for sym in ("QQQ", "^NDX"):
        ses, starts = yahoo_h60(sym)
        rows = run("N3", grid=60, ses=ses)[0]
        series[sym] = dict(rows)
        res[f"{sym}_bar_starts"] = {f"{m // 60:02d}:{m % 60:02d}": n for m, n in sorted(starts.items())}
    hd = dict(run("N3", grid=60, y0=2024, y1=2027)[0])
    series["HistData_NSXUSD"] = hd
    first = min(min(series["QQQ"]), min(series["^NDX"]))
    for name, s in series.items():
        sel = sorted((d, x) for d, x in s.items() if d >= first)
        res[name] = vs.summarize([d for d, _ in sel], [x for _, x in sel], 1, 5, 0.0, boot=False)
    for a, b in (("HistData_NSXUSD", "QQQ"), ("HistData_NSXUSD", "^NDX"), ("QQQ", "^NDX")):
        common = sorted(set(series[a]) & set(series[b]))
        xa, xb = [series[a][d] for d in common], [series[b][d] for d in common]
        ma, mb = vs.mean(xa), vs.mean(xb)
        cov = sum((u - ma) * (v - mb) for u, v in zip(xa, xb)) / len(common)
        res[f"corr_{a}_vs_{b}"] = {"n_common": len(common), "corr": cov / (vs.sd(xa) * vs.sd(xb)), "mean_a": ma, "mean_b": mb,
                                   "same_sign": (ma > 0) == (mb > 0)}
    c = res["corr_HistData_NSXUSD_vs_QQQ"]
    res["verdict"] = "FEEDS AGREE" if c["corr"] >= 0.6 and c["same_sign"] else "FEEDS DISAGREE"
    return res


def e1():
    rows = [r for r in daily("SPY") if date(1993, 2, 1) <= r["date"] <= date(2026, 8, 31)]
    trades = []
    for i in range(3, len(rows) - 3):
        c = [rows[i - k]["adj"] for k in range(4)]
        if c[0] < c[1] < c[2] < c[3]:
            r = [(rows[i + k]["adj"] / rows[i]["adj"] - 1) * BPS for k in (1, 2, 3)]
            trades.append((rows[i]["date"], r))
    res = {"n_signals": len(trades)}
    for k in (1, 2, 3):
        x = [r[k - 1] for _, r in trades]
        res[f"exit_t+{k}"] = {"mean_bps_per_trade": vs.mean(x), "t_hac": vs.nw_t(x, 5), "mean_bps_per_day_held": vs.mean(x) / k}
    for k in (2, 3):
        d = [r[k - 1] / k - r[0] for _, r in trades]
        t = vs.nw_t(d, 5)
        res[f"per_day_t+{k}_minus_t+1"] = {"mean_bps": vs.mean(d), "t_hac": t, "p_one_sided": 1 - vs.N01.cdf(t)}
    better = [k for k in (2, 3) if res[f"per_day_t+{k}_minus_t+1"]["p_one_sided"] < 0.05]
    res["decision"] = f"switch to t+{better[0]}" if better else "keep exit at t+1"
    return res


def books():
    from prop_lifecycle_real import build_books
    return build_books(["B1", "B2", "B2n"])


SETUPS = (("N3 news-filtered 4x, FTMO 1-Step", "B2n", "ftmo_1step_100k.json", 0.02, 4.0),
          ("N3 4x, FTMO 2-Step Swing", "B2", "ftmo_2step_100k.json", 0.03, 4.0),
          ("MR-06 3x, FTMO 2-Step Swing", "B1", "ftmo_2step_100k.json", 0.03, 3.0))


def keep(a):
    return {k: a[k] for k in ("p_pass", "ev_per_attempt_usd", "mean_months", "ev_per_account_month_usd", "p_any_payout")}


def s1_s2(bk):
    s1, s2 = {}, {}
    for label, b, preset, guard, L in SETUPS:
        book = bk[b]
        s1[label] = {}
        for per, lo, hi in (("2014_2019", date(2014, 1, 1), date(2019, 12, 31)), ("2020_2025", date(2020, 1, 1), date(2025, 12, 31)),
                            ("2014_2025", date(2014, 1, 1), date(2025, 12, 31))):
            sub = {d: v for d, v in book.items() if lo <= d <= hi}
            s1[label][per] = keep(evaluate(to_days(sub), preset, guard, L, None))
            s1[label][per]["mean_bps_per_day_1x"] = vs.mean([v[0] for v in sub.values()]) * BPS
            print("S1", label, per, s1[label][per], flush=True)
        m = vs.mean([v[0] for v in book.values()])
        s2[label] = {}
        for lam in (0.0, 0.25, 0.5, 0.75, 1.0):
            shift = m * (1 - lam)
            bl = {d: (p - shift, lo_ - shift, h - shift) for d, (p, lo_, h) in book.items()}
            s2[label][f"lambda_{lam:g}"] = keep(evaluate(to_days(bl), preset, guard, L, None))
            print("S2", label, lam, s2[label][f"lambda_{lam:g}"], flush=True)
    return s1, s2


def f1():
    edges = {"N3 (per trading day)": (3.02, 65.7, 252), "N3 pooled with 2026 (per day)": (2.91, 65.7, 252),
             "MR-06 vol-scaled (per trade)": (18.5, 127.2, 19), "MR-08 intraday half (per trade)": (11.3, 138.2, 19)}
    res = {}
    a = math.log(9)
    for k, (mu, sd, per_year) in edges.items():
        n_t2 = (2 * sd / mu) ** 2
        esn = (0.9 * a - 0.1 * a) / (mu ** 2 / (2 * sd ** 2))
        stop = {f"after_{n}": mu - 2.326 * sd / math.sqrt(n) for n in (60, 126, 252, 504)}
        res[k] = {"mu_bps": mu, "sd_bps": sd, "per_year": per_year, "n_for_t2": n_t2, "years_for_t2": n_t2 / per_year,
                  "sprt_expected_n_if_edge_real": esn, "sprt_expected_years": esn / per_year,
                  "stop_if_forward_mean_below_bps (1% one-sided vs in-sample)": stop}
    return res


def c1(bk):
    b1, b2 = bk["B1"], bk["B2"]
    days = sorted(d for d in set(b1) | set(b2) if d.weekday() < 5)
    x1 = [b1.get(d, (0.0,))[0] for d in days]
    x2_ = [b2.get(d, (0.0,))[0] for d in days]

    def corr(a, b):
        ma, mb = vs.mean(a), vs.mean(b)
        return sum((u - ma) * (v - mb) for u, v in zip(a, b)) / len(a) / (vs.sd(a) * vs.sd(b))

    mo1, mo2 = {}, {}
    for d, u, v in zip(days, x1, x2_):
        mo1[(d.year, d.month)] = mo1.get((d.year, d.month), 0) + u
        mo2[(d.year, d.month)] = mo2.get((d.year, d.month), 0) + v
    ks = sorted(mo1)
    both = [d for d in days if d in b1 and d in b2]
    worst = sorted(b2, key=lambda d: b2[d][0])[:20]
    return {"daily_corr": corr(x1, x2_), "monthly_corr": corr([mo1[k] for k in ks], [mo2[k] for k in ks]),
            "days_both_trade": len(both), "share_of_20_worst_N3_days_with_MR06_loss": vs.mean([b1.get(d, (0,))[0] < 0 for d in worst]),
            "corr_on_common_days": corr([b1[d][0] for d in both], [b2[d][0] for d in both]) if len(both) > 10 else None}


def main(parts):
    path = os.path.join(OUT, "round8.json")
    res = json.load(open(path)) if os.path.exists(path) else {}
    if "X2" in parts:
        res["X2"] = x2()
        print("X2", {k: v for k, v in res["X2"].items() if k.startswith("corr") or k == "verdict"}, flush=True)
    if "E1" in parts:
        res["E1"] = e1()
        print("E1", res["E1"], flush=True)
    if "F1" in parts:
        res["F1"] = f1()
    if parts & {"S1", "C1"}:
        bk = books()
        if "C1" in parts:
            res["C1"] = c1(bk)
            print("C1", res["C1"], flush=True)
        if "S1" in parts:
            res["S1"], res["S2"] = s1_s2(bk)
    json.dump(res, open(path, "w"), indent=1, default=str)


if __name__ == "__main__":
    main(set(sys.argv[1:]) or {"X2", "E1", "F1", "C1", "S1"})
