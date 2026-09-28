# Curated findings: edges and portfolios for StrategyQuant X and prop-firm challenges

*Forty-three rounds of pre-registered research, September 2026. No Treasury strategies (user scope).
Every number's source is [validation/REPORT.md](validation/REPORT.md). Test definitions, committed before
each test, are in [validation/PREREGISTRATION.md](validation/PREREGISTRATION.md). Every variant, with its
statistics, is in [strategy_library.csv](strategy_library.csv). How to build each edge in SQX:
[SQX build matrix](../evidence/edges/SQX_build_matrix.md).*

## The verdict

**One edge family is robust enough to build a portfolio on: short-term reversal in US equity indices (and the Nikkei).**
- **Scale of the test:** round 9 explored it as a grid of 864 variants (12 entry signals, 3 exits, 3 regime filters, 8 indices).
- **Multiple-testing checks:**
  - Hansen SPA p = 0.03 on timing value;
  - probability of backtest overfitting 0.19;
  - walk-forward Sharpe 0.47 (t = 2.1).
- **Breadth:** 79–94% of the US variants are positive after 2013. MR-06, found in round 1, is one member.

**Round 11 checked that SQX can actually trade it:**
- **The recommended build:** an M5 chart with daily conditions on the cash session; signal, entry and exit at 15:55 NY. On CFD quotes it keeps **82–87% of the research Sharpe**, and its daily P&L correlates 0.87–0.89 with the research version.
- **Broker daily bars** (17:00 NY close, next-open orders) work for US500/US100, not for JP225.
- **Weekend holds are not needed:** without them, the Sharpe is the same. FTMO Standard accounts are fine.
- **141 variants** are positive under all three SQX builds: [sqx_implementation_grid.csv](sqx_implementation_grid.csv).

**A second, narrower edge: intraday momentum on US100 only.**
- It is significant within its own family (SPA p = 0.036), and a second data feed agrees.
- **Round 11:** SQX can build it from standard blocks. At 09:30, place stop orders at the open ± 0.5 × yesterday's range, and go flat at 15:59. The native 12-variant grid keeps 89% of the original rule's Sharpe.

**A third edge, and the first in FX (round 19): the Tokyo fix on Gotobi days.**
- **Mechanism:** Japanese importers buy dollars at their banks' 09:55 JST fixing on the 5th, 10th, 15th, 20th, 25th, 30th and at month-end. Banks buy ahead of the fix, and USD/JPY gives the move back after it (Ito & Yamada 2017).
- **Rule:** sell USDJPY at 09:55 JST on those days and buy back at 10:55. Pre-registered and tested after the paper's sample (2014–26).
- **Result:** +2.1 bps gross and **+1.1 net per trade (t 2.6, Holm p 0.010)**, positive in both halves and in 22 of 24 years. The 42-variant grid passes the family battery (SPA 0.027, PBO 0.05).
- **Checks:** every JPY pair shows it; EURUSD, GBPUSD and the other non-JPY pairs don't; a second data feed agrees.
- **Confirmed on unseen data (round 20):** JPY crosses 2002–07 earn +2.80 bps gross (t 4.5), +1.9 above ordinary days (t 2.8). EURJPY alone earns +1.8 net (t 3.1), so it may join USDJPY.
- **Build choices (round 20):** keep the 10:55 exit. Add a buy stop at entry + 20 bps: it keeps 97.5% of the edge and cuts the worst trade from −84 to −21 bps.
- **Limits:** it is small. It needs a raw-spread account (round trip ≤ 1 bp) and an order at the fix minute: a 1-minute delay loses 40%.
- **Prop:** in its own FTMO 2-Step account, with the stop, it passes 74% at 10× notional (zero edge 29%) and 50% at 20× (26%), post hoc. The worst day is −2.1% / −4.2%.

**FX and metals otherwise: no tradeable edge after costs.** Round 11 added four families built for prop accounts (292 variants):
- FX session seasonality;
- FX night mean reversion;
- European open gaps;
- session-range breakouts and fades.

