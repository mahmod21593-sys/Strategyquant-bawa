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

> **Updated after eleven rounds of own-data validation** ([research/validation/REPORT.md](../research/validation/REPORT.md)). **Curated summary:** [research/FINDINGS.md](../research/FINDINGS.md).
> **How to build each edge in SQX (round 11):** [edges/SQX_build_matrix.md](edges/SQX_build_matrix.md). It has the chart and session set-up, trading options, expected results under each build, prop sizing, and the checks to run first.
> **The user excludes Treasury strategies,** so CF-07 is out of scope.
>
> - **Build first:** the **index-reversal family as an ensemble** ([REV card](edges/REV_index_reversal_family.md)).
>   - It is the only edge family after multiple-testing control (round 9), and it survives the way SQX trades it (round 11).
>   - **Build:** M5 chart plus a D1 cash-session chart; signal and market entry at 15:55 NY.
>   - **Variants:** the 141 positive under all three builds ([research/sqx_implementation_grid.csv](../research/sqx_implementation_grid.csv)).
>   - **MR-06** (three down closes) is one member.
>   - **Weekend holds are not needed** (R2: same Sharpe), so FTMO Standard is fine.
>   - **Size it for survival:** signals cluster in crashes.
>   - **Hold US legs through the next session** (round 12): overnight-only exits give back most of the edge. JP225 may exit at the next Tokyo open.
>   - **Regime (rounds 15–16):** keep entries in stress (US500 ≥ 9% below its 60-day high, or VIX ≥ VIX3M), where most of the US edge is. **No regime filter and no VIX data:** round 16 withdrew the JP225 stress filter as look-ahead.
> - **Candidate:** **IM-04 momentum on US100, built from native SQX blocks** (R3).
>   - **Rule:** at 09:30, stop orders at the open ± 0.5 × the prior session's range; flat at 15:59. It keeps 89% of the custom-indicator rule's Sharpe.
>   - **Before funding:** it needs a forward test and a second data feed (step 2b). It failed on US500, doesn't survive deflation over all trials, and its 2026 holdout (+1.4 bps/day) is consistent but uninformative.
> - **FX candidate (round 19):** **GT, the Tokyo fix on Gotobi days** ([card](edges/GT_tokyo_fix_gotobi.md)).
>   - **Rule:** USDJPY M1. Sell at 09:55:00 JST on Gotobi days; buy back at 10:55 JST.
>   - **Build notes:** needs a Japanese holiday list and a DST-aware clock.
>   - **Evidence:** EDGE by its pre-registered test (net +1.10 bps per trade, t 2.59) with a second feed.
>   - **Before funding:** measure the broker's round-trip cost at 09:55 JST (≤ 1 bp) and the fill delay. It runs in its own account.
> - **Optional candidate:** **MR-08**, MR-06's intraday half (09:30 → 16:00 after three down closes), for flat-by-close accounts. It is WEAK by rule, with 33 years of SPY support.
> - **Parked, with their numbers:** everything else, including all round-5, 7 and 10–15 negatives ([R5](edges/R5_prop_instrument_negatives.md), [R7](edges/R7_negatives.md), [R10](edges/R10_negatives.md), [R11](edges/R11_negatives.md), [R12](edges/R12_negatives.md), [R13–15](edges/R13_15_negatives.md)). Don't re-test them unless the user asks.
>   - **FX and metals have no other tradeable edge** on the data here (FOMC/BoJ-day premia decayed, round 19).
>   - The USDJPY intraday-momentum lead failed on unseen data (round 18): don't build it. The London-afternoon breakout on GBPUSD and gold is untested on bid/ask data.
> - **Round 18 build notes:** the RB signals keep 98% (US100), 107% (JP225) and 72% (US500) of their daily-close Sharpe in the M5/15:55 build. Use **fixed notional per trade** for the ensemble; volatility-scaled size made the worst day worse.

