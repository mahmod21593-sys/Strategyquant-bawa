import unittest
from datetime import date, timedelta

from propsim.engine import Day, challenge_cost, run_challenge
from propsim.rules import Funded, Phase, Rules


def days(pnls, d0=date(2020, 1, 6)):
    return [Day(d0 + timedelta(days=i), p, min(p, 0.0), max(p, 0.0), traded=True, n_trades=1) for i, p in enumerate(pnls)]


def base(**kw):
    args = dict(name="t", initial_balance=50000, phases=[Phase(name="p1", profit_target=0.06, min_trading_days=1)],
                max_loss=0.04, max_loss_type="static", daily_loss=None)
    args.update(kw)
    return Rules(**args)


class TestFees(unittest.TestCase):
    def test_subscription_and_activation(self):
        r = base(fee=0.0, fee_per_30_days=49.0, fee_on_pass=149.0)
        self.assertEqual(challenge_cost(r, 1, False), 49.0)
        self.assertEqual(challenge_cost(r, 30, False), 49.0)
        self.assertEqual(challenge_cost(r, 31, True), 2 * 49.0 + 149.0)

    def test_failed_challenge_pays_months_used(self):
        r = base(fee=0.0, fee_per_30_days=49.0)
        out = run_challenge(days([0.0] * 40 + [-0.05]), r)
        self.assertEqual(out.fail_reason, "max_loss")
        self.assertEqual(out.value, -2 * 49.0)


class TestBestDayRule(unittest.TestCase):
    def test_positive_days_basis_is_looser_than_net(self):
        seq = days([0.03, -0.01, 0.02, 0.02])  # net 6%, winning days 7%, best 3%
        net = base(consistency=0.45)
        pos = base(consistency=0.45, consistency_basis="positive_days")
        self.assertFalse(run_challenge(seq, net).passed_all)  # 3% > 0.45 x 6% = 2.7%
        self.assertTrue(run_challenge(seq, pos).passed_all)  # 3% <= 0.45 x 7% = 3.15%


class TestPartialPayouts(unittest.TestCase):
    def rules(self, **fk):
        f = dict(horizon_days=60, payout_every_days=0, profit_split=0.9, payout_mode="partial", payout_fraction=0.5,
                 payout_cap=0.04, winning_days_required=5, winning_day_min=0.003, lock_floor_after_payout=True)
        f.update(fk)
        return base(max_loss_type="trailing_eod", trailing_lock=0.0, funded=Funded(**f))

    def test_payout_after_five_winning_days_capped_and_floor_locked(self):
        # pass on day 1 (+6%), then five +2% days in the funded stage -> balance +10%, payout min(5%, cap 4%)
        seq = days([0.06] + [0.02] * 5 + [-0.065])
        out = run_challenge(seq, self.rules())
        self.assertTrue(out.passed_all)
        self.assertEqual(out.funded_n_payouts, 1)
        self.assertAlmostEqual(out.funded_payouts, 0.9 * 0.04)
        # after the payout equity is 1.06 and the floor sits at 1.0, so a -6.5% day breaches
        self.assertTrue(out.funded_breached)

    def test_small_days_do_not_count_as_winning_days(self):
        seq = days([0.06] + [0.002] * 30)
        out = run_challenge(seq, self.rules())
        self.assertEqual(out.funded_n_payouts, 0)

    def test_funded_consistency_gate(self):
        seq = days([0.06] + [0.05, 0.005, 0.005, 0.005, 0.005] + [0.05] * 4)
        gated = run_challenge(seq, self.rules(consistency=0.4, winning_days_required=0))
        # best day 5% vs net 7% after five days: blocked until more profit arrives; pays once the ratio is <= 40%
        self.assertGreaterEqual(gated.funded_n_payouts, 1)
        free = run_challenge(seq, self.rules(winning_days_required=0))
        self.assertGreaterEqual(free.funded_n_payouts, gated.funded_n_payouts)

    def test_reset_mode_rejects_cap(self):
        with self.assertRaises(ValueError):
            Funded(payout_mode="reset", payout_cap=0.02)


if __name__ == "__main__":
    unittest.main()
