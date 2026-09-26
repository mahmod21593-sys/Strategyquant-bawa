import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from multitest import mann_whitney_z, pbo, romano_wolf, spa, walk_forward  # noqa: E402


class TestMultitest(unittest.TestCase):
    def test_spa_null_not_rejected_and_signal_found(self):
        rng = np.random.default_rng(1)
        ps = [spa(rng.normal(0, 1, (1000, 40)), 5, 500, seed=s)["p_spa"] for s in range(8)]
        self.assertGreater(np.mean(ps), 0.2)  # no systematic false rejection under the null
        X = rng.normal(0, 1, (1000, 40))
        X[:, 7] += 0.15  # t ~ 4.7
        r = spa(X, 5, 500)
        self.assertLess(r["p_spa"], 0.01)
        self.assertEqual(r["best_index"], 7)

    def test_romano_wolf_controls_fwer(self):
        rng = np.random.default_rng(2)
        X = rng.normal(0, 1, (1500, 60))
        X[:, 3] += 0.2
        p, t = romano_wolf(X, 5, 500)
        self.assertLess(p[3], 0.01)
        self.assertLessEqual((np.delete(p, 3) < 0.05).sum(), 2)
        self.assertTrue(np.all(p >= 0) and np.all(p <= 1))

    def test_pbo_null_near_half_and_low_with_signal(self):
        rng = np.random.default_rng(3)
        null = pbo(rng.normal(0, 1, (1600, 30)), S=10)["pbo"]
        self.assertGreater(null, 0.25)
        self.assertLess(null, 0.75)
        X = rng.normal(0, 1, (1600, 30))
        X[:, 0] += 0.25
        self.assertLess(pbo(X, S=10)["pbo"], 0.1)

    def test_mann_whitney_direction(self):
        self.assertGreater(mann_whitney_z(np.arange(10, 20.0), np.arange(0, 10.0)), 3)

    def test_walk_forward_is_out_of_sample(self):
        years = np.repeat(np.arange(2000, 2010), 100)
        X = np.zeros((1000, 3))
        X[years < 2005, 0] = 1.0  # great early, useless later
        X[:, 1] = np.where(np.arange(1000) % 2, 0.5, -0.4)
        out = walk_forward(X + 1e-9 * np.random.default_rng(0).normal(size=X.shape), years, 2006, 1, 200)
        self.assertTrue(np.all(out[years < 2006] == 0))


if __name__ == "__main__":
    unittest.main()
