"""Tests for session timing (including DST) and the rule engine."""

from __future__ import annotations

import datetime as dt

import pytest

from forex_mastery.core.rule_engine import (
    RULE_TYPES,
    SetupContext,
    evaluate_setup,
    load_rules,
)
from forex_mastery.core.sessions import (
    SESSION_DEFINITIONS,
    active_sessions,
    current_overlaps,
    format_session_table,
    is_low_liquidity_lull,
    is_market_open,
    next_session_open,
    session_liquidity_rank,
    session_table,
    session_window_utc,
)

UTC = dt.timezone.utc


class TestSessionWindows:
    def test_london_winter_is_0800_utc(self):
        window = session_window_utc("London", dt.date(2026, 1, 15))
        assert window.start_utc.hour == 8
        assert window.end_utc.hour == 17

    def test_london_summer_is_0700_utc(self):
        window = session_window_utc("London", dt.date(2026, 7, 15))
        assert window.start_utc.hour == 7
        assert window.end_utc.hour == 16

    def test_new_york_moves_with_us_daylight_saving(self):
        january = session_window_utc("New York", dt.date(2026, 1, 15))
        july = session_window_utc("New York", dt.date(2026, 7, 15))
        assert january.start_utc.hour == 13
        assert july.start_utc.hour == 12

    def test_tokyo_does_not_change_because_japan_has_no_dst(self):
        assert session_window_utc("Tokyo", dt.date(2026, 1, 15)).start_utc.hour == 0
        assert session_window_utc("Tokyo", dt.date(2026, 7, 15)).start_utc.hour == 0

    def test_active_sessions_in_winter_overlap(self):
        when = dt.datetime(2026, 1, 15, 14, 0, tzinfo=UTC)
        assert active_sessions(when) == ["London", "New York"]
        assert current_overlaps(when) == ["London/New York"]

    def test_active_sessions_in_asian_window(self):
        """Sydney (21:00-06:00 UTC in its summer) and Tokyo (00:00-09:00 UTC) both cover 02:00."""
        when = dt.datetime(2026, 1, 15, 2, 0, tzinfo=UTC)
        assert active_sessions(when) == ["Sydney", "Tokyo"]

    def test_asian_window_is_flagged_as_low_liquidity_despite_being_open(self):
        """A session being *open* is not the same as liquidity being present.

        This distinction matters: the NY-close-to-Tokyo window still has Sydney
        open, so naive 'is a session open?' logic would wrongly treat 22:30 UTC
        as a good trading hour.
        """
        when = dt.datetime(2026, 1, 15, 22, 30, tzinfo=UTC)
        assert active_sessions(when) == ["Sydney"]
        assert is_low_liquidity_lull(when) is True
        assert session_liquidity_rank(when)["liquidity_score"] == 1

    def test_naive_datetime_is_treated_as_utc(self):
        assert active_sessions(dt.datetime(2026, 1, 15, 14, 0)) == ["London", "New York"]

    def test_next_session_open(self):
        when = dt.datetime(2026, 1, 15, 23, 0, tzinfo=UTC)
        window = next_session_open(when, "Tokyo")
        assert window.name == "Tokyo"
        assert window.start_utc > when

    def test_session_table_has_all_four_sessions(self):
        rows = session_table(dt.date(2026, 1, 15), display_tz="UTC")
        assert [r["session"] for r in rows] == list(SESSION_DEFINITIONS)
        assert "FOREX SESSIONS" in format_session_table(dt.date(2026, 1, 15))

    def test_all_definitions_have_valid_timezones(self):
        from zoneinfo import ZoneInfo

        for name, spec in SESSION_DEFINITIONS.items():
            ZoneInfo(spec["tz"])  # raises if the tz database entry is wrong


class TestMarketOpen:
    def test_saturday_is_closed(self):
        assert not is_market_open(dt.datetime(2026, 9, 12, 12, 0, tzinfo=UTC))

    def test_sunday_before_2100_is_closed_then_opens(self):
        assert not is_market_open(dt.datetime(2026, 9, 13, 19, 0, tzinfo=UTC))
        assert is_market_open(dt.datetime(2026, 9, 13, 22, 0, tzinfo=UTC))

    def test_friday_closes_after_2200_utc(self):
        assert is_market_open(dt.datetime(2026, 9, 11, 20, 0, tzinfo=UTC))
        assert not is_market_open(dt.datetime(2026, 9, 11, 23, 0, tzinfo=UTC))

    def test_weekday_is_open(self):
        assert is_market_open(dt.datetime(2026, 9, 15, 9, 0, tzinfo=UTC))

    def test_liquidity_rank_peaks_in_the_overlap(self):
        overlap = session_liquidity_rank(dt.datetime(2026, 1, 15, 14, 0, tzinfo=UTC))
        quiet = session_liquidity_rank(dt.datetime(2026, 1, 15, 22, 30, tzinfo=UTC))
        assert overlap["liquidity_score"] == 4
        assert quiet["liquidity_score"] == 1
        assert overlap["overlaps"] == ["London/New York"]


