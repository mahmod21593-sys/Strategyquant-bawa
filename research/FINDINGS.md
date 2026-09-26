# Curated findings: edges for StrategyQuant X and prop-firm challenges

*Eight rounds of pre-registered research, September 2026. No Treasury strategies (user scope).
Detail and every number's source: [validation/REPORT.md](validation/REPORT.md). Test definitions,
committed before each test: [validation/PREREGISTRATION.md](validation/PREREGISTRATION.md).*

## The verdict in one paragraph

**About 747 hypotheses tested; two tradeable edges survived.**
- **MR-06**, buying US index weakness at the close after three down days, is established.
- **Noise-area intraday momentum on US100 (N3)** is a strong candidate.

Two more results are real but secondary: MR-06's intraday half (MR-08) and the small pre-holiday effect. Trend following is a genuine, diversifying premium, but prop accounts can't hold it economically.

Everything else, including 16 families added in the last two rounds and a 653-candidate scan, failed out of sample, decayed after publication, or didn't survive retail costs.

**The prop question is mostly about where and how to trade the two edges, not about finding a third.** Planning case (half the in-sample edge, or the 2014–19 regime, whichever is lower): about $370–540 per account-month for N3 on FTMO, and about $85 for MR-06 on an FTMO Swing account. The raw in-sample figures are $715–983 and $210. Everything else in this document follows from that.

---

## 1. The edge book

