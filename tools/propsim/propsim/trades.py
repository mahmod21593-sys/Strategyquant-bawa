"""Load trade lists (SQX, QuantAnalyzer, MT4/MT5 exports) and turn them into daily records."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Optional

from .engine import Day

DATE_FORMATS = (
    "%Y.%m.%d %H:%M:%S",
    "%Y.%m.%d %H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%dT%H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d %H:%M",
    "%d.%m.%Y %H:%M:%S",
    "%d.%m.%Y %H:%M",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%Y.%m.%d",
    "%Y-%m-%d",
)

COLUMN_CANDIDATES = {
    "open": ("opentime", "opendate", "entrytime", "entrydate", "timeopen", "dateopen"),
    "close": ("closetime", "closedate", "exittime", "exitdate", "timeclose", "dateclose"),
    "pnl": ("profitloss", "pl", "pnl", "profit", "netprofit", "netpl", "plmoney", "result"),
    "mae": ("mae", "maxopenloss", "maemoney"),
    "mfe": ("mfe", "maxopenprofit", "mfemoney"),
    "symbol": ("symbol", "instrument", "market"),
}


@dataclass(frozen=True)
class Trade:
    open_time: datetime
    close_time: datetime
    pnl: float  # money at the backtest's reference sizing
    mae: Optional[float] = None  # adverse excursion, money, positive magnitude
    mfe: Optional[float] = None  # favourable excursion, money, positive magnitude
    symbol: str = ""
    source: str = ""


def _norm(name: str) -> str:
    name = re.sub(r"\(.*?\)", "", name.lower())
    return re.sub(r"[^a-z0-9]", "", name)


def parse_number(text: str) -> float:
    s = re.sub(r"[^0-9,.\-]", "", text.strip().replace("−", "-"))
    if not s or s in "-.,":
        raise ValueError(f"not a number: {text!r}")
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        head, _, tail = s.rpartition(",")
        s = s.replace(",", "") if (s.count(",") > 1 or len(tail) == 3) else f"{head}.{tail}"
    return float(s)


def parse_datetime(text: str, fmt: Optional[str] = None) -> datetime:
    text = text.strip()
    formats = (fmt,) if fmt else DATE_FORMATS
    for f in formats:
        try:
            return datetime.strptime(text, f)
        except ValueError:
            continue
    raise ValueError(f"unrecognised date/time {text!r}; pass --date-format")


def _find_column(headers: list[str], role: str, override: Optional[str]) -> Optional[int]:
    normed = [_norm(h) for h in headers]
    if override:
        key = _norm(override)
        if key not in normed:
            raise ValueError(f"column {override!r} not found; available: {headers}")
        return normed.index(key)
    for cand in COLUMN_CANDIDATES[role]:
        if cand in normed:
            return normed.index(cand)
    return None


def load_trades(
    path: str | Path,
    columns: Optional[dict[str, Optional[str]]] = None,
    date_format: Optional[str] = None,
) -> list[Trade]:
    """Read a trade-list CSV. Delimiter and common column names are detected automatically."""
    columns = columns or {}
    raw = Path(path).read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    rows = [r for r in csv.reader(io.StringIO(text), dialect) if any(c.strip() for c in r)]
    if not rows:
        raise ValueError(f"{path}: empty file")
    headers = rows[0]
    idx = {role: _find_column(headers, role, columns.get(role)) for role in COLUMN_CANDIDATES}
    for role in ("open", "close", "pnl"):
        if idx[role] is None:
            raise ValueError(
                f"{path}: cannot find the {role!r} column in {headers}; pass --col-{role}"
            )
    trades = []
    for n, row in enumerate(rows[1:], start=2):
        try:
            get = lambda role: row[idx[role]] if idx[role] is not None and idx[role] < len(row) else ""
            mae_txt, mfe_txt = get("mae"), get("mfe")
            trades.append(
                Trade(
                    open_time=parse_datetime(get("open"), date_format),
                    close_time=parse_datetime(get("close"), date_format),
                    pnl=parse_number(get("pnl")),
                    mae=abs(parse_number(mae_txt)) if mae_txt.strip() else None,
                    mfe=abs(parse_number(mfe_txt)) if mfe_txt.strip() else None,
                    symbol=get("symbol").strip(),
                    source=Path(path).stem,
                )
            )
        except ValueError as exc:
            raise ValueError(f"{path}, line {n}: {exc}") from None
    return trades


def trading_date(ts: datetime, day_start_hour: float = 0.0) -> date:
    """Calendar date of the prop firm's trading day containing ``ts``."""
    return (ts - timedelta(hours=day_start_hour)).date()


def build_days(
    trades: Iterable[Trade],
    ref_balance: float,
    day_start_hour: float = 0.0,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    weights: Optional[dict[str, float]] = None,
) -> list[Day]:
    """Aggregate trades into one ``Day`` per weekday (plus any weekend day with activity).

    P&L is attributed to the day the trade closes. Within a day the floating low is
    estimated conservatively: just before each trade closes, every trade that closes
    that day and is already open is assumed to sit at its MAE at the same moment.
    Without MAE, losing trades are assumed to have gone no worse than their final loss.
    Floating losses of positions held overnight are attributed to the close day only.
    """
    weights = weights or {}
    by_close: dict[date, list[Trade]] = {}
    active: set[date] = set()
    for t in trades:
        cd = trading_date(t.close_time, day_start_hour)
        by_close.setdefault(cd, []).append(t)
        active.add(cd)
        active.add(trading_date(t.open_time, day_start_hour))
    if not active:
        return []

    first, last = min(active), max(active)
    if date_from:
        first = max(first, date_from)
    if date_to:
        last = min(last, date_to)

    days = []
    d = first
    while d <= last:
        todays = by_close.get(d, [])
        if todays or d in active or d.weekday() < 5:
            days.append(_make_day(d, todays, d in active, ref_balance, weights))
        d += timedelta(days=1)
    return days


def _make_day(d: date, trades: list[Trade], traded: bool, ref: float, weights: dict[str, float]) -> Day:
    ts = sorted(trades, key=lambda t: t.close_time)
    w = [weights.get(t.source, 1.0) / ref for t in ts]
    pnl = [t.pnl * wi for t, wi in zip(ts, w)]
    mae = [max(t.mae if t.mae is not None else 0.0, -t.pnl, 0.0) * wi for t, wi in zip(ts, w)]
    mfe = [max(t.mfe if t.mfe is not None else 0.0, t.pnl, 0.0) * wi for t, wi in zip(ts, w)]
    running = low = high = 0.0
    for i, t in enumerate(ts):
        open_mae = sum(mae[j] for j in range(i, len(ts)) if ts[j].open_time <= t.close_time)
        low = min(low, running - open_mae)
        high = max(high, running + mfe[i])
        running += pnl[i]
        low = min(low, running)
        high = max(high, running)
    return Day(date=d, pnl=running, low=low, high=high, traded=traded or bool(ts), n_trades=len(ts))


def daily_series(days: list[Day]) -> list[float]:
    return [d.pnl for d in days]
