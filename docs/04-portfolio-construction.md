# 04 — Portfolio Construction, Deployment and Monitoring

A great portfolio comes from combining **different return drivers**, not from collecting the highest
backtests. This document covers how survivors of the funnel become a portfolio, how it is sized and
stress-tested, and how it is monitored live.

---

## 1. Why low correlation beats more strategies

For N equal-risk strategies with the same Sharpe and average pairwise correlation ρ̄, the portfolio
Sharpe multiplier is √(N / (1 + (N − 1)ρ̄)). This is the diversification logic of the fundamental law
of active management (Grinold & Kahn, 2000) and of Carver's diversification multiplier (Carver, 2015).

| ρ̄ | N = 5 | N = 10 | N = 20 | N = 40 | Limit (N → ∞) |
|---:|---:|---:|---:|---:|---:|
| 0.0 | 2.24 | 3.16 | 4.47 | 6.32 | ∞ |
| 0.1 | 1.89 | 2.29 | 2.63 | 2.86 | 3.16 |
| 0.2 | 1.67 | 1.89 | 2.04 | 2.13 | 2.24 |
| 0.3 | 1.51 | 1.64 | 1.73 | 1.77 | 1.83 |
| 0.5 | 1.29 | 1.35 | 1.38 | 1.40 | 1.41 |

**Takeaway:** going from ρ̄ = 0.3 to ρ̄ = 0.1 is worth more than going from 10 to 40 strategies. Five
SQX variants of the same breakout on EURUSD are *one* strategy with extra overfitting risk. This is
why the plan is organised by edge family.

---

## 2. Portfolio architecture: risk budget by family

Risk budgets are shares of **portfolio risk** (volatility or drawdown contribution), not capital.

| Sleeve | Families | Target risk share | Role |
|---|---|---:|---|
| Trend / TSMOM | F1, F7 (CA-01) | 30% | Positive skew; historically strong in extended crises (Hurst, Ooi & Pedersen, 2017) |
| Index mean reversion | F2 (+ F5 overlays) | 20% | Negative skew; profits in choppy and recovering markets; complements trend |
| Intraday momentum / ORB | F3 | 15–20% | Flat overnight; driven by intraday flow, not multi-day trends |
| Volatility breakout | F4 | 10–15% | Captures expansion across FX, metals and energy |
| Calendar and flow | F5, F6 | 10–15% | Timing-based, largely independent of price patterns |
| Exploratory | F8, F9 | ≤ 5–10% | Only after 6 months of live results within expectation |

**Why this mix:** positively skewed sleeves (F1, F3, F4) make money when markets move and lose small
amounts often. Negatively skewed sleeves (F2, F5, F7, F9) make money in calm or mean-reverting
markets and occasionally lose large amounts. Holding both flattens the equity curve. Neither type has
to be "right" about the regime.

### Diversification caps

| Dimension | Cap / minimum |
|---|---|
| Any single family | ≤ 35–40% of risk |
| Any single asset class | ≤ 40% of risk |
| Any single market (net across strategies) | ≤ 20–25% of risk |
| Any single strategy | ≤ 10% of risk |
| Timeframes represented | ≥ 3 |
| Net equity beta (vs US500 daily returns) | Measured and capped (long-biased F2/F5 sleeves add beta) |

---

## 3. Regime coverage matrix

These are the **expected** behaviours from the literature and each family's mechanism. **Verify them
with your own data** by splitting backtests by regime (realised-volatility tercile × trend strength)
and filling in actual numbers.

| Regime | F1 Trend | F2 Index MR | F3 Intraday mom. | F4 Vol breakout | F5 Calendar | F6 FX flows | F7 Carry | F9 Range MR |
|---|---|---|---|---|---|---|---|---|
| Strong trend, rising vol | **++** | − | + | + | 0 | 0 | −/+ | − |
| Strong trend, low vol | + | + (dips shallow) | 0 | 0 | + | 0 | + | 0 |
| Range, low vol | − | + | − | − | + | 0 | + | **++** |
| Range, high vol (choppy) | −− | **++** (Nagel) | + | − | 0 | 0 | − | − |
| Crash / crisis | + (short side) | −− then ++ | + | + | − | 0 | −− | − |
| V-shaped recovery | − | ++ | + | + | + | 0 | + | 0 |

The target is **no regime column where every sleeve is negative**. Check the realised version of this
table before finalising the allocation.

---

## 4. Selection procedure

1. **Pool:** all strategies that passed the funnel (doc 03 Stages 0–11), per family.
2. **Within-family selection:** rank by *robustness*, not profit: SPP median Ret/DD, the Monte Carlo 95% Ret/DD, and market-basket pass rate. Keep 2–5 per family with pairwise daily-P&L ρ < 0.5.
3. **Cross-family check:**
   - Daily-P&L correlation matrix (SQX Correlation Filter / QuantAnalyzer).
   - **Drawdown overlap:** for each strategy's 3 worst drawdowns, what share of other strategies were also in drawdown? Correlations rise in stress, so this catches hidden tail dependence.
   - Long/short and market-exposure netting (e.g., three long US500 strategies firing on the same day).
