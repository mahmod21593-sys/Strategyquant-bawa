# TF-01 / TF-02 — Time-series momentum (trend following)

**Verdict:** BUILD for the long-term portfolio; **not** for prop challenges · **Grade:** A (with documented regime risk) · **Prop fit:** Low

## Evidence

| Source | Level | Sample | Result |
|---|---|---|---|
| Moskowitz, Ooi & Pedersen (2012), *JFE* 104(2) | V1 | 58 futures: 24 commodities, 12 cross-currency pairs, 9 equity indexes, 13 bond futures; Jan 1965 – Dec 2009 | 12-month TSMOM: **all 58 contracts positive, 52 significant at 5%** (1985–2009). Diversified portfolio **Sharpe > 1** (~2.5× equity market). 1966–1985: Sharpe 1.1. Strong in late 2008. Persistence over 1–12 months, partial reversal beyond |
| MOP spec | V1 | — | r_TSMOM(t, t+1) = sign(r(t−12, t)) × (40% / σ_t) × r(t, t+1); σ_t² = 261 × EWMA of squared daily returns, centre of mass 60 days |
| Hurst, Ooi & Pedersen (2017), *JPM* 44(1) | V2 | Back to 1880; equity, bond, commodity, FX | "Consistently profitable over the next 110 years" (landing-page summary). Detailed numbers not verified here |
| Levine & Pedersen (2016), *FAJ* 72(3) | V2 | — | MA crossovers ≈ TSMOM filters; horizon matters more than indicator |

## Contrary and decay evidence

| Source | Level | Finding |
|---|---|---|
| Huang, Li, Wang & Zhou (2020), *JFE* 135(3) | V2 | Asset-by-asset predictability weak; profits similar to a sample-mean strategy |
| Kim, Tse & Wald (2016), *JFM* 30 | V2 | TSMOM alpha largely from **volatility scaling**; unscaled ≈ buy-and-hold |
| Industry (SG Trend Index via Hedgeweek / Price Action Lab) | V3 | **2009–2018 "lost decade": ≈ 0.4%/yr, max drawdown ≈ 21.8%**; 2022 +27.3% |

## Own data, round 7 re-test on prop instruments (G6; [REPORT.md](../../research/validation/REPORT.md) §17.2–17.3)

MOP rule on 16 ETFs (US, German, UK and Japanese equity; gold, silver, oil; six currencies) plus BTC, no
bonds, after publication (2012-01 → 2026-08):

| Measure | Result |
|---|---|
| Mean, net of 2 bps turnover | **+91 bps/month, t = 2.62, Sharpe 0.62**; 2007–11 also positive |
| Verdict | **WEAK**: Holm p 0.053 across the 13 round-7 tests (0.044 across the original 11) |
| Same weights, always long | +54 bps/month (t = 1.0) |
| Timing value (TSMOM − long) | +39 (t = 0.6). The FX leg rode the dollar (+184, t = 1.8); equities negative (−78) |
| Correlation with SPY | 0.04 |
| **As a prop book (FTMO 2-Step Swing)** | ~3.5× gross notional: a **2%/yr CFD financing mark-up leaves +1.8%/yr at 19% vol**; **$23 per account-month** (0% mark-up $88; 4% negative) |

**Conclusion:** a real, diversifying premium for a long-term, low-cost (futures or ETF) portfolio. It is
uneconomic in CFD prop accounts, and futures prop firms ban the overnight holds it needs.

## Paper-exact spec

See the MOP formula above: monthly rebalance, 12-month lookback, 40% volatility target per instrument,
equal-weight across instruments. Variants: 1, 3 and 12-month blend (Hurst et al.); Donchian or MA
equivalents (Levine & Pedersen).

## Replication targets

On a diversified futures set, 1985–2009: the large majority of instruments have positive 12-month
TSMOM returns, and the portfolio Sharpe is near or above 1 gross.

## Adapting to SQX

- One strategy per market, D1, with a **volatility-scaled position size**: SQX fixed-% risk with an ATR stop approximates it. Evaluate at **portfolio level** across ≥ 8 markets. Single-market backtests will look weak, which is expected (Huang et al.).
- Unsuitable for challenges: multi-year flat periods, large open-profit giveback, overnight gaps.
