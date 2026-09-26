# VB-02 — Asian-range breakout at the London open

**Verdict:** DROP. Tested in round 7 (G8): real before costs, negative after · **Prop fit:** —

## Own-data result (round 7, G8, pre-registered in A15)

- **Rule:** range 00:00–06:59 London; first touch 07:00–11:59; stop at the other side of the range; exit 16:00 London.
- **Data:** EURUSD + GBPUSD, HistData 2014–25 with the corrected clock; 258 trades a year.
- **Result:** +1.14 bps per trade gross (t = 2.54), but **−0.12 net** at 1.0 / 1.5 bps cost. 2026 holdout −0.6 gross.
- **Conclusion:** the breakout direction carries information, but less than a retail spread. Not tradeable.

## Evidence status

| Item | Level | Finding |
|---|---|---|
| Peer-reviewed tests of the rule | — | **None found** (search Sep 2026). Only practitioner guides and blog backtests |
| Volatility jump at European open / low Asian-session volatility | V2 | Andersen & Bollerslev (1997); Ranaldo (2009) |
| Dollar reversal around the London fix (Krohn, Mueller & Whelan, 2024) | V1 | USD tends to **rise from European open into the 16:00 London fix, then fall**. A naive "breakout continues all day" assumption may run into this reversal. Direction of break vs USD matters |
| Intraday momentum in FX with fixed trading hours (Elaut et al., 2018; RUB on MICEX) | V2 | First → last half-hour momentum, driven by liquidity providers avoiding overnight inventory; weak transfer to 24-hour FX |

## Spec to test (pre-registered, no mining)

```
Range: 00:00–07:00 Europe/London (or 00:00–08:00); entries: stop orders at range high/low, 07:00–10:00 London;
exit: 16:00 London (before/at the fix) — compare with exit at 12:00 and at NY close
Filters (at most one): range width / ATR(14) low tercile
```

## Falsification tests (Grade C bar)

Pooled t ≥ 3 across ≥ 4 pairs (EURUSD, GBPUSD, USDJPY, XAUUSD); positive in ≥ 60% of years; survives
1.5× costs; breakout direction interacted with USD side is consistent with the Krohn et al. pattern (or
explicitly contradicts it with evidence).
