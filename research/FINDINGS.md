# Curated findings: edges and portfolios for StrategyQuant X and prop-firm challenges

*Ten rounds of pre-registered research, September 2026. No Treasury strategies (user scope).
Every number's source: [validation/REPORT.md](validation/REPORT.md). Test definitions, committed before
each test: [validation/PREREGISTRATION.md](validation/PREREGISTRATION.md). Every variant with its
statistics: [strategy_library.csv](strategy_library.csv).*

## The verdict

**One edge family is robust enough to build a portfolio on: short-term reversal in US equity indices (and the Nikkei).**
- **Scale of the test:** round 9 explored it as a grid of 864 variants (12 entry signals, 3 exits, 3 regime filters, 8 indices).
- **It passes every multiple-testing check:**
  - Hansen SPA p = 0.03 on timing value;
  - probability of backtest overfitting 0.19;
  - walk-forward Sharpe 0.47 (t = 2.1).
- **Breadth:** 79–94% of the US variants are positive after 2013.
- **Ensemble:** trading them together gives Sharpe 0.9–1.0 in 2013–26.

MR-06, found in round 1, is one member of this family.

**A second, narrower edge:** noise-area intraday momentum works on **US100 only**. Its family of 324 variants on 9 markets is weak overall, but US100 is significant on its own (SPA p = 0.036). A second data feed agrees (correlation 0.99).

**Real, but not for prop accounts:** trend following (weak after data-snooping; CFD financing eats it).
G10 carry and currency momentum died after 2012.

**Round 10 searched for more edge families.** Seven new families, 3,768 variants:
- reversal outside equities;
- per-market trend and breakout;
- index-pair relative value;
- calendar effects;
- crypto trend;
- reversal on more indices;
- cross-sectional stock reversal.

None adds an independent edge. The only rule-based "edge family" among them is US tech again (the Nasdaq Composite), plus one isolated Euro Stoxx 50 variant. Adding it to the portfolio lowered the out-of-sample Sharpe. Round 10 also caught a data artefact: Yahoo daily FX bars fake a huge FX reversal edge that disappears on clean data.

