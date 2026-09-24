# IM-04 — "Noise area" intraday momentum (Zarattini, Aziz & Barbon)

**Verdict:** BUILD (after IM-01 works) · **Grade:** B− (single working paper, practitioner authors, strong detail) · **Prop fit:** High

## Evidence

| Source | Level | Sample | Result |
|---|---|---|---|
| Zarattini, Aziz & Barbon, "Beat the Market", SSRN 4824172 (v. 3 Feb 2025) | V1 (WP) | SPY, 2007 – early 2024; $100k start; commission $0.0035/share + slippage $0.001/share | See table below |

| Version (paper's Table 2) | Total | IRR | Vol | Sharpe | Hit | Max DD |
|---|---|---|---|---|---|---|
| Stop at opposite band, 100% sizing | 178% | 6.2% | 10.9% | 0.61 | 54% | 21% |
| Stop = current band or VWAP, 100% sizing | 380% | 9.7% | 7.7% | 1.24 | 43% | 12% |
| Same + dynamic sizing (2% daily vol target, ≤ 4×) | 1,985% | 19.6% | 14.3% | 1.33 | 43% | 25% |
| SPY buy-and-hold | 227% | 7.2% | 20.2% | 0.45 | 54% | 56% |

**Caveat:** most of the jump from 0.61 to 1.24 Sharpe comes from one design change, the exit rule. That
was chosen with the full sample in view. Treat 0.61 as the conservative baseline and 1.24 as an upper
bound.

## Paper-exact spec

```
For each day t and each intraday time HH:MM (market hours, 30-minute grid):
  move(t−i, HH:MM) = | Close(t−i, HH:MM) / Open(t−i, 09:30) − 1 |,  i = 1..14
  sigma(t, HH:MM)  = mean_i move(t−i, HH:MM)
  UB(t, HH:MM) = max(Open(t, 09:30), Close(t−1, 16:00)) × (1 + sigma)
  LB(t, HH:MM) = min(Open(t, 09:30), Close(t−1, 16:00)) × (1 − sigma)
Signals evaluated ONLY on :00 / :30 marks:
  price > UB → long;  price < LB → short;  opposite-boundary cross → flip
Trailing stop (checked on the same marks): long = max(UB, VWAP), short = min(LB, VWAP); VWAP from market-hours data
Flat at 16:00.
Sizing: shares = AUM(t−1) × min(4, 0.02 / sigma_SPY(t)) / Open(t);  sigma_SPY = 14-day stdev of daily returns
```

## Replication targets

SPY 2007 → early 2024, 100% sizing, VWAP stop, same costs: Sharpe around 1.2, hit rate around 43%, max
drawdown around 12%.

## Adapting to SQX

- Needs a **custom indicator**: per-time-of-day average absolute move from the open over 14 days. It isn't a standard SQX block. VWAP is also required (custom if absent).
- CFD volume for VWAP is tick volume, not real volume. Test with futures data if possible, or use TWAP as a documented substitute.

## Falsification tests

1. Paper-window replication (above).
2. Post-2024 data is not negative.
3. Robust to lookback 10/14/20 days and a 15/30/60-minute grid (plateau, not peak).
4. Works on at least one more index (US100 or GER40) with unchanged parameters.