4. **Weighting:** start with **equal risk per strategy**, then apply the family and market caps. Avoid mean-variance or "optimised" weights on the backtest: they overfit, and naive 1/N allocation is hard to beat out of sample (DeMiguel, Garlappi & Uppal, 2009).
5. **Tools:** QuantAnalyzer Portfolio Master can search combinations with correlation limits. Use it on the **development period only**, and treat its output as a shortlist, not a final answer.

---

## 5. Position sizing

| Layer | Rule | Evidence |
|---|---|---|
| Per trade | Fixed-fractional risk per trade (start at 0.25% of equity in incubation; 0.5–1% at full size), with ATR-based stops. This makes size inversely proportional to volatility | Volatility targeting reduces extreme returns across all asset classes and raises Sharpe for risk assets (Harvey et al., 2018; Moreira & Muir, 2017) |
| Per strategy | Scale so each strategy's expected annual volatility ≈ its risk-budget share × the portfolio target | Equal-risk contribution |
| Portfolio | Target 10–15% annualised volatility; derive leverage from the combined backtest **and** the 95th-percentile MC drawdown vs your drawdown tolerance | — |
| Kelly | Never full Kelly. At most 0.25–0.5 of the estimated Kelly fraction, because edge estimates are noisy and decay | MacLean, Thorp & Ziemba (2011) |
| Net exposure | Cap net position per symbol across strategies | Prevents hidden concentration |

**Drawdown-based sizing check:** if your tolerance is 20% and the portfolio's 95th-percentile Monte
Carlo max drawdown at current sizing is 14%, you have headroom. If it is 25%, scale down by 20 / 25.
Then **haircut again**, because live drawdowns typically exceed backtest drawdowns.

---

## 6. Portfolio-level validation

1. **Combined equity** on OOS-A, OOS-B and then (once) the holdout.
2. **Portfolio Monte Carlo** (trade shuffle and skip, per strategy, then combined) → drawdown distribution.
3. **Stress windows.** Report every sleeve and the total for each:

| Window | Why |
|---|---|
| Sep 2008 – Mar 2009 | Crisis, trend-favourable, MR-hostile |
| May 2010 (Flash Crash) | Intraday gap and stop risk |
| Jan 2015 (SNB de-peg) | FX tail; CHF crosses |
| Aug 2015 and Feb 2018 (volatility spikes) | Short-vol and MR stress |
| Feb – Apr 2020 | Crash and V-recovery |
| 2022 | Rate shock; trend-favourable; bond/equity correlation flip |
| Aug 2024 | Yen carry unwind |

4. **Acceptance:** portfolio Ret/DD better than the best single sleeve; average pairwise ρ ≤ 0.2; no stress window loss larger than the 95th-percentile MC drawdown; no sleeve responsible for more than 50% of total profit.

---

## 7. Incubation and deployment

| Step | Duration | Check |
|---|---|---|
| Code parity | Before incubation | Exported code reproduces SQX trades in the target platform (≥ 50 trades reconciled) |
| Incubation | 2–3 months on demo or minimum size (Davey, 2014) | Real spreads and slippage vs the model; missed or rejected orders; VPS latency; broker time |
| Stage 1 | Until ≥ 30 trades or 3 months | Live equity within the MC 5th–95th band → move to 50% size |
| Stage 2 | Until ≥ 60 trades or 6 months | Still within band → full size |

---

## 8. Monitoring and retirement (pre-registered)

Retirement rules are set **before** going live so they aren't decided emotionally in a drawdown.

| Signal | Action |
|---|---|
| Live drawdown > 95th-percentile MC max drawdown | **Pause** and investigate (execution? regime? decay?) |
| Live cumulative P&L below the MC 5th-percentile band after ≥ 30 trades | Reduce to 50% size; retire if still below after another 30 trades |
| Live slippage / costs > 1.5× modelled for 2 months | Fix execution or retire (the edge may not survive real costs) |
| Family-level Phase 1 raw effect (annual re-run) has lost significance or reversed sign | Freeze new strategies from that family; phase out existing ones over 3–6 months |
| Structural change affecting the mechanism (fix rules, product changes, market-hours changes) | Re-run the family's raw study immediately |

**Don't retire on normal drawdowns.** Trend following historically goes through long flat periods,
and a strategy inside its MC band is behaving as expected. Decay examples in this plan (pre-FOMC drift
after 2015; overnight drift after 2021) show why a **family-level** raw-effect check is part of
monitoring (McLean & Pontiff, 2016; Lo, 2004).

---

## 9. Rebalancing and the research loop

- **Monthly:** recompute realised volatility per strategy and rescale to the risk budget. Don't reallocate towards recent winners; performance chasing is a known source of underperformance.
- **Quarterly:** research sprint. Take the weakest family (or the next hypothesis in the register) through Phases 1–3; add survivors that **lower** portfolio correlation.
- **Annually:** full re-run of Phase 1 raw studies; update the regime matrix with realised numbers; review the risk-budget table.
