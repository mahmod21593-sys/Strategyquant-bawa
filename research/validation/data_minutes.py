"""Round 11 (PREREGISTRATION.md A24): HistData 1-minute bars as numpy arrays on a local wall clock.

File time = London - 5 h all year (A14 addendum); `data_histdata.clock_shift` converts it per file date, as
`local_table` does. Parsed arrays are cached per symbol-year as .npz in $ROUND11_DIR (default /tmp/round11).
"""
from __future__ import annotations

import os
import zipfile
from datetime import date

import numpy as np

from data_histdata import available_years, clock_shift, fetch_year

CACHE = os.environ.get("ROUND11_DIR", "/tmp/round11")
EPOCH = date(1970, 1, 1).toordinal()
O, H, L, C = 0, 1, 2, 3


def _file_year(sym: str, year: int):
    """(file-clock minutes since 1970-01-01, OHLC matrix) for one symbol-year."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"m1_{sym}_{year}.npz")
    if os.path.exists(path):
        p = np.load(path)
        return p["t"], p["x"]
    z = zipfile.ZipFile(fetch_year(sym, year))
    name = next(n for n in z.namelist() if n.endswith(".csv"))
    a = np.fromstring(z.read(name).replace(b";", b" ").replace(b"\r", b" ").replace(b"\n", b" "), sep=" ").reshape(-1, 7)
    ymd, hms = a[:, 0].astype(np.int64), a[:, 1].astype(np.int64)
    u, inv = np.unique(ymd, return_inverse=True)
    ords = np.array([date(int(v // 10000), int(v // 100 % 100), int(v % 100)).toordinal() - EPOCH for v in u])
    t = ords[inv] * 1440 + (hms // 10000) * 60 + hms // 100 % 100
    x = np.ascontiguousarray(a[:, 2:6])
    tmp = f"{path}.{os.getpid()}.tmp.npz"
    np.savez(tmp, t=t, x=x)
    os.replace(tmp, path)  # atomic: parallel runs share the cache
    return t, x


def local(sym: str, years, tz) -> tuple[np.ndarray, np.ndarray]:
    """(local wall-clock minutes since 1970-01-01 in ``tz``, OHLC matrix), sorted, one row per minute."""
    parts = [_file_year(sym, y) for y in available_years(sym, years)]
    t = np.concatenate([p[0] for p in parts])
    x = np.concatenate([p[1] for p in parts])
    u, inv = np.unique(t // 1440, return_inverse=True)
    t = t + np.array([clock_shift(date.fromordinal(int(v) + EPOCH), tz) for v in u])[inv]
    o = np.argsort(t, kind="stable")
    t, x = t[o], x[o]
    keep = np.r_[True, np.diff(t) > 0]
    return t[keep], x[keep]


def day_of(n: int) -> date:
    return date.fromordinal(int(n) + EPOCH)


def price_at(day, mod, x, m: int, tol: int = 2, prefer_open: bool = False) -> dict:
    """{local day number: price at local minute m}: the close of the bar ending at m, else the open of the bar starting
    at m (reversed with ``prefer_open``), else the nearest bar edge within ``tol`` minutes (data_histdata.price)."""
    assert tol <= m and m + tol < 1440
    cands = [(m, O), (m - 1, C)] if prefer_open else [(m - 1, C), (m, O)]
    for k in range(2, tol + 1):
        cands += [(m - k, C), (m + k - 1, O)]
    out = {}
    for mm, col in reversed(cands):
        sel = np.nonzero(mod == mm)[0]
        out.update(zip(day[sel].tolist(), x[sel, col].tolist()))
    return out


def group(key, x):
    """Rows sorted by ``key``: (unique keys, O, H, L, C, row count, first row index)."""
    st = np.r_[0, np.nonzero(np.diff(key))[0] + 1]
    en = np.r_[st[1:], len(key)] - 1
    return key[st], x[st, O], np.maximum.reduceat(x[:, H], st), np.minimum.reduceat(x[:, L], st), x[en, C], en - st + 1, st
