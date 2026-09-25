# Own-data validation report

**What this is:** every edge in the plan tested on real market data, with the tests fixed *before*
looking at results ([PREREGISTRATION.md](PREREGISTRATION.md)). There were three rounds, each
pre-registered and committed before its data was tested:

| Round | Pre-registered | Data | Tests |
|---|---|---|---|
| 1 | Main table + A1, A2 (09:10–09:19 UTC, 2026-09-25) | Yahoo daily (13 indices, 25 ETFs); Yahoo 60-min (2023–26) | P1–P19, exploratory scan E01–E20 |
| 2 | A3, A4, A5 (13:33–13:46 UTC) | HistData.com 1-minute: US500, US100, GER40 2014–25; 9 USD pairs 2004–23 | Q1–Q7 (Q7 = the original minute-data tests P7–P14) |
| 3 | A6, A7 (14:00–14:03 UTC) | **Data not yet downloaded or inspected**: earlier years, other instruments, a later period | R1–R7 confirmation tests of the round-2 leads |

The git commit timestamps are the evidence of ordering. Every deviation is logged as an amendment.

---

## 1. Bottom line (after three rounds)

| Edge | Final status | Best evidence | After realistic costs | Prop use |
|---|---|---|---|---|
| **MR-06: next day after ≥ 3 down closes, US500/US100** | **Only edge standing.** Confirmed out of sample (round 1); survives a realistic 15:55 entry (R7: +15.9 bps, p = 0.03, 2014–25) but with less statistical margin than the daily data suggested | Daily data 1990 → : +19.8 bps, t = 4.6; 2014–25 minute data (S&P): +20 to +24 bps, t ≈ 2.3–2.7 whether entered at 15:55 or at the close | +14 to +22 bps/trade; ~19–26 trades/yr | **Weak on its own:** 37–44% pass (two-step 10%/5%) vs 33% for zero edge, and 3–18 months to pass (§11) |
| Pre-holiday | Validated (round 1) | +12.0 bps, t = 3.2 | +8.3 bps, t = 1.7 | Small add-on (~9 days/yr) |
| GER40 close momentum (17:00 → 17:30) | **Failed confirmation.** Strong 2014–25 (t = 4.9), **absent 2010–13** (−0.2 bps) and below costs on CAC/FTSE | — | +0.6 bps (2014–25), −0.2 from 2022 | No |
| Opening-range breakouts (5-min Zarattini, 30-min stop entry) | Partial: positive 2014–25 (t = 2.4–3.2), **not replicated 2010–13** (t = 0.8–1.2, low power) | +2.5 bps/trade gross | ≈ +1 bp at equal notional; **≈ 0R with the paper's risk sizing** | No, not as a standalone edge |
| FX dollar-fix windows (W1 + W4) | **Round-1 "replication" was a data artifact** (bid quotes at the NY 17:00 rollover). Clean windows: W4 gone after 2019; W1 gone in 2024–25 | — | ≈ 0 | No |
| Macro-announcement premium | Partial: +14 bps (t = 2.6), but only +5 bps after 2013; FOMC days ≈ 0 after 2013 | — | — | No |
| Overnight premium, turn of month, TSMOM timing, IBS, 5-day low, last-30-min momentum, next-day reversal of the close, crypto TSMOM | Not validated, decayed or not tradeable | — | — | No |

**The honest summary:** after testing 57 hypotheses on up to 56 years of data, one edge survives
everything: **MR-06, three down closes on US indices.** Everything intraday that looked good in
2014–2025 either failed on earlier years, was below realistic costs, or was a data artifact. A
prop challenge can't be passed *reliably* with MR-06 alone. It is a real but slow, high-variance
building block. See §12 for what this means for the plan.

---

## 2. How the tests were run

- Pre-registered: rule, prediction, sample splits, costs, statistics and verdict rules, before the data was examined. Amendments were committed before the tests they affect.
- Per test: Newey-West HAC t (lag ≥ 5), one-sided p in the predicted direction, stationary-bootstrap 95% CI (2,000 resamples), year-by-year sign share, pre- vs post-publication split, net of pre-registered cost.
- **Multiple testing:** Holm and Benjamini-Hochberg within each round's family, and pooled for rounds 1 + 2 (29 tests). Deflated Sharpe ratio with the cumulative trial count (N = 35 in round 1, 50 in round 2, 57 in round 3).
- Verdict rules are applied mechanically by [verdicts.py](verdicts.py), [verdicts_round2.py](verdicts_round2.py) and [run_round3.py](run_round3.py). **Appraisal flags** record problems found after a test ran. They never change the rule-based verdict, only its interpretation.

