"""Tests for position sizing, margin and the risk / drawdown mathematics."""

from __future__ import annotations

import math

import pytest

from forex_mastery.core.margin import (
    adverse_move_impact,
    effective_leverage,
    free_margin,
    margin_level_percent,
    notional_value,
    price_at_equity,
    required_margin,
)
from forex_mastery.core.position_size import (
    PositionSizeRequest,
    calculate_position_size,
    risk_level_scenarios,
)
from forex_mastery.core.risk import (
    breakeven_win_rate,
    break_even_win_rate_with_costs,
    consecutive_loss_probability,
    drawdown_ladder,
    drawdown_percent,
    expectancy_currency,
    expectancy_r,
    kelly_fraction,
    losing_streak_probabilities,
    max_drawdown_percent,
    portfolio_heat,
    r_multiple,
    recovery_gain_required,
    risk_reward,
)
from forex_mastery.core.validation import InputError, require_positive


class TestPositionSizing:
    def test_eurusd_1000_account_one_percent(self):
        """1000 USD, 1% risk = 10 USD; 20-pip stop at 10 USD/pip per lot -> 0.05 lots."""
        res = calculate_position_size(
            PositionSizeRequest("EURUSD", balance=1000, entry=1.1000, stop=1.0980, risk_percent=1.0)
        )
        assert res.ok
        assert res.risk_target_amount == pytest.approx(10.0)
        assert res.stop_pips == pytest.approx(20.0)
        assert res.risk_per_lot == pytest.approx(200.0)
        assert res.lots_exact == pytest.approx(0.05)
        assert res.lots == pytest.approx(0.05)
        assert res.actual_risk_amount == pytest.approx(10.0)

    def test_gold_sizing(self):
        """1000 USD at 0.5% = 5 USD; XAUUSD 100-pip stop (1.00) = 100 USD/lot -> 0.05 lots."""
        res = calculate_position_size(
            PositionSizeRequest(
                "XAUUSD", balance=1000, entry=2400.00, stop=2399.00, risk_percent=0.5
            )
        )
        assert res.ok
        assert res.pip_value_per_lot == pytest.approx(1.0)
        assert res.stop_pips == pytest.approx(100.0)
        assert res.risk_per_lot == pytest.approx(100.0)
        assert res.lots_exact == pytest.approx(0.05)

    def test_usdjpy_sizing_requires_and_uses_the_conversion_rate(self):
        """1000 USD, 1% = 10 USD; 30-pip stop; pip value 6.6667 USD/lot -> 0.05 lots."""
        res = calculate_position_size(
            PositionSizeRequest(
                "USDJPY",
                balance=1000,
                entry=150.00,
                stop=149.70,
                risk_percent=1.0,
                prices={"USDJPY": 150.0},
            )
        )
        assert res.ok
        assert res.pip_value_per_lot == pytest.approx(6.6667, abs=1e-4)
        assert res.lots_exact == pytest.approx(0.05, abs=1e-4)

    def test_short_trade_direction_inference(self):
        res = calculate_position_size(
            PositionSizeRequest("EURUSD", balance=1000, entry=1.1000, stop=1.1050, risk_percent=0.5)
        )
        assert res.direction == "short"
        assert res.lots_exact == pytest.approx(0.01)

    def test_take_profit_and_rr(self):
        res = calculate_position_size(
            PositionSizeRequest(
                "EURUSD",
                balance=1000,
                entry=1.1000,
                stop=1.0980,
                take_profit=1.1040,
                risk_percent=0.5,
                min_risk_reward=1.5,
            )
        )
        assert res.rr == pytest.approx(2.0)
        assert res.reward_pips == pytest.approx(40.0)
        # 5.00 USD risk budget / (20 pips x 10 USD) = 0.025 lots -> rounded DOWN to 0.02
        assert res.lots == pytest.approx(0.02)
        # 40 pips x 10 USD x 0.02 lots = 8.00 USD of potential profit
        assert res.potential_profit == pytest.approx(8.0)

    def test_tp_on_wrong_side_is_an_error(self):
        res = calculate_position_size(
            PositionSizeRequest(
                "EURUSD", balance=1000, entry=1.1000, stop=1.0980, take_profit=1.0950, risk_percent=0.5
            )
        )
        assert not res.ok
        assert any(d.code == "tp_wrong_side" for d in res.diagnostics.errors)

    def test_minimum_lot_problem_is_reported_honestly(self):
        """A 250 USD account risking 0.5% cannot size a 40-pip EURUSD stop.

        0.5% of 250 = 1.25 USD; 40 pips x 10 USD = 400 USD/lot -> 0.003125 lots,
        below the 0.01 minimum. The tool must refuse rather than silently
        rounding up to a trade that risks 1.6% of equity.
        """
        res = calculate_position_size(
            PositionSizeRequest(
                "EURUSD", balance=250, entry=1.1000, stop=1.0960, risk_percent=0.5, max_risk_percent=1.0
            )
        )
        assert not res.ok
        assert res.lots == 0.0
        assert any(d.code == "below_min_lot" for d in res.diagnostics.errors)
        assert "0.01" in res.report()

    def test_rounding_down_reduces_actual_risk(self):
        """Risk 1% of 250 = 2.50 USD with a 15-pip stop: 2.50/150 = 0.0167 -> 0.01 lots."""
        res = calculate_position_size(
            PositionSizeRequest("EURUSD", balance=250, entry=1.1000, stop=1.0985, risk_percent=1.0)
        )
        assert res.lots == pytest.approx(0.01)
        assert res.actual_risk_amount == pytest.approx(1.50)
        assert res.actual_risk_percent == pytest.approx(0.6, abs=0.01)

    def test_risk_above_house_limit_warns(self):
        res = calculate_position_size(
            PositionSizeRequest("EURUSD", balance=1000, entry=1.1000, stop=1.0980, risk_percent=2.0)
        )
        assert any(d.code == "risk_above_house_limit" for d in res.diagnostics.warnings)

    def test_absurd_risk_is_an_error(self):
        res = calculate_position_size(
            PositionSizeRequest("EURUSD", balance=1000, entry=1.1000, stop=1.0980, risk_percent=20.0)
        )
        assert not res.ok
        assert any(d.code == "risk_absurd" for d in res.diagnostics.errors)

    def test_tight_stop_against_spread_warns(self):
        res = calculate_position_size(
            PositionSizeRequest(
                "EURUSD", balance=1000, entry=1.1000, stop=1.0998, risk_percent=0.5, spread_pips=1.2
            )
        )
        assert any(d.code == "stop_vs_spread" for d in res.diagnostics.warnings)

    def test_margin_and_effective_leverage_are_reported(self):
        """250 USD, 1% risk = 2.50 USD budget; a 10-pip stop allows 0.02 lots."""
        res = calculate_position_size(
            PositionSizeRequest(
                "EURUSD",
                balance=250,
                entry=1.1000,
                stop=1.0990,
                risk_percent=1.0,
                leverage=2000,
            )
        )
        assert res.lots == pytest.approx(0.02)
        # 0.02 lots x 100,000 x 1.10 = 2,200 USD notional; /2000 = 1.10 margin
        assert res.margin_required == pytest.approx(1.10, abs=0.01)
        assert res.notional == pytest.approx(2200.0)
        assert res.effective_leverage == pytest.approx(8.8, abs=0.05)

    def test_risk_scenario_table(self):
        rows = risk_level_scenarios("EURUSD", 250, 1.1000, 1.0975, risk_percents=(0.25, 1.0))
        assert [r.risk_percent for r in rows] == [0.25, 1.0]
        assert rows[0].risk_amount == pytest.approx(0.625)
        assert rows[1].risk_amount == pytest.approx(2.50)
        # 25-pip stop: 1 USD risk / 250 USD per lot = 0.004 -> below min lot
        assert rows[0].lots == 0.0

    def test_zero_stop_distance_is_rejected(self):
        res = calculate_position_size(
            PositionSizeRequest("EURUSD", balance=1000, entry=1.1, stop=1.1, risk_percent=0.5)
        )
        assert not res.ok
        assert any(d.code == "zero_stop" for d in res.diagnostics.errors)

    def test_risk_amount_overrides_percent_and_warns(self):
        res = calculate_position_size(
            PositionSizeRequest(
                "EURUSD",
                balance=1000,
                entry=1.1000,
                stop=1.0980,
                risk_percent=0.5,
                risk_amount=10.0,
            )
        )
        assert res.risk_target_amount == pytest.approx(10.0)
        assert any(d.code == "both_risk_inputs" for d in res.diagnostics.warnings)


