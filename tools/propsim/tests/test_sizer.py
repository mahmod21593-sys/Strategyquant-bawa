import unittest
from datetime import date, timedelta

from propsim.engine import Account, Day, run_challenge
from propsim.rules import Phase, Rules


def rules():
    return Rules(name="t", initial_balance=100000, phases=[Phase(name="p1", profit_target=0.10, min_trading_days=1)],
                 max_loss=0.10, max_loss_type="static", daily_loss=None)


def days(pnls):
    d0 = date(2020, 1, 6)
    return [Day(d0 + timedelta(days=i), p, min(p, 0.0), max(p, 0.0), traded=True, n_trades=1) for i, p in enumerate(pnls)]


class TestSizer(unittest.TestCase):
    def test_constant_sizer_matches_scale(self):
        seq = days([0.02, -0.01, 0.03, 0.04, 0.03])
        a = run_challenge(seq, rules(), scale=2.0)
        b = run_challenge(seq, rules(), scale=99.0, sizer=lambda acct: 2.0)
        self.assertEqual(a.passed_all, b.passed_all)
        self.assertEqual(a.days_to_pass, b.days_to_pass)

    def test_cppi_sizer_avoids_breach(self):
        seq = days([-0.03] * 30)
        fixed = run_challenge(seq, rules(), scale=1.0)
        cppi = run_challenge(seq, rules(), sizer=lambda acct: 10 * acct.cushion())
        self.assertEqual(fixed.fail_reason, "max_loss")
        self.assertNotEqual(cppi.fail_reason, "max_loss")  # exposure shrinks with the cushion

    def test_cushion(self):
        acct = Account(rules(), 1.0)
        self.assertAlmostEqual(acct.cushion(), 0.10)


if __name__ == "__main__":
    unittest.main()
