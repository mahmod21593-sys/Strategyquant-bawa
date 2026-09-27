"""Round 36 (PREREGISTRATION.md A50): five published practitioner setups as their books state them — Williams' Oops!,
Raschke & Connors' Turtle Soup and 80-20s, DeMark's TD Sequential buy/sell setup, Dalton's Market Profile 80% rule —
on US500, US100, GER40, UK100, JP225 and XAUUSD cash sessions (HistData one-minute quotes, 2013 -> 2026-09-18).

    python3 run_round36.py   -> results/round36_practitioner_setups.json
"""
from __future__ import annotations

import json
import math
import os
from datetime import date
from zoneinfo import ZoneInfo

import numpy as np

import run_family_a as fa
import vstats as vs
from data_histdata import NY
from data_minutes import C, H, L, O
from run_round24 import clean_local, to_battery

OUT = os.path.join(os.path.dirname(__file__), "results")
fa.N_TRIALS = 14274
E = date(1970, 1, 1).toordinal()
START, END = date(2013, 1, 1), date(2026, 9, 18)
TSE_CUT = date(2024, 11, 5)
TOKYO, BERLIN, LONDON = ZoneInfo("Asia/Tokyo"), ZoneInfo("Europe/Berlin"), ZoneInfo("Europe/London")
# name: (HistData symbol, tz, cash open, cash close for a date (local minutes), cost per round trip, first year)
MARKETS = {
    "US500": ("SPXUSD", NY, 570, lambda d: 960, 1.5e-4, 2013),
    "US100": ("NSXUSD", NY, 570, lambda d: 960, 1.5e-4, 2013),
    "GER40": ("GRXEUR", BERLIN, 540, lambda d: 1050, 1.5e-4, 2013),
    "UK100": ("UKXGBP", LONDON, 480, lambda d: 990, 1.5e-4, 2013),
    "JP225": ("JPXJPY", TOKYO, 540, lambda d: 900 if d < TSE_CUT else 930, 3.0e-4, 2013),
    "XAUUSD": ("XAUUSD", NY, 500, lambda d: 810, 2.5e-4, 2012),
}
SETUPS = {"OO": ("close", "next_open"), "TS": ("next_close", "same_close"), "E8": ("same_close", "next_close"),
          "TD": ("hold5", "hold1"), "MP": ("limit", "time")}


class Session:
    __slots__ = ("d", "m", "x", "o", "h", "l", "c", "p")

    def __init__(self, d, m, x, cl):
        self.d, self.m, self.x = d, m, x
        self.o, self.h, self.l, self.c = x[0, O], x[:, H].max(), x[:, L].min(), x[-1, C]
        pre = np.nonzero(m < cl - 5)[0]
        self.p = x[pre[-1], C] if len(pre) else self.c  # price 5 minutes before the close


def sessions(name):
    sym, tz, op, close_of, _, y0 = MARKETS[name]
    t, x = clean_local(sym, range(y0, 2027), tz)
    day, mod = t // 1440, t % 1440
    st = np.r_[0, np.nonzero(np.diff(day))[0] + 1]
    en = np.r_[st[1:], len(day)]
    out = []
    for a, b in zip(st, en):
        d = date.fromordinal(int(day[a]) + E)
        if d.weekday() >= 5 or d > END:
            continue
        cl = close_of(d)
        m = mod[a:b]
        sel = np.nonzero((m >= op) & (m < cl))[0]
        if len(sel) < 0.6 * (cl - op) or m[sel[0]] > op + 2 or m[sel[-1]] < cl - 5:
            continue
        out.append(Session(d, m[sel], x[a + sel], cl))
    return out


def first_touch(s, level, above, start=0):
    """Index of the first bar at or after `start` whose high reaches `level` (above) or whose low reaches it."""
    hit = s.x[start:, H] >= level if above else s.x[start:, L] <= level
    k = np.nonzero(hit)[0]
    return start + int(k[0]) if len(k) else None


def ret(side, entry, exit_, cost):
    return side * (exit_ / entry - 1) - cost


