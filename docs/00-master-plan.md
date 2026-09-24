# StrategyQuant X Edge Research Plan — Master Plan

> **Goal:** build a live-tradable portfolio of **15–30 robust, low-correlation StrategyQuant X (SQX)
> strategies** covering **at least 5 edge families, 3 asset classes and 3 timeframes**, where every
> strategy can be traced back to (1) an economic reason why the edge exists, (2) published evidence,
> (3) a measurement of the raw effect in *our own* data, and (4) a validation funnel whose pass/fail
> rules are written down before any build runs.

Companion documents:

| Doc | What it covers |
|---|---|
| [01-evidence-standards.md](01-evidence-standards.md) | How research is graded, the data-mining problem in numbers, where edges come from, statistical bars |
| [02-edge-catalog.md](02-edge-catalog.md) | Nine edge families: mechanism, evidence for and against, markets and timeframes, SQX template, falsification tests, hypotheses |
| [03-sqx-validation-pipeline.md](03-sqx-validation-pipeline.md) | Data and cost setup, builder configuration, robustness funnel with thresholds, noise-calibration test, statistical checks |
| [04-portfolio-construction.md](04-portfolio-construction.md) | Risk budget by family, correlation and regime coverage, sizing, portfolio stress tests, incubation, monitoring and retirement |
| [references.md](references.md) | Full bibliography, with what each source supports in this plan |
| [../research/hypothesis-register.csv](../research/hypothesis-register.csv) | Every hypothesis with an ID, grade, priority and status |
| [../research/templates/](../research/templates/) | Edge card, acceptance checklist and research log templates |

---

## 1. Why this plan is built the way it is

SQX is a **data-mining engine**. The genetic builder can evaluate millions of rule combinations, and
with that many trials some backtests will look excellent purely by chance. With 10 years of data, the
best of 10,000 strategies that have **zero** true edge is expected to show an annualised Sharpe of
about **1.2** (Bailey & López de Prado, 2014; see the table in doc 01). Academic reviews of technical
trading reach the same conclusion: once data snooping and costs are accounted for, most apparent rule
profits disappear (Sullivan, Timmermann & White, 1999; Bajgrowicz & Scaillet, 2012).

This plan therefore uses SQX as a **hypothesis refiner, not a hypothesis generator**:

1. **Theory first.** Pick an edge that has a documented mechanism and published evidence.
2. **Measure the raw effect.** Confirm the effect exists in our data, on our instruments and after our costs, before building anything.
3. **Mine inside a narrow box.** Limit SQX's building blocks, rule complexity and parameter ranges to those that express that one edge.
4. **Try to kill it.** Run a pre-registered robustness funnel, including a noise-calibration test that measures how often our own process "finds" edges in random data.
5. **Diversify on purpose.** Combine survivors across families whose return drivers and skew differ.
6. **Expect decay.** Monitor live performance against pre-defined statistical bands, and keep a standing research pipeline to replace strategies that stop working.

### What the evidence says to expect

| Finding | Source | Implication for us |
|---|---|---|
| Published return predictors earn ~26% less out of sample and ~58% less after publication | McLean & Pontiff (2016) | Assume roughly half of any paper's edge survives. Plan position sizes on the haircut number. |
| Daily technical rules on S&P 500 were unprofitable from the early 1990s, but the same models on 30-minute data still averaged 7.2%/yr gross in 1983–2007 | Schulmeister (2009) | Edges move to other timeframes. Test each hypothesis on several timeframes. |
| FX technical-rule profits declined over time | Olson (2004); Neely, Weller & Ulrich (2009) | FX-only trend systems are weak. Trend belongs in a multi-asset basket. |
| Pre-FOMC drift essentially disappeared after 2015 | Kurov, Wolfe & Gilbert (2021) | Documented edges can die completely. |
| US equity-futures "overnight drift" (2–3am ET) earned ~3.7%/yr in 1998–2020 and ~0 since 2021 | Boyarchenko, Larsen & Whelan (2023); NY Fed Liberty Street (2026) | Structural or flow edges vanish when the structure changes. Monitoring is required. |
| Markets are adaptive; edges wax and wane with participants and conditions | Lo (2004) | Retirement rules and continuous research are part of the system, not an afterthought. |

---

## 2. Scope

**In scope:** single-instrument strategies (optionally using other symbols or timeframes as signal
inputs) that SQX can build, backtest and export to your platform (MT4/MT5, TradeStation/MultiCharts,
NinjaTrader and others) on:

- **FX:** majors and liquid crosses
- **Equity indices:** US500, US100, US30, US2000, GER40, UK100, EU50, JP225, AUS200 (as CFDs or futures)
- **Metals and energy:** XAUUSD, XAGUSD, WTI, Brent (natural gas optional)
- **Bonds:** if trading futures (ZN, ZB, Bund)
- **Crypto:** BTC and ETH, optional, as a separate sleeve

