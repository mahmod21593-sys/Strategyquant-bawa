"""Closed-form first-passage results for arithmetic Brownian motion.

With daily mean ``mu`` and daily standard deviation ``sigma`` (as fractions of the
initial balance), the probability of gaining ``target`` before losing ``loss`` is

    P = (exp(k*loss) - 1) / (exp(k*loss) - exp(-k*target)),   k = 2*mu / sigma**2

which tends to loss / (target + loss) when mu = 0. This ignores daily loss limits,
trailing drawdowns, time limits and fat tails. Use it as a sanity check against the
simulator, not as a substitute.
"""

from __future__ import annotations

import math


def pass_probability(mu: float, sigma: float, target: float, loss: float) -> float:
    if sigma <= 0:
        return 1.0 if mu > 0 else 0.0
    k = 2.0 * mu / sigma**2
    if abs(k) * (target + loss) < 1e-9:
        return loss / (target + loss)
    # Numerically stable rearrangements of the formula above.
    j = abs(k)
    base = math.expm1(-j * loss) / math.expm1(-j * (target + loss))
    return base if k > 0 else base * math.exp(-j * target)


def expected_days(mu: float, sigma: float, target: float, loss: float) -> float:
    """Expected days until either barrier is hit."""
    if sigma <= 0:
        return target / mu if mu > 0 else math.inf
    if abs(mu) < 1e-15:
        return target * loss / sigma**2
    p = pass_probability(mu, sigma, target, loss)
    return (target * p - loss * (1.0 - p)) / mu


def multi_phase_probability(mu: float, sigma: float, targets: list[float], loss: float) -> float:
    prob = 1.0
    for t in targets:
        prob *= pass_probability(mu, sigma, t, loss)
    return prob
