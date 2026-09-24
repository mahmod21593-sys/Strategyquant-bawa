import io
import json
import random
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date, datetime, timedelta
from pathlib import Path

from propsim.cli import main
from propsim.trades import Trade, build_days, load_trades, parse_number, trading_date

SQX_LIKE = """Ticket;Symbol;Type;Open time;Open price;Close time;Close price;Size;Profit/Loss;MAE ($);MFE ($)
1;US500;Buy;2024.01.02 10:00;4700.0;2024.01.02 12:00;4705.0;1;100.00;50.00;120.00
2;US500;Sell;2024.01.02 11:00;4702.0;2024.01.02 13:00;4712.0;1;-200.00;250.00;30.00
3;US500;Buy;2024.01.05 15:00;4720.0;2024.01.05 15:30;4721.0;1;1 000,50;0;1100
"""


def write(tmp: Path, name: str, text: str) -> Path:
    p = tmp / name
    p.write_text(text, encoding="utf-8")
    return p


class Parsing(unittest.TestCase):
    def test_numbers(self):
        self.assertEqual(parse_number("1,234.50"), 1234.5)
        self.assertEqual(parse_number("1.234,50"), 1234.5)
        self.assertEqual(parse_number("12,5"), 12.5)
        self.assertEqual(parse_number("1,234"), 1234.0)
        self.assertEqual(parse_number("$ -45.20"), -45.2)
        self.assertEqual(parse_number("1 000,50"), 1000.5)

    def test_sqx_like_semicolon_file(self):
        with tempfile.TemporaryDirectory() as d:
            trades = load_trades(write(Path(d), "orb.csv", SQX_LIKE))
        self.assertEqual(len(trades), 3)
        self.assertEqual(trades[0].open_time, datetime(2024, 1, 2, 10, 0))
        self.assertEqual(trades[1].pnl, -200.0)
        self.assertEqual(trades[1].mae, 250.0)
        self.assertEqual(trades[2].pnl, 1000.5)
        self.assertEqual(trades[0].source, "orb")

    def test_missing_column_message(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(Path(d), "bad.csv", "a,b,c\n1,2,3\n")
            with self.assertRaisesRegex(ValueError, "--col-open"):
                load_trades(p)

    def test_column_override(self):
        text = "entered,left,money\n2024-01-02 10:00,2024-01-02 11:00,50\n"
        with tempfile.TemporaryDirectory() as d:
            trades = load_trades(write(Path(d), "x.csv", text),
                                 {"open": "entered", "close": "left", "pnl": "money"})
        self.assertEqual(trades[0].pnl, 50.0)


class DailyAggregation(unittest.TestCase):
    def test_overlapping_trades_conservative_low(self):
        with tempfile.TemporaryDirectory() as d:
            trades = load_trades(write(Path(d), "orb.csv", SQX_LIKE))
        days = build_days(trades, ref_balance=10_000)
        tue = next(x for x in days if x.date == date(2024, 1, 2))
        self.assertAlmostEqual(tue.pnl, -0.01)
        # Before trade 1 closes, both trades are assumed at their MAE: -(50 + 250) / 10k.
        self.assertAlmostEqual(tue.low, -0.03)
        # After trade 1 banks +1%, trade 2's MFE (+0.3%) can still stack on top.
        self.assertAlmostEqual(tue.high, 0.013)
        self.assertEqual(tue.n_trades, 2)

    def test_weekdays_filled_and_weekend_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            trades = load_trades(write(Path(d), "orb.csv", SQX_LIKE))
        days = build_days(trades, ref_balance=10_000)
        self.assertEqual([x.date for x in days], [date(2024, 1, 2) + timedelta(days=i) for i in range(4)])
        self.assertFalse(days[1].traded)

    def test_day_start_hour_shifts_trading_day(self):
        self.assertEqual(trading_date(datetime(2024, 1, 3, 1, 0), day_start_hour=2), date(2024, 1, 2))
        self.assertEqual(trading_date(datetime(2024, 1, 3, 3, 0), day_start_hour=2), date(2024, 1, 3))

    def test_weights_scale_one_strategy(self):
        t = [Trade(datetime(2024, 1, 2, 10), datetime(2024, 1, 2, 11), 100.0, source="a"),
             Trade(datetime(2024, 1, 2, 10), datetime(2024, 1, 2, 12), 100.0, source="b")]
        days = build_days(t, 10_000, weights={"b": 0.5})
        self.assertAlmostEqual(days[0].pnl, 0.015)


def synthetic_trades(path: Path, seed: int, n_days: int = 700) -> None:
    rng = random.Random(seed)
    lines = ["Open time,Close time,Profit/Loss,MAE"]
    d = date(2021, 1, 4)
    for _ in range(n_days):
        if d.weekday() < 5 and rng.random() < 0.8:
            pnl = rng.gauss(60, 400)
            mae = abs(min(pnl, 0)) + abs(rng.gauss(0, 100))
            o = datetime.combine(d, datetime.min.time()) + timedelta(hours=15, minutes=30)
            lines.append(f"{o:%Y.%m.%d %H:%M},{o + timedelta(minutes=30):%Y.%m.%d %H:%M},{pnl:.2f},{mae:.2f}")
        d += timedelta(days=1)
    path.write_text("\n".join(lines) + "\n")


class CommandLine(unittest.TestCase):
    def test_end_to_end_portfolio_scan(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / "orb.csv", Path(d) / "lasthour.csv"
            synthetic_trades(a, 1)
            synthetic_trades(b, 2)
            out_json = Path(d) / "res.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--trades", str(a), f"{b}@0.5", "--rules", "two_step_10_5",
                           "--ref-balance", "100000", "--scan", "1:2:1", "--paths", "200",
                           "--hist-step", "10", "--json", str(out_json)])
            text = buf.getvalue()
            self.assertEqual(rc, 0)
            self.assertIn("Daily P&L correlation", text)
            self.assertIn("== historical ==", text)
            self.assertIn("== bootstrap ==", text)
            self.assertIn("Highest pass probability", text)
            data = json.loads(out_json.read_text())
            self.assertEqual(len(data["results"]), 4)
            for r in data["results"]:
                self.assertGreaterEqual(r["p_pass_all"], 0.0)
                self.assertLessEqual(r["p_pass_all"], 1.0)

    def test_unknown_preset_lists_available(self):
        with tempfile.TemporaryDirectory() as d:
            a = Path(d) / "s.csv"
            synthetic_trades(a, 3)
            with self.assertRaises(SystemExit) as ctx:
                main(["--trades", str(a), "--rules", "nope", "--ref-balance", "100000"])
            self.assertIn("two_step_10_5", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
