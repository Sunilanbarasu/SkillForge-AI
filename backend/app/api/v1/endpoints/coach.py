from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.study_coach import (
    build_student_context,
    generate_coach_response,
)


router = APIRouter()


class CoachQuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
    )


class CoachResponse(BaseModel):
    question: str
    answer: str


@router.post(
    "/ask",
    response_model=CoachResponse,
    summary="Ask the student-aware AI study coach",
)
def ask_coach(
    payload: CoachQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        context = build_student_context(
            current_user_id=current_user.id,
            db=db,
        )

        answer = generate_coach_response(
            context=context,
            question=payload.question,
        )

        return CoachResponse(
            question=payload.question.strip(),
            answer=answer,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate coach response: {str(exc)}",
        )
