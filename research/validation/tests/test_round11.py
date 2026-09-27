import os
import sys
import unittest
from datetime import date
from zoneinfo import ZoneInfo

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import run_family_a as fa  # noqa: E402
from data_minutes import EPOCH, group, price_at  # noqa: E402
from run_round11 import bracket_exit, gap_week, hybrid_signals, positions_up  # noqa: E402


def random_bars(n, seed):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    h = c * (1 + rng.uniform(0, 0.01, n))
    l = c * (1 - rng.uniform(0, 0.01, n))
    return c, h, l


class TestRound11(unittest.TestCase):
    def test_hybrid_signals_equal_family_a_when_the_mark_is_the_close(self):
        """With the 15:55 price equal to the close and the range up to the mark equal to the full range, the
        pre-close signals must be exactly family A's."""
        c, h, l = random_bars(900, 3)
        ret = np.r_[0.0, c[1:] / c[:-1] - 1]
        s_a, f_a = fa.signals(c, h, l, c, ret)
        s_h, f_h = hybrid_signals(c, c, h, l)
        for k in s_a:
            self.assertTrue(np.array_equal(s_a[k], s_h[k]), k)
        for k in f_a:
            self.assertTrue(np.array_equal(f_a[k].astype(bool), f_h[k].astype(bool)), k)

    def test_positions_up_equals_family_a_positions(self):
        c, h, l = random_bars(700, 4)
        ret = np.r_[0.0, c[1:] / c[:-1] - 1]
        sig, filt = fa.signals(c, h, l, c, ret)
        up = np.r_[False, c[1:] > c[:-1]]
        for sn in ("K3", "R10", "I25"):
            for ex in fa.EXITS:
                p1, e1 = fa.positions(sig[sn], filt["F0"], c, ex)
                p2, e2 = positions_up(sig[sn], filt["F0"], up, ex)
                self.assertTrue(np.array_equal(p1, p2) and np.array_equal(e1, e2), (sn, ex))

    def test_no_weekend_rule(self):
        """R2: no entry on a flagged bar, and an open position exits at the next flagged bar."""
        sig = np.array([True, False, False, False, True, False, False])
        flt = np.ones(7, dtype=bool)
        up = np.zeros(7, dtype=bool)  # never an up close: XU would hold 5 bars
        stop = np.array([False, False, True, False, True, False, False])
        pos, entry = positions_up(sig, flt, up, "XU", stop)
        self.assertEqual(list(pos), [0, 1, 1, 0, 0, 0, 0])  # entered at bar 0's mark, forced out at bar 2; bar 4 is blocked
        self.assertEqual(entry.sum(), 1)

    def test_bracket_exit(self):
        bars = np.array([[100, 100.5, 99.8, 100.2], [100.2, 101.2, 100.1, 101.0], [101.0, 101.1, 98.0, 98.5]])
        self.assertEqual(bracket_exit(bars, 1, 99.0, 101.0, 100.0), 101.0)  # target first
        self.assertEqual(bracket_exit(bars, 1, 99.0, None, 100.0), 99.0)  # no target: the stop in bar 3
        self.assertEqual(bracket_exit(bars, -1, 101.0, 99.0, 100.0), 101.0)  # short: stop at 101 in bar 2
        gap = np.array([[97.0, 97.5, 96.5, 97.2]])
        self.assertEqual(bracket_exit(gap, 1, 99.0, 101.0, 100.0), 97.0)  # gapped through the stop: filled at the open

    def test_price_at_and_group(self):
        day = np.array([10, 10, 10, 11, 11])
        mod = np.array([569, 570, 959, 570, 571])
        x = np.array([[1, 2, 0.5, 1.5], [1.5, 3, 1, 2], [2, 2.5, 1.8, 2.2], [5, 6, 4, 5.5], [5.5, 7, 5, 6]], dtype=float)
        self.assertEqual(price_at(day, mod, x, 570), {10: 1.5, 11: 5.0})  # close of 09:29 bar, else open of 09:30
        self.assertEqual(price_at(day, mod, x, 570, prefer_open=True), {10: 1.5, 11: 5.0})
        self.assertEqual(price_at(day, mod, x, 960), {10: 2.2})
        k, o, h, l, c, n, st = group(day, x)
        self.assertEqual(list(k), [10, 11])
        self.assertEqual(list(h), [3, 7])
        self.assertEqual(list(n), [3, 2])

    def test_gap_weeks(self):
        self.assertTrue(gap_week(date(2024, 3, 20)))  # US on DST, UK not yet
        self.assertFalse(gap_week(date(2024, 4, 10)))
        self.assertTrue(gap_week(date(2024, 10, 30)))  # UK back on GMT, US still on DST
        self.assertFalse(gap_week(date(2024, 1, 10)))
        self.assertEqual(EPOCH, date(1970, 1, 1).toordinal())


if __name__ == "__main__":
    unittest.main()
