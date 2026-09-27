"""Dukascopy free datafeed: BID 1-minute candles, cached per UTC day (round 34, A48). The round-2 module
data_dukascopy.py is kept unchanged for the record; this one adds polite throttling, a per-day cache and a
data_minutes.local-compatible loader.

File format (LZMA): 24-byte records >5if = (seconds from 00:00 UTC, open, close, low, high, volume); prices are
integers scaled by POINT[sym]. A missing day returns 404 (holiday / before history); 429/503 are rate limits, retried
with backoff. The downloader is polite (a pause between requests) and resumable (a day is fetched once).

    python3 data_duka_minutes.py USSC2000IDXUSD 2012 2026     # fill the cache
"""
from __future__ import annotations

import lzma
import os
import struct
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone

import numpy as np

from data_minutes import EPOCH

CACHE = os.environ.get("DUKA_MIN_CACHE", "/tmp/duka_min_cache")
POINT = {"USA30IDXUSD": 1000.0, "USSC2000IDXUSD": 1000.0, "USATECHIDXUSD": 1000.0, "USA500IDXUSD": 1000.0}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
PAUSE = float(os.environ.get("DUKA_PAUSE", "2.0"))


def _path(sym, d):
    return os.path.join(CACHE, sym, f"{d.isoformat()}.bi5")


def fetch_day(sym: str, d: date) -> str | None:
    """Path of the cached day file, '' for a confirmed missing day (404), None if it could not be fetched."""
    os.makedirs(os.path.join(CACHE, sym), exist_ok=True)
    p = _path(sym, d)
    if os.path.exists(p):
        return p
    if os.path.exists(p + ".404"):
        return ""
    url = f"https://datafeed.dukascopy.com/datafeed/{sym}/{d.year}/{d.month - 1:02d}/{d.day:02d}/BID_candles_min_1.bi5"
    wait = 20
    for _ in range(8):
        r = subprocess.run(["curl", "-sS", "-m", "60", "-A", UA, "-H", "Referer: https://www.dukascopy.com/", "-o", p + ".part",
                            "-w", "%{http_code}", url], capture_output=True, text=True)
        code = r.stdout.strip()
        time.sleep(PAUSE)
        if code == "200":
            os.replace(p + ".part", p)
            return p
        if code == "404":
            open(p + ".404", "w").close()
            if os.path.exists(p + ".part"):
                os.remove(p + ".part")
            return ""
        time.sleep(wait)  # 429 / 503 / network: back off
        wait = min(wait * 2, 600)
    return None


def read_day(sym, d):
    p = _path(sym, d)
    if not os.path.exists(p):
        return None
    raw = open(p, "rb").read()
    if not raw:
        return np.zeros((0, 6))
    try:
        b = lzma.decompress(raw)
    except lzma.LZMAError:
        return np.zeros((0, 6))
    n = len(b) // 24
    a = np.array(struct.unpack(">" + "5if" * n, b[:n * 24]), dtype=float).reshape(n, 6)
    a[:, 1:5] /= POINT[sym]
    return a


