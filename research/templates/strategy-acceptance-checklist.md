# Strategy Acceptance Checklist — `<strategy name>` (`<HYPOTHESIS-ID>`)

Default thresholds from [doc 03](../../docs/03-sqx-validation-pipeline.md). Where the edge card
pre-registered an override, write the override value next to the item.

## A. Provenance

- [ ] Edge card complete (mechanism, evidence, prediction, Phase 1 study, pre-registration)
- [ ] Phase 1 gate passed (predicted sign in ≥ 60% of years; gross effect > 2× costs; ≥ 2 markets, or ≥ 3 for Grade C)
- [ ] All trials that led to this strategy are logged in the research log
- [ ] Strategy statistics match the family signature (doc 02)

## B. Data and costs

- [ ] Data QA passed for every symbol used
- [ ] Costs = 75th-percentile spread + commission + slippage; swap scenarios bracketed
- [ ] Holdout never loaded during development

## C. Build filters

- [ ] IS: trades ≥ 100 (swing) / ≥ 300 (intraday); PF ≥ 1.3 / 1.2; Ret/DD ≥ 3; average trade ≥ 3× cost
- [ ] OOS-A and OOS-B: PF ≥ 1.1; Ret/DD per year ≥ 50% of IS; ≥ 30 trades each
- [ ] ≤ 3 entry conditions; ≤ 6 free parameters; shift ≤ 3

## D. Robustness funnel

- [ ] Stage 1: not a near-duplicate (ρ ≤ 0.7 vs other candidates)
- [ ] Stage 2: higher precision — PF drop ≤ 15%, Ret/DD drop ≤ 25%
- [ ] Stage 3: costs ×1.5 → PF ≥ 1.1; costs ×2 → still profitable
- [ ] Stage 4: MC retest (≥ 200 runs) at 95% — profit > 0; Ret/DD ≥ 50% of original; max DD ≤ 2× original
- [ ] Stage 5: MC trade manipulation — 95th-percentile DD within the risk budget
- [ ] Stage 6: other markets / timeframes — family rule met (e.g., F1 ≥ 60% of basket; F2 ≥ 4/6 indices; F3 ≥ 3 markets)
- [ ] Stage 7: WF Matrix — ≥ 60–70% of cells pass, contiguous cluster
- [ ] Stage 8: parameter neighbourhood ≥ 70% profitable; SPP median meets the minimum
- [ ] Stage 9: ablation — every condition and filter adds OOS value
- [ ] Stage 10: beats the 95th percentile of the random-entry benchmark
- [ ] Stage 11: DSR ≥ 0.90 (with logged N); family PBO < 0.5
- [ ] Template passed the noise-calibration test

## E. Family-specific falsification tests (from doc 02)

- [ ] Test 1:
- [ ] Test 2:
- [ ] Mechanism / conditional prediction holds

## F. Portfolio fit

- [ ] Daily-P&L correlation with each existing strategy ≤ 0.5; average with the portfolio ≤ 0.3
- [ ] Drawdown overlap with the existing portfolio is acceptable
- [ ] Family / asset-class / market caps are not breached after adding

## G. Deployment readiness

- [ ] Exported code reproduces SQX trades in the target platform (≥ 50 trades reconciled)
- [ ] Monte Carlo 5th / 50th / 95th bands saved for live monitoring
- [ ] Retirement thresholds written down (doc 04 §8)

**Decision:** accept / reject / park   **Date:**   **Signed off by:**