| Rank | Edge | Rule (short) | Why it's believed | Weak points | Build status |
|---|---|---|---|---|---|
| **1** | **MR-06: three down closes, US indices** | Signal at 15:55 ET when US500 (or US100) is below the prior close after two lower closes. Buy at 15:55, sell at the next 16:00 close. Size min(2, 1% ÷ 20-day volatility) | Found by a pre-registered scan (1990–2012, BH q = 0.01), then confirmed out of sample: 2013 → +21.9 bps/trade, t = 3.0. Realistic 15:55 entry: +15.9 bps, p = 0.03. SPY 1993–2026: +26 bps/trade raw, t = 5.4 (711 trades). 2026: +44 bps over 23 trades | US-only: 15 other world indices n.s. Absent before 1990. Strongest since 2020. Needs overnight **and** weekend holds. ~19 trades/yr | **Build first** |
| **2** | **N3: noise-area momentum, US100** (Zarattini, Aziz & Barbon) | Band = 14-day average \|move from the open\| at each :00/:30 mark, around max/min(open, prior close). Enter on a close outside the band, flip at the opposite band, flat at 16:00, flat sizing | Pre-registered; passed Holm within its family (p = 0.028): +3.0 bps/day net, t = 2.5, Sharpe 0.73. Plateau across lookbacks; unseen 2011–13 +2.9. **Second feed (Yahoo QQQ) correlates 0.99.** 2026 holdout +1.4 bps/day (consistent) | Fails on US500 (the paper's instrument), GER40 and gold. DSR over all trials only 0.22. 2014–19 weak (+1.4), 2020–25 strong (+4.9). No verified mechanism (the leveraged-ETF explanation failed P7) | **Candidate: build, paper-trade, fund small** |
| 3 | MR-08: MR-06's intraday half | Same signal; buy the next 09:30 open, sell at 16:00 | SPY 1993–2026: +10.5 bps net, t = 2.65. HistData 2014–25: +11.9 net, t = 2.1. The overnight/intraday split of MR-06 is about 55/45 | WEAK by rule (26 trades in 2026 lost 8 bps). Too slow for subscription futures accounts | Optional; for flat-by-close accounts only |
| 4 | Pre-holiday (round 1, P18) | Long the session before a US market holiday | +12.0 bps, t = 3.25; +8.3 after 2001 (p = 0.048) | ~9 trades/yr. Published tests (Ko 2021) say it faded; my own data disagrees | Small add-on |
| — | Time-series momentum (MOP 2012) on prop instruments | Month-end sign of the 12-month return, 40% volatility target per asset | 2012–26 +91 bps/month, Sharpe 0.62, correlation with SPY 0.04 | WEAK after Holm (p = 0.053). **CFD financing on ~3.5× gross exposure leaves +1.8%/yr.** Futures prop firms ban overnight holds | Long-term portfolio only, **not prop** |
| — | Treasury end-of-month (CF-07) | Long 7–10yr Treasuries over the last 3 days of the month | Confirmed after its paper's sample | — | **Excluded by the user** |

**Build specs, variants and SQX notes** are in the edge cards:
[MR-06](../evidence/edges/MR-06_three_down_days.md), [IM-04 / N3](../evidence/edges/IM-04_noise_area_momentum.md),
[TF-01](../evidence/edges/TF-01_time_series_momentum.md). The coding agent's work order is
[AGENT_BRIEF.md](../evidence/AGENT_BRIEF.md).

**Settled build choices:**
- MR-06 exits at the next close. Holding 2–3 days earns less per day (26 → 19 → 16 bps; significantly worse).
- MR-06 keeps volatility-scaled size. Conditioning on VIX adds nothing significant.
- N3 keeps flat size. The paper's volatility targeting drops Sharpe from 0.73 to 0.57.
- N3 uses 30-minute marks (60-minute works, +2.65; 15-minute is weaker).

---

## 2. Where to trade them (published firm terms, 2014–25 books)

EV per account-month at the recommended fixed exposure, with pass rates (zero-edge twin in brackets).
**Planning column:** half the in-sample edge, or the 2014–19 regime, whichever is lower.

| Account | Edge | Pass rate | EV per attempt | Months per account | **EV / account-month** | Planning case |
|---|---|---|---|---|---|---|
| **FTMO 1-Step $100K** (news blackout once funded) | N3, 4× | 37% (25%) | $2,271 | 2.3 | **$983** | ≈ $540 |
| FTMO 2-Step $100K Standard | N3, 4× | 31% (16%) | $2,043 | 2.9 | $715 | ≈ $370 (scaled from Swing) |
| FTMO 2-Step $100K Swing | N3, 4× | 31% (17%) | $2,189 | 2.8 | $772 | ≈ $400 |
| **FTMO 2-Step $100K Swing** (weekend holds allowed) | **MR-06, 3×** | 47% (13%) | $3,654 | 17 | **$210** | ≈ $85 |
| FTMO 2-Step Standard / 1-Step (no weekend holds) | MR-06, 3× | 36–44% | $1,128–1,594 | 18–22 | $62–73 | — |
| Topstep 50K (flat by 3:10 PM CT, $49/month) | N3, 3× | 23% (14%) | $109 | 0.9 | $124 | ≈ $50 (interpolated) |
| Topstep 50K | MR-06 | **not allowed** (overnight hold) | — | — | — | — |

**How to read it:**

1. **Two accounts, two edges.** N3 on an FTMO 1-Step or 2-Step account; MR-06 on an FTMO 2-Step **Swing** account. Their P&Ls are uncorrelated (0.03), so the accounts are close to independent bets.
2. **Sizing is set by objective:**
   - **Money per month:** fixed 3–4× exposure with repeated attempts. Most attempts fail, and the passes pay.
   - **Chance of passing this attempt:** cushion (CPPI) sizing, exposure = min(cap, k × distance to the loss floor), k = 10–20. That gives 71–82% pass rates against 13–22% for zero edge, but about five years per account.
   - **Keeping a funded account:** switch to CPPI (k = 40) once funded.
3. **The EA daily guard is mandatory** (2–3% of balance). Without it, MR-06 at 2× breaches a 5% daily limit in 82% of runs.
4. **Discount the simulator's EV:**
   - **The zero-edge twin earns +$300–530 per attempt in these presets.** Losses stop at the fee while funded profits are withdrawn every 14 days. Firms counter that option with reviews and conduct rules that aren't modelled, so only the **edge value above the twin** is yours.
   - A 30% payout haircut for counterparty risk cuts every figure by about a third.
5. **Futures prop firms fit neither edge well.** They require flat by the close, charge a monthly subscription, and cap and gate payouts.

---

## 3. What paper trading can and can't tell you

| Edge | Forward data needed for t = 2 | Sequential test, expected length | Pre-set stop rule (1% one-sided vs the in-sample edge) |
|---|---|---|---|
| N3 | 1,893 trading days ≈ **7.5 years** | 6.6 years | Stop if the forward mean is below −16.7 / −10.6 / −6.6 bps/day after 60 / 126 / 252 days |
| MR-06 | 189 trades ≈ **10 years** | 8.7 years | Stop if below −19.7 / −7.9 bps per trade after 60 / 126 trades |
| MR-08 | 598 trades ≈ 31 years | 28 years | — |

**So:** a 3–6-month forward test is an **implementation check**, not validation. It should confirm:
- the EA fills and times match the backtest (15:55 entries, :00/:30 marks, 16:00 exits);
- the costs are as assumed;
- nothing is catastrophically broken (the stop rule).

The decision to fund rests on the out-of-sample evidence above, sized small enough that being wrong is affordable.

---

## 4. What not to build (and why), grouped

| Group | Tested and failed | Typical reason |
|---|---|---|
| Other index mean reversion | IBS < 0.2 (P1/P2), 5-day low (P3), 1-day reversal (P4), MR-06 on 15 non-US indices (W1), VIX-conditioned MR (G4), MR-06 on single large stocks (H3: +1 bp net) | Not significant, or US-only, or eaten by costs |
| Intraday momentum elsewhere | Last-30-min (P7), Gao first→last half-hour (P8), high-volatility threshold (P9), GER40/CAC/FTSE close momentum (P12, R1, R2), Asian indices (T7), gold/silver/oil (T1), crude and EIA days (T2, T3), Bitcoin (T4), noise-area on US500/GER40/gold (N1, N2, N4, N5), last-hour reversal (G7) | Decayed after publication, below costs, or failed the 2026 holdout |
| Breakouts | 5-min and 30-min ORB (P10, P11), Asian-range at the London open (G8), Williams (G10), NR7 (G11), opening-gap fade (G13) | ≈ 0 after costs; Williams' US100 strength is probably the N3 effect again |
| Calendar and flows | Turn of month, overnight 02:00–03:00 drift, FOMC day and cycle, macro-announcement premium (all decayed as predicted), Halloween (G1), options-expiration weeks (G2, G3), rebalancing flows (CF-02, S6), Treasury auction cycle, FX fixes (daily and month-end; the round-1 "hit" was a bid-quote artefact), Bitcoin hour/Monday rules, crypto weekend → Monday, earnings-announcement premium in large stocks (H2: decayed after 2013) | Published calendar effects on liquid instruments have mostly been arbitraged away |
| Trend and cross-section | Crypto weekly TSMOM, momentum across 14 equity indices (H1), volatility-managed exposure (G5), crypto funding-rate filter (G9) | Not significant after publication |
| Systematic scan | 653 hour-of-day, day-of-week, streak, IBS and breakout candidates on 24 instruments: 20 discovered in 2011–17, **0 confirmed** in 2018–25 | The multiple-testing guard doing its job |

**Calibration check:** in the untouched 2026 data, the rules that were WEAK or PARTIAL earlier averaged a
holdout t of −0.15, the same as rules that never worked (0.00). Rejecting them was right.

---

## 5. How far to trust this

**Why it can be trusted:**
- Every test was written down and committed **before** its data was examined. Git timestamps prove the order.
- About 747 trials, with Holm/BH within families and a deflated Sharpe over the cumulative trial count.
- Published edges were tested after their papers' samples, and 2026 was used as a genuine holdout.
- A second data feed agrees for N3.

**Known data issues:**
- HistData quotes are bid-only. The New York 17:00 rollover produced one false FX result, which was withdrawn.
- HistData's clock follows European daylight-saving time (file time = London − 5 h). US-index rules lost ~4 weeks a year, with no bias; hour-bucket rules were blurred on ~8% of days. New code converts correctly.
- WTI and Euro Stoxx files end early.

**What is still in-sample:**
- The prop figures (sizing, venue EV) re-use 2014–25.
- Presets reflect firms' published terms on 2026-09-26 and **will change**. The FTMO 1-Step Best Day Rule as a payout gate is an assumption.

**Weakest links:**
- N3's DSR (0.22) and its missing mechanism.
- MR-06's dependence on the post-2020 volatility regime.
- The simulator's free-option EV (section 2, item 4).

---

## 6. What would change these conclusions (next research, by value)

1. **Replicate both edges on the broker's own data** (AGENT_BRIEF steps 1–2). A parity failure there matters more than any extra statistical test.
2. **X1: N3's 30-minute rule on a second minute feed** (the broker's US100 data, or Dukascopy with patience). Yahoo's 60-minute bars already agree.
3. **The chosen firm's exact terms in the simulator**, including payout reviews and swap costs. Then pick CPPI or fixed sizing by your objective.
4. **Monitor the regime:** both edges earn much more in high-volatility years.
5. **Only then, new edges.** The remaining untested ideas in the register have low priors (practitioner lore, or mirror images of tested rules).

---

## Where things are

| Need | File |
|---|---|
| Every result, per round | [validation/REPORT.md](validation/REPORT.md) §1 (bottom line), §3–§18 (rounds 1–8), §19 (appraisal), §20 (plan) |
| Test definitions and amendments | [validation/PREREGISTRATION.md](validation/PREREGISTRATION.md) |
| Every hypothesis and its status | [hypothesis-register.csv](hypothesis-register.csv) |
| Edge cards, negatives, agent brief | [../evidence/](../evidence/README.md) |
| Prop simulator and firm presets | [../tools/propsim/](../tools/propsim/README.md) (`presets/ftmo_*`, `presets/topstep_50k.json`) |
| Prop plan and sizing playbook | [../docs/05-prop-firm-edge-plan.md](../docs/05-prop-firm-edge-plan.md) |
