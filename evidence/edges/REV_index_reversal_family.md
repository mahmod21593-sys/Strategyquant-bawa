# REV — Short-term reversal family in equity indices (MR-06 is one member)

**Verdict:** BUILD as the core sleeve. It is the only **edge family** in nine rounds (round 9, [REPORT.md](../../research/validation/REPORT.md) §19) · **Grade:** A− on own data (family-level, multiple-testing adjusted) · **Prop fit:** High as an ensemble, needs overnight holds · **Markets:** US500, US100, US30, US2000, JP225. **Not** GER40, UK100, AUS200

## Claim and mechanism

After short-term weakness, US index products (and the Nikkei) earn above-normal returns over the next
one to few sessions. The signal can be consecutive down closes, a close near the day's low, a low RSI(2)
or a fresh N-day low; the effect is the same. The mechanism is liquidity provision against index-level
price pressure:
- Baltussen, van Bekkum & Da (2019, *JFE*): index-level serial dependence turned negative as index products grew.
- Nagel (2012, *RFS*): reversal returns as compensation for liquidity provision.

## Evidence (own data, pre-registered in A22)

| Test | Result |
|---|---|
| Grid | 8 indices × 12 signals × 3 exits × 3 filters = **864 variants**; discovery 1993–2012, validation 2013-01 → 2026-08 |
| Hansen SPA, validation (does any variant beat zero after data snooping?) | **p = 0.031** on timing value (P&L minus exposure × the index's same-year mean); 0.0125 with an expanding-mean benchmark; 0.0005 raw |
| CSCV probability of backtest overfitting | **0.19**: picking the in-sample best usually picks a good out-of-sample variant |
| Selection test | The top 10% of discovery variants beat the rest in validation (Mann–Whitney z = 7.0) |
| Walk-forward (re-pick the top 5 each January on past data) | **Sharpe 0.47, t = 2.1** on timing value; raw 0.69, t = 2.9 |
| Romano–Wolf survivors (family-wise 5%) | US100 **IBS < 0.10, exit at the first up close** (timing Sharpe 0.96, 23 trades/yr); US100 **RSI(2) < 20, first up close** (0.80, 28 trades/yr). 17 survive on raw P&L |
| Breadth | 79–94% of each US index's 108 variants have positive timing value in 2013–26. JP225 per-index SPA p = 0.007 |
| Ensemble (every variant, weighted by discovery volatility) | US100: validation Sharpe **1.00 (t = 4.7)**; 4 US indices + JP225: 0.90 (t = 4.0) |
| Independent bets | ≈ 8 effective bets among the 432 US variants (median correlation 0.28); US vs JP225 ≈ 0.1 |
| Costs | +3 bps per trade leaves 95% of US variants positive |
| Earlier rounds | MR-06 (three down closes): confirmed out of sample 2013 → ; 15:55 entry works; about half the edge is intraday; 2026 +44 bps over 23 trades |

## Parameter map (median validation timing Sharpe over the US variants)

| Choice | Best | Weaker |
|---|---|---|
| Signal | IBS < 0.10 (0.44); 2/3/5 down closes, RSI(2) < 10–20, 5-day low (0.33–0.34) | 4 down closes (0.22), return < −1.5σ (0.09) |
| Exit | First close above the prior close, max 5 days (0.38); next close (0.34) | Fixed 3 days (0.20) |
| Filter | None (0.37); only below SMA(200) (0.35) | **Only above SMA(200) (0.19)**: the popular uptrend filter hurts |
| Market | US100 > US500 > US2000 > US30; JP225 | GER40, UK100, AUS200 (no edge) |

## SQX build spec (ensemble)

```
Markets:  US500, US100, US30, US2000 (index CFDs or micro futures), optional JP225
Signals (each a separate strategy):
  IBS = (C - L)/(H - L) < 0.10 | < 0.25
  RSI(2) (Wilder) < 5 | < 10 | < 20
  k consecutive lower closes, k in {2, 3, 5}
  close = lowest close of 5 | 10 days
Entry:    at the close of the signal day (or 15:55 ET with the running 15:55 price for US markets)
Exit:     first close above the previous close, max 5 sessions  | or next close
Filter:   none, or only when close < SMA(200)  (not the "above SMA(200)" filter)
Stops:    catastrophic only (e.g. 3 x ATR); stops hurt mean reversion
Sizing:   volatility-scaled per strategy; cap total gross exposure per index (signals cluster on crash days)
Portfolio: pick 10-20 per market from Tier 1/2 of research/strategy_library.csv, de-duplicated at correlation 0.6
Prop:     EA daily guard 2-3%; account type that allows overnight + weekend holds (FTMO Swing)
```

## Prop results (post hoc ensemble, [prop_ensemble.py](../../research/validation/prop_ensemble.py))

- **Setup:** weights from pre-2013 data; exact per-index intraday lows; bootstrapped from 2013–26; 1× ≈ 15% annual volatility.
- **FTMO 2-Step:**
  - 1×: 70% pass (zero edge 26%), $7,649 per attempt, 17 months, $452 per account-month;
  - 2×: 52% pass, $995 per account-month;
  - CPPI k = 10: 74% pass (zero edge 12%).
- **FTMO 1-Step, US + JP225, 2×:** 49% pass (zero edge 18%), $1,103 per account-month.
- **Treat these as upper bounds.** The ensemble idea came after the family result, and 2013–26 is also the period that qualified the family.

## Known risks

- **Crash clustering:** signals fire together in sell-offs (2008, 2020, 2022), so exposure concentrates in the worst weeks. Cap gross exposure and use the daily guard.
- **Regime:** stronger since 2020 (volatile). Absent before 1990 on US data. US-centred.
- **Weekend holds:** a Standard FTMO funded account forbids them. Skip Friday signals there (for MR-06 this cost about a third of the value in 2014–25).
- **Futures prop firms** that force flat by the close can't hold it. Only the intraday half works there (MR-08, weak).

## Falsification tests for the SQX build

1. On the broker's data, 2013 → : ≥ 80% of the chosen variants have positive net P&L, and the ensemble has Sharpe > 0.5.
2. The "above SMA(200)" filter is worse than no filter (a mechanism check).
3. The ensemble survives +3 bps per trade.
4. The per-market ensembles on DAX, FTSE and ASX show no edge. A positive result there would mean the build differs from this research.
