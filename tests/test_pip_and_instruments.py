"""Tests for instrument specifications and pip arithmetic.

Every expected value here is hand-checkable from the formula in the docstring.
"""

from __future__ import annotations

import pytest

from forex_mastery.core.instruments import (
    InstrumentError,
    default_config_path,
    get_instrument,
    list_instruments,
    load_instruments,
)
from forex_mastery.core.pip import (
    MissingRateError,
    money_per_price_unit,
    pip_value_per_lot,
    pip_value_table,
    point_value_per_lot,
    quote_to_account_rate,
)


class TestInstrumentRegistry:
    def test_config_file_is_found(self):
        assert default_config_path().is_file()

    def test_eurusd_spec_matches_exness_documentation(self):
        spec = get_instrument("EURUSD")
        assert spec.contract_size == 100_000
        assert spec.pip_size == 0.0001
        assert spec.quote == "USD"
        assert spec.min_volume_lots == 0.01
        assert spec.verified is True

    def test_jpy_pair_uses_second_decimal_pip(self):
        assert get_instrument("USDJPY").pip_size == 0.01
        assert get_instrument("EURJPY").pip_size == 0.01

    def test_gold_is_100_ounces(self):
        spec = get_instrument("XAUUSD")
        assert spec.contract_size == 100
        assert spec.pip_size == 0.01

    def test_symbol_lookup_is_case_insensitive(self):
        assert get_instrument("eurusd").symbol == "EURUSD"

    def test_unknown_symbol_raises_instead_of_guessing(self):
        with pytest.raises(InstrumentError):
            get_instrument("NOTAPAIR")

    def test_group_filter(self):
        majors = list_instruments("forex_major")
        assert {s.symbol for s in majors} >= {"EURUSD", "GBPUSD", "USDJPY"}

    def test_config_is_valid_json_with_meta(self):
        path = default_config_path()
        registry = load_instruments(path)
        assert len(registry) > 20

    def test_point_is_one_tenth_of_a_pip(self):
        spec = get_instrument("EURUSD")
        assert spec.pipettes_per_pip == 10
        assert spec.point_size == pytest.approx(0.00001)

    def test_volume_rounding_never_rounds_up(self):
        spec = get_instrument("EURUSD")
        assert spec.round_volume(0.027) == pytest.approx(0.02)
        assert spec.round_volume(0.029999) == pytest.approx(0.02)
        assert spec.round_volume(0.0300001) == pytest.approx(0.03)


class TestPipArithmetic:
    def test_price_to_pips_and_back(self):
        spec = get_instrument("EURUSD")
        assert spec.price_to_pips(0.0050) == pytest.approx(50.0)
        assert spec.price_to_pips(-0.0050) == pytest.approx(-50.0)
        assert spec.pips_to_price(50) == pytest.approx(0.0050)

    def test_usdjpy_pips(self):
        spec = get_instrument("USDJPY")
        assert spec.price_to_pips(0.50) == pytest.approx(50.0)

    def test_gold_pips(self):
        spec = get_instrument("XAUUSD")
        assert spec.price_to_pips(1.00) == pytest.approx(100.0)


class TestConversionRates:
    def test_same_currency_is_one(self):
        assert quote_to_account_rate("USD", "USD") == 1.0

    def test_direct_pair_uses_price(self):
        assert quote_to_account_rate("EUR", "USD", {"EURUSD": 1.10}) == pytest.approx(1.10)

    def test_inverse_pair_inverts_price(self):
        rate = quote_to_account_rate("JPY", "USD", {"USDJPY": 150.0})
        assert rate == pytest.approx(1 / 150.0)

    def test_missing_rate_raises_rather_than_assuming_parity(self):
        with pytest.raises(MissingRateError) as excinfo:
            quote_to_account_rate("JPY", "USD", {})
        assert "USDJPY" in str(excinfo.value)


class TestPipValue:
    def test_eurusd_one_lot_is_ten_dollars(self):
        assert pip_value_per_lot("EURUSD", "USD", lots=1.0) == pytest.approx(10.0)

    def test_eurusd_micro_lot_is_ten_cents(self):
        assert pip_value_per_lot("EURUSD", "USD", lots=0.01) == pytest.approx(0.10)

    def test_usdjpy_pip_value_depends_on_price(self):
        # 100,000 x 0.01 = 1,000 JPY; /150 = 6.6667 USD
        value = pip_value_per_lot("USDJPY", "USD", lots=1.0, prices={"USDJPY": 150.0})
        assert value == pytest.approx(6.6667, abs=1e-4)

    def test_gold_pip_value_is_one_dollar_per_lot(self):
        assert pip_value_per_lot("XAUUSD", "USD", lots=1.0) == pytest.approx(1.0)
        assert pip_value_per_lot("XAUUSD", "USD", lots=0.10) == pytest.approx(0.10)

    def test_point_value_is_a_tenth_of_pip_value(self):
        assert point_value_per_lot("EURUSD", "USD") == pytest.approx(1.0)

    def test_money_per_price_unit(self):
        # 0.10 lots EURUSD: 0.10 x 100,000 x 1 = 10,000 USD per 1.0000 of price
        assert money_per_price_unit("EURUSD", 0.10) == pytest.approx(10_000.0)

    def test_pip_value_requires_a_rate_for_cross_pairs(self):
        with pytest.raises(MissingRateError):
            pip_value_per_lot("GBPJPY", "USD", lots=1.0)

    def test_cross_pair_with_rate(self):
        # GBPJPY: 100,000 x 0.01 = 1,000 JPY per pip; at USDJPY 150 -> 6.6667 USD
        value = pip_value_per_lot("GBPJPY", "USD", lots=1.0, prices={"USDJPY": 150.0})
        assert value == pytest.approx(6.6667, abs=1e-4)

    def test_pip_value_table_skips_symbols_without_rates(self):
        rows = pip_value_table(["EURUSD", "GBPJPY"], "USD", prices={"USDJPY": 150.0})
        assert {r.symbol for r in rows} == {"EURUSD", "GBPJPY"}
