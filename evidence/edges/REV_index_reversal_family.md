# REV — Short-term reversal family in equity indices (MR-06 is one member)

**Verdict:** BUILD as the core sleeve. It is the only **edge family** in eleven rounds (round 9, [REPORT.md](../../research/validation/REPORT.md) §19), and it **survives the way SQX would trade it** (round 11, §21) · **Grade:** A− on own data (family-level, multiple-testing adjusted) · **Prop fit:** Medium–high as an ensemble. It needs overnight holds but not weekend holds; size it for survival (crash clustering) · **Markets:** US500, US100, US30, US2000, JP225. **Not** GER40, UK100, AUS200

## Claim and mechanism

After short-term weakness, US index products (and the Nikkei) earn above-normal returns over the next
one to few sessions. The signal can be consecutive down closes, a close near the day's low, a low RSI(2)
or a fresh N-day low; the effect is the same. The mechanism is liquidity provision against index-level
price pressure:
- Baltussen, van Bekkum & Da (2019, *JFE*): index-level serial dependence turned negative as index products grew.
- Nagel (2012, *RFS*): reversal returns as compensation for liquidity provision.

## Evidence (own data, pre-registered in A22)

| Test | Result |
|---|---|
| Grid | 8 indices × 12 signals × 3 exits × 3 filters = **864 variants**; discovery 1993–2012, validation 2013-01 → 2026-08 |
| Hansen SPA, validation (does any variant beat zero after data snooping?) | **p = 0.031** on timing value (P&L minus exposure × the index's same-year mean); 0.0125 with an expanding-mean benchmark; 0.0005 raw |
| CSCV probability of backtest overfitting | **0.19**: picking the in-sample best usually picks a good out-of-sample variant |
| Selection test | The top 10% of discovery variants beat the rest in validation (Mann–Whitney z = 7.0) |
| Walk-forward (re-pick the top 5 each January on past data) | **Sharpe 0.47, t = 2.1** on timing value; raw 0.69, t = 2.9 |
| Romano–Wolf survivors (family-wise 5%) | US100 **IBS < 0.10, exit at the first up close** (timing Sharpe 0.96, 23 trades/yr); US100 **RSI(2) < 20, first up close** (0.80, 28 trades/yr). 17 survive on raw P&L |
| Breadth | 79–94% of each US index's 108 variants have positive timing value in 2013–26. JP225 per-index SPA p = 0.007 |
| Ensemble (every variant, weighted by discovery volatility) | US100: validation Sharpe **1.00 (t = 4.7)**; 4 US indices + JP225: 0.90 (t = 4.0) |
| Independent bets | ≈ 8 effective bets among the 432 US variants (median correlation 0.28); US vs JP225 ≈ 0.1 |
| Costs | +3 bps per trade leaves 95% of US variants positive |
| Earlier rounds | MR-06 (three down closes): confirmed out of sample 2013 → ; 15:55 entry works; about half the edge is intraday; 2026 +44 bps over 23 trades |

## Parameter map (median validation timing Sharpe over the US variants)

| Choice | Best | Weaker |
|---|---|---|
| Signal | IBS < 0.10 (0.44); 2/3/5 down closes, RSI(2) < 10–20, 5-day low (0.33–0.34) | 4 down closes (0.22), return < −1.5σ (0.09) |
| Exit | First close above the prior close, max 5 days (0.38); next close (0.34) | Fixed 3 days (0.20) |
| Filter | None (0.37); only below SMA(200) (0.35) | **Only above SMA(200) (0.19)**: the popular uptrend filter hurts |
| Market | US100 > US500 > US2000 > US30; JP225 | GER40, UK100, AUS200 (no edge) |

## SQX build spec (ensemble; round 11, full detail in [SQX_build_matrix.md](SQX_build_matrix.md))

Round 11 (R1) re-ran the 108-variant grid three ways on HistData CFD quotes, 2014-01 → 2026-08. Figures are ensemble timing-value Sharpes, with the per-market SPA p for US100:

| Build | US500 + US100 | + JP225 | US100 SPA p |
|---|---|---|---|
| Research (Yahoo closes, entry at the close) | 0.65 | 0.67 | 0.010 |
| **(c) M5 chart, D1 cash-session conditions, signal/entry/exit at 15:55** | **0.53** | **0.58** | 0.024 |
| (c) without weekend holds (R2) | 0.52 | 0.59 | 0.009 |
| (a) broker D1 bars (17:00 NY), next-open orders | 0.48 | 0.42 | 0.017 |
| (b) cash-session D1 bars, next-open orders | 0.41 | 0.31 | 0.012 |

Two findings decide the build:
- **JP225 needs the pre-close entry.** Under (b) it has no edge (−0.04), and under (a) it keeps 64% of (c).
- **Controls stay negative under every build:** GER40 and gold.

```
Markets:  US500, US100, JP225 (+ US30, US2000 from family A)
Chart:    M5 main chart + D1 chart on a cash-session definition (Data Manager -> Sessions):
          US 09:30-16:00 NY; Tokyo 09:00-15:00 JST (15:30 from 2024-11-05)
Signals (each a separate strategy), evaluated at 15:55 NY (JP225 14:55 JST / 15:25 from 2024-11-05):
  IBS = (C - L)/(H - L) of today's session so far < 0.10 | < 0.25
  RSI(2) (Wilder) < 5 | < 10 | < 20
  k consecutive lower closes, k in {2, 3, 5}
  close = lowest close of 5 | 10 sessions
Entry:    market at 15:55
Exit:     15:55 on the first session that closes above the previous close, max 5 sessions | or the next session's 15:55
Filter:   none, or only when close < SMA(200) (never the "above SMA(200)" filter: worst under every build)
Weekend:  FTMO Standard: no entry on the last session of the week; exit at Friday's 15:55 (R2: no Sharpe cost)
Fallback: US only: broker D1 bars, market at the next open (keeps ~90% of (c))
Stops:    catastrophic only (e.g. 3 x ATR); stops hurt mean reversion (not tested in R1)
Sizing:   equal risk per market; cap total gross notional (signals cluster on crash days)
Portfolio: pick 10-20 per market from the 141 Tier 1/2 variants that are positive under all three builds
           (research/sqx_implementation_grid.csv), de-duplicated at correlation 0.6
Prop:     EA daily guard 2-3%; FTMO 2-Step Standard or Swing; CPPI or <= 1x (A25)
Check first: how SQX exposes today's unfinished D1 bar at 15:55 (SQX_build_matrix.md, check 1)
```

## Prop results (post hoc ensemble, [prop_ensemble.py](../../research/validation/prop_ensemble.py))

- **Setup:** weights from pre-2013 data; exact per-index intraday lows; bootstrapped from 2013–26; 1× ≈ 15% annual volatility.
- **FTMO 2-Step:**
  - 1×: 70% pass (zero edge 26%), $7,649 per attempt, 17 months, $452 per account-month;
  - 2×: 52% pass, $995 per account-month;
  - CPPI k = 10: 74% pass (zero edge 12%).
- **FTMO 1-Step, US + JP225, 2×:** 49% pass (zero edge 18%), $1,103 per account-month.
- **Treat these as upper bounds.** The ensemble idea came after the family result, and 2013–26 is also the period that qualified the family.

**Round 11 (A25): the SQX build as a prop book.** Book B8/B8w: build (c), every variant equally weighted, exact intraday lows, 2014–26:
- **Book statistics:**
  - Sharpe 0.82 with weekend holds, 0.79 without;
  - 14.6–14.8% a year at 17.8–18.8% volatility at 1×;
  - positive in 12 of 13 years with weekend holds, 10 of 13 without.
- **Pass rates** (zero-edge twin in brackets):

  | Account | Fixed 1× | CPPI k = 10 |
  |---|---|---|
  | FTMO 2-Step Swing | 42% (10%), $342 per account-month | 53% (7%) |
  | FTMO 2-Step Standard | 35% (7%), $254 | 49% (6%) |
  | FTMO 1-Step | 26% (7%), $158 | 50% (7%) |

- **Why it is lower than the post hoc round-9 figures** (70% at 1×):
  - the CFD-quote Sharpe is lower;
  - **the crash tail:** the worst day at 1× was −18% on 2020-03-12, with other bad days on 2015-08-25, 2024-08-05 and 2025-04-07.

  Size for survival.

## Round 12: where the return is earned, and the short side ([REPORT.md](../../research/validation/REPORT.md) §22)

**Exit timing (family T).** The same signals were entered at 15:55 with one-day exits. Ensemble Sharpe on timing value, 2014–26:

| Exit | Sharpe | Reading |
|---|---|---|
| Next 03:00 NY (after the European open) | −0.29 | Nothing |
| Next cash open | 0.23 | A third of the edge |
| **Next 15:55** | **0.69** (2020–26: 0.95) | The edge |

- Overnight-only exits are significantly worse: bootstrap intervals −0.99 [−1.51, −0.50] and −0.46 [−0.79, −0.11].
- **Hold US legs through the next session.**
- **JP225 is earned overnight,** during the US session: exiting at the next Tokyo open works (per-market SPA 0.002).
- **Mechanism.** The European-open overnight drift (Boyarchenko et al. 2023) died after 2021 on our data too, while this edge stayed strong. The reversal is not that inventory effect. Liquidity provision against index-level price pressure (Nagel 2012; Baltussen et al. 2019) remains the reading.

**Short side (family S).** Selling after strength has at most a sliver of timing value and a negative raw P&L. The edge is long-only.

## Round 15: where the edge is paid ([REPORT.md](../../research/validation/REPORT.md) §22.1)

Family A's variants, 2007–26, were split by the VIX term structure at the signal close. Stress means VIX ≥ VIX3M, on 11% of days.

| | US indices | JP225 (**withdrawn in round 16:** look-ahead) |
|---|---|---|
| Timing value per trade, stress entries | **+56 bps** | −29 bps |
| Timing value per trade, calm entries | +5 bps | **+16.5 bps** |
| Ensemble Sharpe, all → calm-only | 0.54 → 0.27 | 0.20 → 0.51 (difference interval [+0.04, +0.65]) |

- **The US edge is a stress-regime liquidity premium,** as Nagel (2012) predicts. Filtering stress out would halve it while cutting the worst day by 38%. Control the tail with size, not a filter.
- **~~JP225 is the reverse~~ (withdrawn, round 16).** That split used a VIX close published after the Tokyo close. With the prior US close, JP225 shows no regime effect: no filter.
- **No VIX needed (round 16).** The US split shows on US500 alone: when it is ≥ 9% below its 60-day high, trades earn +71 bps against +4 in calm markets.
- **Round 14 (XR):** the US signal does not transmit to risk currencies or gold. The rebound is specific to index products.

## Round 17: the same edge on standard SQX indicators, and US30 / US2000 ([REPORT.md](../../research/validation/REPORT.md) §22.3)

The 540-variant family RB used 12 new entry signals:

| Signal | Rule |
|---|---|
| ST10, ST20 | Stochastic %K(14) < 10 / < 20 |
| WR5 | Williams %R(5) < −95 |
| BB0 | Bollinger %B(20, 2) < 0 |
| KC2 | Close < EMA(20) − 2 × ATR(10) |
| CR10, CR15 | Connors RSI < 10 / < 15 |
| LL3 | 3 lower lows in a row |
| ATP | Close < SMA(5) − ATR(10) |
| CUM35 | 2-day cumulative RSI(2) < 35 |
| PR5 | 5-day return in the bottom decile of its 252-day history |
| WRB | Wide-range bar with IBS < 0.25 |

It is an **EDGE FAMILY** in its own right:
- **Battery:** SPA 0.031 on timing value (0.001 raw); walk-forward t 2.7.
- **Breadth:** 100% of SPY and QQQ variants positive in 2013–26; US30 90%, US2000 78%, JP225 94%.
- **Library:** 189 Tier 1/2 variants (75 US100, 61 US500, 25 US30, 17 US2000, 11 JP225).
- **Same edge:** it correlates 0.93 with family A. Use it for more building blocks and more markets, not for diversification.
- **Best choices:** cumulative RSI(2) < 35, Stochastic %K(14) < 10, Bollinger %B < 0, ATR pullback; exit at the first up close.
- **The "above SMA(200)" filter** is harmless with these signals.

## Round 18: RB in the SQX build, and sizing ([REPORT.md](../../research/validation/REPORT.md) §22.4)

**RB in the M5/15:55 build** (HistData CFD quotes, 2014 → 2026-08, 108 variants per market):

| Market | Variants positive | Ensemble timing Sharpe: build / daily close | Kept |
|---|---|---|---|
| US100 | 100% | 0.63 / 0.64 (SPA 0.024) | 98% |
| JP225 | 88% | 0.30 / 0.28 | 107% |
| US500 | 95% | 0.37 / 0.52 | 72% |

**Sizing:**
- **Use fixed notional per trade.** Volatility-scaled size (min(2, 1% ÷ σ20)) was tested on the US daily ensemble.
- **What it did:** the worst day went from −9.9% to −13.9% and the max drawdown from −25.2% to −27.6%.
- **Pass rates:** the FTMO 2-Step edge-adjusted pass rate fell (+37 vs +46 points over zero edge). Rejected by the pre-registered rule.

## Known risks

- **Crash clustering:** signals fire together in sell-offs (2008, 2020, 2022), so exposure concentrates in the worst weeks. Cap gross exposure and use the daily guard.
- **Regime:** stronger since 2020 (volatile). Absent before 1990 on US data. US-centred.
- **Weekend holds:** a Standard FTMO funded account forbids them. Skip Friday signals there (for MR-06 this cost about a third of the value in 2014–25).
- **Futures prop firms** that force flat by the close can't hold it. Only the intraday half works there (MR-08, weak).

## Falsification tests for the SQX build (round 11 adds 5 and 6)

1. On the broker's data, 2013 → : ≥ 80% of the chosen variants have positive net P&L, and the ensemble has Sharpe > 0.5.
2. The "above SMA(200)" filter is worse than no filter (a mechanism check).
3. The ensemble survives +3 bps per trade.
4. The per-market ensembles on DAX, FTSE and ASX show no edge. A positive result there would mean the build differs from this research.
5. Build (c) ≥ build (a) on US indices; JP225 is much weaker under (a) and has no edge under (b).
6. The no-weekend version is within ±0.1 Sharpe of the full version.
