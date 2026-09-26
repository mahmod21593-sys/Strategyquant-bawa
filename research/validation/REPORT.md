# Own-data validation report

**What this is:** every edge in the plan tested on real market data, with the tests fixed *before*
looking at results ([PREREGISTRATION.md](PREREGISTRATION.md)). There were five rounds, each
pre-registered and committed before its data was tested:

| Round | Pre-registered | Data | Tests |
|---|---|---|---|
| 1 | Main table + A1, A2 (09:10–09:19 UTC, 2026-09-25) | Yahoo daily (13 indices, 25 ETFs); Yahoo 60-min (2023–26) | P1–P19, exploratory scan E01–E20 |
| 2 | A3, A4, A5 (13:33–13:46 UTC) | HistData.com 1-minute: US500, US100, GER40 2014–25; 9 USD pairs 2004–23 | Q1–Q7 (Q7 = the original minute-data tests P7–P14) |
| 3 | A6, A7 (14:00–14:03 UTC) | **Data not yet downloaded or inspected**: earlier years, other instruments, a later period | R1–R7 confirmation tests of the round-2 leads |
| 4 | A8 (17:07 UTC) | Yahoo daily (^GSPC, SPY, IEF, TLT, 10 equity indices), TreasuryDirect auctions, FRED 10-year yields 1962–2001, HistData FX | S1–S7: published edges tested **after their papers' samples**, plus the untested FX-02 and CF-02 |
| 5 | A9–A11 (21:18 UTC →) | HistData gold, silver, WTI, Brent, Nikkei, ASX 200, Hang Seng, FX crosses; Binance BTC/ETH; Yahoo world indices | **No Treasury strategies (user scope).** 8 literature tests (T), a 653-candidate scan over 24 instruments (X), MR-06 on 15 untested indices (W1), noise-area momentum (N) |

The git commit timestamps are the evidence of ordering. Every deviation is logged as an amendment.

---

## 1. Bottom line (after five rounds; no Treasury strategies)