---

## 3. Round 1 — primary tests (all results)

| ID | Test | n | Mean bps | Net bps | t (HAC) | p (1-sided) | Holm p | Post-publication mean (p) | Years with predicted sign | DSR | 95% CI | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | IBS < 0.2 above SMA200, S&P 500, 1990 → | 1,230 | 2.72 | 1.22 | 1.14 | 0.128 | 1.00 | 2014 → : 1.94 (0.31) | 67% | 0.14 | [−1.6, 6.9] | NOT VALIDATED |
| P2 | IBS, 9 non-US indices pooled | 5,424 | −1.71 | −3.21 | −1.24 | 0.89 | 1.00 | 0.02 (0.50) | 38% | 0.00 | [−4.6, 1.1] | NOT VALIDATED |
| P3 | 5-day low above SMA200, 3-day hold, S&P + NDX | 1,175 | −2.03 | −3.53 | −0.32 | 0.63 | 1.00 | 4.63 (0.31) | 55% | 0.01 | [−13.5, 10.4] | NOT VALIDATED |
| P4 | 1-day reversal, 13 indices pooled, 2000 → | 6,954 | 0.90 | 0.90 | 1.11 | 0.13 | 1.00 | 2017 → : 1.00 (0.23) | 56% | 0.14 | [−0.6, 2.6] | NOT VALIDATED |
| P5 | Turn of month (control), S&P 1970 → | 2,723 | 6.66 | — | 3.31 | 0.0005 | 0.007 | 2001 → : 2.21 (0.24) | 58% | 0.87 | [2.5, 10.8] | **DECAY CONFIRMED** |
| P6 | TSMOM, 25 ETFs, monthly 2007 → | 236 months | 79.8 | 79.8 | 2.64 | 0.004 | 0.0498 | 2013 → : 76.6 (0.014) | 80% | 0.66 | [27, 135] | **VALIDATED** (fragile) |
| P16 | Rebalancing flows (SPY vs TLT month-end) | 252 | −26.5 | −26.5 | −2.81 | 0.998 | 1.00 | −24.4 (0.99) | 19% | 0.00 | [−46.5, −10.8] | NOT VALIDATED (opposite sign) |
| P17 | Overnight premium SPY + QQQ, 1999 → | 6,928 | 3.97 | 1.97 | 4.66 | < 0.0001 | < 0.0001 | 2013 → : 4.06 (0.0003) | 82% | 0.98 | [2.3, 5.7] | **VALIDATED** (gross; see §6) |
| P18 | Pre-holiday, S&P 1970 → | 492 | 11.98 | 10.48 | 3.25 | 0.0006 | 0.008 | 2001 → : 8.30 (0.048) | 68% | 0.84 | [4.4, 19.7] | **VALIDATED** |
| P19 | IBS trades: high-VIX minus low-VIX tercile | 877 | 8.21 | — | 1.21 | 0.11 | 1.00 | — | — | — | — | NOT VALIDATED |
| P7y | Rest-of-day → last 30 min, SPY/QQQ/IWM/DIA, 2023–26 | 720 | −1.72 | −3.22 | −2.78 | 0.997 | 1.00 | whole sample post | 25% | 0.00 | [−2.9, −0.6] | NOT VALIDATED (**opposite sign**) |
| P8y | First hour → last 30 min, 2023–26 | 720 | −0.38 | −1.88 | −0.50 | 0.69 | 1.00 | — | 50% | 0.00 | [−1.9, 1.2] | NOT VALIDATED |
| P9y | P7y, strong signals only (Rosa threshold) | 332 | −3.49 | −4.99 | −2.94 | 0.998 | 1.00 | — | 0% | 0.00 | [−5.5, −1.6] | NOT VALIDATED (**opposite sign**) |
| P13y | Next-day reversal of last 30 min | 719 | 2.25 | 0.75 | 0.71 | 0.24 | 1.00 | — | 75% | 0.07 | [−4.2, 8.5] | NOT VALIDATED |
| P15y | FX: long USD 08:00→16:00 London, short USD 16:00 London→17:00 NY, 9 pairs, 2023–26 | 727 | −0.69 (net) | −0.69 | −0.52 | 0.70 | 1.00 | — | 25% | 0.00 | [−3.3, 2.0] | NOT VALIDATED |

**Secondary results that matter:**

