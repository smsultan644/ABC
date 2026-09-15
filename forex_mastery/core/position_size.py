"""
Risk-based position sizing - the single most important calculation in trading.

THE IDEA IN ONE SENTENCE
-----------------------
**Choose the risk first, then let the stop distance decide the lot size.**

The correct order of operations is fixed and non-negotiable:

1. Decide the maximum money you are willing to lose on this trade (a % of
   equity, normally 0.25%-1.00%, and 0.10%-0.25% while learning).
2. Find the price level that proves your idea wrong (the stop loss).
3. Measure the distance between entry and stop, in pips.
4. Divide the risk budget by (pips x pip value) to get the lot size.

Beginners reverse this: they pick a familiar lot size ("0.10 feels normal"),
then discover their stop implies a risk of 4% of the account. That is how
accounts die.

FORMULAS
--------
``risk_amount      = equity x risk_percent / 100``
``risk_per_lot     = stop_pips x pip_value_per_lot``
``lots_exact       = risk_amount / risk_per_lot``
``lots_tradable    = round_down(lots_exact, volume_step)``
``actual_risk      = lots_tradable x risk_per_lot``

All money figures are in the account currency.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Mapping

from .instruments import InstrumentSpec, get_instrument
from .margin import effective_leverage, notional_value, required_margin
from .pip import pip_value_per_lot, quote_to_account_rate
from .risk import breakeven_win_rate, risk_reward
from .validation import Diagnostics

__all__ = [
    "PositionSizeRequest",
    "PositionSizeResult",
    "RiskScenarioRow",
    "calculate_position_size",
    "position_size_report",
    "risk_level_scenarios",
]


@dataclass
class PositionSizeRequest:
    """Everything needed to size a trade. Nothing here is guessed.

    Parameters
    ----------
    symbol:
        Broker symbol, e.g. ``"EURUSD"`` (case-insensitive).
    balance:
        Account equity the percentage is measured against. Use *equity*
        (balance + floating P/L), not balance, when you already have open
        trades - otherwise your total risk drifts above plan.
    entry, stop:
        Your intended entry price and the invalidation price. The direction is
        inferred: ``stop < entry`` means long, ``stop > entry`` means short.
    risk_percent / risk_amount:
        Supply exactly one. ``risk_amount`` overrides ``risk_percent`` when both
        are given (and a warning is recorded).
    take_profit:
        Optional. Must be on the correct side of the entry, else it is rejected.
    account_currency:
        Your account's currency (Exness default: USD).
    prices:
        FX conversion prices, e.g. ``{"USDJPY": 150.0}``, needed whenever the
        instrument's quote currency differs from the account currency. Never
        invented by this module.
    pip_value_per_lot:
        Optional manual override (account currency per pip per 1.00 lot). Use
        when your broker's contract specification differs from
        ``config/instruments.json``.
    leverage:
        Broker leverage as a ratio (``2000`` for 1:2000). Only used for the
        margin estimate.
    spread_pips, atr_pips, commission_per_lot_round_turn:
        Used for cost-aware diagnostics: is the stop wider than the noise? what
        does the round trip actually cost?
    max_risk_percent, min_risk_reward, max_effective_leverage:
        House rules. Defaults are deliberately conservative and are the
        thresholds this project teaches (see ``config/risk_profile.json``).
    """

    symbol: str
    balance: float
    entry: float
    stop: float
    account_currency: str = "USD"
    risk_percent: float | None = 0.5
    risk_amount: float | None = None
    take_profit: float | None = None
    prices: Mapping[str, float] | None = None
    pip_value_per_lot: float | None = None
    leverage: float | None = None
    spread_pips: float | None = None
    atr_pips: float | None = None
    commission_per_lot_round_turn: float = 0.0
    max_risk_percent: float = 1.0
    min_risk_reward: float = 1.5
    max_effective_leverage: float = 10.0
    instrument: InstrumentSpec | None = None

    # ------------------------------------------------------------------ #
    def direction(self) -> str:
        """``"long"`` or ``"short"``, inferred from entry vs stop."""
        return "long" if self.stop < self.entry else "short"


@dataclass
class PositionSizeResult:
    """Outcome of a position-sizing calculation, ready for display or JSON."""

    ok: bool
    symbol: str
    direction: str
    account_currency: str
    balance: float
    entry: float
    stop: float
    take_profit: float | None

    stop_distance_price: float = 0.0
    stop_pips: float = 0.0
    pip_value_per_lot: float = 0.0

    risk_target_amount: float = 0.0
    risk_percent_target: float = 0.0
    risk_per_lot: float = 0.0

    lots_exact: float = 0.0
    lots: float = 0.0
    units: float = 0.0

    actual_risk_amount: float = 0.0
    actual_risk_percent: float = 0.0

    potential_profit: float | None = None
    reward_pips: float | None = None
    rr: float | None = None
    rr_net_of_costs: float | None = None
    round_trip_cost: float = 0.0

    notional: float = 0.0
    margin_required: float | None = None
    margin_percent_of_equity: float | None = None
    effective_leverage: float | None = None
    broker_leverage: float | None = None

    breakeven_win_rate: float | None = None
    diagnostics: Diagnostics = field(default_factory=Diagnostics)
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        """JSON-serialisable view (diagnostics flattened to strings)."""
        data = asdict(self)
        data["diagnostics"] = self.diagnostics.messages()
        return data

    def report(self) -> str:
        """Plain-text summary suitable for a terminal or a journal entry."""
        spec = get_instrument(self.symbol)
        d = spec.digits
        lines = [
            "=" * 74,
            f"POSITION SIZE  {self.symbol}  ({self.direction.upper()})",
            "=" * 74,
            f"  account equity        : {self.balance:,.2f} {self.account_currency}",
            f"  entry / stop          : {self.entry:.{d}f}  /  {self.stop:.{d}f}",
            f"  stop distance         : {self.stop_pips:,.1f} pips "
            f"({self.stop_distance_price:g} price units)",
            f"  pip value per 1.00 lot: {self.pip_value_per_lot:,.4f} {self.account_currency}",
            "-" * 74,
            f"  risk budget           : {self.risk_target_amount:,.2f} {self.account_currency} "
            f"({self.risk_percent_target:.3f}% of equity)",
            f"  risk per 1.00 lot     : {self.risk_per_lot:,.2f} {self.account_currency}",
            f"  lots (exact)          : {self.lots_exact:.6f}",
            f"  LOTS TO TRADE         : {self.lots:g}   ({self.units:,.0f} {spec.quoted_units})",
            f"  actual risk           : {self.actual_risk_amount:,.2f} {self.account_currency} "
            f"({self.actual_risk_percent:.3f}% of equity)",
        ]
        if self.take_profit is not None:
            suffix = (
                f"  ({self.reward_pips:,.1f} pips)" if self.reward_pips is not None else ""
            )
            lines.append(f"  take profit           : {self.take_profit:.{d}f}{suffix}")
            lines.append(
                f"  R:R (planned)         : 1:{self.rr:.2f}"
                if self.rr is not None
                else "  R:R (planned)         : n/a"
            )
            if self.rr_net_of_costs is not None:
                lines.append(f"  R:R net of costs      : 1:{self.rr_net_of_costs:.2f}")
            if self.potential_profit is not None:
                lines.append(f"  potential profit       : {self.potential_profit:,.2f} {self.account_currency}")
        if self.round_trip_cost:
            lines.append(
                f"  round-trip cost       : {self.round_trip_cost:,.2f} {self.account_currency} "
                f"({(self.round_trip_cost / self.risk_target_amount * 100.0) if self.risk_target_amount else 0:.1f}% of planned risk)"
            )
        if self.notional:
            lines.append(f"  notional value        : {self.notional:,.2f} {self.account_currency}")
        if self.margin_required is not None and self.broker_leverage:
            lines.append(
                f"  margin @ 1:{self.broker_leverage:g}         : {self.margin_required:,.2f} "
                f"{self.account_currency} ({self.margin_percent_of_equity:.2f}% of equity)"
            )
        if self.effective_leverage is not None:
            lines.append(f"  effective leverage    : {self.effective_leverage:,.1f}:1")
        if self.breakeven_win_rate is not None:
            lines.append(f"  break-even win rate   : {self.breakeven_win_rate * 100:.1f}% (before costs)")

        if self.notes:
            lines.append("-" * 74)
            lines.extend(f"  note: {n}" for n in self.notes)
        if self.diagnostics.items:
            lines.append("-" * 74)
            lines.extend(f"  {m}" for m in self.diagnostics.messages())
        lines.append("=" * 74)
        if not self.ok:
            lines.append("  RESULT: NOT VALID - do not trade this setup until the errors above are fixed.")
        return "\n".join(lines)


@dataclass(frozen=True)
class RiskScenarioRow:
    """One row of the risk-percentage scenario table (Level 15 / Level 39)."""

    risk_percent: float
    risk_amount: float
    lots_exact: float
    lots: float
    actual_risk_amount: float
    actual_risk_percent: float
    consecutive_losses_to_10pct_dd: int


def calculate_position_size(request: PositionSizeRequest) -> PositionSizeResult:
    """Size a trade from risk budget and stop distance.

    Never raises for "bad trading decisions" - it returns a result with
    diagnostics. It *does* raise for structurally impossible input (unknown
    symbol, non-positive prices), because no answer is better than a wrong one.

    Example
    -------
    A USD 1,000 account risking 1% on EURUSD at 1.1000 with a 20-pip stop:

    >>> req = PositionSizeRequest("EURUSD", balance=1000, entry=1.1000, stop=1.0980, risk_percent=1.0)
    >>> res = calculate_position_size(req)
    >>> round(res.risk_target_amount, 2)
    10.0
    >>> res.lots            # 10 USD / (20 pips x 10 USD per lot) = 0.05 lots
    0.05

    The same setup on a USD 250 account risking 0.5% is **not tradable** on a
    standard account, and the tool says so rather than quietly rounding up into
    a position that risks 1.6% of equity:

    >>> small = calculate_position_size(PositionSizeRequest(
    ...     "EURUSD", balance=250, entry=1.1000, stop=1.0960, risk_percent=0.5))
    >>> (small.ok, small.lots)
    (False, 0.0)
    """
    spec = request.instrument or get_instrument(request.symbol)
    diag = Diagnostics()
    notes: list[str] = []

    # ---------------------------------------------------------------- #
    # 1. Structural validation
    # ---------------------------------------------------------------- #
    if request.balance <= 0:
        diag.error("balance", f"Account equity must be > 0, got {request.balance!r}")
    if request.entry <= 0 or request.stop <= 0:
        diag.error("price", "Entry and stop prices must be > 0.")
    if request.entry == request.stop:
        diag.error("zero_stop", "Entry equals stop - there is no stop distance to size from.")
    if not diag.ok:
        return PositionSizeResult(
            ok=False,
            symbol=spec.symbol,
            direction=request.direction(),
            account_currency=request.account_currency.upper(),
            balance=request.balance,
            entry=request.entry,
            stop=request.stop,
            take_profit=request.take_profit,
            diagnostics=diag,
        )

    direction = request.direction()

    # ---------------------------------------------------------------- #
    # 2. Risk budget
    # ---------------------------------------------------------------- #
    if request.risk_amount is not None and request.risk_percent is not None:
        diag.warn(
            "both_risk_inputs",
            "Both risk_percent and risk_amount were supplied; risk_amount is used. "
            "Supplying both is how silent risk drift starts.",
        )
    if request.risk_amount is not None:
        risk_amount = float(request.risk_amount)
        risk_percent = risk_amount / request.balance * 100.0
    else:
        risk_percent = float(request.risk_percent if request.risk_percent is not None else 0.5)
        risk_amount = request.balance * risk_percent / 100.0

    if risk_percent <= 0:
        diag.error("risk_zero", "Risk percent must be > 0.")
    if risk_percent > 10:
        diag.error(
            "risk_absurd",
            f"Risk of {risk_percent:.2f}% per trade is not a risk framework, it is an account "
            "liquidation schedule. Reduce to <= 1% (0.25% while learning).",
        )
    elif risk_percent > request.max_risk_percent:
        diag.warn(
            "risk_above_house_limit",
            f"Risk {risk_percent:.2f}% exceeds your own limit of {request.max_risk_percent:.2f}%.",
        )
    if 0 < risk_percent <= 0.05:
        diag.warn(
            "risk_very_small",
            f"{risk_percent:.3f}% risk (about {risk_amount:.2f} {request.account_currency}) may be "
            "smaller than the minimum tradable lot allows.",
        )

    # ---------------------------------------------------------------- #
    # 3. Stop distance and pip value
    # ---------------------------------------------------------------- #
    stop_distance = abs(request.entry - request.stop)
    stop_pips = stop_distance / spec.pip_size

    if stop_pips < 1.0:
        diag.error(
            "stop_tiny",
            f"Stop distance is {stop_pips:.2f} pips on {spec.symbol} (pip size {spec.pip_size:g}). "
            "That is inside the spread and will be hit by noise.",
        )

    try:
        pv_per_lot = (
            float(request.pip_value_per_lot)
            if request.pip_value_per_lot is not None
            else pip_value_per_lot(
                spec.symbol, request.account_currency, lots=1.0, prices=request.prices, spec=spec
            )
        )
        if request.pip_value_per_lot is not None:
            notes.append("pip value supplied manually - confirm it against MT5 > Specification.")
    except Exception as exc:  # MissingRateError or unknown symbol
        diag.error("pip_value", str(exc))
        pv_per_lot = float("nan")

    if request.pip_value_per_lot is None and not diag.errors and request.account_currency.upper() != spec.quote.upper():
        rate = quote_to_account_rate(spec.quote, request.account_currency, request.prices)
        notes.append(
            f"pip value converted at {spec.quote}->{request.account_currency} rate {rate:.6g}; "
            "recompute if the rate moves materially before execution."
        )

    if not diag.ok:
        return PositionSizeResult(
            ok=False,
            symbol=spec.symbol,
            direction=direction,
            account_currency=request.account_currency.upper(),
            balance=request.balance,
            entry=request.entry,
            stop=request.stop,
            take_profit=request.take_profit,
            stop_distance_price=stop_distance,
            stop_pips=stop_pips,
            diagnostics=diag,
        )

    # ---------------------------------------------------------------- #
    # 4. The sizing arithmetic
    # ---------------------------------------------------------------- #
    risk_per_lot = stop_pips * pv_per_lot
    lots_exact = risk_amount / risk_per_lot if risk_per_lot > 0 else float("inf")
    lots = spec.round_volume(lots_exact)

    min_lot_risk = spec.min_volume_lots * risk_per_lot
    if lots < spec.min_volume_lots:
        # What stop distance WOULD the minimum lot allow at this risk budget?
        # max_stop_pips = risk_amount / (min_lot x pip_value_per_lot)
        max_stop_for_min_lot = (
            risk_amount / (spec.min_volume_lots * pv_per_lot) if pv_per_lot > 0 else 0.0
        )
        diag.error(
            "below_min_lot",
            f"Required size {lots_exact:.6f} lots is below the broker minimum of "
            f"{spec.min_volume_lots:g}. The smallest tradable position would risk "
            f"{min_lot_risk:,.2f} {request.account_currency} "
            f"({min_lot_risk / request.balance * 100:.2f}% of equity) on this "
            f"{stop_pips:.1f}-pip stop. At {risk_percent:.3f}% risk, a "
            f"{spec.min_volume_lots:g}-lot position would need a stop of no more than "
            f"{max_stop_for_min_lot:.1f} pips, which is inside normal noise. "
            "Honest options: (1) skip the trade; (2) use a Standard Cent account where 0.01 "
            "cent-lots are 1/100th the size; (3) trade an instrument whose minimum lot has a "
            "smaller money value per pip; (4) deliberately accept the larger percentage, having "
            "recalculated how many such losses reach your drawdown limit. Never 'fix' this by "
            "moving the stop to a price that makes the arithmetic work.",
        )
        lots = 0.0
        notes.append(
            f"MINIMUM-LOT CONSTRAINT: at {request.balance:,.2f} {request.account_currency} equity "
            f"and {risk_percent:.3f}% risk, this instrument cannot express the intended risk. "
            "This is the single most common practical problem on accounts below about 1,000 USD, "
            "and it is a reason to use a Cent account or a longer timeframe - not a reason to "
            "widen a stop arbitrarily."
        )

    actual_risk = lots * risk_per_lot
    actual_risk_pct = actual_risk / request.balance * 100.0
    if lots and abs(lots - lots_exact) > 1e-12:
        notes.append(
            f"Rounded down from {lots_exact:.6f} to {lots:g} lots, so actual risk is "
            f"{actual_risk:,.2f} ({actual_risk_pct:.3f}%)."
        )
    if actual_risk_pct > request.max_risk_percent and spec.min_volume_lots == lots:
        diag.warn(
            "min_lot_exceeds_limit",
            f"Even the minimum lot risks {actual_risk_pct:.2f}% of equity, above your "
            f"{request.max_risk_percent:.2f}% limit. Skip the trade or grow the account.",
        )

    # ---------------------------------------------------------------- #
    # 5. Costs
    # ---------------------------------------------------------------- #
    round_trip_cost = 0.0
    if request.spread_pips:
        round_trip_cost += request.spread_pips * pv_per_lot * lots
        if stop_pips < 3 * request.spread_pips:
            diag.warn(
                "stop_vs_spread",
                f"Stop ({stop_pips:.1f} pips) is less than 3x the spread "
                f"({request.spread_pips:.1f} pips). Spread noise alone can trigger the stop.",
            )
    if request.commission_per_lot_round_turn:
        round_trip_cost += request.commission_per_lot_round_turn * lots

    # ---------------------------------------------------------------- #
    # 6. Take profit and R:R
    # ---------------------------------------------------------------- #
    reward_pips = None
    potential_profit = None
    rr = None
    rr_net = None
    if request.take_profit is not None:
        correct_side = (
            request.take_profit > request.entry
            if direction == "long"
            else request.take_profit < request.entry
        )
        if not correct_side:
            diag.error(
                "tp_wrong_side",
                f"Take profit {request.take_profit:g} is on the wrong side of entry "
                f"{request.entry:g} for a {direction} trade.",
            )
        else:
            # Distance and R:R are properties of the prices, so they are reported even
            # when the position size is untradable - hiding them would hide the reason.
            reward_pips = abs(request.take_profit - request.entry) / spec.pip_size
            rr = risk_reward(request.entry, request.stop, request.take_profit, direction)
            if rr is not None and rr < request.min_risk_reward:
                diag.warn(
                    "rr_low",
                    f"Planned R:R is 1:{rr:.2f}, below your minimum of "
                    f"1:{request.min_risk_reward:.2f}. A sub-1:1 target means a high win rate "
                    "is mandatory - that is a fragile edge.",
                )
            if lots > 0:
                potential_profit = reward_pips * pv_per_lot * lots
                net_reward = potential_profit - round_trip_cost
                net_risk = risk_amount + round_trip_cost * 0.5
                rr_net = (net_reward / net_risk) if net_risk > 0 else None
            else:
                notes.append(
                    "Reward and cost figures describe the intended trade only: "
                    "the position cannot be sized within your risk limit at the broker's "
                    "minimum volume, so there is nothing to trade yet."
                )

    # ---------------------------------------------------------------- #
    # 7. Margin, notional and leverage reality check
    # ---------------------------------------------------------------- #
    notional = notional_value(spec.symbol, lots, request.entry, request.account_currency, prices=request.prices, spec=spec)
    margin_required = None
    margin_pct = None
    if request.leverage and request.leverage > 0:
        margin_required = required_margin(
            spec.symbol, lots, request.entry, request.leverage, request.account_currency,
            prices=request.prices,
        )
        margin_pct = margin_required / request.balance * 100.0
        if margin_required >= request.balance:
            diag.error(
                "margin_exceeds_balance",
                f"Required margin {margin_required:,.2f} >= account equity {request.balance:,.2f}. "
                "The order would be rejected or the account is over-leveraged.",
            )
        elif margin_pct > 50:
            diag.warn(
                "margin_heavy",
                f"This single position would consume {margin_pct:.1f}% of equity as margin, "
                "leaving very little free margin to survive adverse movement.",
            )
    else:
        notes.append("No broker leverage supplied - margin estimate skipped.")

    eff_lev = effective_leverage(
        spec.symbol, lots, request.entry, request.balance, request.account_currency,
        prices=request.prices,
    ) if lots else 0.0
    if eff_lev > request.max_effective_leverage:
        diag.warn(
            "effective_leverage",
            f"Effective leverage is {eff_lev:.1f}:1 versus your house limit of "
            f"{request.max_effective_leverage:.0f}:1. Note: with a fixed stop this does NOT change "
            "your risk per trade, but it means a gap or a widening spread can cost far more than planned.",
        )

    # ---------------------------------------------------------------- #
    # 8. Volatility context
    # ---------------------------------------------------------------- #
    if request.atr_pips:
        ratio = stop_pips / request.atr_pips
        if ratio < 0.5:
            diag.warn(
                "stop_vs_atr",
                f"Stop is {ratio:.2f}x ATR({request.atr_pips:.1f} pips) - very tight. Normal "
                "volatility will trigger it before the idea is proven wrong.",
            )
        elif ratio > 4:
            diag.warn(
                "stop_vs_atr_wide",
                f"Stop is {ratio:.2f}x ATR({request.atr_pips:.1f} pips) - very wide. Check the stop "
                "is at a real invalidation level rather than an arbitrary round number.",
            )

    be_wr = breakeven_win_rate(rr) if rr else None

    return PositionSizeResult(
        ok=diag.ok,
        symbol=spec.symbol,
        direction=direction,
        account_currency=request.account_currency.upper(),
        balance=request.balance,
        entry=request.entry,
        stop=request.stop,
        take_profit=request.take_profit,
        stop_distance_price=stop_distance,
        stop_pips=stop_pips,
        pip_value_per_lot=pv_per_lot,
        risk_target_amount=risk_amount,
        risk_percent_target=risk_percent,
        risk_per_lot=risk_per_lot,
        lots_exact=lots_exact,
        lots=lots,
        units=lots * spec.contract_size,
        actual_risk_amount=actual_risk,
        actual_risk_percent=actual_risk_pct,
        potential_profit=potential_profit,
        reward_pips=reward_pips,
        rr=rr,
        rr_net_of_costs=rr_net,
        round_trip_cost=round_trip_cost,
        notional=notional,
        margin_required=margin_required,
        margin_percent_of_equity=margin_pct,
        effective_leverage=eff_lev,
        broker_leverage=request.leverage,
        breakeven_win_rate=be_wr,
        diagnostics=diag,
        notes=notes,
    )


def position_size_report(result: PositionSizeResult) -> str:
    """Alias kept for readability at call sites."""
    return result.report()


def risk_level_scenarios(
    symbol: str,
    balance: float,
    entry: float,
    stop: float,
    *,
    risk_percents: tuple[float, ...] = (0.10, 0.25, 0.50, 1.00),
    account_currency: str = "USD",
    prices: Mapping[str, float] | None = None,
    leverage: float | None = None,
    max_risk_percent: float = 1.0,
) -> list[RiskScenarioRow]:
    """Compare several risk percentages on the same setup.

    This is the table a disciplined trader builds *before* choosing a risk
    level, so the choice is a policy decision rather than a mood.

    ``consecutive_losses_to_10pct_dd`` = how many losses in a row at that risk
    level produce a 10% drawdown, using compounding:
    ``n = ceil(ln(0.90) / ln(1 - risk))``.
    """
    import math

    rows: list[RiskScenarioRow] = []
    for rp in risk_percents:
        res = calculate_position_size(
            PositionSizeRequest(
                symbol=symbol,
                balance=balance,
                entry=entry,
                stop=stop,
                account_currency=account_currency,
                risk_percent=rp,
                prices=prices,
                leverage=leverage,
                max_risk_percent=max_risk_percent,
            )
        )
        n_to_10 = math.ceil(math.log(1 - 0.10) / math.log(1 - rp / 100.0))
        rows.append(
            RiskScenarioRow(
                risk_percent=rp,
                risk_amount=res.risk_target_amount,
                lots_exact=res.lots_exact,
                lots=res.lots,
                actual_risk_amount=res.actual_risk_amount,
                actual_risk_percent=res.actual_risk_percent,
                consecutive_losses_to_10pct_dd=n_to_10,
            )
        )
    return rows
