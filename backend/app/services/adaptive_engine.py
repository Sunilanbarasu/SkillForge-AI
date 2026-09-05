from typing import Dict, Any, List

from sqlalchemy.orm import Session

from app.models.assessment import Assessment, SkillScore, Answer
from app.models.question import Question


def classify_score(score: float) -> str:
    """
    Uses SkillForge's existing score classification.
    """

    if score >= 80.0:
        return "Strong"
    elif score >= 65.0:
        return "Good"
    elif score >= 50.0:
        return "Needs Improvement"
    else:
        return "Critical"


def calculate_trend(
    current_score: float,
    previous_score: float | None,
) -> str:

    if previous_score is None:
        return "New"

    change = current_score - previous_score

    if change > 5:
        return "Improving"

    if change < -5:
        return "Declining"

    return "Stable"


def calculate_priority(
    score: float,
    score_change: float | None,
    classification: str,
) -> str:

    if classification == "Critical":
        return "High"

    if score_change is not None and score_change <= -10:
        return "High"

    if classification == "Needs Improvement":
        return "Medium"

    if score_change is not None and score_change < 0:
        return "Medium"

    return "Low"


def _get_latest_assessments(
    current_user_id: int,
    db: Session,
) -> tuple[Assessment, Assessment | None]:

    assessments = (
        db.query(Assessment)
        .filter(
            Assessment.user_id == current_user_id,
            Assessment.completed_at.isnot(None),
        )
        .order_by(Assessment.completed_at.desc())
        .all()
    )

    if not assessments:
        raise ValueError(
            "At least one completed assessment is required."
        )

    current = assessments[0]
    previous = assessments[1] if len(assessments) >= 2 else None

    return current, previous


def _get_skill_scores(
    assessment_id: int,
    db: Session,
) -> Dict[str, SkillScore]:

    rows = (
        db.query(SkillScore)
        .filter(
            SkillScore.assessment_id == assessment_id
        )
        .all()
    )

    return {
        row.skill: row
        for row in rows
    }


def _get_question_performance(
    assessment_id: int,
    db: Session,
) -> Dict[str, Any]:

    rows = (
        db.query(
            Answer,
            Question,
        )
        .join(
            Question,
            Answer.question_id == Question.id,
        )
        .filter(
            Answer.assessment_id == assessment_id
        )
        .all()
    )

    result: Dict[str, Any] = {}

    for answer, question in rows:

        skill = question.skill
        difficulty = question.difficulty or "Unknown"

        if skill not in result:
            result[skill] = {
                "total": 0,
                "correct": 0,
                "difficulty": {},
            }

        skill_data = result[skill]

        skill_data["total"] += 1

        if answer.is_correct:
            skill_data["correct"] += 1

        if difficulty not in skill_data["difficulty"]:
            skill_data["difficulty"][difficulty] = {
                "total": 0,
                "correct": 0,
            }

        difficulty_data = skill_data["difficulty"][difficulty]

        difficulty_data["total"] += 1

        if answer.is_correct:
            difficulty_data["correct"] += 1

    return result


def _accuracy(
    correct: int,
    total: int,
) -> float:

    if total == 0:
        return 0.0

    return round(
        (correct / total) * 100,
        2,
    )


def build_adaptive_analysis(
    current_user_id: int,
    db: Session,
) -> Dict[str, Any]:

    current, previous = _get_latest_assessments(
        current_user_id,
        db,
    )

    current_scores = _get_skill_scores(
        current.id,
        db,
    )

    previous_scores = {}

    if previous:
        previous_scores = _get_skill_scores(
            previous.id,
            db,
        )

    question_performance = _get_question_performance(
        current.id,
        db,
    )

    all_skills = sorted(
        set(current_scores.keys())
        | set(previous_scores.keys())
    )

    insights: List[Dict[str, Any]] = []

    strong_skills = []
    good_skills = []
    weak_skills = []
    critical_skills = []

    improving_skills = []
    declining_skills = []

    for skill in all_skills:

        current_row = current_scores.get(skill)
        previous_row = previous_scores.get(skill)

        current_score = (
            float(current_row.score)
            if current_row
            else 0.0
        )

        previous_score = (
            float(previous_row.score)
            if previous_row
            else None
        )

        score_change = (
            round(
                current_score - previous_score,
                2,
            )
            if previous_score is not None
            else None
        )

        classification = classify_score(
            current_score
        )

        trend = calculate_trend(
            current_score,
            previous_score,
        )

        priority = calculate_priority(
            current_score,
            score_change,
            classification,
        )

        performance = question_performance.get(
            skill,
            {
                "total": 0,
                "correct": 0,
                "difficulty": {},
            },
        )

        total_questions = performance["total"]
        correct_answers = performance["correct"]

        accuracy = _accuracy(
            correct_answers,
            total_questions,
        )

        beginner_accuracy = None
        intermediate_accuracy = None

        beginner = performance["difficulty"].get(
            "Beginner"
        )

        intermediate = performance["difficulty"].get(
            "Intermediate"
        )

        if beginner:
            beginner_accuracy = _accuracy(
                beginner["correct"],
                beginner["total"],
            )

        if intermediate:
            intermediate_accuracy = _accuracy(
                intermediate["correct"],
                intermediate["total"],
            )

        if classification == "Strong":
            strong_skills.append(skill)

        elif classification == "Good":
            good_skills.append(skill)

        elif classification == "Needs Improvement":
            weak_skills.append(skill)

        else:
            critical_skills.append(skill)

        if trend == "Improving":
            improving_skills.append(skill)

        elif trend == "Declining":
            declining_skills.append(skill)

        if previous_score is None:

            reason = (
                f"{skill} currently scores "
                f"{current_score:.2f}% and is classified "
                f"as {classification}."
            )

        else:

            direction = (
                "increased"
                if score_change >= 0
                else "decreased"
            )

            reason = (
                f"{skill} {direction} by "
                f"{abs(score_change):.2f} percentage points "
                f"from {previous_score:.2f}% to "
                f"{current_score:.2f}%. "
                f"Current classification: "
                f"{classification}."
            )

        insights.append(
            {
                "skill": skill,
                "current_score": current_score,
                "previous_score": previous_score,
                "score_change": score_change,
                "classification": classification,
                "trend": trend,
                "priority": priority,
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "accuracy": accuracy,
                "beginner_accuracy": beginner_accuracy,
                "intermediate_accuracy": intermediate_accuracy,
                "reason": reason,
            }
        )

    priority_order = {
        "High": 0,
        "Medium": 1,
        "Low": 2,
    }

    insights.sort(
        key=lambda item: (
            priority_order[item["priority"]],
            item["current_score"],
        )
    )

    priority_skills = [
        item["skill"]
        for item in insights
        if item["priority"] in ("High", "Medium")
    ]

    overall_score = float(
        current.overall_score
    )

    previous_overall_score = (
        float(previous.overall_score)
        if previous
        else None
    )

    overall_score_change = (
        round(
            overall_score - previous_overall_score,
            2,
        )
        if previous_overall_score is not None
        else None
    )

    return {
        "assessment_id": current.id,
        "previous_assessment_id": (
            previous.id if previous else None
        ),
        "overall_score": overall_score,
        "previous_overall_score": previous_overall_score,
        "overall_score_change": overall_score_change,
        "strong_skills": strong_skills,
        "good_skills": good_skills,
        "weak_skills": weak_skills,
        "critical_skills": critical_skills,
        "improving_skills": improving_skills,
        "declining_skills": declining_skills,
        "priority_skills": priority_skills,
        "skills": insights,
    }