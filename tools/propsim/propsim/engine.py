"""Day-by-day replay of a P&L path against prop-firm rules.

Model
-----
The account is tracked as a fraction of its initial balance (1.0 = start).
Each ``Day`` carries, at the strategy's reference sizing (scale 1.0):

* ``pnl``  - realised P&L of trades closed that day
* ``low``  - lowest running P&L inside the day, including floating losses (<= 0)
* ``high`` - highest running P&L inside the day, including floating profits (>= 0)

A position-size multiplier ``scale`` multiplies all three. Breach checks use
the intraday ``low``. For intraday-trailing drawdowns the day's ``high`` is
assumed to come *before* its ``low``, which is the conservative ordering.
Touching a limit counts as a breach.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date
from typing import Callable, Iterable, Iterator, Optional

from .rules import Rules

EPS = 1e-12


@dataclass(frozen=True)
class Day:
    date: date
    pnl: float = 0.0
    low: float = 0.0
    high: float = 0.0
    traded: bool = False
    n_trades: int = 0

    def normalised(self) -> "Day":
        """Guarantee low <= min(0, pnl) and high >= max(0, pnl)."""
        low = min(self.low, 0.0, self.pnl)
        high = max(self.high, 0.0, self.pnl)
        if low == self.low and high == self.high:
            return self
        return replace(self, low=low, high=high)


@dataclass
class Outcome:
    passed_phases: int = 0
    passed_all: bool = False
    fail_reason: Optional[str] = None  # daily_loss | max_loss | time_limit | incomplete
    phase_days: list[int] = field(default_factory=list)
    days_to_pass: Optional[int] = None  # calendar days from challenge start to passing all phases
    days_run: int = 0  # calendar days the challenge ran (to pass or to failure)
    funded_payouts: float = 0.0  # trader's share, fraction of initial balance
    funded_n_payouts: int = 0
    funded_breached: bool = False
    funded_days: int = 0
    funded_complete: bool = True
    value: float = 0.0  # money: payouts + refund - fee

    @property
    def decided(self) -> bool:
        return self.fail_reason != "incomplete"

    @property
    def complete(self) -> bool:
        return self.decided and self.funded_complete


class Account:
    """Equity, drawdown floor and phase counters for one account.

    ``daily_guard`` models an equity stop in the EA itself (not a firm rule): when the
    day's floating loss reaches ``daily_guard`` (fraction of initial balance), everything
    is closed at that level plus ``guard_slippage`` and the strategy stops for the day.
    """

    def __init__(
        self,
        rules: Rules,
        scale: float,
        daily_guard: Optional[float] = None,
        guard_slippage: float = 0.0,
        sizer: Optional[Callable[["Account"], float]] = None,
    ) -> None:
        self.rules = rules
        self.scale = scale
        self.daily_guard = daily_guard
        self.guard_slippage = guard_slippage
        self.sizer = sizer
        self.reset()

    def cushion(self) -> float:
        """Distance from equity to the loss floor that applies today (fraction of initial balance)."""
        return self.equity - self._capped(self.floor)

    def reset(self) -> None:
        r = self.rules
        self.equity = 1.0
        self.floor = 1.0 - r.max_loss
        self.peak_eod = 1.0
        self.peak_intraday = 1.0
        self.traded_days = 0
        self.best_day = 0.0
        self.lock_level = None if r.trailing_lock is None else 1.0 + r.trailing_lock

    def _capped(self, floor: float) -> float:
        return floor if self.lock_level is None else min(floor, self.lock_level)

    def step(self, day: Day) -> Optional[str]:
        """Apply one day. Returns a breach reason or None."""
        r = self.rules
        d = day.normalised()
        scale = self.sizer(self) if self.sizer is not None else self.scale
        low, high, pnl = scale * d.low, scale * d.high, scale * d.pnl
        if self.daily_guard is not None and low <= -self.daily_guard:
            low = pnl = -(self.daily_guard + self.guard_slippage)
        e0 = self.equity
        e_low = e0 + low
        e_high = e0 + high
        e_end = e0 + pnl

        if r.daily_loss:
            basis = 1.0 if r.daily_loss_basis == "initial" else e0
            if e_low <= e0 - r.daily_loss * basis + EPS:
                return "daily_loss"

        if r.max_loss_type == "trailing_intraday":
            peak = max(self.peak_intraday, e_high)
            floor_today = self._capped(max(self.floor, peak - r.max_loss))
        else:
            floor_today = self.floor
        if e_low <= floor_today + EPS:
            return "max_loss"

        self.equity = e_end
        if d.traded:
            self.traded_days += 1
        self.best_day = max(self.best_day, pnl)

        if r.max_loss_type == "trailing_eod":
            self.peak_eod = max(self.peak_eod, e_end)
            self.floor = self._capped(max(self.floor, self.peak_eod - r.max_loss))
        elif r.max_loss_type == "trailing_intraday":
            self.peak_intraday = max(self.peak_intraday, e_high, e_end)
            self.floor = self._capped(max(self.floor, self.peak_intraday - r.max_loss))
        return None

    def target_reached(self, target: float) -> bool:
        profit = self.equity - 1.0
        if profit < target - EPS:
            return False
        c = self.rules.consistency
        return c is None or self.best_day <= c * profit + EPS


def run_challenge(
    days: Iterable[Day],
    rules: Rules,
    scale: float = 1.0,
    payout_reliability: float = 1.0,
    daily_guard: Optional[float] = None,
    guard_slippage: float = 0.0,
    sizer: Optional[Callable[["Account"], float]] = None,
    funded_sizer: Optional[Callable[["Account"], float]] = None,
    funded_scale: Optional[float] = None,
) -> Outcome:
    """Replay ``days`` through every phase and (optionally) the funded stage.

    ``sizer`` (optional) returns the exposure multiple for the next day from the account state, e.g. a
    CPPI rule ``lambda a: min(2.0, 20 * a.cushion())``. When given, it replaces the constant ``scale``.
    ``funded_sizer`` / ``funded_scale`` (optional) replace them in the funded stage only.
    """
    it: Iterator[Day] = iter(days)
    out = Outcome()
    challenge_start: Optional[date] = None
    last_date: Optional[date] = None

    def new_account() -> Account:
        return Account(rules, scale, daily_guard, guard_slippage, sizer)

    for phase in rules.phases:
        acct = new_account()
        phase_start: Optional[date] = None
        passed = False
        for day in it:
            if phase_start is None:
                phase_start = day.date
                if challenge_start is None:
                    challenge_start = day.date
            last_date = day.date
            breach = acct.step(day)
            if breach:
                out.fail_reason = breach
                break
            elapsed = (day.date - phase_start).days + 1
            if acct.target_reached(phase.profit_target):
                missing = phase.min_trading_days - acct.traded_days
                if missing <= 0:
                    passed = True
                elif rules.after_target == "pause":
                    # Stop running the strategy; place token trades on the next `missing` days.
                    for _ in range(missing):
                        nxt = next(it, None)
                        if nxt is None:
                            out.fail_reason = "incomplete"
                            break
                        last_date = nxt.date
                    if out.fail_reason:
                        break
                    elapsed = (last_date - phase_start).days + 1
                    passed = phase.max_days is None or elapsed <= phase.max_days
                    if not passed:
                        out.fail_reason = "time_limit"
                        break
                if passed:
                    out.phase_days.append(elapsed)
                    break
            if phase.max_days is not None and elapsed >= phase.max_days:
                out.fail_reason = "time_limit"
                break
        if not passed:
            if out.fail_reason is None:
                out.fail_reason = "incomplete"
            out.value = -rules.fee
            out.days_run = (last_date - challenge_start).days + 1 if challenge_start and last_date else 0
            return out
        out.passed_phases += 1

    out.passed_all = True
    out.days_to_pass = (last_date - challenge_start).days + 1 if challenge_start and last_date else 0
    out.days_run = out.days_to_pass
    funded_acct = Account(rules, scale if funded_scale is None else funded_scale, daily_guard, guard_slippage,
                          funded_sizer if (funded_sizer is not None or funded_scale is not None) else sizer)
    _run_funded(it, rules, funded_acct, payout_reliability, out)
    return out


def _run_funded(it: Iterator[Day], rules: Rules, acct: Account, reliability: float, out: Outcome) -> None:
    f = rules.funded
    if f is None:
        out.value = -rules.fee
        return
    start: Optional[date] = None
    last_payout: Optional[date] = None
    out.funded_complete = False
    for day in it:
        if start is None:
            start = last_payout = day.date
        elapsed = (day.date - start).days + 1
        if elapsed > f.horizon_days:
            out.funded_complete = True
            break
        out.funded_days = elapsed
        if acct.step(day):
            out.funded_breached = True
            out.funded_complete = True
            break
        if (day.date - last_payout).days >= f.payout_every_days:
            profit = acct.equity - 1.0
            if profit > max(f.min_payout_profit, 0.0):
                out.funded_payouts += f.profit_split * profit
                out.funded_n_payouts += 1
                acct.reset()
            last_payout = day.date
    money = out.funded_payouts * rules.initial_balance * reliability
    refund = rules.fee if rules.fee_refund_on_first_payout and out.funded_n_payouts > 0 else 0.0
    out.value = money + refund - rules.fee
