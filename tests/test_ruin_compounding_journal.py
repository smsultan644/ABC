"""Tests for risk of ruin, compounding projections and the journal model."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from forex_mastery.core.compounding import (
    drawdown_recovery_trades,
    growth_rate_per_trade,
    project_equity,
    risk_level_growth_table,
    trades_to_target,
)
from forex_mastery.core.risk_of_ruin import (
    risk_of_ruin_fixed_fraction_analytic,
    risk_of_ruin_fixed_stake,
    simulate_risk_of_ruin,
)
from forex_mastery.core.validation import InputError
from forex_mastery.journal.model import (
    Direction,
    SetupQuality,
    TradeRecord,
    TradeStatus,
)
from forex_mastery.journal.storage import JournalStore


class TestRiskOfRuin:
    def test_fixed_stake_with_no_edge_ruins_you(self):
        assert risk_of_ruin_fixed_stake(0.50, 1.0, 1.0, 10.0) == pytest.approx(1.0)

    def test_fixed_stake_with_edge_is_small(self):
        # ratio = (1 x 0.45) / (1 x 0.55) = 0.81818; n = 20 -> ratio**20
        expected = ((1 * 0.45) / (1 * 0.55)) ** 20
        assert risk_of_ruin_fixed_stake(0.55, 1.0, 1.0, 20.0) == pytest.approx(expected)
        assert expected == pytest.approx(0.0180, abs=0.001)

    def test_bigger_bankroll_reduces_ruin(self):
        small = risk_of_ruin_fixed_stake(0.55, 1.0, 1.0, 10.0)
        large = risk_of_ruin_fixed_stake(0.55, 1.0, 1.0, 40.0)
        assert large < small

    def test_analytic_lower_bound_for_fixed_fraction(self):
        # 1% risk, 0.25% ... n = ceil(ln(0.5)/ln(0.99)) = 69 consecutive losses
        value = risk_of_ruin_fixed_fraction_analytic(0.45, 1.5, 0.01, 0.5)
        assert value == pytest.approx(0.55 ** 69, rel=1e-6)
        assert value < 1e-15

    def test_monte_carlo_is_reproducible(self):
        a = simulate_risk_of_ruin(0.45, 1.5, 0.005, trades=100, paths=300, seed=99)
        b = simulate_risk_of_ruin(0.45, 1.5, 0.005, trades=100, paths=300, seed=99)
        assert a.ruin_probability == b.ruin_probability
        assert a.median_final_equity == b.median_final_equity

    def test_higher_risk_produces_more_ruin_and_deeper_drawdowns(self):
        low = simulate_risk_of_ruin(0.45, 1.5, 0.0025, trades=400, paths=1500, seed=5)
        high = simulate_risk_of_ruin(0.45, 1.5, 0.05, trades=400, paths=1500, seed=5)
        assert high.ruin_probability > low.ruin_probability
        assert high.percentile_95_max_drawdown_pct > low.percentile_95_max_drawdown_pct

    def test_negative_edge_ruins_a_high_risk_framework_almost_surely(self):
        result = simulate_risk_of_ruin(0.30, 1.0, 0.02, trades=500, paths=800, seed=3)
        assert result.ruin_probability > 0.9

    def test_median_outcome_improves_with_a_real_edge(self):
        result = simulate_risk_of_ruin(0.45, 2.0, 0.005, trades=300, paths=800, seed=8,
                                       starting_equity=250.0)
        assert result.median_final_equity > 250.0
        assert result.mean_final_equity >= result.median_final_equity  # right-skewed

    def test_costs_reduce_the_outcome(self):
        free = simulate_risk_of_ruin(0.45, 1.5, 0.005, trades=200, paths=500, seed=4, cost_in_r=0.0)
        costly = simulate_risk_of_ruin(0.45, 1.5, 0.005, trades=200, paths=500, seed=4, cost_in_r=0.15)
        assert costly.median_final_equity < free.median_final_equity

    def test_report_renders(self):
        text = simulate_risk_of_ruin(0.45, 1.5, 0.005, trades=100, paths=200, seed=1).report()
        assert "RISK OF RUIN" in text

    def test_invalid_risk_is_rejected(self):
        with pytest.raises(InputError):
            simulate_risk_of_ruin(0.45, 1.5, 0.75)


class TestCompounding:
    def test_growth_rate_sign_follows_the_edge(self):
        assert growth_rate_per_trade(0.45, 2.0, 0.005) > 0
        assert growth_rate_per_trade(0.30, 1.0, 0.005) < 0
        # At exactly 50% with 1R targets and fixed-fractional risk the expectation is
        # marginally negative before costs: the compounding of a -0.5% loss needs
        # slightly more than +0.5% to recover.
        assert growth_rate_per_trade(0.50, 1.0, 0.005) == pytest.approx(-1.25e-5, abs=1e-6)

    def test_growth_rate_matches_manual_computation(self):
        p, r, f = 0.45, 2.0, 0.005
        expected = p * math.log(1 + f * r) + (1 - p) * math.log(1 - f)
        assert growth_rate_per_trade(p, r, f) == pytest.approx(expected)

    def test_costs_lower_growth(self):
        assert growth_rate_per_trade(0.45, 2.0, 0.005, cost_in_r=0.1) < growth_rate_per_trade(
            0.45, 2.0, 0.005
        )

    def test_projection_scales_with_trades(self):
        hundred = project_equity(0.45, 2.0, 0.005, trades=100, starting_equity=250)
        two_hundred = project_equity(0.45, 2.0, 0.005, trades=200, starting_equity=250)
        assert two_hundred.median_final_equity > hundred.median_final_equity
        assert hundred.median_final_equity == pytest.approx(
            250 * math.exp(growth_rate_per_trade(0.45, 2.0, 0.005) * 100)
        )

    def test_no_edge_yields_no_growth(self):
        projection = project_equity(0.40, 1.5, 0.005, trades=250, starting_equity=250)
        # break-even win rate at 1.5R is 40%; expectancy is ~0 before costs
        assert projection.median_final_equity == pytest.approx(250.0, rel=0.01)

    def test_trades_to_target_is_infinite_without_edge(self):
        assert trades_to_target(0.30, 1.0, 0.005, 2.0) == math.inf
        assert trades_to_target(0.45, 2.0, 0.005, 2.0) > 0

    def test_recovery_takes_longer_than_the_drawdown_itself(self):
        trades = drawdown_recovery_trades(0.45, 2.0, 0.005, 20.0)
        assert trades > 100

    def test_risk_level_table_quantifies_drawdown_tradeoff(self):
        rows = risk_level_growth_table(0.45, 2.0, (0.0025, 0.05), trades=250, starting_equity=250)
        # Higher risk produces BOTH a bigger median (positive expectancy compounds
        # faster) and a far deeper probable drawdown. That trade-off - not "risk is
        # always bad" - is what the table exists to show.
        assert rows[1]["drawdown_from_that_streak_pct"] > rows[0]["drawdown_from_that_streak_pct"]
        assert rows[1]["median_final_equity"] > rows[0]["median_final_equity"]
        # The streak itself is identical across risk levels - only its consequence
        # differs. This is the point: risk changes the damage, not the odds.
        assert rows[1]["p95_losing_streak"] == rows[0]["p95_losing_streak"]

    def test_projection_report_contains_caveats(self):
        text = project_equity(0.45, 2.0, 0.005, trades=250).report()
        assert "CAVEATS" in text


class TestTradeRecord:
    def make(self, **overrides) -> TradeRecord:
        base = dict(
            trade_id="T-0001",
            date="2026-09-15",
            symbol="EURUSD",
            direction="long",
            entry=1.1000,
            stop_loss=1.0950,
            take_profit=1.1100,
            lots=0.01,
            account_equity_at_entry=250.0,
            risk_percent=0.5,
            planned_rr=2.0,
        )
        base.update(overrides)
        return TradeRecord(**base)

    def test_risk_amount_derived_from_percent_and_equity(self):
        trade = self.make()
        assert trade.risk_amount == pytest.approx(1.25)

    def test_direction_string_is_coerced_to_enum(self):
        assert self.make(direction="short").direction is Direction.SHORT

    def test_r_multiple_is_computed_not_typed(self):
        trade = self.make()
        trade.pnl = 3.75
        assert trade.r_multiple == pytest.approx(3.0)

    def test_status_inferred_from_pnl(self):
        trade = self.make(pnl=2.0)
        assert trade.status is TradeStatus.WIN
        assert self.make(pnl=-2.0).status is TradeStatus.LOSS
        assert self.make(pnl=0.0).status is TradeStatus.BREAKEVEN

    def test_open_trade_has_no_r_multiple(self):
        assert self.make().r_multiple is None
        assert not self.make().is_closed

    def test_net_pnl_subtracts_costs(self):
        trade = self.make(pnl=2.50, commission=0.07, swap=-0.02)
        assert trade.net_pnl == pytest.approx(2.50 - 0.07 + 0.02)

    def test_rule_violations_are_split_for_analysis(self):
        trade = self.make(rule_violations="moved stop; traded during news, risk too high")
        assert trade.violations_list() == ["moved stop", "traded during news", "risk too high"]

    def test_stop_distance_and_planned_reward(self):
        trade = self.make()
        assert trade.stop_distance == pytest.approx(0.0050)
        assert trade.planned_reward_distance == pytest.approx(0.0100)

    def test_row_round_trip_preserves_values(self):
        trade = self.make(pnl=3.75, status="win", setup_quality="A", session="London")
        row = trade.to_row()
        restored = TradeRecord.from_row(row)
        assert restored.pnl == pytest.approx(3.75)
        assert restored.r_multiple == pytest.approx(3.0)
        assert restored.setup_quality is SetupQuality.A
        assert restored.direction is Direction.LONG

    def test_from_row_requires_mandatory_fields(self):
        with pytest.raises(ValueError):
            TradeRecord.from_row({"trade_id": "T1", "date": "2026-09-15"})

    def test_unknown_columns_are_preserved_in_extra(self):
        row = self.make().to_row()
        row["my_custom_field"] = "keep me"
        assert TradeRecord.from_row(row).extra["my_custom_field"] == "keep me"


class TestJournalStore:
    def test_add_load_and_summary(self, tmp_path: Path):
        store = JournalStore(tmp_path / "journal.csv")
        trade = TradeRecord(
            trade_id="T-0001", date="2026-09-15", symbol="EURUSD", direction="long",
            entry=1.1000, stop_loss=1.0950, lots=0.01, account_equity_at_entry=250.0,
            risk_percent=0.5, pnl=1.25, status="win",
        )
        store.add(trade)
        loaded = store.load()
        assert len(loaded) == 1
        assert loaded[0].r_multiple == pytest.approx(1.0)
        summary = store.summary()
        assert summary["closed"] == 1
        assert summary["net_pnl"] == pytest.approx(1.25)
        assert summary["win_rate"] == pytest.approx(100.0)

    def test_headers_exist_even_when_empty(self, tmp_path: Path):
        store = JournalStore(tmp_path / "empty.csv")
        store.ensure_template()
        text = (tmp_path / "empty.csv").read_text()
        assert "trade_id" in text and "r_multiple" in text
        assert store.load() == []

    def test_sequential_ids(self, tmp_path: Path):
        store = JournalStore(tmp_path / "journal.csv")
        assert store.next_trade_id() == "T-0001"
        store.add(TradeRecord(trade_id="T-0007", date="2026-09-15", symbol="EURUSD",
                              direction="long", entry=1.1, stop_loss=1.09))
        assert store.next_trade_id() == "T-0008"

    def test_update_and_close(self, tmp_path: Path):
        store = JournalStore(tmp_path / "journal.csv")
        store.add(TradeRecord(trade_id="T-1", date="2026-09-15", symbol="EURUSD",
                              direction="short", entry=1.1000, stop_loss=1.1050,
                              account_equity_at_entry=250.0, risk_percent=0.5))
        closed = store.close_trade("T-1", exit_price=1.0900, pnl=2.5,
                                   reason_for_exit="target hit", thesis_valid=True)
        assert closed.status is TradeStatus.WIN
        assert closed.r_multiple == pytest.approx(2.0)
        assert store.summary()["closed"] == 1

    def test_missing_file_returns_empty_list(self, tmp_path: Path):
        assert JournalStore(tmp_path / "nope.csv").load() == []

    def test_json_round_trip(self, tmp_path: Path):
        store = JournalStore(tmp_path / "journal.csv")
        store.add(TradeRecord(trade_id="T-1", date="2026-09-15", symbol="XAUUSD",
                              direction="long", entry=2400.0, stop_loss=2395.0,
                              risk_amount=2.5, pnl=-2.5, status="loss"))
        target = store.export_json(tmp_path / "journal.json")
        assert target.is_file()
        other = JournalStore(tmp_path / "other.csv")
        other.import_json(target, replace=True)
        assert len(other.load()) == 1
        assert other.load()[0].symbol == "XAUUSD"

    def test_write_is_atomic_and_leaves_no_temp_files(self, tmp_path: Path):
        store = JournalStore(tmp_path / "journal.csv")
        store.write([TradeRecord(trade_id="T-1", date="2026-09-15", symbol="EURUSD",
                                 direction="long", entry=1.1, stop_loss=1.09)])
        leftovers = [p for p in tmp_path.iterdir() if p.suffix == ".tmp"]
        assert leftovers == []
