"""Command-line interface: python -m propsim --help"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from collections import Counter
from dataclasses import asdict, replace
from datetime import date
from pathlib import Path
from typing import Optional

from .analytic import multi_phase_probability
from .engine import Outcome, run_challenge
from .rules import Rules, describe, load_rules
from .sampling import historical_paths, stationary_bootstrap
from .trades import Trade, build_days, load_trades

PRESET_DIR = Path(__file__).resolve().parent.parent / "presets"


def resolve_rules(arg: str) -> Rules:
    path = Path(arg)
    if not path.exists():
        path = PRESET_DIR / (arg if arg.endswith(".json") else f"{arg}.json")
    if not path.exists():
        names = sorted(p.stem for p in PRESET_DIR.glob("*.json"))
        raise SystemExit(f"rules file {arg!r} not found. Presets: {', '.join(names)}")
    return load_rules(path)


def parse_scales(scale: Optional[float], scan: Optional[str]) -> list[float]:
    if scan:
        start, stop, step = (float(x) for x in scan.split(":"))
        out, x = [], start
        while x <= stop + 1e-9:
            out.append(round(x, 6))
            x += step
        return out
    return [scale if scale is not None else 1.0]


def percentile(values: list[float], q: float) -> float:
    if not values:
        return math.nan
    s = sorted(values)
    pos = (len(s) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def summarize(outcomes: list[Outcome], rules: Rules) -> dict:
    decided = [o for o in outcomes if o.decided]
    n = len(decided)
    passed = [o for o in decided if o.passed_all]
    days = [float(o.days_to_pass) for o in passed]
    complete = [o for o in outcomes if o.complete]
    funded = [o for o in complete if o.passed_all]
    fails = Counter(o.fail_reason for o in decided if not o.passed_all)
    res = {
        "paths": len(outcomes),
        "decided": n,
        "incomplete": len(outcomes) - n,
        "p_pass_all": len(passed) / n if n else math.nan,
        "p_pass_phase1": sum(o.passed_phases >= 1 for o in decided) / n if n else math.nan,
        "median_days": percentile(days, 0.5),
        "p75_days": percentile(days, 0.75),
        "fail_daily_loss": fails["daily_loss"] / n if n else math.nan,
        "fail_max_loss": fails["max_loss"] / n if n else math.nan,
        "fail_time_limit": fails["time_limit"] / n if n else math.nan,
    }
    if rules.funded:
        res.update(
            {
                "funded_p_payout": statistics.fmean(o.funded_n_payouts > 0 for o in funded) if funded else math.nan,
                "funded_mean_payout": statistics.fmean(o.funded_payouts for o in funded) * rules.initial_balance
                if funded
                else math.nan,
                "funded_p_breach": statistics.fmean(o.funded_breached for o in funded) if funded else math.nan,
                "ev_per_attempt": statistics.fmean(o.value for o in complete) if complete else math.nan,
            }
        )
    else:
        res["ev_per_attempt"] = math.nan
    return res


def _fmt_pct(x: float) -> str:
    return "   n/a" if x != x else f"{x:6.1%}"


def _fmt_num(x: float, width: int = 7) -> str:
    return " " * (width - 3) + "n/a" if x != x else f"{x:{width},.0f}"


def load_inputs(args: argparse.Namespace) -> tuple[list[Trade], dict[str, float]]:
    trades: list[Trade] = []
    weights: dict[str, float] = {}
    seen: Counter = Counter()
    columns = {
        "open": args.col_open,
        "close": args.col_close,
        "pnl": args.col_pnl,
        "mae": args.col_mae,
        "mfe": args.col_mfe,
    }
    for spec in args.trades:
        path, _, w = spec.rpartition("@") if "@" in spec else (spec, "", "")
        loaded = load_trades(path, columns, args.date_format)
        stem = Path(path).stem
        seen[stem] += 1
        name = stem if seen[stem] == 1 else f"{stem}#{seen[stem]}"
        weights[name] = float(w) if w else 1.0
        trades.extend(replace(t, source=name) for t in loaded)
    return trades, weights


def print_inputs(trades, weights, days, args, out) -> dict:
    pnl = [d.pnl for d in days]
    mu = statistics.fmean(pnl)
    sd = statistics.pstdev(pnl)
    sharpe = mu / sd * math.sqrt(252) if sd > 0 else math.nan
    worst = min(days, key=lambda d: d.low)
    stats = {
        "trades": len(trades),
        "days": len(days),
        "traded_days": sum(d.traded for d in days),
        "first_day": days[0].date.isoformat(),
        "last_day": days[-1].date.isoformat(),
        "daily_mean": mu,
        "daily_sd": sd,
        "annualised_sharpe": sharpe,
        "worst_day_pnl": min(pnl),
        "worst_intraday_low": worst.low,
        "worst_intraday_low_date": worst.date.isoformat(),
    }
    print(f"Inputs: {len(trades)} trades from {len(weights)} file(s), "
          f"{stats['first_day']} to {stats['last_day']} ({len(days)} days, {stats['traded_days']} traded)", file=out)
    print(f"At scale 1.0: daily mean {mu:+.3%}, daily sd {sd:.3%}, annualised Sharpe {sharpe:.2f}, "
          f"worst day {min(pnl):+.2%}, worst intraday low {worst.low:+.2%} ({worst.date})", file=out)
    if len(weights) > 1:
        names = list(weights)
        series = {}
        for name in names:
            sub = [t for t in trades if t.source == name]
            sd_days = build_days(sub, args.ref_balance, args.day_start_hour,
                                 days[0].date, days[-1].date, weights)
            series[name] = {d.date: d.pnl for d in sd_days}
        dates = [d.date for d in days]
        print("Daily P&L correlation between strategies:", file=out)
        width = max(len(n) for n in names)
        corr = {}
        for a in names:
            row = []
            for b in names:
                xa = [series[a].get(d, 0.0) for d in dates]
                xb = [series[b].get(d, 0.0) for d in dates]
                try:
                    c = statistics.correlation(xa, xb)
                except statistics.StatisticsError:
                    c = math.nan
                corr[f"{a}|{b}"] = c
                row.append(f"{c:6.2f}")
            print(f"  {a:<{width}} " + " ".join(row), file=out)
        stats["correlation"] = corr
    return stats


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="propsim",
        description="Simulate prop-firm challenges on StrategyQuant X (or any) trade lists.",
    )
    p.add_argument("--trades", nargs="+", required=True,
                   help="trade-list CSV files; append @weight to scale one strategy (e.g. orb.csv@0.5)")
    p.add_argument("--rules", required=True, help="rules JSON file or preset name (see presets/)")
    p.add_argument("--ref-balance", type=float, required=True,
                   help="account balance the backtest P&L refers to (fixed position sizing assumed)")
    p.add_argument("--scale", type=float, help="position-size multiplier vs the backtest (default 1.0)")
    p.add_argument("--scan", help="scan multipliers start:stop:step, e.g. 0.25:3:0.25")
    p.add_argument("--method", choices=("historical", "bootstrap", "both"), default="both")
    p.add_argument("--paths", type=int, default=2000, help="bootstrap paths per scale (default 2000)")
    p.add_argument("--block", type=float, default=5.0, help="mean bootstrap block length in days (default 5)")
    p.add_argument("--hist-step", type=int, default=1, help="start a historical challenge every N days")
    p.add_argument("--max-path-days", type=int, default=2520, help="cap on simulated weekdays per path")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--from", dest="date_from", type=date.fromisoformat, help="first date to use (YYYY-MM-DD)")
    p.add_argument("--to", dest="date_to", type=date.fromisoformat, help="last date to use (YYYY-MM-DD)")
    p.add_argument("--day-start-hour", type=float, default=0.0,
                   help="hour (in the CSV's time zone) at which the firm's trading day starts")
    p.add_argument("--payout-reliability", type=float, default=1.0,
                   help="probability-weighted share of payouts actually received (counterparty haircut)")
    p.add_argument("--daily-guard", type=float,
                   help="EA equity stop: flatten for the day at this loss (fraction of initial balance, e.g. 0.03)")
    p.add_argument("--guard-slippage", type=float, default=0.0025,
                   help="extra loss beyond the guard level when it triggers (default 0.0025)")
    p.add_argument("--max-median-days", type=float,
                   help="only recommend scales whose median days-to-pass is at most this")
    p.add_argument("--json", help="write full results to this JSON file")
    p.add_argument("--date-format", help="strptime format for date columns if auto-detection fails")
    for role in ("open", "close", "pnl", "mae", "mfe"):
        p.add_argument(f"--col-{role}", help=f"name of the {role} column if not auto-detected")
    args = p.parse_args(argv)
    out = sys.stdout

    rules = resolve_rules(args.rules)
    trades, weights = load_inputs(args)
    days = build_days(trades, args.ref_balance, args.day_start_hour, args.date_from, args.date_to, weights)
    if len(days) < 20:
        raise SystemExit("fewer than 20 days of data in range; nothing meaningful to simulate")

    print(describe(rules), file=out)
    if args.daily_guard:
        print(f"  EA daily equity guard: {args.daily_guard:.1%} (+{args.guard_slippage:.2%} slippage)", file=out)
    print(file=out)
    stats = print_inputs(trades, weights, days, args, out)
    print(file=out)

    scales = parse_scales(args.scale, args.scan)
    methods = ["historical", "bootstrap"] if args.method == "both" else [args.method]
    targets = [ph.profit_target for ph in rules.phases]
    results = []
    for method in methods:
        header = (f"{'scale':>5} {'daily sd':>8} {'analytic':>8} {'P(ph1)':>7} {'P(all)':>7} "
                  f"{'med d':>6} {'p75 d':>6} {'dailyL':>7} {'maxL':>7} {'time':>7}")
        if rules.funded:
            header += f" {'P(paid)':>7} {'payout':>8} {'EV/try':>8}"
        print(f"== {method} ==" + (f" ({args.paths} paths, mean block {args.block:g} days)"
                                    if method == "bootstrap" else f" (start every {args.hist_step} day(s))"), file=out)
        print(header, file=out)
        for k in scales:
            rng = random.Random(args.seed)
            if method == "historical":
                paths = historical_paths(days, args.hist_step)
            else:
                paths = (stationary_bootstrap(days, rng, args.block, args.max_path_days) for _ in range(args.paths))
            outcomes = [run_challenge(path, rules, k, args.payout_reliability, args.daily_guard, args.guard_slippage)
                        for path in paths]
            s = summarize(outcomes, rules)
            s.update({"method": method, "scale": k, "daily_sd": k * stats["daily_sd"],
                      "analytic_p_pass_all": multi_phase_probability(
                          k * stats["daily_mean"], k * stats["daily_sd"], targets, rules.max_loss)})
            results.append(s)
            line = (f"{k:5.2f} {s['daily_sd']:8.2%} {_fmt_pct(s['analytic_p_pass_all']):>8} "
                    f"{_fmt_pct(s['p_pass_phase1']):>7} {_fmt_pct(s['p_pass_all']):>7} "
                    f"{_fmt_num(s['median_days'], 6)} {_fmt_num(s['p75_days'], 6)} "
                    f"{_fmt_pct(s['fail_daily_loss']):>7} {_fmt_pct(s['fail_max_loss']):>7} "
                    f"{_fmt_pct(s['fail_time_limit']):>7}")
            if rules.funded:
                line += (f" {_fmt_pct(s['funded_p_payout']):>7} {_fmt_num(s['funded_mean_payout'], 8)} "
                         f"{_fmt_num(s['ev_per_attempt'], 8)}")
            if s["incomplete"]:
                line += f"  ({s['incomplete']} incomplete)"
            print(line, file=out)
        print(file=out)

    recommend(results, args, rules, out)
    if args.json:
        Path(args.json).write_text(json.dumps({"rules": asdict(rules), "inputs": stats, "results": results},
                                              indent=2, default=str))
        print(f"Wrote {args.json}", file=out)
    return 0


def recommend(results: list[dict], args, rules: Rules, out) -> None:
    pool = [r for r in results if r["method"] == "bootstrap"] or results
    if args.max_median_days:
        pool = [r for r in pool if r["median_days"] == r["median_days"] and r["median_days"] <= args.max_median_days]
    if not pool:
        print("No scale meets --max-median-days; relax it or improve the strategy.", file=out)
        return
    best_p = max(pool, key=lambda r: r["p_pass_all"])
    print(f"Highest pass probability ({best_p['method']}): scale {best_p['scale']:.2f} -> "
          f"{best_p['p_pass_all']:.1%}, median {best_p['median_days']:.0f} calendar days", file=out)
    if rules.funded:
        best_ev = max(pool, key=lambda r: r["ev_per_attempt"] if r["ev_per_attempt"] == r["ev_per_attempt"] else -math.inf)
        print(f"Highest expected value per attempt ({best_ev['method']}): scale {best_ev['scale']:.2f} -> "
              f"EV {best_ev['ev_per_attempt']:,.0f} (pass {best_ev['p_pass_all']:.1%})", file=out)
    print("Out-of-sample data only. Treat these numbers as an upper bound: live edges decay.", file=out)


if __name__ == "__main__":
    raise SystemExit(main())
