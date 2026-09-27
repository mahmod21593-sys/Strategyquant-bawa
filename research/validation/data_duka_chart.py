"""Dukascopy one-minute BID candles from the chart service (freeserv.dukascopy.com, JSON; A48b), cached and resumable.

Each request returns up to 30,000 candles [utc ms, open, high, low, close, volume] from a start time forward, including
filler candles for closed hours (volume 0, open = high = low = close), which `local` drops.

    python3 data_duka_chart.py USA30.IDX/USD 2012-04-01 2026-09-19
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import date, datetime, timezone

import numpy as np

from data_minutes import EPOCH

CACHE = os.environ.get("DUKA_CHART_CACHE", "/tmp/duka_chart")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
URL = ("https://freeserv.dukascopy.com/2.0/?path=chart/json3&instrument={ins}&offer_side=B&interval=1MIN&splits=true"
       "&stocks=true&limit=30000&time_direction=N&timestamp={ts}&jsonp=_cb")


def _dir(ins):
    d = os.path.join(CACHE, ins.replace("/", "_").replace(".", ""))
    os.makedirs(d, exist_ok=True)
    return d


def fetch_page(ins: str, ts: int) -> np.ndarray:
    p = os.path.join(_dir(ins), f"{ts}.npy")
    if os.path.exists(p):
        return np.load(p)
    wait = 5
    for attempt in range(12):
        rows = None
        r = subprocess.run(["curl", "-sS", "-m", "60", "-A", UA, "-H", "Referer: https://freeserv.dukascopy.com/2.0/?path=chart/index",
                            "-w", "\n%{http_code}", URL.format(ins=ins, ts=ts)], capture_output=True, text=True)
        body, _, code = r.stdout.rpartition("\n")
        if code == "200" and "(" in body:
            try:
                rows = json.loads(body[body.find("(") + 1:body.rfind(")")])
            except ValueError:
                rows = None
            if not (isinstance(rows, list) and all(isinstance(r, list) and len(r) == 6 for r in rows)):
                rows, code = None, "bad json"
        if rows is not None and code == "200":
            a = np.array(rows, dtype=float).reshape(-1, 6)
            if len(a):
                np.save(p, a)
                return a
            if attempt >= 2:
                return a  # empty after retries: a gap (not cached, so a rerun tries again)
        time.sleep(wait)
        wait = min(wait * 2, 300)
    raise RuntimeError(f"chart fetch failed: {ins} {ts} ({code})")


def fill(ins: str, start: date, end: date, pause: float = 0.5):
    ts = int(datetime(start.year, start.month, start.day, tzinfo=timezone.utc).timestamp() * 1000)
    stop = int(datetime(end.year, end.month, end.day, tzinfo=timezone.utc).timestamp() * 1000)
    n = 0
    while ts < stop:
        cached = os.path.exists(os.path.join(_dir(ins), f"{ts}.npy"))
        a = fetch_page(ins, ts)
        if not len(a):
            print(ins, "empty page, skipping a day:", datetime.fromtimestamp(ts / 1000, timezone.utc), flush=True)
            ts += 86_400_000
            continue
        ts = int(a[-1, 0]) + 60_000
        n += 1
        if n % 100 == 0:
            print(ins, n, datetime.fromtimestamp(ts / 1000, timezone.utc).date(), flush=True)
        if not cached:
            time.sleep(pause)
    print(ins, "done", n, "pages", flush=True)


def load(ins: str) -> np.ndarray:
    d = _dir(ins)
    parts = [np.load(os.path.join(d, f)) for f in sorted(os.listdir(d), key=lambda s: int(s.split(".")[0])) if f.endswith(".npy")]
    a = np.concatenate([p for p in parts if len(p)]) if parts else np.zeros((0, 6))
    _, first = np.unique(a[:, 0], return_index=True)
    return a[np.sort(first)]


def local(ins: str, tz, end: date | None = None):
    """(local minutes since 1970-01-01, OHLC) with filler candles dropped; same conventions as data_minutes.local."""
    a = load(ins)
    filler = (a[:, 5] == 0) & (a[:, 1] == a[:, 2]) & (a[:, 2] == a[:, 3]) & (a[:, 3] == a[:, 4])
    a = a[~filler]
    um = (a[:, 0] // 60_000).astype(np.int64)
    ud = um // 1440
    u, inv = np.unique(ud, return_inverse=True)
    off = np.array([int(datetime.fromordinal(int(v) + EPOCH).replace(hour=12, tzinfo=timezone.utc).astimezone(tz).utcoffset().total_seconds() // 60)
                    for v in u], dtype=np.int64)
    t = um + off[inv]
    x = a[:, 1:5].copy()
    if end is not None:
        keep = t < (end.toordinal() - EPOCH + 1) * 1440
        t, x = t[keep], x[keep]
    o = np.argsort(t, kind="stable")
    return t[o], x[o]


if __name__ == "__main__":
    fill(sys.argv[1], date.fromisoformat(sys.argv[2]), date.fromisoformat(sys.argv[3]))
