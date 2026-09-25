import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data_histdata import price  # noqa: E402
from run_histdata import orb5, orb30  # noqa: E402


def flat_day(px=100.0):
    return {m: (px, px, px, px) for m in range(570, 961)}


class TestPrice(unittest.TestCase):
    def test_close_of_previous_bar_then_open_then_nearest(self):
        tab = {"d": {599: (1, 1, 1, 2.0), 600: (3.0, 3, 3, 3)}}
        self.assertEqual(price(tab, "d", 600), 2.0)
        tab = {"d": {600: (3.0, 3, 3, 3)}}
        self.assertEqual(price(tab, "d", 600), 3.0)
        tab = {"d": {597: (1, 1, 1, 5.0)}}
        self.assertIsNone(price(tab, "d", 600, tol=2))
        self.assertEqual(price(tab, "d", 600, tol=3), 5.0)


class TestOrb5(unittest.TestCase):
    def test_long_stopped_at_candle_low(self):
        b = flat_day()
        b[570] = (100.0, 100.5, 99.8, 100.2)
        b[574] = (100.2, 100.4, 100.1, 100.3)  # first candle closes above its open -> long
        b[575] = (100.3, 100.3, 100.3, 100.3)
        b[600] = (100.3, 100.3, 99.0, 99.2)  # through the 99.8 stop
        bps, r = orb5(b)
        self.assertAlmostEqual(r, -1.0)
        self.assertAlmostEqual(bps, (99.8 / 100.3 - 1) * 1e4)

    def test_short_hits_10r_target(self):
        b = flat_day()
        b[570] = (100.0, 100.1, 99.7, 99.8)
        b[574] = (99.8, 99.9, 99.7, 99.9)  # 100.0 -> 99.9: bearish -> short
        b[575] = (99.9, 99.9, 99.9, 99.9)  # entry 99.9, stop 100.1, R = 0.2, target 97.9
        b[700] = (99.9, 99.9, 97.0, 97.5)
        bps, r = orb5(b)
        self.assertAlmostEqual(r, 10.0)

    def test_doji_no_trade(self):
        self.assertIsNone(orb5(flat_day()))


class TestOrb30(unittest.TestCase):
    def test_breakout_long_to_close(self):
        b = flat_day()
        b[580] = (100.0, 101.0, 99.0, 100.0)  # range 99-101
        b[650] = (100.5, 101.5, 100.5, 101.4)  # break up, fill at 101
        for m in range(651, 961):
            b[m] = (102.0, 102.0, 102.0, 102.0)
        tab = {"d": b}
        self.assertAlmostEqual(orb30(b, tab, "d"), (102 / 101 - 1) * 1e4)

    def test_ambiguous_bar_skipped(self):
        b = flat_day()
        b[580] = (100.0, 101.0, 99.0, 100.0)
        b[650] = (100.0, 101.5, 98.5, 100.0)
        self.assertEqual(orb30(b, {"d": b}, "d"), "ambiguous")


if __name__ == "__main__":
    unittest.main()
