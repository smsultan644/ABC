"""
The trade record - the atomic unit of the whole system.

PHILOSOPHY
----------
If a trade is not recorded with enough detail to answer "why did I do this, and
was it within my plan?", it did not happen as far as improvement is concerned.
The journal is not documentation for its own sake: it is the data set you will
run statistics on in Level 20, and the only honest feedback loop a trader has.

WHAT THIS MODEL DELIBERATELY INCLUDES
-------------------------------------
* **Risk before result.** ``risk_amount`` is mandatory; a P/L without its risk is
  not measurable in R.
* **Reason before outcome.** ``reason_for_entry``, ``reason_for_exit``,
  ``invalidation`` and ``thesis_valid`` capture the decision, so a losing trade
  can still be graded as a good decision (and a winner as a bad one).
* **Process flags.** ``rules_followed`` / ``rule_violations`` /
  ``setup_quality`` / ``emotional_state`` let the performance analysis separate
  "the edge did not work" from "I did not work".
* **Screenshots.** ``screenshot_before`` / ``screenshot_after`` paths. If you
  cannot re-see the chart, you cannot review the decision.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any

from ..core.risk import r_multiple

__all__ = [
    "Direction",
    "EmotionalState",
    "MarketRegime",
    "Outcome",
    "Session",
    "SetupQuality",
    "TradeRecord",
    "TradeStatus",
    "JOURNAL_COLUMNS",
]


class Direction(str, Enum):
    LONG = "long"
    SHORT = "short"


class TradeStatus(str, Enum):
    OPEN = "open"
    WIN = "win"
    LOSS = "loss"
    BREAKEVEN = "breakeven"
    CANCELLED = "cancelled"


class Outcome(str, Enum):
    """Grading of the *decision*, independent of the P/L."""

    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    F = "F"


class Session(str, Enum):
    SYDNEY = "Sydney"
    TOKYO = "Tokyo"
    LONDON = "London"
    NEW_YORK = "New York"
    LONDON_NY_OVERLAP = "London/New York overlap"
    OFF_HOURS = "Off-hours"


class MarketRegime(str, Enum):
    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    RANGE = "range"
    TRANSITION = "transition"
    UNCLEAR = "unclear"


class SetupQuality(str, Enum):
    """Honest self-grade of the setup at entry (see Level 22 / Level 27)."""

    A = "A"      # textbook, all criteria met, from the written plan
    B = "B"      # valid but imperfect (level slightly off, second-tier session)
    C = "C"      # marginal; taken for discretionary reasons
    D = "D"      # should not have been taken


class EmotionalState(str, Enum):
    CALM = "calm"
    CONFIDENT = "confident"
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    EUPHORIC = "euphoric"
    BORED = "bored"
    FEARFUL = "fearful"
    IMPATIENT = "impatient"


# The CSV schema. Order matters for human-readable journals.
JOURNAL_COLUMNS: tuple[str, ...] = (
    "trade_id",
    "date",
    "entry_time",
    "exit_time",
    "symbol",
    "direction",
    "session",
    "timeframe",
    "setup",
    "market_regime",
    "setup_quality",
    "entry",
    "stop_loss",
    "take_profit",
    "lots",
    "risk_percent",
    "risk_amount",
    "account_equity_at_entry",
    "planned_rr",
    "exit_price",
    "pnl",
    "r_multiple",
    "status",
    "result_pips",
    "spread_at_entry_pips",
    "commission",
    "swap",
    "reason_for_entry",
    "invalidation",
    "reason_for_exit",
    "thesis_valid",
    "rules_followed",
    "rule_violations",
    "emotional_state",
    "mistakes",
    "lesson",
    "screenshot_before",
    "screenshot_after",
    "notes",
)


@dataclass
class TradeRecord:
    """A single trade, from idea to review.

    Parameters
    ----------
    trade_id:
        Any stable identifier (``"T-2026-0001"`` is a good convention).
    date / entry_time:
        ``date`` is the ISO date used for daily statistics; ``entry_time`` the
        exact timestamp (include the timezone offset, e.g. ``2026-09-15T08:31+00:00``).
    symbol, direction, timeframe, setup:
        What you traded and with which system.
    entry, stop_loss, take_profit, lots:
        The execution plan as it existed *before* the trade.
    account_equity_at_entry, risk_percent, risk_amount:
        Risk context. If ``risk_amount`` is omitted it is derived from
        ``equity x risk_percent / 100``.
    planned_rr:
        Reward:risk as planned. Comparing planned vs realised R is one of the
        most useful statistics in the whole journal.
    exit_price, pnl, status:
        Filled in when the trade closes. ``r_multiple`` is computed, never
        typed by hand, so it can never disagree with P/L and risk.
    """

    trade_id: str
    date: date | str
    symbol: str
    direction: Direction | str
    entry: float
    stop_loss: float
    take_profit: float | None = None
    lots: float = 0.0
    exit_price: float | None = None
    pnl: float | None = None
    status: TradeStatus | str = TradeStatus.OPEN

    entry_time: str | None = None
    exit_time: str | None = None
    session: Session | str | None = None
    timeframe: str | None = None
    setup: str | None = None
    market_regime: MarketRegime | str | None = None
    setup_quality: SetupQuality | str | None = None

    account_equity_at_entry: float | None = None
    risk_percent: float | None = None
    risk_amount: float | None = None
    planned_rr: float | None = None

    result_pips: float | None = None
    spread_at_entry_pips: float | None = None
    commission: float = 0.0
    swap: float = 0.0

    reason_for_entry: str = ""
    invalidation: str = ""
    reason_for_exit: str = ""
    thesis_valid: bool | None = None

    rules_followed: bool = True
    rule_violations: str = ""
    emotional_state: EmotionalState | str | None = None
    mistakes: str = ""
    lesson: str = ""

    screenshot_before: str = ""
    screenshot_after: str = ""
    notes: str = ""

    extra: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------ #
    # Derived values
    # ------------------------------------------------------------------ #
    def __post_init__(self) -> None:
        """Normalise enums and derive whatever is missing but derivable."""
        if isinstance(self.direction, str):
            self.direction = Direction(self.direction.lower())
        if isinstance(self.status, str):
            try:
                self.status = TradeStatus(self.status.lower())
            except ValueError:
                self.status = TradeStatus.OPEN
        for attr, enum_cls in (
            ("session", Session),
            ("market_regime", MarketRegime),
            ("setup_quality", SetupQuality),
            ("emotional_state", EmotionalState),
        ):
            value = getattr(self, attr)
            if isinstance(value, str) and value:
                try:
                    setattr(self, attr, enum_cls(value))
                except ValueError:
                    # Keep the raw string: journals evolve, and rejecting a
                    # record over a new label would lose data.
                    pass
        if isinstance(self.date, str):
            self.date = self.date[:10]
        if self.risk_amount is None and self.risk_percent and self.account_equity_at_entry:
            self.risk_amount = self.account_equity_at_entry * self.risk_percent / 100.0
        if self.status == TradeStatus.OPEN and self.pnl is not None:
            self.status = self._infer_status()

    def _infer_status(self) -> TradeStatus:
        if self.pnl is None:
            return TradeStatus.OPEN
        if abs(self.pnl) < 1e-9:
            return TradeStatus.BREAKEVEN
        return TradeStatus.WIN if self.pnl > 0 else TradeStatus.LOSS

    @property
    def is_closed(self) -> bool:
        return self.pnl is not None

    @property
    def is_win(self) -> bool:
        return self.pnl is not None and self.pnl > 0

    @property
    def r_multiple(self) -> float | None:
        """P/L expressed in R. ``None`` while the trade is open or risk is unknown."""
        if self.pnl is None or not self.risk_amount:
            return None
        return r_multiple(self.pnl, self.risk_amount)

    @property
    def stop_distance(self) -> float:
        return abs(self.entry - self.stop_loss)

    @property
    def planned_reward_distance(self) -> float:
        if self.take_profit is None:
            return 0.0
        return abs(self.take_profit - self.entry)

    @property
    def risk_percent_of_equity(self) -> float | None:
        if self.risk_amount and self.account_equity_at_entry:
            return self.risk_amount / self.account_equity_at_entry * 100.0
        return self.risk_percent

    @property
    def net_pnl(self) -> float | None:
        """P/L after commission and swap, when those are recorded separately."""
        if self.pnl is None:
            return None
        return self.pnl - abs(self.commission or 0.0) - (self.swap or 0.0)

    def violations_list(self) -> list[str]:
        """Split the free-text violations field into individual items."""
        if not self.rule_violations:
            return []
        return [v.strip() for v in self.rule_violations.replace(";", ",").split(",") if v.strip()]

    # ------------------------------------------------------------------ #
    # Serialisation
    # ------------------------------------------------------------------ #
    def to_row(self) -> dict[str, Any]:
        """Flat dict matching :data:`JOURNAL_COLUMNS` for CSV/Excel output."""
        row: dict[str, Any] = {}
        for column in JOURNAL_COLUMNS:
            value = getattr(self, column, None)
            if isinstance(value, Enum):
                value = value.value
            if value is None and column == "r_multiple":
                value = self.r_multiple
            row[column] = "" if value is None else value
        return row

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "TradeRecord":
        """Build a record from a CSV/Excel row (extra columns go to ``extra``)."""
        known = {f for f in cls.__dataclass_fields__}
        kwargs: dict[str, Any] = {}
        extra: dict[str, Any] = {}
        for key, raw in row.items():
            if key not in known:
                extra[key] = raw
                continue
            kwargs[key] = _coerce(key, raw)
        for required in ("trade_id", "date", "symbol", "direction", "entry", "stop_loss"):
            if kwargs.get(required) in (None, ""):
                raise ValueError(f"Journal row is missing required field {required!r}: {row!r}")
        kwargs["extra"] = extra
        return cls(**kwargs)

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["r_multiple"] = self.r_multiple
        return data


_TRUE = {"true", "yes", "y", "1", "t"}
_FALSE = {"false", "no", "n", "0", "f"}


def _coerce(key: str, raw: Any) -> Any:
    """Convert CSV strings into the right Python types, defensively."""
    if raw is None or raw == "":
        if key in ("lots", "commission", "swap"):
            return 0.0
        if key == "rules_followed":
            return True
        return None
    if key in ("entry", "stop_loss", "take_profit", "exit_price", "pnl", "lots",
               "risk_percent", "risk_amount", "planned_rr", "account_equity_at_entry",
               "result_pips", "spread_at_entry_pips", "commission", "swap"):
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None
    if key in ("rules_followed", "thesis_valid"):
        text = str(raw).strip().lower()
        if text in _TRUE:
            return True
        if text in _FALSE:
            return False
        return None
    if key == "date":
        return str(raw)[:10]
    if isinstance(raw, (datetime, date)):
        return raw.isoformat()
    if key == "trade_id":
        return str(raw)
    return str(raw)
