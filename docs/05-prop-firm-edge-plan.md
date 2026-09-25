# 05 — Finding Edges That Pass Prop-Firm Challenges

A prop challenge is not scored like a normal backtest. It is a **race**: reach a profit target before
touching a daily-loss limit or a maximum-loss limit, often with minimum-day, consistency and
trading-style rules. This document adapts the research plan (docs 00–04) to that objective. It
explains the maths that decides who passes, which edge families fit the rules, how to size and
protect them, and how to verify pass odds on your own StrategyQuant X output with the
[`propsim`](../tools/propsim/README.md) simulator in this repo.

> **Firm rules change often and differ between firms.** Every rule value here is an *archetype* used
> to illustrate the maths. Before relying on any result, copy the firm's **current** rules into a
> propsim JSON file.

---

## 0. Key findings

1. **The industry base rate is poor.** Firms report that roughly 5–10% of challenges pass. Data cited
   for 300,000 accounts shows about 7% reaching a payout, with an average payout of about 4% of account
   size. One firm's CEO said only 1–2% of clients receive a payout (Finance Magnates, 2025).
2. **With zero edge you would pass more often than that.** A two-step 10% → 5% challenge with a 10%
   max loss passes about **33%** of the time with no edge at all. Real pass rates far below that mean the
   typical challenger trades with a **negative** edge after costs, rule breaches and behaviour.
3. **Pass odds are driven by daily Sharpe and position size, not by returns or win rate.**
   Mathematically, what matters is edge relative to variance, (2μ/σ²), compared with the distance to
   each barrier.
4. **A single strategy with a Sharpe of 1 is not enough.** At a size that passes in about 3–4 months, it
   passes both phases only about 55–65% of the time, or less once fat tails hit the daily-loss limit.
   To pass reliably you need a **portfolio daily Sharpe of 2 or more**, which in practice means
   **several uncorrelated intraday strategies**.
