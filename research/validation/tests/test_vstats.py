import math
import random
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import vstats as vs  # noqa: E402


class Stats(unittest.TestCase):
    def test_hac_t_matches_iid_t_at_lag0(self):
        rng = random.Random(1)
        x = [rng.gauss(0.1, 1) for _ in range(3000)]
        naive = vs.mean(x) / (vs.sd(x) / math.sqrt(len(x)))
        self.assertAlmostEqual(vs.nw_t(x, 0), naive, delta=0.05)

    def test_hac_shrinks_t_for_autocorrelated_series(self):
        rng = random.Random(2)
        e = [rng.gauss(0.05, 1) for _ in range(3000)]
        x = [sum(e[i:i + 10]) for i in range(len(e) - 10)]
        self.assertLess(abs(vs.nw_t(x, 10)), abs(vs.nw_t(x, 0)))

    def test_bootstrap_ci_covers_true_mean(self):
        rng = random.Random(3)
        x = [rng.gauss(2.0, 5) for _ in range(800)]
        lo, hi = vs.bootstrap_ci(x, reps=400)
        self.assertLess(lo, 2.0)
        self.assertGreater(hi, 2.0)

    def test_holm_and_bh(self):
        p = {"a": 0.01, "b": 0.04, "c": 0.03}
        self.assertEqual(vs.holm(p), {"a": 0.03, "c": 0.06, "b": 0.06})
        self.assertAlmostEqual(vs.bh(p)["a"], 0.03)
        self.assertAlmostEqual(vs.bh(p)["b"], 0.04)

    def test_deflated_sharpe_penalises_noise(self):
        rng = random.Random(4)
        noise = [rng.gauss(0, 1) for _ in range(1000)]
        self.assertLess(vs.deflated_sharpe(noise, 35), 0.5)
        self.assertGreater(vs.deflated_sharpe([v + 0.2 for v in noise], 35), 0.95)

    def test_randomization_p_uniform_under_null(self):
        rng = random.Random(5)
        pool = [rng.gauss(0, 1) for _ in range(2000)]
        p = vs.randomization_p(vs.mean(rng.sample(pool, 100)), lambda r: vs.mean(r.sample(pool, 100)), reps=500)
        self.assertTrue(0.0 < p <= 1.0)
        big = vs.randomization_p(1.0, lambda r: vs.mean(r.sample(pool, 100)), reps=500)
        self.assertLess(big, 0.01)

    def test_year_share(self):
        ds = [date(2000, 1, 1) + timedelta(days=i) for i in range(3 * 365)]
        vals = [1.0 if d.year != 2001 else -1.0 for d in ds]
        share, n = vs.year_share(ds, vals, 1)
        self.assertEqual(n, 3)
        self.assertAlmostEqual(share, 2 / 3)


if __name__ == "__main__":
    unittest.main()
