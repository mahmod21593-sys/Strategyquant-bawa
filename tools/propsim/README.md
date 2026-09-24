# propsim — prop-firm challenge simulator

Replays StrategyQuant X trade lists (or any trade-list CSV) against prop-firm rules. It estimates how
often a strategy **or a portfolio of strategies** passes, how long passing takes, why it fails, and the
expected value of an attempt, for a range of position sizes.

It complements SQX's own **Prop Monte Carlo** (Build 144+), which shuffles trade order. propsim adds:

- **Historical rolling starts:** a challenge started on every day of your data, replaying the real sequence.
- **Block bootstrap of whole days** (Politis & Romano, 1994): keeps streaks of bad days together.
- **Multi-phase challenges**, **static / end-of-day trailing / intraday trailing** drawdowns (with lock level), **daily loss** on initial or day-start balance, **minimum trading days**, **time limits**, **consistency rules**.
- **Several strategies combined**, with per-strategy weights and a correlation report.
- A **position-size scan** and a **funded-stage** payout simulation with expected value per attempt.
- An optional **EA daily equity guard**, to measure what a "flatten at −3% today" rule is worth.

Only the Python 3.10+ standard library is needed.

## Quick start

```bash
cd tools/propsim
python -m propsim --trades my_strategy.csv --rules two_step_10_5 --ref-balance 100000 --scan 0.5:3:0.25
```

- `--trades`: one or more CSV trade lists. Append `@weight` to scale one strategy, e.g. `orb.csv@0.5`.
- `--rules`: a preset name from `presets/` or a path to your own JSON.
- `--ref-balance`: the account balance your backtest P&L refers to. **Backtest with fixed position sizing** so P&L scales linearly.
- `--scan start:stop:step`: position-size multipliers vs the backtest (1.0 = as backtested).

Useful options:

| Option | Meaning |
|---|---|
| `--from / --to YYYY-MM-DD` | Restrict to your **out-of-sample** period. Don't evaluate on in-sample data |
| `--method historical\|bootstrap\|both` | Path generation (default both) |
| `--paths N`, `--block D` | Bootstrap paths per scale (default 2000) and mean block length in days (default 5) |
| `--daily-guard 0.03` | EA equity guard: flatten for the day at a 3% loss (plus `--guard-slippage`, default 0.25%) |
| `--day-start-hour H` | Hour, in the CSV's time zone, when the firm's trading day starts |
| `--payout-reliability 0.7` | Haircut on payouts for counterparty risk |
| `--max-median-days 90` | Only recommend sizes that pass within this median number of calendar days |
| `--json out.json` | Save everything |
| `--col-open/--col-close/--col-pnl/--col-mae/--col-mfe`, `--date-format` | If your CSV headers or dates aren't auto-detected |

## Reading the output

| Column | Meaning |
|---|---|
| `daily sd` | Daily volatility of the combined P&L at this size (fraction of initial balance) |
| `analytic` | Closed-form pass probability for all phases (Brownian motion with drift). It assumes a **static** max loss, no daily limit and no minimum days, so it is a sanity check, and it reads too high for trailing-drawdown rules |
| `P(ph1)`, `P(all)` | Simulated probability of passing phase 1 and all phases |
| `med d`, `p75 d` | Median and 75th-percentile calendar days to pass all phases (passing paths only) |
| `dailyL`, `maxL`, `time` | Share of challenges failed by the daily limit, max loss, or time limit |
| `P(paid)`, `payout`, `EV/try` | Funded stage: share of funded paths with at least one payout, mean payout, and expected value per attempt including the fee |
| `(n incomplete)` | Paths where the data ran out before the outcome was decided (historical method near the end of the data). Excluded from the probabilities |

## Input format

Delimiters (`,` `;` tab `|`) and common headers are detected automatically:

| Role | Recognised headers (case and punctuation ignored) |
|---|---|
| Open time | Open time, Open date, Entry time, Entry date |
| Close time | Close time, Close date, Exit time, Exit date |
| P&L (money) | Profit/Loss, P/L, PnL, Profit, Net profit |
| MAE (optional) | MAE, Max open loss |
| MFE (optional) | MFE, Max open profit |

**Include MAE if you can.** Daily-loss rules usually count floating losses, and without MAE the
simulator only sees losses at trade close.

## Rules file

```json
{
  "name": "My firm 2-step",
  "initial_balance": 100000,
  "phases": [
    {"name": "Phase 1", "profit_target": 0.10, "min_trading_days": 4, "max_days": null},
    {"name": "Phase 2", "profit_target": 0.05, "min_trading_days": 4}
  ],
  "daily_loss": 0.05,
  "daily_loss_basis": "initial",
  "max_loss": 0.10,
  "max_loss_type": "static",
  "trailing_lock": null,
  "consistency": null,
  "after_target": "pause",
  "fee": 500,
  "fee_refund_on_first_payout": true,
  "funded": {"horizon_days": 365, "payout_every_days": 14, "profit_split": 0.8, "min_payout_profit": 0.0}
}
```

| Field | Values |
|---|---|
| `daily_loss_basis` | `initial` (limit = % of initial balance) or `day_start` (% of that day's starting balance). Loss is measured from the day's starting balance |
| `max_loss_type` | `static`, `trailing_eod` (floor follows the highest end-of-day balance), `trailing_intraday` (floor follows the highest intraday equity, including open profit) |
| `trailing_lock` | Floor stops trailing at `1 + lock` × initial (e.g. `0.0` = stops at the initial balance) |
| `consistency` | Best day must be ≤ this share of the phase's profit before the phase passes |
| `after_target` | `pause`: stop the strategy once the target is hit and just complete minimum days; `continue`: keep trading until every condition is met |

The presets in `presets/` are **archetypes with placeholder fees**, not any specific firm's rules.
Copy one and edit it to your firm's current terms.

## Model and limitations

- **P&L is attributed to the day a trade closes.** Within a day, the floating low is estimated conservatively: just before each trade closes, every other trade that closes that day and is already open is assumed to be at its MAE. For positions held overnight, floating losses on earlier days are not seen, so prefer intraday strategies or check them with the historical method.
- **Intraday trailing drawdowns** assume the day's high came before its low, which is the conservative ordering.
- **Touching a limit counts as a breach.**
- **Fixed position sizing** relative to the initial balance, with no compounding inside a challenge.
- **Funded stage:** a payout is requested every `payout_every_days` if profit exceeds `min_payout_profit`; the trader's share is paid and the balance resets to the initial level.
- **Results are only as good as the trade lists.** Use out-of-sample trades with realistic costs, and treat the output as an upper bound.

## Tests

```bash
cd tools/propsim
python -m unittest discover -s tests -t tests
```

The tests cover each rule type with hand-checkable cases, CSV parsing (SQX-style semicolon files,
decimal commas), daily aggregation with overlapping trades, an end-to-end CLI run, and convergence of
the simulator to the closed-form first-passage probability.
