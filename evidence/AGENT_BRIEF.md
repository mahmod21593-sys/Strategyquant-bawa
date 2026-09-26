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

> **Updated after seven rounds of own-data validation** ([research/validation/REPORT.md](../research/validation/REPORT.md)).
> **The user excludes Treasury strategies,** so CF-07 is out of scope.
>
> - **Build:** **MR-06** (three down closes, US indices, established). It needs weekend holds, so use an FTMO Swing-type account.
> - **Candidate:** **IM-04 noise-area momentum on US100**. It needs a forward test and a second data feed (step 2b): it failed on US500, doesn't survive deflation over ~745 trials, and its 2026 holdout (+1.4 bps/day) is consistent but uninformative.
> - **Optional candidate:** **MR-08**, MR-06's intraday half (09:30 → 16:00 after three down closes), for flat-by-close accounts. It is WEAK by rule, with 33 years of SPY support.
> - **Parked, with their numbers:** everything else, including all round-5 and round-7 negatives ([R5_prop_instrument_negatives.md](edges/R5_prop_instrument_negatives.md), [R7_negatives.md](edges/R7_negatives.md)). Don't re-test them unless the user asks.

| Step | Edge / task | Deliverable |
|---|---|---|
| 0 | Data loading, time-zone conversion, session calendars, cost model | Tested loaders; DST unit tests; cost table per instrument and time of day. **FX/metals/energy: bid/ask or mid data only, or no window touching 16:00–19:00 NY on bid-only data.** **HistData file time = London − 5 h** (EU DST calendar; one hour behind New York in the US/EU gap weeks). Convert through London time, as `data_histdata.local_table` does |
| 1 | **MR-06** on US500 (primary) and US100: signal and entry at 15:55 ET, exit at the next 16:00 close, **volatility-scaled size** (min(2, 1% ÷ 20-day vol)); optional JP225 (entry 5 min before the Tokyo close) and AUS200 | Replicates +15 to +25 bps/trade 2014 → on US500, or stop |
| 2 | **IM-04 noise-area on US100** (card spec: 14-day lookback, 30-min marks, bands from max/min(open, prior close), flip at the opposite band, flat at 16:00; **flat sizing**); the TWAP/VWAP trailing stop as a pre-registered variant; for FTMO Standard funded accounts, the news blackout of the card | Replicates ≈ +3 bps/day net on US100 2014 → ; then a **6-month forward test** before live |
| 2b | **Second-feed check of N3 (X1, pre-registered in A14):** the same code on an independent minute feed (Dukascopy `USATECHIDXUSD`, or the broker's own US100 data), 2014–25, via `run_noise_area.run(..., ses=...)` | Net mean > 0 with one-sided p < 0.05, and the daily correlation with the HistData series. **Not done here** (the feed was throttled) |
| 3 | **Decay controls** (`decay_controls.md`): turn of month, overnight drift 02:00–03:00, FOMC-day premium, FOMC cycle, commodity intraday momentum | The pipeline shows them alive early and faded later (own data did). **This validates the pipeline** |
| 4 | Variants, **pre-registered before running**: MR-06 exit after 2 or 3 days, US30; IM-04 VWAP (with real volume) vs TWAP | Per market × year table; fix one variant per edge before paper trading |
| 5 | Pre-holiday (Ariel) as a small add-on | Net of costs per year; ~9 trades/yr |
| 6 | SQX translation of MR-06 and IM-04 | Spec: entry/exit/time rules, custom blocks ("third down close by 15:55"; "14-day average move from the open at this time of day"; TWAP/VWAP), trading options, cost settings |
| 7 | Prop fit in `tools/propsim` with an EA daily guard, over the **sizing policies** of [REPORT.md](../research/validation/REPORT.md) §16–17.5: fixed exposure vs CPPI (`sizer=lambda a: min(cap, k * a.cushion())`), and a separate funded-stage sizer (`funded_sizer`). Start from the published-terms presets (`ftmo_2step_100k`, `ftmo_1step_100k`, `topstep_50k`: subscription and activation fees, Best Day and consistency gates, partial payouts with caps) and re-check them against the firm's current page. Apply each account type's **holding rules to the book** (weekend holds, news blackout, flat by the close). **Separate accounts per strategy** | EV per attempt and per account-month, pass rate, funded breach rate, each against a zero-edge twin. Own-data reference (published terms, 2014–25 books): US100 4× ≈ $980/month on FTMO 1-Step, $715–770 on FTMO 2-Step; MR-06 3× ≈ $210 on FTMO 2-Step Swing ($73 without weekend holds); Topstep US100 ≈ $124; CPPI k = 10 ≈ 71–82% pass |
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
(MR-06 at 15:55), `prop_mr06_minute.py` (prop simulation) and `data_histdata.py` (HistData loader).
Round 7 added `run_holdout_2026.py` (2026 holdout), `run_round7.py` (families G, incl. MOP TSMOM and
intraday MR-06), `prop_lifecycle_real.py` (published firm terms, holding-rule-aware books) and
`data_histdata.local_table`.

**HistData time stamps** are neither the documented "EST without DST" nor plain New York time. File time
= London − 5 h: New York time except in the US/EU daylight-saving gap weeks, when it is New York − 1 h.
Rounds 2–6 read them as New York time; the affected days are listed in PREREGISTRATION A14.

## Definition of done

Every edge in the work order has a report in the format above. Every replication either matches its
target or is flagged. Every "ADVANCE" edge has an SQX translation spec. No holdout data was used.