| Edge | Status | Best evidence | After costs | Prop use |
|---|---|---|---|---|
| **MR-06: next day after ≥ 3 down closes, US500 (and US100)** | **Confirmed** (rounds 1–3); realistic 15:55 entry checked | Daily 1990 → : +19.8 bps, t = 4.6; 2014–25 minute data: +20 to +24 bps, t ≈ 2.3–2.7 | +14 to +22 bps/trade; ~19 trades/yr | **Volatility-scaled 2×: 60% pass (two-step), ~21 months**; base rate 15–33% |
| **IM-04 noise-area intraday momentum, US100 (new, round 5)** | **Confirmed within its family** (N3: Holm p = 0.028), **not** on US500 (the paper's own instrument), GER40 or gold | +3.0 bps/day net, t = 2.54, Sharpe 0.73; same size on unseen 2011–13 (+2.9); stable across lookbacks | Survives 3 bps cost (+2.1) | **Fast:** 40% pass at 2× in ~6 months; the TWAP-stop variant (post hoc) 52% at 3× in ~4.5 months; base rate ≈ 11% |
| MR-06 on JP225 and AUS200 (execution check) | Positive with a pre-close entry: JP225 +20.5 bps (t = 2.3), AUS200 +13.8 (t = 2.3) | Concentrated in volatile episodes (JP225 after 2024) | — | Adds speed, not pass probability |
| Pre-holiday | Validated (round 1), small | +12.0 bps, t = 3.2 | +8.3 bps | Add-on (~9 days/yr) |
| Treasury end-of-month (CF-07) | Confirmed out of sample (round 4) | IEF +19.8 bps/month after 2019 | — | **Excluded by the user (no Treasury strategies)**; evidence kept on file |
| Everything else | Failed on unseen data, decayed after publication, below costs, or a data artifact | See §3–§15 | — | No |

**The honest summary:**

- **What was tested.** About 730 pre-registered hypotheses on up to 64 years of data, 24 prop-tradeable instruments and 1-minute data.
- **What survived.** Two edges outside Treasuries: **MR-06** (buy US index weakness at the close) and **noise-area momentum on US100**. The first is solidly established. The second passed its own test and every robustness check, but is not significant after deflating for everything tried (DSR 0.22). Treat it as a strong candidate that must prove itself in paper trading.
- **What failed.** Every published intraday, time-of-day, crypto, commodity-momentum, FX-flow and calendar edge tested in round 5 failed after its paper's sample or after costs.
- **What it means for prop challenges.** How you size decides more than which edge you pick (§16). Maximising money per month means fast, repeated attempts at 3–4× (US100 momentum ≈ $780 per account-month on a two-step account; MR-06 ≈ $210). Maximising the chance of passing means cushion (CPPI) sizing: MR-06 79%, US100 78%, against 15–19% for zero edge, but slowly. Base rates are 11–33% depending on rules and leverage.

---

## 2. How the tests were run

- Pre-registered: rule, prediction, sample splits, costs, statistics and verdict rules, before the data was examined. Amendments were committed before the tests they affect.
- Per test: Newey-West HAC t (lag ≥ 5), one-sided p in the predicted direction, stationary-bootstrap 95% CI (2,000 resamples), year-by-year sign share, pre- vs post-publication split, net of pre-registered cost.
- **Multiple testing:** Holm and Benjamini-Hochberg within each round's family, and pooled for rounds 1 + 2 (29 tests). Deflated Sharpe ratio with the cumulative trial count (N = 35 in round 1, 50 in round 2, 57 in round 3, 64 in round 4).
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
| Treasury end-of-month (round 4) | — | — | S2: +19.8 bps/month 2019 → (t = 2.95) | Confirmed, but **excluded by the user** (no Treasury strategies) |
| FOMC cycle, auction cycle, FX month-end fix, bond reversal (round 4) | — | — | Decayed or n.s. out of sample | **Drop** |
| Rebalancing, paper timing (round 4) | P16 wrong timing, opposite sign | — | S6: +7.2 bps (t = 2.1), n.s. after 2023 | Lead only |
| **Noise-area momentum, US100 (round 5)** | — | — | N3: +3.0 bps/day (t = 2.54, Holm p = 0.028); US500/GER40/gold fail | **Keep as candidate** (DSR over all trials 0.22) |
| Commodity/crypto/oil intraday rules; 653-candidate scan; MR-06 on world indices (round 5) | — | — | 0 confirmed | **Drop** |

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
at ≤ 2×, and don't rely on MR-06 alone. **Round 4 improves on this:** volatility-scaled sizing lifts
MR-06 to 60%, and adding the Treasury end-of-month edge lifts the book to 73–83% (§13).

---

## 12. Round 4 — published edges tested after their papers' samples (amendment A8)

Specs read from the primary papers (V1) before A8 was committed. Family S (7 tests), Holm within S,
DSR N = 64. The primary sample of each test lies **after** the paper's own sample.

| ID | Edge (source) | Primary sample | n | Mean bps | Net bps | t | p | Holm S | In the paper's own period | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | FOMC cycle: even-minus-odd weeks (Cieslak, Morse & Vissing-Jorgensen 2019) | 2017-01 → 2026-09 | 2,420 days | **−4.77**/day | — | −1.08 | 0.86 | 1.00 | 1994–2016: **+11.98, t = 3.89** (paper: 12 bps); 2004–16: +11.0 (t = 2.65) | NOT CONFIRMED (**decayed after publication**) |
| S2 | **Treasury end-of-month**: IEF, last 3 trading days, excess over T-bill (Hartley & Schwarz 2019) | 2019-01 → 2026-08 | 92 months | **+19.82** | **+17.82** | **2.95** | 0.0016 | **0.011** | 2002–18: **+20.97, t = 4.59** (paper: ≈ 25 bps on the 10-yr note) | **CONFIRMED** |
| S3 | Treasury auction cycle: IEF short 5 days before, long 5 days after 10-yr auctions (Lou, Yan & Zhang 2013) | 2013-09 → 2026-09 | 159 | +8.11 | +4.11 | 0.90 | 0.18 | 0.92 | 2002–08: +11.75 (t = 0.91) | NOT CONFIRMED |
| S4 | Month-end fix hedging: −sign(relative equity MTD) over 15:00–16:00 London (Melvin & Prins 2015) | 2013-01 → 2025-12 | 155 | +0.84 | −0.16 | 0.60 | 0.28 | 0.92 | 2004–12: +2.05 (t = 1.27) | NOT CONFIRMED |
| S5 | Post-fix reversal, 16:00 → next-day noon (Melvin & Prins 2015) | 2013-01 → 2025-12 | 143 | +1.65 | +0.65 | 0.76 | 0.22 | 0.92 | 2004–12: +5.83 (t = 1.90) | NOT CONFIRMED |
| S6 | Rebalancing, Calendar signal, last 5 days (Harvey, Mazzoleni & Melone 2025) | 2002-08 → 2026-09 | 1,445 days | +7.15 | +6.15 | 2.06 | 0.020 | 0.12 | to 2023-03: +7.88 (t = 2.00); after: +2.87 (t = 0.47, n = 210) | WEAK |
| S7 | Bond reversal after 3 down days (round-2 lead) | 1962–2001 (FRED 10-yr) | 1,065 | **−2.57** | −3.07 | −1.97 | 0.98 | 1.00 | (TLT 2002 → : +11.4, t = 3.4, the data that suggested it) | NOT CONFIRMED (**opposite sign**: the lead was period-specific) |

**Secondaries:**

- **S1:** even weeks averaged +2.5 bps/day and odd weeks +7.2 after 2017, against +9.8 and −2.2 in 1994–2016. The implementation reproduces the paper, so the effect itself has gone. A long-only even-week strategy earned 0.85 bps/day net after 2017, against 5.0 for buy-and-hold. Uppal's claim (V3) that it faded "as early as 2004" is **not** supported here (2004–16: t = 2.65). Its disappearance dates from publication.
- **S2:** rest-of-month IEF excess return after 2019 was −33 bps/month (t = −1.7). The whole term premium sits at month-end, as the paper says. TLT: +24.1 after 2019 (t = 1.77); +39.3 in 2002–18 (t = 4.61).
- **S3:** the 5-year-auction version gave +12.4 (t = 1.10). Excluding the 45 events whose windows touch a month-end: +12.3 (t = 1.29). Positive, but not significant in any version, including the paper's own period.
- **S4 per pair (2013 →):** AUD +4.7 (t = 2.1) and CHF +4.4 (t = 2.2) positive; NOK −4.4, CAD −1.7. No consistent pattern: this is the 2015 reform era (Ito & Yamada 2017, NBER w23327, find the fix anomalies changed shape after it).
- **S6, SPY only** (for accounts without bonds): +6.99 bps (t = 2.41) on 2002–2026, +2.97 after 2023 (t = 0.55). This corrects round 1's P16, which traded the first day of the next month, after the rebalancing is done. That explains its opposite sign.

## 13. Round 4 follow-up — robustness and prop books (post hoc, [round4_followup.py](round4_followup.py))

> The Treasury books below were superseded in round 5 by the user's scope (no Treasury strategies). See §15 for the current books.

Not pre-registered, except I1 (volatility-scaled MR-06), whose design was fixed in A8. These checks
were run after S2 was confirmed. They describe the edge; they don't add evidence to the verdict.

### 13.1 Treasury end-of-month: robustness

| Window (IEF) | 2002–2018 | 2019 → |
|---|---|---|
| Last day only | +11.4 (t = 4.2) | +7.5 (t = 2.0) |
| Last 2 days | +18.9 (t = 4.6) | +12.8 (t = 2.5) |
| **Last 3 days (tested)** | **+21.0 (t = 4.6)** | **+19.8 (t = 3.0)** |
| Last 4 days | +20.5 (t = 4.0) | +18.9 (t = 2.6) |
| Last 5 days | +23.0 (t = 4.0) | +24.0 (t = 2.8) |
| SHY (1–3 yr), last 3 | +5.6 (t = 5.1) | +5.5 (t = 3.7) |
| TLT (20+ yr), last 3 | +39.3 (t = 4.6) | +24.1 (t = 1.8) |

The effect doesn't depend on the exact window, scales with duration as an index-extension mechanism
predicts, and was positive in **24 of 25 calendar years** (2002–2026; only the partial 2026 is negative).

### 13.2 MR-06 with volatility-scaled size (I1, design fixed in A8)

Notional = min(2, 1% ÷ 20-day realized daily volatility), normalised to the same average notional as
fixed sizing. US500, 15:55 entry, 2014–25, two-step 10%/5% with a 3% guard:

| Sizing | Mean / sd per trade (bps) | 2× | 4× |
|---|---|---|---|
| Fixed | 19.7 / 152.8 | 44% · 556 days | 37% · 271 days |
| **Volatility-scaled** | 18.5 / 127.2 | **60% · 641 days** | **48% · 292 days** |

Scaling down after volatile weeks removes the trades most likely to breach the daily-loss limit, at
almost no cost in mean return.

### 13.3 Prop books, 2014–2025 (bootstrap; 1,500 runs each)

MR-06 = volatility-scaled US500 (§13.2). S2 = IEF excess return, standing in for a 10-yr Treasury
future (a 50K futures account trading 1–2 ZN contracts is roughly 2–4× notional). Weights are notional
multiples. Zero-edge base rates use the S2 book with its mean removed.

| Book | Two-step 10%/5% (3% guard) | Futures 50K: 6% target, 4% EOD trailing (2% guard) |
|---|---|---|
| **Zero edge (base rate)** | 27% (4×), 23% (8×) | 19% (4×), 16% (8×) |
| MR-06 2× | 60% · 641 days | 29% · 227 days |
| **S2 4×** | **86% · 494 days** | **50% · 134 days** |
| S2 8× | 68% · 208 days | 42% · 88 days |
| **MR-06 1× + S2 4×** | **83% · 373 days** | 48% · 95 days |
| MR-06 2× + S2 4× | 73% · 292 days | 37% · 86 days |
| MR-06 2× + S2 8× | 60% · 163 days | 36% · 58 days |

**Reading this:** S2 is the better prop component, with high consistency and 12 short trades a year.
Adding MR-06 roughly halves the time to pass for a small loss of pass probability. Trailing-drawdown
futures accounts are much harder (a 4% trailing limit against a 6% target), but S2 still gives 2.5×
the no-edge rate. All of these numbers are **in-sample for sizing**: the bootstrap re-uses the same
2014–25 history that was used to pick the weights.

## 14. Round 5 — prop-tradeable instruments only (amendments A9–A11)

The user asked for **no Treasury strategies**. Round 5 searched only instruments a CFD prop account
offers. It added HistData gold, silver, WTI (served only to 2023), Brent, Nikkei 225, ASX 200, Hang Seng,
EURJPY, GBPJPY and EURGBP, plus Binance BTC/ETH. Every new HistData symbol passed the time-zone check:
the Tokyo, Hong Kong and Sydney opens move one New York hour between seasons, and Brent settles at 14:28 NY.

### 14.1 Literature tests (family T), each on data after its paper's sample

| ID | Edge (source) | Primary sample | n | Mean bps | Net bps | t | p | Holm T | Paper's own period (my data) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 | Commodity intraday momentum: gold, silver, crude (Baltussen et al. 2021, *JFE*) | 2020-06 → 2025 | 1,388 | +0.42 | −3.38 | 0.86 | 0.19 | 1.00 | 2011 → 2020-05: **+2.34, t = 3.21** | NOT CONFIRMED (**decayed after publication**) |
| T2 | Crude oil: prior close → 10:00 predicts 15:30–16:00 (Wen et al. 2021) | 2019 → 2023 | 1,098 | −0.23 | −4.23 | −0.24 | 0.59 | 1.00 | 2011–18: +0.29 (t = 0.65) | NOT CONFIRMED |
| T3 | EIA Wednesdays: 10:30–11:00 predicts 15:30–16:00 (Wen et al. 2023) | 2019 → 2023 | 205 | −3.26 | −7.26 | −1.52 | 0.94 | 1.00 | 2011–18: +0.05 | NOT CONFIRMED |
| T4 | Bitcoin intraday momentum (Shen, Urquhart & Wang 2022) | 2021 → 2026-08 | 2,068 | −0.31 | −5.31 | −0.35 | 0.64 | 1.00 | 2017-09 → 2020: −0.37 | NOT CONFIRMED |
| T5 | Bitcoin long 22:00–24:00 UTC (Padyšák & Vojtko 2021) | 2022 → 2026-08 | 1,703 | +1.54 | −3.46 | 0.93 | 0.18 | 1.00 | 2017-09 → 2021: +3.44 (t = 1.06) | NOT CONFIRMED (the 2-hour share of BTC's drift is +0.55) |
| T6 | Bitcoin Monday effect (Caporale & Plastun 2019) | 2018 → 2026-08 | 3,160 days | +26.2 (Mon − other) | — | 1.38 | 0.084 | 0.59 | — | NOT CONFIRMED |
| T7 | Asian index intraday momentum, JP225 + AUS200 (Baltussen et al.) | 2020-06 → 2025 | 1,439 | +0.75 | −2.25 | 2.28 | 0.011 | 0.089 | 2011 → 2020-05: +0.29 | WEAK (below cost) |
| T8 | Crypto weekend → Monday US500, short after negative weekends (2025 *FRL*), **tradeable version** from the Sunday futures reopen | 2021 → 2025-06 (paper's period) | 77 | −8.2 | −9.7 | −0.50 | 0.69 | 1.00 | — | **NOT TRADEABLE**: whatever predictability exists is in the gap before futures reopen |

### 14.2 Systematic scan (family X): 24 instruments, 653 candidates

The scan covered hour-of-day, day-of-week, streaks, IBS and 20-day breakouts. Discovery ran on 2011–2017
(crypto 2018–21) and was **committed before the confirmation data was examined** (commit d3bf6be).
Confirmation ran on 2018–2025 (crypto 2022–26).

| | Count |
|---|---|
| Candidates | 653 |
| Discovered (BH q < 0.10) | 20: 16 hour-of-day effects, 1 day-of-week, 0 streak/IBS/breakout |
| **Confirmed** (Holm p < 0.05, same sign, net of cost > 0) | **0** |
| Significant but below cost (WEAK) | 1: **silver, 06:00–07:00 NY** (the hour before the 12:00 London silver fix): −5.1 bps in discovery, −2.4 in confirmation (Holm p = 0.006) against a 5-bps cost |

Every discovered effect shrank out of sample: gold's AM-fix hour, Brent on Mondays (−35 bps in
discovery), the ETH hours and the FX hours. The US500 02:00–03:00 drift was discovered again and failed
again (it is the Q7-P14 decay control). **Simple calendar and time-of-day rules on prop instruments don't
survive out of sample at retail costs.**

### 14.3 MR-06 on 15 untested world indices (W1, amendment A10)

Pooled 2000–2026: **+2.8 bps, t = 1.24**, NOT CONFIRMED. By index: FTSE MIB +20.3 (t = 2.8), IBEX +13.7
(t = 2.0), AEX +13.4 (t = 2.0) and Bovespa +10.3 were positive; Jakarta −11.9, Kuala Lumpur −5.9 and
Merval −7.9 were negative; the rest ≈ 0. Picking the winners now would be cherry-picking. MR-06 is a US
edge that also appears in Japan, Australia and possibly southern Europe, not a global law.

### 14.4 Noise-area intraday momentum (family N, amendment A11)

The rule is Zarattini, Aziz & Barbon's: a 14-day average move from the open at each half-hour mark; long
above the upper band, short below the lower band, flip at the opposite band, flat at the close.

| ID | Instrument / version | Net bps/day | t | Holm N | Sharpe | Paper's period (to 2024-04) | After (2024-05 → 2025) | Verdict |
|---|---|---|---|---|---|---|---|---|
| N1 | US500, conservative | +0.70 | 0.69 | 0.74 | 0.20 | +0.57 (paper reports Sharpe 0.61 on SPY) | +1.47 | NOT CONFIRMED |
| N2 | US500, TWAP trailing stop (the paper's best exit, TWAP for VWAP) | +1.09 | 1.58 | 0.23 | 0.44 | +1.39 (t = 1.89) | −0.75 | NOT CONFIRMED |
| **N3** | **US100, conservative** | **+3.02** | **2.54** | **0.028** | **0.73** | +2.66 (t = 2.15) | +5.31 (t = 1.38) | **CONFIRMED** |
| N4 | GER40 | +0.64 | 0.53 | 0.74 | 0.15 | +0.12 | +3.69 | NOT CONFIRMED |
| N5 | Gold (COMEX session) | +0.44 | 0.62 | 0.74 | 0.18 | +0.17 | +2.03 | NOT CONFIRMED |

**N3 robustness (post hoc,** [noise_area_robustness.py](noise_area_robustness.py)**):**

| Check | Net bps/day (t) |
|---|---|
| Lookback 10 / 14 / 20 days | +3.05 (2.55) / +3.02 (2.54) / +3.19 (2.67) |
| 60-min grid / 15-min grid | +2.65 (2.41) / +1.88 (1.44) |
| Cost 3 bps instead of 1.5 | +2.11 (1.77) |
| TWAP trailing stop | +3.06 (**3.50**), Sharpe 0.96 |
| **2011–2013, never used for this rule** | +2.93 (1.28), Sharpe 0.83 (3 years, low power) |
| 2014–2019 / 2020–2025 | +1.37 (0.96) / +4.86 (2.52) |
| Deflated Sharpe: family (N = 5) / all trials (N ≈ 731) | 0.90 / **0.22** |

**Reading this:** the effect is specific to US100, has the same sign and size in every period
including unseen 2011–13, and forms a plateau across parameters. It fails on US500, the paper's own
instrument. A plausible mechanism: leveraged Nasdaq ETFs (TQQQ/SQQQ) must rebalance in the direction of
the day's move before the close, and that flow is much larger relative to the market in the NDX than in
the S&P. Against it: one success among ~730 hypotheses is roughly what chance would produce, which is
what the DSR of 0.22 says. It needs a forward test before any money is committed.

## 15. Round 5 — prop books without Treasuries ([prop_round5.py](prop_round5.py), [prop_noise.py](prop_noise.py))

Bootstrap on 2014–25, intraday paths from minute bars, EA daily guard (3% two-step, 2% otherwise).
Pass probability · median days to pass. Zero-edge base rates use the demeaned combined books.

| Book | Two-step 10%/5% | One-step 10% (6% trailing) | Futures 50K (4% trailing) |
|---|---|---|---|
| **Zero edge** | 11–16% | 12–13% | 9–11% |
| **MR-06 US500, vol-scaled 2×** | **60% · 641 d** | 37% · 249 d | 29% · 227 d |
| MR-06 JP225 2× | 39% · 361 d | 31% · 157 d | 24% · 142 d |
| MR-06 AUS200 2× | 42% · 822 d | 24% · 334 d | 25% · 204 d |
| MR-06 US500 + JP225 + AUS200, 1× each | 55% · 435 d | 35% · 199 d | 32% · 121 d |
| **Noise-area US100 (N3) 2×** | 40% · 173 d | 26% · 65 d | 25% · 33 d |
| N3 3× | 34% · 92 d | 26% · 32 d | 21% · 26 d |
| **N3 with TWAP stop 3× (post hoc)** | **52% · 135 d** | 35% · 51 d | 26% · 39 d |
| MR-06 2× + N3 2× | 33% · 143 d | 25% · 54 d | 21% · 32 d |

**Reading this:**

- **MR-06 has the better edge-to-variance ratio,** so it has the higher pass probability, but it trades only ~19 times a year.
- **N3 trades almost every day,** so it is fast but noisier. Combining the two gives the speed of N3 and the pass rate of neither.
- **Choose by what the challenge rewards:**
  - A two-step account with no time limit favours MR-06.
  - A trailing-drawdown account is hard for every book here (about 2–3× the base rate at best).
- **These are in-sample sizing estimates.**

## 16. Round 6 — playing the prop game optimally (decision analysis, amendments A12–A13)

**Why this matters more than another edge test.** Five rounds show that robust retail edges are few and
small. With a small real edge, most of what a prop trader can still control is **how the edge is played
inside the firm's rules**:

- how much exposure to run;
- whether to size relative to the distance from the loss limit;
- whether to change sizing once funded.

These are decision problems with known theory:

- **Timid play is optimal in a favourable game** (Dubins & Savage 1965): with a positive edge and no deadline, smaller bets raise the probability of reaching the target before the floor.
- **CPPI** (Black & Perold 1992): exposure proportional to the cushion above a floor approaches the floor only asymptotically.
- **The funded account is an option:** the firm absorbs losses beyond the limit, so part of any account's value is the prop structure itself. The zero-edge twins measure that part.

This round tests no edge. It uses the return series of the two surviving books (in-sample) to rank
policies by money: EV per attempt and per account-month, including fee, pass rate, time, payouts and breach.

Rules: two-step 10%/5% (fee $500, 80% split, fee refunded on the first payout); one-step 10% (6% trailing);
futures 50K (4% EOD trailing, fee $150, 90% split, 50% consistency). All three have 365 days funded with
payouts every 14 days and an EA daily guard. Stationary bootstrap of 2014–25, 1,500 runs per cell; **every
run counts** (see the A12 correction). US$ per $100K two-step account ($50K futures).

### 16.1 Sizing changes the money more than the edge does

Two-step 10%/5%. Pass rate (zero-edge twin in brackets) · EV per attempt · mean months · EV per account-month.

| Book | Fixed 1× | Fixed 2× | Fixed 3–4× (fastest) | CPPI k = 10 | CPPI k = 20 |
|---|---|---|---|---|---|
| **MR-06 US500** (B1) | 77% (22%) · $2,782 · 56 mo · $50 | 60% (15%) · $3,818 · 28 mo · $137 | 3×: 47% (13%) · $3,678 · 17 mo · **$212** | 79% (16%) · $2,655 · 72 mo · $37 | cap 2×: **72% (17%) · $3,971** · 53 mo · $75 |
| **Noise-area US100** (B2) | 64% (24%) · $4,612 · 24 mo · $190 | 39% (17%) · $3,337 · 8 mo · $406 | 4×: 31% (17%) · $2,221 · 2.8 mo · **$783** | **78% (19%) · $4,801** · 62 mo · $77 | 49% (12%) · $3,405 · 75 mo · $46 |
| Noise-area US100, TWAP stop (B3, post hoc) | 91% (27%) · $6,249 · 37 mo · $171 | 65% (21%) · $7,204 · 16 mo · $454 | 4×: 44% (20%) · $5,218 · 4.7 mo · **$1,101** | 97% (17%) · $5,550 · 46 mo · $121 | 89% (15%) · **$7,965** · 47 mo · $168 |

**What this shows:**

- **The edge is what pays.** Zero-edge twins pass only 12–27% and earn between −$400 and +$800 per attempt. Every policy's edge value is positive.
- **For the same edge, the policy moves EV per account-month by 5–20×** (MR-06: $10 at 0.5× to $212 at 3×). Faster, riskier play wins per unit of time; cushion sizing wins per attempt.
- **Cushion sizing (CPPI) is the "timid play" lever.** It lifts pass rates well above fixed sizing on the same edge (MR-06 79% vs 60%; US100 78% vs 39%), while zero-edge twins stay at 16–19%. The boost comes from the edge, but it takes 4–6 years and 21–22% of runs are still undecided at the 10-year mark (k = 10).
- **By the pre-registered decision rule (maximum EV per account-month with positive edge value):** fixed 3× for MR-06 and fixed 4× for US100 on the two-step account; fixed 3–4× on the other rule sets.
- **With 30% payout haircut for counterparty risk:** MR-06 3× $143 per month; US100 4× $506 per month.

### 16.2 Other rule sets (EV per account-month at the recommended policy)

| Book | Two-step 10%/5% | One-step 10% (6% trailing) | Futures 50K (4% trailing) |
|---|---|---|---|
| MR-06 US500 | $212 (3×) | $233 (3×) | $79 (3×) |
| Noise-area US100 | $783 (4×) | $566 (4×) | $156 (3×) |
| Noise-area US100, TWAP stop (post hoc) | $1,101 (4×) | $870 (4×) | $263 (3×) |

Trailing-drawdown futures accounts return 3–5× less than the two-step account for the same edge.

### 16.3 Funded-stage sizing (A13)

Challenge at the A12-recommended exposure. Funded stage:

| Book (two-step) | Funded policy | Breached within the year, given pass | EV per attempt | EV per account-month |
|---|---|---|---|---|
| MR-06 US500 | same (3×) | 53% | $3,678 | **$212** |
| | CPPI k = 40, cap 4× | **19%** | **$3,889** | $208 |
| | fixed 1× | 9% | $1,529 | $82 |
| Noise-area US100 | same (4×) | 99% | $2,221 | **$783** |
| | CPPI k = 40, cap 4× | 73% | $2,246 | $511 |
| | fixed 2× | 86% | $2,404 | $628 |

**Reading this:**

- **Money per month:** keep the challenge sizing. Funded accounts then churn, being breached within the year in most cases, but pay fast.
- **Keeping the funded account:** switch to cushion sizing once funded. For MR-06 it breaches 19% of the time instead of 53%, for about the same money per attempt.
- **Firms police aggressive funded behaviour** (consistency rules, payout caps, account reviews), and the presets only partly model this. Check each firm's actual terms before relying on the aggressive end.

### 16.4 What round 6 does and doesn't show

- **It shows** that, with the two edges this research found, prop accounts are positive-EV in this simulation, and that sizing policy is the biggest lever left: it changes money per month by an order of magnitude.
- **It doesn't show new edges.** The return series are in-sample (2014–25), the fees and terms are placeholders, and the bootstrap can't reproduce regime changes. N3 in particular is a candidate, not an established edge (DSR 0.22).
- **Parallel accounts on the same strategy are not independent.** They pass and fail on the same market days, so running five accounts is not five independent bets.

## 17. Appraisal: how much to trust this

| Issue | Effect on conclusions | Severity |
|---|---|---|
| **Data are CFD-style quotes, not exchange prints** (HistData bid quotes; Yahoo indices) | Artifacts at spread-widening times are real (§8). Index results at 15:30–16:00 and 17:00–17:30 Berlin are at liquid hours, and the cross-source check agreed (correlation 0.98) | High for FX; low–medium for indices |
| **Power of the confirmation tests** | R3/R4 (ORB, 35–50% power) can't rule out a smaller real effect. R2 (80%) and R7 (93%) are informative | Medium |
| Multiple testing | About 730 hypotheses in total (64 in rounds 1–4, 8 literature tests and 653 scan candidates in round 5, plus W1 and family N). The round-5 scan confirmed nothing, which is what a working multiple-testing guard should produce. **N3 (noise-area, US100) passes Holm in its own family but has a DSR of only 0.22 over all trials.** MR-06 survives BH in discovery, independent confirmation, DSR 0.95 (N = 39, daily data) and R7 at p = 0.03. R7's DSR at N = 57 is only 0.29: **the 2014–25 minute sample alone wouldn't justify it.** S2 passes Holm within its round (p = 0.011), and its DSR at N = 64 is 0.70 with only 92 monthly observations. Its case rests on replicating a published effect after the paper's sample, not on DSR | Medium |
| **Treasury end-of-month data** | IEF/TLT are ETFs, not futures. The effect is also documented in futures and swaps (Hartley & Schwarz §4.2), but futures roll near month-end in Feb/May/Aug/Nov, and the SQX build must handle the roll | Medium: verify on ZN/ZB futures data |
| **Data gaps** | HistData serves WTI only to 2023 and Euro Stoxx 50 only to 2019. The T1–T3 oil tests use 2019–2023; Brent (to 2025) is reported as a secondary and agrees | Low |
| **Post-hoc variant** | The TWAP-stop version of N3 was pre-registered only for US500. Its better US100 result (Sharpe 0.96) is post hoc | Medium: treat the conservative N3 as the tested rule |
| **Prop books are in-sample for sizing** | The notional weights in §13.3 were chosen on the same 2014–25 history the bootstrap re-uses. The pass rates are upper bounds for a trader who picks the best row | Medium |
| Post-hoc analysis | The FX clean windows, the P10 R-multiples, the P12 perturbations and the prop diagnostics are post hoc and labelled so. They were used to *downgrade* claims, never to promote one | Low |
| Researcher degrees of freedom | Round 3 was chosen after seeing round 2. That's why it used only unseen data | Low |
| Costs are assumptions | ORB, GER40 and FX results flip sign within ±1 bp of cost, so no realistic cost model rescues them. MR-06 (~20 bps) is robust to costs | Low for MR-06 |
| Regime dependence | MR-06 is strongest 2020 → and absent before 1990. The mechanism (index products, dealer liquidity provision) can change | Medium: monitor yearly |
| No holdout left | Every series here is now in-sample for an SQX build | **Paper-trade or use post-Sep-2026 data first** |

**Overall confidence:**

- **High:** MR-06 is a real, US-specific, post-1990 effect of about 20 bps per trade, whether you enter at the close or at 15:55.
- **High:** Treasury end-of-month is real and persisted after publication, but it is outside the user's scope.
- **Moderate:** noise-area momentum on US100 is real enough to paper-trade, not to fund. It passed its own family test, a parameter plateau and an unseen 2011–13 period, but fails on US500 and doesn't survive deflation over all trials.
- **High:** simple time-of-day, day-of-week, streak, IBS and breakout rules on 24 prop instruments, and the published commodity, crude-oil and Bitcoin intraday rules, don't survive out of sample at retail costs.
- **High:** GER40 close momentum, the ORBs, FX fix windows (daily and month-end), the announcement premium, the FOMC cycle, overnight drift and turn of month are **not** tradeable edges at retail costs today.
- **Moderate:** the prop pass-rate estimates. They depend on the challenge rules, the guard, leverage and the bootstrap, and the sizing is in-sample.

## 18. What changes in the plan

- **Build candidates (no Treasury strategies):**
  1. **MR-06** on US500 (primary) and US100: 15:55 entry after three down closes, exit at the next close, **volatility-scaled size** (min(2, 1% ÷ 20-day vol)). JP225 (entry 5 min before the Tokyo close) and AUS200 are optional extra markets.
  2. **IM-04 noise-area momentum on US100** (N3 rule, 30-min marks, 14-day lookback, flip at the opposite band, flat at 16:00; the TWAP trailing stop as a pre-registered variant for the forward test). **Paper-trade it first** (DSR 0.22).
- **For prop challenges, choose the sizing policy by objective (§16):**
  - **Maximum money per month** (you can afford repeated attempts): fixed 3–4× exposure. US100 noise-area ≈ \$780 per account-month on a two-step account; MR-06 ≈ \$210. Most attempts fail, but the ones that pass pay.
  - **Maximum chance of passing a given attempt:** cushion (CPPI) sizing, exposure = min(cap, k × distance to the loss floor), with k = 10–20. MR-06 passes 72–79% of the time, US100 78%, against 15–19% for zero edge. It takes years.
  - **Once funded:** keep the sizing for speed, or switch to CPPI (k = 40) to keep the account (MR-06 funded breach 19% vs 53%).
  - **Throughout:** the EA daily guard is mandatory, and the two books should run in separate accounts.
- **Excluded by the user:** CF-07 Treasury end-of-month (confirmed, but out of scope).
- **Drop from the build list:**
  - GER40 close momentum, both ORB variants, the FX fix windows (daily and month-end), commodity and crude-oil intraday momentum, EIA-day rules, Bitcoin intraday/hour/Monday rules, the crypto-weekend Monday trade, and noise-area on US500/GER40/gold;
  - the Treasury auction cycle, FOMC cycle, announcement days, last-30-minute momentum/reversal, overnight premium, turn of month, IBS-only, non-US mean reversion, bond reversal, and all 653 scan candidates.
- **Data rule for the coding agent:** FX, metal and energy tests need bid/ask (or mid) data, or must avoid windows touching 16:00–19:00 NY on bid-only data.
- **Open leads (not evidence):** silver's pre-fix hour (real, t = 3.4 out of sample, but 2.4 bps against a 5-bps cost; worth checking with a tighter-spread broker); rebalancing Calendar signal (S6); month-start continuation (P16).

## Reproduce

```bash
cd research/validation
export YAHOO_CACHE=/path/to/cache HISTDATA_CACHE=/path/to/cache BINANCE_CACHE=/path/to/cache
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
python3 run_round4.py           # S1–S7, I1             -> results/round4.json
python3 round4_followup.py      # S2 robustness, books  -> results/round4_followup.json
python3 run_scan.py discover    # X scan, discovery     -> results/scan_discovery.json (committed before the next step)
python3 run_scan.py confirm     # X scan, confirmation  -> results/scan_confirmation.json
python3 run_round5.py           # T1–T8, I2             -> results/round5.json
python3 run_world_mr06.py       # W1                    -> results/world_mr06.json
python3 run_noise_area.py       # N1–N5                 -> results/noise_area.json
python3 noise_area_robustness.py # N3 checks (post hoc) -> results/noise_area_robustness.json
python3 prop_round5.py          # MR-06 Asia books      -> results/prop_round5.json
python3 prop_noise.py           # MR-06 + N3 books      -> results/prop_noise.json
python3 prop_lifecycle.py B1 && python3 prop_lifecycle.py B2 && python3 prop_lifecycle.py B3 && python3 prop_lifecycle.py merge   # §16 (A12)
python3 prop_lifecycle_funded.py B1 && python3 prop_lifecycle_funded.py B2 && python3 prop_lifecycle_funded.py B3 && python3 prop_lifecycle_funded.py merge   # §16.3 (A13)
python3 -m unittest discover -s tests
```

HistData files are fetched year by year by `data_histdata.fetch_year` (free, no key). Treasury auction dates come from the TreasuryDirect API (`data_calendar.treasury_auctions`), 10-year yields from FRED (`data_fred.py`). The post-hoc
diagnostics in §7.3, §8 and §9 come from [diagnostics_post_hoc.py](diagnostics_post_hoc.py)
(`results/diagnostics_post_hoc.json`).
