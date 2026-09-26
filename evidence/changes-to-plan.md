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

## Prop-book shortlist after round-1 validation (superseded below)

1. **MR-06** three down days on US500 / US100: the only edge confirmed out of sample after costs
2. **FX-01 W1 + W4** (long USD NY close → Tokyo, short USD London fix → NY close): pre-register and test on 2004–2023 hourly data
3. **IM-02** ORB variants: still untested on own data (needs minute data)
4. **Pre-holiday** as a small add-on (≈ 9 trades/yr)
5. Last-30-minute **reversal** (new lead): test 2014–2021 vs 2022 → before any build
6. **Dropped:** IBS-only, non-US index mean reversion, turn of month, overnight premium, last-30-minute momentum

## Changes from validation rounds 2–3 (minute data, unseen-data confirmation)

| Item | Round-1 view | Rounds 2–3 result | Action |
|---|---|---|---|
| **MR-06** execution | Needs a close-proxy test | 15:55 entry keeps the effect (+15.9 bps, p = 0.03; US500 +20.2); next-open entry keeps only half (+11.4) | Build with a 15:55 entry, not the next open |
| MR-06 prop fit | 58–67% pass (daily bars) | **37–44% pass** at 2–8× with intraday paths and a 3% guard (33% = no edge); ≈ 17% without a guard | Building block only; ≤ 2×; EA guard mandatory |
| IM-01 last 30 min | "Reversed 2023–26; test the flip" | No flip: 2014–21 +0.4, 2022–25 −0.3 bps (p = 0.50). Gao version significantly reversed | Drop |
| GER40 close momentum (new) | — | 2014–25 +2.1 bps (t = 4.9), but **−0.2 on 2010–13** and below costs on CAC/FTSE | Drop |
| IM-02 ORB | Untested | ≈ +2.5 bps gross, ≈ +1 net; ≈ 0R with risk sizing; n.s. on 2010–13 | Drop as standalone |
| **FX-01** W1 + W4 | "Replicates Krohn et al." | **Artifact:** bid quotes drop at the NY 17:00 rollover. Clean data: real 2004–18, gone after 2019 | Drop; withdraw the round-1 claim; bid/ask data rule for all FX tests |
| Announcement premium (new) | — | +14 bps (t = 2.6) overall, +5 after 2013; FOMC days ≈ 0 after 2013 | Drop (decay) |
| Overnight drift 02:00–03:00 | Decay control | Decay confirmed (2014–20 t = 3.8 → 2021 → t = −1.2) | Control only |
| Crypto TSMOM (new) | — | +61 bps/week, t = 1.6; buy-and-hold +124 | Drop |

## Prop-book shortlist after round 3 (superseded below)

1. **MR-06** on US500 (primary) and US100: 15:55 entry, next-close exit, ≤ 2×, EA daily guard.
2. **Pre-holiday** add-on (~9 trades/yr, +8 bps net).
3. Nothing else has passed. Candidates for a fresh pre-registered round, with no evidence yet: Treasury-ETF reversal after three down days (TLT t = 3.4, IEF 2.6 in Q4); month-start continuation after equity outperformance (P16).

**Implication:** with the evidence in hand, a prop challenge is a ~40% proposition that takes 12–18 months at 2×. Any faster plan relies on leverage, not edge.

## Changes from validation round 4 (published edges after their papers' samples)

| Item | Before | Round-4 result | Action |
|---|---|---|---|
| **CF-07 Treasury end-of-month** (new) | Not in the plan | **Confirmed after the paper's sample:** IEF last 3 days +19.8 bps/month 2019 → (t = 2.95, Holm p = 0.011); 24 of 25 years positive | **Build** (futures ZN/ZB) |
| MR-06 sizing | Fixed size | Volatility-scaled size: 60% pass at 2× (vs 44%) | Use volatility scaling |
| CF-08 FOMC cycle (new) | — | +12 bps/day 1994–2016 (t = 3.9) → −4.8 after 2017 | Decay control |
| CF-09 Treasury auction cycle (new) | — | +8 bps/event (t = 0.9) after 2013; n.s. in 2002–08 too | Drop |
| FX-02 / FX-03 month-end fix | Untested | +0.8 bps (t = 0.6) after 2013; reversal +1.7 (t = 0.8) | Drop |
| CF-02 rebalancing | Opposite sign (P16) | Paper timing: +7.2 bps/day (t = 2.1), n.s. after 2023. P16 traded the day after rebalancing | Lead |
| MR-07 bond reversal | Lead from Q4 | Opposite sign in 1962–2001 (t = −2.0) | Drop |

