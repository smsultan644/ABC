"""Tests for the candle-pattern statistics module.

All bars here are SYNTHETIC constructions written to exercise the code paths.
They are not market data, they are not a backtest, and they say nothing about any
instrument. The point of these tests is the arithmetic and the guard rails, not
the patterns.
"""

from __future__ import annotations

import csv
import io
import random
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from forex_mastery.core.candles import (
    PATTERN_NAMES,
    Bar,
    analyse_pattern,
    classify_bar,
    load_bars_csv,
    pattern_description,
)
from forex_mastery.core.validation import InputError


def bar(index: int, o: float, h: float, l: float, c: float, date: str = "") -> Bar:
    return Bar(index=index, date=date or f"2026-01-{index + 1:02d}", open=o, high=h, low=l, close=c)


# --------------------------------------------------------------------- #
# Geometry
# --------------------------------------------------------------------- #
def test_bar_geometry():
    candle = bar(0, o=1.1000, h=1.1060, l=1.0890, c=1.1050)
    assert candle.body == pytest.approx(0.0050)
    assert candle.range == pytest.approx(0.0170)
    assert candle.upper_wick == pytest.approx(0.0010)
    assert candle.lower_wick == pytest.approx(0.0110)
    assert candle.direction == 1
    assert candle.is_valid


def test_invalid_bars_are_rejected():
    assert not bar(0, o=1.1, h=1.1, l=1.1, c=1.1).is_valid      # zero range
    assert not bar(0, o=1.2, h=1.1, l=1.0, c=1.05).is_valid      # open outside the range
    assert not bar(0, o=1.0, h=0.9, l=1.1, c=1.0).is_valid       # high below low


# --------------------------------------------------------------------- #
# Classification rules — each pattern pinned by an exact construction
# --------------------------------------------------------------------- #
def test_doji_and_marubozu():
    doji = bar(0, o=1.1000, h=1.1050, l=1.0950, c=1.1001)        # body 1% of range
    assert "doji" in classify_bar(doji)
    assert "marubozu" not in classify_bar(doji)

    marubozu = bar(0, o=1.1000, h=1.1050, l=1.0999, c=1.1049)    # body 98% of range
    assert "marubozu" in classify_bar(marubozu)
    assert "doji" not in classify_bar(marubozu)


def test_pins_are_directional_and_mutually_distinct():
    hammer = bar(0, o=1.1030, h=1.1040, l=1.0900, c=1.1035)      # long lower wick, body high
    names = classify_bar(hammer)
    assert "bullish_pin" in names
    assert "bearish_pin" not in names

    shooting_star = bar(0, o=1.0960, h=1.1090, l=1.0955, c=1.0965)
    names = classify_bar(shooting_star)
    assert "bearish_pin" in names
    assert "bullish_pin" not in names


def test_spinning_top_needs_two_sided_wicks():
    spinning = bar(0, o=1.1000, h=1.1074, l=1.0926, c=1.1016)
    assert "spinning_top" in classify_bar(spinning)
    assert "bullish_pin" not in classify_bar(spinning)


def test_engulfing_and_inside_outside_bars():
    previous = bar(0, o=1.1050, h=1.1060, l=1.1000, c=1.1010)    # bearish
    engulfing = bar(1, o=1.1005, h=1.1075, l=1.1000, c=1.1065)   # bullish, covers the body
    names = classify_bar(engulfing, previous)
    assert "bullish_engulfing" in names
    assert "bearish_engulfing" not in names

    inside = bar(2, o=1.1030, h=1.1055, l=1.1005, c=1.1040)
    assert "inside_bar" in classify_bar(inside, previous)

    outside = bar(3, o=1.1030, h=1.1070, l=1.0990, c=1.1040)
    assert "outside_bar" in classify_bar(outside, previous)


def test_multi_bar_patterns_need_the_full_look_back():
    # morning star: strong bearish, small body, bullish close back above the first body's midpoint
    first = bar(0, o=1.1100, h=1.1105, l=1.0995, c=1.1000)      # bearish, body 0.0100 of 0.0110
    second = bar(1, o=1.1000, h=1.1008, l=1.0985, c=1.0998)     # small body
    third = bar(2, o=1.0999, h=1.1075, l=1.0995, c=1.1070)      # bullish, closes above 1.1050
    assert "morning_star" in classify_bar(third, second, first)
    # without the look-back bars it cannot be recognised - and must not be guessed
    assert "morning_star" not in classify_bar(third, second)

    # three white soldiers: three rising bullish candles with bodies >= half their range
    s1 = bar(0, o=1.1000, h=1.1020, l=1.0995, c=1.1016)
    s2 = bar(1, o=1.1017, h=1.1040, l=1.1012, c=1.1035)
    s3 = bar(2, o=1.1036, h=1.1060, l=1.1030, c=1.1055)
    assert "three_soldiers" in classify_bar(s3, s2, s1)
    assert "three_crows" not in classify_bar(s3, s2, s1)


