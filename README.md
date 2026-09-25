# Strategyquant-bawa

StrategyQuant deep research: a research-backed plan for finding, validating and combining trading
edges in **StrategyQuant X**, aimed at building diversified portfolios.

## Start here

> **Own-data validation (Sep 2026):** every edge was tested on real data in four pre-registered rounds: daily data back to 1962–1970, 1-minute data for 2010–2025, confirmation on data not seen before, and published edges tested after their papers' samples. See [research/validation/REPORT.md](research/validation/REPORT.md).
>
> **Result:** two edges survived out of sample:
> - **MR-06:** the day after three down closes on US indices, ≈ +20 bps/trade, including with a realistic 15:55 entry.
> - **CF-07:** Treasury end-of-month (long 7–10-yr Treasuries over the last 3 trading days), ≈ +20 bps/month, 24 of 25 years positive.
>
> Intraday momentum, opening-range breakouts, GER40 close momentum, the FX fix windows and the FOMC cycle failed on unseen data, were below realistic costs, were a data artifact, or decayed after publication. For prop challenges, CF-07 plus volatility-scaled MR-06 gives ≈ 73–83% bootstrap pass odds on a two-step challenge (27% with no edge). That is an in-sample sizing estimate, so paper-trade first.
>
> **Handing this to a coding agent?** Start with [evidence/AGENT_BRIEF.md](evidence/AGENT_BRIEF.md) and the [evidence pack](evidence/README.md). Every edge there has been checked against its primary sources, with paper-exact specs and known-answer replication targets.

1. **[Master plan](docs/00-master-plan.md):** goals, principles, phased timeline, decision gates, deliverables.
2. **[Evidence standards](docs/01-evidence-standards.md):** what counts as solid research, the data-mining problem in numbers, evidence grades, statistical bars.
3. **[Edge catalog](docs/02-edge-catalog.md):** nine edge families, each with mechanism, evidence for and against, markets and timeframes, SQX template, falsification tests and hypotheses.
4. **[SQX validation pipeline](docs/03-sqx-validation-pipeline.md):** data and cost setup, builder settings, a 12-stage robustness funnel, the noise-calibration test, DSR/PBO.
5. **[Portfolio construction](docs/04-portfolio-construction.md):** risk budget by family, regime coverage, sizing, stress tests, incubation, monitoring and retirement.
6. **[Prop-firm challenge plan](docs/05-prop-firm-edge-plan.md):** the maths of passing, which edges fit challenge rules, sizing and EA risk guards, and validation with SQX Prop Analytics / Prop Monte Carlo plus `propsim`.
7. **[References](docs/references.md):** full bibliography, with what each source supports.

## Working files

| File | Purpose |
|---|---|
| [research/hypothesis-register.csv](research/hypothesis-register.csv) | 43 hypotheses with ID, family, grade, references, markets, SQX skeleton, Phase 1 test, priority, prop-challenge fit and status |
| [research/templates/edge-card-template.md](research/templates/edge-card-template.md) | Fill in one per hypothesis before building |
| [research/templates/strategy-acceptance-checklist.md](research/templates/strategy-acceptance-checklist.md) | Sign-off checklist per strategy |
| [research/templates/research-log-template.csv](research/templates/research-log-template.csv) | Log every run. The trial count feeds the Deflated Sharpe Ratio |
| [tools/edgelab/](tools/edgelab/README.md) | Phase 1 raw-edge studies on OHLC bar exports (intraday momentum, range breakouts, IBS, turn of month, compression, breakouts, variance ratios, time-of-day profile), each printing the Gate 1 advance/park verdict against costs (standard-library Python) |
| [tools/propsim/](tools/propsim/README.md) | Prop-firm challenge simulator for SQX trade lists: multi-phase rules, trailing drawdowns, daily-loss limits, portfolio combination, position-size scan, funded-stage EV (standard-library Python) |

## Edge families at a glance

| ID | Family | Literature grade | Own-data result | Typical TF |
|---|---|---|---|---|
| F1 | Time-series momentum / trend following | A | Validated on ETFs, but equal to vol-scaled buy-and-hold | D1, H4 |
| F2 | Short-term mean reversion in equity indices | B (strong) | **MR-06 validated (US only)**; IBS, 5-day low and non-US not | D1 |
| F3 | Intraday momentum and opening-range breakout | B | Not validated / below costs (2010–2025 minute data) | M5–M30 |
| F4 | Volatility-compression breakout | B/C | Untested | H1–D1 |
| F5 | Calendar and flow effects (indices, Treasuries) | B (rebalancing) / D (turn of month) | **Treasury end-of-month validated**; pre-holiday validated (small); turn of month, overnight drift, FOMC day and FOMC cycle decayed; rebalancing weak | D1 |
| F6 | FX session and fix flows | B+ | Real 2004–18 in clean data; gone after 2019 | M15–H1 |
| F7 | Carry-aware FX | A / B | Untested | D1 |
| F8 | Intermarket and regime-conditioned variants | B/C | Untested | D1, H4 |
| F9 | Session-range mean reversion (exploratory) | C | Untested | M15–H1 |

## Core principle

SQX can search millions of rule combinations, so a great-looking backtest is expected even when there
is no edge. This plan uses SQX to **refine and try to kill** hypotheses that come from published
research, not to generate them. Every strategy must have a mechanism, evidence, a raw-effect
measurement in our own data, and a pre-registered pass through the validation funnel.
