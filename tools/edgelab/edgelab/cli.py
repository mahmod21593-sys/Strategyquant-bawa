"""Command-line interface: python -m edgelab <study> --help"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from datetime import date
from pathlib import Path
from typing import Optional

from . import studies
from .bars import convert, filter_dates, load_bars, parse_hhmm, parse_tz, to_daily

DAILY_STUDIES = {"ibs", "tom", "compression", "breakout"}


def _fmt(key: str, v) -> str:
    if isinstance(v, bool) or v is None:
        return str(v)
    if isinstance(v, float):
        if v != v:
            return "n/a"
        if key in ("hit", "up", "years_pos", "years_same_sign", "years_negative", "years_frac"):
            return f"{v:.0%}"
        if key in ("r2",):
            return f"{v:.4f}"
        if key in ("beta", "VR", "lag1_autocorr", "mean_R", "next_range_atr", "next_range_vs_today"):
            return f"{v:.3f}"
        return f"{v:,.2f}"
    return str(v)


def print_table(caption: str, rows: list[dict], out) -> None:
    if not rows:
        return
    keys = list(rows[0])
    cells = [[_fmt(k, r.get(k)) for k in keys] for r in rows]
    widths = [max(len(k), *(len(c[i]) for c in cells)) for i, k in enumerate(keys)]
    print(f"  {caption}", file=out)
    print("    " + "  ".join(k.rjust(w) for k, w in zip(keys, widths)), file=out)
    for c in cells:
        print("    " + "  ".join(v.rjust(w) for v, w in zip(c, widths)), file=out)
    print(file=out)


def gate(primary: Optional[dict], cost_bps: Optional[float], min_years: float, cost_mult: float) -> Optional[dict]:
    """Doc 00 Gate 1: predicted sign in >= min_years of years and gross effect > cost_mult x costs."""
    if not primary:
        return None
    effect = primary["effect_bps"] * primary["sign"]
    reasons = []
    if not effect > 0:
        reasons.append("wrong sign")
    if not primary["years_frac"] >= min_years:
        reasons.append(f"sign held in {primary['years_frac']:.0%} of years (< {min_years:.0%})")
    if cost_bps is not None and not effect >= cost_mult * cost_bps:
        reasons.append(f"gross {effect:.2f} bps < {cost_mult:g} x cost {cost_bps:.2f} bps")
    return {"advance": not reasons, "reasons": reasons, "cost_bps": cost_bps}


def run_one(args: argparse.Namespace, path: str) -> tuple[studies.Result, Optional[float]]:
    bars = load_bars(path, args.date_format)
    bars = convert(bars, parse_tz(args.file_tz), parse_tz(args.tz))
    bars = filter_dates(bars, args.date_from, args.date_to)
    if len(bars) < 10:
        raise SystemExit(f"{path}: fewer than 10 bars in range")
    cost_bps = args.cost_bps
    if args.cost_points is not None:
        cost_bps = args.cost_points / statistics.median(b.c for b in bars) * 1e4
    s = args.study
    if s in DAILY_STUDIES:
        bars = to_daily(bars, args.day_start_hour)
    if s == "profile":
        res = studies.profile(bars, args.slot, args.weekday)
    elif s == "varratio":
        if args.daily:
            bars = to_daily(bars, args.day_start_hour)
        res = studies.varratio(bars, tuple(int(x) for x in args.horizons.split(",")))
    elif s == "intraday-momentum":
        res = studies.intraday_momentum(bars, parse_hhmm(args.open), parse_hhmm(args.close),
                                        args.first, args.last, args.from_open)
    elif s == "range-break":
        res = studies.range_break(bars, parse_hhmm(args.range_start), parse_hhmm(args.range_end),
                                  parse_hhmm(args.exit), parse_hhmm(args.entry_end) if args.entry_end else None,
                                  args.buffer, args.stop)
    elif s == "ibs":
        res = studies.ibs(bars, args.sma, args.low, args.nlow)
    elif s == "tom":
        res = studies.tom(bars, args.before, args.after)
    elif s == "compression":
        res = studies.compression(bars, args.n, args.atr)
    elif s == "breakout":
        res = studies.breakout(bars, args.n, tuple(int(x) for x in args.horizons.split(",")))
    else:  # pragma: no cover - argparse restricts choices
        raise SystemExit(f"unknown study {s}")
    return res, cost_bps


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="edgelab", description="Phase 1 raw-edge studies on OHLC bar exports.")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--bars", nargs="+", required=True, help="one CSV per market (OHLC bars)")
    common.add_argument("--file-tz", help="time zone of the CSV timestamps: UTC, UTC+2, NYCLOSE, or an IANA name")
    common.add_argument("--tz", help="time zone to analyse in (session times are in this zone), e.g. America/New_York")
    common.add_argument("--from", dest="date_from", type=date.fromisoformat)
    common.add_argument("--to", dest="date_to", type=date.fromisoformat)
    common.add_argument("--date-format", help="strptime format if auto-detection fails")
    common.add_argument("--day-start-hour", type=float, default=0.0, help="hour when a trading day starts (daily studies)")
    common.add_argument("--cost-bps", type=float, help="round-trip cost per trade in bps of price")
    common.add_argument("--cost-points", type=float, help="round-trip cost per trade in price points (converted to bps)")
    common.add_argument("--min-years", type=float, default=0.6, help="Gate 1: share of years with predicted sign")
    common.add_argument("--cost-mult", type=float, default=2.0, help="Gate 1: gross effect must exceed this x cost")
    common.add_argument("--min-markets", type=int, default=2, help="Gate 1: markets that must pass")
    common.add_argument("--json", help="write results to this JSON file")
    sub = p.add_subparsers(dest="study", required=True)

    s = sub.add_parser("profile", parents=[common], help="time-of-day return and volatility profile")
    s.add_argument("--slot", type=int, default=60, help="slot size in minutes")
    s.add_argument("--weekday", action="store_true", help="split slots by weekday")

    s = sub.add_parser("varratio", parents=[common], help="variance ratios: trending vs mean-reverting by horizon")
    s.add_argument("--horizons", default="2,4,8,16,32")
    s.add_argument("--daily", action="store_true", help="aggregate to daily bars first")

    s = sub.add_parser("intraday-momentum", parents=[common], help="last-period vs earlier returns (IM-01/IM-05)")
    s.add_argument("--open", required=True, help="session open HH:MM in --tz")
    s.add_argument("--close", required=True, help="session close HH:MM in --tz")
    s.add_argument("--first", type=int, default=30, help="first-period minutes")
    s.add_argument("--last", type=int, default=30, help="last-period minutes")
    s.add_argument("--from-open", action="store_true", help="measure from the session open instead of the prior close")

    s = sub.add_parser("range-break", parents=[common], help="opening-range / session-range breakout (IM-02, VB-02)")
    s.add_argument("--range-start", required=True)
    s.add_argument("--range-end", required=True)
    s.add_argument("--exit", required=True, help="exit time HH:MM")
    s.add_argument("--entry-end", help="no new entries at or after HH:MM (default: exit time)")
    s.add_argument("--buffer", type=float, default=0.0, help="entry buffer as a fraction of range width")
    s.add_argument("--stop", choices=("opposite", "none"), default="opposite")

    s = sub.add_parser("ibs", parents=[common], help="IBS and N-day-low mean reversion (MR-01/MR-02)")
    s.add_argument("--sma", type=int, default=200)
    s.add_argument("--low", type=float, default=0.2)
    s.add_argument("--nlow", type=int, default=5)

    s = sub.add_parser("tom", parents=[common], help="turn-of-month effect (CF-01)")
    s.add_argument("--before", type=int, default=1)
    s.add_argument("--after", type=int, default=3)

    s = sub.add_parser("compression", parents=[common], help="NR-n compression and breakout (VB-01)")
    s.add_argument("--n", type=int, default=7)
    s.add_argument("--atr", type=int, default=20)

    s = sub.add_parser("breakout", parents=[common], help="N-day closing breakout forward returns (TF-01)")
    s.add_argument("--n", type=int, default=55)
    s.add_argument("--horizons", default="1,5,10,20")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    out = sys.stdout
    summary, dump = [], []
    for path in args.bars:
        res, cost_bps = run_one(args, path)
        print(f"=== {Path(path).name}: {res.title} ===", file=out)
        for caption, rows in res.tables:
            print_table(caption, rows, out)
        for note in res.notes:
            print(f"  Note: {note}", file=out)
        g = gate(res.primary, cost_bps, args.min_years, args.cost_mult)
        if res.primary:
            pr = res.primary
            verdict = "ADVANCE" if g["advance"] else "PARK (" + "; ".join(g["reasons"]) + ")"
            print(f"  Primary: {pr['label']}: {pr['effect_bps']:.2f} bps, t {pr['t']:.2f}, n {pr['n']}, "
                  f"predicted sign in {pr['years_frac']:.0%} of {pr['n_years']} years", file=out)
            print(f"  Gate 1: {verdict}" + ("" if cost_bps is not None else "  [no cost given]"), file=out)
            summary.append((Path(path).name, pr, g))
        print(file=out)
        dump.append({"file": path, "study": res.study, "title": res.title, "tables": res.tables,
                     "primary": res.primary, "gate": g, "notes": res.notes})
    if len(summary) > 1:
        print("=== Summary ===", file=out)
        rows = [{"market": name, "effect_bps": pr["effect_bps"], "t": pr["t"], "years_frac": pr["years_frac"],
                 "gate": "ADVANCE" if g["advance"] else "PARK"} for name, pr, g in summary]
        print_table("Primary effect per market", rows, out)
        passed = sum(g["advance"] for _, _, g in summary)
        ok = passed >= args.min_markets
        print(f"  Hypothesis Gate 1: {'ADVANCE' if ok else 'PARK'} ({passed} of {len(summary)} markets pass; "
              f"need {args.min_markets})", file=out)
    if args.json:
        Path(args.json).write_text(json.dumps(dump, indent=2, default=lambda o: None if o != o else str(o)))
        print(f"Wrote {args.json}", file=out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
