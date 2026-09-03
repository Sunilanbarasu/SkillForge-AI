from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.assessment import Assessment, SkillScore
from app.models.progress import SkillProgress
from app.schemas.progress import (
    SkillProgressResponse,
    ProgressSummaryResponse,
)

router = APIRouter()


def _get_completed_assessments(current_user: User, db: Session):
    assessments = (
        db.query(Assessment)
        .filter(
            Assessment.user_id == current_user.id,
            Assessment.completed_at.isnot(None),
        )
        .order_by(Assessment.completed_at.desc())
        .all()
    )

    if len(assessments) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least two completed assessments are required to calculate progress.",
        )

    current = assessments[0]
    previous = assessments[1]

    return previous, current


@router.get(
    "/current",
    response_model=ProgressSummaryResponse,
    summary="Get progress between the two latest completed assessments",
)
def get_current_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    previous, current = _get_completed_assessments(current_user, db)

    previous_scores = (
        db.query(SkillScore)
        .filter(SkillScore.assessment_id == previous.id)
        .all()
    )

    current_scores = (
        db.query(SkillScore)
        .filter(SkillScore.assessment_id == current.id)
        .all()
    )

    previous_map = {
        score.skill: score.score
        for score in previous_scores
    }

    current_map = {
        score.skill: score.score
        for score in current_scores
    }

    all_skills = sorted(set(previous_map) | set(current_map))

    progress_items = []

    for skill in all_skills:
        previous_score = float(previous_map.get(skill, 0.0))
        current_score = float(current_map.get(skill, 0.0))

        score_change = round(current_score - previous_score, 2)

        if score_change > 5:
            progress_status = "Improved"
        elif score_change < -5:
            progress_status = "Declined"
        else:
            progress_status = "Unchanged"

        progress_items.append(
            SkillProgressResponse(
                skill=skill,
                previous_score=previous_score,
                current_score=current_score,
                score_change=score_change,
                status=progress_status,
            )
        )

    improved = sum(
        1 for item in progress_items if item.status == "Improved"
    )

    declined = sum(
        1 for item in progress_items if item.status == "Declined"
    )

    unchanged = sum(
        1 for item in progress_items if item.status == "Unchanged"
    )

    overall_change = round(
        float(current.overall_score) - float(previous.overall_score),
        2,
    )

    # Replace any previous stored comparison for this exact pair.
    db.query(SkillProgress).filter(
        SkillProgress.user_id == current_user.id,
        SkillProgress.previous_assessment_id == previous.id,
        SkillProgress.current_assessment_id == current.id,
    ).delete()

    for item in progress_items:
        db.add(
            SkillProgress(
                user_id=current_user.id,
                previous_assessment_id=previous.id,
                current_assessment_id=current.id,
                skill=item.skill,
                previous_score=item.previous_score,
                current_score=item.current_score,
                score_change=item.score_change,
                status=item.status,
            )
        )

    db.commit()

    return ProgressSummaryResponse(
        previous_assessment_id=previous.id,
        current_assessment_id=current.id,
        previous_overall_score=float(previous.overall_score),
        current_overall_score=float(current.overall_score),
        overall_score_change=overall_change,
        improved_skills=improved,
        declined_skills=declined,
        unchanged_skills=unchanged,
        skill_progress=progress_items,
    )