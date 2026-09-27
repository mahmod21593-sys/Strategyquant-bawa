# Round-11 negatives: FX, metals and European-index families built for prop accounts

**Verdict:** DON'T BUILD. Pre-registered in A24, tested with the round-9 battery · **Source:** [REPORT.md](../../research/validation/REPORT.md) §21.3 · **Data:** HistData 1-minute bars, no window touching 16:45–19:00 NY.

| Family (variants) | Result | Why it fails |
|---|---|---|
| L. FX and gold session seasonality: long or short Asia 00–07, Europe 07–12, overlap 12–16, US afternoon 16–21 London; 7 majors + gold (64) | SPA 1.00, walk-forward Sharpe −0.33 | The Breedon–Ranaldo pattern (a currency is weak in its home hours) held in 2003–13: EURUSD and GBPUSD short in European hours, Sharpe 0.53 / 0.50. After 2013: 0.08 / 0.07. Gross effects are now ≈ 1 bp per window; gold long in Asian hours is +2.0 bps gross, below its 2.5-bp cost |
| M. FX night mean reversion: fade M15 closes outside BB(20; 1.5, 2, 2.5) or RSI(3) < 10 / > 90, 19:00–00:45 NY; exits at the middle band, after 1 hour, or at 01:00; 6 crosses + 3 majors (108) | All 108 negative in 2016–26 (median Sharpe −2.5); walk-forward −2.1 (t −7.1) | Night reversion exists gross (median +0.14 bps per trade) but is a tenth of night spreads (1.5–3 bps round trip) |
| Q. European cash-open gap: fade or follow gaps above 0.5 / 1 / 1.5 × the 20-day mean; exits at 11:00, 13:00, the close, or a gap-sized bracket; GER40, UK100, FRA40 (72) | SPA 1.00, walk-forward −0.34 | Gap-follow on FRA40 and GER40 worked in 2013–19 (Sharpe 0.4–0.7) and faded after 2020 (≤ 0.21); fades lose |
| R. Session-range breakout or fade: the Asian range traded 07–12 London, or the London-morning range traded 13–16; gold, silver, EURUSD, GBPUSD, USDJPY, AUDUSD (48) | **EDGE by the rule** (SPA 0.031, PBO 0.0005), but walk-forward Sharpe 0.005, and 43 of 48 variants negative | USDJPY alone: without it, SPA 0.59. The one lead is the London-afternoon breakout ([SQX_build_matrix.md](SQX_build_matrix.md) §4): news-driven (17.5% of entries at US data times), and halved by +1 bp of slippage |

**What round 11 confirms about FX and metals.** Together with earlier rounds, these families have now been tested:
- reversal on FX, gold, silver, oil and gas (family E);
- per-market trend (F);
- G10 carry and currency momentum (D);
- the FX fix windows and month-end hedging flows (FX-01, FX-02, FX-03);
- the Asian-range London breakout (VB-02);
- noise-area momentum on gold (N5);
- a 653-candidate scan on 24 instruments.

**No FX or metals rule survives retail costs on bid-quote data.** Gross effects of 1–3 bps exist in a few
places: the London-afternoon breakout on USDJPY, GBPUSD and gold; silver's pre-fix hour; gold's Asian-session
drift. They are leads for raw-spread accounts, re-tested on bid/ask data, not builds.
