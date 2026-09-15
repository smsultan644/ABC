"""
Markdown -> PDF rendering with ReportLab (optional dependency).

The output is designed to be **printed and written on**, because the workbooks
in this course are meant to be completed by hand as well as on screen:

* wide margins for notes,
* a footer with the document name and page number,
* tables that wrap rather than overflow,
* code blocks in a monospace font with a light background.

If ReportLab is not installed, the CLI prints an actionable message instead of
raising a stack trace: ``pip install reportlab``.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Iterable

from .markdown_renderer import Block

__all__ = ["pdf_available", "markdown_to_pdf", "render_markdown_file"]

PAGE_WIDTH_MM = 210
MARGIN_MM = 20


def pdf_available() -> bool:
    try:
        import reportlab  # noqa: F401
    except Exception:
        return False
    return True


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _inline(text: str) -> str:
    """Markdown inline markup -> ReportLab paragraph markup."""
    text = _escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text, flags=re.DOTALL)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]+?)`", r'<font face="Courier" size="8.5">\1</font>', text)
    return text


def markdown_to_pdf(
    blocks: Iterable[Block],
    target: Path,
    title: str,
    subtitle: str = "",
    footer: str | None = None,
) -> Path:
    """Render parsed markdown blocks into a paginated PDF.

    Raises
    ------
    RuntimeError
        If ReportLab is unavailable, with the exact install command in the message.
    """
    if not pdf_available():  # pragma: no cover - depends on optional dependency
        raise RuntimeError(
            "PDF generation needs ReportLab. Install it with:  pip install reportlab"
        )

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        HRFlowable,
        KeepTogether,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.5,
        leading=14, alignment=TA_JUSTIFY, spaceAfter=6,
    )
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold",
                        fontSize=17, leading=21, spaceBefore=12, spaceAfter=7,
                        textColor=colors.HexColor("#12305c"))
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold",
                        fontSize=13, leading=17, spaceBefore=12, spaceAfter=5,
                        textColor=colors.HexColor("#1f4e79"))
    h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontName="Helvetica-Bold",
                        fontSize=11, leading=15, spaceBefore=10, spaceAfter=4,
                        textColor=colors.HexColor("#2e5496"))
    h4 = ParagraphStyle("H4", parent=styles["Heading4"], fontName="Helvetica-Bold",
                        fontSize=10, leading=14, spaceBefore=8, spaceAfter=3)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=14, bulletIndent=4,
                            spaceAfter=3, alignment=0)
    code = ParagraphStyle("Code", parent=styles["Code"], fontName="Courier",
                          fontSize=7.8, leading=10, backColor=colors.HexColor("#f4f4f4"),
                          borderPadding=4, spaceAfter=1, spaceBefore=1)
    quote = ParagraphStyle("Quote", parent=body, leftIndent=14, textColor=colors.HexColor("#333333"))
    title_style = ParagraphStyle("TitleX", parent=styles["Title"], fontName="Helvetica-Bold",
                                 fontSize=26, leading=30, alignment=TA_CENTER,
                                 textColor=colors.HexColor("#12305c"))
    sub_style = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=11.5, leading=16,
                               alignment=TA_CENTER, textColor=colors.HexColor("#444444"))
    note_style = ParagraphStyle("Note", parent=body, fontSize=8.5, leading=12,
                                alignment=TA_CENTER, textColor=colors.HexColor("#7a1f1f"))

    doc = SimpleDocTemplate(
        str(target),
        pagesize=A4,
        leftMargin=MARGIN_MM * mm,
        rightMargin=MARGIN_MM * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=title,
        author="Forex Mastery System",
        subject="Forex education, risk management and trading process documentation",
    )

    story: list = [Spacer(1, 60 * mm), Paragraph(_escape(title), title_style)]
    if subtitle:
        story.append(Spacer(1, 5 * mm))
        story.append(Paragraph(_escape(subtitle), sub_style))
    story.append(Spacer(1, 10 * mm))
    story.append(
        Paragraph(
            f"Generated {date.today().isoformat()} from the Forex Mastery System "
            "(Markdown source in <font face='Courier'>docs/</font>).",
            sub_style,
        )
    )
    story.append(Spacer(1, 12 * mm))
    story.append(
        Paragraph(
            "<b>Risk warning.</b> Trading foreign exchange and CFDs on margin carries a high "
            "level of risk and can result in the loss of all of your capital. Nothing in this "
            "document is investment advice, a recommendation, or a prediction. No method "
            "described here guarantees a profit, and past performance does not indicate "
            "future results. Verify every broker-specific figure against your own platform.",
            note_style,
        )
    )
    story.append(PageBreak())

    for block in blocks:
        if block.kind == "h1":
            story.append(Paragraph(_inline(block.text), h1))
        elif block.kind == "h2":
            story.append(Paragraph(_inline(block.text), h2))
        elif block.kind == "h3":
            story.append(Paragraph(_inline(block.text), h3))
        elif block.kind == "h4":
            story.append(Paragraph(_inline(block.text), h4))
        elif block.kind == "p":
            story.append(Paragraph(_inline(block.text), body))
        elif block.kind == "quote":
            story.append(Paragraph(_inline(block.text), quote))
        elif block.kind == "ul":
            for item in block.items:
                story.append(Paragraph(_inline(item), bullet, bulletText="\u2022"))
        elif block.kind == "ol":
            for number, item in enumerate(block.items, start=1):
                story.append(Paragraph(_inline(item), bullet, bulletText=f"{number}."))
        elif block.kind == "code":
            lines = (block.text or "").split("\n")
            story.append(Spacer(1, 2))
            for line in lines:
                story.append(Paragraph(_escape(line.replace(" ", "&nbsp;")) or "&nbsp;", code))
            story.append(Spacer(1, 4))
        elif block.kind == "table":
            table = _build_table(block, body, colors, Table, TableStyle)
            if table is not None:
                story.append(KeepTogether([table, Spacer(1, 6)]))
        elif block.kind == "hr":
            story.append(HRFlowable(width="100%", thickness=0.6,
                                    color=colors.HexColor("#bbbbbb"), spaceBefore=6, spaceAfter=6))

    def decorate(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColorRGB(0.42, 0.42, 0.42)
        label = footer or title
        canvas.drawString(MARGIN_MM * mm, 12 * mm, label[:95])
        canvas.drawRightString(A4[0] - MARGIN_MM * mm, 12 * mm, f"page {document.page}")
        canvas.restoreState()

    target.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    return target


def _build_table(block: Block, body_style, colors, Table, TableStyle):
    """Build a wrapped ReportLab table from a markdown table block."""
    header = block.header
    rows = block.rows
    if not header and not rows:
        return None
    from reportlab.platypus import Paragraph

    cell_style = body_style.clone("Cell", fontSize=8, leading=10.5, spaceAfter=0, alignment=0)
    head_style = cell_style.clone("CellHead", fontName="Helvetica-Bold", textColor=colors.white)
    data = [[Paragraph(_inline(cell), head_style) for cell in header]]
    for row in rows:
        padded = list(row) + [""] * (len(header) - len(row))
        data.append([Paragraph(_inline(cell), cell_style) for cell in padded[: len(header)]])
    available = 170.0
    columns = max(1, len(header))
    table = Table(data, colWidths=[available / columns] * columns, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b9c6d6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fb")]),
            ]
        )
    )
    return table


def render_markdown_file(
    source: Path, target: Path, title: str = "", subtitle: str = ""
) -> Path:
    """Convenience wrapper: parse a ``.md`` file and render it to PDF."""
    from .markdown_renderer import parse_markdown

    text = Path(source).read_text(encoding="utf-8")
    blocks = parse_markdown(text)
    return markdown_to_pdf(blocks, Path(target), title=title or Path(source).stem, subtitle=subtitle)
