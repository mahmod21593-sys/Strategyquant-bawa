# What verification changed

Primary-source checks (September 2026) changed these conclusions in the plan. The docs, the hypothesis
register and the README were updated to match.

| Item | Before | After | Why |
|---|---|---|---|
| IM-01 market intraday momentum | Grade A, always-on | **Grade B**, trade only on strong signals; report post-2013 and post-2022 separately | Rosa (2022, *J. Futures Markets*): out-of-sample predictability disappears unless conditioned on signal strength. Baltussen et al. (2021) report Sharpe **before** costs. Gao et al.'s own net results fell from 6.67% to 4.46%/yr after spreads |
| IM-02 opening-range breakout | One "ORB" | **Three distinct rules** (first-candle direction, range stop-entry, open ± threshold) to test separately | Zarattini & Aziz enter at the 2nd-candle open, not a breakout, and assume no slippage. Tsai et al. (2019) choose the range length in-sample. Holmberg et al. use a threshold from the open on daily data |
| IM-04 noise area | Grade B | **B−**, with 0.61 Sharpe as the conservative baseline | Sharpe doubled from 0.61 to 1.24 through one exit-rule change chosen on the full sample |
| MR-01 index mean reversion | Index basket (US, EU, Asia) | **US indices first**; others must pass alone | Pagonidis (2013): the IBS effect is weak or absent in German, French, UK, Australian, Spanish, Swiss and Taiwanese local ETFs. It also disappears on low-volume US days, and IBS alone is eaten by commissions |
| MR-04 fade-the-close | Hypothesis | **Supported** | Baltussen et al. (2021): the last-30-minute move reverses over the next 3 days in equities, bonds and commodities |
| FX-01 FX time of day | Grade B, "short the home currency in its session" (Ranaldo) | **Grade B+**, dollar reversals around the Tokyo and London fixes | Krohn, Mueller & Whelan (2024, *JF*): 1999–2018, every year, t-stats up to 12; but ~2 bps/day, so cost-critical |
| FX-02 month-end fix | Grade B | Grade B, with exact windows and a **post-2015 retest** required | Melvin & Prins' sample ends 2012; the fix window widened in Feb 2015 |
| CF-01 turn of month | **Grade A−**, priority 1 | **Grade D, decay control only** | Han, Han & Tian (2025, *FRL*): "disappears entirely after 2001" |
| CF-03 TOM overlay | Priority 2 | Priority 3, conditional on CF-01 being alive in your data | Follows from CF-01 |
| VB-02 London-open breakout | Grade C | Grade C, plus a note that it may conflict with the USD reversal at the London fix | No peer-reviewed study found; Krohn et al. show the dollar reverses after the London fix |
| TF-01 trend | Grade A | Grade A, with the 2009–2018 flat decade documented | MOP formula verified; industry data (V3) shows ≈ 0.4%/yr over 2009–2018 |

## Prop-book shortlist after verification (doc 05 §8)

1. **IM-01 / IM-05**, thresholded: US500, US100
2. **IM-02** ORB (three variants tested separately): US100, US500, GER40, XAUUSD
3. **MR-01 / MR-02**, US indices first, with Friday exit
4. **FX-01** fix reversals, if costs allow: EURUSD, GBPUSD, USDJPY, AUDUSD
5. **VB-02**, test only
6. Turn of month **removed**; kept as a decay control
