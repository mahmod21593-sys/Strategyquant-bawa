# Round-10 negatives: seven more families that add nothing

**Verdict:** DON'T BUILD (pre-registered in A23; same battery as round 9) · Source: [REPORT.md](../../research/validation/REPORT.md) §20

| Family (variants) | Result | Why it fails |
|---|---|---|
| E. Reversal outside equities: gold, silver, oil, gas, EURUSD, GBPUSD, USDJPY, AUDUSD, BTC, ETH (2,160) | SPA 0.25, walk-forward −0.02 | The index-reversal effect is specific to equity-index products |
| F. Per-market trend: Donchian 20/55/100, MA 10/50, 20/100, 50/200, momentum 20/60/120; 22 markets (396) | No timing value (SPA 0.47). Raw SPA 0.02 comes from Bitcoin's drift | Long-only trend on a rising asset is beta, not timing |
| G. Index-pair relative value (324) | SPA 1.00 | Two legs of cost and financing; no convergence edge |
| H. Calendar: turn of month, weekday, pre-holiday (176) | SPA 0.46 (timing), 0.11 (raw) | Published calendar effects are arbitraged |
| I. Crypto trend, 2019 top-8 coins (160) | SPA 0.48; negative at 10%/yr financing | Bitcoin's 2015–21 trend profits don't generalise |
| J. Reversal grid on HK50, EU50, FRA40, SPA35, Nasdaq Composite (540) | SPA 0.017 by rule, but it comes from the Nasdaq Composite (= US100) and one isolated EU50 variant | No new market. It lowered the portfolio's out-of-sample Sharpe |
| K. Cross-sectional weekly reversal, large US stocks (12) | All negative in 2014–26 | Gone in large caps after costs |

**Data lesson:** Yahoo daily FX bars fake a reversal edge (IBS vs next-day return correlation −0.69).
Clean HistData bars show none. Never use them for close-anchored rules.
