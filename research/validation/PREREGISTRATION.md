# Pre-registration: own-data statistical validation

**Written and committed on 2026-09-25, before any test result was computed.** The git commit
timestamp of this file is the evidence of ordering. Any later change to a test is logged in the
"Amendments" section with its reason, and reported as a deviation.

## Data

| Source | Instruments | Notes |
|---|---|---|
| Yahoo chart API, daily | Indices: ^GSPC, ^NDX, ^DJI, ^RUT, ^GDAXI, ^FTSE, ^FCHI, ^N225, ^STOXX50E, ^AXJO, ^HSI, ^GSPTSE, ^SSMI, ^VIX. ETFs: SPY, QQQ, IWM, EFA, EEM, EWJ, TLT, IEF, SHY, LQD, HYG, GLD, SLV, USO, UNG, DBC, DBA, UUP, FXE, FXY, FXB, FXA, FXC, FXF, VNQ | Index OHLC is price-only; ETF "adjusted close" includes distributions |
| Dukascopy, BID candles | Minute: USA500IDXUSD, USATECHIDXUSD, DEUIDXEUR (2014 → 2026-09-18). Hourly: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, USDNOK, USDSEK (2004 → 2026-08) | CFD / OTC quotes, not exchange prints. Intraday tests run **only if the download completes**; otherwise they are reported as NOT RUN |

End date for all tests: the last available bar (≈ 2026-09-24). **No holdout is reserved**, because this is
an evidence audit, not a strategy build. Every result below is therefore in-sample for the purpose of
any later SQX build, and the build must use fresh data.

## Statistics (same for every test)

- **Unit:** return per trade (or per day for always-in-market rules), in basis points of price, gross and net of the pre-registered cost.
- **t-statistic:** Newey-West HAC, lag = max(5, holding days); one-sided p-value in the predicted direction.
- **95% CI:** stationary bootstrap of the per-period P&L series (mean block 10 periods, 2,000 resamples, seed 20260925).
- **Randomization p-value** (where marked R): the signal is replaced by a random signal with the same frequency (5,000 draws). p = share of draws with mean ≥ observed.
- **Year consistency:** share of calendar years (≥ 5 trades) with the predicted sign.
- **Splits:** each test reports the original-paper period and the post-publication period separately.
- **Multiple testing:** the primary tests P1–P19 form one family. Report raw one-sided p, Holm-adjusted p, and Benjamini-Hochberg q. Deflated Sharpe ratio uses N = number of primary tests actually run.
- **Costs** (round trip, bps of price): index CFD/futures 1.5; FX majors 1.0 per pair per window; ETFs 2.0 (spread + slippage); monthly-rebalanced ETF TSMOM 5 bps per unit of turnover.

## Verdict rules (fixed now)

| Verdict | Rule |
|---|---|
| **VALIDATED** | Predicted sign; Holm-adjusted p < 0.05 on the full sample; post-publication subsample same sign with one-sided p < 0.10; net-of-cost mean > 0; predicted sign in ≥ 60% of years |
| **PARTIAL** | Predicted sign, raw p < 0.05, net > 0, but fails Holm or the post-publication condition |
| **NOT VALIDATED** | Anything else |
| **DECAY CONFIRMED** (controls only) | Pre-period one-sided p < 0.05 and post-period p ≥ 0.10 (or wrong sign) |

## Primary tests

| ID | Edge | Data / sample | Rule (exact) | Predicted | Split |
|---|---|---|---|---|---|
| P1 | MR-01 IBS, US | ^GSPC, 1990-01-01 → end | Long next close-to-close when C > SMA200 and IBS < 0.2. Metric: return minus same-year mean daily return | + | ≤ 2013 / ≥ 2014 |
| P2 | MR-01 IBS, non-US | 9 non-US indices pooled (DAX, FTSE, CAC, N225, STOXX50, ASX200, HSI, TSX, SMI), from first real H/L | Same as P1 | + (Baltussen et al.) vs ≈ 0 (Pagonidis) | ≤ 2013 / ≥ 2014 |
| P3 | MR-02 5-day low | ^GSPC and ^NDX, 1990 → | C < min(prev 5 closes) and C > SMA200: long 3 days, no overlapping trades; excess over 3 × same-year mean daily return | + | ≤ 2013 / ≥ 2014 |
| P4 | Index reversal (Baltussen, van Bekkum & Da) | 13 indices pooled, 2000 → | Daily position = −sign(yesterday's return), always in market | + | 2000–2016 / 2017 → |
| P5 | Turn of month (**control**) | ^GSPC 1970 → | Last trading day + first 3 of month vs other days (difference in mean daily return) | decay | ≤ 2000 / ≥ 2001 |
| P6 | TF-01 TSMOM (MOP 2012 rule) | 25 ETFs, monthly, 2007-01 → | sign(12-month total return) × (40% / σ_EWMA,60d); equal-weight across instruments available that month | + | 2007–2012 / 2013–2019 / 2020 → |
| P7 | IM-01b Baltussen | US500 minute, 2014 → | sign(prior 16:00 close → 15:30 ET) held 15:30 → 16:00 ET | + | 2014–2021 / 2022 → (0DTE) |
| P8 | IM-01a Gao | US500 minute, 2014 → | sign(prior close → 10:00 ET) held 15:30 → 16:00 | + | as P7 |
| P9 | IM-05 Rosa threshold | US500 minute, 2014 → | P7 but only when abs(signal) > 1.0 × rolling 60-day sd of the signal (computed on prior days) | + | as P7 |
| P10 | IM-02A first-candle ORB | US100 + US500 minute, 2014 → | Zarattini & Aziz rules (first 5-min bar direction, entry at bar-2 open, stop at bar-1 extreme, 10R or close) | + | 2014–2022 / 2023 → |
| P11 | IM-02B 30-min ORB | US100 + US500 minute, 2014 → | Stop entry at the 09:30–10:00 range, exit 15:59, stop at opposite side | + | as P10 |
| P12 | GER40 intraday momentum | DEUIDXEUR minute, 2014 → | sign(prior 17:30 close → 17:00 Frankfurt) held 17:00 → 17:30 | + | 2014–2021 / 2022 → |
| P13 | MR-04 next-day reversal | US500 minute + daily, 2014 → | Position next day (close → close) = −sign(last-30-min return) | + | as P7 |
| P14 | Overnight drift 02–03 ET (**control**) | US500 minute, 2014 → | Long 02:00 → 03:00 ET | decay | 2014–2020 / 2021 → |
| P15 | FX-01 fix reversal (Krohn et al.) | 9 USD pairs hourly, 2004 → | Short-USD basket from London 16:00 → NY 17:00 and long-USD basket from London 08:00 → London 16:00; daily P&L = average over pairs | + | 2004–2018 / 2019 → |
| P16 | CF-02 rebalancing (Harvey et al.) | SPY, TLT daily 2003 → | On the last trading day of each month: z = (SPY MTD − TLT MTD return) / 36-month rolling sd of that spread; position in SPY for the next day = −z (capped ±2) | + | 2003–2023 / 2023-04 → |
| P17 | Overnight premium (Cliff, Cooper & Gulen 2008; Lou, Polk & Skouras 2019) | SPY and QQQ daily 1999 → | Long close → next open vs open → close | close → open > 0 | 1999–2012 / 2013 → |
| P18 | Pre-holiday (Ariel 1990) | ^GSPC 1970 → | Return on the trading day before an exchange holiday (weekday gap) vs other days | + | ≤ 2000 / ≥ 2001 |
| P19 | Nagel mechanism for MR | ^GSPC 1990 → with ^VIX | P1 trades split by prior-day VIX tercile: high-tercile mean > low-tercile mean | + (difference) | none |

## Secondary (reported, not in the multiple-testing family)

- P2 per country; P4 per index; P6 per instrument and vs vol-scaled buy-and-hold (Kim, Tse & Wald).
- Variance ratio VR(5) per index by decade.
- FX windows around the Tokyo fix (W1/W2).
- Break-even cost for every primary test.

## Amendments

### A1 (2026-09-25, after the daily primaries P1–P6 and P16–P19 were run, before any intraday test)

The daily primaries are unchanged. Added an **exploratory scan** to search for new edges without
fooling ourselves. The US-only pattern in the P4 secondaries motivated its inclusion, which is why it
is labelled exploratory and must pass an independent confirmation period.

- **Universe:** ^GSPC (primary) and ^NDX (replication). SPY for signals that need reliable opens.
- **Discovery:** 1990-01-01 → 2012-12-31. **Confirmation:** 2013-01-01 → end. The confirmation data is not inspected until the discovery ranking is saved to `results/exploratory_discovery.json`.
- **Metric:** next-period return minus the same-year mean daily return (bps), per signal occurrence; HAC t (lag 5).
- **Discovery rule:** two-sided test; Benjamini-Hochberg q < 0.10 across all candidates. The sign found in discovery becomes the prediction.
- **Confirmation rule:** same sign, one-sided p < 0.05 on ^GSPC 2013 → end, net of 1.5 bps per trade; and same sign on ^NDX 2013 → end.
- **Candidates (fixed now):**
  - E01–E05: Monday … Friday
  - E06: after ≥ 3 consecutive down closes
  - E07: after ≥ 3 consecutive up closes
  - E08: after a down day (1-day reversal, the P4 US subset)
  - E09: after an up day
  - E10: first trading day of the month
  - E11: last trading day of the month
  - E12: November–April days vs May–October (Halloween)
  - E13: options-expiration Friday (3rd Friday)
  - E14: day after options expiration
  - E15: options-expiration week (Mon–Fri containing the 3rd Friday)
  - E16: after a ≥ 2% down day
  - E17: after a ≥ 2% up day
  - E18: SPY overnight (close → open) after a down day minus after an up day (Boyarchenko et al. asymmetry)
  - E19: SPY open → close after a gap down > 0.5% (gap fill)
  - E20: SPY open → close after a gap up > 0.5%

### A2 (2026-09-25, before any intraday result was computed)

Dukascopy's data feed blocked this connection after ~90 files (timeouts and 503s logged by the
proxy), so the minute-data tests P7–P14 cannot run as specified. Substitute with **Yahoo 60-minute
bars, ≈ 2023-10 → 2026-09** (the post-2022 regime only). Deviations:

| Test | Substitute rule | Deviation |
|---|---|---|
| P7y (for P7) | SPY, QQQ, IWM, DIA: sign(prior close → 15:30) held over the 15:30–16:00 bar | Only the post-2022 subsample exists |
| P8y (for P8) | sign(prior close → 10:30) held over 15:30–16:00 | 10:30 instead of 10:00 (first hourly bar ends 10:30) |
| P9y (for P9) | P7y when abs(signal) > 1.0 × rolling 60-day sd of the signal | — |
| P13y (for P13) | −sign(15:30–16:00 return) × next day's close-to-close return | — |
| P15y (for P15) | 9 USD pairs from Yahoo (EURUSD=X, GBPUSD=X, AUDUSD=X, NZDUSD=X, JPY=X, CHF=X, CAD=X, NOK=X, SEK=X). Long USD from London 08:00 → London 16:00, short USD from London 16:00 → New York 17:00 (DST-aware, hour bars) | Only 2023-12 → 2026-09 (post-paper); Yahoo indicative quotes |
| P10–P12, P14 | NOT RUN (need minute data / GER40 / 02:00 ET bars) | — |

Costs as pre-registered (1.5 bps per index trade; 1.0 bps per FX pair per window). Verdicts use the
post-publication rule only, since no in-paper period exists in this data. Holm family = all primary
tests actually run.

### A3 (2026-09-25, round 2, written before any of these tests was run)

New family **Q** (Holm/BH within Q; also reported pooled with round 1). Same statistics and verdict
rules as the primaries.

| ID | Edge | Data / sample | Rule (exact) | Predicted | Split |
|---|---|---|---|---|---|
| Q1 | Macro-announcement premium (Savor & Wilson 2013; Ai, Bansal & Guo 2024) | ^GSPC 1994 → ; FOMC scheduled decision days from federalreserve.gov (conference calls excluded); Employment Situation days reconstructed with the BLS rule "third Friday after the week containing the 12th" | Return on announcement day (close t−1 → close t) minus the same-year mean daily return; union of FOMC and employment days | + | ≤ 2012 / ≥ 2013 |
| Q2 | MR-06 with a realistic entry | SPY 1993 → | After ≥ 3 down closes, **buy at the next open**, sell at that day's close; metric: return minus same-year mean open→close return | + | ≤ 2012 / ≥ 2013 |
| Q2b | MR-06, next open → close of the following day | SPY 1993 → | Same signal; buy next open, sell at the close one day later; minus 2 × same-year mean daily return | + | ≤ 2012 / ≥ 2013 |
| Q3 | MR-06 with a pre-close signal | SPY/QQQ/IWM/DIA Yahoo 60-min, 2023-10 → | Third down day judged at 15:30 (15:30 price < prior close, after two down closes); enter at the 15:30 price; exit next close; minus same-year mean daily return | + | none |
| Q4 | MR-06 outside equity indices (**mechanism check**) | TLT, IEF, GLD, SLV, USO, FXE, FXY, UUP, BTC-USD, ETH-USD daily | Same rule as E06 (next close-to-close excess) | ≈ 0: the index-product mechanism predicts no effect. Two-sided; a positive result would count **against** the mechanism story | ≤ 2012 / ≥ 2013 |
| Q5 | Crypto time-series momentum (Liu & Tsyvinski 2021) | BTC-USD 2014-09 → , ETH-USD 2017-11 → (Yahoo, 7-day weeks) | Weekly (Mon–Sun): position = sign(prior 1-week return); hold 1 week; 10 bps round-trip cost when the position flips | + | ≤ 2020 / ≥ 2021 |
| Q6 | FX W1 + W4 (lead from round 1) | Dukascopy hourly 9 USD pairs, 2004-01 → 2023-09 (independent of the 2023–26 Yahoo data), **only if the download completes** | Long USD NY 17:00 → 01:00 UTC; short USD London 16:00 → NY 17:00; 2 × 1.0 bps cost | + | 2004–2018 / 2019–2023 |
| Q7 | Original P7–P14 (minute data) | Dukascopy US500 minute 2014 → , **only if the download completes** | As specified in the original table | as original | as original |

For Q7, the round-1 finding that P7y reversed in 2023–26 motivates a secondary two-sided comparison:
P7 on 2014–2021 vs 2022 → (difference in means).

### A4 (2026-09-25, before any minute or FX-hourly data was downloaded or tested)

Dukascopy stayed blocked. Substitute **HistData.com** free 1-minute bars (timestamps are EST with no
daylight-saving adjustment, i.e. fixed UTC−5; converted to America/New_York, Europe/Berlin and
Europe/London as needed):

- **Q7 (P7–P14):** US500 → SPXUSD, US100 → NSXUSD, GER40 → GRXEUR; sample 2014-01 → 2025-12. Rules, costs and splits are unchanged. The 2022 → split, together with the 2023–26 Yahoo result, answers whether momentum flipped to reversal.
- **Q6 (FX W1 + W4):** EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, USDNOK, USDSEK from HistData 1-minute, aggregated to prices at the window boundaries; sample 2004-01 → 2023-09 (splits 2004–2018 / 2019–2023-09). Windows use the minute nearest each boundary. Pairs missing from HistData are dropped and reported.
- **Data check before testing:** for each symbol, verify the daily session break sits at 17:00 America/New_York in both January and July (confirms the time-zone handling).

### A5 (2026-09-25, data-check result and implementation details; written before any Q6 or Q7 result was computed)

**Data-check result.** HistData timestamps are **America/New_York local time with daylight saving**, not the
fixed EST that HistData's documentation (and A4) state. Evidence (winter = Dec–Feb, summer = Jun–Aug; the four
highest-volatility minutes of the day are the same local minutes in both seasons):

| Symbol / years | Winter top minutes (NY) | Summer top minutes (NY) | Reads as |
|---|---|---|---|
| SPXUSD 2014, 2019, 2023 | 08:30, 10:00, 15:59, 09:30 | 08:30, 09:35, 10:00, 15:59 | US data 08:30, cash open 09:30, close 16:00 |
| NSXUSD 2014, 2023 | 09:30–09:35, 10:00, 08:30 | 09:30–09:35, 10:00, 08:30 | same |
| GRXEUR 2014, 2019, 2024 | 03:00, 02:00, 08:30, 10:00 | 03:00, 02:00, 08:30, 10:00 | Xetra open 09:00 Berlin = 03:00 NY in both seasons |
| EURUSD 2004, 2012, 2022; USDJPY 2006, 2021 | 08:30, 10:00 | 08:30, 10:00 | US data releases |
| GBPUSD 2010 | 04:30 | 04:30 | UK data 09:30 London |

With fixed EST, summer events would appear one hour earlier (07:30, 08:30, 14:59). Bars are labelled by
their **start** minute (the 08:30 release is in the bar stamped 08:30). SPXUSD/NSXUSD trade futures hours
(18:00 → 16:15 NY from 2019; 18:00 → 17:15 in 2014), GRXEUR 08:00 → 22:00 Berlin (2014) and nearly 24 h (2025).
The loader (`data_histdata.py`) reads timestamps as America/New_York.

**Implementation details (fixed now):**

