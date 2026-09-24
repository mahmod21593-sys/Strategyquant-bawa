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
    min_payout_profit: float = 0.0  # minimum profit (fraction) to request a payout; balance resets to initial after each payout


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
    after_target: str = "pause"
    fee: float = 0.0
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
        parts.append(f"  Consistency: best day <= {rules.consistency:.0%} of phase profit")
    if rules.funded:
        f = rules.funded
        parts.append(
            f"  Funded: {f.horizon_days} days, payout every {f.payout_every_days} days, split {f.profit_split:.0%}"
        )
    parts.append(f"  Fee: {rules.fee:,.0f}{' (refunded with first payout)' if rules.fee_refund_on_first_payout else ''}")
    return "\n".join(parts)
