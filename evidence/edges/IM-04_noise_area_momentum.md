# IM-04 — "Noise area" intraday momentum (Zarattini, Aziz & Barbon)

**Verdict:** CANDIDATE on **US100 only**: paper-trade before building (own data: confirmed within its family, fails on US500). **Round 11: build it from native SQX blocks** (§ below) · **Grade:** B− (paper) → B− (own data; DSR over all trials 0.22) · **Prop fit:** High (intraday, flat at the close; fast)



**Practitioner validation (round 31):** Davey monkey test 100th percentile (actual +2.86 bps/day net vs −3.03 for 2,000 random-direction twins on the same sessions and costs).

**0DTE-era risk check (round 33):** N3 earned +4.87 bps/day after daily SPX expiries began (2022-11-14 → 2026-09, t 1.92, n 649) vs +1.73 before. The long-gamma dampening story predicted erosion; the data show the opposite.

**The edge lives in the first half hour (round 34, post hoc):** the native primary started at 10:00 instead of 09:30 earns +1.46 bps/day (t 1.23) against +4.18 (t 3.21); hourly bars from 10:00 track that late start at correlation 0.985. Stops must be placed at the 09:30 open on M1–M5 bars. For the same reason the US30/US2000 breadth test could not be run on hourly data (calibration gate failed, verdict UNTESTABLE).
## Round 11: a native SQX build ([REPORT.md](../../research/validation/REPORT.md) §21.2, [SQX_build_matrix.md](SQX_build_matrix.md))

