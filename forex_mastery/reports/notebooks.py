"""
Notebook curriculum generator (Level 35).

The 20 notebooks are written as **nbformat v4 JSON directly**, using only the
standard library. Consequences:

* no dependency is needed to *generate* the curriculum (``nbformat`` is only
  needed if you want to execute the notebooks programmatically with nbconvert);
* the notebooks open in VS Code, JupyterLab and Colab;
* the curriculum is data (a table of lessons and exercises), so adding a lesson
  is a one-line change rather than a copy-paste of JSON.

Each notebook contains: the objective, the theory in short form, runnable code
that imports the calculation engine, at least one exercise with a blank to fill,
a quiz pointer, and a written assignment to complete in the trading journal.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

__all__ = ["CURRICULUM", "build_notebooks", "nbformat_available", "notebook_names"]


def nbformat_available() -> bool:
    """True: notebooks are written as plain JSON (nbformat is not required).

    ``nbformat`` is listed in requirements.txt only for *executing* notebooks
    with nbconvert. Generation needs nothing beyond the standard library.
    """
    return True


CURRICULUM: tuple[tuple[str, str, str, str], ...] = (
    ("01_forex_basics", "Forex basics",
     "What FX is, pairs, base/quote, pips, lots, spread, swaps, and who the participants are.",
     "Compute the pip value of 0.10 lots of EURUSD, USDJPY at 150.00, and XAUUSD using the toolkit, then verify each by hand."),
    ("02_market_mechanics", "Market mechanics",
     "Bid/ask, execution, slippage, margin, leverage, stop-out, and what actually happens when you click buy.",
     "Explain in writing the difference between leverage and risk, then demonstrate it with one calculation."),
    ("03_exness_and_mt5", "Exness and MetaTrader 5",
     "Account types, verified specifications, platform navigation, order types and trading costs.",
     "Find and record the spread, swap and margin requirement for three instruments in your own MT5 terminal."),
    ("04_candlesticks", "Candlesticks",
     "OHLC, candle anatomy, twelve patterns, and why a pattern alone is never a strategy.",
     "Find ten hammer/engulfing candles on H4. For each, record where it formed and what happened next - including the failures."),
    ("05_market_structure", "Market structure",
     "Swing points, higher highs and lows, trend, range, transition, breakouts and false breakouts.",
     "Mark the structure on 20 charts blind and score your own regime classification."),
    ("06_support_resistance", "Support and resistance",
     "Levels, zones, round numbers, session highs/lows, and why levels fail.",
     "Build a level map for EURUSD on W1/D1/H4 and track how price treated each level for a week."),
    ("07_indicators", "Indicators",
     "Moving averages, MACD, RSI, ATR, Bollinger Bands, volume caveats and indicator redundancy.",
     "Demonstrate that RSI and Stochastic give near-identical signals, then argue for keeping only one."),
    ("08_multi_timeframe", "Multi-timeframe analysis",
     "Higher timeframe bias, lower timeframe execution, top-down procedure and timeframe conflict.",
     "Write your own top-down procedure in under 10 steps and time yourself doing it on three pairs."),
    ("09_sessions", "Sessions",
     "Sydney, Tokyo, London, New York, overlaps, daylight saving, and liquidity lulls.",
     "Produce a session timetable in your own local time and identify your available windows."),
    ("10_fundamental_analysis", "Fundamental analysis",
     "GDP, CPI, employment, PMIs, central banks, rate expectations, real yields and risk sentiment.",
     "Write a one-page macro note on one currency: what the central bank is doing, what is priced in, and what would change it."),
    ("11_news_analysis", "News analysis",
     "Calendar work, pre- and post-release behaviour, spread widening, slippage and the news risk protocol.",
     "Track five high-impact releases: record the spread before and after, and the price range in the first two minutes."),
    ("12_correlations", "Correlations",
     "EURUSD/GBPUSD/AUDUSD, DXY, yields, oil and gold; correlation breakdown and hidden exposure.",
     "Identify a week in which EURUSD and GBPUSD diverged, and explain what could have caused it."),
    ("13_price_action", "Price action",
     "Impulse, correction, expansion, compression, liquidity sweeps, and an objective look at SMC/ICT terminology.",
     "Separate one popular 'smart money' claim into its observable part and its interpretive part, then design a test for the observable part."),
    ("14_risk_management", "Risk management",
     "Risk per trade, position sizing, R-multiples, expectancy, drawdown, streaks and risk of ruin.",
     "Size ten hypothetical trades by hand across four instruments and verify each with the toolkit."),
    ("15_strategy_development", "Strategy development",
     "The thirteen strategy families, their required conditions and their failure modes.",
     "Write one setup so precisely that a stranger could execute it, then list the conditions under which it should not be traded."),
    ("16_backtesting", "Backtesting",
     "Manual backtesting, data handling, sample size, costs, biases and the seven-stage validation gate.",
     "Backtest your setup on 100 trades, recording every trade including the ugly ones, with costs applied."),
    ("17_statistics", "Statistics for traders",
     "Expectancy, standard error, confidence intervals, streaks, multiple testing and overfitting.",
     "Compute the confidence interval for your own expectancy and explain in one sentence what it does not say."),
    ("18_psychology", "Psychology",
     "Loss aversion, revenge trading, FOMO, overconfidence, outcome bias and mechanical defences.",
     "Name your three personal failure modes and write a specific, checkable counter-measure for each."),
    ("19_trading_journal", "The trading journal",
     "Every field, why it exists, and how to record a trade in under five minutes.",
     "Record five trades end-to-end with before/after screenshots and grade each decision A-F."),
    ("20_performance_analysis", "Performance analysis",
     "Reading your own statistics: expectancy, drawdown, breakdowns and evidence-based improvement.",
     "Produce a one-page monthly report with the statistics, the biggest loss source, and one change."),
)


def notebook_names() -> list[str]:
    """File names of the generated notebooks."""
    return [f"{name}.ipynb" for name, _, _, _ in CURRICULUM]


def _cell(kind: str, source: str) -> dict:
    if kind == "code":
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": source.splitlines(keepends=True),
        }
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def _notebook(name: str, title: str, theory: str, assignment: str) -> dict:
    cells = [
        _cell("markdown", f"# {title}\n\n*Part of the Forex Mastery System notebook curriculum.*\n"),
        _cell("markdown",
              "## How to use this notebook\n\n"
              "1. Read the theory section, then run each code cell (Shift+Enter).\n"
              "2. Do the exercises by hand **first**, then check with the code.\n"
              "3. Write your answers where the notebook says `your answer here`.\n"
              "4. Finish with the written assignment; that is the part that changes behaviour.\n\n"
              "> Nothing in this notebook predicts the market. The code measures, sizes and audits.\n"),
        _cell("markdown", "## Theory in short form\n\n" + theory + "\n"),
        _cell("code",
              "import sys\n"
              "from pathlib import Path\n"
              "# Make the project importable when the notebook is opened from notebooks/\n"
              "ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
              "if str(ROOT) not in sys.path:\n"
              "    sys.path.insert(0, str(ROOT))\n"
              "\n"
              "from forex_mastery.core.instruments import get_instrument, list_instruments\n"
              "from forex_mastery.core.pip import pip_value_per_lot, point_value_per_lot\n"
              "from forex_mastery.core.position_size import PositionSizeRequest, calculate_position_size, risk_level_scenarios\n"
              "from forex_mastery.core.margin import required_margin, notional_value, effective_leverage, margin_level_percent\n"
              "from forex_mastery.core.risk import (r_multiple, risk_reward, breakeven_win_rate, expectancy_r,\n"
              "                                     drawdown_ladder, recovery_gain_required, losing_streak_probabilities)\n"
              "from forex_mastery.core.metrics import compute_performance\n"
              "from forex_mastery.core.risk_of_ruin import simulate_risk_of_ruin\n"
              "from forex_mastery.core.compounding import project_equity, growth_rate_per_trade\n"
              "from forex_mastery.core.sessions import format_session_table, active_sessions, session_liquidity_rank\n"
              "from forex_mastery.core.rule_engine import SetupContext, evaluate_setup, load_rules\n"
              "\n"
              "SPECS = {spec.symbol: spec for spec in list_instruments()}\n"
              "print(f'{len(SPECS)} instruments loaded; engine is standard library only.')\n"),
        _cell("markdown", "## Worked example\n\nRun this, then change the numbers and predict what will happen before you re-run it.\n"),
        _cell("code",
              "# A worked example you can adapt: sizing one trade properly\n"
              "request = PositionSizeRequest('EURUSD', balance=250, entry=1.1000, stop=1.0950,\n"
              "                              risk_percent=0.25, leverage=100, spread_pips=1.2)\n"
              "result = calculate_position_size(request)\n"
              "print(result.report())\n"),
        _cell("markdown",
              "## Exercises\n\n"
              "1. **Hand calculation first.** Work out the number with pen and paper, then use the "
              "code to check. A discrepancy is a learning opportunity, not a bug.\n"
              "2. Change one input at a time and predict the effect before running.\n"
              "3. Write your reasoning in the cell below the code, not just the number.\n"),
        _cell("code", "# Exercise 1 - your working\n"),
        _cell("markdown", "your answer here\n"),
        _cell("code", "# Exercise 2 - your working\n"),
        _cell("markdown", "your answer here\n"),
        _cell("markdown",
              "## Check your understanding\n\n"
              f"Run: `python main.py quiz --category {_quiz_category(name)} --n 8 --interactive`\n\n"
              "Answers are hidden until you commit to one. Review every wrong answer until you can "
              "explain the correct reasoning in your own words.\n"),
        _cell("markdown", f"## Written assignment\n\n{assignment}\n\n"
                          "Record it in your journal or in `docs/handbooks/` notes. An unrecorded "
                          "insight is a lost insight.\n"),
        _cell("markdown",
              "## Common mistakes in this module\n\n"
              "- Learning the vocabulary and mistaking it for competence.\n"
              "- Skipping straight to the code without doing the hand calculation.\n"
              "- Changing a rule because a single example contradicted it.\n"
              "- Treating a notebook result as evidence about future markets. It is arithmetic, not foresight.\n"),
    ]
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10"},
            "title": title,
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def _quiz_category(name: str) -> str:
    mapping = {
        "01_forex_basics": "beginner",
        "02_market_mechanics": "market_mechanics",
        "03_exness_and_mt5": "market_mechanics",
        "04_candlesticks": "technical_analysis",
        "05_market_structure": "technical_analysis",
        "06_support_resistance": "technical_analysis",
        "07_indicators": "technical_analysis",
        "08_multi_timeframe": "technical_analysis",
        "09_sessions": "market_mechanics",
        "10_fundamental_analysis": "fundamental_analysis",
        "11_news_analysis": "fundamental_analysis",
        "12_correlations": "fundamental_analysis",
        "13_price_action": "technical_analysis",
        "14_risk_management": "risk_management",
        "15_strategy_development": "strategy",
        "16_backtesting": "backtesting",
        "17_statistics": "statistics",
        "18_psychology": "psychology",
        "19_trading_journal": "strategy",
        "20_performance_analysis": "statistics",
    }
    return mapping.get(name, "beginner")


def build_notebooks(target_dir: Path, overwrite: bool = False) -> list[Path]:
    """Write the 20-notebook curriculum. Returns the files created."""
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, title, theory, assignment in CURRICULUM:
        path = target_dir / f"{name}.ipynb"
        if path.exists() and not overwrite:
            written.append(path)
            continue
        path.write_text(
            json.dumps(_notebook(name, title, theory, assignment), indent=1), encoding="utf-8"
        )
        written.append(path)
    return written


def iter_notebook_titles() -> Iterable[str]:
    """Titles only (used by documentation generators)."""
    for _, title, _, _ in CURRICULUM:
        yield title
