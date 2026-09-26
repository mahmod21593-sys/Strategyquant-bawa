"""Prop-firm rule definitions.

All money amounts are expressed as fractions of the account's initial balance
(0.05 == 5%), so the same rules work for any account size.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

MAX_LOSS_TYPES = ("static", "trailing_eod", "trailing_intraday")
DAILY_LOSS_BASES = ("initial", "day_start")
AFTER_TARGET_MODES = ("pause", "continue")
CONSISTENCY_BASES = ("net", "positive_days")
PAYOUT_MODES = ("reset", "partial")


@dataclass
class Phase:
    name: str
    profit_target: float
    min_trading_days: int = 0
    max_days: Optional[int] = None  # calendar days; None = unlimited


@dataclass
class Funded:
    horizon_days: int = 365  # calendar days simulated after the last phase
    payout_every_days: int = 14  # calendar days between payout requests
    profit_split: float = 0.8
    min_payout_profit: float = 0.0  # minimum profit (fraction) to request a payout
    # "reset": withdraw all profit and reset the account to its initial balance (FTMO-style).
    # "partial": withdraw payout_fraction of the profit, capped at payout_cap; the rest stays in the account (Topstep XFA-style).
    payout_mode: str = "reset"
    payout_fraction: float = 1.0
    payout_cap: Optional[float] = None  # fraction of initial balance per payout
    winning_days_required: int = 0  # days with P&L >= winning_day_min since the last payout
    winning_day_min: float = 0.0
    consistency: Optional[float] = None  # payout gate: best day since the last payout <= consistency x basis
    consistency_basis: str = "net"
    lock_floor_after_payout: bool = False  # after the first payout the loss floor sits at the initial balance for good

    def __post_init__(self) -> None:
        if self.payout_mode not in PAYOUT_MODES:
            raise ValueError(f"payout_mode must be one of {PAYOUT_MODES}")
        if self.consistency_basis not in CONSISTENCY_BASES:
            raise ValueError(f"consistency_basis must be one of {CONSISTENCY_BASES}")
        if self.payout_mode == "reset" and (self.payout_cap is not None or self.payout_fraction != 1.0):
            raise ValueError("payout_cap and payout_fraction apply to payout_mode 'partial' only")


@dataclass
class Rules:
    name: str
    initial_balance: float
    phases: list[Phase]
    max_loss: float
    max_loss_type: str = "static"
    trailing_lock: Optional[float] = None  # trailing floor stops at 1 + lock (0.0 = initial balance)
    daily_loss: Optional[float] = None
    daily_loss_basis: str = "initial"
    consistency: Optional[float] = None  # max share of phase profit from the best day
    consistency_basis: str = "net"  # "net": phase profit; "positive_days": sum of the phase's winning days (FTMO Best Day Rule)
    after_target: str = "pause"
    fee: float = 0.0
    fee_per_30_days: float = 0.0  # subscription: charged for every started 30 calendar days of the challenge
    fee_on_pass: float = 0.0  # activation fee paid when the challenge is passed
    fee_refund_on_first_payout: bool = False
    funded: Optional[Funded] = None
    notes: str = ""

    def __post_init__(self) -> None:
        if self.max_loss_type not in MAX_LOSS_TYPES:
            raise ValueError(f"max_loss_type must be one of {MAX_LOSS_TYPES}")
        if self.daily_loss_basis not in DAILY_LOSS_BASES:
            raise ValueError(f"daily_loss_basis must be one of {DAILY_LOSS_BASES}")
        if self.after_target not in AFTER_TARGET_MODES:
            raise ValueError(f"after_target must be one of {AFTER_TARGET_MODES}")
        if not self.phases:
            raise ValueError("at least one phase is required")
        if self.max_loss <= 0:
            raise ValueError("max_loss must be positive")
        if self.consistency_basis not in CONSISTENCY_BASES:
            raise ValueError(f"consistency_basis must be one of {CONSISTENCY_BASES}")


def rules_from_dict(data: dict) -> Rules:
    data = {k: v for k, v in data.items() if not k.startswith("_")}
    phases = [Phase(**p) for p in data.pop("phases")]
    funded_data = data.pop("funded", None)
    funded = Funded(**funded_data) if funded_data else None
    return Rules(phases=phases, funded=funded, **data)


def load_rules(path: str | Path) -> Rules:
    with open(path, encoding="utf-8") as fh:
        return rules_from_dict(json.load(fh))


def describe(rules: Rules) -> str:
    parts = [f"{rules.name} (initial balance {rules.initial_balance:,.0f})"]
    for ph in rules.phases:
        limit = f", max {ph.max_days} days" if ph.max_days else ""
        parts.append(
            f"  {ph.name}: target {ph.profit_target:.1%}, min {ph.min_trading_days} trading days{limit}"
        )
    daily = (
        f"{rules.daily_loss:.1%} of {'initial' if rules.daily_loss_basis == 'initial' else 'day-start'} balance"
        if rules.daily_loss
        else "none"
    )
    lock = "" if rules.trailing_lock is None else f", floor locks at {1 + rules.trailing_lock:.1%}"
    parts.append(f"  Daily loss: {daily}")
    parts.append(f"  Max loss: {rules.max_loss:.1%} {rules.max_loss_type}{lock}")
    if rules.consistency:
        basis = "winning days' profit" if rules.consistency_basis == "positive_days" else "phase profit"
        parts.append(f"  Consistency: best day <= {rules.consistency:.0%} of {basis}")
    if rules.funded:
        f = rules.funded
        parts.append(
            f"  Funded: {f.horizon_days} days, payout every {f.payout_every_days} days, split {f.profit_split:.0%}"
        )
        if f.payout_mode == "partial":
            cap = "" if f.payout_cap is None else f", cap {f.payout_cap:.1%}"
            parts.append(f"  Payouts: {f.payout_fraction:.0%} of profit{cap}; the rest stays in the account")
        if f.winning_days_required:
            parts.append(f"  Payout gate: {f.winning_days_required} days >= {f.winning_day_min:.2%} since the last payout")
        if f.consistency:
            parts.append(f"  Payout gate: best day <= {f.consistency:.0%} ({f.consistency_basis})")
    fee = f"  Fee: {rules.fee:,.0f}{' (refunded with first payout)' if rules.fee_refund_on_first_payout else ''}"
    if rules.fee_per_30_days:
        fee += f" + {rules.fee_per_30_days:,.0f} per started 30 days"
    if rules.fee_on_pass:
        fee += f" + {rules.fee_on_pass:,.0f} on passing"
    parts.append(fee)
    return "\n".join(parts)
