"""Round 11: append families L, M, Q, R to ../strategy_library.csv and write ../sqx_implementation_grid.csv
(the R1 reversal grid under the three SQX implementations). Idempotent: existing round-11 rows are replaced.

    python3 library_round11.py
"""
from __future__ import annotations

import csv
import json
import os

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "results")
LIB = os.path.join(HERE, "..", "strategy_library.csv")
GRID = os.path.join(HERE, "..", "sqx_implementation_grid.csv")
FAMILIES = {"l": "L FX/gold session seasonality", "m": "M FX night mean reversion", "q": "Q European open gap", "r": "R session-range breakout/fade"}
PARAMS = {"l": ("window", "side"), "m": ("signal", "exit"), "q": ("gap_k", "direction", "exit"), "r": ("range", "rule", "exit")}


def neighbours_r(name, names):
    """Family R one-step neighbours: same instrument and rule, other exit; same instrument, rule and exit, other range."""
    sym, rng, rule, ex = name.split("|")
    other_ex = {"END": "TGT", "TGT": "END"}[ex]
    other_rng = {"ASIA": "LDNAM", "LDNAM": "ASIA"}[rng]
    return [n for n in (f"{sym}|{rng}|{rule}|{other_ex}", f"{sym}|{other_rng}|{rule}|{ex}") if n in names]


def library_rows():
    rows = []
    for f, label in FAMILIES.items():
        res = json.load(open(os.path.join(RES, f"family_{f}.json")))
        trades = json.load(open(os.path.join(RES, f"family_{f}_trades.json")))["trade_stats"]
        verdict = res["family_verdict"]
        per_inst = res["raw"]["per_instrument"]
        rw = set(res["raw"]["romano_wolf_significant_5pct"])
        sv = {v["name"]: v["sharpe_validation_raw"] for v in res["variants"]}
        for v in res["variants"]:
            name = v["name"]
            inst, *parts = name.split("|")
            if verdict != "EDGE FAMILY":
                tier = f"reject (family {verdict.lower()})"
            elif name in rw:
                tier = "1 (Romano-Wolf significant)"
            elif per_inst[inst]["p_spa"] >= 0.05:
                tier = f"3 (market not significant: per-market SPA p={per_inst[inst]['p_spa']:.2f})" if v["sharpe_validation_raw"] > 0 else "reject"
            elif v["sharpe_validation_raw"] >= 0.3 and all(sv[n] > 0 for n in neighbours_r(name, sv)):
                tier = "2 (robust)"
            elif v["sharpe_validation_raw"] > 0:
                tier = "3 (positive; family R rests on this market)"
            else:
                tier = "reject"
            t = trades[name]
            rows.append({"family": label, "strategy": name, "instrument": inst,
                         "params": "; ".join(f"{k}={p}" for k, p in zip(PARAMS[f], parts)),
                         "trades_per_year": round(t["trades_per_year_val"], 1), "exposure_pct": "",
                         "sharpe_discovery": round(v["sharpe_discovery"], 2), "sharpe_validation_raw": round(v["sharpe_validation_raw"], 2),
                         "sharpe_validation_timing": "", "rw_p_timing": round(v["rw_p_verdict_basis"], 3), "sharpe_holdout_2026": "", "tier": tier})
    return rows


def write_library():
    with open(LIB, newline="") as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames
        old = [r for r in reader if r["family"] not in FAMILIES.values()]
    new = library_rows()
    with open(LIB, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(old + new)
    return len(old), len(new)


def write_grid():
    """One row per market x variant: validation-window Sharpe under each implementation (R1, 2014-01 -> 2026-08)."""
    r1 = json.load(open(os.path.join(RES, "round11_r1.json")))
    lib = {}
    with open(LIB, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["family"] == "A reversal":
                lib[r["strategy"]] = r["tier"]
    twin = {"US500": "SPY", "US100": "QQQ", "JP225": "^N225", "GER40": "^GDAXI", "XAUUSD": None}
    impls = ("a", "b", "c", "c_no_weekend")
    rows = []
    for key, v in sorted(r1["variants"].items()):
        market, sig, ex, flt = key.split("|")
        row = {"market": market, "signal": sig, "exit": ex, "filter": flt}
        for im in impls:
            row[f"sharpe_timing_{im}"] = round(v[im]["sharpe_timing"], 2)
            row[f"sharpe_raw_{im}"] = round(v[im]["sharpe_raw"], 2)
        row["trades_per_year_c"] = round(v["c"]["trades_per_year"], 1)
        row["exposure_pct_c"] = round(v["c"]["exposure"] * 100, 1)
        row["positive_timing_all_three"] = all(v[im]["sharpe_timing"] > 0 for im in ("a", "b", "c"))
        row["family_a_tier"] = lib.get(f"{twin[market]}|{sig}|{ex}|{flt}", "") if twin[market] else ""
        rows.append(row)
    with open(GRID, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    print("library rows kept/added", write_library())
    print("grid rows", write_grid())