def run_market(name):
    """{variant: {date: net pnl}} for the 5 setups x 2 sides x 2 choices; plus MP hit counts."""
    S = sessions(name)
    _, _, op, _, cost, _ = MARKETS[name]
    n = len(S)
    res = {f"{st}|{side}|{ch}": {} for st, chs in SETUPS.items() for side in ("long", "short") for ch in chs}
    mp_hits = {"long": [0, 0], "short": [0, 0]}

    def book(key, d, v):
        if START <= d <= END:
            res[key][d] = res[key].get(d, 0.0) + v

    for i in range(1, n):
        s, pv = S[i], S[i - 1]
        nxt = S[i + 1] if i + 1 < n else None
        # OO: Oops!
        for side, cond, lvl in ((1, s.o < pv.l, pv.l), (-1, s.o > pv.h, pv.h)):
            if cond:
                j = first_touch(s, lvl, side == 1)
                if j is not None:
                    e = max(lvl, s.x[j, O]) if side == 1 else min(lvl, s.x[j, O])
                    lab = "long" if side == 1 else "short"
                    book(f"OO|{lab}|close", s.d, ret(side, e, s.c, cost))
                    if nxt is not None:
                        book(f"OO|{lab}|next_open", s.d, ret(side, e, nxt.o, cost))
        # TS: Turtle Soup (20-session extreme set >= 4 sessions earlier; new extreme first, then the stop)
        if i >= 20:
            lows = np.array([S[k].l for k in range(i - 20, i)])
            highs = np.array([S[k].h for k in range(i - 20, i)])
            for side, ext, arr in ((1, lows.min(), lows), (-1, highs.max(), highs)):
                pos = int(np.nonzero(arr == ext)[0][-1]) + (i - 20)
                if i - pos < 4:
                    continue
                beyond = s.x[:, L] < ext if side == 1 else s.x[:, H] > ext
                k0 = np.nonzero(beyond)[0]
                if not len(k0):
                    continue
                j = first_touch(s, ext, side == 1, int(k0[0]) + 1)
                if j is None:
                    continue
                e = max(ext, s.x[j, O]) if side == 1 else min(ext, s.x[j, O])
                lab = "long" if side == 1 else "short"
                book(f"TS|{lab}|same_close", s.d, ret(side, e, s.c, cost))
                if nxt is not None:
                    book(f"TS|{lab}|next_close", s.d, ret(side, e, nxt.c, cost))
        # E8: 80-20s
        rng = pv.h - pv.l
        if rng > 0:
            top, bot = pv.l + 0.8 * rng, pv.l + 0.2 * rng
            for side, cond, lvl in ((1, pv.o >= top and pv.c <= bot, pv.l), (-1, pv.o <= bot and pv.c >= top, pv.h)):
                if not cond:
                    continue
                beyond = s.x[:, L] < lvl if side == 1 else s.x[:, H] > lvl
                k0 = np.nonzero(beyond)[0]
                if not len(k0):
                    continue
                j = first_touch(s, lvl, side == 1, int(k0[0]) + 1)
                if j is None:
                    continue
                e = max(lvl, s.x[j, O]) if side == 1 else min(lvl, s.x[j, O])
                lab = "long" if side == 1 else "short"
                book(f"E8|{lab}|same_close", s.d, ret(side, e, s.c, cost))
                if nxt is not None:
                    book(f"E8|{lab}|next_close", s.d, ret(side, e, nxt.c, cost))
        # TD: setup completes at nine, judged 5 minutes before the close (today's close = mark price)
        if i >= 13:
            c = [S[k].c for k in range(i - 13, i)] + [s.p]  # c[-1] is today (index 13)
            for side in (1, -1):
                below = [(c[k] < c[k - 4]) if side == 1 else (c[k] > c[k - 4]) for k in range(5, 14)]
                flip = not ((c[4] < c[0]) if side == 1 else (c[4] > c[0]))
                if all(below) and flip:
                    lab = "long" if side == 1 else "short"
                    for ch, hold in (("hold5", 5), ("hold1", 1)):
                        if i + hold < n:
                            book(f"TD|{lab}|{ch}", s.d, ret(side, s.p, S[i + hold].c, cost))
        # MP: value-area 80% rule
        w = (pv.h - pv.l) / 60
        if w > 0:
            marks = np.zeros(60)
            br = (pv.m - op) // 30
            for b in np.unique(br):
                sel = br == b
                lo_b = min(59, int((pv.x[sel, L].min() - pv.l) / w))
                hi_b = min(59, int((pv.x[sel, H].max() - pv.l) / w))
                marks[lo_b:hi_b + 1] += 1
            poc = int(np.argmax(marks))
            lo, hi, acc, tot = poc, poc, marks[poc], marks.sum()
            while acc < 0.7 * tot:
                up = marks[hi + 1] if hi < 59 else -1
                dn = marks[lo - 1] if lo > 0 else -1
                if up >= dn:
                    hi += 1
                    acc += up
                else:
                    lo -= 1
                    acc += dn
            val, vah = pv.l + lo * w, pv.l + (hi + 1) * w
            side = -1 if s.o > vah else 1 if s.o < val else 0
            if side:
                bs = (s.m - op) // 30
                ub = np.unique(bs)
                closes = [s.x[np.nonzero(bs == b)[0][-1], C] for b in ub]
                ends = [int(np.nonzero(bs == b)[0][-1]) for b in ub]
                for q in range(len(ub) - 2):
                    if val <= closes[q] <= vah and val <= closes[q + 1] <= vah:
                        k_e = ends[q + 1]
                        e = closes[q + 1]
                        tgt = vah if side == 1 else val
                        j = first_touch(s, tgt, side == 1, k_e + 1)
                        lab = "long" if side == 1 else "short"
                        mp_hits[lab][0] += 1
                        mp_hits[lab][1] += j is not None
                        book(f"MP|{lab}|limit", s.d, ret(side, e, tgt if j is not None else s.c, cost))
                        book(f"MP|{lab}|time", s.d, ret(side, e, s.c, cost))
                        break
    return res, mp_hits


