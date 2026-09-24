# edgelab — Phase 1 raw-edge studies

Before building anything in StrategyQuant X, the plan (doc 00, Phase 1) requires each hypothesis to
show its effect **in your own data, on your instruments, at a size that beats your costs**. edgelab
runs those studies on exported OHLC bars and prints the **Gate 1** verdict:

> Advance only if the effect has the predicted sign in **≥ 60% of calendar years**, the gross effect per
> trade is **> 2× round-trip costs**, and it holds in **≥ 2 markets**.

No optimisation, no genetic search: one fixed rule per hypothesis, so the result isn't contaminated by
data mining. Standard-library Python 3.10+ only (on Windows, `pip install tzdata` for time-zone names).

> **Keep the holdout locked:** pass `--to` so the most recent 2–3 years (doc 00, Phase 0) are excluded.

## Studies

| Command | Tests | Hypotheses | Source |
|---|---|---|---|
| `intraday-momentum` | Last-30m return vs first-30m and rest-of-day return; timing return; volatility-tercile mechanism check | IM-01, IM-05 | Gao et al. (2018); Baltussen et al. (2021) |
| `range-break` | Breakout of a time-window range (opening range, Asian range) held to a fixed exit, with an opposite-side stop; by range width / ATR | IM-02, IM-03, VB-02 | Crabel (1990); Holmberg et al. (2013) |
| `ibs` | Next-day return by IBS bucket above/below the 200-day SMA; N-day-low forward returns | MR-01, MR-02 | Pagonidis (2013); Baltussen, van Bekkum & Da (2019) |
| `tom` | Turn-of-month (last day + first 3) vs other days | CF-01 | McConnell & Xu (2008) |
| `compression` | Range expansion and next-day breakout after NR-n days, **with an ablation vs non-compressed days** | VB-01 | Crabel (1990) |
| `breakout` | Signed forward returns after N-day closing breakouts | TF-01 | Moskowitz, Ooi & Pedersen (2012) |
| `varratio` | Variance ratios by horizon: trending vs mean-reverting character | F1, F2, F9 | Lo & MacKinlay (1988) |
| `profile` | Mean return and volatility per time-of-day slot, with yearly sign stability | FX-01, VB-02, F9 | Ranaldo (2009); Andersen & Bollerslev (1997) |

## Examples for the prop-book shortlist (doc 05 §8)

```bash
cd tools/edgelab
# MT5 server time is usually New York close (GMT+2/+3): --file-tz NYCLOSE

# IM-01 / IM-05: last-half-hour continuation, US cash session
python -m edgelab intraday-momentum --bars US500_M5.csv US100_M5.csv \
    --file-tz NYCLOSE --tz America/New_York --open 09:30 --close 16:00 --to 2023-06-30 --cost-points 1.0

# IM-02: 30-minute opening-range breakout, exit 5 minutes before the close
python -m edgelab range-break --bars US100_M5.csv US500_M5.csv --file-tz NYCLOSE --tz America/New_York \
    --range-start 09:30 --range-end 10:00 --exit 15:55 --to 2023-06-30 --cost-points 1.5
# ...and on GER40 in Frankfurt time
python -m edgelab range-break --bars GER40_M5.csv --file-tz NYCLOSE --tz Europe/Berlin \
    --range-start 09:00 --range-end 09:30 --exit 17:25 --to 2023-06-30 --cost-points 1.5

# VB-02: Asian-range breakout at the London open
python -m edgelab range-break --bars EURUSD_M15.csv GBPUSD_M15.csv XAUUSD_M15.csv --file-tz NYCLOSE \
    --tz Europe/London --range-start 00:00 --range-end 08:00 --entry-end 11:00 --exit 17:00 --cost-bps 1.0

# MR-01: IBS dip-buying on indices (daily bars, or intraday aggregated to days)
python -m edgelab ibs --bars US500_D1.csv GER40_D1.csv UK100_D1.csv --to 2023-06-30 --cost-bps 1.5

# CF-01: turn of month
python -m edgelab tom --bars US500_D1.csv GER40_D1.csv JP225_D1.csv --cost-bps 1.5
```

Common options: `--from/--to` (date range), `--file-tz` and `--tz` (time zones), `--cost-bps` or
`--cost-points` (round-trip cost: spread + commission + slippage), `--min-years`, `--cost-mult`,
`--min-markets` (Gate 1 thresholds), `--json out.json`. Run `python -m edgelab <study> --help` for
study parameters.

## Input

Delimiter, header and date format are detected automatically. Tested with MT4/MT5 history exports
(`<DATE> <TIME> <OPEN> …`, tab-separated), Dukascopy (`Gmt time,Open,…` with `02.01.2024 09:30:00.000`),
headerless `date,time,open,high,low,close[,volume]` files (including `20240102,093000`), and
semicolon / decimal-comma files. Bars are assumed to be stamped at their **open** time. Use `--date-format`
if detection fails.

**Time zones:** `--file-tz` is the zone of the timestamps in the file: `UTC`, `UTC+2`, `NYCLOSE`
(New York + 7 h, the common MT server clock that follows US daylight saving), or an IANA name.
`--tz` is the zone that session times are given in. Converting through real time zones keeps the US
cash open at 09:30 even in the weeks when US and European daylight saving differ.

**Bar size:** M5 or M15 is a good default. Intraday studies need bars that divide the windows
(e.g. `--first 30` needs M1/M5/M15/M30). Ten years of M1 data works but is slow in pure Python.

## Reading the results

- **Primary / Gate 1** lines are what doc 00 asks for. A `PARK` lists the reason: wrong sign, unstable across years, or too small vs costs.
- **Mechanism checks** matter as much as the headline. Intraday momentum should be stronger on high-volatility days. The compression filter must beat the same breakout on ordinary days (ablation). If the headline passes but the mechanism check fails, be suspicious.
- **Many slots or buckets mean multiple testing.** The profile study prints how many slots would pass |t| ≥ 2 by chance.
- A pass here earns the hypothesis a place in the SQX build queue (doc 02 template, doc 03 funnel). It is not a tradable strategy yet.

## Tests

```bash
cd tools/edgelab
python -m unittest discover -s tests -t tests
```

The tests plant known effects in synthetic data (intraday momentum, IBS, turn of month, trend regimes,
autocorrelation, a time-of-day drift) and check they are found; confirm random data shows no edge;
check the variance-ratio z-statistic is calibrated under the null; hand-check breakout fills, stops, gaps
and ambiguous bars; and test file formats and time-zone conversion across daylight-saving changes.
