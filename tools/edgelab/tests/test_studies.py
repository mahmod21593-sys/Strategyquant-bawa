import io
import json
import random
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, time
from pathlib import Path

from edgelab import studies
from edgelab.bars import Bar
from edgelab.cli import gate, main
from edgelab.stats import nw_tstat, ols, variance_ratio

from synth import daily_bars, intraday_sessions, write_csv


class Statistics(unittest.TestCase):
    def test_variance_ratio_detects_autocorrelation(self):
        rng = random.Random(3)
        for phi, lo, hi in ((0.3, 1.2, 1.45), (-0.3, 0.6, 0.8), (0.0, 0.9, 1.1)):
            r, prev = [], 0.0
            for _ in range(5000):
                prev = phi * prev + rng.gauss(0, 1)
                r.append(prev)
            vr, z = variance_ratio(r, 2)
            self.assertTrue(lo < vr < hi, (phi, vr))
            if phi:
                self.assertGreater(abs(z), 5)

    def test_variance_ratio_z_is_calibrated_under_the_null(self):
        rejections = 0
        for s in range(150):
            rng = random.Random(100 + s)
            r = [rng.gauss(0, 1) * (3 if rng.random() < 0.1 else 1) for _ in range(800)]
            rejections += abs(variance_ratio(r, 4)[1]) > 1.96
        self.assertTrue(0.005 <= rejections / 150 <= 0.10, rejections)

    def test_ols_recovers_slope(self):
        rng = random.Random(1)
        x = [rng.gauss(0, 1) for _ in range(2000)]
        y = [0.5 * v + rng.gauss(0, 1) for v in x]
        o = ols(y, x)
        self.assertAlmostEqual(o["beta"], 0.5, delta=0.06)
        self.assertGreater(o["t"], 10)

    def test_newey_west_shrinks_t_for_overlapping_sums(self):
        rng = random.Random(2)
        e = [rng.gauss(0.05, 1) for _ in range(3000)]
        overl = [sum(e[i:i + 10]) for i in range(len(e) - 10)]
        naive = nw_tstat(overl, 0)
        robust = nw_tstat(overl, 9)
        self.assertLess(abs(robust), abs(naive))


class IntradayMomentum(unittest.TestCase):
    def test_planted_momentum_is_found(self):
        bars = intraday_sessions(500, seed=4, momentum=0.4)
        res = studies.intraday_momentum(bars, time(9, 30), time(16, 0))
        reg = res.tables[0][1][1]
        self.assertGreater(reg["beta"], 0.2)
        self.assertGreater(reg["t_hc"], 4)
        self.assertGreater(res.primary["effect_bps"], 0)

    def test_random_walk_has_no_edge(self):
        bars = intraday_sessions(500, seed=5, momentum=0.0)
        res = studies.intraday_momentum(bars, time(9, 30), time(16, 0))
        self.assertLess(abs(res.primary["t"]), 3)

    def test_bar_size_must_divide_periods(self):
        bars = intraday_sessions(60, seed=6)
        with self.assertRaisesRegex(ValueError, "multiples"):
            studies.intraday_momentum(bars, time(9, 30), time(16, 0), first_min=7)


def day_bars(day, spec):
    """spec: list of (HH:MM, o, h, l, c) on one day."""
    return [Bar(datetime.combine(day, time.fromisoformat(t)), o, h, l, c) for t, o, h, l, c in spec]


class RangeBreak(unittest.TestCase):
    def setUp(self):
        from datetime import date, timedelta
        self.days = [date(2024, 1, 1) + timedelta(days=i) for i in range(60)]

    def run_days(self, spec, **kw):
        bars = []
        for d in self.days:
            bars += day_bars(d, spec)
        return studies.range_break(bars, time(9, 30), time(10, 0), time(16, 0), **kw)

    def test_upside_break_held_to_exit(self):
        spec = [("09:30", 100, 101, 99, 100.5), ("10:00", 100.5, 101.5, 100.4, 101.2), ("15:55", 101.2, 102.1, 101, 102)]
        res = self.run_days(spec)
        row = res.tables[0][1][0]
        # Entry at the range high 101, exit at the 15:55 close 102: +99.0 bps, 0.5 R.
        self.assertAlmostEqual(row["mean_bps"], (102 - 101) / 101 * 1e4, places=6)
        self.assertAlmostEqual(row["mean_R"], 0.5)
        self.assertEqual(row["n"], 60)

    def test_stop_at_opposite_side(self):
        spec = [("09:30", 100, 101, 99, 100.5), ("10:00", 100.5, 101.5, 100.4, 101.2), ("11:00", 101, 101.1, 98.5, 98.8),
                ("15:55", 98.8, 99, 98, 98.2)]
        row = self.run_days(spec).tables[0][1][0]
        self.assertAlmostEqual(row["mean_bps"], (99 - 101) / 101 * 1e4, places=6)
        self.assertAlmostEqual(row["mean_R"], -1.0)

    def test_gap_through_the_level_fills_at_open(self):
        spec = [("09:30", 100, 101, 99, 100.5), ("10:00", 101.5, 102, 101.4, 101.8), ("15:55", 101.8, 102.1, 101.7, 102)]
        row = self.run_days(spec).tables[0][1][0]
        self.assertAlmostEqual(row["mean_bps"], (102 - 101.5) / 101.5 * 1e4, places=6)

    def test_ambiguous_bar_is_skipped(self):
        spec = [("09:30", 100, 101, 99, 100.5), ("10:00", 100.5, 101.5, 98.5, 100), ("15:55", 100, 100.2, 99.8, 100)]
        res = self.run_days(spec)
        self.assertIsNone(res.primary)
        self.assertIn("only 0 trades", res.notes[0])


