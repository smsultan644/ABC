"""
The 90-day demo trading programme (Level 23) and the mastery/readiness framework
(Levels 37, 38).

HOW THIS IS STRUCTURED
----------------------
Thirteen weeks, ten phases, with a **gate** at the end of each phase. A gate is a
list of objective conditions; if any is unmet you repeat the phase. Gates are the
reason this is a programme and not a reading list.

Daily tasks are given as *templates with time budgets* rather than as 90 unique
scripts. That is deliberate honesty: nobody can predict which day EURUSD will
give you a textbook pullback, and a rigid daily script would teach you to force
setups to match the calendar. What is fixed is the **weekly rhythm**:

    Mon  market preparation and written plan
    Tue  study block (theory, quiz) + review of the plan
    Wed  execution practice (demo) with journaling
    Thu  study block + chart-marking drills
    Fri  execution practice + weekly review
    Sat  statistics: update journal, compute performance, no trading
    Sun  rest, plan next week, verify the calendar

RULES OF THE PROGRAMME
----------------------
1. **No live money** until every readiness criterion in
   :func:`assess_readiness` is met, and the assessment is run three weeks apart
   with consistent results.
2. **Risk never exceeds 0.25%** during the programme. This is not timidity: a
   250 USD account at 0.25% is a 0.63 USD loss per trade, which is the price of
   a coffee. The account's job is to buy experience cheaply.
3. **Backtest before forward test.** A strategy that has not been measured has
   not been studied, only believed.
4. **Rules change only in writing, only at a scheduled review, never during a
   drawdown.** If you break this, you are not following a system.
5. **Journaling is not optional.** A day without a journal entry is a day that
   produced no evidence.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable

__all__ = [
    "DailyTask",
    "Gate",
    "Phase",
    "MasteryCategory",
    "MASTERY_CATEGORIES",
    "READINESS_CRITERIA",
    "demo_programme",
    "format_day",
    "format_week",
    "mastery_level",
    "mastery_score",
    "progress_path",
    "readiness_report",
    "load_progress",
    "save_progress",
]


# ---------------------------------------------------------------------- #
# Programme data
# ---------------------------------------------------------------------- #
@dataclass(frozen=True)
class DailyTask:
    """One task on one day, with an explicit time budget."""

    day_offset: int          # 1..90 relative to programme start
    weekday: str
    title: str
    detail: str
    minutes: int
    deliverable: str = ""


@dataclass(frozen=True)
class Gate:
    """Objective conditions required to leave a phase."""

    name: str
    conditions: list[str]


@dataclass(frozen=True)
class Phase:
    """One phase of the programme."""

    number: int
    name: str
    weeks: str
    level_refs: str
    objective: str
    study: list[str]
    exercises: list[str]
    demo_tasks: list[str]
    gate: Gate
    warning: str = ""


_PHASES: tuple[Phase, ...] = (
    Phase(
        1, "Market education and mechanics", "1-2", "Levels 0-3",
        "Understand what the FX market is, who is in it, and what actually happens "
        "when you click buy or sell - before touching a chart pattern.",
        [
            "Level 0: asset classes, OTC vs exchange, market participants",
            "Level 1: pairs, base/quote, pip, lot, spread, swap, leverage, margin",
            "Level 2: Exness account structure, demo setup, MT5 navigation",
            "Level 3: why price moves, bid/ask, order flow, liquidity",
        ],
        [
            "Open a demo account and place/cancel a limit order purely to observe what happens",
            "Compute pip value by hand for EURUSD, USDJPY and XAUUSD; check against the toolkit",
            "Find the spread, swap and margin requirement for three instruments in MT5",
        ],
        [
            "Watch one major pair for a full London session without trading",
            "Write 10 observations about how price behaved and how spreads changed",
        ],
        Gate(
            "Mechanics gate",
            [
                "Can explain bid/ask and why the spread is an immediate cost",
                "Can compute pip value for USD-quoted, JPY-quoted and gold instruments by hand",
                "Can explain the difference between leverage and risk",
                "Quiz score >= 70% on the 'beginner' and 'market mechanics' categories",
            ],
        ),
    ),
    Phase(
        2, "Chart reading", "2-4", "Levels 4-6, 8",
        "Read a bare chart: candles, structure, levels, and which timeframe is telling the truth.",
        [
            "Level 4: OHLC, candle anatomy, the twelve patterns that matter",
            "Level 5: swings, HH/HL/LH/LL, trend, range, transition",
            "Level 6: horizontal levels, zones, round numbers, session highs/lows",
            "Level 8: multi-timeframe top-down analysis procedure",
        ],
        [
            "Mark 30 historical charts: label the regime (trend/range/transition) before looking forward",
            "Identify 50 candlestick patterns in context and record whether the location was sensible",
            "Build a level map for EURUSD, GBPUSD, XAUUSD on W1/D1/H4 for the last 6 months",
        ],
        [
            "Each day: mark levels on your watchlist in the morning, then compare with the day's actual behaviour in the evening",
        ],
        Gate(
            "Chart reading gate",
            [
                "Regime (trend/range/transition) identified correctly on 70% of 30 blind charts",
                "A written top-down analysis procedure you can repeat in under 15 minutes",
                "Can explain why a candlestick pattern alone is not a strategy",
                "Quiz score >= 70% on 'technical analysis'",
            ],
        ),
    ),
    Phase(
        3, "Risk management mastery (mandatory - cannot be skipped)", "4-5", "Levels 15-16, 39",
        "Make position sizing, drawdown maths and expectancy automatic. This phase is a gate, not a topic.",
        [
            "Level 15: risk per trade, R-multiples, expectancy, drawdown, ruin",
            "Level 16: position sizing from stop distance (the correct order of operations)",
            "Level 39: the USD 250 framework at 0.10/0.25/0.50/1.00% risk",
        ],
        [
            "Size 25 hypothetical trades by hand; then verify every one with the CLI",
            "Compute the number of consecutive losses to -10% and -50% at four risk levels",
            "Run the risk-of-ruin simulation for 0.25%, 1% and 5% risk and explain the difference",
            "Explain in writing why recovery after a 50% drawdown needs a 100% gain",
        ],
        [
            "Open no positions this phase unless the sizing is pre-calculated and matches the plan",
        ],
        Gate(
            "Risk gate (hard requirement)",
            [
                "Position size computed correctly for 10/10 varied examples (majors, JPY, gold, cross)",
                "Can state your risk per trade in money for your account, without looking it up",
                "Can explain what R-multiple means and compute it from P/L and risk",
                "Quiz score >= 80% on 'risk management' - higher than any other category",
            ],
        ),
        warning=(
            "If this gate is not passed, the programme stops here. Every known path to a blown "
            "retail account runs through this phase's material."
        ),
    ),
    Phase(
        4, "Strategy selection and rule writing", "5-7", "Levels 14, 26, 27",
        "Choose a small number of strategy families that fit your schedule, and write their rules so precisely that a stranger could execute them.",
        [
            "Level 14: thirteen strategy families and their failure conditions",
            "Level 26: the rule engine (turn your plan into IF-THEN logic)",
            "Level 27: the no-trade system",
        ],
        [
            "Write the rules for two setups (maximum) in the exact form: context, entry trigger, stop, target, invalidation, session, instrument",
            "Run 20 historical examples of each setup through the rule engine and record the verdicts",
            "Write your no-trade conditions explicitly and test them against a losing period",
        ],
        [
            "Trade no new ideas. Anything not in the written plan is, by definition, not a setup",
        ],
        Gate(
            "Strategy gate",
            [
                "Two setups fully specified in writing, with objective entry and invalidation rules",
                "Rule engine configured in config/strategy_rules.json and run successfully on a real setup",
                "A written no-trade list with at least 10 explicit conditions",
                "A stranger could execute the plan without asking you a question",
            ],
        ),
    ),
    Phase(
        5, "Backtesting", "7-9", "Levels 21-22",
        "Measure the setups on historical data before risking anything, and learn why 20 trades prove nothing.",
        [
            "Level 21: manual backtesting method, sample size, in/out-of-sample, biases",
            "Level 22: the seven-stage validation process",
        ],
        [
            "Backtest setup A on 100+ trades by hand (bar replay), recording every trade including the ones you would rather skip",
            "Split the sample: 70% in-sample, 30% out-of-sample. Do not look at the out-of-sample set until the rules are frozen",
            "Compute expectancy with confidence intervals, profit factor, max drawdown and streak length",
            "Note the transaction-cost assumption (spread + commission) in every result",
        ],
        [
            "Compare your backtest with the simulation: is the drawdown you experienced consistent with what the maths predicted?",
        ],
        Gate(
            "Backtest gate",
            [
                ">= 100 backtested trades for the primary setup, with rules frozen before the out-of-sample test",
                "Out-of-sample expectancy still positive after costs",
                "Max drawdown from the backtest is survivable at your risk level (<= 10%)",
                "Written record of the conditions under which the strategy fails",
            ],
        ),
    ),
    Phase(
        6, "Demo forward testing", "9-11", "Levels 19-20, 23",
        "Execute the tested plan on demo, in real time, with real emotions and a complete journal.",
        [
            "Level 19: the trading journal and what each field is for",
            "Level 20: performance analysis - expectancy, drawdown, breakdowns",
        ],
        [
            "Take only the written setups, at the written risk, in the written sessions",
            "Journal every trade within 15 minutes of closing it, with before/after screenshots",
            "Run the analytics weekly; do not change the strategy mid-week",
        ],
        [
            "Maximum two trades per day, one open position, portfolio heat <= 0.5%",
        ],
        Gate(
            "Forward test gate",
            [
                ">= 40 live-demo trades executed exactly per plan",
                "Journal complete: no missing screenshots, risks or reasons",
                "Rule violation rate <= 10%",
                "Positive or break-even expectancy over the sample (if negative, return to Phase 5)",
            ],
        ),
    ),
    Phase(
        7, "Execution practice and consistency", "11-12", "Levels 28, 40",
        "Turn the plan into a routine that you can execute when you are tired, bored or annoyed.",
        [
            "Level 28: the toolkit (position size, R:R, drawdown, correlation exposure)",
            "Level 40: the professional trading routine (before/during/after)",
        ],
        [
            "Run the full pre-market routine every trading day for two weeks",
            "Practise pending-order entry, partial close, break-even moves and manual exits - each with written rules",
            "Rehearse the no-trade decision: take a day where you plan a trade and correctly decline it",
        ],
        [
            "Consistency drill: identical process on five consecutive sessions, regardless of results",
        ],
        Gate(
            "Execution gate",
            [
                "Pre-market routine completed on >= 8 of 10 trading days",
                "No trade taken without a pre-calculated position size",
                "At least one day where a valid-looking setup was declined and the reason was written down",
                "No stop loss widened or removed after entry",
            ],
        ),
    ),
    Phase(
        8, "Psychology and discipline", "12-13", "Levels 17, 27, 40",
        "Identify your specific failure modes and build mechanical defences against them.",
        [
            "Level 17: biases, loss aversion, revenge trading, overtrading and their checklists",
        ],
        [
            "Review the psychology journal for recurring triggers and name your top three",
            "Write a specific counter-measure for each (for example: 'after two losses I close the platform for the day')",
            "Practise the psychological checklists before, during and after trades for a week",
        ],
        [
            "Any trade taken in a poor state must be recorded as such and counted as a violation even if it won",
        ],
        Gate(
            "Psychology gate",
            [
                "Three named personal failure modes with written counter-measures",
                "Zero revenge trades (a trade within 60 minutes of a loss with increased size or no plan) in the last 20 trades",
                "Able to describe accurately what your emotional state was during your last 10 trades",
            ],
        ),
    ),
    Phase(
        9, "Performance analysis", "13", "Levels 20, 33",
        "Learn to read your own data: where the money actually comes from, and what to change first.",
        [
            "Statistical thinking: sample size, confidence intervals, overfitting, multiple testing",
        ],
        [
            "Run the analytics report and interpret it in writing - not just read the numbers",
            "Break performance down by setup, session, instrument, weekday and quality grade",
            "Identify the single largest source of lost R and write a specific correction",
        ],
        ["Produce a one-page monthly report you would be comfortable showing another trader"],
        Gate(
            "Analysis gate",
            [
                "Can interpret expectancy with a confidence interval and explain what it does not say",
                "Can identify the biggest loss source from the data, with evidence",
                "One process improvement identified per month - and only one",
            ],
        ),
    ),
    Phase(
        10, "Readiness assessment", "13", "Levels 37-39",
        "Decide, against strict written criteria, whether a small live account is justified.",
        [
            "Level 37: mastery scorecard",
            "Level 38: live account readiness criteria",
            "Level 39: the USD 250 capital plan",
        ],
        [
            "Complete the scorecard honestly; have someone else read your journal and check it",
            "Run the readiness assessment three times, a week apart, on settled data",
            "If not ready: write down exactly which criteria failed and what evidence will satisfy them",
        ],
        [
            "Continue demo trading if any hard criterion is unmet. There is no penalty for that, "
            "and a substantial penalty for skipping it.",
        ],
        Gate(
            "Readiness gate (see assess_readiness for the full list)",
            [
                ">= 100 demo trades with a complete journal",
                "Positive expectancy over >= 60 trades after the rules were frozen",
                "Max drawdown <= 10%; rule violation rate <= 5%",
                "Documented plan, routine, journal and analysis discipline",
            ],
        ),
    ),
)

_WEEK_TEMPLATE: tuple[tuple[str, str, int], ...] = (
    (
        "Market preparation and written plan",
        "Check the economic calendar for today and the next 24 hours. Mark weekly/daily/session "
        "levels on your watchlist. Write two scenarios (bullish and bearish) and the level that "
        "would invalidate each. Decide in advance whether today is a trading day at all.",
        60,
    ),
    (
        "Study block + level marking drill",
        "Complete the current lesson/notebook section. Then mark 5 historical charts blind: write "
        "the regime, the nearest level, and whether you would trade it, BEFORE scrolling forward.",
        75,
    ),
    (
        "Execution practice (demo)",
        "Take only written setups, at the planned risk, in the allowed sessions. Pre-calculate the "
        "position size. Screenshot before entry. Journal within 15 minutes of the exit.",
        60,
    ),
    (
        "Study block + quiz",
        "Continue the curriculum. Take a 10-question quiz in the category you are weakest at, then "
        "review every wrong answer until you can explain the correct reasoning in your own words.",
        75,
    ),
    (
        "Execution practice + weekly statistics",
        "Trade the plan, then update the journal, compute total R, expectancy, profit factor and "
        "drawdown, and count rule violations. Write the weekly review sheet.",
        75,
    ),
    (
        "Deep review (no trading)",
        "Re-read every trade of the week with the screenshots. Grade the decision (A-F), separate "
        "skill from luck, and find the single most expensive mistake. Do not change rules today.",
        90,
    ),
    (
        "Rest and planning",
        "No charts. Read one chapter of the handbook, review next week's calendar, and set the "
        "week's focus in one sentence. Rest is part of the process, not a reward for it.",
        45,
    ),
)

_WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def demo_programme(start: date | None = None) -> list[DailyTask]:
    """Expand the 13-week programme into 91 dated daily tasks."""
    start = start or date.today()
    tasks: list[DailyTask] = []
    day = 1
    for phase in _PHASES:
        weeks = _phase_weeks(phase)
        for _ in range(weeks):
            for weekday_index, (title, detail, minutes) in enumerate(_WEEK_TEMPLATE):
                if day > 91:
                    break
                deliverable = ""
                if weekday_index == 4:
                    deliverable = "weekly review sheet"
                elif weekday_index == 5:
                    deliverable = "trade grading + mistake analysis"
                elif weekday_index == 6:
                    deliverable = "next week's focus in one sentence"
                tasks.append(
                    DailyTask(
                        day_offset=day,
                        weekday=_WEEKDAYS[weekday_index],
                        title=f"Phase {phase.number} ({phase.name}): {title}",
                        detail=detail,
                        minutes=minutes,
                        deliverable=deliverable,
                    )
                )
                day += 1
    return tasks


def _phase_weeks(phase: Phase) -> int:
    """Number of weeks a phase spans, parsed from its ``weeks`` string."""
    text = phase.weeks.replace(" ", "")
    if "-" in text:
        first, last = text.split("-")
        return max(1, int(last) - int(first) + 1)
    return 1


def format_day(day: int, start: date | None = None) -> str:
    """Render a single programme day (with its week, phase and gate context)."""
    start = start or date.today()
    tasks = demo_programme(start)
    if not 1 <= day <= len(tasks):
        raise ValueError(f"Day must be between 1 and {len(tasks)}")
    task = tasks[day - 1]
    week = (day - 1) // 7 + 1
    calendar_date = start + timedelta(days=day - 1)
    lines = [
        "=" * 74,
        f"DAY {day} of {len(tasks)}   ({calendar_date.strftime('%A %d %B %Y')})   week {week}",
        f"{task.title}",
        "=" * 74,
        f"  time budget : {task.minutes} minutes",
        f"  task        : {task.detail}",
    ]
    if task.deliverable:
        lines.append(f"  deliverable : {task.deliverable}")
    lines.append("-" * 74)
    lines.append("  Non-negotiables: risk <= 0.25% per trade, maximum 2 trades, one open position,")
    lines.append("  no new positions within 30 minutes of high-impact news, journal every trade today.")
    return "\n".join(lines)


def format_week(week: int, start: date | None = None) -> str:
    """Render one full week of the programme."""
    start = start or date.today()
    tasks = demo_programme(start)
    first = (week - 1) * 7 + 1
    if not 1 <= first <= len(tasks):
        raise ValueError(f"Week must be between 1 and {(len(tasks) + 6) // 7}")
    lines = ["=" * 74, f"WEEK {week} of the 90-day programme", "=" * 74]
    for task in tasks[first - 1: first + 6]:
        lines.append(f"\nDay {task.day_offset} ({task.weekday}) - {task.minutes} min")
        lines.append(f"  {task.title}")
        lines.append(f"  {task.detail}")
        if task.deliverable:
            lines.append(f"  deliverable: {task.deliverable}")
    return "\n".join(lines)


def phases() -> tuple[Phase, ...]:
    """All programme phases (exposed for reporting and documents)."""
    return _PHASES


# ---------------------------------------------------------------------- #
# Mastery scorecard (Level 37)
# ---------------------------------------------------------------------- #
@dataclass(frozen=True)
class MasteryCategory:
    """One scored category of the mastery assessment."""

    key: str
    name: str
    weight: float
    evidence: str


MASTERY_CATEGORIES: tuple[MasteryCategory, ...] = (
    MasteryCategory("forex_knowledge", "Forex knowledge and market mechanics", 0.08,
                    "Quiz scores on 'beginner' and 'market mechanics'; can explain bid/ask, pip, lot, leverage without notes"),
    MasteryCategory("technical_analysis", "Technical analysis and chart reading", 0.10,
                    "Blind chart drills: regime and level identification accuracy; 'technical analysis' quiz score"),
    MasteryCategory("fundamental_analysis", "Fundamental and macro analysis", 0.08,
                    "'fundamental analysis' quiz score; a written macro note on one currency you got right for the right reason"),
    MasteryCategory("risk_management", "Risk management (weighted highest)", 0.18,
                    "Sizing accuracy on varied instruments; 'risk management' quiz >= 80%; zero trades above the risk limit"),
    MasteryCategory("strategy", "Strategy development and rules", 0.10,
                    "Two written setups with objective rules; rule engine configured and used"),
    MasteryCategory("backtesting", "Backtesting and statistics", 0.12,
                    ">= 100 backtested trades; out-of-sample test; correct use of confidence intervals"),
    MasteryCategory("execution", "Execution and routine", 0.08,
                    "Pre-market routine completion rate; no widened stops; pending orders used as planned"),
    MasteryCategory("psychology", "Psychology and discipline", 0.12,
                    "Rule violation rate over the last 30 trades; no revenge trades; psychology journal completed daily"),
    MasteryCategory("journaling", "Journaling and record keeping", 0.07,
                    "Journal completeness: screenshots, reasons, invalidation, emotion, lesson for every trade"),
    MasteryCategory("analysis", "Performance analysis and improvement", 0.07,
                    "Monthly report produced; correct interpretation of expectancy and drawdown; one evidence-based change per month"),
)

MASTERY_LEVELS: tuple[tuple[int, str, str], ...] = (
    (20, "Absolute beginner",
     "Learning vocabulary and mechanics. Do not trade live. Focus: Levels 0-3."),
    (40, "Beginner",
     "Understands the market and can read a chart, but risk management is not yet automatic. Stay in demo."),
    (60, "Intermediate",
     "Can analyse, size and execute a written plan with support. Continue demo with a full journal."),
    (75, "Advanced learner",
     "Consistent process in demo with a measured, positive-expectancy setup. Small live evaluation may be justified if all readiness criteria are met."),
    (90, "Competent demo trader",
     "Disciplined execution, documented statistics, controlled drawdown. Ready for a small live evaluation - not for a large account."),
    (100, "Advanced / ready for controlled live evaluation",
     "A long, documented record of disciplined trade. This is still not 'professional'; it is an evidence-backed case for risking a small amount."),
)


def mastery_level(score: float) -> tuple[str, str]:
    """Return ``(level name, guidance)`` for a 0-100 score."""
    for threshold, name, guidance in MASTERY_LEVELS:
        if score <= threshold:
            return name, guidance
    return MASTERY_LEVELS[-1][1], MASTERY_LEVELS[-1][2]


def mastery_score(scores: dict[str, float]) -> dict[str, Any]:
    """Weighted 0-100 mastery score from per-category scores (each 0-100)."""
    total_weight = sum(category.weight for category in MASTERY_CATEGORIES)
    weighted = 0.0
    missing: list[str] = []
    for category in MASTERY_CATEGORIES:
        value = scores.get(category.key)
        if value is None:
            missing.append(category.key)
            continue
        weighted += max(0.0, min(100.0, float(value))) * category.weight
    score = weighted / total_weight if total_weight else 0.0
    name, guidance = mastery_level(score)
    return {
        "score": round(score, 1),
        "level": name,
        "guidance": guidance,
        "missing_categories": missing,
        "weakest": sorted(
            ((k, v) for k, v in scores.items() if v is not None), key=lambda item: item[1]
        )[:3],
    }


def format_mastery(score: float, scores: dict[str, float] | None = None) -> str:
    """Render the scorecard as text."""
    name, guidance = mastery_level(score)
    lines = ["=" * 74, "MASTERY SCORECARD (0-100)", "=" * 74,
             f"  overall score : {score:5.1f} / 100", f"  level         : {name}",
             f"  guidance      : {guidance}", "-" * 74]
    if scores:
        for category in MASTERY_CATEGORIES:
            value = scores.get(category.key)
            bar = "" if value is None else "#" * int(max(0, min(100, value)) // 5)
            shown = "not assessed" if value is None else f"{value:5.1f}"
            lines.append(f"  {category.name:<48} {shown:>10}  {bar}")
    lines.append("=" * 74)
    lines.append("  Scoring a category highly does NOT make you a professional trader.")
    lines.append("  It means you have evidence of competence in one area of a very")
    lines.append("  unforgiving activity. The market is the only examiner that counts.")
    return "\n".join(lines)


# ---------------------------------------------------------------------- #
# Live readiness (Level 38)
# ---------------------------------------------------------------------- #
@dataclass(frozen=True)
class ReadinessCriterion:
    """One hard or soft criterion for considering a small live account."""

    key: str
    description: str
    hard: bool
    evidence_hint: str


READINESS_CRITERIA: tuple[ReadinessCriterion, ...] = (
    ReadinessCriterion("demo_trades", "At least 100 completed demo trades, journaled in full", True,
                       "Journal count of closed trades with screenshots and reasons"),
    ReadinessCriterion("frozen_sample", "At least 60 trades since the strategy rules were frozen", True,
                       "Date the rules were frozen; count trades after that date"),
    ReadinessCriterion("positive_expectancy", "Positive expectancy in R after costs over the frozen sample", True,
                       "Analytics report: expectancy and its confidence interval"),
    ReadinessCriterion("interval_excludes_zero", "The 95% bootstrap interval for expectancy excludes zero", False,
                       "Analytics report - if it includes zero, you have no demonstrated edge"),
    ReadinessCriterion("max_drawdown", "Maximum drawdown <= 10% of equity", True,
                       "Analytics report: max drawdown and recovery requirement"),
    ReadinessCriterion("rule_violations", "Rule violation rate <= 5% of the last 30 trades", True,
                       "Journal: rules_followed column and violations text"),
    ReadinessCriterion("risk_discipline", "No trade ever risked more than 1% (0.25% during learning)", True,
                       "Journal risk_percent column maximum"),
    ReadinessCriterion("no_revenge", "No revenge trade in the last 30 trades", True,
                       "Journal: trades within 60 minutes of a loss with equal or larger size"),
    ReadinessCriterion("journal_complete", "Journal complete: no missing screenshots, invalidation or lessons", True,
                       "Journal completeness check"),
    ReadinessCriterion("written_plan", "A written trading plan exists, is dated and is being followed", True,
                       "docs/TRADING_PLAN.md, with a version date"),
    ReadinessCriterion("documented_routine", "Pre-market routine completed on >= 80% of trading days", True,
                       "Daily checklist records"),
    ReadinessCriterion("psychology_stable", "No trading in a frustrated, euphoric or revenge state for 30 trades", True,
                       "Psychology journal and journal emotional_state column"),
    ReadinessCriterion("costs_understood", "Can state the round-trip cost (spread + commission) of your typical trade in money and in R", True,
                       "Written cost calculation for your main instrument"),
    ReadinessCriterion("stop_the_process", "Has demonstrated stopping for the day/week after hitting a loss limit, at least twice", True,
                       "Journal or checklist evidence"),
    ReadinessCriterion("capital", "Live capital is money whose complete loss would not change your life", True,
                       "Your own written statement; 250 USD must be disposable"),
    ReadinessCriterion("time", "Realistic schedule: at least 3 sessions per week for the next 3 months", False,
                       "Calendar check - sessions must occur in the windows your strategy needs"),
)


def readiness_report(
    answers: dict[str, bool], *, journal_stats: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Evaluate readiness criteria and produce a verdict.

    Parameters
    ----------
    answers:
        ``{criterion_key: bool}``. Unanswered criteria count as **not met** - the
        same "unverified is not approved" rule the rule engine uses.
    journal_stats:
        Optional statistics (``summary`` from the analytics pipeline) used to add
        computed evidence alongside the self-assessment.

    Returns
    -------
    dict with ``verdict``, ``passed``, ``failed_hard``, ``failed_soft``, ``score``
    and a printable ``text``.
    """
    hard = [c for c in READINESS_CRITERIA if c.hard]
    soft = [c for c in READINESS_CRITERIA if not c.hard]
    failed_hard = [c for c in hard if not answers.get(c.key, False)]
    failed_soft = [c for c in soft if not answers.get(c.key, False)]
    passed = len(READINESS_CRITERIA) - len(failed_hard) - len(failed_soft)
    score = passed / len(READINESS_CRITERIA) * 100.0

    if failed_hard:
        verdict = "NOT READY - continue demo trading"
        reason = (
            f"{len(failed_hard)} hard criterion/criteria unmet. This is the normal state of "
            "affairs for a first pass, and it is useful information rather than a failure."
        )
    elif failed_soft:
        verdict = "READY FOR A SMALL, RULE-BOUND LIVE EVALUATION (with caveats)"
        reason = (
            f"All hard criteria met; {len(failed_soft)} soft criterion/criteria unmet. If you "
            "proceed, use the smallest possible size and treat it as a test of execution, not a "
            "source of income."
        )
    else:
        verdict = "READY FOR A CONTROLLED SMALL LIVE EVALUATION"
        reason = (
            "All criteria met. Proceed with 0.10%-0.25% risk per trade, identical rules to demo, "
            "and a written review date. Success is measured by rule compliance, not profit."
        )

    lines = ["=" * 74, "LIVE ACCOUNT READINESS ASSESSMENT", "=" * 74,
             f"  criteria met : {passed}/{len(READINESS_CRITERIA)}  ({score:.0f}%)",
             f"  VERDICT      : {verdict}", f"  reason       : {reason}", "-" * 74]
    for criterion in READINESS_CRITERIA:
        met = answers.get(criterion.key, False)
        mark = "PASS" if met else ("FAIL" if criterion.hard else "warn")
        lines.append(f"  [{mark:4}] {criterion.description}")
        if not met:
            lines.append(f"         evidence needed: {criterion.evidence_hint}")
    if failed_hard:
        lines.append("-" * 74)
        lines.append("  Recommendation: continue demo trading.")
        lines.append("  Write down exactly which criteria failed and what evidence will satisfy")
        lines.append("  them. Re-run this assessment in three weeks. Do not lower the criteria")
        lines.append("  to make them pass - they exist because each one corresponds to a way that")
        lines.append("  small live accounts are lost.")
    lines.append("=" * 74)

    return {
        "verdict": verdict,
        "reason": reason,
        "score": score,
        "passed": passed,
        "total": len(READINESS_CRITERIA),
        "failed_hard": [c.key for c in failed_hard],
        "failed_soft": [c.key for c in failed_soft],
        "journal_stats": journal_stats or {},
        "text": "\n".join(lines),
    }


