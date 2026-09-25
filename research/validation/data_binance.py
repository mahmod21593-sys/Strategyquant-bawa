"""Binance spot klines from data.binance.vision (monthly zips), cached. Times are UTC; bars labelled by open time."""
from __future__ import annotations

import io
import os
import subprocess
import zipfile
from datetime import date, datetime, timezone

CACHE = os.environ.get("BINANCE_CACHE", "/tmp/binance_cache")


def _month_zip(sym, interval, y, m):
    os.makedirs(CACHE, exist_ok=True)
    name = f"{sym}-{interval}-{y}-{m:02d}.zip"
    path = os.path.join(CACHE, name)
    if not (os.path.exists(path) and zipfile.is_zipfile(path)):
        url = f"https://data.binance.vision/data/spot/monthly/klines/{sym}/{interval}/{name}"
        subprocess.run(["curl", "-sS", "-m", "120", "-o", path, url], capture_output=True)
        if not zipfile.is_zipfile(path):
            if os.path.exists(path):
                os.remove(path)
            return None
    return path


def klines(sym: str, interval: str, start: date, end: date) -> dict:
    """{UTC datetime of bar open: (o, h, l, c)} for months start..end inclusive."""
    out = {}
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        p = _month_zip(sym, interval, y, m)
        if p:
            z = zipfile.ZipFile(p)
            for line in io.TextIOWrapper(z.open(z.namelist()[0]), encoding="ascii"):
                f = line.split(",")
                if not f[0].isdigit():
                    continue
                t = int(f[0])
                if t > 10 ** 14:  # microseconds (Binance switched in 2025)
                    t //= 1000
                out[datetime.fromtimestamp(t / 1000, tz=timezone.utc)] = (float(f[1]), float(f[2]), float(f[3]), float(f[4]))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out