class DailyStudies(unittest.TestCase):
    def test_planted_ibs_effect(self):
        bars = daily_bars(3000, seed=7, ibs_edge_bps=40)
        res = studies.ibs(bars)
        self.assertGreater(res.primary["effect_bps"], 15)
        self.assertGreater(res.primary["t"], 2.5)

    def test_planted_turn_of_month(self):
        bars = daily_bars(3000, seed=8, tom_edge_bps=25)
        res = studies.tom(bars)
        self.assertGreater(res.primary["effect_bps"], 50)
        self.assertGreater(res.primary["years_frac"], 0.7)

    def test_trend_regimes_show_in_breakouts(self):
        trend = studies.breakout(daily_bars(3000, seed=9, trend_regimes=15))
        noise = studies.breakout(daily_bars(3000, seed=9))
        self.assertGreater(trend.primary["effect_bps"], noise.primary["effect_bps"] + 50)

    def test_compression_runs_and_reports_ablation(self):
        res = studies.compression(daily_bars(2000, seed=10))
        self.assertIn("Ablation", res.notes[0])
        self.assertIsNotNone(res.primary)

    def test_varratio_on_bars(self):
        res = studies.varratio(daily_bars(3000, seed=11, ar=0.25))
        self.assertEqual(res.tables[0][1][0]["reading"], "trending")

    def test_profile_finds_planted_hour(self):
        rng = random.Random(12)
        bars, price = [], 100.0
        from datetime import date, timedelta
        for i in range(24 * 400):
            ts = datetime(2020, 1, 1) + timedelta(hours=i)
            drift = 0.0005 if ts.hour == 10 else 0.0
            o = price
            price = o * (1 + drift + rng.gauss(0, 0.001))
            bars.append(Bar(ts, o, max(o, price), min(o, price), price))
        rows = {r["slot"]: r for r in studies.profile(bars).tables[0][1]}
        self.assertGreater(rows["10:00"]["t"], 5)


class Gate(unittest.TestCase):
    def test_rules(self):
        p = {"effect_bps": 6.0, "sign": 1, "years_frac": 0.7}
        self.assertTrue(gate(p, 2.0, 0.6, 2.0)["advance"])
        self.assertFalse(gate(p, 4.0, 0.6, 2.0)["advance"])
        self.assertFalse(gate({**p, "years_frac": 0.5}, 2.0, 0.6, 2.0)["advance"])
        self.assertFalse(gate({**p, "effect_bps": -1.0}, None, 0.6, 2.0)["advance"])


class CommandLine(unittest.TestCase):
    def test_two_markets_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / "us500.csv", Path(d) / "us100.csv"
            write_csv(a, intraday_sessions(300, seed=13, momentum=0.5))
            write_csv(b, intraday_sessions(300, seed=14, momentum=0.5))
            out_json = Path(d) / "r.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["intraday-momentum", "--bars", str(a), str(b), "--open", "09:30", "--close", "16:00",
                           "--cost-bps", "0.5", "--json", str(out_json)])
            text = buf.getvalue()
            self.assertEqual(rc, 0)
            self.assertIn("Gate 1: ADVANCE", text)
            self.assertIn("Hypothesis Gate 1: ADVANCE (2 of 2", text)
            self.assertEqual(len(json.loads(out_json.read_text())), 2)

    def test_daily_study_from_intraday_file(self):
        with tempfile.TemporaryDirectory() as d:
            a = Path(d) / "x.csv"
            write_csv(a, daily_bars(1500, seed=15))
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(["tom", "--bars", str(a), "--cost-points", "0.1"])
            self.assertIn("Turn of month", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