def format_readiness_criteria() -> str:
    """List the criteria with their evidence hints (used by the CLI and docs)."""
    lines = ["=" * 74, "READINESS CRITERIA", "=" * 74]
    for criterion in READINESS_CRITERIA:
        flag = "HARD" if criterion.hard else "soft"
        lines.append(f"  [{flag}] {criterion.key}: {criterion.description}")
        lines.append(f"          evidence: {criterion.evidence_hint}")
    return "\n".join(lines)


# ---------------------------------------------------------------------- #
# Progress persistence
# ---------------------------------------------------------------------- #
def progress_path(root: Path | None = None) -> Path:
    """``outputs/progress.json`` (git-ignored: it is personal progress data)."""
    base = Path(root) if root else Path(__file__).resolve().parents[2]
    return base / "outputs" / "progress.json"


def load_progress(path: Path | None = None) -> dict[str, Any]:
    """Load saved progress, returning an empty structure when absent."""
    target = Path(path) if path else progress_path()
    if not target.is_file():
        return {"categories": {}, "gate_results": {}, "history": [], "quiz_history": []}
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"categories": {}, "gate_results": {}, "history": [], "quiz_history": []}


def save_progress(progress: dict[str, Any], path: Path | None = None) -> Path:
    """Persist progress to JSON."""
    target = Path(path) if path else progress_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(progress, indent=2, default=str), encoding="utf-8")
    return target