- **P4 per index:** the 1-day reversal is significant on ^GSPC (+4.5 bps/day net, t = 3.2), ^NDX (t = 2.4) and ^DJI (t = 2.0), but negative on ^HSI (t = −2.2) and ^GSPTSE (t = −2.5). **US-specific.**
- **P2 per index:** IBS < 0.2 is significantly *negative* on FTSE (t = −3.3), TSX (t = −5.1), SMI (t = −3.1), DAX and CAC (t ≈ −2). This confirms Pagonidis: the IBS effect is a US phenomenon.
- **P1 randomization p = 0.0096:** IBS < 0.2 days beat random up-trend days, but not a zero-excess benchmark (HAC p = 0.13). The pre-registered primary is the HAC test, so the verdict stands.
- **P15 by window: WITHDRAWN (see §8.3).** Round 1 reported NY close → Tokyo +1.78 bps (t = 3.9) and London fix → NY close −2.03 (t = −3.1) as replicating Krohn, Mueller & Whelan. Split by pair, the effect comes almost entirely from USD-base pairs (NOK t = 10.9, SEK 6.5, CHF 4.4, CAD 4.2), while EUR, AUD, NZD and JPY are ≈ 0. That is the signature of a bid-quote artifact at the NY 17:00 rollover, the boundary of both windows.
- **P6 by period:** 2007–12 +87 bps/month (t = 1.5), 2013–19 +60 (t = 1.2), 2020 → +94 (t = 2.0).

## 4. Round 1 — exploratory scan (new edges), amendment A1

20 simple signals on the S&P 500 (and SPY for open-based signals). Discovery 1990–2012 with BH
q < 0.10; the confirmation period 2013 → was examined only after discovery results were saved.

| Candidate | Discovery 1990–2012 | Confirmation 2013 → (S&P 500) | Nasdaq 100 2013 → | Result |
|---|---|---|---|---|
| **E06** ≥ 3 down closes → next day | +18.7 bps, t = 3.48, q = 0.010 | **+21.9 bps, t = 3.01, p = 0.001** | +24.8, t = 2.48 | **CONFIRMED** |
| E07 ≥ 3 up closes → next day | −8.1, t = −2.52, q = 0.077 | −4.4, p = 0.086 | −3.7 | not confirmed |
| E10 first trading day of month | +20.3, t = 2.61, q = 0.077 | +6.9, p = 0.17 | +10.2 | not confirmed |
| E16 after a ≥ 2% down day | +28.8, t = 2.42, q = 0.077 | +30.9, p = 0.097 | +24.9 | not confirmed (borderline) |
| 16 others (weekdays, OPEX, Halloween, gaps, streaks…) | q ≥ 0.16 | — | — | not discovered |

A real screen should reject most discoveries, and 3 of 4 failed confirmation.

### E06 robustness (post-confirmation; reported, does not change the verdict)

| Check | Result |
|---|---|
| Mechanism (index products, post-1990) | S&P 500 **before 1990: −11.0 bps (t = −2.7)**, 1990–2012 +18.7 (t = 3.5), 2013 → +21.9 (t = 3.0), **2020 → +35.8 (t = 3.6)** |
| Dose-response (number of down days k), 1990 → | k = 2: +8.6 (t = 2.9) · **k = 3: +19.8 (t = 4.6)** · k = 4: +31.5 (t = 3.6) · k = 5: +56.0 (t = 3.7) |
| Holding period (excess, 1990 →) | 1 day +19.8 (t = 4.6) · 2 days +31.1 (t = 4.8) · 3 days +38.7 · 5 days +52.9 (t = 4.7) |
| Regime | Above SMA200 +12.1 (t = 3.1); below SMA200 +32.9 (t = 3.1) |
| Random-entry benchmark | p = 0.0002 (5,000 random draws of the same number of days) |
| Bootstrap 95% CI (1990 →) | [+12.5, +27.8] bps |
| Deflated Sharpe (N = 39 trials) | 0.95 |
| Years positive | 31 of 37 |
| Other markets | SPY +22.5 (t = 4.7), ^DJI +10.6 (t = 2.5), ^AXJO +10.9 (t = 2.5), ^N225 +11.1 (t = 2.1); ^RUT only after 2013 (+16.3, t = 2.0); DAX, FTSE (post-2013), TSX, SMI, HSI: no |

## 5. Round 1 — leads (status after rounds 2–3)

