from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.profile import Profile
from app.schemas.profile import ProfileCreateOrUpdate, ProfileResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.get("", response_model=ProfileResponse, summary="Get student placement profile")
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Protected endpoint to retrieve the student profile of the current user.
    """
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        # Create empty profile if none exists
        profile = Profile(
            user_id=current_user.id,
            target_role="Software Engineer",
            experience_level="Beginner",
            interests=[],
            selected_skills=["Python", "DSA", "SQL"]
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return profile


@router.put("", response_model=ProfileResponse, summary="Update student placement profile")
def update_profile(
    profile_in: ProfileCreateOrUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Protected endpoint to update student target role, experience level, interests, and selected skills.
    """
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)

    if profile_in.target_role is not None:
        profile.target_role = profile_in.target_role.strip()
    if profile_in.experience_level is not None:
        profile.experience_level = profile_in.experience_level.strip()
    if profile_in.interests is not None:
        profile.interests = profile_in.interests
    if profile_in.selected_skills is not None:
        profile.selected_skills = profile_in.selected_skills

    db.commit()
    db.refresh(profile)

    return profile
