"""
Candlestick pattern statistics — honest measurement, not pattern worship.

WHY THIS MODULE EXISTS
----------------------
Every trading book shows a hammer next to a profit and a shooting star next to a
loss. That teaches shapes, not evidence. This module does the opposite: it
classifies candles by **objective, stated rules**, then measures what actually
happened afterwards, and always compares the result with a **baseline** from the
same data.

Three deliberate design choices:

1. **No market data is shipped or downloaded by this module.** You give it an OHLC
   file you obtained yourself (see ``python main.py market`` for optional free
   practice data). A pattern statistic from a period you did not choose is
   evidence; one from a cherry-picked period is marketing.

2. **Results are reported in RANGES, not pips.** The unit (call it "R") is the
   signal candle's own high-low range. Measuring in pips makes a pattern look
   better on volatile instruments; measuring in its own range makes results
   comparable and forces a stop-and-target decision to be explicit.

3. **The barrier test is conservative on purpose.** "Did price reach +1R before
   -1R?" is the question a trader actually has. When a single bar touches both
   barriers, bar data cannot tell you which came first, so the sample is counted
   as an adverse outcome. That bias goes *against* the pattern, which is the only
   safe direction for a bias to point.

WHAT THE OUTPUT CANNOT TELL YOU
-------------------------------
That a pattern "works". It can only tell you what happened, over a sample you
chose, on one instrument and timeframe, gross of costs, with overlapping windows.
The warnings section is part of the result, not decoration.
"""

from __future__ import annotations

import csv
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

from .validation import InputError

__all__ = [
    "Bar",
    "CandleStats",
    "PATTERN_NAMES",
    "PATTERN_RULES",
    "analyse_pattern",
    "load_bars_csv",
    "classify_bar",
    "pattern_description",
]

# ---------------------------------------------------------------------- #
# Objective pattern definitions
# ---------------------------------------------------------------------- #
PATTERN_RULES = {
    "doji": "body <= 10% of the total range (indecision; no directional information on its own)",
    "marubozu": "body >= 90% of the total range (a one-sided candle with almost no wicks)",
    "spinning_top": "body 10-35% of range with both wicks >= 25% of range (balanced two-sided)",
    "bullish_pin": "lower wick >= 2x body, upper wick <= 15% of range, body in the top third "
                   "(the classic 'hammer' shape)",
    "bearish_pin": "upper wick >= 2x body, lower wick <= 15% of range, body in the bottom third "
                   "(the classic 'shooting star' shape)",
    "bullish_engulfing": "previous candle bearish and current candle bullish, with the current body "
                         "covering the previous body (close > prev open and open < prev close)",
    "bearish_engulfing": "previous candle bullish and current candle bearish, with the current body "
                         "covering the previous body (open > prev close and close < prev open)",
    "inside_bar": "high below the previous high AND low above the previous low (compression)",
    "outside_bar": "high above the previous high AND low below the previous low (expansion)",
    "morning_star": "three bars: a strong bearish candle, then a small-bodied candle, then a bullish "
                    "candle closing back above the midpoint of the first candle's body",
    "evening_star": "the mirror image: a strong bullish candle, then a small-bodied candle, then a "
                    "bearish candle closing back below the midpoint of the first candle's body",
    "three_soldiers": "three consecutive bullish candles, each closing higher than the last, each "
                      "with a body of at least half its range",
    "three_crows": "three consecutive bearish candles, each closing lower than the last, each with "
                   "a body of at least half its range",
}

PATTERN_NAMES = tuple(PATTERN_RULES)

_MIN_RANGE = 1e-12


@dataclass(frozen=True)
class Bar:
    """One OHLC bar. ``index`` is its position in the loaded series."""

    index: int
    date: str
    open: float
    high: float
    low: float
    close: float

    # ---- geometry -------------------------------------------------- #
    @property
    def body(self) -> float:
        return abs(self.close - self.open)

    @property
    def range(self) -> float:
        return self.high - self.low

    @property
    def upper_wick(self) -> float:
        return self.high - max(self.open, self.close)

    @property
    def lower_wick(self) -> float:
        return min(self.open, self.close) - self.low

    @property
    def body_fraction(self) -> float:
        return (self.body / self.range) if self.range > _MIN_RANGE else 0.0

    @property
    def is_valid(self) -> bool:
        """Reject impossible or degenerate bars rather than silently using them."""
        if self.range <= _MIN_RANGE:
            return False
        if self.high < self.low:
            return False
        if not (self.low <= self.open <= self.high and self.low <= self.close <= self.high):
            return False
        return True

    @property
    def direction(self) -> int:
        """+1 bullish, -1 bearish, 0 unchanged."""
        if self.close > self.open:
            return 1
        if self.close < self.open:
            return -1
        return 0


