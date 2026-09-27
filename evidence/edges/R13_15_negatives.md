# Rounds 13–15: negatives, and the reversal edge by regime

**Verdict:** DON'T BUILD. Pre-registered in A27–A29 and judged with the round-9 battery; DSR count 13,013 · **Source:** [REPORT.md](../../research/validation/REPORT.md) §22.1.

| Family (variants) | Result | Why it fails |
|---|---|---|
| Y. Daily reversal on 21 FX crosses, long and short, plus Bollinger(20, 2) to the middle band (4,662) | WEAK: SPA 0.12 | Crosses don't reverse at the daily horizon after 2–3 bps of costs. AUDNZD, the textbook range pair, has 22% of variants positive |
| Z. VIX-regime entries on US index ETFs: backwardation, spikes, VIX above its average, variance risk premium (108) | WEAK on timing value | Not new: it correlates 0.73 with the reversal family, with negative alpha. Buying fear *is* the reversal edge |
| ZM. Index momentum by VIX regime (4 tests) | Not confirmed | US100 momentum is stronger in high VIX (+3.7 vs +0.9 bps/day, t 1.84), but misses Holm (0.065). US500 has nothing |
| CT. COT positioning: speculator or hedger extremes, with or against; FX, gold, silver, S&P, Nasdaq (264) | WEAK: SPA 0.86 | Weekly positioning extremes carry no tradeable information after 2014 |
| XR. The US index reversal signal traded through risk FX and gold (80) | NO EDGE | Risk currencies don't share the index rebound. It is specific to index products |

**Round 17 (A31):**
- **FM, FX and gold intraday momentum** (80 variants, SPA 0.50): WEAK. Session first-half-hour / last-half-hour momentum loses after costs in every pair. **Lead:** USDJPY noise-area bands, 6 of 6 variants positive in both periods, but small (+0.3 to +0.9 bps/day).
- **IM2, late-day momentum on US500 and US100** (8 variants): NO EDGE. The last half hour now leans toward reversal gross, and neither direction clears 1.5 bps.

**Round 18 (A32), JY: the USDJPY lead on unseen data. NOT CONFIRMED.**
- **USDJPY 2003–09:** the London-afternoon breakout earns −0.17 bps (t −0.22) and the L14 noise area +1.00 (t 0.86, Holm 0.78). Grid SPA 0.71.
- **Six JPY crosses, 2008–26:** both rules lose after 2 bps (−2.56 and −1.28 bps, averaged across crosses). None of the 14 rules is positive.
- **The lead is closed.**

**Round 21 (A35, A35a):**
- **RN, round-number barriers in FX and gold** (64 variants): NO EDGE.
  - Rates now reverse *less* often at round numbers than at arbitrary levels (FX 47.9% vs 48.8%; gold 45.3% vs 46.8%).
  - After a crossing they run on slightly more (FX +0.75 pp, gold +3.1 pp).
  - Every fade or follow rule loses after costs.
- **SG, Shanghai Gold Benchmark auctions** (8 variants): NO EDGE. There is no pre/post-auction pattern, and nothing changed at the 2016 launch.
- **Data audit:** HistData has isolated corrupt bars (e.g., AUDUSD 2004-11-24 at 39.82). Use `data_audit.spike_mask` before building level- or range-based events.

**Round 22 (A36):**
- **GS, gold and silver autumn effect** (Baur 2013): NO EDGE. September and November lost −1.6% a month net after 2010. Post hoc leads: January (+3.7%, t 3.0) and August.
- **AB, the Asian bid in gold after NY sell-offs** (12 variants): NO EDGE. There is no dip-buying. The unconditional Asian-session drift decayed after 2017.

**Round 24 (A38):**
- **PB, PBoC-fix reaction momentum** (AUD/NZD/JPY, 12 variants): NO EDGE. The 09:15 Beijing fix reaction doesn't continue (AUD gross ≈ 0, net −1.0 bps), and the 2015-08-11 reform is invisible in AUD's 09:10–09:20 move.
- **RV, gold-silver ratio mean reversion** (18 variants): NO EDGE. Not mean-reverting even before costs at 30–120-day lookbacks; every variant negative net (−42 to −118 bps per trade).
- **FG, pre-Dhanteras gold** (15 events): NO EDGE by rule. +1.18% gross (t 1.06), carried by 2024–25.

**Round 25 (A39):**
- **OX, COMEX option expiry** (8 variants): NO EDGE, and the folklore is backwards. Gold drifts up ~10 bps into the monthly expiry and down ~9 after, in both halves; silver the same.
- **JM, Japanese fiscal year-end** (n 19): NO EDGE. Late-March USDJPY shorts lose −36 bps per event; the early-April rebound died after 2014.

**The reversal edge by regime (round 15, family A's variants, 2007–26).** The regime is set at the signal close: stress = VIX ≥ VIX3M, on 11% of days.

| | US indices | JP225 (**withdrawn in round 16:** look-ahead; corrected: no effect) |
|---|---|---|
| Timing value per trade, stress entries | **+56 bps** | −29 bps |
| Timing value per trade, calm entries | +5 bps | **+16.5 bps** |
| Calm-only ensemble Sharpe (all trades) | 0.27 (0.54) | 0.51 (0.20) |

**For the build:**
- **US legs:** keep stress entries; they are the edge. Control the crash tail with size, not with a filter.
- **JP225 legs:** no filter. Round 15's JP225 split used a same-day VIX close published after the Tokyo close; round 16 corrected it and the effect vanished (see [REPORT.md](../../research/validation/REPORT.md) §22.2).
- **No VIX data needed.** US500 ≥ 9% below its 60-day high identifies the same stress regime on symbols FTMO offers.