- Price at time T = close of the bar starting at T − 1 min; else the open of the bar at T; else the nearest bar edge within 2 min (indices) or 10 min (FX).
- US regular day = weekday with bars at 09:30 and 15:59 (drops holidays and half-days). "Prior close" = 16:00 price of the previous regular day.
- P10: first 5-minute candle = bars 09:30–09:34; doji → no trade; entry at the 09:35 open; stop at the candle's opposite extreme; target 10R; within a bar the stop is checked before the target; a bar that opens beyond a level fills at its open; otherwise exit at the 15:59 bar's close; risk ≤ 0 → no trade. Metric in bps of price as pre-registered; R-multiples reported as a secondary.
- P11: range = bars 09:30–09:59 (≥ 25 bars present); the first bar from 10:00 with high > range high (long) or low < range low (short); fill at the range edge, or at the bar's open if it gapped through; a first breakout bar that crosses both edges → no trade (counted); stop at the opposite edge; exit at the 15:59 price.
- P10 and P11 pool US100 and US500 by date (mean of the instruments trading that day), as in round 1.
- P12: 17:00 and 17:30 Berlin converted to NY time per day; prior 17:30 = previous weekday with a 17:30 price.
- P14: every weekday with prices at 02:00 and 03:00 NY.
- Q6: W1 for date d = NY 17:00 on the previous calendar day → 01:00 UTC on d (Monday's starts at the Sunday open); W4 = London 16:00 → NY 17:00 on d; a pair-day needs both windows; daily P&L = mean over pairs of the USD-signed log returns (long W1, short W4); cost 2 × 1.0 bps per pair-day.
- Family Q for Holm/BH: Q1, Q2, Q2b, Q3, Q5, Q6 and Q7-P7 … Q7-P14 (Q4 stays out: it is a two-sided mechanism check). Also reported pooled with round 1. DSR trial count N = 50 (15 round-1 primaries + 20 exploratory candidates + 6 round-2 tests + Q6 + 8 Q7 tests).
- Post-hoc robustness, reported but not in any family: Q6 with the NY 17:00 boundary moved off the rollover minute (16:55 / 17:10); P7 on US100; break-even costs.

### A6 (2026-09-25, round 3 confirmation tests; written after the round-2 results and **before any of this data was downloaded**)

Round 2 left four leads that were found on data already seen: GER40 close momentum (Q7-P12), the two ORB
variants (Q7-P10, P11), MR-06 with an open entry (Q2) and a clean USD-into-Tokyo window (post hoc, Q6 diagnostics).
Round 3 tests each on data **not yet downloaded or inspected**: earlier years, other instruments, or a later period.
Family **R**: Holm/BH within R. Statistics and costs as before. DSR trial count N = 56.

| ID | Lead | Data (unseen) | Rule (exact) | Predicted |
|---|---|---|---|---|
| R1 | P12 on other European closes | HistData FRXEUR (CAC 40), ETXEUR (Euro Stoxx 50), UKXGBP (FTSE 100), 2014-01 → 2025-12 | CAC and Euro Stoxx: sign(prior 17:30 → 17:00 Paris) held 17:00 → 17:30. FTSE: sign(prior 16:30 → 16:00 London) held 16:00 → 16:30. Pooled by date (mean). Cost 1.5 bps | + |
| R2 | P12 backward | HistData GRXEUR, earliest available year → 2013-12 | P12 rule exactly | + |
| R3 | P11 backward | HistData SPXUSD + NSXUSD, earliest available year → 2013-12 | P11 rule exactly (A5 details) | + |
| R4 | P10 backward | same as R3 | P10 rule exactly (A5 details), bps of price | + |
| R5 | MR-06 open entry (Q2) on other US indices | Yahoo DIA and IWM, 2013-01 → end | Q2 rule: after ≥ 3 down closes buy the next open, sell that close; minus same-year mean open → close return; pooled by date | + |
| R6 | Clean USD-into-Tokyo window | HistData EURUSD, GBPUSD, AUDUSD, NZDUSD, 2024-01 → 2025-12 | Long USD from NY 18:30 (previous evening) → 01:00 UTC; mean over the 4 pairs; cost 1.0 bps per pair-day. USD-quote pairs only, so any leftover bid-rollover artifact works **against** the prediction | + |

Notes fixed now:

- R1 is not independent of P12: the three closes fall in the same clock half-hour as the DAX close and the indices are highly correlated. It tests whether the effect is specific to GER40, not whether it is a separate edge. R2 is the independent test (different years).
- Replication verdict: **REPLICATED** if the sign is as predicted, Holm-adjusted p (within R) < 0.05 and the net mean > 0; **WEAK** if raw one-sided p < 0.05 but it fails Holm or net; otherwise **NOT REPLICATED**.
- Secondary (not in the family): R1 per index; R6 with the 5 USD-base pairs; R5 per ETF; the post-hoc P12 top-tercile rule on R1 and R2 data (terciles of |signal| computed within each sample).

### A7 (2026-09-25, added to family R before any round-3 test was run)

| ID | Lead | Data | Rule (exact) | Predicted |
|---|---|---|---|---|
| R7 | MR-06 with a realistic pre-close entry (the MR-06 card's falsification test 1) | HistData SPXUSD + NSXUSD, 2014-01 → 2025-12. This data was used for Q7, but this rule has not been computed on it | Closes = 16:00 prices of regular days (A5). Signal at 15:55 NY on day t: P(15:55) < close(t−1) and close(t−1) < close(t−2) < close(t−3). Entry at P(15:55); exit at close(t+1). Metric: return minus the same-year mean close-to-close return; pooled by date; cost 1.5 bps | + |

Family R becomes R1–R7 (Holm/BH within R); DSR trial count N = 57. Secondary: share of R7 signal days that are also true three-down-close days.

### A8 (2026-09-25, round 4; written before any of these tests was run or its data examined)

Round 4 tests two untested edges from the plan (FX-02, and CF-02 with the paper's timing, which P16 got
wrong), three published edges that futures-based prop accounts can trade, and one round-2 lead on an
unseen period. Specs were read from the primary sources (V1) before writing this. Family **S**:
Holm/BH within S. DSR trial count N = 64. Statistics as before (HAC t, lag 5; stationary bootstrap CI).

| ID | Edge (source) | Data | Rule (exact) | Predicted | Primary sample (unseen by the paper) |
|---|---|---|---|---|---|
| S1 | FOMC cycle (Cieslak, Morse & Vissing-Jorgensen 2019, *JF* 74(5), V1) | ^GSPC daily; FOMC scheduled decision days (A3 calendar; day 0 = announcement day) | Day index = weekdays relative to the nearest FOMC day, taking days −6…−1 from the next meeting and 0…33 from the last one; beyond 33 dropped. Even weeks: days −1…3, 9…13, 19…23, 29…33. Metric: mean daily return on even-week days minus odd-week days (HAC t from the regression on an even-week dummy) | + | **2017-01 → 2026-09** (after the paper's 1994–2016 sample) |
| S2 | End-of-month Treasury returns (Hartley & Schwarz 2019, V1) | IEF (7–10 yr) adjusted close; ^IRX | Long from the close 3 trading days before the last trading day of the month to the last day's close (the paper's t = 3); excess over the T-bill; one observation per month; cost 2 bps | + | **2019-01 → 2026-08** (after the 1990–2018 sample) |
| S3 | Treasury auction cycle (Lou, Yan & Zhang 2013, *RFS* 26(8), V1) | IEF; 10-year note auction dates (new issues and reopenings) from TreasuryDirect | Per auction: return from close of day 0 (auction day) to close of day +5, **minus** the return from close of day −6 to close of day −1 (short before, long after); cost 4 bps (two round trips) | + | **2013-09 → 2026-09** (after publication; the paper's sample ends 2008) |
| S4 | Month-end fix hedging (Melvin & Prins 2015, *JFM* 22, V1) | HistData 1-min, 9 USD pairs; Yahoo equity indices: ^GSPC (US), ^STOXX50E (EMU; ^GDAXI before 2007-03), ^N225, ^FTSE, ^GSPTSE, ^AXJO, ^SSMI, ^OMX (SE, from 2008-11), OSEBX.OL (NO, from 2013-03), ^NZ50 | Fix day T = last London business day of the month (UK bank holidays excluded). e_c = index return from its last close on or before the previous month's T to its last close before T. Position in currency c vs USD = −sign(e_c − e_US), held 15:00 → 16:00 London on day T; mean across available pairs; cost 1.0 bps per pair | + | **2013-01 → 2025-12** (the paper's sample is 2004-04 → 2012-12); secondary split 2015-02 → (fix-window reform) |
| S5 | Post-fix reversal (Melvin & Prins 2015) | as S4 | Position = +sign(e_c − e_US), held 16:00 London on T → 12:00 London the next weekday | + | 2013-01 → 2025-12 |
| S6 | Rebalancing, Calendar signal (Harvey, Mazzoleni & Melone 2025, NBER w33554, V1) | SPY and IEF adjusted closes | w_t = equity weight of a 60/40 portfolio reset to 0.60 at each month's last trading-day close and drifted daily by SPY and IEF returns; signal_t = w_t − 0.60. For each day t in the **last 5 trading days of the month**: P&L(t+1) = −sign(signal_t) × (R_SPY − R_IEF)(t+1); cost 1.0 bps per day | + | Full 2002-08 → 2026-09 (the paper is 2025; only 2023-03-18 → is outside its sample, reported separately) |
| S7 | Bond reversal after three down days (round-2 lead MR-07; exploratory in Q4) | FRED DGS10, 1962-01 → 2001-12 (before TLT/IEF existed; not yet examined) | Daily bond return ≈ −D·Δy + y/252, with D = modified duration of a 10-year par bond at the prior day's yield. After ≥ 3 consecutive negative returns: next-day return minus the same-year mean daily return; cost 0.5 bps | + | 1962–2001 (whole sample unseen); split 1962–1989 / 1990–2001 |

Verdicts:

- **CONFIRMED:** predicted sign in the primary sample, Holm p (within S) < 0.05, net mean > 0.
- **WEAK:** raw one-sided p < 0.05 in the primary sample, but it fails Holm or net.
- **NOT CONFIRMED:** otherwise.
- The in-paper period is reported as an implementation check (does it reproduce the paper's sign and rough size?). It is not part of the verdict, except for S6, whose primary sample includes it.

Secondary, not in the family:

- S1: 1994–2016 and 2004–2016 (Uppal's claim, V3: "weakening as early as 2004"); trading version (long US500 on even-week days only, 1.5 bps per switch).
- S2: TLT; IEF 2002-08 → 2018.
- S3: 5-year note auctions; IEF 2002-08 → 2008; excluding events whose windows touch the last 3 trading days of a month (overlap with S2).
- S4: per pair; 2004–2012 replication.
- S6: SPY-only version (prop CFD accounts rarely offer bonds).
- S7: TLT 2002 → as a comparison.

**Implementability I1 (not a hypothesis test):** MR-06 (R7 rule, US500, HistData 2014–25), prop pass rates with **volatility-scaled size** (notional = min(2, 1% ÷ 20-day realized daily vol) × base leverage) vs fixed size at the same average notional, same bootstrap and rules as §11 of the report.

### A9 (2026-09-25, round 5; written before any of this data was downloaded or examined)

**Scope change from the user:** no Treasury strategies. CF-07 stays in the evidence record but is removed
from the build list and from prop books. Round 5 searches for edges only in instruments a CFD prop account
offers: equity indices, gold, silver, WTI, Brent, FX majors and crosses, BTC and ETH.

**Data (new):** HistData 1-minute bars for XAUUSD, XAGUSD, WTIUSD, BCOUSD, JPXJPY (Nikkei 225), AUXAUD
(ASX 200), HKXHKD (Hang Seng), EURJPY, GBPJPY and EURGBP, plus 2010–2013 for UKXGBP and FRXEUR; Binance
BTCUSDT and ETHUSDT 30-minute klines (2017-08 →). Each HistData symbol gets the A5 time-zone check before
any test. Bid-only rule (A5/§8): for FX, metals and energy no window may start or end between 16:00 and
19:00 New York.

#### Family T: literature tests (Holm/BH within T; DSR N = 64 + 8 + scan candidates)

| ID | Edge (source, level) | Data | Rule (exact) | Pred. | Primary sample |
|---|---|---|---|---|---|
| T1 | Commodity intraday momentum (Baltussen, Da, Lammers & Martens 2021, *JFE*, V1; commodity panel t = 3.0) | XAUUSD, XAGUSD, WTIUSD | Sessions from the paper's Table 1 (New York time): gold 08:20–13:30, silver 08:25–13:25, crude 09:00–14:30. sign(prior session close → close − 30 min) × (close − 30 min → close); mean across the three by date; cost 2.5 / 5 / 4 bps | + | **2020-06 → 2025-12** (after the paper's sample, which ends 2020-05); 2011 → 2020-05 reported |
| T2 | Crude-oil first → last half-hour (Wen, Gong, Ma & Xu 2021, *Economic Modelling*, V2) | WTIUSD | sign(prior 16:00 → 10:00 NY) × (15:30 → 16:00 NY); cost 4 bps | + | **2019-01 → 2025-12** (the paper: USO 2006–2018) |
| T3 | EIA-day third half-hour (Wen, Indriawan, Lien & Xu 2023, *Energy Journal*, V2) | WTIUSD | Regular Wednesday EIA releases only (weeks with no US federal holiday Mon–Wed): sign(10:30 → 11:00) × (15:30 → 16:00 NY); cost 4 bps | + | **2019-01 → 2025-12** |
| T4 | Bitcoin intraday momentum (Shen, Urquhart & Wang 2022, *Financial Review*, V1) | BTCUSDT | sign(17:00 NY previous day → 09:30 NY) × (16:30 → 17:00 NY); cost 5 bps. The paper reports a break-even cost of only 3 bps | + | **2021-01 → 2026-08** (the paper: 2013–2020) |
| T5 | Bitcoin 22:00–24:00 UTC (Padyšák & Vojtko 2021, SSRN working paper, V2 via QuantPedia) | BTCUSDT | Long 22:00 → 00:00 UTC daily; cost 5 bps | + | **2022-01 → 2026-08** (the paper: 2015–2021) |
| T6 | Bitcoin Monday effect (Caporale & Plastun 2019, *FRL* 31, V2) | BTCUSDT | Monday (UTC day) return minus the mean return of the other six days (HAC t on the Monday-dummy difference) | + | **2018-01 → 2026-08** (the paper: to 2017) |
| T7 | Asian index intraday momentum (Baltussen et al. 2021, V1) | JPXJPY, AUXAUD | Nikkei 09:00–15:00 Tokyo (15:30 from 2024-11-05, the TSE's longer session); ASX 10:00–16:00 Sydney. Rule as T1; mean across both; cost 3 bps | + | **2020-06 → 2025-12** |
| T8 | Crypto-weekend → Monday equity (2025, *FRL* 86, V2; its sample is 2021-01 → 2025-06) | BTCUSDT, SPXUSD | **Tradeability test in the paper's own period:** if BTC's Friday 16:00 NY → Sunday 18:00 NY return is < 0, short US500 from the Sunday 18:00 NY futures reopen to Monday's 16:00 close (the paper's asymmetry: only negative weekends predict); otherwise flat; cost 1.5 bps | + | 2021-01 → 2025-06 (flagged: in-paper period); 2018–2020 reported |

Verdicts as in A8: **CONFIRMED** = predicted sign, Holm p (within T) < 0.05 and net > 0 in the primary
sample; **WEAK** = raw p < 0.05 only; otherwise **NOT CONFIRMED**. T8 can only be "tradeable in-sample"
or not.

#### Family X: systematic discovery/confirmation scan

**Why:** to find edges that no paper in the plan covers, without fooling ourselves. It uses the A1
design, which found MR-06, applied to 24 prop-tradeable instruments.

- **Instruments and costs (round trip, bps):** SPXUSD 1.5, NSXUSD 1.5, GRXEUR 1.5, UKXGBP 2, FRXEUR 2, JPXJPY 3, AUXAUD 3, HKXHKD 4, XAUUSD 2.5, XAGUSD 5, WTIUSD 4, BCOUSD 4, EURUSD 1, GBPUSD 1.5, USDJPY 1, AUDUSD 1.5, USDCAD 1.5, USDCHF 1.5, NZDUSD 2, EURJPY 2, GBPJPY 3, EURGBP 2, BTCUSDT 5, ETHUSDT 8.
- **Periods:** HistData instruments: discovery **2011-01 → 2017-12**, confirmation **2018-01 → 2025-12**. Crypto: discovery 2018-01 → 2021-12, confirmation 2022-01 → 2026-08. Confirmation data is not examined until the discovery table is saved to `results/scan_discovery.json` and committed.
- **Reference clocks:** indices use exchange local time (US: New York; GER40 Berlin; FRA40 Paris; UK100 London; JP225 Tokyo; AUS200 Sydney; HK50 Hong Kong). FX, metals and energy use New York time. Crypto uses UTC.
- **Daily close:** cash close (US 16:00; GER40/FRA40 17:30; UK100 16:30; JP225 15:00, 15:30 from 2024-11-05; AUS200 16:00; HK50 16:00). FX, metals and energy use 16:00 NY (before the rollover). Crypto uses 00:00 UTC.
- **Candidates per instrument:**
  - **Hour-of-day:** the return over each local clock hour [h:00, h+1:00) with data on ≥ 80% of weekdays in discovery; FX/metals/energy exclude the hours starting 16:00, 17:00 and 18:00 NY.
  - **Day-of-week:** 5 (crypto 7).
  - After **≥ 3 down / ≥ 3 up** daily closes (next day).
  - **IBS** < 0.2 / > 0.8 (next day).
  - Close at a **20-day high / low** (next day).
- **Metric:** per-day return minus the same-year mean of that return (hour-of-day: the same-year mean of that hour across all hours; daily signals: the same-year mean daily return), in bps.
- **Discovery:** two-sided HAC t (lag 5); **BH q < 0.10** across all candidates. The discovery sign becomes the prediction.
- **Confirmation (CONFIRMED):** same sign; one-sided p < 0.05 after **Holm across all discovered candidates**; net raw P&L (sign × raw return − cost) > 0.
- **Disclosure of previously examined windows** (their mean returns were seen in rounds 2–4, so discoveries there are flagged): US500 02:00–03:00 and 15:30–16:00 NY; GER40 17:00–17:30 Berlin; UK100 16:00–16:30 London; FRA40 17:00–17:30 Paris; FX multi-hour windows London 16:00 → NY 16:45 and NY 18:30 → 01:00 UTC; the MR-06 streak rule on US500/US100.

#### Implementability (not tests)

- **I2:** MR-06 with a pre-close entry on JP225 (14:55 Tokyo; 15:25 from 2024-11-05) and AUS200 (15:55 Sydney). This is an execution check only: round 1 already saw the daily-data result.
- **I3:** Prop books without Treasuries: volatility-scaled MR-06, plus pre-holiday, plus anything CONFIRMED in T or X. Two-step 10%/5%, one-step 10% (6% trailing), and futures 50K presets, each with a zero-edge base rate.

### A10 (2026-09-25, written after round 5 and before this test was run; none of these indices has been tested before)

**W1: does MR-06 generalise?** The E06 rule (next close-to-close return minus the same-year mean daily
return, after ≥ 3 consecutive down closes) on 15 indices not used in any earlier round: ^IBEX, ^AEX,
FTSEMIB.MI, ^BFX, ^ATX, ^KS11, ^TWII, ^BSESN, ^BVSP, ^MXX, ^STI, ^JKSE, ^KLSE, ^TA125.TA, ^MERV
(Yahoo daily). Pooled by date (mean of the indices signalling that day).

- **Sample:** 2000-01 → 2026-09 (the index-product era).
- **Cost:** 1.5 bps.
- **Prediction:** + (index-product liquidity provision; Baltussen, van Bekkum & Da 2019). One-sided test; the two-sided p is also reported, because round 1 found the effect absent in DAX, FTSE, CAC, SMI, TSX and HSI.
- **Verdict:** CONFIRMED if the one-sided p < 0.05 and net > 0; otherwise NOT CONFIRMED.
- **Secondary:**
  - per index;
  - developed (IBEX, AEX, FTSE MIB, BFX, ATX, TA125, STI) vs emerging (the rest);
  - 2000–2012 vs 2013 →;
  - US broad indices ^NYA, ^MID, ^XAX (correlated with the S&P 500, so they don't count as independent).

### A11 (2026-09-25, written before any of these tests was run; the rule has never been computed on this data)

**Family N: noise-area intraday momentum** (Zarattini, Aziz & Barbon 2025, SSRN 4824172, V1; spec from the
IM-04 card). 30-minute decision grid; 100% notional; flat at the session close; cost per entry
(round trip) as in A9. For each mark HH:MM:

- σ(t, HH:MM) = mean over the prior 14 sessions of |P(HH:MM)/Open − 1|.
- UB = max(Open, prior close) × (1 + σ); LB = min(Open, prior close) × (1 − σ).
- At each mark: P > UB → long; P < LB → short. A cross of the opposite band flips the position.
- Metric: daily P&L in bps of notional; one-sided test; predicted +.

| ID | Version | Data | Session (local), marks | Cost |
|---|---|---|---|---|
| N1 | Conservative (the paper's 0.61-Sharpe version: flip at the opposite band) | SPXUSD 2014-01 → 2025-12 | 09:30–16:00 NY, marks 10:00 … 15:30 | 1.5 |
| N2 | Paper's best exit: trailing stop at max(UB, TWAP) for longs, min(LB, TWAP) for shorts, checked on marks; re-entry allowed. **TWAP replaces VWAP** (HistData has no volume) | SPXUSD | as N1 | 1.5 |
| N3 | N1 unchanged | NSXUSD | as N1 | 1.5 |
| N4 | N1 unchanged | GRXEUR | 09:00–17:30 Berlin, marks 09:30 … 17:00 | 1.5 |
| N5 | N1 unchanged | XAUUSD | 08:20–13:30 NY (COMEX), marks 09:00 … 13:00 | 2.5 |

- **Splits:** the paper's period (2014 → 2024-04) and after it (2024-05 → 2025-12, about 20 months, low power).
- **Verdict:** CONFIRMED = Holm p (within N) < 0.05 on 2014–2025, net > 0, and the post-paper mean > 0; WEAK = raw p < 0.05 only.

### A12 (2026-09-26, round 6: decision analysis for prop accounts; written before it was run)

**This is not a test for new edges.** It asks how to play the two surviving books inside prop rules to
maximise money, using the full lifecycle: challenge fee, pass probability, time, funded-stage payouts and
breach. Theory motivating it:

- **Timid play is optimal in a favourable game** when the goal is to reach a target before ruin with no deadline (Dubins & Savage 1965; Browne 1997). Smaller exposure raises the pass probability but costs time.
- **CPPI** keeps exposure proportional to the cushion above a floor, so the floor is approached only asymptotically (Black & Jones 1987; Black & Perold 1992).

**Books** (2014–2025 daily P&L with intraday paths, from rounds 3–5):

- **B1:** MR-06 US500, volatility-scaled, 15:55 entry.
- **B2:** noise-area US100, the pre-registered N3 rule.
- **B3:** the N3 TWAP-stop variant (post hoc; labelled as such).

Each book has a **zero-edge twin** with its mean daily P&L removed. The twin shows how much of the value
comes from the prop structure (the firm absorbs losses beyond the limits) rather than from the edge.

**Sizing policies:**

- **Fixed exposure L:** B1 {0.5, 1, 1.5, 2, 3}; B2/B3 {1, 2, 3, 4}.
- **CPPI:** exposure = min(cap, k × cushion), where cushion = equity − today's loss floor as a fraction of the initial balance. k ∈ {10, 20, 40}; cap: B1 {2, 3}, B2/B3 {3, 4}.

**Rule sets** (propsim presets, placeholder fees and terms):

- **two_step_10_5:** fee 500, 80% split, fee refunded on the first payout.
- **one_step_10_trailing:** fee 500.
- **futures_50k_eod_trailing:** fee 150, 90% split, 50% consistency rule.
- For all three: funded stage 365 days, payout requests every 14 days, EA daily guard 3% (two-step) or 2% (others).

**Simulation:** stationary bootstrap, mean block 5 days, 1,500 runs per cell, seed 7.

**Metrics:**

- P(pass); median days to pass; P(≥ 1 payout).
- Mean payouts; **EV per attempt** = payouts + refund − fee.
- **EV per account-month** = EV ÷ mean total months (challenge + funded). This is the primary ranking metric, because accounts can run in parallel and time is the binding constraint.
- **Edge value** = EV(book) − EV(zero-edge twin) under the same policy.
- Sensitivity: payout reliability 0.7 (counterparty risk).

**Decision rule, fixed now:** for each book and rule set, recommend the policy with the highest EV per
account-month among policies whose **edge value is positive**, i.e. whose EV comes from the edge and not
only from the prop option.

### A13 (2026-09-26, written while A12 was running and before any A13 cell was computed)

**Different sizing in the challenge and the funded stage.** Once funded, the firm absorbs losses beyond
the limit, so the trader's payoff is option-like. Higher exposure may raise expected payouts even though
it lowers the challenge pass rate.

- **Grid:** for each book (B1, B2; B3 labelled post hoc) and rule set, the challenge policy is the one A12's decision rule recommends. The funded policy is one of:
  - the same policy;
  - fixed 1×, 2×, 3× (and 4× for B2/B3);
  - CPPI k = 40 with cap 4×.
- **Metrics:** as in A12, each against the zero-edge twin under the same pair of policies.
- **Decision rule:** the pair with the highest EV per account-month whose edge value is positive.
- **Caveat recorded now:** real firms limit this with consistency rules, payout caps and minimum trading days, and the presets only partly model them. Treat funded-stage aggressiveness as a result to check against each firm's actual terms, not as a recommendation by itself.

**A12 correction (2026-09-26, found before any A12 result was reported):** the first A12 run averaged
only over *decided* runs (passed or breached within the 2,520-day bootstrap window). Slow policies (CPPI,
low exposure) leave many runs undecided, so this inflated their pass rates. It even produced a 100% pass
rate for a zero-edge twin, which is impossible for a zero-drift account. The faithful implementation of
the pre-registered metrics counts **every** run: an undecided challenge is a failure that used the whole
window. A12 and A13 are re-run on that basis, and the undecided share is reported. The earlier prop
scripts (rounds 3–5) used the same decided-only filter; their fixed-exposure books are re-checked in the report.

### A14 (2026-09-26, round 7: a true holdout and a second data feed; written before any 2026 HistData file or any Dukascopy US100 file was downloaded)

**Why:** every HistData test so far ends on 2025-12-31 (the code reads `range(…, 2026)`), and HistData now
serves monthly 1-minute files for 2026-01 → 2026-09. That is the first data none of the ~730 trials has
touched. A second, independent feed checks that N3 is not a HistData artefact (bid-only quotes, gaps).

**Holdout data:** HistData 2026 files, from January to the last day served at download (about 2026-09-25).
The 2025 files are loaded only as warm-up for look-backs and prior closes. Only 2026 days are scored.

**Frozen code.** The only changes allowed are:
- year-range parameters (with defaults that reproduce the earlier runs);
- a monthly downloader for the current year;
- an optional pre-built session table for `run_noise_area.run()`, used for the second feed.

| ID | Rule (code as run earlier) | In-sample result |
|---|---|---|
| **H1 (primary)** | N3, noise-area US100 | CONFIRMED: +3.02 bps/day net, t 2.54, n 2,767 (2014–25) |
| H2 | N3 TWAP-stop variant (B3, post hoc) | +3.06 bps/day, t 3.50 |
| H3 | N1, N2, N4, N5 | NOT CONFIRMED (calibration: these should stay ≈ 0) |
| H4 | R7, MR-06 with a 15:55 entry, US500 + US100 pooled | WEAK: +15.9 bps/trade, t 1.89. **Not a clean holdout:** 2026 daily index closes entered the round-6 1990–2026 weekend diagnostic in aggregate |
| H5 | Q7-P10 first-candle ORB; Q7-P11 30-minute ORB (US100 + US500) | PARTIAL: +2.57 (t 3.16); +2.47 (t 2.39) |
| H6 | Q7-P12 GER40 close momentum; R1 CAC/Euro Stoxx/FTSE closes | P12 +2.07 (t 4.85) but not replicated in 2000–13 (R2); R1 WEAK +1.01 (t 2.99). Euro Stoxx is dropped if HistData serves no 2026 file (its data stops in 2019) |
| H7 | T7, Asian index intraday momentum | WEAK: +0.75 (t 2.28) |
| H8 | the 18 non-crypto scan candidates (A9), signed as discovered | 3 WEAK, 15 NOT CONFIRMED. The two ETH candidates are excluded: their confirmation window already ran to 2026-08 |

**Statistics per rule (2026 days only):**
- n, mean (net for rules with a cost; for H8, the signed excess as in A9), HAC t (lag 5) and one-sided p.
- **Prediction check:** z = (m_H − m_IS) / √(SE_H² + SE_IS²), where H is the holdout and IS the in-sample result.
- **Bayes factor** for "edge = in-sample estimate" against "edge = 0": BF = φ((m_H − m_IS)/SE_H) / φ(m_H/SE_H).
- **Pooled estimate:** the precision-weighted mean of IS and H.

**Power, fixed now from the in-sample SD:**
- N3's daily SD is 65.7 bps. With about 180 holdout days, SE_H ≈ 4.9 bps.
- If the true edge equals the in-sample +3.0, then P(m_H > 0) ≈ 73% and P(one-sided p < 0.05) ≈ 15%.
- If the true edge is 0, then P(m_H > 0) = 50%, and the rejection rule below fires with probability ≈ 14%.

**Nine months cannot confirm N3.** The holdout updates the estimate and can catch a collapse; it cannot
promote a rule. No rule is promoted on holdout evidence alone.

**Decision rule for H1 (and reported the same way for H2–H7):**
- **REJECTED** if z < −1.645.
- **CONSISTENT** if m_H > 0 and z ≥ −1.645.
- **INCONCLUSIVE** otherwise.

**Pipeline calibration:**
- Compare the mean holdout t-statistic of the in-sample CONFIRMED/WEAK/PARTIAL rules (H1, H2, H4–H7 and the H8 WEAKs) with that of the NOT CONFIRMED rules (H3 and the other H8 candidates).
- The prediction is that, if the pipeline's WEAK results are mostly noise, both groups average t ≈ 0.

**X1: second data feed for N3**
- **Data:** Dukascopy `USATECHIDXUSD` 1-minute BID candles. Timestamps are UTC, converted to New York local time, and bars are labelled by their start minute as in A5.
- **Test:** N3 code, 1.5 bps cost, 2014-01 → 2025-12.
- **CONFIRMED on the second feed** if the net mean > 0 and the one-sided HAC p < 0.05. Otherwise NOT CONFIRMED on the second feed.
- **Also reported:** the correlation of daily P&L with the HistData series on common dates; the share of days that trade on both feeds; the 2026 holdout on this feed (secondary to H1).
- **Data check, done and reported before the result:** coverage of full 09:30–16:00 sessions, and date overlap with HistData.

Trial count: H1–H8 and X1 re-test existing rules and add no new trials to the DSR count (N stays 731).

**A14 data-check addendum (2026-09-26, found by the holdout coverage check, after the holdout run):**
HistData's clock follows the **European** daylight-saving calendar. File time = London time − 5 h all
year: New York local time outside the US/EU gap weeks, but New York − 1 h during them (second Sunday of
March → last Sunday of March; last Sunday of October → first Sunday of November).
- A4/A5 compared January with July, so the check could not see the gap weeks.
- **Effect on earlier tests:** US-index rules that need the 09:30 or 15:55/15:59 bars (N-family, R7, P10, P11) lose those days, because the bars fall inside the file's break. They are not mis-timed.
- Hour-bucket and FX rules, and the Berlin/Paris/Tokyo/Sydney conversions made through NY time (N4, P12, R1, T7, the scan), are one hour off on those ~20 days a year. That blurs a signal; it does not create one.
- **From A15 on,** new HistData tests convert through London time: UTC = (file time + 5 h) read as Europe/London local time.

### A15 (2026-09-26, round 7 family G: written before any of this data was downloaded or examined; ^GSPC daily was loaded once to check the loader works — row count and dates only)

**Scope:** the register's never-tested families that fit prop instruments, plus literature leads not in
the register.

**Dropped before testing, with reasons:**
- **Pre-holiday premium:** faded to nothing out of sample (Ko 2021: t = 0.9 for the S&P 500, 1983–2019).
- **FX carry (CA-01/02, TF-05):** needs multi-week holding. That is banned on FTMO Standard funded accounts, and swap mark-ups eat the premium.
- **IX-03, TF-03:** practitioner lore with no testable single specification.
- **SR-02:** it is the mirror image of N1, which has already been tested.
- **Crypto cash-and-carry (Schmeling, Schrimpf & Todorov 2023, BIS WP 1087):** an arbitrage between spot and futures that a CFD prop account cannot hold. Only its directional crowding signal (G9) is tested.

**Family G** (Holm/BH within G; DSR N = 731 + 11 = 742; one-sided in the predicted direction; HAC lag 5 for daily, 3 for monthly and 2 for weekly series):

| ID | Hypothesis (reference) | Data | Rule and metric | Pred. | Primary period |
|---|---|---|---|---|---|
| G1 | Halloween: winter beats summer (Bouman & Jacobsen 2002 AER; Jacobsen & Zhang 2018) | SPY adj. close, ^IRX | Daily excess return over T-bill, Nov–Apr minus May–Oct (difference of means, HAC SE per group) | + | 2002-11 → 2026-08 (after publication) |
| G2 | Options-expiration week is strong (Stivers & Sun 2013 JBF) | SPY, ^IRX | Weekly Fri→Fri excess return (Thursday if Friday is a holiday). Week ending on the third Friday minus all other weeks | + | 2011-01 → 2026-08 (after their sample) |
| G3 | The week after expiration is weak (same) | SPY, ^IRX | Week after the expiration week minus the other non-expiration weeks | − | as G2 |
| G4 | Index reversal pays more when VIX is high (Nagel 2012 RFS mechanism) | ^GSPC, ^VIX | MR-06 daily trades (3 down closes; close t → close t+1). Mean trade return when VIX(t) > median VIX over t−252…t−1, minus when not | + | 1990-01 → 2026-08; 2011 → reported |
| G5 | Volatility-managed index exposure (Moreira & Muir 2017 JF) | SPY, ^IRX | Monthly weight c / RV(t−1), where RV is the prior month's realised variance of daily excess returns, capped at 2. c matches the unmanaged volatility over 1993–2015 and is then fixed. Alpha of the managed series regressed on the unmanaged, net of 1 bp per unit turnover | + | 2016-01 → 2026-08 (after their sample) |
| G6 | Time-series momentum across prop instruments (Moskowitz, Ooi & Pedersen 2012) | ETFs: SPY QQQ DIA IWM EWG EWU EWJ GLD SLV USO FXE FXY FXB FXA FXC FXF; BTC-USD from 2015 | Month-end sign of the 12-month excess return. Weight 0.40 / annualised EWMA volatility (centre of mass 60 days) per asset, equally weighted across available assets, held one month. Mean monthly return net of 2 bps per unit turnover | + | 2012-01 → 2026-08 (after publication); 2007–11 reported |
| G7 | Strong last-hour index moves reverse the next day (Baltussen, Da, Lammers & Martens 2021 JFE) | HistData SPXUSD, NSXUSD | r = P(16:00)/P(15:00) − 1 (NY). If \|r\| ≥ the 67th percentile of the prior 250 days, go −sign(r) at P(16:00) and exit at the next day's P(16:00). Pooled by date; 1.5 bps | + | 2014-01 → 2025-12; 2026 holdout reported |
| G8 | Asian-range breakout at the London open (practitioner staple, VB-02) | HistData EURUSD, GBPUSD | Range = high/low of 00:00–06:59 London. From 07:00 to 11:59, the first touch of the high (low) buys (sells) at the level; stop at the other side of the range; exit at 16:00 London. Skip the day if both sides are touched in one bar. Pooled by date; 1.0 / 1.5 bps | + | 2014-01 → 2025-12; 2026 holdout |
| G9 | Crowded crypto leverage predicts lower returns (Schmeling et al. 2023 mechanism) | Binance BTCUSDT/ETHUSDT perpetual funding; spot daily closes (00:00 UTC) | Signal at the day-t close = 7-day mean funding. Long day t+1 if the signal ≤ its trailing 365-day median, else short. Mean daily return, pooled by date; 5 bps per position change | + | 2020-09 → 2026-08 |
| G10 | Williams volatility breakout (practitioner, VB-03) | HistData SPXUSD, NSXUSD, GRXEUR | Buy stop at open + 0.5 × the prior session's range; sell stop at open − 0.5 × range. First trigger only; exit at the close. Sessions 09:30–16:00 NY and 09:00–17:30 Berlin. Pooled by date; 1.5 bps | + | 2014-01 → 2025-12; 2026 holdout |
| G11 | NR7 breakout (Crabel 1990, VB-01) | same as G10 | If the prior session's range is the narrowest of the last 7, buy stop at the prior high and sell stop at the prior low. First trigger only; exit at the close. Pooled by date; 1.5 bps | + | as G10 |

**Verdicts:**
- **CONFIRMED:** Holm p (within G) < 0.05 in the predicted direction; net > 0 for tradeable rules; and positive in the reported secondary split (G1, G4, G6: the other period; G7, G8, G10, G11: the 2026 holdout sign).
- **WEAK:** raw p < 0.05 only.
- **NOT CONFIRMED:** anything else.

**Reporting and implementation notes:**
- Every rule is also reported per instrument and per year.
- Stop-entry rules fill at the stop level: an optimistic assumption on bid-only data, disclosed.
- G4 changes no MR-06 rule. It only informs sizing.

**A15 amendment (2026-09-26, before any G result was computed):** Binance publishes USDT-M funding files
from 2020-01, not 2019-09. G9's 365-day median therefore first exists in 2021-01, and G9's primary period
becomes **2021-01 → 2026-08**. The rule is unchanged.

### A16 (2026-09-26, round 7: prop lifecycle on published firm terms; written after family G's verdicts and before any A16 cell or H1 result was computed)

**Correction to A12, found while collecting firm terms:** Topstep auto-liquidates every position at
3:10 PM CT. No overnight or weekend holds are allowed, and the other large futures firms have the same
rule. MR-06 holds overnight, so it cannot run at such a firm. A12's `futures_50k_eod_trailing` results for
B1 describe a trade those firms do not allow. Only intraday books are simulated on Topstep.

**Rule sets** (presets written 2026-09-26 from the firms' published terms; sources in each preset's `_note`):

| Preset | Account types | Books allowed |
|---|---|---|
| `ftmo_2step_100k` | Standard (no weekend holds and no trades within ±2 minutes of high-impact news once funded) | B1s, B2n, B5s |
| `ftmo_2step_100k` | Swing (both allowed; 1:30 leverage) | B1, B2, B4, B5 |
| `ftmo_1step_100k` | Standard only | B1s, B2n, B5s |
| `topstep_50k` | intraday only | B2 |

The EA daily guard is 3% on FTMO 2-Step and 2% on the others, with 0.25% slippage.

**Books** (2014–2025 daily P&L with intraday paths):

- **B1:** MR-06, as A12.
- **B1s:** B1 without trades whose holding spans a market closure longer than overnight (weekends and holidays: exit date − entry date > 1 calendar day).
- **B2:** N3, as A12.
- **B2n:** N3 with no action at a mark that falls on high-impact news. The position is carried through such marks:
  - the 10:00 mark on ISM days (first and third business days of the month);
  - the 14:00 and 14:30 marks on FOMC statement days;
  - the 14:00 mark 21 days after each FOMC statement (minutes).
- **B4:** G6 time-series momentum as daily P&L.
  - Weights are fixed at each month end.
  - The intraday low is the sum of each position's worst excursion against the prior close. This is conservative: every asset hits its worst point at once.
  - CFD financing mark-up: 2%/yr on gross notional (central case), with 0% and 4% sensitivities.
- **B5:** B1 + B2 + B4, each scaled to 0.5% daily P&L volatility over 2014–2025 (all weekdays).
- **B5s:** B1s + B2n scaled the same way.

**Policies, metrics and decision rule:** as A12 and A13.
- Fixed L: {0.5, 1, 1.5, 2, 3} for B1/B1s/B4/B5/B5s and {1, 2, 3, 4} for B2/B2n.
- CPPI k ∈ {10, 20, 40}, capped at {2, 3} and {3, 4} respectively.
- The funded stage uses the same policy.
- Every run counts; 1,500 runs per cell; seed 7; each result against its zero-edge twin.
- Recommend the policy with the highest EV per account-month among those with positive edge value.

### A17 (2026-09-26, family H; written before this data was downloaded)

| ID | Hypothesis | Data | Rule and metric | Pred. | Period |
|---|---|---|---|---|---|
| H1 | Cross-sectional momentum across equity indices (Asness, Moskowitz & Pedersen 2013 JF; Chan, Hameed & Tong 2000 JFQA) | Yahoo daily closes: ^GSPC ^NDX ^DJI ^RUT ^GDAXI ^FTSE ^FCHI ^STOXX50E ^N225 ^HSI ^AXJO ^IBEX ^SSMI ^AEX (local currency, price indices) | At each month end, rank on the 12-month return skipping the last month. Long the top 3, short the bottom 3, each leg weighted 1 / (60-day volatility) and normalised to 1 per leg. Held one month. Mean monthly return net of 2 bps per unit turnover and a 2%/yr mark-up on gross notional | + | 2013-01 → 2026-08 (after AMP 2013); 2000–12 reported |

DSR N = 743. CONFIRMED needs raw p < 0.05, net > 0, and a positive 2000–12 mean.

### A18 (2026-09-26, family G extension, intraday versions for futures firms; written before any open-to-close result conditional on these signals was computed)

Futures prop firms require every position flat before the daily close (A16). These tests ask whether
the index reversal and gap effects exist **inside the regular session**, where such accounts can trade.

| ID | Hypothesis | Data | Rule and metric | Pred. | Period |
|---|---|---|---|---|---|
| G12 | MR-06 intraday: the reversal after 3 down closes continues within the next session | HistData SPXUSD + NSXUSD (corrected clock); SPY daily open/close | Signal: close(t) < close(t−1) < close(t−2) < close(t−3), using 16:00 closes. Long at P(09:30, t+1), exit at P(16:00, t+1). Metric: trade return minus the same-year mean open-to-close return. Pooled by date; 1.5 bps | + | 2014-01 → 2025-12; 2026 holdout; SPY 1993-02 → 2026-08 reported (secondary) |
| G13 | Opening-gap fade: large overnight gaps partly reverse intraday (Berkman, Koch, Tuttle & Zhang 2012 mechanism, index level) | same | gap = P(09:30)/close(t−1) − 1. If \|gap\| ≥ the 20-day mean \|gap\|, trade −sign(gap) from P(09:30) to P(16:00). Pooled by date; 1.5 bps | + | as G12 |

- **Verdict rules:** as A15, with Holm across G1–G13; DSR N = 745.
- **Secondary requirement:** positive 2026 holdout (net) and a positive SPY 1993–2026 mean.
- **Diagnostic, not a test:** MR-06's next-day return split into overnight (16:00 → 09:30) and intraday (09:30 → 16:00) parts.

**Implementability I3 (not a test):** N3 sized as the paper sizes it: exposure = min(4, 2% ÷ the 14-day
realised volatility of daily US100 close-to-close returns), rescaled to the same mean exposure as N3.
Compare Sharpe and the prop metrics with flat sizing on 2014–2025, plus the 2026 holdout.

**A16 addendum (2026-09-26, after G12's verdict (WEAK) and before these cells were computed; labelled post hoc):**

**Books:**
- **B6:** G12's intraday MR-06 on US500 only (as B1). Long from P(09:30) to P(16:00) on the session after three down 16:00 closes; raw return net of 1.5 bps, with the intraday path from minute bars.
- **B7:** B2 + B6, each scaled to 0.5% daily volatility.

**Where they run:** Topstep 50K (both books) and FTMO 2-Step Standard (B6). Both books are flat overnight, and their entries and exits (09:30, 16:00) are not news times. Same policies and decision rule as A16. B6 and B7 use B1's fixed and CPPI grid.

### A19 (2026-09-26, family H, single-stock CFDs; written before any event list or stock price for this universe was downloaded; only Apple's EDGAR filing index was fetched, to check access)

FTMO and other CFD prop firms list large US stocks as CFDs. The earnings-announcement premium is one of
the best-documented stock-level effects:
- Frazzini & Lamont (2007): the premium is concentrated around the announcement.
- Barber, De George, Lehavy & Trueman (2013, JFE): more than 11%/yr in announcement months, across 46 countries.
- Savor & Wilson (2016, JF): announcing firms earn a premium for bearing systematic risk.

| ID | Hypothesis | Data | Rule and metric | Pred. | Period |
|---|---|---|---|---|---|
| H2 | Earnings-announcement premium in large US stocks | **Universe fixed ex ante:** the 19 largest US stocks at end-2013, excluding Berkshire (weekend releases). AAPL, XOM, GOOG (Google Inc. and Alphabet CIKs), MSFT, GE, JNJ, WMT, CVX, WFC, JPM, PG, PFE, IBM, T, KO, AMZN, ORCL, BAC, VZ. Events: SEC EDGAR 8-K filings with Item 2.02. Prices: Yahoo adjusted closes; SPY | **Reaction day E** is the first session whose close reflects the release, from the acceptance time in New York (≥ 16:00 → the next session). Long at the close of E−2, exit at the close of E. **Metric:** stock minus SPY return over the window, averaged over the stocks with the same E, net of 6.5 bps (stock CFD 5 + index hedge 1.5) | + | **2014-01 → 2026-08** (after Barber et al.); 2005–13 reported |

**Verdict:**
- **CONFIRMED:** one-sided HAC p < 0.05, net > 0, and a positive 2005–13 mean.
- **WEAK:** raw p < 0.05 only.

DSR N = 746.

**Also reported (not in the verdict):**
- per stock and per year;
- other windows: E−6 → E−1 (pre-event drift), the reaction day E alone, E → E+5 (post-event);
- the unhedged excess return over the T-bill.

A 2014 universe avoids choosing today's winners, whose past earnings surprises were mostly good.

### A20 (2026-09-26, after H2's result; written before any stock-level reversal result was computed)

| ID | Hypothesis | Data | Rule and metric | Pred. | Period |
|---|---|---|---|---|---|
| H3 | MR-06 on single large stocks: short-term reversal as liquidity provision (Nagel 2012; Jegadeesh 1990 at weekly horizons) | H2's 19 stocks, Yahoo adjusted closes | close(t) < close(t−1) < close(t−2) < close(t−3) → hold close(t) → close(t+1). Metric: return minus the stock's same-year mean daily return, pooled by date across stocks; 5 bps per trade | + | 2014-01 → 2026-08; 2005–13 reported |

**Verdict:** as H2. DSR N = 747.

**Also reported:** the market-adjusted version (minus SPY), and the share of signal days that coincide with an index MR-06 signal. The second shows whether H3 is just MR-06 on the index again.

### A21 (2026-09-26, round 8: checks that decide how to build and fund; written before any of these results was computed)

**X2 — second feed for N3 (the substitute for X1, which Dukascopy blocked).**
- **Data:** Yahoo 60-minute bars for QQQ and ^NDX, the last 730 days (≈ 2024-09 → 2026-09).
- **Rule:** the 60-minute-grid variant of N3 (marks 10:30 … 15:30), on the same code via `run(..., grid=60, ses=...)`.
  - It was already computed on HistData in the round-5 robustness (+2.65 bps/day, t = 2.41, 2014–25).
  - Yahoo bars start at 09:30, so the marks are exact bar closes.
- **Pre-registered criteria:**
  - daily-P&L correlation between HistData NSXUSD and QQQ ≥ 0.6 on common dates;
  - means of the same sign on both feeds.
- **Pass** means the feeds agree, so N3 is not a HistData artefact at the 60-minute grain. It does not test the 30-minute rule, and two years give no power on the mean.

**E1 — MR-06 exit variants (listed as pre-registered alternatives in the MR-06 card).**
- **Data:** SPY adjusted closes, 1993-02 → 2026-08.
- **Signal:** three down closes; enter at the close.
- **Exits:** close(t+1), close(t+2) or close(t+3). Metric: mean return per trade and per day held.
- **Decision rule:** switch from t+1 only if a variant's per-day mean beats t+1's with one-sided p < 0.05 (HAC difference on the trade sequence).

**S1 — regime sensitivity of the recommended prop set-ups** (A16 policies, same presets and simulation; not a test).
- **Set-ups:**
  - N3 news-filtered 4× on FTMO 1-Step;
  - N3 4× on FTMO 2-Step Swing;
  - MR-06 3× on FTMO 2-Step Swing.
- **Method:** bootstrap from 2014–19 only and from 2020–25 only.

**F1 — forward-test arithmetic** (analytic, not a test).
- The number of trading days or trades a forward test needs to reach t = 2, and the expected length of a sequential test (SPRT, α = β = 0.10) between "edge = in-sample" and "edge = 0", for N3, MR-06 and MR-08.
- A pre-set stop rule for paper trading.

**C1 — correlation between the MR-06 and N3 books** (2014–25 daily P&L), and how often both accounts would be breached in the same month.

**A21 addendum (before any A21 result):** **S2, edge-haircut sensitivity** (decision support, not a test).
- **Set-ups:** the three from S1.
- **Method:** rebuild each book as its zero-edge twin plus λ × its mean daily P&L, for λ ∈ {0, 0.25, 0.5, 0.75, 1}, and report EV per attempt and per account-month.
- **Question:** how much of the in-sample edge must be real for the set-up to beat the prop structure alone, and to be worth the fee at all.

### A22 (2026-09-26, round 9: edge families as strategy grids, then portfolios; written before any grid result was computed)

**Why:** a portfolio needs many validated, weakly correlated strategies, not one rule per mechanism.
Round 9 explores each mechanism across instruments, signal definitions, holding periods and regime
filters. It then asks the questions that matter when you choose from a grid:
- Does anything in the family beat zero after data snooping? (Hansen SPA)
- Which variants survive family-wise error control? (Romano–Wolf stepdown)
- How likely is it that picking the best in-sample picks an out-of-sample loser? (CSCV probability of backtest overfitting, PBO)
- Does choosing on past data work going forward? (walk-forward selection)
- How well does a portfolio chosen *only* from discovery data do out of sample?

Every grid below is fixed now. Statistics are computed on the daily net P&L of each variant (0 when flat).

#### Family A — short-term reversal in equity indices (daily; Yahoo)

**Instruments:**
- US: SPY, QQQ, DIA, IWM (adjusted; = US500, US100, US30, US2000).
- World: ^GDAXI, ^FTSE, ^N225, ^AXJO (price indices).

**Signals at the close of day t:**

| Signal | Definition |
|---|---|
| K2–K5 | k consecutive down closes, k ∈ {2, 3, 4, 5} |
| R5, R10, R20 | RSI(2) (Wilder) below 5, 10 or 20 |
| I10, I25 | IBS = (C − L)/(H − L) below 0.10 or 0.25 |
| L5, L10 | Close is the lowest close of 5 or 10 days |
| D15 | Return below −1.5 × 20-day volatility |

**Grid:**
- **Entry:** at the close of t.
- **Exits:**
  - X1: next close;
  - XU: the first close above the previous close, at most 5 days;
  - X3: the close of t+3.
- **Filters:** none; close > SMA(200); close < SMA(200).
- **Size:** 12 signals × 3 exits × 3 filters = 108 variants per instrument, **864 in total**.

**Net P&L per held day:**
- US ETFs: position × (return − T-bill) − 1 bp of CFD mark-up.
- World indices: the price return, with the T-bill subtracted.
- Every instrument: 1.5 bps charged on each entry.

**Split:** discovery to 2012-12; validation 2013-01 → 2026-08.

#### Family B — noise-area intraday momentum (1-minute HistData, clock converted through London time)

**Instruments** (local sessions; cost in bps):

| Instrument | Session | Cost | Notes |
|---|---|---|---|
| NSXUSD | 09:30–16:00 NY | 1.5 | |
| SPXUSD | 09:30–16:00 NY | 1.5 | |
| GRXEUR | 09:00–17:30 Berlin | 1.5 | |
| FRXEUR | 09:00–17:30 Paris | 2 | |
| UKXGBP | 08:00–16:30 London | 2 | |
| JPXJPY | 09:00–15:00 Tokyo | 3 | 15:30 from 2024-11-05; no marks in the 11:30–12:30 lunch break |
| AUXAUD | 10:00–16:00 Sydney | 3 | |
| HKXHKD | 09:30–16:00 HK | 4 | no marks 12:00–13:00 |
| XAUUSD | 08:20–13:30 NY | 2.5 | |

**Grid:**
- lookback ∈ {7, 14, 28} days;
- band multiplier ∈ {0.8, 1.0, 1.25}, applied to σ;
- mark grid ∈ {30, 60} minutes;
- exit ∈ {flip at the opposite band (N-rule), TWAP trailing stop};
- **36 variants × 9 instruments = 324 in total.**

**Split:** discovery 2014–2019; validation 2020–2025; 2026 holdout reported.

**Disclosed:** US100 with lookback 14, band 1.0, grid 30 and flip is N3, already confirmed on 2014–25. Its validation years are not clean. The family verdict is also reported without NSXUSD.

#### Family C — time-series trend (daily; G6's 17 ETFs + BTC, excess returns)

**Grid:**
- lookback ∈ {21, 63, 126, 252} days;
- signal ∈ {sign of the lookback return; close vs SMA(lookback); SMA(lookback/4) vs SMA(lookback)};
- sizing ∈ {40% vol target per asset (MOP); equal notional};
- rebalance ∈ {monthly; weekly};
- **48 portfolio-level variants.**

**Costs:** 2 bps per unit turnover, 0 financing; CFD sensitivity at 2%/yr.

**Split:** discovery 2007–2016; validation 2017-01 → 2026-08.

#### Family D — G10 currency premia (new; FRED)

**Data:**
- Month-end FX from the daily H.10 series: EUR, GBP, JPY, AUD, CAD, CHF, NZD, NOK, SEK vs USD.
- 3-month interbank rates, OECD IR3TIB01, for the ten currencies.

**Excess return of holding a currency for a month:** spot change + (its rate − the US rate) / 12.

**Strategies** (monthly, USD included as a zero-return asset):
- **Carry:** long the top k, short the bottom k by interest differential, k ∈ {2, 3}. Either unfiltered, or flat when the cross-currency 1-month realized volatility is above its trailing 36-month 80th percentile (CA-02).
- **Momentum:** long the top k, short the bottom k by past 1, 3 or 12-month excess return, k ∈ {2, 3}.
- **10 variants** in total.

**Costs:** 3 bps per unit turnover + 1%/yr swap mark-up on gross notional.

**Split:** discovery 1999-02 → 2011-12; validation 2012-01 → 2026-08.

#### Statistics (every family; numpy; stationary bootstrap, mean block 10 days / 3 months, B = 2,000, seed 7)

1. **Hansen SPA** (consistent version, studentized) on the validation period: H0 is that no variant has positive expected net return. Also reported per instrument for A and B.
2. **Romano–Wolf stepdown** (studentized max-t) on the validation period: FWER-adjusted p per variant, and the count significant at 5%.
3. **CSCV PBO** (Bailey, Borwein, López de Prado & Zhu 2017), full sample, S = 16 blocks, all 12,870 splits: the probability that the in-sample best ranks below the out-of-sample median. Also the slope of OOS Sharpe on IS Sharpe.
4. **Selection test:** the top 10% of variants by discovery Sharpe vs the rest, on validation Sharpe (Mann–Whitney).
5. **Walk-forward selection:** each January, pick the 5 best variants per family by expanding-window Sharpe and hold them equal-risk for the year. This is the purest out-of-sample number.
6. **Deflated Sharpe** of each family's best validation variant, N = 747 + 1,246.

**Family verdict:**
- **EDGE FAMILY:** SPA p < 0.05 on validation, PBO < 0.5, and a walk-forward Sharpe > 0.
- **WEAK FAMILY:** SPA p < 0.10, or walk-forward > 0 alone.
- **NO EDGE:** anything else.

#### Portfolio P (selection uses discovery data only)

**Selecting the candidates:**
- **Candidates:** per family, variants in the top 20% by discovery Sharpe whose *parameter neighbours* also have positive discovery Sharpe. Neighbours are the variants that differ by one grid step (A: same instrument and signal, the other exits and filters; B: one step in lookback or band; C: one step in lookback).
- **Clustering:** if two candidates' discovery daily correlation exceeds 0.6, keep the one with the higher discovery Sharpe.
- **Caps:** at most 8 per family, 2 per instrument in A and B.

**Weights:**
- inverse discovery volatility within a family;
- then equal risk across the families present.

**Evaluation:**
- **Common out-of-sample window:** 2020-01 → 2025-12. Every family is out of sample there (B's validation starts 2020).
- **Report:** Sharpe, maximum drawdown, correlations and each family's contribution. Compare with (i) equal weight on all variants and (ii) the single best discovery variant.
- **Prop:** the portfolio as one book on FTMO 2-Step Swing (A12 policies) against its zero-edge twin, and the families as separate accounts.

**Descriptive "aspects" reports (post hoc, not tests):** for MR-06-type and N3-type variants, P&L by
weekday, month, VIX regime, trend regime and year. These are for SQX parameter choices; no verdict rests on them.

**A22 amendment (2026-09-26, after Family A's first battery and before any other family was run):** for
long-biased families (A, C), a positive net P&L partly reflects the asset's own premium (beta), not timing
skill. The verdicts therefore use the **timing-value** series: P&L_t − position_t × the asset's same-year
mean daily excess return. That is this project's convention since round 1 (MR-06's "minus same-year mean").
- Raw results are reported too; the raw battery is what the P&L of a prop book sees.
- B (intraday long/short) and D (long/short currencies) are not adjusted: their positions are symmetric and have no persistent market exposure.
- The amendment can only make results weaker. It was prompted by Family A's result, so it is disclosed as post hoc.

**Second A22 amendment (after Family C's first run):** the same-year-mean benchmark is **invalid for trend
strategies**. It contains the year's own drift, the very thing trend following exploits, so it subtracts
the signal. Every trend variant turned negative (timing Sharpe −0.5 to −0.8) for that reason, not because
the strategies failed.
- **Family C's verdict** reverts to the pre-registered raw battery.
- **A look-ahead-free alternative is added** for both A and C: position × the asset's expanding-window mean daily excess return up to t−1 (from 252 days of history). It is reported for both families.
- **Family A's verdict** stays on the same-year timing series, as amended. For short holds its look-ahead is negligible, and it is the harsher of the two.

### A23 (2026-09-27, round 10: four more edge families; written before any of these grids was computed)

Same battery as A22: SPA and Romano–Wolf on validation, CSCV PBO on the full sample, selection test,
walk-forward top 5, and the same verdict rule. **Benchmark:** long-biased families are judged on timing
value against the **expanding-window** mean (position × the instrument's mean daily excess return up to
t−1, from 252 days of history; look-ahead-free). Raw results are reported too. The market-neutral family
G is judged raw. All data are Yahoo daily OHLC (adjusted where available); excess returns are over the
T-bill.

#### Family E — short-term reversal outside equity indices (does family A's edge generalise?)

- **Instruments (10):**
  - commodities via ETFs: GLD, SLV, USO, UNG;
  - FX: EURUSD=X, GBPUSD=X, USDJPY=X, AUDUSD=X;
  - crypto: BTC-USD, ETH-USD.
- **Signals and exits:**
  - Long after weakness: family A's 12 signals.
  - Short after strength: the mirror images (k up closes; RSI(2) > 95/90/80; IBS > 0.90/0.75; 5/10-day high; return > +1.5σ).
  - Exits: X1, X3, or XU (the first close back against the move).
- **Filters:** none; with the SMA(200) trend (long only above, short only below); against it.
- **Grid:** 12 × 2 directions × 3 × 3 = 216 per instrument, **2,160 in total.**
- **Costs:** per entry, commodities 2.5 bps, FX 1.0, crypto 5.0. CFD mark-up per held day: 2%/yr (commodities, crypto) and 0.5%/yr (FX).
- **Split:** discovery to 2014-12; validation 2015-01 → 2026-08. Crypto has no discovery period, so its variants enter the validation tests only.

#### Family F — per-market trend and breakout (the classic SQX family)

- **Instruments (22):** SPY, QQQ, DIA, IWM, ^GDAXI, ^FTSE, ^N225, ^AXJO; GLD, SLV, USO, UNG; EURUSD=X, GBPUSD=X, USDJPY=X, AUDUSD=X, USDCAD=X, USDCHF=X, NZDUSD=X; BTC-USD, ETH-USD; ^HSI.
- **Rules:**
  - Donchian breakout with an N/2 exit channel, N ∈ {20, 55, 100};
  - SMA crossover, (fast, slow) ∈ {(10, 50), (20, 100), (50, 200)};
  - sign of the L-day return, L ∈ {20, 60, 120}, re-evaluated daily.
- **Direction:** long-only or long-short.
- **Grid:** 9 × 2 = 18 per instrument, **396 in total.**
- **Costs:** as family E (indices 1.5 bps and 2%/yr mark-up). The mark-up is included in the primary; results without it are reported (futures).
- **Split:** discovery to 2014-12; validation 2015-01 → 2026-08.

#### Family G — relative-value reversal between index pairs (market-neutral)

- **Pairs (synchronous closes only):** QQQ/SPY, IWM/SPY, DIA/SPY, QQQ/IWM, ^GDAXI/^FCHI, ^FTSE/^GDAXI.
- **Signal:** the z-score of the log price ratio over L ∈ {20, 60, 120} days.
- **Direction:**
  - reversion: when |z| > k (k ∈ {1.5, 2.0, 2.5}), long the laggard and short the leader, dollar-neutral;
  - momentum: the opposite.
- **Exits:** z crosses 0, or a time stop of 5 or 20 days.
- **Grid:** 3 × 3 × 2 × 3 = 54 per pair, **324 in total.**
- **Costs:** 1.5 bps per leg per entry and exit, and 2%/yr mark-up on each leg.
- **Split:** discovery to 2012-12; validation 2013-01 → 2026-08.

#### Family H — calendar effects on 8 indices

- **Instruments:** SPY, QQQ, DIA, IWM, ^GDAXI, ^FTSE, ^N225, ^AXJO.
- **Rules:**
  - Turn of month: enter at the close k trading days before the month's last trading day, exit at the close m trading days into the new month, (k, m) ∈ {1…4}².
  - Weekday: long each weekday's close-to-close.
  - Pre-holiday (US instruments only): long the one or two sessions before a US market holiday.
- **Grid:** 23 variants per US instrument, 21 per world index, **176 in total.**
- **Costs:** 1.5 bps per entry, plus the mark-up (US ETFs).
- **Split:** discovery 1993–2012; validation 2013-01 → 2026-08.

**Portfolio extension:** any family rated EDGE FAMILY is added to the A22 portfolio with the same
discovery-only selection rule, and the portfolio is re-evaluated out of sample (2020–25 and 2026).

DSR trial count: 747 + 1,246 + 3,056 = 5,049.

**A23 amendment (2026-09-27, after family E's first run showed an impossible result):** **Yahoo daily FX
bars are unusable.**
- Family E's FX variants showed a walk-forward Sharpe near 10.
- A check found that on Yahoo EURUSD (2015–25), IBS correlates **−0.69** with the next day's return. On HistData minute data rebuilt into daily bars that close at 17:00 NY, the correlation is −0.01, and the IBS rule earns +0.29 bps (t = 0.25).
- Yahoo's FX close sits 36 bps on average from the 17:00 NY price; its close and range come from inconsistent windows.

**What changes:**
- The Yahoo-based FX legs of families E and F are **withdrawn**.
- Both families are re-run with FX daily bars built from HistData minute data (2003–2026). Each bar closes at 16:45 NY, before the rollover spread widening that caused the round-2 artefact. Minutes 16:45–19:00 NY are excluded from each bar's high/low.
- Rules, grids, costs and splits are unchanged.

#### Family I (added to A23 before any of its data was downloaded) — crypto trend

- **Motivation:** family F's only positive market was Bitcoin (per-market SPA p = 0.031). Crypto time-series momentum at 1–4 week horizons is well documented (Liu & Tsyvinski 2021, *RFS*).
- **Universe, fixed to avoid survivorship:** the largest coins by market cap on 2019-01-01, excluding stablecoins and the November 2018 BSV fork: **BTC, XRP, ETH, BCH, EOS, XLM, LTC, TRX** (Yahoo `-USD` daily).
- **Rules:**
  - Donchian N ∈ {10, 20, 55} (N/2 exit);
  - SMA crossover (5, 20), (10, 50), (20, 100);
  - sign of the L-day return, L ∈ {7, 14, 28, 56};
  - long-only or long-short.
- **Grid:** 20 per coin, **160 in total.**
- **Costs:** 5 bps per trade. CFD financing 2%/yr in the primary result; 10%/yr sensitivity (many CFD brokers charge more on crypto).
- **Split:** discovery 2018-01 → 2021-12; validation 2022-01 → 2026-08.
- **Benchmark:** timing value against the expanding mean, as the rest of A23.

DSR count: 5,049 + 160 = 5,209.

#### Families J and K (added to A23 after E–I's results; written before either was computed)

**J — family A's reversal grid on the remaining prop-tradeable indices.**
- **Instruments:** ^HSI (HK50), ^STOXX50E (EU50), ^FCHI (FRA40), ^IBEX (SPA35), ^IXIC (Nasdaq Composite, a second US check).
- **Grid:** family A's 108-variant grid unchanged, **540 variants.**
- **Costs:** 1.5 bps per entry (3 bps for ^HSI).
- **Split:** discovery to 2012-12; validation 2013-01 → 2026-08.
- **Benchmark:** timing value against the same-year mean, as family A.

**K — cross-sectional short-term reversal among large US stocks (market-neutral).**
- **Universe:** H2's 19 largest US stocks at end-2013.
- **Rule:** each formation date, rank stocks by the past F-day return, F ∈ {1, 5, 10}. Long the bottom q and short the top q, q ∈ {3, 5}, equal weight, dollar-neutral. Hold H ∈ {1, 5} days (H = 5 uses 5 overlapping sub-portfolios).
- **Grid:** 12 variants.
- **Costs:** 5 bps per unit turnover per leg, and a 2%/yr mark-up on gross.
- **Split:** discovery 2005–2013; validation 2014 → 2026-08.

The verdict rule is unchanged. DSR count: 5,209 + 552 = 5,761.

### A24 (2026-09-27, round 11: SQX- and prop-implementability review, plus FX / metals / European-index families; written before any of these results was computed)

**User scope from here on:** edges that StrategyQuant X can build and that suit prop-firm CFD accounts,
mainly FX, indices and metals.

**Data:** HistData 1-minute bars (clock converted through London time, `local_table`), 2013 → 2026-09. FX
and metals with no window touching 16:45–19:00 NY.

**Battery and verdict rule:** as A22.

#### Part 1 — review of the index edges as SQX would trade them

**R1. The reversal family (family A's 108-variant grid) under three implementations:**

| Implementation | Bars | Signal | Entry | Exit |
|---|---|---|---|---|
| (a) SQX on broker daily bars | 24-hour CFD bars closing 17:00 NY | at the bar close | next bar's open | the open after the exit condition |
| (b) SQX with a cash-session daily bar | 09:30–16:00 NY (Tokyo 09:00–15:00, 15:30 from 2024-11-05) | at the session close | next session's **open** | an open |
| (c) SQX M5 chart with session-daily conditions | cash-session closes; the 15:55 price stands in for today's close | at 15:55 (Tokyo: 5 minutes before the close) | at 15:55 | at 15:55 on the exit day |

- **Instruments:** US500, US100, JP225 (the edge's markets); GER40 and XAUUSD as controls.
- **Period:** 2014-01 → 2026-08; SPA on the whole period.
- **Costs:** 1.5 bps per entry (JP225 3.0, XAUUSD 2.5).
- **Report:** median Sharpe, share of variants positive, per-instrument SPA and the equal-risk ensemble Sharpe, per implementation.
- **Prediction:** (c) ≈ family A; (b) loses about half the edge (the overnight part); (a) is unknown.

**R2. Prop-rule variants of the (c) ensemble:**
- **No weekend holds:** no entry on the last session of a week; open trades exit at Friday's 15:55.
- **Report:** its Sharpe against unrestricted (c).

**R3. SQX-native approximations of the US100 intraday rule (N3):**
- **Grid** (US100 2014–26; US500 secondary):
  - band = session open ± k × {prior session range, ATR(14) of session ranges}, k ∈ {0.3, 0.5, 0.7};
  - the first touch enters;
  - either flat at 15:59, or reverse at the opposite band.
- **Size:** 12 variants.
- **Recommend a native build if:** its median Sharpe is ≥ 70% of N3's, and its daily-P&L correlation with N3 is ≥ 0.5.

#### Part 2 — new families for FX, metals and European indices (SQX-native, intraday, flat before the rollover)

**Family L — FX and gold session seasonality** (Breedon & Ranaldo 2013, *JMCB*: currencies depreciate during their home trading hours).
- **Instruments:** EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, XAUUSD.
- **Windows (London time):** Asia 00:00–07:00, Europe 07:00–12:00, overlap 12:00–16:00, US afternoon 16:00–21:00.
- **Rule:** long or short at the window start, exit at its end.
- **Grid:** 8 × 4 × 2 = **64 variants.**
- **Costs:** 1.0 bps per round trip (majors), 2.5 (gold).
- **Split:** discovery 2003–2013; validation 2014 → 2026-09.

**Family M — FX low-liquidity mean reversion (the "night scalper" family).**
- **Instruments:** EURGBP, EURCHF, AUDNZD, EURCAD, AUDCAD, GBPCHF, USDCAD, USDCHF, EURUSD.
- **Bars and window:** M15, entries 19:00–00:45 NY.
- **Signal:** the bar closes outside a Bollinger band (20, k), k ∈ {1.5, 2.0, 2.5}, or RSI(3) < 10 / > 90. Fade it at the bar close.
- **Exit:** the middle band (or RSI crossing 50), a 1-hour time stop, or 01:00 NY.
- **Grid:** 9 × (3 + 1) × 3 = **108 variants.**
- **Costs:** night spreads, 1.5 bps per round trip (EURUSD, USDCAD, USDCHF), 3.0 (crosses).
- **Split:** discovery 2008–2015; validation 2016 → 2026-09.

**Family Q — European index open (gap fade or follow).**
- **Instruments:** GER40, UK100, FRA40.
- **Gap:** the cash open (09:00 Berlin/Paris, 08:00 London) vs the prior cash close. Trade when |gap| > k × its 20-day mean |gap|, k ∈ {0.5, 1.0, 1.5}.
- **Direction:** fade or follow.
- **Exit:** at 11:00, 13:00 or the cash close, or on gap fill with a stop of one gap size.
- **Grid:** 3 × 3 × 2 × 4 = **72 variants.**
- **Costs:** 1.5 bps (GER40), 2.0 (UK100, FRA40).
- **Split:** discovery 2013–2019; validation 2020 → 2026-09.

**Family R — session-range breakouts and fades in FX and metals.**
- **Instruments:** XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, AUDUSD.
- **Ranges:** Asia 00:00–07:00 London (traded 07:00–12:00), or London morning 07:00–13:00 (traded 13:00–16:00).
- **Rule:** breakout (stop at the edge, stop-loss at the other edge), or fade (limit at the edge, stop at 50% of the range beyond it).
- **Exit:** the window end, or a target of 1× the range.
- **Grid:** 6 × 2 × 2 × 2 = **48 variants.**
- **Costs:** FX 1.0 bps, gold 2.5, silver 5.0.
- **Split:** discovery 2010–2016; validation 2017 → 2026-09.

**Verdicts:**
- Families L, M, Q, R: as A22.
- R1–R3 are implementability measurements that choose how to build, not new tests. Their SPA values are reported.

**Prop suitability**, checked for any EDGE family:
- intraday and flat before the 17:00 NY rollover (no swaps, no weekend exposure);
- trade times against news windows;
- an FTMO lifecycle with the A16 presets.

DSR count: 5,761 + 292 = 6,053, with R1 (1,620 measurements) disclosed as implementation variants.

### A25 (2026-09-27, round 11 addendum: prop lifecycle of the SQX builds and of family R; written after the R1–R3 and L/M/Q/R results, before any lifecycle number was computed)

**Purpose:**
- Turn the R1–R3 results into prop decisions.
- Run the prop suitability check that A24 requires for family R, the only round-11 family rated EDGE.

This is a decision analysis, not a hypothesis test. The edge estimates are in-sample for 2014–26.

**Books** (daily P&L with intraday low and high, as fractions of equity; HistData minutes 2014-01 → 2026-08; R1 raw-P&L conventions for financing, mark-up and costs):
- **B8, REV-SQX:**
  - R1 implementation (c) on US500, US100 and JP225.
  - Within a market, the 108 variants are weighted equally. The book's exposure is the share of variants in a position.
  - Markets are weighted to equal risk.
  - Weekend holds are allowed.
  - Each market's intraday low and high are exact: all variants are long the same instrument between the same marks. Across markets, lows are summed (conservative).
- **B8w:** B8 with R2's no-weekend rule.
- **B9, N3-native:**
  - The 12 R3 variants on US100, weighted to equal risk.
  - The path is exact at the minute level: the book's position is the weighted sum of the variants' positions.
  - Entries and reversals are skipped within ±2 min of the A16 `news_skip` times (ISM 10:00 on the first and third trading days, FOMC 14:00 and 14:30, minutes 14:00).
- **B10:** B8w + B9, weighted to equal risk.
- **B11, family R:** USDJPY|LDNAM|BRK|END, the SPA's best variant (an upper bound), with an exact path.
- **B11n:** B11 without entries within ±2 min of 08:30 or 10:00 NY on any weekday, a conservative stand-in for FTMO Standard's high-impact news blackout.

**Where each book is run (guard 3% on FTMO 2-Step, 2% on the others, as A16):**

| Preset | Books |
|---|---|
| FTMO 2-Step 100k, Swing | B8 |
| FTMO 2-Step 100k, Standard | B8w, B9, B10, B11n |
| FTMO 1-Step 100k | B8w, B9, B10, B11n |
| Topstep 50K (flat by 15:10 CT) | B9 |

**Scale and policies:**
- Each book is scaled to 1% daily volatility at 1×, using its 2014–2016 volatility.
- Policies: fixed 0.5, 1, 1.5, 2 and 3×; CPPI with k = 10 and 20, cap 3×.
- Every run has a zero-edge twin (the demeaned book).
- Decision rule (A16): among the policies with positive edge value, recommend the one with the highest EV per account-month.
- Report the instrument leverage (notional ÷ equity) implied by the recommended policy, so SQX money management can be set.

**Family R prop check (A24):**
- It is intraday and flat by 16:00 London by construction.
- Report B11's share of entries inside the news windows.
- Report B11's P&L at +0.5 and +1.0 bps extra slippage per trade.
- Report the family battery without USDJPY (descriptive, like family B's "excluding NSXUSD").

### A26 (2026-09-27, round 12: edge research, SQX-buildable designs; written before any of these results was computed)

**User scope:**
- Research edges; implementation comes later.
- Every rule must be buildable in StrategyQuant X from bar data: time-of-day, session and day-of-week conditions, standard indicators, stop and limit orders.
- Markets: FX, indices, metals. No Treasuries.

**Battery and verdict rule:** as A22.
**DSR count:** 6,053 + 1,842 = 7,895.
**Data:** HistData minute data converted through London time (`data_minutes.local`); no FX or metals price inside 16:45–19:00 NY; Yahoo daily for family S.

#### Family S — the short side of index reversal (Baltussen, van Bekkum & Da 2019, *JFE*: index-level serial dependence is negative)

**Hypothesis:** the mirror image of family A. After short-term strength, US index returns over the next 1–5 sessions are below normal.
- **Grid:** family A's grid mirrored: k up closes (2–5); RSI(2) > 95/90/80; IBS > 0.90/0.75; the close is the highest close of 5/10 days; an up day > 1.5σ. Exits: next close, first down close (max 5), 3 days. Filters: none, below SMA(200) (with the trend for a short), above SMA(200). Markets: family A's 8 (SPY, QQQ, DIA, IWM, ^GDAXI, ^FTSE, ^N225, ^AXJO).
- **Size:** 864 variants.
- **P&L:** short CFD: −(excess return) − mark-up − costs (family A's costs).
- **Split:** 1993 → 2012 discovery; 2013 → 2026-08 validation.
- **Verdict:** on timing value (same-year-mean benchmark, as A). Raw P&L is reported.
- **Prediction:**
  - positive timing value on US indices, weaker than the long side;
  - Boyarchenko et al. 2023 find reversals after rallies "much more modest" than after sell-offs;
  - raw P&L ≤ 0 (shorting against the drift).

#### Family T — anatomy and durability of the reversal edge (Boyarchenko, Larsen & Whelan 2023, *RFS*; NY Fed 2026 "The Disappearing Overnight Drift")

**Setting:** R1 build (c), US500, US100, JP225 and a GER40 control, 2014-01 → 2026-08.

**Grid (108 per market):** the 12 signals × 3 filters × 3 one-day exits:
- **E1:** the next 03:00 NY, after the first European hour;
- **E2:** the next cash open (09:31 NY; Tokyo 09:00 JST);
- **E3:** the next mark (15:55 NY; Tokyo 14:55, 15:25 from 2024-11-05).

Costs as R1, plus one night of financing.

**Tests:**
- **T1:** the battery per exit group. Discovery 2014–2019; validation 2020 → 2026-08.
- **T2:** the US500 + US100 + JP225 ensemble Sharpe per exit, with a 95% stationary-bootstrap interval for E1 − E3 and E2 − E3.
- **T3 (mechanism, post-publication check):** the US500 and US100 02:00–03:00 NY return, and the 16:00 → 09:30 NY return, after a down close vs after an up close (close-to-close at 16:00). The difference and its HAC t are reported for 2014–2020 and 2021 → 2026-08.

**Predictions:**
- E1 and E2 carry most of the reversal (inventory mechanism).
- **The NY Fed reports the unconditional drift and the order-imbalance link gone after 2021.** If our T3 difference is also gone after 2021 while REV stayed profitable, the mechanism story needs revising.

#### Family U — US macro-release shocks: follow or fade (Evans & Lyons 2008: macro news is transmitted partly through subsequent order flow; Andersen et al. 2003: prices adjust within minutes)

**Instruments:** EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, XAUUSD, XAGUSD, US500, US100.

**Event times:** 08:30, 10:00 and 14:00 NY. No calendar is needed. A shock is the return from T to T + 5 min when it exceeds k × its median absolute value at the same time over the prior 60 weekdays, with k ∈ {3, 6}.

**Trade:**
- **Entry:** at T + 5 min, outside FTMO's ±2-minute window.
- **Direction:** follow or fade the shock.
- **Exit:** T + 65 min, T + 125 min, or end of day (FX and metals 16:40 NY; indices 15:55 NY, which caps later exits).

**Size:** 9 × 3 × 2 × 2 × 3 = **324 variants.**

**Costs (round trip):** FX 1.5 bps, gold 3.0, silver 6.0, indices 2.0.

**Split:** discovery 2010 → 2017 (indices 2013 → 2017); validation 2018 → 2026-09.

**Prediction:** follow > 0 at 1–2 hours in FX and gold (order-flow transmission; consistent with round 11's gross London-afternoon breakout). The prior is low: Andersen et al. and Chordia, Green & Kottimukkalur (2018) find little predictability minutes after a release.

#### Family V — precious-metals auction windows (Caminschi & Heaney 2014, *JFM*: the old London PM gold fixing leaked information within minutes)

**Events:**
- **Gold:** LBMA 10:30 and 15:00 London, and the COMEX open 08:20 NY.
- **Silver:** LBMA 12:00 London, and the COMEX open 08:25 NY.

**Windows:** [event − 60 min, event], [event, event + 60], [event, event + 180]; long or short.

**Size:** 30 variants.

**Costs:** gold 2.5 bps, silver 5.0.

**Split:** discovery 2009 → 2016; validation 2017 → 2026-09.

**Prediction:** no edge after the 2014–15 move to electronic auctions. This family is a control that also formally re-tests round 5's silver pre-fix lead.

#### Family W — FX weekend-gap reversal (Dao, McGroarty & Urquhart 2016: after a large Friday-close-to-Monday-open gap, most FX pairs reverse)

**The paper:** Bloomberg daily data 2002 → 2014-05; top and bottom 5 / 10 / 15% gaps; 8 bps round-trip cost; up to 10% a year out of sample.

**Instruments:** EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, XAUUSD.

**The gap:**
- It runs from the price at 16:45 NY on Friday to the price at 19:00 NY on Sunday, the first clean price after the rollover.
- "Large" means in the top or bottom q of the trailing 104 weekend gaps (rolling, no look-ahead), q ∈ {5%, 10%, 20%}.

**Trade:**
- **Entry:** at Sunday 19:00 NY. Nothing is held over a weekend.
- **Direction:** fade (the paper) or follow.
- **Exit:** Monday 08:00 London, Monday 13:00 London, Monday 16:45 NY, or Friday 16:45 NY (one week).

**Size:** 8 × 3 × 2 × 4 = **192 variants.**

**Costs:** FX 1.5 bps (Sunday spreads), gold 3.0; plus the A23 FX mark-up of 0.5%/yr per night held.

**Split:** discovery 2003 → 2014 (gold 2009 → 2014), roughly the paper's sample; **validation 2015 → 2026-09, after publication.**

**Prediction:** fade > 0 on most majors.

**SQX buildability (all five families):**
- day-of-week and time conditions;
- a fixed-time bar return compared with its rolling median (U) or rolling quantiles of the Sunday gap (W), which is a custom block or an approximation with standard percent-rank indicators;
- stop, limit and market orders;
- time exits.

### A27 (2026-09-27, round 13: FX-cross reversal, volatility-regime index entries, momentum by volatility regime; written before any of these results was computed)

**Scope:** edge research only. Every rule must be buildable in SQX: daily bars on an NY-close clock, standard indicators, and multi-symbol conditions for VIX data imported as an extra symbol.

**Battery and verdict rule:** as A22.
**DSR count:** 7,895 + 4,662 + 108 + 4 = 12,669.

#### Family Y — reversal on FX crosses

**Why:** crosses between similar economies (AUDNZD, EURGBP, EURCHF…) are practitioner mean-reversion pairs. Family E tested reversal only on USD majors, gold, silver, oil, gas and crypto.

**Instruments (21):** EURGBP, EURCHF, AUDNZD, EURCAD, AUDCAD, GBPCHF, NZDCAD, CADCHF, AUDCHF, EURAUD, EURNZD, GBPAUD, GBPCAD, GBPNZD, EURJPY, GBPJPY, AUDJPY, CHFJPY, CADJPY, NZDJPY, NZDCHF.

**Bars:** daily bars from HistData minutes, running 19:00 NY → 16:45 NY. Nothing inside 16:45–19:00 NY is used (A23 rule).

**Grid:**
- **Family E's long/short grid,** 216 per cross: 12 signals, mirrored for shorts; 3 exits; filters none / with the SMA(200) trend / against it.
- **Plus a Bollinger rule,** 6 per cross: the close outside BB(20, 2); exit at the middle band, at most 20 days; long and short; the same 3 filters.

**Size:** 21 × 222 = **4,662 variants.**

**Costs:**
- EURGBP, EURCHF and EURJPY: 2.0 bps per round trip; the other crosses 3.0.
- Plus the A23 FX mark-up of 0.5% a year per calendar day held.

**Split:** discovery 2008-10 → 2016; validation 2017 → 2026-09.

**Verdict:** on timing value with the expanding-mean benchmark, as family E. Raw is reported.

**Prediction:** positive for the similar-economy crosses (AUDNZD, EURGBP, EURCHF, AUDCAD, NZDCAD, CADCHF); weaker for JPY crosses (carry and trend).

#### Family Z — volatility-regime entries on US indices ("buy fear")

**Sources:**
- Fassas & Hourvouliades (2019, *JRFM*): VIX-futures backwardation predicts positive S&P 500 returns.
- Bollerslev, Tauchen & Zhou (2009, *RFS*): the variance risk premium predicts market returns.

**Markets:** SPY, QQQ, DIA, IWM (Yahoo, family A's loader and costs). Long only; entry at the close.

**Triggers (at the close of t):**

| Trigger | Condition |
|---|---|
| BW | VIX / VIX3M ≥ 1.00, 1.05 or 1.10 |
| SP | VIX up ≥ 15% or ≥ 25% on the day |
| EL | VIX ≥ 1.2× or ≥ 1.4× its 20-day SMA |
| VRP | VRP = (VIX/100)² − 252 × the mean squared daily index return over 21 days, in the top third or top fifth of its trailing 252-day distribution |

**Exits:**
- **ST:** hold while the trigger holds;
- **H5:** 5 days;
- **H10:** 10 days.

Re-entry is allowed at an exit.

**Size:** 9 triggers × 3 exits × 4 markets = **108 variants.**

**Split:** discovery 2007-07 → 2016; validation 2017 → 2026-08.

**Verdict:** on timing value (same-year mean, as family A).

**Novelty test:** regress the validation-period equal-risk Z ensemble on family A's US ensemble (timing value, Newey-West). **Z counts as a new edge only if its alpha t > 2**; otherwise it is the reversal edge again.

#### Family ZM — US index intraday momentum by volatility regime

**Sources:** Gao, Han, Li & Zhou (2018) and Zarattini et al. find intraday momentum stronger in volatile markets.

**Series:** the N1 (US500) and N3 (US100) daily P&L, family B's clock-corrected series, 2014-01 → 2026-08.

**Regime:** high if the previous day's VIX close is above its trailing 252-day median.

**Tests:**
- **ZM1:** the US500 high-regime mean is > 0.
- **ZM2:** the US100 high-regime mean is > 0.
- One-sided, HAC t (lag 5), Holm over the two tests.
- Low-regime means and the high − low difference are reported.

**Prediction:** positive in the high regime for both markets. A US500 pass would add a second market for the momentum edge (conditional).

### A28 (2026-09-27, round 14: futures positioning (COT) and the index rebound through FX and gold; written after round 13's results, before any of these results was computed)

**Battery and verdict rule:** as A22.
**DSR count:** 12,669 + 264 + 80 = 13,013.

#### Family CT — trader positioning from the CFTC Commitments of Traders (legacy, futures only)

**Sources:**
- Wang (2001, *JFM*) and Wang (2003): large-speculator sentiment forecasts continuation; hedger sentiment forecasts reversal.
- Tornell & Yuan (2012, *JFM*): peaks and troughs of net positions predict currency moves.

**Data:** CFTC weekly reports 1986 → 2026 (as of Tuesday).

**Contracts and the spot or ETF traded** (inverse where the future is the foreign currency against USD):

| Contract | Code | Traded as |
|---|---|---|
| Euro FX | 099741 | EURUSD |
| Yen | 097741 | USDJPY, inverse |
| Pound | 096742 | GBPUSD |
| Swiss franc | 092741 | USDCHF, inverse |
| Canadian dollar | 090741 | USDCAD, inverse |
| Australian dollar | 232741 | AUDUSD |
| NZ dollar | 112741 | NZDUSD |
| Gold | 088691 | XAUUSD |
| Silver | 084691 | XAGUSD |
| E-mini S&P 500 | 13874A | SPY |
| Nasdaq-100 mini | 209742 | QQQ |

**Signal:**
- The net position of a group, noncommercial (speculators) or commercial (hedgers), as a share of open interest.
- It is scaled to Wang's sentiment index over the trailing 156 weeks: (NP − min) ÷ (max − min).
- **Extreme bullish:** SI ≥ 0.9 or ≥ 0.8. **Extreme bearish:** SI ≤ 0.1 or ≤ 0.2.

**Trade:**
- **Entry:** at the close of the trading day 6 calendar days after the as-of date (the Monday after Friday's release). FX and metals use the 16:45 NY close; SPY and QQQ their close.
- **Direction:** WITH the group's extreme or AGAINST it.
- **Hold:** 5, 10 or 20 trading days.
- **Overlap:** trades don't overlap. A report whose entry date falls inside an open trade is skipped.

**Size:** 11 markets × 2 groups × 2 thresholds × 2 directions × 3 holds = **264 variants.**

**Costs (round trip):** FX 1.0 bps, gold 2.5, silver 5.0, SPY/QQQ 1.5. Plus mark-ups: FX 0.5%/yr, metals 2%/yr, index CFDs as family A.

**Split:** discovery → 2013 (FX 2003 →, gold 2009 →, silver 2010 →, SPY/QQQ 2003 →); validation 2014 → 2026-08.

**Verdict:** on timing value (expanding-mean benchmark).

**Prediction:** WITH speculators and WITH hedgers are both positive (continuation and hedging-pressure reversal).

**SQX:** the COT series is imported as an extra symbol (the weekly value held as a daily series). SQX's multi-symbol conditions and a highest/lowest(156-week) scaling reproduce the rule.

#### Family XR — the US index rebound traded through FX and gold

**Question:** is the US-index reversal edge (family A) a broad risk-on rebound that FX and gold share, or specific to index products?

**Signal:** family A's signals on ^GSPC's daily close, which are known by 16:00 NY: IBS < 0.10, RSI(2) < 10, three down closes, the close at a 5-day low.

**Legs:** entry at the 16:45 NY FX/metal close the same day (outside the rollover zone).
- **Long:** AUDJPY, NZDJPY, CADJPY, EURJPY, USDJPY, AUDUSD, NZDUSD, USDCHF.
- **Gold:** long, and separately short.

**Exits:** the next 16:45 close, or the first day ^GSPC closes above its prior close (at most 5 days; exit at that day's 16:45 close).

**Size:** 4 × 2 × 10 = **80 variants.**

**Costs:** majors 1.0 bps, JPY crosses 2.0, gold 2.5; plus mark-ups as CT.

**Split:** discovery 2008 → 2013; validation 2014 → 2026-08.

**Verdict:** on timing value (expanding mean).

**Prediction:** long risk currencies positive if the rebound is broad risk-on. A null here supports the index-product liquidity-provision reading.

### A29 (2026-09-27, round 15: the reversal edge by volatility regime; a decision analysis, written before any of these results was computed)

**Question:**
- Does the index-reversal edge (family A) earn its timing value in stress or in calm regimes?
- Would a regime filter improve its risk-adjusted return or its crash tail, the prop problem found in §21.4?

**Source:** Nagel (2012, *RFS*): reversal (liquidity-provision) returns rise with the VIX.

**Data:**
- **Signals and trades:** family A's 108 variants on SPY, QQQ, DIA, IWM and ^N225, Yahoo daily.
- **Window:** 2007-07 → 2026-08.
- **Regime at the signal close:** STRESS if VIX / VIX3M ≥ 1.0, CALM otherwise.

**Measures:**
- **RG1:** mean timing value per trade, STRESS vs CALM (US variants pooled, one observation per trade), with Welch t.
- **RG2:** the equal-risk US ensemble, all trades vs CALM-only trades:
  - Sharpe of timing value and raw P&L;
  - 95% stationary-bootstrap interval for the difference;
  - worst day and maximum drawdown.
- **RG3:** RG1 and RG2 for ^N225 (US VIX regime).

**Prediction:**
- STRESS trades earn more per trade (Nagel).
- The CALM-only ensemble has a smaller tail. Its Sharpe could go either way.

**Decision rule:** recommend a CALM filter for prop books only if the CALM-only Sharpe is not lower (the upper end of the difference interval is ≥ 0) and the worst day improves.

This is not a new family. The DSR count is unchanged (13,013).

### A30 (2026-09-27, round 16: a VIX-free regime for FTMO, and a look-ahead correction to A29; written before any of these results was computed)

**Why:**
- FTMO's server has no VIX symbol. An MT4/MT5 EA can only read symbols from its own server.
- **Look-ahead in A29 RG3 (found now):** for ^N225, A29 took the regime from the same calendar date's VIX close. That close is published at about 16:15 NY, roughly 15 hours after the Tokyo close it was used for.
- The JP225 result in REPORT §22.1 is therefore withdrawn until this re-run. The US results are unaffected in substance: the US close and the VIX close are 15 minutes apart, and US legs are not filtered.

**Regimes:** stress vs calm. Every signal uses only data known at the signal close. For ^N225 that means the US close of the previous US trading day.
- **VIX:** VIX / VIX3M ≥ 1, the A29 rule with the lag corrected.
- **FTMO-available proxies,** from US500 daily bars (^GSPC here; US500.cash on FTMO):
  - **RVR:** std(returns, 5) ÷ std(returns, 60);
  - **ATRR:** ATR(5) ÷ ATR(50);
  - **DD:** the close vs its 60-day high;
  - **RVL:** 20-day realized volatility, annualized.

**Calibration:**
- Each proxy's threshold is set so that its stress share over 2007-07 → 2016 equals the VIX regime's share in the same period. This matches frequency, not outcomes.
- **Primary proxy:** the one with the highest phi correlation with the VIX regime over 2007-07 → 2016.

**Measures:** A29's RG1–RG3 for ^N225 and the US ETFs under each regime definition:
- the full period 2007-07 → 2026-08;
- 2017 → 2026-08 (after calibration).

**Decision rule, for JP225 legs:** filter stress entries only if both hold:
- the calm-only Sharpe difference interval excludes 0 on the full period under the corrected VIX regime;
- the primary proxy's difference is positive in 2017 → 2026-08.

US legs stay unfiltered (A29).

### A31 (2026-09-27, round 17: FX/gold intraday momentum, reversal breadth, late-day index momentum; written before any of these results was computed)

**Battery and verdict rule:** as A22.
**DSR count:** 13,013 + 80 + 540 + 8 = 13,641.

#### Family FM — intraday momentum in FX and gold

**Sources:**
- Elaut, Frömmel & Lampaert (2018, *JFM*): the first half hour predicts the last half hour in FX; liquidity providers avoid overnight risk.
- Gao, Han, Li & Zhou (2018, *JFE*) and Baltussen et al. (2021, *JFE*): the same effect in index futures.
- Zarattini, Aziz & Barbon: the noise area. It is the US100 edge here, and was never tested on FX.

**Instruments:** EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, XAUUSD.

**Rules:**
- **Session momentum.** Two "days": London 08:00–16:00 London, and New York 08:00–16:30 NY. The predictor is either the first-half-hour return or the return from the open to the start of the last half hour. The position is held for the last half hour in the predictor's direction. That gives 2 × 2 = 4 rules.
- **Noise area.** The session opens at 08:00 London; 30-minute marks run 08:30–20:00 London; the book is flat at 20:30 London, which is 15:30 NY, or 16:30 NY in the daylight-saving gap weeks. Lookback {7, 14, 28} × band {1.0, 1.25}, flipping at the opposite band. That gives 6 rules.

**Size:** 8 × 10 = **80 variants.**

**Costs:** FX 1.0 bps per entry, gold 2.5.

**Split:** discovery 2010 → 2016; validation 2017 → 2026-09. **Verdict:** raw P&L.

**Prediction:** positive in the session-momentum rules; noise area positive at least for USDJPY and gold.

#### Family RB — breadth of the index-reversal edge (new SQX-native entry signals, more markets)

**Why:** to give SQX a larger validated set of reversal entry blocks, and to add US30 and US2000 (FTMO symbols).

**Markets:** SPY, QQQ, DIA, IWM, ^N225 (Yahoo daily, family A's data and costs).

**Signals (12):**

| Code | Rule |
|---|---|
| ST10, ST20 | Stochastic %K(14) < 10 / < 20 |
| WR5 | Williams %R(5) < −95 |
| BB0 | Bollinger %B(20, 2) < 0 |
| KC2 | Close < EMA(20) − 2 × ATR(10) |
| CR10, CR15 | Connors RSI(3, 2, 100) < 10 / < 15 |
| LL3 | Three lower lows in a row |
| ATP | Close < SMA(5) − ATR(10) |
| CUM35 | Two-day cumulative RSI(2) < 35 |
| PR5 | The 5-day return in the bottom decile of its 252-day history |
| WRB | IBS < 0.25 and range > 1.5 × ATR(10) |

**Exits:** the next close (X1); the first up close, max 5 (XU); the close above SMA(5), max 10 (XS5).

**Filters:** none; below SMA(200); above SMA(200).

**Size:** 12 × 3 × 3 × 5 = **540 variants.**

**Split:** discovery 1993 → 2012; validation 2013 → 2026-08.

**Verdict:** timing value (same-year mean), as family A.

**Also reported:** the correlation of the RB ensemble with family A's ensemble.

**Prediction:** EDGE family (the same mechanism as family A), with US30 and US2000 positive.

#### Family IM2 — late-day momentum on US indices

**Sources:** Gao et al. (2018); Baltussen et al. (2021); Rosa (2022, "strong signals only").

**Data:** HistData US500 and US100, 2014 → 2026-08.

**Rule:**
- **Predictor:** the first half hour (09:30–10:00) or the day so far (09:30–15:30).
- **Position:** the last half hour (15:30–16:00), in the predictor's direction.
- **Filter:** always, or only when the predictor's size exceeds its 20-day median.

**Size:** 2 × 2 × 2 = **8 variants.**

**Costs:** 1.5 bps.

**Split:** discovery 2014 → 2019; validation 2020 → 2026-08.

**Prediction:** positive for US100 (leveraged-ETF rebalancing, the N3 mechanism); weak for US500 (round 1's IM-01).

### A32 (2026-09-27, round 18: USDJPY intraday-momentum confirmation on unseen data; volatility-scaled reversal book; RB in the SQX build; written before any of these results was computed)

#### JY — confirmatory test of the USDJPY intraday-momentum lead

**The lead:**
- Round 11, family R: USDJPY|LDNAM|BRK|END, per-market SPA 0.009.
- Round 17, family FM: USDJPY noise area, 6/6 variants positive in 2010–16 and 2017–26.

Both used 2010 → only.

**Unseen test data:**
- USDJPY, 2003-01 → 2009-12;
- six JPY crosses never run with these rules: EURJPY, GBPJPY, AUDJPY, CADJPY, CHFJPY, NZDJPY, 2008 → 2026-09.

**Rules, exactly as in A24 (family R) and A31 (family FM):**
- **Range rules (8):** {Asian range traded 07–12 London, London-morning range traded 13–16} × {breakout, fade} × {window end, 1× range target}.
- **Noise-area rules (6):** London open 08:00, marks 08:30–20:00, flat 20:30 London; lookback {7, 14, 28} × band {1.0, 1.25}.

**Costs:** USDJPY 1.0 bps; JPY crosses 2.0 bps per trade.

**Primary hypotheses** (one-sided mean > 0, HAC t with lag 5, Holm over the four):

| | Rule | Data |
|---|---|---|
| H1 | LDNAM\|BRK\|END | USDJPY 2003–09 |
| H2 | NOISE L14 b1.25 | USDJPY 2003–09 |
| H3 | LDNAM\|BRK\|END, equal-weight average across the 6 crosses | Crosses 2008–26 |
| H4 | NOISE L14 b1.25, equal-weight average across the 6 crosses | Crosses 2008–26 |

**Secondary:** each 14-rule grid under the A22 battery, on USDJPY 2003–09 and on the crosses (SPA over the grid).

**Verdict:**
- **CONFIRMED EDGE** if H1 or H2 passes Holm, and H3 or H4 has a positive mean.
- **WEAK** if a primary test passes without the other condition.
- **NOT CONFIRMED** otherwise.

#### VS — volatility-scaled reversal book (prop suitability)

**Book:** the family A + RB US ensemble (SPY, QQQ, DIA, IWM; Yahoo daily, 2007-07 → 2026-08).

**Sizing:** every trade's notional is scaled by 1% ÷ (the index's 20-day realized daily volatility at entry), capped at 2×. That is money-management only; the signals don't change.

**Compared with fixed size on:**
- Sharpe;
- worst day;
- max drawdown;
- an FTMO 2-Step lifecycle (A25 method, close-only path, fixed 1× and CPPI k = 10), both books scaled to 1% daily volatility on 2007–2012.

**Decision:** recommend vol-scaling if it improves the worst day and the zero-edge-adjusted pass rate without cutting the Sharpe by more than 20%.

#### RBc — RB signals in the SQX build

The 12 RB signals × 3 exits (X1, XU, XS5) × 3 filters, run in R1 implementation (c) (M5, 15:55) on HistData US500, US100 and JP225, 2014 → 2026-08.

**Report:** the share of variants positive and the ensemble Sharpe, against RB's daily-close version over the same window.

**Expected:** 80–90% of the daily-close result, as family A kept under R1.

**DSR count:** 13,641 + 28 (JY grids: 14 on USDJPY 2003–09, 14 on the crosses) = 13,669. VS and RBc are implementability measurements.

### A33 (2026-09-27, round 19: Tokyo-fix Gotobi flows and central-bank-day currency premia; written before any of these results was computed)

**Why these two:**
- FX is the user's main market, and 18 rounds found no FX edge.
- Two documented mechanisms, one a customer-flow effect and one a risk premium, have not been tested here.
- Both are time-and-date rules that SQX can express.

**GT: the Tokyo fix on Gotobi days** (Ito & Yamada, NBER WP 22820, 2016; *JIMF* 2017; sample 1999–2013).
- **Mechanism:** Japanese importers buy dollars for settlement on the 5th, 10th, 15th, 20th, 25th and 30th ("Gotobi") and on the month's last business day. Banks buy ahead of their 09:55 JST fixing, so USD/JPY rises into 09:55 and partly reverses after.
- **Published size:** their 5-minute long / 5-minute short switch at 09:55 earned 1.8 bps on average over 15 years, more on 5th/10th days and at month-end.
- **Not tested before:** round 1's FX-01 tested the dollar's Tokyo leg on all days across nine pairs. USDJPY on Gotobi days was not tested.

**FD: central-bank announcement days** (Mueller, Tahbaz-Salehi & Vedolin, *JF* 2017; sample 1994–2013).
- **FOMC days:** short USD against the G10 (DOL) earned 10.8 bps per scheduled FOMC day. The high-interest-rate portfolio earned 14.5 bps, against 1.7 bps on other days.
- **BoJ days:** the pattern is "virtually identical" against JPY (1998–2013).

**Data:**
- **Minute data (HistData 1-minute):**
  - USDJPY and the majors 2003 → 2026-09-18 (NZDUSD 2005 →);
  - EURJPY and the JPY crosses 2008 →;
  - XAUUSD 2009 →.
- **Calendars:**
  - Japanese national holidays (python `holidays` 0.105), plus the bank holidays Dec 31 and Jan 2–3;
  - scheduled FOMC decision days (`data_calendar.fomc_days`);
  - BoJ decision days, from the file dates of the statements on the BoJ's past-meetings page. The extraordinary 2020-05-22 meeting is excluded; the rescheduled 2020-03-16 meeting is kept.
- **Rates:** FRED OECD 3-month interbank rates (monthly, `IR3TIB01xxM156N`), for the rate sort.

**Primary sample, after both papers' samples:** 2014-01-01 → 2026-09-18. The replication sample 2003–2013 is secondary.

#### GT definitions

- **Tokyo business day:** Mon–Fri, not a Japanese holiday or bank holiday.
- **Gotobi day:** in each month, the 5th, 10th, 15th, 20th, 25th and 30th, each moved to the preceding business day if it is not one, plus the month's last business day.
- **Windows** (Asia/Tokyo; Japan has no DST):
  - **PRE:** long USDJPY 09:00 → 09:55 JST;
  - **POST:** short USDJPY 09:55 → 10:55 JST.
- **Prices:** the close of the bar ending at the minute (`data_minutes.price_at`, tolerance 2 minutes). Both windows are outside the NY rollover zone all year.
- **Cost per trade:** USDJPY 1.0 bps, EURJPY 2.0 bps (as in rounds 11–18).

**GT primary hypotheses** (one-sided mean > 0 net of cost, HAC t with lag 5; Holm over G1 and G3):

| | Rule | Days | Data |
|---|---|---|---|
| G1 | PRE, long | Gotobi | USDJPY 2014–26 |
| G3 | POST, short | Gotobi | USDJPY 2014–26 |
| G2 (mechanism, not in Holm) | PRE gross mean, Gotobi minus other business days (Welch t) | — | USDJPY 2014–26 |

**GT verdict:**
- **EDGE:** G1 or G3 passes Holm at 5%, and its net mean is positive in both 2014–19 and 2020–26.
- **WEAK:** a primary passes Holm without both halves positive, or its gross mean has one-sided p < 0.05 while the net fails.
- **NO EDGE** otherwise.

**GT secondary grid (42 variants).**
- **Battery:** daily P&L (0 on days without a trade), split 2020-01-01, walk-forward from 2016, raw benchmark (intraday windows).
- **Pairs:** USDJPY, EURJPY.
- **Windows (7):**
  - PRE 09:00–09:55;
  - PRE-late 09:30–09:55;
  - PRE-early 08:30–09:55 (it starts at 18:30 NY in US winter: disclosed);
  - POST 09:55–10:00;
  - POST 09:55–10:55;
  - POST 09:55–12:00;
  - POST 09:55–15:00.
- **Day sets (3):** all Gotobi days; 5/10 days that are not the month's last business day; the month's last business day only.
- **Reported, not in the grid:** the same windows on non-Gotobi days (control), per-year means, Fridays vs other days, and the 2003–2013 replication.

#### FD definitions

- **Windows (NY time):**
  - **DAY:** 16:45 NY on the previous weekday → 16:45 NY on the announcement day. For FOMC this is the NY date of the statement. For BoJ it is the Tokyo decision date, whose NY window (16:45 of the day before) contains the Tokyo decision.
  - **PRE:** 16:45 prior → 13:55 NY.
  - **POST:** 13:55 → 16:45 NY (FOMC only; the statement is at 14:00).
- **Returns:** spot, long the foreign currency. The swap is not modelled (≤ ±2 bps a day; disclosed).
- **Portfolios:**
  - **DOL:** equal-weight long EUR, GBP, JPY, AUD, CAD, CHF, NZD against USD.
  - **HY:** equal-weight long the three of those seven with the highest 3-month rate at the previous month-end (last value carried forward), against USD.
  - **JPYB:** equal-weight long USD, EUR, GBP, AUD, CAD, CHF, NZD against JPY (USDJPY and six crosses).
  - **GOLD:** long XAUUSD (secondary only).
- **Cost:** 1.0 bp per trade on the majors, 2.0 on the crosses, 2.5 on gold. A basket's cost is the average of its legs.

**FD primary hypotheses** (one-sided mean > 0 net, t on event returns; Holm over F1–F3):

| | Portfolio and window | Days | Data |
|---|---|---|---|
| F1 | DOL, DAY | Scheduled FOMC | 2014–26 |
| F2 | HY, DAY | Scheduled FOMC | 2014–26 |
| F3 | JPYB, DAY | BoJ decision | 2014–26 |

**Mechanism** (reported, not in Holm): the announcement-day mean minus the other-weekday mean (Welch t).

**FD verdict:**
- **EDGE:** one of F1–F3 passes Holm, and its mean is positive in both 2014–19 and 2020–26.
- **WEAK:** a primary has one-sided p < 0.05 but misses Holm or the halves.
- **NO EDGE** otherwise.

**Power, stated before running.** There are about 100 events per test. With DOL's σ ≈ 45 bps a day, the standard error is ≈ 4.5 bps. That gives about 65% power at the published 10.8 bps and about 20% at half of it. A null here can't rule out a smaller effect.

**FD secondary grid (11 variants):**
- **FOMC:** {DOL, HY, GOLD} × {DAY, PRE, POST};
- **BoJ:** JPYB DAY and DOL DAY.

It uses the same battery settings as GT, plus the 2003–2013 replication.

**DSR count:** 13,669 + 42 + 11 = 13,722.

### A34 (2026-09-27, round 20: the Gotobi effect on unseen JPY-cross data; exit and stop choices for the build; written before any of these data were downloaded)

**Why:** round 19's GT passed its pre-registered test on USDJPY. Its breadth across the JPY crosses (2014–26) and its better late exits were found post hoc. HistData serves EURJPY, GBPJPY, AUDJPY and CHFJPY from 2002, CADJPY from 2007 and NZDJPY from 2006. This project has never downloaded those years, so they are unseen.
- **Coverage of the period:** Ito & Yamada's sample (1999–2013) covers these years, but it studied USDJPY and EURJPY only.
- **So this is a confirmation of breadth,** not a post-publication test.

**Data:** HistData 1-minute, 2002-01 → 2007-12:
- EURJPY, GBPJPY, AUDJPY, CHFJPY;
- CADJPY 2007;
- NZDJPY 2006–07.

The rules are round 19's GT definitions exactly (Gotobi days, Tokyo business days, `price_at` tolerance 2). A day counts only if both window prices exist.

**The basket:** the equal-weight average of the crosses with both prices that day. A day needs at least 3 crosses.

#### GC — confirmation (one-sided; HAC t lag 5 unless stated; Holm over C1–C3)

| | Test | Data |
|---|---|---|
| C1 | Basket, short 09:55 → 10:55 JST on Gotobi days, gross mean > 0 | Crosses 2002–07 |
| C2 | Basket, the same window, Gotobi minus non-Gotobi business days, gross (Welch t) | Crosses 2002–07 |
| C3 | EURJPY alone, short 09:55 → 10:55 on Gotobi days, net of 1 bp > 0 | EURJPY 2002–07 |

**Verdict:**
- **CONFIRMED:** C1 and C2 both pass Holm at 5%.
- **PARTIAL:** exactly one of them passes.
- **NOT CONFIRMED:** neither passes.

C3 decides whether EURJPY may join USDJPY in the build (it must pass Holm).

**Also reported:**
- each cross alone (gross, Gotobi and other days);
- month-end vs other Gotobi days;
- the pre-fix long 09:00 → 09:55.

#### GX — exit time for the build (decided on the unseen basket)

- **Exits compared** (entry 09:55): 10:25, 10:55 (pre-registered in A33), 11:30 (best post hoc on 2014–26), 12:00 and 15:00 JST.
- **Measure:** per-trade mean ÷ standard deviation on Gotobi days (the basket, 2002–07).
- **Decision:** switch the build's exit from 10:55 to 11:30 only if 11:30 has the higher mean ÷ σ and its gross mean has t ≥ 2. Otherwise keep 10:55. The other exits are reported, not chosen.

#### GS — disaster stop for the build (implementation measurement; USDJPY minute path 2014–26, data already seen)

- **Stops:** a buy stop at entry + {20, 30, 50, 80} bps, filled at the stop level. When a minute bar's high crosses it, the fill is the stop plus the bar's excess over the stop.
- **Report** for each stop: net mean (1 bp), the worst trade and the share of trades stopped.
- **Decision:** use the tightest stop that keeps ≥ 95% of the no-stop net mean. If none does, use no stop, and let the EA guard cap the loss.

**DSR count:** 13,722 + 3 (C1–C3) + 5 (GX exits) = 13,730. GS is an implementation measurement.

#### A34a (2026-09-27, data-integrity amendment after the first A34 run; written before the corrected run)

**What happened:** the first A34 run returned **NOT CONFIRMED**. C1 was +266 bps (σ 5,238 bps) and C2 +275 bps, both n.s. The cause was one corrupt file.
- **The file:** HistData's AUDJPY 2005 file mixes in prices of other instruments (0.67, 105, 135 next to AUDJPY's ~82), with **12,319** one-minute moves beyond ±3%.
- **Every other cross-year** has 0–4 such minutes, all outside the trading windows.
- **C3** (EURJPY alone) was unaffected: +1.80 bps net, t 3.10, Holm 0.003.

**Rule, blind to the effect being tested:**
- Drop a symbol-year whose minute closes have more than 100 one-minute log moves beyond ±3%. Here that drops only AUDJPY 2005.
- Drop a window return beyond ±5%. The largest genuine move in round 19 was 2.4%, on the 2011-03-18 intervention.

**Re-run:** C1–C3 and GX with the rule. The verdicts of both runs are reported. GS is unaffected (USDJPY 2014–26).

### A35 (2026-09-27, round 21: round-number barriers in FX and gold; the Shanghai Gold Benchmark; written before any of these results was computed)

**Why:** the user asked for more FX and metals edges. Round 19 showed that scheduled customer flows can survive where price patterns don't. Two flow and microstructure mechanisms with published evidence have not been tested here:

- **RN, round-number order clustering:**
  - **FX** (Osler, *JF* 2003; *JIMF* 2005; order data 1996–98): take-profit orders cluster at round numbers, so trends reverse there more often (59.3% vs 54.8% at arbitrary levels for dollar–mark). Stop-loss orders cluster just beyond them, so moves accelerate after a crossing.
  - **Gold** (Aggarwal & Lucey, *RFE* 2007): prices ending in 0 and 00 act as barriers.
- **SG, the Shanghai Gold Benchmark:** a physical-delivery auction at 10:15 and 14:15 Beijing time, launched on 2016-04-19. China is a large net buyer. If dealers buy ahead of the auction, gold would rise into it and give some back after, as USDJPY does at the Tokyo fix. The launch date is a natural experiment: the pattern should be absent before it.

**Data:** HistData 1-minute. EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF 2003 → 2026-09; NZDUSD 2005 →; XAUUSD 2009 →; XAGUSD 2010 → (secondary). All of these are post-sample for both RN papers.

#### RN definitions

- **Sessions:**
  - **FX:** events 07:00–20:00 London;
  - **gold:** events 01:00–20:00 London;
  - **outcomes:** followed for up to 120 minutes, never past 20:45 London.
- **Level grids:**
  - **FX:** Round50 = multiples of 50 pips (1 pip = 0.0001; 0.01 for JPY); Round100 = multiples of 100 pips; Arb50 = the 50-pip grid offset by 17 and by 33 pips (both offsets pooled).
  - **Gold:** Round10 = multiples of $10; Round50 = multiples of $50; Arb10 = the $10 grid offset by $3.3 and by $6.7.
- **Touch event:** the first minute in the session whose range contains level L. The approach side is the previous minute's close. There is at most one event per level, side and session.
- **k (distance)** = 10 bps of L. The **penetration trigger** p = 3 bps.
- **Reversal first:** after the touch, the price reaches L ∓ k (back to the approach side) before L ± k (through the level). The touch minute counts only if it already reached L ± k (then penetration first). A minute that reaches both is "tie": left out of frequency tests and booked as the loss in the P&L of either rule.
- **Fade rule:**
  - **Entry:** at the touch, a limit order at L against the approach (sell from below, buy from above).
  - **Exits:** take-profit k and stop k from L; otherwise exit at market after 120 minutes (or 20:45 London).
- **Follow rule:**
  - **Entry:** at the first minute in the session that trades L ± p beyond the level from the approach side, enter in the direction of the crossing at L ± p.
  - **Exits:** take-profit and stop k from the entry, with the same timeout.
- **Costs per trade:** FX 1.0 bp; gold 2.5 bps; silver 5 bps.

**RN primary hypotheses** (one-sided; Holm over RN1–RN4):

| | Test | Data |
|---|---|---|
| RN1 | FX pooled (7 pairs): reversal-first frequency at Round50 minus Arb50 (decided events), day-block bootstrap | 2003–26 |
| RN2 | XAUUSD: the same, Round10 minus Arb10 | 2009–26 |
| RN3 | FX pooled: fade at Round50, net P&L > 0 (events summed per day, HAC t lag 5) | 2003–26 |
| RN4 | XAUUSD: fade at Round10, net P&L > 0 (daily, HAC) | 2009–26 |

**RN verdict:**
- **EDGE:** RN3 or RN4 passes Holm, and its net mean is positive in both halves (FX 2003–14 / 2015–26; gold 2009–17 / 2018–26).
- **MECHANISM ONLY:** RN1 or RN2 passes Holm, but neither rule does.
- **NO EDGE** otherwise.

**RN secondary grid** (64 variants for the A22 battery; daily P&L, split 2016-01-01, walk-forward from 2008):
- 8 instruments (7 FX + gold) × {fade, follow} × {Round50, Round100 (gold: Round10, Round50)} × k ∈ {10, 20 bps}.

**Also reported:**
- Osler's second prediction: follow-rule continuation frequency at round minus arbitrary levels;
- per pair;
- approach from below vs above;
- silver (XAGUSD, $0.50 grid).

#### SG definitions

- **SGE days:** weekdays that are not mainland-China holidays (python `holidays` China).
- **Windows** (Asia/Shanghai = UTC + 8, no DST):
  - AM PRE: long 09:15 → 10:15;
  - AM POST: short 10:15 → 11:15;
  - PM PRE: long 13:30 → 14:15;
  - PM POST: short 14:15 → 15:15.
- **PRE** = AM PRE + PM PRE and **POST** = AM POST + PM POST, per day (two trades each).
- **Periods:** pre-launch 2009-01 → 2016-04-18; post-launch 2016-04-19 → 2026-09-18.

**SG primary hypotheses** (one-sided; Holm over SG1–SG3):

| | Test |
|---|---|
| SG1 | PRE, post-launch, gross mean > 0 (HAC) |
| SG2 | POST, post-launch, gross mean > 0 (HAC) |
| SG3 | Natural experiment: (PRE + POST) post-launch minus pre-launch > 0 (Welch) |

**SG verdict:**
- **EDGE:** SG1 or SG2 passes Holm, its mean net of 2.5 bps per trade is positive, and SG3 passes Holm.
- **FLOW, NOT TRADEABLE:** SG1 or SG2 passes Holm, but the net mean is ≤ 0 or SG3 fails.
- **NO EDGE** otherwise.

**SG secondary:**
- each auction on its own;
- XAGUSD in the same windows;
- the same windows on mainland holidays that are weekdays (a placebo: no auction).

The 8 variants ({AM, PM} × {PRE, POST} × {XAU, XAG}) go through the battery.

**DSR count:** 13,730 + 64 + 8 = 13,802.

#### A35a (2026-09-27, data-integrity amendment after the first A35 run; written before the corrected run)

**What happened:** the first RN run was dominated by corrupt bars. One AUDUSD bar on 2004-11-24 has an open and high of 39.82 (the price was 0.79). It generated 7,806 fake level touches in a single day, all of them "stopped". There are similar single bars elsewhere:
- EURJPY 2004 lows at 67.5 (price ~135);
- USDCHF 2004 lows at 0.64 (price ~1.28);
- NZDUSD 2008-12-23 at 2.17.

The round-20 close-based rule (A34a) doesn't see them: their closes are normal, or they are single bars.

**Rule, blind to the effect being tested** ([data_audit.py](data_audit.py), [results/data_audit_spikes.json](results/data_audit_spikes.json)):
- **Spike bar:** a bar whose open, high, low or close is more than 1% (FX) or 2% (metals and indices) from the median close of the two bars before and the two after, when those four neighbours agree within half that limit.
- **Drop** spike bars before building events (RN) and window prices (SG).
- **Scale:** across the 39 cached files it flags 0–16 bars per symbol, plus 76 in the already excluded AUDJPY 2005. Some flagged bars may be genuine flash moves (2015-01-15 SNB, 2016-02-11); dropping them is conservative for both rules.

**Re-run:** RN and SG in full. The first-run files are kept as `round21_rn_first_run.json` and `round21_sg_first_run.json`, and both verdicts are reported.

### A36 (2026-09-27, round 22: gold and silver seasonality; the Asian bid in gold; a holiday check of the Tokyo-fix mechanism; written before any of these results was computed)

**Why:** the user asked for more FX and metals edges. Round 21's two flow tests failed. Round 22 tests two demand-driven effects in metals and one mechanism prediction of the round-19/20 FX edge.

**All minute data:** audited spike bars are dropped (A35a). Costs are gold 2.5 bps and silver 5 bps per trade, as before.

#### GS — the autumn effect in gold (Baur, *RIBAF* 2013; sample 1980–2010)

- **Published result:** September and November were the only months with significantly positive gold returns, which Baur links to Indian wedding-season demand and pre-Halloween hedging.
- **Data:** XAUUSD daily bars at 16:45 NY from HistData (`run_round13.fx_bars`). A month's return runs from the last weekday of the previous month to the month's last weekday.
- **Sample:** after the paper, 2011-01 → 2026-08 (Sep and Nov 2011–2025, 30 months).
- **Net:** minus 2.5 bps per trade and a month of long financing: the US 3-month rate (FRED `IR3TIB01USM156N`, previous month) plus 2%/yr mark-up.

| | Test (one-sided; Holm over GS1–GS2) |
|---|---|
| GS1 | Mean net return of Sep and Nov months > 0 (t on the 30 months) |
| GS2 | Gross mean of Sep/Nov minus the other months > 0 (Welch) |

**GS verdict:**
- **EDGE:** GS1 passes Holm and both the Sep and the Nov means are positive.
- **SEASONAL, NOT TRADEABLE:** GS2 passes but GS1 doesn't.
- **NO EDGE** otherwise.

**GS secondary:**
- all twelve months;
- XAGUSD (2011 →);
- gold's turn of the month (the last trading day and the first 3, daily, net).

#### AB — the Asian bid in gold after New York sell-offs

- **Mechanism:** Chinese and Indian physical buyers are price-sensitive. A sharp fall in the NY session draws their buying in the next Asian session.
- **NY-session return:** XAUUSD 08:30 → 16:00 New York, with σ20 = the standard deviation of the previous 20 NY-session returns.
- **Signal:** the NY-session return < −1.0 σ20.
- **Trade:** long 09:00 → 15:00 Beijing on the next Beijing weekday. The session is outside the NY rollover all year.

| | Test (one-sided; Holm over AB1–AB2) |
|---|---|
| AB1 | Long Asia after a signal, net mean > 0 (HAC t, lag 5), 2009–2026 |
| AB2 | Asian-session gross mean after signals minus on the other days (Welch) |

**AB verdict:**
- **EDGE:** AB1 passes Holm, and the net mean is positive in both 2009–17 and 2018–26.
- **DEMAND EFFECT, NOT TRADEABLE:** AB2 passes but AB1 doesn't.
- **NO EDGE** otherwise.

**AB secondary grid** (12 variants for the battery; split 2018-01-01; walk-forward from 2011):
- {XAUUSD, XAGUSD} × {signal < −1.0 σ, < −1.5 σ, > +1.0 σ traded short (the symmetric case)} × {exit 15:00, 11:30 Beijing}.

#### JH — the Tokyo fix on Japanese holidays (mechanism check of GT; it doesn't change the GT verdict)

- **Prediction:** with no fix on a Japanese national holiday, the fix pattern should vanish.
- **Holiday days:** weekday national holidays, 2003–2026, excluding the Dec 31 and Jan 1–3 bank holidays (FX trades thinly then).
- **Comparison:** non-holiday, non-Gotobi business days (the "all days" pattern of round 19).
- **Windows:** PRE (09:00 → 09:55 JST) and POST (short 09:55 → 10:55), gross.

| | Test (one-sided, Welch) |
|---|---|
| J1 | USDJPY POST: holidays minus normal days < 0 |
| J2 | USDJPY PRE: holidays minus normal days < 0 |

EURJPY is reported the same way (2008 →).

**DSR count:** 13,802 + 4 (GS: Sep and Nov × gold and silver) + 12 (AB grid) + 4 (JH) = 13,822.

### A37 (2026-09-27, round 23: the Japanese-holiday Tokyo-morning effect on unseen cross data, and the day after a holiday; written before any of these results was computed)

**Why:** round 22 found, in a pre-registered mechanism test (J2), that USDJPY's pre-fix rise turns into a fall on Japanese holidays: −2.69 bps from 09:00 to 09:55 JST (t −3.5). EURJPY showed the same (−2.13). A short on those mornings is a post hoc rule. It needs data not used for it: the 2002–07 JPY-cross files, which round 20 used only for Gotobi days.

A second prediction follows from the same flow story. Payments that fall due on a holiday but aren't on a Gotobi date are often settled on the next business day. The first business day after a holiday should then carry extra importer demand and look like a Gotobi day.

**Data:**
- **Unseen crosses:** HistData EURJPY, GBPJPY, CHFJPY, AUDJPY (2005 excluded per A34a), 2002–07, plus NZDJPY 2006–07 and CADJPY 2007. Spike bars are dropped (A35a).
- **USDJPY 2014 → 2026-09**, for the day-after test only; its day-after days were not examined before.

**Days:**
- **Holiday:** a weekday Japanese national holiday, excluding Dec 31 and Jan 1–3.
- **Day after:** the first Tokyo business day after one or more weekday holidays, if it is not itself a Gotobi day.
- **Normal:** a Tokyo business day that is neither Gotobi, nor a holiday, nor a day after.

**Windows** (JST, as in A33): PRE long 09:00 → 09:55; POST short 09:55 → 10:55; gross returns. The basket is the equal-weight average of the crosses with both prices that day (≥ 3).

**Primary hypotheses** (one-sided; Holm over H1, H2, D1, D2):

| | Test | Data |
|---|---|---|
| H1 | Basket PRE on holidays < 0 (HAC t, lag 5) | Crosses 2002–07 |
| H2 | Basket PRE, holidays minus normal days < 0 (Welch) | Crosses 2002–07 |
| D1 | USDJPY POST, day-after minus normal days > 0 (Welch) | USDJPY 2014–26 |
| D2 | Basket POST, day-after minus normal days > 0 (Welch) | Crosses 2002–07 |

**Verdicts:**
- **HOLIDAY LEG CONFIRMED** if H1 and H2 pass Holm. The GT build may then add "short USDJPY 09:00 → 09:55 JST on Japanese holidays", subject to its net mean at 1 bp on USDJPY 2003–26 being positive (reported).
- **DAY-AFTER EFFECT** if D1 and D2 pass Holm. The day-after days may then join the GT day set, subject to a net POST mean on USDJPY 2014–26 above 0 at 1 bp (reported).
- Otherwise each is **NOT CONFIRMED**.

**Also reported:** each cross alone, and the day-after PRE window.

**DSR count:** 13,822 + 4 = 13,826.

### A38 (2026-09-27, round 24: PBoC-fix reaction momentum in AUD; gold-silver relative value; festival gold demand; written before any of these results was computed)

**Why:** the user asked for more FX and metals edges. Three mechanisms from today's literature sweep are testable with data already on hand. All minute and daily series drop audited spike bars (A35a); AUDJPY-style corrupt years per A34a.

#### PB — the PBoC fix as an information event (AUD spillover)

- **Mechanism:** the PBoC publishes the USD/CNY central parity at 09:15 Beijing. It moves commodity and Asian currencies; since the 2015-08-11 reform the fix carries daily news. If the surprise diffuses slowly, the first reaction should continue.
- **Rule:** jump = AUDUSD return 09:10 → 09:20 Beijing (bar closes). Enter at 09:20 in the direction of sign(jump); exit 10:15 Beijing. Cost 1 bp per trade.
- **Days:** weekdays that are not mainland-China holidays (fix days). **Reform split:** pre 2005-01 → 2015-08-10; post 2015-08-12 → 2026-09-18.

**Primary hypotheses** (one-sided; Holm over P1–P3):

| | Test |
|---|---|
| P1 | AUDUSD net mean > 0 on post-reform fix days (HAC t, lag 5) |
| P2 | Post-reform gross mean minus pre-reform gross mean > 0 (Welch): the reform created the signal |
| P3 | Post-reform fix days minus weekday China holidays (no fix), gross (Welch) |

**Verdict:**
- **EDGE:** P1 passes Holm and the net mean is positive in both 2015-08 → 2020 and 2021 → 2026.
- **MECHANISM ONLY:** P2 or P3 passes without P1.
- **NO EDGE** otherwise.

**Grid (12 variants for the battery;** split 2021-01-01, walk-forward from 2017): {AUDUSD, NZDUSD, USDJPY} × jump filter {all days, |jump| > 1 σ of the last 20 jumps} × exit {10:15, 11:15}.

#### RV — gold-silver relative value

- **Mechanism:** partial cointegration of gold and silver (Escribano & Granger 1998; Yaya et al. 2021); the ratio mean-reverts.
- **Data:** daily 16:45-NY bars from minute data (`fx_bars`), XAUUSD and XAGUSD, common days 2010 → 2026-09.
- **Signal:** z = (log(XAU/XAG) − rolling L-day mean) ÷ rolling L-day sd, using closes through the signal day.
- **Trade:** at z > k, long silver and short gold from the next close (spread return = silver return − gold return, half notional each leg so 1 unit of spread = 0.5 long + 0.5 short); at z < −k the mirror. **Exit** when |z| < 0.5 or after 20 trading days. One position at a time per side.
- **Costs:** 7.5 bps per spread entry and 7.5 per exit (half of gold 2.5 + silver 5, both legs); financing 4%/yr ÷ 365 per calendar day held (2% mark-up on each leg).

**Primary hypotheses** (Holm over RV1–RV2), on L = 60, k = 2.0, both sides pooled:

| | Test |
|---|---|
| RV1 | Net mean per trade > 0 (t over trades) |
| RV2 | Gross mean per trade > 0 |

**Verdict:**
- **EDGE:** RV1 passes Holm and the net mean is positive in both 2010–17 and 2018–26.
- **REVERSION, NOT TRADEABLE:** RV2 passes without RV1.
- **NO EDGE** otherwise.

**Grid (18 variants for the battery;** split 2019-01-01, walk-forward from 2013): L {30, 60, 120} × k {1.5, 2.0, 2.5} × exit {|z| < 0.5, 20 days}.

#### FG — festival gold demand (Dhanteras/Diwali)

- **Mechanism:** Indian festival gold buying peaks at Dhanteras (2 days before Diwali). Wholesalers stock up in the weeks before. Diwali dates from python `holidays` India.
- **Rule:** long XAUUSD for the 15 weekdays ending 2 calendar days before Diwali, 2011 → 2025 (15 events). Net of 2.5 bps and financing (US 3-month + 2%, ~21 calendar days).
- **F1 (single test):** net mean per event > 0 (t over the 15 events).
- **Verdict: EDGE** only if F1 has p < 0.05 and both 2011–17 and 2018–25 means are positive; otherwise **NO EDGE**. Power is low (n = 15): a null is weak evidence.
- **Also reported:** the same window gross, the 15 days after Diwali, and Akshaya-free months as context.

**DSR count:** 13,826 + 12 + 18 + 1 = 13,857.

### A39 (2026-09-27, round 25: COMEX metals option expiry; Japanese fiscal year-end; written before any of these results was computed)

**Why:** two precise calendar claims from the practitioner literature, both SQX-expressible, neither tested here. Daily bars are 16:45-NY closes from minute data with spike bars dropped (`run_round24.rv_bars`).

#### OX — COMEX gold and silver option expiry

- **Claim:** monthly COMEX options expire **4 business days before month-end**; option writers "manage" the price into expiry, so metals are weak into the expiry day and rebound after.
- **OpEx day:** the 4th-to-last US business day of each month (weekdays that are not US federal holidays; approximation of the CME calendar, disclosed). 2010-01 → 2026-08, ~200 events.
- **Windows** (16:45-NY closes): INTO = close of the 3rd trading day before OpEx → OpEx close; AFTER = OpEx close → the 3rd trading day after.

**Primary hypotheses** (one-sided; Holm over OX1–OX2), gold:

| | Test |
|---|---|
| OX1 | Gold INTO mean < 0 (t over events) |
| OX2 | Gold AFTER mean > 0 (t over events) |

**Verdict:**
- **EDGE:** either passes Holm, its matching trade nets > 0 after 2.5 bps + financing, and both 2010–17 and 2018–26 means have the predicted sign.
- **NO EDGE** otherwise.

**Grid (8 variants for the battery;** split 2019-01-01, walk-forward from 2013): {gold, silver} × {short INTO, long AFTER} × {3-day, 5-day} windows, net of costs.

#### JM — the Japanese fiscal year-end

- **Claim:** corporate repatriation into the March 31 fiscal year-end strengthens the yen in late March; flows reverse in early April.
- **JM1:** short USDJPY over the last 5 Tokyo business days of March (enter at the 6th-to-last close, exit at the March-end close), 2003–2026, net of 1 bp. Mean > 0 for the short (t over 24 events).
- **JM2:** long USDJPY over the first 5 Tokyo business days of April, net of 1 bp, mean > 0.
- Holm over JM1–JM2. **EDGE** only if one passes with both halves (2003–14 / 2015–26) of the predicted sign; otherwise **NO EDGE**. n = 24 per test: low power, and a null is weak evidence.

**DSR count:** 13,857 + 8 + 2 = 13,867.

### A40 (2026-09-27, round 26: US→overseas daily spillover on FTMO index CFDs; macro-print reaction momentum on US indices; written before any of these results was computed)

**Why:** the user asked for FTMO-tradable prop edges. Both families here are intraday on FTMO index CFDs — no overnight or weekend holds, so they fit every account type — and both enter ≥ 15 minutes after any news print, inside FTMO's news rule. Minute data with spike bars dropped (A35a).

#### SP — the US session traded in the next overseas session

- **Mechanism:** foreign markets historically continued the prior US move during their own next session (Becker, Finnerty & Gupta 1990 *JF*; Hamao, Masulis & Ng 1990 *RFS*). Everything since 1990 is post-sample.
- **Signal:** the most recent completed US session return, SPXUSD 15:55-NY close to 15:55-NY close, taken strictly before the target session's open.
- **Targets and sessions (local time):** JP225 09:00 → 15:00 Tokyo (15:30 from 2024-11-05); HK50 09:30 → 16:00 Hong Kong; AUS200 10:00 → 16:00 Sydney; GER40 09:00 → 17:30 Berlin; UK100 08:00 → 16:30 London. 2013 → 2026-09-18.
- **Trades:** LS = long the session (open to exit) when the US signal is positive, short when negative; LO = long-only (flat after a US down day).
- **Costs per side:** JP225 / HK50 / AUS200 3.0 bps; GER40 / UK100 1.5 bps. A day costs two sides.

**Primary hypotheses** (one-sided; Holm over SP1–SP2):

| | Test |
|---|---|
| SP1 | JP225 LS, open → close, net mean > 0 (HAC t, lag 5) |
| SP2 | Equal-weight {JP225, HK50, AUS200} LS, open → close, net mean > 0 |

**Verdict:** **EDGE** if SP1 or SP2 passes Holm and its net mean is positive in both 2013–19 and 2020–26; **NO EDGE** otherwise.

**Grid (20 variants for the battery;** split 2020-01-01, walk-forward from 2016): 5 markets × {LS, LO} × exit {session close, open + 4 hours}.

#### ED — reaction momentum after scheduled US prints, on US index CFDs

- **Mechanism:** slow incorporation of macro news; intraday momentum is strongest on announcement days (Gao et al. 2018; Zarattini et al.). Family U killed this for FX; indices were never tested.
- **Events, 2013 → 2026-09:** Employment-report days (`data_calendar.employment_days`, the BLS third-Friday rule — an approximation, disclosed) and scheduled FOMC statement days (`data_calendar.fomc_days`, exact).
- **Rule:** NFP: r = 08:30 → 08:45 NY close-to-close reaction; enter sign(r) at 08:45, exit 15:55. FOMC: r = 14:00 → 14:15 reaction; enter at 14:15, exit 15:55.
- **Costs:** 1.5 bps per side (3.0 per round trip). Entries 15 minutes after the print satisfy FTMO's 2-minute news restriction.

**Primary hypotheses** (one-sided; Holm over E1–E2), US500:

| | Test |
|---|---|
| E1 | NFP-day reaction momentum to 15:55, net mean > 0 (t over ~164 events) |
| E2 | FOMC-day reaction momentum to 15:55, net mean > 0 (t over ~109 events) |

**Verdict:** **EDGE** if E1 or E2 passes Holm and its net mean is positive in both 2013–19 and 2020–26; **NO EDGE** otherwise.

**Grid (8 variants for the battery;** split 2020-01-01, walk-forward from 2016): {US500, US100} × {NFP, FOMC} × exit {15:55, entry + 90 minutes}.

**DSR count:** 13,867 + 20 + 8 = 13,895.

### A41 (2026-09-27, round 27: the Japanese-holiday morning and the day after, confirmed on the five unexamined crosses; Toshin month-start flows; written before any of these results was computed)

**Why:** rounds 22–23 left two Japanese-calendar findings unresolved.
- **The holiday morning:** J2 (pre-registered, round 22) showed USDJPY's rise into the 09:55 fix *reverses* on Japanese holidays (−2.69 bps, t −3.5; difference from normal days t −5.5). EURJPY agreed. Round 23's confirmation on 2002–07 crosses had only 64 events (−0.79 bps, t −0.69): underpowered, not contradicting.
- **The unexamined data:** GBPJPY, CHFJPY, AUDJPY, CADJPY and NZDJPY holiday mornings, 2008 → 2026-09 (~230 events per cross). **Disclosure:** these crosses' 2014–26 Gotobi/other days appeared in a post hoc breadth check, but that check *excluded holidays entirely* (`d not in hol`) and mixed day-after days into "other"; the holiday-morning category has never been measured on them. EURJPY (used in round 22) and USDJPY (the source of the finding) are excluded from the primaries.
- **Mechanism:** with no fixing and Japanese corporates absent, the usual pre-fix demand is missing; the baseline Asian-hours yen strength shows undamped.

**Data:** HistData 1-minute, Tokyo clock, spike bars dropped (A35a); windows PRE = long 09:00 → 09:55 JST and POST = short 09:55 → 10:55, gross, |window| < 5%. Day types as round 23: HOL (weekday national holiday, excluding Dec 31 / Jan 1–3), AFTER (first business day after a weekday holiday, not Gotobi), GOTO, NORMAL. The basket is the equal-weight average over the five crosses with both prices (≥ 3).

#### HD — primary hypotheses (one-sided; Holm over H1–H3), crosses 2008 → 2026-09

| | Test |
|---|---|
| H1 | Basket PRE on HOL days: mean < 0 (HAC t, lag 5; ~230 events) |
| H2 | Basket PRE, HOL minus NORMAL < 0 (Welch) |
| H3 | Basket POST, AFTER minus NORMAL > 0 (Welch) |

**Verdicts:**
- **HOLIDAY LEG CONFIRMED** if H1 and H2 both pass Holm. The GT build then adds "short USDJPY 09:00 → 09:55 JST on Japanese weekday holidays", provided the build check — USDJPY 2003–26, net of 1 bp — is positive in both 2003–14 and 2015–26 (reported either way).
- **DAY-AFTER CONFIRMED** if H3 passes Holm. Day-after days then join the GT day set, provided USDJPY's POST net at 1 bp (2014–26) is positive (reported).
- Otherwise each is **NOT CONFIRMED**, and both leads are closed.

**Also reported:** each cross alone (PRE on HOL; POST on AFTER), the basket POST on HOL, and USDJPY by day type.

#### TS — Toshin month-start flows (exploratory primary, USDJPY 2003 → 2026)

- **Mechanism:** Japanese investment trusts settle new foreign-asset purchases in the first days of the month; the retail flow buys dollars at the fixing.
- **TS days:** the first 3 Tokyo business days of each month that are not HOL, AFTER or GOTO days.
- **T1:** USDJPY PRE on TS days, gross mean > 0 (HAC).
- **T2:** TS minus NORMAL (Welch) > 0.
- Holm over T1–T2. **CANDIDATE** (needing its own confirmation round on crosses before any build) if both pass and the net at 1 bp is positive in both 2003–14 and 2015–26; otherwise **NO EDGE**.
- **Descriptive:** days 1, 2, 3 separately; the POST window; the full session 09:00 → 15:00; EURJPY 2008 →.

**DSR count:** 13,895 + 3 (HD) + 2 (TS) + 10 (HD per-cross) + 8 (TS descriptive) = 13,918.

### A42 (2026-09-27, round 28: the Toshin month-start flow confirmed on the five crosses; written before any of these results was computed)

**Why:** round 27's TS test on USDJPY passed decisively (T1 +2.46 bps gross, t 3.99, Holm 0.00007; T2 vs normal days t 3.03) and is a CANDIDATE by its pre-registered rule. The confirmation set: the same 09:00 → 09:55 JST window on **GBPJPY, CHFJPY, AUDJPY, CADJPY and NZDJPY month-start days, 2008 → 2026-09** — a category never isolated on these crosses (round 27 measured their HOL days and their pooled NORMAL average only; TS days sat unexamined inside NORMAL).
- **Mechanism prediction:** Toshin flows buy foreign currencies broadly (historically concentrated in AUD and NZD uridashi/toshin products), so the crosses should rise on the same mornings.
- **Disclosure:** EURJPY's TS mornings were reported in round 27 as a descriptive (+0.50, t 0.67) and are excluded here.

**Definitions exactly as A41:** TS days = the first 3 Tokyo business days of the month that are not Gotobi, holiday or day-after days; PRE window long 09:00 → 09:55 JST; spike bars dropped; |window| < 5%; basket = equal weight over the crosses with prices (≥ 3).

**Primary hypotheses** (one-sided; Holm over C1–C2):

| | Test |
|---|---|
| C1 | Basket PRE on TS days, gross mean > 0 (HAC t, lag 5; ~620 events) |
| C2 | Basket PRE, TS days minus NORMAL days > 0 (Welch) |

**Verdict:**
- **CONFIRMED EDGE** if C1 and C2 both pass Holm at 5%. The build is then long USDJPY 09:00 → 09:55 JST on TS days at ≤ 1 bp round trip (net +1.46/trade full sample), with the same account and calendar block as GT; a prop simulation of the combined GT + TS calendar book follows (implementation measurement).
- **PARTIAL** if exactly one passes.
- **NOT CONFIRMED** otherwise, and the TS candidate is closed.

**Also reported:** each cross alone; AUDJPY + NZDJPY (the toshin currencies) vs the rest; 2008–14 vs 2015–26 halves; day-rank 1/2/3 on the basket.

**DSR count:** 13,918 + 2 = 13,920.

### A43 (2026-09-27, round 29: the ECB 14:15 CET fix, with the July 2016 publication reform as a natural experiment; written before any of these results was computed)

**Why:** the ECB's euro reference rates are set from a 14:15 CET snapshot (concertation ~14:10). Until mid-2016 they were published ~14:30 and widely used for corporate transactions; on **2016-07-01** the ECB moved publication to 16:00 CET explicitly to discourage transactional use, citing trading activity around the fixing. Fix-driven flow implies pre-fix pressure and post-fix reversal (Evans 2018 documents this at the WM/R fix); the reform should have attenuated it. This is the last untested benchmark fix on our calendar; the Tokyo (rounds 19–20) and London/WMR (rounds 1–3) fixes are done.

**Data:** HistData 1-minute — EURUSD 2003 →, EURJPY 2002 →, EURGBP 2008 → 2026-09-18; Berlin clock (the fix follows CET/CEST); spike bars dropped (A35a); |window| < 5%.

**Windows (Berlin time):** PRE = 13:45 → 14:15; POST = 14:15 → 15:00; POST30 = 14:15 → 14:45.

**Rules:** **R** (fix reversal): at 14:15 trade against sign(PRE), exit at the window end. **M** (momentum): with sign(PRE).

**Reform split:** pre = through 2016-06-30; post = 2016-07-01 →. **Costs per trade:** EURUSD 1.0 bp, EURGBP 1.5, EURJPY 2.0.

**Primary hypotheses** (one-sided; Holm over E1–E3):

| | Test |
|---|---|
| E1 | EURUSD R (exit 15:00), gross mean > 0, pre-reform (HAC t, lag 5) |
| E2 | EURUSD R: pre-reform mean minus post-reform mean > 0 (Welch) — the reform attenuated the pattern |
| E3 | Equal-weight 3-pair basket R, gross > 0, pre-reform |

**Verdicts:**
- **TRADEABLE EDGE** if E1 or E3 passes Holm **and** the post-reform net is positive in both 2016H2–2021 and 2022–26.
- **MECHANISM, REGIME OVER** if E1 or E3 passes and E2 passes, but the post-reform net fails.
- **NO EDGE** otherwise.

**Grid (12 variants for the battery;** split 2016-07-01, walk-forward from 2010): 3 pairs × {R, M} × exit {15:00, 14:45}.

**Also reported:** the mean |PRE| move pre vs post reform (activity check); month-end days separately; the POST window unconditioned.

**Implementation measurement (no DSR):** GT's month-end Gotobi days at fiscal quarter ends (Mar/Jun/Sep/Dec) vs other month-ends, USDJPY POST 2003–26 — sizing information for the GT build only.

**DSR count:** 13,920 + 3 + 12 = 13,935.

### A44 (2026-09-27, round 30: quarter-end settlement days beyond the Gotobi dates; written before any of these results was computed)

**Why:** round 29's implementation measurement showed the Tokyo-fix flow concentrates at fiscal quarter ends: month-end Gotobi days in Mar/Jun/Sep/Dec earn +6.90 bps on the post-fix short (t 7.3) against +2.71 at other month-ends. Corporate settlement at quarter end is not confined to the 5/10 dates, so the mechanism predicts elevated fix flow on the **other business days of the quarter-end week** — a day category never isolated on any series here (it has only ever been pooled inside NORMAL).

**Day set D:** the last 4 Tokyo business days of March, June, September and December that are **not** Gotobi days (so the month-end day, the 30th and a moved 25th are excluded), and not holidays or day-after days. Roughly 2–3 days per quarter month.

**Windows and data as A41:** POST = short USDJPY 09:55 → 10:55 JST (2003–26) and the five-cross basket (GBPJPY, CHFJPY, AUDJPY, CADJPY, NZDJPY; 2008–26); PRE reported. Spike bars dropped; |window| < 5%.

**Primary hypotheses** (one-sided; Holm over Q1–Q2):

| | Test |
|---|---|
| Q1 | USDJPY POST on D minus NORMAL days > 0 (Welch), 2003–26 |
| Q2 | Cross-basket POST on D minus NORMAL days > 0 (Welch), 2008–26 |

**Verdict:**
- **CONFIRMED EXPANSION** if Q1 and Q2 both pass Holm at 5% **and** USDJPY's POST net of 1 bp on D is positive in both 2003–14 and 2015–26. The GT build then adds day set D (~10 extra trades a year, same rule, same stop).
- **PARTIAL** if exactly one passes.
- **NOT CONFIRMED** otherwise, and the expansion is closed.

**Also reported:** the PRE window on D; USDJPY POST on D outright (HAC); Mar/Sep (Japanese fiscal half-year ends) vs Jun/Dec; the same set at non-quarter month ends (the placebo: last 4 non-Gotobi business days of the other eight months).

**DSR count:** 13,935 + 2 + 6 = 13,943.

### A45 (2026-09-27, round 31: Kaufman's noise hypothesis; Davey's monkey test; Pardo's walk-forward efficiency; written before any of these results was computed)

**Why:** the user asked for the practitioner canon (Pardo, Kaufman, Davey) to be brought to bear. Their methods are largely already embedded here (walk-forward validation, multi-market breadth, zero-edge benchmarks, mechanism-first design). What remains untested is Kaufman's *substantive* claim, and two of their validation instruments applied to our confirmed edges.

#### KN — Kaufman's noise hypothesis (Kaufman, *Trading Systems and Methods*: the efficiency ratio; noisier markets favor mean reversion)

- **Efficiency ratio:** ER(10)_t = |C_t − C_{t−10}| ÷ Σ|C_i − C_{i−1}| over the same 10 days. **Noise** = 1 − ER(10).
- **N1 (cross-sectional):** across the 12 indices with per-market REV results (SPY, QQQ, DIA, IWM, ^N225, ^GDAXI, ^FTSE, ^AXJO, ^FCHI, ^HSI, ^IBEX, ^STOXX50E; ^IXIC excluded as a QQQ duplicate), the Spearman rank correlation between mean noise (2013 → end, daily closes) and the market's **median raw validation Sharpe** (families A and J) is **positive**. p by 10,000 permutations, one-sided.
- **N2 (time-series):** for SPY and QQQ, the family-A ensemble's **timing value on active days** is higher when the market's own noise at the prior close is above its trailing 252-day median. Days pooled across the two markets; Welch, one-sided. Active day = any variant holds a position.
- Holm over N1–N2.
- **Outcome use:** documentation and market selection only. No filter is added to the build on this evidence alone (the round-15 lesson: condition sizing, don't drop trades).

#### Implementation measurements (no DSR):

- **MK — Davey's monkey test** on the three confirmed edges. For each: 2,000 monkey books that keep everything except the selection skill —
  - **REV (SPY, QQQ):** monkeys pick the same number of days uniformly from all weekdays (2013 → end) and go long; compared on mean daily raw excess P&L vs the ensemble's active days.
  - **N3 (US100):** monkeys trade the same number of session days with a random direction each day (same 09:30 → 15:59 window, same costs); compared on mean daily net P&L.
  - **GT (USDJPY):** monkeys pick the same number of non-holiday weekdays (2014–26) and short 09:55 → 10:55 JST at the same cost; compared on mean per-trade net.
  - **Report:** the actual book's percentile among its monkeys. Davey's bar: ≥ 90th.
- **WF — Pardo's walk-forward efficiency** (walk-forward Sharpe ÷ best in-sample variant Sharpe) for the A, RB and GT grids. Pardo's bar: ≥ 50%.

**DSR count:** 13,943 + 2 = 13,945.

### A46 (2026-09-27, round 32: annual return seasonality across the FTMO universe; intraday half-hour periodicity; written before any of these results was computed)

**Why:** two *Journal of Finance* anomaly families with flow mechanisms, untouched in 31 rounds, both testable on data in hand, both largely post-publication in our samples.
- **KS** — Keloharju, Linnainmaa & Nyberg (2016): assets' same-calendar-month historical returns predict their future returns (stocks 13%/yr; also country indices, commodities, currencies). Mechanism: recurring seasonal flows/risk premia.
- **HP** — Heston, Korajczyk & Sadka (2010): returns continue at half-hour intervals that are exact multiples of a trading day, for ≥ 40 days. Mechanism: institutional order-splitting at fixed clock times.

#### KS — annual seasonality, cross-sectional across FTMO instruments

- **Universe (21):** SPY, QQQ, DIA, IWM, ^N225, ^GDAXI, ^FTSE, ^AXJO, ^FCHI, ^HSI, ^IBEX, ^STOXX50E (Yahoo daily, adjusted closes); XAUUSD, XAGUSD (16:45-NY daily bars); EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD (`fx_daily`). Monthly returns from month-end closes.
- **Signal at month-end t:** the instrument's mean return in calendar month(t+1) over its full prior history; an instrument enters only with ≥ 8 prior observations of that month.
- **Portfolio:** rank available instruments; long the top 3, short the bottom 3, equal weight, hold one month.
- **Costs:** per-side per rebalance — indices 1.5 bp, FX 1.0, gold 2.5, silver 5.0; both legs replaced monthly. Financing 2%/yr on each leg's gross (4%/yr total, ≈ 33 bp/month).

| | Primary (one-sided; Holm over K1–K2) |
|---|---|
| K1 | Gross long−short monthly mean > 0, 2003-02 → 2026-08 (t over months) |
| K2 | The same, post-publication 2017-01 → 2026-08 |

**Verdict:** **EDGE** if K1 and K2 pass Holm and the post-publication **net** mean is positive in both 2017–21 and 2022–26; **SEASONAL, NOT TRADEABLE** if K1–K2 pass but the net fails; **NO EDGE** otherwise.
**Grid (4 variants for the battery;** split 2017-01): {top/bottom 3, terciles} × {min 8, min 15 observations}.

#### HP — intraday half-hour periodicity

- **Instruments and bins:** SPXUSD and NSXUSD, 13 half-hours 09:30 → 16:00 NY (2013 →); EURUSD and USDJPY, 26 half-hours 07:00 → 20:00 London (2003 →). Bin returns from minute closes at the bin edges; spike bars dropped; |bin| < 3%.
- **Rule:** in bin b on day t, hold sign(r(b, t−1)) for the bin.

| | Primary (one-sided; Holm over H1–H3) |
|---|---|
| H1 | Mechanism: pooled correlation of r(b, t) with r(b, t−1) > 0 (day-block bootstrap, 2,000 draws, all four instruments) |
| H2 | Rule, gross: mean per bin-trade > 0 (daily aggregates, HAC lag 5) |
| H3 | Tradeable: only bins where \|r(b, t−1)\| exceeds that bin's trailing-60-day 80th percentile, **net** of per-side costs (indices 1.5 bp, FX 1.0; two sides per bin-trade) > 0 |

**Verdict:** **EDGE** if H3 passes Holm and its net mean is positive in both sample halves (per instrument class); **MECHANISM, NOT TRADEABLE** if H1 or H2 passes without H3; **NO EDGE** otherwise.
**Grid (8 variants for the battery;** split 2020-01): 4 instruments × {all bins, filtered bins}, net books.

**DSR count:** 13,945 + 5 + 4 + 8 = 13,962.

### A47 (2026-09-27, round 33: the 0DTE regime — intraday reversal on US index CFDs; written before any of these results was computed)

**Why:** a mechanism with current literature and a clean natural experiment, never tested here.
- **Baltussen, Da, Lammers & Martens (JFE 2021):** hedgers who are *short* gamma trade with the move, creating intraday momentum; *long* gamma hedging does the opposite.
- **Dim, Eraker & Vilkov (2024, SSRN 4692190):** in 0DTE SPX options, market makers' net gamma is on average **positive**, and positive gamma **strengthens intraday reversal**.
- **The experiment:** Cboe added Tuesday/Thursday SPX expiries in April–May 2022 and had daily expiries by 2022-11-14; 0DTE reached 40–50% of SPX options volume. If the mechanism is right, afternoon reversal of the day's move should be stronger after 2022-11 than before.
- **Prop fit:** intraday, flat by 15:55 NY, fits every FTMO account type.

**Data:** HistData 1-minute SPXUSD (US500) and NSXUSD (US100), NY clock, spike bars dropped (A35a).
- **Periods:** PRE = 2013-01-02 → 2022-04-29; TRANSITION (excluded) = 2022-05-02 → 2022-11-11; POST = 2022-11-14 → 2026-09-18.
- **Signal:** r_am = the return from the 09:30 open to the entry mark. σ20 = the standard deviation of the previous 20 days' r_am.
- **Rule R14 (primary):** at 14:00, take −sign(r_am); exit at 15:55.
- **Costs:** 1.5 bps per side (3.0 per trade).

**Primary hypotheses** (one-sided; Holm over Z1–Z3):

| | Test |
|---|---|
| Z1 | US500 R14, POST, net mean > 0 (HAC t, lag 5) |
| Z2 | US500 R14 gross mean, POST minus PRE > 0 (Welch): the regime created or strengthened reversal |
| Z3 | US100 R14, POST, net mean > 0 |

**Verdict:**
- **EDGE:** Z1 passes Holm, its net mean is positive in both halves of POST (2022-11 → 2024-06, 2024-07 → 2026-09), and US100's POST net mean is positive (breadth).
- **REGIME SHIFT, NOT TRADEABLE:** Z2 passes without Z1.
- **NO EDGE** otherwise.

**Grid (12 variants for the battery;** split 2022-11-14, walk-forward from 2016): {US500, US100} × entry {13:00, 14:00, 15:00} × {all days, |r_am| > 1 σ20}. Exit 15:55 throughout.

**Also reported (risk check on an existing edge):** N3's (US100 noise-area momentum) mean per day in PRE vs POST. The mechanism predicts momentum rules weaken in POST.

**DSR count:** 13,962 + 12 = 13,974.

### A48 (2026-09-27, round 34: the US100 momentum edge on US30 and US2000 — a breadth test on a new, independent data feed; written before these data were downloaded)

**Why:** N3 (US100 intraday momentum) is one of the three confirmed edges, but it is single-market: it failed on US500, and HistData has no minute data for FTMO's US30 or US2000. Round 33 found it strengthened after 2022. Dukascopy's free datafeed (an independent broker's quotes) carries both US30 (USA30IDXUSD) and US2000 (USSC2000IDXUSD) at one-minute resolution. If N3's mechanism (trend-day continuation driven by hedging flows) is general to US index products, it should appear there; if not, N3 stays a US100-specific edge.

**Data:** Dukascopy BID 1-minute candles, downloaded after this entry is committed; UTC day files converted to New York time; spike bars dropped (A35a, 2% for indices); a session needs ≥ 300 minutes between 09:30 and 16:00. The sample starts at each instrument's first available year (reported) and ends 2026-09-18. Dukascopy USATECHIDXUSD (US100) is downloaded as a second-feed check of the existing edge.

**Rule:** the native N3 grid of round 11 (R3), unchanged: at 09:30 NY, stop orders at the session open ± k × width, width ∈ {prior session's range, ATR(14)}, k ∈ {0.3, 0.5, 0.7}, mode ∈ {flat after the first fill, stop-and-reverse}, everything flat at 15:59. **Primary variant: range | k 0.5 | flat** (the round-11 recommended native build).

**Costs per entry (round trip):** US30 1.5 bps; US2000 3.0 bps (wider CFD spread); US100 1.5 bps.

**Primary hypotheses** (one-sided; Holm over B1–B2):

| | Test |
|---|---|
| B1 | US30, primary variant, net mean per day > 0 (HAC t, lag 5) |
| B2 | US2000, primary variant, net mean per day > 0 |

**Verdict:**
- **BREADTH CONFIRMED:** B1 and B2 both pass Holm at 5%, and each instrument's net mean is positive in both halves of its sample (split at the sample midpoint). N3 then becomes a three-index momentum family, each index run in its own account or sized as a basket.
- **PARTIAL:** exactly one passes; that instrument may join the build only if its own halves are both positive.
- **NOT CONFIRMED:** neither passes; N3 remains US100-only.

**Also reported:** the 12-variant grid per instrument (A22 battery, share positive); the second-feed check — the primary variant's daily P&L on Dukascopy US100 vs HistData US100 (correlation, and mean on common days); results after 2022-11-14 (the 0DTE era).

**DSR count:** 13,974 + 24 = 13,998.

#### A48a (2026-09-27, data-access amendment to A48; written before any US30/US2000 return was computed)

**What happened:** Dukascopy's free datafeed rate-limits to roughly one file every 20–30 seconds. Minute candles come one file per day (~3,400 per instrument), which at that rate is ~28 hours per instrument. Hourly candles come one file per month (~170 per instrument). No US30 or US2000 return has been computed or inspected; only file availability was probed.

**Change:** the breadth test runs on **Dukascopy hourly candles** with an hourly adaptation of the native rule, validated first on US100, where the minute-exact answer is known.

- **Hourly rule (HN3):** New York hourly bars (whole-hour offsets, so bar edges are NY hours). The session is the six bars 10:00 → 16:00. Open = the 10:00 bar's open. Width = the prior session's range (max high − min low over its six bars) or ATR(14) of session ranges. Bands = open ± k × width. The entry is the first bar whose high reaches the upper band or whose low reaches the lower band, filled at the band or the bar's open if it gapped through. **If both bands are reached inside the same bar, the worse of the two outcomes is booked** (conservative). Hold to the 16:00 close. One trade a day (the "flat" mode; stop-and-reverse cannot be resolved inside hourly bars and is dropped).
- **Primary variant:** range | k 0.5, as registered. **Grid:** {range, atr14} × k ∈ {0.3, 0.5, 0.7} = 6 variants per instrument.
- **Costs:** as registered (US30 1.5 bps, US2000 3.0, US100 1.5 per trade).

**Calibration gate (new, decided before the test):** on HistData US100 2014 → 2026-08, resampled to NY hourly bars, HN3's primary daily P&L must correlate **≥ 0.60** with the minute-exact native primary (round 11), and HN3's mean must be positive. If the gate fails, the verdict is **UNTESTABLE WITH HOURLY DATA** and no breadth claim is made either way.

**Hypotheses and verdict rule unchanged** (B1 US30, B2 US2000; Holm; both halves positive), applied to HN3. The Dukascopy US100 hourly series is reported as the second-feed check.

**DSR count:** 13,974 + 12 (6 per instrument) = 13,986, replacing A48's 13,998.

#### A48b (2026-09-27, round 34 continued: the A48 minute test on a faster route to the same Dukascopy candles; written before any US30/US2000 return was computed)

**What happened:** the A48a hourly route failed its calibration gate (hourly N3 correlates 0.455 with the minute rule; verdict for that route: UNTESTABLE WITH HOURLY DATA, reported in REPORT §22.20). The post hoc diagnostic showed why: the edge sits in 09:30–10:00, which NY hourly bars cannot resolve. Dukascopy's chart service (freeserv.dukascopy.com, JSON, BID side) serves the same one-minute candles **5,000 per request at about one request a second**. Probes so far: first-available dates (US100 2012-01-19, US30 2012-04-04, US2000 2018-08-08) and five raw candle pages. No rule return has been computed on US30, US2000 or Dukascopy US100.

**Change:** A48 is run **as originally registered**, on these minute candles: the native N3 grid of round 11 (R3) unchanged (width ∈ {prior session range, ATR(14)}, k ∈ {0.3, 0.5, 0.7}, mode ∈ {flat, reverse}; stops at the 09:30 open; flat at 15:59), **primary range | k 0.5 | flat**; costs per entry US30 1.5 bps, US2000 3.0, US100 1.5; B1 (US30) and B2 (US2000) one-sided, Holm over the two; verdict rules as in A48 (both halves positive, split at each sample's midpoint). Code: the round-11 R3 logic as `run_round34_minute.r3_grid`, the same function that reproduced round 11 on HistData US100 in the A48a gate.

**Data handling (fixed now):** UTC timestamps converted to New York time; filler candles (volume 0 with open = high = low = close) dropped; spike bars dropped (A35a, 2% for indices); a session needs ≥ 300 minutes between 09:30 and 16:00. Samples: US30 2012-04-04 → 2026-09-18; US2000 2018-08-08 → 2026-09-18 (its first available date); Dukascopy US100 2012-01-19 → 2026-09-18.

**Feed-validation gate (new, decided before the test):** on common days 2013-01 → 2026-08, the native primary's daily P&L on Dukascopy US100 must correlate **≥ 0.60** with the same rule on HistData US100. If it fails, the verdict is **FEED NOT VALIDATED** and no breadth claim is made.

**Also reported:** the 12-variant grid per instrument with the A22 battery (24 variants), share positive, results after 2022-11-14, and the US100 second-feed comparison.

**DSR count:** 13,986 + 24 = **14,010** (the 12 hourly trials of A48a stay counted although never run).

### A49 (2026-09-27, round 35: intraday momentum in FTMO's US mega-cap stock CFDs — the N3 mechanism below the index; written before any stock return was computed)

**Why:** N3 (US100 intraday momentum from the 09:30 open) is confirmed, and round 34's diagnostic put its edge in the first half hour. Its mechanism, hedging by option dealers who are short gamma, is documented at the single-stock level: negative dealer gamma imbalance predicts intraday momentum (Barbon & Buraschi 2021, "Gamma Fragility"), and opening-range momentum on "stocks in play" earned high net returns in US stocks 2016–2023 (Zarattini, Barbon & Aziz 2024). US100 is a weighted average of these same mega-caps. If the effect lives in the constituents, a stock-level book would multiply N3's trade count. Evidence against: individual stocks reverse in the last 30 minutes (Baltussen, Da & Soebhag 2024), which works against a hold-to-close rule; and stock CFD spreads are 2–5× index spreads.

**Data:** Dukascopy stock CFD one-minute BID candles from the chart service (split-adjusted; the A48b downloader), 2017-03-01 (AMD 2017-11-02) → 2026-09-18, New York time; filler candles dropped; spike bars dropped at **3%** (A35a logic; single stocks jump more than indices); a session needs ≥ 300 minutes between 09:30 and 16:00. No stock return has been computed. Probes so far: first-available dates, FB ticker continuity, and one bid/ask page each for AAPL and JPM (spread only).

**Universe (12, fixed now):** AAPL, AMZN, MSFT, NVDA, TSLA, META (Dukascopy ticker FB), GOOGL, JPM, V, AMD, AVGO, NFLX. These are the US mega-caps named in FTMO's equity CFD list with Dukascopy history from 2017.

**Rule:** the native N3 grid of round 11, unchanged (`run_round34_minute.r3_grid`): stop orders at the 09:30 open ± k × width, width ∈ {prior session range, ATR(14)}, k ∈ {0.3, 0.5, 0.7}, mode ∈ {flat, reverse}, flat at 15:59. 12 variants per stock. **Primary: range | k 0.5 | flat.**

**Costs per entry (fixed procedure, applied after this commit and before any return):** each stock's median Dukascopy ask − bid over session minutes (09:30–16:00) in the 30,000-candle page starting 2025-03-03, in bps of mid, **plus 1 bp** commission allowance. Sensitivity at 2× cost is reported.

**Hypotheses:**

| | Test |
|---|---|
| S1 (primary) | Equal-weight basket (mean over the stocks with a session that day) of the primary variant, net mean per day > 0 (HAC t, lag 5), one-sided |
| S2 (breadth) | At least 10 of the 12 stocks have a positive net mean on the primary variant (sign test, p = 0.019) |

**Verdict:**
- **EDGE:** S1 p < 0.05, the basket's net mean is positive in both halves (split at the sample midpoint), and S2 holds.
- **PARTIAL:** S1 passes but S2 fails (edge concentrated in a few names). Those names are leads for a later confirmation, not for the build.
- **NO EDGE:** S1 fails.

**Also reported (not tests):**
- Stocks in play: the basket's primary variant on earnings-reaction sessions vs other sessions (Welch). An earnings-reaction session is the session after an SEC 8-K Item 2.02 filing: the same day if it was accepted before 09:30 ET, the next session if accepted after 16:00 ET. Filings accepted during the session are excluded. Source: `data_edgar.py`.
- The 12 × 12 grid under the A22 battery; the 0DTE era (from 2022-11-14); results at 2× cost; the basket's correlation with US100 N3.

**DSR count:** 14,010 + 144 = **14,154**.

### A50 (2026-09-27, round 36: five published practitioner setups, tested as their books state them; written before any of these rules was run)

**Why:** the user asked for edges from the trading literature itself. Rounds 1–35 tested the academic anomalies and the practitioners' methods (Kaufman, Davey, Pardo). They did not test the best-known *setups* from the practitioner books, as those books define them. Five setups, each specific enough to code without choices:

| Code | Setup (source) | Rule as published (long side; the short side mirrors it) |
|---|---|---|
| OO | **Oops!** (L. Williams, *Long-Term Secrets to Short-Term Trading*, 1999) | The session opens below the prior session's low → buy stop at the prior low; exit at the session close |
| TS | **Turtle Soup** (Raschke & Connors, *Street Smarts*, 1995) | The session makes a new 20-session low, and the previous 20-session low was set ≥ 4 sessions earlier → after the new low, buy stop at the previous 20-session low; exit at the next session's close |
| E8 | **80-20s** (Raschke & Connors, *Street Smarts*) | The prior session opened in the top 20% of its range and closed in the bottom 20% → if this session trades below the prior low, buy stop at the prior low; exit at the session close |
| TD | **TD Sequential buy setup** (T. DeMark, *The New Science of Technical Analysis*, 1994) | Nine consecutive session closes each below the close four sessions earlier → buy at the ninth close; exit at the close five sessions later |
| MP | **Market Profile 80% rule** (Dalton, Jones & Dalton, *Mind Over Markets*, 1990) | The session opens outside the prior session's value area, then two consecutive 30-minute brackets close inside it → enter toward the far side at the second bracket's close; exit at the far value-area edge (limit) or the session close |

**Definitions:** sessions are cash sessions in local time: US500, US100 09:30–16:00 NY; GER40 09:00–17:30 Berlin; UK100 08:00–16:30 London; JP225 09:00–15:00 Tokyo (15:30 from 2024-11-05); XAUUSD 08:20–13:30 NY. The session open is the first minute's open. Stops fill at the stop price, or at the bar's open if it gapped through. Intraday order is resolved on one-minute bars, so the new low must print before the buy stop is hit (TS, E8). Value area (MP): the prior session's 30-minute brackets mark the price bins they touched (bin = prior session range / 60); the POC is the bin with most marks; the area grows from the POC toward the side with more marks until it holds ≥ 70% of them.

**Data and costs:** HistData one-minute CFD quotes (spike filter A35a), indices 2013 → 2026-09-18, gold 2009 →. Costs per round trip: US500, US100, GER40, UK100 1.5 bps; JP225 3.0; XAUUSD 2.5. Multi-session holds (TS, TD) carry no financing, since round 11 found the mark-up immaterial at these horizons for index CFDs.

**Variants (4 per setup and instrument, 120 in all):** side ∈ {long, short} × a second choice per setup: OO {exit at close, exit at next session's open}; TS {exit next close, exit same close}; E8 {exit same close, exit next close}; TD {hold 5, hold 1}; MP {limit exit, time exit only}. **Primary variant per setup: both sides combined, first choice** (the book version).

**Hypotheses (one-sided, Holm over the five):** P_OO, P_TS, P_E8, P_TD, P_MP. Each is the setup's primary: the equal-weight portfolio of the six instruments (daily P&L averaged over instruments, zero on days without a trade), net mean per day > 0 (HAC t, lag 5).

**Verdict per setup:** **EDGE** if Holm p < 0.05 and the net mean is positive in both halves of 2013–2026. Setups that pass are then compared with the reversal family (REV, already in the book): if their correlation with the REV ensemble is ≥ 0.5, the verdict is **EDGE, SAME AS REV** (no new source).

**Also reported:** the 120-variant grid with the A22 battery; the MP rule's hit rate against its "80%" claim; per-instrument results; long vs short.

**DSR count:** 14,154 + 120 = **14,274**.

### A51 (2026-09-27, round 37: "stocks in play" — N3 momentum on earnings-reaction sessions, confirmed on 71 stocks never tested here; written before these stocks' candles were downloaded)

**Why:** round 35 (A49) found no edge in N3 momentum on 12 mega-caps as a basket. Its pre-registered "also reported" split showed one strong result: on **earnings-reaction sessions** the native primary earned **+21.4 bps per stock-session net** (n 496, t 1.83), against −0.4 on other sessions (Welch p 0.03). That matches the published "stocks in play" result (Zarattini, Barbon & Aziz 2024: opening-range momentum pays on stocks with news-driven activity). The same cross-section showed momentum paying in high-volatility, retail-option names (TSLA, NVDA, AMD) and reversing in low-volatility ones (JPM, V), as the dealer-gamma account predicts (Barbon & Buraschi 2021). Both are post hoc cuts of one sample, so they are tested here on stocks that sample did not touch.

**Universe (71, fixed now):** the S&P 100 names below, excluding the 12 of round 35, that Dukascopy serves with one-minute data from 2019-01-01 or earlier (first-available dates probed; no candles downloaded):
BA AMGN BAC C CMCSA CSCO CVX DIS GE GILD GS HD IBM INTC PFE T WFC ABT ADBE AIG AMAT BK BMY CAT CI CRM DE KHC LLY LMT MA MMM ADP AXP CL COP COST CVS F FDX GM HON KMI LOW MDLZ MET MO MRK MS NKE ORCL PEP PM PYPL QCOM SBUX SCHW SO TGT TMO TXN UNH BRKB UPS USB VZ WMT EMR EXC ISRG NEE.
Not available on Dukascopy (dropped by the rule): ABBV BKNG CHTR DHR DUK INTU JNJ KO LIN MCD PG RTX XOM. Available only from 2022 (dropped): ACN BLK GD MDT NOW SLB SPGI TMUS.

**Data, rule, costs:** as A49. Dukascopy BID minute candles (chart service) from each stock's first date to 2026-09-18; spike filter 3%; sessions ≥ 300 minutes. The native primary is unchanged: range | k 0.5 | flat, stops at the 09:30 open ± 0.5 × prior session range, flat at 15:59. Costs are measured per stock by the A49 procedure (median session ask − bid in the page starting 2025-03-03, + 1 bp).

**Earnings-reaction session (as A49):** the session after an SEC 8-K Item 2.02 filing — the same day if accepted before 09:30 ET, the next session if accepted after 16:00 ET; filings during the session are excluded. CIKs come from the SEC ticker file; DIS and CI include their pre-2019 CIKs (1001039, 701221); BK = 1390777.

**Hypotheses (one-sided; Holm over E1–E3):**

| | Test |
|---|---|
| **E1 (primary)** | Event portfolio: on each date with ≥ 1 earnings-reaction session, the mean net P&L of the primary across those stocks; mean > 0 (HAC t, lag 5, dates in order) |
| E2 | Stock-session level: earnings-reaction sessions minus other sessions > 0 (Welch) |
| E3 | Cross-section: Spearman ρ > 0 between each stock's ex-ante volatility (close-to-close, its first 250 sessions) and its primary net mean on the remaining non-earnings sessions |

**Verdict:**
- **STOCKS IN PLAY CONFIRMED** if E1 passes Holm at 5% and the event portfolio is positive in both halves (split at the median event date).
- **VOLATILITY LINK CONFIRMED** if E3 passes Holm at 5%. This would support restricting N3-type momentum to high-volatility names.
- Otherwise each lead is closed.

**Also reported:** the 12-variant grid on earnings sessions; round 35 + 37 combined (83 stocks); filings before the open vs after the close; long vs short; the FTMO-listed subset; results per year.

**DSR count:** 14,274 + 12 + 2 = **14,288**.

#### A51a (2026-09-27, amendment to A51 written while the candles download, before any round-37 return was computed)

**Why:** SQX cannot read an earnings calendar with native blocks. If "stocks in play" is real, the build needs a price-only way to spot an in-play session.

**Added hypothesis E4 (one-sided; Holm now over E1–E4):** a **gap proxy**. A session is "in play" if its 09:30 open is more than 2× the stock's average absolute open-vs-prior-close gap over the previous 20 sessions away from the prior 16:00 close. E4 is E1's test with gap-proxy sessions in place of earnings sessions: on each date with ≥ 1 proxy session, the mean net P&L of the native primary across those stocks; mean > 0 (HAC t, lag 5).

**Verdict addition:** **GAP PROXY CONFIRMED** if E4 passes Holm at 5% and is positive in both halves; then the SQX build uses the gap filter (native blocks) instead of a calendar.

**DSR count:** 14,288 + 1 = **14,289**.

### A52 (2026-09-27, round 38: the native N3 momentum rule on FTMO's energy and silver CFDs; written before these candles were downloaded or any return computed)

**Why:** N3 (US100) is confirmed on two feeds but does not travel to other indices or to single stocks (rounds 34, 35, 37). Its likely driver is hedging by option dealers and leveraged ETFs. The other FTMO markets with large retail leveraged-ETF and option complexes are crude oil (USO, UCO/SCO), natural gas (BOIL/KOLD) and silver (SLV, AGQ/ZSL). Intraday momentum is documented across 60+ futures (Baltussen, Da, Lammers & Martens 2021). The noise-area family of round 9 covered indices and gold only; **silver, WTI, Brent and natural gas have never been tested with the N3 rule**. Caution: the different last-30-minute commodity rule (round 5, T1) decayed after 2020.

**Instruments, sessions (New York time) and data:**

| | Session | Data |
|---|---|---|
| WTI (FTMO USOIL) | 09:00–14:30 (NYMEX floor hours; settlement 14:28–14:30) | Dukascopy LIGHT.CMD/USD minute, 2011-12 → |
| Brent (FTMO UKOIL) | 09:00–14:30 | Dukascopy BRENT.CMD/USD, 2010-12 → |
| Natural gas (FTMO NATGAS) | 09:00–14:30 | Dukascopy GAS.CMD/USD, 2012-06 → |
| Silver (FTMO XAGUSD) | 08:25–13:25 (COMEX) | HistData XAGUSD minute, 2010 → (Dukascopy XAG only from 2014-07: second-feed check) |

All samples end 2026-09-18. Filler candles dropped; spike filter 2%; a session needs ≥ 77% of its minutes (the 300-of-390 ratio of A48).

**Rule:** the native N3 grid unchanged (width ∈ {prior session range, ATR(14)}, k ∈ {0.3, 0.5, 0.7}, mode ∈ {flat, reverse}): stop orders at the session open ± k × width, flat one minute before the session close. **Primary: range | k 0.5 | flat.** 12 variants × 4 = 48.

**Costs per entry (procedure fixed now, applied before any return):** the median Dukascopy ask − bid over session minutes in the 30,000-candle page starting 2025-03-03, plus 0.5 bp (FTMO charges no commission on energy; a small allowance for slippage). Silver uses the Dukascopy XAG/USD spread the same way. Sensitivity at 2× cost is reported.

**Hypotheses (one-sided):**

| | Test |
|---|---|
| **C0 (primary)** | Equal-weight portfolio of the four primaries (mean over instruments with a session that day), net mean per day > 0 (HAC t, lag 5) |
| C1–C4 | Each instrument's primary, net mean > 0 (Holm over the four) |

**Verdict:** **EDGE (commodity momentum family)** if C0 p < 0.05 and the portfolio is positive in both halves. **Per-instrument EDGE** if an instrument passes Holm and is positive in both of its halves. Otherwise **NO EDGE**.

**Also reported:** the 48-variant grid under the A22 battery; results before and after 2020-06 (the T1 decay date); the silver second feed (Dukascopy from 2014-07); correlation with US100 N3; results at 2× cost.

**DSR count:** 14,289 + 48 = **14,337**.

### A53 (2026-09-27, round 39: volume-conditioned reversal and continuation — Campbell, Grossman & Wang; written before any volume data was downloaded)

**Why (a new information source):** every round so far used price and time only; HistData has no volume. Dukascopy's candles carry volume, and SQX reads the broker's tick volume natively (Volume blocks), so a volume rule is buildable. Theory: price moves on **high volume** are more often liquidity-driven and **reverse**; moves on **low volume** are more often informed and **continue** (Campbell, Grossman & Wang 1993, *QJE*; Llorente, Michaely, Saar & Wang 2002, *RFS*). Unconditional daily reversal failed on FX and gold (round 10). If CGW is right, the volume split separates the reversing days from the rest. The critical risk is that Dukascopy volume is only a proxy for FTMO tick volume; the signal therefore uses **relative** volume only.

**Data:** Dukascopy hourly BID candles with volume (chart service), rebuilt into daily bars closing at **17:00 New York** (FTMO's MT5 server day; the Sunday open joins Monday). Markets and samples: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD 2004 →; XAUUSD 2004 →; US500, US100, GER40 2013 →; all to 2026-09-18.

**Signal (SQX-native: Close, ATR, Volume, SMA of Volume):** r_t = C_t / C_{t−1} − 1; RV_t = V_t / SMA(V, 20)_{t−1}; σ_t = standard deviation of r over the prior 20 days. A day qualifies if |r_t| ≥ 0.5 σ_t.
- **Reversal arm:** RV_t ≥ 1.5 → enter against r_t at the 17:00 close; exit at the next 17:00 close.
- **Continuation arm:** RV_t ≤ 0.75 → enter with r_t; exit at the next close.

**Costs per trade:** FX majors 1.0 bp round trip + 0.5 bp financing; gold 2.0 + 0.5; indices 1.5 + 1.0.

**Variants (reported under the A22 battery):** RV threshold {1.25, 1.5, 2.0} (reversal) / {0.6, 0.75, 0.9} (continuation) × hold {1, 3 days} × move filter {0.5σ, none}, per market: 24 per market, 264 in all.

**Primary hypotheses (one-sided; Holm over V1–V5):**

| | Test |
|---|---|
| V1 | FX majors, reversal arm (primary parameters), equal-weight portfolio of the 7 pairs, net mean per day > 0 (HAC, lag 5) |
| V2 | XAUUSD, reversal arm, net > 0 |
| V3 | US500 + US100 + GER40 portfolio, reversal arm, net > 0 |
| V4 | FX majors, continuation arm, net > 0 |
| V5 | Mechanism: pooled over all 11 markets, the slope c < 0 in r_{t+1} = a + b·r_t + c·r_t·log(RV_t) (standardized r; HAC t) |

**Verdict:** each arm V1–V4 is an **EDGE** if Holm p < 0.05 and its net mean is positive in both halves; V5 decides whether the CGW mechanism is present at all. Index results are also checked against REV: correlation ≥ 0.5 → "same as REV".

**DSR count:** 14,337 + 264 = **14,601**.

#### A53a (2026-09-27, data-integrity amendment to A53, written after the first run exposed the problems)

**What happened:** (1) the hourly downloader stopped at the first empty page, so **XAUUSD ended in 2018**; (2) Dukascopy's **index CFD volume is unusable**: US500/US100 miss most of 2015–2017, and their volume units change by ~1,000× across years (median minute volume 0.04, 99th percentile 39). FX data are clean (≈ 260 days per year, 2004–2026).

**Change:** the downloader steps past empty pages; **V3 (indices) is dropped** as untestable with this volume source, and the index variants leave the battery; V1, V2, V4 and V5 (now FX + gold only) are rerun unchanged. First-run output is kept as `results/round39_volume_run1.json`. Already visible before the rerun, and reported as such: on FX alone, high-volume days show no next-day reversal (−0.003 σ, t −0.08; 1,788 days).

**DSR count:** unchanged (14,601; the dropped trials stay counted).

### A54 (2026-09-28, round 40: month-end rebalancing in the closing auction; Nasdaq-minus-S&P spread momentum; written before either rule was run)

**Part 1 — ME (month-end rebalancing at the close).** Calendar-rebalancing pensions sell equities after equities outperform and buy after they lag, and the pressure shows up over the next trading day (−17 bps, Harvey, Mazzoleni & Melone 2025, NBER w33554). Round 4's daily test of the rebalancing signal (CF-02) was weak (+7.2 bps/day, t 2.1) and faded after 2023. If the orders go through the closing auction (MOC), the pressure should concentrate in the **last 30 minutes of the month's last trading day**, a timing the daily test could not isolate.
- **Rule (SQX-native: time, month-to-date return, last trading day of the month):** at **15:30 NY on the last trading day of the month**, go against the sign of the index's month-to-date return (last close of the prior month → 15:30); exit at 15:59.
- **Markets and data:** US500, US100 (HistData minute 2013 → 2026-09-18); US30 (Dukascopy minute 2012-04 →). Costs 1.5 bps per round trip.
- **Primary ME1:** equal-weight US500 + US100 + US30, net mean per event > 0 (t over the ≈ 160 month-ends, HAC lag 1).
- **ME2 (mechanism):** the fade pays more after big months: slope of the event P&L on |MTD| > 0.
- Variants reported: entry {15:30, 15:50}; threshold |MTD| {0, 1%, 2%}; exit {15:59, next day 10:00}; quarter-ends only.

**Part 2 — SPM (US100 − US500 spread momentum).** Round 34 showed N3's momentum is specific to the Nasdaq-100. If so, the Nasdaq-specific part of the move, the spread between the two indices, should itself trend inside the day, with the market's direction hedged out.
- **Spread:** S(t) = P100(t)/P100(09:30) − P500(t)/P500(09:30) on synchronized minutes (dollar-neutral, equal notional). Width = the prior session's range of S.
- **Rule:** the native N3 grid applied to S (k ∈ {0.3, 0.5, 0.7} × width ∈ {prior range, ATR(14) of S ranges} × {flat, reverse}): long the spread (long US100, short US500) when S reaches +k·width, short it at −k·width, flat 15:59. **Primary: range | k 0.5 | flat.** Costs: 3.0 bps per entry (two legs).
- **Data:** HistData US500 and US100 minute, 2013 → 2026-09-18.
- **Primary SP1:** net mean per day > 0 (HAC t, lag 5), both halves positive. Also reported: correlation with US100 N3; the spread's Sharpe against N3's; the 12-variant grid.

**Holm over ME1, ME2, SP1. Verdict per part: EDGE if its primary passes Holm at 5% and is positive in both halves.**

**DSR count:** 14,601 + 3 + 24 (ME variants) + 12 (SPM variants) = **14,640**.

### A55 (2026-09-28, round 41: overseas sessions fade the prior US session — confirmation on unseen 2000–2012 data; written before any 2000–2012 return was computed)

**Why (a critical re-read of round 26):** round 26 (A40) tested the published *continuation* of US moves into overseas sessions and found it had **inverted**. After a US up-day the next overseas cash session fell (JP225 −4.2, HK50 −6.6, AUS200 −4.6, GER40 −1.8 bps); after a US down-day it rose (+4.5 / +4.2 / +3.2 / +3.7). The continuation trade lost −10.4 bps/day (t −7.0) on JP225 and −10.5 (t −9.9) pooled, uniformly across both halves of 2013–26. The fade was set aside for two reasons that do not hold. (1) "It is REV": REV only buys after declines, while the fade's short side after US **up** days is as large. (2) "Below costs": that assumed 3–6 bps per round trip, while FTMO's index CFDs carry no commission and spreads of about 1–3 bps. The fade was never tested out of sample, because it is a post hoc flip, so it is tested here on years never used: **2000–2012**.

**Rule (SQX-native: US500 loaded as a second data series):** at the overseas cash open, go against the sign of the most recent completed US session's close-to-close return (the last US close before that open); exit at the overseas cash close.

**Data (unseen years):** Yahoo daily open and close, 2000-01-01 → 2012-12-31: Nikkei 225 (JP225), Hang Seng (HK50), ASX 200 (AUS200), DAX (GER40); S&P 500 closes for the signal. Data rules fixed now: FTSE is excluded (Yahoo's opens for 2000–12 equal the prior close on 96% of days); ASX 200 days whose open equals the prior close (16%) are dropped as missing opens; sessions with |open→close| > 12% are dropped.

**Costs per round trip (procedure fixed now):** each market's median Dukascopy ask − bid over its cash session in the 30,000-candle page starting 2025-03-03 (JPN.IDX/JPY, HKG.IDX/HKD, AUS.IDX/AUD, DEU.IDX/EUR), plus 0.5 bp.

**Hypotheses (one-sided; Holm over F1–F3):**

| | Test |
|---|---|
| **F1** | 2000–2012, equal-weight portfolio of the four fades, **gross** mean per day > 0 (HAC t, lag 5): the mechanism on unseen data |
| **F2** | 2000–2012, the same portfolio **net** of the measured costs, mean > 0 |
| F3 | 2000–2012, conditional strength: the fade after large US days (\|US return\| > 1 σ, 20-day) earns more than after small ones (Welch) |

**Verdict:** **EDGE** if F1 and F2 pass Holm at 5%, the net portfolio is positive in both halves of 2000–2012 (split 2006-07-01), and the 2013–26 net (measured costs, HistData minute opens and closes) is positive. Then it is built as an SQX strategy per market in its own account. Also reported: per-market results; long vs short legs; correlation with REV on 2013–26; the 1990–1999 sample as a further check (reported, not a test).

**DSR count:** 14,652 + 3 = **14,655**.

### A56 (2026-09-28, round 42: N3 momentum on Bitcoin and Ether anchored to the New York open — a spot-ETF natural experiment; written before any crypto session return was computed)

**Why (a synthesis of two findings):** (1) N3's edge comes from anchoring bands at a cash open where hedging flows concentrate; it fails where that structure is missing (rounds 34–38). (2) Since the US spot ETFs launched (2024-01-11), Bitcoin's intraday activity is anchored to New York hours, with peaks at 10:00 and in the 15:00–16:00 benchmark window (Schmidt & Kraft, SSRN 7384239), driven by ETF market makers and a new listed-options complex (IBIT options from 2024-11). Crypto intraday momentum is documented (Concretum; Wen, Bouri, Xu & Zhao). Earlier crypto tests used other rules (round 5 CR-01: last half hour; round 10: daily trend), never N3. Cost check: FTMO charges 0.0325% per side (≈ 6.5 bps round trip), but BTC's intraday range is 5–10× an index's, so cost relative to the typical move is comparable to US100's.

**Data:** Binance spot BTCUSDT and ETHUSDT one-minute klines (data.binance.vision), 2019-01 → 2026-08, New York time, weekdays only (FTMO CFDs; SQX weekday sessions).

**Rule:** the native N3 grid unchanged (`r3_grid`, session 09:30–16:00 NY, stops at the 09:30 open ± k × width, flat at 15:59; width ∈ {prior session range, ATR(14)}, k ∈ {0.3, 0.5, 0.7}, {flat, reverse}). **Primary: range | k 0.5 | flat.** Cost **10 bps per entry** (6.5 commission + 3.5 spread/slippage); sensitivity at 15.

**Hypotheses (one-sided; Holm over K1–K2):**

| | Test |
|---|---|
| **K1** | BTC + ETH equal-weight, primary, net mean per day > 0 (HAC t, lag 5), 2019–2026 |
| K2 | Natural experiment: the post-ETF mean (2024-01-11 →) minus the pre-ETF mean > 0 (Welch) |

**Verdict:** **EDGE** if K1 passes Holm at 5% and both halves are positive. **EDGE (ETF ERA ONLY)** if K1 fails but K2 passes and the post-ETF mean alone is positive with t > 2. Then the build trades only in the ETF regime, and the 2024–26 evidence is flagged as short. Otherwise **NO EDGE**.

**Also reported:** the 12-variant grid per coin under the A22 battery; per-year means; the same grid anchored at 00:00 UTC (the crypto day; a control — New York anchoring should beat it after the ETF launch); results at 15 bps.

**DSR count:** 14,655 + 2 + 24 = **14,681**.

### A57 (2026-09-28, round 43: the crypto-day momentum lead of round 42, confirmed on 13 FTMO altcoins and on unseen 2017–18 BTC/ETH; written before any of these returns was computed)

**Why:** round 42's pre-registered control found the native N3 rule on BTC + ETH anchored at **00:00 UTC** (weekday sessions, flat before midnight) earning +15.6 bps/day net of 10 bps (t 2.93), 2019–26. That is a post hoc lead. It fits documented short-horizon time-series momentum in crypto (Liu & Tsyvinski 2021) in an intraday form that avoids CFD financing. It is confirmed here on data round 42 never touched.

**Universe (fixed; FTMO-listed, never used here):** ADA, DOT, DASH, LTC, XRP, DOGE, XMR, NEO, SOL, BNB, XLM, AAVE, LINK (Binance USDT spot one-minute klines from 2019-01 or each coin's listing, to 2026-08, or to delisting). Unseen years for the two majors: **BTC and ETH 2017-08 → 2018-12**.

**Rule:** the native N3 grid unchanged (`r3_grid`), weekday sessions only, as in round 42. Two anchors:
- **C1 — FTMO server day (the build version):** session 00:05 → 23:55 in FTMO server time (New York + 7 h: the day runs 17:00 → 17:00 New York, which is SQX's D1 bar on FTMO), so trades close before the server-midnight swap.
- **C2 — 00:00 UTC (the exact form of the lead):** session 00:05 → 23:55 UTC. It holds through FTMO's server midnight, so one swap is charged per trade.

**Primary: range | k 0.5 | flat. Costs per entry:** altcoins 15 bps (0.0325% × 2 commission + wider spreads); + 5 bps swap in C2. BTC/ETH 10 bps (+5 in C2). Sensitivity at +5 bps.

**Hypotheses (one-sided; Holm over C1–C3):**

| | Test |
|---|---|
| **C1** | 13-altcoin equal-weight basket, server-day anchor, net mean per day > 0 (HAC t, lag 5) |
| **C2** | Same basket, 00:00 UTC anchor, net (incl. swap) > 0 |
| C3 | BTC + ETH, 2017-08 → 2018-12, 00:00 UTC anchor, net (incl. swap) > 0 |

**Verdict:** **EDGE** if C1 or C2 passes Holm at 5% and its basket is positive in both halves (split at the median date); the build uses C1 if it passes (no swap). C3 is supporting evidence for the majors. Otherwise **NO EDGE**.

**Also reported:** per coin; share of coins positive; the 12-variant grid per anchor; by year; before vs after 2024-01-11.

**DSR count:** 14,681 + 3 + 312 (13 coins × 12 variants × 2 anchors) = **14,996**.
