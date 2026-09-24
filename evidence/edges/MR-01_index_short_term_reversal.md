# MR-01 / MR-02 / MR-03 — Short-term mean reversion in equity indices

**Verdict:** BUILD, **US indices first**, other indices only after they pass on their own · **Grade:** B · **Prop fit:** High (with Friday exit and gap stress)

## Claim

After short-term weakness, especially a close near the day's low, index returns over the next 1–5 days
are above average.

## Evidence

| Source | Level | Sample | Result |
|---|---|---|---|
| Baltussen, van Bekkum & Da (2019), *JFE* 132(1) | V1 | 20 indexes, 15 countries | Index serial dependence **positive until the 1990s, negative since the 2000s**, in most markets; linked to index products (futures, ETFs) and index arbitrage. Trading against weekly MAC(5) serial dependence: Sharpe **0.63** (all indexes) / **0.67** (S&P 500) after 2 Mar 1999, vs 0.36 average buy-and-hold (costs not stated) |
| Pagonidis (2013), NAAIM | V1 (practitioner) | US and international equity-index ETFs, early 1990s – 2013 | IBS < 0.2 → next day **+0.35%**; IBS > 0.8 → **−0.13%**. Non-linear (thresholds ~0.4 / ~0.9). Stronger in high volatility, after high-range days, on Mondays; **disappears on low-volume days (US)** |
| Pagonidis (2013) | V1 | Local ETFs: France, Australia, Germany, Spain, Switzerland, Taiwan, UK | **Little or no IBS effect outside the US.** After 2008, international-ETF IBS depends on SPY's IBS |
| Pagonidis (2013) | V1 | — | IBS-only trading is badly hurt by commissions. Best used as a **filter** on a longer mean-reversion rule (e.g. RSI(3) on QQQ) |
| Nagel (2012), *RFS* 25(7) | V1 | US stocks and industries, 1998–2010 (cross-sectional) | Reversal returns are the payoff to liquidity provision; strongly predictable by VIX, spiking in crises. **Indirect** evidence for index MR |
| Baltussen, Da, Lammers & Martens (2021) | V1 | 62 futures | The last-30-minute momentum move **reverses over the next 3 days** (MR-04) |
| Connors & Alvarez (2009), book | — (not verified) | — | RSI(2) dip-buying above the 200-day MA; practitioner rules |

## Contrary and decay evidence

- IBS looks **US-centric** (Pagonidis), while index-level negative autocorrelation looks **global** (Baltussen et al.). The two measures differ, so each market must pass on its own.
- A practitioner blog (Price Action Lab, 2021, V3) reports S&P 500 autocorrelation below −0.35 from March 2020 to March 2021, then near −0.07. The effect is **time-varying and may be weakening**.
- Negative skew: large losses in trending selloffs (Q4 2008, Feb–Mar 2020).

## Paper-exact specs to replicate first

```
IBS (Pagonidis):  IBS_t = (C_t − L_t) / (H_t − L_t);  bucket into [0,.2) [.2,.4) [.4,.6) [.6,.8) [.8,1]
                  target: next close-to-close return C_{t+1}/C_t − 1
                  report per bucket; split by C_t vs SMA200 and by volume / volatility terciles
MAC(5) (Baltussen et al.): weekly multi-period autocorrelation of daily index returns; trade against its sign
Long-only dip rule (MR-01): C_t > SMA200 and IBS_t < 0.2 → buy the close, exit next close
                            (or first close > previous high; pre-register one)
N-day low (MR-02): C_t < min(C_{t−5..t−1}) and C_t > SMA200 → forward 1/3/5-day returns
```

## Replication targets

SPY daily, about 1993–2013: mean next-day return for IBS < 0.2 clearly positive, and IBS > 0.8
negative; the order of magnitude should be close to +0.35% / −0.13% (the paper averages across ETFs).

## Adapting to SQX

- Needs an **IBS custom block**. Entry must happen **at or just before the cash close** (the effect lives in the close). On CFDs, use the cash-close time, not the midnight daily bar.
- Measure the edge as the **excess over the same year's average day** to remove equity drift.
- Wide catastrophic stop only; time exit (Kaminski & Lo, 2014: stops subtract value under mean reversion).

## Falsification tests

1. US500 and US100 pass Gate 1 on their own; GER40, UK100 and JP225 are tested separately. Expect weaker results.
2. Stronger in high-volatility terciles (Nagel / Pagonidis mechanism check).
3. Positive in 2014–2019 and 2021+ separately (not only 2008 and 2020).
4. Survives realistic close-of-day costs (spread at the close, 1-day holds).
