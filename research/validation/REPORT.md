# Own-data validation report

**What this is:** every edge in the plan tested on real market data, with the tests fixed *before*
looking at results ([PREREGISTRATION.md](PREREGISTRATION.md)). There were forty-one rounds, each
pre-registered and committed before its data was tested:

| Round | Pre-registered | Data | Tests |
|---|---|---|---|
| 1 | Main table + A1, A2 (09:10–09:19 UTC, 2026-09-25) | Yahoo daily (13 indices, 25 ETFs); Yahoo 60-min (2023–26) | P1–P19, exploratory scan E01–E20 |
| 2 | A3, A4, A5 (13:33–13:46 UTC) | HistData.com 1-minute: US500, US100, GER40 2014–25; 9 USD pairs 2004–23 | Q1–Q7 (Q7 = the original minute-data tests P7–P14) |
| 3 | A6, A7 (14:00–14:03 UTC) | **Data not yet downloaded or inspected**: earlier years, other instruments, a later period | R1–R7 confirmation tests of the round-2 leads |
| 4 | A8 (17:07 UTC) | Yahoo daily (^GSPC, SPY, IEF, TLT, 10 equity indices), TreasuryDirect auctions, FRED 10-year yields 1962–2001, HistData FX | S1–S7: published edges tested **after their papers' samples**, plus the untested FX-02 and CF-02 |
| 5 | A9–A11 (21:18 UTC →) | HistData gold, silver, WTI, Brent, Nikkei, ASX 200, Hang Seng, FX crosses; Binance BTC/ETH; Yahoo world indices | **No Treasury strategies (user scope).** 8 literature tests (T), a 653-candidate scan over 24 instruments (X), MR-06 on 15 untested indices (W1), noise-area momentum (N) |
| 6 | A12–A13 (2026-09-26) | The surviving books, 2014–25 | Prop decision analysis: sizing policy, CPPI, funded-stage sizing (no edge tests) |
| 7 | A14–A18 (2026-09-26) | **HistData 2026-01 → 09-18 (first untouched data)**; Yahoo ETFs and indices; Binance funding; published FTMO/Topstep terms | 2026 holdout of every intraday rule; 14 more families (G1–G13, H1); prop lifecycle on real firm terms |
| 8 | A19–A21 (2026-09-26) | Yahoo 60-min, SEC EDGAR, Binance | Build and funding checks (second feed for N3, planning cases, stop rules) |
| 9 | A22 (2026-09-27) | Yahoo daily 1993 →, HistData, FRED | Families A–D as strategy grids (1,246 variants) under SPA, Romano–Wolf, PBO and walk-forward; discovery-only portfolio |
| 10 | A23 (2026-09-27) | As round 9; FX rebuilt from HistData | Families E–K (3,768 variants) |
| 11 | A24, A25 (2026-09-27) | HistData 1-minute: indices 2013 →, FX majors 2003 →, crosses 2008 →, gold and silver 2009 → | **The edges as SQX would trade them** (R1–R3); FX/metals/European-index families L, M, Q, R (292 variants); prop lifecycle of the SQX builds |
| 12 | A26 (2026-09-27) | HistData 1-minute (FX 2003 →, metals 2009 →, indices 2013 →); Yahoo daily 1993 → | Edge research: short-side reversal, reversal anatomy and the overnight drift, macro-release shocks, metals auctions, FX weekend gaps (1,842 variants) |
| 13–15 | A27–A29 (2026-09-27) | HistData 1-minute (21 FX crosses 2008 →); Yahoo daily + VIX/VIX3M; CFTC COT 1986 → | FX-cross reversal, VIX-regime entries, momentum by regime, COT positioning, the index rebound through FX/gold (5,114 variants and 4 regime tests); the reversal edge by regime |
| 16–17 | A30–A31 (2026-09-27) | As above; Yahoo DIA/IWM for US30/US2000 | VIX-free regime proxies and a look-ahead correction; reversal breadth with 12 SQX-native signals; FX/gold intraday momentum; late-day index momentum (628 variants) |
| 35 | A49 (2026-09-27) | **Dukascopy one-minute stock CFD candles 2017 →: 12 FTMO mega-caps**; measured bid/ask costs; SEC EDGAR earnings filings | N3 momentum on single stocks (144 variants); earnings-session split |
| 41 | A55 (2026-09-28) | Yahoo daily Nikkei, Hang Seng, ASX 200, DAX 2000–12 (unseen, but stale cash opens); HistData CFD minute 2013–26; measured costs | Overseas-session fade of the prior US session (3 tests) |
| 40 | A54 (2026-09-28) | HistData US500/US100 minute 2013 →; Dukascopy US30 minute 2012 → | Month-end closing-auction rebalancing fade; US100 − US500 spread momentum (48 variants) |
| 39 | A53, A53a (2026-09-27) | **Dukascopy hourly candles with volume** (first use of volume), 17:00 NY daily bars: 7 FX majors and gold 2004 → | Volume-conditioned reversal/continuation (Campbell–Grossman–Wang), 192 variants + mechanism slope |
| 38 | A52 (2026-09-27) | **Dukascopy minute WTI 2011 →, Brent 2010 →, natural gas 2012 →**; HistData silver 2010 →; measured costs | N3 native grid on energy and silver (48 variants) |
| 37 | A51, A51a (2026-09-27) | **Dukascopy minute candles for 71 S&P 100 stocks never used before**, 2017 →; 2,913 SEC earnings filings; measured costs | Stocks-in-play momentum on earnings sessions; volatility cross-section; SQX-native gap proxy (4 tests + 12 variants) |
| 36 | A50 (2026-09-27) | HistData minute: US500, US100, GER40, UK100, JP225 2013 →, gold 2012 → | Five published practitioner setups: Oops!, Turtle Soup, 80-20s, TD Sequential, Market Profile 80% rule (120 variants) |
| 34 | A48, A48a, A48b (2026-09-27) | **Dukascopy one-minute candles (new feed): US30 2012 →, US2000 2018 →, US100 2012 →**; HistData US100 for the gates | N3 breadth on US30/US2000 (24 variants): hourly route failed its gate; minute route run as registered — not confirmed; N3 confirmed on the second feed |
| 33 | A47 (2026-09-27) | HistData US500/US100 minute 2013–26; 0DTE regime split 2022-11-14 | Intraday reversal in the 0DTE era (12 variants); N3 risk check |
| 32 | A46 (2026-09-27) | Yahoo/HistData daily (21 instruments); minute bins on US500/US100/EURUSD/USDJPY | KLN annual seasonality (4 variants); HKS half-hour periodicity (8) |
| 31 | A45 (2026-09-27) | Yahoo daily closes (12 indices); the A/RB/GT grids and books | Kaufman's noise hypothesis (2 tests); Davey monkey tests and Pardo walk-forward efficiency on the three edges |
| 30 | A44 (2026-09-27) | USDJPY 2003–26, 5 crosses 2008–26 (quarter-end-week days, never isolated) | Quarter-end settlement days beyond the Gotobi dates (2 tests + placebo) |
| 29 | A43 (2026-09-27) | EURUSD 2003 →, EURJPY 2002 →, EURGBP 2008 →, Berlin clock | The ECB 14:15 fix (12 variants; 2016-07-01 reform as natural experiment); GT quarter-end measurement |
| 28 | A42 (2026-09-27) | **Month-start mornings on 5 JPY crosses 2008–26 (never isolated)** | Confirmation of the Toshin month-start candidate |
| 27 | A41 (2026-09-27) | **Holiday mornings on 5 JPY crosses 2008–26 (never measured)**; USDJPY 2003–26 month-start days | Confirmation of the holiday-morning short and the day-after effect; Toshin month-start flows |
| 26 | A40 (2026-09-27) | HistData minute data: JP225, HK50, AUS200, GER40, UK100, US500, US100 2013 → | US→overseas session spillover (20 variants); NFP/FOMC reaction momentum on US indices (8) |
| 25 | A39 (2026-09-27) | Gold/silver daily bars 2010 →; USDJPY daily bars 2008 →; US federal and Japanese holiday calendars | COMEX option-expiry windows (8 variants); Japanese fiscal year-end flows (2) |
| 24 | A38 (2026-09-27) | HistData AUDUSD/NZDUSD/USDJPY 2005 →, gold/silver daily bars 2010 →; China and India holiday calendars | PBoC-fix reaction momentum (12 variants, natural experiment 2015-08-11); gold-silver relative value (18); Dhanteras/Diwali gold (1) |
| 23 | A37 (2026-09-27) | JPY crosses 2002–07 (unseen for these tests); USDJPY 2014–26 | Confirmation of the Japanese-holiday Tokyo-morning effect; the day after a holiday |
| 22 | A36 (2026-09-27) | HistData gold 2009 →, silver 2010 →, USDJPY 2003 →, EURJPY 2008 →; FRED 3-month rate; Japanese holiday calendar | Gold/silver autumn effect (Baur); the Asian bid in gold after NY sell-offs (12 variants); the Tokyo fix on Japanese holidays (GT mechanism) |
| 21 | A35, A35a (2026-09-27) | HistData 1-minute: 7 FX majors 2003 →, gold 2009 →, silver 2010 →; spike-bar audit of all 39 files | Round-number barriers (Osler; Aggarwal & Lucey) in FX and gold (64 variants); the Shanghai Gold Benchmark as a natural experiment (8) |
| 20 | A34, A34a (2026-09-27) | **HistData EURJPY, GBPJPY, AUDJPY, CHFJPY 2002–07, CADJPY 2007, NZDJPY 2006–07 (downloaded after A34)** | Confirmation of the Gotobi effect on unseen data; the build's exit and stop |
| 19 | A33 (2026-09-27) | HistData 1-minute: USDJPY and majors 2003 →, JPY crosses 2008 →, gold 2009 →; Japanese holiday, FOMC and BoJ calendars; FRED 3-month rates | **The Tokyo fix on Gotobi days** (USDJPY, EURJPY; 42 variants); FOMC- and BoJ-day currency premia (11 variants) |
| 18 | A32 (2026-09-27) | **HistData USDJPY 2003–09 and six JPY crosses, never run with these rules**; Yahoo daily; HistData indices | Confirmation of the USDJPY intraday-momentum lead; volatility-scaled reversal book; RB signals in the SQX build |

The git commit timestamps are the evidence of ordering. Every deviation is logged as an amendment.

---

## 1. Bottom line (after forty-one rounds; no Treasury strategies)

*Curated version: [../FINDINGS.md](../FINDINGS.md).*

