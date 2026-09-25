"""Apply the pre-registered verdict rules to round 2 (family Q: A3, A4, A5). -> results/verdicts_round2.json

Holm/BH within Q and pooled with the round-1 primaries. DSR with N = 50 trials (A5). Appraisal flags record
problems found after the tests ran; they never change the rule-based verdict, only its interpretation.
"""
import json
import os

import vstats as vs

R = os.path.join(os.path.dirname(__file__), "results")
r2 = json.load(open(os.path.join(R, "round2.json")))
hd = json.load(open(os.path.join(R, "histdata.json")))
series = {**json.load(open(os.path.join(R, "series_round2.json"))), **json.load(open(os.path.join(R, "series_histdata.json")))}
r1 = json.load(open(os.path.join(R, "verdicts.json")))

N_TRIALS = 50
NAMES = {
    "Q1": "Macro-announcement premium (FOMC + employment), S&P 500", "Q2": "MR-06: buy next open, sell that close, SPY",
    "Q2b": "MR-06: buy next open, sell next-day close, SPY", "Q3": "MR-06 with a 15:30 signal, US ETFs (2023-26)",
    "Q5": "Crypto weekly TSMOM, BTC + ETH", "Q6": "FX W1 + W4, 9 USD pairs, 2004-2023 (HistData)",
    "Q7_P7": "Rest-of-day -> last 30 min, US500 2014-25", "Q7_P8": "First 30 min -> last 30 min, US500",
    "Q7_P9": "P7 with Rosa threshold, US500", "Q7_P10": "First-candle ORB (Zarattini & Aziz), US100 + US500",
    "Q7_P11": "30-min ORB stop entry, US100 + US500", "Q7_P12": "GER40 intraday momentum 17:00 -> 17:30",
    "Q7_P13": "Next-day reversal of last 30 min, US500", "Q7_P14": "US500 02:00 -> 03:00 ET drift (control)",
}
CONTROLS = {"Q7_P14"}
FLAGS = {
    "Q6": "MEASUREMENT ARTIFACT. HistData FX quotes are bids, and the bid drops at the NY 17:00 rollover in all 9 pairs "
          "(spread widening), which is where both windows start or end. That flatters USD-base pairs and hurts USD-quote pairs, "
          "matching the per-pair results. With clean boundaries (post hoc) W4 is gone after 2019 and the net P&L is about 0. "
          "See REPORT.md, Round 2.",
    "Q7_P10": "Sized by risk as in the paper (stop at the first candle), costs take the whole edge: median stop 12-20 bps, "
              "net about 0R per trade.",
    "Q7_P12": "Survives the post-hoc timing perturbations (t 3.9-4.8). Net of 1.5 bps: +0.57 full sample, -0.18 from 2022. "
              "Concentrated in the top tercile of |signal| (post hoc).",
    "Q2": "The MR-06 open-entry version; the edge that carries into realistic execution.",
}


def verdict(k, v, holm_p, post):
    net = v["net_mean_bps"]
    years = v.get("years_pred_sign")
    if k in CONTROLS:
        pre_p = v["pre"]["p_one_sided"]
        ok = pre_p < 0.05 and (post["p_one_sided"] >= 0.10 or post["mean_bps"] <= 0)
        return "DECAY CONFIRMED" if ok else "DECAY NOT CONFIRMED"
    sign_ok = v["mean_bps"] > 0
    post_ok = post is not None and post.get("mean_bps", -1) > 0 and post.get("p_one_sided", 1) < 0.10
    if sign_ok and holm_p < 0.05 and post_ok and net > 0 and (years is None or years >= 0.6):
        return "VALIDATED"
    if sign_ok and v["p_one_sided"] < 0.05 and net > 0:
        return "PARTIAL"
    out = "NOT VALIDATED"
    if v["mean_bps"] < 0 and v["p_one_sided"] > 0.975:
        out += " (significant opposite sign)"
    return out


def main():
    res = {**{k: r2[k] for k in ("Q1", "Q2", "Q2b", "Q3", "Q5")}, **{k: hd[k] for k in NAMES if k in hd}}
    pq = {k: v["p_one_sided"] for k, v in res.items()}
    pooled = {**pq, **{k: v["p_raw"] for k, v in r1.items() if k.startswith("P")}}
    holm_q, bh_q = vs.holm(pq), vs.bh(pq)
    holm_all, bh_all = vs.holm(pooled), vs.bh(pooled)
    out = {}
    for k, v in res.items():
        post = v.get("post_publication")
        if k == "Q3":  # no split: whole sample is the post-2022 regime
            post = {"p_one_sided": v["p_one_sided"], "mean_bps": v["mean_bps"], "n": v["n"], "from": "whole sample"}
        s = series.get(k)
        row = {"name": NAMES[k], "n": v["n"], "mean_bps": v["mean_bps"], "net_mean_bps": v["net_mean_bps"], "t": v["t_hac"],
               "p_raw": v["p_one_sided"], "p_holm_Q": holm_q[k], "q_bh_Q": bh_q[k], "p_holm_pooled": holm_all[k],
               "q_bh_pooled": bh_all[k], "pre": {x: v["pre"].get(x) for x in ("n", "mean_bps", "t_hac", "p_one_sided")} if "pre" in v else None,
               "post": {x: post.get(x) for x in ("n", "mean_bps", "t_hac", "p_one_sided", "from")} if post else None,
               "years_pred_sign": v.get("years_pred_sign"), "ci95_bps": v.get("ci95_bps"),
               "dsr_N50": vs.deflated_sharpe(s["pnl_bps"], N_TRIALS) if s else None}
        row["verdict_Q_family"] = verdict(k, v, holm_q[k], post)
        row["verdict_pooled_family"] = verdict(k, v, holm_all[k], post)
        if k in FLAGS:
            row["appraisal_flag"] = FLAGS[k]
        out[k] = row
    q4 = r2["Q4"]
    out["Q4"] = {"name": "MR-06 outside equity indices (mechanism check, two-sided)", "n": q4["n"], "mean_bps": q4["mean_bps"],
                 "t": q4["t_hac"], "p_two_sided": q4["p_two_sided"],
                 "per_asset_t": {a: round(x["t_hac"], 2) for a, x in q4["per_asset"].items()},
                 "verdict": "PREDICTION HELD (pooled approx 0), but TLT, IEF and UUP show reversal individually"}
    json.dump(out, open(os.path.join(R, "verdicts_round2.json"), "w"), indent=2, default=str)
    for k, v in out.items():
        if k == "Q4":
            print(k, v["verdict"])
            continue
        pp = v["post"] or {}
        print(f"{k:7s} {v['verdict_Q_family']:38s} pooled={v['verdict_pooled_family']:38s} mean={v['mean_bps']:7.2f} "
              f"net={v['net_mean_bps']:6.2f} t={v['t']:5.2f} p={v['p_raw']:.4f} holmQ={v['p_holm_Q']:.4f} "
              f"holmAll={v['p_holm_pooled']:.4f} post_p={pp.get('p_one_sided', float('nan')):.4f} "
              f"yrs={v['years_pred_sign'] if v['years_pred_sign'] is None else round(v['years_pred_sign'], 2)} dsr={v['dsr_N50'] if v['dsr_N50'] is None else round(v['dsr_N50'], 3)}")


if __name__ == "__main__":
    main()
