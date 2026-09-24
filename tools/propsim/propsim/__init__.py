"""propsim: simulate prop-firm challenges on trade lists exported from StrategyQuant X."""

from .analytic import expected_days, multi_phase_probability, pass_probability
from .engine import Day, Outcome, run_challenge
from .rules import Funded, Phase, Rules, load_rules, rules_from_dict
from .sampling import historical_paths, stationary_bootstrap
from .trades import Trade, build_days, load_trades

__all__ = [
    "Day",
    "Funded",
    "Outcome",
    "Phase",
    "Rules",
    "Trade",
    "build_days",
    "expected_days",
    "historical_paths",
    "load_rules",
    "load_trades",
    "multi_phase_probability",
    "pass_probability",
    "rules_from_dict",
    "run_challenge",
    "stationary_bootstrap",
]