## Prop-book shortlist after round 4 (superseded: Treasuries excluded by the user)

1. **CF-07** Treasury end-of-month on ZN (or ZB): long the last 3 trading days, ≈ 4× notional on a CFD account (≈ 2 ZN per 50K futures account).
2. **MR-06** on US500 (and US100): 15:55 entry, next-close exit, volatility-scaled, ≈ 1× notional.
3. **Pre-holiday** add-on (~9 trades/yr).

**Implication:** with CF-07 and MR-06 together, bootstrap pass rates are ≈ 73–83% on a two-step CFD
challenge (27% for zero edge) and ≈ 37–48% on a 4%-trailing futures account (19% for zero edge). Both
figures are in-sample for sizing, so paper-trade before paying for a challenge.

## Changes from validation round 5 (no Treasury strategies; prop instruments only)

| Item | Before | Round-5 result | Action |
|---|---|---|---|
| CF-07 Treasury end-of-month | Build (round 4) | — | **Excluded by the user** |
| **IM-04 noise-area momentum** | Untested | **US100 confirmed** (+3.0 bps/day, t = 2.54, Holm p = 0.028; same size on unseen 2011–13); US500, GER40, gold fail; DSR over all trials 0.22 | **Candidate: paper-trade on US100** |
| MR-06 on JP225, AUS200 | Seen in daily data | Pre-close entry works: +20.5 / +13.8 bps (t = 2.3 each) | Optional extra markets |
| MR-06 on 15 untested world indices | — | +2.8 bps pooled (t = 1.2) | Not a global edge; keep US-centred |
| Commodity intraday momentum, crude-oil and EIA-day rules | Literature | Decayed after publication or never present | Drop |
| Bitcoin intraday momentum, 22:00–24:00 UTC, Monday; crypto weekend → Monday equities | Literature | Not confirmed / not tradeable | Drop |
| 653-candidate scan on 24 prop instruments | — | 20 discovered, 0 confirmed | Drop (silver's pre-fix hour is real but below cost) |

## Prop-book shortlist (current, after round 5; no Treasuries)

1. **MR-06** on US500 (+ US100; optional JP225, AUS200): 15:55 entry, next-close exit, volatility-scaled, ≤ 2× on a two-step account without a time limit. ≈ 60% pass, ~21 months.
2. **IM-04 noise-area on US100**, after a forward test: a separate, faster attempt. ≈ 40% pass at 2× in ~6 months; with the TWAP stop (post hoc) ≈ 52% at 3× in ~4.5 months.
3. **Pre-holiday** add-on.

**Implication:** zero-edge base rates on these books are about 11–16%. The evidence supports roughly a
50–60% attempt, not a sure thing. Paper-trade before paying for a challenge.

## Round 6: sizing policy for prop accounts (decision analysis, not new edges)

| Item | Before | Round-6 result | Action |
|---|---|---|---|
| Exposure | "≤ 2× with an EA guard" | Fixed 3–4× maximises EV per account-month; CPPI cushion sizing maximises pass probability (MR-06 72–79%, US100 78%) | Choose the policy by objective (prop plan, sizing playbook) |
| Funded stage | Same sizing | CPPI k = 40 once funded keeps the account alive (MR-06 breach 19% vs 53%) for about the same EV per attempt | Option for traders who want to keep the funded account |
| Prop-sim accounting | Pass rate over decided runs | Every run counts; undecided = failure (affected only slow policies; earlier fixed-exposure numbers unchanged) | Fixed in `prop_lifecycle*.py` |
