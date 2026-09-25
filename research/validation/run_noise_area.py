"""Family N (PREREGISTRATION.md A11): noise-area intraday momentum (Zarattini, Aziz & Barbon 2025).

-> results/noise_area.json, results/series_noise_area.json
"""
from __future__ import annotations

import json
import math
import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import vstats as vs
from data_histdata import NY, available_years, table

OUT = os.path.join(os.path.dirname(__file__), "results")
BPS = 1e4
BER = ZoneInfo("Europe/Berlin")
PAPER_END = date(2024, 4, 30)
SERIES = {}

# id: (symbol, tz, open (h, m), close (h, m), first mark, last mark, cost bps, variant)
TESTS = {
    "N1": ("SPXUSD", NY, (9, 30), (16, 0), (10, 0), (15, 30), 1.5, "flip"),
    "N2": ("SPXUSD", NY, (9, 30), (16, 0), (10, 0), (15, 30), 1.5, "twap_stop"),
    "N3": ("NSXUSD", NY, (9, 30), (16, 0), (10, 0), (15, 30), 1.5, "flip"),
    "N4": ("GRXEUR", BER, (9, 0), (17, 30), (9, 30), (17, 0), 1.5, "flip"),
    "N5": ("XAUUSD", NY, (8, 20), (13, 30), (9, 0), (13, 0), 2.5, "flip"),
}


