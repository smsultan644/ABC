"""Tests for the performance statistics engine."""

from __future__ import annotations

import math

import pytest

from forex_mastery.core.metrics import (
    bootstrap_mean_ci,
    compute_performance,
    welch_ttest,
)


def sample_trades():
    """A small, fully hand-checkable sample of 10 closed trades.

    P/L and risk are set so that every R-multiple is exact:
        win  = +2R,  win  = +3R,  loss = -1R ...
    """
    rows = [
        # (pnl, risk, setup, session, symbol, weekday/date, quality, violation)
        (2.50, 1.25, "trend_pullback", "London", "EURUSD", "2026-09-01", "A", False),
        (-1.25, 1.25, "trend_pullback", "London", "EURUSD", "2026-09-02", "A", False),
        (2.50, 1.25, "trend_pullback", "London", "EURUSD", "2026-09-03", "A", False),
        (-1.25, 1.25, "breakout_retest", "New York", "GBPUSD", "2026-09-04", "B", False),
        (3.75, 1.25, "breakout_retest", "New York", "GBPUSD", "2026-09-08", "B", False),
        (-1.25, 1.25, "breakout_retest", "New York", "GBPUSD", "2026-09-09", "B", False),
        (-1.25, 1.25, "range_edge_rejection", "London", "USDJPY", "2026-09-10", "C", True),
        (1.25, 1.25, "range_edge_rejection", "London", "USDJPY", "2026-09-11", "C", True),
        (-2.50, 1.25, "range_edge_rejection", "London", "USDJPY", "2026-09-15", "C", True),
        (0.00, 1.25, "range_edge_rejection", "London", "USDJPY", "2026-09-15", "C", False),
    ]
    trades = []
    for index, (pnl, risk, setup, session, symbol, date, quality, violated) in enumerate(rows):
        trades.append(
            {
                "trade_id": f"T-{index + 1:04d}",
                "date": date,
                "symbol": symbol,
                "setup": setup,
                "session": session,
                "timeframe": "4H",
                "direction": "long" if index % 2 == 0 else "short",
                "setup_quality": quality,
                "pnl": pnl,
                "risk_amount": risk,
                "risk_percent": 0.5,
                "r_multiple": pnl / risk,
                "rule_violation": violated,
                "emotion": violated,
            }
        )
    return trades


