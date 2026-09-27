# Evidence pack

Verified research evidence for the edges in this repo, prepared to hand to a coding agent. Everything
here was checked against primary sources in September 2026. Each claim carries a **verification level**,
so the agent (and you) can tell a number read from a paper apart from a summary.

**Start with [AGENT_BRIEF.md](AGENT_BRIEF.md)**. It is written to be pasted into a coding agent as its task.

## Verification levels

| Level | Meaning |
|---|---|
| **V1** | Checked against the **full text** of the primary source (published PDF or the authors' working-paper PDF). Numbers are quoted from it |
| **V2** | Checked against the **abstract or official summary** (publisher, SSRN, NBER, IDEAS/EconPapers, author landing page). Headline only |
| **V3** | Secondary source or search-engine summary. **Not verified**; treat as a lead, not evidence |
| (WP) | Working paper or practitioner paper, not peer-reviewed |

## Own-data validation (Sep 2026)

Every edge below has also been tested on real data in seven pre-registered rounds (daily data back to
1970, 1-minute data 2010–2025, and an untouched 2026 holdout): [research/validation/REPORT.md](../research/validation/REPORT.md).
**Read that report first,** or the curated summary [research/FINDINGS.md](../research/FINDINGS.md). Its verdicts override the literature grades where they disagree.

**Result (twelve rounds, no Treasury strategies):**

- **Edge family (round 9):** short-term **index reversal** on US500/US100/US30/US2000/JP225, robust across 864 variants under multiple-testing control. Build it as an ensemble ([REV card](edges/REV_index_reversal_family.md); curated summary [research/FINDINGS.md](../research/FINDINGS.md)).
- **Round 11, built as SQX trades it:** the reversal ensemble keeps 82–87% of its Sharpe in an M5/15:55 build on CFD quotes and needs no weekend holds. US100 momentum can be built from native SQX blocks. FX and metals: four more families, no tradeable edge. **How to build each edge: [SQX_build_matrix.md](edges/SQX_build_matrix.md).**
- **Established:** **MR-06** (three down closes, US indices), a member of that family. About half its edge is earned in the next session (MR-08, weak by rule, 33 years of SPY support).
- **Candidate:** **IM-04 noise-area momentum on US100**. It passed its pre-registered family test and robustness checks, but not deflation over all ~745 trials. Its 2026 holdout was consistent but uninformative, so paper-trade it first.
- **Real but not a prop edge:** time-series momentum. It is weak after Holm, and CFD financing eats it.
- **Out of scope:** CF-07 (Treasury end-of-month) was confirmed in round 4, but the user excluded Treasury strategies.
- **Everything else** failed on unseen data, fell below realistic costs, or was a data artifact: [R5_prop_instrument_negatives.md](edges/R5_prop_instrument_negatives.md), [R7_negatives.md](edges/R7_negatives.md).
- **Best venue tested (published terms):** FTMO 1-Step with the US100 rule at 4× (≈ $980 per account-month, in-sample). MR-06 needs weekend holds (FTMO Swing). Flat-by-close futures firms fit neither edge well.

## Edge cards

| Card | Verdict | Grade (literature → own data) | Prop fit | Own-data result |
|---|---|---|---|---|
| [CF-07 Treasury end-of-month](edges/CF-07_treasury_month_end.md) | **Excluded by user** (no Treasuries) | B (working paper) → A− | — | IEF last 3 days +19.8 bps/month after the paper's sample (t = 2.95); kept on record |
| **[SQX build matrix (round 11)](edges/SQX_build_matrix.md)** | **Build spec** for REV, US100 momentum (native) and MR-06; the FX lead as paper-only | — | Sizing per account from the A25 lifecycle | R1: M5/15:55 build keeps 82–87% of the research Sharpe; R3: native US100 bands keep 89% |
| [Round-11 negatives](edges/R11_negatives.md) | **Don't build** | — | — | FX/gold session seasonality, FX night mean reversion, European open gap; session-range breakouts (USDJPY lead only) |
| [Round-12 negatives and reversal anatomy](edges/R12_negatives.md) | **Don't build** (the anatomy result changes how REV is held) | — | — | Short-side index reversal, macro-release shocks, metals auctions, FX weekend gaps; REV needs the next session (overnight-only exits fail) |
| **[REV Index-reversal family (round 9)](edges/REV_index_reversal_family.md)** | **Build first (core, as an ensemble)** | — → **A−** (family-level) | High as an ensemble: FTMO 2-Step 1× 70% pass (zero edge 26%), ≈ $450–1,100 per account-month (post hoc) | 864 variants: SPA p = 0.03 (timing value), PBO 0.19, walk-forward t = 2.1; 79–94% of US variants positive 2013–26; ensemble Sharpe 0.9–1.0 |
| **[MR-06 Three down days (new)](edges/MR-06_three_down_days.md)** | **Build first** | — → **A−** | Medium: FTMO 2-Step Swing 3× ≈ $210 per account-month; no weekend holds $73; not allowed at futures firms | +20 bps/trade; confirmed 2013 → ; 15:55 entry works; half the edge is intraday; also JP225/AUS200; not global |
| [IM-01 Market intraday momentum](edges/IM-01_market_intraday_momentum.md) | **Don't build** | B → not supported | — | US500 2014–25: +0.2 bps (t = 0.4); Gao version reversed (t = −2.6). GER40 close +2.1 bps (t = 4.9) failed on 2010–13 and is below costs on CAC/FTSE |
| [IM-02 Opening-range breakout](edges/IM-02_opening_range_breakout.md) | **Don't build standalone** | B → C | — | +2.5 bps gross (t = 2.4–3.2), ≈ +1 bp net; ≈ 0R with risk sizing; n.s. on 2010–13 |
| **[IM-04 Noise-area momentum](edges/IM-04_noise_area_momentum.md)** | **Candidate: US100 only, paper-trade first** | B− → B− | High: FTMO 1-Step 4× ≈ $980 per account-month; FTMO 2-Step $715–770; Topstep $124 | US100 +3.0 bps/day (t = 2.54, Holm p = 0.028, Sharpe 0.73); 2026 +1.4 (consistent); US500, GER40, gold fail; DSR 0.22; second feed still to do |
| [Round-5 negatives](edges/R5_prop_instrument_negatives.md) | **Don't build** | — | — | Commodity, crude-oil, Bitcoin and Asian intraday rules; the crypto-weekend trade; 653 scan candidates: 0 confirmed |
| [Round-10 negatives](edges/R10_negatives.md) | **Don't build** | — | — | Seven more families (3,768 variants): reversal outside equities, per-market trend, pair relative value, calendar, crypto trend, reversal on more indices, cross-sectional stock reversal. The Yahoo FX artefact |
| [Round-7 negatives](edges/R7_negatives.md) | **Don't build** | — | — | Halloween, options expiration, VIX-conditioned MR, volatility management, last-hour reversal, Asian-range/Williams/NR7 breakouts, crypto funding, gap fade, index momentum; the 2026 holdout of earlier WEAK rules |
| [MR-01 Index mean reversion](edges/MR-01_index_short_term_reversal.md) | Filter only; use MR-06 instead | B → C | — | IBS < 0.2: +2.7 bps, t = 1.1; non-US negative |
| [FX-01 Fix reversals](edges/FX-01_fx_fix_reversals.md) | **Don't build** | B+ → D (current) | — | Round-1 "replication" was a bid-quote artifact at the NY rollover. Clean data: real 2004–18, gone after 2019 |
| [FX-02 Month-end fix hedging](edges/FX-02_month_end_fix_hedging.md) | **Don't build** | B → D | — | 2013–25: +0.8 bps (t = 0.6); weak even in the paper's period (t = 1.3) |
| [CF-02 Rebalancing flows](edges/CF-02_rebalancing_flows.md) | Lead | B → C | — | Paper timing: +7.2 bps/day (t = 2.1) on 2002–26, n.s. after 2023. Round 1's opposite sign came from trading the wrong day |
| [TF-01 Time-series momentum](edges/TF-01_time_series_momentum.md) | Portfolio sleeve only (not prop) | A | Low | Prop instruments 2012 → : Sharpe 0.62, correlation with SPY 0.04, WEAK after Holm; +1.8%/yr after CFD financing |
| [VB-02 London-open breakout](edges/VB-02_london_open_breakout.md) | **Don't build** | C → D | — | +1.1 bps gross (t = 2.5), −0.1 net |
| [Decay controls](edges/decay_controls.md) | Controls only | D | — | Turn of month, overnight drift and FOMC-day premium all **decayed as predicted**: the pipeline passes calibration. **FOMC cycle** added: +12 bps/day 1994–2016, −4.8 after 2017 |

Machine-readable version: [evidence-index.json](evidence-index.json).
What this verification changed in the rest of the repo: [changes-to-plan.md](changes-to-plan.md).

## What was not verified

- Hurst, Ooi & Pedersen (2017): numbers beyond the abstract.
- Connors & Alvarez (2009): RSI(2) rules (book).
- Dim, Eraker & Vilkov (2024): 0DTE gamma findings (V3). Own data found no lasting momentum-to-reversal flip.
- Li, Sakkas & Urquhart (2022) and Elaut et al. (2018): numbers beyond the abstract.
- Industry CTA index figures (V3).

Anything not listed in a card should be treated as unverified.
