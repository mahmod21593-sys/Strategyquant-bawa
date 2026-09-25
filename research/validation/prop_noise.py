"""I3 continued: prop books with MR-06 (US500, volatility-scaled) and the noise-area US100 rule (N3).
Intraday paths from minute bars; no Treasury strategies. -> results/prop_noise.json"""
import json
import os
from datetime import date

import vstats as vs
from round4_followup import combine, mr06_days, simulate
from run_noise_area import run

R = os.path.join(os.path.dirname(__file__), "results")


def main():
    mr = mr06_days()
    n3 = {d: v for d, v in run("N3", path=True)[0] if date(2014, 1, 1) <= d <= date(2025, 12, 31)}
    n3t = {d: v for d, v in run("N3", variant="twap_stop", path=True)[0] if date(2014, 1, 1) <= d <= date(2025, 12, 31)}
    x = [v[0] * 1e4 for v in n3.values()]
    res = {"n3_daily": {"mean_bps": vs.mean(x), "sd_bps": vs.sd(x), "mean_intraday_low_bps": vs.mean([v[1] * 1e4 for v in n3.values()])},
           "correlation_note": "MR-06 trades on ~19 days/yr; N3 is active most days (flat on ~40%)"}
    both = sorted(set(mr) & set(n3))
    a, b = [mr[d][0] for d in both], [n3[d][0] for d in both]
    ma, mb = vs.mean(a), vs.mean(b)
    res["corr_on_shared_days"] = sum((p - ma) * (q - mb) for p, q in zip(a, b)) / (len(a) - 1) / vs.sd(a) / vs.sd(b)
    books = {"N3 x2": ([n3], [2.0]), "N3 x3": ([n3], [3.0]), "N3 x4": ([n3], [4.0]), "N3 TWAP-stop x3 (post hoc)": ([n3t], [3.0]),
             "MR-06 x2": ([mr], [2.0]), "MR-06 x1 + N3 x2": ([mr, n3], [1.0, 2.0]), "MR-06 x2 + N3 x2": ([mr, n3], [2.0, 2.0]),
             "MR-06 x2 + N3 x3": ([mr, n3], [2.0, 3.0])}
    for preset, guard in (("two_step_10_5.json", 0.03), ("one_step_10_trailing.json", 0.02), ("futures_50k_eod_trailing.json", 0.02)):
        res[preset] = {name: simulate(combine(l, w), preset, guard) for name, (l, w) in books.items()}
        comb = combine([mr, n3], [2.0, 2.0])
        m = vs.mean([v[0] for v in comb.values()])
        res[preset]["zero_edge (MR-06 x2 + N3 x2, demeaned)"] = simulate({d: (v[0] - m, v[1] - m, v[2] - m) for d, v in comb.items()}, preset, guard)
    json.dump(res, open(os.path.join(R, "prop_noise.json"), "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if not k.endswith(".json")}, default=str))
    for p in ("two_step_10_5.json", "one_step_10_trailing.json", "futures_50k_eod_trailing.json"):
        print(p)
        for k, v in res[p].items():
            print("   ", k, v)


if __name__ == "__main__":
    main()
