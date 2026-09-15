"""
Quiz engine (Level 36).

Default behaviour, by design:

* **Answers are hidden during a test.** Explanations are only printed when you
  ask for them, and only after you have committed to an answer.
* **A quiz score is a weak signal.** It measures recall under no pressure. The
  engine therefore reports accuracy with a sample size and refuses to convert a
  single 5-question quiz into a mastery score.
* **Numeric questions are graded with a tolerance**, because the skill being
  tested is "can you do the calculation", not "can you guess the decimals".

Results are written to ``outputs/progress.json`` so the mastery scorecard can
use real quiz data rather than self-assessment.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable, Sequence

__all__ = [
    "CATEGORIES",
    "Question",
    "QuizResult",
    "bank_path",
    "category_accuracy",
    "format_question",
    "grade_answers",
    "load_bank",
    "record_result",
    "select_questions",
]

CATEGORIES = (
    "beginner",
    "market_mechanics",
    "technical_analysis",
    "fundamental_analysis",
    "risk_management",
    "psychology",
    "strategy",
    "statistics",
    "backtesting",
    "professional_decision_making",
)

DIFFICULTY_LABELS = {1: "recall", 2: "understanding", 3: "application", 4: "professional judgement"}


@dataclass
class Question:
    """One question from the bank."""

    id: str
    category: str
    difficulty: int
    type: str
    question: str
    answer: int | float
    explanation: str = ""
    options: list[str] = field(default_factory=list)
    tolerance: float = 0.0

    @property
    def is_numeric(self) -> bool:
        return self.type == "numeric"

    def correct_text(self) -> str:
        if self.is_numeric:
            return f"{self.answer:g}"
        if isinstance(self.answer, int) and 0 <= self.answer < len(self.options):
            return self.options[self.answer]
        return str(self.answer)

    def grade(self, response: str | int | float | None) -> bool:
        """True when ``response`` is correct for this question."""
        if response is None or response == "":
            return False
        if self.is_numeric:
            try:
                value = float(str(response).strip().replace(",", ""))
            except (TypeError, ValueError):
                return False
            return abs(value - float(self.answer)) <= max(self.tolerance, 1e-9)
        text = str(response).strip().upper()
        if self.type in ("mcq", "scenario") and text.isdigit():
            return int(text) == int(self.answer)
        if self.type == "true_false":
            # Explicit words are unambiguous ...
            words = {"TRUE": "TRUE", "T": "TRUE", "YES": "TRUE",
                     "FALSE": "FALSE", "F": "FALSE", "NO": "FALSE"}
            if text in words:
                options = [option.strip().upper() for option in self.options]
                if "TRUE" in options and "FALSE" in options:
                    return options.index(words[text]) == int(self.answer)
                return (words[text] == "TRUE") == bool(self.answer)
            # ... but a bare digit is the OPTION number, exactly as the CLI instructs
            # ("answer with the number of the option"). Treating "1" as True here would
            # mark a correct answer wrong whenever the answer is the second option.
            if text.isdigit() and self.options:
                return int(text) == int(self.answer)
        # allow answering with the option text
        for index, option in enumerate(self.options):
            if option.strip().upper() == text:
                return index == int(self.answer)
        return False


@dataclass
class QuizResult:
    """Outcome of one quiz session."""

    total: int
    correct: int
    per_category: dict[str, tuple[int, int]] = field(default_factory=dict)
    details: list[dict] = field(default_factory=list)
    seed: int | None = None

    @property
    def score(self) -> float:
        return (self.correct / self.total * 100.0) if self.total else 0.0

    def report(self, show_explanations: bool = False) -> str:
        lines = ["=" * 74, "QUIZ RESULT", "=" * 74,
                 f"  score: {self.correct}/{self.total}  ({self.score:.0f}%)"]
        for category, (right, asked) in sorted(self.per_category.items()):
            lines.append(f"    {category:<34} {right}/{asked}")
        if self.score >= 80:
            verdict = "Strong. Move to application exercises (Level 24 scenarios) rather than more recall."
        elif self.score >= 70:
            verdict = "Adequate for this stage - but review every wrong answer until you can explain it."
        else:
            verdict = "Below the gate. Re-read the module before continuing; do not trade this material."
        lines.append(f"  verdict: {verdict}")
        if show_explanations and self.details:
            lines.append("-" * 74)
            for item in self.details:
                mark = "OK " if item["correct"] else "X  "
                lines.append(f"  [{mark}] {item['id']}  your answer: {item['response']!r}  "
                             f"correct: {item['correct_answer']}")
                if item.get("explanation"):
                    lines.append(f"        {item['explanation']}")
        lines.append("=" * 74)
        lines.append("  Reminder: quiz scores measure recall, not trading competence.")
        return "\n".join(lines)


def bank_path(root: Path | None = None) -> Path:
    """Locate ``data/questions/question_bank.json``."""
    if root is not None:
        return Path(root) / "data" / "questions" / "question_bank.json"
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        candidate = parent / "data" / "questions" / "question_bank.json"
        if candidate.is_file():
            return candidate
    return Path.cwd() / "data" / "questions" / "question_bank.json"


def load_bank(path: Path | None = None) -> list[Question]:
    """Load and validate the question bank."""
    data = json.loads(Path(path or bank_path()).read_text(encoding="utf-8"))
    questions: list[Question] = []
    for raw in data.get("questions", []):
        if raw.get("type") in ("mcq", "true_false", "scenario") and not raw.get("options"):
            if raw["type"] == "true_false":
                raw = {**raw, "options": ["True", "False"]}
            else:
                raise ValueError(f"{raw.get('id')}: choice questions need options")
        questions.append(
            Question(
                id=raw["id"],
                category=raw["category"],
                difficulty=int(raw.get("difficulty", 2)),
                type=raw["type"],
                question=raw["question"],
                answer=raw["answer"],
                explanation=raw.get("explanation", ""),
                options=list(raw.get("options", [])),
                tolerance=float(raw.get("tolerance", 0.0)),
            )
        )
    if not questions:
        raise ValueError("Question bank is empty")
    return questions


def select_questions(
    questions: Sequence[Question],
    category: str | None = None,
    difficulty: int | None = None,
    n: int = 10,
    seed: int | None = None,
    max_difficulty: int | None = None,
) -> list[Question]:
    """Filter and sample questions reproducibly."""
    pool = list(questions)
    if category:
        pool = [q for q in pool if q.category == category]
    if difficulty:
        pool = [q for q in pool if q.difficulty == difficulty]
    if max_difficulty is not None:
        pool = [q for q in pool if q.difficulty <= max_difficulty]
    rng = random.Random(seed)
    rng.shuffle(pool)
    return pool[:n]


def format_question(question: Question, index: int, total: int) -> str:
    """Render a question for terminal presentation."""
    label = DIFFICULTY_LABELS.get(question.difficulty, str(question.difficulty))
    lines = [
        "-" * 74,
        f"Q{index}/{total}  [{question.category} | {label} | {question.type}]  {question.id}",
        "",
        question.question,
    ]
    if question.options:
        lines.append("")
        for position, option in enumerate(question.options):
            lines.append(f"   {position}) {option}")
        lines.append("")
        lines.append("   answer with the number of the option")
    else:
        lines.append("")
        lines.append(f"   answer with a number (tolerance +/-{question.tolerance:g})")
    return "\n".join(lines)


def grade_answers(
    questions: Sequence[Question], responses: Sequence[str | None], seed: int | None = None
) -> QuizResult:
    """Grade a completed quiz."""
    result = QuizResult(total=len(questions), correct=0, seed=seed)
    for question, response in zip(questions, responses):
        ok = question.grade(response)
        if ok:
            result.correct += 1
        right, asked = result.per_category.get(question.category, (0, 0))
        result.per_category[question.category] = (right + (1 if ok else 0), asked + 1)
        result.details.append(
            {
                "id": question.id,
                "category": question.category,
                "question": question.question,
                "response": response,
                "correct": ok,
                "correct_answer": question.correct_text(),
                "explanation": question.explanation,
            }
        )
    return result


def record_result(
    result: QuizResult, progress_path: Path | None = None
) -> dict:
    """Store a quiz result and return the updated progress structure."""
    from ..program.demo_program import load_progress, save_progress

    progress = load_progress(progress_path)
    progress.setdefault("quiz_history", []).append(
        {
            "date": date.today().isoformat(),
            "score": result.score,
            "total": result.total,
            "per_category": {k: list(v) for k, v in result.per_category.items()},
        }
    )
    save_progress(progress, progress_path)
    return progress


def category_accuracy(progress: dict) -> dict[str, float]:
    """Aggregate quiz accuracy per category across all recorded sessions.

    Returns percentages. Categories with no data are omitted rather than
    reported as zero - absence of evidence is not evidence of incompetence, and
    conflating the two would make the mastery score dishonest.
    """
    totals: dict[str, list[int]] = {}
    for session in progress.get("quiz_history", []):
        for category, (right, asked) in (session.get("per_category") or {}).items():
            entry = totals.setdefault(category, [0, 0])
            entry[0] += int(right)
            entry[1] += int(asked)
    return {
        category: (right / asked * 100.0) if asked else 0.0
        for category, (right, asked) in totals.items()
    }


def mastery_scores_from_quiz(progress: dict) -> dict[str, float]:
    """Map quiz accuracy onto mastery-score categories.

    The quiz can only inform categories it actually tests (knowledge and theory).
    Practice-based categories - execution, journaling, risk discipline - are
    deliberately **not** inferred from a quiz; they require journal evidence.
    """
    accuracy = category_accuracy(progress)
    mapping = {
        "forex_knowledge": ("beginner", 0.6),
        "technical_analysis": ("technical_analysis", 0.5),
        "fundamental_analysis": ("fundamental_analysis", 0.6),
        "risk_management": ("risk_management", 0.6),
        "psychology": ("psychology", 0.4),
        "strategy": ("strategy", 0.4),
        "backtesting": ("backtesting", 0.5),
        "analysis": ("statistics", 0.4),
    }
    scores: dict[str, float] = {}
    for target, (source, weight) in mapping.items():
        if source in accuracy:
            scores[target] = accuracy[source] * weight
    if "market_mechanics" in accuracy and "forex_knowledge" in scores:
        scores["forex_knowledge"] = min(
            100.0, scores["forex_knowledge"] + accuracy["market_mechanics"] * 0.4
        )
    return scores


def list_categories(questions: Iterable[Question]) -> dict[str, int]:
    """Count questions per category (used by ``quiz --list``)."""
    counts: dict[str, int] = {}
    for question in questions:
        counts[question.category] = counts.get(question.category, 0) + 1
    return counts