def stats(v):
    x = np.array(v, dtype=float)
    t = vs.nw_t(list(x), 5)
    return {"n": int(len(x)), "mean_bps": float(x.mean() * 1e4), "t_hac": t, "p_one_sided": vs.p_one_sided(t),
            "sharpe": float(x.mean() / x.std(ddof=1) * math.sqrt(252)) if x.std(ddof=1) > 0 else None}


def main():
    from run_round10 import weekday_calendar
    cal = [d for d in weekday_calendar(START, END)]
    mid = cal[len(cal) // 2]
    per, hits, trades = {}, {}, {}
    for name in MARKETS:
        g, h = run_market(name)
        hits[name] = h
        for k, v in g.items():
            per[f"{name}|{k}"] = v
        trades[name] = {k: len(v) for k, v in g.items()}
        print("PS", name, {k: len(v) for k, v in g.items() if k.endswith(("|close", "|next_close", "|same_close", "|hold5", "|limit"))}, flush=True)

    def port(keys):
        out = np.zeros(len(cal))
        ci = {d: i for i, d in enumerate(cal)}
        for k in keys:
            for d, v in per[k].items():
                if d in ci:
                    out[ci[d]] += v / len(MARKETS)
        return out

    prim, series = {}, {}
    for st, chs in SETUPS.items():
        keys = [f"{m}|{st}|{side}|{chs[0]}" for m in MARKETS for side in ("long", "short")]
        p = port(keys)
        series[st] = p
        prim[st] = stats(p)
        prim[st]["halves_bps"] = (float(p[:len(cal) // 2].mean() * 1e4), float(p[len(cal) // 2:].mean() * 1e4))
        prim[st]["trades"] = int(sum(len(per[k]) for k in keys))
    holm = vs.holm({k: v["p_one_sided"] for k, v in prim.items()})
    for k in prim:
        prim[k]["p_holm"] = holm[k]
    # REV ensemble (round 11 build (c), US500 + US100 + JP225, equal weight) for the overlap check
    from run_round4 import irx_map
    from run_round11 import rev_leg
    rates = irx_map()
    keys_r = sorted(rates)
    rev = np.zeros(len(cal))
    ci = {d: i for i, d in enumerate(cal)}
    for s in ("SPXUSD", "NSXUSD", "JPXJPY"):
        for d, r in rev_leg(s, rates, keys_r, False).items():
            if d in ci:
                rev[ci[d]] += r[0] / 3
    verdict = {}
    for st, p in prim.items():
        ok = p["p_holm"] < 0.05 and all(h > 0 for h in p["halves_bps"])
        p["corr_with_REV"] = float(np.corrcoef(series[st], rev)[0, 1])
        verdict[st] = ("EDGE, SAME AS REV" if p["corr_with_REV"] >= 0.5 else "EDGE") if ok else "NO EDGE"
    res = {"primary": prim, "verdict": verdict, "mp_hit_rate": {m: {s: (h[1] / h[0] if h[0] else None, h[0]) for s, h in hs.items()}
                                                                  for m, hs in hits.items()}}
    res["by_setup_side"] = {f"{st}|{side}": stats(port([f"{m}|{st}|{side}|{chs[0]}" for m in MARKETS]))
                            for st, chs in SETUPS.items() for side in ("long", "short")}
    res["by_market_primary"] = {f"{m}|{st}": stats(np.array([per[f"{m}|{st}|long|{chs[0]}"].get(d, 0.0) + per[f"{m}|{st}|short|{chs[0]}"].get(d, 0.0)
                                                             for d in cal]))
                                for m in MARKETS for st, chs in SETUPS.items()}
    res["variants"] = {k: stats(list(v.values())) for k, v in per.items() if len(v) >= 10}
    res["share_variants_positive"] = float(np.mean([v["mean_bps"] > 0 for v in res["variants"].values()]))
    res["trades"] = trades
    res["battery"] = to_battery(per, "PS", START, mid, 2016)
    json.dump(res, open(os.path.join(OUT, "round36_practitioner_setups.json"), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("primary", "verdict", "mp_hit_rate", "by_setup_side", "share_variants_positive", "battery")},
                     indent=1, default=str))


if __name__ == "__main__":
    main()