| Edge | Status | Best evidence | After costs | Prop use (published terms, §17.5) |
|---|---|---|---|---|
| **MR-06: next day after ≥ 3 down closes, US500 (and US100)** | **Confirmed** (rounds 1–3); realistic 15:55 entry checked; 2026: +44 bps over 23 trades | Daily 1990 → : +19.8 bps, t = 4.6; 2014–25 minute data: +20 to +24 bps, t ≈ 2.3–2.7 | +14 to +22 bps/trade; ~19 trades/yr | **FTMO 2-Step Swing, 3×: 47% pass (zero edge 13%), ≈ $210 per account-month.** Needs weekend holds (Standard: $73). **Not allowed at futures firms** (overnight) |
| MR-06's intraday half (G12, new) | **Weak** by rule (2026: 26 trades, −8 bps); 33 years of SPY support | SPY 1993–2026: +10.5 bps net, t = 2.65 (708 trades); HistData 2014–25 +11.9, t = 2.1 | +10 to +12 bps/trade | The only index edge here a flat-by-close futures account can hold; too slow for Topstep's subscription model |
| **Noise-area intraday momentum, US100 (IM-04 / N3)** | **Candidate:** confirmed in its family (Holm 0.028), DSR 0.22 over all trials; **2026 holdout +1.4 bps/day, consistent but uninformative** (15% power); **second feed agrees** (Yahoo QQQ, correlation 0.99; **Dukascopy minute 2012–26: native primary +3.73 bps/day, t 3.25, 12/12 variants positive, round 34**); **US100-only** (US30 and US2000 negative in all 24 variants, round 34) | +3.0 bps/day net, t = 2.54, Sharpe 0.73; unseen 2011–13 +2.9 | Survives 3 bps; the news blackout costs 11% | **FTMO 1-Step, 4×: 37% pass (zero edge 25%), ≈ $980 per account-month**; FTMO 2-Step ≈ $715–770; Topstep ≈ $124 |
| Time-series momentum, prop instruments (G6 = round-1 P6 re-tested) | **Weak** (Holm 0.053 across 13 tests; 0.044 across the original 11) | +91 bps/month, Sharpe 0.62, 2012–26; correlation with SPY 0.04 | **Killed by CFD financing:** ~3.5× gross notional × 2%/yr mark-up leaves +1.8%/yr | Not viable: $23 per account-month on FTMO Swing; futures firms ban overnight |
| MR-06 on JP225 and AUS200 (execution check) | Positive with a pre-close entry: JP225 +20.5 bps (t = 2.3), AUS200 +13.8 (t = 2.3) | Concentrated in volatile episodes (JP225 after 2024) | — | Adds speed, not pass probability |
| Pre-holiday | Validated (round 1), small | +12.0 bps, t = 3.2 | +8.3 bps | Add-on (~9 days/yr) |
| Treasury end-of-month (CF-07) | Confirmed out of sample (round 4) | IEF +19.8 bps/month after 2019 | — | **Excluded by the user (no Treasury strategies)**; evidence kept on file |
| **Index-reversal family (round 9)**: IBS, RSI(2), 2–5 down closes and N-day lows with next-close or first-up-close exits on US500, US100, US30, US2000 and JP225 | **Edge family**: SPA p = 0.03 on timing value over 864 variants, PBO 0.19, walk-forward Sharpe 0.47 (t = 2.1). Two variants survive Romano–Wolf (US100 IBS < 0.10 and RSI(2) < 20) | 79–94% of US variants positive in 2013–26; the all-variant ensemble has validation Sharpe 0.9–1.0 (t ≈ 4–4.7) | Robust to +3 bps/trade | **Ensemble prop book** (post hoc): 70% pass at 1× on FTMO 2-Step (zero edge 26%), ≈ $450–1,100 per account-month depending on size and account |
| **Round 11: the reversal family built as SQX trades it** (M5 chart, signal and entry at 15:55; broker D1 bars; cash-session D1 bars) | **Survives.** Build (c) keeps 82–87% of the research Sharpe, and its daily P&L correlates 0.87–0.89 with it. Broker D1 bars are fine for US indices, not JP225. Without weekend holds: same Sharpe | US500 + US100 + JP225, 2014–26 CFD quotes: timing Sharpe 0.58 (raw 0.86); US100 alone SPA 0.009–0.024 under every build. 141 Tier 1/2 variants are positive under all builds | 1.5 bps/trade (JP225 3.0) | FTMO 2-Step Standard, 1×: 35% pass (zero edge 7%), $254 per account-month; CPPI 49% (6%). Crash clustering: −18% at 1× on 2020-03-12 → size for survival (§21.4) |
| **Round 11: US100 momentum from native SQX blocks** (open ± 0.5 × prior range, stop orders, flat 15:59) | **Native build recommended:** the 12-variant grid keeps 89% of N3's Sharpe (median 0.47 vs 0.52; correlation 0.58); all 12 positive in both halves | Best: prior-range k = 0.5, Sharpe 0.91 (post hoc) | 1.5 bps/entry | FTMO 2-Step Standard, 1×: 57% pass (zero edge 31%), $660 per account-month; 3×: $1,927. FTMO 1-Step CPPI: 72% (29%) |
| **Round 17: the reversal edge on 12 SQX-native indicators and US30/US2000** | **EDGE FAMILY again** (SPA 0.031 timing, 0.001 raw; walk-forward t 2.7; 3/17 Romano–Wolf survivors). 100% of SPY/QQQ variants positive after 2013; US30 90%, US2000 78%. Same edge as family A (correlation 0.93) | 189 Tier 1/2 variants: Stochastic, Williams %R, Bollinger, Keltner, Connors RSI, lower lows, cumulative RSI(2) | As family A | As §21.4 (one book) |
| **Round 19: the Tokyo fix on Gotobi days, USDJPY (new, FX)** — short USDJPY 09:55 → 10:55 JST on the 5th/10th/15th/20th/25th/30th and month-end | **EDGE, confirmed on unseen data (round 20: 2002–07 JPY crosses, +2.80 bps, t 4.5)** (pre-registered, after the paper's sample): net +1.10 bps per trade, t 2.59, Holm p 0.010; both halves positive. Grid EDGE FAMILY (SPA 0.027, PBO 0.05, walk-forward t 2.85). Every JPY pair has it; non-JPY pairs don't; a second feed agrees | 2014–26: gross +2.10 bps (t 5.0), 963 trades; 2003–13 +3.00 (t 4.9); 22/24 years positive | **Needs ≤ 1 bp round trip** and entry at the fix minute (09:56 loses 40%) | Own account, 10–20× notional: FTMO 2-Step 50–67% pass (zero edge 24–26%), $300–780 per account-month (post hoc) |
| Round 26: US→overseas spillover and macro-print momentum on FTMO index CFDs | **No edge.** The 1990 spillover has **inverted**: overseas sessions fade the prior US move (−10.4 bps/day on the published trade, t −7). The inversion is the reversal edge (REV) from another angle, already in the book, and below costs as a daily session trade. Post-print reaction momentum reverts (NFP −8 bps gross/event) | §22.12 | — | No; REV already harvests the inversion |
| Round 25: COMEX option expiry and the Japanese fiscal year-end | **No edge, and the folklore is backwards:** gold drifts *up* into the monthly option expiry (+10 bps) and down after; late-March USDJPY shorts (repatriation) lose −36 bps per event | §22.11 | — | No |
| Round 29: the ECB 14:15 fix | **No edge, ever:** no reversal even pre-reform (+0.30 bps, t 0.9); the 2016 reform is invisible in returns. Every benchmark fix is now tested; only Tokyo pays. **GT measurement:** quarter-end Gotobi month-ends earn +6.9 bps (t 7.3) vs +2.7 on other month-ends | §22.15 | — | Documents where GT's value sits |
| Rounds 27–28: Japanese-calendar extensions (holiday morning, day-after, Toshin month-start) | **None confirmed.** The holiday short misses Holm narrowly on 5 unexamined crosses (sign right in all); the Toshin month-start flow is strong on USDJPY (+2.46 bps, t 4.0) but its cross basket carries only half the effect (t 1.3) — closed as a single-series finding | §22.13–22.14 | — | GT stays Gotobi-days-only |
| Round 24: PBoC-fix momentum, gold-silver relative value, festival gold | **No edge.** The 09:15 CNY-fix reaction doesn't continue in AUD (gross ≈ 0) and the 2015 reform changed nothing; the gold-silver ratio isn't mean-reverting even gross at 30–120-day lookbacks; pre-Diwali gold is +1.2% gross (t 1.1, n 15) — under-powered and bull-market-driven | §22.10 | — | No |
| Round 22: gold/silver seasonality and the Asian bid in gold | **No edge.** The autumn effect reversed after publication (Sep/Nov −1.6% net); no dip-buying in Asia. **The Tokyo-fix mechanism holds for the pre-fix leg:** on Japanese holidays the rise into 09:55 disappears (−3.6 bps vs normal days, t −5.5) | §22.8 | — | GT unchanged; leads: gold in January, a JPY holiday short |
| Round 21: round-number barriers (FX, gold) and the Shanghai Gold Benchmark | **No edge.** Rates now reverse *less* at round numbers (FX −0.9 pp, gold −1.4 pp); continuation after crossing is slightly higher but far below costs. The SGE auction created no fix pattern in gold | §22.7 | — | No |
| Round 19: FOMC- and BoJ-day currency premia | **No edge:** DOL +4.7 bps per FOMC day (t 0.8) after publication, against +28 in 2005–13 | §22.5 | — | No |
| **Round 18: confirmation and build checks** | **USDJPY intraday momentum NOT CONFIRMED** on unseen 2003–09 data and six JPY crosses (lead closed). Vol-scaled sizing of the reversal book rejected (worst day −13.9% vs −9.9%). RB signals survive the SQX M5/15:55 build: US100 98% of the daily-close Sharpe, JP225 107%, US500 72% | §22.4 | — | Fixed size for the ensemble; no FX build |
| Rounds 13–16 (FX-cross reversal, VIX-regime entries, COT positioning, the index rebound via FX/gold; 5,114 variants) and the reversal by regime | **No new edge.** The US reversal is a stress-regime liquidity premium: +56 bps per trade when VIX ≥ VIX3M vs +5 calm; +71 vs +4 when US500 is ≥ 9% below its 60-day high (no VIX needed). Risk FX doesn't share the rebound. The JP225 stress result was a look-ahead artefact (round 16) | §22.1–22.2 | — | Size REV down; no regime filter |
| Round 12 families (short-side reversal, macro-release shocks, metals auction windows, FX weekend gaps; 1,410 variants) and the reversal-anatomy study (432) | **No new edge.** The reversal edge is long-only; it needs the next session (the overnight or European-open part alone is worthless for US indices; JP225's is earned overnight). The published overnight drift and FX weekend reversal did not survive publication | §22 | — | No |
| Round 11 FX / metals / European-index families (session seasonality, night mean reversion, European open gap, session-range breakout; 292 variants) | **No tradeable edge.** Family R is an EDGE by rule, but it is USDJPY alone (without it SPA 0.59), news-driven, and slippage-sensitive | §21.3 | — | Lead only: the London-afternoon breakout on USDJPY, GBPUSD and gold |
| Round 10's seven families (reversal outside equities, per-market trend, index-pair relative value, calendar, crypto trend, reversal on more indices, cross-sectional stock reversal; 3,768 variants) | None adds an independent edge. The only rule-based EDGE (J) is US tech again plus one isolated EU50 variant | §20 | — | No |
| Everything else | Failed on unseen data, decayed after publication, below costs, or a data artifact | See §3–§20 | — | No |

**The honest summary:**

- **What was tested.** About 747 pre-registered hypotheses on up to 64 years of data, 24 prop-tradeable instruments and 1-minute data, plus the first truly untouched period (HistData 2026).
- **What survived.** Outside Treasuries: **MR-06** (buy US index weakness at the close), whose edge is split about evenly between the overnight and the next session, and **noise-area momentum on US100**, still a candidate.
- **What the holdout said.** In 2026 the rules that were WEAK or PARTIAL in-sample averaged a holdout t of −0.15, the same as the null rules. The guards were right to reject them. N3 stayed positive, but nine months can't confirm it.
- **What round 7 added.** 16 more families were tested: Halloween, options expiration, VIX-conditioned reversal, volatility management, trend following, last-hour reversal, Asian-range, Williams and NR7 breakouts, crypto funding, gap fade, intraday MR-06, index momentum, and, on single-stock CFDs, the earnings-announcement premium and stock-level MR-06. None is a new tradeable edge. Trend following is a real diversifying premium, but CFD financing eats it. The earnings premium in large stocks decayed after 2013.
- **What it means for prop challenges** (published terms, in-sample books):
  - The best venue tested is **FTMO 1-Step with the US100 rule at 4×**, about $980 per account-month.
  - **MR-06 belongs on an FTMO 2-Step Swing account** (weekend holds allowed), about $210.
  - **Topstep-style futures accounts fit neither edge well**: they must be flat overnight, and the monthly fee and payout caps drag.
  - Cushion (CPPI) sizing still gives 71–82% pass rates against 13–22% for zero edge, but takes years.
- **Round 11, built as SQX trades it:**
  - The reversal ensemble survives an M5/15:55 build on CFD quotes (82–87% of the research Sharpe) and doesn't need weekend holds.
  - The US100 rule can be built from native blocks.
  - FX and metals still have no tradeable edge after costs. Four more families were tested; the only lead is the US-data breakout in the London afternoon.
  - In prop accounts, the SQX-style reversal book passes less often than round 9's estimate (35–42% at 1×), because its signals cluster in crashes. The native US100 book is the faster earner.
- **Round 19, the first FX edge:**
  - **The Tokyo fix on Gotobi days** (Ito & Yamada 2017) survives a pre-registered test after the paper's sample. Short USDJPY from 09:55 to 10:55 JST on settlement days: +2.1 bps gross, +1.1 net per trade (t 2.6).
  - It shows in every JPY pair, not in other pairs, and in a second data feed.
  - It is small: it needs a raw-spread account (≤ 1 bp round trip) and an order at the fix minute.
  - The FOMC-day short-dollar premium decayed after publication.
- **Round 20, confirmation:**
  - The Gotobi effect holds on unseen 2002–07 data for four JPY crosses: +2.80 bps gross (t 4.5), above ordinary days by +1.9 (t 2.8).
  - The first run failed on a corrupt HistData file (AUDJPY 2005). It was dropped by a data-integrity amendment committed before the re-run.
  - The build keeps the 10:55 exit and adds a 20-bps stop, which caps the worst trade at −21 bps.
  - EURJPY may join USDJPY.
- **Round 18:**
  - The USDJPY intraday-momentum lead failed on unseen data (USDJPY 2003–09, six JPY crosses). FX intraday momentum is closed.
  - Vol-scaled sizing of the reversal book was rejected: fixed size has the smaller worst day.
  - The RB signals survive the SQX M5/15:55 build (US100 98%, JP225 107%, US500 72%).
- **Round 17:**
  - The reversal edge holds on 12 standard SQX indicators and on US30 and US2000: 189 robust variants to build from.
  - Intraday momentum doesn't carry over to FX or gold, except a small USDJPY pocket (a lead).
  - Late-day momentum on US indices is gone.
- **Rounds 13–15:**
  - FX crosses don't reverse at the daily horizon, and COT positioning carries no signal.
  - VIX-based entries are the reversal edge again.
  - The reversal edge itself is a US stress-regime liquidity premium: size it down rather than filter it.
  - Round 16 withdrew a JP225 filter that rested on look-ahead. No VIX data is needed for the build.
- **Round 12, edge research:**
  - Five more mechanism-led families found nothing new.
  - The reversal edge is long-only, and US legs must be held through the next session.
  - The overnight drift and the FX weekend-gap reversal died after publication.
- **Round 8, sizing the expectations:**
  - The zero-edge twin is positive-EV in these presets (+$300–530 per attempt): that is the funded-account "free option", which firms police in ways not modelled.
  - At half the in-sample edge, N3 on FTMO 1-Step is ≈ $540 per account-month and MR-06 on Swing ≈ $85.
  - The two books are uncorrelated (0.03).
  - A forward test needs 7.5–10 years to confirm either edge statistically, so paper trading is an implementation check (stop rules in §18).

---

## 2. How the tests were run

- Pre-registered: rule, prediction, sample splits, costs, statistics and verdict rules, before the data was examined. Amendments were committed before the tests they affect.
- Per test: Newey-West HAC t (lag ≥ 5), one-sided p in the predicted direction, stationary-bootstrap 95% CI (2,000 resamples), year-by-year sign share, pre- vs post-publication split, net of pre-registered cost.
- **Multiple testing:** Holm and Benjamini-Hochberg within each round's family, and pooled for rounds 1 + 2 (29 tests). Deflated Sharpe ratio with the cumulative trial count (N = 35 in round 1, 50 in round 2, 57 in round 3, 64 in round 4).
- Verdict rules are applied mechanically by [verdicts.py](verdicts.py), [verdicts_round2.py](verdicts_round2.py) and [run_round3.py](run_round3.py). **Appraisal flags** record problems found after a test ran. They never change the rule-based verdict, only its interpretation.

---

## 3. Round 1 — primary tests (all results)

| ID | Test | n | Mean bps | Net bps | t (HAC) | p (1-sided) | Holm p | Post-publication mean (p) | Years with predicted sign | DSR | 95% CI | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | IBS < 0.2 above SMA200, S&P 500, 1990 → | 1,230 | 2.72 | 1.22 | 1.14 | 0.128 | 1.00 | 2014 → : 1.94 (0.31) | 67% | 0.14 | [−1.6, 6.9] | NOT VALIDATED |
| P2 | IBS, 9 non-US indices pooled | 5,424 | −1.71 | −3.21 | −1.24 | 0.89 | 1.00 | 0.02 (0.50) | 38% | 0.00 | [−4.6, 1.1] | NOT VALIDATED |
| P3 | 5-day low above SMA200, 3-day hold, S&P + NDX | 1,175 | −2.03 | −3.53 | −0.32 | 0.63 | 1.00 | 4.63 (0.31) | 55% | 0.01 | [−13.5, 10.4] | NOT VALIDATED |
| P4 | 1-day reversal, 13 indices pooled, 2000 → | 6,954 | 0.90 | 0.90 | 1.11 | 0.13 | 1.00 | 2017 → : 1.00 (0.23) | 56% | 0.14 | [−0.6, 2.6] | NOT VALIDATED |
| P5 | Turn of month (control), S&P 1970 → | 2,723 | 6.66 | — | 3.31 | 0.0005 | 0.007 | 2001 → : 2.21 (0.24) | 58% | 0.87 | [2.5, 10.8] | **DECAY CONFIRMED** |
| P6 | TSMOM, 25 ETFs, monthly 2007 → | 236 months | 79.8 | 79.8 | 2.64 | 0.004 | 0.0498 | 2013 → : 76.6 (0.014) | 80% | 0.66 | [27, 135] | **VALIDATED** (fragile) |
| P16 | Rebalancing flows (SPY vs TLT month-end) | 252 | −26.5 | −26.5 | −2.81 | 0.998 | 1.00 | −24.4 (0.99) | 19% | 0.00 | [−46.5, −10.8] | NOT VALIDATED (opposite sign) |
| P17 | Overnight premium SPY + QQQ, 1999 → | 6,928 | 3.97 | 1.97 | 4.66 | < 0.0001 | < 0.0001 | 2013 → : 4.06 (0.0003) | 82% | 0.98 | [2.3, 5.7] | **VALIDATED** (gross; see §6) |
| P18 | Pre-holiday, S&P 1970 → | 492 | 11.98 | 10.48 | 3.25 | 0.0006 | 0.008 | 2001 → : 8.30 (0.048) | 68% | 0.84 | [4.4, 19.7] | **VALIDATED** |
| P19 | IBS trades: high-VIX minus low-VIX tercile | 877 | 8.21 | — | 1.21 | 0.11 | 1.00 | — | — | — | — | NOT VALIDATED |
| P7y | Rest-of-day → last 30 min, SPY/QQQ/IWM/DIA, 2023–26 | 720 | −1.72 | −3.22 | −2.78 | 0.997 | 1.00 | whole sample post | 25% | 0.00 | [−2.9, −0.6] | NOT VALIDATED (**opposite sign**) |
| P8y | First hour → last 30 min, 2023–26 | 720 | −0.38 | −1.88 | −0.50 | 0.69 | 1.00 | — | 50% | 0.00 | [−1.9, 1.2] | NOT VALIDATED |
| P9y | P7y, strong signals only (Rosa threshold) | 332 | −3.49 | −4.99 | −2.94 | 0.998 | 1.00 | — | 0% | 0.00 | [−5.5, −1.6] | NOT VALIDATED (**opposite sign**) |
| P13y | Next-day reversal of last 30 min | 719 | 2.25 | 0.75 | 0.71 | 0.24 | 1.00 | — | 75% | 0.07 | [−4.2, 8.5] | NOT VALIDATED |
| P15y | FX: long USD 08:00→16:00 London, short USD 16:00 London→17:00 NY, 9 pairs, 2023–26 | 727 | −0.69 (net) | −0.69 | −0.52 | 0.70 | 1.00 | — | 25% | 0.00 | [−3.3, 2.0] | NOT VALIDATED |

**Secondary results that matter:**

- **P4 per index:** the 1-day reversal is significant on ^GSPC (+4.5 bps/day net, t = 3.2), ^NDX (t = 2.4) and ^DJI (t = 2.0), but negative on ^HSI (t = −2.2) and ^GSPTSE (t = −2.5). **US-specific.**
- **P2 per index:** IBS < 0.2 is significantly *negative* on FTSE (t = −3.3), TSX (t = −5.1), SMI (t = −3.1), DAX and CAC (t ≈ −2). This confirms Pagonidis: the IBS effect is a US phenomenon.
- **P1 randomization p = 0.0096:** IBS < 0.2 days beat random up-trend days, but not a zero-excess benchmark (HAC p = 0.13). The pre-registered primary is the HAC test, so the verdict stands.
- **P15 by window: WITHDRAWN (see §8.3).** Round 1 reported NY close → Tokyo +1.78 bps (t = 3.9) and London fix → NY close −2.03 (t = −3.1) as replicating Krohn, Mueller & Whelan. Split by pair, the effect comes almost entirely from USD-base pairs (NOK t = 10.9, SEK 6.5, CHF 4.4, CAD 4.2), while EUR, AUD, NZD and JPY are ≈ 0. That is the signature of a bid-quote artifact at the NY 17:00 rollover, the boundary of both windows.
- **P6 by period:** 2007–12 +87 bps/month (t = 1.5), 2013–19 +60 (t = 1.2), 2020 → +94 (t = 2.0).

## 4. Round 1 — exploratory scan (new edges), amendment A1

20 simple signals on the S&P 500 (and SPY for open-based signals). Discovery 1990–2012 with BH
q < 0.10; the confirmation period 2013 → was examined only after discovery results were saved.

| Candidate | Discovery 1990–2012 | Confirmation 2013 → (S&P 500) | Nasdaq 100 2013 → | Result |
|---|---|---|---|---|
| **E06** ≥ 3 down closes → next day | +18.7 bps, t = 3.48, q = 0.010 | **+21.9 bps, t = 3.01, p = 0.001** | +24.8, t = 2.48 | **CONFIRMED** |
| E07 ≥ 3 up closes → next day | −8.1, t = −2.52, q = 0.077 | −4.4, p = 0.086 | −3.7 | not confirmed |
| E10 first trading day of month | +20.3, t = 2.61, q = 0.077 | +6.9, p = 0.17 | +10.2 | not confirmed |
| E16 after a ≥ 2% down day | +28.8, t = 2.42, q = 0.077 | +30.9, p = 0.097 | +24.9 | not confirmed (borderline) |
| 16 others (weekdays, OPEX, Halloween, gaps, streaks…) | q ≥ 0.16 | — | — | not discovered |

A real screen should reject most discoveries, and 3 of 4 failed confirmation.

### E06 robustness (post-confirmation; reported, does not change the verdict)

| Check | Result |
|---|---|
| Mechanism (index products, post-1990) | S&P 500 **before 1990: −11.0 bps (t = −2.7)**, 1990–2012 +18.7 (t = 3.5), 2013 → +21.9 (t = 3.0), **2020 → +35.8 (t = 3.6)** |
| Dose-response (number of down days k), 1990 → | k = 2: +8.6 (t = 2.9) · **k = 3: +19.8 (t = 4.6)** · k = 4: +31.5 (t = 3.6) · k = 5: +56.0 (t = 3.7) |
| Holding period (excess, 1990 →) | 1 day +19.8 (t = 4.6) · 2 days +31.1 (t = 4.8) · 3 days +38.7 · 5 days +52.9 (t = 4.7) |
| Regime | Above SMA200 +12.1 (t = 3.1); below SMA200 +32.9 (t = 3.1) |
| Random-entry benchmark | p = 0.0002 (5,000 random draws of the same number of days) |
| Bootstrap 95% CI (1990 →) | [+12.5, +27.8] bps |
| Deflated Sharpe (N = 39 trials) | 0.95 |
| Years positive | 31 of 37 |
| Other markets | SPY +22.5 (t = 4.7), ^DJI +10.6 (t = 2.5), ^AXJO +10.9 (t = 2.5), ^N225 +11.1 (t = 2.1); ^RUT only after 2013 (+16.3, t = 2.0); DAX, FTSE (post-2013), TSX, SMI, HSI: no |

## 5. Round 1 — leads (status after rounds 2–3)

1. **Last-30-minute reversal in the 0DTE era.** Tested in round 2 (Q7-P7): **no flip.** 2014–21 +0.43 bps, 2022–25 −0.30; difference p = 0.50. The 2023–26 Yahoo reversal is real in the data (HistData agrees on the overlapping days: correlation 0.98), but it is a 2024–25 pattern (2022 was +2.3 bps), not a regime break.
2. **Month-start continuation after equity outperformance** (P16 opposite sign): not retested; still a lead.
3. **FX W1 + W4:** tested in round 2 (Q6). It passed the rules, but the result is a measurement artifact (§8.3). **Withdrawn.**

## 6. Round 1 — can the survivors be traded? ([implementability.py](implementability.py))

Costs: US500 CFD spread 0.75 bps round trip; overnight financing = 13-week T-bill rate (^IRX) × nights / 360; CFD swap = T-bill + 2.5%/yr.

| Edge (1994 →) | Trades/yr | Gross bps | Net, futures/cash | Net, CFD | Ann. return at 1× (CFD) | Sharpe 1× | Max DD 1× |
|---|---|---|---|---|---|---|---|
| E06 | 22.1 | 24.7 (t = 5.1) | 22.2 (t = 4.6) | **21.9 (t = 4.5)** | 4.8% | 0.66 | −18.9% |
| P18 pre-holiday | 9.1 | 10.5 (t = 2.2) | 8.3 (t = 1.7) | 8.3 (t = 1.7) | 0.8% | 0.27 | −8.5% |
| P17 overnight | 252 | 3.3 (t = 4.8) | **0.8 (t = 1.2)** | **0.5 (t = 0.8)** | 1.3% | 0.12 | −56% |

Round-1 prop simulation (Yahoo daily, 2013 → , E06 + P18, execution at the official close):
58–67% pass at 2–8× and 108–425 days to pass. **§11 replaces this with a more realistic estimate (37–44%).**

---

## 7. Round 2 — tests Q1–Q7 (amendments A3–A5)

### 7.1 Data check (A5): HistData time stamps

HistData documents its time stamps as "EST without daylight saving". **They are New York local time
with DST.** The US 08:30 data release, the 09:30 cash open, the 03:00 (09:00 Berlin) Xetra open and the
04:30 (09:30 London) UK release all sit at the same NY clock minute in winter and summer, for every
symbol and year checked (2004–2025). Taking the documentation at face value would have shifted every
summer window by an hour. Bars are labelled by their start minute.

### 7.2 Results

Holm within family Q (14 tests) and pooled across rounds 1 + 2 (29 tests). DSR with N = 50.

| ID | Test | n | Mean bps | Net bps | t | p | Holm Q | Holm pooled | Later period mean (p) | Years | DSR | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | Announcement days (FOMC + employment), S&P 1994 → | 629 | 13.97 | 12.47 | 2.64 | 0.004 | 0.042 | 0.091 | 2013 → : 5.22 (0.18) | 64% | 0.75 | PARTIAL |
| Q2 | **MR-06, buy next open, sell that close**, SPY 1993 → | 735 | 11.41 | 9.91 | 2.61 | 0.005 | 0.042 | 0.091 | 2013 → : 9.73 (0.062) | 65% | 0.45 | **VALIDATED** (Q) / PARTIAL (pooled) |
| Q2b | MR-06, next open → close a day later | 735 | 18.04 | 16.54 | 2.67 | 0.004 | 0.041 | 0.086 | 13.17 (0.11) | 74% | 0.60 | PARTIAL |
| Q3 | MR-06 with a 15:30 signal, US ETFs 2023–26 | 127 | 12.10 | 10.60 | 0.96 | 0.17 | 0.85 | 1.00 | — | 67% | 0.08 | NOT VALIDATED (n = 127) |
| Q5 | Crypto weekly TSMOM, BTC + ETH | 624 wk | 61.4 | 61.4 | 1.62 | 0.053 | 0.32 | 0.90 | 2021 → : 68.2 (0.058) | 69% | 0.26 | NOT VALIDATED |
| Q6 | FX W1 + W4, 9 USD pairs 2004 – 2023-09 | 4,887 | 3.53 | 1.53 | 9.33 | < 0.0001 | < 0.0001 | < 0.0001 | 2019 → : 2.22 (0.0001) | 95% | 1.00 | VALIDATED by rule — **INVALID: artifact (§8.3)** |
| Q7-P7 | Rest-of-day → last 30 min, US500 2014–25 | 2,768 | 0.20 | −1.30 | 0.43 | 0.34 | 1.00 | 1.00 | 2022 → : −0.30 (0.63) | 58% | 0.03 | NOT VALIDATED |
| Q7-P8 | First 30 min → last 30 min, US500 | 2,763 | −1.23 | −2.73 | −2.55 | 0.995 | 1.00 | 1.00 | −0.81 (0.80) | 25% | 0.00 | NOT VALIDATED (**opposite sign**) |
| Q7-P9 | P7 with Rosa threshold | 738 | −0.36 | −1.86 | −0.29 | 0.61 | 1.00 | 1.00 | −0.09 (0.52) | 42% | 0.01 | NOT VALIDATED |
| Q7-P10 | First-candle ORB (Zarattini & Aziz), US100 + US500 | 2,811 | 2.57 | 1.07 | 3.16 | 0.0008 | 0.010 | 0.019 | 2023 → : 0.82 (0.29) | 92% | 0.77 | PARTIAL |
| Q7-P11 | 30-min ORB stop entry, US100 + US500 | 2,808 | 2.47 | 0.97 | 2.39 | 0.009 | 0.062 | 0.15 | 2023 → : 3.81 (0.034) | 75% | 0.46 | PARTIAL |
| Q7-P12 | **GER40 17:00 → 17:30 momentum** | 2,962 | 2.07 | 0.57 | 4.85 | < 0.0001 | < 0.0001 | < 0.0001 | 2022 → : 1.32 (0.024) | 83% | 1.00 | **VALIDATED** — then failed confirmation (§9) |
| Q7-P13 | Next-day reversal of last 30 min, US500 | 2,735 | 1.35 | −0.15 | 0.65 | 0.26 | 1.00 | 1.00 | 5.32 (0.11) | 50% | 0.05 | NOT VALIDATED |
| Q7-P14 | US500 02:00 → 03:00 drift (**control**) | 3,065 | 0.66 | — | 2.42 | 0.008 | 0.062 | 0.15 | 2014–20: 1.45 (t = 3.75) → 2021 → : −0.43 (t = −1.2) | 58% | — | **DECAY CONFIRMED** |
| Q4 | MR-06 rule on bonds, gold, oil, FX ETFs, crypto (**mechanism check, two-sided**) | 2,619 | 0.45 | — | 0.15 | 0.88 (2-sided) | — | — | — | — | — | Prediction held (≈ 0 pooled); but TLT (t = 3.4), IEF (2.6), UUP (2.3) show reversal individually |

### 7.3 Round-2 secondaries and diagnostics

- **Q1 by event:** FOMC days +19.0 bps (t = 2.3) overall but **+0.9 bps after 2013** (t = 0.1); employment days +9.7 (t = 1.4), +8.3 after 2013. The pre-FOMC/FOMC-day premium looks arbitraged away, as the decay-control card expected.
- **Q2 vs E06:** buying at the next open keeps about half of the close-to-close effect (11.4 vs ~20 bps). Most of the E06 reversal happens overnight.
- **Q5:** buy-and-hold made 124 bps/week against 61 for weekly TSMOM. Crypto TSMOM mostly harvests the drift.
- **Q7-P10 sized as the paper sizes it** (risk = distance to the first-candle stop; post hoc): the median stop is 12 bps (US500) and 20 bps (US100), so a 1.5 bps cost is 0.08–0.12R per trade. Gross +0.14R (t = 2.8) and +0.16R (t = 3.4) become **−0.02R and +0.05R net (t = −0.4, 1.2)**; 2023 → : −0.05R and +0.01R. The paper's headline returns rely on zero costs.
- **Q7-P12 perturbations** (post hoc): signal to 16:58, entry 17:02, exit 17:29 or 17:35: t = 3.9–4.8. Long leg +2.4 (t = 4.4), short leg +1.7 (t = 2.4). Unconditional 17:00–17:30 drift +0.5 (t = 1.2). Top tercile of |signal| +4.5 (t = 5.2). Year by year: 2014 3.4, 2015 3.8, 2016 3.1, 2017 0.4, 2018 4.2, 2019 −0.4, 2020 4.1, 2021 0.8, 2022 2.4, 2023 −0.1, 2024 0.4, 2025 2.2.
- **Cross-source check for P7:** on the 494 overlapping days (2023-10 → 2025-12), SPY on Yahoo and SPXUSD on HistData give −2.02 and −1.94 bps/day (P&L correlation 0.98). The two sources agree.

---

## 8. Round 2 — appraisal of the FX result (Q6)

### 8.1 What the pre-registered test said

W1 + W4 on 9 pairs, 2004–2023: +3.53 bps/day gross, t = 9.3, 95% of years positive, post-2019 +2.2
(t = 3.8). Under the verdict rules this is VALIDATED, and it would have been the strongest result in the audit.

### 8.2 Why it can't be trusted

Per pair: USDNOK +11.0 bps/day, USDSEK +8.1, USDCHF +5.0, USDCAD +4.1 (all t > 9), but
**EURUSD −2.3, GBPUSD −2.7, AUDUSD −3.2, NZDUSD −6.7 after 2019** (t ≈ −3 to −8). A genuine dollar
move can't favour every USD-base pair and hurt every USD-quote pair. A **bid-only quote whose spread
widens at the NY 17:00 rollover** does exactly that: both windows start or end at 17:00, and a
depressed bid flatters USDxxx trades and penalizes xxxUSD trades.

Direct check (mean bid at t minus bid at 16:30, Mon–Thu, 2019–23): EURUSD −0.7 bps at 17:00;
USDCHF −2.5; USDNOK −5.3 at 17:00 and −9.2 at 17:10; USDSEK −4.0 and −8.7. The dip is the same sign
for USD-base and USD-quote pairs and lasts until about 18:30. That is spread, not price.

### 8.3 Clean re-measurement (post hoc; boundaries where spreads are normal)

USD-signed return, bps/day, basket of 9 pairs (t):

| Segment | 2004–2018 | 2019–2023 |
|---|---|---|
| London 16:00 → NY 16:45 (clean W4; predicted USD down) | **−1.62 (−4.2)** | −0.25 (−0.5) |
| NY 18:30 → 01:00 UTC (clean W1; predicted USD up) | **+1.19 (+6.6)** | **+1.37 (+4.7)** |
| Both, flat through the rollover | +2.80 (+6.5) | +1.79 (+3.1), **net of 2 bps: −0.2** |

The dollar-fix pattern of Krohn et al. was real in 2004–18 in clean data. After 2019 the
post-London-fix leg is gone, and the Tokyo leg is about 1 bp/day, below realistic retail costs. The
round-3 test (R6) found the Tokyo leg absent in 2024–25 as well.

**Lesson for the SQX build:** backtests on bid-only FX data are biased at the rollover. Use bid/ask
data (or mid plus modeled spread), and never place a window boundary at 17:00 NY.

---

## 9. Round 3 — confirmation on unseen data (amendments A6, A7)

Each round-2 lead tested on data not downloaded or inspected before A6/A7 were committed. Family R, Holm
within R. Verdict: REPLICATED = predicted sign, Holm p < 0.05 and net > 0; WEAK = raw p < 0.05 only.

| ID | Lead | Unseen data | n | Mean bps | Net bps | t | p | Holm R | Power* | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | P12 on other European closes (CAC 40, Euro Stoxx 50, FTSE 100) | 2014–25 (Euro Stoxx 2014–19 only†) | 3,006 | 1.01 | −0.49 | 2.99 | 0.001 | 0.010 | — | **WEAK** (below costs) |
| R2 | **P12 on earlier years** (GER40) | 2010-11 → 2013 | 783 | −0.24 | −1.74 | −0.24 | 0.59 | 0.70 | 0.80 | **NOT REPLICATED** |
| R3 | 30-min ORB on earlier years (US500 + US100) | 2010-11 → 2013 | 771 | 1.65 | 0.15 | 0.84 | 0.20 | 0.70 | 0.35 | NOT REPLICATED (underpowered) |
| R4 | First-candle ORB on earlier years | 2010-11 → 2013 | 765 | 1.69 | 0.19 | 1.21 | 0.11 | 0.56 | 0.50 | NOT REPLICATED (underpowered) |
| R5 | MR-06 open entry (Q2) on DIA + IWM | 2013 → 2026-09 | 476 | 4.48 | 2.98 | 0.94 | 0.17 | 0.70 | 0.64 | NOT REPLICATED |
| R6 | Clean USD-into-Tokyo, EUR/GBP/AUD/NZD | 2024–25 | 521 | 0.21 | −0.79 | 0.44 | 0.33 | 0.70 | — | NOT REPLICATED |
| R7 | **MR-06 with a 15:55 entry** (US500 + US100) | 2014–25 minute data (rule not computed on it before) | 308 | **15.88** | **14.38** | 1.89 | **0.030** | 0.18 | 0.93 | **WEAK** (magnitude replicates; Holm fails) |

\* Power: probability of p < 0.05 (one-sided) if the true effect equals the round-2 estimate.
† HistData stopped serving Euro Stoxx 50 after 2019. GER40 starts 2010-11; US500/US100 start 2010-11.

**Secondaries:**

- R1 per index: CAC +1.09 (t = 2.7), FTSE +1.02 (t = 3.0), Euro Stoxx +0.66 (t = 0.9). The top-tercile rule (post hoc) gives +2.1 to +2.9 bps. Close-momentum exists in European index quotes in 2014–25, at about half the DAX size and below cost.
- R2: the 2010–13 result is 2.7 standard errors below what the 2014–25 GER40 effect predicts. The top-tercile rule is also negative there (−0.8 bps). **The GER40 effect is not stable across periods.**
- R6 USD-base pairs: +1.43 bps (t = 3.6), driven by NOK (+3.8, t = 7.2) and SEK (+3.2, t = 5.7). The 18:30 boundary is still inside the wide-spread period for those two pairs. More artifact, not edge.
- R7 per index: US500 +20.2 bps (t = 2.3), US100 +11.8 (t = 1.1). Signal agreement: 98% (US500) and 93% (US100) of 15:55 signals are true three-down-close days. **On the same data and years, the 15:55 entry and the exact close give the same result** (US500 +23.5 vs +21.2 bps raw; US100 +16.8 vs +20.3). Execution timing isn't the problem; the 2014–25 sample is simply shorter and noisier than 1990–2026 (US500 t ≈ 2.6, US100 t ≈ 1.5–1.9).

---

## 10. What survived, in one table

| Lead | Round 1 | Round 2 | Round 3 | Final |
|---|---|---|---|---|
| MR-06 (≥ 3 down closes, US) | Confirmed OOS (t = 3.0) | Open entry: validated within Q (t = 2.6) | 15:55 entry: +15.9 bps, p = 0.03; open entry on DIA/IWM: n.s. | **Keep. Enter near the close, not the next open** |
| GER40 close momentum | — | Validated (t = 4.9) | Failed on 2010–13; below costs elsewhere | **Drop** |
| ORB (5-min, 30-min) | — | Partial (t = 2.4–3.2) | n.s. on 2010–13 (underpowered) | **Drop as standalone**; ≤ 1 bp net |
| FX fix windows | "Replicated" | Artifact | Clean Tokyo leg gone 2024–25 | **Drop** |
| Announcement premium | — | Partial; decayed after 2013 | — | **Drop** |
| Last-30-min reversal | Lead | No flip | — | **Drop** |
| Treasury end-of-month (round 4) | — | — | S2: +19.8 bps/month 2019 → (t = 2.95) | Confirmed, but **excluded by the user** (no Treasury strategies) |
| FOMC cycle, auction cycle, FX month-end fix, bond reversal (round 4) | — | — | Decayed or n.s. out of sample | **Drop** |
| Rebalancing, paper timing (round 4) | P16 wrong timing, opposite sign | — | S6: +7.2 bps (t = 2.1), n.s. after 2023 | Lead only |
| **Noise-area momentum, US100 (round 5)** | — | — | N3: +3.0 bps/day (t = 2.54, Holm p = 0.028); US500/GER40/gold fail | **Keep as candidate** (DSR over all trials 0.22) |
| Commodity/crypto/oil intraday rules; 653-candidate scan; MR-06 on world indices (round 5) | — | — | 0 confirmed | **Drop** |

---

## 11. Prop-challenge implications ([prop_mr06_minute.py](prop_mr06_minute.py))

MR-06 with the realistic 15:55 entry, HistData 2014–25, raw returns net of 1.5 bps and CFD swap,
intraday path from entry to exit, two-step 10%/5% (5% daily, 10% static), 3% EA daily guard,
stationary bootstrap:

| Book | Trades/yr | Net bps/trade (t) | 2× | 4× | 6× | 8× |
|---|---|---|---|---|---|---|
| US500 + US100 (capital split) | 26 | 16.8 (2.0) | 41% · 360 d | 41% · 169 d | 37% · 122 d | 37% · 99 d |
| US500 only | 19 | 19.7 (2.3) | 44% · 556 d | 37% · 271 d | 35% · 186 d | 33% · 149 d |

(pass probability · median days to pass; zero-edge base rate = 33%)

**Why the pass rate is low despite a real edge.** Per trade at 1×, MR-06 has σ = 153 bps against a
+20 bps mean, and an average adverse excursion of −89 bps: it buys into falling markets. US500 at 2×:

| Assumption | Pass | Main failure |
|---|---|---|
| No EA guard, real intraday path | **17%** | 82% breach the 5% daily loss |
| 3% EA guard, real intraday path | 44% | 56% hit the 10% max loss |
| 3% guard, exits only at the close (unrealistic) | 89% | — |

The daily-loss rule, not the edge, decides the outcome. That's why the round-1 estimate (58–67%,
daily bars, official-close execution) was optimistic. **Conclusions:** use an EA guard, keep leverage
at ≤ 2×, and don't rely on MR-06 alone. **Round 4 improves on this:** volatility-scaled sizing lifts
MR-06 to 60%, and adding the Treasury end-of-month edge lifts the book to 73–83% (§13).

---

## 12. Round 4 — published edges tested after their papers' samples (amendment A8)

Specs read from the primary papers (V1) before A8 was committed. Family S (7 tests), Holm within S,
DSR N = 64. The primary sample of each test lies **after** the paper's own sample.

| ID | Edge (source) | Primary sample | n | Mean bps | Net bps | t | p | Holm S | In the paper's own period | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | FOMC cycle: even-minus-odd weeks (Cieslak, Morse & Vissing-Jorgensen 2019) | 2017-01 → 2026-09 | 2,420 days | **−4.77**/day | — | −1.08 | 0.86 | 1.00 | 1994–2016: **+11.98, t = 3.89** (paper: 12 bps); 2004–16: +11.0 (t = 2.65) | NOT CONFIRMED (**decayed after publication**) |
| S2 | **Treasury end-of-month**: IEF, last 3 trading days, excess over T-bill (Hartley & Schwarz 2019) | 2019-01 → 2026-08 | 92 months | **+19.82** | **+17.82** | **2.95** | 0.0016 | **0.011** | 2002–18: **+20.97, t = 4.59** (paper: ≈ 25 bps on the 10-yr note) | **CONFIRMED** |
| S3 | Treasury auction cycle: IEF short 5 days before, long 5 days after 10-yr auctions (Lou, Yan & Zhang 2013) | 2013-09 → 2026-09 | 159 | +8.11 | +4.11 | 0.90 | 0.18 | 0.92 | 2002–08: +11.75 (t = 0.91) | NOT CONFIRMED |
| S4 | Month-end fix hedging: −sign(relative equity MTD) over 15:00–16:00 London (Melvin & Prins 2015) | 2013-01 → 2025-12 | 155 | +0.84 | −0.16 | 0.60 | 0.28 | 0.92 | 2004–12: +2.05 (t = 1.27) | NOT CONFIRMED |
| S5 | Post-fix reversal, 16:00 → next-day noon (Melvin & Prins 2015) | 2013-01 → 2025-12 | 143 | +1.65 | +0.65 | 0.76 | 0.22 | 0.92 | 2004–12: +5.83 (t = 1.90) | NOT CONFIRMED |
| S6 | Rebalancing, Calendar signal, last 5 days (Harvey, Mazzoleni & Melone 2025) | 2002-08 → 2026-09 | 1,445 days | +7.15 | +6.15 | 2.06 | 0.020 | 0.12 | to 2023-03: +7.88 (t = 2.00); after: +2.87 (t = 0.47, n = 210) | WEAK |
| S7 | Bond reversal after 3 down days (round-2 lead) | 1962–2001 (FRED 10-yr) | 1,065 | **−2.57** | −3.07 | −1.97 | 0.98 | 1.00 | (TLT 2002 → : +11.4, t = 3.4, the data that suggested it) | NOT CONFIRMED (**opposite sign**: the lead was period-specific) |

**Secondaries:**

- **S1:** even weeks averaged +2.5 bps/day and odd weeks +7.2 after 2017, against +9.8 and −2.2 in 1994–2016. The implementation reproduces the paper, so the effect itself has gone. A long-only even-week strategy earned 0.85 bps/day net after 2017, against 5.0 for buy-and-hold. Uppal's claim (V3) that it faded "as early as 2004" is **not** supported here (2004–16: t = 2.65). Its disappearance dates from publication.
- **S2:** rest-of-month IEF excess return after 2019 was −33 bps/month (t = −1.7). The whole term premium sits at month-end, as the paper says. TLT: +24.1 after 2019 (t = 1.77); +39.3 in 2002–18 (t = 4.61).
- **S3:** the 5-year-auction version gave +12.4 (t = 1.10). Excluding the 45 events whose windows touch a month-end: +12.3 (t = 1.29). Positive, but not significant in any version, including the paper's own period.
- **S4 per pair (2013 →):** AUD +4.7 (t = 2.1) and CHF +4.4 (t = 2.2) positive; NOK −4.4, CAD −1.7. No consistent pattern: this is the 2015 reform era (Ito & Yamada 2017, NBER w23327, find the fix anomalies changed shape after it).
- **S6, SPY only** (for accounts without bonds): +6.99 bps (t = 2.41) on 2002–2026, +2.97 after 2023 (t = 0.55). This corrects round 1's P16, which traded the first day of the next month, after the rebalancing is done. That explains its opposite sign.

## 13. Round 4 follow-up — robustness and prop books (post hoc, [round4_followup.py](round4_followup.py))

> The Treasury books below were superseded in round 5 by the user's scope (no Treasury strategies). See §15 for the current books.

Not pre-registered, except I1 (volatility-scaled MR-06), whose design was fixed in A8. These checks
were run after S2 was confirmed. They describe the edge; they don't add evidence to the verdict.

### 13.1 Treasury end-of-month: robustness

| Window (IEF) | 2002–2018 | 2019 → |
|---|---|---|
| Last day only | +11.4 (t = 4.2) | +7.5 (t = 2.0) |
| Last 2 days | +18.9 (t = 4.6) | +12.8 (t = 2.5) |
| **Last 3 days (tested)** | **+21.0 (t = 4.6)** | **+19.8 (t = 3.0)** |
| Last 4 days | +20.5 (t = 4.0) | +18.9 (t = 2.6) |
| Last 5 days | +23.0 (t = 4.0) | +24.0 (t = 2.8) |
| SHY (1–3 yr), last 3 | +5.6 (t = 5.1) | +5.5 (t = 3.7) |
| TLT (20+ yr), last 3 | +39.3 (t = 4.6) | +24.1 (t = 1.8) |

The effect doesn't depend on the exact window, scales with duration as an index-extension mechanism
predicts, and was positive in **24 of 25 calendar years** (2002–2026; only the partial 2026 is negative).

### 13.2 MR-06 with volatility-scaled size (I1, design fixed in A8)

Notional = min(2, 1% ÷ 20-day realized daily volatility), normalised to the same average notional as
fixed sizing. US500, 15:55 entry, 2014–25, two-step 10%/5% with a 3% guard:

| Sizing | Mean / sd per trade (bps) | 2× | 4× |
|---|---|---|---|
| Fixed | 19.7 / 152.8 | 44% · 556 days | 37% · 271 days |
| **Volatility-scaled** | 18.5 / 127.2 | **60% · 641 days** | **48% · 292 days** |

Scaling down after volatile weeks removes the trades most likely to breach the daily-loss limit, at
almost no cost in mean return.

### 13.3 Prop books, 2014–2025 (bootstrap; 1,500 runs each)

MR-06 = volatility-scaled US500 (§13.2). S2 = IEF excess return, standing in for a 10-yr Treasury
future (a 50K futures account trading 1–2 ZN contracts is roughly 2–4× notional). Weights are notional
multiples. Zero-edge base rates use the S2 book with its mean removed.

| Book | Two-step 10%/5% (3% guard) | Futures 50K: 6% target, 4% EOD trailing (2% guard) |
|---|---|---|
| **Zero edge (base rate)** | 27% (4×), 23% (8×) | 19% (4×), 16% (8×) |
| MR-06 2× | 60% · 641 days | 29% · 227 days |
| **S2 4×** | **86% · 494 days** | **50% · 134 days** |
| S2 8× | 68% · 208 days | 42% · 88 days |
| **MR-06 1× + S2 4×** | **83% · 373 days** | 48% · 95 days |
| MR-06 2× + S2 4× | 73% · 292 days | 37% · 86 days |
| MR-06 2× + S2 8× | 60% · 163 days | 36% · 58 days |

**Reading this:** S2 is the better prop component, with high consistency and 12 short trades a year.
Adding MR-06 roughly halves the time to pass for a small loss of pass probability. Trailing-drawdown
futures accounts are much harder (a 4% trailing limit against a 6% target), but S2 still gives 2.5×
the no-edge rate. All of these numbers are **in-sample for sizing**: the bootstrap re-uses the same
2014–25 history that was used to pick the weights.

## 14. Round 5 — prop-tradeable instruments only (amendments A9–A11)

The user asked for **no Treasury strategies**. Round 5 searched only instruments a CFD prop account
offers. It added HistData gold, silver, WTI (served only to 2023), Brent, Nikkei 225, ASX 200, Hang Seng,
EURJPY, GBPJPY and EURGBP, plus Binance BTC/ETH. Every new HistData symbol passed the time-zone check:
the Tokyo, Hong Kong and Sydney opens move one New York hour between seasons, and Brent settles at 14:28 NY.

### 14.1 Literature tests (family T), each on data after its paper's sample

| ID | Edge (source) | Primary sample | n | Mean bps | Net bps | t | p | Holm T | Paper's own period (my data) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 | Commodity intraday momentum: gold, silver, crude (Baltussen et al. 2021, *JFE*) | 2020-06 → 2025 | 1,388 | +0.42 | −3.38 | 0.86 | 0.19 | 1.00 | 2011 → 2020-05: **+2.34, t = 3.21** | NOT CONFIRMED (**decayed after publication**) |
| T2 | Crude oil: prior close → 10:00 predicts 15:30–16:00 (Wen et al. 2021) | 2019 → 2023 | 1,098 | −0.23 | −4.23 | −0.24 | 0.59 | 1.00 | 2011–18: +0.29 (t = 0.65) | NOT CONFIRMED |
| T3 | EIA Wednesdays: 10:30–11:00 predicts 15:30–16:00 (Wen et al. 2023) | 2019 → 2023 | 205 | −3.26 | −7.26 | −1.52 | 0.94 | 1.00 | 2011–18: +0.05 | NOT CONFIRMED |
| T4 | Bitcoin intraday momentum (Shen, Urquhart & Wang 2022) | 2021 → 2026-08 | 2,068 | −0.31 | −5.31 | −0.35 | 0.64 | 1.00 | 2017-09 → 2020: −0.37 | NOT CONFIRMED |
| T5 | Bitcoin long 22:00–24:00 UTC (Padyšák & Vojtko 2021) | 2022 → 2026-08 | 1,703 | +1.54 | −3.46 | 0.93 | 0.18 | 1.00 | 2017-09 → 2021: +3.44 (t = 1.06) | NOT CONFIRMED (the 2-hour share of BTC's drift is +0.55) |
| T6 | Bitcoin Monday effect (Caporale & Plastun 2019) | 2018 → 2026-08 | 3,160 days | +26.2 (Mon − other) | — | 1.38 | 0.084 | 0.59 | — | NOT CONFIRMED |
| T7 | Asian index intraday momentum, JP225 + AUS200 (Baltussen et al.) | 2020-06 → 2025 | 1,439 | +0.75 | −2.25 | 2.28 | 0.011 | 0.089 | 2011 → 2020-05: +0.29 | WEAK (below cost) |
| T8 | Crypto weekend → Monday US500, short after negative weekends (2025 *FRL*), **tradeable version** from the Sunday futures reopen | 2021 → 2025-06 (paper's period) | 77 | −8.2 | −9.7 | −0.50 | 0.69 | 1.00 | — | **NOT TRADEABLE**: whatever predictability exists is in the gap before futures reopen |

### 14.2 Systematic scan (family X): 24 instruments, 653 candidates

The scan covered hour-of-day, day-of-week, streaks, IBS and 20-day breakouts. Discovery ran on 2011–2017
(crypto 2018–21) and was **committed before the confirmation data was examined** (commit d3bf6be).
Confirmation ran on 2018–2025 (crypto 2022–26).

| | Count |
|---|---|
| Candidates | 653 |
| Discovered (BH q < 0.10) | 20: 16 hour-of-day effects, 1 day-of-week, 0 streak/IBS/breakout |
| **Confirmed** (Holm p < 0.05, same sign, net of cost > 0) | **0** |
| Significant but below cost (WEAK) | 1: **silver, 06:00–07:00 NY** (the hour before the 12:00 London silver fix): −5.1 bps in discovery, −2.4 in confirmation (Holm p = 0.006) against a 5-bps cost |

Every discovered effect shrank out of sample: gold's AM-fix hour, Brent on Mondays (−35 bps in
discovery), the ETH hours and the FX hours. The US500 02:00–03:00 drift was discovered again and failed
again (it is the Q7-P14 decay control). **Simple calendar and time-of-day rules on prop instruments don't
survive out of sample at retail costs.**

### 14.3 MR-06 on 15 untested world indices (W1, amendment A10)

Pooled 2000–2026: **+2.8 bps, t = 1.24**, NOT CONFIRMED. By index: FTSE MIB +20.3 (t = 2.8), IBEX +13.7
(t = 2.0), AEX +13.4 (t = 2.0) and Bovespa +10.3 were positive; Jakarta −11.9, Kuala Lumpur −5.9 and
Merval −7.9 were negative; the rest ≈ 0. Picking the winners now would be cherry-picking. MR-06 is a US
edge that also appears in Japan, Australia and possibly southern Europe, not a global law.

### 14.4 Noise-area intraday momentum (family N, amendment A11)

The rule is Zarattini, Aziz & Barbon's: a 14-day average move from the open at each half-hour mark; long
above the upper band, short below the lower band, flip at the opposite band, flat at the close.

| ID | Instrument / version | Net bps/day | t | Holm N | Sharpe | Paper's period (to 2024-04) | After (2024-05 → 2025) | Verdict |
|---|---|---|---|---|---|---|---|---|
| N1 | US500, conservative | +0.70 | 0.69 | 0.74 | 0.20 | +0.57 (paper reports Sharpe 0.61 on SPY) | +1.47 | NOT CONFIRMED |
| N2 | US500, TWAP trailing stop (the paper's best exit, TWAP for VWAP) | +1.09 | 1.58 | 0.23 | 0.44 | +1.39 (t = 1.89) | −0.75 | NOT CONFIRMED |
| **N3** | **US100, conservative** | **+3.02** | **2.54** | **0.028** | **0.73** | +2.66 (t = 2.15) | +5.31 (t = 1.38) | **CONFIRMED** |
| N4 | GER40 | +0.64 | 0.53 | 0.74 | 0.15 | +0.12 | +3.69 | NOT CONFIRMED |
| N5 | Gold (COMEX session) | +0.44 | 0.62 | 0.74 | 0.18 | +0.17 | +2.03 | NOT CONFIRMED |

**N3 robustness (post hoc,** [noise_area_robustness.py](noise_area_robustness.py)**):**

| Check | Net bps/day (t) |
|---|---|
| Lookback 10 / 14 / 20 days | +3.05 (2.55) / +3.02 (2.54) / +3.19 (2.67) |
| 60-min grid / 15-min grid | +2.65 (2.41) / +1.88 (1.44) |
| Cost 3 bps instead of 1.5 | +2.11 (1.77) |
| TWAP trailing stop | +3.06 (**3.50**), Sharpe 0.96 |
| **2011–2013, never used for this rule** | +2.93 (1.28), Sharpe 0.83 (3 years, low power) |
| 2014–2019 / 2020–2025 | +1.37 (0.96) / +4.86 (2.52) |
| Deflated Sharpe: family (N = 5) / all trials (N ≈ 731) | 0.90 / **0.22** |

**Reading this:** the effect is specific to US100, has the same sign and size in every period
including unseen 2011–13, and forms a plateau across parameters. It fails on US500, the paper's own
instrument. A plausible mechanism: leveraged Nasdaq ETFs (TQQQ/SQQQ) must rebalance in the direction of
the day's move before the close, and that flow is much larger relative to the market in the NDX than in
the S&P. Against it: one success among ~730 hypotheses is roughly what chance would produce, which is
what the DSR of 0.22 says. It needs a forward test before any money is committed.

## 15. Round 5 — prop books without Treasuries ([prop_round5.py](prop_round5.py), [prop_noise.py](prop_noise.py))

Bootstrap on 2014–25, intraday paths from minute bars, EA daily guard (3% two-step, 2% otherwise).
Pass probability · median days to pass. Zero-edge base rates use the demeaned combined books.

| Book | Two-step 10%/5% | One-step 10% (6% trailing) | Futures 50K (4% trailing) |
|---|---|---|---|
| **Zero edge** | 11–16% | 12–13% | 9–11% |
| **MR-06 US500, vol-scaled 2×** | **60% · 641 d** | 37% · 249 d | 29% · 227 d |
| MR-06 JP225 2× | 39% · 361 d | 31% · 157 d | 24% · 142 d |
| MR-06 AUS200 2× | 42% · 822 d | 24% · 334 d | 25% · 204 d |
| MR-06 US500 + JP225 + AUS200, 1× each | 55% · 435 d | 35% · 199 d | 32% · 121 d |
| **Noise-area US100 (N3) 2×** | 40% · 173 d | 26% · 65 d | 25% · 33 d |
| N3 3× | 34% · 92 d | 26% · 32 d | 21% · 26 d |
| **N3 with TWAP stop 3× (post hoc)** | **52% · 135 d** | 35% · 51 d | 26% · 39 d |
| MR-06 2× + N3 2× | 33% · 143 d | 25% · 54 d | 21% · 32 d |

**Reading this:**

- **MR-06 has the better edge-to-variance ratio,** so it has the higher pass probability, but it trades only ~19 times a year.
- **N3 trades almost every day,** so it is fast but noisier. Combining the two gives the speed of N3 and the pass rate of neither.
- **Choose by what the challenge rewards:**
  - A two-step account with no time limit favours MR-06.
  - A trailing-drawdown account is hard for every book here (about 2–3× the base rate at best).
- **These are in-sample sizing estimates.**

## 16. Round 6 — playing the prop game optimally (decision analysis, amendments A12–A13)

**Why this matters more than another edge test.** Five rounds show that robust retail edges are few and
small. With a small real edge, most of what a prop trader can still control is **how the edge is played
inside the firm's rules**:

- how much exposure to run;
- whether to size relative to the distance from the loss limit;
- whether to change sizing once funded.

These are decision problems with known theory:

- **Timid play is optimal in a favourable game** (Dubins & Savage 1965): with a positive edge and no deadline, smaller bets raise the probability of reaching the target before the floor.
- **CPPI** (Black & Perold 1992): exposure proportional to the cushion above a floor approaches the floor only asymptotically.
- **The funded account is an option:** the firm absorbs losses beyond the limit, so part of any account's value is the prop structure itself. The zero-edge twins measure that part.

This round tests no edge. It uses the return series of the two surviving books (in-sample) to rank
policies by money: EV per attempt and per account-month, including fee, pass rate, time, payouts and breach.

Rules: two-step 10%/5% (fee $500, 80% split, fee refunded on the first payout); one-step 10% (6% trailing);
futures 50K (4% EOD trailing, fee $150, 90% split, 50% consistency). All three have 365 days funded with
payouts every 14 days and an EA daily guard. Stationary bootstrap of 2014–25, 1,500 runs per cell; **every
run counts** (see the A12 correction). US$ per $100K two-step account ($50K futures).

### 16.1 Sizing changes the money more than the edge does

Two-step 10%/5%. Pass rate (zero-edge twin in brackets) · EV per attempt · mean months · EV per account-month.

| Book | Fixed 1× | Fixed 2× | Fixed 3–4× (fastest) | CPPI k = 10 | CPPI k = 20 |
|---|---|---|---|---|---|
| **MR-06 US500** (B1) | 77% (22%) · $2,782 · 56 mo · $50 | 60% (15%) · $3,818 · 28 mo · $137 | 3×: 47% (13%) · $3,678 · 17 mo · **$212** | 79% (16%) · $2,655 · 72 mo · $37 | cap 2×: **72% (17%) · $3,971** · 53 mo · $75 |
| **Noise-area US100** (B2) | 64% (24%) · $4,612 · 24 mo · $190 | 39% (17%) · $3,337 · 8 mo · $406 | 4×: 31% (17%) · $2,221 · 2.8 mo · **$783** | **78% (19%) · $4,801** · 62 mo · $77 | 49% (12%) · $3,405 · 75 mo · $46 |
| Noise-area US100, TWAP stop (B3, post hoc) | 91% (27%) · $6,249 · 37 mo · $171 | 65% (21%) · $7,204 · 16 mo · $454 | 4×: 44% (20%) · $5,218 · 4.7 mo · **$1,101** | 97% (17%) · $5,550 · 46 mo · $121 | 89% (15%) · **$7,965** · 47 mo · $168 |

**What this shows:**

- **The edge is what pays.** Zero-edge twins pass only 12–27% and earn between −$400 and +$800 per attempt. Every policy's edge value is positive.
- **For the same edge, the policy moves EV per account-month by 5–20×** (MR-06: $10 at 0.5× to $212 at 3×). Faster, riskier play wins per unit of time; cushion sizing wins per attempt.
- **Cushion sizing (CPPI) is the "timid play" lever.** It lifts pass rates well above fixed sizing on the same edge (MR-06 79% vs 60%; US100 78% vs 39%), while zero-edge twins stay at 16–19%. The boost comes from the edge, but it takes 4–6 years and 21–22% of runs are still undecided at the 10-year mark (k = 10).
- **By the pre-registered decision rule (maximum EV per account-month with positive edge value):** fixed 3× for MR-06 and fixed 4× for US100 on the two-step account; fixed 3–4× on the other rule sets.
- **With 30% payout haircut for counterparty risk:** MR-06 3× $143 per month; US100 4× $506 per month.

### 16.2 Other rule sets (EV per account-month at the recommended policy)

| Book | Two-step 10%/5% | One-step 10% (6% trailing) | Futures 50K (4% trailing) |
|---|---|---|---|
| MR-06 US500 | $212 (3×) | $233 (3×) | $79 (3×) |
| Noise-area US100 | $783 (4×) | $566 (4×) | $156 (3×) |
| Noise-area US100, TWAP stop (post hoc) | $1,101 (4×) | $870 (4×) | $263 (3×) |

Trailing-drawdown futures accounts return 3–5× less than the two-step account for the same edge.
**Correction (round 7):** futures prop firms (Topstep, Apex and others) require every position flat before
the daily close, so the MR-06 futures cell describes a trade those firms don't allow. See §17.5 for
published terms.

### 16.3 Funded-stage sizing (A13)

Challenge at the A12-recommended exposure. Funded stage:

| Book (two-step) | Funded policy | Breached within the year, given pass | EV per attempt | EV per account-month |
|---|---|---|---|---|
| MR-06 US500 | same (3×) | 53% | $3,678 | **$212** |
| | CPPI k = 40, cap 4× | **19%** | **$3,889** | $208 |
| | fixed 1× | 9% | $1,529 | $82 |
| Noise-area US100 | same (4×) | 99% | $2,221 | **$783** |
| | CPPI k = 40, cap 4× | 73% | $2,246 | $511 |
| | fixed 2× | 86% | $2,404 | $628 |

**Reading this:**

- **Money per month:** keep the challenge sizing. Funded accounts then churn, being breached within the year in most cases, but pay fast.
- **Keeping the funded account:** switch to cushion sizing once funded. For MR-06 it breaches 19% of the time instead of 53%, for about the same money per attempt.
- **Firms police aggressive funded behaviour** (consistency rules, payout caps, account reviews), and the presets only partly model this. Check each firm's actual terms before relying on the aggressive end.

### 16.4 What round 6 does and doesn't show

- **It shows** that, with the two edges this research found, prop accounts are positive-EV in this simulation, and that sizing policy is the biggest lever left: it changes money per month by an order of magnitude.
- **It doesn't show new edges.** The return series are in-sample (2014–25), the fees and terms are placeholders, and the bootstrap can't reproduce regime changes. N3 in particular is a candidate, not an established edge (DSR 0.22).
- **Parallel accounts on the same strategy are not independent.** They pass and fail on the same market days, so running five accounts is not five independent bets.

## 17. Round 7 — a true holdout, 16 more families, published firm terms (amendments A14–A20)

### 17.1 The 2026 holdout (A14, [run_holdout_2026.py](run_holdout_2026.py))

HistData now serves 2026-01-02 → 2026-09-18. None of the ~730 earlier trials touched it. The rules ran as
frozen code, with 2025 loaded only as warm-up. **Power was fixed in advance:** N3 had a 15% chance of
p < 0.05 even if its in-sample edge is true, so this holdout can catch a collapse but can't confirm.

| Rule | In-sample (bps, t) | 2026 (bps, t, n) | z vs in-sample | Verdict (A14 rule) |
|---|---|---|---|---|
| **N3 noise-area US100 (primary)** | +3.02 (2.54) | **+1.39 (0.33), 162** | −0.37 | **CONSISTENT** (Bayes factor ≈ 1; pooled estimate +2.9) |
| N3 TWAP stop (post hoc variant) | +3.06 (3.50) | −1.46 (−0.44) | −1.31 | INCONCLUSIVE |
| P10 first-candle ORB / P11 30-min ORB | +2.57 (3.16) / +2.47 (2.39) | −1.04 / −2.22 | −1.2 / −1.3 | INCONCLUSIVE |
| P12 GER40 close momentum | +2.07 (4.85) | +0.63 (0.45) | −0.98 | CONSISTENT |
| R1 CAC/FTSE close momentum | +1.01 (2.99) | −1.36 (−1.34) | −2.21 | **REJECTED** |
| T7 Asian index intraday momentum | +0.75 (2.28) | −0.99 (−0.76) | −1.30 | INCONCLUSIVE |
| R7 MR-06, 15:55 entry (not a clean holdout) | +15.9 (1.89) | +44.3 (1.56), 23 trades | — | descriptive only (n < 30) |
| Scan WEAKs: silver H06, EURUSD H06, NZDUSD H01 | +2.4 / +0.5 / +0.6 | +0.2 / −0.0 / +0.7 | — | CONSISTENT / INCONCLUSIVE / CONSISTENT |
| N1, N2, N4, N5 (calibration) | ≈ 0 | −1.9 / −4.9 / −0.5 / −4.7 | — | N2 REJECTED, others INCONCLUSIVE |

**Pipeline calibration (pre-registered):**
- The 10 rules that were positive in-sample (CONFIRMED, WEAK or PARTIAL) averaged a holdout t of **−0.15** (40% positive).
- The 19 null rules averaged **0.00**.
- **The WEAK and PARTIAL intraday results carried no detectable signal into 2026. They behaved like noise, which is what the multiple-testing guards predicted.** N3 stayed positive but the data can't separate +3 from 0.

**Data-quality finding (A14 addendum):** HistData's clock follows the **European** DST calendar (file time =
London − 5 h), not New York's. In the ~4 US/EU gap weeks a year the file is one hour behind New York.
- The A5 check (January vs July) could not see this.
- US-index rules that need the 09:30 or 15:55 bars simply lose those days, because the bars fall inside the file's break.
- Hour-bucket rules and non-US conversions were one hour off on ~8% of days, which blurs a signal but can't create one.
- New tests use `data_histdata.local_table`, which converts through London time.

**Second feed for N3 (X1, Dukascopy):** blocked. Dukascopy throttled this environment to about one daily
file per 30 seconds, so the 3,400-file sample could not be downloaded in the session (79 files done). **X1
is not reported.** It remains the cheapest independent check of N3 and belongs on the coding agent's list.
**Resolved in round 34 (§22.20):** Dukascopy's chart service serves the same candles fast. N3 on Dukascopy US100 2012–26: +3.73 bps/day (t 3.25), correlation 0.97 with HistData, 12/12 variants positive.

### 17.2 Family G and H: 16 more families (A15, A17–A20, [run_round7.py](run_round7.py), [run_h1.py](run_h1.py))

Each test ran on data after its paper's sample where possible. Holm is across G1–G13, as A18 fixed.

| ID | Hypothesis | Effect | t | Holm p | Verdict |
|---|---|---|---|---|---|
| G1 | Halloween, SPY 2002-11 → 2026-08 | winter − summer +1.6 bps/day | 0.58 | 1.00 | NOT CONFIRMED |
| G2 / G3 | Options-expiration week / the week after, 2011 → | −21.9 / +6.8 bps/week (both wrong sign) | −1.17 / 0.33 | 1.00 | NOT CONFIRMED |
| G4 | MR-06 pays more when VIX is high (Nagel 2012) | +12.7 bps/trade (high 27.4 vs low 14.6) | 1.58 | 0.45 | NOT CONFIRMED |
| G5 | Volatility-managed SPY, 2016 → | alpha +2.7%/yr; Sharpe 0.86 vs 0.86 | 0.99 | 1.00 | NOT CONFIRMED |
| **G6** | **Time-series momentum, 16 ETFs + BTC, 2012 →** | **+91 bps/month net, Sharpe 0.62** | **2.62** | **0.053** | **WEAK** (CONFIRMED under the original 11-test Holm, 0.044) |
| G7 | Next-day reversal of strong last-hour moves | +9.0 bps/trade net | 2.10 | 0.17 | WEAK (2026 −0.3) |
| G8 | Asian-range breakout at the London open, EURUSD/GBPUSD | +1.1 gross, **−0.1 net** | 2.54 | 0.06 | WEAK (net < 0) |
| G9 | Crypto funding crowding filter, 2021 → | −1.5 bps/day | −0.22 | 1.00 | NOT CONFIRMED |
| G10 | Williams volatility breakout, US500/US100/GER40 | +1.5 bps/day net (US100 t = 3.9) | 2.66 | 0.050 | WEAK (2026 −1.3) |
| G11 | NR7 breakout | −1.0 net | 0.21 | 1.00 | NOT CONFIRMED |
| **G12** | **MR-06 inside the next session (09:30 → 16:00)** | **+11.9 bps/trade net; SPY 1993–2026 +10.5 net (t = 2.65, 708 trades)** | **2.12** | 0.17 | **WEAK** (2026: 26 trades, −8.4) |
| G13 | Opening-gap fade | −1.4 net | 0.03 | 1.00 | NOT CONFIRMED |
| H1 | Cross-sectional momentum across 14 equity indices, 2013 → | −17 bps/month net | −0.88 | — | NOT CONFIRMED (2000–12 also negative) |
| H2 | Earnings-announcement premium, 19 large US stocks (a 2014 universe; EDGAR 8-K Item 2.02 release times), close E−2 → close E, minus SPY ([run_h2.py](run_h2.py)) | +13.7 bps gross, +7.2 net per event (1,650 events) | 0.71 | — | NOT CONFIRMED. It was +46.6 (t = 1.89) in 2005–13, and the pre-event drift +39.5 (t = 2.8): **decayed after publication** |
| H3 | MR-06 on the same 19 stocks ([run_h3.py](run_h3.py)) | +6.0 gross, **+1.0 net** per trade | 1.89 | — | **CONFIRMED by rule, economically nil**: market-adjusted net −2.3; DSR 0.002; 27% of signals fall on index MR-06 days. Don't build |

**Two corrections to my own round-7 bookkeeping:**
- **G6 is a re-test, not a new family.** Round 1's P6 (TSMOM on 25 ETFs, including bonds) was already "validated (fragile)", and TF-01 was "validated but = vol-scaled beta". G6 re-tests it on the prop-tradeable universe with no bonds, after publication.
- **A15 was wrong to drop the pre-holiday premium as faded.** My own round 1 validated it (P18: +12.0 bps, t = 3.25; 2001 → +8.3, p = 0.048). The published fading (Ko 2021) conflicts with my own data. P18's result stands as the evidence; it is small (~9 days a year).

### 17.3 What is behind trend following (G6, post hoc, [diag_round7.py](diag_round7.py))

| Universe, 2012-01 → 2026-08 | TSMOM (bps/month, t) | Same weights, always long | Timing value (TSMOM − long) |
|---|---|---|---|
| All 17 | +91 (2.62), Sharpe 0.62 | +54 (1.00) | +39 (0.59) |
| FX ETFs only | +31 (0.64) | −150 (−2.23) | **+184 (1.79)** (rode the dollar) |
| Equity ETFs only | +114 (2.16) | +193 (2.92) | −78 (−1.48) |
| Commodities only | +63 (0.90) | +52 (0.71) | +12 (0.11) |

- Correlation with SPY is 0.04. **It is a diversifying risk premium, not disguised equity beta**, but its timing value is not significant by itself.
- **It does not survive prop-account implementation.** The weights put ~3.5× gross notional on the account:
  - A 2%/yr CFD financing mark-up turns +9%/yr into **+1.8%/yr at 19% volatility** (2014–2025).
  - Futures prop firms, which have no mark-up, ban overnight holds.
  - FTMO lifecycle (§17.5): **$23 per account-month** (2% mark-up), $88 (0%), negative at 4%.

### 17.4 Where MR-06's edge sits inside the day (G12 and a diagnostic)

The next-day return after three down closes splits into overnight (16:00 → 09:30) and intraday
(09:30 → 16:00) parts:

| Data | Overnight (bps, t) | Intraday (bps, t) | Trades |
|---|---|---|---|
| SPY 1993–2026 | +15.2 (5.84) | +11.7 (2.63) | 713 |
| HistData US500 2014–25 | +10.6 (1.99) | +13.1 (2.17) | 261 |
| HistData US100 2014–25 | +10.3 (1.65) | +15.3 (1.90) | 245 |

About half of MR-06's edge is earned during the next session, and that half is tradeable in futures
accounts that must be flat by the close. By rule G12 is WEAK (26 trades in the 2026 holdout lost), but it
has 33 years of SPY evidence behind it.

### 17.5 Published firm terms (A16, [prop_lifecycle_real.py](prop_lifecycle_real.py))

Presets built from the firms' published terms on 2026-09-26 (`tools/propsim/presets/ftmo_*`, `topstep_50k`):

- **FTMO 2-Step $100K:** $540; 10%/5%; 5% daily; 10% static; 80% split; fee refunded.
- **FTMO 1-Step $100K:** $499; 10%; 3% daily; 10% EOD trailing; 50% Best Day Rule; 90% split.
- **Topstep 50K:** $49/month + $149 activation; $3,000 target; $2,000 EOD trailing; 55% consistency; payouts after 5 winning days of $150, capped at 50% of the balance or $2,000.

Each book runs only where its holding period is allowed:
- **FTMO Standard:** no weekend holds and a ±2-minute news blackout once funded.
- **FTMO Swing:** both allowed.
- **Topstep:** flat by 3:10 PM CT.

Recommended policy (A12 rule), pass rate (zero-edge twin) · EV per attempt · mean months · **EV per account-month**:

| Venue | MR-06 | Noise-area US100 | MR-06 + US100 combined | Other |
|---|---|---|---|---|
| **FTMO 1-Step (Standard)** | no-weekend, 3×: 44% (20%) · $1,128 · 18 mo · $62 | **news-filtered, 4×: 37% (25%) · $2,271 · 2.3 mo · $983** | 3×: 35% (18%) · $2,112 · 3.6 mo · $590 | — |
| **FTMO 2-Step Standard** | no-weekend, 3×: 36% (14%) · $1,594 · 22 mo · $73 | news-filtered, 4×: 31% (16%) · $2,043 · 2.9 mo · **$715** | 3×: 30% (11%) · $1,971 · 4.4 mo · $449 | intraday MR-06 3×: $93 |
| **FTMO 2-Step Swing** | 3×: 47% (13%) · $3,654 · 17 mo · **$210** | 4×: 31% (17%) · $2,189 · 2.8 mo · **$772** | + trend: 1×: $116 | trend alone: $23 |
| **Topstep 50K** | not allowed (overnight) | 3×: 23% (14%) · $109 · 0.9 mo · $124 | N3 + intraday MR-06: $19 | intraday MR-06: −$35 |

**What this shows:**

- **FTMO 1-Step with the US100 rule is the best venue tested:** about $980 per account-month. Its 3% daily limit sits above the 2% EA guard, and its 90% split and cheap fee help. The Best Day Rule (50% of winning days' profit) is modelled both in the challenge and as a payout gate (the gate is my assumption; FTMO lists the rule under "Challenge & Account").
- **MR-06 needs a Swing account.** FTMO Standard bans weekend holds, and in 2014–25 the weekend-spanning MR-06 trades were the best ones (the no-weekend book averages 9.4 bps a trade against 18.5). The value falls from $210 to $73 per account-month.
- **The news blackout costs the US100 rule 11%** (3.02 → 2.68 bps/day) and about 7% of its value.
- **Topstep is a poor venue for these edges.** The monthly subscription punishes slow books, and the payout cap and 5-winning-day gate slow the funded stage. Best case is $124 per account-month.
- **Combining books didn't pay per account-month here.** Equal-risk weighting shrinks the fast US100 book, and it is the fast book that earns the most per month. Run the books in separate accounts.
- **Maximum pass probability is still cushion sizing** (CPPI k = 10: 71–82% pass vs 13–22% for zero edge), at five years or more per account.
- **A 30% payout haircut** cuts every figure by about a third.

**Correction to §16.2:** its futures column simulated MR-06 on a trailing-drawdown account as if overnight
holds were allowed. They are not at Topstep-style firms. Treat that column as "not allowed" for MR-06.

### 17.6 Other round-7 checks (post hoc or implementability)

- **I3, N3 with the paper's own volatility targeting:** Sharpe **falls** from 0.73 to 0.57 (2014–25). The effect is stronger when volatility is high, which is exactly when volatility targeting cuts size. Keep flat sizing. The prop metrics are about equal ($754 vs $772 per account-month).
- **Where the rules fired in 2026:** R7 (MR-06, 15:55 entry) had 23 trades averaging +44 bps (t = 1.6). N3 averaged +1.4 bps a day. Neither is evidence by itself, but neither contradicts the case for building them.

## 18. Round 8 — checks that decide how to build and fund (amendment A21, [round8.py](round8.py))

| Check | Result | Consequence |
|---|---|---|
| **X2: second feed for N3** (Yahoo 60-min QQQ and ^NDX, 60-min-grid variant, 2023-11 → 2026-09) | Daily P&L correlation with HistData US100 **0.99** (QQQ, 596 common days) and 0.94 (^NDX). Means +3.7 (QQQ) vs +4.1 bps/day (HistData) on common days. QQQ alone: +2.9 bps/day over 706 days (t = 1.3) | **FEEDS AGREE.** N3 is not a HistData artefact at the 60-minute grain. The 30-minute rule on a second feed (X1) is still open |
| **E1: MR-06 exit** (SPY 1993–2026, 711 signals) | Per day held: t+1 **26.1 bps**, t+2 19.3, t+3 16.5. Holding longer is significantly worse per day (t = −2.1 and −2.3) | **Keep the next-close exit** |
| **C1: MR-06 vs N3** (2014–25) | Correlation 0.03 daily and 0.03 monthly; MR-06 lost on 15% of N3's 20 worst days | Separate accounts are close to independent bets |
| **S1: regime** (bootstrap from each half) | N3 FTMO 1-Step 4×: **$877** (2014–19) vs **$1,244** (2020–25) per account-month. N3 FTMO 2-Step 4×: $643 vs $1,138. MR-06 FTMO Swing 3×: $123 vs $372 | Positive in both halves, but 2020–25 volatility did much of the work. Plan on the 2014–19 figures |
| **S2: edge haircut** (twin + λ × mean) | EV per attempt at λ = 0 / 0.5 / 1: N3 1-Step **$532 / $1,091 / $2,271**; N3 2-Step $321 / $988 / $2,189; MR-06 Swing $296 / $1,180 / $3,654 | **The zero-edge twin is positive-EV in every preset.** Losses stop at the fee while funded payouts are withdrawn, which is the "free option" in funded-account rules. Firms counter it with reviews, conduct rules and denied payouts that the simulator doesn't model. **Count only the edge value above λ = 0**, and treat λ ≈ 0.5 as the planning case |
| **F1: forward-test arithmetic** | Time to t = 2 on forward data: N3 **7.5 years** (1,893 days); MR-06 **10 years** (189 trades); MR-08 31 years. A sequential test (SPRT, α = β = 0.1) expects 6.6 / 8.7 / 27.7 years | **Paper trading can't validate these edges.** It checks implementation parity and catches a collapse. Pre-set stop rule: N3 forward mean below −16.7 / −10.6 / −6.6 bps/day after 60 / 126 / 252 days; MR-06 below −19.7 / −7.9 bps per trade after 60 / 126 trades |

## 19. Round 9 — edge families as strategy grids, and portfolios (amendment A22)

**Why this round is different.** Rounds 1–8 validated single rules. A portfolio needs families of
strategies explored across instruments, signal definitions, exits and filters. Choosing from a grid needs
the statistics built for that: Hansen SPA, Romano–Wolf stepdown, CSCV probability of backtest overfitting
(PBO), and walk-forward selection ([multitest.py](multitest.py), with unit tests).

Four families, **1,246 variants**, each split into discovery and validation periods:

| Family | Variants | SPA p (validation) | PBO | Walk-forward (yearly re-pick, top 5) | Romano–Wolf survivors | Verdict |
|---|---|---|---|---|---|---|
| **A. Index reversal** (8 indices × 12 signals × 3 exits × 3 filters; validation 2013–26) | 864 | **0.031** timing value (0.0125 expanding benchmark; 0.0005 raw) | **0.19** | **Sharpe 0.47, t = 2.1** (raw 0.69, t = 2.9) | 2 (timing) / 17 (raw), all but one on US100 | **EDGE FAMILY** |
| B. Noise-area intraday momentum (9 markets × 36; validation 2020–25) | 324 | 0.23 (US100 alone 0.036) | 0.06 | Sharpe 0.48, t = 1.3 | 0 | WEAK (US100 only; US500 all positive but n.s.; 2026 holdout median −0.9) |
| C. Trend (48 portfolio variants; validation 2017–26) | 48 | 0.16 raw; 0.76 expanding benchmark | 0.61 | Sharpe 0.28, t = 0.9 | 0 | WEAK (raw), no timing value |
| D. G10 carry and momentum (validation 2012–26) | 10 | 0.72 | 0.003 | Sharpe −0.05 | 0 | NO EDGE (carry Sharpe 0.4–0.55 before 2012, ≈ 0 after swap mark-ups) |

**Two amendments, disclosed (PREREGISTRATION A22):**
- Long-biased families are judged on timing value, P&L minus position × the asset's same-year mean return, so that the equity premium doesn't count as edge.
- That benchmark turned out to be invalid for trend strategies, because it contains the year's own drift. Family C therefore reverts to its pre-registered raw verdict, and a look-ahead-free expanding-mean benchmark is reported for both A and C.

### 19.1 Family A up close ([family_a_aspects.py](family_a_aspects.py), descriptive)

- **A plateau, not a peak.** In 2013–26, 79–94% of each US index's 108 variants have positive timing value (median raw Sharpe 0.43). At +3 bps extra cost per trade, 95% stay positive.
- **Where it works:**
  - US500, US100, US30, US2000 and JP225 (per-index SPA p: QQQ 0.006, N225 0.007, SPY 0.09, DIA 0.10, IWM 0.11);
  - **not** DAX, FTSE or ASX 200 (p 0.53–0.68).
- **Best choices** (median validation timing Sharpe across US variants):

  | Choice | Best | Worst |
  |---|---|---|
  | Signal | **IBS < 0.10 (0.44)** | the large-down-day signal (0.09) |
  | Exit | **first up close (0.38)** | fixed 3 days (0.20) |
  | Filter | **none (0.37)** or below SMA(200) (0.35) | "only above SMA(200)" (0.19) |

  Other signals: 2–5 down closes, RSI(2) < 5–20 and 5-day lows are all at 0.31–0.34. The common "only above SMA(200)" filter *hurts*.
- **Ensembles beat single picks.** Trading every variant, weighted by discovery volatility:
  - all 108 US100 variants: validation Sharpe **1.00** (t = 4.7), timing value 0.67 (t = 3.1);
  - all 432 US variants plus JP225: 0.90 (t = 4.0).
- **Diversification inside the family:**
  - about **8 effective independent bets** among the 432 US variants (median pairwise correlation 0.28);
  - the same rule correlates 0.4–0.7 across US indices, but ≈ 0.1 between the US and JP225.
- **Tier-1 strategies** (Romano–Wolf, timing value):
  - US100 IBS < 0.10 with a first-up-close exit: timing Sharpe 0.96, 23 trades/yr;
  - US100 RSI(2) < 20 with a first-up-close exit: 0.80, 28 trades/yr.
- **Full list:** [../strategy_library.csv](../strategy_library.csv) has every variant with discovery, validation and 2026 statistics and a robustness tier:
  - Tier 1: 2 strategies;
  - Tier 2: 218 reversal variants (validation timing Sharpe ≥ 0.3 with all parameter neighbours positive) and 22 intraday-momentum variants, 19 of them on US100.

### 19.2 A portfolio chosen only from discovery data ([run_portfolio.py](run_portfolio.py))

**Rule, fixed in A22:**
- Per family, keep variants in the top 20% by discovery Sharpe whose parameter neighbours are positive.
- De-duplicate at correlation 0.6; cap at 8 per family and 2 per instrument.
- Weight by inverse volatility within a family, then equal risk across families.

**Out of sample 2020–25:**

| Book | Sharpe | Return / volatility | Max drawdown |
|---|---|---|---|
| **Portfolio** | **0.69** (t = 1.8) | 6.2% / 9.0% | −20% |
| Family A part | 0.79 (t = 2.1) | 3.7% / 4.7% | −6% |
| Family B part | 0.34 | 2.1% / 6.1% | −14% |
| Family C part | 0.02 | — | −11% |
| Family D part | 0.08 | — | −7% |
| All 1,246 variants equal-risk | −0.07 | — | −20% |
| The single best discovery variant | 0.44 | — | −18% |

- **2026 holdout:** the portfolio 0.42; family A 1.81, D 1.69, B −0.84, C −0.71.
- Family correlations out of sample are between −0.10 and +0.09.
- **The selection rule works, and blind diversification doesn't.** 60% of the return came from family A. Adding the weak families diluted it.

### 19.3 As prop books

**The whole portfolio** ([portfolio_paths.py](portfolio_paths.py)) is bootstrapped from its out-of-sample 2020–25 returns, with three models of intraday lows. The answer depends entirely on how the 14 legs' intraday lows are modelled:
- **Pessimistic** (every leg at its worst at once): 24% pass at 1× on FTMO 2-Step.
- **Middle** (independent excursions): 54% pass at 1× (zero edge 17%); CPPI 73%.
- **Close-only** (no intraday risk): implausibly good; not used.
- **Conclusion:** a multi-market book is a poor single prop account. Keep prop accounts focused.

**Family A alone** (8 legs, lows summed, pessimistic):
- FTMO 2-Step at 4×: 41% pass (15%), about $393 per account-month;
- FTMO 1-Step at 4×: 56% pass (24%), about $708;
- CPPI: 86–87% pass.

**The reversal ensemble** ([prop_ensemble.py](prop_ensemble.py), post hoc; all variants per index, weights from pre-2013 data, exact per-index intraday lows, bootstrapped from 2013–26, 1× ≈ 15% annual volatility):

| Book | Account | Size | Pass (zero edge) | EV per attempt | Months | EV / account-month |
|---|---|---|---|---|---|---|
| 4 US indices | FTMO 2-Step | 1× | **70% (26%)** | $7,649 | 17 | $452 |
| 4 US indices | FTMO 2-Step | 2× | 52% (19%) | $6,981 | 7.0 | **$995** |
| 4 US indices | FTMO 2-Step | CPPI k = 10 | **74% (12%)** | $6,215 | 29 | $213 |
| US + JP225 | FTMO 2-Step | CPPI k = 10 | **80% (17%)** | $8,644 | 26 | $335 |
| US + JP225 | FTMO 1-Step | 2× | 49% (18%) | $4,976 | 4.5 | **$1,103** |

**Compared with the single MR-06 rule** (≈ $210 per account-month on the same account): the ensemble trades on many more days at a similar Sharpe, so it reaches targets 3–5× faster.

**Caveats:**
- The ensemble was chosen after seeing family A.
- 2013–26 is also the period that qualified family A.
- The zero-edge twin still shows positive EV (the funded-account option; §18).

## 20. Round 10 — seven more families (amendment A23, [run_round10.py](run_round10.py))

The same battery as round 9 on **3,768 more variants.** Long-biased families are judged on timing value
against a look-ahead-free expanding mean (J against the same-year mean, as family A).

| Family | Variants | SPA p (validation) | PBO | Walk-forward | Verdict and reading |
|---|---|---|---|---|---|
| E. Reversal outside equities (gold, silver, oil, gas, 4 FX pairs, BTC, ETH; long and short) | 2,160 | 0.25 | 0.25 | Sharpe −0.02 | **NO EDGE.** Family A's effect does not carry over to commodities, FX or crypto |
| F. Per-market trend (Donchian, MA crossover, momentum; 22 markets) | 396 | 0.47 timing (0.02 raw) | 0.28 | −0.03 timing (0.74 raw) | **NO EDGE** on timing value. The raw "edge" is Bitcoin's drift: long-only Bitcoin trend rules ride the bull market |
| G. Index-pair relative value (6 synchronous pairs, reversion and momentum) | 324 | 1.00 | 0.43 | negative | **NO EDGE.** Two legs of cost and financing |
| H. Calendar (turn of month 4×4, weekday, pre-holiday; 8 indices) | 176 | 0.46 timing (0.11 raw) | 0.36 | Sharpe 0.05 | WEAK. The pre-holiday and turn-of-month effects seen in round 1 don't survive family-level testing |
| I. Crypto trend (8 coins, the 2019 top-8 to avoid survivorship; validation 2022–26) | 160 | 0.48 | 0.44 | t = 0.7 | WEAK. Bitcoin's trend edge in F does not hold on a survivorship-free universe after 2021; 10%/yr CFD financing makes it negative |
| J. Family A's grid on HK50, EU50, FRA40, SPA35 and the Nasdaq Composite | 540 | **0.017** | 0.35 | Sharpe 0.11, t = 0.5 | **EDGE FAMILY by the rule, not a new edge** (see below) |
| K. Cross-sectional weekly reversal, 19 large US stocks (market-neutral) | 12 | 1.00 | 0.02 | Sharpe −0.61 | **NO EDGE.** All 12 variants are negative in 2014–26 |

**Reading family J honestly:**
- **Where the significance comes from:**
  - the Nasdaq Composite (95% of variants positive; per-market p = 0.026), which is essentially US100 again;
  - a single Euro Stoxx 50 variant (per-market p = 0.002, but only 55% of its variants positive).
- **CAC 40, IBEX and the Hang Seng have no edge** (p 0.19–0.90).
- **Selection has no predictive power** within J (z = −0.15).
- **In the portfolio it hurt:** adding J, as A23 requires, lowered the 2020–25 portfolio Sharpe from 0.69 to 0.63 and deepened the maximum drawdown from −20% to −34%. J correlates 0.57 with family A; the 2026 holdout rose from 0.42 to 0.86.
- **Limitation of the verdict rule:** it does not test plateau breadth. **J adds no new market to the reversal sleeve.**

**A data artefact caught (A23 amendment):** Yahoo's daily FX bars are unusable for close-anchored rules.
- On Yahoo EURUSD, IBS correlated −0.69 with the next day's return, and family E's FX variants showed a walk-forward Sharpe near 10.
- On HistData bars that close at 16:45 NY, the correlation is −0.02 to +0.01 and the edge is zero.
- Yahoo's FX close sits 36 bps on average from the 17:00 NY price.
- The FX legs of E and F were rebuilt from HistData, and the Yahoo results withdrawn.

**Round 10's answer to "are there more edge families?":** not on prop-tradeable instruments, with the
data and costs available here. Reversal is the one mechanism that survives family-level testing, and only
in US index products (plus JP225). Everything else is weak, redundant or absent. The strategy library now
lists all **5,014** variants.

## 21. Round 11 — the edges as SQX would trade them, and FX / metals families (amendments A24, A25; [run_round11.py](run_round11.py))

**The user's question:** which edges can StrategyQuant X build that suit prop accounts, mainly in FX,
indices and metals? Round 11 answers it in two parts.

1. **A review of the index edges as SQX would trade them:**
   - the reversal family on SQX-style bars (R1);
   - without weekend holds (R2);
   - the US100 momentum rule rebuilt from native SQX blocks (R3).
2. **Four new families for FX, metals and European indices** (L, M, Q, R). All are intraday and flat before the NY rollover.

A25 then ran the prop lifecycle on the resulting books.

**Common settings:**
- **Data:** HistData 1-minute CFD quotes with the corrected clock, parsed into arrays ([data_minutes.py](data_minutes.py)).
- **Costs:** A24's costs per round trip.
- **Battery:** the A22 battery.
- **DSR count:** 6,053 trials, with R1's 1,620 implementation measurements disclosed separately.

### 21.1 Does the reversal edge survive the way SQX trades it? (R1, R2)

Family A's grid is 12 signals × 3 exits × 3 filters = 108 variants per market. It was re-run three ways, 2014-01 → 2026-08:

| Build | Bars | Signal | Entry and exit |
|---|---|---|---|
| **(c) M5 chart + session-daily conditions** | Cash-session daily bars; the 15:55 price stands in for today's close | 15:55 NY (Tokyo 14:55, 15:25 from 2024-11-05) | At 15:55; exit at 15:55 on the exit day |
| **(a) broker daily bars** | 24-hour CFD bars closing 17:00 NY. Gold uses 19:00 → 16:45, per the A24 data rule | At the bar close | Next bar's open |
| **(b) cash-session daily bars** | 09:30–16:00 NY (Tokyo cash) | At the session close | Next session's open |

**Per market.** Each cell shows three numbers:
- the equal-risk ensemble's timing-value Sharpe;
- the share of the 108 variants with positive timing value;
- the per-market SPA p (timing value).

| Build | US500 | US100 | JP225 | GER40 (control) | XAUUSD (control) |
|---|---|---|---|---|---|
| Family A (Yahoo closes, entry at the close): the research baseline | 0.56 · 93% · p 0.107 | 0.69 · 93% · p 0.010 | 0.29 · 83% · p 0.013 | −0.11 · 40% · p 0.833 | — |
| **(c) M5, 15:55** | 0.43 · 86% · p 0.112 | **0.59 · 94% · p 0.024** | 0.33 · 83% · p 0.054 | −0.63 · 1% · p 0.967 | 0.06 · 52% · p 0.780 |
| (a) broker D1, next open | 0.45 · 86% · p 0.066 | 0.48 · 85% · p 0.017 | 0.21 · 74% · p 0.189 | −0.39 · 19% · p 0.939 | −0.16 · 30% · p 0.224 |
| (b) cash-session D1, next open | 0.27 · 79% · p 0.105 | 0.53 · 90% · p 0.012 | −0.04 · 49% · p 0.638 | −0.58 · 5% · p 0.980 | −0.19 · 22% · p 0.888 |
| **(c) without weekend holds (R2)** | 0.36 · 80% · p 0.255 | **0.65 · 90% · p 0.009** | 0.33 · 80% · p 0.045 | −0.35 · 31% · p 0.236 | −0.04 · 39% · p 0.627 |

**Combined books** (equal risk across markets; timing-value Sharpe with HAC t, then the raw Sharpe):

| Build | US500 + US100 | US500 + US100 + JP225 |
|---|---|---|
| Family A (Yahoo closes) | 0.65 (t 3.0) · raw 0.89 | 0.67 (t 2.8) · raw 0.96 |
| **(c) M5, 15:55** | **0.53 (t 2.5) · raw 0.76** | **0.58 (t 2.4) · raw 0.86** |
| (a) broker D1 | 0.48 (t 2.0) · raw 0.69 | 0.42 (t 1.8) · raw 0.64 |
| (b) cash-session D1 | 0.41 (t 1.8) · raw 0.63 | 0.31 (t 1.3) · raw 0.57 |
| **(c) no weekend holds (R2)** | **0.52 (t 2.2) · raw 0.72** | **0.59 (t 2.3) · raw 0.84** |

**Reading:**
- **The edge survives an SQX build.**
  - Build (c) keeps 82–87% of the research ensemble's Sharpe.
  - Its daily P&L correlates 0.87–0.89 with family A's in each market: it is the same edge, measured on tradeable CFD quotes at 15:55.
  - US100 is significant on its own under every build (per-market SPA 0.009–0.024).
- **Broker daily bars (a) are fine for the US and poor for JP225.**
  - US500 + US100 keep 91% of (c) (0.48 vs 0.53).
  - JP225 falls to 0.21, and its correlation with the research version drops to 0.25. A 17:00-NY daily bar mixes the Tokyo session with the following US session.
- **Cash-session bars with next-open entry (b) lose the overnight part:**
  - JP225: all of it (−0.04). Its reversal return is earned right after the Tokyo close.
  - US500: 37% (0.27 vs 0.43).
  - US100: little (0.53 vs 0.59).
- **Predictions (A24):**
  - "(c) ≈ family A": roughly right.
  - "(b) loses half": right for US500, too pessimistic for US100, too optimistic for JP225.
- **Controls behave:** GER40 and gold show no edge under any build (1–52% of variants positive). A build cannot manufacture this edge where the research found none.
- **The parameter map is stable across builds** (US variants, median timing Sharpe):
  - IBS < 0.10 is at or near the top in every build (0.42–0.52; in (a), RSI(2) < 20 and IBS < 0.25 edge it);
  - the "above SMA(200)" filter is worst in every build (0.09–0.18);
  - a fixed 3-day exit is worse than the first up close or the next close, except in (b), where the three exits are similar.
- **Variants to build:** 141 of the family-A Tier 1/2 variants on SPY, QQQ and ^N225 have positive timing value under all three builds. They are listed in [../sqx_implementation_grid.csv](../sqx_implementation_grid.csv), which gives every variant's Sharpe under each build.

**R2, no weekend holds.** An FTMO Standard account forbids weekend holds. Skipping entries on the last session
of the week, and exiting open trades at Friday's 15:55, leaves the Sharpe unchanged:
- US500 + US100: 0.52 vs 0.53;
- with JP225: 0.59 vs 0.58.

Trades per year fall from about 11 to 8.8, and exposure from 7% to 5%. The P&L shrinks with the exposure;
the risk-adjusted return doesn't. (MR-06 alone lost about a third of its value to the same rule, §17.5.)
**The ensemble does not need a Swing account.**

### 21.2 A native SQX version of the US100 momentum rule (R3)

N3 needs a custom indicator: the 14-day average move from the open at each time of day. R3 tested 12
versions built only from standard blocks:
- **Bands:** the session open ± k × (the prior session's range, or ATR(14) of session bars).
- **Entry:** stop orders; the first touch enters.
- **Exit:** flat at 15:59, or stop-and-reverse at the opposite band.
- **Costs:** 1.5 bps per entry.

Period: US100, 2014-01 → 2026-08.

| Variant | Sharpe | Net bps/day | t | Correlation with N3 | Entries/day | 2014–19 | 2020–26 |
|---|---|---|---|---|---|---|---|
| range, k 0.3, flat | 0.39 | +2.27 | 1.48 | 0.55 | 0.94 | 0.21 | 0.52 |
| range, k 0.3, reverse | 0.77 | +4.41 | 2.66 | 0.62 | 1.30 | 0.62 | 0.88 |
| **range, k 0.5, flat** | **0.91** | **+4.21** | **3.27** | 0.60 | 0.75 | 0.73 | 1.05 |
| range, k 0.5, reverse | 0.94 | +4.37 | 3.28 | 0.61 | 0.84 | 0.79 | 1.07 |
| range, k 0.7, flat | 0.52 | +2.00 | 1.79 | 0.53 | 0.55 | 0.40 | 0.61 |
| range, k 0.7, reverse | 0.42 | +1.64 | 1.46 | 0.55 | 0.58 | 0.26 | 0.53 |
| ATR14, k 0.3, flat | 0.37 | +2.10 | 1.45 | 0.56 | 0.91 | 0.25 | 0.46 |
| ATR14, k 0.3, reverse | 0.43 | +2.44 | 1.57 | 0.63 | 1.14 | 0.30 | 0.52 |
| ATR14, k 0.5, flat | 0.59 | +2.66 | 1.93 | 0.63 | 0.66 | 0.35 | 0.77 |
| ATR14, k 0.5, reverse | 0.51 | +2.28 | 1.68 | 0.64 | 0.70 | 0.28 | 0.68 |
| ATR14, k 0.7, flat | 0.36 | +1.26 | 1.17 | 0.53 | 0.41 | 0.28 | 0.42 |
| ATR14, k 0.7, reverse | 0.36 | +1.27 | 1.19 | 0.53 | 0.42 | 0.34 | 0.38 |
| *N3 on the same data* | *0.52* | *+2.27* | *2.02* | *1* | — | — | — |

**Verdict (A24 rule): build N3 natively.**
- The grid's median Sharpe is 0.47, 89% of N3's; the rule needed ≥ 70%.
- The median correlation with N3 is 0.58; the rule needed ≥ 0.5.

**Robustness:**
- All 12 variants are positive in both halves of the sample.
- Prior-range bands beat ATR bands, and k = 0.5 is the best width. Choosing k = 0.5 is post hoc; the median is the tested claim.

**US500:** N1's native versions have a median Sharpe of 0.04, against 0.13 for N1 itself. Still no edge there.

### 21.3 Four new families for FX, metals and European indices (A24 Part 2)

| Family | Variants | SPA p (validation) | PBO | Walk-forward | Verdict and reading |
|---|---|---|---|---|---|
| **L.** FX and gold session seasonality (Breedon & Ranaldo 2013): long or short each London-time window. 7 majors + gold; validation 2014 → | 64 | 1.00 | 0.11 | Sharpe −0.33 | **NO EDGE.** The published pattern (a currency is weak in its home hours) was there in 2003–13 and is gone: EURUSD and GBPUSD short in European hours, discovery Sharpe 0.53 / 0.50 → validation 0.08 / 0.07. After 2013, gross effects are about 1 bp per window or less (largest ≈ 1.1 bps), except gold long in Asian hours (+2.0 bps gross, below its 2.5-bp cost) |
| **M.** FX night mean reversion: fade M15 closes outside BB(20, k) or RSI(3) extremes, 19:00–00:45 NY. 6 crosses + 3 majors; validation 2016 → | 108 | 1.00 | 0.0001 | Sharpe −2.10 (t −7.1) | **NO EDGE.** All 108 variants are negative after costs (median Sharpe −2.5). Night reversion exists gross (median +0.14 bps per trade; 57% of variants gross-positive) but is a tenth of night spreads (1.5–3 bps) |
| **Q.** European cash-open gap, fade or follow: GER40, UK100, FRA40; validation 2020 → | 72 | 1.00 | 0.25 | Sharpe −0.34 | **NO EDGE.** Following gaps on FRA40 and GER40 worked in 2013–19 (Sharpe 0.4–0.7) and faded after (≤ 0.21). Fading gaps loses |
| **R.** Session-range breakout or fade: the Asian range traded 07–12 London, or the London-morning range traded 13–16. Gold, silver, 4 majors; validation 2017 → | 48 | **0.031** | 0.0005 | **Sharpe 0.005** (t 0.02) | **EDGE FAMILY by the rule, resting on USDJPY alone** (see below) |

**Reading family R honestly:**
- **One market carries it:**
  - USDJPY per-market SPA 0.009; all other markets 0.33–1.00.
  - **Without USDJPY:** SPA 0.59, walk-forward −0.16, NO EDGE.
- **Most variants lose:** 43 of 48 are negative in validation, and none survives Romano–Wolf.
- **The best variant is the USDJPY London-afternoon breakout:**
  - rule: the range is 07:00–13:00 London; stop entries at its edges from 13:00 to 16:00; stop-loss at the other edge; exit at 16:00;
  - discovery Sharpe 0.22 → validation 0.97; DSR 0.24;
  - +1.7 bps per trade over about 218 trades a year.
- **It is a US-data breakout:**
  - 17.5% of its entries fall within ±2 minutes of 08:30 or 10:00 NY.
  - Without those entries (FTMO Standard's news blackout), its 2014–26 Sharpe falls from 0.75 to 0.43.
- **Slippage-sensitive:** validation Sharpe 1.09 → 0.78 with +0.5 bps per trade → 0.47 with +1.0 bps.
- **Gross,** the London-afternoon breakout is positive in both periods (discovery / validation, bps per trade):
  - USDJPY +1.4 / +2.7;
  - GBPUSD +2.3 / +1.6;
  - gold +1.2 / +2.7.

  Retail costs take most of it. **A lead for raw-spread accounts that allow news trading, not a build.**

### 21.4 Prop lifecycle of the SQX builds (A25, [results/round11_prop.json](results/round11_prop.json), [results/round11_books.json](results/round11_books.json))

**How the books were built:**
- Daily P&L with exact intraday paths from the minute data, 2014-01 → 2026-08.
- Each book is scaled to 1% daily volatility at 1× on its 2014–16 data.
- Books are bootstrapped against their zero-edge twins with the published-terms presets.
- The EA daily guard is 3% on FTMO 2-Step and 2% elsewhere.

| Book | Sharpe | Return / vol at 1× | Worst day at 1× (intraday low) | Years positive | Notional ÷ equity at 1× (p99) |
|---|---|---|---|---|---|
| **B8** REV build (c), US500 + US100 + JP225, 108 variants each, weekend holds | 0.82 | 14.6% / 17.8% | −17.8% on 2020-03-12 (−19.7%) | 12 of 13 | 2.5 |
| **B8w** the same, no weekend holds | 0.79 | 14.8% / 18.8% | −22.7% on 2020-03-12 (−25.0%) | 10 of 13 | 3.0 |
| **B9** native N3, 12 variants, US100, news blackout | 0.65 | 13.2% / 20.2% | −12.7% on 2020-03-13 | 8 of 13 | 2.1 |
| B10 = B8w + B9 | 0.97 | 19.7% / 20.3% | −23.5% | — | 3.7 |
| B11 family R's best (USDJPY breakout) | 0.75 | 12.0% / 16.0% | −3.8% | 10 of 13 | 3.9 |
| B11n the same, news blackout | 0.43 | 6.9% / 16.1% | −4.0% | 8 of 13 | 4.1 |

B8 and B9 correlate 0.06.

In the lifecycle table, the "recommended" column applies the A16 rule: the highest EV per account-month among policies with positive edge value. Pass rates are shown with the zero-edge twin in brackets.

| Book → account | Recommended | Pass | EV per attempt | Per account-month | Fixed 1×: pass, per month | CPPI k = 10: pass |
|---|---|---|---|---|---|---|
| B8 → FTMO 2-Step Swing | fixed 3× | 21% (5%) | $818 | $375 | 42% (10%), $342 | 53% (7%) |
| **B8w → FTMO 2-Step Standard** | fixed 3× | 18% (5%) | $740 | $337 | **35% (7%), $254** | **49% (6%)** |
| B8w → FTMO 1-Step | fixed 3× | 21% (6%) | $452 | $229 | 26% (7%), $158 | 50% (7%) |
| **B9 → FTMO 2-Step Standard** | fixed 3× | 33% (20%) | $3,302 | **$1,927** | **57% (31%), $660** | 65% (21%) |
| **B9 → FTMO 1-Step** | fixed 3× | 35% (23%) | $2,164 | **$1,678** | 56% (34%), $824 | **72% (29%)** |
| B9 → Topstep 50K | fixed 2× | 21% (12%) | $194 | $261 | 31% (20%), $126 | 60% (19%), negative EV |
| B10 → FTMO 2-Step Standard | fixed 1× | 37% (7%) | $2,874 | $382 | 37% (7%), $382 | 55% (7%) |
| B10 → FTMO 1-Step | fixed 0.5× | 55% (13%) | $3,363 | $234 | 28% (7%), $204 | 56% (8%) |
| B11n → FTMO 2-Step Standard | fixed 3× | 30% (23%) | $2,412 | $1,269 | 42% (26%), $286 | 53% (26%) |
| B11n → FTMO 1-Step | fixed 3× | 33% (25%) | $1,751 | $1,256 | 45% (34%), $448 | 61% (32%) |

**Reading:**

- **The reversal build is less comfortable in a prop account than round 9's post hoc estimate.**
  - FTMO 2-Step Swing at 1×: 42% pass, against 70% for round 9's four-US-index ensemble; $342 per account-month, against $452.
  - First reason: the raw Sharpe on CFD data at 15:55 is 0.82, not 0.9–1.0.
  - Second reason: **its signals cluster in crashes.** Scaled on calm 2014–16 data, the book lost 18% at 1× on 2020-03-12. Other bad days: 2015-08-25, 2024-08-05 (the Nikkei crash) and 2025-04-07.
  - The simulator's EA guard truncates such days. A gap through the guard (Monday opens, overnight) would not be truncated.
  - **Size it as a pass-first book:** CPPI (49–53% pass against 6–7% for zero edge), or 0.5–1× fixed with a hard cap on gross notional. The 3× "recommended" row only wins on EV per month by failing fast.
- **The native US100 book (B9) is the stronger prop book:**
  - FTMO 2-Step Standard: 57% pass at 1× (zero edge 31%), $660–1,927 per account-month depending on size.
  - FTMO 1-Step: 56% pass at 1×; 72% with CPPI.
  - Its zero-edge twin is strongly positive (the funded-account option, §18), so the edge is only the $1.6–5.3k per attempt above the twin.
  - B9 is lumpy by year: 2020 −25% at 1×, 2022 +59%.
- **Keep the two books in separate accounts.** One account holding both (B10) earns less per month than B9 alone at every size: REV's crash days dominate. §19.3 found the same fragility.
- **Family R's book barely beats its zero-edge twin** once the news blackout applies: 30% vs 23% pass.
- **Topstep** fits only the intraday book, and pays little ($261 per account-month at best), as in §17.5.
- **Planning case:** half the in-sample edge, as in §18. Everything here is in-sample for 2014–26.

### 21.5 The SQX build matrix

The full spec, with SQX settings and the checks to run first, is in
[../../evidence/edges/SQX_build_matrix.md](../../evidence/edges/SQX_build_matrix.md). In short:

| Edge | Chart and data | Entry | Exit | Prop account |
|---|---|---|---|---|
| **REV ensemble** (US500, US100, JP225; 141 variants positive under every build) | M5 main chart with a D1 chart on a cash-session definition (Data Manager → Sessions). **Fallback for the US only:** broker D1 bars with next-open orders | Market at 15:55 NY (JP225 at 14:55 / 15:25 JST) when the D1 condition holds (IBS < 0.10, RSI(2) < 5–20, 2–5 lower closes, 5/10-day low; no filter or below SMA(200)) | 15:55 on the first up close (max 5 sessions) or the next session. No entry on Fridays and exit at Friday's 15:55 for Standard accounts | FTMO 2-Step Standard or Swing. CPPI or ≤ 1× with a notional cap |
| **US100 momentum, native** (R3) | M1/M5, US100 cash session | At 09:30, buy stop at open + 0.5 × prior range, sell stop at open − 0.5 × prior range (OCO) | Exit at end of day, 15:59 NY; max 1 trade per day (or stop-and-reverse) | FTMO 2-Step Standard or 1-Step, fixed 1–3×; Topstep only at small size |
| MR-06 (member of REV) | As REV | 15:55 after 3 lower closes | Next session's 15:55 | As REV |
| *Lead only:* USDJPY London-afternoon breakout | M1, London time | Stop orders at the 07:00–13:00 London range, 13:00–16:00 | Other edge (stop-loss) or 16:00 London | Paper only. Needs news trading (FTMO Swing) and raw spreads |

### 21.6 What round 11 changes

- **The core edge is buildable in SQX:**
  - Build (c) first.
  - Build (a) is acceptable for US-only portfolios.
  - Avoid (b) for JP225.
- **FTMO Standard works for the ensemble:** the no-weekend rule costs no Sharpe.
- **N3 no longer needs a custom indicator:** native bands keep 89% of its Sharpe (grid median); open ± 0.5 × prior range is the best of them.
- **FX and metals:**
  - Four more families (292 variants) found no tradeable edge after costs.
  - That adds to the earlier FX work: fix windows, month-end hedging, carry, momentum, reversal, and the 653-candidate scan.
  - The only FX/metals lead is the London-afternoon (US-data) breakout on USDJPY, GBPUSD and gold. It is positive gross in both periods, but fragile to costs and news rules.
- **Prop sizing:** size the reversal ensemble for survival (CPPI or ≤ 1× with a notional cap). Use the native US100 book for speed. Keep separate accounts.

## 22. Rounds 12–17 — edge research (amendments A26–A31, [run_round12.py](run_round12.py))

Round 12 was research only. Each family came from a published mechanism, and each rule had to be buildable
in SQX from bar data.
- **Verdicts:** the A22 battery.
- **DSR count:** 7,895 trials in total.
- **Library:** the round-12 variants were added to [../strategy_library.csv](../strategy_library.csv).

| Family (source) | Variants | SPA p (validation) | PBO | Walk-forward | Verdict and reading |
|---|---|---|---|---|---|
| **S.** Short side of index reversal: family A mirrored; sell after strength (Baltussen, van Bekkum & Da 2019) | 864 | 0.58 timing (0.71 raw) | 0.33 | Sharpe 0.16 (t 0.6) | **WEAK.** US variants have slightly positive timing value (medians 0.05–0.12), but raw P&L is negative (medians −0.16 to −0.42). No per-market SPA below 0.14. **The reversal edge is one-sided:** buying weakness pays, shorting strength doesn't, as Boyarchenko et al. (2023) report for dealer-inventory reversals |
| **T.** Where the reversal return is earned: family A's signals at 15:55 with three one-day exits (Boyarchenko, Larsen & Whelan 2023) | 432 | E1 0.06, E2 0.006, **E3 0.04** | 0.48 / 0.22 / 0.44 | E1 −1.21, E2 −0.16, **E3 +0.58** | See below |
| **U.** US macro-release shocks at 08:30, 10:00 and 14:00 NY, follow or fade (Evans & Lyons 2008; Andersen et al. 2003) | 324 | 0.74 | 0.50 | Sharpe −0.43 | **NO EDGE.** Following the 08:30 shock loses in 91% of variants after costs. Prices adjust within minutes, as Andersen et al. and Chordia et al. (2018) found |
| **V.** Precious-metals auction windows: LBMA gold 10:30/15:00, silver 12:00, COMEX opens (Caminschi & Heaney 2014) | 30 | 1.00 | 0.04 | Sharpe −2.37 | **NO EDGE.** Gross effects after 2016 are at most 1.3 bps against 2.5–5 bps costs. The old fixing leak ended with the electronic auctions |
| **W.** FX weekend-gap reversal, fade or follow the Friday → Sunday gap (Dao, McGroarty & Urquhart 2016) | 192 | 0.98 | 0.45 | Sharpe 0.10 | **WEAK.** After publication (2015 →), fading the gap to Friday has a median Sharpe of 0.04, and to Monday 08:00 London −0.22. The paper measured the Monday open at 22:00 GMT, inside the rollover spread widening; the clean price at 19:00 NY shows no reversal |

**Family T: the anatomy of the one real edge.** The build is R1 (c), US500, US100 and JP225 with a GER40 control;
discovery runs 2014–19 and validation 2020 → 2026-08. The three exits are:
- **E1:** the next 03:00 NY, after the first European hour;
- **E2:** the next cash open;
- **E3:** the next 15:55.

| Exit | Ensemble Sharpe, timing (raw) | 2014–19 | 2020–26 | Per-market SPA p (timing): US500 / US100 / JP225 |
|---|---|---|---|---|
| E1, to 03:00 NY | −0.29 (−0.15) | −0.35 | −0.26 | 0.033 / 0.019 / 0.94 |
| E2, to the next cash open | 0.23 (0.39) | −0.29 | 0.57 | 0.011 / 0.18 / **0.002** |
| **E3, to the next 15:55** | **0.69 (0.88)** | 0.35 | **0.95** | 0.044 / 0.054 / 0.009 |

**T2, the Sharpe differences** (timing value; 95% bootstrap interval):
- E1 − E3 = −0.99 [−1.51, −0.50];
- E2 − E3 = −0.46 [−0.79, −0.11].

The full-session hold is significantly better. The raw results agree.

**T3, the Boyarchenko mechanism after publication.** US500 and US100, return in bps; the last column is after a down close minus after an up close, with its t:

| Market, period | 02:00–03:00 NY, all days | 02:00–03:00, down − up | 16:00 → 09:30, down − up |
|---|---|---|---|
| US500, 2014–20 | +1.6 (t 3.6) | +0.7 (t 1.0) | −0.9 (t −0.3) |
| US500, 2021–26 | +0.2 (t 0.5) | +0.1 (t 0.1) | +2.6 (t 0.8) |
| US100, 2014–20 | +1.7 (t 3.6) | −0.4 (t −0.5) | −3.0 (t −0.9) |
| US100, 2021–26 | +0.5 (t 1.2) | +0.6 (t 0.5) | +3.9 (t 0.8) |

**Reading:**
- **The reversal edge needs the next session, not just the night.**
  - Exiting at the European open (E1) gives it all back.
  - Exiting at the cash open (E2) keeps a third.
  - Holding to the next 15:55 is the edge. The same holds for the round-1 finding that about half of MR-06's return comes during the next session.
- **JP225 is the exception:** its reversal is earned overnight (E2 per-market SPA 0.002, with 86% of variants positive). The night after the Tokyo close is the US session. This matches R1, where JP225 needed the pre-close entry.
- **The European-open drift is gone on our data too:**
  - It was +1.6–1.7 bps an hour in 2014–20 and is ≈ 0 since 2021, as the NY Fed reports.
  - The after-sell-off difference is not visible in either period with this simple conditioning. Boyarchenko et al. condition on closing order imbalances, which bar data can't reproduce.
- **REV is a different effect from the overnight drift.** It stayed strong after 2021 (E3 Sharpe 0.95) while the drift died. The liquidity-provision reading (Nagel 2012; Baltussen et al. 2019) is intact. The dealer-inventory channel at the European open is not the carrier.
- **For the build:**
  - US legs: hold to the next session's pre-close.
  - JP225 legs: exiting at the next Tokyo open is a valid, shorter hold. The exit grid was pre-registered here, but choosing it for JP225 is post hoc.

**Round 12's answer:** no new edge in five mechanism-led families (1,842 variants). Adding rounds 1–11, the search space
of published, SQX-buildable rules on FX, indices and metals is now mostly covered:
- **Indices:** reversal (long side only), intraday momentum (US100), trend, calendar, flows, gaps, breakouts, news, overnight drift.
- **FX:** carry, momentum, reversal, sessions, fixes, month-end, weekend gaps, news shocks, night reversion, breakouts.
- **Metals:** reversal, trend, sessions, fixes, breakouts.

The edge set is still the long-side index reversal, plus US100 intraday momentum.

### 22.1 Rounds 13–15 (amendments A27–A29; [run_round13.py](run_round13.py), [run_round14.py](run_round14.py), [run_round15.py](run_round15.py))

Three more rounds went after the remaining gaps:
- reversal on FX crosses (only USD majors had been tested);
- VIX-based "buy fear" entries;
- futures positioning (CFTC COT, a new information source);
- whether the index rebound also shows up in FX and gold.

**DSR count:** 13,013.

| Family (source) | Variants | SPA p (validation) | PBO | Walk-forward | Verdict and reading |
|---|---|---|---|---|---|
| **Y.** Reversal on 21 FX crosses, long and short; family E's grid plus a Bollinger(20, 2) → middle-band rule; daily bars 19:00 → 16:45 NY | 4,662 | 0.12 timing (0.47 raw) | 0.38 | Sharpe 0.17 (t 0.5) | **WEAK.** AUDNZD, the textbook mean-reversion cross, has 22% of variants positive (median −0.29). EURCHF's per-market p = 0.005 comes from isolated variants (median −0.08). Crosses don't reverse at the daily horizon net of 2–3 bps |
| **Z.** VIX-regime entries on SPY/QQQ/DIA/IWM: VIX/VIX3M backwardation, VIX spikes, VIX above its SMA(20), variance risk premium (Fassas & Hourvouliades 2019; Bollerslev, Tauchen & Zhou 2009) | 108 | 0.56 timing (0.03 raw) | 0.53 | 0.06 timing | **WEAK, and not new.** Its raw significance is equity drift plus the reversal edge. In validation its ensemble correlates 0.73 with family A (β 1.9, t 6.1) with alpha −1.5 bps/day (t −1.8) |
| **ZM.** Noise-area momentum by VIX regime | 4 tests | — | — | — | **Not confirmed.** US100 high-VIX regime: +3.7 bps/day (t 1.84, Holm p 0.065) against +0.9 in low; US500 +1.0 (t 0.5). Momentum is stronger in volatile markets on US100, as Gao et al. and Zarattini et al. report, but not significant after Holm |
| **CT.** COT positioning: speculators' and hedgers' net positions scaled to Wang's 3-year sentiment index; with or against extremes; 7 FX, gold, silver, S&P and Nasdaq futures (Wang 2001; Tornell & Yuan 2012) | 264 | 0.86 | 0.29 | Sharpe 0.12 | **WEAK.** No market has a median-positive variant after 2014. Weekly positioning extremes, public three days later, carry no tradeable information today |
| **XR.** Family A's signals on the S&P 500 close, traded through risk FX (AUDJPY, NZDJPY, CADJPY, EURJPY, USDJPY, AUDUSD, NZDUSD, long USDCHF) and gold, long or short | 80 | 0.45 | 0.68 | Sharpe −0.30 | **NO EDGE.** Risk currencies don't share the index rebound: 12% of JPY-cross variants are positive. Long USDCHF is the closest (median 0.28, p 0.075). **This supports the index-product liquidity reading of REV** |

**Round 15: the reversal edge by volatility regime (A29, decision analysis).** The regime is set at the signal close: STRESS
when VIX/VIX3M ≥ 1 (11% of days, 2007–26). Family A's variants, 2007-07 → 2026-08.

| | US (SPY, QQQ, DIA, IWM) | ^N225 (**withdrawn:** look-ahead, see §22.2) |
|---|---|---|
| Timing value per trade, STRESS entries | **+56.1 bps** (29,725 variant-trades) | −29.0 bps (6,524) |
| Timing value per trade, CALM entries | +4.8 bps (96,270) | **+16.5 bps** (27,018) |
| Ensemble Sharpe, all trades → CALM only | 0.54 → **0.27**; difference −0.27 [−0.57, +0.03] | 0.20 → **0.51**; difference +0.31 [+0.04, +0.65] |
| Worst day, all → CALM only | −2.85% → −1.75% | −5.19% → −5.19% |
| Max drawdown, all → CALM only | −7.0% → −5.3% | −12.3% → −7.4% |
| A29 rule (Sharpe interval reaches 0, and the worst day improves) | "Recommend" by the letter, but the point estimate halves the Sharpe | Not met (the worst day is unchanged) |

Per-trade t statistics pool overlapping variants, so they are descriptive.

**Reading round 15:**

- **The US reversal edge is mostly a stress-regime liquidity premium,** as Nagel (2012) predicts. Entries made when the VIX curve is inverted earn about 12× the calm-regime timing value.
- **The crash tail is the price of the edge,** not a removable flaw. A calm-only filter halves the Sharpe to cut the worst day by 38%.
  - For prop books, size the whole ensemble down (§21.4) rather than filter out stress.
  - The A29 letter-rule "recommendation" is noted, but the economics argue against it.
- ~~JP225 behaves the other way…~~ **Withdrawn in round 16 (§22.2):** the JP225 split used the same calendar day's VIX close, published after the Tokyo close. With the previous US close, JP225 shows no regime effect.

**Rounds 12–15 in one line:** ten more families (≈ 7,000 variants) found no new edge on FX, metals or European
indices. They sharpened the one real edge:
- long-only;
- hold through the next session;
- paid in stress on US indices;
- specific to index products, not a broad risk-on rebound.

### 22.2 Round 16: a VIX-free regime for FTMO, and a look-ahead correction (A30, [run_round16.py](run_round16.py))

**Why this round:**
- **FTMO's server has no VIX symbol,** so an EA can't read it.
- **A bug was found while preparing this:** round 15's ^N225 split took the regime from the *same calendar day's* VIX close. That close is published about 15 hours after the Tokyo close.

Round 16 re-ran the split with only information known at the signal close. It also tested four regime proxies built from US500 daily bars, which FTMO offers. Each proxy's threshold was matched to the VIX regime's 2007–16 stress frequency (14%).

| Proxy (US500 daily bars) | Threshold | Correlation with the VIX regime, 2007–16 / 2017–26 | Agreement, 2017–26 |
|---|---|---|---|
| **DD:** close vs its 60-day high (primary, per the pre-registered rule) | ≥ 9.0% below | **0.51 / 0.42** | 91% |
| RVL: 20-day realized volatility | ≥ 26.6% a year | 0.37 / 0.26 | 89% |
| ATRR: ATR(5) ÷ ATR(50) | ≥ 1.33 | 0.36 / 0.35 | 85% |
| RVR: std(5) ÷ std(60) of returns | ≥ 1.42 | 0.30 / 0.33 | 86% |

**Timing value per trade, stress / calm entries** (family A's variants, 2007-07 → 2026-08):

| Regime | US: stress / calm | US calm-only Sharpe (all 0.54) | JP225: stress / calm | JP225 calm-only Sharpe (all 0.20) |
|---|---|---|---|---|
| VIX ≥ VIX3M (**JP225 lagged one US close**) | +56 / +5 bps | 0.27 | **+12 / +7 bps** | **0.20** (difference 0.00 [−0.26, +0.30]) |
| **DD ≥ 9%** | **+71 / +4 bps** | 0.20 (difference −0.34 [−0.59, −0.06]) | +36 / +3 bps | 0.07 |
| RVL ≥ 26.6% | +67 / +10 bps | 0.40 | +35 / +4 bps | 0.12 |
| ATRR ≥ 1.33 | +34 / +12 bps | 0.43 | −30 / +18 bps | 0.55 ([+0.04, +0.67]) |
| RVR ≥ 1.42 | +12 / +18 bps | 0.59 | −28 / +16 bps | 0.46 ([+0.02, +0.50]) |

**Reading:**

- **Round 15's JP225 finding was a look-ahead artefact.**
  - With the VIX close JP225 could actually see, stress entries don't lose (+12 bps) and the filter gains nothing (0.20 → 0.20).
  - The pre-registered decision rule is not met. **No JP225 filter, and no VIX needed.**
- **The US finding holds, and it is visible without VIX.**
  - When US500 is ≥ 9% below its 60-day high (about 9–14% of days), US reversal trades earn +71 bps of timing value against +4 in calm markets. Removing them cuts the Sharpe from 0.54 to 0.20, a significant loss.
  - The same holds with realized volatility (RVL).
  - **The edge lives in sell-offs.** A prop build should keep full size, within its risk cap, in exactly the regimes where drawdowns are deepest. That is why sizing, not filtering, is the control (§21.4).
- **A post hoc lead, not a recommendation.** Short-term volatility *expansion* on US500 (ATR(5)/ATR(50) ≥ 1.33, the previous US close) separates losing JP225 entries: calm-only Sharpe 0.20 → 0.55, interval [+0.04, +0.67]. RVR agrees. Neither was the pre-registered primary proxy, so this needs a fresh test before any build uses it. In SQX it would be native: ATR on US500.cash D1 as a second symbol.

### 22.3 Round 17: reversal breadth, FX/gold intraday momentum, late-day index momentum (A31, [run_round17.py](run_round17.py))

| Family (source) | Variants | SPA p (validation) | PBO | Walk-forward | Verdict and reading |
|---|---|---|---|---|---|
| **RB.** The index-reversal edge with 12 new SQX-native entry signals on US500, US100, **US30, US2000** and JP225. Signals: Stochastic %K(14) < 10/20, Williams %R(5) < −95, Bollinger %B < 0, Keltner (EMA20 − 2 ATR), Connors RSI < 10/15, 3 lower lows, ATR pullback below SMA(5), cumulative RSI(2) < 35, 5-day return in the bottom decile, wide-range weak close. Exits: next close, first up close, close above SMA(5) | 540 | **0.031** timing (0.001 raw) | 0.25 | **Sharpe 0.53 (t 2.7)** timing; 0.74 (t 3.3) raw | **EDGE FAMILY.** 3 Romano–Wolf survivors on timing value, 17 on raw |
| **FM.** FX and gold intraday momentum: the first half hour or the day so far predicting the last half hour, for London and NY sessions (Elaut, Frömmel & Lampaert 2018; Gao et al. 2018); noise-area bands from the London open; 7 majors + gold | 80 | 0.50 | 0.01 | Sharpe 0.35 (t 1.1) | **WEAK.** Session momentum loses after 1 bp costs in every pair (median Sharpe −1.8 to −3.8). The one consistent pocket is **USDJPY noise-area momentum**: 6 of 6 variants positive in both 2010–16 and 2017–26 (validation Sharpe 0.15–0.48, +0.3 to +0.9 bps/day, per-market p 0.13). It matches round 11's USDJPY afternoon breakout. **A lead** |
| **IM2.** Late-day momentum on US500/US100: the first half hour or the day so far predicting the last half hour, all days or strong signals only (Gao et al.; Baltussen et al. 2021; Rosa 2022) | 8 | 1.00 | 0.14 | Sharpe −0.63 | **NO EDGE.** Hit rates 43–46%: gross, the last half hour leans toward *reversal* in 2014–26, and neither direction clears costs |

**RB in detail:**
- **Breadth:** 100% of the SPY and QQQ variants have positive timing value in 2013–26; DIA (US30) 90%, IWM (US2000) 78%, ^N225 94%. Per-market SPA (raw): QQQ 0.001, SPY 0.0005, IWM 0.028, ^N225 0.038, DIA 0.057.
- **Library:** 189 variants are Tier 1/2 in [../strategy_library.csv](../strategy_library.csv): 75 US100, 61 US500, 25 US30, 17 US2000, 11 JP225.
- **Same edge as family A:** the two validation ensembles correlate 0.93. RB widens the building blocks, not the independent bets.
- **Best choices** (median US timing Sharpe):
  - signals: cumulative RSI(2) < 35 (0.36), Stochastic %K(14) < 10 (0.32), Bollinger %B < 0 (0.31), ATR pullback (0.31);
  - exit: the first up close (0.34);
  - filter: none (0.31).
- **The SMA(200) filters differ here:** the "above SMA(200)" filter is not harmful with these signals (0.30), unlike family A's (0.19). Two of the three Romano–Wolf survivors use it (SPY Stochastic %K < 20 and SPY Bollinger %B < 0, both with the first-up-close exit).
- **Frequency:** median trades per year about 7 per variant (family A: 11–23), so more variants are needed for the same activity.
- **Caveat:** RB was measured on daily closes (entry at the close), not re-run in the R1 M5/15:55 build. Family A's R1 result (82–87% kept) is the guide. *Round 18 (§22.4) ran that build.*

### 22.4 Round 18: the USDJPY lead on unseen data, volatility-scaled sizing, RB in the SQX build (A32, [run_round18.py](run_round18.py))

**JY: the USDJPY intraday-momentum lead, confirmation on data not used before** ([results/round18_jy.json](results/round18_jy.json)). The rules are round 11's and round 17's, unchanged.

| | Rule and data | n | Mean, bps (net) | HAC t | Holm p |
|---|---|---|---|---|---|
| H1 | USDJPY London-morning breakout to window end, 2003–09 | 1,495 | −0.17 | −0.22 | 1.00 |
| H2 | USDJPY noise area L14 b1.25, 2003–09 | 1,361 | +1.00 | 0.86 | 0.78 |
| H3 | The breakout on six JPY crosses (average), 2008–26 | 4,787 | −2.56 | −7.76 | 1.00 |
| H4 | The noise area on six JPY crosses (average), 2008–26 | 4,822 | −1.28 | −2.93 | 1.00 |

**Verdict: NOT CONFIRMED.**
- **Grids:** USDJPY 2003–09 has SPA 0.71 over the 14 rules (6 of 14 positive); the crosses have SPA 1.00, with none of the 14 positive after 2 bps.
- **Crosses:** every cross loses under both rules after costs. The breakout's gross mean averages −0.6 bps across the six crosses (it trades once a day, so gross = net + 2).
- **By year:** the USDJPY breakout ranges from −4.6 bps (2008) to +4.6 (2009), with no sign that holds.
- **Reading:** the USDJPY pocket was a feature of one pair after 2010. **The lead is closed.** FX intraday momentum has now failed in rounds 11, 17 and 18.

**VS: volatility-scaled reversal book** ([results/round18_vs.json](results/round18_vs.json)).
- **Book:** family A + RB, US ETFs, Yahoo daily 2007-07 → 2026-08. Both versions are scaled to 1% daily volatility on 2007–12.
- **Lifecycle:** FTMO 2-Step 100k, close-only path, 3% guard.

| Book | Sharpe | Return / vol, %/yr | Worst day | Max DD | FTMO 2-Step at 1×: pass (zero edge) | Edge value per attempt | EV per account-month |
|---|---|---|---|---|---|---|---|
| Fixed size | 0.71 | 9.3 / 13.0 | **−9.9%** | −25.2% | **87% (41%)** | $7,190 | $366 |
| Volatility-scaled (min(2, 1% ÷ σ20)) | 0.73 | 11.6 / 15.9 | −13.9% | −27.6% | 83% (47%) | $8,100 | $559 |

- **Decision (pre-registered rule): keep fixed size.** Vol-scaling doesn't improve the worst day (−13.9% vs −9.9%) or the zero-edge-adjusted pass rate (+37 vs +46 points).
- **Why:** it raises size in calm markets (up to 2×), so a shock after a calm spell costs more. It earns faster per account-month because the book runs at higher average risk, not because the edge is better (Sharpe 0.73 vs 0.71).
- **Not comparable with §21.4:** these pass rates are for a diversified daily book on ETFs, at a larger size than §21.4's CFD book.

**RBc: the 12 RB signals in the SQX M5/15:55 build** ([results/round18_rbc.json](results/round18_rbc.json)).
- **Scope:** 108 variants per market, HistData CFD quotes, 2014 → 2026-08.
- **Approximation:** the signal history uses each day's 15:55 snapshot as that day's bar.

| Market | Share of variants positive | Ensemble timing Sharpe: SQX build / daily close | Kept | SPA p (build) |
|---|---|---|---|---|
| US500 | 95% | 0.37 / 0.52 | 72% | 0.127 |
| US100 | 100% | 0.63 / 0.64 | 98% | **0.024** |
| JP225 | 88% | 0.30 / 0.28 | 107% | 0.247 |

- **Reading:** RB survives the build as family A did, US100 fully and JP225 fully.
- **US500** keeps 72%, below the 80–90% expected. Prefer US100 and the family A signals when building US500 legs.

**DSR count:** 13,669 (A32).

### 22.5 Round 19: the Tokyo fix on Gotobi days, and central-bank-day currency premia (A33, [run_round19.py](run_round19.py))

**GT: the Tokyo fix on Gotobi days** (Ito & Yamada 2017; [results/round19_gt.json](results/round19_gt.json); card: [GT](../../evidence/edges/GT_tokyo_fix_gotobi.md)).
- **Mechanism:** importers buy dollars at banks' 09:55 JST fixing on the 5th/10th/…/30th and at month-end. Banks buy ahead of the fix, so USD/JPY rises into 09:55 and gives it back after.
- **Scope:** tested on USDJPY after the paper's sample (2014-01 → 2026-09-18), at 1 bp per trade.

| | Rule (USDJPY, Gotobi days, 2014–26) | n | Net, bps | HAC t | Holm p | 2014–19 / 2020–26 net | Gross, bps (t) |
|---|---|---|---|---|---|---|---|
| **G3** | **Short 09:55 → 10:55 JST** | 963 | **+1.10** | **2.59** | **0.010** | +0.49 / +1.64 | +2.10 (5.0) |
| G1 | Long 09:00 → 09:55 JST | 963 | +0.61 | 1.36 | 0.087 | +0.95 / +0.30 | +1.61 (3.6) |
| G2 | Mechanism: pre-fix, Gotobi minus other days (gross) | 963 / 2,139 | +1.04 | 2.05 (Welch) | — | — | — |

**Verdict: EDGE** (G3 passes Holm and is positive in both halves).
- **Grid:** the 42-variant grid is an **EDGE FAMILY**: SPA 0.027, PBO 0.05, walk-forward top-5 Sharpe 1.06 (t 2.85). Romano–Wolf survivors are USDJPY post-fix on all Gotobi days and three EURJPY month-end post-fix variants.
- **Replication in the paper's period** (2003–13): post-fix +3.00 bps gross (t 4.9), pre-fix +1.78 (t 3.6).
- **Other days:** the fix pattern is there too (pre-fix +0.57, post-fix +0.98 gross), about a third to a half of the Gotobi size and below costs.

**Post hoc checks** ([gt_robustness.py](gt_robustness.py), [gt_breadth.py](gt_breadth.py); they don't change the verdict):
- **Breadth:** every JPY pair has it. The post-fix hour on Gotobi days is +1.3 to +2.2 bps gross (t 2.1–5.8) on EURJPY, GBPJPY, AUDJPY, CADJPY, CHFJPY and NZDJPY.
- **Placebo:** it is absent from non-JPY pairs (EURUSD +0.01, GBPUSD +0.22, USDCHF +0.15, USDCAD −0.26, AUDUSD +0.78; all n.s.).
- **Second feed:** Yahoo USDJPY=X agrees. 5-min bars correlate 0.9994 with HistData over the window; 60-min bars 0.9994 over 720 days, with the same Gotobi mean (0.80 vs 0.78 bps on 10:00–11:00).
- **Stability:** 22 of 24 years are positive. Trimming 1% tails leaves +2.11 bps; the median trade is +1.77.
- **The fix minute matters:** entering at 09:56 leaves +1.31 bps gross, and 10:00 leaves +0.73. Later exits earn more: 11:30 +2.86 (t 5.8), 15:00 +3.33 (t 3.5). Month-end days: +3.71.
- **Costs decide it:** net +1.61 at 0.5 bp, +1.11 at 1 bp, +0.61 at 1.5 bps, +0.11 at 2 bps.

**As a prop book** (post hoc, [gt_prop.py](gt_prop.py), [results/round19_gt_prop.json](results/round19_gt_prop.json)).
- **Book:** USDJPY 2014–26, ~76 trades a year, per-trade σ 12 bps, annual Sharpe 0.83. Correlation with REV 0.02, with US100 momentum −0.04.

| Notional ÷ equity | FTMO 2-Step: pass (zero edge) | EV per account-month | Median days to pass | FTMO 1-Step: pass (zero edge) | EV per account-month |
|---|---|---|---|---|---|
| 10× | 67% (26%) | $297 | 387 | 63% (29%) | $384 |
| 20× | 50% (24%) | $779 | 143 | 50% (27%) | $913 |
| 30× | 40% (20%) | $1,159 | 85 | 44% (24%) | $1,179 |

- **Crosses:** the equal-weight basket of all seven JPY pairs nets −0.02 bps at 2 bps per cross, so only USDJPY (and any cross at ≤ 1 bp) pays.
- **Account:** GT belongs in its own account. Added to REV + US100 at 1× each, it didn't raise the pass rate, because that book is already too large for one account.

**FD: FOMC- and BoJ-day currency premia** (Mueller, Tahbaz-Salehi & Vedolin 2017; [results/round19_fd.json](results/round19_fd.json)).

| | Portfolio, announcement days 2014–26 | n | Net mean, bps | t | Holm p | Event minus other days |
|---|---|---|---|---|---|---|
| F1 | DOL: long 7 currencies vs USD, FOMC days | 96 | +4.7 | 0.76 | 0.67 | +6.3 (t 1.0) |
| F2 | HY: the 3 highest-rate currencies vs USD, FOMC days | 96 | +1.9 | 0.27 | 0.79 | +3.9 (t 0.6) |
| F3 | Long 7 currencies vs JPY, BoJ days | 109 | −5.7 | −0.69 | 0.79 | −4.9 (t −0.6) |

**Verdict: NO EDGE** (grid SPA 0.80, walk-forward t 0.26).
- **What remains:** the FOMC-day short-dollar return is positive but small (+4.7 vs 10.8 bps in the paper). With about 100 events, the test had ~20% power at half the published size, so a smaller effect can't be ruled out.
- **Gold** on FOMC days: +12.5 bps (t 1.1).
- **Replication inside the paper's sample** (2005–13): DOL +28.3 bps per FOMC day (t 2.41) and HY +34.7 (t 2.44), mostly before the 14:00 statement. After publication it is +4.7: the premium has **decayed**, like the other announcement effects in round 4.

**DSR count:** 13,722 (A33).

### 22.6 Round 20: the Gotobi effect on unseen data; exit and stop for the build (A34, A34a; [run_round20.py](run_round20.py), [results/round20_gotobi_confirm.json](results/round20_gotobi_confirm.json))

**Unseen data:**
- HistData EURJPY, GBPJPY, AUDJPY and CHFJPY 2002–07, plus CADJPY 2007 and NZDJPY 2006–07, downloaded after A34 was committed.
- Rules exactly as round 19. The basket is the equal-weight average of the crosses with prices that day (≥ 3).

**First run: NOT CONFIRMED, because of a corrupt file** ([results/round20_gotobi_confirm_first_run.json](results/round20_gotobi_confirm_first_run.json)).
- **The file:** HistData's AUDJPY 2005 mixes in other instruments' prices (12,319 one-minute moves beyond ±3%; every other cross-year has 0–4).
- **The effect on the tests:** it put the basket's mean at +266 bps with σ 5,238 bps, so C1 and C2 failed (t ≈ 1.0).
- **Amendment A34a:** an integrity rule that doesn't depend on the effect. It drops symbol-years with > 100 such moves (only AUDJPY 2005) and window returns beyond ±5%. It was committed before the corrected run.

**Corrected run: CONFIRMED.**

| | Test (Gotobi days, 2002–07, unseen) | n | Mean, bps | t | Holm p |
|---|---|---|---|---|---|
| C1 | Basket, short 09:55 → 10:55 JST, gross | 404 | **+2.80** | 4.48 | < 0.0001 |
| C2 | Basket, Gotobi minus other days, gross | 404 / 894 | **+1.93** | 2.76 (Welch) | 0.003 |
| C3 | EURJPY alone, net of 1 bp | 426 | **+1.80** | 3.10 | 0.002 |

- **Per cross** (Gotobi vs other days, gross): EURJPY +2.80 vs +0.86 · GBPJPY +2.51 vs +0.73 · CHFJPY +3.29 vs +1.09 · AUDJPY (2005 dropped) +1.56 vs +0.89 · NZDJPY +3.06 vs +1.16 (n 99) · CADJPY +0.37 (n 60).
- **The pre-fix long** (09:00 → 09:55) is +0.83 bps (t 1.3). It is too small to trade.
- **Reading:** the effect was already in all JPY crosses before 2008, at the same size as in 2014–26. It is a yen-fixing flow, not a feature of one period or pair. **EURJPY may join USDJPY in the build (C3), at a round trip ≤ 1 bp.**

**GX, the exit.** Mean ÷ σ per trade on the unseen basket:

| Exit | 10:25 | **10:55** | 11:30 | 12:00 | 15:00 |
|---|---|---|---|---|---|
| Mean ÷ σ | 0.271 | **0.246** | 0.198 | 0.187 | 0.144 |

- **Decision (pre-registered): keep 10:55.** The post hoc 11:30 exit didn't hold up. The means are flat after 10:25 (+2.5 to +3.0 bps), so later exits add risk, not return.
- **Note:** 10:25 scored best but was not a candidate under the rule.

**GS, the stop** (USDJPY 2014–26):

| Buy stop at entry + | none | **20 bps** | 30 | 50 | 80 |
|---|---|---|---|---|---|
| Net mean, bps | 1.11 | **1.08** | 1.06 | 1.07 | 1.11 |
| Worst trade, bps | −84 | **−21** | −32 | −51 | −80 |
| Trades stopped | 0 | 7.0% | 2.8% | 0.6% | 0.1% |

**Decision (pre-registered): a 20-bps stop.** It keeps 97.5% of the mean and cuts the worst trade fourfold.

**The build as a prop book** (post hoc, [results/round19_gt_prop_stop20.json](results/round19_gt_prop_stop20.json); USDJPY, 20-bps stop, 1 bp):
- **Book:** Sharpe 0.85, ~76 trades a year.

| Notional ÷ equity | Return / vol, %/yr | Worst day | FTMO 2-Step: pass (zero edge) | EV per account-month | Median days to pass | FTMO 1-Step: pass (zero edge) |
|---|---|---|---|---|---|---|
| 10× | 8.5 / 9.8 | −2.1% | **74% (29%)** | $298 | 414 | 63% (31%) |
| 20× | 17.0 / 19.6 | −4.2% | 50% (26%) | $779 | 143 | 50% (28%) |
| 30× | 25.5 / 29.4 | −6.3% | 40% (21%) | $1,159 | 85 | 44% (24%) |
| 40× | 34.1 / 39.3 | −8.4% | 37% (19%) | $1,434 | 58 | 38% (24%) |

- **Adding EURJPY** (half each, 1 bp) gives the same Sharpe (0.85) and similar pass rates; the two share the yen leg.
- **Sizing:** at 20× the worst day stays inside FTMO's 5% daily limit without relying on the guard.

**DSR count:** 13,730 (A34).

### 22.7 Round 21: round-number barriers in FX and gold; the Shanghai Gold Benchmark (A35, A35a; [run_round21.py](run_round21.py))

**First run and data audit:**
- **What went wrong:** the first RN run was contaminated by corrupt bars. One AUDUSD bar on 2004-11-24 has an open and high of 39.82 (the price was 0.79) and produced 7,806 fake level touches in a day. Similar single bars exist in EURJPY and USDCHF 2004 and NZDUSD 2008.
- **The audit** ([data_audit.py](data_audit.py), [results/data_audit_spikes.json](results/data_audit_spikes.json)): a spike bar is more than 1% (FX) or 2% (metals, indices) away from its four neighbours' median close while they agree. It flags 0–16 bars per file across 39 files, plus AUDJPY 2005.
- **Earlier rounds:** no flagged bar falls in the round-19/20 Gotobi windows. The close-based windows of earlier rounds mostly filtered moves beyond ±5%. A35a drops spike bars, and both runs are on file.

**RN: round numbers** ([results/round21_rn.json](results/round21_rn.json); Osler 2003, 2005; Aggarwal & Lucey 2007).
- **Scope:** 7 FX majors 2003–26, gold 2009–26, first touches of 50-pip (FX) or $10 (gold) levels against arbitrary offsets of the same grid.
- **Trades:** take-profit and stop 10 bps; costs 1 bp (FX) and 2.5 bps (gold).

| | Test | Round | Arbitrary | Difference | z / t | Holm p |
|---|---|---|---|---|---|---|
| RN1 | FX: reversal-first frequency at the level | 47.9% | 48.8% | **−0.9 pp** | −9.0 | 1.00 |
| RN2 | Gold: the same | 45.3% | 46.8% | **−1.4 pp** | −5.0 | 1.00 |
| RN3 | FX: fade at round levels, net per day (all pairs) | −30.4 bps | — | — | −45 | 1.00 |
| RN4 | Gold: fade at round levels, net per day | −17.8 bps | — | — | −18 | 1.00 |

**Verdict: NO EDGE** (grid SPA 1.00; every variant negative net).
- **Osler's first prediction has flipped since 1996–98:** rates now reverse *less* often at round numbers than at arbitrary levels.
- **His second prediction holds:** after a crossing, the move runs on more often at round levels, in FX (+0.75 pp, z 5.1) and gold (+3.1 pp, z 8.6), as stop-loss cascades would imply. It is far too small to pay: follow trades lose −1.0 to −1.5 bps net per FX trade and −3.9 bps per gold trade.
- **Costs:** fades lose −1.4 bps per FX trade, roughly the cost. Round numbers aren't an edge for a retail trader in either direction.

**SG: the Shanghai Gold Benchmark** ([results/round21_sg.json](results/round21_sg.json)).
- **Scope:** XAUUSD around the 10:15 and 14:15 Beijing auctions. Post-launch 2016-04-19 → 2026, pre-launch 2009–16 as the control.

| | Test | Mean, bps | t | Holm p |
|---|---|---|---|---|
| SG1 | Long into both auctions (09:15 → 10:15, 13:30 → 14:15), post-launch | +0.62 per day | 1.10 | 0.41 |
| SG2 | Short after both auctions (to 11:15 and 15:15), post-launch | −1.34 per day | −2.79 | 1.00 |
| SG3 | Natural experiment: post-launch minus pre-launch | −1.77 | −1.62 | 1.00 |

**Verdict: NO EDGE.**
- **No fix pattern:** the auction didn't create one. Gold drifts up about 1 bp from 09:15 to 10:15 Beijing time (t 2.3), but it did so before the launch too (+1.06, t 2.5), and it is below the 2.5-bp cost.
- **Silver:** nothing.

**DSR count:** 13,802 (A35).

### 22.8 Round 22: gold and silver seasonality, the Asian bid in gold, and a holiday check of the Tokyo fix (A36; [run_round22.py](run_round22.py))

**GS: the autumn effect in gold** (Baur 2013; [results/round22_gs.json](results/round22_gs.json)).
- **Sample:** 2011–2025, after the paper.
- **Net of costs:** after 2.5 bps and a month of long financing (US 3-month rate + 2%).

| | Test | Result | Holm p |
|---|---|---|---|
| GS1 | Gold in Sep and Nov, net | **−1.61% per month** (t −1.81, n 30) | 1.00 |
| GS2 | Sep/Nov minus the other months, gross | −2.38% (t −2.44) | 1.00 |

**Verdict: NO EDGE.** The effect reversed after publication: September −1.57%, November −0.98% (2009–10 had +5.4% and +7.3%). Silver is the same (Sep −3.5%, Nov −1.0%).

**Other months, post hoc (1 of 12, not corrected):**
- January +3.68% (t 2.97); August +2.84% (t 2.49).
- Silver in January: +3.91% (t 2.08).
- Gold's turn of the month nets +0.26% (t 1.80).
- **These are leads, not evidence.**

**AB: the Asian bid in gold after NY sell-offs** ([results/round22_ab.json](results/round22_ab.json)).

| | Test (2009–26) | Result | Holm p |
|---|---|---|---|
| AB1 | Long gold 09:00 → 15:00 Beijing after an NY-session fall < −1σ, net | −1.43 bps (t −0.74, n 601) | 1.00 |
| AB2 | Asian return after sell-offs minus other days | −1.64 bps (t −0.71) | 1.00 |

**Verdict: NO EDGE** (grid SPA 1.00).
- **No dip-buying:** Asian buyers don't absorb NY sell-offs. After large NY *rises*, the Asian session continues up (+4.1 bps gross, t 2.4), which is momentum, not a bid.
- **The unconditional Asian-session drift** (+2.5 bps gross, t 4.1) has **decayed:** +3.7 (2009–17) to +1.5 (2018–26), below the 2.5-bp cost. Round 11 (family L) saw the same.

**JH: the Tokyo fix on Japanese holidays** (mechanism check of GT; [results/round22_jh.json](results/round22_jh.json)).

| USDJPY, 2003–26 (EURJPY 2008–26) | Holidays (n 310) | Normal non-Gotobi days (n 3,980) | Difference |
|---|---|---|---|
| Pre-fix, long 09:00 → 09:55 | **−2.69 bps** (t −3.5) | +0.93 (t 4.4) | **J2: −3.62 (t −5.5), p < 10⁻⁷** |
| Post-fix, short 09:55 → 10:55 | +1.41 (t 2.1) | +1.05 (t 4.8) | J1: +0.36 (t 0.5): not lower |
| EURJPY pre-fix | −2.13 (t −2.4) | 0.00 | −2.13 (t −2.5) |

**Reading:**
- **Pre-fix leg:** the rise into 09:55 is a fixing-day flow. On holidays it disappears and turns into a fall, as the importer-demand mechanism predicts.
- **Post-fix leg:** the fall after 09:55 happens on holidays too. Part of it is a general Tokyo-morning pattern, not fix flow. The GT rule is unaffected: Gotobi days still add about +1 bp over normal days (§22.5), and the rule was confirmed on unseen data (§22.6).
- **Post hoc lead:** shorting USDJPY 09:00 → 09:55 on Japanese holidays earns +1.7 bps net at 1 bp, about 13 days a year.

**DSR count:** 13,822 (A36).

### 22.9 Round 23: the Japanese-holiday effect on unseen data, and the day after a holiday (A37; [run_round23.py](run_round23.py), [results/round23_jpy_holidays.json](results/round23_jpy_holidays.json))

| | Test | Data | Result | Holm p |
|---|---|---|---|---|
| H1 | Cross basket, long 09:00 → 09:55 JST on Japanese holidays | Unseen crosses 2002–07 | −0.79 bps (t −0.69, n 64) | 0.49 |
| H2 | The same, holidays minus normal days | Unseen crosses 2002–07 | −1.25 bps (t −1.02) | 0.46 |
| D1 | USDJPY post-fix short, day after a holiday minus normal days | USDJPY 2014–26 | +1.74 bps (t 1.45, n 110) | 0.30 |
| D2 | The same on the cross basket | Unseen crosses 2002–07 | 0.00 (t 0.00, n 41) | 0.50 |

**Verdict: both NOT CONFIRMED.**
- **Holiday short:** the holiday-morning fall has the right sign on the 2002–07 crosses but is small (64 holidays). On USDJPY it is large (2014–26: −4.0 bps, t −4.4; 2003–26 net of 1 bp +1.69, t 2.2), but those are the data it was found on. It stays a lead, not a build item.
- **Day after a holiday:** it looks like a Gotobi day on USDJPY 2014–26 (pre-fix +2.82, post-fix +2.65) but not on the crosses. It is a lead.

**DSR count:** 13,826 (A37).

### 22.10 Round 24: the PBoC fix, gold-silver relative value, festival gold (A38; [run_round24.py](run_round24.py))

**PB: the PBoC fix as an information event** ([results/round24_pb.json](results/round24_pb.json)).
- **Rule:** the AUDUSD move over 09:10 → 09:20 Beijing (the 09:15 CNY fix) traded on in sign to 10:15; the 2015-08-11 fixing reform as the natural experiment.

| | Test | Result | Holm p |
|---|---|---|---|
| P1 | AUDUSD net, post-reform fix days | −1.02 bps (t −3.3, n 2,660) | 1.00 |
| P2 | Post-reform minus pre-reform, gross | −0.21 (t −0.4) | 1.00 |
| P3 | Fix days minus China-holiday placebo, gross | +1.87 (t 1.6) | 0.17 |

**Verdict: NO EDGE.** The fix reaction doesn't continue: gross ≈ 0, and the reform changed nothing (AUD's 09:10–09:20 move is no larger after it: 4.5 vs 5.3 bps average absolute). The 12-variant grid (AUD, NZD, JPY) has SPA 1.00 with every validation Sharpe negative.

**RV: gold-silver relative value** ([results/round24_rv.json](results/round24_rv.json)).
- **Rule:** z of log(XAU/XAG) over L days; long the cheap leg at |z| > k; exit at |z| < 0.5 or 20 days; 15 bps per spread round trip plus financing.

| | Test (L 60, k 2.0, 85 trades 2010–26) | Result | Holm p |
|---|---|---|---|
| RV1 | Net mean per trade | **−50.7 bps** (t −1.5) | 1.00 |
| RV2 | Gross mean per trade | −10.4 bps (t −0.3) | 1.00 |

**Verdict: NO EDGE.** The ratio is not usefully mean-reverting at these horizons even **before** costs; shorting silver at low z loses −29.6 bps gross per trade. All 18 grid variants are negative net (−42 to −118 bps per trade; battery SPA 1.00). The published Sharpe > 2 results rest on in-sample model selection.

**FG: festival gold demand (Dhanteras/Diwali)** ([results/round24_fg.json](results/round24_fg.json)).
- **Rule:** long gold for the 15 weekdays into Dhanteras, 2011–2025.
- **Result:** gross +1.18% per event (t 1.06), net +0.94% (t 0.86, p 0.20); NO EDGE by the rule. The mean is carried by 2024 (+5.9%) and 2025 (+12.9%), i.e. by the gold bull, not the calendar; 2011–17 nets ≈ 0. The 15 days after Diwali average −0.96%. With 15 events the test has little power either way.

**DSR count:** 13,857 (A38).

### 22.11 Round 25: COMEX option expiry and the Japanese fiscal year-end (A39; [run_round25.py](run_round25.py))

**OX: COMEX gold and silver option expiry** ([results/round25_ox.json](results/round25_ox.json)).
- **Claim tested:** metals are "managed" down into the monthly option expiry (the 4th-to-last US business day) and rebound after.

| | Test (gold, 200 expiries 2010–26) | Result | Holm p |
|---|---|---|---|
| OX1 | 3 days into expiry < 0 | **+10.0 bps** (t 0.91): wrong sign | 1.00 |
| OX2 | 3 days after expiry > 0 | **−8.9 bps** (t −0.80): wrong sign | 1.00 |

**Verdict: NO EDGE.** The folklore is backwards in 2010–26 data: gold drifts *up* into expiry and *down* after, in both halves, and silver does the same (+17 / −20 bps, n.s.). Both trades lose net (−17 and −15 bps per event); the 8-variant grid confirms.

**JM: the Japanese fiscal year-end** ([results/round25_jm.json](results/round25_jm.json)).
- **Deviation, disclosed:** the daily-bar builder starts in 2008, so n = 19 events (2008–26), not 2003–26 as registered.

| | Test | Result | Holm p |
|---|---|---|---|
| JM1 | Short USDJPY, last 5 business days of March | **−35.5 bps** per event (t −1.16): repatriation shorts lose | 0.88 |
| JM2 | Long USDJPY, first 5 business days of April | +41.8 bps (t 1.08), all of it before 2015 | 0.28 |

**Verdict: NO EDGE.** USDJPY *rose* in late March more often than not; the April rebound died after 2014.

**DSR count:** 13,867 (A39).

### 22.12 Round 26: US→overseas session spillover; macro-print reaction momentum (A40; [run_round26.py](run_round26.py))

**SP: the prior US session traded in the next overseas session** ([results/round26_sp.json](results/round26_sp.json)). Becker–Finnerty–Gupta (1990) and Hamao et al. (1990) found overseas sessions *continued* the prior US move; everything since is post-sample.

| | Test (2013–26) | Result | Holm p |
|---|---|---|---|
| SP1 | JP225 long-short on the prior US sign, open → close, net | **−10.4 bps/day** (t −7.0, n 3,413) | 1.00 |
| SP2 | Pooled JP225 + HK50 + AUS200 | −10.5 (t −9.9) | 1.00 |

**Verdict: NO EDGE — the published effect has fully inverted.** After a US up-day the overseas session averages **−4.2 bps** (JP225), −6.6 (HK50), −4.6 (AUS200), −1.8 (GER40); after a US down-day **+4.5 / +4.2 / +3.2 / +3.7**. The sign correlation is ≈ −0.05 in all five markets, uniform across both halves.
- **What the inversion is:** the index-reversal edge (REV) seen from another angle. "Buy the overseas session after a US down-day" is REV's next-session hold on those markets. As a stand-alone session trade it grosses +2.6 to +5.6 bps/day against 3–6 bps of round-trip costs, so the ensemble REV book (few trades, held through the session) remains the right way to harvest it; a daily fade book would be a post hoc flip **and** net-negative.

**ED: reaction momentum after NFP and FOMC prints, US500/US100** ([results/round26_ed.json](results/round26_ed.json)).

| | Test (US500) | Result | Holm p |
|---|---|---|---|
| E1 | NFP: sign of the 08:30 → 08:45 reaction, held 08:45 → 15:55, net | −11.3 bps/event (t −1.6, n 146; gross −8.3) | 1.00 |
| E2 | FOMC: sign of 14:00 → 14:15, held 14:15 → 15:55, net | −5.5 (t −0.8, n 103; gross −2.5) | 1.00 |

**Verdict: NO EDGE.** The first reaction partially reverts rather than continues (hit rate 54% on NFP but losers run larger), in both halves and on US100 too. This matches family U (FX macro shocks, dead) and IM2 (late-day reversal).

**DSR count:** 13,895 (A40).

### 22.13 Round 27: the holiday morning on the unexamined crosses; Toshin month-start flows (A41; [run_round27.py](run_round27.py), [results/round27_hd_ts.json](results/round27_hd_ts.json))

**HD: the Japanese-holiday morning, on five crosses never measured for it** (GBPJPY, CHFJPY, AUDJPY, CADJPY, NZDJPY, 2008–26; ~252 holiday events).

| | Test | Result | Holm p |
|---|---|---|---|
| H1 | Basket long 09:00 → 09:55 JST on holidays < 0 | −1.94 bps (t −1.68) | **0.092** |
| H2 | Holidays minus normal days < 0 | −2.11 bps (t −2.08) | **0.056** |
| H3 | Day-after POST minus normal > 0 | +0.71 (t 0.56) | 0.29 |

**Verdict: both NOT CONFIRMED** by the pre-registered rule — H1 and H2 miss the 5% Holm gate narrowly.
- **What the data shows anyway:** the sign replicated in all five crosses (GBPJPY −2.48 t −2.6, CHFJPY −2.16 t −2.5, CADJPY −2.49 t −2.3, NZDJPY −2.02, AUDJPY −0.39), and the USDJPY build check nets +1.69 bps (t 2.2, 15 of 24 years positive).
- **The honest call:** likely a real but small effect (~2 bps × ~13 days a year) that this dataset cannot push past the gate. Both leads are **closed** — the unseen data is spent, and even at face value the annual value is minor.

**TS: Toshin month-start flows, USDJPY 2003–26** (620 events).
- **Mechanism:** Japanese investment trusts settle retail purchases of foreign assets in the first days of the month; the flow buys dollars at the fixing.
- **Rule:** long USDJPY 09:00 → 09:55 JST on the first 3 Tokyo business days of the month (excluding Gotobi, holiday and day-after days).

| | Test | Result | Holm p |
|---|---|---|---|
| **T1** | Gross mean > 0 | **+2.46 bps** (t 3.99) | **0.00007** |
| **T2** | TS days minus normal days | **+1.89 bps** (t 3.03) | **0.0012** |

**Verdict: CANDIDATE** (both pass Holm; net at 1 bp positive in both halves: +2.50 in 2003–14, +0.41 in 2015–26). By the pre-registered rule it must be confirmed on the crosses (round 28) before any build.
- **Structure:** the effect grows through the settlement window (day 1 +1.68, day 2 +2.67, day 3 +3.69, t 2.9) and, unlike Gotobi, does **not** reverse after the fix (POST −0.32): consistent with a flow spread across the morning rather than concentrated pre-hedging.
- **The whole session:** 09:00 → 15:00 on TS days is +3.04 bps (t 2.7) against **−1.25 on normal days** (t −2.6).
- **Caveats:** the second-half net (+0.41 bps at 1 bp cost) is thin; EURJPY's TS mornings are weakly positive only (+0.50, t 0.67).

**DSR count:** 13,918 (A41).

### 22.14 Round 28: the Toshin candidate on the crosses (A42; [run_round28.py](run_round28.py), [results/round28_ts_confirm.json](results/round28_ts_confirm.json))

**The confirmation set:** month-start (TS-day) mornings on GBPJPY, CHFJPY, AUDJPY, CADJPY and NZDJPY, 2008–26 — a category never isolated on these crosses.

| | Test (basket, 493 events) | Result | Holm p |
|---|---|---|---|
| C1 | PRE on TS days, gross > 0 | +1.06 bps (t 1.26) | 0.20 |
| C2 | TS days minus normal days > 0 | +1.07 bps (t 1.29) | 0.20 |

**Verdict: NOT CONFIRMED. The TS candidate is closed.**
- **What the crosses show:** the sign is right in all five (TS means +0.8 to +1.4 bps; every TS-minus-normal difference positive; GBPJPY and CADJPY individually p ≈ 0.04), but the basket carries about **half** of USDJPY's effect (+1.06 vs +2.46) and misses the gate by a wide margin.
- **Reading:** if the flow is real it is mostly a *dollar* purchase (the crosses inherit only the yen leg), which a five-cross basket cannot confirm. By this project's standard — the same one that closed family R's USDJPY-only breakout — a single-series effect without breadth support is not built.
- **On file:** USDJPY's month-start morning remains a striking single-market fact (+2.46 bps, t 3.99 over 620 events, no post-fix reversal, whole session +3.0 vs −1.25 on normal days). If independent flow data (Toshin settlement calendars, MoF weekly flows) ever becomes available, it is the first thing to re-test.

**DSR count:** 13,920 (A42).

### 22.15 Round 29: the ECB 14:15 fix; the GT quarter-end measurement (A43; [run_round29.py](run_round29.py), [results/round29_ecb_fix.json](results/round29_ecb_fix.json))

**EF: the ECB fix.** The euro reference rate is snapshotted at 14:15 CET; until 2016-07-01 it was published ~14:30 and used transactionally, and the ECB moved publication to 16:00 explicitly to stop that.

| | Test | Result | Holm p |
|---|---|---|---|
| E1 | EURUSD fix reversal (fade the 13:45 → 14:15 move to 15:00), gross, pre-reform | +0.30 bps (t 0.89, n 3,389) | 0.56 |
| E2 | Pre-reform minus post-reform | +0.13 (t 0.29) | 0.56 |
| E3 | 3-pair basket reversal, pre-reform | +0.14 (t 0.62) | 0.56 |

**Verdict: NO EDGE.** Unlike the Tokyo fix, the ECB concertation never produced a tradeable reversal, even when it was used transactionally; the reform is invisible in returns (only the average pre-fix |move| fell, 7.6 → 5.6 bps, in line with the general post-2016 vol decline). Post-reform, fading the fix **loses** −0.84 bps net (t −2.7). The 12-variant grid confirms. With this, every benchmark fix on the calendar — Tokyo, London/WMR, ECB, LBMA, SGE — has been tested; **only Tokyo pays.**

**GT quarter-end measurement (implementation, no verdict).** On USDJPY's post-fix short, month-end Gotobi days at fiscal quarter ends (Mar/Jun/Sep/Dec) earn **+6.90 bps gross (t 7.3, n 93)** against +2.71 (t 3.1, n 190) on other month-ends and +2.10 on all Gotobi days. The fixing flow concentrates at quarter-end corporate payments. The GT book already contains these days; the measurement documents where its value sits (≈ 4 days a year carry ~13% of the annual gross). It is *not* used to re-optimize sizing (that would be in-sample).

**DSR count:** 13,935 (A43).

### 22.16 Round 30: quarter-end settlement days beyond the Gotobi dates (A44; [run_round30.py](run_round30.py), [results/round30_quarter_end.json](results/round30_quarter_end.json))

**The prediction:** if quarter-end payments drive round 29's +6.9-bps amplification, the *other* business days of the quarter-end week (never isolated before) should carry elevated fix flow too.

| | Test | Result | Holm p |
|---|---|---|---|
| Q1 | USDJPY POST on quarter-end non-Gotobi days minus normal days | +0.36 bps (t 0.44; D +1.28 vs normal +0.92) | 0.70 |
| Q2 | Cross basket, the same | −1.11 (t −0.86; D −0.47) | 0.80 |

**Verdict: NOT CONFIRMED.** The quarter-end concentration lives **on the dated days themselves** (the 25th, 30th and month-end), not on the surrounding week — consistent with Gotobi settlement being date-contractual, not week-diffuse. The expansion is closed. (Jun/Dec's +2.77 within D is a 1-of-2 post hoc split, not evidence.)

**DSR count:** 13,943 (A44).

### 22.17 Round 31: the practitioner canon — Kaufman's noise hypothesis, Davey's monkey test, Pardo's walk-forward efficiency (A45; [run_round31.py](run_round31.py), [results/round31_kaufman.json](results/round31_kaufman.json))

**KN: Kaufman's noise hypothesis** (*Trading Systems and Methods*: noisier markets favor mean reversion; noise = 1 − efficiency ratio).

| | Test | Result | Holm p |
|---|---|---|---|
| N1 | Across 12 indices: rank correlation of mean noise (2013–26) with the market's median raw REV validation Sharpe | **ρ = −0.09** (10,000 permutations) | 0.61 |
| N2 | SPY/QQQ: family-A timing value on active days after high-noise vs low-noise closes | high 0.83 vs low **3.24 bps** (t −2.17, reversed) | 1.00 |

**Verdict: NOT SUPPORTED**, in both dimensions, within this universe.
- **Cross-section:** QQQ — the best mean-reversion market here — is the *least* noisy of the 12; IWM, AXJO and N225 top the noise ranking with middling Sharpes; FTSE is 4th noisiest with none. Kaufman's ranking does not explain where index MR pays.
- **Time series (descriptive; the reverse of a failed one-sided test, not evidence):** REV's timing value concentrates after **low-noise** (smooth, directional) moves — clean sell-offs, not choppy ones. That is the round-15 stress-liquidity story again (sharp liquidations command the rebound premium), and it argues once more against noise- or calm-filters on the build.

**MK: Davey's monkey test** (2,000 selection-skill-stripped twins per edge; his bar: ≥ 90th percentile).

| Edge | Actual | Monkey mean | Percentile |
|---|---|---|---|
| **N3 US100 momentum** (random-direction twins, same sessions/costs) | +2.86 bps/day net | −3.03 | **100.0** |
| **GT Tokyo fix** (random-day twins, same short/window/cost) | +1.14 bps/trade net | +0.32 | **98.2** |
| REV day-selection, SPY / QQQ (market return on active days vs random days) | +6.62 / +9.23 bps/day | +5.31 / +7.39 | 71.4 / 74.7 |

- GT and N3 pass Davey's bar outright. REV's *day-selection* alone is only modestly better than random at daily granularity (the test is underpowered there: the selection premium of +1.3–1.8 bps/day is ~0.7 SE); REV's case rests on its family battery, breadth and walk-forward — which is where it is overwhelming.

**WF: Pardo's walk-forward efficiency** (walk-forward Sharpe ÷ best in-sample variant Sharpe; his robustness bar: ≥ 50%).

| Family | WFE |
|---|---|
| A (index reversal) | **84.3%** |
| RB (SQX-native reversal) | **87.5%** |
| GT (Tokyo fix grid) | **86.3%** |

All three confirmed edges sit far above Pardo's bar — walk-forward performance retains ~85% of the optimized in-sample level, the signature of an edge that isn't an optimization artifact.

**DSR count:** 13,945 (A45).

### 22.18 Round 32: annual return seasonality; intraday half-hour periodicity (A46; [run_round32.py](run_round32.py))

**KS: Keloharju–Linnainmaa–Nyberg (2016) annual seasonality on the FTMO universe** ([results/round32_ks.json](results/round32_ks.json)). 21 instruments (12 indices, 7 FX majors, gold, silver); long the 3 best / short the 3 worst historical same-calendar-month performers, monthly.

| | Test | Result | Holm p |
|---|---|---|---|
| K1 | Gross long−short, 2003–26 (283 months) | +26.9 bps/month (t 1.26) | 0.21 |
| K2 | Post-publication 2017–26 | +9.1 bps/month (t 0.21) | 0.42 |

**Verdict: NO EDGE.**
- The pattern exists faintly — the tercile-book grid variant grossed +47.8 bps/month (t 2.98), but the family battery puts selection in context: SPA 0.35, walk-forward t 0.74, **WEAK FAMILY**.
- It decayed after publication (+9 vs +27 bps gross), and CFD economics bury it regardless: two financed legs cost ≈ 33 bps/month, leaving −31 bps/month net post-publication. A 21-instrument cross-section cannot deliver what KLN's 13%/yr needed — thousands of stocks and financing-free execution.

**HP: Heston–Korajczyk–Sadka (2010) half-hour periodicity on index CFDs and FX majors** ([results/round32_hp.json](results/round32_hp.json)). 388,159 bin pairs across US500, US100 (13 bins, 2013–26), EURUSD, USDJPY (26 bins, 2003–26).

| | Test | Result | Holm p |
|---|---|---|---|
| H1 | Pooled same-bin lag-1 correlation | **ρ = 0.0013** (z 0.35) | 1.00 |
| H2 | Sign rule, gross per bin-trade | −0.0001 bps (t 0.00) | 1.00 |
| H3 | Filtered rule, net per day | −9.8 bps (t −33) | 1.00 |

**Verdict: NO EDGE — the effect does not exist at this level.** HKS periodicity is a *cross-sectional single-stock* phenomenon (per-stock institutional order-splitting); at the index and FX-pair level the flows aggregate away completely. The cleanest null of the whole program.

**DSR count:** 13,962 (A46).

### 22.19 Round 33: the 0DTE regime — does intraday reversal replace momentum? (A47; [run_round33.py](run_round33.py), [results/round33_0dte.json](results/round33_0dte.json))

**Hypothesis:** 0DTE market makers are on average long gamma (Dim, Eraker & Vilkov 2024), and long-gamma hedging strengthens intraday reversal (Baltussen et al. 2021). SPX reached daily expiries on 2022-11-14 — a natural experiment.

| | Test (fade the 09:30 → 14:00 move until 15:55) | Result | Holm p |
|---|---|---|---|
| Z1 | US500, post-2022-11, net | **−3.49 bps/day** (t −2.73, n 866) | 1.00 |
| Z2 | Post minus pre, gross | +0.43 (t 0.28) | 1.00 |
| Z3 | US100, post, net | −3.94 (t −2.65) | 1.00 |

**Verdict: NO EDGE — the mechanism prediction fails.** The afternoon did not turn to reversal after 2022; if anything it leans further toward *continuation*. The morning–afternoon correlation from 15:00 rose on US500 (0.047 → 0.146) and US100 (0.103 → 0.129); every reversal variant is negative net in both periods.

**Risk check on an existing edge — good news for N3:** US100 noise-area momentum earned **+4.87 bps/day after 2022-11 (t 1.92, n 649)** against +1.73 before. The 0DTE era has *not* eroded the momentum edge; it has coincided with its strongest stretch. (The 15:00 correlation rise is post hoc and driven by large days; it is not a separate rule.)

**DSR count:** 13,974 (A47).

### 22.20 Round 34: N3 breadth on US30/US2000 from a second feed (A48, A48a; [run_round34.py](run_round34.py), [results/round34_calibration.json](results/round34_calibration.json), [results/round34_diagnostic.json](results/round34_diagnostic.json))

**Question:** does the US100 momentum edge (N3) exist on US30 and US2000, which HistData lacks? Dukascopy's free feed has both, but it allows about one file every 20–30 seconds, so minute data (one file per day) would take ~28 hours per instrument. Amendment A48a, written before any US30/US2000 return was computed, switched to hourly candles, with a calibration gate on US100 first.

| Gate (A48a, decided in advance) | Required | Result |
|---|---|---|
| Hourly primary vs minute-exact native primary, HistData US100, 3,031 common days | correlation ≥ 0.60 | **0.455 — failed** |
| Hourly primary mean | > 0 | +1.16 bps (t 0.96) against the minute rule's +4.18 (t 3.21) |

**Verdict: UNTESTABLE WITH HOURLY DATA.** No breadth claim either way; no US30/US2000 return was computed. The download was stopped.

**Why it failed (post hoc, reproducible with `DIAG`):** the minute-exact rule started at **10:00** instead of 09:30 earns only +1.46 bps (t 1.23), and it correlates **0.985** with the hourly rule. The bar size is harmless; **the session start is everything.** About two-thirds of N3's edge is earned by bands set at the 09:30 open and touched in the first half hour, and hourly bars (whole NY hours) cannot start at 09:30.

**Build consequence (new, important):** N3 must place its stop orders **at the 09:30 NY cash open**, on M1–M5 bars. A build that waits for the first hourly bar, or starts at 10:00, keeps about a third of the edge, which is below costs at FTMO spreads. (Post hoc split of the 09:30 rule by fill time: fills before 10:00 earn 8.7 bps per trade, later fills 3.8–5.1. What matters is anchoring the bands at the 09:30 open, not a time filter.)

**DSR count:** 13,986 (A48a; the 12 trials are counted though never run).

#### The minute test itself (A48b; [data_duka_chart.py](data_duka_chart.py), `run_round34.py RUNM`, [results/round34_n3_breadth_minute.json](results/round34_n3_breadth_minute.json))

Dukascopy's chart service turned out to serve the same one-minute BID candles 30,000 per request, so A48 was run **as originally registered**: the native grid unchanged, stops at the 09:30 open, flat 15:59.

| | Result |
|---|---|
| **Feed-validation gate** (Dukascopy US100 vs HistData US100, native primary, 3,235 common days) | correlation **0.969**, passed; +4.04 vs +3.80 bps/day |
| **N3 on a second broker's US100 feed**, 2012–2026 | primary **+3.73 bps/day (t 3.25)**; **12/12 variants positive** |
| **B1 US30** (2012-04 → 2026-09, 3,517 sessions) | **−0.99 bps/day** (t −1.07); halves −0.57 / −1.40; 0/12 variants positive |
| **B2 US2000** (2018-08 → 2026-09, 2,010 sessions) | **−3.19 bps/day** (t −1.64); halves −1.49 / −4.89; 0/12 variants positive |
| A22 battery, 24 US30/US2000 variants | SPA 1.00, walk-forward t −3.15, NO EDGE |

**Verdict: NOT CONFIRMED — N3 is a US100-only edge, and it is now confirmed on an independent feed.** Two findings:

1. **Robustness:** a different broker's quotes reproduce N3 day by day (correlation 0.97), in every variant. HistData artefacts cannot explain the edge.
2. **Mechanism:** the same rule loses on the Dow and the Russell in every variant, so the effect is not generic index "trend-day" behaviour. It is specific to the Nasdaq-100. The leading candidate is the Nasdaq-specific hedging complex: the largest leveraged-ETF pair (TQQQ/SQQQ) rebalances in the direction of the day's move, and QQQ options carry the heaviest short-dated retail call activity. Round 35 tests whether the effect lives in the Nasdaq mega-cap constituents themselves.

**Build note:** don't clone N3 onto US30 or US2000. Dukascopy's measured session spreads are 0.6 bps (US30) and 0.7 bps (US100), so the registered 1.5 bps cost is conservative.

**DSR count:** 14,010 (A48b).

### 22.21 Round 35: N3 momentum in FTMO's US mega-cap stock CFDs (A49; [run_round35.py](run_round35.py), [results/round35_stock_momentum.json](results/round35_stock_momentum.json), [results/round35_costs.json](results/round35_costs.json))

**Question:** round 34 showed N3 is Nasdaq-100 specific. Does the effect live in the constituents? The native N3 grid, unchanged, ran on 12 FTMO-listed mega-caps: Dukascopy minute candles 2017-03 → 2026-09, 2,200–2,370 sessions each. Costs were measured per stock before any return was computed: median Dukascopy spread plus 1 bp, from 2.7 bps per entry (NVDA) to 10.2 (NFLX).

| | Result |
|---|---|
| **S1** equal-weight basket, primary (range, k 0.5, flat), net | **−0.07 bps/day (t −0.05)**; halves +0.15 / −0.29 |
| **S2** stocks with a positive net mean | **5 of 12** (needed 10) |
| Basket at 2× cost | −4.10 bps/day (t −2.89) |
| A22 battery (144 variants) | SPA 0.42, PBO 0.04, walk-forward t 0.92: WEAK FAMILY |
| Correlation of the basket with US100 N3 | 0.67 |

**Verdict: NO EDGE for the registered basket.** The rule does not work on mega-caps as a group.

**But the cross-section shows the mechanism clearly (descriptive, per-stock primary, net):**

| Momentum pays | bps/day (t) | Momentum loses | bps/day (t) |
|---|---|---|---|
| **TSLA** | **+9.10 (2.20)** | **JPM** | **−7.61 (−3.80)** |
| **NVDA** | **+8.57 (2.34)** | **V** | **−5.59 (−2.89)** |
| AMD | +5.80 (1.41) | META | −4.25 (−1.55) |
| AMZN | +2.99 (1.29) | AVGO | −3.81 (−1.33) |
| GOOGL | +1.10 (0.48) | MSFT | −2.91 (−1.43) |
| | | NFLX, AAPL | −2.63, −0.70 |

The names with the heaviest retail call-option and leveraged-ETF activity (TSLA, NVDA, AMD) carry intraday momentum; the low-volatility, institutionally held names (JPM, V) *reverse* strongly. This is what the dealer-gamma account predicts (Barbon & Buraschi 2021): short-gamma dealers amplify moves, long-gamma dealers dampen them. It also explains why the Nasdaq-100, and not the Dow, shows N3. The split was not pre-registered, so it is a lead, not a result.

**Stocks in play (pre-registered as "also reported"):** on **earnings-reaction sessions** the primary earns **+21.4 bps per stock-session net** (n 496, t 1.83), against −0.39 on the other 27,599 (Welch t 1.85, p 0.032). This is the "stocks in play" effect of Zarattini, Barbon & Aziz (2024), found here on an independent sample and after measured CFD costs. It was the strongest new lead of rounds 34–36. **Round 37 tested it on 71 unseen stocks, and it failed** (§22.23).

**DSR count:** 14,154 (A49).

### 22.22 Round 36: five famous practitioner setups, as their books state them (A50; [run_round36.py](run_round36.py), [results/round36_practitioner_setups.json](results/round36_practitioner_setups.json))

**Question:** do the best-known published setups work on FTMO instruments today? Each was coded exactly as its book defines it, with the intraday order of events resolved on one-minute bars. Instruments: US500, US100, GER40, UK100, JP225 and gold cash sessions, 2013 → 2026-09-18, costs 1.5–3.0 bps per round trip.

| Setup (source) | Trades | Net, bps/day (6-market portfolio) | t | Holm p | Verdict |
|---|---|---|---|---|---|
| **Oops!** (Williams 1999) | 5,209 | −0.23 | −0.79 | 1.00 | NO EDGE |
| **Turtle Soup** (Raschke & Connors 1995) | 1,140 | −0.57 | −2.32 | 1.00 | NO EDGE |
| **80-20s** (Raschke & Connors 1995) | 2,121 | −0.37 | −1.98 | 1.00 | NO EDGE |
| **TD Sequential setup** (DeMark 1994) | 570 | +0.21 | 0.48 | 1.00 | NO EDGE |
| **Market Profile 80% rule** (Dalton et al. 1990) | 4,451 | −0.13 | −0.89 | 1.00 | NO EDGE |

**Verdict: NO EDGE in any of the five.** The 120-variant grid confirms it: SPA 0.85, walk-forward t 0.33, only 32% of variants positive after costs, no Romano–Wolf survivor.

- **The "80% rule" is a myth on today's markets:** after the open-outside, two-brackets-inside trigger, price reached the far side of the value area on **49%** of 4,505 occasions (per market 38–59%), not 80%.
- **Short sides lose everywhere** (Turtle Soup short −0.45 bps/day, t −3.3; 80-20s short t −2.1; TD sell t −2.4): fading index strength fights the upward drift, as round 12 found for the short side of reversal.
- **TD Sequential's buy setup** (+0.72 bps/day, t 1.91, hold 5) is the only positive leg. It is the reversal effect seen through a slower, rarer trigger (≈ 3 trades per market-year), and it adds nothing to REV.
- Gold is the worst market for these setups (Oops! −1.58 bps/day, t −3.2).

**Lesson for SQX users:** these patterns fill SQX's building-block library and trading forums, but as published they carry no edge on FTMO's instruments after 2013. Where they touch a real effect (the long side of reversal after declines in indices), the reversal family (REV) harvests it better.

**DSR count:** 14,274 (A50).

### 22.23 Round 37: "stocks in play" on 71 unseen S&P 100 stocks (A51, A51a; [run_round37.py](run_round37.py), [results/round37_stocks_in_play.json](results/round37_stocks_in_play.json), [results/round37_costs.json](results/round37_costs.json))

**Question:** round 35's strongest lead was N3 momentum on earnings-reaction sessions (+21.4 bps per stock-session). Does it hold on stocks that sample never touched? The test covered 71 S&P 100 stocks with Dukascopy minute data 2017–26. Earnings sessions came from 2,913 SEC 8-K Item 2.02 filings. Costs were measured per stock before any return: median 7.4 bps per entry, range 4.0–16.9.

| | Test | Result | Holm p |
|---|---|---|---|
| **E1** | Earnings-session portfolio, native primary, net | **−1.73 bps per event-day** (t −0.31; 2,583 events on 1,082 days); halves −1.49 / −1.97 | 1.00 |
| E2 | Earnings minus other sessions | +4.99 bps (t 1.08) | 0.56 |
| E3 | Ex-ante volatility vs momentum P&L across stocks | ρ = 0.007 (n 71) | 1.00 |
| E4 | Gap proxy (SQX-native "in play" filter; A51a) | −2.40 bps per event-day (t −1.28; 19,425 sessions) | 1.00 |

**Verdict: NOT CONFIRMED — all three leads closed.** Stocks in play, the volatility link and the gap proxy all fail on fresh stocks. Pooled with round 35's 12 names (83 stocks, 3,079 events) the earnings-session effect is +2.6 bps per event (t 0.59). Round 35's +21 bps was a small-sample result concentrated in a few mega-caps. The only pattern is directional: **long** fills on earnings sessions earned +15.4 bps (t 2.34), shorts −20.9 (t −2.93). That is the 2017–26 bull market in the event-day drift, not momentum.

**What rounds 35 and 37 establish together:**
1. Intraday opening-range momentum is **not** a general single-stock effect net of CFD costs (median 7.4 bps per entry on S&P 100 names). A 2016–23 "stocks in play" result on the whole US market (Zarattini et al.) does not carry over to large-cap CFDs.
2. N3's edge is an **index-level** Nasdaq-100 phenomenon (US100 only; round 34), not something its constituents inherit.

**DSR count:** 14,289 (A51a).

### 22.24 Round 38: N3 momentum on FTMO energy and silver (A52; [run_round38.py](run_round38.py), [results/round38_commodity_momentum.json](results/round38_commodity_momentum.json), [results/round38_costs.json](results/round38_costs.json))

**Question:** crude oil, natural gas and silver carry large retail leveraged-ETF and option complexes (USO/UCO/SCO, BOIL/KOLD, SLV/AGQ). Does N3's momentum, which is specific to the Nasdaq-100 among indices, appear there? None of these markets had been tested with the N3 rule. Data: Dukascopy minute data for WTI (2011 →), Brent (2010 →) and natural gas (2012 →), 09:00–14:30 NY; HistData silver (2010 →), 08:25–13:25 NY. Costs were measured before any return: 7.5–10.9 bps per entry (Dukascopy spreads).

| | Result |
|---|---|
| **C0** four-market portfolio, primary, net | **−5.61 bps/day (t −4.46)**; halves −4.22 / −7.00 |
| WTI / Brent / natural gas / silver | −5.68 (t −2.49) / −5.28 (−2.70) / −4.21 (−1.46) / −7.01 (−4.66); Holm 1.00 each |
| Gross (before costs), portfolio | ≈ +1.1 bps/day |
| 48-variant battery | SPA 0.79, walk-forward t −1.07; 19% of variants positive |
| Silver on a second feed (Dukascopy 2014 →) | correlation 0.985, −6.80 bps/day: the same answer |
| Correlation with US100 N3 | 0.05 |

**Verdict: NO EDGE.** The problem is not only costs: gross momentum is about +1 bp/day, so no realistic FTMO spread rescues it. With round 34 (US30/US2000), round 35/37 (single stocks) and round 9 (other indices, gold), **N3 is now tested on 21 markets and 83 stocks. It pays only on US100.** Keep it as a single-market edge.

**DSR count:** 14,337 (A52).

### 22.25 Round 39: does volume separate reversing days from continuing days? (A53, A53a; [run_round39.py](run_round39.py), [results/round39_volume.json](results/round39_volume.json))

**A new information source:** every earlier round used price and time; HistData has no volume. Dukascopy candles carry volume, and SQX reads the broker's tick volume natively, so a volume rule is buildable. Theory (Campbell, Grossman & Wang 1993; Llorente et al. 2002): high-volume moves are liquidity-driven and **reverse**, low-volume moves are informed and **continue**. That might explain why plain daily reversal failed on FX and gold. The data were Dukascopy hourly candles with volume, rebuilt into 17:00 New York daily bars (FTMO's server day). The signal is **relative** volume (today vs its 20-day mean), so broker volume scales don't matter.

| | Test (net; primary: RV ≥ 1.5 fade / RV ≤ 0.75 follow, move ≥ 0.5 σ, hold 1 day) | Result | Holm p |
|---|---|---|---|
| V1 | FX majors (7), high-volume reversal | −0.06 bps/day (t −0.68) | 1.00 |
| V2 | Gold, high-volume reversal | −0.34 bps/day (t −1.17); −12.9 bps per trade | 1.00 |
| V4 | FX majors, low-volume continuation | −0.08 bps/day (t −0.91) | 1.00 |
| V5 | **Mechanism:** slope of next-day return on today's return × log relative volume (predicted < 0) | **c = +0.003 (t 0.15)** | 1.00 |

**Verdict: NO EDGE, and the mechanism is absent.** Volume does not change what happens the next day in FX or gold (2004–26, 7 pairs + gold, 42,000 market-days); only 27% of 192 variants are positive. **Data amendment A53a:** the first run stopped gold's download at 2018 (a downloader bug, fixed), and Dukascopy's index CFD volume proved unusable (years missing, units jumping ~1,000×), so the index arm V3 was dropped rather than tested on broken data.

**DSR count:** 14,601 (A53).

### 22.26 Round 40: month-end rebalancing in the closing auction; US100 − US500 spread momentum (A54; [run_round40.py](run_round40.py), [results/round40_me_spm.json](results/round40_me_spm.json))

| | Test | Result | Holm p |
|---|---|---|---|
| ME1 | Fade the month-to-date move 15:30 → 15:59 on the last trading day (US500 + US100 + US30, 184 month-ends, net) | **−2.81 bps/event** (t −1.08); right 41% of the time | 1.00 |
| ME2 | The fade pays more after big months (slope on \|MTD\|) | +1.5 bps per 1% (t 1.92) | 0.08 |
| SP1 | Native N3 rule on the dollar-neutral US100 − US500 spread (net, 2013–26) | **−0.37 bps/day** (t −0.70); no variant positive | 1.00 |

**Verdict: NO EDGE in either part.** Even month-ends with |MTD| ≥ 2% earn only 0 to +2 bps (t < 0.5) into the close, and holding the fade to the next morning loses heavily (US100 −32 bps). The documented next-day rebalancing effect (Harvey et al. 2025) does not show up in the closing auction of FTMO's index CFDs after costs. **The spread result is informative:** US100 − US500 has **no** intraday momentum (correlation 0.40 with N3), so N3's profit is not a Nasdaq-relative flow; it comes from US100's own intraday trend.

**DSR count:** 14,652 (A54; 36 ME variants counted).

### 22.27 Round 41: do overseas sessions fade the prior US session? (A55; [run_round41.py](run_round41.py), [results/round41_overseas_fade.json](results/round41_overseas_fade.json), [results/round41_costs.json](results/round41_costs.json))

**Why re-open it:** round 26 found the published US→overseas continuation **inverted** in 2013–26 (t −7 to −9.9, stable across halves). The fade was set aside on two weak grounds: REV covers only its long side, and round 26 charged 6 bps per round trip, while Dukascopy's measured spreads are JP225 2.4, HK50 5.2, AUS200 2.7 and GER40 1.1 bps. As a post hoc flip it needed unseen data.

| | Test | Result | Holm p |
|---|---|---|---|
| F1 | Unseen 2000–2012 (Yahoo daily), four-market fade, gross | **−8.00 bps/day** (t −6.16) | 1.00 |
| F2 | Same, net of measured costs; halves | −10.83 (t −8.34); −9.71 / −11.95 | 1.00 |
| F3 | Fade after large US days minus small | −19.9 bps (t −8.5) | 1.00 |
| — | 2013–26 (HistData CFD minute data), net of measured costs | **+1.60 bps/day** (t 1.83); per market t ≤ 1.3 | — |

**Verdict: NO EDGE.** Two findings, one of them a lesson:
1. **The 2000–2012 "confirmation" is contaminated.** Cash-index daily opens (Yahoo) are stale. The ASX opens stocks in stages, and the Nikkei's first print uses unopened stocks' prior closes, so an open-to-close return still contains the catch-up to the US move and shows spurious *continuation* (ASX +25 bps after US up days, −28 after down days). The test could not measure what a CFD trader at the open gets. Only index CFD or futures quotes are valid for open-anchored rules, and none exist here before 2012.
2. **On the valid CFD data (2013–26), the fade nets +1.6 bps/day (t 1.8) at FTMO-level costs.** That is too weak to build, and it cannot be confirmed out of sample. Closed.

**DSR count:** 14,655 (A55).

## 23. Appraisal: how much to trust this

| Issue | Effect on conclusions | Severity |
|---|---|---|
| **Data are CFD-style quotes, not exchange prints** (HistData bid quotes; Yahoo indices) | Artifacts at spread-widening times are real (§8). Index results at 15:30–16:00 and 17:00–17:30 Berlin are at liquid hours, and the cross-source check agreed (correlation 0.98) | High for FX; low–medium for indices |
| **Power of the confirmation tests** | R3/R4 (ORB, 35–50% power) can't rule out a smaller real effect. R2 (80%) and R7 (93%) are informative | Medium |
| Multiple testing | About 745 hypotheses in total (64 in rounds 1–4, 8 literature tests and 653 scan candidates in round 5, plus W1 and family N; 14 more in round 7). The round-5 scan confirmed nothing, which is what a working multiple-testing guard should produce. **N3 (noise-area, US100) passes Holm in its own family but has a DSR of only 0.22 over all trials.** MR-06 survives BH in discovery, independent confirmation, DSR 0.95 (N = 39, daily data) and R7 at p = 0.03. R7's DSR at N = 57 is only 0.29: **the 2014–25 minute sample alone wouldn't justify it.** S2 passes Holm within its round (p = 0.011), and its DSR at N = 64 is 0.70 with only 92 monthly observations. Its case rests on replicating a published effect after the paper's sample, not on DSR | Medium |
| **Treasury end-of-month data** | IEF/TLT are ETFs, not futures. The effect is also documented in futures and swaps (Hartley & Schwarz §4.2), but futures roll near month-end in Feb/May/Aug/Nov, and the SQX build must handle the roll | Medium: verify on ZN/ZB futures data |
| **Data gaps** | HistData serves WTI only to 2023 and Euro Stoxx 50 only to 2019. The T1–T3 oil tests use 2019–2023; Brent (to 2025) is reported as a secondary and agrees | Low |
| **Post-hoc variant** | The TWAP-stop version of N3 was pre-registered only for US500. Its better US100 result (Sharpe 0.96) is post hoc | Medium: treat the conservative N3 as the tested rule |
| **Prop books are in-sample for sizing** | The notional weights in §13.3 were chosen on the same 2014–25 history the bootstrap re-uses. The pass rates are upper bounds for a trader who picks the best row | Medium |
| Post-hoc analysis | The FX clean windows, the P10 R-multiples, the P12 perturbations and the prop diagnostics are post hoc and labelled so. They were used to *downgrade* claims, never to promote one | Low |
| Researcher degrees of freedom | Round 3 was chosen after seeing round 2. That's why it used only unseen data | Low |
| Costs are assumptions | ORB, GER40 and FX results flip sign within ±1 bp of cost, so no realistic cost model rescues them. MR-06 (~20 bps) is robust to costs | Low for MR-06 |
| Regime dependence | MR-06 is strongest 2020 → and absent before 1990. The mechanism (index products, dealer liquidity provision) can change | Medium: monitor yearly |
| **The 2026 holdout is short** | Nine months give N3 a 15% chance of significance even if its edge is real. The holdout rejected or downgraded several WEAK rules and left N3 consistent, but it cannot confirm anything | Medium |
| **HistData clock (found in round 7)** | File time follows the EU DST calendar. On ~4 weeks a year, US-index rules lost those days (no bias). Hour-bucket and non-US conversions were one hour off on ~8% of days, which blurs results and can't create them. New code converts through London time | Low |
| **Second data feed for N3** | Yahoo 60-min bars agree with HistData (correlation 0.99, round 8). The 30-minute rule itself is still single-feed (X1 blocked by throttling) | Low–medium: run X1 on the broker's data |
| **Firm terms change** | Presets reflect published terms on 2026-09-26. The FTMO 1-Step Best Day Rule as a payout gate is my assumption. Swaps, and payout rules beyond those modelled (scaling plans, reviews), are not included | Medium |
| **Round-9 amendments and post hoc steps** | Two benchmark amendments (timing value; its invalidity for trend) were made after seeing results. Both are disclosed, and the family verdicts are reported under all benchmarks. The ensemble prop book is post hoc and evaluated on 2013–26, the period that qualified family A | Medium: treat the ensemble figures as upper bounds |
| **Intraday lows in multi-market books** | The combined portfolio's prop result swings from failure to success with the excursion model. Single-family books with exact per-index paths are reliable | Medium |
| **SQX's handling of the forming daily bar (round 11)** | Build (c) assumes that at 15:55 a D1 condition sees today's forming session bar (close = current price, high and low so far) and earlier completed session bars. The SQX documentation read here does not say how a higher-timeframe bar in progress is exposed | **Medium: check it in SQX before trusting a (c) backtest.** Fallback: compute today's values on the M5 chart, or use build (a) for the US |
| **Round-11 books are CFD quotes and in-sample** | R1–R3 and the A25 books use HistData bid quotes for 2014–26, the same years that qualified the edges. Scaling on 2014–16 made the reversal book's tail large (−18% at 1× on 2020-03-12) | Medium: the simulator's guard truncates such days; real gaps may not |
| **Family R passed the verdict rule narrowly** | Walk-forward Sharpe 0.005 cleared "> 0" by rounding; one market carries it. The rule does not test breadth (as with family J) | Low: reported as a lead, not an edge |
| **Look-ahead found and corrected (round 16)** | Round 15's JP225 regime split used a VIX close published after the Tokyo close. It was withdrawn and re-run. The other cross-market steps of rounds 12–16 were re-checked. ZM uses the previous VIX close. XR enters FX at 16:45 NY, after the 16:00 signal. Z and the US regime split use a VIX close 15 minutes after the equity close; the US500-only proxy (round 16) confirms the US split without it. Earlier rounds were not re-audited for this | Low after the fix |
| No holdout left | Every series here, including 2026 to September, is now in-sample for an SQX build | **Paper-trade or use post-Sep-2026 data first** |

**Overall confidence:**

- **High:** MR-06 is a real, US-specific, post-1990 effect of about 20 bps per trade, whether you enter at the close or at 15:55.
- **High:** Treasury end-of-month is real and persisted after publication, but it is outside the user's scope.
- **Moderate:** noise-area momentum on US100 is real enough to paper-trade, not to fund. It passed its own family test, a parameter plateau and an unseen 2011–13 period, but fails on US500 and doesn't survive deflation over all trials.
- **High:** simple time-of-day, day-of-week, streak, IBS and breakout rules on 24 prop instruments, and the published commodity, crude-oil and Bitcoin intraday rules, don't survive out of sample at retail costs.
- **High:** GER40 close momentum, the ORBs, FX fix windows (daily and month-end), the announcement premium, the FOMC cycle, overnight drift and turn of month are **not** tradeable edges at retail costs today.
- **Moderate:** the prop pass-rate estimates. They depend on the challenge rules, the guard, leverage and the bootstrap, and the sizing is in-sample.
- **Moderate:** MR-06's intraday half (G12). It is WEAK by rule, but backed by 33 years of SPY data and by the overnight/intraday decomposition.
- **High:** time-series momentum is a real, diversifying premium (Sharpe ≈ 0.6 after publication), and CFD financing makes it uneconomic in prop accounts.
- **High:** Halloween, options-expiration weeks, VIX-conditioned reversal, volatility management, NR7, gap fades, crypto funding and cross-index momentum give nothing tradeable at retail costs today.
- **High (round 11):** the index-reversal edge survives the way SQX trades it: 82–87% of the research Sharpe in an M5/15:55 build on CFD quotes. It holds without weekend holds.
- **High (round 11):** FX session seasonality, FX night mean reversion and European open-gap rules are not tradeable after costs today.
- **Low (rounds 11 and 18):** the London-afternoon (US-data) breakout in USDJPY, GBPUSD and gold. It was positive gross in both periods, but depends on one market after costs; on unseen USDJPY 2003–09 and six JPY crosses it was not confirmed (round 18).
- **High (rounds 19–20):** the Tokyo-fix effect on Gotobi days is real and persistent: 24 years, every JPY pair, a null placebo, a second feed, and a pre-registered confirmation on unseen 2002–07 cross data. **Moderate** that it pays after retail costs: it clears 1 bp per trade by +1.1 bps, and slippage at the fix is not modelled.
- **High (round 12):** the reversal edge is long-only and needs the next session. The European-open overnight drift, the FX weekend-gap reversal and post-release continuation are not tradeable today.

## 24. What changes in the plan

- **Build candidates (no Treasury strategies):**
  0. **The index-reversal family as an ensemble (round 9, §19):** Tier-1 and Tier-2 variants from [../strategy_library.csv](../strategy_library.csv).
     - **Markets:** US500, US100, US30, US2000 and JP225.
     - **Signals:** IBS < 0.10–0.25, RSI(2) < 5–20, 2–5 down closes, 5/10-day lows.
     - **Exits:** first up close (max 5 days) or next close.
     - **Filters:** none, or only below SMA(200). Don't use the "above SMA(200)" filter.
     - **Sizing:** weighted by volatility.
     - **SQX:** build it as a portfolio of 10–20 de-correlated variants per market. There are about 8 independent bets in the US set. MR-06 below is one member of this family.
     - **How to build it in SQX (round 11, [SQX build matrix](../../evidence/edges/SQX_build_matrix.md)):**
       - M5 main chart plus a D1 chart on a cash-session definition.
       - Signal and market entry at 15:55 NY (JP225: 14:55 JST, 15:25 from 2024-11-05); exit at 15:55 on the exit day.
       - For US-only books, broker D1 bars with next-open orders keep ~90% of that.
       - Pick from the 141 variants positive under all three builds ([../sqx_implementation_grid.csv](../sqx_implementation_grid.csv)).
       - **FTMO Standard:** no entry on the last session of the week, and exit at Friday's 15:55. That costs no Sharpe (R2).
       - **Hold US legs through the next session** (to the 15:55 mark or later). An overnight-only exit gives back most of the edge (§22, T). JP225 legs may exit at the next Tokyo open.
       - **Don't filter out stress entries on US legs.** They carry most of the edge (§22.1–22.2). No regime filter on JP225 (the round-15 JP225 result was look-ahead). No VIX data is needed.
       - **Size (round 18):** fixed notional per trade. Volatility-scaled size made the worst day worse (−13.9% vs −9.9%) and did not improve the zero-edge-adjusted pass rate.
       - **In the M5/15:55 build (round 18),** the RB signals keep 98% of their daily-close Sharpe on US100 and 107% on JP225, but 72% on US500.
       - **More entry blocks (round 17):** Stochastic %K(14) < 10–20, Williams %R(5) < −95, Bollinger %B < 0, Keltner (EMA20 − 2 ATR10), Connors RSI < 10–15, 3 lower lows, close < SMA(5) − ATR(10), cumulative RSI(2) < 35. US30 and US2000 qualify: 189 Tier 1/2 RB variants in the library.
  1. **MR-06** on US500 (primary) and US100: 15:55 entry after three down closes, exit at the next close, **volatility-scaled size** (min(2, 1% ÷ 20-day vol)). It needs an account that allows overnight **and weekend** holds (FTMO Swing). On a Standard account, skip trades that span a weekend or holiday and expect about a third of the value. JP225 (entry 5 min before the Tokyo close) and AUS200 are optional extra markets.
  2. **IM-04 on US100, now as a native SQX build (R3):** at 09:30, a buy stop at the session open + 0.5 × the prior session's range and a sell stop at open − 0.5 × range (OCO); flat at 15:59; one trade a day, or stop-and-reverse. The 12-variant native grid keeps 89% of N3's Sharpe (correlation 0.58). The original rule follows for reference: **IM-04 noise-area momentum on US100** (N3 rule, 30-min marks, 14-day lookback, flip at the opposite band, flat at 16:00, **flat sizing**: the paper's volatility targeting is worse). On FTMO funded Standard accounts, take no action at the 10:00 mark on ISM days or at 14:00/14:30 on FOMC days. **Paper-trade it first** (DSR 0.22, 2026 holdout +1.4 bps/day), and run the second-feed check X1.
  3. **GT, the Tokyo fix on Gotobi days (round 19, FX):**
     - **Rule:** USDJPY on M1 (EURJPY too if its round trip is ≤ 1 bp). Sell at 09:55:00 JST on Gotobi days (the 5th, 10th, 15th, 20th, 25th, 30th, moved to the previous Tokyo business day, plus the month's last business day); buy back at 10:55 JST. **Buy stop at entry + 20 bps** (round 20).
     - **Days:** needs a Japanese holiday list in a custom block.
     - **Account:** its own FTMO account, 10–20× notional (worst day −2.1% / −4.2% with the stop), EA daily guard.
     - **Costs:** only on a raw-spread account with a round trip ≤ 1 bp. Add the pre-fix long (09:00 → 09:55) if costs are ≤ 0.7 bp.
     - **Details:** [card](../../evidence/edges/GT_tokyo_fix_gotobi.md).
  4. **Optional, for flat-by-close accounts:** MR-06's intraday half (G12: buy the 09:30 open after three down closes, sell at 16:00). It is WEAK by rule, so treat it as a paper-trade candidate.
- **Venue and sizing (§16, §17.5):**
  - **Round 11 update (§21.4), on the SQX-style books:**
    - **Reversal ensemble:** size for survival. On FTMO 2-Step Standard: CPPI k = 10 passes 49% (zero edge 6%); fixed 1× passes 35% (7%) for $254 per account-month. Cap gross notional near 2.5–3× equity. Its signals cluster in crashes.
    - **Native US100 book:** the faster earner. FTMO 2-Step Standard at 1×: 57% pass (31%), $660 per account-month; at 3×: $1,927. FTMO 1-Step is similar.
    - **Separate accounts:** one account holding both earns less at every size.
  - **Maximum money per month:** fixed 3–4× exposure with repeated attempts. The best venue tested is FTMO 1-Step with US100 (≈ $980 per account-month); FTMO 2-Step ≈ $715–770 (US100) and ≈ $210 (MR-06, Swing).
  - **Maximum chance of passing a given attempt:** CPPI sizing, exposure = min(cap, k × distance to the loss floor), k = 10–20. 71–82% pass vs 13–22% for zero edge, over years.
  - **Once funded:** keep the sizing for speed, or switch to CPPI (k = 40) to keep the account.
  - **Throughout:** the EA daily guard is mandatory, each book runs in its own account, and each firm's terms are re-checked before relying on these numbers.
  - **Avoid, for these edges:** futures prop accounts with a monthly subscription and payout caps (Topstep ≈ $124 per account-month at best for US100; MR-06 not allowed), and trend following on CFD accounts (financing).
- **Excluded by the user:** CF-07 Treasury end-of-month (confirmed, but out of scope).
- **Drop from the build list:**
  - GER40 close momentum, both ORB variants, the FX fix windows (daily and month-end), commodity and crude-oil intraday momentum, EIA-day rules, Bitcoin intraday/hour/Monday rules, the crypto-weekend Monday trade, and noise-area on US500/GER40/gold;
  - the Treasury auction cycle, FOMC cycle, announcement days, last-30-minute momentum/reversal, overnight premium, turn of month, IBS-only, non-US mean reversion, bond reversal, and all 653 scan candidates;
  - Halloween, options-expiration weeks, VIX-conditioned MR sizing, volatility-managed index exposure, the Asian-range, Williams and NR7 breakouts, next-day reversal of last-hour moves, gap fades, crypto funding filters and cross-index momentum (round 7).
  - FX and gold session-seasonality windows, FX night mean reversion on 9 pairs, European open-gap fade or follow, and session-range breakouts or fades outside the lead below (round 11).
  - Short-side index reversal, macro-release shock follow or fade (08:30 / 10:00 / 14:00 NY), LBMA and COMEX metals windows, the FX weekend-gap reversal, and overnight-only index holds (round 12).
  - Daily reversal on FX crosses, VIX-regime index entries (redundant with REV), COT positioning rules, and trading the index rebound through FX or gold (rounds 13–14).
- **Data rules for the coding agent:**
  - FX, metal and energy tests need bid/ask (or mid) data, or must avoid windows touching 16:00–19:00 NY on bid-only data.
  - **HistData file time = London − 5 h.** Convert through London time (`data_histdata.local_table`), never assume New York time. `data_minutes.local` does the same, faster, as numpy arrays.
  - **Session daily bars:** build them from minute data. SQX sessions set the daily open, close, high and low. For JP225 the Tokyo close moved from 15:00 to 15:30 on 2024-11-05.
- **Closed lead (round 18):** USDJPY intraday momentum (the London-afternoon breakout and the noise-area bands) was not confirmed on USDJPY 2003–09 or on six JPY crosses. Don't build it.
- **Open leads (not evidence):** the London-afternoon breakout on GBPUSD and gold (not re-tested). Silver's pre-fix hour (real, t = 3.4 out of sample, but 2.4 bps against a 5-bps cost; worth checking with a tighter-spread broker); rebalancing Calendar signal (S6); month-start continuation (P16); the recurring strength of intraday trend rules on US100 only (N3, G10 t = 3.9, G7), which may be a single effect.

## Reproduce

```bash
cd research/validation
export YAHOO_CACHE=/path/to/cache HISTDATA_CACHE=/path/to/cache BINANCE_CACHE=/path/to/cache
python3 run_daily.py            # P1–P6, P16–P19        -> results/daily.json
python3 run_exploratory.py      # A1 scan               -> results/exploratory_*.json
python3 robust_e06.py           # E06 robustness        -> results/e06_robustness.json
python3 run_intraday_yahoo.py   # A2 intraday           -> results/intraday_yahoo.json (Yahoo keeps ~730 days of 60-min bars)
python3 verdicts.py             # round-1 verdicts      -> results/verdicts.json
python3 implementability.py     # round-1 costs, prop   -> results/implementability.json
python3 run_round2.py           # Q1–Q5                 -> results/round2.json
python3 run_histdata.py         # Q6, Q7 (HistData)     -> results/histdata.json
python3 verdicts_round2.py      # round-2 verdicts      -> results/verdicts_round2.json
python3 run_round3.py           # R1–R7                 -> results/round3.json
python3 prop_mr06_minute.py     # prop, realistic entry -> results/prop_mr06_minute.json
python3 diagnostics_post_hoc.py # post-hoc checks       -> results/diagnostics_post_hoc.json
python3 run_round4.py           # S1–S7, I1             -> results/round4.json
python3 round4_followup.py      # S2 robustness, books  -> results/round4_followup.json
python3 run_scan.py discover    # X scan, discovery     -> results/scan_discovery.json (committed before the next step)
python3 run_scan.py confirm     # X scan, confirmation  -> results/scan_confirmation.json
python3 run_round5.py           # T1–T8, I2             -> results/round5.json
python3 run_world_mr06.py       # W1                    -> results/world_mr06.json
python3 run_noise_area.py       # N1–N5                 -> results/noise_area.json
python3 noise_area_robustness.py # N3 checks (post hoc) -> results/noise_area_robustness.json
python3 prop_round5.py          # MR-06 Asia books      -> results/prop_round5.json
python3 prop_noise.py           # MR-06 + N3 books      -> results/prop_noise.json
python3 prop_lifecycle.py B1 && python3 prop_lifecycle.py B2 && python3 prop_lifecycle.py B3 && python3 prop_lifecycle.py merge   # §16 (A12)
python3 prop_lifecycle_funded.py B1 && python3 prop_lifecycle_funded.py B2 && python3 prop_lifecycle_funded.py B3 && python3 prop_lifecycle_funded.py merge   # §16.3 (A13)
python3 run_holdout_2026.py     # A14 2026 holdout      -> results/holdout_2026.json
python3 run_round7.py && python3 run_round7.py verdicts   # G1–G13 (A15, A18) -> results/round7.json
python3 diag_round7.py          # G6 decomposition (post hoc) -> results/round7_diagnostics.json
python3 run_h1.py               # H1 (A17)              -> results/h1.json
python3 implement_i3.py         # I3 N3 paper sizing    -> results/i3.json
python3 run_h2.py               # H2 earnings premium (EDGAR) -> results/h2.json
python3 run_h3.py               # H3 stock-level MR-06  -> results/h3.json
python3 round8.py               # X2, E1, F1, C1, S1, S2 (A21) -> results/round8.json
pip install numpy                # round 9 needs numpy
python3 run_family_a.py && python3 run_family_c.py && python3 run_family_d.py   # families A, C, D (A22)
python3 run_family_b.py build NSXUSD SPXUSD GRXEUR FRXEUR UKXGBP JPXJPY AUXAUD HKXHKD XAUUSD && python3 run_family_b.py battery
python3 family_a_aspects.py && python3 run_portfolio.py && python3 portfolio_paths.py && python3 prop_ensemble.py
for f in E F G H I J K; do python3 run_round10.py $f; done; PORTFOLIO_WITH_J=1 python3 run_portfolio.py   # round 10 (A23)
for g in ftmo2_standard ftmo2_swing ftmo1 topstep intraday_extra; do python3 prop_lifecycle_real.py $g; done; python3 prop_lifecycle_real.py merge   # §17.5 (A16)
python3 run_round11.py R1 && python3 run_round11.py R3        # round 11 review (A24)  -> results/round11_r1.json, round11_r3.json
for f in L M Q R; do python3 run_round11.py $f; done           # round 11 families      -> results/family_<x>.json
python3 run_round11.py PROP && python3 run_round11.py BOOKS    # A25 prop lifecycle     -> results/round11_prop.json, round11_books.json
python3 library_round11.py                                      # library rows + ../sqx_implementation_grid.csv
for f in S T U V W; do python3 run_round12.py $f; done; python3 library_round12.py   # round 12 (A26)
for f in Y Z ZM; do python3 run_round13.py $f; done; for f in CT XR; do python3 run_round14.py $f; done; python3 run_round15.py; python3 run_round16.py; python3 library_round13.py   # rounds 13-16 (A27-A30)
for f in FM RB IM2; do python3 run_round17.py $f; done; python3 library_round17.py   # round 17 (A31)
for f in JY VS RBC; do python3 run_round18.py $f; done                                   # round 18 (A32)
pip install holidays              # rounds 19-20: Japanese holiday calendar (tested with 0.105)
python3 run_round19.py GT && python3 run_round19.py FD && python3 library_round19.py    # round 19 (A33)
python3 gt_robustness.py && python3 gt_breadth.py && python3 gt_prop.py && GT_ONLY=stop20 python3 gt_prop.py   # GT post hoc checks and prop books
A34A=0 python3 run_round20.py && python3 run_round20.py                                 # round 20 (A34: first run; A34a: corrected run)
python3 data_audit.py && python3 run_round21.py RN && python3 run_round21.py SG        # round 21 (A35, A35a)
for f in GS AB JH; do python3 run_round22.py $f; done                                   # round 22 (A36)
python3 run_round23.py                                                                   # round 23 (A37)
for f in PB RV FG; do python3 run_round24.py $f; done                                    # round 24 (A38)
python3 run_round25.py OX && python3 run_round25.py JM                                   # round 25 (A39)
python3 run_round26.py SP && python3 run_round26.py ED                                   # round 26 (A40)
python3 run_round27.py && python3 run_round28.py                                         # rounds 27-28 (A41, A42)
python3 run_round29.py                                                                   # round 29 (A43)
python3 run_round30.py                                                                   # round 30 (A44)
python3 run_round31.py                                                                   # round 31 (A45)
python3 run_round32.py KS && python3 run_round32.py HP                                   # round 32 (A46)
python3 run_round33.py                                                                   # round 33 (A47)
python3 run_round34.py CAL && python3 run_round34.py DIAG                                # round 34 (A48, A48a)
for s in USA30 USSC2000 USATECH; do python3 data_duka_chart.py $s.IDX/USD 2012-01-15 2026-09-19; done
python3 run_round34.py RUNM                                                              # round 34 (A48b)
python3 measure_stock_costs.py && python3 run_round35.py                                 # round 35 (A49); stock candles via data_duka_chart.py
python3 run_round36.py                                                                   # round 36 (A50)
python3 measure_stock_costs.py round37_costs.json $(python3 -c "from run_round37 import CIKS; print(*CIKS)") && python3 run_round37.py   # round 37 (A51)
python3 run_round38.py COST && python3 run_round38.py RUN                             # round 38 (A52); candles via data_duka_chart.py
python3 run_round39.py                                                                   # round 39 (A53, A53a)
python3 run_round40.py                                                                   # round 40 (A54)
python3 run_round41.py COST && python3 run_round41.py RUN                             # round 41 (A55)
python3 -m unittest discover -s tests
```

HistData files are fetched year by year by `data_histdata.fetch_year` (free, no key). Treasury auction dates come from the TreasuryDirect API (`data_calendar.treasury_auctions`), 10-year yields from FRED (`data_fred.py`). The post-hoc
diagnostics in §7.3, §8 and §9 come from [diagnostics_post_hoc.py](diagnostics_post_hoc.py)
(`results/diagnostics_post_hoc.json`).
