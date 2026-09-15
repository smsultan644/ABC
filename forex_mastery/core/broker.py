"""
Broker conditions that are not instrument specifications.

``config/instruments.json`` answers "how much is one pip worth?". This module
answers the other half of the same question: *what happens when a trade goes
wrong* — the account's margin call and stop-out levels, when the platform
demands more margin (Higher Margin Requirements), how trading volume is defined,
and what each account type costs.

Everything carries the date it was verified, because broker conditions are a
snapshot, not a law. The module never guesses: an unknown field returns ``None``
and the CLI prints UNVERIFIED rather than filling the gap with a plausible
number.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .validation import InputError

__all__ = [
    "BrokerProfile",
    "AccountType",
    "account_type",
    "broker_profile",
    "format_account_table",
    "format_hmr_summary",
    "stop_out_level",
    "verification_age_days",
]

_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_PATH = _ROOT / "config" / "broker.json"


@dataclass(frozen=True)
class AccountType:
    """One documented account type."""

    key: str
    name: str
    tier: str
    minimum_initial_deposit: str
    spread_from_pips: float | None
    commission: str
    margin_call_percent: float | None
    stop_out_percent: float | None
    notes: str
    verified: bool

    @property
    def stop_out_is_zero(self) -> bool:
        """True when the documented stop out is 0% (no automatic protection)."""
        return self.stop_out_percent == 0.0

    def summary_line(self) -> str:
        deposit = self.minimum_initial_deposit
        spread = "n/a" if self.spread_from_pips is None else f"from {self.spread_from_pips:g} pips"
        stop_out = "unknown" if self.stop_out_percent is None else f"{self.stop_out_percent:g}%"
        call = "unknown" if self.margin_call_percent is None else f"{self.margin_call_percent:g}%"
        flag = "verified" if self.verified else "VERIFY"
        return (
            f"{self.name} ({self.key}) [{flag}]  min deposit: {deposit} | spread: {spread} | "
            f"commission: {self.commission} | margin call: {call} | stop out: {stop_out}"
        )


@dataclass(frozen=True)
class BrokerProfile:
    """The loaded broker conditions file, with its provenance intact."""

    path: Path
    verified_on: str
    data: dict[str, Any]

    @property
    def account_types(self) -> list[AccountType]:
        types: list[AccountType] = []
        for entry in self.data.get("account_types", []):
            types.append(
                AccountType(
                    key=entry["key"],
                    name=entry["name"],
                    tier=entry.get("tier", ""),
                    minimum_initial_deposit=entry.get("minimum_initial_deposit", "unknown"),
                    spread_from_pips=entry.get("spread_from_pips"),
                    commission=entry.get("commission", "unknown"),
                    margin_call_percent=entry.get("margin_call_percent"),
                    stop_out_percent=entry.get("stop_out_percent"),
                    notes=entry.get("notes", ""),
                    verified=bool(entry.get("verified", False)),
                )
            )
        return types

    @property
    def warnings(self) -> list[str]:
        """Things the file itself says must be double-checked."""
        collection: list[str] = []
        meta = self.data.get("_meta", {})
        if meta.get("important_warning"):
            collection.append(meta["important_warning"])
        self_checks = self.data.get("stop_out_exceptions", {})
        if self_checks.get("consequence"):
            collection.append(self_checks["consequence"])
        return collection


@lru_cache(maxsize=4)
def _load_cached(path_str: str) -> BrokerProfile:
    path = Path(path_str)
    if not path.is_file():
        raise InputError(
            f"broker conditions file not found: {path}\n"
            "It should live at config/broker.json. Restore it before trusting any "
            "margin call or stop-out figure."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise InputError(f"config/broker.json is not valid JSON: {exc}") from exc
    verified_on = data.get("_meta", {}).get("verified_on", "unknown")
    return BrokerProfile(path=path, verified_on=verified_on, data=data)


def broker_profile(path: Path | str | None = None) -> BrokerProfile:
    """Load (and cache) the broker conditions profile."""
    return _load_cached(str(Path(path) if path else _DEFAULT_PATH))


def account_type(key: str, path: Path | str | None = None) -> AccountType:
    """Look up one account type by key or by name (case-insensitive)."""
    wanted = key.strip().lower().replace(" ", "_")
    for entry in broker_profile(path).account_types:
        if entry.key == wanted or entry.name.lower().replace(" ", "_") == wanted:
            return entry
    available = ", ".join(entry.key for entry in broker_profile(path).account_types)
    raise InputError(f"unknown account type {key!r}. Known types: {available}")


def stop_out_level(key: str, path: Path | str | None = None) -> float | None:
    """Documented stop-out percentage for an account type, or ``None`` if unknown.

    ``None`` means "not documented" — never "safe". Callers must treat it as an
    unknown rather than assume a protective value.
    """
    return account_type(key, path).stop_out_percent


def verification_age_days(reference_date: str, path: Path | str | None = None) -> int | None:
    """Days between the file's verification date and ``reference_date`` (ISO).

    Returns ``None`` when either date is missing or unparseable, so a caller can
    distinguish "old" from "unknown" instead of guessing.
    """
    from datetime import date

    verified = broker_profile(path).verified_on
    try:
        then = date.fromisoformat(verified)
        now = date.fromisoformat(reference_date)
    except ValueError:
        return None
    return (now - then).days


def format_account_table(path: Path | str | None = None) -> str:
    """Aligned table of account types, for the terminal."""
    profile = broker_profile(path)
    lines = [
        "=" * 100,
        f"BROKER ACCOUNT TYPES  (verified {profile.verified_on} from official documentation)",
        "=" * 100,
        f"{'account type':<16}{'min deposit':<20}{'spread from':>12}{'commission':>34}"
        f"{'margin call':>13}{'stop out':>10}",
        "-" * 100,
    ]
    for entry in profile.account_types:
        spread = "n/a" if entry.spread_from_pips is None else f"{entry.spread_from_pips:g} pips"
        call = "?" if entry.margin_call_percent is None else f"{entry.margin_call_percent:g}%"
        stop = "?" if entry.stop_out_percent is None else f"{entry.stop_out_percent:g}%"
        lines.append(
            f"{entry.name:<16}{entry.minimum_initial_deposit:<20}{spread:>12}"
            f"{entry.commission:>34}{call:>13}{stop:>10}"
        )
    lines.append("-" * 100)
    lines.append("  'region based' means the official documentation does not publish one figure;")
    lines.append("  check your own Personal Area. A 0% stop out means the broker's automatic")
    lines.append("  protection does not act until equity is essentially exhausted - your own stop")
    lines.append("  and your own position size are the protection.")
    for warning in profile.warnings:
        lines.append(f"  ! {warning}")
    return "\n".join(lines)


def format_hmr_summary(path: Path | str | None = None) -> str:
    """Higher Margin Requirement windows, quoted, with interpretation separated."""
    profile = broker_profile(path)
    hmr = profile.data.get("higher_margin_requirements", {})
    lines = [
        "=" * 100,
        "HIGHER MARGIN REQUIREMENTS (HMR)",
        "=" * 100,
        f"  {hmr.get('summary', 'not documented')}",
        "",
        "  Weekend / scheduled market break",
        f"    documented: {hmr.get('weekend_window', {}).get('quote', 'not documented')}",
        f"    exception : {hmr.get('weekend_window', {}).get('crypto_exception', '')}",
        f"    {hmr.get('weekend_window', {}).get('interpretation', '')}",
        "",
        "  High-impact news",
        f"    documented: {hmr.get('news_window', {}).get('quote', 'not documented')}",
        f"    existing positions: {hmr.get('news_window', {}).get('existing_positions', '')}",
        f"    {hmr.get('news_window', {}).get('interpretation', '')}",
        "",
        f"  duration : {hmr.get('duration_caveat', '')}",
        f"  how to know : {hmr.get('how_to_know', '')}",
        "=" * 100,
        "  Practical rule for this project: do not open positions inside the news blackout",
        "  (30 minutes before / 15 minutes after) and do not carry positions through the",
        "  weekend while learning. Both rules already keep you out of these windows.",
    ]
    return "\n".join(lines)
