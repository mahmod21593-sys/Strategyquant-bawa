# IM-01 / IM-05 — Market intraday momentum (trade the last 30 minutes)

**Verdict:** DON'T BUILD (failed own-data validation, rounds 1–3) · **Grade:** B in the literature, **not supported** on 2014–25 data · **Prop fit:** High if it worked


## Own-data validation (rounds 1–3; [REPORT.md](../../research/validation/REPORT.md))

| Test | Data | Result |
|---|---|---|
| P7 Baltussen: sign(prior close → 15:30) held 15:30 → 16:00 | HistData US500 2014–25 | +0.20 bps, t = 0.43. 2014–21 +0.43, 2022–25 −0.30 (difference p = 0.50). **No momentum, no regime flip** |
| P8 Gao: sign(prior close → 10:00) held 15:30 → 16:00 | same | **−1.23 bps, t = −2.55 (opposite sign)** |
| P9 Rosa threshold (\|signal\| > 1 sd) | same | −0.36, t = −0.29 |
| P13 next-day reversal of the last 30 min | same | +1.35, t = 0.65 |
| P7y on Yahoo ETFs | 2023–26 | −1.72, t = −2.78. HistData agrees on the overlapping days (correlation 0.98): a 2024–25 reversal, not a new regime |
| **GER40 close (17:00 → 17:30 Berlin), P12** | HistData 2014–25 | **+2.07 bps, t = 4.85; net +0.57** (−0.18 from 2022) |
| GER40 on **earlier years** (R2, unseen) | 2010-11 → 2013 | **−0.24 bps, t = −0.24** (80% power): not replicated |
| Same rule on CAC 40, Euro Stoxx 50, FTSE 100 (R1, unseen) | 2014–25 | +1.01 bps, t = 2.99, **net −0.49** |

**Bottom line:** in 2014–25 CFD quotes, market intraday momentum isn't there in the US (the Gao
version is significantly reversed). The European close version is statistically real in 2014–25, but
it vanishes in 2010–13 and is below retail costs.

## Claim

The market's return earlier in the day predicts its return in the last 30 minutes before the close, in
the same direction.

## Evidence

| Source | Level | Sample | Predictor → target | Key result |
|---|---|---|---|---|
| Gao, Han, Li & Zhou (2018), *JFE* 129(2) | V1 | SPY (TAQ), Feb 1993 – Dec 2013; also 10 other ETFs; S&P futures similar | r1 = prior close → 10:00 ET ⇒ r13 = 15:30 → 16:00 ET (r12 = 15:00 → 15:30 adds power) | Predictive R² 1.6% (r1), 2.6% (r1 + r12); OOS R² 1.4% / 2.0%. Timing (sign of r1): 6.67%/yr, sd 6.19%, Sharpe 1.08 vs buy-and-hold 0.29. Stronger on high-vol, high-volume, recession and macro-news days (FOMC days ≈ 20%/yr annualised) |
| Gao et al., costs section | V1 | Post-decimalisation Jul 2001 – 2013 | Bid/ask at 15:30, closing auction at 16:00, commissions ignored | Timing falls to 4.46%/yr after spreads (−2.47%); since 2005, 6.52% after vs 7.96% before. SPY spread ≈ 1.2 bps after 2005 |
| Baltussen, Da, Lammers & Martens (2021), *JFE* 142(1) | V1 | 62 futures (17 equity, 16 bond, 21 commodity, 8 FX), Dec 1974 – May 2020 | r_ROD = prior close → close − 30 min ⇒ r_LH = last 30 min | r_ROD predicts r_LH in all asset classes, robustly over time; beats Gao's predictor out of sample. Timing Sharpe **0.87–1.73** per asset class **before costs** (costs "not considered"). Last-30-minute move **reverses over the next 3 days** |
| Baltussen et al., mechanism | V1 | S&P 500 option dealer gamma (SqueezeMetrics); leveraged-ETF rebalancing | — | Momentum present when dealers are short gamma, and stronger the shorter they are. It can vanish or reverse when dealers are long gamma. Leveraged-ETF hedging drives magnitude |
| Li, Sakkas & Urquhart (2022), *JFM* 57 | V2 | 16 developed markets | First → last half-hour | Significant in and out of sample in most markets; stronger with low liquidity, high volatility, discrete information |
| Zarattini, Aziz & Barbon (2024/25), SSRN 4824172 | V1 (WP) | SPY 2007 – early 2024 | See IM-04 | Intraday momentum still profitable net of costs through 2024 |

