import os
import sys
import unittest
from datetime import date
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data_histdata import LDN, NY, clock_shift  # noqa: E402


class TestHistDataClock(unittest.TestCase):
    """File time = London - 5 h (A14 addendum)."""

    def test_new_york_outside_gap_weeks(self):
        for d in (date(2026, 1, 14), date(2026, 6, 15), date(2025, 11, 4)):
            self.assertEqual(clock_shift(d, NY), 0)

    def test_new_york_in_gap_weeks(self):
        for d in (date(2026, 3, 10), date(2025, 3, 20), date(2025, 10, 28)):
            self.assertEqual(clock_shift(d, NY), 60)

    def test_london_and_berlin_constant(self):
        ber = ZoneInfo("Europe/Berlin")
        for d in (date(2026, 1, 14), date(2026, 3, 10), date(2026, 6, 15), date(2025, 10, 28)):
            self.assertEqual(clock_shift(d, LDN), 300)
            self.assertEqual(clock_shift(d, ber), 360)


if __name__ == "__main__":
    unittest.main()
