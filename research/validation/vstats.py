"""Statistics used by every validation test (standard library only). See PREREGISTRATION.md."""
from __future__ import annotations

import math
import random
from statistics import NormalDist
from typing import Callable, Sequence

N01 = NormalDist()
SEED = 20260925


def mean(x):
    return sum(x) / len(x) if x else math.nan


def sd(x):
    if len(x) < 2:
        return math.nan
    m = mean(x)
    return math.sqrt(sum((v - m) ** 2 for v in x) / (len(x) - 1))


def nw_t(x: Sequence[float], lag: int) -> float:
    """t-stat of the mean with a Newey-West (Bartlett) HAC variance."""
    n = len(x)
    if n < 10:
        return math.nan
    m = mean(x)
    e = [v - m for v in x]
    s = sum(v * v for v in e) / n
    for k in range(1, min(lag, n - 1) + 1):
        s += 2 * (1 - k / (lag + 1)) * sum(e[i] * e[i - k] for i in range(k, n)) / n
    return m / math.sqrt(s / n) if s > 0 else math.nan


def p_one_sided(t: float, sign: int = 1) -> float:
    if t != t:
        return math.nan
    return 1 - N01.cdf(sign * t)


def bootstrap_ci(x: Sequence[float], block: float = 10, reps: int = 2000, seed: int = SEED) -> tuple[float, float]:
    """Politis-Romano stationary bootstrap 95% CI for the mean."""
    n = len(x)
    if n < 20:
        return (math.nan, math.nan)
    rng = random.Random(seed)
    p = 1 / block
    means = []
    for _ in range(reps):
        i = rng.randrange(n)
        total = 0.0
        for _ in range(n):
            total += x[i]
            i = rng.randrange(n) if rng.random() < p else (i + 1) % n
        means.append(total / n)
    means.sort()
    return means[int(0.025 * reps)], means[int(0.975 * reps) - 1]


def randomization_p(observed: float, draw: Callable[[random.Random], float], reps: int = 5000, seed: int = SEED) -> float:
    rng = random.Random(seed)
    hits = sum(draw(rng) >= observed for _ in range(reps))
    return (hits + 1) / (reps + 1)


def year_share(dates, values, sign: int = 1, min_n: int = 5) -> tuple[float, int]:
    g: dict[int, list[float]] = {}
    for d, v in zip(dates, values):
        g.setdefault(d.year, []).append(v)
    ys = [y for y, v in g.items() if len(v) >= min_n]
    if not ys:
        return math.nan, 0
    return sum(sign * mean(g[y]) > 0 for y in ys) / len(ys), len(ys)


def moments(x):
    n = len(x)
    m = mean(x)
    s = sd(x)
    if not s or s != s:
        return math.nan, math.nan
    sk = sum(((v - m) / s) ** 3 for v in x) / n
    ku = sum(((v - m) / s) ** 4 for v in x) / n
    return sk, ku


def expected_max_z(n: int) -> float:
    g = 0.5772156649
    if n < 2:
        return 0.0
    return (1 - g) * N01.inv_cdf(1 - 1 / n) + g * N01.inv_cdf(1 - 1 / (n * math.e))


def deflated_sharpe(x: Sequence[float], n_trials: int) -> float:
    """Bailey & Lopez de Prado (2014) DSR with SR0 = E[max of n_trials null Sharpes], null SR s.e. = 1/sqrt(T-1)."""
    t = len(x)
    s = sd(x)
    if t < 20 or not s:
        return math.nan
    sr = mean(x) / s
    sk, ku = moments(x)
    sr0 = expected_max_z(n_trials) / math.sqrt(t - 1)
    denom = math.sqrt(max(1e-12, 1 - sk * sr + (ku - 1) / 4 * sr * sr))
    return N01.cdf((sr - sr0) * math.sqrt(t - 1) / denom)


def holm(pvals: dict[str, float]) -> dict[str, float]:
    items = sorted((p, k) for k, p in pvals.items() if p == p)
    m = len(items)
    out, running = {}, 0.0
    for i, (p, k) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out


def bh(pvals: dict[str, float]) -> dict[str, float]:
    items = sorted((p, k) for k, p in pvals.items() if p == p)
    m = len(items)
    out, running = {}, 1.0
    for i in range(m - 1, -1, -1):
        p, k = items[i]
        running = min(running, p * m / (i + 1))
        out[k] = running
    return out


def summarize(dates, pnl_bps, sign: int = 1, lag: int = 5, cost_bps: float = 0.0, per_trade_cost: bool = True,
              boot: bool = True) -> dict:
    """Standard block of statistics for a P&L series (bps per trade or per period)."""
    n = len(pnl_bps)
    if n < 10:
        return {"n": n}
    net = [v - cost_bps for v in pnl_bps] if per_trade_cost else list(pnl_bps)
    t = nw_t(pnl_bps, lag)
    ys, ny = year_share(dates, pnl_bps, sign)
    out = {
        "n": n, "mean_bps": mean(pnl_bps), "net_mean_bps": mean(net), "sd_bps": sd(pnl_bps),
        "t_hac": t, "p_one_sided": p_one_sided(t, sign), "years_pred_sign": ys, "n_years": ny,
        "hit": mean([v * sign > 0 for v in pnl_bps]), "first": str(dates[0]), "last": str(dates[-1]),
    }
    if boot:
        out["ci95_bps"] = bootstrap_ci(pnl_bps)
    return out