1. **Last-30-minute reversal in the 0DTE era.** Tested in round 2 (Q7-P7): **no flip.** 2014–21 +0.43 bps, 2022–25 −0.30; difference p = 0.50. The 2023–26 Yahoo reversal is real in the data (HistData agrees on the overlapping days: correlation 0.98), but it is a 2024–25 pattern (2022 was +2.3 bps), not a regime break.
2. **Month-start continuation after equity outperformance** (P16 opposite sign): not retested; still a lead.
3. **FX W1 + W4:** tested in round 2 (Q6). It passed the rules, but the result is a measurement artifact (§8.3). **Withdrawn.**

## 6. Round 1 — can the survivors be traded? ([implementability.py](implementability.py))

Costs: US500 CFD spread 0.75 bps round trip; overnight financing = 13-week T-bill rate (^IRX) × nights / 360; CFD swap = T-bill + 2.5%/yr.

| Edge (1994 →) | Trades/yr | Gross bps | Net, futures/cash | Net, CFD | Ann. return at 1× (CFD) | Sharpe 1× | Max DD 1× |
|---|---|---|---|---|---|---|---|
| E06 | 22.1 | 24.7 (t = 5.1) | 22.2 (t = 4.6) | **21.9 (t = 4.5)** | 4.8% | 0.66 | −18.9% |
| P18 pre-holiday | 9.1 | 10.5 (t = 2.2) | 8.3 (t = 1.7) | 8.3 (t = 1.7) | 0.8% | 0.27 | −8.5% |
| P17 overnight | 252 | 3.3 (t = 4.8) | **0.8 (t = 1.2)** | **0.5 (t = 0.8)** | 1.3% | 0.12 | −56% |

Round-1 prop simulation (Yahoo daily, 2013 → , E06 + P18, execution at the official close):
58–67% pass at 2–8× and 108–425 days to pass. **§11 replaces this with a more realistic estimate (37–44%).**

---

## 7. Round 2 — tests Q1–Q7 (amendments A3–A5)

### 7.1 Data check (A5): HistData time stamps

HistData documents its time stamps as "EST without daylight saving". **They are New York local time
with DST.** The US 08:30 data release, the 09:30 cash open, the 03:00 (09:00 Berlin) Xetra open and the
04:30 (09:30 London) UK release all sit at the same NY clock minute in winter and summer, for every
symbol and year checked (2004–2025). Taking the documentation at face value would have shifted every
summer window by an hour. Bars are labelled by their start minute.

### 7.2 Results

Holm within family Q (14 tests) and pooled across rounds 1 + 2 (29 tests). DSR with N = 50.