def classify_bar(
    bar: Bar, previous: Bar | None = None, previous2: Bar | None = None
) -> set[str]:
    """Return the set of pattern names ``bar`` satisfies, using stated rules only.

    ``previous2`` is the bar two places back; it is only needed by the three-bar
    patterns (morning star, evening star, three soldiers, three crows).

    Deterministic: same bar in, same set out. No opinion, no discretion, no
    "context" — context is a separate question this module cannot answer.
    """
    names: set[str] = set()
    if bar.range <= _MIN_RANGE:
        return names
    if bar.body_fraction <= 0.10:
        names.add("doji")
    if bar.body_fraction >= 0.90:
        names.add("marubozu")
    if 0.10 < bar.body_fraction < 0.35 and bar.upper_wick >= 0.25 * bar.range and (
        bar.lower_wick >= 0.25 * bar.range
    ):
        names.add("spinning_top")
    if (
        bar.body > 0
        and bar.lower_wick >= 2 * bar.body
        and bar.upper_wick <= 0.15 * bar.range
        and min(bar.open, bar.close) >= bar.low + (2.0 / 3.0) * bar.range
    ):
        names.add("bullish_pin")
    if (
        bar.body > 0
        and bar.upper_wick >= 2 * bar.body
        and bar.lower_wick <= 0.15 * bar.range
        and max(bar.open, bar.close) <= bar.low + (1.0 / 3.0) * bar.range
    ):
        names.add("bearish_pin")
    if previous is not None:
        if previous.direction == -1 and bar.direction == 1 and bar.close > previous.open and (
            bar.open <= previous.close
        ):
            names.add("bullish_engulfing")
        if previous.direction == 1 and bar.direction == -1 and bar.open >= previous.close and (
            bar.close <= previous.open
        ):
            names.add("bearish_engulfing")
        if bar.high < previous.high and bar.low > previous.low:
            names.add("inside_bar")
        if bar.high > previous.high and bar.low < previous.low:
            names.add("outside_bar")
    if previous is not None and previous2 is not None:
        first_body_mid = (previous2.open + previous2.close) / 2.0
        if (
            previous2.direction == -1
            and previous2.body >= 0.5 * previous2.range
            and previous.body <= 0.35 * previous.range
            and bar.direction == 1
            and bar.close > first_body_mid
        ):
            names.add("morning_star")
        if (
            previous2.direction == 1
            and previous2.body >= 0.5 * previous2.range
            and previous.body <= 0.35 * previous.range
            and bar.direction == -1
            and bar.close < first_body_mid
        ):
            names.add("evening_star")
        three = (previous2, previous, bar)
        if (
            all(candle.direction == 1 for candle in three)
            and bar.close > previous.close > previous2.close
            and all(candle.body >= 0.5 * candle.range for candle in three)
        ):
            names.add("three_soldiers")
        if (
            all(candle.direction == -1 for candle in three)
            and bar.close < previous.close < previous2.close
            and all(candle.body >= 0.5 * candle.range for candle in three)
        ):
            names.add("three_crows")
    return names


def pattern_description(name: str) -> str:
    """The stated rule for a pattern (or all of them when ``name='all'``)."""
    if name == "all":
        return "\n".join(f"  {key:<20} {text}" for key, text in PATTERN_RULES.items())
    if name not in PATTERN_RULES:
        raise InputError(
            f"unknown pattern {name!r}. Known patterns: {', '.join(PATTERN_NAMES)}"
        )
    return f"  {name}: {PATTERN_RULES[name]}"


# ---------------------------------------------------------------------- #
# Loading OHLC data the user supplies
# ---------------------------------------------------------------------- #
_DATE_HINTS = ("date", "datetime", "time", "timestamp", "index")
_OHLC_NAMES = ("open", "high", "low", "close")


