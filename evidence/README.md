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

## Edge cards

| Card | Verdict | Grade | Prop fit | Key change from the original plan |
|---|---|---|---|---|
| [IM-01 Market intraday momentum](edges/IM-01_market_intraday_momentum.md) | **Build first** (with signal threshold) | B (was A) | High | Rosa (2022): unconditional version disappears out of sample; Baltussen et al. results are gross of costs |
| [IM-02 Opening-range breakout](edges/IM-02_opening_range_breakout.md) | Build | B | High | Three incompatible "ORB" definitions in the evidence; added peer-reviewed TORB (Tsai et al., 2019) |
| [IM-04 Noise-area momentum](edges/IM-04_noise_area_momentum.md) | Build (after IM-01) | B− | High | Full formula spec extracted; most of the Sharpe gain comes from one exit choice |
| [MR-01 Index mean reversion](edges/MR-01_index_short_term_reversal.md) | Build, **US first** | B | High | IBS effect largely **US-only** (Pagonidis); non-US indices must pass on their own |
| [FX-01 Fix reversals](edges/FX-01_fx_fix_reversals.md) | Build (cost-sensitive) | **B+ (was B)** | Medium–High | New primary: Krohn, Mueller & Whelan (2024, *JF*), 20 years, every year |
| [FX-02 Month-end fix hedging](edges/FX-02_month_end_fix_hedging.md) | Test | B | Low–Medium | Exact windows extracted; the 2015 fix-window change postdates the sample |
| [CF-02 Rebalancing flows](edges/CF-02_rebalancing_flows.md) | Test | B | Medium | Revised NBER WP (Jan 2026); −16/−17 bps next-day equity effect |
| [TF-01 Time-series momentum](edges/TF-01_time_series_momentum.md) | Build (portfolio, not prop) | A | Low | Exact MOP formula; 2009–2018 lost decade documented |
| [VB-02 London-open breakout](edges/VB-02_london_open_breakout.md) | Test only | C | High if it passes | No peer-reviewed support found; may conflict with the fix-reversal pattern |
| [Decay controls](edges/decay_controls.md) | Controls only | D | — | **Turn of month downgraded A− → D** (Han, Han & Tian 2025: gone after 2001) |

Machine-readable version: [evidence-index.json](evidence-index.json).
What this verification changed in the rest of the repo: [changes-to-plan.md](changes-to-plan.md).

## What was not verified

- Hurst, Ooi & Pedersen (2017): numbers beyond the abstract.
- Connors & Alvarez (2009): RSI(2) rules (book).
- Dim, Eraker & Vilkov (2024): 0DTE gamma findings (V3).
- Li, Sakkas & Urquhart (2022) and Elaut et al. (2018): numbers beyond the abstract.
- Industry CTA index figures (V3).

Anything not listed in a card should be treated as unverified.
