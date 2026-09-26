"""A14 (PREREGISTRATION.md): 2026 holdout of the HistData intraday rules. -> results/holdout_2026.json

Every rule is the frozen code from its round; 2025 is loaded only as warm-up and only 2026 days are scored.
"""
from __future__ import annotations

import json
import math
import os
from datetime import date

import run_histdata as rh
import run_round3 as r3
import run_round5 as r5
import run_scan as sc
import vstats as vs
from data_histdata import available_years, table
from run_noise_area import run

R = os.path.join(os.path.dirname(__file__), "results")
WARM = [2025, 2026]
H0 = date(2026, 1, 1)


def load(name):
    return json.load(open(os.path.join(R, name)))


def only_2026(rows):
    return [(d, x) for d, x in rows if d >= H0]


def compare(key, rows, m_is, t_is, cost=0.0, sign=1, note=None):
    """Holdout statistics and the pre-registered prediction check against the in-sample estimate."""
    rows = only_2026(rows)
    x = [sign * v for _, v in rows]
    out = {"n": len(x), "first": str(rows[0][0]) if rows else None, "last": str(rows[-1][0]) if rows else None,
           "in_sample_mean_bps": m_is, "in_sample_t": t_is}
    if note:
        out["note"] = note
    if len(x) < 30:
        out["verdict"] = "TOO FEW DAYS"
        return out
    m, t = vs.mean(x), vs.nw_t(x, 5)
    se_h = abs(m / t) if t else vs.sd(x) / math.sqrt(len(x))
    se_is = abs(m_is / t_is)
    z = (m - m_is) / math.hypot(se_h, se_is)
    log_bf = (m ** 2 - (m - m_is) ** 2) / (2 * se_h ** 2)
    w_is, w_h = 1 / se_is ** 2, 1 / se_h ** 2
    out.update({"mean_bps": m, "net_mean_bps": m - cost, "sd_bps": vs.sd(x), "t_hac": t, "p_one_sided": 1 - vs.N01.cdf(t),
                "se_bps": se_h, "z_vs_in_sample": z, "bayes_factor_edge_vs_zero": math.exp(max(min(log_bf, 50), -50)),
                "pooled_mean_bps": (w_is * m_is + w_h * m) / (w_is + w_h), "pooled_se_bps": (w_is + w_h) ** -0.5,
                "hit": vs.mean([v > 0 for v in x])})
    out["verdict"] = "REJECTED" if z < -1.645 else "CONSISTENT" if m > 0 else "INCONCLUSIVE"
    print(f"{key:14s} {out['verdict']:12s} n={len(x):4d} mean={m:7.2f} t={t:5.2f} | in-sample {m_is:6.2f} (t {t_is:4.2f}) "
          f"| z={z:5.2f} BF={out['bayes_factor_edge_vs_zero']:.2f} pooled={out['pooled_mean_bps']:.2f}", flush=True)
    return out


