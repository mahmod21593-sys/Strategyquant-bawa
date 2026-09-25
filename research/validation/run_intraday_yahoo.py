"""Intraday primaries on Yahoo 60-minute bars (PREREGISTRATION.md amendment A2): P7y, P8y, P9y, P13y, P15y."""
from __future__ import annotations

import json
import math
import os
import subprocess
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import vstats as vs

OUT = os.path.join(os.path.dirname(__file__), "results")
CACHE = os.environ.get("YAHOO_CACHE", "/tmp/yahoo_cache")
NY, LDN = ZoneInfo("America/New_York"), ZoneInfo("Europe/London")
BPS = 1e4


def bars60(sym):
    path = os.path.join(CACHE, "h60_" + sym.replace("=", "_").replace("^", "_") + ".json")
    if not os.path.exists(path):
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?range=730d&interval=60m"
        for a in range(6):
            r = subprocess.run(["curl", "-sS", "-m", "60", "-A", "Mozilla/5.0", url], capture_output=True, text=True)
            try:
                if json.loads(r.stdout)["chart"]["result"]:
                    open(path, "w").write(r.stdout)
                    break
            except Exception:
                pass
            time.sleep(3 + 3 * a)
    d = json.load(open(path))["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    out = {}
    for i, t in enumerate(d["timestamp"]):
        o, c = q["open"][i], q["close"][i]
        if o and c:
            out[datetime.fromtimestamp(t, timezone.utc)] = (o, c)
    return out


def us_series(sym):
    b = bars60(sym)
    days = {}
    for ts, (o, c) in b.items():
        loc = ts.astimezone(NY)
        days.setdefault(loc.date(), {})[loc.strftime("%H:%M")] = (o, c)
    rows = []
    for d in sorted(days):
        x = days[d]
        if "09:30" in x and "15:30" in x:
            rows.append((d, x["09:30"][1], x["15:30"][0], x["15:30"][1]))  # 10:30 price, 15:30 price, close
    out = []
    for prev, cur, nxt in zip(rows, rows[1:], rows[2:] + [None]):
        pc = prev[3]
        d, p1030, p1530, close = cur
        out.append({"date": d, "r1": p1030 / pc - 1, "rod": p1530 / pc - 1, "lh": close / p1530 - 1,
                    "next": (nxt[3] / close - 1) if nxt else None})
    return out


def pooled(per_symbol):
    g = {}
    for rows in per_symbol.values():
        for d, v in rows:
            g.setdefault(d, []).append(v)
    ds = sorted(g)
    return ds, [vs.mean(g[d]) for d in ds]


def fx_series(sym, usd_base):
    b = bars60(sym)

    def price(t):
        if t in b:
            return b[t][0]
        prev = t - timedelta(hours=1)
        return b[prev][1] if prev in b else None

    dates = sorted({ts.astimezone(LDN).date() for ts in b})
    out = []
    for d in dates:
        if d.weekday() >= 5:
            continue
        ta = datetime(d.year, d.month, d.day, 8, tzinfo=LDN).astimezone(timezone.utc)
        tb = datetime(d.year, d.month, d.day, 16, tzinfo=LDN).astimezone(timezone.utc)
        tc = datetime(d.year, d.month, d.day, 17, tzinfo=NY).astimezone(timezone.utc)
        tp = datetime(d.year, d.month, d.day, 17, tzinfo=NY).astimezone(timezone.utc) - timedelta(days=1)
        tt = datetime(d.year, d.month, d.day, 1, tzinfo=timezone.utc)  # ~ Tokyo 10:00 JST (fix 09:55)
        pa, pb, pc, pp, pt = (price(x) for x in (ta, tb, tc, tp, tt))
        s = 1 if usd_base else -1  # USD appreciation sign
        rec = {"date": d}
        if pa and pb:
            rec["w3"] = s * math.log(pb / pa)
        if pb and pc:
            rec["w4"] = s * math.log(pc / pb)
        if pp and pt:
            rec["w1"] = s * math.log(pt / pp)
        if pt and pa:
            rec["w2"] = s * math.log(pa / pt)
        out.append(rec)
    return out


SERIES = {}


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {}
    us = {s: us_series(s) for s in ["SPY", "QQQ", "IWM", "DIA"]}
    per7, per8, per9, per13 = {}, {}, {}, {}
    for s, rows in us.items():
        per7[s] = [(r["date"], (1 if r["rod"] > 0 else -1) * r["lh"] * BPS) for r in rows]
        per8[s] = [(r["date"], (1 if r["r1"] > 0 else -1) * r["lh"] * BPS) for r in rows]
        sel = []
        for i, r in enumerate(rows):
            if i >= 60:
                thr = vs.sd([x["rod"] for x in rows[i - 60:i]])
                if abs(r["rod"]) > thr:
                    sel.append((r["date"], (1 if r["rod"] > 0 else -1) * r["lh"] * BPS))
        per9[s] = sel
        per13[s] = [(r["date"], -(1 if r["lh"] > 0 else -1) * r["next"] * BPS) for r in rows if r["next"] is not None]
    for key, per, cost in (("P7y", per7, 1.5), ("P8y", per8, 1.5), ("P9y", per9, 1.5), ("P13y", per13, 1.5)):
        ds, ps = pooled({k: v for k, v in per.items()})
        r = vs.summarize(ds, ps, 1, 5, cost)
        SERIES[key] = {"dates": [str(d) for d in ds], "pnl_bps": ps, "cost_bps": cost, "lag": 5}
        r["per_symbol"] = {k: vs.summarize([d for d, _ in v], [x for _, x in v], 1, 5, cost, boot=False) for k, v in per.items()}
        res[key] = r
    pairs = {"EURUSD=X": False, "GBPUSD=X": False, "AUDUSD=X": False, "NZDUSD=X": False,
             "JPY=X": True, "CHF=X": True, "CAD=X": True, "NOK=X": True, "SEK=X": True}
    fx = {p: fx_series(p, base) for p, base in pairs.items()}
    comb, win = {}, {w: {} for w in ("w1", "w2", "w3", "w4")}
    per_pair = {}
    for p, rows in fx.items():
        pp = []
        for r in rows:
            for w in win:
                if w in r:
                    win[w].setdefault(r["date"], []).append(r[w] * BPS)
            if "w3" in r and "w4" in r:
                v = (r["w3"] - r["w4"]) * BPS - 2 * 1.0
                comb.setdefault(r["date"], []).append(v)
                pp.append((r["date"], v))
        per_pair[p] = vs.summarize([d for d, _ in pp], [x for _, x in pp], 1, 5, 0.0, boot=False)
    ds = sorted(comb)
    r = vs.summarize(ds, [vs.mean(comb[d]) for d in ds], 1, 5, 0.0)
    SERIES["P15y"] = {"dates": [str(d) for d in ds], "pnl_bps": [vs.mean(comb[d]) for d in ds], "cost_bps": 0.0, "lag": 5}
    r["note"] = "daily basket P&L already net of 2 x 1.0 bps (two windows)"
    r["per_pair_net"] = per_pair
    exp = {"w1": 1, "w2": -1, "w3": 1, "w4": -1}
    r["windows_usd_bps_per_day"] = {w: dict(vs.summarize(sorted(v), [vs.mean(v[d]) for d in sorted(v)], exp[w], 5, 0.0, boot=False),
                                            expected_sign=exp[w]) for w, v in win.items()}
    res["P15y"] = r
    json.dump(res, open(os.path.join(OUT, "intraday_yahoo.json"), "w"), indent=2, default=str)
    json.dump(SERIES, open(os.path.join(OUT, "series_intraday.json"), "w"), default=str)
    for k, v in res.items():
        print(k, "n", v["n"], "mean", round(v["mean_bps"], 2), "net", round(v["net_mean_bps"], 2), "t", round(v["t_hac"], 2),
              "p1", round(v["p_one_sided"], 4), "ci", [round(x, 2) for x in v["ci95_bps"]], "yrs", v["years_pred_sign"])
        for s, x in (v.get("per_symbol") or v.get("per_pair_net") or {}).items():
            print("    ", s, "n", x["n"], "mean", round(x["mean_bps"], 2), "t", round(x["t_hac"], 2))
    for w, x in res["P15y"]["windows_usd_bps_per_day"].items():
        print("  FX", w, "expected", x["expected_sign"], "USD bps/day", round(x["mean_bps"], 2), "t", round(x["t_hac"], 2))


if __name__ == "__main__":
    main()
