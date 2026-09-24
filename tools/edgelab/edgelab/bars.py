"""Load OHLC bars (MT4/MT5, Dukascopy, SQX Data Manager or generic CSV exports) and reshape them."""

from __future__ import annotations

import csv
import io
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone, tzinfo
from pathlib import Path
from typing import Optional

DATETIME_FORMATS = (
    "%Y.%m.%d %H:%M:%S",
    "%Y.%m.%d %H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%dT%H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d %H:%M",
    "%Y%m%d %H:%M:%S",
    "%Y%m%d %H:%M",
    "%d.%m.%Y %H:%M:%S.%f",
    "%d.%m.%Y %H:%M:%S",
    "%d.%m.%Y %H:%M",
    "%Y.%m.%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S.%f",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%Y.%m.%d",
    "%Y-%m-%d",
    "%Y%m%d",
    "%d.%m.%Y",
    "%m/%d/%Y",
)


@dataclass(frozen=True)
class Bar:
    ts: datetime  # bar OPEN time, naive, in the analysis time zone
    o: float
    h: float
    l: float
    c: float


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _number(text: str) -> float:
    s = text.strip()
    if "," in s and "." not in s:
        s = s.replace(",", ".")
    return float(s.replace(",", ""))


def _normalise_time(text: str) -> str:
    t = text.strip()
    if re.fullmatch(r"\d{6}", t):
        return f"{t[:2]}:{t[2:4]}:{t[4:]}"
    if re.fullmatch(r"\d{4}", t):
        return f"{t[:2]}:{t[2:]}"
    return t


class _DateParser:
    def __init__(self, fmt: Optional[str]) -> None:
        self.formats = [fmt] if fmt else list(DATETIME_FORMATS)
        self.last: Optional[str] = None

    def __call__(self, text: str) -> datetime:
        text = text.strip()
        if self.last:
            try:
                return datetime.strptime(text, self.last)
            except ValueError:
                pass
        for f in self.formats:
            try:
                value = datetime.strptime(text, f)
            except ValueError:
                continue
            self.last = f
            return value
        raise ValueError(f"unrecognised date/time {text!r}; pass --date-format")


def load_bars(path: str | Path, date_format: Optional[str] = None) -> list[Bar]:
    """Read an OHLC CSV. Header or headerless; combined or separate date and time columns."""
    raw = Path(path).read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    rows = [r for r in csv.reader(io.StringIO(text), dialect) if any(c.strip() for c in r)]
    if not rows:
        raise ValueError(f"{path}: empty file")

    parse = _DateParser(date_format)
    header = [_norm(c) for c in rows[0]]
    has_header = any(h in ("open", "high", "low", "close", "o", "h", "l", "c") for h in header)
    if has_header:
        body = rows[1:]

        def col(*names: str) -> Optional[int]:
            for n in names:
                if n in header:
                    return header.index(n)
            return None

        i_date = col("date", "day")
        i_time = col("time", "hour")
        i_dt = col("datetime", "timestamp", "gmttime", "localtime", "opentime", "barstart")
        i_o, i_h, i_l, i_c = col("open", "o"), col("high", "h"), col("low", "l"), col("close", "c")
        if None in (i_o, i_h, i_l, i_c):
            raise ValueError(f"{path}: need open/high/low/close columns, got {rows[0]}")
        if i_dt is None and i_date is None and i_time is not None:
            i_dt, i_time = i_time, None
        if i_dt is None and i_date is None:
            raise ValueError(f"{path}: cannot find a date/time column in {rows[0]}")
    else:
        body = rows
        first = rows[0]
        i_date = 0
        i_time = 1 if re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?|\d{4}|\d{6}", first[1].strip()) else None
        start = 2 if i_time is not None else 1
        i_dt = None
        i_o, i_h, i_l, i_c = start, start + 1, start + 2, start + 3

    bars = []
    for n, r in enumerate(body, start=2 if has_header else 1):
        try:
            if i_dt is not None:
                stamp = r[i_dt]
            elif i_time is not None:
                stamp = f"{r[i_date].strip()} {_normalise_time(r[i_time])}"
            else:
                stamp = r[i_date]
            bars.append(Bar(parse(stamp), _number(r[i_o]), _number(r[i_h]), _number(r[i_l]), _number(r[i_c])))
        except (ValueError, IndexError) as exc:
            raise ValueError(f"{path}, line {n}: {exc}") from None
    bars.sort(key=lambda b: b.ts)
    return bars