def record_category_scores(scores: dict[str, float], path: Path | None = None) -> dict[str, Any]:
    """Merge new category scores into saved progress and store the timestamp."""
    progress = load_progress(path)
    progress.setdefault("categories", {}).update(scores)
    progress.setdefault("history", []).append(
        {"date": date.today().isoformat(), "scores": scores,
         "mastery": mastery_score(progress["categories"])["score"]}
    )
    save_progress(progress, path)
    return progress


def record_gate_result(phase_number: int, passed: bool, notes: str = "",
                       path: Path | None = None) -> dict[str, Any]:
    """Record whether a programme gate was passed."""
    progress = load_progress(path)
    progress.setdefault("gate_results", {})[str(phase_number)] = {
        "passed": bool(passed), "notes": notes, "date": date.today().isoformat(),
    }
    save_progress(progress, path)
    return progress


def next_incomplete_gate(path: Path | None = None) -> int:
    """The first phase whose gate has not been passed (1..10)."""
    progress = load_progress(path)
    gates = progress.get("gate_results", {})
    for phase in _PHASES:
        if not gates.get(str(phase.number), {}).get("passed", False):
            return phase.number
    return len(_PHASES) + 1


def gate_conditions(phase_number: int) -> Iterable[str]:
    """Conditions for one phase gate."""
    for phase in _PHASES:
        if phase.number == phase_number:
            return phase.gate.conditions
    raise KeyError(f"No phase {phase_number}")