The noise band needs a custom indicator: the 14-day average move from the open at each time of day. R3
tested 12 native versions on US100, 2014-01 → 2026-08:
- **Bands:** the session open ± k × (the prior session's range, or ATR(14) of session bars), k ∈ {0.3, 0.5, 0.7}.
- **Entry:** stop orders; the first touch enters.
- **Exit:** flat at 15:59, or stop-and-reverse.
- **Costs:** 1.5 bps per entry.

**Results:**
- **Median Sharpe 0.47,** against 0.52 for N3 on the same data (89%; the pre-registered bar was 70%).
- **Median daily correlation with N3: 0.58** (bar: 0.5). **Native build recommended.**
- All 12 variants are positive in both 2014–19 and 2020–26.
- The best is the prior-range band with k = 0.5: Sharpe 0.91 flat, 0.94 reverse (post hoc).
- US500: still nothing (N1 0.13; native median 0.04).

**Prop (A25, 12-variant book with the news blackout):**

| Account | Fixed 1× | Fixed 3× | CPPI k = 10 |
|---|---|---|---|
| FTMO 2-Step Standard | 57% pass (zero edge 31%), $660 per account-month | $1,927 | 65% (21%) |
| FTMO 1-Step | 56% (34%), $824 | $1,678 | 72% (29%) |
| Topstep 50K | — | 2×: $261 | negative EV |

The book is lumpy by year (2020 −25%, 2022 +59% at 1×) and uncorrelated with the reversal book (0.06). Run it in its own account.

## Own-data validation (round 5, family N; [REPORT.md](../../research/validation/REPORT.md) §14.4–15)

Paper-exact rule (14-day lookback, 30-minute marks, bands from max/min of open and prior close, flip at
the opposite band, flat at the close) on HistData minute data, 2014–2025, 100% notional, 1.5 bps per
entry (gold 2.5):

| Test | Net bps/day | t | Sharpe | Verdict |
|---|---|---|---|---|
| N1 US500, conservative (the paper's instrument; paper Sharpe 0.61 on SPY) | +0.70 | 0.69 | 0.20 | NOT CONFIRMED |
| N2 US500, TWAP trailing stop (VWAP not available) | +1.09 | 1.58 | 0.44 | NOT CONFIRMED |
| **N3 US100, conservative** | **+3.02** | **2.54** (Holm 0.028) | **0.73** | **CONFIRMED** |
| N4 GER40 (09:00–17:30 Berlin) | +0.64 | 0.53 | 0.15 | NOT CONFIRMED |
| N5 Gold (COMEX 08:20–13:30) | +0.44 | 0.62 | 0.18 | NOT CONFIRMED |

N3 robustness (post hoc): lookback 10/20 → +3.05/+3.19; 60-min grid +2.65; 15-min grid +1.88 (t = 1.4);
cost 3 bps +2.11 (t = 1.8); TWAP stop +3.06 (t = 3.5, Sharpe 0.96); **unseen 2011–13 +2.93** (t = 1.3);
2014–19 +1.37, 2020–25 +4.86. DSR over ≈ 731 trials: 0.22.

Prop (two-step 10%/5%, 3% guard): 40% pass at 2× in ~6 months; TWAP-stop variant 52% at 3× in ~4.5
months; zero-edge ≈ 11%.

**Interpretation:** a US100-specific effect with a plausible flow mechanism: leveraged Nasdaq-100 ETFs
(TQQQ/SQQQ) rebalance with the day's move into the close, and their size relative to the market is much
larger in the NDX than the S&P. But it failed on the paper's own instrument, and one pass among ~730
hypotheses could be chance. Forward-test 6 months before live.

## Round 7 ([REPORT.md](../../research/validation/REPORT.md) §17)

- **2026 holdout (A14, first untouched data, 162 sessions to 2026-09-18):** +1.39 bps/day (t = 0.33).
  - That is **CONSISTENT** with the in-sample +3.02 (z = −0.37) but uninformative: the pre-registered power was 15%, and the Bayes factor is ≈ 1.
  - The pooled estimate is +2.9 bps/day.
  - The TWAP-stop variant earned −1.46 in 2026.
- **Paper's own sizing (I3):** exposure = min(4, 2% ÷ 14-day realized volatility) **lowers** Sharpe from 0.73 to 0.57 in 2014–25. The rule earns more when volatility is high, exactly when volatility targeting cuts size. **Keep flat sizing.**
- **News blackout (as FTMO funded Standard accounts require):** no action at the 10:00 mark on ISM days or at 14:00/14:30 on FOMC days. The mean falls from 3.02 to 2.68 bps/day (−11%).
- **Related US100-only effects:** the Williams breakout (G10: US100 t = 3.9) and the last-hour reversal (G7: US100 t = 2.9) are also strongest on US100. Both failed their 2026 holdout. They may be the same underlying effect; don't stack them as independent edges.
- **Second data feed (X1, Dukascopy): not done.** The feed was throttled in this session. **Run it before funding N3.** The same code accepts any minute feed through `run(..., ses=...)`.
- **Published firm terms (A16, fixed 4×, 2014–25 book):**

  | Venue | Pass (zero edge) | EV per attempt | Months | EV per account-month |
  |---|---|---|---|---|
  | **FTMO 1-Step** (news-filtered) | 37% (25%) | $2,271 | 2.3 | **$983** |
  | FTMO 2-Step Swing | 31% (17%) | $2,189 | 2.8 | $772 |
  | FTMO 2-Step Standard (news-filtered) | 31% (16%) | $2,043 | 2.9 | $715 |
  | Topstep 50K (3×) | 23% (14%) | $109 | 0.9 | $124 |

  CPPI k = 10 (cap 3×) passes 71–78% on FTMO against 16–22% for zero edge, but runs about five years per account.

## Evidence

| Source | Level | Sample | Result |
|---|---|---|---|
| Zarattini, Aziz & Barbon, "Beat the Market", SSRN 4824172 (v. 3 Feb 2025) | V1 (WP) | SPY, 2007 – early 2024; $100k start; commission $0.0035/share + slippage $0.001/share | See table below |

| Version (paper's Table 2) | Total | IRR | Vol | Sharpe | Hit | Max DD |
|---|---|---|---|---|---|---|
| Stop at opposite band, 100% sizing | 178% | 6.2% | 10.9% | 0.61 | 54% | 21% |
| Stop = current band or VWAP, 100% sizing | 380% | 9.7% | 7.7% | 1.24 | 43% | 12% |
| Same + dynamic sizing (2% daily vol target, ≤ 4×) | 1,985% | 19.6% | 14.3% | 1.33 | 43% | 25% |
| SPY buy-and-hold | 227% | 7.2% | 20.2% | 0.45 | 54% | 56% |

**Caveat:** most of the jump from 0.61 to 1.24 Sharpe comes from one design change, the exit rule. That
was chosen with the full sample in view. Treat 0.61 as the conservative baseline and 1.24 as an upper
bound.

## Paper-exact spec

```
For each day t and each intraday time HH:MM (market hours, 30-minute grid):
  move(t−i, HH:MM) = | Close(t−i, HH:MM) / Open(t−i, 09:30) − 1 |,  i = 1..14
  sigma(t, HH:MM)  = mean_i move(t−i, HH:MM)
  UB(t, HH:MM) = max(Open(t, 09:30), Close(t−1, 16:00)) × (1 + sigma)
  LB(t, HH:MM) = min(Open(t, 09:30), Close(t−1, 16:00)) × (1 − sigma)
Signals evaluated ONLY on :00 / :30 marks:
  price > UB → long;  price < LB → short;  opposite-boundary cross → flip
Trailing stop (checked on the same marks): long = max(UB, VWAP), short = min(LB, VWAP); VWAP from market-hours data
Flat at 16:00.
Sizing: shares = AUM(t−1) × min(4, 0.02 / sigma_SPY(t)) / Open(t);  sigma_SPY = 14-day stdev of daily returns
```

## Replication targets

SPY 2007 → early 2024, 100% sizing, VWAP stop, same costs: Sharpe around 1.2, hit rate around 43%, max
drawdown around 12%.

## Prop-rule constraints

- **News windows:** the 10:00 ET decision mark coincides with several US releases (ISM, JOLTS, consumer confidence, new home sales). FTMO funded Standard accounts ban opening or closing trades within 2 minutes of high-impact news; the Swing type doesn't. The tested blackout (`run(..., skip=...)` in [run_noise_area.py](../../research/validation/run_noise_area.py); dates in `prop_lifecycle_real.news_skip`) takes no action at those marks and carries the position. It costs 11% of the edge.
- **Intraday only:** flat by 16:00, so there is no overnight or weekend exposure and no swap.

## Adapting to SQX

- Needs a **custom indicator**: per-time-of-day average absolute move from the open over 14 days. It isn't a standard SQX block. VWAP is also required (custom if absent).
- CFD volume for VWAP is tick volume, not real volume. Test with futures data if possible, or use TWAP as a documented substitute.

## Falsification tests

1. Paper-window replication (above).
2. Post-2024 data is not negative.
3. Robust to lookback 10/14/20 days and a 15/30/60-minute grid (plateau, not peak).
4. Works on at least one more index (US100 or GER40) with unchanged parameters.
