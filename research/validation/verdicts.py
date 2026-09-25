"""Apply the pre-registered verdict rules (PREREGISTRATION.md) to all results. -> results/verdicts.json"""
import json
import math
import os

import vstats as vs

R = os.path.join(os.path.dirname(__file__), "results")
daily = json.load(open(os.path.join(R, "daily.json")))
intra = json.load(open(os.path.join(R, "intraday_yahoo.json")))
series = {**json.load(open(os.path.join(R, "series_daily.json"))), **json.load(open(os.path.join(R, "series_intraday.json")))}
conf = json.load(open(os.path.join(R, "exploratory_confirmation.json")))
disc = json.load(open(os.path.join(R, "exploratory_discovery.json")))
e06 = json.load(open(os.path.join(R, "e06_robustness.json")))

N_TRIALS = 35  # 15 primary tests run + 20 exploratory candidates
NAMES = {
    "P1": "MR-01 IBS < 0.2 above SMA200, S&P 500", "P2": "MR-01 IBS, 9 non-US indices", "P3": "MR-02 5-day low, S&P 500 + Nasdaq 100",
    "P4": "Index 1-day reversal, 13 indices pooled", "P5": "Turn of month (control)", "P6": "TSMOM, 25 ETFs (MOP rule)",
    "P16": "Rebalancing flows, SPY/TLT", "P17": "Overnight premium, SPY + QQQ", "P18": "Pre-holiday, S&P 500",
    "P19": "Nagel mechanism: IBS trades high vs low VIX", "P7y": "Rest-of-day -> last 30 min, US ETFs (2023-26)",
    "P8y": "First hour -> last 30 min, US ETFs (2023-26)", "P9y": "P7y with signal threshold (Rosa)",
    "P13y": "Next-day reversal of last 30 min, US ETFs", "P15y": "FX fix reversal W3+W4, 9 pairs (2023-26)",
}
CONTROLS = {"P5"}
prim = {**{k: v for k, v in daily.items()}, **intra}

pvals = {k: v["p_one_sided"] for k, v in prim.items()}
holm, bh = vs.holm(pvals), vs.bh(pvals)
out = {}
for k, v in prim.items():
    post = v.get("post_publication")
    if k.endswith("y"):
        post = {"p_one_sided": v["p_one_sided"], "mean_bps": v["mean_bps"], "n": v["n"], "from": "whole sample is post-publication"}
    net = v.get("net_mean_bps", v.get("diff_bps"))
    years = v.get("years_pred_sign")
    s = series.get(k)
    dsr = vs.deflated_sharpe(s["pnl_bps"], N_TRIALS) if s else None
    row = {"name": NAMES[k], "n": v.get("n", (v.get("n_high", 0) + v.get("n_low", 0))), "mean_bps": v.get("mean_bps", v.get("diff_bps")),
           "net_mean_bps": net, "t": v.get("t_hac", v.get("t_welch")), "p_raw": v["p_one_sided"], "p_holm": holm.get(k), "q_bh": bh.get(k),
           "post": post, "years_pred_sign": years, "dsr": dsr, "ci95_bps": v.get("ci95_bps")}
    if k in CONTROLS:
        pre = next(x for x in v["splits"] if x["to"] != "end")
        pre_p, post_p = pre["p_one_sided"], post["p_one_sided"]
        row["verdict"] = "DECAY CONFIRMED" if pre_p < 0.05 and (post_p >= 0.10 or post["mean_bps"] <= 0) else "DECAY NOT CONFIRMED"
        row["pre_p"] = pre_p
    else:
        sign_ok = row["mean_bps"] > 0
        post_ok = post is not None and post["mean_bps"] > 0 and post["p_one_sided"] < 0.10
        net_ok = net is not None and net > 0
        years_ok = years is None or (years == years and years >= 0.6)
        if sign_ok and holm.get(k, 1) < 0.05 and post_ok and net_ok and years_ok:
            row["verdict"] = "VALIDATED"
        elif sign_ok and row["p_raw"] < 0.05 and net_ok:
            row["verdict"] = "PARTIAL"
        else:
            row["verdict"] = "NOT VALIDATED"
            if row["mean_bps"] < 0 and row["p_raw"] > 0.975:
                row["verdict"] += " (significant opposite sign)"
    out[k] = row

# exploratory
g = e06["GSPC_1990_on_bootstrap_ci"]
out["E06"] = {"name": "Exploratory: next day after >= 3 down closes, S&P 500 (confirmed on 2013+ and Nasdaq 100)",
              "discovery": {x: disc["E06"][x] for x in ("n", "mean_bps", "t_hac", "bh_q")},
              "confirmation_gspc": {x: conf["E06"]["gspc_2013"][x] for x in ("n", "mean_bps", "t_hac", "p_one_sided")},
              "confirmation_ndx": {x: conf["E06"]["ndx_2013"][x] for x in ("n", "mean_bps", "t_hac", "p_one_sided")},
              "ci95_bps_1990_on": g, "randomization_p": e06["GSPC_1990_on_randomization_p"], "dsr_N39": e06["GSPC_1990_on_dsr_N39"],
              "verdict": "CONFIRMED (exploratory, out-of-sample)" if conf["E06"]["CONFIRMED"] else "NOT CONFIRMED"}
for k in ("E07", "E10", "E16"):
    out[k] = {"name": f"Exploratory {k}", "verdict": "NOT CONFIRMED (discovered in 1990-2012, failed 2013+)",
              "discovery_mean_bps": disc[k]["mean_bps"], "confirmation_mean_bps": conf[k]["gspc_2013"]["mean_bps"],
              "confirmation_p": conf[k]["gspc_2013"]["p_one_sided"]}
json.dump(out, open(os.path.join(R, "verdicts.json"), "w"), indent=2, default=str)
for k, v in out.items():
    if k.startswith("P"):
        pp = v["post"] or {}
        print(f"{k:5s} {v['verdict']:45s} mean={v['mean_bps']:7.2f} net={v['net_mean_bps'] if v['net_mean_bps'] is None else round(v['net_mean_bps'],2)} "
              f"t={v['t']:5.2f} p={v['p_raw']:.4f} holm={v['p_holm']:.4f} post_p={pp.get('p_one_sided', float('nan')):.4f} "
              f"yrs={v['years_pred_sign']} dsr={v['dsr'] if v['dsr'] is None else round(v['dsr'],3)}")
    else:
        print(k, v["verdict"])