| Step | Edge / task | Deliverable |
|---|---|---|
| 0 | Data loading, time-zone conversion, session calendars, cost model | Tested loaders; DST unit tests; cost table per instrument and time of day. **FX/metals/energy: bid/ask or mid data only, or no window touching 16:00–19:00 NY on bid-only data.** **HistData file time = London − 5 h** (EU DST calendar; one hour behind New York in the US/EU gap weeks). Convert through London time, as `data_histdata.local_table` does. **Never use Yahoo daily FX bars** for close-anchored rules: their close and range come from inconsistent windows (IBS vs next-day return correlation −0.69; round 10). Build FX daily bars from minute data (`run_round10.fx_daily`) |
| 1 | **Index-reversal ensemble** (SQX build matrix §1; REV card): first run **check 1 of the build matrix** (how SQX exposes today's unfinished D1 bar at 15:55), then replicate R1 on the broker's data. US500, US100, US30, US2000, JP225. Signals IBS < 0.10/0.25, RSI(2) < 5/10/20, 2/3/5 down closes, 5/10-day low; exit at the first up close (max 5) or the next close; no filter, or below SMA(200) only. Pick 10–20 de-correlated Tier 1/2 variants per market; volatility-scaled; gross-exposure cap per index. **MR-06** (15:55 entry, next-close exit) is one member | On the broker's data 2013 → : ≥ 80% of the chosen variants positive and ensemble Sharpe > 0.5, or stop |
| 2 | **IM-04 on US100, native build** (SQX build matrix §2): at 09:30, Buy Stop at open + 0.5 × prior session range and Sell Stop at open − 0.5 × range (OCO), Exit At End Of Day at 15:59, max 1 trade/day (or the stop-and-reverse variant). **Flat sizing.** For FTMO Standard, the news blackout of the card. The custom-indicator N3 (card spec) is the reference | Native grid median Sharpe ≈ 0.47 on US100 2014 → (N3 0.52 on the same data; correlation ≈ 0.58); then a **6-month forward test** before live |
| 2b | **Second-feed check of N3 (X1, pre-registered in A14):** the same code on an independent minute feed (Dukascopy `USATECHIDXUSD`, or the broker's own US100 data), 2014–25, via `run_noise_area.run(..., ses=...)` | Net mean > 0 with one-sided p < 0.05, and the daily correlation with the HistData series. The 30-minute rule is **not done here** (the feed was throttled). The 60-minute variant on Yahoo QQQ agrees (correlation 0.99, round 8) |
| 3 | **Decay controls** (`decay_controls.md`): turn of month, overnight drift 02:00–03:00, FOMC-day premium, FOMC cycle, commodity intraday momentum | The pipeline shows them alive early and faded later (own data did). **This validates the pipeline** |
| 4 | Variants, **pre-registered before running**: MR-06 exit after 2 or 3 days, US30; IM-04 VWAP (with real volume) vs TWAP | Per market × year table; fix one variant per edge before paper trading |
| 5 | Pre-holiday (Ariel) as a small add-on | Net of costs per year; ~9 trades/yr |
| 6 | SQX translation: done at spec level in [SQX_build_matrix.md](edges/SQX_build_matrix.md) (round 11). Implement it, and confirm the three unverified points (forming D1 bar, bar time stamps for Limit Time Range, session definitions in the data's time zone) | SQX projects whose backtests on the broker's data match the R1/R3 figures within the tolerance in the matrix |
| 7 | Prop fit in `tools/propsim` with an EA daily guard, over the **sizing policies** of [REPORT.md](../research/validation/REPORT.md) §16–17.5: fixed exposure vs CPPI (`sizer=lambda a: min(cap, k * a.cushion())`), and a separate funded-stage sizer (`funded_sizer`). Start from the published-terms presets (`ftmo_2step_100k`, `ftmo_1step_100k`, `topstep_50k`: subscription and activation fees, Best Day and consistency gates, partial payouts with caps) and re-check them against the firm's current page. Apply each account type's **holding rules to the book** (weekend holds, news blackout, flat by the close). **Separate accounts per strategy** | EV per attempt and per account-month, pass rate, funded breach rate, each against a zero-edge twin. Own-data reference (round 11, SQX-style books, published terms, 2014–26): reversal ensemble on FTMO 2-Step Standard 1× 35% pass (zero edge 7%), CPPI k = 10 49% (6%); native US100 on FTMO 2-Step Standard 1× 57% (31%), $660/month, 3× $1,927/month; FTMO 1-Step CPPI 72% (29%); Topstep ≈ $261/month at best. Separate accounts (together they earn less) |
| 8 | Optional, only if asked: replicate parked edges on the user's broker data | Report in the format below; compare with the card numbers |
| 9 | **Forward test = implementation check** ([FINDINGS.md](../research/FINDINGS.md) §3): 3–6 months of paper trading to confirm fills, times and costs match the backtest, with the pre-set stop rules. It cannot validate the edge statistically (N3 needs ~7.5 years for t = 2) | Parity report; stop-rule status |

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
