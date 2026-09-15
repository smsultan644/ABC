"""End-to-end tests for the analytics, reporting and document pipeline.

These tests write a small, fully deterministic journal, then check the numbers
the analytics layer derives from it, plus every output format the system claims
to produce (CSV, JSON, PNG, XLSX, PDF, DOCX).
"""

from __future__ import annotations

import csv
import json
import zipfile

import pytest

from forex_mastery.analytics.performance import (
    analyse_journal,
    write_breakdown_csvs,
    write_equity_curve_csv,
)
from forex_mastery.journal.model import TradeRecord
from forex_mastery.journal.storage import JournalStore


@pytest.fixture()
def small_journal(tmp_path):
    """10 closed trades with known outcomes: 4 winners, 5 losers, 1 breakeven."""
    path = tmp_path / "journal.csv"
    store = JournalStore(path)
    plan = [
        # (pnl, risk_amount, setup, symbol, session, rules_followed, emotion)
        (+2.00, 2.00, "trend_pullback", "EURUSD", "London", True, "calm"),
        (-1.00, 1.00, "range_reversal", "EURUSD", "New York", True, "calm"),
        (+3.00, 1.50, "trend_pullback", "GBPUSD", "London", True, "calm"),
        (-1.00, 1.00, "breakout_retest", "GBPUSD", "London", False, "frustrated"),
        (+2.50, 1.25, "trend_pullback", "USDJPY", "New York", True, "neutral"),
        (-1.00, 0.90, "range_reversal", "USDJPY", "New York", True, "neutral"),
        (0.00, 1.00, "session_open", "AUDUSD", "London", True, "calm"),
        (+2.50, 1.25, "trend_pullback", "AUDUSD", "London", True, "calm"),
        (-1.50, 1.50, "breakout_retest", "XAUUSD", "New York", False, "anxious"),
        (-0.50, 1.00, "session_open", "XAUUSD", "London", True, "tired"),
    ]
    for index, (pnl, risk, setup, symbol, session, followed, emotion) in enumerate(plan, start=1):
        store.add(
            TradeRecord(
                trade_id=f"T-{index:04d}",
                date=f"2026-07-{index:02d}",
                symbol=symbol,
                direction="long" if index % 2 else "short",
                entry=1.1000,
                stop_loss=1.0950,
                take_profit=1.1100,
                lots=0.05,
                account_equity_at_entry=250.0,
                risk_percent=round(risk / 250.0 * 100.0, 4),
                risk_amount=risk,
                planned_rr=2.0,
                setup=setup,
                session=session,
                rules_followed=followed,
                rule_violations="" if followed else "traded outside the plan",
                emotional_state=emotion,
            )
        )
        store.close_trade(
            f"T-{index:04d}",
            exit_price=1.1000 + (0.001 if pnl > 0 else -0.001),
            pnl=pnl,
            reason_for_exit="target or stop reached",
            thesis_valid=pnl > 0,
            lesson="reviewed",
        )
    return path


# --------------------------------------------------------------------- #
# Analytics
# --------------------------------------------------------------------- #
def test_analyse_journal_core_statistics(small_journal):
    result = analyse_journal(small_journal, starting_equity=250.0)
    report = result.report

    assert report.sample_size == 10
    assert report.wins == 4
    assert report.losses == 5
    assert report.breakeven == 1
    assert report.win_rate == pytest.approx(4 / 9, abs=1e-9)
    # gross profit 2.00 + 3.00 + 2.50 + 2.50 = 10.00 ; gross loss 1 + 1 + 1 + 1.5 + 0.5 = 5.00
    assert report.gross_profit == pytest.approx(10.00)
    assert report.gross_loss == pytest.approx(5.00)
    assert report.profit_factor == pytest.approx(2.0)
    assert report.net_pnl == pytest.approx(5.0)
    # R multiples: 1.00, -1.00, 2.00, -1.00, 2.00, -1.11, 0.00, 2.00, -1.00, -0.50
    assert report.total_r == pytest.approx(2.39, abs=0.01)
    assert report.rule_violation_count == 2
    assert report.rule_violation_rate == pytest.approx(0.2)


