# FX-02 / FX-03 — Month-end London-fix hedging flows

**Verdict:** TEST (12 events a year; pool across pairs) · **Grade:** B · **Prop fit:** Low–Medium

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
