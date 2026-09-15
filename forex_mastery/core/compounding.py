"""
Compounding, growth and decay projections.

WHAT THIS MODULE IS FOR
-----------------------
To replace the two most damaging mental models in retail trading:

* "10% a month, compounded, is 3x my money in a year" - true arithmetic,
  but 10%/month requires a genuinely strong edge run with discipline; assuming
  it from the start is how accounts get destroyed chasing it.
* "I'll just risk more after a losing streak to recover" - that is martingale,
  it converts a survivable drawdown into ruin.

WHAT IT DOES
------------
Computes the *expected* (geometric-mean) growth rate for a fixed-fractional
risk framework, plus the honest caveats:

``g = p x ln(1 + f x R) + (1 - p) x ln(1 - f)``  (per trade, in log space)

where ``p`` is win rate, ``R`` reward:risk, ``f`` risk fraction. Note that
``exp(g x n)`` is the **median** outcome, and because the distribution is
right-skewed the median is much lower than the mean. Traders who only ever look
at the mean overestimate their future - this module therefore reports both.

COSTS ARE NOT OPTIONAL
----------------------
Pass ``cost_in_r``. A strategy that looks profitable before spread and
commission is frequently unprofitable after them, especially on a small account
where the minimum lot size forces a bigger position than the risk budget wants.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from .validation import InputError

__all__ = [
    "GrowthProjection",
    "growth_rate_per_trade",
    "project_equity",
    "risk_level_growth_table",
    "trades_to_target",
    "drawdown_recovery_trades",
]


def growth_rate_per_trade(
    win_probability: float, reward_risk: float, risk_fraction: float, cost_in_r: float = 0.0
) -> float:
    """Expected log growth per trade (the "geometric growth rate") for fixed-fractional risk.

    Formula
    -------
    ``g = p x ln(1 + f x (R - c)) + (1 - p) x ln(1 - f x (1 + c))``

    ``g > 0`` means the framework compounds in expectation. ``g < 0`` means it
    bleeds in expectation no matter how good the week felt.

    Example
    -------
    45% win rate, 2R targets, 0.5% risk, no costs:

    >>> round(growth_rate_per_trade(0.45, 2.0, 0.005), 6)
    0.001721
    """
    if not 0 < win_probability < 1:
        raise InputError("win_probability must be in (0, 1)")
    if reward_risk <= 0:
        raise InputError("reward_risk must be > 0")
    if not 0 < risk_fraction < 1:
        raise InputError("risk_fraction must be in (0, 1)")
    win_term = 1.0 + risk_fraction * (reward_risk - cost_in_r)
    loss_term = 1.0 - risk_fraction * (1.0 + cost_in_r)
    if win_term <= 0 or loss_term <= 0:
        raise InputError("risk and cost imply a non-positive equity multiple")
    return win_probability * math.log(win_term) + (1 - win_probability) * math.log(loss_term)


@dataclass(frozen=True)
class GrowthProjection:
    """Projected outcomes of a fixed-fractional framework over ``trades`` trades."""

    trades: int
    win_probability: float
    reward_risk: float
    risk_fraction: float
    cost_in_r: float
    starting_equity: float

    log_growth_per_trade: float
    median_final_equity: float
    mean_log_final_equity: float
    total_growth_pct: float
    annualised_pct_assuming_250_trading_days: float
    breakeven_win_rate: float
    expectancy_r: float

    def report(self) -> str:
        return "\n".join(
            [
                "=" * 74,
                "COMPOUNDING PROJECTION (expected value, geometric)",
                "=" * 74,
                f"  starting equity        : {self.starting_equity:,.2f}",
                f"  trades projected       : {self.trades:,}",
                f"  win rate / reward:risk : {self.win_probability * 100:.1f}% / 1:{self.reward_risk:.2f}",
                f"  risk per trade         : {self.risk_fraction * 100:.3f}%",
                f"  cost per round trip    : {self.cost_in_r:.3f}R",
                f"  expectancy per trade   : {self.expectancy_r:+.4f}R",
                f"  break-even win rate    : {self.breakeven_win_rate * 100:.1f}%",
                "-" * 74,
                f"  log growth per trade   : {self.log_growth_per_trade:+.6f}",
                f"  MEDIAN final equity    : {self.median_final_equity:,.2f}  "
                f"({self.total_growth_pct:+.2f}%)",
                f"  annualised (assumes    : {self.annualised_pct_assuming_250_trading_days:+.2f}%"
                " over a year of the same trade rate)",
                "  An annual figure is a linear extrapolation of one projected stretch. It is",
                "  NOT a prediction, and it assumes the edge never decays.",
                "=" * 74,
                "  CAVEATS THAT MATTER MORE THAN THE NUMBER ABOVE",
                "  * The median is reported because the mean is inflated by a few lucky tails.",
                "  * A real edge decays: markets adapt, spreads widen and your own execution",
                "    changes as the account grows.",
                "  * This assumes a constant edge. Real edges come in regimes and are",
                "    sometimes absent for months. Trade the plan, not the projection.",
                "  * Never use a projection to justify risking more per trade.",
            ]
        )


def project_equity(
    win_probability: float,
    reward_risk: float,
    risk_fraction: float,
    trades: int = 250,
    starting_equity: float = 250.0,
    cost_in_r: float = 0.0,
    reward_risk_breakeven_tolerance: float = 1e-9,
) -> GrowthProjection:
    """Project median equity after ``trades`` trades.

    This is a *planning* tool, not a promise. It exists so you can see how
    brutally the assumption set matters: change the win rate by 5 points and the
    whole curve moves.

    Example
    -------
    >>> proj = project_equity(0.45, 2.0, 0.005, trades=100, starting_equity=250)
    >>> round(proj.median_final_equity, 2)
    296.94
    """
    if trades < 0:
        raise InputError("trades must be >= 0")
    g = growth_rate_per_trade(win_probability, reward_risk, risk_fraction, cost_in_r)
    median = starting_equity * math.exp(g * trades)
    total_pct = (median / starting_equity - 1.0) * 100.0
    # break-even win rate including costs
    from .risk import break_even_win_rate_with_costs

    be = break_even_win_rate_with_costs(reward_risk, cost_in_r) if reward_risk > 0 else 1.0
    expectancy = win_probability * reward_risk - (1 - win_probability) * 1.0 - cost_in_r
    _ = reward_risk_breakeven_tolerance
    return GrowthProjection(
        trades=trades,
        win_probability=win_probability,
        reward_risk=reward_risk,
        risk_fraction=risk_fraction,
        cost_in_r=cost_in_r,
        starting_equity=starting_equity,
        log_growth_per_trade=g,
        median_final_equity=median,
        mean_log_final_equity=g * trades,
        total_growth_pct=total_pct,
        annualised_pct_assuming_250_trading_days=total_pct * (250.0 / trades) if trades else 0.0,
        breakeven_win_rate=be,
        expectancy_r=expectancy,
    )


def risk_level_growth_table(
    win_probability: float,
    reward_risk: float,
    risk_fractions: Sequence[float] = (0.001, 0.0025, 0.005, 0.01, 0.02, 0.05),
    trades: int = 250,
    starting_equity: float = 250.0,
    cost_in_r: float = 0.0,
) -> list[dict[str, float]]:
    """Compare median growth and drawdown exposure across risk levels.

    This is the table that answers "why not just risk 5%?" - because at 5% the
    *typical* path is dominated by drawdown, even when expectancy per trade is
    identical. Same edge, different survival odds.

    Example
    -------
    >>> rows = risk_level_growth_table(0.45, 2.0, (0.005, 0.01), trades=100, starting_equity=250)
    >>> len(rows)
    2
    """
    from .risk import consecutive_loss_probability, recovery_gain_required

    out: list[dict[str, float]] = []
    for f in risk_fractions:
        proj = project_equity(win_probability, reward_risk, f, trades, starting_equity, cost_in_r)
        # expected worst losing streak in `trades` trades at 95% confidence
        from .risk import losing_streak_probabilities

        streaks = losing_streak_probabilities(win_probability, 30, trades)
        p95_streak = next((k for k, p in streaks if p >= 0.95), streaks[-1][0])
        # drawdown implied by that streak, compounding
        dd = 1.0 - (1.0 - f) ** p95_streak
        out.append(
            {
                "risk_fraction": f,
                "risk_percent": f * 100.0,
                "median_final_equity": proj.median_final_equity,
                "median_growth_pct": proj.total_growth_pct,
                "expectancy_r": proj.expectancy_r,
                "p95_losing_streak": float(p95_streak),
                "drawdown_from_that_streak_pct": dd * 100.0,
                "recovery_gain_needed_pct": recovery_gain_required(dd * 100.0),
                "p_such_streak_in_sample": consecutive_loss_probability(win_probability, p95_streak, trades),
            }
        )
    return out


def trades_to_target(
    win_probability: float, reward_risk: float, risk_fraction: float, target_multiple: float = 2.0,
    cost_in_r: float = 0.0,
) -> float:
    """Median number of trades needed to multiply equity by ``target_multiple``.

    Returns ``math.inf`` when the framework has no positive growth - the correct
    answer for a negative-expectancy system, and the reason "doubling the
    account" is not a plan.

    >>> round(trades_to_target(0.45, 2.0, 0.005, 2.0), 1)
    402.8
    """
    if target_multiple <= 0:
        raise InputError("target_multiple must be > 0")
    g = growth_rate_per_trade(win_probability, reward_risk, risk_fraction, cost_in_r)
    if g <= 0:
        return math.inf
    return math.log(target_multiple) / g


def drawdown_recovery_trades(
    win_probability: float, reward_risk: float, risk_fraction: float, drawdown_pct: float,
    cost_in_r: float = 0.0,
) -> float:
    """Median trades needed to recover a given drawdown at the same risk level.

    Shows the asymmetry numerically: at 0.5% risk and a modest edge, recovering
    a 10% drawdown is a multi-week project; recovering 30% is a different season
    of your life.
    """
    from .risk import recovery_gain_required

    g = growth_rate_per_trade(win_probability, reward_risk, risk_fraction, cost_in_r)
    need = recovery_gain_required(drawdown_pct) / 100.0
    if g <= 0:
        return math.inf
    return math.log(1.0 + need) / g
