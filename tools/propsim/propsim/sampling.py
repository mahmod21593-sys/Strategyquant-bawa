"""Ways of generating day paths for challenge simulation."""

from __future__ import annotations

import random
from dataclasses import replace
from datetime import date, timedelta
from typing import Iterator

from .engine import Day


def historical_paths(days: list[Day], step: int = 1) -> Iterator[list[Day]]:
    """Start a challenge on every ``step``-th weekday of the history and replay forward."""
    for start in range(0, len(days), max(1, step)):
        if days[start].date.weekday() < 5:
            yield days[start:]


def stationary_bootstrap(
    days: list[Day],
    rng: random.Random,
    mean_block: float = 5.0,
    max_days: int = 2520,
    start: date = date(2001, 1, 1),
) -> Iterator[Day]:
    """Politis & Romano (1994) stationary bootstrap over whole days.

    Blocks of consecutive days (geometric length, mean ``mean_block``) keep short-term
    clustering of good and bad days. Dates are re-stamped as consecutive weekdays so
    calendar rules (time limits, payout intervals) behave normally.
    """
    if not days:
        return
    n = len(days)
    p_new = 1.0 / max(mean_block, 1.0)
    idx = rng.randrange(n)
    d = start
    for _ in range(max_days):
        while d.weekday() >= 5:
            d += timedelta(days=1)
        yield replace(days[idx], date=d)
        d += timedelta(days=1)
        idx = rng.randrange(n) if rng.random() < p_new else (idx + 1) % n