def test_classification_is_deterministic_and_uses_only_the_stated_rules():
    candle = bar(0, o=1.1030, h=1.1040, l=1.0900, c=1.1035)
    first = classify_bar(candle)
    assert first == classify_bar(candle)
    # A pin bar with a huge lower wick has a small body, so it cannot also be a marubozu.
    assert "marubozu" not in first


def test_pattern_description_lists_every_rule():
    text = pattern_description("all")
    for name in PATTERN_NAMES:
        assert name in text
    with pytest.raises(InputError):
        pattern_description("magic_candle")


# --------------------------------------------------------------------- #
# Forward statistics
# --------------------------------------------------------------------- #
def _drifting_series(count: int = 400, seed: int = 5, drift: float = 0.0002) -> list[Bar]:
    """A synthetic random walk with occasional pin bars. Test data, not market data."""
    rng = random.Random(seed)
    bars: list[Bar] = []
    price = 1.1000
    for index in range(count):
        spread = rng.uniform(0.0010, 0.0040)
        open_price = price
        close_price = open_price + drift + rng.uniform(-1, 1) * spread * 0.6
        high = max(open_price, close_price) + rng.uniform(0, spread * 0.5)
        low = min(open_price, close_price) - rng.uniform(0, spread * 0.5)
        if index % 37 == 0:  # inject a bullish pin bar shape
            low = min(open_price, close_price) - spread * 3
            high = max(open_price, close_price) + 0.00005
            close_price = max(open_price, close_price)
        bars.append(bar(index, open_price, high, low, close_price))
        price = close_price
    return bars


def test_analysis_counts_only_complete_forward_windows():
    bars = _drifting_series(200)
    stats = analyse_pattern(bars, "bullish_pin", forward=20)
    # occurrences near the end cannot be measured, so they must not be counted
    assert stats.occurrences < 200
    assert 0.0 <= (stats.hit_rate or 0) <= 1.0
    assert 0.0 <= (stats.p_barrier_favourable or 0) <= 1.0
    assert stats.baseline_p_barrier is not None
    assert stats.median_mfe_r is not None and stats.median_mae_r is not None


def test_analysis_reports_zero_occurrences_without_inventing_a_conclusion():
    bars = _drifting_series(120, seed=11)
    # "outside_bar" requires an unrealistically wide range, so it should not appear.
    stats = analyse_pattern(bars, "outside_bar", forward=10)
    if stats.occurrences == 0:
        report = stats.report()
        assert "N o occurrences" not in report
        assert "Nothing to measure" in report
    else:
        assert stats.hit_rate is not None


def test_overlapping_windows_are_counted_and_warned_about():
    bars = _drifting_series(300, seed=3)
    stats = analyse_pattern(bars, "doji", forward=30)
    if stats.occurrences > 1:
        assert stats.overlap_pairs >= 0
        if stats.overlap_pairs:
            assert any("overlap" in warning for warning in stats.warnings)


def test_warnings_always_include_costs_selection_and_the_barrier_caveat():
    bars = _drifting_series(300, seed=7)
    stats = analyse_pattern(bars, "inside_bar", forward=10)
    joined = " ".join(stats.warnings).lower()
    assert "gross" in joined                      # costs not modelled
    assert "you chose" in joined                  # selection bias
    assert "barrier test" in joined               # stop-placement caveat
    assert "not a strategy" in joined


def test_too_few_bars_or_samples_raise_instead_of_reporting():
    bars = _drifting_series(40)
    with pytest.raises(InputError):
        analyse_pattern(bars, "doji", forward=100)
    with pytest.raises(InputError):
        analyse_pattern(bars, "doji", forward=5, min_samples=10_000)
    with pytest.raises(InputError):
        analyse_pattern(bars, "doji", forward=0)
    with pytest.raises(InputError):
        analyse_pattern(bars, "doji", barrier=0)
    with pytest.raises(InputError):
        analyse_pattern(bars, "doji", direction_bias="sideways")


