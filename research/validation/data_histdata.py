"""HistData.com free 1-minute ASCII bars. Cached zips.

HistData documents its timestamps as "EST without DST", but the data check in PREREGISTRATION A4 showed the
files follow New York local time WITH daylight saving: the S&P session break starts at 16:16 and US 08:30 data
spikes appear at 08:30 in both January and July. Timestamps are therefore read as America/New_York local time.
"""
from __future__ import annotations

import io
import os
import re
import subprocess
import time
import zipfile
from datetime import date, datetime
from zoneinfo import ZoneInfo

CACHE = os.environ.get("HISTDATA_CACHE", "/tmp/histdata_cache")
NY = ZoneInfo("America/New_York")


def _zip_path(sym, year):
    return os.path.join(CACHE, f"{sym.upper()}_M1_{year}.zip")


def available_years(sym: str, years) -> list[int]:
    """Years already in the cache (the downloader logs years HistData does not serve)."""
    return [y for y in years if os.path.exists(_zip_path(sym, y)) and zipfile.is_zipfile(_zip_path(sym, y))]


def fetch_year(sym: str, year: int, attempts: int = 5) -> str:
    os.makedirs(CACHE, exist_ok=True)
    path = _zip_path(sym, year)
    if os.path.exists(path) and zipfile.is_zipfile(path):
        return path
    page = f"https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/{sym.lower()}/{year}"
    ck = path + ".ck"
    for attempt in range(attempts):
        html = subprocess.run(["curl", "-sS", "-m", "30", "-A", "Mozilla/5.0", "-c", ck, page], capture_output=True, text=True).stdout
        m = re.search(r'id="tk" value="([^"]+)"', html)
        if m:
            subprocess.run(["curl", "-sS", "-m", "180", "-A", "Mozilla/5.0", "-b", ck, "-e", page, "-o", path,
                            "-d", f"tk={m.group(1)}&date={year}&datemonth={year}&platform=ASCII&timeframe=M1&fxpair={sym.upper()}",
                            "https://www.histdata.com/get.php"], capture_output=True)
            if zipfile.is_zipfile(path):
                return path
        time.sleep(5 + 5 * attempt)
    raise RuntimeError(f"histdata failed {sym} {year}")


def minutes(sym: str, year: int, tz=None):
    """Yield (aware datetime, o, h, l, c): New York local time, converted to ``tz`` if given."""
    z = zipfile.ZipFile(fetch_year(sym, year))
    name = next(n for n in z.namelist() if n.endswith(".csv"))
    for line in io.TextIOWrapper(z.open(name), encoding="ascii"):
        ts, o, h, l, c, _ = line.strip().split(";")
        dt = datetime(int(ts[0:4]), int(ts[4:6]), int(ts[6:8]), int(ts[9:11]), int(ts[11:13]), tzinfo=NY)
        if tz is not None:
            dt = dt.astimezone(tz)
        yield dt, float(o), float(h), float(l), float(c)


def table(sym: str, years, keep: set[int]) -> dict:
    """{New York local date: {minute of day: (o, h, l, c)}}, keeping only bars that start at a minute in ``keep``.

    Minutes are counted from local midnight (09:30 -> 570). Bars are labelled by their start minute: the data check
    in A5 found US 08:30 releases in the bar stamped 08:30, not 08:31.
    """
    out, dates = {}, {}
    for y in years:
        z = zipfile.ZipFile(fetch_year(sym, y))
        name = next(n for n in z.namelist() if n.endswith(".csv"))
        for line in io.TextIOWrapper(z.open(name), encoding="ascii"):
            m = int(line[9:11]) * 60 + int(line[11:13])
            if m not in keep:
                continue
            key = line[0:8]
            d = dates.get(key)
            if d is None:
                d = dates[key] = date(int(key[0:4]), int(key[4:6]), int(key[6:8]))
            p = line.split(";")
            out.setdefault(d, {})[m] = (float(p[1]), float(p[2]), float(p[3]), float(p[4]))
    return out


def price(tab: dict, d, m: int, tol: int = 2):
    """Price at local time ``m`` on date ``d``: close of the bar ending at m, else the open of the bar starting at m,
    else the nearest bar edge within ``tol`` minutes (earlier close first on ties)."""
    bars = tab.get(d)
    if not bars:
        return None
    if m - 1 in bars:
        return bars[m - 1][3]
    if m in bars:
        return bars[m][0]
    for k in range(2, tol + 1):
        if m - k in bars:
            return bars[m - k][3]
        if m + k - 1 in bars:
            return bars[m + k - 1][0]
    return None


def bars30(sym: str, years) -> dict:
    """{(NY-local date, half-hour index 0..47): (o, h, l, c)} aggregated from 1-minute bars; cached per year."""
    import pickle
    out = {}
    for y in years:
        path = os.path.join(CACHE, f"{sym.upper()}_B30_{y}.pkl")
        if os.path.exists(path):
            part = pickle.load(open(path, "rb"))
        else:
            part = {}
            z = zipfile.ZipFile(fetch_year(sym, y))
            name = next(n for n in z.namelist() if n.endswith(".csv"))
            dates = {}
            for line in io.TextIOWrapper(z.open(name), encoding="ascii"):
                key = line[0:8]
                d = dates.get(key)
                if d is None:
                    d = dates[key] = date(int(key[0:4]), int(key[4:6]), int(key[6:8]))
                k = (d, (int(line[9:11]) * 60 + int(line[11:13])) // 30)
                p = line.split(";")
                o, h, l, c = float(p[1]), float(p[2]), float(p[3]), float(p[4])
                b = part.get(k)
                if b is None:
                    part[k] = [o, h, l, c]
                else:
                    if h > b[1]:
                        b[1] = h
                    if l < b[2]:
                        b[2] = l
                    b[3] = c
            part = {k: tuple(v) for k, v in part.items()}
            pickle.dump(part, open(path, "wb"))
        out.update(part)
    return out
