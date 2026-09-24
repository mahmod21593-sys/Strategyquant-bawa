# References

Grouped by topic. **Used for** says where each source supports this plan. Peer-reviewed journal
articles are marked **(PR)**. Working papers, practitioner papers and books are marked as such, and
the plan grades them lower.

---

## Research methodology, data mining and overfitting

| Reference | Used for |
|---|---|
| Arnott, R., Harvey, C. R., & Markowitz, H. (2019). A backtesting protocol in the era of machine learning. *Journal of Financial Data Science*, 1(1), 64–74. **(PR)** | Research-protocol checklist (doc 01) |
| Aronson, D. (2006). *Evidence-Based Technical Analysis.* Wiley. **(Book)** | Data-mining bias; random-entry benchmarks |
| Bailey, D. H., Borwein, J., López de Prado, M., & Zhu, Q. J. (2014). Pseudo-mathematics and financial charlatanism: The effects of backtest overfitting on out-of-sample performance. *Notices of the AMS*, 61(5), 458–471. **(PR)** | Why high backtest Sharpe is expected under heavy search |
| Bailey, D. H., Borwein, J., López de Prado, M., & Zhu, Q. J. (2017). The probability of backtest overfitting. *Journal of Computational Finance*, 20(4), 39–69. **(PR)** | PBO / CSCV (doc 03 §6.2) |
| Bailey, D. H., & López de Prado, M. (2014). The deflated Sharpe ratio: Correcting for selection bias, backtest overfitting and non-normality. *Journal of Portfolio Management*, 40(5), 94–107. **(PR)** | Expected-max-Sharpe table; DSR (doc 01 §1, doc 03 §6.1) |
| Bajgrowicz, P., & Scaillet, O. (2012). Technical trading revisited: False discoveries, persistence tests, and transaction costs. *Journal of Financial Economics*, 106(3), 473–491. **(PR)** | DJIA technical rules fail after FDR control and costs |
| Chordia, T., Goyal, A., & Saretto, A. (2020). Anomalies and false rejections. *Review of Financial Studies*, 33(5), 2134–2179. **(PR)** | Multiple-testing context |
| Hansen, P. R. (2005). A test for superior predictive ability. *Journal of Business & Economic Statistics*, 23(4), 365–380. **(PR)** | SPA test (doc 03 §6.3) |
| Harvey, C. R., & Liu, Y. (2015). Backtesting. *Journal of Portfolio Management*, 42(1), 13–28. **(PR)** | Sharpe haircuts for multiple testing |
| Harvey, C. R., Liu, Y., & Zhu, H. (2016). …and the cross-section of expected returns. *Review of Financial Studies*, 29(1), 5–68. **(PR)** | t ≥ 3 hurdle for new discoveries |
| Lo, A. W. (2002). The statistics of Sharpe ratios. *Financial Analysts Journal*, 58(4), 36–52. **(PR)** | Sharpe standard errors; minimum trade counts |
| Lo, A. W., & MacKinlay, A. C. (1988). Stock market prices do not follow random walks: Evidence from a simple specification test. *Review of Financial Studies*, 1(1), 41–66. **(PR)** | Variance-ratio test (Phase 1) |
| Masters, T. (2020). *Permutation and Randomization Tests for Trading System Development: Algorithms in C++.* Independently published. **(Book)** | Permutation / noise-calibration tests (doc 03 §5) |
| McLean, R. D., & Pontiff, J. (2016). Does academic research destroy stock return predictability? *Journal of Finance*, 71(1), 5–32. **(PR)** | ~26% OOS and ~58% post-publication decay; haircut rule |
| Pardo, R. (2008). *The Evaluation and Optimization of Trading Strategies* (2nd ed.). Wiley. **(Book)** | Walk-forward analysis; parameter plateaus |
| Politis, D. N., & Romano, J. P. (1994). The stationary bootstrap. *Journal of the American Statistical Association*, 89(428), 1303–1313. **(PR)** | Synthetic null series (doc 03 §5) |
| Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. *Econometrica*, 73(4), 1237–1282. **(PR)** | Multiple-testing alternative |
| Sullivan, R., Timmermann, A., & White, H. (1999). Data-snooping, technical trading rule performance, and the bootstrap. *Journal of Finance*, 54(5), 1647–1691. **(PR)** | Technical-rule profits vs data snooping |
| Walton, D. (2014). Know your system! Turning data mining from bias to benefit through System Parameter Permutation. NAAIM Wagner Award (1st place). [SSRN 2423187](https://dx.doi.org/10.2139/ssrn.2423187) **(Practitioner)** | SPP median as the realistic expectation (doc 03 Stage 8) |
| White, H. (2000). A reality check for data snooping. *Econometrica*, 68(5), 1097–1126. **(PR)** | Reality Check test |

## Market efficiency, adaptation and edge decay

| Reference | Used for |
|---|---|
| Kurov, A., Wolfe, M. H., & Gilbert, T. (2021). The disappearing pre-FOMC announcement drift. *Finance Research Letters*, 40, 101781. **(PR)** | Decay example (Grade D control) |
| Lo, A. W. (2004). The adaptive markets hypothesis. *Journal of Portfolio Management*, 30(5), 15–29. **(PR)** | Why edges wax and wane; monitoring |
| Lucca, D. O., & Moench, E. (2015). The pre-FOMC announcement drift. *Journal of Finance*, 70(1), 329–371. **(PR)** | Original pre-FOMC drift |
| Neely, C. J., Weller, P. A., & Ulrich, J. M. (2009). The adaptive markets hypothesis: Evidence from the foreign exchange market. *Journal of Financial and Quantitative Analysis*, 44(2), 467–488. **(PR)** | FX technical-rule decay |
| Olson, D. (2004). Have trading rule profits in the currency markets declined over time? *Journal of Banking & Finance*, 28(1), 85–105. **(PR)** | FX technical-rule decay |
| Schulmeister, S. (2009). Profitability of technical stock trading: Has it moved from daily to intraday data? *Review of Financial Economics*, 18(4), 190–201. **(PR)** | Edge migration to 30-minute data |

## F1 — Trend following / time-series momentum

| Reference | Used for |
|---|---|
| Hong, H., & Stein, J. C. (1999). A unified theory of underreaction, momentum trading, and overreaction in asset markets. *Journal of Finance*, 54(6), 2143–2184. **(PR)** | Behavioural mechanism |
| Huang, D., Li, J., Wang, L., & Zhou, G. (2020). Time series momentum: Is it there? *Journal of Financial Economics*, 135(3), 774–794. [doi:10.1016/j.jfineco.2019.08.004](https://doi.org/10.1016/j.jfineco.2019.08.004) **(PR)** | Contrary evidence: weak per-asset predictability |
| Hurst, B., Ooi, Y. H., & Pedersen, L. H. (2017). A century of evidence on trend-following investing. *Journal of Portfolio Management*, 44(1), 15–29. **(PR)** | Long-run and crisis evidence |
| Kim, A. Y., Tse, Y., & Wald, J. K. (2016). Time series momentum and volatility scaling. *Journal of Financial Markets*, 30, 103–124. [doi:10.1016/j.finmar.2016.05.003](https://doi.org/10.1016/j.finmar.2016.05.003) **(PR)** | Contrary evidence: vol scaling drives alpha |
| Lempérière, Y., Deremble, C., Seager, P., Potters, M., & Bouchaud, J.-P. (2014). Two centuries of trend following. *Journal of Investment Strategies*, 3(3), 41–61. **(PR)** | Long-run, multi-asset evidence |
| Levine, A., & Pedersen, L. H. (2016). Which trend is your friend? *Financial Analysts Journal*, 72(3), 51–66. **(PR)** | MA crossovers ≈ TSMOM; lookback matters most |
| Liu, Y., & Tsyvinski, A. (2021). Risks and returns of cryptocurrency. *Review of Financial Studies*, 34(6), 2689–2727. **(PR)** | Crypto time-series momentum (TF-04) |
| Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228–250. **(PR)** | Core TSMOM evidence |
| Szakmary, A. C., Shen, Q., & Sharma, S. C. (2010). Trend-following trading strategies in commodity futures: A re-examination. *Journal of Banking & Finance*, 34(2), 409–426. **(PR)** | MA and channel rules in commodities |

## F2 — Short-term mean reversion

| Reference | Used for |
|---|---|
| Baltussen, G., van Bekkum, S., & Da, Z. (2019). Indexing and stock market serial dependence around the world. *Journal of Financial Economics*, 132(1), 26–48. **(PR)** | Negative index autocorrelation since the 2000s |
| Connors, L., & Alvarez, C. (2009). *Short Term Trading Strategies That Work.* TradingMarkets. **(Book, practitioner)** | RSI(2) dip-buying templates |
| Kaminski, K. M., & Lo, A. W. (2014). When do stop-loss rules stop losses? *Journal of Financial Markets*, 18, 234–254. **(PR)** | Stops add value with momentum, subtract under mean reversion (exit design, F1 vs F2) |
| Nagel, S. (2012). Evaporating liquidity. *Review of Financial Studies*, 25(7), 2005–2039. **(PR)** | Reversal = liquidity provision; stronger when VIX is high (MR-03, IX-01) |
| Pagonidis, A. S. (2013). The IBS effect: Mean reversion in equity ETFs. NAAIM. [PDF](https://www.naaim.org/wp-content/uploads/2014/04/00V_Alexander_Pagonidis_The-IBS-Effect-Mean-Reversion-in-Equity-ETFs-1.pdf) **(Practitioner)** | IBS trigger |

## F3 — Intraday momentum and ORB

| Reference | Used for |
|---|---|
| Baltussen, G., Da, Z., Lammers, S., & Martens, M. (2021). Hedging demand and market intraday momentum. *Journal of Financial Economics*, 142(1), 377–403. [doi:10.1016/j.jfineco.2021.04.029](https://doi.org/10.1016/j.jfineco.2021.04.029) **(PR)** | 60+ futures; gamma-hedging mechanism; next-day reversal |
| Crabel, T. (1990). *Day Trading with Short Term Price Patterns and Opening Range Breakout.* Traders Press. **(Book, practitioner)** | ORB, NR4/NR7 |
| Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). Market intraday momentum. *Journal of Financial Economics*, 129(2), 394–414. **(PR)** | First half-hour predicts last half-hour |
| Holmberg, U., Lönnbark, C., & Lundström, C. (2013). Assessing the profitability of intraday opening range breakout strategies. *Finance Research Letters*, 10(1), 27–33. **(PR)** | ORB on crude oil futures |
| Li, Z., Sakkas, A., & Urquhart, A. (2022). Intraday time series momentum: Global evidence and links to market characteristics. *Journal of Financial Markets*, 57, 100619. **(PR)** | 16 markets; stronger in low liquidity and high volatility |
| Zarattini, C., & Aziz, A. (2023). Can day trading really be profitable? Evidence of sustainable long-term profits from opening range breakout (ORB) day trading strategy vs. benchmark in the US stock market. [SSRN 4416622](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622) **(Working paper)** | 5-minute ORB on QQQ |
| Zarattini, C., Aziz, A., & Barbon, A. (2024). Beat the market: An effective intraday momentum strategy for S&P500 ETF (SPY). [SSRN 4824172](https://ssrn.com/abstract=4824172) **(Working paper)** | Noise-area intraday momentum (IM-04) |

## F4 — Volatility

| Reference | Used for |
|---|---|
| Andersen, T. G., & Bollerslev, T. (1997). Intraday periodicity and volatility persistence in financial markets. *Journal of Empirical Finance*, 4(2–3), 115–158. **(PR)** | Session volatility patterns |
| Engle, R. F., & Patton, A. J. (2001). What good is a volatility model? *Quantitative Finance*, 1(2), 237–245. **(PR)** | Volatility clustering and mean reversion |

## F5 — Calendar and flows

| Reference | Used for |
|---|---|
| Ariel, R. A. (1987). A monthly effect in stock returns. *Journal of Financial Economics*, 18(1), 161–174. **(PR)** | Turn of month |
| Ariel, R. A. (1990). High stock returns before holidays: Existence and evidence on possible causes. *Journal of Finance*, 45(5), 1611–1626. **(PR)** | Pre-holiday effect |
| Bouman, S., & Jacobsen, B. (2002). The Halloween indicator, "Sell in May and go away": Another puzzle. *American Economic Review*, 92(5), 1618–1635. **(PR)** | Seasonal overlay (CF-04) |
| Boyarchenko, N., Larsen, L. C., & Whelan, P. (2023). The overnight drift. *Review of Financial Studies*, 36(9), 3502–3547. **(PR)** | Overnight drift (now a decay control) |
| Federal Reserve Bank of New York (2026, July). The disappearing overnight drift. *Liberty Street Economics.* [Link](https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/) **(Blog, central bank)** | Overnight drift ≈ 0 since 2021 |
| Harvey, C. R., Mazzoleni, M. G., & Melone, A. (2025). The unintended consequences of rebalancing. NBER Working Paper 33554. [Link](https://www.nber.org/papers/w33554) **(Working paper)** | Month-end rebalancing flows (CF-02) |
| Lakonishok, J., & Smidt, S. (1988). Are seasonal anomalies real? A ninety-year perspective. *Review of Financial Studies*, 1(4), 403–425. **(PR)** | Turn of month; holidays |
| McConnell, J. J., & Xu, W. (2008). Equity returns at the turn of the month. *Financial Analysts Journal*, 64(2), 49–64. **(PR)** | 1926–2005; 31 of 35 countries |

## F6 — FX session and fix flows

| Reference | Used for |
|---|---|
| Breedon, F., & Ranaldo, A. (2013). Intraday patterns in FX returns and order flow. *Journal of Money, Credit and Banking*, 45(5), 953–965. **(PR)** | Order-flow explanation of time-of-day patterns |
| Evans, M. D. D. (2018). Forex trading and the WMR fix. *Journal of Banking & Finance*, 87, 233–247. **(PR)** | Fix dynamics |
| Melvin, M., & Prins, J. (2015). Equity hedging and exchange rates at the London 4 p.m. fix. *Journal of Financial Markets*, 22, 50–72. **(PR)** | Month-end fix hedging flow (FX-02, FX-03) |
| Ranaldo, A. (2009). Segmentation and time-of-day patterns in foreign exchange markets. *Journal of Banking & Finance*, 33(12), 2199–2206. [doi:10.1016/j.jbankfin.2009.05.019](https://doi.org/10.1016/j.jbankfin.2009.05.019) **(PR)** | Domestic-hours depreciation pattern (FX-01) |

## F7 — Carry

| Reference | Used for |
|---|---|
| Brunnermeier, M. K., Nagel, S., & Pedersen, L. H. (2008). Carry trades and currency crashes. *NBER Macroeconomics Annual*, 23, 313–347. **(PR)** | Crash risk |
| Burnside, C., Eichenbaum, M., & Rebelo, S. (2011). Carry trade and momentum in currency markets. *Annual Review of Financial Economics*, 3, 511–535. **(PR)** | Carry and momentum payoffs |
| Koijen, R. S. J., Moskowitz, T. J., Pedersen, L. H., & Vrugt, E. B. (2018). Carry. *Journal of Financial Economics*, 127(2), 197–225. **(PR)** | Carry across asset classes |
| Lustig, H., Roussanov, N., & Verdelhan, A. (2011). Common risk factors in currency markets. *Review of Financial Studies*, 24(11), 3731–3777. **(PR)** | Carry as a risk factor |
| Menkhoff, L., Sarno, L., Schmeling, M., & Schrimpf, A. (2012a). Carry trades and global foreign exchange volatility. *Journal of Finance*, 67(2), 681–718. **(PR)** | Carry losses when FX volatility rises (CA-02) |
| Menkhoff, L., Sarno, L., Schmeling, M., & Schrimpf, A. (2012b). Currency momentum strategies. *Journal of Financial Economics*, 106(3), 660–684. **(PR)** | Currency momentum |

## F8 — Intermarket

| Reference | Used for |
|---|---|
| Bork, L., Rovira Kaltwasser, P., & Sercu, P. (2014). Do exchange rates really help forecasting commodity prices? Working paper; published as: Exchange rates do not predict commodity prices. *Critical Finance Review*, 14(4). [SSRN 2473624](http://ssrn.com/abstract=2473624) **(PR)** | Replication finds no robust out-of-sample predictability, so IX-02 is downgraded to D |
| Chen, Y.-C., Rogoff, K. S., & Rossi, B. (2010). Can exchange rates forecast commodity prices? *Quarterly Journal of Economics*, 125(3), 1145–1194. **(PR)** | Commodity currencies lead commodity prices (IX-02). The finding is contested; see Bork et al. above |

## Portfolio construction and sizing

| Reference | Used for |
|---|---|
| Carver, R. (2015). *Systematic Trading.* Harriman House. **(Book)** | Diversification multiplier; risk budgeting |
| Davey, K. (2014). *Building Winning Algorithmic Trading Systems.* Wiley. **(Book)** | Incubation; live monitoring |
| DeMiguel, V., Garlappi, L., & Uppal, R. (2009). Optimal versus naive diversification: How inefficient is the 1/N portfolio strategy? *Review of Financial Studies*, 22(5), 1915–1953. **(PR)** | Equal-risk weighting over optimised weights |
| Grinold, R. C., & Kahn, R. N. (2000). *Active Portfolio Management* (2nd ed.). McGraw-Hill. **(Book)** | Breadth and correlation |
| Harvey, C. R., Hoyle, E., Korgaonkar, R., Rattray, S., Sargaison, M., & Van Hemert, O. (2018). The impact of volatility targeting. *Journal of Portfolio Management*, 45(1), 14–33. **(PR)** | Volatility-scaled sizing |
| MacLean, L. C., Thorp, E. O., & Ziemba, W. T. (Eds.) (2011). *The Kelly Capital Growth Investment Criterion.* World Scientific. **(Book)** | Fractional-Kelly caution |
| Moreira, A., & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611–1644. **(PR)** | Volatility-managed exposure |

## StrategyQuant X documentation

- Settings — What to build: https://strategyquant.com/doc/strategyquant/what-to-build/
- Settings — Data (multi-TF / multi-symbol): https://strategyquant.com/doc/strategyquant/data/
- Settings — Trading options: https://strategyquant.com/doc/strategyquant/trading-options/
- Monte Carlo retest methods: https://strategyquant.com/doc/strategyquant/monte-carlo-retest-methods/
- Monte Carlo trades manipulation: https://strategyquant.com/doc/strategyquant/monte-carlo-trades-manipulation/
- Optimization profile and System Parameter Permutation: https://strategyquant.com/doc/strategyquant/optimization-profile-system-parameter-permutation-strategyquant/
- Correlation filter (custom analysis): https://strategyquant.com/codebase/correlation-filter-custom-analysis/
- QuantAnalyzer Portfolio Master: https://strategyquant.com/quantanalyzer/portfolio-master/
