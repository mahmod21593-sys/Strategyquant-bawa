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

Every edge below has also been tested on real data in three pre-registered rounds (daily data back to
1970, and 1-minute data 2010–2025): [research/validation/REPORT.md](../research/validation/REPORT.md).
**Read that report first.** Its verdicts override the literature grades where they disagree.

**Result:** two edges survived out of sample: **MR-06** (three down closes, US indices) and **CF-07**
(Treasury end-of-month, added in round 4). Everything intraday either failed on unseen data, fell below
realistic costs, or (FX) turned out to be a data artifact.

## Edge cards

| Card | Verdict | Grade (literature → own data) | Prop fit | Own-data result |
|---|---|---|---|---|
| **[CF-07 Treasury end-of-month (new)](edges/CF-07_treasury_month_end.md)** | **Build** | B (working paper) → **A−** | High on futures accounts | IEF last 3 days +19.8 bps/month after the paper's sample (t = 2.95, Holm p = 0.011); 24 of 25 years positive |
| **[MR-06 Three down days (new)](edges/MR-06_three_down_days.md)** | **Build** | — → **A−** | Medium (60% pass vol-scaled; 73–83% with CF-07) | +20 bps/trade; confirmed 2013 → ; 15:55 entry works (+15.9 bps, p = 0.03); next-open entry loses half |
| [IM-01 Market intraday momentum](edges/IM-01_market_intraday_momentum.md) | **Don't build** | B → not supported | — | US500 2014–25: +0.2 bps (t = 0.4); Gao version reversed (t = −2.6). GER40 close +2.1 bps (t = 4.9) failed on 2010–13 and is below costs on CAC/FTSE |
| [IM-02 Opening-range breakout](edges/IM-02_opening_range_breakout.md) | **Don't build standalone** | B → C | — | +2.5 bps gross (t = 2.4–3.2), ≈ +1 bp net; ≈ 0R with risk sizing; n.s. on 2010–13 |
| [IM-04 Noise-area momentum](edges/IM-04_noise_area_momentum.md) | Untested; low priority (IM-01 failed) | B− | — | — |
| [MR-01 Index mean reversion](edges/MR-01_index_short_term_reversal.md) | Filter only; use MR-06 instead | B → C | — | IBS < 0.2: +2.7 bps, t = 1.1; non-US negative |
| [FX-01 Fix reversals](edges/FX-01_fx_fix_reversals.md) | **Don't build** | B+ → D (current) | — | Round-1 "replication" was a bid-quote artifact at the NY rollover. Clean data: real 2004–18, gone after 2019 |
| [FX-02 Month-end fix hedging](edges/FX-02_month_end_fix_hedging.md) | **Don't build** | B → D | — | 2013–25: +0.8 bps (t = 0.6); weak even in the paper's period (t = 1.3) |
| [CF-02 Rebalancing flows](edges/CF-02_rebalancing_flows.md) | Lead | B → C | — | Paper timing: +7.2 bps/day (t = 2.1) on 2002–26, n.s. after 2023. Round 1's opposite sign came from trading the wrong day |
| [TF-01 Time-series momentum](edges/TF-01_time_series_momentum.md) | Portfolio sleeve only | A | Low | Sharpe 0.58, but equal to vol-scaled buy-and-hold on ETFs |
| [VB-02 London-open breakout](edges/VB-02_london_open_breakout.md) | Test only | C | — | — |
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
