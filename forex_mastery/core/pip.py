"""
Pip arithmetic and pip value.

WHY THIS MATTERS
----------------
A "pip" is a unit of price, not a unit of money. Turning pips into money
requires three things: the instrument's contract size, its pip size, and the
exchange rate between the instrument's *quote currency* and your *account
currency*. Get any of the three wrong and your position is the wrong size.

Worked examples (all hand-checkable)
------------------------------------
1. EURUSD, USD account, 1.00 lot
     pip value in quote currency = contract_size x pip_size = 100,000 x 0.0001
                                = 10.00 USD
     quote (USD) == account (USD), so the conversion rate is 1
     => 1 pip = 10.00 USD per lot.  0.01 lots => 0.10 USD per pip.

2. USDJPY, USD account at USDJPY = 150.00, 1.00 lot
     pip value in quote currency = 100,000 x 0.01 = 1,000 JPY
     1 JPY is worth 1/150 USD  => 1,000 / 150 = 6.6667 USD per pip
     (JPY pip value *falls* as USDJPY rises - that is not a bug.)

3. XAUUSD, USD account, 1.00 lot
     contract = 100 troy oz, pip = 0.01  =>  100 x 0.01 = 1.00 USD per pip.
     Gold's small pip value is why gold stops look "huge" in pips: the same
     USD risk can need ~1/10 of the lot size you would use on EURUSD.

A PACKAGE THAT INVENTS A PRICE IS DANGEROUS
------------------------------------------
This module never guesses an exchange rate. If you do not supply the rate (or a
price from which it can be derived) it raises :class:`MissingRateError`. You
either provide it, or the calculation does not happen.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .instruments import InstrumentSpec, get_instrument

__all__ = [
    "MissingRateError",
    "quote_to_account_rate",
    "pip_value_in_quote_currency",
    "pip_value_per_lot",
    "point_value_per_lot",
    "money_per_price_unit",
    "pip_value_table",
]


class MissingRateError(ValueError):
    """Raised when an FX conversion rate is required but was not supplied."""


def quote_to_account_rate(
    quote_currency: str,
    account_currency: str,
    prices: Mapping[str, float] | None = None,
) -> float:
    """How much 1 unit of ``quote_currency`` is worth in ``account_currency``.

    Parameters
    ----------
    quote_currency:
        The currency the instrument is priced in (e.g. ``"JPY"`` for USDJPY).
    account_currency:
        Your account's currency (e.g. ``"USD"``).
    prices:
        Mapping of ``"SYMBOL" -> last price`` used to derive the conversion.
        Accepted keys, in order of preference:

        * ``"<QUOTE><ACCOUNT>"``  e.g. ``"JPYUSD"`` (rarely quoted)
        * ``"<QUOTE>USD"`` style direct pairs
        * ``"<ACCOUNT><QUOTE>"``  e.g. ``"USDJPY"`` -> rate = 1 / price

    Returns
    -------
    float
        Multiplier converting quote-currency amounts into account currency.

    Raises
    ------
    MissingRateError
        If no price is available. We refuse to assume ``1.0``: assuming parity
        for a JPY or CHF quote currency would mis-size the trade by 20-150%.

    Examples
    --------
    >>> round(quote_to_account_rate("JPY", "USD", {"USDJPY": 150.0}), 6)
    0.006667
    >>> quote_to_account_rate("USD", "USD", {})
    1.0
    """
    q = quote_currency.upper()
    a = account_currency.upper()
    if q == a:
        return 1.0

    prices = dict(prices or {})
    direct = f"{q}{a}"
    inverse = f"{a}{q}"
    if direct in prices and prices[direct] > 0:
        return float(prices[direct])
    if inverse in prices and prices[inverse] > 0:
        return 1.0 / float(prices[inverse])

    raise MissingRateError(
        f"Need a conversion rate from {q} to {a}. Supply prices={{'{inverse}': <current "
        f"price>}} (or '{direct}' if that pair is quoted on your platform). "
        "This toolkit will not invent a rate."
    )


def pip_value_in_quote_currency(spec: InstrumentSpec, lots: float = 1.0) -> float:
    """Value of a 1-pip move expressed in the instrument's quote currency.

    Formula
    -------
    ``pip value = lots x contract_size x pip_size``

    Example
    -------
    >>> from .instruments import get_instrument
    >>> pip_value_in_quote_currency(get_instrument("EURUSD"), 1.0)
    10.0
    >>> pip_value_in_quote_currency(get_instrument("XAUUSD"), 1.0)
    1.0
    """
    return float(lots) * spec.contract_size * spec.pip_size


def pip_value_per_lot(
    symbol: str,
    account_currency: str = "USD",
    *,
    lots: float = 1.0,
    prices: Mapping[str, float] | None = None,
    spec: InstrumentSpec | None = None,
) -> float:
    """Value of a 1-pip move for ``lots`` of ``symbol`` in the account currency.

    Formula
    -------
    ``pip_value = lots x contract_size x pip_size x (quote -> account rate)``

    Example
    -------
    >>> round(pip_value_per_lot("EURUSD", "USD"), 2)
    10.0
    >>> round(pip_value_per_lot("USDJPY", "USD", prices={"USDJPY": 150.0}), 4)
    6.6667
    """
    spec = spec or get_instrument(symbol)
    rate = quote_to_account_rate(spec.quote, account_currency, prices)
    return pip_value_in_quote_currency(spec, lots) * rate


def point_value_per_lot(
    symbol: str,
    account_currency: str = "USD",
    *,
    lots: float = 1.0,
    prices: Mapping[str, float] | None = None,
) -> float:
    """Value of a 1-point (1/10 pip) move in the account currency.

    Useful because MetaTrader spread columns and "Stop Level" fields are
    expressed in points, and mixing points and pips is one of the classic
    beginner errors (a 10x error in trade size).
    """
    spec = get_instrument(symbol)
    return pip_value_per_lot(
        symbol, account_currency, lots=lots, prices=prices, spec=spec
    ) / spec.pipettes_per_pip


def money_per_price_unit(
    symbol: str,
    lots: float,
    account_currency: str = "USD",
    *,
    prices: Mapping[str, float] | None = None,
) -> float:
    """Money gained/lost per 1.0 of price movement, in account currency.

    This is the raw conversion used by every profit/loss calculation:

    ``money_per_price_unit = lots x contract_size x (quote -> account rate)``

    Example: 0.10 lots of EURUSD => 0.10 x 100,000 x 1 = 10,000 USD per 1.0000
    of price movement, i.e. 1.00 USD per pip.
    """
    spec = get_instrument(symbol)
    rate = quote_to_account_rate(spec.quote, account_currency, prices)
    return float(lots) * spec.contract_size * rate


@dataclass(frozen=True)
class PipValueRow:
    """One row of the pip-value reference table."""

    symbol: str
    name: str
    pip_size: float
    quote: str
    pip_value_1_lot: float
    pip_value_0_10_lot: float
    pip_value_0_01_lot: float
    verified: bool


def pip_value_table(
    symbols: list[str] | None = None,
    account_currency: str = "USD",
    prices: Mapping[str, float] | None = None,
) -> list[PipValueRow]:
    """Build a pip-value reference table for a set of symbols.

    Any symbol whose conversion rate is unavailable is still included, but its
    pip values are ``float('nan')``-free sentinels of ``0.0`` plus
    ``verified=False`` would be misleading, so instead the row is skipped and
    reported by the caller. To keep this function total, rows are only emitted
    for symbols that can be fully computed.
    """
    from .instruments import list_instruments

    specs = (
        [get_instrument(s) for s in symbols]
        if symbols
        else [s for s in list_instruments() if s.group.startswith("forex")]
    )
    rows: list[PipValueRow] = []
    for spec in specs:
        try:
            one = pip_value_per_lot(spec.symbol, account_currency, prices=prices, spec=spec)
        except MissingRateError:
            continue
        rows.append(
            PipValueRow(
                symbol=spec.symbol,
                name=spec.name,
                pip_size=spec.pip_size,
                quote=spec.quote,
                pip_value_1_lot=one,
                pip_value_0_10_lot=one * 0.1,
                pip_value_0_01_lot=one * 0.01,
                verified=spec.verified,
            )
        )
    return rows
