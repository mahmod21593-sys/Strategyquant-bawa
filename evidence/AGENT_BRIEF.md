# Brief for the coding agent

> Paste this file, plus the repository, into the coding agent as its task.

## Goal

Turn the verified evidence in `evidence/edges/` into **tested, StrategyQuant X-ready strategy
specifications** for a portfolio aimed at passing prop-firm challenges (see `docs/05-prop-firm-edge-plan.md`).
Each edge must:

1. **Replicate its source paper first**, on the paper's own instrument and sample, using the paper-exact spec in its card.
2. Only then extend to the user's instruments, costs and post-publication data.
3. Pass Gate 1 (predicted sign in ≥ 60% of years, gross effect > 2× round-trip cost, ≥ 2 markets), or be parked with its numbers.

## Hard rules

1. **Don't invent parameters.** Use the values in each card's "Paper-exact spec". Where a card says to read a detail from the paper (e.g. CF-02 band width), read it from the PDF. Don't guess.
2. **Replicate before you extend.** If a replication target isn't met (wrong sign, or magnitude off by more than 2×), **stop and report**. Don't tune until it matches.
3. **No look-ahead.** Session-anchored values use only bars that have closed. Cross-market signals respect different close times (US500 closes after GER40).
4. **Time zones are real time zones.** Convert via IANA zones (`America/New_York`, `Europe/London`, `Asia/Tokyo`). US/EU daylight-saving mismatch weeks must be handled. Include tests for March and November transition weeks.
5. **Holdout locked.** The most recent 2–3 years of the user's data stay unused until the user asks for the final test.
6. **Pre-register variants.** Any threshold or grid (e.g. Rosa-style signal threshold, ORB probe length) is fixed before running. Log every run with the number of variants tried (`research/templates/research-log-template.csv`).
7. **Costs at the actual trade times.** Spreads at the open, the close and the fixes are wider than daily averages. Report gross and net.
8. **Report by market × year and by regime:** pre/post publication, and post-2022 (0DTE era) for US intraday edges. Never report only a pooled number.
9. **V3 claims are leads, not facts.** Don't cite them as evidence in outputs.

## Work order

| Step | Edge / task | Deliverable |
|---|---|---|
| 0 | Data loading, time-zone conversion, session calendars, cost model | Tested loaders; DST unit tests; cost table per instrument and time of day |
| 1 | **Decay controls** (`decay_controls.md`): turn of month, pre-FOMC, overnight drift | The pipeline shows them alive in-sample and faded later. **This validates the pipeline** |
| 2 | **IM-01** Gao and Baltussen replications, then the Rosa threshold variant | Replication table vs targets; post-2013 / post-2022 splits; cross-market |
| 3 | **IM-02** ORB variants A (Zarattini), B (TORB), C (Holmberg) | Replication of variant A trade count and win rate; net-of-slippage results per market |
| 4 | **MR-01** IBS / N-day low on US indices, then other indices separately | Bucket tables; excess-over-drift; volatility-tercile check |
| 5 | **FX-01** dollar fix reversals (W1–W4 windows) | Replication of the signs for 1999–2018; post-2018; net of the user's costs |
| 6 | **IM-04** noise-area momentum | Replication vs Table 2 (Sharpe ≈ 1.2 with the VWAP stop) |
| 7 | FX-02, CF-02, VB-02 | Gate 1 results |
| 8 | TF-01 (portfolio sleeve, not prop) | MOP-style replication on the available futures set |
| 9 | For every edge that passes Gate 1: SQX translation | Spec listing entry/exit/time rules, **custom blocks needed**, trading options, cost settings |
| 10 | Prop fit: combine passing edges' OOS trade lists in `tools/propsim` | Pass probability, days to pass, recommended size, with an EA daily guard |

## Per-edge report format

```
## <ID> — <name>
Replication: target vs obtained (table) — PASS / FAIL
Extension (user data): per market × year table: n, gross bps/trade, net bps/trade, t-stat, % years positive
Regime splits: pre/post publication; post-2022 (US intraday)
Mechanism check: <card's mechanism test> — result
Gate 1: ADVANCE / PARK (reasons)
Variants tried (count) and which were pre-registered
SQX translation (if ADVANCE): blocks, custom blocks, trading options, costs
Open issues
```

## Existing code in the repo (optional)

`tools/edgelab` already implements several Phase 1 studies (Gao/Baltussen windows, stop-entry range
breakouts, IBS, turn of month, compression, breakouts, variance ratios, time-of-day profiles).
`tools/propsim` simulates prop-firm rules. Use, extend or replace them.

Known gaps: Zarattini first-candle ORB (variant A), the noise-area model, the FX fix-window study,
rebalancing signals, and MOP volatility-scaled TSMOM are **not** implemented.

## Definition of done

Every edge in the work order has a report in the format above. Every replication either matches its
target or is flagged. Every "ADVANCE" edge has an SQX translation spec. No holdout data was used.