| ID | Test | n | Mean bps | Net bps | t | p | Holm Q | Holm pooled | Later period mean (p) | Years | DSR | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | Announcement days (FOMC + employment), S&P 1994 → | 629 | 13.97 | 12.47 | 2.64 | 0.004 | 0.042 | 0.091 | 2013 → : 5.22 (0.18) | 64% | 0.75 | PARTIAL |
| Q2 | **MR-06, buy next open, sell that close**, SPY 1993 → | 735 | 11.41 | 9.91 | 2.61 | 0.005 | 0.042 | 0.091 | 2013 → : 9.73 (0.062) | 65% | 0.45 | **VALIDATED** (Q) / PARTIAL (pooled) |
| Q2b | MR-06, next open → close a day later | 735 | 18.04 | 16.54 | 2.67 | 0.004 | 0.041 | 0.086 | 13.17 (0.11) | 74% | 0.60 | PARTIAL |
| Q3 | MR-06 with a 15:30 signal, US ETFs 2023–26 | 127 | 12.10 | 10.60 | 0.96 | 0.17 | 0.85 | 1.00 | — | 67% | 0.08 | NOT VALIDATED (n = 127) |
| Q5 | Crypto weekly TSMOM, BTC + ETH | 624 wk | 61.4 | 61.4 | 1.62 | 0.053 | 0.32 | 0.90 | 2021 → : 68.2 (0.058) | 69% | 0.26 | NOT VALIDATED |
| Q6 | FX W1 + W4, 9 USD pairs 2004 – 2023-09 | 4,887 | 3.53 | 1.53 | 9.33 | < 0.0001 | < 0.0001 | < 0.0001 | 2019 → : 2.22 (0.0001) | 95% | 1.00 | VALIDATED by rule — **INVALID: artifact (§8.3)** |
| Q7-P7 | Rest-of-day → last 30 min, US500 2014–25 | 2,768 | 0.20 | −1.30 | 0.43 | 0.34 | 1.00 | 1.00 | 2022 → : −0.30 (0.63) | 58% | 0.03 | NOT VALIDATED |
| Q7-P8 | First 30 min → last 30 min, US500 | 2,763 | −1.23 | −2.73 | −2.55 | 0.995 | 1.00 | 1.00 | −0.81 (0.80) | 25% | 0.00 | NOT VALIDATED (**opposite sign**) |
| Q7-P9 | P7 with Rosa threshold | 738 | −0.36 | −1.86 | −0.29 | 0.61 | 1.00 | 1.00 | −0.09 (0.52) | 42% | 0.01 | NOT VALIDATED |
| Q7-P10 | First-candle ORB (Zarattini & Aziz), US100 + US500 | 2,811 | 2.57 | 1.07 | 3.16 | 0.0008 | 0.010 | 0.019 | 2023 → : 0.82 (0.29) | 92% | 0.77 | PARTIAL |
| Q7-P11 | 30-min ORB stop entry, US100 + US500 | 2,808 | 2.47 | 0.97 | 2.39 | 0.009 | 0.062 | 0.15 | 2023 → : 3.81 (0.034) | 75% | 0.46 | PARTIAL |
| Q7-P12 | **GER40 17:00 → 17:30 momentum** | 2,962 | 2.07 | 0.57 | 4.85 | < 0.0001 | < 0.0001 | < 0.0001 | 2022 → : 1.32 (0.024) | 83% | 1.00 | **VALIDATED** — then failed confirmation (§9) |
| Q7-P13 | Next-day reversal of last 30 min, US500 | 2,735 | 1.35 | −0.15 | 0.65 | 0.26 | 1.00 | 1.00 | 5.32 (0.11) | 50% | 0.05 | NOT VALIDATED |
| Q7-P14 | US500 02:00 → 03:00 drift (**control**) | 3,065 | 0.66 | — | 2.42 | 0.008 | 0.062 | 0.15 | 2014–20: 1.45 (t = 3.75) → 2021 → : −0.43 (t = −1.2) | 58% | — | **DECAY CONFIRMED** |
| Q4 | MR-06 rule on bonds, gold, oil, FX ETFs, crypto (**mechanism check, two-sided**) | 2,619 | 0.45 | — | 0.15 | 0.88 (2-sided) | — | — | — | — | — | Prediction held (≈ 0 pooled); but TLT (t = 3.4), IEF (2.6), UUP (2.3) show reversal individually |

### 7.3 Round-2 secondaries and diagnostics

- **Q1 by event:** FOMC days +19.0 bps (t = 2.3) overall but **+0.9 bps after 2013** (t = 0.1); employment days +9.7 (t = 1.4), +8.3 after 2013. The pre-FOMC/FOMC-day premium looks arbitraged away, as the decay-control card expected.
- **Q2 vs E06:** buying at the next open keeps about half of the close-to-close effect (11.4 vs ~20 bps). Most of the E06 reversal happens overnight.
- **Q5:** buy-and-hold made 124 bps/week against 61 for weekly TSMOM. Crypto TSMOM mostly harvests the drift.
- **Q7-P10 sized as the paper sizes it** (risk = distance to the first-candle stop; post hoc): the median stop is 12 bps (US500) and 20 bps (US100), so a 1.5 bps cost is 0.08–0.12R per trade. Gross +0.14R (t = 2.8) and +0.16R (t = 3.4) become **−0.02R and +0.05R net (t = −0.4, 1.2)**; 2023 → : −0.05R and +0.01R. The paper's headline returns rely on zero costs.
- **Q7-P12 perturbations** (post hoc): signal to 16:58, entry 17:02, exit 17:29 or 17:35: t = 3.9–4.8. Long leg +2.4 (t = 4.4), short leg +1.7 (t = 2.4). Unconditional 17:00–17:30 drift +0.5 (t = 1.2). Top tercile of |signal| +4.5 (t = 5.2). Year by year: 2014 3.4, 2015 3.8, 2016 3.1, 2017 0.4, 2018 4.2, 2019 −0.4, 2020 4.1, 2021 0.8, 2022 2.4, 2023 −0.1, 2024 0.4, 2025 2.2.
- **Cross-source check for P7:** on the 494 overlapping days (2023-10 → 2025-12), SPY on Yahoo and SPXUSD on HistData give −2.02 and −1.94 bps/day (P&L correlation 0.98). The two sources agree.

---

## 8. Round 2 — appraisal of the FX result (Q6)

