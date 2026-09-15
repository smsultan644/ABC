"""
Performance analytics pipeline: journal in, statistics and files out.

This is the glue between the journal (data) and the metrics engine (maths).
It intentionally contains no statistics of its own - every number comes from
``forex_mastery.core.metrics`` - so there is exactly one implementation of each
formula in the whole system.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from ..core.metrics import BucketStat, PerformanceReport, compute_performance
from ..journal.model import TradeRecord
from ..journal.storage import JournalStore

__all__ = [
    "AnalyticsResult",
    "analyse_journal",
    "bucket_rows",
    "write_breakdown_csvs",
    "write_equity_curve_csv",
]


@dataclass
class AnalyticsResult:
    """Everything derived from a journal, ready to be written to files."""

    report: PerformanceReport
    trades: list[TradeRecord]
    summary: dict[str, Any]

    def to_json(self, target: Path) -> Path:
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "summary": self.summary,
            "performance": self.report.as_dict(),
        }
        target.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        return target


def analyse_journal(
    journal_path: str | Path,
    starting_equity: float = 250.0,
    trades_per_year: int | None = None,
) -> AnalyticsResult:
    """Run the full statistics on a journal file.

    Only **closed** trades are analysed. Open trades have no R-multiple, and
    including them as zeros would dilute every statistic.
    """
    store = JournalStore(Path(journal_path))
    records = store.load()
    closed = [r for r in records if r.is_closed]

    # Pass the raw dataclass objects: the metrics engine reads attributes or dict
    # keys, and the dataclass exposes `r_multiple` as a computed property.
    report = compute_performance(
        [
            {
                "trade_id": t.trade_id,
                "date": t.date,
                "symbol": t.symbol,
                "instrument": t.symbol,
                "setup": _enum_value(t.setup),
                "session": _enum_value(t.session),
                "timeframe": t.timeframe,
                "direction": _enum_value(t.direction),
                "setup_quality": _enum_value(t.setup_quality),
                "market_regime": _enum_value(t.market_regime),
                "emotional_state": _enum_value(t.emotional_state),
                "pnl": t.pnl,
                "risk_amount": t.risk_amount,
                "risk_percent": t.risk_percent_of_equity,
                "r_multiple": t.r_multiple,
                "rule_violation": not t.rules_followed or bool(t.rule_violations),
                "emotion": _is_emotional(_enum_value(t.emotional_state)),
                "status": _enum_value(t.status),
            }
            for t in closed
        ],
        starting_equity=starting_equity,
        trades_per_year=trades_per_year,
    )

    summary = {
        **store.summary(),
        "starting_equity_assumed": starting_equity,
        "final_equity_from_curve": report.equity_curve[-1] if report.equity_curve else starting_equity,
        "expectancy_r": report.expectancy_r,
        "calls_to_action": _action_items(report),
    }
    return AnalyticsResult(report=report, trades=closed, summary=summary)


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _is_emotional(state: Any) -> bool:
    return str(state or "").lower() in {
        "anxious", "frustrated", "euphoric", "bored", "fearful", "impatient"
    }


def _action_items(report: PerformanceReport) -> list[str]:
    """Turn statistics into a short, non-negotiable list of next actions.

    This is the difference between a dashboard and a coach: the numbers must
    end in a decision. Every item is phrased as an instruction, not a judgement.
    """
    items: list[str] = []
    if report.sample_size == 0:
        return ["No closed trades yet. Record trades in the journal before drawing conclusions."]
    if report.sample_size < 30:
        items.append(
            f"Sample is {report.sample_size} trades. Keep recording; do not change the strategy yet."
        )
    if report.rule_violation_rate > 0.10:
        items.append(
            f"{report.rule_violation_rate * 100:.0f}% of trades broke a rule. Fix process before "
            "judging the edge (rule-breaking trades cost "
            f"{report.rule_violation_total_r:+.2f}R in this sample)."
        )
    if report.expectancy_ci95[0] <= 0 <= report.expectancy_ci95[1]:
        items.append(
            "Expectancy confidence interval includes zero: the strategy is unproven. Keep it in "
            "demo, do not increase risk, and collect more data."
        )
    else:
        items.append(
            f"Expectancy is {report.expectancy_r:+.3f}R with the interval above zero - some "
            "evidence of an edge. Do not increase risk; keep the framework identical for "
            "another 50 trades before adjusting anything."
        )
    if report.max_drawdown_pct > 10:
        items.append(
            f"Max drawdown is {report.max_drawdown_pct:.1f}%. Review whether the loss limit rules "
            "were respected; a drawdown beyond your plan is a process failure, not bad luck."
        )
    if report.max_risk_percent > 1.0:
        items.append(
            f"Some trades risked {report.max_risk_percent:.2f}% (limit 1%). Return to <= 0.5% and "
            "re-read Level 15."
        )
    worst = report.by_setup[-1] if report.by_setup else None
    best = report.by_setup[0] if report.by_setup else None
    if best and worst and best.label != worst.label:
        items.append(
            f"Best setup: {best.label} ({best.total_r:+.2f}R). Worst: {worst.label} "
            f"({worst.total_r:+.2f}R). Stop trading the worst one until it is either fixed in "
            "writing or dropped from the plan."
        )
    if report.emotional_trade_count:
        items.append(
            f"{report.emotional_trade_count} trades were taken in a poor emotional state "
            f"({report.emotional_trade_total_r:+.2f}R). Add the state to the pre-trade checklist "
            "and treat 'anxious/euphoric/frustrated' as a hard block."
        )
    return items


def bucket_rows(buckets: Sequence[BucketStat]) -> list[dict[str, Any]]:
    """Convert bucket statistics into rows for CSV/Excel."""
    return [
        {
            "group": b.label,
            "trades": b.trades,
            "wins": b.wins,
            "win_rate_pct": round(b.win_rate * 100, 2),
            "total_r": round(b.total_r, 3),
            "avg_r": round(b.avg_r, 4),
            "net_pnl": round(b.net_pnl, 2),
            "profit_factor": (
                round(b.profit_factor, 3) if b.profit_factor != float("inf") else "inf"
            ),
        }
        for b in buckets
    ]


def write_equity_curve_csv(report: PerformanceReport, target: Path) -> Path:
    """Equity curve (starting equity + one row per trade) as CSV."""
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["trade_index", "equity", "cumulative_r"])
        cumulative_r = 0.0
        writer.writerow([0, round(report.equity_curve[0], 4) if report.equity_curve else 0.0, 0.0])
        for index, r_value in enumerate(report.r_series, start=1):
            cumulative_r += r_value
            equity = report.equity_curve[index] if index < len(report.equity_curve) else ""
            writer.writerow([index, round(equity, 4) if equity != "" else "", round(cumulative_r, 4)])
    return target


def write_breakdown_csvs(report: PerformanceReport, outdir: Path) -> list[Path]:
    """Write one CSV per breakdown dimension. Returns the files created."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    dimensions = {
        "by_setup": report.by_setup,
        "by_instrument": report.by_instrument,
        "by_session": report.by_session,
        "by_timeframe": report.by_timeframe,
        "by_direction": report.by_direction,
        "by_weekday": report.by_weekday,
        "by_quality": report.by_quality,
        "by_month": report.monthly,
    }
    for name, buckets in dimensions.items():
        if not buckets:
            continue
        rows = bucket_rows(buckets)
        path = outdir / f"{name}.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        written.append(path)
    if report.r_series:
        path = outdir / "r_distribution.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["trade_index", "r_multiple"])
            writer.writerows(enumerate(report.r_series, start=1))
        written.append(path)
    return written
