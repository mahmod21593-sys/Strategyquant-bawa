# Strategyquant-bawa

StrategyQuant deep research: a research-backed plan for finding, validating and combining trading
edges in **StrategyQuant X**, aimed at building diversified portfolios.

## Start here

> **Own-data validation (Sep 2026):** about 750 pre-registered hypotheses and 5,306 strategy variants tested in eleven rounds: daily data from 1962–1970, 1-minute data 2010–2025 on 24 prop instruments, published edges tested after their papers' samples, and an untouched 2026 holdout. See [research/validation/REPORT.md](research/validation/REPORT.md).
>
> **Result (no Treasury strategies, per the user):**
> - **Edge family (round 9):** short-term **index reversal** (IBS, RSI(2), down-close streaks and N-day lows on US500, US100, US30, US2000 and JP225). It holds across 864 variants under data-snooping control: SPA p = 0.03, overfitting probability 0.19, walk-forward t = 2.1. Traded as an ensemble it has Sharpe 0.9–1.0 in 2013–26, and a portfolio chosen only from pre-2020 data earned Sharpe 0.69 out of sample. Every variant: [research/strategy_library.csv](research/strategy_library.csv).
> - **Established:** **MR-06**, the day after three down closes on US indices, ≈ +20 bps/trade with a realistic 15:55 entry. It's one member of that family; about half its edge is earned in the next session.
> - **Candidate:** **noise-area intraday momentum on US100**, +3.0 bps/day net, Sharpe 0.73. It passed its own test and robustness checks but not deflation over all trials, and its 2026 holdout (+1.4 bps/day) is consistent but too short to confirm. Paper-trade it first.
> - **Real but not a prop edge:** multi-asset trend following (Sharpe 0.62 after publication, WEAK after Holm); CFD financing eats it.
>
> **Round 10** tested seven more families (3,768 variants: reversal outside equities, per-market trend, index-pair relative value, calendar, crypto trend, reversal on more indices, cross-sectional stock reversal). None adds an independent edge.
>
> **Round 11** answered "can StrategyQuant X trade it, in a prop account, on FX, indices or metals?"
> - **The reversal ensemble survives an SQX build.** An M5 chart with daily cash-session conditions, entering at 15:55, keeps 82–87% of the research Sharpe on CFD quotes, and it doesn't need weekend holds.
> - **The US100 rule can be built from native SQX blocks:** stop orders at the open ± 0.5 × prior range.
> - **FX and metals:** four more families (292 variants) found no tradeable edge after costs.
> - **How to build each edge:** [evidence/edges/SQX_build_matrix.md](evidence/edges/SQX_build_matrix.md).
>
> Everything else failed out of sample or after costs. That covers intraday momentum on other markets, ORBs, FX fixes, commodity, crude-oil and Bitcoin intraday rules, calendar effects, a 653-candidate time-of-day scan, and round 7's further families (Halloween, options expiration, volatility management, breakouts, gap fades, crypto funding, index momentum, and the earnings premium on single-stock CFDs).
>
> **Prop playbook (rounds 6–7):** how you size, and where, matter more than which edge you pick.
> - **Fixed 3–4× exposure** maximises money per account-month. On published terms: US100 rule on **FTMO 1-Step ≈ $980**, MR-06 on an **FTMO 2-Step Swing** account ≈ $210.
> - **Cushion (CPPI) sizing** maximises the pass probability: 71–82% against 13–22% for zero edge, but it is slow.
> - **Flat-by-close futures firms** (Topstep and others) can't hold MR-06, and pay little for the US100 rule.
>
> See the [prop plan](docs/05-prop-firm-edge-plan.md).
>
> **Curated summary of everything found:** [research/FINDINGS.md](research/FINDINGS.md): the edge book, where to trade each edge, what paper trading can and can't show, what not to build, and how far to trust it.
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
| [research/hypothesis-register.csv](research/hypothesis-register.csv) | 58 hypotheses (plus the 653-candidate scan) with ID, family, grade, references, markets, SQX skeleton, Phase 1 test, priority, prop-challenge fit and status |
| [research/templates/edge-card-template.md](research/templates/edge-card-template.md) | Fill in one per hypothesis before building |
| [research/templates/strategy-acceptance-checklist.md](research/templates/strategy-acceptance-checklist.md) | Sign-off checklist per strategy |
| [research/templates/research-log-template.csv](research/templates/research-log-template.csv) | Log every run. The trial count feeds the Deflated Sharpe Ratio |
| [tools/edgelab/](tools/edgelab/README.md) | Phase 1 raw-edge studies on OHLC bar exports (intraday momentum, range breakouts, IBS, turn of month, compression, breakouts, variance ratios, time-of-day profile), each printing the Gate 1 advance/park verdict against costs (standard-library Python) |
| [tools/propsim/](tools/propsim/README.md) | Prop-firm challenge simulator for SQX trade lists: multi-phase rules, trailing drawdowns, daily-loss limits, portfolio combination, position-size scan, funded-stage EV (standard-library Python) |

## Edge families at a glance

| ID | Family | Literature grade | Own-data result | Typical TF |
|---|---|---|---|---|
| F1 | Time-series momentum / trend following | A | Real (Sharpe 0.62 on prop instruments after 2012, WEAK after Holm), diversifying; uneconomic in CFD prop accounts; cross-index momentum fails | D1, H4 |
| F2 | Short-term mean reversion in equity indices | B (strong) | **MR-06 validated (US only)**; IBS, 5-day low and non-US not | D1 |
| F3 | Intraday momentum and opening-range breakout | B | Noise-area momentum works on **US100 only** (candidate); last-30-min, ORB, GER40, commodity, crude, Asian and Bitcoin versions fail | M5–M30 |
| F4 | Volatility-compression breakout | B/C | Williams breakout weak (failed holdout), NR7 and Asian-range breakout fail after costs | H1–D1 |
| F5 | Calendar and flow effects | B (rebalancing) / D (turn of month) | Pre-holiday validated (small); Treasury end-of-month validated but excluded by the user; turn of month, overnight drift, FOMC day, FOMC cycle and every hour-of-day/day-of-week scan candidate failed | D1 |
| F6 | FX session and fix flows | B+ | Real 2004–18 in clean data; gone after 2019 | M15–H1 |
| F7 | Carry-aware FX | A / B | Not tested: multi-week holds are banned on FTMO Standard funded accounts, and swap mark-ups eat the premium | D1 |
| F8 | Intermarket and regime-conditioned variants | B/C | VIX-conditioned MR, volatility management and crypto funding fail | D1, H4 |
| F9 | Session-range mean reversion (exploratory) | C | Not tested directly: mirror images of the tested breakouts and noise-area rules | M15–H1 |

## Core principle

SQX can search millions of rule combinations, so a great-looking backtest is expected even when there
is no edge. This plan uses SQX to **refine and try to kill** hypotheses that come from published
research, not to generate them. Every strategy must have a mechanism, evidence, a raw-effect
measurement in our own data, and a pre-registered pass through the validation funnel.
