from fastapi import APIRouter, Depends
from app.schemas.auth import UserResponse
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserResponse, summary="Get current authenticated user profile")
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Protected endpoint returning current authenticated user details.
    Password hash is never returned.
    """
    return current_user
