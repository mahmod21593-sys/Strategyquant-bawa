"""Small statistics toolkit (standard library only)."""

from __future__ import annotations

import math
from datetime import date
from typing import Iterable, Optional, Sequence


def mean(x: Sequence[float]) -> float:
    return sum(x) / len(x) if x else math.nan


def sd(x: Sequence[float]) -> float:
    n = len(x)
    if n < 2:
        return math.nan
    m = mean(x)
    return math.sqrt(sum((v - m) ** 2 for v in x) / (n - 1))


def tstat(x: Sequence[float]) -> float:
    s = sd(x)
    return mean(x) / (s / math.sqrt(len(x))) if s and s == s and s > 0 else math.nan


def nw_tstat(x: Sequence[float], lags: int) -> float:
    """t-stat of the mean with a Newey-West (Bartlett) long-run variance, for overlapping returns."""
    n = len(x)
    if n < 3:
        return math.nan
    m = mean(x)
    e = [v - m for v in x]
    lrv = sum(v * v for v in e) / n
    for k in range(1, min(lags, n - 1) + 1):
        w = 1.0 - k / (lags + 1)
        lrv += 2 * w * sum(e[i] * e[i - k] for i in range(k, n)) / n
    return m / math.sqrt(lrv / n) if lrv > 0 else math.nan


def welch_t(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) < 2 or len(b) < 2:
        return math.nan
    va, vb = sd(a) ** 2 / len(a), sd(b) ** 2 / len(b)
    return (mean(a) - mean(b)) / math.sqrt(va + vb) if va + vb > 0 else math.nan


def ols(y: Sequence[float], x: Sequence[float]) -> dict:
    """Simple regression y = a + b x with White (HC1) standard error on b."""
    n = len(y)
    if n < 3:
        return {"n": n, "beta": math.nan, "t": math.nan, "r2": math.nan}
    mx, my = mean(x), mean(y)
    sxx = sum((v - mx) ** 2 for v in x)
    if sxx == 0:
        return {"n": n, "beta": math.nan, "t": math.nan, "r2": math.nan}
    beta = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx
    alpha = my - beta * mx
    resid = [b - alpha - beta * a for a, b in zip(x, y)]
    var_b = n / (n - 2) * sum(((a - mx) * e) ** 2 for a, e in zip(x, resid)) / sxx**2
    syy = sum((v - my) ** 2 for v in y)
    r2 = 1 - sum(e * e for e in resid) / syy if syy > 0 else math.nan
    return {"n": n, "alpha": alpha, "beta": beta, "t": beta / math.sqrt(var_b) if var_b > 0 else math.nan, "r2": r2}


def autocorr(x: Sequence[float], lag: int = 1) -> float:
    n = len(x)
    if n <= lag + 1:
        return math.nan
    m = mean(x)
    den = sum((v - m) ** 2 for v in x)
    num = sum((x[i] - m) * (x[i - lag] - m) for i in range(lag, n))
    return num / den if den > 0 else math.nan


def variance_ratio(r: Sequence[float], q: int) -> tuple[float, float]:
    """Lo & MacKinlay (1988) variance ratio with overlapping sums and the heteroskedasticity-robust z*."""
    nq = len(r)
    if q < 2 or nq < 4 * q:
        return math.nan, math.nan
    mu = mean(r)
    dev = [v - mu for v in r]
    ss = sum(d * d for d in dev)
    var_a = ss / (nq - 1)
    csum = [0.0]
    for v in r:
        csum.append(csum[-1] + v)
    m = q * (nq - q + 1) * (1 - q / nq)
    var_c = sum((csum[k] - csum[k - q] - q * mu) ** 2 for k in range(q, nq + 1)) / m
    vr = var_c / var_a if var_a > 0 else math.nan
    sq = [d * d for d in dev]
    theta = 0.0
    for j in range(1, q):
        delta = nq * sum(sq[k] * sq[k - j] for k in range(j, nq)) / ss**2
        theta += (2 * (q - j) / q) ** 2 * delta
    z = math.sqrt(nq) * (vr - 1) / math.sqrt(theta) if theta > 0 else math.nan
    return vr, z


def year_consistency(dates: Iterable[date], values: Iterable[float], sign: int = 1,
                     baseline: Optional[dict[int, float]] = None, min_obs: int = 5) -> tuple[float, int]:
    """Share of calendar years whose mean has the predicted sign (optionally vs a per-year baseline)."""
    groups: dict[int, list[float]] = {}
    for d, v in zip(dates, values):
        groups.setdefault(d.year, []).append(v)
    years = [y for y, vals in groups.items() if len(vals) >= min_obs]
    if not years:
        return math.nan, 0
    hits = 0
    for y in years:
        m = mean(groups[y]) - (baseline.get(y, 0.0) if baseline else 0.0)
        hits += (m * sign) > 0
    return hits / len(years), len(years)


def yearly_means(dates: Iterable[date], values: Iterable[float]) -> dict[int, float]:
    groups: dict[int, list[float]] = {}
    for d, v in zip(dates, values):
        groups.setdefault(d.year, []).append(v)
    return {y: mean(v) for y, v in groups.items()}


def terciles(values: Sequence[float]) -> tuple[float, float]:
    s = sorted(values)
    n = len(s)
    return s[n // 3], s[(2 * n) // 3]


def bucket3(v: float, cuts: tuple[float, float]) -> str:
    return "low" if v < cuts[0] else ("mid" if v < cuts[1] else "high")
