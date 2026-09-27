# SQX build matrix — the surviving edges as StrategyQuant X strategies (round 11)

**What this is:** how to build each edge that survived eleven rounds of testing, in StrategyQuant X: chart
and session set-up, rules, trading options, costs, expected results, prop sizing, and the checks to run
first.

**Evidence:**
- [REPORT.md](../../research/validation/REPORT.md) §21: R1–R3 and the A25 prop lifecycle;
- per-variant results under each build: [sqx_implementation_grid.csv](../../research/sqx_implementation_grid.csv);
- code: [run_round11.py](../../research/validation/run_round11.py).

**SQX features used, and where they are documented:**
- **Trading options** ([SQX docs](https://strategyquant.com/doc/strategyquant/trading-options/)): Exit At End Of Day, Exit On Friday, Limit Time Range (Time Range From/To), Exit At End Of Range, Maximum Trades Per Day, Min/Max SL & PT, Reserved bars, Realistic gaps handling.
- **Sessions** are defined in Data Manager → Sessions ([SQX docs](https://strategyquant.com/doc/strategyquant/reliable-backtesting-of-futures-in-mt5-trading-sessions/)). An SQX administrator on what sessions do: "Using the sessions you can specify range to determine daily open, daily close, daily high/low. Indicator values will be affected as well" ([forum](https://strategyquant.com/forum/topic/data-manager-new-fields/)).
- **Multi-timeframe:** SQX advises the lowest timeframe on the main chart and higher timeframes on additional charts ([best practices](https://strategyquant.com/doc/strategyquant/best-practices-for-multi-tf-strategies-backtesting-and-trading/)).

## 0. Checks before building

1. **How SQX shows today's unfinished daily bar.** Build (c) assumes that, at the M5 bar closing 15:55, the D1 chart's current bar is today's session so far (close = the current price, high and low so far), and that the previous bars are completed sessions. That is how R1 computed it. The documentation read here does not say how a higher-timeframe bar in progress is exposed.
   - **Test:** backtest one known day and print the D1 close, high and low at 15:55 next to the M5 data.
   - **If SQX shows only completed D1 bars:** take today's high and low since 09:30 from the M5 chart, today's "close" from the M5 close, and earlier closes from the D1 chart. Or use build (a) for US-only books.
2. **Session definitions,** in the data's time zone:
   - US cash 09:30–16:00 NY;
   - Tokyo cash 09:00–15:00 JST, 15:30 from 2024-11-05.
3. **Data time zone and daylight saving.** Test the US/EU gap weeks in March and October/November. A 15:55 NY entry must stay at 15:55 NY.
4. **Costs at the trade time:**
   - spread, commission and slippage at 15:55 NY;
   - the research assumed 1.5 bps per round trip on US indices, 3.0 on JP225, 1.5 on US100 intraday entries.
5. **Replicate before selecting.** On the broker's data, the grid's median timing Sharpe per market should be within ±50% of the R1 figures below, or stop and reconcile.

## 1. REV — the index-reversal ensemble (core)

**Evidence:** family A (round 9): SPA 0.03, PBO 0.19, walk-forward t = 2.1. Round 11: survives SQX builds. [Card](REV_index_reversal_family.md).

```
Markets:      US500, US100, JP225 (US30, US2000 also qualified in family A; not re-tested in round 11)
Build (c) — reference
  Main chart: M5, same symbol. No session filter on the main chart
  Extra chart: D1 on the cash session (US 09:30–16:00 NY; Tokyo 09:00–15:00 JST, 15:30 from 2024-11-05)
  When:       only the decision at 15:55 NY (JP225 14:55 JST; 15:25 from 2024-11-05) may open or close trades
              -> Limit Time Range around that one M5 bar (check whether SQX stamps bars by open or close time)
                 and Maximum Trades Per Day = 1 per strategy
  Signals (one strategy each; D1 values, where bar 0 = today's session so far):
              IBS = (Close - Low) / (High - Low) < 0.10 | < 0.25
              RSI(2), Wilder smoothing, < 5 | < 10 | < 20
              k lower closes in a row, k = 2 | 3 | 5  (Close[0] < Close[1] < ... < Close[k])
              Close[0] <= lowest close of the last 5 | 10 sessions
              Round 17 (same edge, EDGE family on its own; 189 Tier 1/2 variants incl. US30/US2000):
              Stochastic %K(14) < 10 | 20;  Williams %R(5) < -95;  Bollinger %B(20,2) < 0;
              Close < EMA(20) - 2 x ATR(10);  Connors RSI < 10 | 15;  3 lower lows;
              Close < SMA(5) - ATR(10);  RSI(2)[0] + RSI(2)[1] < 35;  exit also: close > SMA(5), max 10
  Filter:     none, or Close < SMA(200) of D1. Never "Close > SMA(200)": worst in every build
  Entry:      market order at 15:55
  Exit:       market at 15:55 on the first session with Close[0] > Close[1], at most 5 sessions
              | or at the next session's 15:55
  Stops:      none were tested. If an account needs one, use a far catastrophic stop (e.g. 3 x ATR(14) of D1)
  Weekend:    FTMO Standard: no entry on the last session of the week; Exit On Friday at 15:55 (R2: same Sharpe)
Build (a) — US500 and US100 only (JP225 loses most of its edge on these bars)
  Chart:      D1 broker bars (days closing 17:00 NY, i.e. server time GMT+2/+3 with US daylight saving)
  Signals:    as above, on the completed D1 bar
  Orders:     market at the next bar's open; exit at the open after the exit condition
Costs:        1.5 bps per round trip (JP225 3.0)
Variants:     sqx_implementation_grid.csv rows with positive_timing_all_three = True and family_a_tier 1 or 2 (141).
              Take 10–20 per market, de-duplicated at correlation 0.6
Sizing:       equal risk per market, equal size per variant within a market; the whole book at most ~2.5–3x equity
              gross notional at the A25 "1x" level. Signals cluster in sell-offs
```

**Expected, 2014-01 → 2026-08 (HistData CFD quotes).** Figures are ensemble timing-value Sharpes, with the raw Sharpe where given:

| Build | US500 | US100 | JP225 | US500 + US100 + JP225 |
|---|---|---|---|---|
| (c) M5, 15:55 | 0.43 | 0.59 | 0.33 | **0.58** (raw 0.86) |
| (c) without weekend holds | 0.36 | 0.65 | 0.33 | **0.59** (raw 0.84) |
| (a) broker D1, next open | 0.45 | 0.48 | 0.21 | 0.42 (raw 0.64); **US500 + US100: 0.48** |
| (b) cash-session D1, next open: **don't use for JP225** | 0.27 | 0.53 | −0.04 | 0.31 |

Other expectations:
- **Trades per variant:** about 11 per year (8.8 without weekend holds); exposure about 7% of days.
- **Controls:** GER40 and gold show no edge under any build. If the broker data shows one, the build differs from the research.

**Prop, as the A25 book B8/B8w** (every variant equally weighted; exact intraday lows; FTMO presets):

| Account | Fixed 1× | CPPI k = 10 | Highest EV per month |
|---|---|---|---|
| FTMO 2-Step Swing (weekend holds) | 42% pass (zero edge 10%), $342 per month | 53% (7%) | 3×: 21% pass, $375 |
| **FTMO 2-Step Standard (no weekend)** | 35% (7%), $254 | **49% (6%)** | 3×: 18%, $337 |
| FTMO 1-Step | 26% (7%), $158 | 50% (7%) | 3×: 21%, $229 |

- **Tail risk:** worst day at 1× was −18% on 2020-03-12. Others: 2015-08-25, 2024-08-05, 2025-04-07.
- **Sizing:** size for survival, with CPPI or at most 1×, and keep the EA daily guard (2–3%).

**Falsification tests on the broker's data:**
1. At least 80% of the chosen variants are positive in 2014 →, and the ensemble's raw Sharpe is above 0.5.
2. The "above SMA(200)" filter is worse than no filter.
3. The GER40 control shows no edge.
4. Build (c) ≥ build (a) on the US indices, and JP225 is much weaker under (a).
5. The no-weekend version is within ±0.1 Sharpe of the full version.

## 2. US100 intraday momentum, native build (satellite, own account)

**Evidence:**
- N3: US100 SPA 0.036 in its family; DSR 0.22; 2026 +1.4 bps/day.
- Round 11: the native grid keeps 89% of N3's Sharpe (median 0.47 vs 0.52) and correlates 0.58 with it.
- [Card](IM-04_noise_area_momentum.md).

```
Market:       US100 (CFD or MNQ micro futures)
Chart:        M1 (or M5); session US cash 09:30–16:00 NY
Bands:        U = session open + k x (prior session High - Low);  D = session open - k x (prior range);  k = 0.5
              (grid: k 0.3/0.5/0.7 x prior range or ATR(14) of session bars; all 12 positive in 2014–19 and 2020–26)
Orders:       at 09:30, Buy Stop at U and Sell Stop at D. On a fill, cancel the other ("flat")
              | or keep it as a stop-and-reverse ("reverse")
Exit:         Exit At End Of Day at 15:59 NY
Trades:       Maximum Trades Per Day = 1 (flat variant)
News:         FTMO Standard: no new entry within ±2 min of 10:00 on ISM days (1st and 3rd trading day of the month)
              or of 14:00 / 14:30 on FOMC days (and 14:00 on minutes days)
Costs:        1.5 bps per entry
Sizing:       flat (volatility targeting hurt N3, round 7). The A25 "1x" book = 2.1x notional
```

**Expected, 2014-01 → 2026-08:**

| Variant | Sharpe | Net bps/day | 2014–19 | 2020–26 |
|---|---|---|---|---|
| **range, k 0.5, flat** | 0.91 | +4.2 | 0.73 | 1.05 |
| range, k 0.5, reverse | 0.94 | +4.4 | 0.79 | 1.07 |
| Grid median (12 variants) | 0.47 | — | — | — |
| N3 (custom indicator) | 0.52 | +2.3 | — | — |

The k = 0.5 choice is post hoc; plan on the grid median. The book is lumpy by year (at 1×: 2020 −25%, 2022 +59%).

**Prop, as the A25 book B9** (12 variants, news blackout):

| Account | Fixed 1× | Fixed 3× | CPPI k = 10 |
|---|---|---|---|
| **FTMO 2-Step Standard** | 57% pass (zero edge 31%), $660 per month | 33% (20%), **$1,927** | 65% (21%) |
| **FTMO 1-Step** | 56% (34%), $824 | 35% (23%), $1,678 | **72% (29%)** |
| Topstep 50K | 31% (20%), $126 | 2×: 21% (12%), $261 | negative EV |

**Keep it in its own account.** Holding it together with the reversal book earns less at every size (A25, B10).

**Round 18, the RB signals in this build:**
- US100 keeps 98% of the daily-close ensemble Sharpe, JP225 107%, US500 72%.
- **Sizing:** fixed notional per trade; volatility-scaled size worsened the worst day.

## 3. MR-06 (a member of REV)

Build (c) with the signal "3 lower closes in a row" and a next-session exit. Evidence and prop figures are
in the [MR-06 card](MR-06_three_down_days.md). As part of the ensemble it no longer needs a Swing account (R2).

## 4. Closed lead (round 18: not confirmed on unseen data): London-afternoon breakout, USDJPY

**Round 18:** on USDJPY 2003–09 (unseen) this rule earned −0.17 bps per trade (t −0.2), and on six JPY crosses it lost after costs. **Don't build it.** The record below is kept for reference.


**Rule:**
- The range is 07:00–13:00 London.
- From 13:00 to 16:00 London, Buy Stop at the range high and Sell Stop at the low (OCO).
- Stop-loss at the other edge; exit at 16:00 London.
- One trade a day.

**Evidence (family R, round 11):**
- Formally an EDGE family, but it is USDJPY alone: without USDJPY, SPA 0.59.
- Validation Sharpe 0.97 against discovery 0.22; walk-forward ≈ 0.

**Caveats:**
- **News:** 17.5% of entries fall within ±2 minutes of US data at 08:30 or 10:00 NY. With FTMO Standard's blackout, the 2014–26 Sharpe falls from 0.75 to 0.43.
- **Slippage:** validation Sharpe 1.09 at the base cost, 0.78 with +0.5 bps per trade, 0.47 with +1.0 bps.
- **Gross, the same breakout is positive in both periods** on GBPUSD (+2.3 / +1.6 bps per trade) and gold (+1.2 / +2.7). It needs a raw-spread account that allows news trading (FTMO Swing).

## 5. Don't build (round 11 adds these to the earlier lists)

| Rule | Why |
|---|---|
| FX and gold session windows: long or short Asia, Europe, overlap or US afternoon (Breedon–Ranaldo) | Worked to 2013, gone after; ≤ 1 bp gross per window |
| FX night scalper: fade BB(20) or RSI(3) extremes, 19:00–01:00 NY, 9 pairs | All 108 variants negative after costs; gross reversion is about a tenth of night spreads |
| European open gap, fade or follow (GER40, UK100, FRA40) | Following worked in 2013–19 and faded; fading loses |
| Session-range fades, and Asian-range breakouts | Negative after costs (family R without the lead) |
| The reversal family on GER40 or gold | No edge under any SQX build (controls) |
| Cash-session D1 bars with next-open orders for JP225 | Loses JP225's whole edge |
