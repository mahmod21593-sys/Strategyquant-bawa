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
