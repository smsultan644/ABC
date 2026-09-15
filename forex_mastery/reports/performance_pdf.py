"""
Performance report PDF (Level 33).

A monthly artefact you can archive: headline statistics, the distribution of
outcomes, drawdown behaviour, breakdowns by setup/instrument/session, and a
short list of evidence-derived actions.

The report is deliberately *unflattering*. It shows the confidence interval
around expectancy, names the small-sample problem, and includes the rule
violation count on the front page - because a report that only shows the numbers
you like is not an audit, it is a marketing document.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from ..analytics.performance import AnalyticsResult

__all__ = ["build_performance_pdf"]


def build_performance_pdf(
    result: AnalyticsResult, target: Path, starting_equity: float = 250.0, charts: bool = True
) -> Path:
    """Render a performance report to PDF. Requires ReportLab."""
    from .pdf_docs import pdf_available, _build_table  # type: ignore[attr-defined]

    if not pdf_available():  # pragma: no cover - optional dependency
        raise RuntimeError("PDF generation needs ReportLab. Install: pip install reportlab")

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        Image,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    from .markdown_renderer import Block

    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    report = result.report
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18,
                        textColor=colors.HexColor("#12305c"), spaceAfter=8)
    h2 = ParagraphStyle("H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12.5,
                        textColor=colors.HexColor("#1f4e79"), spaceBefore=10, spaceAfter=5)
    body = ParagraphStyle("Bodyx", parent=styles["BodyText"], fontSize=9.5, leading=13.5)
    small = ParagraphStyle("Smallx", parent=body, fontSize=8, textColor=colors.HexColor("#666666"))
    warn = ParagraphStyle("WarnX", parent=body, fontSize=9, textColor=colors.HexColor("#8a1c1c"))

    doc = SimpleDocTemplate(
        str(target), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm, title="Forex Performance Report",
        author="Forex Mastery System",
    )
    story: list = [
        Paragraph("Performance Report", h1),
        Paragraph(
            f"Generated {date.today().isoformat()} from "
            f"{Path(result.summary.get('path', 'journal')).name} - "
            f"{report.sample_size} closed trades, assumed starting equity {starting_equity:,.2f}.",
            small,
        ),
        Spacer(1, 6),
    ]

    def table(header: list[str], rows: list[list[str]], widths: list[float] | None = None):
        data = [[Paragraph(f"<b>{cell}</b>", body) for cell in header]]
        data += [[Paragraph(str(cell), body) for cell in row] for row in rows]
        instance = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1)
        instance.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b9c6d6")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fb")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return instance

    # ---- headline ------------------------------------------------------ #
    pf = "inf" if report.profit_factor == float("inf") else f"{report.profit_factor:.2f}"
    story.append(Paragraph("Headline statistics", h2))
    story.append(
        table(
            ["Metric", "Value", "Metric", "Value"],
            [
                ["Closed trades", report.sample_size, "Win rate",
                 f"{report.win_rate * 100:.1f}%"],
                ["Net P/L", f"{report.net_pnl:+,.2f}", "Profit factor", pf],
                ["Total R", f"{report.total_r:+.2f}R", "Average R / trade",
                 f"{report.avg_r:+.3f}R"],
                ["Expectancy (R)", f"{report.expectancy_r:+.4f}R",
                 "Expectancy 95% CI",
                 f"[{report.expectancy_ci95[0]:+.3f}, {report.expectancy_ci95[1]:+.3f}]R"],
                ["Average win", f"{report.avg_win:,.2f}", "Average loss",
                 f"-{report.avg_loss:,.2f}"],
                ["Largest win", f"{report.largest_win:+,.2f}", "Largest loss",
                 f"{report.largest_loss:+,.2f}"],
                ["Max drawdown", f"{report.max_drawdown_pct:.2f}%",
                 "Recovery needed", f"{report.recovery_gain_needed_pct:.2f}%"],
                ["Max consecutive losses", report.max_consecutive_losses,
                 "Rule violations",
                 f"{report.rule_violation_count} ({report.rule_violation_rate * 100:.0f}%)"],
            ],
            widths=[100, 90, 110, 100],
        )
    )

    # ---- interpretation ------------------------------------------------ #
    story.append(Paragraph("What this sample does and does not tell you", h2))
    for warning in report.warnings or ["No statistical caveats triggered."]:
        story.append(Paragraph(f"&bull; {warning}", body))
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            "Interpretation rule: an expectancy whose 95% interval includes zero is not evidence of "
            "an edge, however pleasant the equity curve looks. Sample-size rules in this project: "
            "below 30 trades = hypothesis, 30-100 = suggestive, above 100 with an out-of-sample test "
            "= informative.",
            body,
        )
    )

    # ---- actions ------------------------------------------------------- #
    story.append(Paragraph("Action list (from the data)", h2))
    for index, item in enumerate(result.summary.get("calls_to_action", []), start=1):
        story.append(Paragraph(f"{index}. {item}", body))

    # ---- charts -------------------------------------------------------- #
    if charts:
        from ..analytics.charts import build_all_charts, charts_available

        if charts_available():
            chart_dir = target.parent / f"{target.stem}_charts"
            created = build_all_charts(report, chart_dir, starting_equity)
            if created:
                story.append(PageBreak())
                story.append(Paragraph("Charts", h2))
                for path in created:
                    try:
                        story.append(Image(str(path), width=170 * mm, height=85 * mm))
                        story.append(Paragraph(path.name, small))
                        story.append(Spacer(1, 6))
                    except Exception:
                        continue

    # ---- breakdowns ---------------------------------------------------- #
    breakdowns = [
        ("By setup", report.by_setup),
        ("By instrument", report.by_instrument),
        ("By session", report.by_session),
        ("By setup quality", report.by_quality),
        ("By direction", report.by_direction),
        ("By month", report.monthly),
    ]
    for title, buckets in breakdowns:
        if not buckets:
            continue
        story.append(Paragraph(title, h2))
        rows = [
            [b.label, b.trades, f"{b.win_rate * 100:.1f}%", f"{b.total_r:+.2f}",
             f"{b.avg_r:+.3f}", ("inf" if b.profit_factor == float("inf") else f"{b.profit_factor:.2f}")]
            for b in buckets
        ]
        story.append(table(["Group", "Trades", "Win rate", "Total R", "Avg R", "PF"], rows,
                           widths=[150, 55, 60, 60, 60, 50]))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "This report is generated from your own journal and contains no forecasts. Each statistic "
            "carries estimation error; the confidence interval shown is a percentile bootstrap over "
            "the observed R-multiples.",
            warn,
        )
    )

    def decorate(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColorRGB(0.42, 0.42, 0.42)
        canvas.drawString(18 * mm, 10 * mm, "Forex Mastery System - performance report")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"page {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    _ = (Image, _build_table, Block)
    return target
