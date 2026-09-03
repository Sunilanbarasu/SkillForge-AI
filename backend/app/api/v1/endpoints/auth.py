from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.profile import Profile
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=dict)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new student account.
    Checks for duplicate email, hashes password with bcrypt, and initializes default student profile.
    """
    # Check duplicate email
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Hash password with bcrypt
    hashed_pwd = get_password_hash(user_in.password)

    # Create User
    new_user = User(
        name=user_in.name.strip(),
        email=user_in.email.lower(),
        hashed_password=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Automatically initialize empty student Profile linked via 1-to-1 relationship
    new_profile = Profile(
        user_id=new_user.id,
        target_role="Software Engineer",
        experience_level="Beginner",
        interests=[],
        selected_skills=["Python", "DSA", "SQL"]
    )
    db.add(new_profile)
    db.commit()

    # Generate access token
    access_token = create_access_token(subject=new_user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(new_user)
    }


@router.post("/login", response_model=dict)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a student using email and password, returning JWT access token.
    """
    user = db.query(User).filter(User.email == credentials.email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    access_token = create_access_token(subject=user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }
