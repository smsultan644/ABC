"""
Charts for the performance dashboard.

matplotlib is an **optional** dependency. Every function here degrades
gracefully: if matplotlib is missing, the function returns ``None`` and the
caller reports that charts were skipped. That keeps the core analytics usable on
a bare Python install - the numbers are the deliverable, the pictures are a
convenience.

Chart honesty rules applied here:

* the equity curve is plotted against **trade number**, not dates, because
  trade frequency is irregular and a date axis flatters quiet periods;
* the drawdown chart is filled from the running peak, because percentage
  drawdown is the number that determines whether you can keep trading;
* the R-distribution is plotted with a bin width of 0.5R and a marked zero line,
  because the *shape* (many small losses, a few large winners) is the thing to
  understand, not the average.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from ..core.metrics import PerformanceReport

__all__ = [
    "charts_available",
    "plot_drawdown_curve",
    "plot_equity_curve",
    "plot_monthly_performance",
    "plot_r_distribution",
    "plot_setup_performance",
]


def charts_available() -> bool:
    """True when matplotlib can be imported."""
    try:
        import matplotlib  # noqa: F401
    except Exception:
        return False
    return True


def _setup():
    """Import matplotlib with a non-interactive backend and a plain style."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "figure.figsize": (9, 4.5),
            "figure.dpi": 120,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 9,
            "axes.titlesize": 11,
        }
    )
    return plt


def _save(fig, target: Path) -> Path:
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(target, bbox_inches="tight")
    import matplotlib.pyplot as plt

    plt.close(fig)
    return target


def plot_equity_curve(report: PerformanceReport, target: Path, starting_equity: float = 250.0):
    """Equity after each closed trade, with the drawdown region shaded."""
    if not charts_available() or not report.equity_curve:
        return None
    plt = _setup()
    curve = report.equity_curve
    fig, ax = plt.subplots()
    ax.plot(range(len(curve)), curve, linewidth=1.6, color="#1f6feb", label="Equity")
    ax.axhline(starting_equity, color="#888", linestyle="--", linewidth=0.9, label="Start")
    peak = curve[0]
    runs_x, runs_y = [], []
    for index, value in enumerate(curve):
        peak = max(peak, value)
        runs_x.append(index)
        runs_y.append(peak)
    ax.plot(runs_x, runs_y, color="#2da44e", linewidth=0.8, linestyle=":", label="Running peak")
    ax.fill_between(range(len(curve)), curve, runs_y, color="#d1242f", alpha=0.12)
    ax.set_title(f"Equity curve after each trade  (max drawdown {report.max_drawdown_pct:.1f}%)")
    ax.set_xlabel("Trade number")
    ax.set_ylabel("Equity (account currency)")
    ax.legend(loc="best", frameon=False)
    return _save(fig, target)


def plot_drawdown_curve(report: PerformanceReport, target: Path):
    """Percentage below the running peak, after every trade."""
    if not charts_available() or not report.equity_curve:
        return None
    plt = _setup()
    curve = report.equity_curve
    peak = curve[0]
    drawdowns = []
    for value in curve:
        peak = max(peak, value)
        drawdowns.append(-(peak - value) / peak * 100.0 if peak > 0 else 0.0)
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.fill_between(range(len(drawdowns)), drawdowns, 0, color="#d1242f", alpha=0.35)
    ax.plot(range(len(drawdowns)), drawdowns, color="#d1242f", linewidth=1.0)
    for level, label in ((10, "10% - review threshold"), (20, "20% - stop and re-plan")):
        if min(drawdowns) <= -level:
            ax.axhline(-level, color="#8250df", linestyle="--", linewidth=0.8)
            ax.text(0, -level, f"  {label}", va="bottom", fontsize=7, color="#8250df")
    ax.set_title("Drawdown from peak equity (compounding matters here)")
    ax.set_xlabel("Trade number")
    ax.set_ylabel("Drawdown (%)")
    return _save(fig, target)


def plot_r_distribution(report: PerformanceReport, target: Path):
    """Histogram of R-multiples, with the mean marked."""
    if not charts_available() or not report.r_series:
        return None
    plt = _setup()
    values: Sequence[float] = report.r_series
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.hist(values, bins=20, color="#1f6feb", alpha=0.75, edgecolor="white")
    ax.axvline(0, color="#333", linewidth=0.9)
    ax.axvline(report.avg_r, color="#bf8700", linewidth=1.4, linestyle="--",
               label=f"mean {report.avg_r:+.2f}R")
    ax.set_title("Distribution of outcomes in R (the shape of your edge)")
    ax.set_xlabel("R-multiple")
    ax.set_ylabel("Number of trades")
    ax.legend(frameon=False)
    return _save(fig, target)


def plot_monthly_performance(report: PerformanceReport, target: Path):
    """Total R per month - the honest look at consistency."""
    if not charts_available() or not report.monthly:
        return None
    plt = _setup()
    labels = [b.label for b in report.monthly]
    values = [b.total_r for b in report.monthly]
    colours = ["#2da44e" if v >= 0 else "#d1242f" for v in values]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.bar(labels, values, color=colours, alpha=0.85)
    ax.axhline(0, color="#333", linewidth=0.8)
    ax.set_title("Monthly performance in R")
    ax.set_ylabel("Total R")
    ax.tick_params(axis="x", rotation=45)
    return _save(fig, target)


def plot_setup_performance(report: PerformanceReport, target: Path):
    """Total R by setup - which system is actually paying for itself."""
    if not charts_available() or not report.by_setup:
        return None
    plt = _setup()
    labels = [b.label for b in report.by_setup]
    values = [b.total_r for b in report.by_setup]
    colours = ["#2da44e" if v >= 0 else "#d1242f" for v in values]
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.barh(labels, values, color=colours, alpha=0.85)
    ax.axvline(0, color="#333", linewidth=0.8)
    ax.set_title("Total R by setup (sample sizes are shown in the tables - check them)")
    ax.set_xlabel("Total R")
    return _save(fig, target)


def build_all_charts(report: PerformanceReport, outdir: Path, starting_equity: float = 250.0) -> list[Path]:
    """Generate every dashboard chart; returns the files that were created."""
    outdir = Path(outdir)
    if not charts_available():
        return []
    created: list[Path] = []
    for name, func, kwargs in (
        ("equity_curve.png", plot_equity_curve, {"starting_equity": starting_equity}),
        ("drawdown_curve.png", plot_drawdown_curve, {}),
        ("r_distribution.png", plot_r_distribution, {}),
        ("monthly_performance.png", plot_monthly_performance, {}),
        ("setup_performance.png", plot_setup_performance, {}),
    ):
        try:
            path = func(report, outdir / name, **kwargs)
        except Exception:  # pragma: no cover - chart failures must never break the report
            path = None
        if path:
            created.append(path)
    return created
