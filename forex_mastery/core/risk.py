"""
Risk, reward, R-multiples, drawdown mathematics and expectancy.

R - THE UNIVERSAL UNIT
----------------------
One **R** is the amount you risked on a trade. Everything is measured in R
because it makes results comparable across instruments, account sizes and
market conditions:

* risking 1.25 USD and making 3.10 USD is **+2.48R**
* risking 1.25 USD and losing 1.25 USD is **-1.00R**

Total R tells you whether your *process* works. Account currency tells you how
big your account was. A strategy with a positive total R over a large sample is
evidence; a profitable week is not.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from .validation import InputError

__all__ = [
    "DrawdownRow",
    "breakeven_win_rate",
    "break_even_win_rate_with_costs",
    "consecutive_loss_probability",
    "drawdown_ladder",
    "drawdown_percent",
    "expectancy_currency",
    "expectancy_r",
    "kelly_fraction",
    "losing_streak_probabilities",
    "max_consecutive_losses_in_sample",
    "max_drawdown_percent",
    "r_multiple",
    "recovery_gain_required",
    "risk_of_ruin_fixed_fraction_analytic",
    "risk_reward",
    "portfolio_heat",
]


# ---------------------------------------------------------------------- #
# R-multiples, R:R and win-rate thresholds
# ---------------------------------------------------------------------- #
def r_multiple(profit_or_loss: float, risk_amount: float) -> float:
    """Convert a P/L into R.

    Formula: ``R = P/L / risk_amount``

    Example
    -------
    >>> r_multiple(31.0, 12.5)
    2.48
    >>> r_multiple(-12.5, 12.5)
    -1.0
    """
    if risk_amount <= 0:
        raise InputError("risk_amount must be > 0 to compute an R-multiple")
    return float(profit_or_loss) / float(risk_amount)


def risk_reward(entry: float, stop: float, target: float, direction: str = "long") -> float:
    """Reward-to-risk ratio as ``reward / risk`` (so 2.0 means "2R target").

    Validates that the levels are on the correct side for the direction, and
    raises :class:`InputError` otherwise: a "trade" whose target is behind the
    entry is not a trade, it is a typo.

    Example
    -------
    >>> round(risk_reward(1.1000, 1.0950, 1.1150, "long"), 6)
    3.0
    """
    d = direction.lower()
    if d.startswith("l"):
        if not (stop < entry < target):
            raise InputError("For a long: stop < entry < target is required.")
        risk = entry - stop
        reward = target - entry
    elif d.startswith("s"):
        if not (target < entry < stop):
            raise InputError("For a short: target < entry < stop is required.")
        risk = stop - entry
        reward = entry - target
    else:
        raise InputError(f"direction must be 'long' or 'short', got {direction!r}")
    if risk <= 0:
        raise InputError("risk distance must be > 0")
    return reward / risk


def breakeven_win_rate(reward_risk: float) -> float:
    """Win rate needed to break even, ignoring costs.

    Formula: ``p = 1 / (1 + R:R)``

    Examples: 1:1 -> 50%; 1:2 -> 33.3%; 1:3 -> 25%; 1:0.5 -> 66.7%.

    >>> round(breakeven_win_rate(2.0), 4)
    0.3333
    """
    if reward_risk <= 0:
        raise InputError("reward_risk must be > 0")
    return 1.0 / (1.0 + float(reward_risk))


def break_even_win_rate_with_costs(
    avg_win_r: float, cost_in_r: float = 0.0
) -> float:
    """Break-even win rate when the round-trip cost is expressed in R.

    Costs are paid on *both* outcomes, so they are subtracted from the winning
    side and added to the losing side:
    ``p >= 1 / (1 + avg_win_r - 2 x cost_in_r)`` is not quite right; the exact
    break-even is ``p = (1 + c) / (1 + avg_win_r - c)`` where ``c`` is cost in R.
    With cost as a fraction of R, a win yields ``avg_win_r - c`` and a loss
    costs ``1 + c``; setting ``p(avg_win_r - c) = (1-p)(1+c)`` gives this
    function.

    Example: 2R average winner with 0.1R of costs needs 36.7% instead of 33.3%.
    """
    if avg_win_r <= 0:
        raise InputError("avg_win_r must be > 0")
    if cost_in_r < 0:
        raise InputError("cost_in_r must be >= 0")
    denom = (1.0 + avg_win_r)
    if denom <= 0:
        raise InputError("invalid reward")
    return (1.0 + cost_in_r) / denom


# ---------------------------------------------------------------------- #
# Expectancy
# ---------------------------------------------------------------------- #
def expectancy_r(win_rate: float, avg_win_r: float, avg_loss_r: float = 1.0) -> float:
    """Expected value per trade in R.

    Formula: ``E = p x W - (1 - p) x L``

    where ``p`` is the win rate, ``W`` the average winner in R and ``L`` the
    average loser in R (as a positive number; 1.0 means you always respect the
    stop).

    Examples
    --------
    >>> round(expectancy_r(0.40, 2.5, 1.0), 4)   # 40% win rate, 2.5R winners
    0.4
    >>> round(expectancy_r(0.70, 1.0, 1.0), 4)   # 70% win rate, 1R winners
    0.4
    >>> round(expectancy_r(0.45, 1.5, 1.5), 4)   # pays for sloppy stops
    -0.15
    """
    if not 0 < win_rate <= 1:
        raise InputError("win_rate must be in (0, 1]")
    if avg_win_r < 0 or avg_loss_r < 0:
        raise InputError("average win/loss magnitudes must be >= 0")
    return win_rate * avg_win_r - (1.0 - win_rate) * avg_loss_r


def expectancy_currency(
    win_rate: float, avg_win: float, avg_loss: float
) -> float:
    """Expected value per trade in account currency.

    ``E = p x avg_win - (1 - p) x avg_loss`` where the losses are positive
    magnitudes. A positive number is the *only* durable reason a strategy makes
    money; everything else is variance.
    """
    if not 0 < win_rate <= 1:
        raise InputError("win_rate must be in (0, 1]")
    return win_rate * float(avg_win) - (1.0 - win_rate) * abs(float(avg_loss))


def kelly_fraction(win_rate: float, reward_risk: float) -> float:
    """Kelly-optimal fraction of capital to risk (educational).

    Formula: ``f* = p - (1 - p) / R``

    **Read this before using it.** Kelly assumes you know ``p`` and ``R``
    exactly. In trading you estimate them from small samples, and Kelly is
    extremely sensitive to estimation error: feeding it an optimistic win rate
    produces a fraction that destroys the account. Furthermore, full Kelly on a
    *single* edge that you have mis-estimated has an uncomfortably high
    probability of a deep drawdown. The professional convention is to use a
    small fraction of Kelly (often 1/10 to 1/4) and then cap it with a plain
    risk budget like 0.25%-1% per trade. For a USD 250 learning account the cap
    wins, essentially always.

    Returns a negative number when the edge is negative (do not trade it).
    """
    if not 0 < win_rate <= 1:
        raise InputError("win_rate must be in (0, 1]")
    if reward_risk <= 0:
        raise InputError("reward_risk must be > 0")
    return win_rate - (1.0 - win_rate) / reward_risk


# ---------------------------------------------------------------------- #
# Drawdown
# ---------------------------------------------------------------------- #
def drawdown_percent(peak: float, trough: float) -> float:
    """Drawdown from a peak to a later trough, as a positive percentage.

    Formula: ``DD% = (peak - trough) / peak x 100``

    >>> round(drawdown_percent(275.0, 233.75), 4)
    15.0
    """
    if peak <= 0:
        raise InputError("peak must be > 0")
    return max(0.0, (float(peak) - float(trough)) / float(peak) * 100.0)


def max_drawdown_percent(equity_curve: Sequence[float]) -> tuple[float, int, int]:
    """Largest peak-to-trough fall in an equity curve.

    Returns
    -------
    (max_drawdown_percent, peak_index, trough_index)

    Example
    -------
    >>> curve = [250, 260, 255, 300, 280, 270, 275]
    >>> round(max_drawdown_percent(curve)[0], 4)
    10.0
    """
    if not equity_curve:
        return 0.0, 0, 0
    peak = float(equity_curve[0])
    peak_idx = trough_idx = best_peak_idx = 0
    max_dd = 0.0
    for i, value in enumerate(equity_curve):
        v = float(value)
        if v > peak:
            peak, peak_idx = v, i
        if peak > 0:
            dd = (peak - v) / peak * 100.0
            if dd > max_dd:
                max_dd, best_peak_idx, trough_idx = dd, peak_idx, i
    return max_dd, best_peak_idx, trough_idx


def recovery_gain_required(drawdown_pct: float) -> float:
    """Gain needed on the remaining equity to get back to the old peak.

    Formula: ``required% = DD / (1 - DD) x 100``

    | Drawdown | Gain needed to recover |
    |----------|------------------------|
    | 5%       | 5.3%                   |
    | 10%      | 11.1%                  |
    | 20%      | 25.0%                  |
    | 30%      | 42.9%                  |
    | 50%      | 100.0%                 |
    | 70%      | 233.3%                 |

    This asymmetry - not a lack of trading skill - is the mathematical reason
    capital preservation outranks profit maximisation.

    >>> round(recovery_gain_required(20.0), 2)
    25.0
    """
    if not 0 <= drawdown_pct < 100:
        raise InputError("drawdown_pct must be in [0, 100)")
    d = drawdown_pct / 100.0
    return d / (1.0 - d) * 100.0


@dataclass(frozen=True)
class DrawdownRow:
    """One row of the drawdown ladder table."""

    drawdown_percent: float
    equity_multiple_remaining: float
    losses_at_1_00_pct: int
    losses_at_0_50_pct: int
    losses_at_0_25_pct: int
    losses_at_0_10_pct: int
    real_losses_at_0_50_pct_with_1_5R: int


def drawdown_ladder(
    drawdowns: Sequence[float] = (5.0, 10.0, 20.0, 30.0, 50.0),
    risk_percents: Sequence[float] = (1.00, 0.50, 0.25, 0.10),
    reward_risk: float = 1.5,
) -> list[DrawdownRow]:
    """How many consecutive losses produce a given drawdown at each risk level.

    Losses compound on the *remaining* equity, so the loss count is
    ``ceil(ln(1 - DD) / ln(1 - risk))`` - slightly more than the naive
    ``DD / risk``. This is why "30 losses at 0.5%" is not 30 but a little more,
    and why the difference grows as the risk grows.

    ``real_losses_at_0_50_pct_with_1_5R`` models a realistic sequence in which
    every second loss is followed by one winner at ``reward_risk``, i.e. an
    alternating W-L pattern. It exists to show how a modest edge changes the
    arithmetic.
    """
    rows: list[DrawdownRow] = []
    for dd in drawdowns:
        r: dict[float, int] = {}
        for rp in risk_percents:
            if rp >= 100:
                r[rp] = 0
                continue
            n = math.ceil(math.log(1 - dd / 100.0) / math.log(1 - rp / 100.0))
            r[rp] = max(0, n)
        # alternating pattern: for every 2 trades the net outcome is (-1 + R) x risk
        net_per_pair = (reward_risk - 1.0) / 100.0 * 0.50  # in fraction of equity, at 0.5% risk
        if net_per_pair > 0:
            losses_alt = 0
        else:
            per_pair_loss = abs(net_per_pair)
            pairs = math.ceil(math.log(1 - dd / 100.0) / math.log(1 - per_pair_loss)) if per_pair_loss > 0 else 0
            losses_alt = pairs * 2
        rows.append(
            DrawdownRow(
                drawdown_percent=dd,
                equity_multiple_remaining=1 - dd / 100.0,
                losses_at_1_00_pct=r.get(1.00, 0),
                losses_at_0_50_pct=r.get(0.50, 0),
                losses_at_0_25_pct=r.get(0.25, 0),
                losses_at_0_10_pct=r.get(0.10, 0),
                real_losses_at_0_50_pct_with_1_5R=losses_alt,
            )
        )
    return rows


# ---------------------------------------------------------------------- #
# Streaks and ruin
# ---------------------------------------------------------------------- #
def losing_streak_probabilities(
    win_rate: float, max_streak: int, trades: int = 100
) -> list[tuple[int, float]]:
    """Probability of experiencing a run of at least ``k`` losses, for k = 1..max_streak.

    Uses exact dynamic programming over the state "length of the current losing
    run, given that no long enough run has happened yet". Absorbed paths are
    dropped rather than carried forward, so the probabilities cannot be
    double-counted (an earlier version of this function counted them twice and
    overstated streak risk - the unit test brute-forces small cases to keep it
    honest).

    This is the number that stops people being surprised by a 7-loss streak in a
    system that genuinely wins 45% of the time: with 400 trades the chance of a
    7-loss run is substantial.

    Example
    -------
    >>> probs = dict(losing_streak_probabilities(0.45, 6, trades=100))
    >>> bool(0.0 < probs[4] < probs[2] <= 1.0)
    True
    >>> round(dict(losing_streak_probabilities(0.5, 2, trades=5))[2], 5)  # 19/32
    0.59375
    """
    if not 0 < win_rate < 1:
        raise InputError("win_rate must be in (0, 1) for streak analysis")
    if max_streak < 1 or trades < 1:
        raise InputError("max_streak and trades must be >= 1")
    p_loss = 1.0 - win_rate
    results: list[tuple[int, float]] = []
    for k in range(1, max_streak + 1):
        # state[j] = P(current run is exactly j losses AND no k-run has occurred yet)
        state = [0.0] * k
        state[0] = 1.0
        for _ in range(trades):
            new = [0.0] * k
            for run, prob in enumerate(state):
                if prob == 0.0:
                    continue
                new[0] += prob * win_rate                     # a win resets the run
                if run + 1 < k:
                    new[run + 1] += prob * p_loss             # run continues, still "safe"
                # run + 1 == k -> the streak happened: drop the mass (counted below)
            state = new
        never_hit = sum(state)
        results.append((k, max(0.0, min(1.0, 1.0 - never_hit))))
    return results


def consecutive_loss_probability(win_rate: float, streak: int, trades: int = 100) -> float:
    """Contract of probability of at least one run of ``streak`` losses."""
    return dict(losing_streak_probabilities(win_rate, streak, trades))[streak]


def max_consecutive_losses_in_sample(sample: Sequence[float]) -> int:
    """Longest run of negative R values in a realised sample."""
    longest = current = 0
    for value in sample:
        if float(value) < 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def risk_of_ruin_fixed_fraction_analytic(
    win_rate: float, reward_risk: float, risk_fraction: float, ruin_fraction: float = 0.5
) -> float:
    """Approximate ruin probability for fixed-fractional risk.

    There is no exact closed form for fixed-fractional sizing (the outcome
    distribution is not a simple random walk on a finite state space), so this
    uses the standard "risk multiple" transformation:

    * each trade risks ``f`` of current equity
    * a win adds ``f x R`` of current equity, a loss subtracts ``f``
    * ruin is reached after ``n = ceil(ln(1 - ruin_fraction) / ln(1 - f))``
      consecutive losses (a *sufficient* condition, not the only path)

    The returned value is therefore the **probability of an outright
    consecutive-loss wipe-out**, which is a lower bound on true ruin risk
    (streaky-but-interrupted sequences can also grind an account down). For a
    full picture use :func:`forex_mastery.core.risk_of_ruin.simulate_risk_of_ruin`,
    which Monte-Carlos the whole path.

    Note
    ----
    ``ruin_fraction`` must be strictly less than 1. Under fixed-fractional
    sizing you can never lose *exactly* 100% of equity - each loss is a fraction
    of what remains, so equity approaches but never reaches zero. This is a real
    and useful property of fixed-fractional risk, and it is why professionals
    define ruin as a drawdown level (for example -50%) rather than as "blown
    account". It also means the truly dangerous outcome is not zero: it is
    grinding down to a size where the account is useless and your
    decision-making has collapsed.

    Example
    -------
    >>> round(risk_of_ruin_fixed_fraction_analytic(0.45, 1.5, 0.01, ruin_fraction=0.5), 6)
    0.0
    """
    if not 0 < win_rate < 1:
        raise InputError("win_rate must be in (0, 1)")
    if risk_fraction <= 0 or risk_fraction >= 1:
        raise InputError("risk_fraction must be in (0, 1)")
    if not 0 < ruin_fraction < 1:
        raise InputError(
            "ruin_fraction must be in (0, 1). Fixed-fractional risk never reaches exactly zero "
            "equity, so 'ruin' has to be defined as a drawdown level (0.5 = -50%)."
        )
    n = math.ceil(math.log(1 - ruin_fraction) / math.log(1 - risk_fraction))
    p_loss = 1.0 - win_rate
    return p_loss ** n


def portfolio_heat(open_risks: Sequence[float]) -> dict[str, float]:
    """Total risk currently live on the account.

    ``portfolio heat`` = sum of the money you lose if *every* open position hits
    its stop simultaneously. Correlated positions (long EURUSD + long GBPUSD +
    short USDCHF) can all stop out together, so heat must be measured with
    correlation in mind, not position by position.

    House rule used in this project: total heat <= 2% while learning, and
    <= 3% ever. Beyond that, one news event can take most of a week's progress.
    """
    total = float(sum(open_risks))
    return {
        "positions": float(len(list(open_risks))),
        "total_risk": total,
        "max_single_risk": max(open_risks) if open_risks else 0.0,
        "average_risk": (total / len(open_risks)) if open_risks else 0.0,
    }