class TestMargin:
    def test_required_margin_formula(self):
        # 0.01 lots: 1,000 EUR notional at 1.1000 = 1,100 USD ; /2000 = 0.55
        assert required_margin("EURUSD", 0.01, 1.1000, 2000) == pytest.approx(0.55)

    def test_notional_value_uses_contract_size(self):
        assert notional_value("EURUSD", 1.0, 1.1000) == pytest.approx(110_000.0)
        assert notional_value("XAUUSD", 1.0, 2400.0) == pytest.approx(240_000.0)

    def test_margin_level_infinite_without_positions(self):
        assert margin_level_percent(250.0, 0.0) == math.inf

    def test_margin_level_and_free_margin(self):
        assert margin_level_percent(100.0, 200.0) == pytest.approx(50.0)
        assert free_margin(100.0, 200.0) == pytest.approx(-100.0)

    def test_price_at_equity_zero_balance_loss(self):
        # 0.10 lots EURUSD from 1.1000: 250 USD loss = 0.0250 of price
        assert price_at_equity("EURUSD", 0.10, 1.1000, 250.0, 0.0) == pytest.approx(1.0750)

    def test_effective_leverage(self):
        # 0.05 lots XAUUSD at 2,400 = 12,000 notional on 250 equity = 48:1
        assert effective_leverage("XAUUSD", 0.05, 2400.0, 250.0) == pytest.approx(48.0)

    def test_adverse_move_impact_shows_leverage_danger(self):
        impact = adverse_move_impact("XAUUSD", 0.50, 1.0, 250.0, price=2400.0)
        # 1% of 2,400 = 24.00 price move; 0.50 lots x 100 oz x 24 = 1,200 USD
        assert impact["money_loss"] == pytest.approx(1200.0)
        assert impact["equity_after"] == pytest.approx(-950.0)