## Contrary and decay evidence

| Source | Level | Finding |
|---|---|---|
| Rosa (2022), *J. Futures Markets* 42(12):2218–2234 | V2 | "The predictability **disappears in the out-of-sample period**." Markov-switching: predictability depends on signal strength; "a strategy with thresholds delivers higher returns than a strategy that is always active" |
| Dim, Eraker & Vilkov (2024), SSRN 4692190 | V3 | Positive (negative) dealer gamma strengthens intraday reversal (momentum). The 0DTE era (2022+) may change the regime |
| Baltussen et al. (2021) | V1 | Authors warn the strategy "might not be exploitable to many investors after accounting for transaction costs" |

**Reading of the evidence:** the effect is real and pervasive (62 futures over 45 years), but it is
**small per trade and regime-dependent**. It is concentrated on large-signal and high-volatility days.
Unconditional, always-on versions have weakened since Gao's sample. Implement it **with a signal-size
threshold** (Rosa) and **test on post-2013 and post-2022 data separately**.

## Paper-exact specs to replicate first

```
Common: US cash session 09:30–16:00 America/New_York; bars M1/M5/M30; trading day = close(t−1) → close(t).

GAO (IM-01a)
  r1   = P(10:00) / P_close(t−1) − 1
  r12  = P(15:30) / P(15:00) − 1
  r13  = P(16:00) / P(15:30) − 1
  signal_a = sign(r1);  signal_b = sign(r1) if sign(r1) == sign(r12) else 0
  position = signal over 15:30 → 16:00 only; flat otherwise

BALTUSSEN (IM-01b)
  r_ROD = P(close − 30m) / P_close(t−1) − 1
  r_LH  = P(close) / P(close − 30m) − 1
  signal = sign(r_ROD);  position over the last 30 minutes

ROSA THRESHOLD VARIANT (IM-05)
  trade only if |signal return| > k × rolling_sd(signal return, N days); k and N are PRE-REGISTERED
  (e.g. k ∈ {0.5, 1.0}, N = 60). No free search.
```

## Replication targets (known answers)

On SPY Feb 1993 – Dec 2013, a correct implementation should give roughly: r1 → r13 slope positive with
R² ≈ 1.6%; sign(r1) timing ≈ 6.7%/yr gross with sd ≈ 6.2%, Sharpe ≈ 1.1. Small differences are expected
from data vendors. **A wrong sign or R² near zero on this window means a bug**, not a finding.

## Adapting to SQX

- Instruments: US500 / US100 CFDs or ES/NQ futures. Also GER40 (09:00–17:30 Frankfurt), and gold, oil and bonds on their own cash sessions (Baltussen: all asset classes).
- Needs a **custom block for the session-anchored return** (prior cash close → T−30). SQX's built-in daily open/close won't align with the cash session on a near-24-hour CFD.
- Entry at T−30 min as a market order; exit at the cash close (limit time range + exit at end of range). One trade per day.
- **Costs:** model the spread at 15:30 (wider than average) plus commission. Gao's post-2001 result lost about 35% to spreads alone.

## Falsification tests (pass criteria)

1. Paper-window replication matches the targets above (implementation check).
2. **Post-2013 and post-2022 subsamples:** timing return > 0 net of costs in each, or the edge is regime-limited. Report both.
3. **Mechanism:** returns rise from low to high tercile of |signal| or of same-day realised volatility.
4. **Cross-market:** ≥ 3 markets positive net of costs with the same rule.
5. **Next-day reversal present** (Baltussen). If absent, question the hedging mechanism in this instrument.

## Open questions

- Are CFD closing prices at 16:00 ET representative of the futures or cash close? Check CFD vs futures data around the close.
- Does the 0DTE era (2022+) help or hurt? Test separately; don't pool.
