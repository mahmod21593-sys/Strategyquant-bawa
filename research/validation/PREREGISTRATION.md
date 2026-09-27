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