None is tradeable. Earlier rounds had already ruled out FX carry, momentum, reversal, trend, the fix
windows and a 653-candidate scan. The USDJPY intraday-momentum lead (rounds 11 and 17) failed its
confirmation on unseen data in round 18.

**Round 12 dug for new edges in five mechanism-led families (1,842 variants):**
- short-side index reversal;
- US macro-release shocks;
- gold and silver auction windows;
- the published FX weekend-gap reversal;
- an anatomy study of the reversal edge.

**No new edge.** Three things were learned about the one we have:
- **It is long-only:** shorting strength doesn't pay.
- **US legs must be held through the next session:** exiting overnight gives most of it back. JP225 is earned overnight.
- **It is not the published "overnight drift"**, which has died since 2021 while the reversal kept working.

**Rounds 13–15 kept digging:**
- reversal on 21 FX crosses;
- VIX "buy fear" entries;
- momentum by volatility regime;
- CFTC futures positioning (a new information source);
- the index rebound traded through FX and gold.

**Still no new edge.** The regime study pinned down how the core edge pays:
- **US indices:** trades entered when the VIX curve is inverted earn about 12× the calm-regime value (+56 vs +5 bps per trade). It is a stress-regime liquidity premium: keep those trades, and control the crash tail with size.
- **No VIX is needed:** the same split shows with US500 alone (≥ 9% below its 60-day high: +71 vs +4 bps). Round 16 found that round 15's "skip JP225 stress entries" rule rested on look-ahead, and withdrew it.
- **Risk currencies and gold don't share the rebound.**

**Round 17 widened the core edge into an SQX-ready set:**
- **The same reversal edge on 12 standard SQX indicators:** Stochastic, Williams %R, Bollinger %B, Keltner, Connors RSI, lower lows, ATR pullback, cumulative RSI(2).
- **Its own family test passes:** SPA 0.031 on timing value, 0.001 raw; walk-forward t 2.7.
- **Every SPY and QQQ variant is positive after 2013.**
- **It adds US30 (90% positive) and US2000 (78%)**, both FTMO symbols.
- **189 robust variants** to build from, listed in the library.
- **It is the same edge** (correlation 0.93), so more blocks, not more independent bets.
- **Intraday momentum doesn't carry over** to FX or gold. Late-day index momentum is gone.

**Round 18 checked the lead and the build:**
- **USDJPY intraday momentum: not confirmed.** On unseen USDJPY 2003–09 the breakout earns −0.2 bps and the noise rule +1.0 (t 0.9); on six JPY crosses every rule loses after costs. The lead is closed.
- **The RB signals survive the SQX build** (M5, 15:55): US100 keeps 98% of its daily-close Sharpe (SPA 0.024), JP225 107%, US500 72%.
- **Keep fixed size for the reversal book.** Volatility-scaled size made the worst day worse (−13.9% vs −9.9%) without a better zero-edge-adjusted pass rate.

**Real, but not for prop accounts:** trend following. It is weak after data-snooping control, and CFD financing eats it.

