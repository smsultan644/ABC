"""
Configurable trading rule engine (Level 26 / Level 27).

PURPOSE
-------
Turn your trading plan from prose into arithmetic that returns a decision:
**APPROVED**, **APPROVED WITH WARNINGS**, or **NO TRADE**.

The engine is deliberately conservative and *dumb*: it cannot see the future,
it cannot feel FOMO, and it cannot be talked into a trade. Its only job is to
apply your own written rules consistently - including on the days when you least
want it to.

DESIGN RULES
------------
1. **Blocking rules are blocking.** A violated ``severity: "block"`` rule
   produces NO TRADE, no matter how beautiful the setup looks.
2. **Missing data is not a pass.** If a rule needs a field and the field is
   ``None``, the rule is treated as *not satisfied* (blocking rules) or *unknown*
   (warning rules). "I forgot to check the calendar" must never read as
   "no news".
3. **Every decision is explainable.** Each rule reports why it passed or failed,
   so the journal can record the reason rather than a bare verdict.
4. **Rules live in JSON, not in code.** Editing ``config/strategy_rules.json``
   changes behaviour without touching Python, which is what makes the plan
   *yours*.

USAGE
-----
    from forex_mastery.core.rule_engine import SetupContext, evaluate_setup, load_rules

    rules = load_rules()
    context = SetupContext(
        symbol="EURUSD", direction="long", risk_percent=0.25,
        stop_pips=45, spread_pips=1.4, reward_risk=2.2,
        session="London", minutes_to_high_impact_news=180,
        trades_today=0, daily_pnl_percent=0.0, consecutive_losses=0,
        higher_timeframe_bias="bullish", structure_clear=True,
        emotional_state="calm", checklist_complete=True,
    )
    decision = evaluate_setup(context, rules)
    print(decision.report())
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

__all__ = [
    "NO_TRADE_REASONS",
    "RuleOutcome",
    "SetupContext",
    "Decision",
    "default_rules_path",
    "evaluate_setup",
    "load_rules",
]


@dataclass
class SetupContext:
    """Everything the engine is allowed to consider.

    All fields are optional so partially-filled analysis still evaluates - but
    an unset field can never satisfy a blocking rule (see design rule 2).
    """

    symbol: str | None = None
    direction: str | None = None
    timeframe: str | None = None

    # Risk
    risk_percent: float | None = None
    stop_pips: float | None = None
    reward_risk: float | None = None
    planned_lots: float | None = None
    account_equity: float | None = None
    risk_amount: float | None = None

    # Market conditions
    spread_pips: float | None = None
    atr_pips: float | None = None
    session: str | None = None
    minute_of_hour: int | None = None

    # News / event risk
    minutes_to_high_impact_news: int | None = None
    minutes_since_high_impact_news: int | None = None
    high_impact_news_today: bool | None = None
    major_central_bank_event_today: bool | None = None

    # Account state
    trades_today: int | None = None
    daily_pnl_percent: float | None = None
    weekly_pnl_percent: float | None = None
    consecutive_losses: int | None = None
    open_positions: int | None = None
    correlated_positions: int | None = None
    portfolio_heat_percent: float | None = None

    # Analysis quality
    higher_timeframe_bias: str | None = None   # "bullish" | "bearish" | "range"
    structure_clear: bool | None = None
    level_defined: bool | None = None
    invalidation_defined: bool | None = None
    entry_trigger_defined: bool | None = None
    checklist_complete: bool | None = None
    setups_taken_from_plan: bool | None = None
    screenshot_taken: bool | None = None

    # Human factors
    emotional_state: str | None = None          # calm | anxious | frustrated | euphoric | bored
    slept_well: bool | None = None
    had_loss_today: bool | None = None
    revenge_urge: bool | None = None

    extra: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str) -> Any:
        """Read a field, falling back to ``extra``."""
        if hasattr(self, key):
            return getattr(self, key)
        return self.extra.get(key)


@dataclass
class RuleOutcome:
    """Result of evaluating a single rule."""

    code: str
    description: str
    severity: str
    passed: bool
    known: bool
    message: str = ""

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        mark = "PASS" if self.passed else ("BLOCK" if self.severity == "block" else "WARN")
        return f"[{mark:5}] {self.code}: {self.message}"


@dataclass
class Decision:
    """Final engine decision with full audit trail."""

    verdict: str                      # "APPROVED" | "APPROVED WITH WARNINGS" | "NO TRADE"
    approved: bool
    outcomes: list[RuleOutcome] = field(default_factory=list)
    blocking_failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)
    score: float = 0.0               # 0-100 rule-compliance score

    def as_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "approved": self.approved,
            "score": self.score,
            "blocking_failures": self.blocking_failures,
            "warnings": self.warnings,
            "unknown": self.unknown,
            "outcomes": [asdict(o) for o in self.outcomes],
        }

    def report(self) -> str:
        lines = ["=" * 74, "RULE ENGINE DECISION", "=" * 74, f"  VERDICT: {self.verdict}",
                 f"  rule-compliance score: {self.score:.0f}/100", "-" * 74]
        for outcome in self.outcomes:
            lines.append("  " + str(outcome))
        if self.blocking_failures:
            lines.append("-" * 74)
            lines.append("  BLOCKING FAILURES - do not take this trade:")
            lines.extend(f"    * {item}" for item in self.blocking_failures)
        if self.unknown:
            lines.append("-" * 74)
            lines.append("  UNKNOWN / NOT CHECKED (treated as NOT satisfied):")
            lines.extend(f"    ? {item}" for item in self.unknown)
        lines.append("=" * 74)
        lines.append(
            "  Reminder: a NO TRADE verdict is a successful use of the system, not a failure."
            if not self.approved
            else "  Reminder: approval is permission to execute your plan, not a prediction."
        )
        return "\n".join(lines)


NO_TRADE_REASONS: dict[str, str] = {
    "news_window": "High-impact news inside the blackout window",
    "spread_wide": "Spread above the acceptable maximum for this instrument",
    "volatility_abnormal": "ATR far outside its normal band (too quiet or too violent)",
    "structure_unclear": "Market structure is not readable (no clear trend or range)",
    "timeframes_conflict": "Higher and lower timeframe disagree with the intended direction",
    "rr_poor": "Reward-to-risk below the plan minimum",
    "risk_excessive": "Risk per trade above the plan maximum",
    "emotional_state": "You are not in a professional state to trade",
    "revenge_urge": "You want to make back a loss - this is revenge trading",
    "daily_loss_limit": "Daily loss limit reached",
    "weekly_loss_limit": "Weekly loss limit reached",
    "max_trades_day": "Maximum trades per day reached",
    "cooldown": "Cooling-off period after consecutive losses",
    "correlation_excess": "Correlated exposure too high (the same risk twice)",
    "portfolio_heat": "Total portfolio heat above the limit",
    "setup_incomplete": "The setup is not complete against the written checklist",
    "level_missing": "No defined level or invalidation price",
    "not_in_plan": "This idea is not a setup in your written plan",
    "session": "Outside your trading hours",
    "instrument": "Instrument not on your approved list",
}


# ---------------------------------------------------------------------- #
# Rule implementations
# ---------------------------------------------------------------------- #
def _unknown(code: str, description: str, severity: str, why: str) -> RuleOutcome:
    return RuleOutcome(code, description, severity, passed=False, known=False, message=why)


def _max_risk(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    limit = float(params.get("max_percent", 1.0))
    value = ctx.risk_percent
    if value is None:
        return _unknown("risk_max", f"Risk per trade <= {limit}%", severity, "risk_percent not supplied")
    ok = value <= limit
    return RuleOutcome("risk_max", f"Risk per trade <= {limit}%", severity, ok, True,
                       f"risk {value:.3f}% vs limit {limit}%")


def _min_rr(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    limit = float(params.get("min_rr", 1.5))
    value = ctx.reward_risk
    if value is None:
        return _unknown("rr_min", f"Planned R:R >= 1:{limit}", severity, "reward_risk not supplied")
    ok = value >= limit
    return RuleOutcome("rr_min", f"Planned R:R >= 1:{limit}", severity, ok, True,
                       f"planned 1:{value:.2f} vs minimum 1:{limit}")


def _max_spread(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    per_symbol = params.get("max_spread_pips_by_symbol", {}) or {}
    default_max = float(params.get("max_spread_pips", 2.0))
    limit = float(per_symbol.get((ctx.symbol or "").upper(), default_max))
    value = ctx.spread_pips
    if value is None:
        return _unknown("spread_max", f"Spread <= {limit} pips", severity, "spread_pips not supplied")
    ok = value <= limit
    return RuleOutcome("spread_max", f"Spread <= {limit} pips on {ctx.symbol}", severity, ok, True,
                       f"spread {value:.2f} pips vs limit {limit}")


def _news_blackout(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    before = int(params.get("minutes_before", 30))
    after = int(params.get("minutes_after", 15))
    block_cb = bool(params.get("block_central_bank_days", True))
    if block_cb and ctx.major_central_bank_event_today:
        return RuleOutcome("news_blackout", "No entry near high-impact news", severity, False, True,
                           "major central-bank event today - no new positions in this window")
    if ctx.minutes_to_high_impact_news is None and ctx.minutes_since_high_impact_news is None:
        return _unknown("news_blackout", "No entry near high-impact news", severity,
                        "economic calendar not checked (minutes_to/since_high_impact_news unset)")
    to_news = ctx.minutes_to_high_impact_news
    since_news = ctx.minutes_since_high_impact_news
    if to_news is not None and 0 <= to_news < before:
        return RuleOutcome("news_blackout", "No entry near high-impact news", severity, False, True,
                           f"high-impact release in {to_news} min (blackout {before} min before)")
    if since_news is not None and 0 <= since_news < after:
        return RuleOutcome("news_blackout", "No entry near high-impact news", severity, False, True,
                           f"{since_news} min since release (blackout {after} min after)")
    detail = f"next high-impact event in {to_news} min" if to_news is not None else f"{since_news} min after event"
    return RuleOutcome("news_blackout", "No entry near high-impact news", severity, True, True, detail)


def _session_allowed(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    allowed = [s.lower() for s in params.get("allowed", ["London", "New York", "London/New York overlap"])]
    if ctx.session is None:
        return _unknown("session_allowed", "Trade only inside approved sessions", severity, "session not supplied")
    ok = ctx.session.lower() in allowed
    return RuleOutcome("session_allowed", "Trade only inside approved sessions", severity, ok, True,
                       f"session {ctx.session}; allowed {params.get('allowed')}")


def _max_trades_day(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    limit = int(params.get("max_trades_per_day", 2))
    value = ctx.trades_today
    if value is None:
        return _unknown("max_trades_day", f"Max {limit} trades per day", severity, "trades_today not supplied")
    ok = value < limit
    return RuleOutcome("max_trades_day", f"Max {limit} trades per day", severity, ok, True,
                       f"{value} taken today vs limit {limit}")


def _daily_loss_limit(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    limit = float(params.get("max_daily_loss_percent", 1.0))
    value = ctx.daily_pnl_percent
    if value is None:
        return _unknown("daily_loss_limit", f"Daily loss < {limit}%", severity, "daily_pnl_percent not supplied")
    ok = value > -limit
    return RuleOutcome("daily_loss_limit", f"Daily loss < {limit}% of equity", severity, ok, True,
                       f"today {value:+.2f}% vs limit -{limit}%")


def _weekly_loss_limit(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    limit = float(params.get("max_weekly_loss_percent", 3.0))
    value = ctx.weekly_pnl_percent
    if value is None:
        return _unknown("weekly_loss_limit", f"Weekly loss < {limit}%", severity, "weekly_pnl_percent not supplied")
    ok = value > -limit
    return RuleOutcome("weekly_loss_limit", f"Weekly loss < {limit}% of equity", severity, ok, True,
                       f"this week {value:+.2f}% vs limit -{limit}%")


def _cooldown(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    limit = int(params.get("max_consecutive_losses", 2))
    value = ctx.consecutive_losses
    if value is None:
        return _unknown("cooldown", f"Cool off after {limit} consecutive losses", severity,
                        "consecutive_losses not supplied")
    ok = value < limit
    return RuleOutcome("cooldown", f"Cool off after {limit} consecutive losses", severity, ok, True,
                       f"{value} consecutive losses vs limit {limit}")


def _correlation(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    limit = int(params.get("max_correlated_positions", 2))
    value = ctx.correlated_positions
    if value is None:
        return _unknown("correlation", f"Max {limit} positions sharing one currency story", severity,
                        "correlated_positions not supplied")
    ok = value < limit
    return RuleOutcome("correlation", f"Max {limit} positions sharing one currency story", severity, ok, True,
                       f"{value} correlated positions vs limit {limit}")


def _heat(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    limit = float(params.get("max_portfolio_heat_percent", 2.0))
    value = ctx.portfolio_heat_percent
    if value is None:
        return _unknown("portfolio_heat", f"Total heat <= {limit}%", severity,
                        "portfolio_heat_percent not supplied")
    ok = value <= limit
    return RuleOutcome("portfolio_heat", f"Total portfolio heat <= {limit}%", severity, ok, True,
                       f"heat {value:.2f}% vs limit {limit}%")


def _htf_alignment(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    allow_range = bool(params.get("allow_range_setups", True))
    bias = (ctx.higher_timeframe_bias or "").lower()
    direction = (ctx.direction or "").lower()
    if not bias or not direction:
        return _unknown("htf_alignment", "Trade with the higher-timeframe bias", severity,
                        "higher_timeframe_bias and/or direction not supplied")
    if bias == "range" and allow_range:
        return RuleOutcome("htf_alignment", "Trade with the higher-timeframe bias", severity, True, True,
                           "higher timeframe is ranging and range setups are allowed")
    bullish = bias in ("bullish", "up", "uptrend")
    bearish = bias in ("bearish", "down", "downtrend")
    aligns = (bullish and direction.startswith("l")) or (bearish and direction.startswith("s"))
    return RuleOutcome("htf_alignment", "Trade with the higher-timeframe bias", severity, aligns, True,
                       f"HTF {bias} vs {direction} entry")


def _structure_defined(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    flags = {
        "structure_clear": ctx.structure_clear,
        "level_defined": ctx.level_defined,
        "invalidation_defined": ctx.invalidation_defined,
        "entry_trigger_defined": ctx.entry_trigger_defined,
    }
    missing = [k for k, v in flags.items() if v is None]
    if missing:
        return _unknown("setup_complete", "Structure, level, trigger and invalidation defined", severity,
                        f"not supplied: {', '.join(missing)}")
    failed = [k for k, v in flags.items() if not v]
    return RuleOutcome("setup_complete", "Structure, level, trigger and invalidation defined", severity,
                       not failed, True,
                       "all defined" if not failed else f"missing/false: {', '.join(failed)}")


def _in_plan(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    allowed = params.get("allowed_setups", [])
    name = ctx.get("setup_name")
    if name is None and ctx.setups_taken_from_plan is None:
        return _unknown("in_plan", "Setup is defined in the written plan", severity,
                        "setup_name / setups_taken_from_plan not supplied")
    if name is not None and allowed:
        ok = name in allowed
        return RuleOutcome("in_plan", "Setup is defined in the written plan", severity, ok, True,
                           f"setup {name!r}" + ("" if ok else f" not in {allowed}"))
    ok = bool(ctx.setups_taken_from_plan)
    return RuleOutcome("in_plan", "Setup is defined in the written plan", severity, ok, True,
                       "flagged as from-plan" if ok else "not confirmed as a planned setup")


def _volatility_band(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    low = float(params.get("min_atr_pips", 3.0))
    high = float(params.get("max_atr_pips", 200.0))
    value = ctx.atr_pips
    if value is None:
        return _unknown("volatility_band", f"ATR between {low} and {high} pips", severity,
                        "atr_pips not supplied")
    ok = low <= value <= high
    return RuleOutcome("volatility_band", f"ATR between {low} and {high} pips", severity, ok, True,
                       f"ATR {value:.1f} pips")


def _instrument_allowed(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    allowed = [s.upper() for s in params.get("allowed", [])]
    if ctx.symbol is None:
        return _unknown("instrument_allowed", "Instrument on the approved list", severity, "symbol not supplied")
    if not allowed:
        return RuleOutcome("instrument_allowed", "Instrument on the approved list", severity, True, True,
                           "no instrument restriction configured")
    ok = ctx.symbol.upper() in allowed
    return RuleOutcome("instrument_allowed", "Instrument on the approved list", severity, ok, True,
                       f"{ctx.symbol} vs {allowed}")


def _psychology(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    bad_states = {s.lower() for s in params.get("blocked_states", ["frustrated", "euphoric", "revenge", "angry"])}
    state = (ctx.emotional_state or "").lower()
    problems: list[str] = []
    if ctx.revenge_urge:
        problems.append("revenge urge reported")
    if ctx.had_loss_today and state in bad_states:
        problems.append(f"state '{state}' after a loss")
    if state in bad_states:
        problems.append(f"state '{state}'")
    if ctx.slept_well is False and params.get("require_sleep", False):
        problems.append("insufficient sleep")
    if ctx.emotional_state is None:
        return _unknown("psychology", "Professional mental state", severity, "emotional_state not supplied")
    ok = not problems
    return RuleOutcome("psychology", "Professional mental state", severity, ok, True,
                       "state acceptable" if ok else "; ".join(problems))


def _checklist(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    if ctx.checklist_complete is None:
        return _unknown("checklist", "Pre-trade checklist completed", severity,
                        "checklist_complete not supplied")
    return RuleOutcome("checklist", "Pre-trade checklist completed", severity, bool(ctx.checklist_complete),
                       True, "complete" if ctx.checklist_complete else "incomplete")


def _screenshot(ctx: SetupContext, params: dict, severity: str) -> RuleOutcome:
    if ctx.screenshot_taken is None:
        return _unknown("screenshot", "Chart screenshot taken before entry", severity,
                        "screenshot_taken not supplied")
    return RuleOutcome("screenshot", "Chart screenshot taken before entry", severity,
                       bool(ctx.screenshot_taken), True,
                       "captured" if ctx.screenshot_taken else "missing - you cannot review what you did not record")


RULE_TYPES: dict[str, Callable[[SetupContext, dict, str], RuleOutcome]] = {
    "max_risk": _max_risk,
    "min_rr": _min_rr,
    "max_spread": _max_spread,
    "news_blackout": _news_blackout,
    "session_allowed": _session_allowed,
    "max_trades_day": _max_trades_day,
    "daily_loss_limit": _daily_loss_limit,
    "weekly_loss_limit": _weekly_loss_limit,
    "cooldown": _cooldown,
    "correlation": _correlation,
    "portfolio_heat": _heat,
    "htf_alignment": _htf_alignment,
    "setup_complete": _structure_defined,
    "in_plan": _in_plan,
    "volatility_band": _volatility_band,
    "instrument_allowed": _instrument_allowed,
    "psychology": _psychology,
    "checklist": _checklist,
    "screenshot": _screenshot,
}


# ---------------------------------------------------------------------- #
# Config loading and evaluation
# ---------------------------------------------------------------------- #
def default_rules_path() -> Path:
    """Locate ``config/strategy_rules.json`` by searching upward from here."""
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        candidate = parent / "config" / "strategy_rules.json"
        if candidate.is_file():
            return candidate
    candidate = Path.cwd() / "config" / "strategy_rules.json"
    if candidate.is_file():
        return candidate
    raise FileNotFoundError("config/strategy_rules.json not found - run from the project root.")


def load_rules(path: str | Path | None = None) -> list[dict]:
    """Load rule definitions from JSON (``{"rules": [...]}``)."""
    path = Path(path) if path else default_rules_path()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rules = data.get("rules", data if isinstance(data, list) else [])
    for rule in rules:
        if "type" not in rule:
            raise ValueError(f"Rule missing 'type': {rule!r}")
        if rule["type"] not in RULE_TYPES:
            raise ValueError(
                f"Unknown rule type {rule['type']!r}. Known: {sorted(RULE_TYPES)}"
            )
        rule.setdefault("severity", "block")
        if rule["severity"] not in ("block", "warn"):
            raise ValueError(f"severity must be 'block' or 'warn', got {rule['severity']!r}")
        rule.setdefault("enabled", True)
    return [r for r in rules if r.get("enabled", True)]


def evaluate_setup(context: SetupContext, rules: list[dict] | None = None) -> Decision:
    """Evaluate a setup against the rule set and return a decision.

    A blocking rule that returns ``known=False`` (missing input) is treated as a
    **failure** - the engine refuses to approve what it cannot verify.
    """
    rules = rules if rules is not None else load_rules()
    outcomes: list[RuleOutcome] = []
    blocking: list[str] = []
    warnings: list[str] = []
    unknown: list[str] = []

    for rule in rules:
        func = RULE_TYPES[rule["type"]]
        outcome = func(context, rule.get("params", {}) or {}, rule.get("severity", "block"))
        outcome.description = rule.get("description", outcome.description)
        outcomes.append(outcome)
        if not outcome.passed:
            entry = f"{outcome.code}: {outcome.message}"
            if not outcome.known:
                unknown.append(entry)
                if outcome.severity == "block":
                    blocking.append(f"{entry} (unverified -> treated as failure)")
            elif outcome.severity == "block":
                blocking.append(entry)
            else:
                warnings.append(entry)

    evaluated = [o for o in outcomes]
    passed = sum(1 for o in evaluated if o.passed)
    score = (passed / len(evaluated) * 100.0) if evaluated else 0.0
    approved = not blocking
    verdict = (
        "NO TRADE" if blocking else ("APPROVED WITH WARNINGS" if warnings else "APPROVED")
    )
    return Decision(
        verdict=verdict,
        approved=approved,
        outcomes=outcomes,
        blocking_failures=blocking,
        warnings=warnings,
        unknown=unknown,
        score=score,
    )