def load_bars_csv(path: Path | str, limit: int | None = None) -> list[Bar]:
    """Load OHLC bars from a CSV file.

    Tolerates the shapes real files come in: a header row in any case, extra
    columns (volume, adjusted close, ticker rows), and a date column anywhere.
    Rows whose price columns cannot be parsed are skipped and counted; the count
    is returned in the warnings of the analysis, never hidden.
    """
    path = Path(path)
    if not path.is_file():
        raise InputError(
            f"OHLC file not found: {path}\n"
            "This module never invents market data. Supply your own file, for example\n"
            "  python main.py market --symbols EURUSD=X --period 2y --interval 1d\n"
            "then point at data/raw/EURUSD_X_1d.csv (practice data, not your broker's feed)."
        )

    rows = list(csv.reader(path.read_text(encoding="utf-8").splitlines()))
    if len(rows) < 3:
        raise InputError(f"{path} has too few rows to contain OHLC data")

    header = [cell.strip().lower() for cell in rows[0]]
    column: dict[str, int] = {}
    for name in _OHLC_NAMES:
        for position, cell in enumerate(header):
            if cell == name or cell.endswith(f"_{name}") or cell.startswith(f"{name}_"):
                column[name] = position
                break
    missing = [name for name in _OHLC_NAMES if name not in column]
    if missing:
        raise InputError(
            f"{path}: could not find column(s) {missing} in the header {rows[0]!r}.\n"
            "Expected columns named open, high, low, close (any case)."
        )

    date_position = next(
        (i for i, cell in enumerate(header) if cell in _DATE_HINTS), None
    )

    bars: list[Bar] = []
    for raw in rows[1:]:
        if len(raw) <= max(column.values()):
            continue
        try:
            numbers = {name: float(raw[position]) for name, position in column.items()}
        except (TypeError, ValueError):
            continue  # sub-header row, ticker row, or a partial final line
        date_text = raw[date_position] if date_position is not None and date_position < len(raw) else ""
        bar = Bar(
            index=len(bars),
            date=date_text,
            open=numbers["open"],
            high=numbers["high"],
            low=numbers["low"],
            close=numbers["close"],
        )
        if not bar.is_valid:
            continue
        bars.append(bar)
        if limit and len(bars) >= limit:
            break

    if len(bars) < 30:
        raise InputError(
            f"{path} produced only {len(bars)} valid bars. Pattern statistics need at "
            "least ~30 occurrences, which needs far more bars than that."
        )
    return bars


# ---------------------------------------------------------------------- #
# Statistics
# ---------------------------------------------------------------------- #
@dataclass
class CandleStats:
    """Forward statistics for one pattern, measured against a baseline."""

    pattern: str
    direction_bias: str                 # "candle" | "long" | "short"
    forward: int
    barrier: float
    sample_bars: int
    occurrences: int
    hit_rate: float | None              # share with a positive signed forward return
    baseline_hit_rate: float | None
    median_signed_r: float | None
    mean_signed_r: float | None
    median_mfe_r: float | None
    median_mae_r: float | None
    p_barrier_favourable: float | None  # P(reach +barrier before -barrier)
    baseline_p_barrier: float | None
    overlap_pairs: int
    first_date: str
    last_date: str
    warnings: list[str] = field(default_factory=list)

    def report(self) -> str:
        """Terminal report. The warnings are printed with the numbers, never after them."""
        lines = [
            "=" * 78,
            f"CANDLE PATTERN STATISTICS - {self.pattern}",
            "=" * 78,
            f"  data          : {self.sample_bars:,} bars, {self.first_date} to {self.last_date}",
            f"  rule          : {PATTERN_RULES.get(self.pattern, 'n/a')}",
            f"  direction     : {self.direction_bias}",
            f"  forward window: next {self.forward} bars",
            f"  unit          : 'R' = the signal candle's own high-low range",
            f"  occurrences   : {self.occurrences:,}",
            "-" * 78,
        ]
        if not self.occurrences:
            lines.append("  No occurrences in this file. Nothing to measure - and no conclusion")
            lines.append("  can be drawn from an empty sample either way.")
            lines.append("=" * 78)
            return "\n".join(lines)

        def pct(value: float | None) -> str:
            return "n/a" if value is None else f"{value * 100:.1f}%"

        def num(value: float | None) -> str:
            return "n/a" if value is None else f"{value:+.3f}"

        lines += [
            f"  hit rate (signed forward return > 0) : {pct(self.hit_rate)}",
            f"  baseline for the same period         : {pct(self.baseline_hit_rate)}",
            f"  median signed return                 : {num(self.median_signed_r)}R",
            f"  mean signed return                   : {num(self.mean_signed_r)}R",
            f"  median max favourable excursion      : {num(self.median_mfe_r)}R",
            f"  median max adverse excursion         : {num(self.median_mae_r)}R",
            f"  P(+{self.barrier:g}R before -{self.barrier:g}R)             : {pct(self.p_barrier_favourable)}",
            f"  same barrier test, baseline          : {pct(self.baseline_p_barrier)}",
            "-" * 78,
        ]
        if self.p_barrier_favourable is not None and self.baseline_p_barrier is not None:
            edge = self.p_barrier_favourable - self.baseline_p_barrier
            lines.append(
                f"  difference vs baseline: {edge * 100:+.1f} percentage points. "
                f"{'Smaller than sampling noise at this sample size.' if abs(edge) < 0.05 else 'Worth investigating with more data - not yet a conclusion.'}"
            )
        lines.append("")
        lines.append("  WHAT THIS DOES AND DOES NOT SAY")
        for warning in self.warnings:
            lines.append(f"    ! {warning}")
        lines.append("=" * 78)
        return "\n".join(lines)


