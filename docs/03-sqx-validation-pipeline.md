# 03 — SQX Validation Pipeline

How each hypothesis goes from template to accepted strategy inside StrategyQuant X. The numeric
thresholds are **starting defaults**. Adjust them per family *before* the first build, write them on
the edge card, and don't change them after seeing results.

---

## 1. Data and cost setup (Phase 0)

### 1.1 Data

| Asset | Recommended source | Notes |
|---|---|---|
| FX | Tick or M1 history (e.g., Dukascopy, which SQX can import) **plus** your broker's own history | Compare the two. Broker spreads and session times are what you will trade |
| Index / metal / energy CFDs | Broker history (M1) | Check session gaps, daily breaks and DST behaviour |
| Futures | Vendor back-adjusted continuous contracts | Record the roll method. Back-adjustment changes absolute price levels, so avoid rules on absolute price |
| Crypto | Exchange or broker M1 | 24/7 data, so decide explicitly how D1 bars are cut |

**Data QA checklist per symbol:** missing bars and gaps; spikes (>10× ATR bar ranges); duplicate
timestamps; session open/close times vs the exchange; DST transitions; Sunday bars (use New York-close
server time, GMT+2/+3, to get 5 D1 bars per week); roll dates (futures).

### 1.2 Cost model

| Component | Rule |
|---|---|
| Spread | 75th-percentile spread of your broker **at the times the strategy trades**. Open-of-session and rollover spreads are wider |
| Commission | Actual per-lot or per-contract round trip |
| Slippage | Market and stop orders: 1 tick (futures) / 0.2–0.5 pip (FX majors) as a base. Limit orders: 0, but require price to **trade through** the limit, not just touch it |
| Swap | Three scenarios for swing strategies: 0 / current / adverse. SQX uses the swap values you enter, not historical rate differentials |
| Stress | Every candidate is retested at **1.5×** and **2×** spread + slippage |

### 1.3 Precision

Build at a faster precision for search speed. Then **retest every candidate at 1-minute or real-tick
precision**, which is mandatory for intraday strategies and anything with SL/PT that can be hit inside
a bar.

---

## 2. Data partitioning

```
|<------------------- development range (in SQX) ------------------->|<-- HOLDOUT -->|
|  OOS-A (older) |            IS (build / rank)             | OOS-B    |  locked until |
|    ~15%        |               ~60–70%                    |  ~15–20% |  Phase 4      |
```

- **Holdout:** the most recent **2–3 years**, never loaded in any SQX range until Phase 4. Log every look, even an accidental one.
- **Two OOS segments** (one before and one after IS) stop the builder from selecting strategies that only fit the most recent regime. SQX supports multiple IS/OOS ranges.
- For **fixed-rule families** (F5, F6), use the whole development range for the Phase 1 study, but the holdout is still locked.
- Minimum development history: D1 ≥ 12 years; H1/H4 ≥ 8 years; intraday M5–M30 ≥ 6 years. Where history is shorter, pooling across markets is mandatory.

---

## 3. Builder configuration

### 3.1 General settings (all families)

| Setting | Default | Why |
|---|---|---|
| Strategy type | **Strategy from template** (the family skeleton in doc 02), or Simple / Multi-TF with a restricted block list | A smaller search space means a smaller effective N (doc 01 §1) |
| Build mode | Genetic evolution, moderate population and generations | Record the evaluated count in the research log |
| Entry conditions | 1–2, maximum 3 including filters | Each extra condition must survive ablation (§4 Stage 9) |
| Indicator periods | The family's range from doc 02 | Keeps search inside the published region |
| Shift | 0–2 (maximum 3) | Large shifts are a classic overfitting channel |
| Symmetric rules | ON for trend and breakout families; long-only for index MR | Symmetry halves the degrees of freedom |
| SL | Mandatory, ATR-based (wide for MR) | Survivability; comparability |
| Free parameters | ≤ 6 per strategy | Rule of thumb: ≥ 30 trades per free parameter |

### 3.2 Ranking and IS filters

- **Fitness:** a composite of **Ret/DD**, equity-curve stability, and trade count. **Don't rank on net profit or win rate alone.** Net profit favours leverage and tail risk; win rate favours negatively skewed fits.
- **IS filters (defaults):**