def main():
    res, group = {}, {}
    na, rob = load("noise_area.json"), load("noise_area_robustness.json")
    hd, rd3, rd5, scan = load("histdata.json"), load("round3.json"), load("round5.json"), load("scan_confirmation.json")

    # H1-H3: noise area (series are net of cost)
    for k in ("N3", "N1", "N2", "N4", "N5"):
        rows = run(k, y0=2025, y1=2027)[0]
        res[k] = compare(k, rows, na[k]["mean_bps"], na[k]["t_hac"])
        group[k] = "A" if k == "N3" else "B"
    tw = rob["twap_stop_variant"]
    res["N3_twap_stop"] = compare("N3_twap_stop", run("N3", variant="twap_stop", y0=2025, y1=2027)[0], tw["mean_bps"], tw["t_hac"],
                                  note="post hoc variant (B3)")
    group["N3_twap_stop"] = "A"

    # H4: R7 (gross; cost 1.5 bps)
    r3.r7(years=WARM)
    s = r3.SERIES["R7"]
    rows = [(date.fromisoformat(d), x) for d, x in zip(s["dates"], s["pnl_bps"])]
    res["R7"] = compare("R7", rows, rd3["R7"]["mean_bps"], rd3["R7"]["t_hac"], cost=1.5,
                        note="not a clean holdout: 2026 daily index closes entered the round-6 weekend diagnostic in aggregate")
    group["R7"] = "A"

    # H5: P10, P11 (the us_tests loop, gross; cost 1.5 bps)
    tabs = {s: table(s, WARM, rh.RTH | rh.EARLY) for s in ("SPXUSD", "NSXUSD")}
    p10, p11 = {}, {}
    for s, tab in tabs.items():
        p10[s], p11[s] = [], []
        for d in rh.us_days(tab):
            b = tab[d]
            r = rh.orb5(b)
            if r:
                p10[s].append((d, r[0]))
            r = rh.orb30(b, tab, d)
            if r is not None and r != "ambiguous":
                p11[s].append((d, r))
    for key, per in (("Q7_P10", p10), ("Q7_P11", p11)):
        ds, ps = rh.pool(per)
        res[key] = compare(key, list(zip(ds, ps)), hd[key]["mean_bps"], hd[key]["t_hac"], cost=1.5)
        group[key] = "A"

    # H6: P12 GER40 close momentum, R1 other European closes
    rh.YEARS_IDX = WARM
    rh.ger_test()
    s = rh.SERIES["Q7_P12"]
    res["Q7_P12"] = compare("Q7_P12", [(date.fromisoformat(d), x) for d, x in zip(s["dates"], s["pnl_bps"])],
                            hd["Q7_P12"]["mean_bps"], hd["Q7_P12"]["t_hac"], cost=1.5)
    r3.r1(years=WARM)
    s = r3.SERIES["R1"]
    res["R1"] = compare("R1", [(date.fromisoformat(d), x) for d, x in zip(s["dates"], s["pnl_bps"])], rd3["R1"]["mean_bps"],
                        rd3["R1"]["t_hac"], cost=1.5, note="CAC 40 and FTSE 100 only: HistData serves no Euro Stoxx 50 file after 2019")
    group["Q7_P12"] = group["R1"] = "A"

    # H7: T7 Asian index intraday momentum
    jp = r5.session_momentum("JPXJPY", lambda d: (15, 30) if d >= date(2024, 11, 5) else (15, 0), r5.TKY, available_years("JPXJPY", WARM))
    au = r5.session_momentum("AUXAUD", lambda d: (16, 0), r5.SYD, available_years("AUXAUD", WARM))
    rows, cost = r5.pooled({"JPXJPY": jp, "AUXAUD": au}, {"JPXJPY": 3.0, "AUXAUD": 3.0})
    res["T7"] = compare("T7", rows, rd5["T7"]["mean_bps"], rd5["T7"]["t_hac"], cost=cost)
    group["T7"] = "A"

    # H8: non-crypto scan candidates, signed excess as in A9
    sc.YEARS = WARM
    cache = {}
    for key, v in scan["results"].items():
        sym, name = key.split(":")
        if sc.INSTR[sym][0] == "crypto" or "sign" not in v:
            continue
        if sym not in cache:
            cache[sym] = sc.series(sym)[0]
        rows = [(d, e) for d, e, _ in cache[sym].get(name, [])]
        raw = {d: r for d, _, r in cache[sym].get(name, [])}
        out = compare(key, rows, v["mean_excess_signed_bps"], v["t_hac"], sign=v["sign"])
        sel = [d for d, _ in only_2026(rows)]
        if sel:
            out["net_raw_signed_bps"] = vs.mean([v["sign"] * raw[d] - sc.INSTR[sym][3] for d in sel])
        out["in_sample_verdict"] = v["verdict"]
        res[key] = out
        group[key] = "A" if v["verdict"] in ("WEAK", "CONFIRMED") else "B"

    # pipeline calibration
    cal = {}
    for g in ("A", "B"):
        ts = [res[k]["t_hac"] for k in res if group[k] == g and "t_hac" in res[k]]
        cal[g] = {"rules": [k for k in res if group[k] == g], "n": len(ts), "mean_t": vs.mean(ts) if ts else None,
                  "share_positive": vs.mean([t > 0 for t in ts]) if ts else None,
                  "z_if_independent": vs.mean(ts) * math.sqrt(len(ts)) if ts else None}
    res["_calibration"] = cal
    res["_group"] = group
    print("calibration", {g: {k: v[k] for k in ("n", "mean_t", "share_positive", "z_if_independent")} for g, v in cal.items()})
    json.dump(res, open(os.path.join(R, "holdout_2026.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
