"""Round-5 systematic scan, family X (PREREGISTRATION.md amendment A9).

Two steps, run separately so the confirmation data can't influence discovery:
    python3 run_scan.py discover   -> results/scan_discovery.json   (commit this before the next step)
    python3 run_scan.py confirm    -> results/scan_confirmation.json
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import vstats as vs
from data_binance import klines
from data_histdata import NY, available_years, bars30

OUT = os.path.join(os.path.dirname(__file__), "results")
BPS = 1e4
H30 = timedelta(minutes=30)
UTC = timezone.utc

# symbol: (kind, local tz, daily close (h, m), cost bps)
INSTR = {
    "SPXUSD": ("index", "America/New_York", (16, 0), 1.5), "NSXUSD": ("index", "America/New_York", (16, 0), 1.5),
    "GRXEUR": ("index", "Europe/Berlin", (17, 30), 1.5), "UKXGBP": ("index", "Europe/London", (16, 30), 2.0),
    "FRXEUR": ("index", "Europe/Paris", (17, 30), 2.0), "JPXJPY": ("index", "Asia/Tokyo", (15, 0), 3.0),
    "AUXAUD": ("index", "Australia/Sydney", (16, 0), 3.0), "HKXHKD": ("index", "Asia/Hong_Kong", (16, 0), 4.0),
    "XAUUSD": ("otc", "America/New_York", (16, 0), 2.5), "XAGUSD": ("otc", "America/New_York", (16, 0), 5.0),
    "WTIUSD": ("otc", "America/New_York", (16, 0), 4.0), "BCOUSD": ("otc", "America/New_York", (16, 0), 4.0),
    "EURUSD": ("otc", "America/New_York", (16, 0), 1.0), "GBPUSD": ("otc", "America/New_York", (16, 0), 1.5),
    "USDJPY": ("otc", "America/New_York", (16, 0), 1.0), "AUDUSD": ("otc", "America/New_York", (16, 0), 1.5),
    "USDCAD": ("otc", "America/New_York", (16, 0), 1.5), "USDCHF": ("otc", "America/New_York", (16, 0), 1.5),
    "NZDUSD": ("otc", "America/New_York", (16, 0), 2.0), "EURJPY": ("otc", "America/New_York", (16, 0), 2.0),
    "GBPJPY": ("otc", "America/New_York", (16, 0), 3.0), "EURGBP": ("otc", "America/New_York", (16, 0), 2.0),
    "BTCUSDT": ("crypto", "UTC", (0, 0), 5.0), "ETHUSDT": ("crypto", "UTC", (0, 0), 8.0),
}
PERIODS = {"histdata": {"discover": (date(2011, 1, 1), date(2017, 12, 31)), "confirm": (date(2018, 1, 1), date(2025, 12, 31))},
           "crypto": {"discover": (date(2018, 1, 1), date(2021, 12, 31)), "confirm": (date(2022, 1, 1), date(2026, 8, 31))}}
EXCLUDED_OTC_HOURS = {16, 17, 18}  # NY rollover spread window on bid-only data
JPX_LONG_SESSION = date(2024, 11, 5)
SEEN = {("SPXUSD", "H02"), ("SPXUSD", "H15"), ("GRXEUR", "H17"), ("UKXGBP", "H16"), ("FRXEUR", "H17"),
        ("SPXUSD", "S3D"), ("NSXUSD", "S3D")}


def local_bars(sym):
    """{local naive datetime of 30-min bar start: (o, h, l, c)}."""
    kind, tzname, _, _ = INSTR[sym]
    if kind == "crypto":
        k = klines(sym, "30m", date(2017, 8, 1), date(2026, 8, 31))
        return {t.replace(tzinfo=None): v for t, v in k.items()}
    tz = ZoneInfo(tzname)
    raw = bars30(sym, available_years(sym, range(2010, 2026)))
    out = {}
    for (d, i), v in raw.items():
        t = datetime(d.year, d.month, d.day, i // 2, 30 * (i % 2), tzinfo=NY)
        if tzname != "America/New_York":
            t = t.astimezone(tz)
        out[t.replace(tzinfo=None)] = v
    return out


def px(bars, t):
    b = bars.get(t - H30)
    if b:
        return b[3]
    b = bars.get(t)
    return b[0] if b else None


def close_time(sym, d):
    if INSTR[sym][0] == "crypto":  # the UTC day d ends at the next midnight
        return datetime(d.year, d.month, d.day) + timedelta(days=1)
    h, m = INSTR[sym][2]
    if sym == "JPXJPY" and d >= JPX_LONG_SESSION:
        h, m = 15, 30
    return datetime(d.year, d.month, d.day, h, m)


def series(sym):
    """All candidate per-day series for one instrument: {candidate: [(date, excess_bps, raw_bps)]}."""
    kind = INSTR[sym][0]
    bars = local_bars(sym)
    if not bars:
        return {}, {}
    days = sorted({t.date() for t in bars})
    if kind != "crypto":
        days = [d for d in days if d.weekday() < 5]
    out = {}
    # hour-of-day
    hourly = {}
    for d in days:
        for h in range(24):
            if kind == "otc" and h in EXCLUDED_OTC_HOURS:
                continue
            t0 = datetime(d.year, d.month, d.day, h)
            a, b = px(bars, t0), px(bars, t0 + timedelta(hours=1))
            if a and b:
                hourly.setdefault(h, []).append((d, (b / a - 1) * BPS))
    ym = {}
    for h, rows in hourly.items():
        for d, x in rows:
            ym.setdefault(d.year, []).append(x)
    ym = {y: vs.mean(v) for y, v in ym.items()}
    for h, rows in hourly.items():
        out[f"H{h:02d}"] = [(d, x - ym[d.year], x) for d, x in rows]
    # daily closes, high/low between closes
    closes = []
    ts = sorted(bars)
    j = 0
    prev_ct = None
    for d in days:
        ct = close_time(sym, d)
        c = px(bars, ct)
        if c is None:
            continue
        hi, lo = -1e18, 1e18
        while j < len(ts) and ts[j] < ct:
            if prev_ct is None or ts[j] >= prev_ct:
                hi, lo = max(hi, bars[ts[j]][1]), min(lo, bars[ts[j]][2])
            j += 1
        if prev_ct is not None and hi > lo:
            closes.append((d, c, hi, lo))
        prev_ct = ct
    rets = []
    for (d0, c0, _, _), (d1, c1, h1, l1) in zip(closes, closes[1:]):
        if (d1 - d0).days <= 5:
            rets.append((d1, c1 / c0 - 1, c1, h1, l1))
    ymd = {}
    for d, r, *_ in rets:
        ymd.setdefault(d.year, []).append(r * BPS)
    ymd = {y: vs.mean(v) for y, v in ymd.items()}
    ndow = 7 if kind == "crypto" else 5
    for k in range(ndow):
        out[f"D{k}"] = [(d, r * BPS - ymd[d.year], r * BPS) for d, r, *_ in rets if d.weekday() == k]
    sig = {"S3D": [], "S3U": [], "IBSL": [], "IBSH": [], "BH20": [], "BL20": []}
    for i in range(20, len(rets) - 1):
        d, r, c, h, l = rets[i]
        nd, nr = rets[i + 1][0], rets[i + 1][1]
        if (nd - d).days > 5:
            continue
        x = (nr * BPS - ymd[nd.year], nr * BPS)
        last3 = [rets[i - k][1] for k in range(3)]
        if all(v < 0 for v in last3):
            sig["S3D"].append((nd, *x))
        if all(v > 0 for v in last3):
            sig["S3U"].append((nd, *x))
        ibs = (c - l) / (h - l)
        if ibs < 0.2:
            sig["IBSL"].append((nd, *x))
        if ibs > 0.8:
            sig["IBSH"].append((nd, *x))
        win = [rets[i - k][2] for k in range(20)]
        if c >= max(win):
            sig["BH20"].append((nd, *x))
        if c <= min(win):
            sig["BL20"].append((nd, *x))
    out.update(sig)
    cover = {"first": str(days[0]), "last": str(days[-1]), "days": len(days)}
    return out, cover


def period_of(sym):
    return PERIODS["crypto" if INSTR[sym][0] == "crypto" else "histdata"]


def stats(rows, lo, hi):
    sel = [(d, e, r) for d, e, r in rows if lo <= d <= hi]
    if len(sel) < 30:
        return None
    e = [x for _, x, _ in sel]
    t = vs.nw_t(e, 5)
    return {"n": len(sel), "mean_excess_bps": vs.mean(e), "mean_raw_bps": vs.mean([x for *_, x in sel]), "t_hac": t,
            "p_two_sided": 2 * (1 - vs.N01.cdf(abs(t))) if t == t else 1.0}


def discover():
    res, cover = {}, {}
    for sym in INSTR:
        s, cov = series(sym)
        cover[sym] = cov
        lo, hi = period_of(sym)["discover"]
        wd = {d for rows in s.values() for d, _, _ in rows if lo <= d <= hi}
        for name, rows in s.items():
            st = stats(rows, lo, hi)
            if st is None:
                continue
            if name.startswith("H") and st["n"] < 0.8 * len(wd):
                continue
            res[f"{sym}:{name}"] = st
        print(sym, cov, flush=True)
    q = vs.bh({k: v["p_two_sided"] for k, v in res.items()})
    for k in res:
        res[k]["q_bh"] = q[k]
        res[k]["discovered"] = q[k] < 0.10
        res[k]["sign"] = 1 if res[k]["mean_excess_bps"] > 0 else -1
        res[k]["previously_examined_window"] = tuple(k.split(":")) in SEEN
    found = {k: v for k, v in res.items() if v["discovered"]}
    json.dump({"n_candidates": len(res), "n_discovered": len(found), "coverage": cover, "candidates": res},
              open(os.path.join(OUT, "scan_discovery.json"), "w"), indent=1, default=str)
    print("candidates", len(res), "discovered", len(found))
    for k, v in sorted(found.items(), key=lambda kv: kv[1]["q_bh"]):
        print(f"  {k:18s} n={v['n']:5d} excess={v['mean_excess_bps']:7.2f} raw={v['mean_raw_bps']:7.2f} t={v['t_hac']:6.2f} q={v['q_bh']:.4f}"
              f"{'  (seen)' if v['previously_examined_window'] else ''}")


def confirm():
    disc = json.load(open(os.path.join(OUT, "scan_discovery.json")))
    found = {k: v for k, v in disc["candidates"].items() if v["discovered"]}
    by_sym = {}
    for k in found:
        by_sym.setdefault(k.split(":")[0], []).append(k.split(":")[1])
    res = {}
    for sym, names in by_sym.items():
        s, _ = series(sym)
        lo, hi = period_of(sym)["confirm"]
        cost = INSTR[sym][3]
        for name in names:
            key = f"{sym}:{name}"
            sign = found[key]["sign"]
            sel = [(d, e, r) for d, e, r in s.get(name, []) if lo <= d <= hi]
            if len(sel) < 30:
                res[key] = {"n": len(sel), "note": "too few observations"}
                continue
            e = [sign * x for _, x, _ in sel]
            t = vs.nw_t(e, 5)
            net = [sign * r - cost for *_, r in sel]
            res[key] = {"n": len(sel), "sign": sign, "mean_excess_signed_bps": vs.mean(e), "t_hac": t,
                        "p_one_sided": 1 - vs.N01.cdf(t), "net_raw_signed_bps": vs.mean(net), "cost_bps": cost,
                        "discovery": {x: found[key][x] for x in ("n", "mean_excess_bps", "mean_raw_bps", "t_hac", "q_bh")},
                        "previously_examined_window": found[key]["previously_examined_window"]}
    ok = {k: v["p_one_sided"] for k, v in res.items() if "p_one_sided" in v}
    holm = vs.holm(ok) if ok else {}
    for k, v in res.items():
        if k in holm:
            v["p_holm"] = holm[k]
            v["verdict"] = ("CONFIRMED" if holm[k] < 0.05 and v["mean_excess_signed_bps"] > 0 and v["net_raw_signed_bps"] > 0
                            else "WEAK" if v["p_one_sided"] < 0.05 else "NOT CONFIRMED")
    json.dump({"n_discovered": len(found), "results": res}, open(os.path.join(OUT, "scan_confirmation.json"), "w"), indent=1, default=str)
    for k, v in sorted(res.items(), key=lambda kv: kv[1].get("p_one_sided", 1)):
        if "p_one_sided" in v:
            print(f"{k:18s} {v['verdict']:14s} n={v['n']:5d} signed_excess={v['mean_excess_signed_bps']:7.2f} t={v['t_hac']:5.2f} "
                  f"p={v['p_one_sided']:.4f} holm={v['p_holm']:.4f} net={v['net_raw_signed_bps']:7.2f}")


if __name__ == "__main__":
    {"discover": discover, "confirm": confirm}[sys.argv[1]]()
