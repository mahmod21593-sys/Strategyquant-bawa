# 02 — Edge Catalog

Nine edge families. Each entry follows the same structure:

1. **Thesis and mechanism.** What the edge is, its source, and who pays.
2. **Evidence.** For and against, with grade (see [01](01-evidence-standards.md)).
3. **Where to look.** Markets and timeframes.
4. **Expected signature.** What a real implementation should look like; large deviations are a red flag.
5. **SQX implementation.** Template skeleton, allowed and denied building blocks, builder settings.
6. **Falsification tests.** Family-specific tests on top of the standard funnel in [03](03-sqx-validation-pipeline.md).
7. **Hypotheses.** IDs match `research/hypothesis-register.csv`.
8. **Failure regimes.**

> **Parameter ranges below are search boxes, not recommendations.** They keep SQX inside the region
> the research describes. The final values come from the funnel and must sit on a plateau.

> **SQX naming:** building-block and option names differ slightly between SQX builds. Where a block
> doesn't exist in your install (for example IBS, days-to-month-end, or a session-anchored return), it
> is marked **[custom block]**. These can be authored as SQX custom blocks or indicators.

---

## F1 — Time-Series Momentum / Trend Following

**1. Thesis and mechanism.** Returns over the past 1–12 months predict returns in the same direction
over the next weeks to months. **Source:** behavioural. Information diffuses slowly and prices
initially under-react, then herding and trend-chasing extend the move (Hong & Stein, 1999). Hedgers
and central-bank smoothing add slow, price-insensitive flow. **Who pays:** late movers and
price-insensitive hedgers.

**2. Evidence — Grade A**

| For | Against / caveats |
|---|---|
| Moskowitz, Ooi & Pedersen (2012): TSMOM in 58 futures across all asset classes; strongest in extreme markets | Huang, Li, Wang & Zhou (2020): asset-by-asset predictability is weak; profits resemble a sample-mean strategy |
| Hurst, Ooi & Pedersen (2017): positive in every decade since 1880; performed well in most large 60/40 drawdowns | Kim, Tse & Wald (2016): much of the TSMOM alpha comes from **volatility scaling** |
| Lempérière et al. (2014): two centuries of trend following across asset classes | Olson (2004); Neely, Weller & Ulrich (2009): FX technical-rule profits have declined |
| Szakmary, Shen & Sharma (2010): MA and channel rules profitable in 28 commodity futures, 1959–2007, after costs | Bajgrowicz & Scaillet (2012): daily DJIA technical rules show no value after data-snooping control and costs |
| Levine & Pedersen (2016): MA crossovers and TSMOM are closely related filters. The **lookback horizon matters more than the indicator** | Multi-year flat periods are normal for trend followers |
| Liu & Tsyvinski (2021): time-series momentum in crypto at 1–4 week horizons | |

**What the caveats imply for implementation:** the edge per market is small and noisy, so it must be
**diversified across many markets**. **Volatility-scaled sizing** is part of the edge, not an extra.
Equity indices and FX majors are the weakest markets for standalone trend. Commodities, metals and
bonds carry more of the load.

**3. Where to look.** D1 (primary) and H4 (secondary). As many markets as possible across indices,
metals, energy, FX majors and crosses, bonds (futures), and crypto (separate sleeve).

**4. Expected signature.** Win rate 30–45%; average win / average loss 2–4; positive skew; holding
period weeks to months; 5–25 trades per year per market. **If an SQX "trend" strategy has a 65% win
rate, it is probably not a trend strategy.**

**5. SQX implementation**

| Element | Skeleton A: Channel breakout | Skeleton B: Momentum / MA |
|---|---|---|
| Entry | **Stop** order at `Highest(High, N)` / `Lowest(Low, N)`, N ∈ [20, 120] | **Market** at bar close when `ROC(N) > 0` or `EMA(fast) > EMA(slow)`, N ∈ [20, 250] |
| Optional filter (max 1) | `Close > SMA(L)`, L ∈ [100, 250]; or ADX > x; or efficiency ratio | Same |
| Initial stop | k × ATR(20), k ∈ [2, 5] | Same |
| Exit | ATR trailing stop (k ∈ [2, 5]) **or** opposite channel `Lowest(Low, N/2)` | Signal reversal + ATR trailing |
| Profit target | None, or ≥ 5 × ATR. Tight targets cut off the right tail that pays for the strategy | None |
| Sizing | Fixed-fractional risk with the ATR stop (implicit volatility scaling) | Same |

