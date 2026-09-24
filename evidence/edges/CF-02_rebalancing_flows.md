# CF-02 — Institutional rebalancing flows (stocks vs bonds)

**Verdict:** TEST · **Grade:** B (NBER working paper, revised Jan 2026; strong mechanism) · **Prop fit:** Medium

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
