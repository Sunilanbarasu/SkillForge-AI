from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.assessment import Assessment, SkillScore
from app.models.profile import Profile

from app.services.placement_alignment import (
    build_placement_alignment,
    ROLE_REQUIREMENTS,
)


router = APIRouter()


@router.get(
    "/alignment",
    summary="Get placement skill alignment for the current user",
)
def get_placement_alignment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Compare the user's latest completed assessment
    against the requirements of their target placement role.

    All scores come directly from the database.
    """

    # ---------------------------------------------------------
    # 1. Get latest completed assessment
    # ---------------------------------------------------------

    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.user_id == current_user.id,
            Assessment.completed_at.isnot(None),
        )
        .order_by(Assessment.completed_at.desc())
        .first()
    )

    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No completed assessment found. "
                "Complete an assessment before viewing placement alignment."
            ),
        )

    # ---------------------------------------------------------
    # 2. Get user's target role
    # ---------------------------------------------------------

    profile = (
        db.query(Profile)
        .filter(Profile.user_id == current_user.id)
        .first()
    )

    target_role = (
        profile.target_role
        if profile and profile.target_role
        else "Software Developer"
    )

    # ---------------------------------------------------------
    # 3. Get real skill scores
    # ---------------------------------------------------------

    skill_scores = (
        db.query(SkillScore)
        .filter(
            SkillScore.assessment_id == assessment.id
        )
        .order_by(SkillScore.skill.asc())
        .all()
    )

    if not skill_scores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No skill scores found for the latest assessment."
            ),
        )

    score_data = [
        {
            "skill": row.skill,
            "score": float(row.score),
            "total_questions": row.total_questions,
            "correct_answers": row.correct_answers,
        }
        for row in skill_scores
    ]

    # ---------------------------------------------------------
    # 4. Build deterministic placement alignment
    # ---------------------------------------------------------

    alignment = build_placement_alignment(
        target_role=target_role,
        skill_scores=score_data,
    )

    # ---------------------------------------------------------
    # 5. Add assessment metadata
    # ---------------------------------------------------------

    alignment["assessment_id"] = assessment.id
    alignment["overall_score"] = round(
        float(assessment.overall_score),
        2,
    )

    alignment["available_roles"] = list(
        ROLE_REQUIREMENTS.keys()
    )

    return alignment


@router.get(
    "/roles",
    summary="Get available placement target roles",
)
def get_placement_roles():
    """
    Returns the supported placement roles and their
    required skill thresholds.
    """

    return {
        "roles": [
            {
                "name": role,
                "requirements": requirements,
            }
            for role, requirements in ROLE_REQUIREMENTS.items()
        ]
    }
