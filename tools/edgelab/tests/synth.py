"""Synthetic bar generators with planted effects, for tests."""

import math
import random
from datetime import date, datetime, time, timedelta

from edgelab.bars import Bar


def weekdays(start: date, n: int):
    d = start
    out = []
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def intraday_sessions(n_days: int, seed: int = 1, momentum: float = 0.0, bar_min: int = 5,
                      open_t: time = time(9, 30), close_t: time = time(16, 0), vol_bps: float = 8.0):
    """Session bars; the last 30 minutes drift by `momentum` x the rest-of-day return."""
    rng = random.Random(seed)
    bars, price = [], 100.0
    n_bars = int((datetime.combine(date.today(), close_t) - datetime.combine(date.today(), open_t)).seconds / 60 / bar_min)
    last_n = 30 // bar_min
    for d in weekdays(date(2019, 1, 1), n_days):
        price *= math.exp(rng.gauss(0, 0.004))  # overnight gap
        day_start = price
        for i in range(n_bars):
            ts = datetime.combine(d, open_t) + timedelta(minutes=bar_min * i)
            if i == n_bars - last_n:
                rest = math.log(price / day_start)
            drift = momentum * rest / last_n if i >= n_bars - last_n else 0.0
            vol = vol_bps / 1e4 * rng.choice((0.5, 1.0, 2.0)) if i == 0 else vol_bps / 1e4
            o = price
            c = o * math.exp(drift + rng.gauss(0, vol))
            h = max(o, c) * (1 + abs(rng.gauss(0, vol / 2)))
            l = min(o, c) * (1 - abs(rng.gauss(0, vol / 2)))
            bars.append(Bar(ts, o, h, l, c))
            price = c
    return bars


def daily_bars(n_days: int, seed: int = 1, drift_bps: float = 2.0, vol_bps: float = 100.0,
               ibs_edge_bps: float = 0.0, tom_edge_bps: float = 0.0, ar: float = 0.0, trend_regimes: float = 0.0):
    """Daily bars with optional planted effects."""
    rng = random.Random(seed)
    out, price, prev_r, prev_ibs = [], 100.0, 0.0, 0.5
    dates = weekdays(date(2005, 1, 3), n_days)
    regime = 0.0
    for i, d in enumerate(dates):
        if trend_regimes and i % 60 == 0:
            regime = rng.choice((-1, 1)) * trend_regimes
        month_days = [x for x in dates if (x.year, x.month) == (d.year, d.month)]
        is_tom = d in month_days[:3] or d == month_days[-1]
        r = (drift_bps + regime + (ibs_edge_bps if prev_ibs < 0.2 else 0.0)
             + (tom_edge_bps if is_tom else 0.0)) / 1e4 + ar * prev_r + rng.gauss(0, vol_bps / 1e4)
        o = price
        c = o * math.exp(r)
        h = max(o, c) * (1 + abs(rng.gauss(0, vol_bps / 2e4)))
        l = min(o, c) * (1 - abs(rng.gauss(0, vol_bps / 2e4)))
        out.append(Bar(datetime.combine(d, time()), o, h, l, c))
        prev_ibs = (c - l) / (h - l) if h > l else 0.5
        prev_r = r - drift_bps / 1e4 - regime
        price = c
    return out


def write_csv(path, bars, header="Date,Time,Open,High,Low,Close,Volume"):
    lines = [header] if header else []
    for b in bars:
        lines.append(f"{b.ts:%Y.%m.%d},{b.ts:%H:%M},{b.o:.5f},{b.h:.5f},{b.l:.5f},{b.c:.5f},100")
    path.write_text("\n".join(lines) + "\n")