def test_analyse_journal_summary_actions_and_json(small_journal, tmp_path):
    result = analyse_journal(small_journal, starting_equity=250.0)
    assert result.summary["starting_equity_assumed"] == 250.0
    assert result.summary["calls_to_action"], "the report must always produce actions"
    # With 10 trades the CI is meaningless and the summary must say so rather than
    # pretend there is a demonstrated edge.
    joined = " ".join(result.summary["calls_to_action"]).lower()
    assert "confidence interval" in joined or "sample" in joined or "unproven" in joined

    target = result.to_json(tmp_path / "performance.json")
    payload = json.loads(target.read_text())
    assert set(payload) == {"summary", "performance"}
    assert payload["performance"]["sample_size"] == 10


def test_breakdown_and_equity_csvs_are_written(small_journal, tmp_path):
    result = analyse_journal(small_journal, starting_equity=250.0)
    equity = write_equity_curve_csv(result.report, tmp_path / "equity_curve.csv")
    rows = list(csv.DictReader(equity.open()))
    # the curve starts at the untouched account, then one row per closed trade
    assert len(rows) == 11
    assert rows[0]["cumulative_r"] == "0.0"
    assert "cumulative_r" in rows[0]
    # The equity curve must equal the running sum of the R multiples.
    final = float(rows[-1]["cumulative_r"])
    assert final == pytest.approx(result.report.total_r, abs=1e-3)  # CSV is rounded to 4 dp

    written = write_breakdown_csvs(result.report, tmp_path / "breakdowns")
    names = {path.name for path in written}
    assert "by_setup.csv" in names
    assert "r_distribution.csv" in names
    setup_rows = list(csv.DictReader((tmp_path / "breakdowns" / "by_setup.csv").open()))
    labels = {row["group"] for row in setup_rows}
    assert "trend_pullback" in labels


def test_charts_are_optional_and_never_fatal(small_journal, tmp_path):
    from forex_mastery.analytics.charts import build_all_charts, charts_available

    result = analyse_journal(small_journal, starting_equity=250.0)
    produced = build_all_charts(result.report, tmp_path / "charts", 250.0)
    if charts_available():
        assert produced, "matplotlib is installed, so charts should be produced"
        for path in produced:
            assert path.exists() and path.stat().st_size > 1000
    else:
        assert produced == []


# --------------------------------------------------------------------- #
# Report renderers
# --------------------------------------------------------------------- #
def test_markdown_renderer_handles_the_subset():
    from forex_mastery.reports.markdown_renderer import parse_markdown, plain_text_length

    text = (
        "# Title\n\nA paragraph with **bold** text.\n\n"
        "- one\n- two\n\n1. first\n2. second\n\n"
        "| a | b |\n|---|---|\n| 1 | 2 |\n\n```\ncode\n```\n\n> quote\n"
    )
    blocks = parse_markdown(text)
    kinds = [block.kind for block in blocks]
    assert {"h1", "p", "ul", "ol", "table", "code"} <= set(kinds)
    table = next(block for block in blocks if block.kind == "table")
    assert table.header == ["a", "b"]
    assert table.rows == [["1", "2"]]
    assert plain_text_length(blocks) > 10