### 8.1 What the pre-registered test said

W1 + W4 on 9 pairs, 2004–2023: +3.53 bps/day gross, t = 9.3, 95% of years positive, post-2019 +2.2
(t = 3.8). Under the verdict rules this is VALIDATED, and it would have been the strongest result in the audit.

### 8.2 Why it can't be trusted

Per pair: USDNOK +11.0 bps/day, USDSEK +8.1, USDCHF +5.0, USDCAD +4.1 (all t > 9), but
**EURUSD −2.3, GBPUSD −2.7, AUDUSD −3.2, NZDUSD −6.7 after 2019** (t ≈ −3 to −8). A genuine dollar
move can't favour every USD-base pair and hurt every USD-quote pair. A **bid-only quote whose spread
widens at the NY 17:00 rollover** does exactly that: both windows start or end at 17:00, and a
depressed bid flatters USDxxx trades and penalizes xxxUSD trades.

Direct check (mean bid at t minus bid at 16:30, Mon–Thu, 2019–23): EURUSD −0.7 bps at 17:00;
USDCHF −2.5; USDNOK −5.3 at 17:00 and −9.2 at 17:10; USDSEK −4.0 and −8.7. The dip is the same sign
for USD-base and USD-quote pairs and lasts until about 18:30. That is spread, not price.

### 8.3 Clean re-measurement (post hoc; boundaries where spreads are normal)

USD-signed return, bps/day, basket of 9 pairs (t):

| Segment | 2004–2018 | 2019–2023 |
|---|---|---|
| London 16:00 → NY 16:45 (clean W4; predicted USD down) | **−1.62 (−4.2)** | −0.25 (−0.5) |
| NY 18:30 → 01:00 UTC (clean W1; predicted USD up) | **+1.19 (+6.6)** | **+1.37 (+4.7)** |
| Both, flat through the rollover | +2.80 (+6.5) | +1.79 (+3.1), **net of 2 bps: −0.2** |

The dollar-fix pattern of Krohn et al. was real in 2004–18 in clean data. After 2019 the
post-London-fix leg is gone, and the Tokyo leg is about 1 bp/day, below realistic retail costs. The
round-3 test (R6) found the Tokyo leg absent in 2024–25 as well.

**Lesson for the SQX build:** backtests on bid-only FX data are biased at the rollover. Use bid/ask
data (or mid plus modeled spread), and never place a window boundary at 17:00 NY.

---

## 9. Round 3 — confirmation on unseen data (amendments A6, A7)

Each round-2 lead tested on data not downloaded or inspected before A6/A7 were committed. Family R, Holm
within R. Verdict: REPLICATED = predicted sign, Holm p < 0.05 and net > 0; WEAK = raw p < 0.05 only.

| ID | Lead | Unseen data | n | Mean bps | Net bps | t | p | Holm R | Power* | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | P12 on other European closes (CAC 40, Euro Stoxx 50, FTSE 100) | 2014–25 (Euro Stoxx 2014–19 only†) | 3,006 | 1.01 | −0.49 | 2.99 | 0.001 | 0.010 | — | **WEAK** (below costs) |
| R2 | **P12 on earlier years** (GER40) | 2010-11 → 2013 | 783 | −0.24 | −1.74 | −0.24 | 0.59 | 0.70 | 0.80 | **NOT REPLICATED** |
| R3 | 30-min ORB on earlier years (US500 + US100) | 2010-11 → 2013 | 771 | 1.65 | 0.15 | 0.84 | 0.20 | 0.70 | 0.35 | NOT REPLICATED (underpowered) |
| R4 | First-candle ORB on earlier years | 2010-11 → 2013 | 765 | 1.69 | 0.19 | 1.21 | 0.11 | 0.56 | 0.50 | NOT REPLICATED (underpowered) |
| R5 | MR-06 open entry (Q2) on DIA + IWM | 2013 → 2026-09 | 476 | 4.48 | 2.98 | 0.94 | 0.17 | 0.70 | 0.64 | NOT REPLICATED |
| R6 | Clean USD-into-Tokyo, EUR/GBP/AUD/NZD | 2024–25 | 521 | 0.21 | −0.79 | 0.44 | 0.33 | 0.70 | — | NOT REPLICATED |
| R7 | **MR-06 with a 15:55 entry** (US500 + US100) | 2014–25 minute data (rule not computed on it before) | 308 | **15.88** | **14.38** | 1.89 | **0.030** | 0.18 | 0.93 | **WEAK** (magnitude replicates; Holm fails) |