class TestCoreStatistics:
    def test_win_rate_and_counts(self):
        report = compute_performance(sample_trades())
        assert report.sample_size == 10
        # winners: +2R, +2R, +3R, +1R ; losers: -1R x4, -2R ; one breakeven
        assert report.wins == 4
        assert report.losses == 5
        assert report.breakeven == 1
        # decisive = 4 wins + 5 losses = 9 -> 44.4%
        assert report.win_rate == pytest.approx(4 / 9)

    def test_gross_and_net_pnl_and_profit_factor(self):
        report = compute_performance(sample_trades())
        # gross profit = 2.50 + 2.50 + 3.75 + 1.25 = 10.00
        assert report.gross_profit == pytest.approx(10.0)
        # gross loss = (1.25 x 4) + 2.50 = 7.50
        assert report.gross_loss == pytest.approx(7.5)
        assert report.net_pnl == pytest.approx(2.5)
        assert report.profit_factor == pytest.approx(10.0 / 7.5)  # 1.333

    def test_expectancy_in_r_and_currency(self):
        report = compute_performance(sample_trades())
        # total R = +2 -1 +2 -1 +3 -1 -1 +1 -2 +0 = +2R over 10 trades
        assert report.total_r == pytest.approx(2.0)
        assert report.avg_r == pytest.approx(0.2)
        assert report.expectancy_currency == pytest.approx(0.25)

    def test_average_win_loss_and_payoff(self):
        report = compute_performance(sample_trades())
        assert report.avg_win == pytest.approx(2.50)
        assert report.avg_loss == pytest.approx(1.50)
        assert report.payoff_ratio == pytest.approx(2.50 / 1.50)

    def test_streaks(self):
        report = compute_performance(sample_trades())
        assert report.max_consecutive_wins == 1
        assert report.max_consecutive_losses == 2

    def test_equity_curve_and_drawdown(self):
        report = compute_performance(sample_trades(), starting_equity=250.0)
        assert report.equity_curve[0] == pytest.approx(250.0)
        assert report.equity_curve[-1] == pytest.approx(252.50)
        # peak 256.25 -> trough 252.50 = 1.4634%
        assert report.max_drawdown_pct == pytest.approx(1.4634, abs=0.001)
        assert report.max_drawdown_r == pytest.approx(3.0)   # +5R peak -> +2R trough
        assert report.recovery_gain_needed_pct == pytest.approx(1.4851, abs=0.001)

    def test_discipline_metrics(self):
        report = compute_performance(sample_trades())
        assert report.rule_violation_count == 3
        assert report.rule_violation_rate == pytest.approx(0.3)
        # violations: -1R, +1R, -2R = -2R
        assert report.rule_violation_total_r == pytest.approx(-2.0)
        assert report.emotional_trade_count == 3
        assert report.avg_risk_percent == pytest.approx(0.5)

    def test_breakdowns(self):
        report = compute_performance(sample_trades())
        by_setup = {b.label: b for b in report.by_setup}
        assert set(by_setup) == {"trend_pullback", "breakout_retest", "range_edge_rejection"}
        assert by_setup["trend_pullback"].total_r == pytest.approx(3.0)
        assert by_setup["range_edge_rejection"].total_r == pytest.approx(-2.0)
        # ranked best first
        assert report.by_setup[0].label == "trend_pullback"
        by_session = {b.label: b for b in report.by_session}
        assert set(by_session) == {"London", "New York"}
        by_symbol = {b.label: b for b in report.by_instrument}
        assert by_symbol["EURUSD"].win_rate == pytest.approx(2 / 3)
        by_quality = {b.label: b for b in report.by_quality}
        assert set(by_quality) == {"A", "B", "C"}
        assert by_quality["A"].total_r > by_quality["C"].total_r
        assert report.monthly and report.monthly[0].label == "2026-09"

    def test_small_sample_warning_is_present_and_honest(self):
        report = compute_performance(sample_trades())
        assert report.warnings
        assert any("cannot" in w or "provisional" in w for w in report.warnings)

    def test_report_renders_without_error(self):
        text = compute_performance(sample_trades()).report()
        assert "PERFORMANCE REPORT" in text
        assert "expectancy" in text.lower()

    def test_empty_sample_is_handled(self):
        report = compute_performance([])
        assert report.sample_size == 0
        assert "No closed trades" in report.warnings[0]
        assert report.profit_factor == 0.0

    def test_r_derived_from_pnl_and_risk_when_absent(self):
        trades = [{"pnl": 5.0, "risk_amount": 2.5, "date": "2026-09-01"}]
        report = compute_performance(trades)
        assert report.r_series == [pytest.approx(2.0)]

    def test_negative_expectancy_is_reported_as_such(self):
        trades = [{"pnl": -1.0, "risk_amount": 1.0, "date": "2026-09-01"} for _ in range(30)]
        report = compute_performance(trades)
        assert report.expectancy_r == pytest.approx(-1.0)
        assert report.profit_factor == 0.0
        assert report.expectancy_ci95[1] <= 0


class TestStatisticalHelpers:
    def test_bootstrap_interval_is_ordered_and_contains_mean(self):
        values = [2.0, -1.0, -1.0, 3.0, -1.0, 2.0, -1.0, 1.5, -1.0, -1.0]
        low, high = bootstrap_mean_ci(values, n_resamples=2000, seed=3)
        assert low < high
        assert low <= sum(values) / len(values) <= high

    def test_bootstrap_is_reproducible_with_seed(self):
        values = [1.0, -1.0, 2.0, -1.5, 0.5]
        assert bootstrap_mean_ci(values, n_resamples=500, seed=5) == bootstrap_mean_ci(
            values, n_resamples=500, seed=5
        )

    def test_welch_ttest_detects_a_large_difference(self):
        group_a = [2.0, 1.8, 2.2, 1.9, 2.1, 2.0, 1.7, 2.3]
        group_b = [-1.0, -1.1, -0.9, -1.0, -1.2, -0.8, -1.0, -1.05]
        t, p = welch_ttest(group_a, group_b)
        assert t > 10
        assert p < 0.001

    def test_welch_ttest_is_flat_for_identical_samples(self):
        t, p = welch_ttest([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
        assert t == pytest.approx(0.0)
        assert p == pytest.approx(1.0)

    def test_infinite_profit_factor_is_flagged(self):
        trades = [{"pnl": 1.5, "risk_amount": 1.0, "date": "2026-09-01"} for _ in range(5)]
        report = compute_performance(trades)
        assert math.isinf(report.profit_factor)
        assert any("infinite" in w for w in report.warnings)
