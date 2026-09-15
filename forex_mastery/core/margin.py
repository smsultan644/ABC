"""
Margin, free margin, margin level and stop-out distance.

TERMS IN PLAIN ENGLISH
----------------------
* **Notional value** - how much of the asset the position controls. 0.10 lots of
  EURUSD at 1.1000 controls 0.10 x 100,000 = 10,000 EUR, about 11,000 USD.
* **Required margin (used margin)** - the deposit the broker locks up as
  collateral: ``notional / leverage``. Leverage does not change your profit or
  loss per pip; it only changes how much cash is frozen.
* **Free margin** - equity minus used margin. This is what can absorb new
  losses or new trades.
* **Margin level** - ``equity / used margin x 100``, in percent. It is the
  broker's health metric, not yours.
* **Margin call** - a warning threshold (Exness Standard: 60%). Nothing is
  closed automatically; you simply cannot open much more.
* **Stop out** - the level at which the broker force-closes positions. Exness
  advertises 0% for its account types (0% means the broker only closes when
  equity would go negative), which sounds generous but removes the safety net
  that protects careless traders at other brokers. **A 0% stop-out broker is
  more dangerous for beginners, not less**, because nothing stops you except
  your own stop loss.

DESIGN NOTE ON LEVERAGE
-----------------------
This module can compute margin at any leverage, including 1:2000. It also
computes **effective leverage** (notional / equity) and flags it, because the
broker's leverage has almost nothing to do with the risk you actually carry -
your position size and stop distance do. A USD 250 account using 0.50 lots of
EURUSD has effective leverage of roughly 220:1 and will be destroyed by a
20-pip move, regardless of what the broker's leverage setting says.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .instruments import InstrumentSpec, get_instrument
from .pip import quote_to_account_rate
from .validation import Diagnostics

__all__ = [
    "MarginSnapshot",
    "adverse_move_impact",
    "effective_leverage",
    "free_margin",
    "margin_level_percent",
    "notional_value",
    "price_at_equity",
    "price_at_margin_level",
    "required_margin",
    "stop_out_price",
]


def notional_value(
    symbol: str,
    lots: float,
    price: float,
    account_currency: str = "USD",
    *,
    prices: Mapping[str, float] | None = None,
    spec: InstrumentSpec | None = None,
) -> float:
    """Position size in money, converted to the account currency.

    Formula
    -------
    ``notional = lots x contract_size x price x (quote -> account rate)``

    ``price`` must be the price of the instrument in its own quote currency
    (i.e. simply the number you see on the chart).

    Example
    -------
    >>> round(notional_value("EURUSD", 0.10, 1.1000), 2)   # 0.10 x 100,000 x 1.10
    11000.0
    >>> round(notional_value("USDJPY", 0.10, 150.00, prices={"USDJPY": 150.0}), 2)
    10000.0
    """
    spec = spec or get_instrument(symbol)
    rate = quote_to_account_rate(spec.quote, account_currency, prices)
    return abs(float(lots) * spec.contract_size * float(price) * rate)


def required_margin(
    symbol: str,
    lots: float,
    price: float,
    leverage: float,
    account_currency: str = "USD",
    *,
    prices: Mapping[str, float] | None = None,
) -> float:
    """Deposit locked by the broker for an open position.

    Formula
    -------
    ``required margin = notional value / leverage``

    ``leverage`` is written as a ratio: 100 for 1:100, 2000 for 1:2000.

    Example
    -------
    >>> round(required_margin("EURUSD", 0.01, 1.1000, 2000), 2)   # 1,100 / 2000
    0.55
    """
    if leverage <= 0:
        raise ValueError(f"leverage must be > 0, got {leverage!r}")
    return notional_value(
        symbol, lots, price, account_currency, prices=prices
    ) / float(leverage)


def free_margin(equity: float, used_margin: float) -> float:
    """Equity minus used margin. Can be negative, which means trouble."""
    return float(equity) - float(used_margin)


def margin_level_percent(equity: float, used_margin: float) -> float:
    """``equity / used_margin x 100``.

    Returns ``float('inf')`` when nothing is used, because the ratio is
    undefined rather than zero (a common reporting bug that makes an account
    with no positions look "at 0%", i.e. about to be liquidated).
    """
    if used_margin <= 0:
        return float("inf")
    return float(equity) / float(used_margin) * 100.0


def price_at_equity(
    symbol: str,
    lots: float,
    entry: float,
    balance: float,
    target_equity: float,
    account_currency: str = "USD",
    *,
    direction: str = "long",
    prices: Mapping[str, float] | None = None,
) -> float:
    """Price at which a single open position would leave ``target_equity``.

    Derivation for a long position:

    ``unrealised P/L = (P - entry) x lots x contract_size x rate``
    ``equity - balance = unrealised P/L``
    Setting ``equity = target``:  ``P = entry + (target - balance) / (lots x contract x rate)``

    Example
    -------
    >>> round(price_at_equity("EURUSD", 0.10, 1.1000, 250.0, 0.0), 5)  # stop-out at 0%
    1.075
    """
    spec = get_instrument(symbol)
    rate = quote_to_account_rate(spec.quote, account_currency, prices)
    money_per_unit = lots * spec.contract_size * rate
    if money_per_unit <= 0:
        raise ValueError("lots must be > 0")
    sign = 1.0 if str(direction).lower().startswith("l") else -1.0
    delta = (float(target_equity) - float(balance)) / money_per_unit
    return float(entry) + sign * delta


def price_at_margin_level(
    symbol: str,
    lots: float,
    entry: float,
    balance: float,
    level_percent: float,
    *,
    leverage: float,
    account_currency: str = "USD",
    direction: str = "long",
    prices: Mapping[str, float] | None = None,
    other_used_margin: float = 0.0,
    other_equity_delta: float = 0.0,
) -> float:
    """Price at which the account's margin level would equal ``level_percent``.

    Used to answer the two questions a professional asks *before* entering:
    "how far can price go against me before a margin call?" and "...before the
    broker closes my position?"

    ``other_used_margin`` and ``other_equity_delta`` let you model additional
    open positions held alongside this one (for example, a correlated trade).
    """
    spec = get_instrument(symbol)
    rate = quote_to_account_rate(spec.quote, account_currency, prices)
    # Margin requirement is itself price dependent (notional = lots x contract x price)
    # so solve: (balance + pnl(price) + other_equity_delta) / (margin(price) + other) = level
    money_per_unit = lots * spec.contract_size * rate
    contract_per_price = lots * spec.contract_size * rate / leverage  # margin per 1.0 of price
    sign = 1.0 if str(direction).lower().startswith("l") else -1.0

    # equity(price)   = balance + other_equity_delta + sign*(P-entry)*money_per_unit
    # margin(price)   = other_used_margin + contract_per_price * P
    # level/100       = equity(P) / margin(P)
    k = level_percent / 100.0
    # balance + oed + sign*(P - entry)*m = k*(other + c*P)
    numerator_const = balance + other_equity_delta - sign * entry * money_per_unit
    denominator = sign * money_per_unit - k * contract_per_price
    if abs(denominator) < 1e-15:
        return float("nan")
    return (k * other_used_margin - numerator_const) / denominator


def stop_out_price(
    symbol: str,
    lots: float,
    entry: float,
    balance: float,
    *,
    leverage: float,
    stop_out_level_percent: float = 0.0,
    account_currency: str = "USD",
    direction: str = "long",
    prices: Mapping[str, float] | None = None,
    other_used_margin: float = 0.0,
    other_equity_delta: float = 0.0,
) -> float:
    """Price at which the broker's stop-out would trigger for one position.

    Exness advertises a **0%** stop-out for Standard, Standard Cent, Pro, Raw
    Spread and Zero accounts (0% means: only close when equity reaches zero).
    Always confirm your own account's figure in the Exness help centre and in
    your terminal, because it is region- and account-dependent.

    At 0% and a single position this simplifies to *the price at which your
    entire balance is lost*, i.e. ``price_at_equity(..., target_equity=0)``.
    """
    if stop_out_level_percent <= 0:
        return price_at_equity(
            symbol, lots, entry, balance, 0.0, account_currency,
            direction=direction, prices=prices,
        )
    return price_at_margin_level(
        symbol, lots, entry, balance, stop_out_level_percent,
        leverage=leverage, account_currency=account_currency,
        direction=direction, prices=prices,
        other_used_margin=other_used_margin,
        other_equity_delta=other_equity_delta,
    )


def effective_leverage(
    symbol: str,
    lots: float,
    price: float,
    equity: float,
    account_currency: str = "USD",
    *,
    prices: Mapping[str, float] | None = None,
) -> float:
    """``notional / equity`` - the leverage you are *actually* running.

    A USD 250 account holding 0.05 lots of XAUUSD at 2,400 has a notional of
    12,000 USD: effective leverage of 48:1. That is fine. Holding 0.50 lots is
    an effective 480:1 and a 0.2% gold move wipes out 100% of equity.
    """
    if equity <= 0:
        return float("inf")
    return notional_value(symbol, lots, price, account_currency, prices=prices) / float(equity)


def adverse_move_impact(
    symbol: str,
    lots: float,
    percent_move: float,
    equity: float,
    *,
    prices: Mapping[str, float] | None = None,
    account_currency: str = "USD",
    price: float | None = None,
) -> dict[str, float]:
    """How a ``percent_move`` adverse move affects the account.

    Requires ``price`` (current price) so that the % move can be converted into
    money. Returns money and equity-percentage impact. This is the calculation
    that makes leverage concrete.
    """
    if price is None:
        raise ValueError("price is required to evaluate a percentage move")
    spec = get_instrument(symbol)
    rate = quote_to_account_rate(spec.quote, account_currency, prices)
    price_change = abs(price) * float(percent_move) / 100.0
    money = price_change * lots * spec.contract_size * rate
    return {
        "price_change": price_change,
        "money_loss": money,
        "equity_after": equity - money,
        "percent_of_equity": (money / equity * 100.0) if equity > 0 else float("inf"),
    }


@dataclass
class MarginSnapshot:
    """A full margin picture plus diagnostics.

    This is a *reporting* object: it never predicts, it only states what the
    account would look like at the given price.
    """

    symbol: str
    lots: float
    price: float
    entry: float | None
    direction: str
    leverage: float
    account_currency: str
    balance: float
    equity: float
    notional: float
    used_margin: float
    free_margin: float
    margin_level_percent: float
    effective_leverage: float
    margin_call_level_percent: float | None = None
    stop_out_level_percent: float | None = None
    price_at_margin_call: float | None = None
    price_at_stop_out: float | None = None
    pips_to_margin_call: float | None = None
    pips_to_stop_out: float | None = None
    diagnostics: Diagnostics = field(default_factory=Diagnostics)

    def report(self) -> str:
        """Human-readable summary."""
        sym = self.symbol
        spec = get_instrument(sym)
        lines = [
            f"Margin snapshot - {sym} ({self.direction})",
            f"  balance / equity      : {self.balance:,.2f} / {self.equity:,.2f} {self.account_currency}",
            f"  lots / price          : {self.lots:g} @ {self.price:g}",
            f"  notional value        : {self.notional:,.2f} {self.account_currency}",
            f"  leverage (broker)     : 1:{self.leverage:g}",
            f"  used margin           : {self.used_margin:,.2f} {self.account_currency}",
            f"  free margin           : {self.free_margin:,.2f} {self.account_currency}",
            f"  margin level          : {self.margin_level_percent:,.1f}%",
            f"  effective leverage    : {self.effective_leverage:,.1f}:1",
        ]
        if self.margin_call_level_percent is not None:
            lines.append(f"  margin call level     : {self.margin_call_level_percent:g}%")
        if self.stop_out_level_percent is not None:
            lines.append(f"  stop-out level        : {self.stop_out_level_percent:g}%")
        if self.price_at_margin_call is not None and self.price_at_margin_call == self.price_at_margin_call:
            lines.append(
                f"  price at margin call  : {self.price_at_margin_call:.{spec.digits}f}"
                + (f"  ({self.pips_to_margin_call:,.0f} pips away)" if self.pips_to_margin_call is not None else "")
            )
        if self.price_at_stop_out is not None and self.price_at_stop_out == self.price_at_stop_out:
            lines.append(
                f"  price at stop-out     : {self.price_at_stop_out:.{spec.digits}f}"
                + (f"  ({self.pips_to_stop_out:,.0f} pips away)" if self.pips_to_stop_out is not None else "")
            )
        if self.diagnostics.items:
            lines.append("  diagnostics:")
            lines.extend(f"    {m}" for m in self.diagnostics.messages())
        return "\n".join(lines)
