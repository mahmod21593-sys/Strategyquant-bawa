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