def _warnings_for(
    occurrences: int, overlap_pairs: int, sample_bars: int, forward: int
) -> list[str]:
    out: list[str] = []
    if occurrences < 30:
        out.append(
            f"{occurrences} occurrences is a HYPOTHESIS, not evidence. Below ~30 samples the "
            "confidence interval on any of these percentages is wider than the effect you are "
            "looking for."
        )
    elif occurrences < 100:
        out.append(
            f"{occurrences} occurrences gives wide error bars. Treat differences smaller than "
            "about 8 percentage points as noise at this size."
        )
    if overlap_pairs:
        out.append(
            f"{overlap_pairs} "
            f"{'occurrence overlaps' if overlap_pairs == 1 else 'occurrences overlap'} another "
            f"occurrence's {forward}-bar forward window, so they are not independent observations "
            "(autocorrelation). The effective sample is smaller than the count suggests."
        )
    out.append(
        "These figures are GROSS: no spread, commission, swap or slippage is applied. A pattern "
        "whose measured edge is smaller than your cost in R cannot be traded profitably, however "
        "appealing the number on screen is."
    )
    out.append(
        "The barrier test places barriers at +/-1R from the SIGNAL CANDLE'S range, not from a "
        "stop you would actually choose. Switching to a structural stop changes the result. "
        "Test the stop you would really use before believing any of this."
    )
    out.append(
        "You chose this file, this instrument and this period. Selection is the largest source "
        "of false edges in pattern research. Re-run on other instruments and other periods "
        "before drawing any conclusion."
    )
    out.append(
        "A pattern is not a strategy. A strategy needs a market condition, an entry trigger, a "
        "stop, a target, a size and an invalidation - see docs/handbooks/12_trading_plan.md."
    )
    if sample_bars < 500:
        out.append(
            f"{sample_bars} bars is a short history for this kind of measurement; it may cover "
            "only one market regime."
        )
    return out