def local(sym: str, years, tz):
    """(local wall-clock minutes since 1970-01-01 in tz, OHLC matrix) from the cache, like data_minutes.local."""
    ts, xs = [], []
    for y in years:
        d = date(y, 1, 1)
        while d.year == y:
            a = read_day(sym, d)
            if a is not None and len(a):
                base = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
                utc_min = (d.toordinal() - EPOCH) * 1440 + (a[:, 0] // 60).astype(np.int64)
                # convert per minute via the tz offset at that instant (offset changes only at DST boundaries)
                off0 = int(base.astimezone(tz).utcoffset().total_seconds() // 60)
                off1 = int((base + timedelta(hours=23, minutes=59)).astimezone(tz).utcoffset().total_seconds() // 60)
                if off0 == off1:
                    lm = utc_min + off0
                else:
                    lm = np.array([m + int((base + timedelta(minutes=int(m - utc_min[0]))).astimezone(tz).utcoffset().total_seconds() // 60)
                                   for m in utc_min])
                # candles are (open, close, low, high) -> OHLC order used everywhere else
                xs.append(np.stack([a[:, 1], a[:, 4], a[:, 3], a[:, 2]], 1))
                ts.append(lm)
            d += timedelta(days=1)
    if not ts:
        return np.zeros(0, dtype=np.int64), np.zeros((0, 4))
    t, x = np.concatenate(ts), np.concatenate(xs)
    o = np.argsort(t, kind="stable")
    t, x = t[o], x[o]
    keep = np.r_[True, np.diff(t) > 0]
    return t[keep], x[keep]


def fill(sym, y0, y1):
    d = date(y1, 12, 31)
    stop = date(y0, 1, 1)
    today = date(2026, 9, 19)
    n_ok = n_miss = 0
    while d >= stop:
        if d <= today and d.weekday() < 5:
            r = fetch_day(sym, d)
            if r:
                n_ok += 1
            elif r == "":
                n_miss += 1
            if (n_ok + n_miss) % 100 == 0:
                print(sym, d, "ok", n_ok, "missing", n_miss, flush=True)
        d -= timedelta(days=1)
    print(sym, "done", n_ok, n_miss, flush=True)


if __name__ == "__main__" and not (len(sys.argv) > 4 and sys.argv[4] == "hours"):
    fill(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))


# ---------------------------------------------------------------- hourly candles (A48a)

def fetch_month_hours(sym: str, y: int, m: int, pause: float = 25.0) -> str | None:
    """Cache the month's BID hourly candle file. '' = confirmed missing (404), None = could not fetch."""
    os.makedirs(os.path.join(CACHE, sym + "_H1"), exist_ok=True)
    p = os.path.join(CACHE, sym + "_H1", f"{y}-{m:02d}.bi5")
    if os.path.exists(p):
        return p
    if os.path.exists(p + ".404"):
        return ""
    url = f"https://datafeed.dukascopy.com/datafeed/{sym}/{y}/{m - 1:02d}/BID_candles_hour_1.bi5"
    wait = 60
    for _ in range(10):
        r = subprocess.run(["curl", "-sS", "-m", "60", "-A", UA, "-H", "Referer: https://www.dukascopy.com/", "-o", p + ".part",
                            "-w", "%{http_code}", url], capture_output=True, text=True)
        code = r.stdout.strip()
        time.sleep(pause)
        if code == "200":
            os.replace(p + ".part", p)
            return p
        if code == "404":
            open(p + ".404", "w").close()
            return ""
        time.sleep(wait)
        wait = min(wait * 2, 900)
    return None


def hours_local(sym: str, years, tz):
    """(local minutes since 1970-01-01 at each hour-bar start, OHLC) from the cached monthly hour files."""
    ts, xs = [], []
    for y in years:
        for m in range(1, 13):
            p = os.path.join(CACHE, sym + "_H1", f"{y}-{m:02d}.bi5")
            if not os.path.exists(p):
                continue
            raw = open(p, "rb").read()
            if not raw:
                continue
            b = lzma.decompress(raw)
            n = len(b) // 24
            a = np.array(struct.unpack(">" + "5if" * n, b[:n * 24]), dtype=float).reshape(n, 6)
            a[:, 1:5] /= POINT[sym]
            base = datetime(y, m, 1, tzinfo=timezone.utc)
            for rec in a:
                u = base + timedelta(seconds=int(rec[0]))
                lt = u.astimezone(tz)
                ts.append((lt.date().toordinal() - EPOCH) * 1440 + lt.hour * 60 + lt.minute)
                xs.append((rec[1], rec[4], rec[3], rec[2]))  # open, high, low, close
    t = np.array(ts, dtype=np.int64)
    x = np.array(xs, dtype=float)
    o = np.argsort(t, kind="stable")
    return t[o], x[o]


def fill_hours(sym, y0, y1):
    for y in range(y1, y0 - 1, -1):
        for m in range(12, 0, -1):
            if (y, m) > (2026, 9):
                continue
            r = fetch_month_hours(sym, y, m)
            print(sym, y, m, "ok" if r else "missing" if r == "" else "FAILED", flush=True)


if __name__ == "__main__" and len(sys.argv) > 4 and sys.argv[4] == "hours":
    fill_hours(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
