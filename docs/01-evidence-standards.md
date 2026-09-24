# 01 — Evidence Standards

This document defines what counts as "backed by solid research" in this project, and the statistical
bars a strategy must clear before it earns capital.

---

## 1. The data-mining problem, in numbers

When you evaluate *N* strategies that have **no true edge**, the best one still looks good. Using the
expected-maximum approximation from Bailey & López de Prado (2014), and a null Sharpe standard error of
about 1/√years, the **best annualised Sharpe you would expect from pure luck** is:

| Strategies evaluated (N) | E[max z] | 5 yrs of data | 10 yrs | 15 yrs |
|---:|---:|---:|---:|---:|
| 10 | 1.57 | 0.70 | 0.50 | 0.41 |
| 100 | 2.53 | 1.13 | 0.80 | 0.65 |
| 1,000 | 3.26 | 1.46 | 1.03 | 0.84 |
| 10,000 | 3.86 | 1.73 | 1.22 | 1.00 |
| 100,000 | 4.39 | 1.96 | 1.39 | 1.13 |
| 1,000,000 | 4.87 | 2.18 | 1.54 | 1.26 |

A single overnight SQX genetic run can easily evaluate 10⁵–10⁶ candidates. **A backtest Sharpe of 1.3
on 10 years of data is therefore not, by itself, evidence of anything.** The same logic appears in
Bailey, Borwein, López de Prado & Zhu (2014), White (2000), Hansen (2005), Harvey & Liu (2015), and
Harvey, Liu & Zhu (2016).

The flip side: how many years does it take for a *true* Sharpe to be statistically distinguishable
from zero (t ≈ SR × √years)?

| True annual SR | Years for t = 2 | Years for t = 3 |
|---:|---:|---:|
| 0.5 | 16 | 36 |
| 0.8 | 6.2 | 14 |
| 1.0 | 4 | 9 |
| 1.5 | 1.8 | 4 |

**Consequences for this plan:**

1. A single strategy on a single market rarely reaches t ≥ 3 on its own. Credibility has to come from a **prior** (published mechanism and evidence), **pooling across markets** (the same rule working on several instruments), and **cheap external checks** (noise calibration, random-entry benchmarks).
2. **Count your trials.** Every build run, "improve" pass and re-optimisation adds to *N*. Log them in `research/templates/research-log-template.csv`, because the Deflated Sharpe Ratio needs *N*.
3. **Constrain the search.** Fewer building blocks and simpler rules mean a smaller effective *N*, which means less luck to overcome.

---

## 2. Evidence grades

Every hypothesis in the register gets one grade. The grade sets how hard the SQX funnel must be.

| Grade | Definition | Examples in this plan | Extra requirements |
|---|---|---|---|
| **A** | Multiple peer-reviewed studies; several markets or asset classes; long samples; survives out-of-sample or post-publication; plausible mechanism | Time-series momentum in futures (Moskowitz, Ooi & Pedersen, 2012; Hurst, Ooi & Pedersen, 2017) | Standard funnel |
| **B** | Peer-reviewed but narrower (one market, one period, or a working paper), **or** documented partial decay, **or** strong mechanism with partial evidence | Market intraday momentum (Gao et al., 2018; Baltussen et al., 2021; weakened out of sample per Rosa, 2022); FX fix reversals (Krohn, Mueller & Whelan, 2024); index negative autocorrelation (Baltussen, van Bekkum & Da, 2019); ORB (Holmberg et al., 2013; Tsai et al., 2019); FX time-of-day (Ranaldo, 2009); London-fix hedging flows (Melvin & Prins, 2015); rebalancing flows (Harvey, Mazzoleni & Melone, 2025) | Standard funnel **plus** pass on ≥ 3 markets or ≥ 2 sub-periods |
| **C** | Practitioner evidence or plausible mechanism; no rigorous peer-reviewed support | Asian-session range fade; most indicator-combination entries; NR7 breakouts (Crabel, 1990) | Funnel **plus** pooled t ≥ 3, noise-calibration pass, ≤ 5% portfolio risk until 6 months live |
| **D** | Documented to have disappeared, or no mechanism | Turn of month after 2001 (Han, Han & Tian, 2025); pre-FOMC drift after 2015 (Kurov et al., 2021); overnight 2–3am ET drift after 2021 (NY Fed, 2026); weekday effects | Not traded. Kept as **decay controls** to calibrate how quickly edges die. |

