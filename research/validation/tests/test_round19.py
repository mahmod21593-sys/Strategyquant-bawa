"""Round 19 (A33): the Gotobi calendar that the GT rule and its SQX build depend on."""
import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import holidays  # noqa: F401
    HAVE = True
except ImportError:
    HAVE = False


@unittest.skipUnless(HAVE, "python `holidays` not installed")
class TestGotobi(unittest.TestCase):
    def setUp(self):
        from data_calendar import gotobi_days, japan_holidays
        self.g = gotobi_days(2024, 2025)
        self.hol = japan_holidays(2024, 2025)

    def test_weekend_and_holidays_move_back(self):
        # 2025-01-05 is a Sunday; Jan 1-3 and Dec 31 are bank holidays -> 2024-12-30 (also December's last business day)
        self.assertEqual(self.g[date(2024, 12, 30)], "ME")
        self.assertNotIn(date(2025, 1, 3), self.g)
        # 2025-05-05 (Children's Day) and May 3-6 holidays -> Friday 2025-05-02
        self.assertIn(date(2025, 5, 2), self.g)
        self.assertNotIn(date(2025, 5, 5), self.g)

    def test_month_end_and_plain_days(self):
        self.assertEqual(self.g[date(2025, 1, 31)], "ME")
        self.assertEqual(self.g[date(2025, 2, 28)], "ME")
        self.assertEqual(self.g[date(2025, 1, 10)], "510")
        self.assertEqual(self.g[date(2025, 1, 30)], "510")
        # 2025-01-25 is a Saturday -> Friday 2025-01-24
        self.assertIn(date(2025, 1, 24), self.g)

    def test_only_business_days(self):
        for d in self.g:
            self.assertLess(d.weekday(), 5)
            self.assertNotIn(d, self.hol)


if __name__ == "__main__":
    unittest.main()