About 750 single hypotheses and 5,014 family variants were tested in total. Everything not listed above
failed out of sample or after costs ([§5](#5-what-not-to-build)).

---

## 1. The strategy book

| Sleeve | What | Evidence | Build as |
|---|---|---|---|
| **Core: index reversal** ([card](../evidence/edges/REV_index_reversal_family.md)) | Buy US500/US100/US30/US2000/JP225 after short-term weakness, at the close. Signals: IBS < 0.10–0.25, RSI(2) < 5–20, 2–5 down closes, 5/10-day low. Exit at the first up close (max 5 days) or the next close | Edge family (SPA 0.03, PBO 0.19, walk-forward t = 2.1). **Tier 1** (survives Romano–Wolf): US100 IBS < 0.10 and US100 RSI(2) < 20, both exiting at the first up close. **Tier 2:** 218 robust variants | **10–20 de-correlated variants per market** (≈ 8 independent bets in the US set), volatility-scaled, gross-exposure cap per index |
| **Satellite: US100 intraday momentum** ([card](../evidence/edges/IM-04_noise_area_momentum.md)) | Noise-area breakout on US100, flat at 16:00. 19 robust variants (lookback 7–28, band 0.8–1.25, 30/60-min marks) | Candidate: +3.0 bps/day (2014–25); US100 SPA 0.036 within its family; second feed agrees; 2026 +1.4 bps/day | A few variants in a **separate account**. Paper-trade first |
| Optional: MR-06's intraday half | Buy the 09:30 open after three down closes, sell at 16:00 | Weak by rule; SPY 1993–2026 +10.5 bps/trade, t = 2.65 | Only for flat-by-close accounts |
| Small add-on: pre-holiday | Long the session before a US holiday | +12 bps, t = 3.25 (round 1) | ~9 trades/yr |
| Not for prop | Trend following, FX carry, currency momentum | Weak or none after 2012–17; financing costs | Long-term, low-cost portfolios only |

**Choosing variants within the reversal family** (median validation timing Sharpe):

| Choice | Best | Worst |
|---|---|---|
| Signal | IBS < 0.10 (0.44) | a large down day (0.09) |
| Exit | first up close (0.38) | fixed 3 days (0.20) |
| Filter | **none (0.37)**; below SMA(200) (0.35) | above SMA(200) (0.19), even though it's the popular choice |
| Market | US100 > US500 > US2000 > US30; JP225 adds diversification (correlation ≈ 0.1) | DAX, FTSE, ASX: no edge |

The full list, with discovery, validation and 2026 statistics per variant and a robustness tier, is
[strategy_library.csv](strategy_library.csv).

---

## 2. Does a portfolio built this way work out of sample?

Round 9 tested exactly that:
- **Selection:** from every family, strategies were chosen *only on pre-2020 data*: top discovery Sharpe, positive parameter neighbours, correlation ≤ 0.6.
- **Weights:** equal risk across families.
- **Evaluation:** 2020–25 and 2026.

| Book, out of sample 2020–25 | Sharpe | Return / volatility | Max drawdown |
|---|---|---|---|
| **Portfolio (all families)** | **0.69** (t = 1.8) | 6.2% / 9.0% | −20% |
| **Reversal part** | **0.79** (t = 2.1) | 3.7% / 4.7% | −6% |
| Intraday-momentum part | 0.34 | 2.1% / 6.1% | −14% |
| Trend part / FX part | 0.02 / 0.08 | — | — |
| Naive: all 1,246 variants equal-risk | −0.07 | — | −20% |
| The single best discovery variant | 0.44 | — | −18% |

**2026 so far:** portfolio 0.42; reversal part 1.81.

**Lessons:**
1. **Selection rules beat blind diversification.** Robustness plus de-duplication worked; equal-weighting everything failed.
2. **The families are uncorrelated** (−0.10 to +0.09), but diversifying into families with no edge only diluted the return. **Build the portfolio around the reversal family.** Add intraday momentum as a separate sleeve.

---

## 3. Prop accounts: where and how much

| Book | Account | Size | Pass rate (zero edge) | EV per attempt | Per account-month |
|---|---|---|---|---|---|
| **Reversal ensemble, 4 US indices** | FTMO 2-Step $100K (Swing) | 1× (≈ 15% annual vol) | **70% (26%)** | $7,649 | $452 |
| | | 2× | 52% (19%) | $6,981 | **$995** |
| | | CPPI k = 10 | **74% (12%)** | $6,215 | $213 |
| **Reversal ensemble, US + JP225** | FTMO 2-Step Swing | CPPI k = 10 | **80% (17%)** | $8,644 | $335 |
| | FTMO 1-Step $100K | 2× | 49% (18%) | $4,976 | **$1,103** |
| US100 intraday momentum (N3) | FTMO 1-Step, news-filtered | 4× | 37% (25%) | $2,271 | $983 |
| MR-06 alone | FTMO 2-Step Swing | 3× | 47% (13%) | $3,654 | $210 |

**How to read it:**

- **The ensemble is the biggest practical gain of this research.** The same edge traded through many variants reaches targets 3–5× faster than the single MR-06 rule, at similar risk.
- **Run the reversal ensemble and US100 momentum in separate accounts.** They are uncorrelated (0.03). A multi-market book in *one* account is fragile: its prop result swings from failure to success with how intraday lows are modelled (§19.3 of the report).
- **Sizing by objective:**
  - fixed 1–2× maximises money per month;
  - cushion (CPPI) sizing maximises the chance of passing (74–80% vs 12–17% for zero edge), slowly;
  - keep the EA daily guard (2–3%).
- **The reversal family needs overnight and weekend holds** (FTMO Swing). Flat-by-close futures firms can't hold it.
- **Discount the figures:**
  - The ensemble was chosen after seeing the family result, and 2013–26 is also the period that qualified the family, so treat its figures as upper bounds.
  - The simulator gives zero-edge books positive EV (the funded-account option), so only the gap to the zero-edge twin is yours.
  - **Planning case:** half the in-sample figures.

---

## 4. Paper trading: what it can show

| Edge | Forward time to t = 2 | Pre-set stop rule |
|---|---|---|
| Reversal ensemble (Sharpe ≈ 0.9) | ≈ 5 years | Stop if the 6-month forward Sharpe is below −2.4 (1% one-sided vs +0.9) |
| US100 momentum (N3) | ≈ 7.5 years | Forward mean below −10.6 bps/day after 126 days |
| MR-06 alone | ≈ 10 years | Below −7.9 bps per trade after 126 trades |

A 3–6-month forward test is an **implementation check** (fills, times, costs match the backtest), not
validation. The funding decision rests on the out-of-sample and multiple-testing evidence above, sized
so that being wrong is affordable.

---

## 5. What not to build

| Group | Tested and failed |
|---|---|
| Reversal outside its markets | DAX, FTSE and ASX 200 reversal (864-variant family; per-index SPA p 0.53–0.68); 15 other world indices (W1); single large stocks (H3: +1 bp net) |
| Intraday momentum outside US100 | Noise-area on US500 (positive, not significant), DAX, CAC, FTSE, Nikkei, ASX, Hang Seng, gold. Last-30-min, first-half-hour, GER40/CAC/FTSE close momentum, commodity and crude-oil momentum, Bitcoin momentum |
| Breakouts | 5- and 30-min ORB, Asian-range at the London open, Williams volatility breakout, NR7, gap fades |
| Trend and cross-section | 48 trend variants (walk-forward t = 0.9, PBO 0.61), crypto trend, momentum across 14 equity indices, volatility-managed exposure |
| FX | G10 carry (dead after 2012 net of swaps), currency momentum (negative), FX fix windows (daily and month-end), post-fix reversal |
| Calendar and flows | Turn of month, overnight drift, FOMC day and cycle, announcement premium, Halloween, options-expiration weeks, rebalancing flows, Treasury auction cycle, Bitcoin hours/Monday, crypto weekend, earnings-announcement premium in large stocks |
| Systematic scan | 653 time-of-day, day-of-week, streak, IBS and breakout candidates on 24 instruments: 0 confirmed |
| Round 10 families (3,768 variants) | Reversal on gold, silver, oil, gas, FX and crypto (none); per-market Donchian, MA and momentum trend on 22 markets (no timing value); index-pair relative value (none); calendar grid (weak); crypto trend on the 2019 top-8 coins (weak); reversal on HK50, FRA40, SPA35 (none) and EU50 (one isolated variant); cross-sectional weekly reversal in large stocks (all negative) |

Detail: [R5 negatives](../evidence/edges/R5_prop_instrument_negatives.md), [R7 negatives](../evidence/edges/R7_negatives.md), REPORT §3–§19.

---

## 6. How far to trust this

**Strong:**
- Pre-registration with git timestamps.
- Family-level multiple-testing control: SPA, Romano–Wolf, PBO and deflated Sharpe over the cumulative trial count.
- Walk-forward selection, and a discovery-only portfolio evaluated out of sample.
- A second data feed for US100.
- The 2026 holdout. Earlier WEAK rules behaved like noise there, which confirms the filters work.

**Disclosed judgement calls in round 9:**
- Long-only books are judged on timing value, so the equity premium doesn't count as edge.
- That benchmark proved invalid for trend strategies, so trend reverted to its raw verdict.
- Every verdict is reported under all benchmarks.

**Weak points:**
- The prop figures are in-sample or post hoc.
- Firm terms change.
- The reversal edge is regime-dependent (stronger since 2020) and clusters its exposure in sell-offs.
- US100 momentum has a low deflated Sharpe (0.22) and no verified mechanism.

---

## 7. Next steps, by value

1. **Build the reversal ensemble in SQX from Tier 1/2 of the library.** Replicate it on the broker's data, and check that ≥ 80% of the chosen variants are positive after 2013 ([card](../evidence/edges/REV_index_reversal_family.md) falsification tests).
2. **Put the chosen firm's exact terms into `tools/propsim`**, choose fixed or CPPI sizing by objective, and cap gross exposure per index.
3. **Run US100 momentum in its own account** after a second-feed check of the 30-minute rule on the broker's data.
4. **Paper-trade both for 3–6 months** as an implementation check, with the stop rules above.
5. New research only after that: the remaining untested ideas have low priors.

---

## Where things are

| Need | File |
|---|---|
| Every variant, with statistics and tier | [strategy_library.csv](strategy_library.csv) |
| Every result, per round | [validation/REPORT.md](validation/REPORT.md): §1 bottom line, §19 round 9, §20 round 10, §21 appraisal, §22 plan |
| Test definitions and amendments | [validation/PREREGISTRATION.md](validation/PREREGISTRATION.md) (A22 = round 9) |
| Edge cards, negatives, agent brief | [../evidence/](../evidence/README.md) |
| Statistics module (SPA, Romano–Wolf, PBO, walk-forward) | [validation/multitest.py](validation/multitest.py) |
| Prop simulator and firm presets | [../tools/propsim/](../tools/propsim/README.md) |
