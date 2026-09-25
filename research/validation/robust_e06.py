"""Post-confirmation robustness of E06 (>=3 consecutive down closes -> next-day return). Reported separately;
does not change the pre-registered verdict."""
import json, math, os, random
from datetime import date
import vstats as vs
from data_yahoo import daily
BPS = 1e4
def events(rows, k=3, hold=1):
    rets = [None] + [(b["c"] / a["c"] - 1) for a, b in zip(rows, rows[1:])]
    yr = {}
    for i in range(1, len(rows)):
        yr.setdefault(rows[i]["date"].year, []).append(rets[i] * BPS)
    base = {y: vs.mean(v) for y, v in yr.items()}
    closes = [r["c"] for r in rows]
    s200 = [None]*len(rows); s = 0
    for i, c in enumerate(closes):
        s += c
        if i >= 200: s -= closes[i-200]
        if i >= 199: s200[i] = s/200
    out = []
    for i in range(k + 1, len(rows) - hold + 1):
        if all(rets[i - j] < 0 for j in range(1, k + 1)):
            end = i + hold - 1
            x = (closes[end] / closes[i - 1] - 1) * BPS - hold * base[rows[end]["date"].year]
            out.append((rows[end]["date"], x, s200[i-1] is not None and closes[i-1] > s200[i-1], rets[i]*BPS))
    return out, [ (rets[i]*BPS - base[rows[i]["date"].year]) for i in range(1,len(rows)) ]
res = {}
def summ(ev, lo=None, hi=None):
    sel = [(d, x) for d, x, *_ in ev if (lo is None or d >= lo) and (hi is None or d < hi)]
    if len(sel) < 15: return {"n": len(sel)}
    return vs.summarize([d for d,_ in sel], [x for _,x in sel], 1, 5, 1.5, boot=False)
for sym, start in [("^GSPC", date(1970,1,1)), ("^NDX", date(1985,10,1)), ("^DJI", date(1992,1,1)), ("^RUT", date(1987,9,10)),
                   ("SPY", date(1993,1,29)), ("^GDAXI", date(1988,1,1)), ("^FTSE", date(1984,1,1)), ("^N225", date(1988,4,8)),
                   ("^STOXX50E", date(2007,3,30)), ("^GSPTSE", date(1980,1,1)), ("^SSMI", date(1991,1,1)), ("^HSI", date(1988,1,1)), ("^AXJO", date(2000,4,3))]:
    rows = [r for r in daily(sym) if r["date"] >= start]
    ev, _ = events(rows)
    res[sym] = {"all": summ(ev), "pre1990": summ(ev, None, date(1990,1,1)), "1990_2012": summ(ev, date(1990,1,1), date(2013,1,1)),
                "2013_on": summ(ev, date(2013,1,1)), "2020_on": summ(ev, date(2020,1,1))}
rows = [r for r in daily("^GSPC") if r["date"] >= date(1990,1,1)]
ev, allx = events(rows)
vals = [x for _, x, *_ in ev]
res["GSPC_1990_on_bootstrap_ci"] = vs.bootstrap_ci(vals)
res["GSPC_1990_on_randomization_p"] = vs.randomization_p(vs.mean(vals), lambda rng: vs.mean(rng.sample(allx, len(vals))))
res["GSPC_1990_on_dsr_N39"] = vs.deflated_sharpe(vals, 39)
res["GSPC_above_sma200"] = summ([e for e in ev if e[2]]); res["GSPC_below_sma200"] = summ([e for e in ev if not e[2]])
for k in (2, 4, 5):
    e, _ = events(rows, k=k); res[f"GSPC_k{k}"] = summ(e)
for h in (2, 3, 5):
    e, _ = events(rows, hold=h); res[f"GSPC_hold{h}"] = summ(e)
yrs = {}
for d, x, *_ in ev: yrs.setdefault(d.year, []).append(x)
res["GSPC_by_year"] = {y: round(vs.mean(v), 1) for y, v in sorted(yrs.items())}
json.dump(res, open("results/e06_robustness.json", "w"), indent=2, default=str)
def f(s): return f"n={s.get('n'):4d} mean={s.get('mean_bps', math.nan):6.1f} t={s.get('t_hac', math.nan):5.2f}" if 'mean_bps' in s else f"n={s.get('n')}"
for k, v in res.items():
    if isinstance(v, dict) and "all" in v:
        print(f"{k:10s} all[{f(v['all'])}] pre90[{f(v['pre1990'])}] 90-12[{f(v['1990_2012'])}] 13+[{f(v['2013_on'])}] 20+[{f(v['2020_on'])}]")
for k in ["GSPC_1990_on_bootstrap_ci","GSPC_1990_on_randomization_p","GSPC_1990_on_dsr_N39"]: print(k, res[k])
for k in ["GSPC_above_sma200","GSPC_below_sma200","GSPC_k2","GSPC_k4","GSPC_k5","GSPC_hold2","GSPC_hold3","GSPC_hold5"]: print(k, f(res[k]))
yy = res["GSPC_by_year"]; print("years positive", sum(v>0 for v in yy.values()), "of", len(yy))