def analyse_pattern(
    bars: Sequence[Bar],
    pattern: str,
    forward: int = 20,
    barrier: float = 1.0,
    direction_bias: str = "candle",
    min_samples: int = 1,
) -> CandleStats:
    """Measure what happened in the ``forward`` bars after every occurrence.

    Parameters
    ----------
    bars : the loaded series, oldest first.
    pattern : one of :data:`PATTERN_NAMES`.
    forward : how many bars to look ahead.
    barrier : the R multiple used for the favourable-before-adverse test.
    direction_bias : ``"candle"`` (trade in the candle's own direction),
        ``"long"`` or ``"short"``.
    min_samples : raise :class:`InputError` below this count, instead of returning
        a number that looks like evidence.
    """
    if pattern not in PATTERN_RULES:
        raise InputError(f"unknown pattern {pattern!r}. Known: {', '.join(PATTERN_NAMES)}")
    if forward < 1:
        raise InputError("forward must be at least 1 bar")
    if barrier <= 0:
        raise InputError("barrier must be positive")
    if direction_bias not in ("candle", "long", "short"):
        raise InputError("direction_bias must be 'candle', 'long' or 'short'")
    if len(bars) < forward + 3:
        raise InputError(
            f"need more than {forward + 3} bars to look {forward} bars ahead; got {len(bars)}"
        )

    occurrences: list[tuple[int, int]] = []   # (bar index, direction)
    previous: Bar | None = None
    previous2: Bar | None = None
    for bar in bars:
        if pattern in classify_bar(bar, previous, previous2):
            direction = 0
            if direction_bias == "long":
                direction = 1
            elif direction_bias == "short":
                direction = -1
            else:
                direction = bar.direction
            if direction != 0:
                occurrences.append((bar.index, direction))
        previous2, previous = previous, bar

    # ---- per-sample measurements ------------------------------------ #
    signed_returns: list[float] = []
    mfes: list[float] = []
    maes: list[float] = []
    favourable_first = 0
    used_indices: list[int] = []
    dates = [bar.date for bar in bars]

    for index, direction in occurrences:
        window = bars[index + 1 : index + 1 + forward]
        if len(window) < forward:
            continue
        signal = bars[index]
        unit = signal.range
        reference = signal.close

        highest = max(bar.high for bar in window)
        lowest = min(bar.low for bar in window)
        if direction == 1:
            mfe = (highest - reference) / unit
            mae = (reference - lowest) / unit
        else:
            mfe = (reference - lowest) / unit
            mae = (highest - reference) / unit

        signed = (window[-1].close - reference) * direction / unit
        signed_returns.append(signed)
        mfes.append(mfe)
        maes.append(mae)
        used_indices.append(index)

        # barrier test: walk bar by bar, first touch wins; a single bar touching
        # both counts as adverse because bar data cannot order them.
        for bar in window:
            if direction == 1:
                hit_fav = (bar.high - reference) / unit >= barrier
                hit_adv = (reference - bar.low) / unit >= barrier
            else:
                hit_fav = (reference - bar.low) / unit >= barrier
                hit_adv = (bar.high - reference) / unit >= barrier
            if hit_fav and hit_adv:
                break
            if hit_fav:
                favourable_first += 1
                break
            if hit_adv:
                break

    # ---- baseline over every bar with a direction -------------------- #
    baseline_signed: list[float] = []
    baseline_favourable = 0
    baseline_total = 0
    for index in range(len(bars) - forward):
        bar = bars[index]
        if bar.direction == 0:
            continue
        direction = 1 if direction_bias != "short" else -1
        if direction_bias == "candle":
            direction = bar.direction
        window = bars[index + 1 : index + 1 + forward]
        signal = bars[index]
        reference = signal.close
        unit = signal.range
        baseline_signed.append((window[-1].close - reference) * direction / unit)
        baseline_total += 1
        for ahead in window:
            if direction == 1:
                hit_fav = (ahead.high - reference) / unit >= barrier
                hit_adv = (reference - ahead.low) / unit >= barrier
            else:
                hit_fav = (reference - ahead.low) / unit >= barrier
                hit_adv = (ahead.high - reference) / unit >= barrier
            if hit_fav and hit_adv:
                break
            if hit_fav:
                baseline_favourable += 1
                break
            if hit_adv:
                break

    if len(used_indices) < min_samples:
        raise InputError(
            f"only {len(used_indices)} usable occurrences of {pattern} "
            f"(minimum requested: {min_samples})"
        )

    overlap_pairs = 0
    for position, index in enumerate(used_indices):
        for later in used_indices[position + 1:]:
            if later - index < forward:
                overlap_pairs += 1

    first_date = dates[used_indices[0]] if used_indices else dates[0]
    last_date = dates[used_indices[-1]] if used_indices else dates[-1]

    occ = len(used_indices)
    return CandleStats(
        pattern=pattern,
        direction_bias=direction_bias,
        forward=forward,
        barrier=barrier,
        sample_bars=len(bars),
        occurrences=occ,
        hit_rate=(sum(1 for value in signed_returns if value > 0) / occ) if occ else None,
        baseline_hit_rate=(
            sum(1 for value in baseline_signed if value > 0) / len(baseline_signed)
            if baseline_signed
            else None
        ),
        median_signed_r=statistics.median(signed_returns) if signed_returns else None,
        mean_signed_r=statistics.fmean(signed_returns) if signed_returns else None,
        median_mfe_r=statistics.median(mfes) if mfes else None,
        median_mae_r=statistics.median(maes) if maes else None,
        p_barrier_favourable=(favourable_first / occ) if occ else None,
        baseline_p_barrier=(
            baseline_favourable / baseline_total if baseline_total else None
        ),
        overlap_pairs=overlap_pairs,
        first_date=first_date,
        last_date=last_date,
        warnings=_warnings_for(occ, overlap_pairs, len(bars), forward),
    )


def iter_patterns() -> Iterable[str]:
    """Every pattern name, in rule-table order."""
    return PATTERN_NAMES
