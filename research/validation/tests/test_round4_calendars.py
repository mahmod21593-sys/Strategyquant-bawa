import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from run_round4 import easter, fix_day, hac_diff  # noqa: E402


class TestCalendars(unittest.TestCase):
    def test_easter(self):
        self.assertEqual(easter(2024), date(2024, 3, 31))
        self.assertEqual(easter(2013), date(2013, 3, 31))
        self.assertEqual(easter(2019), date(2019, 4, 21))

    def test_fix_day_skips_uk_holidays_and_weekends(self):
        self.assertEqual(fix_day(2024, 3), date(2024, 3, 28))   # Good Friday 29 March
        self.assertEqual(fix_day(2015, 8), date(2015, 8, 28))   # 31 August bank holiday
        self.assertEqual(fix_day(2021, 5), date(2021, 5, 28))   # 31 May spring bank holiday
        self.assertEqual(fix_day(2022, 5), date(2022, 5, 31))   # jubilee year: 30 May was not a holiday
        self.assertEqual(fix_day(2020, 2), date(2020, 2, 28))   # 29 Feb 2020 was a Saturday
        self.assertEqual(fix_day(2023, 12), date(2023, 12, 29))

    def test_hac_diff_mean_difference(self):
        r = [0.5, 3.5, 1.5, 2.5, 1.0, 3.0]
        d = [0, 1, 0, 1, 0, 1]
        out = hac_diff(r, d)
        self.assertAlmostEqual(out["diff_bps"], 2.0)


if __name__ == "__main__":
    unittest.main()