| Metric | Swing (D1/H4) | Intraday (≤ H1) |
|---|---|---|
| Trades (IS) | ≥ 100, pooled across markets allowed | ≥ 300 |
| Profit factor | ≥ 1.3 | ≥ 1.2 |
| Ret/DD | ≥ 3 over the IS period | ≥ 3 over the IS period |
| Average trade | ≥ 3× round-trip cost | ≥ 3× round-trip cost |
| Family signature | Within the ranges in doc 02 | Within the ranges in doc 02 |

- **OOS filters (both OOS-A and OOS-B):** PF ≥ 1.1; OOS Ret/DD per year ≥ 50% of IS; OOS trades ≥ 30; no OOS segment with a loss larger than the IS max drawdown.

---

## 4. The robustness funnel

Build it as an SQX **Custom Project** per family, so the same pipeline runs every time. Cheap tests
come first.

| Stage | Test (SQX feature) | Pass rule (default) | Kills |
|---|---|---|---|
| 0 | **Build** with IS + OOS filters → databank `F#-raw` | §3.2 | Obvious noise |
| 1 | **Correlation de-dup** (Correlation Filter custom analysis on daily P&L) | Drop the lower-fitness member of any pair with ρ > 0.7 | Near-duplicates that inflate apparent success |
| 2 | **Higher-precision retest** (1-minute / real tick) | PF drop ≤ 15%; Ret/DD drop ≤ 25% | Intrabar-fill illusions |
| 3 | **Cost stress** (spread and slippage ×1.5 and ×2) | PF ≥ 1.1 at ×1.5; still profitable at ×2 | Cost-fragile scalps |
| 4 | **Monte Carlo retest**, ≥ 200 runs: randomise history data (small OHLC noise), strategy parameters (±10–20%), spread/slippage, and randomly skip 5–10% of trades | At the 95% confidence level: net profit > 0, Ret/DD ≥ 50% of the original, max DD ≤ 2× the original | Parameter and path fragility |
| 5 | **Monte Carlo trade manipulation** (reshuffle order, resample) | 95th-percentile DD within your per-strategy risk budget | Understated drawdown |
| 6 | **Retest on additional markets / timeframes**, no re-optimisation | Family rule, e.g., F1 ≥ 60% of an 8+ market basket; F2 ≥ 4 of 6 indices; F3 ≥ 3 markets | Single-market curve fits |
| 7 | **Walk-Forward Matrix** (e.g., 5–15 runs × 10–30% OOS) | ≥ 60–70% of matrix cells pass, and passing cells form a contiguous cluster (Pardo, 2008) | Unstable optimisation |
| 8 | **Optimisation profile / System Parameter Permutation (SPP)** | ≥ 70% of the ±30% parameter neighbourhood is profitable; the **SPP median** meets minimum Ret/DD (Walton, 2014). **Use the SPP median, not the best run, as the performance expectation** | Parameter peaks |
| 9 | **Ablation**, run manually: remove each condition or filter one at a time | Each component must improve OOS Ret/DD; otherwise remove it and re-test | Decorative complexity |
| 10 | **Random-entry benchmark**: same exits, same trade frequency, random entries (≥ 500 runs) | Strategy above the 95th percentile of the random distribution (Aronson, 2006; Masters, 2020) | Exit-only or drift-only "edges" |
| 11 | **Statistics** on the surviving set: DSR (with logged N) and PBO | DSR ≥ 0.90; family PBO < 0.5 (target < 0.25) | Selection bias |
| 12 | **Holdout** (Phase 4, portfolio level, once) | Doc 00 Gate 4 | — |

**Expected attrition:** 95–99% of Stage 0 candidates will fail. If more than about 10% of raw builds
survive to Stage 6, your filters are probably too loose. Check with the noise-calibration test (§5).

---

## 5. Noise-calibration test (one per template)

This is the single most important SQX-specific test. It measures **how often your exact build and
funnel configuration "discovers" strategies in data that contains no edge.**

**Procedure**

1. Create 3–5 **synthetic series** from each real market by destroying *only* the structure your hypothesis claims, while preserving everything else (volatility level, volatility clustering, seasonality, price range).
2. Import each as a custom symbol in SQX Data Manager, with the same costs and sessions as the original.
3. Run the **identical** Custom Project (same template, filters, funnel and run length).
4. Compare survivor counts and quality between real and synthetic data.

**Permutation recipes by family**