- **Allowed blocks:** SMA, EMA, KAMA/adaptive MA, Highest/Lowest, ROC/Momentum, ATR, ADX, Keltner, Bollinger bands (as a breakout level), linear-regression slope.
- **Denied blocks:** oscillator threshold triggers (RSI, Stochastic, CCI, Williams %R), candlestick patterns. They express a different hypothesis.
- **Builder:** symmetric long/short rules; both directions (also run long-only on indices as a comparison); entry conditions 1–2; shift 0–2; SL mandatory (ATR-based); PT optional. Build on the primary market, then require the basket test below.

**6. Falsification tests**

- **Basket test:** the same rule with the same parameters is profitable on ≥ 60% of a basket of ≥ 8 markets spanning ≥ 3 asset classes, without re-optimisation.
- **Lookback plateau:** performance is stable across N ± 30%, as Levine & Pedersen's result predicts.
- **Crisis check:** behaviour in the 2008, 2020 and 2022 trend regimes is positive or at least neutral at the portfolio level.

**7. Hypotheses**

| ID | Hypothesis | Priority |
|---|---|---|
| TF-01 | Donchian breakout (N 20–100) + ATR trailing, D1, multi-asset basket | 1 |
| TF-02 | Momentum sign / dual-MA, D1, multi-asset basket (expect high correlation with TF-01; keep the better one per market) | 1 |
| TF-03 | H4 trend entries filtered by D1 trend (multi-timeframe), metals, energy and indices | 2 |
| TF-04 | Crypto TSMOM, 1–4 week lookback, D1, BTC and ETH | 3 |
| TF-05 | FX trend taken only in the carry-positive direction (see F7) | 2 |

**8. Failure regimes.** Range-bound, low-volatility, mean-reverting markets; sharp V-shaped reversals; crowded trend unwinds.

---

## F2 — Short-Term Mean Reversion in Equity Indices

**1. Thesis and mechanism.** After short-term weakness in an index that is in a longer-term uptrend,
next-few-day returns are above average. **Sources:** (a) *structural*: index products (futures, ETFs)
and arbitrage between them and constituents have made index-level serial dependence **negative since
the 2000s**; (b) *risk premium*: short-term reversal returns are the payoff to supplying liquidity, and
that payoff rises when volatility is high. **Who pays:** forced sellers and impatient traders who
demand liquidity during selloffs.

**2. Evidence — Grade B (strong)**

