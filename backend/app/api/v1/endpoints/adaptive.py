from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.adaptive import AdaptiveAnalysisResponse
from app.services.adaptive_engine import build_adaptive_analysis


router = APIRouter()


@router.get(
    "/analysis",
    response_model=AdaptiveAnalysisResponse,
    summary="Get adaptive skill analysis",
)
def get_adaptive_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        analysis = build_adaptive_analysis(
            current_user_id=current_user.id,
            db=db,
        )

        return analysis

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate adaptive analysis: {str(exc)}",
        )
@router.get(
    "/why/{skill}",
    summary="Explain why a skill is prioritized",
)
def explain_skill_priority(
    skill: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns an evidence-based explanation for why a skill
    is currently recommended.

    All performance facts come from the backend adaptive engine.
    """

    try:
        analysis = build_adaptive_analysis(
            current_user_id=current_user.id,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    skill_insight = next(
        (
            item
            for item in analysis["skills"]
            if item["skill"].lower() == skill.lower()
        ),
        None,
    )

    if skill_insight is None:
        raise HTTPException(
            status_code=404,
            detail=f"No adaptive analysis found for skill '{skill}'.",
        )

    classification = skill_insight["classification"]
    trend = skill_insight["trend"]
    priority = skill_insight["priority"]
    current_score = skill_insight["current_score"]
    previous_score = skill_insight["previous_score"]
    score_change = skill_insight["score_change"]
    total_questions = skill_insight["total_questions"]
    correct_answers = skill_insight["correct_answers"]
    accuracy = skill_insight["accuracy"]
    beginner_accuracy = skill_insight["beginner_accuracy"]
    intermediate_accuracy = skill_insight["intermediate_accuracy"]

    evidence = [
        f"Latest score: {current_score:.2f}%",
        f"Correct answers: {correct_answers}/{total_questions}",
        f"Classification: {classification}",
        f"Priority: {priority}",
    ]

    if previous_score is not None and score_change is not None:
        evidence.append(
            f"Previous score: {previous_score:.2f}% "
            f"({score_change:+.2f} percentage points)"
        )

    if beginner_accuracy is not None:
        evidence.append(
            f"Beginner accuracy: {beginner_accuracy:.2f}%"
        )

    if intermediate_accuracy is not None:
        evidence.append(
            f"Intermediate accuracy: {intermediate_accuracy:.2f}%"
        )

    if classification == "Critical":
        explanation = (
            f"{skill_insight['skill']} is prioritized because your latest "
            f"score is {current_score:.2f}%, which is in the Critical range."
        )
    elif classification == "Needs Improvement":
        explanation = (
            f"{skill_insight['skill']} is prioritized because your latest "
            f"score is {current_score:.2f}%, indicating that this skill "
            f"still needs improvement."
        )
    elif trend == "Declining":
        explanation = (
            f"{skill_insight['skill']} is prioritized because your score "
            f"has declined by {abs(score_change):.2f} percentage points."
        )
    else:
        explanation = (
            f"{skill_insight['skill']} is being monitored based on your "
            f"latest assessment performance."
        )

    return {
        "skill": skill_insight["skill"],
        "explanation": explanation,
        "classification": classification,
        "trend": trend,
        "priority": priority,
        "evidence": evidence,
        "performance": {
            "current_score": current_score,
            "previous_score": previous_score,
            "score_change": score_change,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "accuracy": accuracy,
            "beginner_accuracy": beginner_accuracy,
            "intermediate_accuracy": intermediate_accuracy,
        },
    }