| Family | Claimed structure | Destroy it by | Preserve |
|---|---|---|---|
| F1 Trend | Positive autocorrelation over days to months | Stationary block bootstrap of daily returns with a short block (Politis & Romano, 1994), rebuilding each day's OHLC from its original intraday shape | Volatility clustering (partly), fat tails |
| F2 Index MR | Negative autocorrelation over 1–5 days | Same as F1. The null keeps drift but removes short-horizon reversal | Drift, volatility |
| F3 Intraday momentum | Early-session return predicts late-session return | Shuffle the **late-session segment** across days (within volatility buckets) | Intraday seasonality, daily volatility |
| F4 Vol breakout | Compression → expansion, with continuation | Shuffle bar returns within each day, keeping daily ranges | Volatility persistence across days |
| F5/F6 Calendar and time-of-day | Returns depend on date or time | Randomly re-assign calendar dates or time slots to days or hours | Everything else |

**Pass rule:** the survivor rate on synthetic data is **< 10% of the real-data rate**, and the best
synthetic survivor is worse than the median real survivor. If noise produces comparable candidates,
tighten the template and filters. **Don't lower the bar on real data.**

---

## 6. Statistical checks outside SQX

Export each surviving strategy's daily P&L (and the full Stage 6 candidate set per family) to CSV.

### 6.1 Deflated Sharpe Ratio (Bailey & López de Prado, 2014)

$$
\text{DSR} = \Phi\!\left(\frac{(\widehat{SR}-SR_0)\sqrt{T-1}}{\sqrt{1-\hat\gamma_3\widehat{SR}+\frac{\hat\gamma_4-1}{4}\widehat{SR}^2}}\right),\quad
SR_0=\sqrt{V[\widehat{SR}_n]}\left((1-\gamma)\Phi^{-1}\!\left(1-\tfrac1N\right)+\gamma\,\Phi^{-1}\!\left(1-\tfrac1{Ne}\right)\right)
$$

Here SR̂ is the non-annualised Sharpe of the chosen strategy over T observations, γ̂₃ and γ̂₄ are
skew and kurtosis, **N is the logged number of independent trials** (use the number of
de-correlated clusters as a practical estimate), V[SR̂ₙ] is the variance of Sharpe across trials, and
γ ≈ 0.5772.

### 6.2 Probability of Backtest Overfitting (Bailey, Borwein, López de Prado & Zhu, 2017)

Combinatorially symmetric cross-validation (CSCV):

1. Build a T × M matrix of daily P&L for the M candidates, split into S = 16 time blocks.
2. For every combination of S/2 blocks as in-sample (12,870 combinations), select the best in-sample candidate and record its **rank** out of sample.
3. PBO = the share of combinations where the in-sample winner ranks **below the OOS median**.

### 6.3 Multiple-testing alternatives

White's Reality Check (White, 2000), Hansen's SPA test (Hansen, 2005), or Romano–Wolf stepdown
(Romano & Wolf, 2005) on the candidate set versus a benchmark (zero or buy-and-hold for long-only
index strategies).

---

## 7. SQX pitfalls checklist

- [ ] **Multi-TF / multi-symbol look-ahead:** custom blocks must reference closed bars. Watch different session closes across symbols.
- [ ] **Session definition** for CFDs: the cash-session open and close are set explicitly; DST verified on both US and EU transition weeks.
- [ ] **Stop and limit fills at gaps:** stop orders fill at the gap price, not the stop level; confirm SQX and your platform agree.
- [ ] **Exit-at-end-of-day time** matches broker server time and leaves a buffer before the daily break.
- [ ] **"Improve existing strategy" and repeated re-optimisation** add to the trial count. Log them.
- [ ] **Exported code parity:** after export (MT5/TS/NT), run the strategy in the target platform's tester over the same period and reconcile trades one by one for at least 50 trades.
- [ ] **Pending-order expiry, max trades per day and time ranges** behave identically in SQX and the target platform.
- [ ] **Absolute price levels** are never used on back-adjusted futures data.

---

## 8. Documentation per accepted strategy

1. Edge card (`research/templates/edge-card-template.md`)
2. Completed acceptance checklist (`research/templates/strategy-acceptance-checklist.md`)
3. SQX files: strategy `.sqx`, Custom Project config, databank export
4. Monte Carlo drawdown bands (5th / 50th / 95th percentile), used later for live monitoring
5. Research-log rows covering all trials that led to it