\* Power: probability of p < 0.05 (one-sided) if the true effect equals the round-2 estimate.
† HistData stopped serving Euro Stoxx 50 after 2019. GER40 starts 2010-11; US500/US100 start 2010-11.

**Secondaries:**

- R1 per index: CAC +1.09 (t = 2.7), FTSE +1.02 (t = 3.0), Euro Stoxx +0.66 (t = 0.9). The top-tercile rule (post hoc) gives +2.1 to +2.9 bps. Close-momentum exists in European index quotes in 2014–25, at about half the DAX size and below cost.
- R2: the 2010–13 result is 2.7 standard errors below what the 2014–25 GER40 effect predicts. The top-tercile rule is also negative there (−0.8 bps). **The GER40 effect is not stable across periods.**
- R6 USD-base pairs: +1.43 bps (t = 3.6), driven by NOK (+3.8, t = 7.2) and SEK (+3.2, t = 5.7). The 18:30 boundary is still inside the wide-spread period for those two pairs. More artifact, not edge.
- R7 per index: US500 +20.2 bps (t = 2.3), US100 +11.8 (t = 1.1). Signal agreement: 98% (US500) and 93% (US100) of 15:55 signals are true three-down-close days. **On the same data and years, the 15:55 entry and the exact close give the same result** (US500 +23.5 vs +21.2 bps raw; US100 +16.8 vs +20.3). Execution timing isn't the problem; the 2014–25 sample is simply shorter and noisier than 1990–2026 (US500 t ≈ 2.6, US100 t ≈ 1.5–1.9).

---

## 10. What survived, in one table

| Lead | Round 1 | Round 2 | Round 3 | Final |
|---|---|---|---|---|
| MR-06 (≥ 3 down closes, US) | Confirmed OOS (t = 3.0) | Open entry: validated within Q (t = 2.6) | 15:55 entry: +15.9 bps, p = 0.03; open entry on DIA/IWM: n.s. | **Keep. Enter near the close, not the next open** |
| GER40 close momentum | — | Validated (t = 4.9) | Failed on 2010–13; below costs elsewhere | **Drop** |
| ORB (5-min, 30-min) | — | Partial (t = 2.4–3.2) | n.s. on 2010–13 (underpowered) | **Drop as standalone**; ≤ 1 bp net |
| FX fix windows | "Replicated" | Artifact | Clean Tokyo leg gone 2024–25 | **Drop** |
| Announcement premium | — | Partial; decayed after 2013 | — | **Drop** |
| Last-30-min reversal | Lead | No flip | — | **Drop** |

---

## 11. Prop-challenge implications ([prop_mr06_minute.py](prop_mr06_minute.py))

MR-06 with the realistic 15:55 entry, HistData 2014–25, raw returns net of 1.5 bps and CFD swap,
intraday path from entry to exit, two-step 10%/5% (5% daily, 10% static), 3% EA daily guard,
stationary bootstrap:

| Book | Trades/yr | Net bps/trade (t) | 2× | 4× | 6× | 8× |
|---|---|---|---|---|---|---|
| US500 + US100 (capital split) | 26 | 16.8 (2.0) | 41% · 360 d | 41% · 169 d | 37% · 122 d | 37% · 99 d |
| US500 only | 19 | 19.7 (2.3) | 44% · 556 d | 37% · 271 d | 35% · 186 d | 33% · 149 d |

(pass probability · median days to pass; zero-edge base rate = 33%)

**Why the pass rate is low despite a real edge.** Per trade at 1×, MR-06 has σ = 153 bps against a
+20 bps mean, and an average adverse excursion of −89 bps: it buys into falling markets. US500 at 2×:

| Assumption | Pass | Main failure |
|---|---|---|
| No EA guard, real intraday path | **17%** | 82% breach the 5% daily loss |
| 3% EA guard, real intraday path | 44% | 56% hit the 10% max loss |
| 3% guard, exits only at the close (unrealistic) | 89% | — |

The daily-loss rule, not the edge, decides the outcome. That's why the round-1 estimate (58–67%,
daily bars, official-close execution) was optimistic. **Conclusions:** use an EA guard, keep leverage
at ≤ 2×, expect 12–18 months per pass, and don't rely on MR-06 alone.

---

## 12. Appraisal: how much to trust this

