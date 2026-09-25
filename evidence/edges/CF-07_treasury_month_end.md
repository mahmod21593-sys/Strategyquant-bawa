# CF-07 — Treasury end-of-month returns (new, round 4)

**Verdict:** BUILD (second candidate after MR-06; the strongest prop component found) · **Grade:** A− (published, V1, and confirmed on own data after the paper's sample) · **Prop fit:** High on futures accounts (ZN/TN/ZB); needs a broker with Treasury CFDs otherwise

## Claim

Coupon Treasuries earn their term premium almost entirely in the **last few trading days of each
month**. Returns at other times are ≈ 0. The mechanism is predictable buying on benchmark-index
rebalancing dates. Index providers extend duration at month-end, and index-tracking investors (life
insurers in particular) buy the added securities on that date. Window dressing adds to it.

## Evidence

| Source | Level | Sample | Result |
|---|---|---|---|
| Hartley & Schwarz (2019), "Predictable End-of-Month Treasury Returns", SSRN 3440417 | V1 (Nov 2019 WP) | Off-the-run curve (Gürkaynak, Sack & Wright), 1990–2018; also on-the-run notes, futures, swaps | 10-yr note over the **last 3 trading days: +0.25%/month excess** (≈ 3%/yr); **Sharpe ≈ 1**; other days not significantly different from zero; the effect rises with maturity; present in Treasury futures (annualized > 3 pp on the longest contracts) and in swap yields |
| Same | V1 | Insurer transaction data | Life insurers are large net buyers of Treasuries on index-rebalancing dates, concentrated in the securities added to the index |
| NY Fed Liberty Street (Sep 2024), "End-of-Month Liquidity in the Treasury Market" | V3 (title only, not read) | — | Context on month-end Treasury liquidity |
| Allocate Smartly; practitioner write-ups | V3 | ETFs to 2025 | Report that the pattern persisted in TLT/IEF after 2019. Leads only |

## Own-data validation ([REPORT.md](../../research/validation/REPORT.md) §12–13)

| Test | Sample | Result |
|---|---|---|
| **S2 (pre-registered, A8):** IEF, last 3 trading days, excess over T-bill | **2019-01 → 2026-08 (after the paper's sample)** | **+19.8 bps/month, t = 2.95, p = 0.0016, Holm p = 0.011**; net of 2 bps +17.8; 95% CI [+9.3, +29.7]; 88% of years positive |
| Same rule, the paper's period | IEF 2002-08 → 2018 | +21.0 bps, t = 4.59 |
| Rest of the month (post hoc) | IEF 2019 → | −33 bps/month (t = −1.7): all of the term premium sits at month-end |
| Window length (post hoc) | IEF 2019 → | Last day +7.5 (t = 2.0); last 2 +12.8; **last 3 +19.8**; last 4 +18.9; last 5 +24.0 (t = 2.8). The same pattern in 2002–18 |
| Duration dose-response (post hoc) | Last 3 days, 2019 → | SHY +5.5 (t = 3.7) · IEF +19.8 (t = 3.0) · TLT +24.1 (t = 1.8) |
| Year by year | IEF 2002–2026 | **Positive in 24 of 25 years** (only the partial 2026 negative) |

## Spec (the tested rule; fix one before building)

```
E  = last trading day of the month (exchange calendar)
entry: buy at the close of trading day E−3      (3 trading days before E)
exit:  sell at the close of E
instrument: 10-yr T-note future ZN (duration ≈ 6) — or IEF/TN; TLT/ZB/UB for larger moves and more noise
size: fixed notional; no stop (12 short trades a year); an EA daily guard for prop accounts
```

## Prop simulation (post hoc, in-sample for sizing; [round4_followup.py](../../research/validation/round4_followup.py))

| Book, 2014–25 | Two-step 10%/5% | Futures 50K, 4% EOD trailing |
|---|---|---|
| Zero edge | 27% | 19% |
| **CF-07 at 4× notional** (≈ 2 ZN on 50K) | **86% · 494 days** | **50% · 134 days** |
| CF-07 4× + MR-06 1× (vol-scaled) | 83% · 373 days | 48% · 95 days |
| CF-07 4× + MR-06 2× | 73% · 292 days | 37% · 86 days |

MR-06 and CF-07 overlapped on only 27 trading days in 12 years.

## Known risks

- **Futures roll:** ZN/ZB roll before first notice at the end of Feb, May, Aug and Nov, inside the trading window. Roll to the next contract **before** E−3 in those months, or trade the deferred contract.
- **Rate shocks:** a month-end window can still lose on a macro surprise (a CPI or payrolls release in the window). The 2022 rate shock was positive for the strategy (+34.6 bps/month), but single months can lose 1–2%.
- **Crowding:** the effect is published and practitioner-known. It hasn't decayed through 2025, but monitor the rolling 24-month mean.
- **ETF vs futures:** own-data tests used ETFs. Replicate on ZN/ZB futures data (incl. the roll) before live.

## Falsification tests for the SQX build

1. ZN futures (back-adjusted, correct roll), 2010 → : last-3-day mean > +10 bps/trade (duration-adjusted from IEF), predicted sign in ≥ 70% of years.
2. Rest-of-month mean not significantly positive (the mechanism predicts the premium is concentrated at month-end).
3. Net of the broker's commission and slippage > 0 per trade.
4. Paper-trade 6 months (or use post-Sep-2026 data) before live.
