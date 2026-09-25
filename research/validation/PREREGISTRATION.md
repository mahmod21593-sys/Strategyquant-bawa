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
