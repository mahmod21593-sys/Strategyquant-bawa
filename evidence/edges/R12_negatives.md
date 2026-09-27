# Round-12 negatives, and what they say about the reversal edge

**Verdict:** DON'T BUILD. Pre-registered in A26 and judged with the round-9 battery; DSR count 7,895 · **Source:** [REPORT.md](../../research/validation/REPORT.md) §22.

| Family (variants) | Result | Why it fails |
|---|---|---|
| S. Short side of index reversal: sell after up streaks, RSI(2) > 80–95, IBS > 0.75–0.90, N-day highs; 8 indices (864) | WEAK: SPA 0.58 on timing value; raw P&L negative (medians −0.16 to −0.42) | The index-reversal edge is one-sided. Buying weakness pays; shorting strength doesn't cover the drift |
| U. US macro-release shocks at 08:30, 10:00 and 14:00 NY: follow or fade the first 5 minutes; FX, gold, silver, US500, US100 (324) | NO EDGE: SPA 0.74, walk-forward −0.43 | Prices absorb releases within minutes. Following the 08:30 shock loses in 91% of variants |
| V. LBMA gold 10:30 / 15:00, silver 12:00, and the COMEX opens: before or after the event, long or short (30) | NO EDGE: SPA 1.00 | The old fixing leak (Caminschi & Heaney 2014) ended with the electronic auctions. Gross effects are ≤ 1.3 bps |
| W. FX weekend-gap reversal: fade or follow the Friday 16:45 → Sunday 19:00 NY gap; 7 majors + gold (192) | WEAK: SPA 0.98 after publication | Dao, McGroarty & Urquhart (2016) measured the Monday open inside the rollover spread widening. On clean prices there is no reversal |

**Family T (432 variants): where the reversal return is earned.** Family A's signals, entered at 15:55, with one-day exits. Ensemble Sharpe on timing value:

| Exit | Sharpe | Bootstrap difference from the full-day hold |
|---|---|---|
| Next 03:00 NY (after the European open) | −0.29 | −0.99 [−1.51, −0.50] |
| Next cash open | 0.23 | −0.46 [−0.79, −0.11] |
| **Next 15:55** | **0.69** (2020–26: 0.95) | — |

- **Hold US legs through the next session.** The night alone does not carry the edge.
- **JP225 is the exception.** Its reversal is earned overnight, during the US session: exiting at the next Tokyo open works (per-market SPA 0.002).
- **The published overnight drift** (US equities in the 02:00–03:00 NY hour; Boyarchenko, Larsen & Whelan 2023) was +1.6 bps a night in 2014–20. It has been ≈ 0 since 2021, as the NY Fed reported in 2026. The reversal edge stayed strong over the same years, so it is a separate effect.