**Contrary evidence is recorded alongside supporting evidence.** For example, the trend-following
case includes Huang, Li, Wang & Zhou (2020), who find weak asset-by-asset predictability, and Kim, Tse
& Wald (2016), who attribute much of TSMOM's alpha to volatility scaling. Those papers shape how F1 is
implemented: diversify across many markets and use volatility-scaled sizing.

---

## 3. Where edges come from

Each strategy must state **who is on the other side of the trade and why they keep taking it.**
Without an answer, the result is presumed to be luck.

| Source | Why it can persist | How it dies | Families |
|---|---|---|---|
| **Risk premium:** you are paid for bearing a risk others avoid (crash risk, liquidity provision in stress) | Rational compensation; limits to arbitrage | Rarely disappears, but crashes occasionally and can be crowded | F2 (in stress), F7, F8 |
| **Behavioural:** under-reaction then herding; over-reaction and reversal | Human biases and institutional frictions are slow to change (Hong & Stein, 1999; Lo, 2004) | Gradually, as more capital exploits it | F1, F2, F4 |
| **Structural / flow:** non-economic, scheduled or forced trades (hedging, rebalancing, fixes, dealer inventory) | The flow is contractual or mandated, and the counterparty is price-insensitive | **Abruptly**, when the structure changes (rules, products, dealer balance sheets) | F3, F5, F6 |
| **Microstructure** (bid-ask bounce, queue effects) | Real but tiny | Costs and latency | Out of scope |

Structural edges are the most valuable to monitor. They can be very strong, but they die quickly when
the structure changes. The overnight drift is the textbook case: the authors attribute its
disappearance to a compression of closing order imbalances.

---

## 4. Required elements before a hypothesis may be built

Fill in `research/templates/edge-card-template.md`. It must contain:

1. **Mechanism:** source type and who pays.
2. **Evidence:** at least one supporting source and any known contrary or decay evidence, with grade.
3. **Prediction:** sign, horizon, markets, and *when it should be stronger* (e.g., "higher on high-volatility days"). This is a mechanism check: if the effect is present but the conditional prediction fails, be suspicious.
4. **Raw effect** (Phase 1 numbers): effect size, t-stat, fraction of years with the predicted sign, gross effect vs costs.
5. **Pre-registration:** allowed building blocks, rule-complexity limits, parameter ranges, exit logic, IS/OOS ranges and funnel thresholds. Any later change is logged as a new trial.

---

## 5. Statistical bars

| Check | Bar | Source |
|---|---|---|
| Trade count | Swing/D1 ≥ 100 trades in development (pooled across markets allowed); intraday ≥ 300 | Standard error of SR (Lo, 2002) |
| t-stat of mean trade (development period) | ≥ 2.0 for Grade A/B with a family prior; ≥ 3.0 for Grade C or anything without a prior | Harvey, Liu & Zhu (2016) |
| Deflated Sharpe Ratio | DSR probability ≥ 0.90, using the logged trial count | Bailey & López de Prado (2014) |
| Probability of Backtest Overfitting (family set) | PBO < 0.5 required; target < 0.25 | Bailey, Borwein, López de Prado & Zhu (2017) |
| Haircut expectation | Plan sizing on ≤ 50% of the backtest's excess return | McLean & Pontiff (2016); Harvey & Liu (2015) |
| Random-entry benchmark | Strategy beats the 95th percentile of random-entry strategies with the same exits and frequency | Aronson (2006); Masters (2020) |

**Tooling note:** SQX computes most performance metrics and robustness tests natively. DSR and PBO
(via CSCV) are easy to compute on the exported daily P&L of a candidate set in a spreadsheet or short
Python script. Arnott, Harvey & Markowitz (2019) is a good checklist to keep open while doing this.

---

## 6. Research hygiene checklist

- [ ] No look-ahead: higher-timeframe and other-symbol inputs use **closed** bars only. Check session-close misalignment; for example, a US500 daily close is later than a GER40 daily close.
- [ ] No holdout contamination: holdout dates are never inside any SQX data range until Phase 4.
- [ ] Every run is logged with its trial count.
- [ ] Costs are at least the 75th-percentile broker spread plus modelled slippage.
- [ ] Results are reported per market and per year, not only in aggregate.
- [ ] Contrary evidence is noted on the edge card.
- [ ] Every parameter or filter added after first results counts as a new trial.
