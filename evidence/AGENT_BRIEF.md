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

> **Updated after five rounds of own-data validation** ([research/validation/REPORT.md](../research/validation/REPORT.md)).
> **The user excludes Treasury strategies,** so CF-07 is out of scope.
>
> - **Build:** **MR-06** (three down closes, US indices, established).
> - **Candidate:** **IM-04 noise-area momentum on US100**. It needs a forward test, because it failed on US500 and doesn't survive deflation over all ~730 trials.
> - **Parked, with their numbers:** everything else, including all round-5 commodity, crude-oil, crypto and time-of-day rules ([R5_prop_instrument_negatives.md](edges/R5_prop_instrument_negatives.md)). Don't re-test them unless the user asks.

| Step | Edge / task | Deliverable |
|---|---|---|
| 0 | Data loading, time-zone conversion, session calendars, cost model | Tested loaders; DST unit tests; cost table per instrument and time of day. **FX/metals/energy: bid/ask or mid data only, or no window touching 16:00–19:00 NY on bid-only data** |
| 1 | **MR-06** on US500 (primary) and US100: signal and entry at 15:55 ET, exit at the next 16:00 close, **volatility-scaled size** (min(2, 1% ÷ 20-day vol)); optional JP225 (entry 5 min before the Tokyo close) and AUS200 | Replicates +15 to +25 bps/trade 2014 → on US500, or stop |
| 2 | **IM-04 noise-area on US100** (card spec: 14-day lookback, 30-min marks, bands from max/min(open, prior close), flip at the opposite band, flat at 16:00); the TWAP/VWAP trailing stop as a pre-registered variant | Replicates ≈ +3 bps/day net on US100 2014 → ; then a **6-month forward test** before live |
| 3 | **Decay controls** (`decay_controls.md`): turn of month, overnight drift 02:00–03:00, FOMC-day premium, FOMC cycle, commodity intraday momentum | The pipeline shows them alive early and faded later (own data did). **This validates the pipeline** |
| 4 | Variants, **pre-registered before running**: MR-06 exit after 2 or 3 days, US30; IM-04 VWAP (with real volume) vs TWAP | Per market × year table; fix one variant per edge before paper trading |
| 5 | Pre-holiday (Ariel) as a small add-on | Net of costs per year; ~9 trades/yr |
| 6 | SQX translation of MR-06 and IM-04 | Spec: entry/exit/time rules, custom blocks ("third down close by 15:55"; "14-day average move from the open at this time of day"; TWAP/VWAP), trading options, cost settings |
| 7 | Prop fit in `tools/propsim` with an EA daily guard: MR-06 on a two-step preset (no time limit); IM-04 separately (fast attempts). **Don't put both in one account** (it lowers the pass probability) | Pass probability and days to pass; own-data estimates: MR-06 2× ≈ 60% (~21 months), IM-04 2× ≈ 40% (~6 months), TWAP-stop 3× ≈ 52% (post hoc) |
| 8 | Optional, only if asked: replicate parked edges on the user's broker data | Report in the format below; compare with the card numbers |

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

`research/validation` contains the code that produced every own-data number: `run_noise_area.py`
(IM-04), `run_scan.py` (the 653-candidate scan), `run_round5.py` (round-5 literature tests), `prop_noise.py` and
`prop_round5.py` (Treasury-free prop books), `run_round4.py`, `round4_followup.py`, `run_histdata.py`
(minute-data rules, including the Zarattini first-candle ORB and the 30-min ORB), `run_round3.py`
(MR-06 at 15:55), `prop_mr06_minute.py` (prop simulation) and `data_histdata.py` (HistData loader;
its time stamps are New York local time **with** DST, contrary to HistData's documentation).
Not implemented anywhere: the noise-area model, rebalancing signals, MOP volatility-scaled TSMOM.

## Definition of done

Every edge in the work order has a report in the format above. Every replication either matches its
target or is flagged. Every "ADVANCE" edge has an SQX translation spec. No holdout data was used.