def clean_context(**overrides) -> SetupContext:
    """A setup that satisfies every rule, used as the baseline for tests."""
    context = SetupContext(
        symbol="EURUSD",
        direction="long",
        timeframe="4H",
        risk_percent=0.25,
        stop_pips=45.0,
        reward_risk=2.2,
        account_equity=250.0,
        spread_pips=1.2,
        atr_pips=60.0,
        session="London",
        minutes_to_high_impact_news=240,
        minutes_since_high_impact_news=600,
        major_central_bank_event_today=False,
        trades_today=0,
        daily_pnl_percent=0.0,
        weekly_pnl_percent=0.0,
        consecutive_losses=0,
        correlated_positions=0,
        portfolio_heat_percent=0.25,
        higher_timeframe_bias="bullish",
        structure_clear=True,
        level_defined=True,
        invalidation_defined=True,
        entry_trigger_defined=True,
        checklist_complete=True,
        setups_taken_from_plan=True,
        screenshot_taken=True,
        emotional_state="calm",
        slept_well=True,
        had_loss_today=False,
        revenge_urge=False,
        extra={"setup_name": "trend_pullback"},
    )
    for key, value in overrides.items():
        if key in context.extra:
            context.extra[key] = value
        else:
            setattr(context, key, value)
    return context


class TestRuleEngine:
    def test_default_config_loads_and_only_uses_known_rules(self):
        rules = load_rules()
        assert len(rules) >= 15
        assert all(r["type"] in RULE_TYPES for r in rules)

    def test_clean_setup_is_approved(self):
        decision = evaluate_setup(clean_context())
        assert decision.approved, decision.report()
        assert decision.verdict in ("APPROVED", "APPROVED WITH WARNINGS")
        assert not decision.blocking_failures
        assert decision.score == pytest.approx(100.0, abs=0.01)

    def test_risk_above_limit_blocks(self):
        decision = evaluate_setup(clean_context(risk_percent=2.0))
        assert not decision.approved
        assert any("risk_max" in item for item in decision.blocking_failures)

    def test_poor_rr_blocks(self):
        decision = evaluate_setup(clean_context(reward_risk=1.1))
        assert not decision.approved
        assert any("rr_min" in item for item in decision.blocking_failures)

    def test_news_window_blocks(self):
        decision = evaluate_setup(clean_context(minutes_to_high_impact_news=10))
        assert not decision.approved
        assert any("news_blackout" in item for item in decision.blocking_failures)

    def test_unchecked_calendar_is_treated_as_unverified_not_approved(self):
        """The critical design rule: 'I did not check' must not read as 'no news'."""
        decision = evaluate_setup(
            clean_context(minutes_to_high_impact_news=None, minutes_since_high_impact_news=None,
                          major_central_bank_event_today=None)
        )
        assert not decision.approved
        assert decision.unknown
        assert any("news_blackout" in item for item in decision.blocking_failures)

    def test_emotional_state_blocks(self):
        decision = evaluate_setup(clean_context(emotional_state="frustrated"))
        assert not decision.approved
        assert any("psychology" in item for item in decision.blocking_failures)

    def test_revenge_urge_blocks_even_when_calm(self):
        decision = evaluate_setup(clean_context(revenge_urge=True))
        assert not decision.approved

    def test_daily_loss_limit_blocks(self):
        decision = evaluate_setup(clean_context(daily_pnl_percent=-1.2))
        assert not decision.approved
        assert any("daily_loss_limit" in item for item in decision.blocking_failures)

    def test_max_trades_per_day_blocks(self):
        decision = evaluate_setup(clean_context(trades_today=2))
        assert not decision.approved
        assert any("max_trades_day" in item for item in decision.blocking_failures)

    def test_losing_streak_cooldown_blocks(self):
        decision = evaluate_setup(clean_context(consecutive_losses=3))
        assert not decision.approved
        assert any("cooldown" in item for item in decision.blocking_failures)

    def test_correlation_limit_blocks(self):
        decision = evaluate_setup(clean_context(correlated_positions=1))
        assert not decision.approved
        assert any("correlation" in item for item in decision.blocking_failures)

    def test_htf_conflict_blocks(self):
        decision = evaluate_setup(clean_context(higher_timeframe_bias="bearish"))
        assert not decision.approved
        assert any("htf_alignment" in item for item in decision.blocking_failures)

    def test_incomplete_setup_blocks(self):
        decision = evaluate_setup(clean_context(invalidation_defined=False))
        assert not decision.approved
        assert any("setup_complete" in item for item in decision.blocking_failures)

    def test_setup_not_in_plan_blocks(self):
        decision = evaluate_setup(clean_context(setup_name="gut_feeling_scalp"))
        assert not decision.approved
        assert any("in_plan" in item for item in decision.blocking_failures)

    def test_unapproved_instrument_blocks(self):
        decision = evaluate_setup(clean_context(symbol="USDTRY"))
        assert not decision.approved
        assert any("instrument_allowed" in item for item in decision.blocking_failures)

    def test_out_of_session_blocks(self):
        decision = evaluate_setup(clean_context(session="Sydney"))
        assert not decision.approved
        assert any("session_allowed" in item for item in decision.blocking_failures)

    def test_warning_only_rule_does_not_block_but_is_reported(self):
        decision = evaluate_setup(clean_context(spread_pips=5.0))
        assert decision.approved
        assert decision.verdict == "APPROVED WITH WARNINGS"
        assert any("spread_max" in item for item in decision.warnings)

    def test_decision_is_serialisable_for_the_journal(self):
        payload = evaluate_setup(clean_context()).as_dict()
        assert payload["verdict"] and "outcomes" in payload

    def test_custom_rule_set_can_be_passed_directly(self):
        rules = [{
            "type": "max_risk",
            "code": "risk_max",
            "severity": "block",
            "enabled": True,
            "params": {"max_percent": 0.1},
        }]
        assert not evaluate_setup(clean_context(risk_percent=0.25), rules).approved
        assert evaluate_setup(clean_context(risk_percent=0.05), rules).approved