def local_sessions(sym, tz, open_hm, close_hm, y0=2013):
    """{local date: {local minute: (o, h, l, c)}} for minutes in [open-1, close] (local time)."""
    o_min, c_min = open_hm[0] * 60 + open_hm[1], close_hm[0] * 60 + close_hm[1]
    if tz is NY:
        keep = set(range(o_min - 1, c_min + 1))
        return table(sym, available_years(sym, range(y0, 2026)), keep)
    keep = set(range(60, 13 * 60))  # NY 01:00-13:00 covers Berlin 09:00-17:30 in every DST combination
    raw = table(sym, available_years(sym, range(y0, 2026)), keep)
    out = {}
    for d, bars in raw.items():
        off = int((datetime(d.year, d.month, d.day, 12, tzinfo=NY).astimezone(tz).utcoffset()
                   - datetime(d.year, d.month, d.day, 12, tzinfo=NY).utcoffset()).total_seconds() // 60)
        for m, v in bars.items():
            lm = m + off
            if o_min - 1 <= lm <= c_min:
                out.setdefault(d, {})[lm] = v
    return out


def p_at(bars, m):
    if m - 1 in bars:
        return bars[m - 1][3]
    if m in bars:
        return bars[m][0]
    for k in (2,):
        if m - k in bars:
            return bars[m - k][3]
    return None


def run(test, lookback=14, grid=30, cost=None, variant=None, y0=2013, spec=None, path=False):
    sym, tz, open_hm, close_hm, first, last, cost0, variant0 = spec or TESTS[test]
    cost = cost0 if cost is None else cost
    variant = variant0 if variant is None else variant
    o_min, c_min = open_hm[0] * 60 + open_hm[1], close_hm[0] * 60 + close_hm[1]
    marks = (list(range(first[0] * 60 + first[1], last[0] * 60 + last[1] + 1, 30)) if grid == 30   # pre-registered marks
             else list(range(o_min + grid, c_min, grid)))
    ses = local_sessions(sym, tz, open_hm, close_hm, y0)
    days = sorted(d for d, b in ses.items() if d.weekday() < 5 and o_min in b and c_min - 1 in b)
    info = []
    for d in days:
        b = ses[d]
        o, c = p_at(b, o_min), p_at(b, c_min)
        mk = {m: p_at(b, m) for m in marks}
        info.append((d, o, c, mk, b))
    out, trades_total = [], 0
    for i in range(lookback + 1, len(info)):
        d, o, c, mk, b = info[i]
        prev_close = info[i - 1][2]
        if not (o and c and prev_close) or (d - info[i - 1][0]).days > 5:
            continue
        sig = {}
        for m in marks:
            mv = [abs(x[3][m] / x[1] - 1) for x in info[i - lookback:i] if x[3].get(m) and x[1]]
            sig[m] = vs.mean(mv) if len(mv) >= max(5, round(lookback * 10 / 14)) else None
        pos, entry, pnl, trades = 0, None, 0.0, 0
        tw_sum, tw_cnt, cursor = 0.0, 0, o_min
        lo_path, hi_path = 0.0, 0.0
        for m in marks + [c_min]:
            while cursor < m:  # TWAP of minute closes from the open up to this mark; open-trade excursions
                if cursor in b:
                    tw_sum += b[cursor][3]
                    tw_cnt += 1
                    if path and pos != 0:
                        worst = b[cursor][2] if pos == 1 else b[cursor][1]
                        best = b[cursor][1] if pos == 1 else b[cursor][2]
                        lo_path = min(lo_path, pnl + pos * (worst / entry - 1))
                        hi_path = max(hi_path, pnl + pos * (best / entry - 1))
                cursor += 1
            if m == c_min:
                break
            p = mk[m]
            if p is None or sig[m] is None:
                continue
            ub, lb = max(o, prev_close) * (1 + sig[m]), min(o, prev_close) * (1 - sig[m])
            stopped = False
            if variant == "twap_stop" and pos != 0:
                twap = tw_sum / tw_cnt if tw_cnt else p
                if (pos == 1 and p < max(ub, twap)) or (pos == -1 and p > min(lb, twap)):
                    pnl += pos * (p / entry - 1)
                    pos, stopped = 0, True
            if stopped:
                continue
            if pos == 0:
                if p > ub:
                    pos, entry, trades = 1, p, trades + 1
                elif p < lb:
                    pos, entry, trades = -1, p, trades + 1
            elif pos == 1 and p < lb:
                pnl += p / entry - 1
                pos, entry, trades = -1, p, trades + 1
            elif pos == -1 and p > ub:
                pnl += -(p / entry - 1)
                pos, entry, trades = 1, p, trades + 1
        if pos != 0:
            pnl += pos * (c / entry - 1)
        if path:
            k = cost * trades / BPS
            out.append((d, (pnl - k, min(lo_path, pnl) - k, max(hi_path, pnl))))
        else:
            out.append((d, pnl * BPS - cost * trades))
        trades_total += trades
    return out, trades_total, cost


def summarize(key, rows, lo, hi, boot=False):
    sel = [(d, x) for d, x in rows if lo <= d <= hi]
    r = vs.summarize([d for d, _ in sel], [x for _, x in sel], 1, 5, 0.0, boot=boot)
    if sel:
        x = [v for _, v in sel]
        r["sharpe_annual"] = vs.mean(x) / vs.sd(x) * math.sqrt(252) if vs.sd(x) > 0 else None
    return r


def main():
    res = {}
    for k in TESTS:
        rows, ntr, cost = run(k)
        SERIES[k] = {"dates": [str(d) for d, _ in rows], "pnl_bps_net": [x for _, x in rows]}
        r = summarize(k, rows, date(2014, 1, 1), date(2025, 12, 31), boot=True)
        r["in_paper_2014_2024_04"] = summarize(k, rows, date(2014, 1, 1), PAPER_END)
        r["post_paper_2024_05_2025"] = summarize(k, rows, PAPER_END + timedelta(days=1), date(2025, 12, 31))
        yr = {}
        for d, x in rows:
            yr.setdefault(d.year, []).append(x)
        r["per_year_mean_bps"] = {y: round(vs.mean(v), 2) for y, v in sorted(yr.items())}
        r["entries_per_day"] = ntr / len(rows) if rows else None
        r["cost_bps_per_entry"] = cost
        res[k] = r
    fam = {k: v["p_one_sided"] for k, v in res.items()}
    holm = vs.holm(fam)
    for k, v in res.items():
        v["p_holm_N"] = holm[k]
        post = v["post_paper_2024_05_2025"].get("mean_bps", -1)
        ok = v["mean_bps"] > 0 and holm[k] < 0.05 and post > 0
        v["verdict"] = "CONFIRMED" if ok else "WEAK" if v["p_one_sided"] < 0.05 else "NOT CONFIRMED"
    json.dump(res, open(os.path.join(OUT, "noise_area.json"), "w"), indent=1, default=str)
    json.dump(SERIES, open(os.path.join(OUT, "series_noise_area.json"), "w"), default=str)
    for k, v in res.items():
        a, b = v["in_paper_2014_2024_04"], v["post_paper_2024_05_2025"]
        print(f"{k} {v['verdict']:13s} n={v['n']} net/day={v['mean_bps']:.2f} t={v['t_hac']:.2f} p={v['p_one_sided']:.4f} holm={v['p_holm_N']:.4f} "
              f"SR={v['sharpe_annual']:.2f} entries/day={v['entries_per_day']:.2f} | paper-period {a['mean_bps']:.2f} (t {a['t_hac']:.2f}, SR {a['sharpe_annual']:.2f}) "
              f"| after {b['mean_bps']:.2f} (t {b['t_hac']:.2f})")
        print("    per year", v["per_year_mean_bps"])


if __name__ == "__main__":
    main()
