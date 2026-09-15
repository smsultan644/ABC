"""
Instrument specifications.

An instrument specification answers four questions that must be answered before
any trade can be sized:

1. **What is one lot?**  (``contract_size`` + ``quoted_units``)
2. **How big is one pip?**  (``pip_size``)
3. **How is the instrument priced?**  (``digits`` = decimals shown by the broker)
4. **Which currency is one pip denominated in?**  (``quote``)

Everything else - pip value, position size, margin, stop distance in money - is
derived from those four answers. This module deliberately does not contain
prices: prices change, specifications change slowly, and inventing a price is
the single most dangerous thing a trading tool can do.

Data source: ``config/instruments.json`` (see its ``_meta`` block for official
Exness documentation links and the verification date).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Iterable

__all__ = [
    "InstrumentSpec",
    "InstrumentError",
    "default_config_path",
    "load_instruments",
    "get_instrument",
    "list_instruments",
    "available_symbols",
]

DEFAULT_CONFIG_RELATIVE_PATH = Path("config") / "instruments.json"


class InstrumentError(KeyError):
    """Raised when an unknown symbol is requested."""


@dataclass(frozen=True)
class InstrumentSpec:
    """Specification of a single tradable instrument.

    Attributes
    ----------
    symbol:
        Broker symbol, e.g. ``"EURUSD"`` or ``"XAUUSD"``.
    name:
        Human-readable name.
    group:
        One of ``forex_major``, ``forex_cross``, ``forex_exotic``, ``metal``,
        ``energy``, ``index``, ``crypto``, ``stock``.
    base:
        Base currency / underlying (the first symbol in the pair).
    quote:
        Quote currency - **this is the currency one pip is measured in**, and
        therefore the currency that must be converted into the account currency.
    contract_size:
        How many units of the underlying one lot represents.
    pip_size:
        Price change equal to one pip, expressed in the instrument's own price
        units. EURUSD -> 0.0001; USDJPY -> 0.01; XAUUSD -> 0.01.
    digits:
        Number of decimals the broker shows. ``digits`` and ``pip_size`` are
        independent: a 5-digit EURUSD has a pip at the 4th decimal (1 pip = 10
        platform "points").
    min_volume_lots / volume_step_lots:
        Smallest tradable volume and the increment. Exness: 0.01 both.
    max_volume_lots:
        Optional broker maximum for a single order (Exness Standard: 200 lots
        daytime for majors, 60 at night - this field stores the better-known
        value and the docs record the caveat).
    verified:
        ``True`` only when the values were read from official Exness
        documentation on the verification date. ``False`` means "industry
        convention - confirm in MetaTrader before trading".
    """

    symbol: str
    name: str
    group: str
    base: str
    quote: str
    contract_size: float
    pip_size: float
    digits: int
    quoted_units: str = "units"
    min_volume_lots: float = 0.01
    volume_step_lots: float = 0.01
    max_volume_lots: float | None = None
    verified: bool = False
    note: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    # ------------------------------------------------------------------ #
    # Derived properties - all pure arithmetic, no market data
    # ------------------------------------------------------------------ #
    @property
    def pipettes_per_pip(self) -> int:
        """Platform "points" per pip.

        MetaTrader quotes to one extra decimal than the classic pip for most
        instruments, so 1 pip = 10 points. For instruments where the broker
        shows the same number of decimals as the pip size defines (for example
        indices with pip size 1.0 shown to 1 decimal) this is still 10.
        """
        return 10

    @property
    def point_size(self) -> float:
        """Smallest price increment in the MT4/MT5 sense (1/10 of a pip here)."""
        return self.pip_size / self.pipettes_per_pip

    @property
    def is_jpy_quote(self) -> bool:
        return self.quote.upper() == "JPY"

    @property
    def units_per_lot(self) -> float:
        """Volume of the underlying represented by 1.00 lot."""
        return self.contract_size

    def volume_from_units(self, units: float) -> float:
        """Convert a quantity of underlying units into lots."""
        if self.contract_size <= 0:
            raise InstrumentError(f"{self.symbol}: contract_size must be > 0")
        return units / self.contract_size

    def units_from_volume(self, lots: float) -> float:
        """Convert lots into units of the underlying."""
        return lots * self.contract_size

    def price_to_pips(self, price_change: float) -> float:
        """Convert an absolute price change into pips.

        Sign is preserved: a -0.0050 move on EURUSD is -50 pips.
        """
        return price_change / self.pip_size

    def pips_to_price(self, pips: float) -> float:
        """Convert pips into an absolute price change."""
        return pips * self.pip_size

    def round_volume(self, lots: float) -> float:
        """Round a lot size **down** to the nearest tradable increment.

        Rounding down is deliberate. Rounding up would silently exceed the
        risk budget, which is the one thing position sizing exists to prevent.
        """
        step = self.volume_step_lots
        if step <= 0:
            return lots
        steps = int(lots / step + 1e-9)
        return round(steps * step, 8)

    def describe(self) -> str:
        flag = "verified from Exness docs" if self.verified else "UNVERIFIED - confirm in MT5"
        lines = [
            f"{self.symbol} - {self.name}  [{self.group}] ({flag})",
            f"  1 lot      = {self.contract_size:,.4g} {self.quoted_units}",
            f"  1 pip      = {self.pip_size:g} price units ({self.pipettes_per_pip} points)",
            f"  price shows {self.digits} decimals",
            f"  pip currency = {self.quote}",
            f"  volume      = {self.min_volume_lots} to {self.max_volume_lots or 'broker max'} lots in steps of {self.volume_step_lots}",
        ]
        if self.note:
            lines.append(f"  note: {self.note}")
        return "\n".join(lines)


# ---------------------------------------------------------------------- #
# Loading
# ---------------------------------------------------------------------- #
def default_config_path(start: Path | None = None) -> Path:
    """Locate ``config/instruments.json``.

    Searches upward from ``start`` (default: this file's directory) so the
    package works both from the repository root and when installed elsewhere.
    """
    here = (start or Path(__file__).resolve()).resolve()
    candidates: list[Path] = []
    for parent in [here, *here.parents]:
        candidates.append(parent / DEFAULT_CONFIG_RELATIVE_PATH)
        candidates.append(parent / "config" / "instruments.json")
    candidates.append(Path.cwd() / DEFAULT_CONFIG_RELATIVE_PATH)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"Could not find {DEFAULT_CONFIG_RELATIVE_PATH}. Run the toolkit from the "
        "project root, or pass config_path explicitly."
    )


def load_instruments(config_path: str | Path | None = None) -> dict[str, InstrumentSpec]:
    """Load all instrument specifications.

    Parameters
    ----------
    config_path:
        Optional explicit path to ``instruments.json``.

    Returns
    -------
    dict
        ``{symbol: InstrumentSpec}``.
    """
    path = Path(config_path) if config_path else default_config_path()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    defaults = data.get("defaults", {})
    specs: dict[str, InstrumentSpec] = {}
    for symbol, raw in data.get("instruments", {}).items():
        specs[symbol.upper()] = InstrumentSpec(
            symbol=symbol.upper(),
            name=raw.get("name", symbol),
            group=raw.get("group", "unknown"),
            base=raw.get("base", symbol[:3]).upper(),
            quote=raw.get("quote", symbol[-3:]).upper(),
            contract_size=float(raw["contract_size"]),
            pip_size=float(raw["pip_size"]),
            digits=int(raw.get("digits", 5)),
            quoted_units=raw.get("quoted_units", "units"),
            min_volume_lots=float(raw.get("min_volume_lots", defaults.get("min_volume_lots", 0.01))),
            volume_step_lots=float(
                raw.get("volume_step_lots", defaults.get("volume_step_lots", 0.01))
            ),
            max_volume_lots=raw.get("max_volume_lots"),
            verified=bool(raw.get("verified", False)),
            note=raw.get("note", ""),
            raw=raw,
        )
    if not specs:
        raise InstrumentError(f"No instruments found in {path}")
    return specs


@lru_cache(maxsize=1)
def _registry() -> dict[str, InstrumentSpec]:
    return load_instruments()


def get_instrument(symbol: str, config_path: str | Path | None = None) -> InstrumentSpec:
    """Return the spec for ``symbol`` (case-insensitive).

    Raises
    ------
    InstrumentError
        If the symbol is unknown. We refuse to guess: a made-up pip size
        produces a made-up position size.
    """
    key = str(symbol).upper().strip()
    registry = load_instruments(config_path) if config_path else _registry()
    if key not in registry:
        close = [s for s in registry if key[:3] in s]
        hint = f" Did you mean one of {close}?" if close else ""
        raise InstrumentError(f"Unknown symbol {symbol!r}.{hint}")
    return registry[key]


def list_instruments(
    group: str | None = None, config_path: str | Path | None = None
) -> list[InstrumentSpec]:
    """List instruments, optionally filtered by ``group``."""
    registry = load_instruments(config_path) if config_path else _registry()
    specs = [registry[k] for k in sorted(registry)]
    if group:
        specs = [s for s in specs if s.group == group]
    return specs


def available_symbols(config_path: str | Path | None = None) -> Iterable[str]:
    """Sorted tuple of known symbols."""
    registry = load_instruments(config_path) if config_path else _registry()
    return tuple(sorted(registry))
