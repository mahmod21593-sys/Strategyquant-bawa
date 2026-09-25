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

## Prop-book shortlist after literature verification (superseded below)

1. **IM-01 / IM-05**, thresholded: US500, US100
2. **IM-02** ORB (three variants tested separately): US100, US500, GER40, XAUUSD
3. **MR-01 / MR-02**, US indices first, with Friday exit
4. **FX-01** fix reversals, if costs allow: EURUSD, GBPUSD, USDJPY, AUDUSD
5. **VB-02**, test only
6. Turn of month **removed**; kept as a decay control

## Changes from own-data validation (research/validation, Sep 2026)

| Item | Literature view | Own-data result | Action |
|---|---|---|---|
| **MR-06** three down days (new) | Practitioner rule; index reversal literature | **Confirmed out of sample**: +21.9 bps/trade 2013 → , t = 3.0; fails before 1990 (mechanism) | Build first |
| MR-01 IBS < 0.2 (US) | Grade B | +2.7 bps excess, t = 1.1: not significant | Use only as a filter, not a standalone edge |
| MR-01 non-US | "test separately" | Negative on FTSE, TSX, SMI, DAX, CAC | Don't trade non-US index mean reversion |
| IM-01 last 30 min | Grade B | **Opposite sign 2023–26** (t = −2.8) | Don't build as momentum; test the reversal hypothesis on 2014–2021 vs 2022 → minute data |
| TF-01 TSMOM | Grade A | Sharpe 0.58, but equal to vol-scaled buy-and-hold | Treat as volatility-scaled exposure, not a timing edge (ETF universe) |
| Overnight premium | (not in plan) | Real gross (t = 4.7), ≈ 0 after financing | Not tradeable |
| Pre-holiday | (not in plan) | Validated gross (t = 3.2), +8 bps after costs (t = 1.7) | Small add-on only |
| Turn of month | Grade D | Decay confirmed | Unchanged |
| FX-01 | Grade B+ | W1 and W4 replicate (t = 3.9, −3.1); W2 and W3 don't; the pre-registered W3 + W4 fails | Pre-register W1 + W4 |
| CF-02 rebalancing | Grade B | Significant opposite sign in my implementation | Re-read the paper's timing; re-test |

## Prop-book shortlist after own-data validation (current)

1. **MR-06** three down days on US500 / US100: the only edge confirmed out of sample after costs
2. **FX-01 W1 + W4** (long USD NY close → Tokyo, short USD London fix → NY close): pre-register and test on 2004–2023 hourly data
3. **IM-02** ORB variants: still untested on own data (needs minute data)
4. **Pre-holiday** as a small add-on (≈ 9 trades/yr)
5. Last-30-minute **reversal** (new lead): test 2014–2021 vs 2022 → before any build
6. **Dropped:** IBS-only, non-US index mean reversion, turn of month, overnight premium, last-30-minute momentum
