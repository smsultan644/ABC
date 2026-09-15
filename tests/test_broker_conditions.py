"""Tests for the broker-conditions layer (account types, stop out, HMR, volume)."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from forex_mastery.core.broker import (
    account_type,
    broker_profile,
    format_account_table,
    format_hmr_summary,
    stop_out_level,
    verification_age_days,
)
from forex_mastery.core.validation import InputError

CONFIG = Path(__file__).resolve().parents[1] / "config" / "broker.json"


def test_config_is_valid_json_with_provenance():
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    meta = data["_meta"]
    assert meta["verified_on"] == "2026-09-15"
    # Every source must be an official Exness domain: no forum posts, no review sites.
    for source in meta["sources"]:
        assert "exness.help" in source or "exness.com" in source, source
    assert len(data["account_types"]) == 5


def test_profile_loads_with_five_account_types():
    profile = broker_profile()
    assert profile.verified_on == "2026-09-15"
    keys = [entry.key for entry in profile.account_types]
    assert keys == ["standard_cent", "standard", "pro", "raw_spread", "zero"]
    assert all(entry.verified for entry in profile.account_types)


def test_documented_stop_out_levels():
    # Documented on 2026-09-15: margin call 60% / stop out 0% for Standard and
    # Standard Cent, 30% / 0% for the professional accounts.
    assert stop_out_level("standard") == 0.0
    assert stop_out_level("standard_cent") == 0.0
    assert account_type("standard").margin_call_percent == 60.0
    for key in ("pro", "raw_spread", "zero"):
        assert account_type(key).margin_call_percent == 30.0

    standard = account_type("standard")
    assert standard.stop_out_is_zero is True
    assert "region based" in account_type("raw_spread").minimum_initial_deposit
    # The official page does not publish a Standard minimum deposit figure.
    assert "none stated" in account_type("standard").minimum_initial_deposit


def test_lookup_accepts_names_and_rejects_unknown():
    assert account_type("Raw Spread").key == "raw_spread"
    assert account_type("STANDARD CENT").key == "standard_cent"
    with pytest.raises(InputError) as excinfo:
        account_type("platinum")
    assert "known types" in str(excinfo.value).lower()


def test_verification_age_is_reported_not_guessed():
    assert verification_age_days("2026-12-20") == 96
    assert verification_age_days("not-a-date") is None


def test_account_table_and_hmr_summary_render():
    table = format_account_table()
    for expected in ("Standard Cent", "Standard", "Pro", "Raw Spread", "Zero", "0%"):
        assert expected in table
    assert "region based" in table

    hmr = format_hmr_summary()
    assert "HMR" in hmr
    assert "3 hours before a weekend close" in hmr
    assert "90 seconds" in hmr
    assert "Interpretation" in hmr, "the documentation must be separated from interpretation"


def test_trading_volume_definition_recorded():
    data = broker_profile().data
    volume = data["trading_volume"]
    assert volume["formula"] == "TV = number of lots x contract size"
    assert any("300,000 EUR" in example for example in volume["examples"])


def test_broker_calculator_caveat_recorded():
    calculator = broker_profile().data["broker_calculator"]
    joined = " ".join(calculator["documented_caveats"])
    assert "previous trading day" in joined


def test_cli_broker_command():
    from forex_mastery.cli import main

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["broker", "--account", "standard", "--hmr"])
    output = buffer.getvalue()
    assert code == 0
    assert "stop out" in output.lower()
    assert "0%" in output
    lowered = output.lower()
    for forbidden in ("buy now", "sell now", "guaranteed profit", "risk-free"):
        assert forbidden not in lowered
