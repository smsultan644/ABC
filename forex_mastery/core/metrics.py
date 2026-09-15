"""
Performance statistics for a set of closed trades.

This module is the measurement half of the system. It answers "is there
evidence of an edge, and where is it coming from?" - not "will the next trade
win?".

It accepts **either** dictionaries **or** objects (dataclasses) as trade
records, so it works with the project's journal model, a freshly imported CSV,
or hand-typed test data without conversion.

Every metric is defined in plain English in its docstring, and every one has a
unit test with a hand-checkable example.

HONESTY NOTES
-------------
* A win rate, a profit factor or an expectancy computed from 20 trades is not
  evidence of anything. The module therefore always reports ``sample_size`` and
  a **standard error** for expectancy, and flags samples that are too small to
  conclude from.
* Sharpe/Sortino "like" ratios here are per-trade figures scaled by
  ``sqrt(trades_per_year)`` only when you supply that number. They are called
  "like" because a trading P/L series is not a normal distribution and the
  annualisation assumes independence - both assumptions are shaky.
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Callable, Iterable, Sequence

from .risk import drawdown_percent, max_drawdown_percent, recovery_gain_required

__all__ = [
    "BucketStat",
    "PerformanceReport",
    "bootstrap_mean_ci",
    "compute_performance",
    "welch_ttest",
]


# ---------------------------------------------------------------------- #
# Helpers
# ---------------------------------------------------------------------- #
def _get(record: Any, key: str, default: Any = None) -> Any:
    """Read a field from a dict-like or object-like record."""
    if isinstance(record, dict):
        return record.get(key, default)
    return getattr(record, key, default)


def _to_float(value: Any, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    if out != out:  # NaN
        return default
    return out


def _month_key(record: Any) -> str | None:
    when = _get(record, "date") or _get(record, "close_time") or _get(record, "open_time")
    if when is None:
        return None
    if isinstance(when, (datetime, date)):
        return f"{when.year:04d}-{when.month:02d}"
    text = str(when)
    return text[:7] if len(text) >= 7 else None


def _weekday_key(record: Any) -> str | None:
    when = _get(record, "date") or _get(record, "close_time")
    if when is None:
        return None
    if isinstance(when, (datetime, date)):
        return when.strftime("%A")
    text = str(when)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[: len(fmt) + 2].strip(), fmt).strftime("%A")
        except ValueError:
            continue
    return None


@dataclass(frozen=True)
class BucketStat:
    """Aggregated statistics for one group (a setup, an instrument, a session...)."""

    label: str
    trades: int
    wins: int
    win_rate: float
    total_r: float
    avg_r: float
    net_pnl: float
    profit_factor: float
    expectancy_r: float

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"{self.label:<22} n={self.trades:<4} win={self.win_rate * 100:5.1f}%  "
            f"totalR={self.total_r:+7.2f}  avgR={self.avg_r:+.3f}  PF={self.profit_factor:5.2f}  "
            f"pnl={self.net_pnl:+9.2f}"
        )


def _bucketise(
    records: Sequence[Any], key_fn: Callable[[Any], str | None]
) -> list[BucketStat]:
    groups: dict[str, list[Any]] = {}
    for record in records:
        key = key_fn(record)
        if key is None or key == "":
            continue
        groups.setdefault(str(key), []).append(record)
    out: list[BucketStat] = []
    for label, items in groups.items():
        rs = [r for r in (_to_float(_get(i, "r_multiple")) for i in items) if r is not None]
        pnls = [p for p in (_to_float(_get(i, "pnl")) for i in items) if p is not None]
        wins = [r for r in rs if r > 0]
        losses = [r for r in rs if r < 0]
        gross_win = sum(r for r in rs if r > 0)
        gross_loss = -sum(r for r in rs if r < 0)
        n = len(rs) or len(pnls)
        out.append(
            BucketStat(
                label=label,
                trades=n,
                wins=len(wins),
                win_rate=(len(wins) / n) if n else 0.0,
                total_r=sum(rs),
                avg_r=(sum(rs) / len(rs)) if rs else 0.0,
                net_pnl=sum(pnls),
                profit_factor=(gross_win / gross_loss) if gross_loss > 0 else (math.inf if gross_win > 0 else 0.0),
                expectancy_r=(sum(rs) / len(rs)) if rs else 0.0,
            )
        )
    # Most productive first: total R is the fairest single ranking.
    out.sort(key=lambda b: b.total_r, reverse=True)
    return out


def bootstrap_mean_ci(
    values: Sequence[float], n_resamples: int = 10_000, confidence: float = 0.95, seed: int = 7
) -> tuple[float, float]:
    """Percentile-bootstrap confidence interval for the mean of ``values``.

    Why bootstrap instead of a t-interval: trading R-multiples are skewed and
    heavy-tailed, so the normal-theory interval is optimistic. Resampling makes
    no distributional assumption. It still cannot rescue a tiny sample - a
    5-trade sample gives a 5-trade-wide interval, which is the correct answer.

    Example
    -------
    >>> lo, hi = bootstrap_mean_ci([2.0, -1, -1, 3, -1, 2, -1, 1.5, -1, -1], n_resamples=2000, seed=1)
    >>> lo < hi
    True
    """
    data = [float(v) for v in values]
    if len(data) < 2:
        value = data[0] if data else 0.0
        return value, value
    rng = random.Random(seed)
    n = len(data)
    means = []
    for _ in range(n_resamples):
        means.append(sum(data[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    lo_idx = int((1 - confidence) / 2 * n_resamples)
    hi_idx = min(n_resamples - 1, int((1 + confidence) / 2 * n_resamples))
    return means[lo_idx], means[hi_idx]


def welch_ttest(a: Sequence[float], b: Sequence[float]) -> tuple[float, float]:
    """Welch's t-test for a difference in means; returns (t, rough two-sided p).

    The p-value uses the normal approximation (no scipy dependency). It is
    adequate for sample sizes above ~30 per group and **misleading below that**.
    Treat it as a screening tool: if two setups differ with p > 0.05 you cannot
    claim one is better, only that you have not shown a difference.
    """
    a = [float(x) for x in a]
    b = [float(x) for x in b]
    if len(a) < 2 or len(b) < 2:
        return 0.0, 1.0
    va, vb = statistics.variance(a), statistics.variance(b)
    na, nb = len(a), len(b)
    se = math.sqrt(va / na + vb / nb)
    if se == 0:
        return 0.0, 1.0
    t = (statistics.fmean(a) - statistics.fmean(b)) / se
    p = math.erfc(abs(t) / math.sqrt(2))
    return t, p


# ---------------------------------------------------------------------- #
# Report container
# ---------------------------------------------------------------------- #
@dataclass
class PerformanceReport:
    """Full statistical picture of a sample of closed trades."""

    sample_size: int = 0
    wins: int = 0
    losses: int = 0
    breakeven: int = 0
    win_rate: float = 0.0

    gross_profit: float = 0.0
    gross_loss: float = 0.0
    net_pnl: float = 0.0
    profit_factor: float = 0.0

    avg_win: float = 0.0
    avg_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    payoff_ratio: float = 0.0

    total_r: float = 0.0
    avg_r: float = 0.0
    median_r: float = 0.0
    std_r: float = 0.0
    avg_win_r: float = 0.0
    avg_loss_r: float = 0.0
    expectancy_r: float = 0.0
    expectancy_currency: float = 0.0
    expectancy_std_error: float = 0.0
    expectancy_ci95: tuple[float, float] = (0.0, 0.0)
    t_statistic: float = 0.0
    p_value_normal_approx: float = 1.0

    sharpe_like: float = 0.0
    sortino_like: float = 0.0
    annualised_sharpe_like: float | None = None

    max_drawdown_pct: float = 0.0
    max_drawdown_r: float = 0.0
    avg_drawdown_pct: float = 0.0
    longest_dd_trades: int = 0
    recovery_gain_needed_pct: float = 0.0

    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    avg_consecutive_losses: float = 0.0

    avg_risk_percent: float = 0.0
    max_risk_percent: float = 0.0
    rule_violation_count: int = 0
    rule_violation_rate: float = 0.0
    rule_violation_total_r: float = 0.0
    emotional_trade_count: int = 0
    emotional_trade_total_r: float = 0.0

    equity_curve: list[float] = field(default_factory=list)
    r_series: list[float] = field(default_factory=list)
    monthly: list[BucketStat] = field(default_factory=list)
    by_setup: list[BucketStat] = field(default_factory=list)
    by_instrument: list[BucketStat] = field(default_factory=list)
    by_session: list[BucketStat] = field(default_factory=list)
    by_timeframe: list[BucketStat] = field(default_factory=list)
    by_direction: list[BucketStat] = field(default_factory=list)
    by_weekday: list[BucketStat] = field(default_factory=list)
    by_quality: list[BucketStat] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    def as_dict(self) -> dict:
        """Flatten to JSON-friendly primitives."""
        data: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if isinstance(value, list) and value and isinstance(value[0], BucketStat):
                data[key] = [vars(v) for v in value]
            else:
                data[key] = value
        return data

    def report(self) -> str:
        """Multi-section plain-text report."""
        w = 74
        L: list[str] = ["=" * w, "PERFORMANCE REPORT".center(w), "=" * w]

        L.append("SAMPLE")
        L.append(f"  trades            : {self.sample_size}  (W {self.wins} / L {self.losses} / BE {self.breakeven})")
        L.append(f"  win rate          : {self.win_rate * 100:.1f}%")
        L.append(f"  net P/L           : {self.net_pnl:+,.2f}")
        L.append(f"  gross profit/loss : {self.gross_profit:,.2f} / -{self.gross_loss:,.2f}")
        L.append(f"  profit factor     : {self.profit_factor:.2f}" + ("  (>1.0 = profitable)" if self.sample_size else ""))
        L.append(f"  total R           : {self.total_r:+.2f}R    average R: {self.avg_r:+.3f}    median R: {self.median_r:+.3f}")
        L.append(f"  avg win / loss    : {self.avg_win:,.2f} / {self.avg_loss:,.2f}   payoff ratio {self.payoff_ratio:.2f}")
        L.append(f"  largest win/loss  : {self.largest_win:+,.2f} / {self.largest_loss:+,.2f}")

        L.append("")
        L.append("EDGE (is the average result better than zero?)")
        L.append(f"  expectancy        : {self.expectancy_r:+.4f}R per trade  ({self.expectancy_currency:+,.3f} per trade)")
        L.append(f"  std error of mean : {self.expectancy_std_error:.4f}R")
        L.append(f"  95% CI (bootstrap): [{self.expectancy_ci95[0]:+.3f}R, {self.expectancy_ci95[1]:+.3f}R]")
        L.append(f"  t-statistic       : {self.t_statistic:+.2f}  (normal-approx p = {self.p_value_normal_approx:.3f})")
        verdict = (
            "CI excludes zero -> some evidence of a positive edge"
            if self.expectancy_ci95[0] > 0 and self.sample_size >= 30
            else "CI includes zero or sample < 30 -> NOT yet evidence of an edge"
        )
        L.append(f"  verdict           : {verdict}")
        L.append(f"  sharpe-like       : {self.sharpe_like:+.3f} per trade"
                 + (f"  (annualised {self.annualised_sharpe_like:+.2f})" if self.annualised_sharpe_like is not None else ""))
        L.append(f"  sortino-like      : {self.sortino_like:+.3f} per trade")

        L.append("")
        L.append("RISK OF THE EQUITY CURVE")
        L.append(f"  max drawdown      : {self.max_drawdown_pct:.2f}%  ({self.max_drawdown_r:.2f}R)")
        L.append(f"  avg drawdown      : {self.avg_drawdown_pct:.2f}%")
        L.append(f"  longest DD (trades): {self.longest_dd_trades}")
        L.append(f"  recovery needed   : {self.recovery_gain_needed_pct:.2f}% gain on remaining equity")
        L.append(f"  max consecutive W : {self.max_consecutive_wins}")
        L.append(f"  max consecutive L : {self.max_consecutive_losses}   (avg losing run {self.avg_consecutive_losses:.2f})")

        L.append("")
        L.append("DISCIPLINE")
        L.append(f"  avg risk/trade    : {self.avg_risk_percent:.3f}% of equity   (max {self.max_risk_percent:.3f}%)")
        L.append(f"  rule violations   : {self.rule_violation_count} ({self.rule_violation_rate * 100:.1f}% of trades), "
                 f"cost {self.rule_violation_total_r:+.2f}R")
        L.append(f"  emotional trades  : {self.emotional_trade_count}, result {self.emotional_trade_total_r:+.2f}R")

        for title, rows in (
            ("BY MONTH", self.monthly),
            ("BY SETUP", self.by_setup),
            ("BY INSTRUMENT", self.by_instrument),
            ("BY SESSION", self.by_session),
            ("BY TIMEFRAME", self.by_timeframe),
            ("BY DIRECTION", self.by_direction),
            ("BY WEEKDAY", self.by_weekday),
            ("BY SETUP QUALITY", self.by_quality),
        ):
            if rows:
                L.append("")
                L.append(title)
                L.extend("  " + str(row) for row in rows)

        if self.warnings:
            L.append("")
            L.append("WARNINGS / LIMITATIONS")
            L.extend("  ! " + w_ for w_ in self.warnings)
        L.append("=" * w)
        return "\n".join(L)


# ---------------------------------------------------------------------- #
# Main computation
# ---------------------------------------------------------------------- #
def compute_performance(
    trades: Iterable[Any],
    *,
    starting_equity: float = 250.0,
    trades_per_year: int | None = None,
    risk_amount_key: str = "risk_amount",
    min_sample_for_evidence: int = 30,
) -> PerformanceReport:
    """Compute the full statistics set for ``trades``.

    Parameters
    ----------
    trades:
        Iterable of dicts or objects. Recognised fields:

        ``r_multiple`` (preferred), ``pnl``, ``risk_amount``, ``risk_percent``,
        ``date``, ``setup``, ``instrument``/``symbol``, ``session``,
        ``timeframe``, ``direction``, ``weekday``, ``setup_quality``,
        ``rule_violation`` (truthy), ``emotion``/``emotional`` (truthy),
        ``status`` ("win"/"loss"/"breakeven" - optional, inferred otherwise).

        ``r_multiple`` is used when present; otherwise it is derived as
        ``pnl / risk_amount``.
    starting_equity:
        Used to build the equity curve and express drawdowns in percent.
    trades_per_year:
        Optional, only to annualise the Sharpe-like ratio.
    min_sample_for_evidence:
        Sample size below which the report refuses to call anything "evidence".
    """
    records = [r for r in trades]
    report = PerformanceReport(sample_size=len(records))
    if not records:
        report.warnings.append("No closed trades supplied - nothing to analyse yet.")
        return report

    # ---- extract series -------------------------------------------------
    r_series: list[float] = []
    pnl_series: list[float] = []
    risk_pcts: list[float] = []
    violation_rs: list[float] = []
    violation_count = 0
    emotional_rs: list[float] = []
    emotional_count = 0

    for record in records:
        r = _to_float(_get(record, "r_multiple"))
        pnl = _to_float(_get(record, "pnl"))
        risk_amount = _to_float(_get(record, risk_amount_key))
        if r is None and pnl is not None and risk_amount:
            r = pnl / risk_amount
        r_series.append(r if r is not None else 0.0)
        pnl_series.append(pnl if pnl is not None else (r or 0.0) * (risk_amount or 0.0))

        risk_pct = _to_float(_get(record, "risk_percent"))
        if risk_pct is None and risk_amount and starting_equity:
            risk_pct = risk_amount / starting_equity * 100.0
        if risk_pct is not None:
            risk_pcts.append(risk_pct)

        violated = bool(_get(record, "rule_violation", False))
        if violated:
            violation_count += 1
            violation_rs.append(r if r is not None else 0.0)
        if bool(_get(record, "emotion", False)) or bool(_get(record, "emotional", False)):
            emotional_count += 1
            emotional_rs.append(r if r is not None else 0.0)

    report.r_series = r_series
    report.wins = sum(1 for r in r_series if r > 1e-9)
    report.losses = sum(1 for r in r_series if r < -1e-9)
    report.breakeven = len(r_series) - report.wins - report.losses
    decisive = report.wins + report.losses
    report.win_rate = (report.wins / decisive) if decisive else 0.0

    report.gross_profit = sum(p for p in pnl_series if p > 0)
    report.gross_loss = -sum(p for p in pnl_series if p < 0)
    report.net_pnl = sum(pnl_series)
    report.profit_factor = (
        report.gross_profit / report.gross_loss
        if report.gross_loss > 0
        else (math.inf if report.gross_profit > 0 else 0.0)
    )

    winning_r = [r for r in r_series if r > 0]
    losing_r = [r for r in r_series if r < 0]
    report.avg_win_r = statistics.fmean(winning_r) if winning_r else 0.0
    report.avg_loss_r = abs(statistics.fmean(losing_r)) if losing_r else 0.0

    winning_pnl = [p for p in pnl_series if p > 0]
    losing_pnl = [p for p in pnl_series if p < 0]
    report.avg_win = statistics.fmean(winning_pnl) if winning_pnl else 0.0
    report.avg_loss = abs(statistics.fmean(losing_pnl)) if losing_pnl else 0.0
    report.largest_win = max(pnl_series) if pnl_series else 0.0
    report.largest_loss = min(pnl_series) if pnl_series else 0.0
    report.payoff_ratio = (report.avg_win / report.avg_loss) if report.avg_loss > 0 else math.inf

    report.total_r = sum(r_series)
    report.avg_r = statistics.fmean(r_series)
    report.median_r = statistics.median(r_series)
    report.std_r = statistics.stdev(r_series) if len(r_series) > 1 else 0.0
    report.expectancy_r = report.avg_r
    report.expectancy_currency = statistics.fmean(pnl_series)
    if len(r_series) > 1:
        report.expectancy_std_error = report.std_r / math.sqrt(len(r_series))
        report.expectancy_ci95 = bootstrap_mean_ci(r_series, seed=11)
        report.t_statistic = (
            report.avg_r / report.expectancy_std_error if report.expectancy_std_error > 0 else 0.0
        )
        report.p_value_normal_approx = math.erfc(abs(report.t_statistic) / math.sqrt(2))

    # ---- risk-adjusted ratios ------------------------------------------
    if report.std_r > 0:
        report.sharpe_like = report.avg_r / report.std_r
        if trades_per_year:
            report.annualised_sharpe_like = report.sharpe_like * math.sqrt(trades_per_year)
    downside = [r for r in r_series if r < 0]
    if downside:
        dd_dev = math.sqrt(sum(r * r for r in downside) / len(r_series))
        report.sortino_like = report.avg_r / dd_dev if dd_dev > 0 else 0.0

    # ---- equity curve and drawdowns ------------------------------------
    equity = float(starting_equity)
    curve = [equity]
    for pnl in pnl_series:
        equity += pnl
        curve.append(equity)
    report.equity_curve = curve
    dd_pct, _, _ = max_drawdown_percent(curve)
    report.max_drawdown_pct = dd_pct
    # same thing measured in R
    cumulative_r: list[float] = [0.0]
    for r in r_series:
        cumulative_r.append(cumulative_r[-1] + r)
    peak = -math.inf
    max_dd_r = 0.0
    dd_lengths: list[int] = []
    current_len = 0
    for value in cumulative_r:
        if value >= peak:
            if current_len:
                dd_lengths.append(current_len)
            peak = value
            current_len = 0
        else:
            current_len += 1
            max_dd_r = max(max_dd_r, peak - value)
    if current_len:
        dd_lengths.append(current_len)
    report.max_drawdown_r = max_dd_r
    report.longest_dd_trades = max(dd_lengths) if dd_lengths else 0
    rolling_dds = [d for d in _rolling_drawdowns(curve) if d > 0]
    report.avg_drawdown_pct = statistics.fmean(rolling_dds) if rolling_dds else 0.0
    report.recovery_gain_needed_pct = recovery_gain_required(report.max_drawdown_pct)

    # ---- streaks -------------------------------------------------------
    report.max_consecutive_wins = _max_run(r_series, positive=True)
    report.max_consecutive_losses = _max_run(r_series, positive=False)
    loss_runs = _runs(r_series, positive=False)
    report.avg_consecutive_losses = statistics.fmean(loss_runs) if loss_runs else 0.0

    # ---- discipline ----------------------------------------------------
    if risk_pcts:
        report.avg_risk_percent = statistics.fmean(risk_pcts)
        report.max_risk_percent = max(risk_pcts)
    report.rule_violation_count = violation_count
    report.rule_violation_rate = violation_count / len(records)
    report.rule_violation_total_r = sum(violation_rs)
    report.emotional_trade_count = emotional_count
    report.emotional_trade_total_r = sum(emotional_rs)

    # ---- breakdowns ----------------------------------------------------
    report.monthly = _bucketise(records, _month_key)
    report.by_setup = _bucketise(records, lambda r: _get(r, "setup"))
    report.by_instrument = _bucketise(
        records, lambda r: _get(r, "instrument") or _get(r, "symbol")
    )
    report.by_session = _bucketise(records, lambda r: _get(r, "session"))
    report.by_timeframe = _bucketise(records, lambda r: _get(r, "timeframe"))
    report.by_direction = _bucketise(records, lambda r: _get(r, "direction"))
    report.by_weekday = _bucketise(records, _weekday_key)
    report.by_quality = _bucketise(records, lambda r: _get(r, "setup_quality"))

    # ---- honest limitations --------------------------------------------
    if report.sample_size < min_sample_for_evidence:
        report.warnings.append(
            f"Only {report.sample_size} trades. Below {min_sample_for_evidence} trades you cannot "
            "distinguish an edge from luck; treat every number above as provisional."
        )
    if report.sample_size < 100:
        report.warnings.append(
            "Fewer than 100 trades: estimates of win rate and expectancy have wide error bars "
            "(the CI above shows the range, not the certainty)."
        )
    if report.expectancy_ci95[0] <= 0 <= report.expectancy_ci95[1]:
        report.warnings.append(
            "The 95% bootstrap interval for expectancy includes zero. The correct conclusion is "
            "'no demonstrated edge yet', not 'the strategy works'."
        )
    if report.max_risk_percent > 1.0:
        report.warnings.append(
            f"Some trades risked more than 1% of equity (max {report.max_risk_percent:.2f}%). "
            "This is outside the framework in this project and inflates both returns and ruin risk."
        )
    if report.rule_violation_rate > 0.10:
        report.warnings.append(
            f"{report.rule_violation_rate * 100:.0f}% of trades broke at least one of your rules. "
            "Performance data from undisciplined execution cannot validate a strategy - fix process first."
        )
    if report.profit_factor == math.inf:
        report.warnings.append(
            "Profit factor is infinite because there were no losing trades. In a real market this "
            "means the sample is too small or the stops are not being respected."
        )
    if len(report.r_series) > 1 and statistics.stdev(report.r_series) > 3:
        report.warnings.append(
            "R-multiple dispersion is unusually wide (std > 3R). Check for a few outsized results "
            "dominating the sample, or for R being recorded inconsistently."
        )
    return report


def _max_run(series: Sequence[float], *, positive: bool) -> int:
    best = current = 0
    for value in series:
        hit = value > 1e-9 if positive else value < -1e-9
        if hit:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def _runs(series: Sequence[float], *, positive: bool) -> list[int]:
    runs: list[int] = []
    current = 0
    for value in series:
        hit = value > 1e-9 if positive else value < -1e-9
        if hit:
            current += 1
        elif current:
            runs.append(current)
            current = 0
    if current:
        runs.append(current)
    return runs


def _rolling_drawdowns(curve: Sequence[float]) -> list[float]:
    """Every drawdown value along the curve (percent from the running peak)."""
    peak = float("-inf")
    out: list[float] = []
    for value in curve:
        peak = max(peak, float(value))
        if peak > 0:
            out.append(drawdown_percent(peak, value))
    return out
