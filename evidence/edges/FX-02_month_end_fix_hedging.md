# FX-02 / FX-03 — Month-end London-fix hedging flows

**Verdict:** DON'T BUILD (own data: not significant, even in the paper's period) · **Grade:** B (paper) / D (own data) · **Prop fit:** —


## Own-data validation (round 4, S4–S5; [REPORT.md](../../research/validation/REPORT.md) §12)

Paper-exact rule on HistData 1-minute FX (9 pairs) with Yahoo equity indices; fix day = last London
business day; position in each currency = −sign(its index return minus the S&P 500's, month to date),
15:00 → 16:00 London. The window avoids the NY rollover, so bid-only data is fine here.

| Test | Sample | Result |
|---|---|---|
| S4 hour before the fix | 2004–12 (paper's period) | +2.05 bps/pair-month (t = 1.27) |
| S4 | **2013–25 (primary)** | **+0.84 (t = 0.60), net −0.16**: not confirmed |
| S4 after the Feb-2015 fix reform | 2015-02 → 2025 | +0.88 (t = 0.54) |
| S5 reversal, 16:00 → next-day noon | 2004–12 / 2013–25 | +5.83 (t = 1.90) / +1.65 (t = 0.76) |

Per pair (2013 →), AUD (+4.7, t = 2.1) and CHF (+4.4, t = 2.2) are positive but NOK and CAD negative:
no stable pattern. Ito & Yamada (2017, NBER w23327, V2) report that after the reform "the volume
spike in the fixing window disappeared" while price anomalies changed shape.

## Evidence

| Source | Level | Sample | Result |
|---|---|---|---|
| Melvin & Prins (2015), *JFM* 22:50–72 | V1 (Nov 2013 WP) | 5-min TWAPs (EBS/Reuters), 28 Apr 2004 – 31 Dec 2012; Datastream total-market indices for US, EMU, JP, UK, CA, AU, SE, CH, NO, NZ | Country equity return **month-to-date up to the second-to-last trading day** predicts that currency **depreciating over 15:00–16:00 GMT on the last trading day** (the hour before the WM/R fix). Partial **reversal from 16:00 to 12:00 the next day** |
| Evans (2018), *JBF* 87 | V2 | WM/R fix | Order-flow and price dynamics around the fix |
| Krohn, Mueller & Whelan (2024) | V1 | 1999–2018 | The daily USD pattern around the London fix (FX-01) is the baseline this sits on |

## Caveats

- **The fix methodology changed in February 2015:** the calculation window widened from about 1 minute to 5 minutes. That is after the paper's sample, so re-test separately for 2015+.
- Mechanism size depends on hedge ratios of international equity funds, which change over time.

## Paper-exact spec

```
Signal (per currency c, month m): R_eq(c) = total-market equity return of country c from the last trading day
  of m−1 through the SECOND-TO-LAST trading day of m, relative to US equities (the paper also uses levels)
Target: FX return 15:00 → 16:00 GMT on the last trading day (currency c vs USD); expect sign = −sign(R_eq(c) − R_eq(US))
Reversal leg (FX-03): 16:00 GMT last day → 12:00 GMT next day, expect the opposite sign
```

## Adapting to SQX

- **Multi-symbol:** equity index month-to-date return as an additional chart, plus custom blocks for "last trading day of month" and "second-to-last trading day". Time-gated entries.

## Falsification tests

2004–2012 replication (sign); 2015+ out-of-sample sign; pooled across ≥ 4 pairs, gross > 2× cost.
