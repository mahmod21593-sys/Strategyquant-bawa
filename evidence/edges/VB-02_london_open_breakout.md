# VB-02 — Asian-range breakout at the London open

**Verdict:** TEST ONLY (Grade C, no peer-reviewed support found) · **Prop fit:** High *if* it passes

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
