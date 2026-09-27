# Rounds 13–15: negatives, and the reversal edge by regime

**Verdict:** DON'T BUILD. Pre-registered in A27–A29 and judged with the round-9 battery; DSR count 13,013 · **Source:** [REPORT.md](../../research/validation/REPORT.md) §22.1.

| Family (variants) | Result | Why it fails |
|---|---|---|
| Y. Daily reversal on 21 FX crosses, long and short, plus Bollinger(20, 2) to the middle band (4,662) | WEAK: SPA 0.12 | Crosses don't reverse at the daily horizon after 2–3 bps of costs. AUDNZD, the textbook range pair, has 22% of variants positive |
| Z. VIX-regime entries on US index ETFs: backwardation, spikes, VIX above its average, variance risk premium (108) | WEAK on timing value | Not new: it correlates 0.73 with the reversal family, with negative alpha. Buying fear *is* the reversal edge |
| ZM. Index momentum by VIX regime (4 tests) | Not confirmed | US100 momentum is stronger in high VIX (+3.7 vs +0.9 bps/day, t 1.84), but misses Holm (0.065). US500 has nothing |
| CT. COT positioning: speculator or hedger extremes, with or against; FX, gold, silver, S&P, Nasdaq (264) | WEAK: SPA 0.86 | Weekly positioning extremes carry no tradeable information after 2014 |
| XR. The US index reversal signal traded through risk FX and gold (80) | NO EDGE | Risk currencies don't share the index rebound. It is specific to index products |

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
