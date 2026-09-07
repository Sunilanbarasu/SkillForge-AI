from fastapi import APIRouter, Depends, HTTPException
from datetime import date, datetime, timezone

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.coding_challenge import CodingChallenge
from app.models.daily_challenge import DailyChallenge
from app.models.coding_submission import CodingSubmission
from app.services.daily_challenge import generate_daily_challenge
from app.services.coding_streak import record_successful_completion
from app.services.code_evaluator import evaluate_python_code


router = APIRouter()


def challenge_response(assignment, challenge, streak=None):
    return {
        "daily_id": assignment.id,
        "challenge_id": challenge.id,
        "challenge_date": assignment.challenge_date,
        "completed": assignment.completed,
        "completed_at": assignment.completed_at,
        "title": challenge.title,
        "description": challenge.description,
        "skill": challenge.skill,
        "language": challenge.language,
        "difficulty": challenge.difficulty,
        "starter_code": challenge.starter_code,
        "test_cases": challenge.test_cases,
        "hints": challenge.hints,
        "explanation": challenge.explanation,
        "streak": (
            {
                "current_streak": streak.current_streak,
                "best_streak": streak.best_streak,
                "total_completed": streak.total_completed,
            }
            if streak else None
        ),
    }


@router.get("/today")
def get_today_challenge(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    assignment = (
        db.query(DailyChallenge)
        .filter(
            DailyChallenge.user_id == current_user.id,
            DailyChallenge.challenge_date == today,
        )
        .first()
    )

    if assignment:
        challenge = (
            db.query(CodingChallenge)
            .filter(CodingChallenge.id == assignment.challenge_id)
            .first()
        )

        if challenge:
            return challenge_response(assignment, challenge)

    try:
        generated = generate_daily_challenge(db, current_user.id)

        challenge = CodingChallenge(
            title=generated["title"],
            description=generated["description"],
            skill=generated["skill"],
            language=generated["language"],
            difficulty=generated["difficulty"],
            starter_code=generated["starter_code"],
            test_cases=generated["test_cases"],
            hints=generated["hints"],
            explanation=generated["explanation"],
        )

        db.add(challenge)
        db.flush()

        assignment = DailyChallenge(
            user_id=current_user.id,
            challenge_id=challenge.id,
            challenge_date=today,
            completed=False,
        )

        db.add(assignment)
        db.commit()

        db.refresh(assignment)
        db.refresh(challenge)

        return challenge_response(assignment, challenge)

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate today's coding challenge: {str(exc)}",
        )


class CodingSubmissionRequest(BaseModel):
    challenge_id: int
    code: str


@router.post("/submit")
def submit_daily_challenge(
    payload: CodingSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    assignment = (
        db.query(DailyChallenge)
        .filter(
            DailyChallenge.user_id == current_user.id,
            DailyChallenge.challenge_date == today,
            DailyChallenge.challenge_id == payload.challenge_id,
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="This challenge is not assigned to you for today.",
        )

    challenge = (
        db.query(CodingChallenge)
        .filter(CodingChallenge.id == payload.challenge_id)
        .first()
    )

    if not challenge:
        raise HTTPException(
            status_code=404,
            detail="Coding challenge not found.",
        )

    if assignment.completed:
        return {
            "submission_id": None,
            "challenge_id": challenge.id,
            "passed": True,
            "score": 100.0,
            "passed_tests": len(challenge.test_cases or []),
            "total_tests": len(challenge.test_cases or []),
            "feedback": "Today's challenge has already been completed.",
            "completed": True,
            "streak": None,
        }

    evaluation = evaluate_python_code(
        payload.code,
        challenge.test_cases or [],
    )

    submission = CodingSubmission(
        user_id=current_user.id,
        challenge_id=challenge.id,
        code=payload.code,
        passed=evaluation["passed"],
        score=evaluation["score"],
        feedback=evaluation["feedback"],
    )

    db.add(submission)

    streak = None

    if evaluation["passed"]:
        assignment.completed = True
        assignment.completed_at = datetime.now(timezone.utc)

        db.flush()

        streak = record_successful_completion(
            db,
            current_user.id,
            today,
        )

    db.commit()
    db.refresh(submission)

    return {
        "submission_id": submission.id,
        "challenge_id": challenge.id,
        "passed": evaluation["passed"],
        "score": evaluation["score"],
        "passed_tests": evaluation["passed_tests"],
        "total_tests": evaluation["total_tests"],
        "feedback": evaluation["feedback"],
        "completed": assignment.completed,
        "streak": (
            {
                "current_streak": streak.current_streak,
                "best_streak": streak.best_streak,
                "total_completed": streak.total_completed,
            }
            if streak else None
        ),
    }


@router.get("/streak")
def get_coding_streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.coding_streak import CodingStreak

    streak = (
        db.query(CodingStreak)
        .filter(CodingStreak.user_id == current_user.id)
        .first()
    )

    if not streak:
        return {
            "current_streak": 0,
            "best_streak": 0,
            "total_completed": 0,
            "last_completed_date": None,
        }

    return {
        "current_streak": streak.current_streak,
        "best_streak": streak.best_streak,
        "total_completed": streak.total_completed,
        "last_completed_date": streak.last_completed_date,
    }