class TestRiskMaths:
    def test_r_multiple(self):
        assert r_multiple(31.0, 12.5) == pytest.approx(2.48)
        assert r_multiple(-12.5, 12.5) == pytest.approx(-1.0)

    def test_risk_reward_long_and_short(self):
        assert risk_reward(1.1000, 1.0950, 1.1150, "long") == pytest.approx(3.0)
        assert risk_reward(1.1000, 1.1050, 1.0900, "short") == pytest.approx(2.0)

    def test_risk_reward_rejects_impossible_levels(self):
        with pytest.raises(InputError):
            risk_reward(1.1000, 1.0950, 1.0900, "long")
        with pytest.raises(InputError):
            risk_reward(1.1000, 1.0950, 1.1150, "sideways")

    def test_breakeven_win_rates(self):
        assert breakeven_win_rate(1.0) == pytest.approx(0.50)
        assert breakeven_win_rate(2.0) == pytest.approx(1 / 3)
        assert breakeven_win_rate(3.0) == pytest.approx(0.25)
        assert breakeven_win_rate(0.5) == pytest.approx(2 / 3)

    def test_breakeven_win_rate_with_costs_is_stricter(self):
        assert break_even_win_rate_with_costs(2.0, 0.0) == pytest.approx(1 / 3)
        # costs shift the required win rate up
        assert break_even_win_rate_with_costs(2.0, 0.1) > 1 / 3

    def test_expectancy_r_three_ways(self):
        assert expectancy_r(0.40, 2.5) == pytest.approx(0.40)
        assert expectancy_r(0.70, 1.0) == pytest.approx(0.40)
        assert expectancy_r(0.45, 1.5, 1.5) == pytest.approx(-0.15)

    def test_expectancy_currency(self):
        assert expectancy_currency(0.40, 25.0, 10.0) == pytest.approx(4.0)

    def test_drawdown_percent_and_recovery(self):
        assert drawdown_percent(275.0, 233.75) == pytest.approx(15.0)
        assert recovery_gain_required(5.0) == pytest.approx(5.263, abs=1e-3)
        assert recovery_gain_required(10.0) == pytest.approx(11.111, abs=1e-3)
        assert recovery_gain_required(20.0) == pytest.approx(25.0)
        assert recovery_gain_required(30.0) == pytest.approx(42.857, abs=1e-3)
        assert recovery_gain_required(50.0) == pytest.approx(100.0)

    def test_max_drawdown_of_equity_curve(self):
        curve = [250, 260, 255, 300, 280, 270, 275]
        dd, peak_idx, trough_idx = max_drawdown_percent(curve)
        assert dd == pytest.approx(10.0)
        assert curve[peak_idx] == 300
        assert curve[trough_idx] == 270

    def test_drawdown_ladder_counts_are_compounding_correct(self):
        rows = {r.drawdown_percent: r for r in drawdown_ladder()}
        # ceil(ln(0.9)/ln(0.99)) = 11 losses at 1% risk for a 10% drawdown
        assert rows[10.0].losses_at_1_00_pct == 11
        # ceil(ln(0.9)/ln(0.995)) = 22 losses at 0.5% risk
        assert rows[10.0].losses_at_0_50_pct == 22
        # ceil(ln(0.5)/ln(0.995)) = 139 losses at 0.5% risk for -50%
        assert rows[50.0].losses_at_0_50_pct == 139

    def test_streak_probability_matches_brute_force(self):
        """DP result must equal exhaustive enumeration on a small case."""
        import itertools

        p = 0.5
        trades, k = 5, 2
        hits = 0
        total = 0
        for seq in itertools.product([1, 0], repeat=trades):  # 1 = win, 0 = loss
            total += 1
            run = 0
            for s in seq:
                run = 0 if s == 1 else run + 1
                if run >= k:
                    hits += 1
                    break
        brute = hits / total
        assert consecutive_loss_probability(p, k, trades) == pytest.approx(brute, abs=1e-9)

    def test_losing_streak_probabilities_increase_with_k_and_trades(self):
        probs = dict(losing_streak_probabilities(0.45, 8, trades=100))
        assert probs[2] > probs[4] > probs[6] > probs[8]
        shorter = dict(losing_streak_probabilities(0.45, 8, trades=20))
        assert shorter[6] < probs[6]

    def test_kelly_is_negative_without_edge(self):
        assert kelly_fraction(0.30, 2.0) < 0
        assert kelly_fraction(0.50, 2.0) == pytest.approx(0.25)

    def test_portfolio_heat(self):
        heat = portfolio_heat([1.25, 1.25, 2.50])
        assert heat["total_risk"] == pytest.approx(5.0)
        assert heat["max_single_risk"] == pytest.approx(2.5)


class TestValidation:
    def test_require_positive_rejects_bad_input(self):
        with pytest.raises(InputError):
            require_positive(entry=-1.0)
        with pytest.raises(InputError):
            require_positive(entry=0.0)
        with pytest.raises(InputError):
            require_positive(entry=float("nan"))
        with pytest.raises(InputError):
            require_positive(entry="1.10")
        require_positive(entry=1.10)