def parse_tz(spec: Optional[str]) -> Optional[tzinfo]:
    """UTC, UTC+2, UTC-5, an IANA name (Europe/Berlin), or NYCLOSE (New York + 7h, the usual MT 'GMT+2/+3' server time)."""
    if spec is None:
        return None
    s = spec.strip()
    if s.upper() == "NYCLOSE":
        return _NYClose()
    m = re.fullmatch(r"(?i)(?:utc|gmt)([+-]\d{1,2}(?::?\d{2})?)?", s)
    if m:
        if not m.group(1):
            return timezone.utc
        sign = -1 if m.group(1)[0] == "-" else 1
        digits = m.group(1)[1:].replace(":", "")
        hours = int(digits[:-2] or digits) if len(digits) > 2 else int(digits)
        minutes = int(digits[-2:]) if len(digits) > 2 else 0
        return timezone(sign * timedelta(hours=hours, minutes=minutes))
    from zoneinfo import ZoneInfo  # requires the tzdata package on Windows

    return ZoneInfo(s)


class _NYClose(tzinfo):
    """Server time = New York time + 7 hours, so 17:00 New York is midnight (DST follows New York)."""

    def __init__(self) -> None:
        from zoneinfo import ZoneInfo

        self._ny = ZoneInfo("America/New_York")

    def utcoffset(self, dt: Optional[datetime]) -> timedelta:
        if dt is None:
            return timedelta(hours=2)
        ny = (dt.replace(tzinfo=None) - timedelta(hours=7)).replace(tzinfo=self._ny)
        return ny.utcoffset() + timedelta(hours=7)

    def dst(self, dt: Optional[datetime]) -> timedelta:
        return timedelta(0)

    def fromutc(self, dt: datetime) -> datetime:
        ny = dt.replace(tzinfo=timezone.utc).astimezone(self._ny)
        return (ny.replace(tzinfo=None) + timedelta(hours=7)).replace(tzinfo=self)

    def tzname(self, dt: Optional[datetime]) -> str:
        return "NYCLOSE"


def convert(bars: list[Bar], src: Optional[tzinfo], dst: Optional[tzinfo]) -> list[Bar]:
    """Re-stamp bars from ``src`` to ``dst`` time zone (naive in, naive out)."""
    if src is None or dst is None:
        return bars
    out = []
    for b in bars:
        local = b.ts.replace(tzinfo=src).astimezone(dst).replace(tzinfo=None)
        out.append(Bar(local, b.o, b.h, b.l, b.c))
    return out


def timeframe(bars: list[Bar]) -> timedelta:
    """Most common spacing between consecutive bars."""
    diffs = Counter(b.ts - a.ts for a, b in zip(bars, bars[1:]) if b.ts > a.ts)
    if not diffs:
        raise ValueError("need at least two bars")
    return diffs.most_common(1)[0][0]


def is_daily(bars: list[Bar]) -> bool:
    return timeframe(bars) >= timedelta(hours=20)


def filter_dates(bars: list[Bar], start: Optional[date], end: Optional[date]) -> list[Bar]:
    return [b for b in bars if (start is None or b.ts.date() >= start) and (end is None or b.ts.date() <= end)]


def to_daily(bars: list[Bar], day_start_hour: float = 0.0) -> list[Bar]:
    """Aggregate intraday bars into one bar per trading day (day starts at ``day_start_hour``)."""
    if is_daily(bars):
        return [Bar(datetime.combine(b.ts.date(), time()), b.o, b.h, b.l, b.c) for b in bars]
    shift = timedelta(hours=day_start_hour)
    days: dict[date, list[Bar]] = {}
    for b in bars:
        days.setdefault((b.ts - shift).date(), []).append(b)
    out = []
    for d in sorted(days):
        grp = days[d]
        out.append(Bar(datetime.combine(d, time()), grp[0].o, max(x.h for x in grp), min(x.l for x in grp), grp[-1].c))
    return out


def by_date(bars: list[Bar]) -> dict[date, list[Bar]]:
    out: dict[date, list[Bar]] = {}
    for b in bars:
        out.setdefault(b.ts.date(), []).append(b)
    return out


def parse_hhmm(text: str) -> time:
    h, _, m = text.partition(":")
    return time(int(h), int(m or 0))