5. **The daily-loss limit is the silent killer.** With fat-tailed P&L it causes most failures once daily
   volatility passes about 1% of the account. An **equity guard inside the EA** (flatten at about 60% of
   the firm's limit) turned most of those failures into ordinary bad days in simulation.
6. **Best-fit families:** intraday momentum and opening-range breakout (F3), session and volatility
   breakouts (F4), and short-hold index mean reversion (F2) with gap controls. **Poor fit:** daily trend
   following (F1) and carry (F7). They can be good strategies, but their flat periods, open-profit
   giveback and overnight gaps work against challenge rules.

---

## 1. Reality check before spending on fees

| Fact | Source |
|---|---|
| The Funded Trader: 5–10% of applicants pass; ~20% of those who pass receive payouts; 1–2% of all clients get paid | CEO statements reported by Finance Magnates (March 2025) |
| FPFX Tech data across 300,000 accounts: ~7% achieved a payout; average payout ~4% of funded account size | Same article |
| Counterparty risk is real: 1,272 traders were still waiting more than a year for funds owed by one firm | Same article |

**Implications:**

- **Treat the fee as the cost of a lottery ticket unless your OOS statistics show a real edge.**
- **Haircut payouts for counterparty risk.** In the simulator, `--payout-reliability 0.7` means you
  expect to actually receive 70% of what you earn.
- **Most funded accounts are simulated.** Your "profits" are paid at the firm's discretion under its
  terms. Read the payout conditions as carefully as the challenge rules.

---

## 2. The maths of passing

### 2.1 A challenge is a first-passage problem

Model daily P&L as drift μ and volatility σ, both as fractions of the initial balance. The probability
of gaining the target *a* before losing *b* is the classic Brownian-motion result (e.g., Karlin &
Taylor, 1975):

$$
P(\text{pass}) = \frac{e^{\kappa b}-1}{e^{\kappa b}-e^{-\kappa a}},\qquad \kappa=\frac{2\mu}{\sigma^2}
\qquad\left(\to \frac{b}{a+b}\text{ when }\mu=0\right)
$$

Three consequences follow.

- **No edge:** P = b / (a + b). That is 50% for 10%/10%, 56% for 8%/10%, and 0.5 × 0.67 = **33%** for a
  two-step 10% → 5% challenge with a 10% max loss. This is **independent of position size.**
- **Negative edge (costs):** bigger size *raises* pass odds, because fewer trades means less cost drag.
  This is the "bold play" result for unfavourable games (Dubins & Savage, 1965). It is why firms add
  daily-loss limits and bans on "gambling" behaviour. **It is not a strategy:** the expected value stays
  negative.
- **Positive edge:** smaller size raises pass odds towards 100% but takes longer. That is "timid play".
  With a deadline, the optimal policy takes more risk when behind and less when ahead (Browne, 1999).
  In practice, the time you're willing to wait sets the size.

### 2.2 Pass probability vs Sharpe and size (analytic, no daily limit)

Two-step 10% → 5%, 10% static max loss. Each cell shows **P(pass both phases) / expected trading days**
until both phases resolve.

| Annual Sharpe of daily P&L | Daily vol 0.5% | 1.0% | 1.5% | 2.0% |
|---|---|---|---|---|
| 0 (no edge) | 33% / 600 | 33% / 150 | 33% / 66 | 33% / 38 |
| 1 | 87% / 401 | 66% / 131 | 55% / 62 | 50% / 36 |
| 2 | 99% / 235 | 87% / 101 | 75% / 53 | 66% / 33 |
| 3 | 100% / 159 | 96% / 76 | 87% / 45 | 78% / 29 |

### 2.3 With fat tails and a daily-loss limit (simulated)

The same challenge with a **5% daily-loss limit** and 4 minimum days per phase. Daily P&L is modelled
as Student-t with 4 degrees of freedom plus an intraday dip, over 1,500 paths each, using `propsim`.
Cells show **P(pass both) / median calendar days to pass**. "Guard" is an EA equity stop at 3% loss
per day, with 0.25% slippage.

| Sharpe | Daily vol | No guard | With 3% guard | Failures from daily limit (no guard) |
|---|---|---|---|---|
| 1 | 1.0% | 58% / 164 | 67% / 177 | 18% |
| 1 | 1.5% | 42% / 73 | 56% / 88 | 37% |
| 2 | 1.0% | 78% / 124 | **90% / 131** | 14% |
| 2 | 1.5% | 59% / 64 | **76% / 73** | 31% |
| 2 | 2.0% | 43% / 39 | 66% / 50 | 50% |
| 3 | 1.0% | 87% / 93 | **97% / 99** | 10% |
| 3 | 1.5% | 70% / 53 | **89% / 60** | 25% |

This is an illustrative model. A guard only helps if the EA can actually exit near the guard level.
Weekend gaps, news spikes and platform outages can jump straight through it, which is why F2
strategies held overnight need extra controls (§4).

### 2.4 What to aim for

| Target | Value | Why |
|---|---|---|
| **Portfolio** Sharpe of daily P&L, out of sample | **≥ 2** (after costs, before haircut); ≥ 1.5 after a 25% haircut | §2.2–2.3 |
| Daily volatility at chosen size, 5% daily / 10% max rules | ~0.75–1.25% of initial balance | Balances pass odds against 2–4 months to pass |
| Daily volatility for tighter rules (3% daily / 6% trailing) | ~0.5–0.8% | Same risk-to-limit ratio |
| EA daily equity guard | ~50–70% of the firm's daily limit | Converts breaches into bad days |
| Worst historical day at chosen size (OOS) | < 50% of the daily limit | Leaves headroom for unseen tails |

These are **starting points**. The actual size comes from a propsim scan on your OOS trade lists (§5).

---

## 3. Which edges fit challenge rules

Each rule penalises a specific trait. Score strategies on those traits, not just on profit.

| Rule | Trait it rewards | Trait it punishes |
|---|---|---|
| Profit target vs max loss (κ) | High **daily** Sharpe | Lumpy P&L, long flat periods |
| Daily-loss limit (often on floating equity) | Bounded intraday risk, flat overnight | Gaps, correlated simultaneous positions, averaging down |
| Time pressure / opportunity cost | Many trades with small, steady edge | 5–25 trades/year strategies |
| Trailing drawdown (esp. intraday) | Quick profit capture | Large open-profit giveback (trend trailing stops) |
| Consistency (best day ≤ X% of profit) | Many similar-sized winning days | Lottery-style positive skew |
| Style rules (news, weekend, HFT and tick-scalping bans, copy trading) | Unique, moderate-frequency, rule-aware EAs | News spikes, latency games, shared commercial EAs |

### Family fit

| Family (doc 02) | Daily Sharpe potential | Daily tail control | Speed | Trailing-DD fit | Consistency fit | Overall prop fit |
|---|---|---|---|---|---|---|
| **F3** Intraday momentum / ORB | Medium per market, high when combined across markets | **High** (flat by close, SL per trade) | **High** (100–250 trades/yr) | Medium (EOD exit caps giveback) | Medium–High | **Core** |
| **F4** Session / vol-compression breakout | Medium | High (intraday variants) | High | Medium | Medium | **Core** (session variants, e.g., VB-02) |
| **F2** Index mean reversion | **High** (win rate 60–75%, smooth) | Medium (overnight gaps) | Medium | High (small quick wins) | High | **Core**, with Friday exit, reduced size and a gap stress test |
| **F6** FX time-of-day / fix flows | Low–Medium | High | High / low | High | High | **Secondary**; only with the firm's actual commissions |
| **F5** Calendar (turn of month) | Medium | Medium | Low | High | High | **Overlay / add-on** |
| **F1** Daily trend following | Low per market | Low (many correlated overnight positions) | Low | **Poor** | **Poor** (few huge days) | **Avoid in challenges**; maybe small in funded accounts with static drawdown |
| **F7** Carry | Low | Low (crash risk, swaps) | Low | Poor | Medium | **Avoid** |
| **F9** Range MR (Grade C) | Unknown | Medium | High | High | High | **Avoid until proven live** |

---

## 4. Designing a "prop book"

### 4.1 Composition

- **4–8 strategies**, from **≥ 2 families** (e.g., F3 + F4 + F2), on **≥ 3 instruments** (e.g., US100, GER40, XAUUSD, EURUSD), with pairwise daily-P&L correlation **≤ 0.2**.
- With average correlation 0.1, six strategies with Sharpe 1.0 each combine to about Sharpe 2.0 (doc 04 §1). This is the main lever for passing.
- Avoid several strategies on the same instrument and direction that fire together. They count as one position on a shock day, and the daily-loss limit sees them as one.

### 4.2 Risk controls to build into the exported EA

SQX trading options cover some of these (exit at end of day, exit on Friday, limit time range, max
trades per day). The rest need a small amount of code in the exported EA or a portfolio-level
risk-manager EA.

| Control | Setting | Purpose |
|---|---|---|
| Per-trade risk | 0.25–0.5% of initial balance per strategy (from the propsim scan) | Keeps daily vol in the §2.4 band |
| **Daily equity guard** (portfolio) | Flatten everything and stop for the day at ~50–70% of the firm's daily limit | Daily-limit breaches become bad days |
| Max open risk (sum of SL distances across open trades) | ≤ the daily guard | The guard is reachable even if every SL is hit at once |
| Target lock | Stop trading once the phase target is reached; place only the minimum trades needed for minimum days (check the firm's rules on what counts) | Avoids giving back a pass |
| Friday flat / no weekend holding | SQX "Exit on Friday" | Weekend-gap tail; some firms prohibit weekend holding |
| News blackout | No new entries, and flat, ±N minutes around high-impact releases; data from an economic-calendar feed in the EA | Firms restrict news trading, and news is where guards fail |
| Server-time alignment | The daily reset time in the EA matches the firm's reset (often midnight in the firm's server time zone) | Daily loss is measured per the firm's day, not yours |

### 4.3 Sizing by stage

- **Phase 1 and Phase 2:** use the propsim scan. Phase 2's smaller target can justify slightly smaller size at the same pass odds.
- **Funded stage:** the objective changes from *reaching a target* to *surviving and collecting payouts*. Evaluate funded expected value with propsim's funded simulation. Typically this means a lower size than the challenge size, especially with trailing drawdowns.
- **Never add risk to "catch up"** in a challenge unless it is a pre-planned, simulated rule. Browne (1999) shows that deadline-optimal policies do this systematically, not emotionally.

---

## 5. Implementation in StrategyQuant X

### 5.1 Build

- Use the F3, F4 and F2 templates from doc 02 on the firm's instruments and data feed. Where possible, build on data from the firm's own server, because symbols, sessions and spreads differ from retail brokers.
- **Costs:** use the firm's commission per lot and typical spreads at your trade times.
- **Trading options:** exit at end of day (F3/F4), exit on Friday (F2), limit time range, max trades per day 1–2, SL mandatory, and a maximum SL as a percentage of the account.
- **Ranking:** add prop-relevant criteria alongside Ret/DD: worst day, percentage of profitable days, number of trades, stagnation. For consistency rules, look at the best day's share of total profit.

### 5.2 Validation: doc 03 funnel plus prop stages

The doc 03 robustness funnel still applies in full, because an overfit strategy fails challenges just as
surely. Then add:

| Stage | Tool | Pass rule (starting default) |
|---|---|---|
| P1 | **SQX Prop Analytics** (Build 144+): worst single-day drawdown, daily-limit headroom, consistency, daily VaR/CVaR | Worst OOS day at intended size < 50% of the daily limit; consistency rule met |
| P2 | **SQX Prop Monte Carlo** (Build 144+): trade-order permutations replayed against daily loss, max drawdown and profit target | Pass % at the chosen size ≥ 70% |
| P3 | **propsim** on the **portfolio's OOS** trade lists: historical rolling starts **and** block bootstrap; multi-phase; your firm's exact drawdown type; minimum days; consistency; EA guard | Bootstrap P(pass all) ≥ 70% with median ≤ 90 calendar days; historical ≥ 60%; EV > 0 with `--payout-reliability 0.7` |
| P4 | Cost stress: propsim on trade lists retested in SQX at ×1.5 costs | P(pass all) drops by ≤ 10 points |
| P5 | Parity on the firm's platform (demo or free trial): exported EA vs SQX trades; guard, news and Friday logic triggered at least once | Trades reconcile; controls fire as designed |

**Why use both SQX Prop Monte Carlo and propsim?** Shuffling trade order (SQX) breaks up streaks of bad
days, so strategies whose losses cluster look better than they are. The block bootstrap (propsim)
keeps short streaks together, and historical rolling starts keep the real sequence. **Use the most
pessimistic of the three.** propsim also covers multi-phase challenges, trailing drawdown variants,
minimum days, the EA guard, several strategies combined, a position-size scan, and funded-stage payouts.

### 5.3 Running propsim

```bash
cd tools/propsim
# One or more SQX trade-list exports (OOS period only), rules = your firm's current rules
python -m propsim --trades orb_us100.csv lasthour_us500.csv asia_breakout_eurusd.csv@0.5 \
    --rules my_firm.json --ref-balance 100000 --from 2022-01-01 \
    --scan 0.5:3:0.25 --daily-guard 0.03 --payout-reliability 0.7 --max-median-days 90
```

The output shows the combined portfolio's daily Sharpe and the correlation matrix, then, for each
position-size multiplier: pass probability (phase 1 and all phases), median and 75th-percentile days,
failure breakdown (daily / max / time), funded payout statistics, and expected value per attempt. It
finishes with the recommended multiplier. See [tools/propsim/README.md](../tools/propsim/README.md).

---

## 6. Compliance checklist

Rules vary by firm and change often. Confirm each item against the firm's **current** terms.

- [ ] **EA and automated trading allowed** on the account type and platform. SQX can export to MT4/MT5 and other platforms, so confirm the firm's platform is one of them.
- [ ] **News rules:** restricted windows, which events count, whether they apply in challenge, funded, or both.
- [ ] **Weekend and overnight holding** rules.
- [ ] **Maximum lot size or leverage** per asset class. Check that your size at the chosen multiplier fits.
- [ ] **Prohibited practices:** HFT, tick scalping, latency or reverse arbitrage, exploiting feed errors, some grid/martingale styles, hedging across accounts, account management or copy trading between different people.
- [ ] **EA uniqueness:** don't run commercially distributed EAs. Identical trades across unrelated accounts can be flagged as group trading. Your own SQX-built strategies on your own VPS avoid this.
- [ ] **Consistency, minimum days and payout conditions** in the funded stage.
- [ ] **Inactivity rules** (maximum days without a trade).
- [ ] **Daily-loss definition:** balance vs equity, and the reset time and time zone. Encode it in propsim with `daily_loss_basis` and `--day-start-hour`.

---

## 7. Expected value and fee budgeting

- **EV per attempt** = P(pass all) × E[funded payouts] × payout reliability + fee refund − fee. propsim reports this per position size.
- **Why the simulator can show positive EV with little edge.** The trader keeps a share of the upside while the firm absorbs losses beyond the limits, so a funded account behaves like a call option. Firms limit this with rules (consistency, minimum payout thresholds, payout caps, prohibited "gambling"). Real-world payout rates (§1) show that costs and behaviour usually destroy the option value. **Only trust a positive EV when the strategy's OOS daily Sharpe is clearly positive on its own.**
- **Attempts:** with P(pass) = 0.6 per independent attempt, P(at least one pass in 3) = 1 − 0.4³ ≈ 94%. Parallel challenges on the **same** strategy are **not** independent: they fail on the same bad days. Run one attempt first, confirm live behaviour matches the simulation, then scale out.

---

## 8. Prop-book hypothesis shortlist

> **Updated after own-data validation** ([research/validation/REPORT.md](../research/validation/REPORT.md), three
> pre-registered rounds, 2026-09). The literature-based shortlist below was tested; most of it failed.

| Priority | ID | Idea | Instruments | Own-data status | Role in the book |
|---|---|---|---|---|---|
| **1** | **CF-07** | Long Treasuries over the last 3 trading days of the month | ZN (or TN/ZB) futures; Treasury CFDs where offered | **Validated after the paper's sample**: +19.8 bps/month on IEF 2019 → (t = 2.95); 24 of 25 years positive | Core: 12 short trades a year, high consistency |
| **1** | **MR-06** | Buy at 15:55 after three down closes, exit next close, volatility-scaled | US500 (primary), US100; ES/NQ | **Validated**: ≈ +20 bps/trade, ~20–26 trades/yr | Core, nearly uncorrelated with CF-07 (27 shared days in 12 years) |
| 2 | Pre-holiday | Long the day before US exchange holidays | US500 | Validated, small (+8 bps net, ~9/yr) | Add-on |
| — | IM-02 | ORB (5-min first candle; 30-min stop entry) | US100, US500 | ≈ +1 bp net; ≈ 0R risk-sized; n.s. 2010–13 | **Dropped** as standalone |
| — | IM-01 / IM-05 | Last-30-minute continuation (incl. Rosa threshold) | US500, US100 | Not present 2014–25; Gao version reversed | **Dropped** |
| — | IM-06 | GER40 close momentum 17:00 → 17:30 | GER40 | t = 4.9 in 2014–25, but failed 2010–13 and below costs on CAC/FTSE | **Dropped** |
| — | FX-01 / FX-02 | Dollar reversals around the fixes; month-end fix hedging | FX majors | Daily pattern gone after 2019 (round-1 result was a bid-quote artifact); month-end fix n.s. | **Dropped** |
| — | CF-08 / CF-01 | FOMC cycle; turn of month | US500 | Both decayed | Controls only |
| ? | VB-02 | Asian-range breakout at the London open | EURUSD, GBPUSD, XAUUSD | Untested (needs bid/ask FX data) | Test only |

**What the evidence supports for a challenge** (bootstrap on 2014–25, in-sample for sizing; report §13):

| Book | Two-step 10%/5% (3% guard) | Futures 50K, 6% target, 4% EOD trailing |
|---|---|---|
| Zero edge | 27% | 19% |
| MR-06 alone, volatility-scaled 2× | 60% · 21 months | 29% · 7 months |
| CF-07 alone, 4× notional | 86% · 16 months | 50% · 4 months |
| **CF-07 4× + MR-06 1×** | **83% · 12 months** | **48% · 3 months** |

The EA daily guard is essential: without it, MR-06 at 2× breaches a 5% daily-loss rule in 82% of runs.
Leverage speeds up passing but *lowers* the pass probability. There is still no validated fast intraday
edge at retail costs; the book above passes by patience, not by trading frequency.

---

## 9. Work plan (about 10 weeks to the first paid attempt)

| Week | Work | Output |
|---|---|---|
| 1 | Shortlist 2–3 firms; encode their current rules as propsim JSON; confirm platform, EA policy, instruments and costs | `rules/<firm>.json`, cost table |
| 1–2 | Phase 1 raw-edge studies (doc 00) for IM-01, IM-02, VB-02 and MR-01 on the firm's instruments and costs, using [`tools/edgelab`](../tools/edgelab/README.md) (commands for each are in its README) | Go / no-go per hypothesis |
| 2–6 | Build and robustness funnel (doc 03) per family; export OOS trade lists | Survivors per family |
| 6–7 | Assemble the prop book; propsim scans (historical + bootstrap) with the guard; choose size; compliance review (§6) | Book definition, chosen multiplier, expected pass odds and days |
| 7–9 | Demo or free trial on the firm's platform: parity check; guard, news and Friday logic tested | Parity report |
| 10 | First paid attempt at the chosen size. **No parameter changes during the challenge.** Log every day | Live log vs simulated bands |
| After | Post-mortem: live daily P&L vs the propsim distribution; decide whether to scale to more accounts | Scale / fix / stop decision |

---

## 10. References added by this document

- Browne, S. (1999). Reaching goals by a deadline: Digital options and continuous-time active portfolio management. *Advances in Applied Probability*, 31(2), 551–577. **(PR)**
- Dubins, L. E., & Savage, L. J. (1965). *How to Gamble If You Must: Inequalities for Stochastic Processes.* McGraw-Hill. **(Book)**
- Karlin, S., & Taylor, H. M. (1975). *A First Course in Stochastic Processes* (2nd ed.). Academic Press. **(Book)**
- Finance Magnates (2025, March 18). Only 1 in 20 traders pass prop firm challenges, reports The Funded Trader. [Link](https://www.financemagnates.com/forex/only-1-in-20-traders-pass-prop-firm-challenges-reports-the-funded-trader/) **(Industry press)**
- StrategyQuant (n.d.). Results plugins: Prop Analytics and Prop Monte Carlo. https://strategyquant.com/doc/strategyquant/results-plugins/
- StrategyQuant (n.d.). StrategyQuant X 144: Prop Firm Analysis. https://strategyquant.com/blog/strategyquant-x-144-claude-code-prop-firm-analysis-build-your-edge/
- Politis & Romano (1994), stationary bootstrap, and the diversification sources are in [references.md](references.md).
