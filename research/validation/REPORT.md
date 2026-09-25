# Own-data validation report

**What this is:** every edge in the plan tested on real market data, with the tests fixed *before*
looking at results ([PREREGISTRATION.md](PREREGISTRATION.md), committed at 09:10 UTC on 2026-09-25,
before any result existed). It also records a pre-registered search for new edges, and an honest
appraisal of what these results can and can't support.

Data: Yahoo daily bars (13 indices from 1970/1980s/1990s; 25 ETFs from their launch) and Yahoo
60-minute bars (US ETFs and 9 USD pairs, Oct/Dec 2023 → Sep 2026). Dukascopy minute data was planned
but the feed blocked this connection (see §7).

---

## 1. Bottom line

| Edge | Verdict | Gross | After realistic costs | Tradeable? |
|---|---|---|---|---|
| **E06 — next day after ≥ 3 consecutive down closes, US indices** (new, found by the exploratory scan) | **CONFIRMED out of sample** | +24.7 bps/trade, t = 5.1 (1994 → ) | **+21.9 bps/trade, t = 4.5** on a CFD after spread and overnight swap | **Yes**: ~22 trades/yr; Sharpe ≈ 0.66 at 1× |
| Pre-holiday (Ariel 1990), S&P 500 | VALIDATED | +12.0 bps excess, t = 3.2 | +8.3 bps, t = 1.7 | Marginal; ~9 trades/yr |
| Overnight premium (close → open), SPY/QQQ | VALIDATED (gross) | +4.0 bps/night, t = 4.7 | **+0.5 to +0.8 bps, t ≈ 1** after financing / swap | **No**: it is mostly the cost of money |
| TSMOM trend following, 25 ETFs | VALIDATED (just: Holm p = 0.0498) | Sharpe 0.58 | — | **Adds nothing over volatility-scaled buy-and-hold** (difference −20 bps/month, t = −0.4) |
| Turn of month (control) | **DECAY CONFIRMED** | +10.4 bps/day before 2001 (t = 3.9) → +2.2 after (t = 0.7) | — | No (as the literature said) |
| Intraday momentum, last 30 min (Gao / Baltussen) | **Reversed**: significant *opposite* sign 2023–26 | −1.7 bps/day, t = −2.8 | — | No; now looks like a reversal pattern (lead, see §5) |
| IBS dip-buy (US); IBS non-US; 5-day low; 13-index reversal; rebalancing flows; FX fix combo; Nagel VIX split | NOT VALIDATED | — | — | — |

The strongest single finding: **US index short-term reversal is real, but only in a specific form.**
"Three or more down days" is strong and confirmed, and the effect only exists **since ~1990**. Before
that the S&P 500 showed the *opposite* (−11 bps, t = −2.7), exactly as the index-product mechanism of
Baltussen, van Bekkum & Da (2019) predicts. Popular variants (IBS < 0.2, 5-day lows) were **not**
significant under the pre-registered tests.

---

## 2. How the tests were run

- Pre-registered: rule, prediction, sample splits, costs, statistics and verdict rules before any data was examined. Two amendments were committed before the tests they affected: **A1** (exploratory scan) and **A2** (Yahoo 60-minute substitution).
- Per test: Newey-West HAC t (lag ≥ 5), one-sided p in the predicted direction, stationary-bootstrap 95% CI (2,000 resamples), year-by-year sign share, pre- vs post-publication split, net of pre-registered cost.
- **Multiple testing:** Holm and Benjamini-Hochberg across the 15 primary tests that ran. Deflated Sharpe ratio with N = 35 trials (15 primary + 20 exploratory).
- Verdict rules are applied mechanically by [verdicts.py](verdicts.py).

## 3. Primary tests (all results)

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
- **P15 by window (USD return, bps/day):** NY close → Tokyo **+1.78 (t = 3.9)**, Tokyo → London open +0.58 (t = 1.0), London open → London fix −0.69 (t = −0.6), **London fix → NY close −2.03 (t = −3.1)**. Two of Krohn, Mueller & Whelan's four windows replicate almost exactly out of sample (paper: +2.1 and −1.9); the other two don't. The pre-registered combination used one of the failing windows.
- **P6 by period:** 2007–12 +87 bps/month (t = 1.5), 2013–19 +60 (t = 1.2), 2020 → +94 (t = 2.0).

## 4. Exploratory scan (new edges), pre-registered in amendment A1

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

## 5. Leads generated by this audit (NOT evidence; need a fresh pre-registered test)

1. **Last-30-minute reversal in the 0DTE era:** P7y/P9y are significantly negative in 2023–26, the opposite of Gao and Baltussen. This is consistent with dealers being net long gamma (Dim, Eraker & Vilkov, 2024). It needs 2014–2021 minute data to show the flip, plus a fresh post-2026 sample.
2. **Month-start continuation after equity outperformance:** P16's significant opposite sign suggests stocks keep rising on the first day of a month after beating bonds. My implementation may not match Harvey et al.'s timing; read their method and pre-register properly.
3. **FX W1 + W4:** long USD NY close → Tokyo, short USD London fix → NY close. Both replicate Krohn et al. out of sample. Combined gross ≈ 3.8 bps/day vs ~2 bps cost. Pre-register the W1 + W4 combination and test on data not used here (2004–2023 hourly).

