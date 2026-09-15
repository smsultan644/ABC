"""
Printable/editable templates (CSV + Markdown).

Two audiences:

* **CSV** templates are for spreadsheets - the market analysis template, the
  decision log, the correlation exposure calculator, the backtest record.
* **Markdown** templates are for writing - the weekly and monthly reviews, the
  strategy specification, the psychology log.

Every template is deliberately short. A template that takes 30 minutes to fill
in will not be filled in. The journal fields mirror
``forex_mastery.journal.model.JOURNAL_COLUMNS`` so a filled CSV can be appended
directly to the journal.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Callable

from ..journal.model import JOURNAL_COLUMNS

__all__ = ["write_all_templates"]


MARKET_ANALYSIS_TEMPLATE = """# MARKET ANALYSIS TEMPLATE

_Complete this before considering any trade. If a line is blank, you do not have
a trade - you have an idea._

Instrument:
Date and time (UTC):
Session:
Higher timeframe trend (W1/D1):
Current timeframe analysed:
Market structure (HH/HL, LH/LL, range, transition):
Key support levels (with the reason each matters):
Key resistance levels (with the reason each matters):
Liquidity: where are the obvious stop clusters / session extremes?
Volatility: ATR and its normal band:
Spread now vs typical:
News: next high-impact release, and the blackout window:
Fundamental bias (and what is priced in):
Technical bias:
Setup name (must be in the written plan):
Entry trigger (objective, not "when it looks right"):
Entry price:
Stop loss price (and why that price invalidates the idea):
Take profit price (and why price should reach it):
Risk percent:            Risk in money:
Reward:risk:
Position size (lots), calculated not guessed:
Correlation check (am I already expressing this idea?):
Portfolio heat after this trade:
Psychological check (state, sleep, recent losses, urge to trade):
INVALIDATION (the condition that proves this idea wrong):
DECISION: TRADE / NO TRADE
Reason for the decision:
"""

DECISION_LOG_TEMPLATE = """# DECISION LOG

_The most valuable habit in this course: record the decisions you did NOT take.
A declined setup costs nothing and teaches you exactly as much as a taken one._

| Date | Instrument | Setup seen | Why declined | Would it have worked? (check later) | Lesson |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
"""

WEEKLY_REVIEW_TEMPLATE = """# WEEKLY REVIEW - week ending ____________

Equity at start:            Equity at end:
Total trades:               Wins:        Losses:        Breakeven:
Total R:                    Expectancy (R):            Profit factor:
Rule violations (count):    Cost of violations (R):
Best trade (and why it was good):
Worst trade (and why):
Decision quality, ignoring outcomes (A-F, with reasons):
Single most expensive mistake this week:
What I will do differently next week (ONE change maximum):
Did I change any rule mid-week? (If yes, why - and this is almost always wrong.)
Sleep / stress / life context this week:
What I did well that I should repeat:
"""

MONTHLY_REVIEW_TEMPLATE = """# MONTHLY REVIEW - month ____________

## Sample and statistics
Trades this month:            Cumulative trades since rules frozen:
Expectancy this month (R):    Expectancy since freezing (R):
95% confidence interval for expectancy:
Profit factor:                Win rate:            Average win / loss (R):
Maximum drawdown (%):         Recovery gain required (%):
Longest losing streak:        Longest winning streak:

## Strategy assessment
Does the out-of-sample behaviour match the backtest distribution?
Which setup earned the most R? Which lost the most?
Which instrument, session and weekday produced the best and worst results?
Is any result driven by one or two outsized trades? (Recompute without them.)

## Process assessment
Rule violation rate:          Revenge trades:
Trades taken outside the plan:
Journal completeness (screenshots, invalidation, lesson):
Pre-market routine completion rate:

## Cost assessment
Average spread paid:          Commission and swap paid this month:
Total costs as a percentage of gross profit:
Cost as a fraction of R on a typical trade:

## Decisions (in writing, never during a drawdown)
Keep (and why):
Adjust (exactly what, and only one change):
Retire (and why):
What evidence would tell me I am wrong about the above?

## Readiness
Run: python main.py readiness --criteria
Criteria currently unmet:
Evidence I need to produce before the next review:
"""

STRATEGY_SPEC_TEMPLATE = """# STRATEGY SPECIFICATION

Strategy name:                        Version:            Date frozen:
Author (you):

## 1. Market condition it requires
Trend / range / transition:
Volatility regime (ATR band):
Timeframe(s) for bias and entry:
Session(s):
Instruments (with the reason each is suitable):

## 2. Entry rules (objective - a stranger must be able to execute them)
Context requirement:
Setup formation:
Entry trigger (what exactly must be true at the moment of entry):
Entry order type (market / limit / stop):
What must NOT be true (exclusions):

## 3. Exit rules
Stop loss (and the structural reason for its placement):
Stop distance in pips on each instrument (for reference only - size from risk):
Take profit (fixed R, structure-based, or trailing): specify precisely
Break-even rule:
Partial exit rule:
Time-based exit (if any):

## 4. Risk
Risk percent per trade:
Maximum trades per day:
Correlation limits:
News restrictions:

## 5. Expected behaviour (to be filled from the backtest, not guessed)
Number of trades in sample:
Win rate:
Average winner (R):        Average loser (R):
Expectancy (R):            95% confidence interval:
Profit factor:
Maximum drawdown:
Longest losing streak:
Costs assumed (spread, commission, slippage):

## 6. Failure conditions (when this strategy should NOT be traded)
Market condition absent:
Known bad regimes:
News environments to avoid:
Evidence that would retire this strategy:

