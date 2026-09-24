from datetime import date, timedelta

from propsim.engine import Day
from propsim.rules import Funded, Phase, Rules

MONDAY = date(2024, 1, 1)


def weekdays(n: int, start: date = MONDAY) -> list[date]:
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def make_days(pnls, lows=None, highs=None, traded=True) -> list[Day]:
    dates = weekdays(len(pnls))
    lows = lows or [min(0.0, p) for p in pnls]
    highs = highs or [max(0.0, p) for p in pnls]
    return [Day(d, p, lo, hi, traded, 1) for d, p, lo, hi in zip(dates, pnls, lows, highs)]


def rules(**kw) -> Rules:
    base = dict(
        name="test",
        initial_balance=100_000,
        phases=[Phase("P1", 0.10)],
        max_loss=0.10,
    )
    base.update(kw)
    return Rules(**base)


__all__ = ["Funded", "Phase", "make_days", "rules", "weekdays", "MONDAY"]
