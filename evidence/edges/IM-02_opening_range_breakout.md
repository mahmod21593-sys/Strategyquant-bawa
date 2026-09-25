# IM-02 / IM-03 — Opening-range breakout (ORB)

**Verdict:** DON'T BUILD as a standalone edge (own data: ≤ 1 bp/trade net; ≈ 0R with the paper's risk sizing) · **Grade:** B in the literature, **C** on own data · **Prop fit:** High if it worked


## Own-data validation (rounds 2–3; [REPORT.md](../../research/validation/REPORT.md))

| Test | Data | Result |
|---|---|---|
| **Variant A** (Zarattini & Aziz): first 5-min candle direction, entry at the 09:35 open, stop at the candle's opposite extreme, 10R target or close | HistData US500 + US100, 2014–25 | +2.57 bps/trade gross, t = 3.16; **net +1.07**; 2023 → +0.82 (p = 0.29). PARTIAL |
| Variant A with the paper's **risk sizing** (post hoc) | same | Median stop 12 bps (US500) / 20 bps (US100). Gross +0.14R / +0.16R; **net of 1.5 bps: −0.02R / +0.05R** (t = −0.4 / 1.2). Costs take the edge |
| **Variant B**: 09:30–10:00 range, stop entry, stop at the opposite edge, exit 15:59 | same | +2.47 bps gross, t = 2.39; **net +0.97**; 2023 → +3.81 (p = 0.034). PARTIAL (Holm p = 0.062) |
| A and B on **earlier years** (R3, R4, unseen) | 2010-11 → 2013 | +1.69 (t = 1.21) and +1.65 (t = 0.84). Not replicated, but only 35–50% power |

**Bottom line:** the ORB effect is small, positive and consistent in sign. At about 1 bp per trade net
of costs, it isn't a standalone prop edge. The published returns rely on zero-cost fills and
risk-based leverage.

## Claim

A move out of the early-session range (or away from the open) tends to continue for the rest of the
session.

## "ORB" means three different rules in the evidence. Keep them separate.

| Variant | Source | Level | Rule | Sample | Result |
|---|---|---|---|---|---|
| **A. First-candle direction** | Zarattini & Aziz (2023), SSRN 4416622 | V1 (WP) | Direction = sign of the first 5-min candle (skip doji). Enter at the **open of the 2nd 5-min candle**. Stop = first candle's low (long) / high (short). Target 10R, else exit at close. Size = min(1% risk / $R, 4× leverage) | QQQ, 1 Jan 2016 – 17 Feb 2023; $0.0005/share commission; **no slippage** | 1,795 trades (51% long); win rate 24%; +0.13R/trade; annualised 31%, Sharpe 1.12, alpha 33%/yr, beta ≈ 0 |
| **B. Timely range breakout (TORB)** | Tsai et al. (2019), *IEEE Access* 7 | V1 | Range over a "probing time" after the **underlying cash-market open**, then breakout entry; session aligned to cash hours | 1-min data, DJIA, S&P 500, NASDAQ, HSI, TAIEX index futures, 2003–2013; cost 0.01%/trade | > 8%/yr, p < 3% in all 5 markets; TAIEX 20.28%/yr. **Probing time chosen per market by searching all values** (in-sample); short for US, long for Asia |
| **C. Threshold from the open** | Holmberg, Lönnbark & Lundström (2013), *FRL* 10(1) | V1 | Long/short when price moves a set % **above/below the day's open** (Crabel contraction/expansion); tested with daily OHLC only | US crude oil futures, 30 Mar 1983 – 26 Jan 2011, bootstrap | Returns significantly > 0; success rate above a fair game |
| Practitioner origin | Crabel (1990), book | — | ORB, NR4/NR7 | — | — |

## Contrary and decay evidence

- All three variants are **single-study** results; two are short samples (A: 7 years), and variant A assumes **no slippage**.
- TORB's parameter was selected in-sample, so its reported p-values overstate significance.
- Intraday momentum (IM-01) regime dependence probably applies here too (Rosa, 2022).

## Paper-exact specs to replicate first

```
A (Zarattini):  bar = 5 min; o1,h1,l1,c1 = first bar after cash open
                dir = +1 if c1 > o1, −1 if c1 < o1, skip if |c1 − o1| < doji_eps
                entry = open of bar 2; stop = l1 (long) / h1 (short); R = |entry − stop|
                exit = first touch of entry + 10R·dir, or stop, or last bar close
                size = floor(min(A·0.01 / R, 4·A / entry))
B (TORB):       range = [cash_open, cash_open + probe);  probe ∈ pre-registered grid, e.g. {5, 15, 30, 60} min
                stop-entry at range high / low; exit at session close (or the paper's stop, if specified)
C (Holmberg):   long if H ≥ Open·(1 + θ), short if L ≤ Open·(1 − θ); θ fixed in advance or from trailing vol
```

## Replication targets (known answers)

Variant A on QQQ 5-min bars, 2016-01-01 → 2023-02-17: about 1,790 trades, win rate ≈ 24%, mean ≈ +0.13R
per trade before slippage. If your win rate is far above 30%, the stop or entry logic is wrong.

## Adapting to SQX

- US100, US500, GER40, XAUUSD, WTI, on cash-session anchored times. Custom block for the first bar or range of the **cash** session.
- Variant A needs a market order at the next bar open. Variant B needs stop orders at the range, plus order expiry at the entry deadline.
- Exit at end of day always. One trade per day. **Add slippage**: 1 tick on stop fills, and opening-auction spread for variant A.

## Falsification tests (pass criteria)

1. Replicate variant A's trade count and win rate on QQQ/US100 in the paper window.
2. Net of realistic slippage, the mean R per trade stays > 0 on ≥ 3 markets.
3. **Probe-length plateau** (variant B): profitable across neighbouring probe lengths, not just one.
4. Narrow-range days (range / ATR low tercile) ≥ wide-range days; that is the Crabel prediction.
5. Post-2023 data (outside every paper's sample) is not negative.

## Open questions

- Which variant survives costs on CFDs? A is simplest; B is closest to how prop traders execute.
- Does the 10R target matter, or is exit-at-close enough? Test both, pre-registered.
