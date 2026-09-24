import random
import unittest

from propsim.analytic import expected_days, multi_phase_probability, pass_probability
from propsim.engine import run_challenge
from propsim.rules import Phase

from helpers import make_days, rules


class ClosedForm(unittest.TestCase):
    def test_zero_drift_is_distance_ratio(self):
        self.assertAlmostEqual(pass_probability(0.0, 0.01, 0.10, 0.10), 0.5)
        self.assertAlmostEqual(pass_probability(0.0, 0.01, 0.08, 0.10), 10 / 18)

    def test_positive_and_negative_drift_are_mirror_images(self):
        up = pass_probability(0.001, 0.01, 0.10, 0.10)
        down = pass_probability(-0.001, 0.01, 0.10, 0.10)
        self.assertAlmostEqual(up + down, 1.0)
        self.assertAlmostEqual(up, 0.880797, places=5)

    def test_extreme_values_do_not_overflow(self):
        self.assertAlmostEqual(pass_probability(0.05, 0.001, 0.1, 0.1), 1.0)
        self.assertAlmostEqual(pass_probability(-0.05, 0.001, 0.1, 0.1), 0.0)

    def test_zero_drift_expected_time(self):
        self.assertAlmostEqual(expected_days(0.0, 0.01, 0.10, 0.10), 100.0)

    def test_multi_phase_is_product(self):
        p = multi_phase_probability(0.0, 0.01, [0.10, 0.05], 0.10)
        self.assertAlmostEqual(p, 0.5 * (10 / 15))


class SimulatorMatchesTheory(unittest.TestCase):
    def test_gaussian_days_converge_to_first_passage_formula(self):
        mu, sd = 0.0005, 0.005
        rng = random.Random(7)
        r = rules(phases=[Phase("P1", 0.05)], max_loss=0.05)
        n = 3000
        passed = 0
        for _ in range(n):
            days = make_days([rng.gauss(mu, sd) for _ in range(1500)])
            passed += run_challenge(days, r).passed_all
        theory = pass_probability(mu, sd, 0.05, 0.05)
        self.assertAlmostEqual(passed / n, theory, delta=0.03)


if __name__ == "__main__":
    unittest.main()
