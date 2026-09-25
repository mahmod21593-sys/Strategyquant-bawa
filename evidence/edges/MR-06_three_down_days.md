# MR-06 — Next day after ≥ 3 consecutive down closes (US indices)

**Verdict:** BUILD FIRST (daily); the only edge that survived all three validation rounds · **Grade:** A− on own data (confirmed out of sample; realistic entry checked) · **Prop fit:** Medium with volatility-scaled size (60% pass at 2× vs 44% fixed); best combined with [CF-07](CF-07_treasury_month_end.md) · **Source:** found by the pre-registered exploratory scan in [research/validation](../../research/validation/REPORT.md)

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

### Execution tests (rounds 2–3)

| Test | Sample | Result |
|---|---|---|
| **Entry at 15:55 ET, exit next close** (R7, pre-registered, unseen rule) | HistData US500 + US100 minute, 2014–25 | **+15.9 bps excess, t = 1.89, p = 0.030**; US500 alone +20.2 (t = 2.3). 93–98% of 15:55 signals are true three-down-close days |
| Same data, 15:55 vs exact 16:00 close (post hoc) | US500 2014–25 | +23.5 vs +21.2 bps raw (t = 2.65 vs 2.59); US100 +16.8 vs +20.3. **Entering a few minutes early costs nothing** |
| Entry at the **next open**, exit that close (Q2) | SPY 1993 → | +11.4 bps (t = 2.6); 2013 → +9.7 (p = 0.06). **About half the effect is lost overnight** |
| Next open, DIA + IWM (R5, unseen) | 2013 → | +4.5 bps, t = 0.9: not replicated |
| Outside equity indices (Q4 mechanism check) | Bonds, gold, oil, FX ETFs, crypto | ≈ 0 pooled, as the index-product mechanism predicts (TLT and IEF individually positive) |

### Prop-challenge simulation (realistic entry, [prop_mr06_minute.py](../../research/validation/prop_mr06_minute.py))

Two-step 10%/5%, 5% daily loss, 10% static max loss, 3% EA daily guard, 2014–25 bootstrap:

| Book | 2× | 4× | 8× |
|---|---|---|---|
| US500 + US100 | 41% pass · 360 days median | 41% · 169 days | 37% · 99 days |
| US500 only | 44% · 556 days | 37% · 271 days | 33% · 149 days |

Zero-edge base rate: 33%. Per trade at 1×, σ = 153 bps against a +20 bps mean, with a mean adverse
excursion of −89 bps. **Without an EA guard, 82% of challenges breach the 5% daily loss at 2×.**

**Volatility-scaled size (round 4, I1; design fixed in A8):** notional = min(2, 1% ÷ 20-day realized
daily vol), normalised to the same average notional. σ per trade falls to 127 bps (mean 18.5). Pass rate
**60% at 2×** (641 days median) and 48% at 4× (292 days), against 44% and 37% with fixed size.
**Combined with CF-07** (Treasury end-of-month at 4×): 73–83% pass on a two-step challenge, and 3–12
months to pass (see the CF-07 card).

## Spec (pre-register one variant before building; don't pick after the fact)

```
signal at 15:55 ET on day t: P(15:55) < C(t−1) < C(t−2) < C(t−3)   (C = 16:00 cash-session close)
entry: buy at 15:55 (tested, R7). Don't enter at the next open (loses about half the effect)
exit:  close(t+1)  [baseline]   — alternatives to pre-register: close(t+2), close(t+3)
size:  volatility-scaled: min(2, 1% / 20-day realized vol of daily returns, measured before the signal day) × base;
       wide catastrophic stop only (Kaminski & Lo 2014: stops hurt mean reversion)
markets: US500, US100 (primary), US30; not DAX/FTSE/TSX/SMI/HSI
```

## Known risks

- **Execution at the close:** addressed. On the same data the 15:55 proxy matches the exact close (R7: p = 0.03, though it misses Holm within round 3). The next-open entry loses about half the effect.
- **Overnight gap and intraday risk:** the daily-loss rule, not the edge, decides prop outcomes. Use an EA daily guard and ≤ 2× notional; expect 12–18 months per pass.
- **Regime:** the effect appeared with index products after 1990 and is strongest since 2020. Monitor annually (doc 04 §8).
- **Popularity:** "buy after 3 down days" is a well-known practitioner rule (e.g., Connors). It hasn't decayed in this data, but crowding is possible.

## Falsification tests for the SQX build

1. Replicate +15 to +25 bps per trade on your broker's US500 CFD data, 2014 →, at 15:55 entry (HistData gave +20 to +24 bps raw).
2. Net of the broker's close-of-day spread and swap > 0.
3. Positive in ≥ 70% of years 2014 →.
4. **Paper-trade or use post-Sep-2026 data before live.** All data used here is now in-sample.
