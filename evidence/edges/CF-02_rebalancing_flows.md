# CF-02 — Institutional rebalancing flows (stocks vs bonds)

**Verdict:** LEAD (weak on own data with the paper's timing; not significant after the paper's sample) · **Grade:** B (paper) / C (own data) · **Prop fit:** Medium


## Own-data validation ([REPORT.md](../../research/validation/REPORT.md) §12)

| Test | Data | Result |
|---|---|---|
| Round 1 P16: month-end MTD spread → **first day of the next month** | SPY/TLT 2003 → | −26.5 bps (opposite sign, t = −2.8). **Wrong timing:** the paper's pressure is in the last days of the month, before the rebalancing is done. After it, prices bounce, which is what P16 picked up |
| **Round 4 S6: paper-exact Calendar signal** (drifted 60/40 weight, reset at each month-end), trading the spread SPY − IEF the day after each of the **last 5 trading days** | SPY, IEF 2002-08 → 2026-09 | **+7.15 bps/day, t = 2.06, p = 0.020** (Holm 0.12: WEAK). To 2023-03 (paper period): +7.88 (t = 2.00); after: +2.87 (t = 0.47, n = 210) |
| SPY-only version (CFD accounts without bonds) | same | +6.99 bps/day (t = 2.41); after 2023-03: +2.97 (t = 0.55) |

**Bottom line:** the sign and rough size replicate on independent data (ETFs, not futures), but the
out-of-sample period is too short to confirm. Keep as a lead; re-test when 2027–28 data exists.

## Evidence

| Source | Level | Sample | Result |
|---|---|---|---|
| Harvey, Mazzoleni & Melone, "The Unintended Consequences of Rebalancing", NBER WP 33554 (Mar 2025, rev. Jan 2026) | V1 | Daily futures, 1997-09-10 → 2023-03-17 | Simulated 60% S&P 500 / 40% 10-year T-note portfolio. **Threshold** signal (drift beyond a band) and **Calendar** signal (scheduled, e.g. month-end). One-SD signal → next-day **equity −16 bps (Threshold) / −17 bps (Calendar)**, bonds +4 / +2 bps. Pressure **reverts almost fully within 2 weeks**. Front-running strategy: significant alpha, **Sharpe > 1**, robust excluding the GFC and March 2020. Bigger positions in high volatility and low liquidity |

## Paper-exact spec (to confirm against the paper's Section 2–4 before coding)

```
w_eq(t) = weight of equities in a 60/40 portfolio that was last rebalanced at the policy date,
          drifted by S&P 500 futures and 10-year T-note futures daily returns
Calendar signal: deviation w_eq − 0.60 measured at the scheduled rebalance date (e.g. month-end)
Threshold signal: deviation when |w_eq − 0.60| exceeds a band
Trade: short equity (long bonds) the next day when stocks are overweight, and vice versa; size ∝ signal
```

**Open question for the coding agent:** the band width and exact calendar dates are in the paper's
methodology section. Read them from the PDF (NBER w33554) rather than guessing. This card only
confirms the headline effects.

## Adapting to SQX

Multi-symbol (US500 plus a bond series such as ZN futures or a bond CFD). Custom block computing the
drifted 60/40 weight. Daily bars; 1-day hold.

## Falsification tests

Replicate the sign and roughly the magnitude over 1997–2023; out of sample 2023+; the effect is
stronger at month-end and quarter-end.