## 7. Validation status
[ ] Rules written
[ ] Backtested (>= 100 trades, costs included)
[ ] Out-of-sample tested
[ ] Demo forward tested (>= 40 trades)
[ ] Reviewed and approved in writing by the author (you)
"""

PSYCHOLOGY_LOG_TEMPLATE = """# PSYCHOLOGY LOG

| Date | Sleep 1-5 | Stress 1-5 | State before session | Urges felt | Trades taken | Followed plan? | Strongest emotion | Trigger | What I did instead | Note for tomorrow |
|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |
"""

CORRELATION_CSV = """instrument,usd_exposure,driver,correlated_with,live_positions,limit,within_limit
EURUSD,short USD (long EUR),relative growth and rate differential,"GBPUSD (+), XAUUSD (+), DXY (-)",,1,
GBPUSD,short USD (long GBP),UK rates and risk sentiment,"EURUSD (+), DXY (-)",,1,
USDJPY,long USD vs JPY,US-JP rate differential and risk sentiment,"USDCHF (+), UST yields (+)",,1,
USDCHF,long USD,USD flows and SNB policy,"USDJPY (+), EURUSD (-)",,1,
AUDUSD,short USD (long AUD),risk sentiment and commodities,"NZDUSD (+), XAUUSD (+)",,1,
NZDUSD,short USD (long NZD),risk sentiment,"AUDUSD (+)",,1,
USDCAD,long USD vs CAD,oil prices and rate differential,"USOIL (-)",,1,
XAUUSD,long gold (inverse to real yields),real yields and risk sentiment,"AUDUSD (+), USD weakness (+)",,1,
DXY,basket of USD,aggregate USD strength,"EURUSD (-), GBPUSD (-), AUDUSD (-)",,1,
USOIL,long oil,global growth and supply,"USDCAD (-)",,1,
"""

BACKTEST_CSV_HEADER = (
    "trade_number,date,symbol,timeframe,session,direction,setup,entry,stop,target,"
    "stop_pips,planned_rr,spread_pips,cost_in_r,outcome,r_multiple,rules_followed,notes"
)

TRADE_JOURNAL_TEMPLATE_ROW = (
    "T-0001,2026-09-15,08:31,2026-09-15,09:45,EURUSD,long,London,H4,trend_pullback,uptrend,A,"
    "1.10000,1.09500,1.11000,0.01,0.0025,0.63,250.00,2.00,1.11000,2.50,2.00,win,50.0,1.2,0,0,"
    '"H4 uptrend intact; pulled back to prior demand zone; bullish engulfing close above the level",'
    '"H4 close below 1.0950 (prior higher low)",'
    '"Target reached at prior H4 swing high; momentum slowed into the level",TRUE,TRUE,,calm,'
    '"Entered 2 pips early on the M15 confirmation",'
    '"Wait for the candle CLOSE, not the wick, even when the move looks obvious",'
    "shots/T-0001_before.png,shots/T-0001_after.png,"
)


def _write_csv(path: Path, header: list[str], rows: list[list[str]] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for row in rows or []:
            writer.writerow(row)
    return path


def _market_analysis_csv() -> Path:
    return Path("__csv__")


def write_all_templates(target_dir: Path) -> list[Path]:
    """Write every CSV and Markdown template. Returns the files created."""
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    markdown_documents: dict[str, str] = {
        "market_analysis_template.md": MARKET_ANALYSIS_TEMPLATE,
        "decision_log.md": DECISION_LOG_TEMPLATE,
        "weekly_review.md": WEEKLY_REVIEW_TEMPLATE,
        "monthly_review.md": MONTHLY_REVIEW_TEMPLATE,
        "strategy_specification.md": STRATEGY_SPEC_TEMPLATE,
        "psychology_log.md": PSYCHOLOGY_LOG_TEMPLATE,
    }
    for name, content in markdown_documents.items():
        path = target_dir / name
        path.write_text(content, encoding="utf-8")
        written.append(path)

    # Empty trade journal with the exact schema the analytics pipeline expects.
    written.append(
        _write_csv(
            target_dir / "trading_journal_template.csv",
            list(JOURNAL_COLUMNS),
            [TRADE_JOURNAL_TEMPLATE_ROW.rstrip(",").split(",")],
        )
    )
    written.append(
        _write_csv(
            target_dir / "backtest_template.csv",
            BACKTEST_CSV_HEADER.split(","),
        )
    )
    written.append(
        _write_csv(
            target_dir / "correlation_exposure.csv",
            ["instrument", "usd_exposure", "driver", "correlated_with", "live_positions",
             "limit", "within_limit"],
            [row.split(",") for row in CORRELATION_CSV.strip().splitlines()[1:]],
        )
    )
    written.append(
        _write_csv(
            target_dir / "market_analysis_template.csv",
            ["field", "value", "notes"],
            [["instrument", "", ""], ["date_utc", "", ""], ["session", "", ""],
             ["htf_trend", "", ""], ["structure", "", ""], ["support", "", ""],
             ["resistance", "", ""], ["liquidity", "", ""], ["atr_pips", "", ""],
             ["spread_pips", "", ""], ["next_high_impact_news", "", ""],
             ["fundamental_bias", "", ""], ["technical_bias", "", ""],
             ["setup_name", "", ""], ["entry", "", ""], ["stop", "", ""],
             ["take_profit", "", ""], ["risk_percent", "", ""], ["risk_money", "", ""],
             ["rr", "", ""], ["lots", "", ""], ["correlation_check", "", ""],
             ["portfolio_heat", "", ""], ["psychology_check", "", ""],
             ["invalidation", "", ""], ["decision", "", ""]],
        )
    )
    return written


_ = (Callable, _market_analysis_csv)
