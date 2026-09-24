# Edge Card — `<HYPOTHESIS-ID>`: `<short name>`

> Fill in sections 1–5 **before** running any SQX build. Sections 6–8 are filled in as results
> arrive. Any change to section 5 after the first build is logged as a new trial in the research log.

| Field | Value |
|---|---|
| Family | F_ |
| Evidence grade | A / B / C / D |
| Owner / date created | |
| Status | proposed / phase-1 / building / funnel / accepted / rejected / parked / live / retired |

## 1. Mechanism

- **Edge source:** risk premium / behavioural / structural-flow / other
- **Who is on the other side, and why do they keep trading this way?**
- **What would make this edge disappear?** (e.g., a structural change, crowding, regulation)

## 2. Evidence

| Supporting source | Key finding | Sample / markets | Peer-reviewed? |
|---|---|---|---|
| | | | |

| Contrary or decay evidence | Key finding |
|---|---|
| | |

## 3. Prediction (falsifiable)

- **Sign and horizon:**
- **Markets where it should work:**
- **Markets where it should NOT work** (a useful negative control):
- **Conditional prediction (mechanism check):** e.g., "stronger when volatility is high"
- **Expected signature:** win rate __, payoff __, skew __, trades/yr __, holding __

## 4. Phase 1 raw-effect study (no optimisation)

| Market | Period | Effect size (gross) | t-stat | % years with predicted sign | Gross / round-trip cost | Conditional prediction holds? |
|---|---|---|---|---|---|---|
| | | | | | | |

**Gate 1 decision:** advance / park. Reason:

## 5. Pre-registration (SQX)

| Item | Setting |
|---|---|
| Template / skeleton | |
| Allowed building blocks | |
| Denied building blocks | |
| Entry conditions (min–max) | |
| Parameter ranges | |
| Exit logic | |
| Order types | |
| Trading options (time range, EOD exit, max trades/day) | |
| Data: symbols, timeframe, precision | |
| IS / OOS-A / OOS-B dates | |
| Holdout dates (locked) | |
| Costs (spread / commission / slippage / swap scenarios) | |
| Ranking / fitness | |
| IS filters | |
| OOS filters | |
| Funnel thresholds (Stages 1–11) | Default doc 03, or list overrides |
| Family-specific falsification tests | |

## 6. Build and funnel results

| Stage | Candidates in | Candidates out | Notes |
|---|---|---|---|
| 0 Build | | | Trials evaluated (for DSR): |
| 1 Correlation de-dup | | | |
| 2 Higher precision | | | |
| 3 Cost stress | | | |
| 4 MC retest | | | |
| 5 MC trade manipulation | | | |
| 6 Other markets / TF | | | |
| 7 WF Matrix | | | |
| 8 Opt. profile / SPP | | | |
| 9 Ablation | | | |
| 10 Random-entry benchmark | | | |
| 11 DSR / PBO | | | DSR = ; PBO (family) = |

**Noise-calibration result:** real survivors __ vs synthetic survivors __ → pass / fail

## 7. Accepted strategies

| Strategy file | Markets | SPP-median Ret/DD | MC 95% max DD | Correlation to existing portfolio |
|---|---|---|---|---|
| | | | | |

## 8. Live notes

| Date | Observation | Action |
|---|---|---|
| | | |
