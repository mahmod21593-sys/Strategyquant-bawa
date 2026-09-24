import unittest

from propsim.engine import run_challenge

from helpers import Funded, Phase, make_days, rules


class PhaseTargets(unittest.TestCase):
    def test_passes_when_target_reached(self):
        out = run_challenge(make_days([0.03] * 6), rules())
        self.assertTrue(out.passed_all)
        self.assertEqual(out.phase_days, [4])  # Mon..Thu
        self.assertEqual(out.days_to_pass, 4)

    def test_scale_multiplies_pnl(self):
        out = run_challenge(make_days([0.03] * 6), rules(), scale=2.0)
        self.assertEqual(out.phase_days, [2])

    def test_two_phases_restart_from_initial_balance(self):
        r = rules(phases=[Phase("P1", 0.05), Phase("P2", 0.05)])
        out = run_challenge(make_days([0.03] * 6), r)
        self.assertTrue(out.passed_all)
        self.assertEqual(out.phase_days, [2, 2])
        self.assertEqual(out.days_to_pass, 4)

    def test_incomplete_when_data_runs_out(self):
        out = run_challenge(make_days([0.01] * 3), rules())
        self.assertFalse(out.passed_all)
        self.assertEqual(out.fail_reason, "incomplete")
        self.assertFalse(out.decided)

    def test_time_limit(self):
        r = rules(phases=[Phase("P1", 0.10, max_days=5)])
        out = run_challenge(make_days([0.001] * 20), r)
        self.assertEqual(out.fail_reason, "time_limit")


class MinimumDays(unittest.TestCase):
    def test_pause_mode_waits_without_strategy_risk(self):
        r = rules(phases=[Phase("P1", 0.10, min_trading_days=4)], after_target="pause")
        out = run_challenge(make_days([0.11, -0.5, -0.5, -0.5, 0.0]), r)
        self.assertTrue(out.passed_all)
        self.assertEqual(out.phase_days, [4])

    def test_continue_mode_keeps_trading(self):
        r = rules(phases=[Phase("P1", 0.10, min_trading_days=4)], after_target="continue")
        out = run_challenge(make_days([0.11, -0.5, -0.5, -0.5, 0.0]), r)
        self.assertEqual(out.fail_reason, "max_loss")

    def test_pause_respects_time_limit(self):
        r = rules(phases=[Phase("P1", 0.10, min_trading_days=6, max_days=3)])
        out = run_challenge(make_days([0.11] + [0.0] * 10), r)
        self.assertEqual(out.fail_reason, "time_limit")


class DailyLoss(unittest.TestCase):
    def test_intraday_low_breaches_even_if_day_ends_positive(self):
        r = rules(daily_loss=0.05)
        out = run_challenge(make_days([0.01], lows=[-0.051]), r)
        self.assertEqual(out.fail_reason, "daily_loss")

    def test_just_inside_limit_survives(self):
        r = rules(daily_loss=0.05)
        out = run_challenge(make_days([0.01] + [0.03] * 4, lows=[-0.049] + [0.0] * 4), r)
        self.assertTrue(out.passed_all)

    def test_day_start_basis_grows_with_equity(self):
        pnls = [0.10, 0.0]
        lows = [0.0, -0.052]
        tight = rules(phases=[Phase("P1", 0.5)], daily_loss=0.05, daily_loss_basis="initial")
        loose = rules(phases=[Phase("P1", 0.5)], daily_loss=0.05, daily_loss_basis="day_start")
        self.assertEqual(run_challenge(make_days(pnls, lows=lows), tight).fail_reason, "daily_loss")
        # 5% of a 1.10 day-start balance is 5.5%, so a 5.2% dip survives.
        self.assertEqual(run_challenge(make_days(pnls, lows=lows), loose).fail_reason, "incomplete")


class EquityGuard(unittest.TestCase):
    def test_guard_turns_a_breach_into_a_bad_day(self):
        r = rules(daily_loss=0.05, phases=[Phase("P1", 0.5)])
        days = make_days([0.02, 0.0], lows=[-0.06, 0.0])
        self.assertEqual(run_challenge(days, r).fail_reason, "daily_loss")
        guarded = run_challenge(days, r, daily_guard=0.03, guard_slippage=0.005)
        self.assertEqual(guarded.fail_reason, "incomplete")

    def test_guard_books_the_loss_even_if_the_day_would_recover(self):
        r = rules(phases=[Phase("P1", 0.05)])
        days = make_days([0.04, 0.02], lows=[-0.035, 0.0])
        self.assertEqual(run_challenge(days, r).phase_days, [2])  # 0.04 + 0.02 >= 0.05
        guarded = run_challenge(days, r, daily_guard=0.03)
        self.assertEqual(guarded.fail_reason, "incomplete")  # -0.03 + 0.02 never reaches 0.05