## 6. Can the survivors be traded? ([implementability.py](implementability.py))

Costs: US500 CFD spread 0.75 bps round trip; overnight financing = 13-week T-bill rate (^IRX) × nights / 360; CFD swap = T-bill + 2.5%/yr.

| Edge (1994 →) | Trades/yr | Gross bps | Net, futures/cash | Net, CFD | Ann. return at 1× (CFD) | Sharpe 1× | Max DD 1× |
|---|---|---|---|---|---|---|---|
| E06 | 22.1 | 24.7 (t = 5.1) | 22.2 (t = 4.6) | **21.9 (t = 4.5)** | 4.8% | 0.66 | −18.9% |
| P18 pre-holiday | 9.1 | 10.5 (t = 2.2) | 8.3 (t = 1.7) | 8.3 (t = 1.7) | 0.8% | 0.27 | −8.5% |
| P17 overnight | 252 | 3.3 (t = 4.8) | **0.8 (t = 1.2)** | **0.5 (t = 0.8)** | 1.3% | 0.12 | −56% |

**Prop-challenge simulation** (propsim, two-step 10%/5%, 5% daily, 10% max; stationary bootstrap
of 2013 → CFD-net daily P&L; 3% EA daily guard):

| Book | Leverage | P(pass both) | Median days to pass |
|---|---|---|---|
| E06 + P18 (~30 trade days/yr) | 2× | 67% | 425 |
| | 4× | 61% | 186 |
| | 8× | 58% | 108 |

This beats the zero-edge 33% base rate, but is **too slow on its own**. The guard assumes exits near
−3%; E06 holds overnight, so gaps can blow through it. Realistic leverage is ≤ 3–4×. E06 is a
**building block for a prop book, not a complete one.**

## 7. Appraisal: how much to trust this

| Issue | Effect on conclusions | Severity |
|---|---|---|
| **Intraday tests used only 2023–26 Yahoo 60-min data** (Dukascopy blocked; P10–P12, P14 not run) | Intraday verdicts describe the 0DTE regime only; ORB, GER40 and the overnight-drift control are **untested** | High for intraday edges |
| Yahoo index OHLC (price index, not tradeable; H/L quality in early years) | Daily index tests assume trading at the official close; a CFD/futures close differs slightly | Medium |
| Execution at the close (E06, P18, IBS) | The signal uses today's close; in practice you trade at 15:59 or in the closing auction. A late-day move can differ | Medium: test with minute data before live |
| Costs are assumptions (0.75–2 bps + financing) | E06's edge (≈ 22 bps) is 10× costs, so it's robust. P18 and P17 are cost-fragile | Low for E06, high for P17/P18 |
| Multiple testing | 35 trials counted; E06 survives BH in discovery, independent confirmation, and DSR 0.95. But the E06 variants in §4 are post-hoc | Low–medium |
| Researcher degrees of freedom before pre-registration | Tests were chosen after reading papers, not after seeing this data. The P16 timing choice may not match the paper | Low–medium |
| ETF TSMOM universe (25 ETFs, many commodity ETFs with contango) | Not the MOP futures universe; P6 is a weak test of TSMOM itself | Medium |
| Regime dependence | E06 is strongest 2020 → ; the mechanism (index products, dealer gamma) could change | Medium: monitor |
| No holdout left | Everything here is now in-sample for any SQX build | **Build on fresh data or paper-trade first** |

**Overall confidence:** high that E06 is a real, US-specific, post-1990 effect. Moderate that it
survives realistic close-of-day execution. High that the overnight premium and turn of month are not
tradeable edges today. Low confidence in anything intraday until minute data from 2014–2021 is tested.

## 8. What changes in the plan

- **Add E06 as the top daily candidate** for US500/US100/US30: long at the close after ≥ 3 down closes, exit at the next close (or after 2–3 days; pre-register which before building).
- **Demote:** IBS-only dip-buying (not significant), non-US index mean reversion (negative), turn of month (dead), overnight premium (financing eats it), and last-30-minute momentum (reversed since 2023).
- **FX:** replace the W3 + W4 rule with a pre-registered W1 + W4 test.
- Plan for intraday edges: run the ready scripts on Dukascopy minute data when the feed allows (see below).

## Reproduce

```bash
cd research/validation
export YAHOO_CACHE=/path/to/cache DUKA_CACHE=/path/to/cache
python3 run_daily.py            # P1–P6, P16–P19   -> results/daily.json
python3 run_exploratory.py      # A1 scan          -> results/exploratory_*.json
python3 robust_e06.py           # E06 robustness   -> results/e06_robustness.json
python3 run_intraday_yahoo.py   # A2 intraday      -> results/intraday_yahoo.json (Yahoo keeps only ~730 days of 60-min bars)
python3 verdicts.py             # pre-registered verdict rules -> results/verdicts.json
python3 implementability.py     # costs, financing, prop simulation -> results/implementability.json
python3 -m unittest discover -s tests
```

`data_dukascopy.py` is ready for the minute-data tests (P7–P14 as originally specified) once the
feed is reachable.
