# FX-01 — Dollar reversals around the Tokyo and London fixes (replaces the Ranaldo-only framing)

**Verdict:** DON'T BUILD (own data: real in 2004–18, decayed after 2019, below retail costs; the round-1 "replication" was a data artifact) · **Grade:** B+ as history, **D** as a current edge · **Prop fit:** —


## Own-data validation (rounds 1–3; [REPORT.md](../../research/validation/REPORT.md) §8)

| Test | Data | Result |
|---|---|---|
| W1 + W4 (long USD NY 17:00 → 01:00 UTC; short USD London 16:00 → NY 17:00), pre-registered Q6 | HistData 1-min, 9 pairs, 2004 – 2023-09 | +3.53 bps/day, t = 9.3, but **it is an artifact.** USD-base pairs +4 to +11 bps; USD-quote pairs −2 to −7 bps after 2019. HistData quotes are **bids**, and the bid drops at the NY 17:00 rollover in every pair (−0.7 bps EURUSD to −9 bps USDNOK). Both windows start or end at 17:00 |
| Round-1 W1/W4 on Yahoo (2023–26) | 9 pairs | Same signature (NOK t = 10.9, SEK 6.5, CHF 4.4; EUR, AUD, NZD, JPY ≈ 0). **Withdrawn** |
| **Clean W4**: London 16:00 → NY 16:45 (post hoc) | 2004–18 / 2019–23 | **−1.62 bps (t = −4.2)** / −0.25 (t = −0.5) |
| **Clean W1**: NY 18:30 → 01:00 UTC (post hoc) | 2004–18 / 2019–23 | **+1.19 (t = 6.6)** / +1.37 (t = 4.7) |
| Clean W1, USD-quote pairs only (R6, unseen) | 2024–25 | +0.21, t = 0.44: not replicated |

**Bottom line:** Krohn et al.'s dollar pattern is visible in clean 2004–18 data. The post-London-fix
leg has disappeared since 2019. The Tokyo leg (~1 bp/day) was below costs and has faded in 2024–25.
**For any FX intraday test, use bid/ask or mid data, and never put a window boundary between 17:00
and 18:30 NY on bid-only data.**

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
