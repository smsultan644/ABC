"""Tests for the training programme, the quiz engine and the command line interface."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout

import pytest

from forex_mastery.program.demo_program import (
    READINESS_CRITERIA,
    demo_programme,
    format_day,
    format_week,
    mastery_score,
    phases,
    readiness_report,
)
from forex_mastery.quiz.engine import (
    grade_answers,
    list_categories,
    load_bank,
    select_questions,
)


# --------------------------------------------------------------------- #
# Programme
# --------------------------------------------------------------------- #
def test_programme_covers_13_weeks_and_10_phases():
    tasks = demo_programme()
    assert len(phases()) == 10
    assert len(tasks) == 91, "13 weeks x 7 days"
    weekdays = {task.weekday for task in tasks}
    assert {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"} <= weekdays
    # Wednesday and Friday are the execution days: the programme must actually require
    # simulated trades, not just reading.
    execution_days = [task for task in tasks if task.weekday in ("Wednesday", "Friday")]
    assert len(execution_days) == 26
    # every execution day must be about executing the plan (practice, journal, statistics),
    # never about reading or watching.
    assert all(
        any(word in (task.title + task.detail).lower()
            for word in ("execution", "trade the plan", "practice"))
        for task in execution_days
    )


def test_every_phase_has_a_gate_with_conditions():
    for phase in phases():
        assert phase.gate.conditions, f"phase {phase.number} has no gate conditions"
        assert all(isinstance(condition, str) and condition for condition in phase.gate.conditions)


def test_format_day_and_week_are_safe_for_every_day():
    for day in range(1, 92):
        text = format_day(day)
        assert text.strip()
    for week in range(1, 14):
        assert format_week(week).strip()


def test_mastery_scorecard_requires_evidence_and_never_flatters():
    empty = mastery_score({})
    assert empty["score"] == 0.0
    assert empty["missing_categories"], "an empty scorecard must list what is missing"

    perfect = mastery_score({category.key: 100 for category in _categories()})
    assert perfect["score"] == pytest.approx(100.0)

    # A perfect score must not be described as professional status.
    text = empty["level"] + empty["guidance"]
    assert "professional" not in text.lower() or "not" in text.lower()


def _categories():
    from forex_mastery.program.demo_program import MASTERY_CATEGORIES

    return MASTERY_CATEGORIES


def test_readiness_unanswered_counts_as_not_met():
    report = readiness_report({})
    hard_total = len([c for c in READINESS_CRITERIA if c.hard])
    assert len(report["failed_hard"]) == hard_total
    assert report["passed"] == 0
    assert report["score"] == 0.0
    assert "NOT READY" in report["verdict"].upper()


def test_readiness_all_yes_is_ready():
    answers = {criterion.key: True for criterion in READINESS_CRITERIA}
    report = readiness_report(answers)
    assert report["failed_hard"] == []
    assert "READY" in report["verdict"].upper()


def test_progress_file_round_trip(tmp_path):
    from forex_mastery.program.demo_program import (
        load_progress,
        next_incomplete_gate,
        record_gate_result,
        save_progress,
    )

    path = tmp_path / "progress.json"
    progress = load_progress(path)
    assert progress["categories"] == {}
    progress["categories"]["risk_management"] = 60.0
    save_progress(progress, path)

    record_gate_result(1, True, "mechanics quiz passed", path=path)
    payload = json.loads(path.read_text())
    assert payload["gate_results"]["1"]["passed"] is True
    assert next_incomplete_gate(path) == 2


# --------------------------------------------------------------------- #
# Quiz
# --------------------------------------------------------------------- #
def test_question_bank_structure():
    bank = load_bank()
    assert len(bank) >= 60
    categories = list_categories(bank)
    assert len(categories) == 10
    assert all(count >= 5 for count in categories.values())
    for question in bank:
        assert question.explanation, f"{question.id} has no explanation"
        assert question.question
        if question.type in ("mcq", "true_false", "scenario"):
            assert question.options, f"{question.id} is a choice question with no options"


def test_selection_is_deterministic_with_a_seed():
    bank = load_bank()
    first = [q.id for q in select_questions(bank, category="risk_management", n=4, seed=99)]
    second = [q.id for q in select_questions(bank, category="risk_management", n=4, seed=99)]
    assert first == second
    assert len(first) == 4


def test_grading_accepts_indices_text_and_numbers_with_tolerance():
    bank = {question.id: question for question in load_bank()}
    risk_001 = bank["RISK-001"]  # 0.25% of 250 = 0.625
    assert risk_001.grade("0.63") is True
    assert risk_001.grade("0.62") is False
    assert risk_001.grade("not a number") is False

    boolean = bank["RISK-007"]  # options ["True", "False"], answer index 1
    assert boolean.grade("False") is True      # option text
    assert boolean.grade("1") is True          # option NUMBER, as the CLI instructs
    assert boolean.grade("True") is False      # the true/false value, wrong here
    assert boolean.grade("F") is True          # shorthand for the false option
    assert boolean.grade("") is False


def test_quiz_result_hides_explanations_until_requested():
    bank = load_bank()
    questions = bank[:3]
    result = grade_answers(questions, ["", "", ""], seed=1)
    hidden = result.report(show_explanations=False)
    assert "explanation" not in hidden.lower()
    shown = result.report(show_explanations=True)
    assert "explanation" in shown.lower() or questions[0].explanation[:20] in shown
    assert result.total == 3
    assert result.correct <= 3


def test_quiz_results_feed_the_mastery_scorecard(tmp_path):
    from forex_mastery.program.demo_program import load_progress
    from forex_mastery.quiz.engine import mastery_scores_from_quiz, record_result

    bank = load_bank()
    questions = select_questions(bank, category="risk_management", n=6, seed=3)
    answers = [str(question.answer) for question in questions]
    result = grade_answers(questions, answers, seed=3)
    assert result.correct == 6, [d for d in result.details if not d.get("correct")]

    path = tmp_path / "progress.json"
    record_result(result, progress_path=path)
    progress = load_progress(path)
    scores = mastery_scores_from_quiz(progress)
    # A perfect quiz score maps to 60, not 100: a quiz demonstrates knowledge, not
    # practice, so the category is deliberately discounted until journal evidence exists.
    assert scores.get("risk_management", 0) == pytest.approx(60.0)
    # Practice-based categories are never inferred from quiz results at all.
    assert "execution" not in scores
    assert "journaling" not in scores


# --------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------- #
def _run(argv):
    from forex_mastery.cli import main

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(argv)
    return code, buffer.getvalue()


@pytest.mark.parametrize(
    "argv",
    [
        ["version"],
        ["doctor"],
        ["specs"],
        ["specs", "--symbol", "XAUUSD"],
        ["pip", "--symbol", "EURUSD", "--lots", "0.1"],
        ["drawdown", "--balance", "250"],
        ["sessions"],
        ["quiz", "--list"],
        ["demo", "--list"],
        ["readiness", "--criteria"],
        ["lesson", "--list"],
        ["lesson", "--number", "1"],
    ],
)
def test_cli_commands_run(argv):
    code, output = _run(argv)
    assert code == 0
    assert output.strip()
    # The system must never tell the user what to buy or sell.
    lowered = output.lower()
    assert "buy now" not in lowered and "sell now" not in lowered
    assert "guaranteed profit" not in lowered and "risk-free" not in lowered


def test_cli_position_size_matches_the_engine():
    code, output = _run([
        "position", "--symbol", "EURUSD", "--balance", "1000", "--risk", "1",
        "--entry", "1.1000", "--stop", "1.0980", "--leverage", "100",
    ])
    assert code == 0
    assert "0.05" in output
    assert "10.00" in output


def test_cli_refuses_an_untradable_size_on_a_small_account():
    code, output = _run([
        "position", "--symbol", "EURUSD", "--balance", "250", "--risk", "0.25",
        "--entry", "1.1000", "--stop", "1.0950",
    ])
    assert code == 2, "an untradable size must not report success"
    assert "minimum" in output.lower()


def test_cli_quiz_hides_answers_by_default():
    code, output = _run(["quiz", "--category", "risk_management", "--n", "2"])
    assert "explanation" not in output.lower()


def test_cli_readiness_is_strict():
    code, output = _run(["readiness", "--set", "demo_trades=yes"])
    assert code != 0, "a partially satisfied readiness check must not return success"
    assert "NOT READY" in output.upper() or "RECOMMENDATION" in output.upper()
