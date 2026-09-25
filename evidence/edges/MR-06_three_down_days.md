# MR-06 — Next day after ≥ 3 consecutive down closes (US indices)

**Verdict:** BUILD FIRST (daily) · **Grade:** A− on own data (confirmed out of sample) · **Prop fit:** Medium (a building block; ~22 trades/yr) · **Source:** found by the pre-registered exploratory scan in [research/validation](../../research/validation/REPORT.md)

## Claim

After three or more consecutive down closes in a US equity index, the next day's return is well above
average. The mechanism is short-term reversal from liquidity provision in index products (Baltussen,
van Bekkum & Da, 2019; Nagel, 2012).

## Own-data evidence (all V1: computed here, Yahoo daily data)

| Test | Sample | Result |
|---|---|---|
| Discovery (BH-corrected across 20 candidates) | S&P 500, 1990–2012 | +18.7 bps next-day excess, t = 3.48, q = 0.010 |
| **Confirmation** | S&P 500, 2013 – Sep 2026 | **+21.9 bps, t = 3.01, one-sided p = 0.001** |
| Confirmation | Nasdaq 100, 2013 → | +24.8 bps, t = 2.48 |
| Full 1990 → | S&P 500 | +19.8 bps, t = 4.57; bootstrap 95% CI [+12.5, +27.8]; random-entry p = 0.0002; DSR (N = 39) = 0.95; 31 of 37 years positive |
| **Mechanism check** | S&P 500 before 1990 | **−11.0 bps, t = −2.7** (index momentum era), as the index-product mechanism predicts |
| Dose-response | S&P 500, 1990 → | k = 2: +8.6 · k = 3: +19.8 · k = 4: +31.5 · k = 5: +56.0 bps |
| Holding | S&P 500, 1990 → | 1 day +19.8 · 2 days +31.1 · 3 days +38.7 · 5 days +52.9 bps (excess over drift) |
| Regime | S&P 500, 1990 → | Above SMA200 +12.1 (t = 3.1); below +32.9 (t = 3.1) |
| Recent | S&P 500, 2020 → | +35.8 bps, t = 3.58 |
| Other markets | 1990s → | SPY +22.5 (t = 4.7); ^DJI +10.6 (t = 2.5); ^N225 +11.1; ^AXJO +10.9; ^RUT only after 2013. **DAX, FTSE (post-2013), TSX, SMI, HSI: no** |
| Costs | S&P 500, 1994 → | Net of 0.75 bps spread plus CFD swap (T-bill + 2.5%): **+21.9 bps/trade, t = 4.5**; 22 trades/yr; Sharpe 0.66 at 1×; max DD −18.9% at 1× |

## Spec (pre-register one variant before building; don't pick after the fact)

```
signal at close(t): C(t) < C(t−1) < C(t−2) < C(t−3)     (three consecutive lower closes, index cash close)
entry: buy at/near close(t)  (15:59 ET or closing auction; CFD: last minute before the cash close)
exit:  close(t+1)  [baseline]   — alternatives to pre-register: close(t+2), close(t+3)
size:  fixed fraction; wide catastrophic stop only (Kaminski & Lo 2014: stops hurt mean reversion)
markets: US500, US100 (primary), US30; not DAX/FTSE/TSX/SMI/HSI
```

## Known risks

- **Execution at the close:** the signal needs the close, which you can't know before it happens. Test the 15:55–15:59 proxy on minute data.
- **Overnight gap risk:** a prop EA's daily guard can't stop a gap. Size for it (≤ 3–4× notional on a 5%-daily-loss account).
- **Regime:** the effect appeared with index products after 1990 and is strongest since 2020. Monitor annually (doc 04 §8).
- **Popularity:** "buy after 3 down days" is a well-known practitioner rule (e.g., Connors). It hasn't decayed in this data, but crowding is possible.

## Falsification tests for the SQX build

1. Replicate +15 to +25 bps per trade on US500 CFD data, 2014 →, at 15:59 entry.
2. Net of the broker's close-of-day spread and swap > 0.
3. Positive in ≥ 70% of years 2014 →.
4. **Paper-trade or use post-Sep-2026 data before live.** All data used here is now in-sample.