class MaxLoss(unittest.TestCase):
    def test_static(self):
        out = run_challenge(make_days([-0.04, -0.04, -0.04]), rules())
        self.assertEqual(out.fail_reason, "max_loss")

    def test_trailing_eod_follows_closing_high(self):
        pnls, lows = [0.05, -0.02, 0.0], [0.0, -0.02, -0.045]
        trailing = rules(phases=[Phase("P1", 0.5)], max_loss=0.06, max_loss_type="trailing_eod")
        static = rules(phases=[Phase("P1", 0.5)], max_loss=0.06, max_loss_type="static")
        self.assertEqual(run_challenge(make_days(pnls, lows=lows), trailing).fail_reason, "max_loss")
        self.assertEqual(run_challenge(make_days(pnls, lows=lows), static).fail_reason, "incomplete")

    def test_trailing_lock_stops_floor_at_initial_balance(self):
        pnls, lows = [0.08, -0.07, 0.0], [0.0, -0.07, -0.015]
        locked = rules(phases=[Phase("P1", 0.5)], max_loss=0.06, max_loss_type="trailing_eod", trailing_lock=0.0)
        unlocked = rules(phases=[Phase("P1", 0.5)], max_loss=0.06, max_loss_type="trailing_eod")
        out_locked = run_challenge(make_days(pnls, lows=lows), locked)
        out_unlocked = run_challenge(make_days(pnls, lows=lows), unlocked)
        self.assertEqual(out_unlocked.fail_reason, "max_loss")  # floor 1.02 hit on day 2
        self.assertEqual(out_locked.fail_reason, "max_loss")  # floor 1.00 hit on day 3
        self.assertEqual(out_locked.phase_days, [])

    def test_trailing_intraday_counts_open_profit_high(self):
        days = make_days([0.0], lows=[-0.02], highs=[0.05]) + make_days([0.0] * 3)[1:]
        intraday = rules(phases=[Phase("P1", 0.5)], max_loss=0.06, max_loss_type="trailing_intraday")
        eod = rules(phases=[Phase("P1", 0.5)], max_loss=0.06, max_loss_type="trailing_eod")
        self.assertEqual(run_challenge(days, intraday).fail_reason, "max_loss")
        self.assertEqual(run_challenge(days, eod).fail_reason, "incomplete")


class Consistency(unittest.TestCase):
    def test_must_keep_trading_until_best_day_share_is_low_enough(self):
        r = rules(consistency=0.5)
        out = run_challenge(make_days([0.10] + [0.02] * 10), r)
        self.assertTrue(out.passed_all)
        self.assertEqual(out.days_to_pass, 8)  # 0.10 + 5 * 0.02 = 0.20 on the 6th weekday (Mon 8th)


class FundedStage(unittest.TestCase):
    def test_payouts_and_value(self):
        r = rules(
            phases=[Phase("P1", 0.02)],
            fee=500,
            fee_refund_on_first_payout=True,
            funded=Funded(horizon_days=29, payout_every_days=14, profit_split=0.8),
        )
        out = run_challenge(make_days([0.02] + [0.01] * 40), r)
        self.assertTrue(out.passed_all)
        self.assertEqual(out.funded_n_payouts, 2)
        self.assertAlmostEqual(out.funded_payouts, 0.8 * 0.11 + 0.8 * 0.10)
        self.assertAlmostEqual(out.value, 100_000 * (0.8 * 0.21))
        self.assertTrue(out.complete)

    def test_failed_challenge_loses_fee(self):
        r = rules(fee=500, funded=Funded())
        out = run_challenge(make_days([-0.11]), r)
        self.assertEqual(out.value, -500)

    def test_funded_breach(self):
        r = rules(phases=[Phase("P1", 0.02)], funded=Funded(horizon_days=100))
        out = run_challenge(make_days([0.02, -0.05, -0.06]), r)
        self.assertTrue(out.funded_breached)
        self.assertEqual(out.funded_n_payouts, 0)


if __name__ == "__main__":
    unittest.main()
