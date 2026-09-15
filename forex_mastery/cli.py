"""
Command-line interface - the single entry point for the whole system.

Run ``python main.py --help`` for the command list. Every command is designed to
work in a bare Python 3.10+ environment; commands that need an optional package
(Excel, PDF, charts, notebooks) check for it first and print the exact install
command rather than raising an ImportError.

Design rules
------------
* **Never invent market data.** Commands that need an exchange rate require you
  to pass it (``--price USDJPY=150.0``); they refuse rather than assume.
* **Never print a bare verdict.** Every trading-related command prints the
  assumptions and the failure conditions alongside the number.
* **Always exit non-zero on failure** so the commands are usable in scripts.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parent.parent

__all__ = ["main", "build_parser"]


# ---------------------------------------------------------------------- #
# Small output helpers
# ---------------------------------------------------------------------- #
def _ok(message: str) -> None:
    print(f"  [ok]   {message}")


def _warn(message: str) -> None:
    print(f"  [warn] {message}")


def _fail(message: str) -> None:
    print(f"  [FAIL] {message}", file=sys.stderr)


def _parse_prices(items: Sequence[str] | None) -> dict[str, float]:
    """Parse ``SYMBOL=PRICE`` pairs into a dict."""
    prices: dict[str, float] = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"--price expects SYMBOL=PRICE, got {item!r}")
        symbol, _, value = item.partition("=")
        try:
            prices[symbol.strip().upper()] = float(value)
        except ValueError:
            raise SystemExit(f"Could not parse price for {symbol!r}: {value!r}")
    return prices


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, default=str))


# ---------------------------------------------------------------------- #
# Commands
# ---------------------------------------------------------------------- #
def cmd_doctor(args: argparse.Namespace) -> int:
    """Check the environment, the configuration and the data files."""
    print("=" * 74)
    print("FOREX MASTERY SYSTEM - ENVIRONMENT CHECK")
    print("=" * 74)
    print(f"  python        : {sys.version.split()[0]}")
    print(f"  project root  : {ROOT}")

    print("\nCore packages (required: none - the engine is standard library only)")
    for module in ("pandas", "numpy", "matplotlib", "openpyxl", "xlsxwriter", "reportlab", "scipy"):
        try:
            imported = __import__(module)
            version = getattr(imported, "__version__", "?")
            _ok(f"{module:<12} {version}")
        except Exception:
            _warn(f"{module:<12} not installed (optional)")

    print("\nConfiguration files")
    checks = [
        ("config/instruments.json", "instrument specifications"),
        ("config/strategy_rules.json", "trading rule engine rules"),
        ("config/risk_profile.json", "risk framework for the 250 USD account"),
        ("data/questions/question_bank.json", "quiz question bank"),
    ]
    failures = 0
    for relative, description in checks:
        path = ROOT / relative
        if path.is_file():
            _ok(f"{relative:<38} {description}")
        else:
            _fail(f"{relative:<38} MISSING ({description})")
            failures += 1

    print("\nInstrument specification status (from Exness documentation)")
    from .core.instruments import list_instruments

    specs = list_instruments()
    verified = sum(1 for s in specs if s.verified)
    unverified = [s.symbol for s in specs if not s.verified]
    _ok(f"{verified}/{len(specs)} instruments verified from official documentation")
    if unverified:
        _warn(f"confirm these in MT5 > Specification before sizing: {', '.join(unverified)}")

    print("\nJournals and outputs")
    journal = ROOT / "data" / "journal" / "journal.csv"
    if journal.is_file():
        from .journal.storage import JournalStore

        summary = JournalStore(journal).summary()
        _ok(f"journal: {summary['closed']} closed / {summary['open']} open trades")
    else:
        _warn("no journal yet - create it with: python main.py journal add ...")

    print("\nSanity checks on the calculations")
    from .core.position_size import PositionSizeRequest, calculate_position_size
    from .core.risk import recovery_gain_required

    probe = calculate_position_size(
        PositionSizeRequest("EURUSD", balance=1000, entry=1.1000, stop=1.0980, risk_percent=1.0)
    )
    if probe.ok and abs(probe.lots - 0.05) < 1e-9:
        _ok("position sizing self-test: 1000 USD @ 1% with a 20-pip stop -> 0.05 lots")
    else:
        _fail(f"position sizing self-test failed (got {probe.lots!r})")
        failures += 1
    if abs(recovery_gain_required(50.0) - 100.0) < 1e-9:
        _ok("drawdown recovery self-test: -50% requires +100%")
    else:
        _fail("drawdown recovery self-test failed")
        failures += 1

    print("\n" + "=" * 74)
    if failures:
        _fail(f"{failures} problem(s) found. Fix these before trading anything.")
        return 1
    print("  environment OK")
    print("  Reminder: no configuration check makes a strategy profitable. It only")
    print("  ensures the numbers you are looking at are the numbers you think they are.")
    return 0


def cmd_specs(args: argparse.Namespace) -> int:
    from .core.instruments import get_instrument, list_instruments

    if args.symbol:
        print(get_instrument(args.symbol).describe())
        return 0
    specs = list_instruments(args.group)
    print("=" * 74)
    print(f"INSTRUMENT SPECIFICATIONS ({len(specs)} instruments)")
    print("=" * 74)
    print(f"{'symbol':<10}{'group':<14}{'contract':>12}{'pip size':>11}{'quote':>7}  verified")
    for spec in specs:
        print(
            f"{spec.symbol:<10}{spec.group:<14}{spec.contract_size:>12,.0f}"
            f"{spec.pip_size:>11g}{spec.quote:>7}  {'yes' if spec.verified else 'VERIFY'}"
        )
    print("-" * 74)
    print("  'verified' = read from official Exness documentation on 2026-09-15.")
    print("  Always confirm in MT5 > Market Watch > right-click symbol > Specification.")
    return 0


def cmd_pip(args: argparse.Namespace) -> int:
    from .core.instruments import get_instrument
    from .core.pip import pip_value_per_lot, point_value_per_lot

    spec = get_instrument(args.symbol)
    prices = _parse_prices(args.price)
    value = pip_value_per_lot(spec.symbol, args.account_ccy, lots=args.lots, prices=prices)
    point = point_value_per_lot(spec.symbol, args.account_ccy, lots=args.lots, prices=prices)
    print(f"{spec.symbol} - {spec.name}")
    print(f"  lots                 : {args.lots:g}")
    print(f"  pip size             : {spec.pip_size:g}  ({spec.pipettes_per_pip} points per pip)")
    print(f"  contract size        : {spec.contract_size:,.0f} {spec.quoted_units}")
    print(f"  pip value            : {value:,.4f} {args.account_ccy}")
    print(f"  point value          : {point:,.4f} {args.account_ccy}")
    print(f"  10-pip move is worth : {value * 10:,.4f} {args.account_ccy}")
    if args.pips:
        print(f"  a {args.pips:g}-pip move is worth: {value * args.pips:,.4f} {args.account_ccy}")
    if not spec.verified:
        _warn("specification is not verified from official docs - check MT5 first")
    return 0


def cmd_position(args: argparse.Namespace) -> int:
    from .core.position_size import PositionSizeRequest, calculate_position_size

    request = PositionSizeRequest(
        symbol=args.symbol,
        balance=args.balance,
        entry=args.entry,
        stop=args.stop,
        account_currency=args.account_ccy,
        risk_percent=args.risk,
        risk_amount=args.risk_amount,
        take_profit=args.take_profit,
        prices=_parse_prices(args.price),
        leverage=args.leverage,
        spread_pips=args.spread,
        atr_pips=args.atr,
        commission_per_lot_round_turn=args.commission,
        min_risk_reward=args.min_rr,
    )
    result = calculate_position_size(request)
    if args.json:
        _print_json(result.as_dict())
    else:
        print(result.report())
    return 0 if result.ok else 2


def cmd_scenarios(args: argparse.Namespace) -> int:
    from .core.position_size import risk_level_scenarios

    rows = risk_level_scenarios(
        args.symbol,
        args.balance,
        args.entry,
        args.stop,
        risk_percents=tuple(args.risks),
        prices=_parse_prices(args.price),
        leverage=args.leverage,
    )
    print("=" * 78)
    print(f"RISK-SCENARIO COMPARISON - {args.symbol}  entry {args.entry:g} / stop {args.stop:g}")
    print("=" * 78)
    print(f"{'risk %':>8}{'risk $':>10}{'lots exact':>13}{'lots':>8}{'actual risk':>13}"
          f"{'actual %':>10}{'losses to -10%':>16}")
    for row in rows:
        print(
            f"{row.risk_percent:>8.2f}{row.risk_amount:>10.2f}{row.lots_exact:>13.5f}"
            f"{row.lots:>8.2f}{row.actual_risk_amount:>13.2f}{row.actual_risk_percent:>10.3f}"
            f"{row.consecutive_losses_to_10pct_dd:>16}"
        )
    print("-" * 78)
    print("  Lots of 0.00 mean the required size is below the broker minimum at that")
    print("  risk level. The honest options are: skip the trade, use a Cent account,")
    print("  or accept a different percentage having recalculated the drawdown maths.")
    return 0


def cmd_drawdown(args: argparse.Namespace) -> int:
    from .core.risk import drawdown_ladder, recovery_gain_required

    rows = drawdown_ladder()
    print("=" * 78)
    print(f"DRAWDOWN FRAMEWORK - {args.balance:,.2f} account, losses compound on remaining equity")
    print("=" * 78)
    print("What each drawdown level costs you:")
    print(f"{'drawdown':>10}{'equity left':>14}{'money lost':>12}{'gain to recover':>17}")
    for row in rows:
        remaining = args.balance * row.equity_multiple_remaining
        print(
            f"{'-' + format(row.drawdown_percent, '.0f') + '%':>10}"
            f"{remaining:>14.2f}{args.balance - remaining:>12.2f}"
            f"{'+' + format(recovery_gain_required(row.drawdown_percent), '.1f') + '%':>17}"
        )
    print("-" * 78)
    print("Consecutive losses needed to reach each drawdown "
          "(losses are taken on the remaining equity, so these are not simple divisions):")
    print(f"{'risk %':>8}{'to -5%':>9}{'to -10%':>9}{'to -20%':>9}{'to -30%':>9}{'to -50%':>9}"
          f"{'risk $':>10}")
    for risk in (0.10, 0.25, 0.50, 1.00, 2.00, 5.00):
        counts = []
        for dd in (5, 10, 20, 30, 50):
            counts.append(math.ceil(math.log(1 - dd / 100) / math.log(1 - risk / 100)))
        print(
            f"{risk:>8.2f}" + "".join(f"{c:>9}" for c in counts)
            + f"{args.balance * risk / 100:>10.2f}"
        )
    print("-" * 78)
    print("Recovery asymmetry (gain required on remaining equity):")
    for dd in (5, 10, 20, 30, 50, 70):
        print(f"   -{dd:>2}% drawdown  ->  +{recovery_gain_required(dd):.1f}% required")
    print("=" * 78)
    print("  The point of this table is not to frighten you. It is to show that the")
    print("  only reliable way to survive a long career is to keep each individual loss")
    print("  small enough that the drawdown ladder never reaches its last rows.")
    return 0


def cmd_ruin(args: argparse.Namespace) -> int:
    from .core.risk_of_ruin import simulate_risk_of_ruin

    result = simulate_risk_of_ruin(
        args.win_rate,
        args.rr,
        args.risk / 100.0,
        trades=args.trades,
        paths=args.paths,
        starting_equity=args.equity,
        ruin_fraction=args.ruin,
        cost_in_r=args.cost,
        seed=args.seed,
    )
    print(result.report())
    return 0


def cmd_compound(args: argparse.Namespace) -> int:
    from .core.compounding import project_equity

    projection = project_equity(
        args.win_rate, args.rr, args.risk / 100.0, trades=args.trades,
        starting_equity=args.equity, cost_in_r=args.cost,
    )
    print(projection.report())
    return 0


def cmd_sessions(args: argparse.Namespace) -> int:
    from .core.sessions import (
        SESSION_CHARACTERISTICS,
        active_sessions,
        is_low_liquidity_lull,
        is_market_open,
        session_liquidity_rank,
        format_session_table,
    )

    target = date.fromisoformat(args.date) if args.date else datetime.now(timezone.utc)
    print(format_session_table(target, display_tz=args.tz))
    now = datetime.now(timezone.utc)
    print(f"  current UTC time   : {now:%Y-%m-%d %H:%M}")
    print(f"  sessions open now  : {', '.join(active_sessions(now)) or 'none (quiet window)'}")
    print(f"  market open        : {'yes' if is_market_open(now) else 'no (weekend/close)'}")
    if is_low_liquidity_lull(now):
        _warn("low-liquidity lull (NY close to Tokyo open): default no-trade window")
    rank = session_liquidity_rank(now)
    print(f"  liquidity score    : {rank['liquidity_score']}/4")
    print(f"  context            : {str(rank['note'])[:150]}...")
    if args.explain:
        print("-" * 74)
        for name, text in SESSION_CHARACTERISTICS.items():
            print(f"  {name}:")
            print(f"    {text}")
    return 0


def _state_from_journal(path: Path, symbol: str | None, balance: float | None) -> dict[str, Any]:
    """Derive the risk-state inputs of the rule engine from the journal.

    This exists so that "I forgot to pass --trades-today" cannot silently turn a
    blocked setup into an approved one: the numbers come from the record you
    already keep. Anything the journal cannot tell us stays ``None`` and is still
    treated as unverified by the rule engine.
    """
    from .journal.storage import JournalStore

    store = JournalStore(path)
    records = store.load()
    if not records:
        return {}
    today = date.today()
    closed = [r for r in records if r.pnl is not None]
    today_trades = [r for r in closed if str(r.date)[:10] == today.isoformat()]
    week_start = date.fromordinal(today.toordinal() - today.weekday())
    week_trades = [r for r in closed if str(r.date)[:10] >= week_start.isoformat()]

    equity = balance or (records[-1].account_equity_at_entry or 0.0)
    daily_pnl = sum(r.pnl or 0.0 for r in today_trades)
    weekly_pnl = sum(r.pnl or 0.0 for r in week_trades)

    consecutive_losses = 0
    for record in reversed(closed):
        if (record.pnl or 0.0) < 0:
            consecutive_losses += 1
        else:
            break

    correlated = 0
    if symbol:
        base, quote = symbol[:3].upper(), symbol[3:6].upper()
        for record in records:
            if record.status.value != "open":
                continue
            other_base, other_quote = record.symbol[:3].upper(), record.symbol[3:6].upper()
            if {base, quote} & {other_base, other_quote}:
                correlated += 1

    derived: dict[str, Any] = {
        "trades_today": len(today_trades),
        "daily_pnl_percent": (daily_pnl / equity * 100.0) if equity else None,
        "weekly_pnl_percent": (weekly_pnl / equity * 100.0) if equity else None,
        "consecutive_losses": consecutive_losses,
        "correlated_positions": correlated,
    }
    summary = ", ".join(
        f"{key}={value:g}" if isinstance(value, float) else f"{key}={value}"
        for key, value in derived.items()
    )
    print(f"  journal-derived state: {summary}")
    return derived

def cmd_rules(args: argparse.Namespace) -> int:
    from .core.rule_engine import SetupContext, evaluate_setup, load_rules

    derived: dict[str, Any] = {}
    journal_path = Path(args.journal) if getattr(args, "journal", None) else (
        ROOT / "data" / "journal" / "journal.csv"
    )
    if getattr(args, "from_journal", False):
        if journal_path.is_file():
            derived = _state_from_journal(journal_path, args.symbol, args.equity)
        else:
            _warn(f"no journal at {journal_path}; state inputs cannot be derived")

    def pick(name: str, value: Any) -> Any:
        return value if value is not None else derived.get(name)

    extra: dict[str, Any] = {}
    if args.setup:
        extra["setup_name"] = args.setup
    context = SetupContext(
        symbol=args.symbol,
        direction=args.direction,
        timeframe=args.timeframe,
        risk_percent=args.risk,
        stop_pips=args.stop_pips,
        reward_risk=args.rr,
        account_equity=args.equity,
        spread_pips=args.spread,
        atr_pips=args.atr,
        session=args.session,
        minutes_to_high_impact_news=args.news_in,
        minutes_since_high_impact_news=args.news_since,
        major_central_bank_event_today=args.central_bank_day,
        trades_today=pick("trades_today", args.trades_today),
        daily_pnl_percent=pick("daily_pnl_percent", args.daily_pnl),
        weekly_pnl_percent=pick("weekly_pnl_percent", args.weekly_pnl),
        consecutive_losses=pick("consecutive_losses", args.consecutive_losses),
        correlated_positions=pick("correlated_positions", args.correlated),
        portfolio_heat_percent=args.heat,
        higher_timeframe_bias=args.htf_bias,
        structure_clear=args.structure_clear,
        level_defined=args.level_defined,
        invalidation_defined=args.invalidation_defined,
        entry_trigger_defined=args.trigger_defined,
        checklist_complete=args.checklist,
        setups_taken_from_plan=args.from_plan,
        screenshot_taken=args.screenshot,
        emotional_state=args.emotional_state,
        slept_well=args.slept_well,
        had_loss_today=args.had_loss,
        revenge_urge=args.revenge,
        extra=extra,
    )
    try:
        rules = load_rules(args.config)
    except Exception as exc:
        _fail(str(exc))
        return 1
    decision = evaluate_setup(context, rules)
    print(decision.report())
    return 0 if decision.approved else 3


def cmd_journal(args: argparse.Namespace) -> int:
    from .journal.model import TradeRecord
    from .journal.storage import JournalStore, default_journal_path

    path = Path(args.journal) if args.journal else default_journal_path(ROOT)
    store = JournalStore(path)

    if args.action == "new":
        store.ensure_template()
        print(f"journal ready: {path}")
        return 0

    if args.action == "add":
        record = TradeRecord(
            trade_id=args.id or store.next_trade_id(),
            date=args.date or date.today().isoformat(),
            symbol=args.symbol,
            direction=args.direction,
            entry=args.entry,
            stop_loss=args.stop,
            take_profit=args.take_profit,
            lots=args.lots,
            account_equity_at_entry=args.equity,
            risk_percent=args.risk,
            planned_rr=args.planned_rr,
            session=args.session,
            timeframe=args.timeframe,
            setup=args.setup,
            reason_for_entry=args.reason or "",
            invalidation=args.invalidation or "",
            emotional_state=args.emotional_state,
            screenshot_before=args.screenshot_before or "",
        )
        store.add(record)
        print(f"recorded {record.trade_id}: {record.symbol} {record.direction.value} "
              f"risk {record.risk_amount:.4f}" if record.risk_amount else record.trade_id)
        print("  next: close it with  python main.py journal close --id "
              f"{record.trade_id} --exit-price ... --pnl ...")
        return 0

    if args.action == "close":
        record = store.close_trade(
            args.id,
            exit_price=args.exit_price,
            pnl=args.pnl,
            reason_for_exit=args.reason or "",
            thesis_valid=args.thesis_valid,
            lesson=args.lesson or "",
        )
        r = record.r_multiple
        print(f"closed {record.trade_id}: P/L {record.pnl:+.2f}  "
              f"R {r:+.2f}" if r is not None else f"closed {record.trade_id}")
        return 0

    if args.action == "list":
        records = store.load()
        if not records:
            print("no trades recorded yet")
            return 0
        print(f"{'id':<10}{'date':<12}{'symbol':<9}{'dir':<7}{'lots':>7}{'R':>8}{'P/L':>10}"
              f"  quality  status")
        for record in records[-args.limit:]:
            r = record.r_multiple
            print(
                f"{record.trade_id:<10}{str(record.date):<12}{record.symbol:<9}"
                f"{record.direction.value:<7}{record.lots:>7.2f}"
                f"{(f'{r:+.2f}' if r is not None else '-'):>8}"
                f"{(f'{record.pnl:+.2f}' if record.pnl is not None else '-'):>10}"
                f"  {str(record.setup_quality.value if hasattr(record.setup_quality, 'value') else '-'):<8}"
                f" {record.status.value}"
            )
        return 0

    if args.action == "summary":
        _print_json(store.summary())
        return 0

    return 1


def cmd_report(args: argparse.Namespace) -> int:
    from .analytics.performance import analyse_journal
    from .journal.storage import default_journal_path

    journal = Path(args.journal) if args.journal else default_journal_path(ROOT)
    if not Path(journal).is_file():
        _fail(f"journal not found: {journal}")
        print("  create one with:  python main.py journal new")
        return 1
    result = analyse_journal(journal, starting_equity=args.equity)
    print(result.report.report())

    print("\nNEXT ACTIONS (derived from the data above)")
    for index, item in enumerate(result.summary["calls_to_action"], start=1):
        print(f"  {index}. {item}")

    outdir = Path(args.outdir) if args.outdir else ROOT / "outputs"
    outdir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    from .analytics.performance import write_breakdown_csvs, write_equity_curve_csv

    written.append(write_equity_curve_csv(result.report, outdir / "equity_curve.csv"))
    written.extend(write_breakdown_csvs(result.report, outdir / "breakdowns"))
    if args.json:
        written.append(result.to_json(outdir / "performance.json"))

    if args.charts:
        from .analytics.charts import build_all_charts, charts_available

        if not charts_available():
            _warn("matplotlib is not installed; skipping charts (pip install matplotlib)")
        else:
            written.extend(build_all_charts(result.report, outdir / "charts", args.equity))

    if args.pdf:
        from .reports.performance_pdf import build_performance_pdf

        try:
            written.append(
                build_performance_pdf(result, outdir / "performance_report.pdf", args.equity)
            )
        except RuntimeError as exc:
            _warn(str(exc))

    print("\nFILES WRITTEN")
    for path in written:
        print(f"  {path}")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    from .program.demo_program import demo_programme, format_day, format_week, phases

    if args.list:
        print("=" * 78)
        print("90-DAY DEMO PROGRAMME")
        print("=" * 78)
        for phase in phases():
            print(f"  Phase {phase.number}: {phase.name}  (weeks {phase.weeks}, {phase.level_refs})")
            print(f"      objective: {phase.objective}")
            print(f"      gate     : {phase.gate.name} - {len(phase.gate.conditions)} conditions")
            if phase.warning:
                print(f"      !! {phase.warning}")
        print("-" * 78)
        print(f"  {len(demo_programme())} daily tasks defined (13 weeks x 7 days)")
        print("  Show one day:  python main.py demo --day 12")
        return 0
    if args.day:
        print(format_day(args.day))
        return 0
    if args.week:
        print(format_week(args.week))
        return 0
    print(format_day(1))
    print("\n(tip: --list shows the ten phases and their gates; --day N or --week N for detail)")
    return 0


def cmd_quiz(args: argparse.Namespace) -> int:
    from .quiz.engine import (
        bank_path,
        format_question,
        grade_answers,
        list_categories,
        load_bank,
        record_result,
        select_questions,
    )

    try:
        bank = load_bank()
    except Exception as exc:
        _fail(f"could not load question bank: {exc}")
        return 1

    if args.list:
        counts = list_categories(bank)
        print("=" * 74)
        print(f"QUESTION BANK - {len(bank)} questions  ({bank_path()})")
        print("=" * 74)
        for category, count in sorted(counts.items()):
            print(f"  {category:<36} {count}")
        print("-" * 74)
        print("  Answers are hidden during a test. Use --answers to see explanations")
        print("  AFTER committing to answers.")
        return 0

    questions = select_questions(
        bank, category=args.category, difficulty=args.difficulty, n=args.n, seed=args.seed
    )
    if not questions:
        _fail("no questions matched those filters")
        return 1

    interactive = args.interactive and sys.stdin is not None and sys.stdin.isatty()
    responses: list[str | None] = []
    for index, question in enumerate(questions, start=1):
        print(format_question(question, index, len(questions)))
        if interactive:
            try:
                response = input("   your answer: ").strip()
            except EOFError:
                response = ""
        else:
            response = args.answer[index - 1] if args.answer and index <= len(args.answer) else None
        responses.append(response)

    result = grade_answers(questions, responses, seed=args.seed)
    print(result.report(show_explanations=args.answers or not interactive))
    if args.record:
        record_result(result)
        print("  recorded to outputs/progress.json")
    return 0 if result.score >= 70 else 4


def cmd_progress(args: argparse.Namespace) -> int:
    from .program.demo_program import (
        format_mastery,
        load_progress,
        mastery_score,
        record_category_scores,
        record_gate_result,
        save_progress,
    )
    from .quiz.engine import mastery_scores_from_quiz

    if args.action == "update":
        scores: dict[str, float] = {}
        for item in args.score or []:
            key, _, value = item.partition("=")
            try:
                scores[key.strip()] = float(value)
            except ValueError:
                _fail(f"--score expects key=value, got {item!r}")
                return 1
        if scores:
            record_category_scores(scores)
            print(f"updated {len(scores)} category score(s)")
        return 0

    if args.action == "gate":
        record_gate_result(args.phase, args.passed, args.notes or "")
        print(f"phase {args.phase} gate recorded as {'PASSED' if args.passed else 'NOT PASSED'}")
        return 0

    progress = load_progress()
    scores = dict(progress.get("categories", {}))
    from_quiz = mastery_scores_from_quiz(progress)
    merged = {**from_quiz, **scores}
    summary = mastery_score(merged)
    print(format_mastery(summary["score"], merged))
    if summary["missing_categories"]:
        print("  not yet assessed (no evidence):", ", ".join(summary["missing_categories"]))
    print("  categories with quiz evidence only are marked low on purpose:")
    print("  risk_management and execution require journal evidence, not quiz scores.")
    if args.save:
        progress.setdefault("categories", {}).update(merged)
        save_progress(progress)
        print(f"  saved to {ROOT / 'outputs' / 'progress.json'}")
    return 0


def cmd_readiness(args: argparse.Namespace) -> int:
    from .program.demo_program import (
        READINESS_CRITERIA,
        format_readiness_criteria,
        readiness_report,
    )

    if args.criteria or not args.set:
        print(format_readiness_criteria())
        if not args.set:
            print("\nTo assess yourself:")
            for criterion in READINESS_CRITERIA:
                print(f"  --set {criterion.key}=yes")
            print("  (answering nothing counts as NOT MET, by design)")
        return 0

    answers: dict[str, bool] = {}
    for item in args.set:
        key, _, value = item.partition("=")
        answers[key.strip()] = value.strip().lower() in {"y", "yes", "true", "1"}
    report = readiness_report(answers)
    print(report["text"])
    return 0 if report["failed_hard"] == [] else 5



def cmd_broker(args: argparse.Namespace) -> int:
    """Show documented broker conditions: account types, stop-out levels, HMR."""
    from .core.broker import (
        broker_profile,
        format_account_table,
        format_hmr_summary,
        stop_out_level,
        verification_age_days,
    )

    profile = broker_profile()
    print(format_account_table())

    print()
    if args.hmr or args.all:
        print(format_hmr_summary())
        print()

    if args.account:
        entry = _account_or_exit(args.account)
        print(f"ACCOUNT TYPE: {entry.name}")
        print(f"  minimum initial deposit : {entry.minimum_initial_deposit}")
        print(f"  spread from             : "
              f"{'n/a' if entry.spread_from_pips is None else f'{entry.spread_from_pips:g} pips'}")
        print(f"  commission              : {entry.commission}")
        print(f"  margin call             : "
              f"{'?' if entry.margin_call_percent is None else f'{entry.margin_call_percent:g}%'}")
        print(f"  stop out                : "
              f"{'?' if entry.stop_out_percent is None else f'{entry.stop_out_percent:g}%'}")
        print(f"  documented on           : {profile.verified_on}  "
              f"(source: official Exness Help Center)")
        print(f"  notes                   : {entry.notes}")
        level = stop_out_level(entry.key)
        if level == 0.0:
            print()
            print("  A document-free warning: a 0% stop out is not protection. On a single")
            print("  position it means the broker may not close you until equity is essentially")
            print("  gone. Your own stop loss and your own size are the only limits that act")
            print("  before then.")
        print()
        print("  Confirm this in your own Personal Area before trading: conditions are")
        print("  region- and entity-specific and can change.")

    if args.check:
        age = verification_age_days(args.check)
        if age is None:
            _warn("could not compare dates; pass an ISO date such as --check 2026-09-15")
        else:
            print(f"  age of these figures on {args.check}: {age} days")
            if age > 90:
                _warn("older than a quarter - re-read the official sources before relying on them")

    print()
    print("Reminder: this records documented BROKER conditions, not a recommendation to")
    print("open, fund or trade any account. The 250 USD live step comes after the readiness")
    print("criteria pass:  python main.py readiness --criteria")
    return 0


def _account_or_exit(key: str):
    from .core.broker import account_type

    try:
        return account_type(key)
    except Exception as exc:
        _fail(str(exc))
        raise SystemExit(1)




def cmd_candles(args: argparse.Namespace) -> int:
    """Measure candle-pattern behaviour on data YOU supply. Never fabricates data."""
    from .core.candles import (
        PATTERN_RULES,
        analyse_pattern,
        load_bars_csv,
        pattern_description,
    )

    if args.rules:
        print("=" * 78)
        print("OBJECTIVE CANDLE PATTERN RULES")
        print("=" * 78)
        print(pattern_description("all"))
        print("-" * 78)
        print("  These are mechanical definitions, not opinions. A pattern is a shape in the")
        print("  data; whether it has any predictive value is a separate question that only")
        print("  measurement can answer - and the measurement is printed with its caveats.")
        return 0

    if not args.file:
        _fail("--file is required (a CSV with open, high, low, close columns)")
        print("  Obtain data you are permitted to use, for example free practice data:")
        print("    python main.py market --symbols EURUSD=X --period 2y --interval 1d")
        print("  then:  python main.py candles --file data/raw/EURUSD_X_1d.csv "
              "--pattern bullish_pin --forward 20")
        return 1

    try:
        bars = load_bars_csv(args.file, limit=args.limit)
    except Exception as exc:
        _fail(str(exc))
        return 1

    only_this = args.pattern or "all"
    targets = list(PATTERN_RULES) if only_this == "all" else [only_this]
    failures = 0
    for name in targets:
        try:
            stats = analyse_pattern(
                bars,
                name,
                forward=args.forward,
                barrier=args.barrier,
                direction_bias=args.bias,
                min_samples=args.min_samples,
            )
        except Exception as exc:
            _fail(f"{name}: {exc}")
            failures += 1
            continue
        print(stats.report())
        print()
    if failures and failures == len(targets):
        return 1
    print("  Reminder: this measures what happened in YOUR sample, gross of costs, with")
    print("  overlapping windows and a period you chose. It is a starting point for")
    print("  honest testing, not a signal and not a promise.")
    return 0



def cmd_lesson(args: argparse.Namespace) -> int:
    """List or print the lesson documents in docs/lessons/."""
    lessons_dir = ROOT / "docs" / "lessons"
    files = sorted(lessons_dir.glob("*.md")) if lessons_dir.is_dir() else []
    if not args.answers:
        # Answer keys are excluded from listing and never printed by accident: a test
        # you can read while answering it is not a test.
        files = [path for path in files if not path.stem.endswith("answer_key")]
    else:
        files = [path for path in files if path.stem.endswith("answer_key")]
    if not files:
        _fail(f"no lesson files found in {lessons_dir}")
        return 1
    if args.list or args.number is None:
        print("=" * 74)
        print("LESSONS")
        print("=" * 74)
        for path in files:
            print(f"  {path.stem:<58} {path.stat().st_size:>7,} bytes")
        print("-" * 74)
        print("  Print one with:  python main.py lesson --number 1")
        return 0
    match = [p for p in files if p.stem.startswith(f"{args.number:02d}") or
             p.stem.startswith(str(args.number))]
    if not match:
        _fail(f"no lesson numbered {args.number}")
        return 1
    print(match[0].read_text(encoding="utf-8"))
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    """Generate the documentation, workbook and notebook artefacts."""
    outdir = Path(args.outdir) if args.outdir else ROOT / "outputs"
    outdir.mkdir(parents=True, exist_ok=True)
    targets = {args.what} if args.what != "all" else {"excel", "pdf", "docx", "notebooks", "templates"}
    failures = 0

    if "excel" in targets:
        from .reports.excel_workbook import build_master_workbook, excel_available

        if not excel_available():
            _warn("skipping Excel: pip install XlsxWriter")
            failures += 1
        else:
            path = build_master_workbook(outdir / "Forex_Trading_Master.xlsx")
            _ok(f"Excel workbook -> {path}  (20 sheets)")

    if "pdf" in targets or "docx" in targets:
        from .reports.library import DOCUMENT_LIBRARY, build_documents

        results, problems = build_documents(
            which=targets & {"pdf", "docx"}, outdir=outdir, include_notebooks=False
        )
        for path in results:
            _ok(f"document -> {path}")
        for problem in problems:
            _warn(problem)
            failures += 1
        _ = DOCUMENT_LIBRARY

    if "notebooks" in targets:
        from .reports.notebooks import build_notebooks, nbformat_available

        if not nbformat_available():
            _warn("skipping notebooks: pip install nbformat (optional)")
            failures += 1
        else:
            paths = build_notebooks(ROOT / "notebooks")
            _ok(f"{len(paths)} notebooks written to {ROOT / 'notebooks'}")

    if "templates" in targets:
        from .reports.templates import write_all_templates

        paths = write_all_templates(outdir / "templates")
        _ok(f"{len(paths)} CSV/Markdown templates written to {outdir / 'templates'}")

    print("\nGenerated artefacts are git-ignored by default; regenerate any time with")
    print("  python main.py build all")
    return 0 if failures == 0 else 1


def cmd_market(args: argparse.Namespace) -> int:
    """Fetch free reference data for practice (never for live decisions)."""
    try:
        import yfinance  # type: ignore
    except Exception:
        _warn("yfinance is not installed; install it with: pip install yfinance")
        print("  This is optional. It downloads free proxy data so you can practise")
        print("  backtesting mechanics. It is NOT your broker's feed: spreads, session")
        print("  boundaries and gold pricing differ from Exness, so never size a live")
        print("  trade from it.")
        return 1

    symbols = [s.strip().upper() for s in (args.symbols or "EURUSD=X,GBPUSD=X,JPY=X,XAUUSD=X").split(",")]
    outdir = Path(args.outdir) if args.outdir else ROOT / "data" / "raw"
    outdir.mkdir(parents=True, exist_ok=True)
    print(f"downloading {len(symbols)} symbol(s) into {outdir}")
    for symbol in symbols:
        try:
            frame = yfinance.download(
                symbol, period=args.period, interval=args.interval, progress=False, auto_adjust=False
            )
        except Exception as exc:
            _warn(f"{symbol}: {exc}")
            continue
        if frame is None or frame.empty:
            _warn(f"{symbol}: no data returned")
            continue
        target = outdir / f"{symbol.replace('=', '_')}_{args.interval}.csv"
        frame.to_csv(target)
        _ok(f"{target.name}: {len(frame)} rows")
    print("\nReminder: practice data only. Confirm every backtest assumption against")
    print("your broker's own historical data before drawing conclusions.")
    return 0


def cmd_version(args: argparse.Namespace) -> int:
    from . import __version__

    print(f"forex-mastery {__version__}")
    print("Core calculation engine: standard library only, unit-tested.")
    print("See README.md for the architecture and docs/00_MASTER_ROADMAP.md for the curriculum.")
    return 0


# ---------------------------------------------------------------------- #
# Parser
# ---------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description=(
            "Forex Mastery System - education, risk management, journaling, analytics and "
            "documentation for a disciplined approach to FX trading. Nothing here predicts the "
            "market; everything here measures, sizes and audits."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "EXAMPLES\n"
            "  python main.py doctor\n"
            "  python main.py position --symbol EURUSD --balance 250 --risk 0.25 "
            "--entry 1.1000 --stop 1.0950 --take-profit 1.1100 --leverage 100\n"
            "  python main.py position --symbol USDJPY --balance 1000 --risk 1 --entry 150.00 "
            "--stop 149.70 --price USDJPY=150.0\n"
            "  python main.py drawdown --balance 250\n"
            "  python main.py rules --symbol EURUSD --direction long --risk 0.25 --rr 2.0 "
            "--session London --stop-pips 45 --news-in 240 --trades-today 0 --htf-bias bullish "
            "--emotional-state calm --checklist --from-plan --screenshot "
            "--structure-clear --level-defined --invalidation-defined --trigger-defined "
            "--setups-trend_pullback\n"
            "  python main.py journal add --symbol EURUSD --direction long --entry 1.1 "
            "--stop 1.095 --lots 0.01 --equity 250 --risk 0.25\n"
            "  python main.py report --charts --pdf\n"
            "  python main.py demo --list\n"
            "  python main.py quiz --category risk_management --n 10 --interactive\n"
            "  python main.py build all\n"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="check environment, config and calculations").set_defaults(
        func=cmd_doctor
    )

    p = sub.add_parser("specs", help="show instrument specifications")
    p.add_argument("--symbol")
    p.add_argument("--group")
    p.set_defaults(func=cmd_specs)

    p = sub.add_parser("pip", help="pip value calculator")
    p.add_argument("--symbol", required=True)
    p.add_argument("--lots", type=float, default=1.0)
    p.add_argument("--account-ccy", default="USD")
    p.add_argument("--pips", type=float, default=None, help="also value this many pips")
    p.add_argument("--price", action="append", help="conversion price, e.g. --price USDJPY=150.0")
    p.set_defaults(func=cmd_pip)

    for name, help_text in (("position", "risk-based position size calculator"),
                            ("size", "alias for position")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--symbol", required=True)
        p.add_argument("--balance", type=float, required=True, help="account equity")
        p.add_argument("--entry", type=float, required=True)
        p.add_argument("--stop", type=float, required=True)
        p.add_argument("--take-profit", type=float, default=None)
        p.add_argument("--risk", type=float, default=0.5, help="risk percent (default 0.5)")
        p.add_argument("--risk-amount", type=float, default=None, help="risk in account currency")
        p.add_argument("--account-ccy", default="USD")
        p.add_argument("--leverage", type=float, default=None, help="broker leverage, e.g. 100")
        p.add_argument("--spread", type=float, default=None, help="current spread in pips")
        p.add_argument("--atr", type=float, default=None, help="ATR in pips, for stop sanity checks")
        p.add_argument("--commission", type=float, default=0.0,
                       help="round-turn commission per 1.00 lot")
        p.add_argument("--min-rr", type=float, default=1.5)
        p.add_argument("--price", action="append", help="conversion price, e.g. --price USDJPY=150.0")
        p.add_argument("--json", action="store_true")
        p.set_defaults(func=cmd_position)

    p = sub.add_parser("scenarios", help="compare risk percentages on one setup")
    p.add_argument("--symbol", required=True)
    p.add_argument("--balance", type=float, required=True)
    p.add_argument("--entry", type=float, required=True)
    p.add_argument("--stop", type=float, required=True)
    p.add_argument("--risks", type=float, nargs="+", default=[0.10, 0.25, 0.50, 1.00])
    p.add_argument("--leverage", type=float, default=None)
    p.add_argument("--price", action="append")
    p.set_defaults(func=cmd_scenarios)

    p = sub.add_parser("drawdown", help="drawdown ladder for an account")
    p.add_argument("--balance", type=float, default=250.0)
    p.set_defaults(func=cmd_drawdown)

    p = sub.add_parser("ruin", help="Monte Carlo risk-of-ruin simulation")
    p.add_argument("--win-rate", type=float, required=True, help="e.g. 0.45")
    p.add_argument("--rr", type=float, default=1.5, help="reward:risk, e.g. 1.5")
    p.add_argument("--risk", type=float, default=0.25, help="risk percent per trade")
    p.add_argument("--trades", type=int, default=500)
    p.add_argument("--paths", type=int, default=20000)
    p.add_argument("--equity", type=float, default=250.0)
    p.add_argument("--ruin", type=float, default=0.5, help="ruin threshold as a fraction (0.5 = -50%)")
    p.add_argument("--cost", type=float, default=0.0, help="round-trip cost in R")
    p.add_argument("--seed", type=int, default=42)
    p.set_defaults(func=cmd_ruin)

    p = sub.add_parser("compound", help="expected growth projection (with caveats)")
    p.add_argument("--win-rate", type=float, required=True)
    p.add_argument("--rr", type=float, default=1.5)
    p.add_argument("--risk", type=float, default=0.25)
    p.add_argument("--trades", type=int, default=250)
    p.add_argument("--equity", type=float, default=250.0)
    p.add_argument("--cost", type=float, default=0.0)
    p.set_defaults(func=cmd_compound)

    p = sub.add_parser("sessions", help="session timetable in UTC and your timezone")
    p.add_argument("--date", help="ISO date, e.g. 2026-09-15")
    p.add_argument("--tz", default=None, help="your IANA timezone, e.g. Asia/Kolkata")
    p.add_argument("--explain", action="store_true", help="describe each session's character")
    p.set_defaults(func=cmd_sessions)

    p = sub.add_parser("rules", help="evaluate a setup against config/strategy_rules.json")
    p.add_argument("--symbol", default=None)
    p.add_argument("--direction", default=None, choices=[None, "long", "short"])
    p.add_argument("--timeframe", default=None)
    p.add_argument("--risk", type=float, default=None)
    p.add_argument("--rr", type=float, default=None)
    p.add_argument("--stop-pips", type=float, default=None)
    p.add_argument("--equity", type=float, default=None)
    p.add_argument("--spread", type=float, default=None)
    p.add_argument("--atr", type=float, default=None)
    p.add_argument("--session", default=None)
    p.add_argument("--news-in", type=int, default=None, dest="news_in",
                   help="minutes until the next high-impact release")
    p.add_argument("--news-since", type=int, default=None, dest="news_since")
    p.add_argument("--central-bank-day", action="store_true", default=None)
    p.add_argument("--trades-today", type=int, default=None)
    p.add_argument("--daily-pnl", type=float, default=None, help="today's P/L in percent")
    p.add_argument("--weekly-pnl", type=float, default=None)
    p.add_argument("--consecutive-losses", type=int, default=None)
    p.add_argument("--correlated", type=int, default=None, help="positions sharing one currency story")
    p.add_argument("--heat", type=float, default=None, help="total portfolio heat in percent")
    p.add_argument("--htf-bias", default=None, choices=[None, "bullish", "bearish", "range"])
    p.add_argument("--structure-clear", action="store_true", default=None)
    p.add_argument("--level-defined", action="store_true", default=None)
    p.add_argument("--invalidation-defined", action="store_true", default=None)
    p.add_argument("--trigger-defined", action="store_true", default=None, dest="trigger_defined")
    p.add_argument("--checklist", action="store_true", default=None)
    p.add_argument("--from-plan", action="store_true", default=None)
    p.add_argument("--screenshot", action="store_true", default=None)
    p.add_argument("--emotional-state", default=None)
    p.add_argument("--slept-well", action="store_true", default=None)
    p.add_argument("--had-loss", action="store_true", default=None, dest="had_loss")
    p.add_argument("--revenge", action="store_true", default=None)
    p.add_argument("--setups", default=None, dest="setup", help="setup name, e.g. trend_pullback")
    p.add_argument("--config", default=None, help="path to a custom rules JSON")
    p.add_argument("--journal", default=None, help="journal path for --from-journal")
    p.add_argument("--from-journal", action="store_true", dest="from_journal",
                   help="derive trades today, daily/weekly P/L, loss streak and correlated "
                        "positions from your journal instead of typing them")
    p.set_defaults(func=cmd_rules)

    p = sub.add_parser("journal", help="create, add to, close and summarise the journal")
    p.add_argument("action", choices=["new", "add", "close", "list", "summary"])
    p.add_argument("--journal", default=None)
    p.add_argument("--id", default=None)
    p.add_argument("--date", default=None)
    p.add_argument("--symbol", default=None)
    p.add_argument("--direction", default="long", choices=["long", "short"])
    p.add_argument("--entry", type=float, default=None)
    p.add_argument("--stop", type=float, default=None)
    p.add_argument("--take-profit", type=float, default=None)
    p.add_argument("--lots", type=float, default=0.0)
    p.add_argument("--equity", type=float, default=None)
    p.add_argument("--risk", type=float, default=None)
    p.add_argument("--planned-rr", type=float, default=None)
    p.add_argument("--session", default=None)
    p.add_argument("--timeframe", default=None)
    p.add_argument("--setup", default=None)
    p.add_argument("--reason", default=None)
    p.add_argument("--invalidation", default=None)
    p.add_argument("--emotional-state", default=None)
    p.add_argument("--screenshot-before", default=None)
    p.add_argument("--exit-price", type=float, default=None)
    p.add_argument("--pnl", type=float, default=None)
    p.add_argument("--thesis-valid", action="store_true", default=None)
    p.add_argument("--lesson", default=None)
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_journal)

    p = sub.add_parser("report", help="performance analytics from the journal")
    p.add_argument("--journal", default=None)
    p.add_argument("--equity", type=float, default=250.0, help="starting equity")
    p.add_argument("--charts", action="store_true")
    p.add_argument("--pdf", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--outdir", default=None)
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("demo", help="the 90-day demo programme")
    p.add_argument("--day", type=int, default=None)
    p.add_argument("--week", type=int, default=None)
    p.add_argument("--list", action="store_true")
    p.set_defaults(func=cmd_demo)

    p = sub.add_parser("quiz", help="question bank and tests (answers hidden by default)")
    p.add_argument("--category", choices=[None, "beginner", "market_mechanics", "technical_analysis",
                                         "fundamental_analysis", "risk_management", "psychology",
                                         "strategy", "statistics", "backtesting",
                                         "professional_decision_making"], default=None)
    p.add_argument("--difficulty", type=int, choices=[None, 1, 2, 3, 4], default=None)
    p.add_argument("--n", type=int, default=10)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--interactive", action="store_true")
    p.add_argument("--answers", action="store_true", help="show explanations after grading")
    p.add_argument("--answer", nargs="*", default=None, help="non-interactive answers, in order")
    p.add_argument("--record", action="store_true", help="save the result to outputs/progress.json")
    p.add_argument("--list", action="store_true")
    p.set_defaults(func=cmd_quiz)

    p = sub.add_parser("progress", help="mastery scorecard and gate tracking")
    p.add_argument("action", nargs="?", default="show", choices=["show", "update", "gate"])
    p.add_argument("--score", action="append", help="category=value (0-100), repeatable")
    p.add_argument("--phase", type=int, default=None)
    p.add_argument("--passed", action="store_true")
    p.add_argument("--notes", default=None)
    p.add_argument("--save", action="store_true")
    p.set_defaults(func=cmd_progress)

    p = sub.add_parser("readiness", help="live-account readiness assessment (strict)")
    p.add_argument("--criteria", action="store_true", help="list the criteria")
    p.add_argument("--set", action="append", help="criterion=yes|no, repeatable")
    p.set_defaults(func=cmd_readiness)

    p = sub.add_parser("candles", help="measure candle-pattern behaviour on OHLC data you supply")
    p.add_argument("--file", default=None, help="CSV with open, high, low, close columns")
    p.add_argument("--pattern", default=None,
                   help="one pattern name, or omit for all of them")
    p.add_argument("--forward", type=int, default=20, help="bars to look ahead (default 20)")
    p.add_argument("--barrier", type=float, default=1.0,
                   help="R multiple for the favourable-before-adverse test (default 1.0)")
    p.add_argument("--bias", default="candle", choices=["candle", "long", "short"],
                   help="direction to measure: the candle's own, always long, or always short")
    p.add_argument("--min-samples", type=int, default=1, dest="min_samples",
                   help="refuse to report below this many occurrences")
    p.add_argument("--limit", type=int, default=None, help="only load the first N bars")
    p.add_argument("--rules", action="store_true", help="print the objective pattern rules")
    p.set_defaults(func=cmd_candles)

    p = sub.add_parser("broker", help="documented broker conditions: account types, "
                                      "stop-out levels, higher margin requirements")
    p.add_argument("--account", default=None,
                   help="detail one account type: standard_cent, standard, pro, raw_spread, zero")
    p.add_argument("--hmr", action="store_true",
                   help="also print the higher-margin-requirement windows (weekend and news)")
    p.add_argument("--all", action="store_true", help="everything")
    p.add_argument("--check", default=None, metavar="ISO_DATE",
                   help="report how old the documented figures are on that date")
    p.set_defaults(func=cmd_broker)

    p = sub.add_parser("lesson", help="list or print the lesson documents")
    p.add_argument("--number", type=int, default=None)
    p.add_argument("--list", action="store_true")
    p.add_argument("--answers", action="store_true",
                   help="show the answer key instead of the lesson (only after you have "
                        "committed to your own answers)")
    p.set_defaults(func=cmd_lesson)

    p = sub.add_parser("build", help="generate Excel, PDF/DOCX, notebooks and templates")
    p.add_argument("what", nargs="?", default="all",
                   choices=["all", "excel", "pdf", "docx", "notebooks", "templates"])
    p.add_argument("--outdir", default=None)
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("market", help="download free practice data (optional, not for live use)")
    p.add_argument("--symbols", default=None, help="comma-separated, e.g. EURUSD=X,JPY=X")
    p.add_argument("--period", default="2y")
    p.add_argument("--interval", default="1d")
    p.add_argument("--outdir", default=None)
    p.set_defaults(func=cmd_market)

    sub.add_parser("version", help="print the version").set_defaults(func=cmd_version)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130
    except Exception as exc:  # pragma: no cover - top-level guard for CLI use
        _fail(f"{type(exc).__name__}: {exc}")
        if "--traceback" in (argv or sys.argv):
            raise
        print("  (re-run with --traceback for the full stack trace)", file=sys.stderr)
        return 1
