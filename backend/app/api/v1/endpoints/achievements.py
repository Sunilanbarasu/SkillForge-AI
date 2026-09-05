from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.achievements import build_achievements


router = APIRouter()


class AchievementResponse(BaseModel):
    key: str
    title: str
    description: str
    evidence: str


@router.get(
    "",
    response_model=List[AchievementResponse],
    summary="Get evidence-based student achievements",
)
def get_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return build_achievements(
        current_user_id=current_user.id,
        db=db,
    )
