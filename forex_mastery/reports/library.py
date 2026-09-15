"""
The document library: which documents exist, where their source lives, and how
they are rendered to PDF/DOCX.

ARCHITECTURE DECISION
---------------------
**Markdown is the source of truth.** Every handbook is a ``.md`` file under
``docs/handbooks/``. The generators in this package only *render* them:

    docs/handbooks/*.md   ->   outputs/pdf/*.pdf   (ReportLab)
                          ->   outputs/docx/*.docx (built-in OOXML writer)

Consequences that matter:

* the content is readable and editable in VS Code, and diffs cleanly in git;
* the same source produces both formats, so they cannot disagree;
* nothing in the content depends on a paid tool or a proprietary format;
* a document that has not been written yet is reported as such, never faked.

Two documents are **generated** rather than authored, because their content is
computed: the risk framework (tables produced by the calculation engine) and the
90-day programme (produced by the programme module). Generated documents are
marked with ``generator`` so it is always clear where a number came from.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

__all__ = ["DOCUMENT_LIBRARY", "Document", "build_documents", "library_summary"]


@dataclass(frozen=True)
class Document:
    """One document in the library."""

    key: str
    title: str
    subtitle: str
    source: str | None = None           # path relative to the repo root
    generator: str | None = None        # name of a function that produces Markdown
    category: str = "handbook"
    required: bool = True


DOCUMENT_LIBRARY: tuple[Document, ...] = (
    Document("master_roadmap", "Master Roadmap and System Architecture",
             "The complete journey, curriculum, architecture and milestones",
             "docs/00_MASTER_ROADMAP.md", category="orientation"),
    Document("curriculum", "Complete Curriculum",
             "Every module, submodule and gate, from Level 0 to Level 28",
             "docs/01_CURRICULUM.md", category="orientation"),
    Document("complete_handbook", "Complete Forex Mastery Handbook",
             "The full course: Levels 0-28 in one printable volume - assembled from the "
             "individual handbook chapters so the two can never disagree",
             None, generator="complete_handbook_markdown", category="handbook"),
    Document("beginner_guide", "Beginner Forex Guide",
             "Absolute-beginner edition: mechanics, vocabulary and first principles",
             "docs/handbooks/02_beginner_guide.md", category="handbook"),
    Document("technical_handbook", "Technical Analysis Handbook",
             "Candles, structure, levels, indicators and multi-timeframe procedure",
             "docs/handbooks/03_technical_analysis.md", category="handbook"),
    Document("fundamental_handbook", "Fundamental and Macro Handbook",
             "Central banks, data releases, yields and how they reach price",
             "docs/handbooks/04_fundamental_analysis.md", category="handbook"),
    Document("price_action_handbook", "Price Action Handbook",
             "Impulse, correction, expansion, liquidity and how to test the frameworks",
             "docs/handbooks/05_price_action.md", category="handbook"),
    Document("risk_handbook", "Risk Management Handbook",
             "The most important module: sizing, drawdown, expectancy and ruin",
             "docs/handbooks/06_risk_management.md", category="handbook"),
    Document("psychology_handbook", "Trading Psychology Handbook",
             "Biases, checklists and mechanical defences",
             "docs/handbooks/07_psychology.md", category="handbook"),
    Document("strategy_handbook", "Strategy Handbook",
             "Thirteen strategy families with conditions, rules and failure modes",
             "docs/handbooks/08_strategies.md", category="handbook"),
    Document("backtesting_handbook", "Backtesting and Validation Handbook",
             "Manual and programmatic testing, biases and the seven-stage gate",
             "docs/handbooks/09_backtesting.md", category="handbook"),
    Document("exness_guide", "Exness / MetaTrader Operating Guide",
             "Account structure, platform operation and verified broker specifications",
             "docs/handbooks/10_exness_mt5_guide.md", category="broker"),
    Document("demo_manual", "Demo Trading Manual",
             "How to run the 90-day programme, day by day and week by week",
             "docs/handbooks/11_demo_manual.md", category="programme"),
    Document("trading_plan", "Professional Trading Plan",
             "Your written plan: the single document that governs every decision",
             "docs/handbooks/12_trading_plan.md", category="plan"),
    Document("daily_checklist", "Daily Trading Checklist",
             "Pre-trade, during-trade and post-trade checklists",
             "docs/handbooks/13_daily_checklist.md", category="checklist"),
    Document("weekly_review", "Weekly Review",
             "The weekly process review: statistics, discipline and next week's focus",
             "docs/handbooks/14_weekly_review.md", category="checklist"),
    Document("monthly_review", "Monthly Review",
             "The month is the smallest honest unit for judging a strategy",
             "docs/handbooks/15_monthly_review.md", category="checklist"),
    Document("strategy_workbook", "Strategy Development Workbook",
             "Fill-in forms for designing and freezing a strategy",
             "docs/handbooks/16_strategy_development_workbook.md", category="workbook"),
    Document("decision_workbook", "Decision-Making Workbook",
             "Progressive scenario drills with model reasoning",
             "docs/handbooks/17_decision_making_workbook.md", category="workbook"),
    Document("demo_programme", "90-Day Demo Training Programme",
             "Thirteen weeks, ten phases, ten gates",
             "docs/handbooks/18_90_day_programme.md", category="programme"),
    Document("risk_framework_250", "USD 250 Risk Framework",
             "Generated risk tables for a 250 USD account at four risk levels",
             None, generator="risk_framework_markdown", category="plan"),
)


def library_summary() -> str:
    """Human-readable list of the document library."""
    lines = ["=" * 78, "DOCUMENT LIBRARY", "=" * 78]
    for document in DOCUMENT_LIBRARY:
        origin = document.source or f"generated: {document.generator}"
        lines.append(f"  {document.key:<24} {document.category:<12} {origin}")
        lines.append(f"      {document.title}")
    lines.append("-" * 78)
    lines.append("  Markdown is the source of truth; PDF and DOCX are rendered from it.")
    return "\n".join(lines)


def risk_framework_markdown() -> str:
    """Generate the 250 USD risk framework document from the calculation engine.

    Generated rather than authored so the tables can never disagree with the
    code that produces them.
    """
    import json

    from ..core.risk import drawdown_ladder, recovery_gain_required
    from ..core.risk_of_ruin import simulate_risk_of_ruin

    profile_path = Path(__file__).resolve().parents[2] / "config" / "risk_profile.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8")) if profile_path.is_file() else {}

    lines: list[str] = []
    lines.append("# USD 250 Risk Framework")
    lines.append("")
    lines.append(
        "**Generated document.** Every number below is produced by the calculation engine in "
        "`forex_mastery.core`, so the tables cannot drift from the code. Re-generate with "
        "`python main.py build pdf`."
    )
    lines.append("")
    lines.append("## 1. The philosophy in one paragraph")
    lines.append("")
    lines.append(
        "A 250 USD account cannot be traded safely in the sense of 'protected from loss'; at 0.25% "
        "risk, one loss is 0.63 USD. That is the point. The account exists to buy experience at a "
        "price low enough that one bad week does not end the project, and to build the habits that "
        "make a larger account survivable later. The objective is capital preservation and "
        "decision-making quality; profit is a consequence of those two, if it comes at all."
    )
    lines.append("")
    lines.append("## 2. Risk levels and what they mean")
    lines.append("")
    lines.append("| Risk per trade | Money at risk on 250 USD | Typical use |")
    lines.append("|---|---|---|")
    for risk, use in (
        (0.10, "First 4 weeks of demo execution: learning to follow the process at almost zero cost"),
        (0.25, "Standard demo risk for the programme; the level at which a live evaluation should start"),
        (0.50, "Only after 100+ journalled demo trades with proven rule compliance"),
        (1.00, "Hard cap. Never exceeded, including during a winning streak"),
    ):
        lines.append(f"| {risk:.2f}% | {250 * risk / 100:.2f} USD | {use} |")
    lines.append("")
    lines.append("## 3. How many losses to reach each drawdown (compounding)")
    lines.append("")
    lines.append(
        "Losses are calculated on the *remaining* equity, so these counts are slightly higher than "
        "naive division by the risk percentage. Formula: "
        "`n = ceil(ln(1 - DD) / ln(1 - risk))`."
    )
    lines.append("")
    lines.append("| Risk per trade | -5% | -10% | -20% | -30% | -50% |")
    lines.append("|---|---|---|---|---|---|")
    for risk in (0.10, 0.25, 0.50, 1.00, 2.00, 5.00):
        import math

        counts = [
            math.ceil(math.log(1 - dd / 100) / math.log(1 - risk / 100)) for dd in (5, 10, 20, 30, 50)
        ]
        lines.append(f"| {risk:.2f}% | " + " | ".join(str(c) for c in counts) + " |")
    lines.append("")
    lines.append("## 4. Why recovery gets harder, not easier")
    lines.append("")
    lines.append("| Drawdown | Gain required on the remaining equity |")
    lines.append("|---|---|")
    for dd in (5, 10, 20, 30, 50, 70):
        lines.append(f"| -{dd}% | +{recovery_gain_required(dd):.1f}% |")
    lines.append("")
    lines.append(
        "After a 50% drawdown you must double what is left. Nothing about your edge has improved to "
        "make that easier, and your ability to size correctly has been reduced by the same factor. "
        "This asymmetry - not lack of skill - is why capital preservation outranks profit."
    )
    lines.append("")
    lines.append("## 5. Risk of ruin simulation (fixed-fractional risk)")
    lines.append("")
    lines.append(
        "Monte Carlo, 5,000 paths x 400 trades, assuming a genuine 45% win rate at 1.5R with 0.05R "
        "of round-trip cost, ruin defined as -50% of the starting equity:"
    )
    lines.append("")
    lines.append("| Risk per trade | P(ruin) | P(drawdown > 20%) | P(drawdown > 50%) | Median final equity |")
    lines.append("|---|---|---|---|---|")
    for risk in (0.0025, 0.005, 0.01, 0.02, 0.05):
        result = simulate_risk_of_ruin(
            0.45, 1.5, risk, trades=400, paths=5000, starting_equity=250.0,
            ruin_fraction=0.5, cost_in_r=0.05, seed=17,
        )
        lines.append(
            f"| {risk * 100:.2f}% | {result.ruin_probability * 100:.2f}% | "
            f"{result.prob_drawdown_over_20pct * 100:.1f}% | "
            f"{result.prob_drawdown_over_50pct * 100:.1f}% | "
            f"{result.median_final_equity:.2f} |"
        )
    lines.append("")
    lines.append(
        "Read this as a distribution rather than a forecast: it assumes the 45% win rate is real, "
        "which is exactly the thing you have not yet demonstrated. The shape of the result - ruin "
        "probability climbing steeply with risk while median growth also rises - is the trade-off "
        "you are choosing between."
    )
    lines.append("")
    lines.append("## 6. The minimum-lot problem, stated honestly")
    if profile:
        section = profile.get("minimum_lot_problem", {})
        if section:
            lines.append("")
            lines.append(section.get("statement", ""))
            lines.append("")
            lines.append(f"**Consequence:** {section.get('consequence', '')}")
            lines.append("")
            lines.append(f"**Never do:** {section.get('never_do', '')}")
    lines.append("")
    lines.append("## 7. Prohibited practices")
    lines.append("")
    for item in profile.get("prohibited", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 8. Review cadence")
    lines.append("")
    for cadence, detail in (profile.get("review_cadence") or {}).items():
        lines.append(f"- **{cadence}**: {detail}")
    return "\n".join(lines)


def _programme_markdown() -> str:
    """Generate the 90-day programme document from the programme module."""
    from ..program.demo_program import READINESS_CRITERIA, demo_programme, phases

    lines = ["# 90-Day Demo Training Programme", "",
             "Thirteen weeks, ten phases, ten gates. A gate that is not passed means the phase is "
             "repeated - that is the mechanism which makes this a programme rather than a reading "
             "list.", ""]
    lines.append("## The weekly rhythm")
    lines.append("")
    lines.append("| Day | Focus | Time |")
    lines.append("|---|---|---|")
    lines.append("| Monday | Market preparation and written plan | 60 min |")
    lines.append("| Tuesday | Study block + blind chart-marking drill | 75 min |")
    lines.append("| Wednesday | Execution practice (demo) with journaling | 60 min |")
    lines.append("| Thursday | Study block + quiz on the weakest category | 75 min |")
    lines.append("| Friday | Execution practice + weekly statistics | 75 min |")
    lines.append("| Saturday | Deep review with screenshots (no trading) | 90 min |")
    lines.append("| Sunday | Rest, reading, plan next week | 45 min |")
    lines.append("")
    lines.append("Total commitment: roughly 8 hours per week. If you cannot sustain that, halve the "
                 "trading days rather than halving the study - studying without executing produces "
                 "knowledge you cannot use, and executing without studying produces data you cannot "
                 "interpret.")
    lines.append("")
    lines.append("## The ten phases")
    lines.append("")
    for phase in phases():
        lines.append(f"### Phase {phase.number}: {phase.name} (weeks {phase.weeks})")
        lines.append("")
        lines.append(f"**Curriculum:** {phase.level_refs}")
        lines.append("")
        lines.append(f"**Objective:** {phase.objective}")
        lines.append("")
        lines.append("**Study:**")
        for item in phase.study:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("**Exercises:**")
        for item in phase.exercises:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("**Demo tasks:**")
        for item in phase.demo_tasks:
            lines.append(f"- {item}")
        lines.append("")
        lines.append(f"**Gate - {phase.gate.name}:** pass every condition to continue:")
        for condition in phase.gate.conditions:
            lines.append(f"- [ ] {condition}")
        if phase.warning:
            lines.append("")
            lines.append(f"> **Warning.** {phase.warning}")
        lines.append("")
    lines.append("## Daily task list")
    lines.append("")
    lines.append("The full expanded schedule (91 days) is available with "
                 "`python main.py demo --day N` and `python main.py demo --week N`.")
    lines.append("")
    lines.append("## Readiness criteria for a small live account")
    lines.append("")
    lines.append("| Criterion | Hard? | Evidence required |")
    lines.append("|---|---|---|")
    for criterion in READINESS_CRITERIA:
        lines.append(
            f"| {criterion.description} | {'**HARD**' if criterion.hard else 'soft'} | "
            f"{criterion.evidence_hint} |"
        )
    lines.append("")
    lines.append("Run `python main.py readiness --criteria` to list them, and "
                 "`python main.py readiness --set key=yes ...` to assess yourself. Unanswered "
                 "criteria count as NOT MET.")
    _ = demo_programme()
    return "\n".join(lines)


def complete_handbook_markdown() -> str:
    """Assemble every handbook chapter into one printable volume, in curriculum order."""
    root = Path(__file__).resolve().parents[2]
    handbook_dir = root / "docs" / "handbooks"
    parts: list[str] = [
        "# Complete Forex Mastery Handbook",
        "",
        "**How this document is built.** It is assembled automatically from the individual "
        "handbook files in `docs/handbooks/`. Editing a chapter means editing that file and "
        "re-running `python main.py build pdf`; the volume can never drift from its chapters.",
        "",
        "**How to use it.** Read the section that matches your current phase, do the exercises, "
        "and pass the associated gate before moving on. Reading without doing changes nothing.",
        "",
        "**What this is not.** No forecasts, no signals, no promises. It teaches a process; the "
        "market decides the outcomes.",
        "",
    ]
    found = 0
    for path in sorted(handbook_dir.glob("*.md")):
        if path.name.startswith("01_"):
            continue
        parts.append("\n\n---\n\n")
        parts.append(path.read_text(encoding="utf-8").strip())
        found += 1
    if not found:
        parts.append(
            "\n\n*(No handbook chapters exist yet in `docs/handbooks/`. Build the curriculum in "
            "order so this volume is assembled from real chapters rather than placeholders.)*"
        )
    return "\n".join(parts)


GENERATORS: dict[str, Callable[[], str]] = {
    "complete_handbook_markdown": complete_handbook_markdown,
    "risk_framework_markdown": risk_framework_markdown,
    "programme_markdown": _programme_markdown,
}


def build_documents(
    which: Iterable[str] = ("pdf", "docx"),
    outdir: Path | None = None,
    include_notebooks: bool = False,
    root: Path | None = None,
) -> tuple[list[Path], list[str]]:
    """Render every library document to the requested formats.

    Returns
    -------
    (written_paths, problems)
        ``problems`` lists documents that could not be rendered, with the reason.
        Missing content is reported, never silently skipped: a library that
        quietly produces nine of eighteen documents is worse than one that says
        which nine are missing.
    """
    root = Path(root) if root else Path(__file__).resolve().parents[2]
    outdir = Path(outdir) if outdir else root / "outputs"
    formats = {fmt.lower() for fmt in which}
    written: list[Path] = []
    problems: list[str] = []

    from .markdown_renderer import parse_markdown

    for document in DOCUMENT_LIBRARY:
        if document.source:
            source = root / document.source
            if not source.is_file():
                problems.append(f"missing source for '{document.key}': {document.source}")
                continue
            text = source.read_text(encoding="utf-8")
        elif document.generator:
            generator = GENERATORS.get(document.generator)
            if generator is None:
                problems.append(f"unknown generator '{document.generator}' for '{document.key}'")
                continue
            text = generator()
        else:
            problems.append(f"document '{document.key}' has neither source nor generator")
            continue

        blocks = parse_markdown(text)
        if "pdf" in formats:
            try:
                from .pdf_docs import markdown_to_pdf, pdf_available

                if not pdf_available():
                    problems.append("PDF skipped: pip install reportlab")
                    formats.discard("pdf")
                else:
                    target = outdir / "pdf" / f"{document.key}.pdf"
                    written.append(
                        markdown_to_pdf(blocks, target, document.title, document.subtitle)
                    )
            except Exception as exc:  # pragma: no cover - defensive
                problems.append(f"PDF failed for '{document.key}': {exc}")
        if "docx" in formats:
            try:
                from .docx_writer import write_docx

                target = outdir / "docx" / f"{document.key}.docx"
                written.append(write_docx(blocks, target, title=document.title))
            except Exception as exc:  # pragma: no cover - defensive
                problems.append(f"DOCX failed for '{document.key}': {exc}")

    if include_notebooks:
        try:
            from .notebooks import build_notebooks

            written.extend(build_notebooks(root / "notebooks"))
        except Exception as exc:  # pragma: no cover - optional dependency
            problems.append(f"notebooks skipped: {exc}")

    return written, problems
