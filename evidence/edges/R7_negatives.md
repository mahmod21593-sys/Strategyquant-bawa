# Round-7 negatives: what not to build

**Verdict:** DON'T BUILD (each pre-registered in A15–A18, on data after each paper's sample where one exists) · Source: [REPORT.md](../../research/validation/REPORT.md) §17

This card exists so the coding agent doesn't spend time re-testing these. Costs are realistic CFD costs;
Holm p is across the 13 family-G tests.

| Idea (source) | Instrument, period | Result | Why it fails |
|---|---|---|---|
| Halloween / "sell in May" (Bouman & Jacobsen 2002) | SPY 2002-11 → 2026-08 | winter − summer +1.6 bps/day (t = 0.58) | Not significant after publication |
| Options-expiration week strong / week after weak (Stivers & Sun 2013) | SPY 2011 → 2026 | −21.9 / +6.8 bps/week | Wrong sign on both |
| Reversal pays more when VIX is high (Nagel 2012 mechanism) | MR-06 trades 1990–2026 | +12.7 bps high − low VIX (t = 1.58) | Not significant; keep volatility-scaled size |
| Volatility-managed index exposure (Moreira & Muir 2017) | SPY 2016 → 2026 | alpha +2.7%/yr (t = 0.99); Sharpe 0.86 vs 0.86 | Gone after publication |
| Time-series momentum on prop instruments (MOP 2012; re-test of round-1 P6) | 16 ETFs + BTC 2012 → | +91 bps/month (t = 2.6) but WEAK after Holm; **+1.8%/yr after CFD financing** | Real premium, not a prop edge (see TF-01) |
| Next-day reversal of strong last-hour moves (Baltussen et al. 2021) | US500 + US100 2014–25 | +9.0 bps/trade net (t = 2.1), 2026 −0.3 | WEAK; failed holdout |
| Asian-range breakout at the London open | EURUSD, GBPUSD 2014–25 | +1.1 gross, −0.1 net | Below the spread (see VB-02) |
| Crypto funding crowding filter (Schmeling et al. 2023 mechanism) | BTC, ETH 2021 → 2026 | −1.5 bps/day | Nothing there |
| Williams volatility breakout (open ± 0.5 × prior range) | US500, US100, GER40 2014–25 | +1.5 bps/day net (t = 2.7), 2026 −1.3 | WEAK; failed holdout; strongest on US100, likely the IM-04 effect |
| NR7 breakout (Crabel 1990) | US500, US100, GER40 2014–25 | −1.0 net | Nothing there |
| Opening-gap fade (Berkman et al. 2012 mechanism) | US500, US100 2014–25; SPY 1993 → | −1.4 net; SPY −3.5 net | Nothing there |
| Cross-sectional momentum across 14 equity indices (Asness et al. 2013) | 2013 → 2026; 2000–12 | −17 and −6 bps/month net | Negative in both periods |
| **2026 holdout of rounds 2–5's WEAK/PARTIAL intraday rules** (ORBs, GER40/CAC/FTSE close momentum, Asian index momentum, scan WEAKs) | HistData 2026-01 → 09 | mean holdout t −0.15 (null rules: 0.00) | They behaved like noise, as the multiple-testing guards predicted |

**Not re-tested, with reasons (A15):** FX carry swings (multi-week holds are banned on FTMO Standard
funded accounts, and swap mark-ups eat the premium); the Asian band fade and intraday range fade (mirror
images of G8 and N1); H4-with-D1 trend and AUDJPY-with-US500 trend (no testable single specification).
The pre-holiday premium was already validated in round 1 (P18) and stays a small add-on.
