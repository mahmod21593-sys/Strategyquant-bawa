# Decay controls — published edges that have faded (don't trade; use to calibrate the pipeline)

A correct research pipeline should find these **strong in their original samples and weak or absent
afterwards**. If the pipeline says they still work, suspect look-ahead or data errors.

| ID | Edge | Original evidence | Decay evidence | Level | Control test |
|---|---|---|---|---|---|
| CF-01 | **Turn of month** (last day + first 3 days) | McConnell & Xu (2008), *FAJ* 64(2): 1926–2005, 0.15%/day at turn of month vs ≈ 0 otherwise; 31 of 35 countries | **Han, Han & Tian (2025), *FRL* 71, 106461: "disappears entirely after 2001"**; attributed to lower transaction costs (arbitrage, more frequent trading) | V2 | TOM excess strongly positive pre-2001, insignificant 2001+ |
| CF-05a | **Pre-FOMC drift** (24h before announcements) | Lucca & Moench (2015), *JF* 70(1) | Kurov, Wolfe & Gilbert (2021), *FRL* 40: essentially disappeared after 2015 | V2 | Strong 1994–2011, ≈ 0 after 2015 |
| CF-05b | **Overnight drift**, US equity futures 02:00–03:00 ET | Boyarchenko, Larsen & Whelan (2023), *RFS* 36(9): 1998–2020, ≈ 3.7%/yr | NY Fed Liberty Street (July 2026): ≈ 0 since 2021; order-imbalance dispersion halved; NightShares ETFs closed after 14 months | V2 | Positive 1998–2020, ≈ 0 2021+ |
| IM-01 (partial) | Overnight / first-half-hour → last half-hour | Gao et al. (2018) | Rosa (2022): disappears out of sample unless conditioned on signal strength | V2 | Unconditional version weak post-2013; thresholded version stronger |

**Note on CF-01:** the plan previously graded turn-of-month A−. With the 2025 evidence it is now **D for
US large caps**. Keep it only as a control, or as an overlay if Phase 1 on *your* markets shows it
alive post-2001.

## Own-data control results ([REPORT.md](../../research/validation/REPORT.md))

The pipeline passed its own calibration: every control that could be tested showed the predicted decay.

| Control | Own-data result | Verdict |
|---|---|---|
| CF-01 turn of month (P5) | S&P 500 +10.4 bps/day before 2001 (t = 3.9) → +2.2 after (t = 0.7) | **DECAY CONFIRMED** |
| CF-05b overnight drift 02:00 → 03:00 ET (Q7-P14) | HistData US500: 2014–20 +1.45 bps (t = 3.75) → 2021–25 −0.43 (t = −1.2) | **DECAY CONFIRMED** (matches the NY Fed's "≈ 0 since 2021") |
| CF-05a FOMC-day / announcement premium (Q1, related) | FOMC days +19.0 bps overall (t = 2.3) → **+0.9 after 2013** (t = 0.1); employment days +8.3 after 2013 (t = 1.2) | Decayed (PARTIAL under the rules) |
| IM-01 unconditional (Q7-P7, P8) | US500 2014–25: P7 +0.2 (t = 0.4); P8 −1.2 (t = −2.6) | Gone (P8 reversed) |
| **CF-08 FOMC cycle** (Cieslak, Morse & Vissing-Jorgensen 2019, *JF*; round 4, S1) | Even-minus-odd weeks: 1994–2016 **+12.0 bps/day (t = 3.9)**, matching the paper; **2017 → −4.8 (t = −1.1)** | **Decayed after publication.** A clean decay case: the implementation reproduces the paper exactly |
| CF-09 Treasury auction cycle (Lou, Yan & Zhang 2013; S3) | IEF around 10-yr auctions: 2002–08 +11.8 (t = 0.9); 2013 → +8.1 (t = 0.9) | Not significant in either period |
| **Commodity intraday momentum** (Baltussen et al. 2021, gold/silver/crude; round 5, T1) | 2011 → 2020-05: +2.34 bps/day (t = 3.21) → after the paper: +0.42 (t = 0.86) | **Decayed after publication** |
| Bitcoin 22:00–24:00 UTC (Padyšák & Vojtko 2021; T5) | 2017–21: +3.4 (t = 1.1) → 2022 → : +1.5 (t = 0.9), below the 5-bps cost | Not a control (never significant in my data), recorded for completeness |
