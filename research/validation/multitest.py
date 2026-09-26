"""Multiple-testing battery for strategy grids (round 9, PREREGISTRATION.md A22). Requires numpy.

- Stationary bootstrap (Politis & Romano 1994), as resampling weights.
- Hansen (2005) SPA test, consistent version, studentized: does any variant beat zero?
- Romano & Wolf (2005) stepdown, studentized max-t: FWER-adjusted p-value per variant.
- CSCV probability of backtest overfitting (Bailey, Borwein, López de Prado & Zhu 2017).
- Walk-forward selection: re-pick the best variants each year on expanding-window data only.

X is always a T x K matrix of per-period net returns (0 when flat), rows in time order.
"""
from __future__ import annotations

import math
from itertools import combinations

import numpy as np


def boot_weights(T: int, mean_block: float, B: int, seed: int = 7) -> np.ndarray:
    """B x T matrix of how often each period appears in each stationary-bootstrap resample."""
    rng = np.random.default_rng(seed)
    p = 1.0 / mean_block
    idx = np.empty((B, T), dtype=np.int64)
    idx[:, 0] = rng.integers(0, T, size=B)
    new = rng.random((B, T)) < p
    jump = rng.integers(0, T, size=(B, T))
    for t in range(1, T):
        idx[:, t] = np.where(new[:, t], jump[:, t], (idx[:, t - 1] + 1) % T)
    W = np.zeros((B, T), dtype=np.float64)
    for b in range(B):
        W[b] = np.bincount(idx[b], minlength=T)
    return W


def _boot(X, mean_block, B, seed):
    T = X.shape[0]
    W = boot_weights(T, mean_block, B, seed)
    mu = X.mean(0)
    mb = W @ X / T
    omega = np.sqrt(T * mb.var(0, ddof=1))
    omega = np.where(omega > 0, omega, np.inf)
    return T, mu, mb, omega


def spa(X: np.ndarray, mean_block: float = 10, B: int = 2000, seed: int = 7) -> dict:
    """Hansen's SPA_c p-value for H0: max_k E[X_k] <= 0."""
    T, mu, mb, omega = _boot(X, mean_block, B, seed)
    stat = max(0.0, float(np.max(math.sqrt(T) * mu / omega)))
    thr = -omega * math.sqrt(2 * math.log(math.log(T)) / T)
    g = np.where(mu >= thr, mu, 0.0)
    tb = np.maximum(0.0, np.max(math.sqrt(T) * (mb - g) / omega, axis=1))
    best = int(np.argmax(mu / omega))
    return {"p_spa": float((tb >= stat).mean()), "stat": stat, "best_index": best, "best_t": float(math.sqrt(T) * mu[best] / omega[best])}


def romano_wolf(X: np.ndarray, mean_block: float = 10, B: int = 2000, seed: int = 7) -> tuple[np.ndarray, np.ndarray]:
    """(FWER-adjusted one-sided p-values, studentized t) per column."""
    T, mu, mb, omega = _boot(X, mean_block, B, seed)
    t = math.sqrt(T) * mu / omega
    tb = math.sqrt(T) * (mb - mu) / omega
    order = np.argsort(-t)
    ts = tb[:, order]
    M = np.maximum.accumulate(ts[:, ::-1], axis=1)[:, ::-1]
    p_sorted = np.maximum.accumulate((M >= t[order][None, :]).mean(0))
    p = np.empty_like(p_sorted)
    p[order] = p_sorted
    return p, t


def sharpe(X: np.ndarray, periods_per_year: float) -> np.ndarray:
    sd = X.std(0, ddof=1)
    return np.where(sd > 0, X.mean(0) / np.where(sd > 0, sd, 1) * math.sqrt(periods_per_year), 0.0)


def pbo(X: np.ndarray, S: int = 16) -> dict:
    """CSCV: share of the C(S, S/2) splits in which the in-sample best ranks at or below the OOS median."""
    T, K = X.shape
    blocks = np.array_split(np.arange(T), S)
    s1 = np.array([X[b].sum(0) for b in blocks])
    s2 = np.array([(X[b] ** 2).sum(0) for b in blocks])
    n = np.array([len(b) for b in blocks], dtype=float)

    def sr(ix):
        m = s1[ix].sum(0) / n[ix].sum()
        v = s2[ix].sum(0) / n[ix].sum() - m * m
        return m / np.sqrt(np.maximum(v, 1e-18))

    lam, is_best, oos_best = [], [], []
    for c in combinations(range(S), S // 2):
        ci = list(c)
        co = [i for i in range(S) if i not in c]
        a, o = sr(ci), sr(co)
        best = int(np.argmax(a))
        w = ((o < o[best]).sum() + 0.5 * ((o == o[best]).sum() - 1) + 1) / (K + 1)
        lam.append(math.log(w / (1 - w)))
        is_best.append(a[best])
        oos_best.append(o[best])
    lam = np.array(lam)
    ib, ob = np.array(is_best), np.array(oos_best)
    slope = float(np.polyfit(ib, ob, 1)[0]) if ib.std() > 0 else float("nan")
    return {"pbo": float((lam <= 0).mean()), "n_splits": len(lam), "median_logit": float(np.median(lam)),
            "oos_sharpe_of_is_best_mean": float(ob.mean()), "share_oos_best_negative": float((ob < 0).mean()), "slope_oos_on_is": slope}


def mann_whitney_z(a: np.ndarray, b: np.ndarray) -> float:
    """z for H1: values in a tend to exceed values in b (normal approximation, average ranks for ties)."""
    x = np.concatenate([a, b])
    order = x.argsort(kind="mergesort")
    ranks = np.empty(len(x))
    i = 0
    xs = x[order]
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    n1, n2 = len(a), len(b)
    u = ranks[:n1].sum() - n1 * (n1 + 1) / 2
    return float((u - n1 * n2 / 2) / math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12))


def walk_forward(X: np.ndarray, years: np.ndarray, first_year: int, top: int, min_periods: int) -> np.ndarray:
    """Each year from first_year: pick the `top` columns by expanding-window Sharpe, weight them by inverse
    expanding-window volatility, hold for the year. Returns the out-of-sample per-period series (0 before first_year)."""
    out = np.zeros(X.shape[0])
    for y in range(first_year, int(years.max()) + 1):
        past = years < y
        cur = years == y
        if past.sum() < min_periods or not cur.any():
            continue
        P = X[past]
        sd = P.std(0, ddof=1)
        sr = np.where(sd > 0, P.mean(0) / np.where(sd > 0, sd, 1), -np.inf)
        pick = np.argsort(-sr)[:top]
        pick = pick[np.isfinite(sr[pick])]
        if len(pick) == 0:
            continue
        w = 1 / sd[pick]
        w = w / w.sum()
        out[cur] = X[cur][:, pick] @ w
    return out