**Out of scope, and why:**

- **Cross-sectional stock factors** (value, cross-sectional momentum, quality). These need universe-wide ranking, which is not native to SQX single-instrument strategies.
- **Options and volatility risk premia.** SQX does not model options.
- **HFT and microstructure.** Latency and queue position dominate at those horizons, and costs overwhelm the edge.
- **True multi-leg pairs or stat-arb.** SQX strategies place orders on the main chart. Other charts can be signal sources, which is covered in family F8.

---

## 3. Edge families covered

The goal is return drivers that are **economically different**, not just different indicators.

| ID | Family | Edge source | Typical TF | Skew | Evidence grade |
|---|---|---|---|---|---|
| F1 | Time-series momentum / trend following | Behavioural under-reaction and herding; risk transfer | D1, H4 | + | **A** |
| F2 | Short-term mean reversion in equity indices | Liquidity provision; index-arbitrage-driven negative autocorrelation | D1, H4 | − | **B** (strong) |
| F3 | Intraday momentum and opening-range breakout | Structural: dealer gamma hedging, late-informed flow | M5–M30 | + | **A** (last-half-hour) / **B** (ORB) |
| F4 | Volatility-compression breakout | Volatility clustering; stop cascades | H1–D1 | + | **B/C** |
| F5 | Calendar and flow effects (indices) | Structural: month-end flows, rebalancing | D1 | − / mixed | **A−/B** |
| F6 | FX session and fix flows | Structural: time-zone order flow, hedging at London fix | M15–H1 | mixed | **B** |
| F7 | Carry-aware FX | Risk premium (crash risk) | D1 | − | **A** (premium) / **B** (implementation) |
| F8 | Intermarket and regime-conditioned variants | Risk premium in stress; cross-asset information flow | D1, H4 | mixed | **B/C** |
| F9 | Session-range mean reversion (exploratory) | Liquidity provision in quiet sessions | M15–H1 | − | **C** |

Families F1, F3 and F4 have positive skew and tend to profit when markets move. F2, F5, F7 and F9
have negative skew and tend to profit when markets are quiet or recovering. Combining the two groups
is the core diversification idea (see doc 04).

---

## 4. Phased work plan

The timeline assumes about 10–15 hours per week and one SQX licence. Phases overlap: one family can be
in the build phase while another is in the funnel.

### Phase 0 — Foundation (Weeks 1–2)

| Task | Output |
|---|---|
| Decide platform and broker (CFD/MT5 vs futures/TS/NT), markets actually tradable, account size, max drawdown tolerance | `decisions.md` (see §6) |
| Acquire data. FX: tick or M1 (e.g., Dukascopy) and broker data. CFDs: broker history. Futures: back-adjusted continuous contracts from a vendor | Data inventory |
| Data QA per symbol: gaps, spikes, session times, DST handling, Sunday bars, roll method | Data QA report per symbol |
| Standardise server time (e.g., New York close = GMT+2/+3 with DST) so D1 bars are 5 per week | SQX Data Manager configuration |
| Build a cost model: 75th-percentile spread (not the minimum), commission, slippage for market and stop orders, swap scenarios | `cost-model` table (doc 03 §1) |
| **Lock the holdout.** Remove the most recent 2–3 years from every SQX data range | Holdout dates recorded in the research log |
| Set up the hypothesis register, research log (counts every build), naming convention and databank layout | `research/` folder |

**Gate 0:** data QA passed, costs documented, holdout locked.

### Phase 1 — Raw edge measurement (Weeks 2–4)

The question for each hypothesis is **"does the effect exist in my data, at a size that beats my
costs?"** Answer it with the simplest fixed rule or statistic, with **no optimisation**. Use SQX
AlgoWizard or a manually defined strategy, or a spreadsheet or Python script on exported bars.

| Study | Tests hypotheses in | Method |
|---|---|---|
| Autocorrelation and variance ratio by timeframe (M15 → W1) per market | F1, F2, F9 | Lo & MacKinlay (1988) variance ratio. A ratio above 1 indicates trending; below 1 indicates mean reversion. |
| Time-of-day return and volatility profile (per hour, per weekday) | F3, F4, F6, F9 | Mean return, volatility and t-stat per hour (Andersen & Bollerslev, 1997; Ranaldo, 2009) |
| First-period return → last-30-minute return regression | F3 | Gao, Han, Li & Zhou (2018) specification |
| Forward returns after N-bar-high breaks vs unconditional | F1, F4 | Event study with 1/5/10/20-bar forward returns |
| Forward range after compression (NR7, ATR ratio) vs baseline | F4 | Tests whether volatility expansion is predictable in our data |
| Next-day return by IBS bucket and after N-day lows, above and below the 200-day MA | F2 | Conditional mean vs unconditional, per index |
| Turn-of-month window vs other days; month-end performance vs month-to-date moves | F5, F6 | Calendar event study |

