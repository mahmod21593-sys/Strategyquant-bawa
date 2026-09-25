"""Download and decode Dukascopy candle archives (BID side) with caching and retries.

URL layout (months are 0-based):
  minute : /datafeed/{SYM}/{YYYY}/{MM}/{DD}/BID_candles_min_1.bi5   (offsets from day start, UTC)
  hour   : /datafeed/{SYM}/{YYYY}/{MM}/BID_candles_hour_1.bi5        (offsets from month start, UTC)
  day    : /datafeed/{SYM}/{YYYY}/BID_candles_day_1.bi5              (offsets from year start, UTC)
Record: big-endian (int32 seconds, open, close, low, high, float32 volume), prices in integer points.
Only ratios are used downstream, so the point divisor does not matter.
"""
from __future__ import annotations

import lzma
import os
import struct
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone

BASE = "https://datafeed.dukascopy.com/datafeed"
CACHE = os.environ.get("DUKA_CACHE", "/tmp/duka_cache")


def _fetch(url: str, path: str) -> bytes:
    if os.path.exists(path):
        return open(path, "rb").read()
    delay = 0.5
    for attempt in range(25):
        r = subprocess.run(["curl", "-sS", "-m", "8", "--connect-timeout", "4", "-A", "Mozilla/5.0", "-w", "%{http_code}", "-o", path + ".part", url],
                           capture_output=True, text=True)
        code = r.stdout.strip()[-3:]
        if code == "200":
            data = open(path + ".part", "rb").read()
            if not data or data[:1] == b"]":  # empty (no data) or LZMA-alone header
                os.replace(path + ".part", path)
                return data
        if code == "404":
            open(path, "wb").close()
            return b""
        time.sleep(delay)
        delay = min(delay * 1.3, 4)
    raise RuntimeError(f"failed after retries: {url} (last code {code})")


def _decode(blob: bytes, t0: datetime):
    if not blob:
        return []
    raw = lzma.decompress(blob)
    out = []
    for i in range(len(raw) // 24):
        s, o, c, lo, hi, v = struct.unpack(">5if", raw[i * 24:(i + 1) * 24])
        if v == 0 and o == c == lo == hi:
            continue  # filler bar with no ticks
        out.append((t0 + timedelta(seconds=s), o, hi, lo, c, v))
    return out


def minute_day(sym: str, d: date):
    path = os.path.join(CACHE, sym, "min", f"{d:%Y%m%d}.bi5")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    url = f"{BASE}/{sym}/{d.year}/{d.month - 1:02d}/{d.day:02d}/BID_candles_min_1.bi5"
    return _decode(_fetch(url, path), datetime(d.year, d.month, d.day, tzinfo=timezone.utc))


def hour_month(sym: str, year: int, month: int):
    path = os.path.join(CACHE, sym, "hour", f"{year}{month:02d}.bi5")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    url = f"{BASE}/{sym}/{year}/{month - 1:02d}/BID_candles_hour_1.bi5"
    return _decode(_fetch(url, path), datetime(year, month, 1, tzinfo=timezone.utc))


def minutes(sym: str, start: date, end: date, workers: int = 6):
    days = []
    d = start
    while d <= end:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    with ThreadPoolExecutor(workers) as ex:
        chunks = list(ex.map(lambda x: minute_day(sym, x), days))
    return [bar for ch in chunks for bar in ch]


def hours(sym: str, start_year: int, end_year: int, end_month: int = 12, workers: int = 6):
    months = [(y, m) for y in range(start_year, end_year + 1) for m in range(1, 13)
              if not (y == end_year and m > end_month)]
    with ThreadPoolExecutor(workers) as ex:
        chunks = list(ex.map(lambda ym: hour_month(sym, *ym), months))
    return [bar for ch in chunks for bar in ch]