| For | Against / caveats |
|---|---|
| Baltussen, van Bekkum & Da (2019): 20 major indexes in 15 countries; serial dependence switched from positive to **negative** since the 2000s, linked to the growth of index products | Mechanism tied to indexing structure. Monitor for reversal of the sign |
| Nagel (2012): reversal returns proxy liquidity-provision returns and are highly predictable by VIX; conditional Sharpe ratios spike in turmoil | Negatively skewed: large losses in trending crashes (Q4 2008, Feb–Mar 2020) |
| Pagonidis (2013, NAAIM): low IBS (close near the day's low) is followed by high next-day returns in US equity-index ETFs (IBS < 0.2: +0.35%; > 0.8: −0.13%) | Practitioner paper. **Little or no effect in local ETFs of Germany, France, the UK, Australia, Spain, Switzerland and Taiwan**; disappears on low-volume days; IBS-only trading hurt by commissions |
| Connors & Alvarez (2009): RSI(2)-style dip-buying above the 200-day MA | Practitioner; widely known and possibly crowded |
| Baltussen, Da, Lammers & Martens (2021): intraday momentum **reverts over the next days** (links to MR-04) | Long-only results are inflated by equity drift. Must beat an exposure-matched random-entry benchmark |

**3. Where to look.** US500, US100, US30, US2000, GER40, UK100, EU50, JP225, AUS200. D1 (primary);
H4 or H1 entries with D1 context (secondary). **Not expected** to work on commodities, where trend
dominates. Test FX separately and expect weak results.

**4. Expected signature.** Win rate 60–75%; average win / average loss 0.5–1.0; negative skew;
holding 1–7 days; 10–40 trades per year per index; time in market 10–30%.

**5. SQX implementation**

| Element | Skeleton |
|---|---|
| Direction | **Long only** (the short side is run separately as control MR-05) |
| Regime filter (1) | `Close > SMA(L)`, L ∈ [100, 250] |
| Trigger (1) | One of: `RSI(n) < x` (n 2–5, x 5–30); **IBS < 0.2–0.3** [custom block: (C−L)/(H−L)]; `Close < Lowest(Close, k)[1]` (k 3–10); N consecutive lower closes; `Close < BB lower(20, 1.5–2.5)` |
| Entry | Market at close / next open **or** limit at `Close − m × ATR` (m 0–1). Test both; limit entries often help MR |
| Exit | `Close > High[1]`, **or** `Close > SMA(3–10)`, **or** `RSI(n) > 50–80`; plus time exit after 3–10 bars |
| Stop | **Wide** catastrophic stop only (2.5–5 × ATR), or none. Kaminski & Lo (2014) show stops subtract value when returns mean-revert and add value only with momentum |
| No | Trailing stops, tight profit targets |

- **Allowed blocks:** RSI, Stochastic, Williams %R, CCI, Bollinger, Keltner, SMA/EMA, Highest/Lowest, ATR, IBS [custom], consecutive-bars counter.
- **Denied blocks:** channel-breakout stop entries.
- **Builder:** long only; exactly 1 filter + 1 trigger (at most 2 triggers); SL optional and wide; "exit after bars" enabled, 2–10.

**6. Falsification tests**

- **Index basket:** the same rule works on ≥ 4 of 6 indices.
- **Exposure-matched benchmark:** beats random long entries with the same holding period and time in market. This removes the equity drift.
- **Mechanism check (Nagel):** returns per trade are higher when volatility is high (ATR percentile or VIX tercile). If they are not, question the mechanism.
- **Regime split:** positive both before and after 2015, and in high-vol and low-vol halves.

**7. Hypotheses**

| ID | Hypothesis | Priority |
|---|---|---|
| MR-01 | RSI(2–5) or IBS dip-buy above SMA(200), D1, index basket | 1 |
| MR-02 | N-day-low close with a limit entry below the close, D1 | 1 |
| MR-03 | Volatility-conditioned MR: trade only when the ATR percentile (or VIX) is elevated (Nagel) | 2 |
| MR-04 | Fade intraday momentum the next day: after a strong last-hour move, take the reversal over 1–3 days (Baltussen et al., 2021) | 2 |
| MR-05 | Control: short-side MR below SMA(200). Expected weak; documents asymmetry | 3 |

**8. Failure regimes.** Persistent trending selloffs; a regime where index autocorrelation turns positive again; vol spikes with gap-downs through wide stops.

---

## F3 — Intraday Momentum and Opening-Range Breakout

**1. Thesis and mechanism.** The direction of the market's early-session move predicts its
end-of-session move. **Sources:** *structural*: options dealers and leveraged ETFs that are short
gamma must trade in the direction of the move late in the day (Baltussen et al., 2021);
infrequent rebalancers and late-informed traders trade near the close (Gao et al., 2018).
*Behavioural:* intraday time-series momentum is stronger when liquidity is low, volatility is high and
information arrives in discrete jumps (Li, Sakkas & Urquhart, 2022). **Who pays:** price-insensitive
hedgers.

**2. Evidence — Grade B (downgraded from A after verification; see [evidence/edges/IM-01](../evidence/edges/IM-01_market_intraday_momentum.md) and [IM-02](../evidence/edges/IM-02_opening_range_breakout.md))**

| For | Against / caveats |
|---|---|
| Gao, Han, Li & Zhou (2018): SPY 1993–2013; first half-hour return (from prior close) predicts last half-hour; stronger on volatile, high-volume, recession and macro-news days; also in 10 other ETFs | Signal is small per day. Costs and execution quality at the open and close matter a lot |
| Baltussen, Da, Lammers & Martens (2021): 60+ futures on equities, bonds, commodities and currencies, 1974–2020; last-30-minute return predicted by rest-of-day return; linked to gamma hedging; **reverts over next days** | Gamma positioning isn't observable in SQX. Realised volatility is used as a proxy |
| Li, Sakkas & Urquhart (2022): intraday TSMOM significant in- and out-of-sample in most of 16 developed markets | |
| Schulmeister (2009): technical-model profits on S&P 500 moved from daily to 30-minute data | |
| Holmberg, Lönnbark & Lundström (2013): ORB profitable on US crude oil futures, 1983–2011 | Single market |
| Zarattini & Aziz (2023, SSRN): 5-min ORB on QQQ, 2016–2023. Zarattini, Aziz & Barbon (2024, SSRN): SPY "noise-area" intraday momentum, 2007–2024, reported Sharpe 1.33 net | Working papers, not peer-reviewed; reported numbers are in-sample for the authors. Haircut heavily |
| Crabel (1990): ORB and narrow-range day patterns | Practitioner |
| Tsai et al. (2019, *IEEE Access*): opening-range breakout profitable on DJIA, S&P 500, NASDAQ, HSI and TAIEX futures, 2003–2013, after 0.01% costs | Range length chosen in-sample per market |
| — | **Rosa (2022, *J. Futures Markets*): the overnight → last-half-hour predictability "disappears in the out-of-sample period"; works only when the signal is strong, so use a threshold** |

**3. Where to look.** US500, US100, US30, GER40 (cash session anchored); crude oil and gold;
optionally bond and FX futures. **Timeframes:** M5–M30 bars; decisions anchored to the **exchange
cash session** (for example 09:30–16:00 New York for US indices, 09:00–17:30 Frankfurt for GER40).

> **CFD warning:** index CFDs trade nearly 24 hours. Define the cash-session open and close explicitly
> in SQX time settings, check DST on both sides (US and EU shift on different dates), and use M1 or
> tick precision. Spreads at the open are wider than the daily average, so model that.

**4. Expected signature.** Win rate 40–55%; average win / average loss 1.2–2; mild positive skew; at
most 1 trade per day; flat overnight (no swap, no gap risk); 100–250 trades per year per market.

**5. SQX implementation**

| Skeleton | Entry | Exit | Key settings |
|---|---|---|---|
| **A. Last half-hour (Gao / Baltussen)** | At T−30 min before the cash close, go in the direction of the return from prior close (or session open) to T−30 [custom block: session-anchored return] | Exit at the cash close | Limit time range; exit at end of range; max 1 trade/day; optional filter: today's range / ATR > x (high-vol days) |
| **B. Opening-range breakout** | Stop orders at OR high + buffer / OR low − buffer, where OR = first 5–60 minutes of the cash session [custom block or `Highest/Lowest` over session bars] | SL at the opposite side of the OR or k × ATR(D1); exit at end of day; optional trailing | Max 1–2 trades/day; filters: OR width / ATR(D1) (narrow is better, per Crabel), gap direction, prior-day trend |
| **C. Noise-area breakout (Zarattini et al.)** | Band = session open ± average absolute move from open to the same time of day over the past 14 sessions [custom indicator]; enter on a close outside the band, checked every 30 minutes | Trailing stop at the band or VWAP [custom]; exit at end of day | Needs a custom time-of-day indicator |

- **Builder:** few free parameters. Mine only the OR length, buffer, and one volatility filter. Most of the work is robustness testing, not search.
- **Allowed blocks:** time and session blocks, session Highest/Lowest, ATR, range ratio, gap size, D1 trend context via multi-timeframe.

**6. Falsification tests**

- **Phase 1 regression** reproduces the sign and significance in our data before any build.
- **Mechanism check:** stronger on high-volatility days (Gao et al.; Li et al.).
- **Cross-market:** works on ≥ 3 of US500, US100, US30, GER40, crude oil and gold with shared parameters.
- **Cost stress:** survives 2× spread at the open and 1 extra tick of slippage on stop entries.

**7. Hypotheses**

| ID | Hypothesis | Priority |
|---|---|---|
| IM-01 | Last-30-minute continuation on US500 and US100 | 1 |
| IM-02 | 15/30/60-minute ORB on US100, US500 and GER40 | 1 |
| IM-03 | ORB on crude oil and gold (Holmberg et al.) | 2 |
| IM-04 | Noise-area intraday momentum on US500 (needs a custom indicator) | 2 |
| IM-05 | Intraday momentum only on high-volatility days (ATR ratio filter) | 2 |

**8. Failure regimes.** Low-volatility grind-up markets; range days; periods when dealers are long
gamma, which dampens moves.

---

## F4 — Volatility-Compression Breakout

**1. Thesis and mechanism.** Volatility is persistent and mean-reverting, so periods of unusually
low range tend to be followed by range expansion. Stop orders placed around a compressed range capture
the expansion. Direction comes from short-horizon continuation after the break (F3 mechanism) and from
stop cascades. **Source:** statistical property of volatility plus behavioural/structural
continuation. **Who pays:** traders whose stops cluster around obvious ranges; late momentum entrants.

**2. Evidence — B for the volatility component, C for rule profitability**

| For | Against / caveats |
|---|---|
| Volatility clustering and mean reversion are among the most robust facts in finance (Engle & Patton, 2001) | Knowing vol will expand says nothing about **direction** |
| Strong intraday volatility periodicity, e.g., around session opens (Andersen & Bollerslev, 1997) | Profitability of NR4/NR7 or Williams-style rules is mostly practitioner evidence (Crabel, 1990) |
| Intraday continuation evidence (F3) supports follow-through after breaks | False breakouts are common in range regimes |

**3. Where to look.** FX majors and crosses (H1–H4), XAUUSD, crude oil, indices (H1–D1). Session
breakouts: Asian range → London open.

**4. Expected signature.** Win rate 35–50%; average win / average loss 1.5–3; moderate positive skew;
20–80 trades per year per market; short holding periods (breakouts that don't move quickly tend to fail).

**5. SQX implementation**

| Element | Skeleton |
|---|---|
| Compression filter (1) | `ATR(fast) / ATR(slow) < c` (c 0.5–0.9), **or** Bollinger bandwidth in its lowest q-percentile, **or** NR-n day (today's range is the smallest of n days) [custom block if not native] |
| Entry | Stop orders at `Highest(High, N) + b` / `Lowest(Low, N) − b`, **or** `Open ± k × ATR` (k 0.3–1.0, Williams-style) |
| Order expiry | Cancel pending orders after 1–3 bars |
| Exit | SL at the opposite side of the range or k × ATR; PT 1.5–3R optional; ATR trailing; **exit after N bars** if the breakout doesn't follow through |
| Session variant | Asian range (e.g., 00:00–07:00 GMT) → stop entries 07:00–10:00 GMT → exit at end of day |

- **Builder:** symmetric rules; both directions; 1 compression filter + 1 entry-level rule; SL mandatory.

**6. Falsification tests**

- **Ablation (critical):** the same breakout **without** the compression filter must be worse. If it isn't, the filter is decoration.
- **Phase 1 check:** forward range after compression is significantly greater than baseline in our data.
- **Cross-market:** ≥ 3 markets.

**7. Hypotheses**

| ID | Hypothesis | Priority |
|---|---|---|
| VB-01 | NR7 / ATR-ratio compression → stop-entry breakout, D1, FX + metals + indices | 2 |
| VB-02 | Asian-range breakout at the London open on EURUSD, GBPUSD, XAUUSD and GER40 | 2 |
| VB-03 | Williams-style `Open ± k × ATR` volatility breakout, D1/H4, indices and gold | 3 |

**8. Failure regimes.** Choppy ranges with repeated false breaks; news spikes with slippage.

---

## F5 — Calendar and Flow Effects (Equity Indices)

**1. Thesis and mechanism.** Scheduled, non-discretionary flows cluster on known dates: salary and
pension inflows around month turns, and calendar-based rebalancing by large institutions. **Source:**
structural. **Who pays:** price-insensitive institutions trading on a timetable.

**2. Evidence**

| Effect | Evidence | Grade |
|---|---|---|
| **Turn of month** (last day → first 3 days) | Ariel (1987); Lakonishok & Smidt (1988); McConnell & Xu (2008): 1926–2005, 0.15%/day at the turn of the month vs ≈ 0 other days; present in 31 of 35 countries. **But Han, Han & Tian (2025, *FRL*): the effect "disappears entirely after 2001"** | **D**: decay control (was A−) |
| **Month-end rebalancing pressure** | Harvey, Mazzoleni & Melone (NBER WP 33554, 2025): when stocks are overweight after outperforming bonds, rebalancing sales lower next-day equity returns by ~17 bps; the flows are predictable | **B** (working paper; strong mechanism) |
| **Pre-holiday** | Ariel (1990); Lakonishok & Smidt (1988) | **B−** (few events) |
| **Halloween / Sell in May** | Bouman & Jacobsen (2002): Nov–Apr returns exceed May–Oct in most of 37 markets | **B**, as a regime overlay only |
| Overnight drift (2–3am ET, US equity futures) | Boyarchenko, Larsen & Whelan (2023); **~0 since 2021** (NY Fed, 2026) | **D**: decay control |
| Pre-FOMC drift | Lucca & Moench (2015); **gone after 2015** (Kurov, Wolfe & Gilbert, 2021) | **D**: decay control |

**3. Where to look.** Index basket, D1 (with H1 execution timing if helpful).

**4. Expected signature.** Few trades (about 12 per year per market for turn-of-month); short holding;
long-biased; high win rate and modest payoff. **Low statistical power:** pool across indices.

**5. SQX implementation**

- **These are fixed rules. Do not genetically mine them.** Use a tiny optimisation grid (≤ 20 combinations: entry day T−2…T0 × exit day T+1…T+4) and require a plateau.
- **Custom blocks needed:** `TradingDaysToMonthEnd`, `TradingDayOfMonth` (holiday-calendar aware), `IsPreHoliday`, and `MonthToDateReturn` of the traded instrument and of a bond instrument (via multi-symbol).
- **CF-02 logic:** on the last 1–3 trading days, if month-to-date equity minus bond return is above +x%, stand aside or go short; if it is below −x%, go long.
- **Use as overlays:** CF-03 and CF-04 modify F2 sizing or entries rather than standing alone.

**6. Falsification tests.** Effect present in ≥ 4 of 6 indices; positive in ≥ 60% of years; checked
separately for post-2008 and post-2020.

**7. Hypotheses**

| ID | Hypothesis | Priority |
|---|---|---|
| CF-01 | Turn-of-month long (T−1 → T+3) on the index basket. Decayed after 2001; control only | Control |
| CF-02 | Month-end rebalancing contrarian (Harvey et al.) on US500 and GER40 | 2 |
| CF-03 | Turn-of-month as an entry/size overlay on MR-01. Only if CF-01 is alive in your own post-2001 data | 3 |
| CF-04 | Halloween regime overlay for long-only index sleeves (full size Nov–Apr, reduced May–Oct) | 3 |
| CF-05 | Decay controls: overnight 2–3am ET long and pre-FOMC long. Tracked, never traded | 3 |

**8. Failure regimes.** Changes in pension/rebalancing practice (e.g., threshold-based instead of
calendar rebalancing); crowding; month-end shocks.

---

## F6 — FX Session and Fix Flows

**1. Thesis and mechanism.** (a) **Time-of-day:** domestic participants buy foreign currency during
their own working hours, so currencies tend to *depreciate during domestic hours and appreciate during
foreign hours*. (b) **Month-end London 4pm fix:** international equity investors resize currency
hedges at the month-end fix, so a market's relative equity outperformance predicts **depreciation** of
its currency into the final fix of the month, with partial reversal afterwards. **Source:** structural
order flow. **Who pays:** hedgers and corporates who trade on schedules.

**2. Evidence — Grade B**

| For | Against / caveats |
|---|---|
| **Krohn, Mueller & Whelan (2024, *JF*): G10 1999–2018, USD appreciates into the Tokyo and London fixes and depreciates after them (≈ 2 bps/day swings, t up to 12), in each of the 20 years** | Authors: "not easy to exploit once transaction costs are accounted for"; EUR around the London fix still Sharpe 0.65 after conservative costs |
| Ranaldo (2009): systematic time-of-day pattern, highly significant and persistent across years and after calendar controls | Effect per trade is small. **Cost-sensitive**: needs raw-spread accounts |
| Breedon & Ranaldo (2013): pattern linked to order flow | |
| Melvin & Prins (2015): relative equity appreciation predicts that market's currency depreciating before the final London fix of the month, followed by some reversal | About 12 events per year. Pool across pairs. The fix calculation window was widened in 2015, so test pre- and post-2015 separately |
| Evans (2018): order flow and price dynamics around the WM/Reuters fix | |

**3. Where to look.** EURUSD, USDJPY, GBPUSD, AUDUSD, USDCHF; H1 (time-of-day) and M15/H1 (fix).

**4. Expected signature.** Time-of-day: many small trades with a low edge per trade. Fix: about 12
trades per year per pair, held a few hours.

**5. SQX implementation**

- **Derive session windows from the Phase 1 time-of-day profile in your broker's server time.** Don't copy clock times from papers.
- **FX-01:** time-gated entry and exit (limit time range + exit at end of range), direction set by which currency's domestic session is active. Optional filter: day-of-week.
- **FX-02:** multi-symbol. `MonthToDateReturn(US500) − MonthToDateReturn(foreign index)` [custom block] sets direction on the last trading day of the month; enter a few hours before 16:00 London and exit at the fix. **FX-03** takes the reversal after the fix.
- **Builder:** no genetic mining of FX-01 or FX-02 logic; a small grid over window start/end only.

**6. Falsification tests.** Present in ≥ 3 pairs; survives 1.5× raw spread plus commission; sign
stable across years; FX-02 checked pre- and post-2015.

**7. Hypotheses**

| ID | Hypothesis | Priority |
|---|---|---|
| FX-01 | Dollar reversals around the Tokyo and London fixes: USD up into each fix, down after (Krohn, Mueller & Whelan, 2024, *JF*; extends Ranaldo, 2009). See [evidence card](../evidence/edges/FX-01_fx_fix_reversals.md) | 2 |
| FX-02 | Month-end London fix hedging flow, with the equity month-to-date return as the signal | 2 |
| FX-03 | Post-fix reversal | 3 |
| FX-04 | Session volatility ramp as a filter for F4 breakouts | 3 |

**8. Failure regimes.** Changes to fix methodology; wider spreads; changes in central-bank or
corporate hedging practice.

---

## F7 — Carry-Aware FX

**1. Thesis and mechanism.** High-yield currencies earn a premium over low-yield ones on average.
**Source:** risk premium; carry pays for crash risk, which shows up when global FX volatility spikes.
**Who pays:** borrowers and hedgers in low-yield currencies; the premium compensates for crash
exposure.

**2. Evidence — Grade A for the premium; B for implementation in SQX**

| For | Against / caveats |
|---|---|
| Koijen, Moskowitz, Pedersen & Vrugt (2018): carry predicts returns across asset classes | **Crash risk:** Brunnermeier, Nagel & Pedersen (2008); the August 2024 yen carry unwind |
| Lustig, Roussanov & Verdelhan (2011): common risk factors in currency returns | Menkhoff, Sarno, Schmeling & Schrimpf (2012, JF): carry losses concentrate when global FX volatility rises |
| Menkhoff, Sarno, Schmeling & Schrimpf (2012, JFE): currency momentum; Burnside, Eichenbaum & Rebelo (2011): carry and momentum payoffs and their combination | Single-pair carry is undiversified |

**3. SQX reality check.** SQX has no interest-rate data, and a single swap value per symbol does not
capture how rate differentials changed over time (e.g., the 2022 hiking cycle).

- **Bracket swap costs:** run every FX swing strategy with swap = 0, swap = current, and swap = adverse.
- **Carry signal:** import a daily rate-differential series (e.g., 2-year yield or policy-rate differential) as a **custom instrument** in SQX Data Manager, and use it as an additional chart in a multi-symbol strategy. The sign of the differential acts as a direction filter.

**4. Expected signature.** Negative skew for carry alone. Combined with trend (CA-01), win rate and
skew look like F1 but with better carry.

**5. Hypotheses**

| ID | Hypothesis | Priority |
|---|---|---|
| CA-01 | F1 trend signals on FX taken only in the carry-positive direction, D1 | 2 |
| CA-02 | Carry-direction swing strategy that stands aside when FX volatility spikes (ATR percentile across a pair basket, or VIX) | 3 |

**6. Falsification.** Carry filter ablation: CA-01 must beat the same trend rule without the carry
filter, pooled across ≥ 6 pairs.

**7. Failure regimes.** Carry unwinds (2008, August 2024), sudden central-bank pivots.

---

## F8 — Intermarket and Regime-Conditioned Variants

These are **conditioning layers** on F1–F5 more than standalone strategies. They use SQX's
multi-symbol mode, where other charts feed signals but orders go to the main chart.

| ID | Idea | Evidence | Grade | Priority |
|---|---|---|---|---|
| IX-01 | Take MR entries only when VIX (or index realised vol) is elevated | Nagel (2012) | B | 2 (= MR-03) |
| IX-02 | Commodity-currency momentum (AUD, CAD, NZD) as a leading filter for gold, oil or commodity indices | Chen, Rogoff & Rossi (2010) found predictability at a quarterly horizon, **but** a replication (Bork, Rovira Kaltwasser & Sercu; *Critical Finance Review*) finds it isn't robust out of sample | **D** (contested) | Parked |
| IX-03 | Risk-on/off filter: trade AUDJPY/USDJPY trend only in the direction of the US500 trend | Practitioner | C | 3 |
| IX-04 | Stand aside from **carry** when cross-asset volatility spikes. Don't apply this to MR: Nagel (2012) implies MR pays *more* in high volatility, which is tested in MR-03 | Menkhoff et al. (2012) | B | 3 |

**Look-ahead warning:** daily closes are at different clock times (US500 closes after GER40). A rule
that uses another market's *same-day* close can leak future information. Use the prior closed bar, or
align on intraday bars with explicit timestamps.

---

## F9 — Session-Range Mean Reversion (Exploratory)

**1. Thesis.** In quiet, low-information sessions (for example the Asian session for EUR and GBP
pairs), price oscillates around fair value and liquidity providers earn the spread plus the reversion.
**Source:** liquidity provision.

**2. Evidence — Grade C.** Intraday volatility periodicity is well documented (Andersen & Bollerslev,
1997; Ranaldo, 2009), but peer-reviewed evidence that fading ranges is **profitable after costs** is
thin. Many retail "Asian scalpers" have failed on rollover-hour spread widening and on news tails
(e.g., the January 2015 SNB event on CHF crosses).

**3. SQX implementation.** Limit-order fades at Bollinger or Keltner extremes inside a fixed session
window; target the middle band; wide stop; exit at the end of the session. Avoid rollover hours; model
rollover spreads explicitly.

**4. Extra requirements (Grade C).** Pooled t ≥ 3 across ≥ 4 pairs; noise-calibration pass;
≤ 5% portfolio risk until 6 months of live results.

| ID | Hypothesis | Priority |
|---|---|---|
| SR-01 | Asian-session band fade on low-volatility crosses (e.g., EURGBP, AUDNZD) with limit entries | 3 |
| SR-02 | Intraday range fade on index CFDs in low-volatility regimes only (the complement to IM-05) | 3 |

---

## Family comparison at a glance

| Family | Direction | Win rate | Payoff | Skew | Trades/yr/mkt | Holding | Stop philosophy |
|---|---|---|---|---|---|---|---|
| F1 Trend | L/S | 30–45% | 2–4 | + | 5–25 | weeks–months | ATR trailing; no tight PT |
| F2 Index MR | Long | 60–75% | 0.5–1 | − | 10–40 | 1–7 days | Wide or none; time exit |
| F3 Intraday mom. | L/S | 40–55% | 1.2–2 | + | 100–250 | hours | OR / ATR stop; EOD exit |
| F4 Vol breakout | L/S | 35–50% | 1.5–3 | + | 20–80 | bars–days | Range stop; time exit |
| F5 Calendar | Long-biased | 55–65% | ~1 | − | 12–24 | 1–5 days | Wide |
| F6 FX flows | L/S | 50–55% | ~1 | ~0 | 12–250 | hours | Time-based |
| F7 Carry-aware | L/S | 35–50% | 1.5–3 | −/+ | 5–20 | weeks | ATR trailing |
| F9 Range MR | L/S | 60–75% | 0.4–0.8 | − | 50–200 | hours | Wide; session exit |

These signatures are what you should see if a strategy expresses its family's edge. **An SQX build
whose statistics don't match its family's signature is probably fitting noise.**