**Gate 1:** a hypothesis advances only if the raw effect has the **predicted sign in at least 60% of
calendar years**, a **gross effect above 2× round-trip costs**, and appears in **at least 2 markets**
(or at least 3 for Grade C). Everything else is parked in the register with its numbers, not deleted.

### Phase 2 — Constrained building (Weeks 4–10)

Work through the families in priority order, each with its own template (doc 02) and a pre-registered
funnel configuration (doc 03).

| Order | Family | Why this order |
|---|---|---|
| 1 | F1 Trend following | Strongest evidence, lowest cost sensitivity, crisis diversifier |
| 2 | F2 Index mean reversion | Negative correlation to F1 in normal regimes; strong index evidence |
| 3 | F3 Intraday momentum / ORB | Peer-reviewed mechanism; flat overnight, so no swap or gap risk |
| 4 | F5 Calendar/flow | Few parameters, cheap to test, uncorrelated timing |
| 5 | F4 Vol-compression breakout | Broad market coverage; complements F3 |
| 6 | F6 FX session and fix | Cost-sensitive; needs good FX data |
| 7 | F7 Carry-aware FX | Needs a custom rate-differential data series |
| 8 | F8 / F9 Exploratory | Only after the core sleeves exist |

Per family, budget about 1 week for template and custom blocks, 1 week for builds, and the funnel runs
alongside the next family's build.

**Gate 2 (per family):** at least 3 strategies survive the full funnel **and** the family's candidate
set has PBO < 0.5 (target < 0.25), **and** the noise-calibration pass rate is below 10% of the
real-data pass rate.

### Phase 3 — Robustness funnel and selection (Weeks 6–12, overlapping)

Run the funnel in doc 03 §4. Record every pass and every failure. Expect **95–99% attrition** of raw
builds; that is the system working, not failing.

### Phase 4 — Portfolio construction and holdout test (Weeks 10–14)

- Assemble the portfolio from survivors using the rules in doc 04.
- Run the **holdout test once**, on the final portfolio and each component. Log it.
- If the portfolio fails the holdout, do not tweak and re-test. Go back to Phase 2 with a **new** hypothesis or with new data.

**Gate 4:** the holdout portfolio has positive return, a max drawdown within the 95th-percentile Monte Carlo band, and no single sleeve responsible for more than 50% of profit.

### Phase 5 — Incubation and staged deployment (Months 4–7)

- 2–3 months on demo or at minimum size (Davey, 2014). Check execution parity: exported code vs SQX backtest trade by trade, real slippage vs modelled, and spreads at entry times.
- Scale capital 25% → 50% → 100% as live results stay inside the Monte Carlo bands.

### Phase 6 — Continuous research loop (ongoing)

- **Monthly:** live vs expected bands; flag strategies approaching retirement thresholds.
- **Quarterly:** a research sprint (new hypotheses, rebuild the weakest family); rebalance risk budgets.
- **Annually:** re-run the Phase 1 raw-edge studies on all live families to detect decay early.

---

## 5. Deliverables checklist

- [ ] Data QA reports and cost model per symbol
- [ ] Phase 1 raw-edge study results for every hypothesis in the register
- [ ] One SQX template (and custom blocks where needed) per family
- [ ] Custom Project (build → funnel) per family, saved and versioned
- [ ] Noise-calibration results per template
- [ ] Edge card + completed acceptance checklist for every surviving strategy
- [ ] Portfolio report: allocation, correlation matrix, regime table, MC drawdown bands, stress periods
- [ ] Holdout test log (run once)
- [ ] Live monitoring sheet with retirement thresholds per strategy

## 6. Decisions to make before Phase 0 ends

| Decision | Default if undecided |
|---|---|
| Platform (MT5 CFDs vs futures on TS/NT/MultiCharts) | MT5 CFDs for FX/indices/metals. Futures data is used for research where available, because it has cleaner sessions and history. |
| Markets | 8 FX pairs, 6 indices, 2 metals, 1–2 energy |
| Starting risk per trade | 0.25% of equity per strategy during incubation |
| Portfolio max drawdown tolerance | 20% (sizes are derived from this; doc 04 §6) |
| Holdout | Most recent 2.5 years |
| Research tooling outside SQX | Spreadsheet for Phase 1; optional Python for PBO/DSR and the noise series |

## 7. Research KPIs

| KPI | Target |
|---|---|
| Hypotheses with a completed Phase 1 study | 100% before any build |
| Families with at least 3 funnel survivors | ≥ 5 |
| Average pairwise daily-P&L correlation in the portfolio | ≤ 0.2 |
| Portfolio Ret/DD (holdout, after costs) | ≥ 1.0, judged on the haircut expectation, not the backtest |
| Live results inside the MC band after 6 months | ≥ 80% of strategies |
