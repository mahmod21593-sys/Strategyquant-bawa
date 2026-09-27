# GT — The Tokyo fix on Gotobi days (USDJPY)

**Verdict:** BUILD as a small FX sleeve in its own account (round 19: EDGE by the pre-registered rule; family grid EDGE FAMILY) · **Grade:** A− on own data; the mechanism is published · **Prop fit:** Medium: it's a real edge but slow, and it needs round-trip costs ≤ 1 bp and an entry at the fix minute.

## Claim and mechanism

Japanese importers pay foreign suppliers in dollars on the 5th, 10th, 15th, 20th, 25th and 30th of the month ("Gotobi"), and on the month's last business day. They buy those dollars at their bank's Tokyo fixing rate, which is set from the market at **09:55 JST**. The banks buy dollars ahead of the fix (pre-hedging). That pushes USD/JPY up into 09:55, and the temporary pressure unwinds after the fix. The yen weakens into the fix and strengthens after it.

- **Source:** Ito & Yamada, [NBER WP 22820](https://www.nber.org/system/files/working_papers/w22820/w22820.pdf) (2016); *Journal of International Money and Finance* (2017). Sample 1999–2013.
- **Their result:** "USD and EUR tend to appreciate toward the fixing on average because of the buying pressure." A 5-minute-long / 5-minute-short switch at 09:55 earned 1.8 bps on average, "particularly high at 5th and 10th days … and the end of month."
- **Related:** Krohn, Mueller & Whelan (2024, *JF*): the dollar rises from the NY close to the Tokyo fix and falls after, on all days (the round-1 FX-01 card).

## Own-data evidence (pre-registered in A33; [REPORT.md](../../research/validation/REPORT.md) §22.5)

**The tested rule (G3):** on Gotobi days, **sell USDJPY at 09:55 JST and buy back at 10:55 JST**. Cost 1.0 bp per trade.

| Test | Data | Result |
|---|---|---|
| **G3, primary** (after the paper's sample) | HistData 1-minute, 2014-01 → 2026-09, 963 trades | **Net +1.10 bps per trade, HAC t 2.59, Holm p 0.010**; gross +2.10 bps (t 5.0). Positive in both halves: +0.49 (2014–19), +1.64 (2020–26). **EDGE** |
| G1, the pre-fix leg (long 09:00 → 09:55) | same | Gross +1.61 (t 3.6), net +0.61 (t 1.4, Holm 0.087): real, but it doesn't clear 1 bp |
| G2, mechanism: pre-fix return on Gotobi days minus other days | same | +1.04 bps (t 2.05) |
| Replication | 2003–2013 | Post-fix +3.00 bps gross (t 4.9); pre-fix +1.78 (t 3.6) |
| 42-variant grid (2 pairs × 7 windows × 3 day sets) | 2003–2026 | **EDGE FAMILY:** SPA 0.027, PBO 0.05, walk-forward Sharpe 1.06 (t 2.85). Romano–Wolf survivors: USDJPY post-fix on all Gotobi days, and three EURJPY month-end variants |

**Post hoc checks** (labelled; they don't change the verdict):

| Check | Result |
|---|---|
| Every JPY pair, 2014–26, post-fix hour (gross, bps) | USDJPY +2.10, EURJPY +2.02, GBPJPY +1.80, AUDJPY +1.27, CADJPY +1.81, CHFJPY +2.20, NZDJPY +1.36 (t 2.1–5.8). On other days, +0.2 to +1.0 |
| Placebo: non-JPY pairs over the same hour on Gotobi days | EURUSD +0.01, GBPUSD +0.22, AUDUSD +0.78, USDCHF +0.15, USDCAD −0.26 (all n.s.). **It is a yen effect** |
| Second feed: Yahoo USDJPY=X | 5-min bars (54 days): correlation 0.9994 with HistData over the window. 60-min bars (720 days): 0.9994, and the same Gotobi mean (0.80 vs 0.78 bps, 10:00–11:00) |
| Years positive (post-fix, USDJPY) | 22 of 24 (2015 −1.0; partial 2026 −0.9). EURJPY 13 of 13 since 2014 |
| Outliers | Trimming the top and bottom 1% leaves +2.11 bps; median +1.77. Worst trades are real events: 2011-03-18 G7 intervention −238 bps, 2010-09-15 BoJ intervention −121, 2015-08-25 China devaluation −84 |
| Entry delay (exit 10:55) | 09:55 bar open +2.17; **09:56 +1.31; 09:57 +1.14; 10:00 +0.73**. About 40% of the edge is in the first minute after the fix |
| Exit time (entry 09:55) | 10:00 +1.38 (t 9.0), 10:25 +2.17, 10:55 +2.11, 11:30 +2.86 (t 5.8), 12:00 +2.67, 15:00 +3.33 (t 3.5) |
| Day type | Month-end +3.71 (t 4.0, n 152); other Gotobi days +1.81 (t 4.0). Tuesdays are weak in both pairs (+0.2 / +0.1, n ≈ 140) |
| Cost sensitivity (net, post-fix only / pre-fix + post-fix per day) | 0.5 bp: +1.61 / +2.72 · 0.7: +1.41 / +2.32 · **1.0: +1.11 / +1.72** · 1.5: +0.61 / +0.72 · 2.0: +0.11 / −0.28 |
| Correlation with the other books | REV 0.02, US100 momentum −0.04 |

## Prop results (post hoc, [results/round19_gt_prop.json](../../research/validation/results/round19_gt_prop.json))

**Scope:** USDJPY, 2014–2026, 1 bp per trade, exact minute path, 3% daily guard (2% on 1-Step). About 76 trades a year, σ 12 bps per trade, annual Sharpe 0.83.

| Size (notional ÷ equity) | Return / vol, %/yr | Worst trade | FTMO 2-Step: pass (zero edge) | EV per account-month | Median days to pass | FTMO 1-Step: pass (zero edge) |
|---|---|---|---|---|---|---|
| 5× | 4.4 / 5.1 | −4.3% | 90% (27%) | $93 | 1,060 | 83% (31%) |
| 10× | 8.8 / 10.3 | −8.6% | 67% (26%) | $297 | 387 | 63% (29%) |
| 20× | 17.7 / 20.5 | −17.3% | 50% (24%) | $779 | 143 | 50% (27%) |
| 30× | 26.5 / 30.8 | −25.9% | 40% (20%) | $1,159 | 85 | 44% (24%) |

- **The whole JPY basket doesn't pay** at 2 bps per cross (net −0.02 bps). Add a cross only where its round-trip cost is ≤ 1 bp.
- **Separate account:** adding GT to the REV + US100 book at 1× each didn't raise the pass rate, because that book is already too large for one account.
- **The worst trade exceeds the 5% daily limit at 10× and above.** The EA guard, or a stop, must cap it (see the build).

## SQX build spec

| Item | Setting |
|---|---|
| Symbol, chart | USDJPY, M1. Optional: EURJPY where the round trip is ≤ 1 bp |
| Days | Gotobi days: the 5th, 10th, 15th, 20th, 25th, 30th and the month's last Tokyo business day. A date that is a Saturday, Sunday, Japanese national holiday or bank holiday (Dec 31, Jan 1–3) moves to the preceding business day. **Needs a custom block with a Japanese holiday list** (the research list: python `holidays` Japan plus the bank holidays). Skip Japanese holidays: there is no fix |
| Entry | **Sell at market at 09:55:00 JST** (the open of the 09:55 M1 bar). JST = UTC + 9 all year. FTMO server time is UTC + 2 / + 3, so it is 02:55 in the northern winter and 03:55 in summer. A 1-minute delay costs ~40% of the edge |
| Exit | Time exit at 10:55 JST (pre-registered). 11:30 JST was better post hoc (+2.86 bps); round 20 re-tests the choice on unseen data |
| Stop | A disaster stop only (the tested rule had none). Size so that a 90-bp move (the 2015-08-25 trade) stays inside the daily loss limit |
| Size | Fixed notional, 10–20× equity on an FTMO 2-Step or 1-Step account of its own |
| Costs | **Round trip ≤ 1 bp** (raw spread + commission). At 1.5 bps the edge halves; at 2 bps it's gone |
| Add-on (costs ≤ 0.7 bp) | Long 09:00 → 09:55 JST on the same days: net +2.3 bps per day with the post-fix leg |

## Known risks

- **Small per trade:** +1.1 bps net. Costs, slippage at the fix and latency decide whether it pays.
- **Intervention days:** the Ministry of Finance can intervene in Tokyo hours. The 2011 yen-selling intervention cost 238 bps on this short. Recent interventions bought yen, which helps the short.
- **The flow could fade:** fixing practice, importer hedging or bank pre-hedging may change. The effect was smaller in 2014–19 (+1.49 gross) than in 2003–13 (+3.00), then rose again in 2020–26.
- **Tuesdays are weak** in both pairs (post hoc; don't filter on it).

## Falsification tests for the build

1. On the broker's data 2014 →, the post-fix hour on Gotobi days has a gross mean of ≥ 1.5 bps, and the non-Gotobi mean is lower.
2. The same window on EURUSD or GBPUSD shows nothing (a placebo).
3. Entering at 10:00 instead of 09:55 loses more than a third of the gross mean (a mechanism check: the fix minute matters).
