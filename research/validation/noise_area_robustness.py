"""Post-hoc robustness of N3 (noise-area, US100), per the IM-04 card's falsification tests 3-4. Not pre-registered.
-> results/noise_area_robustness.json"""
import json
import os
from datetime import date

import vstats as vs
from run_noise_area import run, summarize

R = os.path.join(os.path.dirname(__file__), "results")


def s(rows, lo=date(2014, 1, 1), hi=date(2025, 12, 31)):
    x = summarize("r", rows, lo, hi)
    return {k: (round(v, 3) if isinstance(v, float) else v) for k, v in x.items() if k in ("n", "mean_bps", "t_hac", "p_one_sided", "sharpe_annual")}


def main():
    res = {}
    base, _, _ = run("N3")
    res["pre_registered"] = s(base)
    res["2014_2019"], res["2020_2025"] = s(base, hi=date(2019, 12, 31)), s(base, lo=date(2020, 1, 1))
    for lb in (10, 20):
        res[f"lookback_{lb}"] = s(run("N3", lookback=lb)[0])
    for g in (15, 60):
        res[f"grid_{g}min"] = s(run("N3", grid=g)[0])
    res["cost_3bps"] = s(run("N3", cost=3.0)[0])
    res["twap_stop_variant"] = s(run("N3", variant="twap_stop")[0])
    back, _, _ = run("N3", y0=2010)
    res["backward_2011_2013_unseen"] = s(back, lo=date(2011, 1, 1), hi=date(2013, 12, 31))
    x = [v for d, v in base if date(2014, 1, 1) <= d <= date(2025, 12, 31)]
    res["dsr_all_trials_N731"] = vs.deflated_sharpe(x, 731)
    res["dsr_family_N5"] = vs.deflated_sharpe(x, 5)
    json.dump(res, open(os.path.join(R, "noise_area_robustness.json"), "w"), indent=1, default=str)
    for k, v in res.items():
        print(k, v)


if __name__ == "__main__":
    main()