def test_docx_writer_produces_a_valid_zip(tmp_path):
    from forex_mastery.reports.docx_writer import write_docx
    from forex_mastery.reports.markdown_renderer import parse_markdown

    blocks = parse_markdown("# Test\n\nHello **world**.\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
    target = write_docx(blocks, tmp_path / "test.docx", title="Test document")
    assert target.exists() and target.stat().st_size > 1000
    with zipfile.ZipFile(target) as archive:
        names = set(archive.namelist())
        assert "word/document.xml" in names
        assert "[Content_Types].xml" in names
        document = archive.read("word/document.xml").decode()
        assert "Hello" in document and "Test document" in document


def test_pdf_generation_or_explicit_error(tmp_path):
    from forex_mastery.reports import pdf_docs

    if not pdf_docs.pdf_available():
        with pytest.raises(RuntimeError) as excinfo:
            pdf_docs.markdown_to_pdf([], tmp_path / "x.pdf", "t", "s")
        assert "reportlab" in str(excinfo.value).lower()
        return
    from forex_mastery.reports.markdown_renderer import parse_markdown

    blocks = parse_markdown("# Heading\n\nBody text with a list:\n\n- a\n- b\n")
    target = pdf_docs.markdown_to_pdf(blocks, tmp_path / "test.pdf", "Title", "Subtitle")
    assert target.exists() and target.stat().st_size > 1000
    assert target.read_bytes()[:5] == b"%PDF-"


def test_excel_workbook_or_explicit_error(tmp_path):
    from forex_mastery.reports import excel_workbook

    if not excel_workbook.excel_available():
        with pytest.raises(RuntimeError) as excinfo:
            excel_workbook.build_master_workbook(tmp_path / "x.xlsx")
        assert "xlsxwriter" in str(excinfo.value).lower()
        return
    target = excel_workbook.build_master_workbook(tmp_path / "master.xlsx")
    assert target.exists() and target.stat().st_size > 5000
    with zipfile.ZipFile(target) as archive:
        workbook_xml = archive.read("xl/workbook.xml").decode()
    for sheet in excel_workbook.SHEET_NAMES:
        assert sheet in workbook_xml, f"sheet {sheet!r} missing from the workbook"


def test_performance_pdf_renders_from_analytics(small_journal, tmp_path):
    from forex_mastery.reports import pdf_docs, performance_pdf

    if not pdf_docs.pdf_available():
        pytest.skip("reportlab not installed")
    result = analyse_journal(small_journal, starting_equity=250.0)
    target = performance_pdf.build_performance_pdf(
        result, tmp_path / "performance.pdf", starting_equity=250.0, charts=False
    )
    assert target.stat().st_size > 1000
    assert target.read_bytes()[:5] == b"%PDF-"


def test_document_library_reports_missing_sources_honestly(tmp_path):
    from forex_mastery.reports.library import DOCUMENT_LIBRARY, build_documents

    assert len(DOCUMENT_LIBRARY) >= 18
    written, problems = build_documents(which=("docx",), outdir=tmp_path, root=tmp_path)
    # The generated documents (no markdown source) are still produced ...
    assert sorted(path.name for path in written) == [
        "complete_handbook.docx", "risk_framework_250.docx"
    ]
    # ... and every source-based document is reported as missing rather than silently
    # skipped or, worse, faked with placeholder content.
    sourced = [doc for doc in DOCUMENT_LIBRARY if doc.source]
    assert len(problems) == len(sourced)
    assert all("missing source" in problem for problem in problems)


def test_generated_risk_framework_document_matches_the_engine():
    from forex_mastery.core.risk import drawdown_ladder, recovery_gain_required
    from forex_mastery.reports.library import risk_framework_markdown

    text = risk_framework_markdown()
    assert text.startswith("# USD 250 Risk Framework")
    assert f"+{recovery_gain_required(50):.1f}%" in text
    ladder = {row.drawdown_percent: row for row in drawdown_ladder()}
    assert str(ladder[10.0].losses_at_0_25_pct) in text
    assert "prohibited" not in text.lower() or "Prohibited practices" in text


def test_templates_are_written_and_journal_schema_matches(tmp_path):
    from forex_mastery.journal.model import JOURNAL_COLUMNS
    from forex_mastery.reports.templates import write_all_templates

    paths = write_all_templates(tmp_path)
    names = {path.name for path in paths}
    assert "trading_journal_template.csv" in names
    assert "strategy_specification.md" in names
    header = (tmp_path / "trading_journal_template.csv").read_text().splitlines()[0]
    assert header.split(",") == list(JOURNAL_COLUMNS)


def test_notebooks_are_valid_nbformat_json(tmp_path):
    from forex_mastery.reports.notebooks import build_notebooks, notebook_names

    written = build_notebooks(tmp_path)
    assert len(written) == 20
    assert {path.name for path in written} == set(notebook_names())
    for path in written:
        payload = json.loads(path.read_text())
        assert payload["nbformat"] == 4
        kinds = [cell["cell_type"] for cell in payload["cells"]]
        assert "code" in kinds and "markdown" in kinds
