"""
Input validation and structured diagnostics.

Every calculator in this package returns data *and* diagnostics. A calculator
that silently accepts nonsense (negative prices, a stop above the entry on a
long, a 0.0001-pip stop) is more dangerous than one that refuses.

Two severities are used:

* ``ERROR``   - the calculation cannot be trusted; the result is not produced.
* ``WARNING``  - the calculation is arithmetically valid but is probably a
  mistake or is outside the assumptions the formula was written for.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence


class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass(frozen=True)
class Diagnostic:
    """A single validation message."""

    severity: Severity
    code: str
    message: str

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"[{self.severity.value}] {self.code}: {self.message}"


@dataclass
class Diagnostics:
    """Collects diagnostics from a calculation."""

    items: list[Diagnostic] = field(default_factory=list)

    # -- recording ---------------------------------------------------------
    def error(self, code: str, message: str) -> "Diagnostics":
        self.items.append(Diagnostic(Severity.ERROR, code, message))
        return self

    def warn(self, code: str, message: str) -> "Diagnostics":
        self.items.append(Diagnostic(Severity.WARNING, code, message))
        return self

    # -- querying ----------------------------------------------------------
    @property
    def errors(self) -> list[Diagnostic]:
        return [d for d in self.items if d.severity is Severity.ERROR]

    @property
    def warnings(self) -> list[Diagnostic]:
        return [d for d in self.items if d.severity is Severity.WARNING]

    @property
    def ok(self) -> bool:
        """True when no ERROR-level diagnostic was recorded."""
        return not self.errors

    def messages(self) -> list[str]:
        return [str(d) for d in self.items]

    def extend(self, other: "Diagnostics") -> "Diagnostics":
        self.items.extend(other.items)
        return self


class InputError(ValueError):
    """Raised when input cannot produce a trustworthy result.

    Calculators that return diagnostics never raise this; it exists for the
    small helper functions where returning an object would be over-engineering.
    """


def require_positive(**values: float) -> None:
    """Raise :class:`InputError` unless every value is a finite number > 0."""
    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError(f"{name} must be a number, got {value!r}")
        if value != value or value in (float("inf"), float("-inf")):
            raise InputError(f"{name} must be finite, got {value!r}")
        if value <= 0:
            raise InputError(f"{name} must be > 0, got {value!r}")


def require_non_negative(**values: float) -> None:
    """Raise :class:`InputError` unless every value is a finite number >= 0."""
    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError(f"{name} must be a number, got {value!r}")
        if value != value or value in (float("inf"), float("-inf")):
            raise InputError(f"{name} must be finite, got {value!r}")
        if value < 0:
            raise InputError(f"{name} must be >= 0, got {value!r}")


def require_fraction(name: str, value: float, *, allow_one: bool = True) -> None:
    """Raise unless ``value`` is a probability/fraction in (0, 1] (or [0, 1])."""
    lower_ok = (value >= 0.0) if not allow_one else (value > 0.0)
    if not lower_ok or value > 1.0:
        raise InputError(f"{name} must be between 0 and 1, got {value!r}")


def require_one_of(name: str, value: str, allowed: Sequence[str]) -> None:
    """Raise unless ``value`` is in ``allowed`` (case-insensitive)."""
    if value.lower() not in {a.lower() for a in allowed}:
        raise InputError(f"{name} must be one of {tuple(allowed)}, got {value!r}")
