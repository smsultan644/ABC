"""
Risk of ruin: how likely is it that this risk framework destroys the account?

Two tools are provided, because they answer slightly different questions:

1. :func:`risk_of_ruin_fixed_stake` - classic gambler's ruin, exact, for a
   **fixed** bet size. Good for understanding the maths.
2. :func:`simulate_risk_of_ruin` - Monte Carlo for **fixed-fractional** risk
   (what this project actually teaches), where the bet size shrinks as the
   account shrinks. There is no simple closed form for this, so it is simulated.

"RUIN" IS A CHOICE YOU MAKE, NOT A FACT
--------------------------------------
Ruin is usually defined as losing a stated fraction of the account:
``ruin_fraction=1.0`` means "lost everything", ``0.5`` means "lost half",
``0.3`` means "lost the 30% that would make me stop trading". Choose the
threshold before you simulate. For a USD 250 learning account a sensible
definition of ruin is **-50%**, because continuing after that is a psychological
and financial mistake regardless of the strategy.

WHAT THE NUMBERS TYPICALLY SHOW
-------------------------------
With a genuine edge (say 45% win rate at 1.5R) and honest costs:

* 0.10%-0.25% risk per trade  -> ruin is effectively a rounding error
* 1.00% risk per trade        -> still small, but the *drawdown experience*
  becomes severe enough to break discipline
* 5%-10% risk per trade       -> ruin becomes a realistic outcome within a few
  hundred trades even with a positive edge

That last row is the whole lesson: **edge determines whether you make money,
risk determines whether you survive long enough to collect it.**
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass, field
from typing import Sequence

from .risk import risk_of_ruin_fixed_fraction_analytic  # noqa: F401  (re-exported)
from .validation import InputError

__all__ = [
    "RuinSimulationResult",
    "risk_of_ruin_fixed_fraction_analytic",
    "risk_of_ruin_fixed_stake",
    "simulate_risk_of_ruin",
]


def risk_of_ruin_fixed_stake(
    win_probability: float, win_units: float, loss_units: float, starting_units: float
) -> float:
    """Classic gambler's ruin for a fixed stake, in *units* rather than money.

    Formula (biased random walk)
    ----------------------------
    With ``p`` the win probability, ``q = 1 - p``, and equal-size bets of one
    unit, ruin probability from ``N`` units is::

        (q/p)^N            if p < 0.5   (no edge: ruin is certain in the limit)
        q/p                if p = 0.5
        (q/p)^N            if p > 0.5   (ruin still possible, but decays fast)

    For unequal win/loss sizes the standard generalisation is used here:

    ``ratio = (loss_units x q) / (win_units x p)`` and ruin ``= ratio ** N``
    where ``N = starting_units / loss_units``.

    Example
    -------
    A 50/50 game, betting 1 unit of a 10-unit bankroll, with an opponent of
    infinite wealth, ruins you with probability 1. With a genuine 55% edge:

    >>> round(risk_of_ruin_fixed_stake(0.55, 1.0, 1.0, 20.0), 6)
    0.018072
    """
    if not 0 < win_probability < 1:
        raise InputError("win_probability must be in (0, 1)")
    if win_units <= 0 or loss_units <= 0:
        raise InputError("win_units and loss_units must be > 0")
    if starting_units <= 0:
        raise InputError("starting_units must be > 0")
    p = win_probability
    q = 1.0 - p
    ratio = (loss_units * q) / (win_units * p)
    n = starting_units / loss_units
    if ratio >= 1:
        return 1.0
    return min(1.0, ratio ** n)


@dataclass
class RuinSimulationResult:
    """Outcome distribution of a Monte Carlo ruin simulation."""

    paths: int
    trades: int
    win_probability: float
    reward_risk: float
    risk_fraction: float
    ruin_fraction: float
    outcomes_per_path: int

    ruin_probability: float = 0.0
    profit_probability: float = 0.0
    median_final_equity: float = 0.0
    mean_final_equity: float = 0.0
    percentile_5: float = 0.0
    percentile_25: float = 0.0
    percentile_75: float = 0.0
    percentile_95: float = 0.0
    median_max_drawdown_pct: float = 0.0
    percentile_95_max_drawdown_pct: float = 0.0
    prob_drawdown_over_20pct: float = 0.0
    prob_drawdown_over_50pct: float = 0.0
    prob_bankrupt_before_doubling: float = 0.0
    equity_samples: list[float] = field(default_factory=list, repr=False)

    def report(self) -> str:
        lines = [
            "=" * 74,
            "RISK OF RUIN SIMULATION (Monte Carlo)",
            "=" * 74,
            f"  paths x trades        : {self.paths:,} x {self.trades:,} "
            f"({self.paths * self.trades:,} simulated trades)",
            f"  assumed win rate      : {self.win_probability * 100:.1f}%",
            f"  assumed reward:risk   : 1:{self.reward_risk:.2f} (before costs)",
            f"  risk per trade        : {self.risk_fraction * 100:.3f}% of current equity",
            f"  'ruin' defined as     : losing {self.ruin_fraction * 100:.0f}% of starting equity",
            f"  starting equity       : {self.outcomes_per_path:,.2f} (units)",
            "-" * 74,
            f"  P(ruin)                          : {self.ruin_probability * 100:6.3f}%",
            f"  P(profitable after {self.trades} trades) : {self.profit_probability * 100:6.2f}%",
            f"  P(max drawdown > 20%)            : {self.prob_drawdown_over_20pct * 100:6.2f}%",
            f"  P(max drawdown > 50%)            : {self.prob_drawdown_over_50pct * 100:6.2f}%",
            f"  P(ruin before doubling)          : {self.prob_bankrupt_before_doubling * 100:6.2f}%",
            "-" * 74,
            f"  median final equity              : {self.median_final_equity:,.2f}",
            f"  mean final equity                : {self.mean_final_equity:,.2f}",
            f"  5th / 25th percentile            : {self.percentile_5:,.2f} / {self.percentile_25:,.2f}",
            f"  75th / 95th percentile           : {self.percentile_75:,.2f} / {self.percentile_95:,.2f}",
            f"  median max drawdown              : {self.median_max_drawdown_pct:,.2f}%",
            f"  95th-percentile max drawdown     : {self.percentile_95_max_drawdown_pct:,.2f}%",
            "=" * 74,
            "  Read this as a distribution, not a forecast. Real markets also change",
            "  regime: a backtested win rate is itself an estimate with error bars.",
        ]
        return "\n".join(lines)


def simulate_risk_of_ruin(
    win_probability: float,
    reward_risk: float,
    risk_fraction: float,
    *,
    trades: int = 500,
    paths: int = 20_000,
    starting_equity: float = 250.0,
    ruin_fraction: float = 0.5,
    seed: int = 42,
    cost_in_r: float = 0.0,
    max_equity_samples: int = 0,
) -> RuinSimulationResult:
    """Monte Carlo the equity path of a fixed-fractional risk framework.

    Model
    -----
    Each trade: with probability ``p`` equity multiplies by
    ``1 + risk_fraction x (reward_risk - cost_in_r)``, otherwise by
    ``1 - risk_fraction x (1 + cost_in_r)``. A path stops early if equity falls
    below ``(1 - ruin_fraction) x starting_equity``.

    Parameters
    ----------
    win_probability, reward_risk:
        Your *assumed* edge. Garbage in, garbage out: if you feed the simulator
        the win rate from 20 lucky trades, it will hand you a comfortable
        lie. Use backtest or demo results with a sample size you can defend.
    risk_fraction:
        Risk per trade as a fraction (``0.005`` = 0.5%).
    ruin_fraction:
        Fraction of starting equity that counts as ruin (``0.5`` = -50%).
    cost_in_r:
        Round-trip cost expressed in R (spread + commission / risk). A 50-pip
        stop with a 1-pip spread on a 10 USD/pip lot costs 0.02R; adding it
        makes the simulation honest.
    seed:
        Fixed by default so results are reproducible in tests and reports.

    Example
    -------
    >>> res = simulate_risk_of_ruin(0.45, 1.5, 0.005, trades=200, paths=500, seed=1)
    >>> res.ruin_probability <= 1.0 and res.median_final_equity > 0
    True
    """
    if not 0 < win_probability < 1:
        raise InputError("win_probability must be in (0, 1)")
    if reward_risk <= 0:
        raise InputError("reward_risk must be > 0")
    if not 0 < risk_fraction < 0.5:
        raise InputError("risk_fraction must be in (0, 0.5) - larger is not trading, it is gambling")
    if not 0 < ruin_fraction < 1:
        raise InputError(
            "ruin_fraction must be in (0, 1): fixed-fractional risk never reaches exactly zero "
            "equity, so 'ruin' must be a drawdown level such as 0.5 (-50%)."
        )
    if trades < 1 or paths < 1:
        raise InputError("trades and paths must be >= 1")

    rng = random.Random(seed)
    ruin_level = starting_equity * (1.0 - ruin_fraction)
    double_level = starting_equity * 2.0

    finals: list[float] = []
    max_dds: list[float] = []
    ruined = 0
    doubled = 0
    ruined_before_doubling = 0
    dd_over_20 = 0
    dd_over_50 = 0
    samples: list[float] = []

    win_mult = 1.0 + risk_fraction * (reward_risk - cost_in_r)
    loss_mult = 1.0 - risk_fraction * (1.0 + cost_in_r)

    for path_index in range(paths):
        equity = starting_equity
        peak = equity
        max_dd = 0.0
        hit_ruin = False
        hit_double = False
        for step in range(trades):
            if rng.random() < win_probability:
                equity *= win_mult
            else:
                equity *= loss_mult
            peak = max(peak, equity)
            if peak > 0:
                max_dd = max(max_dd, (peak - equity) / peak * 100.0)
            if equity <= ruin_level:
                hit_ruin = True
                break
            if equity >= double_level:
                hit_double = True
                break
            if max_equity_samples and step % max(1, trades // max_equity_samples) == 0 and path_index == 0:
                samples.append(equity)
        if equity <= 0:
            equity = 0.0
        finals.append(equity)
        max_dds.append(max_dd)
        if hit_ruin:
            ruined += 1
            if not hit_double:
                ruined_before_doubling += 1
        if hit_double:
            doubled += 1
        if max_dd >= 20:
            dd_over_20 += 1
        if max_dd >= 50:
            dd_over_50 += 1

    finals_sorted = sorted(finals)
    dds_sorted = sorted(max_dds)

    def pct(values: Sequence[float], q: float) -> float:
        if not values:
            return 0.0
        idx = min(len(values) - 1, max(0, int(round(q * (len(values) - 1)))))
        return values[idx]

    result = RuinSimulationResult(
        paths=paths,
        trades=trades,
        win_probability=win_probability,
        reward_risk=reward_risk,
        risk_fraction=risk_fraction,
        ruin_fraction=ruin_fraction,
        outcomes_per_path=int(starting_equity),
        ruin_probability=ruined / paths,
        profit_probability=sum(1 for f in finals if f > starting_equity) / paths,
        median_final_equity=statistics.median(finals),
        mean_final_equity=statistics.fmean(finals),
        percentile_5=pct(finals_sorted, 0.05),
        percentile_25=pct(finals_sorted, 0.25),
        percentile_75=pct(finals_sorted, 0.75),
        percentile_95=pct(finals_sorted, 0.95),
        median_max_drawdown_pct=statistics.median(max_dds) if max_dds else 0.0,
        percentile_95_max_drawdown_pct=pct(dds_sorted, 0.95),
        prob_drawdown_over_20pct=dd_over_20 / paths,
        prob_drawdown_over_50pct=dd_over_50 / paths,
        prob_bankrupt_before_doubling=ruined_before_doubling / paths,
        equity_samples=samples,
    )
    _ = doubled  # available for future reporting without changing the dataclass
    return result