| Issue | Effect on conclusions | Severity |
|---|---|---|
| **Data are CFD-style quotes, not exchange prints** (HistData bid quotes; Yahoo indices) | Artifacts at spread-widening times are real (§8). Index results at 15:30–16:00 and 17:00–17:30 Berlin are at liquid hours, and the cross-source check agreed (correlation 0.98) | High for FX; low–medium for indices |
| **Power of the confirmation tests** | R3/R4 (ORB, 35–50% power) can't rule out a smaller real effect. R2 (80%) and R7 (93%) are informative | Medium |
| Multiple testing | 57 hypotheses. MR-06 survives BH in discovery, independent confirmation, DSR 0.95 (N = 39, daily data) and R7 at p = 0.03. R7's DSR at N = 57 is only 0.29: **the 2014–25 minute sample alone wouldn't justify it** | Medium |
| Post-hoc analysis | The FX clean windows, the P10 R-multiples, the P12 perturbations and the prop diagnostics are post hoc and labelled so. They were used to *downgrade* claims, never to promote one | Low |
| Researcher degrees of freedom | Round 3 was chosen after seeing round 2. That's why it used only unseen data | Low |
| Costs are assumptions | ORB, GER40 and FX results flip sign within ±1 bp of cost, so no realistic cost model rescues them. MR-06 (~20 bps) is robust to costs | Low for MR-06 |
| Regime dependence | MR-06 is strongest 2020 → and absent before 1990. The mechanism (index products, dealer liquidity provision) can change | Medium: monitor yearly |
| No holdout left | Every series here is now in-sample for an SQX build | **Paper-trade or use post-Sep-2026 data first** |

**Overall confidence:**

- **High:** MR-06 is a real, US-specific, post-1990 effect of about 20 bps per trade, whether you enter at the close or at 15:55.
- **High:** GER40 close momentum, the ORBs, FX fix windows, the announcement premium, overnight drift and turn of month are **not** tradeable edges at retail costs today.
- **Moderate:** the prop pass-rate estimates. They depend on the challenge rules, the guard, leverage and the bootstrap.

## 13. What changes in the plan

- **MR-06 stays the only build candidate.** Pre-register the 15:55 entry (close-proxy) version with the next-close exit on US500 (primary) and US100. Don't use the next-open entry: it loses half the effect.
- **For prop challenges,** MR-06 is a slow building block (≈ 40% pass, 12–18 months at 2×). Combine it with pre-holiday (small), run at ≤ 2× with an EA guard, and treat any additional edge as unproven until it passes a pre-registered test on fresh data.
- **Drop from the build list:** GER40 close momentum, both ORB variants as standalone strategies, FX fix windows, announcement days, last-30-minute momentum/reversal, overnight premium, turn of month, IBS-only, non-US mean reversion.
- **Data rule for the coding agent:** FX tests need bid/ask (or mid) data, and no window may start or end within 17:00–18:30 NY on bid-only data.
- **Open leads (not evidence):** reversal in Treasury ETFs after three down days (Q4: TLT t = 3.4, IEF 2.6); month-start continuation after equity outperformance (P16).

## Reproduce

```bash
cd research/validation
export YAHOO_CACHE=/path/to/cache HISTDATA_CACHE=/path/to/cache
python3 run_daily.py            # P1–P6, P16–P19        -> results/daily.json
python3 run_exploratory.py      # A1 scan               -> results/exploratory_*.json
python3 robust_e06.py           # E06 robustness        -> results/e06_robustness.json
python3 run_intraday_yahoo.py   # A2 intraday           -> results/intraday_yahoo.json (Yahoo keeps ~730 days of 60-min bars)
python3 verdicts.py             # round-1 verdicts      -> results/verdicts.json
python3 implementability.py     # round-1 costs, prop   -> results/implementability.json
python3 run_round2.py           # Q1–Q5                 -> results/round2.json
python3 run_histdata.py         # Q6, Q7 (HistData)     -> results/histdata.json
python3 verdicts_round2.py      # round-2 verdicts      -> results/verdicts_round2.json
python3 run_round3.py           # R1–R7                 -> results/round3.json
python3 prop_mr06_minute.py     # prop, realistic entry -> results/prop_mr06_minute.json
python3 diagnostics_post_hoc.py # post-hoc checks       -> results/diagnostics_post_hoc.json
python3 -m unittest discover -s tests
```

HistData files are fetched year by year by `data_histdata.fetch_year` (free, no key). The post-hoc
diagnostics in §7.3, §8 and §9 come from [diagnostics_post_hoc.py](diagnostics_post_hoc.py)
(`results/diagnostics_post_hoc.json`).