About 750 single hypotheses and about 13,000 family variants were tested in total (DSR trial count 14,996). Everything not listed above
failed out of sample or after costs ([§5](#5-what-not-to-build)).

---

## 1. The strategy book

| Sleeve | What | Evidence | Build in SQX as |
|---|---|---|---|
| **Core: index reversal** ([card](../evidence/edges/REV_index_reversal_family.md)) | Buy US500/US100/JP225 (also US30/US2000) after short-term weakness, at 15:55. Signals: IBS < 0.10–0.25, RSI(2) < 5–20, 2–5 down closes, 5/10-day low. Exit at the first up close (max 5 sessions) or the next session's 15:55. **Long only; hold US legs through the next session; keep stress-regime entries; no regime filter** (JP225 may exit at the next Tokyo open) | Edge family (SPA 0.03, PBO 0.19, walk-forward t = 2.1). Survives the SQX build: 2014–26 CFD quotes, timing Sharpe 0.58 (raw 0.86) for US500 + US100 + JP225 | **10–20 variants per market** from the 141 in [sqx_implementation_grid.csv](sqx_implementation_grid.csv) plus the 189 Tier 1/2 round-17 variants (Stochastic, Williams %R, Bollinger, Keltner, Connors RSI…; US30 and US2000 included) (≈ 8 independent bets in the US set). M5 chart + D1 cash-session chart, market orders at 15:55 |
| **Satellite: US100 intraday momentum** ([card](../evidence/edges/IM-04_noise_area_momentum.md)) | At 09:30, Buy Stop at open + 0.5 × prior range, Sell Stop at open − 0.5 × prior range; flat at 15:59 | Candidate: US100 SPA 0.036 in its family; native grid median Sharpe 0.47 (best variant 0.91, post hoc); 2026 holdout consistent | Native blocks, M1/M5, Exit At End Of Day. Its **own account**. Paper-trade first |
| **Satellite: USDJPY Tokyo fix on Gotobi days** ([card](../evidence/edges/GT_tokyo_fix_gotobi.md)) | Sell USDJPY (and EURJPY at ≤ 1 bp) at 09:55:00 JST on Gotobi days (5th/10th/15th/20th/25th/30th, previous Tokyo business day, plus month-end); buy back at 10:55 JST; buy stop at entry + 20 bps | EDGE (round 19): net +1.10 bps/trade, t 2.59, Holm 0.010; grid EDGE FAMILY; all JPY pairs, no non-JPY pairs; second feed agrees. **Confirmed on unseen 2002–07 crosses (round 20): +2.80 bps, t 4.5** | M1, time entry and exit, custom Gotobi/holiday block. **Own account, raw spreads (≤ 1 bp round trip)**, 10–20× notional |
| Optional: MR-06's intraday half | Buy the 09:30 open after three down closes, sell at 16:00 | Weak by rule; SPY 1993–2026 +10.5 bps/trade, t = 2.65 | Only for flat-by-close accounts |
| Small add-on: pre-holiday | Long the session before a US holiday | +12 bps, t = 3.25 (round 1); weak in the round-10 family test | ~9 trades/yr |
| Not for prop | Trend following, FX carry, currency momentum, FOMC-day short-dollar (decayed after publication) | Weak or none after 2012–17; financing costs | Long-term, low-cost portfolios only |

**Choosing variants within the reversal family** (median timing Sharpe; stable across the research data and all three SQX builds):

| Choice | Best | Worst |
|---|---|---|
| Signal | IBS < 0.10 (0.42–0.52 across builds) | 4 down closes; a large down day |
| Exit | first up close, or the next session | fixed 3 days |
| Filter | **none**, or only below SMA(200) | **above SMA(200)**, the popular choice, worst under every build |
| Market | US100 > US500; JP225 adds diversification (correlation ≈ 0.1) but needs the pre-close entry | DAX, FTSE, ASX, gold: no edge |

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

**Lessons:**
1. **Selection rules beat blind diversification.** Robustness plus de-duplication worked; equal-weighting everything failed.
2. **Families with no edge only dilute.** Build around the reversal family, with US100 momentum as a separate sleeve. The two are uncorrelated (0.06 as SQX-style books).

---

## 3. Prop accounts: where and how much

These are the SQX-style books of round 11 (A25): CFD minute data, exact intraday lows, published firm
terms, 2014–26, each against a zero-edge twin (in brackets).

| Book | Account | Fixed 1× | Survival sizing (CPPI k = 10) | Highest EV per account-month |
|---|---|---|---|---|
| **Reversal ensemble** (US500 + US100 + JP225, no weekend holds) | FTMO 2-Step Standard | 35% pass (7%), $254 per account-month | **49% (6%)** | 3×: $337 (18% pass) |
| Reversal ensemble, weekend holds | FTMO 2-Step Swing | 42% (10%), $342 | 53% (7%) | 3×: $375 |
| Reversal ensemble | FTMO 1-Step | 26% (7%), $158 | 50% (7%) | 3×: $229 |
| **US100 momentum, native** | FTMO 2-Step Standard | **57% (31%), $660** | 65% (21%) | **3×: $1,927** (33% pass) |
| US100 momentum, native | FTMO 1-Step | 56% (34%), $824 | **72% (29%)** | 3×: $1,678 |
| US100 momentum, native | Topstep 50K | 31% (20%), $126 | negative EV | 2×: $261 |
| Both books in one account | FTMO 2-Step Standard | 37% (7%), $382 | 55% (7%) | less than US100 alone at every size |

**How to read it:**

- **Run the two books in separate accounts.** Together they earn less than the US100 book alone, because the reversal book's crash days dominate.
- **The reversal ensemble must be sized for survival.** Its signals cluster in sell-offs: at 1× it lost 18% on 2020-03-12, and the next-worst days were 2015-08-25, 2024-08-05 and 2025-04-07.
  - Use CPPI or at most 1× with a cap on gross notional (≈ 2.5–3× equity at 1×), and the EA daily guard (2–3%).
  - The "highest EV per month" rows at 3× win only by failing fast.
- **The US100 book is the faster earner.** Its zero-edge twin also looks profitable in the simulator (the funded-account free option), so only the gap to the twin is yours.
- **Compared with round 9:** the post hoc ensemble passed 70% at 1× on Yahoo data. The SQX-style book on CFD quotes passes 35–42%: its Sharpe is lower (0.82 vs 0.9–1.0) and the tail is fatter.
- **Discount the figures.** They are in-sample for 2014–26. Plan on half the edge. Firm terms change: re-check them.

---

## 4. Paper trading: what it can show

| Edge | Forward time to t = 2 | Pre-set stop rule |
|---|---|---|
| Reversal ensemble (Sharpe ≈ 0.8) | ≈ 6 years | Stop if the 6-month forward Sharpe is below −2.4 (1% one-sided vs +0.9) |
| US100 momentum | ≈ 7.5 years | Forward mean below −10.6 bps/day after 126 days |
| MR-06 alone | ≈ 10 years | Below −7.9 bps per trade after 126 trades |

A 3–6-month forward test is an **implementation check** (fills, times, costs match the backtest), not
validation. The funding decision rests on the out-of-sample and multiple-testing evidence above, sized
so that being wrong is affordable.

---

## 5. What not to build

| Group | Tested and failed |
|---|---|
| Reversal outside its markets | DAX, FTSE and ASX 200 reversal (per-index SPA p 0.53–0.68; GER40 and gold negative under every SQX build); 15 other world indices; single large stocks |
| Intraday momentum outside US100 | Noise-area on US500 (native versions too), DAX, CAC, FTSE, Nikkei, ASX, Hang Seng, gold. Last-30-min, first-half-hour, GER40/CAC/FTSE close momentum, commodity and crude-oil momentum, Bitcoin momentum |
| Breakouts | 5- and 30-min ORB, Asian-range at the London open, Williams volatility breakout, NR7, gap fades; session-range breakouts and fades on FX and metals (round 11) |
| **FX and metals** | G10 carry (dead after 2012 net of swaps), currency momentum, FX and gold reversal, FX fix windows (daily and month-end), post-fix reversal. **Round 11:** session seasonality (dead after 2013), the night scalper (all 108 variants negative after costs), session-range breakouts and fades. **Round 18:** USDJPY intraday momentum not confirmed on 2003–09 or six JPY crosses |
| European indices | Close momentum, reversal, noise-area; **round 11:** open-gap fade or follow |
| **Round 12** | Short-side index reversal (raw P&L negative), macro-release shock follow or fade, LBMA and COMEX metals windows, the FX weekend-gap reversal (dead after publication), overnight-only index holds |
| **Rounds 13–14** | Daily reversal on FX crosses (AUDNZD, EURGBP and 19 others), VIX-regime index entries (redundant with REV), COT positioning extremes, trading the index rebound through risk FX or gold |
| **Round 17** | FX/gold session momentum (first half hour → last half hour), noise-area bands on FX majors and gold, late-day momentum on US500/US100 |
| Trend and cross-section | 48 trend variants (walk-forward t = 0.9, PBO 0.61), per-market trend on 22 markets, crypto trend, index momentum, volatility-managed exposure |
| **Rounds 35, 37** | US100 momentum rule on single stocks: 12 FTMO mega-caps as a basket (−0.07 bps/day); "stocks in play" earnings sessions on 71 unseen S&P 100 names (−1.7 bps, t −0.3), also via an SQX-native gap filter (−2.4). Net of measured CFD costs (median 7.4 bps per entry), intraday momentum is not a single-stock edge |
| **Rounds 42–43** | N3 momentum on crypto: New York anchor +3.5 bps/day (t 1.0); the 00:00 UTC lead on BTC/ETH (+15.6) fails on 13 unseen FTMO altcoins (−8.9 bps/day, 2 of 13 positive) |
| **Rounds 40–41** | Month-end rebalancing into the close (−2.8 bps/event); US100 − US500 spread momentum (−0.4 bps/day: N3 is not a relative-value flow); overseas sessions fading the prior US day (+1.6 bps/day net 2013–26, t 1.8; untestable before 2013 because cash-index opens are stale) |
| **Round 39** | Volume (a new source; SQX-native): high-volume days don't reverse and low-volume days don't continue in FX or gold (mechanism slope +0.003, t 0.15) |
| **Round 38** | US100 momentum rule on WTI, Brent, natural gas and silver: −5.6 bps/day net, gross only ≈ +1 bp. N3 is US100-only (21 markets and 83 stocks tested) |
| **Round 36** | The famous book setups as published: Williams' Oops!, Raschke–Connors Turtle Soup and 80-20s, DeMark's TD Sequential setup, Dalton's Market Profile "80% rule" (it completes 49% of the time, not 80%) — all five negative or flat after costs on US500/US100/GER40/UK100/JP225/gold |
| **Round 34** | US100 momentum (N3) cloned onto US30 and US2000: all 24 variants negative (US30 −0.99, US2000 −3.19 bps/day). N3 itself is confirmed on a second broker feed (Dukascopy, t 3.25) — it is a Nasdaq-100-only edge |
| **Round 32** | KLN annual seasonality (gross +27 bps/mo, t 1.3, buried by CFD financing), HKS half-hour periodicity (does not exist at index/FX level: rho 0.001) |
| **Round 30** | Quarter-end-week days beyond the Gotobi dates (the flow is on the dated days only) |
| **Round 29** | The ECB 14:15 fix (no reversal even when used transactionally, pre-2016) — the fix inventory is complete: only Tokyo pays |
| **Rounds 27–28** | Japanese-holiday morning short (misses the gate on 5 fresh crosses), day-after-holiday flows, Toshin month-start (strong on USDJPY, t 4.0, but fails its cross confirmation — closed) |
| **Round 26** | US→overseas session spillover (the 1990 continuation has inverted into REV-style fading, below costs), NFP/FOMC reaction momentum on US indices (reverts) |
| **Round 25** | COMEX gold/silver option-expiry windows (folklore backwards), Japanese fiscal year-end repatriation (March shorts lose) |
| **Round 24** | PBoC-fix reaction momentum in AUD/NZD/JPY (no continuation; the 2015 reform changed nothing), gold-silver ratio mean reversion (negative even gross), pre-Diwali gold (under-powered, bull-driven) |
| **Round 21** | Round-number barriers in FX and gold (Osler's reversal prediction has flipped; continuation too small to trade), Shanghai Gold Benchmark auction windows |
| **Round 22** | Gold and silver autumn effect (reversed after publication), the Asian bid in gold after NY sell-offs, gold's Asian-session drift (decayed after 2017) |
| Calendar and flows | Turn of month, overnight drift, FOMC day and cycle, announcement premium, FOMC- and BoJ-day currency premia (round 19), Halloween, options-expiration weeks, rebalancing flows, Treasury auction cycle, Bitcoin hours/Monday, crypto weekend, earnings-announcement premium in large stocks |
| Systematic scan | 653 time-of-day, day-of-week, streak, IBS and breakout candidates on 24 instruments: 0 confirmed |

Detail: [R5 negatives](../evidence/edges/R5_prop_instrument_negatives.md), [R7 negatives](../evidence/edges/R7_negatives.md),
[R10 negatives](../evidence/edges/R10_negatives.md), [R11 negatives](../evidence/edges/R11_negatives.md), [R12 negatives](../evidence/edges/R12_negatives.md), [R13–15 negatives](../evidence/edges/R13_15_negatives.md), REPORT §3–§22.

---

## 5b. Practitioner-canon validation (round 31)

The three confirmed edges were put through the standard practitioner gauntlet:
- **Pardo's walk-forward efficiency:** 84–88% for all three grids (his robustness bar: 50%).
- **Davey's monkey test** (2,000 skill-stripped twins): US100 momentum 100th percentile, Tokyo fix 98th; REV's day-selection 71–75th at daily granularity (underpowered there — its case is the family battery and breadth).
- **Kaufman's noise hypothesis is rejected** in this universe: noise ranks don't explain where index MR pays (ρ −0.09), and REV's value concentrates after *smooth* declines, not choppy ones — the stress-liquidity mechanism again.

## 6. How far to trust this

**Strong:**
- Pre-registration with git timestamps.
- Family-level multiple-testing control: SPA, Romano–Wolf, PBO and deflated Sharpe over the cumulative trial count (6,053).
- Walk-forward selection, and a discovery-only portfolio evaluated out of sample.
- The core edge re-measured the way SQX trades it, with controls that stay negative.
- A second data feed for US100, and the 2026 holdout.

**Check in SQX before trusting a backtest:**
- **The forming daily bar:** does SQX show today's unfinished session bar at 15:55 (build (c) assumes so)? If not, use the fallback in the build matrix.
- **The data's time zone** in the US/EU daylight-saving gap weeks.
- **The costs** at 15:55 NY.

**Weak points:**
- The prop figures are in-sample.
- The reversal edge clusters its exposure in sell-offs, and is regime-dependent (stronger since 2020).
- US100 momentum has a low deflated Sharpe (0.22) and no verified mechanism.
- There is no untouched data left: every series through September 2026 is in-sample.

---

## 7. Next steps, by value

1. **Build the reversal ensemble in SQX** as build (c) ([build matrix](../evidence/edges/SQX_build_matrix.md) §1):
   - run check 1 (the forming D1 bar) first;
   - replicate R1 on the broker's data;
   - select 10–20 variants per market from the 141;
   - run the falsification tests.
2. **Build US100 momentum natively** (build matrix §2) and run it in its own account.
3. **Put the chosen firm's exact terms into `tools/propsim`:**
   - size the reversal book for survival (CPPI or ≤ 1× with a notional cap);
   - size the US100 book for speed (1–3×);
   - keep the EA daily guard.
4. **Paper-trade both for 3–6 months** as an implementation check, with the stop rules above.
5. **FX: build GT on a raw-spread account** (build matrix §4): replicate it on the broker's tick data first, and check the fill at 09:55:00 JST. Metals: no build.
6. The USDJPY intraday-momentum lead failed on unseen data (round 18). The London-afternoon breakout on GBPUSD and gold stays untested on bid/ask data.

---

## Where things are

| Need | File |
|---|---|
| How to build each edge in SQX | [../evidence/edges/SQX_build_matrix.md](../evidence/edges/SQX_build_matrix.md) |
| Reversal variants under each SQX build | [sqx_implementation_grid.csv](sqx_implementation_grid.csv) |
| Every variant, with statistics and tier | [strategy_library.csv](strategy_library.csv) |
| Every result, per round | [validation/REPORT.md](validation/REPORT.md): §1 bottom line, §19 round 9, §20 round 10, §21 round 11, §22 rounds 12–43, §23 appraisal, §24 plan |
| Test definitions and amendments | [validation/PREREGISTRATION.md](validation/PREREGISTRATION.md) (A22 = round 9, A24–A25 = round 11, A26–A31 = rounds 12–17) |
| Edge cards, negatives, agent brief | [../evidence/](../evidence/README.md) |
| Statistics module (SPA, Romano–Wolf, PBO, walk-forward) | [validation/multitest.py](validation/multitest.py) |
| Prop simulator and firm presets | [../tools/propsim/](../tools/propsim/README.md) |