def test_direction_bias_changes_the_measurement_not_the_sample():
    bars = _drifting_series(400, seed=13)
    long_only = analyse_pattern(bars, "bullish_pin", forward=10, direction_bias="long")
    short_only = analyse_pattern(bars, "bullish_pin", forward=10, direction_bias="short")
    assert long_only.occurrences == short_only.occurrences
    # Measuring the same candles in opposite directions must not give the same numbers.
    assert (long_only.median_signed_r or 0) != (short_only.median_signed_r or 0)


def test_report_never_claims_a_signal_or_a_promise():
    bars = _drifting_series(400, seed=17)
    stats = analyse_pattern(bars, "bullish_pin", forward=20)
    report = stats.report().lower()
    for forbidden in ("buy", "sell", "guaranteed", "sure thing", "win rate is"):
        assert forbidden not in report.replace("hit rate", "")


# --------------------------------------------------------------------- #
# CSV loading
# --------------------------------------------------------------------- #
def test_loader_accepts_common_csv_shapes(tmp_path):
    path = tmp_path / "bars.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        writer.writerow(["2026-01-01", "1.1000", "1.1050", "1.0950", "1.1020", "1000"])
        for index in range(60):
            writer.writerow([f"2026-02-{index % 28 + 1:02d}", "1.1020", "1.1070",
                             "1.0970", "1.1040", "1100"])
    loaded = load_bars_csv(path)
    assert len(loaded) == 61
    assert loaded[0].open == pytest.approx(1.1000)
    assert loaded[0].date == "2026-01-01"


def test_loader_tolerates_a_second_header_row(tmp_path):
    path = tmp_path / "messy.csv"
    lines = ["Date,Open,High,Low,Close"]
    lines.append("EURUSD=X,EURUSD=X,EURUSD=X,EURUSD=X,EURUSD=X")   # ticker row
    for index in range(40):
        lines.append(f"2026-03-{index % 28 + 1:02d},1.1,1.101,1.099,1.1005")
    path.write_text("\n".join(lines), encoding="utf-8")
    loaded = load_bars_csv(path)
    assert len(loaded) == 40


def test_loader_refuses_missing_columns_and_missing_files(tmp_path):
    path = tmp_path / "wrong.csv"
    # enough rows to get past the row-count guard, so the missing-column check is reached
    path.write_text(
        "date,price\n" + "\n".join(f"2026-01-{i + 1:02d},1.1" for i in range(10)),
        encoding="utf-8",
    )
    with pytest.raises(InputError) as excinfo:
        load_bars_csv(path)
    assert "open" in str(excinfo.value)

    with pytest.raises(InputError) as missing:
        load_bars_csv(tmp_path / "does_not_exist.csv")
    assert "never invents market data" in str(missing.value)


def test_loader_refuses_too_little_data(tmp_path):
    path = tmp_path / "short.csv"
    lines = ["date,open,high,low,close"] + [
        f"2026-01-{i + 1:02d},1.1,1.101,1.099,1.1005" for i in range(10)
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    with pytest.raises(InputError) as excinfo:
        load_bars_csv(path)
    assert "30" in str(excinfo.value)


# --------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------- #
def test_cli_rules_listing():
    from forex_mastery.cli import main

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["candles", "--rules"])
    output = buffer.getvalue()
    assert code == 0
    for name in PATTERN_NAMES:
        assert name in output


def test_cli_requires_a_file_and_explains_where_to_get_one():
    from forex_mastery.cli import main

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["candles", "--pattern", "doji"])
    assert code == 1
    assert "market" in buffer.getvalue()


def test_cli_measures_a_supplied_file(tmp_path):
    from forex_mastery.cli import main

    path = tmp_path / "series.csv"
    lines = ["date,open,high,low,close"]
    for candle in _drifting_series(300, seed=23):
        lines.append(
            f"{candle.date},{candle.open:.5f},{candle.high:.5f},{candle.low:.5f},{candle.close:.5f}"
        )
    path.write_text("\n".join(lines), encoding="utf-8")

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["candles", "--file", str(path), "--pattern", "doji",
                     "--forward", "15", "--min-samples", "1"])
    output = buffer.getvalue()
    assert code == 0
    assert "CANDLE PATTERN STATISTICS" in output
    assert "WHAT THIS DOES AND DOES NOT SAY" in output
    lowered = output.lower()
    for forbidden in ("buy now", "sell now", "guaranteed profit"):
        assert forbidden not in lowered
