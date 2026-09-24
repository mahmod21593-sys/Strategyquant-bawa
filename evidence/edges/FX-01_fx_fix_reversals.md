# FX-01 — Dollar reversals around the Tokyo and London fixes (replaces the Ranaldo-only framing)

**Verdict:** BUILD (cost-sensitive; needs a raw-spread account) · **Grade:** B+ (upgraded: top-journal, 20-year, every-year evidence) · **Prop fit:** Medium–High (intraday, flat by the NY close)

## Claim

The US dollar systematically **appreciates in the hours before** the major benchmark fixes (Tokyo
09:55 JST, London WM/R 16:00) and **depreciates after** them. This comes from intermediaries' inventory
risk as corporate, pension and insurer dollar flows are warehoused across time zones.

## Evidence

| Source | Level | Sample | Result |
|---|---|---|---|
| Krohn, Mueller & Whelan (2024), *Journal of Finance* (doi 10.1111/jofi.13306) | V1 (June 2020 WP) | G10 vs USD (AUD, CAD, EUR, GBP, JPY, NZD, NOK, SEK, CHF), Jan 1999 – Dec 2018 | Equal-weight dollar portfolio (DOL): **NY close → Tokyo fix +5.3%/yr (2.1 bps/day, t = 12.0); after Tokyo fix −5.5%/yr (t = 9.2); European open → London fix +4.3%/yr (1.7 bps/day, t = 4.1); London fix → NY close −4.8%/yr (1.9 bps/day, t = 5.5)**. Present every weekday, every month and in **each of the 20 years** |
| Krohn et al., trading | V1 | EUR around the London fix | Gross: $1 → $15 (1999–2018). With conservative costs, $1 more than triples; **Sharpe 0.65**. Authors: "not easy to exploit once transaction costs are accounted for" |
| Ranaldo (2009), *JBF* 33(12) | V2 | Hourly indicative quotes, 1993–2005 (DEM/EUR, JPY, CHF, USD) | Domestic currencies depreciate during domestic hours and appreciate during foreign hours; persistent; not explained by calendar effects |
| Breedon & Ranaldo (2013), *JMCB* 45(5) | V2 | — | Pattern linked to order flow |

## Paper-exact spec to replicate

```
DOL_t(window) = mean over the 9 G10 currencies of the return of (foreign currency vs USD) over the window,
                sign convention: positive = USD appreciates
Windows (convert via exchange time zones; the fixes follow local DST):
  W1: NY close (17:00 America/New_York)  → Tokyo fix 09:55 Asia/Tokyo           expect USD up
  W2: Tokyo fix 09:55 JST                → European open (≈ 08:00 Europe/London) expect USD down
  W3: European open                      → London fix 16:00 Europe/London        expect USD up
  W4: London fix 16:00 Europe/London     → NY close 17:00 America/New_York       expect USD down
Trade candidates: short USD over W4 (long EURUSD/GBPUSD…, short USDJPY…), long USD over W3; per pair and DOL basket
```

The window boundaries above paraphrase the paper's text ("after trading in New York ceases… until the
Tokyo fix", "European open… until the London fix… until New York close"). **Take the exact boundary
times from the paper's Section I and Figure 1** before coding.

## Replication targets

2.1, 2.2, 1.7 and 1.9 bps/day for W1–W4 on the DOL basket, 1999–2018, and the sign in every calendar
year. Per-pair magnitudes vary; EUR around the London fix is the paper's worked example.

## Adapting to SQX

- Pure **time-gated** rules: limit time range plus exit at end of range, no indicators. Use SQX only for backtest and robustness. **Don't genetically mine.**
- The dominant risk is **cost vs a ~2 bps/day gross edge**. Model the raw spread plus commission at those exact times; London 16:00 spreads are usually tight, but check the Tokyo-fix hours on your broker. Require gross > 2× cost (Gate 1).
- Holidays: the fixes still occur on some local holidays; follow each exchange's calendar.

## Falsification tests

1. Replicate W1–W4 signs on 1999–2018.
2. **Post-2018 data** (outside the paper) has the same signs.
3. Net of your broker's costs, W3 + W4 per-pair P&L > 0 on ≥ 3 pairs.
4. Month-end days are analysed separately. FX-02 flows sit on top of this pattern.
