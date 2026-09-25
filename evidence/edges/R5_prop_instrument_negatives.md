# Round-5 negatives: what not to build on prop instruments

**Verdict:** DON'T BUILD (all tested, pre-registered, on data after each paper's sample) · Source: [REPORT.md](../../research/validation/REPORT.md) §14

This card exists so the coding agent doesn't spend time re-testing these. Each line is a pre-registered
test on data the source paper didn't use, net of realistic CFD costs.

| Idea (source) | Instrument | Result after the paper's sample | Why it fails |
|---|---|---|---|
| Commodity intraday momentum (Baltussen et al. 2021, *JFE*) | Gold, silver, WTI | +0.4 bps/day (t = 0.9); was +2.3 (t = 3.2) in the paper's period | Decayed after publication; below 2.5–5 bps costs |
| Crude oil: first half-hour → last half-hour (Wen et al. 2021) | WTI (Brent secondary) | −0.2 bps (t = −0.2) | Never present in my data |
| EIA-day third half-hour → last half-hour (Wen et al. 2023) | WTI, Brent | −3.3 bps (t = −1.5) | Wrong sign |
| Bitcoin intraday momentum (Shen, Urquhart & Wang 2022) | BTC | −0.3 bps (t = −0.4) | The paper's own break-even was 3 bps |
| Bitcoin long 22:00–24:00 UTC (Padyšák & Vojtko 2021) | BTC | +1.5 bps (t = 0.9) vs 5-bps cost | Mostly BTC's own drift (+0.55 per 2 h) |
| Bitcoin Monday effect (Caporale & Plastun 2019) | BTC | +26 bps Monday excess (t = 1.4) | Not significant |
| Asian index intraday momentum (Baltussen et al.) | JP225, AUS200 | +0.75 bps (t = 2.3) | Real but below the 3-bps cost |
| Crypto weekend → Monday equities (2025 *FRL*), traded from the Sunday futures reopen | US500 | −8 bps (t = −0.5) | The predictable part is in the gap before futures reopen |
| MR-06 on 15 untested world indices | IBEX, AEX, FTSE MIB, KOSPI, TWII, Sensex, Bovespa… | +2.8 bps pooled (t = 1.2) | US-centred effect |
| Noise-area momentum (Zarattini et al.) on US500, GER40, gold | — | Sharpe 0.15–0.44, n.s. | Works only on US100 (see IM-04) |
| **653-candidate scan**: hour-of-day, day-of-week, streaks, IBS, 20-day breakouts on 24 instruments | Indices, metals, energy, FX majors/crosses, BTC, ETH | 20 discovered in 2011–17, **0 confirmed** in 2018–25 | Discovery-period effects shrink out of sample |

**The one near-miss:** silver falls in the hour before the 12:00 London silver fix (06:00–07:00 NY):
−5.1 bps in 2011–17, −2.4 bps in 2018–25 (Holm p = 0.006). It is real but below a 5-bps silver CFD
cost. Worth a look only with a broker whose silver spread is ≤ 1.5 bps at that hour.
